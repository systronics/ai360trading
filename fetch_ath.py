"""
fetch_ath.py — Nifty200 all-time-high distance feed — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY THIS EXISTS (found 2026-07-29):
  Owner asked why DIVISLAB and EXIDEIND both got a "breakout" style
  Breakout_Stage tag on the same day, and pointed out they didn't look the
  same kind of setup. Checked with yfinance full history (back to each
  stock's IPO):
    • DIVISLAB: today's close WAS the true all-time high — zero overhead
      resistance, uncharted territory.
    • EXIDEIND: today's close was still 24.8% below its REAL all-time high
      (set 2024-06-25) — a bounce inside a 1.6-year-old range, with real
      supply sitting overhead that the sheet had no way to see.
  Root cause: Breakout_Stage (Nifty200 col W) only ever compares CMP to
  52_Weeks_High — it has no concept of a stock's TRUE all-time high, so a
  recovery toward a depressed 52-week ceiling gets the exact same "breakout"
  label as a genuine new high. Different setups, same tag.

WHAT THIS DOES:
  Weekly (Saturday, markets closed), one batched yfinance download of EVERY
  Nifty200 symbol's FULL history (period="max", back to each stock's IPO —
  DIVISLAB/EXIDEIND both go back to 2002-2003, ~5,800+ daily bars), and
  writes two NEW, additive columns:
    • All_Time_High   — max of the daily "High" series across full history
                         (same field 52_Weeks_High already uses, for an
                         apples-to-apples comparison)
    • %_from_ATH       — (CMP − All_Time_High) / All_Time_High × 100,
                         reading CMP from whatever's already in column C
                         (same "read whatever's already there" doctrine
                         VCP Status uses in fetch_rs.py — this is a read,
                         not a hard gate, a few minutes of CMP staleness
                         doesn't matter)

DELIBERATELY NOT WIRED INTO ANY GATE (owner instruction, 2026-07-29):
  "yes, add the ATH check, but don't fix gate yet." Breakout_Stage,
  Trade_Type, and every appscript.gs GATE are UNTOUCHED — these two columns
  are informational only, same doctrine as Sector_Trend when it was first
  added (v15.30: "deliberately INFO not a new hard gate so it doesn't
  shrink the candidate pool"). Do NOT reference these columns from any gate
  or scoring formula without the owner explicitly approving it first — see
  CLAUDE.md 🔒 NEVER CHANGE discipline for calibrated thresholds.

SAFETY / DESIGN:
  • Finds/creates columns by HEADER NAME — never hardcoded letters. If the
    two headers don't exist yet, appends them after the last used column
    (does not touch or reorder any existing column).
  • Fail-open per symbol: a symbol whose history can't be downloaded or is
    too short keeps its last-good value untouched, never blanked.
  • DRY-RUN by default; the workflow passes --write.
  • Never adds/removes rows, never touches any other column.

SCHEDULE (see .github/workflows/fetch_ath.yml):
  Saturday 10:45 IST weekly (offset from fetch_index_meta's 10:00 IST slot,
  separate concurrency group, no shared resource contention). ₹0 (public-repo
  Actions + free yfinance).
"""

import os
import sys
import json
import time
from datetime import datetime

import pytz

IST = pytz.timezone("Asia/Kolkata")
VERSION = "v1.0"
SHEET_NAME = "Ai360tradingAlgo"
NIFTY200 = "Nifty200"

