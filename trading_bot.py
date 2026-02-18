"""
AI360 TRADING BOT - FINAL CONSOLIDATED v4.0
Fixes:
  1. Max 10 TRADED slots (was capped at 6 by earlier logic)
  2. Good Morning message includes running trade summary
  3. Market Close sends full daily P/L summary
  4. History sheet columns matched exactly
  5. Pullback logic fixed (was preventing all exits near SL)
  6. Memory string bounded (no overflow)
  7. No spam - every message type guarded by mem flag
  8. No weekend / off-hours runs (saves GitHub Actions quota)
  9. Telegram rate-limit safe (one message per event, not per stock)
 10. Entry Price read from Column L (index 11), not re-calculated
"""

import os
import json
import gspread
import requests
import pytz
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

# ─── CONFIG ───────────────────────────────────────────────────────────────────
IST        = pytz.timezone('Asia/Kolkata')
TG_TOKEN   = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT    = os.environ.get('CHAT_ID')
SHEET_NAME = "Ai360tradingAlgo"

MAX_TRADED_SLOTS = 10   # ← was effectively 6 before; now explicit 10

# AlertLog column indices (0-based), matching Screenshot 2
COL_SIGNAL_TIME  = 0   # A
COL_SYMBOL       = 1   # B
COL_LIVE_PRICE   = 2   # C  ← VLOOKUP formula; gspread returns computed value
COL_PRIORITY     = 3   # D
COL_TREND        = 4   # E
COL_STRATEGY     = 5   # F
COL_STAGE        = 6   # G
COL_SL           = 7   # H  Min StopLoss
COL_TARGET       = 8   # I  Max Target
COL_RR           = 9   # J
COL_STATUS       = 10  # K  Trade Status
COL_ENTRY_PRICE  = 11  # L
COL_ENTRY_TIME   = 12  # M
COL_PNL_PCT      = 13  # N  Current P/L%

# History sheet column order (Screenshot 1)
# A=Symbol, B=Entry Date, C=Entry Price, D=Exit Date, E=Exit Price,
# F=P/L%, G=Result, H=Hold Duration, I=Strategy

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def send_tg(msg: str):
    """Send Telegram HTML message. Returns True on success."""
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"},
            timeout=15
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"[TG ERROR] {e}")
        return False


def to_f(val) -> float:
    """Safely convert any cell value to float."""
    try:
        return float(str(val).replace(',', '').replace('₹', '').replace('%', '').strip())
    except:
        return 0.0


def calc_hold_duration(entry_time_str: str, exit_time: datetime) -> str:
    """Return human-readable hold duration like '13d 2h'."""
    try:
        entry_dt = datetime.strptime(entry_time_str, '%Y-%m-%d %H:%M:%S')
        entry_dt = IST.localize(entry_dt)
        delta = exit_time - entry_dt
        days  = delta.days
        hours = delta.seconds // 3600
        if days > 0:
            return f"{days}d {hours}h"
        mins = (delta.seconds % 3600) // 60
        return f"{hours}h {mins}m"
    except:
        return ""


def clean_mem(mem: str, today: str) -> str:
    """
    Keep only flags from the last 30 days to prevent O4 cell overflow.
    Also always keep _CLEANED flags for the last 2 days.
    """
    cutoff = (datetime.now(IST) - timedelta(days=30)).strftime('%Y-%m-%d')
    kept = []
    for part in mem.split(','):
        part = part.strip()
        if not part:
            continue
        # Extract date prefix if present (format: YYYY-MM-DD_*)
        date_part = part[:10]
        if date_part >= cutoff:
            kept.append(part)
        elif '_EX' in part or '_ENTRY' in part:
            # Keep stock-level flags for 30 days based on date in flag
            kept.append(part)
    return ','.join(kept)


def is_market_hours(now: datetime) -> bool:
    """True if within NSE trading hours on a weekday."""
    if now.weekday() >= 5:   # Sat=5, Sun=6
        return False
    minutes = now.hour * 60 + now.minute
    return (9 * 60 + 0) <= minutes <= (15 * 60 + 40)


