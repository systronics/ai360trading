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
    """Calculates holding period like '1d 23h'"""
    try:
        # Matches format: 2026-02-02 10:22:59
        start_dt = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=IST)
        diff = end_dt - start_dt
        days = diff.days
        hours = diff.seconds // 3600
        return f"{days}d {hours}h"
    except: return "N/A"

def move_to_history(ss, trade_data):
    """
    FIXED: Matches your History sheet exactly:
    Symbol | Entry Date | Entry Price | Exit Date | Exit Price | P/L % | Result | Hold Duration | Strategy
    """
    try:
        hist = ss.worksheet("History")
        entry_p = trade_data['entry_p']
        exit_p = trade_data['exit_p']
        pnl_pct = ((exit_p - entry_p) / entry_p) * 100
        result = "WIN ✅" if pnl_pct > 0 else "LOSS 🔴"
        
        # Exact Column Order
        new_row = [
            trade_data['sym'],           # Symbol
            trade_data['entry_t'],       # Entry Date
            entry_p,                     # Entry Price
            trade_data['exit_t'],        # Exit Date
            exit_p,                      # Exit Price
            f"{pnl_pct:.2f}%",           # P/L %
            result,                      # Result
            trade_data['duration'],      # Hold Duration
            trade_data['strat']          # Strategy
        ]
        hist.append_row(new_row)
        return True
    except Exception as e:
        print(f"❌ History Error: {e}")
        return False

def run_trading_cycle():
    now = datetime.now(IST)
    curr_hm = now.strftime("%H:%M")
    
    # 1. Connect to Sheet
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
    if not creds_json: return
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope)
    client = gspread.authorize(creds)
    ss = client.open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")

    today_date = now.strftime('%Y-%m-%d')
    sent_status = str(sheet.acell("O4").value).strip()

    # 2. Gather Portfolio Data
    data = sheet.get_all_values()[1:]
    active_trades_data = []
    for row in data:
        if len(row) >= 12 and "TRADED" in str(row[10]).upper():
            sym, price, entry_p = str(row[1]), to_f(row[2]), to_f(row[11])
            if entry_p > 0:
                pnl_pct = ((price - entry_p) / entry_p) * 100
                active_trades_data.append({'sym': sym, 'pnl': pnl_pct, 'row': row})

    # --- 3. TIMED MESSAGES (8:45-9:15 for Morning, 3:15-3:45 for Close) ---
    if "08:45" <= curr_hm <= "09:15" and sent_status != f"{today_date}-AM":
        p_list = "\n".join([f"• {t['sym']}: {t['pnl']:+.2f}%" for t in active_trades_data])
        send_tg(f"🌅 <b>Good Morning! Market is Opening.</b>\n\n📊 <b>Current Holdings:</b>\n{p_list if p_list else 'No active trades.'}")
        sheet.update_acell("O4", f"{today_date}-AM")

    if "15:15" <= curr_hm <= "15:45" and sent_status != f"{today_date}-PM":
        # (This triggers the summary)
        send_tg(f"🔔 <b>Market is Closing!</b>\nFinalizing your daily report...")
        sheet.update_acell("O4", f"{today_date}-PM")

    # --- 4. CORE TRADING LOGIC ---
    try:
        active_count = len(active_trades_data)
        rows_to_delete = []

        for i, row in enumerate(data):
            r_num = i + 2
            if len(row) < 14 or "TRADED" not in str(row[10]).upper(): continue
            
            sym, price, sl, entry_p = str(row[1]), to_f(row[2]), to_f(row[7]), to_f(row[11])
            entry_time = str(row[12]) # Assumes Entry Time is Column M
            strategy = str(row[5])    # Column F
            
            # NO-SPAM TSL Logic
            new_sl = sl
            if pnl_pct >= 6.0: new_sl = max(sl, entry_p * 1.04)
            elif pnl_pct >= 4.0: new_sl = max(sl, entry_p * 1.02)
            elif pnl_pct >= 2.0: new_sl = max(sl, entry_p)
                
            if new_sl > sl:
                sheet.update_cell(r_num, 8, round(new_sl, 2))
                send_tg(f"🛡️ <b>TSL UPDATED: {sym}</b>\nNew SL: ₹{new_sl:.2f}\nP/L: {pnl_pct:+.2f}%")
                sl = new_sl

            # EXIT LOGIC
            if sl > 0 and price <= sl:
                exit_time_str = now.strftime('%Y-%m-%d %H:%M:%S')
                duration = calculate_duration(entry_time, now)
                
                trade_info = {
                    'sym': sym, 'entry_p': entry_p, 'exit_p': price, 
                    'entry_t': entry_time, 'exit_t': exit_time_str, 
                    'duration': duration, 'strat': strategy
                }
                
                if move_to_history(ss, trade_info):
                    send_tg(f"📉 <b>STOPLOSS HIT: {sym}</b>\nExit Price: ₹{price:.2f}\nDuration: {duration}")
                    rows_to_delete.append(r_num)
                    active_count -= 1

        if rows_to_delete:
            for r in reversed(rows_to_delete): sheet.delete_rows(r)
        
        sheet.update_acell("O3", f"Scanner Active | A:{active_count}/{MAX_ACTIVE_SLOTS} | {now.strftime('%H:%M:%S')}")
    except Exception as e: print(f"❌ Logic Error: {e}")

if __name__ == "__main__":
    run_trading_cycle()
