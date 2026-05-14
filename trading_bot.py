"""
AI360 TRADING BOT — v14.0

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
  T2 = automation switch, T4 = Python-only state (TSL/MAX/LP/ATR/EXDT)

HISTORY COLUMNS (A–R):
  A  Symbol        B  Entry Date    C  Entry Price   D  Exit Date
  E  Exit Price    F  P/L%          G  Result         H  Strategy
  I  Exit Reason   J  Trade Type    K  Initial SL     L  TSL at Exit
  M  Max Price     N  ATR at Entry  O  Days Held       P  Capital ₹
  Q  Profit/Loss ₹ R  Options Note
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, json, pytz, requests, gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

IST        = pytz.timezone('Asia/Kolkata')
TG_TOKEN   = os.environ.get('TELEGRAM_BOT_TOKEN')

# ── 3 Telegram channels — v14.0 FIX: correct env var names ───────────────────
CHAT_BASIC = os.environ.get('CHAT_ID_BASIC')      # FREE Follow/Subscribe
CHAT_ADVANCE = os.environ.get('CHAT_ID_ADVANCE')    # Advance Rs. ₹1000/month
CHAT_PREMIUM = os.environ.get('CHAT_ID_PREMIUM')    # Premium Rs. ₹3000/month

SHEET_NAME = "Ai360tradingAlgo"

# ── NSE Market Holidays 2026 ──────────────────────────────────────────────────
NSE_HOLIDAYS_2026 = {
    "2026-01-26", "2026-03-25", "2026-04-02", "2026-04-14",
    "2026-05-01", "2026-05-27", "2026-06-17", "2026-08-15",
    "2026-08-27", "2026-10-02", "2026-10-21", "2026-10-22",
    "2026-11-05", "2026-12-25",
}

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

# ── v14.0: Sync with AppScript v14.1 / v15.0 ─────────────────────────────────
MAX_TRADES     = 8       # was 5 — now matches AppScript
MAX_WAITING    = 10
LOG_ROWS       = 21      # matches AppScript v15.0

# Capital tiers — always from BotMemory sheet; these are fallback defaults
CAPITAL_HIGH   = 13000
CAPITAL_MED    = 10000
CAPITAL_STD    =  7000

MIN_RR         = 1.8
HARD_LOSS_PCT  = 5.0

# Result day threshold — skip entry if stock gapped >6% (result/event day)
RESULT_DAY_GAP_PCT = 6.0

# ── TSL mode parameters — unchanged from v13.5 ───────────────────────────────
TSL_PARAMS = {
    "VCP": {
        "breakeven": 3.0, "lock1": 5.0,
        "trail": 8.0, "atr_mult": 2.0, "gap_lock": 9.0,
    },
    "MOM": {
        "breakeven": 2.5, "lock1": 4.5,
        "trail": 7.0, "atr_mult": 1.8, "gap_lock": 8.0,
    },
    "STD": {
        "breakeven": 2.0, "lock1": 4.0,
        "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0,
    },
}

TSL_GAP_LOCK_FRAC = 0.5
MIN_HOLD_SWING    = 2
MIN_HOLD_POS      = 3


# ══════════════════════════════════════════════════════════════════════════════
# TELEGRAM — v14.0: fixed channel mapping, differentiated messages
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
            print(f"[TG FAIL] chat={chat_id[-6:]}*** status={r.status_code}: {r.text[:100]}")
            return False
        return True
    except Exception as e:
        print(f"[TG ERROR] {e}")
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


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS — identical to v13.5
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
    """Clean T4 Python-only state (TSL, MAX, LP, ATR, EXDT, AM/PM flags)."""
    cutoff = (datetime.now(IST) - timedelta(days=14)).strftime("%Y-%m-%d")
    kept   = []
    for p in mem.split(","):
        p = p.strip()
        if not p: continue
        if len(p) >= 10 and p[4] == "-" and p[7] == "-":
            if p[:10] >= cutoff: kept.append(p)
        else:
            kept.append(p)
    result = ",".join(kept)
    if len(result) > 20000:
        parts  = [p for p in result.split(",") if p.strip()]
        result = ",".join(parts[-100:])
        print(f"[MEM] ⚠️ Hard cap applied — trimmed to last 100 entries")
    print(f"[MEM] ✅ T4 size: {len(result):,} chars")
    return result

def is_market_hours(now: datetime) -> bool:
    if now.weekday() >= 5: return False
    today_str = now.strftime('%Y-%m-%d')
    if today_str in NSE_HOLIDAYS_2026: return False
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

def ce_candidate_flag(cp: float, atr: float, stage: str,
                      is_bullish: bool, rank: int = 99) -> str:
    """
    CE candidate flag — shown in Premium entry alerts only.
    v14.0: gated by rank ≤ 5 (sector leaders only) to reduce noise.
    """
    if not is_bullish: return ""
    if cp <= 0 or atr <= 0: return ""
    if rank > 5: return ""   # Only sector leaders (rank 1-5) get CE flag

    atr_pct = (atr / cp) * 100
    if atr_pct < 1.5: return ""

    gap = 5 if cp < 200 else (10 if cp < 500 else (20 if cp < 1000 else 50))
    atm_strike = round(cp / gap) * gap
    otm_strike = atm_strike + gap

    if "BREAKOUT CONFIRMED" in stage:
        strike_str = f"{int(otm_strike)} CE (OTM — breakout in progress)"
    else:
        strike_str = f"{int(atm_strike)} CE or {int(otm_strike)} CE"

    if atr_pct >= 2.5:
        target_pct, sl_pct, speed_tag = 50, 35, "⚡ Fast mover"
    else:
        target_pct, sl_pct, speed_tag = 65, 40, "📈 Normal mover"

    return (
        f"\n\n📊 <b>CE CANDIDATE — PREMIUM</b> ({speed_tag})\n"
        f"   ATR%: {atr_pct:.1f}% | Strike: {strike_str}\n"
        f"   Target: +{target_pct}% on premium | SL: -{sl_pct}% on premium\n"
        f"   Entry: Only above ₹{cp + atr * 0.3:.1f} (breakout confirm)\n"
        f"   ⚠️ Check actual premium on Zerodha option chain\n"
        f"   ⚠️ Wednesday entry → prefer monthly expiry"
    )


# ══════════════════════════════════════════════════════════════════════════════
# T4 MEMORY HELPERS — Python-only state (TSL, MAX, LP, ATR, EXDT, AM/PM flags)
# DO NOT use T4 for _CAP, _MODE, _SEC, _RANK — those come from BotMemory sheet
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
# BOTMEMORY SHEET READ — v14.0 FIX: read _CAP/_MODE/_SEC/_RANK from sheet
# ══════════════════════════════════════════════════════════════════════════════

def load_bm_sheet(ss) -> dict:
    """Load BotMemory sheet into dict {key: value}."""
    try:
        bm_ws  = ss.worksheet("BotMemory")
        rows   = bm_ws.get_all_values()
        result = {}
        for row in rows[1:]:  # skip header
            if len(row) >= 2:
                k = str(row[0]).strip()
                v = str(row[1]).strip()
                if k:
                    result[k] = v
        return result
    except Exception as e:
        print(f"[BM] Failed to load BotMemory sheet: {e}")
        return {}

def bm_get(bm_data: dict, key: str) -> str:
    return bm_data.get(key, "")

def get_trade_mode(bm_data: dict, key: str) -> str:
    val = bm_get(bm_data, f"{key}_MODE")
    return val if val in ("VCP", "MOM", "STD") else "STD"

def get_tsl_params(bm_data: dict, key: str) -> dict:
    mode = get_trade_mode(bm_data, key)
    return TSL_PARAMS[mode]

def get_capital(bm_data: dict, key: str) -> int:
    """Read capital from BotMemory sheet. Falls back to tier defaults."""
    cap_str = bm_get(bm_data, f"{key}_CAP")
    if cap_str:
        try:
            cap = int(cap_str)
            if cap in (CAPITAL_STD, CAPITAL_MED, CAPITAL_HIGH): return cap
        except:
            pass
    return CAPITAL_MED  # safe default

def get_rank(bm_data: dict, key: str) -> int:
    """Read sector rank from BotMemory sheet."""
    rank_str = bm_get(bm_data, f"{key}_RANK")
    try:
        return int(float(rank_str)) if rank_str else 99
    except:
        return 99

def get_sector(bm_data: dict, key: str) -> str:
    return bm_get(bm_data, f"{key}_SEC") or "Unknown"


# ══════════════════════════════════════════════════════════════════════════════
# TSL CALCULATION — mode-aware, unchanged from v13.5
# ══════════════════════════════════════════════════════════════════════════════

def calc_new_tsl(cp: float, ent: float, init_sl: float, atr: float,
                 ttype: str = "", params: dict = None) -> float:
    if params is None:
        params = TSL_PARAMS["STD"]
    if ent <= 0: return init_sl
    gain_pct    = ((cp - ent) / ent) * 100
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
# MESSAGE BUILDERS — v14.0: differentiated advance vs premium
# ══════════════════════════════════════════════════════════════════════════════

def build_gm_basic(today: str, trade_count: int, waiting_count: int,
                   is_bullish: bool) -> str:
    mood = "🐂 Bullish" if is_bullish else "🐻 Bearish"
    return (
        f"🌅 <b>GOOD MORNING — {today}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📈 AI360 Scanner is LIVE\n"
        f"Market: <b>{mood}</b> | Active: {trade_count}/{MAX_TRADES}\n"
        f"Setups Ready: {waiting_count}\n\n"
        f"🔔 <i>Full entry/exit alerts → Join advance channel\nai360trading.in/membership</i>"
    )

def build_gm_advance(today: str, lines: list, deployed: int,
                     waiting_count: int, sector_line: str = "") -> str:
    """Advance channel: full trade details, no CE options data."""
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

def build_gm_premium(today: str, lines_adv: list, lines_prem: list,
                     deployed: int, waiting_count: int, sector_line: str = "") -> str:
    """Premium channel: same as advance + CE candidate note on eligible trades."""
    body = "\n\n".join(lines_prem) if lines_prem else "📭 No open trades"
    msg  = (
        f"🌅 <b>GOOD MORNING — {today}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📈 Open: {len(lines_adv)}/{MAX_TRADES} | "
        f"⏳ Waiting: {waiting_count}/{MAX_WAITING}\n"
        f"💰 Deployed: ~₹{deployed:,}\n"
    )
    if sector_line:
        msg += f"{sector_line}\n"
    msg += f"\n{body}"
    return msg

def build_entry_advance(sym, cp, init_sl, target, ttype, strat, stage,
                        priority, pos_size, capital, risk_rs, reward_rs,
                        rr_num, trade_mode) -> str:
    """Advance: full entry details, no CE options."""
    mode_tag = {"VCP": "🎯 VCP", "MOM": "🚀 MOM", "STD": "📊 Swing"}.get(trade_mode, "📊 Swing")
    return (
        f"🚀 <b>TRADE ENTERED</b>\n\n"
        f"<b>Stock:</b> {sym}\n"
        f"<b>Type:</b> {ttype} [{mode_tag}]\n"
        f"<b>Entry:</b> ₹{cp:.2f}\n"
        f"<b>Setup:</b> {strat} | {stage}\n"
        f"<b>Qty:</b> {pos_size} shares @ ₹{capital:,}\n"
        f"<b>SL:</b> ₹{init_sl:.2f} (Risk: ₹{risk_rs:,})\n"
        f"<b>Target:</b> ₹{target:.2f} (Reward: ₹{reward_rs:,})\n"
        f"<b>RR:</b> 1:{rr_num:.1f} | Priority: {priority}/30"
    )

def build_entry_premium(sym, cp, init_sl, target, ttype, strat, stage,
                        priority, pos_size, capital, risk_rs, reward_rs,
                        rr_num, trade_mode, ce_flag="", o_hint="") -> str:
    """Premium: advance entry + CE candidate flag + options hint."""
    base = build_entry_advance(sym, cp, init_sl, target, ttype, strat, stage,
                               priority, pos_size, capital, risk_rs,
                               reward_rs, rr_num, trade_mode)
    extras = ""
    if ce_flag:   extras += ce_flag
    if o_hint:    extras += o_hint
    return base + extras

def build_exit_advance(sym, ttype, ent, cp, pnl_pct, pl_rupees,
                       hold_str, max_price, strat, exit_reason) -> str:
    em = "🎯" if "TARGET" in exit_reason else "🚨" if "HARD" in exit_reason else "🔒"
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
        f"🔔 <i>Real-time alerts → ai360trading.in/membership</i>"
    )


# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE SHEETS — unchanged from v13.5
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
    delays    = [5, 15, 30, 60, 120]
    last_error = None
    for attempt, delay in enumerate(delays):
        try:
            ss = gspread.authorize(creds).open(SHEET_NAME)
            return (ss,
                    ss.worksheet("AlertLog"),
                    ss.worksheet("History"),
                    ss.worksheet("Nifty200"))
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
            return True
        cmp_nifty = to_f(row[2])
        dma20     = to_f(row[4])
        if cmp_nifty <= 0 or dma20 <= 0: return True
        bullish = cmp_nifty >= dma20
        print(f"[REGIME] Nifty ₹{cmp_nifty:.0f} vs 20DMA ₹{dma20:.0f} → {'BULLISH' if bullish else 'BEARISH'}")
        return bullish
    except Exception as e:
        print(f"[REGIME] Error: {e} — defaulting bullish")
        return True

def _read_atr_from_nifty200(nifty_sheet, sym: str) -> float:
    try:
        nifty_data = nifty_sheet.get_all_values()
        for row in nifty_data[1:]:
            if str(row[0]).strip() == sym.strip():
                if len(row) > 28:
                    val = to_f(row[28])
                    if val > 0: return val
                break
    except Exception as e:
        print(f"[ATR] Nifty200 lookup failed for {sym}: {e}")
    return 0.0

def _read_pct_change_from_nifty200(nifty_sheet, sym: str) -> float:
    """Read today's %Change (col D, index 3) for result day detection."""
    try:
        nifty_data = nifty_sheet.get_all_values()
        for row in nifty_data[1:]:
            if str(row[0]).strip() == sym.strip():
                if len(row) > 3:
                    return abs(to_f(row[3]))
                break
    except:
        pass
    return 0.0

