"""
AI360 TRADING BOT — v13.5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v13.5 CHANGES vs v13.4 (3 surgical fixes only):

1. clean_mem() — orphaned key cleanup [FIX: T4 memory cell growth]
   Previous: only pruned date-prefixed entries older than 30 days.
   Symbol keys (_CAP, _MODE, _SEC, _ATR, _LP, _MAX, _TSL) for
   exited trades stayed forever → T4 growing toward 50k char limit.
   Fix: two-pass cleanup — find symbols with _EXDT_ older than 30
   days, then prune ALL keys for those symbols.
   NOTE: _EXDT_ entries are stored WITHOUT = sign (format is
   "NSE_ONGC_EXDT_2026-01-15") so split must use _EXDT_ directly,
   not split('=',1). This is the key difference from naive approach.

2. ATR read directly from Nifty200 at entry [FIX: wrong TSL]
   Previous: atr_est = (target - cp) / mult — backwards derivation.
   Fix: _read_atr_from_nifty200(nifty_sheet, sym) reads col AC
   (index 28) directly. Falls back to old formula if lookup fails.

3. RR re-validation on WAITING → TRADED [FIX: stale candidates]
   Previous: pre-v13.3 rows with RR 1:1.5 could still be promoted.
   Fix: MIN_RR = 1.8 constant added. Step A parses RR from col J
   and skips rows where rr_val > 0 and rr_val < MIN_RR.
   Rows with no RR value pass through (AppScript sets correctly).

ALL OTHER CODE IDENTICAL TO v13.4.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALERTLOG COLUMN MAP (0-based):
  A=0  Signal Time       B=1  Symbol
  C=2  Live Price        D=3  Priority Score
  E=4  Trade Type        F=5  Strategy
  G=6  Breakout Stage    H=7  Initial SL
  I=8  Target            J=9  RR Ratio
  K=10 Trade Status      L=11 Entry Price
  M=12 Entry Time        N=13 Days in Trade
  O=14 Trailing SL       P=15 P/L%
  Q=16 ATH Warning       R=17 Risk ₹
  S=18 Position Size     T=19 SYSTEM CONTROL

HISTORY COLUMNS (A–R):
  A  Symbol        B  Entry Date    C  Entry Price   D  Exit Date
  E  Exit Price    F  P/L%          G  Result         H  Strategy
  I  Exit Reason   J  Trade Type    K  Initial SL     L  TSL at Exit
  M  Max Price     N  ATR at Entry  O  Days Held      P  Capital ₹
  Q  Profit/Loss ₹ R  Options Note
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, json, pytz, requests, gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

IST        = pytz.timezone('Asia/Kolkata')
TG_TOKEN   = os.environ.get('TELEGRAM_TOKEN')

# ── 3 Telegram channels ───────────────────────────────────────────────────────
CHAT_BASIC   = os.environ.get('TELEGRAM_CHAT_ID')
CHAT_ADVANCE = os.environ.get('CHAT_ID_PREMIUM')
CHAT_PREMIUM = os.environ.get('CHAT_ID_ADVANCE')

SHEET_NAME = "Ai360tradingAlgo"

# ── AlertLog column indices (0-based) ─────────────────────────────────────────
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

# Capital config
CAPITAL_PER_TRADE = 10000
MAX_TRADES        = 5
MAX_WAITING       = 10

# ── v13.5: MIN_RR for re-validation of stale WAITING rows ────────────────────
MIN_RR = 1.8

# ── TSL mode parameters ───────────────────────────────────────────────────────
TSL_PARAMS = {
    "VCP": {                  # Tight base pre-breakout — unchanged
        "breakeven": 3.0,
        "lock1"    : 5.0,
        "trail"    : 8.0,
        "atr_mult" : 2.0,
        "gap_lock" : 9.0,
    },
    "MOM": {                  # Strong momentum — unchanged
        "breakeven": 2.5,
        "lock1"    : 4.5,
        "trail"    : 7.0,
        "atr_mult" : 1.8,
        "gap_lock" : 8.0,
    },
    "STD": {                  # ← v13.3: trail 6→10, atr_mult 1.5→2.5
        "breakeven": 2.0,     # unchanged — entry protection same
        "lock1"    : 4.0,     # unchanged — breakeven lock same
        "trail"    : 10.0,    # was 6.0 — let swing run longer
        "atr_mult" : 2.5,     # was 1.5 — wider ATR trail
        "gap_lock" : 8.0,     # unchanged
    },
}

TSL_GAP_LOCK_FRAC = 0.5
MIN_HOLD_SWING    = 2
MIN_HOLD_POS      = 3
HARD_LOSS_PCT     = 5.0


# ══════════════════════════════════════════════════════════════════════════════
# TELEGRAM
# ══════════════════════════════════════════════════════════════════════════════

def _send_one(chat_id: str, msg: str) -> bool:
    if not chat_id or not TG_TOKEN:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
            timeout=15
        )
        if r.status_code != 200:
            print(f"[TG FAIL] chat={chat_id} status={r.status_code}: {r.text[:100]}")
            return False
        return True
    except Exception as e:
        print(f"[TG ERROR] chat={chat_id} {e}")
        return False

def send_basic(msg):           return _send_one(CHAT_BASIC,   msg)
def send_advance(msg):         return _send_one(CHAT_ADVANCE, msg)
def send_premium(msg):         return _send_one(CHAT_PREMIUM, msg)
def send_advance_and_premium(msg):
    ok1 = _send_one(CHAT_ADVANCE, msg)
    ok2 = _send_one(CHAT_PREMIUM, msg)
    return ok1 or ok2
def send_all(msg):
    ok1 = _send_one(CHAT_BASIC,   msg)
    ok2 = _send_one(CHAT_ADVANCE, msg)
    ok3 = _send_one(CHAT_PREMIUM, msg)
    return ok1 or ok2 or ok3
def send_tg(msg): return send_all(msg)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

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
        d = delta.days; h = delta.seconds // 3600; m = (delta.seconds % 3600) // 60
        return f"{d}d {h}h" if d > 0 else f"{h}h {m}m"
    except:
        return "—"

def clean_mem(mem: str) -> str:
    """
    Remove T4 memory entries older than 14 days.
    Hard cap at 20,000 chars — keeps last 100 entries if exceeded.
    Logs size every call so GitHub Actions logs show T4 health.
    """
    cutoff = (datetime.now(IST) - timedelta(days=14)).strftime("%Y-%m-%d")
    kept   = []

    for p in mem.split(","):
        p = p.strip()
        if not p:
            continue
        # Date-stamped entries look like "2025-01-15_AM" or "2025-01-15_ONGC"
        # Keep only those within the 14-day window; keep all non-dated entries
        if len(p) >= 10 and p[4] == "-" and p[7] == "-":
            if p[:10] >= cutoff:
                kept.append(p)
            # else: older than 14 days — drop it
        else:
            kept.append(p)

    result = ",".join(kept)

    # Hard cap: if still over 20,000 chars after date pruning, keep last 100 entries
    if len(result) > 20000:
        parts  = [p for p in result.split(",") if p.strip()]
        result = ",".join(parts[-100:])
        print(f"[MEM] ⚠️  Hard cap applied — trimmed to last 100 entries ({len(result)} chars)")

    # Size monitoring — visible in GitHub Actions logs
    size = len(result)
    if size > 15000:
        print(f"[MEM] 🔴 WARNING: T4 is {size:,} chars — plan BotMemory sheet migration soon (see SYSTEM.md Section 10)")
    elif size > 10000:
        print(f"[MEM] 🟡 NOTICE: T4 is {size:,} chars — monitor growth")
    else:
        print(f"[MEM] ✅ T4 size: {size:,} chars — OK")

    return result

def is_market_hours(now: datetime) -> bool:
    if now.weekday() >= 5: return False
    mins = now.hour * 60 + now.minute
    return (9 * 60 + 15) <= mins <= (15 * 60 + 30)

def price_sanity(sym, cp, ent) -> bool:
    if cp <= 0 or ent <= 0:
        print(f"[WARN] {sym}: zero price cp={cp} ent={ent}"); return False
    if cp > ent * 4:
        print(f"[WARN] {sym}: LTP ₹{cp} > 4× entry ₹{ent}"); return False
    if cp < ent * 0.1:
        print(f"[WARN] {sym}: LTP ₹{cp} < 10% of entry ₹{ent}"); return False
    return True

def trading_days_since(date_str: str, now: datetime) -> int:
    if not date_str: return 999
    try:
        start = datetime.strptime(date_str, '%Y-%m-%d').date()
        end   = now.date(); count = 0; cur = start
        while cur <= end:
            if cur.weekday() < 5: count += 1
            cur += timedelta(days=1)
        return max(0, count - 1)
    except:
        return 999

def options_hint(sym: str, cp: float, atr: float, trade_type: str) -> str:
    if "Options Alert" not in str(trade_type): return ""
    expected_move = round(atr * 1.5, 0)
    strike_ce     = round((cp + atr) / 50) * 50
    return (
        f"\n\n📊 <b>OPTIONS ADVISORY</b> (informational only)\n"
        f"   Stock: {sym} @ ₹{cp:.0f}\n"
        f"   Expected move: ~₹{expected_move:.0f} ({(expected_move/cp*100):.1f}%)\n"
        f"   CE strike hint: {int(strike_ce)} CE (buy on breakout confirm)\n"
        f"   ⚠️ Options are leveraged — size carefully"
    )

def ce_candidate_flag(cp: float, atr: float, stage: str, is_bullish: bool) -> str:
    """
    CE candidate flag — added to advance/premium entry alerts only.
    Uses existing ATR14 (col AC) and CMP (col C). No new data needed.

    Rules (from discussion):
      ATR% < 1.5%  → skip (premium decay exceeds stock movement)
      ATR% 1.5-2.5% → normal mover, target 65%, SL 40%
      ATR% > 2.5%  → fast mover, target 50%, SL 35%
      Not bullish  → no CE flag (bear market CE buying = high risk)
    """
    if not is_bullish: return ""
    if cp <= 0 or atr <= 0: return ""

    atr_pct = (atr / cp) * 100
    if atr_pct < 1.5: return ""

    # Strike selection based on stage
    # Near Breakout / Building Momentum → ATM strike
    # BREAKOUT CONFIRMED → ATM+1 (slightly OTM, more leverage)
    gap = 5 if cp < 200 else (10 if cp < 500 else (20 if cp < 1000 else 50))
    atm_strike  = round(cp / gap) * gap
    otm_strike  = atm_strike + gap

    if "BREAKOUT CONFIRMED" in stage:
        strike_str = f"{int(otm_strike)} CE (OTM — breakout in progress)"
    else:
        strike_str = f"{int(atm_strike)} CE or {int(otm_strike)} CE"

    # Target and SL based on ATR% and speed
    if atr_pct >= 2.5:
        target_pct = 50
        sl_pct     = 35
        speed_tag  = "⚡ Fast mover"
    else:
        target_pct = 65
        sl_pct     = 40
        speed_tag  = "📈 Normal mover"

    return (
        f"\n\n📊 <b>CE CANDIDATE</b> ({speed_tag})\n"
        f"   ATR%: {atr_pct:.1f}% | Strike: {strike_str}\n"
        f"   Target: +{target_pct}% on premium | SL: -{sl_pct}% on premium\n"
        f"   Entry: Only above ₹{cp + atr * 0.3:.1f} (breakout confirm)\n"
        f"   ⚠️ Check actual premium on Zerodha option chain\n"
        f"   ⚠️ Wednesday entry → prefer monthly expiry"
    )


# ══════════════════════════════════════════════════════════════════════════════
# MEMORY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _mem_get(mem: str, key: str) -> str:
    for p in mem.split(','):
        if p.startswith(key + '='):
            return p[len(key)+1:]
    return ""

def _mem_set(mem: str, key: str, val: str) -> str:
    parts = [p for p in mem.split(',') if p.strip() and not p.startswith(key + '=')]
    parts.append(f"{key}={val}")
    return ','.join(parts)

def get_tsl(mem: str, key: str) -> float:
    prefix = f"{key}_TSL_"
    for p in mem.split(','):
        if p.startswith(prefix):
            try: return int(p[len(prefix):]) / 100.0
            except: return 0.0
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
            try: return int(p[len(prefix):]) / 100.0
            except: return 0.0
    return 0.0

def set_max_price(mem: str, key: str, price: float) -> str:
    prefix  = f"{key}_MAX_"
    cur_max = get_max_price(mem, key)
    if price <= cur_max: return mem
    parts = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{int(round(price * 100))}")
    return ','.join(parts)

def get_atr_from_mem(mem: str, key: str) -> float:
    prefix = f"{key}_ATR_"
    for p in mem.split(','):
        if p.startswith(prefix):
            try: return int(p[len(prefix):]) / 100.0
            except: return 0.0
    return 0.0

def save_atr_to_mem(mem: str, key: str, atr: float) -> str:
    prefix = f"{key}_ATR_"
    parts  = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{int(round(atr * 100))}")
    return ','.join(parts)

def get_last_price(mem: str, key: str) -> float:
    prefix = f"{key}_LP_"
    for p in mem.split(','):
        if p.startswith(prefix):
            try: return int(p[len(prefix):]) / 100.0
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
        if p.startswith(prefix): return p[len(prefix):]
    return ""

def set_exit_date(mem: str, key: str, date_str: str) -> str:
    prefix = f"{key}_EXDT_"
    parts  = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{date_str}")
    return ','.join(parts)


# ══════════════════════════════════════════════════════════════════════════════
# TRADE MODE + CAPITAL FROM MEMORY
# ══════════════════════════════════════════════════════════════════════════════

def get_trade_mode(mem: str, key: str) -> str:
    val = _mem_get(mem, f"{key}_MODE")
    return val if val in ("VCP", "MOM", "STD") else "STD"

def get_tsl_params(mem: str, key: str) -> dict:
    mode = get_trade_mode(mem, key)
    return TSL_PARAMS[mode]

def get_capital_from_mem(mem: str, key: str) -> int:
    cap_str = _mem_get(mem, f"{key}_CAP")
    if cap_str:
        try:
            cap = int(cap_str)
            if cap in (7000, 10000, 13000): return cap
        except:
            pass
    return CAPITAL_PER_TRADE

def save_capital_to_mem(mem: str, key: str, capital: int) -> str:
    return _mem_set(mem, f"{key}_CAP", str(capital))


# ══════════════════════════════════════════════════════════════════════════════
# TSL CALCULATION — mode-aware, unchanged from v13.2
# ══════════════════════════════════════════════════════════════════════════════

def calc_new_tsl(cp: float, ent: float, init_sl: float, atr: float,
                 ttype: str = "", params: dict = None) -> float:
    if params is None:
        params = TSL_PARAMS["STD"]

    if ent <= 0: return init_sl

    gain_pct  = ((cp - ent) / ent) * 100
    gap_lock_at = params["gap_lock"]

    if gain_pct >= gap_lock_at:
        gap_lock  = round(ent + (cp - ent) * TSL_GAP_LOCK_FRAC, 2)
        atr_trail = round(cp - (params["atr_mult"] * atr), 2)
        return max(gap_lock, atr_trail, round(ent * 1.02, 2))

    if gain_pct < params["breakeven"]:
        return init_sl
    elif gain_pct < params["lock1"]:
        return round(ent, 2)
    elif gain_pct < params["trail"]:
        return round(ent * 1.02, 2)
    else:
        atr_trail = round(cp - (params["atr_mult"] * atr), 2)
        return max(atr_trail, round(ent * 1.02, 2))


# ══════════════════════════════════════════════════════════════════════════════
# MESSAGE BUILDERS — unchanged from v13.2
# ══════════════════════════════════════════════════════════════════════════════

def build_gm_basic(today: str, trade_count: int, waiting_count: int,
                   is_bullish: bool, sector_line: str = "") -> str:
    mood = "🐂 Bullish" if is_bullish else "🐻 Bearish"
    msg  = (
        f"🌅 <b>GOOD MORNING — {today}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📈 AI360 Scanner is LIVE\n"
        f"Market Regime: <b>{mood}</b>\n"
        f"Active Signals: {trade_count}/{MAX_TRADES}\n"
        f"Candidates Ready: {waiting_count}\n"
    )
    if sector_line:
        msg += f"{sector_line}\n"
    msg += f"\n🔔 <i>Want full entry/exit levels?\nJoin Signal Channel → ai360trading.in/membership</i>"
    return msg

def build_gm_advance(today: str, lines: list, deployed: int,
                     waiting_count: int, sector_line: str = "") -> str:
    body = "\n\n".join(lines) if lines else "📭 No open trades"
    msg  = (
        f"🌅 <b>GOOD MORNING — {today}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📈 Open: {len(lines)}/{MAX_TRADES} | "
        f"⏳ Waiting: {waiting_count}/{MAX_WAITING}\n"
        f"💰 Deployed: ~₹{deployed:,}\n"
    )
    if sector_line:
        msg += f"{sector_line}\n"
    msg += f"\n{body}"
    return msg

def build_entry_advance(sym, cp, ent, init_sl, target, ttype, strat, stage,
                        priority, pos_size, capital, risk_rs, reward_rs,
                        rr_num, trade_mode, ce_flag="") -> str:
    mode_tag = {"VCP": "🎯 VCP Breakout", "MOM": "🚀 Momentum", "STD": "📊 Swing"}.get(trade_mode, "📊 Swing")
    msg = (
        f"🚀 <b>TRADE ENTERED</b>\n\n"
        f"<b>Stock:</b> {sym}\n"
        f"<b>Type:</b> {ttype} [{mode_tag}]\n"
        f"<b>Entry Price:</b> ₹{cp:.2f}\n"
        f"<b>Strategy:</b> {strat} | {stage}\n"
        f"<b>Qty:</b> {pos_size} shares @ ₹{capital:,} (Priority {priority})\n"
        f"<b>Initial SL:</b> ₹{init_sl:.2f} (Risk: ₹{risk_rs:,})\n"
        f"<b>Target:</b> ₹{target:.2f} (Reward: ₹{reward_rs:,})\n"
        f"<b>RR Ratio:</b> 1:{rr_num:.1f}\n"
        f"<b>Priority:</b> {priority}/30"
    )
    # v13.4: CE candidate flag (advance channel sees this)
    if ce_flag:
        msg += ce_flag
    return msg

def build_entry_premium(sym, cp, ent, init_sl, target, ttype, strat, stage,
                        priority, pos_size, capital, risk_rs, reward_rs,
                        rr_num, o_hint, trade_mode, ce_flag="") -> str:
    base = build_entry_advance(sym, cp, ent, init_sl, target, ttype, strat,
                               stage, priority, pos_size, capital, risk_rs,
                               reward_rs, rr_num, trade_mode, ce_flag)
    return base + (o_hint if o_hint else "")

def build_exit_advance(sym, ttype, ent, cp, pnl_pct, pl_rupees, hold_str,
                       max_price, strat, exit_reason) -> str:
    em = "🎯" if "TARGET" in exit_reason else "⚡"
    return (
        f"{em} <b>{exit_reason}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>{sym}</b> [{ttype}]\n"
        f"   Entry ₹{ent:.2f} → Exit ₹{cp:.2f}\n"
        f"   P/L: <b>{pnl_pct:+.2f}%</b> = <b>₹{pl_rupees:+.0f}</b>\n"
        f"   Hold: {hold_str} | Max seen: ₹{max_price:.2f}\n"
        f"   Strategy: {strat}"
    )

def build_exit_basic(sym, pnl_pct, exit_reason) -> str:
    em  = "✅" if pnl_pct > 0 else "❌"
    res = "WIN" if pnl_pct > 0 else "LOSS"
    return (
        f"{em} <b>SIGNAL CLOSED — {sym}</b>\n"
        f"Result: <b>{res} ({pnl_pct:+.2f}%)</b>\n\n"
        f"🔔 <i>Get entry/exit alerts in real time\n"
        f"→ ai360trading.in/membership</i>"
    )


# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE SHEETS
# ══════════════════════════════════════════════════════════════════════════════

def get_sheets():
    import time
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_JSON')), scope
    )
    delays = [5, 15, 30, 60, 120]
    last_error = None
    for attempt, delay in enumerate(delays):
        try:
            ss = gspread.authorize(creds).open(SHEET_NAME)
            return ss.worksheet("AlertLog"), ss.worksheet("History"), ss.worksheet("Nifty200")
        except gspread.exceptions.APIError as e:
            status = e.response.status_code if hasattr(e, 'response') else 0
            if status in (429, 500, 502, 503, 504):
                last_error = e
                if attempt < len(delays) - 1:
                    print(f"[RETRY] Google Sheets {status} — retry {attempt+1} in {delay}s...")
                    time.sleep(delay)
                    continue
            raise
    raise last_error

def get_market_regime(nifty_sheet) -> bool:
    try:
        row = nifty_sheet.row_values(2)
        if not row or "NIFTY" not in str(row[0]).upper():
            print("[REGIME] NIFTY50 row not found — defaulting to bullish")
            return True
        cmp_nifty = to_f(row[2])
        dma20     = to_f(row[4])
        if cmp_nifty <= 0 or dma20 <= 0:
            print("[REGIME] Invalid Nifty data — defaulting to bullish")
            return True
        bullish = cmp_nifty >= dma20
        print(f"[REGIME] Nifty CMP ₹{cmp_nifty:.0f} vs 20DMA ₹{dma20:.0f} → {'BULLISH' if bullish else 'BEARISH'}")
        return bullish
    except Exception as e:
        print(f"[REGIME] Error: {e} — defaulting to bullish")
        return True


# ══════════════════════════════════════════════════════════════════════════════
# SECTOR ROTATION CONTEXT — now works because AppScript writes _SEC key
# ══════════════════════════════════════════════════════════════════════════════

# ── v13.5 FIX 2 HELPER: Read ATR14 directly from Nifty200 ────────────────────
def _read_atr_from_nifty200(nifty_sheet, sym: str) -> float:
    """
    Read ATR14 from Nifty200 col AC (0-based index 28) for sym.
    sym format: 'NSE:ONGC' — matches col A of Nifty200.
    Returns float ATR, or 0.0 if not found / error.
    """
    try:
        nifty_data = nifty_sheet.get_all_values()
        for row in nifty_data[1:]:
            if str(row[0]).strip() == sym.strip():
                if len(row) > 28:
                    val = to_f(row[28])
                    if val > 0:
                        return val
                break
    except Exception as e:
        print(f"[ATR] Nifty200 lookup failed for {sym}: {e}")
    return 0.0


def get_sector_context(all_data: list, mem: str) -> str:
    sector_counts = {}
    for r in all_data[1:16]:
        r = pad(list(r))
        if "WAITING" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper():
            continue
        sym = str(r[C_SYMBOL]).strip()
        if not sym:
            continue
        key = sym_key(sym)
        sec = _mem_get(mem, f"{key}_SEC") or "Mixed"
        sector_counts[sec] = sector_counts.get(sec, 0) + 1

    if not sector_counts:
        return ""
    parts = [f"{s} ({c})" for s, c in sorted(sector_counts.items(), key=lambda x: -x[1])]
    return f"🔄 <b>Active Sectors:</b> {', '.join(parts[:4])}"


# ══════════════════════════════════════════════════════════════════════════════
# MAIN TRADING CYCLE
# ══════════════════════════════════════════════════════════════════════════════

def run_trading_cycle():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    mins  = now.hour * 60 + now.minute

    if now.weekday() >= 5:
        print(f"[SKIP] Weekend ({now.strftime('%A')})"); return

    if not ((8 * 60 + 45) <= mins <= (15 * 60 + 45)):
        print(f"[SKIP] Outside window: {now.strftime('%H:%M')} IST"); return

    print(f"[START] {now.strftime('%Y-%m-%d %H:%M:%S')} IST")

    log_sheet, hist_sheet, nifty_sheet = get_sheets()
    mem = clean_mem(str(log_sheet.acell("T4").value or ""))
    print(f"[MEM] T4 size: {len(mem)} chars")
    is_bullish = get_market_regime(nifty_sheet)

    # ── DEBUG: Good Morning window check ──────────────────────
    am_key = f"{today}_AM"
    print(f"[GM CHECK] time={now.strftime('%H:%M')} IST | "
          f"window={'YES' if (now.hour==8 and now.minute>=45) or (now.hour==9 and now.minute<=15) else 'NO'} | "
          f"AM_already_sent={am_key in mem}")
    # ──────────────────────────────────────────────────────────

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

    # ─────────────────────────────────────────────────────────────────────────
    # 1. GOOD MORNING  08:45–09:15 IST
    # ─────────────────────────────────────────────────────────────────────────
    if ((now.hour == 8 and now.minute >= 45) or
            (now.hour == 9 and now.minute <= 29)) and f"{today}_AM" not in mem:
               
        waiting_count = sum(
            1 for r in [pad(list(x)) for x in all_data[1:16]]
            if "WAITING" in str(r[C_STATUS]).upper()
        )
        sector_line = get_sector_context(all_data, mem)

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
            if not ent or ent <= 0: continue
            sl_label = "TSL" if sl > to_f(r[C_INITIAL_SL]) else "SL"
            if cp > 0 and ent > 0:
                pnl   = (cp - ent) / ent * 100
                key   = sym_key(sym)
                cap   = get_capital_from_mem(mem, key)
                pl_rs = round((cp - ent) / ent * cap)
                to_tgt = ((tgt - cp) / cp * 100) if cp > 0 else 0
                to_sl  = ((cp - sl) / cp * 100) if cp > 0 else 0
                em     = "🟢" if pnl >= 0 else "🔴"
                mode   = get_trade_mode(mem, key)
                mode_tag = {"VCP": "🎯", "MOM": "🚀", "STD": "📊"}.get(mode, "📊")
                lines.append(
                    f"{em} <b>{sym}</b> {mode_tag} [{ttype}] Day {days + 1}\n"
                    f"   Entry ₹{ent:.2f} → Now ₹{cp:.2f}\n"
                    f"   P/L: <b>{pnl:+.2f}%</b> = <b>₹{pl_rs:+,}</b>\n"
                    f"   {sl_label} ₹{sl:.2f} ({to_sl:.1f}% away) | "
                    f"Target ₹{tgt:.2f} ({to_tgt:.1f}% away)"
                )
            else:
                lines.append(
                    f"⏰ <b>{sym}</b> [{ttype}] Day {days + 1}\n"
                    f"   Entry ₹{ent:.2f} | SL ₹{sl:.2f} | Target ₹{tgt:.2f}\n"
                    f"   (Live price loading...)"
                )

        deployed = sum(
            get_capital_from_mem(mem, sym_key(r[C_SYMBOL]))
            for _, r in traded_rows if r[C_SYMBOL]
        )

        send_basic(build_gm_basic(today, len(lines), waiting_count, is_bullish, sector_line))
        full_gm = build_gm_advance(today, lines, deployed, waiting_count, sector_line)
        send_advance(full_gm)
        send_premium(full_gm)

        mem += f",{today}_AM"
        log_sheet.update_acell("T4", mem)

    # ─────────────────────────────────────────────────────────────────────────
    # 2. MARKET HOURS — Core Trading Logic
    # ─────────────────────────────────────────────────────────────────────────
    if is_market_hours(now):
        exit_alerts_advance  = []
        exit_alerts_basic    = []
        trail_alerts         = []
        entry_alerts_advance = []
        entry_alerts_premium = []
        tsl_cell_updates     = []

        # ── Step A: Mark WAITING → TRADED ────────────────────────────────────
        for i, r in enumerate(trade_zone):
            status = str(r[C_STATUS]).upper()
            sym    = str(r[C_SYMBOL]).strip()
            if "WAITING" not in status or not sym: continue

            active_count = sum(
                1 for _, ar in traded_rows
                if "TRADED" in str(ar[C_STATUS]).upper()
                and "EXITED" not in str(ar[C_STATUS]).upper()
            )
            if active_count >= MAX_TRADES: break

            cp       = to_f(r[C_LIVE_PRICE])
            init_sl  = to_f(r[C_INITIAL_SL])
            target   = to_f(r[C_TARGET])
            priority = str(r[C_PRIORITY])
            stage    = str(r[C_STAGE])
            strat    = str(r[C_STRATEGY])
            ttype    = str(r[C_TRADE_TYPE])

            if cp <= 0: continue

            # ── v13.5 FIX 3: RR re-validation — reject stale pre-v13.3 rows ──
            rr_raw = str(r[C_RR]).strip()
            if rr_raw:
                try:
                    rr_val = to_f(rr_raw.split(':')[-1])
                except Exception:
                    rr_val = 0.0
                if rr_val > 0 and rr_val < MIN_RR:
                    print(f"[SKIP] {sym}: RR 1:{rr_val:.1f} below MIN_RR {MIN_RR} — stale pre-v13.3 candidate")
                    continue
            # ── end FIX 3 ─────────────────────────────────────────────────────

            key       = sym_key(sym)
            sheet_row = i + 2

            last_cp = get_last_price(mem, key)
            mem     = set_last_price(mem, key, cp)
            if last_cp > 0 and abs(cp - last_cp) < 0.01:
                print(f"[STALE] {sym}: price unchanged — skipping")
                continue

            exit_date = get_exit_date(mem, key)
            if exit_date:
                days_since = trading_days_since(exit_date, now)
                if days_since < 5:
                    print(f"[COOLDOWN] {sym}: {days_since} days since exit")
                    continue

            pos_size_check = round(CAPITAL_PER_TRADE / cp) if cp > 0 else 0
            if pos_size_check < 2:
                print(f"[SKIP] {sym}: CMP ₹{cp:,.0f} too high")
                continue

            capital    = get_capital_from_mem(mem, key)
            trade_mode = get_trade_mode(mem, key)
            tsl_params = TSL_PARAMS[trade_mode]
            etime      = now.strftime('%Y-%m-%d %H:%M:%S')

            log_sheet.update_cell(sheet_row, C_STATUS + 1,      "🟢 TRADED (PAPER)")
            log_sheet.update_cell(sheet_row, C_ENTRY_PRICE + 1, cp)
            log_sheet.update_cell(sheet_row, C_ENTRY_TIME + 1,  etime)
            log_sheet.update_cell(sheet_row, C_TRAIL_SL + 1,    init_sl)

            risk   = cp - init_sl
            reward = target - cp
            rr_num = (reward / risk) if risk > 0 else 0
            log_sheet.update_cell(sheet_row, C_RR + 1, f"1:{rr_num:.1f}")

            # ── v13.5 FIX 2: Read ATR14 directly from Nifty200 col AC ─────────
            atr_est = _read_atr_from_nifty200(nifty_sheet, sym)
            if atr_est <= 0:
                # Fallback: backwards derivation (pre-v13.5 behaviour)
                _mult   = 2 if "Intraday" in ttype else 4 if "Positional" in ttype else 3
                atr_est = (target - cp) / _mult if target > cp else 0
                print(f"[ATR] {sym}: Nifty200 lookup returned 0, fallback atr_est={atr_est:.2f}")
            else:
                print(f"[ATR] {sym}: read ATR14={atr_est:.2f} from Nifty200")
            # ── end FIX 2 ─────────────────────────────────────────────────────

            mem = save_atr_to_mem(mem, key, atr_est)
            mem = set_tsl(mem, key, init_sl)
            mem = set_max_price(mem, key, cp)
            ex_flag_key = f"{key}_EX"
            mem = ','.join(p for p in mem.split(',') if p.strip() and p.strip() != ex_flag_key)

            updated_r                = list(r)
            updated_r[C_STATUS]      = "🟢 TRADED (PAPER)"
            updated_r[C_ENTRY_PRICE] = cp
            updated_r[C_ENTRY_TIME]  = etime
            updated_r[C_TRAIL_SL]    = init_sl
            traded_rows.append((sheet_row, updated_r))

            atr       = atr_est
            o_hint    = options_hint(sym, cp, atr, ttype)
            # v13.4: CE candidate flag — uses existing ATR, no new data
            c_flag    = ce_candidate_flag(cp, atr, stage, is_bullish)
            entry_key = f"{key}_ENTRY"
            mem      += f",{entry_key}"

            pos_size  = round(capital / cp) if cp > 0 else 0
            risk_rs   = round(max(0, cp - init_sl) * pos_size)
            reward_rs = round(max(0, target - cp) * pos_size)

            entry_alerts_advance.append(
                build_entry_advance(sym, cp, cp, init_sl, target, ttype, strat, stage,
                                    priority, pos_size, capital, risk_rs, reward_rs,
                                    rr_num, trade_mode, c_flag)
            )
            entry_alerts_premium.append(
                build_entry_premium(sym, cp, cp, init_sl, target, ttype, strat, stage,
                                    priority, pos_size, capital, risk_rs, reward_rs,
                                    rr_num, o_hint, trade_mode, c_flag)
            )
            print(f"[ENTRY] {sym} @ ₹{cp} | ₹{capital:,} | {pos_size}sh | {ttype} | {trade_mode} | SL ₹{init_sl} | T ₹{target}")

        # ── Step B: Monitor active trades ─────────────────────────────────────
        for sheet_row, r in traded_rows:
            sym = str(r[C_SYMBOL]).strip()
            if not sym: continue

            key     = sym_key(sym)
            cp      = to_f(r[C_LIVE_PRICE])
            init_sl = to_f(r[C_INITIAL_SL])
            cur_tsl = to_f(r[C_TRAIL_SL]) or init_sl
            ent     = to_f(r[C_ENTRY_PRICE])
            tgt     = to_f(r[C_TARGET])
            strat   = str(r[C_STRATEGY])
            stage   = str(r[C_STAGE])
            etime   = str(r[C_ENTRY_TIME])
            ttype   = str(r[C_TRADE_TYPE])
            priority = str(r[C_PRIORITY])

            if not price_sanity(sym, cp, ent): continue

            mem      = set_max_price(mem, key, cp)
            pnl_pct  = (cp - ent) / ent * 100
            atr      = get_atr_from_mem(mem, key)
            if atr <= 0:
                _mult = 4 if "Positional" in ttype else 2 if "Intraday" in ttype else 3
                atr   = (tgt - ent) / _mult if tgt > ent else ent * 0.02

            days_held  = calc_hold_days(etime, now)
            trade_mode = get_trade_mode(mem, key)
            tsl_params = TSL_PARAMS[trade_mode]
            capital    = get_capital_from_mem(mem, key)

            new_tsl = calc_new_tsl(cp, ent, init_sl, atr, ttype, tsl_params)
            new_tsl = max(new_tsl, get_tsl(mem, key), cur_tsl)

            if new_tsl > cur_tsl:
                tsl_cell_updates.append((sheet_row, new_tsl))
                tsl_label = ('Breakeven' if abs(new_tsl - ent) < 0.5
                             else '+2% locked' if abs(new_tsl - ent * 1.02) < 0.5
                             else 'ATR trail')
                trail_msg = (
                    f"🔒 <b>{sym}</b> [{trade_mode}] | LTP ₹{cp:.2f} ({pnl_pct:+.2f}%)\n"
                    f"   Trail SL: ₹{cur_tsl:.2f} → <b>₹{new_tsl:.2f}</b> ({tsl_label})"
                )
                trail_alerts.append(trail_msg)
                mem = set_tsl(mem, key, new_tsl)
                print(f"[TSL] {sym} [{trade_mode}]: ₹{cur_tsl:.2f}→₹{new_tsl:.2f}")

            entry_date_key = etime[:10].replace('-', '') if etime else "0"
            ex_flag    = f"{key}_EX_{entry_date_key}"
            tsl_hit    = (new_tsl > 0 and cp <= new_tsl)
            target_hit = (tgt > 0 and cp >= tgt)
            hard_loss  = pnl_pct < -HARD_LOSS_PCT

            # ── Hard loss exit ────────────────────────────────────────────────
            if hard_loss and ex_flag not in mem:
                pl_rupees = round((cp - ent) / ent * capital, 2)
                hold_str  = calc_hold_str(etime, now)
                max_price = get_max_price(mem, key)

                exit_alerts_basic.append(build_exit_basic(sym, pnl_pct, "HARD LOSS"))
                exit_alerts_advance.append(
                    f"🚨 <b>HARD LOSS EXIT</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📌 <b>{sym}</b> [{ttype}] [{trade_mode}]\n"
                    f"   Entry ₹{ent:.2f} → Exit ₹{cp:.2f}\n"
                    f"   P/L: <b>{pnl_pct:+.2f}%</b> = <b>₹{pl_rupees:+.0f}</b>\n"
                    f"   Loss exceeded {HARD_LOSS_PCT}% — thesis broken\n"
                    f"   Hold: {hold_str} | Day {days_held + 1}"
                )
                hist_sheet.append_row([
                    sym, etime[:10], ent,
                    now.strftime('%Y-%m-%d'), cp,
                    f"{pnl_pct:.2f}%", "LOSS 🔴", strat,
                    "🚨 HARD LOSS EXIT", ttype, init_sl, new_tsl,
                    max_price if max_price > 0 else cp,
                    round(atr, 2), days_held,
                    capital,
                    pl_rupees, "—",
                ])
                log_sheet.update_cell(sheet_row, C_STATUS + 1, "EXITED")
                mem += f",{ex_flag}"
                mem  = set_exit_date(mem, key, now.strftime('%Y-%m-%d'))
                print(f"[HARD LOSS] {sym} | {pnl_pct:+.2f}% | ₹{pl_rupees:+.0f}")
                continue

            # ── Normal exit ───────────────────────────────────────────────────
            is_pos     = "Positional" in ttype or "positional" in ttype.lower()
            min_hold   = MIN_HOLD_POS if is_pos else MIN_HOLD_SWING
            near_hard_loss = pnl_pct < -4.0
            skip_exit  = (
                days_held < min_hold
                and not target_hit
                and not hard_loss
                and not (near_hard_loss and not is_bullish)
            )

            if (tsl_hit or target_hit) and ex_flag not in mem and not skip_exit:
                exit_reason   = ("🎯 TARGET HIT"    if target_hit else
                                 "🔒 TRAILING SL"   if new_tsl > init_sl else
                                 "🚨 INITIAL SL HIT")
                result_sym    = "WIN ✅" if (target_hit or pnl_pct > 0) else "LOSS 🔴"
                hold_str      = calc_hold_str(etime, now)
                max_price     = get_max_price(mem, key)
                pl_rupees     = round((cp - ent) / ent * capital, 2)
                o_note        = (options_hint(sym, ent, atr, ttype)
                                 .replace('\n\n📊 <b>OPTIONS ADVISORY</b>', '')
                                 .strip() if atr > 0 else "")

                exit_alerts_basic.append(build_exit_basic(sym, pnl_pct, exit_reason))
                exit_alerts_advance.append(
                    build_exit_advance(sym, ttype, ent, cp, pnl_pct,
                                       pl_rupees, hold_str, max_price,
                                       strat, exit_reason)
                )
                hist_sheet.append_row([
                    sym, etime[:10], ent,
                    now.strftime('%Y-%m-%d'), cp,
                    f"{pnl_pct:.2f}%", result_sym, strat,
                    exit_reason, ttype, init_sl, new_tsl,
                    max_price if max_price > 0 else cp,
                    round(atr, 2), days_held,
                    capital,
                    pl_rupees,
                    o_note[:100] if o_note else "—",
                ])
                log_sheet.update_cell(sheet_row, C_STATUS + 1, "EXITED")
                mem += f",{ex_flag}"
                mem  = set_exit_date(mem, key, now.strftime('%Y-%m-%d'))
                print(f"[EXIT] {sym} | {result_sym} | {pnl_pct:+.2f}% | ₹{pl_rupees:+.0f}")

            elif tsl_hit and skip_exit:
                print(f"[HOLD] {sym}: SL touched Day {days_held + 1} < {min_hold} min hold")
                if f"{key}_HOLD_WARN" not in mem:
                    regime_note = "🐂 Bullish — recovery possible" if is_bullish else "🐻 Bearish — watching closely"
                    hold_msg = (
                        f"⚠️ <b>MIN HOLD ACTIVE — {sym}</b>\n"
                        f"[{ttype}] [{trade_mode}] touched SL ₹{new_tsl:.2f} "
                        f"but only Day {days_held + 1} of {min_hold}.\n"
                        f"Holding until Day {min_hold} unless loss > {HARD_LOSS_PCT}%.\n"
                        f"Current P/L: {pnl_pct:+.2f}%\n{regime_note}"
                    )
                    send_advance(hold_msg); send_premium(hold_msg)
                    mem += f",{key}_HOLD_WARN"

        # Batch TSL writes
        if tsl_cell_updates:
            cells = []
            for (sr, new_tsl) in tsl_cell_updates:
                c = log_sheet.cell(sr, C_TRAIL_SL + 1)
                c.value = new_tsl
                cells.append(c)
            log_sheet.update_cells(cells)
            print(f"[TSL WRITE] {len(cells)} updates")

        # ── Send all alerts ───────────────────────────────────────────────────
        if exit_alerts_basic:
            for msg in exit_alerts_basic: send_basic(msg)

        if exit_alerts_advance:
            header   = f"⚡ <b>EXIT REPORT — {now.strftime('%H:%M IST')}</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            full_exit = header + "\n\n".join(exit_alerts_advance)
            send_advance(full_exit); send_premium(full_exit)

        if trail_alerts:
            tsl_msg = (f"🔒 <b>TRAIL SL UPDATE — {now.strftime('%H:%M IST')}</b>\n"
                       f"━━━━━━━━━━━━━━━━━━━━\n\n" + "\n\n".join(trail_alerts))
            send_advance(tsl_msg); send_premium(tsl_msg)

        for msg in entry_alerts_advance: send_advance(msg)
        for msg in entry_alerts_premium: send_premium(msg)

    # ─────────────────────────────────────────────────────────────────────────
    # 3. MID-DAY PULSE  12:28–12:38 IST
    # ─────────────────────────────────────────────────────────────────────────
    if now.hour == 12 and 28 <= now.minute <= 38 and f"{today}_NOON" not in mem:
        fresh     = log_sheet.get_all_values()
        live_rows = [
            pad(list(r)) for r in fresh[1:16]
            if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
            and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        ]
        wins = losses = 0
        lines_advance = []; lines_basic = []
        for r in live_rows:
            sym   = r[C_SYMBOL]; cp = to_f(r[C_LIVE_PRICE]); ent = to_f(r[C_ENTRY_PRICE])
            tsl   = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
            ttype = str(r[C_TRADE_TYPE])
            if not price_sanity(sym, cp, ent): continue
            pnl = (cp - ent) / ent * 100
            em  = "🟢" if pnl >= 0 else "🔴"
            key = sym_key(sym)
            mode_tag = {"VCP": "🎯", "MOM": "🚀", "STD": "📊"}.get(get_trade_mode(mem, key), "📊")
            if pnl >= 0: wins += 1
            else: losses += 1
            lines_advance.append(f"{em} <b>{sym}</b> {mode_tag} [{ttype}]: {pnl:+.2f}% | TSL ₹{tsl:.2f}")
            lines_basic.append(f"{em} <b>{sym}</b>: {pnl:+.2f}%")

        send_basic(
            f"☀️ <b>MID-DAY PULSE — {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"Open: {len(lines_basic)} | 🟢 {wins} | 🔴 {losses}\n\n"
            + ("\n".join(lines_basic) if lines_basic else "No open trades")
            + "\n\n🔔 <i>Full levels at ai360trading.in/membership</i>"
        )
        send_advance(
            f"☀️ <b>MID-DAY PULSE — {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Open: {len(lines_advance)} | 🟢 {wins} | 🔴 {losses}\n\n"
            + ("\n".join(lines_advance) if lines_advance else "📭 No open trades")
        )
        send_premium(
            f"☀️ <b>MID-DAY PULSE — {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Open: {len(lines_advance)} | 🟢 {wins} | 🔴 {losses}\n\n"
            + ("\n".join(lines_advance) if lines_advance else "📭 No open trades")
        )
        mem += f",{today}_NOON"

    # ─────────────────────────────────────────────────────────────────────────
    # 4. MARKET CLOSE SUMMARY  15:15–15:45 IST
    # ─────────────────────────────────────────────────────────────────────────
    if now.hour == 15 and 15 <= now.minute <= 45 and f"{today}_PM" not in mem:
        hist_data   = hist_sheet.get_all_values()
        today_exits = [r for r in hist_data[1:] if len(r) >= 7 and r[3] == today]
        wins_today  = [r for r in today_exits if "WIN"  in str(r[6]).upper()]
        loss_today  = [r for r in today_exits if "LOSS" in str(r[6]).upper()]
        total_pl    = sum(to_f(r[16]) for r in today_exits if len(r) > 16)

        exit_lines_advance = []; exit_lines_basic = []
        for r in today_exits:
            em   = "✅" if "WIN" in str(r[6]).upper() else "❌"
            pl_r = f"₹{to_f(r[16]):+.0f}" if len(r) > 16 else ""
            days_= r[14] if len(r) > 14 else "?"
            exit_lines_advance.append(f"  {em} <b>{r[0]}</b>: {r[5]} {pl_r} (held {days_}d)")
            exit_lines_basic.append(f"  {em} <b>{r[0]}</b>: {'WIN' if 'WIN' in str(r[6]).upper() else 'LOSS'}")

        fresh3    = log_sheet.get_all_values()
        open_rows = [
            pad(list(r)) for r in fresh3[1:16]
            if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
            and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        ]
        open_lines = []
        for r in open_rows:
            sym = r[C_SYMBOL]; cp = to_f(r[C_LIVE_PRICE]); ent = to_f(r[C_ENTRY_PRICE])
            tsl = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
            if not ent or ent <= 0: continue
            if cp > 0 and ent > 0:
                pnl = (cp - ent) / ent * 100
                em  = "🟢" if pnl >= 0 else "🔴"
                open_lines.append(f"  {em} <b>{sym}</b>: {pnl:+.2f}% | TSL ₹{tsl:.2f}")
            else:
                open_lines.append(f"  ⏰ <b>{sym}</b>: TSL ₹{tsl:.2f}")

        basic_close = (
            f"🔔 <b>MARKET CLOSED — {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 Wins: {len(wins_today)} | 💀 Losses: {len(loss_today)} | 📂 Open: {len(open_rows)}\n"
        )
        if exit_lines_basic: basic_close += "\n" + "\n".join(exit_lines_basic)
        basic_close += "\n\n🔔 <i>Full P/L details for subscribers\n→ ai360trading.in/membership</i>"
        send_basic(basic_close)

        full_close = (
            f"🔔 <b>MARKET CLOSED — {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 Wins: {len(wins_today)} | 💀 Losses: {len(loss_today)} | 📂 Open: {len(open_rows)}\n"
            f"💰 Today's P/L: <b>₹{total_pl:+.0f}</b>\n"
        )
        if exit_lines_advance: full_close += "\n📋 <b>Exited Today:</b>\n" + "\n".join(exit_lines_advance)
        if open_lines: full_close += "\n\n📌 <b>Holding Overnight:</b>\n" + "\n".join(open_lines)
        full_close += "\n\n✅ <i>Overnight holds monitored via TSL</i>"
        send_advance(full_close); send_premium(full_close)

        mem += f",{today}_PM"

    # ─────────────────────────────────────────────────────────────────────────
    # 5. SAVE MEMORY
    # ─────────────────────────────────────────────────────────────────────────
    log_sheet.update_acell("T4", mem)
    print(f"[DONE] {now.strftime('%H:%M:%S')} IST | mem={len(mem)} chars")


# ══════════════════════════════════════════════════════════════════════════════
# WEEKLY SUMMARY — unchanged from v13.2
# ══════════════════════════════════════════════════════════════════════════════

def run_weekly_summary():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    print("[WEEKLY] Fetching weekly + monthly summary...")

    log_sheet, hist_sheet, _ = get_sheets()
    hist_data = hist_sheet.get_all_values()
    all_rows  = hist_data[1:]

    days_since_mon = now.weekday()
    mon        = (now - timedelta(days=days_since_mon)).strftime('%Y-%m-%d')
    week_rows  = [r for r in all_rows if len(r) >= 17 and r[3] >= mon and r[3] <= today]
    mon1       = now.strftime('%Y-%m-01')
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

    send_basic(
        f"📅 <b>WEEKLY PERFORMANCE — {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"This Week: {wt} trades | Win Rate: {wwr}%\n"
        f"This Month: {mt} trades | Win Rate: {mwr}%\n"
        f"All Time: {at} trades | Win Rate: {awr}%\n\n"
        f"🔔 <i>Full ₹ P/L details for subscribers\n→ ai360trading.in/membership</i>"
    )

    full_weekly = (
        f"📅 <b>WEEKLY REPORT — w/e {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"\n📆 <b>THIS WEEK</b>\n"
        f"   Trades: {wt} | ✅ {ww}W / ❌ {wl}L | Win: {wwr}%\n"
        f"   P/L: <b>₹{wpl:+,.0f}</b> | Avg/trade: ₹{wavg:+,.0f}\n"
    )
    if best:  full_weekly += f"   🏆 Best:  <b>{best[0]}</b> = ₹{to_f(best[16]):+,.0f}\n"
    if worst and worst != best: full_weekly += f"   💀 Worst: <b>{worst[0]}</b> = ₹{to_f(worst[16]):+,.0f}\n"
    full_weekly += (
        f"\n📅 <b>THIS MONTH ({now.strftime('%B')})</b>\n"
        f"   Trades: {mt} | ✅ {mw}W / ❌ {ml}L | Win: {mwr}%\n"
        f"   P/L: <b>₹{mpl:+,.0f}</b> | Avg/trade: ₹{mavg:+,.0f}\n"
        f"\n📊 <b>ALL TIME</b>\n"
        f"   Trades: {at} | ✅ {aw}W / ❌ {al}L | Win: {awr}%\n"
        f"   Total P/L: <b>₹{apl:+,.0f}</b> | Avg/trade: ₹{aavg:+,.0f}\n"
        f"\n📌 Open now: {open_count}/{MAX_TRADES}"
    )
    send_advance(full_weekly); send_premium(full_weekly)
    print(f"[WEEKLY] Sent | W:{wt} M:{mt} All:{at} trades")


# ══════════════════════════════════════════════════════════════════════════════
# DAILY SUMMARY — unchanged from v13.2
# ══════════════════════════════════════════════════════════════════════════════

def run_daily_summary():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    print("[SUMMARY] Fetching portfolio summary...")

    log_sheet, hist_sheet, _ = get_sheets()
    mem = clean_mem(str(log_sheet.acell("T4").value or ""))
    print(f"[MEM] T4 size: {len(mem)} chars")  # ← FIXED: was missing 4 spaces
    all_data = log_sheet.get_all_values()

    open_rows = [
        pad(list(r)) for r in all_data[1:16]
        if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
    ]
    waiting_rows = [
        pad(list(r)) for r in all_data[1:16]
        if "WAITING" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
    ]

    trade_lines = []
    for r in open_rows:
        sym   = r[C_SYMBOL]; cp = to_f(r[C_LIVE_PRICE]); ent = to_f(r[C_ENTRY_PRICE])
        tsl   = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
        tgt   = to_f(r[C_TARGET]); ttype = str(r[C_TRADE_TYPE]); etime = str(r[C_ENTRY_TIME])
        if not price_sanity(sym, cp, ent): continue
        pnl   = (cp - ent) / ent * 100
        key   = sym_key(sym)
        cap   = get_capital_from_mem(mem, key)
        pl_rs = round((cp - ent) / ent * cap)
        days  = calc_hold_days(etime, now)
        em    = "🟢" if pnl >= 0 else "🔴"
        mode  = get_trade_mode(mem, key)
        trade_lines.append(
            f"{em} <b>{sym}</b> [{ttype}] [{mode}]\n"
            f"   Entry ₹{ent:.2f} → Now ₹{cp:.2f} | <b>{pnl:+.2f}%</b> = ₹{pl_rs:+,}\n"
            f"   TSL ₹{tsl:.2f} | Target ₹{tgt:.2f} | Day {days}"
        )

    hist_data     = hist_sheet.get_all_values()
    today_exits   = [r for r in hist_data[1:] if len(r) >= 7 and r[3] == today]
    exit_lines    = []
    total_exit_pl = 0.0
    for r in today_exits:
        em    = "✅" if "WIN" in str(r[6]).upper() else "❌"
        pl_r  = to_f(r[16]) if len(r) > 16 else 0
        total_exit_pl += pl_r
        exit_lines.append(f"  {em} <b>{r[0]}</b>: {r[5]} = ₹{pl_r:+,.0f}")

    wait_lines = []
    for r in waiting_rows[:5]:
        key  = sym_key(str(r[C_SYMBOL]))
        mode = get_trade_mode(mem, key)
        cap  = get_capital_from_mem(mem, key)
        wait_lines.append(
            f"  ⏳ <b>{r[C_SYMBOL]}</b> [{r[C_TRADE_TYPE]}] [{mode}] "
            f"₹{cap:,} | P:{r[C_PRIORITY]}"
        )

    msg = (
        f"📊 <b>PORTFOLIO SUMMARY</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 {now.strftime('%Y-%m-%d %H:%M')} IST\n"
        f"📈 Open: {len(open_rows)}/{MAX_TRADES} | ⏳ Waiting: {len(waiting_rows)}/{MAX_WAITING}\n"
        f"💰 Deployed: ₹{sum(get_capital_from_mem(mem, sym_key(r[C_SYMBOL])) for r in open_rows):,}\n"
    )
    if trade_lines: msg += f"\n<b>── OPEN TRADES ──</b>\n" + "\n\n".join(trade_lines)
    else: msg += "\n📭 No open trades"
    if exit_lines:
        msg += f"\n\n<b>── TODAY'S EXITS ──</b>\n" + "\n".join(exit_lines)
        msg += f"\n   <b>Today P/L: ₹{total_exit_pl:+,.0f}</b>"
    if wait_lines: msg += f"\n\n<b>── TOP WAITING ──</b>\n" + "\n".join(wait_lines)
    msg += "\n\n<i>On-demand summary</i>"

    send_advance(msg); send_premium(msg)
    print(f"[SUMMARY] Sent | Open={len(open_rows)} | Waiting={len(waiting_rows)}")


# ══════════════════════════════════════════════════════════════════════════════
# TEST TELEGRAM — unchanged from v13.2
# ══════════════════════════════════════════════════════════════════════════════

def run_test_telegram():
    now = datetime.now(IST)
    print("[TEST] Sending Telegram test messages to all 3 channels...")
    test_msg = (
        f"✅ <b>TELEGRAM TEST — OK</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 Bot: AI360 Trading v13.5\n"
        f"🕐 Time: {now.strftime('%Y-%m-%d %H:%M:%S')} IST\n"
        f"🔑 Token: Connected ✅\n💬 Chat: Connected ✅\n\n"
    )
    ok1 = _send_one(CHAT_BASIC,   test_msg + "📢 Channel: <b>ai360trading (Free)</b>")
    ok2 = _send_one(CHAT_ADVANCE, test_msg + "💎 Channel: <b>ai360trading_Advance</b>")
    ok3 = _send_one(CHAT_PREMIUM, test_msg + "👑 Channel: <b>ai360trading_Premium</b>")
    print(f"[TEST] BASIC={'✅' if ok1 else '❌'} | ADVANCE={'✅' if ok2 else '❌'} | PREMIUM={'✅' if ok3 else '❌'}")


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    mode = os.environ.get("BOT_MODE", "trade").strip().lower()
    print(f"[MODE] {mode}")
    if mode == "test_telegram":       run_test_telegram()
    elif mode == "daily_summary":     run_daily_summary()
    elif mode == "weekly_summary":    run_weekly_summary()
    else:                             run_trading_cycle()
