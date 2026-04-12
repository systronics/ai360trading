# AI360Trading — Master System Documentation

**Last Updated:** April 12, 2026 — Trading Bot v13.4 + AppScript v13.3
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete (active bugs) | Phase 3 Planned | Phase 4 (Dhan Live) Planned
**Primary Audience:** Bilingual Hindi + English — Indian retail traders + global investors

> ⚠️ **Read this file completely before making ANY changes.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT).

---

## 1. Real Mission

> This system is built to run **forever, fully automated**, generating passive income for the owner's family — even without active involvement. Built on ₹0/month infrastructure. No employees. No office. Pure automation.

### Monetisation — Every Stream Simultaneously

| Stream | Platform | High-CPM Target Countries |
| --- | --- | --- |
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
> All hooks and CTAs rotate from human\_touch.py — never hardcode them in generators.

---

## 2. Platform Status

| Platform | Status | Notes |
| --- | --- | --- |
| YouTube Hindi | ⚠️ Bugs | Double upload + OAuth scope missing — fix Section 20 Items 1, 2, 3 |
| YouTube English | 🔄 Building | Phase 3 — English scripts from scratch (not translated) |
| YouTube Shorts | ⚠️ Bugs | SEO titles/desc/hashtags generic — fix Section 20 Item 4 |
| YouTube Community Posts | ✅ Built | generate\_community\_post.py — 12:00 PM daily |
| YouTube Reels | ⚠️ Bugs | SEO titles/desc/hashtags generic — fix Section 20 Item 4 |
| YouTube Morning Reel | ✅ Auto | 7:00 AM reel working |
| YouTube Playlists | ⏭️ Skipped | Add after channel grows — secrets not set yet |
| Facebook Page | ⚠️ Broken | RSS 404 — articles not posting — fix Section 20 Item 5 |
| Facebook Group | 🤚 Manual | Owner posts manually. Auto-posting deferred to future phase. |
| Instagram | 🤚 Manual | Owner posts manually. Auto-posting deferred to future phase. |
| GitHub Pages | ⚠️ Partial | Articles generating but Search Console not indexing all pages — Section 20 Item 6 |
| Telegram | ✅ Auto | Signal alerts to all 3 channels (paper trading) |

> **Manual posting note:** Facebook Group and Instagram are intentionally manual.
> `upload_facebook.py` posts to FB Page only. `upload_instagram.py` not called in any workflow.

---

## 3. Content Mode System

Mode is **auto-detected** by `indian_holidays.py` at the start of every workflow and written to `$GITHUB_ENV`. All scripts read `CONTENT_MODE` environment variable — never hardcoded.

| Mode | When | Content Strategy |
| --- | --- | --- |
| `market` | Mon–Fri (excluding Indian holidays) | Live Nifty50/Global data, trade setups, signals |
| `weekend` | Saturday–Sunday | Educational, wealth-building, global audience focus |
| `holiday` | Indian Market Holidays | Motivational, "Market band hai par seekhna chalu", holiday name shown |

**Detection logic:** `indian_holidays.py` → NSE API (primary) → hardcoded fallback dates

---

## 4. Daily Content Output (Fully Automated)

| # | Content | Time (IST) | Platform | Target Duration | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + FB Page | 45–60s | ✅ |
| 2 | Part 1 Analysis (16:9) | 7:30 AM weekday / 9:30 AM weekend | YouTube | **8–12 min** (mid-roll ads) | ⚠️ Fix needed — currently 2.8 min |
| 3 | Part 2 Education (16:9) | 7:30 AM (same workflow) | YouTube | **8–15 min** (mid-roll ads) | ✅ 11.3 min |
| 4 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | 15–59s | ⚠️ SEO fix needed |
| 5 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | 15–59s | ⚠️ SEO fix needed |
| 6 | Short 4 English (9:16) | 11:30 AM (same workflow) | YouTube English Shorts | 15–59s | 🔄 Phase 3 |
| 7 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + FB Page | 800–1200 words each | ⚠️ RSS fix needed |
| 8 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB Page | 45–60s | ⚠️ SEO fix needed |
| 9 | YouTube Community Post | 12:00 PM | YouTube Community Tab | 100–200 chars | ✅ |
| **Total** | **12 pieces/day** | — | — | — | — |

> **Mid-roll ads rule:** YouTube enables mid-roll ads only on videos **8 minutes or longer**. Both Part 1 and Part 2 must always be ≥8 min. Part 1 is currently only 2.8 min — must be fixed.

> **USA/UK prime time:** Videos uploaded at IST times but SEO-optimised for 11 PM–1 AM IST peak.

---

## 5. GitHub Actions Workflows

| File | Trigger (IST) | Purpose | Mode-Aware |
| --- | --- | --- | --- |
| `main.yml` | Every 5 min (market hours, Mon–Fri) | `trading_bot.py` — Nifty200 signals | ✅ Auto-skips weekends/holidays |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 (analysis) + Part 2 (education) | ✅ |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 + Community Post | ✅ |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning Reel + ZENO Reel | ✅ |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages | ✅ |
| `token_refresh.yml` | Every 50 days (1st + 20th of month) | Auto META token refresh | N/A |
| `keepalive.yml` | Periodic | Prevents GitHub disabling inactive workflows | N/A |

> ⚠️ **Failure alerting (Section 20 Item 7):** All workflows must send Telegram alert on failure. Not yet implemented.

All workflows support `workflow_dispatch` with a `content_mode` dropdown to force any mode for testing.

---

## 6. Complete File Map

