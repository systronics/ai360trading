# AI360Trading — Master System Documentation

**Last Updated:** April 4, 2026 — Trading Bot v13.5 + AppScript v13.3
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 Planned | Phase 4 (Dhan Live) Planned
**Primary Audience:** Bilingual Hindi + English — Indian retail traders + global investors

> ⚠️ **Read this file completely before making ANY changes.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT).

---

## 1. Real Mission

> This system is built to run **forever, fully automated**, generating passive income for the owner's family — even without active involvement. Built on ₹0/month infrastructure. No employees. No office. Pure automation.

### Monetisation — Every Stream Simultaneously

| Stream | Platform | High-CPM Target Countries |
|---|---|---|
| Video Ad Revenue | YouTube (Hindi) | USA, UK, Canada, Australia, UAE |
| Video Ad Revenue | YouTube (English) | USA, UK, Canada, Australia — 3–5x higher CPM |
| Shorts / Reels Bonus | YouTube, Facebook, Instagram | USA, UK, Brazil, India |
| Website Ad Revenue | GitHub Pages (ai360trading.in) | USA, UK, Canada |
| In-Stream Video Ads | Facebook Page | USA, UK, Brazil, India |
| Paid Signal Subscriptions | Telegram (Advance + Premium channels) | India, UAE, Global |

### Target Countries by Ad CPM Priority

1. 🇺🇸 USA — Highest CPM globally for finance content
2. 🇬🇧 UK — Very high CPM, strong trading audience
3. 🇦🇺 Australia — High CPM, growing retail base
4. 🇦🇪 UAE — High CPM, large NRI + Gulf investor audience
5. 🇨🇦 Canada — High CPM, similar to USA
6. 🇧🇷 Brazil — Large audience, fast-growing finance CPM
7. 🇮🇳 India — Largest volume, Nifty/stock focus

> **AI Rule:** Always optimise content topics, hooks, SEO tags, and posting times for these countries.
> USA/UK prime time = 11 PM–1 AM IST. Include global keywords in all titles, descriptions, and tags.
> All hooks and CTAs rotate from human_touch.py — never hardcode them in generators.

---

## 2. Platform Status

| Platform | Status | Notes |
|---|---|---|
| YouTube Hindi | ✅ Auto | Analysis + Education + Shorts + Reels working |
| YouTube English | 🔄 Building | Phase 3 — auto-translated separate channel |
| YouTube Shorts | ✅ Auto | Short 2 + Short 3 working |
| YouTube Community Posts | ✅ Built | generate_community_post.py — 12:00 PM daily |
| YouTube Reels | ✅ Auto | ZENO reel (8:30 PM) working |
| YouTube Morning Reel | ✅ Auto | 7:00 AM reel (generate_reel_morning.py) working |
| Facebook Page | ✅ Auto | Posts, reels, article shares all working |
| Facebook Group | ❌ Broken | Missing `publish_to_groups` token scope — see Section 12 |
| Instagram | ⚠️ Partial | Upload chain built; `INSTAGRAM_ACCOUNT_ID` secret needed |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | Signal alerts to all 3 channels (paper trading — followers take manual entry) |

---

## 3. Content Mode System

Mode is **auto-detected** by `indian_holidays.py` at the start of every workflow and written to `$GITHUB_ENV`. All scripts read `CONTENT_MODE` environment variable — never hardcoded.

| Mode | When | Content Strategy |
|---|---|---|
| `market` | Mon–Fri (excluding Indian holidays) | Live Nifty50/Global data, trade setups, signals |
| `weekend` | Saturday–Sunday | Educational, wealth-building, global audience focus |
| `holiday` | Indian Market Holidays | Motivational, "Market band hai par seekhna chalu", holiday name shown |

**Detection logic:** `indian_holidays.py` → NSE API (primary) → hardcoded fallback dates

---

## 4. Daily Content Output (Fully Automated)

| # | Content | Time (IST) | Platform | Status |
|---|---|---|---|---|
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + FB + Instagram | ✅ |
| 2 | Part 1 Video (16:9) | 7:30 AM weekday / 9:30 AM weekend | YouTube | ✅ |
| 3 | Part 2 Video (16:9) | 7:30 AM (same workflow) | YouTube | ✅ |
| 4 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | ✅ |
| 5 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 6 | Short 4 English (9:16) | 11:30 AM (same workflow) | YouTube English Shorts | 🔄 Phase 3 |
| 7 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 8 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB + Instagram | ✅ |
| 9 | YouTube Community Post | 12:00 PM | YouTube Community Tab | ✅ |
| **Total** | **12 pieces/day** | — | — | — |

> **USA/UK prime time content:** Videos uploaded at IST times but SEO-optimised for 11 PM–1 AM IST peak.

---

## 5. GitHub Actions Workflows

| File | Trigger (IST) | Purpose | Mode-Aware |
|---|---|---|---|
| `main.yml` | Every 5 min (market hours, Mon–Fri) | `trading_bot.py` — Nifty200 signals | ✅ Auto-skips weekends/holidays |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 (analysis) + Part 2 (education) | ✅ |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 + Community Post | ✅ |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning Reel + ZENO Reel | ✅ |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages | ✅ |
| `token_refresh.yml` | Every 50 days (1st + 20th of month) | Auto META token refresh | N/A |
| `keepalive.yml` | Periodic | Prevents GitHub disabling inactive workflows | N/A |

All workflows support `workflow_dispatch` with a `content_mode` dropdown to force any mode for testing.

---

## 6. Complete File Map

### Core Infrastructure (Phase 1 — Complete)

| File | Role | Status |
|---|---|---|
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates fallback | ✅ |
| `human_touch.py` | Anti-AI-penalty layer — 50+ hooks, personal phrases, TTS variation, SEO tags | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update + Telegram alert | ✅ |

### Core Content Generation (Phase 2 — All Upgraded)

