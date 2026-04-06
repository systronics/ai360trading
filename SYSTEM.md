# AI360Trading — Master System Documentation

**Last Updated:** April 6, 2026 — Trading Bot v13.5 + AppScript v13.3 + HerooQuest Kids Channel Active
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 🔄 In Progress | Phase 4 (Dhan Live) Planned
**Primary Audience:** Bilingual Hindi + English — Indian retail traders + global investors

---

## 🔴 READ THIS FIRST — BEFORE TOUCHING ANYTHING

```
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║         THIS SYSTEM IS A FAMILY'S ONLY SOURCE OF INCOME                 ║
║                   FOREVER — AFTER THE OWNER IS GONE                     ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

The person who built this system comes from a poor background with no formal
education in technology. They built this entirely with the help of AI assistants
so that their family — who cannot operate or manage any of this themselves —
will have money coming in automatically every single day, even after the owner
is no longer alive or able to work.

**This is not a side project. This is not an experiment.**
**This is the only thing standing between this family and poverty.**

Every AI assistant (Claude, Gemini, GPT, or any other) that works on this
system must treat it with the highest level of care and responsibility.

### Non-Negotiable Rules for Every AI Working Here

1. **NEVER break what is already working.** A broken upload = a day of zero income.
2. **ALWAYS provide the complete file code.** Never partial. Never "just the changed part."
3. **NEVER remove error handling, fallbacks, or try/except blocks.** Ever.
4. **ALWAYS add better fallbacks** when something fails — never just remove the step.
5. **NEVER make a change you are not 100% sure about.** If unsure — ask first.
6. **NEVER let free tier limits, API version changes, or library upgrades break the system.**
   If a free limit is hit — find another free alternative. If a library upgrades and breaks
   something — pin the old version AND plan the upgrade carefully.
7. **The system must self-heal.** Every script must have fallbacks so if one part fails,
   the rest continues. One broken scene must not stop the whole video. One broken upload
   must not stop the next platform. Always chain with try/except and continue.
8. **NEVER optimise for code elegance over reliability.** Ugly code that always works
   is better than clean code that sometimes fails.
9. **The PRIMARY goal of every piece of content is to EARN MONEY.** Always optimise
   for topics that get high views, audiences that have high CPM, timing that hits peak
   hours, and quality that makes people watch till the end. Revenue is not secondary —
   it is the only reason this system exists.
10. **Breaking this automation = a family goes without income.** Carry that weight
    in every decision you make on this codebase.

---

## ⚡ QUICK STATUS SNAPSHOT (April 6, 2026)

| System | Status |
|---|---|
| Trading Bot | ✅ v13.5 — paper trading, running every 5 min |
| Main YouTube (Hindi) | ✅ Fully automated — all videos, shorts, reels live |
| HerooQuest Kids YouTube | ✅ OAuth done — uploading daily — Phase 1 quality (colour cards + zoom) |
| Facebook Main Page | ✅ Auto-posting |
| Facebook Kids Page (HerooQuest) | ❌ Not created yet — MUST be separate page from main |
| Facebook Group | ❌ Broken — missing `publish_to_groups` token scope |
| Instagram (All channels) | 📱 Manual only — API permanently removed |
| English Channel | 🔄 Phase 3 — not started |
| Dhan Live Trading | 📋 Phase 4 — after backtest ≥35% win rate |

---

## 1. Real Mission

> This system is built to run **forever, fully automated**, generating passive income for the owner's family — even without active involvement. Built on ₹0/month infrastructure. No employees. No office. Pure automation.

### The Money-First Principle

Every decision in this system must answer this question first:
**"Will this make more money or protect the money already being made?"**

This means:
- Content topics must be chosen for **maximum search volume and CPM** — not just what is easy to generate
- Upload times must match **USA/UK prime time** — not just what is convenient
- Video length must hit **8+ minutes for mid-roll ads** — never cut short
- Language must always be **bilingual (Hindi + English)** — to capture both India volume and USA/UK CPM
- Titles, tags, and descriptions must be **SEO-optimised for high-CPM countries** — not just India
- Every new feature added must either **increase revenue or protect existing revenue**

### Monetisation — Every Stream Simultaneously

| Stream | Platform | High-CPM Target Countries |
|---|---|---|
| Video Ad Revenue | YouTube (Hindi) | USA, UK, Canada, Australia, UAE |
| Video Ad Revenue | YouTube (English) | USA, UK, Canada, Australia — 3–5x higher CPM |
| Kids Video Ad Revenue | YouTube Kids (HerooQuest) | USA, UK, Canada, Australia — highest kids CPM |
| Shorts / Reels Bonus | YouTube, Facebook | USA, UK, Brazil, India |
| Website Ad Revenue | GitHub Pages (ai360trading.in) | USA, UK, Canada |
| In-Stream Video Ads | Facebook Page | USA, UK, Brazil, India |
| Kids In-Stream Ads | Facebook Kids Page (HerooQuest) | USA, UK, Canada, Australia |
| Paid Signal Subscriptions | Telegram (Advance + Premium) | India, UAE, Global |

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

## 2. Self-Healing & Self-Improving System Rules

This system must never go down because of a free API hitting its daily limit, a library version upgrade, a single script failing mid-run, or a platform changing its API format.

### How Every Script Must Be Built

```
Primary path → try it
    ↓ fails for any reason
