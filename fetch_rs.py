"""
fetch_rs.py — Nifty200 RS + ATR + slow-moving-stats repair feed — v2.1
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

v2.1 (2026-07-24) — SLOW-MOVING STATS COLUMNS ALSO MOVED OFF GOOGLEFINANCE:

  Full-system audit (2026-07-23) found ~25 of Nifty200's 37 columns were still
  live GOOGLEFINANCE formulas — including CMP itself, the single most
  foundational cell (nearly every other formula starts `IF(C3="","",...)`), so
  a GOOGLEFINANCE outage on CMP alone would zero the WHOLE scoring engine again,
  the same way the June RS outage did.

  The 12 GOOGLEFINANCE columns split into two tiers by how trading_bot.py and
  appscript.gs actually consume them:
    • FAST LANE (needs true intraday freshness, both engines poll every 5 min
      during market hours): CMP, %Change, and the live-volume input to
      Volume_vs_Avg %. Handled by the NEW fetch_live_prices.py (v1.0) +
      fetch_live_prices.yml — NOT this script. CMP/%Change/live-volume need a
      5-minute cadence; a 2x/day script like this one is too stale for them.
    • SLOW LANE (daily freshness is fine — moving averages / 52-week stats
      don't meaningfully change intraday, the exact tier RS/ATR already live
      in): 20/50/200-DMA, 52-week low/high, Avg_Volume_(20D), Pivot_Resistance,
      VCP Status, Days Since Low. THIS is what v2.1 adds to this script.

  Same doctrine as the original RS/ATR fix: columns found by HEADER NAME (never
  hardcoded letters), fail-open per symbol (a symbol that can't be priced keeps
  its last-good value, never blanked), dry-run by default, one batched
  yfinance download for everything.

  LOOKBACK BUMPED 3mo → 15mo: the old RS/ATR-only download only needed ~2
  months of daily bars (35d RS window, 14-session ATR). A 200-day moving
  average and a genuine 52-week high/low need ~10-13 months of history — 15mo
  covers all of it (RS, ATR, and every new column) from the SAME single
  download, no extra API calls.

  Same "drop today's still-forming candle while the market is open" rule the
  ATR fix already established is applied to every new historical-window stat
  (DMAs / 52wk hi-lo / Avg Volume / Pivot / VCP / Days Since Low) — keeps a
  consistent, already-proven semantic: these are "as-of-yesterday's-close"
  numbers during market hours, refreshed pre-market + midday, exactly like ATR.

  VCP Status is the one exception that needs a *live* number even though it's
  in the slow lane: its formula is (5-day High − 5-day Low) / CMP. The 5-day
  high/low part is slow-moving; CMP is not. This script reads whatever CMP is
  already sitting in column C (from fetch_live_prices.py) at the moment it
  runs — VCP Status is a volatility-contraction READ, not a hard gate, so a
  CMP that's up to 5 minutes old here is fine (same freshness tier as the DMAs).

  2026-05-26 → 2026-07-17 v1.0/v2.0 history (RS + ATR) is unchanged below.

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
  • 20_DMA / 50_DMA / 200_DMA: mean of the last N completed daily closes.
  • 52_Weeks_Low / 52_Weeks_High: min/max of daily Low/High over the trailing
    365 calendar days (completed sessions only).
  • Avg_Volume_(20D): mean of the last 20 completed daily volumes.
  • Pivot_Resistance: max daily High over the trailing 30 calendar days.
  • VCP Status: (5-session High − 5-session Low) / current CMP (col C).
  • Days Since Low: days since the lowest daily Low in the trailing 60
    calendar days.

SAFETY / DESIGN:
  • Finds columns by HEADER NAME — never hardcoded letters. Any column not
    found on the sheet is skipped (printed, not fatal) — safe if a header is
    ever renamed.
  • DRY-RUN by default: prints the computed table and writes NOTHING. Pass
    --write to actually update the sheet. The workflow passes --write.
  • Fail-open: any symbol that can't be priced is left UNCHANGED (its existing
    cell is not overwritten with a wrong value). A dead feed leaves values
    stale-but-sane — never random-wrong like the old formula.
  • Idempotent: safe to run repeatedly; a later run just refreshes the numbers.
  • No subscriber Telegram noise — this is internal plumbing. Prints only.

SCHEDULE (see .github/workflows/fetch_rs.yml):
  Mon–Fri ~08:45 IST (pre-market) so the trading day starts with live numbers,
  plus a midday refresh. ₹0 (public-repo Actions + free yfinance).
"""

