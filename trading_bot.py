import os, gspread, requests, pandas as pd
from dhanhq import dhanhq

# --- CONFIG & RISK MANAGEMENT ---
LIVE_MODE = True  # Set to False to stop real trades instantly
TOTAL_CAPITAL = 50000
MAX_TRADES = 5
CAP_PER_TRADE = 10000 
TRAIL_PERCENT = 0.005 # 0.5% Trailing Stop Loss to stay in trend

# Initialize Dhan
dhan = dhanhq(os.environ.get('DHAN_CLIENT_ID'), os.environ.get('DHAN_API_KEY'))

def get_security_id(symbol):
    """Maps symbols like NSE:RELIANCE to Dhan numeric IDs"""
    clean_symbol = symbol.replace("NSE:", "").strip()
    try:
        url = "https://images.dhan.co/api-data/api-scrip-master.csv"
        df = pd.read_csv(url)
        match = df[df['SEM_SYMBOL_NAME'] == clean_symbol]
        return str(match.iloc[0]['SEM_SMST_SECURITY_ID']) if not match.empty else None
    except: return None

def run_trading_cycle():
    # ... (Standard Gspread login using your Secrets) ...
    sheet = client.open("Ai360tradingAlgo").worksheet("AlertLog")
    records = sheet.get_all_records()
    
    # 1. Count current Active Holdings
    active_count = sum(1 for r in records if "TRADED" in str(r.get('Status')))

    for i, row in enumerate(records):
        row_num = i + 2
        symbol = str(row.get('Symbol'))
        price = float(row.get('Live Price') or 0)
        status = str(row.get('Status', ''))
        entry_price = float(row.get('Entry Price') or 0)
        current_sl = float(row.get('StopLoss') or 0)

        # --- PATH A: NEW ENTRY (Real + Paper) ---
        if not status and symbol and active_count < MAX_TRADES:
            qty = int(CAP_PER_TRADE / price)
            sec_id = get_security_id(symbol)

            if LIVE_MODE and sec_id and qty > 0:
                try:
                    dhan.place_order(
                        security_id=sec_id, exchange_segment=dhan.NSE,
                        transaction_type=dhan.BUY, quantity=qty,
                        order_type=dhan.MARKET, product_type=dhan.CNC, tag='AlgoBot'
                    )
                except Exception as e: print(f"Dhan Error: {e}")

            # Update Sheet for Followers (Paper Trade Status)
            sheet.update_cell(row_num, 11, "TRADED (PAPER)")
            active_count += 1
            send_telegram(f"🚀 <b>NEW SIGNAL: {symbol}</b>\nQty: {qty} | Price: {price}")

        # --- PATH B: MONITOR & TRAIL STOPLOSS (Remaining in Trend) ---
        elif "TRADED" in status:
            # Trailing Stop Loss Logic: if price goes up, move SL up
            new_trailing_sl = round(price * (1 - TRAIL_PERCENT), 2)
            if new_trailing_sl > current_sl:
                sheet.update_cell(row_num, 8, new_trailing_sl) # Column H is StopLoss

            # Exit Logic
            if price <= current_sl:
                # Execute Real Sell if LIVE
                # ... dhan.place_order(transaction_type=dhan.SELL ...)
                sheet.update_cell(row_num, 11, "EXIT (SL/TRAIL)")
                send_telegram(f"📉 <b>EXIT: {symbol}</b>\nPrice: {price}")
