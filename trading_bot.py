import os
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# --- CAPITAL MANAGEMENT CONFIG ---
TOTAL_CAPITAL = 50000      # Total trading capital
RISK_PERCENT = 1.0         # Risk 1% per trade (₹500)
RISK_PER_TRADE = int(TOTAL_CAPITAL * RISK_PERCENT / 100)  # ₹500
MAX_POSITIONS = 5          # Maximum 5 concurrent positions
CAPITAL_PER_POSITION = TOTAL_CAPITAL / MAX_POSITIONS  # ₹10,000 each

# --- TRADE PARAMETERS ---
SHEET_NAME = "Ai360tradingAlgo"
SMA_BUFFER_PERCENT = 2.0   # 2% below SMA20 for stop loss
PRIMARY_RR = 3.0           # Target at 3x risk
TELEGRAM_ALERTS = True     # Send Telegram updates

# --- SETUP ---
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
creds = Credentials.from_service_account_info(eval(creds_json), scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open(SHEET_NAME)
alert_sheet = sh.worksheet('AlertLog')

# Telegram config (optional)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

def send_telegram(message):
    """Send Telegram notification"""
    if not TELEGRAM_ALERTS or not TELEGRAM_TOKEN:
        return
    
    try:
        import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram error: {e}")

def calculate_institutional_levels(entry_price, sma20, priority_score):
    """Calculate stop loss, target, and position size"""
    
    # Stop Loss: SMA20 - 2% buffer
    stop_loss = round(sma20 * (1 - SMA_BUFFER_PERCENT/100), 2)
    
    # If stop too close, use 3% fixed
    risk_per_share = entry_price - stop_loss
    if risk_per_share < (entry_price * 0.01):
        stop_loss = round(entry_price * 0.97, 2)
        risk_per_share = entry_price - stop_loss
    
    # Position sizing: Risk ₹500 per trade
    quantity = int(RISK_PER_TRADE / risk_per_share)
    
    # Don't exceed capital per position
    max_qty = int(CAPITAL_PER_POSITION / entry_price)
    if quantity > max_qty:
        quantity = max_qty
    
    if quantity < 1:
        quantity = 1
    
    # Target: 1:3 RR
    target = round(entry_price + (risk_per_share * PRIMARY_RR), 2)
    rr_ratio = f"1:{PRIMARY_RR}"
    
    return stop_loss, target, rr_ratio, quantity

def get_current_price(symbol):
    """
    Get current price from Nifty200 sheet
    In production, this would fetch live price from API
    """
    try:
        nifty_sheet = sh.worksheet('Nifty200')
        records = nifty_sheet.get_all_records()
        
        for row in records:
            if row.get('Symbol') == symbol:
                return float(row.get('Price', 0))
        
        return None
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None

def enter_new_trades():
    """Scan for new trade signals and enter positions"""
    
    records = alert_sheet.get_all_records()
    new_trades_count = 0
    
    print(f"\n{'='*50}")
    print(f"🔍 SCANNING FOR NEW TRADES")
    print(f"{'='*50}")
    print(f"💰 Capital: ₹{TOTAL_CAPITAL:,} | Risk/Trade: ₹{RISK_PER_TRADE}")
    
    for i, row in enumerate(records):
        row_num = i + 2
        
        symbol = row.get('Symbol', '').strip()
        entry_price = float(row.get('Price', 0))
        sma20 = float(row.get('Trend', 0))
        priority = int(row.get('Priority', 0))
        status = str(row.get('Status', '')).strip()
        
        if status == "" and symbol and entry_price > 0:
            if new_trades_count < MAX_POSITIONS:
                
                # Calculate levels
                stop_loss, target, rr_ratio, quantity = calculate_institutional_levels(
                    entry_price, sma20, priority
                )
                
                capital_used = entry_price * quantity
                risk_amount = (entry_price - stop_loss) * quantity
                reward_amount = (target - entry_price) * quantity
                
                print(f"\n✅ ENTERING TRADE #{new_trades_count + 1}")
                print(f"   Symbol: {symbol}")
                print(f"   Entry: ₹{entry_price} | Qty: {quantity} shares")
                print(f"   Capital Used: ₹{capital_used:,.0f}")
                print(f"   Stop: ₹{stop_loss} | Target: ₹{target}")
                print(f"   Risk: ₹{risk_amount:.0f} | Reward: ₹{reward_amount:.0f} | RR: {rr_ratio}")
                
                try:
                    # Update AlertLog
                    alert_sheet.update_cell(row_num, 8, stop_loss)              # H: StopLoss
                    alert_sheet.update_cell(row_num, 9, target)                 # I: Target
                    alert_sheet.update_cell(row_num, 10, rr_ratio)              # J: RR_Ratio
                    alert_sheet.update_cell(row_num, 11, "OPEN")                # K: Status
                    alert_sheet.update_cell(row_num, 12, entry_price)           # L: Entry_Price
                    alert_sheet.update_cell(row_num, 13, datetime.now().strftime("%H:%M"))  # M: Entry_Time
                    
                    # Send Telegram alert
                    msg = (
                        f"🟢 <b>TRADE ENTERED</b>\n\n"
                        f"Symbol: {symbol}\n"
                        f"Entry: ₹{entry_price} × {quantity} shares\n"
                        f"Capital: ₹{capital_used:,.0f}\n"
                        f"Stop: ₹{stop_loss} (-₹{risk_amount:.0f})\n"
                        f"Target: ₹{target} (+₹{reward_amount:.0f})\n"
                        f"RR: {rr_ratio}"
                    )
                    send_telegram(msg)
                    
                    new_trades_count += 1
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            else:
                break
    
    print(f"\n{'='*50}")
    print(f"📊 New Trades: {new_trades_count}/{MAX_POSITIONS}")
    print(f"{'='*50}\n")
    
    return new_trades_count

def monitor_open_positions():
    """Monitor all open positions and exit at stop/target"""
    
    records = alert_sheet.get_all_records()
    exits_count = 0
    
    print(f"\n{'='*50}")
    print(f"👁️  MONITORING OPEN POSITIONS")
    print(f"{'='*50}")
    
    for i, row in enumerate(records):
        row_num = i + 2
        
        status = str(row.get('Status', '')).strip()
        
        # Only check OPEN positions
        if status != "OPEN":
            continue
        
        symbol = row.get('Symbol', '').strip()
        entry_price = float(row.get('Entry_Price', 0))
        stop_loss = float(row.get('StopLoss', 0))
        target = float(row.get('Target', 0))
        entry_time = row.get('Entry_Time', '')
        
        # Get current price
        current_price = get_current_price(symbol)
        
        if not current_price:
            print(f"⚠️  {symbol}: Could not fetch price")
            continue
        
        # Calculate P&L
        pnl = current_price - entry_price
        pnl_percent = (pnl / entry_price) * 100
        
        print(f"\n📊 {symbol}")
        print(f"   Entry: ₹{entry_price} @ {entry_time}")
        print(f"   Current: ₹{current_price} ({pnl_percent:+.2f}%)")
        print(f"   Stop: ₹{stop_loss} | Target: ₹{target}")
        
        # Check for exit conditions
        exit_status = None
        exit_reason = None
        
        # HIT STOP LOSS
        if current_price <= stop_loss:
            exit_status = "STOPPED OUT"
            exit_reason = f"Stop Loss Hit at ₹{current_price}"
            pnl_final = stop_loss - entry_price
            print(f"   🔴 STOP LOSS HIT!")
        
        # HIT TARGET
        elif current_price >= target:
            exit_status = "TARGET HIT"
            exit_reason = f"Target Hit at ₹{current_price}"
            pnl_final = target - entry_price
            print(f"   🟢 TARGET HIT!")
        
        # Still in trade
        else:
            # Calculate distance to stop/target
            to_stop = ((current_price - stop_loss) / entry_price) * 100
            to_target = ((target - current_price) / entry_price) * 100
            print(f"   Distance to Stop: {to_stop:.1f}% | To Target: {to_target:.1f}%")
            continue
        
        # EXIT TRADE
        if exit_status:
            try:
                # Update status and P&L
                alert_sheet.update_cell(row_num, 11, exit_status)              # K: Status
                alert_sheet.update_cell(row_num, 14, f"{pnl_final:.2f}")       # N: Profit/Loss
                
                # Send Telegram alert
                emoji = "🟢" if "TARGET" in exit_status else "🔴"
                msg = (
                    f"{emoji} <b>TRADE CLOSED</b>\n\n"
                    f"Symbol: {symbol}\n"
                    f"Entry: ₹{entry_price} @ {entry_time}\n"
                    f"Exit: ₹{current_price} @ {datetime.now().strftime('%H:%M')}\n"
                    f"Result: {exit_status}\n"
                    f"P&L: ₹{pnl_final:.2f} ({pnl_percent:+.2f}%)"
                )
                send_telegram(msg)
                
                exits_count += 1
                print(f"   ✅ Trade closed and logged")
                
            except Exception as e:
                print(f"   ❌ Error closing trade: {e}")
    
    print(f"\n{'='*50}")
    print(f"🏁 Exits Processed: {exits_count}")
    print(f"{'='*50}\n")
    
    return exits_count

def get_portfolio_summary():
    """Get current portfolio status"""
    
    records = alert_sheet.get_all_records()
    
    open_count = 0
    total_pnl = 0
    wins = 0
    losses = 0
    
    for row in records:
        status = str(row.get('Status', '')).strip()
        
        if status == "OPEN":
            open_count += 1
        elif status in ["TARGET HIT", "STOPPED OUT"]:
            pnl = float(row.get('Profit/Loss', 0))
            total_pnl += pnl
            if pnl > 0:
                wins += 1
            else:
                losses += 1
    
    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    print(f"\n{'='*50}")
    print(f"📈 PORTFOLIO SUMMARY")
    print(f"{'='*50}")
    print(f"Capital: ₹{TOTAL_CAPITAL:,}")
    print(f"Open Positions: {open_count}/{MAX_POSITIONS}")
    print(f"Closed Trades: {total_trades} (W:{wins} | L:{losses})")
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Total P&L: ₹{total_pnl:,.2f}")
    print(f"{'='*50}\n")

def main():
    """
    Main trading cycle:
    1. Enter new trades (if positions available)
    2. Monitor open positions
    3. Exit at stop/target
    """
    
    print(f"\n{'#'*50}")
    print(f"🤖 PROFESSIONAL TRADE MANAGER")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*50}")
    
    # Get current portfolio status
    get_portfolio_summary()
    
    # Step 1: Enter new trades
    new_entries = enter_new_trades()
    
    # Step 2: Monitor and exit open positions
    exits = monitor_open_positions()
    
    # Final summary
    if new_entries > 0 or exits > 0:
        get_portfolio_summary()
    else:
        print("ℹ️  No activity this cycle\n")

if __name__ == "__main__":
    main()
