# AI360Trading — Complete System Documentation
> Last updated: March 2026
> Read this file before making ANY changes to this project.

---

## 1. Project Overview

AI360Trading is a **fully automated content + trading signal system** running on GitHub Actions (free, public repo = unlimited minutes).

**What it does every day — automatically:**
- Posts stock buy/sell signals to Telegram (trading bot)
- Creates and uploads 2 YouTube videos (market analysis + education)
- Writes and publishes 4 articles to website
- Creates a 60-second ZENO reel and posts to YouTube Shorts + Facebook
- Shares all content links to Facebook Page + Group
- Sends Instagram caption file for manual posting

**Only manual task:** Instagram Reels posting (~30 seconds/day)

---

## 2. Complete File Map

### Root files
| File | Purpose | Called by |
|---|---|---|
| `trading_bot.py` | Stock signal scanner — Nifty200 stocks | `main.yml` |
| `generate_analysis.py` | Part 1: 12-slide market analysis video (~15 min) | `daily-videos.yml` |
| `generate_education.py` | Part 2: Education video (~12 min) | `daily-videos.yml` |
| `generate_articles.py` | 4 daily market articles pushed to `_posts/` | `daily-articles.yml` |
| `generate_reel.py` | ZENO 60s Hinglish moral reel with Ken Burns effect | `daily_reel.yml` |
| `upload_youtube.py` | Uploads ZENO reel to YouTube Shorts | `daily_reel.yml` |
| `upload_facebook.py` | Uploads ZENO reel video to Facebook Page | `daily_reel.yml` |
| `upload_instagram.py` | Saves Instagram caption to artifact for manual posting | `daily_reel.yml` |
| `content_calendar.py` | Weekly education topic rotation (Mon–Fri topics) | `generate_education.py` |
| `requirements.txt` | Python dependencies for all scripts | all workflows |

### Do NOT delete
- `content_calendar.py` — `generate_education.py` imports it directly
- `requirements.txt` — all workflows depend on it
- `public/image/` — ZENO character images used by `generate_reel.py`

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

### `daily-articles.yml` — 4 Articles
- **Weekday cron:** `45 1 * * 1-5` = 7:15 AM IST Mon–Fri
- **Weekend cron:** `30 4 * * 6,0` = 10:00 AM IST Sat–Sun
- **Sequence:**
  1. `generate_articles.py` → pushes articles to `_posts/` folder
  2. Facebook share step → posts article links to Page + Group
- **Weekend mode:** Educational/beginner topics instead of market analysis

### `daily_reel.yml` — ZENO Reel
- **Weekday cron:** `0 3 * * 1-5` = 8:30 AM IST Mon–Fri
- **Weekend cron:** `30 5 * * 6,0` = 11:00 AM IST Sat–Sun
- **Sequence:**
  1. `generate_reel.py` → Groq script → edge-tts voice → Ken Burns video → saves `output/reel_YYYYMMDD.mp4`
  2. `upload_youtube.py` → uploads to YouTube Shorts
  3. `upload_facebook.py` → uploads reel to Facebook Page
  4. `upload_instagram.py` → saves caption to `output/instagram_caption.txt`
  5. Artifact upload → `reel_*.mp4` + `instagram_caption.txt` downloadable from Actions UI
- **Weekend mode:** Emotional/life lesson topics, no market data in script or captions
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
| 8:30 AM | daily_reel | ZENO 60s Hinglish reel | YouTube Shorts + Facebook + Instagram caption |
| 8:15–4:30 PM | AlgoTradeBot | Stock signals every 5 min | Telegram (3 channels) |

### Saturday and Sunday (market closed)
| Time IST | Workflow | Content |
|---|---|---|
| 9:00 AM | daily-videos | Educational videos — no live market data |
| 10:00 AM | daily-articles | Educational/beginner articles |
| 11:00 AM | daily_reel | Emotional/life lesson ZENO reel |

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
| `GROQ_API_KEY` | Groq API key (free) — generates scripts | all generate scripts |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth2 JSON (client_id, client_secret, refresh_token) | upload_youtube.py, generate_analysis.py, generate_education.py |
| `META_ACCESS_TOKEN` | Facebook long-lived page token — expires every 60 days | upload_facebook.py, daily-videos.yml, daily-articles.yml |
| `FACEBOOK_PAGE_ID` | Numeric page ID — permanent, never changes | upload_facebook.py, daily-videos.yml, daily-articles.yml |
| `FACEBOOK_GROUP_ID` | Numeric group ID — permanent, never changes | upload_facebook.py, daily-videos.yml, daily-articles.yml |
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

### Story arc logic (3 images per reel)
Every reel uses 3 ZENO images in a story arc — never random:
- Image 1 (hook): matches script emotion
- Image 2 (middle/lesson): related reflective emotion
- Image 3 (CTA/end): always positive — `zeno_celebrating` or `zeno_happy`

Example for sad topic: `zeno_sad → zeno_thinking → zeno_celebrating`

### Ken Burns animation
Each image gets a smooth zoom or pan effect:
- Segment 1: zoom_in
- Segment 2: pan_left
- Segment 3: zoom_out

---

## 7. ZENO Reel Generation Pipeline

```
GitHub Actions trigger
       ↓
Weekend detection (datetime.weekday() >= 5)
       ↓
Groq API → Hinglish script (weekday: market+moral, weekend: pure emotional)
       ↓
edge-tts → Hindi voice (hi-IN-SwaraNeural, free forever)
       ↓
select_zeno_images() → 3 images based on emotion + market mood
       ↓
make_ken_burns() → smooth zoom/pan on each image
       ↓
moviepy → assemble: background + ZENO segments + voice + subtitles + title
       ↓
output/reel_YYYYMMDD.mp4
       ↓
upload_youtube.py → YouTube Shorts
upload_facebook.py → Facebook Page Reel
upload_instagram.py → saves caption.txt for manual posting
```

