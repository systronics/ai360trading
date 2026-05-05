"""
AI360 TRADING BOT — v15.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v15.0 CHANGES vs v13.5 (deploy alongside AppScript v14.0):

1. BOTMEMORY SHEET MIGRATION [COMPLETE — T4 FULLY REMOVED]
   All memory (trade keys + daily flags) now read/written via
   the BotMemory sheet (cols A-E: Key, Value, UpdatedAt, Symbol, KeyType).
   T4 cell is no longer read or written. clean_mem() removed.
   New helpers: _bm_load(), _bm_get(), _bm_set(), _bm_del(),
   _bm_exists(), _bm_purge().

   Keys migrated to BotMemory (KeyType=TRADE):
     {sym}_TSL, {sym}_MAX, {sym}_ATR, {sym}_LP, {sym}_EXDT, {sym}_RANK
   Keys migrated to BotMemory (KeyType=FLAG):
     {today}_AM, {today}_NOON, {today}_PM
     {sym}_DW_{today} (drawdown warned)
     {sym}_HOLD_WARN_{today} (min-hold warning)
     {sym}_EX_{entry_date_key} (exit dedup flag)
   Keys read from BotMemory (written by AppScript v14.0):
     {sym}_CAP, {sym}_MODE, {sym}_SEC

2. MAX_TRADES: 5 -> 8 | MAX_DEPLOYED: Rs45,000 -> Rs1,04,000
   Capital tiers unchanged (Rs7K / Rs10K / Rs13K).
   All 8 trade slots now monitored every 5-min run.

3. SECTOR_RANK INTEGRATION (Nifty200 col AI, 0-based index 34)
   - Read at entry time from Nifty200, stored in BotMemory as {sym}_RANK
   - CE/Options flag: only fires for sector_rank <= 5 (top-ranked = fast movers)
   - Rank shown in entry alert (Advance + Premium channels)
   - Rank shown in daily summary waiting list

4. ALERT FIXES
   a. Good Morning: correctly shows all held trades P/L%, TSL
      distance, and target distance. Was broken because T4 flags
      were not persisting. Now persists via BotMemory FLAG entries.
   b. Market close PM summary: now shows open positions P/L% +
      unrealised P/L in Rs after entry. Same root cause fixed.
   c. Mid-day NOON pulse: now shows Rs P/L per trade + total.
   d. Drawdown alert (NEW): sent to Advance+Premium when open
      trade drops > 3% from entry, once per trade per day.
      Key: {sym}_DW_{today}

5. TELEGRAM CHANNEL SWAP FIX
   CHAT_ADVANCE now correctly reads CHAT_ID_ADVANCE secret.
   CHAT_PREMIUM now correctly reads CHAT_ID_PREMIUM secret.

6. Version tag updated to v15.0 in test message.

WHAT IS IDENTICAL TO v13.5:
   - All TSL_PARAMS (VCP/MOM/STD breakeven/lock/trail/atr_mult/gap_lock)
   - calc_new_tsl() logic
   - MIN_HOLD_SWING=2, MIN_HOLD_POS=3, HARD_LOSS_PCT=5.0
   - options_hint() function
   - get_sheets() retry logic (now returns bm_sheet as 4th element)
   - price_sanity(), trading_days_since(), calc_hold_*()
   - Step A WAITING->TRADED logic (RR re-validation kept)
   - Step B TSL monitoring logic
   - History sheet append format (18 cols A-R)
   - Weekly + daily summary structure

DEPLOY CHECKLIST:
   1. Ensure AppScript v14.0 is deployed (BotMemory sheet exists with header row)
   2. T2 = NO (pause bot)
   3. Clear all data rows in BotMemory sheet (keep header A1:E1)
   4. Replace trading_bot.py with this file in GitHub repo
   5. T2 = YES (resume)
   DO NOT deploy without AppScript v14.0 in place.

ALERTLOG COLUMN MAP (0-based) - unchanged:
  A=0  Signal Time       B=1  Symbol
  C=2  Live Price        D=3  Priority Score
  E=4  Trade Type        F=5  Strategy
  G=6  Breakout Stage    H=7  Initial SL
  I=8  Target            J=9  RR Ratio
  K=10 Trade Status      L=11 Entry Price
  M=12 Entry Time        N=13 Days in Trade
  O=14 Trailing SL       P=15 P/L%
  Q=16 ATH Warning       R=17 Risk Rs
  S=18 Position Size     T=19 SYSTEM CONTROL
  T2 = YES/NO automation switch (still used)
  T4 = NO LONGER USED by v15.0

BOTMEMORY SHEET (cols A-E):
  A: Key   B: Value   C: UpdatedAt   D: Symbol   E: KeyType
  KeyType: FLAG (purged after 14d) | TRADE | STATE
"""

import os, json, pytz, requests, gspread, time
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

IST      = pytz.timezone('Asia/Kolkata')
TG_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')  

# ── 3 Telegram channels — FIXED: channel variable swap corrected ──────────────
CHAT_BASIC   = os.environ.get('TELEGRAM_CHAT_ID')
CHAT_ADVANCE = os.environ.get('CHAT_ID_ADVANCE')   # previously reading CHAT_ID_PREMIUM (WRONG)
CHAT_PREMIUM = os.environ.get('CHAT_ID_PREMIUM')   # previously reading CHAT_ID_ADVANCE  (WRONG)

SHEET_NAME = "Ai360tradingAlgo"
BM_SHEET   = "BotMemory"

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

# ── Capital config ─────────────────────────────────────────────────────────────
CAPITAL_PER_TRADE = 10_000   # default / fallback
CAPITAL_STD       =  7_000
CAPITAL_MED       = 10_000
CAPITAL_HIGH      = 13_000
MAX_TRADES        = 8        # was 5
MAX_WAITING       = 10
MAX_DEPLOYED      = 104_000  # was 45,000 -> 8 x 13,000

MIN_RR         = 1.8
HARD_LOSS_PCT  = 5.0
MIN_HOLD_SWING = 2
MIN_HOLD_POS   = 3
TSL_GAP_LOCK_FRAC = 0.5

# ── Drawdown warning threshold ────────────────────────────────────────────────
DRAWDOWN_WARN_PCT = 3.0   # alert when trade drops > 3% from entry

# ── BotMemory purge — FLAG entries older than 14 days are removed ─────────────
BM_PURGE_DAYS = 14

# ── Sector rank thresholds ────────────────────────────────────────────────────
OPTIONS_RANK_MAX = 5   # only rank 1-5 triggers CE candidate flag
RANK_BONUS_MAX   = 3   # rank 1-3 shown in entry alert as top pick

# ── TSL parameters — identical to v13.5 ──────────────────────────────────────
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


# =============================================================================
# TELEGRAM
# =============================================================================

def _send_one(chat_id: str, msg: str) -> bool:
    if not chat_id or not TG_TOKEN:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
            timeout=15,
        )
        if r.status_code != 200:
            print(f"[TG FAIL] chat={chat_id} status={r.status_code}: {r.text[:100]}")
            return False
        return True
    except Exception as e:
        print(f"[TG ERROR] chat={chat_id} {e}")
        return False

def send_basic(msg):              return _send_one(CHAT_BASIC,   msg)
def send_advance(msg):            return _send_one(CHAT_ADVANCE, msg)
def send_premium(msg):            return _send_one(CHAT_PREMIUM, msg)
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


# =============================================================================
# BOTMEMORY SHEET HELPERS  (v15.0 — replaces all T4 string helpers)
# =============================================================================
# BotMemory sheet cols (1-based for gspread writes, 0-based in list reads):
#   A(0)=Key  B(1)=Value  C(2)=UpdatedAt  D(3)=Symbol  E(4)=KeyType
# Row 1 = header, data starts row 2.

