# AI360Trading — Master System Documentation

**Last Updated:** April 5, 2026 — Trading Bot v13.5 + AppScript v13.3 + HerooQuest Kids Channel Added
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 Planned | Phase 4 (Dhan Live) Planned
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
| Kids Video Ad Revenue | YouTube Kids (HerooQuest) | USA, UK, Canada, Australia — highest kids CPM |
| Shorts / Reels Bonus | YouTube, Facebook, Instagram | USA, UK, Brazil, India |
| Website Ad Revenue | GitHub Pages (ai360trading.in) | USA, UK, Canada |
| In-Stream Video Ads | Facebook Page | USA, UK, Brazil, India |
| Kids In-Stream Ads | Facebook Kids Page | USA, UK, Canada, Australia |
| Paid Signal Subscriptions | Telegram (Advance + Premium channels) | India, UAE, Global |

### Target Countries by Ad CPM Priority

1. 🇺🇸 USA — Highest CPM globally for finance + kids content
2. 🇬🇧 UK — Very high CPM, strong trading + kids audience
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
| YouTube English | 🔄 Building | Phase 3 — auto-translated separate channel |
| YouTube Shorts | ✅ Auto | Short 2 + Short 3 working |
| YouTube Community Posts | ✅ Built | generate_community_post.py — 12:00 PM daily |
| YouTube Reels | ✅ Auto | ZENO reel (8:30 PM) working |
| YouTube Morning Reel | ✅ Auto | 7:00 AM reel (generate_reel_morning.py) working |
| YouTube Kids (HerooQuest) | 🔄 Building | kids-daily.yml — 8:00 AM IST daily — pending OAuth |
| Facebook Page | ✅ Auto | Posts, reels, article shares all working |
| Facebook Kids Page | 🔄 Building | Separate kids page under same account — pending creation |
| Facebook Group | ❌ Broken | Missing `publish_to_groups` token scope — see Section 12 |
| Instagram | ⚠️ Partial | Upload chain built; `INSTAGRAM_ACCOUNT_ID` secret needed |
| Instagram Kids | 📱 Manual | Share from Facebook Kids Page manually |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | Signal alerts to all 3 channels (paper trading) |

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

## 4. Daily Content Output (Fully Automated)

| # | Content | Time (IST) | Platform | Status |
|---|---|---|---|---|
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + FB + Instagram | ✅ |
| 2 | Part 1 Video (16:9) | 7:30 AM weekday / 9:30 AM weekend | YouTube | ✅ |
| 3 | Part 2 Video (16:9) | 7:30 AM (same workflow) | YouTube | ✅ |
| 4 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | ✅ |
| 5 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 6 | Short 4 English (9:16) | 11:30 AM (same workflow) | YouTube English Shorts | 🔄 Phase 3 |
| 7 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 8 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB + Instagram | ✅ |
| 9 | YouTube Community Post | 12:00 PM | YouTube Community Tab | ✅ |
| 10 | Kids Story Video (16:9) 8–10 min | 8:00 AM | YouTube Kids (HerooQuest) | 🔄 |
| 11 | Kids Short (9:16) 60 sec | 8:01 AM | YouTube Kids Shorts | 🔄 |
| 12 | Kids Story Video (same) | 9:00 AM | Facebook Kids Page | 🔄 |
| **Total** | **15 pieces/day** | — | — | — |

> **USA/UK prime time content:** Videos uploaded at IST times but SEO-optimised for 11 PM–1 AM IST peak.

---

## 5. GitHub Actions Workflows

| File | Trigger (IST) | Purpose | Mode-Aware |
|---|---|---|---|
| `main.yml` | Every 5 min (market hours, Mon–Fri) | `trading_bot.py` — Nifty200 signals | ✅ Auto-skips weekends/holidays |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 (analysis) + Part 2 (education) | ✅ |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 + Community Post | ✅ |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning Reel + ZENO Reel | ✅ |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages | ✅ |
| `kids-daily.yml` | 8:00 AM daily (cron: 30 2 * * *) | Kids video + YouTube Kids + Facebook Kids | ✅ |
| `token_refresh.yml` | Every 50 days (1st + 20th of month) | Auto META token refresh | N/A |
| `keepalive.yml` | Periodic | Prevents GitHub disabling inactive workflows | N/A |

