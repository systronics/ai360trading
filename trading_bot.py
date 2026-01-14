import os, json, gspread, requests, pandas as pd, pyotp, pytz
from dhanhq import dhanhq
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIG ---
LIVE_MODE = False  
MAX_ACTIVE_SLOTS = 5

def get_dhan_client():
    """Initialize Dhan client with TOTP authentication"""
    client_id = os.environ.get('DHAN_CLIENT_ID')
    totp_key = os.environ.get('DHAN_TOTP_KEY')
    pin = os.environ.get('DHAN_PIN')
    
    if not all([client_id, totp_key, pin]):
        print("❌ Missing Dhan credentials in environment variables")
        return None
    
    try:
        totp_gen = pyotp.TOTP(totp_key)
        temp_client = dhanhq(client_id, "")
        auth_data = temp_client.generate_token(pin, totp_gen.now())
        access_token = auth_data.get('access_token') or auth_data.get('data', {}).get('access_token')
        
        if not access_token:
            print("❌ Failed to get Dhan access token")
            return None
            
        return dhanhq(client_id, access_token)
    except Exception as e:
        print(f"❌ Dhan authentication failed: {e}")
        return None

def send_telegram(message):
    """Send notification to Telegram"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("⚠️ Telegram credentials not found, skipping notification")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = requests.post(
            url, 
            json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, 
            timeout=15
        )
        if response.status_code == 200:
            print("✅ Telegram notification sent")
        else:
            print(f"⚠️ Telegram API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Telegram failed: {e}")

def to_f(val):
    """Convert value to float, handling various formats"""
    if not val: 
        return 0.0
    clean = str(val).replace(',', '').replace('₹', '').replace('%', '').strip()
    try:
        return float(clean)
    except:
        return 0.0

def calculate_hold_duration(entry_time_str):
    """Calculate how many days/hours a position has been held"""
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
    except Exception as e:
        print(f"⚠️ Failed to calculate hold duration: {e}")
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
        
        # Append to History: Symbol, Entry Date, Entry Price, Exit Date, Exit Price, P/L %, Result, Hold Duration
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
    """Main trading cycle - runs every 2 minutes during market hours"""
    print("=" * 60)
    print(f"🤖 Trading Bot Cycle Started at {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 1. Setup Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_data = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
        
        if not creds_data:
            print("❌ Error: GCP_SERVICE_ACCOUNT_JSON not found in environment variables")
            return
        
        print("🔑 Authenticating with Google Sheets...")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_data), scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open("Ai360tradingAlgo")
        sheet = spreadsheet.worksheet("AlertLog")
        print("✅ Connected to Google Sheets")

        # 2. Kill Switch Check
        kill_switch = str(sheet.acell("O2").value).strip().upper()
        print(f"🔍 Kill Switch Status: {kill_switch}")
        
        if kill_switch != "YES":
            print(f"🛑 Trading is PAUSED (Kill Switch: {kill_switch})")
            sheet.update_acell("O3", f"Bot Paused | {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')}")
            return

        # 3. Get Data
        all_values = sheet.get_all_values()
        if len(all_values) < 2:
            print("ℹ️ No data in AlertLog sheet")
            return
            
        data_rows = all_values[1:]
        print(f"📊 Found {len(data_rows)} rows in AlertLog")
        
        # Filter for active trades
        active_trades = [r for r in data_rows if len(r) > 10 and "TRADED" in str(r[10]).upper() and "EXITED" not in str(r[10]).upper()]
        active_count = len(active_trades)
        print(f"📈 Active Trades: {active_count}/{MAX_ACTIVE_SLOTS}")

        # Track rows to delete (moved to History)
        rows_to_delete = []

        # 4. Process Rows - MONITOR & EXIT
        for i, row in enumerate(data_rows):
            row_num = i + 2
            if len(row) < 14:
                continue

            symbol = str(row[1]).strip()
            status = str(row[10]).strip().upper()
            
            if not symbol:
                continue

            try:
                price = to_f(row[2])         # Column C - Live Price (VLOOKUP formula)
                sl = to_f(row[7])            # Column H - StopLoss
                target = to_f(row[8])        # Column I - Target
                entry_price = to_f(row[11])  # Column L - Entry Price
                entry_time = str(row[12]).strip() if len(row) > 12 else ""  # Column M - Entry Time
            except (ValueError, IndexError) as e:
                print(f"⚠️ Skipping row {row_num}: Invalid data format")
                continue

            # --- CASE A: MONITOR ACTIVE TRADES & EXIT ---
            if "TRADED" in status and "EXITED" not in status:
                # Calculate current P/L % for logging (formula in sheet handles display)
                profit_pct = 0
                if entry_price > 0:
                    profit_pct = ((price - entry_price) / entry_price) * 100
                
                # Note: Column N (P/L %) is now auto-calculated by formula - no need to update
                print(f"📊 {symbol}: Price=₹{price}, Entry=₹{entry_price}, P/L={profit_pct:.2f}%")

                # --- TRAILING STOP-LOSS LOGIC ---
                new_sl = sl
                if profit_pct >= 4.0:
                    # At 4%+ profit, trail SL to 2% above entry
                    trail_at_2_pct = entry_price * 1.02
                    if trail_at_2_pct > sl:
                        new_sl = trail_at_2_pct
                elif profit_pct >= 2.0:
                    # At 2%+ profit, move SL to entry (breakeven)
                    if entry_price > sl:
                        new_sl = entry_price

                if new_sl > sl:
                    sheet.update_cell(row_num, 8, round(new_sl, 2))
                    print(f"🛡️ TSL Updated: {symbol} SL moved to ₹{round(new_sl, 2)}")
                    send_telegram(
                        f"🛡️ <b>TSL UPDATED:</b> {symbol}\n"
                        f"SL moved to: ₹{round(new_sl, 2)}\n"
                        f"Current Profit: {round(profit_pct, 1)}%"
                    )
                    sl = new_sl

                # --- EXIT CHECK ---
                is_target_hit = target > 0 and price >= target
                is_sl_hit = sl > 0 and price <= sl

                if is_target_hit or is_sl_hit:
                    label = "TARGET 🎯" if is_target_hit else "STOPLOSS 🛑"
                    exit_pnl = ((price - entry_price) / entry_price * 100) if entry_price > 0 else 0
                    
                    # Calculate hold duration
                    hold_duration = calculate_hold_duration(entry_time) if entry_time else "N/A"
                    
                    print(f"🚪 EXIT: {symbol} @ ₹{price} - {label} - P/L: {exit_pnl:+.2f}%")
                    
                    # Enhanced exit message
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
                    sheet.update_cell(row_num, 15, exit_time)
                    
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
                    entry_timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                    
                    print(f"🚀 NEW ENTRY: {symbol} @ ₹{price}")
                    
                    # Update status and entry details
                    sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                    sheet.update_cell(row_num, 12, price)        # Entry Price
                    sheet.update_cell(row_num, 13, entry_timestamp)  # Entry Time
                    # Column N (P/L %) auto-calculates via formula - no need to set
                    
                    send_telegram(
                        f"🚀 <b>PAPER ENTRY:</b> {symbol} @ ₹{price}\n"
                        f"Target: ₹{target} (6%)\n"
                        f"SL: ₹{sl} (1.5%)\n"
                        f"Slot: {active_count+1}/{MAX_ACTIVE_SLOTS}\n"
                        f"Time: {entry_timestamp}"
                    )
                    active_count += 1
                else:
                    print(f"⏳ Slots full ({active_count}/{MAX_ACTIVE_SLOTS}). {symbol} skipped.")

        # 5. Move completed trades to History
        if rows_to_delete:
            print(f"📜 Moving {len(rows_to_delete)} completed trades to History...")
            
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
                    print(f"❌ Failed to delete row {trade['row_num']}: {e}")

        # 6. AUTO-PROMOTE WAITING STOCKS
        if active_count < MAX_ACTIVE_SLOTS:
            print(f"🔄 Checking for WAITING stocks to promote... (Active: {active_count}/{MAX_ACTIVE_SLOTS})")
            
            # Re-fetch data after deletions
            all_values = sheet.get_all_values()
            data_rows = all_values[1:] if len(all_values) > 1 else []
            
            for i, row in enumerate(data_rows):
                row_num = i + 2
                if len(row) < 14:
                    continue
                
                symbol = str(row[1]).strip()
                status = str(row[10]).strip().upper()
                
                if not symbol:
                    continue
                
                # Promote WAITING stocks to active
                if "WAITING" in status and active_count < MAX_ACTIVE_SLOTS:
                    try:
                        price = to_f(row[2])
                        sl = to_f(row[7])
                        target = to_f(row[8])
                        
                        entry_timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                        
                        print(f"⬆️ PROMOTING: {symbol} from WAITING to ACTIVE")
                        
                        # Promote: Update status to TRADED, set entry price and entry time
                        sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                        sheet.update_cell(row_num, 12, price)
                        sheet.update_cell(row_num, 13, entry_timestamp)
                        # Column N (P/L %) auto-calculates via formula - no need to set
                        
                        send_telegram(
                            f"⬆️ <b>PROMOTED & ENTERED:</b> {symbol} @ ₹{price}\n"
                            f"Target: ₹{target} (6%)\n"
                            f"SL: ₹{sl} (1.5%)\n"
                            f"Slot: {active_count+1}/{MAX_ACTIVE_SLOTS}\n"
                            f"Time: {entry_timestamp}"
                        )
                        active_count += 1
                        print(f"✅ Promoted {symbol} from WAITING to ACTIVE")
                    except Exception as e:
                        print(f"❌ Failed to promote {symbol}: {e}")

        # 7. Count waiting stocks for display
        waiting_count = sum(1 for r in data_rows if len(r) > 10 and "WAITING" in str(r[10]).upper())

        # 8. Heartbeat Update
        now_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')
        heartbeat = f"Bot Live | Active: {active_count}/{MAX_ACTIVE_SLOTS} | Waiting: {waiting_count} | {now_time}"
        sheet.update_acell("O3", heartbeat)
        print(f"💚 {heartbeat}")
        
        print("=" * 60)
        print("✅ Trading cycle completed successfully")
        print("=" * 60)

    except Exception as e:
        print(f"❌ System Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to send error notification
        try:
            send_telegram(f"🚨 <b>BOT ERROR:</b>\n{str(e)[:200]}")
        except:
            pass

if __name__ == "__main__":
    run_trading_cycle()
