# CHANGELOG — AI360Trading

---

## 2026-05-30 (cont.) — Auto-heal loop + self-sustaining holidays + article image fix

- **Auto-heal self-remediation** (NEW `auto_heal.py` + `auto_heal.yml`, every 30 min): finds failed GitHub Actions jobs and auto-re-runs them (up to 2 retries; most failures are transient), considers only each workflow's latest run, skips monitoring workflows, and escalates to Telegram ONLY when a job fails all retries. Zero human action for the common case. **Verified live** (run 26652423075 → healthy=6, nothing to fix).
- **Article images FIXED** (`media_helper.py` v1.1 + `daily-articles.yml`): images weren't showing because (1) the workflow never passed `PEXELS_API_KEY` into the generator, and (2) the fallback `source.unsplash.com` was discontinued by Unsplash in 2024 (dead URLs). Wired the key; replaced Unsplash Source with LoremFlickr that is VERIFIED to resolve to a real image (rejects the "defaultImage" placeholder) before use, else Picsum — so a dead/placeholder image can never be written again. Patched the 2 already-published broken posts. All 4 pillars verified to resolve.
- **Holidays now self-sustaining** (`fetch_holidays.py` v1.2 → v1.3, `fetch_holidays.yml` yearly → monthly): fetches CURRENT + next year every month (was next-year-only on Dec 1), so a single failed fetch can't lose a year and mid-year special holidays are captured. **Caught + fixed a real bug live:** the NSE parser summed ALL market segments → returned **238** "holidays" for 2026 (would have stopped trading nearly every day). Fixed to parse the CM (equities) segment only + dedup + reject implausible counts (>25). BotMemory now holds the authoritative 20-date HOLIDAYS_2026 (16 weekday + 4 weekend, all correct), closing the gap where no HOLIDAYS_2026 existed.

---

## 2026-05-30 — MULTI-YEAR AUTONOMY: pinned deps + self-heal watchdog + family runbook

Goal (Amit ji): run perfect for YEARS, self-healing, free forever, working WITHOUT Claude after the subscription ends. Honest assessment given: system was robust for *months*, not yet *years-unattended*. Closed the biggest gaps:

- **Dependencies PINNED** (`requirements.txt`): was open ranges (`>=`) → every run pulled latest packages → one breaking upstream release (esp. yfinance) = silent unattended breakage. Pinned to the EXACT set verified green in run 26640890465. **Verified:** dispatched a real CI run (26650990707) → installed cleanly on Python 3.11, bot booted v15.14, `[SKIP]` outside hours. ✅
- **Self-heal watchdog** (NEW `health_watchdog.py` + `watchdog.yml`, daily 08:05 IST): checks Sheet reachability + automation switch (T2), trading-bot freshness, NSE data-feed freshness, GitHub Actions failures (24h), Telegram token validity. Sends a **plain-language** Telegram alert ONLY on problems (each with a fix step), plus a Monday ✅ heartbeat so silence is meaningful. Fail-safe, stdlib Telegram, ₹0. Manual `test_alert=true` button. **Verified live** (run 26651428062): all checks ran, "all healthy", test message delivered to Basic. ✅
- **Family runbook** (NEW `RUNBOOK.md`): plain-language "what each alert means + exact steps" for a non-technical family member — which issues they can fix themselves (T2, re-run a job, test alerts) vs. what to hand a developer. Watchdog alerts point here.

Remaining autonomy item: harden `fetch_holidays.py` to write current+next year (so holidays self-update forever). Then content channels (FB Group/IG/website/visuals) per Amit ji's 10-day goal.

---

## 2026-05-30 — CRITICAL: H2-2026 holiday correction (`trading_bot.py` v15.14 + `appscript.gs` v15.17)

Came out of the line-by-line `appscript.gs` audit. The Aug–Dec 2026 holidays in BOTH files were approximations and **materially wrong** — the same bug-class that caused the 2026-05-27 outage (one wrong date = a whole trading day with no signals, no monitoring, no exits).

