# CHANGELOG — AI360Trading

---

## 2026-05-26 (late evening) — WORKFLOW FAILURE ALERTS + FII DIAGNOSTIC SCRIPT

### Added
- **Workflow failure alerts** — 4 daily workflows (6 jobs) now post a "System Notice" to the **Basic Telegram channel only** (NOT Advance/Premium — those stay pure trade signals) when the job fails. Uses stdlib `urllib` so it works even if pip install failed earlier in the run. `continue-on-error: true` ensures the alert step itself never crashes the workflow further. Message clearly marks "system message, not a trade signal" so followers don't confuse it with trading.
  - `daily_reel.yml` — failure step after Facebook upload
  - `daily-morning-reel.yml` — failure step after FB upload
  - `daily-shorts.yml` — failure step after debug-artifact step
  - `kids-daily.yml` — failure step in each of 3 jobs (Hindi Full / Cliffhanger / Did You Know)
- `inspect_nifty200.py` — read-only diagnostic script. Connects to `Ai360tradingAlgo` → `Nifty200` tab and prints the raw FORMULA (not just the displayed value) of cells P/Q/R/AG for rows 2-4 (FII_Buy_Zone, FII_Rating, Leader_Type, FII_Signal). Output reveals whether these columns are powered by GOOGLEFINANCE / IMPORT / manual values / external feed — currently unknown from codebase alone. Run once locally: `python inspect_nifty200.py`, paste output to confirm data source.

---

## 2026-05-26 (evening) — AUDIT FOLLOW-UP: BUG-3 → BUG-9 ALL FIXED

### Fixed
- `generate_longterm.py` v1.5 → **v1.6** —
  - **BUG-3 (HIGH):** `_rsi()` returned NaN on flat 14-day windows (0/0). Now divides by `loss.replace(0, 1e-10)` and clamps NaN → 50.0.
  - **BUG-4 (MEDIUM):** `make_signal()` ladder evaluated `score >= 3` (HOLD) before BOOK PARTIAL, so stocks near 52W high with moderate score were tagged HOLD. BOOK PARTIAL check moved between ACCUMULATE and HOLD — now fires whenever `pos_pct >= 85` or `rsi >= 72`.

- `trading_bot.py` v15.7 → **v15.8** —
  - **BUG-5 (MEDIUM):** `auto_maintain_sheets` (line 1414) and monthly P&L gate (line 1461) were using substring `flag_key in mem` checks — Batch 1 had fixed the same pattern in GM/MD/PM but missed these two. Switched to `_mem_get(mem, key)` exact-key lookup.

- `appscript_v14.gs` v15.14 → **v15.15** —
  - **BUG-6 (MEDIUM):** Cash candidates wrote BotMemory `_CAP/_MODE/_SEC` at detection time. Slots later lost (window expired or `LOG_ROWS` cap) left orphan entries. Both early `_bmSet` sites removed; writes consolidated into the final "add to finalWaiting" allocator — BotMemory only records candidates that actually got a WAITING slot.
  - **BUG-9 (LOW):** `_bmPurge` ran on every 5-min fire (~120/day). Gated to once per day via `${today}_BMPURGED` FLAG. Bm reloaded after purge so row indexes stay fresh.

- `.github/workflows/token_refresh.yml` —
  - **BUG-7 (LOW):** Inner comment block still said "Runs every 40 days" — contradicted actual cron schedule (1st + 15th). Corrected.

- `.github/workflows/daily-articles.yml` —
  - **BUG-8 (MEDIUM):** Facebook share message hardcoded 4-bullet pillar/topic list that could mismatch actual articles. Replaced with generic pillar-set summary that points to the homepage for the live list — message is now truthful in any content mode.

### Audit closed
All 9 numbered audit findings (BUG-1 through BUG-9) from the 2026-05-26 full-project audit are now resolved. Versions: trading_bot v15.6→v15.8, appscript v15.13→v15.15, generate_longterm v1.5→v1.6, token_refresh.yml/daily-articles.yml comment-level updates.

