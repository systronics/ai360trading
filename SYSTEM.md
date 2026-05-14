# AI360Trading — Master System Documentation

**Last Updated:** May 14, 2026 — AppScript v15.4 | Bot v14.0 | Base Entry + Options System
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
| Phase 2 | Content Upgrade | ✅ Complete | All generators use ai_client + human_touch; trading bot v14.0 |
| Phase 3 | English Channel + Global Scale | 🔄 Building | English Shorts + YouTube English upload + Instagram auto |
| Phase 4 | Live Trading + Premium Options | 📋 Planned | Dhan API, real options advisory, 30+ paper trades first |

---

## 3. Priority Fix Order

### ✅ FIXED (May 2026 — this session)

| Item | Fixed | Notes |
|------|-------|-------|
| Telegram CHAT_ID swap (Advance/Premium reversed) | ✅ v14.0 | Fixed in trading_bot.py |
| AppScript Gate 5 blocking all stocks (RETEST_MAX_PULLBACK=-0.03) | ✅ v15.2 | Changed to -0.08 |
| AppScript RR check failing all leaders (ATR_TGT_SWING_LEADER=3.5) | ✅ v15.2 | Changed to 4.0 |
| India VIX not fetching from sheet | ✅ v15.3 | Live Yahoo Finance fetch |
| Options signal system | ✅ v15.3 | Premium only, VIX+expiry+strike |
| Base entry system | ✅ v15.4 | Gate 11, non-F&O equity, F&O BASE CE |
| generate_analysis.py SEOTags TypeError | ✅ | human_touch.py v2.1 — deploy from outputs |
| YouTube tags 480 char limit | ✅ | get_youtube_safe_tags() in human_touch.py v2.1 |
| Facebook page token #200 error | ✅ | get_page_token() in upload_facebook.py v2.1 |
| generate_shorts.py Facebook fix | ✅ | get_fb_page_token() added |
| head.html Schema fix + dateModified | ✅ | Deployed |
| robots.txt pagination rule | ✅ | Deployed |
| HerooQuest Kids Facebook upload | ✅ | META_ACCESS_TOKEN_KIDS page token |
| Kids daily yml cron + STABILITY_API_KEY | ✅ | v2.1 deployed |

### 🔴 CRITICAL — Fix Now

| # | Issue | File | Impact |
|---|-------|------|--------|
| 1 | trading_bot.py v14.0 not pushed to GitHub yet | `trading_bot.py` | v13.5 running on server — missing 7 fixes |
| 2 | human_touch.py v2.1 not pushed | `human_touch.py` | generate_analysis.py still failing |

### 🟡 IMPORTANT — This Week

| # | Issue | File | Impact |
|---|-------|------|--------|
| 3 | HerooQuest YouTube thumbnail 403 | studio.youtube.com | No custom thumbnails — verify phone |
| 4 | Facebook Group posting broken (token scope) | `upload_facebook.py` | Missing group distribution |
| 5 | Short 4 English not yet live | `generate_shorts.py` | Missing USA/UK audience — highest CPM gap |

### 🟢 MEDIUM TERM — Next Month

| # | Issue | File | Impact |
|---|-------|------|--------|
| 6 | HerooQuest thumbnails CTR 0.6% — too dark | Kids generator | Very low CTR |
| 7 | Pinned comment on every video → Telegram growth | Post-upload step | Membership funnel |
| 8 | Instagram fully automated | `upload_instagram.py` | Currently manual |
| 9 | Test v15.4 base entry (needs bullish market) | AppScript | Market currently bearish |

---

## 4. Platform Status

