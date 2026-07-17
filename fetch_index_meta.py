"""
fetch_index_meta.py — Nifty200 membership + F&O eligibility maintenance — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY THIS EXISTS (found 2026-07-17):
  The Nifty200 sheet had silently drifted from the real index: 17 current
  Nifty 200 members were missing (GROWW, LENSKART, LGEINDIA, TATACAP, IRCTC,
  MRF, ...) and 26 sheet stocks had exited the index (incl. IEX while it held a
  live WAITING entry). Separately, SEBI's 2025 F&O eligibility purge removed
  derivatives from stocks the system still treated as option-tradable — the
  AppScript's hardcoded F_AND_O_LIQUID_STOCKS list still contained IRCTC,
  TATAMOTORS (pre-demerger) and ZOMATO (pre-rename). Hardcoded lists rot; this
  project has been burned by them before (holiday list outage 2026-05-27,
  year-locked expiry list). This feed keeps the SHEET the single live source.

WHAT THIS DOES (weekly, Saturday — markets closed):
  1. Downloads the OFFICIAL lists with a browser User-Agent:
       • ind_nifty200list.csv  (niftyindices.com — members + NSE macro Industry)
       • ind_nifty50list.csv   (niftyindices.com)
       • fo_mktlots.csv        (nsearchives.nseindia.com — F&O underlyings)
  2. Refreshes for every existing sheet row (matched BY SYMBOL, never position):
       • col AJ "Options": "N50" / "YES" / "" (no derivatives)
       • col AK "N200":    "YES" (current member) / "EX" (index-exited)
  3. DETECTS DRIFT and tells the owner via a Telegram system notice:
       • new index members not yet in the sheet (row-adding needs formula
         replication in cols C–AI — deliberately NOT automated; done with
         Claude in a session, see .internal-ops.md 2026-07-17)
       • sheet stocks newly exited from the index
     No drift → no Telegram noise, prints only.

SAFETY / DESIGN:
  • Finds columns by HEADER NAME ("Options", "N200") — never hardcoded letters.
  • DRY-RUN by default; the workflow passes --write.
  • Fail-open: any download failure → exit 1 WITHOUT touching the sheet
    (last-good tags stay; memberships change rarely, staleness is benign).
    The workflow's failure step notifies Telegram.
  • Never adds/removes rows, never touches any other column.

SCHEDULE (see .github/workflows/fetch_index_meta.yml):
  Saturday 10:00 IST weekly. ₹0 (public-repo Actions + free official CSVs).
"""

import os, sys, json, time, csv, io
from datetime import datetime
from urllib.request import Request, urlopen
import pytz

IST        = pytz.timezone("Asia/Kolkata")
VERSION    = "v1.0"
SHEET_NAME = "Ai360tradingAlgo"
NIFTY200   = "Nifty200"
SYM_HEADER = "NSE_SYMBOL"
OPT_HEADER = "Options"
N200_HEADER = "N200"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

URL_N200 = "https://niftyindices.com/IndexConstituent/ind_nifty200list.csv"
URL_N50  = "https://niftyindices.com/IndexConstituent/ind_nifty50list.csv"
URL_FO   = "https://nsearchives.nseindia.com/content/fo/fo_mktlots.csv"


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
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)
    return gspread.authorize(creds).open(SHEET_NAME)


def _download(url):
    req = Request(url, headers={"User-Agent": UA})
    return urlopen(req, timeout=30).read().decode("utf-8-sig", errors="replace")


