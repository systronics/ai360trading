import requests
import pandas as pd
from datetime import datetime
import pytz

# Set Timezone to IST
IST = pytz.timezone('Asia/Kolkata')

def get_day_mode():
    """Returns 'market', 'weekend', or 'holiday'."""
    now = datetime.now(IST)
    
    # 1. Check Weekend
    if now.weekday() >= 5: # 5=Saturday, 6=Sunday
        return "weekend"
    
    # 2. Check Indian Market Holiday
    if is_market_holiday(now.strftime('%d-%b-%Y')):
        return "holiday"
    
    return "market"

def is_market_holiday(date_str=None):
    """
    Checks if the given date (DD-Mon-YYYY) is an NSE holiday.
    Example: '15-Aug-2026'
    """
    if not date_str:
        date_str = datetime.now(IST).strftime('%d-%b-%Y')

    # Primary: Official NSE API
    try:
        url = "https://www.nseindia.com/api/holiday-master?type=trading"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        # Note: NSE often requires a session cookie; if it fails, we hit the fallback.
        resp = requests.get(url, headers=headers, timeout=5)
        holidays = resp.json().get('tradingHoliday', [])
        holiday_list = [h['tradingDate'] for h in holidays]
        if date_str in holiday_list:
            return True
    except:
        pass

    # Fallback: Manual Hardcoded List for 2026 (Manual Hard Work)
    # This ensures your bot is safe even if the API is blocked.
    fallback_holidays = [
        "26-Jan-2026", "06-Mar-2026", "27-Mar-2026", "02-Apr-2026", 
        "10-Apr-2026", "01-May-2026", "15-Aug-2026", "02-Oct-2026",
        "22-Oct-2026", "23-Oct-2026", "05-Nov-2026", "25-Dec-2026"
    ]
    
    return date_str in fallback_holidays

def get_holiday_name():
    """Optional: Returns the name of the holiday for social media captions."""
    # Logic to return 'Diwali' or 'Independence Day'
    return "Market Holiday"

if __name__ == "__main__":
    print(f"Today's Mode: {get_day_mode().upper()}")