### Core Infrastructure (Phase 1 — Complete)

| File | Role | Status |
| --- | --- | --- |
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates fallback | ✅ |
| `human_touch.py` | Anti-AI-penalty layer — 50+ hooks, personal phrases, TTS variation, SEO tags | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update + Telegram alert | ✅ |

### Core Content Generation (Phase 2)

| File | Role | Key Tech | Status |
| --- | --- | --- | --- |
| `trading_bot.py` | Nifty200 signal monitor + TSL manager + Telegram alerts | gspread + Google Sheets + Telegram Bot API | ✅ v13.4 |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Swara) | ai\_client, human\_touch, Edge-TTS | ⚠️ SEO fix needed |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ai\_client, human\_touch, MoviePy | ⚠️ SEO fix needed |
| `generate_reel_morning.py` | Morning reel (7:00 AM) | ai\_client, human\_touch, MoviePy | ✅ |
| `generate_analysis.py` | Market analysis video (Part 1) | ai\_client, human\_touch, MoviePy | ⚠️ Remove internal upload + fix duration |
| `generate_education.py` | Educational deep-dive video (Part 2) | ai\_client, human\_touch, content\_calendar | ✅ 11.3 min |
| `generate_articles.py` | 4 SEO articles daily → Jekyll \_posts | ai\_client, human\_touch, Google Indexing | ⚠️ RSS + indexing fix needed |
| `generate_community_post.py` | YouTube daily community text post — 12:00 PM | ai\_client, human\_touch | ⚠️ Verify file exists in repo root |

### Upload & Distribution

| File | Role | Status |
| --- | --- | --- |
| `upload_youtube.py` | **Single upload point** — reads meta JSON, uploads with proper SEO title/desc/tags | ⚠️ Fix generic title fallback |
| `upload_youtube_english.py` | Uploads to English channel | 🔄 Phase 3 |
| `upload_facebook.py` | Uploads reel to FB Page + posts articles via RSS | ⚠️ RSS 404 fix needed |
| `upload_instagram.py` | Built but NOT called in any workflow. Manual posting only. | 🤚 Manual |

### Infrastructure

| File | Role |
| --- | --- |
| `indian_holidays.py` | Mode detection — NSE API + fallback; shared by ALL workflows |
| `content_calendar.py` | Rotates topics: Options, Technical Analysis, Psychology |

### Static Assets

| Path | Contents |
| --- | --- |
| `public/image/` | `zeno_happy.png`, `zeno_sad.png`, `zeno_greed.png`, `zeno_thinking.png` |
| `public/music/` | `bgmusic1.mp3`, `bgmusic2.mp3`, `bgmusic3.mp3` — rotated by weekday |

> **ZENO image improvement (Section 20 Item 8):** ZENO PNG sizing not optimised for 9:16 frame. Good framing = higher click-through rate in Shorts feed.

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

**Usage pattern:**

```python
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang="hi")
data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
clean = ht.humanize(raw_output, lang="hi")
hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")
tags = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")
```

---

## 8. Trading Bot Architecture

### Overview

| Component | File | Role |
| --- | --- | --- |
| AppScript v13.3 | Google Sheets bound script | Scans Nifty200, applies filters, writes WAITING candidates to AlertLog, stores memory in T4 |
| Python Bot v13.4 | `trading_bot.py` | Monitors AlertLog every 5 min, manages WAITING→TRADED, TSL updates, exit logic, Telegram alerts |

**Current status:** Paper trading. Followers receive Telegram signals and take manual entry.

### Google Sheets Structure

| Sheet | Purpose |
| --- | --- |
| `Nifty200` | Live data for 200 stocks — CMP, DMAs, FII data, signals, scores (34 cols) |
| `AlertLog` | Active + waiting trades — 15 rows, 19 cols. T2=YES/NO switch. T4=memory |
| `History` | Closed trade log — 18 cols A–R |

### AlertLog Column Map (0-based)

```
A=0  Signal Time    B=1  Symbol        C=2  Live Price     D=3  Priority Score
E=4  Trade Type     F=5  Strategy      G=6  Breakout Stage H=7  Initial SL
I=8  Target         J=9  RR Ratio      K=10 Trade Status   L=11 Entry Price
M=12 Entry Time     N=13 Days in Trade O=14 Trailing SL    P=15 P/L%
Q=16 ATH Warning    R=17 Risk ₹        S=18 Position Size  T=19 SYSTEM CONTROL
```

**T2** = automation on/off (YES to enable)
**T4** = memory string

> ⚠️ **T4 fragility:** Currently raw `key=value,key=value` CSV. Migration to JSON planned — Section 20 Item 9.

**T4 memory keys per stock:** `{sym}_TSL`, `{sym}_MAX`, `{sym}_ATR`, `{sym}_CAP`, `{sym}_MODE`, `{sym}_SEC`

### Nifty200 Column Map (0-based)

```
r[0]  NSE_SYMBOL     r[1]  SECTOR         r[2]  CMP            r[3]  %Change (D)
r[4]  20_DMA         r[5]  50_DMA         r[6]  200_DMA        r[7]  SMA_Structure
r[8]  52W_Low        r[9]  52W_High       r[10] %up_52W_Low    r[11] %down_52W_High
r[12] %dist_20DMA    r[13] Avg_Volume_20D r[14] Volume_vs_Avg% r[15] FII_Buy_Zone
r[16] FII_Rating     r[17] Leader_Type    r[18] Signal_Score   r[19] FINAL_ACTION
r[20] RS             r[21] Sector_Trend   r[22] Breakout_Stage r[23] Retest%
r[24] Trade_Type     r[25] Priority_Score r[26] Pivot_Resistance r[27] VCP_Status
r[28] ATR14          r[29] Days_Since_Low r[30] 52W_Breakout_Score r[31] Sector_Rotation_Score
r[32] FII_Buying_Signal r[33] Master_Score
```

