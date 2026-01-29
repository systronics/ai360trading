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
        print(f"✅ Moved {trade['sym']} to History: {result} ({pnl:.2f}%)")
        return True
    except Exception as e:
        print(f"❌ Failed to move {trade['sym']} to History: {e}")
        return False

def send_daily_summary(ss):
    """Send daily P/L summary at market close"""
    try:
        hist = ss.worksheet("History")
        today = datetime.now(IST).strftime('%Y-%m-%d')
        
        all_trades = hist.get_all_values()[1:]  # Skip header
        today_trades = [t for t in all_trades if t[1].startswith(today)]  # Entry Date column
        
        if not today_trades:
            send_tg(f"📊 <b>Daily Summary - {today}</b>\n\nNo trades today.")
            return
        
        wins = sum(1 for t in today_trades if "WIN" in t[6])
        losses = len(today_trades) - wins
        
        total_pnl = sum(to_f(t[5]) for t in today_trades)  # P/L % column
        
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
        print("✅ Daily summary sent")
    except Exception as e:
        print(f"❌ Failed to send daily summary: {e}")

def send_good_morning():
    """Send good morning message at market open"""
    msg = (
        f"🌅 <b>Good Morning!</b>\n\n"
        f"Market opens in 15 minutes.\n"
        f"Bot is active and ready.\n"
        f"Max Positions: {MAX_ACTIVE_SLOTS}\n\n"
        f"Let's make today profitable! 💪"
    )
    send_tg(msg)
    print("✅ Good morning message sent")

