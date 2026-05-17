# AI360Trading — Master System Documentation
**Last Updated:** 17 May 2026 — Full day session — Major fixes applied
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

> NEVER write, suggest, or modify any code without FIRST reading the
> current version from GitHub. GitHub master branch is the ONLY source of truth.
> Drive files may be outdated. Never use them as reference for code.

### How Any AI Can Read Any File Instantly

The repo is PUBLIC. Construct raw URL from filename:

```
Format:
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/FILENAME

All Python files:
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

### Other Info Sources
```
AppScript (NOT in GitHub — owner must share code directly)
Google Sheets: 1fPNGL6AHs-7M-oC22zILg9FlyWi-7DF9NoVVqZQs2vk
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

Build a fully automated passive income system that runs forever on Rs.0/month infrastructure.

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

---

# SECTION 2 — FILE STRUCTURE (confirmed 17 May 2026)

## Python Files

| File | Purpose | Version | Status |
|------|---------|---------|--------|
| `ai_client.py` | Universal AI fallback chain + video generation | v2.4 | ✅ Live |
| `human_touch.py` | Anti-AI-penalty layer | v2.2 | ✅ Live |
| `content_calendar.py` | 52-week education + day topics + get_article_seo_seeds() | v2.2 | ✅ Live |
| `kids_content_calendar.py` | Kids story topics (SEPARATE file) | — | ✅ Live |
| `indian_holidays.py` | NSE holiday + mode detection | — | ✅ Live |
| `trading_bot.py` | Signal monitor + TSL + 5 filters | v15.0 | ✅ Live |
| `generate_education.py` | 52-week education videos | v1.1 | ✅ Live |
| `generate_shorts.py` | Stock shorts + ZENO + Facebook | v3.0 | ✅ Live |
| `generate_kids_video.py` | HerooQuest full/short/didyouknow | v2.1 | ✅ Live |
| `generate_reel.py` | ZENO evening reel — no bgmusic | v2.1 | ✅ Live |
| `generate_reel_morning.py` | Morning reel — no bgmusic + live Nifty | v2.1 | ✅ Live |
| `generate_articles.py` | 4 SEO articles daily | v2.1 | ✅ Live |
| `token_refresh.py` | Auto META token refresh | — | ✅ Live |
| `upload_youtube.py` | YouTube upload (trading channel) | — | ✅ Live |
| `upload_kids_youtube.py` | YouTube upload (kids channel) | — | ✅ Live |
| `upload_facebook.py` | Facebook page upload | v2.1 | ✅ Live |
| `requirements.txt` | Python dependencies + google-genai v2.3 | v2.3 | ✅ Live |
| `generate_analysis.py` | DELETED | — | ❌ |
| `upload_instagram.py` | DELETED | — | ❌ |
| `generate_community_post.py` | DELETED | — | ❌ |

## GitHub Actions Workflows

| File | Schedule (IST) | Purpose |
|------|---------------|---------|
| `trading_bot.yml` | Every 5 min 8:15-16:29 Mon-Fri | Signal monitor + TSL |
| `daily-videos.yml` | 7:30 AM Mon-Fri / 9:30 AM Sat-Sun | Education video |
| `daily-shorts.yml` | 11:30 AM Mon-Fri / 1:30 PM Sat-Sun | Stock shorts |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning + ZENO reels |
| `daily-morning-reel.yml` | 7:00 AM daily | Morning reel |
| `daily-articles.yml` | 10:00 AM Mon-Fri / 11:30 AM Sat-Sun | 4 SEO articles |
| `kids-daily.yml` | 8:00 AM daily | HerooQuest 3 outputs |
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
| `public/music/` | ❌ DELETED May 17 — bgmusic caused Meta muting |

---

# SECTION 3 — DAILY CONTENT SCHEDULE

| Time IST | Content | Generator | Platform |
|----------|---------|-----------|---------|
| 7:00 AM | Morning reel (9:16) | generate_reel_morning.py | YouTube + Facebook |
| 7:30 AM | Education video Hindi (~17 min) | generate_education.py EDUCATION_LANG=hi | YouTube Hindi |
| 7:30 AM | Education video English | generate_education.py EDUCATION_LANG=en | YouTube English (Phase 3) |
| 8:00 AM | HerooQuest Full Story | generate_kids_video.py KIDS_OUTPUT=full | YouTube Kids |
| 8:00 AM | HerooQuest Cliffhanger | generate_kids_video.py KIDS_OUTPUT=short | YouTube Kids |
| 8:00 AM | HerooQuest Did You Know | generate_kids_video.py KIDS_OUTPUT=didyouknow | YouTube Kids |
| 10:00 AM | 4 SEO articles | generate_articles.py | GitHub Pages + Facebook |
| 11:30 AM | Stock short Hindi | generate_shorts.py | YouTube Shorts + Facebook |
| 8:30 PM | ZENO reel | generate_reel.py | YouTube + Facebook |