### AppScript v13.3 — Key Logic

**Market Regime:** Nifty50 CMP vs 20DMA → Bullish or Bearish.

**Bearish gate (all 4 required):**
* Leader\_Type = "Sector Leader"
* AF ≥ 5 (RS≥2.5 with sector tailwind)
* Master\_Score ≥ 22
* FII signal ≠ "FII CAUTION" or "FII SELLING"

**10 scan gates:** FII SELLING skip → regime filter → late entry block → price validity → extension filter → pivot buffer → volume filter → ATH buffer → trade type → sector concentration

**Capital tiers:** ₹13,000 (MasterScore≥28 + AF≥10) | ₹10,000 (MasterScore≥22 or Accumulation) | ₹7,000 (standard)

**Trade modes:** VCP (AB<0.04 + pre-breakout) | MOM (Strong Bull + RS≥6) | STD (default)

**Sort order:** finalScore DESC, ATR% ASC tiebreaker within ±2 score points.

### Python Bot v13.4 — Key Logic

> ⚠️ **Circuit breaker to be added — Section 20 Item 10.**

**TSL Parameters:**

```python
TSL_PARAMS = {
    "VCP": { "breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0 },
    "MOM": { "breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0 },
    "STD": { "breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0 },
}
```

**TSL progression (STD):** <2% hold | 2–4% breakeven | 4–10% lock entry+2% | >10% ATR trail | >8% gap-up lock 50%

**Daily messages:** 08:45 Good Morning | 09:15–15:30 live alerts | 12:28 Mid-day pulse | 15:15 Close summary

**CE candidate flag (v13.4):** ATR%<1.5% no flag | 1.5–2.5% normal mover +65%/-40% | >2.5% fast mover +50%/-35%

**Hard exits:** Loss >5% immediate | Min hold 2d swing / 3d positional | 5-day cooldown after exit

### History Sheet Columns (A–R)

```
A Symbol  B Entry Date  C Entry Price  D Exit Date  E Exit Price  F P/L%
G Result  H Strategy    I Exit Reason  J Trade Type K Initial SL  L TSL at Exit
M Max Price N ATR Entry O Days Held   P Capital ₹  Q Profit/Loss ₹  R Options Note
```

---

## 9. Critical Upload Chain

> ⚠️ **GOLDEN RULE — Generators generate. Uploaders upload. Never mix.**
> `generate_*.py` → renders mp4 + writes meta JSON → exits. NO YouTube API calls inside generators.
> `upload_youtube.py` → reads meta JSON → uploads once → writes video ID back to meta.
> Mixing these causes double uploads with wrong titles — **confirmed bug April 11, 2026**.

### Evening ZENO Reel (8:30 PM)

```
generate_reel.py
    └── output/reel_YYYYMMDD.mp4
    └── output/meta_YYYYMMDD.json  ← AI SEO title, description, tags written here

upload_youtube.py --type reel
    └── Reads meta JSON → uses AI-generated SEO title (NOT a generic fallback)
    └── Uploads to YouTube ONCE
    └── Writes youtube_video_id back to meta

upload_facebook.py
    └── Uploads reel to Facebook Page only
    └── Posts articles via RSS feed (after RSS fix — Section 20 Item 5)
    └── Group posting: MANUAL
```

### Morning Reel (7:00 AM)

```
generate_reel_morning.py → output mp4 + meta JSON
upload_youtube.py --type morning_reel → YouTube
upload_facebook.py → FB Page only
```

### Daily Videos (7:30 AM)

```
generate_analysis.py
    └── output/analysis_video.mp4
    └── output/analysis_meta_YYYYMMDD.json  ← AI SEO title saved here
    └── ❌ MUST NOT contain internal YouTube upload call

upload_youtube.py --type analysis
    └── Reads analysis_meta → uses AI SEO title → uploads ONCE
    └── Writes ID to analysis_video_id.txt

generate_education.py
    └── Reads analysis_video_id.txt → adds Part 1 link in description
    └── output/education_video.mp4
    └── output/education_meta_YYYYMMDD.json
    └── ❌ MUST NOT contain internal YouTube upload call

upload_youtube.py --type education
    └── Reads education_meta → uses AI SEO title → uploads ONCE
    └── Updates Part 1 description with Part 2 URL
       (requires youtube.force-ssl OAuth scope — Section 20 Item 2)
```

### Daily Shorts (11:30 AM)

```
generate_shorts.py → short2 + short3 mp4 + meta JSON (NO upload)
upload_youtube.py --type short → uploads short2 with correct SEO title
upload_youtube.py --type short3 → uploads short3 with correct SEO title
```

---

## 10. Environment Variables & Secrets

All in **GitHub Actions Secrets**. Never hardcode.

### YouTube

| Secret | Purpose | Status |
| --- | --- | --- |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON — Hindi channel | ✅ Needs re-auth for force-ssl scope |
| `YOUTUBE_CREDENTIALS_EN` | YouTube OAuth JSON — English channel | ✅ Added |
| `YOUTUBE_PLAYLIST_ANALYSIS` | Playlist: Nifty50 Daily Analysis | ⏭️ Add after channel grows |
| `YOUTUBE_PLAYLIST_SWING` | Playlist: Swing Trade Setups | ⏭️ Add after channel grows |

