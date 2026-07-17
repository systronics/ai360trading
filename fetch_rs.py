"""
fetch_rs.py — Nifty200 RS + ATR repair feed — v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY THIS EXISTS (root cause, found 2026-06-02):
  The Nifty200 sheet's `RS` column is a GOOGLEFINANCE() historical formula:

      =...C / INDEX(GOOGLEFINANCE(A,"price",TODAY()-35),...) ...
        - GOOGLEFINANCE("NSE:NIFTYBEES","price",...) ...

  Google has been failing GOOGLEFINANCE historical calls for NSE symbols, so
  RS = #N/A for ALL ~210 stocks. That #N/A cascades through the scoring engine:
    • Signal_Score (S)        → #N/A   (formula adds IF(U>0,1,0), inherits the error)
    • FINAL_ACTION (T)        → #N/A
    • Sector_Rotation_Score   → 0       (IFERROR masks the error as 0)
    • Master_Score (AH)       → 0
  In a BEARISH market (Nifty < 20DMA) the AppScript scanner allows a new WAITING
  slot ONLY via the exception  Signal_Score >= 40 AND Leader_Type = "Sector Leader"
  AND RS >= 15.  With Signal_Score and RS dead, NO stock can ever enter in a
  bearish regime — the entire bearish path is silently disabled (the bullish path
  keys off Breakout_Stage + Leader_Type, which still work, so it was never noticed).

v2.0 (2026-07-17) — TWO NEW ROOT CAUSES FIXED:

  1. ATR COLUMN WAS NEVER AN ATR (audit 2026-07-17):
     Nifty200 col "ATR (14)" held the formula
         AVERAGE(ARRAYFORMULA(INDEX(GOOGLEFINANCE(sym,"high",TODAY()-21,TODAY()),2,2,14)
                            - INDEX(GOOGLEFINANCE(sym,"low", TODAY()-21,TODAY()),2,2,14)))
     INDEX(range,2,2) returns ONE cell (the 4th arg is ignored), so the column
     was the high−low range of a SINGLE day ~3 weeks back — re-randomizing daily
     as the window slid. Proven: all sampled symbols exactly matched 2026-06-29's
     range (ABB 381.5 vs true ATR ~239 = +60%; IEX 2.1 vs 2.84 = −26%).
     That column feeds BOTH engines:
       • appscript.gs  r[28] → every swing/positional/base/momentum SL + target,
         the v15.22 MIN_SL_ATR_MULT noise floor, the ≥5% target reachability
         check, options atrPct mapping and _generateOptionsSignal strikes.
       • trading_bot.py _read_atr_from_nifty200 → trailing SL, resistance-room
         veto, CE candidate flag.
     THIS SCRIPT now computes a REAL ATR(14) — simple mean of the True Range
     max(H−L, |H−prevC|, |L−prevC|) over the last 14 COMPLETED sessions (today's
     partial candle is excluded while the market is open) — and writes it into
     the "ATR (14)" column as a plain number, replacing the broken formula.
     Fixing the DATA fixes stock alerts AND option signals with zero AppScript
     or bot code changes.

  2. RS WAS FROZEN AT 2026-07-13 (found 2026-07-17):
     The workflow shared concurrency group `trading-bot` with the all-day session
     loop. GH keeps only ONE queued run per group, so fetch_rs queued behind the
     session loop and was then kicked out by the next session run
     ("Canceling since a higher priority waiting request for trading-bot exists")
     — it never executed after 07-13, freezing RS while the RS ≥ 5 hard gate kept
     filtering on dead data (ABB real RS ≈ +10 → sheet said −7.02 → wrongly
     blocked on its breakout day). The workflow now uses its own `fetch-rs`
     group; single-cell batch writes never corrupt a concurrent bot read (each
     API call is atomic), so sharing the bot's group was never needed.
     Also: yfinance's NIFTYBEES.NS data was found lagging 2 sessions behind the
     stocks — a stale benchmark silently shifts EVERY RS value by the market's
     missed move, so v2.0 falls back to ^NSEI when NIFTYBEES is not as fresh as
     the stock data.

WHAT THIS DOES:
  • RS  (col "RS"):        RS = (stock 35-calendar-day % return)
                                − (benchmark 35-calendar-day % return)
    Benchmark = NIFTYBEES.NS, falling back to ^NSEI if NIFTYBEES is stale.
    (Definition unchanged from v1.0 / the original GOOGLEFINANCE formula.)
  • ATR (col "ATR (14)"):  mean True Range of the last 14 completed sessions.

SAFETY / DESIGN:
  • Finds columns by HEADER NAME ("RS", "ATR (14)") — never hardcoded letters.
  • DRY-RUN by default: prints the computed table and writes NOTHING. Pass
    --write to actually update the sheet. The workflow passes --write.
  • Fail-open: any symbol that can't be priced is left UNCHANGED (its existing
    cell is not overwritten with a wrong value). A dead feed leaves values
    stale-but-sane — never random-wrong like the old formula.
  • Idempotent: safe to run repeatedly; a later run just refreshes the numbers.
  • No subscriber Telegram noise — this is internal plumbing. Prints only.

SCHEDULE (see .github/workflows/fetch_rs.yml):
  Mon–Fri ~08:45 IST (pre-market) so the trading day starts with live RS + ATR,
  plus a midday refresh. ₹0 (public-repo Actions + free yfinance).
"""