---

## 2026-05-26 — CRITICAL TSL EXIT BUG FIX + F&O EXPIRY DAY (LAST TUESDAY)

### Fixed — BUG-1 (CRITICAL)
- `trading_bot.py` v15.6 → **v15.7** — `step_b_monitor_trades` was comparing CMP against the recomputed `new_tsl` (which `calc_new_tsl` caps at `cp * 0.99`) instead of the actually-stored `cur_tsl`. On a gap-down BELOW the activated TSL, `cp <= cp*0.99` is always False → TSL exit silently never fires. After breakeven pushed cur_tsl above entry, the hard-loss path also won't catch it (it requires `cur_tsl < ent`). FIX: keep local `cur_tsl` in sync after `set_tsl(...)` and compare CMP against `cur_tsl`. Any gap below the live TSL now exits.

### Fixed — BUG-2 (HIGH — would have broken Jan 2027 + already on wrong day)
- `appscript_v14.gs` v15.13 → **v15.14** — Two issues in one fix:
  1. **Wrong expiry day** — SEBI/NSE moved monthly F&O expiry from **Last Thursday → Last Tuesday** effective Sep 1, 2025 (NIFTY, BANKNIFTY, FINNIFTY, single stocks). Old code still used last-Thursdays.
  2. **Hardcoded year list** — `NSE_EXPIRY_DATES_2026` was a 12-entry array; from Jan 1 2027 onwards `_getRecommendedExpiry` would have fallen through to Dec 31 2026 with a literal `daysLeft: 30`, breaking every options signal in 2027.
  - **FIX:** removed `NSE_EXPIRY_DATES_2026`. Added `_lastTuesdayOfMonth(year, monthIdx)` helper. `_getRecommendedExpiry` now walks forward month-by-month from today, generating last-Tuesday expiries on the fly — works forever, no annual maintenance. Applies holiday adjustment via `_RUNTIME_HOLIDAYS` (if last Tuesday is an NSE holiday, expiry moves to the preceding trading day, per NSE rule).
  - All user-facing version labels (Telegram messages, daily/weekly summary, test functions) bumped to v15.14.

### Audit reference
- Findings BUG-1 and BUG-2 from the 2026-05-26 full-project audit. Remaining audit items (BUG-3 RSI NaN, BUG-4 BOOK PARTIAL ladder order, BUG-5 substring flag matches, BUG-6 cash candidate BotMemory orphan, BUG-7 token_refresh.yml inner comment, BUG-8 daily-articles.yml hardcoded FB message, BUG-9 _bmPurge every-tick) intentionally deferred — lower severity.

---

## 2026-05-26 — SEO SEEDS BLOCK FIX

### Fixed
- `content_calendar.py` → **v2.3** — `get_article_seo_seeds()` return shape was a dict (`global_seeds`, `india_seeds`, `usa_seeds`, `uk_seeds`, `no_price_numbers`, `title_style`), but `generate_articles.py:1141-1155` consumed it as a list of pillar dicts (reading `s["primary_target"]`, `s["seo_seed"]`, `s["long_tail"]`, `s["affiliate_hint"]`). The mismatch silently raised `TypeError` inside the `try/except` → printed `[SEO-SEED] Skipped (...)` → left the SEO keyword strategy block **empty in every single generated article since v2.2**. Reshaped to return a list of 5 pillar dicts (stock / bitcoin / personal / ai / global fallback) with day-of-week seed rotation so Mon-Fri articles get fresh keyword angles. Weekend/holiday returns evergreen seeds with no live-price refs. Verified locally — all 4 pillars now match their seed correctly and `seo_seed_block` is populated in the LLM prompt → stronger Google ranking → better AdSense revenue from ai360trading.in.

### Impact
- 4 articles per day × past N days had **zero SEO keyword targeting** in the prompt — content was still generated, but without the structured keyword guidance Google rewards.
- Going forward: every article gets a pillar-specific primary keyword, 2 long-tail keywords as H2/FAQ suggestions, and an affiliate hint tied to the pillar.

