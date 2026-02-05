import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
IST = pytz.timezone('Asia/Kolkata')
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT = os.environ.get('CHAT_ID')

def send_tg(msg):
    if TG_TOKEN and TG_CHAT:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        try: requests.post(url, json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}, timeout=10)
        except Exception as e: print(f"❌ TG Error: {e}")

def to_f(val):
    if not val: return 0.0
    try: return float(str(val).replace(',', '').replace('₹', '').replace('%', '').strip())
    except: return 0.0

def send_daily_summary(ss, active_trades):
    """Processes History and Active trades for a full report"""
    try:
        hist = ss.worksheet("History")
        today = datetime.now(IST).strftime('%Y-%m-%d')
        all_hist = hist.get_all_values()[1:]
        today_closed = [t for t in all_hist if str(t[3]).startswith(today)]
        
        wins = sum(1 for t in today_closed if "WIN" in str(t[6]))
        losses = len(today_closed) - wins
        
        holdings_text = "\n".join([f"• {t['sym']}: {t['pnl']:+.2f}%" for t in active_trades])
        
        msg = (
            f"📊 <b>DAILY TRADE SUMMARY</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✅ <b>Closed Today:</b> {len(today_closed)} (W: {wins} | L: {losses})\n"
            f"\n📈 <b>Current Holdings:</b>\n{holdings_text if holdings_text else 'No active trades'}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        send_tg(msg)
    except Exception as e: print(f"❌ Summary Error: {e}")

def run_trading_cycle():
    now = datetime.now(IST)
    curr_hm = now.strftime("%H:%M")
    
    # 1. Setup
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
    if not creds_json: return
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope)
    ss = gspread.authorize(creds).open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")

    # --- 2. MANUAL COMMAND CHECK (Cell O5) ---
    manual_cmd = str(sheet.acell("O5").value).strip().upper()
    
    # Pre-calculate active trades for summary
    data = sheet.get_all_values()[1:]
    active_trades = []
    for row in data:
        if len(row) >= 12 and "TRADED" in str(row[10]).upper():
            p, ep = to_f(row[2]), to_f(row[11])
            active_trades.append({'sym': row[1], 'pnl': ((p-ep)/ep)*100 if ep>0 else 0})

    if manual_cmd == "SEND SUMMARY":
        send_daily_summary(ss, active_trades)
        sheet.update_acell("O5", "DONE") # AUTO-DELETE COMMAND
        return 

    # --- 3. DAILY TIMING FLAGS (Cell O4) ---
    today_date = now.strftime('%Y-%m-%d')
    sent_status = str(sheet.acell("O4").value).strip()

    if "09:00" <= curr_hm <= "09:15" and sent_status != f"{today_date}-AM":
        send_tg(f"🌅 <b>Good Morning!</b> Market is opening.")
        sheet.update_acell("O4", f"{today_date}-AM")

    if "15:30" <= curr_hm <= "15:45" and sent_status != f"{today_date}-PM":
        send_daily_summary(ss, active_trades)
        sheet.update_acell("O4", f"{today_date}-PM")

    # --- 4. CORE TRADING LOGIC (SL & HISTORY) ---
    rows_to_delete = []
    for i, row in enumerate(data):
        r_num = i + 2
        if len(row) < 13 or "TRADED" not in str(row[10]).upper(): continue
        
        sym, price, sl = str(row[1]), to_f(row[2]), to_f(row[7])
        entry_p, entry_t = to_f(row[11]), str(row[12])
        strat = str(row[5]) # Col F
        
        if sl > 0 and price <= sl:
            from datetime import timedelta
            exit_t = now.strftime('%Y-%m-%d %H:%M:%S')
            # Duration calculation
            try:
                start_dt = datetime.strptime(entry_t, '%Y-%m-%d %H:%M:%S').replace(tzinfo=IST)
                diff = now - start_dt
                duration = f"{diff.days}d {diff.seconds // 3600}h"
            except: duration = "N/A"
            
            trade_info = {'sym': sym, 'entry_p': entry_p, 'exit_p': price, 'entry_t': entry_t, 'exit_t': exit_t, 'duration': duration, 'strat': strat}
            if move_to_history(ss, trade_info):
                send_tg(f"📉 <b>EXIT: {sym}</b>\nPrice: ₹{price}\nDuration: {duration}")
                rows_to_delete.append(r_num)

    if rows_to_delete:
        for r in reversed(rows_to_delete): sheet.delete_rows(r)
    
    sheet.update_acell("O3", f"Last Run: {now.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    run_trading_cycle()
