import os, gspread, requests, pandas as pd
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
    """Maps NSE Symbol to Dhan Security ID for real trades"""
    try:
        url = "https://images.dhan.co/api-data/api-scrip-master.csv"
        df = pd.read_csv(url)
        clean_symbol = symbol.replace("NSE:", "").strip()
        match = df[df['SEM_SYMBOL_NAME'] == clean_symbol]
        return str(match.iloc[0]['SEM_SMST_SECURITY_ID']) if not match.empty else None
    except: return None

def run_trading_cycle():
    # ... (Gspread login logic using os.environ.get('GCP_SERVICE_ACCOUNT_JSON')) ...
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

        # --- AUTOMATED ENTRY (FOR NEW SIGNALS) ---
        if not status and symbol and active_count < MAX_TRADES:
            qty = int(CAP_PER_TRADE / price)
            sec_id = get_sec_id(symbol)

            if LIVE_MODE and sec_id and qty > 0:
                try:
                    # CNC allows holding for multiple days (Swing)
                    dhan.place_order(security_id=sec_id, exchange_segment=dhan.NSE,
                        transaction_type=dhan.BUY, quantity=qty,
                        order_type=dhan.MARKET, product_type=dhan.CNC)
                    print(f"REAL BUY: {symbol} Qty {qty}")
                except Exception as e: print(f"Dhan Error: {e}")

            # Mark status for followers/website
            sheet.update_cell(row_num, 11, "TRADED (PAPER)")
            active_count += 1

        # --- AUTOMATED MONITORING & EXIT (FOR ACTIVE TRADES) ---
        elif "TRADED" in status and "EXIT" not in status:
            # Trailing Stop Loss: Locked trend following
            new_sl = round(price * (1 - TRAIL_PCT), 2)
            if new_sl > stop_loss:
                sheet.update_cell(row_num, 8, new_sl) # Updates Column H

            # Exit Condition check (Target or Stop Loss/Trailing SL)
            if price >= target or price <= stop_loss:
                if LIVE_MODE:
                    # REAL SELL
                    dhan.place_order(security_id=get_sec_id(symbol), transaction_type=dhan.SELL, 
                                     quantity=qty, order_type=dhan.MARKET, product_type=dhan.CNC)
                
                exit_type = "TARGET ✅" if price >= target else "SL/TRAIL ❌"
                sheet.update_cell(row_num, 11, f"EXIT ({exit_type})")
                send_telegram(f"💰 <b>EXIT: {symbol}</b>\nPrice: {price}\nResult: {exit_type}")