import os, sys, json, time
from datetime import datetime, timedelta
import pytz

IST          = pytz.timezone("Asia/Kolkata")
VERSION      = "v2.1"
SHEET_NAME   = "Ai360tradingAlgo"
NIFTY200     = "Nifty200"
SYM_HEADER   = "NSE_SYMBOL"
CMP_HEADER   = "CMP"
RS_HEADER    = "RS"
ATR_HEADER   = "ATR (14)"
DMA20_HEADER  = "20_DMA"
DMA50_HEADER  = "50_DMA"
DMA200_HEADER = "200_DMA"
LOW52_HEADER  = "52_Weeks_Low"
HIGH52_HEADER = "52_Weeks_High"
AVGVOL_HEADER = "Avg_Volume_(20D)"
PIVOT_HEADER  = "Pivot_Resistance"
VCP_HEADER    = "VCP Status"
DAYSLOW_HEADER = "Days Since Low"

LOOKBACK_D   = 35          # calendar days — matches the GOOGLEFINANCE TODAY()-35 formula
ATR_PERIOD   = 14          # completed sessions in the True-Range mean
AVGVOL_PERIOD = 20         # completed sessions
PIVOT_LOOKBACK_D  = 30     # calendar days — matches the old Pivot_Resistance formula
VCP_LOOKBACK_D    = 5      # completed sessions — matches the old VCP Status formula
DAYSLOW_LOOKBACK_D = 60    # calendar days — matches the old Days Since Low formula
YEAR_LOOKBACK_D    = 365   # calendar days — 52-week window
BENCHMARKS   = ["NIFTYBEES.NS", "^NSEI"]   # in preference order; ^NSEI = freshness fallback


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