| File | Role | Key Tech | Status |
|---|---|---|---|
| `trading_bot.py` | Nifty200 signal monitor + TSL manager + Telegram alerts | gspread + Google Sheets + Telegram Bot API | ✅ v13.5 |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Swara) | ai_client, human_touch, Edge-TTS | ✅ Phase 2 |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ai_client, human_touch, MoviePy | ✅ Phase 2 |
| `generate_reel_morning.py` | Morning reel (7:00 AM) — day/country aware | ai_client, human_touch, MoviePy | ✅ |
| `generate_analysis.py` | 8-slide market analysis video (Part 1) | ai_client, human_touch, MoviePy | ✅ Phase 2 |
| `generate_education.py` | Educational deep-dive video (Part 2) | ai_client, human_touch, content_calendar | ✅ Phase 2 |
| `generate_articles.py` | 4 SEO articles daily → Jekyll _posts | ai_client, human_touch, Google Indexing | ✅ Phase 2 |
| `generate_community_post.py` | YouTube daily community text post — 12:00 PM | ai_client, human_touch | ✅ Phase 2 |

### Upload & Distribution

| File | Role | Status |
|---|---|---|
| `upload_youtube.py` | Uploads reel; saves `youtube_video_id` + `public_video_url` to meta | ✅ |
| `upload_youtube_english.py` | Uploads to English channel (separate credentials) | 🔄 Phase 3 |
| `upload_facebook.py` | Uploads reel to FB Page; shares to Group; posts articles | ✅ |
| `upload_instagram.py` | Auto-uploads via Meta API using `public_video_url` from meta | ✅ |

### Infrastructure

| File | Role |
|---|---|
| `indian_holidays.py` | Mode detection — NSE API + fallback; shared by ALL workflows |
| `content_calendar.py` | Rotates topics: Options, Technical Analysis, Psychology |

### Static Assets

| Path | Contents |
|---|---|
| `public/image/` | `zeno_happy.png`, `zeno_sad.png`, `zeno_greed.png`, `zeno_thinking.png` |
| `public/music/` | `bgmusic1.mp3`, `bgmusic2.mp3`, `bgmusic3.mp3` — rotated by weekday |

---

## 7. AI Fallback Chain

All content generation uses `ai_client.py`. **Never call Groq/Gemini/Claude/OpenAI directly in generators.**

```
Groq — llama-3.3-70b-versatile (primary — fastest, free)
    ↓ fails
Google Gemini — gemini-2.0-flash (secondary — best image/video roadmap for Disney 3D)
    ↓ fails
Anthropic Claude — claude-haiku-4-5 (tertiary — best human-touch writing)
    ↓ fails
OpenAI — gpt-4o-mini (quaternary — reliable fallback)
    ↓ all fail
Pre-generated templates in human_touch.py (always works — zero downtime)
```

**Import pattern in ALL generators — no exceptions:**
```python
from ai_client import ai, img_client
from human_touch import ht, seo
```

**Usage pattern:**
```python
# Text generation
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang="hi")

# JSON generation
data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")

# Humanize raw output
clean = ht.humanize(raw_output, lang="hi")

# Get rotating hook
hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")

# Get SEO tags
tags = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")
```

---

## 8. Trading Bot Architecture

### Overview

The trading system is split across two components that work together:

| Component | File | Version | Role |
|---|---|---|---|
| AppScript | Google Sheets bound script | v13.3 | Scans Nifty200, applies 10 gates, writes WAITING candidates to AlertLog, stores memory in T4 |
| Python Bot | `trading_bot.py` | **v13.5** | Monitors AlertLog every 5 min, manages WAITING→TRADED, TSL updates, exit logic, Telegram alerts |

**Current status:** Paper trading. Followers receive Telegram signals and take manual entry. Dhan API integration planned for Phase 4 after backtest validation.

### Google Sheets Structure

| Sheet | Purpose |
|---|---|
| `Nifty200` | Live data for all 200 stocks — CMP, DMAs, FII data, signals, scores (34 cols A–AH) |
| `AlertLog` | Active + waiting trades — 15 rows max (rows 2–16), 20 cols. T2=YES/NO switch. T4=memory string |
| `History` | Closed trade log — 18 cols A–R |
| `PriceCache` | Helper sheet — Symbol, Date, Close, High, Low, Volume, LastUpdate |
| `TempPriceCalc` | Scratch sheet for intermediate GOOGLEFINANCE calculations |
| `Corporate_Action` | Dividend/split events — NSE Symbol, Action Type, Ex-Date, Amount, Face Value |

> ⚠️ **Corporate_Action sheet is currently unpopulated.** If a dividend ex-date passes on an open trade, the system will not adjust the SL or flag it. Manual monitoring required until Phase 4.

### AlertLog Column Map (0-based)

```
A=0  Signal Time    B=1  Symbol        C=2  Live Price     D=3  Priority Score
E=4  Trade Type     F=5  Strategy      G=6  Breakout Stage H=7  Initial SL
I=8  Target         J=9  RR Ratio      K=10 Trade Status   L=11 Entry Price
M=12 Entry Time     N=13 Days in Trade O=14 Trailing SL    P=15 P/L%
Q=16 ATH Warning    R=17 Risk ₹        S=18 Position Size  T=19 SYSTEM CONTROL
```

**T2** = automation on/off switch (set "YES" to enable — anything else disables)
**T4** = memory string (comma-separated key=value pairs — stores TSL, MAX, ATR, CAP, MODE, SEC, EXDT, daily flags)

> ⚠️ **Known live issue (as of April 4, 2026):** NSE:ONGC and NSE:ADANIPOWER in AlertLog show RR=1:1.5, written before v13.3 raised MIN_RR to 1.8. The v13.5 bot FIX 3 will skip these rows when they are WAITING. However both are already in TRADED status, so they will continue to be monitored normally until exit. The RR column will be recalculated correctly on next entry.

