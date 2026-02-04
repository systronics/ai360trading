import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

IST = pytz.timezone('Asia/Kolkata')
MAX_ACTIVE_SLOTS = 10 
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT = os.environ.get('CHAT_ID')

def send_tg(msg):
    """Sends professional HTML formatted Telegram messages"""
    if TG_TOKEN and TG_CHAT:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        try:
            requests.post(url, json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}, timeout=10)
        except Exception as e: print(f"❌ TG Error: {e}")

def to_f(val):
    """Safely converts sheet values to numbers"""
    if not val: return 0.0
    try: return float(str(val).replace(',', '').replace('₹', '').replace('%', '').strip())
    except: return 0.0

def send_daily_summary(ss, active_trades_data):
    """Generates the professional report for followers"""
    try:
        hist = ss.worksheet("History")
        today = datetime.now(IST).strftime('%Y-%m-%d')
        all_trades = hist.get_all_values()[1:]
        today_trades = [t for t in all_trades if str(t[3]).startswith(today)] 
        
        wins = sum(1 for t in today_trades if "WIN" in str(t[6]))
        losses = len(today_trades) - wins
        closed_pnl = sum(to_f(t[5]) for t in today_trades)
        
        portfolio_report = ""
        total_open_pnl = 0
        if active_trades_data:
            portfolio_report = "\n📊 <b>Current Open Portfolio:</b>\n"
            for trade in active_trades_data:
                icon = "🟢" if trade['pnl'] > 0 else "🔴"
                portfolio_report += f"{icon} {trade['sym']}: {trade['pnl']:+.2f}%\n"
                total_open_pnl += trade['pnl']

        summary = (
            f"🏆 <b>Daily Performance - {today}</b>\n"
            f"{'='*25}\n"
            f"✅ <b>Closed Trades:</b> {len(today_trades)}\n"
            f"Wins: {wins} | Losses: {losses}\n"
            f"Realized P/L: {closed_pnl:+.2f}%\n{portfolio_report}\n"
            f"💰 <b>Total Net P/L: {(closed_pnl + total_open_pnl):+.2f}%</b>\n"
            f"{'='*25}\n"
            f"<i>Holding for targets.</i> 🌙"
        )
        send_tg(summary)
    except Exception as e: print(f"❌ Summary Error: {e}")

def run_trading_cycle():
    now = datetime.now(IST)
    curr_hm = now.strftime("%H:%M")
    curr_min = now.hour * 60 + now.minute
    
    # 1. Connect to Sheet
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ['GCP_SERVICE_ACCOUNT_JSON']), scope)
    client = gspread.authorize(creds)
    ss = client.open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")

    today_prefix = now.strftime('%Y-%m-%d')
    sent_status = str(sheet.acell("O4").value).strip()
    manual_cmd = str(sheet.acell("O5").value).strip().upper()

    # 2. Gather Portfolio Data
    data = sheet.get_all_values()[1:]
    active_trades_data = []
    for row in data:
        if len(row) >= 12 and "TRADED" in str(row[10]).upper():
            sym, price, entry_p = str(row[1]), to_f(row[2]), to_f(row[11])
            pnl_pct = ((price - entry_p) / entry_p) * 100
            active_trades_data.append({'sym': sym, 'pnl': pnl_pct, 'row': row})

    # --- 3. COMMAND CENTER (Cell O5) ---
    if manual_cmd == "SEND SUMMARY":
        send_daily_summary(ss, active_trades_data)
        sheet.update_acell("O5", "DONE")
        return
    elif manual_cmd == "SEND MORNING":
        p_status = "\n\n📈 <b>Open Positions:</b>\n" + "\n".join([f"• {t['sym']}: {t['pnl']:+.2f}%" for t in active_trades_data])
        send_tg(f"🌅 <b>Good Morning! Market is Opening.</b>\nBot is active.{p_status}")
        sheet.update_acell("O5", "DONE")
        return

    # --- 4. AUTO TIMING WINDOWS ---
    if "09:00" <= curr_hm <= "09:15" and sent_status != f"{today_prefix}-AM":
        p_status = "\n\n📈 <b>Open Positions:</b>\n" + "\n".join([f"• {t['sym']}: {t['pnl']:+.2f}%" for t in active_trades_data])
        send_tg(f"🌅 <b>Good Morning! Market is Opening.</b>\nBot is active.{p_status}")
        sheet.update_acell("O4", f"{today_prefix}-AM")

    if "15:30" <= curr_hm <= "15:45" and sent_status != f"{today_prefix}-PM":
        send_tg("🌙 <b>Market Closed. Preparing final report...</b>")
        sheet.update_acell("O4", f"{today_prefix}-PM")

    if "15:45" <= curr_hm <= "16:15" and sent_status != f"{today_prefix}-SUM":
        send_daily_summary(ss, active_trades_data)
        sheet.update_acell("O4", f"{today_prefix}-SUM")

    # --- 5. CORE TRADING LOGIC ---
    try:
        active_count = len(active_trades_data)
        rows_to_delete = []

        for i, row in enumerate(data):
            r_num = i + 2
            if len(row) < 14 or "TRADED" not in str(row[10]).upper(): continue
            
            sym, price, sl, entry_p = str(row[1]), to_f(row[2]), to_f(row[7]), to_f(row[11])
            pnl_pct = ((price - entry_p) / entry_p) * 100
            
            # NO-SPAM TSL LOGIC
            new_sl = sl
            if pnl_pct >= 6.0: new_sl = max(sl, entry_p * 1.04)
            elif pnl_pct >= 4.0: new_sl = max(sl, entry_p * 1.02)
            elif pnl_pct >= 2.0: new_sl = max(sl, entry_p)
                
            if new_sl > sl:
                sheet.update_cell(r_num, 8, round(new_sl, 2))
                send_tg(f"🛡️ <b>TSL UPDATED: {sym}</b>\nNew SL: ₹{new_sl:.2f}\nP/L: {pnl_pct:+.2f}%")
                sl = new_sl

            if sl > 0 and price <= sl:
                # Assuming move_to_history is defined in your main script
                if move_to_history(ss, {'sym': sym, 'entry_p': entry_p, 'exit_p': price, 'entry_t': str(row[12]), 'exit_t': now.strftime('%Y-%m-%d %H:%M:%S'), 'cat': str(row[5]), 'reason': 'STOPLOSS'}):
                    rows_to_delete.append(r_num)
                    active_count -= 1

        # NEW ENTRIES (Market Hours)
        if 555 <= curr_min <= 930 and str(sheet.acell("O2").value).strip().upper() == "YES":
            for i, row in enumerate(data):
                r_num = i + 2
                if active_count >= MAX_ACTIVE_SLOTS or len(row) < 11: break
                if str(row[10]).strip().upper() in ["", "WAITING"]:
                    p = to_f(row[2])
                    if p == 0: continue
                    sheet.update_cell(r_num, 11, "TRADED (PAPER)")
                    sheet.update_cell(r_num, 12, p)
                    sheet.update_cell(r_num, 13, now.strftime('%Y-%m-%d %H:%M:%S'))
                    send_tg(f"🚀 <b>NEW ENTRY: {row[1]}</b>\nPrice: ₹{p:.2f}\nSlot: {active_count+1}/{MAX_ACTIVE_SLOTS}")
                    active_count += 1

        if rows_to_delete:
            for r in reversed(rows_to_delete): sheet.delete_rows(r)
        
        sheet.update_acell("O3", f"Scanner Active | A:{active_count}/{MAX_ACTIVE_SLOTS} | {now.strftime('%H:%M:%S')}")
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_trading_cycle()
