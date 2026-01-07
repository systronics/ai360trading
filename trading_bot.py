import os, json, gspread, requests, pandas as pd, pyotp, pytz
from dhanhq import dhanhq
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIG ---
LIVE_MODE = False  # Keep False for Paper Trading
MAX_TRADES = 10

def get_dhan_client():
    client_id = os.environ.get('DHAN_CLIENT_ID')
    totp_key = os.environ.get('DHAN_TOTP_KEY')
    pin = os.environ.get('DHAN_PIN')
    totp_gen = pyotp.TOTP(totp_key)
    
    # Authenticate for v2.0
    temp_client = dhanhq(client_id, "")
    auth_data = temp_client.generate_token(pin, totp_gen.now())
    # Extract access token safely
    access_token = auth_data.get('access_token') or auth_data.get('data', {}).get('access_token')
    return dhanhq(client_id, access_token)

def send_telegram(message):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10)
    except:
        pass

def run_trading_cycle():
    try:
        # 1. Setup Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_data = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
        if not creds_data:
            print("Error: GCP_SERVICE_ACCOUNT_JSON not found")
            return
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_data), scope)
        client = gspread.authorize(creds)
        sheet = client.open("Ai360tradingAlgo").worksheet("AlertLog")

        # 2. Kill Switch Check (Updated to Column O2)
        kill_switch = str(sheet.acell("O2").value).strip().upper()
        if kill_switch != "YES":
            print(f"🛑 Kill Switch is {kill_switch}. Stopping.")
            return

        # 3. Process Trades (Fixed for Duplicate Headers)
        all_values = sheet.get_all_values()
        if len(all_values) < 2:
            print("Sheet is empty or only contains headers.")
            # Update Heartbeat even if empty
            now = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')
            sheet.update_acell("O3", f"Bot Live (Idle): {now}")
            return

        headers = all_values[0]
        data_rows = all_values[1:]

        for i, row in enumerate(data_rows):
            row_num = i + 2
            # Use index-based access to avoid header duplicate issues
            # K is Index 10 (Status), B is Index 1 (Symbol), C is Index 2 (Live Price)
            # H is Index 7 (SL), I is Index 8 (Target)
            
            symbol = str(row[1]).strip() if len(row) > 1 else ""
            status = str(row[10]).strip() if len(row) > 10 else ""
            
            try:
                price = float(row[2]) if len(row) > 2 and row[2] else 0
                sl = float(row[7]) if len(row) > 7 and row[7] else 0
                target = float(row[8]) if len(row) > 8 and row[8] else 0
            except ValueError:
                continue

            # --- CASE A: NEW SIGNAL (Empty Status) ---
            if not status and symbol:
                sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                send_telegram(f"📝 <b>PAPER ENTRY:</b> {symbol} @ {price}")

            # --- CASE B: MONITOR EXIT ---
            elif "TRADED" in status and "EXIT" not in status:
                if (target > 0 and price >= target) or (sl > 0 and price <= sl):
                    label = "TARGET 🎯" if price >= target else "STOPLOSS 🛑"
                    sheet.update_cell(row_num, 11, f"EXITED ({label})")
                    send_telegram(f"💰 <b>PAPER EXIT:</b> {symbol} @ {price} ({label})")

        # 4. Update Heartbeat (Updated to Column O3)
        now_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')
        sheet.update_acell("O3", f"Bot Live: {now_time}")
        print(f"Cycle Complete at {now_time}")

    except Exception as e:
        print(f"System Error: {e}")

if __name__ == "__main__":
    run_trading_cycle()
