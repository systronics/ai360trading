"""
AI360 NSE Holiday Auto-Fetcher — v1.3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fetches NSE trading holidays from the official API and stores them in BotMemory
(HOLIDAYS_<year>). trading_bot.py + appscript.gs merge these with their hardcoded
lists, so the authoritative NSE dates auto-extend the system every year.

v1.3 (2026-05-30) — AUTONOMY HARDENING (run-for-years, self-healing):
  • Now fetches BOTH the CURRENT and NEXT year every run (was next-year only).
    Writing the current year from the authoritative NSE API auto-captures any
    date the hardcoded baseline missed — and picks up mid-year SPECIAL holidays
    NSE announces during the year (election days, mourning days, etc.).
  • Runs MONTHLY now (was once on Dec 1). A single failed Dec-1 fetch no longer
    means a whole year is missed — the next month retries automatically.
  • Sanity check: only stores a year's list if it has a plausible count
    (>= MIN_PLAUSIBLE dates) so a glitchy partial fetch never overwrites a good
    stored list with junk.

Runs: 1st of every month (fetch_holidays.yml)
Source: NSE official holiday calendar API
Fallback: known approximate 2027 list (next-year only, if API has no data yet)

No code changes needed each year — fully autonomous.
"""

import os, json, requests, time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

IST        = pytz.timezone("Asia/Kolkata")
SHEET_NAME = "Ai360tradingAlgo"
BM_TAB     = "BotMemory"

# Approximate NSE trading holidays 2027 (fallback if API fails)
# NSE observes: Republic Day, Holi, Good Friday, Ambedkar Jayanti (Apr 14),
# Maharashtra Day (May 1), Eid, Independence Day, Ganesh Chaturthi, Gandhi Jayanti,
# Dussehra, Diwali Laxmi Puja, Diwali Balipratipada, Gurunanak Jayanti, Christmas
FALLBACK_2027 = [
    # NOTE: Fallback only — NSE API (fetch_nse_holidays) is the primary path.
    # All "approx" dates below should be verified once NSE publishes the official
    # 2027 calendar (typically Dec 2026). Sundays excluded since NSE is closed anyway.
    "2027-01-26",  # Republic Day (Tuesday)
    "2027-03-26",  # Holi (Friday) — approx
    "2027-04-01",  # Mahavir Jayanti — approx
    "2027-04-02",  # Good Friday
    "2027-04-14",  # Ambedkar Jayanti
    "2027-05-01",  # Maharashtra Day / Labour Day
    "2027-06-17",  # Eid ul-Adha — approx
    "2027-08-23",  # Ganesh Chaturthi — approx
    "2027-10-19",  # Dussehra — approx
    "2027-11-07",  # Diwali Laxmi Puja — approx
    "2027-11-08",  # Diwali Balipratipada — approx
    "2027-11-15",  # Gurunanak Jayanti — approx
    "2027-12-25",  # Christmas
    # Removed: 2027-08-15 (Sunday — NSE closed anyway)
    # Removed: 2027-10-02 (Saturday — NSE closed anyway)
]

def _connect():
    # v1.1: explicit cred validation — fails with clear message instead of cryptic FileNotFoundError
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        try:
            with open("service_account.json") as f:
                raw = f.read().strip()
        except FileNotFoundError:
            raise SystemExit("[CREDS] GCP_SERVICE_ACCOUNT_JSON env var not set and service_account.json not found locally")
    try:
        creds_dict = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"[CREDS] Failed to parse GCP credentials JSON: {e}")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    gc    = gspread.authorize(creds)
    return gc.open(SHEET_NAME)

def _bm_set(bm_sheet, key, value):
    """Write or update a key in BotMemory sheet."""
    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M")
    try:
        data = bm_sheet.get_all_values()
        for i, row in enumerate(data[1:], start=2):
            if row and row[0] == key:
                bm_sheet.update(f"A{i}:E{i}", [[key, value, now_str, "", "SYSTEM"]])
                return
        bm_sheet.append_row([key, value, now_str, "", "SYSTEM"])
    except Exception as e:
        print(f"[BM] Set {key}: {e}")