import os, sys, json, time
from datetime import datetime, timedelta
import pytz

IST         = pytz.timezone("Asia/Kolkata")
VERSION     = "v2.0"
SHEET_NAME  = "Ai360tradingAlgo"
NIFTY200    = "Nifty200"
RS_HEADER   = "RS"
ATR_HEADER  = "ATR (14)"
SYM_HEADER  = "NSE_SYMBOL"
LOOKBACK_D  = 35          # calendar days — matches the GOOGLEFINANCE TODAY()-35 formula
ATR_PERIOD  = 14          # completed sessions in the True-Range mean
BENCHMARKS  = ["NIFTYBEES.NS", "^NSEI"]   # in preference order; ^NSEI = freshness fallback


# ── Google Sheets (same auth convention as fetch_fii_dii.py) ───────────────────
def _connect():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        try:
            with open("service_account.json") as f:
                raw = f.read().strip()
        except FileNotFoundError:
            raise SystemExit("[CREDS] GCP_SERVICE_ACCOUNT_JSON env var not set "
                             "and service_account.json not found locally")
    try:
        creds_dict = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"[CREDS] Failed to parse GCP credentials JSON: {e}")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds).open(SHEET_NAME)


def _yf_symbol(nse_sym: str) -> str:
    """'NSE:TCS' / 'TCS' → 'TCS.NS' for yfinance."""
    s = nse_sym.strip().upper().replace("NSE:", "").strip()
    return f"{s}.NS"


def _pct_return(closes, lookback_days: int):
    """% return from the first close on/after (last_date - lookback_days) to the
    most recent close — mirrors INDEX(GOOGLEFINANCE(.. TODAY()-N ..), first row)."""
    if closes is None or len(closes) < 2:
        return None
    closes = closes.dropna()
    if len(closes) < 2:
        return None
    last_date = closes.index[-1]
    cutoff = last_date - timedelta(days=lookback_days)
    past = closes[closes.index <= cutoff]
    base = past.iloc[-1] if len(past) else closes.iloc[0]   # fall back to oldest we have
    cur = closes.iloc[-1]
    if base <= 0:
        return None
    return (cur / base - 1.0) * 100.0


def _true_atr(ohlc, period: int, drop_last: bool):
    """Mean True Range over the last `period` completed sessions.
    TR = max(H−L, |H−prevClose|, |L−prevClose|) — gap-aware, unlike the old
    sheet formula which ignored gaps AND only ever saw one day.
    drop_last=True excludes the newest row (today's still-forming candle)."""
    if ohlc is None:
        return None
    ohlc = ohlc.dropna(subset=["High", "Low", "Close"])
    if drop_last and len(ohlc) > 0:
        ohlc = ohlc.iloc[:-1]
    if len(ohlc) < period + 1:      # need prevClose for the oldest TR row
        return None
    h, l, c = ohlc["High"], ohlc["Low"], ohlc["Close"]
    prev_c = c.shift(1)
    tr1 = h - l
    tr2 = (h - prev_c).abs()
    tr3 = (l - prev_c).abs()
    tr = tr1.combine(tr2, max).combine(tr3, max)
    val = tr.iloc[-period:].mean()
    if val is None or val <= 0:
        return None
    return round(float(val), 2)


