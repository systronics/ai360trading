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
    
    # 1. MORNING GREETING (Premium Style)
    if now.hour == 9 and 0 <= now.minute <= 5 and f"{today}_AM" not in mem:
        send_tg(f"🌅 <b>GOOD MORNING - {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n🛡️ <b>System:</b> Online\n📊 <b>Status:</b> Monitoring Active Trades")
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
            is_pullback = abs(((cp - sl) / sl) * 100) < 0.5 if sl > 0 else False

            # 2. TSL UPDATE (Premium Style)
            if new_sl > (sl * 1.01):
                sheet.update_cell(idx, 8, new_sl)
                send_tg(f"🛡️ <b>TSL UPDATE</b>\n━━━━━━━━━━━━━━━━━━━━\n📈 <b>Stock:</b> {sym}\n🆙 <b>New SL:</b> ₹{new_sl}\n💰 <b>P/L:</b> {pnl:+.2f}%\n✨ <i>Capital Protection Active</i>")

            # 3. EXIT ALERT (Premium Style - Handles negative gaps)
            if cp <= sl and sl > 0 and not is_pullback:
                if f"{sym}_EX" not in mem:
                    send_tg(f"🚨 <b>TRADE EXIT ALERT</b>\n━━━━━━━━━━━━━━━━━━━━\n📉 <b>Stock:</b> {sym}\n💰 <b>Exit Price:</b> ₹{cp}\n📊 <b>Final P/L:</b> {pnl:+.2f}%\n📁 <i>Moved to History Archive</i>")
                    hist_sheet.append_row([today, r[1], ent, cp, f"{pnl:.2f}%", strat, "EXITED"])
                    sheet.update_cell(idx, 11, "CLOSED/ARCHIVED") 
                    mem += f",{sym}_EX"
                    sheet.update_acell("O4", mem)

    # 4. MARKET CLOSE (Premium Style)
    if now.hour == 15 and 30 <= now.minute <= 40 and f"{today}_PM" not in mem:
        send_tg(f"🔔 <b>MARKET CLOSED - {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n🏁 <b>Status:</b> All trades synced for the day.")
        mem += f",{today}_PM"
        sheet.update_acell("O4", mem)

if __name__ == "__main__":
    run_trading_cycle()
