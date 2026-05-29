# SESSION.md — AI360Trading

---

## Last Updated: 2026-05-30 (bulletproofing — SMC scanner v1.1 shipped; cron-reliability gap found, approach PENDING user pick)

---

## Current Version Map

| File | Version | Last Changed |
|---|---|---|
| `trading_bot.py` | **v15.13** | 2026-05-27 (Batch-4 hotfix: RelVol % conversion + RS column lookup + exact-match) |
| `option_intelligence.py` | **v1.0** | 2026-05-27 (Batch 3) |
| `institutional_edges.py` | **v1.0** | 2026-05-27 (Batch 4) |
| `fetch_earnings.py` | **v1.0** | 2026-05-27 (Batch 3, daily 18:30 IST) |
| `fetch_bhavcopy.py` | **v1.0** | 2026-05-27 (Batch 4, Mon-Fri 20:00 IST) |
| `fetch_smallmidcap.py` | **v1.1** | 2026-05-30 (REAL 5-day volume filter + always-observable tab + safer BotMemory write) |
| `appscript.gs` | **v15.16** | 2026-05-27 (live deployed — verified byte-identical to editor via clasp 2026-05-28) |
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

**2026-05-30 (appscript.gs line-by-line audit):** Read all 2035 lines + cross-checked vs live sheet/BotMemory. **NO logic bugs found.** Column contract PERFECT — all 35 hardcoded Nifty200 indices (r[0]..r[34]) map exactly to live header (Breakout_Stage=22, ATR=28, Master_Score=33, Sector_Rank=34, etc.). Race/lock fixes (_AS_LOCK, atomic setValues), BotMemory dedup+purge, last-Tuesday expiry, bearish hard-block all sound. `_RUNTIME_MEM` confirms bot tracks all 4 open trades (PNBHOUSING TSL 1051.20 etc.). **Findings (all minor/future):** (1) 🟡 H2-2026 holidays (Aug-Dec) are APPROXIMATIONS in the hardcoded NSE_HOLIDAYS_2026 array (lines 181-188 admit "to be verified"); NO HOLIDAYS_2026 override exists in BotMemory → system relies solely on approx dates → same class as the May-27 outage. Verify vs NSE official before August + fix both appscript.gs AND trading_bot.py. (2) 🔵 user-facing Telegram msgs still say "v15.15" while file is v15.16 (cosmetic). (3) 🔵 options hold-text says "option -40%" vs bot's newer "stock -1.5%"; cash RR format "1:" prefix inconsistent between the two cash sources. None affect income. Fixes offered, not yet applied (live file, needs clasp redeploy).

**2026-05-30 (bulletproofing — Opus 4.8):** Live audit first (gh CLI + Sheets MCP), then shipped `fetch_smallmidcap.py` **v1.1**. Found + diagnosed the real reliability gap; awaiting Amit ji's approach pick before touching the income-critical bot.
- **Verified live:** SmallMidCap tab still absent (scanner ran once on Bakri Id holiday → 0 picks → v1.0 never created the tab). Bot core HEALTHY — exited HINDALCO +5.73% & CUMMINSIND +10.13% as TARGET HITs on 05-29, archived to History. AlertLog "stuck" rows (PNBHOUSING etc.) are NOT a bug — `step_b` monitoring is market-hours-gated; PNBHOUSING fell below SL post-close → exits Monday 06-01. No new entries 05-27/29 = filters legitimately rejected all (strict by design).
- **Shipped v1.1 (zero income risk — SMC never produced a live signal):** (1) REAL volume filter — downloads prior 5 bhavcopy days, computes today÷5d-avg per symbol; <3 prior days → excluded (no fake number). Was a misleading "Vol 3.0×" proxy. (2) Always writes SmallMidCap tab + dated status row every scan (picks or "NO CANDIDATES"), idempotent. (3) Safer BotMemory write — only clears/rewrites when picks/stale keys exist (was wiping-risk every run). Verified: py_compile OK + synthetic-data smoke test (4× passes, 1.5× rejected, <3 days → 0).
- **🟢 BIG GAP fixed — cron reliability:** GitHub was throttling the `*/5` trading-bot cron to **3 runs/day** (vs ~96 expected; 3/day for 5 straight trading days). Often only ONE monitoring tick during the whole 6h15m market window → a stock could blow through SL/target uncaught for hours. **Shipped `trading_bot_session.yml`** — two reliable once-daily triggers (08:30 + 11:55 IST), each running an internal 5-min sleep-loop for dense guaranteed ticks. ADDITIVE: trading_bot.py untouched, `*/5` kept as backup, SAME concurrency group `trading-bot` + cancel-in-progress:false ⇒ never double-runs. Repo PUBLIC ⇒ free minutes. Verified live (manual dispatch ran 1 tick → bot booted → [SKIP] outside hours → clean exit). First real sessions Mon 2026-06-01 08:30 + 11:55 IST. **Watch that morning to confirm dense ticks + Monday's first run exits PNBHOUSING (below SL since Fri close).**

