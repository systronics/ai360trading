# AI360Trading — Master System Documentation
**Last Updated:** 17 May 2026 — Education v1.1 confirmed working, 17.9 min video, mid-roll ads active
**Repo:** https://github.com/systronics/ai360trading
**Website:** https://ai360trading.in
**Owner:** Amit Kumar, Haridwar, Uttarakhand, India

---

# ████ READ THIS FIRST — EVERY AI MUST FOLLOW THESE RULES ████

## This Is a Family Survival Project
Amit Kumar has serious health issues and is in debt.
6 family members depend on this system for their livelihood.
The system must run forever, fully automatically, with zero human intervention.
Breaking anything = zero income that day. That is not acceptable.

---

## THE MOST IMPORTANT RULE FOR ANY AI

> **NEVER write, suggest, or modify any code without FIRST reading the**
> **current version from GitHub. GitHub master branch is the ONLY source of truth.**
> **Drive files may be outdated. Never use them as reference for code.**

### How Any AI Can Read Any File Instantly

The repo is PUBLIC. Any AI that knows the filename can construct the raw URL:

```
Format:
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/FILENAME

Python files:
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/trading_bot.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/ai_client.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/human_touch.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/generate_education.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/generate_shorts.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/generate_kids_video.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/generate_reel.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/generate_reel_morning.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/generate_articles.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/content_calendar.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/kids_content_calendar.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/indian_holidays.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/token_refresh.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/upload_youtube.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/upload_kids_youtube.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/upload_facebook.py
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/requirements.txt

Workflows:
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/trading_bot.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/daily-videos.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/daily-shorts.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/daily_reel.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/daily-articles.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/kids-daily.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/daily-morning-reel.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/token_refresh.yml
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/.github/workflows/keepalive.yml

SYSTEM.md (always read first):
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/SYSTEM.md
```

### Mandatory Workflow Before Touching Any File

```
Step 1: Construct raw URL from filename above
Step 2: Fetch and read the COMPLETE current file
Step 3: Understand all imports, architecture, dependencies
Step 4: Make ONLY the minimal changes needed
Step 5: Provide the COMPLETE updated file — never partial snippets or diffs
Step 6: Owner pushes to GitHub after confirming
```

### Additional Info Sources

```
AppScript (Google Sheets bound — NOT in GitHub):
  Owner must share AppScript code directly — no URL access possible

Google Sheets (AlertLog, Nifty200, BotMemory, History):
  Sheet ID: 1fPNGL6AHs-7M-oC22zILg9FlyWi-7DF9NoVVqZQs2vk
  Owner must share sheet data — no direct AI access
```

---

## The 10 Absolute Rules

| # | Rule | Why |
|---|------|-----|
| 1 | Read current GitHub file before ANY code change | Architecture changes — always verify |
| 2 | Always provide COMPLETE file content | Family cannot apply partial changes |
| 3 | Cost must stay Rs.0/month forever | Verify free tier before any new service |
| 4 | Never call AI APIs directly | Always use ai_client.py |
| 5 | Never use raw AI output in videos | Always pass through human_touch.py |
| 6 | Never execute real trades | Paper trading only until Phase 4 |
| 7 | Update SYSTEM.md after every change | Only memory across AI sessions |
| 8 | GitHub = source of truth | Drive may be outdated |
| 9 | Thumbnails = large bold text + face/character visible | CTR is #1 for YouTube growth |
| 10 | When in doubt — stop and ask owner | Never break what is working |

---

# SECTION 1 — MISSION

> Build a fully automated passive income system that runs forever on Rs.0/month
> infrastructure, generating income across every digital monetisation stream.

## Income Streams

| Stream | Platform | Target Countries |
|--------|----------|-----------------|
| Video ad revenue | YouTube Hindi | USA, UK, Canada, Australia, UAE |
| Video ad revenue | YouTube English (Phase 3) | USA, UK, Canada, Australia |
| Shorts/Reels bonus | YouTube + Facebook | USA, UK, Brazil, India |
| Website ad revenue | ai360trading.in | USA, UK, Canada |
| In-stream video ads | Facebook Page | USA, UK, Brazil, India |
| Paid subscriptions | Telegram (3 tiers) | India, UAE, Global |
| Kids content ads | YouTube Kids (HerooQuest) | India, USA, UK |

