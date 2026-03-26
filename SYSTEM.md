# AI360Trading — Complete System Documentation
> Last updated: March 2026 (Updated by Claude — full system review session)
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
| `generate_analysis.py` | Part 1: 8-slide market analysis video + YouTube upload | `daily-videos.yml` |
| `generate_education.py` | Part 2: Education video + YouTube upload + links Part 1 | `daily-videos.yml` |
| `generate_shorts.py` | Short 2 (trade setup) + Short 3 (market pulse) | `daily-shorts.yml` |
| `generate_articles.py` | 4 daily market articles pushed to `_posts/` | `daily-articles.yml` |
| `generate_reel.py` | ZENO 60s Hinglish moral reel with 3D Disney effect + Groq | `daily_reel.yml` |
| `upload_youtube.py` | Uploads ZENO reel to YouTube Shorts | `daily_reel.yml` |
| `upload_facebook.py` | Uploads ZENO reel video to Facebook Page + posts articles | `daily_reel.yml` |
| `upload_instagram.py` | Saves Instagram caption to artifact for manual posting | `daily_reel.yml` |
| `content_calendar.py` | Weekly education topic rotation (Mon–Fri topics) | `generate_education.py` |
| `requirements.txt` | Python dependencies for all scripts | all workflows |
| `SYSTEM.md` | This file — complete system documentation | humans + AI |

### Do NOT delete
- `content_calendar.py` — `generate_education.py` imports it directly
- `requirements.txt` — all workflows depend on it
- `public/image/` — ZENO character images used by `generate_reel.py`
- `public/music/` — background music files (bgmusic1.mp3, bgmusic2.mp3, bgmusic3.mp3)
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
- **Weekday cron:** `0 2 * * 1-5` = 7:30 AM IST Mon–Fri
- **Weekend cron:** `0 4 * * 6,0` = 9:30 AM IST Sat–Sun
- **Sequence:**
  1. `generate_analysis.py` → 8-slide market video → uploads to YouTube → saves `output/analysis_video_id.txt` + `output/analysis_meta_{today}.json`
  2. `generate_education.py` → education video → uploads to YouTube → links back to Part 1 → saves `output/education_video_id.txt` + `output/education_meta_{today}.json`
  3. Facebook share step → reads both meta JSONs → posts video links to Page + Group
- **Weekend mode:** Evergreen educational content — no live market data
- **Timeout:** 90 minutes
- **Cleanup:** Removes temp PNGs/MP3s only — keeps video ID files for shorts

### `daily-shorts.yml` — Two YouTube Shorts (Short 2 + Short 3)
- **Weekday cron:** `0 6 * * 1-5` = 11:30 AM IST Mon–Fri
- **Weekend cron:** `0 8 * * 6,0` = 1:30 PM IST Sat–Sun
- **Runs after:** `daily-videos.yml` so `output/analysis_video_id.txt` exists
- **Sequence:**
  1. Fetch live market data (Nifty, BTC, Gold, S&P500, USD/INR via yfinance)
  2. Short 2 — trade setup vertical card + `hi-IN-MadhurNeural` voice → upload YouTube Shorts
  3. Short 3 — market pulse vertical card + `hi-IN-SwaraNeural` voice → upload YouTube Shorts
  4. Facebook share → both short links posted to Page + Group
- **No ZENO in shorts** — professional card design only
- **Timeout:** 30 minutes

### `daily-articles.yml` — 4 Articles
- **Weekday cron:** `30 4 * * 1-5` = 10:00 AM IST Mon–Fri
- **Weekend cron:** `0 6 * * 6,0` = 11:30 AM IST Sat–Sun
- **Sequence:**
  1. `generate_articles.py` → pushes articles to `_posts/` folder
  2. Git commit + push to master
  3. Facebook share step → posts article links to Page + Group
- **Weekend mode:** Educational/beginner topics instead of market analysis

### `daily_reel.yml` — ZENO Reel (Short 1)
- **Daily cron:** `0 15 * * *` = 8:30 PM IST every day (best time for global audience)
- **Sequence:**
  1. `generate_reel.py` → Groq script → edge-tts voice → 3D Disney ZENO reel → saves `output/reel_{today}.mp4` + `output/final_zeno_reel.mp4` + `output/meta_{today}.json`
  2. `upload_youtube.py` → uploads to YouTube Shorts
  3. `upload_facebook.py` → uploads reel to Facebook Page + posts articles
  4. `upload_instagram.py` → saves caption to `output/instagram_caption.txt`
  5. Artifact upload → `reel_*.mp4` + `meta_*.json` downloadable from Actions UI
- **Weekend mode:** Emotional/life lesson topics, no market data
- **Timeout:** 45 minutes