All workflows support `workflow_dispatch` with dropdowns to force any mode for testing.

---

## 6. Complete File Map

### Core Infrastructure (Phase 1 — Complete)

| File | Role | Status |
|---|---|---|
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates fallback | ✅ |
| `human_touch.py` | Anti-AI-penalty layer — 50+ hooks, personal phrases, TTS variation, SEO tags | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update + Telegram alert | ✅ |

### Core Content Generation (Phase 2 — All Upgraded)

| File | Role | Key Tech | Status |
|---|---|---|---|
| `trading_bot.py` | Nifty200 signal monitor + TSL manager + Telegram alerts | gspread + Sheets + Telegram | ✅ v13.5 |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Swara) | ai_client, human_touch, Edge-TTS | ✅ |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ai_client, human_touch, MoviePy | ✅ |
| `generate_reel_morning.py` | Morning reel (7:00 AM) | ai_client, human_touch, MoviePy | ✅ |
| `generate_analysis.py` | 8-slide market analysis video (Part 1) | ai_client, human_touch, MoviePy | ✅ |
| `generate_education.py` | Educational deep-dive video (Part 2) | ai_client, human_touch, content_calendar | ✅ |
| `generate_articles.py` | 4 SEO articles daily → Jekyll _posts | ai_client, human_touch, Google Indexing | ✅ |
| `generate_community_post.py` | YouTube daily community text post | ai_client, human_touch | ✅ |
| `generate_kids_video.py` | Pixar-style kids story — 7 scenes, Ken Burns, TTS, bilingual | ai_client, edge-tts, MoviePy, Gemini | 🔄 Building |
| `kids_content_calendar.py` | Daily topic auto-picker — 15 categories, rotation by day-of-year | — | ✅ Done |

### Upload & Distribution

| File | Role | Status |
|---|---|---|
| `upload_youtube.py` | Uploads reel; saves youtube_video_id + public_video_url to meta | ✅ |
| `upload_youtube_english.py` | Uploads to English channel (separate credentials) | 🔄 Phase 3 |
| `upload_kids_youtube.py` | Uploads full video + short to HerooQuest kids channel | 🔄 Pending OAuth |
| `upload_facebook.py` | Uploads reel to FB Page; shares to Group; posts articles | ✅ |
| `upload_instagram.py` | Auto-uploads via Meta API using public_video_url from meta | ✅ |

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
Google Gemini — gemini-2.0-flash (secondary)
    ↓ fails
Anthropic Claude — claude-haiku-4-5 (tertiary)
    ↓ fails
OpenAI — gpt-4o-mini (quaternary)
    ↓ all fail