## Target Audience

```
AI360Trading channel:
  Hindi content  → Indian retail traders, NRI investors (India, UAE, Gulf)
  English content → USA, UK, Australia, Canada investors (Phase 3)

HerooQuest Kids channel:
  Hindi → India, UAE (children 4-12 years)
  English → USA, UK, Global (Phase 3)

CPM priority: USA > UK > Australia > UAE > Canada > Brazil > India
India = highest volume, lowest CPM → always include global keywords
USA/UK prime time = 11 PM - 1 AM IST
```

---

# SECTION 2 — COMPLETE FILE STRUCTURE

## Python Files (GitHub root — confirmed 17 May 2026)

| File | Purpose | Version | Status |
|------|---------|---------|--------|
| `ai_client.py` | Universal AI fallback chain | v2.2 | ✅ Live |
| `human_touch.py` | Anti-AI-penalty layer | v2.2 | ✅ Live |
| `content_calendar.py` | 52-week education + day topics | v2.1 | ✅ Live |
| `kids_content_calendar.py` | Kids story topics (SEPARATE file) | — | ✅ Live |
| `indian_holidays.py` | NSE holiday + mode detection | — | ✅ Live |
| `trading_bot.py` | Signal monitor + TSL + 5 filters | v15.0 | ✅ Live |
| `generate_education.py` | 52-week education videos | v1.1 | ✅ Live |
| `generate_shorts.py` | Stock shorts + ZENO + Facebook | v3.0 | ✅ Live |
| `generate_kids_video.py` | HerooQuest full/short/didyouknow | v2.1 | ✅ Live |
| `generate_reel.py` | ZENO evening reel | v2 | ✅ Live |
| `generate_reel_morning.py` | Morning reel | v2 | ✅ Live |
| `generate_articles.py` | 4 SEO articles daily | v2.1 | ✅ Live |
| `token_refresh.py` | Auto META token refresh | — | ✅ Live |
| `upload_youtube.py` | YouTube upload (trading channel) | — | ✅ Live |
| `upload_kids_youtube.py` | YouTube upload (kids channel) | — | ✅ Live |
| `upload_facebook.py` | Facebook page upload | v2.1 | ✅ Live |
| `requirements.txt` | Python dependencies | — | ✅ Live |
| `generate_analysis.py` | ❌ DELETED | — | ❌ Removed |
| `upload_instagram.py` | ❌ DELETED — manual only | — | ❌ Removed |
| `generate_community_post.py` | ❌ DELETED — unused | — | ❌ Removed |

## GitHub Actions Workflows (.github/workflows/)

| File | Schedule (IST) | Purpose |
|------|---------------|---------|
| `trading_bot.yml` | Every 5 min 8:15-16:29 Mon-Fri | Signal monitor + TSL |
| `daily-videos.yml` | 7:30 AM Mon-Fri / 9:30 AM Sat-Sun | Education video Hindi + English |
| `daily-shorts.yml` | 11:30 AM Mon-Fri / 1:30 PM Sat-Sun | Stock short Hindi + English |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning reel + ZENO reel |
| `daily-morning-reel.yml` | 7:00 AM daily | Morning market reel |
| `daily-articles.yml` | 10:00 AM Mon-Fri / 11:30 AM Sat-Sun | 4 SEO articles |
| `kids-daily.yml` | 8:00 AM daily | HerooQuest 3 outputs x 2 languages |
| `token_refresh.yml` | 1st + 20th of month | META token auto-refresh |
| `keepalive.yml` | Periodic | Prevents GitHub disabling workflows |

## Static Assets (public/image/)

| File | Status |
|------|--------|
| `heroo.png` | ✅ Fixed May 16 (was heroo.png.png) |
| `zeno_happy.png` | ✅ |
| `zeno_greed.png` | ✅ |
| `zeno_thinking.png` | ✅ |
| `zeno_sad.png` | ✅ |
| `zeno_fear.png` | ✅ |
| `zeno_angry.png` | ✅ |
| `zeno_celebrating.png` | ✅ |

---

# SECTION 3 — CONTENT SCHEDULE

## Daily Automated Output

