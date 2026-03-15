"""
AI360 TRADING BOT — FINAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE: trading_bot.py  (replace content, keep filename)

CHANNEL ROUTING (added on top of all existing logic):
  ⚡ Intraday      → Premium only
  🔄 Swing         → Basic + Premium
  📈 Positional    → Advance + Premium
  📊 Options Alert → Advance + Premium
  Regime/Summary   → Free public channel only

All existing logic unchanged — TSL, regime, history, memory etc.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, json, pytz, requests, gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

IST         = pytz.timezone('Asia/Kolkata')
TG_TOKEN    = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT     = os.environ.get('CHAT_ID')           # free public — regime/summary only
TG_CHAT_BASIC   = os.environ.get('CHAT_ID_BASIC')     # ai360trading_Basic — Swing
TG_CHAT_ADVANCE = os.environ.get('CHAT_ID_ADVANCE')   # ai360trading_Advance — Positional+Options
TG_CHAT_PREMIUM = os.environ.get('CHAT_ID_PREMIUM')   # ai360trading_Premium — ALL signals
SHEET_NAME  = "Ai360tradingAlgo"

# ── AlertLog column indices (0-based) ────────────────────────────────────────
C_SIGNAL_TIME = 0
C_SYMBOL      = 1
C_LIVE_PRICE  = 2
C_PRIORITY    = 3
C_TRADE_TYPE  = 4
C_STRATEGY    = 5
C_STAGE       = 6
C_INITIAL_SL  = 7
C_TARGET      = 8
C_RR          = 9
C_STATUS      = 10
C_ENTRY_PRICE = 11
C_ENTRY_TIME  = 12
C_DAYS        = 13
C_TRAIL_SL    = 14
C_PNL         = 15

CAPITAL_PER_TRADE = 10000
MAX_TRADES        = 5
MAX_WAITING       = 10

def get_position_capital(priority_str: str) -> int:
    try:
        p = float(str(priority_str).strip())
    except:
        p = 20
    if p >= 28: return 16000
    if p >= 25: return 13000
    if p >= 21: return 10000
    return 7000

TSL_BREAKEVEN_AT  = 2.0
TSL_LOCK1PCT_AT   = 4.0
TSL_ATR_TRAIL_AT  = 6.0
TSL_ATR_MULT      = 1.5
TSL_GAP_UP_PCT    = 8.0
TSL_GAP_LOCK_FRAC = 0.5
MIN_HOLD_SWING    = 2
MIN_HOLD_POS      = 3
HARD_LOSS_PCT     = 5.0


# ── HELPERS ──────────────────────────────────────────────────────────────────

def get_chat_ids_for_signal(ttype: str) -> list:
    """
    Route signal to correct channels based on trade type.
    Intraday      → Premium only
    Swing         → Basic + Premium
    Positional    → Advance + Premium
    Options Alert → Advance + Premium
    """
    t = ttype.upper()
    if "INTRADAY" in t:
        ids = [TG_CHAT_PREMIUM]
    elif "SWING" in t:
        ids = [TG_CHAT_BASIC, TG_CHAT_PREMIUM]
    elif "POSITIONAL" in t or "OPTIONS" in t:
        ids = [TG_CHAT_ADVANCE, TG_CHAT_PREMIUM]
    else:
        ids = [TG_CHAT_PREMIUM]
    return [i for i in ids if i]


def send_tg(msg: str, chat_ids: list = None) -> bool:
    """
    Send Telegram message to one or more chat IDs.
    Default (None) sends to free public channel only.
    """
    if chat_ids is None:
        chat_ids = [TG_CHAT]
    chat_ids = [c for c in chat_ids if c]
    if not chat_ids:
        print("[TG WARN] No valid chat IDs")
        return False
    chat_ids = list(dict.fromkeys(chat_ids))  # deduplicate
    success = True
    for chat_id in chat_ids:
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
                timeout=15
            )
            if r.status_code != 200:
                print(f"[TG FAIL] chat={chat_id} {r.status_code}: {r.text[:150]}")
                success = False
            else:
                print(f"[TG OK] chat={chat_id}")
        except Exception as e:
            print(f"[TG ERROR] chat={chat_id} {e}")
            success = False
    return success


def to_f(val) -> float:
    try:
        return float(str(val).replace(',', '').replace('₹', '').replace('%', '').strip())
    except:
        return 0.0


def sym_key(sym: str) -> str:
    return str(sym).replace(':', '_').replace(' ', '_').strip()


def pad(r: list, n: int = 20) -> list:
    r = list(r)
    while len(r) < n:
        r.append("")
    return r


def calc_hold_days(entry_str: str, exit_dt: datetime) -> int:
    try:
        entry_dt = IST.localize(datetime.strptime(str(entry_str)[:19], '%Y-%m-%d %H:%M:%S'))
        return max(0, (exit_dt - entry_dt).days)
    except:
        return 0


def calc_hold_str(entry_str: str, exit_dt: datetime) -> str:
    try:
        entry_dt = IST.localize(datetime.strptime(str(entry_str)[:19], '%Y-%m-%d %H:%M:%S'))
        delta    = exit_dt - entry_dt
        d = delta.days
        h = delta.seconds // 3600
        m = (delta.seconds % 3600) // 60
        return f"{d}d {h}h" if d > 0 else f"{h}h {m}m"
    except:
        return "—"


def clean_mem(mem: str) -> str:
    cutoff = (datetime.now(IST) - timedelta(days=30)).strftime('%Y-%m-%d')
    kept = []
    for p in mem.split(','):
        p = p.strip()
        if not p:
            continue
        if len(p) > 10 and p[4] == '-' and p[7] == '-':
            if p[:10] >= cutoff:
                kept.append(p)
        else:
            kept.append(p)
    return ','.join(kept)


def is_market_hours(now: datetime) -> bool:
    if now.weekday() >= 5:
        return False
    mins = now.hour * 60 + now.minute
    return (9 * 60 + 15) <= mins <= (15 * 60 + 30)


def get_tsl(mem: str, key: str) -> float:
    prefix = f"{key}_TSL_"
    for p in mem.split(','):
        if p.startswith(prefix):
            try:
                return int(p[len(prefix):]) / 100.0
            except:
                return 0.0
    return 0.0


def set_tsl(mem: str, key: str, price: float) -> str:
    prefix = f"{key}_TSL_"
    parts  = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{int(round(price * 100))}")
    return ','.join(parts)


def get_max_price(mem: str, key: str) -> float:
    prefix = f"{key}_MAX_"
    for p in mem.split(','):
        if p.startswith(prefix):
            try:
                return int(p[len(prefix):]) / 100.0
            except:
                return 0.0
    return 0.0


def set_max_price(mem: str, key: str, price: float) -> str:
    prefix   = f"{key}_MAX_"
    cur_max  = get_max_price(mem, key)
    if price <= cur_max:
        return mem
    parts = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{int(round(price * 100))}")
    return ','.join(parts)


def calc_new_tsl(cp: float, ent: float, init_sl: float, atr: float, ttype: str = "") -> float:
    if ent <= 0:
        return init_sl
    gain_pct = ((cp - ent) / ent) * 100
    if gain_pct >= TSL_GAP_UP_PCT:
        gap_lock = round(ent + (cp - ent) * TSL_GAP_LOCK_FRAC, 2)
        atr_trail = round(cp - (TSL_ATR_MULT * atr), 2)
        return max(gap_lock, atr_trail, round(ent * 1.02, 2))
    if gain_pct < TSL_BREAKEVEN_AT:
        return init_sl
    elif gain_pct < TSL_LOCK1PCT_AT:
        return round(ent, 2)
    elif gain_pct < TSL_ATR_TRAIL_AT:
        return round(ent * 1.02, 2)
    else:
        atr_trail = round(cp - (TSL_ATR_MULT * atr), 2)
        return max(atr_trail, round(ent * 1.02, 2))


def price_sanity(sym, cp, ent) -> bool:
    if cp <= 0 or ent <= 0:
        print(f"[WARN] {sym}: zero price cp={cp} ent={ent}")
        return False
    if cp > ent * 4:
        print(f"[WARN] {sym}: LTP ₹{cp} > 4× entry ₹{ent} — bad VLOOKUP")
        return False
    if cp < ent * 0.1:
        print(f"[WARN] {sym}: LTP ₹{cp} < 10% of entry ₹{ent} — bad VLOOKUP")
        return False
    return True


def get_atr_from_mem(mem: str, key: str) -> float:
    prefix = f"{key}_ATR_"
    for p in mem.split(','):
        if p.startswith(prefix):
            try:
                return int(p[len(prefix):]) / 100.0
            except:
                return 0.0
    return 0.0


def save_atr_to_mem(mem: str, key: str, atr: float) -> str:
    prefix = f"{key}_ATR_"
    parts  = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{int(round(atr * 100))}")
    return ','.join(parts)


def get_capital_from_mem(mem: str, key: str) -> int:
    prefix = f"{key}_CAP_"
    for p in mem.split(','):
        if p.startswith(prefix):
            try:    return int(p[len(prefix):])
            except: return CAPITAL_PER_TRADE
    return CAPITAL_PER_TRADE


def save_capital_to_mem(mem: str, key: str, capital: int) -> str:
    prefix = f"{key}_CAP_"
    parts  = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{capital}")
    return ','.join(parts)


def get_last_price(mem: str, key: str) -> float:
    prefix = f"{key}_LP_"
    for p in mem.split(','):
        if p.startswith(prefix):
            try:    return int(p[len(prefix):]) / 100.0
            except: return 0.0
    return 0.0


def set_last_price(mem: str, key: str, price: float) -> str:
    prefix = f"{key}_LP_"
    parts  = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{int(round(price * 100))}")
    return ','.join(parts)


def get_exit_date(mem: str, key: str) -> str:
    prefix = f"{key}_EXDT_"
    for p in mem.split(','):
        if p.startswith(prefix):
            return p[len(prefix):]
    return ""


def set_exit_date(mem: str, key: str, date_str: str) -> str:
    prefix = f"{key}_EXDT_"
    parts  = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{date_str}")
    return ','.join(parts)


def trading_days_since(date_str: str, now: datetime) -> int:
    if not date_str:
        return 999
    try:
        start = datetime.strptime(date_str, '%Y-%m-%d').date()
        end   = now.date()
        count = 0
        cur   = start
        while cur <= end:
            if cur.weekday() < 5:
                count += 1
            cur += timedelta(days=1)
        return max(0, count - 1)
    except:
        return 999


def options_hint(sym: str, cp: float, atr: float, trade_type: str) -> str:
    if "Options Alert" not in str(trade_type):
        return ""
    expected_move = round(atr * 1.5, 0)
    strike_ce     = round((cp + atr) / 50) * 50
    return (
        f"\n\n📊 <b>OPTIONS ADVISORY</b> (informational only)\n"
        f"   Stock: {sym} @ ₹{cp:.0f}\n"
        f"   Expected move: ~₹{expected_move:.0f} ({(expected_move/cp*100):.1f}%)\n"
        f"   CE strike hint: {int(strike_ce)} CE (buy on breakout confirm)\n"
        f"   ⚠️ Options are leveraged — size carefully"
    )


def get_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_JSON')), scope
    )
    ss = gspread.authorize(creds).open(SHEET_NAME)
    return ss.worksheet("AlertLog"), ss.worksheet("History"), ss.worksheet("Nifty200")


def get_market_regime(nifty_sheet) -> bool:
    try:
        row = nifty_sheet.row_values(2)
        if not row or "NIFTY" not in str(row[0]).upper():
            print("[REGIME] NIFTY50 row not found — defaulting to bullish")
            return True
        cmp_nifty  = to_f(row[2])
        dma20      = to_f(row[4])
        if cmp_nifty <= 0 or dma20 <= 0:
            print("[REGIME] Invalid Nifty data — defaulting to bullish")
            return True
        bullish = cmp_nifty >= dma20
        print(f"[REGIME] Nifty CMP ₹{cmp_nifty:.0f} vs 20DMA ₹{dma20:.0f} → {'BULLISH' if bullish else 'BEARISH'}")
        return bullish
    except Exception as e:
        print(f"[REGIME] Error: {e} — defaulting to bullish")
        return True


# ── MAIN ─────────────────────────────────────────────────────────────────────

def run_trading_cycle():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    mins  = now.hour * 60 + now.minute

    if now.weekday() >= 5:
        print(f"[SKIP] Weekend ({now.strftime('%A')})")
        return

    if not ((8 * 60 + 45) <= mins <= (15 * 60 + 45)):
        print(f"[SKIP] Outside window: {now.strftime('%H:%M')} IST")
        return

    print(f"[START] {now.strftime('%Y-%m-%d %H:%M:%S')} IST")

    log_sheet, hist_sheet, nifty_sheet = get_sheets()
    mem        = clean_mem(str(log_sheet.acell("T4").value or ""))
    is_bullish = get_market_regime(nifty_sheet)

    if str(log_sheet.acell("T2").value or "").strip().upper() != "YES":
        print("[SKIP] Automation OFF (T2 != YES)")
        log_sheet.update_acell("T4", mem)
        return

    all_data   = log_sheet.get_all_values()
    trade_zone = [pad(list(r)) for r in all_data[1:16]]

    traded_rows = []
    for i, r in enumerate(trade_zone):
        status = str(r[C_STATUS]).upper()
        if "TRADED" in status and "EXITED" not in status:
            traded_rows.append((i + 2, r))

    print(f"[INFO] Active trades: {len(traded_rows)}/{MAX_TRADES}")

    # ── GOOD MORNING ─────────────────────────────────────────────────────────
    if ((now.hour == 8 and now.minute >= 45) or (now.hour == 9 and now.minute <= 15)) and f"{today}_AM" not in mem:
        waiting_count = sum(
            1 for r in [pad(list(x)) for x in all_data[1:16]]
            if "WAITING" in str(r[C_STATUS]).upper()
        )
        lines = []
        for _, r in traded_rows:
            sym   = r[C_SYMBOL]
            cp    = to_f(r[C_LIVE_PRICE])
            ent   = to_f(r[C_ENTRY_PRICE])
            sl    = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
            tgt   = to_f(r[C_TARGET])
            ttype = str(r[C_TRADE_TYPE])
            etime = str(r[C_ENTRY_TIME])
            days  = calc_hold_days(etime, now)
            if not ent or ent <= 0:
                continue
            sl_label = "TSL" if sl > to_f(r[C_INITIAL_SL]) else "SL"
            if cp > 0 and ent > 0:
                pnl   = (cp - ent) / ent * 100
                pl_rs = round((cp - ent) / ent * CAPITAL_PER_TRADE)
                to_tgt = ((tgt - cp) / cp * 100) if cp > 0 else 0
                to_sl  = ((cp - sl) / cp * 100) if cp > 0 else 0
                em     = "🟢" if pnl >= 0 else "🔴"
                lines.append(
                    f"{em} <b>{sym}</b> [{ttype}] Day {days + 1}\n"
                    f"   Entry ₹{ent:.2f} → Now ₹{cp:.2f}\n"
                    f"   P/L: <b>{pnl:+.2f}%</b> = <b>₹{pl_rs:+,}</b>\n"
                    f"   {sl_label} ₹{sl:.2f} ({to_sl:.1f}% away) | "
                    f"Target ₹{tgt:.2f} ({to_tgt:.1f}% away)"
                )
            else:
                lines.append(
                    f"⏰ <b>{sym}</b> [{ttype}] Day {days + 1}\n"
                    f"   Entry ₹{ent:.2f} | {sl_label} ₹{sl:.2f} | Target ₹{tgt:.2f}\n"
                    f"   (Live price loading...)"
                )
        body     = "\n\n".join(lines) if lines else "📭 No open trades"
        deployed = sum(get_capital_from_mem(mem, sym_key(r[C_SYMBOL])) for _, r in traded_rows if r[C_SYMBOL])
        # Good morning goes to FREE public channel only
        if send_tg(
            f"🌅 <b>GOOD MORNING — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📈 Open: {len(lines)}/{MAX_TRADES} | "
            f"⏳ Waiting: {waiting_count}/{MAX_WAITING}\n"
            f"💰 Deployed: ~₹{deployed:,}\n\n"
            f"{body}"
        ):
            mem += f",{today}_AM"
            log_sheet.update_acell("T4", mem)

    # ── MARKET HOURS ─────────────────────────────────────────────────────────
    if is_market_hours(now):
        exit_alerts_with_type  = []   # list of (msg, ttype)
        trail_alerts_with_type = []   # list of (msg, ttype)
        entry_alerts_with_type = []   # list of (msg, ttype)
        tsl_cell_updates       = []
        entry_writes           = []

        # ── Step A: Mark WAITING → TRADED ────────────────────────────────────
        for i, r in enumerate(trade_zone):
            status = str(r[C_STATUS]).upper()
            sym    = str(r[C_SYMBOL]).strip()
            if "WAITING" not in status or not sym:
                continue

            active_count = sum(
                1 for _, ar in traded_rows
                if "TRADED" in str(ar[C_STATUS]).upper()
                and "EXITED" not in str(ar[C_STATUS]).upper()
            )
            if active_count >= MAX_TRADES:
                break

            cp       = to_f(r[C_LIVE_PRICE])
            init_sl  = to_f(r[C_INITIAL_SL])
            target   = to_f(r[C_TARGET])
            priority = str(r[C_PRIORITY])
            stage    = str(r[C_STAGE])
            strat    = str(r[C_STRATEGY])
            ttype    = str(r[C_TRADE_TYPE])

            if cp <= 0:
                continue

            key       = sym_key(sym)
            sheet_row = i + 2

            last_cp = get_last_price(mem, key)
            mem     = set_last_price(mem, key, cp)
            if last_cp > 0 and abs(cp - last_cp) < 0.01:
                print(f"[STALE] {sym}: price ₹{cp} unchanged — skipping entry")
                continue

            exit_date = get_exit_date(mem, key)
            if exit_date:
                days_since = trading_days_since(exit_date, now)
                if days_since < 5:
                    print(f"[COOLDOWN] {sym}: exited {days_since} trading days ago")
                    continue

            pos_size_check = round(CAPITAL_PER_TRADE / cp) if cp > 0 else 0
            if pos_size_check < 2:
                print(f"[SKIP] {sym}: CMP ₹{cp:,.0f} > ₹5,000 cap")
                continue

            capital = get_position_capital(priority)
            etime   = now.strftime('%Y-%m-%d %H:%M:%S')

            log_sheet.update_cell(sheet_row, C_STATUS + 1,      "🟢 TRADED (PAPER)")
            log_sheet.update_cell(sheet_row, C_ENTRY_PRICE + 1, cp)
            log_sheet.update_cell(sheet_row, C_ENTRY_TIME + 1,  etime)
            log_sheet.update_cell(sheet_row, C_TRAIL_SL + 1,    init_sl)

            risk   = cp - init_sl
            reward = target - cp
            rr_num = (reward / risk) if risk > 0 else 0
            log_sheet.update_cell(sheet_row, C_RR + 1, f"1:{rr_num:.1f}")

            if "Intraday" in ttype or "INTRADAY" in ttype:
                atr_tgt_mult = 2
            elif "Positional" in ttype or "POSITIONAL" in ttype:
                atr_tgt_mult = 4
            else:
                atr_tgt_mult = 3
            atr_est = (target - cp) / atr_tgt_mult if target > cp else 0
            mem = save_atr_to_mem(mem, key, atr_est)
            mem = save_capital_to_mem(mem, key, capital)
            mem = set_tsl(mem, key, init_sl)
            mem = set_max_price(mem, key, cp)

            updated_r                = list(r)
            updated_r[C_STATUS]      = "🟢 TRADED (PAPER)"
            updated_r[C_ENTRY_PRICE] = cp
            updated_r[C_ENTRY_TIME]  = etime
            updated_r[C_TRAIL_SL]    = init_sl
            traded_rows.append((sheet_row, updated_r))

            atr    = atr_est
            o_hint = options_hint(sym, cp, atr, ttype)
            mem   += f",{key}_ENTRY"

            pos_size  = round(capital / cp) if cp > 0 else 0
            risk_rs   = round(max(0, cp - init_sl) * pos_size)
            reward_rs = round(max(0, target - cp) * pos_size)

            alert_msg = (
                f"🚀 <b>TRADE ENTERED</b>\n\n"
                f"<b>Stock:</b> {sym}\n"
                f"<b>Type:</b> {ttype}\n"
                f"<b>Entry Price:</b> ₹{cp:.2f}\n"
                f"<b>Strategy:</b> {strat} | {stage}\n"
                f"<b>Qty:</b> {pos_size} shares @ ₹{capital:,} (Priority {priority})\n"
                f"<b>Initial SL:</b> ₹{init_sl:.2f} (Risk: ₹{risk_rs:,})\n"
                f"<b>Target:</b> ₹{target:.2f} (Reward: ₹{reward_rs:,})\n"
                f"<b>RR Ratio:</b> 1:{rr_num:.1f}\n"
                f"<b>Priority:</b> {priority}/30"
                f"{o_hint}"
            )
            entry_alerts_with_type.append((alert_msg, ttype))
            print(f"[ENTRY] {sym} @ ₹{cp} | Capital ₹{capital:,} | {pos_size}sh | Type={ttype}")

        # ── Step B: Monitor active trades ─────────────────────────────────────
        for sheet_row, r in traded_rows:
            sym      = str(r[C_SYMBOL]).strip()
            if not sym:
                continue

            key      = sym_key(sym)
            cp       = to_f(r[C_LIVE_PRICE])
            init_sl  = to_f(r[C_INITIAL_SL])
            cur_tsl  = to_f(r[C_TRAIL_SL]) or init_sl
            ent      = to_f(r[C_ENTRY_PRICE])
            tgt      = to_f(r[C_TARGET])
            strat    = str(r[C_STRATEGY])
            stage    = str(r[C_STAGE])
            etime    = str(r[C_ENTRY_TIME])
            ttype    = str(r[C_TRADE_TYPE])
            priority = str(r[C_PRIORITY])

            if not price_sanity(sym, cp, ent):
                continue

            mem     = set_max_price(mem, key, cp)
            pnl_pct = (cp - ent) / ent * 100
            atr     = get_atr_from_mem(mem, key)
            if atr <= 0:
                _tgt_mult = 4 if "Positional" in ttype else 2 if "Intraday" in ttype else 3
                atr = (tgt - ent) / _tgt_mult if tgt > ent else ent * 0.02

            days_held = calc_hold_days(etime, now)

            new_tsl = calc_new_tsl(cp, ent, init_sl, atr, ttype)
            new_tsl = max(new_tsl, get_tsl(mem, key), cur_tsl)

            if new_tsl > cur_tsl:
                tsl_cell_updates.append((sheet_row, new_tsl))
                trail_msg = (
                    f"🔒 <b>{sym}</b> | LTP ₹{cp:.2f} ({pnl_pct:+.2f}%)\n"
                    f"   Trail SL: ₹{cur_tsl:.2f} → <b>₹{new_tsl:.2f}</b> "
                    f"({'Breakeven' if abs(new_tsl-ent)<0.5 else 'ATR trail'})"
                )
                trail_alerts_with_type.append((trail_msg, ttype))
                mem = set_tsl(mem, key, new_tsl)
                print(f"[TSL] {sym}: ₹{cur_tsl:.2f}→₹{new_tsl:.2f}")

            ex_flag    = f"{key}_EX"
            tsl_hit    = (new_tsl > 0 and cp <= new_tsl)
            target_hit = (tgt > 0 and cp >= tgt)
            hard_loss  = pnl_pct < -HARD_LOSS_PCT

            if hard_loss and ex_flag not in mem:
                trade_capital = get_capital_from_mem(mem, key)
                pl_rupees  = round((cp - ent) / ent * trade_capital, 2)
                hold_str   = calc_hold_str(etime, now)
                max_price  = get_max_price(mem, key)
                exit_msg   = (
                    f"🚨 <b>HARD LOSS EXIT</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📌 <b>{sym}</b> [{ttype}]\n"
                    f"   Entry ₹{ent:.2f} → Exit ₹{cp:.2f}\n"
                    f"   P/L: <b>{pnl_pct:+.2f}%</b> = <b>₹{pl_rupees:+.0f}</b>\n"
                    f"   Loss exceeded {HARD_LOSS_PCT}% — thesis broken\n"
                    f"   Hold: {hold_str} | Day {days_held + 1}"
                )
                exit_alerts_with_type.append((exit_msg, ttype))
                hist_sheet.append_row([
                    sym, etime[:10], ent,
                    now.strftime('%Y-%m-%d'), cp,
                    f"{pnl_pct:.2f}%", "LOSS 🔴", strat,
                    "🚨 HARD LOSS EXIT", ttype, init_sl, new_tsl,
                    max_price if max_price > 0 else cp,
                    round(atr, 2), days_held,
                    CAPITAL_PER_TRADE, pl_rupees, "—",
                ])
                log_sheet.update_cell(sheet_row, C_STATUS + 1, "EXITED")
                mem += f",{ex_flag}"
                mem  = set_exit_date(mem, key, now.strftime('%Y-%m-%d'))
                print(f"[HARD LOSS] {sym} | {pnl_pct:+.2f}% | ₹{pl_rupees:+.0f}")
                continue

            is_pos   = "Positional" in ttype or "positional" in ttype.lower()
            min_hold = MIN_HOLD_POS if is_pos else MIN_HOLD_SWING

            near_hard_loss = pnl_pct < -4.0
            skip_exit = (
                days_held < min_hold
                and not target_hit
                and not hard_loss
                and not (near_hard_loss and not is_bullish)
            )

            if (tsl_hit or target_hit) and ex_flag not in mem and not skip_exit:
                exit_reason = "🎯 TARGET HIT"   if target_hit else \
                              "🔒 TRAILING SL"   if new_tsl > init_sl else \
                              "🚨 INITIAL SL HIT"
                result_sym  = "WIN ✅" if (target_hit or pnl_pct > 0) else "LOSS 🔴"
                hold_str    = calc_hold_str(etime, now)
                max_price   = get_max_price(mem, key)
                trade_capital = get_capital_from_mem(mem, key)
                pl_rupees   = round((cp - ent) / ent * trade_capital, 2)
                o_note      = ""

                exit_msg = (
                    f"{'🎯' if target_hit else '⚡'} <b>{exit_reason}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📌 <b>{sym}</b> [{ttype}]\n"
                    f"   Entry ₹{ent:.2f} → Exit ₹{cp:.2f}\n"
                    f"   P/L: <b>{pnl_pct:+.2f}%</b> = <b>₹{pl_rupees:+.0f}</b>\n"
                    f"   Hold: {hold_str} | Max seen: ₹{max_price:.2f}\n"
                    f"   Strategy: {strat}"
                )
                exit_alerts_with_type.append((exit_msg, ttype))

                hist_sheet.append_row([
                    sym, etime[:10], ent,
                    now.strftime('%Y-%m-%d'), cp,
                    f"{pnl_pct:.2f}%", result_sym, strat,
                    exit_reason, ttype, init_sl, new_tsl,
                    max_price if max_price > 0 else cp,
                    round(atr, 2), days_held,
                    CAPITAL_PER_TRADE, pl_rupees,
                    o_note[:100] if o_note else "—",
                ])
                log_sheet.update_cell(sheet_row, C_STATUS + 1, "EXITED")
                mem += f",{ex_flag}"
                mem  = set_exit_date(mem, key, now.strftime('%Y-%m-%d'))
                print(f"[EXIT] {sym} | {result_sym} | {pnl_pct:+.2f}% | ₹{pl_rupees:+.0f}")

            elif tsl_hit and skip_exit:
                print(f"[HOLD] {sym}: SL touched but Day {days_held + 1} < {min_hold} min hold")
                if f"{key}_HOLD_WARN" not in mem:
                    regime_note = "🐂 Bullish market — recovery possible" if is_bullish else "🐻 Bearish market — watching closely"
                    # Min hold warning → free public channel only
                    send_tg(
                        f"⚠️ <b>MIN HOLD ACTIVE</b>\n"
                        f"<b>{sym}</b> [{ttype}] touched SL ₹{new_tsl:.2f} but only Day {days_held + 1} of {min_hold}.\n"
                        f"Holding until Day {min_hold} unless loss exceeds {HARD_LOSS_PCT}%.\n"
                        f"Current P/L: {pnl_pct:+.2f}%\n"
                        f"{regime_note}"
                    )
                    mem += f",{key}_HOLD_WARN"

        # Batch write TSL
        if tsl_cell_updates:
            cells = []
            for (sr, new_tsl) in tsl_cell_updates:
                c       = log_sheet.cell(sr, C_TRAIL_SL + 1)
                c.value = new_tsl
                cells.append(c)
            log_sheet.update_cells(cells)
            print(f"[TSL WRITE] {len(cells)} updates")

        # ── Send alerts to correct channels ───────────────────────────────────
        # Exit alerts — each to its own channel set
        for alert_msg, ttype in exit_alerts_with_type:
            send_tg(
                f"⚡ <b>EXIT REPORT — {now.strftime('%H:%M IST')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                + alert_msg,
                get_chat_ids_for_signal(ttype)
            )

        # Trail SL alerts — each to its own channel set
        for trail_msg, ttype in trail_alerts_with_type:
            send_tg(
                f"🔒 <b>TRAIL SL UPDATE — {now.strftime('%H:%M IST')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                + trail_msg,
                get_chat_ids_for_signal(ttype)
            )

        # Entry alerts — each to its own channel set
        for alert_msg, ttype in entry_alerts_with_type:
            send_tg(alert_msg, get_chat_ids_for_signal(ttype))

    # ── MID-DAY PULSE ─────────────────────────────────────────────────────────
    if now.hour == 12 and 28 <= now.minute <= 38 and f"{today}_NOON" not in mem:
        fresh      = log_sheet.get_all_values()
        live_rows  = [
            pad(list(r)) for r in fresh[1:16]
            if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
            and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        ]
        wins = losses = 0
        lines = []
        for r in live_rows:
            sym   = r[C_SYMBOL]
            cp    = to_f(r[C_LIVE_PRICE])
            ent   = to_f(r[C_ENTRY_PRICE])
            tsl   = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
            ttype = str(r[C_TRADE_TYPE])
            if not price_sanity(sym, cp, ent):
                continue
            pnl = (cp - ent) / ent * 100
            em  = "🟢" if pnl >= 0 else "🔴"
            if pnl >= 0: wins += 1
            else:        losses += 1
            lines.append(f"{em} <b>{sym}</b> [{ttype}]: {pnl:+.2f}% | TSL ₹{tsl:.2f}")
        # Mid-day → free public channel only
        if send_tg(
            f"☀️ <b>MID-DAY PULSE — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Open: {len(lines)} | 🟢 {wins} | 🔴 {losses}\n\n"
            + ("\n".join(lines) if lines else "📭 No open trades")
        ):
            mem += f",{today}_NOON"

    # ── MARKET CLOSE ──────────────────────────────────────────────────────────
    if now.hour == 15 and 15 <= now.minute <= 45 and f"{today}_PM" not in mem:
        hist_data   = hist_sheet.get_all_values()
        today_exits = [r for r in hist_data[1:] if len(r) >= 7 and r[3] == today]
        wins_today  = [r for r in today_exits if "WIN"  in str(r[6]).upper()]
        loss_today  = [r for r in today_exits if "LOSS" in str(r[6]).upper()]
        total_pl    = sum(to_f(r[16]) for r in today_exits if len(r) > 16)

        exit_lines = []
        for r in today_exits:
            em   = "✅" if "WIN" in str(r[6]).upper() else "❌"
            pl_r = f"₹{to_f(r[16]):+.0f}" if len(r) > 16 else ""
            exit_lines.append(f"  {em} <b>{r[0]}</b>: {r[5]} {pl_r} (hold {r[14] if len(r)>14 else '?'}d)")

        fresh3    = log_sheet.get_all_values()
        open_rows = [
            pad(list(r)) for r in fresh3[1:16]
            if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
            and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        ]
        open_lines = []
        for r in open_rows:
            sym  = r[C_SYMBOL]
            cp   = to_f(r[C_LIVE_PRICE])
            ent  = to_f(r[C_ENTRY_PRICE])
            tsl  = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
            if not ent or ent <= 0:
                continue
            if cp > 0 and ent > 0:
                pnl = (cp - ent) / ent * 100
                em  = "🟢" if pnl >= 0 else "🔴"
                open_lines.append(f"  {em} <b>{sym}</b>: {pnl:+.2f}% | TSL ₹{tsl:.2f}")
            else:
                open_lines.append(f"  ⏰ <b>{sym}</b>: TSL ₹{tsl:.2f}")

        msg = (
            f"🔔 <b>MARKET CLOSED — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 Wins: {len(wins_today)} | 💀 Losses: {len(loss_today)} | "
            f"📂 Open: {len(open_rows)}\n"
            f"💰 Today's P/L: <b>₹{total_pl:+.0f}</b>\n"
        )
        if exit_lines:
            msg += "\n📋 <b>Exited Today:</b>\n" + "\n".join(exit_lines)
        if open_lines:
            msg += "\n\n📌 <b>Holding Overnight:</b>\n" + "\n".join(open_lines)
        msg += "\n\n✅ <i>Overnight holds monitored via TSL</i>"
        # Market close → free public channel only
        if send_tg(msg):
            mem += f",{today}_PM"

    # ── SAVE MEMORY ───────────────────────────────────────────────────────────
    log_sheet.update_acell("T4", mem)
    print(f"[DONE] {now.strftime('%H:%M:%S')} IST | mem={len(mem)} chars")


# ── WEEKLY SUMMARY ────────────────────────────────────────────────────────────
def run_weekly_summary():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    print("[WEEKLY] Fetching weekly + monthly summary...")

    log_sheet, hist_sheet, _ = get_sheets()
    hist_data = hist_sheet.get_all_values()
    all_rows  = hist_data[1:]

    days_since_mon = now.weekday()
    mon  = (now - timedelta(days=days_since_mon)).strftime('%Y-%m-%d')
    mon1 = now.strftime('%Y-%m-01')

    week_rows  = [r for r in all_rows if len(r) >= 17 and r[3] >= mon  and r[3] <= today]
    month_rows = [r for r in all_rows if len(r) >= 17 and r[3] >= mon1 and r[3] <= today]
    all_closed = [r for r in all_rows if len(r) >= 17 and r[3]]

    def stats(rows):
        wins   = [r for r in rows if "WIN"  in str(r[6]).upper()]
        losses = [r for r in rows if "LOSS" in str(r[6]).upper()]
        pl     = sum(to_f(r[16]) for r in rows)
        wr     = round(len(wins) / len(rows) * 100) if rows else 0
        avg    = pl / len(rows) if rows else 0
        return len(rows), len(wins), len(losses), pl, wr, avg

    wt, ww, wl, wpl, wwr, wavg = stats(week_rows)
    mt, mw, ml, mpl, mwr, mavg = stats(month_rows)
    at, aw, al, apl, awr, aavg = stats(all_closed)

    best  = max(week_rows, key=lambda r: to_f(r[16]), default=None)
    worst = min(week_rows, key=lambda r: to_f(r[16]), default=None)

    all_data   = log_sheet.get_all_values()
    open_count = sum(
        1 for r in all_data[1:16]
        if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
    )

    msg = (
        f"📅 <b>WEEKLY REPORT — w/e {today}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"\n📆 <b>THIS WEEK</b>\n"
        f"   Trades: {wt} | ✅ {ww}W / ❌ {wl}L | Win: {wwr}%\n"
        f"   P/L: <b>₹{wpl:+,.0f}</b> | Avg/trade: ₹{wavg:+,.0f}\n"
    )
    if best:
        msg += f"   🏆 Best:  <b>{best[0]}</b> = ₹{to_f(best[16]):+,.0f}\n"
    if worst and worst != best:
        msg += f"   💀 Worst: <b>{worst[0]}</b> = ₹{to_f(worst[16]):+,.0f}\n"
    msg += (
        f"\n📅 <b>THIS MONTH ({now.strftime('%B')})</b>\n"
        f"   Trades: {mt} | ✅ {mw}W / ❌ {ml}L | Win: {mwr}%\n"
        f"   P/L: <b>₹{mpl:+,.0f}</b> | Avg/trade: ₹{mavg:+,.0f}\n"
        f"\n📊 <b>ALL TIME</b>\n"
        f"   Trades: {at} | ✅ {aw}W / ❌ {al}L | Win: {awr}%\n"
        f"   Total P/L: <b>₹{apl:+,.0f}</b> | Avg/trade: ₹{aavg:+,.0f}\n"
        f"\n📌 Open now: {open_count}/{MAX_TRADES}"
    )
    # Weekly summary → free public channel only
    ok = send_tg(msg)
    print(f"[WEEKLY] {'✅ Sent' if ok else '❌ Failed'}")


# ── TEST TELEGRAM ─────────────────────────────────────────────────────────────
def run_test_telegram():
    now = datetime.now(IST)
    print("[TEST] Sending Telegram test to all channels...")

    channels = {
        "Free Public":  TG_CHAT,
        "Basic":        TG_CHAT_BASIC,
        "Advance":      TG_CHAT_ADVANCE,
        "Premium":      TG_CHAT_PREMIUM,
    }

    for name, chat_id in channels.items():
        if not chat_id:
            print(f"[TEST] {name}: No chat ID set — skipping")
            continue
        ok = send_tg(
            f"✅ <b>TELEGRAM TEST — {name}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 Bot: AI360 Trading\n"
            f"📢 Channel: {name}\n"
            f"🕐 Time: {now.strftime('%Y-%m-%d %H:%M:%S')} IST\n"
            f"🔑 Token: Connected ✅\n\n"
            f"<i>If you see this, channel routing is working correctly.</i>",
            [chat_id]
        )
        print(f"[TEST] {name}: {'✅ OK' if ok else '❌ FAILED'}")


# ── DAILY SUMMARY ─────────────────────────────────────────────────────────────
def run_daily_summary():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    print("[SUMMARY] Fetching portfolio summary...")

    log_sheet, hist_sheet, _ = get_sheets()

    all_data  = log_sheet.get_all_values()
    open_rows = [
        pad(list(r)) for r in all_data[1:16]
        if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
    ]
    waiting_rows = [
        pad(list(r)) for r in all_data[1:16]
        if "WAITING" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
    ]

    trade_lines   = []
    total_pnl_pct = 0.0
    for r in open_rows:
        sym   = r[C_SYMBOL]
        cp    = to_f(r[C_LIVE_PRICE])
        ent   = to_f(r[C_ENTRY_PRICE])
        tsl   = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
        tgt   = to_f(r[C_TARGET])
        ttype = str(r[C_TRADE_TYPE])
        etime = str(r[C_ENTRY_TIME])
        if not price_sanity(sym, cp, ent):
            continue
        pnl   = (cp - ent) / ent * 100
        pl_rs = round((cp - ent) / ent * CAPITAL_PER_TRADE)
        days  = calc_hold_days(etime, now)
        em    = "🟢" if pnl >= 0 else "🔴"
        total_pnl_pct += pnl
        trade_lines.append(
            f"{em} <b>{sym}</b> [{ttype}]\n"
            f"   Entry ₹{ent:.2f} → Now ₹{cp:.2f} | <b>{pnl:+.2f}%</b> = ₹{pl_rs:+,}\n"
            f"   TSL ₹{tsl:.2f} | Target ₹{tgt:.2f} | Day {days}"
        )

    hist_data   = hist_sheet.get_all_values()
    today_exits = [r for r in hist_data[1:] if len(r) >= 7 and r[3] == today]
    exit_lines  = []
    total_exit_pl = 0.0
    for r in today_exits:
        em   = "✅" if "WIN" in str(r[6]).upper() else "❌"
        pl_r = to_f(r[16]) if len(r) > 16 else 0
        total_exit_pl += pl_r
        exit_lines.append(f"  {em} <b>{r[0]}</b>: {r[5]} = ₹{pl_r:+,.0f}")

    wait_lines = []
    for r in waiting_rows[:5]:
        wait_lines.append(f"  ⏳ <b>{r[C_SYMBOL]}</b> [{r[C_TRADE_TYPE]}] Priority:{r[C_PRIORITY]}")

    msg = (
        f"📊 <b>PORTFOLIO SUMMARY</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 {now.strftime('%Y-%m-%d %H:%M')} IST\n"
        f"📈 Open: {len(open_rows)}/{MAX_TRADES} | "
        f"⏳ Waiting: {len(waiting_rows)}/{MAX_WAITING}\n"
        f"💰 Capital deployed: ₹{len(open_rows) * CAPITAL_PER_TRADE:,}\n"
    )
    if trade_lines:
        msg += f"\n<b>── OPEN TRADES ──</b>\n" + "\n\n".join(trade_lines)
    else:
        msg += "\n📭 No open trades currently"
    if exit_lines:
        msg += f"\n\n<b>── TODAY'S EXITS ──</b>\n" + "\n".join(exit_lines)
        msg += f"\n   <b>Today P/L: ₹{total_exit_pl:+,.0f}</b>"
    if wait_lines:
        msg += f"\n\n<b>── TOP WAITING ──</b>\n" + "\n".join(wait_lines)
    msg += "\n\n<i>Sent on demand via daily_summary mode</i>"

    # Daily summary → free public channel only
    ok = send_tg(msg)
    print(f"[SUMMARY] {'✅ Sent' if ok else '❌ Failed'} | Open={len(open_rows)}")


# ── ENTRY POINT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mode = os.environ.get("BOT_MODE", "trade").strip().lower()
    print(f"[MODE] {mode}")

    if mode == "test_telegram":
        run_test_telegram()
    elif mode == "daily_summary":
        run_daily_summary()
    elif mode == "weekly_summary":
        run_weekly_summary()
    else:
        run_trading_cycle()