### What was wrong → corrected (VERIFIED against NSE official circular + Zerodha + ClearTax, all three agree)
- ❌ `2026-08-27` Janmashtami — **not an NSE holiday** → removed
- ❌ `2026-10-21` + `2026-10-22` Diwali (guessed) → removed; actual **Diwali Balipratipada = `2026-11-10` (Tue)**
- ❌ `2026-11-04` Guru Nanak (guessed) → corrected to **`2026-11-24` (Tue)**
- ➕ added **`2026-09-14` Ganesh Chaturthi (Mon)** — was missing
- ➕ added **`2026-10-20` Dussehra (Tue)** — was missing
- ✅ kept `2026-10-02` Gandhi Jayanti, `2026-12-25` Christmas
- Note: `2026-11-08` Diwali Laxmi Pujan is a **Sunday** (Muhurat session only) — weekend check already handles it, intentionally not listed.

### Files
- `trading_bot.py` **v15.13 → v15.14** — NSE_HOLIDAYS_2026 H2 block corrected; version strings bumped. `py_compile` OK.
- `appscript.gs` **v15.16 → v15.17** — identical H2 correction; also bumped stale subscriber-facing "v15.15" Telegram strings to v15.17. **Deployed live via clasp** — verified pushed Code.js shows v15.17 + corrected dates.
- H1-2026 dates re-verified unchanged (already correct).

---

## 2026-05-30 — BULLETPROOFING: SMC scanner trust + observability (`fetch_smallmidcap.py` v1.0 → v1.1)

Session goal (Amit ji): "make the trading system bulletproof." Started with a live audit (gh CLI + Sheets MCP) before touching anything.

### Verified live state first (facts, not memory)
- **SmallMidCap tab still does NOT exist.** Scanner ran exactly once (manual dispatch 2026-05-28 23:42 IST, on Bakri Id holiday) → loaded stale bhavcopy → `0 candidates` → tab never created (v1.0 only wrote the tab when picks existed). Friday scheduled cron had not fired yet.
- **Trading bot core is HEALTHY.** 2026-05-29 12:13 IST run exited HINDALCO (+5.73%) and CUMMINSIND (+10.13%) as TARGET HITs → archived to History. Entry filters correctly rejected MOTHERSON/NATIONALUM/MARICO (overbought RSI / weak RS / low volume).
- **AlertLog "stuck" rows are NOT a bug.** Monitoring (`step_b`) only runs `if is_market_hours()`. PNBHOUSING fell below SL near/after close; post-close + weekend runs skip monitoring by design → it will exit Monday 2026-06-01 first market tick.

### Fixed in v1.1 (zero income risk — SMC has never produced a live signal)
- **REAL volume filter.** v1.0's "Vol 3.0×" shown to subscribers was a fake proxy (`turnover_cr / 20` = just "turnover ≥ ₹60 Cr"). v1.1 downloads the prior 5 trading days of bhavcopy and computes a genuine `today_qty ÷ 5-day-avg-qty` per symbol. Symbols with < 3 prior days of history are excluded (cannot confirm momentum → no fake number). New `fetch_bhavcopy_window()` + `build_avg_volume()`. Verified with synthetic data: 4× passes, 1.5× rejected, <3 days → 0 picks.
- **Always-observable tab.** `write_smc_sheet()` now always ensures the SmallMidCap tab and writes a dated row every scan — pick rows, or a single `NO CANDIDATES` status row on 0-pick days. Idempotent: a re-run for the same bhav date (e.g. weekday holidays re-serving the last file) does not duplicate rows. Amit ji now gets daily proof the scan ran.
- **Safer BotMemory write.** v1.0 did `bm.clear()` + full rewrite EVERY run — a crash between clear and rewrite would wipe the BotMemory the trading bot depends on. v1.1 only touches BotMemory when there are picks to add OR stale SMC_ keys to purge; otherwise BotMemory is left completely untouched. Also fixed the deprecated `worksheet.update()` arg order.

