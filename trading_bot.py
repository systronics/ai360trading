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
    ss = gspread.authorize(creds).open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")
    hist_sheet = ss.worksheet("History")

    mem_cell = sheet.acell("O4")
    mem = str(mem_cell.value or "")
    
    # Morning Greeting at 9 AM
    if now.hour == 9 and 0 <= now.minute <= 5 and f"{today}_AM" not in mem:
        send_tg(f"🌅 <b>GOOD MORNING - {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n🛡️ <b>System:</b> Online")
        mem += f",{today}_AM"
        sheet.update_acell("O4", mem)

    all_data = sheet.get_all_values()
    trade_zone = all_data[1:31] 

    for idx, r in enumerate(trade_zone, start=2):
        status = str(r[10]).upper()
        if "TRADED" in status:
            sym = r[1].replace("NSE:", "")
            cp, sl, ent, strat = to_f(r[2]), to_f(r[7]), to_f(r[11]), r[5]
            if cp <= 0 or ent <= 0: continue 
            
            pnl = ((cp - ent) / ent) * 100
            new_sl = round(cp * 0.965, 2)
            
            # Pullback logic: Do not exit during a bullish moment
            is_pullback = abs(((cp - sl) / sl) * 100) < 0.5 if sl > 0 else False

            if cp <= sl and sl > 0 and not is_pullback:
                if f"{sym}_EX" not in mem:
                    send_tg(f"🚨 <b>TRADE EXIT ALERT</b>\n━━━━━━━━━━━━━━━━━━━━\n📉 <b>Stock:</b> {sym}\n💰 <b>Exit Price:</b> ₹{cp}\n📊 <b>Final P/L:</b> {pnl:+.2f}%")
                    
                    # MATCHED TO ROW 2 & 3: [Symbol, Date, EntryP, ExitP, P/L, Strategy, Result]
                    # This fixes the formatting in the History sheet
                    hist_sheet.append_row([r[1], today, ent, cp, f"{pnl:.2f}%", strat, "STF EXITED"])
                    
                    # Update status to trigger promotion in Apps Script
                    sheet.update_cell(idx, 11, "EXITED") 
                    mem += f",{sym}_EX"
                    sheet.update_acell("O4", mem)

    # Market Close at 3:30 PM
    if now.hour == 15 and 30 <= now.minute <= 40 and f"{today}_PM" not in mem:
        send_tg(f"🔔 <b>MARKET CLOSED - {today}</b>")
        mem += f",{today}_PM"
        sheet.update_acell("O4", mem)

if __name__ == "__main__":
    run_trading_cycle()
