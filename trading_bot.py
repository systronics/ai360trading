import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
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

def calculate_duration(start_str, end_dt):
    """Calculates time between Entry Time (Col M) and Now"""
    try:
        # Expected format from Col M: 2026-02-02 10:22:59
        start_dt = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=IST)
        diff = end_dt - start_dt
        days = diff.days
        hours = diff.seconds // 3600
        return f"{days}d {hours}h"
    except: return "N/A"

def move_to_history(ss, trade_data):
    """
    Logs to History Sheet using your exact 9-column layout:
    Symbol | Entry Date | Entry Price | Exit Date | Exit Price | P/L % | Result | Hold Duration | Strategy
    """
    try:
        hist = ss.worksheet("History")
        entry_p = trade_data['entry_p']
        exit_p = trade_data['exit_p']
        pnl_pct = ((exit_p - entry_p) / entry_p) * 100
        result = "WIN ✅" if pnl_pct > 0 else "LOSS 🔴"
        
        # EXACT MAPPING
        new_row = [
            trade_data['sym'],           # A: Symbol
            trade_data['entry_t'],       # B: Entry Date
            entry_p,                     # C: Entry Price
            trade_data['exit_t'],        # D: Exit Date
            exit_p,                      # E: Exit Price
            f"{pnl_pct:.2f}%",           # F: P/L %
            result,                      # G: Result
            trade_data['duration'],      # H: Hold Duration
            trade_data['strat']          # I: Strategy
        ]
        hist.append_row(new_row)
        return True
    except Exception as e:
        print(f"❌ History Error: {e}")
        return False

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

    today_date = now.strftime('%Y-%m-%d')
    sent_status = str(sheet.acell("O4").value).strip()

    # 2. Portfolio Scan
    data = sheet.get_all_values()[1:]
    active_trades = []
    for row in data:
        if len(row) >= 13 and "TRADED" in str(row[10]).upper():
            p, ep = to_f(row[2]), to_f(row[11])
            pnl = ((p - ep) / ep) * 100 if ep > 0 else 0
            active_trades.append({'sym': row[1], 'pnl': pnl})

    # --- 3. TIMED MESSAGES (9:00 AM & 3:30 PM) ---
    if "09:00" <= curr_hm <= "09:15" and sent_status != f"{today_date}-AM":
        p_list = "\n".join([f"• {t['sym']}: {t['pnl']:+.2f}%" for t in active_trades])
        send_tg(f"🌅 <b>Good Morning!</b> Market scanner is active.\n\n📊 <b>Holdings:</b>\n{p_list if p_list else 'None'}")
        sheet.update_acell("O4", f"{today_date}-AM")

    if "15:30" <= curr_hm <= "15:45" and sent_status != f"{today_date}-PM":
        send_tg(f"🔔 <b>Market Close!</b> Daily performance logged to History.")
        sheet.update_acell("O4", f"{today_date}-PM")

    # --- 4. TRAILING EXIT LOGIC ---
    rows_to_delete = []
    for i, row in enumerate(data):
        r_num = i + 2
        # Check Column K (index 10) for "TRADED"
        if len(row) < 13 or "TRADED" not in str(row[10]).upper(): continue
        
        sym = str(row[1])       # Col B
        price = to_f(row[2])    # Col C
        sl = to_f(row[7])       # Col H (Min Stoploss - Your dynamic TSL)
        entry_p = to_f(row[11]) # Col L (Entry Price)
        entry_t = str(row[12]) # Col M (Entry Time)
        strat = str(row[5])    # Col F (Strategy Category)
        
        # EXIT ONLY WHEN TRAILING SL IS HIT
        if sl > 0 and price <= sl:
            exit_t = now.strftime('%Y-%m-%d %H:%M:%S')
            duration = calculate_duration(entry_t, now)
            
            trade_info = {
                'sym': sym, 'entry_p': entry_p, 'exit_p': price, 
                'entry_t': entry_t, 'exit_t': exit_t, 
                'duration': duration, 'strat': strat
            }
            
            if move_to_history(ss, trade_info):
                send_tg(f"📉 <b>TSL HIT - EXIT: {sym}</b>\nPrice: ₹{price}\nDuration: {duration}")
                rows_to_delete.append(r_num)

    # 5. Cleanup
    if rows_to_delete:
        for r in reversed(rows_to_delete): sheet.delete_rows(r)
    
    # Heartbeat
    sheet.update_acell("O3", f"Scanner Active | A:{len(active_trades)} | {now.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    run_trading_cycle()
