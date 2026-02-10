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
        payload = {"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}
        try: requests.post(url, json=payload, timeout=15)
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
        p_list = "".join([f"{'🟢' if t['pnl'] >= 0 else '🔴'} {t['sym']}: {t['pnl']:+.2f}%\n" for t in active_trades])
        unrealized_total = sum(t['pnl'] for t in active_trades)
        return today, len(today_closed), wins, losses, realized_pl, p_list, (realized_pl + unrealized_total)
    except: return None

def send_pro_summary(ss, active_trades, title_prefix="🏆 Daily Performance"):
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
    creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
    if not creds_json: return
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    ss = gspread.authorize(creds).open("Ai360tradingAlgo")
    sheet = ss.worksheet("AlertLog")

    # MIDNIGHT RESET
    if now.hour == 0:
        sheet.update_acell("O4", ""); sheet.update_acell("O5", ""); return

    rows = sheet.get_all_values()
    active_trades = []
    
    for i, row in enumerate(rows[1:], start=2):
        if len(row) > 11 and "TRADED" in str(row[10]).upper():
            sym, curr_p, old_sl, entry_p = row[1], to_f(row[2]), to_f(row[4]), to_f(row[11])
            pnl = ((curr_p - entry_p) / entry_p) * 100 if entry_p > 0 else 0
            
            # --- PRO TRAILING LOGIC ---
            # Using 3.5% to avoid the "Retail Stop Hunt" at 3.0%
            calculated_sl = round(curr_p * 0.965, 2)
            # Initial protective floor at -3.5%
            hard_floor = round(entry_p * 0.965, 2)
            
            # Only update if the new SL is significantly higher (0.5% move)
            if calculated_sl > (old_sl * 1.005):
                final_sl = max(calculated_sl, hard_floor)
                sheet.update_cell(i, 5, final_sl)
                send_tg(f"🛡️ <b>TSL Shift: {sym}</b>\nNew SL: ₹{final_sl}\nP/L: {pnl:+.2f}%")
            
            # EXIT NOTIFICATION
            if curr_p <= old_sl:
                send_tg(f"🚨 <b>EXIT SIGNAL: {sym}</b>\nPrice ₹{curr_p} hit SL ₹{old_sl}.\nP/L: {pnl:.2f}%")

            active_trades.append({'sym': sym, 'pnl': pnl})

    # MANUAL OVERRIDE
    manual_cmd = str(sheet.acell("O5").value).strip().upper()
    if manual_cmd == "SEND SUMMARY":
        send_pro_summary(ss, active_trades, "📊 Manual Update")
        sheet.update_acell("O5", "DONE"); return

    # AUTOMATED MESSAGES
    sent_status = str(sheet.acell("O4").value).strip()
    if now.hour == 9 and sent_status != f"{today_date}-AM":
        send_tg(f"🌅 <b>Good Morning!</b> Market is open. Monitoring {len(active_trades)} trades.")
        sheet.update_acell("O4", f"{today_date}-AM")

    if (now.hour == 15 and now.minute >= 30) or (now.hour > 15):
        if sent_status != f"{today_date}-PM":
            send_pro_summary(ss, active_trades)
            sheet.update_acell("O4", f"{today_date}-PM")

if __name__ == "__main__":
    run_trading_cycle()
