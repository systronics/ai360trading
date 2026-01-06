import os, gspread, requests, pandas as pd
from dhanhq import dhanhq

# --- CONFIG ---
LIVE_MODE = True  
TOTAL_CAPITAL = 50000
MAX_TRADES = 5
CAP_PER_TRADE = 10000 
TRAIL_PCT = 0.005 # 0.5% Trailing Stop Loss

# Initialize Dhan API using your Secrets
dhan = dhanhq(os.environ.get('DHAN_CLIENT_ID'), os.environ.get('DHAN_API_KEY'))

def get_sec_id(symbol):
    """Maps NSE Symbol to Dhan Security ID"""
    try:
        url = "https://images.dhan.co/api-data/api-scrip-master.csv"
        df = pd.read_csv(url)
        clean_symbol = symbol.replace("NSE:", "").strip()
        match = df[df['SEM_SYMBOL_NAME'] == clean_symbol]
        return str(match.iloc[0]['SEM_SMST_SECURITY_ID']) if not match.empty else None
    except: return None

def run_trading_cycle():
    # ... (Gspread login) ...
    records = log_sheet.get_all_records()
    
    # 1. Count rows marked 'TRADED' that haven't 'EXITED' yet
    active_holdings = [r for r in records if "TRADED" in str(r.get('Status')) and "EXIT" not in str(r.get('Status'))]
    active_count = len(active_holdings)

    for i, row in enumerate(records):
        row_num = i + 2
        symbol = str(row.get('Symbol'))
        price = float(row.get('Live Price') or 0)
        status = str(row.get('Status', ''))
        entry_price = float(row.get('Entry Price') or 0)
        target = float(row.get('Target') or 0)
        stop_loss = float(row.get('StopLoss') or 0)

        # --- NEW ENTRY (Automation Step 1) ---
        if not status and symbol and active_count < MAX_TRADES:
            qty = int(CAP_PER_TRADE / price)
            sec_id = get_sec_id(symbol)

            if LIVE_MODE and sec_id:
                try:
                    # CNC allows holding for multiple days
                    dhan.place_order(security_id=sec_id, exchange_segment=dhan.NSE,
                        transaction_type=dhan.BUY, quantity=qty,
                        order_type=dhan.MARKET, product_type=dhan.CNC)
                    print(f"REAL BUY: {symbol} Qty {qty}")
                except Exception as e: print(f"Dhan Error: {e}")

            log_sheet.update_cell(row_num, 11, "TRADED (PAPER)")
            active_count += 1

        # --- MONITORING & MULTI-DAY HOLD (Automation Step 2) ---
        elif "TRADED" in status and "EXIT" not in status:
            # Trailing Stop Loss: Lock in profits if price rises
            new_sl = round(price * (1 - TRAIL_PCT), 2)
            if new_sl > stop_loss:
                log_sheet.update_cell(row_num, 8, new_sl) # Updates Column H

            # Exit Condition (Target or Stop Loss hit)
            if price >= target or price <= stop_loss:
                if LIVE_MODE:
                    # REAL SELL
                    dhan.place_order(security_id=get_sec_id(symbol), transaction_type=dhan.SELL, 
                                     quantity=int(CAP_PER_TRADE/entry_price), 
                                     order_type=dhan.MARKET, product_type=dhan.CNC)
                
                exit_type = "TARGET ✅" if price >= target else "SL/TRAIL ❌"
                log_sheet.update_cell(row_num, 11, f"EXIT ({exit_type})")
                send_telegram(f"💰 <b>EXIT: {symbol}</b>\nPrice: {price}\nResult: {exit_type}")