### Live AlertLog State (April 4, 2026)

| Symbol | Status | Entry | SL | Target | RR | Mode | Capital |
|---|---|---|---|---|---|---|---|
| NSE:ONGC | 🟢 TRADED (PAPER) | ₹275.10 | ₹232.35 | ₹339.35 | 1:1.5* | VCP | ₹13,000 |
| NSE:ADANIPOWER | 🟢 TRADED (PAPER) | ₹150.30 | ₹143.48 | ₹160.53 | 1:1.5* | MOM | ₹13,000 |

*Pre-v13.3 entries — RR below current MIN_RR 1.8 but actively monitored since already TRADED.

### T4 Memory — Current State

```
Length: ~5,056 chars (248 parts) as of April 4, 2026
After v13.5 clean_mem runs: ~4,788 chars (233 parts)
Symbols cleaned (>30 days exited): NSE_ONGC (March exit), NSE_PNB
Market regime flags: BEARISH every day since 2026-03-05 onwards
```

> ⚠️ T4 is approaching the Google Sheets 50,000 char cell limit over time. v13.5 `clean_mem()` now does two-pass cleanup — first finding symbols with `_EXDT_` dates older than 30 days, then pruning ALL their keys. This resolves the growth issue identified in v13.4. Monitor `mem=N chars` in GitHub Actions logs.

### Nifty200 Column Map (0-based, used by AppScript)

```
r[0]  NSE_SYMBOL          r[1]  SECTOR
r[2]  CMP                 r[3]  %Change (D)
r[4]  20_DMA              r[5]  50_DMA
r[6]  200_DMA             r[7]  SMA_Structure (H)
r[8]  52W_Low             r[9]  52W_High (J)
r[10] %up_52W_Low         r[11] %down_52W_High
r[12] %dist_20DMA (M)     r[13] Avg_Volume_20D
r[14] Volume_vs_Avg% (O)  r[15] FII_Buy_Zone (P)
r[16] FII_Rating (Q)      r[17] Leader_Type (R)
r[18] Signal_Score (S)    r[19] FINAL_ACTION (T)
r[20] RS (U)              r[21] Sector_Trend (V)
r[22] Breakout_Stage (W)  r[23] Retest% (X)
r[24] Trade_Type (Y)      r[25] Priority_Score (Z)
r[26] Pivot_Resistance(AA) r[27] VCP_Status (AB)
r[28] ATR14 (AC)          r[29] Days_Since_Low (AD)
r[30] 52W_Breakout_Score  r[31] Sector_Rotation_Score (AF)
r[32] FII_Buying_Signal(AG) r[33] Master_Score (AH)
```

> **ATR14 (col AC, r[28]):** This is GOOGLEFINANCE-derived — 14-day average of (daily high − daily low). Cached static value stored alongside formula using `IFERROR(__xludf.DUMMYFUNCTION(...), cached_val)` pattern. The v13.5 bot reads this column directly via `_read_atr_from_nifty200()` at entry time, which is the correct source. Sample values verified: ONGC ≈ ₹7.65, ADANIPOWER ≈ ₹8.60, ADANIENSOL ≈ ₹44.40, ADANIENT ≈ ₹48.20.

> ⚠️ **ATR memory vs Nifty200 discrepancy:** The pre-v13.5 bot estimated ATR backwards from `(target - cmp) / mult`. For ONGC: memory shows ATR ₹21.42, but Nifty200 col AC shows ₹7.65 (correct). For ADANIPOWER: memory shows ₹3.41, Nifty200 shows ₹8.60 (correct). Existing open trades use the wrong ATR for TSL calculations until they exit. New entries from v13.5 onward use the correct value.

### AppScript v13.3 — Key Logic

**Market Regime:** Nifty50 CMP vs 20DMA → Bullish or Bearish. Controls which filter gate applies.
Current state: Bearish continuously since March 5, 2026.

**Bearish gate (4 conditions all required):**
- Leader_Type = "Sector Leader"
- AF ≥ 5 (Sector_Rotation_Score ≥ 5)
- Master_Score ≥ 22
- FII signal ≠ "FII CAUTION" or "FII SELLING"

**10 scan gates (in order):**
1. FII SELLING → skip always
2. Market regime filter (bullish vs bearish path)
3. Late entry block (BREAKOUT CONFIRMED needs RS≥7)
4. Price validity (CMP>0, ATR>0, CMP≤₹5,000)
5. Extension filter (>8% above 20DMA → skip)
6. Pivot resistance buffer (within 2% below pivot → skip)
7. Volume filter (bullish market only — vol<120% → skip)
8. ATH buffer (within 3% of 52W high → skip)
9. Trade type (AVOID/NO TRADE → skip)
10. Sector concentration (max 2 stocks per sector)

**Capital tiers:**
- ₹13,000 — MasterScore≥28 AND AF≥10 (high conviction)
- ₹10,000 — MasterScore≥22 OR Accumulation Zone (medium conviction)
- ₹7,000 — standard
- Max deployed: ₹45,000 (₹5,000 always held as buffer)

**Trade modes (stored as `{sym}_MODE` in T4 memory):**
- `VCP` — VCP_Status (AB) < 0.04 + pre-breakout stage
- `MOM` — SMA_Structure = "Strong Bull" + RS ≥ 6
- `STD` — everything else (default in bear market)

**Memory keys written per stock (by AppScript):**
- `{sym}_CAP` = capital tier (7000/10000/13000)
- `{sym}_MODE` = trade mode (VCP/MOM/STD)
- `{sym}_SEC` = sector name (for Good Morning sector context)

**Sort order:** finalScore DESC, then ATR% ASC as tiebreaker within ±2 score points (minimum SL preference).

