import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

IST = pytz.timezone('Asia/Kolkata')
MAX_ACTIVE_SLOTS = 5
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

def send_daily_summary(ss):
    """Send daily P/L summary at market close"""
    try:
        hist = ss.worksheet("History")
        today = datetime.now(IST).strftime('%Y-%m-%d')
        all_trades = hist.get_all_values()[1:]
        today_trades = [t for t in all_trades if t[3].startswith(today)] # Checking Exit Date
        
        if not today_trades:
            send_tg(f"📊 <b>Daily Summary - {today}</b>\n\nNo trades exited today.")
            return
        
        wins = sum(1 for t in today_trades if "WIN" in t[6])
        losses = len(today_trades) - wins
        total_pnl = sum(to_f(t[5]) for t in today_trades)
        
        summary = (
            f"📊 <b>Daily Summary - {today}</b>\n\n"
            f"Total Trades: {len(today_trades)}\n"
            f"Wins: {wins} 🟢 | Losses: {losses} 🔴\n"
            f"Win Rate: {(wins/len(today_trades)*100):.1f}%\n"
            f"Total P/L: {total_pnl:+.2f}%\n"
            f"\n{'='*25}\n"
            f"See you tomorrow! 🌙"
        )
        send_tg(summary)
    except Exception as e:
        print(f"❌ Summary Error: {e}")

def run_trading_cycle():
    """Main trading cycle with exact timings"""
    now = datetime.now(IST)
    curr_hm = now.strftime("%H:%M")
    curr_min = now.hour * 60 + now.minute
    
    print("=" * 60)
    print(f"🤖 Bot Started: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. 9:00 AM Message
    if curr_hm == "09:00":
        send_tg("🌅 <b>Good Morning, Market Open</b>")
        return

    # 2. 3:30 PM Message
    if curr_hm == "15:30":
        send_tg("🌙 <b>Good Bye, Market Close</b>")

    # 3. 3:45 PM Summary
    if curr_hm == "15:45":
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ['GCP_SERVICE_ACCOUNT_JSON']), scope)
            client = gspread.authorize(creds)
            ss = client.open("Ai360tradingAlgo")
            send_daily_summary(ss)
        except Exception as e:
            print(f"❌ Summary Trigger Error: {e}")
        return

    # 4. Trading Window Filter (9:15 AM - 3:30 PM)
    if not (555 <= curr_min <= 930):
        print(f"💤 Outside trading hours ({curr_hm}). Skipping logic.")
        return

    # --- START TRADING LOGIC ---
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ['GCP_SERVICE_ACCOUNT_JSON']), scope)
        client = gspread.authorize(creds)
        ss = client.open("Ai360tradingAlgo")
        sheet = ss.worksheet("AlertLog")
        
        # Kill Switch Check
        kill_switch = str(sheet.acell("O2").value).strip().upper()
        if kill_switch != "YES":
            sheet.update_acell("O3", f"Scanner Paused | {now.strftime('%H:%M:%S')}")
            return
        
        data = sheet.get_all_values()[1:]
        active_count = sum(1 for r in data if len(r) > 10 and "TRADED" in str(r[10]).upper() and "EXITED" not in str(r[10]).upper())
        
        rows_to_delete = []
        entries_made, exits_made, tsl_updates = 0, 0, 0

        # PHASE 1: MONITOR ACTIVE TRADES
        for i, row in enumerate(data):
            r_num = i + 2
            if len(row) < 14: continue
            sym = str(row[1]).strip()
            if not sym: continue
            
            stat = str(row[10]).strip().upper()
            if "TRADED" in stat and "EXITED" not in stat:
                try:
                    price, sl, entry_p = to_f(row[2]), to_f(row[7]), to_f(row[11])
                    entry_t, cat = str(row[12]), str(row[5])
                    
                    profit_pct = ((price - entry_p) / entry_p) * 100
                    
                    # TSL Logic
                    new_sl, tsl_triggered = sl, False
                    if profit_pct >= 6.0:
                        if (entry_p * 1.04) > sl: new_sl, tsl_triggered = entry_p * 1.04, True
                    elif profit_pct >= 4.0:
                        if (entry_p * 1.02) > sl: new_sl, tsl_triggered = entry_p * 1.02, True
                    elif profit_pct >= 2.0:
                        if entry_p > sl: new_sl, tsl_triggered = entry_p, True
                        
                    if tsl_triggered:
                        sheet.update_cell(r_num, 8, round(new_sl, 2))
                        send_tg(f"🛡️ <b>TSL UPDATED: {sym}</b>\nNew SL: ₹{new_sl:.2f}\nP/L: {profit_pct:+.2f}%")
                        sl, tsl_updates = new_sl, tsl_updates + 1

                    # Exit Check
                    if sl > 0 and price <= sl:
                        if move_to_history(ss, {'sym': sym, 'entry_p': entry_p, 'exit_p': price, 'entry_t': entry_t, 'exit_t': now.strftime('%Y-%m-%d %H:%M:%S'), 'cat': cat, 'reason': 'STOPLOSS'}):
                            rows_to_delete.append(r_num)
                            active_count -= 1
                            exits_made += 1
                except: continue

        if rows_to_delete:
            for r in reversed(rows_to_delete): sheet.delete_rows(r)
            data = sheet.get_all_values()[1:]

        # PHASE 2 & 3: PROMOTE WAITING & NEW ENTRIES
        for i, row in enumerate(data):
            r_num = i + 2
            if active_count >= MAX_ACTIVE_SLOTS or len(row) < 11: break
            sym, stat = str(row[1]).strip(), str(row[10]).strip().upper()
            
            if stat == "" or "WAITING" in stat:
                price, sl, tgt = to_f(row[2]), to_f(row[7]), to_f(row[11])
                if price == 0: continue
                
                sheet.update_cell(r_num, 11, "TRADED (PAPER)")
                sheet.update_cell(r_num, 12, price)
                sheet.update_cell(r_num, 13, now.strftime('%Y-%m-%d %H:%M:%S'))
                
                send_tg(f"🚀 <b>NEW ENTRY: {sym}</b>\nPrice: ₹{price:.2f}\nTarget: ₹{row[8]}\nSL: ₹{row[7]}\nSlot: {active_count+1}/{MAX_ACTIVE_SLOTS}")
                active_count += 1
                entries_made += 1

        heartbeat = f"Bot Active | A:{active_count}/{MAX_ACTIVE_SLOTS} | {now.strftime('%H:%M:%S')}"
        sheet.update_acell("O3", heartbeat)
        
    except Exception as e:
        print(f"❌ SYSTEM ERROR: {e}")

if __name__ == "__main__":
    run_trading_cycle()