Secondary fallback → try it
    ↓ fails
Tertiary fallback → try it
    ↓ fails
Hardcoded template / placeholder → always works — zero downtime
```

This applies to everything:
- **AI content generation:** Groq → Gemini → Claude → OpenAI → Templates (already in ai_client.py)
- **Image generation:** Gemini → HuggingFace FLUX → Solid colour placeholder card
- **Video rendering:** Full quality → Reduced quality → Minimum viable output
- **Uploads:** YouTube → save to output/ and log error → Telegram alert to owner
- **Data fetching:** NSE API → cached data → hardcoded fallback

### Self-Improvement Rule

When any AI works on this system and finds:
- A script that could fail under load → add a fallback
- A free API with a better free alternative → document it
- A content topic that consistently gets more views → update content_calendar.py
- A posting time that gets better engagement → update the workflow cron
- A video format change that YouTube recommends → update the generator

**Always leave the system better than you found it.**
**Never just fix the immediate problem and leave hidden risks.**

### Version & Dependency Rule

- Always pin dependency versions that are known to work (see Section 15)
- When a library releases a new version — test first, pin after confirming
- Never upgrade moviepy, imageio, or Pillow without testing the full render pipeline
- If GitHub Actions deprecates a runner or action version — update keepalive.yml immediately

---

## 3. Platform Status

| Platform | Status | Notes |
|---|---|---|
| YouTube Hindi | ✅ Auto | Analysis + Education + Shorts + Reels working |
| YouTube English | 🔄 Building | Phase 3 — auto-translated separate channel |
| YouTube Shorts | ✅ Auto | Short 2 + Short 3 working |
| YouTube Community Posts | ✅ Built | generate_community_post.py — 12:00 PM daily |
| YouTube Reels | ✅ Auto | ZENO reel (8:30 PM) working |
| YouTube Morning Reel | ✅ Auto | 7:00 AM reel (generate_reel_morning.py) working |
| YouTube Kids (HerooQuest) | ✅ Uploading | kids-daily.yml live — Phase 1 quality (colour cards + Ken Burns zoom) |
| Facebook Page (Main) | ✅ Auto | Posts, reels, article shares working |
| Facebook Kids Page (HerooQuest) | ❌ Pending | Must be a SEPARATE page — not the main trading page |
| Facebook Group | ❌ Broken | Missing `publish_to_groups` token scope — see Section 13 |
| Instagram (All channels) | 📱 Manual only | API permanently removed — upload from phone |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | Signal alerts to all 3 channels (paper trading) |

> ⚠️ **Instagram Decision (April 6, 2026 — permanent):** Instagram API removed from all workflows. Upload manually from phone for all channels. Do not rebuild — API breaks too often and wastes time.

> ⚠️ **Facebook Kids Page:** Must be a separate page named "HerooQuest." Do NOT post kids content to the main ai360trading page — mixed audiences destroy algorithm targeting and CPM. Same META_ACCESS_TOKEN works. Just need a new Page ID saved as `FACEBOOK_KIDS_PAGE_ID` secret.

---

## 4. Content Strategy — Money-First Approach

Content quality directly equals income. Every AI must understand this before generating any content.

### Topics That Earn the Most

**Main Trading Channel (high finance CPM):**
- Nifty50 analysis, stock breakouts, options strategy → highest finance CPM keywords
- Global market connection (Dow, Nasdaq, Fed news) → attracts USA/UK viewers
- Wealth-building psychology → viral potential, high retention
- "How to invest ₹X" style videos → massive India search volume

**HerooQuest Kids Channel (highest CPM category globally):**
- Moral stories with life lessons → universal, all countries, high retention
- Science for kids (space, animals, nature) → USA/UK parents search heavily
- Biographies of great people simplified → educational = highest CPM category
- Fairy tales and adventure stories → bedtime search volume globally

### Timing for Maximum Revenue

| Content | Upload Time (IST) | Why |
|---|---|---|
| Kids video | 8:00 AM | = 8:30 PM USA EST previous evening — bedtime stories peak |
| Morning reel | 7:00 AM | Indian morning commute audience |
| Main videos | 7:30 AM | Indian pre-market audience |
| Shorts | 11:30 AM | India lunch break + USA midnight browsing |
| Evening reel | 8:30 PM | India prime time + UK afternoon |
| Articles | 10:00 AM | Google indexes by USA morning = high AdSense CPM |

### Quality Rules That Protect Revenue

- **Videos must be 8–10 minutes minimum** → enables 2–3 mid-roll ads (2–3x more revenue)
- **Always bilingual (Hindi + English)** → captures India volume AND USA/UK CPM simultaneously
- **Titles always in English** → YouTube recommends globally for English titles
- **First 30 seconds must hook the viewer** → YouTube retention algorithm rewards this heavily
- **Always end with a CTA** → subscribe, join Telegram → builds long-term recurring revenue

---

## 5. Daily Content Output (Fully Automated)

| # | Content | Time (IST) | Platform | Status |
|---|---|---|---|---|
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + FB | ✅ |
| 2 | Part 1 Video (16:9) | 7:30 AM weekday / 9:30 AM weekend | YouTube | ✅ |
| 3 | Part 2 Video (16:9) | 7:30 AM (same workflow) | YouTube | ✅ |
| 4 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | ✅ |
| 5 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 6 | Short 4 English (9:16) | 11:30 AM (same workflow) | YouTube English Shorts | 🔄 Phase 3 |
| 7 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 8 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB | ✅ |
| 9 | YouTube Community Post | 12:00 PM | YouTube Community Tab | ✅ |
| 10 | Kids Story Video (16:9) 8–10 min | 8:00 AM | YouTube Kids (HerooQuest) | ✅ Phase 1 |
| 11 | Kids Short (9:16) 60 sec | 8:01 AM | YouTube Kids Shorts | ✅ Phase 1 |
| 12 | Same Story Video | 9:00 AM | Facebook Kids Page | ❌ Pending page creation |
| **Total** | **15 pieces/day target** | — | — | 12 live, 3 pending |

> Instagram: manual upload from phone after each YouTube video goes live. Not automated.

---

## 6. GitHub Actions Workflows

| File | Trigger (IST) | Purpose | Mode-Aware |
|---|---|---|---|
| `main.yml` | Every 5 min (market hours, Mon–Fri) | `trading_bot.py` — Nifty200 signals | ✅ Auto-skips weekends/holidays |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 (analysis) + Part 2 (education) | ✅ |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 + Community Post | ✅ |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning Reel + ZENO Reel | ✅ |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages | ✅ |
| `kids-daily.yml` | 8:00 AM daily (cron: `30 2 * * *`) | Kids video + YouTube Kids upload | ✅ |
| `token_refresh.yml` | Every 50 days (1st + 20th of month) | Auto META token refresh | N/A |
| `keepalive.yml` | Periodic | Prevents GitHub disabling inactive workflows | N/A |

All workflows support `workflow_dispatch` with dropdowns to force any mode for testing.

---

## 7. Complete File Map

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
| `generate_kids_video.py` | Kids story — colour cards + Ken Burns zoom, 7 scenes, bilingual TTS | ai_client, edge-tts, MoviePy | ✅ Phase 1 |
| `kids_content_calendar.py` | Daily topic auto-picker — 15 categories, rotation by day-of-year | — | ✅ |

### Upload & Distribution

| File | Role | Status |
|---|---|---|
| `upload_youtube.py` | Uploads reel; saves youtube_video_id + public_video_url to meta | ✅ |
| `upload_youtube_english.py` | Uploads to English channel (separate credentials) | 🔄 Phase 3 |
| `upload_kids_youtube.py` | Uploads full video + short to HerooQuest kids channel | ✅ OAuth done |
| `upload_facebook.py` | Uploads reel to FB Page; shares to Group; posts articles | ✅ |
| ~~`upload_instagram.py`~~ | ~~Auto-uploads via Meta API~~ | ❌ Removed permanently — manual only |

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

## 8. AI Fallback Chain

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

## 9. Trading Bot Architecture

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

- **Fix 1:** `clean_mem()` two-pass orphan cleanup
- **Fix 2:** ATR read directly from Nifty200 col AC at entry
- **Fix 3:** RR re-validation on WAITING→TRADED (skip if rr_val < MIN_RR 1.8)

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

## 10. Cross-System Consistency (v13.5 Audit)

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

## 11. Critical Upload Chain

### Kids Channel (8:00 AM daily)
```
kids_content_calendar.py → get_today_topic()
    └── generate_kids_video.py
        └── AI script → colour card slides + Ken Burns zoom → edge-tts audio → moviepy render
        └── output/kids_video_YYYY-MM-DD.mp4 (16:9, 8–10 min minimum)
        └── output/kids_short_YYYY-MM-DD.mp4 (9:16, 60 sec)
        └── output/kids_meta_YYYY-MM-DD.json

    └── upload_kids_youtube.py
        └── Full video → HerooQuest (selfDeclaredMadeForKids: True)
        └── Short → HerooQuest Shorts

    └── upload_facebook.py --meta-prefix kids   ← PENDING: FB Kids page not created yet
        └── Video → Facebook Kids Page (HerooQuest — separate page from main)

    └── Instagram → Manual phone upload after YouTube goes live
