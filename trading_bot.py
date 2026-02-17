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
    
    # Load Credentials
    creds_dict = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_JSON'))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    ss = gspread.authorize(creds).open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")
    hist_sheet = ss.worksheet("History")

    # Memory for Daily Greeting & Exit Alerts
    mem = str(sheet.acell("O4").value or "")
    
    # 1. MORNING GREETING (9:00 AM IST)
    if now.hour == 9 and now.minute < 10 and f"{today}_AM" not in mem:
        send_tg(f"🌅 <b>GOOD MORNING - {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n🛡️ <b>System:</b> Online")
        sheet.update_acell("O4", f"{today}_AM")
        mem = f"{today}_AM"

    # 2. SCANNING TRADE ZONE (Rows 2 to 31)
    all_data = sheet.get_all_values()
    trade_zone = all_data[1:31] # Extracts Rows 2-31

    for idx, r in enumerate(trade_zone, start=2):
        status = str(r[10]).upper()
        
        # Only process active TRADED stocks
        if "TRADED" in status:
            sym = r[1]
            cp = to_f(r[2])   # Live Price
            sl = to_f(r[7])   # Stop Loss
            ent = to_f(r[11]) # Entry Price
            strat = r[5]      # Strategy Category
            
            if cp <= 0 or ent <= 0: continue 
            
            pnl = ((cp - ent) / ent) * 100
            
            # Trailing Stop Loss Logic (96.5% of current price)
            new_sl = round(cp * 0.965, 2)
            
            # BULLISH PULLBACK PROTECTION
            # If current price is within 0.5% of SL, check if it's just a dip
            is_pullback = abs(((cp - sl) / sl) * 100) < 0.5 if sl > 0 else False

            # Update TSL if the new calculated SL is higher than current SL
            if new_sl > (sl * 1.01):
                sheet.update_cell(idx, 8, new_sl) # Updates Column H
                send_tg(f"🛡️ <b>TSL UPDATE</b>\n━━━━━━━━━━━━━━━━━━━━\n📈 <b>Stock:</b> {sym}\n🆙 <b>New SL:</b> ₹{new_sl}\n💰 <b>P/L:</b> {pnl:+.2f}%")

            # EXIT LOGIC: Price hits SL and it's NOT a minor pullback
            if cp <= sl and sl > 0 and not is_pullback:
                if f"{sym}_EX" not in mem:
                    send_tg(f"🚨 <b>TRADE EXIT ALERT</b>\n━━━━━━━━━━━━━━━━━━━━\n📉 <b>Stock:</b> {sym}\n💰 <b>Exit Price:</b> ₹{cp}\n📊 <b>Final P/L:</b> {pnl:+.2f}%")
                    
                    # Archive to History Sheet
                    hist_sheet.append_row([today, sym, ent, cp, f"{pnl:.2f}%", strat, "EXITED"])
                    
                    # Mark as Closed and update memory
                    sheet.update_cell(idx, 11, "CLOSED/ARCHIVED") 
                    mem += f",{sym}_EX"
                    sheet.update_acell("O4", mem)

    # 3. MARKET CLOSE MESSAGE (3:30 PM IST)
    if now.hour == 15 and now.minute >= 30 and now.minute < 40 and f"{today}_PM" not in mem:
        send_tg(f"🔔 <b>MARKET CLOSED - {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n📊 <b>Status:</b> All trades synced.")
        sheet.update_acell("O4", mem + f",{today}_PM")

if __name__ == "__main__":
    run_trading_cycle()