### `keepalive.yml` — Repository Keepalive
- **Cron:** `30 18 * * 0-4` = 11:59 PM IST Sun–Thu
- Prevents GitHub from disabling scheduled workflows on inactive repos

---

## 4. Content Schedule

### Monday to Friday (market days)
| Time IST | Workflow | Content | Posts to |
|---|---|---|---|
| 7:30 AM | daily-videos | Part 1: Market analysis video ~12 min | YouTube |
| 7:45 AM | daily-videos | Part 2: Education video ~12 min | YouTube |
| 8:00 AM | daily-videos | Both video links shared | Facebook Page + Group |
| 10:00 AM | daily-articles | 4 market articles + Facebook share | Website + Facebook |
| 11:30 AM | daily-shorts | Short 2: Trade setup + Short 3: Market pulse | YouTube Shorts + Facebook |
| 8:30 PM | daily_reel | Short 1: ZENO 60s moral reel | YouTube Shorts + Facebook + Instagram caption |

### Saturday and Sunday (market closed)
| Time IST | Workflow | Content |
|---|---|---|
| 9:30 AM | daily-videos | Educational videos — no live market data |
| 11:30 AM | daily-articles | Educational/beginner articles |
| 1:30 PM | daily-shorts | Short 2 + Short 3: Educational market content |
| 8:30 PM | daily_reel | Short 1: Emotional/life lesson ZENO reel |

### Daily content totals
- 2 full YouTube videos
- 3 YouTube Shorts
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
| `GCP_SERVICE_ACCOUNT_JSON` | Google Cloud service account for Sheets access + Google Indexing API | main.yml, generate_articles.py |
| `DHAN_API_KEY` | Dhan broker API key | trading_bot.py |
| `DHAN_API_SECRET` | Dhan broker secret | trading_bot.py |
| `DHAN_CLIENT_ID` | Dhan client ID | trading_bot.py |
| `DHAN_PIN` | Dhan PIN | trading_bot.py |
| `DHAN_TOTP_KEY` | Dhan TOTP key | trading_bot.py |

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

### ZENO is ONLY used in generate_reel.py
- **NOT in generate_shorts.py** — shorts are professional market data cards
- **NOT in generate_education.py** — education videos are slide-based
- **NOT in generate_analysis.py** — analysis videos are professional slides

### 3D Disney Effect (generate_reel.py)
- ZENO scaled to 85% screen width for hero impact
- GaussianBlur shadow layer for 3D depth effect
- Single emotion per reel matching Groq script sentiment
- Cinematic dark blue gradient background

### Background Music (public/music/)
Day-based rotation used by generate_reel.py, generate_analysis.py, generate_education.py, generate_shorts.py:
- Mon/Thu → bgmusic1.mp3
- Tue/Fri → bgmusic2.mp3
- Wed/Sat → bgmusic3.mp3
- Sun → bgmusic1.mp3
- Volume: 7-8% so voice is always clear

---

## 7. Output Files — What Each Script Saves

### generate_reel.py saves:
- `output/final_zeno_reel.mp4` — upload_youtube.py reads this
- `output/reel_{YYYYMMDD}.mp4` — upload_facebook.py reads this (glob: reel_*.mp4)
- `output/meta_{YYYYMMDD}.json` — upload_facebook.py + upload_instagram.py read this

### meta_{today}.json fields:
```json
{
  "title": "ZENO Ki Baat - TITLE",
  "description": "...",
  "sentiment": "fearful/positive/neutral/etc",
  "hashtags": "#ZenoKiBaat ...",
  "public_video_url": ""
}
```

### generate_analysis.py saves:
- `output/analysis_video.mp4`
- `output/analysis_video_id.txt` — generate_education.py + generate_shorts.py read this
- `output/analysis_meta_{YYYYMMDD}.json` — daily-videos.yml Facebook step reads this

### generate_education.py saves:
- `output/education_video.mp4`
- `output/education_video_id.txt`
- `output/education_meta_{YYYYMMDD}.json` — daily-videos.yml Facebook step reads this

### generate_shorts.py saves:
- `output/short2_{YYYYMMDD}.mp4`
- `output/short3_{YYYYMMDD}.mp4`

---

## 8. Voice System

| Script | Voice | Style |
|---|---|---|
| `generate_reel.py` | `hi-IN-SwaraNeural` | Female Hinglish — warm kid-friendly |
| `generate_analysis.py` | `hi-IN-SwaraNeural` | Female Hinglish — market analysis |
| `generate_education.py` | `hi-IN-SwaraNeural` | Female Hinglish — education |
| `generate_shorts.py` Short 2 | `hi-IN-MadhurNeural` | Male Hinglish — authoritative trade setup |
| `generate_shorts.py` Short 3 | `hi-IN-SwaraNeural` | Female Hinglish — energetic market pulse |