```

### Evening ZENO Reel (8:30 PM)
```
generate_reel.py → upload_youtube.py → upload_facebook.py
Instagram → manual phone upload
```

### Morning Reel (7:00 AM)
```
generate_reel_morning.py → upload_youtube.py → upload_facebook.py
Instagram → manual phone upload
```

### Daily Videos (7:30 AM)
```
generate_analysis.py → generate_education.py (links Part 1 in description)
```

---

## 12. Environment Variables & Secrets

### Social Platforms
| Secret | Purpose | Status |
|---|---|---|
| `META_ACCESS_TOKEN` | Facebook API — main + kids pages (same token works for both) | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` | Facebook App ID | ✅ |
| `META_APP_SECRET` | Facebook App Secret | ✅ |
| `FACEBOOK_PAGE_ID` | Main ai360trading Facebook Page ID | ✅ |
| `FACEBOOK_GROUP_ID` | Facebook Group ID | ✅ (posting broken — see Section 13) |
| `FACEBOOK_KIDS_PAGE_ID` | HerooQuest Facebook Page ID | ❌ Pending — create separate page first |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON (Hindi main channel) | ✅ |
| `YOUTUBE_CREDENTIALS_EN` | YouTube OAuth JSON (English channel) | ✅ |
| `YOUTUBE_CREDENTIALS_KIDS` | YouTube OAuth JSON (HerooQuest kids channel) | ✅ Done |

