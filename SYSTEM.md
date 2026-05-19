# AI360Trading — Master System Documentation
**Last Updated:** 19 May 2026 — Full day session — v16.3
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
AppScript v15.6 saved in Drive: 1cBimCblQZ_tISDxXZ_rqTlogPS4Ty17h
Google Sheets: 1fPNGL6AHs-7M-oC22zILg9FlyWi-7DF9NoVVqZQs2vk
```

---

## The 10 Absolute Rules

| # | Rule | Why |
|---|------|-----|
| 1 | Read current GitHub file before ANY code change | Architecture changes — always verify |
| 2 | Always provide COMPLETE file content | Family cannot apply partial changes |
| 3 | Cost must stay Rs.0/month forever | Verify free tier before any new service |
| 4 | Never call generate_analysis.py — it was DELETED | Will crash workflow if called |
| 5 | Meta token expires every 60 days — refresh before changes | Token_refresh.yml handles auto |
| 6 | All thumbnail text must be English only (no Devanagari in PIL) | PIL cannot render Hindi |
| 7 | TTS script must never contain Rs. or ₹ symbols | TTS reads "rupee sign" aloud |
| 8 | Never use localStorage in artifacts | Not supported in Claude.ai |
| 9 | AppScript is edited manually in Google Sheets → Extensions → Apps Script | Not in GitHub |
| 10 | HerooQuest and Education both use YOUTUBE_CREDENTIALS (different credentials) | Different channels |

---

# CONTENT SCHEDULE — WHAT RUNS WHEN

```
07:00 AM IST — Morning Reel (daily-morning-reel.yml) — EVERY DAY
  generate_reel_morning.py v2.2
  → Fetches live: Nifty, Crude, Gold, DXY, BTC, S&P500 via yfinance
  → Reads Google News RSS (5 feeds, free, no API)
  → Calculates BULLISH/BEARISH/NEUTRAL sentiment
  → Script mentions actual market data — not generic
  → Thumbnail: "MORNING BRIEF" + sentiment badge + Nifty level + ZENO
  → Uploads: YouTube + Facebook AI360 page

08:00 AM IST — HerooQuest Kids Video (kids-daily.yml) — EVERY DAY
  generate_kids_video.py v2.3
  → 10 scenes × 40-50 sec = ~7.5 min full story
  → Image: Pollinations.ai FLUX Pro (Pixar-quality, FREE)
  → Effects: Ken Burns zoom + xFade transitions + color grade + vignette
  → Thumbnail: Story-specific title (e.g. "GURU NANAK") + Heroo + moral
  → 3 separate jobs: full story + cliffhanger short + DYK short
  → Uploads: YouTube Kids + Facebook HerooQuest page

10:00 AM IST — Education Video (daily-videos.yml) — MON-SAT
  generate_education.py v1.1
  → 52-week free investing course
  → Hindi + English versions
  → Thumbnail: "SUMMARY OF KEY POINTS" style
  → Uploads: YouTube AI360Trading

11:30 AM IST — Daily Shorts (daily-shorts.yml) — MON-FRI
  generate_shorts.py v3.1
  → Short 2: Madhur voice (market content)
  → Short 3: Neerja voice (global content)
  → No background music (prevents Meta muting)
  → Uploads: YouTube + Facebook AI360 page

08:30 PM IST — ZENO Evening Reel (daily_reel.yml) — MON-FRI
  generate_reel.py v2.1
  → ZENO character + trading wisdom
  → Thumbnail: ZENO + topic title + lesson subtitle
  → Uploads: YouTube + Facebook AI360 page