**Batched scanner:** Processes 60 rows per 5-min time trigger, stores intermediate candidates in `_BATCH_CANDS` key (URL-encoded JSON). Full scan on manual SYNC.

### Python Bot v13.5 — Key Logic + All Changes

#### v13.5 Changes (3 surgical fixes)

**Fix 1 — `clean_mem()` two-pass orphan cleanup:**

Previous version only pruned date-prefixed flags older than 30 days. Symbol keys (_CAP, _MODE, _SEC, _ATR, _LP, _MAX, _TSL) for exited symbols grew forever.

New logic:
- Pass 1: scan all parts for `_EXDT_` entries (no `=` sign, format `NSE_ONGC_EXDT_2026-01-15`). Build set of symbols exited >30 days ago.
- Pass 2: drop (a) old date flags AND (b) ALL keys starting with `{sym}_` or `{sym}=` for old symbols.

Key detail: `_EXDT_` entries have NO `=` sign. The date is embedded directly in the key: `NSE_ONGC_EXDT_2026-03-04`. Split on `_EXDT_` not `=`.

**Fix 2 — ATR read directly from Nifty200 at entry:**

Previous: `atr_est = (target - cp) / mult` — backwards derivation, systematically wrong.

New: `_read_atr_from_nifty200(nifty_sheet, sym)` scans Nifty200 for the row where col A matches `sym`, reads col AC (index 28). Falls back to old formula only if lookup returns 0.

This fixes TSL calculations for all new entries. Existing open trades (ONGC, ADANIPOWER) continue using the memory-cached (wrong) ATR until they exit.

**Fix 3 — RR re-validation on WAITING→TRADED:**

Previous: pre-v13.3 WAITING rows with RR 1:1.5 could be promoted to TRADED.

New: Step A parses `r[C_RR]` (col J), splits on `:`, takes the last part as `rr_val`. If `rr_val > 0 and rr_val < MIN_RR (1.8)` → skip with log message. Rows with empty RR pass through (AppScript sets correctly for new candidates).

#### TSL Parameters (mode-aware, unchanged from v13.3)

```python
TSL_PARAMS = {
    "VCP": { "breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0 },
    "MOM": { "breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0 },
    "STD": { "breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0 },
}
TSL_GAP_LOCK_FRAC = 0.5
```

**TSL progression (STD example):**
- Gain < 2% → hold initial SL
- Gain 2–4% → move to breakeven (entry price)
- Gain 4–10% → lock at entry +2%
- Gain > 10% → ATR trail (2.5× ATR below CMP)
- Gain > 8% gap-up → lock 50% of gap + ATR trail (whichever higher)

**STD trail widened in v13.3** (trail 6→10%, atr_mult 1.5→2.5) to let swing trades run longer before trailing kicks in.

#### Daily Message Schedule

| Time (IST) | Trigger | Channels |
|---|---|---|
| 08:45–09:15 | Good Morning | All 3 |
| 09:15–15:30 | Market hours — entry/exit/TSL | Basic: exits only; Advance+Premium: full |
| 12:28–12:38 | Mid-day pulse | All 3 |
| 15:15–15:45 | Market close summary | All 3 |
| Friday 15:15 | Weekly summary (via AppScript) | Basic: win rate only; Advance+Premium: full ₹ |

#### Good Morning — Sector Context

Reads `{sym}_SEC` key from T4 memory for each WAITING row. Groups by sector. Sends top 4 sectors with count to Advance+Premium. Example: `🔄 Active Sectors: Power (2), Pharma (1), FMCG (1)`.

#### Telegram Channel Tiers

| Channel | Content |
|---|---|
| Basic (free, @ai360trading) | Market mood, signal closed (WIN/LOSS only, no ₹), membership CTA |
| Advance (₹499/mo) | Full entry/exit with ₹ P/L, TSL updates, mid-day pulse, CE candidate flag |
| Premium (bundle) | Same as Advance + Options Advisory (for "Options Alert" trade type) |

#### CE Candidate Flag (v13.4, unchanged in v13.5)

Added to Advance+Premium entry alerts when market is bullish AND stock ATR% > 1.5%.
Uses ATR14 from Nifty200 (same value read by Fix 2) — no new data needed.

```
ATR% < 1.5%    → no flag (premium decay exceeds stock move)
ATR% 1.5–2.5%  → normal mover: Strike ATM, Target +65%, SL -40% on premium
ATR% > 2.5%    → fast mover: Strike ATM+1, Target +50%, SL -35% on premium
BREAKOUT CONFIRMED stage → use OTM strike (ATM+1)
```

Currently informational only. Dhan API needed for live CE execution (Phase 4).

#### Hard Exit Rules

- Loss > 5% → hard loss exit (immediate, no min-hold check)
- Min hold: 2 trading days swing, 3 days positional (prevents TSL whipsaw on day 1)
- Near hard loss (<−4%) in bearish market → skip min-hold, allow early exit
- 5 trading day cooldown per symbol after exit before re-entry

#### BOT_MODE Entry Points

```python
if mode == "test_telegram":    run_test_telegram()
elif mode == "daily_summary":  run_daily_summary()
elif mode == "weekly_summary": run_weekly_summary()
else:                          run_trading_cycle()   # default
```

### History Sheet Columns (A–R)

```
A  Symbol      B  Entry Date   C  Entry Price  D  Exit Date
E  Exit Price  F  P/L%         G  Result        H  Strategy
I  Exit Reason J  Trade Type   K  Initial SL    L  TSL at Exit
M  Max Price   N  ATR at Entry O  Days Held     P  Capital ₹
Q  Profit/Loss ₹               R  Options Note
```

### All-Time Performance (as of April 4, 2026)

```
Total closed trades: 25
Wins: 2 | Losses: 23 | Win rate: 8%
Total P/L: ₹−7,013
Period: All trades since Feb 27, 2026 — bear market conditions throughout
Market was in BEARISH regime from March 5, 2026 onwards
```

