# AI360Trading — Complete System Documentation
> Last updated: March 2026
> Read this file before making ANY changes to this project.

---

## 1. Project Overview

AI360Trading is a **fully automated content + trading signal system** running on GitHub Actions (free, public repo = unlimited minutes).

**What it does every day — automatically:**
- Posts stock buy/sell signals to Telegram (trading bot)
- Creates and uploads 2 YouTube full videos (market analysis + education)
- Creates and uploads 3 YouTube Shorts (ZENO reel + trade setup + market pulse)
- Writes and publishes 4 articles to website
- Shares all content links to Facebook Page + Group
- Sends Instagram caption file for manual posting

**Total daily content: 9 pieces — fully automatic**
**Only manual task:** Instagram Reels posting (~30 seconds/day)

---

## 2. Complete File Map

### Root files
| File | Purpose | Called by |
|---|---|---|
| `trading_bot.py` | Stock signal scanner — Nifty200 stocks | `main.yml` |
| `generate_analysis.py` | Part 1: 12-slide market analysis video (~15 min) | `daily-videos.yml` |
| `generate_education.py` | Part 2: Education video (~12 min) | `daily-videos.yml` |
| `generate_shorts.py` | Short 2 (trade setup) + Short 3 (market pulse) | `daily-shorts.yml` |
| `generate_articles.py` | 4 daily market articles pushed to `_posts/` | `daily-articles.yml` |
| `generate_reel.py` | ZENO 60s Hinglish moral reel with Ken Burns effect | `daily_reel.yml` |
| `upload_youtube.py` | Uploads ZENO reel to YouTube Shorts | `daily_reel.yml` |
| `upload_facebook.py` | Uploads ZENO reel video to Facebook Page | `daily_reel.yml` |
| `upload_instagram.py` | Saves Instagram caption to artifact for manual posting | `daily_reel.yml` |
| `content_calendar.py` | Weekly education topic rotation (Mon–Fri topics) | `generate_education.py` |
| `requirements.txt` | Python dependencies for all scripts | all workflows |
| `SYSTEM.md` | This file — complete system documentation | humans + AI |

### Do NOT delete
- `content_calendar.py` — `generate_education.py` imports it directly
- `requirements.txt` — all workflows depend on it
- `public/image/` — ZENO character images used by `generate_reel.py` and `generate_shorts.py`
- `SYSTEM.md` — project memory for AI assistants and developers

---

## 3. Workflows (`.github/workflows/`)

### `main.yml` — AlgoTradeBot
- **Runs:** Every 5 min, 8:15 AM–4:30 PM IST, Mon–Fri
- **Also:** 8:45 AM backup, 12:28 PM backup, 3:15 PM backup
- **Does:** Runs `trading_bot.py` — scans Google Sheets, sends Telegram signals
- **Posts to:** Telegram (3 channels: free, advance, premium)
- **Timeout:** 4 minutes per run

### `daily-videos.yml` — Two YouTube Videos
- **Weekday cron:** `30 0 * * 1-5` = 6:00 AM IST Mon–Fri
- **Weekend cron:** `30 3 * * 6,0` = 9:00 AM IST Sat–Sun
- **Sequence:**
  1. `generate_analysis.py` → 12-slide market video → uploads to YouTube → saves `output/analysis_video_id.txt`
  2. `generate_education.py` → education video → uploads to YouTube → links back to Part 1 → saves `output/education_video_id.txt`
  3. Facebook share step → posts both video links to Page + Group
- **Weekend mode:** No live market data — evergreen educational content
- **Timeout:** 90 minutes

### `daily-shorts.yml` — Two YouTube Shorts (Short 2 + Short 3)
- **Weekday cron:** `0 6 * * 1-5` = 11:30 AM IST Mon–Fri
- **Weekend cron:** `0 8 * * 6,0` = 1:30 PM IST Sat–Sun
- **Runs after:** `daily-videos.yml` so `output/analysis_video_id.txt` exists
- **Sequence:**
  1. Fetch live market data (Nifty, BTC, Gold, S&P500, USD/INR)
  2. Short 2 — trade setup vertical card + Hinglish voice → upload YouTube Shorts
  3. Short 3 — market pulse vertical card + Hinglish voice → upload YouTube Shorts
  4. Facebook share → both short links posted to Page + Group