def main():
    write = "--write" in sys.argv
    mode = "WRITE" if write else "DRY-RUN"
    now_ist = datetime.now(IST)
    print(f"[fetch_rs {VERSION}] {now_ist:%Y-%m-%d %H:%M IST} | mode={mode}")

    try:
        import yfinance as yf
        import pandas as pd  # noqa: F401
    except Exception as e:
        print(f"[FATAL] yfinance unavailable: {e}")
        return 1

    sh = _connect()
    ws = sh.worksheet(NIFTY200)
    header = ws.row_values(1)

    def col_of(name):
        for j, h in enumerate(header):
            if h.strip().lower() == name.lower():
                return j
        return None

    sym_c = col_of(SYM_HEADER)
    rs_c = col_of(RS_HEADER)
    atr_c = col_of(ATR_HEADER)
    if sym_c is None or rs_c is None:
        print(f"[FATAL] could not find columns: {SYM_HEADER}={sym_c} {RS_HEADER}={rs_c}")
        return 1
    rs_col_letter = _a1_col(rs_c + 1)
    atr_col_letter = _a1_col(atr_c + 1) if atr_c is not None else None
    print(f"[COLS] symbol=col{sym_c+1} RS={rs_col_letter} ATR={atr_col_letter or 'NOT FOUND — RS only'}")

    all_vals = ws.get_all_values()
    rows = all_vals[1:]            # data rows (sheet row = i+2)

    # Map data-row index → NSE symbol, skipping index/blank rows.
    targets = []                   # (sheet_row, nse_sym, yf_sym)
    for i, r in enumerate(rows):
        if len(r) <= sym_c:
            continue
        nse = r[sym_c].strip()
        if not nse or "NIFTY" in nse.upper():   # skip the NIFTY50 index header row
            continue
        targets.append((i + 2, nse, _yf_symbol(nse)))

    yf_syms = sorted({t[2] for t in targets} | set(BENCHMARKS))
    print(f"[YF] downloading {len(yf_syms)} symbols (incl. benchmarks) ...")

    # One batched download — 3 months daily OHLC covers both the 35d RS window
    # and the 14-session ATR window.
    data = yf.download(yf_syms, period="3mo", interval="1d",
                       group_by="ticker", auto_adjust=False,
                       progress=False, threads=True)

    def frame_for(sym):
        try:
            if len(yf_syms) == 1:
                return data
            return data[sym]
        except Exception:
            return None

    def closes_for(sym):
        f = frame_for(sym)
        try:
            return f["Close"] if f is not None else None
        except Exception:
            return None

    # ── Benchmark with freshness fallback ──────────────────────────────────────
    # A benchmark lagging the stock data shifts EVERY RS value by the market's
    # missed move (seen live 2026-07-17: NIFTYBEES 2 sessions behind). Prefer
    # NIFTYBEES, but require it to be as fresh as the freshest stock close.
    def last_date(closes):
        if closes is None:
            return None
        closes = closes.dropna()
        return closes.index[-1] if len(closes) else None

    stock_dates = [d for d in (last_date(closes_for(t[2])) for t in targets) if d is not None]
    if not stock_dates:
        print("[FATAL] no stock price data at all — aborting")
        return 1
    freshest = max(stock_dates)

    bench_ret, bench_used = None, None
    for bench in BENCHMARKS:
        bd = last_date(closes_for(bench))
        if bd is None:
            print(f"[BENCH] {bench}: no data — trying next")
            continue
        if bd < freshest:
            print(f"[BENCH] {bench}: stale (last {bd.date()} < stocks {freshest.date()}) — trying next")
            continue
        bench_ret = _pct_return(closes_for(bench), LOOKBACK_D)
        if bench_ret is not None:
            bench_used = bench
            break
    if bench_ret is None:
        # Fail-open-ish: use the freshest benchmark we have rather than aborting,
        # but say so loudly — stale bench shifts all RS equally.
        best = None
        for bench in BENCHMARKS:
            bd = last_date(closes_for(bench))
            if bd is not None and (best is None or bd > best[1]):
                best = (bench, bd)
        if best is None:
            print("[FATAL] no benchmark data (NIFTYBEES or ^NSEI) — aborting (no RS without a baseline)")
            return 1
        bench_used = best[0]
        bench_ret = _pct_return(closes_for(bench_used), LOOKBACK_D)
        if bench_ret is None:
            print("[FATAL] benchmark return unavailable — aborting")
            return 1
        print(f"[BENCH] WARNING: using STALE benchmark {bench_used} (last {best[1].date()}) — "
              f"all RS values shifted by the market's missed move")
    print(f"[BENCH] {bench_used} {LOOKBACK_D}d return = {bench_ret:+.2f}%")

    # ── ATR: exclude today's partial candle while the market is still open ─────
    # (Daily runs are pre-market 08:45 and midday 12:30 IST; by 15:35 the candle
    # is complete. Weekend/holiday runs have no partial candle to drop.)
    drop_last_if_today = now_ist.hour * 60 + now_ist.minute < 15 * 60 + 35

    rs_updates = []       # (sheet_row, rs_value)
    atr_updates = []      # (sheet_row, atr_value)
    rs_missing = atr_missing = 0
    atr_by_row = {}
    for sheet_row, nse, yf_sym in targets:
        f = frame_for(yf_sym)
        stock_ret = _pct_return(closes_for(yf_sym), LOOKBACK_D)
        if stock_ret is None:
            rs_missing += 1
        else:
            rs_updates.append((sheet_row, round(stock_ret - bench_ret, 2)))
        if atr_c is not None:
            drop = False
            if drop_last_if_today and f is not None:
                fl = f.dropna(subset=["Close"])
                drop = len(fl) > 0 and fl.index[-1].date() == now_ist.date()
            atr = _true_atr(f, ATR_PERIOD, drop_last=drop)
            if atr is None:
                atr_missing += 1
            else:
                atr_updates.append((sheet_row, atr))
                atr_by_row[sheet_row] = atr

    print(f"[RS ] computed {len(rs_updates)} / {len(targets)} symbols "
          f"({rs_missing} unpriced, left unchanged)")
    if atr_c is not None:
        print(f"[ATR] computed {len(atr_updates)} / {len(targets)} symbols "
              f"({atr_missing} without enough history, left unchanged)")

    # Show the strongest + weakest as a sanity check.
    updates_sorted = sorted(rs_updates, key=lambda x: x[1], reverse=True)
    rowmap = {t[0]: t[1] for t in targets}
    print("\n  TOP 10 RS (sector leaders):")
    for sr, rs in updates_sorted[:10]:
        print(f"    {rowmap[sr]:16} RS {rs:+7.2f}  ATR {atr_by_row.get(sr, '—')}")
    print("  BOTTOM 5 RS (laggards):")
    for sr, rs in updates_sorted[-5:]:
        print(f"    {rowmap[sr]:16} RS {rs:+7.2f}  ATR {atr_by_row.get(sr, '—')}")

    if not write:
        print("\n[DRY-RUN] nothing written. Re-run with --write to update the sheet.")
        return 0

    # Batched write: one cell per row per column. Plain RAW numbers so the
    # dependent Signal_Score / Sector_Rotation_Score formulas recompute on RS,
    # and appscript/trading_bot read a REAL ATR instead of the broken formula.
    body = [{"range": f"{rs_col_letter}{sr}", "values": [[v]]} for sr, v in rs_updates]
    if atr_col_letter:
        body += [{"range": f"{atr_col_letter}{sr}", "values": [[v]]} for sr, v in atr_updates]
    CHUNK = 200
    written = 0
    for k in range(0, len(body), CHUNK):
        part = body[k:k + CHUNK]
        ws.batch_update(part, value_input_option="USER_ENTERED")
        written += len(part)
        time.sleep(1.0)
    print(f"[WRITE] updated {written} cells in {NIFTY200} "
          f"({len(rs_updates)} RS + {len(atr_updates)} ATR). "
          f"Dependent scores recompute; SL/target math now uses a real ATR.")
    return 0


def _a1_col(n: int) -> str:
    """1-based column index → A1 letters (1→A, 27→AA)."""
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


if __name__ == "__main__":
    sys.exit(main())
