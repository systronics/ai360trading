import os, json, gspread, requests, pandas as pd, pyotp, pytz
from dhanhq import dhanhq
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIG ---
LIVE_MODE = False  
MAX_ACTIVE_SLOTS = 5  

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
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=15)
    except Exception as e:
        print(f"Telegram failed: {e}")

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
        if len(all_values) < 2: return
        data_rows = all_values[1:]
        
        # Count only rows that are currently "TRADED" but not "EXITED"
        active_trades = [r for r in data_rows if len(r) > 10 and "TRADED" in str(r[10]).upper() and "EXITED" not in str(r[10]).upper()]
        active_count = len(active_trades)

        # 4. Process Rows
        for i, row in enumerate(data_rows):
            row_num = i + 2
            if len(row) < 12: continue 

            symbol = str(row[1]).strip()
            status = str(row[10]).strip().upper()
            if not symbol: continue

            try:
                def to_f(val):
                    if not val: return 0.0
                    clean = str(val).replace(',', '').replace('₹', '').strip()
                    return float(clean)

                price = to_f(row[2])        # Column C
                sl = to_f(row[7])           # Column H
                target = to_f(row[8])       # Column I
                entry_price = to_f(row[11])  # Column L (Captured at Entry)
            except ValueError:
                continue

            # --- CASE A: MONITOR EXIT WITH TRAILING ---
            if "TRADED" in status and "EXITED" not in status:
                # Calculate Current Profit Percentage
                profit_pct = 0
                if entry_price > 0:
                    profit_pct = ((price - entry_price) / entry_price) * 100

                # --- AGGRESSIVE TRAILING LOGIC ---
                new_sl = sl
                # If profit > 4%, Lock in 2% Profit
                if profit_pct >= 4.0:
                    trail_at_2_pct = entry_price * 1.02
                    if trail_at_2_pct > sl:
                        new_sl = trail_at_2_pct
                
                # If profit > 2%, Move to Break-Even (Risk-Free)
                elif profit_pct >= 2.0:
                    if entry_price > sl:
                        new_sl = entry_price

                # Update Sheet if TSL moved up
                if new_sl > sl:
                    sheet.update_cell(row_num, 8, round(new_sl, 2)) # Column H
                    send_telegram(f"🛡️ <b>TSL UPDATED:</b> {symbol} SL moved to {round(new_sl, 2)} (+{round(profit_pct, 1)}% profit)")
                    sl = new_sl 

                # --- FINAL EXIT CHECK ---
                is_target_hit = target > 0 and price >= target
                is_sl_hit = sl > 0 and price <= sl

                if is_target_hit or is_sl_hit:
                    label = "TARGET 🎯" if is_target_hit else "STOPLOSS 🛑"
                    send_telegram(f"💰 <b>PAPER EXIT:</b> {symbol} @ {price} ({label})")
                    sheet.update_cell(row_num, 11, f"EXITED ({label})")
                    active_count -= 1
                    print(f"✅ {symbol} closed via {label}")

            # --- CASE B: NEW SIGNAL (Entry) ---
            elif status == "" and symbol:
                if active_count < MAX_ACTIVE_SLOTS:
                    send_telegram(f"🚀 <b>PAPER ENTRY:</b> {symbol} @ {price} (Slot {active_count+1}/5)")
                    sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                    
                    # IMPORTANT: Store Entry Price in Column L for TSL Math
                    sheet.update_cell(row_num, 12, price) 
                    
                    now_ist = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')
                    sheet.update_cell(row_num, 13, now_ist)
                    active_count += 1
                else:
                    print(f"⏳ Slots full ({active_count}/5). {symbol} skipped.")

        # 5. Heartbeat Update
        now_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')
        sheet.update_acell("O3", f"Bot Live | Active: {active_count}/5 | {now_time}")

    except Exception as e:
        print(f"System Error: {e}")

if __name__ == "__main__":
    run_trading_cycle()
