# AI360Trading — Master System Documentation

**Last Updated:** May 15, 2026 — AppScript v15.5 | Bot v14.0 | Education Course + ZENO v3.0 + HerooQuest v2.0
**Repo:** https://github.com/systronics/ai360trading
**Website:** https://ai360trading.in
**Owner:** Amit Kumar, Haridwar, Uttarakhand, India

---

## ⚠️ EVERY AI MUST READ THIS SECTION COMPLETELY BEFORE TOUCHING ANYTHING

This system is the **sole livelihood** of Amit Kumar's family. Amit has serious health issues and is in debt. His family is non-technical and cannot fix anything if it breaks. The system must run **forever, fully automatically, with zero human intervention.** This is not a hobby project — it is a family survival project.

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
3. Check Section 13 for known bugs before starting
4. After your task, update Section 13 and this header's Last Updated date

---

## 1. Mission & Monetisation

> Build a fully automated passive income system that runs forever on ₹0/month infrastructure, generating income across every possible digital monetisation stream simultaneously. This is Amit's family's survival — it must work.

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

### CPM Target Countries (priority order)
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
| Phase 2 | Content Upgrade | ✅ Complete | All generators upgraded; trading bot v14.0 |
| Phase 3 | English Channel + Global Scale | 🔄 Building | Education course live, dual-lang shorts live, HerooQuest v2.0 live |
| Phase 4 | Live Trading + Premium Options | 📋 Planned | Dhan API, 30+ paper trades first |

---

## 3. Priority Fix Order

### ✅ FIXED (May 2026)

| Item | Fixed | Notes |
|------|-------|-------|
| Telegram CHAT_ID swap (Advance/Premium reversed) | ✅ v14.0 | Fixed in trading_bot.py |
| AppScript Gate 5 blocking all stocks | ✅ v15.2 | RETEST_MAX_PULLBACK -0.03 → -0.08 |
| AppScript RR check failing all leaders | ✅ v15.2 | ATR_TGT_SWING_LEADER 3.5 → 4.0 |
| India VIX not fetching | ✅ v15.3 | Live Yahoo Finance fetch in AppScript |
| Options signal system | ✅ v15.3 | Premium only, VIX+expiry+strike |
| Base entry system | ✅ v15.4 | Gate 11, non-F&O equity, F&O BASE CE |
| AppScript T4 BotMemory spill (col T rows 3+) | ✅ v15.5 | _cleanSystemControlColumn() added |
| generate_analysis.py SEOTags TypeError | ✅ | Fixed build_video_meta() — returns 5 values |
| YouTube tags 480 char limit | ✅ | ASCII filter in generate_shorts.py v3.0 |
| Facebook page token #200 error | ✅ | get_page_token() in upload_facebook.py |
| generate_shorts.py Facebook fix | ✅ v3.0 | get_fb_page_token() added (Hindi only) |
| head.html Schema + dateModified | ✅ | Deployed |
| robots.txt pagination rule | ✅ | Deployed |
| HerooQuest Kids Facebook upload | ✅ | META_ACCESS_TOKEN_KIDS page token |
| generate_education.py replaces generate_analysis.py | ✅ May 15 | 52-week course, dual language |
| generate_shorts.py v3.0 | ✅ May 15 | AlertLog connected, ZENO auto, dual lang, FB fix |
| generate_kids_video.py v2.0 | ✅ May 15 | 3 outputs, heroo.png, dual lang |
| daily-videos.yml | ✅ May 15 | Runs education (not analysis), Hindi + English |
| daily-shorts.yml | ✅ May 15 | Dual language, AlertLog mode |
| kids-daily.yml | ✅ May 15 | Hindi + English split jobs, 3 output types |
| heroo.png | ✅ May 15 | Uploaded to public/image/heroo.png |

### 🔴 CRITICAL — Fix Now

| # | Issue | File | Impact |
|---|-------|------|--------|
| 1 | human_touch.py v2.1 not pushed | `human_touch.py` | Some generators may fail SEO tag calls |

### 🟡 IMPORTANT — This Week

| # | Issue | File | Impact |
|---|-------|------|--------|
| 2 | HerooQuest YouTube thumbnail 403 | studio.youtube.com | No custom thumbnails — verify phone |
| 3 | Facebook Group posting broken (token scope) | `upload_facebook.py` | Missing group distribution |
| 4 | English YouTube channel credentials | `YOUTUBE_CREDENTIALS_EN` secret | English shorts upload fails gracefully but no upload |

### 🟢 MEDIUM TERM — Next Month

