import os
import json
import gspread
import requests
import pandas as pd
from dhanhq import dhanhq
from google.oauth2.service_account import Credentials

# CONFIGURATION
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fPNGL6AHs-7M-oC22zILg9FlyWi-7DF9NoVVqZQs2vk/edit"
TELEGRAM_CHAT_ID = "-1001904635185" # e.g., @ai360trading or -100123456789 

def send_telegram(msg):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token:
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={msg}"
        requests.get(url)

def start_algo():
    print("🤖 Algo Bot Started...")

    # --- 2. CONNECT TO GOOGLE SHEETS ---
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # Reads the JSON secret you saved in GitHub
        secret_json = os.getenv('GCP_SERVICE_ACCOUNT_JSON')
        if not secret_json:
            raise Exception("GCP_SERVICE_ACCOUNT_JSON Secret is missing!")
            
        creds_dict = json.loads(secret_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_url(SHEET_URL).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        print("✅ Connected to Google Sheet.")
    except Exception as e:
        print(f"❌ Error connecting to Sheet: {e}")
        return

    # --- 3. CONNECT TO DHAN ---
    try:
        client_id = os.getenv('DHAN_CLIENT_ID')
        api_key = os.getenv('DHAN_API_KEY')
        # Use API Key as the access token in the latest SDK logic
        dhan = dhanhq(client_id, api_key)
        print("✅ Connected to Dhan API.")
    except Exception as e:
        print(f"❌ Error connecting to Dhan: {e}")
        return

    # --- 4. CHECK SIGNALS & EXECUTE ---
    # We look for rows where Signal is 'BULLISH' and Status is 'PENDING'
    for index, row in df.iterrows():
        signal = str(row.get('Signal', '')).upper()
        status = str(row.get('Status', '')).upper()

        if signal == 'BULLISH' and status == 'PENDING':
            stock_name = row.get('Stock', 'Unknown')
            price = row.get('Price', '0')
            sec_id = str(row.get('SecurityID', '')) # Ensure your sheet has this column!

            print(f"🚀 Signal Found for {stock_name}!")

            # A. Send Alert to Telegram
            msg = f"🟢 *ALGO BUY SIGNAL*\nStock: {stock_name}\nPrice: {price}"
            send_telegram(msg)

            # B. Place Order on Dhan (PAPER TRADE by default - comment out to go live)
            # To go live, uncomment the block below:
            """
            dhan.place_order(
                security_id=sec_id,
                exchange_segment=dhan.NSE,
                transaction_type=dhan.BUY,
                quantity=1,
                order_type=dhan.MARKET,
                product_type=dhan.INTRA
            )
            """

            # C. Update Sheet to 'TRADED' so it doesn't repeat
            # Sheet rows are 1-indexed, and index 0 is row 2 (header is 1)
            try:
                # Find the column number for 'Status'
                status_col_idx = list(df.columns).index('Status') + 1
                sheet.update_cell(index + 2, status_col_idx, "TRADED")
                print(f"✅ {stock_name} marked as TRADED in Sheet.")
            except Exception as e:
                print(f"⚠️ Could not update Sheet status: {e}")

    # --- 5. EXPORT FOR WEBSITE ---
    # Create the live_signals.json file for your website to display
    with open("live_signals.json", "w") as f:
        json.dump(data, f)
    print("✅ live_signals.json updated for website.")

if __name__ == "__main__":
    start_algo()