def run_trading_cycle():
    """Main trading cycle - runs every 2 minutes"""
    print("=" * 60)
    print(f"🤖 Bot Started: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    current_time = datetime.now(IST)
    current_hour = current_time.hour
    current_minute = current_time.minute
    
    try:
        # Setup Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(os.environ['GCP_SERVICE_ACCOUNT_JSON']), scope
        )
        client = gspread.authorize(creds)
        ss = client.open("Ai360tradingAlgo")
        sheet = ss.worksheet("AlertLog")
        print("✅ Connected to Google Sheets")
        
        # Send Good Morning at 9:15 AM (once per day)
        if current_hour == 9 and current_minute == 15:
            send_good_morning()
        
        # Send Daily Summary at 3:30 PM (once per day)
        if current_hour == 15 and current_minute == 30:
            send_daily_summary(ss)
            print("📊 Daily summary triggered at market close")
            return
        
        # Kill Switch Check
        kill_switch = str(sheet.acell("O2").value).strip().upper()
        if kill_switch != "YES":
            print(f"🛑 Trading PAUSED (Kill Switch: {kill_switch})")
            sheet.update_acell("O3", f"Scanner Paused | {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            return
        
        # Get all data
        data = sheet.get_all_values()[1:]  # Skip header
        print(f"📊 Loaded {len(data)} rows from AlertLog")
        
        # Calculate CORRECT active count (exclude EXITED trades)
        active_count = sum(1 for r in data if len(r) > 10 and "TRADED" in str(r[10]).upper() and "EXITED" not in str(r[10]).upper())
        print(f"📈 Active trades: {active_count}/{MAX_ACTIVE_SLOTS}")
        
        rows_to_delete = []
        entries_made = 0
        exits_made = 0
        tsl_updates = 0
        
        # PHASE 1: MONITOR ACTIVE TRADES & EXIT
        for i, row in enumerate(data):
            r_num = i + 2
            if len(row) < 14:
                continue
            
            sym = str(row[1]).strip()
            if not sym:
                continue
            
            stat = str(row[10]).strip().upper()
            
            # Only process ACTIVE trades (not EXITED, not WAITING)
            if "TRADED" in stat and "EXITED" not in stat:
                try:
                    price = to_f(row[2])       # Column C - Live Price
                    sl = to_f(row[7])          # Column H - StopLoss
                    tgt = to_f(row[8])         # Column I - Target
                    entry_p = to_f(row[11])    # Column L - Entry Price
                    entry_t = str(row[12]).strip() if len(row) > 12 else ""
                    cat = str(row[5]).strip() if len(row) > 5 else ""
                    
                    if entry_p == 0 or price == 0:
                        print(f"⚠️ {sym}: Invalid data (entry={entry_p}, price={price})")
                        continue
                    
                    # Calculate current profit %
                    profit_pct = ((price - entry_p) / entry_p) * 100
                    print(f"📊 {sym}: Price=₹{price:.2f}, Entry=₹{entry_p:.2f}, P/L={profit_pct:+.2f}%, SL=₹{sl:.2f}")
                    
                    # TRAILING STOP-LOSS LOGIC
                    new_sl = sl
                    tsl_triggered = False
                    
                    if profit_pct >= 6.0:
                        # At 6%+ profit, trail SL to 4% above entry
                        trail_target = entry_p * 1.04
                        if trail_target > sl:
                            new_sl = trail_target
                            tsl_triggered = True
                    elif profit_pct >= 4.0:
                        # At 4%+ profit, trail SL to 2% above entry
                        trail_target = entry_p * 1.02
                        if trail_target > sl:
                            new_sl = trail_target
                            tsl_triggered = True
                    elif profit_pct >= 2.0:
                        # At 2%+ profit, move SL to breakeven
                        if entry_p > sl:
                            new_sl = entry_p
                            tsl_triggered = True
                    
                    # Update trailing stop-loss in sheet
                    if tsl_triggered:
                        sheet.update_cell(r_num, 8, round(new_sl, 2))
                        print(f"🛡️ TSL Updated: {sym} SL → ₹{new_sl:.2f} (was ₹{sl:.2f})")
                        send_tg(
                            f"🛡️ <b>TSL UPDATED: {sym}</b>\n"
                            f"New SL: ₹{new_sl:.2f}\n"
                            f"Current P/L: {profit_pct:+.2f}%"
                        )
                        sl = new_sl
                        tsl_updates += 1
                    
                    # EXIT CHECK - ONLY ON STOP-LOSS HIT (NOT TARGET)
                    # We want to ride the trend, so we never exit at target
                    if sl > 0 and price <= sl:
                        print(f"🚪 EXIT: {sym} @ ₹{price:.2f} - STOPLOSS HIT")
                        
                        exit_time = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
                        
                        if move_to_history(ss, {
                            'sym': sym,
                            'entry_p': entry_p,
                            'exit_p': price,
                            'entry_t': entry_t,
                            'exit_t': exit_time,
                            'cat': cat,
                            'reason': 'STOPLOSS'
                        }):
                            rows_to_delete.append(r_num)
                            active_count -= 1
                            exits_made += 1
                
                except Exception as e:
                    print(f"❌ Error processing {sym}: {e}")
        
        # Delete exited trades (reverse order to maintain indices)
        if rows_to_delete:
            print(f"🗑️ Deleting {len(rows_to_delete)} exited trades...")
            for r in reversed(rows_to_delete):
                try:
                    sheet.delete_rows(r)
                    print(f"✅ Deleted row {r}")
                except Exception as e:
                    print(f"❌ Failed to delete row {r}: {e}")
        
        # RE-FETCH DATA after deletions
        print("🔄 Re-fetching data after deletions...")
        data = sheet.get_all_values()[1:]
        
        # Recalculate active count
        active_count = sum(1 for r in data if len(r) > 10 and "TRADED" in str(r[10]).upper() and "EXITED" not in str(r[10]).upper())
        print(f"📈 Active trades after exits: {active_count}/{MAX_ACTIVE_SLOTS}")
        
        # PHASE 2: PROMOTE WAITING STOCKS
        if active_count < MAX_ACTIVE_SLOTS:
            print(f"⬆️ Checking for WAITING stocks to promote...")
            
            for i, row in enumerate(data):
                r_num = i + 2
                if len(row) < 14:
                    continue
                
                sym = str(row[1]).strip()
                if not sym:
                    continue
                
                stat = str(row[10]).strip().upper()
                
                if "WAITING" in stat and active_count < MAX_ACTIVE_SLOTS:
                    try:
                        price = to_f(row[2])
                        sl = to_f(row[7])
                        tgt = to_f(row[8])
                        
                        if price == 0:
                            print(f"⚠️ {sym}: No live price available, skipping")
                            continue
                        
                        entry_time = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
                        
                        print(f"⬆️ PROMOTING: {sym} @ ₹{price:.2f}")
                        
                        sheet.update_cell(r_num, 11, "TRADED (PAPER)")
                        sheet.update_cell(r_num, 12, price)
                        sheet.update_cell(r_num, 13, entry_time)
                        
                        send_tg(
                            f"⬆️ <b>PROMOTED: {sym}</b>\n"
                            f"Entry: ₹{price:.2f}\n"
                            f"Target: ₹{tgt:.2f}\n"
                            f"SL: ₹{sl:.2f}\n"
                            f"Slot: {active_count + 1}/{MAX_ACTIVE_SLOTS}"
                        )
                        
                        active_count += 1
                        entries_made += 1
                        print(f"✅ Promoted {sym}")
                        
                    except Exception as e:
                        print(f"❌ Failed to promote {sym}: {e}")
        
        # PHASE 3: TAKE NEW ENTRIES (Empty status)
        if active_count < MAX_ACTIVE_SLOTS:
            for i, row in enumerate(data):
                r_num = i + 2
                if len(row) < 14:
                    continue
                
                sym = str(row[1]).strip()
                if not sym:
                    continue
                
                stat = str(row[10]).strip()
                
                if stat == "" and active_count < MAX_ACTIVE_SLOTS:
                    try:
                        price = to_f(row[2])
                        sl = to_f(row[7])
                        tgt = to_f(row[8])
                        
                        if price == 0:
                            print(f"⚠️ {sym}: No live price, skipping")
                            continue
                        
                        entry_time = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
                        
                        print(f"🚀 NEW ENTRY: {sym} @ ₹{price:.2f}")
                        
                        sheet.update_cell(r_num, 11, "TRADED (PAPER)")
                        sheet.update_cell(r_num, 12, price)
                        sheet.update_cell(r_num, 13, entry_time)
                        
                        send_tg(
                            f"🚀 <b>NEW ENTRY: {sym}</b>\n"
                            f"Entry: ₹{price:.2f}\n"
                            f"Target: ₹{tgt:.2f}\n"
                            f"SL: ₹{sl:.2f}\n"
                            f"Slot: {active_count + 1}/{MAX_ACTIVE_SLOTS}"
                        )
                        
                        active_count += 1
                        entries_made += 1
                        
                    except Exception as e:
                        print(f"❌ Failed to enter {sym}: {e}")
        
        # Count waiting stocks
        waiting_count = sum(1 for r in data if len(r) > 10 and "WAITING" in str(r[10]).upper())
        
        # Update heartbeat in O3
        heartbeat = f"Bot Active | A:{active_count}/{MAX_ACTIVE_SLOTS} | W:{waiting_count} | {current_time.strftime('%H:%M:%S')}"
        sheet.update_acell("O3", heartbeat)
        print(f"💚 {heartbeat}")
        
        # Summary
        print("=" * 60)
        print(f"✅ Cycle Complete:")
        print(f"   Entries: {entries_made}")
        print(f"   Exits: {exits_made}")
        print(f"   TSL Updates: {tsl_updates}")
        print(f"   Active: {active_count}/{MAX_ACTIVE_SLOTS}")
        print(f"   Waiting: {waiting_count}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ SYSTEM ERROR: {e}")
        import traceback
        traceback.print_exc()
        try:
            send_tg(f"🚨 <b>BOT ERROR:</b>\n{str(e)[:200]}")
        except:
            pass

if __name__ == "__main__":
    run_trading_cycle()