| Time IST | Content | Generator | Platform |
|----------|---------|-----------|---------|
| 7:00 AM | Morning reel (9:16) | generate_reel_morning.py | YouTube + Facebook |
| 7:30 AM | Education video Hindi (~17 min) | generate_education.py EDUCATION_LANG=hi | YouTube Hindi |
| 7:30 AM | Education video English (~14 min) | generate_education.py EDUCATION_LANG=en | YouTube English (Phase 3) |
| 8:00 AM | HerooQuest Full Story Hindi | generate_kids_video.py KIDS_OUTPUT=full | YouTube Kids |
| 8:00 AM | HerooQuest Cliffhanger Short | generate_kids_video.py KIDS_OUTPUT=short | YouTube Kids |
| 8:00 AM | HerooQuest Did You Know | generate_kids_video.py KIDS_OUTPUT=didyouknow | YouTube Kids |
| 10:00 AM | 4 SEO articles | generate_articles.py | GitHub Pages + Facebook |
| 11:30 AM | Stock short Hindi (45-60s) | generate_shorts.py SHORT_LANG=hi | YouTube Shorts + Facebook |
| 11:30 AM | Stock short English | generate_shorts.py SHORT_LANG=en | YouTube English (Phase 3) |
| 8:30 PM | ZENO reel (9:16) | generate_reel.py | YouTube + Facebook |

## Content Mode Detection

| CONTENT_MODE | When | Used For |
|-------------|------|---------|
| `market` | Mon-Fri non-holiday | AlertLog stock, market content |
| `weekend` | Sat-Sun | Base stocks, evergreen content |
| `holiday` | NSE holidays | Motivational content |

```
NOTE: CONTENT_MODE env var is sometimes empty in workflows (known issue)
generate_education.py v1.1 auto-detects from weekday when empty — working correctly
Saturday detected as "weekend" automatically ✅
```

---

# SECTION 4 — CONFIRMED PERFORMANCE (17 May 2026)

## Education Video — Fully Working ✅

```
Hindi: youtube.com/watch?v=cvRcZNzLbPw
  Duration: 17.9 min ✅ (was 3.3 min before fix)
  Mid-roll ads: WILL ACTIVATE ✅ (needs 8+ min threshold)
  Title: "Stock Market Kya Hai | Week 1 | AI360 Trading" ✅
  22 slides | 2262 words ✅

English: 14.5 min (not uploaded — YOUTUBE_CREDENTIALS_EN not set)

NOTE: 17.9 min is long — consider reducing MIN_WORDS_SLIDE from 80 to 60
or MIN_STORY_SLIDES from 22 to 16 for sweet spot of ~10 min
Both values are in generate_education.py
```

## Paper Trading Performance (Week 1)

```
3 wins / 0 losses = 100% win rate
  BSE:        Entry Rs.3880 → Rs.4030 | +3.87% | Rs.502 | 1 day
  IDEA:       Entry Rs.12.45 → Rs.13.19 | +5.94% | Rs.773 | 2 days
  ADANIPORTS: Entry Rs.1716 → Rs.1812 | +5.58% | Rs.725 | 2 days
Total realised: Rs.2,001

Open: 8 trades
Need: 27+ more completed trades before Phase 4
```

---

# SECTION 5 — KEY FILE DETAILS

## generate_education.py v1.1

```
Mode detection: auto-detects from weekday if CONTENT_MODE env is empty
  Empty + Saturday = weekend (confirmed working 17 May 2026)
LANG: from EDUCATION_LANG env var (hi or en)

Title format: "Topic | Week N | AI360 Trading"
  clean_edu_title() strips stray percentages

Duration settings:
  MIN_SLIDES = 22
  MIN_WORDS_SLIDE = 80 (produces ~17 min — may want to reduce to 60 for ~10 min)
  expand_slide_content() forces minimum word count
  check_duration() warns if under 8 min threshold

Week auto-advances from content_calendar.get_todays_education_topic()
  COURSE_START = date(2026, 5, 15)
  Week 1 = May 15-21 | Week 2 = May 22-28 | etc.
```

## ai_client.py v2.2

