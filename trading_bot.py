"""
AI360 TRADING BOT — v14
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v14 CHANGES vs v13.5 — 6 changes, zero sheet-structure changes:

CHANGE 1 — BotMemory sheet replaces T4 cell
  Previous: All memory stored as one giant comma-separated string
            in AlertLog cell T4. Growing toward Google's 50k limit.
  Fix: Each key is now one row in the BotMemory sheet
       (Key | Value | UpdatedAt | Symbol | KeyType).
       First run automatically migrates all live T4 data.
       T4 is cleared after migration. Never written again.
  Why: Scalable, queryable, no size limit, easier to debug.

CHANGE 2 — Bearish market blocks ALL new entries (Step A)
  Previous: is_bullish was computed but never used in Step A.
            Bot would still promote WAITING→TRADED in a falling
            market if a WAITING row already existed.
  Fix: If market is bearish, Step A is skipped entirely.
       Existing TRADED rows continue to be monitored (Step B runs).
  Why: All 7 hard losses occurred during Feb–Apr 2026 correction.
       The regime filter existed in AppScript but was missing in bot.

CHANGE 3 — Re-entry cooldown 5 → 15 trading days
  Previous: 5 trading days. GLENMARK re-entered 3×, ASTRAL 2×,
            NATIONALUM 3×, CUMMINSIND 2× — all in same downtrend.
  Fix: COOLDOWN_DAYS = 15
  Why: Data shows stocks that fail once continue failing for 2–3
       weeks in the same market regime. 15 days = ~3 trading weeks.

CHANGE 4 — TSL_PARAMS STD: breakeven 2% → 4%, lock1 4% → 7%
  Previous: STD breakeven=2.0, lock1=4.0
            Stocks gaining 2.1% then dipping to 1.9% exit at zero.
            8 of 29 trades exited at breakeven with zero profit.
  Fix: breakeven=4.0, lock1=7.0 (trail and gap_lock unchanged)
  Why: Swing trades need room to breathe. 4% is the minimum move
       needed to confirm the breakout is real, not a fakeout.

CHANGE 5 — _HOLD_WARN flag cleared when TSL rises above entry
  Previous: Once set, _HOLD_WARN stayed in memory forever.
            Added permanent bloat even after trade recovered.
  Fix: When TSL moves above entry price (breakeven achieved),
       _HOLD_WARN for that symbol is deleted from BotMemory.

CHANGE 6 — clean_mem() replaced with BotMemory cleanup
  Previous: clean_mem() was a string operation on T4.
            154 orphaned old-format keys were never cleaned.
  Fix: cleanup_botmemory() removes rows for symbols whose
       EXDT is > 30 days ago. Also removes date-stamp rows
       older than 14 days. Runs once per bot cycle.

ALL OTHER CODE IDENTICAL TO v13.5.
Zero changes to: TSL logic (calc_new_tsl), message builders,
ATR read, RR validation, capital tiers, Telegram routing,
Good Morning, Mid-Day Pulse, Market Close, Weekly Summary.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALERTLOG COLUMN MAP (0-based) — UNCHANGED:
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
  T2 = YES/NO switch (still used)
  T4 = CLEARED after migration, no longer written

BOTMEMORY SHEET COLUMNS:
  A=Key | B=Value | C=UpdatedAt | D=Symbol | E=KeyType

HISTORY COLUMNS (A–R) — UNCHANGED:
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

# ── AlertLog column indices (0-based) — UNCHANGED ─────────────────────────────
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

# Capital config — UNCHANGED
CAPITAL_PER_TRADE = 10000
MAX_TRADES        = 5
MAX_WAITING       = 10

# ── v13.5: MIN_RR for re-validation — UNCHANGED ───────────────────────────────
MIN_RR = 1.8

# ── v14 CHANGE 3: Re-entry cooldown raised from 5 → 15 trading days ──────────
COOLDOWN_DAYS = 15

# ── TSL mode parameters — v14 CHANGE 4: STD breakeven/lock1 widened ──────────
TSL_PARAMS = {
    "VCP": {                  # Tight base pre-breakout — UNCHANGED
        "breakeven": 3.0,
        "lock1"    : 5.0,
        "trail"    : 8.0,
        "atr_mult" : 2.0,
        "gap_lock" : 9.0,
    },
    "MOM": {                  # Strong momentum — UNCHANGED
        "breakeven": 2.5,
        "lock1"    : 4.5,
        "trail"    : 7.0,
        "atr_mult" : 1.8,
        "gap_lock" : 8.0,
    },
    "STD": {
        # v14 CHANGE 4: breakeven 2.0→4.0, lock1 4.0→7.0
        # Previous 2% breakeven was causing 8 trades to exit at zero
        # profit when stocks gained 2-3% then pulled back normally.
        # Swing trades need 4% gain before locking at entry.
        "breakeven": 4.0,     # was 2.0
        "lock1"    : 7.0,     # was 4.0
        "trail"    : 10.0,    # UNCHANGED
        "atr_mult" : 2.5,     # UNCHANGED
        "gap_lock" : 8.0,     # UNCHANGED
    },
}

TSL_GAP_LOCK_FRAC = 0.5
MIN_HOLD_SWING    = 2
MIN_HOLD_POS      = 3
HARD_LOSS_PCT     = 5.0


# ══════════════════════════════════════════════════════════════════════════════
# TELEGRAM — UNCHANGED from v13.5
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
# HELPERS — UNCHANGED from v13.5
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
    if not is_bullish: return ""
    if cp <= 0 or atr <= 0: return ""
    atr_pct = (atr / cp) * 100
    if atr_pct < 1.5: return ""
    gap = 5 if cp < 200 else (10 if cp < 500 else (20 if cp < 1000 else 50))
    atm_strike  = round(cp / gap) * gap
    otm_strike  = atm_strike + gap
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
        f"   ATR%: {atr_pct:.1f}% | Strike: {strike_str}\n"
        f"   Target: +{target_pct}% on premium | SL: -{sl_pct}% on premium\n"
        f"   Entry: Only above ₹{cp + atr * 0.3:.1f} (breakout confirm)\n"
        f"   ⚠️ Check actual premium on Zerodha option chain\n"
        f"   ⚠️ Wednesday entry → prefer monthly expiry"
    )


# ══════════════════════════════════════════════════════════════════════════════
# BOTMEMORY — v14 CHANGE 1
# Replaces all T4 string operations. Each key = one sheet row.
# BotMemory sheet columns: Key | Value | UpdatedAt | Symbol | KeyType
# ══════════════════════════════════════════════════════════════════════════════

def _bm_parse_keytype(key: str) -> tuple:
    """
    Given a full key string, return (symbol, keytype) for BotMemory cols D and E.

    Handles both formats found in T4:
      New format: "NSE_CANBK_CAP=10000"  → key stored as "NSE_CANBK_CAP"
      Old format: "NSE_CANBK_TSL_14186"  → stored as-is in Key col

    For date-stamp entries like "2026-04-15_CLEANED":
      symbol = "DATE", keytype = "DATESTAMP"
    """
    if len(key) >= 10 and key[4] == '-' and key[7] == '-':
        return ("DATE", "DATESTAMP")
    parts = key.split('_')
    if len(parts) >= 2 and parts[0] == 'NSE':
        sym = '_'.join(parts[:2])           # e.g. NSE_CANBK
        ktype = '_'.join(parts[2:]) if len(parts) > 2 else ''
        # Strip trailing value from old-format keys like MAX_95315 → MAX
        # KeyType should be the semantic type, not the encoded value
        ktype_base = ktype.split('_')[0] if ktype else ''
        return (sym, ktype_base)
    return ("OTHER", key)


def load_botmemory(ss) -> tuple:
    """
    Read entire BotMemory sheet into a dict {key: value}.
    Returns (mem_dict, bm_sheet, changed_keys_set).
    One API call for all reads — fast and rate-limit friendly.
    """
    try:
        bm_sheet = ss.worksheet("BotMemory")
        rows     = bm_sheet.get_all_values()
        mem_dict = {}
        for row in rows[1:]:            # skip header row
            if row and len(row) >= 2 and row[0]:
                mem_dict[row[0]] = row[1]
        print(f"[MEM] BotMemory loaded: {len(mem_dict)} keys")
        return mem_dict, bm_sheet, set()
    except Exception as e:
        print(f"[MEM] BotMemory load failed: {e}")
        return {}, None, set()


def save_botmemory(bm_sheet, mem_dict: dict, changed_keys: set,
                   deleted_keys: set = None):
    """
    Write only changed/new keys back to BotMemory sheet.
    Delete rows for keys in deleted_keys set.
    Batch update — one API call for updates, one for appends.
    """
    if bm_sheet is None:
        print("[MEM] BotMemory sheet not available — skipping save")
        return

    if deleted_keys is None:
        deleted_keys = set()

    now_str = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')

    # Read current sheet to map key → row number
    try:
        all_rows    = bm_sheet.get_all_values()
        key_to_row  = {}
        for i, row in enumerate(all_rows):
            if i == 0: continue          # skip header
            if row and row[0]:
                key_to_row[row[0]] = i + 1   # 1-based row number
    except Exception as e:
        print(f"[MEM] BotMemory row-map failed: {e}")
        return

    # Delete rows for deleted keys (reverse order to preserve row numbers)
    if deleted_keys:
        rows_to_delete = sorted(
            [key_to_row[k] for k in deleted_keys if k in key_to_row],
            reverse=True
        )
        for row_num in rows_to_delete:
            try:
                bm_sheet.delete_rows(row_num)
            except Exception as e:
                print(f"[MEM] Delete row {row_num} failed: {e}")
        print(f"[MEM] Deleted {len(rows_to_delete)} rows from BotMemory")

    if not changed_keys:
        return

    # Separate updates (existing rows) from new rows (appends)
    cells_to_update = []
    new_rows        = []

    for key in changed_keys:
        if key in deleted_keys:
            continue
        val           = mem_dict.get(key, "")
        sym, ktype    = _bm_parse_keytype(key)

        if key in key_to_row:
            r = key_to_row[key]
            cells_to_update.append(gspread.Cell(r, 2, val))
            cells_to_update.append(gspread.Cell(r, 3, now_str))
        else:
            new_rows.append([key, val, now_str, sym, ktype])

    if cells_to_update:
        try:
            bm_sheet.update_cells(cells_to_update)
        except Exception as e:
            print(f"[MEM] BotMemory cell update failed: {e}")

    if new_rows:
        try:
            bm_sheet.append_rows(new_rows, value_input_option='RAW')
        except Exception as e:
            print(f"[MEM] BotMemory append failed: {e}")

    print(f"[MEM] BotMemory saved: {len(changed_keys)} changed, "
          f"{len(new_rows)} new rows, {len(deleted_keys)} deleted")


def cleanup_botmemory(bm_sheet, mem_dict: dict) -> set:
    """
    v14 replacement for clean_mem().
    Returns a set of keys to delete (passed to save_botmemory as deleted_keys).

    Pass 1: Remove DATE-STAMP entries older than 14 days.
    Pass 2: Find symbols whose EXDT is > 30 days ago,
            remove ALL keys for those symbols.
    Pass 3: Log size so GitHub Actions shows BotMemory health.
    """
    now_ist   = datetime.now(IST)
    cutoff_14 = (now_ist - timedelta(days=14)).strftime("%Y-%m-%d")
    cutoff_30 = (now_ist - timedelta(days=30)).strftime("%Y-%m-%d")

    to_delete = set()

    # Pass 1: stale date-stamp entries
    for key in list(mem_dict.keys()):
        if len(key) >= 10 and key[4] == '-' and key[7] == '-':
            if key[:10] < cutoff_14:
                to_delete.add(key)

    # Pass 2: find symbols exited > 30 days ago
    stale_syms = set()
    for key in mem_dict:
        if '_EXDT_' in key:
            try:
                date_part  = key.split('_EXDT_')[-1][:10]
                sym_prefix = key.split('_EXDT_')[0]    # e.g. NSE_CANBK
                if date_part < cutoff_30:
                    stale_syms.add(sym_prefix)
            except Exception:
                pass

    # Mark all keys for stale symbols for deletion
    for key in list(mem_dict.keys()):
        for sym_prefix in stale_syms:
            if key.startswith(sym_prefix + '_') or key.startswith(sym_prefix + '='):
                to_delete.add(key)

    # Pass 3: size reporting
    remaining = len(mem_dict) - len(to_delete)
    print(f"[MEM] BotMemory cleanup: {len(mem_dict)} keys → "
          f"{remaining} after removing {len(to_delete)} stale keys")
    if remaining > 200:
        print(f"[MEM] 🔴 WARNING: {remaining} keys remaining — investigate growth")
    elif remaining > 100:
        print(f"[MEM] 🟡 NOTICE: {remaining} keys — monitor growth")
    else:
        print(f"[MEM] ✅ BotMemory size: {remaining} keys — OK")

    return to_delete


# ── BotMemory key accessors — drop-in replacements for old _mem_get/_mem_set ─

def bm_get(mem_dict: dict, key: str) -> str:
    """Get a value from BotMemory dict. Returns '' if not found."""
    return mem_dict.get(key, "")

def bm_set(mem_dict: dict, changed_keys: set, key: str, val: str):
    """Set a value in BotMemory dict and mark key as changed."""
    mem_dict[key]     = val
    changed_keys.add(key)

def bm_delete(mem_dict: dict, deleted_keys: set, key: str):
    """Delete a key from BotMemory dict and mark for sheet deletion."""
    if key in mem_dict:
        del mem_dict[key]
    deleted_keys.add(key)

def bm_has(mem_dict: dict, key: str) -> bool:
    """Check if a key exists in BotMemory dict."""
    return key in mem_dict and mem_dict[key] != ""

def bm_contains_prefix(mem_dict: dict, prefix: str) -> bool:
    """Check if any key starts with the given prefix."""
    return any(k.startswith(prefix) for k in mem_dict)


# ══════════════════════════════════════════════════════════════════════════════
# T4 → BOTMEMORY MIGRATION — runs once on first v14 boot
# ══════════════════════════════════════════════════════════════════════════════

def migrate_t4_to_botmemory(log_sheet, bm_sheet, mem_dict: dict,
                             changed_keys: set):
    """
    One-time migration: reads T4 string, parses all entries, writes
    them to BotMemory sheet, then clears T4.

    Called automatically when BotMemory is empty AND T4 has content.
    After migration completes, T4 is set to "MIGRATED_v14" as a marker.
    On all future runs BotMemory is non-empty so this is never called again.

    Handles both key formats found in live T4:
      New format: "NSE_CANBK_CAP=10000"
      Old format: "NSE_CANBK_TSL_14186", "NSE_CANBK_ENTRY", "2026-04-15_CLEANED"

    For old-format keys that encode value in the key name:
      NSE_CANBK_TSL_14186  → Key="NSE_CANBK_TSL", Value="14186" (÷100 later by accessor)
      NSE_CANBK_MAX_95315  → Key="NSE_CANBK_MAX", Value="95315"
      NSE_CANBK_LP_86840   → Key="NSE_CANBK_LP",  Value="86840"
      NSE_CANBK_ATR_3075   → Key="NSE_CANBK_ATR", Value="3075"
      NSE_CANBK_ENTRY      → Key="NSE_CANBK_ENTRY", Value="1"
      NSE_CANBK_HOLD_WARN  → Key="NSE_CANBK_HOLD_WARN", Value="1"
      NSE_CANBK_EX         → Key="NSE_CANBK_EX", Value="1"
      NSE_CANBK_EXDT_2026-04-23 → Key="NSE_CANBK_EXDT", Value="2026-04-23"
      2026-04-15_CLEANED   → Key="2026-04-15_CLEANED", Value="1"
    """
    try:
        t4_raw = str(log_sheet.acell("T4").value or "").strip()
    except Exception as e:
        print(f"[MIGRATE] Could not read T4: {e}")
        return

    if not t4_raw or t4_raw == "MIGRATED_v14":
        print("[MIGRATE] T4 empty or already migrated — skipping")
        return

    parts   = [p.strip() for p in t4_raw.split(',') if p.strip()]
    migrated = 0
    skipped  = 0

    now_ist    = datetime.now(IST)
    cutoff_30  = (now_ist - timedelta(days=30)).strftime("%Y-%m-%d")

    for p in parts:
        try:
            if not p:
                continue

            # ── New format: "NSE_CANBK_CAP=10000" ────────────────────────────
            if '=' in p and not p.startswith('20'):
                key, val = p.split('=', 1)
                key = key.strip()
                val = val.strip()
                if key and val:
                    bm_set(mem_dict, changed_keys, key, val)
                    migrated += 1
                continue

            # ── Date-stamp: "2026-04-15_CLEANED" ─────────────────────────────
            if len(p) >= 10 and p[4] == '-' and p[7] == '-':
                # Only migrate date-stamps from last 14 days
                cutoff_14 = (now_ist - timedelta(days=14)).strftime("%Y-%m-%d")
                if p[:10] >= cutoff_14:
                    bm_set(mem_dict, changed_keys, p, "1")
                    migrated += 1
                else:
                    skipped += 1
                continue

            # ── Old format symbol keys ────────────────────────────────────────
            # These patterns encode value in key name (no = sign)
            parts_k = p.split('_')
            if len(parts_k) < 2 or parts_k[0] != 'NSE':
                skipped += 1
                continue

            sym_prefix = '_'.join(parts_k[:2])   # NSE_CANBK

            # _EXDT_: "NSE_CANBK_EXDT_2026-04-23"
            if '_EXDT_' in p:
                date_val = p.split('_EXDT_')[-1]
                key = f"{sym_prefix}_EXDT"
                # Skip if exited > 30 days ago (stale)
                if date_val[:10] < cutoff_30:
                    skipped += 1
                    continue
                bm_set(mem_dict, changed_keys, key, date_val)
                migrated += 1
                continue

            # _TSL_: "NSE_CANBK_TSL_14186"
            if '_TSL_' in p:
                val = parts_k[-1]
                bm_set(mem_dict, changed_keys, f"{sym_prefix}_TSL", val)
                migrated += 1
                continue

            # _MAX_: "NSE_CANBK_MAX_95315"
            if '_MAX_' in p:
                val = parts_k[-1]
                bm_set(mem_dict, changed_keys, f"{sym_prefix}_MAX", val)
                migrated += 1
                continue

            # _LP_: "NSE_CANBK_LP_86840"
            if '_LP_' in p:
                val = parts_k[-1]
                bm_set(mem_dict, changed_keys, f"{sym_prefix}_LP", val)
                migrated += 1
                continue

            # _ATR_: "NSE_CANBK_ATR_3075"
            if '_ATR_' in p:
                val = parts_k[-1]
                bm_set(mem_dict, changed_keys, f"{sym_prefix}_ATR", val)
                migrated += 1
                continue

            # _CAP_: old "NSE_CANBK_CAP_10000" (pre-v13.3 format, no =)
            if len(parts_k) >= 4 and parts_k[2] == 'CAP':
                val = parts_k[-1]
                bm_set(mem_dict, changed_keys, f"{sym_prefix}_CAP", val)
                migrated += 1
                continue

            # _EX_YYYYMMDD: "NSE_CANBK_EX_20260423"
            if len(parts_k) >= 4 and parts_k[2] == 'EX':
                val = '_'.join(parts_k[3:])
                bm_set(mem_dict, changed_keys, f"{sym_prefix}_EX_{val}", "1")
                migrated += 1
                continue

            # _ENTRY: "NSE_CANBK_ENTRY" (flag, no value)
            if p.endswith('_ENTRY'):
                bm_set(mem_dict, changed_keys, f"{sym_prefix}_ENTRY", "1")
                migrated += 1
                continue

            # _HOLD_WARN: "NSE_CANBK_HOLD_WARN"
            if p.endswith('_HOLD_WARN'):
                bm_set(mem_dict, changed_keys, f"{sym_prefix}_HOLD_WARN", "1")
                migrated += 1
                continue

            # _EX: plain flag "NSE_CANBK_EX"
            if p.endswith('_EX'):
                bm_set(mem_dict, changed_keys, f"{sym_prefix}_EX", "1")
                migrated += 1
                continue

            # Anything else — store as-is with value "1"
            bm_set(mem_dict, changed_keys, p, "1")
            migrated += 1

        except Exception as e:
            print(f"[MIGRATE] Error on entry '{p}': {e}")
            skipped += 1
            continue

    print(f"[MIGRATE] T4 → BotMemory: {migrated} keys migrated, {skipped} skipped (stale/invalid)")

    # Clear T4 — set marker so migration never runs again
    try:
        log_sheet.update_acell("T4", "MIGRATED_v14")
        print("[MIGRATE] T4 cleared ✅ — BotMemory is now primary memory")
    except Exception as e:
        print(f"[MIGRATE] Could not clear T4: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# BOTMEMORY KEY ACCESSORS
# These replace the old T4 string helpers (_mem_get, get_tsl, set_tsl etc.)
# API is identical so the rest of the code just passes mem_dict instead of mem
# ══════════════════════════════════════════════════════════════════════════════

def get_tsl(mem_dict: dict, key: str) -> float:
    """
    TSL stored as integer × 100 (e.g. value "28905" = ₹289.05)
    Key stored as "NSE_CANBK_TSL"
    """
    val = bm_get(mem_dict, f"{key}_TSL")
    if val:
        try: return int(val) / 100.0
        except: pass
    return 0.0

def set_tsl(mem_dict: dict, changed_keys: set, key: str, price: float):
    bm_set(mem_dict, changed_keys, f"{key}_TSL", str(int(round(price * 100))))

def get_max_price(mem_dict: dict, key: str) -> float:
    val = bm_get(mem_dict, f"{key}_MAX")
    if val:
        try: return int(val) / 100.0
        except: pass
    return 0.0

def set_max_price(mem_dict: dict, changed_keys: set, key: str, price: float):
    cur_max = get_max_price(mem_dict, key)
    if price <= cur_max: return
    bm_set(mem_dict, changed_keys, f"{key}_MAX", str(int(round(price * 100))))

def get_atr_from_mem(mem_dict: dict, key: str) -> float:
    val = bm_get(mem_dict, f"{key}_ATR")
    if val:
        try: return int(val) / 100.0
        except: pass
    return 0.0

def save_atr_to_mem(mem_dict: dict, changed_keys: set, key: str, atr: float):
    bm_set(mem_dict, changed_keys, f"{key}_ATR", str(int(round(atr * 100))))

def get_last_price(mem_dict: dict, key: str) -> float:
    val = bm_get(mem_dict, f"{key}_LP")
    if val:
        try: return int(val) / 100.0
        except: pass
    return 0.0

def set_last_price(mem_dict: dict, changed_keys: set, key: str, price: float):
    bm_set(mem_dict, changed_keys, f"{key}_LP", str(int(round(price * 100))))

def get_exit_date(mem_dict: dict, key: str) -> str:
    return bm_get(mem_dict, f"{key}_EXDT")

def set_exit_date(mem_dict: dict, changed_keys: set, key: str, date_str: str):
    bm_set(mem_dict, changed_keys, f"{key}_EXDT", date_str)

def get_trade_mode(mem_dict: dict, key: str) -> str:
    val = bm_get(mem_dict, f"{key}_MODE")
    return val if val in ("VCP", "MOM", "STD") else "STD"

def get_tsl_params(mem_dict: dict, key: str) -> dict:
    mode = get_trade_mode(mem_dict, key)
    return TSL_PARAMS[mode]

def get_capital_from_mem(mem_dict: dict, key: str) -> int:
    cap_str = bm_get(mem_dict, f"{key}_CAP")
    if cap_str:
        try:
            cap = int(cap_str)
            if cap in (7000, 10000, 13000): return cap
        except:
            pass
    return CAPITAL_PER_TRADE

def save_capital_to_mem(mem_dict: dict, changed_keys: set,
                        key: str, capital: int):
    bm_set(mem_dict, changed_keys, f"{key}_CAP", str(capital))


# ══════════════════════════════════════════════════════════════════════════════
# TSL CALCULATION — UNCHANGED from v13.5
# (TSL_PARAMS STD values changed above — that is the only difference)
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
# MESSAGE BUILDERS — UNCHANGED from v13.5
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
    mode_tag = {"VCP": "🎯 VCP Breakout", "MOM": "🚀 Momentum",
                "STD": "📊 Swing"}.get(trade_mode, "📊 Swing")
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
# GOOGLE SHEETS — get_spreadsheet() added alongside get_sheets()
# ══════════════════════════════════════════════════════════════════════════════

def _authorize():
    """Shared authorization logic."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_JSON')), scope
    )
    return gspread.authorize(creds)

