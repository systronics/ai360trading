"""
AI360 TRADING BOT — FINAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE: trading_bot.py  (replace content, keep filename)

COMPLETE CHANGE LOG vs original v7:

1. SYSTEM CONTROL: Q2/Q4 → T2/T4
   AlertLog col T = SYSTEM CONTROL (T2=YES/NO switch, T4=memory)
   Col Q is now ATH Warning (formula). Reading Q2 would read formula
   result not YES/NO — automation would never turn on.

2. pad() SIZE: 17 → 20
   AlertLog now has 20 columns A–T. Old pad(17) caused index errors
   when Google Sheets returned fewer cols than expected.

3. RISK ₹ CALCULATION FIXED in entry alert:
   Old: (cp - init_sl) × 1  = risk per 1 share only (wrong!)
   New: (cp - init_sl) × round(10000/cp) = actual rupee risk on ₹10k
   Entry alert now also shows quantity of shares.

4. TRAILING SL — Professional 3-step Chandelier:
   +1% gain → SL to breakeven (can never lose)
   +2% gain → SL locks 1% profit
   +3%+ gain → SL = Price - 1.5×ATR (trend trail)
   SL NEVER moves down.

5. 3-DAY MINIMUM HOLD:
   Days < 3 AND loss < 5% → HOLD (normal noise, wait)
   Days < 3 AND loss > 5% → EXIT (thesis broken)
   Days ≥ 3 → normal TSL/target rules

6. ENTRY PRICE by Python, not AppScript:
   AppScript leaves L and M blank for WAITING rows.
   Python writes entry price when marking TRADED.
   P/L% calculated from actual entry, not signal price.

7. MAX 5 TRADES hard cap enforced in Python too.

8. HISTORY gets 9 new columns (I–R):
   Exit Reason, Trade Type, Initial SL, TSL at Exit,
   Max Price, ATR at Entry, Days Held, Capital ₹, P/L ₹, Options Note

9. INITIAL SL (col H) never changed by Python.
   TRAILING SL (col O) updated by Python as price rises.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALERTLOG COLUMN MAP (0-based):
  A=0  Signal Time       B=1  Symbol
  C=2  Live Price        D=3  Priority Score
  E=4  Trade Type        F=5  Strategy
  G=6  Breakout Stage    H=7  Initial SL  (AppScript writes ONCE)
  I=8  Target            J=9  RR Ratio
  K=10 Trade Status      L=11 Entry Price  (Python writes when TRADED)
  M=12 Entry Time        N=13 Days in Trade (formula, Python ignores)
  O=14 Trailing SL       P=15 P/L% (formula, Python ignores)
  Q=16 ATH Warning       R=17 Risk ₹
  S=18 Position Size     T=19 SYSTEM CONTROL (T2=switch, T4=memory)

HISTORY COLUMNS (A–R):
  A  Symbol        B  Entry Date    C  Entry Price   D  Exit Date
  E  Exit Price    F  P/L%          G  Result         H  Strategy
  I  Exit Reason   J  Trade Type    K  Initial SL     L  TSL at Exit
  M  Max Price     N  ATR at Entry  O  Days Held      P  Capital ₹
  Q  Profit/Loss ₹ R  Options Note

APPSCRIPT HANDSHAKE:
  AppScript → K="⏳ WAITING", H=InitialSL, I=Target, L="", M=""
  Python    → reads C (live price), writes K="🟢 TRADED (PAPER)"
              writes L=EntryPrice, M=timestamp, O=InitialSL
  Python    → updates O (Trailing SL) as price rises
  Python    → writes K="EXITED" on SL/target hit
  AppScript → removes EXITED row, fills next best candidate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, json, pytz, requests, gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

IST         = pytz.timezone('Asia/Kolkata')
TG_TOKEN    = os.environ.get('TELEGRAM_TOKEN')
TG_CHAT     = os.environ.get('CHAT_ID')
SHEET_NAME  = "Ai360tradingAlgo"

# ── AlertLog column indices (0-based) ────────────────────────────────────────
C_SIGNAL_TIME = 0
C_SYMBOL      = 1
C_LIVE_PRICE  = 2
C_PRIORITY    = 3
C_TRADE_TYPE  = 4
C_STRATEGY    = 5
C_STAGE       = 6
C_INITIAL_SL  = 7   # AppScript writes this ONCE — Python NEVER changes it
C_TARGET      = 8
C_RR          = 9
C_STATUS      = 10
C_ENTRY_PRICE = 11  # Python writes CMP here when marking TRADED
C_ENTRY_TIME  = 12  # Python writes timestamp here when marking TRADED
C_DAYS        = 13  # Formula column — Python does not write here
C_TRAIL_SL    = 14  # Python updates this as price rises
C_PNL         = 15  # Formula column — Python does not write here

# Capital config
CAPITAL_PER_TRADE = 10000
MAX_TRADES        = 5

# Trailing SL thresholds (% gain from entry)
TSL_BREAKEVEN_AT  = 1.0   # +1% → move SL to breakeven
TSL_LOCK1PCT_AT   = 2.0   # +2% → lock 1% profit
TSL_ATR_TRAIL_AT  = 3.0   # +3%+ → trail at Price - 1.5×ATR
TSL_ATR_MULT      = 1.5   # multiplier for ATR-based trail

# Min hold before exit (days) — unless hard loss > this %
MIN_HOLD_DAYS     = 3
HARD_LOSS_PCT     = 5.0   # override min hold if loss exceeds this %


# ── HELPERS ──────────────────────────────────────────────────────────────────

def send_tg(msg: str) -> bool:
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"},
            timeout=15
        )
        if r.status_code != 200:
            print(f"[TG FAIL] {r.status_code}: {r.text[:150]}")
            return False
        return True
    except Exception as e:
        print(f"[TG ERROR] {e}")
        return False


def to_f(val) -> float:
    try:
        return float(str(val).replace(',', '').replace('₹', '').replace('%', '').strip())
    except:
        return 0.0


def sym_key(sym: str) -> str:
    return str(sym).replace(':', '_').replace(' ', '_').strip()


def pad(r: list, n: int = 20) -> list:
    # AlertLog has 20 cols A-T. Python reads A-P (0-15), T4 read via acell()
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
        # Date flags (YYYY-MM-DD_XXX) — keep only last 30 days
        if len(p) > 10 and p[4] == '-' and p[7] == '-':
            if p[:10] >= cutoff:
                kept.append(p)
        else:
            kept.append(p)  # _EX, _ENTRY, _TSL_*, _TRADED kept always
    return ','.join(kept)


def is_market_hours(now: datetime) -> bool:
    if now.weekday() >= 5:
        return False
    mins = now.hour * 60 + now.minute
    return (9 * 60 + 15) <= mins <= (15 * 60 + 30)


def get_tsl(mem: str, key: str) -> float:
    """Get last saved Trailing SL value for a symbol from memory."""
    prefix = f"{key}_TSL_"
    for p in mem.split(','):
        if p.startswith(prefix):
            try:
                return int(p[len(prefix):]) / 100.0
            except:
                return 0.0
    return 0.0


def set_tsl(mem: str, key: str, price: float) -> str:
    """Save Trailing SL value for a symbol into memory."""
    prefix = f"{key}_TSL_"
    parts  = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{int(round(price * 100))}")
    return ','.join(parts)


def get_max_price(mem: str, key: str) -> float:
    """Get highest seen price for a symbol (for History max_price column)."""
    prefix = f"{key}_MAX_"
    for p in mem.split(','):
        if p.startswith(prefix):
            try:
                return int(p[len(prefix):]) / 100.0
            except:
                return 0.0
    return 0.0


def set_max_price(mem: str, key: str, price: float) -> str:
    """Update highest seen price for a symbol in memory."""
    prefix   = f"{key}_MAX_"
    cur_max  = get_max_price(mem, key)
    if price <= cur_max:
        return mem  # no update needed
    parts = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{int(round(price * 100))}")
    return ','.join(parts)


def calc_new_tsl(cp: float, ent: float, init_sl: float, atr: float) -> float:
    """
    Professional 3-step Chandelier trailing SL for NSE swing trades.
    Returns the new TSL price. Caller ensures it only moves UP.

    Step 1: Gain < +1%  → no trail yet (too early, avoid noise stop-out)
    Step 2: Gain +1–2%  → move SL to breakeven (entry price)
    Step 3: Gain +2–3%  → lock 1% profit above entry
    Step 4: Gain > +3%  → trail at Price - (1.5 × ATR)
    """
    if ent <= 0:
        return init_sl
    gain_pct = ((cp - ent) / ent) * 100

    if gain_pct < TSL_BREAKEVEN_AT:
        return init_sl                                     # Step 1: hold initial SL
    elif gain_pct < TSL_LOCK1PCT_AT:
        return round(ent, 2)                               # Step 2: breakeven
    elif gain_pct < TSL_ATR_TRAIL_AT:
        return round(ent * 1.01, 2)                        # Step 3: lock 1%
    else:
        atr_trail = round(cp - (TSL_ATR_MULT * atr), 2)   # Step 4: ATR trail
        # Never go below entry (never back to a loss after +3%)
        return max(atr_trail, round(ent * 1.01, 2))


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
    """Retrieve ATR saved at entry time."""
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


def options_hint(sym: str, cp: float, atr: float, trade_type: str) -> str:
    """Generate options advisory note for Options Alert trade type."""
    if "Options Alert" not in str(trade_type):
        return ""
    # Estimate expected move = 1.5×ATR (conservative)
    expected_move = round(atr * 1.5, 0)
    strike_ce     = round((cp + atr) / 50) * 50  # nearest 50-strike above
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
    return ss.worksheet("AlertLog"), ss.worksheet("History")


# ── MAIN ─────────────────────────────────────────────────────────────────────

def run_trading_cycle():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    mins  = now.hour * 60 + now.minute

    if now.weekday() >= 5:
        print(f"[SKIP] Weekend ({now.strftime('%A')})")
        return

    # Window: 08:55–15:45 IST
    if not ((8 * 60 + 55) <= mins <= (15 * 60 + 45)):
        print(f"[SKIP] Outside window: {now.strftime('%H:%M')} IST")
        return

    print(f"[START] {now.strftime('%Y-%m-%d %H:%M:%S')} IST")

    log_sheet, hist_sheet = get_sheets()

    mem = clean_mem(str(log_sheet.acell("T4").value or ""))

    # Automation switch T2 — must be YES to run
    if str(log_sheet.acell("T2").value or "").strip().upper() != "YES":
        print("[SKIP] Automation OFF (T2 != YES)")
        log_sheet.update_acell("T4", mem)
        return

    all_data   = log_sheet.get_all_values()
    # Rows 2–11 (10 rows = 5 max traded + 5 waiting)
    trade_zone = [pad(list(r)) for r in all_data[1:11]]

    traded_rows = []
    for i, r in enumerate(trade_zone):
        status = str(r[C_STATUS]).upper()
        if "TRADED" in status and "EXITED" not in status:
            traded_rows.append((i + 2, r))  # (sheet_row_1based, data)

    print(f"[INFO] Active trades: {len(traded_rows)}/{MAX_TRADES}")

    # ─────────────────────────────────────────────────────────────────────────
    # 1. GOOD MORNING  09:00–09:10 IST
    # ─────────────────────────────────────────────────────────────────────────
    if now.hour == 9 and now.minute <= 10 and f"{today}_AM" not in mem:
        lines = []
        for _, r in traded_rows:
            sym  = r[C_SYMBOL]
            cp   = to_f(r[C_LIVE_PRICE])
            ent  = to_f(r[C_ENTRY_PRICE])
            sl   = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
            tgt  = to_f(r[C_TARGET])
            ttype = str(r[C_TRADE_TYPE])
            if not price_sanity(sym, cp, ent):
                continue
            pnl      = (cp - ent) / ent * 100
            em       = "🟢" if pnl >= 0 else "🔴"
            risk_pct = abs((sl - ent) / ent * 100) if ent > 0 else 0
            lines.append(
                f"{em} <b>{sym}</b> [{ttype}]\n"
                f"   Entry ₹{ent:.2f} | Now ₹{cp:.2f} | <b>P/L {pnl:+.2f}%</b>\n"
                f"   TSL ₹{sl:.2f} | Target ₹{tgt:.2f}"
            )
        body = "\n\n".join(lines) if lines else "📭 No open trades"
        if send_tg(
            f"🌅 <b>GOOD MORNING — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ System: Online | Trades: {len(lines)}/{MAX_TRADES}\n\n"
            f"{body}"
        ):
            mem += f",{today}_AM"

    # ─────────────────────────────────────────────────────────────────────────
    # 2. MARKET HOURS — Core Trading Logic
    # ─────────────────────────────────────────────────────────────────────────
    if is_market_hours(now):
        exit_alerts      = []
        trail_alerts     = []
        entry_alerts     = []
        tsl_cell_updates = []   # (sheet_row, new_tsl)
        entry_writes     = []   # (sheet_row, entry_price, entry_time)

        # ── Step A: Mark WAITING→TRADED if conditions met ──────────────────
        # Python is the one that "executes" the trade by writing Entry Price
        for i, r in enumerate(trade_zone):
            status = str(r[C_STATUS]).upper()
            sym    = str(r[C_SYMBOL]).strip()
            if "WAITING" not in status or not sym:
                continue

            # Count currently active trades
            active_count = sum(
                1 for _, ar in traded_rows
                if "TRADED" in str(ar[C_STATUS]).upper()
                and "EXITED" not in str(ar[C_STATUS]).upper()
            )
            if active_count >= MAX_TRADES:
                break  # Hard cap — no more entries

            cp       = to_f(r[C_LIVE_PRICE])
            init_sl  = to_f(r[C_INITIAL_SL])
            target   = to_f(r[C_TARGET])
            priority = str(r[C_PRIORITY])
            stage    = str(r[C_STAGE])
            strat    = str(r[C_STRATEGY])
            ttype    = str(r[C_TRADE_TYPE])

            if cp <= 0:
                continue

            sheet_row = i + 2
            etime     = now.strftime('%Y-%m-%d %H:%M:%S')
            key       = sym_key(sym)

            # Write TRADED status + Entry Price + Entry Time + Initial TSL
            log_sheet.update_cell(sheet_row, C_STATUS + 1, "🟢 TRADED (PAPER)")
            log_sheet.update_cell(sheet_row, C_ENTRY_PRICE + 1, cp)
            log_sheet.update_cell(sheet_row, C_ENTRY_TIME + 1, etime)
            log_sheet.update_cell(sheet_row, C_TRAIL_SL + 1, init_sl)  # TSL starts at Initial SL

            # Recalculate RR from actual entry price
            risk   = cp - init_sl
            reward = target - cp
            rr_num = (reward / risk) if risk > 0 else 0
            log_sheet.update_cell(sheet_row, C_RR + 1, f"1:{rr_num:.1f}")

            # Save ATR in memory (needed for TSL calculation later)
            # ATR was used to compute target: target = entry + ATR*3
            # So ATR ≈ (target - cp) / 3
            atr_est = (target - cp) / 3 if target > cp else 0
            mem = save_atr_to_mem(mem, key, atr_est)
            mem = set_tsl(mem, key, init_sl)
            mem = set_max_price(mem, key, cp)

            # Add to traded_rows for this cycle's TSL monitoring
            updated_r    = list(r)
            updated_r[C_STATUS]      = "🟢 TRADED (PAPER)"
            updated_r[C_ENTRY_PRICE] = cp
            updated_r[C_ENTRY_TIME]  = etime
            updated_r[C_TRAIL_SL]    = init_sl
            traded_rows.append((sheet_row, updated_r))

            # Get options hint if applicable
            atr   = atr_est
            o_hint = options_hint(sym, cp, atr, ttype)
            entry_key = f"{key}_ENTRY"
            mem += f",{entry_key}"

            # Position size and actual risk in rupees
            pos_size   = round(CAPITAL_PER_TRADE / cp) if cp > 0 else 0
            risk_rs    = round(max(0, cp - init_sl) * pos_size)
            reward_rs  = round(max(0, target - cp) * pos_size)

            entry_alerts.append(
                f"🚀 <b>TRADE ENTERED</b>\n\n"
                f"<b>Stock:</b> {sym}\n"
                f"<b>Type:</b> {ttype}\n"
                f"<b>Entry Price:</b> ₹{cp:.2f}\n"
                f"<b>Strategy:</b> {strat} | {stage}\n"
                f"<b>Qty:</b> {pos_size} shares @ ₹{CAPITAL_PER_TRADE:,}\n"
                f"<b>Initial SL:</b> ₹{init_sl:.2f} (Risk: ₹{risk_rs:,})\n"
                f"<b>Target:</b> ₹{target:.2f} (Reward: ₹{reward_rs:,})\n"
                f"<b>RR Ratio:</b> 1:{rr_num:.1f}\n"
                f"<b>Priority:</b> {priority}/30"
                f"{o_hint}"
            )
            print(f"[ENTRY] {sym} @ ₹{cp} | Type={ttype} | SL ₹{init_sl} | T ₹{target}")

        # ── Step B: Monitor active trades (TSL + Exit) ─────────────────────
        for sheet_row, r in traded_rows:
            sym       = str(r[C_SYMBOL]).strip()
            if not sym:
                continue

            key       = sym_key(sym)
            cp        = to_f(r[C_LIVE_PRICE])
            init_sl   = to_f(r[C_INITIAL_SL])
            cur_tsl   = to_f(r[C_TRAIL_SL]) or init_sl
            ent       = to_f(r[C_ENTRY_PRICE])
            tgt       = to_f(r[C_TARGET])
            strat     = str(r[C_STRATEGY])
            stage     = str(r[C_STAGE])
            etime     = str(r[C_ENTRY_TIME])
            ttype     = str(r[C_TRADE_TYPE])
            priority  = str(r[C_PRIORITY])

            if not price_sanity(sym, cp, ent):
                continue

            # Update max price seen
            mem = set_max_price(mem, key, cp)

            pnl_pct = (cp - ent) / ent * 100
            atr     = get_atr_from_mem(mem, key)
            if atr <= 0:
                atr = (tgt - ent) / 3 if tgt > ent else ent * 0.02  # fallback

            days_held = calc_hold_days(etime, now)

            # ── Trailing SL update ─────────────────────────────────────────
            new_tsl = calc_new_tsl(cp, ent, init_sl, atr)
            # TSL never goes down
            new_tsl = max(new_tsl, get_tsl(mem, key), cur_tsl)

            if new_tsl > cur_tsl:
                tsl_cell_updates.append((sheet_row, new_tsl))
                trail_alerts.append(
                    f"🔒 <b>{sym}</b> | LTP ₹{cp:.2f} ({pnl_pct:+.2f}%)\n"
                    f"   Trail SL: ₹{cur_tsl:.2f} → <b>₹{new_tsl:.2f}</b> "
                    f"({'Breakeven' if abs(new_tsl-ent)<0.5 else '+1% locked' if abs(new_tsl-ent*1.01)<0.5 else 'ATR trail'})"
                )
                mem = set_tsl(mem, key, new_tsl)
                print(f"[TSL] {sym}: ₹{cur_tsl:.2f}→₹{new_tsl:.2f} | LTP ₹{cp:.2f}")

            # ── Exit Logic ─────────────────────────────────────────────────
            ex_flag    = f"{key}_EX"
            tsl_hit    = (new_tsl > 0 and cp <= new_tsl)
            target_hit = (tgt > 0 and cp >= tgt)

            # 3-day minimum hold rule:
            # Only bypass if HARD loss > HARD_LOSS_PCT % (thesis clearly broken)
            hard_loss = pnl_pct < -HARD_LOSS_PCT  # e.g. -5%
            skip_exit = (days_held < MIN_HOLD_DAYS and not target_hit and not hard_loss)

            if (tsl_hit or target_hit) and ex_flag not in mem and not skip_exit:
                exit_reason = "🎯 TARGET HIT"   if target_hit else \
                              "🔒 TRAILING SL"   if new_tsl > init_sl else \
                              "🚨 INITIAL SL HIT"
                result_sym  = "WIN ✅" if (target_hit or pnl_pct > 0) else "LOSS 🔴"
                hold_str    = calc_hold_str(etime, now)
                max_price   = get_max_price(mem, key)
                pl_rupees   = round((cp - ent) / ent * CAPITAL_PER_TRADE, 2)
                o_note      = options_hint(sym, ent, atr, ttype).replace('\n\n📊 <b>OPTIONS ADVISORY</b>', '').strip() if atr > 0 else ""

                exit_alerts.append(
                    f"{'🎯' if target_hit else '⚡'} <b>{exit_reason}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📌 <b>{sym}</b> [{ttype}]\n"
                    f"   Entry ₹{ent:.2f} → Exit ₹{cp:.2f}\n"
                    f"   P/L: <b>{pnl_pct:+.2f}%</b> = <b>₹{pl_rupees:+.0f}</b>\n"
                    f"   Hold: {hold_str} | Max seen: ₹{max_price:.2f}\n"
                    f"   Strategy: {strat}"
                )

                # Write full History row (18 columns A–R)
                hist_sheet.append_row([
                    sym,                              # A Symbol
                    etime[:10],                       # B Entry Date
                    ent,                              # C Entry Price
                    now.strftime('%Y-%m-%d'),         # D Exit Date
                    cp,                               # E Exit Price
                    f"{pnl_pct:.2f}%",               # F P/L%
                    result_sym,                       # G Result
                    strat,                            # H Strategy
                    exit_reason,                      # I Exit Reason    [NEW]
                    ttype,                            # J Trade Type     [NEW]
                    init_sl,                          # K Initial SL     [NEW]
                    new_tsl,                          # L TSL at Exit    [NEW]
                    max_price if max_price > 0 else cp, # M Max Price   [NEW]
                    round(atr, 2),                    # N ATR at Entry   [NEW]
                    days_held,                        # O Days Held      [NEW]
                    CAPITAL_PER_TRADE,                # P Capital ₹      [NEW]
                    pl_rupees,                        # Q Profit/Loss ₹  [NEW]
                    o_note[:100] if o_note else "—",  # R Options Note   [NEW]
                ])

                log_sheet.update_cell(sheet_row, C_STATUS + 1, "EXITED")
                mem += f",{ex_flag}"
                print(f"[EXIT] {sym} | {result_sym} | {pnl_pct:+.2f}% | ₹{pl_rupees:+.0f}")

            elif tsl_hit and skip_exit:
                # Min hold protection active — send advisory but don't exit
                print(f"[HOLD] {sym}: SL touched but day {days_held} < {MIN_HOLD_DAYS} min hold. Watching.")
                if f"{key}_HOLD_WARN" not in mem:
                    send_tg(
                        f"⚠️ <b>MIN HOLD ACTIVE</b>\n"
                        f"<b>{sym}</b> touched SL ₹{new_tsl:.2f} but only {days_held} days in trade.\n"
                        f"Holding until day {MIN_HOLD_DAYS} unless loss exceeds {HARD_LOSS_PCT}%.\n"
                        f"Current P/L: {pnl_pct:+.2f}%"
                    )
                    mem += f",{key}_HOLD_WARN"

        # Batch write TSL updates
        if tsl_cell_updates:
            cells = []
            for (sr, new_tsl) in tsl_cell_updates:
                c       = log_sheet.cell(sr, C_TRAIL_SL + 1)  # col O
                c.value = new_tsl
                cells.append(c)
            log_sheet.update_cells(cells)
            print(f"[TSL WRITE] {len(cells)} updates")

        # Send Telegram alerts
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
        for alert in entry_alerts:
            send_tg(alert)

    # ─────────────────────────────────────────────────────────────────────────
    # 3. MID-DAY PULSE  12:28–12:38 IST
    # ─────────────────────────────────────────────────────────────────────────
    if now.hour == 12 and 28 <= now.minute <= 38 and f"{today}_NOON" not in mem:
        fresh      = log_sheet.get_all_values()
        live_rows  = [
            pad(list(r)) for r in fresh[1:11]
            if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
            and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        ]
        wins = losses = 0
        lines = []
        for r in live_rows:
            sym  = r[C_SYMBOL]
            cp   = to_f(r[C_LIVE_PRICE])
            ent  = to_f(r[C_ENTRY_PRICE])
            tsl  = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
            ttype = str(r[C_TRADE_TYPE])
            if not price_sanity(sym, cp, ent):
                continue
            pnl = (cp - ent) / ent * 100
            em  = "🟢" if pnl >= 0 else "🔴"
            if pnl >= 0: wins += 1
            else:        losses += 1
            lines.append(f"{em} <b>{sym}</b> [{ttype}]: {pnl:+.2f}% | TSL ₹{tsl:.2f}")

        if send_tg(
            f"☀️ <b>MID-DAY PULSE — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Open: {len(lines)} | 🟢 {wins} | 🔴 {losses}\n\n"
            + ("\n".join(lines) if lines else "📭 No open trades")
        ):
            mem += f",{today}_NOON"

    # ─────────────────────────────────────────────────────────────────────────
    # 4. MARKET CLOSE SUMMARY  15:30–15:45 IST
    # ─────────────────────────────────────────────────────────────────────────
    if now.hour == 15 and 30 <= now.minute <= 45 and f"{today}_PM" not in mem:
        hist_data   = hist_sheet.get_all_values()
        today_exits = [r for r in hist_data[1:] if len(r) >= 7 and r[3] == today]
        wins_today  = [r for r in today_exits if "WIN"  in str(r[6]).upper()]
        loss_today  = [r for r in today_exits if "LOSS" in str(r[6]).upper()]

        total_pl = sum(to_f(r[16]) for r in today_exits if len(r) > 16)

        exit_lines = []
        for r in today_exits:
            em = "✅" if "WIN" in str(r[6]).upper() else "❌"
            pl_r = f"₹{to_f(r[16]):+.0f}" if len(r) > 16 else ""
            exit_lines.append(f"  {em} <b>{r[0]}</b>: {r[5]} {pl_r} (hold {r[14] if len(r)>14 else '?'}d)")

        fresh3    = log_sheet.get_all_values()
        open_rows = [
            pad(list(r)) for r in fresh3[1:11]
            if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
            and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        ]
        open_lines = []
        for r in open_rows:
            sym  = r[C_SYMBOL]
            cp   = to_f(r[C_LIVE_PRICE])
            ent  = to_f(r[C_ENTRY_PRICE])
            tsl  = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
            if not price_sanity(sym, cp, ent):
                continue
            pnl = (cp - ent) / ent * 100
            em  = "🟢" if pnl >= 0 else "🔴"
            open_lines.append(f"  {em} <b>{sym}</b>: {pnl:+.2f}% | TSL ₹{tsl:.2f}")

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

        if send_tg(msg):
            mem += f",{today}_PM"

    # ─────────────────────────────────────────────────────────────────────────
    # 5. SAVE MEMORY — always last
    # ─────────────────────────────────────────────────────────────────────────
    log_sheet.update_acell("T4", mem)
    print(f"[DONE] {now.strftime('%H:%M:%S')} IST | mem={len(mem)} chars")


if __name__ == "__main__":
    run_trading_cycle()
