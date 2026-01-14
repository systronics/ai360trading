import os, json, gspread, requests, pandas as pd, pyotp, pytz
from dhanhq import dhanhq
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIG ---
LIVE_MODE = False  
MAX_ACTIVE_SLOTS = 5
IST = pytz.timezone('Asia/Kolkata')

def get_dhan_client():
    client_id = os.environ.get('DHAN_CLIENT_ID')
    totp_key = os.environ.get('DHAN_TOTP_KEY')
    pin = os.environ.get('DHAN_PIN')
    
    if not all([client_id, totp_key, pin]):
        print("❌ Missing Dhan credentials")
        return None
    
    try:
        totp_gen = pyotp.TOTP(totp_key)
        temp_client = dhanhq(client_id, "")
        auth_data = temp_client.generate_token(pin, totp_gen.now())
        access_token = auth_data.get('access_token') or auth_data.get('data', {}).get('access_token')
        return dhanhq(client_id, access_token)
    except Exception as e:
        print(f"❌ Dhan Auth failed: {e}")
        return None

def send_telegram(message):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id: return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"❌ Telegram failed: {e}")

def to_f(val):
    if not val: return 0.0
    clean = str(val).replace(',', '').replace('₹', '').replace('%', '').strip()
    try: return float(clean)
    except: return 0.0

def move_to_history(spreadsheet, trade_data):
    """Appends finished trade to History sheet"""
    try:
        history_sheet = spreadsheet.worksheet("History")
        pnl_pct = ((trade_data['exit_p'] - trade_data['entry_p']) / trade_data['entry_p'] * 100) if trade_data['entry_p'] > 0 else 0
        result = "WIN 🟢" if pnl_pct > 0 else "LOSS 🔴"
        
        history_sheet.append_row([
            trade_data['sym'],
            trade_data['entry_t'],
            round(trade_data['entry_p'], 2),
            trade_data['exit_t'],
            round(trade_data['exit_p'], 2),
            f"{pnl_pct:.2f}%",
            result,
            trade_data['cat'] # Strategy used (Retest/Base)
        ])
        return True
    except Exception as e:
        print(f"❌ History move failed: {e}")
        return False

def run_trading_cycle():
    print(f"🤖 Cycle Started: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. Setup Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_data = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_data), scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open("Ai360tradingAlgo")
        sheet = spreadsheet.worksheet("AlertLog")

        # 2. Check Kill Switch
        if str(sheet.acell("O2").value).strip().upper() != "YES":
            print("🛑 Bot Paused via Kill Switch")
            return

        # 3. Process Data
        all_values = sheet.get_all_values()
        if len(all_values) < 2: return
        
        data_rows = all_values[1:] # Skip Header
        active_trades = [r for r in data_rows if len(r) > 10 and "TRADED" in str(r[10]).upper()]
        active_count = len(active_trades)
        rows_to_delete = []

        for i, row in enumerate(data_rows):
            row_num = i + 2
            if not row[1]: continue # Skip if no Symbol
            
            symbol = str(row[1]).strip()
            price = to_f(row[2])     # Col C (Live Price)
            status = str(row[10]).strip().upper()
            sl = to_f(row[7])        # Col H
            target = to_f(row[8])    # Col I
            category = str(row[5])   # Col F (Strategy)
            
            # --- CASE A: MONITOR & EXIT ACTIVE TRADES ---
            if "TRADED" in status:
                entry_price = to_f(row[11]) # Col L
                entry_time = str(row[12])   # Col M
                profit_pct = ((price - entry_price) / entry_price * 100) if entry_price > 0 else 0

                # Trailing Stop Loss Logic
                new_sl = sl
                if profit_pct >= 4.0: new_sl = max(sl, entry_price * 1.02)
                elif profit_pct >= 2.0: new_sl = max(sl, entry_price)
                
                if new_sl > sl:
                    sheet.update_cell(row_num, 8, round(new_sl, 2))
                    sl = new_sl
                    print(f"🛡️ TSL Updated for {symbol}")

                # Exit Check
                if (price >= target and target > 0) or (price <= sl and sl > 0):
                    exit_label = "TARGET 🎯" if price >= target else "STOPLOSS 🛑"
                    exit_time = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
                    
                    send_telegram(f"<b>PAPER EXIT: {symbol}</b>\nResult: {exit_label}\nPrice: ₹{price}\nP/L: {profit_pct:.2f}%")
                    
                    rows_to_delete.append({
                        'row_num': row_num, 'sym': symbol, 'entry_p': entry_price, 
                        'exit_p': price, 'entry_t': entry_time, 'exit_t': exit_time, 'cat': category
                    })
                    active_count -= 1

            # --- CASE B: NEW ENTRY ---
            elif status == "" and active_count < MAX_ACTIVE_SLOTS:
                entry_timestamp = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
                
                # Update Status, Entry Price (Col L), Entry Time (Col M)
                sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                sheet.update_cell(row_num, 12, price)
                sheet.update_cell(row_num, 13, entry_timestamp)
                
                send_telegram(
                    f"🚀 <b>NEW PAPER TRADE:</b> {symbol}\n"
                    f"Strategy: {category}\n"
                    f"Entry: ₹{price}\n"
                    f"Target: ₹{target}\n"
                    f"StopLoss: ₹{sl}\n"
                    f"Slot: {active_count+1}/{MAX_ACTIVE_SLOTS}"
                )
                active_count += 1

        # 4. Clean up: Move to History & Delete from AlertLog
        for trade in reversed(rows_to_delete): # Reverse to keep row numbers valid
            if move_to_history(spreadsheet, trade):
                sheet.delete_rows(trade['row_num'])
                print(f"🗑️ Moved {trade['sym']} to History")

        # Heartbeat
        sheet.update_acell("O3", f"Bot Active | A:{active_count}/5 | {datetime.now(IST).strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ System Error: {e}")
        send_telegram(f"🚨 <b>BOT ERROR:</b> {str(e)[:100]}")

if __name__ == "__main__":
    run_trading_cycle()