### Dhan (Phase 4)

| Secret | Status |
| --- | --- |
| `DHAN_API_KEY`, `DHAN_API_SECRET`, `DHAN_CLIENT_ID`, `DHAN_PIN`, `DHAN_TOTP_KEY` | ✅ Added — not connected yet |

### Social Platforms

| Secret | Purpose | Status |
| --- | --- | --- |
| `META_ACCESS_TOKEN` | Facebook Page API | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` / `META_APP_SECRET` | For token refresh | ✅ |
| `FACEBOOK_PAGE_ID` | Target page | ✅ |
| `FACEBOOK_GROUP_ID` | Kept for future | ✅ (not used) |
| `INSTAGRAM_ACCOUNT_ID` | Kept for future | ✅ (not used) |

### AI Providers

| Secret | Priority | Status |
| --- | --- | --- |
| `GROQ_API_KEY` | Primary | ✅ |
| `GEMINI_API_KEY` | Secondary | ✅ |
| `ANTHROPIC_API_KEY` | Tertiary | ✅ |
| `OPENAI_API_KEY` | Quaternary | ✅ |

### Telegram / GCP

| Secret | Purpose |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Bot auth |
| `TELEGRAM_CHAT_ID` | Free channel |
| `CHAT_ID_ADVANCE` | Advance channel (₹499/mo) |
| `CHAT_ID_PREMIUM` | Premium channel |
| `GCP_SERVICE_ACCOUNT_JSON` | Search Console Indexing + Google Sheets |
| `GH_TOKEN` | GitHub API |

---

## 11. Human Touch System (Anti-AI-Penalty)

All content uses `human_touch.py`. **Never use raw AI output directly.**

| Technique | Method | What It Does |
| --- | --- | --- |
| 50+ rotating hooks | `ht.get_hook(mode, lang)` | No two videos start the same |
| Personal phrases | `ht.get_personal_phrase(lang)` | "Maine dekha hai..." injected naturally |
| TTS speed variation | `ht.get_tts_speed()` | 0.95–1.05x — passed to edge\_tts rate param |
| Humanize output | `ht.humanize(text, lang)` | Strips robotic patterns, varies connectors |
| Emoji rotation | `ht.get_emoji_set()` | Day-seeded set |
| SEO tags | `seo.get_video_tags(mode, lang)` | India + Global combined |
| Banned phrase removal | Internal | "Certainly!", "It's important to note" stripped |

> **Hindi TTS pronunciation (Section 20 Item 11):** Some words mispronounced by edge-tts. Fix via phonetic substitution map in `human_touch.py`.

---

## 12. Known Issues & Current Status

### ❌ Double Upload Bug (Critical — April 11, 2026)
`generate_analysis.py` and `generate_education.py` both upload internally AND the workflow runs `upload_youtube.py`. Each video uploads twice — once with correct AI title, once with generic title. Fix: Section 20 Item 1.

### ⚠️ YouTube OAuth Missing youtube.force-ssl Scope
Blocks: end screen addition, Part 1 description update with Part 2 link. Error: `HttpError 403 insufficientPermissions`. Fix: Section 20 Item 2. Owner to re-authorise when ready.

### ❌ RSS Feed 404
`https://ai360trading.in/feed/` returns 404. Articles not posting to Facebook Page. Fix: Section 20 Item 5.

### ⚠️ Analysis Video Too Short (2.8 min — needs 8+ min)
14 slides × ~12s = 2.8 min. Zero mid-roll ad revenue. Must reach 22+ slides × ~32s = 11+ min. Fix: Section 20 Item 3.

### ⚠️ Reel/Shorts SEO Generic Titles
`upload_youtube.py` uses hardcoded generic titles instead of AI-generated SEO titles from meta JSON. Fix: Section 20 Item 4.

### ⚠️ Google Search Console Not Indexing All Pages
Owner to share Search Console screenshots when ready. Tracked: Section 20 Item 6.

### 🤚 Facebook Group + Instagram — Manual (by choice)
Intentionally deferred. Owner posts manually. No action needed now.

### ✅ META Token Auto-Refresh
`token_refresh.yml` runs every 50 days — working.

### ⚠️ YouTube Community Tab
Requires 500+ subscribers. If below threshold, post text saved to `output/community_post_YYYYMMDD.txt`.

---

## 13. Technical Standards

### Generator vs Uploader Rule — No Exceptions

> **Generators generate. Uploaders upload.**
> Confirmed bug from mixing: April 11, 2026 double upload with wrong titles.

```
generate_*.py  → renders mp4 + writes meta JSON → exits (NO YouTube API)
upload_youtube.py → reads meta JSON → uploads once → writes ID to meta
```

### The "Full Code" Rule

AI assistants must always provide **complete file content**. No partial snippets.

```
Context: I am working on the ai360trading system. Refer to SYSTEM.md for architecture.
Task: [Your Task]
Note: Provide the full code for any file you modify.
```

### AI Client + Human Touch — No Exceptions

```python
from ai_client import ai, img_client
from human_touch import ht, seo
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang=LANG)
clean = ht.humanize(raw_output, lang=LANG)
```

### SEO Standard — All YouTube Uploads

Every upload must use these fields from meta JSON:

| Field | Source | Rule |
| --- | --- | --- |
| Title | `meta["title"]` — AI-generated | Keyword-rich, market-specific. No emojis. No hashtags. |
| Description | `meta["description"]` — AI-generated | 200–300 words. Global keywords. Links to site + Telegram. Hashtags in last 3 lines only. |
| Tags | `seo.get_video_tags(mode, lang)` | India + Global always combined |

