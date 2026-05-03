# AI360Trading — Master System Documentation

**Last Updated:** May 3, 2026 — Trading Bot v13.4 | AppScript v14.0 | Generators v2 | Telegram token fix ✅ | Live trade data in all videos ✅
**Repo:** https://github.com/systronics/ai360trading
**Website:** https://ai360trading.in
**Owner:** Amit Kumar, Haridwar, Uttarakhand, India

---

## ⚠️ EVERY AI MUST READ THIS SECTION COMPLETELY BEFORE TOUCHING ANYTHING

This system is the **sole livelihood** of Amit Kumar's family. His family is non-technical and cannot fix anything if it breaks. The system must run **forever, fully automatically, with zero human intervention.**

### The 10 Absolute Rules — No Exceptions

| # | Rule | Why |
|---|------|-----|
| 1 | **NEVER break working code** | A broken workflow = zero income that day |
| 2 | **Always provide COMPLETE file replacements** | No partial snippets, no diffs, no "add this here" |
| 3 | **Cost must stay ₹0/month forever** | Verify free tier limits before adding any new service |
| 4 | **Never call AI APIs directly** | Always use `ai_client.py` — never Groq/Gemini/Claude/OpenAI directly |
| 5 | **Never use raw AI output** | Always pass through `human_touch.py` — YouTube penalises AI content |
| 6 | **Never execute real trades** | System is paper trading until Phase 4 is explicitly authorised |
| 7 | **Update SYSTEM.md after every change** | This file is the only memory across AI sessions |
| 8 | **Hook in first 5 seconds of every video** | Watch time is dropping — this is the #1 priority fix |
| 9 | **Thumbnails must have large bold text + emotion** | CTR is the #1 factor for YouTube growth |
| 10 | **When in doubt, do nothing new — fix what is broken** | Stability > features |

### How to Use This Document

1. Read Sections 1–3 first (Mission, Status, Priority Fixes)
2. Read the section relevant to your task
3. Check Section 12 for known bugs before starting
4. After your task, update Section 12 and this header's Last Updated date

---

## 1. Mission & Monetisation

> Build a fully automated passive income system that runs forever on ₹0/month infrastructure, generating income across every possible digital monetisation stream simultaneously.

### Income Streams (All Active or Building)

| Stream | Platform | Target Countries | CPM Priority |
|--------|----------|-----------------|--------------|
| Video ad revenue | YouTube Hindi | USA, UK, Canada, Australia, UAE | High |
| Video ad revenue | YouTube English (Phase 3) | USA, UK, Canada, Australia | Highest (3–5× Hindi) |
| Shorts/Reels bonus | YouTube + Facebook | USA, UK, Brazil, India | Medium |
| Website ad revenue | ai360trading.in (GitHub Pages) | USA, UK, Canada | High |
| In-stream video ads | Facebook Page | USA, UK, Brazil, India | Medium |
| Paid signal subscriptions | Telegram (3 tiers) | India, UAE, Global | Recurring |
| Affiliate commissions | Insurance links in articles | India, UK, USA | Per-conversion |

### CPM Target Countries (in priority order)
1. 🇺🇸 USA — Highest CPM globally for finance content
2. 🇬🇧 UK — Very high CPM, strong trading audience
3. 🇦🇺 Australia — High CPM, growing retail base
4. 🇦🇪 UAE — High CPM, large NRI + Gulf investor audience
5. 🇨🇦 Canada — High CPM, similar to USA
6. 🇧🇷 Brazil — Large audience, fast-growing finance CPM
7. 🇮🇳 India — Largest volume, Nifty/stock focus

> **AI Rule:** USA/UK prime time = 11 PM–1 AM IST. Always include global keywords in titles, descriptions, and tags.

---

## 2. Current Phase Status

| Phase | Name | Status | Notes |
|-------|------|--------|-------|
| Phase 1 | Infrastructure | ✅ Complete | GitHub Actions, Jekyll, ai_client, human_touch, META token refresh |
| Phase 2 | Content Upgrade | ✅ Complete | All generators use ai_client + human_touch; trading bot v13.4 |
| Phase 3 | English Channel + Global Scale | 🔄 Building | English Shorts + YouTube English upload + Instagram auto |
| Phase 4 | Live Trading + Premium Options | 📋 Planned | Dhan API, real options advisory, real ATR14 |

---

## 3. Priority Fix Order (Most Important First)

> **Any AI working on this system should address these in order.**

### ✅ RECENTLY FIXED (May 2026)

| Item | Fixed | Notes |
|------|-------|-------|
| Telegram token name mismatch (`TELEGRAM_TOKEN` → `TELEGRAM_BOT_TOKEN`) | ✅ May 2026 | Owner fixed in `trading_bot.py` |
| No hook in first 5 seconds | ✅ May 2026 | All 3 generators v2 — hook overlay on first frame |
| Thumbnail: no emotion, no number, no contrast | ✅ May 2026 | All 3 generators v2 — 120px+ text, ZENO emotion, high contrast |
| Zero CTA at end of videos | ✅ May 2026 | `ht.get_cta()` injected in all 3 generators |
| No live trade data in videos | ✅ May 2026 | `fetch_live_trades()` / `fetch_open_trades()` in all 3 generators |
| Titles missing numbers + curiosity | ✅ May 2026 | `build_short_meta()` and `build_video_meta()` with real ₹ numbers |
| Descriptions: first 2 lines not keyword-rich | ✅ May 2026 | `video_description_line1/2` fields now generated per video |
| HerooQuest Kids Facebook upload broken | ✅ May 2026 | `META_ACCESS_TOKEN_KIDS` Page token created |

### 🔴 CRITICAL — Fix Now

| # | Issue | File | Impact |
|---|-------|------|--------|
| 1 | Telegram channel variables SWAPPED | `trading_bot.py` | Advance and Premium get same content — paying subscribers cheated |

