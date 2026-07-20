"""
AI360 TRADING BOT — v15.28
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v15.28 CHANGES vs v15.27 — VOLUME-GATE SHADOW TRACKER (2026-07-21, owner: "may be we have any hard gate... build it, safe by design only")
  The 1.5x volume-confirmation gate is a binary hard gate with no partial
  credit — never measured against what actually happens to the candidates
  it rejects. New ShadowLedger tab + 3 functions (log_volume_gate_shadow,
  score_volume_gate_shadow, shadow_ledger_report): every candidate that
  passes EVERY other filter (RECD/TIME/DAILY/NIFTY/VIX/RSI/RS) and fails
  ONLY on volume gets logged as a never-traded phantom entry (same SL/
  target a real entry would use), then scored later with the same target/
  SL/TIME_STOP_DAYS rules real trades use. New BOT_MODE=shadow_report
  sends an on-demand plain-language summary. SAFE BY DESIGN: reads/writes
  ONLY the ShadowLedger tab, never touches AlertLog/History/BotMemory
  trade-state, never sends a trade alert, never affects a real position —
  every function fails open independently of the real entry/exit path.

v15.27 CHANGES vs v15.26 — FULL-SYSTEM AUDIT FIXES (2026-07-20, owner: "analyse full system, find loop or gap")
  1. Removed dead ACCUM_{date}_{key} memory write in the accumulation-watch
     scan — nothing ever read it, and clean_mem()'s date-detection didn't
     recognize its shape (starts "ACCUM_", not a date), so it was silently
     permanent instead of pruned after 14 days. Pure deletion, zero callers.
  2. _read_atr_from_nifty200 / _read_opt_tag_from_nifty200 now use the
     existing header-name lookup (_find_nifty200_col) instead of hardcoded
     row[28]/row[35] — a future inserted Nifty200 column would otherwise
     silently corrupt ATR-based SL/target math and option gating with no
     error. Same fix mirrored in appscript.gs v15.27 (header-position guard,
     fails safe to 0/null on mismatch instead of trusting a shifted column).
  3. Doc-only: stale "12-day" comment near the option ledger time-stop skip
     now correctly says OPTION_MAX_TDAYS=2 (was superseded by v15.26 but the
     comment wasn't updated); BUY_PE removed from the option-action docstring
     (PE path has been dead/buy-side-only since 2026-06-05).

v15.26 CHANGES vs v15.25 — OPTIONS = INTRADAY/1-2 DAY ONLY + EASY-LANGUAGE ALERTS (2026-07-18, owner rule)
  Owner's trading structure (stated 2026-07-18): options are bought for
  INTRADAY or max 1-2 day momentum only — never held for the stock's 2-4
  week move (that is traded in CASH/MTF; theta eats a long option hold).
  1. OPTION_MAX_TDAYS=2 replaces OPTION_BASE_MAX_TDAYS=12 — ALL option-type
     ledger rows now exit after 2 trading days if target not hit (the alert
     says "intraday ya max 1-2 din"; ledger follows the alert, v15.25
     doctrine). 20% est-loss cap + expiry-week backstop unchanged.
  2. Entry alerts (advance+premium) carry _trade_style_lines(): how to take
     the trade (CASH/MTF for swing, CASH for intraday cash, accumulate for
     positional), "Entry valid jab tak price SL ke upar hai", and which
     TradingView chart to cross-check (DAILY swing / 15m cash / WEEKLY pos).
  3. Option blocks (smart + fallback) state the 1-2 day hold rule and that
     the CURRENT expiry is used (liquidity). Companion: appscript v15.26
     picks current expiry (rollover ≤5d → next month, never month+2 — the
     old 40-day minimum put a 17-Jul signal on the dead Sep chain).

v15.25 CHANGES vs v15.24 — OPTION LEDGER FOLLOWS THE ALERT'S OWN RULES (2026-07-17, owner: "fix the last remaining ledger item")
  The paper ledger monitored OPTION-type trades under generic STOCK rules
  (5-day time stop, −5% stock hard loss) while the premium alert tells
  subscribers OPTION rules — the EICHERMOT option trade was closed by a
  time stop the alert never mentioned (ledger-vs-alert honesty gap, open
  since 2026-07-15). Option-type rows in step_b now exit per the alert:
    • 🛑 20% ESTIMATED-LOSS HARD CAP (🔒 owner risk rule) — est option P/L
      (premium-aware leverage, v15.24) ≤ −20% exits BEFORE the wider stock
      SL can bleed further (flat-10× fallback ⇒ cap at stock −2%).
    • ⏰ EXPIRY WEEK EXIT — "Do NOT hold past expiry week": exit when ≤5
      calendar days to the col-W expiry.
    • ⏰ BASE 12-TRADING-DAY RULE — the alert's own BASE TRADE NOTE: exit
      after 12 trading days if target not hit.
  Stock-anchored SL/TSL/target checks unchanged (the alert states those
  too); generic time stop now SKIPPED for option trades — unless the expiry
  cell doesn't parse, in which case it stays as the fail-open backstop so a
  bad cell can never mean "hold forever". Leverage logic unified in
  _row_option_leverage (step_b cap + exit note use the same number).

v15.24 CHANGES vs v15.23 — KNOWN-ITEMS PACK (2026-07-17 late evening, owner: "fix the 3 known items also")
  1. STRIKE GRID UNIFIED — the CE fallback path had a THIRD divergent strike
     table (5/10/20/50). Now identical to option_intelligence v1.3 strike_step
     AND appscript v15.25 _getStrikeInterval: <100→1, <250→5, <500→10,
     <1000→20, <2000→50, ≥2000→100 (the coarser grid — a coarse multiple is
     always a real strike when NSE's finer spacing divides it).
  2. PREMIUM-AWARE OPTION P/L — the exit note's flat 10× leverage guess is
     replaced by option_intelligence.est_option_leverage (Δ·S/premium at
     entry, Brenner–Subrahmanyam time value, clamp 5-20×) whenever the
     sheet's Strike (col V) + Expiry (col W) parse and HV is available;
     any missing piece → flat 10× exactly as before. Display only — numeric
     ledger columns keep the stock P/L, label shows the multiplier used.
  (3. Same session: fetch_earnings v1.2 maps BSE long names → real NSE
     symbols via the official EQUITY_L.csv — the first-token keys mostly
     matched nothing, so BSE-sourced earnings coverage was largely dead.)

v15.23 CHANGES vs v15.22 — FULL-AUDIT BUG PACK (2026-07-17 evening, owner: "fix all")
  1. RSI HOT-LEADER EXCEPTION REVIVED — day_pct came ONLY from `_LP_` memory,
     which is written at entry promotion / while monitoring a TRADED row and
     cleared on exit — a fresh WAITING candidate NEVER had it, so day_pct was
     always None → fail-closed → the calibrated v15.20 exception (RSI 65-75
     leaders up on the day) never actually fired. day_pct now falls back to the
     live Nifty200 "%Change" column (the same value the scanner reads as r[3]).
     Same root fix revives: the 6% result-day gap guard at entry (prev_close=0
     meant it was skipped for every fresh entry) and the ≥3% price bypass on
     the volume gate. `_LP_` still preferred when present (exact prev close).
  2. v15.9 BUG-E ACTUALLY FIXED — cash entries also wrote `{date}_ENTRY_{key}`
     and the counter's `not startswith(date_CASH_)` filter could never exclude
     an `_ENTRY_` part, so cash trades STILL consumed the 3/day swing budget on
     the next tick. `_ENTRY_` is now written for swing entries only.
  3. RELVOL HEURISTIC HOLE CLOSED — Volume_vs_Avg % is diff-form (+50 = 1.5×),
     but raw values in (0,5] were returned AS multiples (+3% above avg read as
     "3.0× huge") and values in (−5,0] fell through to fail-open. Now ALL
     numeric values convert 1+raw/100; only a blank/unparseable cell fails open.
  4. TIME STOP ON TRADING DAYS — was calendar days (a Wed entry hit "5 days" by
     Mon = 3 sessions; winners cut ~2 days early over weekends). New
     calc_trading_hold_days (weekends + NSE holidays excluded) used for the
     time stop; min-hold and ledger "days held" deliberately stay calendar
     (no change to live trailing behaviour). trading_days_since (RECD cooldown)
     now also skips holidays.
  5. SHEETS-QUOTA FIX — _read_atr_from_nifty200/_read_opt_tag_from_nifty200 now
     use the per-tick _nifty200_rows cache (each call was a full-sheet fetch),
     and the best-of ranking computes each candidate's score ONCE (was up to 3×
     per row: sort key + filter + log line → 15+ full-sheet reads in seconds →
     silent 429 fallback that disabled best-first ranking on busy mornings).
  6. NIFTY ROW VERIFIED — get_market_regime/get_nifty_pct_change assumed row 2
     is the index row; now verified by symbol ("NIFTY"), with a fallback scan,
     so a future row shift can't silently make the regime "some stock vs its
     own 20DMA".
  7. EARNINGS BLOCK REWIRED — option_intelligence looked for EARNINGS_* keys in
     the _RUNTIME_MEM string, but fetch_earnings.py writes them as BotMemory
     ROWS → the entry-time option earnings block was permanently fail-open.
     bm_data (the BotMemory dict) is now passed through ce_candidate_flag →
     recommend_option → check_earnings_window.
  8. clean_mem truncation now drops oldest DATED flags first and protects
     active-trade state keys (TSL/MAX/LP/ATR/RECD) — the old "keep last 100
     parts" could drop a live trade's trailing stop.
  9. Version stamps unified via VERSION constant (banner + test messages were
     stale at v15.16).

v15.22 CHANGES vs v15.21 — REAL F&O ELIGIBILITY FOR OPTION SUGGESTIONS (2026-07-17, owner-approved)
  • New Nifty200 col AJ "Options" (fed from NSE's official F&O file): "N50" /
    "YES" / "" (no derivatives — SEBI's 2025 purge removed IRCTC/MRF/ATGL/
    TATACOMM/...). ce_candidate_flag now HARD-SKIPS the CE block when the tag
    says the stock has no derivatives (an impossible trade was being suggested),
    and annotates chain liquidity (Nifty50 = deep; midcap = check spread).
    Tag unreadable → fail-open (old behavior), never blocks on a data hiccup.
  • Same-day companion fix: col AC is now a REAL ATR(14) via fetch_rs v2.0
    (the old sheet formula returned a single day's high−low).

v15.21 CHANGES vs v15.20 — TIME-FAIR VOLUME GATE (2026-07-16, owner-approved)
  First market day after v15.20 had ZERO entries again: all 4 queued
  candidates (GMRAIRPORT 99, CHOLAFIN 84, LAURUSLABS 59, TORNTPHARM) were
  blocked every tick by the [VOL] 1.5× gate, then time-blocked after 14:30.
  Root cause: Volume_vs_Avg_% divides today's CUMULATIVE partial-day volume
  by a FULL-DAY ~3-month average, so intraday readings run ~2× low
  (CHOLAFIN read 0.17× at noon vs 0.45× actual EOD; GMRAIRPORT 0.40× at
  10:54 vs 0.94× EOD). Demanding a raw 1.5× before the 14:30 cutoff is
  near-impossible on normal days → structural entry starvation.
  Change: the [VOL] call now passes the IST clock; institutional_edges v1.1
  divides the raw reading by the expected session-volume fraction (NSE
  U-shape curve + 15-min quote-delay allowance) and gates on 1.5× PACE.
  The 1.5× threshold itself is UNCHANGED; no adjustment before 09:45,
  after close, or if data/clock is missing (falls back to raw = old
  behaviour). The ≥3% price bypass and 0.0 fail-open are untouched, and
  the raw (unadjusted) relvol is still what reversal-risk/climax ranking
  sees. One measurement made time-fair — nothing else touched.

v15.20 CHANGES vs v15.19 — CALIBRATED RSI HOT-LEADER EXCEPTION (2026-07-15)
  Owner-approved after a data study of all 13 closed trades (entry-day RSI /
  volume / close-strength reconstructed via yfinance):
  • NOT ONE loser entered overbought — losers' entry RSI was 37-62, so the
    RSI>65 hard veto (v15.10) never prevented a single actual loss.
  • 3 of the 6 target-hit winners entered at RSI 65-82 (BSE 73.3, IDEA 82.3,
    ADANIPORTS 65.4), and NYKAA — which the owner traded MANUALLY for a real
    profit on 2026-07-15 — was refused by the bot at RSI 72.7. The veto was
    blocking exactly the explosive-momentum winner profile.
  • The RS≥5 leadership gate was ALSO validated by the same study (all 6
    target winners pass, 2 of 5 losers correctly blocked) — it is UNTOUCHED.
  Change: in a BULLISH regime, RSI 65..RSI_HOT_MAX(75) no longer hard-blocks
  IF the stock is up on the day (cp > yesterday's close from `_LP_` memory —
  buying strength, not a fading bounce). Fail-CLOSED when day-change data is
  missing; RSI > 75 remains a hard block (climax chase); bearish regime
  unchanged (58 hard cap). One condition relaxed, with guards — no other
  filter, SL, target, trailing or alert logic touched.

v15.19 CHANGES vs v15.18 — DEAD SAFETY-FILTER DATA FEEDS REVIVED (2026-07-15)
  Live-log analysis found TWO protective entry filters silently dead for every
  tick (both fail-open by design, so they always said "entry allowed"):
  1. NIFTY DIRECTION VETO — Nifty200!D2 (NIFTY50 %Change) has NO formula (cell
     is empty; only stock rows got the changepct formula), and the yfinance
     fast_info fallback returns nothing on GitHub runners WITHOUT raising — so
     nifty_pct was 0.00 every tick and the red-day veto (NIFTY_MIN_PCT_BULLISH
     -0.30) could NEVER fire. Fixed twice: D2 got a real GOOGLEFINANCE changepct
     formula (sheet-side), and get_nifty_pct_change() gained a .history()-based
     fallback — the same yfinance call get_rsi() uses, proven working on CI.
  2. INDIA VIX FILTER — get_india_vix() used the same silently-empty fast_info,
     so VIX was 0.0 every tick ("VIX unavailable — entry allowed") and the
     panic-day gate (VIX_MAX 22) could never fire. Same .history() fallback.
  No entry math, SL, trailing, ranking or alert behaviour touched. Both feeds
  stay fail-open (any error → 0.0 → entry allowed), exactly as before — they
  just actually carry data now.

v15.18 CHANGES vs v15.17 — HISTORY ENTRY-DATE FIX (2026-07-13)
  Bug found in full-system audit: _exit_trade wrote today_str (the EXIT date)
  into BOTH the "Entry Date" AND "Exit Date" columns of the History sheet, so
  every closed trade showed Entry Date == Exit Date (e.g. ANGELONE entry
  2026-06-22 / exit 2026-06-22 / Days Held 6 — impossible). The real entry
  timestamp (ent_time, from AlertLog col M) was already available in the same
  function — it drives Days Held — but was never used for the date column.
  Now Entry Date = date part of ent_time (fail-open: falls back to today_str
  if ent_time is missing/unparseable). Display/ledger only — no trading logic,
  entry math, SL, trailing or alert behaviour touched.

v15.17 CHANGES vs v15.16 — RESISTANCE-ROOM VETO + LOSS COOLDOWN (2026-07-12)
  Owner ask (2-month live-trade audit before going to real money): the losing
  trades ALL shared one tell — price moved only +0.2% to +0.7% above entry then
  stalled/reversed (no follow-through), and EICHERMOT was bought TWICE pinned
  right under the same ~₹7440 ceiling. Two surgical, fail-open fixes:
  1. RESISTANCE-ROOM VETO — a fresh long is skipped when the clean runway to the
     next resistance (Pivot_Resistance, in ATR multiples via entry_quality.
     target_room) is below MIN_TARGET_ROOM_ATR (1.5). target_room was computed
     for ranking since v15.15 but NEVER enforced as a gate — now it is. Only
     fires when resistance data exists AND price is below it; a genuine breakout
     ABOVE resistance (room→0.0) or missing data is never blocked (fail-open).
  2. LOSS COOLDOWN — the re-entry cooldown (v15.0) fired ONLY after a TARGET HIT.
     A losing exit set no cooldown, so the bot could immediately re-buy a name
     that just failed (EICHERMOT lost, then was re-entered and lost again). Now
     any losing exit sets the same proven RECD cooldown too.
  3. CASH ROOM VETO — cash intraday gap-trades bypassed ALL filters (allowed =
     cp>0). They now also run the fail-open resistance-room veto so a cash entry
     isn't bought right under a ceiling. Still skip RSI/Nifty/time (gap-driven).
  NOT changed: entry math, SL multiples, trailing logic, appscript — untouched.

v15.16 CHANGES vs v15.15 — WEEKEND-GAP GUARD + OPTION-BASED P/L (2026-06-05)
  Owner ask (audit follow-up): limit weekend gap losses (e.g. PNBHOUSING −6.86%
  blew past its −3.38% SL on a Monday gap-down) and show the REAL option P/L on
  option trades (stock P/L understates it).
  1. WEEKEND-GAP GUARD — on Friday's close summary, append a per-position
     weekend advisory (book partial on winners, EXIT laggards before close —
     2 shut days can gap a stock past its stop). Signal-only; no exit-logic
     change. New-entry side was already blocked after 2 PM Friday (existing).
  2. OPTION-BASED P/L — for 📊 Options Alert trades, the exit Telegram + the
     History "Options Note" column now show an estimated option-premium P/L
     (stock move × OPTION_LEVERAGE_EST≈10 for an ITM ~0.7Δ option), clearly
     labelled "(est.)". Numeric ledger columns keep the stock P/L unchanged.

v15.14 CHANGES vs v15.13 — H2-2026 HOLIDAY CORRECTION (2026-05-30)
  Aug-Dec 2026 holidays were approximations and materially wrong (Diwali was
  guessed at 21/22-Oct; actual Balipratipada is 10-Nov; Ganesh Chaturthi 14-Sep
  and Dussehra 20-Oct were missing; Janmashtami 27-Aug was not an NSE holiday).
  Same bug-class that caused the 2026-05-27 outage. Now VERIFIED against NSE
  official circular + Zerodha + ClearTax (all three agree). appscript.gs H2
  list corrected identically in the same session.

v15.13 CHANGES vs v15.12 — BATCH-4 HOTFIX + BATCH-5 SCAFFOLDING (May 2026)
  HOTFIX 4.1 — Nifty200 column lookups were broken by header-name mismatch.
    From Amit ji's screenshot 8 the actual header is `Volume_vs_Avg_%` (a
    percentage form: +50 → 1.5×, −67 → 0.33×), and Relative Strength is
    in a column literally named `RS`. v15.12 keyword lookup (`relvol/rvol`)
    silently missed both — volume filter was ALWAYS failing open since
    deploy. Fixed:
      • _find_nifty200_col now does EXACT match first (protects short
        headers like `RS` from false-hit on `Pivot_Resistance`), then
        substring fallback.
      • _read_nifty200_relvol now matches `Volume_vs_Avg_%` exactly AND
        converts percentage form (|raw|>5) to multiple internally.
      • New _read_nifty200_rs uses the pre-computed `RS` column from
        the sheet — more accurate than computing from prev_close.
      • RS gate prefers sheet value; falls back to math only if column
        missing.

  BATCH-5 NOTE — Small/Mid Cap scanner is delivered as a STANDALONE
    fetcher (`fetch_smallmidcap.py` v1.0) with its own daily cron.
    Output: new `SmallMidCap` sheet tab (auto-created), BotMemory SMC_*
    keys, Telegram digest. No changes to trading_bot.py monitor flow —
    auto-trade on small caps is deferred to Batch 6 (higher volatility,
    needs explicit approval per Amit ji 2026-05-27: "few signals, long
    ride, max momentum profit, no loss tolerance").

v15.12 CHANGES vs v15.11 — BATCH 4 INSTITUTIONAL EDGES (May 2026)
  Five "smart money" filters consistently-profitable traders + FIIs use.
  Each is a soft-gate added to check_all_entry_filters; every one fails
  open if its data source is unavailable (per free_forever_self_repair).

  1. RELATIVE STRENGTH — entry requires `stock_pct − nifty_pct ≥ 1.0%`.
     A stock not even keeping up with Nifty is not a leader. Uses cp +
     mem `_LP_` (yesterday's close) + already-fetched nifty_pct. No new
     network call.

  2. VOLUME CONFIRMATION — entry requires today's relative-volume ≥ 1.5×.
     Reads the column already populated by the AppScript scanner in
     Nifty200 sheet (`_read_nifty200_value` → "RelVol" column). Volume
     IS institutional footprint; price moves without volume rarely hold.

  3. FII REGIME GATE — for LONG entries, block if today's FII cash net
     ≤ −₹2000 Cr (heavy outflow). Mirror rule for shorts. Uses
     MKT_FII_CASH_NET_<date> + MKT_FII_REGIME already populated by
     fetch_fii_dii.py daily.

  4. PCR SOFT FILTER — Put-Call Ratio extremes are logged but DON'T block
     (PCR extremes are contrarian, not directional). Reads MKT_PCR_NIFTY
     newly populated by fetch_bhavcopy.py.

  5. DELIVERY % — entry requires DLV_{SYM} ≥ 40% (institutional accumulation
     vs day-jobbing). Reads NEW DLV_* keys from fetch_bhavcopy.py.

  New files added in Batch 4:
    • institutional_edges.py v1.0 — the five checks (pure functions)
    • fetch_bhavcopy.py v1.0      — NSE bhavcopy + option-chain fetcher
    • .github/workflows/fetch_bhavcopy.yml — daily 20:00 IST cron

  Architecture (same pattern as Batch 3):
    • institutional_edges import wrapped in try/except — bot survives if
      module missing or broken (falls back to v15.11 filter set).
    • Each filter individually wrapped so one buggy check cannot cascade.
    • Filters added AFTER existing v15.10 filters (RSI, VIX, Nifty dir) so
      removing the new module simply removes Batch-4 gates without
      affecting older behaviour.

v15.11 CHANGES vs v15.10 — BATCH 3 OPTION-BUYING INTELLIGENCE (May 2026)
  Five upgrades to convert the bot from "options as gimmick" to actual
  edge-trading on options. All free, all self-healing — no paid feeds.

  1. SMART ITM STRIKE — was: scanner picked ATM or 1-strike OTM (high theta,
     low delta). Now: option_intelligence.compute_itm_strike() picks 1-2
     strikes ITM (Δ≈0.65–0.75) so the option moves like the stock and theta
     decay is survivable. NSE strike-step table built in (1/2/5/10/20/50/100).
     Sheet keeps scanner's original pick for record; Telegram alert uses smart.

  2. HV-BASED IV FILTER — was: no volatility check; bot suggested CE on days
     when premium was already 80th percentile rich. Now: 20-day annualised
     historical volatility via yfinance is used as IV proxy. Blocks new
     CE/PE if HV > 55% (premium too expensive to make money). Fails open
     if yfinance returns nothing — entry allowed.

  3. STOCK-ANCHORED EXIT — was: "exit if option −40% OR stock hits SL" —
     stock at SL means loss is already 100%+ on the option. Now: SL is
     stock −1.5% which equates to ≈ −15% on a Δ0.7 option — exit while
     there's still premium left to salvage. Target: option +50% (≈ stock +5%).

  4. PE FOR BEARISH — was: `if not is_bullish: return ""` — bot skipped
     options entirely in bearish regime, leaving money on the table during
     correction phases. Now: bearish regime + sell signal = BUY_PE on a
     2-strike ITM put with same risk discipline.

  5. EARNINGS WINDOW BLOCK — was: bot suggested CE the day before results
     = lottery ticket (70% lose to IV crush). Now: reads BotMemory
     EARNINGS_{SYM}_{DATE} keys (populated by fetch_earnings.py — to be
     added in Batch 3b). Within ±3 trading days → SKIP. Today's behaviour:
     no cache yet → fails open (no block) until fetch_earnings.py runs.

  Architecture note — per feedback_free_forever_self_repair memory:
    All option logic lives in a NEW MODULE option_intelligence.py so it
    can be improved/extended without touching trading_bot core. Every
    external call (yfinance HV, BotMemory earnings read) fails open;
    a single API failure cannot stall a tick.

v15.10 CHANGES vs v15.9 — BATCH 2 PROFIT PROTECTION (May 2026)
  GOAL: zero / minimal loss on losers, full-ride trail with profit lock on winners.
  Five upgrades inspired by what consistently-profitable swing traders actually do.

  1. ONE-R BREAKEVEN — was: BE activates at fixed % (e.g. STD = +2.0%).
     Now: BE activates at +1R where R = (entry − initial SL). If a stock has a
     tight 1.2% initial SL the BE moves in at +1.2% (not +2%) so we never give
     back more than the initial risk. Old fixed-% threshold kept as a hard cap
     (never activates LATER than before) so behaviour can only improve.

  2. CHANDELIER TRAIL — was: trail SL = current_price − atr*mult (anchored to
     CMP — so a sharp gap-down before bot tick could lower the trail).
     Now: trail SL = max_price_reached − atr*mult (anchored to highest price
     since entry — true Wilder/Le Beau Chandelier exit). TSL can ONLY rise.
     Locks in larger share of unrealised gains on parabolic runs.

  3. PARTIAL BOOK @ +5% — was: all-or-nothing exit; trade rides full position
     until target/TSL/SL fires.
     Now: at +5% unrealised gain, send a one-time partial-book recommendation
     to Advance/Premium ("book 50%, trail rest"). Stored as {key}_PB1 in
     BotMemory so it fires only once per trade. Paper trading reports keep
     full position P/L (we don't tamper with sheet qty) — the alert is the
     educational signal. Live trading (Phase 4) will actually halve the qty.

  4. TIME STOP (5d / +3%) — was: no time-based exit; sideways trades tied up
     capital indefinitely.
     Now: if hold_days ≥ 5 trading days AND gain < +3%, exit "⏰ TIME STOP".
     Reason: dead capital is opportunity cost. Frees the slot for a fresher
     setup. Triggered AFTER target/TSL checks so winners are never cut early.

  5. INDIA VIX FILTER — was: no volatility regime gate; bot took entries even
     during panic days (VIX > 22).
     Now: fetch ^INDIAVIX via yfinance once per tick; block NEW entries if
     VIX > 22 (configurable VIX_MAX). Existing trades continue normal exit
     monitoring. Fails open (entry allowed) if yfinance fetch errors —
     non-fatal degradation.

  Watchlist breadth note (separate work — Batch 5):
    PositionalLatest webview shows only F&O-eligible stocks because the
    scanner universe is Nifty200. Small/mid cap winners like ALKALI +20%
    or GUJTHEM +15% never enter the universe. Adding a small/mid cap
    scanner from NSE bhavcopy is deferred to Batch 5 — separate concern.

v15.9 CHANGES vs v15.8 — BATCH 1 SAFETY FIXES (May 2026)
  CRITICAL FIX — NSE_HOLIDAYS_2026 list was WRONG. Verified against NSE
                 official holiday calendar. Specifically:
                   • 2026-05-27 (Wed) was listed but is a TRADING DAY → bot
                     skipped today, no Telegram, no target exits for
                     CUMMINSIND (+12% target hit) or HINDALCO (+6% target hit)
                   • 2026-03-25 → corrected to 2026-03-26 (Ram Navami)
                   • Added 2026-03-03 (Holi) — was missing entirely
                   • Added 2026-03-31 (Mahavir Jayanti) — was missing
                   • 2026-04-02 → corrected to 2026-04-03 (Good Friday)
                   • 2026-05-27 → corrected to 2026-05-28 (Bakri Id)
                   • 2026-06-17 → corrected to 2026-06-26 (Muharram)
                 Source: NSE official Holidays 2026 — Equities (screenshot 7).
  BUG-B FIX  — TSL changes were only stored in BotMemory; AlertLog column O
               (Trailing SL) never got the value, so AppScript + website webview
               showed "—" for all winners. Now writes TSL to column O on each
               update. Sheet update is best-effort (try/except) so failure
               does not block the in-memory TSL state.
  BUG-C FIX  — WAITING row with SL >= current price would cause instant exit
               on promotion to TRADED (e.g. MCX 2026-05-26: SL ₹3,194 set
               yesterday, today MCX -4.5% to ₹3,012 → SL > price). Now skips
               such entries with "[SETUP INVALIDATED] SL above price" log.
  BUG-E FIX  — today_entries count included _CASH_ entries, so cash intraday
               consumed swing-trade daily budget. Now filters to ONLY swing
               entries (_ENTRY_ keys, excluding _CASH_).

v15.8 CHANGES vs v15.7 — AUDIT FOLLOW-UP (May 2026)
  BUG-5 FIX — auto_maintain_sheets and monthly P&L gate were still using
              substring `flag_key in mem` checks (Batch 1 had fixed the same
              pattern in GM/MD/PM but missed these two). Switched to
              `_mem_get(mem, key)` for exact-key matching. Currently safe
              (keys are unique) but eliminates a future-bug class.

v15.7 CHANGES vs v15.6 — CRITICAL TSL EXIT BUG FIX (May 2026)
  BUG-1 FIX — step_b_monitor_trades was comparing CMP against the recomputed
              `new_tsl` (which calc_new_tsl caps at cp*0.99) instead of the
              actually-stored `cur_tsl`. Result: on a gap-down BELOW the
              activated TSL, `cp <= cp*0.99` was always False → TSL exit
              never fired. After breakeven moved cur_tsl above entry, the
              hard-loss path (-5%) also won't catch it (requires cur_tsl<ent).
              FIX: keep cur_tsl in sync after set_tsl, then compare cp vs
                   cur_tsl. Now any gap below the live TSL exits the trade.

v15.6 CHANGES vs v15.5 — DEAD CODE REMOVAL (May 2026)
  FIX 1 — Removed obsolete v15.1 Y1 cell migration code. Migration was completed
          long ago and the cleanup was running on every tick (~288 ticks/day)
          for no benefit. Saves 1 sheet read + conditional write per tick.

v15.5 CHANGES vs v15.4 — PERFORMANCE + DATA INTEGRITY (May 2026)
  FIX 1 — _exit_trade now accepts qty parameter and uses actual sheet quantity
          for pnl_rs calculation. Previously recalculated as cap//ent which
          differs from sheet qty when cmp != ent at entry time (gaps between
          AppScript scanner and Python entry). Affects History P/L accuracy.
  FIX 2 — step_a TRADED promotion: batched K:M update (1 API call instead of 3).
          Saves ~2 sec per entry × up to 8 entries = ~16 sec on morning rush.

v15.4 CHANGES vs v15.3 — DEFENSIVE FIXES (May 2026)
  FIX 1 — Cred validation: clear "GCP credentials missing" error instead of
          cryptic FileNotFoundError when secret is empty and no local fallback.
  FIX 2 — Flag-key lookups: 3 daily message dedupe checks (GM/MD/PM) were using
          substring `in` match against the comma-separated memory string. This
          was safe in practice but could false-positive on future overlapping
          prefixes. Now uses exact-key lookup via _mem_get().

v15.1 CHANGES vs v15.0 — MEMORY MIGRATED FROM Y1 TO BOTMEMORY SHEET
  Reason: AlertLog is shown as webview on ai360trading.in website.
          Y1 cell contained raw memory string visible to followers — confusing.
          All runtime state now stored in BotMemory sheet row _RUNTIME_MEM.
          AlertLog is now 100% clean for website display.

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

# v15.11 Batch 3 — option-buying intelligence module. Import is wrapped so the
# bot still runs if the file is missing (graceful degradation, self-repair).
try:
    import option_intelligence as opt_intel
    _OPT_INTEL_AVAILABLE = True
except Exception as _e:
    print(f"[BOOT] option_intelligence module unavailable: {_e} — option alerts will fall back to v15.10 ATM/OTM logic")
    opt_intel = None
    _OPT_INTEL_AVAILABLE = False

# v15.12 Batch 4 — institutional edges module (RS, volume, FII gate, PCR,
# delivery %). Wrapped identically — bot survives a missing/broken module.
try:
    import institutional_edges as inst_edges
    _INST_EDGES_AVAILABLE = True
except Exception as _e:
    print(f"[BOOT] institutional_edges module unavailable: {_e} — Batch-4 filters skipped, older filter set still active")
    inst_edges = None
    _INST_EDGES_AVAILABLE = False

# v15.15 — entry-quality scoring (reversal-risk veto, target-room, best-of
# ranking, confirmed-accumulation). Wrapped identically — bot runs without it.
try:
    import entry_quality as eq
    _EQ_AVAILABLE = True
except Exception as _e:
    print(f"[BOOT] entry_quality module unavailable: {_e} — quality scoring skipped, base logic unchanged")
    eq = None
    _EQ_AVAILABLE = False

IST       = pytz.timezone('Asia/Kolkata')
VERSION   = "v15.28"   # single source for the run banner + test messages (were stale at v15.16 before v15.23)
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
RUNTIME_MEM_KEY        = "_RUNTIME_MEM"   # key in BotMemory sheet for runtime state
MIN_HOLD_SWING         = 2
MIN_HOLD_POS           = 3
TSL_GAP_LOCK_FRAC      = 0.5

RSI_MAX_BULLISH        = 65
RSI_HOT_MAX            = 75   # v15.20: RSI 65-75 allowed in bullish regime IF stock is up today (calibrated 2026-07-15 — see check_rsi_entry)
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

# ── Batch 2 profit-protection thresholds (v15.10) ─────────────────────────────
# All tunable; default values picked from well-known professional rules.
ONE_R_BE_FLOOR_PCT       = 0.8   # never move BE in below +0.8% even if 1R is smaller
PARTIAL_BOOK_TRIGGER_PCT = 5.0   # fire one-time partial-book alert at this gain
TIME_STOP_DAYS           = 5     # exit if hold_days >= this AND gain < TIME_STOP_MIN_GAIN_PCT
TIME_STOP_MIN_GAIN_PCT   = 3.0
VIX_MAX                  = 22.0  # block new entries above this India VIX value
VIX_CALM                 = 15.0  # purely informational — for entry message

# v15.16: ITM ~0.7Δ option moves ~10× the stock in premium % terms (stock −1.5%
# ≈ option −15%, stock +5% ≈ option +50% — the same convention used across the
# option module). Used ONLY to ESTIMATE displayed option P/L; no real premium
# is tracked (paper, stock-anchored). Always shown labelled "(est.)".
# v15.24: replaced by option_intelligence.est_option_leverage whenever
# strike/expiry/HV are available; this flat value is the fallback.
OPTION_LEVERAGE_EST      = 10.0

# v15.25 — OPTION-TRADE LEDGER RULES (paper ledger now follows the ALERT's own
# stated rules instead of generic stock rules — the EICHERMOT case closed on a
# stock time-stop the alert never mentioned; 🔒 owner risk rule: "option loss
# hard-capped 20%, option exit stock-anchored"):
OPTION_LOSS_CAP_PCT      = 20.0  # exit when ESTIMATED option loss reaches 20%
OPTION_EXPIRY_EXIT_DAYS  = 5     # backstop: never hold into expiry week (≤5 calendar days to expiry)
# v15.26 (owner rule 2026-07-18): options are INTRADAY / max 1-2 day holds —
# the alert now says so, and the ledger follows the alert (v15.25 doctrine).
# Replaces OPTION_BASE_MAX_TDAYS=12 (which mirrored the OLD multi-week option
# hold wording). Applies to ALL option-type rows, not just BASE stage.
OPTION_MAX_TDAYS         = 2     # exit after 2 TRADING days if target not hit

CAPITAL_HIGH = 13000
CAPITAL_MED  = 10000
CAPITAL_STD  = 7000

# NSE OFFICIAL Trading Holidays 2026 — verified against NSE website Holidays page
# DO NOT MODIFY without cross-checking nseindia.com → Resources → Holidays.
# fetch_holidays.py (run 1 Dec each year) writes HOLIDAYS_2026/2027 to BotMemory;
# load_dynamic_holidays() unions those into NSE_HOLIDAYS_ALL on startup — but a
# correct HARDCODED baseline is essential because BotMemory may be empty on
# fresh deploy, and any wrong date here permanently blocks that trading day.
NSE_HOLIDAYS_2026 = {
    "2026-01-15",  # Municipal Corporation Election — Maharashtra (Thu)
    "2026-01-26",  # Republic Day (Mon)
    "2026-03-03",  # Holi (Tue)
    "2026-03-26",  # Shri Ram Navami (Thu)
    "2026-03-31",  # Shri Mahavir Jayanti (Tue)
    "2026-04-03",  # Good Friday (Fri)
    "2026-04-14",  # Dr. Baba Saheb Ambedkar Jayanti (Tue)
    "2026-05-01",  # Maharashtra Day (Fri)
    "2026-05-28",  # Bakri Id / Eid ul-Adha (Thu)  ← was wrongly 2026-05-27 in v15.8
    "2026-06-26",  # Muharram (Fri)  ← was wrongly 2026-06-17 in v15.8
    # Aug-Dec 2026 — VERIFIED 2026-05-30 against NSE official + Zerodha + ClearTax
    # (all three agree). Replaces the earlier approximations that were materially
    # wrong (Diwali was guessed at 21/22-Oct; actual Balipratipada is 10-Nov).
    "2026-08-15",  # Independence Day (Sat — weekend anyway; kept for clarity)
    "2026-09-14",  # Ganesh Chaturthi (Mon)
    "2026-10-02",  # Mahatma Gandhi Jayanti (Fri)
    "2026-10-20",  # Dussehra / Vijaya Dashami (Tue)
    "2026-11-10",  # Diwali Balipratipada (Tue)
    "2026-11-24",  # Guru Nanak Jayanti / Prakash Gurpurb (Tue)
    "2026-12-25",  # Christmas (Fri)
    # NOTE: 2026-11-08 Diwali Laxmi Pujan is a SUNDAY (Muhurat session only) —
    # weekend check already skips it, so it is intentionally NOT listed here.
}

# Approximate 2027 fallback — auto-updated by fetch_holidays.py every Dec 1
NSE_HOLIDAYS_2027 = {
    "2027-01-26","2027-03-26","2027-04-02","2027-04-14","2027-05-01",
    "2027-06-17","2027-08-23","2027-10-19","2027-11-07","2027-11-08",
    "2027-11-15","2027-12-25",
}

# Combined — auto-extended from BotMemory on startup (see load_dynamic_holidays)
NSE_HOLIDAYS_ALL = NSE_HOLIDAYS_2026 | NSE_HOLIDAYS_2027

TSL_PARAMS = {
    "VCP":  {"breakeven":3.0,"lock1":5.0,"trail":8.0, "atr_mult":2.0,"gap_lock":9.0},
    "MOM":  {"breakeven":2.5,"lock1":4.5,"trail":7.0, "atr_mult":1.8,"gap_lock":8.0},
    "STD":  {"breakeven":2.0,"lock1":4.0,"trail":10.0,"atr_mult":2.5,"gap_lock":8.0},
    "CASH": {"breakeven":1.5,"lock1":3.0,"trail":5.0, "atr_mult":1.5,"gap_lock":5.0},
}

# ── Cash Intraday ─────────────────────────────────────────────────────────────
CASH_ENTRY_WINDOW_END  = (10, 30)  # cash stocks: entry only 9:15-10:30 AM
CASH_FORCE_EXIT_HOUR   = (15, 0)   # force-exit all cash trades at 3:00 PM
CASH_MAX_DAILY         = 2         # max 2 cash intraday trades per day
CASH_CAPITAL           = CAPITAL_STD  # smallest tier — higher risk position

# ── Sheet Maintenance ─────────────────────────────────────────────────────────
HISTORY_MAX_ROWS       = 500       # archive History when rows exceed this
BOTMEMORY_ALERT_ROWS   = 400       # warn in logs when BotMemory exceeds this


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
def send_advance_and_premium(msg): _send_one(CHAT_ADVANCE, msg); return _send_one(CHAT_PREMIUM, msg)
def send_all(msg):                 send_basic(msg); send_advance(msg); return send_premium(msg)


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

def load_dynamic_holidays(bm_data):
    """Read HOLIDAYS_YYYY keys from BotMemory and merge into NSE_HOLIDAYS_ALL.
    fetch_holidays.py writes these every December 1st."""
    global NSE_HOLIDAYS_ALL
    year = datetime.now(IST).year
    for y in (year, year + 1):
        key = f"HOLIDAYS_{y}"
        val = bm_data.get(key, {}).get("value", "") if isinstance(bm_data.get(key), dict) else bm_data.get(key, "")
        if val:
            dates = {d.strip() for d in val.split(",") if d.strip()}
            NSE_HOLIDAYS_ALL |= dates
            print(f"[HOLIDAYS] Loaded {len(dates)} dates for {y} from BotMemory")

def is_holiday(date_str):
    return date_str in NSE_HOLIDAYS_ALL

def price_sanity(sym,cp,ent):
    if cp<=0 or ent<=0: print(f"[WARN] {sym}: zero price"); return False
    if cp > ent*4: print(f"[WARN] {sym}: LTP too high"); return False
    if cp < ent*0.1: print(f"[WARN] {sym}: LTP too low"); return False
    return True

def trading_days_since(date_str, now):
    # v15.23: NSE holidays no longer count as trading days (RECD cooldown was
    # expiring early around holiday weeks).
    if not date_str: return 999
    try:
        start=datetime.strptime(date_str,'%Y-%m-%d').date(); end=now.date(); count=0; cur=start
        while cur<=end:
            if cur.weekday()<5 and not is_holiday(cur.strftime("%Y-%m-%d")): count+=1
            cur+=timedelta(days=1)
        return max(0,count-1)
    except: return 999

def calc_trading_hold_days(entry_str, now):
    """v15.23: TRADING days held (weekends + NSE holidays excluded) — used by
    the TIME STOP, whose spec (v15.10) says trading days. Calendar-day
    calc_hold_days stays for min-hold and the ledger (unchanged behaviour)."""
    try:
        ent = datetime.strptime(str(entry_str)[:10], '%Y-%m-%d').date()
        end = now.date(); count = 0; cur = ent
        while cur <= end:
            if cur.weekday() < 5 and not is_holiday(cur.strftime("%Y-%m-%d")): count += 1
            cur += timedelta(days=1)
        return max(0, count - 1)   # entry day itself is day 0
    except: return 0

def clean_mem(mem):
    cutoff=(datetime.now(IST)-timedelta(days=14)).strftime("%Y-%m-%d")
    kept=[p for p in mem.split(",") if p.strip() and not (len(p)>=10 and p[4]=="-" and p[7]=="-" and p[:10]<cutoff)]
    result=",".join(kept)
    if len(result)>20000:
        # v15.23: drop oldest DATED daily flags first; symbol-state keys
        # (TSL/MAX/LP/ATR/RECD/MODE — an active trade's trailing stop lives
        # here) are protected. Old code kept an arbitrary "last 100 parts",
        # which could silently drop a live trade's TSL.
        parts=[p for p in result.split(",") if p.strip()]
        dated=[p for p in parts if len(p)>=10 and p[4]=="-" and p[7]=="-"]
        state=[p for p in parts if not (len(p)>=10 and p[4]=="-" and p[7]=="-")]
        result=",".join(state + dated[-50:])
    print(f"[MEM] Y1: {len(result):,} chars")
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
            f"Re-entry cooldown active (after target/loss) — {days_since}/{REENTRY_COOLDOWN_DAYS} trading days since {recd_date}. "
            f"{remaining} more trading days before re-entry allowed. "
            f"Stock needs to reset after the last exit."
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


def check_rsi_entry(symbol: str, is_bullish: bool, day_pct=None) -> tuple:
    rsi       = get_rsi(symbol)
    if rsi < 0: return True, rsi, "RSI unavailable — entry allowed"
    threshold = RSI_MAX_BULLISH if is_bullish else RSI_MAX_BEARISH
    if rsi > threshold:
        # v15.20 CALIBRATED EXCEPTION (2026-07-15 study of all 13 closed trades):
        # NO historical loser entered overbought (losers' entry RSI was 37-62 —
        # this veto never prevented a single actual loss), while 3 of the 6
        # target-hit winners entered at RSI 65-82 (BSE 73.3, IDEA 82.3,
        # ADANIPORTS 65.4) and NYKAA (owner's profitable manual trade,
        # 2026-07-15) was refused at 72.7. Momentum leaders ARE hot at breakout.
        # So: in a BULLISH regime, RSI up to RSI_HOT_MAX is allowed IF the stock
        # is UP on the day (buying strength, not a fading bounce). Fail-CLOSED:
        # if day change is unknown the old veto stands. RSI > RSI_HOT_MAX stays
        # a hard block (climax chase — IDEA-at-82 style luck is not a strategy).
        if is_bullish and rsi <= RSI_HOT_MAX and day_pct is not None and day_pct > 0:
            return True, rsi, f"RSI {rsi} hot but ≤ {RSI_HOT_MAX} + stock up {day_pct:+.1f}% today — momentum leader ✅"
        return False, rsi, f"RSI {rsi} > {threshold} — overbought, skip"
    zone = "oversold" if rsi < 35 else ("healthy" if rsi < 55 else "extended")
    return True, rsi, f"RSI {rsi} — {zone} ✅"


# ══════════════════════════════════════════════════════════════════════════════
# NIFTY DIRECTION CHECK
# ══════════════════════════════════════════════════════════════════════════════

def _nifty_index_row(nifty_sheet):
    """v15.23: return the NIFTY index row's values, VERIFIED by symbol.
    Row 2 is the fast path (current layout); if a future row shift moves it,
    scan for the first row whose symbol contains NIFTY instead of silently
    using a random stock's data for the market regime. None = not found."""
    try:
        row = nifty_sheet.row_values(2)
        if row and "NIFTY" in str(row[0]).upper():
            return row
        for r in _nifty200_rows(nifty_sheet)[1:]:
            if r and "NIFTY" in str(r[0]).upper():
                print(f"[NIFTY-ROW] index row found at symbol {r[0]!r} (not row 2 — layout shifted)")
                return r
        print("[NIFTY-ROW] WARNING: no NIFTY index row found in Nifty200 sheet")
    except Exception as e:
        print(f"[NIFTY-ROW] {e}")
    return None


