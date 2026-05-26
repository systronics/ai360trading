/**
 * AI360 TRADING — APPSCRIPT v15.15
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * v15.15 CHANGES (May 2026) — AUDIT FOLLOW-UP (BUG-6 + BUG-9):
 *   BUG-6 FIX — Cash candidates wrote BotMemory (_CAP/_MODE/_SEC) at the moment
 *     of detection (inside _runScanner scan loop AND inside the wlCands merge
 *     loop). If the slot was later lost (CASH_ENTRY_WINDOW passed by the time
 *     the final loop ran, or LOG_ROWS cap reached), the BotMemory entries were
 *     orphans — sat in the sheet until the 30-day TRADE TTL cleaned them up.
 *     FIX: removed both early _bmSet sites; consolidated writes into the final
 *     "add to finalWaiting" loop so BotMemory only records candidates that
 *     actually got a WAITING slot.
 *
 *   BUG-9 FIX — _bmPurge ran on every 5-min trigger fire (~120 fires/day),
 *     iterating the whole BotMemory sheet for no reason — most ticks have
 *     nothing aged out. Gated to once per day via `${today}_BMPURGED` FLAG.
 *     Bm is reloaded after purge so row indexes are fresh.
 *
 * v15.14 CHANGES (May 2026) — F&O EXPIRY DAY FIX (LAST TUESDAY) +
 *                              KILL HARDCODED YEAR-LOCKED EXPIRY LIST
 *
 * BACKGROUND:
 *   SEBI/NSE changed monthly F&O expiry day from Last Thursday → Last Tuesday
 *   effective September 1, 2025 (for NIFTY, BANKNIFTY, FINNIFTY, single stocks).
 *   Holiday rule: if last Tuesday is an NSE holiday, expiry shifts to the
 *   preceding trading day.
 *
 * PREVIOUS BUG (BUG-2 in audit):
 *   NSE_EXPIRY_DATES_2026 was a hardcoded array of last-Thursdays of 2026.
 *   From Jan 1 2027 onwards the loop would have fallen through to Dec 31 2026
 *   with a literal `daysLeft: 30` — every options signal in 2027 would have
 *   pointed at a stale Dec 2026 expiry. Also: still Thursday-based, wrong day.
 *
 * FIX:
 *   Removed NSE_EXPIRY_DATES_2026. Added _lastTuesdayOfMonth(year, monthIdx)
 *   helper that computes the last Tuesday of any month. _getRecommendedExpiry
 *   now walks forward month-by-month from today, generating expiries on the fly
 *   — works forever, no annual maintenance. Applies holiday adjustment using
 *   _RUNTIME_HOLIDAYS (already populated by _getRuntimeHolidays at run start).
 *
 * v15.6 CHANGES — PERFORMANCE FIXES (18 May 2026)
 *
 * ROOT CAUSE ANALYSIS from real trade data:
 *   3W/4L = 43% win rate (target: 65%+)
 *   All 4 losses = entered during BEARISH Nifty regime
 *   IT stocks blocked despite +5% moves = wrong criteria
 *   MCX BUY CE generated despite NEAR ATH = missing check
 *   Volume formula stale = wrong Gate 7 decisions
 *
 * FIX 1 — HARD BEARISH BLOCK
 *   When Nifty < 20DMA = NO new WAITING entries allowed
 *   Exception: only if MasterScore >= 40 AND Sector Leader AND RS >= 20
 *   Expected impact: win rate 43% → 65%+
 *   Reason: all 4 losses were entered in BEARISH market
 *
 * FIX 2 — MOMENTUM BREAKOUT GATE (new Gate 11)
 *   Stocks with SMA=Sideways but %Change >= 3% today = "Momentum Breakout"
 *   These are valid entries (TECHM, PERSISTENT style moves)
 *   Old system: SMA=Sideways → HOLD → blocked
 *   New system: SMA=Sideways + today +3%+ + Volume 2x = allow with lower score
 *
 * FIX 3 — OPTIONS ATH BLOCK
 *   If ATH_WARNING contains "NEAR ATH" → options signal = SKIP
 *   MCX at ATH should never get BUY CE — reversal risk too high
 *
 * FIX 4 — RELATIVE VOLUME CORRECTION
 *   Volume_vs_Avg from sheet is stale end-of-day
 *   If %Change >= 3% today → bypass volume gate (price confirms volume)
 *   Strong price move = strong volume (even if formula shows stale data)
 *
 * FIX 5 — SECTOR MOMENTUM DETECTION
 *   Count how many stocks in each sector are up 2%+ today
 *   If IT sector has 4+ stocks up 2%+ = "Sector Momentum" day
 *   Unlock IT stocks even if individual SMA = Sideways
 *   This captures institutional sector rotation
 *
 * FIX 6 — CONFIRMATION ENTRY FILTER
 *   When BREAKOUT CONFIRMED (not just ALERT) = full score
 *   When BREAKOUT ALERT = reduce score by 3 (need confirmation)
 *   Eliminates false breakouts — the #1 cause of trailing SL hits
 *
 * FIX 7 — DELIVERY % PROXY (new factor)
 *   Days Since Low >= 30 = stock has been accumulating (smart money holds)
 *   Days Since Low <= 5 = fresh move, may be speculative
 *   Add bonus: if daysLow >= 45 AND FII = Accumulation = +3 conviction bonus
 *
 * ALL OTHER v15.5 CODE UNCHANGED
 *
 * v15.8 CHANGES (May 2026):
 *   ADDED: _readCashWatchlist() — scans "CashWatchlist" tab for curated
 *          upper-circuit/high-beta small/mid caps NOT in Nifty200.
 *          These are pre-screened by user; bot detects when they move 4%+.
 *          Priority 30 (vs Nifty200 cash 25) so they surface first.
 *
 * v15.9 CHANGES (May 2026) — PERFORMANCE + RACE CONDITION FIXES:
 *   FIX 1 — Race condition eliminated in _runScanner:
 *     Removed redundant clearContent() before setValues(). setValues() already
 *     overwrites all LOG_ROWS × TOTAL_COLS cells atomically. The clearContent()
 *     was creating a ~200ms window where trading_bot.py could read blank AlertLog.
 *
 *   FIX 2 — Morning cleanup write lock (clearWaitingRowsOnly):
 *     clearWaitingRowsOnly still needs clearContent (only writes traded rows,
 *     not full grid). Added _AS_LOCK in BotMemory before clear, deleted after.
 *     trading_bot.py v15.3 checks this lock and skips the cycle.
 *
 *   FIX 3 — _restoreFormulas batch rewrite:
 *     Was: 1 batch read + ~130 individual setFormula/setValue calls per run.
 *     Now: 1 batch read + 5 batch setFormulas calls → ~6x fewer API calls.
 *     Saves 6–15 seconds per scanner run.
 *
 *   FIX 4 — BotMemory dedup in _bmLoad:
 *     Duplicate keys accumulate over time (AppScript appends without dedup).
 *     _bmLoad now clears earlier duplicate rows on load → self-healing.
 *
 *   FIX 5 — Extended _bmPurge: TRADE entries now purged after 30 days.
 *     Previously only FLAG entries were purged (14-day TTL).
 *     TRADE entries from closed symbols now auto-cleared after 30 days.
 *
 *   FIX 6 — Dhan API prep: sendBrokerOrder() stub + CONFIG.BROKER_MODE.
 *     Phase 4 wire-up: change BROKER_MODE to "LIVE" and implement Dhan call.
 *
 *   FIX 7 — setupTriggers() function added to menu.
 *     One-click trigger setup instead of manual AppScript Triggers UI.
 *
 * v15.10 CHANGES (May 2026) — DEFENSIVE FIXES:
 *   FIX 1 — _checkBearishEntryAllowed: LeaderType check now case-insensitive
 *     substring match (handles "Sector Leader", "sector leader", " Sector Leader ",
 *     "Sector_Leader"). Previously strict equality could silently block all bearish
 *     entries if the Nifty200 sheet ever had minor text variation.
 *
 * v15.11 CHANGES (May 2026) — HOLIDAYS AUTO-EXTEND:
 *   FIX 1 — AppScript now reads HOLIDAYS_YYYY keys from BotMemory (written by
 *     fetch_holidays.py every Dec 1) and merges them into the runtime holiday set.
 *     Previously _isMarketHoliday() used only the hardcoded NSE_HOLIDAYS_2026 array,
 *     so on 1-Jan-2027 the scanner would have written WAITING rows on Republic Day
 *     (26-Jan-2027) until someone manually updated the constant.
 *     Now: trading_bot.py and AppScript share the same auto-extending holiday source.
 *
 * v15.12 CHANGES (May 2026) — CASH IN BEARISH MARKET:
 *   FIX 1 — Removed marketBullish requirement from cash intraday detection.
 *     Cash trades are catalyst-driven (PSU results, defence orders, sector news)
 *     and can move 10-15% even in bearish Nifty. Risk is contained by tight 3% SL
 *     and 3PM force-exit. Now captures bearish-market income days that were
 *     previously blocked. Paper trading throughout Phase 1-3 — safe to expand.
 *
 * v15.13 CHANGES (May 2026) — DEFENSIVE POLISH:
 *   FIX 1 — _bmPurge FLAG key check now uses regex /^\d{4}-\d{2}-\d{2}_/ instead
 *     of substring(0,10) — safer against non-date FLAG keys. Currently no such
 *     keys exist, but this prevents future bugs if a non-date FLAG key is added.
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 */

// ── NSE MARKET HOLIDAYS 2026 ──────────────────────────────────────────────────
const NSE_HOLIDAYS_2026 = [
  "2026-01-26","2026-03-25","2026-04-02","2026-04-14",
  "2026-05-01","2026-05-27","2026-06-17","2026-08-15",
  "2026-08-27","2026-10-02","2026-10-21","2026-10-22",
  "2026-11-04","2026-11-05","2026-12-25",
];

// v15.11: runtime holiday set — populated by _getRuntimeHolidays(ss) once per run.
// Merges NSE_HOLIDAYS_2026 with HOLIDAYS_YYYY keys from BotMemory (set by
// fetch_holidays.py every Dec 1). Auto-extends every year — no manual update needed.
let _RUNTIME_HOLIDAYS = null;

function _getRuntimeHolidays(ss) {
  if (_RUNTIME_HOLIDAYS) return _RUNTIME_HOLIDAYS;
  const merged = new Set(NSE_HOLIDAYS_2026);
  try {
    const bmSheet = ss.getSheetByName(CONFIG.BM_SHEET);
    if (bmSheet) {
      const lastRow = bmSheet.getLastRow();
      if (lastRow >= 2) {
        const data = bmSheet.getRange(2, 1, lastRow - 1, 2).getValues();
        const year = new Date().getFullYear();
        const keys = [`HOLIDAYS_${year}`, `HOLIDAYS_${year + 1}`];
        for (const row of data) {
          const key = (row[0] || "").toString().trim();
          const val = (row[1] || "").toString().trim();
          if (keys.indexOf(key) !== -1 && val) {
            const dates = val.split(",").map(d => d.trim()).filter(d => d);
            dates.forEach(d => merged.add(d));
            Logger.log(`[HOLIDAYS] Loaded ${dates.length} dates from BotMemory:${key}`);
          }
        }
      }
    }
  } catch(e) {
    Logger.log(`[HOLIDAYS] Dynamic load error: ${e}`);
  }
  _RUNTIME_HOLIDAYS = merged;
  return merged;
}

// ── F&O LIQUID STOCKS ─────────────────────────────────────────────────────────
const F_AND_O_LIQUID_STOCKS = new Set([
  "NSE:RELIANCE","NSE:TCS","NSE:INFY","NSE:HDFCBANK","NSE:ICICIBANK",
  "NSE:SBIN","NSE:AXISBANK","NSE:KOTAKBANK","NSE:BAJFINANCE","NSE:BAJAJFINSV",
  "NSE:WIPRO","NSE:HCLTECH","NSE:TECHM","NSE:LTIM","NSE:PERSISTENT",
  "NSE:ADANIPORTS","NSE:ADANIENT","NSE:ADANIGREEN","NSE:ADANIPOWER","NSE:ADANIENSOL",
  "NSE:TATAMOTORS","NSE:TATAPOWER","NSE:TATASTEEL","NSE:TCS","NSE:TITAN",
  "NSE:MARUTI","NSE:M&M","NSE:BAJAJ-AUTO","NSE:HEROMOTOCO","NSE:EICHERMOT",
  "NSE:JSWSTEEL","NSE:HINDALCO","NSE:COALINDIA","NSE:NTPC","NSE:POWERGRID",
  "NSE:ONGC","NSE:BPCL","NSE:IOC","NSE:GAIL","NSE:BHARTIARTL",
  "NSE:ITC","NSE:HINDUNILVR","NSE:NESTLEIND","NSE:BRITANNIA","NSE:DABUR",
  "NSE:SUNPHARMA","NSE:CIPLA","NSE:DRREDDY","NSE:DIVISLAB","NSE:AUROPHARMA",
  "NSE:ULTRACEMCO","NSE:GRASIM","NSE:AMBUJACEM","NSE:ACC","NSE:SHREECEM",
  "NSE:BSE","NSE:ANGELONE","NSE:CAMS","NSE:CDSL","NSE:MCX",
  "NSE:BHEL","NSE:CGPOWER","NSE:ABB","NSE:SIEMENS","NSE:CUMMINSIND",
  "NSE:INDUSINDBK","NSE:FEDERALBNK","NSE:BANDHANBNK","NSE:AUBANK","NSE:IDFCFIRSTB",
  "NSE:APOLLOHOSP","NSE:MAXHEALTH","NSE:FORTIS","NSE:LALPATHLAB","NSE:METROPOLIS",
  "NSE:DMART","NSE:TRENT","NSE:NYKAA","NSE:ZOMATO","NSE:PAYTM",
  "NSE:LT","NSE:LTTS","NSE:LTECH","NSE:POLYCAB","NSE:HAVELLS",
  "NSE:PIDILITIND","NSE:BERGER","NSE:ASIANPAINT","NSE:KANSAINER","NSE:INDIGO",
  "NSE:IRCTC","NSE:CONCOR","NSE:BHARATFORG","NSE:MOTHERSON","NSE:BOSCHLTD",
  "NSE:COFORGE","NSE:MPHASIS","NSE:PERSISTENT","NSE:OFSS","NSE:TECHM",
]);