- **Timeout:** 30 minutes

### `daily-articles.yml` — 4 Articles
- **Weekday cron:** `45 1 * * 1-5` = 7:15 AM IST Mon–Fri
- **Weekend cron:** `30 4 * * 6,0` = 10:00 AM IST Sat–Sun
- **Sequence:**
  1. `generate_articles.py` → pushes articles to `_posts/` folder
  2. Facebook share step → posts article links to Page + Group
- **Weekend mode:** Educational/beginner topics instead of market analysis

### `daily_reel.yml` — ZENO Reel (Short 1)
- **Weekday cron:** `0 3 * * 1-5` = 8:30 AM IST Mon–Fri
- **Weekend cron:** `30 5 * * 6,0` = 11:00 AM IST Sat–Sun
- **Sequence:**
  1. `generate_reel.py` → Groq script → edge-tts voice → Ken Burns video → saves `output/reel_YYYYMMDD.mp4`
  2. `upload_youtube.py` → uploads to YouTube Shorts
  3. `upload_facebook.py` → uploads reel to Facebook Page
  4. `upload_instagram.py` → saves caption to `output/instagram_caption.txt`
  5. Artifact upload → `reel_*.mp4` + `instagram_caption.txt` downloadable from Actions UI
- **Weekend mode:** Emotional/life lesson topics, no market data
- **Timeout:** 45 minutes

### `keepalive.yml` — Repository Keepalive
- Prevents GitHub from disabling scheduled workflows on inactive repos

---

## 4. Content Schedule

### Monday to Friday (market days)
| Time IST | Workflow | Content | Posts to |
|---|---|---|---|
| 6:00 AM | daily-videos | Part 1: Market analysis video ~15 min | YouTube |
| 6:20 AM | daily-videos | Part 2: Education video ~12 min | YouTube |
| 6:35 AM | daily-videos | Both video links shared | Facebook Page + Group |
| 7:15 AM | daily-articles | 4 market articles + Facebook share | Website + Facebook |
| 8:30 AM | daily_reel | Short 1: ZENO 60s moral reel | YouTube Shorts + Facebook + Instagram caption |
| 11:30 AM | daily-shorts | Short 2: Trade setup clip + Short 3: Market pulse | YouTube Shorts + Facebook |

### Saturday and Sunday (market closed)
| Time IST | Workflow | Content |
|---|---|---|
| 9:00 AM | daily-videos | Educational videos — no live market data |
| 10:00 AM | daily-articles | Educational/beginner articles |
| 11:00 AM | daily_reel | Short 1: Emotional/life lesson ZENO reel |
| 1:30 PM | daily-shorts | Short 2 + Short 3: Educational market content |

### Daily content totals
- 2 full YouTube videos (~27 min total)
- 3 YouTube Shorts (~2.5 min total)
- 4 website articles
- 5 Facebook posts (2 video links + 1 article + 1 reel + 1 shorts)
- 1 Instagram caption (manual posting)
- Stock signals every 5 min on Telegram (market hours)

### Education topic rotation (content_calendar.py)
| Day | Topic category |
|---|---|
| Monday | Options and Derivatives |
| Tuesday | Technical Analysis |
| Wednesday | Global Macro + Fundamentals |
| Thursday | Trading Strategies |
| Friday | Psychology + Risk Management |
| Weekend | Rotates from Monday topics |

---

## 5. GitHub Secrets

