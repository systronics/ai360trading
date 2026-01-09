import os, json, gspread, requests, pandas as pd, pyotp, pytz
from dhanhq import dhanhq
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIG ---
LIVE_MODE = False  
MAX_ACTIVE_SLOTS = 5
MOVE_TO_HISTORY_AFTER_CYCLES = 2  # Move to History after 2 cycles (to let formulas update)

def get_dhan_client():
    client_id = os.environ.get('DHAN_CLIENT_ID')
    totp_key = os.environ.get('DHAN_TOTP_KEY')
    pin = os.environ.get('DHAN_PIN')
    totp_gen = pyotp.TOTP(totp_key)
    
    temp_client = dhanhq(client_id, "")
    auth_data = temp_client.generate_token(pin, totp_gen.now())
    access_token = auth_data.get('access_token') or auth_data.get('data', {}).get('access_token')
    return dhanhq(client_id, access_token)

def send_telegram(message):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=15)
    except Exception as e:
        print(f"Telegram failed: {e}")

def to_f(val):
    """Convert value to float, handling various formats"""
    if not val: return 0.0
    clean = str(val).replace(',', '').replace('₹', '').replace('%', '').strip()
    try:
        return float(clean)
    except:
        return 0.0

def calculate_hold_duration(entry_time_str):
    """Calculate how many days a position has been held"""
    try:
        entry_time = datetime.strptime(entry_time_str, '%Y-%m-%d %H:%M:%S')
        entry_time = pytz.timezone('Asia/Kolkata').localize(entry_time)
        now = datetime.now(pytz.timezone('Asia/Kolkata'))
        delta = now - entry_time
        
        days = delta.days
        hours = delta.seconds // 3600
        
        if days > 0:
            return f"{days}d {hours}h"
        else:
            return f"{hours}h"
    except:
        return "0h"

