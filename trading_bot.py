import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
IST = pytz.timezone('Asia/Kolkata')
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT = os.environ.get('CHAT_ID')
SHEET_NAME = "Ai360tradingAlgo"

def send_tg(msg):
    """Sends a formatted message to Telegram."""
    if TG_TOKEN and TG_CHAT:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}
        try:
            requests.post(url, json=payload, timeout=15)
        except Exception as e:
            print(f"Telegram Error: {e}")

def to_f(val):
    """Converts sheet strings (₹1,200.50) to clean floats."""
    try:
        return float(str(val).replace(',', '').replace('₹', '').replace('%', '').strip())
    except:
        return 0.0

def run_trading_cycle():
    now = datetime.now(IST)
    today_date = now.strftime('%Y-%m-%d')
    
    # 1. Google Sheets Connection
    try:
        creds_dict = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_JSON'))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict, 
            ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(creds)
        ss = client.open(SHEET_NAME)
        sheet = ss.worksheet("AlertLog")
    except Exception as e:
        print(f"Connection Error: {e}")
        return

    # 2. Reset Memory (O4) at Midnight (IST)
    if now.hour == 0 and now.minute < 10:
        sheet.update_acell("O4", "")
        print("Memory Reset for new day.")
        return

    # 3. Fetch Data & Current Memory
    rows = sheet.get_all_values()
    mem_val = str(sheet.acell("O4").value or "")
    active_trades = []
    
    # 4. Process TRADED Rows (Rows 2 to 10 in Sheet)
    # Loop through indices 1 to 9 (corresponds to Sheet Rows 2-10)
    for i, row in enumerate(rows[1:10], start=2):
        if len(row) > 10 and "TRADED" in str(row[10]).upper():
            # Mapping: B=1(Sym), C=2(Price), H=7(SL), L=11(Entry)
            sym = row[1]
            curr_p = to_f(row[2])
            old_sl = to_f(row[7])
            entry_p = to_f(row[11])
            
            if entry_p <= 0 or curr_p <= 0: continue
            
            pnl = ((curr_p - entry_p) / entry_p) * 100
            
            # --- PULLBACK-SAFE TSL LOGIC ---
            # Calculates a 3.5% trailing stop (Bullish Move Support)
            calc_sl = round(curr_p * 0.965, 2)
            
            # Update only if New SL is higher by > 0.5% (Prevents API over-usage)
            if calc_sl > (old_sl * 1.005):
                sheet.update_cell(i, 8, calc_sl) # Update Column H
                
                # Check memory to prevent duplicate Telegram alerts for same shift
                tsl_key = f"{sym}_TSL_{int(calc_sl)}"
                if tsl_key not in mem_val:
                    send_tg(f"🛡️ <b>TSL SHIFT: {sym}</b>\n━━━━━━━━━━━━━━━━━━━━\n🟢 <b>P/L:</b> {pnl:+.2f}%\n🆕 <b>New SL:</b> ₹{calc_sl}\n━━━━━━━━━━━━━━━━━━━━")
                    mem_val += f",{tsl_key}"

            # --- EXIT TRIGGER ---
            if curr_p <= old_sl and old_sl > 0:
                exit_key = f"{sym}_EXIT_{today_date}"
                if exit_key not in mem_val:
                    send_tg(f"🚨 <b>EXIT ALERT: {sym}</b>\n━━━━━━━━━━━━━━━━━━━━\n📉 <b>Final P/L:</b> {pnl:+.2f}%\n💰 <b>Price:</b> ₹{curr_p}\n━━━━━━━━━━━━━━━━━━━━")
                    mem_val += f",{exit_key}"
            
            active_trades.append({'sym': sym, 'pnl': pnl})

    # 5. DAILY UPDATES (9:00 AM & 3:30 PM)
    if now.hour == 9 and f"{today_date}-AM" not in mem_val:
        send_tg(f"🌅 <b>GOOD MORNING</b>\n━━━━━━━━━━━━━━━━━━━━\n📈 <b>Active Trades:</b> {len(active_trades)}\n━━━━━━━━━━━━━━━━━━━━")
        mem_val += f",{today_date}-AM"

    if (now.hour == 15 and now.minute >= 30) and f"{today_date}-PM" not in mem_val:
        p_list = "".join([f"{'🟢' if t['pnl'] >= 0 else '🔴'} {t['sym']}: {t['pnl']:+.2f}%\n" for t in active_trades])
        send_tg(f"🏆 <b>MARKET CLOSE REPORT</b>\n━━━━━━━━━━━━━━━━━━━━\n{p_list if p_list else 'No active trades.'}\n━━━━━━━━━━━━━━━━━━━━")
        mem_val += f",{today_date}-PM"

    # 6. BATCH UPDATE: Save Memory (O4) & Heartbeat (O3)
    final_mem = ",".join(mem_val.split(",")[-25:]) # Keep last 25 events to stay under cell limit
    heartbeat = f"Bot Active | {now.strftime('%H:%M:%S')}"
    
    # Batch update to save quota
    sheet.update([ [heartbeat], [final_mem] ], "O3:O4")

if __name__ == "__main__":
    run_trading_cycle()