---

# SECTION 4 — AI CLIENT v2.4

## Fallback Chain
```
Groq → Gemini → Claude → OpenAI → Templates
```

## Groq Models (v2.4 — updated May 17)
```
ACTIVE (current, free):
  llama-3.3-70b-versatile   ← primary
  llama-3.1-8b-instant      ← fast fallback (NEW)
  gemma2-9b-it              ← Google via Groq (NEW)
  qwen-qwq-32b              ← reasoning (NEW)

REMOVED (decommissioned — were causing errors):
  llama-3.1-70b-versatile   ← decommissioned
  mixtral-8x7b-32768        ← decommissioned
```

## Gemini Models (v2.4 — updated May 17)
```
  gemini-2.5-flash          ← NEW — higher free tier
  gemini-2.0-flash          ← existing
  gemini-2.5-flash-8b       ← NEW fast fallback
```

## Daily Token Limits (causing cascading failure on May 17)
```
Groq free: 100,000 tokens/day
  System uses ~98,000/day (education + shorts + articles + reels)
  Solution: new models added to spread load

Gemini free: exhausted by end of day
  Solution: Gemini 2.5 has higher free limits

Claude: needs credit top-up (balance low)
OpenAI: needs credit top-up (quota exceeded)
```

## Video Generation Chain (v2.3+)
```
img_client.generate_video_clip(prompt, duration, aspect_ratio, output_path)

Layer 1: Google Veo 2 — GEMINI_API_KEY (~50 free/day)
Layer 2: HuggingFace Wan-2.2 — HF_TOKEN (free unlimited)
Layer 3: Stability AI image-to-video — STABILITY_API_KEY
Layer 4: PIL placeholder — always works

No new API keys needed — uses existing keys.
```

## Education System Prompt (v2.3+)
```
mode="education" → teacher persona
  NO: "aaj ka market", "chart pattern", "breakout signal"
  YES: "yeh concept", "samjhate hain", "example ke taur pe"
  Prevents education videos sounding like trading signal videos
```

---

# SECTION 5 — KEY FILE DETAILS

## generate_reel_morning.py v2.1
```
FIX 1: No background music — TTS voice only
  public/music/ deleted — no bgmusic files
  Prevents Meta muting in countries without music rights

FIX 2: Live Nifty data injected before prompt
  get_live_nifty_data() via yfinance before building prompt
  Prevents AI using Nifty 18500 (2022-2023 training data)
  If yfinance fails: blocks AI from mentioning any level

FIX 3: Proper thumbnail
  ZENO 65% height + 120px bold yellow topic text
  "MORNING BRIEF" + "7:00 AM" badge
```

## generate_reel.py v2.1
```
FIX 1: No background music — TTS voice only
FIX 2: Proper thumbnail with ZENO 70% height + 130px bold yellow title
  Drop shadow on text for maximum contrast
  AI360Trading badge top left
```

## generate_education.py v1.1
```
FIX 1: CONTENT_MODE auto-detect when empty (Saturday → weekend)
FIX 2: clean_edu_title() removes stray percentages from title
FIX 3: expand_slide_content() forces 80+ words/slide → 17.9 min video
FIX 4: LANG from EDUCATION_LANG env var
FIX 5: Week number from content_calendar v2.2

Confirmed working May 17:
  Hindi: 17.9 min ✅ mid-roll ads active ✅
  Title: "Stock Market Kya Hai | Week 1 | AI360 Trading" ✅
  youtube.com/watch?v=cvRcZNzLbPw
```

## content_calendar.py v2.2
```
ADDED: get_article_seo_seeds(mode)
  Fixes: [WARN] content_calendar.py not found — SEO seeds skipped
  Weekend/holiday: no_price_numbers=True
    Prevents AI hallucinating "2.1% S&P 500" or "Bitcoin 78,000" in titles
  Market: day-specific SEO seeds (Mon=Options, Tue=Technical, etc.)

PRESERVED: get_todays_topic(), get_todays_education_topic()
```

## generate_kids_video.py v2.1
```
Architecture: AI images (Gemini → HF → DALL-E → PIL) + ffmpeg
Import: from kids_content_calendar import get_today_topic
        NOT from content_calendar (separate file)

FIX 1: 10 scenes × 45 sec = ~7.5 min (was 1.8 min with 4 scenes)
FIX 2: Thumbnail with Heroo 70% height + big yellow title
FIX 3: heroo.png loading with fallback chain

heroo.png: public/image/heroo.png ✅ (was heroo.png.png — fixed May 16)
```

