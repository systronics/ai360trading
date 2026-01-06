import os, gspread, requests, pandas as pd
from dhanhq import dhanhq

# --- AUTOMATION CONFIG ---
LIVE_MODE = True  
TOTAL_CAPITAL = 50000
CAP_PER_TRADE = 10000 
MAX_TRADES = 5
TRAIL_PCT = 0.005 # 0.5% Trailing Stop Loss

# Initialize Dhan API
dhan = dhanhq(os.environ.get('DHAN_CLIENT_ID'), os.environ.get('DHAN_API_KEY'))

def get_sec_id(symbol):
    """Automatically maps NSE Symbol to Dhan Security ID"""
    try:
        url = "https://images.dhan.co/api-data/api-scrip-master.csv"
        df = pd.read_csv(url)
        # Dhan expects numeric IDs for order placement
        match = df[df['SEM_SYMBOL_NAME'] == symbol.replace("NSE:", "")]
        return str(match.iloc[0]['SEM_SMST_SECURITY_ID']) if not match.empty else None
    except: return None

def run_trading_cycle():
    # ... (Gspread login) ...
    records = log_sheet.get_all_records()
    active_count = sum(1 for r in records if "TRADED" in str(r.get('Status')))

    for i, row in enumerate(records):
        row_num = i + 2
        symbol = str(row.get('Symbol'))
        price = float(row.get('Live Price') or 0)
        status = str(row.get('Status', ''))
        current_sl = float(row.get('StopLoss') or 0)

        # --- AUTOMATED ENTRY ---
        if not status and symbol and active_count < MAX_TRADES:
            qty = int(CAP_PER_TRADE / price)
            sec_id = get_sec_id(symbol)

            if LIVE_MODE and sec_id:
                try:
                    # REAL TRADE (Your Account)
                    dhan.place_order(security_id=sec_id, exchange_segment=dhan.NSE,
                        transaction_type=dhan.BUY, quantity=qty,
                        order_type=dhan.MARKET, product_type=dhan.CNC)
                except Exception as e: print(f"Dhan Error: {e}")

            # PAPER TRADE (Followers/Website)
            log_sheet.update_cell(row_num, 11, "TRADED (PAPER)")
            active_count += 1
            send_telegram(f"🚀 NEW TRADE: {symbol} | Qty: {qty}")

        # --- AUTOMATED EXIT & TRAILING ---
        elif "TRADED" in status:
            # Trailing SL: Move SL up if price rises to stay in trend
            new_sl = round(price * (1 - TRAIL_PCT), 2)
            if new_sl > current_sl:
                log_sheet.update_cell(row_num, 8, new_sl) # Updates Column H

            # Exit if Stop Loss is hit
            if price <= current_sl:
                if LIVE_MODE:
                    # REAL SELL (Your Account)
                    dhan.place_order(security_id=get_sec_id(symbol), transaction_type=dhan.SELL, 
                                     quantity=qty, order_type=dhan.MARKET, product_type=dhan.CNC)
                
                log_sheet.update_cell(row_num, 11, "EXIT (SL HIT)")
                send_telegram(f"📉 EXIT: {symbol} at {price}")