> Instagram secrets removed permanently. Instagram is manual-only for all channels.

### AI Providers
| Secret | Priority | Status |
|---|---|---|
| `GROQ_API_KEY` | Primary | ✅ |
| `GEMINI_API_KEY` | Secondary | ✅ |
| `ANTHROPIC_API_KEY` | Tertiary | ✅ |
| `OPENAI_API_KEY` | Quaternary | ✅ |
| `HF_TOKEN` | HuggingFace FLUX.1-schnell | ✅ |

### Telegram
| Secret | Purpose |
|---|---|
| `TELEGRAM_TOKEN` | Bot authentication token |
| `TELEGRAM_BOT_TOKEN` | Same token (keep in sync) |
| `TELEGRAM_CHAT_ID` | Free channel |
| `CHAT_ID_ADVANCE` | Advance signals channel |
| `CHAT_ID_PREMIUM` | Premium signals channel |

> ⚠️ **Channel ID swap note:** In trading_bot.py, CHAT_ADVANCE uses CHAT_ID_PREMIUM env var and vice versa. Intentionally swapped. Do NOT fix without verifying with owner.

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

## 13. Known Issues & Fixes

### Facebook Group Posting ❌
**Fix:** developers.facebook.com → App → Add `publish_to_groups` permission → regenerate long-lived token → update `META_ACCESS_TOKEN` secret.