**2026-05-29 (Fri — HANDOFF for next session / any AI):** Top-gainer coverage analysis. Model switched to **Opus 4.8** (new saved default). NO code changed this session — analysis + handoff only.
- **Trigger:** Amit ji shared 2 NSE top-gainer screenshots (2026-05-29 intraday) and asked why none were traded/alerted, + asked for system improvement.
- **VERIFIED via live sheet + code reads:**
  - **`SmallMidCap` tab does NOT exist yet** (confirmed via list_sheets — 8 tabs, no SmallMidCap). So `fetch_smallmidcap.py` has **never run**. First-ever run is **tonight Fri 2026-05-29 20:30 IST**. As of the intraday screenshots, ZERO small/mid-cap alerts could exist by timing alone.
  - **Screenshot-1 names (+12% to +20%: SUPRIYA, TBZ, COFFEEDAY, BEARDSELL, WOCKPHARMA, SHIVALIK, KERNEX, NETWEB, INDSWFTLAB, ASHAPURMIN, BLUSPRING, BIMETAL, INDNIPPON, SHAILY, OMNI, NPST, RELAXO) are ALL outside Nifty200** (checked all 200 symbols). Main `trading_bot.py` only scans Nifty200 → never looks at them.
  - **`fetch_smallmidcap.py:61` `PCT_MAX = 13.0`** → rejects 12 of the 17 screenshot-1 names (every >13% mover + upper circuits). By design: "no lottery / no upper-circuit." Only INDNIPPON/SHAILY/OMNI/NPST/RELAXO survive the band, then face turnover+delivery+top-3 cuts.
  - **BUG (real) — fake volume filter.** `fetch_smallmidcap.py:220-222`: `vol_mult_proxy = turnover_cr / TURNOVER_MIN_CR` (=turnover/20), required ≥ 3.0 → this is just "turnover ≥ ₹60 Cr", NOT a volume-vs-average measure. But the sheet column "Vol Mult (proxy)" and the Telegram digest both display "Vol 3.0×" to subscribers → misleading. Code comment already admits NSE CSV has no avg-volume field.
  - **Screenshot-2 names (large caps +1.7% to +6%: MOTHERSON, IREDA, HYUNDAI, GMRAIRPORT, SAMMAANCAP, LODHA, LTM, BOSCHLTD, NBCC, POWERINDIA, COFORGE, YESBANK, BANDHANBNK, PERSISTENT, INDUSTOWER) ARE in Nifty200** (only RADICO is not). They're scanned every 5 min but weren't traded because the bot trades SETUPS (breakout/retest stage flagged by AppScript → entry filters: RS, rel-vol, delivery, FII regime, VIX ≤ 22 → max 3 swing/day), not "green stocks". A +1.7-2.8% drift is below setup conviction.
- **YELLOW FLAG (NOT yet verified):** AlertLog's last real entries are 2026-05-25/26 (PNBHOUSING, EICHERMOT, SAIL, INDUSINDBK). NOTHING for Wed 2026-05-27 (a trading day) or Fri 2026-05-29. Could be normal strictness (0 setups) OR AppScript scanner not writing WAITING candidates. Needs AppScript + BotMemory read to confirm.
- **IMPROVEMENT BACKLOG (Amit ji to pick priority — not yet chosen):**
  1. Fix fake volume filter → real 5-day volume-multiple (have `fetch_bhavcopy.py` store avg-vol per symbol; the comment already anticipates this). Low risk, high trust value.
  2. Add intraday early-momentum scan → catch big movers at +3-5% BEFORE upper circuit (only way to actually ride SUPRIYA/WOCKPHARMA-class). Bigger build; mind ₹0/month.
  3. Verify AlertLog gap (diagnosis, no code change).
  4. Re-tune SMC thresholds (+13% cap / turnover / delivery) so scanner surfaces some movers tonight — strategy change, needs risk-appetite call.
