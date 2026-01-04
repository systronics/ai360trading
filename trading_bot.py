import os
import gspread
import requests
from datetime import datetime
from google.oauth2.service_account import Credentials
from dhanhq import dhanhq

# --- 1. CONFIGURATION & TARGETS ---
PAPER_TRADING = True  # Set to False only when you want REAL trades
PROFIT_TARGET = 0.05  # Exit at 5% Profit
TRAILING_GAP = 0.02   # Trail by 2% (Protects gains if price drops slightly)
SHEET_NAME = "ai360trading_results" # Ensure this matches your filename
TAB_NAME = "AlertLog"

# --- 2. SETUP CONNECTIONS ---
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
creds = Credentials.from_service_account_info(eval(creds_json), scopes=scopes)
gc = gspread.authorize(creds)

# Dhan Connect (Ready for live phase)
dhan = dhanhq(os.environ.get('DHAN_CLIENT_ID'), os.environ.get('DHAN_API_KEY'))

# --- 3. EXECUTION ENGINE ---
sh = gc.open(SHEET_NAME)
sheet = sh.worksheet(TAB_NAME)
records = sheet.get_all_records()

print(f"🤖 Bot Pulse: {datetime.now().strftime('%H:%M:%S')}")

for i, row in enumerate(records):
    symbol = row.get('NSE_SYMBOL')
    action = row.get('FINAL_ACTION') # This reads your "🟢 STRONG BUY"
    live_price = float(row.get('CMP', 0))
    status = str(row.get('Status', ''))
    row_num = i + 2 # Header + 0-index offset

    # A. ENTRY LOGIC: Only for new "STRONG BUY" signals
    if action == "🟢 STRONG BUY" and status == "":
        print(f"🚀 Entry Triggered: {symbol} at ₹{live_price}")
        
        updates = [
            {'range': f'J{row_num}', 'values': [['TRADED (PAPER)']]},
            {'range': f'K{row_num}', 'values': [[live_price]]}, # Entry Price
            {'range': f'L{row_num}', 'values': [[datetime.now().strftime("%Y-%m-%d %H:%M")]]} # Time
        ]
        sheet.batch_update(updates)

    # B. EXIT LOGIC: Manage trades already marked as "TRADED"
    elif "TRADED" in status:
        entry_price = float(row.get('Entry_Price', 0))
        if entry_price == 0: continue
        
        current_pnl = (live_price - entry_price) / entry_price

        # Exit Condition: Target Reached (5%)
        if current_pnl >= PROFIT_TARGET:
            pnl_str = f"{current_pnl*100:.2f}%"
            sheet.update_cell(row_num, 10, "CLOSED (PROFIT)")
            sheet.update_cell(row_num, 13, pnl_str) # Writes to Profit/Loss Column
            print(f"💰 Target Hit: {symbol} closed at {pnl_str} profit!")
            
        # Optional: Stop Loss (e.g., -3% to protect capital)
        elif current_pnl <= -0.03:
            sheet.update_cell(row_num, 10, "CLOSED (STOP LOSS)")
            sheet.update_cell(row_num, 13, f"{current_pnl*100:.2f}%")