def get_spreadsheet():
    """Return the raw spreadsheet object (needed for BotMemory worksheet)."""
    import time
    delays     = [5, 15, 30, 60, 120]
    last_error = None
    for attempt, delay in enumerate(delays):
        try:
            return _authorize().open(SHEET_NAME)
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

def get_sheets():
    """Return (log_sheet, hist_sheet, nifty_sheet) — kept for compatibility."""
    ss = get_spreadsheet()
    return ss.worksheet("AlertLog"), ss.worksheet("History"), ss.worksheet("Nifty200")

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
        print(f"[REGIME] Nifty CMP ₹{cmp_nifty:.0f} vs 20DMA ₹{dma20:.0f} → "
              f"{'BULLISH' if bullish else 'BEARISH'}")
        return bullish
    except Exception as e:
        print(f"[REGIME] Error: {e} — defaulting to bullish")
        return True


# ══════════════════════════════════════════════════════════════════════════════
# SECTOR CONTEXT — UNCHANGED from v13.5 (updated to use mem_dict)
# ══════════════════════════════════════════════════════════════════════════════

def _read_atr_from_nifty200(nifty_sheet, sym: str) -> float:
    """Read ATR14 from Nifty200 col AC (0-based index 28). v13.5 FIX 2."""
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

def get_sector_context(all_data: list, mem_dict: dict) -> str:
    sector_counts = {}
    for r in all_data[1:16]:
        r = pad(list(r))
        if "WAITING" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper():
            continue
        sym = str(r[C_SYMBOL]).strip()
        if not sym:
            continue
        key = sym_key(sym)
        sec = bm_get(mem_dict, f"{key}_SEC") or "Mixed"
        sector_counts[sec] = sector_counts.get(sec, 0) + 1
    if not sector_counts:
        return ""
    parts = [f"{s} ({c})" for s, c in sorted(sector_counts.items(),
                                              key=lambda x: -x[1])]
    return f"🔄 <b>Active Sectors:</b> {', '.join(parts[:4])}"


