import os
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# --- CONFIG ---
SHEET_NAME = "Ai360tradingAlgo"
MAX_NEW_TRADES = 5    # Your Strict Top 5 Limit

# --- SETUP ---
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
creds = Credentials.from_service_account_info(eval(creds_json), scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open(SHEET_NAME)
sheet = sh.worksheet('AlertLog')

def run_trading_cycle():
    # Fetch all 10 records from your updated AlertLog
    records = sheet.get_all_records()
    new_trades_count = 0
    
    print(f"🤖 Bot Started: {datetime.now().strftime('%H:%M')}")

    for i, row in enumerate(records):
        row_num = i + 2 # Header is Row 1
        symbol = row.get('Symbol')
        live_price = row.get('Price')
        status = str(row.get('Status', ''))
        
        # ENTRY LOGIC: Only trade if Status is empty
        if status == "" and symbol != "":
            if new_trades_count < MAX_NEW_TRADES:
                print(f"✅ Executing Trade {new_trades_count+1}: {symbol}")
                
                # Update J: Status, K: Entry_Price, L: Entry_Time
                sheet.update_cell(row_num, 10, "TRADED (PAPER)")
                sheet.update_cell(row_num, 11, live_price)
                sheet.update_cell(row_num, 12, datetime.now().strftime("%H:%M"))
                
                new_trades_count += 1
            else:
                # This ensures stocks 6-10 are skipped
                print(f"⏭️ Limit Reached: {symbol} is ranked > 5. Skipping.")

if __name__ == "__main__":
    run_trading_cycle()
