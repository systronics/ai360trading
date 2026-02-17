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

    mem = str(sheet.acell("O4").value or "")
    
    # 1. MORNING GREETING
    if now.hour == 9 and 0 <= now.minute <= 10 and f"{today}_AM" not in mem:
        send_tg(f"🌅 <b>GOOD MORNING - {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n🛡️ <b>System:</b> Online")
        sheet.update_acell("O4", f"{today}_AM")
        mem = f"{today}_AM"

    # 2. SCANNING TRADE ZONE (Rows 2 to 31)
    all_rows = sheet.get_all_values()
    trade_zone = all_rows[1:31] 

    for idx, r in enumerate(trade_zone, start=2):
        status = str(r[10]).upper()
        if "TRADED" in status:
            sym, cp, sl, ent, strat = r[1], to_f(r[2]), to_f(r[7]), to_f(r[11]), r[5]
            if cp <= 0 or ent <= 0: continue 
            
            pnl = ((cp - ent) / ent) * 100
            new_sl = round(cp * 0.965, 2)
            
            # PULLBACK PROTECTION: 0.5% Buffer
            is_pullback = abs(((cp - sl) / sl) * 100) < 0.5 if sl > 0 else False

            # TRAILING STOP LOSS UPDATE
            if new_sl > (sl * 1.01):
                sheet.update_cell(idx, 8, new_sl) # Col H
                send_tg(f"🛡️ <b>TSL UPDATE</b>\n━━━━━━━━━━━━━━━━━━━━\n📈 <b>Stock:</b> {sym}\n🆙 <b>New SL:</b> ₹{new_sl}\n💰 <b>P/L:</b> {pnl:+.2f}%")

            # EXIT LOGIC
            if cp <= sl and sl > 0 and not is_pullback:
                if f"{sym}_EX" not in mem:
                    send_tg(f"🚨 <b>TRADE EXIT ALERT</b>\n━━━━━━━━━━━━━━━━━━━━\n📉 <b>Stock:</b> {sym}\n💰 <b>Exit:</b> ₹{cp}\n📊 <b>P/L:</b> {pnl:+.2f}%")
                    hist_sheet.append_row([today, sym, ent, cp, f"{pnl:.2f}%", strat, "EXITED"])
                    sheet.update_cell(idx, 11, "CLOSED/ARCHIVED") # Col K
                    mem += f",{sym}_EX"
                    sheet.update_acell("O4", mem)

    # 3. MARKET CLOSE SUMMARY
    if now.hour == 15 and 30 <= now.minute <= 40 and f"{today}_PM" not in mem:
        send_tg(f"🔔 <b>MARKET CLOSED - {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n📊 System Sync Complete.")
        sheet.update_acell("O4", mem + f",{today}_PM")

if __name__ == "__main__":
    run_trading_cycle()
