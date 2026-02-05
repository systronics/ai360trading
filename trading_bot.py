import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
IST = pytz.timezone('Asia/Kolkata')
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

def get_summary_data(ss, active_trades):
    """Processes clean data for the professional summary"""
    try:
        hist = ss.worksheet("History")
        today = datetime.now(IST).strftime('%Y-%m-%d')
        all_hist = hist.get_all_values()[1:]
        today_closed = [t for t in all_hist if str(t[3]).startswith(today)]
        
        wins = sum(1 for t in today_closed if "WIN" in str(t[6]))
        losses = len(today_closed) - wins
        
        # Calculate Realized P/L from History
        realized_pl = sum(to_f(t[5]) for t in today_closed)
        unrealized_pl = sum(t['pnl'] for t in active_trades)
        total_net = realized_pl + unrealized_pl

        portfolio_list = ""
        for t in active_trades:
            icon = "🟢" if t['pnl'] >= 0 else "🔴"
            portfolio_list += f"{icon} {t['sym']}: {t['pnl']:+.2f}%\n"

        return today, len(today_closed), wins, losses, realized_pl, portfolio_list, total_net
    except: return None

def send_morning_msg(active_trades):
    """High-energy morning message for followers"""
    p_list = ""
    for t in active_trades:
        icon = "🟢" if t['pnl'] >= 0 else "🔴"
        p_list += f"{icon} {t['sym']}: {t['pnl']:+.2f}%\n"
    
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

def send_pro_summary(ss, active_trades, is_manual=False):
    """Yesterday's Perfect Style Summary"""
    data = get_summary_data(ss, active_trades)
    if not data: return
    date, total, w, l, r_pl, p_list, t_net = data
    
    title = "🏆 Daily Performance" if not is_manual else "📊 Manual Portfolio Update"
    
    msg = (
        f"🏆 <b>{title} - {date}</b>\n"
        f"===========================\n"
        f"✅ <b>Closed Trades: {total}</b>\n"
        f"Wins: {w} | Losses: {l}\n"
        f"Realized P/L: {r_pl:+.2f}%\n\n"
        f"📈 <b>Current Open Portfolio:</b>\n"
        f"{p_list}\n"
        f"💰 <b>Total Net P/L: {t_net:+.2f}%</b>\n"
        f"===========================\n"
        f"<i>Holding for targets... 🌙</i>"
    )
    send_tg(msg)

def run_trading_cycle():
    now = datetime.now(IST)
    curr_hm = now.strftime("%H:%M")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
    if not creds_json: return
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope)
    ss = gspread.authorize(creds).open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")

    # 1. Gather Active Trades First
    data = sheet.get_all_values()[1:]
    active_trades = []
    for row in data:
        if len(row) >= 12 and "TRADED" in str(row[10]).upper():
            p, ep = to_f(row[2]), to_f(row[11])
            active_trades.append({'sym': row[1], 'pnl': ((p-ep)/ep)*100 if ep>0 else 0})

    # 2. Manual Command (O5)
    manual_cmd = str(sheet.acell("O5").value).strip().upper()
    if manual_cmd == "SEND SUMMARY":
        send_pro_summary(ss, active_trades, is_manual=True)
        sheet.update_acell("O5", "DONE")
        return

    # 3. Scheduled Messages (O4)
    today_date = now.strftime('%Y-%m-%d')
    sent_status = str(sheet.acell("O4").value).strip()

    if "09:00" <= curr_hm <= "09:15" and sent_status != f"{today_date}-AM":
        send_morning_msg(active_trades)
        sheet.update_acell("O4", f"{today_date}-AM")

    if "15:30" <= curr_hm <= "15:45" and sent_status != f"{today_date}-PM":
        send_pro_summary(ss, active_trades)
        sheet.update_acell("O4", f"{today_date}-PM")

    # 4. Exit Logic (Column H Trailing SL)
    # ... (Your trailing SL logic remains here)

if __name__ == "__main__":
    run_trading_cycle()