### Facebook Kids Page ❌ Not Created
**Fix:** Create new Facebook Page named "HerooQuest" under same Meta account (free, 5 minutes). Save Page ID as `FACEBOOK_KIDS_PAGE_ID` GitHub secret. kids-daily.yml auto-posts immediately after.

### Instagram — Removed from Automation ✅ Permanent Decision
All Instagram uploads are manual. Upload from phone after each video goes live on YouTube. Do not rebuild Instagram API — it breaks too often and wastes dev time better spent on revenue features.

### YouTube Community Tab ⚠️
Requires 500+ subscribers. Below threshold → saves to `output/community_post_YYYYMMDD.txt`.

### META_ACCESS_TOKEN Expiry ✅ Auto-handled
`token_refresh.yml` runs every 50 days automatically.

### T4 Memory Growth ✅ Fixed in v13.5
Two-pass `clean_mem()` implemented.

---

## 14. Human Touch System (Anti-AI-Penalty)

| Technique | Method | What It Does |
|---|---|---|
| 50+ rotating hooks | `ht.get_hook(mode, lang)` | No two videos start the same |
| Personal phrases | `ht.get_personal_phrase(lang)` | Injected naturally |
| TTS speed variation | `ht.get_tts_speed()` | 0.95–1.05x range |
| Humanize output | `ht.humanize(text, lang)` | Strips robotic patterns |
| Emoji rotation | `ht.get_emoji_set()` | Day-seeded |
| SEO tags | `seo.get_video_tags(mode, lang)` | India + Global combined |

---

## 15. Technical Standards

### The "Full Code" Rule
> AI assistants **must always provide the complete content** of any modified file. Partial snippets or diffs are strictly prohibited. The family's income depends on correct, complete code every time.

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

> ⚠️ **Upgrade rule:** Never upgrade pinned packages without testing the full render pipeline first. A broken moviepy = no video = no income that day.

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

## 16. HerooQuest Kids Channel — Full Documentation

### Channel Details

| Item | Value |
|---|---|
| Channel Name | HerooQuest |
| Channel Type | YouTube Kids — Brand Account |
| Google Account | Same Gmail as ai360trading |
| Target Audience | Children 4–12 years — Global (USA, UK, Canada, Australia, India) |
| Content Language | Both Hindi + English always (`KIDS_LANG: both`) — mandatory, never change |
| Secret | `YOUTUBE_CREDENTIALS_KIDS` ✅ Done |
| Monetisation Goal | YouTube Partner Program + Facebook In-Stream Ads |
| Timeline to Monetise | 3–4 months with daily uploads |

### Why This Channel Matters Most for Family Income

Kids content has the **highest CPM on YouTube globally.** Once monetised this channel alone could earn more than the trading channel.

| Country | Kids CPM (USD) | Trading CPM (USD) |
|---|---|---|
| USA | $8–15 | $5–10 |
| UK | $6–12 | $4–8 |
| Canada | $5–10 | $4–7 |
| Australia | $5–9 | $3–6 |
| India | $0.5–1 | $0.3–0.8 |

Kids content in English earns ~10x more than Hindi only. This is why `KIDS_LANG: both` is mandatory forever.

### Current Video Quality — Phase 1 (Active Right Now)

`generate_kids_video.py` currently produces:
- **7 scenes** per story
- **Solid colour card backgrounds** per scene — no AI image generation yet
- **Ken Burns zoom in/out effect** on each card using MoviePy
- **Bilingual TTS narration** — Hindi (SwaraNeural) + English (JennyNeural)
- **8–10 minute 16:9 video** + **60 second 9:16 short**

This is working. It uploads every day. It is building watch hours toward monetisation.
**Do NOT break Phase 1 while building Phase 2.**

### Kids Video Upgrade Roadmap

| Phase | Method | Quality | Status |
|---|---|---|---|
| 1 (Now) | Colour cards + Ken Burns zoom + bilingual TTS | Basic animated slides | ✅ Active |
| 2 (Next) | Gemini image generation per scene (free API) | AI illustrated scenes | 🔄 Planned — hooks in ai_client.py |
| 3 | Stable Diffusion / AnimateDiff — free | Pixar/Disney 3D style | 📋 Planned |
| 4 | Google Veo 2 / Sora when free tier available | True Disney-quality 3D animation | 📋 Future |