# ══════════════════════════════════════════════════════════════════════════════
# MAIN TRADING CYCLE — v14 changes marked with # v14
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

    # ── v14 CHANGE 1: Open spreadsheet, load BotMemory ───────────────────────
    ss         = get_spreadsheet()
    log_sheet  = ss.worksheet("AlertLog")
    hist_sheet = ss.worksheet("History")
    nifty_sheet= ss.worksheet("Nifty200")

    mem_dict, bm_sheet, changed_keys = load_botmemory(ss)
    deleted_keys = set()

    # ── v14: First-run migration — if BotMemory empty and T4 has data ────────
    if len(mem_dict) == 0:
        print("[MIGRATE] BotMemory empty — checking T4 for migration...")
        migrate_t4_to_botmemory(log_sheet, bm_sheet, mem_dict, changed_keys)

    # ── v14 CHANGE 1: Cleanup stale keys ─────────────────────────────────────
    stale_keys = cleanup_botmemory(bm_sheet, mem_dict)
    deleted_keys.update(stale_keys)
    for k in stale_keys:
        mem_dict.pop(k, None)

    is_bullish = get_market_regime(nifty_sheet)

    # ── DEBUG: Good Morning window check ──────────────────────────────────────
    am_key = f"{today}_AM"
    print(f"[GM CHECK] time={now.strftime('%H:%M')} IST | "
          f"window={'YES' if (now.hour==8 and now.minute>=45) or (now.hour==9 and now.minute<=29) else 'NO'} | "
          f"AM_already_sent={bm_has(mem_dict, am_key)}")

    if str(log_sheet.acell("T2").value or "").strip().upper() != "YES":
        print("[SKIP] Automation OFF (T2 != YES)")
        save_botmemory(bm_sheet, mem_dict, changed_keys, deleted_keys)
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
    # 1. GOOD MORNING  08:45–09:29 IST
    # ─────────────────────────────────────────────────────────────────────────
    if ((now.hour == 8 and now.minute >= 45) or
            (now.hour == 9 and now.minute <= 29)) and not bm_has(mem_dict, am_key):

        waiting_count = sum(
            1 for r in [pad(list(x)) for x in all_data[1:16]]
            if "WAITING" in str(r[C_STATUS]).upper()
        )
        sector_line = get_sector_context(all_data, mem_dict)

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
                cap   = get_capital_from_mem(mem_dict, key)
                pl_rs = round((cp - ent) / ent * cap)
                to_tgt = ((tgt - cp) / cp * 100) if cp > 0 else 0
                to_sl  = ((cp - sl) / cp * 100)  if cp > 0 else 0
                em     = "🟢" if pnl >= 0 else "🔴"
                mode   = get_trade_mode(mem_dict, key)
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
            get_capital_from_mem(mem_dict, sym_key(r[C_SYMBOL]))
            for _, r in traded_rows if r[C_SYMBOL]
        )

        send_basic(build_gm_basic(today, len(lines), waiting_count,
                                  is_bullish, sector_line))
        full_gm = build_gm_advance(today, lines, deployed,
                                   waiting_count, sector_line)
        send_advance(full_gm)
        send_premium(full_gm)

        bm_set(mem_dict, changed_keys, am_key, "1")

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
        # v14 CHANGE 2: Block ALL new entries when market is bearish.
        # Step B (monitoring existing trades) always runs regardless.
        if not is_bullish:
            print("[REGIME] Bearish market — Step A (new entries) SKIPPED. "
                  "Existing trades continue to be monitored.")
        else:
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

                # ── v13.5 FIX 3: RR re-validation (UNCHANGED) ────────────────
                rr_raw = str(r[C_RR]).strip()
                if rr_raw:
                    try:
                        rr_val = to_f(rr_raw.split(':')[-1])
                    except Exception:
                        rr_val = 0.0
                    if rr_val > 0 and rr_val < MIN_RR:
                        print(f"[SKIP] {sym}: RR 1:{rr_val:.1f} below MIN_RR "
                              f"{MIN_RR} — stale pre-v13.3 candidate")
                        continue

                key       = sym_key(sym)
                sheet_row = i + 2

                last_cp = get_last_price(mem_dict, key)
                set_last_price(mem_dict, changed_keys, key, cp)
                if last_cp > 0 and abs(cp - last_cp) < 0.01:
                    print(f"[STALE] {sym}: price unchanged — skipping")
                    continue

                exit_date = get_exit_date(mem_dict, key)
                if exit_date:
                    # v14 CHANGE 3: cooldown raised from 5 → 15 trading days
                    days_since = trading_days_since(exit_date, now)
                    if days_since < COOLDOWN_DAYS:
                        print(f"[COOLDOWN] {sym}: {days_since} days since exit "
                              f"(need {COOLDOWN_DAYS})")
                        continue

                pos_size_check = round(CAPITAL_PER_TRADE / cp) if cp > 0 else 0
                if pos_size_check < 2:
                    print(f"[SKIP] {sym}: CMP ₹{cp:,.0f} too high")
                    continue

                capital    = get_capital_from_mem(mem_dict, key)
                trade_mode = get_trade_mode(mem_dict, key)
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

                # ── v13.5 FIX 2: Read ATR14 from Nifty200 (UNCHANGED) ────────
                atr_est = _read_atr_from_nifty200(nifty_sheet, sym)
                if atr_est <= 0:
                    _mult   = (2 if "Intraday" in ttype else
                               4 if "Positional" in ttype else 3)
                    atr_est = (target - cp) / _mult if target > cp else 0
                    print(f"[ATR] {sym}: Nifty200 lookup returned 0, "
                          f"fallback atr_est={atr_est:.2f}")
                else:
                    print(f"[ATR] {sym}: read ATR14={atr_est:.2f} from Nifty200")

                save_atr_to_mem(mem_dict, changed_keys, key, atr_est)
                set_tsl(mem_dict, changed_keys, key, init_sl)
                set_max_price(mem_dict, changed_keys, key, cp)

                # Clear old EX flag so the new trade can be monitored fresh
                ex_flag_key = f"{key}_EX"
                bm_delete(mem_dict, deleted_keys, ex_flag_key)

                updated_r                = list(r)
                updated_r[C_STATUS]      = "🟢 TRADED (PAPER)"
                updated_r[C_ENTRY_PRICE] = cp
                updated_r[C_ENTRY_TIME]  = etime
                updated_r[C_TRAIL_SL]    = init_sl
                traded_rows.append((sheet_row, updated_r))

                atr     = atr_est
                o_hint  = options_hint(sym, cp, atr, ttype)
                c_flag  = ce_candidate_flag(cp, atr, stage, is_bullish)

                entry_key = f"{key}_ENTRY"
                bm_set(mem_dict, changed_keys, entry_key, "1")

                pos_size  = round(capital / cp) if cp > 0 else 0
                risk_rs   = round(max(0, cp - init_sl) * pos_size)
                reward_rs = round(max(0, target - cp) * pos_size)

                entry_alerts_advance.append(
                    build_entry_advance(sym, cp, cp, init_sl, target, ttype,
                                        strat, stage, priority, pos_size,
                                        capital, risk_rs, reward_rs,
                                        rr_num, trade_mode, c_flag)
                )
                entry_alerts_premium.append(
                    build_entry_premium(sym, cp, cp, init_sl, target, ttype,
                                        strat, stage, priority, pos_size,
                                        capital, risk_rs, reward_rs,
                                        rr_num, o_hint, trade_mode, c_flag)
                )
                print(f"[ENTRY] {sym} @ ₹{cp} | ₹{capital:,} | {pos_size}sh | "
                      f"{ttype} | {trade_mode} | SL ₹{init_sl} | T ₹{target}")

        # ── Step B: Monitor active trades ─────────────────────────────────────
        # Runs regardless of market regime (UNCHANGED from v13.5)
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

            set_max_price(mem_dict, changed_keys, key, cp)
            pnl_pct  = (cp - ent) / ent * 100
            atr      = get_atr_from_mem(mem_dict, key)
            if atr <= 0:
                _mult = 4 if "Positional" in ttype else 2 if "Intraday" in ttype else 3
                atr   = (tgt - ent) / _mult if tgt > ent else ent * 0.02

            days_held  = calc_hold_days(etime, now)
            trade_mode = get_trade_mode(mem_dict, key)
            tsl_params = TSL_PARAMS[trade_mode]
            capital    = get_capital_from_mem(mem_dict, key)

            new_tsl = calc_new_tsl(cp, ent, init_sl, atr, ttype, tsl_params)
            mem_tsl = get_tsl(mem_dict, key)
            new_tsl = max(new_tsl, mem_tsl, cur_tsl)

            if new_tsl > cur_tsl:
                tsl_cell_updates.append((sheet_row, new_tsl))
                tsl_label = ('Breakeven' if abs(new_tsl - ent) < 0.5
                             else '+2% locked' if abs(new_tsl - ent * 1.02) < 0.5
                             else 'ATR trail')
                trail_msg = (
                    f"🔒 <b>{sym}</b> [{trade_mode}] | "
                    f"LTP ₹{cp:.2f} ({pnl_pct:+.2f}%)\n"
                    f"   Trail SL: ₹{cur_tsl:.2f} → "
                    f"<b>₹{new_tsl:.2f}</b> ({tsl_label})"
                )
                trail_alerts.append(trail_msg)
                set_tsl(mem_dict, changed_keys, key, new_tsl)
                print(f"[TSL] {sym} [{trade_mode}]: ₹{cur_tsl:.2f}→₹{new_tsl:.2f}")

                # ── v14 CHANGE 5: Clear _HOLD_WARN when TSL rises above entry ─
                # Once breakeven is locked the stock has recovered —
                # the HOLD_WARN flag is no longer relevant.
                if new_tsl >= ent:
                    hw_key = f"{key}_HOLD_WARN"
                    if bm_has(mem_dict, hw_key):
                        bm_delete(mem_dict, deleted_keys, hw_key)
                        print(f"[MEM] {sym}: HOLD_WARN cleared (TSL above entry)")

            entry_date_key = etime[:10].replace('-', '') if etime else "0"
            ex_flag    = f"{key}_EX_{entry_date_key}"
            tsl_hit    = (new_tsl > 0 and cp <= new_tsl)
            target_hit = (tgt > 0 and cp >= tgt)
            hard_loss  = pnl_pct < -HARD_LOSS_PCT

            # ── Hard loss exit ────────────────────────────────────────────────
            if hard_loss and not bm_has(mem_dict, ex_flag):
                pl_rupees = round((cp - ent) / ent * capital, 2)
                hold_str  = calc_hold_str(etime, now)
                max_price = get_max_price(mem_dict, key)

                exit_alerts_basic.append(
                    build_exit_basic(sym, pnl_pct, "HARD LOSS"))
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
                bm_set(mem_dict, changed_keys, ex_flag, "1")
                set_exit_date(mem_dict, changed_keys, key,
                              now.strftime('%Y-%m-%d'))
                # Clear HOLD_WARN on exit
                bm_delete(mem_dict, deleted_keys, f"{key}_HOLD_WARN")
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

            if (tsl_hit or target_hit) and not bm_has(mem_dict, ex_flag) \
                    and not skip_exit:
                exit_reason   = ("🎯 TARGET HIT"    if target_hit else
                                 "🔒 TRAILING SL"   if new_tsl > init_sl else
                                 "🚨 INITIAL SL HIT")
                result_sym    = "WIN ✅" if (target_hit or pnl_pct > 0) else "LOSS 🔴"
                hold_str      = calc_hold_str(etime, now)
                max_price     = get_max_price(mem_dict, key)
                pl_rupees     = round((cp - ent) / ent * capital, 2)
                o_note        = (options_hint(sym, ent, atr, ttype)
                                 .replace('\n\n📊 <b>OPTIONS ADVISORY</b>', '')
                                 .strip() if atr > 0 else "")

                exit_alerts_basic.append(
                    build_exit_basic(sym, pnl_pct, exit_reason))
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
                bm_set(mem_dict, changed_keys, ex_flag, "1")
                set_exit_date(mem_dict, changed_keys, key,
                              now.strftime('%Y-%m-%d'))
                # Clear HOLD_WARN on exit
                bm_delete(mem_dict, deleted_keys, f"{key}_HOLD_WARN")
                print(f"[EXIT] {sym} | {result_sym} | "
                      f"{pnl_pct:+.2f}% | ₹{pl_rupees:+.0f}")

            elif tsl_hit and skip_exit:
                print(f"[HOLD] {sym}: SL touched Day {days_held + 1} "
                      f"< {min_hold} min hold")
                hw_key = f"{key}_HOLD_WARN"
                if not bm_has(mem_dict, hw_key):
                    regime_note = ("🐂 Bullish — recovery possible"
                                   if is_bullish else "🐻 Bearish — watching closely")
                    hold_msg = (
                        f"⚠️ <b>MIN HOLD ACTIVE — {sym}</b>\n"
                        f"[{ttype}] [{trade_mode}] touched SL ₹{new_tsl:.2f} "
                        f"but only Day {days_held + 1} of {min_hold}.\n"
                        f"Holding until Day {min_hold} unless loss > "
                        f"{HARD_LOSS_PCT}%.\n"
                        f"Current P/L: {pnl_pct:+.2f}%\n{regime_note}"
                    )
                    send_advance(hold_msg); send_premium(hold_msg)
                    bm_set(mem_dict, changed_keys, hw_key, "1")

        # Batch TSL writes to sheet
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
            header    = (f"⚡ <b>EXIT REPORT — {now.strftime('%H:%M IST')}</b>\n"
                         f"━━━━━━━━━━━━━━━━━━━━\n\n")
            full_exit = header + "\n\n".join(exit_alerts_advance)
            send_advance(full_exit); send_premium(full_exit)

        if trail_alerts:
            tsl_msg = (
                f"🔒 <b>TRAIL SL UPDATE — {now.strftime('%H:%M IST')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                + "\n\n".join(trail_alerts)
            )
            send_advance(tsl_msg); send_premium(tsl_msg)

        for msg in entry_alerts_advance: send_advance(msg)
        for msg in entry_alerts_premium: send_premium(msg)

    # ─────────────────────────────────────────────────────────────────────────
    # 3. MID-DAY PULSE  12:28–12:38 IST — UNCHANGED from v13.5
    # ─────────────────────────────────────────────────────────────────────────
    noon_key = f"{today}_NOON"
    if now.hour == 12 and 28 <= now.minute <= 38 and not bm_has(mem_dict, noon_key):
        fresh     = log_sheet.get_all_values()
        live_rows = [
            pad(list(r)) for r in fresh[1:16]
            if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
            and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        ]
        wins = losses = 0
        lines_advance = []; lines_basic = []
        for r in live_rows:
            sym   = r[C_SYMBOL]; cp = to_f(r[C_LIVE_PRICE])
            ent   = to_f(r[C_ENTRY_PRICE])
            tsl   = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
            ttype = str(r[C_TRADE_TYPE])
            if not price_sanity(sym, cp, ent): continue
            pnl = (cp - ent) / ent * 100
            em  = "🟢" if pnl >= 0 else "🔴"
            key = sym_key(sym)
            mode_tag = {"VCP": "🎯", "MOM": "🚀", "STD": "📊"}.get(
                get_trade_mode(mem_dict, key), "📊")
            if pnl >= 0: wins += 1
            else: losses += 1
            lines_advance.append(
                f"{em} <b>{sym}</b> {mode_tag} [{ttype}]: "
                f"{pnl:+.2f}% | TSL ₹{tsl:.2f}")
            lines_basic.append(f"{em} <b>{sym}</b>: {pnl:+.2f}%")

        send_basic(
            f"☀️ <b>MID-DAY PULSE — {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"Open: {len(lines_basic)} | 🟢 {wins} | 🔴 {losses}\n\n"
            + ("\n".join(lines_basic) if lines_basic else "No open trades")
            + "\n\n🔔 <i>Full levels at ai360trading.in/membership</i>"
        )
        adv_noon = (
            f"☀️ <b>MID-DAY PULSE — {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Open: {len(lines_advance)} | 🟢 {wins} | 🔴 {losses}\n\n"
            + ("\n".join(lines_advance) if lines_advance else "📭 No open trades")
        )
        send_advance(adv_noon)
        send_premium(adv_noon)
        bm_set(mem_dict, changed_keys, noon_key, "1")

    # ─────────────────────────────────────────────────────────────────────────
    # 4. MARKET CLOSE SUMMARY  15:15–15:45 IST — UNCHANGED from v13.5
    # ─────────────────────────────────────────────────────────────────────────
    pm_key = f"{today}_PM"
    if now.hour == 15 and 15 <= now.minute <= 45 and not bm_has(mem_dict, pm_key):
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
            exit_lines_advance.append(
                f"  {em} <b>{r[0]}</b>: {r[5]} {pl_r} (held {days_}d)")
            exit_lines_basic.append(
                f"  {em} <b>{r[0]}</b>: "
                f"{'WIN' if 'WIN' in str(r[6]).upper() else 'LOSS'}")

        fresh3    = log_sheet.get_all_values()
        open_rows = [
            pad(list(r)) for r in fresh3[1:16]
            if "TRADED" in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
            and "EXITED" not in str(r[C_STATUS] if len(r) > C_STATUS else "").upper()
        ]
        open_lines = []
        for r in open_rows:
            sym = r[C_SYMBOL]; cp = to_f(r[C_LIVE_PRICE])
            ent = to_f(r[C_ENTRY_PRICE])
            tsl = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
            if not ent or ent <= 0: continue
            if cp > 0 and ent > 0:
                pnl = (cp - ent) / ent * 100
                em  = "🟢" if pnl >= 0 else "🔴"
                open_lines.append(
                    f"  {em} <b>{sym}</b>: {pnl:+.2f}% | TSL ₹{tsl:.2f}")
            else:
                open_lines.append(f"  ⏰ <b>{sym}</b>: TSL ₹{tsl:.2f}")

        basic_close = (
            f"🔔 <b>MARKET CLOSED — {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 Wins: {len(wins_today)} | 💀 Losses: {len(loss_today)} | "
            f"📂 Open: {len(open_rows)}\n"
        )
        if exit_lines_basic:
            basic_close += "\n" + "\n".join(exit_lines_basic)
        basic_close += ("\n\n🔔 <i>Full P/L details for subscribers\n"
                        "→ ai360trading.in/membership</i>")
        send_basic(basic_close)

        full_close = (
            f"🔔 <b>MARKET CLOSED — {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 Wins: {len(wins_today)} | 💀 Losses: {len(loss_today)} | "
            f"📂 Open: {len(open_rows)}\n"
            f"💰 Today's P/L: <b>₹{total_pl:+.0f}</b>\n"
        )
        if exit_lines_advance:
            full_close += ("\n📋 <b>Exited Today:</b>\n"
                           + "\n".join(exit_lines_advance))
        if open_lines:
            full_close += ("\n\n📌 <b>Holding Overnight:</b>\n"
                           + "\n".join(open_lines))
        full_close += "\n\n✅ <i>Overnight holds monitored via TSL</i>"
        send_advance(full_close); send_premium(full_close)
        bm_set(mem_dict, changed_keys, pm_key, "1")

    # ─────────────────────────────────────────────────────────────────────────
    # 5. SAVE BOTMEMORY — replaces T4 write
    # ─────────────────────────────────────────────────────────────────────────
    save_botmemory(bm_sheet, mem_dict, changed_keys, deleted_keys)
    print(f"[DONE] {now.strftime('%H:%M:%S')} IST | "
          f"BotMemory keys: {len(mem_dict)}")