### 🟡 IMPORTANT — Do This Week

| # | Issue | File | Impact |
|---|-------|------|--------|
| 2 | Facebook Group posting broken (token scope) | `upload_facebook.py`, GitHub Secrets | Missing Group distribution |
| 3 | Short 4 English not yet live | `generate_shorts.py` | Missing USA/UK audience entirely — highest CPM gap |
| 4 | Verify `ht.get_cta()` exists in `human_touch.py` | `human_touch.py` | All 3 generators call this — if missing, falls back silently to hardcoded string |
| 5 | Verify `GOOGLE_SHEET_ID` set in GitHub Secrets | All generators | `fetch_live_trades()` falls back to sheet name `"ai360trading"` if missing |

### 🟢 MEDIUM TERM — Next Month

| # | Issue | File | Impact |
|---|-------|------|--------|
| 11 | HerooQuest thumbnails: dark purple "H Scene 3" — nobody clicks | `kids-daily.yml` / kids generator | CTR 0.6% |
| 12 | HerooQuest content: too generic (Tortoise & Hare) | Kids content prompt | No unique angle |
| 13 | HerooQuest better angle: "Heroo learns about money" | Kids content prompt | Parents + kids = higher engagement |
| 14 | Pinned comment on every video driving Telegram growth | Post-upload step | Telegram → paid membership funnel |
| 15 | Instagram fully automated | `upload_instagram.py` | Currently manual |

---

## 4. Platform Status

| Platform | Status | Notes |
|----------|--------|-------|
| YouTube Hindi | ✅ Auto | Analysis + Education + Shorts + Reels |
| YouTube Shorts (Hindi) | ✅ Auto | Short 2 (Madhur) + Short 3 (Swara) — 400+ views |
| YouTube English | 🔄 Phase 3 | English channel automation TBD |
| YouTube Kids (HerooQuest) | 🔄 Building | Credentials added, upload working |
| YouTube Reels (ZENO 8:30 PM) | ✅ Auto | working |
| YouTube Morning Reel (7 AM) | ✅ Auto | working |
| Facebook Page (AI360Trading) | ✅ Auto | Posts, reels, article shares |
| Facebook Page (HerooQuest Kids) | ✅ Auto | Fixed May 2026 — uses `META_ACCESS_TOKEN_KIDS` |
| Facebook Group (ai360trading) | ❌ Broken | Token missing `publish_to_groups` scope — see Section 12 |
| Instagram | 📲 Manual | Download artifact → post manually |
| GitHub Pages (ai360trading.in) | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram (3 channels) | ✅ Auto | Paper trading signals — manual entry by followers |

---

## 5. Content Output Schedule (Daily, Fully Automated)

| # | Content | Time (IST) | Platform | Status |
|---|---------|-----------|----------|--------|
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + Facebook | ✅ |
| 2 | Part 1 Analysis Video (16:9) | 7:30 AM weekday / 9:30 AM weekend | YouTube | ✅ |
| 3 | Part 2 Education Video (16:9) | 7:30 AM (same workflow) | YouTube | ✅ |
| 4 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | ✅ |
| 5 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 6 | Short 4 English (9:16) | 11:30 AM (same workflow) | YouTube English Shorts | 🔄 Phase 3 |
| 7 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 8 | ZENO Reel (9:16) | 8:30 PM | YouTube + Facebook | ✅ |
| 9 | Instagram | Manual | Instagram | 📲 Artifact download |
| **Total** | **11 pieces/day auto + Instagram manual** | | | |

> **Best posting times for India audience:** 7–9 AM and 8–10 PM IST. Verify Shorts at 11:30 AM — may be too late.

---

## 6. Content Mode System

Mode is **auto-detected** by `indian_holidays.py` at workflow start → written to `$GITHUB_ENV`. All scripts read `CONTENT_MODE` — never hardcode it.

| Mode | When | Content Strategy |
|------|------|-----------------|
| `market` | Mon–Fri (excluding Indian holidays) | Live Nifty50/Global data, trade setups, signals |
| `weekend` | Saturday–Sunday | Educational, wealth-building, global audience focus |
| `holiday` | Indian Market Holidays | Motivational, holiday context, "Market band hai par seekhna chalu" |

Detection: `indian_holidays.py` → NSE API (primary) → hardcoded fallback dates

---

## 7. GitHub Actions Workflows

| File | Trigger (IST) | Purpose | Mode-Aware |
|------|--------------|---------|-----------|
| `trading_bot.yml` | Every 5 min (08:15–16:29 Mon–Fri) + 08:45, 12:58, 15:58 | Signal monitor + TSL + Telegram alerts | ✅ Auto-skips weekends/holidays |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 + Part 2 | ✅ |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 | ✅ |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning reel + ZENO reel | ✅ |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages | ✅ |
| `kids-daily.yml` | 8:00 AM daily | Kids video → YouTube + Facebook HerooQuest | ✅ |
| `token_refresh.yml` | 1st + 20th of month | Auto META token refresh | N/A |
| `keepalive.yml` | Periodic | Prevents GitHub disabling inactive workflows | N/A |

All workflows support `workflow_dispatch` with `content_mode` dropdown to force any mode for testing.

---

## 8. Complete File Map

### Core Infrastructure

| File | Role | Status |
|------|------|--------|
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates fallback chain | ✅ |
| `human_touch.py` | Anti-AI-penalty layer — 50+ hooks, personal phrases, TTS variation, SEO tags | ✅ |
| `indian_holidays.py` | Mode detection — NSE API + hardcoded fallback — shared by ALL workflows | ✅ |
| `content_calendar.py` | Rotates topics: Options, Technical Analysis, Psychology | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update + Telegram alert | ✅ |

### Content Generators