**Title format (correct):**
- ✅ `Nifty50 Analysis 12 Apr 2026 | Market Trend Update | AI360 Trading`
- ✅ `Tax Planning India 2026 | 80C to 80U Guide | Save Tax Legally Hindi`
- ❌ `🎯 Market Analysis — AI360Trading #0411 #Shorts` — generic, never use

**Hashtag rule:** All hashtags in **description only** (last 3 lines). Never in the title.

### Dependency Pins

| Package | Version |
| --- | --- |
| `Pillow` | `>=10.3.0` |
| `imageio` | `==2.9.0` |
| `moviepy` | `==1.0.3` |
| `yfinance` | Latest — use `fast_info['last_price']` only |

> ⚠️ All other "Latest" packages should be pinned — Section 20 Item 12.

### Voice Assignments

| Voice | Gender | Used For |
| --- | --- | --- |
| `hi-IN-MadhurNeural` | Male | Short 2 |
| `hi-IN-SwaraNeural` | Female | Short 3, ZENO Reel, Morning Reel, Analysis, Education |
| `en-US-JennyNeural` | Female | English channel |
| `en-US-GuyNeural` | Male | English Short 2 |

### Video Format Rules

| Content | Ratio | Min Duration |
| --- | --- | --- |
| Analysis + Education | 16:9 | **8 min** (mid-roll ads) |
| Shorts / Reels | 9:16 | 15–59s |

---

## 14. Disney 3D Reel Roadmap

| Phase | Tool | Status |
| --- | --- | --- |
| 1 (Now) | PIL + MoviePy + ZENO PNG — 2D slides | ✅ Active |
| 2 | Gemini Veo API free tier — AI video clips | Hooks ready in ai\_client.py |
| 3 | Stable Diffusion + AnimateDiff — 3D frames | Planned 6–12 months |
| 4 | Google Veo 2 / Sora — true Disney 3D | Planned 12–18 months |

> `img_client` in `ai_client.py` is the upgrade hook. Phase 2 swap = zero changes to generators.
> Fix ZENO image sizing first (Section 20 Item 8) — good framing is the foundation for all phases.

---

## 15. Full Data Flow

```
Market hours (Mon–Fri, 9:15–15:30 IST)
└── main.yml (every 5 min)
    └── trading_bot.py v13.4 → AlertLog → Telegram signals

AppScript v13.3 (on schedule or manual)
└── Nifty200 scan → 10-gate filter → write WAITING to AlertLog

7:00 AM → generate_reel_morning.py → upload_youtube.py → upload_facebook.py (Page)
7:30 AM → generate_analysis.py (no upload) → upload_youtube.py --type analysis
        → generate_education.py (no upload) → upload_youtube.py --type education
10:00 AM → generate_articles.py → GitHub Pages → upload_facebook.py (RSS → Page)
11:30 AM → generate_shorts.py (no upload) → upload_youtube.py --type short (×2)
         → generate_community_post.py → YouTube Community Tab
8:30 PM  → generate_reel.py (no upload) → upload_youtube.py --type reel
         → upload_facebook.py (Page)
```

---

## 16. Website & SEO

* **URL:** `ai360trading.in` — Jekyll on GitHub Pages, `master` branch `_posts/`
* **RSS:** `https://ai360trading.in/feed.xml` (after fix — currently 404 at `/feed/`)
* **Indexing:** Google Search Console via `GCP_SERVICE_ACCOUNT_JSON` — not all pages indexed (Section 20 Item 6)
* **Revenue:** Google AdSense — USA/UK readers highest CPM
* **Content pillars:** Stock Market, Bitcoin/Crypto, Personal Finance, AI Trading

---

## 17. Social Media Links

| Platform | Handle | Auto? |
| --- | --- | --- |
| 🌐 Website | ai360trading.in | ✅ Auto |
| 📣 Telegram Free | @ai360trading | ✅ Auto |
| 📣 Telegram Advance | ai360trading\_Advance ₹499/mo | ✅ Auto |
| 📣 Telegram Premium | ai360trading\_Premium | ✅ Auto |
| ▶️ YouTube | @ai360trading | ✅ Auto |
| 📘 Facebook Page | facebook.com/ai360trading | ✅ Auto |
| 📸 Instagram | @ai360trading | 🤚 Manual |
| 👥 Facebook Group | facebook.com/groups/ai360trading | 🤚 Manual |
| 🐦 Twitter/X | @ai360trading | 🤚 Manual |

---

## 18. Phase Roadmap

### Phase 1 ✅ Complete
`ai_client.py`, `human_touch.py`, `token_refresh.py`, `generate_reel_morning.py`

### Phase 2 ✅ Built — Active Bugs to Fix
All generators and uploaders built. Fix all Section 20 items before Phase 3.

**Fix order for Phase 2 bugs:**
1. Item 1 — Double upload (today)
2. Item 2 — YouTube OAuth re-auth (today)
3. Item 3 — Analysis video duration (today)
4. Item 4 — SEO titles/desc/hashtags (today)
5. Item 5 — RSS feed 404 (today)
6. Items 6–12 — remaining improvements (this week)

### Phase 3 🔄 — Start after Phase 2 bugs fixed

| Item | Priority |
| --- | --- |
| English channel — scripts from scratch | 🟡 Medium |
| Instagram auto-post re-enable | 🔵 Deferred |
| Facebook Group auto-post re-enable | 🔵 Deferred |
| ZENO 3D via Veo API | 🔵 Future |