def get_nifty_pct_change(nifty_sheet) -> float:
    try:
        row = _nifty_index_row(nifty_sheet)
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
    # v15.19: fast_info returns nothing on GitHub runners without raising —
    # fall back to .history(), the same call get_rsi() uses (proven on CI).
    # Intraday the last daily candle's Close tracks the live price, so
    # last-vs-previous close = today's % change.
    try:
        import yfinance as yf
        df = yf.Ticker("^NSEI").history(period="5d", interval="1d")
        if len(df) >= 2:
            prev = float(df["Close"].iloc[-2]); curr = float(df["Close"].iloc[-1])
            if prev > 0 and curr > 0:
                pct = round(((curr - prev) / prev) * 100, 2)
                print(f"[NIFTY] {pct:+.2f}% from yfinance history")
                return pct
    except Exception as e:
        print(f"[NIFTY] yfinance history: {e}")
    return 0.0


def check_nifty_direction(nifty_pct: float, is_bullish: bool) -> tuple:
    threshold = NIFTY_MIN_PCT_BULLISH if is_bullish else NIFTY_MIN_PCT_BEARISH
    if nifty_pct < threshold:
        return False, f"Nifty {nifty_pct:+.2f}% < {threshold:+.2f}% — {'wait for recovery' if is_bullish else 'must be green in bearish'}"
    return True, f"Nifty {nifty_pct:+.2f}% — {'green' if nifty_pct > 0 else 'flat'} ✅"