| File | Role | Key Dependencies | Status |
|------|------|-----------------|--------|
| `trading_bot.py` | Nifty200 signal monitor + TSL manager + Telegram alerts | gspread, Telegram Bot API | ✅ v13.4 |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Neerja). v2: hook overlay, live AlertLog trades, 120px thumbnail, CTA via `ht.get_cta()`, curiosity titles | ai_client, human_touch, edge-TTS, gspread | ✅ v2 May 2026 |
| `generate_reel.py` | ZENO 60s reel (8:30 PM). v2: ZENO emotion-matched thumbnail, big hook text, best trade from AlertLog as proof point, CTA, curiosity title | ai_client, human_touch, MoviePy, gspread | ✅ v2 May 2026 |
| `generate_reel_morning.py` | Morning reel (7:00 AM) — day/country aware | ai_client, human_touch, MoviePy | ✅ (not yet v2 — next to upgrade) |
| `generate_analysis.py` | 8-slide market analysis (Part 1). v2: slide 1 = hook slide (no intro), slide 3 = live trades table from AlertLog, CTA slide, curiosity title with real Nifty level | ai_client, human_touch, MoviePy, gspread | ✅ v2 May 2026 |
| `generate_education.py` | Educational deep-dive video (Part 2) | ai_client, human_touch, content_calendar | ✅ Phase 2 |
| `generate_articles.py` | 4 SEO articles daily → Jekyll _posts | ai_client, human_touch, Google Indexing | ✅ Phase 2 |

### Upload & Distribution

| File | Role | Status |
|------|------|--------|
| `upload_youtube.py` | Uploads reel; saves `youtube_video_id` + `public_video_url` to meta | ✅ |
| `upload_youtube_english.py` | Uploads to English channel (separate credentials) | 🔄 Phase 3 |
| `upload_facebook.py` | Uploads reel to FB Page; shares to Group; posts articles | ✅ (Group broken) |
| `upload_instagram.py` | Instagram API chain built; falls back to manual artifact | 📲 Manual |

### Static Assets

| Path | Contents |
|------|----------|
| `public/image/` | `zeno_happy.png`, `zeno_sad.png`, `zeno_greed.png`, `zeno_thinking.png` |
| `public/music/` | `bgmusic1.mp3`, `bgmusic2.mp3`, `bgmusic3.mp3` — rotated by weekday |

---

## 9. AI Fallback Chain

**Never call AI APIs directly. Always use `ai_client.py`.**

```
Groq — llama-3.3-70b-versatile        (Primary — fastest, free)
    ↓ fails
Google Gemini — gemini-2.0-flash       (Secondary — best for image/video roadmap)
    ↓ fails
Anthropic Claude — claude-haiku-4-5-20251001  (Tertiary — best human-touch writing)
    ↓ fails
OpenAI — gpt-4o-mini                   (Quaternary — reliable fallback)
    ↓ all fail
Pre-generated templates in human_touch.py     (Always works — zero downtime)
```

### Mandatory Import Pattern (ALL generators — no exceptions)

```python
from ai_client import ai, img_client
from human_touch import ht, seo

# Text generation
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang="hi")

# JSON generation (structured data)
data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")

# Humanize raw AI output — ALWAYS do this
clean = ht.humanize(raw_output, lang="hi")

# Get rotating hook (first line of every video)
hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")

# Get SEO tags
tags = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")

# Get TTS speed variation (anti-AI detection)
speed = ht.get_tts_speed()
```

---

## 10. Thumbnail Rules (CRITICAL — CTR is the #1 Growth Factor)

Every thumbnail must follow these rules. Long videos currently get 10–13 views. Thumbnails are the reason.

### AI360Trading Shorts Thumbnails
- ZENO face showing emotion: `zeno_happy.png` / `zeno_sad.png` / `zeno_greed.png` / `zeno_thinking.png`
- Choose emotion based on content: profit → happy, loss/crash → sad, greed/FOMO → greed, analysis → thinking
- ONE big bold number or question: `"₹47,000 profit?"` or `"Nifty crash coming?"`
- Font minimum 60px — must be readable on phone screen at thumbnail size
- High contrast: dark background + bright yellow/white text
- Text must be visible without reading the video title

### HerooQuest Kids Thumbnails
- Heroo character large, showing emotion (NOT small "H" logo)
- Story title in big text: `"Tortoise & Hare Race!"` NOT `"Scene 3"`
- Bright colourful background — kids content needs bright colours, NOT dark purple
- Face + emotion + action = clicks

### Title Rules (for all content)
- Always include a number: `"3 signals"`, `"₹47,000"`, `"22,000 level"`
- Always include curiosity: `"Buy or Sell?"`, `"AI says this..."`, `"What happens next?"`
- Bad: `"Weekend Wisdom — ZENO Ki Baat #05"`
- Good: `"Nifty Next Week — 3 Signals That Matter | ZENO Ki Baat"`
- Bad: `"Nifty 22,000 par: 2026-03-28 Update"`
- Good: `"Nifty at 22,000 — Buy or Sell? AI says this..."`

### Hook Rules (first 5 seconds — MOST CRITICAL)
- Start with the most shocking/curious thing — a number, a prediction, a question
- Cut ALL intro animations, logo reveals, jingles — completely remove from start
- Hook examples: `"Aaj Nifty ₹2,400 gira — kya ye sirf shuruat hai?"` or `"3 stocks jo next week 8% de sakte hain"`
- Never start with: channel name, "Namaste doston", music-only intro, logo animation

### CTA Rules (end of every video — ✅ Implemented in all generators v2)
- All 3 generators call `ht.get_cta(lang="hi")` — injected into every script prompt
- ZENO reel: ends with explicit like+subscribe in `audio_script`
- Shorts: `cta` var injected into both `generate_short2_script` and `generate_short3_script` prompts
- Analysis: CTA slide (slide 8) explicitly asks like+subscribe+Telegram+dashboard
- **Verify**: `ht.get_cta()` method must exist in `human_touch.py` — check if missing

