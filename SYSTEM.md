# AI360Trading — Master System Documentation
**Last Updated:** 19 May 2026 — v16.4 FINAL (all files verified from GitHub)
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
> Drive files may be outdated. NEVER use them as reference for code.
> Always fetch the raw GitHub URL before touching any file.

### How To Read Any File

```
Format: https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/FILENAME

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

SYSTEM.md:
https://raw.githubusercontent.com/systronics/ai360trading/refs/heads/master/SYSTEM.md
```

### Mandatory Steps Before Any Code Change
```
1. Read current file from GitHub raw URL
2. Understand ALL imports, dependencies, architecture
3. Make ONLY minimal changes needed
4. Provide COMPLETE file — never partial/diffs
5. Owner pushes to GitHub after confirming
```

### Other Sources
```
AppScript: NOT in GitHub — owner pastes code directly into chat
AppScript v15.6 Drive backup: 1cBimCblQZ_tISDxXZ_rqTlogPS4Ty17h
Google Sheets ID: 1fPNGL6AHs-7M-oC22zILg9FlyWi-7DF9NoVVqZQs2vk
```

---

## The 10 Absolute Rules

| # | Rule | Why |
|---|------|-----|
| 1 | Read current GitHub file before ANY code change | Architecture changes constantly |
| 2 | Always provide COMPLETE file — never partial | Family cannot apply partial changes |
| 3 | Cost must stay Rs.0/month forever | Verify free tier before any new service |
| 4 | Never call generate_analysis.py — DELETED | Will crash workflow |
| 5 | META token expires every 60 days | token_refresh.yml handles auto 1st+15th |
| 6 | All PIL thumbnail text = English only | PIL cannot render Devanagari/Hindi |
| 7 | TTS script must never contain Rs. or ₹ | TTS reads "rupee sign" aloud |
| 8 | instagram upload removed — manual from phone | Instagram API restricted |
| 9 | AppScript edited manually in Sheets → Extensions → Apps Script | Not in GitHub |
| 10 | HerooQuest uses YOUTUBE_CREDENTIALS_KIDS not YOUTUBE_CREDENTIALS | Different channels |

---

# CONTENT SCHEDULE — VERIFIED FROM GITHUB

```
07:00 AM IST — Morning Reel (daily-morning-reel.yml)
  Schedule: EVERY DAY including weekends ✅
  Cron: 30 1 * * *
  Flow: generate_reel_morning.py → upload_youtube.py --type morning → upload_facebook.py --meta-prefix morning
  Content: Live Nifty + News RSS + BULLISH/BEARISH/NEUTRAL sentiment
  Thumbnail: "MORNING BRIEF" + sentiment badge + Nifty level + ZENO emotion

08:00 AM IST — HerooQuest Kids (kids-daily.yml)
  Schedule: EVERY DAY ✅
  Cron: 30 2 * * *
  Flow: 3 separate jobs (full story + cliffhanger short + DYK short)
  Each job: generate_kids_video.py → upload_kids_youtube.py → upload_facebook.py
  Content: 10-scene Pixar-style animated story with moral
  Thumbnail: Story-specific title (e.g. "GURU NANAK") + Heroo character + moral strip

10:00 AM IST — Education Video (daily-videos.yml)
  Schedule: Mon-Sat + Sunday 11 AM ✅
  Cron: 30 4 * * 1-6 and 30 5 * * 0
  Flow: generate_education.py (Hindi LANG=hi) → upload included
  Content: 52-week free investing course, ~18-21 min videos

10:00 AM IST — Articles (daily-articles.yml)
  Schedule: Mon-Fri 10 AM + Sat-Sun 11:30 AM ✅
  Cron: 30 4 * * 1-5 and 0 6 * * 6,0
  Flow: generate_articles.py → git commit → Facebook share inline
  ⚠️ NOTE: Facebook share in this file uses user token directly (no get_page_token())
  Impact: Article FB posts may fail — low priority vs video content

11:30 AM IST — Daily Shorts (daily-shorts.yml)
  Schedule: Mon-Fri 11:30 AM + Sat-Sun 1:30 PM ✅
  Cron: 0 6 * * 1-5 and 0 8 * * 6,0
  Flow: generate_shorts.py (handles both Short 2 + Short 3 + upload internally)
  Content: Short 2 Madhur (market) + Short 3 Neerja (global macro)

08:30 PM IST — ZENO Evening Reel (daily_reel.yml)
  Schedule: EVERY DAY ✅
  Cron: 0 15 * * *
  Flow: generate_reel.py → upload_youtube.py --type reel → upload_facebook.py
  Content: ZENO trading wisdom, weekend = weekend content, holiday = holiday content

Trading Bot (trading_bot.yml)
  Schedule: Every 5 min, 8:15 AM - 4:29 PM IST, Mon-Fri ✅
  Monitors Google Sheet → sends Telegram signals to 3 channels

KeepAlive (keepalive.yml)
  Schedule: Sun-Thu 11:59 PM IST ✅
  Commits .keepalive file → prevents GitHub disabling inactive repo
```

