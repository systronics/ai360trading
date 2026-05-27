# SESSION.md — AI360Trading

---

## Last Updated: 2026-05-27

---

## Current Version Map

| File | Version | Last Changed |
|---|---|---|
| `trading_bot.py` | **v15.12** | 2026-05-27 (Batch 4 institutional edges: RS, volume, FII gate, PCR soft, delivery %) |
| `option_intelligence.py` | **v1.0** | 2026-05-27 (new — pure-Python option strike + risk module; ₹0/month, fail-open) |
| `institutional_edges.py` | **v1.0** | 2026-05-27 (new — 5 institutional filters; pure functions, fail-open) |
| `fetch_earnings.py` | **v1.0** | 2026-05-27 (new — NSE earnings calendar → BotMemory cache, BSE fallback) |
| `fetch_bhavcopy.py` | **v1.0** | 2026-05-27 (new — NSE bhavcopy + option chain → DLV_* + MKT_PCR_* keys) |
| `appscript.gs` | **v15.16** | 2026-05-27 (renamed from appscript_v14.gs + holiday list corrected — needs manual paste to Apps Script editor) |
| `ai_client.py` | v2.4 | May 2026 |
| `human_touch.py` | v2.2 | May 2026 |
| `generate_longterm.py` | **v1.6** | 2026-05-26 (BUG-3 RSI NaN + BUG-4 BOOK PARTIAL ladder) |
| `generate_education.py` | v1.1 | May 2026 |
| `generate_reel.py` | v2.1 | May 2026 |
| `generate_reel_morning.py` | v2.3 | May 2026 |
| `generate_shorts.py` | v3.3 | May 2026 |
| `generate_articles.py` | current | May 2026 |
| `generate_kids_video.py` | v2.3 | May 2026 |
| `refresh_cashwatchlist.py` | **v1.3** | 2026-05-25 (Batch 4) |
| `fetch_holidays.py` | **v1.2** | 2026-05-25 (Batch 4) |
| `token_refresh.py` | **v2.2** | 2026-05-25 (Batch 1) |
| `upload_youtube.py` | v2.2 | May 2026 |
| `upload_facebook.py` | v2.6 | May 2026 |
| `content_calendar.py` | **v2.3** | 2026-05-26 (SEO seeds shape fix) |
| `indian_holidays.py` | current | March 2026 |
| `.internal-ops.md` | 2026-05-25 | May 2026 |
| `CLAUDE.md` | created | 2026-05-25 |
| `CHANGELOG.md` | updated | 2026-05-25 |
| `SESSION.md` | updated | 2026-05-25 |
| `smartsync.bat` | created | 2026-05-25 |
| `instructions.txt` | updated | 2026-05-25 |
| `upload_instagram.py` | v1.0 | 2026-05-25 |

---

## Last Session Summary

**2026-05-27 (night):** Batch 4 institutional edges — `trading_bot.py` v15.11 → **v15.12** + 2 new files (institutional_edges.py + fetch_bhavcopy.py) + 1 new workflow.
- New module **`institutional_edges.py` v1.0** — five "smart money" filters: relative strength (≥+1% vs Nifty), volume confirmation (≥1.5×), FII regime gate (block longs if FII net ≤ −₹2000 Cr), PCR soft filter (informational only — PCR is contrarian), delivery % gate (≥40% indicates institutional accumulation). All pure functions, all fail-open.
- New fetcher **`fetch_bhavcopy.py` v1.0** + workflow **`fetch_bhavcopy.yml`** (Mon-Fri 20:00 IST). Parses NSE cash bhavcopy CSV for `DLV_{SYM}` rows + NSE option chain for `MKT_PCR_NIFTY` / `MKT_PCR_BANKNIFTY`. 5-day fallback if today's file missing.
- `trading_bot.py` `check_all_entry_filters` extended with 5 institutional gates. Each individually try/except'd so a buggy check cannot cascade.
- New self-healing helper `_find_nifty200_col()` — finds column by HEADER NAME match, not hardcoded index. Survives AppScript column additions automatically.
- Smoke tests confirmed all 5 filters block/allow correctly in both pass and fail-open scenarios.

