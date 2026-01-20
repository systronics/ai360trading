import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

IST = pytz.timezone('Asia/Kolkata')
MAX_ACTIVE_SLOTS = 5
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT = os.environ.get('CHAT_ID')

def send_tg(msg):
    if TG_TOKEN and TG_CHAT:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        try: requests.post(url, json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"})
        except: print("TG Error")

def to_f(val):
    if not val: return 0.0
    try: return float(str(val).replace(',', '').replace('₹', '').strip())
    except: return 0.0

def move_to_history(ss, trade):
    try:
        hist = ss.worksheet("History")
        pnl = ((trade['exit_p'] - trade['entry_p']) / trade['entry_p'] * 100)
        res = "WIN 🟢" if pnl > 0 else "LOSS 🔴"
        hist.append_row([trade['sym'], trade['entry_t'], round(trade['entry_p'], 2), 
                         trade['exit_t'], round(trade['exit_p'], 2), f"{pnl:.2f}%", res, "0d", trade['cat']])
        send_tg(f"🏁 <b>EXIT: {trade['sym']}</b>\nPrice: {trade['exit_p']}\nP/L: {pnl:.2f}%")
        return True
    except: return False

def run_trading_cycle():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ['GCP_SERVICE_ACCOUNT_JSON']), scope)
    client = gspread.authorize(creds)
    ss = client.open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")

    if str(sheet.acell("O2").value).upper() != "YES": return

    data = sheet.get_all_values()[1:]
    active_trades = [r for r in data if "TRADED" in str(r[10]).upper()]
    active_count = len(active_trades)
    rows_to_del = []

    for i, row in enumerate(data):
        r_num = i + 2
        sym, price, stat = row[1], to_f(row[2]), str(row[10]).upper()
        sl, tgt, cat = to_f(row[7]), to_f(row[8]), row[5]

        if "TRADED" in stat:
            entry_p = to_f(row[11])
            if (price >= tgt > 0) or (price <= sl > 0): # Exit Condition
                if move_to_history(ss, {'sym': sym, 'entry_p': entry_p, 'exit_p': price, 'entry_t': row[12], 'exit_t': datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S'), 'cat': cat}):
                    rows_to_del.append(r_num)
                    active_count -= 1
        elif stat == "" and active_count < MAX_ACTIVE_SLOTS: # Entry Condition
            sheet.update_cell(r_num, 11, "TRADED (PAPER)")
            sheet.update_cell(r_num, 12, price)
            sheet.update_cell(r_num, 13, datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S'))
            send_tg(f"🚀 <b>ENTRY: {sym}</b>\nPrice: {price}\nTGT: {tgt}")
            active_count += 1

    for r in reversed(rows_to_del): sheet.delete_rows(r)
    sheet.update_acell("O5", f"Bot Active | A:{active_count}/5 | {datetime.now(IST).strftime('%H:%M:%S')}")

if __name__ == "__main__": run_trading_cycle()
