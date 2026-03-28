# AI360Trading — Master System Documentation

**Last Updated:** March 28, 2026 — Full audit by Claude Sonnet
**Status:** Phase 2 Active (FB Group + Instagram being resolved)
**Primary Audience:** Bilingual Hindi + English — Indian retail traders + global investors

> ⚠️ **Read this file completely before making ANY changes.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT).

---

## 1. Real Mission

> This system is built to run **forever, fully automated**, generating passive income for the owner's family — even without active involvement. Built on ₹0/month infrastructure. No employees. No office. Pure automation.

### Monetisation — Every Stream Simultaneously

| Stream | Platform | High-CPM Target Countries |
|---|---|---|
| Video Ad Revenue | YouTube | USA, UK, Canada, Australia, UAE |
| Shorts / Reels Bonus | YouTube, Facebook, Instagram | USA, UK, Brazil, India |
| Website Ad Revenue | GitHub Pages (ai360trading.in) | USA, UK, Canada |
| In-Stream Video Ads | Facebook Page | USA, UK, Brazil, India |
| Paid Signal Subscriptions | Telegram (Advance + Premium channels) | India, UAE, Global |

### Target Countries by Ad CPM Priority

1. 🇺🇸 USA — Highest CPM globally for finance content
2. 🇬🇧 UK — Very high CPM, strong trading audience
3. 🇦🇺 Australia — High CPM, growing retail base
4. 🇦🇪 UAE — High CPM, large NRI + Gulf investor audience
5. 🇨🇦 Canada — High CPM, similar to USA
6. 🇧🇷 Brazil — Large audience, fast-growing finance CPM
7. 🇮🇳 India — Largest volume, Nifty/stock focus

> **AI Rule:** Always optimise content topics, hooks, SEO tags, and posting times for these countries. USA/UK prime time = 11 PM–1 AM IST. Include global keywords (`USStocks`, `UKInvesting`, `BrazilMarket`, `GlobalInvesting`) in all titles, descriptions, and tags.

---

## 2. Platform Status

| Platform | Status | Notes |
|---|---|---|
| YouTube Videos | ✅ Auto | Analysis + Education videos working |
| YouTube Shorts | ✅ Auto | Short 2 + Short 3 working |
| YouTube Reels | ✅ Auto | ZENO reel working |
| Facebook Page | ✅ Auto | Posts, reels, article shares all working |
| Facebook Group | ❌ Broken | Missing `publish_to_groups` token scope — see Section 8 |
| Instagram | ⚠️ Partial | Upload chain built; needs `INSTAGRAM_ACCOUNT_ID` secret added |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | Signal alerts to all 3 channels |

---

## 3. Content Mode System

Mode is **auto-detected** by `indian_holidays.py` at the start of every workflow and written to `$GITHUB_ENV`. All scripts read `CONTENT_MODE` environment variable — never hardcoded.

| Mode | When | Content Strategy |
|---|---|---|
| `market` | Mon–Fri (excluding Indian holidays) | Live Nifty50/Global data, trade setups, signals |
| `weekend` | Saturday–Sunday | Educational, wealth-building, global audience focus |
| `holiday` | Indian Market Holidays | Motivational, "Market band hai par seekhna chalu", holiday name shown |

**Detection logic:** `indian_holidays.py` → NSE API (primary) → hardcoded fallback dates

---

## 4. GitHub Actions Workflows

| File | Trigger (IST) | Purpose | Mode-Aware |
|---|---|---|---|
| `main.yml` | Every 5 min (market hours, Mon–Fri) | `trading_bot.py` — Nifty200 signals | ✅ Auto-skips weekends/holidays |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 (analysis) + Part 2 (education) | ✅ |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 (trade setup) + Short 3 (market pulse) | ✅ |
| `daily_reel.yml` | 8:30 PM daily | ZENO 60s Reel | ✅ Fixed March 2026 |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages | ✅ |
| `keepalive.yml` | Periodic | Prevents GitHub disabling inactive workflows | N/A |

All workflows support `workflow_dispatch` with a `content_mode` dropdown to force any mode for testing.

---

## 5. Complete File Map

### Core Content Generation

| File | Role | Key Tech | Status |
|---|---|---|---|
| `trading_bot.py` | Nifty200 buy/sell signal scanner | Dhan API, Google Sheets | ✅ |
| `generate_shorts.py` | Short 2 + Short 3 generator | yfinance fast_info, PIL, Edge-TTS, Groq | ✅ Fixed Mar 2026 |
| `generate_reel.py` | ZENO 60s reel generator | Groq, MoviePy, PIL | ✅ |
| `generate_analysis.py` | 8-slide market analysis video (Part 1) | PIL, MoviePy, Groq | ✅ |
| `generate_education.py` | Educational deep-dive video (Part 2) | content_calendar.py, Groq | ✅ |
| `generate_articles.py` | 4 SEO articles daily → Jekyll _posts | Groq | ✅ |