| # | Issue | File | Impact |
|---|-------|------|--------|
| 5 | HerooQuest thumbnails CTR 0.6% — too dark | Kids generator | Very low CTR |
| 6 | Pinned comment on every video → Telegram growth | Post-upload step | Membership funnel |
| 7 | Instagram fully automated | `upload_instagram.py` | Currently manual |
| 8 | Test v15.4 base entry (needs bullish market) | AppScript | Market currently bearish |

---

## 4. Platform Status

| Platform | Status | Notes |
|----------|--------|-------|
| YouTube Hindi | ✅ Auto | Education + Shorts + Reels |
| YouTube Shorts (Hindi) | ✅ Auto | AlertLog top stock, ZENO auto-emotion |
| YouTube Shorts (English) | 🔄 Phase 3 | Code ready — needs YOUTUBE_CREDENTIALS_EN secret |
| YouTube English (long) | 🔄 Phase 3 | Code ready — needs YOUTUBE_CREDENTIALS_EN secret |
| YouTube Kids Hindi (HerooQuest) | ✅ Auto | Full story + Cliffhanger + Did You Know |
| YouTube Kids English (HerooQuest) | 🔄 Phase 3 | Code ready — needs YOUTUBE_CREDENTIALS_KIDS_EN secret |
| YouTube Reels (ZENO 8:30 PM) | ✅ Auto | Working |
| YouTube Morning Reel (7 AM) | ✅ Auto | Working |
| Facebook Page (AI360Trading) | ✅ Auto | Shorts + reels + articles — page token fixed |
| Facebook Page (HerooQuest Kids) | ✅ Auto | Fixed May 2026 |
| Facebook Group (ai360trading) | ❌ Broken | Token missing `publish_to_groups` scope |
| Instagram | 📲 Manual | Download artifact → post manually |
| GitHub Pages (ai360trading.in) | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram (3 channels) | ✅ Auto | Paper trading signals |

---

## 5. Content Output Schedule (Daily, Fully Automated)

| # | Content | Generator | Time (IST) | Platform | Status |
|---|---------|-----------|-----------|----------|--------|
| 1 | Morning Reel (9:16) | generate_reel_morning.py | 7:00 AM | YouTube + Facebook | ✅ |
| 2 | Education Video Hindi (16:9, ~9 min) | generate_education.py | 7:30 AM weekday / 9:30 AM weekend | YouTube Hindi | ✅ |
| 3 | Education Video English (16:9) | generate_education.py | 7:30 AM (same workflow) | YouTube English | 🔄 Phase 3 |
| 4 | Stock Short Hindi (9:16, 45-60s) | generate_shorts.py | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts + Facebook | ✅ |
| 5 | Stock Short English (9:16) | generate_shorts.py | 11:30 AM (same workflow) | YouTube English Shorts | 🔄 Phase 3 |
| 6 | 4 SEO Articles | generate_articles.py | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 7 | ZENO Reel (9:16) | generate_reel.py | 8:30 PM | YouTube + Facebook | ✅ |
| 8 | HerooQuest Full Story Hindi | generate_kids_video.py | 8:00 AM | YouTube Kids | ✅ |
| 9 | HerooQuest Cliffhanger Short Hindi | generate_kids_video.py | 8:00 AM | YouTube Kids | ✅ |
| 10 | HerooQuest Did You Know Short Hindi | generate_kids_video.py | 8:00 AM | YouTube Kids | ✅ |
| 11 | HerooQuest Full Story English | generate_kids_video.py | 8:00 AM | YouTube Kids EN | 🔄 Phase 3 |
| 12 | Instagram | Manual | — | Instagram | 📲 Artifact download |

**Total: 10 pieces/day automated (Hindi) + 2 English Phase 3 pending**

### Content Strategy Decision (May 15, 2026)

**Why education replaces market analysis:**
- Market data videos expire hourly → low views (10-13 views per video)
- Education videos are evergreen → views compound for years
- ZENO Wisdom Short = 416 views proof: content works, packaging was wrong

**Short format (v3.0):**
- Top stock auto-selected from AlertLog by Priority Score
- ZENO emotion auto-matched to stock sentiment + % move
- 0-3s: ZENO + big hook text | 4-40s: WHY + setup | 41-55s: CTA
- Facebook share runs after Hindi upload only (page token fixed)

**HerooQuest format (v2.0):**
- Full story: 5-8 min adventure + moral lesson
- Cliffhanger short: DIFFERENT script — 45s teaser driving to full video
- Did You Know: 30s separate fun fact — pure viral
- Heroo character fills first frame → YouTube auto-thumbnail shows face

---

## 6. Content Mode System

