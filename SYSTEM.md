# AI360Trading — Master System Documentation

**Last Updated:** March 28, 2026 — Phase 2 Upgrade in Progress
**Status:** Phase 1 Foundation Complete | Phase 2 Active Build
**Primary Audience:** Bilingual Hindi + English — Indian retail traders + global investors

> ⚠️ **Read this file completely before making ANY changes.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT).

---

## 1. Real Mission

> This system is built to run **forever, fully automated**, generating passive income for the owner's family — even without active involvement. Built on ₹0/month infrastructure. No employees. No office. Pure automation.

### Monetisation — Every Stream Simultaneously

| Stream | Platform | High-CPM Target Countries |
|---|---|---|
| Video Ad Revenue | YouTube (Hindi) | USA, UK, Canada, Australia, UAE |
| Video Ad Revenue | YouTube (English) | USA, UK, Canada, Australia — 3–5x higher CPM |
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

> **AI Rule:** Always optimise content topics, hooks, SEO tags, and posting times for these countries.
> USA/UK prime time = 11 PM–1 AM IST. Include global keywords in all titles, descriptions, and tags.
> All hooks and CTAs rotate from human_touch.py — never hardcode them in generators.

---

## 2. Platform Status

| Platform | Status | Notes |
|---|---|---|
| YouTube Hindi | ✅ Auto | Analysis + Education + Shorts + Reels working |
| YouTube English | 🔄 Building | Phase 2 — auto-translated separate channel |
| YouTube Shorts | ✅ Auto | Short 2 + Short 3 working |
| YouTube Community Posts | 🔄 Building | Phase 2 — daily text post for algo boost |
| YouTube Reels | ✅ Auto | ZENO reel (8:30 PM) working |
| YouTube Morning Reel | 🔄 Building | Phase 2 — 7:00 AM reel (generate_reel_morning.py) |
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

## 4. Daily Content Output (Target — Fully Automated)

| # | Content | Time (IST) | Platform | Status |
|---|---|---|---|---|
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + FB + Instagram | 🔄 Building |
| 2 | Part 1 Video (16:9) | 7:30 AM weekday / 9:30 AM weekend | YouTube | ✅ |
| 3 | Part 2 Video (16:9) | 7:30 AM (same workflow) | YouTube | ✅ |
| 4 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | ✅ |
| 5 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 6 | Short 4 English (9:16) | 11:30 AM (same workflow) | YouTube English Shorts | 🔄 Building |
| 7 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 8 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB + Instagram | ✅ |
| 9 | YouTube Community Post | 12:00 PM | YouTube Community Tab | 🔄 Building |
| **Total** | **12 pieces/day** | — | — | — |

> **USA/UK prime time content:** Videos uploaded at IST times but SEO-optimised for 11 PM–1 AM IST peak.

---

## 5. GitHub Actions Workflows

| File | Trigger (IST) | Purpose | Mode-Aware |
|---|---|---|---|
| `main.yml` | Every 5 min (market hours, Mon–Fri) | `trading_bot.py` — Nifty200 signals | ✅ Auto-skips weekends/holidays |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 (analysis) + Part 2 (education) | ✅ |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 + Short 4 (English) | ✅ |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning Reel + ZENO Reel | ✅ |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages | ✅ |
| `token_refresh.yml` | Every 50 days (1st + 20th of month) | Auto META token refresh | N/A |
| `keepalive.yml` | Periodic | Prevents GitHub disabling inactive workflows | N/A |

All workflows support `workflow_dispatch` with a `content_mode` dropdown to force any mode for testing.

---

## 6. Complete File Map

### Core Infrastructure (Phase 1 — NEW)

| File | Role | Status |
|---|---|---|
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates fallback | ✅ Built |
| `human_touch.py` | Anti-AI-penalty layer — 50+ hooks, personal phrases, TTS variation, SEO tags | ✅ Built |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update + Telegram alert | ✅ Built |

### Core Content Generation