| Platform | Status | Notes |
|----------|--------|-------|
| YouTube Hindi | ✅ Auto | Analysis + Education + Shorts + Reels |
| YouTube Shorts (Hindi) | ✅ Auto | Short 2 (Madhur) + Short 3 (Swara) — 400+ views |
| YouTube English | 🔄 Phase 3 | English channel automation TBD |
| YouTube Kids (HerooQuest) | ✅ Working | Upload working, thumbnails need phone verify |
| YouTube Reels (ZENO 8:30 PM) | ✅ Auto | Working |
| YouTube Morning Reel (7 AM) | ✅ Auto | Working |
| Facebook Page (AI360Trading) | ✅ Auto | Posts, reels, article shares — page token fixed |
| Facebook Page (HerooQuest Kids) | ✅ Auto | Fixed May 2026 |
| Facebook Group (ai360trading) | ❌ Broken | Token missing `publish_to_groups` scope |
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
| 6 | Short 4 English (9:16) | 11:30 AM | YouTube English Shorts | 🔄 Phase 3 |
| 7 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 8 | ZENO Reel (9:16) | 8:30 PM | YouTube + Facebook | ✅ |
| 9 | HerooQuest Kids Video | 4:30 PM weekdays / 10 AM weekends | YouTube Kids + Facebook | ✅ |
| 10 | Instagram | Manual | Instagram | 📲 Artifact download |

---

## 6. Content Mode System

Mode is auto-detected by `indian_holidays.py` at workflow start → written to `$GITHUB_ENV`.

| Mode | When | Content Strategy |
|------|------|-----------------|
| `market` | Mon–Fri (excluding Indian holidays) | Live Nifty50/Global data, trade setups, signals |
| `weekend` | Saturday–Sunday | Educational, wealth-building, global audience focus |
| `holiday` | Indian Market Holidays | Motivational, "Market band hai par seekhna chalu" |

---

## 7. GitHub Actions Workflows

| File | Trigger (IST) | Purpose |
|------|--------------|---------|
| `trading_bot.yml` | Every 5 min (08:15–16:29 Mon–Fri) + 08:45, 12:58, 15:58 | Signal monitor + TSL + Telegram alerts |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Analysis + Education videos |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning reel + ZENO reel |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages |
| `kids-daily.yml` | 4:30 PM weekdays / 10:00 AM weekends | HerooQuest video → YouTube + Facebook |
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

| File | Role | Status |
|------|------|--------|
| `trading_bot.py` | Signal monitor + TSL + Telegram alerts | ✅ v14.0 (local), v13.5 (GitHub) |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Swara) + FB page token fix | ✅ v2.1 |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ✅ v2 |
| `generate_reel_morning.py` | Morning reel (7:00 AM) | ✅ |
| `generate_analysis.py` | 14-slide market analysis | ✅ v2.1 (needs human_touch v2.1) |
| `generate_education.py` | Education deep-dive video | ✅ v2.1 |
| `generate_articles.py` | 4 SEO articles daily | ✅ v2.1 |
| `generate_kids_video.py` | HerooQuest story video | ✅ |

### Upload & Distribution

| File | Role | Status |
|------|------|--------|
| `upload_youtube.py` | Standard YouTube upload | ✅ |
| `upload_kids_youtube.py` | HerooQuest YouTube upload + thumbnail search | ✅ v2.1 |
| `upload_facebook.py` | FB Page upload — get_page_token() fixes #200 error | ✅ v2.1 |
| `upload_instagram.py` | Instagram API chain | 📲 Manual fallback |

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

### AI360Trading Thumbnails
- ZENO face showing emotion: `zeno_happy.png` / `zeno_sad.png` / `zeno_greed.png` / `zeno_thinking.png`
- ONE big bold number or question: `"₹47,000 profit?"` or `"Nifty crash coming?"`
- Font minimum 60px — readable on phone at thumbnail size
- High contrast: dark background + bright yellow/white text

### HerooQuest Kids Thumbnails
- Heroo character large, showing emotion (NOT small "H" logo)
- Story title in big text — bright colourful background
- 403 error: verify channel at studio.youtube.com → Settings → Feature eligibility → phone verify (one time)

### Title Rules
- Always include a number: `"3 signals"`, `"₹47,000"`, `"22,000 level"`
- Always include curiosity: `"Buy or Sell?"`, `"AI says this..."`
- Bad: `"Weekend Wisdom — ZENO Ki Baat #05"`
- Good: `"Nifty Next Week — 3 Signals That Matter | ZENO Ki Baat"`