Pre-generated templates in human_touch.py (always works — zero downtime)
```

**Import pattern in ALL generators — no exceptions:**
```python
from ai_client import ai, img_client
from human_touch import ht, seo
```

---

## 8. Trading Bot Architecture

### Overview

| Component | File | Version | Role |
|---|---|---|---|
| AppScript | Google Sheets bound script | v13.3 | Scans Nifty200, applies 10 gates, writes WAITING candidates to AlertLog |
| Python Bot | `trading_bot.py` | **v13.5** | Monitors AlertLog every 5 min, manages WAITING→TRADED, TSL, Telegram |

**Current status:** Paper trading. Dhan API integration planned for Phase 4.

### Google Sheets Structure

| Sheet | Purpose |
|---|---|
| `Nifty200` | Live data for all 200 stocks — 34 cols A–AH |
| `AlertLog` | Active + waiting trades — 15 rows max. T2=YES/NO switch. T4=memory string |
| `History` | Closed trade log — 18 cols A–R |
| `PriceCache` | Helper sheet |
| `TempPriceCalc` | Scratch sheet for GOOGLEFINANCE calculations |
| `Corporate_Action` | Dividend/split events — currently unpopulated |

### AlertLog Column Map (0-based)

```
A=0  Signal Time    B=1  Symbol        C=2  Live Price     D=3  Priority Score
E=4  Trade Type     F=5  Strategy      G=6  Breakout Stage H=7  Initial SL
I=8  Target         J=9  RR Ratio      K=10 Trade Status   L=11 Entry Price
M=12 Entry Time     N=13 Days in Trade O=14 Trailing SL    P=15 P/L%
Q=16 ATH Warning    R=17 Risk ₹        S=18 Position Size  T=19 SYSTEM CONTROL
```

### Live AlertLog State (April 4, 2026)

| Symbol | Status | Entry | SL | Target | RR | Mode | Capital |
|---|---|---|---|---|---|---|---|
| NSE:ONGC | 🟢 TRADED (PAPER) | ₹275.10 | ₹232.35 | ₹339.35 | 1:1.5* | VCP | ₹13,000 |
| NSE:ADANIPOWER | 🟢 TRADED (PAPER) | ₹150.30 | ₹143.48 | ₹160.53 | 1:1.5* | MOM | ₹13,000 |

*Pre-v13.3 entries — RR below current MIN_RR 1.8 but actively monitored.

### Python Bot v13.5 — Key Fixes

**Fix 1 — `clean_mem()` two-pass orphan cleanup**
**Fix 2 — ATR read directly from Nifty200 col AC at entry**
**Fix 3 — RR re-validation on WAITING→TRADED (skip if rr_val < MIN_RR 1.8)**

### TSL Parameters (mode-aware)

```python
TSL_PARAMS = {
    "VCP": { "breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0 },
    "MOM": { "breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0 },
    "STD": { "breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0 },
}
```

### All-Time Performance (April 4, 2026)

```
Total closed trades: 25 | Wins: 2 | Losses: 23 | Win rate: 8%
Total P/L: ₹−7,013 | Bear market conditions throughout
```

---

## 9. Cross-System Consistency (v13.5 Audit)

### ✅ Aligned

| Item | Status |
|---|---|
| MIN_RR = 1.8 | AppScript + Bot aligned |
| Capital tiers ₹7k/₹10k/₹13k | Aligned |
| ATR from Nifty200 col AC | Fixed in v13.5 |
| Memory key format | Aligned |

### ⚠️ Known Gaps

| Gap | Impact | Resolution |
|---|---|---|
| ATR in memory for existing open trades | Medium | Exit and re-enter. FIX 2 prevents for future |
| RR on existing open trades | Low | Resolves on exit |
| Corporate_Action sheet empty | Low | Manual monitoring until Phase 4 |

---

## 10. Critical Upload Chain

### Kids Channel (8:00 AM daily)
```
kids_content_calendar.py → get_today_topic()
    └── generate_kids_video.py
        └── AI script → Gemini images → edge-tts audio → moviepy render
        └── output/kids_video_YYYY-MM-DD.mp4 (16:9, 8–10 min)
        └── output/kids_short_YYYY-MM-DD.mp4 (9:16, 60 sec)
        └── output/kids_meta_YYYY-MM-DD.json

    └── upload_kids_youtube.py
        └── Full video → HerooQuest (selfDeclaredMadeForKids: True)
        └── Short → HerooQuest Shorts
        └── Saves youtube_video_id to meta

    └── upload_facebook.py --meta-prefix kids
        └── Video → Facebook Kids Page
        └── Instagram Kids → Manual only
```

### Evening ZENO Reel (8:30 PM)
```
generate_reel.py → upload_youtube.py → upload_facebook.py → upload_instagram.py
```

### Morning Reel (7:00 AM)
```
generate_reel_morning.py → upload_youtube.py → upload_facebook.py → upload_instagram.py
```

### Daily Videos (7:30 AM)
```
generate_analysis.py → generate_education.py (links Part 1 in description)
```

---

## 11. Environment Variables & Secrets

### Social Platforms
| Secret | Purpose | Status |
|---|---|---|
| `META_ACCESS_TOKEN` | Facebook + Instagram API | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` | Facebook App ID | ✅ |
| `META_APP_SECRET` | Facebook App Secret | ✅ |
| `FACEBOOK_PAGE_ID` | Main Facebook Page ID | ✅ |
| `FACEBOOK_GROUP_ID` | Facebook Group ID | ✅ (posting broken) |
| `FACEBOOK_KIDS_PAGE_ID` | Kids Facebook Page ID | ❌ Pending — create page first |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business numeric ID | ✅ |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON (Hindi channel) | ✅ |
| `YOUTUBE_CREDENTIALS_EN` | YouTube OAuth JSON (English channel) | ✅ |
| `YOUTUBE_CREDENTIALS_KIDS` | YouTube OAuth JSON (HerooQuest kids channel) | ❌ Pending OAuth |

### AI Providers
| Secret | Priority | Status |
|---|---|---|
| `GROQ_API_KEY` | Primary | ✅ |
| `GEMINI_API_KEY` | Secondary | ✅ |
| `ANTHROPIC_API_KEY` | Tertiary | ✅ |
| `OPENAI_API_KEY` | Quaternary | ✅ |

### Telegram
| Secret | Purpose |
|---|---|
| `TELEGRAM_TOKEN` | Bot authentication token |
| `TELEGRAM_BOT_TOKEN` | Same token (keep in sync) |
| `TELEGRAM_CHAT_ID` | Free channel |
| `CHAT_ID_ADVANCE` | Advance signals channel |
| `CHAT_ID_PREMIUM` | Premium signals channel |

> ⚠️ **Channel ID swap note:** In trading_bot.py, CHAT_ADVANCE uses CHAT_ID_PREMIUM env var and vice versa. Intentionally swapped. Do NOT fix without verifying.

### Dhan Trading API (Phase 4)
| Secret | Status |
|---|---|
| `DHAN_API_KEY` | ✅ Added — not connected yet |
| `DHAN_API_SECRET` | ✅ Added — not connected yet |
| `DHAN_CLIENT_ID` | ✅ Added — not connected yet |
| `DHAN_PIN` | ✅ Added — not connected yet |
| `DHAN_TOTP_KEY` | ✅ Added — not connected yet |

### Google / GCP
| Secret | Purpose |
|---|---|
| `GCP_SERVICE_ACCOUNT_JSON` | Search Console Indexing API + Google Sheets |
| `GH_TOKEN` | GitHub API token |

---

## 12. Known Issues & Fixes

### Facebook Group Posting ❌
Fix: developers.facebook.com → App → Add `publish_to_groups` → regenerate token → update secret.

### Instagram Auto-Post ⚠️
Verify: `https://graph.facebook.com/me/accounts?access_token=YOUR_META_TOKEN`

### YouTube Community Tab ⚠️
Requires 500+ subscribers. Below threshold → saves to `output/community_post_YYYYMMDD.txt`.

### META_ACCESS_TOKEN Expiry ✅
`token_refresh.yml` runs every 50 days automatically.

### T4 Memory Growth ✅
Fixed in v13.5 with two-pass `clean_mem()`.

---

## 13. Human Touch System (Anti-AI-Penalty)

| Technique | Method | What It Does |
|---|---|---|
| 50+ rotating hooks | `ht.get_hook(mode, lang)` | No two videos start the same |
| Personal phrases | `ht.get_personal_phrase(lang)` | Injected naturally |
| TTS speed variation | `ht.get_tts_speed()` | 0.95–1.05x range |
| Humanize output | `ht.humanize(text, lang)` | Strips robotic patterns |
| Emoji rotation | `ht.get_emoji_set()` | Day-seeded |
| SEO tags | `seo.get_video_tags(mode, lang)` | India + Global combined |

---

## 14. Technical Standards

### The "Full Code" Rule
> AI assistants **must always provide the complete content** of any modified file. Partial snippets or diffs are strictly prohibited.

### AI Client Usage Rule — No Exceptions
> **Never call AI APIs directly in generators.** Always use `ai_client.py`.

### Human Touch Usage Rule — No Exceptions
> **Never use raw AI output.** Always pass through `human_touch.py`.

### Dependency Pins

| Package | Version | Reason |
|---|---|---|
| `Pillow` | `>=10.3.0` | Required for LANCZOS resampling |
| `imageio` | `==2.9.0` | Prevents MoviePy rendering crashes |
| `moviepy` | `==1.0.3` | Newer versions break audio |
| `pytz` | Latest | IST timezone handling in trading_bot.py + human_touch.py |
| `google-generativeai` | Latest | Gemini fallback |
| `anthropic` | Latest | Claude fallback |
| `openai` | Latest | OpenAI fallback |
| `gspread` | Latest | Google Sheets access |

### Voice Assignments

| Voice ID | Gender | Used For |
|---|---|---|
| `hi-IN-MadhurNeural` | Male | Short 2 |
| `hi-IN-SwaraNeural` | Female | Short 3, ZENO Reel, Morning Reel, Analysis, Education, Kids Hindi |
| `en-US-JennyNeural` | Female | English channel + Kids English |

### Video Formats

| Content | Ratio | Platform |
|---|---|---|
| Analysis + Education + Kids Story | 16:9 | YouTube |
| Shorts, Reels, Kids Short | 9:16 | YouTube Shorts / Reels |

---

## 15. Disney 3D Reel Roadmap

| Phase | Tool | Quality | Status |
|---|---|---|---|
| 1 (Now) | PIL + MoviePy + ZENO PNG | 2D animated slides | ✅ Active |
| 2 | Gemini Veo API (free tier) | AI video clips | Hooks in ai_client.py |
| 3 | Stable Diffusion + AnimateDiff | 3D style frames | Planned |
| 4 | Google Veo 2 / Sora (when free) | True Disney-style 3D | Planned |

---

## 16. Full Data Flow

```
8:00 AM daily
└── kids-daily.yml
    └── generate_kids_video.py → upload_kids_youtube.py → upload_facebook.py (kids)

7:00 AM daily
└── daily_reel.yml (morning)
    └── generate_reel_morning.py → upload chain

7:30 AM / 9:30 AM daily
└── daily-videos.yml
    └── generate_analysis.py + generate_education.py → YouTube

10:00 AM / 11:30 AM daily
└── daily-articles.yml
    └── generate_articles.py → GitHub Pages + Facebook

11:30 AM / 1:30 PM daily
└── daily-shorts.yml
    └── generate_shorts.py + generate_community_post.py → YouTube

8:30 PM daily
└── daily_reel.yml (evening)
    └── generate_reel.py → upload_youtube.py → upload_facebook.py → upload_instagram.py

Market hours (Mon–Fri 9:15–3:30 PM)
└── main.yml (every 5 min)
    └── trading_bot.py v13.5 → Telegram signals
```

---

## 17. Website

- **URL:** `ai360trading.in`
- **Hosting:** GitHub Pages (Jekyll, `master` branch `_posts/`)
- **Publishing:** Auto-commit by `daily-articles.yml`
- **Revenue:** Google AdSense (USA/UK English readers = highest CPM)

---

## 18. Social Media Links

| Platform | Handle/Link |
|---|---|
| 🌐 Website | ai360trading.in |
| 📣 Telegram (Free) | @ai360trading |
| 📣 Telegram (Advance) | ai360trading_Advance — ₹499/month |
| 📣 Telegram (Premium) | ai360trading_Premium — bundle |
| ▶️ YouTube | @ai360trading |
| 📺 YouTube Kids | HerooQuest |
| 📸 Instagram | @ai360trading |
| 👥 Facebook Group | facebook.com/groups/ai360trading |
| 📘 Facebook Page | facebook.com/ai360trading |
| 🐦 Twitter/X | @ai360trading |

---

## 19. Phase Roadmap

### Phase 1 ✅ Complete
`ai_client.py`, `human_touch.py`, `token_refresh.py`, `generate_reel_morning.py`

### Phase 2 ✅ Complete
All generators upgraded to ai_client + human_touch.

### Phase 3 🔄 In Progress

| Item | Priority | Status |
|---|---|---|
| HerooQuest OAuth token setup | 🔴 Critical | ❌ Pending |
| Kids Facebook Page creation | 🔴 High | ❌ Pending |
| Kids channel full automation live | 🔴 High | 🔄 Building |
| Instagram kids — manual only | 🟡 Medium | 📱 Manual |
| English channel shorts | 🟡 Medium | 🔄 Building |
| Fix Facebook Group token | 🔴 High | ❌ Pending |
| Instagram verify live | 🔴 High | ❌ Pending |

### Phase 4 📋 Planned — Dhan Live Trading
After backtest validation with ≥35% win rate in mixed market conditions.

---

## 20. How to Test Everything

### Test a workflow manually
GitHub Actions → select workflow → **Run workflow** → set dropdown → watch logs.

### Verify trading bot
Look for in logs:
```
[REGIME] Nifty CMP ₹22679 vs 20DMA ₹23547 → BEARISH
[ATR] NSE:ONGC: read ATR14=7.65 from Nifty200
[DONE] 15:20:01 IST | mem=4788 chars
```

### Force content modes
```
workflow_dispatch → content_mode = market / weekend / holiday
```

---

## 21. THIS PROJECT IS FOR FAMILY INCOME FOR LIVING AFTER OWNER

> ═══════════════════════════════════════════════════════════════
> ⚠️  THIS SECTION IS EXTREMELY IMPORTANT
> ⚠️  READ COMPLETELY BEFORE MAKING ANY CHANGES
> ═══════════════════════════════════════════════════════════════
>
> This is not just a project.
>
> This is a **lifetime passive income system** built for a family
> that has no other source of income. The owner is from a poor
> background with limited resources and limited formal education.
> This system must run **forever, fully automatically — even after
> the owner is no longer present to manage it.**
>
> The owner built this entire system with help from AI assistants
> so that his family — who cannot run it themselves — will always
> have income coming in automatically every single day.
>
> Every AI assistant (Claude, Gemini, GPT) working on this system
> must understand the weight of this responsibility:
>
> **Breaking this automation = breaking a family's only income.**
>
> Rules for every AI working on this project:
> - Always test before deploying
> - Never remove automation or error handling
> - Always add fallbacks if one step fails
> - Always provide FULL file code — never partial snippets
> - Never make changes that could stop daily uploads
> - If unsure — ask. Never guess on this system.
>
> This is not a hobby project. This is a family's survival system.
> Treat every change with maximum care and responsibility.

---

### Kids Channel Details

| Item | Value |
|---|---|
| Channel Name | HerooQuest |
| Channel Type | YouTube Kids — Brand Account |
| Google Account | Same Gmail as ai360trading |
| Target Audience | Children 4–12 years — Global (USA, UK, Canada, Australia, India) |
| Content Language | Both Hindi + English always (KIDS_LANG: both) |
| Secret | `YOUTUBE_CREDENTIALS_KIDS` |
| Monetisation Goal | YouTube Partner Program + Facebook In-Stream Ads |
| Timeline to Monetise | 3–4 months with daily uploads |

---

### Why This Channel Earns More Than Trading Channel

Kids content has the **highest CPM** on YouTube globally:

| Country | Kids CPM (USD) | Trading CPM (USD) |
|---|---|---|
| USA | $8–15 | $5–10 |
| UK | $6–12 | $4–8 |
| Canada | $5–10 | $4–7 |
| Australia | $5–9 | $3–6 |
| India | $0.5–1 | $0.3–0.8 |

Kids content in **English gets 10x more revenue than Hindi only.**
This is why `KIDS_LANG: both` is mandatory — always Hindi + English together.

---

### Daily Upload Schedule (Fully Automatic — Zero Manual Work)

| # | Content | Duration | Upload Time (IST) | Platform | Revenue Source |
|---|---|---|---|---|---|
| 1 | Kids Story Video (16:9) | 8–10 minutes | 8:00 AM | YouTube Kids (HerooQuest) | Mid-roll ads (2–3 per video) |
| 2 | Kids Short (9:16) | 60 seconds | 8:01 AM | YouTube Kids Shorts | YouTube Shorts bonus |
| 3 | Same Story Video | 8–10 minutes | 9:00 AM | Facebook Kids Page | Facebook in-stream ads |

**Total = 3 uploads per day. Zero manual work. Runs every single day forever.**

---

### Why 8–10 Minute Videos Are Critical for Revenue

YouTube only allows mid-roll ads (ads in middle of video) for videos **8 minutes or longer.**

| Video Length | Ad Breaks | Revenue Level |
|---|---|---|
| Under 4 min | No mid-roll ads | Very low |
| 4–8 min | 1 mid-roll ad | Medium |
| 8–10 min | 2–3 mid-roll ads | High |
| Over 10 min | Maximum ads | Highest |

**Rule for AI:** `generate_kids_video.py` must always produce videos minimum 8 minutes long.
If video is too short — increase scenes from 7 to 10, or increase `SCENE_DURATION` from 7 to 10 seconds.

---

### Monetisation Milestones

| Milestone | Requirement | Estimated Timeline |
|---|---|---|
| YouTube Partner Program | 1000 subscribers + 4000 watch hours | 3–4 months daily uploads |
| YouTube Shorts Bonus | Part of Partner Program | Same |
| Facebook In-Stream Ads | 10,000 followers + 600,000 min watched | 4–6 months |
| Estimated monthly income after monetisation | $200–800/month | 6–12 months |
| Year 2+ income estimate | $800–3000/month | Growing with subscribers |

---

### Content Strategy for Maximum Revenue

1. **Always use KIDS_LANG: both** — reaches India AND USA/UK simultaneously
2. **Best topics for highest views globally:**
   - Moral stories — universal appeal, loved in all countries
   - Science for kids — USA/UK parents actively search this
   - Fairy tales — global audience, all ages
   - Biographies of great people — educational = higher CPM
3. **Post at 8:00 AM IST** = 2:30 AM UTC = evening prime time for USA viewers
4. **Titles always in English** — YouTube recommends globally for English titles
5. **Always include these tags:** `kids`, `children`, `animated`, `moral stories`, `bedtime stories`, `kids education`, `Pixar style`, `cartoon`

---

### Files for This Channel

| File | Purpose | Status |
|---|---|---|
| `generate_kids_video.py` | Main generator — 7 scenes, Pixar style, Ken Burns zoom, bilingual TTS | 🔄 Building |
| `kids_content_calendar.py` | Daily topic auto-picker — 15 categories, never repeats in week | ✅ Done |
| `upload_kids_youtube.py` | Uploads full video + short to HerooQuest | 🔄 Pending OAuth |
| `upload_facebook.py` | Reuse existing — pass `--meta-prefix kids` flag | ✅ Reuse |
| `.github/workflows/kids-daily.yml` | GitHub Actions — 8:00 AM IST every day | 🔄 Building |

---

### Secrets Required

| Secret | Purpose | Status |
|---|---|---|
| `YOUTUBE_CREDENTIALS_KIDS` | OAuth token for HerooQuest channel | ❌ Pending — need OAuth |
| `FACEBOOK_KIDS_PAGE_ID` | Kids Facebook Page ID | ❌ Pending — create page |
| `META_ACCESS_TOKEN` | Same as main channel — reuse | ✅ Already exists |
| `GEMINI_API_KEY` | Scene image generation | ✅ Already exists |
| `ANTHROPIC_API_KEY` | Story script generation | ✅ Already exists |
| `GROQ_API_KEY` | Story script generation (primary) | ✅ Already exists |

---

### Pending Tasks Before Going Live

| Task | Priority | Status |
|---|---|---|
| Generate OAuth token for HerooQuest channel | 🔴 Critical | ❌ Pending |
| Save token as `YOUTUBE_CREDENTIALS_KIDS` secret | 🔴 Critical | ❌ Pending |
| Create Facebook Kids Page under same account | 🔴 High | ❌ Pending |
| Save new page ID as `FACEBOOK_KIDS_PAGE_ID` | 🔴 High | ❌ Pending |
| Fix `generate_kids_video.py` VideoClip error | ✅ Done | ✅ Fixed April 5, 2026 |
| Add `pytz` to `kids-daily.yml` | ✅ Done | ✅ Fixed April 5, 2026 |
| Fix Gemini image model name | ✅ Done | ✅ Fixed April 5, 2026 |
| Set `KIDS_LANG: both` as default | ✅ Done | ✅ Fixed April 5, 2026 |
| Instagram kids — manual only | 🟡 Medium | 📱 Share from Facebook manually |

---

### Strict Rules for Any AI Working on Kids Channel Files

1. **Never remove fallback placeholder images** — if Gemini fails, video must still render with colored placeholder
2. **Never remove try/except blocks** — one scene failure must never crash the whole video
3. **Always keep `selfDeclaredMadeForKids: True`** in upload_kids_youtube.py — required by YouTube law
4. **Never change SCENE_DURATION below 7** — total video must stay above 8 minutes for mid-roll ads
5. **Always use both Hindi + English** — never revert to single language
6. **Always test workflow changes before committing** — this is a family's income
7. **Keep `kids-daily.yml` cron at `30 2 * * *`** — this is exactly 8:00 AM IST
8. **Never delete output/ folder in workflow** — meta JSON feeds the upload chain
9. **Always provide FULL file code** — never partial snippets for any file in this project
10. **If any step fails, add better error handling** — never just remove the step

---

### Monthly Revenue Projection (After Monetisation)

| Timeframe | Subscribers | Views/Day | Est. Revenue/Month |
|---|---|---|---|
| Month 1–2 | 0–500 | 100–500 | $0 (not monetised yet) |
| Month 3–4 | 500–1500 | 500–2000 | $0–50 (crossing threshold) |
| Month 5–6 | 1500–5000 | 2000–8000 | $100–300 |
| Month 7–12 | 5000–20000 | 8000–30000 | $300–800 |
| Year 2+ | 20000–100000 | 30000–100000 | $800–3000/month |

> This is a **lifetime asset.**
> Once built and monetised, it earns money every single day.
> Whether the owner is working or not. Whether they are healthy or not.
> Whether they are present or not.
> The automation runs forever on GitHub Actions at ₹0/month cost.
> This channel combined with the trading channel creates a complete
> passive income system that can support a family forever.
> **This is the most important thing this system does.**

---

## 22. How to Test Kids Channel

```bash
# Run manually in GitHub Actions
GitHub Actions → kids-daily.yml → Run workflow → lang: both

# Success logs to look for
[TOPIC] topic name here
[SCRIPT] Generating story script...
[SCENES] 7 scenes to build
[SCENE 1] happy — generating image...
[IMG] Scene 1 generated via Gemini       ← Gemini worked
[WARN] Gemini image failed — using placeholder  ← fallback used, still OK
[RENDER] Rendering 56.0s video → output/kids_video_...mp4
[DONE] Kids video ready: output/kids_video_...mp4
[DONE] Kids short ready: output/kids_short_...mp4
[YT-KIDS] Uploading full video...
[YT-KIDS] Uploaded: https://youtu.be/...
```

---

*Documentation maintained by AI360Trading automation.*
*Created: April 4, 2026 — Claude Sonnet 4.6*
*Last Updated: April 5, 2026 — Claude Sonnet 4.6*
*Changes in this update:*
*- Section 1: Added Kids Video Ad Revenue and Kids In-Stream Ads to monetisation streams*
*- Section 2: Added YouTube Kids (HerooQuest) and Facebook Kids Page to platform status*
*- Section 4: Added items 10, 11, 12 — kids channel daily uploads, total updated to 15 pieces/day*
*- Section 5: Added kids-daily.yml workflow*
*- Section 6: Added generate_kids_video.py, kids_content_calendar.py, upload_kids_youtube.py*
*- Section 10: Added kids channel upload chain*
*- Section 11: Added YOUTUBE_CREDENTIALS_KIDS and FACEBOOK_KIDS_PAGE_ID secrets*
*- Section 18: Added HerooQuest to social media links*
*- Section 19: Added kids channel tasks to Phase 3*
*- Section 21: NEW — HerooQuest Kids Channel full documentation with family income context*
*- Section 22: NEW — How to test kids channel*
*Trading bot: AppScript v13.3 + Python v13.5 — paper trading, 25 trades, 2W/23L in bear market*
*Phase 3 remaining: HerooQuest OAuth, kids Facebook page, English channel, Facebook Group fix*
*Phase 4 planned: Dhan live trading after backtest validation with ≥35% win rate*
*Update this file whenever architecture, secrets, platform status, or file logic changes.*