```
Fallback chain:
  Groq (llama-3.3-70b-versatile) → Gemini (gemini-2.0-flash)
  → Claude (claude-haiku-4-5-20251001) → OpenAI (gpt-4o-mini) → Templates

Key methods:
  ai.generate(prompt, content_mode, lang)
  ai.generate_json(prompt, content_mode, lang)
  ai.generate_with_stock_data(prompt, lang, sym, cmp, sl, target)
    — locks stock numbers so AI cannot change them

System prompts by mode:
  "market"    → trader persona
  "education" → teacher persona (NO chart/setup/breakout language)
  "weekend"   → casual educator
  "holiday"   → motivational
```

## human_touch.py v2.2

```
Key functions:
  ht.get_hook(mode, lang, week)
    mode="education" → education hooks (not trading hooks)
    mode="market"    → trading hooks

  ht.get_video_description(mode, lang, week, topic)
  ht.get_cta(lang, mode)
  ht.humanize(text, lang)
  ht.get_tts_speed() → 0.95-1.05x variation

  seo.get_video_tags(mode, is_short, channel, lang)
    mode="education" → education SEO tags
    mode="market"    → trading SEO tags
    channel="kids"   → kids SEO tags

  seo.get_youtube_safe_tags(tags) → ASCII only, max 480 chars

Permanent fixes:
  safe_thumbnail_text(text) → strips Devanagari, keeps Rs. and numbers
  safe_tts_price(val, lang) → "1457 rupaye" not Rs.1457
  get_prompt_rules(lang, sym, cmp, sl, target, mode) → 3 rules in every AI prompt
```

## content_calendar.py v2.1

```
TWO separate functions:

get_todays_topic()
  → day-of-week topics for articles and reels

get_todays_education_topic()
  → 52-week progressive course for education videos
  → week auto-calculated from COURSE_START = date(2026, 5, 15)
  → returns dict WITH "week" key

52-week phases:
  Wk 1-8:   Foundations (demat, NSE/BSE, IPO, dividend, MF, SIP)
  Wk 9-16:  Technical Analysis (charts, candles, EMA, RSI, MACD)
  Wk 17-24: Fundamental Analysis (P/E, ROE, debt, moat, valuation)
  Wk 25-32: Trading Strategies (swing, positional, momentum, TSL)
  Wk 33-40: Options (call/put, Greeks, VIX, expiry, futures)
  Wk 41-48: Risk + Wealth (position sizing, tax, retirement, global)
  Wk 49-52: Advanced (algo, global markets, trading plan, review)
```

## kids_content_calendar.py (SEPARATE from content_calendar.py)

```
Used ONLY by generate_kids_video.py
Import: from kids_content_calendar import get_today_topic
Returns: {hindi_title, english_title, category, ...}
NOT the same as content_calendar.py
```

## generate_kids_video.py v2.1

```
Architecture (DO NOT CHANGE without reading current file):
  Images: Gemini 2.5 Flash → Gemini 2.0 Flash Exp → HuggingFace FLUX.1
          → DALL-E 3 → PIL branded placeholder
  Video: ffmpeg Ken Burns zoom (NOT moviepy)
  Audio: edge-tts

Import: from kids_content_calendar import get_today_topic
        NOT from content_calendar

Characters:
  Heroo: brave 10-yr Indian boy, red-blue superhero suit, golden H emblem
  Arya: cheerful 8-yr Indian girl, orange kurta, star clip braids

KIDS_OUTPUT: full (10 scenes ~7.5 min) | short (35-45s) | didyouknow (20-30s)
KIDS_LANG: hi (Swara) | en (Jenny — Phase 3)
```

## generate_shorts.py v3.0

```
Stock selection:
  Weekday: AlertLog top stock by Priority Score
  Weekend/holiday: Nifty200 base/near-breakout stocks

ZENO emotion (STAGE TAKES PRIORITY OVER PCT_CHANGE):
  BREAKOUT CONFIRMED → zeno_greed.png  (always)
  BREAKOUT ALERT     → zeno_happy.png  (always)
  NEAR BREAKOUT      → zeno_thinking.png
  pct < -5%          → zeno_fear.png
  pct < -3%          → zeno_sad.png
  pct > 5%           → zeno_greed.png
  pct > 2%           → zeno_happy.png
  default            → zeno_thinking.png

Facebook: Hindi only, page token (not group — group broken)
Thumbnail: safe_thumbnail_text() strips Devanagari chars
TTS: safe_tts_price() — no Rs. symbol in spoken script
```

## trading_bot.py v15.0