### Hook Rules (first 5 seconds)
- Start with most shocking/curious thing — number, prediction, question
- Cut ALL intro animations, logo reveals, jingles
- Never start with: channel name, "Namaste doston", music-only intro

### CTA Rules
- All generators call `ht.get_cta(lang="hi")` — injected in every script
- Analysis: CTA slide explicitly asks like+subscribe+Telegram+dashboard

---

## 11. Trading System Architecture (v15.4)

### Overview

| Component | Version | Role |
|-----------|---------|------|
| AppScript v15.4 | Google Sheets bound | Scans 200+ stocks, 11-gate filter, writes WAITING, sends options signals |
| Python Bot v14.0 | trading_bot.py | Monitors AlertLog every 5 min, TSL, entry/exit alerts |

**Status:** Paper trading. Dhan API planned for Phase 4 after 30+ paper trades.

### Two Entry Types (v15.4)

#### 1. Breakout Entry
- Stage: BREAKOUT ALERT or BREAKOUT CONFIRMED
- SL = 2×ATR | Target = 4×ATR | RR ≈ 2.0
- Options: BUY CE if F&O liquid + VIX<18 + 20+ days expiry
- Market: both bullish and bearish (leaders only in bearish)

#### 2. Base Entry (NEW v15.4)
- Stage: Correction Base / Building Momentum / Near Breakout
- ALL 5 conditions required (Gate 11):
  1. FII = "Accumulation Zone" (smart money buying)
  2. VCP < 0.05 (tight base — spring loading)
  3. DaysLow ≥ 15 (mature base — at least 3 weeks)
  4. SMA = "Strong Bull" or "Bull" (trend intact)
  5. Stock > 5% below ATH (room to run)
- SL = 1.5×ATR | Target = 5×ATR | RR ≈ 3.3
- Market: bullish only (base entries blocked in bearish)

**Key insight for base entry:**
```
Non-F&O stock in base:
  → Equity only (no options) — PERFECT
  → Full move captured: entry ₹380 → target ₹450 = +18%
  → No premium decay, no bid-ask loss, no liquidity risk

F&O stock in base:
  → Equity + BASE CE (stricter: VIX<16, 40+ days, ATM only)
  → Options add leverage but equity is primary

F&O stock in breakout:
  → Equity + BUY CE (standard: VIX<18, 20+ days, ATM or OTM)
```

### AppScript v15.4 — 11 Gates

| Gate | Rule | Breakout | Base |
|------|------|----------|------|
| 1 | FII ≠ SELLING | Required | Required |
| 2 | Market Regime | Bearish→Leaders only | Bullish only |
| 3 | Late Entry RS≥5 | Applied | N/A |
| 4 | Price validity | Required | Required |
| 4b | Result/Event day >6% | Required | Required |
| 5 | Retest ≥ -8% | Applied | EXEMPT |
| 6 | Pivot resistance buffer | Applied | EXEMPT |
| 7 | Volume filter | >120% | Relaxed 40% |
| 8 | ATH buffer >1% | Applied | EXEMPT |
| 9 | Trade type not AVOID | Required | Required |
| 10 | Sector concentration ≤2 | Required | Required |
| 11 | Base quality (v15.4) | N/A | FII+VCP+Days+SMA+ATH gap |

### CONFIG Values (AppScript v15.4)

```javascript
MAX_TRADES              : 8
MAX_WAITING             : 10
MIN_PRIORITY            : 15
MIN_RR                  : 1.8

ATR_SL_INTRADAY         : 1.5
ATR_SL_SWING            : 2.0
ATR_SL_BASE             : 1.5   // v15.4 new
ATR_SL_POSITIONAL       : 2.5
ATR_TGT_INTRADAY        : 2.0
ATR_TGT_SWING           : 3.0
ATR_TGT_SWING_LEADER    : 4.0   // v15.2 fix (was 3.5)
ATR_TGT_BASE            : 5.0   // v15.4 new
ATR_TGT_POSITIONAL      : 4.0

RETEST_MAX_PULLBACK     : -0.08  // v15.2 fix (was -0.03)
BEARISH_LEADER_ONLY     : true
BEARISH_MIN_AF          : 5
BEARISH_MIN_MASTER      : 22

BASE_MAX_VCP            : 0.05
BASE_MIN_DAYS_LOW       : 15
BASE_MIN_ATH_GAP_PCT    : 5.0
BASE_MIN_SCORE          : 18

CAPITAL_HIGH            : 13000  // score≥28 + AF≥10
CAPITAL_MED             : 10000  // score≥22 or FII Accum.
CAPITAL_STD             :  7000
MAX_DEPLOYED            : 104000
```