# ══════════════════════════════════════════════════════════════════════════════
# INDIA VIX — v15.10 Batch 2
# ══════════════════════════════════════════════════════════════════════════════

def get_india_vix() -> float:
    """Fetch live India VIX via yfinance. Returns 0 on failure (fail-open)."""
    try:
        import yfinance as yf
        t    = yf.Ticker("^INDIAVIX")
        info = t.fast_info
        val  = float(info.get('last_price', 0) or 0)
        if val > 0:
            print(f"[VIX] India VIX = {val:.2f}")
            return round(val, 2)
        # v15.19: fast_info returns nothing on GitHub runners without raising —
        # fall back to .history() (same proven call as get_rsi / nifty pct).
        df = t.history(period="5d", interval="1d")
        if not df.empty:
            val = float(df["Close"].iloc[-1])
            if val > 0:
                print(f"[VIX] India VIX = {val:.2f} (history)")
                return round(val, 2)
        return 0.0
    except ImportError:
        print("[VIX] yfinance not installed"); return 0.0
    except Exception as e:
        print(f"[VIX] fetch error: {e}"); return 0.0


def check_vix(vix_val: float) -> tuple:
    """Returns (allowed, reason). Fails open if VIX unavailable."""
    if vix_val <= 0:
        return True, "VIX unavailable — entry allowed"
    if vix_val > VIX_MAX:
        return False, f"India VIX {vix_val:.1f} > {VIX_MAX} — high volatility regime, skip new entries"
    zone = "calm" if vix_val < VIX_CALM else "normal"
    return True, f"India VIX {vix_val:.1f} — {zone} ✅"


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