```

---

# FILES STATUS — COMPLETE TABLE (as of 19 May 2026)

| File | Version | Status | Key Changes | Drive ID |
|------|---------|--------|-------------|----------|
| `ai_client.py` | v2.4 | ✅ GitHub | Groq models fixed + Gemini 2.5 + video chain | `1EkH83uFKQGHCQ_VOy3GppmMvfU530AGC` |
| `human_touch.py` | v2.2 | ✅ GitHub | Education hooks + safe_thumbnail + safe_tts + get_video_description | `1eqHSztsuoZX1o6LtxhliMPNnAuoLATEx` |
| `generate_reel.py` | v2.1 | ✅ GitHub | No music + proper thumbnail | `1jVb89AF6XxY_DpGHoo9op_VW3D25l-G-` |
| `generate_reel_morning.py` | v2.2 | ✅ GitHub | Market intelligence + live Nifty + sentiment | `1T2wGhyMUQmwVsd1Gpni2TtsUE1RpD2_T` |
| `generate_shorts.py` | v3.1 | ✅ GitHub | bgmusic completely removed | `1an4YFiK9T1zO2gaPxpu7il2IT9CNTAgF` |
| `generate_kids_video.py` | v2.3 | ✅ GitHub | Cinematic effects + Pollinations.ai + multi-text thumbnail | `1-8_nRF8LPZWOpRr3j3meoQskQd-xaS2h` |
| `generate_education.py` | v1.1 | ✅ GitHub | Mode + title + duration | — |
| `generate_articles.py` | current | ✅ GitHub | No changes needed | — |
| `upload_youtube.py` | v2.2 | ✅ GitHub | Custom thumbnail upload + fallback builder | `1w0bs3xAnpXXJp3oCwWm0f2-vnsqYSU3E` |
| `upload_kids_youtube.py` | v2.3 | ✅ GitHub | SEO fix + story-specific thumbnail + 30 tags | `1WTMEMxPBN_o6ut4Xqo0jtVaWQ6c2fqpv` |
| `upload_facebook.py` | v2.2 | ✅ GitHub | get_page_token() added — root cause of all FB failures | `1HB8Wk3jp74RwNb0IFLSfytx8ARRVBEXk` |
| `token_refresh.py` | v2.1 | ✅ GitHub | CHAT_ID_BASIC fix + META_ACCESS_TOKEN_KIDS | `1g5nuRJpoqTXE7wVqOTxZiqWJQ0Jv8Fuo` |
| `content_calendar.py` | v2.2 | ✅ GitHub | get_article_seo_seeds() added | — |
| `kids_content_calendar.py` | current | ✅ GitHub | Day rotation working — no changes needed | — |
| `indian_holidays.py` | current | ✅ GitHub | NSE API + fallback — no changes needed | — |
| `requirements.txt` | v2.3 | ✅ GitHub | google-genai added for Gemini 2.5 + Veo 2 | `1yrQgpnrnZ6rCXIko6gYx5J9hR4p1dhHu` |
| `trading_bot.py` | v15.0 | ✅ GitHub | Fully operational | — |

### Workflow Files

| File | Version | Status | Key Changes |
|------|---------|--------|-------------|
| `daily-morning-reel.yml` | v2.2 | ✅ GitHub | 7 days/week (was Mon-Fri only) | 
| `daily-videos.yml` | v2.2 | ✅ GitHub | 10 AM IST (was 8 AM — conflicted with HerooQuest) + generate_analysis removed |
| `daily-shorts.yml` | v2.1 | ✅ GitHub | All 4 AI keys passed (was only GROQ) |
| `daily_reel.yml` | current | ✅ GitHub | No changes needed |
| `daily-articles.yml` | current | ✅ GitHub | No changes needed |
| `kids-daily.yml` | v2.1 | ✅ GitHub | KIDS_OUTPUT added + 3 separate jobs |
| `token_refresh.yml` | v2.2 | ✅ GitHub | 1st + 15th every month (was 1st + 20th) |
| `trading_bot.yml` | fixed | ✅ GitHub | TELEGRAM_BOT_TOKEN + CHAT_ID_BASIC |
| `keepalive.yml` | current | ✅ GitHub | Prevents repo from going inactive |
| `_config.yml` | cleaned | ✅ GitHub | Exclude list cleaned |

---

# APPSCRIPT — TRADING SYSTEM

```
Current version: v15.6 (pushed 19 May 2026)
Location: Google Sheets → Extensions → Apps Script
NOT in GitHub — must be shared directly by owner
Drive backup: 1cBimCblQZ_tISDxXZ_rqTlogPS4Ty17h

v15.6 CHANGES (performance fixes from real trade data):
  FIX 1: HARD BEARISH BLOCK
    When Nifty < 20DMA → max 3 WAITING slots, score ≥40 only
    Before: entered 5-8 trades in bearish → all hit SL
    After: blocks weak entries → win rate 43% → 65%+ expected

  FIX 2: MOMENTUM BREAKOUT DETECTION
    New entry type for IT-style moves (TECHM +4.85%, PERSISTENT +5.48%)
    Old: SMA=Sideways → blocked always
    New: SMA=Sideways + today +3%+ + sector momentum = valid entry

  FIX 3: OPTIONS ATH BLOCK
    MCX near ATH was getting BUY CE signal — wrong
    Now: if stock within 3% of ATH → options = ⏸ NEAR ATH

  FIX 4: VOLUME BYPASS FOR STRONG MOVERS
    Stock up 3%+ today → volume formula is stale → bypass gate 7
    Fixes IT stocks invisible problem

  FIX 5: SECTOR MOMENTUM DETECTION
    Counts stocks up 2%+ per sector
    3+ stocks = sector momentum day → unlocks that sector

  FIX 6 (v15.5): OPTIONS ROW MISMATCH
    sheetRow = rowIdx + tradedCount + 2 (was rowIdx + 2)
    Options now show in correct WAITING rows not TRADED rows

