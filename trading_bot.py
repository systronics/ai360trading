import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

IST = pytz.timezone('Asia/Kolkata')
MAX_ACTIVE_SLOTS = 5 # Change to 10 if you want to take more trades
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT = os.environ.get('CHAT_ID')

def send_tg(msg):
    """Send Telegram notification"""
    if TG_TOKEN and TG_CHAT:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        try:
            requests.post(url, json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}, timeout=10)
            print(f"✅ Telegram sent: {msg[:50]}...")
        except Exception as e:
            print(f"❌ Telegram error: {e}")

def to_f(val):
    """Convert to float safely"""
    if not val: return 0.0
    try: return float(str(val).replace(',', '').replace('₹', '').replace('%', '').strip())
    except: return 0.0

def send_daily_summary(ss):
    """Send daily P/L summary at market close"""
    try:
        hist = ss.worksheet("History")
        today = datetime.now(IST).strftime('%Y-%m-%d')
        all_trades = hist.get_all_values()[1:]
        today_trades = [t for t in all_trades if str(t[3]).startswith(today)] 
        
        if not today_trades:
            send_tg(f"📊 <b>Daily Summary - {today}</b>\n\nNo trades exited today.")
            return
        
        wins = sum(1 for t in today_trades if "WIN" in str(t[6]))
        losses = len(today_trades) - wins
        total_pnl = sum(to_f(t[5]) for t in today_trades)
        
        summary = (
            f"📊 <b>Daily Summary - {today}</b>\n\n"
            f"Total Trades Today: {len(today_trades)}\n"
            f"Wins: {wins} 🟢 | Losses: {losses} 🔴\n"
            f"Total P/L: {total_pnl:+.2f}%\n"
            f"\n{'='*25}\n"
            f"See you tomorrow! 🌙"
        )
        send_tg(summary)
    except Exception as e:
        print(f"❌ Summary Error: {e}")

def run_trading_cycle():
    """Main trading cycle with expanded window-based timings"""
    now = datetime.now(IST)
    curr_hm = now.strftime("%H:%M")
    curr_min = now.hour * 60 + now.minute
    
    # Setup Sheets connection for status checks
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ['GCP_SERVICE_ACCOUNT_JSON']), scope)
    client = gspread.authorize(creds)
    ss = client.open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")

    # Tracking labels in O4 to prevent multiple messages
    today_prefix = now.strftime('%Y-%m-%d')
    sent_status = str(sheet.acell("O4").value).strip()

    # 1. Good Morning Window (09:00 - 09:15)
    if "09:00" <= curr_hm <= "09:15":
        if sent_status != f"{today_prefix}-AM":
            send_tg("🌅 <b>Good Morning, Market Open</b>\n<i>Bot is active and monitoring slots.</i>")
            sheet.update_acell("O4", f"{today_prefix}-AM")
        return

    # 2. Market Close Window (15:30 - 15:45)
    if "15:30" <= curr_hm <= "15:45":
        if sent_status != f"{today_prefix}-PM":
            send_tg("🌙 <b>Good Bye, Market Close</b>")
            sheet.update_acell("O4", f"{today_prefix}-PM")

    # 3. Daily Summary Window (15:45 - 16:15)
    if "15:45" <= curr_hm <= "16:15":
        if sent_status != f"{today_prefix}-SUM":
            send_daily_summary(ss)
            sheet.update_acell("O4", f"{today_prefix}-SUM")
        return

    # 4. Trading Window Filter (9:15 AM - 3:30 PM)
    if not (555 <= curr_min <= 930):
        print(f"💤 Outside trading hours ({curr_hm}). Idling.")
        return

    # --- START TRADING LOGIC ---
    try:
        kill_switch = str(sheet.acell("O2").value).strip().upper()
        if kill_switch != "YES":
            sheet.update_acell("O3", f"Scanner Paused | {now.strftime('%H:%M:%S')}")
            return
        
        data = sheet.get_all_values()[1:]
        active_count = sum(1 for r in data if len(r) > 10 and "TRADED" in str(r[10]).upper() and "EXITED" not in str(r[10]).upper())
        
        rows_to_delete = []

        # MONITOR ACTIVE TRADES (Exits & TSL)
        for i, row in enumerate(data):
            r_num = i + 2
            if len(row) < 14 or "TRADED" not in str(row[10]).upper(): continue
            
            try:
                sym, price, sl, entry_p = str(row[1]), to_f(row[2]), to_f(row[7]), to_f(row[11])
                profit_pct = ((price - entry_p) / entry_p) * 100
                
                # TSL Logic (2%, 4%, 6%)
                new_sl, tsl_triggered = sl, False
                if profit_pct >= 6.0 and (entry_p * 1.04) > sl:
                    new_sl, tsl_triggered = entry_p * 1.04, True
                elif profit_pct >= 4.0 and (entry_p * 1.02) > sl:
                    new_sl, tsl_triggered = entry_p * 1.02, True
                elif profit_pct >= 2.0 and entry_p > sl:
                    new_sl, tsl_triggered = entry_p, True
                    
                if tsl_triggered:
                    sheet.update_cell(r_num, 8, round(new_sl, 2))
                    send_tg(f"🛡️ <b>TSL UPDATED: {sym}</b>\nNew SL: ₹{new_sl:.2f}\nP/L: {profit_pct:+.2f}%")
                    sl = new_sl

                # Exit Check
                if sl > 0 and price <= sl:
                    # Logic to move to History... (omitted for brevity, keep your existing move_to_history function)
                    pass 
            except: continue

        # NEW ENTRIES (Promote Waiting)
        for i, row in enumerate(data):
            r_num = i + 2
            if active_count >= MAX_ACTIVE_SLOTS or len(row) < 11: break
            if str(row[10]).strip().upper() in ["", "WAITING"]:
                price = to_f(row[2])
                if price == 0: continue
                sheet.update_cell(r_num, 11, "TRADED (PAPER)")
                sheet.update_cell(r_num, 12, price)
                sheet.update_cell(r_num, 13, now.strftime('%Y-%m-%d %H:%M:%S'))
                send_tg(f"🚀 <b>NEW ENTRY: {row[1]}</b>\nPrice: ₹{price:.2f}\nSlot: {active_count+1}/{MAX_ACTIVE_SLOTS}")
                active_count += 1

        sheet.update_acell("O3", f"Scanner Active | A:{active_count}/{MAX_ACTIVE_SLOTS} | {now.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_trading_cycle()
