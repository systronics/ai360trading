import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
IST = pytz.timezone('Asia/Kolkata')
MAX_SLOTS = 10 
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT = os.environ.get('CHAT_ID')

def send_tg(msg):
    if TG_TOKEN and TG_CHAT:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        try: requests.post(url, json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}, timeout=10)
        except Exception as e: print(f"❌ TG Error: {e}")

def to_f(val):
    if not val: return 0.0
    try: return float(str(val).replace(',', '').replace('₹', '').replace('%', '').strip())
    except: return 0.0

def get_pro_stats(ss, active_trades):
    try:
        hist = ss.worksheet("History")
        today = datetime.now(IST).strftime('%Y-%m-%d')
        all_hist = hist.get_all_values()[1:]
        today_closed = [t for t in all_hist if str(t[3]).startswith(today)]
        wins = sum(1 for t in today_closed if "WIN" in str(t[6]))
        losses = len(today_closed) - wins
        realized_pl = sum(to_f(t[5]) for t in today_closed)
        unrealized_pl = sum(t['pnl'] for t in active_trades)
        total_net = realized_pl + unrealized_pl
        p_list = "".join([f"{'🟢' if t['pnl'] >= 0 else '🔴'} {t['sym']}: {t['pnl']:+.2f}%\n" for t in active_trades])
        return today, len(today_closed), wins, losses, realized_pl, p_list, total_net
    except: return None

def send_morning_msg(p_list):
    msg = (
        f"🌅 <b>Good Morning Traders!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <b>Market is Opening Soon</b>\n"
        f"📊 <b>Current Open Portfolio:</b>\n\n"
        f"{p_list if p_list else 'No active positions.'}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 <i>Riding the trends for maximum gains!</i>"
    )
    send_tg(msg)

def send_pro_summary(ss, active_trades, title_prefix="🏆 Daily Performance"):
    stats = get_pro_stats(ss, active_trades)
    if not stats: return
    date, total, w, l, r_pl, p_list, t_net = stats
    msg = (
        f"🏆 <b>{title_prefix} - {date}</b>\n"
        f"===========================\n"
        f"✅ <b>Closed Today: {total}</b>\n"
        f"Wins: {w} | Losses: {l}\n"
        f"Realized P/L: {r_pl:+.2f}%\n\n"
        f"📈 <b>Current Open Portfolio:</b>\n"
        f"{p_list if p_list else 'No active positions.'}\n"
        f"💰 <b>Total Net P/L: {t_net:+.2f}%</b>\n"
        f"===========================\n"
        f"<i>Holding for targets... 🌙</i>"
    )
    send_tg(msg)

def run_trading_cycle():
    now = datetime.now(IST)
    curr_hm = now.strftime("%H:%M")
    curr_hour = now.hour
    curr_min = now.minute
    
    creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
    if not creds_json: return
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope)
    ss = gspread.authorize(creds).open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")

    # 1. Fetch Data & Categorize
    rows = sheet.get_all_values()[1:]
    active_trades, waiting_trades = [], []
    for i, row in enumerate(rows):
        status = str(row[10]).upper()
        stock = {'row': i+2, 'sym': row[1], 'price': to_f(row[2]), 'score': to_f(row[3]), 'sl': to_f(row[7]), 'entry_p': to_f(row[11])}
        if "TRADED" in status:
            stock['pnl'] = ((stock['price'] - stock['entry_p']) / stock['entry_p']) * 100 if stock['entry_p'] > 0 else 0
            active_trades.append(stock)
        elif "WAITING" in status: waiting_trades.append(stock)

    # 2. PRIORITY #1: Morning Message (9:00 - 9:25 AM Window)
    today_date = now.strftime('%Y-%m-%d')
    sent_status = str(sheet.acell("O4").value).strip()
    
    if curr_hour == 9 and curr_min <= 25:
        if sent_status != f"{today_date}-AM":
            p_list = "".join([f"{'🟢' if t['pnl'] >= 0 else '🔴'} {t['sym']}: {t['pnl']:+.2f}%\n" for t in active_trades])
            send_morning_msg(p_list)
            sheet.update_acell("O4", f"{today_date}-AM")

    # 3. PRIORITY #2: Manual Command (O5)
    manual_cmd = str(sheet.acell("O5").value).strip().upper()
    if manual_cmd == "SEND SUMMARY":
        send_pro_summary(ss, active_trades, "📊 Manual Update")
        sheet.update_acell("O5", "DONE")
        return

    # 4. Strength-Based Entry Logic
    waiting_trades.sort(key=lambda x: x['score'], reverse=True)
    # (Entry Logic based on waiting_trades strength goes here)

    # 5. Market Close Summary (3:30 - 4:00 PM Window)
    if (curr_hour == 15 and curr_min >= 30) or (curr_hour == 16 and curr_min <= 0):
        if sent_status != f"{today_date}-PM":
            send_pro_summary(ss, active_trades)
            sheet.update_acell("O4", f"{today_date}-PM")

if __name__ == "__main__":
    run_trading_cycle()
