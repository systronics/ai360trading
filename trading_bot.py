import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

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
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_JSON')), ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    sheet = gspread.authorize(creds).open(SHEET_NAME).worksheet("AlertLog")

    if now.hour == 0 and now.minute < 10:
        sheet.update_acell("O4", ""); return

    rows = sheet.get_all_values()
    mem_val = str(sheet.acell("O4").value or "")
    active_trades = []
    
    # Process Row 2 to 10
    for i, row in enumerate(rows[1:10], start=2):
        if len(row) > 10 and "TRADED" in str(row[10]).upper():
            # Mapping: B=1(Sym), C=2(Price), H=7(SL), I=8(Target), L=11(Entry)
            sym, curr_p, old_sl, target_p, entry_p = row[1], to_f(row[2]), to_f(row[7]), to_f(row[8]), to_f(row[11])
            
            # --- CRITICAL SAFETY FIX: Prevents Ghost Exits at ₹0 ---
            if curr_p <= 0 or entry_p <= 0: 
                continue 
            
            pnl = ((curr_p - entry_p) / entry_p) * 100
            calc_sl = round(curr_p * 0.965, 2)
            
            # --- 1% SPAM FILTER ---
            if calc_sl > (old_sl * 1.01):
                sheet.update_cell(i, 8, calc_sl)
                tsl_key = f"{sym}_TSL_{int(calc_sl)}"
                if tsl_key not in mem_val:
                    # Clean format: No long lines
                    send_tg(f"🛡️ <b>TSL: {sym}</b>\n📈 <b>P/L:</b> {pnl:+.2f}%\n🆕 <b>SL:</b> ₹{calc_sl}\n🎯 <b>Tgt:</b> ₹{target_p}")
                    mem_val += f",{tsl_key}"

            # Real Exit Logic (only triggers if price is actually valid)
            if curr_p <= old_sl and old_sl > 0:
                exit_key = f"{sym}_EXIT_{today_date}"
                if exit_key not in mem_val:
                    send_tg(f"🚨 <b>EXIT: {sym}</b>\n📉 <b>Final P/L:</b> {pnl:+.2f}%\n💰 <b>Price:</b> ₹{curr_p}")
                    mem_val += f",{exit_key}"
            
            active_trades.append({'sym': sym, 'pnl': pnl})

    # Morning & Evening Reports
    if now.hour == 9 and f"{today_date}-AM" not in mem_val:
        send_tg(f"🌅 <b>9AM START</b>\n📈 <b>Active:</b> {len(active_trades)} stocks"); mem_val += f",{today_date}-AM"

    if (now.hour == 15 and now.minute >= 30) and f"{today_date}-PM" not in mem_val:
        p_list = "".join([f"{'🟢' if t['pnl'] >= 0 else '🔴'} {t['sym']}: {t['pnl']:+.2f}%\n" for t in active_trades])
        send_tg(f"🏆 <b>CLOSE REPORT</b>\n{p_list if p_list else 'No trades.'}"); mem_val += f",{today_date}-PM"

    # Save O3 & O4
    sheet.update([[f"Live | {now.strftime('%H:%M')}"], [",".join(mem_val.split(",")[-25:])]], "O3:O4")

if __name__ == "__main__":
    run_trading_cycle()
