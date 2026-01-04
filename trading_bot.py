import os
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# --- CONFIG ---
SHEET_NAME = "Ai360tradingAlgo"
PROFIT_TARGET = 0.05  # 5% Profit
STOP_LOSS = -0.03     # 3% Loss
MAX_NEW_TRADES = 5    # Strict Limit

# --- SETUP ---
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
# Ensure your GitHub Secret 'GCP_SERVICE_ACCOUNT_JSON' is correctly set
creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
creds = Credentials.from_service_account_info(eval(creds_json), scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open(SHEET_NAME)
sheet = sh.worksheet('AlertLog')

def run_trading_cycle():
    records = sheet.get_all_records()
    new_trades_count = 0
    
    print(f"🤖 Bot Cycle Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    for i, row in enumerate(records):
        row_num = i + 2 # Accounting for header and 0-indexing
        symbol = row.get('Symbol')
        live_price = float(row.get('Price', 0))
        status = str(row.get('Status', ''))
        
        # 1. ENTRY LOGIC (Top 5 Only)
        # If Status is blank, it's a fresh signal from the Apps Script Top 10
        if status == "" and symbol != "":
            if new_trades_count < MAX_NEW_TRADES:
                print(f"🚀 Entering Top 5 Trade: {symbol} @ {live_price}")
                
                # Update J: Status, K: Entry Price, L: Entry Time
                sheet.update_cell(row_num, 10, "TRADED (PAPER)")
                sheet.update_cell(row_num, 11, live_price)
                sheet.update_cell(row_num, 12, datetime.now().strftime("%H:%M"))
                new_trades_count += 1
            else:
                print(f"⏭️ Limit Reached: Skipping {symbol}")

        # 2. EXIT LOGIC (Always monitors open trades)
        elif status == "TRADED (PAPER)":
            entry_price = float(row.get('Entry_Price', 0))
            if entry_price == 0: continue
            
            pnl_pct = (live_price - entry_price) / entry_price

            if pnl_pct >= PROFIT_TARGET:
                print(f"💰 Target Hit: {symbol} (+{pnl_pct*100:.2f}%)")
                sheet.update_cell(row_num, 10, "CLOSED (PROFIT)")
                sheet.update_cell(row_num, 13, f"{pnl_pct*100:.2f}%")
            
            elif pnl_pct <= STOP_LOSS:
                print(f"🛑 Stop Loss Hit: {symbol} ({pnl_pct*100:.2f}%)")
                sheet.update_cell(row_num, 10, "CLOSED (STOP LOSS)")
                sheet.update_cell(row_num, 13, f"{pnl_pct*100:.2f}%")

if __name__ == "__main__":
    run_trading_cycle()