> **Context:** All 25 trades occurred during a sustained bearish Nifty regime (CMP below 20DMA). The bearish filter is now active and restricts entries to Sector Leaders with high conviction scores only. This is expected to improve win rate in Phase 4 once market turns bullish or Dhan live execution tightens entries.

---

## 9. Cross-System Consistency (v13.5 Audit — April 4, 2026)

This section documents confirmed alignment and known gaps between AppScript v13.3, trading_bot.py v13.5, and the Google Sheet.

### ✅ Aligned

| Item | AppScript | Bot | Sheet |
|---|---|---|---|
| MIN_RR | 1.8 | 1.8 (FIX 3) | RR column written correctly for new entries |
| Capital tiers | ₹7k/₹10k/₹13k | reads from memory | memory holds correct values |
| Trade modes | VCP/MOM/STD | reads from memory | memory holds correct values |
| Market regime | Nifty CMP vs 20DMA | same logic | Nifty200 row 2 = NIFTY50 |
| ATR source | r[28] = col AC | Nifty200 col 28 (FIX 2) | GOOGLEFINANCE AVERAGE high-low 14d |
| Memory key format | `{sym}_CAP/MODE/SEC` | reads `{sym}_CAP/MODE/SEC` | T4 cell |
| EXDT format | `{sym}_EXDT_{date}` (no =) | split on `_EXDT_` (FIX 1) | T4 cell |
| Sector context | writes `{sym}_SEC` | reads `{sym}_SEC` for GM | T4 cell |
| Max trades | 5 | 5 | T2 switch controls |
| Max waiting | 10 | 10 | 15 rows total (rows 2–16) |

### ⚠️ Known Gaps (not bugs — by design or pending fix)

| Gap | Detail | Impact | Resolution |
|---|---|---|---|
| Trade Type col Y vs bot `_mapTradeType` | Nifty200 col Y formula still uses old intraday logic (BREAKOUT CONFIRMED + RS>7). AppScript v13.3 overrides this with correct intraday detection (vol>200% + green + Bull). Two are out of sync. | Low — AppScript output is correct, col Y is only a reference | Update col Y formula to match AppScript logic in next sheet revision |
| ATR in memory for existing open trades | ONGC memory ATR=₹21.42, Nifty200 actual=₹7.65. ADANIPOWER memory ATR=₹3.41, Nifty200 actual=₹8.60. TSL calculations for these trades use wrong ATR. | Medium — TSL trails may be too wide (ONGC) or too narrow (ADANIPOWER) | Exit and re-enter. FIX 2 prevents this for all future entries. |
| RR on existing open trades | ONGC and ADANIPOWER show RR=1:1.5 (pre-v13.3). Both are already TRADED so FIX 3 does not affect them. | Low — trades are already active and being monitored | No action needed — will resolve on exit |
| Corporate_Action sheet empty | Dividend ex-dates not tracked. | Low for now — no open trades have known upcoming dividends | Manual monitoring until Phase 4 |
| AppScript weekly summary vs bot weekly summary | AppScript `sendWeeklySummary()` sends only to the single `CHAT_ID` (basic channel). Bot `run_weekly_summary()` sends to all 3 channels with full ₹ breakdown. Two separate weekly messages fire. | Low — subscribers see richer report from bot; AppScript report is redundant | Consider disabling AppScript weekly summary since bot covers it |

---

## 10. Critical Upload Chain

Scripts must run in this exact order. Each one feeds data to the next:

### Evening ZENO Reel (8:30 PM)
```
generate_reel.py
    └── output/reel_YYYYMMDD.mp4
    └── output/meta_YYYYMMDD.json  ← created here (public_video_url = "")

upload_youtube.py
    └── Uploads reel to YouTube
    └── Writes to meta → youtube_video_id, youtube_video_url, public_video_url

upload_facebook.py
    └── Uploads reel to Facebook Page
    └── Posts link to Facebook Group (when fixed)
    └── Overwrites meta → public_video_url (Facebook watch URL)
    └── Posts articles from RSS feed to Page + Group

upload_instagram.py
    └── Reads public_video_url from meta
    └── Submits to Instagram API → polls until FINISHED → publishes
```

### Morning Reel (7:00 AM)
```
generate_reel_morning.py
    └── output/morning_reel_YYYYMMDD.mp4
    └── output/morning_reel_meta_YYYYMMDD.json

upload_youtube.py (morning mode)
upload_facebook.py (morning mode)
upload_instagram.py (morning mode)
```

### Daily Videos (7:30 AM)
```
generate_analysis.py
    └── output/analysis_video.mp4
    └── output/analysis_video_id.txt       ← Part 1 ID for Part 2 linking
    └── output/analysis_meta_YYYYMMDD.json

generate_education.py
    └── Reads analysis_video_id.txt → links Part 1 in description
    └── output/education_video.mp4
    └── output/education_video_id.txt
    └── output/education_meta_YYYYMMDD.json
    └── Updates Part 1 YouTube description with Part 2 URL
```

> **Manual fallback for Instagram:** GitHub Actions → Run → Artifacts → download → post manually.

---

## 11. Environment Variables & Secrets

All stored in **GitHub Actions Secrets**. Never hardcode any of these values.

### Dhan Trading API (added — Phase 4 live trading)
| Secret | Purpose | Status |
|---|---|---|
| `DHAN_API_KEY` | API key | ✅ Added — not connected yet |
| `DHAN_API_SECRET` | API secret | ✅ Added — not connected yet |
| `DHAN_CLIENT_ID` | Client ID | ✅ Added — not connected yet |
| `DHAN_PIN` | Account PIN | ✅ Added — not connected yet |
| `DHAN_TOTP_KEY` | 2FA TOTP key | ✅ Added — not connected yet |