Trigger: Every 5 minutes via time-based trigger
Manual: 🔄 MANUAL SYNC button in Sheet menu
```

---

# PLATFORMS STATUS

| Platform | Channel | Status | Notes |
|---|---|---|---|
| YouTube Hindi | AI360 Trading | ✅ Auto | Education 17-21 min daily |
| YouTube Kids | HerooQuest | ✅ Auto | 3 videos/day, thumbnails working |
| YouTube English | AI360 Trading | 🔄 Phase 3 | Needs YOUTUBE_CREDENTIALS_EN |
| YouTube Kids EN | HerooQuest EN | 🔄 Phase 3 | Needs YOUTUBE_CREDENTIALS_KIDS_EN |
| Facebook AI360 | AI360 Trading | ✅ Fixed | App Live + page token + fresh token |
| Facebook HerooQuest | HerooQuest | ✅ Auto | Reel published confirmed |
| Facebook Group | AI360 Community | ❌ Manual | Needs Advanced Access |
| GitHub Pages | ai360trading.in | ✅ Auto | 4 articles/day |
| Telegram Basic | @ai360trading | ✅ Auto | 3 channels active |

---

# GITHUB SECRETS

```
Required secrets (all must be set):

META_ACCESS_TOKEN          ← Updated 18 May 2026 (60-day, 8 permissions)
META_ACCESS_TOKEN_KIDS     ← HerooQuest Facebook page token
META_APP_ID                ← Facebook App ID
META_APP_SECRET            ← Facebook App Secret
FACEBOOK_PAGE_ID           ← 108076910943724 (AI360 Trading page)
FACEBOOK_KIDS_PAGE_ID      ← 1021152881090398 (HerooQuest page)
YOUTUBE_CREDENTIALS        ← AI360 Trading YouTube OAuth
YOUTUBE_CREDENTIALS_KIDS   ← HerooQuest YouTube OAuth
YOUTUBE_CREDENTIALS_EN     ← ⏳ Pending (Phase 3)
YOUTUBE_CREDENTIALS_KIDS_EN ← ⏳ Pending (Phase 3)
GROQ_API_KEY               ← Primary AI (100k tokens/day free)
GEMINI_API_KEY             ← Gemini 2.5 Flash + image generation
ANTHROPIC_API_KEY          ← Claude fallback
OPENAI_API_KEY             ← DALL-E + GPT fallback
HF_TOKEN                   ← HuggingFace FLUX.1 image generation
TELEGRAM_BOT_TOKEN         ← Bot for all Telegram alerts
CHAT_ID_BASIC              ← Basic channel ID
CHAT_ID_ADVANCE            ← Advance channel ID
CHAT_ID_PREMIUM            ← Premium channel ID
GH_TOKEN                   ← GitHub API for secret updates

Token refresh: Automatic every 14 days (1st + 15th of month)
Next META token expiry: ~July 2026
```

---

# AI CLIENT — FALLBACK CHAIN

```
ai_client.py v2.4 — Priority order:

TEXT GENERATION:
  1. Groq — llama-3.3-70b-versatile (100k/day free) ← primary
  2. Groq — llama-3.1-8b-instant (faster fallback)
  3. Groq — gemma2-9b-it
  4. Groq — qwen-qwq-32b
  5. Gemini — gemini-2.5-flash
  6. Gemini — gemini-2.5-flash-8b
  7. Anthropic — claude-3-haiku-20240307
  8. OpenAI — gpt-4o-mini
  All free tier. Cost = Rs.0

IMAGE GENERATION (for kids video):
  1. Gemini 2.5 Flash Image (50/day free quota)
  2. Pollinations.ai FLUX Pro (FREE, no API key, Pixar quality)
  3. HuggingFace FLUX.1-schnell (free with HF_TOKEN)
  4. DALL-E 2 (OpenAI credits)
  5. PIL placeholder with Heroo character overlay

VIDEO GENERATION:
  Currently: Ken Burns zoom on Pixar images = looks like animated video
  Future: Kling AI $6/month when first revenue arrives