Mode auto-detected by `indian_holidays.py` at workflow start → written to `$GITHUB_ENV`.

| Mode | When | Content Strategy |
|------|------|-----------------|
| `market` | Mon–Fri (excluding Indian holidays) | Top AlertLog stock short, weekly education topic |
| `weekend` | Saturday–Sunday | Base/Near Breakout stock from Nifty200, same education topic |
| `holiday` | Indian Market Holidays | Motivational investing lesson, "Market band hai par seekhna chalu" |

---

## 7. GitHub Actions Workflows

| File | Trigger (IST) | Purpose |
|------|--------------|---------|
| `trading_bot.yml` | Every 5 min (08:15–16:29 Mon–Fri) + 08:45, 12:58, 15:58 | Signal monitor + TSL + Telegram alerts |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Education video Hindi + English |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Stock short Hindi + English |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning reel + ZENO reel |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages |
| `kids-daily.yml` | 8:00 AM daily | HerooQuest: 3 outputs × 2 languages (6 total) |
| `token_refresh.yml` | 1st + 20th of month | Auto META token refresh |
| `keepalive.yml` | Periodic | Prevents GitHub disabling inactive workflows |

---

## 8. Complete File Map

### Core Infrastructure

| File | Role | Status |
|------|------|--------|
| `ai_client.py` | Universal AI — Groq→Gemini→Claude→OpenAI→Templates fallback | ✅ |
| `human_touch.py` | Anti-AI-penalty layer — hooks, phrases, TTS variation, SEO tags | ✅ v2.1 |
| `indian_holidays.py` | Mode detection — NSE API + hardcoded fallback | ✅ |
| `content_calendar.py` | Rotates topics: Options, Technical Analysis, Psychology | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update + Telegram alert | ✅ |

### Content Generators

| File | Role | Version | Status |
|------|------|---------|--------|
| `trading_bot.py` | Signal monitor + TSL + Telegram alerts | v14.0 | ✅ |
| `generate_education.py` | 52-week course, dual language, replaces generate_analysis.py | v1.0 | ✅ May 15 |
| `generate_shorts.py` | AlertLog top stock, ZENO auto-emotion, dual lang, FB share | v3.0 | ✅ May 15 |
| `generate_kids_video.py` | 3 output types, heroo.png, dual lang, cliffhanger + DYK | v2.0 | ✅ May 15 |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | v2 | ✅ |
| `generate_reel_morning.py` | Morning reel (7:00 AM) | v2 | ✅ |
| `generate_articles.py` | 4 SEO articles daily | v2.1 | ✅ |
| `generate_analysis.py` | RETIRED — replaced by generate_education.py | — | ❌ Remove from workflows |

### Upload & Distribution

| File | Role | Status |
|------|------|--------|
| `upload_youtube.py` | Standard YouTube upload | ✅ |
| `upload_kids_youtube.py` | HerooQuest YouTube upload + thumbnail search | ✅ v2.1 |
| `upload_facebook.py` | FB Page upload — get_page_token() fixes #200 error | ✅ v2.1 |
| `upload_instagram.py` | Instagram API chain | 📲 Manual fallback |

### Static Assets

| Path | Contents |
|------|----------|
| `public/image/` | `zeno_happy.png`, `zeno_sad.png`, `zeno_greed.png`, `zeno_thinking.png`, `zeno_fear.png`, `zeno_angry.png`, `zeno_celebrating.png` |
| `public/image/heroo.png` | HerooQuest main character — Pixar-style 3D boy, white cap, rainbow hoodie |

### ZENO Emotions (7 available)

| File | Emotion | Used When |
|------|---------|-----------|
| zeno_happy.png | Happy | Bullish, breakout alert, +2%+ |
| zeno_greed.png | Greed | Breakout confirmed, strong move, +5%+ |
| zeno_thinking.png | Thinking | Near breakout, base building, weekend analysis |
| zeno_sad.png | Sad | Bearish, market down, caution |
| zeno_fear.png | Fear | High VIX, crash, hard stop loss |
| zeno_angry.png | Angry | Missed trade, FOMO warning |
| zeno_celebrating.png | Celebrating | Target hit, big win |

---

## 9. AI Fallback Chain

**Never call AI APIs directly. Always use `ai_client.py`.**

```
Groq — llama-3.3-70b-versatile        (Primary — fastest, free)
    ↓ fails
Google Gemini — gemini-2.0-flash       (Secondary)
    ↓ fails
Anthropic Claude — claude-haiku-4-5-20251001  (Tertiary)
    ↓ fails
OpenAI — gpt-4o-mini                   (Quaternary)
    ↓ all fail
Pre-generated templates in human_touch.py     (Always works)
```