def _to_f(v):
    """Best-effort float parse of a sheet cell (strips commas/%, blank→None)."""
    if v is None:
        return None
    s = str(v).strip().replace(",", "").replace("%", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


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


def _sma(closes, window: int, drop_last: bool):
    """Simple moving average of the last `window` completed daily closes."""
    if closes is None:
        return None
    closes = closes.dropna()
    if drop_last and len(closes) > 0:
        closes = closes.iloc[:-1]
    if len(closes) < window:
        return None
    return round(float(closes.iloc[-window:].mean()), 2)


def _window_by_days(series, days: int, drop_last: bool):
    """Slice a dated series to the trailing `days` calendar days, dropping
    today's still-forming bar if requested."""
    if series is None:
        return None
    series = series.dropna()
    if drop_last and len(series) > 0:
        series = series.iloc[:-1]
    if len(series) == 0:
        return None
    cutoff = series.index[-1] - timedelta(days=days)
    return series[series.index >= cutoff]


def _period_extreme(series, days: int, drop_last: bool, want_max: bool):
    w = _window_by_days(series, days, drop_last)
    if w is None or len(w) == 0:
        return None
    val = w.max() if want_max else w.min()
    return round(float(val), 2) if val is not None else None


def _avg_volume(volumes, period: int, drop_last: bool):
    if volumes is None:
        return None
    volumes = volumes.dropna()
    if drop_last and len(volumes) > 0:
        volumes = volumes.iloc[:-1]
    if len(volumes) < period:
        return None
    return round(float(volumes.iloc[-period:].mean()), 2)


def _days_since_low(lows, days: int, drop_last: bool):
    w = _window_by_days(lows, days, drop_last)
    if w is None or len(w) == 0:
        return None
    low_date = w.idxmin()
    as_of = w.index[-1]
    return int((as_of - low_date).days)


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

    sym_c   = col_of(SYM_HEADER)
    cmp_c   = col_of(CMP_HEADER)
    rs_c    = col_of(RS_HEADER)
    atr_c   = col_of(ATR_HEADER)
    dma20_c  = col_of(DMA20_HEADER)
    dma50_c  = col_of(DMA50_HEADER)
    dma200_c = col_of(DMA200_HEADER)
    low52_c  = col_of(LOW52_HEADER)
    high52_c = col_of(HIGH52_HEADER)
    avgvol_c = col_of(AVGVOL_HEADER)
    pivot_c  = col_of(PIVOT_HEADER)
    vcp_c    = col_of(VCP_HEADER)
    dayslow_c = col_of(DAYSLOW_HEADER)
    if sym_c is None or rs_c is None:
        print(f"[FATAL] could not find columns: {SYM_HEADER}={sym_c} {RS_HEADER}={rs_c}")
        return 1

    slow_cols = {
        "20_DMA": dma20_c, "50_DMA": dma50_c, "200_DMA": dma200_c,
        "52_Weeks_Low": low52_c, "52_Weeks_High": high52_c,
        "Avg_Volume_(20D)": avgvol_c, "Pivot_Resistance": pivot_c,
        "VCP Status": vcp_c, "Days Since Low": dayslow_c,
    }
    rs_col_letter = _a1_col(rs_c + 1)
    atr_col_letter = _a1_col(atr_c + 1) if atr_c is not None else None
    slow_letters = {k: (_a1_col(v + 1) if v is not None else None) for k, v in slow_cols.items()}
    print(f"[COLS] symbol=col{sym_c+1} RS={rs_col_letter} ATR={atr_col_letter or 'NOT FOUND'} "
          f"CMP={'col'+str(cmp_c+1) if cmp_c is not None else 'NOT FOUND — VCP Status skipped'}")
    for name, letter in slow_letters.items():
        if letter is None:
            print(f"[COLS] WARNING: header '{name}' not found on the sheet — that column will be skipped")

    all_vals = ws.get_all_values()
    rows = all_vals[1:]            # data rows (sheet row = i+2)

    # Map data-row index → NSE symbol, skipping index/blank rows.
    targets = []                   # (sheet_row, nse_sym, yf_sym, row_index)
    for i, r in enumerate(rows):
        if len(r) <= sym_c:
            continue
        nse = r[sym_c].strip()
        if not nse or "NIFTY" in nse.upper():   # skip the NIFTY50 index header row
            continue
        targets.append((i + 2, nse, _yf_symbol(nse), i))

    yf_syms = sorted({t[2] for t in targets} | set(BENCHMARKS))
    print(f"[YF] downloading {len(yf_syms)} symbols (incl. benchmarks), 15mo daily history ...")

    # One batched download — 15 months daily OHLCV covers the 35d RS window,
    # the 14-session ATR window, AND the new 200-DMA / 52-week / volume /
    # pivot / VCP / days-since-low windows. No extra API calls needed.
    data = yf.download(yf_syms, period="15mo", interval="1d",
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

    # ── Drop today's partial candle while the market is still open ─────────────
    # (Daily runs are pre-market 08:45 and midday 12:30 IST; by 15:35 the candle
    # is complete. Weekend/holiday runs have no partial candle to drop.) Applied
    # uniformly to ATR and every new slow-moving stat below — keeps a single
    # consistent "as of yesterday's close" semantic during market hours.
    drop_last_if_today = now_ist.hour * 60 + now_ist.minute < 15 * 60 + 35

    rs_updates = []       # (sheet_row, rs_value)
    atr_updates = []      # (sheet_row, atr_value)
    slow_updates = {k: [] for k in slow_cols}   # name -> [(sheet_row, value)]
    rs_missing = atr_missing = 0
    slow_missing = {k: 0 for k in slow_cols}
    atr_by_row = {}
    for sheet_row, nse, yf_sym, row_i in targets:
        f = frame_for(yf_sym)
        stock_ret = _pct_return(closes_for(yf_sym), LOOKBACK_D)
        if stock_ret is None:
            rs_missing += 1
        else:
            rs_updates.append((sheet_row, round(stock_ret - bench_ret, 2)))

        drop = False
        if drop_last_if_today and f is not None:
            fl = f.dropna(subset=["Close"]) if f is not None else None
            drop = fl is not None and len(fl) > 0 and fl.index[-1].date() == now_ist.date()

        if atr_c is not None:
            atr = _true_atr(f, ATR_PERIOD, drop_last=drop)
            if atr is None:
                atr_missing += 1
            else:
                atr_updates.append((sheet_row, atr))
                atr_by_row[sheet_row] = atr

        if f is None:
            for k in slow_cols:
                if slow_cols[k] is not None:
                    slow_missing[k] += 1
            continue

        closes = closes_for(yf_sym)
        highs  = f["High"] if "High" in f else None
        lows   = f["Low"] if "Low" in f else None
        vols   = f["Volume"] if "Volume" in f else None

        def add(name, value):
            if slow_cols[name] is None:
                return
            if value is None:
                slow_missing[name] += 1
            else:
                slow_updates[name].append((sheet_row, value))

        if dma20_c is not None:
            add("20_DMA", _sma(closes, 20, drop))
        if dma50_c is not None:
            add("50_DMA", _sma(closes, 50, drop))
        if dma200_c is not None:
            add("200_DMA", _sma(closes, 200, drop))
        if low52_c is not None:
            add("52_Weeks_Low", _period_extreme(lows, YEAR_LOOKBACK_D, drop, want_max=False))
        if high52_c is not None:
            add("52_Weeks_High", _period_extreme(highs, YEAR_LOOKBACK_D, drop, want_max=True))
        if avgvol_c is not None:
            add("Avg_Volume_(20D)", _avg_volume(vols, AVGVOL_PERIOD, drop))
        if pivot_c is not None:
            add("Pivot_Resistance", _period_extreme(highs, PIVOT_LOOKBACK_D, drop, want_max=True))
        if dayslow_c is not None:
            add("Days Since Low", _days_since_low(lows, DAYSLOW_LOOKBACK_D, drop))
        if vcp_c is not None:
            hi5 = _period_extreme(highs, VCP_LOOKBACK_D, drop, want_max=True)
            lo5 = _period_extreme(lows, VCP_LOOKBACK_D, drop, want_max=False)
            cmp_now = _to_f(rows[row_i][cmp_c]) if cmp_c is not None and len(rows[row_i]) > cmp_c else None
            if hi5 is not None and lo5 is not None and cmp_now and cmp_now > 0:
                add("VCP Status", round((hi5 - lo5) / cmp_now, 4))
            else:
                add("VCP Status", None)

    print(f"[RS ] computed {len(rs_updates)} / {len(targets)} symbols "
          f"({rs_missing} unpriced, left unchanged)")
    if atr_c is not None:
        print(f"[ATR] computed {len(atr_updates)} / {len(targets)} symbols "
              f"({atr_missing} without enough history, left unchanged)")
    for name in slow_cols:
        if slow_cols[name] is not None:
            print(f"[{name}] computed {len(slow_updates[name])} / {len(targets)} symbols "
                  f"({slow_missing[name]} skipped, left unchanged)")

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
    # and appscript/trading_bot read real values instead of GOOGLEFINANCE.
    body = [{"range": f"{rs_col_letter}{sr}", "values": [[v]]} for sr, v in rs_updates]
    if atr_col_letter:
        body += [{"range": f"{atr_col_letter}{sr}", "values": [[v]]} for sr, v in atr_updates]
    total_slow = 0
    for name, updates in slow_updates.items():
        letter = slow_letters[name]
        if letter is None:
            continue
        body += [{"range": f"{letter}{sr}", "values": [[v]]} for sr, v in updates]
        total_slow += len(updates)

    CHUNK = 200
    written = 0
    for k in range(0, len(body), CHUNK):
        part = body[k:k + CHUNK]
        ws.batch_update(part, value_input_option="USER_ENTERED")
        written += len(part)
        time.sleep(1.0)
    print(f"[WRITE] updated {written} cells in {NIFTY200} "
          f"({len(rs_updates)} RS + {len(atr_updates)} ATR + {total_slow} slow-lane). "
          f"Dependent scores recompute; every formerly-GOOGLEFINANCE slow-moving stat "
          f"now uses a Python-fed real value.")
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