```

---

# THUMBNAIL PHILOSOPHY (CRITICAL)

```
The thumbnail IS the content preview.
Viewer scrolls → sees thumbnail → READS text → curious → clicks → watches.

This is why win rate matters:
  Generic thumbnail = 0.6% CTR (HerooQuest before fix)
  Story-specific thumbnail = 3%+ CTR target

PROVEN FORMULA (from competitor research):

For HerooQuest:
  Background: Dramatic scene image (60% dark overlay)
  Left: Story title HUGE yellow 110px (e.g. "GURU NANAK" not "HEROO KI KAHANI")
  Left: Moral strip with yellow left bar (curiosity gap)
  Right: Heroo character 92% height (emotional connection)
  Top left: HerooQuest brand pill (red)
  Top right: "Ep N" badge (yellow)

For Morning Reel:
  Background: Dark gradient
  Text: "MORNING BRIEF" 120px yellow
  Badge: "📈 BULLISH DAY" or "📉 BEARISH DAY" (sentiment colour)
  Number: "NIFTY 23643" visible (specific data = viewer stops)
  Character: ZENO with matching emotion
  Time: "7:00 AM IST"

For ZENO Shorts:
  ZENO character 60% height
  Topic text LARGE bold
  Lesson subtitle readable in 2 seconds
  ✅ Already working well — 10-19 views per short
```

---

# SEO RULES (CRITICAL)

```
HerooQuest title format:
  "{Story Name} | Heroo Ki Kahani | HerooQuest | Hindi Moral Story 2026"
  NOT: "HerooQuest — Heroo Ki Kahani | Kids Stories" (generic every day)

HerooQuest tags (30 tags):
  Brand: HerooQuest, HerooKiKahani, HerooStories
  Genre: KidsStories, MoralStories, AnimatedStories, BedtimeStories
  Language: HindiKahani, HindiCartoon, CartoonInHindi, BachonKiKahani
  Search: BalKahani, HindiStories, KidsVideoHindi, MoralKahani
  Platform: YouTubeKids, KidsShorts
  Year: MoralStory2026

Description rules:
  First 100 chars = CTA (what YouTube shows in search)
  Include timestamps/chapters for videos > 5 min
  15 hashtags at bottom
  Website link + channel subscribe link

Morning Reel title:
  Include sentiment + Nifty level + date
  e.g. "Nifty 23643 BULLISH — 19 May | Morning Brief | AI360Trading #Shorts"

Education title:
  "Stock Market Kya Hai? | Beginners Guide 2026 | Week 1 Hindi | AI360Trading"
```

---

# TRADING SYSTEM STATUS (as of 19 May 2026)

```
Market regime: BEARISH (Nifty 23,649 < 20DMA 24,011)
Paper trades: 3W/4L | Net +₹414 | Win rate 43%

Active positions:
  ONGC     → Entry 298.35 | SL 293.45 | 5 days
  BHEL     → Entry 396.95 | SL 396.95 | 5 days
  NESTLEIND → Entry 1,458.70 | SL 1,415.7 | 3 days
  IDEA     → Entry 13.06 | SL 12.54 | 3 days

Options signals (v15.6 fixed):
  HINDALCO → BUY CE 1100 Jun (correct row now) ✅
  MCX     → ⏸ NEAR ATH (blocked in v15.6) ✅

v15.6 Performance targets:
  Current: 43% win rate
  Target: 65%+ win rate
  Method: Hard bearish block + momentum breakout detection

History:
  Wins: BSE +3.87% | IDEA +5.94% | ADANIPORTS +5.58% (all TARGET HIT)
  Losses: BHARATFORG/TATASTEEL/BANDHANBNK/SAIL (all TRAILING SL HIT in BEARISH market)
  Root cause of losses: Entered during BEARISH regime (Nifty < 20DMA)
  v15.6 fix: HARD BLOCK in bearish = these trades would not have entered
```

---

# KNOWN ISSUES — TRACKING

| # | Issue | Status | Fix |
|---|-------|--------|-----|
| 1 | HerooQuest old videos show "Scene 99" thumbnail | ⚪ Cannot fix retroactively | Only new uploads fixed |
| 2 | Kids video left side still shows placeholder background | ⚠️ Partial | Pollinations generates scene but PIL placeholder shows on left |
| 3 | Education video English (YOUTUBE_CREDENTIALS_EN) | ⏳ Pending | Phase 3 |
| 4 | Facebook Group Advanced Access | ⏳ Pending | Manual application needed |
| 5 | Volume formula stale for intraday moves | ⚠️ Partial | v15.6 bypasses gate if +3% move |

---

# PENDING TASKS

### 🔴 Must Do (Trading)
```
1. Paper trade 27 more times to reach 30 total → Phase 4 live trading
   Currently: 7 completed trades (3W/4L)
   Need: 23 more paper trades
   When: After v15.6 proves 65%+ win rate for 10 consecutive trades
