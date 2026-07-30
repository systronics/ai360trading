"""
fetch_dividends.py — Nifty200 dividend + bonus/split history feed — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY THIS EXISTS (owner ask, 2026-07-30):
  Owner asked which cash stocks "benefit more with dividend, bonus etc." —
  a real, previously-unbuilt question. Checked the whole repo first:
  generate_longterm.py already pulls a trailing dividendYield from yfinance
  .info for the separate 12-month LongTermSignals sheet, but NOTHING in the
  day-to-day cash/swing/options engine (Nifty200, appscript.gs, trading_bot.py)
  carries any dividend or bonus/split data at all.

IMPORTANT DATA-HONESTY NOTE — this is TRAILING, not a forward calendar:
  NSE's real UPCOMING corporate-actions calendar (announced-but-not-yet-
  effective dividends/bonuses/splits) lives behind nseindia.com's protected
  JSON API, which needs a real browser session/cookie dance to access
  reliably — the same class of fragility that caused the 2026-05-27 holiday-
  list outage (this project has been burned by unreliable/hardcoded external
  data before — see CLAUDE.md). Rather than build something that silently
  breaks, this feed uses yfinance's per-ticker `.dividends`/`.splits` series
  (verified reliable and free) to show each stock's ACTUAL PAST dividend/
  bonus-or-split history — a genuine, honest signal for "which stocks have a
  track record of rewarding holders," not a promise of what's coming next.

WHAT THIS DOES (weekly, Saturday — markets closed):
  For every Nifty200 symbol, via yfinance Ticker.dividends / Ticker.splits
  (per-symbol calls — no reliable single bulk endpoint for corporate-action
  history, unlike price bars), writes FOUR new, additive columns:
    • Div_Yield_%_TTM        — sum of dividends paid in the trailing 365
                                days ÷ current CMP (already in the sheet)
                                × 100. Computed directly from the raw
                                dividend series, not from yfinance's .info
                                summary field (which has shown inconsistent
                                units stock-to-stock in spot checks).
    • Last_Div_Date          — date of the most recent dividend payment
    • Last_Bonus_Split_Date  — date of the most recent split/bonus-style
                                corporate action in yfinance's `.splits`
                                series (Indian bonus issues and true stock
                                splits look identical in this data — see
                                note below — labelled honestly as "or")
    • Last_Bonus_Split_Ratio — the ratio itself (e.g. 1.5 = 3:2 bonus/
                                split, 2.0 = 2:1) — NOT distinguishable
                                between a genuine bonus issue and a stock
                                split from this data source alone

DELIBERATELY NOT WIRED INTO ANY GATE (same doctrine as fetch_ath.py):
  These 4 columns are informational only. Do NOT reference them from
  Master_Score, Trade_Type, Priority_Score, or any appscript.gs GATE, and
  do NOT use them to select/filter CASH candidates, without the owner
  explicitly approving it first — see CLAUDE.md 🔒 NEVER CHANGE.

SAFETY / DESIGN:
  • Finds/creates columns by HEADER NAME — never hardcoded letters.
  • Fail-open per symbol: a symbol whose history can't be downloaded (or
    has never paid a dividend / never had a split) keeps its last-good
    value untouched — a genuinely dividend-free stock (e.g. a fresh IPO)
    is expected to have a blank cell, that's correct, not a fetch failure.
  • DRY-RUN by default; the workflow passes --write.
  • Never adds/removes rows, never touches any other column.
  • ~0.8s/symbol sequential (measured) — ~200 symbols in ~3 minutes, well
    inside a normal Actions timeout; no threading needed.

SCHEDULE (see .github/workflows/fetch_dividends.yml):
  Saturday 11:15 IST weekly (offset from fetch_index_meta 10:00 IST and
  fetch_ath 10:45 IST, own concurrency group). ₹0 (public-repo Actions +
  free yfinance).
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta

import pytz

IST = pytz.timezone("Asia/Kolkata")
VERSION = "v1.0"
SHEET_NAME = "Ai360tradingAlgo"
NIFTY200 = "Nifty200"

SYM_HEADER = "NSE_SYMBOL"
CMP_HEADER = "CMP"
DIV_YIELD_HEADER = "Div_Yield_%_TTM"
LAST_DIV_DATE_HEADER = "Last_Div_Date"
LAST_BONUS_DATE_HEADER = "Last_Bonus_Split_Date"
LAST_BONUS_RATIO_HEADER = "Last_Bonus_Split_Ratio"


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


def _ensure_col(ws, header, name, next_col_holder, write):
    """Find a column by header name, or reserve the next free slot for it.
    next_col_holder is a 1-element list used as a mutable int (avoids
    re-scanning `header` after each addition)."""
    for j, h in enumerate(header):
        if h.strip().lower() == name.lower():
            return j
    c = next_col_holder[0]
    next_col_holder[0] += 1
    if write:
        ws.update_cell(1, c + 1, name)
        print(f"[HEADER] created '{name}' at col {_a1_col(c + 1)}")
    else:
        print(f"[HEADER] would create '{name}' at col {_a1_col(c + 1)} (dry-run)")
    return c


def main():
    write = "--write" in sys.argv
    mode = "WRITE" if write else "DRY-RUN"
    now_ist = datetime.now(IST)
    print(f"[fetch_dividends {VERSION}] {now_ist:%Y-%m-%d %H:%M IST} | mode={mode}")

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

    # Reserve/create the 4 new columns, appended after the last used header —
    # never touch or reorder any existing column.
    next_col = [len(header)]
    dy_c   = col_of(DIV_YIELD_HEADER)
    ldd_c  = col_of(LAST_DIV_DATE_HEADER)
    lbd_c  = col_of(LAST_BONUS_DATE_HEADER)
    lbr_c  = col_of(LAST_BONUS_RATIO_HEADER)
    new_needed = sum(1 for c in (dy_c, ldd_c, lbd_c, lbr_c) if c is None)
    if write and new_needed and (len(header) + new_needed) > ws.col_count:
        old_count = ws.col_count
        ws.add_cols((len(header) + new_needed) - old_count)
        print(f"[GRID] expanded sheet from {old_count} to {ws.col_count} columns")

    if dy_c is None:  dy_c  = _ensure_col(ws, header, DIV_YIELD_HEADER, next_col, write)
    if ldd_c is None: ldd_c = _ensure_col(ws, header, LAST_DIV_DATE_HEADER, next_col, write)
    if lbd_c is None: lbd_c = _ensure_col(ws, header, LAST_BONUS_DATE_HEADER, next_col, write)
    if lbr_c is None: lbr_c = _ensure_col(ws, header, LAST_BONUS_RATIO_HEADER, next_col, write)

    dy_l, ldd_l, lbd_l, lbr_l = (_a1_col(c + 1) for c in (dy_c, ldd_c, lbd_c, lbr_c))
    print(f"[COLS] {DIV_YIELD_HEADER}={dy_l} {LAST_DIV_DATE_HEADER}={ldd_l} "
          f"{LAST_BONUS_DATE_HEADER}={lbd_l} {LAST_BONUS_RATIO_HEADER}={lbr_l}")

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

    print(f"[YF] fetching dividend/split history for {len(targets)} symbols "
          f"(per-symbol — no bulk endpoint for corporate-action history) ...")

    cutoff_ttm = now_ist - timedelta(days=365)
    dy_updates, ldd_updates, lbd_updates, lbr_updates = [], [], [], []
    fetch_errors = 0
    no_div = 0
    for n, (sheet_row, nse, yf_sym, cmp_val) in enumerate(targets, start=1):
        try:
            t = yf.Ticker(yf_sym)
            divs = t.dividends
            splits = t.splits
        except Exception as e:
            fetch_errors += 1
            print(f"  [SKIP] {nse}: fetch failed ({e}) — left unchanged")
            continue

        if divs is not None and len(divs):
            last_div_ts = divs.index[-1]
            ldd_updates.append((sheet_row, last_div_ts.strftime("%Y-%m-%d")))
            if cmp_val and cmp_val > 0:
                ttm_sum = float(divs[divs.index >= cutoff_ttm].sum())
                if ttm_sum > 0:
                    dy_updates.append((sheet_row, round(ttm_sum / cmp_val * 100.0, 2)))
        else:
            no_div += 1

        if splits is not None and len(splits):
            last_split_ts = splits.index[-1]
            lbd_updates.append((sheet_row, last_split_ts.strftime("%Y-%m-%d")))
            lbr_updates.append((sheet_row, round(float(splits.iloc[-1]), 3)))

        if n % 40 == 0:
            print(f"  [PROGRESS] {n}/{len(targets)} symbols processed")

    print(f"[DIV] {len(ldd_updates)} symbols have dividend history "
          f"({len(dy_updates)} with a computable TTM yield, {no_div} never paid a dividend) "
          f"| {fetch_errors} fetch errors (left unchanged)")
    print(f"[BONUS/SPLIT] {len(lbd_updates)} symbols have a split/bonus-style event on record")

    # Sanity check: highest trailing yields — a quick eyeball that the numbers
    # are sane before writing (VEDL/COALINDIA-style PSU/mining names are
    # expected to lead; a >20% "yield" would be a red flag worth checking).
    if dy_updates:
        rowmap = {t[0]: t[1] for t in targets}
        top = sorted(dy_updates, key=lambda x: -x[1])[:10]
        print("\n  Highest trailing 12-month dividend yield (sanity check):")
        for sr, y in top:
            print(f"    {rowmap[sr]:16} {y:.2f}%")

    if not write:
        print("\n[DRY-RUN] nothing written. Re-run with --write to update the sheet.")
        return 0

    body = [{"range": f"{dy_l}{sr}",  "values": [[v]]} for sr, v in dy_updates]
    body += [{"range": f"{ldd_l}{sr}", "values": [[v]]} for sr, v in ldd_updates]
    body += [{"range": f"{lbd_l}{sr}", "values": [[v]]} for sr, v in lbd_updates]
    body += [{"range": f"{lbr_l}{sr}", "values": [[v]]} for sr, v in lbr_updates]

    CHUNK = 200
    written = 0
    for k in range(0, len(body), CHUNK):
        part = body[k:k + CHUNK]
        ws.batch_update(part, value_input_option="USER_ENTERED")
        written += len(part)
        time.sleep(1.0)
    print(f"[WRITE] updated {written} cells in {NIFTY200} "
          f"({len(dy_updates)} yield + {len(ldd_updates)} last-div-date + "
          f"{len(lbd_updates)} last-bonus-date + {len(lbr_updates)} last-bonus-ratio). "
          f"INFORMATIONAL ONLY — not read by any gate or scoring formula.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