| Secret name | What it is | Used by |
|---|---|---|
| `GROQ_API_KEY` | Groq API key (free) — generates all scripts | all generate scripts |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth2 JSON (client_id, client_secret, refresh_token) | upload_youtube.py, generate_analysis.py, generate_education.py, generate_shorts.py |
| `META_ACCESS_TOKEN` | Facebook long-lived page token — expires every 60 days | upload_facebook.py, daily-videos.yml, daily-articles.yml, daily-shorts.yml |
| `FACEBOOK_PAGE_ID` | Numeric page ID — permanent, never changes | upload_facebook.py, daily-videos.yml, daily-articles.yml, daily-shorts.yml |
| `FACEBOOK_GROUP_ID` | Numeric group ID — permanent, never changes | upload_facebook.py, daily-videos.yml, daily-articles.yml, daily-shorts.yml |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business account ID | upload_instagram.py |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | main.yml (trading bot) |
| `TELEGRAM_CHAT_ID` | Free channel ID (ai360trading) | main.yml |
| `CHAT_ID_ADVANCE` | Advance channel ID (Rs499/month) | main.yml |
| `CHAT_ID_PREMIUM` | Premium bundle channel ID | main.yml |
| `GCP_SERVICE_ACCOUNT_JSON` | Google Cloud service account for Sheets access | main.yml (trading bot) |
| `DHAN_API_KEY` | Dhan broker API key | trading_bot.py |
| `DHAN_API_SECRET` | Dhan broker secret | trading_bot.py |
| `DHAN_CLIENT_ID` | Dhan client ID | trading_bot.py |
| `DHAN_PIN` | Dhan PIN | trading_bot.py |
| `DHAN_TOTP_KEY` | Dhan TOTP key | trading_bot.py |
| `GH_TOKEN` | GitHub token for repo write access | daily-articles.yml |

### Important: META_ACCESS_TOKEN expires every 60 days
Refresh process:
1. Go to developers.facebook.com/tools/explorer
2. Select AI360Trading app → Generate Access Token
3. Open: `https://graph.facebook.com/me/accounts?access_token=NEW_TOKEN`
4. Copy the `access_token` from response
5. Update `META_ACCESS_TOKEN` secret in GitHub
6. Set phone reminder every 50 days

---

## 6. ZENO Character System

### Image files (in `public/image/`)
| Filename | Emotion | Used when |
|---|---|---|
| `zeno_happy.png` | Happy | Positive topics, bullish market |
| `zeno_celebrating.png` | Excited/celebrating | Strong positive, CTA ending |
| `zeno_thinking.png` | Curious/thinking | Educational, reflective topics |
| `zeno_sad.png` | Sad | Difficult topics, bearish market |
| `zeno_fear.png` | Worried/fear | Cautionary lessons, market fear |
| `zeno_angry.png` | Angry | Strong warning topics |
| `zeno_greed.png` | Greedy | Money/greed related topics |

### Story arc logic in generate_reel.py (3 images per reel)
Every reel uses 3 ZENO images — never random, always tells a story:
- Image 1 (hook): matches script emotion
- Image 2 (middle/lesson): related reflective emotion
- Image 3 (CTA/end): always positive — `zeno_celebrating` or `zeno_happy`

Example for sad topic: `zeno_sad → zeno_thinking → zeno_celebrating`

### ZENO in generate_shorts.py
- Short 2: uses `zeno_happy` or `zeno_celebrating` (bullish) / `zeno_sad` or `zeno_fear` (bearish)
- Short 3: same mood-based selection from `public/image/`

### Ken Burns animation (generate_reel.py only)
Each image gets smooth zoom or pan:
- Segment 1: zoom_in
- Segment 2: pan_left
- Segment 3: zoom_out

---

## 7. Pipeline Diagrams

### ZENO Reel (Short 1) Pipeline
```
GitHub Actions trigger (8:30 AM IST)
→ Weekend detection (datetime.weekday() >= 5)
→ Groq API → Hinglish script (weekday: market+moral, weekend: emotional)
→ edge-tts → Hindi voice (hi-IN-SwaraNeural)
→ select_zeno_images() → 3 images based on emotion + market mood
→ make_ken_burns() → zoom/pan effect on each image
→ moviepy → background + ZENO segments + voice + subtitles + title
→ output/reel_YYYYMMDD.mp4
→ upload_youtube.py → YouTube Shorts
→ upload_facebook.py → Facebook Page Reel
→ upload_instagram.py → saves instagram_caption.txt
```

