import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

IST = pytz.timezone('Asia/Kolkata')
MAX_ACTIVE_SLOTS = 10 
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

def calculate_hold_duration(entry_time_str):
    """Calculate position hold time"""
    try:
        entry_dt = datetime.strptime(entry_time_str, '%Y-%m-%d %H:%M:%S')
        entry_dt = IST.localize(entry_dt)
        now = datetime.now(IST)
        delta = now - entry_dt
        days = delta.days
        hours = delta.seconds // 3600
        return f"{days}d {hours}h" if days > 0 else f"{hours}h"
    except:
        return "0h"

def move_to_history(ss, trade):
    """Move completed trade to History sheet"""
    try:
        hist = ss.worksheet("History")
        pnl = ((trade['exit_p'] - trade['entry_p']) / trade['entry_p'] * 100) if trade['entry_p'] > 0 else 0
        result = "WIN 🟢" if pnl > 0 else "LOSS 🔴"
        hold_time = calculate_hold_duration(trade['entry_t']) if trade.get('entry_t') else "0h"
        
        hist.append_row([
            trade['sym'],
            trade['entry_t'],
            round(trade['entry_p'], 2),
            trade['exit_t'],
            round(trade['exit_p'], 2),
            f"{pnl:.2f}%",
            result,
            hold_time,
            trade.get('cat', '')
        ])
        
        exit_label = "🎯 TARGET" if "TARGET" in trade.get('reason', '') else "🛑 STOPLOSS"
        send_tg(
            f"💰 <b>EXIT: {trade['sym']}</b>\n"
            f"Entry: ₹{trade['entry_p']:.2f}\n"
            f"Exit: ₹{trade['exit_p']:.2f}\n"
            f"P/L: {pnl:+.2f}%\n"
            f"Result: {exit_label}\n"
            f"Hold: {hold_time}"
        )
        return True
    except Exception as e:
        print(f"❌ History Error: {e}")
        return False

def send_daily_summary(ss, active_trades_data):
    """Professional Summary: Shows Closed Trades AND Open Portfolio Status"""
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
            f"Realized P/L: {closed_pnl:+.2f}%\n"
            f"{portfolio_report}\n"
            f"💰 <b>Total Strategy P/L: {(closed_pnl + total_open_pnl):+.2f}%</b>\n"
            f"{'='*25}\n"
            f"<i>Holding for targets. See you tomorrow!</i> 🌙"
        )
        send_tg(summary)
    except Exception as e:
        print(f"❌ Summary Error: {e}")

def run_trading_cycle():
    now = datetime.now(IST)
    curr_hm = now.strftime("%H:%M")
    curr_min = now.hour * 60 + now.minute
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ['GCP_SERVICE_ACCOUNT_JSON']), scope)
    client = gspread.authorize(creds)
    ss = client.open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")

    today_prefix = now.strftime('%Y-%m-%d')
    sent_status = str(sheet.acell("O4").value).strip()

    # Get data early for Morning Report and Trading Logic
    data = sheet.get_all_values()[1:]
    active_trades_data = []
    
    # Process current active trades for data list
    for row in data:
        if len(row) >= 12 and "TRADED" in str(row[10]).upper():
            sym, price, entry_p = str(row[1]), to_f(row[2]), to_f(row[11])
            pnl_pct = ((price - entry_p) / entry_p) * 100
            active_trades_data.append({'sym': sym, 'pnl': pnl_pct})

    # --- 1. Good Morning Window (Includes Portfolio Status) ---
    if "09:00" <= curr_hm <= "09:15" and sent_status != f"{today_prefix}-AM":
        portfolio_status = ""
        if active_trades_data:
            portfolio_status = "\n\n📈 <b>Active Portfolio Status:</b>\n"
            for t in active_trades_data:
                portfolio_status += f"• {t['sym']}: {t['pnl']:+.2f}%\n"
        
        send_tg(f"🌅 <b>Good Morning! Market is Opening.</b>\nBot is active and monitoring 10 slots.{portfolio_status}")
        sheet.update_acell("O4", f"{today_prefix}-AM")

    # --- 2. Market Close Window ---
    if "15:30" <= curr_hm <= "15:45" and sent_status != f"{today_prefix}-PM":
        send_tg("🌙 <b>Market Closed. Preparing final report...</b>")
        sheet.update_acell("O4", f"{today_prefix}-PM")

    # --- CORE TRADING LOGIC ---
    try:
        active_count = len(active_trades_data)
        rows_to_delete = []

        # MONITOR ACTIVE TRADES (Exits & Fixed TSL)
        for i, row in enumerate(data):
            r_num = i + 2
            if len(row) < 14 or "TRADED" not in str(row[10]).upper(): continue
            
            try:
                sym, price, sl, entry_p = str(row[1]), to_f(row[2]), to_f(row[7]), to_f(row[11])
                entry_t, cat = str(row[12]), str(row[5])
                profit_pct = ((price - entry_p) / entry_p) * 100
                
                # FIXED TSL Logic
                new_sl = sl
                if profit_pct >= 6.0: new_sl = max(sl, entry_p * 1.04)
                elif profit_pct >= 4.0: new_sl = max(sl, entry_p * 1.02)
                elif profit_pct >= 2.0: new_sl = max(sl, entry_p)
                    
                if new_sl > sl:
                    sheet.update_cell(r_num, 8, round(new_sl, 2))
                    send_tg(f"🛡️ <b>TSL TRAILED: {sym}</b>\nNew SL: ₹{new_sl:.2f}\nFloating P/L: {profit_pct:+.2f}%")
                    sl = new_sl

                # Exit Check
                if sl > 0 and price <= sl:
                    if move_to_history(ss, {'sym': sym, 'entry_p': entry_p, 'exit_p': price, 'entry_t': entry_t, 'exit_t': now.strftime('%Y-%m-%d %H:%M:%S'), 'cat': cat, 'reason': 'STOPLOSS'}):
                        rows_to_delete.append(r_num)
                        active_count -= 1
            except: continue

        # --- 3. SUMMARY TRIGGER ---
        if "15:45" <= curr_hm <= "16:15" and sent_status != f"{today_prefix}-SUM":
            send_daily_summary(ss, active_trades_data)
            sheet.update_acell("O4", f"{today_prefix}-SUM")

        # PHASE 2: NEW ENTRIES (Trading Hours Only)
        if 555 <= curr_min <= 930:
            kill_switch = str(sheet.acell("O2").value).strip().upper()
            if kill_switch == "YES":
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

        if rows_to_delete:
            for r in reversed(rows_to_delete): sheet.delete_rows(r)
        
        sheet.update_acell("O3", f"Scanner Active | A:{active_count}/{MAX_ACTIVE_SLOTS} | {now.strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ SYSTEM ERROR: {e}")

if __name__ == "__main__":
    run_trading_cycle()
