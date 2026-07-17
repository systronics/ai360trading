"""
prune_ex_stocks.py — remove index-exited (EX) rows from Nifty200 — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY (owner decision 2026-07-17):
  The 2026-07-17 audit found 26 sheet stocks that had exited the Nifty 200
  (marked "EX" in col AK by fetch_index_meta). Owner chose to prune them so
  the sheet tracks the real index — but NEVER while a stock has an active
  trade in AlertLog.

SAFETY RULES (hard-coded, non-negotiable):
  • Deletes ONLY rows where col AK == "EX".
  • A symbol with ANY AlertLog row that has a non-empty Trade Status
    (⏳ WAITING / ✅ TRADED / anything) is PROTECTED — skipped with a notice.
    Run again after the trade closes; it prunes then. A running trade thus
    always keeps its Nifty200 row (the bot reads its ATR from there).
  • DRY-RUN by default; --write to actually delete.
  • Deletes bottom-up in ONE batched API call (row indexes stay valid).
  • Never touches any other sheet, row, or column. Formulas below deleted
    rows shift up automatically (all row-relative).

USAGE:  python prune_ex_stocks.py            (preview)
        python prune_ex_stocks.py --write    (delete)
"""

import os, sys, json
from datetime import datetime
import pytz

IST         = pytz.timezone("Asia/Kolkata")
VERSION     = "v1.0"
SHEET_NAME  = "Ai360tradingAlgo"
NIFTY200    = "Nifty200"
ALERTLOG    = "AlertLog"
SYM_HEADER  = "NSE_SYMBOL"
N200_HEADER = "N200"


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
            raise SystemExit("[CREDS] no GCP_SERVICE_ACCOUNT_JSON and no service_account.json")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)
    return gspread.authorize(creds).open(SHEET_NAME)


def main():
    write = "--write" in sys.argv
    print(f"[prune_ex {VERSION}] {datetime.now(IST):%Y-%m-%d %H:%M IST} | "
          f"mode={'WRITE' if write else 'DRY-RUN'}")

    sh = _connect()
    ws = sh.worksheet(NIFTY200)
    header = ws.row_values(1)

    def col_of(name):
        for j, h in enumerate(header):
            if h.strip().lower() == name.lower():
                return j
        return None

    sym_c, n200_c = col_of(SYM_HEADER), col_of(N200_HEADER)
    if sym_c is None or n200_c is None:
        print(f"[FATAL] columns not found: {SYM_HEADER}={sym_c} {N200_HEADER}={n200_c}")
        return 1

    # Symbols with an ACTIVE AlertLog row (any non-empty Trade Status) are protected.
    protected = set()
    try:
        al = sh.worksheet(ALERTLOG).get_all_values()
        for r in al[1:]:
            sym = (r[1] if len(r) > 1 else "").replace("NSE:", "").strip()
            status = (r[10] if len(r) > 10 else "").strip()   # col K = Trade Status
            if sym and status:
                protected.add(sym)
    except Exception as e:
        print(f"[FATAL] cannot read AlertLog — refusing to delete anything: {e}")
        return 1
    print(f"[ALERTLOG] active-trade symbols (protected): {sorted(protected) or 'none'}")

    rows = ws.get_all_values()
    to_delete, skipped = [], []
    for i, r in enumerate(rows[1:], start=2):
        raw = (r[sym_c] if len(r) > sym_c else "").strip()
        if not raw or "NIFTY" in raw.upper():
            continue
        sym = raw.replace("NSE:", "").strip()
        tag = (r[n200_c] if len(r) > n200_c else "").strip()
        if tag != "EX":
            continue
        if sym in protected:
            skipped.append(sym)
        else:
            to_delete.append((i, sym))

    print(f"[PLAN] delete {len(to_delete)} EX rows | protected (active trade): {skipped or 'none'}")
    for i, sym in to_delete:
        print(f"  row {i}: {sym}")

    if not write:
        print("[DRY-RUN] nothing deleted. Re-run with --write.")
        return 0
    if not to_delete:
        print("[WRITE] nothing to delete.")
        return 0

    # One batched deleteDimension, bottom-up so indexes stay valid.
    reqs = [{"deleteDimension": {"range": {
                "sheetId": ws.id, "dimension": "ROWS",
                "startIndex": i - 1, "endIndex": i}}}
            for i, _ in sorted(to_delete, key=lambda x: -x[0])]
    sh.batch_update({"requests": reqs})
    print(f"[WRITE] deleted {len(to_delete)} rows. "
          f"{'Run again after the protected trade(s) close: ' + ', '.join(skipped) if skipped else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