### Options Signal System (v15.3+)

#### Breakout CE (📊 BUY CE)
- Stage: BREAKOUT ALERT or BREAKOUT CONFIRMED only
- VIX < 18 → buy | 18-22 → caution | >22 → skip
- F&O liquid stocks only (80+ stocks list in code)
- Expiry: 20+ days minimum
- Strike: ATM or ATM+1×ATR
- Channel: Premium only

#### Base CE (📦 BASE CE)
- Stage: Correction Base / Building Momentum / Near Breakout
- VIX < 16 (stricter — trade takes 2-4 weeks)
- F&O liquid stocks only
- Expiry: 40+ days minimum (always next month+)
- Strike: ATM only (need delta, not leverage)
- Channel: Premium only

#### Options Column Map (AlertLog U-X)
| Col | Header | Values |
|-----|--------|--------|
| U (20) | Options Signal | 📊 BUY CE / 📦 BASE CE / ⏸ SKIP / ❌ VIX HIGH |
| V (21) | Strike | e.g. "400 CE Jun" |
| W (22) | Expiry | e.g. "25-Jun-2026" |
| X (23) | Theta Risk | 🟢 LOW / 🟡 MED / 🔴 HIGH |

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
T4 = Python bot state (TSL/MAX/LP/ATR/EXDT per stock)
```

### Nifty200 Column Map (0-based)

```
r[0]  NSE_SYMBOL       r[1]  SECTOR          r[2]  CMP
r[3]  %Change          r[4]  20_DMA          r[5]  50_DMA
r[6]  200_DMA          r[7]  SMA_Structure   r[8]  52W_Low
r[9]  52W_High         r[10] %up_52W_Low     r[11] %down_52W_High
r[12] %dist_20DMA      r[13] Avg_Volume_20D  r[14] Volume_vs_Avg%
r[15] FII_Buy_Zone     r[16] FII_Rating      r[17] Leader_Type
r[18] Signal_Score     r[19] FINAL_ACTION    r[20] RS
r[21] Sector_Trend     r[22] Breakout_Stage  r[23] Retest%
r[24] Trade_Type       r[25] Priority_Score  r[26] Pivot_Resistance
r[27] VCP_Status       r[28] ATR14           r[29] Days_Since_Low
r[30] 52W_Breakout_Score r[31] Sector_Rotation_Score
r[32] FII_Buying_Signal  r[33] Master_Score  r[34] Sector_Rank
```

### Python Bot v14.0 — Key Details

**10 fixes vs v13.5:**
1. CHAT_ID swap fixed (Advance/Premium were reversed)
2. Advance=full details, Premium=details+CE flag
3. BotMemory sheet read (_CAP/_MODE/_SEC/_RANK)
4. Result day skip (>6% gap → skip entry)
5. NSE holiday check in Python
6. MAX_TRADES=8 matching AppScript
7. Capital 3-tier fallback from BotMemory
8. Mid-day pulse 12:28-12:38
9. Market close summary 15:15-15:45
10. CE flag gated by rank≤5

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
TSL_GAP_LOCK_FRAC = 0.5
MIN_HOLD_SWING    = 2    # days
MIN_HOLD_POS      = 3    # days
HARD_LOSS_PCT     = 5.0
```

### Telegram Channels

| Channel | Secret | Audience | Content |
|---------|--------|----------|---------|
| Basic | `CHAT_ID_BASIC` | Free | Market mood, signal result only |
| Advance ₹699/mo | `CHAT_ID_ADVANCE` | Paid | Full entry/exit, TSL, mid-day pulse |
| Premium ₹1,499/mo | `CHAT_ID_PREMIUM` | Paid | Advance + Options signals (📊📦) |