---

## 11. Live Trade Data in Videos (✅ Implemented May 2026)

### What Was Implemented
All 3 generators now pull real trade data from AlertLog via gspread and embed it in thumbnails + scripts. Every video shows real Entry/Target/SL/P&L% — no made-up numbers.

### Per-Generator Implementation

**`generate_shorts.py`** — `fetch_live_trades()`:
- Reads AlertLog, filters TRADED + WAITING, sorts TRADED first then by abs(P&L%)
- Returns top 5 trades
- Short 2 thumbnail: real trade card with Entry/Target/SL/P&L/RR
- Short 2 hook_display auto-set: `"{symbol}: +4.2% P&L Today!"`
- Short 3 thumbnail: traded/waiting count teaser badge

**`generate_reel.py`** — `fetch_best_trade()`:
- Returns single best TRADED trade (highest P&L%)
- ZENO thumbnail: `"● LIVE: {symbol} +4.2% TODAY"` red badge
- Script prompt includes real trade as ZENO's proof point

**`generate_analysis.py`** — `fetch_open_trades()`:
- Returns top 6 trades (TRADED + WAITING combined)
- Slide 3 = dedicated live trades table — symbol/entry/target/SL/P&L for all
- Description: traded/waiting count + dashboard link

### AlertLog Columns Used (0-based)
```
B=1 Symbol   H=7 Initial SL   I=8 Target   K=10 Status
L=11 Entry   O=14 Trailing SL  P=15 P/L%   E=4 Trade Type
```

### Required Environment Variables
| Var | Purpose | Fallback |
|-----|---------|---------|
| `GCP_SERVICE_ACCOUNT_JSON` | gspread auth | Returns `[]` gracefully — video still generates |
| `GOOGLE_SHEET_ID` | Opens sheet by key | Falls back to `client.open("ai360trading")` by name |

### Graceful Fallback Rule
All `fetch_*` functions are wrapped in `try/except`. If Sheets unavailable, generators continue without trade data — they never crash the video pipeline.

---

## 12. Trading Bot Architecture

### Overview

| Component | File | Role |
|-----------|------|------|
| AppScript v14.0 | Google Sheets bound script | Scans Nifty200, applies filters, writes WAITING candidates to AlertLog, stores memory in BotMemory sheet |
| Python Bot v13.4 | `trading_bot.py` | Monitors AlertLog every 5 min, manages WAITING→TRADED transition, TSL updates, exit logic, Telegram alerts |

**Status:** Paper trading. Followers take manual entry based on Telegram alerts. Dhan API planned for Phase 4.

### Google Sheets Structure

| Sheet | Purpose |
|-------|---------|
| `Nifty200` | Live data for all 200 stocks — CMP, DMAs, FII data, signals, scores (35 cols A–AI) |
| `AlertLog` | Active + waiting trades — 15 rows, 19 cols. T2=YES/NO automation switch |
| `BotMemory` | Persistent key-value memory store (cols A–E: Key, Value, UpdatedAt, Symbol, KeyType) |
| `History` | Closed trade log — 18 cols A–R |

> ⚠️ **Memory migration note:** Memory previously stored in AlertLog T4 cell as comma-separated string. Fully migrated to `BotMemory` sheet in v14.0. Any code referencing T4 cell for memory is legacy — do not use.

### AlertLog Column Map (0-based)

```
A=0  Signal Time     B=1  Symbol         C=2  Live Price      D=3  Priority Score
E=4  Trade Type      F=5  Strategy       G=6  Breakout Stage  H=7  Initial SL
I=8  Target          J=9  RR Ratio       K=10 Trade Status    L=11 Entry Price
M=12 Entry Time      N=13 Days in Trade  O=14 Trailing SL     P=15 P/L%
Q=16 ATH Warning     R=17 Risk ₹         S=18 Position Size   T=19 SYSTEM CONTROL
```

T2 = automation on/off switch (YES to enable)

### Nifty200 Column Map (0-based)

```
r[0]  NSE_SYMBOL         r[1]  SECTOR
r[2]  CMP                r[3]  %Change(D)
r[4]  20_DMA             r[5]  50_DMA
r[6]  200_DMA            r[7]  SMA_Structure(H)
r[8]  52W_Low            r[9]  52W_High(J)
r[10] %up_52W_Low        r[11] %down_52W_High
r[12] %dist_20DMA(M)     r[13] Avg_Volume_20D
r[14] Volume_vs_Avg%(O)  r[15] FII_Buy_Zone(P)
r[16] FII_Rating(Q)      r[17] Leader_Type(R)
r[18] Signal_Score(S)    r[19] FINAL_ACTION(T)
r[20] RS(U)              r[21] Sector_Trend(V)
r[22] Breakout_Stage(W)  r[23] Retest%(X)
r[24] Trade_Type(Y)      r[25] Priority_Score(Z)
r[26] Pivot_Resistance(AA) r[27] VCP_Status(AB)
r[28] ATR14(AC)          r[29] Days_Since_Low(AD)
r[30] 52W_Breakout_Score(AE) r[31] Sector_Rotation_Score(AF)
r[32] FII_Buying_Signal(AG)  r[33] Master_Score(AH)
r[34] Sector_Rank(AI)    ← RANK formula only, not read by code
```

### AppScript v14.0 — Key Logic

**Market Regime:** Nifty50 CMP vs 20DMA → Bullish or Bearish → controls which gate applies.

**Bearish gate (ALL 5 required):**
- Leader_Type = "Sector Leader"
- AF ≥ 5
- Master_Score ≥ 22
- FII signal ≠ "FII CAUTION"
- FII signal ≠ "FII SELLING"
- Signal must be: RETEST BUY, STRONG BUY, or BASE PREPARED