### Phase 4 📋 — Dhan Live Trading (after 30+ validated paper trades)

---

## 19. How to Test Everything

**No double upload:** After `daily-videos.yml` runs — check YouTube Studio. Exactly 2 new videos. If 4, bug still present.

**Correct SEO title:** YouTube Studio → video title must be AI-generated keyword title, not `🎯 Market Analysis — AI360Trading #0411`.

**Analysis duration:** Video must be 8+ min. Check duration in YouTube Studio immediately after upload.

**Trading bot:**
```
[REGIME] Nifty CMP ₹22679 vs 20DMA ₹23547 → BEARISH
[TSL] NSE:ONGC [STD]: ₹280.60→₹285.20
[DONE] 15:20:01 IST | mem=842 chars
```

**Force content mode:** `workflow_dispatch → content_mode = market / weekend / holiday`

**Automation switch:** Google Sheet → AlertLog → T2 → "YES" to enable.

---

## 20. Improvement Backlog

Fix in this order. Each item has a complete spec ready for any AI assistant.

---

### Item 1 — Fix Double Upload Bug
**Priority:** 🔴 Fix today
**Files:** `generate_analysis.py`, `generate_education.py`

**Root cause (April 11, 2026 logs):**
- `generate_analysis.py` called YouTube API internally → uploaded with correct title (ID: J6KKiiBQ4UU)
- `upload_youtube.py --type analysis` ran again → uploaded same file with generic title (ID: gwPoh59SRG8)
- Same for education video. Result: 4 videos instead of 2.

**Fix:** In both generators, find and completely remove any code block that:
- imports `googleapiclient` or calls `youtube.videos().insert()`
- prints `✅ YouTube upload success!`

After removal, each generator must only:
1. Render and save the mp4 to `output/`
2. Save meta JSON with `title`, `description`, `tags`, `thumbnail` fields
3. Save a blank/placeholder `*_video_id.txt` (actual ID written by `upload_youtube.py`)
4. Print `✅ Video rendered: output/xxx.mp4` and exit

**Verify `daily-videos.yml` step order after fix:**
```yaml
- run: python generate_analysis.py        # generates only — no upload
- run: python upload_youtube.py --type analysis    # uploads once, correct title
- run: python generate_education.py       # generates only — no upload
- run: python upload_youtube.py --type education   # uploads once, correct title
```

---

### Item 2 — Re-authorise YouTube OAuth (youtube.force-ssl scope)
**Priority:** 🔴 Fix today
**File:** `YOUTUBE_CREDENTIALS` GitHub Secret

**Why needed:** Without this scope, the bot cannot update Part 1 description with Part 2 URL after education uploads. Error: `HttpError 403 — insufficientPermissions`.

**Steps (run once on local machine):**

```python
# save as reauth_youtube.py and run locally
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube",
]

flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
creds = flow.run_local_server(port=0)

output = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": list(creds.scopes)
}
print(json.dumps(output, indent=2))
```

1. Get `client_secrets.json` from: Google Cloud Console → APIs & Services → Credentials → your OAuth 2.0 client → Download JSON
2. Run `python reauth_youtube.py` — browser opens, approve access
3. Copy the JSON printed to terminal
4. GitHub → repo Settings → Secrets → `YOUTUBE_CREDENTIALS` → Update → paste new JSON
5. Done — all workflows use the new token automatically

---

### Item 3 — Fix Analysis Video Duration (2.8 min → 8+ min)
**Priority:** 🔴 Fix today
**File:** `generate_analysis.py`

**Current:** 14 slides × ~12s = 2.8 min → **zero mid-roll ad revenue**
**Target:** 22 slides × ~32s = 11+ min → **mid-roll ads active**

**Code changes in `generate_analysis.py`:**

```python
# Change these constants:
MIN_SLIDES = 22          # was 14
MIN_DURATION = 480       # 8 minutes in seconds — add this check
TARGET_SECONDS_PER_SLIDE = 32   # was ~12
```

**Update the AI script prompt to request 22 slides with these sections:**

```
Market day (22 slides minimum, ~32 seconds of spoken content each):
Slide 1:  Hook — today's big picture + what viewer will learn (1 slide)
Slides 2–3:  Global overnight — USA S&P500/NASDAQ + Europe/UK FTSE (2 slides)
Slides 4–5:  Nifty50 levels — trend, key support, key resistance (2 slides)
Slide 6:  BankNifty levels + key zones (1 slide)
Slides 7–8:  FII/DII flow — what big money is doing (2 slides)
Slides 9–10: Top gainers today with reason (2 slides)
Slides 11–12: Top losers today with reason (2 slides)
Slides 13–14: Sector rotation — which sectors are strong/weak (2 slides)
Slides 15–16: Key stocks to watch — entry zones, technicals (2 slides)
Slide 17: Options data — PCR, max pain level (1 slide)
Slide 18: Bitcoin/Crypto update (1 slide)
Slides 19–20: Trading strategy for today's market (2 slides)
Slide 21: Risk management — position sizing, stop loss reminder (1 slide)
Slide 22: Summary + CTA — subscribe, Telegram link (1 slide)

Weekend mode (22 slides): Use content_calendar.py topic.
Each concept needs example + real-world application for full 32s per slide.
```

**Add duration check after rendering:**
```python
from moviepy.editor import VideoFileClip
clip = VideoFileClip("output/analysis_video.mp4")
duration_min = clip.duration / 60
if clip.duration < 480:  # 8 minutes
    print(f"⚠️ WARNING: Video {duration_min:.1f} min — under 8 min, mid-roll ads will NOT activate")
else:
    print(f"✅ Duration OK — {duration_min:.1f} min — mid-roll ads WILL activate")
clip.close()
```

