import os
import gspread
import pandas as pd
from dhanhq import dhanhq
from oauth2client.service_account import ServiceAccountCredentials
import requests

# CONFIGURATION
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fPNGL6AHs-7M-oC22zILg9FlyWi-7DF9NoVVqZQs2vk/edit"
TELEGRAM_CHAT_ID = "-1001904635185" # e.g., @ai360trading or -100123456789

def send_telegram(msg):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={msg}"
    requests.get(url)

def start_algo():
    # 1. Access Google Sheet
    # Note: You still need to upload your credentials.json from Google Cloud!
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(SHEET_URL).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
    except Exception as e:
        print(f"Error reading sheet: {e}")
        return

    # 2. Setup Dhan (Manual Token for now to keep it simple)
    # Note: Since your token is 24h, we will use the API Key/Secret logic soon.
    dhan = dhanhq(os.getenv('DHAN_CLIENT_ID'), os.getenv('DHAN_API_KEY'))

    # 3. Look for Bullish Signals
    for index, row in df.iterrows():
        if row.get('Signal') == 'BULLISH' and row.get('Status') == 'PENDING':
            stock = row['Stock']
            msg = f"⚡ NEW ALGO TRADE: Buy {stock} at {row['Price']}"
            
            # Send to Telegram
            send_telegram(msg)
            
            # --- PAPER TRADING --- 
            # (Remove the # below to make it real trade when ready)
            # dhan.place_order(securityId=str(row['ID']), exchangeSegment=dhan.NSE, 
            #                  transactionType=dhan.BUY, quantity=1, 
            #                  orderType=dhan.MARKET, productType=dhan.INTRADAY)

            # Update Sheet to avoid double trades
            sheet.update_cell(index + 2, list(df.columns).index('Status') + 1, "TRADED")

if __name__ == "__main__":
    start_algo()