def get_sector_context(bm_data: dict, waiting_syms: list) -> str:
    counts = {}
    for sym in waiting_syms:
        key = sym_key(sym)
        sec = get_sector(bm_data, key) or "Mixed"
        counts[sec] = counts.get(sec, 0) + 1
    if not counts: return ""
    parts = [f"{s}({c})" for s, c in sorted(counts.items(), key=lambda x: -x[1])]
    return f"🔄 <b>Sectors:</b> {', '.join(parts[:4])}"


# ══════════════════════════════════════════════════════════════════════════════
# MAIN TRADING CYCLE
# ══════════════════════════════════════════════════════════════════════════════

def run_trading_cycle():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    mins  = now.hour * 60 + now.minute

    # Weekend check
    if now.weekday() >= 5:
        print(f"[SKIP] Weekend ({now.strftime('%A')})"); return

    # Holiday check
    if today in NSE_HOLIDAYS_2026:
        print(f"[SKIP] NSE Holiday — {today}"); return

    # Window: 08:45–15:45 IST only
    if not ((8 * 60 + 45) <= mins <= (15 * 60 + 45)):
        print(f"[SKIP] Outside window: {now.strftime('%H:%M')} IST"); return

    print(f"[START] {now.strftime('%Y-%m-%d %H:%M:%S')} IST")

    # ── Get sheets + BotMemory ────────────────────────────────────────────────
    ss, log_sheet, hist_sheet, nifty_sheet = get_sheets()
    bm_data   = load_bm_sheet(ss)        # read _CAP/_MODE/_SEC/_RANK from sheet
    mem       = clean_mem(str(log_sheet.acell("T4").value or ""))  # Python-only T4 state

    is_bullish = get_market_regime(nifty_sheet)

    # Automation switch
    if str(log_sheet.acell("T2").value or "").strip().upper() != "YES":
        print("[SKIP] Automation OFF (T2 != YES)")
        log_sheet.update_acell("T4", mem)
        return

    all_data   = log_sheet.get_all_values()
    trade_zone = [pad(list(r)) for r in all_data[1:LOG_ROWS + 1]]

    traded_rows = []
    waiting_syms = []
    for i, r in enumerate(trade_zone):
        status = str(r[C_STATUS]).upper()
        sym    = str(r[C_SYMBOL]).strip()
        if "TRADED" in status and "EXITED" not in status:
            traded_rows.append((i + 2, r))
        elif "WAITING" in status and sym:
            waiting_syms.append(sym)

    print(f"[INFO] Active: {len(traded_rows)}/{MAX_TRADES} | Waiting: {len(waiting_syms)}")

    # ─────────────────────────────────────────────────────────────────────────
    # 1. GOOD MORNING  08:45–09:29 IST — v14.0: differentiated by channel
    # ─────────────────────────────────────────────────────────────────────────
    if ((now.hour == 8 and now.minute >= 45) or
            (now.hour == 9 and now.minute <= 29)) and f"{today}_AM" not in mem:

        sector_line   = get_sector_context(bm_data, waiting_syms)
        lines_advance = []
        lines_premium = []

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

            key      = sym_key(sym)
            cap      = get_capital(bm_data, key)
            mode     = get_trade_mode(bm_data, key)
            mode_tag = {"VCP": "🎯", "MOM": "🚀", "STD": "📊"}.get(mode, "📊")
            sl_label = "TSL" if sl > to_f(r[C_INITIAL_SL]) else "SL"

            if cp > 0 and ent > 0:
                pnl    = (cp - ent) / ent * 100
                pl_rs  = round((cp - ent) / ent * cap)
                to_tgt = ((tgt - cp) / cp * 100) if cp > 0 else 0
                to_sl  = ((cp - sl) / cp * 100) if cp > 0 else 0
                em     = "🟢" if pnl >= 0 else "🔴"
                line   = (
                    f"{em} <b>{sym}</b> {mode_tag} Day {days+1}\n"
                    f"   Entry ₹{ent:.2f} → Now ₹{cp:.2f}\n"
                    f"   P/L: <b>{pnl:+.2f}%</b> = <b>₹{pl_rs:+,}</b>\n"
                    f"   {sl_label} ₹{sl:.2f} ({to_sl:.1f}% away) | T ₹{tgt:.2f} ({to_tgt:.1f}% away)"
                )
                lines_advance.append(line)

                # Premium: same + CE flag if eligible
                rank   = get_rank(bm_data, key)
                atr    = get_atr_from_mem(mem, key)
                stage  = str(r[C_STAGE])
                c_flag = ce_candidate_flag(cp, atr, stage, is_bullish, rank) if atr > 0 else ""
                lines_premium.append(line + (c_flag if c_flag else ""))
            else:
                fallback = (
                    f"⏰ <b>{sym}</b> {mode_tag} Day {days+1}\n"
                    f"   Entry ₹{ent:.2f} | SL ₹{sl:.2f} | T ₹{tgt:.2f}\n"
                    f"   (Price loading...)"
                )
                lines_advance.append(fallback)
                lines_premium.append(fallback)

        deployed = sum(
            get_capital(bm_data, sym_key(r[C_SYMBOL]))
            for _, r in traded_rows if r[C_SYMBOL]
        )

        # v14.0: Each channel gets appropriate content
        send_basic(build_gm_basic(today, len(lines_advance), len(waiting_syms), is_bullish))
        send_advance(build_gm_advance(today, lines_advance, deployed, len(waiting_syms), sector_line))
        send_premium(build_gm_premium(today, lines_advance, lines_premium, deployed, len(waiting_syms), sector_line))

        mem += f",{today}_AM"
        log_sheet.update_acell("T4", mem)
        print(f"[GM] Sent to all 3 channels | Trades: {len(lines_advance)} | Waiting: {len(waiting_syms)}")

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

            active_count = sum(1 for _, ar in traded_rows)
            if active_count >= MAX_TRADES: break

            cp       = to_f(r[C_LIVE_PRICE])
            init_sl  = to_f(r[C_INITIAL_SL])
            target   = to_f(r[C_TARGET])
            priority = str(r[C_PRIORITY])
            stage    = str(r[C_STAGE])
            strat    = str(r[C_STRATEGY])
            ttype    = str(r[C_TRADE_TYPE])

            if cp <= 0: continue

            # RR re-validation
            rr_raw = str(r[C_RR]).strip()
            if rr_raw:
                try: rr_val = to_f(rr_raw.split(':')[-1])
                except: rr_val = 0.0
                if rr_val > 0 and rr_val < MIN_RR:
                    print(f"[SKIP] {sym}: RR 1:{rr_val:.1f} below MIN_RR — stale candidate")
                    continue

            key        = sym_key(sym)
            sheet_row  = i + 2
            last_cp    = get_last_price(mem, key)
            mem        = set_last_price(mem, key, cp)

            if last_cp > 0 and abs(cp - last_cp) < 0.01:
                print(f"[STALE] {sym}: price unchanged"); continue

            # 5-day cooldown after exit
            exit_date  = get_exit_date(mem, key)
            if exit_date and trading_days_since(exit_date, now) < 5:
                print(f"[COOLDOWN] {sym}: recent exit"); continue

            # Min qty check
            cap = get_capital(bm_data, key)
            pos_size_check = round(cap / cp) if cp > 0 else 0
            if pos_size_check < 2:
                print(f"[SKIP] {sym}: CMP ₹{cp:,.0f} too high"); continue

            # v14.0 NEW: Result day filter — skip if stock gapped >6% today
            pct_change_today = _read_pct_change_from_nifty200(nifty_sheet, sym)
            if pct_change_today > RESULT_DAY_GAP_PCT:
                print(f"[RESULT DAY] {sym}: |%Change|={pct_change_today:.1f}% — skipping entry")
                continue

            trade_mode  = get_trade_mode(bm_data, key)
            tsl_params  = TSL_PARAMS[trade_mode]
            rank        = get_rank(bm_data, key)
            etime       = now.strftime('%Y-%m-%d %H:%M:%S')

            log_sheet.update_cell(sheet_row, C_STATUS + 1,      "🟢 TRADED (PAPER)")
            log_sheet.update_cell(sheet_row, C_ENTRY_PRICE + 1, cp)
            log_sheet.update_cell(sheet_row, C_ENTRY_TIME + 1,  etime)
            log_sheet.update_cell(sheet_row, C_TRAIL_SL + 1,    init_sl)

            risk   = cp - init_sl
            reward = target - cp
            rr_num = (reward / risk) if risk > 0 else 0
            log_sheet.update_cell(sheet_row, C_RR + 1, f"1:{rr_num:.1f}")

            # Read ATR from Nifty200 directly
            atr_est = _read_atr_from_nifty200(nifty_sheet, sym)
            if atr_est <= 0:
                _mult   = 2 if "Intraday" in ttype else 4 if "Positional" in ttype else 3
                atr_est = (target - cp) / _mult if target > cp else 0
                print(f"[ATR] {sym}: fallback atr_est={atr_est:.2f}")
            else:
                print(f"[ATR] {sym}: ATR14={atr_est:.2f} from Nifty200")

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

            atr    = atr_est
            o_hint = options_hint(sym, cp, atr, ttype)
            c_flag = ce_candidate_flag(cp, atr, stage, is_bullish, rank)

            pos_size  = round(cap / cp) if cp > 0 else 0
            risk_rs   = round(max(0, cp - init_sl) * pos_size)
            reward_rs = round(max(0, target - cp) * pos_size)

            # v14.0: Advance gets entry without CE, Premium gets CE flag
            entry_alerts_advance.append(
                build_entry_advance(sym, cp, init_sl, target, ttype, strat, stage,
                                    priority, pos_size, cap, risk_rs, reward_rs,
                                    rr_num, trade_mode)
            )
            entry_alerts_premium.append(
                build_entry_premium(sym, cp, init_sl, target, ttype, strat, stage,
                                    priority, pos_size, cap, risk_rs, reward_rs,
                                    rr_num, trade_mode, c_flag, o_hint)
            )
            print(f"[ENTRY] {sym} @ ₹{cp} | ₹{cap:,} | {pos_size}sh | {ttype} | {trade_mode} | Rank={rank}")

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

            if not price_sanity(sym, cp, ent): continue

            mem      = set_max_price(mem, key, cp)
            pnl_pct  = (cp - ent) / ent * 100
            atr      = get_atr_from_mem(mem, key)
            if atr <= 0:
                _mult = 4 if "Positional" in ttype else 2 if "Intraday" in ttype else 3
                atr   = (tgt - ent) / _mult if tgt > ent else ent * 0.02

            days_held  = calc_hold_days(etime, now)
            trade_mode = get_trade_mode(bm_data, key)
            tsl_params = TSL_PARAMS[trade_mode]
            capital    = get_capital(bm_data, key)

            new_tsl = calc_new_tsl(cp, ent, init_sl, atr, ttype, tsl_params)
            new_tsl = max(new_tsl, get_tsl(mem, key), cur_tsl)

            if new_tsl > cur_tsl:
                tsl_cell_updates.append((sheet_row, new_tsl))
                tsl_label = ('Breakeven' if abs(new_tsl - ent) < 0.5
                             else '+2% locked' if abs(new_tsl - ent * 1.02) < 0.5
                             else 'ATR trail')
                trail_msg = (
                    f"🔒 <b>{sym}</b> [{trade_mode}] LTP ₹{cp:.2f} ({pnl_pct:+.2f}%)\n"
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

            # Hard loss exit (no min-hold)
            if hard_loss and ex_flag not in mem:
                pl_rupees = round((cp - ent) / ent * capital, 2)
                hold_str  = calc_hold_str(etime, now)
                max_price = get_max_price(mem, key)

                exit_msg  = build_exit_advance(
                    sym, ttype, ent, cp, pnl_pct, pl_rupees,
                    hold_str, max_price, strat, "🚨 HARD LOSS EXIT"
                )
                exit_alerts_advance.append(exit_msg)
                exit_alerts_basic.append(build_exit_basic(sym, pnl_pct, "HARD LOSS"))

                hist_sheet.append_row([
                    sym, etime[:10], ent,
                    now.strftime('%Y-%m-%d'), cp,
                    f"{pnl_pct:.2f}%", "LOSS 🔴", strat,
                    "🚨 HARD LOSS EXIT", ttype, init_sl, new_tsl,
                    max_price if max_price > 0 else cp,
                    round(atr, 2), days_held, capital, pl_rupees, "—",
                ])
                log_sheet.update_cell(sheet_row, C_STATUS + 1, "EXITED")
                mem += f",{ex_flag}"
                mem  = set_exit_date(mem, key, now.strftime('%Y-%m-%d'))
                print(f"[HARD LOSS] {sym} | {pnl_pct:+.2f}% | ₹{pl_rupees:+.0f}")
                continue

            # Normal exit — with min-hold protection
            is_pos    = "Positional" in ttype or "positional" in ttype.lower()
            min_hold  = MIN_HOLD_POS if is_pos else MIN_HOLD_SWING
            near_hard = pnl_pct < -4.0
            skip_exit = (
                days_held < min_hold
                and not target_hit
                and not hard_loss
                and not (near_hard and not is_bullish)
            )

            if (tsl_hit or target_hit) and ex_flag not in mem and not skip_exit:
                exit_reason = ("🎯 TARGET HIT"   if target_hit
                               else "🔒 TRAILING SL" if new_tsl > init_sl
                               else "🚨 INITIAL SL HIT")
                result_sym  = "WIN ✅" if (target_hit or pnl_pct > 0) else "LOSS 🔴"
                hold_str    = calc_hold_str(etime, now)
                max_price   = get_max_price(mem, key)
                pl_rupees   = round((cp - ent) / ent * capital, 2)

                exit_msg = build_exit_advance(
                    sym, ttype, ent, cp, pnl_pct, pl_rupees,
                    hold_str, max_price, strat, exit_reason
                )
                exit_alerts_advance.append(exit_msg)
                exit_alerts_basic.append(build_exit_basic(sym, pnl_pct, exit_reason))

                hist_sheet.append_row([
                    sym, etime[:10], ent,
                    now.strftime('%Y-%m-%d'), cp,
                    f"{pnl_pct:.2f}%", result_sym, strat,
                    exit_reason, ttype, init_sl, new_tsl,
                    max_price if max_price > 0 else cp,
                    round(atr, 2), days_held, capital, pl_rupees, "—",
                ])
                log_sheet.update_cell(sheet_row, C_STATUS + 1, "EXITED")
                mem += f",{ex_flag}"
                mem  = set_exit_date(mem, key, now.strftime('%Y-%m-%d'))
                print(f"[EXIT] {sym} | {exit_reason} | {pnl_pct:+.2f}% | ₹{pl_rupees:+.0f}")

            elif (tsl_hit or target_hit) and skip_exit:
                print(f"[MIN HOLD] {sym}: Day {days_held+1}/{min_hold} — holding. "
                      f"TSL={tsl_hit} Tgt={target_hit} P/L={pnl_pct:+.2f}%")
                # Alert advance/premium about min-hold protection
                hold_msg = (
                    f"⚠️ <b>MIN HOLD ACTIVE — {sym}</b>\n"
                    f"[{ttype}] [{trade_mode}] touched SL ₹{new_tsl:.2f} "
                    f"but only Day {days_held+1} of {min_hold}.\n"
                    f"Holding until Day {min_hold} unless loss > {HARD_LOSS_PCT}%.\n"
                    f"Current P/L: {pnl_pct:+.2f}%"
                )
                if f"{key}_HOLD_WARN_{today}" not in mem:
                    send_advance_and_premium(hold_msg)
                    mem += f",{key}_HOLD_WARN_{today}"

        # ── Batch TSL cell updates ─────────────────────────────────────────────
        for sheet_row, new_tsl in tsl_cell_updates:
            try:
                log_sheet.update_cell(sheet_row, C_TRAIL_SL + 1, new_tsl)
            except Exception as e:
                print(f"[TSL UPDATE FAIL] row {sheet_row}: {e}")

        # ── Send entry alerts — advance gets clean signal, premium gets CE ─────
        for msg in entry_alerts_advance:
            send_advance(msg)
        for msg in entry_alerts_premium:
            send_premium(msg)
        for msg in exit_alerts_advance:
            send_advance(msg)
            send_premium(msg)
        for msg in exit_alerts_basic:
            send_basic(msg)
        if trail_alerts:
            trail_bundle = "\n\n".join(trail_alerts)
            send_advance_and_premium(f"📊 <b>TSL UPDATES</b>\n━━━━━━━━━━━━━━\n{trail_bundle}")

    # ─────────────────────────────────────────────────────────────────────────
    # 3. MID-DAY PULSE 12:28–12:38 IST
    # ─────────────────────────────────────────────────────────────────────────
    if (now.hour == 12 and 28 <= now.minute <= 38) and f"{today}_MD" not in mem:
        if traded_rows:
            md_lines = []
            for _, r in traded_rows:
                sym  = r[C_SYMBOL]
                cp   = to_f(r[C_LIVE_PRICE])
                ent  = to_f(r[C_ENTRY_PRICE])
                sl   = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
                tgt  = to_f(r[C_TARGET])
                key  = sym_key(sym)
                cap  = get_capital(bm_data, key)
                if ent > 0 and cp > 0:
                    pnl    = (cp - ent) / ent * 100
                    pl_rs  = round((cp - ent) / ent * cap)
                    to_tgt = ((tgt - cp) / cp * 100) if cp > 0 else 0
                    em     = "🟢" if pnl >= 0 else "🔴"
                    md_lines.append(
                        f"{em} <b>{sym}</b> {pnl:+.2f}% = ₹{pl_rs:+,} "
                        f"| Target: {to_tgt:+.1f}% away"
                    )
            if md_lines:
                md_msg = (
                    f"📊 <b>MID-DAY PULSE — {now.strftime('%H:%M')} IST</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    + "\n".join(md_lines)
                )
                send_advance_and_premium(md_msg)
        mem += f",{today}_MD"
        log_sheet.update_acell("T4", mem)

    # ─────────────────────────────────────────────────────────────────────────
    # 4. MARKET CLOSE SUMMARY 15:15–15:45 IST
    # ─────────────────────────────────────────────────────────────────────────
    if (now.hour == 15 and 15 <= now.minute <= 45) and f"{today}_PM" not in mem:
        # Tally from History sheet (exits today)
        try:
            hist_data  = hist_sheet.get_all_values()
            today_rows = [
                r for r in hist_data[1:]
                if len(r) > 3 and str(r[3]).startswith(today)
            ]
            wins_today   = [r for r in today_rows if "WIN" in str(r[6]).upper()]
            losses_today = [r for r in today_rows if "LOSS" in str(r[6]).upper()]
            daily_pl     = sum(to_f(r[16]) for r in today_rows)
        except:
            today_rows   = []
            wins_today   = []
            losses_today = []
            daily_pl     = 0

        # Overnight open trades
        open_overnight = []
        for _, r in traded_rows:
            sym  = r[C_SYMBOL]
            cp   = to_f(r[C_LIVE_PRICE])
            ent  = to_f(r[C_ENTRY_PRICE])
            sl   = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
            if ent > 0 and cp > 0:
                pnl  = (cp - ent) / ent * 100
                key  = sym_key(sym)
                cap  = get_capital(bm_data, key)
                pl_rs = round((cp - ent) / ent * cap)
                em   = "🟢" if pnl >= 0 else "🔴"
                open_overnight.append(f"{em} <b>{sym}</b> {pnl:+.2f}% = ₹{pl_rs:+,} | TSL ₹{sl:.2f}")

        close_adv = (
            f"🔔 <b>MARKET CLOSED — {today}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 Wins: {len(wins_today)} | ❌ Losses: {len(losses_today)} | "
            f"📋 Open: {len(open_overnight)}\n"
            f"💰 Today Realised P/L: <b>₹{daily_pl:+,.0f}</b>\n"
        )
        if today_rows:
            close_adv += f"\n📤 <b>Exited Today:</b>\n"
            for r in today_rows:
                pnl_pct = to_f(r[5].replace('%',''))
                pl_rs   = to_f(r[16])
                em      = "✅" if "WIN" in str(r[6]).upper() else "❌"
                close_adv += f"{em} <b>{r[0]}</b>: {pnl_pct:+.2f}% = ₹{pl_rs:+,.0f}\n"
        if open_overnight:
            close_adv += f"\n📌 <b>Holding Overnight ({len(open_overnight)} trade{'s' if len(open_overnight)>1 else ''}):</b>\n"
            close_adv += "\n".join(open_overnight) + "\n"
            close_adv += f"\n✅ Overnight holds monitored via TSL"

        close_basic = (
            f"🔔 <b>MARKET CLOSED — {today}</b>\n"
            f"Wins: {len(wins_today)} | Losses: {len(losses_today)} | Open: {len(open_overnight)}\n"
            f"Today P/L: ₹{daily_pl:+,.0f}\n\n"
            f"🔔 <i>Full details → ai360trading.in/membership</i>"
        )

        send_basic(close_basic)
        send_advance_and_premium(close_adv)

        mem += f",{today}_PM"
        log_sheet.update_acell("T4", mem)
        print(f"[CLOSE] Sent close summary | Exits: {len(today_rows)} | Open: {len(open_overnight)}")
        return

    # ── Save T4 at end of every run ───────────────────────────────────────────
    log_sheet.update_acell("T4", mem)
    print(f"[DONE] {now.strftime('%H:%M:%S')} IST | T4: {len(mem)} chars")


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import traceback
    mode = os.environ.get('BOT_MODE', 'trade').strip().lower()
    print(f"[MODE] {mode}")

    try:
        if mode == 'test_telegram':
            # Test all 3 channels regardless of market hours
            now = datetime.now(IST)
            test_msg = (
                f"✅ <b>TELEGRAM TEST — {now.strftime('%d-%b %H:%M')} IST</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"AI360 Trading v14.0\n"
                f"Channel: {{channel}}\n"
                f"Status: Bot is alive and connected ✅\n"
                f"Market: {'OPEN' if is_market_hours(now) else 'CLOSED'}"
            )
            ok1 = send_basic(test_msg.format(channel="Basic 🆓"))
            ok2 = send_advance(test_msg.format(channel="Advance 📊"))
            ok3 = send_premium(test_msg.format(channel="Premium 💎"))
            print(f"[TEST] Basic={ok1} Advance={ok2} Premium={ok3}")
            if not (ok1 or ok2 or ok3):
                print("[TEST] ❌ ALL channels failed — check TELEGRAM_BOT_TOKEN")
            elif ok1 and ok2 and ok3:
                print("[TEST] ✅ All 3 channels received message")
            else:
                print("[TEST] ⚠️ Some channels failed — check CHAT_ID secrets")

        elif mode == 'daily_summary':
            # Send daily summary without market hours check
            now     = datetime.now(IST)
            today   = now.strftime('%Y-%m-%d')
            ss, log_sheet, hist_sheet, nifty_sheet = get_sheets()
            bm_data = load_bm_sheet(ss)
            all_data = log_sheet.get_all_values()
            trade_zone = [pad(list(r)) for r in all_data[1:LOG_ROWS + 1]]
            traded = [r for r in trade_zone if "TRADED" in str(r[C_STATUS]).upper() and "EXITED" not in str(r[C_STATUS]).upper()]
            waiting = [r for r in trade_zone if "WAITING" in str(r[C_STATUS]).upper()]
            msg = (
                f"📊 <b>DAILY SUMMARY — {today}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🔹 Active: {len(traded)}/{MAX_TRADES}\n"
                f"🔸 Waiting: {len(waiting)}/{MAX_WAITING}\n"
                f"✅ System: Online v14.0"
            )
            send_advance_and_premium(msg)
            print(f"[DAILY] Sent — Traded:{len(traded)} Waiting:{len(waiting)}")

        elif mode == 'weekly_summary':
            # Trigger weekly summary without day check
            now     = datetime.now(IST)
            today   = now.strftime('%Y-%m-%d')
            ss, log_sheet, hist_sheet, nifty_sheet = get_sheets()
            send_advance_and_premium(f"📅 <b>WEEKLY SUMMARY</b>\n<i>Manual trigger — {today}</i>\nCheck History sheet for full details.")
            print("[WEEKLY] Sent manual trigger")

        else:
            # Default: trade mode
            run_trading_cycle()

    except Exception as e:
        err = traceback.format_exc()
        print(f"[FATAL] {e}\n{err}")
        try:
            adv = os.environ.get('CHAT_ID_ADVANCE')
            tok = os.environ.get('TELEGRAM_BOT_TOKEN')
            if tok and adv:
                requests.post(
                    f"https://api.telegram.org/bot{tok}/sendMessage",
                    json={"chat_id": adv, "text": f"⚠️ <b>BOT ERROR</b>\n{str(e)[:300]}", "parse_mode": "HTML"},
                    timeout=10
                )
        except: pass
        raise