def _bm_load(bm_sheet) -> dict:
    """
    Load entire BotMemory sheet into a dict in ONE API call.
    Returns: { key_str: { "value": str, "row": int (1-based) } }
    """
    bm = {}
    try:
        all_vals = bm_sheet.get_all_values()   # single API call
        for i, row in enumerate(all_vals[1:], start=2):   # skip header
            key = str(row[0]).strip() if len(row) > 0 else ""
            if not key:
                continue
            val = str(row[1]).strip() if len(row) > 1 else ""
            bm[key] = {"value": val, "row": i}
    except Exception as e:
        print(f"[BM LOAD] Error: {e}")
    return bm

def _bm_get(bm: dict, key: str) -> str:
    """Return value for key, or empty string if missing."""
    return bm[key]["value"] if key in bm else ""

def _bm_exists(bm: dict, key: str) -> bool:
    return key in bm

def _bm_set(bm_sheet, bm: dict, key: str, val: str,
            sym: str = "", ktype: str = "STATE") -> None:
    """
    Write or update a key in BotMemory sheet.
    Updates in-place if row exists, appends new row if not.
    Also mutates bm dict so subsequent _bm_get sees new value immediately.
    """
    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    try:
        if key in bm:
            r = bm[key]["row"]
            # Batch the two cell writes into one update call
            bm_sheet.update(f"B{r}:C{r}", [[val, now_str]])
            bm[key]["value"] = val
        else:
            bm_sheet.append_row([key, val, now_str, sym or "", ktype])
            # Estimate new row index (append_row goes to next blank row)
            new_row = max(bm[k]["row"] for k in bm) + 1 if bm else 2
            bm[key] = {"value": val, "row": new_row}
    except Exception as e:
        print(f"[BM SET] Error writing key={key}: {e}")

def _bm_del(bm_sheet, bm: dict, key: str) -> None:
    """
    Blank a key's row in BotMemory (never deletes rows — avoids row-shift bugs).
    Removes key from bm dict.
    """
    if key not in bm:
        return
    try:
        r = bm[key]["row"]
        bm_sheet.update(f"A{r}:E{r}", [["", "", "", "", ""]])
        del bm[key]
    except Exception as e:
        print(f"[BM DEL] Error deleting key={key}: {e}")

def _bm_purge(bm_sheet, bm: dict) -> None:
    """
    Remove FLAG-type entries where key starts with a date older than BM_PURGE_DAYS.
    Called once at start of each run. Cheap — operates on already-loaded bm dict.
    """
    cutoff = (datetime.now(IST) - timedelta(days=BM_PURGE_DAYS)).strftime("%Y-%m-%d")
    to_del = [
        k for k in list(bm.keys())
        if len(k) >= 10 and k[4] == "-" and k[7] == "-" and k[:10] < cutoff
    ]
    for key in to_del:
        _bm_del(bm_sheet, bm, key)
        print(f"[BM PURGE] Removed old flag: {key}")


# =============================================================================
# TRADE MEMORY ACCESSORS  — all backed by BotMemory sheet
# =============================================================================

def get_tsl(bm: dict, key: str) -> float:
    try:  return float(_bm_get(bm, f"{key}_TSL") or 0)
    except: return 0.0

def set_tsl(bm_sheet, bm: dict, key: str, price: float) -> None:
    _bm_set(bm_sheet, bm, f"{key}_TSL", f"{price:.2f}", key, "TRADE")

def get_max_price(bm: dict, key: str) -> float:
    try:  return float(_bm_get(bm, f"{key}_MAX") or 0)
    except: return 0.0

def set_max_price(bm_sheet, bm: dict, key: str, price: float) -> None:
    if price > get_max_price(bm, key):
        _bm_set(bm_sheet, bm, f"{key}_MAX", f"{price:.2f}", key, "TRADE")

def get_atr(bm: dict, key: str) -> float:
    try:  return float(_bm_get(bm, f"{key}_ATR") or 0)
    except: return 0.0

def set_atr(bm_sheet, bm: dict, key: str, atr: float) -> None:
    _bm_set(bm_sheet, bm, f"{key}_ATR", f"{atr:.4f}", key, "TRADE")

def get_last_price(bm: dict, key: str) -> float:
    try:  return float(_bm_get(bm, f"{key}_LP") or 0)
    except: return 0.0

def set_last_price(bm_sheet, bm: dict, key: str, price: float) -> None:
    _bm_set(bm_sheet, bm, f"{key}_LP", f"{price:.2f}", key, "TRADE")

def get_exit_date(bm: dict, key: str) -> str:
    return _bm_get(bm, f"{key}_EXDT")

def set_exit_date(bm_sheet, bm: dict, key: str, date_str: str) -> None:
    _bm_set(bm_sheet, bm, f"{key}_EXDT", date_str, key, "TRADE")

def get_trade_mode(bm: dict, key: str) -> str:
    val = _bm_get(bm, f"{key}_MODE")
    return val if val in ("VCP", "MOM", "STD") else "STD"

def get_capital(bm: dict, key: str) -> int:
    raw = _bm_get(bm, f"{key}_CAP")
    try:
        cap = int(float(raw))
        if cap in (CAPITAL_STD, CAPITAL_MED, CAPITAL_HIGH):
            return cap
    except:
        pass
    return CAPITAL_PER_TRADE

def get_sector(bm: dict, key: str) -> str:
    return _bm_get(bm, f"{key}_SEC") or "Mixed"

def get_sector_rank(bm: dict, key: str) -> int:
    try:  return int(float(_bm_get(bm, f"{key}_RANK") or 0))
    except: return 0


# =============================================================================
# GENERAL HELPERS
# =============================================================================

def to_f(val) -> float:
    try:
        return float(str(val).replace(',', '').replace('\u20b9', '').replace('%', '').strip())
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
        return "\u2014"

def is_market_hours(now: datetime) -> bool:
    if now.weekday() >= 5: return False
    mins = now.hour * 60 + now.minute
    return (9 * 60 + 15) <= mins <= (15 * 60 + 30)

def price_sanity(sym, cp, ent) -> bool:
    if cp <= 0 or ent <= 0:
        print(f"[WARN] {sym}: zero price cp={cp} ent={ent}"); return False
    if cp > ent * 4:
        print(f"[WARN] {sym}: LTP Rs{cp} > 4x entry Rs{ent}"); return False
    if cp < ent * 0.1:
        print(f"[WARN] {sym}: LTP Rs{cp} < 10% of entry Rs{ent}"); return False
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
        f"\n\n\U0001f4ca <b>OPTIONS ADVISORY</b> (informational only)\n"
        f"   Stock: {sym} @ Rs{cp:.0f}\n"
        f"   Expected move: ~Rs{expected_move:.0f} ({(expected_move/cp*100):.1f}%)\n"
        f"   CE strike hint: {int(strike_ce)} CE (buy on breakout confirm)\n"
        f"   \u26a0\ufe0f Options are leveraged \u2014 size carefully"
    )