def _telegram(msg):
    """System notice to the Basic channel — same convention as workflow failure
    notices. Fail-open: missing creds / network error just prints."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat = os.environ.get("CHAT_ID_BASIC", "")
    if not token or not chat:
        print("[NOTIFY] Telegram creds missing — printed only")
        return
    try:
        req = Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=json.dumps({"chat_id": chat, "text": msg, "parse_mode": "HTML"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        urlopen(req, timeout=10).read()
        print("[NOTIFY] drift notice sent")
    except Exception as e:
        print(f"[NOTIFY] send failed (fail-open): {e}")


def main():
    write = "--write" in sys.argv
    print(f"[fetch_index_meta {VERSION}] {datetime.now(IST):%Y-%m-%d %H:%M IST} | "
          f"mode={'WRITE' if write else 'DRY-RUN'}")

    # ── 1. official lists (any failure → abort untouched, exit 1) ─────────────
    try:
        n200 = {r["Symbol"].strip(): r["Industry"].strip()
                for r in csv.DictReader(io.StringIO(_download(URL_N200)))}
        n50 = {r["Symbol"].strip()
               for r in csv.DictReader(io.StringIO(_download(URL_N50)))}
        fo = set()
        for i, line in enumerate(_download(URL_FO).splitlines()):
            if i == 0:
                continue
            p = [x.strip() for x in line.split(",")]
            if len(p) > 1 and p[1] and not p[0].startswith("NIFTY"):
                fo.add(p[1])
    except Exception as e:
        print(f"[FATAL] official list download failed — sheet untouched (fail-open): {e}")
        return 1
    if len(n200) < 150 or len(n50) < 40 or len(fo) < 100:
        print(f"[FATAL] lists look truncated (n200={len(n200)} n50={len(n50)} fo={len(fo)}) "
              f"— refusing to write from suspect data")
        return 1
    print(f"[LISTS] Nifty200={len(n200)} Nifty50={len(n50)} F&O stocks={len(fo)}")

    # ── 2. sheet state ─────────────────────────────────────────────────────────
    sh = _connect()
    ws = sh.worksheet(NIFTY200)
    header = ws.row_values(1)

    def col_of(name):
        for j, h in enumerate(header):
            if h.strip().lower() == name.lower():
                return j
        return None

    sym_c, opt_c, n200_c = col_of(SYM_HEADER), col_of(OPT_HEADER), col_of(N200_HEADER)
    if sym_c is None or opt_c is None or n200_c is None:
        print(f"[FATAL] columns not found: {SYM_HEADER}={sym_c} {OPT_HEADER}={opt_c} {N200_HEADER}={n200_c}")
        return 1
    opt_l, n200_l = _a1_col(opt_c + 1), _a1_col(n200_c + 1)

    rows = ws.get_all_values()[1:]
    sheet = {}                      # symbol → (sheet_row, cur_opt, cur_n200)
    for i, r in enumerate(rows, start=2):
        raw = (r[sym_c] if len(r) > sym_c else "").strip()
        if not raw or "NIFTY" in raw.upper():
            continue
        sym = raw.replace("NSE:", "").strip()
        sheet[sym] = (i,
                      (r[opt_c] if len(r) > opt_c else "").strip(),
                      (r[n200_c] if len(r) > n200_c else "").strip())

    # ── 3. compute updates + drift ─────────────────────────────────────────────
    body, changes = [], []
    for sym, (row, cur_opt, cur_n200) in sheet.items():
        want_opt = "N50" if sym in n50 else ("YES" if sym in fo else "")
        want_n200 = "YES" if sym in n200 else "EX"
        if want_opt != cur_opt:
            body.append({"range": f"{opt_l}{row}", "values": [[want_opt]]})
            changes.append(f"{sym}: Options {cur_opt or '(blank)'} → {want_opt or '(blank)'}")
        if want_n200 != cur_n200:
            body.append({"range": f"{n200_l}{row}", "values": [[want_n200]]})
            changes.append(f"{sym}: N200 {cur_n200 or '(blank)'} → {want_n200}")

    missing = sorted(set(n200) - set(sheet))
    print(f"[SHEET] {len(sheet)} stocks | tag updates: {len(body)} | "
          f"index members missing from sheet: {len(missing)}")
    for c in changes:
        print(f"  [CHANGE] {c}")
    for m in missing:
        print(f"  [MISSING] {m} ({n200[m]}) — needs a new row (manual/Claude session)")

    # ── 4. write + notify ──────────────────────────────────────────────────────
    if write and body:
        for k in range(0, len(body), 200):
            ws.batch_update(body[k:k + 200], value_input_option="USER_ENTERED")
            time.sleep(1.0)
        print(f"[WRITE] {len(body)} tag cells updated")
    elif not write:
        print("[DRY-RUN] nothing written")

    if write and (changes or missing):
        msg = ("🔄 <b>System Notice — AI360Trading</b>\n\n"
               "<b>NSE index/F&amp;O membership drift detected</b> (weekly check):\n")
        if changes:
            msg += "\n".join("• " + c for c in changes[:15])
            if len(changes) > 15:
                msg += f"\n… and {len(changes) - 15} more (see run log)"
            msg += "\n"
        if missing:
            msg += ("\n⚠️ <b>New Nifty200 members NOT in the sheet yet</b> "
                    f"(need rows added): {', '.join(missing)}\n")
        msg += ("\n<i>Tags in the sheet are already refreshed automatically. "
                "This is a system message, not a trade signal.</i>")
        _telegram(msg)
    return 0


def _a1_col(n: int) -> str:
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


if __name__ == "__main__":
    sys.exit(main())
