"""
AI360 NSE Holiday Auto-Fetcher — v1.1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fetches next year's NSE trading holidays and stores them in BotMemory sheet.
trading_bot.py reads HOLIDAYS_NEXT from BotMemory and merges with hardcoded list.

Runs: 1st December every year (fetch_holidays.yml)
Source: NSE official holiday calendar API
Fallback: Known approximate 2027 Indian public holidays

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
    "2027-01-26",  # Republic Day (Tuesday)
    "2027-03-26",  # Holi (Friday) — approx
    "2027-04-01",  # Mahavir Jayanti — approx
    "2027-04-02",  # Good Friday
    "2027-04-14",  # Ambedkar Jayanti / Dr. B.R. Ambedkar Jayanti
    "2027-05-01",  # Maharashtra Day / Labour Day
    "2027-06-17",  # Eid ul-Adha — approx
    "2027-08-15",  # Independence Day (Sunday — no exchange trading anyway)
    "2027-08-23",  # Ganesh Chaturthi — approx
    "2027-10-02",  # Gandhi Jayanti (Saturday)
    "2027-10-19",  # Dussehra — approx
    "2027-11-07",  # Diwali Laxmi Puja — approx
    "2027-11-08",  # Diwali Balipratipada — approx
    "2027-11-15",  # Gurunanak Jayanti — approx
    "2027-12-25",  # Christmas
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
        holidays = []
        for month_data in data.values():
            for entry in month_data:
                date_str = entry.get("tradingDate", "")
                if date_str:
                    # NSE returns dd-MMM-yyyy format like "26-Jan-2026"
                    try:
                        dt = datetime.strptime(date_str, "%d-%b-%Y")
                        if dt.year == year:
                            holidays.append(dt.strftime("%Y-%m-%d"))
                    except ValueError:
                        pass
        holidays.sort()
        print(f"[NSE] Fetched {len(holidays)} holidays for {year}")
        return holidays

    except Exception as e:
        print(f"[NSE] API fetch failed: {e}")
        return []

def main():
    now  = datetime.now(IST)
    year = now.year + 1  # fetch NEXT year's holidays
    print(f"[HOLIDAYS] Fetching NSE holidays for {year}...")

    # Try NSE API first, fallback to hardcoded
    holidays = fetch_nse_holidays(year)
    if not holidays:
        if year == 2027:
            holidays = FALLBACK_2027
            print(f"[HOLIDAYS] Using fallback 2027 list ({len(holidays)} dates)")
        else:
            print(f"[HOLIDAYS] No data available for {year} — skipping")
            return

    # Store in BotMemory: key HOLIDAYS_2027 (or whatever year)
    key   = f"HOLIDAYS_{year}"
    value = ",".join(holidays)

    wb = _connect()
    bm = wb.worksheet(BM_TAB)
    _bm_set(bm, key, value)
    print(f"[HOLIDAYS] Stored {key} = {len(holidays)} dates in BotMemory")
    print(f"  Dates: {', '.join(holidays)}")


if __name__ == "__main__":
    main()