### Upload & Distribution

| File | Role | Status |
|---|---|---|
| `upload_youtube.py` | Uploads ZENO reel; saves `youtube_video_id` + `public_video_url` to meta | ✅ Fixed Mar 2026 |
| `upload_facebook.py` | Uploads reel to FB Page; shares link to Group; posts RSS articles | ✅ Fixed Mar 2026 |
| `upload_instagram.py` | Auto-uploads via Meta API using `public_video_url` from meta | ✅ Fixed Mar 2026 |

### Infrastructure

| File | Role |
|---|---|
| `indian_holidays.py` | Mode detection — NSE API + fallback; shared by ALL workflows |
| `content_calendar.py` | Rotates topics: Options, Technical Analysis, Psychology |

### Static Assets

| Path | Contents |
|---|---|
| `public/image/` | `zeno_happy.png`, `zeno_sad.png`, `zeno_greed.png`, `zeno_thinking.png` |
| `public/music/` | `bgmusic1.mp3`, `bgmusic2.mp3`, `bgmusic3.mp3` — rotated by weekday |

---

## 6. Critical Upload Chain

Scripts must run in this exact order. Each one feeds data to the next:

```
generate_reel.py
    └── output/reel_YYYYMMDD.mp4
    └── output/meta_YYYYMMDD.json  ← created here

upload_youtube.py
    └── Uploads reel to YouTube
    └── Writes to meta → youtube_video_id, youtube_video_url, public_video_url
    └── output/youtube_video_id.txt

upload_facebook.py
    └── Uploads reel to Facebook Page (3-phase upload)
    └── Posts link message to Facebook Group
    └── Overwrites meta → public_video_url (Facebook watch URL)
    └── Posts articles from RSS feed to Page + Group

upload_instagram.py
    └── Reads public_video_url from meta
    └── Submits to Instagram API → polls until FINISHED → publishes
    └── output/instagram_caption.txt (always saved as manual backup)
```

> **Manual fallback for Instagram:** GitHub Actions → Run → Artifacts → download `zeno-reel-{run}-{mode}` → post `.mp4` + `instagram_caption.txt` manually.

---

## 7. Environment Variables & Secrets

All stored in **GitHub Actions Secrets**. Never hardcode any of these values.

### Dhan Trading API
| Secret | Purpose |
|---|---|
| `DHAN_API_KEY` | API key |
| `DHAN_API_SECRET` | API secret |
| `DHAN_CLIENT_ID` | Client ID |
| `DHAN_PIN` | Account PIN |
| `DHAN_TOTP_KEY` | 2FA TOTP key |

### Social Platforms
| Secret | Purpose | Critical Notes |
|---|---|---|
| `META_ACCESS_TOKEN` | Facebook + Instagram API | **Expires every 60 days — set reminder** |
| `FACEBOOK_PAGE_ID` | Target Facebook Page ID | |
| `FACEBOOK_GROUP_ID` | Target Facebook Group ID | Group posting broken until token fixed |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business/Creator numeric ID | **Not yet set — needed for auto-post** |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON | Single secret for all uploads |

### Telegram
| Secret | Purpose |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot authentication token |
| `TELEGRAM_CHAT_ID` | Default channel ID |
| `CHAT_ID_ADVANCE` | Advance signals channel |
| `CHAT_ID_PREMIUM` | Premium signals channel |

### Google / GCP
| Secret | Purpose |
|---|---|
| `GCP_SERVICE_ACCOUNT_JSON` | Search Console Indexing API + Google Sheets |

### General
| Secret | Purpose |
|---|---|
| `GROQ_API_KEY` | Groq API — Llama 3.3 70B — all content generation |
| `GH_TOKEN` | GitHub API token |

---

## 8. Known Issues & How to Fix

### Facebook Group Posting ❌

**Symptom:** Page posts succeed, Group posts fail.

**Diagnose:** Check GitHub Actions log. `upload_facebook.py` now runs `verify_token_permissions()` at startup and prints exactly which permission is missing with fix instructions.

**Root causes (check in order):**
1. `META_ACCESS_TOKEN` missing `publish_to_groups` scope — most common cause
2. Bot account is not an **Admin** of the group (member is not enough)
3. Group Settings → Advanced → "Allow content from apps" is OFF
4. App not approved for Groups API by Meta