- **Amit ji instructions captured:** (a) improve the system; (b) sync must NEVER let old files overwrite improved ones — keep local PC AND GitHub in lockstep; commit+push after every edit; apply improvements ONLINE too now that full access (sheets/clasp/gh) exists.
- **Access confirmed persistent** across model change + Claude Code restart (MCP sheets, clasp, gh CLI, file tools all live outside the chat). Only the conversation resets — hence this handoff.
- **Local-only (NOT pushed):** `xxxxxxxxx.png`, `zzzzzzzz.png` (the gainer screenshots) — kept local at Amit ji's request.

**2026-05-28 (overnight):** SEO + content quality overhaul — 3 phases shipped after live audit of articles, robots, sitemap, generators.
- **AUDIT FINDINGS (8 root causes for tiny growth, 100 YT subs / 50 daily blog visitors):**
  - Same-day duplicate content (4 articles all citing same NIFTY/SP500/BTC numbers) → Google content-farm signal
  - Templated title pattern "INDEX X% as INDEX Y% amid INDEX Z%" → detectable spam structure
  - Boilerplate AI prose (no opinions, no anecdotes, "as we discussed" overused) → Helpful Content Update penalty
  - 318 URLs in 37 days = wrong volume for site age → AI farm signature
  - No internal hub pages
  - ZERO images / videos in articles → no dwell time signal
  - Pagination /page2-15 in sitemap (but blocked in robots.txt) → conflicting signal
  - No on-site search bar → lost dwell signal
- **PHASE 1 SHIPPED (commit b51273d):** NEW `media_helper.py` — Pexels API → Pixabay → Unsplash Source → Picsum cascade for hero + inline images. YouTube RSS feed for own-channel embeds (channel ID `UC9dAJakbfPXk8zL31AVuTfA`). Wired into `generate_articles.py` so every article now gets hero image at top, inline image mid-body, YouTube embed before final FAQ. All fail-open.
- **PHASE 2 SHIPPED (commit cb2f1af):** Daily volume CUT 4 → 2 articles via pillar rotation by day-of-year (even days = stock + personal-finance, odd days = bitcoin + ai-trading). Strict evergreen mode for holiday/weekend (filter trends with numeric regex, neutralize fear_greed, body prompt explicitly forbids current price levels). Title prompt rewritten with hard rules against templated patterns + GOOD/BAD examples.
- **PHASE 3 SHIPPED (commit bb15640):** Body humanization rules expanded 8 → 13 (first-person voice, controversial takes, personal anecdotes, contractions, rhetorical questions, historical parallels with exact dates). Banned word list expanded. Cap on "as we discussed in our previous article" to once per article max. Custom `sitemap.xml` at repo root overrides jekyll-sitemap plugin to exclude pagination + add per-URL changefreq/priority.
- **Phase 4 (Dhan auto-trade) DEFERRED** — Amit ji wants to focus on SEO/content now; will trade manually from Telegram alerts. 10-day plan archived in `project_phase4_plan.md`.
- **Optional next:** add `PEXELS_API_KEY` to GitHub Secrets for higher-quality images (free signup, 200 req/hr). Currently using Unsplash Source fallback (works fine, slightly less topical).
- **Will see effect:** Tomorrow's article run (Fri 2026-05-29 10:00 IST) is the first under new rules. Compare titles + images + word count before/after.

**2026-05-28 (later night):** clasp activated for AppScript + 10-day Phase 4 Dhan auto-trade plan kicked off.
- **clasp installed** (v3.3.0) + **clasp login** authorized as `ai360trading@gmail.com`. Live Apps Script project `1oFYYo6MrK4ab4MSqytcCI9U6en0JzuNsZAZ5vokzSiLJrFwMMll-WCPF` cloned into `apps_script/` workspace.
- **v15.16 deployment verified live** — byte-by-byte comparison shows live editor's `Code.js` (104,243 bytes, LF) is 100% identical content to repo's `appscript.gs` (106,277 bytes, CRLF). Difference is line endings only. The "v15.16 needs manual paste" item from 2026-05-27 batches is **already done** — Amit ji pasted it without telling me. No manual paste backlog remains.
- **New deploy script:** `deploy_appscript.ps1` at repo root. One command (`.\deploy_appscript.ps1`) syncs `appscript.gs` → workspace → `clasp push -f` → live. Future AppScript edits never need manual paste again.
- **`.gitignore` extended** to exclude clasp working-state files (`apps_script/Code.js`, `apps_script/.clasp.json`, `.clasprc.json`).
- **10-day plan started** — Day 1 (today) IN PROGRESS. Tasks 1-10 created and tracked in session task list.
- **User confirmed:** Phase 4 starts with Dhan as broker. ₹0 real money for first 5-10 days (token-only setup + paper testing). Semi-auto Telegram approval for first 10 live trades.
- **Pending from user:** Dhan API activation (via dhanhq.co web portal). Tokens then added to GitHub Secrets as `DHAN_CLIENT_ID` + `DHAN_ACCESS_TOKEN`.

