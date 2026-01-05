import os
import gspread
import json
from datetime import datetime
from google.oauth2.service_account import Credentials

# --- CONFIG ---
SHEET_NAME = "Ai360tradingAlgo"
LOG_SHEET = "AlertLog"
MAX_NEW_TRADES = 5  # Limit daily risk

# --- SETUP ---
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')

# Safety check for the Service Account JSON
if not creds_json:
    print("❌ ERROR: GCP_SERVICE_ACCOUNT_JSON not found in secrets!")
    exit()

creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open(SHEET_NAME)
log_sheet = sh.worksheet(LOG_SHEET)

def run_trading_cycle():
    # 1. Fetch all records from AlertLog
    records = log_sheet.get_all_records()
    new_trades_count = 0
    
    print(f"🤖 Bot Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 2. Iterate through records to find new signals
    for i, row in enumerate(records):
        row_num = i + 2  # Account for Header row
        
        symbol = row.get('Symbol')
        live_price = row.get('Price')
        status = str(row.get('Status', '')).strip()

        # ENTRY LOGIC: Only trade if Status is empty and a Symbol exists
        if not status and symbol:
            if new_trades_count < MAX_NEW_TRADES:
                print(f"🚀 SIGNAL DETECTED: {symbol} at ₹{live_price}")
                
                # --- DHAN API EXECUTION START ---
                # You can add your dhan.place_order() logic here
                # For now, we are marking it as TRADED (PAPER)
                # --- DHAN API EXECUTION END ---

                # 3. LOCK THE TRADE IN THE SHEET
                # Column 11 (K): Status
                # Column 12 (L): Entry_Price
                # Column 13 (M): Entry_Time
                
                try:
                    # Update status first to signal Apps Script to LOCK the row
                    log_sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                    log_sheet.update_cell(row_num, 12, live_price)
                    log_sheet.update_cell(row_num, 13, datetime.now().strftime("%H:%M:%S"))
                    
                    print(f"✅ Trade Locked for {symbol} at {live_price}")
                    new_trades_count += 1
                except Exception as e:
                    print(f"❌ Error updating sheet for {symbol}: {e}")
            else:
                print(f"⏭️ Daily Limit Reached: Skipping {symbol}")

    if new_trades_count == 0:
        print("😴 No new signals to trade at this time.")

if __name__ == "__main__":
    run_trading_cycle()