---

### Item 4 — Fix SEO Titles, Descriptions, Hashtags
**Priority:** 🔴 Fix today
**Files:** `upload_youtube.py`, `generate_reel.py`, `generate_shorts.py`, `generate_reel_morning.py`

**Problem:** `upload_youtube.py` has hardcoded generic title fallbacks. It must ALWAYS read from the meta JSON.

**Fix in `upload_youtube.py`:**
```python
# Remove ALL hardcoded title fallbacks like:
# title = f"📚 Weekend Wisdom — ZENO Reel #{date} #Shorts"
# title = f"🎯 Market Analysis — AI360Trading #{date} #Shorts"

# Replace with:
meta = {}
if os.path.exists(meta_file):
    with open(meta_file) as f:
        meta = json.load(f)

title = meta.get("title")
if not title:
    raise ValueError(f"No title in meta file {meta_file} — cannot upload without SEO title")

description = meta.get("description", "")
tags = meta.get("tags", seo.get_video_tags(CONTENT_MODE, LANG))
```

**Fix in all generators — the meta JSON they write must include these fields:**

```python
# In generate_reel.py, generate_shorts.py, generate_reel_morning.py
# The AI prompt for title must include:
title_prompt = """
Generate a YouTube title for this Hindi finance video about {topic}.
Rules:
- 60–70 characters max
- Start with main keyword (Nifty50, BankNifty, Stock Market India, etc.)
- Include year (2026) or date context
- End with | AI360 Trading
- NO emojis in title
- NO hashtags in title (hashtags go in description ONLY)
Good examples:
  "Nifty50 Aaj Ka Analysis | Market Outlook Today | AI360 Trading"
  "BankNifty Weekly Levels | Key Support Resistance | AI360 Trading"
  "Stock Market Kya Bolega | Weekend Strategy Hindi 2026 | AI360 Trading"
"""

description_prompt = """
Generate YouTube description for this Hindi finance video. Rules:
- Line 1–2: Hook with main keywords (shown before 'show more' in search)
- Next 3 lines: What viewer learns
- Links section:
  📊 Free Signals: https://t.me/ai360trading
  📈 Website: https://ai360trading.in
  📱 Advance Signals: https://t.me/ai360trading_Advance
- Last 3 lines — hashtags ONLY:
  #Nifty50 #StockMarket #AITrading #TradingHindi #BankNifty #NSE
  #SwingTrading #StockMarketIndia #Investing #Shorts
  #ai360trading #FinancialEducation #ShareMarket #SEBI #BSE
- Total: 150–250 words
"""
```

---

### Item 5 — Fix RSS Feed 404
**Priority:** 🔴 Fix today (articles not posting to Facebook)
**Files:** `Gemfile`, `_config.yml`, `upload_facebook.py`

**Step 1 — Add Jekyll Feed plugin to `Gemfile`:**
```ruby
gem "jekyll-feed"
```

**Step 2 — Update `_config.yml`:**
```yaml
plugins:
  - jekyll-feed
  - jekyll-sitemap

feed:
  path: feed.xml
```

**Step 3 — Update `upload_facebook.py`:**
```python
# Change:
RSS_URL = "https://ai360trading.in/feed/"
# To:
RSS_URL = "https://ai360trading.in/feed.xml"
```

**Step 4 — Add to `_layouts/default.html` inside `<head>`:**
```html
<link rel="alternate" type="application/atom+xml" title="AI360Trading Feed" href="/feed.xml">
```

**Step 5 — Check if existing `atom.xml` conflicts with plugin output. If it does, remove `atom.xml` from repo root.**

**Verify:** After push, visit `https://ai360trading.in/feed.xml` — should show XML with recent articles.

---

### Item 6 — Google Search Console Indexing Fix
**Priority:** 🟡 Medium
**Status:** ⬜ Owner to share Search Console screenshots/errors when ready

**Quick wins to apply now without seeing the error:**

1. In `_config.yml` ensure:
```yaml
url: "https://ai360trading.in"
baseurl: ""
```

2. In `generate_articles.py`, verify Indexing API fires for each article:
```python
indexing_service.urlNotifications().publish(body={
    "url": f"https://ai360trading.in{article_url}/",
    "type": "URL_UPDATED"
}).execute()
print(f"✅ Indexed: https://ai360trading.in{article_url}/")
```

3. Ensure article frontmatter does NOT contain `noindex: true`.

**When owner shares Search Console error, check for:**
- "Crawled - currently not indexed" → content quality/depth issue
- "Discovered - currently not indexed" → sitemap/crawl budget issue — fix sitemap
- "Duplicate without canonical" → add canonical URL to frontmatter
- "Page with redirect" → check CNAME + GitHub Pages domain config

---

### Item 7 — Workflow Failure Alerts via Telegram
**Priority:** 🟡 Medium
**Files:** All `.github/workflows/*.yml`

Add as **last step** in every workflow job:

```yaml
- name: Alert on failure
  if: failure()
  env:
    TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
  run: |
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="${TELEGRAM_CHAT_ID}" \
      -d text="⚠️ WORKFLOW FAILED%0AWorkflow: ${{ github.workflow }}%0ADate: $(date '+%d %b %Y %H:%M')%0ALogs: https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}"
```

Add to: `daily-videos.yml`, `daily-shorts.yml`, `daily_reel.yml`, `daily-articles.yml`, `main.yml`, `token_refresh.yml`