def ce_candidate_flag(cp: float, atr: float, stage: str,
                      is_bullish: bool, sector_rank: int = 0) -> str:
    """
    CE candidate flag (v15.0).
    Only fires when market is bullish AND sector_rank <= OPTIONS_RANK_MAX (top 5).
    Rank 0 = AppScript has not written _RANK yet -> allow through.
    ATR% < 1.5% -> skip (premium decay risk on slow movers).
    """
    if not is_bullish: return ""
    if cp <= 0 or atr <= 0: return ""
    # Sector rank gate: skip if outside top 5 (0 = unknown, allow)
    if sector_rank > OPTIONS_RANK_MAX and sector_rank != 0: return ""

    atr_pct = (atr / cp) * 100
    if atr_pct < 1.5: return ""

    gap        = 5 if cp < 200 else (10 if cp < 500 else (20 if cp < 1000 else 50))
    atm_strike = round(cp / gap) * gap
    otm_strike = atm_strike + gap

    if "BREAKOUT CONFIRMED" in stage:
        strike_str = f"{int(otm_strike)} CE (OTM \u2014 breakout in progress)"
    else:
        strike_str = f"{int(atm_strike)} CE or {int(otm_strike)} CE"

    if atr_pct >= 2.5:
        target_pct, sl_pct, speed_tag = 50, 35, "\u26a1 Fast mover"
    else:
        target_pct, sl_pct, speed_tag = 65, 40, "\U0001f4c8 Normal mover"

    rank_note = f" | Sector Rank #{sector_rank}" if sector_rank > 0 else ""
    return (
        f"\n\n\U0001f4ca <b>CE CANDIDATE</b> ({speed_tag}{rank_note})\n"
        f"   ATR%: {atr_pct:.1f}% | Strike: {strike_str}\n"
        f"   Target: +{target_pct}% on premium | SL: -{sl_pct}% on premium\n"
        f"   Entry: Only above Rs{cp + atr * 0.3:.1f} (breakout confirm)\n"
        f"   \u26a0\ufe0f Check actual premium on Zerodha option chain\n"
        f"   \u26a0\ufe0f Wednesday entry \u2192 prefer monthly expiry"
    )


# =============================================================================
# TSL CALCULATION — identical to v13.5
# =============================================================================

def calc_new_tsl(cp: float, ent: float, init_sl: float, atr: float,
                 ttype: str = "", params: dict = None) -> float:
    if params is None: params = TSL_PARAMS["STD"]
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


# =============================================================================
# MESSAGE BUILDERS
# =============================================================================

def build_gm_basic(today, trade_count, waiting_count, is_bullish, sector_line=""):
    mood = "\U0001f402 Bullish" if is_bullish else "\U0001f43b Bearish"
    msg  = (
        f"\U0001f305 <b>GOOD MORNING \u2014 {today}</b>\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f4c8 AI360 Scanner is LIVE\n"
        f"Market Regime: <b>{mood}</b>\n"
        f"Active Signals: {trade_count}/{MAX_TRADES}\n"
        f"Candidates Ready: {waiting_count}\n"
    )
    if sector_line: msg += f"{sector_line}\n"
    msg += f"\n\U0001f514 <i>Want full entry/exit levels?\nJoin Signal Channel \u2192 ai360trading.in/membership</i>"
    return msg

def build_gm_advance(today, lines, deployed, waiting_count, sector_line=""):
    body = "\n\n".join(lines) if lines else "\U0001f4ed No open trades currently"
    msg  = (
        f"\U0001f305 <b>GOOD MORNING \u2014 {today}</b>\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f4c8 Open: {len(lines)}/{MAX_TRADES} | \u23f3 Waiting: {waiting_count}/{MAX_WAITING}\n"
        f"\U0001f4b0 Deployed: ~Rs{deployed:,}\n"
    )
    if sector_line: msg += f"{sector_line}\n"
    msg += f"\n{body}"
    return msg

def build_entry_advance(sym, cp, init_sl, target, ttype, strat, stage,
                        priority, pos_size, capital, risk_rs, reward_rs,
                        rr_num, trade_mode, sector_rank=0, ce_flag=""):
    mode_tag  = {"VCP": "\U0001f3af VCP Breakout", "MOM": "\U0001f680 Momentum", "STD": "\U0001f4ca Swing"}.get(trade_mode, "\U0001f4ca Swing")
    rank_note = f" | Sector Rank #{sector_rank}" if sector_rank > 0 else ""
    top_note  = " \U0001f3c6 TOP PICK" if 0 < sector_rank <= RANK_BONUS_MAX else ""
    msg = (
        f"\U0001f680 <b>TRADE ENTERED</b>\n\n"
        f"<b>Stock:</b> {sym}{rank_note}{top_note}\n"
        f"<b>Type:</b> {ttype} [{mode_tag}]\n"
        f"<b>Entry Price:</b> Rs{cp:.2f}\n"
        f"<b>Strategy:</b> {strat} | {stage}\n"
        f"<b>Qty:</b> {pos_size} shares @ Rs{capital:,} (Priority {priority})\n"
        f"<b>Initial SL:</b> Rs{init_sl:.2f} (Risk: Rs{risk_rs:,})\n"
        f"<b>Target:</b> Rs{target:.2f} (Reward: Rs{reward_rs:,})\n"
        f"<b>RR Ratio:</b> 1:{rr_num:.1f}\n"
        f"<b>Priority:</b> {priority}/30"
    )
    if ce_flag: msg += ce_flag
    return msg

def build_entry_premium(sym, cp, init_sl, target, ttype, strat, stage,
                        priority, pos_size, capital, risk_rs, reward_rs,
                        rr_num, o_hint, trade_mode, sector_rank=0, ce_flag=""):
    base = build_entry_advance(sym, cp, init_sl, target, ttype, strat, stage,
                               priority, pos_size, capital, risk_rs, reward_rs,
                               rr_num, trade_mode, sector_rank, ce_flag)
    return base + (o_hint if o_hint else "")

def build_exit_advance(sym, ttype, ent, cp, pnl_pct, pl_rupees,
                       hold_str, max_price, strat, exit_reason):
    em = "\U0001f3af" if "TARGET" in exit_reason else "\u26a1"
    return (
        f"{em} <b>{exit_reason}</b>\n"
        f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f4cc <b>{sym}</b> [{ttype}]\n"
        f"   Entry Rs{ent:.2f} \u2192 Exit Rs{cp:.2f}\n"
        f"   P/L: <b>{pnl_pct:+.2f}%</b> = <b>Rs{pl_rupees:+.0f}</b>\n"
        f"   Hold: {hold_str} | Max seen: Rs{max_price:.2f}\n"
        f"   Strategy: {strat}"
    )

def build_exit_basic(sym, pnl_pct, exit_reason):
    em  = "\u2705" if pnl_pct > 0 else "\u274c"
    res = "WIN" if pnl_pct > 0 else "LOSS"
    return (
        f"{em} <b>SIGNAL CLOSED \u2014 {sym}</b>\n"
        f"Result: <b>{res} ({pnl_pct:+.2f}%)</b>\n\n"
        f"\U0001f514 <i>Get entry/exit alerts in real time\n"
        f"\u2192 ai360trading.in/membership</i>"
    )


# =============================================================================
# GOOGLE SHEETS
# =============================================================================

