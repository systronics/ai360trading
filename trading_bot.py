import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

IST = pytz.timezone('Asia/Kolkata')
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT = os.environ.get('CHAT_ID')

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
    ss = gspread.authorize(creds).open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")

    if now.hour == 0:
        sheet.update_acell("O3", ""); return

    rows = sheet.get_all_values()
    active_trades = []
    
    # Rows 2-10 are Traded Positions
    for i, row in enumerate(rows[1:10], start=2):
        if len(row) > 10 and "TRADED" in str(row[10]).upper():
            sym, curr_p, old_sl, entry_p = row[1], to_f(row[2]), to_f(row[7]), to_f(row[11])
            pnl = ((curr_p - entry_p) / entry_p) * 100 if entry_p > 0 else 0
            
            # TSL Update logic for Col H (Min StopLoss)
            calc_sl = round(curr_p * 0.965, 2)
            if calc_sl > (old_sl * 1.005):
                sheet.update_cell(i, 8, calc_sl)
                send_tg(f"🛡️ <b>TSL SHIFT: {sym}</b>\n━━━━━━━━━━━━━━━━━━━━\n🟢 <b>P/L:</b> {pnl:+.2f}%\n🆕 <b>New SL:</b> ₹{calc_sl}\n━━━━━━━━━━━━━━━━━━━━")
            
            if curr_p <= old_sl:
                send_tg(f"🚨 <b>EXIT ALERT: {sym}</b>\n━━━━━━━━━━━━━━━━━━━━\n📉 <b>Final P/L:</b> {pnl:+.2f}%\n━━━━━━━━━━━━━━━━━━━━")
            active_trades.append({'sym': sym, 'pnl': pnl})

    # Memory check in O3
    sent_status = str(sheet.acell("O3").value).strip()
    if now.hour == 9 and sent_status != f"{today_date}-AM":
        send_tg(f"🌅 <b>MORNING UPDATE</b>\n━━━━━━━━━━━━━━━━━━━━\n📈 <b>Active Trades:</b> {len(active_trades)}\n━━━━━━━━━━━━━━━━━━━━")
        sheet.update_acell("O3", f"{today_date}-AM")

    if (now.hour == 15 and now.minute >= 30) and sent_status != f"{today_date}-PM":
        p_list = "".join([f"{'🟢' if t['pnl'] >= 0 else '🔴'} {t['sym']}: {t['pnl']:+.2f}%\n" for t in active_trades])
        send_tg(f"🏆 <b>DAILY PERFORMANCE</b>\n━━━━━━━━━━━━━━━━━━━━\n{p_list if p_list else 'No trades.'}\n━━━━━━━━━━━━━━━━━━━━")
        sheet.update_acell("O3", f"{today_date}-PM")

if __name__ == "__main__":
    run_trading_cycle()