def check_all_entry_filters(sym, mem, key, is_bullish, now, nifty_pct, today_entries,
                            vix_val=0.0, cp=0.0, nifty_sheet=None, bm_data=None):
    """
    Run all entry filters in order of cost (fast checks first, API calls last).
    Returns (allowed: bool, reasons: list, rsi_val: float)

    Order:
      1. Re-entry cooldown (memory lookup — instant)
      2. Time window (date math — instant)
      3. Daily entry limit (count — instant)
      4. Nifty direction (already fetched — instant)
      5. India VIX (already fetched once per tick — instant) — v15.10
      6. RSI (yfinance API call — only if 1-5 pass)
      ── Batch 4 institutional gates (added v15.12) ──
      7. Relative Strength    — stock_pct - nifty_pct ≥ 1%
      8. Volume confirmation  — relative volume ≥ 1.5×
      9. FII regime gate      — heavy FII outflow blocks longs
     10. PCR (soft — logs only)
     11. Delivery %           — ≥ 40%
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

    # Filter 5: India VIX regime (NEW v15.10)
    allowed, msg = check_vix(vix_val)
    reasons.append(f"[VIX] {msg}")
    if not allowed:
        return False, reasons, -1

    # Filter 6: RSI (API call — only if 1-5 passed)
    # v15.20: pass today's % change so the hot-but-leading exception can verify
    # the stock is actually up today. Missing data → None → fail-closed inside
    # check_rsi_entry (old hard veto stands).
    # v15.23 BUG FIX: `_LP_` memory only exists for symbols that were already
    # TRADED (set at promotion + in step_b, cleared on exit) — a fresh WAITING
    # candidate NEVER had it, so day_pct was always None and the calibrated
    # v15.20 exception never fired. Fall back to the live Nifty200 "%Change"
    # column (same value the AppScript scanner uses). `_LP_` stays preferred
    # when present (exact previous close beats a delayed quote).
    _pc = get_last_price(mem, key)
    day_pct = ((cp - _pc) / _pc) * 100 if (_pc > 0 and cp > 0) else None
    if day_pct is None:
        day_pct = _read_nifty200_day_pct(nifty_sheet, sym)
    allowed, rsi_val, msg = check_rsi_entry(sym, is_bullish, day_pct)
    reasons.append(f"[RSI] {msg}")
    if not allowed:
        return False, reasons, rsi_val

    # ── v15.12 Batch 4: Institutional edges. Each wrapped individually so a
    #    buggy check cannot cascade. All fail open if their data is missing. ──
    if _INST_EDGES_AVAILABLE:
        # 7. Relative strength — prefer Nifty200 pre-computed RS column (more
        # accurate than computing from prev_close); fall back to math if absent.
        try:
            rs_col_val = _read_nifty200_rs(nifty_sheet, sym) if nifty_sheet is not None else 0.0
            if abs(rs_col_val) > 0.01:
                if rs_col_val >= inst_edges.RS_MIN_PCT:
                    reasons.append(f"[RS] sheet RS {rs_col_val:+.2f} ≥ {inst_edges.RS_MIN_PCT:.1f} ✅")
                else:
                    reasons.append(f"[RS] sheet RS {rs_col_val:+.2f} < {inst_edges.RS_MIN_PCT:.1f} — no leadership")
                    return False, reasons, rsi_val
            else:
                # Fallback: compute from prev close
                prev_close = get_last_price(mem, key)
                ok, msg = inst_edges.check_relative_strength(sym, cp, prev_close, nifty_pct)
                reasons.append(f"[RS] (fallback) {msg}")
                if not ok:
                    return False, reasons, rsi_val
        except Exception as e:
            print(f"[RS] check failed for {sym}: {e} — fail open")
            reasons.append(f"[RS] check errored — entry allowed")

        # 8. Volume confirmation — relative volume from Nifty200 sheet
        try:
            rel_vol = _read_nifty200_relvol(nifty_sheet, sym) if nifty_sheet is not None else 0.0
            # v15.23: use the day_pct already resolved above (LP → sheet
            # "%Change" fallback) so the ≥3% price bypass works for fresh
            # candidates too — it was dead because prev_close was always 0.
            pct_change = day_pct if day_pct is not None else 0
            # v15.21: pass IST clock so the gate can pro-rate the partial-day
            # volume reading against the expected fraction of the session.
            ok, msg = inst_edges.check_volume_confirmation(sym, rel_vol, pct_change=pct_change, now=now)
            reasons.append(f"[VOL] {msg}")
            if not ok:
                return False, reasons, rsi_val
        except Exception as e:
            print(f"[VOL] check failed for {sym}: {e} — fail open")
            reasons.append(f"[VOL] check errored — entry allowed")

        # 9. FII regime — heavy outflow blocks new longs (or inflow blocks shorts)
        try:
            ok, msg = inst_edges.check_fii_regime(bm_data or {}, is_bullish, now)
            reasons.append(f"[FII] {msg}")
            if not ok:
                return False, reasons, rsi_val
        except Exception as e:
            print(f"[FII] check failed: {e} — fail open")
            reasons.append(f"[FII] check errored — entry allowed")

        # 10. PCR soft filter — informational, never blocks
        try:
            ok, msg = inst_edges.check_pcr_regime(bm_data or {}, is_bullish)
            reasons.append(f"[PCR] {msg}")
        except Exception as e:
            print(f"[PCR] check failed: {e} — skip")
            reasons.append(f"[PCR] check errored — skipped")

        # 11. Delivery % from yesterday's bhavcopy
        try:
            ok, msg = inst_edges.check_delivery_percent(sym, bm_data or {})
            reasons.append(f"[DLV] {msg}")
            if not ok:
                return False, reasons, rsi_val
        except Exception as e:
            print(f"[DLV] check failed for {sym}: {e} — fail open")
            reasons.append(f"[DLV] check errored — entry allowed")

    # 12. REVERSAL-RISK VETO (v15.15) — reject "big but about-to-reverse" longs:
    # overbought + at-ATH + over-extended + climax volume. Fail-open: any error
    # or missing data → entry allowed (never blocks on uncertainty).
    if _EQ_AVAILABLE and nifty_sheet is not None:
        try:
            ri = _reversal_inputs(nifty_sheet, sym)
            relv = _read_nifty200_relvol(nifty_sheet, sym)
            rev = eq.reversal_risk(
                rsi=rsi_val if rsi_val and rsi_val > 0 else 0.0,
                pct_below_ath=ri["pct_below_ath"] or None,
                dist_from_20dma=ri["dist_from_20dma"] or None,
                rel_vol=relv, is_bullish=is_bullish,
            )
            if rev >= eq.REVERSAL_RISK_VETO:
                reasons.append(f"[REV] reversal-risk {rev:.0f} ≥ {eq.REVERSAL_RISK_VETO:.0f} — skip (overbought/at-ATH/extended)")
                return False, reasons, rsi_val
            reasons.append(f"[REV] reversal-risk {rev:.0f} ✅")

            # 13. RESISTANCE-ROOM VETO (v15.17) — skip longs pinned right under a
            # ceiling with too little clean runway (in ATR) to the next
            # resistance. Dominant losing pattern in the 2026-07 audit: EICHERMOT
            # bought twice under ~₹7440 with <0.3 ATR of room → stalled → stop.
            # Reuses `ri` above (no extra sheet read). Fail-open: only fires when
            # resistance data EXISTS and price is BELOW it with room below the
            # threshold. A genuine breakout ABOVE resistance (target_room → 0.0)
            # or missing data is never blocked.
            resl  = ri.get("resistance") or 0.0
            if resl and resl > cp and cp > 0:
                atr_r = _read_atr_from_nifty200(nifty_sheet, sym)
                if atr_r > 0:
                    room = eq.target_room(cp, resl, atr_r)
                    if 0 < room < eq.MIN_TARGET_ROOM_ATR:
                        reasons.append(f"[ROOM] only {room:.2f} ATR to resistance ₹{resl:.2f} < {eq.MIN_TARGET_ROOM_ATR:.1f} — skip (capped by resistance)")
                        return False, reasons, rsi_val
                    reasons.append(f"[ROOM] {room:.2f} ATR runway to ₹{resl:.2f} ✅")
        except Exception as e:
            print(f"[REV/ROOM] check errored for {sym}: {e} — fail open")
            reasons.append(f"[REV/ROOM] errored — entry allowed")

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

def is_cash_trade(ttype):
    return "CASH" in str(ttype).upper()


def is_option_trade(ttype):
    """v15.16: True for the 📊 Options Alert trade type (option-buying signals)."""
    return "OPTION" in str(ttype).upper()


def est_option_pnl_pct(stock_pnl_pct):
    """v15.16: rough option-premium P/L from the stock move, for DISPLAY only.
    ITM ~0.7Δ option ≈ OPTION_LEVERAGE_EST× the stock %. Returns a rounded %.
    """
    return round(stock_pnl_pct * OPTION_LEVERAGE_EST, 0)


def _parse_expiry(s):
    """v15.25: AlertLog col W expiry ("25-Aug-2026") → date, or None."""
    try:
        return datetime.strptime(str(s).strip()[:11], "%d-%b-%Y").date()
    except Exception:
        return None


def _row_option_leverage(sym, ent, ent_time, opt_strike, opt_expiry, now):
    """v15.24/25: premium-aware leverage for an option row (Δ·S/premium via
    option_intelligence.est_option_leverage; strike from col V "2100 CE Aug",
    expiry from col W, HV cached). ANY missing piece → flat OPTION_LEVERAGE_EST
    exactly as the old convention. Fail-open, never raises."""
    if _OPT_INTEL_AVAILABLE:
        try:
            _stk = to_f(str(opt_strike).split()[0]) if str(opt_strike).strip() else 0.0
            _exp_d = _parse_expiry(opt_expiry)
            _days = 0
            if _exp_d:
                try:    _ent_d = datetime.strptime(str(ent_time)[:10], "%Y-%m-%d").date()
                except Exception: _ent_d = now.date()
                _days = (_exp_d - _ent_d).days
            _hv = opt_intel.get_historical_volatility(sym)
            _lev = opt_intel.est_option_leverage(ent, _stk, _days, _hv) if (_stk > 0 and _days > 0 and _hv > 0) else None
            if _lev:
                return _lev
        except Exception as _le:
            print(f"[OPT-LEV] {sym}: {_le} — flat {OPTION_LEVERAGE_EST:.0f}x estimate")
    return OPTION_LEVERAGE_EST


def _option_ledger_exit(pnl_pct, eff_lev, stage, opt_expiry, ent_time, now):
    """v15.25: exit decision for OPTION-type paper trades per the ALERT's OWN
    rules (ledger honesty — the ledger must experience what a subscriber
    following the alert would):
      1. 🛑 est option loss ≥ OPTION_LOSS_CAP_PCT (owner 🔒 20% hard cap)
      2. ⏰ never hold past expiry week (≤ OPTION_EXPIRY_EXIT_DAYS to expiry)
      3. ⏰ v15.26: ALL options exit after OPTION_MAX_TDAYS trading days —
         the alert now says "intraday ya max 1-2 din" (owner rule 2026-07-18)
    Returns an exit-reason string or "" (no exit). Stock SL/TSL/target checks
    stay in step_b unchanged — those are stock-anchored per the alert too."""
    opt_est = pnl_pct * eff_lev
    if opt_est <= -OPTION_LOSS_CAP_PCT:
        return f"🛑 OPTION LOSS CAP (est {opt_est:+.0f}% ≤ −{OPTION_LOSS_CAP_PCT:.0f}%)"
    exp_d = _parse_expiry(opt_expiry)
    if exp_d is not None:
        dleft = (exp_d - now.date()).days
        if dleft <= OPTION_EXPIRY_EXIT_DAYS:
            return f"⏰ EXPIRY WEEK EXIT ({dleft}d to expiry)"
    if calc_trading_hold_days(ent_time, now) >= OPTION_MAX_TDAYS:
        return f"⏰ OPTION TIME EXIT ({OPTION_MAX_TDAYS} trading days — alert rule: intraday/1-2 din max)"
    return ""


def calc_new_tsl(cp, ent, init_sl, atr, ttype, mem, key, now, ent_time=""):
    """
    ent_time: entry time string from AlertLog row C_ENTRY_TIME.
    Bug fixed v15.2: was using get_exit_date() (always "") → hold check always blocked TSL.
    Now uses actual entry time from the sheet row.

    v15.10 Batch 2 upgrades:
      • ONE-R BREAKEVEN — effective BE threshold = min(params['breakeven'], 1R%)
        where 1R% = (ent - init_sl) / ent * 100. Floor at ONE_R_BE_FLOOR_PCT so
        a freak tight SL can't trigger BE on tiny intraday wiggle. Behaviour
        only improves (BE moves in EARLIER, never later) vs. v15.9.
      • CHANDELIER TRAIL — trail step now uses cur_max - atr*mult (highest-high
        anchor, true Chandelier), not cp - atr*mult (CMP anchor). TSL can only
        rise — better lock on parabolic moves. Still capped at cp*0.99 to keep
        SL strictly below current price.
    """
    params   = get_tsl_params(mem, key)
    cur_tsl  = get_tsl(mem, key) or init_sl
    cur_max  = get_max_price(mem, key) or ent
    gain_pct = ((cp - ent) / ent) * 100 if ent > 0 else 0
    new_tsl  = cur_tsl

    if is_cash_trade(ttype):        hold = 0   # cash trades: no min hold — trail immediately
    elif "Positional" in str(ttype): hold = MIN_HOLD_POS
    else:                            hold = MIN_HOLD_SWING

    hold_days = calc_hold_days(ent_time, now)
    if hold_days < hold:
        return cur_tsl, f"min hold ({hold}d)"

    # v15.10: compute 1R-based effective breakeven threshold.
    # R is the rupee distance from entry to initial SL; one_r_pct is that as %.
    # We move BE in at whichever is SOONER: 1R or the regime-default %.
    one_r_pct      = ((ent - init_sl) / ent) * 100 if (ent > 0 and init_sl > 0 and ent > init_sl) else 0
    eff_breakeven  = params["breakeven"]
    if one_r_pct > 0:
        eff_breakeven = min(params["breakeven"], max(one_r_pct, ONE_R_BE_FLOOR_PCT))

    if gain_pct >= params["trail"]:
        # v15.10: Chandelier — anchor to highest price reached, not CMP
        trail_sl = cur_max - atr * params["atr_mult"]
        new_tsl  = max(cur_tsl, trail_sl)
        reason   = f"chandelier @ {gain_pct:.1f}%"
    elif gain_pct >= params["lock1"]:
        new_tsl  = max(cur_tsl, ent + atr * 0.5)
        reason   = f"lock1 @ {gain_pct:.1f}%"
    elif gain_pct >= eff_breakeven:
        new_tsl  = max(cur_tsl, ent * 1.002)
        reason   = f"breakeven @ +{gain_pct:.1f}% (1R={one_r_pct:.1f}%)" if one_r_pct > 0 else f"breakeven @ +{gain_pct:.1f}%"
    else:
        new_tsl  = cur_tsl
        reason   = f"below BE thresh {eff_breakeven:.1f}% (gain {gain_pct:.1f}%)"

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
    # v15.4: explicit cred validation — fails with clear message instead of cryptic FileNotFoundError
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    raw   = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        try:
            with open("service_account.json") as f:
                raw = f.read().strip()
        except FileNotFoundError:
            raise SystemExit("[CREDS] GCP_SERVICE_ACCOUNT_JSON env var not set and service_account.json not found locally")
    try:
        creds_dict = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"[CREDS] Failed to parse GCP credentials JSON: {e}")
    creds  = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
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
    # v15.23: reads the per-tick _nifty200_rows cache — each call used to be a
    # fresh full-sheet fetch (the ranking loop burst 15+ reads in seconds →
    # silent 429s that disabled best-first ordering on busy mornings).
    # v15.27: header-name lookup (was hardcoded row[28]) — a future inserted
    # column would otherwise silently corrupt every SL/target/option decision.
    try:
        c_atr = _find_nifty200_col(nifty_sheet, ["ATR (14)"], subs=["atr14", "atr"])
        if c_atr < 0:
            return 0.0
        clean = sym.replace("NSE:","").strip()
        for row in _nifty200_rows(nifty_sheet)[1:]:
            if len(row) > c_atr and str(row[0]).replace("NSE:","").strip() == clean:
                atr = to_f(row[c_atr])
                if atr > 0:
                    print(f"[ATR] {sym}: {atr}")
                    return atr
    except Exception as e:
        print(f"[ATR] {e}")
    return 0.0


def _read_opt_tag_from_nifty200(nifty_sheet, sym):
    """v15.22: Options-eligibility tag from Nifty200 col "Options" —
    "N50" (Nifty50, deep option chain) / "YES" (F&O-listed) / "" (NO derivatives:
    SEBI's 2025 eligibility purge removed IRCTC/MRF/ATGL/TATACOMM/...).
    Column is fed from NSE's official F&O file. Returns None when the column/
    symbol can't be read → caller fails OPEN (old behavior), never blocks on
    a data hiccup. v15.23: served from the per-tick sheet cache.
    v15.27: header-name lookup (was hardcoded row[35])."""
    try:
        c_opt = _find_nifty200_col(nifty_sheet, ["Options"], subs=["optionseligibility"])
        if c_opt < 0:
            return None
        clean = sym.replace("NSE:","").strip()
        for row in _nifty200_rows(nifty_sheet)[1:]:
            if str(row[0] if row else "").replace("NSE:","").strip() == clean:
                if len(row) > c_opt:
                    return str(row[c_opt]).strip()
                return None
    except Exception as e:
        print(f"[OPT-TAG] {e}")
    return None


def _read_nifty200_day_pct(nifty_sheet, sym):
    """v15.23: the stock's LIVE day %change from Nifty200 col "%Change" (the
    same value the AppScript scanner reads as r[3]). Returns None when the
    column/row/cell is missing or unparseable so callers keep their existing
    fail-closed (RSI exception) / fail-open (gap guard skipped) behaviour —
    a genuinely flat 0.00% day IS returned as 0.0."""
    if nifty_sheet is None:
        return None
    col = _find_nifty200_col(nifty_sheet, exact_names=["%Change"], substring_keywords=None)
    if col < 0:
        return None
    try:
        clean = sym.replace("NSE:", "").strip()
        for row in _nifty200_rows(nifty_sheet)[1:]:
            if len(row) > col and str(row[0]).replace("NSE:", "").strip() == clean:
                raw = str(row[col]).strip()
                if not raw:
                    return None
                try:
                    return float(raw.replace(",", "").replace("%", ""))
                except ValueError:
                    return None
    except Exception as e:
        print(f"[DAY%] {sym}: {e}")
    return None


# v15.12 Batch 4: per-tick cache of Nifty200 column index lookups.
# Header text → column index. Resolved once per process, then served from cache.
_NIFTY200_COL_CACHE = {}
_NIFTY200_ROWS_CACHE = None  # full sheet snapshot, fetched once per tick

def _norm_header(s: str) -> str:
    """Normalise header text for matching — lowercase, no spaces, no underscores, no %."""
    return str(s).lower().replace(" ", "").replace("_", "").replace("%", "").replace("(", "").replace(")", "")


def _find_nifty200_col(nifty_sheet, exact_names: list, substring_keywords: list = None) -> int:
    """
    Self-healing column lookup against Nifty200 row-1 headers.
       1. EXACT MATCH first (normalised) — protects short headers like 'RS' from
          false hits on 'Pivot_Resistance'.
       2. SUBSTRING fallback — catches "Volume_vs_Avg_%" via keyword 'volumevsavg'.
    Returns -1 if no header matches (fail-open). Result cached per process.

    Per feedback_free_forever_self_repair: data-layout changes (AppScript adding
    new columns) must not require code edits.
    """
    cache_key = "exact:" + "|".join(exact_names) + "/sub:" + "|".join(substring_keywords or [])
    if cache_key in _NIFTY200_COL_CACHE:
        return _NIFTY200_COL_CACHE[cache_key]
    try:
        header = nifty_sheet.row_values(1)
        norm_headers = [_norm_header(h) for h in header]
        # Pass 1 — exact match
        for needle in exact_names:
            n = _norm_header(needle)
            for i, h in enumerate(norm_headers):
                if h == n:
                    _NIFTY200_COL_CACHE[cache_key] = i
                    print(f"[NIFTY200] EXACT '{header[i]}' col {i} matched {needle!r}")
                    return i
        # Pass 2 — substring (only if explicit substring keywords given)
        if substring_keywords:
            for kw in substring_keywords:
                n = _norm_header(kw)
                for i, h in enumerate(norm_headers):
                    if n in h:
                        _NIFTY200_COL_CACHE[cache_key] = i
                        print(f"[NIFTY200] SUBSTR '{header[i]}' col {i} matched {kw!r}")
                        return i
    except Exception as e:
        print(f"[NIFTY200] header read error: {e}")
    _NIFTY200_COL_CACHE[cache_key] = -1
    return -1


def _nifty200_rows(nifty_sheet):
    """One-shot fetch + cache of full sheet data — avoids 5× sheet reads when
    multiple Nifty200 column reads happen in the same tick."""
    global _NIFTY200_ROWS_CACHE
    if _NIFTY200_ROWS_CACHE is not None:
        return _NIFTY200_ROWS_CACHE
    try:
        _NIFTY200_ROWS_CACHE = nifty_sheet.get_all_values()
    except Exception as e:
        print(f"[NIFTY200] fetch error: {e}")
        _NIFTY200_ROWS_CACHE = []
    return _NIFTY200_ROWS_CACHE


def _read_nifty200_relvol(nifty_sheet, sym) -> float:
    """
    Returns today's relative volume as a MULTIPLE (e.g. 1.5 = 150% of avg).
    The Nifty200 sheet stores this as `Volume_vs_Avg_%` (percentage form,
    can be negative). Convention: column value 50 → 1.5×, -50 → 0.5×.
    Falls open with 0.0 if column or row missing.
    """
    col = _find_nifty200_col(
        nifty_sheet,
        exact_names=["Volume_vs_Avg_%", "VolumeVsAvg%", "RelVol"],
        substring_keywords=["volumevsavg", "relvol", "rvol", "relativevolume"],
    )
    if col < 0:
        return 0.0
    try:
        clean = sym.replace("NSE:", "").strip()
        for row in _nifty200_rows(nifty_sheet)[1:]:
            if len(row) > col and str(row[0]).replace("NSE:", "").strip() == clean:
                # v15.23: the column is ALWAYS diff-form (+50 = 1.5×, −67 =
                # 0.33× — owner-verified v15.13). The old |raw|>5 heuristic
                # returned values in (0,5] AS multiples (+3% above avg volume
                # read as "3.0× huge" and sailed through the 1.5× gate) and
                # values in (−5,0] fell through to fail-open. Now every
                # numeric value converts 1+raw/100; ONLY a blank/unparseable
                # cell fails open with 0.0.
                raw_s = str(row[col]).strip()
                if not raw_s:
                    return 0.0            # blank cell → data unavailable → fail-open
                try:
                    raw = float(raw_s.replace(",", "").replace("%", ""))
                except ValueError:
                    return 0.0            # unparseable → fail-open
                return max(0.0, 1.0 + raw / 100.0)
    except Exception as e:
        print(f"[RELVOL] {sym}: {e}")
    return 0.0


def _read_nifty200_rs(nifty_sheet, sym) -> float:
    """
    Reads the pre-computed RS column (header == 'RS') from Nifty200.
    The sheet already has institutional-grade RS; using it is more accurate
    than computing stock_pct − nifty_pct from yesterday's close.
    Returns 0.0 (fail-open) if column or row not found.
    """
    col = _find_nifty200_col(
        nifty_sheet,
        exact_names=["RS", "Rel_Strength", "Relative_Strength", "RelativeStrength"],
        substring_keywords=None,   # NO substring — too risky for short 'RS'
    )
    if col < 0:
        return 0.0
    try:
        clean = sym.replace("NSE:", "").strip()
        for row in _nifty200_rows(nifty_sheet)[1:]:
            if len(row) > col and str(row[0]).replace("NSE:", "").strip() == clean:
                return to_f(row[col])
    except Exception as e:
        print(f"[RS-col] {sym}: {e}")
    return 0.0


def _read_nifty200_field(nifty_sheet, sym, exact_names, subs=None, numeric=True):
    """Generic self-healing single-cell read from Nifty200 by header name.
    Returns 0.0 / "" (fail-open) if the column or row is missing. Used by the
    entry-quality layer for ATH%, 20-DMA distance, resistance, FII zone, etc."""
    if nifty_sheet is None:
        return 0.0 if numeric else ""
    col = _find_nifty200_col(nifty_sheet, exact_names, subs)
    if col < 0:
        return 0.0 if numeric else ""
    try:
        clean = sym.replace("NSE:", "").strip()
        for row in _nifty200_rows(nifty_sheet)[1:]:
            if len(row) > col and str(row[0]).replace("NSE:", "").strip() == clean:
                return to_f(row[col]) if numeric else str(row[col]).strip()
    except Exception as e:
        print(f"[N200-field] {sym}: {e}")
    return 0.0 if numeric else ""


def _reversal_inputs(nifty_sheet, sym):
    """Pull the columns the reversal-risk score needs (all fail-open)."""
    return {
        "pct_below_ath": _read_nifty200_field(
            nifty_sheet, sym, ["%down_from_52W_UP", "%down_from_52W_High"],
            subs=["downfrom52w"]),
        "dist_from_20dma": _read_nifty200_field(
            nifty_sheet, sym, ["%Distance_from_20_DMA", "%Dist_from_20DMA"],
            subs=["distancefrom20", "distfrom20"]),
        "resistance": _read_nifty200_field(
            nifty_sheet, sym, ["Pivot_Resistance", "Resistance"],
            subs=["resistance", "pivot"]),
    }


def get_market_regime(nifty_sheet):
    try:
        row  = _nifty_index_row(nifty_sheet)   # v15.23: verified NIFTY row, not blind row 2
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
                      opt_signal="", opt_strike="", opt_expiry="", opt_theta="",
                      sym="", mem="", now=None, opt_tag=None, bm_data=None):
    """
    v15.11 Batch 3 — now produces a smart option recommendation via
    option_intelligence module: ITM strike pick, HV-based IV filter,
    earnings block, PE-side support for bearish regime, stock-anchored
    SL/target. Old v15.10 ATM/OTM path retained as fallback when the
    module is unavailable (self-repair).

    Eligibility gates (unchanged):
      • rank > 5            → skip (only top-5 priority stocks get options)
      • cp <= 0 or atr <= 0 → skip (bad data)
    """
    if rank > 5:                  return ""
    if cp <= 0 or atr <= 0:       return ""
    # v15.22: hard gate on the Nifty200 "Options" tag (col AJ, from NSE's
    # official F&O list). "" = the stock HAS NO derivatives (SEBI 2025 purge) —
    # suggesting a CE for it would be an impossible trade. None = tag unknown
    # (column unreadable) → fail-open, keep old behavior.
    if opt_tag is not None and str(opt_tag).strip() == "":
        return ""
    _liq_note = ""
    if opt_tag is not None:
        _liq_note = ("\n   💧 Chain: 🟦 Nifty50 — deep & liquid"
                     if str(opt_tag).strip() == "N50"
                     else "\n   💧 Chain: ⚠️ midcap — check bid-ask spread first")

    # Smart path — preferred when option_intelligence loaded successfully.
    # v15.23: bm_data passed through — fetch_earnings.py writes EARNINGS_* as
    # BotMemory ROWS, not into the _RUNTIME_MEM string, so the earnings block
    # was permanently fail-open when it only searched `mem`.
    if _OPT_INTEL_AVAILABLE and sym and now is not None:
        try:
            rec = opt_intel.recommend_option(
                symbol=sym, cp=cp, atr=atr, stage=stage,
                is_bullish=is_bullish, mem=mem or "", now=now,
                bm_data=bm_data,
            )
            _txt = opt_intel.format_option_alert(
                symbol=sym, cp=cp, rec=rec,
                scanner_strike=opt_strike, scanner_expiry=opt_expiry,
                scanner_theta=opt_theta,
            )
            return (_txt + _liq_note) if _txt else _txt
        except Exception as e:
            print(f"[OPT] smart recommend failed for {sym}: {e} — falling back to v15.10 path")

    # Fallback path — v15.10 logic, kept verbatim so bot never goes silent
    # on options even if option_intelligence misbehaves. Bearish still skipped
    # in fallback because old code never supported PE side.
    if not is_bullish: return ""
    if opt_signal in ("📊 BUY CE", "📦 BASE CE") and opt_strike:
        label = "BASE OPTIONS" if "BASE" in opt_signal else "OPTIONS"
        return (
            f"\n\n📊 <b>{label} SIGNAL</b> (sirf INTRADAY / 1-2 din)\n"
            f"   🎰 Buy: <b>{opt_strike}</b>\n"
            f"   📅 Expiry: {opt_expiry} (current — yahi volume hai)\n"
            f"   ⏳ Theta: {opt_theta}\n"
            f"   ⚡ Entry: 9:30-9:45 AM after stock triggers\n"
            f"   ⏱ Hold: intraday ya max 1-2 din — usse zyada NAHI\n"
            f"   🛑 Exit: stock −1.5% (≈ option −10% to −15%) ya 2 din pure\n"
            f"   ⚠️ Check live premium on Zerodha"
            f"{_liq_note}"
        )
    atr_pct = (atr/cp)*100
    if atr_pct < 1.5: return ""
    # v15.24: same strike grid as option_intelligence.strike_step / appscript
    # _getStrikeInterval (was a THIRD divergent table).
    gap = 1 if cp<100 else (5 if cp<250 else (10 if cp<500 else (20 if cp<1000 else (50 if cp<2000 else 100))))
    atm = round(cp/gap)*gap; otm = atm+gap
    strike = f"{int(otm)} CE" if "BREAKOUT CONFIRMED" in stage else f"{int(atm)} CE"
    tgt_p = 50 if atr_pct>=2.5 else 65; sl_p = 35 if atr_pct>=2.5 else 40
    return (
        f"\n\n📊 <b>CE CANDIDATE</b> (ATR {atr_pct:.1f}%)\n"
        f"   Strike: {strike} | Target: +{tgt_p}% | SL: stock −1.5%\n"
        f"   ⚠️ VIX check before buying"
        f"{_liq_note}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY MESSAGE BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

# Compliance footer on EVERY member trade alert. We DO share the trade's logic
# (Setup/RSI/Nifty) for education + trust — but AI360Trading is NOT SEBI
# registered, so each alert is framed as educational analysis, not personalised
# advice. (The options alert already carries this; the cash-entry alerts did not.)
ALERT_DISCLAIMER = (
    "\n\n<i>📚 Educational analysis only — AI360Trading is NOT SEBI registered. "
    "Not investment advice. Do your own research and manage your own risk.</i>"
)

def _trade_style_lines(ttype):
    """v15.26 (owner rule 2026-07-18): every entry alert states in easy language
    HOW the trade is taken (cash/MTF vs intraday) and WHICH TradingView chart
    to cross-check, plus that the entry stays valid while price holds above SL."""
    t = str(ttype)
    if is_cash_trade(t):
        how = "💼 Kaise: CASH me kharide — intraday/short trade hai"
        tv  = "📺 TradingView: 15m chart par check kare"
    elif "Positional" in t:
        how = "💼 Kaise: CASH me kharide ya accumulate kare (hafte-mahine ka trade)"
        tv  = "📺 TradingView: WEEKLY chart par check kare"
    else:  # swing
        how = "💼 Kaise: CASH ya MTF me kharide (2-4 hafte ka trade) — option me lamba hold NAHI"
        tv  = "📺 TradingView: DAILY chart par check kare"
    return f"{how}\n✅ Entry valid jab tak price SL ke upar hai\n{tv}"

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
        f"RR: {rr} | Priority: {rank}\n{filters}\n"
        f"{_trade_style_lines(ttype)}"
    )

def build_entry_premium(sym, cp, stage, sl, tgt, rr, ttype, atr, rank, capital, is_bullish,
                        rsi_val=-1, nifty_pct=0, opt_signal="", opt_strike="", opt_expiry="", opt_theta="",
                        mem="", now=None, opt_tag=None, bm_data=None):
    base = build_entry_advance(sym, cp, stage, sl, tgt, rr, ttype, atr, rank, capital, is_bullish,
                                rsi_val, nifty_pct, opt_signal, opt_strike, opt_expiry, opt_theta)
    # v15.11: pass sym/mem/now to enable smart option recommendation via
    # option_intelligence (HV regime + earnings + ITM strike + PE side).
    # v15.22: opt_tag gates the CE block on real F&O eligibility (Nifty200 col AJ).
    # v15.23: bm_data carries the EARNINGS_* BotMemory rows to the earnings block.
    return base + ce_candidate_flag(cp, atr, stage, is_bullish, rank,
                                    opt_signal, opt_strike, opt_expiry, opt_theta,
                                    sym=sym, mem=mem, now=now, opt_tag=opt_tag,
                                    bm_data=bm_data)

def build_entry_basic(sym, cp, stage, pct_chg):
    name = sym.replace("NSE:", "")
    return (
        f"🚨 <b>SIGNAL ALERT — {name}</b>\n"
        f"Entry: ₹{cp:.2f} | {stage}\n\n"
        f"🔒 SL and Target shared with Advance/Premium members only\n\n"
        f"📈 <b>Join Advance @ ₹699/month</b> — get full entry details\n"
        f"📱 ai360trading.in/membership"
    )


# ══════════════════════════════════════════════════════════════════════════════
# STEP A: WAITING → TRADED
# ══════════════════════════════════════════════════════════════════════════════

def step_a_enter_trades(log_sheet, nifty_sheet, bm_sheet, mem, now, is_bullish, nifty_pct, today_entries, vix_val=0.0):
    """
    Check WAITING rows → promote to TRADED if all filters pass.
    v15.0:  RSI + time + day + Nifty + re-entry cooldown checks.
    v15.2:  Cash Intraday trades use separate entry window + capital.
    v15.10: India VIX filter — blocks new entries when VIX > VIX_MAX.
    """
    today_s   = now.strftime("%Y-%m-%d")
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

    # v15.15 BEST-OF RANKING — when several setups wait and only a few daily
    # slots remain, fill them with the BEST candidate first (conviction × RR ×
    # clean room ÷ reversal-risk), not sheet order. Fail-open: any error keeps
    # the original top-to-bottom order. Non-WAITING rows are skipped inside the
    # loop regardless, so their relative order is irrelevant.
    indexed = list(enumerate(rows[1:22], start=2))
    if _EQ_AVAILABLE:
        try:
            def _cand_score(item):
                _i, _r = item
                _r = pad(_r)
                if "WAITING" not in str(_r[C_STATUS]).upper():
                    return -1.0
                _sym = str(_r[C_SYMBOL]).strip()
                _cp  = to_f(_r[C_LIVE_PRICE]); _pri = to_f(_r[C_PRIORITY])
                try:    _rr = float(str(_r[C_RR]).split(':')[-1]) if ':' in str(_r[C_RR]) else to_f(_r[C_RR])
                except: _rr = 0.0
                _atr = _read_atr_from_nifty200(nifty_sheet, _sym)
                _ri  = _reversal_inputs(nifty_sheet, _sym)
                _relv = _read_nifty200_relvol(nifty_sheet, _sym)
                _rev = eq.reversal_risk(pct_below_ath=_ri["pct_below_ath"] or None,
                                        dist_from_20dma=_ri["dist_from_20dma"] or None,
                                        rel_vol=_relv, is_bullish=is_bullish)
                _room = eq.target_room(_cp, _ri["resistance"], _atr)
                return eq.composite_score(priority=_pri, rr=_rr, rev_risk=_rev, room=_room)
            # v15.23: compute each candidate's score exactly ONCE. It was
            # evaluated up to 3× per row (sort key + filter + log line), and
            # with the old uncached ATR read that meant 15+ full-sheet fetches
            # in seconds → silent 429s → ranking quietly fell back to sheet
            # order on exactly the busy mornings it exists for.
            _scores = {it[0]: _cand_score(it) for it in indexed}
            scored = sorted(indexed, key=lambda it: _scores[it[0]], reverse=True)
            top = [it for it in scored if _scores[it[0]] > 0]
            if top:
                print(f"[RANK] best-first: " + ", ".join(
                    f"{str(pad(r)[C_SYMBOL]).strip()}={_scores[i]:.0f}" for i, r in top[:5]))
            indexed = scored
        except Exception as e:
            print(f"[RANK] ordering errored: {e} — using sheet order")
            indexed = list(enumerate(rows[1:22], start=2))

    for i, row in indexed:
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

        # v15.9 BUG-C — Setup-invalidated guard. AlertLog "Initial SL" is fixed at
        # signal time, but Live Price refreshes every tick. If the stock dropped
        # below the SL while still WAITING, promoting it to TRADED would trigger
        # an instant TSL exit on the very next monitor tick (cp <= cur_tsl).
        # Example seen 2026-05-27: MCX signal generated 2026-05-26 with SL ₹3,194
        # → next day MCX -4.5% to ₹3,012 → SL > cp → invalidated.
        # Action: leave row WAITING, log the reason, skip silently this tick.
        if sl > 0 and sl >= cp:
            print(f"[SETUP INVALIDATED] {sym}: SL ₹{sl:.2f} >= Live ₹{cp:.2f} — skip (would exit instantly)")
            continue

        key  = sym_key(sym)
        cash = is_cash_trade(ttype)

        # ── Cash intraday: separate daily cap check ───────────────────────────
        if cash:
            today_cash = sum(1 for p in mem.split(",") if p.strip().startswith(today_s + "_CASH_"))
            if today_cash >= CASH_MAX_DAILY:
                print(f"[STEP A] {sym}: cash daily limit {today_cash}/{CASH_MAX_DAILY} — skip")
                continue
            # Cash entry window: 9:15-10:30 AM only
            if (now.hour, now.minute) > CASH_ENTRY_WINDOW_END:
                print(f"[STEP A] {sym}: cash after 10:30 AM — skip")
                continue

        # ── v15.0: Run ALL filters including re-entry cooldown ────────────────
        # Cash trades skip RSI/Nifty/time filters — they're volume-driven gap moves
        if cash:
            allowed = cp > 0
            filter_reasons = [f"[CASH] Volume breakout trade — standard filters bypassed"]
            rsi_val = -1
            # v15.17: even a cash gap-trade must not be bought right under a
            # ceiling (the audit's dominant loss pattern). Fail-open resistance-
            # room veto — only fires when Nifty200 has resistance data for this
            # symbol AND price is below it with <MIN_TARGET_ROOM_ATR of runway.
            if allowed and _EQ_AVAILABLE and nifty_sheet is not None:
                try:
                    _cri  = _reversal_inputs(nifty_sheet, sym)
                    _cres = _cri.get("resistance") or 0.0
                    if _cres and _cres > cp and cp > 0:
                        _catr = _read_atr_from_nifty200(nifty_sheet, sym)
                        if _catr > 0:
                            _croom = eq.target_room(cp, _cres, _catr)
                            if 0 < _croom < eq.MIN_TARGET_ROOM_ATR:
                                allowed = False
                                filter_reasons.append(
                                    f"[ROOM] cash: only {_croom:.2f} ATR to resistance ₹{_cres:.2f} — skip (capped)")
                except Exception as _ce:
                    print(f"[ROOM] cash check errored for {sym}: {_ce} — fail open")
        else:
            # v15.12: pass cp + nifty_sheet + bm_data so Batch-4 institutional
            # filters can do RS / volume / FII / PCR / delivery checks.
            allowed, filter_reasons, rsi_val = check_all_entry_filters(
                sym, mem, key, is_bullish, now, nifty_pct, today_entries, vix_val,
                cp=cp, nifty_sheet=nifty_sheet, bm_data=bm_data,
            )
        for reason in filter_reasons:
            print(f"[FILTER] {sym}: {reason}")
        if not allowed:
            # v15.28: if this candidate failed ONLY the volume gate (every
            # other filter already passed), log it as a shadow/phantom entry
            # — never trades it, just observes whether it would have worked.
            mem = log_volume_gate_shadow(nifty_sheet, mem, now, sym, filter_reasons, cp, sl, tgt)
            continue

        # Result/event day gap check
        # v15.23 BUG FIX: prev_close (`_LP_`) never exists for a fresh WAITING
        # candidate, so this guard was silently skipped for every first entry —
        # a stock gapping >6% on results COULD be bought. Fall back to the live
        # Nifty200 "%Change" column when memory has no previous close.
        prev_close = get_last_price(mem, key)
        gap_pct = None
        if prev_close > 0:
            gap_pct = abs((cp - prev_close) / prev_close) * 100
        else:
            _sheet_dp = _read_nifty200_day_pct(nifty_sheet, sym)
            if _sheet_dp is not None:
                gap_pct = abs(_sheet_dp)
        if gap_pct is not None and gap_pct > 6.0:
            print(f"[STEP A] {sym}: gap {gap_pct:.1f}% > 6% — skip")
            continue

        capital = CASH_CAPITAL if cash else get_capital_bm(bm_data, sym)
        rank    = get_rank_bm(bm_data, sym)
        atr     = _read_atr_from_nifty200(nifty_sheet, sym)
        if atr <= 0 and sl > 0 and cp > 0: atr = (cp - sl) / 2.0

        # Promote to TRADED — v15.5: single batched K:M update saves 2 API calls per entry
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        try:
            log_sheet.update(f"K{i}:M{i}", [["✅ TRADED (PAPER)", cp, now_str]])
        except Exception as e:
            print(f"[STEP A] {sym}: update failed: {e}"); continue

        mem = save_atr_to_mem(mem, key, atr)
        mem = set_tsl(mem, key, sl)
        mem = set_last_price(mem, key, cp)
        mem = set_max_price(mem, key, cp)
        if cash:
            mem = _mem_set(mem, f"{today_s}_CASH_{key}", "1")
            mem = _mem_set(mem, f"{key}_MODE", "CASH")
            print(f"[CASH ENTRY] {sym} @ ₹{cp:.2f} | SL ₹{sl:.2f} | Tgt ₹{tgt:.2f}")
        else:
            today_entries += 1
            # v15.23 BUG FIX (real BUG-E): `_ENTRY_` is now written for SWING
            # entries ONLY. Cash used to write it too, and the counter's
            # `not startswith(date_CASH_)` filter could never exclude an
            # `_ENTRY_` part — so cash trades still ate the 3/day swing budget.
            mem = _mem_set(mem, f"{today_s}_ENTRY_{key}", "1")

        print(f"[ENTRY] {sym} @ ₹{cp:.2f} | RSI:{rsi_val} | Nifty:{nifty_pct:+.2f}% | #{today_entries}")

        msg_advance = build_entry_advance(sym, cp, stage, sl, tgt, rr_str, ttype, atr,
                                          rank, capital, is_bullish, rsi_val, nifty_pct,
                                          opt_signal, opt_strike, opt_expiry, opt_theta)
        msg_premium = build_entry_premium(sym, cp, stage, sl, tgt, rr_str, ttype, atr,
                                          rank, capital, is_bullish, rsi_val, nifty_pct,
                                          opt_signal, opt_strike, opt_expiry, opt_theta,
                                          mem=mem, now=now,
                                          opt_tag=_read_opt_tag_from_nifty200(nifty_sheet, sym),
                                          bm_data=bm_data)
        msg_basic   = build_entry_basic(sym, cp, stage, to_f(row[C_PNL]))
        # Append the educational/not-SEBI disclaimer to every member alert.
        send_basic(msg_basic + ALERT_DISCLAIMER)
        send_advance(msg_advance + ALERT_DISCLAIMER)
        send_premium(msg_premium + ALERT_DISCLAIMER)

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
        # v15.24: strike/expiry from cols V/W for the premium-aware exit note
        opt_stk = str(row[C_OPT_STRIKE]).strip()
        opt_exp = str(row[C_OPT_EXPIRY]).strip()

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
                              today_str, mem, key, is_target_hit=False, qty=qty,
                              opt_strike=opt_stk, opt_expiry=opt_exp)
            mem = _clear_mem_keys(mem, key); continue

        # v15.25 — OPTION-type trades exit per the ALERT's own rules (ledger
        # honesty; the EICHERMOT option trade was closed by the generic stock
        # time-stop the alert never mentioned): 20% est-loss hard cap (🔒 owner
        # rule — fires before the wider stock SL), expiry-week exit, and
        # v15.26 the 2-TRADING-DAY exit (alert now says options are intraday/
        # max 1-2 din — owner rule 2026-07-18). Stock SL/TSL/target checks
        # below stay unchanged (stock-anchored, exactly what the alert says).
        if is_option_trade(ttype):
            _lev = _row_option_leverage(sym, ent, ent_time, opt_stk, opt_exp, now)
            _oreason = _option_ledger_exit(pnl_pct, _lev, stage, opt_exp, ent_time, now)
            if _oreason:
                mem = _exit_trade(log_sheet, hist_sheet, i, sym, ent, cp, tgt, sl, cur_tsl,
                                  atr, ttype, strat, stage, ent_time, now, _oreason,
                                  today_str, mem, key, is_target_hit=False, qty=qty,
                                  opt_strike=opt_stk, opt_expiry=opt_exp)
                mem = _clear_mem_keys(mem, key); continue

        # TSL — pass actual entry time so hold check works correctly.
        # v15.7: track effective TSL (max of cur and new). calc_new_tsl caps the
        # returned new_tsl at cp*0.99, which on gap-down can be LESS than cur_tsl.
        # The `if new_tsl > cur_tsl` guard correctly avoids lowering stored TSL,
        # but the exit check below must compare cp against the EFFECTIVE stored
        # TSL — not the capped recomputed value. Otherwise gap-down below an
        # activated TSL never triggers exit (cp <= cp*0.99 is always False).
        new_tsl, tsl_reason = calc_new_tsl(cp, ent, sl, atr, ttype, mem, key, now, ent_time)
        if new_tsl > cur_tsl:
            mem = set_tsl(mem, key, new_tsl)
            print(f"[TSL] {sym}: {cur_tsl:.2f} → {new_tsl:.2f} ({tsl_reason})")
            _send_tsl_update(sym, cp, ent, new_tsl, pnl_pct, pnl_rs, tsl_reason)
            cur_tsl = new_tsl   # v15.7: keep local in sync with stored
            # v15.9 BUG-B: write TSL to AlertLog column O so the value is visible
            # to the user, the website webview, and any AppScript display logic.
            # Best-effort — TSL state lives in BotMemory; sheet is presentation.
            try:
                log_sheet.update(f"O{i}", [[round(new_tsl, 2)]])
            except Exception as e:
                print(f"[TSL O-write] {sym}: {e}")

        if cp <= cur_tsl:
            mem = _exit_trade(log_sheet, hist_sheet, i, sym, ent, cp, tgt, sl, cur_tsl,
                              atr, ttype, strat, stage, ent_time, now, "🔔 TRAILING SL HIT",
                              today_str, mem, key, is_target_hit=False, qty=qty,
                              opt_strike=opt_stk, opt_expiry=opt_exp)
            mem = _clear_mem_keys(mem, key); continue

        # Target hit — SET RE-ENTRY COOLDOWN
        if tgt > 0 and cp >= tgt:
            mem = _exit_trade(log_sheet, hist_sheet, i, sym, ent, cp, tgt, sl, new_tsl,
                              atr, ttype, strat, stage, ent_time, now, "🎯 TARGET HIT",
                              today_str, mem, key, is_target_hit=True, qty=qty,
                              opt_strike=opt_stk, opt_expiry=opt_exp)
            mem = _clear_mem_keys(mem, key); continue

        # v15.10 Batch 2 — PARTIAL BOOK ALERT @ PARTIAL_BOOK_TRIGGER_PCT.
        # One-shot per trade, gated by {key}_PB1 flag. Paper trading: alert only,
        # we don't tamper with sheet qty so reported P/L stays clean. In live
        # trading (Phase 4) this branch will fire a real 50% sell.
        if pnl_pct >= PARTIAL_BOOK_TRIGGER_PCT and not _mem_get(mem, f"{key}_PB1"):
            mem = _mem_set(mem, f"{key}_PB1", today_str)
            _send_partial_book_alert(sym, cp, ent, pnl_pct, qty, cur_tsl)

        # v15.10 Batch 2 — TIME STOP. After TIME_STOP_DAYS trading days, if the
        # trade has not delivered TIME_STOP_MIN_GAIN_PCT, exit and free the slot.
        # Runs AFTER target/TSL checks above so winners are never cut early.
        # Cash intraday trades skip time stop (they have their own 3 PM force exit).
        # v15.25: OPTION trades skip it too — their time rules are the alert's
        # own (expiry-week + v15.26 OPTION_MAX_TDAYS=2, handled above). Exception: if the
        # expiry cell doesn't parse, the generic time stop stays as the
        # fail-open backstop so a bad cell can't mean "hold forever".
        if not is_cash_trade(ttype) and not (is_option_trade(ttype) and _parse_expiry(opt_exp) is not None):
            # v15.23: TRADING days (spec since v15.10) — calendar counting cut
            # winners ~2 days early across weekends (Wed entry = "5 days" by Mon).
            hd = calc_trading_hold_days(ent_time, now)
            if hd >= TIME_STOP_DAYS and pnl_pct < TIME_STOP_MIN_GAIN_PCT:
                mem = _exit_trade(log_sheet, hist_sheet, i, sym, ent, cp, tgt, sl, cur_tsl,
                                  atr, ttype, strat, stage, ent_time, now,
                                  f"⏰ TIME STOP ({hd}d, +{pnl_pct:.1f}%)",
                                  today_str, mem, key, is_target_hit=False, qty=qty,
                                  opt_strike=opt_stk, opt_expiry=opt_exp)
                mem = _clear_mem_keys(mem, key); continue

    return mem


def _send_partial_book_alert(sym, cp, ent, pnl_pct, qty, tsl_now):
    """v15.10 Batch 2 — fires once per trade when unrealised gain crosses
    PARTIAL_BOOK_TRIGGER_PCT. Goes to Advance + Premium (educational signal)."""
    booked   = int((qty or 0) // 2)
    book_val = round(booked * cp, 0)
    msg = (
        f"💰 <b>PARTIAL BOOK SIGNAL</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Stock: {sym.replace('NSE:', '')}\n"
        f"LTP ₹{cp:.2f} | Entry ₹{ent:.2f} | <b>+{pnl_pct:.2f}%</b>\n\n"
        f"Recommended action:\n"
        f"   ✅ Book 50% ({booked} sh ≈ ₹{book_val:,.0f}) — locks profit\n"
        f"   📈 Hold remaining 50% with TSL ₹{tsl_now:.2f}\n"
        f"   🎯 Let winners ride to target on the leftover qty\n\n"
        f"<i>Why: removing initial risk turns this into a free trade.</i>"
    )
    send_advance_and_premium(msg + ALERT_DISCLAIMER)


def _send_tsl_update(sym, cp, ent, new_tsl, pnl_pct, pnl_rs, reason):
    msg = (
        f"🔔 <b>TSL UPDATE</b>\n"
        f"{sym.replace('NSE:','')} LTP ₹{cp:.2f} | P/L {pnl_pct:+.2f}%\n"
        f"Trail SL: ₹{new_tsl:.2f} — {reason}\nP/L: ₹{pnl_rs:+.0f}"
    )
    send_advance_and_premium(msg + ALERT_DISCLAIMER)


def _exit_trade(log_sheet, hist_sheet, row_idx, sym, ent, exit_p, tgt, sl, tsl_at_exit,
                atr, ttype, strat, stage, ent_time, now, reason, today_str, mem, key,
                is_target_hit=False, qty=0, opt_strike="", opt_expiry=""):
    """
    Exit trade, write to History, send Telegram.
    v15.0: If is_target_hit=True, set re-entry cooldown in memory.
    v15.2: Use actual trade capital from BotMemory, not hardcoded CAPITAL_MED.
    v15.5: qty parameter — use actual sheet quantity if provided. Fixes mismatch
    where pnl_rs was recalculated as cap//ent which differs from sheet qty when
    cmp differed from ent at entry time (gaps between scanner and Python entry).
    """
    cap      = get_capital_from_mem(mem, key)
    pnl_pct  = round(((exit_p - ent) / ent) * 100, 2) if ent > 0 else 0
    result   = "WIN ✅" if exit_p > ent else "LOSS ❌"
    hold_str = calc_hold_str(ent_time, now)
    days     = calc_hold_days(ent_time, now)
    # v15.5: prefer sheet qty (canonical position size), fall back to cap//ent
    eff_qty  = int(qty) if qty and qty > 0 else (int(cap // ent) if ent > 0 else 0)
    pnl_rs   = round((exit_p - ent) * eff_qty, 2) if ent > 0 else 0

    # v15.16: for option trades, estimate the option-premium P/L (stock P/L
    # understates it). Display only — numeric ledger columns keep the stock P/L.
    # v15.24: when the sheet's Strike (col V "2100 CE Aug") + Expiry (col W
    # "25-Aug-2026") parse and HV is available, use a premium-aware leverage
    # (Δ·S/premium at ENTRY, option_intelligence.est_option_leverage) instead
    # of the flat 10× guess; any missing piece → flat 10× exactly as before.
    opt_note = ""
    if is_option_trade(ttype):
        # v15.25: shared helper (same leverage the step_b 20%-cap check uses)
        eff_lev  = _row_option_leverage(sym, ent, ent_time, opt_strike, opt_expiry, now)
        opt_pct  = round(pnl_pct * eff_lev, 0)
        opt_note = f"Option ≈ {opt_pct:+.0f}% (est. ~{eff_lev:.0f}×, ITM ~0.7Δ; stock {pnl_pct:+.2f}%)"

    try:
        log_sheet.update(f"K{row_idx}", [[f"EXITED ({reason})"]])
    except Exception as e:
        print(f"[EXIT] Sheet update: {e}")

    # v15.18: Entry Date must be the REAL entry date (from AlertLog ent_time),
    # not today_str — History showed Entry Date == Exit Date on every trade.
    try:
        datetime.strptime(str(ent_time)[:10], '%Y-%m-%d')
        ent_date = str(ent_time)[:10]
    except Exception:
        ent_date = today_str

    try:
        hist_sheet.append_row([
            sym, ent_date, ent, today_str, exit_p,
            f"{pnl_pct:.2f}%", result, strat, reason, ttype,
            sl, tsl_at_exit, get_max_price(mem, key), atr, days, cap, pnl_rs, opt_note
        ])
    except Exception as e:
        print(f"[EXIT] History: {e}")

    # ── v15.0: re-entry cooldown after TARGET HIT.
    # ── v15.17: ALSO set the cooldown after a LOSING exit — prevents the bot
    #    from immediately re-buying a name that just failed. Audit finding:
    #    EICHERMOT was re-entered after a loss and lost again. Same proven RECD
    #    mechanism; the cooldown key survives _clear_mem_keys so it persists.
    is_loss    = exit_p < ent
    set_cd     = is_target_hit or is_loss
    if set_cd:
        mem = set_reentry_cooldown(mem, key, today_str)

    print(f"[EXIT] {sym} @ ₹{exit_p:.2f} | {pnl_pct:+.2f}% | {result} | {reason} | RECD:{set_cd}")

    msg = (
        f"{'🎯' if 'TARGET' in reason else '🔔' if 'TRAIL' in reason else '❌'} "
        f"<b>TRADE CLOSED — {result}</b>\n\n"
        f"Stock: {sym.replace('NSE:','')}\n"
        f"Entry: ₹{ent:.2f} → Exit: ₹{exit_p:.2f}\n"
        f"P/L: <b>{pnl_pct:+.2f}% (₹{pnl_rs:+.0f})</b>\n"
        + (f"📊 {opt_note}\n" if opt_note else "")
        + f"Hold: {hold_str} | {reason}\n"
        f"TSL at exit: ₹{tsl_at_exit:.2f}"
    )
    if set_cd:
        msg += f"\n⏳ Re-entry blocked for {REENTRY_COOLDOWN_DAYS} trading days"

    send_advance_and_premium(msg + ALERT_DISCLAIMER)
    if exit_p > ent:
        basic_exit = (
            f"✅ <b>TRADE CLOSED — {sym.replace('NSE:', '')}</b>\n"
            f"₹{ent:.2f} → ₹{exit_p:.2f} | <b>{pnl_pct:+.2f}% (₹{pnl_rs:+.0f})</b>\n"
            f"Hold: {hold_str} | {reason}\n\n"
            f"📈 Get live entry + exit alerts\n"
            f"<b>Join Advance @ ₹699/month</b>\n"
            f"📱 ai360trading.in/membership"
        )
    else:
        basic_exit = (
            f"❌ <b>TRADE CLOSED — {sym.replace('NSE:', '')}</b>\n"
            f"₹{ent:.2f} → ₹{exit_p:.2f} | {pnl_pct:+.2f}% | {reason}\n"
            f"🛡️ Trailing SL protected capital — loss controlled\n\n"
            f"📊 Real-time TSL alerts → Advance/Premium\n"
            f"<b>Join Advance @ ₹699/month</b>\n"
            f"📱 ai360trading.in/membership"
        )
    send_basic(basic_exit + ALERT_DISCLAIMER)

    return mem


def _clear_mem_keys(mem, key):
    # v15.10: also clear PB1 (partial book fired) flag and MODE so the next
    # entry for this symbol (after cooldown) starts with a clean slate.
    prefixes = [f"{key}_TSL_", f"{key}_MAX_", f"{key}_LP_", f"{key}_ATR_",
                f"{key}_PB1=", f"{key}_MODE="]
    parts    = [p for p in mem.split(',') if p.strip() and not any(p.startswith(px) for px in prefixes)]
    return ','.join(parts)


# ══════════════════════════════════════════════════════════════════════════════
# RUNTIME MEMORY — BotMemory sheet (replaces Y1 cell in AlertLog)
# Reason: AlertLog is shown as webview on ai360trading.in — keeping it clean
#         for followers. All runtime state now lives in BotMemory sheet only.
# ══════════════════════════════════════════════════════════════════════════════

def read_runtime_mem(bm_sheet) -> str:
    """
    Read the runtime memory string from BotMemory sheet.
    Looks for row where column A = RUNTIME_MEM_KEY ("_RUNTIME_MEM").
    Returns empty string if not found (first run).
    """
    try:
        for row in bm_sheet.get_all_values()[1:]:   # skip header
            if len(row) >= 2 and row[0].strip() == RUNTIME_MEM_KEY:
                val = row[1].strip()
                print(f"[MEM] BotMemory loaded: {len(val):,} chars")
                return val
        print("[MEM] _RUNTIME_MEM not found in BotMemory — first run or reset")
    except Exception as e:
        print(f"[MEM] BotMemory read error: {e}")
    return ""


def write_runtime_mem(bm_sheet, mem_str: str):
    """
    Write the runtime memory string to BotMemory sheet.
    Updates existing _RUNTIME_MEM row in-place, or appends if not found.
    """
    try:
        now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
        rows    = bm_sheet.get_all_values()
        for i, row in enumerate(rows[1:], start=2):
            if len(row) >= 1 and row[0].strip() == RUNTIME_MEM_KEY:
                bm_sheet.update(f"B{i}:C{i}", [[mem_str, now_str]])
                print(f"[MEM] BotMemory saved: {len(mem_str):,} chars (row {i})")
                return
        # Row not found — create it
        bm_sheet.append_row([RUNTIME_MEM_KEY, mem_str, now_str, "", "STATE"])
        print(f"[MEM] BotMemory: created _RUNTIME_MEM ({len(mem_str):,} chars)")
    except Exception as e:
        print(f"[MEM] BotMemory write error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# GOOD MORNING — 8:45 AM
# ══════════════════════════════════════════════════════════════════════════════

def send_good_morning(log_sheet, mem, is_bullish, nifty_cmp, nifty_dma, nifty_pct, now):
    flag_key = now.strftime("%Y-%m-%d") + "_AM"
    # v15.4: exact-key lookup (was substring `in mem` — safe in practice but fragile)
    if _mem_get(mem, flag_key):
        print(f"[GM] Already sent today — skip"); return mem

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
        f"RSI filter: < {RSI_MAX_BULLISH if is_bullish else RSI_MAX_BEARISH}{f' (leaders up on the day allowed to {RSI_HOT_MAX:.0f})' if is_bullish else ''} | Re-entry: {REENTRY_COOLDOWN_DAYS}d cooldown after target\n\n"
        f"{'Watching: ' + ', '.join(waiting_stocks[:5]) if waiting_stocks else 'No WAITING stocks'}\n\n"
        f"<i>{VERSION} — entry-quality: reversal veto + resistance-room veto + loss cooldown + best-of ranking + time-fair volume gate + real F&O option eligibility</i>"
    )
    watchlist_line = f"📋 Watchlist: {waiting} stock(s) identified today" if waiting else "📋 No setups in watchlist yet — scan runs at market open"
    msg_basic = (
        f"🌅 <b>Good Morning — {now.strftime('%d %b %Y')}</b>\n"
        f"Market: {regime} | Nifty: ₹{nifty_cmp:.0f}\n\n"
        f"{watchlist_line}\n"
        f"💼 Active trades: {traded}/{MAX_TRADES}\n\n"
        f"🔒 Entry price, SL and Target sent to Advance/Premium only\n"
        f"📈 <b>Join Advance @ ₹699/month</b>\n"
        f"📱 ai360trading.in/membership"
    )
    send_advance_and_premium(msg_adv); send_basic(msg_basic)
    print(f"[GM] Sent — {waiting} waiting, {traded} active")
    return _mem_set(mem, flag_key, "1")


# ══════════════════════════════════════════════════════════════════════════════
# MID-DAY PULSE — 12:28-12:38
# ══════════════════════════════════════════════════════════════════════════════

def send_midday_pulse(log_sheet, mem, now, is_bullish):
    flag_key = now.strftime("%Y-%m-%d") + "_MD"
    # v15.4: exact-key lookup (was substring `in mem` — safe in practice but fragile)
    if _mem_get(mem, flag_key):
        print(f"[MIDDAY] Already sent today — skip"); return mem
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
        basic_md = (
            f"📊 <b>Mid-Day Update — {now.strftime('%d %b %I:%M %p')}</b>\n"
            f"Active trades: {len(open_trades)}\n"
            f"{'💰' if total_pnl>=0 else '📉'} Unrealised P/L: ₹{total_pnl:+.0f}\n\n"
            f"🔒 TSL updates and trade details → Advance/Premium\n"
            f"📈 <b>Join Advance @ ₹699/month</b>\n"
            f"📱 ai360trading.in/membership"
        )
        send_advance_and_premium(msg); send_basic(basic_md)
        print(f"[MIDDAY] {len(open_trades)} trades, ₹{total_pnl:+.0f}")
        return _mem_set(mem, flag_key, "1")
    except Exception as e:
        print(f"[MIDDAY] {e}"); return mem


# ══════════════════════════════════════════════════════════════════════════════
# MARKET CLOSE — 15:15-15:45
# ══════════════════════════════════════════════════════════════════════════════

def send_market_close_summary(log_sheet, hist_sheet, mem, now, is_bullish, nifty_pct):
    flag_key = now.strftime("%Y-%m-%d") + "_PM"
    # v15.4: exact-key lookup (was substring `in mem` — safe in practice but fragile)
    if _mem_get(mem, flag_key):
        print(f"[CLOSE] Already sent today — skip"); return mem
    is_friday = (now.weekday() == 4)   # v15.16: weekend-gap guard fires on Fridays
    try:
        rows = log_sheet.get_all_values(); open_list = []; total_unrl = 0.0
        weekend_advice = []
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
            # v15.16 WEEKEND-GAP GUARD — 2 shut days can gap a stock past its SL
            # (e.g. PNBHOUSING opened well below its stop on a Monday). Advise per
            # position: book winners, EXIT laggards before the weekend.
            if is_friday:
                if pct <= 0:
                    weekend_advice.append(f"🔴 {sym} {pct:+.1f}% — laggard: EXIT before close (weekend gap risk)")
                elif pct < 3:
                    weekend_advice.append(f"🟡 {sym} {pct:+.1f}% — small gain: tighten SL or book partial")
                else:
                    weekend_advice.append(f"✅ {sym} {pct:+.1f}% — book ~50%, trail the rest over the weekend")
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
        # v15.16: weekend-gap guard block (Friday only, when something is held)
        if is_friday and weekend_advice:
            msg_adv += (
                f"\n\n⚠️ <b>WEEKEND-GAP GUARD (Friday)</b>\n"
                f"Markets shut 2 days — a stock can OPEN past your SL on Monday "
                f"(stops can't fire while shut). Per overnight hold:\n"
                + "\n".join(weekend_advice)
                + "\n<i>Rule: book partials on winners, exit laggards. Never carry a "
                  "losing position over the weekend just to hope.</i>"
            )
        pnl_emoji = "💰" if today_pnl >= 0 else "📉"
        msg_basic = (
            f"🔔 <b>Market Closed — {today_str}</b>\n"
            f"Today: {wins}✅ {losses}❌ | {pnl_emoji} Realised: ₹{today_pnl:+.0f}\n"
            f"Holding overnight: {len(open_list)} trade(s)\n"
            + (f"⚠️ Weekend gap risk — manage open trades before close\n\n" if (is_friday and open_list) else "\n")
            + f"📊 Full report and overnight TSL alerts sent to Advance/Premium\n"
            f"📈 <b>Join Advance @ ₹699/month</b>\n"
            f"📱 ai360trading.in/membership"
        )
        send_advance_and_premium(msg_adv); send_basic(msg_basic)
        print(f"[CLOSE] {wins}W {losses}L, {len(open_list)} overnight")
        return _mem_set(mem, flag_key, "1")
    except Exception as e:
        print(f"[CLOSE] {e}"); return mem


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# STEP C: CASH INTRADAY FORCE EXIT — 3:00 PM
# ══════════════════════════════════════════════════════════════════════════════

def step_c_intraday_exit(log_sheet, hist_sheet, nifty_sheet, mem, now):
    """
    Force-exit all 🔥 Cash Intraday trades at 3:00 PM regardless of P/L.
    Cash intraday = same-day trade — must not hold overnight.
    Runs only in the 3:00-3:15 PM window.
    """
    h, m = now.hour, now.minute
    if not (h == 15 and m <= 15):
        return mem

    today_str = now.strftime("%Y-%m-%d")
    exits = 0
    try:
        rows = log_sheet.get_all_values()
    except Exception as e:
        print(f"[CASH EXIT] Sheet read: {e}"); return mem

    for i, row in enumerate(rows[1:22], start=2):
        row    = pad(row)
        status = str(row[C_STATUS]).upper()
        if "TRADED" not in status or "EXITED" in status: continue
        ttype  = str(row[C_TRADE_TYPE]).strip()
        if not is_cash_trade(ttype): continue

        sym      = str(row[C_SYMBOL]).strip()
        cp       = to_f(row[C_LIVE_PRICE])
        ent      = to_f(row[C_ENTRY_PRICE])
        sl       = to_f(row[C_INITIAL_SL])
        tgt      = to_f(row[C_TARGET])
        strat    = str(row[C_STRATEGY]).strip()
        stage    = str(row[C_STAGE]).strip()
        ent_time = str(row[C_ENTRY_TIME]).strip()
        qty      = to_f(row[C_QTY])   # v15.5: pass actual sheet qty to _exit_trade
        key      = sym_key(sym)

        if cp <= 0: cp = ent
        atr = get_atr_from_mem(mem, key)
        if atr <= 0: atr = abs(ent - sl) / 2.0 if sl > 0 and ent != sl else ent * 0.02

        mem = _exit_trade(
            log_sheet, hist_sheet, i, sym, ent, cp, tgt, sl, sl,
            atr, ttype, strat, stage, ent_time, now, "⏰ INTRADAY TIME EXIT",
            today_str, mem, key, is_target_hit=False, qty=qty
        )
        mem = _clear_mem_keys(mem, key)
        exits += 1

    if exits > 0:
        print(f"[CASH EXIT] {exits} intraday trade(s) force-exited at 3 PM")
    return mem


# ══════════════════════════════════════════════════════════════════════════════
# MONTHLY P&L REPORT — first Monday of each month, fully automatic
# ══════════════════════════════════════════════════════════════════════════════

def _send_monthly_pnl(hist_sheet, now):
    """
    Calculates last calendar month's closed trades from History sheet.
    Sends performance summary to all Telegram channels.
    Runs first Monday of each month — zero manual task, runs forever.
    """
    try:
        first_day       = now.date().replace(day=1)
        last_month_end  = first_day - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        start = last_month_start.isoformat()
        end   = last_month_end.isoformat()
        month_str = last_month_end.strftime("%B %Y")

        rows = hist_sheet.get_all_values()[1:]
        wins = losses = 0; total_pnl = 0.0; trades = []

        for r in rows:
            while len(r) < 17: r.append("")
            exit_dt = str(r[3]).strip()
            if not exit_dt or not (start <= exit_dt <= end): continue
            sym = str(r[0]).replace("NSE:", "").strip()
            result = str(r[6]).upper()
            try: pnl_rs = float(str(r[16]).replace(",", ""))
            except: pnl_rs = 0.0
            if "WIN" in result: wins += 1
            elif "LOSS" in result: losses += 1
            total_pnl += pnl_rs
            trades.append((sym, pnl_rs))

        total = wins + losses
        if total == 0:
            print(f"[MONTHLY] No closed trades in {month_str}"); return

        win_rate  = round(wins / total * 100)
        pnl_emoji = "💰" if total_pnl >= 0 else "📉"
        trades_s  = sorted(trades, key=lambda x: x[1], reverse=True)
        best      = trades_s[0] if trades_s else None
        worst     = trades_s[-1] if len(trades_s) > 1 and trades_s[-1][1] < 0 else None

        b_msg = (
            f"📅 <b>MONTHLY RESULTS — {month_str}</b>\n"
            f"AI360Trading | Paper Trading\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{pnl_emoji} <b>Net P/L: ₹{total_pnl:+,.0f}</b>\n"
            f"✅ Jeet: {wins}  |  ❌ Haar: {losses}  |  Win Rate: {win_rate}%\n\n"
            f"📊 Poori monthly report → Advance/Premium members\n"
            f"📈 Upgrade karo ₹699/month → ai360trading.in/membership"
        )
        send_basic(b_msg)

        a_lines = [
            f"📅 <b>MONTHLY PERFORMANCE — {month_str}</b>",
            f"AI360Trading | Paper Trading",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"\n{pnl_emoji} <b>Net Realised P/L: ₹{total_pnl:+,.0f}</b>",
            f"Total Trades: {total}  |  Wins: {wins} ✅  |  Losses: {losses} ❌  |  Win Rate: {win_rate}%",
        ]
        if best:  a_lines.append(f"🏆 Best: <b>{best[0]}</b> ₹{best[1]:+,.0f}")
        if worst: a_lines.append(f"📉 Worst: <b>{worst[0]}</b> ₹{worst[1]:+,.0f}")
        a_lines.append("\n<i>Paper trading — educational results only</i>")
        send_advance_and_premium("\n".join(a_lines))
        print(f"[MONTHLY] {month_str}: {wins}W {losses}L ₹{total_pnl:+,.0f}")
    except Exception as e:
        print(f"[MONTHLY] {e}")


# ══════════════════════════════════════════════════════════════════════════════
# SHEET MAINTENANCE — weekly, prevents overflow
# ══════════════════════════════════════════════════════════════════════════════

def auto_maintain_sheets(bm_sheet, hist_sheet, mem, now):
    """
    Runs once per week (Monday during morning window).
    1. History > 500 rows: archive oldest 250 rows to HistoryArchive sheet.
    2. BotMemory > 400 rows: remove blank/empty rows.
    Prevents sheets from growing indefinitely and becoming slow.
    """
    if now.weekday() != 0:   # Monday only
        return mem

    flag_key = now.strftime("%Y-W%W") + "_MAINT"
    # v15.8 (BUG-5): exact-key lookup (was substring `in mem` — Batch 1 missed this site)
    if _mem_get(mem, flag_key):
        return mem

    print("[MAINTAIN] Weekly sheet maintenance starting...")

    # ── History: archive old rows when > HISTORY_MAX_ROWS ────────────────────
    try:
        rows = hist_sheet.get_all_values()
        data = rows[1:]  # exclude header
        if len(data) > HISTORY_MAX_ROWS:
            ss = hist_sheet.spreadsheet
            archive_name = "HistoryArchive"
            try:
                archive = ss.worksheet(archive_name)
            except Exception:
                archive = ss.add_worksheet(title=archive_name, rows=3000, cols=20)
                archive.append_row(rows[0])  # copy header to archive

            to_move = data[:250]
            archive.append_rows(to_move)
            remaining = [rows[0]] + data[250:]
            hist_sheet.clear()
            hist_sheet.update("A1", remaining)
            print(f"[MAINTAIN] History: moved 250 rows to HistoryArchive. Remaining: {len(remaining)-1}")
        else:
            print(f"[MAINTAIN] History: {len(data)} rows — no archive needed")
    except Exception as e:
        print(f"[MAINTAIN] History archive error: {e}")

    # ── BotMemory: remove blank rows when > BOTMEMORY_ALERT_ROWS ─────────────
    try:
        bm_rows = bm_sheet.get_all_values()
        print(f"[MAINTAIN] BotMemory: {len(bm_rows)} rows")
        if len(bm_rows) > BOTMEMORY_ALERT_ROWS:
            non_blank = [r for r in bm_rows if any(str(c).strip() for c in r)]
            removed = len(bm_rows) - len(non_blank)
            if removed > 0:
                bm_sheet.clear()
                bm_sheet.update("A1", non_blank)
                print(f"[MAINTAIN] BotMemory: removed {removed} blank rows. Now: {len(non_blank)}")
    except Exception as e:
        print(f"[MAINTAIN] BotMemory cleanup error: {e}")

    # ── Monthly P&L report: first Monday of each month ───────────────────────
    # today.day <= 7 → this is the first Monday of the month (within day 1-7)
    if now.day <= 7:
        monthly_flag = now.strftime("%Y-%m") + "_MONTHLY_PNL"
        # v15.8 (BUG-5): exact-key lookup (was substring `not in mem`)
        if not _mem_get(mem, monthly_flag):
            _send_monthly_pnl(hist_sheet, now)
            mem = _mem_set(mem, monthly_flag, "1")

    mem = _mem_set(mem, flag_key, "1")
    print("[MAINTAIN] Weekly maintenance done.")
    return mem


def send_test_messages():
    now = datetime.now(IST)
    msg = (
        f"✅ <b>TEST MESSAGE — AI360 Trading Bot {VERSION}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Time: {now.strftime('%d %b %Y %H:%M')} IST\n"
        f"Token: {'✅ OK' if TG_TOKEN else '❌ MISSING'}\n\n"
        f"If you see this, Telegram is working! 🎉"
    )
    r1 = send_basic(msg.replace("TEST MESSAGE", "TEST — BASIC CHANNEL"))
    r2 = send_advance(msg.replace("TEST MESSAGE", "TEST — ADVANCE CHANNEL"))
    r3 = send_premium(msg.replace("TEST MESSAGE", "TEST — PREMIUM CHANNEL"))
    print(f"[TEST] Basic:{r1} | Advance:{r2} | Premium:{r3}")
    print(f"[TEST] Token present: {bool(TG_TOKEN)}")
    print(f"[TEST] CHAT_BASIC: {'set' if CHAT_BASIC else 'MISSING'}")
    print(f"[TEST] CHAT_ADVANCE: {'set' if CHAT_ADVANCE else 'MISSING'}")
    print(f"[TEST] CHAT_PREMIUM: {'set' if CHAT_PREMIUM else 'MISSING'}")


# ══════════════════════════════════════════════════════════════════════════════
# v15.28 — VOLUME-GATE SHADOW TRACKER (owner: "is the 1.5x volume gate a hard
# gate that's throwing away good trades, or correctly protecting us?")
#
# The volume-confirmation gate is a binary hard gate — a stock at 1.49x pace
# is rejected exactly as hard as one at 0.5x. Nobody has ever measured what
# happens to the stocks it rejects. This logs a NEVER-TRADED "phantom" entry
# every time a candidate passes EVERY other filter (RECD/TIME/DAILY/NIFTY/
# VIX/RSI/RS) and fails ONLY on volume, using the exact same SL/target a real
# entry would have used, then scores it later with the same target/SL/
# TIME_STOP_DAYS rules real trades use. After enough data accumulates, the
# ShadowLedger tab answers the calibration question with evidence instead of
# assumption — the same approach that validated the RSI hot-leader exception
# in the 07-15 audit.
#
# SAFE BY DESIGN: reads/writes ONLY the ShadowLedger tab. Never touches
# AlertLog, History, BotMemory trade-state keys, never sends a Telegram
# alert, never affects a real position. Every function fails open — any
# error just skips shadow-tracking for that tick, the real bot is unaffected.
# ══════════════════════════════════════════════════════════════════════════════
SHADOW_SHEET_NAME = "ShadowLedger"
SHADOW_HEADER = ["Symbol", "Signal Date", "Entry (CMP)", "Volume Pace %", "RS",
                  "Signal", "SL", "Target", "Outcome", "Score P/L %",
                  "Scored Date", "Trading Days Held"]


def _get_shadow_sheet(nifty_sheet):
    """Lazily gets/creates the ShadowLedger tab. Reuses the already-authorized
    session via nifty_sheet.spreadsheet — no extra credential/API-quota cost.
    Fail-open: returns None on any error (missing perms, quota, etc.)."""
    try:
        ss = nifty_sheet.spreadsheet
        try:
            return ss.worksheet(SHADOW_SHEET_NAME)
        except gspread.exceptions.WorksheetNotFound:
            ws = ss.add_worksheet(title=SHADOW_SHEET_NAME, rows=2000, cols=len(SHADOW_HEADER))
            ws.update("A1", [SHADOW_HEADER])
            print(f"[SHADOW] created {SHADOW_SHEET_NAME} tab")
            return ws
    except Exception as e:
        print(f"[SHADOW] sheet access failed: {e} — shadow tracking skipped this tick")
        return None


def log_volume_gate_shadow(nifty_sheet, mem, now, sym, filter_reasons, cp, sl, tgt):
    """
    Called from step_a right where a real entry would have been rejected. If
    the LAST filter reason recorded is [VOL] (meaning every filter before it —
    RECD/TIME/DAILY/NIFTY/VIX/RSI/RS — already passed), this candidate failed
    on volume alone: log it as a shadow (never-traded) entry, once per stock
    per day. Uses the SAME sl/tgt the real AlertLog row already computed, so
    the phantom trade is directly comparable to a real one.
    """
    try:
        if not filter_reasons or not filter_reasons[-1].startswith("[VOL]"):
            return mem   # rejected for a different (or no) reason — not a volume near-miss
        today_s = now.strftime("%Y-%m-%d")
        key = sym_key(sym)
        flag = f"{today_s}_SHADOWVOL_{key}"
        if _mem_get(mem, flag):
            return mem   # already logged this stock today
        sheet = _get_shadow_sheet(nifty_sheet)
        if sheet is None or cp <= 0:
            return mem
        rel_vol = _read_nifty200_relvol(nifty_sheet, sym)
        rs_val  = _read_nifty200_rs(nifty_sheet, sym)
        sheet.append_row(
            [sym, today_s, cp, rel_vol, rs_val, "NEAR-MISS (VOL only)", sl, tgt,
             "PENDING", "", "", ""],
            value_input_option="USER_ENTERED",
        )
        mem = _mem_set(mem, flag, "1")
        print(f"[SHADOW] logged {sym} — passed every filter except volume "
              f"(pace {rel_vol:+.0f}%, RS {rs_val:+.1f})")
    except Exception as e:
        print(f"[SHADOW] log failed for {sym}: {e} — fail open")
    return mem


def score_volume_gate_shadow(nifty_sheet, now):
    """
    Once per tick: checks every PENDING ShadowLedger row and marks it WIN
    (target reached), LOSS (SL hit), or TIMEOUT (TIME_STOP_DAYS trading days
    passed with neither) — the same rules a real entry is monitored under.
    Read/writes ONLY the ShadowLedger tab. Fail-open: any error leaves rows
    PENDING for the next tick to retry, never crashes the caller.
    """
    try:
        sheet = _get_shadow_sheet(nifty_sheet)
        if sheet is None:
            return
        rows = sheet.get_all_values()
        if len(rows) < 2:
            return
        updates = []
        for i, r in enumerate(rows[1:], start=2):
            if len(r) < 9 or r[8].strip() != "PENDING":
                continue
            sym, sig_date_s = r[0].strip(), r[1].strip()
            try:
                entry_cp = float(r[2]); sl = float(r[6]); tgt = float(r[7])
            except Exception:
                continue
            cmp_now = _read_nifty200_field(nifty_sheet, sym, ["CMP"], subs=["cmp", "ltp"])
            if not cmp_now or cmp_now <= 0:
                continue
            hd = calc_trading_hold_days(sig_date_s, now)
            outcome = None
            if tgt > 0 and cmp_now >= tgt:
                outcome = "WIN (target)"
            elif sl > 0 and cmp_now <= sl:
                outcome = "LOSS (SL)"
            elif hd >= TIME_STOP_DAYS:
                outcome = "TIMEOUT"
            if outcome:
                pnl_pct = round((cmp_now - entry_cp) / entry_cp * 100, 2) if entry_cp > 0 else 0.0
                updates.append((i, sym, outcome, pnl_pct, now.strftime("%Y-%m-%d"), hd))
        for i, sym, outcome, pnl_pct, scored_at, hd in updates:
            sheet.update(f"I{i}:L{i}", [[outcome, pnl_pct, scored_at, hd]])
            print(f"[SHADOW] scored row {i} ({sym}): {outcome} ({pnl_pct:+.2f}%)")
    except Exception as e:
        print(f"[SHADOW] scoring pass failed: {e} — fail open, will retry next tick")


def shadow_ledger_report(nifty_sheet) -> str:
    """On-demand plain-language summary of everything scored so far — answers
    'is the volume gate well-calibrated?' with real numbers. Returns a Telegram-
    ready string. Fail-open: returns an explanatory string on any error."""
    try:
        sheet = _get_shadow_sheet(nifty_sheet)
        if sheet is None:
            return "⚠️ Shadow ledger unavailable right now."
        rows = sheet.get_all_values()[1:]
        if not rows:
            return "📊 <b>Volume-Gate Shadow Ledger</b>\nNo candidates logged yet."
        scored  = [r for r in rows if len(r) > 8 and r[8].strip() not in ("", "PENDING")]
        pending = len(rows) - len(scored)
        if not scored:
            return (f"📊 <b>Volume-Gate Shadow Ledger</b>\n"
                     f"{len(rows)} near-miss candidate(s) logged so far, "
                     f"{pending} still pending (needs {TIME_STOP_DAYS} trading days to score).\n"
                     f"Not enough scored data yet — check back in a few days.")
        wins   = [r for r in scored if r[8].startswith("WIN")]
        losses = [r for r in scored if r[8].startswith("LOSS")]
        others = [r for r in scored if r not in wins and r not in losses]
        pnls   = [float(r[9]) for r in scored if len(r) > 9 and r[9].strip()]
        avg_pnl = round(sum(pnls) / len(pnls), 2) if pnls else 0.0
        win_rate = round(len(wins) / len(scored) * 100) if scored else 0
        return (
            f"📊 <b>Volume-Gate Shadow Ledger</b> — would-have-been trades if the "
            f"1.5x volume gate didn't exist\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>{len(scored)} scored</b> ({pending} still pending) · "
            f"<b>{win_rate}% would-be win rate</b> · avg P/L {avg_pnl:+.2f}%\n"
            f"🎯 Target hit: {len(wins)} · 🛑 SL hit: {len(losses)} · ⏰ Timeout: {len(others)}\n\n"
            f"<i>If the would-be win rate/avg P/L here is meaningfully worse than the "
            f"real ledger's, the volume gate is protecting you correctly. If it's "
            f"similar or better, the gate may be too strict.</i>"
        )
    except Exception as e:
        return f"⚠️ Shadow ledger report failed: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# v15.15 — CONFIRMED-ACCUMULATION WATCH (the "corrected sector leader" case)
# ══════════════════════════════════════════════════════════════════════════════
ACCUM_MAX_DAILY = 1   # at most one accumulation signal per day (quality > quantity)

def scan_accumulation_watch(nifty_sheet, bm_sheet, mem, now, is_bullish):
    """
    Finds a genuine "buy the corrected SECTOR LEADER" setup that the normal
    breakout scan misses in a weak index — sector leader + FII accumulating +
    VALUE BUY/BASE PREPARED + price reclaimed its 20-DMA + sector rotating up.
    This is the falling-knife-vs-accumulation distinction (see entry_quality).

    SAFE BY DESIGN — this never writes AlertLog, so it CANNOT affect live trades
    or break the income pipeline:
      • Default = WATCH: sends one 'ACCUMULATION WATCH' alert per stock per day to
        Advance+Premium and records a shadow entry in BotMemory (to score later).
      • Set secret ACCUM_AUTOTRADE=true to graduate it to real (paper) auto-entry
        once the shadow track record looks good — a one-flag change, no code edit.
    Fully fail-open. Only runs in a BEARISH/weak index (bullish already trades these).
    """
    if not _EQ_AVAILABLE or nifty_sheet is None or is_bullish:
        return mem
    today_s = now.strftime("%Y-%m-%d")
    try:
        rows = _nifty200_rows(nifty_sheet)
        if not rows or len(rows) < 2:
            return mem
        col = lambda *names, subs=None: _find_nifty200_col(nifty_sheet, list(names), subs)
        c_sym  = 0
        c_cmp  = col("CMP", subs=["cmp", "ltp"])
        c_lt   = col("Leader_Type", subs=["leadertype"])
        c_fii  = col("FII_Buy_Zone", subs=["fiibuyzone"])
        c_fa   = col("FINAL_ACTION", subs=["finalaction"])
        c_rs   = col("RS")
        c_dma  = col("20_DMA", subs=["20dma", "20_dma"])
        c_sect = col("Sector_Rotation_Score", subs=["sectorrotation"])
        if min(c_cmp, c_lt, c_fii, c_fa, c_dma) < 0:
            return mem   # required columns missing → fail-open, do nothing
        found = 0
        for r in rows[1:]:
            if found >= ACCUM_MAX_DAILY:
                break
            if len(r) <= max(c_cmp, c_lt, c_fii, c_fa, c_dma):
                continue
            sym = str(r[c_sym]).replace("NSE:", "").strip()
            if not sym or "NIFTY" in sym.upper():
                continue
            ok, why = eq.is_confirmed_accumulation(
                leader_type=r[c_lt], fii_zone=r[c_fii], final_action=r[c_fa],
                rs=to_f(r[c_rs]) if c_rs >= 0 else 0.0,
                cmp=to_f(r[c_cmp]), dma20=to_f(r[c_dma]),
                sector_rotation=to_f(r[c_sect]) if c_sect >= 0 else 0.0,
            )
            if not ok:
                continue
            key = sym_key(sym)
            flag = f"{today_s}_ACCUMW_{key}"
            if _mem_get(mem, flag):     # already alerted this stock today
                continue
            cmp = to_f(r[c_cmp]); dma = to_f(r[c_dma]); rs = to_f(r[c_rs]) if c_rs >= 0 else 0.0
            atr = _read_atr_from_nifty200(nifty_sheet, sym) or (cmp * 0.03)
            sl  = round(min(dma * 0.985, cmp - 2 * atr), 2)   # hard stop just below the reclaimed 20-DMA
            tgt = round(cmp + 5 * atr, 2)
            mem = _mem_set(mem, flag, "1")
            found += 1
            auto = os.environ.get("ACCUM_AUTOTRADE", "").lower() in ("1", "true", "yes")
            print(f"[ACCUM] {sym}: {why} | CMP ₹{cmp:.2f} SL ₹{sl:.2f} Tgt ₹{tgt:.2f} RS {rs:.1f} | autotrade={auto}")
            msg = (
                f"🏦 <b>ACCUMULATION WATCH</b> {'(half-size)' if auto else '(watch)'}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>{sym}</b> — corrected sector leader, FII accumulating, reclaimed 20-DMA\n"
                f"CMP ₹{cmp:.2f} | SL ₹{sl:.2f} | Target ₹{tgt:.2f}\n"
                f"RS {rs:+.1f} · sector rotating up\n\n"
                f"<i>Lower-risk accumulation in a weak market — small/staggered size, "
                f"hard stop below the base. Not a breakout chase.</i>"
            )
            send_advance_and_premium(msg + ALERT_DISCLAIMER)
        return mem
    except Exception as e:
        print(f"[ACCUM] scan errored: {e} — fail open")
        return mem


def main():
    bot_mode = os.environ.get('BOT_MODE', 'trade')

    if bot_mode == 'test_telegram':
        print("[MODE] test_telegram — sending test messages")
        send_test_messages()
        return

    now      = datetime.now(IST)
    today_s  = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    dow      = now.weekday()

    print(f"\n{'='*55}")
    print(f"AI360 Trading Bot {VERSION} — {now.strftime('%d %b %Y %H:%M')} IST")
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

    if bot_mode == 'shadow_report':
        print("[MODE] shadow_report — sending volume-gate shadow ledger summary")
        send_advance_and_premium(shadow_ledger_report(nifty))
        return

    # v15.3: Check AppScript write lock (_AS_LOCK in BotMemory).
    # AppScript sets this key during morning cleanup (clearWaitingRowsOnly) when
    # it briefly clears AlertLog before rewriting traded rows. Reading during that
    # window returns blank rows. Lock expires after 2 minutes to self-heal if
    # AppScript crashes mid-write.
    try:
        bm_all = bm.get_all_values()
        for _bm_row in bm_all[1:]:
            if len(_bm_row) >= 3 and _bm_row[0].strip() == "_AS_LOCK" and _bm_row[2].strip():
                _lock_str = _bm_row[2].strip()[:19]
                _lock_t   = IST.localize(datetime.strptime(_lock_str, "%Y-%m-%d %H:%M:%S"))
                _lock_age = (datetime.now(IST) - _lock_t).total_seconds()
                if _lock_age < 120:
                    print(f"[LOCK] AppScript writing AlertLog (lock age {_lock_age:.0f}s) — skip this cycle")
                    return
                else:
                    print(f"[LOCK] Stale lock ignored ({_lock_age:.0f}s old)")
                break
    except Exception as _lock_err:
        print(f"[LOCK] Check error (safe to proceed): {_lock_err}")

    is_bullish, nifty_cmp, nifty_dma, nifty_pct = get_market_regime(nifty)

    mem = read_runtime_mem(bm)

    # Merge dynamically-fetched holidays from BotMemory (set by fetch_holidays.py)
    bm_raw = get_bm_data(bm)
    load_dynamic_holidays(bm_raw)

    # Weekly sheet maintenance (Monday morning only, once per week)
    if "08:44" <= time_str <= "08:52":
        mem = auto_maintain_sheets(bm, hist, mem, now)

    # v15.6: removed obsolete v15.1 Y1 migration code. Migration was completed long
    # ago and the cleanup was running on every tick (~288 ticks/day) for no benefit.
    mem = clean_mem(mem)

    # Count today's SWING entries only (cash intraday tracked separately via _CASH_
    # keys with its own CASH_MAX_DAILY limit). v15.23: the v15.9 BUG-E filter here
    # was ineffective (an `_ENTRY_` part can never start with `_CASH_`); the real
    # fix is in step_a — cash entries no longer write `_ENTRY_` keys at all.
    today_entries = sum(
        1 for p in mem.split(",")
        if p.strip().startswith(today_s + "_ENTRY_")
    )

    if "08:44" <= time_str <= "08:52":
        mem = send_good_morning(log, mem, is_bullish, nifty_cmp, nifty_dma, nifty_pct, now)

    # v15.10: fetch India VIX once per tick (one yfinance call, fail-open).
    # Used as a regime filter for new entries only; existing trades continue
    # to be monitored / exited normally regardless of VIX.
    vix_val = get_india_vix() if is_market_hours(now) else 0.0

    if is_market_hours(now):
        mem, today_entries = step_a_enter_trades(
            log, nifty, bm, mem, now, is_bullish, nifty_pct, today_entries, vix_val
        )
        mem = step_b_monitor_trades(log, hist, nifty, mem, now, is_bullish)

        # v15.15 — confirmed-accumulation watch (bearish/weak index only; the
        # function self-gates on is_bullish + ACCUM entry window). Fail-open.
        if (now.hour, now.minute) <= ENTRY_WINDOW_BEARISH_END:
            mem = scan_accumulation_watch(nifty, bm, mem, now, is_bullish)

        # v15.28 — score any PENDING volume-gate shadow entries (target/SL/
        # timeout check against today's CMP). Cheap (ShadowLedger tab only,
        # reuses the already-open Nifty200 sheet cache), fail-open.
        try:
            score_volume_gate_shadow(nifty, now)
        except Exception as _shadow_err:
            print(f"[SHADOW] scoring call errored (fail-open): {_shadow_err}")

        if "12:28" <= time_str <= "12:38":
            mem = send_midday_pulse(log, mem, now, is_bullish)

        # Cash intraday force-exit at 3:00 PM (before market close summary)
        if "15:00" <= time_str <= "15:15":
            mem = step_c_intraday_exit(log, hist, nifty, mem, now)

        if "15:15" <= time_str <= "15:45":
            mem = send_market_close_summary(log, hist, mem, now, is_bullish, nifty_pct)

    write_runtime_mem(bm, mem)

    print(f"[DONE] {time_str} IST | Bullish:{is_bullish} | Entries:{today_entries}")


if __name__ == "__main__":
    main()