> Dhan integration planned for Phase 4 after backtest validation. Currently all trading is paper-mode via Google Sheets + AppScript.

### Social Platforms
| Secret | Purpose | Status |
|---|---|---|
| `META_ACCESS_TOKEN` | Facebook + Instagram API | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` | Facebook App ID | ✅ Added |
| `META_APP_SECRET` | Facebook App Secret | ✅ Added |
| `FACEBOOK_PAGE_ID` | Target Facebook Page ID | ✅ |
| `FACEBOOK_GROUP_ID` | Target Facebook Group ID | ✅ (posting broken — token scope issue) |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business/Creator numeric ID | ✅ Added |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON (Hindi channel) | ✅ |
| `YOUTUBE_CREDENTIALS_EN` | YouTube OAuth JSON (English channel) | ✅ Added |

### AI Providers (Fallback Chain)
| Secret | Purpose | Priority | Status |
|---|---|---|---|
| `GROQ_API_KEY` | Groq — Llama 3.3 70B | Primary | ✅ |
| `GEMINI_API_KEY` | Google Gemini 2.0 Flash | Secondary | ✅ Added |
| `ANTHROPIC_API_KEY` | Claude Haiku | Tertiary | ✅ Added |
| `OPENAI_API_KEY` | GPT-4o-mini | Quaternary | ✅ Added |

### Telegram
| Secret | Purpose |
|---|---|
| `TELEGRAM_TOKEN` | Bot authentication token (used by trading_bot.py) |
| `TELEGRAM_BOT_TOKEN` | Same token (used by some generators — keep in sync) |
| `TELEGRAM_CHAT_ID` | Free channel — `CHAT_BASIC` in bot |
| `CHAT_ID_ADVANCE` | Advance signals channel — ₹499/month |
| `CHAT_ID_PREMIUM` | Premium signals channel — bundle |

> ⚠️ **Channel ID swap note:** In trading_bot.py, `CHAT_ADVANCE = os.environ.get('CHAT_ID_PREMIUM')` and `CHAT_PREMIUM = os.environ.get('CHAT_ID_ADVANCE')`. The env var names are intentionally swapped. Do NOT "fix" this without verifying which channel ID is which in your Telegram setup.

### Google / GCP
| Secret | Purpose |
|---|---|
| `GCP_SERVICE_ACCOUNT_JSON` | Search Console Indexing API + Google Sheets (gspread) |

### General
| Secret | Purpose |
|---|---|
| `GH_TOKEN` | GitHub API token |

---

## 12. Known Issues & Fixes

### Facebook Group Posting ❌

**Root causes (check in order):**
1. `META_ACCESS_TOKEN` missing `publish_to_groups` scope
2. Bot account not **Admin** of the group
3. Group Settings → Advanced → "Allow content from apps" OFF
4. App not approved for Groups API by Meta

**Fix:** developers.facebook.com → App → Add `publish_to_groups` → regenerate token → update secret.

### Instagram Auto-Post ⚠️

`INSTAGRAM_ACCOUNT_ID` is now added. If still failing:
```
https://graph.facebook.com/me/accounts?access_token=YOUR_META_TOKEN
```
Verify the numeric ID matches exactly.

### YouTube Community Tab ⚠️

Requires **500+ subscribers**. If below threshold:
- `generate_community_post.py` saves post to `output/community_post_YYYYMMDD.txt` for manual posting
- Does not crash the workflow

### META_ACCESS_TOKEN Expiry — Automated ✅

`token_refresh.yml` runs every 50 days. Requires `META_APP_ID` and `META_APP_SECRET`.

### T4 Memory Growth — Fixed in v13.5 ✅

Two-pass `clean_mem()` now prunes ALL keys for symbols exited >30 days ago.
Monitor `mem=N chars` in GitHub Actions logs. Alert if approaching 40,000 chars.

### AppScript Duplicate Weekly Summary

AppScript `sendWeeklySummary()` fires on Fridays to one channel. Bot `run_weekly_summary()` also fires with richer content to all 3 channels. The AppScript version is redundant. Consider commenting out `sendWeeklySummary()` from `_runUnifiedManager()` and relying on the bot's weekly summary exclusively. Bot version is significantly better (includes monthly + all-time stats, best/worst trade, open count).

---

## 13. Human Touch System (Anti-AI-Penalty)

All content uses `human_touch.py`. **Never use raw AI output directly.**

| Technique | Method | What It Does |
|---|---|---|
| 50+ rotating hooks | `ht.get_hook(mode, lang)` | No two videos start the same |
| Personal phrases | `ht.get_personal_phrase(lang)` | "Maine dekha hai..." injected naturally |
| TTS speed variation | `ht.get_tts_speed()` | 0.95–1.05x range — passed to edge_tts rate param |
| Humanize output | `ht.humanize(text, lang)` | Strips robotic patterns, varies connectors |
| Emoji rotation | `ht.get_emoji_set()` | Day-seeded — different emoji set each day |
| SEO tags | `seo.get_video_tags(mode, lang)` | India + Global tags combined |
| Connector variation | Internal to humanize() | "aur/lekin/kyunki" rotated |
| Banned phrase removal | Internal to humanize() | "Certainly!", "It's important to note" stripped |

---

## 14. Technical Standards

### The "Full Code" Rule
> AI assistants **must always provide the complete content** of any modified file. Partial snippets or diffs are strictly prohibited.

**Standard AI task prompt:**
```
Context: I am working on the ai360trading system. Refer to SYSTEM.md for architecture.
Task: [Your Task]
Note: Provide the full code for any file you modify.
```

### AI Client Usage Rule — No Exceptions
> **Never call AI APIs directly in generators.** Always use:
```python
from ai_client import ai, img_client
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang=LANG)
data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang=LANG)
```

### Human Touch Usage Rule — No Exceptions
> **Never use raw AI output.** Always pass through human_touch:
```python
from human_touch import ht, seo
hook   = ht.get_hook(mode=CONTENT_MODE, lang=LANG)
clean  = ht.humanize(raw_script, lang=LANG)
tags   = seo.get_video_tags(mode=CONTENT_MODE, lang=LANG)
speed  = ht.get_tts_speed()  # pass to edge_tts rate param
```

### Dependency Pins

| Package | Version | Reason |
|---|---|---|
| `Pillow` | `>=10.3.0` | Required for LANCZOS resampling |
| `imageio` | `==2.9.0` | Prevents MoviePy rendering crashes |
| `moviepy` | `==1.0.3` | Force reinstall — newer versions break audio |
| `yfinance` | Latest | Use `fast_info['last_price']` only — not `.history()` |
| `PyNaCl` | Latest | Required for GitHub Secret encryption in token_refresh.py |
| `google-generativeai` | Latest | Gemini fallback in ai_client.py |
| `anthropic` | Latest | Claude fallback in ai_client.py |
| `openai` | Latest | OpenAI fallback in ai_client.py |
| `gspread` | Latest | Google Sheets access in trading_bot.py |
| `oauth2client` | Latest | GCP service account auth for gspread |
| `pytz` | Latest | IST timezone handling in trading_bot.py |

### Voice Assignments

| Voice ID | Gender | Used For |
|---|---|---|
| `hi-IN-MadhurNeural` | Male | Short 2 — authoritative trade setups |
| `hi-IN-SwaraNeural` | Female | Short 3, ZENO Reel, Morning Reel, Analysis, Education |
| `en-US-JennyNeural` | Female | English channel — all English content |
| `en-US-GuyNeural` | Male | English Short 2 alternative |

### TTS Speed via human_touch
```python
tts_speed = ht.get_tts_speed()           # returns float 0.95–1.05
rate_pct  = int((tts_speed - 1.0) * 100)
rate_str  = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
await edge_tts.Communicate(text, VOICE, rate=rate_str).save(path)
```

### Video Formats

| Content | Ratio | Platform |
|---|---|---|
| Analysis + Education | 16:9 | YouTube |
| Short 2, Short 3, Short 4, Morning Reel, ZENO Reel | 9:16 | YouTube Shorts / Reels / Instagram |

### SEO Tags Strategy

Every video includes both India-specific AND global tags via `seo.get_video_tags()`:
- India: `Nifty50`, `TradingIndia`, `StockMarketIndia`, `BankNifty`
- Global: `USStocks`, `UKInvesting`, `BrazilMarket`, `UAEInvesting`, `GlobalInvesting`
- Universal: `Finance`, `Investing`, `FinancialLiteracy`, `Shorts`

---

## 15. Disney 3D Reel Roadmap

| Phase | Tool | Quality | Timeline | Status |
|---|---|---|---|---|
| 1 (Now) | PIL + MoviePy + ZENO PNG | 2D animated slides | Current | ✅ Active |
| 2 | Gemini Veo API (free tier) | AI video clips | 3–6 months | Hooks in ai_client.py |
| 3 | Stable Diffusion + AnimateDiff | 3D style frames | 6–12 months | Planned |
| 4 | Google Veo 2 / Sora (when free) | True Disney-style 3D | 12–18 months | Planned |

> `img_client` in `ai_client.py` is the upgrade hook — swap in Phase 2 generation with zero changes to generators.

---

## 16. Full Data Flow

```
Market hours (Mon–Fri, 9:15 AM–3:30 PM IST)
└── main.yml (every 5 min)
    └── trading_bot.py v13.5
        └── clean_mem() → two-pass orphan cleanup (FIX 1)
        └── get_sheets() → gspread → AlertLog + History + Nifty200
        └── get_market_regime() → Nifty CMP vs 20DMA → bullish/bearish
        └── Step A: WAITING→TRADED
            └── FIX 3: RR re-validation (skip if rr_val > 0 and rr_val < 1.8)
            └── FIX 2: _read_atr_from_nifty200() → col AC (index 28)
            └── Entry alert → Advance+Premium (with CE candidate flag if bullish + ATR%>1.5%)
        └── Step B: Monitor TRADED (TSL update → Advance+Premium)
        └── Exit logic (TSL hit / target hit / hard loss / min-hold)
        └── History sheet append on exit
        └── T4 memory string saved each run

