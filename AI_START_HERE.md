# AI_START_HERE - read this FIRST (about 5 minutes), then work ONLY on the problem the owner names

*Written 2026-11-15 for the day the owner's Claude plan is over (18 Nov 2026). Any AI (Claude, ChatGPT, Gemini ...) can use this file. It exists because the full docs are huge and a free AI used its whole daily limit just reading them.*

## 0. How the owner uses this (3 steps, no technical knowledge needed)
1. Double-click `collect_problem.bat` (or run `python collect_problem.py`). It creates `problem_report.txt` = the recent failed GitHub runs + the last log lines + the on/off switches.
2. Paste into the AI: **this file + problem_report.txt + one sentence** of what was seen (example: "Good Morning message did not come today").
3. The AI works ONLY on that problem, using section 3 to find the 1-3 files involved. It must NOT read or "understand" the whole project first.

## 1. What this is (6 lines)
- **AI360Trading**, owner Amit Kumar, Haridwar. 6 family members live on it. Owner is non-technical. Everything is FREE (Rs 0/month) and runs by itself on GitHub Actions (repo `systronics/ai360trading`, public), a Google Sheet `Ai360tradingAlgo`, Google Apps Script (`appscript.gs`) and the external cron-job.org (starts the bot at 08:40 IST).
- Products: Telegram trade alerts (Basic/Advance/Premium channels), website ai360trading.in, YouTube/Facebook/Instagram/Threads/Pinterest content. The bot is **PAPER trading only**; the owner trades by hand with real money from the alerts, so alert quality = family income.
- Nothing at run-time uses Claude. AI text chain = Groq -> Gemini -> Cloudflare -> templates (free). So the system keeps running without any AI; an AI is only needed to CHANGE or REPAIR code.

## 2. HARD RULES (breaking one can cost real money)
1. Paper trading only. Never connect a broker, never put a trading/API secret in GitHub, never place real orders. (Only exception: read-only `UPSTOX_ANALYTICS_TOKEN`.)
2. Rs 0/month: never add a paid service.
3. Buy-side only: no shorting, no put buying.
4. Do NOT change a trading gate/threshold because of a few trades. Locked: RS>=5, RSI exception (65-75 only if up on the day, >75 blocked), volume gate 1.5x pace, option loss cap 20%, options = current expiry intraday/1-2 day, cash force exit 15:10, `ROOM_VETO_ENFORCE=False`, `CASH_REGIME_GATE`, `INTRADAY_PAUSE` (cash/option only). Full reasons: `CLAUDE.md` -> section "NEVER CHANGE" (search it, do not load the whole file: it is 175 KB).
5. Observation trackers (SignalWatch, ResultLean, GainersLog, GateAudit, BuildupWatch, ShadowLedger, SwingShadow, RunupWatch, TrendWatch, WatchPlan, OptionSnap, OptionDiary, OptionWatch, OptionCapWatch) are read by NO gate. Never wire them into trading without the owner's approval after 4+ weeks of data (review date: on/after 11 Dec 2026).
6. Fail-open for data feeds (a dead feed must never kill the bot). Never delete sheet rows/tabs without the owner's yes.
7. NSE holidays only from the official NSE list (`fetch_holidays.py`), never from memory.
8. `.bat/.cmd/.ps1` files must keep CRLF line endings.
9. No emoji inside Pillow `draw.text()` in the video generators (renders as boxes).
10. Honest wording: paper results are "paper", say win/loss, no guaranteed-profit language, AI use is disclosed, never advice/tips language.
11. The owner has to be told in plain easy Hindi/Hinglish what was changed, what was verified, and how to undo it.