---

## 9. Known Fixes Applied

| Fix | Where | Why |
|---|---|---|
| `PIL.Image.ANTIALIAS = PIL.Image.LANCZOS` | all generate scripts | Pillow 10+ removed ANTIALIAS |
| `imageio==2.9.0` pinned | requirements.txt | moviepy 1.0.3 breaks with newer imageio |
| `decorator==4.4.2` pinned | requirements.txt | moviepy 1.0.3 breaks with newer decorator |
| `Pillow>=10.3.0` | requirements.txt | Old Pillow==9.5.0 was breaking LANCZOS fix |
| ImageMagick policy fix | all workflows | TextClip fails without this |
| `YOUTUBE_CREDENTIALS` single JSON | all upload scripts | Repo uses one JSON not 3 separate keys |
| `TELEGRAM_CHAT_ID` not `TELEGRAM_ADMIN_CHAT_ID` | main.yml | Match actual secret name in repo |
| `meta_{today}.json` saved by generate_reel.py | generate_reel.py | upload_facebook + upload_instagram were failing — no meta file |
| `reel_{today}.mp4` saved by generate_reel.py | generate_reel.py | upload_facebook glob reel_*.mp4 was failing |
| YouTube upload inside generate scripts | generate_analysis.py, generate_education.py | analysis_video_id.txt now saved immediately after upload |
| ZENO removed from generate_education.py | generate_education.py | ZENO is only for reels — education uses slides |
| Facebook share step implemented | daily-videos.yml | Was placeholder comment before — now fully working |
| Output cleanup fixed | daily-videos.yml | Now only removes temp files — keeps video ID for shorts |
| daily_reel.yml schedule fixed | daily_reel.yml | Was running twice daily — now once at 8:30 PM IST |

---

## 10. Platform Details

### YouTube
- Short 1 (ZENO reel) → **Shorts** (vertical 1080x1920, ~60s)
- Short 2 (trade setup) → **Shorts** (vertical 1080x1920, ~45s)
- Short 3 (market pulse) → **Shorts** (vertical 1080x1920, ~35s)
- Analysis video → **regular video** (horizontal 1920x1080, ~12 min)
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
- Google Indexing API: new articles submitted immediately after publish

---

## 11. Monetization Status and Roadmap

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

## 12. Future Roadmap (Phase 3+)

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

## 13. Quick Reference — All Cron Times

| Cron expression | UTC | IST | Days | Workflow |
|---|---|---|---|---|
| `0 2 * * 1-5` | 02:00 | 7:30 AM | Mon-Fri | daily-videos (analysis + education) |
| `0 4 * * 6,0` | 04:00 | 9:30 AM | Sat-Sun | daily-videos (educational) |
| `30 4 * * 1-5` | 04:30 | 10:00 AM | Mon-Fri | daily-articles |
| `0 6 * * 6,0` | 06:00 | 11:30 AM | Sat-Sun | daily-articles (educational) |
| `0 6 * * 1-5` | 06:00 | 11:30 AM | Mon-Fri | daily-shorts (Short 2 + Short 3) |
| `0 8 * * 6,0` | 08:00 | 1:30 PM | Sat-Sun | daily-shorts (educational) |
| `0 15 * * *` | 15:00 | 8:30 PM | Every day | daily_reel (ZENO Short 1) |
| `30 18 * * 0-4` | 18:30 | 11:59 PM | Sun-Thu | keepalive |
| `*/5 2-10 * * 1-5` | every 5 min | 8:15-4:30 IST | Mon-Fri | AlgoTradeBot |

---

## 14. How to Test Each Workflow

1. Go to GitHub repo → Actions tab
2. Click workflow name on left sidebar
3. Click "Run workflow" → branch: master → Run workflow
4. Watch steps live — green = success, red = error
5. Click any red step → expand logs → find error message

### Recommended test order (first time or after changes)
1. `daily_reel.yml` — simplest, tests ZENO + YouTube + Facebook + meta fix
2. `daily-shorts.yml` — tests Short 2 + Short 3 market data
3. `daily-articles.yml` — tests article generation + Facebook share
4. `daily-videos.yml` — longest (~30 min), test last
5. `main.yml` (AlgoTradeBot) — already running, do not break

### What to check in logs
- generate_reel.py: `✅ Meta saved: meta_YYYYMMDD.json` + `✅ Video saved`
- upload_youtube.py: `✅ Success! Video ID: xxxxx`
- upload_facebook.py: `✅ Facebook Reel Published!`
- upload_instagram.py: `✅ Caption saved for manual use`

---

## 15. How to Use This File with Any AI Assistant

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
*Last full system review: March 2026 — all files checked and fixed by Claude.*