```
5 entry filters (fastest first):
  1. Re-entry cooldown (RECD) — memory lookup, instant
     After TARGET HIT: 5 trading days no re-entry
     After SL/TSL: no cooldown

  2. Time window — date math, instant
     Bearish: 9:15 AM - 11:00 AM only
     Bullish: 9:15 AM - 2:30 PM
     Monday before 10 AM: skip | Friday after 2 PM: skip

  3. Daily entry limit — count, instant
     Bearish: max 1 per day | Bullish: max 3 per day

  4. Nifty direction — sheet value, instant
     Bearish: Nifty must be GREEN (>0%)
     Bullish: Nifty > -0.3%

  5. RSI(14) via yfinance — API call, only if 1-4 pass
     Bearish: RSI < 58 | Bullish: RSI < 65
     Failure: entry allowed (safe default)

Telegram: Basic (simplified) | Advance (full details) | Premium (+ options)
```

---

# SECTION 6 — TRADING SYSTEM

## AppScript v15.5 (NOT in GitHub)

```
Bound to sheet: 1fPNGL6AHs-7M-oC22zILg9FlyWi-7DF9NoVVqZQs2vk
Tabs: AlertLog, Nifty200, History, BotMemory

11-gate filter → WAITING stocks → AlertLog
_cleanSystemControlColumn() → protects T4
Options signals → cols U-X + Premium Telegram
Entry types: Breakout (Gates 1-10) | Base (Gate 11)
```

## AlertLog Column Map (0-based)

```
A=0  Signal Time    B=1  Symbol        C=2  Live Price
D=3  Priority Score E=4  Trade Type    F=5  Strategy
G=6  Breakout Stage H=7  Initial SL    I=8  Target
J=9  RR Ratio       K=10 Trade Status  L=11 Entry Price
M=12 Entry Time     N=13 Days in Trade O=14 Trailing SL
P=15 P/L%           Q=16 ATH Warning   R=17 Risk Rs.
S=18 Position Size  T=19 SYSTEM CONTROL
U=20 Options Signal V=21 Strike        W=22 Expiry
X=23 Theta Risk

T2 = automation switch YES/NO
T4 = Python bot state (TSL/MAX/LP/ATR/EXDT/RECD per stock)
```

---

# SECTION 7 — PLATFORMS STATUS

| Platform | Status | Note |
|----------|--------|------|
| YouTube Hindi | ✅ Auto | Education + Shorts + Reels |
| YouTube Kids Hindi (HerooQuest) | ✅ Auto | 3 videos/day |
| YouTube English | 🔄 Phase 3 | Add YOUTUBE_CREDENTIALS_EN |
| YouTube Kids English | 🔄 Phase 3 | Add YOUTUBE_CREDENTIALS_KIDS_EN |
| Facebook AI360 Page | ✅ Auto | Token updated 17 May 2026 |
| Facebook HerooQuest Page | ✅ Auto | Same token — auto exchanges |
| Facebook Group | ❌ Broken | Needs publish_to_groups Advanced Access |
| Instagram | ❌ Removed | Manual only |
| GitHub Pages ai360trading.in | ✅ Auto | 4 articles/day |
| Telegram 3 channels | ✅ Auto | Paper trading signals |

## Facebook Pages (confirmed 17 May 2026)

```
AI360Trading page:
  URL: facebook.com/ai360trading.official
  Name: still "Unofficial Amit Kumar" — change pending after category switch
  Category: Education (changed from Digital Creator)
  Type: Business (changed from Creator)
  Action: Try name change to "AI360 Trading" via Settings → Page Info → Name

HerooQuest page:
  URL: facebook.com/HerooQuest
  Name: HerooQuest ✅ (correct — no change needed)
  Category: Education ✅
  Type: Business ✅

META_ACCESS_TOKEN: Updated 17 May 2026
  Token works for both pages automatically
  token_refresh.py auto-renews on 1st and 20th of month
```

---

# SECTION 8 — GITHUB SECRETS