def fetch_nse_holidays(year):
    """
    Attempt to fetch NSE holidays via NSE API.
    NSE API requires browser-like headers.
    Returns list of YYYY-MM-DD strings or [] on failure.
    """
    try:
        session = requests.Session()
        # NSE requires a session cookie from the main page first
        session.get("https://www.nseindia.com", timeout=10,
                    headers={"User-Agent": "Mozilla/5.0"})
        time.sleep(1)

        r = session.get(
            "https://www.nseindia.com/api/holiday-master?type=trading",
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "application/json",
                "Referer": "https://www.nseindia.com/",
            }
        )
        if r.status_code != 200:
            print(f"[NSE] API returned {r.status_code}")
            return []

        data = r.json()
        # NSE holiday-master returns a dict keyed by SEGMENT:
        #   {"CM":[...], "FO":[...], "CD":[...], "COM":[...], ...}
        # We want EQUITIES only = "CM" (Capital Market). Summing every segment
        # (the old bug) produced ~238 duplicate dates and would mark almost every
        # day a holiday. Use CM; fall back to any one list segment if CM absent.
        segment = data.get("CM")
        if not isinstance(segment, list) or not segment:
            segment = next((v for v in data.values() if isinstance(v, list)), [])
        seen, holidays = set(), []
        for entry in segment:
            date_str = (entry or {}).get("tradingDate", "")
            if not date_str:
                continue
            try:
                dt = datetime.strptime(date_str, "%d-%b-%Y")  # e.g. "26-Jan-2026"
            except ValueError:
                continue
            if dt.year == year:
                iso = dt.strftime("%Y-%m-%d")
                if iso not in seen:
                    seen.add(iso)
                    holidays.append(iso)
        holidays.sort()
        print(f"[NSE] Fetched {len(holidays)} equity (CM) holidays for {year}")
        return holidays

    except Exception as e:
        print(f"[NSE] API fetch failed: {e}")
        return []

MIN_PLAUSIBLE = 8    # a real NSE year has ~14-17 weekday holidays; <8 = bad fetch
MAX_PLAUSIBLE = 25   # >25 = parser grabbed multiple segments / junk — reject

def main():
    now = datetime.now(IST)
    # v1.3: fetch CURRENT + NEXT year every run, monthly.
    years = [now.year, now.year + 1]
    print(f"[HOLIDAYS] Fetching NSE holidays for {years}...")

    wb = _connect()
    bm = wb.worksheet(BM_TAB)

    stored = 0
    for year in years:
        holidays = fetch_nse_holidays(year)

        # Fallback only for next year when the API has nothing yet.
        if not holidays and year == 2027:
            holidays = FALLBACK_2027
            print(f"[HOLIDAYS] {year}: API empty — using fallback ({len(holidays)} dates)")

        if not holidays:
            print(f"[HOLIDAYS] {year}: no data — leaving any existing value untouched")
            continue

        # Sanity gate — reject implausible counts (partial fetch, or the
        # all-segments bug that yields ~238). Never overwrite a good list with junk.
        if not (MIN_PLAUSIBLE <= len(holidays) <= MAX_PLAUSIBLE):
            print(f"[HOLIDAYS] {year}: {len(holidays)} dates outside "
                  f"[{MIN_PLAUSIBLE},{MAX_PLAUSIBLE}] — implausible, skipping to protect existing value")
            continue

        key = f"HOLIDAYS_{year}"
        _bm_set(bm, key, ",".join(holidays))
        stored += 1
        print(f"[HOLIDAYS] Stored {key} = {len(holidays)} dates")
        print(f"  {', '.join(holidays)}")

    print(f"[HOLIDAYS] Done — {stored} year(s) updated in BotMemory")


if __name__ == "__main__":
    main()