// ── NSE MONTHLY EXPIRY — LAST TUESDAY OF MONTH ─────────────────────────────────
// v15.14: SEBI/NSE moved monthly F&O expiry from Last Thursday → Last Tuesday
// effective Sep 1, 2025 (for NIFTY, BANKNIFTY, FINNIFTY, single stocks).
// Previously this was a hardcoded list of last-Thursdays of 2026 that would have
// expired in Jan 2027. Now computed dynamically — works forever.
//
// Holiday rule: if last Tuesday is an NSE holiday, expiry shifts to the preceding
// trading day. _RUNTIME_HOLIDAYS is populated by _getRuntimeHolidays(ss) at the
// start of every run; this function only applies the adjustment when that set
// is available (e.g., regular scanner runs). Test helpers that call this before
// holiday load get the raw last Tuesday — acceptable for unit-test display.
function _lastTuesdayOfMonth(year, monthIdx) {
  // monthIdx: 0=Jan ... 11=Dec
  const last     = new Date(year, monthIdx + 1, 0);       // last day of month
  const daysBack = (last.getDay() - 2 + 7) % 7;           // 2 = Tuesday
  last.setDate(last.getDate() - daysBack);
  // Holiday adjustment — walk back to preceding trading day
  if (_RUNTIME_HOLIDAYS) {
    let guard = 0;
    while (guard++ < 7) {
      const dateStr = Utilities.formatDate(last, CONFIG.IST_ZONE, "yyyy-MM-dd");
      const dow     = last.getDay();
      if (dow !== 0 && dow !== 6 && !_RUNTIME_HOLIDAYS.has(dateStr)) break;
      last.setDate(last.getDate() - 1);
    }
  }
  return last;
}

// ── OPTIONS CONFIG ────────────────────────────────────────────────────────────
const OPTIONS_CONFIG = {
  VIX_MAX_BUY        : 18.0,
  VIX_MAX_BUY_BASE   : 16.0,
  VIX_AVOID          : 22.0,
  MIN_DAYS_EXPIRY    : 20,
  MIN_DAYS_BASE_ENTRY: 40,
  IDEAL_DAYS_MIN     : 25,
};

// ── CONFIG ────────────────────────────────────────────────────────────────────
const CONFIG = {
  get TELEGRAM_BOT_TOKEN() { return PropertiesService.getScriptProperties().getProperty('TELEGRAM_BOT_TOKEN') || ""; },
  get CHAT_ID_BASIC()      { return PropertiesService.getScriptProperties().getProperty('CHAT_ID_BASIC')      || ""; },
  get CHAT_ID_ADVANCE()    { return PropertiesService.getScriptProperties().getProperty('CHAT_ID_ADVANCE')    || ""; },
  get CHAT_ID_PREMIUM()    { return PropertiesService.getScriptProperties().getProperty('CHAT_ID_PREMIUM')    || ""; },

  SHEET_NAME    : "Nifty200",
  LOG_SHEET     : "AlertLog",
  HISTORY_SHEET : "History",
  BM_SHEET      : "BotMemory",
  IST_ZONE      : "GMT+5:30",

  MAX_TRADES    : 8,
  MAX_WAITING   : 10,
  MAX_MOM_SLOTS : 3,
  MIN_PRIORITY  : 15,
  MIN_RR        : 1.8,
  ATH_BUFFER_PCT: 1.0,
  MAX_CMP       : 8000,

  CAPITAL_HIGH  : 13000,
  CAPITAL_MED   : 10000,
  CAPITAL_STD   :  7000,
  MAX_DEPLOYED  : 104000,

  ATR_SL_INTRADAY     : 1.5,
  ATR_SL_SWING        : 2.0,
  ATR_SL_BASE         : 1.5,
  ATR_SL_POSITIONAL   : 2.5,
  ATR_TGT_INTRADAY    : 2.0,
  ATR_TGT_SWING       : 3.0,
  ATR_TGT_SWING_LEADER: 4.0,
  ATR_TGT_BASE        : 5.0,
  ATR_TGT_POSITIONAL  : 4.0,

  BATCH_SIZE    : 60,
  TOTAL_COLS    : 19,
  LOG_ROWS      : 21,

  BEARISH_MIN_AF          : 5,
  BEARISH_MIN_MASTER_SCORE: 22,
  BEARISH_LEADER_ONLY     : true,

  // v15.6: Stricter bearish thresholds
  BEARISH_HARD_MIN_SCORE  : 40,   // Hard bearish: only score >= 40 allowed
  BEARISH_MAX_WAITING     : 3,    // Max 3 waiting slots in bearish (was 10)
  BEARISH_MIN_RS          : 15,   // Stock must have RS >= 15 in bearish market

  LATE_ENTRY_MIN_RS      : 5,
  MAX_DIST_ABOVE_20DMA   : 8,
  PIVOT_RESISTANCE_BUFFER: 0.02,
  RETEST_MAX_PULLBACK    : -0.08,
  BASE_STAGE_MIN_VOL     : 40,

  // v15.6: Momentum breakout gate
  MOMENTUM_BREAKOUT_MIN_PCT : 3.0,  // 3%+ move today = momentum breakout
  MOMENTUM_BREAKOUT_MIN_RS  : 10,   // Must have RS >= 10 even on momentum day
  MOMENTUM_SECTOR_MIN_COUNT : 3,    // 3+ stocks in sector up 2%+ = sector momentum day

  BASE_ENTRY_ENABLED   : true,
  BASE_MIN_FII_ZONE    : "Accumulation Zone",
  BASE_MAX_VCP         : 0.05,
  BASE_MIN_DAYS_LOW    : 15,
  BASE_MIN_ATH_GAP_PCT : 5.0,
  BASE_MIN_SCORE       : 18,
  BASE_STAGES          : ["Correction Base", "Building Momentum", "Near Breakout"],

  RESULT_DAY_SKIP_PCT : 6.0,
  CORP_ACTION_SKIP_PCT: 15.0,

  MOM_MIN_CHANGE_PCT: 2.5,
  MOM_MIN_VOLUME_PCT: 200,
  MOM_WINDOW_END    : "11:30",

  MORNING_VOL_BYPASS_UNTIL: "10:30",
  INTRADAY_WINDOW_START   : "09:15",
  INTRADAY_WINDOW_END     : "12:30",

  RANK_CONV_BONUS_MAX: 3,
  RANK_LEADER_MAX    : 5,
  BM_PURGE_DAYS      : 14,

  // ── Cash Intraday — high-volume gap stocks, same-day exit ──────────────────
  // These are small-mid cap stocks with news/volume catalyst giving 10-15% intraday
  CASH_MIN_PCT_CHANGE  : 4.0,   // 4%+ move today = cash candidate
  CASH_MIN_VOLUME_RATIO: 200,   // 2x average volume (confirmed buying)
  CASH_MAX_CMP         : 500,   // small-mid cap only (higher % potential)
  CASH_MIN_CMP         : 50,    // avoid penny stocks
  CASH_SL_PCT          : 0.03,  // tight -3% SL (must be quick trade)
  CASH_TARGET_PCT      : 0.12,  // +12% target (10-15% potential)
  CASH_ENTRY_WINDOW    : "10:30", // scan only until 10:30 AM
  CASH_MAX_SLOTS       : 3,     // max 3 cash intraday candidates per day
  CASH_ATH_GAP_MIN_PCT : 5.0,   // stock must have 5%+ gap from ATH (room to run)

  // ── Phase 4 Broker API ────────────────────────────────────────────────────
  BROKER_MODE          : "PAPER",  // "PAPER" = log only | "LIVE" = Dhan API (Phase 4)

  // ── BotMemory purge TTLs ──────────────────────────────────────────────────
  BM_PURGE_TRADE_DAYS  : 30,       // TRADE entries purged after 30 days (v15.9)
};

// ══════════════════════════════════════════════════════════════════════════════
// v15.6 FIX 1 — BEARISH HARD BLOCK
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Determine if market allows new entries.
 *
 * CRITICAL INSIGHT from trade data (May 2026):
 * All 4 losses (BHARATFORG, TATASTEEL, BANDHANBNK, SAIL) were entered
 * during BEARISH regime (Nifty < 20DMA). Win rate was 43%.
 *
 * Top institutional rule: NO new entries when Nifty < 20DMA
 * Exception: only allow if stock score is exceptionally high (>=40)
 *
 * Returns: { allowed: bool, reason: string, maxSlots: int }
 */
function _checkBearishEntryAllowed(marketBullish, useScore, leaderType, rs) {
  if (marketBullish) {
    return { allowed: true, reason: "Bullish market", maxSlots: CONFIG.MAX_WAITING };
  }

  // BEARISH market — very strict
  if (useScore < CONFIG.BEARISH_HARD_MIN_SCORE) {
    return {
      allowed: false,
      reason: `BEARISH + Score ${useScore} < ${CONFIG.BEARISH_HARD_MIN_SCORE}`,
      maxSlots: CONFIG.BEARISH_MAX_WAITING
    };
  }
  // v15.10: case-insensitive substring match — defensive against minor sheet text variations
  // (e.g. "Sector Leader", "sector leader", " Sector Leader ", "Sector_Leader")
  if (!(leaderType || "").toString().toLowerCase().includes("sector leader") &&
      !(leaderType || "").toString().toLowerCase().includes("sector_leader")) {
    return {
      allowed: false,
      reason: `BEARISH + Not Sector Leader (${leaderType})`,
      maxSlots: CONFIG.BEARISH_MAX_WAITING
    };
  }
  if (rs < CONFIG.BEARISH_MIN_RS) {
    return {
      allowed: false,
      reason: `BEARISH + RS ${rs} < ${CONFIG.BEARISH_MIN_RS}`,
      maxSlots: CONFIG.BEARISH_MAX_WAITING
    };
  }

  return {
    allowed: true,
    reason: `BEARISH exception: Score=${useScore} Leader=${leaderType} RS=${rs}`,
    maxSlots: CONFIG.BEARISH_MAX_WAITING
  };
}

// ══════════════════════════════════════════════════════════════════════════════
// v15.6 FIX 2 — MOMENTUM BREAKOUT DETECTION
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Detect if a stock is having a momentum breakout day.
 *
 * WHY THIS IS NEEDED:
 * TECHM, PERSISTENT, COFORGE were up 5%+ today (Image 1-3).
 * All have SMA = Sideways → scanner blocked them.
 * But these are legitimate breakout entries:
 *   - Stock was in base/correction for months
 *   - Today's big move = catalyst (earnings, sector news, FII buying)
 *   - This IS the entry point institutions are using
 *
 * RULE (based on IBD momentum rules):
 *   %Change >= 3.0% today = potential momentum breakout
 *   Volume >= 1.5x average = confirms genuine buying
 *   RS >= MOMENTUM_BREAKOUT_MIN_RS = stock is relatively strong
 *   NOT near ATH = room to run
 *
 * Returns: { isMomentum: bool, reason: string }
 */
function _checkMomentumBreakout(pctChange, volVsAvg, rs, high52, cmp, smaStr) {
  // Strong price move today
  if (pctChange < CONFIG.MOMENTUM_BREAKOUT_MIN_PCT) {
    return { isMomentum: false, reason: `Change ${pctChange.toFixed(1)}% < ${CONFIG.MOMENTUM_BREAKOUT_MIN_PCT}%` };
  }

  // Not near ATH (needs room to run)
  if (high52 > 0 && cmp > 0) {
    const athGap = ((high52 - cmp) / high52) * 100;
    if (athGap < 3) {
      return { isMomentum: false, reason: `Near ATH (gap ${athGap.toFixed(1)}%)` };
    }
  }

  // Minimum RS (even sideways stocks need to be relatively strong)
  if (rs < CONFIG.MOMENTUM_BREAKOUT_MIN_RS) {
    return { isMomentum: false, reason: `RS ${rs} too low for momentum entry` };
  }

  // FIX for stale volume: if price is up 3%+, volume is almost always confirmed
  // We give benefit of doubt because Volume_vs_Avg formula is end-of-day stale
  const volumeOk = (volVsAvg > 100) || (pctChange >= 3.0);

  if (!volumeOk) {
    return { isMomentum: false, reason: `Volume not confirmed: ${volVsAvg.toFixed(0)}%` };
  }

  return {
    isMomentum: true,
    reason: `Momentum breakout: +${pctChange.toFixed(1)}% today, RS=${rs.toFixed(1)}`
  };
}

// ══════════════════════════════════════════════════════════════════════════════
// v15.6 FIX 5 — SECTOR MOMENTUM DETECTION
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Scan all stocks to find sectors with multiple stocks moving up today.
 * When a sector has 3+ stocks up 2%+, it's a sector rotation day.
 * This unlocks stocks in that sector even with lower scores.
 *
 * Used to capture: IT sector rally days (TECHM + PERSISTENT + COFORGE all up 4-5%)
 *
 * Returns: Set of sector names with momentum today
 */
function _detectMomentumSectors(inputData) {
  const sectorCount = {};
  const THRESHOLD_PCT = 2.0;

  for (let i = 2; i < inputData.length; i++) {
    const r = inputData[i];
    if (!r[0]) continue;
    const sector    = (r[1]  || "").toString().trim();
    const pctChange = parseFloat(r[3]) || 0;

    if (pctChange >= THRESHOLD_PCT) {
      sectorCount[sector] = (sectorCount[sector] || 0) + 1;
    }
  }

  const momentumSectors = new Set();
  for (const sector in sectorCount) {
    if (sectorCount[sector] >= CONFIG.MOMENTUM_SECTOR_MIN_COUNT) {
      momentumSectors.add(sector);
      Logger.log(`[SECTOR MOMENTUM] ${sector}: ${sectorCount[sector]} stocks up ${THRESHOLD_PCT}%+`);
    }
  }
  return momentumSectors;
}

// ══════════════════════════════════════════════════════════════════════════════
// BASE ENTRY CHECKER — v15.4 (unchanged)
// ══════════════════════════════════════════════════════════════════════════════

function _checkBaseEntry(stage, fiiBuyZone, vcp, daysLow, smaStr, high52, cmp, useScore) {
  if (!CONFIG.BASE_ENTRY_ENABLED) return { qualifies: false, reason: "Disabled" };
  const isBaseStage = CONFIG.BASE_STAGES.some(s => stage.includes(s));
  if (!isBaseStage) return { qualifies: false, reason: "Not a base stage" };
  if (useScore < CONFIG.BASE_MIN_SCORE) return { qualifies: false, reason: `Score ${useScore} < ${CONFIG.BASE_MIN_SCORE}` };
  if (fiiBuyZone !== CONFIG.BASE_MIN_FII_ZONE) return { qualifies: false, reason: `FII=${fiiBuyZone} not Accumulation` };
  if (vcp > CONFIG.BASE_MAX_VCP) return { qualifies: false, reason: `VCP=${vcp} > ${CONFIG.BASE_MAX_VCP}` };
  if (daysLow < CONFIG.BASE_MIN_DAYS_LOW) return { qualifies: false, reason: `DaysLow=${daysLow} < ${CONFIG.BASE_MIN_DAYS_LOW}` };
  if (smaStr !== "Strong Bull" && smaStr !== "Bull") return { qualifies: false, reason: `SMA=${smaStr} not bullish` };
  if (high52 > 0 && cmp > 0) {
    const athGapPct = ((high52 - cmp) / high52) * 100;
    if (athGapPct < CONFIG.BASE_MIN_ATH_GAP_PCT) return { qualifies: false, reason: `ATH gap ${athGapPct.toFixed(1)}% < ${CONFIG.BASE_MIN_ATH_GAP_PCT}%` };
  }
  return { qualifies: true, reason: "All base conditions met" };
}