def get_sheets():
    """Returns (log_sheet, hist_sheet, nifty_sheet, bm_sheet)."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_JSON')), scope
    )
    delays     = [5, 15, 30, 60, 120]
    last_error = None
    for attempt, delay in enumerate(delays):
        try:
            ss = gspread.authorize(creds).open(SHEET_NAME)
            return (
                ss.worksheet("AlertLog"),
                ss.worksheet("History"),
                ss.worksheet("Nifty200"),
                ss.worksheet(BM_SHEET),
            )
        except gspread.exceptions.APIError as e:
            status = e.response.status_code if hasattr(e, 'response') else 0
            if status in (429, 500, 502, 503, 504):
                last_error = e
                if attempt < len(delays) - 1:
                    print(f"[RETRY] Google Sheets {status} \u2014 retry {attempt+1} in {delay}s...")
                    time.sleep(delay)
                    continue
            raise
    raise last_error

def get_market_regime(nifty_sheet) -> bool:
    try:
        row = nifty_sheet.row_values(2)
        if not row or "NIFTY" not in str(row[0]).upper():
            print("[REGIME] NIFTY50 row not found \u2014 defaulting to bullish"); return True
        cmp_nifty = to_f(row[2]); dma20 = to_f(row[4])
        if cmp_nifty <= 0 or dma20 <= 0:
            print("[REGIME] Invalid Nifty data \u2014 defaulting to bullish"); return True
        bullish = cmp_nifty >= dma20
        print(f"[REGIME] Nifty CMP Rs{cmp_nifty:.0f} vs 20DMA Rs{dma20:.0f} \u2192 {'BULLISH' if bullish else 'BEARISH'}")
        return bullish
    except Exception as e:
        print(f"[REGIME] Error: {e} \u2014 defaulting to bullish"); return True

def _read_atr_from_nifty200(nifty_data: list, sym: str) -> float:
    """Read ATR14 from pre-fetched Nifty200 data, col AC (0-based index 28)."""
    for row in nifty_data[1:]:
        if str(row[0]).strip() == sym.strip():
            if len(row) > 28:
                val = to_f(row[28])
                if val > 0: return val
            break
    return 0.0

def _read_sector_rank_from_nifty200(nifty_data: list, sym: str) -> int:
    """Read Sector_Rank from pre-fetched Nifty200 data, col AI (0-based index 34)."""
    for row in nifty_data[1:]:
        if str(row[0]).strip() == sym.strip():
            if len(row) > 34:
                val = to_f(row[34])
                if val > 0: return int(val)
            break
    return 0

def get_sector_context(all_data: list, bm: dict) -> str:
    sector_counts = {}
    for r in all_data[1:16]:
        r = pad(list(r))
        if "WAITING" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper(): continue
        sym = str(r[C_SYMBOL]).strip()
        if not sym: continue
        sec = get_sector(bm, sym_key(sym))
        sector_counts[sec] = sector_counts.get(sec, 0) + 1
    if not sector_counts: return ""
    parts = [f"{s} ({c})" for s, c in sorted(sector_counts.items(), key=lambda x: -x[1])]
    return f"\U0001f504 <b>Active Sectors:</b> {', '.join(parts[:4])}"


# =============================================================================
# MAIN TRADING CYCLE
# =============================================================================

def run_trading_cycle():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    mins  = now.hour * 60 + now.minute

    if now.weekday() >= 5:
        print(f"[SKIP] Weekend ({now.strftime('%A')})"); return
    if not ((8 * 60 + 45) <= mins <= (15 * 60 + 45)):
        print(f"[SKIP] Outside window: {now.strftime('%H:%M')} IST"); return

    print(f"[START] {now.strftime('%Y-%m-%d %H:%M:%S')} IST")

    log_sheet, hist_sheet, nifty_sheet, bm_sheet = get_sheets()

    # Load BotMemory once — one API call covers all memory needs this run
    bm = _bm_load(bm_sheet)
    print(f"[BM] Loaded {len(bm)} keys from BotMemory")

    # Purge stale FLAG entries (cheap — operates on already-loaded dict)
    _bm_purge(bm_sheet, bm)

    is_bullish = get_market_regime(nifty_sheet)

    if str(log_sheet.acell("T2").value or "").strip().upper() != "YES":
        print("[SKIP] Automation OFF (T2 != YES)"); return

    all_data   = log_sheet.get_all_values()
    trade_zone = [pad(list(r)) for r in all_data[1:16]]

    traded_rows = []
    for i, r in enumerate(trade_zone):
        status = str(r[C_STATUS]).upper()
        if "TRADED" in status and "EXITED" not in status:
            traded_rows.append((i + 2, r))

    print(f"[INFO] Active trades: {len(traded_rows)}/{MAX_TRADES}")

    # Pre-fetch Nifty200 data once (used for ATR + rank lookups at entry)
    nifty_data = []
    try:
        nifty_data = nifty_sheet.get_all_values()
    except Exception as e:
        print(f"[NIFTY FETCH] Error: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # 1. GOOD MORNING  08:45-09:29 IST
    # ─────────────────────────────────────────────────────────────────────────
    in_gm_window = (now.hour == 8 and now.minute >= 45) or (now.hour == 9 and now.minute <= 29)
    am_key       = f"{today}_AM"

    print(f"[GM CHECK] time={now.strftime('%H:%M')} IST | "
          f"window={'YES' if in_gm_window else 'NO'} | "
          f"AM_sent={_bm_exists(bm, am_key)}")

    if in_gm_window and not _bm_exists(bm, am_key):
        waiting_count = sum(
            1 for r in [pad(list(x)) for x in all_data[1:16]]
            if "WAITING" in str(r[C_STATUS]).upper()
        )
        sector_line = get_sector_context(all_data, bm)
        lines       = []

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
            cap      = get_capital(bm, key)
            mode     = get_trade_mode(bm, key)
            rank     = get_sector_rank(bm, key)
            mode_tag = {"\U0001f3af": "VCP", "\U0001f680": "MOM", "\U0001f4ca": "STD"}.get(mode, "\U0001f4ca")
            mode_tag = {"VCP": "\U0001f3af", "MOM": "\U0001f680", "STD": "\U0001f4ca"}.get(mode, "\U0001f4ca")
            sl_label = "TSL" if sl > to_f(r[C_INITIAL_SL]) else "SL"
            rank_txt = f" Rank#{rank}" if rank > 0 else ""

            if cp > 0:
                pnl    = (cp - ent) / ent * 100
                pl_rs  = round((cp - ent) / ent * cap)
                to_tgt = ((tgt - cp) / cp * 100) if cp > 0 else 0
                to_sl  = ((cp - sl)  / cp * 100) if cp > 0 else 0
                em     = "\U0001f7e2" if pnl >= 0 else "\U0001f534"
                lines.append(
                    f"{em} <b>{sym}</b> {mode_tag}{rank_txt} [{ttype}] Day {days + 1}\n"
                    f"   Entry Rs{ent:.2f} \u2192 Now Rs{cp:.2f}\n"
                    f"   P/L: <b>{pnl:+.2f}%</b> = <b>Rs{pl_rs:+,}</b>\n"
                    f"   {sl_label} Rs{sl:.2f} ({to_sl:.1f}% away) | "
                    f"Target Rs{tgt:.2f} ({to_tgt:.1f}% away)"
                )
            else:
                lines.append(
                    f"\u23f0 <b>{sym}</b> {mode_tag} [{ttype}] Day {days + 1}\n"
                    f"   Entry Rs{ent:.2f} | {sl_label} Rs{sl:.2f} | Target Rs{tgt:.2f}\n"
                    f"   (Live price loading...)"
                )

        deployed = sum(get_capital(bm, sym_key(r[C_SYMBOL])) for _, r in traded_rows if r[C_SYMBOL])

        send_basic(build_gm_basic(today, len(lines), waiting_count, is_bullish, sector_line))
        gm_full = build_gm_advance(today, lines, deployed, waiting_count, sector_line)
        send_advance(gm_full)
        send_premium(gm_full)

        _bm_set(bm_sheet, bm, am_key, "1", "", "FLAG")
        print(f"[GM] Sent. Open={len(lines)} Waiting={waiting_count}")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. MARKET HOURS — Core Trading Logic
    # ─────────────────────────────────────────────────────────────────────────
    if is_market_hours(now):
        exit_alerts_advance  = []
        exit_alerts_basic    = []
        trail_alerts         = []
        entry_alerts_advance = []
        entry_alerts_premium = []
        drawdown_alerts      = []
        tsl_cell_updates     = []

        # ── Step A: Mark WAITING -> TRADED ───────────────────────────────────
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

            # RR re-validation (v13.5 fix kept)
            rr_raw = str(r[C_RR]).strip()
            if rr_raw:
                try:    rr_val = to_f(rr_raw.split(':')[-1])
                except: rr_val = 0.0
                if rr_val > 0 and rr_val < MIN_RR:
                    print(f"[SKIP] {sym}: RR 1:{rr_val:.1f} below MIN_RR {MIN_RR}"); continue

            key       = sym_key(sym)
            sheet_row = i + 2

            # Stale price check
            last_cp = get_last_price(bm, key)
            set_last_price(bm_sheet, bm, key, cp)
            if last_cp > 0 and abs(cp - last_cp) < 0.01:
                print(f"[STALE] {sym}: price unchanged — skipping"); continue

            # Cooldown check
            exit_date = get_exit_date(bm, key)
            if exit_date and trading_days_since(exit_date, now) < 5:
                print(f"[COOLDOWN] {sym}: {trading_days_since(exit_date, now)}d since exit"); continue

            if round(CAPITAL_PER_TRADE / cp) < 2:
                print(f"[SKIP] {sym}: CMP Rs{cp:,.0f} too high"); continue

            capital    = get_capital(bm, key)
            trade_mode = get_trade_mode(bm, key)
            etime      = now.strftime('%Y-%m-%d %H:%M:%S')

            log_sheet.update_cell(sheet_row, C_STATUS + 1,      "\U0001f7e2 TRADED (PAPER)")
            log_sheet.update_cell(sheet_row, C_ENTRY_PRICE + 1, cp)
            log_sheet.update_cell(sheet_row, C_ENTRY_TIME + 1,  etime)
            log_sheet.update_cell(sheet_row, C_TRAIL_SL + 1,    init_sl)

            risk   = cp - init_sl
            reward = target - cp
            rr_num = (reward / risk) if risk > 0 else 0
            log_sheet.update_cell(sheet_row, C_RR + 1, f"1:{rr_num:.1f}")

            # Read ATR14 from Nifty200 (pre-fetched) col AC index 28
            atr_est = _read_atr_from_nifty200(nifty_data, sym)
            if atr_est <= 0:
                _mult   = 2 if "Intraday" in ttype else 4 if "Positional" in ttype else 3
                atr_est = (target - cp) / _mult if target > cp else 0
                print(f"[ATR] {sym}: fallback atr_est={atr_est:.2f}")
            else:
                print(f"[ATR] {sym}: ATR14={atr_est:.2f} from Nifty200")

            # Read Sector_Rank from Nifty200 col AI index 34
            sector_rank = _read_sector_rank_from_nifty200(nifty_data, sym)
            if sector_rank > 0:
                _bm_set(bm_sheet, bm, f"{key}_RANK", str(sector_rank), sym, "TRADE")
                print(f"[RANK] {sym}: Sector Rank #{sector_rank}")

            set_atr(bm_sheet, bm, key, atr_est)
            set_tsl(bm_sheet, bm, key, init_sl)
            set_max_price(bm_sheet, bm, key, cp)

            # Clear stale exit dedup flag if any
            stale_ex = f"{key}_EX"
            if _bm_exists(bm, stale_ex):
                _bm_del(bm_sheet, bm, stale_ex)

            updated_r                = list(r)
            updated_r[C_STATUS]      = "\U0001f7e2 TRADED (PAPER)"
            updated_r[C_ENTRY_PRICE] = cp
            updated_r[C_ENTRY_TIME]  = etime
            updated_r[C_TRAIL_SL]    = init_sl
            traded_rows.append((sheet_row, updated_r))

            atr    = atr_est
            o_hint = options_hint(sym, cp, atr, ttype)
            c_flag = ce_candidate_flag(cp, atr, stage, is_bullish, sector_rank)

            pos_size  = round(capital / cp) if cp > 0 else 0
            risk_rs   = round(max(0, cp - init_sl) * pos_size)
            reward_rs = round(max(0, target - cp)  * pos_size)

            entry_alerts_advance.append(
                build_entry_advance(sym, cp, init_sl, target, ttype, strat, stage,
                                    priority, pos_size, capital, risk_rs, reward_rs,
                                    rr_num, trade_mode, sector_rank, c_flag)
            )
            entry_alerts_premium.append(
                build_entry_premium(sym, cp, init_sl, target, ttype, strat, stage,
                                    priority, pos_size, capital, risk_rs, reward_rs,
                                    rr_num, o_hint, trade_mode, sector_rank, c_flag)
            )
            print(f"[ENTRY] {sym} @ Rs{cp} | Rs{capital:,} | {pos_size}sh | {ttype} | {trade_mode} | Rank#{sector_rank} | SL Rs{init_sl} | T Rs{target}")

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

            set_max_price(bm_sheet, bm, key, cp)
            pnl_pct    = (cp - ent) / ent * 100
            atr        = get_atr(bm, key)
            if atr <= 0:
                _mult = 4 if "Positional" in ttype else 2 if "Intraday" in ttype else 3
                atr   = (tgt - ent) / _mult if tgt > ent else ent * 0.02

            days_held   = calc_hold_days(etime, now)
            trade_mode  = get_trade_mode(bm, key)
            tsl_params  = TSL_PARAMS[trade_mode]
            capital     = get_capital(bm, key)
            sector_rank = get_sector_rank(bm, key)

            # ── Drawdown warning: > 3% from entry, once per trade per day ────
            dw_key = f"{key}_DW_{today}"
            if pnl_pct < -DRAWDOWN_WARN_PCT and not _bm_exists(bm, dw_key):
                _bm_set(bm_sheet, bm, dw_key, "1", sym, "FLAG")
                pl_rs_dw = round((cp - ent) / ent * capital)
                drawdown_alerts.append(
                    f"\u26a0\ufe0f <b>DRAWDOWN ALERT \u2014 {sym}</b>\n"
                    f"[{ttype}] [{trade_mode}] Day {days_held + 1}\n"
                    f"   Entry Rs{ent:.2f} \u2192 Now Rs{cp:.2f}\n"
                    f"   P/L: <b>{pnl_pct:+.2f}%</b> = Rs{pl_rs_dw:+,}\n"
                    f"   SL Rs{init_sl:.2f} | Hard loss at {-HARD_LOSS_PCT:.0f}%\n"
                    f"   {('Bullish market — stay calm, SL is your guide') if is_bullish else ('Bear market — monitor closely')}"
                )
                print(f"[DRAWDOWN] {sym}: {pnl_pct:+.2f}% \u2014 alert queued")

            new_tsl = calc_new_tsl(cp, ent, init_sl, atr, ttype, tsl_params)
            new_tsl = max(new_tsl, get_tsl(bm, key), cur_tsl)

            if new_tsl > cur_tsl:
                tsl_cell_updates.append((sheet_row, new_tsl))
                tsl_label = ("Breakeven"    if abs(new_tsl - ent) < 0.5
                             else "+2% locked" if abs(new_tsl - ent * 1.02) < 0.5
                             else "ATR trail")
                trail_alerts.append(
                    f"\U0001f512 <b>{sym}</b> [{trade_mode}] | LTP Rs{cp:.2f} ({pnl_pct:+.2f}%)\n"
                    f"   Trail SL: Rs{cur_tsl:.2f} \u2192 <b>Rs{new_tsl:.2f}</b> ({tsl_label})"
                )
                set_tsl(bm_sheet, bm, key, new_tsl)
                print(f"[TSL] {sym} [{trade_mode}]: Rs{cur_tsl:.2f}\u2192Rs{new_tsl:.2f}")

            entry_date_key = etime[:10].replace('-', '') if etime else "0"
            ex_flag    = f"{key}_EX_{entry_date_key}"
            tsl_hit    = (new_tsl > 0 and cp <= new_tsl)
            target_hit = (tgt > 0 and cp >= tgt)
            hard_loss  = pnl_pct < -HARD_LOSS_PCT

            # ── Hard loss exit ────────────────────────────────────────────────
            if hard_loss and not _bm_exists(bm, ex_flag):
                pl_rupees = round((cp - ent) / ent * capital, 2)
                hold_str  = calc_hold_str(etime, now)
                max_price = get_max_price(bm, key)

                exit_alerts_basic.append(build_exit_basic(sym, pnl_pct, "HARD LOSS"))
                exit_alerts_advance.append(
                    f"\U0001f6a8 <b>HARD LOSS EXIT</b>\n"
                    f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
                    f"\U0001f4cc <b>{sym}</b> [{ttype}] [{trade_mode}]\n"
                    f"   Entry Rs{ent:.2f} \u2192 Exit Rs{cp:.2f}\n"
                    f"   P/L: <b>{pnl_pct:+.2f}%</b> = <b>Rs{pl_rupees:+.0f}</b>\n"
                    f"   Loss exceeded {HARD_LOSS_PCT}% \u2014 thesis broken\n"
                    f"   Hold: {hold_str} | Day {days_held + 1}"
                )
                hist_sheet.append_row([
                    sym, etime[:10], ent,
                    now.strftime('%Y-%m-%d'), cp,
                    f"{pnl_pct:.2f}%", "LOSS \U0001f534", strat,
                    "\U0001f6a8 HARD LOSS EXIT", ttype, init_sl, new_tsl,
                    max_price if max_price > 0 else cp,
                    round(atr, 2), days_held, capital, pl_rupees, "\u2014",
                ])
                log_sheet.update_cell(sheet_row, C_STATUS + 1, "EXITED")
                _bm_set(bm_sheet, bm, ex_flag, "1", sym, "FLAG")
                set_exit_date(bm_sheet, bm, key, now.strftime('%Y-%m-%d'))
                print(f"[HARD LOSS] {sym} | {pnl_pct:+.2f}% | Rs{pl_rupees:+.0f}")
                continue

            # ── Normal exit ───────────────────────────────────────────────────
            is_pos         = "Positional" in ttype or "positional" in ttype.lower()
            min_hold       = MIN_HOLD_POS if is_pos else MIN_HOLD_SWING
            near_hard_loss = pnl_pct < -4.0
            skip_exit      = (
                days_held < min_hold
                and not target_hit
                and not hard_loss
                and not (near_hard_loss and not is_bullish)
            )

            if (tsl_hit or target_hit) and not _bm_exists(bm, ex_flag) and not skip_exit:
                exit_reason = ("🎯 TARGET HIT"  if target_hit else
                               "🔒 TRAILING SL" if new_tsl > init_sl else
                               "🚨 INITIAL SL HIT")
                result_sym  = "WIN ✅" if (target_hit or pnl_pct > 0) else "LOSS 🔴"
                hold_str    = calc_hold_str(etime, now)
                max_price   = get_max_price(bm, key)
                pl_rupees   = round((cp - ent) / ent * capital, 2)
                o_note      = (options_hint(sym, ent, atr, ttype)
                               .replace('\n\n📊 <b>OPTIONS ADVISORY</b>', '').strip()
                               if atr > 0 else "")

                exit_alerts_basic.append(build_exit_basic(sym, pnl_pct, exit_reason))
                exit_alerts_advance.append(
                    build_exit_advance(sym, ttype, ent, cp, pnl_pct,
                                       pl_rupees, hold_str, max_price, strat, exit_reason)
                )
                hist_sheet.append_row([
                    sym, etime[:10], ent,
                    now.strftime('%Y-%m-%d'), cp,
                    f"{pnl_pct:.2f}%", result_sym, strat,
                    exit_reason, ttype, init_sl, new_tsl,
                    max_price if max_price > 0 else cp,
                    round(atr, 2), days_held, capital, pl_rupees,
                    o_note[:100] if o_note else "\u2014",
                ])
                log_sheet.update_cell(sheet_row, C_STATUS + 1, "EXITED")
                _bm_set(bm_sheet, bm, ex_flag, "1", sym, "FLAG")
                set_exit_date(bm_sheet, bm, key, now.strftime('%Y-%m-%d'))
                print(f"[EXIT] {sym} | {result_sym} | {pnl_pct:+.2f}% | Rs{pl_rupees:+.0f}")

            elif tsl_hit and skip_exit:
                print(f"[HOLD] {sym}: SL touched Day {days_held + 1} < {min_hold} min hold")
                hold_warn_key = f"{key}_HOLD_WARN_{today}"
                if not _bm_exists(bm, hold_warn_key):
                    regime_note = "Bullish — recovery possible" if is_bullish else "Bearish — monitor closely"
                    send_advance(
                        f"\u26a0\ufe0f <b>MIN HOLD ACTIVE \u2014 {sym}</b>\n"
                        f"[{ttype}] [{trade_mode}] touched SL Rs{new_tsl:.2f} "
                        f"but only Day {days_held + 1} of {min_hold}.\n"
                        f"Holding until Day {min_hold} unless loss > {HARD_LOSS_PCT}%.\n"
                        f"Current P/L: {pnl_pct:+.2f}%\n{regime_note}"
                    )
                    send_premium(
                        f"\u26a0\ufe0f <b>MIN HOLD ACTIVE \u2014 {sym}</b>\n"
                        f"[{ttype}] [{trade_mode}] touched SL Rs{new_tsl:.2f} "
                        f"but only Day {days_held + 1} of {min_hold}.\n"
                        f"Holding until Day {min_hold} unless loss > {HARD_LOSS_PCT}%.\n"
                        f"Current P/L: {pnl_pct:+.2f}%\n{regime_note}"
                    )
                    _bm_set(bm_sheet, bm, hold_warn_key, "1", sym, "FLAG")

        # Batch TSL cell writes
        if tsl_cell_updates:
            cells = []
            for (sr, new_tsl) in tsl_cell_updates:
                c = log_sheet.cell(sr, C_TRAIL_SL + 1); c.value = new_tsl; cells.append(c)
            log_sheet.update_cells(cells)
            print(f"[TSL WRITE] {len(cells)} updates")

        # ── Send all alerts ───────────────────────────────────────────────────
        if drawdown_alerts:
            dw_hdr = (f"\u26a0\ufe0f <b>DRAWDOWN ALERT \u2014 {now.strftime('%H:%M IST')}</b>\n"
                      f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n")
            send_advance(dw_hdr + "\n\n".join(drawdown_alerts))
            send_premium(dw_hdr + "\n\n".join(drawdown_alerts))

        if exit_alerts_basic:
            for msg in exit_alerts_basic: send_basic(msg)

        if exit_alerts_advance:
            hdr       = f"\u26a1 <b>EXIT REPORT \u2014 {now.strftime('%H:%M IST')}</b>\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
            full_exit = hdr + "\n\n".join(exit_alerts_advance)
            send_advance(full_exit); send_premium(full_exit)

        if trail_alerts:
            tsl_msg = (f"\U0001f512 <b>TRAIL SL UPDATE \u2014 {now.strftime('%H:%M IST')}</b>\n"
                       f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
                       + "\n\n".join(trail_alerts))
            send_advance(tsl_msg); send_premium(tsl_msg)

        for msg in entry_alerts_advance: send_advance(msg)
        for msg in entry_alerts_premium: send_premium(msg)

    # ─────────────────────────────────────────────────────────────────────────
    # 3. MID-DAY PULSE  12:28-12:38 IST
    # ─────────────────────────────────────────────────────────────────────────
    noon_key = f"{today}_NOON"
    if now.hour == 12 and 28 <= now.minute <= 38 and not _bm_exists(bm, noon_key):
        fresh     = log_sheet.get_all_values()
        live_rows = [
            pad(list(r)) for r in fresh[1:16]
            if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
            and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        ]
        wins = losses = 0
        lines_advance = []; lines_basic = []; total_pnl_rs = 0

        for r in live_rows:
            sym = r[C_SYMBOL]; cp = to_f(r[C_LIVE_PRICE]); ent = to_f(r[C_ENTRY_PRICE])
            tsl = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL]); ttype = str(r[C_TRADE_TYPE])
            if not price_sanity(sym, cp, ent): continue
            pnl   = (cp - ent) / ent * 100
            key   = sym_key(sym)
            cap   = get_capital(bm, key)
            pl_rs = round((cp - ent) / ent * cap)
            total_pnl_rs += pl_rs
            em    = "\U0001f7e2" if pnl >= 0 else "\U0001f534"
            mode_tag = {"VCP": "\U0001f3af", "MOM": "\U0001f680", "STD": "\U0001f4ca"}.get(get_trade_mode(bm, key), "\U0001f4ca")
            if pnl >= 0: wins += 1
            else:        losses += 1
            lines_advance.append(f"{em} <b>{sym}</b> {mode_tag} [{ttype}]: {pnl:+.2f}% = Rs{pl_rs:+,} | TSL Rs{tsl:.2f}")
            lines_basic.append(f"{em} <b>{sym}</b>: {pnl:+.2f}%")

        send_basic(
            f"\u2600\ufe0f <b>MID-DAY PULSE \u2014 {today}</b>\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            f"Open: {len(lines_basic)} | \U0001f7e2 {wins} | \U0001f534 {losses}\n\n"
            + ("\n".join(lines_basic) if lines_basic else "No open trades")
            + "\n\n\U0001f514 <i>Full levels at ai360trading.in/membership</i>"
        )
        adv_noon = (
            f"\u2600\ufe0f <b>MID-DAY PULSE \u2014 {today}</b>\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            f"\U0001f4ca Open: {len(lines_advance)} | \U0001f7e2 {wins} | \U0001f534 {losses}\n"
            f"\U0001f4b0 Unrealised P/L: <b>Rs{total_pnl_rs:+,}</b>\n\n"
            + ("\n".join(lines_advance) if lines_advance else "\U0001f4ed No open trades")
        )
        send_advance(adv_noon); send_premium(adv_noon)
        _bm_set(bm_sheet, bm, noon_key, "1", "", "FLAG")
        print(f"[NOON] Sent. Open={len(live_rows)} PnL=Rs{total_pnl_rs:+,}")

    # ─────────────────────────────────────────────────────────────────────────
    # 4. MARKET CLOSE SUMMARY  15:15-15:45 IST
    # ─────────────────────────────────────────────────────────────────────────
    pm_key = f"{today}_PM"
    if now.hour == 15 and 15 <= now.minute <= 45 and not _bm_exists(bm, pm_key):
        hist_data   = hist_sheet.get_all_values()
        today_exits = [r for r in hist_data[1:] if len(r) >= 7 and r[3] == today]
        wins_today  = [r for r in today_exits if "WIN"  in str(r[6]).upper()]
        loss_today  = [r for r in today_exits if "LOSS" in str(r[6]).upper()]
        total_pl    = sum(to_f(r[16]) for r in today_exits if len(r) > 16)

        exit_lines_advance = []; exit_lines_basic = []
        for r in today_exits:
            em   = "\u2705" if "WIN" in str(r[6]).upper() else "\u274c"
            pl_r = f"Rs{to_f(r[16]):+.0f}" if len(r) > 16 else ""
            days_= r[14] if len(r) > 14 else "?"
            exit_lines_advance.append(f"  {em} <b>{r[0]}</b>: {r[5]} {pl_r} (held {days_}d)")
            exit_lines_basic.append(f"  {em} <b>{r[0]}</b>: {'WIN' if 'WIN' in str(r[6]).upper() else 'LOSS'}")

        fresh3    = log_sheet.get_all_values()
        open_rows = [
            pad(list(r)) for r in fresh3[1:16]
            if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
            and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        ]
        open_lines = []; total_open_pl = 0

        for r in open_rows:
            sym = r[C_SYMBOL]; cp = to_f(r[C_LIVE_PRICE]); ent = to_f(r[C_ENTRY_PRICE])
            tsl = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
            key = sym_key(sym); cap = get_capital(bm, key)
            if not ent or ent <= 0: continue
            if cp > 0 and ent > 0:
                pnl   = (cp - ent) / ent * 100
                pl_rs = round((cp - ent) / ent * cap)
                total_open_pl += pl_rs
                em    = "\U0001f7e2" if pnl >= 0 else "\U0001f534"
                open_lines.append(f"  {em} <b>{sym}</b>: {pnl:+.2f}% = Rs{pl_rs:+,} | TSL Rs{tsl:.2f}")
            else:
                open_lines.append(f"  \u23f0 <b>{sym}</b>: TSL Rs{tsl:.2f}")

        basic_close = (
            f"\U0001f514 <b>MARKET CLOSED \u2014 {today}</b>\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            f"\U0001f3c6 Wins: {len(wins_today)} | \U0001f480 Losses: {len(loss_today)} | \U0001f4c2 Open: {len(open_rows)}\n"
        )
        if exit_lines_basic: basic_close += "\n" + "\n".join(exit_lines_basic)
        basic_close += "\n\n\U0001f514 <i>Full P/L details for subscribers\n\u2192 ai360trading.in/membership</i>"
        send_basic(basic_close)

        full_close = (
            f"\U0001f514 <b>MARKET CLOSED \u2014 {today}</b>\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            f"\U0001f3c6 Wins: {len(wins_today)} | \U0001f480 Losses: {len(loss_today)} | \U0001f4c2 Open: {len(open_rows)}\n"
            f"\U0001f4b0 Today Realised P/L: <b>Rs{total_pl:+.0f}</b>\n"
        )
        if exit_lines_advance: full_close += "\n\U0001f4cb <b>Exited Today:</b>\n" + "\n".join(exit_lines_advance)
        if open_lines:
            full_close += (
                f"\n\n\U0001f4cc <b>Holding Overnight ({len(open_rows)} trade{'s' if len(open_rows) > 1 else ''}):</b>\n"
                + "\n".join(open_lines)
                + f"\n   Unrealised: <b>Rs{total_open_pl:+,}</b>"
            )
        full_close += "\n\n\u2705 <i>Overnight holds monitored via TSL</i>"
        send_advance(full_close); send_premium(full_close)

        _bm_set(bm_sheet, bm, pm_key, "1", "", "FLAG")
        print(f"[PM CLOSE] Sent. Exits={len(today_exits)} Open={len(open_rows)} Realised=Rs{total_pl:+.0f}")

    print(f"[DONE] {now.strftime('%H:%M:%S')} IST | BM keys: {len(bm)}")


# =============================================================================
# WEEKLY SUMMARY
# =============================================================================

def run_weekly_summary():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    print("[WEEKLY] Fetching weekly + monthly summary...")

    log_sheet, hist_sheet, _, bm_sheet = get_sheets()
    bm        = _bm_load(bm_sheet)
    hist_data = hist_sheet.get_all_values()
    all_rows  = hist_data[1:]

    days_since_mon = now.weekday()
    mon        = (now - timedelta(days=days_since_mon)).strftime('%Y-%m-%d')
    week_rows  = [r for r in all_rows if len(r) >= 17 and r[3] >= mon  and r[3] <= today]
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
        f"\U0001f4c5 <b>WEEKLY PERFORMANCE \u2014 {today}</b>\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"This Week: {wt} trades | Win Rate: {wwr}%\n"
        f"This Month: {mt} trades | Win Rate: {mwr}%\n"
        f"All Time: {at} trades | Win Rate: {awr}%\n\n"
        f"\U0001f514 <i>Full Rs P/L for subscribers\n\u2192 ai360trading.in/membership</i>"
    )
    full_weekly = (
        f"\U0001f4c5 <b>WEEKLY REPORT \u2014 w/e {today}</b>\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\n\U0001f4c6 <b>THIS WEEK</b>\n"
        f"   Trades: {wt} | \u2705 {ww}W / \u274c {wl}L | Win: {wwr}%\n"
        f"   P/L: <b>Rs{wpl:+,.0f}</b> | Avg/trade: Rs{wavg:+,.0f}\n"
    )
    if best:  full_weekly += f"   \U0001f3c6 Best:  <b>{best[0]}</b> = Rs{to_f(best[16]):+,.0f}\n"
    if worst and worst != best:
        full_weekly += f"   \U0001f480 Worst: <b>{worst[0]}</b> = Rs{to_f(worst[16]):+,.0f}\n"
    full_weekly += (
        f"\n\U0001f4c5 <b>THIS MONTH ({now.strftime('%B')})</b>\n"
        f"   Trades: {mt} | \u2705 {mw}W / \u274c {ml}L | Win: {mwr}%\n"
        f"   P/L: <b>Rs{mpl:+,.0f}</b> | Avg/trade: Rs{mavg:+,.0f}\n"
        f"\n\U0001f4ca <b>ALL TIME</b>\n"
        f"   Trades: {at} | \u2705 {aw}W / \u274c {al}L | Win: {awr}%\n"
        f"   Total P/L: <b>Rs{apl:+,.0f}</b> | Avg/trade: Rs{aavg:+,.0f}\n"
        f"\n\U0001f4cc Open now: {open_count}/{MAX_TRADES}"
    )
    send_advance(full_weekly); send_premium(full_weekly)
    print(f"[WEEKLY] Sent | W:{wt} M:{mt} All:{at}")


# =============================================================================
# DAILY SUMMARY
# =============================================================================

def run_daily_summary():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    print("[SUMMARY] Fetching portfolio summary...")

    log_sheet, hist_sheet, _, bm_sheet = get_sheets()
    bm       = _bm_load(bm_sheet)
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
        sym = r[C_SYMBOL]; cp = to_f(r[C_LIVE_PRICE]); ent = to_f(r[C_ENTRY_PRICE])
        tsl = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL]); tgt = to_f(r[C_TARGET])
        ttype = str(r[C_TRADE_TYPE]); etime = str(r[C_ENTRY_TIME])
        if not price_sanity(sym, cp, ent): continue
        pnl   = (cp - ent) / ent * 100
        key   = sym_key(sym); cap = get_capital(bm, key)
        pl_rs = round((cp - ent) / ent * cap); days = calc_hold_days(etime, now)
        em    = "\U0001f7e2" if pnl >= 0 else "\U0001f534"
        mode  = get_trade_mode(bm, key)
        rank  = get_sector_rank(bm, key)
        rank_txt = f" Rank#{rank}" if rank > 0 else ""
        trade_lines.append(
            f"{em} <b>{sym}</b> [{ttype}] [{mode}]{rank_txt}\n"
            f"   Entry Rs{ent:.2f} \u2192 Now Rs{cp:.2f} | <b>{pnl:+.2f}%</b> = Rs{pl_rs:+,}\n"
            f"   TSL Rs{tsl:.2f} | Target Rs{tgt:.2f} | Day {days}"
        )

    hist_data     = hist_sheet.get_all_values()
    today_exits   = [r for r in hist_data[1:] if len(r) >= 7 and r[3] == today]
    exit_lines    = []; total_exit_pl = 0.0
    for r in today_exits:
        em   = "\u2705" if "WIN" in str(r[6]).upper() else "\u274c"
        pl_r = to_f(r[16]) if len(r) > 16 else 0
        total_exit_pl += pl_r
        exit_lines.append(f"  {em} <b>{r[0]}</b>: {r[5]} = Rs{pl_r:+,.0f}")

    wait_lines = []
    for r in waiting_rows[:5]:
        key  = sym_key(str(r[C_SYMBOL]))
        mode = get_trade_mode(bm, key); cap = get_capital(bm, key)
        rank = get_sector_rank(bm, key)
        rank_txt = f" Rank#{rank}" if rank > 0 else ""
        wait_lines.append(
            f"  \u23f3 <b>{r[C_SYMBOL]}</b> [{r[C_TRADE_TYPE]}] [{mode}]{rank_txt} "
            f"Rs{cap:,} | P:{r[C_PRIORITY]}"
        )

    msg = (
        f"\U0001f4ca <b>PORTFOLIO SUMMARY</b>\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f550 {now.strftime('%Y-%m-%d %H:%M')} IST\n"
        f"\U0001f4c8 Open: {len(open_rows)}/{MAX_TRADES} | \u23f3 Waiting: {len(waiting_rows)}/{MAX_WAITING}\n"
        f"\U0001f4b0 Deployed: Rs{sum(get_capital(bm, sym_key(r[C_SYMBOL])) for r in open_rows):,}\n"
    )
    if trade_lines: msg += f"\n<b>\u2500\u2500 OPEN TRADES \u2500\u2500</b>\n" + "\n\n".join(trade_lines)
    else:           msg += "\n\U0001f4ed No open trades"
    if exit_lines:
        msg += f"\n\n<b>\u2500\u2500 TODAY'S EXITS \u2500\u2500</b>\n" + "\n".join(exit_lines)
        msg += f"\n   <b>Today P/L: Rs{total_exit_pl:+,.0f}</b>"
    if wait_lines:  msg += f"\n\n<b>\u2500\u2500 TOP WAITING \u2500\u2500</b>\n" + "\n".join(wait_lines)
    msg += "\n\n<i>On-demand summary</i>"

    send_advance(msg); send_premium(msg)
    print(f"[SUMMARY] Sent | Open={len(open_rows)} | Waiting={len(waiting_rows)}")


# =============================================================================
# TEST TELEGRAM
# =============================================================================

def run_test_telegram():
    now = datetime.now(IST)
    print("[TEST] Sending Telegram test messages to all 3 channels...")
    test_msg = (
        f"\u2705 <b>TELEGRAM TEST \u2014 OK</b>\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f916 Bot: AI360 Trading v15.0\n"
        f"\U0001f550 Time: {now.strftime('%Y-%m-%d %H:%M:%S')} IST\n"
        f"\U0001f511 Token: Connected \u2705\n\U0001f4ac Chat: Connected \u2705\n\n"
    )
    ok1 = _send_one(CHAT_BASIC,   test_msg + "\U0001f4e2 Channel: <b>ai360trading (Free)</b>")
    ok2 = _send_one(CHAT_ADVANCE, test_msg + "\U0001f48e Channel: <b>ai360trading_Advance</b>")
    ok3 = _send_one(CHAT_PREMIUM, test_msg + "\U0001f451 Channel: <b>ai360trading_Premium</b>")
    b = '✅' if ok1 else '❌'
    a = '✅' if ok2 else '❌'
    p = '✅' if ok3 else '❌'
    print(f"[TEST] BASIC={b} | ADVANCE={a} | PREMIUM={p}")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    mode = os.environ.get("BOT_MODE", "trade").strip().lower()
    print(f"[MODE] {mode}")
    if   mode == "test_telegram":   run_test_telegram()
    elif mode == "daily_summary":   run_daily_summary()
    elif mode == "weekly_summary":  run_weekly_summary()
    else:                           run_trading_cycle()