---

### Item 8 — Fix ZENO Image Sizing for 9:16 Frame
**Priority:** 🟡 Medium (affects Shorts click-through rate)
**Files:** `generate_reel.py`, `generate_shorts.py`, `generate_reel_morning.py`

**Target layout (1080×1920):**
- Top 15%: title text (2–3 lines)
- Centre 55%: ZENO image fills 80% of frame width, centred horizontally
- Bottom 30%: body text / stat / number

**Fix:**
```python
frame_w, frame_h = 1080, 1920
zeno = Image.open(f"public/image/zeno_{emotion}.png").convert("RGBA")

# Resize ZENO to fill 80% of frame width
target_w = int(frame_w * 0.80)
ratio = target_w / zeno.width
target_h = int(zeno.height * ratio)
zeno = zeno.resize((target_w, target_h), Image.LANCZOS)

# Position: horizontally centred, starting at 22% from top
zeno_x = (frame_w - target_w) // 2
zeno_y = int(frame_h * 0.22)
frame.paste(zeno, (zeno_x, zeno_y), zeno)
```

**Future 3D animation (best free method):** Gemini Veo API free tier → 5–8s animated ZENO clips. Use `img_client.generate_video(prompt, duration=6)` when Veo API becomes available. Zero code change in generators — only `ai_client.py` changes.

---

### Item 9 — T4 Memory: Migrate CSV to JSON
**Priority:** 🟡 Medium
**Files:** `trading_bot.py`, AppScript

```python
# trading_bot.py — backward-compatible read
def read_t4(t4_string):
    t4_string = (t4_string or "").strip()
    if t4_string.startswith("{"):
        try:
            return json.loads(t4_string)
        except json.JSONDecodeError:
            return {}
    mem = {}
    for pair in t4_string.split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            mem[k.strip()] = v.strip()
    return mem

def write_t4(mem_dict):
    return json.dumps(mem_dict, separators=(',', ':'))
```

```javascript
// AppScript — replace setValue(memoryString) with:
sheet.getRange("T4").setValue(JSON.stringify(memoryObj));
```

Deploy Python first (CSV fallback keeps old data safe). Then update AppScript.

---

### Item 10 — Trading Bot Circuit Breaker
**Priority:** 🟡 Medium
**File:** `trading_bot.py`

```python
MAX_NEW_SIGNALS_PER_RUN = 3
new_signals_this_run = 0

# At start of main():
try:
    sheets = get_sheets()
except Exception as e:
    send_telegram(TELEGRAM_CHAT_ID, f"⚠️ Bot failed — Sheets unreachable: {e}")
    sys.exit(1)

# In WAITING→TRADED block:
new_signals_this_run += 1
if new_signals_this_run >= MAX_NEW_SIGNALS_PER_RUN:
    print(f"[GUARD] Max signals/run reached — stopping")
    break
```

---

### Item 11 — Fix Hindi TTS Pronunciation
**Priority:** 🟡 Medium
**File:** `human_touch.py`

Add phonetic substitution map. Apply BEFORE TTS call in all generators:

```python
HINDI_TTS_FIXES = {
    "RSI": "आर एस आई",
    "FII": "एफ आई आई",
    "DII": "डी आई आई",
    "SMA": "एस एम ए",
    "EMA": "ई एम ए",
    "PCR": "पी सी आर",
    "ATR": "ए टी आर",
    # Add more as you discover mispronounced words while listening
}

def fix_hindi_tts(text):
    for wrong, right in HINDI_TTS_FIXES.items():
        text = text.replace(wrong, right)
    return text
```

Usage in generators:
```python
script = ht.fix_hindi_tts(script)  # before TTS call
await edge_tts.Communicate(script, VOICE, rate=rate_str).save(path)
```

**Action:** As you listen to audio output, write down every mispronounced word and add to `HINDI_TTS_FIXES`.

---

### Item 12 — Pin All requirements.txt Packages
**Priority:** 🟢 Nice-to-have
**File:** `requirements.txt`

Run `pip freeze` in clean environment → pin every package. Add pin date comment at top. Review quarterly.

---

### Item 13 — Dhan Live Trading Integration Spec
**Priority:** 🔵 Phase 4 — do not start until 30+ paper trades validated
**Pre-conditions:** Win rate >35%, max drawdown <15%, 2 weeks crash-free

Key decisions before coding:
1. Order type: Market or Limit?
2. `LIVE_TRADING=true` env flag (default false = paper mode)
3. Margin check before every order
4. If order fails: Telegram alert + do NOT mark TRADED in sheet

---

### Item 14 — English Channel Content Strategy
**Priority:** 🟡 Phase 3
**Decision:** Write English scripts from scratch (NOT translated Hindi). Focus: S&P 500, FTSE 100, Bitcoin. USA/UK audience.

Voice: `en-US-JennyNeural` | Upload: `upload_youtube_english.py` | Slides: 22+ × 32s = 11+ min | SEO: `S&P500 USStocks UKInvesting GlobalInvesting Bitcoin2026`

---

*Documentation maintained by AI360Trading automation.*
*Last audit: April 12, 2026 — Bugs from April 11 run documented. Improvement backlog updated.*
*Critical fixes needed (in order): Item 1 (double upload), Item 2 (OAuth), Item 3 (analysis duration), Item 4 (SEO titles), Item 5 (RSS feed)*
*FB Group + Instagram: Manual by owner — no action needed.*
*Update this file whenever architecture, secrets, platform status, or file logic changes.*
