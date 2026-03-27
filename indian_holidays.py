"""
indian_holidays.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Shared Indian market holiday detection for ALL scripts.
Import this in any script that needs to know if market is closed.

Usage:
    from indian_holidays import is_market_holiday, get_day_mode

    if is_market_holiday():
        # run holiday content
    
    mode = get_day_mode()
    # returns: "market" | "weekend" | "holiday"

Strategy:
    1. Try NSE official API — works forever, zero maintenance
    2. If API fails — fallback to hardcoded major Indian holidays
    3. If date not in either — assume market day

Last updated: March 2026
"""

import requests
from datetime import datetime
import pytz

# ─── IST timezone ─────────────────────────────────────────────────────────────
IST = pytz.timezone("Asia/Kolkata")

# ─── FALLBACK: Major Indian market holidays (permanent, recurring approx dates)
# These are approximate — NSE API is the accurate source.
# Fallback only used when NSE API is unreachable.
# Format: (month, day) — year-independent
FALLBACK_HOLIDAYS = [
    # Republic Day
    (1, 26),
    # Mahashivratri (approx Feb)
    (2, 26),
    # Holi (approx March)
    (3, 14),
    # Ram Navami (approx April)
    (4, 6),
    # Dr. Ambedkar Jayanti
    (4, 14),
    # Good Friday (approx April)
    (4, 18),
    # Maharashtra Day
    (5, 1),
    # Buddha Purnima (approx May)
    (5, 12),
    # Eid ul-Fitr (approx — varies)
    (3, 31),
    # Eid ul-Adha (approx — varies)
    (6, 7),
    # Muharram (approx — varies)
    (7, 6),
    # Independence Day
    (8, 15),
    # Janmashtami (approx August)
    (8, 16),
    # Ganesh Chaturthi (approx September)
    (8, 27),
    # Mahatma Gandhi Jayanti / Dussehra (approx October)
    (10, 2),
    (10, 2),
    # Diwali Laxmi Puja (approx October/November — 2 days)
    (10, 20),
    (10, 21),
    # Diwali Balipratipada
    (10, 22),
    # Gurunanak Jayanti (approx November)
    (11, 5),
    # Christmas
    (12, 25),
]

# ─── NSE API holiday fetch ────────────────────────────────────────────────────
def _fetch_nse_holidays():
    """
    Fetch official NSE trading holidays for current year.
    Returns set of date strings in YYYY-MM-DD format.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/",
        }
        # Step 1: Get cookies first (NSE requires session cookie)
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=10)

        # Step 2: Fetch holiday list
        resp = session.get(
            "https://www.nseindia.com/api/holiday-master?type=trading",
            headers=headers,
            timeout=10
        )
        if not resp.ok:
            return None

        data = resp.json()
        holidays = set()

        # NSE returns dict with month keys
        for month_key, entries in data.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                # Date format from NSE: "26-Jan-2026"
                date_str = entry.get("tradingDate", "")
                if date_str:
                    try:
                        dt = datetime.strptime(date_str.strip(), "%d-%b-%Y")
                        holidays.add(dt.strftime("%Y-%m-%d"))
                    except Exception:
                        pass

        if holidays:
            print(f"  📅 NSE holidays loaded: {len(holidays)} dates for {datetime.now().year}")
            return holidays

    except Exception as e:
        print(f"  ⚠️  NSE API unavailable ({e}) — using fallback holiday list")

    return None


def _get_fallback_holidays():
    """
    Returns set of YYYY-MM-DD strings for current year
    based on approximate recurring holiday dates.
    """
    year = datetime.now().year
    holidays = set()
    for month, day in FALLBACK_HOLIDAYS:
        try:
            dt = datetime(year, month, day)
            holidays.add(dt.strftime("%Y-%m-%d"))
        except Exception:
            pass
    return holidays


# ─── Cache so we don't hit NSE API on every slide/article ────────────────────
_holiday_cache = None

def _get_holiday_set():
    global _holiday_cache
    if _holiday_cache is None:
        _holiday_cache = _fetch_nse_holidays() or _get_fallback_holidays()
    return _holiday_cache


# ─── PUBLIC FUNCTIONS ─────────────────────────────────────────────────────────
def is_weekend():
    """True if today is Saturday or Sunday IST."""
    return datetime.now(IST).weekday() >= 5


def is_market_holiday():
    """
    True if today is an Indian market holiday (weekday but market closed).
    Does NOT include weekends — check is_weekend() separately.
    """
    today = datetime.now(IST).strftime("%Y-%m-%d")
    return today in _get_holiday_set()


def is_non_market_day():
    """True if today is weekend OR market holiday."""
    return is_weekend() or is_market_holiday()


def get_day_mode():
    """
    Returns the content mode for today.
    
    "market"  → Normal weekday, market open
    "weekend" → Saturday or Sunday
    "holiday" → Weekday but market closed (Indian holiday)
    """
    if is_weekend():
        return "weekend"
    if is_market_holiday():
        return "holiday"
    return "market"


def get_holiday_name():
    """
    Returns name of today's holiday if available from NSE API, else generic string.
    """
    try:
        today = datetime.now(IST).strftime("%Y-%m-%d")
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/",
        }
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        resp = session.get(
            "https://www.nseindia.com/api/holiday-master?type=trading",
            headers=headers,
            timeout=10
        )
        if resp.ok:
            data = resp.json()
            for month_key, entries in data.items():
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    date_str = entry.get("tradingDate", "")
                    try:
                        dt = datetime.strptime(date_str.strip(), "%d-%b-%Y")
                        if dt.strftime("%Y-%m-%d") == today:
                            return entry.get("description", "Indian Market Holiday")
                    except Exception:
                        pass
    except Exception:
        pass
    return "Indian Market Holiday"


# ─── Quick test when run directly ────────────────────────────────────────────
if __name__ == "__main__":
    mode = get_day_mode()
    print(f"Today: {datetime.now(IST).strftime('%A, %d %B %Y')}")
    print(f"Mode: {mode}")
    if mode == "holiday":
        print(f"Holiday: {get_holiday_name()}")
    print(f"Is weekend: {is_weekend()}")
    print(f"Is market holiday: {is_market_holiday()}")
    print(f"Is non-market day: {is_non_market_day()}")