SYM_HEADER = "NSE_SYMBOL"
CMP_HEADER = "CMP"
ATH_HEADER = "All_Time_High"
PCT_ATH_HEADER = "%_from_ATH"


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
    if v is None:
        return None
    s = str(v).strip().replace(",", "").replace("%", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


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
    print(f"[fetch_ath {VERSION}] {now_ist:%Y-%m-%d %H:%M IST} | mode={mode}")

    try:
        import yfinance as yf
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
    if sym_c is None:
        print(f"[FATAL] could not find column: {SYM_HEADER}")
        return 1

    # Create the two new columns if this is the first run — append after the
    # last used header, never touch/reorder any existing column.
    ath_c = col_of(ATH_HEADER)
    pct_c = col_of(PCT_ATH_HEADER)
    next_col = len(header)  # 0-indexed next free slot
    needed_cols = next_col + (0 if ath_c is not None else 1) + (0 if pct_c is not None else 1)
    if write and needed_cols > ws.col_count:
        old_count = ws.col_count
        ws.add_cols(needed_cols - old_count)
        print(f"[GRID] expanded sheet from {old_count} to {needed_cols} columns")
    if ath_c is None:
        ath_c = next_col
        next_col += 1
        if write:
            ws.update_cell(1, ath_c + 1, ATH_HEADER)
            print(f"[HEADER] created '{ATH_HEADER}' at col {_a1_col(ath_c + 1)}")
        else:
            print(f"[HEADER] would create '{ATH_HEADER}' at col {_a1_col(ath_c + 1)} (dry-run)")
    if pct_c is None:
        pct_c = next_col
        next_col += 1
        if write:
            ws.update_cell(1, pct_c + 1, PCT_ATH_HEADER)
            print(f"[HEADER] created '{PCT_ATH_HEADER}' at col {_a1_col(pct_c + 1)}")
        else:
            print(f"[HEADER] would create '{PCT_ATH_HEADER}' at col {_a1_col(pct_c + 1)} (dry-run)")

    ath_letter = _a1_col(ath_c + 1)
    pct_letter = _a1_col(pct_c + 1)
    print(f"[COLS] symbol=col{sym_c+1} CMP={'col'+str(cmp_c+1) if cmp_c is not None else 'NOT FOUND — %_from_ATH skipped'} "
          f"All_Time_High={ath_letter} %_from_ATH={pct_letter}")

    all_vals = ws.get_all_values()
    rows = all_vals[1:]

    targets = []   # (sheet_row, nse_sym, yf_sym, cmp)
    for i, r in enumerate(rows):
        if len(r) <= sym_c:
            continue
        nse = r[sym_c].strip()
        if not nse or "NIFTY" in nse.upper():   # skip the NIFTY50 index header row
            continue
        cmp_val = _to_f(r[cmp_c]) if (cmp_c is not None and len(r) > cmp_c) else None
        targets.append((i + 2, nse, _yf_symbol(nse), cmp_val))

    yf_syms = sorted({t[2] for t in targets})
    print(f"[YF] downloading {len(yf_syms)} symbols, FULL history (period=max) ...")

    data = yf.download(yf_syms, period="max", interval="1d",
                        group_by="ticker", auto_adjust=False,
                        progress=False, threads=True)

    def frame_for(sym):
        try:
            if len(yf_syms) == 1:
                return data
            return data[sym]
        except Exception:
            return None

    ath_updates = []    # (sheet_row, ath_value)
    pct_updates = []    # (sheet_row, pct_value)
    ath_missing = 0
    for sheet_row, nse, yf_sym, cmp_val in targets:
        f = frame_for(yf_sym)
        if f is None:
            ath_missing += 1
            continue
        highs = f["High"].dropna() if "High" in f else None
        if highs is None or len(highs) == 0:
            ath_missing += 1
            continue
        ath = round(float(highs.max()), 2)
        ath_updates.append((sheet_row, ath))
        if cmp_val is not None and ath > 0:
            pct_updates.append((sheet_row, round((cmp_val - ath) / ath * 100.0, 2)))

    print(f"[ATH] computed {len(ath_updates)} / {len(targets)} symbols "
          f"({ath_missing} skipped, left unchanged)")
    print(f"[%_from_ATH] computed {len(pct_updates)} / {len(targets)} symbols "
          f"(needs a live CMP already in the sheet)")

    # Sanity check: symbols currently AT their all-time high (0.0%) — these are
    # the clean, no-overhead-resistance setups like today's DIVISLAB.
    at_ath = sorted([p for p in pct_updates if p[1] >= -0.5], key=lambda x: -x[1])
    if at_ath:
        rowmap = {t[0]: t[1] for t in targets}
        print("\n  AT / NEAR ALL-TIME HIGH today (%_from_ATH >= -0.5%):")
        for sr, pct in at_ath[:15]:
            print(f"    {rowmap[sr]:16} {pct:+.2f}%")

    if not write:
        print("\n[DRY-RUN] nothing written. Re-run with --write to update the sheet.")
        return 0

    body = [{"range": f"{ath_letter}{sr}", "values": [[v]]} for sr, v in ath_updates]
    body += [{"range": f"{pct_letter}{sr}", "values": [[v]]} for sr, v in pct_updates]

    CHUNK = 200
    written = 0
    for k in range(0, len(body), CHUNK):
        part = body[k:k + CHUNK]
        ws.batch_update(part, value_input_option="USER_ENTERED")
        written += len(part)
        time.sleep(1.0)
    print(f"[WRITE] updated {written} cells in {NIFTY200} "
          f"({len(ath_updates)} All_Time_High + {len(pct_updates)} %_from_ATH). "
          f"INFORMATIONAL ONLY — not read by any gate or scoring formula.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
