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
    access_token = auth_data.get('access_token') or auth_data.get('data', {}).get('access_token')
    return dhanhq(client_id, access_token)

def send_telegram(message):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})

def run_trading_cycle():
    try:
        # 1. Setup Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_JSON')), scope)
        client = gspread.authorize(creds)
        sheet = client.open("Ai360tradingAlgo").worksheet("AlertLog")

        # 2. Kill Switch Check (Q2)
        if str(sheet.acell("Q2").value).strip().upper() != "YES":
            return

        # 3. Process Trades
        records = sheet.get_all_records()
        for i, row in enumerate(records):
            row_num = i + 2
            symbol = str(row.get('Symbol', ''))
            status = str(row.get('Status', '')).strip()
            price = float(row.get('Live Price') or 0)
            target = float(row.get('Target') or 0)
            sl = float(row.get('StopLoss') or 0)

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

        # Update Heartbeat (Q3)
        now = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')
        sheet.update_acell("Q3", f"Bot Live: {now}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_trading_cycle()