---

# FILES STATUS — VERIFIED FROM GITHUB (19 May 2026)

## Python Files

| File | Ver | GitHub Status | Key Features |
|------|-----|---------------|--------------|
| `ai_client.py` | v2.4 | ✅ | Groq 4 models + Gemini 2.5 + Anthropic + OpenAI + video chain |
| `human_touch.py` | v2.2 | ✅ | Education hooks + safe_thumbnail_text() + safe_tts_price() + get_video_description() |
| `generate_reel.py` | v2.1 | ✅ | No music + ZENO thumbnail + sentiment-aware |
| `generate_reel_morning.py` | v2.2 | ✅ | Live market data + News RSS + sentiment calc + BULLISH/BEARISH thumbnail |
| `generate_shorts.py` | v3.1 | ✅ | bgmusic REMOVED + Short2 Madhur + Short3 Neerja |
| `generate_kids_video.py` | v2.3 | ✅ | 10 scenes + Pollinations FLUX Pro + Ken Burns + xFade + vignette + multi-text thumb |
| `generate_education.py` | v1.1 | ✅ | Mode + title + duration + 52-week course |
| `generate_articles.py` | current | ✅ | No changes needed |
| `upload_youtube.py` | v2.2 | ✅ | Custom thumbnail upload + fallback builder |
| `upload_kids_youtube.py` | v2.3 | ✅ | SEO 30 tags + story-specific thumb + chapters + 15 hashtags |
| `upload_facebook.py` | v2.2 | ✅ | get_page_token() — fixes Error 200 page post failures |
| `token_refresh.py` | v2.1 | ✅ | CHAT_ID_BASIC fix + META_ACCESS_TOKEN_KIDS refresh |
| `content_calendar.py` | v2.2 | ✅ | get_article_seo_seeds() added |
| `kids_content_calendar.py` | current | ✅ | Day rotation — no changes needed |
| `indian_holidays.py` | current | ✅ | NSE API + fallback — no changes needed |
| `trading_bot.py` | v15.0 | ✅ | Fully operational |
| `requirements.txt` | v2.3 | ✅ | google-genai added for Gemini 2.5 |

## Workflow Files — VERIFIED STATUS

