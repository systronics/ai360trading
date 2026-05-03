"""
AI360 TRADING BOT — v14.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v14.0 CHANGES vs v13.5:

1. BotMemory sheet migration — T4 cell removed completely
   All state that was stored in AlertLog T4 as comma-separated string
   is now stored in the BotMemory sheet (cols A–E: Key, Value,
   UpdatedAt, Symbol, KeyType).
   - _mem_get / _mem_set / clean_mem → REMOVED
   - All string-based TSL/MAX/ATR/LP/CAP/MODE/SEC/EXDT helpers →
     replaced with BotMemory sheet read/write functions (_bm_*)
   - Daytime flags (AM, NOON, PM, WEEKLY) → stored as FLAG entries
   - Per-symbol state (TSL, MAX, ATR, CAP, MODE, SEC, LP, EXDT) →
     stored as TRADE entries
   - log_sheet.update_acell("T4", ...) calls → REMOVED
   IMPORTANT: Deploy AppScript v14.0 and this file together on a day
   with no open trades.

2. Telegram token fix
   WRONG: os.environ.get('TELEGRAM_TOKEN')
   FIXED: os.environ.get('TELEGRAM_BOT_TOKEN')
   Workflow already passes TELEGRAM_BOT_TOKEN as TELEGRAM_TOKEN env var
   (legacy mapping kept in trading_bot.yml). Both now align.

3. Telegram channel swap fix
   WRONG: CHAT_ADVANCE read CHAT_ID_PREMIUM, CHAT_PREMIUM read CHAT_ID_ADVANCE
   FIXED: Each variable reads its own correct secret.

4. Capital tiers raised
   OLD: ₹7,000 / ₹10,000 / ₹13,000 | MAX_DEPLOYED ₹45,000 | MAX_TRADES 5
   NEW: ₹15,000 / ₹20,000 / ₹25,000 | MAX_DEPLOYED ₹1,00,000 | MAX_TRADES 8

5. Options advisory split
   Advance channel: CE candidate flag (informational, ATR%-based)
   Premium channel: full options buying block (strike, trigger, target%,
                    SL%, expiry note) — separate build_options_premium()

6. CE ATR fix
   ce_candidate_flag() now receives real ATR14 from Nifty200 (via
   _read_atr_from_nifty200), not backwards-derived estimate.
   Falls back to estimated ATR only if sheet lookup fails (same as v13.5 entry fix).

WHAT IS NOT CHANGED vs v13.5:
   - All TSL logic (calc_new_tsl, TSL_PARAMS, mode thresholds)
   - All exit rules (hard loss, min hold, cooldown, target/TSL hit)
   - Market regime detection (get_market_regime)
   - Message builders (GM, entry, exit, trail) — structure unchanged
   - Daily message schedule (AM/NOON/PM windows)
   - Weekly summary, daily summary run modes
   - Nifty200 ATR14 read (_read_atr_from_nifty200)
   - RR re-validation (MIN_RR = 1.8)
   - Sector context helper (get_sector_context)
   - get_sheets() with retry logic
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
  T2 = YES/NO automation switch

BOTMEMORY SHEET (cols A–E, header in row 1, data from row 2):
  A: Key   B: Value   C: UpdatedAt   D: Symbol   E: KeyType
  KeyType: FLAG (date-stamped, purged after 14 days by AppScript)
           TRADE (per-symbol persistent state)
           STATE (batch state — written by AppScript, not bot)

PER-SYMBOL TRADE KEYS written by this bot:
  {sym}_TSL   — current trailing SL (int, price×100 to avoid floats)
  {sym}_MAX   — highest price seen since entry (int, price×100)
  {sym}_ATR   — ATR14 at entry (int, atr×100)
  {sym}_LP    — last known live price (int, price×100) for staleness check
  {sym}_EXDT  — exit date "YYYY-MM-DD" for 5-day cooldown

FLAG KEYS written by this bot:
  {today}_AM     — Good Morning sent
  {today}_NOON   — Mid-day pulse sent
  {today}_PM     — Market close summary sent

PER-SYMBOL TRADE KEYS written by AppScript (read-only by bot):
  {sym}_CAP   — capital tier (15000/20000/25000)
  {sym}_MODE  — trade mode (VCP/MOM/STD)
  {sym}_SEC   — sector name

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

IST      = pytz.timezone('Asia/Kolkata')
TG_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')   # v14.0 fix: was 'TELEGRAM_TOKEN'

# ── 3 Telegram channels ───────────────────────────────────────────────────────
CHAT_BASIC   = os.environ.get('TELEGRAM_CHAT_ID')
CHAT_ADVANCE = os.environ.get('CHAT_ID_ADVANCE')   # v14.0 fix: was reading CHAT_ID_PREMIUM
CHAT_PREMIUM = os.environ.get('CHAT_ID_PREMIUM')   # v14.0 fix: was reading CHAT_ID_ADVANCE

SHEET_NAME = "Ai360tradingAlgo"
BM_SHEET   = "BotMemory"          # v14.0: new memory sheet

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

# ── Capital config — v14.0 raised tiers ───────────────────────────────────────
CAPITAL_HIGH      = 25000   # was 13000
CAPITAL_MED       = 20000   # was 10000
CAPITAL_STD       = 15000   # was  7000
CAPITAL_PER_TRADE = CAPITAL_STD    # fallback default
MAX_TRADES        = 8       # was 5
MAX_WAITING       = 10
MAX_DEPLOYED      = 100000  # was 45000

# ── RR minimum ────────────────────────────────────────────────────────────────
MIN_RR = 1.8

# ── TSL mode parameters — unchanged from v13.5 ────────────────────────────────
TSL_PARAMS = {
    "VCP": {
        "breakeven": 3.0,
        "lock1"    : 5.0,
        "trail"    : 8.0,
        "atr_mult" : 2.0,
        "gap_lock" : 9.0,
    },
    "MOM": {
        "breakeven": 2.5,
        "lock1"    : 4.5,
        "trail"    : 7.0,
        "atr_mult" : 1.8,
        "gap_lock" : 8.0,
    },
    "STD": {
        "breakeven": 2.0,
        "lock1"    : 4.0,
        "trail"    : 10.0,
        "atr_mult" : 2.5,
        "gap_lock" : 8.0,
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
# GENERAL HELPERS
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


# ══════════════════════════════════════════════════════════════════════════════
# BOTMEMORY SHEET HELPERS — v14.0 replacement for T4 string helpers
# ══════════════════════════════════════════════════════════════════════════════
# BotMemory sheet cols (1-based for gspread, 0-based in array):
#   A(0)=Key  B(1)=Value  C(2)=UpdatedAt  D(3)=Symbol  E(4)=KeyType
# Row 1 is header. Data starts row 2.
# bm dict: { key: { "value": str, "row": int (1-based) } }

def bm_load(bm_sheet) -> dict:
    """Load entire BotMemory sheet into a dict."""
    bm = {}
    if not bm_sheet:
        return bm
    last_row = bm_sheet.row_count
    if last_row < 2:
        return bm
    try:
        data = bm_sheet.get_all_values()
    except Exception as e:
        print(f"[BM LOAD] Error: {e}")
        return bm
    for i, row in enumerate(data[1:], start=2):   # skip header row 1
        key = str(row[0]).strip() if row else ""
        if not key:
            continue
        bm[key] = {
            "value": str(row[1]) if len(row) > 1 else "",
            "row"  : i,
        }
    print(f"[BM] Loaded {len(bm)} keys from BotMemory sheet")
    return bm

def bm_get(bm: dict, key: str) -> str:
    """Get a value from the loaded bm dict. Returns '' if missing."""
    return bm[key]["value"] if key in bm else ""

def bm_exists(bm: dict, key: str) -> bool:
    return key in bm

def bm_set(bm_sheet, bm: dict, key: str, val: str,
           sym: str = "", ktype: str = "STATE") -> None:
    """Write or update a key in BotMemory sheet. Mutates bm in-place."""
    if not bm_sheet:
        return
    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    sym   = sym   or ""
    ktype = ktype or "STATE"

    if key in bm:
        # Update existing row in-place (B=Value, C=UpdatedAt only)
        r = bm[key]["row"]
        try:
            bm_sheet.update(f"B{r}:C{r}", [[val, now_str]])
        except Exception as e:
            print(f"[BM SET] Update error key={key}: {e}")
            return
        bm[key]["value"] = val
    else:
        # Append new row
        try:
            bm_sheet.append_row([key, val, now_str, sym, ktype],
                                 value_input_option="RAW")
        except Exception as e:
            print(f"[BM SET] Append error key={key}: {e}")
            return
        # Compute new row index (approximation — safe because we only read row later)
        new_row = max((v["row"] for v in bm.values()), default=1) + 1
        bm[key] = {"value": val, "row": new_row}

def bm_del(bm_sheet, bm: dict, key: str) -> None:
    """Clear a key row without physically deleting (avoids row-shift bugs)."""
    if not bm_sheet or key not in bm:
        return
    r = bm[key]["row"]
    try:
        bm_sheet.update(f"A{r}:E{r}", [["", "", "", "", ""]])
    except Exception as e:
        print(f"[BM DEL] Error key={key}: {e}")
        return
    del bm[key]


# ── BotMemory: per-symbol float helpers ───────────────────────────────────────
# Values stored as int (price×100) to avoid float serialisation issues.

def bm_get_f(bm: dict, key: str) -> float:
    """Get an int-encoded float from bm (stored as price×100)."""
    raw = bm_get(bm, key)
    if not raw:
        return 0.0
    try:
        return int(raw) / 100.0
    except:
        return 0.0

def bm_set_f(bm_sheet, bm: dict, key: str, val: float,
             sym: str = "", ktype: str = "TRADE") -> None:
    """Store a float as int (×100) in BotMemory."""
    bm_set(bm_sheet, bm, key, str(int(round(val * 100))), sym, ktype)


# ── BotMemory: TSL / MAX / ATR / LP / EXDT per-symbol wrappers ───────────────

def get_tsl(bm: dict, key: str) -> float:
    return bm_get_f(bm, f"{key}_TSL")

def set_tsl(bm_sheet, bm: dict, key: str, sym: str, price: float) -> None:
    bm_set_f(bm_sheet, bm, f"{key}_TSL", price, sym, "TRADE")

def get_max_price(bm: dict, key: str) -> float:
    return bm_get_f(bm, f"{key}_MAX")

def set_max_price(bm_sheet, bm: dict, key: str, sym: str, price: float) -> None:
    cur = get_max_price(bm, key)
    if price <= cur:
        return
    bm_set_f(bm_sheet, bm, f"{key}_MAX", price, sym, "TRADE")

def get_atr_from_bm(bm: dict, key: str) -> float:
    return bm_get_f(bm, f"{key}_ATR")

def save_atr_to_bm(bm_sheet, bm: dict, key: str, sym: str, atr: float) -> None:
    bm_set_f(bm_sheet, bm, f"{key}_ATR", atr, sym, "TRADE")

def get_last_price(bm: dict, key: str) -> float:
    return bm_get_f(bm, f"{key}_LP")

def set_last_price(bm_sheet, bm: dict, key: str, sym: str, price: float) -> None:
    bm_set_f(bm_sheet, bm, f"{key}_LP", price, sym, "TRADE")

def get_exit_date(bm: dict, key: str) -> str:
    return bm_get(bm, f"{key}_EXDT")

def set_exit_date(bm_sheet, bm: dict, key: str, sym: str, date_str: str) -> None:
    bm_set(bm_sheet, bm, f"{key}_EXDT", date_str, sym, "TRADE")


# ── BotMemory: trade mode + capital ───────────────────────────────────────────

def get_trade_mode(bm: dict, key: str) -> str:
    val = bm_get(bm, f"{key}_MODE")
    return val if val in ("VCP", "MOM", "STD") else "STD"

def get_tsl_params(bm: dict, key: str) -> dict:
    mode = get_trade_mode(bm, key)
    return TSL_PARAMS[mode]

def get_capital_from_bm(bm: dict, key: str) -> int:
    """Read _CAP written by AppScript. Falls back to CAPITAL_STD."""
    cap_str = bm_get(bm, f"{key}_CAP")
    if cap_str:
        try:
            cap = int(cap_str)
            if cap in (CAPITAL_HIGH, CAPITAL_MED, CAPITAL_STD):
                return cap
        except:
            pass
    return CAPITAL_PER_TRADE


# ── BotMemory: exit flag ───────────────────────────────────────────────────────

def get_ex_flag_key(key: str, etime: str) -> str:
    entry_date_key = etime[:10].replace('-', '') if etime else "0"
    return f"{key}_EX_{entry_date_key}"

def ex_flag_exists(bm: dict, key: str, etime: str) -> bool:
    return bm_exists(bm, get_ex_flag_key(key, etime))

def set_ex_flag(bm_sheet, bm: dict, key: str, sym: str, etime: str) -> None:
    bm_set(bm_sheet, bm, get_ex_flag_key(key, etime), "1", sym, "FLAG")

def hold_warn_exists(bm: dict, key: str) -> bool:
    return bm_exists(bm, f"{key}_HOLD_WARN")

def set_hold_warn(bm_sheet, bm: dict, key: str, sym: str) -> None:
    bm_set(bm_sheet, bm, f"{key}_HOLD_WARN", "1", sym, "FLAG")


# ══════════════════════════════════════════════════════════════════════════════
# OPTIONS ADVISORY — v14.0: Advance gets CE flag, Premium gets full block
# ══════════════════════════════════════════════════════════════════════════════

def ce_candidate_flag(cp: float, atr: float, stage: str, is_bullish: bool) -> str:
    """
    CE candidate flag — shown in Advance entry alerts only.
    Informational only (no lot sizing, no specific expiry).
    ATR comes from Nifty200 col AC (real ATR14).

    ATR% < 1.5%    → no flag
    ATR% 1.5–2.5%  → normal mover: target +65%, SL -40% on premium
    ATR% > 2.5%    → fast mover:   target +50%, SL -35% on premium
    Not bullish    → no flag
    """
    if not is_bullish: return ""
    if cp <= 0 or atr <= 0: return ""

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
        target_pct = 50; sl_pct = 35; speed_tag = "⚡ Fast mover"
    else:
        target_pct = 65; sl_pct = 40; speed_tag = "📈 Normal mover"

    return (
        f"\n\n📊 <b>CE CANDIDATE</b> ({speed_tag})\n"
        f"   ATR%: {atr_pct:.1f}% | Strike hint: {strike_str}\n"
        f"   Target: +{target_pct}% on premium | SL: -{sl_pct}% on premium\n"
        f"   Entry only above ₹{cp + atr * 0.3:.1f} (breakout confirm)\n"
        f"   ⚠️ Check actual premium on Zerodha option chain"
    )

def build_options_premium(sym: str, cp: float, atr: float, stage: str,
                          is_bullish: bool) -> str:
    """
    Full options buying block — Premium channel ONLY.
    Includes: strike selection, entry trigger, target%, SL%, lot sizing note,
    expiry guidance. Separate from the simpler CE flag shown in Advance.
    """
    if not is_bullish: return ""
    if cp <= 0 or atr <= 0: return ""

    atr_pct = (atr / cp) * 100
    if atr_pct < 1.5: return ""

    gap = 5 if cp < 200 else (10 if cp < 500 else (20 if cp < 1000 else 50))
    atm_strike = round(cp / gap) * gap
    otm_strike = atm_strike + gap

    # Entry trigger: 0.3× ATR above CMP (same logic as CE flag)
    entry_trigger = round(cp + atr * 0.3, 1)

    # Premium budget estimate: ATM CE roughly 1–3% of CMP
    premium_est_low  = round(cp * 0.008)
    premium_est_high = round(cp * 0.025)

    # Lot sizing note: use 1 lot first (standard NSE lot = 75 for Nifty; for stocks, varies)
    # Keep generic — actual lot size must be checked on Zerodha
    if atr_pct >= 2.5:
        target_pct = 50; sl_pct = 35; speed_tag = "⚡ Fast mover"
        ce_strike  = int(otm_strike)
        strike_note = "OTM — breakout already running"
    else:
        target_pct = 65; sl_pct = 40; speed_tag = "📈 Normal mover"
        ce_strike  = int(atm_strike)
        strike_note = "ATM — maximum delta"

    # Expiry guidance
    from datetime import datetime
    dow = datetime.now(IST).weekday()   # 0=Mon … 6=Sun
    if dow >= 2:   # Wed Thu Fri
        expiry_note = "⚠️ Wednesday+ entry → prefer monthly expiry (weekly decays fast)"
    else:
        expiry_note = "Weekly expiry OK — enough days remain"

    return (
        f"\n\n👑 <b>OPTIONS ADVISORY — PREMIUM</b> ({speed_tag})\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"   Stock: {sym} @ ₹{cp:.0f} | ATR%: {atr_pct:.1f}%\n"
        f"   Strike: <b>{ce_strike} CE</b> ({strike_note})\n"
        f"   Entry trigger: ₹{entry_trigger} (wait for stock to cross this)\n"
        f"   Est. premium: ₹{premium_est_low}–₹{premium_est_high} per share\n"
        f"   Target: <b>+{target_pct}%</b> on premium\n"
        f"   SL: <b>-{sl_pct}%</b> on premium (strict — no averaging)\n"
        f"   Lot sizing: Start with 1 lot — check lot size on Zerodha\n"
        f"   {expiry_note}\n"
        f"   ⚠️ Options are leveraged. Size = max 5% of options capital."
    )


# ══════════════════════════════════════════════════════════════════════════════
# TSL CALCULATION — unchanged from v13.5
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
# MESSAGE BUILDERS — unchanged from v13.5 except Premium entry builder
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
    if ce_flag:
        msg += ce_flag
    return msg

def build_entry_premium(sym, cp, ent, init_sl, target, ttype, strat, stage,
                        priority, pos_size, capital, risk_rs, reward_rs,
                        rr_num, options_block, trade_mode, ce_flag="") -> str:
    """
    Premium entry alert = Advance alert (with CE flag) + full options block.
    ce_flag is included here too (same as Advance) so Premium sees everything.
    options_block is built by build_options_premium() separately.
    """
    base = build_entry_advance(sym, cp, ent, init_sl, target, ttype, strat,
                               stage, priority, pos_size, capital, risk_rs,
                               reward_rs, rr_num, trade_mode, ce_flag)
    return base + (options_block if options_block else "")

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
            return (ss.worksheet("AlertLog"),
                    ss.worksheet("History"),
                    ss.worksheet("Nifty200"),
                    ss.worksheet(BM_SHEET))
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


# ── ATR14 from Nifty200 — unchanged from v13.5 ───────────────────────────────

def _read_atr_from_nifty200(nifty_sheet, sym: str) -> float:
    """Read ATR14 from Nifty200 col AC (index 28) for sym."""
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


# ── Sector context — reads _SEC from BotMemory ────────────────────────────────

def get_sector_context(all_data: list, bm: dict) -> str:
    sector_counts = {}
    for r in all_data[1:16]:
        r = pad(list(r))
        if "WAITING" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper():
            continue
        sym = str(r[C_SYMBOL]).strip()
        if not sym:
            continue
        key = sym_key(sym)
        sec = bm_get(bm, f"{key}_SEC") or "Mixed"
        sector_counts[sec] = sector_counts.get(sec, 0) + 1

    if not sector_counts:
        return ""
    parts = [f"{s} ({c})" for s, c in sorted(sector_counts.items(), key=lambda x: -x[1])]
    return f"🔄 <b>Active Sectors:</b> {', '.join(parts[:4])}"


# ══════════════════════════════════════════════════════════════════════════════
# MAIN TRADING CYCLE — v14.0
# ══════════════════════════════════════════════════════════════════════════════

def run_trading_cycle():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    mins  = now.hour * 60 + now.minute

    if now.weekday() >= 5:
        print(f"[SKIP] Weekend ({now.strftime('%A')})"); return

    if not ((8 * 60 + 45) <= mins <= (15 * 60 + 45)):
        print(f"[SKIP] Outside window: {now.strftime('%H:%M')} IST"); return

    print(f"[START] {now.strftime('%Y-%m-%d %H:%M:%S')} IST | v14.0")

    log_sheet, hist_sheet, nifty_sheet, bm_sheet = get_sheets()

    # Load BotMemory once per run — all reads/writes use this dict
    bm = bm_load(bm_sheet)

    is_bullish = get_market_regime(nifty_sheet)

    # Automation switch — T2 still lives in AlertLog
    if str(log_sheet.acell("T2").value or "").strip().upper() != "YES":
        print("[SKIP] Automation OFF (T2 != YES)")
        return

    all_data   = log_sheet.get_all_values()
    trade_zone = [pad(list(r)) for r in all_data[1:16]]

    traded_rows = []
    for i, r in enumerate(trade_zone):
        status = str(r[C_STATUS]).upper()
        if "TRADED" in status and "EXITED" not in status:
            traded_rows.append((i + 2, r))

    print(f"[INFO] Active trades: {len(traded_rows)}/{MAX_TRADES}")

    # ── DEBUG: Good Morning window check ──────────────────────────────────────
    am_key = f"{today}_AM"
    print(f"[GM CHECK] time={now.strftime('%H:%M')} IST | "
          f"window={'YES' if (now.hour==8 and now.minute>=45) or (now.hour==9 and now.minute<=29) else 'NO'} | "
          f"AM_already_sent={bm_exists(bm, am_key)}")

    # ─────────────────────────────────────────────────────────────────────────
    # 1. GOOD MORNING  08:45–09:29 IST
    # ─────────────────────────────────────────────────────────────────────────
    if ((now.hour == 8 and now.minute >= 45) or
            (now.hour == 9 and now.minute <= 29)) and not bm_exists(bm, am_key):

        waiting_count = sum(
            1 for r in [pad(list(x)) for x in all_data[1:16]]
            if "WAITING" in str(r[C_STATUS]).upper()
        )
        sector_line = get_sector_context(all_data, bm)

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
            key      = sym_key(sym)
            sl_label = "TSL" if sl > to_f(r[C_INITIAL_SL]) else "SL"
            if cp > 0 and ent > 0:
                pnl   = (cp - ent) / ent * 100
                cap   = get_capital_from_bm(bm, key)
                pl_rs = round((cp - ent) / ent * cap)
                to_tgt = ((tgt - cp) / cp * 100) if cp > 0 else 0
                to_sl  = ((cp - sl) / cp * 100) if cp > 0 else 0
                em     = "🟢" if pnl >= 0 else "🔴"
                mode   = get_trade_mode(bm, key)
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
            get_capital_from_bm(bm, sym_key(r[C_SYMBOL]))
            for _, r in traded_rows if r[C_SYMBOL]
        )

        send_basic(build_gm_basic(today, len(lines), waiting_count, is_bullish, sector_line))
        full_gm = build_gm_advance(today, lines, deployed, waiting_count, sector_line)
        send_advance(full_gm)
        send_premium(full_gm)

        bm_set(bm_sheet, bm, am_key, "1", "", "FLAG")
        print(f"[GM] Sent and flagged: {am_key}")

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

        # ── Step A: Mark WAITING → TRADED ─────────────────────────────────────
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

            # RR re-validation — reject stale pre-v13.3 rows
            rr_raw = str(r[C_RR]).strip()
            if rr_raw:
                try:
                    rr_val = to_f(rr_raw.split(':')[-1])
                except Exception:
                    rr_val = 0.0
                if rr_val > 0 and rr_val < MIN_RR:
                    print(f"[SKIP] {sym}: RR 1:{rr_val:.1f} below MIN_RR {MIN_RR}")
                    continue

            key       = sym_key(sym)
            sheet_row = i + 2

            last_cp = get_last_price(bm, key)
            set_last_price(bm_sheet, bm, key, sym, cp)
            if last_cp > 0 and abs(cp - last_cp) < 0.01:
                print(f"[STALE] {sym}: price unchanged — skipping")
                continue

            exit_date = get_exit_date(bm, key)
            if exit_date:
                days_since = trading_days_since(exit_date, now)
                if days_since < 5:
                    print(f"[COOLDOWN] {sym}: {days_since} days since exit")
                    continue

            capital    = get_capital_from_bm(bm, key)
            pos_size_check = round(capital / cp) if cp > 0 else 0
            if pos_size_check < 2:
                print(f"[SKIP] {sym}: CMP ₹{cp:,.0f} too high for ₹{capital:,}")
                continue

            trade_mode = get_trade_mode(bm, key)
            etime      = now.strftime('%Y-%m-%d %H:%M:%S')

            log_sheet.update_cell(sheet_row, C_STATUS + 1,      "🟢 TRADED (PAPER)")
            log_sheet.update_cell(sheet_row, C_ENTRY_PRICE + 1, cp)
            log_sheet.update_cell(sheet_row, C_ENTRY_TIME + 1,  etime)
            log_sheet.update_cell(sheet_row, C_TRAIL_SL + 1,    init_sl)

            risk   = cp - init_sl
            reward = target - cp
            rr_num = (reward / risk) if risk > 0 else 0
            log_sheet.update_cell(sheet_row, C_RR + 1, f"1:{rr_num:.1f}")

            # Read ATR14 directly from Nifty200
            atr_est = _read_atr_from_nifty200(nifty_sheet, sym)
            if atr_est <= 0:
                _mult   = 2 if "Intraday" in ttype else 4 if "Positional" in ttype else 3
                atr_est = (target - cp) / _mult if target > cp else 0
                print(f"[ATR] {sym}: fallback atr_est={atr_est:.2f}")
            else:
                print(f"[ATR] {sym}: ATR14={atr_est:.2f} from Nifty200")

            save_atr_to_bm(bm_sheet, bm, key, sym, atr_est)
            set_tsl(bm_sheet, bm, key, sym, init_sl)
            set_max_price(bm_sheet, bm, key, sym, cp)
            # Clear any stale exit flag for this entry date
            bm_del(bm_sheet, bm, get_ex_flag_key(key, etime))

            updated_r                = list(r)
            updated_r[C_STATUS]      = "🟢 TRADED (PAPER)"
            updated_r[C_ENTRY_PRICE] = cp
            updated_r[C_ENTRY_TIME]  = etime
            updated_r[C_TRAIL_SL]    = init_sl
            traded_rows.append((sheet_row, updated_r))

            atr      = atr_est
            c_flag   = ce_candidate_flag(cp, atr, stage, is_bullish)
            o_block  = build_options_premium(sym, cp, atr, stage, is_bullish)

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
                                    rr_num, o_block, trade_mode, c_flag)
            )
            print(f"[ENTRY] {sym} @ ₹{cp} | ₹{capital:,} | {pos_size}sh | {ttype} | {trade_mode} | SL ₹{init_sl} | T ₹{target}")

        # ── Step B: Monitor active trades ──────────────────────────────────────
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

            set_max_price(bm_sheet, bm, key, sym, cp)
            pnl_pct    = (cp - ent) / ent * 100
            atr        = get_atr_from_bm(bm, key)
            if atr <= 0:
                _mult = 4 if "Positional" in ttype else 2 if "Intraday" in ttype else 3
                atr   = (tgt - ent) / _mult if tgt > ent else ent * 0.02

            days_held  = calc_hold_days(etime, now)
            trade_mode = get_trade_mode(bm, key)
            tsl_params = TSL_PARAMS[trade_mode]
            capital    = get_capital_from_bm(bm, key)

            new_tsl = calc_new_tsl(cp, ent, init_sl, atr, ttype, tsl_params)
            bm_tsl  = get_tsl(bm, key)
            new_tsl = max(new_tsl, bm_tsl, cur_tsl)

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
                set_tsl(bm_sheet, bm, key, sym, new_tsl)
                print(f"[TSL] {sym} [{trade_mode}]: ₹{cur_tsl:.2f}→₹{new_tsl:.2f}")

            tsl_hit    = (new_tsl > 0 and cp <= new_tsl)
            target_hit = (tgt > 0 and cp >= tgt)
            hard_loss  = pnl_pct < -HARD_LOSS_PCT

            # ── Hard loss exit ─────────────────────────────────────────────────
            if hard_loss and not ex_flag_exists(bm, key, etime):
                pl_rupees = round((cp - ent) / ent * capital, 2)
                hold_str  = calc_hold_str(etime, now)
                max_price = get_max_price(bm, key)

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
                set_ex_flag(bm_sheet, bm, key, sym, etime)
                set_exit_date(bm_sheet, bm, key, sym, now.strftime('%Y-%m-%d'))
                print(f"[HARD LOSS] {sym} | {pnl_pct:+.2f}% | ₹{pl_rupees:+.0f}")
                continue

            # ── Normal exit ────────────────────────────────────────────────────
            is_pos        = "Positional" in ttype or "positional" in ttype.lower()
            min_hold      = MIN_HOLD_POS if is_pos else MIN_HOLD_SWING
            near_hard_loss = pnl_pct < -4.0
            skip_exit = (
                days_held < min_hold
                and not target_hit
                and not hard_loss
                and not (near_hard_loss and not is_bullish)
            )

            if (tsl_hit or target_hit) and not ex_flag_exists(bm, key, etime) and not skip_exit:
                exit_reason = ("🎯 TARGET HIT"    if target_hit else
                               "🔒 TRAILING SL"   if new_tsl > init_sl else
                               "🚨 INITIAL SL HIT")
                result_sym  = "WIN ✅" if (target_hit or pnl_pct > 0) else "LOSS 🔴"
                hold_str    = calc_hold_str(etime, now)
                max_price   = get_max_price(bm, key)
                pl_rupees   = round((cp - ent) / ent * capital, 2)

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
                    pl_rupees, "—",
                ])
                log_sheet.update_cell(sheet_row, C_STATUS + 1, "EXITED")
                set_ex_flag(bm_sheet, bm, key, sym, etime)
                set_exit_date(bm_sheet, bm, key, sym, now.strftime('%Y-%m-%d'))
                print(f"[EXIT] {sym} | {result_sym} | {pnl_pct:+.2f}% | ₹{pl_rupees:+.0f}")

            elif tsl_hit and skip_exit:
                print(f"[HOLD] {sym}: SL touched Day {days_held + 1} < {min_hold} min hold")
                if not hold_warn_exists(bm, key):
                    regime_note = "🐂 Bullish — recovery possible" if is_bullish else "🐻 Bearish — watching closely"
                    hold_msg = (
                        f"⚠️ <b>MIN HOLD ACTIVE — {sym}</b>\n"
                        f"[{ttype}] [{trade_mode}] touched SL ₹{new_tsl:.2f} "
                        f"but only Day {days_held + 1} of {min_hold}.\n"
                        f"Holding until Day {min_hold} unless loss > {HARD_LOSS_PCT}%.\n"
                        f"Current P/L: {pnl_pct:+.2f}%\n{regime_note}"
                    )
                    send_advance(hold_msg); send_premium(hold_msg)
                    set_hold_warn(bm_sheet, bm, key, sym)

        # Batch TSL writes
        if tsl_cell_updates:
            cells = []
            for (sr, new_tsl) in tsl_cell_updates:
                c = log_sheet.cell(sr, C_TRAIL_SL + 1)
                c.value = new_tsl
                cells.append(c)
            log_sheet.update_cells(cells)
            print(f"[TSL WRITE] {len(cells)} updates")

        # ── Send all alerts ────────────────────────────────────────────────────
        if exit_alerts_basic:
            for msg in exit_alerts_basic: send_basic(msg)

        if exit_alerts_advance:
            header    = f"⚡ <b>EXIT REPORT — {now.strftime('%H:%M IST')}</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
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
    noon_key = f"{today}_NOON"
    if now.hour == 12 and 28 <= now.minute <= 38 and not bm_exists(bm, noon_key):
        fresh     = log_sheet.get_all_values()
        live_rows = [
            pad(list(r)) for r in fresh[1:16]
            if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
            and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        ]
        wins = losses = 0
        lines_advance = []
        lines_basic   = []
        for r in live_rows:
            sym   = r[C_SYMBOL]; cp = to_f(r[C_LIVE_PRICE]); ent = to_f(r[C_ENTRY_PRICE])
            tsl   = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
            ttype = str(r[C_TRADE_TYPE])
            if not price_sanity(sym, cp, ent): continue
            pnl = (cp - ent) / ent * 100
            em  = "🟢" if pnl >= 0 else "🔴"
            key = sym_key(sym)
            mode_tag = {"VCP": "🎯", "MOM": "🚀", "STD": "📊"}.get(get_trade_mode(bm, key), "📊")
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
        full_noon = (
            f"☀️ <b>MID-DAY PULSE — {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Open: {len(lines_advance)} | 🟢 {wins} | 🔴 {losses}\n\n"
            + ("\n".join(lines_advance) if lines_advance else "📭 No open trades")
        )
        send_advance(full_noon); send_premium(full_noon)
        bm_set(bm_sheet, bm, noon_key, "1", "", "FLAG")

    # ─────────────────────────────────────────────────────────────────────────
    # 4. MARKET CLOSE SUMMARY  15:15–15:45 IST
    # ─────────────────────────────────────────────────────────────────────────
    pm_key = f"{today}_PM"
    if now.hour == 15 and 15 <= now.minute <= 45 and not bm_exists(bm, pm_key):
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

        bm_set(bm_sheet, bm, pm_key, "1", "", "FLAG")

    print(f"[DONE] {now.strftime('%H:%M:%S')} IST | v14.0 | BotMemory: {len(bm)} keys")


# ══════════════════════════════════════════════════════════════════════════════
# WEEKLY SUMMARY — unchanged from v13.5 (except get_sheets signature)
# ══════════════════════════════════════════════════════════════════════════════

def run_weekly_summary():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    print("[WEEKLY] Fetching weekly + monthly summary...")

    log_sheet, hist_sheet, _, bm_sheet = get_sheets()
    bm = bm_load(bm_sheet)

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
# DAILY SUMMARY — unchanged from v13.5 (except get_sheets signature + bm)
# ══════════════════════════════════════════════════════════════════════════════

def run_daily_summary():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    print("[SUMMARY] Fetching portfolio summary...")

    log_sheet, hist_sheet, _, bm_sheet = get_sheets()
    bm = bm_load(bm_sheet)
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
        cap   = get_capital_from_bm(bm, key)
        pl_rs = round((cp - ent) / ent * cap)
        days  = calc_hold_days(etime, now)
        em    = "🟢" if pnl >= 0 else "🔴"
        mode  = get_trade_mode(bm, key)
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
        mode = get_trade_mode(bm, key)
        cap  = get_capital_from_bm(bm, key)
        wait_lines.append(
            f"  ⏳ <b>{r[C_SYMBOL]}</b> [{r[C_TRADE_TYPE]}] [{mode}] "
            f"₹{cap:,} | P:{r[C_PRIORITY]}"
        )

    msg = (
        f"📊 <b>PORTFOLIO SUMMARY — v14.0</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 {now.strftime('%Y-%m-%d %H:%M')} IST\n"
        f"📈 Open: {len(open_rows)}/{MAX_TRADES} | ⏳ Waiting: {len(waiting_rows)}/{MAX_WAITING}\n"
        f"💰 Deployed: ₹{sum(get_capital_from_bm(bm, sym_key(r[C_SYMBOL])) for r in open_rows):,}\n"
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
# TEST TELEGRAM
# ══════════════════════════════════════════════════════════════════════════════

def run_test_telegram():
    now = datetime.now(IST)
    print("[TEST] Sending Telegram test messages to all 3 channels...")
    test_msg = (
        f"✅ <b>TELEGRAM TEST — OK</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 Bot: AI360 Trading v14.0\n"
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
