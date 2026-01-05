import os
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# --- CONFIG ---
SHEET_NAME = "Ai360tradingAlgo"
MAX_NEW_TRADES = 5    # Top 5 Limit

# --- SETUP ---
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
creds = Credentials.from_service_account_info(eval(creds_json), scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open(SHEET_NAME)
sheet = sh.worksheet('AlertLog')

def run_trading_cycle():
    # Fetch all records from AlertLog
    records = sheet.get_all_records()
    new_trades_count = 0
    
    print(f"🤖 Bot Started: {datetime.now().strftime('%H:%M')}")
    for i, row in enumerate(records):
        row_num = i + 2 # Account for Header
        
        # Mapping to your Apps Script Columns:
        symbol = row.get('Symbol')
        live_price = row.get('Price')
        status = str(row.get('Status', '')).strip()
        
        # ENTRY LOGIC: Only trade if Status is empty and Symbol exists
        if status == "" and symbol != "":
            if new_trades_count < MAX_NEW_TRADES:
                print(f"✅ Executing Trade: {symbol} at {live_price}")
                
                # UPDATED COLUMN POSITIONS (after adding Breakout_Stage in Column G):
                # Column K (11): Status
                # Column L (12): Entry_Price
                # Column M (13): Entry_Time
                sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                sheet.update_cell(row_num, 12, live_price)
                sheet.update_cell(row_num, 13, datetime.now().strftime("%H:%M"))
                
                new_trades_count += 1
            else:
                print(f"⏭️ Limit Reached: Skipping {symbol}")

if __name__ == "__main__":
    run_trading_cycle()