# ══════════════════════════════════════════════════════════════════════════════
# WEEKLY SUMMARY — updated to use mem_dict, logic UNCHANGED from v13.5
# ══════════════════════════════════════════════════════════════════════════════

def run_weekly_summary():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    print("[WEEKLY] Fetching weekly + monthly summary...")

    ss         = get_spreadsheet()
    log_sheet  = ss.worksheet("AlertLog")
    hist_sheet = ss.worksheet("History")
    mem_dict, bm_sheet, changed_keys = load_botmemory(ss)
    deleted_keys = set()

    hist_data = hist_sheet.get_all_values()
    all_rows  = hist_data[1:]

    days_since_mon = now.weekday()
    mon        = (now - timedelta(days=days_since_mon)).strftime('%Y-%m-%d')
    week_rows  = [r for r in all_rows if len(r) >= 17
                  and r[3] >= mon and r[3] <= today]
    mon1       = now.strftime('%Y-%m-01')
    month_rows = [r for r in all_rows if len(r) >= 17
                  and r[3] >= mon1 and r[3] <= today]
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
        f"🔔 <i>Full ₹ P/L details for subscribers\n"
        f"→ ai360trading.in/membership</i>"
    )

    full_weekly = (
        f"📅 <b>WEEKLY REPORT — w/e {today}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"\n📆 <b>THIS WEEK</b>\n"
        f"   Trades: {wt} | ✅ {ww}W / ❌ {wl}L | Win: {wwr}%\n"
        f"   P/L: <b>₹{wpl:+,.0f}</b> | Avg/trade: ₹{wavg:+,.0f}\n"
    )
    if best:
        full_weekly += f"   🏆 Best:  <b>{best[0]}</b> = ₹{to_f(best[16]):+,.0f}\n"
    if worst and worst != best:
        full_weekly += f"   💀 Worst: <b>{worst[0]}</b> = ₹{to_f(worst[16]):+,.0f}\n"
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

    # Save weekly flag to BotMemory
    weekly_key = f"{today}_WEEKLY"
    bm_set(mem_dict, changed_keys, weekly_key, "1")
    save_botmemory(bm_sheet, mem_dict, changed_keys, deleted_keys)
    print(f"[WEEKLY] Sent | W:{wt} M:{mt} All:{at} trades")


