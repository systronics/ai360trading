import os, gspread, requests
import pandas as pd
from dhanhq import dhanhq

# --- AUTOMATION CONFIG ---
LIVE_MODE = True  
TOTAL_CAPITAL = 50000
MAX_TRADES = 5
CAP_PER_TRADE = 10000 
TRAIL_PCT = 0.005 # 0.5% Trailing Stop Loss

# Initialize Dhan API using your Secrets
dhan = dhanhq(os.environ.get('DHAN_CLIENT_ID'), os.environ.get('DHAN_API_KEY'))

def get_sec_id(symbol):
    """Maps 'NSE:HINDALCO' to Dhan Security ID automatically"""
    try:
        url = "https://images.dhan.co/api-data/api-scrip-master.csv"
        df = pd.read_csv(url)
        
        # CLEANING STEP: Convert 'NSE:HINDALCO' -> 'HINDALCO-EQ'
        clean_symbol = symbol.split(":")[-1].strip()
        dhan_target = f"{clean_symbol}-EQ"
        
        # Match against SEM_TRADING_SYMBOL column
        match = df[df['SEM_TRADING_SYMBOL'] == dhan_target]
        
        if not match.empty:
            return str(match.iloc[0]['SEM_SMST_SECURITY_ID'])
        return None
    except Exception as e:
        print(f"Error fetching Security ID: {e}")
        return None

def run_trading_cycle():
    # ... (Your Gspread login logic here) ...
    sheet = client.open("Ai360tradingAlgo").worksheet("AlertLog")
    records = sheet.get_all_records()
    
    # 1. Identify active holdings to manage the 5-slot limit
    active_holdings = [r for r in records if "TRADED" in str(r.get('Status')) and "EXIT" not in str(r.get('Status'))]
    active_count = len(active_holdings)

    for i, row in enumerate(records):
        row_num = i + 2
        symbol = str(row.get('Symbol'))
        price = float(row.get('Live Price') or row.get('Price', 0))
        status = str(row.get('Status', ''))
        target = float(row.get('Target') or 0)
        stop_loss = float(row.get('StopLoss') or 0)

        # --- AUTOMATED ENTRY ---
        if not status and symbol and active_count < MAX_TRADES:
            qty = int(CAP_PER_TRADE / price) if price > 0 else 0
            sec_id = get_sec_id(symbol)

            if LIVE_MODE and sec_id and qty > 0:
                try:
                    # Place Real Order
                    order = dhan.place_order(
                        security_id=sec_id, 
                        exchange_segment=dhan.NSE,
                        transaction_type=dhan.BUY, 
                        quantity=qty,
                        order_type=dhan.MARKET, 
                        product_type=dhan.CNC
                    )
                    print(f"✅ REAL BUY: {symbol} | ID: {sec_id} | Qty {qty}")
                    sheet.update_cell(row_num, 11, "TRADED (LIVE)")
                except Exception as e: 
                    print(f"❌ Dhan Buy Error: {e}")
            else:
                # Paper trade if Live Mode is off or setup fails
                sheet.update_cell(row_num, 11, "TRADED (PAPER)")
            
            active_count += 1

        # --- AUTOMATED MONITORING & EXIT ---
        elif "TRADED" in status and "EXIT" not in status:
            # Trailing Stop Loss logic
            new_sl = round(price * (1 - TRAIL_PCT), 2)
            if new_sl > stop_loss:
                sheet.update_cell(row_num, 8, new_sl) 

            # Exit Condition check
            if price >= target or (stop_loss > 0 and price <= stop_loss):
                if LIVE_MODE:
                    sec_id = get_sec_id(symbol)
                    try:
                        # REAL SELL (We use the same qty as entry)
                        qty = int(CAP_PER_TRADE / price) 
                        dhan.place_order(
                            security_id=sec_id, 
                            exchange_segment=dhan.NSE,
                            transaction_type=dhan.SELL, 
                            quantity=qty, 
                            order_type=dhan.MARKET, 
                            product_type=dhan.CNC
                        )
                        print(f"✅ REAL EXIT: {symbol}")
                    except Exception as e:
                        print(f"❌ Dhan Sell Error: {e}")
                
                exit_type = "TARGET ✅" if price >= target else "SL/TRAIL ❌"
                sheet.update_cell(row_num, 11, f"EXIT ({exit_type})")
