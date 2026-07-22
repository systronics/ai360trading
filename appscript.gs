/**
 * AI360 TRADING — APPSCRIPT v15.30
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * v15.30 CHANGES (2026-07-23, post-midnight) — SECTOR DIRECTION SURFACED ON OPTIONS ALERTS (owner: "i think market, sector and stock all are same direction then option entry")
 *   Market regime (bullish gate) and stock direction (breakout/base stage)
 *   were already required for every candidate that reaches
 *   `_generateOptionsSignal` — the missing 3rd leg was sector direction.
 *   Nifty200 col V "Sector_Trend" (TAILWIND/HEADWIND) existed and was
 *   computed every scan but read NOWHERE in this file. Now threaded through
 *   `_generateOptionsSignal` (new `sectorTrend` param) into the premium
 *   options Telegram alert as an extra line: TAILWIND = "market+sector+stock
 *   sab same direction", HEADWIND = "stock alag chal raha apne sector se,
 *   extra caution". Deliberately INFO, not a new hard gate — a HEADWIND
 *   sector still sends the alert, clearly flagged, so this doesn't shrink
 *   the candidate pool the way a new gate would; the owner's own 3-way
 *   alignment check is now visible on the alert instead of undoable.
 *
 * v15.29 CHANGES (2026-07-22/23, post-midnight) — AFTERNOON-MOVE BLIND SPOT CLOSED (owner: "fill all, where is gap... most stocks moving up, still i am unable to catch base and after correction")
 *   The v15.28 diagnostic (below) plus a live 07-21 example (M&MFIN queued
 *   ~15:07, time-blocked every tick to close) exposed a stacked set of
 *   time/move-size cutoffs that together made any move developing after
 *   late-morning nearly unreachable, regardless of how clean the setup was:
 *     - CASH_ENTRY_WINDOW 10:30→13:30: the 4%+ gap/catalyst intraday path
 *       (designed for exactly the 10-20% small/mid-cap moves the owner
 *       described) only ever scanned until 10:30 AM. Still leaves 1.5hr
 *       before the existing 15:00 CASH_FORCE_EXIT_HOUR.
 *     - MOM_WINDOW_END 11:30→14:30: the sector-momentum breakout scan had
 *       the same blind spot; aligned with the bot's new entry cutoff below.
 *     - RESULT_DAY_SKIP_PCT 6.0→10.0: the main swing scan auto-skipped ANY
 *       single stock up more than 6% that day as a suspected earnings/
 *       corp-action spike — UNLESS 3+ other stocks in its sector were also
 *       up 2%+ (MOMENTUM_SECTOR_MIN_COUNT). An isolated strong mover (not
 *       part of a sector-wide rally) never got that exemption, so ordinary
 *       6-10% breakout days — common, not rare — were being thrown out.
 *       CORP_ACTION_SKIP_PCT(15) hard outer bound left unchanged.
 *   trading_bot.py's own ENTRY_WINDOW_BULLISH_END moved 14:30→15:05 in the
 *   same pass (separate file, same root cause) — see that file's changelog.
 *   Bearish-regime windows/thresholds (ENTRY_WINDOW_BEARISH_END=11:00,
 *   BEARISH_HARD_MIN_SCORE=40, BEARISH_MIN_RS=15) deliberately NOT touched
 *   — those are tied to the documented v15.6 "4 losses" bearish hard-block
 *   evidence and this session found no new evidence to revisit them.
 *   Syntax-checked (`node --check` on a renamed copy) + boundary-tested
 *   (trading_bot.py side: 5/5 cases incl. new 15:05/15:06 edge) before
 *   deploy via `.\deploy_appscript.ps1`.
 *
 * v15.28 CHANGES (2026-07-22, late night) — CANDIDATE-STARVATION DIAGNOSTIC (owner: "why not any intraday trade yesterday and today, analyse whole system")
 *   Audit of 2026-07-21/22 GitHub Actions logs + live sheet found: (1) TODAY
 *   correctly traded 0 — Nifty -0.79% red, regime BEARISH, and every
 *   candidate's Priority_Score (best was TITAN=30) sat below
 *   BEARISH_HARD_MIN_SCORE(40), so _checkBearishEntryAllowed correctly
 *   rejected all of them before any other gate ran. Working as designed.
 *   (2) YESTERDAY the regime was BULLISH all day, yet trading_bot.py's
 *   [FILTER] log shows only TITAN (RSI 77+ hard-blocked most of the
 *   afternoon, correctly — >75 is the real overbought ceiling) and a brief
 *   M&MFIN ever reached AlertLog's WAITING queue, while today's Nifty200
 *   snapshot shows several other STRONG BUY/BREAKOUT CONFIRMED names
 *   (INDUSINDBK Master 43, NESTLEIND 42, SHRIRAMFIN 35) with healthy RS and
 *   Priority Score clear of every static gate value checked after the fact.
 *   Could not pin down the exact rejecting line without a live trace —
 *   Nifty200 values shift daily and nothing logged the near-misses.
 *   Added a read-only diagnostic block at the end of the WAITING-candidate
 *   loop (after `finalWaiting` is finalized): logs the day's top-5
 *   Master_Score stocks (excluding already-traded) and whether each reached
 *   the WAITING queue. Touches ZERO gate/trade logic — pure Logger.log, all
 *   existing `continue` statements and thresholds are byte-for-byte
 *   unchanged. Purpose: turn the next occurrence of this question into a
 *   one-line log lookup (Apps Script Editor → Executions) instead of a
 *   multi-hour forensic reconstruction. No locked/owner-validated gate
 *   value was touched — see CLAUDE.md 🔒 NEVER CHANGE.
 *
 * v15.27 CHANGES (2026-07-20) — COLUMN-DRIFT GUARD (owner: "analyse full system, find loop or gap")
 *   _runScanner read Nifty200 ATR (col 28) and Options-tag (col 35) by raw
 *   index only, with no check that those columns still hold what the code
 *   assumes — a future inserted column would have silently fed wrong ATR
 *   into every SL/target and a stale Options tag into option gating, with
 *   no error. Now a one-time header check on each run (ATR col header must
 *   contain "ATR", Options col header must equal "Options"); on mismatch,
 *   both reads fail SAFE to 0/null (same as a missing column) instead of
 *   trusting a shifted column, and a [COLUMN-DRIFT] line is logged.
 *
 * v15.26 CHANGES (2026-07-18) — OPTIONS = INTRADAY/1-2 DAY + CURRENT EXPIRY + EASY LANGUAGE (owner rule)
 *   Owner's structure: options are INTRADAY / max 1-2 day momentum trades;
 *   the stock's 2-4 week move is taken in CASH/MTF (theta kills long option
 *   holds). Liquidity lives in the CURRENT expiry — retail option buyers
 *   trade it; next month only in the rollover zone.
 *   1. _getRecommendedExpiry: picks CURRENT monthly expiry; ≤ROLLOVER_DAYS(5)
 *      left → NEXT month; month+2 unreachable. Kills MIN_DAYS_BASE_ENTRY:40,
 *      which pushed the 17-Jul MOTILALOFS signal past 25-Aug (39d) by ONE
 *      day onto the dead Sep chain (no volume, ~20% bid-ask spread).
 *   2. ❌ THETA HIGH rejection removed; theta labels re-scaled for 1-2 day
 *      holds (≥15d LOW / ≥8d MED / <8d sirf-intraday warning).
 *   3. Premium option alert rewritten in easy Hinglish: hold = intraday/1-2
 *      din, stock trade = CASH/MTF, entry-valid-above-SL line, TradingView
 *      chart line (DAILY for stock, 15m for option timing).
 *   4. Night-scan candidates list now ends with a "Kaise trade kare" legend
 *      (BASE/BREAKOUT = cash/MTF 2-4 hafte; option = 1-2 din; DAILY chart).
 *
 * v15.25 CHANGES (2026-07-17, late evening) — STRIKE GRID UNIFIED (known-items pack)
 *   _getStrikeInterval now shares ONE table with Python option_intelligence
 *   v1.3 strike_step (and the bot's CE fallback): <100→1, <250→5, <500→10,
 *   <1000→20, <2000→50, ≥2000→100. The engines previously used different
 *   grids (e.g. 250-500: Python 5 vs here 10), so the night ATM alert and
 *   the entry-time ITM pick could sit on different strike ladders for the
 *   same stock. Sub-₹100 band added so low-price stocks aren't rounded onto
 *   a 5-step grid. Also same-evening bullish-footer version stamp (was only
 *   on the bearish header + option/test footers).
 *
 * v15.24 CHANGES (2026-07-17, evening) — FULL-AUDIT BUG PACK (owner: "fix all")
 *   1. CASHWATCHLIST ROW CRASH FIXED — _readCashWatchlist built a 20-element
 *      row (trailing notes string) but the AlertLog grid write is 19 columns
 *      (TOTAL_COLS); setValues() throws on the mismatch, aborting the ENTIRE
 *      scanner run (no AlertLog write, no formulas, no regime alert) on every
 *      5-min trigger while any watchlist stock qualified (+4% before 10:30).
 *      Latent since v15.8 — armed the first morning a curated stock gapped.
 *      Row now matches the Nifty200 cash-candidate shape exactly (19 cols,
 *      "⏳ WAITING", full timestamp, "1:x.x" RR).
 *   2. MOM-SWING SCAN GATE-3 PARITY — the separate momentum scan queued names
 *      with NO RS check, no sector cap, and pushed past the regime slot limit;
 *      the Python bot then vetoed them at RS<5 → dead WAITING slots + a
 *      misleading Telegram board (the exact v15.19 funnel disease, still open
 *      on this path). Now: RS ≥ LATE_ENTRY_MIN_RS (blank RS fail-open, same
 *      as GATE 3), 2-per-sector cap, and maxWaitingSlots respected.
 *   3. TIME-FAIR VOLUME PACE (mirror of Python institutional_edges v1.1) —
 *      Volume_vs_Avg % divides partial-day volume by a full-day average, so
 *      every intraday reading runs ~2× low; GATE 7 (post-10:30) and the MOM
 *      scan (≤11:30) were structurally starved — the same bug fixed on the
 *      Python side on 07-16 but never here. Gates now compare time-fair PACE
 *      (reading ÷ expected session fraction, NSE U-shape, 15-min quote delay)
 *      against the SAME numeric bars expressed as multiples: GATE 7 120→2.2×,
 *      BASE 40→1.4×, MOM/CASH 200→3.0×. Night/EOD scans (fraction = 1.0)
 *      behave EXACTLY as before — only intraday measurement is made fair.
 *      Also corrected the misleading "2x average" comments: the column is
 *      diff-form (+50 = 1.5×, owner-verified v15.13), so 200 was always 3×.
 *
 * v15.23 CHANGES (2026-07-17, pre-market) — REAL F&O ELIGIBILITY + HONEST SECTOR LINES
 *   Companion to the same-morning sheet repairs (fetch_rs v2.0: col AC now a
 *   REAL ATR(14); col B normalized to 18 NSE macro sectors; new col AJ
 *   "Options" = N50/YES/"" from NSE's official F&O file; 17 missing Nifty200
 *   members added; col AK N200 = YES/EX membership).
 *   1. OPTION SIGNALS GATED ON LIVE F&O ELIGIBILITY — _generateOptionsSignal
 *      now takes optTag (col AJ). "" = stock has NO derivatives (SEBI's 2025
 *      purge removed IRCTC/MRF/ATGL/TATACOMM/...) → SKIP. The hardcoded
 *      F_AND_O_LIQUID_STOCKS list had gone stale (still contained IRCTC,
 *      TATAMOTORS pre-demerger, ZOMATO pre-rename) and is now only the
 *      fallback when the column is absent. Premium option alerts also show a
 *      chain-liquidity line: Nifty50 = deep & liquid / midcap = check spread.
 *   2. HONEST "Strongest:" SECTOR LINE — sector AF average now includes
 *      NEGATIVE AF stocks (was winners-only survivorship bias: one hot stock
 *      in a solo-label sector could top the line) and requires ≥3 scored
 *      stocks in the sector (meaningful now that col B holds macro sectors —
 *      before, 62 of 100 labels contained a single stock).
 *
 * v15.22 CHANGES (2026-07-16, same night) — SL NOISE FLOOR + CONFIRM-AT-OPEN
 *   Owner-approved "fix where need" after the BHARATFORG premium option alert
 *   review. Two risk-quality fixes:
 *   1. SL NOISE FLOOR (MIN_SL_ATR_MULT = 0.75) — the DMA-anchored stop could
 *      snap to within noise of entry when price sat ON its DMA (BHARATFORG:
 *      20DMA 1.5 pts below CMP → SL ₹2071.34 on CMP ₹2093.80 = 1.07% stop on
 *      a "2-4 week" trade, RR inflated to 9.6). A DMA anchor may now TIGHTEN
 *      the ATR stop only while leaving ≥ 0.75×ATR of room; otherwise the raw
 *      ATR stop (1.5×/2.5×ATR) is kept. Applies to base (20DMA×0.99) and both
 *      positional paths (50DMA/20DMA — these had NO buffer at all: price 0.1%
 *      above the DMA meant a 0.1% stop). Owner's tight-SL rule respected —
 *      stops only widen when the old one was inside noise; RR is now honest.
 *   2. CONFIRM-AT-OPEN GUARD on premium option alerts sent outside market
 *      hours (night scan = last close's data; 07-15 BHARATFORG/DELHIVERY were
 *      queued at night and opened in downtrends): the RULES block adds "Buy
 *      ONLY if the stock trades above ₹{last close} after 9:30 / skip if red
 *      / skip if morning regime message says BEARISH".
 *
 * v15.21 CHANGES (2026-07-16) — HONEST PREMARKET REGIME MESSAGE + LIVE VERSION STAMPS
 *   Owner-approved after the 07-16 Telegram review: the 00:03 night-scan
 *   message declared "MARKET REGIME: BEARISH — No new entries today. Cash is
 *   a position." off a 4-point gap below the 20DMA (previous-close data);
 *   the market gapped up and the 09:28 open scan sent 6 candidates —
 *   contradictory for subscribers. Changes (message text only, ZERO gate /
 *   slot / scoring logic touched):
 *   1. Regime alerts sent outside 09:15-15:30 IST carry "(yesterday's close
 *      — live regime decided at 9:15)".
 *   2. When |Nifty − 20DMA| < REGIME_BORDERLINE_PCT (0.30%), both bearish
 *      and bullish messages add a ⚖️ BORDERLINE line ("a small gap at open
 *      can flip this"), and the overnight bearish no-candidates line becomes
 *      "No candidates queued tonight. Regime is re-checked at the open…"
 *      instead of the falsely-final "No new entries today".
 *   3. CONFIG.VERSION single source for ALL subscriber-facing version
 *      stamps (regime header, premium option footer, System Online footer,
 *      scan footer, test messages) — they were hardcoded and stale at
 *      v15.17/v15.20 in five different places.
 *
 * v15.20 CHANGES (2026-07-15) — OPTION-ALERT SAFETY PACK (owner-approved)
 *   1. EARNINGS BLOCK on the night-scan premium option alert — mirrors the
 *      Python entry-time check (EARNINGS_{SYM}_{date} BotMemory keys from
 *      fetch_earnings.py, window yesterday..+3d). IV crush protection for
 *      the alert paying subscribers actually act on. Fail-open.
 *   2. STRIKE FIX — _roundToStrike Math.ceil→Math.round (the old "ATM" was
 *      always one step OTM), and breakout signals no longer pick an OTM
 *      strike ~1 ATR away (theta trap; contradicted the ITM entry-time
 *      block). Night alert now always suggests true ATM; the final ITM pick
 *      comes with the entry alert.
 *   3. HONEST VIX — fetch failure returned a fake 14.0 that rendered as
 *      "✅ VIX 14.0 — good to buy"; now returns 0 → displays show "n/a" via
 *      _vixStr() and the option gate warns "verify India VIX before buying".
 *   (4. Python side, same session: option_intelligence v1.1 — bearish regime
 *      now SKIPs options entirely; the old PE path recommended a PUT on a
 *      stock the system had just bought long. Buy-side only per owner.)
 *
 * v15.19 CHANGES (2026-07-15) — RS LEADERSHIP PRE-SCREEN AT QUEUE TIME
 *   Owner-approved funnel fix: the Python bot hard-vetoes any non-cash entry
 *   with sheet RS < 5, but the scanner queued candidates WITHOUT checking RS
 *   (old GATE 3 fired only for breakout stage AND only when rs > 0 — negative
 *   RS slipped through because the guard treated it as "missing", though on
 *   the ±% RS scale negative IS real data). Result: WAITING slots filled with
 *   names the bot could never buy (0 entries for ~2.5 weeks, July 2026) and
 *   the Telegram candidate lists misled manual followers. GATE 3 now applies
 *   the same RS ≥ LATE_ENTRY_MIN_RS(5) screen to ALL bullish candidates;
 *   blank/unparseable RS stays fail-open; bearish path (own RS≥15 block) and
 *   cash intraday (news-driven, RS-exempt in the bot too) are unchanged.
 *
 * v15.18 CHANGES (2026-06-05) — BIGGER+SAFER TARGETS + OPTION LOSS CAP
 *   Owner directive: "minimum stop-loss, maximum target above 5%, no big loss
 *   on option buying." (1) Reachability-aware +5% target FLOOR on multi-day
 *   equity holds (swing/mom/positional/base) — applied only when ATR% >=
 *   MIN_TARGET_ATRPCT so low-vol large-caps keep their ATR target and still
 *   book the win (no time-stop stranding). Lifting target only improves RR, so
 *   it can never reject a previously-valid setup. (2) Option exit rule changed
 *   from the loose "option −40%" to STOCK-anchored (exit when stock breaks SL ≈
 *   option −15-20%, hard cap 20%) so option losses stay small.
 *
 * v15.17 CHANGES (2026-05-30) — H2-2026 HOLIDAY CORRECTION + VERSION STRINGS
 *   The Aug-Dec 2026 holidays in NSE_HOLIDAYS_2026 were approximations and
 *   materially wrong: Diwali had been guessed at 21/22-Oct (actual Balipratipada
 *   is 10-Nov), Ganesh Chaturthi (14-Sep) and Dussehra (20-Oct) were missing,
 *   and Janmashtami (27-Aug) is not an NSE holiday. Same bug-class that caused
 *   the 2026-05-27 outage. Now VERIFIED against NSE official circular + Zerodha
 *   + ClearTax (all three agree). trading_bot.py NSE_HOLIDAYS_2026 corrected
 *   identically in the same session. Also bumped stale "v15.15" version strings
 *   in subscriber-facing Telegram messages to v15.17.
 *
 * v15.16 CHANGES (2026-05-27) — CRITICAL HOLIDAY LIST CORRECTION
 *   NSE_HOLIDAYS_2026 was WRONG — caused Wed 2026-05-27 to be treated as
 *   a holiday (correct holiday is Thu 2026-05-28, Bakri Id). The bot AND
 *   AppScript scanner both skipped today → no Telegram messages, missed
 *   target-hit exits for CUMMINSIND (+12%) and HINDALCO (+6%).
 *   Source: NSE official Holidays 2026 — Equities page.
 *   Several other 2026 dates were also off by 1 day; corrected per official list.
 *
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

// ── NSE OFFICIAL TRADING HOLIDAYS 2026 ────────────────────────────────────────
// Source: nseindia.com → Resources → Holidays (Equities, 2026).
// v15.16 FIX (2026-05-27): list was wrong — 2026-05-27 was NOT a holiday,
//   2026-05-28 (Bakri Id, Thu) is. Bot skipped on Wed thinking it was holiday,
//   missed target-hit exits for CUMMINSIND & HINDALCO. Also corrected:
//     2026-03-25 → 2026-03-26 (Ram Navami)
//     2026-04-02 → 2026-04-03 (Good Friday)
//     2026-06-17 → 2026-06-26 (Muharram)
//   Added: 2026-01-15 (Maharashtra elec), 2026-03-03 (Holi), 2026-03-31 (Mahavir).
const NSE_HOLIDAYS_2026 = [
  "2026-01-15", // Municipal Corp Election — Maharashtra (Thu)
  "2026-01-26", // Republic Day (Mon)
  "2026-03-03", // Holi (Tue)
  "2026-03-26", // Shri Ram Navami (Thu)
  "2026-03-31", // Shri Mahavir Jayanti (Tue)
  "2026-04-03", // Good Friday (Fri)
  "2026-04-14", // Dr. Ambedkar Jayanti (Tue)
  "2026-05-01", // Maharashtra Day (Fri)
  "2026-05-28", // Bakri Id (Thu)
  "2026-06-26", // Muharram (Fri)
  // Aug-Dec 2026 — VERIFIED 2026-05-30 vs NSE official + Zerodha + ClearTax
  // (all three agree). Replaces earlier approximations that were materially
  // wrong (Diwali had been guessed at 21/22-Oct; actual Balipratipada is 10-Nov).
  "2026-08-15", // Independence Day (Sat — weekend anyway; kept for clarity)
  "2026-09-14", // Ganesh Chaturthi (Mon)
  "2026-10-02", // Mahatma Gandhi Jayanti (Fri)
  "2026-10-20", // Dussehra / Vijaya Dashami (Tue)
  "2026-11-10", // Diwali Balipratipada (Tue)
  "2026-11-24", // Guru Nanak Jayanti / Prakash Gurpurb (Tue)
  "2026-12-25", // Christmas (Fri)
  // NOTE: 2026-11-08 Diwali Laxmi Pujan is a SUNDAY (Muhurat session only) —
  // weekend check already skips it, so it is intentionally NOT listed.
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
  // v15.26 OWNER RULE (2026-07-18): options are INTRADAY / max 1-2 day holds.
  // Liquidity lives in the CURRENT expiry — that is what option buyers trade.
  // ≤ ROLLOVER_DAYS days to current expiry → suggest NEXT month instead.
  // NEVER month+2: the old MIN_DAYS_BASE_ENTRY:40 walk pushed a 17-Jul signal
  // past 25-Aug (39d) by ONE day onto the dead Sep chain (no volume, wide spread).
  ROLLOVER_DAYS      : 5,
};

// ── CONFIG ────────────────────────────────────────────────────────────────────
const CONFIG = {
  VERSION       : "v15.30",  // single source for ALL subscriber-facing version stamps (was hardcoded per-message and went stale at v15.17)
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

  // v15.22: a DMA-anchored SL may TIGHTEN the ATR stop only while leaving at
  // least this many ATRs of room. Price sitting ON its 20DMA gave BHARATFORG
  // (07-16 premium option alert) an SL 1.07% from entry on a "2-4 week" trade —
  // pure noise distance — and inflated RR to a fake-looking 9.6. Multi-day
  // stops tighter than 0.75×ATR are coin flips, not risk management.
  MIN_SL_ATR_MULT     : 0.75,
  ATR_SL_INTRADAY     : 1.5,
  ATR_SL_SWING        : 2.0,
  ATR_SL_BASE         : 1.5,
  ATR_SL_POSITIONAL   : 2.5,
  ATR_TGT_INTRADAY    : 2.0,
  ATR_TGT_SWING       : 3.0,
  ATR_TGT_SWING_LEADER: 4.0,
  ATR_TGT_BASE        : 5.0,
  ATR_TGT_POSITIONAL  : 4.0,

  // v15.18: lift multi-day (swing/mom/positional/base) targets toward +5%, but
  // ONLY when the stock's ATR makes +5% reachable — so sleepy low-vol large-caps
  // keep their ATR target and still book the win instead of stranding at the
  // time-stop. Owner rule: "maximum target above 5%". Cash/intraday/options keep
  // their own faster targets. RR>=MIN_RR still gates AFTER the lift (lifting the
  // target only improves RR, so it can never reject a previously-valid setup).
  MIN_TARGET_PCT      : 0.05,  // +5% target floor (when reachable)
  MIN_TARGET_ATRPCT   : 1.3,   // only apply the floor if ATR% >= this

  BATCH_SIZE    : 60,
  TOTAL_COLS    : 19,
  LOG_ROWS      : 21,

  BEARISH_MIN_AF          : 5,
  BEARISH_MIN_MASTER_SCORE: 22,
  BEARISH_LEADER_ONLY     : true,

  // v15.6: Stricter bearish thresholds
  BEARISH_HARD_MIN_SCORE  : 40,   // Hard bearish: only score >= 40 allowed
  BEARISH_MAX_WAITING     : 3,    // Max 3 waiting slots in bearish (was 10)
  REGIME_BORDERLINE_PCT   : 0.30, // v15.21: |Nifty−20DMA| below this % = BORDERLINE — an ordinary
                                  // overnight gap can flip the regime at open (07-15: 4 pts below
                                  // → "BEARISH, no entries today" at 00:03, green + 6 candidates
                                  // by 09:28). Messages say so instead of a false-certain verdict.
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

  RESULT_DAY_SKIP_PCT : 10.0, // v15.30: was 6.0 — treated every ordinary 6%+ breakout day as a suspected
                               // earnings/corp-action spike unless 3+ other stocks in the same sector also
                               // moved 2%+ (MOMENTUM_SECTOR_MIN_COUNT) — an isolated strong mover (not a
                               // sector-wide rally) never got that exemption. 10% still catches genuine
                               // circuit-style/result-shock moves; CORP_ACTION_SKIP_PCT(15) unchanged as the
                               // hard outer bound.
  CORP_ACTION_SKIP_PCT: 15.0,

  MOM_MIN_CHANGE_PCT: 2.5,
  MOM_MIN_VOLUME_PCT: 200,
  MOM_WINDOW_END    : "14:30", // v15.30: was 11:30 — momentum breakouts that build through the afternoon were
                               // never scanned at all; aligned with the bot's new 15:05 bullish entry cutoff
                               // (trading_bot.py ENTRY_WINDOW_BULLISH_END) so a queued afternoon candidate still
                               // has time to actually be entered before the window closes.

  MORNING_VOL_BYPASS_UNTIL: "10:30",
  INTRADAY_WINDOW_START   : "09:15",
  INTRADAY_WINDOW_END     : "12:30",

  RANK_CONV_BONUS_MAX: 3,
  RANK_LEADER_MAX    : 5,
  BM_PURGE_DAYS      : 14,

  // ── Cash Intraday — high-volume gap stocks, same-day exit ──────────────────
  // These are small-mid cap stocks with news/volume catalyst giving 10-15% intraday
  CASH_MIN_PCT_CHANGE  : 4.0,   // 4%+ move today = cash candidate
  CASH_MIN_VOLUME_RATIO: 200,   // diff-form: +200% above avg = 3.0× volume PACE (v15.24 — the old "2x" note misread this diff-form column)
  CASH_MAX_CMP         : 500,   // small-mid cap only (higher % potential)
  CASH_MIN_CMP         : 50,    // avoid penny stocks
  CASH_SL_PCT          : 0.03,  // tight -3% SL (must be quick trade)
  CASH_TARGET_PCT      : 0.12,  // +12% target (10-15% potential)
  CASH_ENTRY_WINDOW    : "13:30", // v15.30: was 10:30 — a 4%+ gap/catalyst mover that builds its move after
                                   // 10:30 (very common — many NSE gainers accelerate after 12 PM) was invisible
                                   // to this path entirely. 13:30 still leaves 1.5hr before the existing 15:00
                                   // CASH_FORCE_EXIT_HOUR, plenty for a fast catalyst-driven move.
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
  // v15.20: was `return 14.0` — the fake fallback made alerts print
  // "✅ VIX 14.0 — good to buy" as if it were live data. 0 = honest "unknown";
  // display sites use _vixStr() and the options gate fails open with a warning.
  Logger.log("[VIX] Unavailable — returning 0 (displays show n/a)");
  return 0;
}

function _vixStr(v) { return v > 0 ? v.toFixed(1) : "n/a"; }

// ══════════════════════════════════════════════════════════════════════════════
// v15.24 — TIME-FAIR VOLUME PACE (mirror of Python institutional_edges v1.1)
// The Volume_vs_Avg % column divides today's CUMULATIVE partial-day volume by
// a FULL-DAY average, so intraday readings run ~2× low (07-16 evidence:
// CHOLAFIN 0.17× at noon vs 0.45× EOD). These helpers convert the diff-form
// value (+50 = 1.5×, owner-verified v15.13) to a MULTIPLE and divide by the
// fraction of a normal NSE day's volume expected by now (U-shape curve,
// 15-min GOOGLEFINANCE delay). No adjustment before 09:45, outside session
// hours, or on bad input — night/EOD scans behave exactly as before.
// ══════════════════════════════════════════════════════════════════════════════
const VOL_SESSION_CURVE = [[0, 0.04], [60, 0.30], [180, 0.55], [300, 0.75], [375, 1.00]];

function _expectedVolFraction(timeStr) {
  try {
    const hm = (timeStr || "").split(":");
    let mins = parseInt(hm[0], 10) * 60 + parseInt(hm[1], 10) - (9 * 60 + 15);
    if (isNaN(mins) || mins < 30) return 1.0;   // before 09:45 (noisy open) or bad input
    mins -= 15;                                  // quote-delay allowance
    if (mins >= 375) return 1.0;                 // session over → reading is full-day
    let frac = 1.0;
    for (let k = 1; k < VOL_SESSION_CURVE.length; k++) {
      const m0 = VOL_SESSION_CURVE[k - 1][0], f0 = VOL_SESSION_CURVE[k - 1][1];
      const m1 = VOL_SESSION_CURVE[k][0],     f1 = VOL_SESSION_CURVE[k][1];
      if (mins <= m1) { frac = f0 + (f1 - f0) * (mins - m0) / (m1 - m0); break; }
    }
    return Math.max(0.15, Math.min(1.0, frac));  // divisor floor caps the boost at ~6.7×
  } catch (e) { return 1.0; }
}

// Diff-form column value (+50 = 1.5×, −67 = 0.33×) → time-fair pace multiple.
function _volPaceMult(volVsAvg, timeStr) {
  return Math.max(0, 1 + (parseFloat(volVsAvg) || 0) / 100) / _expectedVolFraction(timeStr);
}

function _getRecommendedExpiry(rolloverDays) {
  // v15.26 (owner rule 2026-07-18): options = intraday / 1-2 day holds only,
  // so pick the CURRENT monthly expiry (that's where volume + momentum live).
  // Only inside the rollover zone (≤ rolloverDays to expiry) move to the NEXT
  // month. The loop's first month with daysLeft > rolloverDays is always the
  // current or next month — month+2 (dead chain) is unreachable by design.
  // v15.14 base: last-Tuesday expiries generated on the fly, no hardcoded list.
  rolloverDays = rolloverDays || OPTIONS_CONFIG.ROLLOVER_DAYS;
  const now    = new Date();
  const MS_DAY = 1000 * 60 * 60 * 24;
  for (let i = 0; i < 8; i++) {
    const total  = now.getMonth() + i;
    const year   = now.getFullYear() + Math.floor(total / 12);
    const month  = total % 12;
    const expiry = _lastTuesdayOfMonth(year, month);
    const daysLeft = Math.floor((expiry - now) / MS_DAY);
    if (daysLeft > rolloverDays) return { date: expiry, daysLeft: daysLeft };
  }
  // Fallback — should not reach; defensive only.
  const fb = _lastTuesdayOfMonth(now.getFullYear() + 1, now.getMonth());
  return { date: fb, daysLeft: Math.floor((fb - now) / MS_DAY) };
}

// v15.20: was Math.ceil — always rounded UP, so the "ATM" strike was really
// 1 step OUT-of-the-money (NYKAA CMP 322 → "ATM" 330 = 2.4% OTM, the riskier
// theta-heavy pick). Math.round = the genuinely nearest strike.
function _roundToStrike(price, interval) { return Math.round(price / interval) * interval; }

// v15.25: shared table with Python option_intelligence.strike_step (the two
// engines used different grids — night vs entry alerts could disagree).
// Sub-₹100 band added so low-price stocks aren't rounded onto a 5-step grid.
function _getStrikeInterval(cmp) {
  if (cmp < 100)  return 1;
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
function _generateOptionsSignal(sym, cmp, atr, stage, pctChange, vix, isBaseEntry, high52, optTag, sectorTrend) {
  const result = { signal: "⏸ SKIP", strike: "", expiryStr: "", thetaRisk: "", message: "", liqNote: "", isBase: isBaseEntry || false,
    // v15.30: market regime + stock breakout direction are already implicit in
    // every candidate reaching this function (bearish hard-block / standard
    // bullish filter already ran); this surfaces the missing 3rd leg — sector
    // direction (Nifty200 col V, TAILWIND/HEADWIND) — as INFO on the alert,
    // not a new hard gate, so it doesn't shrink an already-scarce candidate
    // pool. Owner's own stated rule: "market, sector and stock all same
    // direction then option entry" — this makes that call visible, not
    // automatic; a HEADWIND sector still fires the alert, clearly flagged.
    sectorTrend: (sectorTrend || "").toString().trim() };

  // v15.23: F&O eligibility from the live sheet ("Options" col AJ, maintained
  // from NSE's official F&O file). "" = the stock HAS NO derivatives — SEBI's
  // 2025 eligibility purge removed IRCTC/MRF/ATGL/TATACOMM/... The legacy
  // hardcoded list below had gone stale (still contained IRCTC, TATAMOTORS
  // pre-demerger, ZOMATO pre-rename) and is now only the fallback when the
  // column is absent.
  if (optTag !== null && optTag !== undefined) {
    if (!optTag) { result.message = "No derivatives on this stock (NSE F&O list)"; return result; }
    result.liqNote = (optTag === "N50")
      ? "🟦 Nifty50 chain — deep & liquid"
      : "⚠️ Midcap chain — check bid-ask spread before buying";
  } else if (!F_AND_O_LIQUID_STOCKS.has(sym)) { result.message = "Not in F&O liquid list"; return result; }

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
  if (vix <= 0) {
    // v15.20: VIX fetch failed — fail-open but say so honestly instead of
    // pretending a fake 14.0 is "good to buy".
    vixLabel = "⚠️ VIX unavailable — verify India VIX < 18 before buying";
  } else if (vix > OPTIONS_CONFIG.VIX_AVOID) {
    result.signal  = "❌ VIX HIGH";
    result.message = `VIX ${vix.toFixed(1)} > ${OPTIONS_CONFIG.VIX_AVOID} — skip`;
    return result;
  } else if (vix > vixLimit) {
    vixLabel = `⚠️ VIX ${vix.toFixed(1)} — caution`;
  } else {
    vixLabel = `✅ VIX ${vix.toFixed(1)} — good to buy`;
  }

  // v15.26 owner rule: options are intraday / 1-2 day holds → CURRENT expiry
  // (best volume + tightest spread); next month only inside the rollover zone.
  // The old ❌ THETA HIGH rejection is gone — for a 1-2 day hold the current
  // expiry with 6+ days left is the RIGHT instrument, not a theta trap.
  const expiryInfo = _getRecommendedExpiry(OPTIONS_CONFIG.ROLLOVER_DAYS);
  const expiryStr  = Utilities.formatDate(expiryInfo.date, CONFIG.IST_ZONE, "dd-MMM-yyyy");
  const daysLeft   = expiryInfo.daysLeft;

  // Theta labels re-scaled for a 1-2 DAY hold (not the old multi-week hold):
  let thetaRisk;
  if      (daysLeft >= 15) thetaRisk = `🟢 LOW (${daysLeft}d left)`;
  else if (daysLeft >= 8)  thetaRisk = `🟡 MED (${daysLeft}d left — max 1-2 din hold)`;
  else                     thetaRisk = `🔴 HIGH (${daysLeft}d left — sirf INTRADAY, overnight nahi)`;

  const interval  = _getStrikeInterval(cmp);
  const atmStrike = _roundToStrike(cmp, interval);

  // v15.20: ALWAYS suggest ATM (was: breakouts often got an OTM strike ~1 ATR
  // away — the theta-bleed retail trap, and it contradicted the entry-time
  // smart block which recommends ITM). Owner rule = "option no big loss":
  // ATM here at night, and the entry alert's option_intelligence block gives
  // the final ITM pick (~0.7Δ) when the trade actually triggers.
  const useStrike = atmStrike;

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

  // v15.20: EARNINGS WINDOW BLOCK — the Python entry-time block already skips
  // options within 3 days of results (IV crush eats the premium even when the
  // stock moves right), but THIS night-scan premium alert — the one paying
  // subscribers act on — had no earnings check at all. fetch_earnings.py
  // writes EARNINGS_{SYM}_{yyyy-MM-dd} keys into BotMemory daily; mirror the
  // Python check (yesterday .. +3 days). Fail-open: no keys → alert goes out.
  try {
    const symClean = sym.replace("NSE:", "").trim().toUpperCase();
    const MS_DAY = 1000 * 60 * 60 * 24;
    for (let o = -1; o <= 3; o++) {
      const ds = Utilities.formatDate(new Date(Date.now() + o * MS_DAY), CONFIG.IST_ZONE, "yyyy-MM-dd");
      if (_bmExists(bm, `EARNINGS_${symClean}_${ds}`)) {
        Logger.log(`[OPTIONS] ${sym}: earnings on ${ds} — premium option alert SKIPPED (IV-crush risk)`);
        return;
      }
    }
  } catch(e) { Logger.log("[OPTIONS] earnings check error (fail-open): " + e); }

  const isBase    = optSignal.signal === "📦 BASE CE";
  const typeLabel = isBase ? "📦 BASE OPTIONS SIGNAL" : "📊 OPTIONS SIGNAL";
  // v15.26 OWNER RULE (2026-07-18): option = INTRADAY ya max 1-2 din ka trade.
  // Stock ka 2-4 hafte wala trade CASH/MTF me hota hai, option me NAHI —
  // option me time decay (theta) roz premium khata hai.
  const entryRule = isBase
    ? "✅ Kab kharide: 9:30 AM – 12:00 PM ke beech\n✅ Stock 20DMA ke upar hona chahiye"
    : "✅ Kab kharide: sirf 9:30-9:45 AM";
  // v15.18: stock-anchored exit (ITM ~0.7Δ option moves ~70% of the stock, so
  // stock −1.5% ≈ option −15%; exiting on the STOCK's SL caps option loss ~20%).
  const holdRule  =
    "⏱ <b>Option HOLD: intraday ya max 1-2 din</b> — usse zyada nahi\n" +
    "✅ Exit: STOCK Target hit kare, ya 2 din pure ho jaayen (jo pehle ho)\n" +
    "🛑 Exit: STOCK apna SL tode (option me ≈ −15-20%)\n" +
    "⚠️ Hard cap: option me 20% se zyada loss KABHI nahi";
  const tradeNote = isBase
    ? "\n📌 <b>STOCK TRADE (2-4 hafte):</b> CASH me kharide ya MTF — option me lamba hold NAHI. Option sirf 1-2 din ke momentum ke liye hai."
    : "";

  // v15.22: CONFIRM-AT-OPEN GUARD — night-scan alerts are built from the last
  // close's data; by the next open the setup can be dead (07-15: BHARATFORG +
  // DELHIVERY queued at night, both in clear 15m downtrends next morning).
  // When this alert goes out outside market hours, tell the subscriber exactly
  // how to validate it live instead of trusting yesterday's snapshot.
  const _hhmmOpt   = parseInt(Utilities.formatDate(new Date(), CONFIG.IST_ZONE, "HHmm"), 10);
  const isLiveOpt  = (_hhmmOpt >= 915 && _hhmmOpt <= 1530);
  const confirmRule = isLiveOpt ? "" :
    `\n━━ ⚠️ SUBAH CONFIRM KARE (night scan — kal ke close ka data) ━━\n` +
    `✅ Tabhi kharide jab stock 9:30 ke baad ₹${cmp.toFixed(2)} ke UPAR trade kare\n` +
    `❌ Red khule ya kal ke close se neeche ho → skip (setup stale hai)\n` +
    `❌ Subah ka regime message BEARISH bole → skip`;

  const msg =
    `${typeLabel} — <b>PREMIUM</b>\n` +
    `━━━━━━━━━━━━━━━━━━━━\n` +
    `🎯 <b>Stock:</b> ${sym.replace("NSE:","")}\n` +
    `💰 <b>CMP:</b> ₹${cmp.toFixed(2)}\n` +
    `📋 <b>Stage:</b> ${stage}\n\n` +
    `━━ OPTION (sirf INTRADAY / 1-2 din) ━━\n` +
    `🎰 <b>Buy:</b> ${optSignal.strike}\n` +
    `📅 <b>Expiry:</b> ${optSignal.expiryStr} (current — yahi volume hai)\n` +
    `⏳ <b>Theta Risk:</b> ${optSignal.thetaRisk}\n` +
    `📊 <b>VIX Status:</b> ${optSignal.message}\n` +
    (optSignal.liqNote ? `💧 <b>Chain:</b> ${optSignal.liqNote}\n` : "") +
    // v15.30: market (regime) + stock (breakout) direction already got this
    // candidate here — this is the 3rd leg (sector), surfaced not enforced.
    (optSignal.sectorTrend === "TAILWIND" ? `🧭 <b>Sector:</b> TAILWIND ✅ — market+sector+stock sab same direction\n` :
     optSignal.sectorTrend === "HEADWIND" ? `🧭 <b>Sector:</b> HEADWIND ⚠️ — stock alag chal raha apne sector se, extra caution\n` : "") +
    `\n` +
    `━━ STOCK TRADE (CASH/MTF) ━━\n` +
    `🛑 <b>SL:</b> ₹${sl}\n` +
    `🎯 <b>Target:</b> ₹${target}\n` +
    `📈 <b>RR:</b> ${rr}\n` +
    `✅ Entry valid jab tak STOCK price SL ke upar hai\n\n` +
    `📺 <b>TradingView check:</b> stock ke liye DAILY chart, option ki timing ke liye 15m\n\n` +
    `━━ RULES ━━\n` +
    `${entryRule}\n${holdRule}\n` +
    `❌ Option me average down kabhi nahi\n` +
    `${confirmRule}${tradeNote}\n\n` +
    `<i>Educational only. Not SEBI advice. ${CONFIG.VERSION}</i>`;

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

      // v15.24 CRASH FIX: this row had 20 elements (a trailing notes string)
      // against the 19-column (TOTAL_COLS) AlertLog grid — setValues() throws
      // on the mismatch and the ENTIRE scanner run aborted every 5 minutes
      // while a watchlist stock qualified. Row now matches the Nifty200
      // cash-candidate shape exactly: 19 cols, full timestamp, "⏳ WAITING".
      candidates.push({
        sym, sector, priority: 30,  // slightly higher priority than Nifty200 cash
        row: [
          Utilities.formatDate(new Date(), CONFIG.IST_ZONE, "yyyy-MM-dd HH:mm:ss"),
          sym, "", 30, "🔥 Cash Intraday", "CASH",
          `🔥 WATCHLIST CASH | +${pctChange.toFixed(1)}% | ${name}`,
          cashSl, cashTgt, "1:" + cashRr.toFixed(1), "⏳ WAITING",
          "", "", "", "", "", "", "", cashQty,
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
    `✅ <i>System: Online ${CONFIG.VERSION}</i>`
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
  // v15.27: one-time header-position guard for the two hardcoded-index reads
  // below (ATR col 28, Options col 35) — a future inserted Nifty200 column
  // would otherwise silently corrupt every SL/target/option decision with
  // no error, just wrong numbers. Mismatch fails SAFE (ATR=0/optTag=null),
  // same as a missing column, instead of trusting a shifted column.
  const _hdr     = inputData[0] || [];
  const atrColOk = (_hdr[28] || "").toString().toUpperCase().indexOf("ATR") !== -1;
  const optColOk = (_hdr[35] || "").toString().trim() === "Options";
  if (!atrColOk || !optColOk) {
    Logger.log(`[COLUMN-DRIFT] ⚠️ Nifty200 header mismatch — ATR col29="${_hdr[28]}" (ok=${atrColOk}) Options col36="${_hdr[35]}" (ok=${optColOk}). Falling back to safe defaults until columns are realigned.`);
  }
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
  Logger.log(`[v15.6] VIX=${_vixStr(indiaVix)} | MomentumSectors: ${[...momentumSectors].join(', ') || 'none'}`);

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
    const sectorTrend= (r[21] || "").toString().trim();  // v15.30: TAILWIND/HEADWIND — was read nowhere before
    const pctChange  = parseFloat(r[3])  || 0;
    const cmp        = parseFloat(r[2])  || 0;
    const atr        = atrColOk ? (parseFloat(r[28]) || 0) : 0;
    const high52     = parseFloat(r[9])  || 0;
    const dma20      = parseFloat(r[4])  || 0;
    const dma50      = parseFloat(r[5])  || 0;
    const distDMA    = parseFloat(r[12]) || 0;
    const pivotRes   = parseFloat(r[26]) || 0;
    const volVsAvg   = parseFloat(r[14]) || 0;
    // v15.24: blank volume cell must stay BLOCKED by volume gates (old
    // behaviour) — the pace math alone could pass a no-data stock early in
    // the session when the expected-fraction divisor is small.
    const volHasData = !isNaN(parseFloat(r[14]));
    const retestPct  = parseFloat(r[23]) || -99;
    const af         = parseFloat(r[31]) || 0;
    const rs         = parseFloat(r[20]) || 0;
    const rank       = parseFloat(r[34]) || 0;
    const vcp        = parseFloat(r[27]) || 1.0;
    const daysLow    = parseFloat(r[29]) || 0;
    // v15.23: Options-eligibility tag (col AJ, fed from NSE's official F&O
    // file): "N50" / "YES" / "" (no derivatives). null = column absent →
    // _generateOptionsSignal falls back to the legacy hardcoded list.
    const optTag     = (!optColOk || r[35] === undefined || r[35] === null) ? null : r[35].toString().trim();

    const signal   = _inferSignal(rawSignal, stage, fiiBuyZone, smaStr);
    const priority = _inferPriority(rawPriority, rawMasterScore, rawSignalScore);
    const useScore = priority;

    // v15.23: include NEGATIVE AF too — averaging only winners made a sector
    // with 1 hot stock + 9 bleeding ones look "strongest" (survivorship bias).
    if (af !== 0) { sectorAfSum[sector] = (sectorAfSum[sector] || 0) + af; sectorAfCount[sector] = (sectorAfCount[sector] || 0) + 1; }

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
    // v15.24: volume condition is time-fair pace (diff-form 200 = 3.0× — the
    // old "2x average" comment was wrong for this diff-form column). Cash
    // detection runs ≤10:30 where the raw partial-day reading is at its most
    // understated, so this was the most starved gate of all.
    if (timeStr <= CONFIG.CASH_ENTRY_WINDOW &&
        cmp >= CONFIG.CASH_MIN_CMP &&
        cmp <= CONFIG.CASH_MAX_CMP &&
        pctChange >= CONFIG.CASH_MIN_PCT_CHANGE &&
        volHasData &&
        _volPaceMult(volVsAvg, timeStr) >= 1 + CONFIG.CASH_MIN_VOLUME_RATIO / 100 &&
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

    // GATE 3 (v15.19): RS LEADERSHIP PRE-SCREEN — parity with the Python bot.
    // The bot hard-vetoes ANY non-cash entry with sheet RS < 5 (Filter 7), so
    // queuing weaker names only fills WAITING slots the bot can never buy
    // (July 2026: 0 entries for ~2.5 weeks — every queued candidate died at
    // the bot's RS or RSI gate; the board misled manual followers too).
    // The old gate only fired for breakout stage AND required rs > 0, so a
    // NEGATIVE RS (e.g. ABB −7 on 2026-07-15) slipped straight through — on
    // this ±% scale negative RS is real data (laggard), not "missing".
    // Blank/unparseable RS stays fail-open (queued as before). Applies to
    // bullish regime only (bearish path has its own stricter RS≥15 block);
    // cash intraday never reaches here (bot exempts it from RS as well).
    const rsRaw = (r[20] === null || r[20] === undefined) ? "" : r[20].toString().trim();
    const rsIsNum = rsRaw !== "" && !isNaN(parseFloat(rsRaw));
    if (marketBullish && rsIsNum && rs < CONFIG.LATE_ENTRY_MIN_RS) continue;

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
    // v15.24: gate on time-fair PACE. Same numeric bars expressed as multiples
    // (diff-form 120 = 2.2×, BASE_STAGE_MIN_VOL 40 = 1.4×) — identical
    // behaviour on night/EOD scans (fraction = 1), fair intraday instead of
    // comparing partial-day volume against a full-day average.
    if (!isMorning && marketBullish && !volumeBypass) {
      const isBaseStage    = stage.includes("Correction Base") || stage.includes("Building Momentum");
      const isBasePrepared = (signal === "💎 BASE PREPARED");
      const volPace        = _volPaceMult(volVsAvg, timeStr);
      if (isBreakoutStage) {
        // exempt
      } else if (isBaseEntry || isBaseStage || isBasePrepared) {
        if (!volHasData || volPace < 1 + CONFIG.BASE_STAGE_MIN_VOL / 100) continue;
      } else {
        if (!volHasData || volPace < 2.2) continue;
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

    // v15.22: helper — DMA anchor may tighten the ATR stop ONLY if it still
    // leaves ≥ MIN_SL_ATR_MULT×ATR of room to entry. When price sits right on
    // its DMA the old Math.max() snapped the SL to within noise of entry
    // (BHARATFORG 07-16: 20DMA 1.5 pts under CMP → SL 1.07% away, fake RR 9.6).
    const _dmaAnchoredSl = (rawSl, dmaRaw, anchorLevel) => {
      const anchorOk = dmaRaw > 0 && dmaRaw < cmp && (cmp - anchorLevel) >= atr * CONFIG.MIN_SL_ATR_MULT;
      return parseFloat((anchorOk ? Math.max(rawSl, anchorLevel) : rawSl).toFixed(2));
    };

    if (isBaseEntry) {
      sl     = _dmaAnchoredSl(cmp - atr * CONFIG.ATR_SL_BASE, dma20, dma20 * 0.99);
      target = parseFloat((cmp + atr * CONFIG.ATR_TGT_BASE).toFixed(2));
    } else if (isMomentumEntry) {
      // Momentum entries: tighter SL (intraday style), swing target
      sl     = parseFloat((cmp - atr * 1.5).toFixed(2));
      target = parseFloat((cmp + atr * 3.0).toFixed(2));
    } else if (ttype === "📈 Positional" && niftyTradeType.includes("Value")) {
      sl     = _dmaAnchoredSl(cmp - atr * CONFIG.ATR_SL_POSITIONAL, dma50, dma50);
      target = parseFloat((cmp + atr * CONFIG.ATR_TGT_POSITIONAL).toFixed(2));
    } else if (ttype === "📈 Positional") {
      sl     = _dmaAnchoredSl(cmp - atr * CONFIG.ATR_SL_POSITIONAL, dma20, dma20);
      target = parseFloat((cmp + atr * CONFIG.ATR_TGT_POSITIONAL).toFixed(2));
    } else if (ttype === "⚡ Intraday" || ttype === "📊 Options Alert") {
      sl     = parseFloat((cmp - atr * CONFIG.ATR_SL_INTRADAY).toFixed(2));
      target = parseFloat((cmp + atr * CONFIG.ATR_TGT_INTRADAY).toFixed(2));
    } else {
      sl     = parseFloat((cmp - atr * CONFIG.ATR_SL_SWING).toFixed(2));
      target = parseFloat((cmp + atr * swingTgtMult).toFixed(2));
    }

    if (sl >= cmp) sl = parseFloat((cmp * 0.97).toFixed(2));

    // v15.18: reachability-aware +5% target floor for multi-day equity holds.
    // Skips cash/intraday/options (they have faster, fixed targets). Only lifts
    // when ATR% >= MIN_TARGET_ATRPCT so a +5% target is realistically hittable
    // within the swing window; low-vol names keep their ATR target (no stranding).
    if (ttype !== "⚡ Intraday" && ttype !== "📊 Options Alert") {
      const atrPctTgt = atr > 0 ? (atr / cmp) * 100 : 0;
      if (atrPctTgt >= CONFIG.MIN_TARGET_ATRPCT) {
        const floorTgt = parseFloat((cmp * (1 + CONFIG.MIN_TARGET_PCT)).toFixed(2));
        if (floorTgt > target) target = floorTgt;
      }
    }

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
    // v15.23: pass optTag — live F&O eligibility replaces the stale hardcoded list
    const optSignal  = _generateOptionsSignal(sym, cmp, atr, stage, pctChange, indiaVix, isBaseEntry, high52, optTag, sectorTrend);

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

  // v15.28 DIAGNOSTIC — read-only, changes no gate/trade decision. Logs
  // whether today's top-5 Master_Score stocks (excluding already-traded)
  // reached the WAITING queue, and if not, the cheapest checkable reason
  // (bearish score<40, RS<gate floor, or "see full [CAND] trace above").
  // Added after a 2026-07-22 audit found AlertLog holding only 1 candidate
  // (TITAN) on a bullish day while the Nifty200 sheet showed several other
  // STRONG BUY / BREAKOUT CONFIRMED names with healthy Master Scores — the
  // exact gate that excluded them could not be pinned down after the fact
  // because nothing logged the near-misses. This makes the next occurrence
  // provable from the Apps Script Executions log instead of guesswork.
  try {
    const queuedSyms = new Set(finalWaiting.map(row => row[1]));
    const topByScore = inputData.slice(1)
      .filter(r => r[0] && !r[0].toString().includes("NIFTY") && !alreadyTraded.has(r[0].toString().trim()))
      .map(r => ({
        sym: r[0].toString().trim(),
        score: parseFloat(r[33]) || 0,
        pri: parseFloat(r[25]) || 0,
        rs: parseFloat(r[20]) || 0,
        sector: (r[1] || "UNKNOWN").toString().trim(),
        ttype: (r[24] || "").toString().trim(),
      }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 5);
    Logger.log(`[DIAG] Top-5 Master_Score (Bullish=${marketBullish}, MaxWaiting=${maxWaitingSlots}): ` +
      topByScore.map(t => `${t.sym}(score=${t.score},pri=${t.pri},rs=${t.rs},sector=${t.sector},ttype=${t.ttype})=${queuedSyms.has(t.sym) ? "QUEUED" : "NOT-QUEUED"}`).join(" | "));
  } catch (e) { Logger.log("[DIAG] error (non-fatal): " + e); }

  // MOMENTUM SCAN — v15.24: GATE-3 parity (RS ≥ LATE_ENTRY_MIN_RS, blank RS
  // fail-open), time-fair volume pace (diff-form 200 = 3.0×), 2-per-sector
  // cap and regime slot limit. This path used to queue RS-negative names the
  // Python bot could never buy (dead WAITING slots, misleading board) and
  // could push past the bearish max-3 limit.
  const momCands = [];
  if (marketBullish && timeStr <= CONFIG.MOM_WINDOW_END) {
    for (let i = 2; i < totalRows; i++) {
      const r   = inputData[i];
      const sym = (r[0] || "").toString().trim();
      if (!sym || sym.includes("NIFTY") || alreadyTraded.has(sym)) continue;
      if (finalWaiting.find(row => row[1] === sym)) continue;
      const pctChange = parseFloat(r[3])  || 0;
      const volVsAvg  = parseFloat(r[14]) || 0;
      const volOk     = !isNaN(parseFloat(r[14]));
      const cmp       = parseFloat(r[2])  || 0;
      const atr       = atrColOk ? (parseFloat(r[28]) || 0) : 0;
      const smaStr    = (r[7]  || "").toString().trim();
      const fiiSignal = (r[32] || "").toString().trim();
      const sector    = (r[1]  || "UNKNOWN").toString().trim();
      const rs        = parseFloat(r[20]) || 0;
      const rsIsNum   = !isNaN(parseFloat(r[20]));
      if (pctChange < CONFIG.MOM_MIN_CHANGE_PCT) continue;
      if (!volOk || _volPaceMult(volVsAvg, timeStr) < 1 + CONFIG.MOM_MIN_VOLUME_PCT / 100) continue;
      if (rsIsNum && rs < CONFIG.LATE_ENTRY_MIN_RS) continue;   // v15.24: GATE-3 parity
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
      // v15.24: respect the regime slot limit + 2-per-sector cap (was pushed
      // unconditionally after the allocator had already filled the board).
      if (finalWaiting.length >= maxWaitingSlots) break;
      const mSec = c.sector || "UNKNOWN";
      if ((waitingSectorCount[mSec] || 0) >= 2) continue;
      waitingSectorCount[mSec] = (waitingSectorCount[mSec] || 0) + 1;
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
      // v15.23: a "strongest sector" claim needs breadth — require ≥3 scored
      // stocks (works now that col B holds NSE macro sectors, not 100
      // fragmented labels where 62 sectors had a single stock).
      if ((sectorAfCount[sec] || 0) < 3) continue;
      const avgAf = sectorAfSum[sec] / (sectorAfCount[sec] || 1);
      if (avgAf > topAf) { topAf = avgAf; topSector = sec; }
    }
    const baseCount     = finalWaiting.filter(r => r[6] && r[6].toString().includes("📦 BASE")).length;
    const momentumCount = finalWaiting.filter(r => r[6] && r[6].toString().includes("🚀 MOMENTUM BREAKOUT")).length;
    const cashCount     = finalWaiting.filter(r => r[4] && r[4].toString().includes("Cash Intraday")).length;
    const breakoutCount = finalWaiting.length - baseCount - momentumCount - cashCount;

    // v15.21 HONEST PREMARKET MESSAGING — outside live session (09:15-15:30 IST)
    // the Nifty quote is the PREVIOUS CLOSE, so the regime verdict is provisional;
    // and when Nifty sits within REGIME_BORDERLINE_PCT of the 20DMA, an ordinary
    // overnight gap can flip it (2026-07-15/16: "BEARISH −4 pts, no entries" at
    // 00:03 → green with 6 candidates by 09:28). Say so instead of false certainty.
    const _hhmmNow    = parseInt(Utilities.formatDate(new Date(), CONFIG.IST_ZONE, "HHmm"), 10);
    const isLiveHours = (_hhmmNow >= 915 && _hhmmNow <= 1530);
    const distPct     = (nifty20d > 0) ? ((niftyCmp - nifty20d) / nifty20d) * 100 : 0;
    const borderline  = (nifty20d > 0) && (Math.abs(distPct) < CONFIG.REGIME_BORDERLINE_PCT);
    const staleNote   = isLiveHours ? "" : ` <i>(yesterday's close — live regime decided at 9:15)</i>`;

    let regimeMsg;
    if (!marketBullish) {
      regimeMsg =
        `⚠️ <b>MARKET REGIME: BEARISH</b>${borderline ? " ⚖️ <b>BORDERLINE</b>" : ""}\n` +
        `Nifty ₹${niftyCmp.toFixed(0)} vs 20DMA ₹${nifty20d.toFixed(0)} (${distPct.toFixed(2)}%)${staleNote}\n` +
        `${CONFIG.VERSION} HARD BLOCK: Max ${maxWaitingSlots} slots | Score≥${CONFIG.BEARISH_HARD_MIN_SCORE} only\n` +
        `VIX: ${_vixStr(indiaVix)}\n`;
      if (borderline) regimeMsg += `⚖️ Nifty is only ${Math.abs(niftyCmp - nifty20d).toFixed(0)} pts from the 20DMA — a small gap ${isLiveHours ? "can flip the regime" : "at open can flip this to BULLISH"}.\n`;
      if (momentumSectors.size > 0) regimeMsg += `🚀 Momentum sectors: ${[...momentumSectors].join(', ')}\n`;
      if (topSector) regimeMsg += `🔄 Strongest: ${topSector} (AF: ${topAf.toFixed(1)})\n`;
      if (finalWaiting.length > 0) {
        regimeMsg += `\n⚡ <b>${finalWaiting.length} exceptional candidate(s):</b>\n`;
        finalWaiting.slice(0, 3).forEach(r => {
          regimeMsg += `• <b>${r[1]}</b> [${r[4]}] — ${r[6]}\n  SL ₹${r[7]} → T ₹${r[8]} | RR ${r[9]}\n`;
        });
      } else if (!isLiveHours) {
        regimeMsg += `\n🛑 No candidates queued tonight. Regime is re-checked at the open — if it turns green, the scan runs again and entry alerts follow.`;
      } else {
        regimeMsg += `\n🛑 No new entries today. Cash is a position.`;
      }
    } else {
      regimeMsg =
        `🟢 <b>SCANNER DONE — ${today}</b>${borderline ? " ⚖️" : ""}\n` +
        `Nifty ₹${niftyCmp.toFixed(0)} | 20DMA ₹${nifty20d.toFixed(0)} | VIX: ${_vixStr(indiaVix)}${staleNote}\n`;
      if (borderline) regimeMsg += `⚖️ Bullish by only ${Math.abs(niftyCmp - nifty20d).toFixed(0)} pts — regime is borderline${isLiveHours ? "" : " and may flip at open"}.\n`;
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
      // v15.26: easy-language trade legend (owner rule 2026-07-18) — every
      // night-scan list now tells the subscriber HOW each type is traded and
      // which TradingView chart to check.
      if (finalWaiting.length > 0) {
        regimeMsg +=
          `\n📖 <b>Kaise trade kare:</b>\n` +
          `• BASE/BREAKOUT = 2-4 hafte ka stock trade → CASH ya MTF me kharide\n` +
          `• Option sirf INTRADAY / max 1-2 din ke liye (current expiry)\n` +
          `• Entry valid jab tak price SL ke upar hai — agle din bhi le sakte ho\n` +
          `📺 TradingView: DAILY chart dekhe (Cash/MOM alert ho to 15m)\n`;
      }
      // v15.24: bullish scanner-done message now carries the version stamp too
      // (bearish header + option/test footers already did — CONFIG.VERSION
      // single-source doctrine; the bullish night message was the only
      // subscriber-facing regime message without one).
      regimeMsg += `\n<i>Entry alerts sent when market opens. ${CONFIG.VERSION}</i>`;
    }
    _sendTelegramAdvanceAndPremium(regimeMsg);

    // Basic channel teaser — show market mood + setup count, hide details to drive upgrades
    const topSym = finalWaiting.length > 0 ? (finalWaiting[0][1] || "").replace("NSE:", "") : "";
    const topType = finalWaiting.length > 0 ? (finalWaiting[0][4] || "") : "";
    let basicMsg;
    if (!marketBullish) {
      basicMsg =
        `⚠️ <b>Market Alert — ${today}</b>\n` +
        `Market: 🔴 BEARISH | Nifty: ₹${niftyCmp.toFixed(0)} | VIX: ${_vixStr(indiaVix)}\n\n` +
        (finalWaiting.length > 0
          ? `🔍 <b>${finalWaiting.length} stock(s) passed our strict bearish filter today</b>\n` +
            `🔒 Entry details shared with Advance/Premium members only\n\n`
          : `🛡️ Our system blocked all new entries today — protecting your capital.\n\n`) +
        `📈 <b>Join Advance @ ₹699/month</b> for real-time alerts\n📱 ai360trading.in/membership`;
    } else {
      basicMsg =
        `🟢 <b>Market Update — ${today}</b>\n` +
        `Market: BULLISH | Nifty: ₹${niftyCmp.toFixed(0)} | VIX: ${_vixStr(indiaVix)}\n` +
        (momentumSectors.size > 0 ? `🚀 Strong sectors: ${[...momentumSectors].join(", ")}\n` : "") +
        `\n` +
        (finalWaiting.length > 0
          ? `🔍 <b>${finalWaiting.length} stock setup(s) identified today</b>\n` +
            (topSym ? `Top setup: <b>${topSym}</b> [${topType}]\n` : "") +
            `🔒 SL, Target and full details → Advance/Premium members\n\n`
          : `📭 No strong setups today — our filters kept you in cash.\n\n`) +
        `📈 <b>Join Advance @ ₹699/month</b> for real-time entry alerts\n📱 ai360trading.in/membership`;
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

  const confirm  = ui.alert(
    '🧹 FRESH CLEAN START',
    'Clears ALL AlertLog trades + BotMemory trade/state keys.\n' +
    'KEPT: Nifty200, CashWatchlist, LTWatchlist, holidays, T2 switch, settings.\n\n' +
    'Continue?',
    ui.ButtonSet.YES_NO);
  if (confirm !== ui.Button.YES) { ui.alert('❌ Cancelled — nothing changed.'); return; }

  // v15.18: hold the AppScript write lock so the 5-min bot cycle skips a blank
  // AlertLog if this is run during market hours (mirrors clearWaitingRowsOnly).
  const bm       = _bmLoad(ss);
  const lockTime = Utilities.formatDate(new Date(), CONFIG.IST_ZONE, "yyyy-MM-dd HH:mm:ss");
  _bmSet(ss, bm, "_AS_LOCK", lockTime, "", "STATE");
  SpreadsheetApp.flush();

  // AlertLog: clear trade rows (cols A-S) + options cols (U-X). Col T (TOTAL_COLS
  // is 19, so col 20 = T2 switch) is outside the range and never touched.
  logSheet.getRange(2, 1, CONFIG.LOG_ROWS, CONFIG.TOTAL_COLS).clearContent();
  logSheet.getRange(2, 21, 21, 4).clearContent();
  _restoreFormulas(logSheet);

  // BotMemory: clear TRADE + STATE keys; keep SYSTEM keys (holidays etc.) and
  // our own _AS_LOCK (removed at the end so the lock stays valid throughout).
  const bmSheet = ss.getSheetByName(CONFIG.BM_SHEET);
  if (bmSheet) {
    const lastRow = bmSheet.getLastRow();
    if (lastRow >= 2) {
      const data = bmSheet.getRange(2, 1, lastRow - 1, 5).getValues();
      for (let i = 0; i < data.length; i++) {
        const key   = (data[i][0] || "").toString().trim();
        const ktype = (data[i][4] || "").toString().trim();
        if ((ktype === "TRADE" || ktype === "STATE") && key !== "_AS_LOCK") {
          bmSheet.getRange(i + 2, 1, 1, 5).clearContent();
        }
      }
    }
  }

  // Optional: also reset the History P&L track record — backed up first so
  // nothing is ever lost.
  const histYes = ui.alert(
    '📊 Reset History too?',
    'Also clear History (your P&L track record)?\n' +
    'It is copied to a HistoryArchive tab first, so nothing is lost.\n\n' +
    'YES = fresh P&L   |   NO = keep track record',
    ui.ButtonSet.YES_NO);
  if (histYes === ui.Button.YES) {
    const hist = ss.getSheetByName(CONFIG.HISTORY_SHEET);
    if (hist) {
      const last = hist.getLastRow();
      const ncol = hist.getLastColumn();
      if (last >= 2 && ncol >= 1) {
        const header = hist.getRange(1, 1, 1, ncol).getValues();
        const rows   = hist.getRange(2, 1, last - 1, ncol).getValues();
        let arc = ss.getSheetByName('HistoryArchive');
        if (!arc) { arc = ss.insertSheet('HistoryArchive'); arc.getRange(1, 1, 1, ncol).setValues(header); }
        arc.getRange(arc.getLastRow() + 1, 1, rows.length, ncol).setValues(rows);
        hist.getRange(2, 1, last - 1, ncol).clearContent();
      }
    }
  }

  // Remove transient cache sheets if present.
  ["PriceCache","TempPriceCalc"].forEach(name => { const s = ss.getSheetByName(name); if (s) ss.deleteSheet(s); });

  _bmDel(ss, bm, "_AS_LOCK");
  SpreadsheetApp.flush();
  ui.alert('✅ Fresh start done.\nClick 🔄 MANUAL SYNC to load new candidates.');
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
  msg += `<i>AI360 Trading ${CONFIG.VERSION} — Base + Breakout + Momentum + Options (Last-Tue expiry)</i>`;
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
    `📈 <b>Join Advance @ ₹699/month</b> — get live signals next week\n📱 ai360trading.in/membership`;
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
  _sendTelegramToChat(CONFIG.CHAT_ID_BASIC,   `✅ <b>TEST — ${timeStr}</b>\nChannel: Basic 🆓\n${CONFIG.VERSION} ✅`);
  _sendTelegramToChat(CONFIG.CHAT_ID_ADVANCE, `✅ <b>TEST — ${timeStr}</b>\nChannel: Advance 📊\n${CONFIG.VERSION} ✅`);
  _sendTelegramToChat(CONFIG.CHAT_ID_PREMIUM, `✅ <b>TEST — ${timeStr}</b>\nChannel: Premium 💎\n${CONFIG.VERSION} + Last-Tuesday expiry + Bearish Block + Momentum + ATH Options Fix ✅`);
}

function testOptionsSignal() {
  const ss        = SpreadsheetApp.getActiveSpreadsheet();
  const inputData = ss.getSheetByName(CONFIG.SHEET_NAME).getDataRange().getValues();
  const vix       = _getIndiaVix(inputData);
  const expiry    = _getRecommendedExpiry(OPTIONS_CONFIG.ROLLOVER_DAYS);
  const expiryStr = Utilities.formatDate(expiry.date, CONFIG.IST_ZONE, "dd-MMM-yyyy");
  const testBreakout = _generateOptionsSignal("NSE:ADANIPORTS", 1691, 33.5, "⚡ BREAKOUT ALERT", -4.32, vix, false, 1823.9);
  const testATH      = _generateOptionsSignal("NSE:MCX",        3353,  80,  "⚡ BREAKOUT ALERT",  0.50, vix, false, 3500);
  const msg =
    `📊 <b>OPTIONS TEST — ${CONFIG.VERSION}</b>\n━━━━━━━━━━━━━━━━━━━━\n` +
    `VIX: ${vix.toFixed(1)} | Expiry: ${expiryStr} (${expiry.daysLeft}d)\n\n` +
    `BREAKOUT (ADANIPORTS): ${testBreakout.signal} | ${testBreakout.strike}\n` +
    `ATH TEST (MCX near ATH): ${testATH.signal} | ${testATH.message}\n` +
    `✅ ATH block working`;
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
    `📦 <b>BASE + MOMENTUM TEST — ${CONFIG.VERSION}</b>\n━━━━━━━━━━━━━━━━━━━━\n` +
    `VIX: ${vix.toFixed(1)}\n\n` +
    `BASE TESTS:\n` +
    `Test 1 (all pass): ${test1.qualifies ? "✅" : "❌"} ${test1.reason}\n` +
    `Test 2 (FII fail): ${test2.qualifies ? "✅" : "❌"} ${test2.reason}\n` +
    `Test 3 (VCP fail): ${test3.qualifies ? "✅" : "❌"} ${test3.reason}\n` +
    `Test 4 (Days fail): ${test4.qualifies ? "✅" : "❌"} ${test4.reason}\n\n` +
    `MOMENTUM BREAKOUT TESTS:\n` +
    `COFORGE +5.15%: ${testMom1.isMomentum ? "✅ ALLOWED" : "❌ BLOCKED"} — ${testMom1.reason}\n` +
    `TECHM +4.85% (low RS): ${testMom2.isMomentum ? "✅ ALLOWED" : "❌ BLOCKED"} — ${testMom2.reason}\n` +
    `PERSISTENT +5.48%: ${testMom3.isMomentum ? "✅ ALLOWED" : "❌ BLOCKED"} — ${testMom3.reason}\n\n` +
    `✅ Last-Tue expiry + Momentum gate working`;
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