| File | Ver | GitHub Status | Timing | Issues |
|------|-----|---------------|--------|--------|
| `daily-morning-reel.yml` | v2.2 | ✅ PUSHED | 7:00 AM every day | None |
| `daily-videos.yml` | v2.2 | ✅ PUSHED | 10:00 AM Mon-Sat | generate_analysis removed |
| `daily-shorts.yml` | v2.1 | ⚠️ NEEDS PUSH | 11:30 AM daily | Only GROQ key — needs all 4 AI keys |
| `daily_reel.yml` | v2.1 | ⚠️ NEEDS PUSH | 8:30 PM daily | Only GROQ key — needs all 4 AI keys |
| `daily-articles.yml` | current | ✅ OK | 10:00 AM daily | FB share uses user token (low priority) |
| `kids-daily.yml` | v2.1 | ⚠️ NEEDS PUSH | 8:00 AM daily | OLD: single job, KIDS_LANG=both broken |
| `trading_bot.yml` | v2.1 | ⚠️ NEEDS PUSH | Every 5 min | TELEGRAM_CHAT_ID → CHAT_ID_BASIC |
| `token_refresh.yml` | v2.2 | ✅ PUSHED | 1st + 15th monthly | Schedule fixed |
| `daily-morning-reel.yml` | v2.2 | ✅ PUSHED | 7:00 AM daily | Now 7 days/week |
| `keepalive.yml` | current | ✅ GOOD | Sun-Thu 11:59 PM | No changes needed |

---

# APPSCRIPT v15.6 — TRADING SYSTEM

```
Location: Google Sheets → Extensions → Apps Script (NOT in GitHub)
Drive backup: 1cBimCblQZ_tISDxXZ_rqTlogPS4Ty17h
Pushed: 19 May 2026

v15.6 FIXES (from real trade data analysis):
  FIX 1 — HARD BEARISH BLOCK
    Nifty < 20DMA → max 3 WAITING slots, score ≥40, Sector Leader, RS ≥15
    Before: 5-8 trades in bearish → all hit SL (BHARATFORG, TATASTEEL, SAIL, BANDHANBNK)
    After:  0 trades in bearish unless exceptional → win rate 43% → 65%+ expected

  FIX 2 — MOMENTUM BREAKOUT DETECTION (new entry type)
    +3% move today + sector momentum = valid entry even with SMA=Sideways
    Captures: TECHM +4.85%, PERSISTENT +5.48%, COFORGE +5.15% style moves
    Old: These were blocked by SMA=Sideways gate → system missed IT rally

  FIX 3 — OPTIONS ATH BLOCK
    Stock within 3% of 52W High → options = "⏸ NEAR ATH" (was generating BUY CE)
    Fixes: MCX was getting BUY CE despite NEAR ATH warning

  FIX 4 — VOLUME BYPASS
    +3% price move = volume formula stale → bypass Gate 7
    Fixes: IT stocks with stale volume data showing as low volume

  FIX 5 — SECTOR MOMENTUM DETECTION
    3+ stocks in same sector up 2%+ = sector momentum day
    Unlocks that sector for entries even if individual scores are moderate

  FIX 6 (from v15.5) — OPTIONS ROW MISMATCH
    sheetRow = rowIdx + tradedCount + 2
    Options now appear in WAITING rows not TRADED rows

Performance impact:
  All 4 losses = entered in BEARISH market
  v15.6 would have blocked all 4
  Expected win rate: 43% → 65%+
```

---

# PLATFORMS STATUS

| Platform | Channel | Status | Notes |
|---|---|---|---|
| YouTube Hindi | AI360 Trading | ✅ Auto | Education 17-21 min daily, shorts 11:30 AM |
| YouTube Kids | HerooQuest | ✅ Auto | 3 videos/day, story-specific thumbnails |
| YouTube English | AI360 Trading | ⏳ Phase 3 | Needs YOUTUBE_CREDENTIALS_EN |
| YouTube Kids EN | HerooQuest EN | ⏳ Phase 3 | Needs YOUTUBE_CREDENTIALS_KIDS_EN |
| Facebook AI360 | AI360 Trading | ✅ Fixed | App Live + get_page_token() + fresh token |
| Facebook HerooQuest | HerooQuest | ✅ Auto | META_ACCESS_TOKEN_KIDS |
| Facebook Group | AI360 Community | ❌ Manual | Needs Advanced Access application |
| GitHub Pages | ai360trading.in | ✅ Auto | 4 articles/day Mon-Fri |
| Telegram Basic | @ai360trading | ✅ Auto | Free signals |
| Telegram Advance | @ai360trading_Advance | ✅ Auto | Rs.499/month |
| Telegram Premium | @ai360trading_Premium | ✅ Auto | Bundle plan |