**2026-05-27 (evening):** Batch 3 option-buying intelligence — `trading_bot.py` v15.10 → **v15.11** + 2 new files.
- New module **`option_intelligence.py` v1.0** — pure-Python smart-options engine. Pure-math NSE strike-step table (1/2/5/10/20/50/100). 20-day HV via yfinance as IV proxy. Earnings window reader (reads BotMemory cache). PE-side support for bearish regime. Stock-anchored exit recommendations.
- New fetcher **`fetch_earnings.py` v1.0** + workflow **`.github/workflows/fetch_earnings.yml`** (daily 18:30 IST). NSE event calendar → BSE fallback → existing cache. Self-repair: never marks GH Action failed if upstream APIs down.
- `trading_bot.py` `ce_candidate_flag(...)` now routes through `opt_intel.recommend_option(...)` for smart picks. Wrapped in try/except — if `option_intelligence` is missing or broken, bot falls back to v15.10 ATM/OTM path (graceful degradation).
- Bearish-regime options no longer silently skipped — PE side now supported.
- Exit text changed from "option −40%" to "stock −1.5%" (≈ option −15% at Δ0.7).
- Saved feedback memory **`feedback_free_forever_self_repair`** — captures Amit ji's principle that every component must be ₹0/month + auto-update + fail-open.

**2026-05-27 (afternoon):** Batch 2 profit protection — `trading_bot.py` v15.9 → **v15.10**.
- **ONE-R BREAKEVEN** — BE now activates at the SOONER of fixed-% threshold or +1R (initial risk distance). Floor at +0.8% to avoid tight-SL whipsaws. Behaviour only improves over v15.9 (BE never moves in later than before).
- **CHANDELIER TRAIL** — trail SL anchored to highest-price-reached minus atr*mult (not CMP). Trail can only rise. Locks much more of a parabolic run vs. the CMP-anchored formula. Cap at cp*0.99 retained.
- **PARTIAL BOOK @ +5%** — one-time Advance/Premium alert recommending "book 50%, trail rest". Paper trading keeps full-position P/L (no sheet qty tampering). Phase-4 live trading will actually halve the order. Flag stored as `{key}_PB1` so fires once per trade.
- **TIME STOP** — exit after 5 trading days if gain < +3%. Cash intraday exempt (has its own 3 PM force exit). Runs AFTER target/TSL checks so winners are never cut early.
- **INDIA VIX FILTER** — yfinance `^INDIAVIX` fetched once per tick; blocks new entries if VIX > 22. Fails open if fetch errors. Existing trades continue normal monitoring/exits.
- **Renamed `appscript_v14.gs` → `appscript.gs`** (filename mismatch with internal v15.16 was confusing). Historical CHANGELOG entries unchanged. AppScript editor doesn't care about filename — manual paste flow unchanged.

**2026-05-27 (morning):** Batch 1 safety fixes — `trading_bot.py` v15.8 → **v15.9**, `appscript.gs` v15.15 → **v15.16**.
- **CRITICAL — NSE_HOLIDAYS_2026 was wrong.** 2026-05-27 (today, Wed) was listed as a holiday — actual holiday is 2026-05-28 (Bakri Id, Thu). Bot AND AppScript both skipped today. Result: no Good Morning Telegram, no entry checks, no target-hit exit for CUMMINSIND (+12.01%) or HINDALCO (+6.08%) — both still showing as TRADED on the sheet instead of EXITED. Fixed both files using the NSE official 2026 holiday list (cross-checked against nseindia.com screenshot supplied by Amit ji). Multiple other 2026 dates corrected too (Ram Navami, Good Friday, Muharram, plus three missing entries — Maharashtra elec, Holi, Mahavir).
- **BUG-B** — Trailing SL was never written to AlertLog column O (only stored in BotMemory). Screenshot 2 showed `Trailing SL: —` for every TRADED row. Now writes the new TSL to col O after each set_tsl. Best-effort try/except.
- **BUG-C** — WAITING row with SL >= current price would exit instantly on promotion (MCX example: SL ₹3,194 set Tuesday, today MCX -4.5% to ₹3,012). Now skipped with `[SETUP INVALIDATED]` log; row left for AppScript to age out.
- **BUG-E** — Cash intraday trades were counted toward swing 3/day budget. Fixed.
- **AppScript v15.16 needs manual paste** into Google Apps Script editor before it goes live (auto-deploy not supported from GitHub).

**2026-05-26 (night):** Real FII/DII data layer added.
- `fetch_fii_dii.py` v1.0 — fetches NSE Cash market FII/DII daily, free official source. Writes BotMemory MKT_* keys, sends Telegram digest.
- `fetch_fii_dii.yml` — Mon-Fri 6:45 PM IST cron. Has on-failure alert.
- Confirmed via `inspect_nifty200.py` formula inspection: existing FII_* columns in Nifty200 are technical-only labels, not real institutional flow. Decision: keep them (renaming would break code), add real FII as MKT_* alongside.
- Memory updated: `project_fii_columns_reality.md` documents this for future sessions.
- Phase 2 roadmap: extend fetch_fii_dii.py to F&O FII data for options buying flow.