### RELIABILITY FIX SHIPPED — new `trading_bot_session.yml` (cron throttling)
- **Problem:** GitHub throttled the `*/5` trading-bot cron to ~3 runs/day (was 6–13/day early May, now 3/day for 5 straight trading days) vs ~96 expected. During the 6h15m market window often only ONE monitoring tick fired → a stock could blow through SL/target uncaught for hours.
- **Fix:** New `trading_bot_session.yml` — two reliable once-daily triggers (08:30 + 11:55 IST; low-frequency crons are honoured far better than `*/5`), each running an internal 5-min `sleep`-loop across its half of the session for dense, guaranteed ticks. Repo is PUBLIC → multi-hour loops cost ₹0.
- **Safety:** ADDITIVE — `trading_bot.py` untouched; the `*/5` cron stays as backup. Same concurrency group `trading-bot` + `cancel-in-progress:false` ⇒ session and backup cron can NEVER run together (no double-entry). Per-tick crash doesn't stop the loop.
- **Verified:** YAML + bash time-logic locally; live manual dispatch on the real runner (`end_time=21:21`) ran 1 tick → bot booted v15.13 → correctly `[SKIP] Outside hours` (no sheet writes) → loop self-exited at 21:21. First scheduled sessions: Monday 2026-06-01 08:30 + 11:55 IST.

---

## 2026-05-28 (evening) — LOCAL TOOLING SETUP (no repo file changes)

Operational setup only — no Python/AppScript/workflow files touched. All installs live outside the repo so they do not affect production.

### Installed on Amit ji's PC
- **GitHub CLI** v2.93.0 (portable zip, no admin) at `C:\Users\Admin\gh\bin\gh.exe` — added to user PATH. `gh auth login` completed via web device-flow as `systronics`. Token stored in Windows keyring, persists across sessions. Future Claude Code sessions can now query workflows + logs directly (`gh run list`, `gh run view --log-failed`).
- **mcp-google-sheets** pip package v0.6.3 at `C:\Users\Admin\AppData\Roaming\Python\Python314\Scripts\mcp-google-sheets.exe` — MCP server registered in `C:\Users\Admin\.claude.json` (user scope) with env `SERVICE_ACCOUNT_PATH=C:\Users\Admin\ai360trading\service_account.json`. Currently **disconnected** — `service_account.json` not yet downloaded. Will activate after Amit ji downloads JSON from Google Cloud Console + restarts Claude Code.

### Health audit (via new `gh` access)
Last 50 GitHub Actions runs: **zero failures since 2026-05-19** (9+ days clean). Trading Bot, content generators, FII/DII tracker, KeepAlive — all green. System healthy heading into Friday 2026-05-29 (first full day with Batch 1-5 active) and Friday 20:30 IST (first `fetch_smallmidcap.py` run, will auto-create SmallMidCap tab).

### Safety
`.gitignore` already protects `service_account.json` (line 69), `credentials.json` (68), `token.json` (70). JSON download will be safe from accidental commits.

---

## 2026-05-27 (late night) — BATCH-4 HOTFIX + BATCH 5 SMALL/MID CAP SCANNER (`trading_bot.py` v15.13 + new `fetch_smallmidcap.py`)

### Batch-4 silent bug — caught via Amit ji's screenshot 8
v15.12 keyword lookup for the Nifty200 "RelVol" column failed because the actual header is `Volume_vs_Avg_%` (percentage form, not multiple) — none of `relvol/rvol/rel_volume/relativevolume` matched. The volume filter has been failing-open since deploy. Also: relative-strength was being computed from `cp − prev_close` when the sheet already has a pre-computed `RS` column.

#### Fixed in `trading_bot.py` v15.12 → v15.13
- `_find_nifty200_col(sheet, exact_names, substring_keywords)` now does EXACT match first (protects short headers like `RS` from false-hits on `Pivot_Resistance`), substring fallback second.
- `_read_nifty200_relvol(...)` matches `Volume_vs_Avg_%` exactly AND converts percentage form (|raw|>5) to multiple internally (`1 + raw/100`).
- New `_read_nifty200_rs(...)` reads the pre-computed `RS` column directly.
- RS filter in `check_all_entry_filters` prefers the sheet's RS value; falls back to the v15.12 math path if column absent.
- New `_nifty200_rows(sheet)` cache — one sheet fetch per tick, served to every column reader.

### Batch 5 — Small/Mid Cap Momentum Scanner
Highly selective daily scanner for small/mid cap winners outside Nifty200 universe. Per Amit ji's instruction "few signals, long ride, max momentum profit, no loss tolerance" — 0-3 picks/day, no auto-trade yet (deferred to Batch 6 with explicit approval).