AppScript v13.3 (Google Sheets bound — triggered on schedule or manually)
└── Nifty200 sheet scan (batched 60 rows per run)
└── 10-gate filter → bearish or bullish path
└── Conviction bonus + capital tier + trade mode
└── ATR% tiebreaker sort (min SL preference within ±2 score)
└── Write WAITING rows to AlertLog
└── Write _CAP, _MODE, _SEC keys to T4 memory
└── Bearish alert with top sector context → Telegram (1 channel)
└── Morning cleanup 9:05–9:15: clear WAITING rows, keep TRADED
└── Friday 15:15: weekly summary → Telegram (1 channel — redundant with bot)

7:00 AM daily
└── daily_reel.yml (morning job)
    └── generate_reel_morning.py → upload chain ✅

7:30 AM / 9:30 AM daily
└── daily-videos.yml
    └── generate_analysis.py → Part 1 → YouTube ✅
    └── generate_education.py → Part 2 → YouTube ✅

10:00 AM / 11:30 AM daily
└── daily-articles.yml
    └── generate_articles.py → 4 articles → GitHub Pages ✅ → Facebook ✅

11:30 AM / 1:30 PM daily
└── daily-shorts.yml
    └── generate_shorts.py → Short 2 + Short 3 → YouTube ✅
    └── generate_community_post.py → Community Tab ✅

8:30 PM daily
└── daily_reel.yml (evening job)
    └── generate_reel.py → ZENO reel
    └── upload_youtube.py ✅ → upload_facebook.py ✅ → upload_instagram.py ⚠️