**10 scan gates (in order):**
1. FII SELLING → skip always
2. Market regime filter (bullish vs bearish path)
3. Late entry block (BREAKOUT CONFIRMED needs RS≥7)
4. Price validity (CMP>0, ATR>0, CMP≤₹5000)
5. Extension filter — retest% < -3% → skip; others: >8% above 20DMA → skip
6. Pivot resistance buffer (within 2% below pivot → skip) — RETEST BUY exempt
7. Volume filter (bullish only) — base/correction: vol<60% → skip; others: vol<120% → skip
8. ATH buffer (within 3% of 52W high → skip)
9. Trade type (AVOID/NO TRADE → skip)
10. Sector concentration (max 2 per sector across traded + waiting combined)

**Capital tiers:**
- ₹13,000 — MasterScore≥28 AND AF≥10 (high conviction)
- ₹10,000 — MasterScore≥22 OR Accumulation Zone (medium conviction)
- ₹7,000 — standard
- Max deployed: ₹45,000 across all trades

**RR minimum:** 1.8 (below this → skip)

**ATR multipliers:**

| Type | SL mult | Target mult |
|------|---------|------------|
| Intraday / Options | 1.5× ATR | 2.0× ATR |
| Swing (default) | 2.0× ATR | 3.0× ATR |
| Positional | 2.5× ATR | 4.0× ATR |

> Positional SL anchored to 20DMA (or 50DMA for Value trades) if DMA is closer than raw ATR SL.

**Conviction bonus table:**

| Condition | Bonus |
|-----------|-------|
| VCP < 0.04 | +3 |
| VCP < 0.07 | +1 |
| Accumulation Zone | +2 |
| Momentum Zone | +1 |
| Days since low > 30 | +2 |
| Days since low > 20 | +1 |
| Strong Bull SMA | +1 |
| Near Breakout / Building Momentum / Correction Base stage | +1 |
| BREAKOUT CONFIRMED + RS < 7 | -3 |
| AF ≥ 10 | +2 |
| AF ≥ 6 | +1 |
| Bearish market + day gain > 0 | +1 |
| FII BUYING signal | +2 |
| STRONG FII signal | +1 |

**Trade modes (stored as `_MODE` in BotMemory):**
- `VCP` — VCP_Status < 0.04 + pre-breakout stage
- `MOM` — Strong Bull SMA + RS≥6
- `STD` — everything else (default in bear market)

**Sort order:** finalScore DESC, then ATR% ASC as tiebreaker within ±2 score points.

**Intraday window:** 09:15–12:30 only.

**BotMemory sheet (cols A–E: Key, Value, UpdatedAt, Symbol, KeyType):**

KeyType values:
- `FLAG` — date-stamped, purged after 14 days
- `TRADE` — per-symbol data
- `STATE` — batch scan state

Memory keys written by AppScript (KeyType=TRADE):
- `{sym}_CAP` — capital tier (7000/10000/13000)
- `{sym}_MODE` — trade mode (VCP/MOM/STD)
- `{sym}_SEC` — sector name

Memory keys written by trading_bot.py (KeyType=TRADE):
- `{sym}_TSL` — current trailing SL price
- `{sym}_MAX` — highest price seen since entry
- `{sym}_ATR` — ATR at entry
- `{sym}_EXDT` — exit date (for 5-day cooldown)

Batch state keys (KeyType=STATE):
- `_BATCH_START` — next row index (60 rows per 5-min run)
- `_BATCH_CANDS` — accumulated candidates (JSON, URL-encoded)

### Python Bot v13.4 — TSL Parameters (mode-aware)

```python
TSL_PARAMS = {
    "VCP": { "breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0 },
    "MOM": { "breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0 },
    "STD": { "breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0 },
}
```

> v13.3 change: STD trail widened 6→10, atr_mult 1.5→2.5. Lets swing trades run longer.

**TSL progression (STD):**
- Gain < 2% → hold initial SL
- Gain 2–4% → move to breakeven
- Gain 4–10% → lock at entry +2%
- Gain > 10% → ATR trail (2.5× ATR below CMP)
- Gain > 8% gap-up → lock 50% of gap

**Hard exit rules:**
- Loss > 5% → immediate hard exit
- Min hold: 2 days swing, 3 days positional (prevents TSL whipsaw on day 1)
- 5 trading day cooldown after exit before same stock re-enters

**Daily message schedule:**
- 08:45–09:15 → Good Morning (open trades P/L + waiting count + sector context)
- 09:15–15:30 → Market hours (entry alerts, TSL updates, exit alerts)
- 12:28–12:38 → Mid-day pulse
- 15:15–15:45 → Market close summary

**Telegram channels:**

| Channel | Secret | Audience | Content |
|---------|--------|----------|---------|
| Basic (free) | `TELEGRAM_CHAT_ID` | Free followers | Market mood, closed signal result only |
| Advance | `CHAT_ID_ADVANCE` | ₹499/month | Full entry/exit, TSL updates, mid-day, CE flag |
| Premium | `CHAT_ID_PREMIUM` | Bundle | Everything in Advance + full options advisory block |

### History Sheet Columns (A–R)

```
A Symbol      B Entry Date   C Entry Price  D Exit Date
E Exit Price  F P/L%         G Result       H Strategy
I Exit Reason J Trade Type   K Initial SL   L TSL at Exit
M Max Price   N ATR at Entry O Days Held    P Capital ₹
Q Profit/Loss ₹              R Options Note
```

### CE Candidate Flag (Advance + Premium entry alerts)

Fires when market is bullish AND stock ATR% > 1.5%:
```
ATR% < 1.5%    → no flag (premium decay risk)
ATR% 1.5–2.5%  → normal mover: target +65%, SL -40% on premium
ATR% > 2.5%    → fast mover: target +50%, SL -35% on premium
```
> Currently uses estimated ATR from target/SL spread, not actual ATR14 from sheet col AC. Real ATR14 integration planned for Phase 4.