## trading_bot.py v15.0
```
5 entry filters (fastest first):
1. Re-entry cooldown (RECD) — 5 trading days after TARGET HIT
2. Time window — Bearish: 9:15-11:00 AM | Bullish: 9:15-2:30 PM
3. Daily limit — Bearish: max 1 | Bullish: max 3
4. Nifty direction — Bearish: must be green | Bullish: > -0.3%
5. RSI — Bearish: <58 | Bullish: <65

Paper trading: 3W/0L = 100% win rate | Rs.2,001 profit | 8 open trades
```

---

# SECTION 6 — FACEBOOK STATUS (May 17 2026)

## App Status — FIXED TODAY
```
Problem: App was in Development mode → only app admins could post
         All page posts returning Error 200
Fix: App switched to Live mode (17 May 2026)
     New token generated with all 8 permissions
     META_ACCESS_TOKEN updated in GitHub secrets

Token permissions (8 selected):
  ✅ instagram_content_publish
  ✅ pages_read_engagement
  ✅ pages_manage_metadata
  ✅ pages_read_user_content
  ✅ pages_manage_posts
  ✅ pages_manage_engagement
  + 2 more

Expected result: Tonight's 8:30 PM ZENO reel → Facebook post should work
```

## Pages Status
```
AI360Trading: facebook.com/ai360trading.official
  Name: "Unofficial Amit Kumar" → change request pending
  Category: Education ✅ | Type: Business ✅
  App: Live ✅ | Token: Updated May 17 ✅

HerooQuest: facebook.com/HerooQuest
  Name: HerooQuest ✅ | Category: Education ✅ | Type: Business ✅
```

## Background Music — REMOVED
```
public/music/ folder deleted May 17
Reason: Meta mutes videos with copyrighted bgmusic
        "Your video is muted in certain countries"
        = zero watch time on Facebook

All generators now: TTS voice only
  generate_reel.py v2.1 ✅
  generate_reel_morning.py v2.1 ✅
  generate_shorts.py — check if bgmusic still referenced
  generate_kids_video.py — never had music ✅
```

## Group Posting
```
Facebook Group: facebook.com/groups/ai360trading
Status: ❌ publish_to_groups requires Advanced Access (Meta review)
Strategy: Post to Page automatically (works now with Live app)
          Manual group posts 2x/day for community feel
          Morning: "Aaj ke signals: [stocks]"
          Evening: "Aaj ka result: [performance]"
```

---

# SECTION 7 — TRADING SYSTEM

## AppScript v15.5 (NOT in GitHub)
```
Bound to: 1fPNGL6AHs-7M-oC22zILg9FlyWi-7DF9NoVVqZQs2vk
11-gate filter → WAITING → AlertLog
Options signals → cols U-X + Premium Telegram
Entry types: Breakout (Gates 1-10) | Base (Gate 11)
_cleanSystemControlColumn() protects T4
```

## AlertLog Column Map
```
A=0 Signal Time  B=1 Symbol      C=2 Live Price  D=3 Priority
E=4 Trade Type   F=5 Strategy    G=6 Stage       H=7 Initial SL
I=8 Target       J=9 RR          K=10 Status     L=11 Entry Price
M=12 Entry Time  N=13 Days       O=14 Trail SL   P=15 P/L%
Q=16 ATH Warn    R=17 Risk Rs.   S=18 Qty        T=19 SYS CTRL
U=20 Opt Signal  V=21 Strike     W=22 Expiry     X=23 Theta

T2 = automation switch YES/NO
T4 = bot state per stock (TSL/MAX/LP/ATR/EXDT/RECD)
```

## Telegram Channels
| Channel | Secret | Content |
|---------|--------|---------|
| Basic | CHAT_ID_BASIC | Market mood, count, CTA |
| Advance Rs.699/mo | CHAT_ID_ADVANCE | Full entry/exit, TSL, mid-day |
| Premium Rs.1499/mo | CHAT_ID_PREMIUM | Advance + options signals |

## Paper Trading (Week 1)
```
3 wins / 0 losses = 100% | Rs.2,001 total
  BSE:        +3.87% | Rs.502
  IDEA:       +5.94% | Rs.773
  ADANIPORTS: +5.58% | Rs.725
Open: 8 trades | Need 27+ more → Phase 4
```

---

# SECTION 8 — PLATFORMS

