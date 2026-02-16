import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

IST = pytz.timezone('Asia/Kolkata')
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT = os.environ.get('CHAT_ID')

def send_tg(msg):
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}, timeout=15)

def to_f(val):
    try: return float(str(val).replace(',', '').replace('₹', '').strip())
    except: return 0.0

def run_trading_cycle():
    now = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_JSON')), ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    sheet = gspread.authorize(creds).open("Ai360tradingAlgo").worksheet("AlertLog")

    # Morning Message (9 AM)
    mem = str(sheet.acell("O4").value or "")
    if now.hour == 9 and now.minute < 10 and f"{today}_AM" not in mem:
        send_tg(f"🌅 <b>GOOD MORNING - {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n🛡️ <b>System:</b> Online\n📊 <b>Market:</b> Tracking Nifty200\n━━━━━━━━━━━━━━━━━━━━")
        sheet.update_acell("O4", f"{today}_AM") # Reset memory to keep it short

    # Market Close Summary (3:30 PM)
    if now.hour == 15 and 30 <= now.minute < 40 and f"{today}_PM" not in mem:
        send_tg(f"🏁 <b>MARKET CLOSE - {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n✅ <b>Status:</b> Market Closed.\n📈 <b>P/L Summary:</b> Checking positions...\n━━━━━━━━━━━━━━━━━━━━")
        sheet.update_acell("O4", mem + f",{today}_PM")

    # SCAN ROWS 11 TO 30 (Where your data actually is)
    rows = sheet.get_all_values()
    traded_rows = rows[10:30] # Row 11 to 30

    for idx, r in enumerate(traded_rows, start=11):
        status = str(r[10]).upper()
        if "TRADED" in status:
            sym, cp, sl, ent = r[1], to_f(r[2]), to_f(r[7]), to_f(r[2]) # Using Col C for entry if Col L empty
            
            if cp <= 0 or ent <= 0: continue 
            
            pnl = ((cp - ent) / ent) * 100
            
            # Exit Alert (Price hits SL)
            if cp <= sl and sl > 0:
                if f"{sym}_EX" not in mem:
                    send_tg(f"🚨 <b>TRADE EXIT ALERT</b>\n━━━━━━━━━━━━━━━━━━━━\n📉 <b>Stock:</b> {sym}\n💰 <b>Exit:</b> ₹{cp}\n📊 <b>P/L:</b> {pnl:+.2f}%\n━━━━━━━━━━━━━━━━━━━━")
                    sheet.update_acell("O4", mem + f",{sym}_EX")

if __name__ == "__main__":
    run_trading_cycle()