---

## 13. Known Bugs & Fixes (CRITICAL — Check Before Editing trading_bot.py)

### Bug 1 — Telegram Channel Variables SWAPPED ⚠️ CRITICAL

```python
# WRONG (current code):
CHAT_ADVANCE = os.environ.get('CHAT_ID_PREMIUM')   # reads wrong secret
CHAT_PREMIUM = os.environ.get('CHAT_ID_ADVANCE')   # reads wrong secret

# FIX (change to):
CHAT_ADVANCE = os.environ.get('CHAT_ID_ADVANCE')
CHAT_PREMIUM = os.environ.get('CHAT_ID_PREMIUM')
```

After fixing: Premium channel needs a dedicated options advisory block (separate from CE flag in Advance). Premium gets: CE strike price recommendation, entry trigger, target % on premium, SL % on premium, suggested lot sizing note.

### Bug 2 — Telegram Token Name Mismatch ✅ Fixed May 2026

`trading_bot.py` previously read `os.environ.get('TELEGRAM_TOKEN')` but the GitHub Secret is named `TELEGRAM_BOT_TOKEN`. Fixed by owner — now reads `TELEGRAM_BOT_TOKEN` correctly. All Telegram sends confirmed working.

### Bug 3 — Facebook Group Posting ❌ Broken

Code in `upload_facebook.py` supports group posting — the bug is in the token, not the code.

Root causes (check in order):
1. `META_ACCESS_TOKEN` missing `publish_to_groups` permission scope (most likely)
2. Bot account not Admin of the group (must be Admin, not just member)
3. Group Settings → Advanced → "Allow content from apps" is OFF
4. App not approved for Groups API by Meta

Fix steps:
1. Graph API Explorer → add `publish_to_groups` permission → Generate Access Token
2. Extend to long-lived token (60 days)
3. Update `META_ACCESS_TOKEN` in GitHub Secrets
4. Verify Amit Kumar account is Admin of ai360trading group

### Bug 4 — HerooQuest Kids Facebook Upload ✅ Fixed May 2026

Was failing with Error 200 (permission denied) — workflow used main `META_ACCESS_TOKEN` instead of kids token. Fixed by creating `META_ACCESS_TOKEN_KIDS` as a Page Access Token (never expires, no refresh needed).

---

## 14. Critical Upload Chain (Order Matters)

Scripts must run in this exact order — each feeds data to the next.

### Evening ZENO Reel (8:30 PM)
```
generate_reel.py
    → output/reel_YYYYMMDD.mp4
    → output/meta_YYYYMMDD.json  (public_video_url = "" at this point)

upload_youtube.py
    → uploads reel
    → writes youtube_video_id, youtube_video_url, public_video_url to meta

upload_facebook.py
    → uploads reel to Facebook Page
    → overwrites meta → public_video_url (Facebook watch URL)
    → posts articles from RSS to Page + Group

upload_instagram.py
    → reads public_video_url from meta
    → attempts Instagram API → polls until FINISHED → publishes
    → on failure: saves caption to output/instagram_caption.txt for manual posting
```

### Morning Reel (7:00 AM)
```
generate_reel_morning.py → output/morning_reel_YYYYMMDD.mp4
upload_youtube.py (morning mode) → upload_facebook.py (morning mode)
```

### Daily Videos (7:30 AM)
```
generate_analysis.py
    → output/analysis_video.mp4
    → output/analysis_video_id.txt  (Part 1 ID for Part 2 linking)

generate_education.py
    → reads analysis_video_id.txt → links Part 1 in description
    → output/education_video.mp4
    → updates Part 1 YouTube description with Part 2 URL
```

---

## 15. Environment Variables & GitHub Secrets

All stored in GitHub Actions Secrets. Never hardcode any value. All confirmed as of May 2026.

### Telegram

| Secret | Purpose | Status |
|--------|---------|--------|
| `TELEGRAM_BOT_TOKEN` | Bot authentication token | ✅ Confirmed name |
| `TELEGRAM_CHAT_ID` | Free channel (@ai360trading) | ✅ |
| `CHAT_ID_ADVANCE` | Advance signals (₹499/month) | ✅ |
| `CHAT_ID_PREMIUM` | Premium signals (bundle) | ✅ |

### Social — Main Channel (AI360Trading)