---

# GITHUB SECRETS — COMPLETE LIST

```
Content/Social:
  META_ACCESS_TOKEN          ← Updated 18 May 2026 (60-day, 8 permissions)
  META_ACCESS_TOKEN_KIDS     ← HerooQuest Facebook page
  META_APP_ID                ← Facebook App ID
  META_APP_SECRET            ← Facebook App Secret
  FACEBOOK_PAGE_ID           ← 108076910943724 (AI360 Trading)
  FACEBOOK_KIDS_PAGE_ID      ← 1021152881090398 (HerooQuest)
  FACEBOOK_GROUP_ID          ← AI360 Community group
  YOUTUBE_CREDENTIALS        ← AI360 Trading YouTube OAuth
  YOUTUBE_CREDENTIALS_KIDS   ← HerooQuest YouTube OAuth
  YOUTUBE_CREDENTIALS_EN     ← ⏳ Pending Phase 3
  YOUTUBE_CREDENTIALS_KIDS_EN ← ⏳ Pending Phase 3

AI Providers:
  GROQ_API_KEY               ← Primary (100k tokens/day free)
  GEMINI_API_KEY             ← Gemini 2.5 + image generation
  ANTHROPIC_API_KEY          ← Claude fallback
  OPENAI_API_KEY             ← DALL-E + GPT fallback
  HF_TOKEN                   ← HuggingFace FLUX.1

Trading:
  GCP_SERVICE_ACCOUNT_JSON   ← Google Sheets API access
  TELEGRAM_BOT_TOKEN         ← Bot token for all channels
  CHAT_ID_BASIC              ← Basic channel (was TELEGRAM_CHAT_ID — wrong!)
  CHAT_ID_ADVANCE            ← Advance channel
  CHAT_ID_PREMIUM            ← Premium channel
  GH_TOKEN                   ← GitHub API for secret updates

Token auto-refresh: 1st + 15th of every month
Next META expiry: ~July 2026
```

---

# AI CLIENT — FALLBACK CHAIN (ai_client.py v2.4)

```
TEXT GENERATION (priority order):
  1. Groq llama-3.3-70b-versatile  — 100k tokens/day free ← primary
  2. Groq llama-3.1-8b-instant     — faster fallback
  3. Groq gemma2-9b-it
  4. Groq qwen-qwq-32b
  5. Gemini gemini-2.5-flash
  6. Gemini gemini-2.5-flash-8b
  7. Anthropic claude-3-haiku
  8. OpenAI gpt-4o-mini
  Cost: Rs.0

IMAGE GENERATION (for kids video, priority order):
  1. Gemini 2.5 Flash Image  — ~50/day free
  2. Pollinations.ai FLUX Pro — FREE, no API key, Pixar quality ← best free option
  3. HuggingFace FLUX.1      — free with HF_TOKEN
  4. DALL-E 2                — uses OpenAI credits
  5. PIL placeholder         — always works, Heroo.png overlaid

VIDEO QUALITY:
  Currently: Pixar images + Ken Burns zoom + xFade + color grade + vignette
  Looks like animated video to most viewers
  Future: Kling AI $6/month when first revenue arrives
```

---

# THUMBNAIL PHILOSOPHY

```
The thumbnail IS the content preview.
Viewer scrolls → READS thumbnail text → curious → clicks → watches.

PROVEN FORMULA (competitor analysis confirmed):

HerooQuest 16:9:
  Left: Story-specific title 110px YELLOW (e.g. "GURU NANAK" not "HEROO KI KAHANI")
  Left: Moral strip — "💡 PATIENCE WINS" (curiosity gap)
  Left bottom: "Ep N" badge
  Right: Heroo character 92% height (emotional connection)
  Top left: HerooQuest brand pill (red)
  Top right: Episode badge (yellow)
  Background: Scene image with 60% dark overlay

Morning Reel 9:16:
  "MORNING BRIEF" 120px yellow
  "📈 BULLISH DAY" or "📉 BEARISH DAY" (colour-coded badge)
  "NIFTY 23643" — specific number stops traders scrolling
  ZENO character matching sentiment emotion
  "7:00 AM IST" time tag

ZENO Shorts 9:16:
  ZENO character 60% height
  Topic text LARGE bold (already working — 10-19 views per short)
  Lesson subtitle readable in 2 seconds
```