---

## 8. Video Generation Pipeline

```
generate_analysis.py:
  fetch_all() → Nifty + BankNifty + 9 global tickers + Options + FII/DII
  Groq → 12 analysis slides JSON
  PIL → render each slide as 1920x1080 PNG
  edge-tts → voice for each slide
  moviepy → concatenate all clips → analysis_video.mp4
  YouTube API → upload → save analysis_video_id.txt
  PIL → custom thumbnail

generate_education.py:
  content_calendar.py → get today's topic
  read output/analysis_video_id.txt → link Part 1 in description
  Groq → education slides JSON
  PIL → render each slide
  edge-tts → voice
  moviepy → education_video.mp4
  YouTube API → upload → update Part 1 description with Part 2 link
```

---

## 9. Known Fixes Applied

| Fix | Where | Why |
|---|---|---|
| `PIL.Image.ANTIALIAS = PIL.Image.LANCZOS` | generate_reel.py assemble_video() | Pillow 10+ removed ANTIALIAS |
| `imageio==2.9.0` pinned | requirements.txt | moviepy 1.0.3 breaks with newer imageio |
| `decorator==4.4.2` pinned | requirements.txt | moviepy 1.0.3 breaks with newer decorator |
| ImageMagick policy fix | daily_reel.yml system deps step | TextClip fails without this |
| `YOUTUBE_CREDENTIALS` single JSON secret | upload_youtube.py | Repo uses one JSON not 3 separate keys |
| `TELEGRAM_CHAT_ID` not `TELEGRAM_ADMIN_CHAT_ID` | all files | Match actual secret name in repo |

---

## 10. Platform Details

### YouTube
- ZENO reel → posted as **Shorts** (vertical 1080x1920, <60s)
- Analysis video → posted as **regular video** (horizontal 1920x1080, ~15 min)
- Education video → posted as **regular video** (horizontal 1920x1080, ~12 min)
- Channel: `@ai360trading`

### Facebook
- Page: "Unofficial Amit Kumar" (will rename to ai360trading after getting followers)
- Group: `ai360trading`
- ZENO reel → uploaded as Facebook Reel via video_reels API
- Articles + video links → posted as feed posts with link preview

### Instagram
- Account linked to Facebook Business account
- Reels cannot be auto-posted via API — manual posting required
- Caption saved to `output/instagram_caption.txt` in GitHub Actions artifact
- Download artifact → copy caption → post manually (~30 seconds)

### Telegram
- 3 channels: free (ai360trading), advance (paid Rs499), premium (bundle)
- Only for stock buy/sell signals — NOT used for reel/video/article notifications
- Bot token: `TELEGRAM_BOT_TOKEN`

---

## 11. Website

- URL: `https://ai360trading.in`
- Static Jekyll site hosted on GitHub Pages
- Articles auto-pushed to `_posts/` folder by `generate_articles.py`
- RSS feed: `https://ai360trading.in/feed/` (used by Facebook article sharing)

---

## 12. How to Test Each Workflow

1. Go to GitHub repo → Actions tab
2. Click the workflow name on left
3. Click "Run workflow" → select branch `master` → Run
4. Watch steps live — green = success, red = error
5. Click any red step to see full error logs

### Test order (first time setup):
1. `daily_reel.yml` — test ZENO reel first (simplest)
2. `daily-articles.yml` — test article generation
3. `daily-videos.yml` — test video generation (takes longest ~30 min)
4. `main.yml` — AlgoTradeBot (already running, do not break)

---

## 13. AdSense / Monetization Status

- YouTube Partner Program requires: 1,000 subscribers + 4,000 watch hours
- Posting 2 videos + 1 Short daily = fastest path to 4,000 watch hours
- AdSense not yet applied — target after hitting watch hour requirement
- Facebook monetization: available after 10,000 followers on page

---

## 14. Future Roadmap

- [ ] Live trading via Angel One SmartAPI (after 30 paper trades validated)
- [ ] MTF (Margin Trading Facility) — only after consistent live profits
- [ ] Instagram auto-posting (blocked by Meta API restrictions as of 2026)
- [ ] ZENO lip-sync animation (requires GPU — not possible on free GitHub Actions)
- [ ] Facebook Page rename to `ai360trading` (after getting more followers)
- [ ] META_ACCESS_TOKEN auto-refresh (currently manual every 60 days)

---

## 15. Quick Reference — Cron Times

| Cron | UTC time | IST time | Runs |
|---|---|---|---|
| `30 0 * * 1-5` | 00:30 UTC | 6:00 AM IST | Mon-Fri |
| `30 3 * * 6,0` | 03:30 UTC | 9:00 AM IST | Sat-Sun |
| `45 1 * * 1-5` | 01:45 UTC | 7:15 AM IST | Mon-Fri |
| `30 4 * * 6,0` | 04:30 UTC | 10:00 AM IST | Sat-Sun |
| `0 3 * * 1-5` | 03:00 UTC | 8:30 AM IST | Mon-Fri |
| `30 5 * * 6,0` | 05:30 UTC | 11:00 AM IST | Sat-Sun |
| `*/5 2-10 * * 1-5` | every 5 min | 8:15-4:30 IST | Mon-Fri |

---

*This document covers the complete AI360Trading automation system as of March 2026.*
*Always read this before making changes. Never delete content_calendar.py or requirements.txt.*