### Mandatory Import Pattern (ALL generators)

```python
from ai_client import ai, img_client
from human_touch import ht, seo

response = ai.generate(prompt, content_mode=CONTENT_MODE, lang="hi")
data     = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
clean    = ht.humanize(raw_output, lang="hi")
hook     = ht.get_hook(mode=CONTENT_MODE, lang="hi")
tags     = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")
speed    = ht.get_tts_speed()
```

---

## 10. Thumbnail & Hook Rules (CRITICAL — CTR is #1 Growth Factor)

### AI360Trading Shorts Thumbnails (v3.0)
- ZENO face auto-selected by emotion (7 options): large, 65% of frame height
- Stock name in huge text (160px+): `"BHEL +4.2%"`
- Hook phrase below (72px): `"BREAKOUT TODAY!"`
- Sentiment-based background: green (bullish), red (bearish), blue (neutral)
- % badge shown if move > 1.5% (green for up, red for down)

### HerooQuest Kids Thumbnails (v2.0)
- Heroo character fills first frame (80% height) — YouTube auto-thumbnail = face ✅
- Story title in big text — bright colourful background
- 403 error fix: studio.youtube.com → Settings → Feature eligibility → Verify phone (one time)

### Title Rules (all content)
- Always include a number: `"3 signals"`, `"₹47,000"`, `"22,000 level"`
- Always include curiosity: `"Buy or Sell?"`, `"AI says this..."`
- Bad: `"Weekend Wisdom — ZENO Ki Baat #05"`
- Good: `"BHEL +4.2% — Breakout Confirmed! | AI360 Trading #Shorts"`

### Hook Rules (first 5 seconds)
- Start with most shocking/curious thing — number, prediction, question
- Cut ALL intro animations, logo reveals, jingles
- Short opens directly on ZENO + big text + stock name

---

## 11. Content Generator Details

### generate_education.py (v1.0 — NEW May 15)

**Replaces:** generate_analysis.py (retired)

**52-week course auto-advances:**
```
COURSE_START = date(2026, 5, 15)  # Week 1 starts here — never change
Week = (today - COURSE_START).days // 7 + 1
Topic auto-selected from COURSE list
```

**Languages:** EDUCATION_LANG=hi → Hindi (Swara) | EDUCATION_LANG=en → English (Jenny)

**Output:** `output/education_video_hi.mp4` + `output/education_video_en.mp4`

**Format:** 14 slides × ~40s = ~9-10 min (mid-roll ad eligible)

### generate_shorts.py (v3.0 — Updated May 15)

**Stock selection:**
- Weekday: AlertLog top stock by Priority Score (WAITING or TRADED, not EXITED)
- Weekend/Holiday: Nifty200 base/near-breakout stocks by Master Score
- Fallback: NIFTY50 if sheets unavailable

**ZENO emotion auto-selection:**
```python
pct > 5%    → greed
pct > 2%    → happy
pct < -5%   → fear
pct < -3%   → sad
stage has BREAKOUT CONFIRMED + pct > 3% → greed
stage has NEAR BREAKOUT → thinking
```