## 3. SYMPTOM -> WHERE TO LOOK (find your row, open only those files)
| What the owner sees | Workflow (GitHub > Actions) | Code | First thing to check |
|---|---|---|---|
| No Good Morning / bot silent in market hours | `trading_bot_session.yml` (started 08:40 IST by cron-job.org; backup crons are delayed hours) | `trading_bot.py` | Did cron-job.org fire (owner's account)? Is cell AlertLog **T2 = YES**? Latest run log. Manual fix: Actions > run `trading_bot_session.yml` |
| Prices/CMP in sheet old | `fetch_live_prices_session.yml` + `fetch_live_prices.yml` | `fetch_live_prices.py`, `live_prices_upstox.py` | `UPSTOX_MODE` variable (live/shadow/off), Upstox token (1-year, renew ~Oct 2027) |
| RS / ATR / DMA / 52-week columns old | `fetch_rs.yml` (08:45 + 12:30 IST) | `fetch_rs.py`, `fetch_opt_trend.py` | yfinance change; run log |
| Option signals missing/odd | appscript + bot | `appscript.gs` (`_mapTradeType`, `_generateOptionsSignal`), `trading_bot.py` `option_entry_gate` | Nifty200 columns `Opt_Trend`/`Options`; `[OPT-GATE]` lines in bot log. Switch off: `OPTION_REQUIRE_TREND=False` |
| No alerts at all although market moved | Apps Script (not GitHub) | `appscript.gs` | Script editor > Executions for errors; tabs `ScanReasons`/`ScanDiag` show WHY each stock was rejected. Deploy a fix: `.\deploy_appscript.ps1` (clasp, account ai360trading@gmail.com), bump `CONFIG.VERSION` |
| Result Watch / pre-market reel missing | `result-watch.yml`, `premarket-brief.yml` (both kicked by the bot start) | `result_watch.py`, `premarket_*.py` | Variables `RESULT_WATCH_MODE`, `PREMARKET_MODE` must be `scheduled` |
| Tech Short not uploaded | `tech-daily.yml` (05:47 UTC) | `tech_daily.py`, `tech_short.py` | Queue empty? (Telegram note says so); `YOUTUBE_CREDENTIALS_TECH`; `TECH_MODE=scheduled` |
| Website tech/lesson page missing or wrong | `tech-daily.yml` / `lessons-weekly.yml` (last step) | `tech_pages.py`, `lesson_pages.py` | run `python tech_pages.py` / `python lesson_pages.py` locally, commit `_pages/tt-*.html`, `_pages/ls-*.html` and the `_data/*_pages.json` |
| Weekly lesson missing | `lessons-weekly.yml` | `lesson_runner.py`, `lesson_builders*.py` | `LESSONS_ENABLED=true`; queue empty; failed quality gate (then nothing is published, by design) |
| Story Short (Tue/Thu) missing | `story-real.yml` | `story_real.py`, `story_writer.py` | `REAL_MODE=scheduled`; workflow must be ACTIVE (`gh workflow list --all`) |
| Articles / website | `daily-articles.yml`, Pages build | `generate_articles.py`, `_config.yml` | Jekyll build error in the Pages run; `ads_active: false` is intentional |
| Threads / Pinterest | `threads-post.yml`, `threads-refresh.yml`, `pin-feed.yml` | `threads_post.py`, `pin_feed.py` | `THREADS_MODE`; secret `THREADS_ACCESS_TOKEN` (auto-refresh 1st/15th) |
| Facebook/Instagram upload fails | the workflow that posts (pre-market, story) | `upload_facebook.py` (Instagram has retry + re-encode) | Meta token (`token_refresh.py` runs 1st/15th); kill switches `TOPICAL_FB`, `FB_ARTICLE_SHARE`, `TECH_FB_IG` are OFF on purpose |
| YouTube upload auth error | the workflow that uploads | `reauth_youtube.py` (`--which tech` for the tech channel) | Owner must log in once in the browser |
| Red "AI360 System Alert" | `watchdog.yml`, `auto_heal.yml` | `health_watchdog.py` | `RUNBOOK.md` has the non-technical steps per alert |
| Sheet formulas show #N/A | - | `fetch_*.py` feeds | GOOGLEFINANCE was replaced by Python feeds (never restore formulas in CMP/DMA/ATR columns) |
| Weekly Saturday Tracker report missing | `tracker-report.yml` | `tracker_report.py` | `TRACKER_REPORT_MODE=scheduled` |

Reach/views summary (read-only, no network): `python reach_report.py` (also the first section of the Saturday Tracker report).

Useful read-only checks: `python check_calls.py` (static call/argument check), `python -m pytest -q test_*.py` (155 tests), `python channel_health.py` via workflow `channel-health.yml` (Facebook/Instagram/YouTube status).

## 4. How the AI should work (keeps token use small)
1. Read this file + problem_report.txt. Ask the owner ONE question only if truly needed.
2. Open ONLY the files in the table row. Use search (grep) to find the function, then read ~100 lines around it. Do not read `SESSION.md` (690 KB), `.internal-ops.md` (700 KB), `CHANGELOG.md` (400 KB) or all of `CLAUDE.md` (175 KB); search them for the exact keyword when a past decision is in question (e.g. the file name or constant).
3. Make the smallest fix. Prefer a kill-switch variable or a revert over a rewrite.
4. Before pushing: `python check_calls.py` and `python -m pytest -q test_*.py` must both pass, `python -m py_compile` on the changed file; for `appscript.gs` a node syntax check.
5. Push to `master` (GitHub runs it next time). Code changes do NOT affect a session loop that is already running: the three session workflows (`trading_bot_session`, `fetch_live_prices_session`, `swing_board_session`) check out code once per start, so a same-day fix takes effect at the next fresh start (cancel + re-run the workflow to force it).
6. Tell the owner (easy Hinglish): what was wrong, what you changed, what you verified, how to undo, what to look at tomorrow. Add 3-4 lines to `SESSION.md` and, if a locked rule or version changed, one line to the matching `CLAUDE.md` table row.

## 5. Keeping the content running after the queues end (no subscription needed)
- **Tech Shorts queue ends about 23 Jan 2027** (81 topics; `tech_topics5.py` was added 2026-11-15). Add topics: copy the pattern of `tech_topics5.py` into a new file `tech_topics6.py` (same dict shape via `_mk`, a list `ORDER`, a `register()`), import it next to `tech_topics5` in `tech_short.py` (try/except blocks) and in `tech_daily.py` (`TOPIC_ORDER = TOPIC_ORDER + [...]`), and add its `OBJ3D` update in `tech_short.py`. Rules for every topic: simple Hinglish, facts only, NO invented numbers, no digits in narration (spell numbers; the cyber-crime helpline 1930 is spoken as words), no risky repair advice (say "technician"), no brand names unless the topic is that app, 5 scenes, under 59 seconds. Test: run workflow `tech-sample.yml` (does not upload), listen/look, then it just continues daily. Ask any AI: "write 30 more topics in the exact shape of tech_topics5.py about common everyday phone/laptop/internet/scam problems people search in Hindi".
- **Weekly lessons queue ends about 19 Dec (US English) and 27 Dec (India Hindi) 2026** (`lesson_builders3.py` added sw01, ct01, sv01 on 2026-11-15). Add a lesson: a `build_xxx(region)` function in a new `lesson_builders4.py` (same shape as `build_sw01` / `build_rm03`, using `_pack` from `lesson_builders2`), register it at the bottom of `lesson_builders.py` like `lesson_builders3`. Test one locally without uploading: `python lesson_runner.py --region in --lang hi --mode dry --lesson ID --out some_folder`. Every lesson must pass `lesson_bank.quality_gate()` (a real number from our own data, a "Rule:" line, an honest limit, no hype). Run `lessons-weekly.yml` manually with a test/private mode first. If you do nothing: it only sends a Telegram note and never repeats.
- **Story Shorts** write new stories automatically (`story_writer.py`). If it stops: set `REAL_MODE=dry` and tell an AI.
- Any content stopping is NOT dangerous: trading alerts do not depend on it.

## 6. Tokens and renewals (the only things that expire)
| Secret | Renewal |
|---|---|
| `GH_TOKEN` (GitHub PAT) | watchdog warns 21 days before; make a new PAT (no expiration) and update the secret |
| `UPSTOX_ANALYTICS_TOKEN` | about Oct 2027; read-only |
| `THREADS_ACCESS_TOKEN` | auto-refresh on the 1st and 15th |
| Meta (Facebook/Instagram) | `token_refresh.py` on the 1st and 15th; if it fails, new long-lived token |
| `YOUTUBE_CREDENTIALS` (trading) / `_TECH` | `python reauth_youtube.py [--which tech] --set-secret` |
| `GCP_SERVICE_ACCOUNT_JSON` | Google service account; the Sheet must stay shared with it |
| `TELEGRAM_BOT_TOKEN` | @BotFather; secret update |
| Groq / Gemini / Cloudflare / Pexels | free keys; if one dies jobs fall back to templates or send a failure note |
Writing a GitHub secret needs the owner's explicit OK in chat. Never print or paste a token.

## 7. Kill switches (GitHub > Settings > Secrets and variables > Actions > Variables, or `gh variable set NAME --body VALUE`)
`RESULT_WATCH_MODE`, `PREMARKET_MODE`, `THREADS_MODE`, `TECH_MODE`, `REAL_MODE`, `OPTION_WATCH_MODE`, `TRACKER_REPORT_MODE` (scheduled/dry) | `LESSONS_ENABLED`, `LESSON_FB` | `TECH_VISUAL` (3d/footage) | `UPSTOX_MODE` (live/shadow/off) | `TOPICAL_FB`, `FB_ARTICLE_SHARE`, `TECH_FB_IG` (off on purpose) | `LEGACY_REELS` (off). Pause everything trading: AlertLog cell **T2 = NO**.

**Website rule (17 Nov 2026):** any NEW root `.py` / `.gs` / `.bat` / `.ps1` or root doc `.md` MUST be added to `_config.yml` `exclude` by exact name (no globs), otherwise the public site serves it; `python -m pytest -q test_guards.py` checks this. Never rename the repo, never link to github.com from the site, videos or messages.

**Retest-only options (17 Nov 2026, owner order):** the Premium OPTIONS SIGNAL / Options Alert needs the sheet's `FINAL_ACTION` = '🎯 RETEST BUY' (appscript.gs `OPTIONS_CONFIG.RETEST_ONLY`). Off-switch without a deploy: add a BotMemory row with key `OPT_RETEST_OFF`. Review on/after 11 Dec with `python signal_watch.py --report`.

**Option rules (16 Nov 2026):** the Premium 'OPTIONS SIGNAL' is sent by `appscript.gs` and follows the SAME rule as the bot gate (expiry >= 8 calendar days (owner order 17 Nov; was 15), HV-20 <= 35% from sheet column `Opt_HV20`, NIFTY PCR 0.6-1.4, daily trend OK). `OPTION_WATCH_MODE` is **dry on purpose** (members mistook the watch list for calls) - do not set it to scheduled without the owner re-wording the message.

## 8. Where the real documentation is
`PROJECT_HANDOFF.md` (PC-local, not on GitHub: top section = final state, evidence, pending decisions) | `RUNBOOK.md` (non-technical alert guide) | `CLAUDE.md` (every file's version + the locked decisions) | `.internal-ops.md`/`SESSION.md`/`CHANGELOG.md` (full history, PC-local, backed up in the owner's private backup repo by `backup_pc_docs.bat`).