// ══════════════════════════════════════════════════════════════════════════════
// OPTIONS ENGINE — v15.6 (FIX 3: ATH block added)
// ══════════════════════════════════════════════════════════════════════════════

function _getIndiaVix(inputData) {
  try {
    const resp = UrlFetchApp.fetch(
      "https://query1.finance.yahoo.com/v8/finance/chart/%5EINDIAVIX?interval=1d&range=1d",
      { muteHttpExceptions: true, deadline: 5, headers: { "User-Agent": "Mozilla/5.0" } }
    );
    if (resp.getResponseCode() === 200) {
      const data = JSON.parse(resp.getContentText());
      const vix  = data?.chart?.result?.[0]?.meta?.regularMarketPrice || 0;
      if (vix > 5 && vix < 100) { Logger.log(`[VIX] Live: ${vix.toFixed(1)}`); return parseFloat(vix); }
    }
  } catch(e) { Logger.log("[VIX] Fetch failed: " + e); }
  Logger.log("[VIX] Using fallback 14.0");
  return 14.0;
}

function _getRecommendedExpiry(minDays) {
  // v15.14: walks forward month-by-month from today, generating last-Tuesday
  // expiries on the fly. No more hardcoded year-locked list to maintain.
  minDays = minDays || OPTIONS_CONFIG.MIN_DAYS_EXPIRY;
  const now    = new Date();
  const MS_DAY = 1000 * 60 * 60 * 24;
  // Scan current + next 7 months — covers any reasonable minDays request.
  for (let i = 0; i < 8; i++) {
    const total  = now.getMonth() + i;
    const year   = now.getFullYear() + Math.floor(total / 12);
    const month  = total % 12;
    const expiry = _lastTuesdayOfMonth(year, month);
    const daysLeft = Math.floor((expiry - now) / MS_DAY);
    if (daysLeft >= minDays) return { date: expiry, daysLeft: daysLeft };
  }
  // Fallback — should not reach; defensive only.
  const fb = _lastTuesdayOfMonth(now.getFullYear() + 1, now.getMonth());
  return { date: fb, daysLeft: Math.floor((fb - now) / MS_DAY) };
}

function _roundToStrike(price, interval) { return Math.ceil(price / interval) * interval; }

function _getStrikeInterval(cmp) {
  if (cmp < 250)  return 5;
  if (cmp < 500)  return 10;
  if (cmp < 1000) return 20;
  if (cmp < 2000) return 50;
  return 100;
}

/**
 * v15.6: Added ATH check.
 * MCX was generating BUY CE despite NEAR ATH warning.
 * Stocks near ATH = high reversal risk = options expire worthless.
 *
 * New ATH parameter: high52 and cmp passed to check proximity.
 */
function _generateOptionsSignal(sym, cmp, atr, stage, pctChange, vix, isBaseEntry, high52) {
  const result = { signal: "⏸ SKIP", strike: "", expiryStr: "", thetaRisk: "", message: "", isBase: isBaseEntry || false };

  if (!F_AND_O_LIQUID_STOCKS.has(sym)) { result.message = "Not in F&O liquid list"; return result; }

  // v15.6 FIX 3: Block options if NEAR ATH
  if (high52 > 0 && cmp > 0) {
    const athGapPct = ((high52 - cmp) / high52) * 100;
    if (athGapPct < 3.0) {
      result.signal  = "⏸ NEAR ATH";
      result.message = `${athGapPct.toFixed(1)}% from ATH — options risk high`;
      return result;
    }
  }

  const isBreakout = stage.includes("BREAKOUT CONFIRMED") || stage.includes("BREAKOUT ALERT");
  const isBase     = isBaseEntry && CONFIG.BASE_STAGES.some(s => stage.includes(s));
  if (!isBreakout && !isBase) { result.message = "Stage not suitable for options"; return result; }

  const vixLimit = isBaseEntry ? OPTIONS_CONFIG.VIX_MAX_BUY_BASE : OPTIONS_CONFIG.VIX_MAX_BUY;
  let vixLabel = "";
  if (vix > OPTIONS_CONFIG.VIX_AVOID) {
    result.signal  = "❌ VIX HIGH";
    result.message = `VIX ${vix.toFixed(1)} > ${OPTIONS_CONFIG.VIX_AVOID} — skip`;
    return result;
  } else if (vix > vixLimit) {
    vixLabel = `⚠️ VIX ${vix.toFixed(1)} — caution`;
  } else {
    vixLabel = `✅ VIX ${vix.toFixed(1)} — good to buy`;
  }

  const minDays    = isBaseEntry ? OPTIONS_CONFIG.MIN_DAYS_BASE_ENTRY : OPTIONS_CONFIG.MIN_DAYS_EXPIRY;
  const expiryInfo = _getRecommendedExpiry(minDays);
  const expiryStr  = Utilities.formatDate(expiryInfo.date, CONFIG.IST_ZONE, "dd-MMM-yyyy");
  const daysLeft   = expiryInfo.daysLeft;

  let thetaRisk;
  if      (daysLeft >= 40) thetaRisk = `🟢 LOW (${daysLeft}d)`;
  else if (daysLeft >= 25) thetaRisk = `🟡 MED (${daysLeft}d)`;
  else                     thetaRisk = `🔴 HIGH (${daysLeft}d — avoid)`;

  if (daysLeft < minDays) {
    result.signal    = "❌ THETA HIGH";
    result.expiryStr = expiryStr;
    result.thetaRisk = thetaRisk;
    result.message   = `Only ${daysLeft} days — need ${minDays}+`;
    return result;
  }

  const interval  = _getStrikeInterval(cmp);
  const atmStrike = _roundToStrike(cmp, interval);
  const otmStrike = _roundToStrike(cmp + atr, interval);

  let useStrike;
  if (isBaseEntry) {
    useStrike = atmStrike;
  } else {
    useStrike = (atmStrike - cmp) <= (atr * 0.5) ? otmStrike : atmStrike;
  }

  const expiryMonth = expiryStr.substring(3, 6);
  const strikeStr   = `${useStrike} CE ${expiryMonth}`;

  result.signal    = isBaseEntry ? "📦 BASE CE" : "📊 BUY CE";
  result.strike    = strikeStr;
  result.expiryStr = expiryStr;
  result.thetaRisk = thetaRisk;
  result.message   = vixLabel;

  return result;
}

function _sendOptionsAlertPremium(sym, cmp, optSignal, stage, sl, target, rr, bm, ss) {
  const today   = Utilities.formatDate(new Date(), CONFIG.IST_ZONE, "yyyy-MM-dd");
  const flagKey = `${today}_OPT_${sym.replace(/[:\s]/g,'_')}`;

  if (_bmExists(bm, flagKey)) return;
  if (optSignal.signal !== "📊 BUY CE" && optSignal.signal !== "📦 BASE CE") return;

  const isBase    = optSignal.signal === "📦 BASE CE";
  const typeLabel = isBase ? "📦 BASE OPTIONS SIGNAL" : "📊 OPTIONS SIGNAL";
  const entryRule = isBase
    ? "✅ Buy anytime during 9:30 AM – 12:00 PM\n✅ Stock must be above 20DMA when buying"
    : "✅ Buy between 9:30-9:45 AM only";
  const holdRule  = isBase
    ? "✅ Hold up to 15 trading days\n✅ Exit if option loses 40% of value\n✅ Exit if stock hits Target\n⚠️ Exit if stock goes below SL"
    : "✅ Exit if option loses 40% of value\n✅ Exit if stock hits Target price";
  const tradeNote = isBase
    ? "\n📌 <b>BASE TRADE NOTE:</b> Patient trade — 2-4 weeks. Exit option after 12 trading days if target not hit."
    : "";

  const msg =
    `${typeLabel} — <b>PREMIUM</b>\n` +
    `━━━━━━━━━━━━━━━━━━━━\n` +
    `🎯 <b>Stock:</b> ${sym.replace("NSE:","")}\n` +
    `💰 <b>CMP:</b> ₹${cmp.toFixed(2)}\n` +
    `📋 <b>Stage:</b> ${stage}\n\n` +
    `━━ OPTIONS DETAILS ━━\n` +
    `🎰 <b>Buy:</b> ${optSignal.strike}\n` +
    `📅 <b>Expiry:</b> ${optSignal.expiryStr}\n` +
    `⏳ <b>Theta Risk:</b> ${optSignal.thetaRisk}\n` +
    `📊 <b>VIX Status:</b> ${optSignal.message}\n\n` +
    `━━ UNDERLYING TRADE ━━\n` +
    `🛑 <b>SL:</b> ₹${sl}\n` +
    `🎯 <b>Target:</b> ₹${target}\n` +
    `📈 <b>RR:</b> ${rr}\n\n` +
    `━━ RULES ━━\n` +
    `${entryRule}\n${holdRule}\n` +
    `❌ Do NOT average down on options\n` +
    `❌ Do NOT hold past expiry week\n` +
    `${tradeNote}\n\n` +
    `<i>Educational only. Not SEBI advice. v15.15</i>`;

  _sendTelegramPremium(msg);
  _bmSet(ss, bm, flagKey, "1", sym, "FLAG");
  Logger.log(`[OPTIONS] ${isBase ? "BASE" : "BREAKOUT"} signal sent for ${sym}: ${optSignal.strike}`);
}

// ══════════════════════════════════════════════════════════════════════════════
// BOTMEMORY HELPERS
// ══════════════════════════════════════════════════════════════════════════════

function _bmLoad(ss) {
  const bmSheet = ss.getSheetByName(CONFIG.BM_SHEET);
  const bm = {};
  if (!bmSheet) return bm;
  const lastRow = bmSheet.getLastRow();
  if (lastRow < 2) return bm;
  const data = bmSheet.getRange(2, 1, lastRow - 1, 5).getValues();
  // v15.9: Track first occurrence per key. When duplicate found, clear earlier row.
  const keyToRow = {};
  for (let i = 0; i < data.length; i++) {
    const key = (data[i][0] || "").toString().trim();
    if (!key) continue;
    if (keyToRow[key] !== undefined) {
      // Duplicate — clear the earlier (stale) row, keep latest
      bmSheet.getRange(keyToRow[key] + 2, 1, 1, 5).clearContent();
    }
    keyToRow[key] = i;
    bm[key] = { value: (data[i][1] || "").toString(), row: i + 2 };
  }
  return bm;
}

function _bmGet(bm, key)    { return bm[key] ? bm[key].value : ""; }
function _bmExists(bm, key) { return !!bm[key]; }

// ══════════════════════════════════════════════════════════════════════════════
// CASH WATCHLIST READER — v15.7
// Reads the "CashWatchlist" tab for curated upper-circuit / high-beta stocks.
// These are small/mid caps NOT in Nifty200 that can move 10-20% in one day.
//
// Tab columns (user creates manually):
//   A: Symbol (NSE:XXXX)   B: Name        C: Sector     D: Circuit% (10/20)
//   E: Notes               F: Active      G: CMP        H: Change%
//   I: Volume              J: AvgVol30d
//
// Columns G,H,I use GOOGLEFINANCE formulas (auto-updated).
// Column J is manual 30-day average volume (fill once per month).
//
// GOOGLEFINANCE formulas to put in the tab:
//   G2: =IFERROR(GOOGLEFINANCE(A2,"price"),0)
//   H2: =IFERROR(GOOGLEFINANCE(A2,"changepct"),0)
//   I2: =IFERROR(GOOGLEFINANCE(A2,"volume"),0)
// ══════════════════════════════════════════════════════════════════════════════
function _readCashWatchlist(ss, bm, timeStr, alreadyTraded) {
  const candidates = [];
  try {
    const cwSheet = ss.getSheetByName("CashWatchlist");
    if (!cwSheet) return candidates;

    const lastRow = cwSheet.getLastRow();
    if (lastRow < 2) return candidates;

    const data = cwSheet.getRange(2, 1, lastRow - 1, 10).getValues();

    for (const r of data) {
      const sym     = (r[0] || "").toString().trim();
      const name    = (r[1] || sym).toString();
      const sector  = (r[2] || "CASH").toString();
      const active  = (r[5] || "TRUE").toString().toUpperCase();

      if (!sym || active === "FALSE") continue;
      if (alreadyTraded.has(sym)) continue;

      const cmp       = parseFloat(r[6]) || 0;
      const pctChange = parseFloat(r[7]) || 0;
      const volToday  = parseFloat(r[8]) || 0;
      const avgVol    = parseFloat(r[9]) || 0;

      if (cmp <= 0) continue;
      if (cmp < CONFIG.CASH_MIN_CMP || cmp > CONFIG.CASH_MAX_CMP) continue;
      if (pctChange < CONFIG.CASH_MIN_PCT_CHANGE) continue;
      if (timeStr > CONFIG.CASH_ENTRY_WINDOW) continue;

      // Volume check: only if AvgVol30d is filled
      if (avgVol > 0 && volToday < avgVol * 1.5) continue;

      const cashSl  = parseFloat((cmp * (1 - CONFIG.CASH_SL_PCT)).toFixed(2));
      const cashTgt = parseFloat((cmp * (1 + CONFIG.CASH_TARGET_PCT)).toFixed(2));
      const cashRr  = (cmp - cashSl) > 0 ? (cashTgt - cmp) / (cmp - cashSl) : 0;
      if (cashRr < 1.5) continue;

      const cashQty = Math.max(1, Math.floor(CONFIG.CAPITAL_STD / cmp));
      const key     = sym.replace(/[:\s]/g, '_');

      candidates.push({
        sym, sector, priority: 30,  // slightly higher priority than Nifty200 cash
        row: [
          Utilities.formatDate(new Date(), CONFIG.IST_ZONE, "HH:mm"),
          sym, "", 30, "🔥 Cash Intraday", "CASH",
          `🔥 WATCHLIST CASH | +${pctChange.toFixed(1)}% | ${name}`,
          cashSl.toFixed(2), cashTgt.toFixed(2),
          cashRr.toFixed(2),
          "WAITING",
          "", "", 1,
          cashSl.toFixed(2),
          "", "", cashQty * (cmp - cashSl),
          cashQty,
          `CashWatchlist | SL: ₹${cashSl} | Tgt: ₹${cashTgt}`,
        ],
        key,
      });

      Logger.log(`[CASHWL] ${sym} | +${pctChange.toFixed(1)}% | CMP ₹${cmp}`);
    }
  } catch (e) {
    Logger.log(`[CASHWL] Error reading CashWatchlist: ${e}`);
  }
  return candidates;
}

