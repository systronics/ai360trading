import os, json, gspread, requests, pandas as pd, pyotp, pytz
from dhanhq import dhanhq  # Standard import for v2.0+
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIG ---
LIVE_MODE = False  # Set to True only when ready for real money
CAP_PER_TRADE = 10000 
MAX_TRADES = 5

def get_dhan_client():
    """Automated login using TOTP and PIN for DhanHQ v2.0+"""
    client_id = os.environ.get('DHAN_CLIENT_ID')
    totp_key = os.environ.get('DHAN_TOTP_KEY')
    pin = os.environ.get('DHAN_PIN')
    
    # Generate TOTP
    totp_gen = pyotp.TOTP(totp_key)
    current_otp = totp_gen.now()
    
    # In v2.0+, we use the dhanhq class to generate the token
    # We initialize with a dummy token first to access the login methods
    temp_client = dhanhq(client_id, "")
    
    auth_data = temp_client.generate_token(pin, current_otp)
    access_token = auth_data.get('data', {}).get('access_token') or auth_data.get('access_token')
    
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
        # Match symbol-EQ (e.g., RELIANCE-EQ)
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

        # 2. Kill Switch & Heartbeat (Column Q is 17)
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
        
        # Kill Switch Check (Row 2, Column 17 / Q2)
        kill_switch = str(sheet.cell(2, 17).value).strip().upper()
        sheet.update_cell(3, 17, f"Last Run: {now_ist}") # Q3 Heartbeat

        if kill_switch != "YES":
            print("🛑 Kill Switch is NOT 'YES'. Bot stopped.")
            return

        # 3. Initialize Dhan
        dhan = get_dhan_client()

        # 4. Trading Logic
        records = sheet.get_all_records()
        
        # Correctly count active trades to avoid exceeding MAX_TRADES
        active_trades = [r for r in records if "TRADED" in str(r.get('Status', '')) and "EXIT" not in str(r.get('Status', ''))]
        active_count = len(active_trades)

        for i, row in enumerate(records):
            row_num = i + 2 # Header is row 1
            symbol = str(row.get('Symbol', '')).strip()
            
            # Ensure price is a valid number
            try:
                price = float(row.get('Live Price') or row.get('Price', 0))
            except:
                price = 0
                
            status = str(row.get('Status', '')).strip()

            # --- BUY LOGIC (For Empty Status slots) ---
            if not status and symbol and active_count < MAX_TRADES:
                sec_id = get_sec_id(symbol)
                qty = int(CAP_PER_TRADE / price) if price > 0 else 0
                
                if sec_id and qty > 0:
                    if LIVE_MODE:
                        dhan.place_order(security_id=sec_id, exchange_segment=dhan.NSE, transaction_type=dhan.BUY, 
                                        quantity=qty, order_type=dhan.MARKET, product_type=dhan.CNC, price=0)
                        sheet.update_cell(row_num, 11, "TRADED (LIVE)")
                    else:
                        sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                    
                    send_telegram(f"🚀 <b>BUY:</b> {symbol} @ {price}")
                    active_count += 1
            
            # --- SELL LOGIC (For Active Trades) ---
            elif "TRADED" in status and "EXIT" not in status:
                try:
                    target = float(row.get('Target') or 0)
                    sl = float(row.get('StopLoss') or 0)
                except:
                    target, sl = 0, 0
                
                if (target > 0 and price >= target) or (sl > 0 and price <= sl):
                    if LIVE_MODE:
                        sec_id = get_sec_id(symbol)
                        qty = int(CAP_PER_TRADE / price) if price > 0 else 0
                        dhan.place_order(security_id=sec_id, exchange_segment=dhan.NSE, transaction_type=dhan.SELL, 
                                         quantity=qty, order_type=dhan.MARKET, product_type=dhan.CNC, price=0)
                    
                    sheet.update_cell(row_num, 11, "EXITED")
                    trigger_type = "TARGET 🎯" if price >= target else "STOPLOSS 🛑"
                    send_telegram(f"💰 <b>EXIT ({trigger_type}):</b> {symbol} @ {price}")

    except Exception as e:
        print(f"System Error: {e}")
        send_telegram(f"⚠️ <b>CRITICAL BOT ERROR:</b> {e}")

if __name__ == "__main__":
    run_trading_cycle()