### History Sheet Columns (A–R)

```
A Symbol      B Entry Date   C Entry Price  D Exit Date
E Exit Price  F P/L%         G Result       H Strategy
I Exit Reason J Trade Type   K Initial SL   L TSL at Exit
M Max Price   N ATR at Entry O Days Held    P Capital ₹
Q Profit/Loss ₹              R Options Note
```

---

## 12. Live Trade Data in Videos (Implemented)

All 3 generators pull real trade data from AlertLog via gspread and embed in thumbnails + scripts.

```
generate_shorts.py  → fetch_live_trades() → top 5 trades → Short 2 thumbnail card
generate_reel.py    → fetch_best_trade()  → best TRADED → ZENO red badge
generate_analysis.py → fetch_open_trades() → slide 3 = live trades table
```

**AlertLog columns used:** B=1 Symbol, H=7 SL, I=8 Target, K=10 Status, L=11 Entry, P=15 P/L%

**Fallback:** All fetch_* wrapped in try/except — video still generates if Sheets unavailable.

---

## 13. Known Bugs & Status

### Bug 1 — Bot v14.0 Not on GitHub ⚠️ CRITICAL
```
Local: v14.0 (all 10 fixes done)
GitHub: v13.5 (old version running on server)
Fix: git add trading_bot.py && git commit -m "v14.0" && git push
```

### Bug 2 — human_touch.py v2.1 Not Pushed
```
generate_analysis.py fails: SEOTags.get_video_tags() unexpected arg 'channel'
Fix: deploy human_touch.py v2.1 from outputs folder
```

### Bug 3 — Facebook Group Posting ❌ Broken
```
Code in upload_facebook.py supports groups — bug is in token scope.
Root causes (check in order):
1. META_ACCESS_TOKEN missing publish_to_groups permission
2. Bot account not Admin of group
3. Group Settings → Advanced → "Allow content from apps" OFF
Fix: Graph API Explorer → add publish_to_groups → regenerate token
```

### Bug 4 — HerooQuest YouTube Thumbnails 403
```
"doesn't have permissions to upload custom thumbnails"
Fix (one time, 5 minutes):
  studio.youtube.com → HerooQuest channel
  Settings → Channel → Feature eligibility → Verify → phone SMS
```

---

## 14. Critical Upload Chain (Order Matters)

### Evening ZENO Reel (8:30 PM)
```
generate_reel.py → output/reel_YYYYMMDD.mp4 + meta_YYYYMMDD.json
upload_youtube.py → writes youtube_video_id + public_video_url to meta
upload_facebook.py → uploads reel, posts articles to Page + Group
upload_instagram.py → reads public_video_url → API or manual fallback
```

### Daily Videos (7:30 AM)
```
generate_analysis.py → output/analysis_video.mp4 + analysis_video_id.txt
generate_education.py → reads analysis_video_id.txt → links Part 1 in description
```