**2026-05-26 (late evening):** Workflow failure alerts + FII diagnostic.
- Added `if: failure()` Telegram alert step to 4 workflows (6 jobs) — `daily_reel.yml`, `daily-morning-reel.yml`, `daily-shorts.yml`, `kids-daily.yml` (3 jobs). Posts to **Basic channel only** with "System Notice" prefix; Advance/Premium stay pure trade signals. Uses stdlib `urllib` so it works even if pip install failed.
- Created `inspect_nifty200.py` — one-time diagnostic to reveal where Nifty200 FII columns (P/Q/R/AG) get their data. Read-only. Amit ji runs locally, pastes output back.

**2026-05-26 (evening):** Audit follow-up — BUG-3 through BUG-9 all fixed.
- `generate_longterm.py` v1.5 → **v1.6**: BUG-3 (RSI NaN guard), BUG-4 (BOOK PARTIAL ladder order).
- `trading_bot.py` v15.7 → **v15.8**: BUG-5 (exact-key flag lookup in auto_maintain + monthly P&L).
- `appscript_v14.gs` v15.14 → **v15.15**: BUG-6 (cash candidate BotMemory only on allocation), BUG-9 (_bmPurge gated to once per day).
- `.github/workflows/token_refresh.yml`: BUG-7 (corrected misleading "every 40 days" comment).
- `.github/workflows/daily-articles.yml`: BUG-8 (removed hardcoded per-article bullet list that could mismatch actual content).
- **All 9 numbered audit findings now resolved.**
- AppScript v15.15 needs another manual paste into Google Apps Script editor before it goes live (auto-deploy not supported from GitHub).

**2026-05-26 (afternoon):** Full-project audit + 2 critical fixes applied.
- Audited every Python module, AppScript, content_calendar, indian_holidays, fetch_holidays, refresh_cashwatchlist, key workflows.
- Found 1 CRITICAL + 2 HIGH + 6 MEDIUM + 7 LOW issues; logged in conversation.
- Fixed **BUG-1** in `trading_bot.py` v15.6 → **v15.7**: TSL exit was using recomputed (capped) `new_tsl` instead of stored `cur_tsl`, so gap-down below activated TSL never triggered exit. Now keeps local in sync and compares against `cur_tsl`. Critical for paper-trading data integrity and for live trading in Phase 4.
- Fixed **BUG-2** in `appscript_v14.gs` v15.13 → **v15.14**: removed hardcoded `NSE_EXPIRY_DATES_2026` (was last-Thursdays, would have failed Jan 2027). Added `_lastTuesdayOfMonth(year, month)` + dynamic `_getRecommendedExpiry()`. Now uses Last Tuesday per SEBI/NSE rule effective Sep 1 2025. Holiday-adjusted via `_RUNTIME_HOLIDAYS`. Works forever — no annual maintenance.
- Verified online via WebSearch: NSE monthly expiry IS Last Tuesday (NSE & ICICI Direct confirmed).
- Remaining audit items deferred: BUG-3 RSI NaN, BUG-4 BOOK PARTIAL ladder, BUG-5 substring flag checks, BUG-6 cash orphan, BUG-7 token_refresh comment, BUG-8 daily-articles FB message, BUG-9 _bmPurge every-tick.

**2026-05-25 (afternoon):** Full trading system audit + Batches 1 & 2 fixes applied.
- **Audit scope:** Everything trading-related (12 files: trading_bot.py, appscript_v14.gs, generate_longterm.py, refresh_cashwatchlist.py, fetch_holidays.py, token_refresh.py, indian_holidays.py + 5 GitHub Actions workflows).
- **Findings:** 3 Critical, 9 High, 11 Medium, 7 Low, 10 Suggestions.
- **Batch 1 applied (6 fixes — all zero-risk, high-priority):**
  - C1: token_refresh.py now alerts both Basic+Advance (was Advance-only)
  - C2: trading_bot.yml timeout 4→8 min
  - H1: 4 scripts get clear cred validation errors
  - H3: trading_bot.py daily dedup flags use exact-key lookup
  - H8: 2 workflows standardized to requirements.txt
  - H9: AppScript LeaderType match is now case-insensitive
- **Batch 2 applied (5 fixes — small risk, high value):**
  - C3: AppScript holidays auto-load from BotMemory (no more manual yearly update)
  - H2: trading_bot.py _exit_trade uses actual sheet qty for P/L (data integrity)
  - M1: step_a TRADED promotion batched K:M update (saves ~16s/morning)
  - M3: Removed 3 redundant trading_bot.yml backup crons
  - M4: Tightened cron window (saves ~3 wasted runs/day)
