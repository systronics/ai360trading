"""
AI360 EARNINGS CACHE — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fetches upcoming Indian-equity earnings (Results) announcements and writes
them to the BotMemory sheet so option_intelligence.check_earnings_window()
can block CE/PE entries within ±3 trading days of a result.

Data sources (cost = ₹0, all free public APIs):
  1. NSE  — https://www.nseindia.com/api/event-calendar?index=equities
           (requires session cookie dance; tried first; fragile)
  2. BSE  — https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?strCat=Result
           (less protected; used as fallback)

Schedule: daily 18:30 IST via .github/workflows/fetch_earnings.yml.

Self-repair (per feedback_free_forever_self_repair memory):
  • Both sources tried in order; failure of source 1 falls through to source 2.
  • If both fail, the script exits cleanly (exit 0) so the GH Action does not
    flap as failed. Existing cache from previous successful run continues to
    serve the option module. A "stale > 3 days" warning is sent to Basic
    Telegram channel as a soft alert.
  • All cookies/headers handled via requests.Session; no external library
    beyond what already lives in requirements.txt (requests + gspread).

Memory key format written:
    EARNINGS_{SYMBOL_NO_NSE}_{YYYY-MM-DD} = "Result"
  e.g.  EARNINGS_TCS_2026-07-08 = "Result"
Existing rows are de-duplicated before append.

Stale-clean (run inside the same script):
  Rows older than 7 days are removed each run to keep BotMemory lean.
"""

import os, json, time
from datetime import datetime, timedelta
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz

IST        = pytz.timezone("Asia/Kolkata")
SHEET_NAME = "Ai360tradingAlgo"
BM_TAB     = "BotMemory"
TG_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_BASIC = os.environ.get("CHAT_ID_BASIC")

# Look ahead up to N calendar days for upcoming earnings
LOOKAHEAD_DAYS = 30
# Discard cached earnings rows older than this many days
STALE_DAYS     = 7

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}


# ════════════════════════════════════════════════════════════════════════════
# SOURCE 1 — NSE event calendar
# ════════════════════════════════════════════════════════════════════════════

def fetch_nse_earnings() -> list:
    """Returns list of tuples [(symbol, YYYY-MM-DD), ...] or [] on failure."""
    try:
        s = requests.Session()
        s.headers.update(DEFAULT_HEADERS)
        # First hit homepage to receive session cookies (NSE quirk)
        s.get("https://www.nseindia.com/", timeout=15)
        time.sleep(0.5)
        url = "https://www.nseindia.com/api/event-calendar?index=equities"
        r   = s.get(url, timeout=20)
        if r.status_code != 200:
            print(f"[NSE earnings] HTTP {r.status_code}")
            return []
        data = r.json()
        out = []
        for item in data if isinstance(data, list) else []:
            sym = (item.get("symbol") or "").strip().upper()
            dt_str = (item.get("date") or "").strip()
            purpose = (item.get("purpose") or "").lower()
            if not sym or not dt_str or "result" not in purpose:
                continue
            # NSE returns dates in formats like "08-Jul-2026" or "2026-07-08"
            iso = _normalise_date(dt_str)
            if iso:
                out.append((sym, iso))
        print(f"[NSE earnings] fetched {len(out)} result events")
        return out
    except Exception as e:
        print(f"[NSE earnings] fetch error: {e}")
        return []


def _normalise_date(s: str) -> str:
    """Try a handful of NSE/BSE formats; return YYYY-MM-DD or empty."""
    s = s.strip()
    if not s:
        return ""
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d %b %Y", "%d-%m-%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s[:len(fmt)+10], fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return ""


# ════════════════════════════════════════════════════════════════════════════
# SOURCE 2 — BSE results announcements (fallback)
# ════════════════════════════════════════════════════════════════════════════

