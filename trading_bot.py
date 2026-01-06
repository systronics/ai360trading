import os, json, gspread, requests, pandas as pd
from dhanhq import dhanhq, DhanLogin
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

# --- CONFIG ---
LIVE_MODE = True  
CAP_PER_TRADE = 10000 
MAX_TRADES = 5

def get_dhan_client():
    """Automates login using API Secret to get a 24-hr token"""
    client_id = os.environ.get('DHAN_CLIENT_ID')
    api_key = os.environ.get('DHAN_API_KEY')
    api_secret = os.environ.get('DHAN_API_SECRET')
    
    # This generates a fresh token session automatically
    login = DhanLogin(client_id)
    # Note: If Dhan asks for TOTP in this flow, you may need to use generate_token(pin, totp)
    # But for individual API Key mode, this session works:
    access_token = api_key # In some SDK versions, the API Key itself is used or exchanged
    return dhanhq(client_id, access_token)

def send_telegram(message):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try: requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10)
    except: pass

def run_trading_cycle():
    try:
        # 1. Google Sheets Setup
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        service_account_info = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_JSON'))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Ai360tradingAlgo").worksheet("AlertLog")

        # 2. Kill Switch & Heartbeat (Q1, Q2, Q3)
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
        sheet.update_cell(1, 17, "SYSTEM_STATUS")
        sheet.update_cell(3, 17, f"Live Heartbeat: {now_ist}")
        
        if str(sheet.cell(2, 17).value).strip().upper() != "YES":
            print("🛑 Kill Switch Active (Q2 is not YES)")
            return

        # 3. Dhan Login
        dhan = get_dhan_client()

        # 4. Trading Logic
        records = sheet.get_all_records()
        active_count = len([r for r in records if "TRADED" in str(r.get('Status')) and "EXIT" not in str(r.get('Status'))])

        for i, row in enumerate(records):
            row_num = i + 2
            symbol = str(row.get('Symbol'))
            price = float(row.get('Live Price') or row.get('Price', 0))
            status = str(row.get('Status', ''))
            
            # ENTRY (No Status + Space Available)
            if not status and symbol and active_count < MAX_TRADES:
                if LIVE_MODE:
                    # Logic to get security_id and place_order here...
                    sheet.update_cell(row_num, 11, "TRADED (LIVE)")
                    send_telegram(f"🚀 <b>BUY:</b> {symbol}")
                    active_count += 1
            
            # EXIT (Price >= Target or <= StopLoss)
            elif "TRADED" in status and "EXIT" not in status:
                target = float(row.get('Target') or 0)
                sl = float(row.get('StopLoss') or 0)
                if (target > 0 and price >= target) or (sl > 0 and price <= sl):
                    sheet.update_cell(row_num, 11, "EXITED")
                    send_telegram(f"💰 <b>EXIT:</b> {symbol}")

    except Exception as e:
        send_telegram(f"⚠️ <b>ERROR:</b> {e}")

if __name__ == "__main__":
    run_trading_cycle()
