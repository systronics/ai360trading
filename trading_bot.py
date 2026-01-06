import os, json, gspread, requests, pandas as pd, pyotp, pytz
from dhanhq import dhanhq, DhanLogin
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIG ---
LIVE_MODE = True  
CAP_PER_TRADE = 10000 
MAX_TRADES = 5

def get_dhan_client():
    """Fully automated login using TOTP and PIN"""
    client_id = os.environ.get('DHAN_CLIENT_ID')
    totp_key = os.environ.get('DHAN_TOTP_KEY')
    pin = os.environ.get('DHAN_PIN')
    
    # Generate the 6-digit TOTP code
    totp_gen = pyotp.TOTP(totp_key)
    current_otp = totp_gen.now()
    
    # Authenticate via PIN + TOTP flow
    login = DhanLogin(client_id)
    auth_data = login.generate_token(pin, current_otp)
    
    # Extract access token from the dictionary response
    access_token = auth_data.get('access_token')
    if not access_token:
        raise Exception(f"Login Failed: {auth_data}")
        
    return dhanhq(client_id, access_token)

def send_telegram(message):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try: requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10)
    except: pass

def get_sec_id(symbol):
    """Fetches Security ID from Dhan's Scrip Master"""
    try:
        url = "https://images.dhan.co/api-data/api-scrip-master.csv"
        df = pd.read_csv(url)
        # Search for Equity segment specifically
        match = df[df['SEM_TRADING_SYMBOL'] == f"{symbol.strip().upper()}-EQ"]
        return str(match.iloc[0]['SEM_SMST_SECURITY_ID']) if not match.empty else None
    except Exception as e:
        print(f"Scrip Master Error: {e}")
        return None

def run_trading_cycle():
    try:
        # 1. Connect to Sheet
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
        service_account_info = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Ai360tradingAlgo").worksheet("AlertLog")

        # 2. Kill Switch & Heartbeat (Q1: Header, Q2: YES/NO, Q3: Time)
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
        sheet.update_cell(3, 17, f"Heartbeat: {now_ist}")
        
        # Kill Switch Check
        if str(sheet.cell(2, 17).value).strip().upper() != "YES":
            print("🛑 Kill Switch is NO. Bot stopped.")
            return

        # 3. Initialize Dhan
        dhan = get_dhan_client()

        # 4. Trading Logic
        records = sheet.get_all_records()
        active_trades = [r for r in records if "TRADED" in str(r.get('Status')) and "EXIT" not in str(r.get('Status'))]
        active_count = len(active_trades)

        for i, row in enumerate(records):
            row_num = i + 2
            symbol = str(row.get('Symbol')).strip()
            price = float(row.get('Live Price') or row.get('Price', 0))
            status = str(row.get('Status', ''))

            # --- BUY LOGIC ---
            if not status and symbol and active_count < MAX_TRADES:
                sec_id = get_sec_id(symbol)
                qty = int(CAP_PER_TRADE / price) if price > 0 else 0
                
                if LIVE_MODE and sec_id and qty > 0:
                    # Place Order
                    dhan.place_order(security_id=sec_id, exchange_segment=dhan.NSE, transaction_type=dhan.BUY, 
                                     quantity=qty, order_type=dhan.MARKET, product_type=dhan.CNC, price=0)
                    
                    sheet.update_cell(row_num, 11, "TRADED (LIVE)")
                    send_telegram(f"🚀 <b>BUY:</b> {symbol} @ {price}")
                    active_count += 1
            
            # --- SELL LOGIC ---
            elif "TRADED" in status and "EXIT" not in status:
                target = float(row.get('Target') or 0)
                sl = float(row.get('StopLoss') or 0)
                
                if (target > 0 and price >= target) or (sl > 0 and price <= sl):
                    if LIVE_MODE:
                        sec_id = get_sec_id(symbol)
                        qty = int(CAP_PER_TRADE / price)
                        dhan.place_order(security_id=sec_id, exchange_segment=dhan.NSE, transaction_type=dhan.SELL, 
                                         quantity=qty, order_type=dhan.MARKET, product_type=dhan.CNC, price=0)
                    
                    sheet.update_cell(row_num, 11, "EXITED")
                    send_telegram(f"💰 <b>EXIT:</b> {symbol} @ {price}")

    except Exception as e:
        print(f"System Error: {e}")
        send_telegram(f"⚠️ <b>CRITICAL BOT ERROR:</b> {e}")

if __name__ == "__main__":
    run_trading_cycle()
