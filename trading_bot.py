import os, json, gspread, requests, pyotp, pytz
from dhanhq import dhanhq
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

IST = pytz.timezone('Asia/Kolkata')
MAX_ACTIVE_SLOTS = 5

def to_f(val):
    if not val: return 0.0
    try: return float(str(val).replace(',', '').replace('₹', '').strip())
    except: return 0.0

def calculate_hold_duration(entry_time_str):
    """Calculates holding time for History sheet"""
    try:
        entry_time = IST.localize(datetime.strptime(entry_time_str, '%Y-%m-%d %H:%M:%S'))
        delta = datetime.now(IST) - entry_time
        return f"{delta.days}d {delta.seconds // 3600}h"
    except: return "N/A"

def move_to_history(spreadsheet, trade):
    try:
        history_sheet = spreadsheet.worksheet("History")
        pnl_pct = ((trade['exit_p'] - trade['entry_p']) / trade['entry_p'] * 100)
        hold_time = calculate_hold_duration(trade['entry_t'])
        history_sheet.append_row([
            trade['sym'], trade['entry_t'], round(trade['entry_p'], 2),
            trade['exit_t'], round(trade['exit_p'], 2), f"{pnl_pct:.2f}%",
            "WIN 🟢" if pnl_pct > 0 else "LOSS 🔴", hold_time, trade['cat']
        ])
        return True
    except: return False

def run_trading_cycle():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ['GCP_SERVICE_ACCOUNT_JSON']), scope)
    client = gspread.authorize(creds)
    ss = client.open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")

    if str(sheet.acell("O2").value).upper() != "YES": return

    data_rows = sheet.get_all_values()[1:]
    active_count = len([r for r in data_rows if "TRADED" in str(r[10]).upper()])
    rows_to_delete = []

    for i, row in enumerate(data_rows):
        row_num = i + 2
        symbol, price, status = row[1], to_f(row[2]), str(row[10]).upper()
        sl, target, category = to_f(row[7]), to_f(row[8]), row[5]

        if "TRADED" in status:
            entry_p = to_f(row[11])
            if (price >= target > 0) or (price <= sl > 0):
                if move_to_history(ss, {'sym': symbol, 'entry_p': entry_p, 'exit_p': price, 'entry_t': row[12], 'exit_t': datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S'), 'cat': category}):
                    rows_to_delete.append(row_num)
                    active_count -= 1
        elif status == "" and active_count < MAX_ACTIVE_SLOTS:
            sheet.update_cell(row_num, 11, "TRADED (PAPER)")
            sheet.update_cell(row_num, 12, price)
            sheet.update_cell(row_num, 13, datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S'))
            active_count += 1

    for r_num in reversed(rows_to_delete): sheet.delete_rows(r_num)
    sheet.update_acell("O5", f"Bot Active | A:{active_count}/5 | {datetime.now(IST).strftime('%H:%M:%S')}")

if __name__ == "__main__":
    run_trading_cycle()
