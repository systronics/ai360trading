"""
AI360 TRADING BOT — v7.0 FRESH START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALERTLOG COLUMN MAP (0-based, verified):
  A=0  Signal Time(IST)       B=1  Symbol
  C=2  Live Price (VLOOKUP)   D=3  Priority Score
  E=4  Trend Status           F=5  Strategy (FINAL_ACTION)
  G=6  Breakout Stage         H=7  Min StopLoss (Pivot_Support)
  I=8  Max Target (CMP+ATR*3) J=9  RR Ratio
  K=10 Trade Status           L=11 Entry Price (CMP at signal)
  M=12 Entry Time             N=13 Current P/L%
  O=14 SYSTEM CONTROL (O2=switch, O4=memory)

HISTORY COLUMNS (verified from screenshot):
  A=Symbol  B=Entry Date  C=Entry Price  D=Exit Date
  E=Exit Price  F=P/L%  G=Result  H=Hold Duration  I=Strategy

APPSCRIPT HANDSHAKE:
  AppScript → writes K="TRADED (PAPER)", L=CMP, M=timestamp
  Python    → reads L+M, monitors price
  Python    → writes K="EXITED", appends History on SL/target
  AppScript → sees EXITED, removes row, fills new candidate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, json, pytz, requests, gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

IST        = pytz.timezone('Asia/Kolkata')
TG_TOKEN   = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT    = os.environ.get('CHAT_ID')
SHEET_NAME = "Ai360tradingAlgo"

# AlertLog columns (0-based, verified)
COL_SIGNAL_TIME = 0
COL_SYMBOL      = 1
COL_LIVE_PRICE  = 2
COL_PRIORITY    = 3
COL_TREND       = 4
COL_STRATEGY    = 5
COL_STAGE       = 6
COL_SL          = 7   # Python writes trail SL here only
COL_TARGET      = 8
COL_RR          = 9
COL_STATUS      = 10  # Python writes "EXITED" here only
COL_ENTRY_PRICE = 11  # AppScript writes CMP here
COL_ENTRY_TIME  = 12  # AppScript writes timestamp here
COL_PNL         = 13


# ── HELPERS ──────────────────────────────────────────────────────────────────

def send_tg(msg: str) -> bool:
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"},
            timeout=15
        )
        ok = r.status_code == 200
        if not ok:
            print(f"[TG FAIL] status={r.status_code} body={r.text[:200]}")
        return ok
    except Exception as e:
        print(f"[TG ERROR] {e}")
        return False


def to_f(val) -> float:
    try:
        return float(str(val).replace(',', '').replace('₹', '').replace('%', '').strip())
    except:
        return 0.0


def sym_key(sym: str) -> str:
    """Sanitize symbol for memory keys — remove colon, spaces."""
    return str(sym).replace(':', '_').replace(' ', '_').strip()


def calc_hold(entry_str: str, exit_dt: datetime) -> str:
    try:
        entry_dt = IST.localize(datetime.strptime(entry_str[:19], '%Y-%m-%d %H:%M:%S'))
        delta    = exit_dt - entry_dt
        d = delta.days
        h = delta.seconds // 3600
        m = (delta.seconds % 3600) // 60
        return f"{d}d {h}h" if d > 0 else f"{h}h {m}m"
    except:
        return ""


def clean_mem(mem: str) -> str:
    """Keep only last 30 days of date flags. Stock flags kept always."""
    cutoff = (datetime.now(IST) - timedelta(days=30)).strftime('%Y-%m-%d')
    kept   = []
    for p in mem.split(','):
        p = p.strip()
        if not p:
            continue
        is_date = len(p) > 10 and p[4] == '-' and p[7] == '-'
        if is_date:
            if p[:10] >= cutoff:
                kept.append(p)
        else:
            kept.append(p)  # _EX, _ENTRY, _TSL_ kept always
    return ','.join(kept)


def is_market_hours(now: datetime) -> bool:
    if now.weekday() >= 5:
        return False
    mins = now.hour * 60 + now.minute
    return (9 * 60 + 15) <= mins <= (15 * 60 + 30)


def get_tsl_price(mem: str, key: str) -> float:
    """Get last TSL checkpoint price for a symbol."""
    prefix = f"{key}_TSL_"
    for p in mem.split(','):
        if p.startswith(prefix):
            try:
                return int(p[len(prefix):]) / 100.0
            except:
                return 0.0
    return 0.0


def set_tsl_price(mem: str, key: str, price: float) -> str:
    """Update TSL checkpoint for a symbol in memory."""
    prefix = f"{key}_TSL_"
    parts  = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{int(round(price * 100))}")
    return ','.join(parts)


def pad(r: list, n: int = 15) -> list:
    r = list(r)
    while len(r) < n:
        r.append("")
    return r


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


def price_sanity(sym, cp, ent) -> bool:
    """Return True if prices are valid and realistic."""
    if cp <= 0 or ent <= 0:
        print(f"[WARN] {sym}: zero price cp={cp} ent={ent}")
        return False
    # Guard against VLOOKUP returning wrong stock price
    if cp > ent * 3:
        print(f"[WARN] {sym}: LTP ₹{cp} > 3x entry ₹{ent} — bad VLOOKUP, skipping")
        return False
    if cp < ent * 0.1:
        print(f"[WARN] {sym}: LTP ₹{cp} < 10% of entry ₹{ent} — bad VLOOKUP, skipping")
        return False
    return True


# ── MAIN ─────────────────────────────────────────────────────────────────────

def run_trading_cycle():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    mins  = now.hour * 60 + now.minute

    # Weekend gate
    if now.weekday() >= 5:
        print(f"[SKIP] Weekend ({now.strftime('%A')})")
        return

    # Time gate: 08:55–15:45 IST only
    if not ((8 * 60 + 55) <= mins <= (15 * 60 + 45)):
        print(f"[SKIP] Outside window: {now.strftime('%H:%M')} IST")
        return

    print(f"[START] {now.strftime('%Y-%m-%d %H:%M:%S')} IST")

    log_sheet, hist_sheet = get_sheets()

    # Load and clean memory from O4
    mem = clean_mem(str(log_sheet.acell("O4").value or ""))

    # Automation switch O2
    if str(log_sheet.acell("O2").value or "").strip().upper() != "YES":
        print("[SKIP] Automation OFF (O2 != YES)")
        log_sheet.update_acell("O4", mem)
        return

    # Read all 30 trade rows (rows 2–31)
    all_data   = log_sheet.get_all_values()
    trade_zone = [pad(list(r)) for r in all_data[1:31]]

    traded_rows = []   # (sheet_row_1based, row_data)
    for i, r in enumerate(trade_zone):
        status = str(r[COL_STATUS]).upper()
        if "TRADED" in status and "EXITED" not in status:
            traded_rows.append((i + 2, r))

    print(f"[INFO] Traded={len(traded_rows)}")

    # ═══════════════════════════════════════════════════════════
    # 1. GOOD MORNING  09:00–09:10 IST, once per day
    # ═══════════════════════════════════════════════════════════
    if now.hour == 9 and now.minute <= 10 and f"{today}_AM" not in mem:
        lines = []
        for _, r in traded_rows:
            sym  = r[COL_SYMBOL]
            live = to_f(r[COL_LIVE_PRICE])
            ent  = to_f(r[COL_ENTRY_PRICE])
            sl   = to_f(r[COL_SL])
            tgt  = to_f(r[COL_TARGET])
            if not price_sanity(sym, live, ent):
                continue
            pnl = (live - ent) / ent * 100
            em  = "🟢" if pnl >= 0 else "🔴"
            risk_pct   = abs((sl - ent) / ent * 100) if ent > 0 else 0
            reward_pct = abs((tgt - ent) / ent * 100) if ent > 0 else 0
            lines.append(
                f"{em} <b>{sym}</b>\n"
                f"   Entry ₹{ent:.2f} | LTP ₹{live:.2f} | <b>P/L {pnl:+.2f}%</b>\n"
                f"   SL ₹{sl:.2f} ({risk_pct:.1f}%) | T ₹{tgt:.2f} ({reward_pct:.1f}%)"
            )

        block = "\n\n".join(lines) if lines else "📭 No open trades"
        msg   = (
            f"🌅 <b>GOOD MORNING — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ System: Online | Market opens 09:15 IST\n\n"
            f"📋 <b>Open Trades ({len(lines)}):</b>\n\n"
            f"{block}"
        )
        if send_tg(msg):
            mem += f",{today}_AM"
            print("[MSG] Good Morning sent")

    # ═══════════════════════════════════════════════════════════
    # 2. MARKET HOURS — Entry / Trail SL / Exit
    # ═══════════════════════════════════════════════════════════
    if is_market_hours(now):
        exit_alerts      = []
        trail_alerts     = []
        entry_alerts     = []
        trail_sl_updates = []   # (sheet_row, new_sl_value)

        for sheet_row, r in traded_rows:
            sym = str(r[COL_SYMBOL]).strip()
            if not sym:
                continue

            key   = sym_key(sym)
            cp    = to_f(r[COL_LIVE_PRICE])
            sl    = to_f(r[COL_SL])
            ent   = to_f(r[COL_ENTRY_PRICE])
            tgt   = to_f(r[COL_TARGET])
            strat = str(r[COL_STRATEGY]).strip()
            stage = str(r[COL_STAGE]).strip()
            etime = str(r[COL_ENTRY_TIME]).strip()
            prio  = str(r[COL_PRIORITY]).strip()

            # Skip if prices invalid or impossible
            if not price_sanity(sym, cp, ent):
                continue

            pnl_pct = (cp - ent) / ent * 100

            # ── 2a. NEW ENTRY ALERT ─────────────────────────────────────────
            # Fires once per symbol when it first appears as TRADED
            entry_flag = f"{key}_ENTRY"
            if entry_flag not in mem:
                risk_pct   = abs((sl - ent) / ent * 100) if ent > 0 else 0
                reward_pct = abs((tgt - ent) / ent * 100) if ent > 0 else 0
                rr_reward  = (tgt - ent) if tgt > ent else 0
                rr_risk    = (ent - sl)  if ent > sl  else 1
                rr_ratio   = rr_reward / rr_risk if rr_risk > 0 else 0

                entry_alerts.append(
                    f"🚀 <b>NEW SIGNAL DETECTED</b>\n\n"
                    f"<b>Stock:</b> {sym}\n"
                    f"<b>Entry Type:</b> {stage}\n"
                    f"<b>CMP:</b> ₹{cp:.2f}\n"
                    f"<b>Stop Loss:</b> ₹{sl:.2f} (Risk: {risk_pct:.1f}%)\n"
                    f"<b>Target:</b> ₹{tgt:.2f} (Reward: {reward_pct:.1f}%)\n"
                    f"<b>Risk:Reward:</b> 1:{rr_ratio:.1f}\n"
                    f"<b>Strategy:</b> {strat}\n"
                    f"<b>Priority:</b> {prio}/30\n"
                    f"<b>Status:</b> ✅ Entered\n"
                    f"💡 <i>Bot has entered this trade</i>"
                )
                mem += f",{entry_flag}"
                # Initialise TSL checkpoint at entry price
                mem  = set_tsl_price(mem, key, ent)
                print(f"[ENTRY] {sym} @ ₹{ent} SL ₹{sl} T ₹{tgt}")

            # ── 2b. TRAILING STOP-LOSS ──────────────────────────────────────
            # Fires only when LTP rises ≥ 0.5% above last TSL checkpoint
            # New SL = entry + 50% of profit (locks half the gain)
            # SL moves UP only, never down
            # One message per 0.5% step — no spam
            if pnl_pct > 0 and sl > 0:
                last_cp   = get_tsl_price(mem, key)
                if last_cp <= 0:
                    last_cp = ent
                pct_above = (cp - last_cp) / last_cp * 100

                if pct_above >= 0.5:
                    new_sl = round(ent + (cp - ent) * 0.5, 2)
                    if new_sl > sl:
                        trail_sl_updates.append((sheet_row, new_sl))
                        trail_alerts.append(
                            f"📈 <b>{sym}</b> | LTP ₹{cp:.2f} (+{pnl_pct:.2f}%)\n"
                            f"   🔒 Trail SL: ₹{sl:.2f} → ₹{new_sl:.2f}"
                        )
                        mem = set_tsl_price(mem, key, cp)  # advance checkpoint
                        print(f"[TSL] {sym}: ₹{sl:.2f} → ₹{new_sl:.2f} | LTP ₹{cp:.2f}")

            # ── 2c. EXIT: SL BREACH OR TARGET HIT ──────────────────────────
            # Python writes "EXITED" to col K
            # AppScript removes the row on its next 5-min scan
            ex_flag    = f"{key}_EX"
            sl_hit     = (sl > 0 and cp <= sl)
            target_hit = (tgt > 0 and cp >= tgt)

            if (sl_hit or target_hit) and ex_flag not in mem:
                result_sym  = "WIN ✅" if target_hit else "LOSS 🔴"
                exit_label  = "🎯 TARGET HIT" if target_hit else "🚨 STOP-LOSS HIT"
                hold        = calc_hold(etime, now)

                exit_alerts.append(
                    f"{exit_label}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📌 <b>{sym}</b>\n"
                    f"   Entry ₹{ent:.2f} → Exit ₹{cp:.2f}\n"
                    f"   P/L: <b>{pnl_pct:+.2f}%</b> | Hold: {hold}\n"
                    f"   Strategy: {strat}"
                )

                # Write to History — exact columns from screenshot
                hist_sheet.append_row([
                    sym,                        # A Symbol
                    etime[:10],                 # B Entry Date
                    ent,                        # C Entry Price
                    now.strftime('%Y-%m-%d'),   # D Exit Date
                    cp,                         # E Exit Price
                    f"{pnl_pct:.2f}%",          # F P/L%
                    result_sym,                 # G Result "WIN ✅" / "LOSS 🔴"
                    hold,                       # H Hold Duration
                    strat                       # I Strategy
                ])

                # Handshake: set EXITED → AppScript removes row next scan
                log_sheet.update_cell(sheet_row, COL_STATUS + 1, "EXITED")
                mem += f",{ex_flag}"
                print(f"[EXIT] {sym} | {result_sym} | {pnl_pct:+.2f}%")

        # Batch write all trail SL updates in one API call
        if trail_sl_updates:
            cells = []
            for (sr, new_sl) in trail_sl_updates:
                c       = log_sheet.cell(sr, COL_SL + 1)  # col H = index 7 = sheet col 8
                c.value = new_sl
                cells.append(c)
            log_sheet.update_cells(cells)
            print(f"[TSL WRITE] {len(cells)} SL updates written")

        # Send batched Telegram messages — one per alert type
        if exit_alerts:
            send_tg(
                f"⚡ <b>EXIT REPORT — {now.strftime('%H:%M IST')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                + "\n\n".join(exit_alerts)
            )

        if trail_alerts:
            send_tg(
                f"🔒 <b>TRAIL SL UPDATE — {now.strftime('%H:%M IST')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                + "\n\n".join(trail_alerts)
            )

        # Each entry alert sent individually (matches your existing style)
        for alert in entry_alerts:
            send_tg(alert)

    # ═══════════════════════════════════════════════════════════
    # 3. MID-DAY PULSE  12:28–12:38 IST, once per day
    # ═══════════════════════════════════════════════════════════
    if now.hour == 12 and 28 <= now.minute <= 38 and f"{today}_NOON" not in mem:
        fresh       = log_sheet.get_all_values()
        live_traded = [
            pad(list(r)) for r in fresh[1:31]
            if "TRADED" in str(r[COL_STATUS] if len(r) > COL_STATUS else "").upper()
            and "EXITED" not in str(r[COL_STATUS] if len(r) > COL_STATUS else "").upper()
        ]
        wins = losses = 0
        lines = []
        for r in live_traded:
            sym  = r[COL_SYMBOL]
            live = to_f(r[COL_LIVE_PRICE])
            ent  = to_f(r[COL_ENTRY_PRICE])
            if not price_sanity(sym, live, ent):
                continue
            pnl = (live - ent) / ent * 100
            em  = "🟢" if pnl >= 0 else "🔴"
            if pnl >= 0: wins += 1
            else:        losses += 1
            lines.append(f"{em} <b>{sym}</b>: {pnl:+.2f}% (₹{live:.2f})")

        body = "\n".join(lines) if lines else "📭 No open trades"
        msg  = (
            f"☀️ <b>MID-DAY PULSE — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Open: {len(lines)} | 🟢 Profit: {wins} | 🔴 Loss: {losses}\n\n"
            f"{body}"
        )
        if send_tg(msg):
            mem += f",{today}_NOON"
            print("[MSG] Mid-day pulse sent")

    # ═══════════════════════════════════════════════════════════
    # 4. MARKET CLOSE SUMMARY  15:30–15:45 IST, once per day
    # ═══════════════════════════════════════════════════════════
    if now.hour == 15 and 30 <= now.minute <= 45 and f"{today}_PM" not in mem:
        # Today's exits from History sheet
        hist_data   = hist_sheet.get_all_values()
        today_exits = [r for r in hist_data[1:] if len(r) >= 7 and r[3] == today]
        wins        = [r for r in today_exits if "WIN"  in str(r[6]).upper()]
        losses      = [r for r in today_exits if "LOSS" in str(r[6]).upper()]

        exited_block = ""
        if today_exits:
            lines = []
            for r in today_exits:
                em = "✅" if "WIN" in str(r[6]).upper() else "❌"
                lines.append(f"  {em} <b>{r[0]}</b>: {r[5]} (hold {r[7]})")
            exited_block = "\n\n📋 <b>Exited Today:</b>\n" + "\n".join(lines)

        # Still-open overnight holds
        fresh2    = log_sheet.get_all_values()
        open_rows = [
            pad(list(r)) for r in fresh2[1:31]
            if "TRADED" in str(r[COL_STATUS] if len(r) > COL_STATUS else "").upper()
            and "EXITED" not in str(r[COL_STATUS] if len(r) > COL_STATUS else "").upper()
        ]
        open_block = ""
        if open_rows:
            lines = []
            for r in open_rows:
                sym  = r[COL_SYMBOL]
                live = to_f(r[COL_LIVE_PRICE])
                ent  = to_f(r[COL_ENTRY_PRICE])
                if not price_sanity(sym, live, ent):
                    continue
                pnl = (live - ent) / ent * 100
                em  = "🟢" if pnl >= 0 else "🔴"
                lines.append(f"  {em} <b>{sym}</b>: {pnl:+.2f}%")
            if lines:
                open_block = "\n\n📌 <b>Holding Overnight:</b>\n" + "\n".join(lines)

        msg = (
            f"🔔 <b>MARKET CLOSED — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 Wins: {len(wins)} | 💀 Losses: {len(losses)} | "
            f"📂 Open: {len(open_rows)}\n"
            f"📝 Exited today: {len(today_exits)} trades"
            f"{exited_block}"
            f"{open_block}\n\n"
            f"✅ <i>System active — overnight holds monitored</i>"
        )
        if send_tg(msg):
            mem += f",{today}_PM"
            print("[MSG] Market close summary sent")

    # ═══════════════════════════════════════════════════════════
    # 5. SAVE MEMORY — always last, every cycle
    # ═══════════════════════════════════════════════════════════
    log_sheet.update_acell("O4", mem)
    print(f"[DONE] {now.strftime('%H:%M:%S')} IST | mem_len={len(mem)}")


if __name__ == "__main__":
    run_trading_cycle()