**Fix:** Go to [developers.facebook.com](https://developers.facebook.com) → Your App → Add `publish_to_groups` permission → regenerate long-lived token → update `META_ACCESS_TOKEN` in GitHub Secrets.

**Current workaround:** Group posting now sends a text post with the video link (instead of direct video upload). This only requires `publish_to_groups` scope — not the stricter Groups Video API approval.

### Instagram Auto-Post ⚠️

**One missing secret:** Add `INSTAGRAM_ACCOUNT_ID` to GitHub Secrets.

Find your ID:
```
https://graph.facebook.com/me/accounts?access_token=YOUR_META_TOKEN
```

**How the chain works:** YouTube uploads reel → saves public URL to meta → Facebook uploads → overwrites with FB watch URL → Instagram reads URL from meta → processes and publishes automatically.

### META_ACCESS_TOKEN Expiry

- Expires every **60 days**
- Set a calendar reminder when you refresh
- After refresh → update `META_ACCESS_TOKEN` in GitHub Secrets immediately
- When expired: Facebook Page, Group, AND Instagram all stop working simultaneously

---

## 9. Technical Standards

### The "Full Code" Rule
> AI assistants **must always provide the complete content** of any modified file. Partial snippets or diffs are strictly prohibited — they break the GitHub Actions environment.

**Standard AI task prompt:**
```
Context: I am working on the ai360trading system. Refer to SYSTEM.md for architecture.
Task: [Your Task]
Note: Provide the full code for any file you modify.
```

### Dependency Pins

| Package | Version | Reason |
|---|---|---|
| `Pillow` | `>=10.3.0` | Required for LANCZOS resampling |
| `imageio` | `==2.9.0` | Prevents MoviePy rendering crashes |
| `moviepy` | `==1.0.3` | Force reinstall — newer versions break audio |
| `yfinance` | Latest | Use `fast_info['last_price']` only — not `.history()` |

### Voice Assignments

| Voice ID | Gender | Used For |
|---|---|---|
| `hi-IN-MadhurNeural` | Male | Short 2 — authoritative trade setups |
| `hi-IN-SwaraNeural` | Female | Short 3, ZENO Reel, Analysis, Education |

### Video Formats

| Content | Ratio | Platform |
|---|---|---|
| Analysis + Education | 16:9 | YouTube |
| Short 2, Short 3, ZENO Reel | 9:16 | YouTube Shorts / Reels / Instagram |

### SEO Tags Strategy

Every video includes both India-specific AND global tags:
- India: `Nifty50`, `TradingIndia`, `StockMarketIndia`, `BankNifty`
- Global: `USStocks`, `UKInvesting`, `BrazilMarket`, `UAEInvesting`, `GlobalInvesting`
- Universal: `Finance`, `Investing`, `FinancialLiteracy`, `Shorts`

---

## 10. Full Data Flow

```
Market hours (Mon–Fri, 9:15 AM–3:30 PM IST)
└── main.yml (every 5 min)
    └── trading_bot.py → Dhan API → Buy/Sell signals
        └── → Google Sheets + Telegram (all 3 channels)

7:30 AM / 9:30 AM daily
└── daily-videos.yml
    └── Detect mode → indian_holidays.py ✅
    └── generate_analysis.py → Groq → 8-slide Part 1 video → YouTube ✅
    └── generate_education.py → Groq → Part 2 video → YouTube ✅
    └── Saves: output/analysis_video_id.txt
    └── Posts: video links → Facebook Page ✅ | Group ❌

11:30 AM / 1:30 PM daily
└── daily-shorts.yml
    └── Detect mode → indian_holidays.py ✅
    └── generate_shorts.py
        └── yfinance fast_info → live prices (market mode)
        └── Groq → scripts for Short 2 + Short 3
        └── Short 2 (Madhur) + Short 3 (Swara) → YouTube ✅
        └── Facebook Page ✅ | Group ❌

8:30 PM daily
└── daily_reel.yml
    └── Detect mode → indian_holidays.py ✅
    └── generate_reel.py → Groq script → ZENO reel
    └── upload_youtube.py → YouTube ✅ → saves public_video_url to meta
    └── upload_facebook.py → FB Page ✅ | Group ❌ → updates public_video_url in meta
    └── upload_instagram.py → reads URL → Instagram API ⚠️

10:00 AM / 11:30 AM daily
└── daily-articles.yml
    └── Detect mode → indian_holidays.py ✅
    └── generate_articles.py → Groq → 4 Jekyll articles
    └── git commit → GitHub Pages ✅
    └── GCP Indexing API → instant Google indexing ✅
    └── Posts: article links → Facebook Page ✅ | Group ❌
```

---

## 11. Website

- **URL:** `ai360trading.in`
- **Hosting:** GitHub Pages (Jekyll, `master` branch `_posts/`)
- **Publishing:** Auto-commit by `daily-articles.yml` (`admin@ai360trading.in`)
- **SEO Indexing:** Instant via `GCP_SERVICE_ACCOUNT_JSON` after each publish
- **Revenue:** Google AdSense (USA/UK English readers = highest CPM)

---

*Documentation maintained by AI360Trading automation.*
*Full audit completed: March 28, 2026 — Claude Sonnet 4.6*
*Update this file whenever architecture, secrets, platform status, or file logic changes.*
