# AI360Trading — Master System Documentation

**Last Updated:** March 28, 2026
**Status:** Phase 2 — Partially Operational (See Platform Status below)
**Primary Audience:** Bilingual Hindi + English (Indian retail traders + global audience)

> ⚠️ **Read this file completely before making ANY changes to logic, workflows, or environment variables.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT) working on this project.

---

## 1. Project Overview

**AI360Trading** is a zero-cost, high-frequency automated content engine and trading signal system running entirely on **GitHub Actions** (Free Tier). It uses AI (Groq / Llama 3.3) and real-time financial data to maintain a consistent, human-feel presence across 5+ social platforms.

### Core Goals

| Goal | Detail |
|---|---|
| Daily Output | 9 unique content pieces (Videos, Shorts, Reels, Articles) |
| Cost | ₹0 / $0 — Free API tiers + GitHub Free Tier |
| Automation | 95% target (Instagram & Facebook Group still being resolved) |
| Strategy | "Value Buying" and "Fast Returns" for retail traders |
| Language | Bilingual: Hindi + English |

---

## 2. Platform Status (Current)

| Platform | Status | Notes |
|---|---|---|
| YouTube (Videos) | ✅ Fully Auto | Main videos, Reels, Shorts all working |
| YouTube (Shorts) | ✅ Fully Auto | 9:16 format, posting correctly |
| Facebook Page | ✅ Fully Auto | Posts text, video, mode-aware content |
| Facebook Group | ❌ Broken | Posting fails — root cause unknown (token scope or group ID issue) |
| Instagram | ❌ Manual | Video + caption saved as GitHub Artifact; must be posted manually |
| GitHub Pages (Website) | ✅ Fully Auto | Articles auto-published + indexed via Google Search Console |
| Telegram | ✅ Fully Auto | Signal alerts via TELEGRAM_BOT_TOKEN |

### Active Work Items (Priority)
1. **Fix Facebook Group posting** — Diagnose whether it is a token permission issue, wrong Group ID, or code logic bug
2. **Automate Instagram** — Evaluate Meta Content Publishing API vs third-party tools (Buffer, Make.com) — approach not yet decided

---

## 3. Content Mode System

The system reads the `CONTENT_MODE` environment variable to switch content strategy automatically.

| Mode | When | Content Type |
|---|---|---|
| `market` | Monday–Friday (excluding Indian holidays) | Live Nifty50/Global data, trade setups, technical signals |
| `weekend` | Saturday–Sunday | Educational/Evergreen content, wealth-building mindset |
| `holiday` | Indian Market Holidays | Motivational stories, savings tips, "Market band hai, par seekhna chalu rakho!" |

**Mode detection logic lives in:** `indian_holidays.py` (uses NSE API with fallback)

---

## 4. GitHub Actions Workflows

There are **6 workflow files** in `.github/workflows/`:

| File | Trigger (IST) | Purpose |
|---|---|---|
| `main.yml` | Every 5 mins (market hours, weekdays) | Runs `trading_bot.py` — scans Nifty200 for buy/sell signals. Auto-skips on weekends/holidays. |
| `daily-shorts.yml` | 11:30 AM (weekday) / 1:30 PM (weekend) | Generates Short 2 (Trade Setup) + Short 3 (Global Market Pulse) |
| `daily-videos.yml` | Scheduled daily | Generates Part 1 (8-slide market analysis) via `generate_analysis.py` |
| `daily_reel.yml` | 8:30 PM daily | Generates ZENO 60s Reel — posts auto to YouTube + Facebook; Instagram is manual |
| `daily-articles.yml` | Scheduled daily | Generates 4 SEO-optimised articles via `generate_articles.py` → Jekyll `_posts` |
| `keepalive.yml` | Periodic | Prevents GitHub Actions from disabling inactive workflows |

---

## 5. Complete File Map

### Core Content Generation

| File | Role | Key Technology |
|---|---|---|
| `trading_bot.py` | Scans Nifty200 for buy/sell signals | Dhan API, Google Sheets |
| `generate_shorts.py` | Live Price Market Pulse + Trade Setup cards | yfinance (`fast_info`), PIL, Edge-TTS |
| `generate_reel.py` | ZENO 3D Disney-style moral/wisdom reels | Groq, MoviePy, PIL (Hero scaling) |
| `generate_analysis.py` | Part 1: 8-slide market analysis video | PIL, MoviePy, Groq |
| `generate_education.py` | Part 2: Educational deep-dive (links to Part 1) | `content_calendar.py`, Groq |
| `generate_articles.py` | 4 SEO-optimised articles daily | Groq, Jekyll (`_posts`) |

### Infrastructure & Support

| File | Role |
|---|---|
| `indian_holidays.py` | Mode detection brain — NSE API + fallback calendar |
| `content_calendar.py` | Rotates topics: Options, Tech Analysis, Psychology |
| `upload_facebook.py` | Facebook upload handler — includes emergency string search for RSS feeds |

### Static Assets

| Path | Contents |
|---|---|
| `public/image/` | ZENO emotion assets: `happy`, `sad`, `greed`, `thinking` |
| `public/music/` | Background tracks: `bgmusic1`, `bgmusic2`, `bgmusic3` — rotated by day of week |

---

## 6. Environment Variables & Secrets

All secrets are stored in **GitHub Actions Secrets**. Never hardcode any of these.

### Dhan Trading API
| Secret | Purpose |
|---|---|
| `DHAN_API_KEY` | Dhan broker API key |
| `DHAN_API_SECRET` | Dhan broker API secret |
| `DHAN_CLIENT_ID` | Dhan client ID |
| `DHAN_PIN` | Dhan account PIN |
| `DHAN_TOTP_KEY` | TOTP key for 2FA login |