# ══════════════════════════════════════════════════════════════════════════════
# DAILY SUMMARY — updated to use mem_dict, logic UNCHANGED from v13.5
# ══════════════════════════════════════════════════════════════════════════════

def run_daily_summary():
    now   = datetime.now(IST)
    today = now.strftime('%Y-%m-%d')
    print("[SUMMARY] Fetching portfolio summary...")

    ss         = get_spreadsheet()
    log_sheet  = ss.worksheet("AlertLog")
    hist_sheet = ss.worksheet("History")
    mem_dict, bm_sheet, changed_keys = load_botmemory(ss)
    deleted_keys = set()

    print(f"[MEM] BotMemory keys: {len(mem_dict)}")
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
        sym   = r[C_SYMBOL]; cp = to_f(r[C_LIVE_PRICE])
        ent   = to_f(r[C_ENTRY_PRICE])
        tsl   = to_f(r[C_TRAIL_SL]) or to_f(r[C_INITIAL_SL])
        tgt   = to_f(r[C_TARGET]); ttype = str(r[C_TRADE_TYPE])
        etime = str(r[C_ENTRY_TIME])
        if not price_sanity(sym, cp, ent): continue
        pnl   = (cp - ent) / ent * 100
        key   = sym_key(sym)
        cap   = get_capital_from_mem(mem_dict, key)
        pl_rs = round((cp - ent) / ent * cap)
        days  = calc_hold_days(etime, now)
        em    = "🟢" if pnl >= 0 else "🔴"
        mode  = get_trade_mode(mem_dict, key)
        trade_lines.append(
            f"{em} <b>{sym}</b> [{ttype}] [{mode}]\n"
            f"   Entry ₹{ent:.2f} → Now ₹{cp:.2f} | "
            f"<b>{pnl:+.2f}%</b> = ₹{pl_rs:+,}\n"
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
        mode = get_trade_mode(mem_dict, key)
        cap  = get_capital_from_mem(mem_dict, key)
        wait_lines.append(
            f"  ⏳ <b>{r[C_SYMBOL]}</b> [{r[C_TRADE_TYPE]}] [{mode}] "
            f"₹{cap:,} | P:{r[C_PRIORITY]}"
        )

    msg = (
        f"📊 <b>PORTFOLIO SUMMARY</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 {now.strftime('%Y-%m-%d %H:%M')} IST\n"
        f"📈 Open: {len(open_rows)}/{MAX_TRADES} | "
        f"⏳ Waiting: {len(waiting_rows)}/{MAX_WAITING}\n"
        f"💰 Deployed: ₹{sum(get_capital_from_mem(mem_dict, sym_key(r[C_SYMBOL])) for r in open_rows):,}\n"
    )
    if trade_lines:
        msg += f"\n<b>── OPEN TRADES ──</b>\n" + "\n\n".join(trade_lines)
    else:
        msg += "\n📭 No open trades"
    if exit_lines:
        msg += (f"\n\n<b>── TODAY'S EXITS ──</b>\n" + "\n".join(exit_lines)
                + f"\n   <b>Today P/L: ₹{total_exit_pl:+,.0f}</b>")
    if wait_lines:
        msg += f"\n\n<b>── TOP WAITING ──</b>\n" + "\n".join(wait_lines)
    msg += "\n\n<i>On-demand summary</i>"

    send_advance(msg); send_premium(msg)
    print(f"[SUMMARY] Sent | Open={len(open_rows)} | Waiting={len(waiting_rows)}")


# ══════════════════════════════════════════════════════════════════════════════
# TEST TELEGRAM — version bumped to v14
# ══════════════════════════════════════════════════════════════════════════════

def run_test_telegram():
    now = datetime.now(IST)
    print("[TEST] Sending Telegram test messages to all 3 channels...")
    test_msg = (
        f"✅ <b>TELEGRAM TEST — OK</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 Bot: AI360 Trading v14\n"
        f"🕐 Time: {now.strftime('%Y-%m-%d %H:%M:%S')} IST\n"
        f"🔑 Token: Connected ✅\n💬 Chat: Connected ✅\n\n"
    )
    ok1 = _send_one(CHAT_BASIC,   test_msg + "📢 Channel: <b>ai360trading (Free)</b>")
    ok2 = _send_one(CHAT_ADVANCE, test_msg + "💎 Channel: <b>ai360trading_Advance</b>")
    ok3 = _send_one(CHAT_PREMIUM, test_msg + "👑 Channel: <b>ai360trading_Premium</b>")
    print(f"[TEST] BASIC={'✅' if ok1 else '❌'} | "
          f"ADVANCE={'✅' if ok2 else '❌'} | "
          f"PREMIUM={'✅' if ok3 else '❌'}")


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT — UNCHANGED from v13.5
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    mode = os.environ.get("BOT_MODE", "trade").strip().lower()
    print(f"[MODE] {mode}")
    if mode == "test_telegram":       run_test_telegram()
    elif mode == "daily_summary":     run_daily_summary()
    elif mode == "weekly_summary":    run_weekly_summary()
    else:                             run_trading_cycle()