- **Batch 3 applied (5 fixes — medium risk, behavioral + perf):**
  - H4 (refresh_cashwatchlist): _current_price uses fast_info → info → history fallback chain
  - H4 (generate_longterm): price/52w from hist (not .info); .info wrapped for graceful fallback
  - H7: AppScript cash detection works in BEARISH market (was bullish-only)
  - M7: LTWatchlist batch_update — 1 API call instead of 25 (saves ~30s/Sunday)
  - M9: indian_holidays.py — removed duplicate (10,2) entry
- **Batch 4 applied (6 fixes — final polish):**
  - M2: refresh_cashwatchlist.py batch_update for all formula/status writes (saves ~2 min/monthly)
  - M5: token_refresh.yml comment corrected (was "every 40 days" — actual is 1st+15th)
  - M6: AppScript _bmPurge uses regex for date check (defensive)
  - M8: fetch_holidays.py FALLBACK_2027 cleaned (removed weekend dates)
  - M10: generate_longterm.py P&L cutoff widened 7→8 days (captures Friday-edge trades)
  - Removed obsolete v15.1 Y1 migration code from trading_bot.py (was running every tick)

**AUDIT COMPLETE.** 22 of 27 numbered findings addressed across 4 batches. Remaining 5 (M11, L2, L5, L6, L7) intentionally deferred as low-value or requiring coordinated changes.
- **Telegram routing verified working** by Amit ji — Basic/Advance/Premium all receive correct trade alerts.

**2026-05-26:** SEO Seeds block fix — `content_calendar.py` v2.2 → **v2.3**. `get_article_seo_seeds()` return shape was a dict; consumer in `generate_articles.py` expected a list of pillar dicts → silent TypeError every run → SEO keyword block was **empty in every article since v2.2**. Reshaped to return 5 pillar dicts (stock/bitcoin/personal/ai/global) with day-of-week seed rotation. Verified locally — all 4 pillars match correctly. Impact: stronger Google ranking → better AdSense revenue going forward.

**2026-05-25 (morning):** Created SmartSync memory system — 4 new files added (CLAUDE.md, CHANGELOG.md, SESSION.md, smartsync.bat).

---

## Pending Tasks — Priority Order

1. **Facebook Group posting** — Code ready in `upload_facebook.py` v2.6. Token needs `publish_to_groups` scope. Manual fix required (see Known Issues below).
2. **AdSense Publisher ID** — Replace `pub-XXXXXXXXXXXXXXXX` in `ads.txt` after AdSense approval.
3. **Phase 3** — Hindi→English dubbed audio track for global audience scale.

---

## Known Issues

| Issue | Status | Notes |
|---|---|---|
| Facebook Group posting | ❌ Blocked | Token missing `publish_to_groups` scope — manual fix in Graph API Explorer |
| AdSense Publisher ID | 📋 Pending | Replace pub-XXXXXXXXXXXXXXXX in ads.txt after approval |
| Dhan API (Phase 4) | 📋 Planned | Do NOT connect until explicitly approved |

---

## Starting Instruction for Any AI
*(Paste this at the start of any Claude.ai or AI chat session)*

```
You are helping me with my AI360Trading project.

OWNER: Amit Kumar, Haridwar. 6 family members depend on this system.
This is a fully automated trading signals + content income platform running on GitHub Actions.
Cost: ₹0/month. Paper trading only (Phase 1-3).

STRICT RULES you must follow:
1. NEVER provide partial code or snippets — always provide the complete file, every line.
2. NEVER assume file contents — I will paste the file for you to read before editing.
3. NEVER say something is fixed without showing the corrected content.
4. NEVER break working code — one broken workflow = zero income that day.
5. NEVER connect Dhan API or execute real trades — paper trading only.
6. Always use ai_client.py for AI calls (Groq→Gemini→Claude→OpenAI fallback).
7. Always use human_touch.py for content — never bypass it.
8. After every change: update .internal-ops.md + tell me the new version number.

CURRENT FILE VERSIONS:
- trading_bot.py → v15.8
- appscript_v14.gs → v15.15
- ai_client.py → v2.4
- human_touch.py → v2.2
- generate_longterm.py → v1.6
- generate_education.py → v1.1
- generate_reel.py → v2.1
- generate_reel_morning.py → v2.3
- generate_shorts.py → v3.3
- generate_kids_video.py → v2.3
- refresh_cashwatchlist.py → v1.3
- fetch_holidays.py → v1.2
- token_refresh.py → v2.2
- upload_youtube.py → v2.2
- upload_facebook.py → v2.6
- content_calendar.py → v2.3

PENDING:
1. Facebook Group posting (needs publish_to_groups token scope)
2. Instagram full auto (depends on FB Group fix)

KNOWN ISSUES:
- FB Group posting blocked — token scope missing
- Instagram posting not yet live

Now please help me with: [describe your task here]
```

---

*Update this file at the end of every session.*
*Last sync: SmartSync or manual git pull — check before starting any session.*
