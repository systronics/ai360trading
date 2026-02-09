import os, json, gspread, requests, pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
IST = pytz.timezone('Asia/Kolkata')
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT = os.environ.get('CHAT_ID')

def send_tg(msg):
    """Sends formatted HTML messages to Telegram."""
    if TG_TOKEN and TG_CHAT:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}
        try: 
            requests.post(url, json=payload, timeout=15)
        except Exception as e: 
            print(f"❌ TG Error: {e}")

def to_f(val):
    """Cleanly converts sheet values to floats."""
    if not val: return 0.0
    try: 
        return float(str(val).replace(',', '').replace('₹', '').replace('%', '').strip())
    except: 
        return 0.0

def get_pro_stats(ss, active_trades):
    """Calculates realized and unrealized performance from History and Active trades."""
    try:
        hist = ss.worksheet("History")
        today = datetime.now(IST).strftime('%Y-%m-%d')
        all_hist = hist.get_all_values()[1:]
        
        # Filter for trades closed today
        today_closed = [t for t in all_hist if str(t[3]).startswith(today)]
        wins = sum(1 for t in today_closed if "WIN" in str(t[6]))
        losses = len(today_closed) - wins
        realized_pl = sum(to_f(t[5]) for t in today_closed)
        
        # Portfolio formatting
        unrealized_pl = sum(t['pnl'] for t in active_trades)
        p_list = "".join([f"{'🟢' if t['pnl'] >= 0 else '🔴'} {t['sym']}: {t['pnl']:+.2f}%\n" for t in active_trades])
        
        return today, len(today_closed), wins, losses, realized_pl, p_list, (realized_pl + unrealized_pl)
    except Exception as e:
        print(f"Stats Error: {e}")
        return None

def send_pro_summary(ss, active_trades, title_prefix="🏆 Daily Performance"):
    """Sends the final market-close summary."""
    stats = get_pro_stats(ss, active_trades)
    if not stats: return
    date, total, w, l, r_pl, p_list, t_net = stats
    msg = (f"🏆 <b>{title_prefix} - {date}</b>\n"
           f"━━━━━━━━━━━━━━━━━━━━\n"
           f"✅ <b>Closed Today: {total}</b> (W:{w} L:{l})\n"
           f"💰 <b>Realized P/L: {r_pl:+.2f}%</b>\n\n"
           f"📈 <b>Portfolio Status:</b>\n{p_list if p_list else 'No active trades.'}\n"
           f"💎 <b>Total Net P/L: {t_net:+.2f}%</b>\n"
           f"━━━━━━━━━━━━━━━━━━━━")
    send_tg(msg)

def run_trading_cycle():
    now = datetime.now(IST)
    today_date = now.strftime('%Y-%m-%d')
    
    # 1. AUTHENTICATION
    creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
    if not creds_json: return
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(creds_json), 
        ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    ss = gspread.authorize(creds).open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")

    # 2. MIDNIGHT SYSTEM RESET (Self-Cleaning Logic)
    # Clears O4/O5 status markers between 12:00 AM and 1:00 AM IST
    if now.hour == 0:
        sheet.update_acell("O4", "")
        sheet.update_acell("O5", "")
        print("🧹 Midnight reset complete. Ready for new day.")
        return

    # 3. DATA CATEGORIZATION
    rows = sheet.get_all_values()[1:]
    active_trades = []
    for row in rows:
        if len(row) > 11 and "TRADED" in str(row[10]).upper():
            entry_p = to_f(row[11])
            curr_p = to_f(row[2])
            pnl = ((curr_p - entry_p) / entry_p) * 100 if entry_p > 0 else 0
            active_trades.append({'sym': row[1], 'pnl': pnl})

    # 4. MANUAL OVERRIDE (Cell O5)
    manual_cmd = str(sheet.acell("O5").value).strip().upper()
    if manual_cmd == "SEND SUMMARY":
        send_pro_summary(ss, active_trades, "📊 Manual Update")
        sheet.update_acell("O5", "DONE")
        return

    # 5. AUTOMATED MESSAGES (Cell O4)
    sent_status = str(sheet.acell("O4").value).strip()

    # Morning Message (9:00 - 10:00 AM)
    if now.hour == 9 and sent_status != f"{today_date}-AM":
        send_tg(f"🌅 <b>Good Morning!</b> Market is open. Monitoring {len(active_trades)} trades.")
        sheet.update_acell("O4", f"{today_date}-AM")

    # Evening Summary (After 3:30 PM / 15:30)
    if (now.hour == 15 and now.minute >= 30) or (now.hour > 15):
        if sent_status != f"{today_date}-PM":
            send_pro_summary(ss, active_trades)
            sheet.update_acell("O4", f"{today_date}-PM")

if __name__ == "__main__":
    run_trading_cycle()
