import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
IST = pytz.timezone('Asia/Kolkata')
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT = os.environ.get('CHAT_ID')
SHEET_NAME = "Ai360tradingAlgo"

def send_tg(msg):
    if TG_TOKEN and TG_CHAT:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=15)

def to_f(val):
    try: return float(str(val).replace(',', '').replace('₹', '').replace('%', '').strip())
    except: return 0.0

def run_trading_cycle():
    now = datetime.now(IST)
    today_date = now.strftime('%Y-%m-%d')
    
    # 1. Google Sheets Connection
    creds_dict = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_JSON'))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    ss = gspread.authorize(creds).open(SHEET_NAME)
    sheet = ss.worksheet("AlertLog")

    # 2. Reset Memory (O4) at midnight to start fresh
    if now.hour == 0 and now.minute < 5:
        sheet.update_acell("O4", "")
        return

    # 3. Fetch Data & Current Memory
    rows = sheet.get_all_values()
    mem_val = str(sheet.acell("O4").value or "")
    active_trades = []
    
    # 4. Process TRADED Rows (2 to 10)
    # i is the spreadsheet row number (start=2)
    for i, row in enumerate(rows[1:10], start=2):
        if len(row) > 10 and "TRADED" in str(row[10]).upper():
            # Column Mapping: B=1(Sym), C=2(Curr_P), H=7(StopLoss), L=11(Entry_P)
            sym, curr_p, old_sl, entry_p = row[1], to_f(row[2]), to_f(row[7]), to_f(row[11])
            
            if entry_p == 0: continue
            pnl = ((curr_p - entry_p) / entry_p) * 100
            
            # --- PULLBACK-SAFE TSL LOGIC ---
            # Moves SL to 3.5% below current price to give "breathing room"
            calc_sl = round(curr_p * 0.965, 2)
            
            # Update only if New SL is significantly higher (0.5% jump)
            if calc_sl > (old_sl * 1.005):
                sheet.update_cell(i, 8, calc_sl)
                
                # Memory Check: Don't spam the same TSL update
                tsl_key = f"{sym}_TSL_{int(calc_sl)}"
                if tsl_key not in mem_val:
                    send_tg(f"🛡️ <b>TSL SHIFT: {sym}</b>\n━━━━━━━━━━━━━━━━━━━━\n🟢 <b>P/L:</b> {pnl:+.2f}%\n🆕 <b>New SL:</b> ₹{calc_sl}\n━━━━━━━━━━━━━━━━━━━━")
                    mem_val += f",{tsl_key}"

            # --- EXIT TRIGGER ---
            if curr_p <= old_sl and old_sl > 0:
                exit_key = f"{sym}_EXIT_{today_date}"
                if exit_key not in mem_val:
                    send_tg(f"🚨 <b>EXIT ALERT: {sym}</b>\n━━━━━━━━━━━━━━━━━━━━\n📉 <b>Final P/L:</b> {pnl:+.2f}%\n💰 <b>Exit Price:</b> ₹{curr_p}\n━━━━━━━━━━━━━━━━━━━━")
                    mem_val += f",{exit_key}"
            
            active_trades.append({'sym': sym, 'pnl': pnl})

    # 5. DAILY SCHEDULED MESSAGES (9:00 AM & 3:30 PM)
    # Morning Update
    if now.hour == 9 and f"{today_date}-AM" not in mem_val:
        send_tg(f"🌅 <b>GOOD MORNING</b>\n━━━━━━━━━━━━━━━━━━━━\n📈 <b>Active Trades:</b> {len(active_trades)}\n📅 <b>Date:</b> {today_date}\n━━━━━━━━━━━━━━━━━━━━")
        mem_val += f",{today_date}-AM"

    # Evening Performance Report
    if (now.hour == 15 and now.minute >= 30) and f"{today_date}-PM" not in mem_val:
        p_list = "".join([f"{'🟢' if t['pnl'] >= 0 else '🔴'} {t['sym']}: {t['pnl']:+.2f}%\n" for t in active_trades])
        send_tg(f"🏆 <b>MARKET CLOSE REPORT</b>\n━━━━━━━━━━━━━━━━━━━━\n{p_list if p_list else 'No active trades.'}\n━━━━━━━━━━━━━━━━━━━━")
        mem_val += f",{today_date}-PM"

    # 6. Save Memory (O4) & Heartbeat (O3)
    # Keep memory string manageable (last 30 entries)
    final_mem = ",".join(mem_val.split(",")[-30:])
    sheet.update_acell("O4", final_mem)
    sheet.update_acell("O3", f"Bot Active | {now.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    run_trading_cycle()