| Secret | Purpose | Status |
|--------|---------|--------|
| `META_ACCESS_TOKEN` | Facebook Page token (AI360Trading) | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` | Facebook App ID | ✅ |
| `META_APP_SECRET` | Facebook App Secret | ✅ |
| `FACEBOOK_PAGE_ID` | Main trading Facebook Page ID | ✅ |
| `FACEBOOK_GROUP_ID` | Trading Facebook Group ID | ✅ (posting broken — Bug 3) |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business numeric ID | ✅ |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON (Hindi trading channel) | ✅ |

> ⚠️ Page rename in progress: "Unofficial Amit Kumar" → "AI360 Algo Trading". Facebook review up to 7 days. Same Page ID, same token — nothing changes in system.

### Social — Kids Channel (HerooQuest)

| Secret | Purpose | Status |
|--------|---------|--------|
| `FACEBOOK_KIDS_PAGE_ID` | HerooQuest Kids Facebook Page ID | ✅ |
| `META_ACCESS_TOKEN_KIDS` | HerooQuest Page Token — never expires | ✅ Fixed May 2026 |
| `YOUTUBE_CREDENTIALS_KIDS` | YouTube OAuth JSON (Kids channel) | ✅ |

### AI Providers

| Secret | Priority | Model | Status |
|--------|----------|-------|--------|
| `GROQ_API_KEY` | Primary | llama-3.3-70b-versatile | ✅ |
| `GEMINI_API_KEY` | Secondary | gemini-2.0-flash | ✅ |
| `ANTHROPIC_API_KEY` | Tertiary | claude-haiku-4-5-20251001 | ✅ |
| `OPENAI_API_KEY` | Quaternary | gpt-4o-mini | ✅ |
| `HF_TOKEN` | Image gen | Hugging Face | ✅ |
| `STABILITY_API_KEY` | Image gen | Stability AI | ✅ |

### YouTube Playlists

| Secret | Playlist |
|--------|---------|
| `PLAYLIST_NIFTY_ANALYSIS` | Nifty analysis videos |
| `PLAYLIST_SWING_TRADE` | Swing trade videos |
| `PLAYLIST_WEEKLY_OUTLOOK` | Weekly outlook videos |
| `PLAYLIST_ZENO_WISDOM` | ZENO reel series |

### Affiliate Links

| Secret | Market |
|--------|--------|
| `AFFILIATE_INSURANCE_IN` | India |
| `AFFILIATE_INSURANCE_UK` | UK |
| `AFFILIATE_INSURANCE_US` | USA |

### Dhan Trading API (Phase 4 — not connected yet)

| Secret | Status |
|--------|--------|
| `DHAN_API_KEY` | ✅ Added — not connected |
| `DHAN_API_SECRET` | ✅ Added — not connected |
| `DHAN_CLIENT_ID` | ✅ Added — not connected |
| `DHAN_PIN` | ✅ Added — not connected |
| `DHAN_TOTP_KEY` | ✅ Added — not connected |

### Google / GitHub

| Secret | Purpose |
|--------|---------|
| `GCP_SERVICE_ACCOUNT_JSON` | Google Sheets (gspread) + Search Console Indexing API |
| `GH_TOKEN` | GitHub API — used by token_refresh.py to update secrets |

---

## 16. Human Touch System (Anti-AI-Penalty Layer)

**Never use raw AI output. Always pass through `human_touch.py`.**

| Technique | Method | What It Does |
|-----------|--------|-------------|
| 50+ rotating hooks | `ht.get_hook(mode, lang)` | No two videos start the same |
| Personal phrases | `ht.get_personal_phrase(lang)` | "Maine dekha hai..." injected naturally |
| TTS speed variation | `ht.get_tts_speed()` | 0.95–1.05× range — passed to edge_tts rate param |
| Humanize output | `ht.humanize(text, lang)` | Strips robotic patterns, varies connectors |
| Emoji rotation | `ht.get_emoji_set()` | Day-seeded — different emoji set each day |
| SEO tags | `seo.get_video_tags(mode, lang)` | India + Global tags combined |
| Banned phrase removal | Internal to humanize() | "Certainly!", "It's important to note" stripped |

### TTS Speed Pattern

```python
tts_speed = ht.get_tts_speed()              # returns float 0.95–1.05
rate_pct  = int((tts_speed - 1.0) * 100)
rate_str  = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
await edge_tts.Communicate(text, VOICE, rate=rate_str).save(path)
```

---

## 17. Technical Standards

### The Full Code Rule
> Always provide the complete content of any modified file. Partial snippets, diffs, or "add this here" instructions are prohibited. The owner's family cannot apply partial changes.

### Voice Assignments

| Voice ID | Gender | Used For |
|----------|--------|---------|
| `hi-IN-MadhurNeural` | Male | Short 2 — authoritative trade setups |
| `hi-IN-SwaraNeural` | Female | Short 3, ZENO Reel, Morning Reel, Analysis, Education |
| `en-US-JennyNeural` | Female | English channel — all English content |
| `en-US-GuyNeural` | Male | English Short 2 alternative |

### Video Formats

| Content | Ratio | Platform |
|---------|-------|---------|
| Analysis + Education | 16:9 | YouTube |
| All Shorts, Morning Reel, ZENO Reel | 9:16 | YouTube Shorts / Reels / Instagram |

### Dependency Pins

| Package | Version | Reason |
|---------|---------|--------|
| `Pillow` | `>=10.3.0` | Required for LANCZOS resampling |
| `imageio` | `==2.9.0` | Prevents MoviePy rendering crashes |
| `moviepy` | `==1.0.3` | Force reinstall — newer versions break audio |
| `yfinance` | Latest | Use `fast_info['last_price']` only — not `.history()` |
| `PyNaCl` | Latest | Required for GitHub Secret encryption in token_refresh.py |
| `google-generativeai` | Latest | Gemini fallback |
| `anthropic` | Latest | Claude fallback |
| `openai` | Latest | OpenAI fallback |
| `gspread` | Latest | Google Sheets access |
| `oauth2client` | Latest | GCP service account auth for gspread |
| `pytz` | Latest | IST timezone handling |

### SEO Tags Strategy

Every video via `seo.get_video_tags()`:
- India: `Nifty50`, `TradingIndia`, `StockMarketIndia`, `BankNifty`
- Global: `USStocks`, `UKInvesting`, `BrazilMarket`, `UAEInvesting`, `GlobalInvesting`
- Universal: `Finance`, `Investing`, `FinancialLiteracy`, `Shorts`

---

## 18. Website

| Property | Value |
|----------|-------|
| URL | ai360trading.in |
| Hosting | GitHub Pages (Jekyll, `master` branch `_posts/`) |
| Publishing | Auto-commit by `daily-articles.yml` |
| SEO Indexing | Instant via `GCP_SERVICE_ACCOUNT_JSON` |
| Revenue | Google AdSense (USA/UK English readers = highest CPM) |
| Content pillars | Stock Market, Bitcoin/Crypto, Personal Finance, AI Trading |
| Market coverage | India (Nifty50, BankNifty), USA (S&P500, NASDAQ), UK (FTSE100), Brazil (IBOVESPA), Crypto |
| MAX_POSTS | 60 articles retained in `_posts/` — older auto-deleted |

---

## 19. Disney 3D Reel Roadmap

| Phase | Tool | Quality | Status |
|-------|------|---------|--------|
| 1 (Now) | PIL + MoviePy + ZENO PNG | 2D animated slides | ✅ Active |
| 2 | Gemini Veo API (free tier) | AI video clips | Hooks in ai_client.py |
| 3 | Stable Diffusion + AnimateDiff | 3D style frames | Planned |
| 4 | Google Veo 2 / Sora (when free) | True Disney-style 3D | Planned |

> `img_client` in `ai_client.py` is the upgrade hook — Phase 2 generation swaps in with zero changes to generators.

---

## 20. Full Data Flow Diagram

```
MARKET HOURS (Mon–Fri, 9:15 AM–3:30 PM IST)
└── trading_bot.yml (every 5 min)
    └── trading_bot.py v13.4
        ├── get_sheets() → AlertLog + History + Nifty200
        ├── get_market_regime() → Nifty CMP vs 20DMA
        ├── Step A: WAITING→TRADED (entry alert → all 3 channels)
        ├── Step B: Monitor TRADED (TSL updates → Advance+Premium)
        ├── Exit logic (TSL / target / hard loss → History append)
        └── BotMemory sheet updated each run

