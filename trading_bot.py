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
    if now.hour == 9 and now.minute < 5 and f"{today}_AM" not in mem:
        send_tg(f"🌅 <b>GOOD MORNING - {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n🛡️ <b>System:</b> Online\n🚀 <b>Focus:</b> Priority 20+ Stocks\n━━━━━━━━━━━━━━━━━━━━")
        sheet.update_acell("O4", mem + f",{today}_AM")

    rows = sheet.get_all_values()
    for i, r in enumerate(rows[1:10], start=2):
        if "TRADED" in str(r[10]).upper():
            sym, cp, sl, ent = r[1], to_f(r[2]), to_f(r[7]), to_f(r[11])
            
            # --- ZERO SAFETY ---
            if cp <= 0: continue 
            
            pnl = ((cp - ent) / ent) * 100
            new_sl = round(cp * 0.965, 2)

            # TSL Shift (>1% move)
            if new_sl > (sl * 1.01):
                sheet.update_cell(i, 8, new_sl)
                send_tg(f"🛡️ <b>TRAILING SL UPDATE</b>\n━━━━━━━━━━━━━━━━━━━━\n📈 <b>Stock:</b> {sym}\n🆙 <b>New SL:</b> ₹{new_sl}\n💰 <b>P/L:</b> {pnl:+.2f}%\n━━━━━━━━━━━━━━━━━━━━")

            # Exit Alert
            if cp <= sl and sl > 0:
                if f"{sym}_EX" not in mem:
                    send_tg(f"🚨 <b>TRADE EXIT ALERT</b>\n━━━━━━━━━━━━━━━━━━━━\n📉 <b>Stock:</b> {sym}\n💰 <b>Exit:</b> ₹{cp}\n📊 <b>P/L:</b> {pnl:+.2f}%\n━━━━━━━━━━━━━━━━━━━━")
                    sheet.update_acell("O4", mem + f",{sym}_EX")

if __name__ == "__main__":
    run_trading_cycle()