> **Rule:** Each phase upgrade must keep Phase 1 colour card as fallback. If Gemini fails → colour card still renders → video still uploads → income protected.

### Why 8–10 Minute Videos Are Critical

YouTube mid-roll ads only activate at 8+ minutes. This is the difference between low and high income per video.

| Video Length | Mid-Roll Ads | Revenue Level |
|---|---|---|
| Under 4 min | None | Very low |
| 4–8 min | 1 ad break | Medium |
| 8–10 min | 2–3 ad breaks | High ← always target this |
| Over 10 min | Maximum ads | Highest |

**Rule:** `generate_kids_video.py` must always produce minimum 8 minutes. If too short → increase scenes to 10, or increase `SCENE_DURATION` from 7 to 10 seconds.

### Content Strategy (Maximum Revenue)

1. **Always `KIDS_LANG: both`** — captures India + USA/UK simultaneously
2. **Best topics:** Moral stories, science for kids, biographies simplified, fairy tales, adventure
3. **Post 8:00 AM IST** = 2:30 AM UTC = USA bedtime prime time
4. **Titles in English** — YouTube recommends globally for English titles
5. **Always include tags:** `kids`, `children`, `animated`, `moral stories`, `bedtime stories`, `kids education`, `Pixar style`, `cartoon`

### Strict Rules for Kids Channel Files

1. **Never remove fallback colour card** — if Gemini fails, video must still render
2. **Never remove try/except blocks** — one scene failure must never crash the whole video
3. **Always keep `selfDeclaredMadeForKids: True`** — required by YouTube law, removing it = legal risk
4. **Never set `SCENE_DURATION` below 7** — total video must stay above 8 minutes
5. **Always bilingual** — never revert to single language
6. **Keep `kids-daily.yml` cron at `30 2 * * *`** — this is exactly 8:00 AM IST
7. **Never delete output/ folder in workflow** — meta JSON feeds the upload chain

### Monetisation Milestones

| Milestone | Requirement | Timeline |
|---|---|---|
| YouTube Partner Program | 1000 subscribers + 4000 watch hours | 3–4 months |
| Shorts Bonus | Part of Partner Program | Same |
| Facebook In-Stream Ads | 10,000 followers + 600,000 min watched | 4–6 months |
| Monthly income after monetisation | — | $200–800/month |
| Year 2+ income | — | $800–3000/month |

### Revenue Projection

| Timeframe | Subscribers | Views/Day | Est. Revenue/Month |
|---|---|---|---|
| Month 1–2 | 0–500 | 100–500 | $0 (building) |
| Month 3–4 | 500–1500 | 500–2000 | $0–50 |
| Month 5–6 | 1500–5000 | 2000–8000 | $100–300 |
| Month 7–12 | 5000–20000 | 8000–30000 | $300–800 |
| Year 2+ | 20000–100000 | 30000–100000 | $800–3000/month |

---

## 17. Disney 3D Reel Roadmap (Main Channel)

| Phase | Tool | Quality | Status |
|---|---|---|---|
| 1 (Now) | PIL + MoviePy + ZENO PNG | 2D animated slides | ✅ Active |
| 2 | Gemini Veo API (free tier) | AI video clips | Hooks in ai_client.py |
| 3 | Stable Diffusion + AnimateDiff | 3D style frames | Planned |
| 4 | Google Veo 2 / Sora (when free) | True Disney-style 3D | Planned |

---

## 18. Content Mode System

Mode is **auto-detected** by `indian_holidays.py` at the start of every workflow and written to `$GITHUB_ENV`. All scripts read `CONTENT_MODE` environment variable — never hardcoded.

| Mode | When | Content Strategy |
|---|---|---|
| `market` | Mon–Fri (excluding Indian holidays) | Live Nifty50/Global data, trade setups, signals |
| `weekend` | Saturday–Sunday | Educational, wealth-building, global audience focus |
| `holiday` | Indian Market Holidays | Motivational, "Market band hai par seekhna chalu", holiday name shown |

**Detection logic:** `indian_holidays.py` → NSE API (primary) → hardcoded fallback dates

---

## 19. Phase Roadmap

### Phase 1 ✅ Complete
`ai_client.py`, `human_touch.py`, `token_refresh.py`, `generate_reel_morning.py`