| File | Role | Key Tech | Status |
|---|---|---|---|
| `trading_bot.py` | Nifty200 buy/sell signal scanner | Dhan API, Google Sheets | ✅ |
| `generate_shorts.py` | Short 2 + Short 3 + Short 4 (English) | ai_client, human_touch, Edge-TTS | 🔄 Upgrading |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ai_client, human_touch, MoviePy | 🔄 Upgrading |
| `generate_reel_morning.py` | Morning reel (7:00 AM) — day/country aware | ai_client, human_touch, MoviePy | ✅ Built |
| `generate_analysis.py` | 8-slide market analysis video (Part 1) | ai_client, human_touch, MoviePy | 🔄 Upgrading |
| `generate_education.py` | Educational deep-dive video (Part 2) | ai_client, content_calendar.py | 🔄 Upgrading |
| `generate_articles.py` | 4 SEO articles daily → Jekyll _posts | ai_client, human_touch | 🔄 Upgrading |
| `generate_community_post.py` | YouTube daily community text post | ai_client, human_touch | 🔄 Building |
| `generate_english.py` | English script generator for all content | ai_client, human_touch (en) | 🔄 Building |

### Upload & Distribution

| File | Role | Status |
|---|---|---|
| `upload_youtube.py` | Uploads reel; saves `youtube_video_id` + `public_video_url` to meta | ✅ |
| `upload_youtube_english.py` | Uploads to English channel (separate credentials) | 🔄 Building |
| `upload_facebook.py` | Uploads reel to FB Page; shares to Group; posts articles | ✅ |
| `upload_instagram.py` | Auto-uploads via Meta API using `public_video_url` from meta | ✅ |

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

## 7. AI Fallback Chain

All content generation uses `ai_client.py`. **Never call Groq/Gemini/Claude/OpenAI directly in generators.**

```
Groq — llama-3.3-70b-versatile (primary — fastest, free)
    ↓ fails
Google Gemini — gemini-2.0-flash (secondary — best image/video roadmap for Disney 3D)
    ↓ fails
Anthropic Claude — claude-haiku-4-5 (tertiary — best human-touch writing)
    ↓ fails
OpenAI — gpt-4o-mini (quaternary — reliable fallback)
    ↓ all fail
Pre-generated templates in human_touch.py (always works — zero downtime)
```

**Import pattern in ALL generators:**
```python
from ai_client import ai, img_client
from human_touch import ht, seo
```

---

## 8. Critical Upload Chain

Scripts must run in this exact order. Each one feeds data to the next:

### Evening ZENO Reel (8:30 PM)
```
generate_reel.py
    └── output/reel_YYYYMMDD.mp4
    └── output/meta_YYYYMMDD.json  ← created here

upload_youtube.py
    └── Uploads reel to YouTube
    └── Writes to meta → youtube_video_id, youtube_video_url, public_video_url

upload_facebook.py
    └── Uploads reel to Facebook Page
    └── Posts link to Facebook Group (when fixed)
    └── Overwrites meta → public_video_url (Facebook watch URL)
    └── Posts articles from RSS feed to Page + Group

upload_instagram.py
    └── Reads public_video_url from meta
    └── Submits to Instagram API → polls until FINISHED → publishes
```

### Morning Reel (7:00 AM)
```
generate_reel_morning.py
    └── output/morning_reel_YYYYMMDD.mp4
    └── output/morning_reel_meta_YYYYMMDD.json

upload_youtube.py (morning mode)
upload_facebook.py (morning mode)
upload_instagram.py (morning mode)
```

> **Manual fallback for Instagram:** GitHub Actions → Run → Artifacts → download → post manually.

---

## 9. Environment Variables & Secrets

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
| `META_ACCESS_TOKEN` | Facebook + Instagram API | **Auto-refreshed every 50 days by token_refresh.yml** |
| `META_APP_ID` | Facebook App ID | **NEW — needed for auto token refresh** |
| `META_APP_SECRET` | Facebook App Secret | **NEW — needed for auto token refresh** |
| `FACEBOOK_PAGE_ID` | Target Facebook Page ID | |
| `FACEBOOK_GROUP_ID` | Target Facebook Group ID | Group posting broken until token fixed |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business/Creator numeric ID | **Not yet set — needed for auto-post** |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON (Hindi channel) | |
| `YOUTUBE_CREDENTIALS_EN` | YouTube OAuth JSON (English channel) | **NEW — needed for English channel** |

### AI Providers (Fallback Chain)
| Secret | Purpose | Priority |
|---|---|---|
| `GROQ_API_KEY` | Groq — Llama 3.3 70B | Primary |
| `GEMINI_API_KEY` | Google Gemini 2.0 Flash | Secondary |
| `ANTHROPIC_API_KEY` | Claude Haiku | Tertiary |
| `OPENAI_API_KEY` | GPT-4o-mini | Quaternary |

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
| `GH_TOKEN` | GitHub API token |