### HerooQuest Kids
```
generate_kids_video.py → output/kids_video_*.mp4 + kids_short_*.mp4 + kids_meta_*.json
upload_kids_youtube.py → uploads both + thumbnail (after channel verify)
upload_facebook.py --meta-prefix kids → uploads reel to HerooQuest FB Page
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

### Social — HerooQuest Kids
| Secret | Purpose | Status |
|--------|---------|--------|
| `FACEBOOK_KIDS_PAGE_ID` | HerooQuest FB Page | ✅ |
| `META_ACCESS_TOKEN_KIDS` | HerooQuest page token | ✅ |
| `YOUTUBE_CREDENTIALS_KIDS` | YouTube OAuth (Kids) | ✅ |

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
| YouTube safe tags | `seo.get_youtube_safe_tags()` | 480 char limit, ASCII only |
| Article tags | `seo.format_article_tags()` | Jekyll frontmatter format |

---

## 17. Technical Standards

### The Full Code Rule
> Always provide complete file content. Partial snippets, diffs, or "add this here" are prohibited. The owner's family cannot apply partial changes.

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
| `Pillow` | >=10.3.0 | Required for LANCZOS resampling |
| `imageio` | ==2.9.0 | Prevents MoviePy rendering crashes |
| `moviepy` | ==1.0.3 | Force reinstall — newer versions break audio |
| `yfinance` | Latest | Use `fast_info['last_price']` only — not `.history()` |

### SEO Tags Strategy
Every video via `seo.get_video_tags()`:
- India: `Nifty50`, `TradingIndia`, `StockMarketIndia`, `BankNifty`
- Global: `USStocks`, `UKInvesting`, `BrazilMarket`, `UAEInvesting`
- Universal: `Finance`, `Investing`, `FinancialLiteracy`, `Shorts`

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
| 1 (Now) | PIL + MoviePy + ZENO PNG | 2D animated slides | ✅ Active |
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

AppScript v15.4 (Google Sheets bound, every 5 min trigger)
└── Nifty200 scan (60 rows/run, batched)
    ├── 11-gate filter → bullish or bearish path
    │   ├── Breakout entries: Gates 1-10
    │   └── Base entries: Gates 1-4b + 7 relaxed + Gate 11
    ├── Conviction bonus + capital tier + trade mode
    ├── Options signal: _generateOptionsSignal()
    │   ├── F&O liquid check → VIX check → expiry → strike
    │   └── Non-F&O → ⏸ SKIP (equity only for base)
    ├── Write WAITING to AlertLog (19 cols)
    ├── Write options to cols U-X
    ├── Send regime alert once/day → Advance+Premium
    └── Send options alert → Premium only

Content (daily automated):
7:00 AM → generate_reel_morning.py → YouTube + Facebook
7:30 AM → generate_analysis.py + generate_education.py → YouTube
10:00 AM → generate_articles.py → GitHub Pages + Facebook
11:30 AM → generate_shorts.py → YouTube Shorts
4:30 PM → generate_kids_video.py → HerooQuest YouTube + Facebook
8:30 PM → generate_reel.py (ZENO) → YouTube + Facebook
```

---

## 22. Channel Analytics & Growth Context

**AI360Trading (Main — as of May 2026):**
- 53 subscribers (+4 in 28 days)
- 3,700 views/month (flat)
- Watch time: 2.4 hours — DOWN 31% (critical)
- Top Short: 416 views (ZENO Wisdom) — formula works, replicate it
- Long videos: 10–13 views — thumbnail and hook problem

**HerooQuest (Kids — as of May 2026):**
- 1 subscriber, 162 views/28 days
- CTR: 0.6% — extremely low (thumbnail problem)

**Key Insight:** ZENO Wisdom at 416 views with zero promotion proves content works. Problem is packaging (thumbnail + hook), not content.

---

## 23. Phase Roadmap

### Phase 1 ✅ Infrastructure (Complete)
- Jekyll site, GitHub Actions, ai_client, human_touch, paper trading bot, META token auto-refresh

### Phase 2 ✅ Content Upgrade (Complete)
- All generators v2 with hooks, thumbnails, CTA, live trade data
- Trading bot v13.4 → v14.0 (all bugs fixed)
- AppScript v14.0 → v15.4 (base entry + options system)

### Phase 3 🔄 English Channel + Global Scale
- [x] Fix Telegram token name ✅
- [x] Hooks in all generators ✅
- [x] Thumbnails upgraded ✅
- [x] CTA in all generators ✅
- [x] Live trade data in all generators ✅
- [x] Options signal system ✅ (v15.3)
- [x] Base entry system ✅ (v15.4)
- [ ] Push trading_bot.py v14.0 to GitHub
- [ ] Push human_touch.py v2.1 to GitHub
- [ ] Short 4 English — same workflow as Short 2/3
- [ ] YouTube English channel auto-upload
- [ ] Instagram fully automated
- [ ] HerooQuest thumbnail CTR fix

### Phase 4 📋 Live Trading (After 30+ Paper Trades)
- Dhan API integration for live execution
- Real options advisory (after 30 paper trades validate win rate)
- Real ATR14 from Nifty200 col AC confirmed working
- BotMemory fully stable
- Win rate > 55% required before going live

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