---

# SEO RULES

```
HerooQuest title:
  "{Story Name} | Heroo Ki Kahani | HerooQuest | Hindi Moral Story 2026"
  NOT generic: "HerooQuest — Heroo Ki Kahani" (same every day)

HerooQuest tags (30):
  Brand + Genre + Language-specific + India-specific + Platform + Year
  Key: HindiCartoon, BachonKiKahani, CartoonInHindi, BalKahani

Description rules:
  First 100 chars = CTA (shown in YouTube search)
  Timestamps/chapters for videos >5 min (YouTube algorithm boost)
  15 hashtags at bottom
  Website + subscribe link

Morning Reel title:
  "Nifty {LEVEL} {SENTIMENT} — {DD MMM} | Morning Brief | AI360Trading #Shorts"
  Specific data in title = trader search traffic

Education title:
  "Stock Market Kya Hai? | Beginners Guide 2026 | Week N Hindi | AI360Trading"
```

---

# TRADING SYSTEM (19 May 2026)

```
Market: BEARISH (Nifty 23,649 < 20DMA 24,011)
Paper trades: 7 total | 3W/4L | Win rate 43% | Net +₹414

Active positions:
  ONGC     → Entry 298.35 | SL 293.45 | 6 days
  BHEL     → Entry 396.95 | SL 396.95 | 6 days
  NESTLEIND → Entry 1,458.70 | SL 1,415.7 | 4 days
  IDEA     → Entry 13.06   | SL 12.54   | 4 days

Loss analysis:
  All 4 losses = entered during BEARISH regime
  v15.6 hard block = these 4 trades would NOT have entered
  Expected win rate with v15.6: 65%+

Phase 4 trigger: 30 paper trades with 60%+ win rate
  Currently: 7 done, 23 more needed
  Target: Live trading with Rs.1,000 starting capital
```

---

# KNOWN ISSUES

| # | Issue | Status | Fix |
|---|-------|--------|-----|
| 1 | kids-daily.yml OLD on GitHub | 🔴 NEEDS PUSH | v2.1 in Drive: 1zJIGeWfOZwnznNuJTAWyohWUM0qITkA9 |
| 2 | daily-shorts.yml OLD on GitHub | 🔴 NEEDS PUSH | v2.1 in Drive: 1x9PvDmr9uRioU3wCJb1SplG30PuhMIY5 |
| 3 | trading_bot.yml TELEGRAM_CHAT_ID wrong | 🔴 NEEDS PUSH | v2.1 in Drive: 14aNlWzoizZ7WBM5kBU7DLERWSM7-D2cJ |
| 4 | daily_reel.yml only GROQ key | 🟡 NEEDS PUSH | v2.1 in Drive: 1Go1AVab3lB4jjI8mRqtJ3YriWxV0zbK4 |
| 5 | daily-articles.yml FB uses user token | 🟡 Low priority | Article FB posts may fail occasionally |
| 6 | Old HerooQuest thumbnails "Scene 99" | ⚪ Cannot fix | Only new uploads have correct thumbnails |
| 7 | YOUTUBE_CREDENTIALS_EN missing | ⏳ Phase 3 | Create when Phase 3 starts |
| 8 | Facebook Group Advanced Access | ⏳ Pending | Apply at business.facebook.com |

---

# PENDING TASKS

