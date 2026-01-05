import os, gspread, json, requests
from datetime import datetime
from google.oauth2.service_account import Credentials

# --- CONFIG ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def run_trading_cycle():
    # ... (Standard Gspread setup) ...
    records = log_sheet.get_all_records()
    
    for i, row in enumerate(records):
        row_num = i + 2
        symbol, price, status = row.get('Symbol'), row.get('Price'), row.get('Status')
        entry, sl, tgt = row.get('Entry Price'), row.get('StopLoss'), row.get('Target')

        # --- CASE 1: NEW ENTRY ---
        if not status and symbol:
            log_sheet.update_cell(row_num, 11, "TRADED (PAPER)")
            send_telegram(f"🚀 <b>NEW TRADE ENTRY</b>\nStock: {symbol}\nPrice: ₹{price}\nTgt: ₹{tgt}\nSL: ₹{sl}")

        # --- CASE 2: MONITOR EXIT ---
        elif "TRADED" in status:
            if price >= tgt:
                log_sheet.update_cell(row_num, 11, "EXIT (TARGET ✅)")
                send_telegram(f"💰 <b>TARGET HIT!</b>\nStock: {symbol}\nExit: ₹{price}\nProfit: +2.00%")
            elif price <= sl:
                log_sheet.update_cell(row_num, 11, "EXIT (STOPLOSS ❌)")
                send_telegram(f"📉 <b>STOPLOSS HIT</b>\nStock: {symbol}\nExit: ₹{price}\nLoss: -1.00%")

if __name__ == "__main__":
    run_trading_cycle()