def move_to_history(spreadsheet, symbol, entry_price, exit_price, status, exit_date, entry_date):
    """Move completed trade to History sheet with enhanced metrics"""
    try:
        history_sheet = spreadsheet.worksheet("History")
        
        # Determine result
        result = "WIN" if "TARGET" in status else "LOSS"
        
        # Calculate P/L %
        pnl_pct = ((exit_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
        
        # Calculate hold duration
        try:
            entry_dt = datetime.strptime(entry_date, '%Y-%m-%d %H:%M:%S')
            exit_dt = datetime.strptime(exit_date, '%Y-%m-%d %H:%M:%S')
            hold_duration = exit_dt - entry_dt
            days_held = hold_duration.days
            hours_held = hold_duration.seconds // 3600
            duration_str = f"{days_held}d {hours_held}h" if days_held > 0 else f"{hours_held}h"
        except:
            duration_str = "N/A"
        
        # Append to History sheet: Symbol, Entry Date, Entry Price, Exit Date, Exit Price, P/L %, Result, Hold Duration
        history_sheet.append_row([
            symbol,
            entry_date,
            round(entry_price, 2),
            exit_date,
            round(exit_price, 2),
            f"{pnl_pct:.2f}%",
            result,
            duration_str
        ])
        
        print(f"✅ Moved {symbol} to History: {result} ({pnl_pct:.2f}%) - Held {duration_str}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to move {symbol} to History: {e}")
        return False

def run_trading_cycle():
    try:
        # 1. Setup Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_data = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
        if not creds_data:
            print("Error: GCP_SERVICE_ACCOUNT_JSON not found")
            return
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_data), scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open("Ai360tradingAlgo")
        sheet = spreadsheet.worksheet("AlertLog")

        # 2. Kill Switch Check
        kill_switch = str(sheet.acell("O2").value).strip().upper()
        if kill_switch != "YES":
            print(f"🛑 Kill Switch is {kill_switch}. Stopping.")
            return

        # 3. Get Data
        all_values = sheet.get_all_values()
        if len(all_values) < 2: return
        data_rows = all_values[1:]
        
        # Filter for active trades in slot check
        active_trades = [r for r in data_rows if len(r) > 10 and "TRADED" in str(r[10]).upper() and "EXITED" not in str(r[10]).upper()]
        active_count = len(active_trades)

        # Track rows to delete (moved to History)
        rows_to_delete = []

        # 4. Process Rows - MONITOR & EXIT
        for i, row in enumerate(data_rows):
            row_num = i + 2
            if len(row) < 14: continue  # Need at least 14 columns (up to N)

            symbol = str(row[1]).strip()
            status = str(row[10]).strip().upper()
            if not symbol: continue

            try:
                price = to_f(row[2])         # Column C - Live Price
                sl = to_f(row[7])            # Column H - StopLoss
                target = to_f(row[8])        # Column I - Target
                entry_price = to_f(row[11])  # Column L - Entry Price
                entry_time = str(row[12]).strip() if len(row) > 12 else ""  # Column M - Entry Time
            except ValueError:
                continue

            # --- CASE A: MONITOR EXIT & TRAILING ---
            if "TRADED" in status and "EXITED" not in status:
                # Calculate current P/L %
                profit_pct = 0
                if entry_price > 0:
                    profit_pct = ((price - entry_price) / entry_price) * 100
                
                # Update P/L % in real-time (Column N)
                sheet.update_cell(row_num, 14, f"{profit_pct:.2f}%")

                # --- TRAILING LOGIC ---
                new_sl = sl
                if profit_pct >= 4.0:
                    trail_at_2_pct = entry_price * 1.02
                    if trail_at_2_pct > sl:
                        new_sl = trail_at_2_pct
                elif profit_pct >= 2.0:
                    if entry_price > sl:
                        new_sl = entry_price

                if new_sl > sl:
                    sheet.update_cell(row_num, 8, round(new_sl, 2)) # Update Column H
                    send_telegram(f"🛡️ <b>TSL UPDATED:</b> {symbol}\nSL moved to: ₹{round(new_sl, 2)}\nCurrent Profit: {round(profit_pct, 1)}%")
                    sl = new_sl 

                # --- EXIT CHECK ---
                is_target_hit = target > 0 and price >= target
                is_sl_hit = sl > 0 and price <= sl

                if is_target_hit or is_sl_hit:
                    label = "TARGET 🎯" if is_target_hit else "STOPLOSS 🛑"
                    exit_pnl = ((price - entry_price) / entry_price * 100) if entry_price > 0 else 0
                    
                    # Calculate hold duration
                    hold_duration = calculate_hold_duration(entry_time) if entry_time else "N/A"
                    
                    # Enhanced exit message with P/L and hold duration
                    send_telegram(
                        f"💰 <b>PAPER EXIT:</b> {symbol} @ ₹{price}\n"
                        f"Result: {label}\n"
                        f"Entry: ₹{entry_price}\n"
                        f"P/L: {exit_pnl:+.2f}%\n"
                        f"Hold Duration: {hold_duration}"
                    )
                    
                    # Update exit status and timestamp
                    exit_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                    sheet.update_cell(row_num, 11, f"EXITED ({label})")
                    sheet.update_cell(row_num, 1, exit_time)  # Update timestamp in Column A
                    
                    active_count -= 1
                    
                    # Mark for moving to History
                    rows_to_delete.append({
                        'row_num': row_num,
                        'symbol': symbol,
                        'entry_price': entry_price,
                        'exit_price': price,
                        'status': f"EXITED ({label})",
                        'exit_date': exit_time,
                        'entry_date': entry_time
                    })

            # --- CASE B: NEW SIGNAL (Entry) ---
            elif status == "" and symbol:
                if active_count < MAX_ACTIVE_SLOTS:
                    # Get current timestamp for entry
                    entry_timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Update status to lock the slot
                    sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                    # Store Entry Price in Column L
                    sheet.update_cell(row_num, 12, price)
                    # Store Entry Time in Column M (not entry price!)
                    sheet.update_cell(row_num, 13, entry_timestamp)
                    # Initialize P/L % as 0.00%
                    sheet.update_cell(row_num, 14, "0.00%")
                    
                    send_telegram(
                        f"🚀 <b>PAPER ENTRY:</b> {symbol} @ ₹{price}\n"
                        f"Target: ₹{target} (6%)\n"
                        f"SL: ₹{sl} (1.5%)\n"
                        f"Slot: {active_count+1}/5\n"
                        f"Time: {entry_timestamp}"
                    )
                    active_count += 1
                else:
                    print(f"⏳ Slots full. {symbol} skipped.")

        # 5. Move completed trades to History
        for trade in rows_to_delete:
            success = move_to_history(
                spreadsheet,
                trade['symbol'],
                trade['entry_price'],
                trade['exit_price'],
                trade['status'],
                trade['exit_date'],
                trade['entry_date']
            )
            
            # Delete row from AlertLog after moving to History
            if success:
                try:
                    sheet.delete_rows(trade['row_num'])
                    print(f"🗑️ Deleted {trade['symbol']} from AlertLog")
                except Exception as e:
                    print(f"Failed to delete row {trade['row_num']}: {e}")

        # 6. AUTO-PROMOTE WAITING STOCKS
        if active_count < MAX_ACTIVE_SLOTS:
            print(f"🔄 Checking for WAITING stocks to promote... (Active: {active_count}/{MAX_ACTIVE_SLOTS})")
            
            # Re-fetch data after deletions
            all_values = sheet.get_all_values()
            data_rows = all_values[1:] if len(all_values) > 1 else []
            
            for i, row in enumerate(data_rows):
                row_num = i + 2
                if len(row) < 14: continue
                
                symbol = str(row[1]).strip()
                status = str(row[10]).strip().upper()
                
                if not symbol: continue
                
                # Promote WAITING stocks to active
                if "WAITING" in status and active_count < MAX_ACTIVE_SLOTS:
                    try:
                        price = to_f(row[2])
                        sl = to_f(row[7])
                        target = to_f(row[8])
                        
                        # Get entry timestamp
                        entry_timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Promote: Update status to TRADED, set entry price, entry time, and P/L %
                        sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                        sheet.update_cell(row_num, 12, price)
                        sheet.update_cell(row_num, 13, entry_timestamp)
                        sheet.update_cell(row_num, 14, "0.00%")
                        
                        send_telegram(
                            f"⬆️ <b>PROMOTED & ENTERED:</b> {symbol} @ ₹{price}\n"
                            f"Target: ₹{target} (6%)\n"
                            f"SL: ₹{sl} (1.5%)\n"
                            f"Slot: {active_count+1}/5\n"
                            f"Time: {entry_timestamp}"
                        )
                        active_count += 1
                        print(f"✅ Promoted {symbol} from WAITING to ACTIVE")
                    except Exception as e:
                        print(f"Failed to promote {symbol}: {e}")

        # 7. Count waiting stocks for display
        waiting_count = sum(1 for r in data_rows if len(r) > 10 and "WAITING" in str(r[10]).upper())

        # 8. Heartbeat Update
        now_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')
        sheet.update_acell("O3", f"Bot Live | Active: {active_count}/5 | Waiting: {waiting_count} | {now_time}")

    except Exception as e:
        print(f"System Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_trading_cycle()