### 🔴 Push to GitHub NOW
```
1. kids-daily.yml v2.1    → 3 jobs + requirements.txt (Drive: 1zJIGeWfOZwnznNuJTAWyohWUM0qITkA9)
2. daily-shorts.yml v2.1  → all 4 AI keys            (Drive: 1x9PvDmr9uRioU3wCJb1SplG30PuhMIY5)
3. trading_bot.yml v2.1   → CHAT_ID_BASIC fix         (Drive: 14aNlWzoizZ7WBM5kBU7DLERWSM7-D2cJ)
4. daily_reel.yml v2.1    → all 4 AI keys             (Drive: 1Go1AVab3lB4jjI8mRqtJ3YriWxV0zbK4)
5. SYSTEM.md v16.4        → this file                 (Drive: current)
```

### 🟡 This Week
```
6. Apply Facebook Group Advanced Access (business.facebook.com)
7. Monitor HerooQuest CTR (target 0.6% → 3%+ with story-specific thumbnails)
8. Paper trade 23 more times to reach 30 total → Phase 4 live trading
```

### 🟢 After First Revenue
```
9. Kling AI $6/month → true animation for HerooQuest
10. Top up Claude and OpenAI credits
11. Phase 4: Live trading with Rs.1,000 capital
```

---

# DRIVE FILE REGISTRY

| File | Version | Drive ID |
|------|---------|----------|
| AppScript v15.6 | Trading | `1cBimCblQZ_tISDxXZ_rqTlogPS4Ty17h` |
| ai_client.py | v2.4 | `1EkH83uFKQGHCQ_VOy3GppmMvfU530AGC` |
| human_touch.py | v2.2 | `1eqHSztsuoZX1o6LtxhliMPNnAuoLATEx` |
| generate_reel.py | v2.1 | `1jVb89AF6XxY_DpGHoo9op_VW3D25l-G-` |
| generate_reel_morning.py | v2.2 | `1T2wGhyMUQmwVsd1Gpni2TtsUE1RpD2_T` |
| generate_shorts.py | v3.1 | `1an4YFiK9T1zO2gaPxpu7il2IT9CNTAgF` |
| generate_kids_video.py | v2.3 | `1-8_nRF8LPZWOpRr3j3meoQskQd-xaS2h` |
| upload_youtube.py | v2.2 | `1w0bs3xAnpXXJp3oCwWm0f2-vnsqYSU3E` |
| upload_kids_youtube.py | v2.3 | `1WTMEMxPBN_o6ut4Xqo0jtVaWQ6c2fqpv` |
| upload_facebook.py | v2.2 | `1HB8Wk3jp74RwNb0IFLSfytx8ARRVBEXk` |
| token_refresh.py | v2.1 | `1g5nuRJpoqTXE7wVqOTxZiqWJQ0Jv8Fuo` |
| requirements.txt | v2.3 | `1yrQgpnrnZ6rCXIko6gYx5J9hR4p1dhHu` |
| daily-morning-reel.yml | v2.2 | `1pDV29PdA6hM8OfgC_nZUxN0Qk8SfRF_B` |
| daily-videos.yml | v2.2 | `1rD3wglXm7VV35ilgdEq-vFzHXfhHOUhX` |
| daily-shorts.yml | v2.1 FINAL | `1x9PvDmr9uRioU3wCJb1SplG30PuhMIY5` |
| daily_reel.yml | v2.1 FINAL | `1Go1AVab3lB4jjI8mRqtJ3YriWxV0zbK4` |
| kids-daily.yml | v2.1 FINAL | `1zJIGeWfOZwnznNuJTAWyohWUM0qITkA9` |
| trading_bot.yml | v2.1 FINAL | `14aNlWzoizZ7WBM5kBU7DLERWSM7-D2cJ` |
| token_refresh.yml | v2.2 | `1M_rUNxepr2ZIMBGwCqxfb4gTYtR3_VYg` |
| _config.yml | cleaned | `1iVwSvNtEzbAbH7hTSDXBtSb7hTWud0It` |
| SYSTEM.md | v16.4 | `(this file — push to GitHub)` |