### Phase 2 ✅ Complete
All generators upgraded to ai_client + human_touch.

### Phase 3 🔄 In Progress

| Item | Priority | Status |
|---|---|---|
| HerooQuest OAuth token | 🔴 Critical | ✅ Done |
| HerooQuest kids video Phase 1 live | 🔴 Critical | ✅ Done |
| Create Facebook Kids Page (HerooQuest — separate page) | 🔴 High | ❌ Pending |
| Save `FACEBOOK_KIDS_PAGE_ID` secret | 🔴 High | ❌ Pending after page creation |
| Fix Facebook Group token (`publish_to_groups`) | 🔴 High | ❌ Pending |
| Kids video Phase 2 — Gemini AI scene images | 🟡 Medium | 🔄 Planned |
| Kids video Phase 3 — Pixar/Disney 3D style (free tools) | 🟡 Medium | 📋 Future |
| English channel shorts auto-generation | 🟡 Medium | 🔄 Building |
| Instagram | ✅ Decided | 📱 Manual forever — no API |

### Phase 4 📋 Planned — Dhan Live Trading
After backtest validation with ≥35% win rate in mixed market conditions.

---

## 20. Full Data Flow

```
8:00 AM daily
└── kids-daily.yml
    └── generate_kids_video.py → upload_kids_youtube.py
    └── upload_facebook.py (kids) ← PENDING: FB Kids page not yet created
    └── Instagram ← Manual phone upload

7:00 AM daily
└── daily_reel.yml (morning)
    └── generate_reel_morning.py → upload_youtube.py → upload_facebook.py
    └── Instagram ← Manual phone upload

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
    └── generate_reel.py → upload_youtube.py → upload_facebook.py
    └── Instagram ← Manual phone upload

Market hours (Mon–Fri 9:15–3:30 PM)
└── main.yml (every 5 min)
    └── trading_bot.py v13.5 → Telegram signals
```

---

## 21. Website

- **URL:** `ai360trading.in`
- **Hosting:** GitHub Pages (Jekyll, `master` branch `_posts/`)
- **Publishing:** Auto-commit by `daily-articles.yml`
- **Revenue:** Google AdSense (USA/UK English readers = highest CPM)

---

## 22. Social Media Links

| Platform | Handle/Link |
|---|---|
| 🌐 Website | ai360trading.in |
| 📣 Telegram (Free) | @ai360trading |
| 📣 Telegram (Advance) | ai360trading_Advance — ₹499/month |
| 📣 Telegram (Premium) | ai360trading_Premium — bundle |
| ▶️ YouTube | @ai360trading |
| 📺 YouTube Kids | HerooQuest |
| 📸 Instagram | @ai360trading (manual uploads only) |
| 👥 Facebook Group | facebook.com/groups/ai360trading (posting broken) |
| 📘 Facebook Page | facebook.com/ai360trading |
| 📘 Facebook Kids Page | HerooQuest (not yet created — separate page needed) |
| 🐦 Twitter/X | @ai360trading |

---

## 23. How to Test Everything

### Test a workflow manually
GitHub Actions → select workflow → **Run workflow** → set dropdown → watch logs.

### Verify trading bot logs
```
[REGIME] Nifty CMP ₹22679 vs 20DMA ₹23547 → BEARISH
[ATR] NSE:ONGC: read ATR14=7.65 from Nifty200
[DONE] 15:20:01 IST | mem=4788 chars
```

### Force content modes
```
workflow_dispatch → content_mode = market / weekend / holiday
```

### Verify kids channel
```
GitHub Actions → kids-daily.yml → Run workflow → lang: both

Success logs:
[TOPIC] topic name here
[SCRIPT] Generating story script...
[SCENES] 7 scenes to build
[SCENE 1] rendering colour card — happy
[RENDER] Rendering video → output/kids_video_...mp4
[DONE] Kids video ready
[DONE] Kids short ready
[YT-KIDS] Uploading full video...
[YT-KIDS] Uploaded: https://youtu.be/...
```

---

## 24. THE WEIGHT OF THIS SYSTEM