#### Added — `fetch_smallmidcap.py` v1.0
- Pulls NSE cash bhavcopy CSV (5-day fallback walk if today's missing).
- Excludes Nifty200 symbols (universe = small/mid caps only).
- Filters: % change 4–12% (excludes upper-circuit lottery), turnover ≥ ₹20 Cr, delivery % ≥ 50%, volume multiple ≥ 3×.
- Score = `pct × delivery × min(vol_mult, 6) / 100`. Top 3.
- Outputs: new `SmallMidCap` sheet tab (auto-created via `add_worksheet`), BotMemory `SMC_{YYYY-MM-DD}_RANK{N}_{SYM}` keys, Telegram digest to Advance + Premium.
- Stale-cleans `SMC_*` rows older than 14 days each run.
- 0-pick days send a "no qualifying setups today" digest — quality over quantity.

#### Added — `.github/workflows/fetch_smallmidcap.yml`
- Mon-Fri 20:30 IST (15:00 UTC) — after bhavcopy publishes (~18:30) and after `fetch_bhavcopy.py` at 20:00.
- Standard failure-alert step.

### Manual tasks for Amit ji
None for Batch 5. AppScript v15.16 paste is the only pending manual task (already mentioned — confirm if done). Screenshot 8 confirmed the sheet has the columns we need; no rename necessary.

### Pending next batches
- Batch 4b (optional): VWAP filter via yfinance 1m data
- Batch 6: auto-trade on SMC picks (after 2-4 weeks of paper-tracked performance)

---

## 2026-05-27 (night) — BATCH 4 INSTITUTIONAL EDGES (`trading_bot.py` v15.12 + new `institutional_edges.py` + new `fetch_bhavcopy.py`)

### Goal
Add five "smart money" filters that consistently-profitable traders + FIIs use to confirm a setup. Each is a soft-gate added to `check_all_entry_filters`; every one fails open if its data source is unavailable. Per `feedback_free_forever_self_repair` — all free, all self-healing.

### Added — `institutional_edges.py` v1.0 (new module)
- **`check_relative_strength(sym, cp, prev_close, nifty_pct)`** — entry requires stock_pct − nifty_pct ≥ 1.0%. A stock not keeping up with Nifty is not a leader.
- **`check_volume_confirmation(sym, rel_vol)`** — entry requires today's relative volume ≥ 1.5×. Volume is institutional footprint.
- **`check_fii_regime(bm_data, is_bullish, now)`** — blocks longs if FII cash net ≤ ₹-2000 Cr (heavy outflow); blocks shorts if ≥ +₹2000 Cr. Uses already-fetched `MKT_FII_CASH_NET_{date}` from `fetch_fii_dii.py`.
- **`check_pcr_regime(bm_data, is_bullish)`** — soft filter; logs PCR extremes but doesn't block (PCR is contrarian indicator). Uses `MKT_PCR_NIFTY` from `fetch_bhavcopy.py`.
- **`check_delivery_percent(sym, bm_data)`** — entry requires `DLV_{SYM}` ≥ 40% (institutional accumulation vs day-jobbing). Uses NEW DLV_* keys from `fetch_bhavcopy.py`.

### Added — `fetch_bhavcopy.py` v1.0 (new fetcher)
- Daily NSE cash bhavcopy parser (`sec_bhavdata_full_DDMMYYYY.csv`) → `DLV_{SYM}` per equity.
- NSE option-chain indices API → `MKT_PCR_NIFTY` + `MKT_PCR_BANKNIFTY`.
- DLV_*  rows are wholesale-replaced each day (not accumulated) so BotMemory stays lean.
- 3-tier fail-safe: NSE bhavcopy → walks back 5 days for missing files → existing cache continues if all fail. Soft Basic-channel notice if both sub-fetchers down.

### Added — `.github/workflows/fetch_bhavcopy.yml`
- Mon-Fri 20:00 IST (14:30 UTC) — NSE archives publish bhavcopy ~6:30 PM, 1.5h buffer.
- Standard failure-alert step matching existing workflows.

### Changed — `trading_bot.py` v15.11 → v15.12
- Wrapped `import institutional_edges as inst_edges` with try/except — bot survives missing/broken module (falls back to v15.11 filter set).
- New self-healing helper `_find_nifty200_col(sheet, header_keywords)` — finds column by HEADER NAME via case-insensitive substring match. Caches per-process. No hardcoded column indices that drift when AppScript adds columns.
- New helper `_read_nifty200_relvol(sheet, sym)` — uses the above to find relative-volume column dynamically.
- `check_all_entry_filters` extended with 5 new filters (RS, Volume, FII, PCR, Delivery) appended AFTER existing v15.10 filters. Each individually try/except'd so a buggy check cannot cascade.
- `step_a_enter_trades` passes `cp`, `nifty_sheet`, `bm_data` through to filters.

### Self-repair design
1. `institutional_edges` import wrapped — bot runs without it.
2. Each of the 5 filters individually try/except'd in `check_all_entry_filters`.
3. Nifty200 RelVol column resolved by header name (not index) — survives AppScript column additions.
4. `fetch_bhavcopy.py` walks back 5 days if today's bhavcopy missing.
5. Wholesale DLV_* replacement each day prevents stale rows from building up.
6. PCR is contrarian → soft filter, never blocks (just informational log).

### Pending for next batches
- Batch 4b: VWAP filter (yfinance 1m data — deferred because per-stock yfinance call is expensive)
- Batch 5: Small/mid cap scanner from NSE bhavcopy (fixes PositionalLatest missing the ALKALI / GUJTHEM / TVSSRICHAK-class movers)

---

## 2026-05-27 (evening) — BATCH 3 OPTION-BUYING INTELLIGENCE (`trading_bot.py` v15.11 + new `option_intelligence.py` + new `fetch_earnings.py`)

### Goal
Move option recommendations from "guesswork ATM/OTM picks" to actual edge-trading: ITM strikes (Δ≈0.7), HV-based IV gate, stock-anchored exits, PE side for bearish regime, earnings-window block. All free, all self-healing — per `feedback_free_forever_self_repair` memory.

### Added — `option_intelligence.py` v1.0 (new module)
- **`compute_itm_strike(cp, direction, depth)`** — NSE strike-step table (1/2/5/10/20/50/100); picks 1-2 strikes ITM for ~0.65–0.75 delta. Pure math, no API.
- **`get_historical_volatility(symbol, days=20)`** — annualised 20-day HV via yfinance, IV-proxy. In-process cache to avoid duplicate calls per tick.
- **`check_iv_regime(symbol)`** — calm/normal/elevated/extreme classification; blocks new CE/PE if HV > 55%. Fails open if yfinance unavailable.
- **`check_earnings_window(symbol, mem, now, days=3)`** — reads BotMemory `EARNINGS_{SYM}_{DATE}` keys; blocks if announcement within ±3 days.
- **`recommend_option(symbol, cp, atr, stage, is_bullish, mem, now)`** — single entry point combining all checks. Returns `{action, strike, label, delta, hv, reasons, sl_pct, tgt_pct}`. Bearish regime now produces `BUY_PE`, not `SKIP`.
- **`format_option_alert(...)`** — builds the option block appended to TRADE ENTRY alerts.

### Added — `fetch_earnings.py` v1.0 (new fetcher)
- Daily NSE event calendar fetcher with BSE fallback.
- Writes/de-dupes BotMemory `EARNINGS_{SYM}_{DATE} = "Result"` rows.
- Stale-clean: rows older than 7 days purged per run.
- If both NSE & BSE fail: exits cleanly (no GH Action failure flap), sends soft Basic-channel notice; existing cache continues serving.

### Added — `.github/workflows/fetch_earnings.yml`
- Daily 18:30 IST cron (13:00 UTC).
- Standard failure-alert step matching `fetch_fii_dii.yml` pattern.

### Changed — `trading_bot.py` v15.10 → v15.11
- Imports `option_intelligence` with graceful fallback (try/except). If module missing or import fails, bot still runs — falls back to old v15.10 ATM/OTM logic.
- `ce_candidate_flag(...)` accepts `sym`, `mem`, `now` and routes through `opt_intel.recommend_option` for smart path; old logic kept as fallback for self-repair.
- `build_entry_premium(...)` passes `mem` and `now` through.
- Stock-anchored exit text on fallback path too: "Exit on stock −1.5%" (was "option −40%").

### Self-repair design notes (per `feedback_free_forever_self_repair`)
1. `option_intelligence` module load wrapped in try/except — bot survives a missing or broken module.
2. Every `option_intelligence` external call (yfinance HV, BotMemory earnings read) fails open. A single network failure cannot stall a tick.
3. `fetch_earnings.py` tries NSE → BSE → existing cache, in that order. Never marks GH Action as failed if both upstream sources are down (existing cache is the third tier).
4. BotMemory cache aged out automatically (7-day TTL inside the fetcher).
5. New module is independently version-stamped (v1.0) and unit-testable without the live sheet.

### Pending for next batches
- Batch 4 (institutional edges): volume + relative-strength + VWAP + PCR/OI/delivery via NSE bhavcopy, gate entries on real FII flow.
- Batch 5 (universe breadth): small/mid cap scanner from NSE bhavcopy.

---

## 2026-05-27 (afternoon) — BATCH 2 PROFIT PROTECTION (`trading_bot.py` v15.10) + filename cleanup

### Goal
"Zero/min loss on losers, full ride with profit-lock on winners." Five professional-grade upgrades on top of v15.9.

### Added (`trading_bot.py` v15.9 → v15.10)
- **ONE-R BREAKEVEN** — breakeven now activates at the SOONER of the fixed-% threshold (e.g. STD = +2.0%) or +1R, where R = (entry − initial SL). Floor at +0.8% so a freak tight SL can't trigger BE on a tiny wiggle. Behaviour only improves vs. v15.9 — BE moves in EARLIER, never later.
- **CHANDELIER TRAIL** — trail step now uses `cur_max − atr*mult` (highest-high anchor), replacing the CMP-anchored `cp − atr*mult`. TSL can only rise. Cap at `cp*0.99` retained so SL is always strictly below current price. Locks much more of a parabolic gain.
- **PARTIAL BOOK @ +5%** — at +5% unrealised gain, fires a one-time Advance/Premium alert recommending "book 50%, trail rest". Gated by `{key}_PB1` flag in BotMemory so it fires once per trade. Paper trading keeps full-position P/L unchanged (no sheet qty tampering); Phase-4 live trading will actually halve the order.
- **TIME STOP** — after 5 trading days if gain < +3%, exit with reason `⏰ TIME STOP (Nd, +X%)`. Cash intraday exempt (has 3 PM force exit). Triggers AFTER target/TSL checks so winners are never cut early.
- **INDIA VIX FILTER** — fetch `^INDIAVIX` via yfinance once per tick; block new entries if `VIX > 22`. Fails open if fetch errors. Existing trades continue normal monitoring/exits regardless of VIX.

### Renamed
- `appscript_v14.gs` → `appscript.gs` — filename was misleading (file content is v15.16, name said v14). AppScript editor doesn't read filenames; manual paste flow unchanged. Historical CHANGELOG entries kept with old name (accurate as of those dates).

### Watchlist breadth — deferred to Batch 5
User noted PositionalLatest webview shows only F&O-eligible large caps; today's screenshots showed +10-20% movers in small/mid caps (ALKALI, SURYALA, THOMASCOTT, JPPOWER, GUJTHEM, TVSSRICHAK). Scanner universe is Nifty200 — these stocks were never scanned. Fix is a separate small/mid cap scanner pulling NSE bhavcopy (free, daily). Out of scope for Batch 2.

### Not yet in this batch
- Batch 3 (option-buying upgrade): ITM strikes, IV percentile via NSE option chain, earnings block, stock-anchored exits, PE side
- Batch 4 (institutional edges): volume + relative-strength + VWAP filter, PCR + OI + delivery % from NSE bhavcopy, gate entries on real FII flow already being fetched
- Batch 5 (universe breadth): small/mid cap scanner

---

## 2026-05-27 (morning) — BATCH 1 SAFETY FIXES (`trading_bot.py` v15.9 + `appscript_v14.gs` v15.16)

### CRITICAL — Holiday list was wrong
- Wed 2026-05-27 was hardcoded as a holiday in **both** `trading_bot.py:155` and `appscript_v14.gs:156`. The actual NSE holiday is **Thu 2026-05-28 (Bakri Id)**.
- Impact today: bot exited at startup with `[SKIP] Holiday` → no Good Morning Telegram, no entry checks, no target-hit exit. **CUMMINSIND (+12.01% target hit)** and **HINDALCO (+6.08% target hit)** stayed open with status `TRADED` instead of being booked as wins.
- Several other 2026 dates were also off-by-one vs. the NSE official Equities calendar (Holi, Ram Navami, Mahavir Jayanti missing; Good Friday + Muharram on wrong day). All corrected from the official NSE list (screenshot 7).
- AppScript file bumped v15.15 → v15.16 — **needs manual paste into Apps Script editor** (GitHub deploy not supported for AppScript).

### Fixed (`trading_bot.py` v15.8 → v15.9)
- **BUG-B** — Trailing SL was only stored in BotMemory; AlertLog column O stayed blank for every winner (see screenshot 2 — all `Trailing SL: —`). Now writes the trailing SL value to column O after each TSL update. Best-effort try/except so a sheet write failure doesn't block the in-memory state.
- **BUG-C** — WAITING row with SL >= current price would cause instant exit on promotion to TRADED (MCX example today: SL ₹3,194 set Tue, today MCX -4.5% to ₹3,012 → SL above price). Now skipped with `[SETUP INVALIDATED]` log line, row left as WAITING for AppScript to age out.
- **BUG-E** — `today_entries` count included `_CASH_` keys, so a cash intraday trade silently ate into the 3-per-day swing budget. Now counts only `_ENTRY_` keys that aren't cash.

### Why this batch
User reported "no Telegram today". Diagnosis showed bot-killed-by-bad-holiday-list. Same root cause also explains the screenshot anomalies (HINDALCO + CUMMINSIND past target but still TRADED; trailing SL column empty for all winners; MCX waiting row showing SL > price). All four issues fixed in one batch with full file edits per Rule C.

### Pending for next batches
- Batch 2 (profit protection): tighter breakeven, partial book at +5%, Chandelier exit, time stop, VIX filter
- Batch 3 (options buying upgrade): ITM strikes, IV percentile via NSE option chain, earnings block, stock-anchored exits, PE side for bearish regime
- Batch 4 (institutional edges): volume + relative-strength + VWAP filter, PCR + OI + delivery from NSE bhavcopy, gate entries on real FII flow already being fetched

---

## 2026-05-26 (night) — REAL FII/DII DATA LAYER ADDED

### Added
- `fetch_fii_dii.py` v1.0 — daily NSE FII/DII Cash market flow tracker. Free, official NSE source, no API key needed. Writes BotMemory keys under `MKT_*` prefix (e.g., `MKT_FII_CASH_NET_2026-05-26`, `MKT_FII_TREND_5D`, `MKT_FII_REGIME`). Posts Hinglish summary to Basic and full breakdown + interpretation to Advance/Premium.
- `.github/workflows/fetch_fii_dii.yml` — runs Mon-Fri 6:45 PM IST (cron `15 13 * * 1-5`). Includes the new on-failure Telegram alert.

### Why this matters
The existing `FII_Buy_Zone`, `FII_Rating`, `Leader_Type`, `FII_Signal` columns in the Nifty200 sheet are **technical indicators with FII-themed labels** — they compute from price + SMA + 52W position + volume (confirmed 2026-05-26 by reading the cell formulas). They were NOT real institutional flow data despite the naming.

Decision: NOT renaming the existing columns (renaming the output strings would require coordinated sheet + code change across many match sites in appscript_v14.gs, risking breakage). Instead, added a SEPARATE real FII data layer under `MKT_*` namespace that doesn't collide.

### Roadmap (Phase 2)
- F&O FII data: index futures position, options call/put bought/sold — for options buying entry decisions
- Integration into AppScript scanner as second-layer confirmation (only enter when both technical setup AND real FII regime agree)
- Stock-level FII data deferred (free sources don't expose; paid service breaks ₹0/month rule)

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
