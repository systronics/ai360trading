import os, json, gspread, requests, pandas as pd
from dhanhq import dhanhq
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

# --- CONFIG ---
LIVE_MODE = True  
CAP_PER_TRADE = 10000 
MAX_TRADES = 5
TRAIL_PCT = 0.005 

# Initialize Dhan
dhan = dhanhq(os.environ.get('DHAN_CLIENT_ID'), os.environ.get('DHAN_API_KEY'))

def send_telegram(message):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try: requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10)
    except: pass

def get_sec_id(symbol):
    try:
        url = "https://images.dhan.co/api-data/api-scrip-master.csv"
        df = pd.read_csv(url)
        clean_symbol = symbol.split(":")[-1].strip()
        dhan_target = f"{clean_symbol}-EQ"
        match = df[df['SEM_TRADING_SYMBOL'] == dhan_target]
        return str(match.iloc[0]['SEM_SMST_SECURITY_ID']) if not match.empty else None
    except: return None

def run_trading_cycle():
    try:
        # --- LOGIN ---
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
        service_account_info = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Ai360tradingAlgo").worksheet("AlertLog")

        # --- Q1, Q2, Q3 HEARTBEAT & KILL SWITCH ---
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
        
        # Write "SYSTEM_STATUS" to Q1 if empty, then heartbeat to Q3
        sheet.update_cell(1, 17, "SYSTEM_STATUS") 
        sheet.update_cell(3, 17, f"Live Heartbeat: {now_ist}")

        # Check Q2 (Row 2, Column 17) for "YES"
        system_active = sheet.cell(2, 17).value
        if str(system_active).strip().upper() != "YES":
            print(f"🛑 Kill Switch is {system_active}. Bot Paused.")
            return

        # --- TRADING LOGIC ---
        records = sheet.get_all_records()
        active_trades = [r for r in records if "TRADED" in str(r.get('Status')) and "EXIT" not in str(r.get('Status'))]
        active_count = len(active_trades)

        for i, row in enumerate(records):
            row_num = i + 2
            symbol = str(row.get('Symbol'))
            price = float(row.get('Live Price') or row.get('Price', 0))
            status = str(row.get('Status', ''))
            target = float(row.get('Target') or 0)
            stop_loss = float(row.get('StopLoss') or 0)

            # ENTRY
            if not status and symbol and active_count < MAX_TRADES:
                qty = int(CAP_PER_TRADE / price) if price > 0 else 0
                sec_id = get_sec_id(symbol)
                if LIVE_MODE and sec_id and qty > 0:
                    try:
                        dhan.place_order(security_id=sec_id, exchange_segment=dhan.NSE, transaction_type=dhan.BUY, quantity=qty, order_type=dhan.MARKET, product_type=dhan.CNC)
                        sheet.update_cell(row_num, 11, "TRADED (LIVE)")
                        send_telegram(f"🚀 <b>BOT BUY:</b> {symbol} @ {price}")
                        active_count += 1
                    except Exception as e: print(f"Order Error: {e}")

            # EXIT
            elif "TRADED" in status and "EXIT" not in status:
                if price >= target or (stop_loss > 0 and price <= stop_loss):
                    if LIVE_MODE:
                        sec_id = get_sec_id(symbol)
                        try:
                            qty_exit = int(CAP_PER_TRADE / price)
                            dhan.place_order(security_id=sec_id, exchange_segment=dhan.NSE, transaction_type=dhan.SELL, quantity=qty_exit, order_type=dhan.MARKET, product_type=dhan.CNC)
                            send_telegram(f"💰 <b>BOT EXIT:</b> {symbol} @ {price}")
                        except: pass
                    sheet.update_cell(row_num, 11, "EXITED")

    except Exception as e:
        print(f"Error: {e}")
        send_telegram(f"⚠️ <b>BOT ALERT:</b> Check logs - {e}")

if __name__ == "__main__":
    run_trading_cycle()