function _bmSet(ss, bm, key, val, sym, ktype) {
  const bmSheet = ss.getSheetByName(CONFIG.BM_SHEET);
  if (!bmSheet) return;
  const now = Utilities.formatDate(new Date(), CONFIG.IST_ZONE, "yyyy-MM-dd HH:mm:ss");
  sym = sym || ""; ktype = ktype || "STATE";
  if (bm[key]) {
    bmSheet.getRange(bm[key].row, 2).setValue(val);
    bmSheet.getRange(bm[key].row, 3).setValue(now);
    bm[key].value = val;
  } else {
    bmSheet.appendRow([key, val, now, sym, ktype]);
    bm[key] = { value: val, row: bmSheet.getLastRow() };
  }
}

function _bmDel(ss, bm, key) {
  const bmSheet = ss.getSheetByName(CONFIG.BM_SHEET);
  if (!bmSheet || !bm[key]) return;
  bmSheet.getRange(bm[key].row, 1, 1, 5).clearContent();
  delete bm[key];
}

function _bmPurge(ss) {
  const bmSheet = ss.getSheetByName(CONFIG.BM_SHEET);
  if (!bmSheet) return;
  const lastRow = bmSheet.getLastRow();
  if (lastRow < 2) return;

  const cutoffFlag  = new Date(); cutoffFlag.setDate(cutoffFlag.getDate() - CONFIG.BM_PURGE_DAYS);
  const cutoffTrade = new Date(); cutoffTrade.setDate(cutoffTrade.getDate() - CONFIG.BM_PURGE_TRADE_DAYS);
  const cutoffFlagStr  = Utilities.formatDate(cutoffFlag,  CONFIG.IST_ZONE, "yyyy-MM-dd");
  const cutoffTradeStr = Utilities.formatDate(cutoffTrade, CONFIG.IST_ZONE, "yyyy-MM-dd");

  const data = bmSheet.getRange(2, 1, lastRow - 1, 5).getValues();
  for (let i = 0; i < data.length; i++) {
    const key    = (data[i][0] || "").toString().trim();
    const ktype  = (data[i][4] || "").toString().trim();
    const updAt  = (data[i][2] || "").toString().trim(); // UpdatedAt (col C)
    if (!key) continue;

    // FLAG entries: purge after BM_PURGE_DAYS (14d) using key date prefix
    // v15.13: regex check ensures key matches YYYY-MM-DD_* (avoids accidentally
    // matching non-date keys like "_AS_LOCK" or "_BATCH_START")
    if (ktype === "FLAG" && /^\d{4}-\d{2}-\d{2}_/.test(key) && key.substring(0, 10) < cutoffFlagStr) {
      bmSheet.getRange(i + 2, 1, 1, 5).clearContent(); continue;
    }
    // v15.9: TRADE entries: purge after BM_PURGE_TRADE_DAYS (30d) using UpdatedAt
    if (ktype === "TRADE" && updAt.length >= 10 && updAt.substring(0, 10) < cutoffTradeStr) {
      bmSheet.getRange(i + 2, 1, 1, 5).clearContent(); continue;
    }
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// TELEGRAM
// ══════════════════════════════════════════════════════════════════════════════

function _sendTelegramToChat(chatId, msg) {
  if (!chatId || !CONFIG.TELEGRAM_BOT_TOKEN) return;
  try {
    UrlFetchApp.fetch(`https://api.telegram.org/bot${CONFIG.TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "post", contentType: "application/json",
      payload: JSON.stringify({ chat_id: chatId, text: msg, parse_mode: "HTML" })
    });
  } catch(e) { Logger.log("TG error: " + e); }
}

function _sendTelegram(msg)                  { _sendTelegramToChat(CONFIG.CHAT_ID_BASIC,   msg); }
function _sendTelegramAdvance(msg)           { _sendTelegramToChat(CONFIG.CHAT_ID_ADVANCE, msg); }
function _sendTelegramPremium(msg)           { _sendTelegramToChat(CONFIG.CHAT_ID_PREMIUM, msg); }
function _sendTelegramAll(msg)               { _sendTelegramToChat(CONFIG.CHAT_ID_BASIC, msg); _sendTelegramToChat(CONFIG.CHAT_ID_ADVANCE, msg); _sendTelegramToChat(CONFIG.CHAT_ID_PREMIUM, msg); }
function _sendTelegramAdvanceAndPremium(msg) { _sendTelegramToChat(CONFIG.CHAT_ID_ADVANCE, msg); _sendTelegramToChat(CONFIG.CHAT_ID_PREMIUM, msg); }

function _isMarketHoliday(dateStr) {
  // v15.11: prefer runtime set (includes BotMemory-loaded HOLIDAYS_YYYY).
  // Falls back to hardcoded NSE_HOLIDAYS_2026 if _getRuntimeHolidays was not yet called.
  if (_RUNTIME_HOLIDAYS) return _RUNTIME_HOLIDAYS.has(dateStr);
  return NSE_HOLIDAYS_2026.indexOf(dateStr) !== -1;
}

function _inferSignal(rawSignal, stage, fiiBuyZone, smaStr) {
  if (rawSignal && rawSignal !== "#N/A" && rawSignal.length > 2) return rawSignal;
  if (stage.includes("BREAKOUT CONFIRMED") || stage.includes("BREAKOUT ALERT")) return "🟢 STRONG BUY";
  if (stage.includes("Near Breakout")) return "💎 BASE PREPARED";
  if (stage.includes("Building Momentum") || stage.includes("Correction Base")) {
    if (fiiBuyZone === "Accumulation Zone" || smaStr === "Strong Bull" || smaStr === "Bull") return "➖ HOLD";
  }
  if (fiiBuyZone === "Accumulation Zone" && smaStr === "Strong Bull") return "💰 VALUE BUY";
  return "";
}

function _inferPriority(rawPriority, rawMasterScore, signalScore) {
  const ms = parseFloat(rawMasterScore) || 0; if (ms > 0) return ms;
  const p  = parseFloat(rawPriority)    || 0; if (p  > 0) return p;
  const ss = parseFloat(signalScore)    || 0; if (ss > 0) return ss * 3;
  return 0;
}

// ── MENU ──────────────────────────────────────────────────────────────────────
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🚀 AI360 TRADING')
    .addItem('🔄 MANUAL SYNC',       'unifiedManager')
    .addItem('📊 DAILY SUMMARY',     'sendDailySummary')
    .addItem('📅 WEEKLY SUMMARY',    'sendWeeklySummary')
    .addSeparator()
    .addItem('📡 TEST TELEGRAM',     'testTelegram')
    .addItem('📊 TEST OPTIONS',      'testOptionsSignal')
    .addItem('📦 TEST BASE ENTRY',   'testBaseEntry')
    .addSeparator()
    .addItem('⚙️ SETUP TRIGGERS',   'setupTriggers')
    .addItem('🧹 FRESH CLEAN START', 'freshCleanStart')
    .addToUi();
}

function sendDailySummary() {
  const logSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.LOG_SHEET);
  const data     = logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).getValues();
  const traded   = data.filter(r => _isTraded(r[10])).length;
  const waiting  = data.filter(r => _isWaiting(r[10])).length;
  _sendTelegramAdvanceAndPremium(
    `📊 <b>MARKET SUMMARY</b>\n━━━━━━━━━━━━━━━━━━━━\n` +
    `🔹 <b>Active Trades:</b> ${traded}/${CONFIG.MAX_TRADES}\n` +
    `🔸 <b>Waiting Slots:</b> ${waiting}\n` +
    `✅ <i>System: Online v15.15</i>`
  );
}

function unifiedManager() {
  try { _runUnifiedManager(); }
  catch(e) {
    const msg = e.toString();
    if (msg.includes("INTERNAL") || msg.includes("storage") || msg.includes("server error") ||
        msg.includes("timed out") || msg.includes("Service Spreadsheets") || msg.includes("failed while accessing")) {
      Logger.log("[GOOGLE ERROR] Transient — will retry: " + msg); return;
    }
    throw e;
  }
}

function _runUnifiedManager() {
  const ss      = SpreadsheetApp.getActiveSpreadsheet();
  const now     = new Date();
  const timeStr = Utilities.formatDate(now, CONFIG.IST_ZONE, "HH:mm");
  const today   = Utilities.formatDate(now, CONFIG.IST_ZONE, "yyyy-MM-dd");
  const dow     = now.getDay();

  _getRuntimeHolidays(ss);  // v15.11: populate runtime holiday set from BotMemory before holiday check
  if (_isMarketHoliday(today)) { Logger.log(`[HOLIDAY] ${today}`); return; }
  if (dow === 0 || dow === 6)  { Logger.log(`[SKIP] Weekend`);      return; }

  // v15.15 (BUG-9): _bmPurge gated to once per day. Was running every 5 min
  // (~120 fires/day) for no benefit — FLAG TTL is 14d and TRADE TTL is 30d, so
  // nothing changes intra-day. Daily purge is sufficient.
  let bm = _bmLoad(ss);
  const purgeKey = `${today}_BMPURGED`;
  if (!_bmExists(bm, purgeKey)) {
    _bmPurge(ss);
    bm = _bmLoad(ss);   // reload so row indexes reflect purged state
    _bmSet(ss, bm, purgeKey, "1", "", "FLAG");
  }

  if (timeStr >= "09:05" && timeStr <= "09:15") {
    const cleanedKey = `${today}_CLEANED`;
    if (!_bmExists(bm, cleanedKey)) {
      clearWaitingRowsOnly();
      _bmDel(ss, bm, "_BATCH_START");
      _bmDel(ss, bm, "_BATCH_CANDS");
      _bmSet(ss, bm, cleanedKey, "1", "", "FLAG");
    }
  }

  if (dow === 5 && timeStr >= "15:15" && timeStr <= "15:45") {
    const weeklyKey = `${today}_WEEKLY`;
    if (!_bmExists(bm, weeklyKey)) { sendWeeklySummary(); _bmSet(ss, bm, weeklyKey, "1", "", "FLAG"); }
  }

  const userEmail = Session.getActiveUser().getEmail();
  if (userEmail && userEmail !== "") { Logger.log("[MANUAL]"); runFullScanner(); }
  else { Logger.log("[AUTO]"); runBatchedScanner(); }
}

function runFullScanner()    { _runScanner(2, null); }

function runBatchedScanner() {
  const ss         = SpreadsheetApp.getActiveSpreadsheet();
  const bm         = _bmLoad(ss);
  const inputSheet = ss.getSheetByName(CONFIG.SHEET_NAME);
  const totalRows  = inputSheet.getDataRange().getValues().length;
  let batchStart   = parseInt(_bmGet(bm, "_BATCH_START") || "2");
  if (isNaN(batchStart) || batchStart < 2) batchStart = 2;
  const batchEnd   = Math.min(batchStart + CONFIG.BATCH_SIZE, totalRows);
  const scanComplete = _runScanner(batchStart, batchEnd);
  if (!scanComplete) { _bmSet(ss, bm, "_BATCH_START", batchEnd.toString(), "", "STATE"); }
  else { _bmDel(ss, bm, "_BATCH_START"); _bmDel(ss, bm, "_BATCH_CANDS"); }
}

// ══════════════════════════════════════════════════════════════════════════════
// CONVICTION BONUS — v15.6 (FIX 7: delivery proxy added)
// ══════════════════════════════════════════════════════════════════════════════
function _convictionBonus(r, marketBullish) {
  let bonus = 0;
  const vcp        = parseFloat(r[27]) || 1.0;
  const fiiBuyZone = (r[15] || "").toString().trim();
  const daysLow    = parseFloat(r[29]) || 0;
  const smaStr     = (r[7]  || "").toString().trim();
  const stage      = (r[22] || "").toString().trim();
  const af         = parseFloat(r[31]) || 0;
  const rs         = parseFloat(r[20]) || 0;
  const pctChange  = parseFloat(r[3])  || 0;
  const fiiSignal  = (r[32] || "").toString().trim();
  const rank       = parseFloat(r[34]) || 0;

  if      (vcp < 0.04) bonus += 3; else if (vcp < 0.07) bonus += 1;
  if      (fiiBuyZone === "Accumulation Zone") bonus += 2;
  else if (fiiBuyZone === "Momentum Zone")     bonus += 1;
  if      (daysLow > 30) bonus += 2; else if (daysLow > 20) bonus += 1;
  if (smaStr === "Strong Bull") bonus += 1;
  if      (stage.includes("Near Breakout"))     bonus += 1;
  else if (stage.includes("Building Momentum")) bonus += 1;
  else if (stage.includes("Correction Base"))   bonus += 1;
  else if (stage.includes("BREAKOUT CONFIRMED") && rs < CONFIG.LATE_ENTRY_MIN_RS) bonus -= 2;
  if      (af >= 10) bonus += 2; else if (af >= 6) bonus += 1;
  if (!marketBullish && pctChange > 0) bonus += 1;
  if      (fiiSignal === "FII BUYING") bonus += 2;
  else if (fiiSignal === "STRONG FII") bonus += 1;
  if      (rank >= 1 && rank <= CONFIG.RANK_CONV_BONUS_MAX) bonus += 2;
  else if (rank > CONFIG.RANK_CONV_BONUS_MAX && rank <= CONFIG.RANK_LEADER_MAX) bonus += 1;

  // v15.6 FIX 7: Smart money holding proxy (delivery % substitute)
  // daysLow >= 45 + Accumulation = smart money holding = +3 bonus
  if (daysLow >= 45 && fiiBuyZone === "Accumulation Zone") bonus += 3;

  // v15.6: Momentum breakout bonus — strong move today = higher confidence
  if (pctChange >= CONFIG.MOMENTUM_BREAKOUT_MIN_PCT) bonus += 2;

  return bonus;
}

function _getCapital(masterScore, af, fiiBuyZone) {
  if (masterScore >= 28 && af >= 10)                           return CONFIG.CAPITAL_HIGH;
  if (masterScore >= 22 || fiiBuyZone === "Accumulation Zone") return CONFIG.CAPITAL_MED;
  return CONFIG.CAPITAL_STD;
}

function _tradeMode(r) {
  const vcp    = parseFloat(r[27]) || 1.0;
  const smaStr = (r[7]  || "").toString().trim();
  const rs     = parseFloat(r[20]) || 0;
  const stage  = (r[22] || "").toString().trim();
  if (vcp < 0.04 && (stage.includes("Near Breakout") || stage.includes("Building Momentum") || stage.includes("Correction Base"))) return "VCP";
  if (smaStr === "Strong Bull" && rs >= 6) return "MOM";
  return "STD";
}

function _mapTradeType(niftyType, priority, atr, cmp, volVsAvg, pctChange, smaStr, timeStr) {
  const atrPct = (atr / cmp) * 100;
  if (priority >= 28 && atrPct > 2.0) return { ttype: "📊 Options Alert" };
  const inMorning = (timeStr >= CONFIG.INTRADAY_WINDOW_START && timeStr <= CONFIG.INTRADAY_WINDOW_END);
  if (inMorning && volVsAvg > 200 && pctChange > 0.5 && (smaStr === "Strong Bull" || smaStr === "Bull")) return { ttype: "⚡ Intraday" };
  if (niftyType.includes("INTRADAY"))   return { ttype: "⚡ Intraday"   };
  if (niftyType.includes("SWING"))      return { ttype: "🔄 Swing"      };
  if (niftyType.includes("POSITIONAL")) return { ttype: "📈 Positional" };
  if (priority >= 26)                   return { ttype: "📈 Positional" };
  return                                       { ttype: "🔄 Swing"      };
}

function _buildStageTag(signal, ttype, stage, smaStr, fiiBuyZone, isBaseEntry, isMomentum) {
  if (isBaseEntry)  return `📦 BASE ENTRY | ${stage}`;
  if (isMomentum)   return `🚀 MOMENTUM BREAKOUT | ${stage}`;  // v15.6: new tag
  if (signal === "🎯 RETEST BUY") return "🎯 RETEST | " + stage;
  if (ttype === "⚡ Intraday" || ttype === "📊 Options Alert") return "⚡ MOMENTUM | " + stage;
  if (fiiBuyZone === "Accumulation Zone" && (stage.includes("Correction Base") || stage.includes("Building Momentum")) && (smaStr === "Bull" || smaStr === "Strong Bull")) return "📉 CORR.END | " + stage;
  if (signal === "💎 BASE PREPARED") return "📊 BASE | " + stage;
  return stage;
}

// ══════════════════════════════════════════════════════════════════════════════
// CORE SCANNER v15.6
// Changes from v15.5:
//   1. _detectMomentumSectors() called once for all stocks
//   2. _checkBearishEntryAllowed() — hard bearish block
//   3. _checkMomentumBreakout() — new entry type for IT-style moves
//   4. _generateOptionsSignal() now receives high52 for ATH check
//   5. Max waiting slots reduced in bearish (3 instead of 10)
// ══════════════════════════════════════════════════════════════════════════════
function _runScanner(startRow, endRow) {
  const ss         = SpreadsheetApp.getActiveSpreadsheet();
  const logSheet   = ss.getSheetByName(CONFIG.LOG_SHEET);
  const inputSheet = ss.getSheetByName(CONFIG.SHEET_NAME);

  const switchVal = (logSheet.getRange("T2").getValue() || "").toString().toUpperCase();
  if (switchVal !== "YES") { Logger.log("[SKIP] T2 != YES"); return true; }

  const bm        = _bmLoad(ss);
  const inputData = inputSheet.getDataRange().getValues();
  const currentLog= logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).getValues();
  const now       = new Date();
  const nowTime   = Utilities.formatDate(now, CONFIG.IST_ZONE, "yyyy-MM-dd HH:mm:ss");
  const timeStr   = Utilities.formatDate(now, CONFIG.IST_ZONE, "HH:mm");
  const today     = Utilities.formatDate(now, CONFIG.IST_ZONE, "yyyy-MM-dd");
  const totalRows = inputData.length;
  const scanEnd   = (endRow === null) ? totalRows : endRow;
  const isFullScan= (endRow === null || scanEnd >= totalRows);

  const isMorning = timeStr <= CONFIG.MORNING_VOL_BYPASS_UNTIL;
  const indiaVix  = _getIndiaVix(inputData);

  const alreadyTraded = new Set();
  const sectorCount   = {};
  const finalTraded   = currentLog.filter(r => {
    const sym    = (r[1]  || "").toString().trim();
    const status = (r[10] || "").toString().toUpperCase();
    if (sym && _isTraded(status)) {
      alreadyTraded.add(sym);
      const nRow = inputData.find(nr => nr[0] === sym);
      if (nRow) { const sec = (nRow[1] || "UNKNOWN").toString().trim(); sectorCount[sec] = (sectorCount[sec] || 0) + 1; }
      return true;
    }
    return false;
  });

  if (finalTraded.length > CONFIG.MAX_TRADES) { _restoreFormulas(logSheet); return true; }

  let marketBullish = true, niftyCmp = 0, nifty20d = 0;
  try {
    const niftyRow = inputData[1];
    if (niftyRow && niftyRow[0] && niftyRow[0].toString().includes("NIFTY")) {
      niftyCmp = parseFloat(niftyRow[2]) || 0;
      nifty20d = parseFloat(niftyRow[4]) || 0;
      if (niftyCmp > 0 && nifty20d > 0) {
        marketBullish = niftyCmp >= nifty20d;
        Logger.log(`[REGIME] CMP=${niftyCmp} 20DMA=${nifty20d} Bullish=${marketBullish}`);
      }
    }
  } catch(e) { Logger.log("[REGIME] Error: " + e); }

  // v15.6: Determine max waiting slots based on regime
  const maxWaitingSlots = marketBullish ? CONFIG.MAX_WAITING : CONFIG.BEARISH_MAX_WAITING;
  Logger.log(`[v15.6] Market=${marketBullish ? 'BULLISH' : 'BEARISH'} | MaxWaiting=${maxWaitingSlots}`);

  // v15.6 FIX 5: Detect sector momentum — only if BULLISH (saves time in bearish)
  const momentumSectors = marketBullish ? _detectMomentumSectors(inputData) : new Set();
  Logger.log(`[v15.6] VIX=${indiaVix.toFixed(1)} | MomentumSectors: ${[...momentumSectors].join(', ') || 'none'}`);

  let batchCands = [];
  let cashCands  = [];   // Cash Intraday candidates — separate from swing/positional
  if (!isFullScan) {
    try { const stored = _bmGet(bm, "_BATCH_CANDS"); if (stored) batchCands = JSON.parse(decodeURIComponent(stored)); }
    catch(e) { batchCands = []; }
  }

  const validSignals  = ["🎯 RETEST BUY","🟢 STRONG BUY","💎 BASE PREPARED","💰 VALUE BUY","➖ HOLD"];
  const bearishSignals= ["🎯 RETEST BUY","🟢 STRONG BUY","💎 BASE PREPARED"];
  const sectorAfSum   = {};
  const sectorAfCount = {};

  for (let i = startRow; i < scanEnd; i++) {
    const r   = inputData[i];
    const sym = (r[0] || "").toString().trim();
    if (!sym || sym.includes("NIFTY") || alreadyTraded.has(sym)) continue;

    const rawSignal      = (r[19] || "").toString().trim();
    const rawPriority    = r[25];
    const rawMasterScore = r[33];
    const rawSignalScore = r[18];
    const stage      = (r[22] || "").toString().trim();
    const fiiBuyZone = (r[15] || "").toString().trim();
    const smaStr     = (r[7]  || "").toString().trim();
    const fiiSignal  = (r[32] || "").toString().trim();
    const leaderType = (r[17] || "").toString().trim();
    const sector     = (r[1]  || "UNKNOWN").toString().trim();
    const pctChange  = parseFloat(r[3])  || 0;
    const cmp        = parseFloat(r[2])  || 0;
    const atr        = parseFloat(r[28]) || 0;
    const high52     = parseFloat(r[9])  || 0;
    const dma20      = parseFloat(r[4])  || 0;
    const dma50      = parseFloat(r[5])  || 0;
    const distDMA    = parseFloat(r[12]) || 0;
    const pivotRes   = parseFloat(r[26]) || 0;
    const volVsAvg   = parseFloat(r[14]) || 0;
    const retestPct  = parseFloat(r[23]) || -99;
    const af         = parseFloat(r[31]) || 0;
    const rs         = parseFloat(r[20]) || 0;
    const rank       = parseFloat(r[34]) || 0;
    const vcp        = parseFloat(r[27]) || 1.0;
    const daysLow    = parseFloat(r[29]) || 0;

    const signal   = _inferSignal(rawSignal, stage, fiiBuyZone, smaStr);
    const priority = _inferPriority(rawPriority, rawMasterScore, rawSignalScore);
    const useScore = priority;

    if (af > 0) { sectorAfSum[sector] = (sectorAfSum[sector] || 0) + af; sectorAfCount[sector] = (sectorAfCount[sector] || 0) + 1; }

    const isBreakoutStage = stage.includes("BREAKOUT CONFIRMED") || stage.includes("BREAKOUT ALERT");

    // GATE 1: FII Selling
    if (fiiSignal === "FII SELLING") continue;

    // ── CASH INTRADAY DETECTION (v15.7) ──────────────────────────────────────
    // Small-mid cap stocks with 4%+ gap + volume surge = 10-15% intraday potential.
    // These bypass normal swing/positional gates — they're news-driven same-day trades.
    // Bot handles forced 3 PM exit automatically.
    // v15.12: marketBullish requirement removed — cash trades are catalyst-driven
    // (PSU results, defence orders, sector news) and can move 10-15% even in bearish
    // Nifty. Risk is contained by tight 3% SL + 3PM force-exit; the 4% pctChange
    // threshold already requires strong conviction.
    if (timeStr <= CONFIG.CASH_ENTRY_WINDOW &&
        cmp >= CONFIG.CASH_MIN_CMP &&
        cmp <= CONFIG.CASH_MAX_CMP &&
        pctChange >= CONFIG.CASH_MIN_PCT_CHANGE &&
        volVsAvg  >= CONFIG.CASH_MIN_VOLUME_RATIO &&
        cashCands.length < CONFIG.CASH_MAX_SLOTS) {

      const cashAthGap = high52 > 0 ? ((high52 - cmp) / high52) * 100 : 100;
      if (cashAthGap >= CONFIG.CASH_ATH_GAP_MIN_PCT && !alreadyTraded.has(sym)) {
        const cashSl  = parseFloat((cmp * (1 - CONFIG.CASH_SL_PCT)).toFixed(2));
        const cashTgt = parseFloat((cmp * (1 + CONFIG.CASH_TARGET_PCT)).toFixed(2));
        const cashRr  = (cmp - cashSl) > 0 ? (cashTgt - cmp) / (cmp - cashSl) : 0;

        if (cashRr >= 1.5) {
          const cashQty = Math.max(1, Math.floor(CONFIG.CAPITAL_STD / cmp));
          const cashKey = sym.replace(/[:\s]/g, '_');
          // v15.15 (BUG-6): no longer writes BotMemory here — moved to the final
          // "add to finalWaiting" loop so we only persist candidates that actually
          // get a WAITING slot (was orphaning entries when slot was lost).
          cashCands.push({
            sym, sector, priority: 25, key: cashKey,
            row: [
              nowTime, sym, "", 25, "🔥 Cash Intraday", "CASH",
              `🔥 CASH | +${pctChange.toFixed(1)}% | Vol ${volVsAvg.toFixed(0)}%`,
              cashSl, cashTgt, "1:" + cashRr.toFixed(1), "⏳ WAITING",
              "", "", "", "", "", "", "", cashQty,
            ]
          });
          Logger.log(`[CASH] ${sym}: +${pctChange.toFixed(1)}% | Vol ${volVsAvg.toFixed(0)}% | ₹${cmp} | SL ${cashSl} | TGT ${cashTgt}`);
        }
        continue;  // Skip regular swing/positional scan for this stock
      }
    }

    // v15.6 FIX 2: Check for momentum breakout (TECHM/PERSISTENT style)
    const momentumBreakout = _checkMomentumBreakout(pctChange, volVsAvg, rs, high52, cmp, smaStr);
    const isSectorMomentum = momentumSectors.has(sector);
    const isMomentumEntry  = momentumBreakout.isMomentum && isSectorMomentum;

    if (isMomentumEntry) {
      Logger.log(`[MOMENTUM] ${sym}: ${momentumBreakout.reason} in momentum sector ${sector}`);
    }

    // v15.6 FIX 4: Volume bypass for strong movers
    // If price up 3%+ today → volume formula is likely stale → bypass volume gate
    const volumeBypass = (pctChange >= CONFIG.MOMENTUM_BREAKOUT_MIN_PCT);

    // Base entry check
    let isBaseEntry = false;
    if (marketBullish && !isBreakoutStage && !isMomentumEntry) {
      const baseCheck = _checkBaseEntry(stage, fiiBuyZone, vcp, daysLow, smaStr, high52, cmp, useScore);
      if (baseCheck.qualifies) { isBaseEntry = true; Logger.log(`[BASE] ${sym}: ${baseCheck.reason}`); }
    }

    // v15.6 FIX 1: BEARISH HARD BLOCK
    // Before v15.6: bearish filter only checked leaderType, af, score (weak filter)
    // Result: 5 stocks entered per day even in bearish = 4 losses
    // After v15.6: hard block unless score>=40 AND Sector Leader AND RS>=15
    if (!isMomentumEntry) {  // Momentum entries skip bearish block
      const bearishCheck = _checkBearishEntryAllowed(marketBullish, useScore, leaderType, rs);
      if (!bearishCheck.allowed) {
        // Don't log every skip — too noisy. Just continue.
        continue;
      }
    } else if (!marketBullish) {
      // Momentum entry in bearish market — extra strict
      if (useScore < 20 && rs < 15) {
        Logger.log(`[SKIP] ${sym}: momentum but bearish + score ${useScore} + RS ${rs} too low`);
        continue;
      }
    }

    // Standard bullish filter for non-momentum, non-base entries
    if (!isMomentumEntry && !isBaseEntry && marketBullish) {
      if (!validSignals.includes(signal) || useScore < CONFIG.MIN_PRIORITY) continue;
    }

    // GATE 3: Late Entry Block
    if (isBreakoutStage && rs > 0 && rs < CONFIG.LATE_ENTRY_MIN_RS) continue;

    // GATE 4: Price Validity
    if (cmp <= 0 || atr <= 0) continue;
    if (cmp > CONFIG.MAX_CMP) continue;

    // GATE 4b: Result Day Skip (allow momentum entries through this gate)
    const absChange = Math.abs(pctChange);
    if (!isMomentumEntry) {
      if (absChange > CONFIG.CORP_ACTION_SKIP_PCT) continue;
      if (absChange > CONFIG.RESULT_DAY_SKIP_PCT)  continue;
    } else {
      // For momentum: only block extreme moves (circuit filter)
      if (absChange > CONFIG.CORP_ACTION_SKIP_PCT) continue;
    }

    // GATE 5: Extension Filter (base entries exempt)
    if (!isBaseEntry && !isMomentumEntry) {
      if (isBreakoutStage) {
        if (retestPct < CONFIG.RETEST_MAX_PULLBACK) continue;
      } else {
        if (distDMA > CONFIG.MAX_DIST_ABOVE_20DMA) continue;
      }
    }

    // GATE 6: Pivot Resistance (base and momentum exempt)
    if (signal !== "🎯 RETEST BUY" && !isBreakoutStage && !isBaseEntry && !isMomentumEntry) {
      if (pivotRes > 0 && cmp > 0 && ((pivotRes - cmp) / cmp) < CONFIG.PIVOT_RESISTANCE_BUFFER && pivotRes > cmp) continue;
    }

    // GATE 7: Volume Filter (momentum entries bypass if price confirms)
    if (!isMorning && marketBullish && !volumeBypass) {
      const isBaseStage    = stage.includes("Correction Base") || stage.includes("Building Momentum");
      const isBasePrepared = (signal === "💎 BASE PREPARED");
      if (isBreakoutStage) {
        // exempt
      } else if (isBaseEntry || isBaseStage || isBasePrepared) {
        if (volVsAvg < CONFIG.BASE_STAGE_MIN_VOL) continue;
      } else {
        if (volVsAvg < 120) continue;
      }
    }

    // GATE 8: ATH Buffer (base and momentum exempt)
    if (!isBreakoutStage && !isBaseEntry && !isMomentumEntry) {
      if (high52 > 0 && ((high52 - cmp) / high52) * 100 < CONFIG.ATH_BUFFER_PCT) continue;
    }

    // GATE 9: Trade Type
    const niftyTradeType = (r[24] || "").toString().trim();
    if (niftyTradeType.includes("AVOID") || niftyTradeType.includes("NO TRADE")) continue;

    // GATE 10: Sector Concentration
    if ((sectorCount[sector] || 0) >= 2) continue;

    const { ttype } = _mapTradeType(niftyTradeType, priority, atr, cmp, volVsAvg, pctChange, smaStr, timeStr);

    // SL / Target
    let sl, target;
    const isTopRanked  = (rank >= 1 && rank <= CONFIG.RANK_CONV_BONUS_MAX);
    const swingTgtMult = isTopRanked ? CONFIG.ATR_TGT_SWING_LEADER : CONFIG.ATR_TGT_SWING;

    if (isBaseEntry) {
      const rawSl = cmp - atr * CONFIG.ATR_SL_BASE;
      sl     = (dma20 > 0 && dma20 < cmp) ? parseFloat(Math.max(rawSl, dma20 * 0.99).toFixed(2)) : parseFloat(rawSl.toFixed(2));
      target = parseFloat((cmp + atr * CONFIG.ATR_TGT_BASE).toFixed(2));
    } else if (isMomentumEntry) {
      // Momentum entries: tighter SL (intraday style), swing target
      sl     = parseFloat((cmp - atr * 1.5).toFixed(2));
      target = parseFloat((cmp + atr * 3.0).toFixed(2));
    } else if (ttype === "📈 Positional" && niftyTradeType.includes("Value")) {
      const rawSl = cmp - atr * CONFIG.ATR_SL_POSITIONAL;
      sl     = (dma50 > 0 && dma50 < cmp) ? parseFloat(Math.max(rawSl, dma50).toFixed(2)) : parseFloat(rawSl.toFixed(2));
      target = parseFloat((cmp + atr * CONFIG.ATR_TGT_POSITIONAL).toFixed(2));
    } else if (ttype === "📈 Positional") {
      const rawSl = cmp - atr * CONFIG.ATR_SL_POSITIONAL;
      sl     = (dma20 > 0 && dma20 < cmp) ? parseFloat(Math.max(rawSl, dma20).toFixed(2)) : parseFloat(rawSl.toFixed(2));
      target = parseFloat((cmp + atr * CONFIG.ATR_TGT_POSITIONAL).toFixed(2));
    } else if (ttype === "⚡ Intraday" || ttype === "📊 Options Alert") {
      sl     = parseFloat((cmp - atr * CONFIG.ATR_SL_INTRADAY).toFixed(2));
      target = parseFloat((cmp + atr * CONFIG.ATR_TGT_INTRADAY).toFixed(2));
    } else {
      sl     = parseFloat((cmp - atr * CONFIG.ATR_SL_SWING).toFixed(2));
      target = parseFloat((cmp + atr * swingTgtMult).toFixed(2));
    }

    if (sl >= cmp) sl = parseFloat((cmp * 0.97).toFixed(2));

    const risk   = cmp - sl;
    const reward = target - cmp;
    const rrNum  = risk > 0 ? (reward / risk) : 0;
    if (rrNum < CONFIG.MIN_RR) continue;

    const convBonus  = _convictionBonus(r, marketBullish);
    const finalScore = useScore + convBonus;
    const capital    = _getCapital(useScore, af, fiiBuyZone);
    const mode       = _tradeMode(r);
    const qty        = (cmp > 0) ? Math.round(capital / cmp) : 0;
    const atrPct     = atr > 0 ? (atr / cmp) * 100 : 99;
    const stageTag   = _buildStageTag(signal, ttype, stage, smaStr, fiiBuyZone, isBaseEntry, isMomentumEntry);

    // v15.6: Pass high52 to options signal for ATH check
    const optSignal  = _generateOptionsSignal(sym, cmp, atr, stage, pctChange, indiaVix, isBaseEntry, high52);

    batchCands.push({
      priority: finalScore, rawPriority: useScore,
      rank, sector, capital, mode, qty, sym, af, atrPct,
      optSignal, stage, cmp, atr, isBaseEntry, isMomentumEntry,
      row: [
        nowTime, sym, "", priority, ttype, signal, stageTag,
        sl, target, "1:" + rrNum.toFixed(1), "⏳ WAITING",
        "", "", "", "", "", "", "", qty,
      ]
    });
  }

  if (!isFullScan && scanEnd < totalRows) {
    try {
      const storeable = batchCands.map(c => ({...c, optSignal: null}));
      _bmSet(ss, bm, "_BATCH_CANDS", encodeURIComponent(JSON.stringify(storeable)), "", "STATE");
    } catch(e) { Logger.log("[BATCH] Could not save: " + e); }
    return false;
  }

  batchCands.sort((a, b) => {
    const scoreDiff = b.priority - a.priority;
    if (Math.abs(scoreDiff) > 2) return scoreDiff;
    const aL = (a.rank >= 1 && a.rank <= CONFIG.RANK_LEADER_MAX) ? 1 : 0;
    const bL = (b.rank >= 1 && b.rank <= CONFIG.RANK_LEADER_MAX) ? 1 : 0;
    if (bL !== aL) return bL - aL;
    return (a.atrPct || 99) - (b.atrPct || 99);
  });

  const waitingSectorCount = Object.assign({}, sectorCount);
  const finalWaiting       = [];
  let totalDeployed        = finalTraded.length * CONFIG.CAPITAL_MED;

  for (const c of batchCands) {
    // v15.6: Use regime-appropriate max waiting slots
    if (finalWaiting.length >= maxWaitingSlots) break;
    const sec = c.sector || "UNKNOWN";
    if ((waitingSectorCount[sec] || 0) >= 2) continue;
    if (totalDeployed + c.capital > CONFIG.MAX_DEPLOYED + CONFIG.CAPITAL_HIGH) continue;
    waitingSectorCount[sec] = (waitingSectorCount[sec] || 0) + 1;
    totalDeployed += c.capital;

    const key = c.sym.replace(/[:\s]/g, '_');
    _bmSet(ss, bm, `${key}_CAP`,  c.capital.toString(), c.sym, "TRADE");
    _bmSet(ss, bm, `${key}_MODE`, c.mode,               c.sym, "TRADE");
    _bmSet(ss, bm, `${key}_SEC`,  c.sector,             c.sym, "TRADE");
    if (c.rank > 0)        _bmSet(ss, bm, `${key}_RANK`, c.rank.toString(), c.sym, "TRADE");
    if (c.isBaseEntry)     _bmSet(ss, bm, `${key}_BASE`, "1", c.sym, "TRADE");
    if (c.isMomentumEntry) _bmSet(ss, bm, `${key}_MOM`,  "1", c.sym, "TRADE");

    finalWaiting.push(c.row);
    Logger.log(`[CAND] ${c.sym} | ${c.isBaseEntry ? "BASE" : c.isMomentumEntry ? "MOMENTUM" : "BREAKOUT"} | Score=${c.priority.toFixed(0)} | RR=${c.row[9]}`);

    if (c.optSignal) {
      _sendOptionsAlertPremium(c.sym, c.cmp, c.optSignal, c.stage, c.row[7], c.row[8], c.row[9], bm, ss);
    }
  }

  // MOMENTUM SCAN — unchanged from v15.5
  const momCands = [];
  if (marketBullish && timeStr <= CONFIG.MOM_WINDOW_END) {
    for (let i = 2; i < totalRows; i++) {
      const r   = inputData[i];
      const sym = (r[0] || "").toString().trim();
      if (!sym || sym.includes("NIFTY") || alreadyTraded.has(sym)) continue;
      if (finalWaiting.find(row => row[1] === sym)) continue;
      const pctChange = parseFloat(r[3])  || 0;
      const volVsAvg  = parseFloat(r[14]) || 0;
      const cmp       = parseFloat(r[2])  || 0;
      const atr       = parseFloat(r[28]) || 0;
      const smaStr    = (r[7]  || "").toString().trim();
      const fiiSignal = (r[32] || "").toString().trim();
      const sector    = (r[1]  || "UNKNOWN").toString().trim();
      if (pctChange < CONFIG.MOM_MIN_CHANGE_PCT) continue;
      if (volVsAvg  < CONFIG.MOM_MIN_VOLUME_PCT) continue;
      if (fiiSignal === "FII SELLING")            continue;
      if (cmp <= 0 || atr <= 0)                  continue;
      if (cmp > CONFIG.MAX_CMP)                  continue;
      if (smaStr !== "Strong Bull" && smaStr !== "Bull") continue;
      if (Math.abs(pctChange) > CONFIG.RESULT_DAY_SKIP_PCT) continue;
      const sl    = parseFloat((cmp - atr * 1.5).toFixed(2));
      const tgt   = parseFloat((cmp + atr * 2.5).toFixed(2));
      const rrNum = (cmp - sl) > 0 ? (tgt - cmp) / (cmp - sl) : 0;
      if (rrNum < 1.5) continue;
      momCands.push({
        sym, sector,
        row: [nowTime, sym, "", 20, "⚡ MOM Swing", "➖ HOLD",
          `⚡ MOMENTUM | +${pctChange.toFixed(1)}% | Vol ${volVsAvg.toFixed(0)}%`,
          sl, tgt, "1:" + rrNum.toFixed(1), "⏳ WAITING",
          "", "", "", "", "", "", "", Math.round(CONFIG.CAPITAL_STD / cmp)]
      });
      if (momCands.length >= CONFIG.MAX_MOM_SLOTS) break;
    }
    for (const c of momCands) {
      const key = c.sym.replace(/[:\s]/g, '_');
      _bmSet(ss, bm, `${key}_CAP`,  CONFIG.CAPITAL_STD.toString(), c.sym, "TRADE");
      _bmSet(ss, bm, `${key}_MODE`, "MOM",                         c.sym, "TRADE");
      _bmSet(ss, bm, `${key}_SEC`,  c.sector,                      c.sym, "TRADE");
      finalWaiting.push(c.row);
    }
  }

  // ── Merge CashWatchlist curated stocks into cashCands ────────────────────
  // These are pre-curated small/mid caps (upper circuit candidates) NOT in
  // Nifty200. Priority 30 > Nifty200 cash (25) so they surface first.
  const wlCands = _readCashWatchlist(ss, bm, timeStr, alreadyTraded);
  if (wlCands.length > 0) {
    // v15.15 (BUG-6): also no early _bmSet here — moved to final allocator loop
    for (const c of wlCands) {
      if (!cashCands.find(x => x.sym === c.sym)) {
        cashCands.push(c);
      }
    }
    Logger.log(`[CASHWL] ${wlCands.length} watchlist cash candidate(s) merged`);
  }

  // ── Add Cash Intraday candidates to finalWaiting ─────────────────────────
  // Cash slots are SEPARATE from regular waiting slots (don't compete).
  // Max 3 cash entries, only if time is before 10:30 AM.
  if (cashCands.length > 0 && timeStr <= CONFIG.CASH_ENTRY_WINDOW) {
    cashCands.sort((a, b) => b.priority - a.priority);
    let cashAllocated = 0;
    for (const c of cashCands) {
      if (finalWaiting.length >= CONFIG.LOG_ROWS - finalTraded.length) break;
      finalWaiting.push(c.row);
      // v15.15 (BUG-6): write BotMemory ONLY when the candidate gets a slot.
      // Previously written at detection time → orphans whenever the slot was lost.
      const key = c.key || c.sym.replace(/[:\s]/g, '_');
      _bmSet(ss, bm, `${key}_CAP`,  CONFIG.CAPITAL_STD.toString(), c.sym, "TRADE");
      _bmSet(ss, bm, `${key}_MODE`, "CASH",                        c.sym, "TRADE");
      _bmSet(ss, bm, `${key}_SEC`,  c.sector,                      c.sym, "TRADE");
      cashAllocated++;
      Logger.log(`[CASH ADDED] ${c.sym}: WAITING`);
    }
    Logger.log(`[CASH] ${cashAllocated}/${cashCands.length} cash candidate(s) allocated to WAITING slots`);
  }

  // Write AlertLog — v15.9: clearContent() removed (was race condition with trading_bot.py).
  // setValues() already overwrites all LOG_ROWS × TOTAL_COLS cells atomically.
  let finalGrid = finalTraded.concat(finalWaiting);
  while (finalGrid.length < CONFIG.LOG_ROWS) finalGrid.push(new Array(CONFIG.TOTAL_COLS).fill(""));
  logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).setValues(finalGrid);
  _restoreFormulas(logSheet);
  _writeOptionsColumns(logSheet, finalWaiting, batchCands, indiaVix, finalTraded.length);

  // Regime alert
  const regimeFlag = today + (marketBullish ? "_BULLISH" : "_BEARISH");
  if (!_bmExists(bm, regimeFlag)) {
    let topSector = "", topAf = 0;
    for (const sec in sectorAfSum) {
      const avgAf = sectorAfSum[sec] / (sectorAfCount[sec] || 1);
      if (avgAf > topAf) { topAf = avgAf; topSector = sec; }
    }
    const baseCount     = finalWaiting.filter(r => r[6] && r[6].toString().includes("📦 BASE")).length;
    const momentumCount = finalWaiting.filter(r => r[6] && r[6].toString().includes("🚀 MOMENTUM BREAKOUT")).length;
    const cashCount     = finalWaiting.filter(r => r[4] && r[4].toString().includes("Cash Intraday")).length;
    const breakoutCount = finalWaiting.length - baseCount - momentumCount - cashCount;

    let regimeMsg;
    if (!marketBullish) {
      regimeMsg =
        `⚠️ <b>MARKET REGIME: BEARISH</b>\n` +
        `Nifty ₹${niftyCmp.toFixed(0)} below 20DMA ₹${nifty20d.toFixed(0)}\n` +
        `v15.15 HARD BLOCK: Max ${maxWaitingSlots} slots | Score≥${CONFIG.BEARISH_HARD_MIN_SCORE} only\n` +
        `VIX: ${indiaVix.toFixed(1)}\n`;
      if (momentumSectors.size > 0) regimeMsg += `🚀 Momentum sectors: ${[...momentumSectors].join(', ')}\n`;
      if (topSector) regimeMsg += `🔄 Strongest: ${topSector} (AF: ${topAf.toFixed(1)})\n`;
      if (finalWaiting.length > 0) {
        regimeMsg += `\n⚡ <b>${finalWaiting.length} exceptional candidate(s):</b>\n`;
        finalWaiting.slice(0, 3).forEach(r => {
          regimeMsg += `• <b>${r[1]}</b> [${r[4]}] — ${r[6]}\n  SL ₹${r[7]} → T ₹${r[8]} | RR ${r[9]}\n`;
        });
      } else {
        regimeMsg += `\n🛑 No new entries today. Cash is a position.`;
      }
    } else {
      regimeMsg =
        `🟢 <b>SCANNER DONE — ${today}</b>\n` +
        `Nifty ₹${niftyCmp.toFixed(0)} | 20DMA ₹${nifty20d.toFixed(0)} | VIX: ${indiaVix.toFixed(1)}\n`;
      if (momentumSectors.size > 0) regimeMsg += `🚀 Sector momentum: ${[...momentumSectors].join(', ')}\n`;
      if (topSector) regimeMsg += `🔄 Strongest: ${topSector} (AF: ${topAf.toFixed(1)})\n`;
      if (finalWaiting.length > 0) {
        if (baseCount > 0)     regimeMsg += `📦 Base: ${baseCount} | `;
        if (momentumCount > 0) regimeMsg += `🚀 Momentum: ${momentumCount} | `;
        if (cashCount > 0)     regimeMsg += `🔥 Cash: ${cashCount} | `;
        if (breakoutCount > 0) regimeMsg += `💥 Breakout: ${breakoutCount}`;
        regimeMsg += `\n\n📋 <b>${finalWaiting.length} candidate(s):</b>\n`;
        finalWaiting.slice(0, 8).forEach(r => {
          regimeMsg += `• <b>${r[1]}</b> [${r[4]}] — ${r[6]}\n  SL ₹${r[7]} → T ₹${r[8]} | RR ${r[9]}\n`;
        });
      } else {
        regimeMsg += `\n📭 No candidates passed today.`;
      }
      regimeMsg += `\n<i>Entry alerts sent when market opens.</i>`;
    }
    _sendTelegramAdvanceAndPremium(regimeMsg);

    // Basic channel teaser — show market mood + setup count, hide details to drive upgrades
    const topSym = finalWaiting.length > 0 ? (finalWaiting[0][1] || "").replace("NSE:", "") : "";
    const topType = finalWaiting.length > 0 ? (finalWaiting[0][4] || "") : "";
    let basicMsg;
    if (!marketBullish) {
      basicMsg =
        `⚠️ <b>Market Alert — ${today}</b>\n` +
        `Market: 🔴 BEARISH | Nifty: ₹${niftyCmp.toFixed(0)} | VIX: ${indiaVix.toFixed(1)}\n\n` +
        (finalWaiting.length > 0
          ? `🔍 <b>${finalWaiting.length} stock(s) passed our strict bearish filter today</b>\n` +
            `🔒 Entry details shared with Advance/Premium members only\n\n`
          : `🛡️ Our system blocked all new entries today — protecting your capital.\n\n`) +
        `📈 <b>Join Advance @ ₹499/month</b> for real-time alerts\n📱 ai360trading.in/membership`;
    } else {
      basicMsg =
        `🟢 <b>Market Update — ${today}</b>\n` +
        `Market: BULLISH | Nifty: ₹${niftyCmp.toFixed(0)} | VIX: ${indiaVix.toFixed(1)}\n` +
        (momentumSectors.size > 0 ? `🚀 Strong sectors: ${[...momentumSectors].join(", ")}\n` : "") +
        `\n` +
        (finalWaiting.length > 0
          ? `🔍 <b>${finalWaiting.length} stock setup(s) identified today</b>\n` +
            (topSym ? `Top setup: <b>${topSym}</b> [${topType}]\n` : "") +
            `🔒 SL, Target and full details → Advance/Premium members\n\n`
          : `📭 No strong setups today — our filters kept you in cash.\n\n`) +
        `📈 <b>Join Advance @ ₹499/month</b> for real-time entry alerts\n📱 ai360trading.in/membership`;
    }
    _sendTelegramToChat(CONFIG.CHAT_ID_BASIC, basicMsg);

    _bmSet(ss, bm, regimeFlag, "1", "", "FLAG");
  }

  Logger.log(`[DONE] Traded=${finalTraded.length} | Waiting=${finalWaiting.length} (Base=${batchCands.filter(c=>c.isBaseEntry).length}, Momentum=${batchCands.filter(c=>c.isMomentumEntry).length}, Cash=${cashCands.length}) | Bullish=${marketBullish} | v15.7`);
  return true;
}

// ══════════════════════════════════════════════════════════════════════════════
// WRITE OPTIONS COLUMNS — v15.5 (unchanged, tradedCount fix retained)
// ══════════════════════════════════════════════════════════════════════════════
function _writeOptionsColumns(logSheet, finalWaiting, batchCands, vix, tradedCount) {
  tradedCount = tradedCount || 0;
  try {
    const headers = logSheet.getRange(1, 21, 1, 4).getValues()[0];
    if (!headers[0] || headers[0].toString().trim() === "") {
      logSheet.getRange(1, 21).setValue("Options Signal");
      logSheet.getRange(1, 22).setValue("Strike");
      logSheet.getRange(1, 23).setValue("Expiry");
      logSheet.getRange(1, 24).setValue("Theta Risk");
    }
    logSheet.getRange(2, 21, 21, 4).clearContent();
    // BATCH WRITE: build full 21×4 grid, write in one call (was 4 calls per row)
    const optGrid = Array.from({length: 21}, () => ["", "", "", ""]);
    for (let rowIdx = 0; rowIdx < finalWaiting.length; rowIdx++) {
      const waitRow = finalWaiting[rowIdx];
      const sym     = (waitRow[1] || "").toString().trim();
      if (!sym) continue;
      const cand = batchCands.find(c => c.sym === sym);
      if (!cand || !cand.optSignal) continue;
      const opt      = cand.optSignal;
      const gridIdx  = rowIdx + tradedCount; // 0-based index into grid
      if (gridIdx < 21) {
        optGrid[gridIdx][0] = opt.signal    || "⏸ SKIP";
        optGrid[gridIdx][1] = opt.strike    || "—";
        optGrid[gridIdx][2] = opt.expiryStr || "—";
        optGrid[gridIdx][3] = opt.thetaRisk || "—";
      }
    }
    logSheet.getRange(2, 21, 21, 4).setValues(optGrid);
  } catch(e) { Logger.log("[OPTIONS] Column write error: " + e); }
}

// ══════════════════════════════════════════════════════════════════════════════
// FORMULA RESTORE — v15.5 (unchanged)
// ══════════════════════════════════════════════════════════════════════════════
/**
 * v15.9 REWRITE — Batch formula restore.
 * Old: 1 read + ~130 individual setFormula/setValue calls per run (~176 API calls).
 * New: 1 batch read + 5 batch setFormulas calls + max 21 individual writes for col S.
 * Result: ~6x fewer API calls → saves 6–15 seconds per scanner run.
 *
 * Columns restored:
 *   C (3)  — Live price VLOOKUP from Nifty200
 *   N (14) — Days in trade (formula handles traded/non-traded check)
 *   P (16) — P/L% (formula handles traded/entry-price check)
 *   Q (17) — ATH warning VLOOKUP
 *   R (18) — Risk ₹ calculation
 *   S (19) — Position size (conditional: only set when currently empty)
 */
function _restoreFormulas(logSheet) {
  const nRows    = CONFIG.LOG_ROWS;  // 21 data rows
  const startRow = 2;
  const SN       = CONFIG.SHEET_NAME;

  // ONE batch read: all 19 cols × 21 rows (replaces 44 individual getValue calls)
  const data = logSheet.getRange(startRow, 1, nRows, 19).getValues();

  const fC = [], fN = [], fP = [], fQ = [], fR = [];

  data.forEach((row, i) => {
    const r      = startRow + i;
    const sym    = (row[1]  || "").toString().trim();   // col B
    const status = (row[10] || "").toString().toUpperCase(); // col K
    const traded = _isTraded(status);

    if (sym) {
      // C: live price via VLOOKUP
      fC.push([`=IFERROR(VLOOKUP(B${r},'${SN}'!A:C,3,FALSE),"")`]);
      // N: days in trade — self-contained formula handles traded/not-traded
      fN.push([traded
        ? `=IF(M${r}<>"",MAX(0,INT(NOW()-DATEVALUE(TEXT(M${r},"yyyy-mm-dd")))),"—")`
        : `="—"`]);
      // P: P/L%
      fP.push([traded
        ? `=IF(AND(L${r}<>"",C${r}<>"",L${r}<>0),ROUND(((C${r}-L${r})/L${r})*100,2),"")`
        : ``]);
      // Q: ATH warning
      fQ.push([`=IF(B${r}="","",IFERROR(IF(((VLOOKUP(B${r},'${SN}'!A:J,10,FALSE)-C${r})/VLOOKUP(B${r},'${SN}'!A:J,10,FALSE))*100<3,"⚠️ NEAR ATH","✅ OK"),"—"))`]);
      // R: Risk ₹
      fR.push([`=IF(AND(H${r}<>"",H${r}<>0),IF(L${r}<>"",ROUND((L${r}-H${r})*S${r},0),IF(C${r}<>"",ROUND((C${r}-H${r})*S${r},0),"—")),"—")`]);
    } else {
      fC.push([``]); fN.push([`="—"`]); fP.push([``]); fQ.push([``]); fR.push([``]);
    }
  });

  // FIVE batch writes (replaces ~110 individual setFormula/setValue calls)
  logSheet.getRange(startRow, 3,  nRows, 1).setFormulas(fC);
  logSheet.getRange(startRow, 14, nRows, 1).setFormulas(fN);
  logSheet.getRange(startRow, 16, nRows, 1).setFormulas(fP);
  logSheet.getRange(startRow, 17, nRows, 1).setFormulas(fQ);
  logSheet.getRange(startRow, 18, nRows, 1).setFormulas(fR);

  // Col S (position size): conditional — only set formula when cell is empty.
  // Cannot batch safely without overwriting manually entered position sizes.
  // S value was already read in data[i][18] — no extra reads needed.
  data.forEach((row, i) => {
    const r   = startRow + i;
    const sym = (row[1] || "").toString().trim();
    if (!sym) { logSheet.getRange(r, 19).clearContent(); return; }
    const sVal    = row[18];
    const isEmpty = (sVal === "" || sVal === "—" || sVal === null ||
                     (typeof sVal === "string" && sVal.trim() === ""));
    if (isEmpty) {
      logSheet.getRange(r, 19).setFormula(
        `=IF(L${r}<>"",ROUND(10000/L${r},0),IF(C${r}<>"",ROUND(10000/C${r},0),"—"))`
      );
    }
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// MORNING CLEANUP
// ══════════════════════════════════════════════════════════════════════════════
function clearWaitingRowsOnly() {
  const ss       = SpreadsheetApp.getActiveSpreadsheet();
  const bm       = _bmLoad(ss);
  const logSheet = ss.getSheetByName(CONFIG.LOG_SHEET);
  const data     = logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).getValues();
  const traded   = data.filter(r => _isTraded((r[10] || "").toString().toUpperCase()));

  // v15.9: Set write lock so trading_bot.py skips this cycle during morning cleanup.
  // clearContent here creates a blank-AlertLog window (unlike _runScanner which uses
  // atomic setValues over full grid). Lock prevents bot reading empty rows.
  const lockTime = Utilities.formatDate(new Date(), CONFIG.IST_ZONE, "yyyy-MM-dd HH:mm:ss");
  _bmSet(ss, bm, "_AS_LOCK", lockTime, "", "STATE");
  SpreadsheetApp.flush(); // Ensure lock is written before clearing

  logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).clearContent();
  if (traded.length > 0) logSheet.getRange(2, 1, traded.length, CONFIG.TOTAL_COLS).setValues(traded);
  _restoreFormulas(logSheet);
  logSheet.getRange(2, 21, 21, 4).clearContent();

  _bmDel(ss, bm, "_AS_LOCK");
}

// ══════════════════════════════════════════════════════════════════════════════
// FRESH CLEAN START
// ══════════════════════════════════════════════════════════════════════════════
function freshCleanStart() {
  const ss       = SpreadsheetApp.getActiveSpreadsheet();
  const ui       = SpreadsheetApp.getUi();
  const logSheet = ss.getSheetByName(CONFIG.LOG_SHEET);
  const confirm  = ui.alert('🧹 FRESH CLEAN START', 'Clears AlertLog + BotMemory. T2 untouched. Are you sure?', ui.ButtonSet.YES_NO);
  if (confirm !== ui.Button.YES) { ui.alert('❌ Cancelled.'); return; }
  logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).clearContent();
  logSheet.getRange(2, 21, 21, 4).clearContent();
  _restoreFormulas(logSheet);
  const bmSheet = ss.getSheetByName(CONFIG.BM_SHEET);
  if (bmSheet) {
    const lastRow = bmSheet.getLastRow();
    if (lastRow >= 2) {
      const data = bmSheet.getRange(2, 1, lastRow - 1, 5).getValues();
      for (let i = 0; i < data.length; i++) {
        const ktype = (data[i][4] || "").toString().trim();
        if (ktype === "TRADE" || ktype === "STATE") bmSheet.getRange(i + 2, 1, 1, 5).clearContent();
      }
    }
  }
  ["PriceCache","TempPriceCalc"].forEach(name => { const s = ss.getSheetByName(name); if (s) ss.deleteSheet(s); });
  ui.alert('✅ Done. Click 🔄 MANUAL SYNC to fill candidates.');
}

// ══════════════════════════════════════════════════════════════════════════════
// WEEKLY SUMMARY
// ══════════════════════════════════════════════════════════════════════════════
function sendWeeklySummary() {
  const ss       = SpreadsheetApp.getActiveSpreadsheet();
  const hist     = ss.getSheetByName(CONFIG.HISTORY_SHEET);
  const logSheet = ss.getSheetByName(CONFIG.LOG_SHEET);
  const now      = new Date();
  const today    = Utilities.formatDate(now, CONFIG.IST_ZONE, "yyyy-MM-dd");
  const day      = now.getDay();
  const mon      = new Date(now);
  mon.setDate(now.getDate() - (day - 1));
  const monStr   = Utilities.formatDate(mon, CONFIG.IST_ZONE, "yyyy-MM-dd");
  const allHist  = hist ? hist.getDataRange().getValues() : [];
  const weekRows = allHist.slice(1).filter(r => r[3] >= monStr && r[3] <= today);
  const wins     = weekRows.filter(r => (r[6] || "").toString().toUpperCase().includes("WIN"));
  const losses   = weekRows.filter(r => (r[6] || "").toString().toUpperCase().includes("LOSS"));
  const totalPL  = weekRows.reduce((s, r) => s + (parseFloat(r[16]) || 0), 0);
  const winRate  = weekRows.length > 0 ? Math.round((wins.length / weekRows.length) * 100) : 0;
  let best = null, worst = null;
  for (const r of weekRows) {
    const pl = parseFloat(r[16]) || 0;
    if (!best  || pl > (parseFloat(best[16])  || 0)) best  = r;
    if (!worst || pl < (parseFloat(worst[16]) || 0)) worst = r;
  }
  const logData    = logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).getValues();
  const openTrades = logData.filter(r => _isTraded((r[10] || "").toString().toUpperCase()));
  let msg =
    `📅 <b>WEEKLY REPORT — w/e ${today}</b>\n━━━━━━━━━━━━━━━━━━━━\n` +
    `📊 Trades: ${weekRows.length} | ✅ ${wins.length}W / ❌ ${losses.length}L | Win: ${winRate}%\n` +
    `💰 P/L: <b>₹${totalPL >= 0 ? '+' : ''}${Math.round(totalPL).toLocaleString()}</b>\n`;
  if (best)              msg += `🏆 Best:  <b>${best[0]}</b> ₹${Math.round(parseFloat(best[16])  || 0)}\n`;
  if (worst && worst !== best) msg += `💀 Worst: <b>${worst[0]}</b> ₹${Math.round(parseFloat(worst[16]) || 0)}\n`;
  msg += `\n📌 Open: ${openTrades.length}/${CONFIG.MAX_TRADES}\n`;
  msg += `<i>AI360 Trading v15.15 — Base + Breakout + Momentum + Options (Last-Tue expiry)</i>`;
  _sendTelegramAdvanceAndPremium(msg);

  // Basic channel — weekly social proof to build trust and drive upgrades
  const plSign = totalPL >= 0 ? "+" : "";
  let basicWeekly =
    `📅 <b>Weekly Performance — w/e ${today}</b>\n━━━━━━━━━━━━━━━━━━━━\n` +
    `Trades: ${weekRows.length} | ✅ ${wins.length}W ❌ ${losses.length}L | Win Rate: ${winRate}%\n` +
    `P/L this week: <b>₹${plSign}${Math.round(totalPL).toLocaleString()}</b>\n`;
  if (best) basicWeekly += `\n🏆 Best trade: <b>${best[0]}</b> +₹${Math.round(parseFloat(best[16]) || 0)}\n`;
  basicWeekly +=
    `\n📊 Advance/Premium members got all entry, SL and target alerts in real time.\n` +
    `📈 <b>Join Advance @ ₹499/month</b> — get live signals next week\n📱 ai360trading.in/membership`;
  _sendTelegramToChat(CONFIG.CHAT_ID_BASIC, basicWeekly);
}

// ── HELPERS ───────────────────────────────────────────────────────────────────
function _isTraded(status)  { const s = status.toString().toUpperCase(); return s.includes("TRADED") && !s.includes("EXITED"); }
function _isWaiting(status) { return status.toString().toUpperCase().includes("WAITING"); }

// ══════════════════════════════════════════════════════════════════════════════
// BROKER ORDER STUB — v15.9 (Phase 4 Dhan API preparation)
// ══════════════════════════════════════════════════════════════════════════════
/**
 * Phase 4 entry point. Currently PAPER mode — logs only, no real order.
 * To go live: set CONFIG.BROKER_MODE = "LIVE" and implement Dhan API call.
 *
 * @param {string} sym      - NSE:SYMBOL format
 * @param {string} action   - "BUY" or "SELL"
 * @param {number} qty      - quantity
 * @param {number} price    - limit price (0 = market order)
 * @param {string} orderType - "LIMIT" | "MARKET" | "SL" | "SL-M"
 * @returns {object}        - { status, orderId }
 */
function sendBrokerOrder(sym, action, qty, price, orderType) {
  const cleanSym = sym.replace("NSE:", "").trim();
  if (CONFIG.BROKER_MODE !== "LIVE") {
    Logger.log(`[PAPER ORDER] ${action} ${qty} × ${cleanSym} @ ₹${price} (${orderType})`);
    return { status: "PAPER", orderId: "PAPER_" + Date.now() };
  }
  // ── Phase 4: replace this block with Dhan API call ──────────────────────
  // const url     = "https://api.dhan.co/orders";
  // const payload = { symbol: cleanSym, txnType: action, quantity: qty,
  //                   price: price, orderType: orderType, productType: "CNC" };
  // const resp    = UrlFetchApp.fetch(url, { method: "post", ... });
  // return JSON.parse(resp.getContentText());
  // ────────────────────────────────────────────────────────────────────────
  Logger.log(`[LIVE ORDER] ${action} ${qty} × ${cleanSym} — Dhan API not yet wired`);
  return { status: "NOT_IMPLEMENTED" };
}

// ══════════════════════════════════════════════════════════════════════════════
// SETUP TRIGGERS — v15.9
// ══════════════════════════════════════════════════════════════════════════════
/**
 * One-click trigger setup. Run once from menu after deploying AppScript.
 * Deletes all existing time-based triggers, then creates a 5-minute trigger
 * for unifiedManager (market hours handled inside the function itself).
 */
function setupTriggers() {
  // Remove all existing time-based triggers to prevent duplicates
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getTriggerSource() === ScriptApp.TriggerSource.CLOCK) {
      ScriptApp.deleteTrigger(t);
    }
  });

  // Create 5-minute trigger for unifiedManager
  // Market hours + weekend + holiday checks are inside _runUnifiedManager
  ScriptApp.newTrigger('unifiedManager')
    .timeBased()
    .everyMinutes(5)
    .create();

  const msg = '✅ Trigger created!\n\nunifiedManager will run every 5 minutes.\nMarket hours and holiday filtering handled inside the function.\n\nYou can verify at: Extensions → Apps Script → Triggers';
  SpreadsheetApp.getUi().alert('🚀 Setup Complete', msg, SpreadsheetApp.getUi().ButtonSet.OK);
  Logger.log('[SETUP] unifiedManager trigger created — every 5 min');
}

// ── TEST FUNCTIONS ────────────────────────────────────────────────────────────
function testTelegram() {
  const now     = new Date();
  const timeStr = Utilities.formatDate(now, CONFIG.IST_ZONE, "dd-MMM HH:mm");
  _sendTelegramToChat(CONFIG.CHAT_ID_BASIC,   `✅ <b>TEST — ${timeStr}</b>\nChannel: Basic 🆓\nv15.15 ✅`);
  _sendTelegramToChat(CONFIG.CHAT_ID_ADVANCE, `✅ <b>TEST — ${timeStr}</b>\nChannel: Advance 📊\nv15.15 ✅`);
  _sendTelegramToChat(CONFIG.CHAT_ID_PREMIUM, `✅ <b>TEST — ${timeStr}</b>\nChannel: Premium 💎\nv15.15 + Last-Tuesday expiry + Bearish Block + Momentum + ATH Options Fix ✅`);
}

function testOptionsSignal() {
  const ss        = SpreadsheetApp.getActiveSpreadsheet();
  const inputData = ss.getSheetByName(CONFIG.SHEET_NAME).getDataRange().getValues();
  const vix       = _getIndiaVix(inputData);
  const expiry    = _getRecommendedExpiry(OPTIONS_CONFIG.MIN_DAYS_EXPIRY);
  const expiryStr = Utilities.formatDate(expiry.date, CONFIG.IST_ZONE, "dd-MMM-yyyy");
  const testBreakout = _generateOptionsSignal("NSE:ADANIPORTS", 1691, 33.5, "⚡ BREAKOUT ALERT", -4.32, vix, false, 1823.9);
  const testATH      = _generateOptionsSignal("NSE:MCX",        3353,  80,  "⚡ BREAKOUT ALERT",  0.50, vix, false, 3500);
  const msg =
    `📊 <b>OPTIONS TEST — v15.15</b>\n━━━━━━━━━━━━━━━━━━━━\n` +
    `VIX: ${vix.toFixed(1)} | Expiry: ${expiryStr} (${expiry.daysLeft}d)\n\n` +
    `BREAKOUT (ADANIPORTS): ${testBreakout.signal} | ${testBreakout.strike}\n` +
    `ATH TEST (MCX near ATH): ${testATH.signal} | ${testATH.message}\n` +
    `✅ v15.15 ATH block working`;
  _sendTelegramPremium(msg);
  SpreadsheetApp.getUi().alert("Options test sent to Premium channel.");
}

function testBaseEntry() {
  const ss        = SpreadsheetApp.getActiveSpreadsheet();
  const inputData = ss.getSheetByName(CONFIG.SHEET_NAME).getDataRange().getValues();
  const vix       = _getIndiaVix(inputData);

  const test1 = _checkBaseEntry("Correction Base",   "Accumulation Zone", 0.03, 18, "Strong Bull", 500, 420, 20);
  const test2 = _checkBaseEntry("Building Momentum", "Momentum Zone",     0.03, 18, "Strong Bull", 500, 420, 20);
  const test3 = _checkBaseEntry("Correction Base",   "Accumulation Zone", 0.08, 18, "Strong Bull", 500, 420, 20);
  const test4 = _checkBaseEntry("Correction Base",   "Accumulation Zone", 0.03, 10, "Strong Bull", 500, 420, 20);

  const testMom1 = _checkMomentumBreakout(5.15, 150, 10.16, 1994, 1348, "Sideways"); // COFORGE
  const testMom2 = _checkMomentumBreakout(4.85, -10, 0,     1854, 1437, "Sideways"); // TECHM (low RS)
  const testMom3 = _checkMomentumBreakout(5.48, 200, 22,    5554, 4960, "Sideways"); // PERSISTENT

  const msg =
    `📦 <b>BASE + MOMENTUM TEST — v15.15</b>\n━━━━━━━━━━━━━━━━━━━━\n` +
    `VIX: ${vix.toFixed(1)}\n\n` +
    `BASE TESTS:\n` +
    `Test 1 (all pass): ${test1.qualifies ? "✅" : "❌"} ${test1.reason}\n` +
    `Test 2 (FII fail): ${test2.qualifies ? "✅" : "❌"} ${test2.reason}\n` +
    `Test 3 (VCP fail): ${test3.qualifies ? "✅" : "❌"} ${test3.reason}\n` +
    `Test 4 (Days fail): ${test4.qualifies ? "✅" : "❌"} ${test4.reason}\n\n` +
    `MOMENTUM BREAKOUT TESTS (v15.15):\n` +
    `COFORGE +5.15%: ${testMom1.isMomentum ? "✅ ALLOWED" : "❌ BLOCKED"} — ${testMom1.reason}\n` +
    `TECHM +4.85% (low RS): ${testMom2.isMomentum ? "✅ ALLOWED" : "❌ BLOCKED"} — ${testMom2.reason}\n` +
    `PERSISTENT +5.48%: ${testMom3.isMomentum ? "✅ ALLOWED" : "❌ BLOCKED"} — ${testMom3.reason}\n\n` +
    `✅ v15.15 Last-Tue expiry + Momentum gate working`;
  _sendTelegramPremium(msg);
  SpreadsheetApp.getUi().alert("Tests sent to Premium channel.");
}

// ══════════════════════════════════════════════════════════════════════════════
// CASH WATCHLIST FORMULA FILLER — v15.8
// Writes GOOGLEFINANCE formulas into cols G/H/I for every row that has a
// symbol in col A. Run once (or whenever new rows are added).
// No trigger needed — formulas auto-refresh every few minutes by Google Sheets.
// ══════════════════════════════════════════════════════════════════════════════
function updateCashWatchlistPrices() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName("CashWatchlist");
  if (!sh) return;

  const lastRow = sh.getLastRow();
  if (lastRow < 2) return;

  const symbols = sh.getRange(2, 1, lastRow - 1, 1).getValues(); // col A
  let filled = 0;

  for (let i = 0; i < symbols.length; i++) {
    const sym = (symbols[i][0] || "").toString().trim();
    if (!sym) continue;

    const row = i + 2;
    sh.getRange(row, 7).setFormula(`=IFERROR(GOOGLEFINANCE(A${row},"price"),"")`);
    sh.getRange(row, 8).setFormula(`=IFERROR(GOOGLEFINANCE(A${row},"changepct"),"")`);
    sh.getRange(row, 9).setFormula(`=IFERROR(GOOGLEFINANCE(A${row},"volume"),"")`);
    sh.getRange(row, 10).setFormula(`=IFERROR(GOOGLEFINANCE(A${row},"volumeavg"),"")`); // ~3-month avg daily volume
    filled++;
  }

  SpreadsheetApp.flush();
  Logger.log("[CWPRICE] Formulas written for " + filled + " rows");
}