### Shorts 2 + 3 Pipeline
```
GitHub Actions trigger (11:30 AM IST)
→ Read output/analysis_video_id.txt (link to today's Part 1)
→ fetch_market() → Nifty + BTC + Gold + S&P500 + USD/INR (Yahoo Finance)
→ Short 2:
   make_short2_frame() → vertical 1080x1920 trade setup card (PIL)
   make_short2_script() → Groq Hinglish trade setup script
   edge-tts → hi-IN-SwaraNeural voice
   moviepy → short2_YYYYMMDD.mp4
   YouTube API → upload as Short
→ Short 3:
   make_short3_frame() → vertical 1080x1920 market pulse card (PIL)
   make_short3_script() → Groq Hinglish market pulse script
   edge-tts → hi-IN-MadhurNeural voice (different voice = variety)
   moviepy → short3_YYYYMMDD.mp4
   YouTube API → upload as Short
→ Facebook → share both short links to Page + Group
```

### Analysis + Education Videos Pipeline
```
GitHub Actions trigger (6:00 AM IST)
→ generate_analysis.py:
   fetch_all() → Nifty + BankNifty + 9 global + Options + FII/DII
   Groq → 12 analysis slides JSON
   PIL → render each slide 1920x1080 PNG
   edge-tts → voice for each slide
   moviepy → analysis_video.mp4 (~15 min)
   YouTube API → upload → save analysis_video_id.txt
   PIL → custom thumbnail
→ generate_education.py:
   content_calendar.py → get today's topic
   read analysis_video_id.txt → link Part 1
   Groq → education slides JSON
   PIL → render slides
   edge-tts → voice
   moviepy → education_video.mp4 (~12 min)
   YouTube API → upload → update Part 1 with Part 2 link
→ Facebook → share both video links
```

---

## 8. Known Fixes Applied

| Fix | Where | Why |
|---|---|---|
| `PIL.Image.ANTIALIAS = PIL.Image.LANCZOS` | generate_reel.py, generate_shorts.py | Pillow 10+ removed ANTIALIAS |
| `imageio==2.9.0` pinned | requirements.txt | moviepy 1.0.3 breaks with newer imageio |
| `decorator==4.4.2` pinned | requirements.txt | moviepy 1.0.3 breaks with newer decorator |
| ImageMagick policy fix | daily_reel.yml system deps | TextClip fails without this |
| `YOUTUBE_CREDENTIALS` single JSON | upload_youtube.py, generate_shorts.py | Repo uses one JSON not 3 separate keys |
| `TELEGRAM_CHAT_ID` not `TELEGRAM_ADMIN_CHAT_ID` | all files | Match actual secret name in repo |
| `select_zeno_images` (plural) | generate_reel.py | Returns list of 3 images for Ken Burns arc |

---

## 9. Platform Details

### YouTube
- Short 1 (ZENO reel) → **Shorts** (vertical 1080x1920, ~60s)
- Short 2 (trade setup) → **Shorts** (vertical 1080x1920, ~45s)
- Short 3 (market pulse) → **Shorts** (vertical 1080x1920, ~35s)
- Analysis video → **regular video** (horizontal 1920x1080, ~15 min)
- Education video → **regular video** (horizontal 1920x1080, ~12 min)
- Channel: `@ai360trading`
- Auth: `YOUTUBE_CREDENTIALS` JSON secret (OAuth2 refresh token — never expires)

### Facebook
- Page: "Unofficial Amit Kumar" (will rename to ai360trading after followers)
- Group: `ai360trading`
- ZENO reel → uploaded as Facebook Reel via video_reels API
- Articles + video + shorts links → feed posts with link preview
- Token: `META_ACCESS_TOKEN` — expires every 60 days, must refresh manually

### Instagram
- Cannot auto-post Reels via API (Meta restriction as of 2026)
- Caption saved to `output/instagram_caption.txt` in GitHub Actions artifact
- Download artifact → copy caption → post manually (~30 seconds)

### Telegram
- 3 channels: free (ai360trading), advance (Rs499/month), premium (bundle)
- ONLY for stock buy/sell signals — not used for video/reel/article notifications
- AlgoTradeBot runs every 5 min during market hours