| Platform | Status | Note |
|----------|--------|------|
| YouTube Hindi | ✅ Auto | Education + Shorts + Reels |
| YouTube Kids Hindi | ✅ Auto | 3 videos/day |
| YouTube English | 🔄 Phase 3 | Add YOUTUBE_CREDENTIALS_EN |
| YouTube Kids English | 🔄 Phase 3 | Add YOUTUBE_CREDENTIALS_KIDS_EN |
| Facebook AI360 Page | ✅ Fixed May 17 | App now Live + new token |
| Facebook HerooQuest Page | ✅ Auto | Same token |
| Facebook Group | ❌ Manual | publish_to_groups needs Meta review |
| Instagram | ❌ Removed | Manual only |
| GitHub Pages | ✅ Auto | 4 articles/day |
| Telegram | ✅ Auto | 3 channels |

---

# SECTION 9 — GITHUB SECRETS

```
Telegram:
  TELEGRAM_BOT_TOKEN | CHAT_ID_BASIC | CHAT_ID_ADVANCE | CHAT_ID_PREMIUM

AI360Trading:
  META_ACCESS_TOKEN  ← UPDATED May 17 2026 (Live mode token, 8 permissions)
  META_APP_ID | META_APP_SECRET
  FACEBOOK_PAGE_ID | FACEBOOK_GROUP_ID
  YOUTUBE_CREDENTIALS | YOUTUBE_CREDENTIALS_EN (Phase 3)

HerooQuest:
  FACEBOOK_KIDS_PAGE_ID | META_ACCESS_TOKEN_KIDS
  YOUTUBE_CREDENTIALS_KIDS | YOUTUBE_CREDENTIALS_KIDS_EN (Phase 3)

AI Providers:
  GROQ_API_KEY | GEMINI_API_KEY | ANTHROPIC_API_KEY | OPENAI_API_KEY
  HF_TOKEN | STABILITY_API_KEY

Google + GitHub:
  GCP_SERVICE_ACCOUNT_JSON | GH_TOKEN | GOOGLE_SHEET_ID

Dhan API (Phase 4):
  DHAN_API_KEY | DHAN_API_SECRET | DHAN_CLIENT_ID | DHAN_PIN | DHAN_TOTP_KEY
```

---

# SECTION 10 — PENDING TASKS

## 🔴 Critical
| Task | Action |
|------|--------|
| Verify Facebook posting working | Check tonight's 8:30 PM ZENO reel on Facebook page |
| Facebook page name change | Settings → Page Info → Name → "AI360 Trading" (category now Education+Business) |
| Claude/OpenAI credits | Top up to prevent cascading AI failures |

## 🟡 Important
| Task | Action |
|------|--------|
| Add YOUTUBE_CREDENTIALS_EN | English trading channel |
| Add YOUTUBE_CREDENTIALS_KIDS_EN | HerooQuest English |
| Monitor education video length | 17.9 min may be too long — reduce MIN_SLIDES 22→16 for ~10 min |
| Check generate_shorts.py for bgmusic | May still reference MUSIC_DIR |

## 🟢 Medium Term
| Task | Action |
|------|--------|
| 30 paper trades → Phase 4 | Currently 3/30 |
| HerooQuest CTR 0.6% → 3%+ | Thumbnail improvement |
| Facebook Group Advanced Access | Apply at developers.facebook.com |
| Add ZENO to morning reel | CTR improvement |

---

# SECTION 11 — PHASE ROADMAP

## Phase 1 ✅ Infrastructure (Complete)
## Phase 2 ✅ Content Upgrade (Complete)

## Phase 3 🔄 Building
- [x] Education course 52 weeks ✅
- [x] All generators v2+ ✅
- [x] heroo.png fixed ✅
- [x] Background music removed ✅
- [x] Facebook app Live mode ✅
- [x] Token updated with correct permissions ✅
- [x] Groq decommissioned models fixed ✅
- [x] Gemini 2.5 added ✅
- [x] Video generation chain added ✅
- [ ] YOUTUBE_CREDENTIALS_EN
- [ ] YOUTUBE_CREDENTIALS_KIDS_EN
- [ ] Facebook Group token

## Phase 4 📋 Live Trading
After 30+ paper trades with win rate > 55%

---

# SECTION 12 — MEMBERSHIP

| Plan | Price | Annual |
|------|-------|--------|
| Advance | Rs.699/month | Rs.5,588/year |
| Premium | Rs.1,499/month | Rs.11,988/year |

UPI: 9634759528@upi | WhatsApp: 9634759528
Brokers: Zerodha bit.ly/2VK6k5F | Dhan invite.dhan.co/?invite=MSIVC45309
Contact: admin@ai360trading.in
Legal: Educational only. Not SEBI registered.
