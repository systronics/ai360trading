"""
fetch_live_prices.py — Nifty200 live CMP / %Change / Volume feed — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY THIS EXISTS (2026-07-24 full-system audit):
  The 2026-07-23 audit found ~25 of Nifty200's 37 columns were still live
  GOOGLEFINANCE() spreadsheet formulas — including CMP itself. Nearly every
  other column's formula starts with IF(C3="","",...), so a GOOGLEFINANCE
  outage on CMP alone zeroes the WHOLE scoring engine (Signal_Score,
  FINAL_ACTION, Master_Score — everything), exactly the way the 2026-06-02
  RS outage did, just through a different column. CMP is the single most
  foundational number on the sheet.

  Unlike the slow-moving stats (DMAs, 52-week hi/lo, etc. — see fetch_rs.py
  v2.1, refreshed 2x/day), CMP / %Change / live Volume are read by BOTH
  trading_bot.py and appscript.gs's unifiedManager EVERY 5 MINUTES during
  market hours for real entry/exit/SL/target decisions. A 2x/day feed would
  be far too stale for these three — they need their own fast-lane script on
  the SAME 5-minute cadence as the bots that consume them.

WHAT THIS DOES (per 5-minute tick, market hours only):
  • CMP            (col "CMP"):           last available 1-minute close
  • %Change        (col "%Change"):       (CMP − previous daily close) / previous close × 100
  • live volume     (col "Live_Volume"):   sum of today's 1-minute volume bars so far

  "Live_Volume" is a NEW helper column (not in the original 37) — the
  existing "Volume_vs_Avg %" column keeps its own formula but is repointed
  to read this cell instead of calling GOOGLEFINANCE(A3,"volume") directly
  (see the one-time sheet-formula edit noted in .internal-ops.md 2026-07-24).
  This script never touches Volume_vs_Avg % itself, only feeds it.

HONEST TRADEOFF (stated in the audit, repeating here since it's this
script's whole reason to exist): this replaces "GOOGLEFINANCE, which already
failed sheet-wide once" with "yfinance polled every 5 minutes from
GitHub-hosted runners" — a new dependency at a much higher frequency than
any other current use of yfinance in this codebase. Yahoo Finance has no
official rate limit but is known to occasionally throttle heavy shared-IP
polling. The mitigation is the same fail-open doctrine fetch_rs.py already
proved out: a failed fetch (per-symbol OR whole-batch) leaves the existing
cell value untouched — NEVER blanked. That is categorically safer than
GOOGLEFINANCE's failure mode, which goes #N/A and poisons every downstream
formula immediately. "Stale for one extra 5-minute tick sometimes" beats
"the whole engine goes to zero for days," which is what actually happened.

SAFETY / DESIGN (mirrors fetch_rs.py):
  • Finds columns by HEADER NAME — never hardcoded letters.
  • DRY-RUN by default: prints computed values, writes nothing. --write to
    commit (the workflow passes --write).
  • Fail-open per symbol: missing from the batch response → cell untouched.
  • Fail-open per batch: if the whole yfinance call throws, exits without
    writing anything this tick (same as fetch_rs.py's [FATAL] abort).
  • No subscriber Telegram noise — internal plumbing, prints only.

SCHEDULE (see .github/workflows/fetch_live_prices.yml):
  Every 5 minutes, market hours, Mon-Fri (*/5 3-10 * * 1-5) — identical
  window to trading_bot.yml. Runs in its OWN concurrency group
  (fetch-live-prices) — never share trading-bot's group, that's the exact
  bug that froze RS for 4 days in July (see fetch_rs.py's docstring).
"""

import os, sys, json, time
from datetime import datetime
import pytz

IST         = pytz.timezone("Asia/Kolkata")
VERSION     = "v1.0"
SHEET_NAME  = "Ai360tradingAlgo"
NIFTY200    = "Nifty200"
SYM_HEADER  = "NSE_SYMBOL"
CMP_HEADER  = "CMP"
PCT_HEADER  = "%Change"
LIVEVOL_HEADER = "Live_Volume"


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
    s = nse_sym.strip().upper().replace("NSE:", "").strip()
    return f"{s}.NS"