---

## 2026-05-25 15:30 — BATCH 4 AUDIT FIXES (FINAL POLISH)

### Fixed
- `refresh_cashwatchlist.py` → **v1.3** — M2: All formula writes (G/H/I) and status writes (F/J) now use `batch_update` instead of 5 `update_cell` calls per stock. 35 stocks × 5 calls = 175 API calls → 2 batch calls. Also reduced per-stock sleep from 2.0s → 1.0s (fast_info is lighter than .info). Saves ~2 min per monthly run.
- `token_refresh.yml` — M5: Comment header corrected. Was "every 40 days" but actual schedule is 1st + 15th of month (~15 day cycle). Updated comment to reflect reality (and note that v2.2 fix made the script actually read CHAT_ID_BASIC env var).
- `appscript_v14.gs` → **v15.13** — M6: `_bmPurge` FLAG key date check now uses regex `/^\d{4}-\d{2}-\d{2}_/` instead of substring(0,10). Defensive — prevents future bugs if a non-date FLAG key is ever added.
- `fetch_holidays.py` → **v1.2** — M8: Removed `2027-08-15` (Sunday — NSE doesn't observe) and `2027-10-02` (Saturday) from FALLBACK_2027. Added clear note that fallback dates are approximate and NSE API is the primary path.
- `generate_longterm.py` → **v1.5** — M10: Weekly P&L cutoff widened from 7 → 8 days to capture Friday-edge trades on Sunday morning run.
- `trading_bot.py` → **v15.6** — Removed obsolete v15.1 Y1 cell migration code that was running on every tick (~288 ticks/day) for no benefit. Migration was completed long ago.

### Audit complete
All 16 numbered findings (C1-C3, H1-H9, M1-M10 except M11) have been addressed across Batches 1-4. M11 (lock check timing) intentionally deferred — current implementation works in practice; fix would require coordinated AppScript change with marginal benefit. L1-L7 cosmetic items partially addressed (L1, L3, L4 closed in Batches 1-2); L2, L5, L6, L7 deferred as low-value cosmetic.

---

## 2026-05-25 15:00 — BATCH 3 AUDIT FIXES

### Fixed
- `appscript_v14.gs` → **v15.12** — H7: Cash intraday detection no longer requires `marketBullish`. Cash trades are catalyst-driven (PSU results, defence orders, sector news) and can move 10-15% even in bearish Nifty. Risk is contained by tight 3% SL + 3PM force-exit; the 4% pctChange threshold already requires strong conviction. Now captures bearish-market income days previously blocked. Safe in paper trading Phase 1-3.
- `generate_longterm.py` → **v1.4** — (a) H4: Decoupled price/52w from yfinance `.info`. CMP/52W/RSI now come from `hist` (always reliable); `.info` is best-effort for fundamentals only (wrapped in try/except). yfinance `.info` is heavily throttled and returns null for many Indian-stock fields; this way FundScore may degrade silently but signals always have correct prices. (b) M7: LTWatchlist update uses `batch_update` (1 API call) instead of 25 sequential `update_cell` + 25 cell reads. Notes pre-fetched in `_load_watchlist`. Saves ~30s per Sunday run.
- `refresh_cashwatchlist.py` → **v1.2** — H4: `_current_price` now tries `fast_info.last_price` first (less throttled, more reliable), falls back to `.info`, then `history.Close.iloc[-1]` as last resort.
- `indian_holidays.py` — M9: Removed duplicate `(10, 2)` entry in FALLBACK_HOLIDAYS. Comment cleaned up (was "Mahatma Gandhi Jayanti / Dussehra" — Dussehra is a different date).

---

## 2026-05-25 14:30 — BATCH 2 AUDIT FIXES

### Fixed
- `appscript_v14.gs` → **v15.11** — Holidays auto-extend from BotMemory. Added `_RUNTIME_HOLIDAYS` set + `_getRuntimeHolidays(ss)` loader that reads `HOLIDAYS_YYYY` keys (written by `fetch_holidays.py` every Dec 1) and merges them with hardcoded NSE_HOLIDAYS_2026. `_isMarketHoliday()` now uses the runtime set. `_runUnifiedManager` calls the loader once per run before the holiday check. Means AppScript will automatically respect 2027 holidays without code changes — was a manual-update requirement before. Closes audit finding C3.
- `trading_bot.py` → **v15.5** — (a) `_exit_trade` now accepts `qty` parameter and uses actual sheet quantity for `pnl_rs` calculation. Previously recalculated as `cap // ent` which differs from sheet qty when cmp != ent at entry time. Affects History P/L accuracy. All 4 call sites in `step_b` and `step_c` updated to pass `qty`. Closes H2. (b) `step_a` TRADED promotion batched into single K:M update (1 API call instead of 3). Saves ~2 sec per entry × up to 8 entries = ~16 sec on morning rush. Closes M1.
- `trading_bot.yml` — Removed 3 redundant backup crons (concurrency already queues overlaps). Tightened start hour 02:45 → 03:00 UTC (saves wasted pre-open runs 08:15-08:25 IST). Closes M3 + M4.

---

## 2026-05-25 14:00 — BATCH 1 AUDIT FIXES

### Fixed
- `token_refresh.py` → **v2.2** — Token refresh alerts now sent to BOTH Basic and Advance channels (was Advance-only despite v2.1 changelog claiming a Basic fix). Reads `CHAT_ID_BASIC` + `CHAT_ID_ADVANCE`, iterates both. Closes audit finding C1.
- `trading_bot.py` → **v15.4** — (a) `get_sheets()` now validates GCP creds with a clear `[CREDS]` SystemExit instead of a cryptic `FileNotFoundError` when both env var and local file are missing. (b) Replaced 3 unsafe substring matches in daily-dedupe flags (GM `_AM`, MD `_MD`, PM `_PM`) with exact-key `_mem_get()` lookup. Closes findings H1, H3.
- `appscript_v14.gs` → **v15.10** — `_checkBearishEntryAllowed`: LeaderType check now case-insensitive substring match (`"sector leader"` or `"sector_leader"`). Previously strict equality could silently block all bearish entries on minor sheet text variation. Closes finding H9.
- `refresh_cashwatchlist.py` → **v1.1** — Explicit cred validation in `_connect()`. Closes H1.
- `fetch_holidays.py` → **v1.1** — Explicit cred validation in `_connect()`. Closes H1.
- `generate_longterm.py` → **v1.3** — Explicit cred validation in `_connect()`. Closes H1.
- `trading_bot.yml` — (a) `timeout-minutes` raised 4 → 8 to prevent partial-write failures on slow runs (still well under the 5-min cron interval; `cancel-in-progress:false` queues overlaps). Closes C2. (b) Switched to `pip install -r requirements.txt` instead of inline list to prevent dependency drift. Closes H8.
- `fetch_holidays.yml` — Switched to `pip install -r requirements.txt`. Closes H8.

### Removed
- `trading_bot.yml` — `permissions: contents: write` (unused — bot does not push to repo).

---

## 2026-05-25 13:05
### Changed
- `instructions.txt` — Added upload_instagram.py v1.0 to current file versions list

---

## 2026-05-25 13:00
### Added
- `upload_instagram.py` → v1.0 — Recreated. Standalone Instagram Reels uploader. Supports --type reel/morning/short2/short3. Uses same 4-step resumable upload protocol as upload_facebook.py v2.6 and generate_shorts.py v3.3. Gets page token same way. Builds mode-aware captions (market/weekend/holiday). Saves ig_post_id to meta JSON on success. Saves caption to instagram_fallback_YYYYMMDD.txt on failure for manual posting.

---

## 2026-05-25 12:40
### Fixed
- `token_refresh.yml` — Added CHAT_ID_BASIC to env vars. Token refresh success/failure alerts now also reach the Basic channel which Amit ji monitors.

---

## 2026-05-25 12:35
### Fixed
- `longterm_signals.yml` — Replaced manual pip install with `pip install -r requirements.txt` to prevent silent failures if generate_longterm.py uses any package not in the manual list.
- `refresh_watchlists.yml` — Same fix applied to both jobs (refresh-cashwatchlist + refresh-longterm-watchlist).

---

## 2026-05-25 12:30
### Fixed
- `.gitignore` — Removed stale entries: `!generate_analysis.py` (file doesn't exist), `!generate_community_post.py` (file doesn't exist), `!SYSTEM.md` (renamed to .internal-ops.md). Added missing files that exist: `!generate_longterm.py`, `!refresh_cashwatchlist.py`, `!fetch_holidays.py`. Updated `!SYSTEM.md` → `!.internal-ops.md`.

---

## 2026-05-25 12:25
### Fixed
- `daily_reel.yml` — FACEBOOK_GROUP_ID was missing from upload_facebook.py step. Evening ZENO reel will now post to Group once token scope is fixed.

---

## 2026-05-25 12:20
### Fixed
- `daily-morning-reel.yml` — Two bugs fixed: (1) Content mode detection broken — same `python indian_holidays.py` issue as daily-videos, replaced with inline Python snippet; (2) FACEBOOK_GROUP_ID missing from Post to Facebook step — group will now receive morning reel when token is fixed.

---

## 2026-05-25 12:15
### Fixed
- `daily-videos.yml` — Content mode detection was broken: `python indian_holidays.py` only printed to stdout, never wrote CONTENT_MODE to GITHUB_ENV. Replaced with proper inline Python snippet that writes to GITHUB_ENV (same pattern as all other working workflows).

---

## 2026-05-25 12:00
### Fixed
- `appscript_v14.gs` — Header comment corrected: v15.8 → v15.9 (code was already v15.9, only comment was stale)

---

## 2026-05-25 11:45
### Changed
- `instructions.txt` — File versions updated to exact values read from actual files: trading_bot.py v15.1→v15.3, appscript v15.6→v15.8, added ai_client/human_touch/longterm/refresh/fetch/token/content_calendar/indian_holidays, generate_kids_video latest→v2.3, upload_youtube latest→v2.2, upload_kids_youtube latest→v2.3

---

## 2026-05-25 11:30
### Changed
- `instructions.txt` — Replaced with universal AI instructions: environment detection (PC vs Online), URL fallbacks for online AI, rules, pending tasks, file versions

---

## 2026-05-25 11:00
### Added
- `CLAUDE.md` — Claude Code session guide: owner info, file versions, strict rules, session protocol
- `CHANGELOG.md` — This file: version history for all project files
- `SESSION.md` — Persistent session state: version map, pending tasks, known issues, AI start prompt
- `smartsync.bat` — Windows batch file: syncs PC ↔ GitHub bidirectionally before every session

### Current File Versions (baseline snapshot — read from actual files)
- `trading_bot.py` → v15.3
- `appscript_v14.gs` → v15.8 in file header / v15.9 per .internal-ops.md
- `ai_client.py` → v2.4
- `human_touch.py` → v2.2
- `generate_longterm.py` → v1.2
- `generate_education.py` → v1.1
- `generate_reel.py` → v2.1
- `generate_reel_morning.py` → v2.3
- `generate_shorts.py` → v3.3
- `generate_articles.py` → current (no version tag)
- `generate_kids_video.py` → v2.3
- `refresh_cashwatchlist.py` → v1.0
- `fetch_holidays.py` → v1.0
- `token_refresh.py` → v2.1
- `upload_youtube.py` → v2.2
- `upload_facebook.py` → v2.6
- `content_calendar.py` → v2.2
- `indian_holidays.py` → current (no version tag)
- `.internal-ops.md` → 2026-05-23 (last updated)

---

<!-- Add new entries above this line. Most recent entry always at top. -->
<!-- Format:
## YYYY-MM-DD HH:MM
### Changed
- filename.py → vX.X — what changed
### Added
- new file — what it does
### Fixed
- what bug was fixed
-->
