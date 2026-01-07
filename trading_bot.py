import os, json, gspread, requests, pandas as pd, pyotp, pytz
from dhanhq import dhanhq
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIG ---
LIVE_MODE = False  
MAX_ACTIVE_SLOTS = 5  # We only want top 5 to be traded

def get_dhan_client():
    client_id = os.environ.get('DHAN_CLIENT_ID')
    totp_key = os.environ.get('DHAN_TOTP_KEY')
    pin = os.environ.get('DHAN_PIN')
    totp_gen = pyotp.TOTP(totp_key)
    
    temp_client = dhanhq(client_id, "")
    auth_data = temp_client.generate_token(pin, totp_gen.now())
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

        # 2. Kill Switch Check
        kill_switch = str(sheet.acell("O2").value).strip().upper()
        if kill_switch != "YES":
            print(f"🛑 Kill Switch is {kill_switch}. Stopping.")
            return

        # 3. Get Data
        all_values = sheet.get_all_values()
        if len(all_values) < 2:
            return

        data_rows = all_values[1:]
        
        # --- NEW: COUNT CURRENTLY ACTIVE TRADES ---
        # Checks Column K (Index 10) for any row that contains "TRADED" but not "EXITED"
        active_trades = [r for r in data_rows if len(r) > 10 and "TRADED" in str(r[10]) and "EXITED" not in str(r[10])]
        active_count = len(active_trades)
        print(f"Active Trades Found: {active_count}/{MAX_ACTIVE_SLOTS}")

        # 4. Process Rows
        for i, row in enumerate(data_rows):
            row_num = i + 2
            symbol = str(row[1]).strip() if len(row) > 1 else ""
            status = str(row[10]).strip() if len(row) > 10 else ""
            
            try:
                price = float(row[2]) if len(row) > 2 and row[2] else 0
                sl = float(row[7]) if len(row) > 7 and row[7] else 0
                target = float(row[8]) if len(row) > 8 and row[8] else 0
            except ValueError:
                continue

            # --- CASE A: MONITOR EXIT (Existing Trades) ---
            if "TRADED" in status and "EXIT" not in status:
                if (target > 0 and price >= target) or (sl > 0 and price <= sl):
                    label = "TARGET 🎯" if price >= target else "STOPLOSS 🛑"
                    sheet.update_cell(row_num, 11, f"EXITED ({label})")
                    send_telegram(f"💰 <b>PAPER EXIT:</b> {symbol} @ {price} ({label})")
                    active_count -= 1 # Free up slot for current cycle

            # --- CASE B: NEW SIGNAL (Entry) ---
            elif not status and symbol:
                if active_count < MAX_ACTIVE_SLOTS:
                    # Mark as TRADED in Col K
                    sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                    
                    # Update Timestamp in Col M (Index 13) for followers
                    now_ist = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')
                    sheet.update_cell(row_num, 13, now_ist)
                    
                    send_telegram(f"🚀 <b>PAPER ENTRY:</b> {symbol} @ {price} (Slot {active_count+1}/5)")
                    active_count += 1
                else:
                    print(f"⏳ Slot limit reached. {symbol} waiting in queue.")

        # 5. Update Heartbeat
        now_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')
        sheet.update_acell("O3", f"Bot Live | Active: {active_count}/5 | {now_time}")
        print(f"Cycle Complete at {now_time}")

    except Exception as e:
        print(f"System Error: {e}")

if __name__ == "__main__":
    run_trading_cycle()