```

---

## 17. Website

- **URL:** `ai360trading.in`
- **Hosting:** GitHub Pages (Jekyll, `master` branch `_posts/`)
- **Publishing:** Auto-commit by `daily-articles.yml`
- **SEO Indexing:** Instant via `GCP_SERVICE_ACCOUNT_JSON`
- **Revenue:** Google AdSense (USA/UK English readers = highest CPM)
- **Content pillars:** Stock Market, Bitcoin/Crypto, Personal Finance, AI Trading
- **Market coverage:** India (Nifty50, BankNifty), USA (S&P500, NASDAQ), UK (FTSE100), Brazil (IBOVESPA), Crypto (BTC, ETH)

---

## 18. Social Media Links

| Platform | Handle/Link |
|---|---|
| 🌐 Website | ai360trading.in |
| 📣 Telegram (Free) | @ai360trading |
| 📣 Telegram (Advance) | ai360trading_Advance — ₹499/month |
| 📣 Telegram (Premium) | ai360trading_Premium — bundle |
| ▶️ YouTube | @ai360trading |
| 📸 Instagram | @ai360trading |
| 👥 Facebook Group | facebook.com/groups/ai360trading |
| 📘 Facebook Page | facebook.com/ai360trading |
| 🐦 Twitter/X | @ai360trading |

---

## 19. Phase Roadmap

### Phase 1 ✅ Complete
`ai_client.py`, `human_touch.py`, `token_refresh.py`, `generate_reel_morning.py`

### Phase 2 ✅ Complete
`generate_articles.py`, `generate_analysis.py`, `generate_education.py`, `generate_reel.py`, `generate_shorts.py`, `generate_community_post.py` — all upgraded to ai_client + human_touch

### Phase 3 🔄 In Progress
| Item | File | Priority |
|---|---|---|
| English channel shorts | `generate_english.py` | 🟡 Medium |
| English channel upload | `upload_youtube_english.py` | 🟡 Medium |
| Fix Facebook Group token | Manual config task | 🔴 High |
| Instagram verify live | Test after `INSTAGRAM_ACCOUNT_ID` added | 🔴 High |
| Disney 3D reel upgrade | `ai_client.py` img_client Phase 2 | 🔵 Future |
| Update Nifty200 col Y formula | Match AppScript v13.3 intraday logic | 🟡 Medium |

### Phase 4 📋 Planned — Dhan Live Trading
| Item | Dependency | Notes |
|---|---|---|
| Backtest validation | 30–40 paper trades at ≥35% win rate | Currently 8% in bear market — wait for regime change |
| Dhan API connection | `DHAN_API_KEY` secrets already added | Auto-execute on WAITING→TRADED |
| Options CE execution | Dhan API + lot size data | CE flag already in alerts (informational only) |
| Live capital deployment | After backtest confirms system | ₹45,000 max deployed (₹5k buffer) |
| Fix ATR for existing trades | Manual re-entry or wait for exit | ONGC and ADANIPOWER using pre-v13.5 ATR |

---

## 20. How to Test Everything

### Test a workflow manually
GitHub Actions → select workflow → **Run workflow** → set `content_mode` dropdown → watch logs.

### Verify trading bot
In logs (`main.yml`), look for:
```
[REGIME] Nifty CMP ₹22679 vs 20DMA ₹23547 → BEARISH
[INFO] Active trades: 2/5
[ATR] NSE:ONGC: read ATR14=7.65 from Nifty200
[TSL] NSE:ONGC [VCP]: ₹232.35→₹235.00
[DONE] 15:20:01 IST | mem=4788 chars
```

If FIX 2 active: `[ATR] {sym}: read ATR14=X.XX from Nifty200`
If FIX 2 fallback: `[ATR] {sym}: Nifty200 lookup returned 0, fallback atr_est=X.XX`
If FIX 3 active: `[SKIP] {sym}: RR 1:1.5 below MIN_RR 1.8 — stale pre-v13.3 candidate`

### Verify AppScript
Open Google Sheet → AI360 TRADING menu → MANUAL SYNC → check Logger output:
```
[REGIME] CMP=22679 20DMA=23547 Bullish=false
[CAND] NSE:ADANIPOWER | Score=24 | ATR%=2.1 | ₹10000 | STD | AF=8.2 | Qty=64
[DONE] Traded=2 | Waiting=3 | Bullish=false
```

### Automation on/off switch
Google Sheet → AlertLog → cell T2 → set "YES" to enable, anything else to disable.

### Force each content mode
```
workflow_dispatch → content_mode = market   # weekday content
workflow_dispatch → content_mode = weekend  # weekend content
workflow_dispatch → content_mode = holiday  # holiday content
```

### Verify ai_client fallback chain
In logs, look for:
```
✅ AI generated via groq
```
If Groq is down: `⚠️ groq failed` → `✅ AI generated via gemini`

---

*Documentation maintained by AI360Trading automation.*
*Full audit: April 4, 2026 — Claude Sonnet 4.6*
*v13.5 changes: clean_mem() two-pass orphan cleanup, ATR direct from Nifty200 col AC, RR re-validation on WAITING→TRADED*
*Phase 1 complete: ai_client.py, human_touch.py, token_refresh.py, generate_reel_morning.py*
*Phase 2 complete: generate_articles.py, generate_analysis.py, generate_education.py, generate_reel.py, generate_shorts.py, generate_community_post.py*
*Trading bot: AppScript v13.3 + Python v13.5 — paper trading, 25 trades, 2W/23L in sustained bear market*
*Phase 3 remaining: generate_english.py, upload_youtube_english.py, Facebook Group fix, Instagram verify, Nifty200 col Y formula update*
*Phase 4 planned: Dhan live trading after backtest validation with ≥35% win rate in mixed market conditions*
*Update this file whenever architecture, secrets, platform status, or file logic changes.*
