"""
AI360 TRADING BOT — v15.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v15.0 CHANGES vs v14.0 — RSI + TIME + DAY + NIFTY DIRECTION FILTER

NEW FILTERS:
1. RSI FILTER — fetch live RSI(14) before entry
   BULLISH market: enter only if stock RSI < 65
   BEARISH market: enter only if stock RSI < 58

2. NIFTY DIRECTION AT ENTRY
   BULLISH market: Nifty % change > -0.3%
   BEARISH market: Nifty % change > 0.0% (must be green)

3. TIME WINDOW
   BULLISH market: entries 09:15 AM - 02:30 PM
   BEARISH market: entries 09:15 AM - 11:00 AM ONLY

4. DAY FILTER
   Monday before 10:00 AM: NO new entries
   Friday after 2:00 PM: NO new entries

5. DAILY ENTRY LIMIT
   BULLISH: max 3 per day | BEARISH: max 1 per day

6. RE-ENTRY COOLDOWN — 5 trading days after TARGET HIT
   Problem: IDEA hit target (+5.94%), then bot re-entered same day at 12:11 PM
   Fix: After TARGET HIT, set RECD key in T4 memory with exit date
        In step_a_enter_trades: check RECD before re-entering
        If RECD within last 5 trading days → skip re-entry
   Why 5 days: stock needs to reset after hitting target
                re-entering too soon = chasing, not momentum
   Note: Cooldown only after TARGET HIT — not after SL or TSL exit
         Losing trade can re-enter next day if setup is fresh

ALL v14.0 FIXES PRESERVED:
  - CHAT_ID swap fixed
  - Advance = full details, Premium = details + options
  - BotMemory sheet read
  - Result day skip (>6% gap)
  - Holiday check
  - MAX_TRADES = 8
  - Capital 3-tier from BotMemory
  - Mid-day pulse 12:28-12:38
  - Market close summary 15:15-15:45
  - CE flag gated by rank <= 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALERTLOG COLUMN MAP (0-based):
  A=0  Signal Time     B=1  Symbol         C=2  Live Price
  D=3  Priority Score  E=4  Trade Type     F=5  Strategy
  G=6  Breakout Stage  H=7  Initial SL     I=8  Target
  J=9  RR Ratio        K=10 Trade Status   L=11 Entry Price
  M=12 Entry Time      N=13 Days in Trade  O=14 Trailing SL
  P=15 P/L%            Q=16 ATH Warning    R=17 Risk Rs.
  S=18 Position Size   T=19 SYSTEM CONTROL
  U=20 Options Signal  V=21 Strike         W=22 Expiry
  X=23 Theta Risk
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, json, pytz, requests, gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

IST       = pytz.timezone('Asia/Kolkata')
TG_TOKEN  = os.environ.get('TELEGRAM_BOT_TOKEN')

CHAT_BASIC   = os.environ.get('CHAT_ID_BASIC')
CHAT_ADVANCE = os.environ.get('CHAT_ID_ADVANCE')
CHAT_PREMIUM = os.environ.get('CHAT_ID_PREMIUM')

SHEET_NAME = "Ai360tradingAlgo"

C_SIGNAL_TIME = 0;  C_SYMBOL = 1;     C_LIVE_PRICE = 2;  C_PRIORITY = 3
C_TRADE_TYPE  = 4;  C_STRATEGY = 5;   C_STAGE = 6;       C_INITIAL_SL = 7
C_TARGET      = 8;  C_RR = 9;         C_STATUS = 10;     C_ENTRY_PRICE = 11
C_ENTRY_TIME  = 12; C_DAYS = 13;      C_TRAIL_SL = 14;   C_PNL = 15
C_ATH_WARN    = 16; C_RISK = 17;      C_QTY = 18;        C_SYS_CTRL = 19
C_OPT_SIGNAL  = 20; C_OPT_STRIKE = 21; C_OPT_EXPIRY = 22; C_OPT_THETA = 23

MAX_TRADES             = 8
MAX_WAITING            = 10
MIN_RR                 = 1.8
HARD_LOSS_PCT          = 5.0
MIN_HOLD_SWING         = 2
MIN_HOLD_POS           = 3
TSL_GAP_LOCK_FRAC      = 0.5

RSI_MAX_BULLISH        = 65
RSI_MAX_BEARISH        = 58
NIFTY_MIN_PCT_BULLISH  = -0.30
NIFTY_MIN_PCT_BEARISH  = 0.00
ENTRY_WINDOW_BULLISH_END = (14, 30)
ENTRY_WINDOW_BEARISH_END = (11, 00)
MONDAY_ENTRY_START       = (10, 00)
FRIDAY_ENTRY_END         = (14, 00)
MAX_NEW_ENTRIES_BEARISH  = 1
MAX_NEW_ENTRIES_BULLISH  = 3

# v15.0: Re-entry cooldown after TARGET HIT
REENTRY_COOLDOWN_DAYS    = 5   # trading days — not calendar days

CAPITAL_HIGH = 13000
CAPITAL_MED  = 10000
CAPITAL_STD  = 7000

NSE_HOLIDAYS_2026 = {
    "2026-01-26","2026-03-25","2026-04-02","2026-04-14","2026-05-01",
    "2026-05-27","2026-06-17","2026-08-15","2026-08-27","2026-10-02",
    "2026-10-21","2026-10-22","2026-11-04","2026-11-05","2026-12-25",
}

TSL_PARAMS = {
    "VCP": {"breakeven":3.0,"lock1":5.0,"trail":8.0, "atr_mult":2.0,"gap_lock":9.0},
    "MOM": {"breakeven":2.5,"lock1":4.5,"trail":7.0, "atr_mult":1.8,"gap_lock":8.0},
    "STD": {"breakeven":2.0,"lock1":4.0,"trail":10.0,"atr_mult":2.5,"gap_lock":8.0},
}


# ══════════════════════════════════════════════════════════════════════════════
# TELEGRAM
# ══════════════════════════════════════════════════════════════════════════════

def _send_one(chat_id, msg):
    if not chat_id or not TG_TOKEN: return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
            timeout=15
        )
        if r.status_code != 200:
            print(f"[TG FAIL] {chat_id} {r.status_code}")
            return False
        return True
    except Exception as e:
        print(f"[TG ERROR] {e}"); return False

def send_basic(msg):               return _send_one(CHAT_BASIC, msg)
def send_advance(msg):             return _send_one(CHAT_ADVANCE, msg)
def send_premium(msg):             return _send_one(CHAT_PREMIUM, msg)
def send_advance_and_premium(msg): return _send_one(CHAT_ADVANCE, msg) or _send_one(CHAT_PREMIUM, msg)
def send_all(msg):                 return _send_one(CHAT_BASIC, msg) or _send_one(CHAT_ADVANCE, msg) or _send_one(CHAT_PREMIUM, msg)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def to_f(val):
    try: return float(str(val).replace(',','').replace('₹','').replace('%','').strip())
    except: return 0.0

def sym_key(sym): return str(sym).replace(':','_').replace(' ','_').strip()

def pad(r, n=24):
    r = list(r)
    while len(r) < n: r.append("")
    return r

def calc_hold_days(entry_str, exit_dt):
    try:
        ent = IST.localize(datetime.strptime(str(entry_str)[:19],'%Y-%m-%d %H:%M:%S'))
        return max(0,(exit_dt-ent).days)
    except: return 0

def calc_hold_str(entry_str, exit_dt):
    try:
        ent   = IST.localize(datetime.strptime(str(entry_str)[:19],'%Y-%m-%d %H:%M:%S'))
        delta = exit_dt - ent
        d = delta.days; h = delta.seconds//3600; m = (delta.seconds%3600)//60
        return f"{d}d {h}h" if d > 0 else f"{h}h {m}m"
    except: return "—"

def is_market_hours(now):
    if now.weekday() >= 5: return False
    mins = now.hour*60+now.minute
    return (9*60+15) <= mins <= (15*60+30)

def is_holiday(date_str):
    return date_str in NSE_HOLIDAYS_2026

def price_sanity(sym,cp,ent):
    if cp<=0 or ent<=0: print(f"[WARN] {sym}: zero price"); return False
    if cp > ent*4: print(f"[WARN] {sym}: LTP too high"); return False
    if cp < ent*0.1: print(f"[WARN] {sym}: LTP too low"); return False
    return True

def trading_days_since(date_str, now):
    if not date_str: return 999
    try:
        start=datetime.strptime(date_str,'%Y-%m-%d').date(); end=now.date(); count=0; cur=start
        while cur<=end:
            if cur.weekday()<5: count+=1
            cur+=timedelta(days=1)
        return max(0,count-1)
    except: return 999

def clean_mem(mem):
    cutoff=(datetime.now(IST)-timedelta(days=14)).strftime("%Y-%m-%d")
    kept=[p for p in mem.split(",") if p.strip() and not (len(p)>=10 and p[4]=="-" and p[7]=="-" and p[:10]<cutoff)]
    result=",".join(kept)
    if len(result)>20000:
        parts=[p for p in result.split(",") if p.strip()]
        result=",".join(parts[-100:])
    print(f"[MEM] T4: {len(result):,} chars")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# RE-ENTRY COOLDOWN HELPERS — v15.0 NEW
# ══════════════════════════════════════════════════════════════════════════════

def get_reentry_cooldown_date(mem: str, key: str) -> str:
    """
    Get the date when TARGET HIT cooldown expires for a stock.
    RECD = Re-Entry Cooldown Date.
    Format stored: NSE_SYMBOL_RECD_2026-05-15 (date of target hit)
    Returns: date string "YYYY-MM-DD" or "" if no cooldown
    """
    prefix = f"{key}_RECD_"
    for p in mem.split(','):
        if p.startswith(prefix):
            return p[len(prefix):]
    return ""

def set_reentry_cooldown(mem: str, key: str, hit_date: str) -> str:
    """
    Set re-entry cooldown after TARGET HIT.
    Stores the date of the target hit.
    check_reentry_allowed() calculates if 5 trading days have passed.
    """
    prefix = f"{key}_RECD_"
    parts  = [p for p in mem.split(',') if p.strip() and not p.startswith(prefix)]
    parts.append(f"{prefix}{hit_date}")
    print(f"[RECD] {key}: cooldown set — no re-entry for {REENTRY_COOLDOWN_DAYS} trading days from {hit_date}")
    return ','.join(parts)

def check_reentry_allowed(mem: str, key: str, sym: str, now: datetime) -> tuple:
    """
    Check if re-entry is allowed for a stock.
    Returns (allowed: bool, reason: str)

    Logic:
      - No cooldown stored → entry allowed (first time entry)
      - Cooldown stored → check if REENTRY_COOLDOWN_DAYS trading days have passed
      - If not enough days → skip with clear reason
      - If enough days passed → clear the cooldown, allow entry

    Why this matters:
      IDEA hit target at ₹13.19 (+5.94%) on May 15
      Bot re-entered IDEA at ₹13.06 same day (12:11 PM)
      New entry started negative immediately
      Stock needs 5 trading days to reset momentum after target hit
    """
    recd_date = get_reentry_cooldown_date(mem, key)

    if not recd_date:
        return True, "No cooldown — entry allowed"

    days_since = trading_days_since(recd_date, now)

    if days_since < REENTRY_COOLDOWN_DAYS:
        remaining = REENTRY_COOLDOWN_DAYS - days_since
        reason = (
            f"TARGET HIT cooldown active — {days_since}/{REENTRY_COOLDOWN_DAYS} trading days since {recd_date}. "
            f"{remaining} more trading days before re-entry allowed. "
            f"Stock needs to reset after hitting target."
        )
        return False, reason

    return True, f"Cooldown expired ({days_since} trading days since {recd_date}) — entry allowed"


# ══════════════════════════════════════════════════════════════════════════════
# RSI CALCULATION
# ══════════════════════════════════════════════════════════════════════════════

def get_rsi(symbol: str, period: int = 14) -> float:
    """Fetch RSI(14) via yfinance. Returns -1 if fails (entry allowed on failure)."""
    try:
        import yfinance as yf
        yf_sym = symbol.replace("NSE:", "").strip() + ".NS"
        ticker = yf.Ticker(yf_sym)
        df     = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < period + 2:
            print(f"[RSI] {symbol}: insufficient data")
            return -1
        delta  = df["Close"].diff()
        gain   = delta.where(delta > 0, 0.0)
        loss   = -delta.where(delta < 0, 0.0)
        avg_g  = gain.ewm(com=period-1, adjust=False).mean()
        avg_l  = loss.ewm(com=period-1, adjust=False).mean()
        rs     = avg_g / avg_l.replace(0, 1e-10)
        rsi    = 100 - (100 / (1 + rs))
        latest = round(float(rsi.iloc[-1]), 1)
        print(f"[RSI] {symbol}: RSI(14) = {latest}")
        return latest
    except ImportError:
        print("[RSI] yfinance not installed"); return -1
    except Exception as e:
        print(f"[RSI] {symbol}: {e}"); return -1


def check_rsi_entry(symbol: str, is_bullish: bool) -> tuple:
    rsi       = get_rsi(symbol)
    if rsi < 0: return True, rsi, "RSI unavailable — entry allowed"
    threshold = RSI_MAX_BULLISH if is_bullish else RSI_MAX_BEARISH
    if rsi > threshold:
        return False, rsi, f"RSI {rsi} > {threshold} — overbought, skip"
    zone = "oversold" if rsi < 35 else ("healthy" if rsi < 55 else "extended")
    return True, rsi, f"RSI {rsi} — {zone} ✅"


# ══════════════════════════════════════════════════════════════════════════════
# NIFTY DIRECTION CHECK
# ══════════════════════════════════════════════════════════════════════════════

def get_nifty_pct_change(nifty_sheet) -> float:
    try:
        row = nifty_sheet.row_values(2)
        if row and len(row) > 3:
            pct = to_f(row[3])
            if pct != 0:
                print(f"[NIFTY] {pct:+.2f}% from sheet")
                return pct
    except Exception as e:
        print(f"[NIFTY] Sheet read: {e}")
    try:
        import yfinance as yf
        n    = yf.Ticker("^NSEI")
        info = n.fast_info
        prev = info.get('previous_close', 0); curr = info.get('last_price', 0)
        if prev > 0 and curr > 0:
            pct = round(((curr-prev)/prev)*100, 2)
            print(f"[NIFTY] {pct:+.2f}% from yfinance")
            return pct
    except Exception as e:
        print(f"[NIFTY] yfinance: {e}")
    return 0.0


def check_nifty_direction(nifty_pct: float, is_bullish: bool) -> tuple:
    threshold = NIFTY_MIN_PCT_BULLISH if is_bullish else NIFTY_MIN_PCT_BEARISH
    if nifty_pct < threshold:
        return False, f"Nifty {nifty_pct:+.2f}% < {threshold:+.2f}% — {'wait for recovery' if is_bullish else 'must be green in bearish'}"
    return True, f"Nifty {nifty_pct:+.2f}% — {'green' if nifty_pct > 0 else 'flat'} ✅"


# ══════════════════════════════════════════════════════════════════════════════
# TIME AND DAY FILTER
# ══════════════════════════════════════════════════════════════════════════════

def check_entry_time_allowed(now: datetime, is_bullish: bool) -> tuple:
    day = now.weekday(); hour = now.hour; mins = now.minute
    if day == 0 and (hour, mins) < MONDAY_ENTRY_START:
        return False, f"Monday before 10 AM — gap risk"
    if day == 4 and (hour, mins) >= FRIDAY_ENTRY_END:
        return False, f"Friday after 2 PM — weekend risk"
    if is_bullish:
        end_h, end_m = ENTRY_WINDOW_BULLISH_END
        if (hour, mins) > (end_h, end_m):
            return False, f"After {end_h}:{end_m:02d} PM — late entry bullish"
    else:
        end_h, end_m = ENTRY_WINDOW_BEARISH_END
        if (hour, mins) > (end_h, end_m):
            return False, f"After {end_h}:{end_m:02d} AM — NO afternoon entries in bearish market"
    day_names = {0:"Mon",1:"Tue",2:"Wed",3:"Thu",4:"Fri"}
    return True, f"{day_names[day]} {hour}:{mins:02d} — window OK ✅"


def check_daily_entry_limit(today_entries: int, is_bullish: bool) -> tuple:
    limit = MAX_NEW_ENTRIES_BULLISH if is_bullish else MAX_NEW_ENTRIES_BEARISH
    if today_entries >= limit:
        return False, f"Daily limit {today_entries}/{limit}"
    return True, f"Entry {today_entries+1}/{limit} ✅"


# ══════════════════════════════════════════════════════════════════════════════
# ALL ENTRY FILTERS COMBINED
# ══════════════════════════════════════════════════════════════════════════════

def check_all_entry_filters(sym, mem, key, is_bullish, now, nifty_pct, today_entries):
    """
    Run all entry filters in order of cost (fast checks first, API calls last).
    Returns (allowed: bool, reasons: list, rsi_val: float)

    Order:
      1. Re-entry cooldown (memory lookup — instant)
      2. Time window (date math — instant)
      3. Daily entry limit (count — instant)
      4. Nifty direction (already fetched — instant)
      5. RSI (yfinance API call — only if 1-4 pass)
    """
    reasons = []

    # Filter 1: Re-entry cooldown (NEW v15.0)
    allowed, msg = check_reentry_allowed(mem, key, sym, now)
    reasons.append(f"[RECD] {msg}")
    if not allowed:
        return False, reasons, -1

    # Filter 2: Time and day
    allowed, msg = check_entry_time_allowed(now, is_bullish)
    reasons.append(f"[TIME] {msg}")
    if not allowed:
        return False, reasons, -1

    # Filter 3: Daily entry limit
    allowed, msg = check_daily_entry_limit(today_entries, is_bullish)
    reasons.append(f"[DAILY] {msg}")
    if not allowed:
        return False, reasons, -1

    # Filter 4: Nifty direction
    allowed, msg = check_nifty_direction(nifty_pct, is_bullish)
    reasons.append(f"[NIFTY] {msg}")
    if not allowed:
        return False, reasons, -1

    # Filter 5: RSI (API call — only if 1-4 passed)
    allowed, rsi_val, msg = check_rsi_entry(sym, is_bullish)
    reasons.append(f"[RSI] {msg}")
    if not allowed:
        return False, reasons, rsi_val

    return True, reasons, rsi_val


# ══════════════════════════════════════════════════════════════════════════════
# MEMORY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _mem_get(mem,key):
    for p in mem.split(','):
        if p.startswith(key+'='): return p[len(key)+1:]
    return ""

def _mem_set(mem,key,val):
    parts=[p for p in mem.split(',') if p.strip() and not p.startswith(key+'=')]
    parts.append(f"{key}={val}"); return ','.join(parts)

def get_tsl(mem,key):
    p=f"{key}_TSL_"
    for x in mem.split(','):
        if x.startswith(p):
            try: return int(x[len(p):])/100.0
            except: return 0.0
    return 0.0

def set_tsl(mem,key,price):
    p=f"{key}_TSL_"
    parts=[x for x in mem.split(',') if x.strip() and not x.startswith(p)]
    parts.append(f"{p}{int(round(price*100))}"); return ','.join(parts)

def get_max_price(mem,key):
    p=f"{key}_MAX_"
    for x in mem.split(','):
        if x.startswith(p):
            try: return int(x[len(p):])/100.0
            except: return 0.0
    return 0.0

def set_max_price(mem,key,price):
    p=f"{key}_MAX_"; cur=get_max_price(mem,key)
    if price<=cur: return mem
    parts=[x for x in mem.split(',') if x.strip() and not x.startswith(p)]
    parts.append(f"{p}{int(round(price*100))}"); return ','.join(parts)

def get_atr_from_mem(mem,key):
    p=f"{key}_ATR_"
    for x in mem.split(','):
        if x.startswith(p):
            try: return int(x[len(p):])/100.0
            except: return 0.0
    return 0.0

def save_atr_to_mem(mem,key,atr):
    p=f"{key}_ATR_"
    parts=[x for x in mem.split(',') if x.strip() and not x.startswith(p)]
    parts.append(f"{p}{int(round(atr*100))}"); return ','.join(parts)

def get_last_price(mem,key):
    p=f"{key}_LP_"
    for x in mem.split(','):
        if x.startswith(p):
            try: return int(x[len(p):])/100.0
            except: return 0.0
    return 0.0

def set_last_price(mem,key,price):
    p=f"{key}_LP_"
    parts=[x for x in mem.split(',') if x.strip() and not x.startswith(p)]
    parts.append(f"{p}{int(round(price*100))}"); return ','.join(parts)

def get_exit_date(mem,key):
    p=f"{key}_EXDT_"
    for x in mem.split(','):
        if x.startswith(p): return x[len(p):]
    return ""

def set_exit_date(mem,key,date_str):
    p=f"{key}_EXDT_"
    parts=[x for x in mem.split(',') if x.strip() and not x.startswith(p)]
    parts.append(f"{p}{date_str}"); return ','.join(parts)

def get_trade_mode(mem,key):
    val=_mem_get(mem,f"{key}_MODE"); return val if val in ("VCP","MOM","STD") else "STD"

def get_tsl_params(mem,key): return TSL_PARAMS[get_trade_mode(mem,key)]

def get_capital_from_mem(mem,key):
    cap=_mem_get(mem,f"{key}_CAP")
    if cap:
        try:
            c=int(cap)
            if c in (7000,10000,13000): return c
        except: pass
    return CAPITAL_MED


# ══════════════════════════════════════════════════════════════════════════════
# TSL CALCULATION
# ══════════════════════════════════════════════════════════════════════════════

def calc_new_tsl(cp, ent, init_sl, atr, ttype, mem, key, now):
    params   = get_tsl_params(mem, key)
    cur_tsl  = get_tsl(mem, key) or init_sl
    cur_max  = get_max_price(mem, key) or ent
    gain_pct = ((cp - ent) / ent) * 100 if ent > 0 else 0
    new_tsl  = cur_tsl

    if "Positional" in str(ttype): hold = MIN_HOLD_POS
    else:                           hold = MIN_HOLD_SWING

    hold_days = calc_hold_days(get_exit_date(mem, key) or "", now)
    if hold_days < hold:
        return cur_tsl, f"min hold ({hold}d)"

    if gain_pct >= params["trail"]:
        trail_sl = cp - atr * params["atr_mult"]
        new_tsl  = max(cur_tsl, trail_sl)
        reason   = f"trailing @ {gain_pct:.1f}%"
    elif gain_pct >= params["lock1"]:
        new_tsl  = max(cur_tsl, ent + atr * 0.5)
        reason   = f"lock1 @ {gain_pct:.1f}%"
    elif gain_pct >= params["breakeven"]:
        new_tsl  = max(cur_tsl, ent * 1.002)
        reason   = f"breakeven @ {gain_pct:.1f}%"
    else:
        new_tsl  = cur_tsl
        reason   = f"below breakeven ({gain_pct:.1f}%)"

    if cp > cur_max:
        gap_pct = ((cp - cur_max) / cur_max) * 100 if cur_max > 0 else 0
        if gap_pct >= params["gap_lock"]:
            gap_sl  = cur_max + (cp - cur_max) * TSL_GAP_LOCK_FRAC
            new_tsl = max(new_tsl, gap_sl)
            reason  = f"gap lock {gap_pct:.1f}%"

    new_tsl = max(new_tsl, init_sl)
    new_tsl = min(new_tsl, cp * 0.99)
    return new_tsl, reason


# ══════════════════════════════════════════════════════════════════════════════
# SHEET ACCESS
# ══════════════════════════════════════════════════════════════════════════════

def get_sheets():
    scope  = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    creds  = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ.get("GCP_SERVICE_ACCOUNT_JSON","{}") or
                   open("service_account.json").read()), scope)
    gc     = gspread.authorize(creds)
    ss     = gc.open(SHEET_NAME)
    return ss.worksheet("AlertLog"), ss.worksheet("History"), ss.worksheet("Nifty200"), ss.worksheet("BotMemory")

def get_bm_data(bm_sheet):
    bm = {}
    try:
        for row in bm_sheet.get_all_values()[1:]:
            if len(row) >= 2 and row[0].strip():
                bm[row[0].strip()] = row[1].strip()
    except Exception as e:
        print(f"[BM] {e}")
    return bm

def get_capital_bm(bm_data, sym):
    k = sym_key(sym) + "_CAP"
    if k in bm_data:
        try:
            c = int(bm_data[k])
            if c in (7000,10000,13000): return c
        except: pass
    return CAPITAL_MED

def get_rank_bm(bm_data, sym):
    k = sym_key(sym) + "_RANK"
    if k in bm_data:
        try: return int(bm_data[k])
        except: pass
    return 99

def _read_atr_from_nifty200(nifty_sheet, sym):
    try:
        clean = sym.replace("NSE:","").strip()
        for row in nifty_sheet.get_all_values()[1:]:
            if len(row) > 28 and str(row[0]).replace("NSE:","").strip() == clean:
                atr = to_f(row[28])
                if atr > 0:
                    print(f"[ATR] {sym}: {atr}")
                    return atr
    except Exception as e:
        print(f"[ATR] {e}")
    return 0.0

def get_market_regime(nifty_sheet):
    try:
        row  = nifty_sheet.row_values(2)
        if row and len(row) > 4:
            cmp  = to_f(row[2]); pct = to_f(row[3]); dma = to_f(row[4])
            bull = cmp >= dma if cmp > 0 and dma > 0 else True
            print(f"[REGIME] Nifty {cmp:.0f} vs 20DMA {dma:.0f} | {pct:+.2f}% | {'BULLISH' if bull else 'BEARISH'}")
            return bull, cmp, dma, pct
    except Exception as e:
        print(f"[REGIME] {e}")
    return True, 0, 0, 0


# ══════════════════════════════════════════════════════════════════════════════
# CE FLAG
# ══════════════════════════════════════════════════════════════════════════════

def ce_candidate_flag(cp, atr, stage, is_bullish, rank=99,
                      opt_signal="", opt_strike="", opt_expiry="", opt_theta=""):
    if not is_bullish: return ""
    if rank > 5:       return ""
    if cp <= 0 or atr <= 0: return ""
    if opt_signal in ("📊 BUY CE", "📦 BASE CE") and opt_strike:
        label = "BASE OPTIONS" if "BASE" in opt_signal else "OPTIONS"
        return (
            f"\n\n📊 <b>{label} SIGNAL</b>\n"
            f"   🎰 Buy: <b>{opt_strike}</b>\n"
            f"   📅 Expiry: {opt_expiry}\n"
            f"   ⏳ Theta: {opt_theta}\n"
            f"   ⚡ Entry: 9:30-9:45 AM after stock triggers\n"
            f"   🛑 Exit: if option -40% OR stock hits SL\n"
            f"   ⚠️ Check live premium on Zerodha"
        )
    atr_pct = (atr/cp)*100
    if atr_pct < 1.5: return ""
    gap = 5 if cp<200 else (10 if cp<500 else (20 if cp<1000 else 50))
    atm = round(cp/gap)*gap; otm = atm+gap
    strike = f"{int(otm)} CE" if "BREAKOUT CONFIRMED" in stage else f"{int(atm)} CE"
    tgt_p = 50 if atr_pct>=2.5 else 65; sl_p = 35 if atr_pct>=2.5 else 40
    return (
        f"\n\n📊 <b>CE CANDIDATE</b> (ATR {atr_pct:.1f}%)\n"
        f"   Strike: {strike} | Target: +{tgt_p}% | SL: -{sl_p}%\n"
        f"   ⚠️ VIX check before buying"
    )


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY MESSAGE BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def build_entry_advance(sym, cp, stage, sl, tgt, rr, ttype, atr, rank, capital, is_bullish,
                        rsi_val=-1, nifty_pct=0, opt_signal="", opt_strike="", opt_expiry="", opt_theta=""):
    rsi_str   = f"RSI: {rsi_val}" if rsi_val > 0 else ""
    nifty_str = f"Nifty: {nifty_pct:+.2f}%" if nifty_pct != 0 else ""
    filters   = " | ".join([x for x in [rsi_str, nifty_str] if x])
    qty       = int(capital // cp) if cp > 0 else 0
    return (
        f"🚀 <b>TRADE ENTERED</b>\n\n"
        f"Stock: {sym}\nType: {ttype}\nEntry: ₹{cp:.2f}\nSetup: {stage}\n"
        f"Qty: {qty} shares @ ₹{capital:,}\n"
        f"SL: ₹{sl:.2f} (Risk: ₹{int((cp-sl)*qty)})\n"
        f"Target: ₹{tgt:.2f} (Reward: ₹{int((tgt-cp)*qty)})\n"
        f"RR: {rr} | Priority: {rank}\n{filters}"
    )

def build_entry_premium(sym, cp, stage, sl, tgt, rr, ttype, atr, rank, capital, is_bullish,
                        rsi_val=-1, nifty_pct=0, opt_signal="", opt_strike="", opt_expiry="", opt_theta=""):
    base = build_entry_advance(sym, cp, stage, sl, tgt, rr, ttype, atr, rank, capital, is_bullish,
                                rsi_val, nifty_pct, opt_signal, opt_strike, opt_expiry, opt_theta)
    return base + ce_candidate_flag(cp, atr, stage, is_bullish, rank, opt_signal, opt_strike, opt_expiry, opt_theta)

def build_entry_basic(sym, cp, stage, pct_chg):
    emoji = "📈" if pct_chg >= 0 else "📉"
    return f"{emoji} <b>Signal Active</b>: {sym.replace('NSE:','')}\nStage: {stage}\nFull details: Join Advance/Premium\n📱 ai360trading.in/membership"


# ══════════════════════════════════════════════════════════════════════════════
# STEP A: WAITING → TRADED
# ══════════════════════════════════════════════════════════════════════════════

def step_a_enter_trades(log_sheet, nifty_sheet, bm_sheet, mem, now, is_bullish, nifty_pct, today_entries):
    """
    Check WAITING rows → promote to TRADED if all filters pass.
    v15.0: RSI + time + day + Nifty + re-entry cooldown checks.
    """
    bm_data   = get_bm_data(bm_sheet)
    try:
        rows = log_sheet.get_all_values()
    except Exception as e:
        print(f"[STEP A] Read error: {e}"); return mem, today_entries

    traded_count = sum(
        1 for r in rows[1:22] if len(r)>10 and "TRADED" in str(r[10]).upper() and "EXITED" not in str(r[10]).upper()
    )
    if traded_count >= MAX_TRADES:
        print(f"[STEP A] Max trades {traded_count}/{MAX_TRADES}"); return mem, today_entries

    for i, row in enumerate(rows[1:22], start=2):
        row    = pad(row)
        status = str(row[C_STATUS]).upper()
        if "WAITING" not in status: continue

        sym  = str(row[C_SYMBOL]).strip()
        if not sym: continue

        cp       = to_f(row[C_LIVE_PRICE])
        sl       = to_f(row[C_INITIAL_SL])
        tgt      = to_f(row[C_TARGET])
        rr_str   = str(row[C_RR])
        stage    = str(row[C_STAGE]).strip()
        ttype    = str(row[C_TRADE_TYPE]).strip()
        strat    = str(row[C_STRATEGY]).strip()
        opt_signal = str(row[C_OPT_SIGNAL]).strip()
        opt_strike = str(row[C_OPT_STRIKE]).strip()
        opt_expiry = str(row[C_OPT_EXPIRY]).strip()
        opt_theta  = str(row[C_OPT_THETA]).strip()

        # RR check
        try:
            rr_val = float(rr_str.split(':')[-1]) if ':' in rr_str else to_f(rr_str)
            if rr_val > 0 and rr_val < MIN_RR:
                print(f"[STEP A] {sym}: RR {rr_val} < {MIN_RR} — skip"); continue
        except: pass

        if cp <= 0: continue

        key = sym_key(sym)

        # ── v15.0: Run ALL filters including re-entry cooldown ────────────────
        allowed, filter_reasons, rsi_val = check_all_entry_filters(
            sym, mem, key, is_bullish, now, nifty_pct, today_entries
        )
        for reason in filter_reasons:
            print(f"[FILTER] {sym}: {reason}")
        if not allowed:
            continue

        # Result/event day gap check
        prev_close = get_last_price(mem, key)
        if prev_close > 0:
            gap_pct = abs((cp - prev_close) / prev_close) * 100
            if gap_pct > 6.0:
                print(f"[STEP A] {sym}: gap {gap_pct:.1f}% > 6% — skip")
                continue

        capital = get_capital_bm(bm_data, sym)
        rank    = get_rank_bm(bm_data, sym)
        atr     = _read_atr_from_nifty200(nifty_sheet, sym)
        if atr <= 0 and sl > 0 and cp > 0: atr = (cp - sl) / 2.0

        # Promote to TRADED
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        try:
            log_sheet.update(f"K{i}", [["✅ TRADED (PAPER)"]])
            log_sheet.update(f"L{i}", [[cp]])
            log_sheet.update(f"M{i}", [[now_str]])
        except Exception as e:
            print(f"[STEP A] {sym}: update failed: {e}"); continue

        mem = save_atr_to_mem(mem, key, atr)
        mem = set_tsl(mem, key, sl)
        mem = set_last_price(mem, key, cp)
        mem = set_max_price(mem, key, cp)
        today_entries += 1

        print(f"[ENTRY] {sym} @ ₹{cp:.2f} | RSI:{rsi_val} | Nifty:{nifty_pct:+.2f}% | #{today_entries}")

        msg_advance = build_entry_advance(sym, cp, stage, sl, tgt, rr_str, ttype, atr,
                                          rank, capital, is_bullish, rsi_val, nifty_pct,
                                          opt_signal, opt_strike, opt_expiry, opt_theta)
        msg_premium = build_entry_premium(sym, cp, stage, sl, tgt, rr_str, ttype, atr,
                                          rank, capital, is_bullish, rsi_val, nifty_pct,
                                          opt_signal, opt_strike, opt_expiry, opt_theta)
        msg_basic   = build_entry_basic(sym, cp, stage, to_f(row[C_PNL]))
        send_basic(msg_basic); send_advance(msg_advance); send_premium(msg_premium)

        traded_count += 1
        if traded_count >= MAX_TRADES: break

    return mem, today_entries


# ══════════════════════════════════════════════════════════════════════════════
# STEP B: MONITOR TRADED
# ══════════════════════════════════════════════════════════════════════════════

def step_b_monitor_trades(log_sheet, hist_sheet, nifty_sheet, mem, now, is_bullish):
    """Monitor TRADED rows — TSL updates, target hit, stop loss."""
    today_str = now.strftime("%Y-%m-%d")
    try:
        rows = log_sheet.get_all_values()
    except Exception as e:
        print(f"[STEP B] {e}"); return mem

    for i, row in enumerate(rows[1:22], start=2):
        row    = pad(row)
        status = str(row[C_STATUS]).upper()
        if "TRADED" not in status or "EXITED" in status: continue

        sym     = str(row[C_SYMBOL]).strip()
        if not sym: continue
        cp      = to_f(row[C_LIVE_PRICE])
        ent     = to_f(row[C_ENTRY_PRICE])
        sl      = to_f(row[C_INITIAL_SL])
        tgt     = to_f(row[C_TARGET])
        ttype   = str(row[C_TRADE_TYPE]).strip()
        stage   = str(row[C_STAGE]).strip()
        strat   = str(row[C_STRATEGY]).strip()
        ent_time= str(row[C_ENTRY_TIME]).strip()
        qty     = to_f(row[C_QTY])

        if not price_sanity(sym, cp, ent): continue
        key    = sym_key(sym)
        atr    = get_atr_from_mem(mem, key)
        if atr <= 0: atr = _read_atr_from_nifty200(nifty_sheet, sym)
        if atr <= 0 and sl > 0 and ent > 0: atr = (ent - sl) / 2.0

        cur_tsl  = get_tsl(mem, key) or sl
        mem      = set_last_price(mem, key, cp)
        mem      = set_max_price(mem, key, cp)
        pnl_pct  = ((cp - ent) / ent) * 100 if ent > 0 else 0
        pnl_rs   = round((cp - ent) * qty, 2) if qty > 0 else 0

        # Hard loss
        if pnl_pct < -HARD_LOSS_PCT and cur_tsl < ent:
            mem = _exit_trade(log_sheet, hist_sheet, i, sym, ent, cp, tgt, sl, cur_tsl,
                              atr, ttype, strat, stage, ent_time, now, "❌ HARD STOP LOSS",
                              today_str, mem, key, is_target_hit=False)
            mem = _clear_mem_keys(mem, key); continue

        # TSL
        new_tsl, tsl_reason = calc_new_tsl(cp, ent, sl, atr, ttype, mem, key, now)
        if new_tsl > cur_tsl:
            mem = set_tsl(mem, key, new_tsl)
            print(f"[TSL] {sym}: {cur_tsl:.2f} → {new_tsl:.2f} ({tsl_reason})")
            _send_tsl_update(sym, cp, ent, new_tsl, pnl_pct, pnl_rs, tsl_reason)

        if cp <= new_tsl:
            mem = _exit_trade(log_sheet, hist_sheet, i, sym, ent, cp, tgt, sl, new_tsl,
                              atr, ttype, strat, stage, ent_time, now, "🔔 TRAILING SL HIT",
                              today_str, mem, key, is_target_hit=False)
            mem = _clear_mem_keys(mem, key); continue

        # Target hit — SET RE-ENTRY COOLDOWN
        if tgt > 0 and cp >= tgt:
            mem = _exit_trade(log_sheet, hist_sheet, i, sym, ent, cp, tgt, sl, new_tsl,
                              atr, ttype, strat, stage, ent_time, now, "🎯 TARGET HIT",
                              today_str, mem, key, is_target_hit=True)
            mem = _clear_mem_keys(mem, key); continue

    return mem


def _send_tsl_update(sym, cp, ent, new_tsl, pnl_pct, pnl_rs, reason):
    msg = (
        f"🔔 <b>TSL UPDATE</b>\n"
        f"{sym.replace('NSE:','')} LTP ₹{cp:.2f} | P/L {pnl_pct:+.2f}%\n"
        f"Trail SL: ₹{new_tsl:.2f} — {reason}\nP/L: ₹{pnl_rs:+.0f}"
    )
    send_advance_and_premium(msg)


def _exit_trade(log_sheet, hist_sheet, row_idx, sym, ent, exit_p, tgt, sl, tsl_at_exit,
                atr, ttype, strat, stage, ent_time, now, reason, today_str, mem, key,
                is_target_hit=False):
    """
    Exit trade, write to History, send Telegram.
    v15.0: If is_target_hit=True, set re-entry cooldown in memory.
    """
    pnl_pct  = round(((exit_p - ent) / ent) * 100, 2) if ent > 0 else 0
    result   = "WIN ✅" if exit_p > ent else "LOSS ❌"
    hold_str = calc_hold_str(ent_time, now)
    days     = calc_hold_days(ent_time, now)
    pnl_rs   = round((exit_p - ent) * int(CAPITAL_MED // ent), 2) if ent > 0 else 0

    try:
        log_sheet.update(f"K{row_idx}", [[f"EXITED ({reason})"]])
    except Exception as e:
        print(f"[EXIT] Sheet update: {e}")

    try:
        hist_sheet.append_row([
            sym, today_str, ent, today_str, exit_p,
            f"{pnl_pct:.2f}%", result, strat, reason, ttype,
            sl, tsl_at_exit, get_max_price(mem, key), atr, days, CAPITAL_MED, pnl_rs, ""
        ])
    except Exception as e:
        print(f"[EXIT] History: {e}")

    # ── v15.0: Set re-entry cooldown ONLY on TARGET HIT ──────────────────────
    if is_target_hit:
        mem = set_reentry_cooldown(mem, key, today_str)

    print(f"[EXIT] {sym} @ ₹{exit_p:.2f} | {pnl_pct:+.2f}% | {result} | {reason} | RECD:{is_target_hit}")

    msg = (
        f"{'🎯' if 'TARGET' in reason else '🔔' if 'TRAIL' in reason else '❌'} "
        f"<b>TRADE CLOSED — {result}</b>\n\n"
        f"Stock: {sym.replace('NSE:','')}\n"
        f"Entry: ₹{ent:.2f} → Exit: ₹{exit_p:.2f}\n"
        f"P/L: <b>{pnl_pct:+.2f}% (₹{pnl_rs:+.0f})</b>\n"
        f"Hold: {hold_str} | {reason}\n"
        f"TSL at exit: ₹{tsl_at_exit:.2f}"
    )
    if is_target_hit:
        msg += f"\n⏳ Re-entry blocked for {REENTRY_COOLDOWN_DAYS} trading days"

    send_advance_and_premium(msg)
    send_basic(f"{'✅' if exit_p>ent else '❌'} {sym.replace('NSE:','')} {pnl_pct:+.2f}% | {reason}")

    return mem


def _clear_mem_keys(mem, key):
    prefixes = [f"{key}_TSL_", f"{key}_MAX_", f"{key}_LP_", f"{key}_ATR_"]
    parts    = [p for p in mem.split(',') if p.strip() and not any(p.startswith(px) for px in prefixes)]
    return ','.join(parts)


# ══════════════════════════════════════════════════════════════════════════════
# GOOD MORNING — 8:45 AM
# ══════════════════════════════════════════════════════════════════════════════

def send_good_morning(log_sheet, is_bullish, nifty_cmp, nifty_dma, nifty_pct, now):
    try:
        rows    = log_sheet.get_all_values()
        mem_val = rows[3][19] if len(rows)>3 and len(rows[3])>19 else ""
    except: mem_val = ""
    flag_key = now.strftime("%Y-%m-%d") + "_AM"
    if flag_key in mem_val: return

    waiting = 0; traded = 0; waiting_stocks = []
    try:
        rows = log_sheet.get_all_values()
        for row in rows[1:22]:
            row = pad(row); st = str(row[C_STATUS]).upper()
            if "WAITING" in st:
                waiting += 1; waiting_stocks.append(row[C_SYMBOL].replace("NSE:",""))
            elif "TRADED" in st and "EXITED" not in st:
                traded += 1
    except Exception as e:
        print(f"[GM] {e}")

    regime = "🟢 BULLISH" if is_bullish else "⚠️ BEARISH"
    window = f"Entry window: 9:15 AM – {ENTRY_WINDOW_BULLISH_END[0]}:{ENTRY_WINDOW_BULLISH_END[1]:02d} PM" if is_bullish else f"⚠️ Bearish: 9:15–{ENTRY_WINDOW_BEARISH_END[0]}:{ENTRY_WINDOW_BEARISH_END[1]:02d} AM ONLY"

    msg_adv = (
        f"🌅 <b>GOOD MORNING — {now.strftime('%d %b %Y')}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Market: {regime}\n"
        f"Nifty: ₹{nifty_cmp:.0f} | 20DMA: ₹{nifty_dma:.0f} | {nifty_pct:+.2f}%\n\n"
        f"📊 Active: {traded}/{MAX_TRADES} | Watching: {waiting}\n"
        f"{window}\n"
        f"RSI filter: < {RSI_MAX_BULLISH if is_bullish else RSI_MAX_BEARISH} | Re-entry: {REENTRY_COOLDOWN_DAYS}d cooldown after target\n\n"
        f"{'Watching: ' + ', '.join(waiting_stocks[:5]) if waiting_stocks else 'No WAITING stocks'}\n\n"
        f"<i>v15.0 — RSI + Time + Nifty + Re-entry filters</i>"
    )
    msg_basic = f"🌅 Good Morning!\nMarket: {regime} | Nifty: ₹{nifty_cmp:.0f}\nSignals: {waiting}\n📱 ai360trading.in/membership"
    send_advance_and_premium(msg_adv); send_basic(msg_basic)
    print(f"[GM] Sent — {waiting} waiting, {traded} active")


# ══════════════════════════════════════════════════════════════════════════════
# MID-DAY PULSE — 12:28-12:38
# ══════════════════════════════════════════════════════════════════════════════

def send_midday_pulse(log_sheet, mem, now, is_bullish):
    try:
        rows   = log_sheet.get_all_values()
        t4_val = rows[3][19] if len(rows)>3 and len(rows[3])>19 else ""
        if (now.strftime("%Y-%m-%d") + "_MD") in t4_val: return
    except: return
    try:
        rows = log_sheet.get_all_values(); open_trades = []; total_pnl = 0.0
        for row in rows[1:22]:
            row = pad(row); st = str(row[C_STATUS]).upper()
            if "TRADED" not in st or "EXITED" in st: continue
            sym = str(row[C_SYMBOL]).replace("NSE:","").strip()
            cp  = to_f(row[C_LIVE_PRICE]); ent = to_f(row[C_ENTRY_PRICE])
            key = sym_key(row[C_SYMBOL]); tsl = get_tsl(mem, key)
            pct = ((cp-ent)/ent*100) if ent>0 else 0
            qty = to_f(row[C_QTY]); pnl_r = round((cp-ent)*qty,0) if qty>0 else 0
            total_pnl += pnl_r
            open_trades.append(f"{'✅' if pct>=0 else '❌'} {sym} {pct:+.2f}% | TSL ₹{tsl:.2f}")
        lines = "\n".join(open_trades) if open_trades else "No open trades"
        msg   = (
            f"📊 <b>MID-DAY PULSE</b>\n━━━━━━━━━━━━━━━━━━━━\n{lines}\n\n"
            f"{'💰' if total_pnl>=0 else '📉'} Unrealised: <b>₹{total_pnl:+.0f}</b>\n"
            f"<i>Entry window ends {'2:30 PM' if is_bullish else '11:00 AM'}</i>"
        )
        send_advance_and_premium(msg); print(f"[MIDDAY] {len(open_trades)} trades, ₹{total_pnl:+.0f}")
    except Exception as e:
        print(f"[MIDDAY] {e}")


# ══════════════════════════════════════════════════════════════════════════════
# MARKET CLOSE — 15:15-15:45
# ══════════════════════════════════════════════════════════════════════════════

def send_market_close_summary(log_sheet, hist_sheet, mem, now, is_bullish, nifty_pct):
    try:
        rows   = log_sheet.get_all_values()
        t4_val = rows[3][19] if len(rows)>3 and len(rows[3])>19 else ""
        if (now.strftime("%Y-%m-%d") + "_PM") in t4_val: return
    except: return
    try:
        rows = log_sheet.get_all_values(); open_list = []; total_unrl = 0.0
        for row in rows[1:22]:
            row = pad(row); st = str(row[C_STATUS]).upper()
            if "TRADED" not in st or "EXITED" in st: continue
            sym  = str(row[C_SYMBOL]).replace("NSE:","").strip()
            cp   = to_f(row[C_LIVE_PRICE]); ent = to_f(row[C_ENTRY_PRICE])
            key  = sym_key(row[C_SYMBOL]); tsl = get_tsl(mem, key)
            pct  = ((cp-ent)/ent*100) if ent>0 else 0
            qty  = to_f(row[C_QTY]); pnl_r = round((cp-ent)*qty,0) if qty>0 else 0
            total_unrl += pnl_r
            open_list.append(f"{'✅' if pct>=0 else '🔴'} {sym} {pct:+.2f}% | TSL ₹{tsl:.0f}")
        today_str = now.strftime("%Y-%m-%d"); wins=losses=0; today_pnl=0.0
        try:
            for r in hist_sheet.get_all_values()[1:]:
                if len(r)>3 and str(r[3])==today_str:
                    if "WIN" in str(r[6]).upper(): wins+=1
                    elif "LOSS" in str(r[6]).upper(): losses+=1
                    try: today_pnl+=float(str(r[16]).replace(',',''))
                    except: pass
        except: pass

        msg_adv = (
            f"🔔 <b>MARKET CLOSED — {today_str}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"Market: {'🟢 BULLISH' if is_bullish else '⚠️ BEARISH'} | Nifty: {nifty_pct:+.2f}%\n\n"
            f"Today: {wins}✅ {losses}❌ | {'💰' if today_pnl>=0 else '📉'} Realised: ₹{today_pnl:+.0f}\n\n"
            f"{'📤 Exited Today:' + chr(10) if wins+losses>0 else ''}"
            f"Holding Overnight ({len(open_list)} trades):\n"
            f"{chr(10).join(open_list) if open_list else 'No overnight holds'}\n\n"
            f"Unrealised: ₹{total_unrl:+.0f}\n✅ Overnight holds monitored via TSL"
        )
        msg_basic = f"Market closed.\nWins: {wins} | Losses: {losses}\nOpen: {len(open_list)}\nFull report → Advance/Premium"
        send_advance_and_premium(msg_adv); send_basic(msg_basic)
        print(f"[CLOSE] {wins}W {losses}L, {len(open_list)} overnight")
    except Exception as e:
        print(f"[CLOSE] {e}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    now      = datetime.now(IST)
    today_s  = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    dow      = now.weekday()

    print(f"\n{'='*55}")
    print(f"AI360 Trading Bot v15.0 — {now.strftime('%d %b %Y %H:%M')} IST")
    print(f"{'='*55}")

    if is_holiday(today_s): print(f"[SKIP] Holiday: {today_s}"); return
    if dow >= 5: print("[SKIP] Weekend"); return
    if not is_market_hours(now):
        if time_str < "08:44" or time_str > "08:52":
            print(f"[SKIP] Outside hours: {time_str}"); return

    try:
        log, hist, nifty, bm = get_sheets()
        print("[SHEETS] Connected ✅")
    except Exception as e:
        print(f"[SHEETS] Failed: {e}"); return

    is_bullish, nifty_cmp, nifty_dma, nifty_pct = get_market_regime(nifty)

    try:
        rows = log.get_all_values()
        mem  = rows[3][C_SYS_CTRL] if len(rows)>3 and len(rows[3])>C_SYS_CTRL else ""
    except Exception as e:
        print(f"[MEM] T4 read: {e}"); mem = ""

    mem = clean_mem(mem)

    # Count today's entries
    today_entries = sum(1 for p in mem.split(",") if p.strip().startswith(today_s + "_ENTRY_"))

    if "08:44" <= time_str <= "08:52":
        send_good_morning(log, is_bullish, nifty_cmp, nifty_dma, nifty_pct, now)

    if is_market_hours(now):
        mem, today_entries = step_a_enter_trades(
            log, nifty, bm, mem, now, is_bullish, nifty_pct, today_entries
        )
        mem = step_b_monitor_trades(log, hist, nifty, mem, now, is_bullish)

        if "12:28" <= time_str <= "12:38":
            send_midday_pulse(log, mem, now, is_bullish)

        if "15:15" <= time_str <= "15:45":
            send_market_close_summary(log, hist, mem, now, is_bullish, nifty_pct)

    try:
        log.update([[mem]], "Y1")
        print(f"[MEM] T4 saved: {len(mem):,} chars")
    except Exception as e:
        print(f"[MEM] T4 save: {e}")

    print(f"[DONE] {time_str} IST | Bullish:{is_bullish} | Entries:{today_entries}")


if __name__ == "__main__":
    main()