### Website
- URL: `https://ai360trading.in`
- Static Jekyll site on GitHub Pages
- Articles auto-pushed to `_posts/` by `generate_articles.py`
- RSS: `https://ai360trading.in/feed/`

---

## 10. Monetization Status and Roadmap

### Current status
- YouTube Partner Program: working toward 1,000 subs + 4,000 watch hours
- AdSense: not yet applied
- Facebook monetization: working toward 10,000 followers
- Paid Telegram: Rs499/month advance channel active

### Earning targets
| Milestone | Target month | Expected earning |
|---|---|---|
| AdSense approved | Month 4-6 | Rs3,000-15,000/month |
| 50 paid Telegram subs | Month 3-4 | Rs25,000/month |
| 100 paid Telegram subs | Month 5-6 | Rs50,000/month |
| Facebook monetization | Month 6-8 | Rs5,000-20,000/month |
| Live trading (Angel One) | After 30 paper trades | Variable |

---

## 11. Future Roadmap (Phase 3+)

- [ ] Twitter/X auto-post — daily Nifty + BTC + reel link
- [ ] Reddit auto-post — share articles to trading communities
- [ ] YouTube Community Posts — auto-post daily poll + Nifty levels
- [ ] Pinterest auto-pin — article links for US/Brazil/UK traffic
- [ ] Live trading via Angel One SmartAPI (after 30 paper trades validated)
- [ ] Instagram auto-posting (blocked by Meta API — check again in future)
- [ ] ZENO lip-sync animation (requires GPU — not possible on free GitHub Actions)
- [ ] Facebook Page rename to `ai360trading` (after more followers)
- [ ] META_ACCESS_TOKEN auto-refresh automation

---

## 12. Quick Reference — All Cron Times

| Cron expression | UTC | IST | Days | Workflow |
|---|---|---|---|---|
| `30 0 * * 1-5` | 00:30 | 6:00 AM | Mon-Fri | daily-videos (analysis + education) |
| `30 3 * * 6,0` | 03:30 | 9:00 AM | Sat-Sun | daily-videos (educational) |
| `45 1 * * 1-5` | 01:45 | 7:15 AM | Mon-Fri | daily-articles |
| `30 4 * * 6,0` | 04:30 | 10:00 AM | Sat-Sun | daily-articles (educational) |
| `0 3 * * 1-5` | 03:00 | 8:30 AM | Mon-Fri | daily_reel (ZENO Short 1) |
| `30 5 * * 6,0` | 05:30 | 11:00 AM | Sat-Sun | daily_reel (emotional) |
| `0 6 * * 1-5` | 06:00 | 11:30 AM | Mon-Fri | daily-shorts (Short 2 + Short 3) |
| `0 8 * * 6,0` | 08:00 | 1:30 PM | Sat-Sun | daily-shorts (educational) |
| `*/5 2-10 * * 1-5` | every 5 min | 8:15-4:30 IST | Mon-Fri | AlgoTradeBot |

---

## 13. How to Test Each Workflow

1. Go to GitHub repo → Actions tab
2. Click workflow name on left sidebar
3. Click "Run workflow" → branch: master → Run workflow
4. Watch steps live — green = success, red = error
5. Click any red step → expand logs → find error message

### Recommended test order (first time or after changes)
1. `daily_reel.yml` — simplest, tests ZENO + YouTube + Facebook
2. `daily-shorts.yml` — tests Short 2 + Short 3
3. `daily-articles.yml` — tests article generation + Facebook share
4. `daily-videos.yml` — longest (~30 min), test last
5. `main.yml` (AlgoTradeBot) — already running, do not break

---

## 14. How to Use This File with Any AI Assistant

Paste this prompt to any AI:
> "Read the SYSTEM.md file in my GitHub repo ai360trading.
> It explains the complete automation system.
> I want to [your request here].
> Make sure you don't break anything that's already working."

The AI will understand the full system instantly. Always update this file after major changes.

---

*Complete AI360Trading automation system — built with Claude AI, March 2026.*
*9 pieces of content daily. Zero cost. Fully automatic.*
*The journey from zero to earning — documented here.*