```
Telegram:
  TELEGRAM_BOT_TOKEN
  CHAT_ID_BASIC, CHAT_ID_ADVANCE, CHAT_ID_PREMIUM

AI360Trading Social:
  META_ACCESS_TOKEN  (updated 17 May 2026 — auto-refreshed)
  META_APP_ID, META_APP_SECRET
  FACEBOOK_PAGE_ID
  FACEBOOK_GROUP_ID  (group posting broken)
  YOUTUBE_CREDENTIALS (Hindi)
  YOUTUBE_CREDENTIALS_EN (Phase 3 — not set)

HerooQuest Kids:
  FACEBOOK_KIDS_PAGE_ID
  META_ACCESS_TOKEN_KIDS (same user token — auto exchanges for kids page)
  YOUTUBE_CREDENTIALS_KIDS (Hindi kids)
  YOUTUBE_CREDENTIALS_KIDS_EN (Phase 3 — not set)

AI Providers:
  GROQ_API_KEY (primary)
  GEMINI_API_KEY (secondary + kids image generation)
  ANTHROPIC_API_KEY (tertiary)
  OPENAI_API_KEY (quaternary + DALL-E 3 for kids)
  HF_TOKEN (HuggingFace FLUX.1 for kids images)
  STABILITY_API_KEY (Stability AI backgrounds)

Google + GitHub:
  GCP_SERVICE_ACCOUNT_JSON
  GH_TOKEN
  GOOGLE_SHEET_ID

Dhan API (Phase 4 — not connected):
  DHAN_API_KEY, DHAN_API_SECRET, DHAN_CLIENT_ID, DHAN_PIN, DHAN_TOTP_KEY
```

---

# SECTION 9 — PENDING TASKS

## 🔴 Critical

| Task | Action |
|------|--------|
| Facebook page name change | Settings → Page Info → Name → "AI360 Trading" (category now Education+Business — should work) |
| Facebook Group posting | Apply for publish_to_groups Advanced Access at developers.facebook.com |

## 🟡 Important This Week

| Task | Action |
|------|--------|
| Add YOUTUBE_CREDENTIALS_EN | English trading channel upload |
| Add YOUTUBE_CREDENTIALS_KIDS_EN | HerooQuest English upload |
| Consider reducing education video length | MIN_WORDS_SLIDE 80→60 or MIN_SLIDES 22→16 for ~10 min sweet spot |

## 🟢 Medium Term

| Task | Action |
|------|--------|
| Add ZENO to morning reel thumbnail | CTR improvement |
| HerooQuest thumbnail CTR (0.6% → 3%+) | Views growth |
| 30 paper trades → Phase 4 live trading | Main milestone |
| Bullish market → test base entry | AppScript v15.4 |

---

# SECTION 10 — PHASE ROADMAP

## Phase 1 ✅ Infrastructure (Complete)
## Phase 2 ✅ Content Upgrade (Complete)

## Phase 3 🔄 English + Global (Building)
- [x] 52-week education course ✅ confirmed working 17.9 min
- [x] generate_shorts.py v3.0 ✅
- [x] generate_kids_video.py v2.1 ✅
- [x] heroo.png fixed ✅
- [x] human_touch.py v2.2 ✅
- [x] ai_client.py v2.2 ✅
- [x] trading_bot.py v15.0 ✅
- [x] Options signals AppScript v15.5 ✅
- [x] Base entry AppScript v15.4 ✅
- [x] META_ACCESS_TOKEN updated ✅
- [x] Facebook pages: Education + Business category ✅
- [ ] YOUTUBE_CREDENTIALS_EN
- [ ] YOUTUBE_CREDENTIALS_KIDS_EN
- [ ] Facebook Group token fix
- [ ] Facebook page name: "AI360 Trading"

## Phase 4 📋 Live Trading
- After 30+ paper trades with win rate > 55%
- Dhan API integration
- Currently: 3 completed, need 27+ more

---

# SECTION 11 — MEMBERSHIP

| Plan | Price | Annual |
|------|-------|--------|
| Advance | Rs.699/month | Rs.5,588/year |
| Premium | Rs.1,499/month | Rs.11,988/year |

UPI: 9634759528@upi | WhatsApp: 9634759528
Advance: signals, TradingView, Chartink, private videos
Premium: Advance + options signals, live sessions, Sheet access

Broker links:
  Zerodha: https://bit.ly/2VK6k5F
  Dhan: https://invite.dhan.co/?invite=MSIVC45309

Contact: admin@ai360trading.in
Legal: Educational only. Not SEBI registered.
Disclaimer: ai360trading.in/disclaimer/