### Social Platforms
| Secret | Purpose | Notes |
|---|---|---|
| `META_ACCESS_TOKEN` | Facebook Page + Group posting | **Expires every 60 days — must refresh manually** |
| `FACEBOOK_PAGE_ID` | Target Facebook Page ID | |
| `FACEBOOK_GROUP_ID` | Target Facebook Group ID | Group posting currently broken |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON | Single JSON secret for all YouTube uploads |

### Telegram Alerts
| Secret | Purpose |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token for sending signals |
| `TELEGRAM_CHAT_ID` | Default chat/channel ID |
| `CHAT_ID_ADVANCE` | Advance signals chat ID |
| `CHAT_ID_PREMIUM` | Premium signals chat ID |

### Google / GCP
| Secret | Purpose |
|---|---|
| `GCP_SERVICE_ACCOUNT_JSON` | Google Search Console Indexing API + Sheets access |

### AI & General
| Secret | Purpose |
|---|---|
| `GROQ_API_KEY` | Groq API (Llama 3.3) for content generation |
| `GH_TOKEN` | GitHub token for cross-repo or API operations |

---

## 7. Technical Standards & Critical Rules

### The "Full Code" Rule
> **AI assistants MUST always provide the complete content of any file they modify.**
> Partial snippets or diffs are strictly prohibited — they break the GitHub Actions environment.

**Always start your task prompt with:**
```
Context: I am working on the ai360trading system. Refer to SYSTEM.md for architecture.
Task: [Your Task Here]
Note: Provide the full code for any file you modify.
```

### Dependency Pins (Do Not Change)
| Package | Required Version | Reason |
|---|---|---|
| `Pillow` | `>=10.3.0` | Required for `LANCZOS` resampling |
| `imageio` | `==2.9.0` | Prevents MoviePy rendering crashes |
| `yfinance` | Latest | Must use `fast_info['last_price']` — avoids 1-day data lag |

### Voice Assignments
| Voice | Gender | Used For |
|---|---|---|
| `Madhur` | Male | Short 2 — Authoritative trade setup narration |
| `Swara` | Female | ZENO Reel, Analysis, Education, Short 3 — Energetic tone |

### Content Output Formats
| Content | Aspect Ratio | Platform |
|---|---|---|
| Analysis / Education Videos | 16:9 | YouTube |
| Shorts 1, 2, 3 | 9:16 | YouTube Shorts |
| ZENO Reel | 9:16 | YouTube, Facebook, Instagram (manual) |

---

## 8. Known Issues & Fixes

### Facebook Group Posting (❌ Broken)
- **Symptom:** Posts succeed on Facebook Page but fail silently or error on Group
- **Suspected causes (not yet confirmed):**
  - `META_ACCESS_TOKEN` may lack `publish_to_groups` permission scope
  - `FACEBOOK_GROUP_ID` may be incorrect or the bot is not a Group admin
  - Code logic in `upload_facebook.py` may not handle group endpoint correctly
- **Next step for AI assistant:** Audit `upload_facebook.py` — check the API endpoint used for group vs page, verify token scopes, and check if the bot account is a Group admin

### Instagram Auto-Post (❌ Manual)
- **Current state:** Video + caption are saved to GitHub Artifacts after each reel/short is generated
- **Manual task:** Download artifact → Post to Instagram app within 24 hours
- **Blocker:** Meta API restricts direct video upload for many account types
- **Next step:** Decide between Meta Content Publishing API or a third-party bridge (Buffer, Make.com) — not yet decided

### META_ACCESS_TOKEN Expiry
- Token expires every **60 days**
- Must be manually refreshed via Meta Developer Console
- After refresh, update the `META_ACCESS_TOKEN` secret in GitHub Actions immediately
- Set a calendar reminder when refreshing

### yfinance Data Lag
- **Wrong:** `yf.Ticker.history()` — returns previous day's close, not live price
- **Correct:** `yf.Ticker.fast_info['last_price']` — returns real-time/near-live price
- This fix is already applied in `generate_shorts.py`

---

## 9. Data Flow Summary

```
market hours (Mon–Fri)
    └── main.yml (every 5 min)
            └── trading_bot.py → Dhan API → Buy/Sell signals → Google Sheets + Telegram

11:30 AM / 1:30 PM daily
    └── daily-shorts.yml
            └── generate_shorts.py → yfinance (live price) → Short 2 + Short 3
                    └── Upload: YouTube ✅ | Instagram: Artifact (manual) ✅

8:30 PM daily
    └── daily_reel.yml
            └── generate_reel.py → Groq (script) + PIL + MoviePy → ZENO Reel
                    └── Upload: YouTube ✅ | Facebook Page ✅ | Instagram: Artifact (manual)

Daily (scheduled)
    └── daily-videos.yml
            └── generate_analysis.py + generate_education.py → Groq → 2-part video
                    └── Upload: YouTube ✅

Daily (scheduled)
    └── daily-articles.yml
            └── generate_articles.py → Groq → 4 Jekyll posts → GitHub Pages ✅
                    └── Google Search Console Indexing API → instant indexing ✅
```

---

## 10. Website

- **URL:** `ai360trading.in`
- **Hosting:** GitHub Pages (Jekyll)
- **Articles:** Auto-published to `_posts/` by `generate_articles.py`
- **Indexing:** New posts submitted instantly to Google Search Console via GCP Indexing API (`GCP_SERVICE_ACCOUNT_JSON`)

---

*Documentation maintained by AI360Trading. Update this file whenever architecture, secrets, or platform status changes.*