---

## 10. Human Touch System (Anti-AI-Penalty)

All content uses `human_touch.py`. **Never use raw AI output directly.**

| Technique | What It Does |
|---|---|
| 50+ rotating hooks | No two videos start the same — `ht.get_hook(mode, lang)` |
| Personal phrases | "Maine dekha hai..." injected naturally — `ht.get_personal_phrase(lang)` |
| TTS speed variation | 0.95–1.05x range — `ht.get_tts_speed()` |
| Connector variation | "aur/lekin/kyunki" rotated to avoid repetition |
| Robotic pattern removal | "Certainly!", "It's important to note" etc. stripped |
| Emoji rotation | Day-seeded so each day's content has different emoji set |
| Day-aware morning topics | 7 different morning reel topics by weekday |

---

## 11. Known Issues & How to Fix

### Facebook Group Posting ❌

**Root causes (check in order):**
1. `META_ACCESS_TOKEN` missing `publish_to_groups` scope
2. Bot account not **Admin** of the group
3. Group Settings → Advanced → "Allow content from apps" OFF
4. App not approved for Groups API by Meta

**Fix:** developers.facebook.com → App → Add `publish_to_groups` → regenerate token → update secret.
**Token is now auto-refreshed** by `token_refresh.yml` — no more manual refresh needed.

### Instagram Auto-Post ⚠️

**One missing secret:** Add `INSTAGRAM_ACCOUNT_ID` to GitHub Secrets.
```
https://graph.facebook.com/me/accounts?access_token=YOUR_META_TOKEN
```

### META_ACCESS_TOKEN Expiry — NOW AUTOMATED ✅

- `token_refresh.yml` runs every 50 days automatically
- Refreshes token + updates GitHub Secret + sends Telegram alert
- **New secrets needed:** `META_APP_ID` and `META_APP_SECRET` (find in developers.facebook.com)
- If auto-refresh fails, Telegram alert sent with manual fix instructions

### New Secrets Needed for Full System
| Secret | Where to Find |
|---|---|
| `META_APP_ID` | developers.facebook.com → Your App → Settings → Basic |
| `META_APP_SECRET` | developers.facebook.com → Your App → Settings → Basic |
| `INSTAGRAM_ACCOUNT_ID` | Graph API: `/me/accounts?access_token=YOUR_TOKEN` |
| `GEMINI_API_KEY` | aistudio.google.com → API Keys |
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |
| `OPENAI_API_KEY` | platform.openai.com → API Keys |
| `YOUTUBE_CREDENTIALS_EN` | Google Cloud Console → OAuth → English channel |

---

## 12. Technical Standards

### The "Full Code" Rule
> AI assistants **must always provide the complete content** of any modified file. Partial snippets or diffs are strictly prohibited.

**Standard AI task prompt:**
```
Context: I am working on the ai360trading system. Refer to SYSTEM.md for architecture.
Task: [Your Task]
Note: Provide the full code for any file you modify.
```

### AI Client Usage Rule
> **Never call AI APIs directly in generators.** Always use:
```python
from ai_client import ai, img_client
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang=LANG)
```

### Human Touch Usage Rule
> **Never use raw AI output.** Always pass through human_touch:
```python
from human_touch import ht, seo
hook = ht.get_hook(mode=CONTENT_MODE, lang=LANG)
script = ht.humanize(raw_script, lang=LANG)
```

### Dependency Pins

| Package | Version | Reason |
|---|---|---|
| `Pillow` | `>=10.3.0` | Required for LANCZOS resampling |
| `imageio` | `==2.9.0` | Prevents MoviePy rendering crashes |
| `moviepy` | `==1.0.3` | Force reinstall — newer versions break audio |
| `yfinance` | Latest | Use `fast_info['last_price']` only — not `.history()` |
| `PyNaCl` | Latest | Required for GitHub Secret encryption in token_refresh.py |
| `google-generativeai` | Latest | Gemini fallback in ai_client.py |
| `anthropic` | Latest | Claude fallback in ai_client.py |
| `openai` | Latest | OpenAI fallback in ai_client.py |

### Voice Assignments

| Voice ID | Gender | Used For |
|---|---|---|
| `hi-IN-MadhurNeural` | Male | Short 2 — authoritative trade setups |
| `hi-IN-SwaraNeural` | Female | Short 3, ZENO Reel, Morning Reel, Analysis, Education |
| `en-US-JennyNeural` | Female | English channel — all English content |
| `en-US-GuyNeural` | Male | English Short 2 alternative |

