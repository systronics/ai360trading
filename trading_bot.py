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
    client = gspread.authorize(creds)
    ss = client.open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")
    hist_sheet = ss.worksheet("History")

    # --- 9 AM & 3:30 PM MESSAGES ---
    mem = str(sheet.acell("O4").value or "")
    if now.hour == 9 and now.minute < 10 and f"{today}_AM" not in mem:
        send_tg(f"🌅 <b>GOOD MORNING - {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n🛡️ <b>System:</b> Online\n🚀 <b>Focus:</b> Priority 20+ Stocks\n━━━━━━━━━━━━━━━━━━━━")
        sheet.update_acell("O4", f"{today}_AM")

    if now.hour == 15 and 30 <= now.minute < 40 and f"{today}_PM" not in mem:
        send_tg(f"🏁 <b>MARKET CLOSE - {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n✅ <b>Status:</b> All Positions Synced.")
        sheet.update_acell("O4", mem + f",{today}_PM")

    # --- SCANNING TRADED STOCKS (Rows 11 to 30) ---
    all_data = sheet.get_all_values()
    trade_zone = all_data[10:30] 

    for idx, r in enumerate(trade_zone, start=11):
        status = str(r[10]).upper()
        if "TRADED" in status:
            sym, cp, sl, ent, strat = r[1], to_f(r[2]), to_f(r[7]), to_f(r[11]), r[5]
            if cp <= 0 or ent <= 0: continue 
            
            pnl = ((cp - ent) / ent) * 100
            new_sl = round(cp * 0.965, 2)
            
            # Bullish Pullback: Do not exit if price is within 0.5% of SL
            is_pullback = abs(((cp - sl) / sl) * 100) < 0.5 if sl > 0 else False

            # TSL Update logic
            if new_sl > (sl * 1.01):
                sheet.update_cell(idx, 8, new_sl)
                send_tg(f"🛡️ <b>TSL UPDATE: {sym}</b>\n🆙 New SL: ₹{new_sl}\n💰 P/L: {pnl:+.2f}%")

            # --- EXIT & HISTORY LOGGING ---
            if cp <= sl and sl > 0 and not is_pullback:
                if f"{sym}_EX" not in mem:
                    # 1. Archive to History
                    hist_sheet.append_row([today, sym, ent, cp, f"{pnl:.2f}%", strat, "EXITED"])
                    # 2. Telegram Alert
                    send_tg(f"🚨 <b>TRADE EXIT: {sym}</b>\n💰 Exit: ₹{cp}\n📊 Final P/L: {pnl:+.2f}%")
                    # 3. Mark for Sheet Cleanup
                    sheet.update_cell(idx, 11, "CLOSED/ARCHIVED") 
                    sheet.update_acell("O4", mem + f",{sym}_EX")

if __name__ == "__main__":
    run_trading_cycle()