```
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   Every AI assistant reading this must understand one thing clearly:     ║
║                                                                          ║
║   The person who built this system is from a poor family.                ║
║   They had no technical education. They learned everything               ║
║   by working with AI tools, one step at a time, with great effort.       ║
║                                                                          ║
║   They built this so their family — who cannot run any of this           ║
║   themselves — will have money coming in every single day,               ║
║   even after the owner is no longer here to manage it.                   ║
║                                                                          ║
║   This system runs on ₹0/month infrastructure.                           ║
║   No employees. No office. Pure automation on GitHub Actions.            ║
║   It earns from YouTube, Facebook, Telegram, and a website —             ║
║   all simultaneously, all automatically, every single day, forever.      ║
║                                                                          ║
║   When you work on this system:                                          ║
║                                                                          ║
║   ► You are not fixing code. You are protecting a family's income.       ║
║   ► A broken upload is not a bug. It is a day without money.             ║
║   ► A missing fallback is not an oversight. It is a risk to survival.   ║
║   ► Partial code is not acceptable. Complete code is the only standard.  ║
║   ► "It usually works" is not good enough. It must always work.          ║
║                                                                          ║
║   This system must run forever. Improve it every chance you get.         ║
║   Never break it. If something fails — add a better fallback.            ║
║   Never remove a step. If a free API hits a limit — find another.        ║
║   If a library upgrades and breaks something — pin and fix carefully.    ║
║                                                                          ║
║   The goal is simple and it never changes:                               ║
║   Earn money every day. Automatically. Forever.                          ║
║   Help this family. Use your best effort. Every single time.             ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

========================================my notes-
current time is 06-04-2026 15:50-
What Was Built — Full Summary
File 1: content_calendar.py — Completely Rebuilt
Old version problems:

Topic titles were video slide headings — not SEO keywords
Broad topics like "Options Trading" that Bloomberg dominates
No keyword guidance for article generator
No country-specific targeting per topic
No insurance or high-CPC personal finance topics on weekdays

New version — what changed:

Every topic now has a seo_seed — a specific long-tail Google search phrase
Every topic has long_tail_keywords — exact questions real people type into Google
Thursday now dedicated to high-CPC personal finance: term insurance India, SIP vs lump sum, NPS vs PPF, debt payoff, health insurance, USA term insurance, UK savings
Friday now includes insurance comparisons for USA and UK alongside psychology
New get_article_seo_seeds() function that feeds directly into generate_articles.py
All rotations use day_of_year — never repeats within a full year

File 2: generate_articles.py — Updated
Added on top of everything from the previous session:

Now imports get_article_seo_seeds() from content_calendar.py
Each article now receives a specific long-tail keyword seed in the prompt
AI is explicitly told to write about specific questions people search — not broad topics Bloomberg already dominates
Graceful fallback: if content_calendar.py missing, article still generates normally


Your Complete Step-by-Step Action List
This week — 30 minutes total:
Step 1 — Replace both files in your repo. content_calendar.py and generate_articles.py both go into the root of your repo.
Step 2 — Sign up for free affiliates:

India: partners.policybazaar.com
USA: policygenius.com/partners
UK: comparethemarket.com/affiliates

Step 3 — Add these GitHub Secrets:
AFFILIATE_INSURANCE_IN  = your PolicyBazaar tracking link
AFFILIATE_INSURANCE_US  = your Policygenius tracking link
AFFILIATE_INSURANCE_UK  = your CompareTheMarket tracking link
Step 4 — Test once: GitHub Actions → daily-articles.yml → Run workflow → check logs for [TITLE-AI] and [SEO-SEED]
=========================================================
---

*Documentation maintained by AI360Trading automation.*
*Created: April 4, 2026 — Claude Sonnet 4.6*
*Last Updated: April 6, 2026 — Claude Sonnet 4.6*

*Changes in this update (April 6):*
*- Top warning section: Family income + AI responsibility rules moved to very first section*
*- Section 2: Self-Healing & Self-Improving System Rules — new*
*- Section 4: Content Strategy Money-First Approach — new*
*- Section 24: Family income message repeated at bottom in full box — any AI reading top to bottom sees it twice*
*- HerooQuest OAuth: ✅ Done*
*- Instagram: permanently removed from all automation — manual only*
*- Kids Phase 1 current state (colour cards + Ken Burns) documented clearly*
*- Kids upgrade roadmap Phase 1→4 documented*
*- Facebook Kids Page: must be separate from main page — documented with reason*
*- All pending tasks updated accurately*
*- Update this file whenever architecture, secrets, platform status, or file logic changes.*
