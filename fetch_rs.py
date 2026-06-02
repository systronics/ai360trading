"""
fetch_rs.py — Nifty200 Relative-Strength (RS) repair feed — v1.0
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

WHAT THIS DOES:
  Computes a REAL RS for every Nifty200 symbol using yfinance (free, reliable —
  GOOGLEFINANCE's job, done in Python) and writes it into the `RS` column,
  REPLACING the broken formula cell with a plain number. Because Signal_Score /
  Sector_Rotation_Score / Master_Score are formulas that *reference* RS, they all
  recompute correctly the moment RS holds a real value — no other cell is touched.

  RS definition (mirrors the original formula exactly):
      RS = (stock 35-calendar-day % return) − (NIFTYBEES 35-calendar-day % return)
  i.e. relative strength vs the Nifty ETF. Positive = outperforming the index.

SAFETY / DESIGN:
  • Finds the RS column by HEADER NAME ("RS") — never a hardcoded letter.
  • DRY-RUN by default: prints the computed RS table and writes NOTHING. Pass
    --write to actually update the sheet. The workflow passes --write.
  • Fail-open: any symbol that can't be priced is left UNCHANGED (its existing
    cell — even if #N/A — is not overwritten with a wrong value).
  • Idempotent: safe to run repeatedly; a later run just refreshes the numbers.
  • No subscriber Telegram noise — this is internal plumbing. Prints only.

SCHEDULE (see .github/workflows/fetch_rs.yml):
  Mon–Fri ~08:45 IST (pre-market) so the trading day starts with live RS, plus a
  light intraday refresh. ₹0 (public-repo Actions + free yfinance).
"""

import os, sys, json, time
from datetime import datetime, timedelta
import pytz

IST        = pytz.timezone("Asia/Kolkata")
VERSION    = "v1.0"
SHEET_NAME = "Ai360tradingAlgo"
NIFTY200   = "Nifty200"
RS_HEADER  = "RS"
SYM_HEADER = "NSE_SYMBOL"
LOOKBACK_D = 35          # calendar days — matches the GOOGLEFINANCE TODAY()-35 formula
BENCHMARK  = "NIFTYBEES.NS"


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


def main():
    write = "--write" in sys.argv
    mode = "WRITE" if write else "DRY-RUN"
    print(f"[fetch_rs {VERSION}] {datetime.now(IST):%Y-%m-%d %H:%M IST} | mode={mode}")

    try:
        import yfinance as yf
        import pandas as pd  # noqa: F401  (yfinance pulls it in; used implicitly)
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
    if sym_c is None or rs_c is None:
        print(f"[FATAL] could not find columns: {SYM_HEADER}={sym_c} {RS_HEADER}={rs_c}")
        return 1
    rs_col_letter = _a1_col(rs_c + 1)
    print(f"[COLS] symbol=col{sym_c+1} RS={rs_col_letter} (header idx {rs_c})")

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

    yf_syms = sorted({t[2] for t in targets} | {BENCHMARK})
    print(f"[YF] downloading {len(yf_syms)} symbols (incl. benchmark) ...")

    # One batched download — ~2 months daily closes.
    data = yf.download(yf_syms, period="3mo", interval="1d",
                       group_by="ticker", auto_adjust=False,
                       progress=False, threads=True)

    def closes_for(sym):
        try:
            if len(yf_syms) == 1:
                return data["Close"]
            return data[sym]["Close"]
        except Exception:
            return None

    bench_ret = _pct_return(closes_for(BENCHMARK), LOOKBACK_D)
    if bench_ret is None:
        print(f"[FATAL] benchmark {BENCHMARK} return unavailable — aborting (no RS without a baseline)")
        return 1
    print(f"[BENCH] {BENCHMARK} {LOOKBACK_D}d return = {bench_ret:+.2f}%")

    updates = []      # (sheet_row, rs_value)
    missing = 0
    for sheet_row, nse, yf_sym in targets:
        stock_ret = _pct_return(closes_for(yf_sym), LOOKBACK_D)
        if stock_ret is None:
            missing += 1
            continue
        rs = round(stock_ret - bench_ret, 2)
        updates.append((sheet_row, rs))

    print(f"[RS] computed {len(updates)} / {len(targets)} symbols "
          f"({missing} unpriced, left unchanged)")

    # Show the strongest + weakest as a sanity check.
    updates_sorted = sorted(updates, key=lambda x: x[1], reverse=True)
    rowmap = {t[0]: t[1] for t in targets}
    print("\n  TOP 10 RS (sector leaders):")
    for sr, rs in updates_sorted[:10]:
        print(f"    {rowmap[sr]:16} RS {rs:+7.2f}")
    print("  BOTTOM 5 RS (laggards):")
    for sr, rs in updates_sorted[-5:]:
        print(f"    {rowmap[sr]:16} RS {rs:+7.2f}")

    if not write:
        print("\n[DRY-RUN] nothing written. Re-run with --write to update the RS column.")
        return 0

    # Batched write: one cell per row in the RS column. Plain RAW numbers so the
    # dependent Signal_Score / Sector_Rotation_Score formulas recompute on these.
    body = [{"range": f"{rs_col_letter}{sr}", "values": [[rs]]} for sr, rs in updates]
    CHUNK = 200
    written = 0
    for k in range(0, len(body), CHUNK):
        part = body[k:k + CHUNK]
        ws.batch_update(part, value_input_option="USER_ENTERED")
        written += len(part)
        time.sleep(1.0)
    print(f"[WRITE] updated {written} RS cells in {NIFTY200}. "
          f"Signal_Score / Sector_Rotation_Score / Master_Score will recompute.")
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