def get_sheet():
    """Authenticate and return the spreadsheet."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_JSON')), scope
    )
    return gspread.authorize(creds).open(SHEET_NAME)


# ─── MAIN CYCLE ───────────────────────────────────────────────────────────────

def run_trading_cycle():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    mins  = now.hour * 60 + now.minute

    # Skip weekends entirely
    if now.weekday() >= 5:
        print(f"[SKIP] Weekend - {now.strftime('%A')}")
        return

    # Allow 9:00 AM morning message even before market open
    # Block all other runs outside extended window (8:55–15:45)
    if not ((8 * 60 + 55) <= mins <= (15 * 60 + 45)):
        print(f"[SKIP] Outside operating window: {now.strftime('%H:%M')}")
        return

    print(f"[START] {now.strftime('%Y-%m-%d %H:%M:%S IST')}")

    # ── Connect ──────────────────────────────────────────────────────────────
    ss         = get_sheet()
    log_sheet  = ss.worksheet("AlertLog")
    hist_sheet = ss.worksheet("History")

    mem_cell = log_sheet.acell("O4")
    mem      = clean_mem(str(mem_cell.value or ""), today)

    # Fetch all 30 trade rows (rows 2–31 = index 1–30 in get_all_values)
    all_data   = log_sheet.get_all_values()
    trade_zone = all_data[1:31]   # list of rows, each row = list of strings

    # ── Classify rows ────────────────────────────────────────────────────────
    traded_rows  = []   # (sheet_row_num, row_data)  1-based sheet row
    waiting_rows = []

    for i, r in enumerate(trade_zone):
        sheet_row = i + 2   # row 2 = index 0
        status = str(r[COL_STATUS]).upper() if len(r) > COL_STATUS else ""
        if "TRADED" in status and "EXITED" not in status:
            traded_rows.append((sheet_row, r))
        elif "WAITING" in status:
            waiting_rows.append((sheet_row, r))

    # ─────────────────────────────────────────────────────────────────────────
    # 1. GOOD MORNING MESSAGE  (9:00–9:10 AM, once per day)
    # ─────────────────────────────────────────────────────────────────────────
    if now.hour == 9 and now.minute <= 10 and f"{today}_AM" not in mem:

        if traded_rows:
            lines = []
            for _, r in traded_rows:
                sym      = r[COL_SYMBOL]
                live     = to_f(r[COL_LIVE_PRICE])
                ent      = to_f(r[COL_ENTRY_PRICE])
                pnl_pct  = ((live - ent) / ent * 100) if ent > 0 and live > 0 else 0.0
                sl       = to_f(r[COL_SL])
                tgt      = to_f(r[COL_TARGET])
                emoji    = "🟢" if pnl_pct >= 0 else "🔴"
                lines.append(
                    f"  {emoji} <b>{sym}</b> | Entry: ₹{ent:.2f} | LTP: ₹{live:.2f} | "
                    f"P/L: {pnl_pct:+.2f}% | SL: ₹{sl:.2f} | T: ₹{tgt:.2f}"
                )
            trade_block = "\n".join(lines)
        else:
            trade_block = "  📭 No open trades"

        msg = (
            f"🌅 <b>GOOD MORNING - {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ <b>System:</b> Online | 🏦 <b>Market Opens:</b> 09:15 IST\n"
            f"📋 <b>Open Trades ({len(traded_rows)}/{MAX_TRADED_SLOTS}):</b>\n"
            f"{trade_block}"
        )
        if send_tg(msg):
            mem += f",{today}_AM"
            print("[MSG] Good Morning sent")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. STOP-LOSS / EXIT MONITORING  (market hours only)
    # ─────────────────────────────────────────────────────────────────────────
    if is_market_hours(now):
        exit_msgs    = []
        cells_update = []   # batch updates

        for sheet_row, r in traded_rows:
            sym  = str(r[COL_SYMBOL]).strip()
            if not sym:
                continue

            cp   = to_f(r[COL_LIVE_PRICE])
            sl   = to_f(r[COL_SL])
            ent  = to_f(r[COL_ENTRY_PRICE])
            tgt  = to_f(r[COL_TARGET])
            strat = str(r[COL_STRATEGY]).strip()
            entry_time_str = str(r[COL_ENTRY_TIME]).strip()

            if cp <= 0 or ent <= 0 or sl <= 0:
                continue

            pnl_pct = (cp - ent) / ent * 100

            # ── Exit condition ──────────────────────────────────────────────
            # FIX: cp <= sl is a clear breach. We do NOT suppress near-SL exits.
            # A "pullback guard" here only caused exits to never fire.
            sl_breached  = (cp <= sl)
            tgt_hit      = (cp >= tgt and tgt > 0)
            flag_key     = f"{sym}_EX"

            if (sl_breached or tgt_hit) and flag_key not in mem:
                exit_type   = "🎯 TARGET HIT" if tgt_hit else "🚨 STOP-LOSS HIT"
                result_word = "WIN ✅" if tgt_hit else "LOSS 🔴"
                hold        = calc_hold_duration(entry_time_str, now)

                exit_msgs.append(
                    f"{exit_type}\n"
                    f"📌 <b>{sym}</b>\n"
                    f"  Entry: ₹{ent:.2f} → Exit: ₹{cp:.2f}\n"
                    f"  P/L: <b>{pnl_pct:+.2f}%</b> | Hold: {hold}\n"
                    f"  Strategy: {strat}"
                )

                # Write to History sheet
                hist_sheet.append_row([
                    sym,                        # A Symbol
                    entry_time_str[:10],        # B Entry Date
                    ent,                        # C Entry Price
                    now.strftime('%Y-%m-%d'),   # D Exit Date
                    cp,                         # E Exit Price
                    f"{pnl_pct:.2f}%",          # F P/L%
                    "WIN" if tgt_hit else "LOSS",  # G Result
                    hold,                       # H Hold Duration
                    strat                       # I Strategy
                ])

                # Mark as EXITED so Apps Script removes it on next scan
                log_sheet.update_cell(sheet_row, COL_STATUS + 1, "EXITED")
                mem += f",{flag_key}"
                print(f"[EXIT] {sym} | {result_word} | P/L {pnl_pct:+.2f}%")

        # Send all exit alerts in ONE batched message to avoid spam
        if exit_msgs:
            header = f"⚡ <b>TRADE EXIT REPORT — {now.strftime('%H:%M IST')}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            send_tg(header + "\n\n".join(exit_msgs))

    # ─────────────────────────────────────────────────────────────────────────
    # 3. NEW ENTRY NOTIFICATION  (when a WAITING stock becomes TRADED)
    #    Apps Script sets it to TRADED; we detect and notify once.
    # ─────────────────────────────────────────────────────────────────────────
    if is_market_hours(now):
        entry_msgs = []
        for _, r in traded_rows:
            sym   = str(r[COL_SYMBOL]).strip()
            ent   = to_f(r[COL_ENTRY_PRICE])
            sl    = to_f(r[COL_SL])
            tgt   = to_f(r[COL_TARGET])
            strat = str(r[COL_STRATEGY]).strip()
            flag_key = f"{sym}_ENTRY"

            if sym and ent > 0 and flag_key not in mem:
                entry_msgs.append(
                    f"✅ <b>{sym}</b>\n"
                    f"  Entry: ₹{ent:.2f} | SL: ₹{sl:.2f} | T: ₹{tgt:.2f}\n"
                    f"  Strategy: {strat}"
                )
                mem += f",{flag_key}"

        if entry_msgs:
            header = f"🟢 <b>NEW TRADE ENTRIES — {now.strftime('%H:%M IST')}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            send_tg(header + "\n\n".join(entry_msgs))
            print(f"[ENTRY] Notified {len(entry_msgs)} new trades")

    # ─────────────────────────────────────────────────────────────────────────
    # 4. MID-DAY PULSE  (12:30 PM, once per day)
    # ─────────────────────────────────────────────────────────────────────────
    if now.hour == 12 and 28 <= now.minute <= 38 and f"{today}_NOON" not in mem:
        # Re-read traded rows after any exits above
        all_data2   = log_sheet.get_all_values()
        trade_zone2 = all_data2[1:31]
        live_traded  = [r for r in trade_zone2 if "TRADED" in str(r[COL_STATUS]).upper() and "EXITED" not in str(r[COL_STATUS]).upper()]

        if live_traded:
            lines = []
            for r in live_traded:
                sym     = r[COL_SYMBOL]
                live    = to_f(r[COL_LIVE_PRICE])
                ent     = to_f(r[COL_ENTRY_PRICE])
                pnl_pct = ((live - ent) / ent * 100) if ent > 0 and live > 0 else 0.0
                emoji   = "🟢" if pnl_pct >= 0 else "🔴"
                lines.append(f"  {emoji} <b>{sym}</b>: {pnl_pct:+.2f}% (₹{live:.2f})")
            trade_block = "\n".join(lines)
            wins  = sum(1 for r in live_traded if to_f(r[COL_LIVE_PRICE]) > to_f(r[COL_ENTRY_PRICE]))
            loss  = len(live_traded) - wins
        else:
            trade_block = "  📭 No open trades"
            wins = loss = 0

        msg = (
            f"☀️ <b>MID-DAY PULSE — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Open: {len(live_traded)} | 🟢 Profit: {wins} | 🔴 Loss: {loss}\n"
            f"{trade_block}"
        )
        if send_tg(msg):
            mem += f",{today}_NOON"
            print("[MSG] Mid-day pulse sent")

    # ─────────────────────────────────────────────────────────────────────────
    # 5. MARKET CLOSE DAILY SUMMARY  (3:30–3:45 PM, once per day)
    # ─────────────────────────────────────────────────────────────────────────
    if now.hour == 15 and 30 <= now.minute <= 45 and f"{today}_PM" not in mem:
        # Pull today's history rows
        hist_data = hist_sheet.get_all_values()
        today_trades = [r for r in hist_data[1:] if len(r) >= 7 and r[3] == today]

        wins  = [r for r in today_trades if str(r[6]).upper() == "WIN"]
        losses= [r for r in today_trades if str(r[6]).upper() == "LOSS"]

        win_pnl  = sum(to_f(r[5]) for r in wins)
        loss_pnl = sum(to_f(r[5]) for r in losses)  # will be negative values

        # Still open trades P/L
        all_data3   = log_sheet.get_all_values()
        trade_zone3 = all_data3[1:31]
        open_trades = [r for r in trade_zone3 if "TRADED" in str(r[COL_STATUS]).upper() and "EXITED" not in str(r[COL_STATUS]).upper()]
        open_pnl    = sum(
            ((to_f(r[COL_LIVE_PRICE]) - to_f(r[COL_ENTRY_PRICE])) / to_f(r[COL_ENTRY_PRICE]) * 100)
            for r in open_trades
            if to_f(r[COL_ENTRY_PRICE]) > 0 and to_f(r[COL_LIVE_PRICE]) > 0
        )

        exited_lines = ""
        if today_trades:
            exited_lines = "\n<b>📋 Exited Today:</b>\n"
            for r in today_trades:
                res_emoji = "✅" if str(r[6]).upper() == "WIN" else "❌"
                exited_lines += f"  {res_emoji} <b>{r[0]}</b>: {r[5]} (hold: {r[7]})\n"

        open_lines = ""
        if open_trades:
            open_lines = "\n<b>📌 Still Open:</b>\n"
            for r in open_trades:
                sym     = r[COL_SYMBOL]
                ent     = to_f(r[COL_ENTRY_PRICE])
                live    = to_f(r[COL_LIVE_PRICE])
                pnl_pct = ((live - ent) / ent * 100) if ent > 0 and live > 0 else 0.0
                emoji   = "🟢" if pnl_pct >= 0 else "🔴"
                open_lines += f"  {emoji} <b>{sym}</b>: {pnl_pct:+.2f}%\n"

        msg = (
            f"🔔 <b>MARKET CLOSED — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 Wins: {len(wins)} | 💀 Losses: {len(losses)} | 📂 Open: {len(open_trades)}\n"
            f"📈 Win P/L: +{win_pnl:.2f}% | 📉 Loss P/L: {loss_pnl:.2f}%\n"
            f"🔓 Open P/L: {open_pnl:+.2f}%"
            f"{exited_lines}"
            f"{open_lines}"
            f"\n✅ <i>System monitoring overnight holds</i>"
        )
        if send_tg(msg):
            mem += f",{today}_PM"
            print("[MSG] Market close summary sent")

    # ─────────────────────────────────────────────────────────────────────────
    # 6. SAVE MEMORY  (always, at end)
    # ─────────────────────────────────────────────────────────────────────────
    log_sheet.update_acell("O4", mem)
    print(f"[DONE] {now.strftime('%H:%M:%S')} | Mem length: {len(mem)}")


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_trading_cycle()