**Facebook share (Hindi only):**
- `get_fb_page_token()` exchanges user token for page token (fixes #200)
- Only runs when LANG=="hi" AND video_id is set
- Posts YouTube Short link + stock setup to Facebook Page

**Languages:** SHORT_LANG=hi → Hindi + Facebook | SHORT_LANG=en → English (no Facebook)

### generate_kids_video.py (v2.0 — Updated May 15)

**3 output types (KIDS_OUTPUT env var):**
```
full      → Full story video (16:9, 5-8 min)
short     → Cliffhanger short (9:16, 45s) — DIFFERENT script from full
didyouknow→ Did You Know? short (9:16, 30s) — separate viral fact
```

**Story series:** 7 series, 52 stories, STORY_START=date(2026,5,15), auto-advances weekly

**Heroo character:**
```python
load_heroo() tries: heroo.png → heroo_happy.png → heroo_character.png
Full video: heroo fills 80% of frame height, centered
If not found: video still generates (warning printed)
```

**Languages:** KIDS_LANG=hi → Swara | KIDS_LANG=en → Jenny

---

## 12. Trading System Architecture (v15.5)

### Overview

| Component | Version | Role |
|-----------|---------|------|
| AppScript v15.5 | Google Sheets bound | Scans 200+ stocks, 11-gate filter, writes WAITING, options signals, cleans T4 |
| Python Bot v14.0 | trading_bot.py | Monitors AlertLog every 5 min, TSL, entry/exit alerts |

**Status:** Paper trading. Dhan API planned for Phase 4 after 30+ paper trades.

### AppScript v15.5 — What Changed vs v15.4

**Bug fixed:** Column T (SYSTEM CONTROL) rows 3+ were being filled with BotMemory data (T4 state string spilling). Fixed by:
- `_cleanSystemControlColumn()` — runs at start of every scan, clears col T rows 3+
- `_restoreFormulas()` — explicitly clears col T for all data rows except row 2

### Two Entry Types (v15.4+)

**Breakout Entry:**
- Stage: BREAKOUT ALERT or BREAKOUT CONFIRMED
- SL = 2×ATR | Target = 4×ATR | RR ≈ 2.0
- Options: BUY CE if F&O liquid + VIX<18 + 20+ days expiry

**Base Entry:**
- Stage: Correction Base / Building Momentum / Near Breakout
- Gate 11 (ALL required): FII=Accumulation + VCP<0.05 + DaysLow≥15 + SMA=Bull + Stock>5% below ATH
- SL = 1.5×ATR | Target = 5×ATR | RR ≈ 3.3
- Bullish market only

**Key insight:**
```
Non-F&O stock in base → Equity only (no options) — PERFECT
  Entry ₹380 → Target ₹450 = +18% captured fully
F&O stock in base → Equity + BASE CE (VIX<16, 40+ days, ATM only)
F&O stock in breakout → Equity + BUY CE (VIX<18, 20+ days, ATM/OTM)
```

### AlertLog Column Map (0-based)

```
A=0  Signal Time     B=1  Symbol         C=2  Live Price
D=3  Priority Score  E=4  Trade Type     F=5  Strategy
G=6  Breakout Stage  H=7  Initial SL     I=8  Target
J=9  RR Ratio        K=10 Trade Status   L=11 Entry Price
M=12 Entry Time      N=13 Days in Trade  O=14 Trailing SL
P=15 P/L%            Q=16 ATH Warning    R=17 Risk ₹
S=18 Position Size   T=19 SYSTEM CONTROL
U=20 Options Signal  V=21 Strike         W=22 Expiry
X=23 Theta Risk

T2 = automation switch (YES/NO)
T4 = Python bot state only (TSL/MAX/LP/ATR/EXDT per stock)
     AppScript v15.5 now protects T4 — clears rows 3+ of col T
```

### Python Bot v14.0

**10 fixes vs v13.5:** CHAT_ID swap, Advance/Premium differentiation, BotMemory sheet read, result day skip, holiday check, MAX_TRADES=8, capital 3-tier, mid-day pulse, market close summary, CE flag by rank.

**T4 cell (Python-only state):**
```
NSE_SYM_TSL_  → Trailing SL ×100
NSE_SYM_MAX_  → Max price seen ×100
NSE_SYM_LP_   → Last price ×100
NSE_SYM_ATR_  → ATR at entry ×100
NSE_SYM_EXDT_ → Exit date (5-day cooldown)
date_AM/PM    → Good morning / market close flags
```

**BotMemory sheet (AppScript writes, Python reads):**
```
{sym}_CAP   → Capital tier (7000/10000/13000)
{sym}_MODE  → Trade mode (VCP/MOM/STD)
{sym}_SEC   → Sector
{sym}_RANK  → Sector rank
{sym}_BASE  → "1" if base entry (v15.4)
```

### TSL Parameters (mode-aware)

```python
TSL_PARAMS = {
  "VCP": { "breakeven":3.0, "lock1":5.0, "trail":8.0,  "atr_mult":2.0, "gap_lock":9.0 },
  "MOM": { "breakeven":2.5, "lock1":4.5, "trail":7.0,  "atr_mult":1.8, "gap_lock":8.0 },
  "STD": { "breakeven":2.0, "lock1":4.0, "trail":10.0, "atr_mult":2.5, "gap_lock":8.0 },
}
HARD_LOSS_PCT = 5.0   MIN_HOLD_SWING = 2   MIN_HOLD_POS = 3
```

### Telegram Channels

| Channel | Secret | Audience | Content |
|---------|--------|----------|---------|
| Basic | `CHAT_ID_BASIC` | Free | Market mood, active count, membership CTA |
| Advance ₹699/mo | `CHAT_ID_ADVANCE` | Paid | Full entry/exit, TSL, mid-day pulse |
| Premium ₹1,499/mo | `CHAT_ID_PREMIUM` | Paid | Advance + Options signals (📊📦) |

---

## 13. Known Bugs & Status

### Bug 1 — human_touch.py v2.1 Not Pushed ⚠️
```
Some generators call seo methods that may not exist in old version.
Fix: Deploy human_touch.py v2.1 — has format_article_tags() and get_youtube_safe_tags()
```

### Bug 2 — HerooQuest YouTube Thumbnails 403
```
"doesn't have permissions to upload custom thumbnails"
Fix (one time, 5 minutes):
  studio.youtube.com → HerooQuest channel
  Settings → Channel → Feature eligibility → Verify → phone SMS
```

### Bug 3 — Facebook Group Posting ❌ Broken
```
Code supports groups — bug is in token scope.
Fix: Graph API Explorer → add publish_to_groups → regenerate token
     → Update META_ACCESS_TOKEN in GitHub Secrets
```

### Bug 4 — English Channel Credentials Missing
```
generate_shorts.py and generate_education.py gracefully skip English upload
if YOUTUBE_CREDENTIALS_EN secret is not set. No crash — just no English upload.
Fix when ready: Add YOUTUBE_CREDENTIALS_EN secret to GitHub.
```

---

## 14. Critical Upload Chain (Order Matters)

### Daily Education Videos (7:30 AM)
```
generate_education.py (LANG=hi) → output/education_video_hi.mp4
generate_education.py (LANG=en) → output/education_video_en.mp4
Both upload directly to respective YouTube channels
```

### Daily Shorts (11:30 AM)
```
generate_shorts.py (LANG=hi)
  → render short → upload to YouTube Hindi
  → share_to_facebook() → Facebook Page post with YouTube link
generate_shorts.py (LANG=en)
  → render short → upload to YouTube English (if credentials set)
  → NO Facebook (English page not set up yet)
```

### HerooQuest Kids (8:00 AM — separate Hindi + English jobs)
```
Hindi job:
  generate_kids_video.py (KIDS_LANG=hi, KIDS_OUTPUT=full)   → YouTube Kids
  generate_kids_video.py (KIDS_LANG=hi, KIDS_OUTPUT=short)  → YouTube Kids
  generate_kids_video.py (KIDS_LANG=hi, KIDS_OUTPUT=didyouknow) → YouTube Kids
English job (needs YOUTUBE_CREDENTIALS_KIDS_EN):
  Same 3 outputs in English
```

### Evening ZENO Reel (8:30 PM)
```
generate_reel.py → output/reel_YYYYMMDD.mp4 + meta
upload_youtube.py → writes youtube_video_id + public_video_url
upload_facebook.py → uploads reel, posts articles
upload_instagram.py → API or manual fallback
```

---

## 15. Environment Variables & GitHub Secrets

### Telegram
| Secret | Purpose |
|--------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot auth token |
| `CHAT_ID_BASIC` | Free channel |
| `CHAT_ID_ADVANCE` | Advance ₹699/mo |
| `CHAT_ID_PREMIUM` | Premium ₹1,499/mo |

### Social — AI360Trading
| Secret | Purpose | Status |
|--------|---------|--------|
| `META_ACCESS_TOKEN` | Facebook Page token | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` / `META_APP_SECRET` | Facebook App | ✅ |
| `FACEBOOK_PAGE_ID` | Main trading page | ✅ |
| `FACEBOOK_GROUP_ID` | Trading group | ✅ (posting broken) |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business ID | ✅ |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth (Hindi) | ✅ |
| `YOUTUBE_CREDENTIALS_EN` | YouTube OAuth (English) | 🔄 Phase 3 — not set yet |

### Social — HerooQuest Kids
| Secret | Purpose | Status |
|--------|---------|--------|
| `FACEBOOK_KIDS_PAGE_ID` | HerooQuest FB Page | ✅ |
| `META_ACCESS_TOKEN_KIDS` | HerooQuest page token | ✅ |
| `YOUTUBE_CREDENTIALS_KIDS` | YouTube OAuth (Kids Hindi) | ✅ |
| `YOUTUBE_CREDENTIALS_KIDS_EN` | YouTube OAuth (Kids English) | 🔄 Phase 3 — not set yet |

### AI Providers
| Secret | Priority | Model |
|--------|----------|-------|
| `GROQ_API_KEY` | Primary | llama-3.3-70b-versatile |
| `GEMINI_API_KEY` | Secondary | gemini-2.0-flash |
| `ANTHROPIC_API_KEY` | Tertiary | claude-haiku-4-5-20251001 |
| `OPENAI_API_KEY` | Quaternary | gpt-4o-mini |
| `HF_TOKEN` | Image gen | Hugging Face |
| `STABILITY_API_KEY` | Image gen | Stability AI |

### Dhan Trading API (Phase 4 — not connected yet)
`DHAN_API_KEY`, `DHAN_API_SECRET`, `DHAN_CLIENT_ID`, `DHAN_PIN`, `DHAN_TOTP_KEY` — all added, not connected.

### Google / GitHub
| Secret | Purpose |
|--------|---------|
| `GCP_SERVICE_ACCOUNT_JSON` | Google Sheets + Search Console Indexing |
| `GH_TOKEN` | GitHub API — used by token_refresh.py |
| `GOOGLE_SHEET_ID` | Sheet ID for fetch_live_trades() |

---

## 16. Human Touch System (Anti-AI-Penalty Layer)

**Never use raw AI output. Always pass through `human_touch.py`.**

| Technique | Method | What It Does |
|-----------|--------|-------------|
| 50+ rotating hooks | `ht.get_hook(mode, lang)` | No two videos start the same |
| Personal phrases | `ht.get_personal_phrase(lang)` | "Maine dekha hai..." injected naturally |
| TTS speed variation | `ht.get_tts_speed()` | 0.95–1.05× range |
| Humanize output | `ht.humanize(text, lang)` | Strips robotic patterns |
| SEO tags | `seo.get_video_tags(mode, lang)` | India + Global tags combined |
| YouTube safe tags | ASCII filter `[t for t in tags if t.isascii()]` | Removes Hindi chars, keeps under 480 chars |

---

## 17. Technical Standards

### The Full Code Rule
> Always provide complete file content. Partial snippets, diffs, or "add this here" are prohibited. The owner's family cannot apply partial changes.

### Voice Assignments
| Voice ID | Gender | Used For |
|----------|--------|---------|
| `hi-IN-SwaraNeural` | Female | Education, Shorts Hindi, Kids Hindi, ZENO, Morning Reel |
| `en-US-JennyNeural` | Female | Education English, Shorts English, Kids English |
| `hi-IN-MadhurNeural` | Male | Available — not currently in use |
| `en-US-GuyNeural` | Male | Available — not currently in use |

### Video Formats
| Content | Ratio | Platform |
|---------|-------|---------|
| Education Video | 16:9, 1920×1080 | YouTube |
| HerooQuest Full Video | 16:9, 1920×1080 | YouTube Kids |
| All Shorts, Reels | 9:16, 1080×1920 | YouTube Shorts / Reels / Instagram |

### Dependency Pins
| Package | Version | Reason |
|---------|---------|--------|
| `Pillow` | >=10.3.0 | Required for LANCZOS resampling |
| `imageio` | ==2.9.0 | Prevents MoviePy rendering crashes |
| `moviepy` | ==1.0.3 | Force reinstall — newer versions break audio |
| `yfinance` | Latest | Use `fast_info['last_price']` only — not `.history()` |

---

## 18. Website

| Property | Value |
|----------|-------|
| URL | ai360trading.in |
| Hosting | GitHub Pages (Jekyll, `master` branch `_posts/`) |
| Publishing | Auto-commit by `daily-articles.yml` |
| SEO Indexing | Instant via `GCP_SERVICE_ACCOUNT_JSON` |
| Revenue | Google AdSense |
| MAX_POSTS | 60 articles retained — older auto-deleted |
| head.html | Conditional schema (NewsArticle/Article) + dateModified=site.time |
| robots.txt | Single `Disallow: /page` covers all pagination |

---

## 19. Membership

| Plan | Price | Annual |
|------|-------|--------|
| Advance | ₹699/month | ₹5,588/year (save ₹2,800) |
| Premium | ₹1,499/month | ₹11,988/year (save ₹6,000) |

Payment: UPI 9634759528@upi
Activation: WhatsApp 9634759528 with screenshot + Telegram username

**Advance:** Daily signals, TradingView indicator, Chartink screener, private videos
**Premium:** Everything + Options signals (📊📦), live sessions 2×/month, Sheet access, portfolio review

---

## 20. Disney 3D Reel Roadmap

| Phase | Tool | Quality | Status |
|-------|------|---------|--------|
| 1 (Now) | PIL + MoviePy + ZENO PNG + Heroo PNG | 2D animated slides | ✅ Active |
| 2 | Gemini Veo API (free tier) | AI video clips | Hooks in ai_client.py |
| 3 | Stable Diffusion + AnimateDiff | 3D style frames | Planned |
| 4 | Google Veo 2 / Sora (when free) | True Disney-style 3D | Planned |

> `img_client` in `ai_client.py` is the upgrade hook — Phase 2 swaps in with zero changes to generators.

---

## 21. Full Data Flow Diagram

```
MARKET HOURS (Mon–Fri, 9:15 AM–3:30 PM IST)
└── trading_bot.yml (every 5 min)
    └── trading_bot.py v14.0
        ├── get_sheets() → AlertLog + History + Nifty200
        ├── get_market_regime() → Nifty CMP vs 20DMA
        ├── Step A: WAITING→TRADED (entry alert → all 3 channels)
        │   ├── Advance: full entry details
        │   └── Premium: entry + CE options flag
        ├── Step B: Monitor TRADED (TSL updates → Advance+Premium)
        ├── Exit logic (TSL/target/hard loss → History append)
        └── BotMemory sheet updated each run

AppScript v15.5 (Google Sheets bound, every 5 min trigger)
└── Nifty200 scan (60 rows/run, batched)
    ├── _cleanSystemControlColumn() → protects T4, clears col T rows 3+
    ├── 11-gate filter → bullish or bearish path
    │   ├── Breakout entries: Gates 1-10
    │   └── Base entries: Gates 1-4b + 7 relaxed + Gate 11
    ├── Options signal: _generateOptionsSignal()
    │   ├── F&O liquid check → VIX check → expiry → strike
    │   └── Non-F&O → ⏸ SKIP (equity only for base)
    ├── Write WAITING to AlertLog (cols A-S)
    ├── Write options to cols U-X
    ├── Send regime alert once/day → Advance+Premium
    └── Send options alert → Premium only

7:00 AM → generate_reel_morning.py → YouTube + Facebook
7:30 AM → generate_education.py (hi + en) → YouTube
8:00 AM → generate_kids_video.py (3 types × 2 langs = 6 videos) → YouTube Kids
10:00 AM → generate_articles.py → GitHub Pages + Facebook
11:30 AM → generate_shorts.py (hi → YouTube + Facebook | en → YouTube)
8:30 PM → generate_reel.py (ZENO) → YouTube + Facebook
```

---

## 22. Channel Analytics & Growth Context

**AI360Trading (Main — as of May 2026):**
- 53 subscribers (+4 in 28 days)
- 3,700 views/month (flat)
- Watch time: 2.4 hours — DOWN 31% (critical)
- Top Short: 416 views (ZENO Wisdom) — formula works, replicate it
- Long videos: 10–13 views — education course now replaces (evergreen > expiring)

**HerooQuest (Kids — as of May 2026):**
- 1 subscriber, 162 views/28 days
- CTR: 0.6% — extremely low
- Fix deployed: heroo.png in first frame + v2.0 separate scripts

**Key insight:** ZENO Wisdom at 416 views with zero promotion proves content works. Problem was packaging. v3.0 shorts fix: ZENO auto-emotion + AlertLog stock + stock story format.

---

## 23. Phase Roadmap

### Phase 1 ✅ Infrastructure (Complete)
- Jekyll site, GitHub Actions, ai_client, human_touch, paper trading bot, META token auto-refresh

### Phase 2 ✅ Content Upgrade (Complete)
- All generators v2 with hooks, thumbnails, CTA, live trade data
- Trading bot v14.0 (all 10 bugs fixed)
- AppScript v15.5 (base entry + options + T4 fix)

### Phase 3 🔄 English Channel + Global Scale
- [x] Education course replacing market analysis ✅ May 15
- [x] generate_shorts.py v3.0 — AlertLog + ZENO auto ✅ May 15
- [x] generate_kids_video.py v2.0 — dual lang + 3 outputs ✅ May 15
- [x] heroo.png uploaded ✅ May 15
- [x] Options signal system ✅ (v15.3)
- [x] Base entry system ✅ (v15.4)
- [x] All Facebook page token fixes ✅
- [ ] Push human_touch.py v2.1 to GitHub
- [ ] Add YOUTUBE_CREDENTIALS_EN secret (English channel upload)
- [ ] Add YOUTUBE_CREDENTIALS_KIDS_EN secret (HerooQuest English)
- [ ] HerooQuest YouTube thumbnail CTR fix (phone verify)
- [ ] Instagram fully automated

### Phase 4 📋 Live Trading (After 30+ Paper Trades)
- Dhan API integration for live execution
- Real options advisory (win rate > 55% required)
- BotMemory fully stable
- 7 paper trades open as of May 13 — need 23+ more completed trades

---

## 24. Broker Partner Links

- [Zerodha](https://bit.ly/2VK6k5F)
- [Dhan](https://invite.dhan.co/?invite=MSIVC45309)

---

## 25. Contact & Legal

- **Admin:** admin@ai360trading.in
- **Location:** Haridwar, Uttarakhand, India
- **Legal:** All content educational only. Not SEBI registered.
- **Disclaimer:** ai360trading.in/disclaimer/