**2026-05-28 (night):** Tooling activation verified — both pending manual steps from earlier session completed.
- **`gh` CLI** — `gh auth login` completed via device-flow code 034B-8CC2; logged in as `systronics` with `gist`/`read:org`/`repo` scopes. Persistent across sessions. `gh auth status` confirms ✓ live.
- **`mcp-google-sheets`** — `service_account.json` now exists at `C:\Users\Admin\ai360trading\service_account.json` (2,390 bytes, gitignored). MCP server connected: `mcp__google-sheets__list_sheets` on spreadsheet `1fPNGL6AHs-7M-oC22zILg9FlyWi-7DF9NoVVqZQs2vk` returned 8 tabs (AlertLog, Nifty200, History, BotMemory, LTWatchlist, LongTermSignals, CashWatchlist, PositionalLatest). `SmallMidCap` will appear after first Batch 5 scan on Fri 2026-05-29 20:30 IST.
- **Future sessions** can now: read live GOOGLEFINANCE values (CMP/Change%/Volume), inspect AppScript-computed columns (Volume_vs_Avg_%, RS, ATR), pull failed GH Action logs without copy-paste, write back to sheet via MCP if needed.
- Memory + MEMORY.md updated to reflect "fully active" state. No repo code changed this session.

**2026-05-28 (evening):** Tooling setup — no repo files changed; all installs live outside the repo.
- **GitHub CLI installed** — portable build v2.93.0 at `C:\Users\Admin\gh\bin\gh.exe` (no admin needed, added to user PATH). `gh auth login` completed via browser device-flow; logged in as `systronics` with `repo`/`gist`/`read:org` scopes. Token in Windows keyring — persists across sessions. Future Claude Code sessions can now pull workflow runs/logs without user copy-paste.
- **mcp-google-sheets installed** — pip package v0.6.3, binary at `C:\Users\Admin\AppData\Roaming\Python\Python314\Scripts\mcp-google-sheets.exe`. MCP server registered in `C:\Users\Admin\.claude.json` under project `C:/Users/Admin/ai360trading` with `SERVICE_ACCOUNT_PATH=C:\Users\Admin\ai360trading\service_account.json`. **Status: ✗ disconnected** — `service_account.json` not yet downloaded from Google Cloud Console. Amit ji will download tonight/tomorrow ("Option C"). Once file exists + Claude Code restart, live read/write of `Ai360tradingAlgo` (including GOOGLEFINANCE values + formulas) becomes available.
- **Workflow health audit run** — Last 50 runs: ZERO failures since 2026-05-19. Trading Bot, content workflows, FII/DII, KeepAlive all green. System healthy heading into first full-Batch-1-5 trading day (Fri 2026-05-29).
- **Memory updated** — new entry `project_tooling_2026-05-28.md` + MEMORY.md index updated. Both `.gitignore` already protects `service_account.json` (line 69) and `credentials.json` + `token.json` — JSON download will be safe by default.

**2026-05-27 (late night):** Batch-4 hotfix + Batch 5 — `trading_bot.py` v15.12 → **v15.13** + new `fetch_smallmidcap.py` v1.0 + workflow.
- **Batch-4 silent bug found via Amit ji's screenshot 8** — Nifty200 has columns `Volume_vs_Avg_%` (percentage form) and `RS` (literal). v15.12 keyword lookup missed both → volume filter was failing-open. v15.13 fix: exact-match lookup + percentage→multiple conversion + dedicated RS-column reader. RS gate now prefers sheet value, falls back to math.
- **Batch 5 Small/Mid Cap Scanner** — Mon-Fri 20:30 IST. Highly selective (0-3 picks/day) per Amit ji's "few signals, long ride, max momentum profit, no loss tolerance" rule. Excludes Nifty200 universe. Filters: 4-12% move (no upper-circuit), ≥₹20Cr turnover, ≥50% delivery, ≥3× volume. Outputs new `SmallMidCap` sheet tab (auto-created), BotMemory `SMC_*` keys, Telegram digest to Advance + Premium. No auto-trade yet — Batch 6.
- **Manual tasks pending:** None as of 2026-05-28. AppScript v15.16 paste verified done (clasp confirms repo and live editor identical).

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