### Video Formats

| Content | Ratio | Platform |
|---|---|---|
| Analysis + Education | 16:9 | YouTube |
| Short 2, Short 3, Short 4, Morning Reel, ZENO Reel | 9:16 | YouTube Shorts / Reels / Instagram |

### SEO Tags Strategy

Every video includes both India-specific AND global tags via `seo.get_video_tags()`:
- India: `Nifty50`, `TradingIndia`, `StockMarketIndia`, `BankNifty`
- Global: `USStocks`, `UKInvesting`, `BrazilMarket`, `UAEInvesting`, `GlobalInvesting`
- Universal: `Finance`, `Investing`, `FinancialLiteracy`, `Shorts`

---

## 13. Disney 3D Reel Roadmap

| Phase | Tool | Quality | Timeline | Status |
|---|---|---|---|---|
| 1 (Now) | PIL + MoviePy + ZENO PNG | 2D animated slides | Current | ✅ Active |
| 2 | Gemini Veo API (free tier) | AI video clips | 3–6 months | Hooks in ai_client.py |
| 3 | Stable Diffusion + AnimateDiff | 3D style frames | 6–12 months | Planned |
| 4 | Google Veo 2 / Sora (when free) | True Disney-style 3D | 12–18 months | Planned |

> `img_client` in `ai_client.py` is the upgrade hook — swap in Phase 2 generation with zero changes to generators.

---

## 14. Full Data Flow

```
Market hours (Mon–Fri, 9:15 AM–3:30 PM IST)
└── main.yml (every 5 min)
    └── trading_bot.py → Dhan API → Buy/Sell signals
        └── → Google Sheets + Telegram (all 3 channels) ✅

7:00 AM daily (NEW)
└── daily_reel.yml (morning job)
    └── generate_reel_morning.py
        └── ai_client → Groq/Gemini/Claude/OpenAI/Template
        └── human_touch → day-aware topic + hook
        └── Morning reel video (9:16)
        └── Upload: YouTube ✅ | Facebook ✅ | Instagram ⚠️

7:30 AM / 9:30 AM daily
└── daily-videos.yml
    └── generate_analysis.py → ai_client → Part 1 video → YouTube ✅
    └── generate_education.py → ai_client → Part 2 video → YouTube ✅
    └── Posts: links → Facebook Page ✅ | Group ❌

11:30 AM / 1:30 PM daily
└── daily-shorts.yml
    └── generate_shorts.py
        └── Short 2 (Hindi, Madhur) → YouTube ✅
        └── Short 3 (Hindi, Swara) → YouTube ✅
        └── Short 4 (English, Jenny) → YouTube English ✅ (🔄 building)
        └── Facebook Page ✅ | Group ❌

12:00 PM daily (NEW)
└── daily-shorts.yml (community post step)
    └── generate_community_post.py → YouTube Community Tab 🔄

8:30 PM daily
└── daily_reel.yml (evening job)
    └── generate_reel.py → ai_client → ZENO reel
    └── upload_youtube.py → YouTube ✅ → saves public_video_url
    └── upload_facebook.py → FB Page ✅ | Group ❌ → updates URL
    └── upload_instagram.py → Instagram ⚠️

10:00 AM / 11:30 AM daily
└── daily-articles.yml
    └── generate_articles.py → ai_client → 4 Jekyll articles
    └── git commit → GitHub Pages ✅
    └── GCP Indexing API → instant Google indexing ✅
    └── Posts: links → Facebook Page ✅ | Group ❌
```

---

## 15. Website

- **URL:** `ai360trading.in`
- **Hosting:** GitHub Pages (Jekyll, `master` branch `_posts/`)
- **Publishing:** Auto-commit by `daily-articles.yml`
- **SEO Indexing:** Instant via `GCP_SERVICE_ACCOUNT_JSON`
- **Revenue:** Google AdSense (USA/UK English readers = highest CPM)

---

*Documentation maintained by AI360Trading automation.*
*Full audit: March 28, 2026 — Claude Sonnet 4.6*
*Phase 1 complete: ai_client.py, human_touch.py, token_refresh.py, token_refresh.yml, generate_reel_morning.py*
*Phase 2 in progress: generate_community_post.py, generate_english.py, upgraded generators*
*Update this file whenever architecture, secrets, platform status, or file logic changes.*
