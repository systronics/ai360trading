"""
AI360 TRADING BOT — FINAL v5.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
APPSCRIPT ↔ PYTHON COORDINATION (zero conflicts):

  AppScript OWNS  → cols A–K rows 2–31 (writes, clears, refills slots)
                    restores col C VLOOKUP formula after every write
                    reads/writes O4 once/day (only _CLEANED flag at 9:05 AM)
                    reads O2 (automation switch)

  Python OWNS     → col H (trail SL update only, never clears)
                    col K (writes "EXITED" to trigger AppScript removal)
                    History sheet (append rows)
                    O4 memory string (every 5-min cycle)

  Safe because:
    - AppScript never touches col H after initial fill
    - Python never clears/reorders rows 2–31 (AppScript does that)
    - "EXITED" in col K is the handshake: Python sets it, AppScript removes the row
    - O4 collision window is <1 min at 9:05 AM (AppScript _CLEANED vs Python cycle)

TRAILING SL:
  - Fires only when LTP rises ≥ 0.5% above last recorded trail checkpoint
  - Trail checkpoint stored per symbol in O4 mem: {SYM}_TSL_{int(price*100)}
  - New SL = entry + 50% of current profit (locks half the gain)
  - SL only moves UP, never down
  - One batched Telegram message per cycle (no per-stock spam)

MESSAGE SCHEDULE (all mem-guarded, fire once per day):
  09:00–09:10  Good Morning + full open trade snapshot
  Market hours Exit alerts (batched single message)
               Trail SL alerts (batched single message)
               New entry alerts (batched single message)
  12:28–12:38  Mid-day pulse
  15:30–15:45  Market close full summary (wins/losses/open P/L)

SKIPPED: weekends, before 08:55, after 15:45
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, json, pytz, requests, gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

# ── CONFIG ────────────────────────────────────────────────────────────────────
IST        = pytz.timezone('Asia/Kolkata')
TG_TOKEN   = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT    = os.environ.get('CHAT_ID')
SHEET_NAME = "Ai360tradingAlgo"

# AlertLog column indices (0-based) — verified against Screenshot 2
COL_SIGNAL_TIME = 0   # A  Signal Time (IST)
COL_SYMBOL      = 1   # B  Symbol
COL_LIVE_PRICE  = 2   # C  Live Price  (VLOOKUP — gspread returns computed value)
COL_PRIORITY    = 3   # D  Priority Score
COL_TREND       = 4   # E  Trend Status
COL_STRATEGY    = 5   # F  Strategy Category
COL_STAGE       = 6   # G  Breakout Stage
COL_SL          = 7   # H  Min StopLoss  ← Python writes trail SL here
COL_TARGET      = 8   # I  Max Target
COL_RR          = 9   # J  RR Ratio
COL_STATUS      = 10  # K  Trade Status  ← Python writes "EXITED" here
COL_ENTRY_PRICE = 11  # L  Entry Price
COL_ENTRY_TIME  = 12  # M  Entry Time
COL_PNL_PCT     = 13  # N  Current P/L%

# History sheet column order — verified against Screenshot 1
# A=Symbol  B=Entry Date  C=Entry Price  D=Exit Date  E=Exit Price
# F=P/L%    G=Result      H=Hold Duration  I=Strategy


# ── HELPERS ───────────────────────────────────────────────────────────────────

def send_tg(msg: str) -> bool:
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"},
            timeout=15
        )
        return r.status_code == 200
    except Exception as e:
        print(f"[TG ERROR] {e}")
        return False


def to_f(val) -> float:
    try:
        return float(str(val).replace(',', '').replace('₹', '').replace('%', '').strip())
    except:
        return 0.0


def calc_hold(entry_str: str, exit_dt: datetime) -> str:
    try:
        entry_dt = IST.localize(datetime.strptime(entry_str[:19], '%Y-%m-%d %H:%M:%S'))
        delta = exit_dt - entry_dt
        d, h  = delta.days, delta.seconds // 3600
        m     = (delta.seconds % 3600) // 60
        return f"{d}d {h}h" if d > 0 else f"{h}h {m}m"
    except:
        return ""


def clean_mem(mem: str) -> str:
    """Drop date-prefixed flags older than 30 days. Keep stock-level flags always."""
    cutoff = (datetime.now(IST) - timedelta(days=30)).strftime('%Y-%m-%d')
    kept   = []
    for p in mem.split(','):
        p = p.strip()
        if not p:
            continue
        # Date-prefixed: YYYY-MM-DD_*
        is_date_flag = len(p) > 10 and p[4] == '-' and p[7] == '-'
        if is_date_flag:
            if p[:10] >= cutoff:
                kept.append(p)
            # else: silently drop old date flags
        else:
            kept.append(p)   # _EX, _ENTRY, _TSL_* — keep always
    return ','.join(kept)


def is_market_hours(now: datetime) -> bool:
    if now.weekday() >= 5:
        return False
    mins = now.hour * 60 + now.minute
    return (9 * 60 + 15) <= mins <= (15 * 60 + 30)


def get_tsl_price(mem: str, sym: str) -> float:
    """Get last recorded trail checkpoint price for symbol. 0.0 if none."""
    prefix = f"{sym}_TSL_"
    for p in mem.split(','):
        if p.startswith(prefix):
            try:
                return int(p[len(prefix):]) / 100.0
            except:
                return 0.0
    return 0.0


def set_tsl_price(mem: str, sym: str, price: float) -> str:
    """Update TSL checkpoint for symbol in mem string."""
    prefix = f"{sym}_TSL_"
    parts  = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{int(round(price * 100))}")
    return ','.join(parts)


def get_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_JSON')), scope
    )
    ss = gspread.authorize(creds).open(SHEET_NAME)
    return ss.worksheet("AlertLog"), ss.worksheet("History")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def run_trading_cycle():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    mins  = now.hour * 60 + now.minute

    # Gate: skip weekends and outside operating window (08:55 – 15:45)
    if now.weekday() >= 5:
        print(f"[SKIP] Weekend ({now.strftime('%A')})")
        return
    if not ((8 * 60 + 55) <= mins <= (15 * 60 + 45)):
        print(f"[SKIP] Outside window: {now.strftime('%H:%M')}")
        return

    print(f"[START] {now.strftime('%Y-%m-%d %H:%M:%S')} IST")

    log_sheet, hist_sheet = get_sheets()

    # Read and clean memory from O4
    mem = clean_mem(str(log_sheet.acell("O4").value or ""))

    # Automation switch (O2) — same check AppScript does; no conflict
    if str(log_sheet.acell("O2").value or "").strip().upper() != "YES":
        print("[SKIP] Automation OFF (O2 != YES)")
        log_sheet.update_acell("O4", mem)
        return

    # Read all 30 trade rows (rows 2–31)
    all_data   = log_sheet.get_all_values()
    trade_zone = all_data[1:31]

    def pad(r):
        while len(r) < 14: r.append("")
        return r

    traded_rows = []   # (sheet_row_1based, row)
    for i, r in enumerate(trade_zone):
        r = pad(r)
        status = str(r[COL_STATUS]).upper()
        if "TRADED" in status and "EXITED" not in status:
            traded_rows.append((i + 2, r))

    print(f"[INFO] Traded={len(traded_rows)}")

    # ═══════════════════════════════════════════════════════════════════════
    # 1. GOOD MORNING  (09:00 – 09:10, once per day)
    # ═══════════════════════════════════════════════════════════════════════
    if now.hour == 9 and now.minute <= 10 and f"{today}_AM" not in mem:
        if traded_rows:
            lines = []
            for _, r in traded_rows:
                sym  = r[COL_SYMBOL]
                live = to_f(r[COL_LIVE_PRICE])
                ent  = to_f(r[COL_ENTRY_PRICE])
                sl   = to_f(r[COL_SL])
                tgt  = to_f(r[COL_TARGET])
                pnl  = ((live - ent) / ent * 100) if ent > 0 and live > 0 else 0.0
                em   = "🟢" if pnl >= 0 else "🔴"
                lines.append(
                    f"  {em} <b>{sym}</b> | Entry ₹{ent:.2f} | LTP ₹{live:.2f} | "
                    f"P/L <b>{pnl:+.2f}%</b> | SL ₹{sl:.2f} | T ₹{tgt:.2f}"
                )
            trade_block = "\n".join(lines)
        else:
            trade_block = "  📭 No open trades yet"

        msg = (
            f"🌅 <b>GOOD MORNING — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ System: Online | Market opens 09:15 IST\n"
            f"📋 <b>Open Trades ({len(traded_rows)}):</b>\n"
            f"{trade_block}"
        )
        if send_tg(msg):
            mem += f",{today}_AM"
            print("[MSG] Good Morning sent")

    # ═══════════════════════════════════════════════════════════════════════
    # 2. MARKET HOURS: Entry / Trail SL / Exit monitoring
    # ═══════════════════════════════════════════════════════════════════════
    if is_market_hours(now):
        exit_alerts  = []
        trail_alerts = []
        entry_alerts = []
        trail_sl_updates = []   # (sheet_row, new_sl) — batch written at end

        for sheet_row, r in traded_rows:
            sym   = str(r[COL_SYMBOL]).strip()
            if not sym:
                continue

            cp    = to_f(r[COL_LIVE_PRICE])
            sl    = to_f(r[COL_SL])
            ent   = to_f(r[COL_ENTRY_PRICE])
            tgt   = to_f(r[COL_TARGET])
            strat = str(r[COL_STRATEGY]).strip()
            etime = str(r[COL_ENTRY_TIME]).strip()

            if cp <= 0 or ent <= 0:
                continue

            pnl_pct = (cp - ent) / ent * 100

            # ── 2a. NEW ENTRY NOTIFICATION (fires once per symbol) ──────────
            # AppScript fills L (Entry Price) and M (Entry Time) when it sets
            # status to "TRADED (PAPER)". Python fires _ENTRY alert once.
            entry_flag = f"{sym}_ENTRY"
            if entry_flag not in mem and ent > 0:
                entry_alerts.append(
                    f"✅ <b>{sym}</b>\n"
                    f"  Entry ₹{ent:.2f} | SL ₹{sl:.2f} | Target ₹{tgt:.2f}\n"
                    f"  Strategy: {strat}"
                )
                mem += f",{entry_flag}"
                # Initialise TSL checkpoint at entry price
                mem = set_tsl_price(mem, sym, ent)

            # ── 2b. TRAILING STOP-LOSS ──────────────────────────────────────
            # Fires only when LTP rises ≥ 0.5% above last TSL checkpoint.
            # New SL = entry + 50% of profit (locks half the gain).
            # SL only ever moves UP.
            # Python writes new SL to col H (sheet col 8).
            # AppScript never modifies col H after initial fill — no conflict.
            if pnl_pct > 0 and sl > 0:
                last_checkpoint = get_tsl_price(mem, sym)
                if last_checkpoint <= 0:
                    last_checkpoint = ent   # fallback

                pct_above = (cp - last_checkpoint) / last_checkpoint * 100

                if pct_above >= 0.5:
                    new_sl = round(ent + (cp - ent) * 0.5, 2)
                    if new_sl > sl:   # only move up
                        trail_sl_updates.append((sheet_row, new_sl))
                        trail_alerts.append(
                            f"📈 <b>{sym}</b> | LTP ₹{cp:.2f} (+{pnl_pct:.2f}%)\n"
                            f"  🔒 Trail SL: ₹{sl:.2f} → ₹{new_sl:.2f}"
                        )
                        mem = set_tsl_price(mem, sym, cp)   # advance checkpoint to current LTP
                        print(f"[TSL] {sym}: ₹{sl} → ₹{new_sl} | LTP ₹{cp}")

            # ── 2c. EXIT: SL BREACH OR TARGET HIT ──────────────────────────
            # Python writes "EXITED" → AppScript removes row on next scan.
            # _EX flag prevents double-processing.
            ex_flag    = f"{sym}_EX"
            sl_hit     = (sl > 0 and cp <= sl)
            target_hit = (tgt > 0 and cp >= tgt)

            if (sl_hit or target_hit) and ex_flag not in mem:
                result     = "WIN" if target_hit else "LOSS"
                exit_label = "🎯 TARGET HIT" if target_hit else "🚨 STOP-LOSS HIT"
                hold       = calc_hold(etime, now)

                exit_alerts.append(
                    f"{exit_label}\n"
                    f"📌 <b>{sym}</b>\n"
                    f"  Entry ₹{ent:.2f} → Exit ₹{cp:.2f}\n"
                    f"  P/L: <b>{pnl_pct:+.2f}%</b> | Hold: {hold}\n"
                    f"  Strategy: {strat}"
                )

                # Append to History — columns match Screenshot 1 exactly
                hist_sheet.append_row([
                    sym,                        # A Symbol
                    etime[:10],                 # B Entry Date
                    ent,                        # C Entry Price
                    now.strftime('%Y-%m-%d'),   # D Exit Date
                    cp,                         # E Exit Price
                    f"{pnl_pct:.2f}%",          # F P/L%
                    result,                     # G Result
                    hold,                       # H Hold Duration
                    strat                       # I Strategy
                ])

                # Mark EXITED in col K (sheet col 11)
                # AppScript will remove this row on its next 5-min scan
                log_sheet.update_cell(sheet_row, COL_STATUS + 1, "EXITED")
                mem += f",{ex_flag}"
                print(f"[EXIT] {sym} | {result} | {pnl_pct:+.2f}%")

        # ── Batch write trail SL to col H (one API call for all) ────────────
        if trail_sl_updates:
            cell_list = []
            for (sr, new_sl) in trail_sl_updates:
                c = log_sheet.cell(sr, COL_SL + 1)   # COL_SL=7, sheet col=8
                c.value = new_sl
                cell_list.append(c)
            log_sheet.update_cells(cell_list)

        # ── Send all alert types as single batched messages ──────────────────
        if exit_alerts:
            send_tg(
                f"⚡ <b>EXIT REPORT — {now.strftime('%H:%M IST')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                + "\n\n".join(exit_alerts)
            )

        if trail_alerts:
            send_tg(
                f"🔒 <b>TRAIL SL UPDATE — {now.strftime('%H:%M IST')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                + "\n".join(trail_alerts)
            )

        if entry_alerts:
            send_tg(
                f"🟢 <b>NEW ENTRIES — {now.strftime('%H:%M IST')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                + "\n\n".join(entry_alerts)
            )

    # ═══════════════════════════════════════════════════════════════════════
    # 3. MID-DAY PULSE  (12:28 – 12:38, once per day)
    # ═══════════════════════════════════════════════════════════════════════
    if now.hour == 12 and 28 <= now.minute <= 38 and f"{today}_NOON" not in mem:
        # Re-read after any exits above
        fresh = log_sheet.get_all_values()
        live_traded = [
            pad(r) for r in fresh[1:31]
            if "TRADED" in str(r[COL_STATUS] if len(r) > COL_STATUS else "").upper()
            and "EXITED" not in str(r[COL_STATUS] if len(r) > COL_STATUS else "").upper()
        ]
        wins = losses = 0
        lines = []
        for r in live_traded:
            sym  = r[COL_SYMBOL]
            live = to_f(r[COL_LIVE_PRICE])
            ent  = to_f(r[COL_ENTRY_PRICE])
            pnl  = ((live - ent) / ent * 100) if ent > 0 and live > 0 else 0.0
            em   = "🟢" if pnl >= 0 else "🔴"
            if pnl >= 0: wins += 1
            else: losses += 1
            lines.append(f"  {em} <b>{sym}</b>: {pnl:+.2f}% (₹{live:.2f})")

        body = "\n".join(lines) if lines else "  📭 No open trades"
        msg  = (
            f"☀️ <b>MID-DAY PULSE — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Open: {len(live_traded)} | 🟢 {wins} profit | 🔴 {losses} loss\n"
            f"{body}"
        )
        if send_tg(msg):
            mem += f",{today}_NOON"
            print("[MSG] Mid-day pulse sent")

    # ═══════════════════════════════════════════════════════════════════════
    # 4. MARKET CLOSE SUMMARY  (15:30 – 15:45, once per day)
    # ═══════════════════════════════════════════════════════════════════════
    if now.hour == 15 and 30 <= now.minute <= 45 and f"{today}_PM" not in mem:
        # Exits from History sheet today
        hist_data    = hist_sheet.get_all_values()
        today_exits  = [r for r in hist_data[1:] if len(r) >= 7 and r[3] == today]
        wins         = [r for r in today_exits if str(r[6]).upper() == "WIN"]
        losses       = [r for r in today_exits if str(r[6]).upper() == "LOSS"]

        exited_block = ""
        if today_exits:
            lines = [
                f"  {'✅' if str(r[6]).upper()=='WIN' else '❌'} "
                f"<b>{r[0]}</b>: {r[5]} (hold {r[7]})"
                for r in today_exits
            ]
            exited_block = "\n\n<b>📋 Exited today:</b>\n" + "\n".join(lines)

        # Still-open trades
        fresh2     = log_sheet.get_all_values()
        open_rows  = [
            pad(r) for r in fresh2[1:31]
            if "TRADED" in str(r[COL_STATUS] if len(r) > COL_STATUS else "").upper()
            and "EXITED" not in str(r[COL_STATUS] if len(r) > COL_STATUS else "").upper()
        ]
        open_block = ""
        open_pnl   = 0.0
        if open_rows:
            lines = []
            for r in open_rows:
                sym  = r[COL_SYMBOL]
                live = to_f(r[COL_LIVE_PRICE])
                ent  = to_f(r[COL_ENTRY_PRICE])
                pnl  = ((live - ent) / ent * 100) if ent > 0 and live > 0 else 0.0
                open_pnl += pnl
                em   = "🟢" if pnl >= 0 else "🔴"
                lines.append(f"  {em} <b>{sym}</b>: {pnl:+.2f}%")
            open_block = "\n\n<b>📌 Holding overnight:</b>\n" + "\n".join(lines)

        msg = (
            f"🔔 <b>MARKET CLOSED — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 Wins: {len(wins)} | 💀 Losses: {len(losses)} | 📂 Open: {len(open_rows)}\n"
            f"📈 Exited today: {len(today_exits)} trades"
            f"{exited_block}"
            f"{open_block}\n\n"
            f"✅ <i>System active — overnight holds monitored</i>"
        )
        if send_tg(msg):
            mem += f",{today}_PM"
            print("[MSG] Market close summary sent")

    # ═══════════════════════════════════════════════════════════════════════
    # 5. SAVE MEMORY — always at the very end
    # ═══════════════════════════════════════════════════════════════════════
    log_sheet.update_acell("O4", mem)
    print(f"[DONE] {now.strftime('%H:%M:%S')} | mem_len={len(mem)}")


if __name__ == "__main__":
    run_trading_cycle()