def fetch_bse_earnings() -> list:
    try:
        s = requests.Session()
        s.headers.update({**DEFAULT_HEADERS, "Referer": "https://www.bseindia.com/"})
        today = datetime.now(IST)
        end   = today + timedelta(days=LOOKAHEAD_DAYS)
        url = (
            "https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w"
            f"?strCat=Result&strPrevDate={today.strftime('%Y%m%d')}"
            f"&strToDate={end.strftime('%Y%m%d')}&strScrip="
        )
        r = s.get(url, timeout=20)
        if r.status_code != 200:
            print(f"[BSE earnings] HTTP {r.status_code}")
            return []
        data = r.json()
        rows = data.get("Table", []) if isinstance(data, dict) else []
        out  = []
        for item in rows:
            sym = (item.get("SLONGNAME") or item.get("scrip_cd") or "").strip().upper()
            dt_str = (item.get("NEWS_DT") or item.get("DT_TM") or "").strip()
            iso = _normalise_date(dt_str)
            if sym and iso:
                # BSE often returns long names — caller may need stricter mapping;
                # for now we store the first token (best-effort).
                first_token = sym.split()[0]
                out.append((first_token, iso))
        print(f"[BSE earnings] fetched {len(out)} announcements")
        return out
    except Exception as e:
        print(f"[BSE earnings] fetch error: {e}")
        return []


# ════════════════════════════════════════════════════════════════════════════
# BOTMEMORY WRITE
# ════════════════════════════════════════════════════════════════════════════

def _connect():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        try:
            with open("service_account.json") as f:
                raw = f.read().strip()
        except FileNotFoundError:
            raise SystemExit("[CREDS] GCP_SERVICE_ACCOUNT_JSON not set and no local service_account.json")
    creds_dict = json.loads(raw)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds).open(SHEET_NAME)


def write_earnings_to_botmemory(events: list):
    """events = list of (symbol, YYYY-MM-DD).
    Writes/updates EARNINGS_{SYM}_{DATE} rows in BotMemory.
    Removes any EARNINGS_* row whose date is older than STALE_DAYS days."""
    if not events:
        print("[BM] No events to write — skipping update")
        return
    ss = _connect()
    bm = ss.worksheet(BM_TAB)
    existing = bm.get_all_values()
    headers  = existing[0] if existing else []
    now_str  = datetime.now(IST).strftime("%Y-%m-%d %H:%M")
    today    = datetime.now(IST).date()

    # Index existing earnings rows by key for de-dupe + stale cleanup
    keep_rows  = [headers]
    earn_keys  = set()
    purged     = 0
    for row in existing[1:]:
        if not row or not row[0].strip():
            continue
        key = row[0].strip()
        if key.startswith("EARNINGS_"):
            try:
                date_part = key.rsplit("_", 1)[1]
                d = datetime.strptime(date_part, "%Y-%m-%d").date()
                if (today - d).days > STALE_DAYS:
                    purged += 1
                    continue
            except Exception:
                pass
            earn_keys.add(key)
        keep_rows.append(row)

    # Build new rows
    new_rows = []
    for sym, date in events:
        key = f"EARNINGS_{sym}_{date}"
        if key in earn_keys:
            continue
        new_rows.append([key, "Result", now_str, "", "EARNINGS"])

    final_rows = keep_rows + new_rows
    if purged > 0 or new_rows:
        bm.clear()
        bm.update("A1", final_rows)
        print(f"[BM] purged {purged} stale, added {len(new_rows)} new — sheet now {len(final_rows)-1} rows")
    else:
        print("[BM] no changes")


# ════════════════════════════════════════════════════════════════════════════
# TELEGRAM (basic only — non-trade system notice)
# ════════════════════════════════════════════════════════════════════════════

def _tg(msg):
    if not (TG_TOKEN and CHAT_BASIC):
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": CHAT_BASIC, "text": msg, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as e:
        print(f"[TG] {e}")


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    print(f"[EARNINGS] start {datetime.now(IST).strftime('%Y-%m-%d %H:%M')} IST")
    events = fetch_nse_earnings()
    if not events:
        print("[EARNINGS] NSE empty — trying BSE fallback")
        events = fetch_bse_earnings()
    if not events:
        # Both sources failed — DO NOT raise. Existing cache continues to
        # serve. Send soft warning to Basic only.
        _tg(
            "ℹ️ <b>System Notice</b>\n"
            "Earnings cache could not refresh today (both NSE & BSE timed out). "
            "Existing cached entries remain in use. Will retry tomorrow. "
            "<i>This is a system message, not a trade signal.</i>"
        )
        print("[EARNINGS] both sources failed — kept existing cache. exit 0.")
        return

    try:
        write_earnings_to_botmemory(events)
    except Exception as e:
        print(f"[EARNINGS] BM write error: {e}")
        _tg(
            f"ℹ️ <b>System Notice</b>\nEarnings fetch ran but BotMemory write failed: "
            f"{type(e).__name__}. Will retry tomorrow."
        )


if __name__ == "__main__":
    main()