AppScript v14.0 (Google Sheets bound)
└── Nifty200 scan (60 rows/run, batched)
    ├── 10-gate filter → bullish or bearish path
    ├── Conviction bonus + capital tier + trade mode
    ├── ATR% tiebreaker sort
    ├── Write WAITING to AlertLog
    └── Write _CAP, _MODE, _SEC to BotMemory

7:00 AM daily
└── daily-morning-reel.yml
    └── generate_reel_morning.py → upload_youtube → upload_facebook

7:30 AM / 9:30 AM daily
└── daily-videos.yml
    ├── generate_analysis.py → Part 1 → YouTube
    └── generate_education.py → Part 2 → YouTube

10:00 AM / 11:30 AM daily
└── daily-articles.yml
    └── generate_articles.py → 4 articles → GitHub Pages → Facebook

11:30 AM / 1:30 PM daily
└── daily-shorts.yml
    └── generate_shorts.py → Short 2 + Short 3 → YouTube

8:30 PM daily
└── daily_reel.yml
    └── generate_reel.py → ZENO reel
        → upload_youtube → upload_facebook → upload_instagram (manual fallback)
```

---

## 21. Channel Analytics & Growth Context

**AI360Trading (Main Channel) — as of May 2026:**
- 53 subscribers (+4 in 28 days)
- 3,700 views/month (flat — not growing)
- Watch time: 2.4 hours — DOWN 31% (critical problem)
- Top Short: 416 views (ZENO Wisdom) — proof of concept that formula works
- Long videos: 10–13 views — thumbnails and hooks are failing

**HerooQuest (Kids Channel):**
- 1 subscriber
- 162 views/28 days
- CTR: 0.6% — extremely low (thumbnail problem)

**Key Insight:** ZENO Wisdom Short at 416 views with zero promotion proves the content works. Replicate that exact formula (thumbnail + hook + topic) for every Short. The problem is not the content — it is the packaging (thumbnails, hooks, CTAs).

---

## 22. Broker Partner Links

- [Zerodha](https://bit.ly/2VK6k5F)
- [Dhan](https://invite.dhan.co/?invite=MSIVC45309)

---

## 23. Phase Roadmap

### Phase 1 ✅ Infrastructure (Complete)
- Jekyll site live at ai360trading.in
- GitHub Actions automation (all workflows)
- ai_client.py fallback chain
- human_touch.py anti-AI-penalty system
- trading_bot.py paper trading + Telegram alerts
- META token auto-refresh

### Phase 2 ✅ Content Upgrade (Complete)
- All generators upgraded (ai_client + human_touch)
- generate_articles.py — 4 articles/day with live prices, Google Trends
- generate_analysis.py + generate_education.py — full video pipeline
- generate_reel_morning.py — 7 AM morning reel
- Trading bot v13.4 — CE flag, mode-aware TSL, capital tiers

### Phase 3 🔄 English Channel + Global Scale (In Progress)
- [x] ~~Fix Telegram token name~~ ✅ Fixed May 2026
- [x] ~~Add hooks in first 5 seconds to all generators~~ ✅ All generators v2
- [x] ~~Upgrade thumbnails (emotion + number + contrast)~~ ✅ All generators v2
- [x] ~~Add CTA at end of every video~~ ✅ `ht.get_cta()` in all generators v2
- [x] ~~Add `fetch_live_trades()` to all generators~~ ✅ All generators v2
- [ ] **Fix Telegram channel variable swap (Bug 1 — CRITICAL)** — `trading_bot.py`
- [ ] Fix Facebook Group posting (token scope — Bug 3)
- [ ] Verify `ht.get_cta()` exists in `human_touch.py`
- [ ] Add `GOOGLE_SHEET_ID` to GitHub Secrets
- [ ] Short 4 English — same workflow as Short 2/3
- [ ] YouTube English channel auto-upload (`upload_youtube_english.py`)
- [ ] Instagram fully automated (after Facebook Group fix)

### Phase 4 📋 Live Trading + Premium Options (Planned)
- Dhan API integration for live trade execution
- Premium channel real options advisory (after channel swap fix)
- Real ATR14 from Nifty200 sheet for CE flag
- Backtest validation before going live
- BotMemory sheet fully migrated and stable

---

## 24. Contact & Legal

- **Admin:** admin@ai360trading.in
- **Location:** Haridwar, Uttarakhand, India
- **Legal:** All content educational only. Not SEBI registered.
- **Disclaimer:** ai360trading.in/disclaimer/