```

### 🟡 Important (Content)
```
2. Apply for Facebook Group Advanced Access
   URL: business.facebook.com → Settings → Advanced Access
   Needed for: posting to AI360 Community group automatically

3. Create YOUTUBE_CREDENTIALS_EN for English channel
   Needed for: Phase 3 English education videos

4. HerooQuest CTR target: 0.6% → 3%+
   Currently at ~0.6% (placeholder thumbnails)
   After v2.3 upload_kids_youtube.py: should improve significantly
```

### 🟢 Future (After First Revenue)
```
5. Kling AI $6/month → true animation for HerooQuest
6. Top up Claude credits for longer sessions
7. Phase 4: Live trading with real Rs.1000 capital
```

---

# DRIVE FILE REGISTRY

All important files saved to Google Drive for reference:

| File | Version | Drive ID |
|------|---------|----------|
| AppScript v15.6 | Trading | `1cBimCblQZ_tISDxXZ_rqTlogPS4Ty17h` |
| AppScript v15.5 | Previous | `1azwDcNDX-GjqxeLlM2S40X78HdYOGZQr` |
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
| daily-shorts.yml | v2.1 | `1zvjg276uZyzZ6Rvi8feOW0Z2M335DEBy` |
| kids-daily.yml | v2.1 | `14Itk-_BWJ8MecS0sAEZWbI3Rvhp_1t5f` |
| token_refresh.yml | v2.2 | `1M_rUNxepr2ZIMBGwCqxfb4gTYtR3_VYg` |
| _config.yml | cleaned | `1iVwSvNtEzbAbH7hTSDXBtSb7hTWud0It` |
| SYSTEM.md | v16.3 | `(this file)` |

---

# SESSION LOG

## 19 May 2026 — Full Day Session

### Problems Fixed
1. **Facebook token expired** — regenerated manually, token_refresh.yml schedule fixed to 1st+15th
2. **Options row mismatch** — v15.5 fix: tradedCount offset in _writeOptionsColumns()
3. **IT stocks invisible** — v15.6: momentum breakout detection + sector momentum
4. **Bearish market losses** — v15.6: hard bearish block (max 3 slots, score ≥40)
5. **MCX options near ATH** — v15.6: 3% ATH buffer check in options engine
6. **Volume formula stale** — v15.6: bypass gate 7 when price +3%+ today
7. **HerooQuest "Scene 4" thumbnail** — upload_kids_youtube.py v2.2: thumbnails().set() added
8. **Thumbnail generic every day** — v2.3: story-specific title e.g. "GURU NANAK" not "HEROO KI KAHANI"
9. **SEO weak** — upload_kids_youtube.py v2.3: 30 tags + chapters + 15 hashtags + CTA first line
10. **Education workflow runner conflict** — daily-videos.yml v2.2: moved to 10 AM (was 8 AM)
11. **Weekend content missing** — daily-morning-reel.yml v2.2: now 7 days/week
12. **generate_analysis.py called** — removed from daily-videos.yml (file was deleted)
13. **CHAT_ID_BASIC missing** — token_refresh.py v2.1: fixed from TELEGRAM_CHAT_ID
14. **bgmusic causing Meta muting** — generate_shorts.py v3.1: music completely removed
15. **Meta date format mismatch** — generate_kids_video.py v2.3: unified %Y%m%d format

### Performance Analysis Findings
```
Root cause of 43% win rate:
  ALL 4 losses (BHARATFORG, TATASTEEL, BANDHANBNK, SAIL) entered in BEARISH market
  System was running at full capacity even when Nifty below 20DMA
  
What institutions do differently:
  1. 0 new entries when index < 20DMA
  2. Sector rotation scanning (IT was running, system missed it)
  3. Relative volume (stale formula was blocking breakouts)
  4. Concentrate positions (3 good trades vs 8 mediocre ones)
  
v15.6 implements all 4 fixes above
```

## 18 May 2026 — Previous Session Summary
```
Facebook App switched to Live mode
Token regenerated with 8 permissions
Background music removed from all generators
HerooQuest upload confirmed working: gaWKA0x-t9U
Morning reel YouTube + Facebook working
Kids video: 10 scenes generating correctly
```
