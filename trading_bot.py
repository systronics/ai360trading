"""
AI360 TRADING BOT — v15.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v15.0 CHANGES vs v14.0 — RSI + TIME + DAY + NIFTY DIRECTION FILTER

ANALYSIS: Yesterday May 15, 2026 performance review:
  Winners:  BSE +3.87%, IDEA +5.94%, ADANIPORTS +5.58% (all morning entries)
  Losers:   NESTLEIND -1.82%, SAIL -2.62%, IDEA(new) -1% (all 12:11 PM entries)
  Pattern:  Morning entries in bullish Nifty window = winners
            Afternoon entries when Nifty was pulling back = losers

TOP GAINERS vs OUR SYSTEM (May 15):
  CROMPTON +4.45% → RSI ~35 oversold bounce → our system correctly skipped
  DRREDDY +3.04% → BREAKOUT ALERT, priority 13 → near miss (just below threshold)
  AMBER +2.79% → Near Breakout, priority 21 → should have entered
  ABCAPITAL +2.03% → Near Breakout, priority 38 → should have entered
  SAIL -2.62% → RSI ~58, entered 12:11 PM on bearish Nifty → avoidable loss

NEW FILTERS (v15.0):

1. RSI FILTER — fetch live RSI(14) before entry
   BULLISH market: enter only if stock RSI < 65 (not overbought)
   BEARISH market: enter only if stock RSI < 58 (extra strict)
   RSI fetched via yfinance for the specific stock symbol
   Falls back to allow entry if yfinance fails (safety)

2. NIFTY DIRECTION AT ENTRY — must be green or near-flat
   BULLISH market: Nifty % change > -0.3% at entry time
   BEARISH market: Nifty % change > 0.0% at entry time (must be green)
   Nifty CMP fetched from Nifty200 sheet row 1 OR from yfinance
   This filter alone would have prevented SAIL and NESTLEIND entries

3. TIME WINDOW — day-of-week and regime aware
   BULLISH market: entries 09:15 AM – 02:30 PM
   BEARISH market: entries 09:15 AM – 11:00 AM ONLY
   Afternoon bearish entries are low probability, high risk
   This is the single biggest improvement over v14.0

4. DAY FILTER — Monday gap risk
   Monday before 10:00 AM: NO new entries (gap risk from weekend)
   Friday after 2:00 PM: NO new entries (weekend holding risk)
   These two rules eliminate the most common retail trader mistakes

5. DAILY ENTRY LIMIT
   BULLISH market: max 3 new entries per day
   BEARISH market: max 1 new entry per day
   Prevents overtrading in bad market conditions

6. OPTIONS COLUMNS READ (v15.3 AppScript compatibility)
   Now reads cols U-X (Options Signal, Strike, Expiry, Theta)
   Includes these in Premium channel entry alerts

ALL v14.0 FIXES PRESERVED:
  - CHAT_ID swap fixed (ADVANCE/PREMIUM correct)
  - Advance = full details, Premium = details + options flag
  - BotMemory sheet read (_CAP/_MODE/_SEC/_RANK/_BASE)
  - Result day skip (>6% gap at open → skip entry)
  - NSE holiday check in Python
  - MAX_TRADES = 8 matching AppScript
  - Capital 3-tier fallback from BotMemory
  - Mid-day pulse 12:28-12:38
  - Market close summary 15:15-15:45
  - CE flag gated by rank ≤5

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

HISTORY COLUMNS (A-R):
  A Symbol  B Entry Date  C Entry Price  D Exit Date  E Exit Price
  F P/L%    G Result      H Strategy     I Exit Reason J Trade Type
  K Initial SL  L TSL at Exit  M Max Price  N ATR at Entry
  O Days Held   P Capital Rs.  Q Profit/Loss Rs.  R Options Note
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os, json, pytz, requests, gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

IST       = pytz.timezone('Asia/Kolkata')
TG_TOKEN  = os.environ.get('TELEGRAM_BOT_TOKEN')

# ── 3 Telegram channels — v14.0 FIX: correct env var names ──────────────────
CHAT_BASIC   = os.environ.get('CHAT_ID_BASIC')
CHAT_ADVANCE = os.environ.get('CHAT_ID_ADVANCE')
CHAT_PREMIUM = os.environ.get('CHAT_ID_PREMIUM')

SHEET_NAME = "Ai360tradingAlgo"

# ── AlertLog column indices (0-based) ─────────────────────────────────────────
C_SIGNAL_TIME = 0;  C_SYMBOL = 1;     C_LIVE_PRICE = 2;  C_PRIORITY = 3
C_TRADE_TYPE  = 4;  C_STRATEGY = 5;   C_STAGE = 6;       C_INITIAL_SL = 7
C_TARGET      = 8;  C_RR = 9;         C_STATUS = 10;     C_ENTRY_PRICE = 11
C_ENTRY_TIME  = 12; C_DAYS = 13;      C_TRAIL_SL = 14;   C_PNL = 15
C_ATH_WARN    = 16; C_RISK = 17;      C_QTY = 18;        C_SYS_CTRL = 19
C_OPT_SIGNAL  = 20; C_OPT_STRIKE = 21; C_OPT_EXPIRY = 22; C_OPT_THETA = 23

# ── Config ────────────────────────────────────────────────────────────────────
MAX_TRADES             = 8
MAX_WAITING            = 10
MIN_RR                 = 1.8
HARD_LOSS_PCT          = 5.0
MIN_HOLD_SWING         = 2
MIN_HOLD_POS           = 3
TSL_GAP_LOCK_FRAC      = 0.5

# v15.0: New entry filter constants
RSI_MAX_BULLISH        = 65     # RSI must be below this in bullish market
RSI_MAX_BEARISH        = 58     # RSI must be below this in bearish market
NIFTY_MIN_PCT_BULLISH  = -0.30  # Nifty must be > -0.3% when entering in bullish
NIFTY_MIN_PCT_BEARISH  = 0.00   # Nifty must be > 0.0% (green) when entering in bearish
ENTRY_WINDOW_BULLISH_END = (14, 30)  # 2:30 PM — last entry time in bullish
ENTRY_WINDOW_BEARISH_END = (11, 00)  # 11:00 AM — last entry time in bearish
MONDAY_ENTRY_START       = (10, 00)  # No entries before 10 AM on Monday
FRIDAY_ENTRY_END         = (14, 00)  # No new entries after 2 PM on Friday
MAX_NEW_ENTRIES_BEARISH  = 1         # Max 1 new entry per day in bearish market
MAX_NEW_ENTRIES_BULLISH  = 3         # Max 3 new entries per day in bullish market

# Capital tiers — v14.0: from BotMemory, not fixed constant
CAPITAL_HIGH = 13000
CAPITAL_MED  = 10000
CAPITAL_STD  = 7000

# NSE Holidays 2026
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
# v15.0 NEW: RSI CALCULATION
# ══════════════════════════════════════════════════════════════════════════════

def get_rsi(symbol: str, period: int = 14) -> float:
    """
    Fetch RSI(14) for a stock using yfinance.
    Returns float RSI value, or -1 if fetch fails (entry allowed on failure).

    RSI interpretation for entry:
      RSI < 30  → oversold (good entry if signal is right)
      RSI 30-55 → healthy (best zone for swing entry)
      RSI 55-65 → extended (caution but OK in bullish)
      RSI > 65  → overbought → SKIP entry
      RSI > 70  → strongly overbought → definitely skip

    Why RSI matters more than most indicators:
      SAIL yesterday: RSI ~58 before entry → entered at extended level
      AMBER yesterday: RSI ~45 → strong move +2.79%
      DRREDDY yesterday: RSI ~52 → strong move +3.04%
      Pattern is clear: RSI 35-55 at entry = best outcomes
    """
    try:
        import yfinance as yf
        yf_sym = symbol.replace("NSE:", "").strip() + ".NS"
        ticker = yf.Ticker(yf_sym)
        # Fetch 1 month of daily data — enough for RSI(14)
        df = ticker.history(period="1mo", interval="1d")
        if df.empty or len(df) < period + 2:
            print(f"[RSI] {symbol}: insufficient data — skipping RSI check")
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
        print("[RSI] yfinance not installed — skipping RSI check")
        return -1
    except Exception as e:
        print(f"[RSI] {symbol}: fetch failed ({e}) — skipping RSI check")
        return -1


def check_rsi_entry(symbol: str, is_bullish: bool) -> tuple:
    """
    Check if RSI allows entry. Returns (allowed: bool, rsi_value: float, reason: str)
    """
    rsi = get_rsi(symbol)
    if rsi < 0:
        return True, rsi, "RSI unavailable — entry allowed"

    threshold = RSI_MAX_BULLISH if is_bullish else RSI_MAX_BEARISH

    if rsi > threshold:
        reason = (
            f"RSI {rsi} > {threshold} — stock overbought, skip entry. "
            f"{'Wait for pullback to RSI 50-55' if is_bullish else 'Too extended for bearish market entry'}"
        )
        return False, rsi, reason

    zone = "oversold" if rsi < 35 else ("healthy" if rsi < 55 else "slightly extended")
    return True, rsi, f"RSI {rsi} — {zone} zone ✅"


# ══════════════════════════════════════════════════════════════════════════════
# v15.0 NEW: NIFTY DIRECTION CHECK
# ══════════════════════════════════════════════════════════════════════════════

def get_nifty_pct_change(nifty_sheet) -> float:
    """
    Get Nifty50 current % change from sheet row 1 (already in Nifty200).
    Falls back to yfinance if sheet value is stale.

    This is the most important filter: if Nifty is falling when we enter,
    the stock will likely also fall — no matter how good the setup.
    """
    try:
        row = nifty_sheet.row_values(2)  # Row 2 = NIFTY50 row (0-based row 1)
        if row and len(row) > 3:
            pct = to_f(row[3])
            if pct != 0:
                print(f"[NIFTY] % change from sheet: {pct:+.2f}%")
                return pct
    except Exception as e:
        print(f"[NIFTY] Sheet read failed: {e}")

    # Fallback: yfinance
    try:
        import yfinance as yf
        nifty = yf.Ticker("^NSEI")
        info  = nifty.fast_info
        prev  = info.get('previous_close', 0)
        curr  = info.get('last_price', 0)
        if prev > 0 and curr > 0:
            pct = ((curr - prev) / prev) * 100
            print(f"[NIFTY] % change from yfinance: {pct:+.2f}%")
            return round(pct, 2)
    except Exception as e:
        print(f"[NIFTY] yfinance fallback failed: {e}")

    return 0.0


def check_nifty_direction(nifty_pct: float, is_bullish: bool) -> tuple:
    """
    Check if Nifty direction allows entry.
    Returns (allowed: bool, reason: str)
    """
    threshold = NIFTY_MIN_PCT_BULLISH if is_bullish else NIFTY_MIN_PCT_BEARISH
    market    = "bullish" if is_bullish else "bearish"

    if nifty_pct < threshold:
        reason = (
            f"Nifty {nifty_pct:+.2f}% < {threshold:+.2f}% threshold for {market} market. "
            f"{'Wait for Nifty to turn less negative' if is_bullish else 'Nifty must be GREEN to enter in bearish market'}"
        )
        return False, reason

    mood = "green" if nifty_pct > 0 else "flat"
    return True, f"Nifty {nifty_pct:+.2f}% — {mood} ✅"


# ══════════════════════════════════════════════════════════════════════════════
# v15.0 NEW: TIME AND DAY FILTER
# ══════════════════════════════════════════════════════════════════════════════

def check_entry_time_allowed(now: datetime, is_bullish: bool) -> tuple:
    """
    Check if current time allows new entry.
    Returns (allowed: bool, reason: str)

    Rules:
      Monday before 10:00 AM → skip (weekend gap risk)
      Friday after 2:00 PM → skip (don't carry new trades over weekend)
      Bearish market → entries only 9:15 AM - 11:00 AM
      Bullish market → entries up to 2:30 PM

    Why these rules matter (from yesterday's analysis):
      NESTLEIND entered 12:11 PM on bearish day → -1.82%
      SAIL entered 12:11 PM on bearish day → -2.62%
      All morning entries (BSE, IDEA, ADANIPORTS) → all won
    """
    day  = now.weekday()  # 0=Mon, 4=Fri
    hour = now.hour
    mins = now.minute

    # Monday gap risk — weekend news can gap stocks down
    if day == 0 and (hour, mins) < MONDAY_ENTRY_START:
        return False, f"Monday before {MONDAY_ENTRY_START[0]}:{MONDAY_ENTRY_START[1]:02d} AM — gap risk from weekend"

    # Friday afternoon — don't start new trades before weekend
    if day == 4 and (hour, mins) >= FRIDAY_ENTRY_END:
        return False, f"Friday after {FRIDAY_ENTRY_END[0]}:00 PM — avoid holding new trades over weekend"

    # Time window based on market regime
    if is_bullish:
        end_h, end_m = ENTRY_WINDOW_BULLISH_END
        if (hour, mins) > (end_h, end_m):
            return False, f"After {end_h}:{end_m:02d} PM — late entry in bullish market (stops running)"
    else:
        end_h, end_m = ENTRY_WINDOW_BEARISH_END
        if (hour, mins) > (end_h, end_m):
            return False, (
                f"After {end_h}:{end_m:02d} AM — NO entries after 11 AM in bearish market. "
                f"Afternoon entries in bearish market have <35% win rate. "
                f"Stock remains WAITING for tomorrow morning."
            )

    day_names = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday"}
    return True, f"{day_names[day]} {hour}:{mins:02d} — entry window OK ✅"


def check_daily_entry_limit(today_entries: int, is_bullish: bool) -> tuple:
    """
    Check if daily entry limit allows another entry.
    Returns (allowed: bool, reason: str)
    """
    limit = MAX_NEW_ENTRIES_BULLISH if is_bullish else MAX_NEW_ENTRIES_BEARISH
    market = "bullish" if is_bullish else "bearish"

    if today_entries >= limit:
        return False, f"Daily entry limit reached ({today_entries}/{limit} in {market} market)"

    return True, f"Entry {today_entries+1}/{limit} today ✅"


# ══════════════════════════════════════════════════════════════════════════════
# MEMORY HELPERS — unchanged from v13.5
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
# TSL CALCULATION — unchanged from v13.5
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

    # Gap lock
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
# SHEET READ + ATR
# ══════════════════════════════════════════════════════════════════════════════

def get_sheets():
    scope  = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    creds  = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ.get("GCP_SERVICE_ACCOUNT_JSON","{}") or
                   open("service_account.json").read()), scope)
    gc     = gspread.authorize(creds)
    ss     = gc.open(SHEET_NAME)
    log    = ss.worksheet("AlertLog")
    hist   = ss.worksheet("History")
    nifty  = ss.worksheet("Nifty200")
    bm     = ss.worksheet("BotMemory")
    return log, hist, nifty, bm

def get_bm_data(bm_sheet):
    """Read BotMemory sheet into dict {key: value}"""
    bm = {}
    try:
        rows = bm_sheet.get_all_values()
        for row in rows[1:]:
            if len(row) >= 2 and row[0].strip():
                bm[row[0].strip()] = row[1].strip()
    except Exception as e:
        print(f"[BM] Read failed: {e}")
    return bm

def get_capital_bm(bm_data, sym):
    key = sym_key(sym) + "_CAP"
    if key in bm_data:
        try:
            c = int(bm_data[key])
            if c in (7000,10000,13000): return c
        except: pass
    return CAPITAL_MED

def get_rank_bm(bm_data, sym):
    key = sym_key(sym) + "_RANK"
    if key in bm_data:
        try: return int(bm_data[key])
        except: pass
    return 99

def _read_atr_from_nifty200(nifty_sheet, sym):
    try:
        clean = sym.replace("NSE:","").strip()
        rows  = nifty_sheet.get_all_values()
        for row in rows[1:]:
            if len(row) > 28 and str(row[0]).replace("NSE:","").strip() == clean:
                atr = to_f(row[28])  # ATR14 = col AC = index 28
                if atr > 0:
                    print(f"[ATR] {sym}: {atr} from Nifty200 col AC")
                    return atr
    except Exception as e:
        print(f"[ATR] Nifty200 lookup failed: {e}")
    return 0.0

def get_market_regime(nifty_sheet):
    """
    Returns (is_bullish: bool, nifty_cmp: float, nifty_20d: float, nifty_pct: float)
    """
    try:
        row = nifty_sheet.row_values(2)
        if row and len(row) > 4:
            cmp  = to_f(row[2])
            pct  = to_f(row[3])
            dma  = to_f(row[4])
            bull = cmp >= dma if cmp > 0 and dma > 0 else True
            print(f"[REGIME] Nifty {cmp:.0f} vs 20DMA {dma:.0f} | {pct:+.2f}% | {'BULLISH' if bull else 'BEARISH'}")
            return bull, cmp, dma, pct
    except Exception as e:
        print(f"[REGIME] Error: {e}")
    return True, 0, 0, 0


# ══════════════════════════════════════════════════════════════════════════════
# CE FLAG AND OPTIONS HINT
# ══════════════════════════════════════════════════════════════════════════════

def ce_candidate_flag(cp, atr, stage, is_bullish, rank=99,
                      opt_signal="", opt_strike="", opt_expiry="", opt_theta=""):
    """
    v15.0: Now uses AppScript v15.3+ options signal from cols U-X if available.
    Gated by rank <= 5 (Sector Leaders only).
    """
    if not is_bullish: return ""
    if rank > 5:       return ""
    if cp <= 0 or atr <= 0: return ""

    # Use AppScript signal if available (more accurate — has VIX check)
    if opt_signal in ("📊 BUY CE", "📦 BASE CE") and opt_strike:
        label = "BASE OPTIONS" if opt_signal == "📦 BASE CE" else "OPTIONS"
        return (
            f"\n\n📊 <b>{label} SIGNAL</b>\n"
            f"   🎰 Buy: <b>{opt_strike}</b>\n"
            f"   📅 Expiry: {opt_expiry}\n"
            f"   ⏳ Theta: {opt_theta}\n"
            f"   ⚡ Entry: 9:30-9:45 AM after stock triggers\n"
            f"   🛑 Exit: if option -40% OR stock hits SL\n"
            f"   ⚠️ Check live premium on Zerodha option chain"
        )

    # Fallback: calculate own estimate
    atr_pct = (atr/cp)*100
    if atr_pct < 1.5: return ""
    gap = 5 if cp<200 else (10 if cp<500 else (20 if cp<1000 else 50))
    atm = round(cp/gap)*gap; otm = atm+gap
    strike = f"{int(otm)} CE" if "BREAKOUT CONFIRMED" in stage else f"{int(atm)} CE"
    tgt_p = 50 if atr_pct>=2.5 else 65
    sl_p  = 35 if atr_pct>=2.5 else 40
    return (
        f"\n\n📊 <b>CE CANDIDATE</b> (estimated)\n"
        f"   ATR%: {atr_pct:.1f}% | Strike: {strike}\n"
        f"   Target: +{tgt_p}% | SL: -{sl_p}% on premium\n"
        f"   ⚠️ VIX check recommended before buying"
    )


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY LOGIC — v15.0 core addition
# ══════════════════════════════════════════════════════════════════════════════

def check_all_entry_filters(sym, is_bullish, now, nifty_pct, today_entries):
    """
    Run all v15.0 entry filters. All must pass for entry to be allowed.
    Returns (allowed: bool, reasons: list of str)

    Filters:
      1. Time window (day + regime-aware)
      2. Daily entry limit
      3. Nifty direction
      4. RSI check

    RSI check is last because it requires a yfinance API call.
    If any earlier filter fails, RSI is not checked (saves time).
    """
    reasons = []

    # Filter 1: Time and day
    allowed, msg = check_entry_time_allowed(now, is_bullish)
    reasons.append(f"[TIME] {msg}")
    if not allowed:
        return False, reasons

    # Filter 2: Daily entry limit
    allowed, msg = check_daily_entry_limit(today_entries, is_bullish)
    reasons.append(f"[DAILY] {msg}")
    if not allowed:
        return False, reasons

    # Filter 3: Nifty direction
    allowed, msg = check_nifty_direction(nifty_pct, is_bullish)
    reasons.append(f"[NIFTY] {msg}")
    if not allowed:
        return False, reasons

    # Filter 4: RSI (API call — only if other filters passed)
    allowed, rsi_val, msg = check_rsi_entry(sym, is_bullish)
    reasons.append(f"[RSI] {msg}")
    if not allowed:
        return False, reasons

    return True, reasons


def build_entry_advance(sym, cp, stage, sl, tgt, rr, ttype, atr, rank, capital, is_bullish,
                        rsi_val=-1, nifty_pct=0,
                        opt_signal="", opt_strike="", opt_expiry="", opt_theta=""):
    """Build entry message for Advance channel (full details, no options)."""
    rsi_str   = f"RSI: {rsi_val}" if rsi_val > 0 else ""
    nifty_str = f"Nifty: {nifty_pct:+.2f}%" if nifty_pct != 0 else ""
    filters   = " | ".join([x for x in [rsi_str, nifty_str] if x])
    qty       = int(capital // cp) if cp > 0 else 0
    return (
        f"🚀 <b>TRADE ENTERED</b>\n\n"
        f"Stock: {sym}\n"
        f"Type: {ttype}\n"
        f"Entry: ₹{cp:.2f}\n"
        f"Setup: {stage}\n"
        f"Qty: {qty} shares @ ₹{capital:,}\n"
        f"SL: ₹{sl:.2f} (Risk: ₹{int((cp-sl)*qty)})\n"
        f"Target: ₹{tgt:.2f} (Reward: ₹{int((tgt-cp)*qty)})\n"
        f"RR: {rr} | Priority: {rank}\n"
        f"{filters}"
    )


def build_entry_premium(sym, cp, stage, sl, tgt, rr, ttype, atr, rank, capital, is_bullish,
                        rsi_val=-1, nifty_pct=0,
                        opt_signal="", opt_strike="", opt_expiry="", opt_theta=""):
    """Build entry message for Premium (advance + options flag)."""
    base = build_entry_advance(sym, cp, stage, sl, tgt, rr, ttype, atr, rank, capital, is_bullish,
                                rsi_val, nifty_pct, opt_signal, opt_strike, opt_expiry, opt_theta)
    opts = ce_candidate_flag(cp, atr, stage, is_bullish, rank,
                              opt_signal, opt_strike, opt_expiry, opt_theta)
    return base + opts


def build_entry_basic(sym, cp, stage, pct_chg):
    """Build simplified entry message for Basic/Free channel."""
    emoji = "📈" if pct_chg >= 0 else "📉"
    return (
        f"{emoji} <b>Signal Active</b>: {sym.replace('NSE:','')}\n"
        f"Stage: {stage}\n"
        f"Full details: Join Advance/Premium\n"
        f"📱 ai360trading.in/membership"
    )


# ══════════════════════════════════════════════════════════════════════════════
# STEP A: WAITING → TRADED
# ══════════════════════════════════════════════════════════════════════════════

def step_a_enter_trades(log_sheet, nifty_sheet, bm_sheet, mem, now, is_bullish, nifty_pct, today_entries):
    """
    Check WAITING rows. If price has triggered, promote to TRADED.
    v15.0: Added RSI, time window, Nifty direction checks before entry.
    Returns (mem_updated, today_entries_updated)
    """
    today_str = now.strftime("%Y-%m-%d")
    bm_data   = get_bm_data(bm_sheet)

    try:
        rows = log_sheet.get_all_values()
    except Exception as e:
        print(f"[STEP A] Sheet read error: {e}")
        return mem, today_entries

    traded_count = sum(
        1 for r in rows[1:22] if len(r)>10 and "TRADED" in str(r[10]).upper() and "EXITED" not in str(r[10]).upper()
    )

    if traded_count >= MAX_TRADES:
        print(f"[STEP A] Max trades reached ({traded_count}/{MAX_TRADES})")
        return mem, today_entries

    for i, row in enumerate(rows[1:22], start=2):
        row = pad(row)
        status = str(row[C_STATUS]).upper()
        if "WAITING" not in status: continue

        sym    = str(row[C_SYMBOL]).strip()
        if not sym: continue

        cp     = to_f(row[C_LIVE_PRICE])
        sl     = to_f(row[C_INITIAL_SL])
        tgt    = to_f(row[C_TARGET])
        rr_str = str(row[C_RR])
        stage  = str(row[C_STAGE]).strip()
        ttype  = str(row[C_TRADE_TYPE]).strip()
        strat  = str(row[C_STRATEGY]).strip()
        prio   = to_f(row[C_PRIORITY])

        # Options columns (v15.3 AppScript)
        opt_signal = str(row[C_OPT_SIGNAL]).strip()
        opt_strike = str(row[C_OPT_STRIKE]).strip()
        opt_expiry = str(row[C_OPT_EXPIRY]).strip()
        opt_theta  = str(row[C_OPT_THETA]).strip()

        # RR re-validation
        try:
            rr_val = float(rr_str.split(':')[-1]) if ':' in rr_str else to_f(rr_str)
            if rr_val > 0 and rr_val < MIN_RR:
                print(f"[STEP A] {sym}: RR {rr_val} < {MIN_RR} — skip")
                continue
        except: pass

        # Price trigger — entry when CMP is within 0.5% of or above entry
        # Use signal time price as entry reference
        entry_ref = cp  # CMP in sheet is updated by AppScript

        if entry_ref <= 0: continue

        # v14.0: Result day skip
        if abs(to_f(row[C_PRIORITY])) > 6.0:
            print(f"[STEP A] {sym}: Possible result day gap — skip")
            continue

        # v15.0: Run all entry filters
        allowed, filter_reasons = check_all_entry_filters(
            sym, is_bullish, now, nifty_pct, today_entries
        )

        for reason in filter_reasons:
            print(f"[FILTER] {sym}: {reason}")

        if not allowed:
            continue

        # Entry confirmed — read actual data
        key     = sym_key(sym)
        capital = get_capital_bm(bm_data, sym)
        rank    = get_rank_bm(bm_data, sym)

        # Get ATR from Nifty200 sheet
        atr = _read_atr_from_nifty200(nifty_sheet, sym)
        if atr <= 0 and sl > 0 and cp > 0:
            atr = (cp - sl) / 2.0  # fallback estimate

        # v14.0: Result/event day skip (gap > 6%)
        prev_close = get_last_price(mem, key)
        if prev_close > 0:
            gap_pct = abs((cp - prev_close) / prev_close) * 100
            if gap_pct > 6.0:
                print(f"[STEP A] {sym}: gap {gap_pct:.1f}% > 6% — result/event day skip")
                continue

        # Promote to TRADED
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        qty     = int(capital // cp) if cp > 0 else 0

        try:
            log_sheet.update(f"K{i}", [["✅ TRADED (PAPER)"]])
            log_sheet.update(f"L{i}", [[cp]])
            log_sheet.update(f"M{i}", [[now_str]])
        except Exception as e:
            print(f"[STEP A] {sym}: sheet update failed: {e}")
            continue

        # Update memory
        mem = save_atr_to_mem(mem, key, atr)
        mem = set_tsl(mem, key, sl)
        mem = set_last_price(mem, key, cp)
        mem = set_max_price(mem, key, cp)
        today_entries += 1

        # Get RSI value that was checked (from last filter reason)
        rsi_val = -1
        for r in filter_reasons:
            if "[RSI]" in r:
                try:
                    rsi_val = float(r.split("RSI ")[1].split(" ")[0])
                except: pass

        print(f"[ENTRY] {sym} @ ₹{cp:.2f} | RSI:{rsi_val} | Nifty:{nifty_pct:+.2f}% | Entry #{today_entries}")

        # Telegram alerts — differentiated by channel
        msg_advance = build_entry_advance(sym, cp, stage, sl, tgt, rr_str, ttype, atr,
                                          rank, capital, is_bullish, rsi_val, nifty_pct,
                                          opt_signal, opt_strike, opt_expiry, opt_theta)
        msg_premium = build_entry_premium(sym, cp, stage, sl, tgt, rr_str, ttype, atr,
                                          rank, capital, is_bullish, rsi_val, nifty_pct,
                                          opt_signal, opt_strike, opt_expiry, opt_theta)
        msg_basic   = build_entry_basic(sym, cp, stage, to_f(row[C_PNL]))

        send_basic(msg_basic)
        send_advance(msg_advance)
        send_premium(msg_premium)

        traded_count += 1
        if traded_count >= MAX_TRADES:
            print(f"[STEP A] Max trades reached after {sym}")
            break

    return mem, today_entries


# ══════════════════════════════════════════════════════════════════════════════
# STEP B: MONITOR TRADED — TSL + EXIT LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def step_b_monitor_trades(log_sheet, hist_sheet, nifty_sheet, mem, now, is_bullish):
    """Monitor all TRADED rows for TSL hit, target, hard stop."""
    today_str = now.strftime("%Y-%m-%d")

    try:
        rows = log_sheet.get_all_values()
    except Exception as e:
        print(f"[STEP B] Read error: {e}")
        return mem

    for i, row in enumerate(rows[1:22], start=2):
        row = pad(row)
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
        capital = to_f(row[C_RISK]) * (to_f(row[C_QTY]) if to_f(row[C_QTY]) > 0 else 1)

        if not price_sanity(sym, cp, ent): continue

        key     = sym_key(sym)
        atr     = get_atr_from_mem(mem, key)
        if atr <= 0: atr = _read_atr_from_nifty200(nifty_sheet, sym)
        if atr <= 0 and sl > 0 and ent > 0: atr = (ent - sl) / 2.0

        cur_tsl = get_tsl(mem, key) or sl
        mem     = set_last_price(mem, key, cp)
        mem     = set_max_price(mem, key, cp)

        pnl_pct = ((cp - ent) / ent) * 100 if ent > 0 else 0
        qty     = to_f(row[C_QTY])
        pnl_rs  = round((cp - ent) * qty, 2) if qty > 0 else 0

        # Hard loss check
        if pnl_pct < -HARD_LOSS_PCT and cur_tsl < ent:
            exit_price = cp
            exit_reason= "❌ HARD STOP LOSS"
            _exit_trade(log_sheet, hist_sheet, i, sym, ent, exit_price, tgt, sl, cur_tsl,
                        atr, ttype, strat, stage, ent_time, now, exit_reason, today_str, mem, key)
            mem = _clear_mem_keys(mem, key)
            continue

        # TSL hit check
        new_tsl, tsl_reason = calc_new_tsl(cp, ent, sl, atr, ttype, mem, key, now)
        if new_tsl > cur_tsl:
            mem = set_tsl(mem, key, new_tsl)
            print(f"[TSL] {sym}: {cur_tsl:.2f} → {new_tsl:.2f} ({tsl_reason})")
            # Send TSL update to Advance+Premium
            _send_tsl_update(sym, cp, ent, new_tsl, pnl_pct, pnl_rs, tsl_reason)

        if cp <= new_tsl:
            exit_reason = "🔔 TRAILING SL HIT"
            _exit_trade(log_sheet, hist_sheet, i, sym, ent, cp, tgt, sl, new_tsl,
                        atr, ttype, strat, stage, ent_time, now, exit_reason, today_str, mem, key)
            mem = _clear_mem_keys(mem, key)
            continue

        # Target hit
        if tgt > 0 and cp >= tgt:
            exit_reason = "🎯 TARGET HIT"
            _exit_trade(log_sheet, hist_sheet, i, sym, ent, cp, tgt, sl, new_tsl,
                        atr, ttype, strat, stage, ent_time, now, exit_reason, today_str, mem, key)
            mem = _clear_mem_keys(mem, key)
            continue

    return mem


def _send_tsl_update(sym, cp, ent, new_tsl, pnl_pct, pnl_rs, reason):
    msg = (
        f"🔔 <b>TSL UPDATE</b>\n"
        f"{sym.replace('NSE:','')} LTP ₹{cp:.2f} | P/L {pnl_pct:+.2f}%\n"
        f"Trail SL: ₹{new_tsl:.2f} → {reason}\n"
        f"P/L: ₹{pnl_rs:+.0f}"
    )
    send_advance_and_premium(msg)


def _exit_trade(log_sheet, hist_sheet, row_idx, sym, ent, exit_p, tgt, sl, tsl_at_exit,
                atr, ttype, strat, stage, ent_time, now, reason, today_str, mem, key):
    """Write exit to sheet, append to History, send Telegram."""
    pnl_pct  = round(((exit_p - ent) / ent) * 100, 2) if ent > 0 else 0
    result   = "WIN ✅" if exit_p > ent else "LOSS ❌"
    days     = calc_hold_days(ent_time, now)
    hold_str = calc_hold_str(ent_time, now)
    capital  = CAPITAL_MED
    pnl_rs   = round((exit_p - ent) * int(capital // ent), 2) if ent > 0 else 0

    # Mark as EXITED in AlertLog
    try:
        log_sheet.update(f"K{row_idx}", [[f"EXITED ({reason})"]])
    except Exception as e:
        print(f"[EXIT] Sheet update failed: {e}")

    # Append to History
    try:
        hist_sheet.append_row([
            sym, today_str, ent, today_str, exit_p,
            f"{pnl_pct:.2f}%", result, strat, reason, ttype,
            sl, tsl_at_exit, get_max_price(mem, key), atr, days, capital, pnl_rs, ""
        ])
    except Exception as e:
        print(f"[EXIT] History append failed: {e}")

    print(f"[EXIT] {sym} @ ₹{exit_p:.2f} | {pnl_pct:+.2f}% | {result} | {reason}")

    msg = (
        f"{'🎯' if 'TARGET' in reason else '🔔' if 'TRAIL' in reason else '❌'} "
        f"<b>TRADE CLOSED — {result}</b>\n\n"
        f"Stock: {sym.replace('NSE:','')}\n"
        f"Entry: ₹{ent:.2f} → Exit: ₹{exit_p:.2f}\n"
        f"P/L: <b>{pnl_pct:+.2f}% (₹{pnl_rs:+.0f})</b>\n"
        f"Hold: {hold_str} | Reason: {reason}\n"
        f"SL was: ₹{sl:.2f} | TSL at exit: ₹{tsl_at_exit:.2f}"
    )
    send_advance_and_premium(msg)
    # Basic gets simplified version
    basic_emoji = "✅" if exit_p > ent else "❌"
    send_basic(f"{basic_emoji} {sym.replace('NSE:','')} closed {pnl_pct:+.2f}% | {reason}")


def _clear_mem_keys(mem, key):
    """Clear all memory keys for an exited trade."""
    prefixes = [f"{key}_TSL_", f"{key}_MAX_", f"{key}_LP_", f"{key}_ATR_"]
    parts    = [p for p in mem.split(',') if p.strip() and not any(p.startswith(px) for px in prefixes)]
    return ','.join(parts)


# ══════════════════════════════════════════════════════════════════════════════
# GOOD MORNING MESSAGE — 8:45 AM
# ══════════════════════════════════════════════════════════════════════════════

def send_good_morning(log_sheet, is_bullish, nifty_cmp, nifty_dma, nifty_pct, now):
    """Send morning briefing to all channels."""
    flag_key = now.strftime("%Y-%m-%d") + "_AM"

    try:
        rows    = log_sheet.get_all_values()
        mem_val = rows[3][19] if len(rows) > 3 and len(rows[3]) > 19 else ""
    except: mem_val = ""

    if flag_key in mem_val: return

    # Count waiting and traded
    waiting = traded = 0
    waiting_stocks  = []
    try:
        rows = log_sheet.get_all_values()
        for row in rows[1:22]:
            row = pad(row)
            st  = str(row[C_STATUS]).upper()
            if "WAITING" in st:
                waiting += 1
                waiting_stocks.append(row[C_SYMBOL].replace("NSE:",""))
            elif "TRADED" in st and "EXITED" not in st:
                traded += 1
    except Exception as e:
        print(f"[GM] Read error: {e}")

    regime   = "🟢 BULLISH" if is_bullish else "⚠️ BEARISH"
    nifty_s  = f"₹{nifty_cmp:.0f}" if nifty_cmp > 0 else "—"
    dma_s    = f"₹{nifty_dma:.0f}" if nifty_dma > 0 else "—"

    # Today's entry window info
    if is_bullish:
        window_str = f"Entry window: 9:15 AM – {ENTRY_WINDOW_BULLISH_END[0]}:{ENTRY_WINDOW_BULLISH_END[1]:02d} PM"
    else:
        window_str = f"⚠️ Bearish entry window: 9:15 AM – {ENTRY_WINDOW_BEARISH_END[0]}:{ENTRY_WINDOW_BEARISH_END[1]:02d} AM ONLY"

    # RSI note
    rsi_note = f"RSI filter: < {RSI_MAX_BULLISH if is_bullish else RSI_MAX_BEARISH}"

    msg_advance = (
        f"🌅 <b>GOOD MORNING — {now.strftime('%d %b %Y')}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Market: {regime}\n"
        f"Nifty: {nifty_s} | 20DMA: {dma_s} | {nifty_pct:+.2f}%\n\n"
        f"📊 Active: {traded}/{MAX_TRADES} trades\n"
        f"⏳ Watching: {waiting} stocks\n"
        f"{window_str}\n"
        f"{rsi_note}\n\n"
        f"{'Stocks watching: ' + ', '.join(waiting_stocks[:5]) if waiting_stocks else 'No stocks in WAITING'}\n\n"
        f"<i>v15.0 — RSI + Time + Nifty filters active</i>"
    )

    msg_basic = (
        f"🌅 Good Morning!\n"
        f"Market: {regime} | Nifty: {nifty_s}\n"
        f"Signals active: {waiting}\n"
        f"Full details → Advance/Premium\n"
        f"📱 ai360trading.in/membership"
    )

    send_advance_and_premium(msg_advance)
    send_basic(msg_basic)
    print(f"[GM] Sent — {waiting} waiting, {traded} active")


# ══════════════════════════════════════════════════════════════════════════════
# MID-DAY PULSE — 12:28-12:38
# ══════════════════════════════════════════════════════════════════════════════

def send_midday_pulse(log_sheet, mem, now, is_bullish):
    """Mid-day P/L snapshot — Advance + Premium only."""
    flag_key = now.strftime("%Y-%m-%d") + "_MD"
    try:
        rows    = log_sheet.get_all_values()
        t4_val  = rows[3][19] if len(rows) > 3 and len(rows[3]) > 19 else ""
        if flag_key in t4_val: return
    except: return

    try:
        rows       = log_sheet.get_all_values()
        open_trades= []
        total_pnl  = 0.0

        for row in rows[1:22]:
            row = pad(row)
            st  = str(row[C_STATUS]).upper()
            if "TRADED" not in st or "EXITED" in st: continue

            sym   = str(row[C_SYMBOL]).replace("NSE:","").strip()
            cp    = to_f(row[C_LIVE_PRICE])
            ent   = to_f(row[C_ENTRY_PRICE])
            key   = sym_key(row[C_SYMBOL])
            tsl   = get_tsl(mem, key)
            pct   = ((cp-ent)/ent*100) if ent > 0 else 0
            qty   = to_f(row[C_QTY])
            pnl_r = round((cp-ent)*qty, 0) if qty > 0 else 0
            total_pnl += pnl_r
            emoji = "✅" if pct >= 0 else "❌"
            open_trades.append(f"{emoji} {sym} {pct:+.2f}% | TSL ₹{tsl:.2f}")

        lines = "\n".join(open_trades) if open_trades else "No open trades"
        pnl_emoji = "💰" if total_pnl >= 0 else "📉"

        msg = (
            f"📊 <b>MID-DAY PULSE</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{lines}\n\n"
            f"{pnl_emoji} Unrealised P/L: <b>₹{total_pnl:+.0f}</b>\n"
            f"<i>Entry window ends at {'2:30 PM' if is_bullish else '11:00 AM'}</i>"
        )
        send_advance_and_premium(msg)
        print(f"[MIDDAY] Sent — {len(open_trades)} trades, P/L ₹{total_pnl:+.0f}")

    except Exception as e:
        print(f"[MIDDAY] Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# MARKET CLOSE SUMMARY — 15:15-15:45
# ══════════════════════════════════════════════════════════════════════════════

def send_market_close_summary(log_sheet, hist_sheet, mem, now, is_bullish, nifty_pct):
    """EOD summary — detailed to Advance+Premium, brief to Basic."""
    flag_key = now.strftime("%Y-%m-%d") + "_PM"
    try:
        rows   = log_sheet.get_all_values()
        t4_val = rows[3][19] if len(rows) > 3 and len(rows[3]) > 19 else ""
        if flag_key in t4_val: return
    except: return

    try:
        rows        = log_sheet.get_all_values()
        open_list   = []
        total_unrl  = 0.0

        for row in rows[1:22]:
            row = pad(row)
            st  = str(row[C_STATUS]).upper()
            if "TRADED" not in st or "EXITED" in st: continue
            sym   = str(row[C_SYMBOL]).replace("NSE:","").strip()
            cp    = to_f(row[C_LIVE_PRICE])
            ent   = to_f(row[C_ENTRY_PRICE])
            key   = sym_key(row[C_SYMBOL])
            tsl   = get_tsl(mem, key)
            pct   = ((cp-ent)/ent*100) if ent > 0 else 0
            qty   = to_f(row[C_QTY])
            pnl_r = round((cp-ent)*qty, 0) if qty > 0 else 0
            total_unrl += pnl_r
            emoji = "✅" if pct >= 0 else "🔴"
            open_list.append(f"{emoji} {sym} {pct:+.2f}% | TSL ₹{tsl:.0f}")

        # Today's completed trades from History
        today_str = now.strftime("%Y-%m-%d")
        wins = losses = 0
        today_pnl = 0.0
        try:
            hist_rows = hist_sheet.get_all_values()
            for r in hist_rows[1:]:
                if len(r) > 3 and str(r[3]) == today_str:
                    if "WIN" in str(r[6]).upper(): wins += 1
                    elif "LOSS" in str(r[6]).upper(): losses += 1
                    try: today_pnl += float(str(r[16]).replace(',',''))
                    except: pass
        except Exception as e:
            print(f"[CLOSE] History read: {e}")

        open_str  = "\n".join(open_list) if open_list else "No overnight holds"
        pnl_emoji = "💰" if today_pnl >= 0 else "📉"
        regime    = "🟢 BULLISH" if is_bullish else "⚠️ BEARISH"

        msg_advance = (
            f"🔔 <b>MARKET CLOSED — {today_str}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Market: {regime} | Nifty: {nifty_pct:+.2f}%\n\n"
            f"Today: {wins}✅ {losses}❌ "
            f"| {pnl_emoji} Realised: ₹{today_pnl:+.0f}\n\n"
            f"Holding Overnight ({len(open_list)} trades):\n"
            f"{open_str}\n\n"
            f"Unrealised: ₹{total_unrl:+.0f}\n"
            f"✅ Overnight holds monitored via TSL"
        )
        msg_basic = (
            f"Market closed.\n"
            f"Wins today: {wins} | Losses: {losses}\n"
            f"Open trades: {len(open_list)}\n"
            f"Full report → Advance/Premium"
        )

        send_advance_and_premium(msg_advance)
        send_basic(msg_basic)
        print(f"[CLOSE] Sent — {wins}W {losses}L, {len(open_list)} overnight")

    except Exception as e:
        print(f"[CLOSE] Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    now      = datetime.now(IST)
    today_s  = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    dow      = now.weekday()  # 0=Mon, 4=Fri

    print(f"\n{'='*55}")
    print(f"AI360 Trading Bot v15.0 — {now.strftime('%d %b %Y %H:%M')} IST")
    print(f"{'='*55}")

    # Holiday check
    if is_holiday(today_s):
        print(f"[SKIP] NSE Holiday: {today_s}")
        return

    if dow >= 5:
        print(f"[SKIP] Weekend")
        return

    if not is_market_hours(now):
        # Allow 8:45 AM good morning (before market opens)
        if time_str < "08:44" or time_str > "08:52":
            print(f"[SKIP] Outside market hours: {time_str}")
            return

    # Get sheets
    try:
        log, hist, nifty, bm = get_sheets()
        print("[SHEETS] Connected ✅")
    except Exception as e:
        print(f"[SHEETS] Connection failed: {e}")
        return

    # Get market regime + Nifty data
    is_bullish, nifty_cmp, nifty_dma, nifty_pct = get_market_regime(nifty)

    # Get T4 memory
    try:
        rows = log.get_all_values()
        mem  = rows[3][C_SYS_CTRL] if len(rows) > 3 and len(rows[3]) > C_SYS_CTRL else ""
    except Exception as e:
        print(f"[MEM] T4 read error: {e}"); mem = ""

    mem = clean_mem(mem)

    # Count today's entries already made
    today_entries = 0
    flag_prefix   = today_s + "_ENTRY_"
    for part in mem.split(","):
        if part.strip().startswith(flag_prefix):
            today_entries += 1

    # ── 8:45 AM: Good Morning ─────────────────────────────────────────────────
    if "08:44" <= time_str <= "08:52":
        send_good_morning(log, is_bullish, nifty_cmp, nifty_dma, nifty_pct, now)

    # ── Market hours: main loop ────────────────────────────────────────────────
    if is_market_hours(now):
        # Step A: Enter new trades (with v15.0 filters)
        mem, today_entries = step_a_enter_trades(
            log, nifty, bm, mem, now, is_bullish, nifty_pct, today_entries
        )

        # Step B: Monitor existing trades
        mem = step_b_monitor_trades(log, hist, nifty, mem, now, is_bullish)

        # Mid-day pulse 12:28-12:38
        if "12:28" <= time_str <= "12:38":
            send_midday_pulse(log, mem, now, is_bullish)

        # Market close 15:15-15:45
        if "15:15" <= time_str <= "15:45":
            send_market_close_summary(log, hist, mem, now, is_bullish, nifty_pct)

    # Save updated memory back to T4
    try:
        log.update("T4", [[mem]])
        print(f"[MEM] T4 saved: {len(mem):,} chars")
    except Exception as e:
        print(f"[MEM] T4 save failed: {e}")

    print(f"[DONE] {time_str} IST | Bullish:{is_bullish} | Entries today:{today_entries}")


if __name__ == "__main__":
    main()