def _a1_col(n: int) -> str:
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def main():
    write = "--write" in sys.argv
    mode = "WRITE" if write else "DRY-RUN"
    now_ist = datetime.now(IST)
    print(f"[fetch_live_prices {VERSION}] {now_ist:%Y-%m-%d %H:%M IST} | mode={mode}")

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
    cmp_c = col_of(CMP_HEADER)
    pct_c = col_of(PCT_HEADER)
    vol_c = col_of(LIVEVOL_HEADER)
    if sym_c is None or cmp_c is None or pct_c is None:
        print(f"[FATAL] could not find columns: {SYM_HEADER}={sym_c} {CMP_HEADER}={cmp_c} {PCT_HEADER}={pct_c}")
        return 1
    cmp_letter = _a1_col(cmp_c + 1)
    pct_letter = _a1_col(pct_c + 1)
    vol_letter = _a1_col(vol_c + 1) if vol_c is not None else None
    print(f"[COLS] symbol=col{sym_c+1} CMP={cmp_letter} %Change={pct_letter} "
          f"Live_Volume={vol_letter or 'NOT FOUND — skipping (Volume_vs_Avg % keeps its old GOOGLEFINANCE call for now)'}")

    all_vals = ws.get_all_values()
    rows = all_vals[1:]
    targets = []   # (sheet_row, nse_sym, yf_sym)
    for i, r in enumerate(rows):
        if len(r) <= sym_c:
            continue
        nse = r[sym_c].strip()
        if not nse or "NIFTY" in nse.upper():
            continue
        targets.append((i + 2, nse, _yf_symbol(nse)))

    yf_syms = sorted({t[2] for t in targets})
    print(f"[YF] downloading {len(yf_syms)} symbols, 1-min intraday bars ...")

    try:
        intraday = yf.download(tickers=yf_syms, period="1d", interval="1m",
                                group_by="ticker", auto_adjust=False,
                                progress=False, threads=True)
        daily = yf.download(tickers=yf_syms, period="5d", interval="1d",
                             group_by="ticker", auto_adjust=False,
                             progress=False, threads=True)
    except Exception as e:
        print(f"[FATAL] yfinance batch download failed: {e} — writing nothing this tick")
        return 1

    if intraday is None or len(intraday) == 0:
        print("[FATAL] empty intraday response — writing nothing this tick")
        return 1

    def frame(data, sym):
        try:
            if len(yf_syms) == 1:
                return data
            return data[sym]
        except Exception:
            return None

    cmp_updates, pct_updates, vol_updates = [], [], []
    missing = 0
    for sheet_row, nse, yf_sym in targets:
        idf = frame(intraday, yf_sym)
        ddf = frame(daily, yf_sym)
        if idf is None:
            missing += 1
            continue
        closes = idf["Close"].dropna() if "Close" in idf else None
        vols   = idf["Volume"].dropna() if "Volume" in idf else None
        if closes is None or len(closes) == 0:
            missing += 1
            continue
        ltp = float(closes.iloc[-1])
        # Anchor %Change to the ACTUAL date of the latest tick, not to
        # calendar-today. Pre-market (before the 09:15 open) yfinance's "1d"
        # intraday window still returns yesterday's last bars — so the LTP's
        # own date is yesterday, and %Change must compare yesterday-vs-the-day-
        # before (exactly what GOOGLEFINANCE shows pre-market: the last
        # COMPLETED session's move). Comparing against "today" in that case
        # self-compares yesterday's price to itself and silently reports ~0%,
        # masking a real move (caught live: SRF genuinely dropped 8.5% on
        # 2026-07-23 and pre-market GOOGLEFINANCE correctly still shows that;
        # naively filtering "< today" instead of "< LTP's own date" reported
        # a false ~0% here). Once the market is open, the LTP's date IS today
        # and this is equivalent to the simpler "< today" rule.
        ltp_date = closes.index[-1].date()

        prev_close = None
        if ddf is not None and "Close" in ddf:
            # Don't assume a fixed row position (iloc[-2]) — yfinance sometimes
            # leaves the most recent daily bar NaN for a symbol (data-provider
            # lag, seen live: 360ONE's 07-23 bar was NaN while ADANIENSOL's
            # wasn't, same fetch, same moment) or appends a live-updating "today"
            # bar once the market opens. Drop NaN AND anything on/after the
            # LTP's own date, then take whatever the last remaining valid
            # close is — correct regardless of which symbols happen to be
            # lagging, and correct both pre-market and intraday.
            dclose = ddf["Close"].dropna()
            dclose = dclose[dclose.index.date < ltp_date]
            if len(dclose) >= 1:
                prev_close = float(dclose.iloc[-1])

        cmp_updates.append((sheet_row, round(ltp, 2)))
        if prev_close and prev_close > 0:
            pct_updates.append((sheet_row, round((ltp - prev_close) / prev_close * 100, 2)))

        if vol_c is not None and vols is not None and len(vols) > 0:
            vol_updates.append((sheet_row, int(vols.sum())))

    print(f"[LIVE] CMP computed {len(cmp_updates)} / {len(targets)} "
          f"({missing} missing from batch, left unchanged)")
    print(f"[LIVE] %Change computed {len(pct_updates)} / {len(targets)} "
          f"(needs a valid previous close; missing ones leave %Change unchanged)")
    if vol_c is not None:
        print(f"[LIVE] Live_Volume computed {len(vol_updates)} / {len(targets)}")

    sample = cmp_updates[:5]
    rowmap = {t[0]: t[1] for t in targets}
    print("\n  SAMPLE (first 5):")
    for sr, v in sample:
        pct = next((p for s, p in pct_updates if s == sr), None)
        print(f"    {rowmap[sr]:16} CMP {v:10.2f}  %Chg {pct if pct is not None else '—'}")

    if not write:
        print("\n[DRY-RUN] nothing written. Re-run with --write to update the sheet.")
        return 0

    body = [{"range": f"{cmp_letter}{sr}", "values": [[v]]} for sr, v in cmp_updates]
    body += [{"range": f"{pct_letter}{sr}", "values": [[v]]} for sr, v in pct_updates]
    if vol_letter:
        body += [{"range": f"{vol_letter}{sr}", "values": [[v]]} for sr, v in vol_updates]

    CHUNK = 200
    written = 0
    for k in range(0, len(body), CHUNK):
        part = body[k:k + CHUNK]
        ws.batch_update(part, value_input_option="USER_ENTERED")
        written += len(part)
        time.sleep(1.0)
    print(f"[WRITE] updated {written} cells in {NIFTY200} "
          f"({len(cmp_updates)} CMP + {len(pct_updates)} %Change + {len(vol_updates)} Live_Volume).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
