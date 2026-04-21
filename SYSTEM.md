# AI360Trading — Master System Documentation

**Last Updated:** April 21, 2026 — upload_youtube.py --type fix + voice fix + duplicate upload fix
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 Planned | Phase 4 (Dhan Live) Planned
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
| YouTube Hindi | ✅ Auto | Analysis + Education + Shorts + Reels working |
| YouTube English | 🔄 Building | Phase 3 — auto-translated separate channel |
| YouTube Shorts | ✅ Auto | Short 2 (Madhur) + Short 3 (Neerja) working |
| YouTube Community Posts | ✅ Built | generate\_community\_post.py — 12:00 PM daily |
| YouTube Reels | ✅ Auto | ZENO reel (8:30 PM) working |
| YouTube Morning Reel | ✅ Auto | 7:00 AM reel (generate\_reel\_morning.py) working |
| Facebook Page | ✅ Auto | Posts, reels, article shares all working |
| Facebook Group | ❌ Broken | Missing `publish_to_groups` token scope — see Section 12 |
| Facebook Kids Page | ❌ Broken | Needs page-specific token `FACEBOOK_KIDS_PAGE_TOKEN` — see Section 12 |
| Instagram | ⚠️ Manual | API permanently removed. Download artifact → post manually from phone |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | Signal alerts to all 3 channels (paper trading — followers take manual entry) |

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

| # | Content | Time (IST) | Platform | Status |
| --- | --- | --- | --- | --- |
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + FB | ✅ |
| 2 | Part 1 Video (16:9) | 7:30 AM weekday / 9:30 AM weekend | YouTube | ✅ |
| 3 | Part 2 Video (16:9) | 7:30 AM (same workflow) | YouTube | ✅ |
| 4 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | ✅ |
| 5 | Short 3 Hinglish (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 6 | Short 4 English (9:16) | 11:30 AM (same workflow) | YouTube English Shorts | 🔄 Phase 3 |
| 7 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 8 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB | ✅ |
| 9 | YouTube Community Post | 12:00 PM | YouTube Community Tab | ✅ |
| **Total** | **12 pieces/day** | — | — | — |

> **Instagram:** API permanently removed. Download artifact from GitHub Actions → post manually from phone.

---

## 5. GitHub Actions Workflows

| File | Trigger (IST) | Purpose | Mode-Aware |
| --- | --- | --- | --- |
| `main.yml` | Every 5 min (market hours, Mon–Fri) | `trading_bot.py` — Nifty200 signals | ✅ Auto-skips weekends/holidays |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 (analysis) + Part 2 (education) — both upload internally | ✅ |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 — uploads internally + Community Post | ✅ |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning Reel + ZENO Reel | ✅ |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages | ✅ |
| `token_refresh.yml` | Every 50 days (1st + 20th of month) | Auto META token refresh | N/A |
| `keepalive.yml` | Periodic | Prevents GitHub disabling inactive workflows | N/A |

All workflows support `workflow_dispatch` with a `content_mode` dropdown to force any mode for testing.

---

## 6. Complete File Map

### Core Infrastructure (Phase 1 — Complete)

| File | Role | Status |
| --- | --- | --- |
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates fallback | ✅ |
| `human_touch.py` | Anti-AI-penalty layer — 50+ hooks, personal phrases, TTS variation, SEO tags | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update + Telegram alert | ✅ |

### Core Content Generation (Phase 2 — All Upgraded)

| File | Role | Key Tech | Status |
| --- | --- | --- | --- |
| `trading_bot.py` | Nifty200 signal monitor + TSL manager + Telegram alerts | gspread + Google Sheets + Telegram Bot API | ✅ v13.4 |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Neerja) — uploads both internally | ai\_client, human\_touch, Edge-TTS | ✅ Fixed Apr 2026 |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) — renders only, does NOT upload | ai\_client, human\_touch, MoviePy | ✅ Phase 2 |
| `generate_reel_morning.py` | Morning reel (7:00 AM) — renders only, does NOT upload | ai\_client, human\_touch, MoviePy | ✅ |
| `generate_analysis.py` | 8-slide market analysis video (Part 1) — uploads internally | ai\_client, human\_touch, MoviePy | ✅ Phase 2 |
| `generate_education.py` | Educational deep-dive video (Part 2) — uploads internally | ai\_client, human\_touch, content\_calendar | ✅ Phase 2 |
| `generate_articles.py` | 4 SEO articles daily → Jekyll \_posts | ai\_client, human\_touch, Google Indexing | ✅ Phase 2 |
| `generate_community_post.py` | YouTube daily community text post — 12:00 PM | ai\_client, human\_touch | ✅ Phase 2 |

### Upload & Distribution

| File | Role | Status |
| --- | --- | --- |
| `upload_youtube.py` | Uploads reels ONLY: `--type reel` (ZENO) or `--type morning`. Shorts/Analysis/Education upload themselves internally. | ✅ Fixed Apr 2026 |
| `upload_youtube_english.py` | Uploads to English channel (separate credentials) | 🔄 Phase 3 |
| `upload_facebook.py` | Uploads reel to FB Page; posts articles; supports `--meta-prefix morning/kids` | ✅ |
| `upload_instagram.py` | Removed — Instagram API requires paid Meta App Review. Post manually. | ❌ Removed |

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

---

## 7. AI Fallback Chain

All content generation uses `ai_client.py`. **Never call Groq/Gemini/Claude/OpenAI directly in generators.**

```
Groq — llama-3.3-70b-versatile (primary — fastest, free)
    ↓ fails
Google Gemini — gemini-2.0-flash (secondary)
    ↓ fails
Anthropic Claude — claude-haiku-4-5 (tertiary — best human-touch writing)
    ↓ fails
OpenAI — gpt-4o-mini (quaternary — reliable fallback)
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
data     = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
clean    = ht.humanize(raw_output, lang="hi")
hook     = ht.get_hook(mode=CONTENT_MODE, lang="hi")
tags     = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")
speed    = ht.get_tts_speed()  # pass to edge_tts rate param
```

---

## 8. Trading Bot Architecture

### Overview

| Component | File | Role |
| --- | --- | --- |
| AppScript v13.3 | Google Sheets bound script | Scans Nifty200 sheet, applies filters, writes WAITING candidates to AlertLog, stores memory in T4 |
| Python Bot v13.4 | `trading_bot.py` | Monitors AlertLog every 5 min, manages WAITING→TRADED transition, TSL updates, exit logic, Telegram alerts |

**Current status:** Paper trading. Followers receive Telegram signals and take manual entry. Dhan API integration planned for Phase 4 after backtest validation.

### Google Sheets Structure

| Sheet | Purpose |
| --- | --- |
| `Nifty200` | Live data for all 200 stocks — CMP, DMAs, FII data, signals, scores (34 cols) |
| `AlertLog` | Active + waiting trades — 15 rows, 19 cols. T2=YES/NO automation switch. T4=memory string |
| `History` | Closed trade log — 18 cols A–R |

### AlertLog Column Map (0-based)

```
A=0  Signal Time    B=1  Symbol        C=2  Live Price     D=3  Priority Score
E=4  Trade Type     F=5  Strategy      G=6  Breakout Stage H=7  Initial SL
I=8  Target         J=9  RR Ratio      K=10 Trade Status   L=11 Entry Price
M=12 Entry Time     N=13 Days in Trade O=14 Trailing SL    P=15 P/L%
Q=16 ATH Warning    R=17 Risk ₹        S=18 Position Size  T=19 SYSTEM CONTROL
```

**T2** = automation on/off switch (set YES to enable)
**T4** = memory string (key=value pairs, comma separated — stores TSL, MAX, ATR, CAP, MODE, SEC, exit dates, daily flags)

### Nifty200 Column Map (0-based, used by AppScript)

```
r[0]  NSE_SYMBOL          r[1]  SECTOR
r[2]  CMP                 r[3]  %Change (D)
r[4]  20_DMA              r[5]  50_DMA
r[6]  200_DMA             r[7]  SMA_Structure (H)
r[8]  52W_Low             r[9]  52W_High (J)
r[10] %up_52W_Low         r[11] %down_52W_High
r[12] %dist_20DMA (M)     r[13] Avg_Volume_20D
r[14] Volume_vs_Avg% (O)  r[15] FII_Buy_Zone (P)
r[16] FII_Rating (Q)      r[17] Leader_Type (R)
r[18] Signal_Score (S)    r[19] FINAL_ACTION (T)
r[20] RS (U)              r[21] Sector_Trend (V)
r[22] Breakout_Stage (W)  r[23] Retest% (X)
r[24] Trade_Type (Y)      r[25] Priority_Score (Z)
r[26] Pivot_Resistance(AA) r[27] VCP_Status (AB)
r[28] ATR14 (AC)          r[29] Days_Since_Low (AD)
r[30] 52W_Breakout_Score  r[31] Sector_Rotation_Score (AF)
r[32] FII_Buying_Signal(AG) r[33] Master_Score (AH)
```

### AppScript v13.3 — Key Logic

**Market Regime:** Nifty50 CMP vs 20DMA → Bullish or Bearish.

**Bearish gate (4 conditions all required):**
- Leader\_Type = "Sector Leader"
- AF ≥ 5 (RS≥2.5 with sector tailwind)
- Master\_Score ≥ 22
- FII signal ≠ "FII CAUTION" or "FII SELLING"

**10 scan gates (in order):**
1. FII SELLING → skip always
2. Market regime filter (bullish vs bearish path)
3. Late entry block (BREAKOUT CONFIRMED needs RS≥7)
4. Price validity (CMP>0, ATR>0, CMP≤₹5000)
5. Extension filter (>8% above 20DMA → skip)
6. Pivot resistance buffer (within 2% below pivot → skip)
7. Volume filter (bullish market only — vol<120% → skip)
8. ATH buffer (within 3% of 52W high → skip)
9. Trade type (AVOID/NO TRADE → skip)
10. Sector concentration (max 2 per sector)

**Capital tiers:**
- ₹13,000 — MasterScore≥28 AND AF≥10 (high conviction)
- ₹10,000 — MasterScore≥22 OR Accumulation Zone (medium conviction)
- ₹7,000 — standard

**Trade modes:** VCP / MOM / STD (stored as `_MODE` in T4 memory)

**Sort order:** finalScore DESC, then ATR% ASC as tiebreaker within ±2 score points.

### Python Bot v13.4 — Key Logic

**TSL Parameters (mode-aware):**

```
TSL_PARAMS = {
    "VCP": { "breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0 },
    "MOM": { "breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0 },
    "STD": { "breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0 },
}
```

**TSL progression (STD):** <2% hold SL → 2–4% breakeven → 4–10% lock +2% → >10% ATR trail → >8% gap-up lock 50%

**Daily message schedule:**
- 08:45–09:15 → Good Morning (open trades P/L + waiting count + sector context)
- 09:15–15:30 → Market hours (entry alerts, TSL updates, exit alerts)
- 12:28–12:38 → Mid-day pulse
- 15:15–15:45 → Market close summary

**Hard exit rules:**
- Loss > 5% → immediate hard exit
- Min hold: 2 days swing, 3 days positional
- 5 trading day cooldown after exit before same stock re-enters

### History Sheet Columns (A–R)

```
A  Symbol      B  Entry Date   C  Entry Price  D  Exit Date
E  Exit Price  F  P/L%         G  Result        H  Strategy
I  Exit Reason J  Trade Type   K  Initial SL    L  TSL at Exit
M  Max Price   N  ATR at Entry O  Days Held     P  Capital ₹
Q  Profit/Loss ₹               R  Options Note
```

---

## 9. Critical Upload Chain

> ⚠️ **RULE: Each video type has exactly ONE upload path. Never call upload_youtube.py for shorts, analysis, or education — they upload internally.**

### Upload Responsibility Map

| Video Type | Who Uploads | Workflow |
| --- | --- | --- |
| ZENO Evening Reel | `upload_youtube.py --type reel` | `daily_reel.yml` step after generate\_reel.py |
| Morning Reel | `upload_youtube.py --type morning` | `daily_reel.yml` morning step |
| Analysis (Part 1) | `generate_analysis.py` internal | No separate upload step in `daily-videos.yml` |
| Education (Part 2) | `generate_education.py` internal | No separate upload step in `daily-videos.yml` |
| Short 2 | `generate_shorts.py` internal | No separate upload step in `daily-shorts.yml` |
| Short 3 | `generate_shorts.py` internal | No separate upload step in `daily-shorts.yml` |

### Evening ZENO Reel (8:30 PM)

```
generate_reel.py
    └── output/reel_YYYYMMDD.mp4
    └── output/meta_YYYYMMDD.json  ← title, description, tags all written here

upload_youtube.py --type reel
    └── Reads meta_YYYYMMDD.json for title/description/tags
    └── Uploads reel_YYYYMMDD.mp4 to YouTube
    └── Writes youtube_video_id + youtube_video_url back to meta

upload_facebook.py
    └── Uploads reel to Facebook Page
    └── Overwrites meta → public_video_url (Facebook watch URL)
    └── Posts articles from RSS feed to Page + Group
```

### Morning Reel (7:00 AM)

```
generate_reel_morning.py
    └── output/morning_reel_YYYYMMDD.mp4
    └── output/morning_reel_meta_YYYYMMDD.json

upload_youtube.py --type morning
    └── Reads morning_reel_meta_YYYYMMDD.json
    └── Uploads morning_reel_YYYYMMDD.mp4 to YouTube
    └── Writes youtube_video_id back to meta

upload_facebook.py --meta-prefix morning
    └── Reads morning_reel_meta_YYYYMMDD.json
    └── Uploads to Facebook Page
```

### Daily Videos (7:30 AM)

```
generate_analysis.py
    └── Generates + UPLOADS to YouTube internally
    └── output/analysis_video.mp4
    └── output/analysis_video_id.txt       ← Part 1 ID for Part 2 to cross-link
    └── output/analysis_meta_YYYYMMDD.json

generate_education.py
    └── Reads analysis_video_id.txt → links Part 1 in description
    └── Generates + UPLOADS to YouTube internally
    └── output/education_video.mp4
    └── output/education_meta_YYYYMMDD.json
```

### Shorts (11:30 AM)

```
generate_shorts.py
    └── Generates Short 2 (Madhur) + Short 3 (Neerja)
    └── UPLOADS both to YouTube internally
    └── Posts links to Facebook Page via share_to_facebook()
    └── output/short2_YYYYMMDD.mp4
    └── output/short3_YYYYMMDD.mp4
```

### Instagram — Manual Only

API access permanently removed (requires paid Meta App Review). Workflow saves artifact → download from GitHub Actions → post manually from phone.

---

## 10. Environment Variables & Secrets

All stored in **GitHub Actions Secrets**. Never hardcode any of these values.

### Dhan Trading API (Phase 4 — not connected yet)

| Secret | Purpose | Status |
| --- | --- | --- |
| `DHAN_API_KEY` | API key | ✅ Added — not connected yet |
| `DHAN_API_SECRET` | API secret | ✅ Added — not connected yet |
| `DHAN_CLIENT_ID` | Client ID | ✅ Added — not connected yet |
| `DHAN_PIN` | Account PIN | ✅ Added — not connected yet |
| `DHAN_TOTP_KEY` | 2FA TOTP key | ✅ Added — not connected yet |

### Social Platforms

| Secret | Purpose | Status |
| --- | --- | --- |
| `META_ACCESS_TOKEN` | Facebook + Instagram API (AI360Trading page) | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` | Facebook App ID | ✅ Added |
| `META_APP_SECRET` | Facebook App Secret | ✅ Added |
| `FACEBOOK_PAGE_ID` | AI360Trading Facebook Page ID | ✅ |
| `FACEBOOK_GROUP_ID` | AI360Trading Facebook Group ID | ✅ (posting broken — token scope) |
| `FACEBOOK_KIDS_PAGE_ID` | HerooQuest Kids Page ID (1021152881090398) | ✅ |
| `FACEBOOK_KIDS_PAGE_TOKEN` | Page-specific token for HerooQuest video upload | ❌ Missing — see Section 12 |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business/Creator numeric ID | ✅ Added (manual post only) |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON (Hindi channel — ai360trading) | ✅ |
| `YOUTUBE_CREDENTIALS_KIDS` | YouTube OAuth JSON (HerooQuest Kids channel) | ✅ |
| `YOUTUBE_CREDENTIALS_EN` | YouTube OAuth JSON (English channel) | ✅ Added |

### AI Providers (Fallback Chain)

| Secret | Purpose | Priority | Status |
| --- | --- | --- | --- |
| `GROQ_API_KEY` | Groq — Llama 3.3 70B | Primary | ✅ |
| `GEMINI_API_KEY` | Google Gemini 2.0 Flash | Secondary | ✅ Added |
| `ANTHROPIC_API_KEY` | Claude Haiku | Tertiary | ✅ Added |
| `OPENAI_API_KEY` | GPT-4o-mini | Quaternary | ✅ Added (billing limit hit — top up) |

### Telegram

| Secret | Purpose |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Bot authentication token |
| `TELEGRAM_CHAT_ID` | Free channel (ai360trading) |
| `CHAT_ID_ADVANCE` | Advance signals channel (₹499/month) |
| `CHAT_ID_PREMIUM` | Premium signals channel (bundle) |

### Google / GCP

| Secret | Purpose |
| --- | --- |
| `GCP_SERVICE_ACCOUNT_JSON` | Search Console Indexing API + Google Sheets (gspread) |

### HuggingFace

| Secret | Purpose | Status |
| --- | --- | --- |
| `HF_TOKEN` | HuggingFace API for kids image generation | ✅ (model endpoints returning 404 — update model IDs) |

### General

| Secret | Purpose |
| --- | --- |
| `GH_TOKEN` | GitHub API token |

---

## 11. Human Touch System (Anti-AI-Penalty)

All content uses `human_touch.py`. **Never use raw AI output directly.**

| Technique | Method | What It Does |
| --- | --- | --- |
| 50+ rotating hooks | `ht.get_hook(mode, lang)` | No two videos start the same |
| Personal phrases | `ht.get_personal_phrase(lang)` | "Maine dekha hai..." injected naturally |
| TTS speed variation | `ht.get_tts_speed()` | 0.95–1.05x range — passed to edge\_tts rate param |
| Humanize output | `ht.humanize(text, lang)` | Strips robotic patterns, varies connectors |
| Emoji rotation | `ht.get_emoji_set()` | Day-seeded — different emoji set each day |
| SEO tags | `seo.get_video_tags(mode, lang)` | India + Global tags combined |
| Connector variation | Internal to humanize() | "aur/lekin/kyunki" rotated |
| Banned phrase removal | Internal to humanize() | "Certainly!", "It's important to note" stripped |

---

## 12. Known Issues & Fixes

### ✅ FIXED April 2026 — Duplicate Video Uploads

**Root cause:** `daily-videos.yml` called `upload_youtube.py --type analysis` and `--type education` after generators that already upload internally. `daily-shorts.yml` called `upload_youtube.py --type short` after `generate_shorts.py` which also uploads internally. Every video was uploading twice with different titles.

**Fix:** Removed all redundant `upload_youtube.py` calls from `daily-videos.yml` and `daily-shorts.yml`. Each video type now has exactly one upload path. See Section 9.

**Rule:** Never call `upload_youtube.py` for shorts, analysis, or education.

### ✅ FIXED April 2026 — Morning Reel YouTube Upload Failing

**Root cause:** `upload_youtube.py` had no `--type` argument. When called with `--type morning` it ignored the flag, looked for `reel_*.mp4`, found nothing, and aborted.

**Fix:** `upload_youtube.py` now uses `argparse` with `--type morning | reel`. Each type resolves to the correct video file and meta JSON via `resolve_files()`.

### ✅ FIXED April 2026 — Short 3 Same Voice as ZENO Reel

**Root cause:** Short 3 used `hi-IN-SwaraNeural` — identical to ZENO reel. Edge TTS only has 2 hi-IN voices (Madhur + Swara). Both shorts and reel sounded the same.

**Fix:** Short 3 now uses `en-IN-NeerjaNeural` — Indian English female, handles Hinglish scripts naturally, completely distinct from Madhur and Swara.

### ✅ FIXED April 2026 — PLAYLIST env vars in Workflows

**Root cause:** `daily_reel.yml`, `daily_reel_morning.yml`, and `daily-shorts.yml` passed `PLAYLIST_ZENO_WISDOM` and `PLAYLIST_SWING_TRADE` env vars. No playlists exist on the channel. These caused noise in logs referencing non-existent secrets.

**Fix:** Removed from all workflow env blocks. See Playlist Policy in Section 13 for when to add them back.

### Facebook Group Posting ❌

**Root causes (check in order):**
1. `META_ACCESS_TOKEN` missing `publish_to_groups` scope
2. Bot account not **Admin** of the group
3. Group Settings → Advanced → "Allow content from apps" OFF
4. App not approved for Groups API by Meta

**Fix:** developers.facebook.com → App → Add `publish_to_groups` → regenerate token → update secret.

### Facebook Kids Page Upload ❌ `(#200) Permission Error`

**Root cause:** `META_ACCESS_TOKEN` is only authorized for the AI360Trading page. HerooQuest Kids page needs its own page-specific access token.

**Fix:**
1. Visit: `https://graph.facebook.com/v21.0/me/accounts?access_token=YOUR_META_TOKEN`
2. Find HerooQuest in the list → copy its `access_token`
3. Add as GitHub secret: `FACEBOOK_KIDS_PAGE_TOKEN`
4. In `kids-daily.yml`, change the Facebook upload step to pass `META_ACCESS_TOKEN: ${{ secrets.FACEBOOK_KIDS_PAGE_TOKEN }}`

### Kids Channel Image Generation — All AI Sources Dead ⚠️

All layers in `generate_kids_video.py` are currently failing:
- Gemini 2.5 Flash Image → free tier daily quota = 0
- Gemini 2.0 Flash Exp Image → model removed by Google (404)
- HuggingFace FLUX/SD models → all returning 404 (model paths changed)
- DALL-E 3 → OpenAI billing hard limit reached

**Current state:** Falls back to Heroo placeholder images. Videos still generate and upload fine. Fix by updating HuggingFace model IDs in `generate_kids_video.py` and topping up OpenAI account.

### YouTube Community Tab ⚠️

Requires **500+ subscribers**. Below that, `generate_community_post.py` saves post text to `output/community_post_YYYYMMDD.txt` for manual posting without crashing.

### META\_ACCESS\_TOKEN Expiry — Automated ✅

`token_refresh.yml` runs every 50 days. Refreshes token + updates GitHub Secret + sends Telegram alert.

---

## 13. Technical Standards

### The "Full Code" Rule

> AI assistants **must always provide the complete content** of any modified file. Partial snippets or diffs are strictly prohibited.

### AI Client Usage Rule — No Exceptions

> **Never call AI APIs directly in generators.** Always use `ai_client.py`.

```python
from ai_client import ai, img_client
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang=LANG)
data     = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang=LANG)
```

### Human Touch Usage Rule — No Exceptions

> **Never use raw AI output.** Always pass through human\_touch.

```python
from human_touch import ht, seo
hook  = ht.get_hook(mode=CONTENT_MODE, lang=LANG)
clean = ht.humanize(raw_script, lang=LANG)
tags  = seo.get_video_tags(mode=CONTENT_MODE, lang=LANG)
speed = ht.get_tts_speed()  # pass to edge_tts rate param
```

### Dependency Pins

| Package | Version | Reason |
| --- | --- | --- |
| `Pillow` | `>=10.3.0` | Required for LANCZOS resampling |
| `imageio` | `==2.9.0` | Prevents MoviePy rendering crashes |
| `moviepy` | `==1.0.3` | Force reinstall — newer versions break audio |
| `yfinance` | Latest | Use `fast_info['last_price']` only — not `.history()` |
| `PyNaCl` | Latest | Required for GitHub Secret encryption in token\_refresh.py |
| `google-generativeai` | Latest | Gemini fallback in ai\_client.py |
| `anthropic` | Latest | Claude fallback in ai\_client.py |
| `openai` | Latest | OpenAI fallback in ai\_client.py |
| `gspread` | Latest | Google Sheets access in trading\_bot.py |
| `oauth2client` | Latest | GCP service account auth for gspread |
| `pytz` | Latest | IST timezone handling in trading\_bot.py |

### Voice Assignments — FINAL (Do NOT change)

| Voice ID | Type | Used For |
| --- | --- | --- |
| `hi-IN-MadhurNeural` | Hindi Male | Short 2 — authoritative trade setups |
| `en-IN-NeerjaNeural` | Indian English Female | Short 3 — global market pulse (Hinglish-compatible) |
| `hi-IN-SwaraNeural` | Hindi Female | ZENO Reel, Morning Reel, Analysis, Education |
| `en-US-JennyNeural` | English Female | English channel — all English content |
| `en-US-GuyNeural` | English Male | English Short 2 alternative |

> **Rule:** Edge TTS only has 2 hi-IN voices (Madhur + Swara). Short 3 uses `en-IN-NeerjaNeural` — Indian English — which handles Hinglish scripts and sounds completely distinct.
> Short 2, Short 3, and ZENO reel must always use THREE DISTINCT VOICES.

### TTS Speed via human\_touch

```python
tts_speed = ht.get_tts_speed()           # returns float 0.95–1.05
rate_pct  = int((tts_speed - 1.0) * 100)
rate_str  = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
await edge_tts.Communicate(text, VOICE, rate=rate_str).save(path)
```

### Video Formats

| Content | Ratio | Platform |
| --- | --- | --- |
| Analysis + Education | 16:9 | YouTube |
| Short 2, Short 3, Short 4, Morning Reel, ZENO Reel | 9:16 | YouTube Shorts / Reels |

### SEO Tags Strategy

Every video uses `seo.get_video_tags()` from `human_touch.py` — **never hardcoded tag lists in any generator or uploader**.

- India: `Nifty50`, `TradingIndia`, `StockMarketIndia`, `BankNifty`
- Global: `USStocks`, `UKInvesting`, `BrazilMarket`, `UAEInvesting`, `GlobalInvesting`
- Universal: `Finance`, `Investing`, `FinancialLiteracy`, `Shorts`

### Playlist Policy

No playlists exist on the channel yet. **Do NOT add `PLAYLIST_*` secrets or env vars to any workflow** until playlists are manually created in YouTube Studio. When ready:
1. Create playlist in YouTube Studio → copy playlist ID (starts with `PL`)
2. Add as GitHub secret (e.g. `PLAYLIST_ZENO_WISDOM`)
3. Add env var to relevant workflow step
4. Add `youtube.playlistItems().insert()` call in `upload_youtube.py` after upload

---

## 14. Disney 3D Reel Roadmap

| Phase | Tool | Quality | Timeline | Status |
| --- | --- | --- | --- | --- |
| 1 (Now) | PIL + MoviePy + ZENO PNG | 2D animated slides | Current | ✅ Active |
| 2 | Gemini Veo API (free tier) | AI video clips | 3–6 months | Hooks in ai\_client.py |
| 3 | Stable Diffusion + AnimateDiff | 3D style frames | 6–12 months | Planned |
| 4 | Google Veo 2 / Sora (when free) | True Disney-style 3D | 12–18 months | Planned |

> `img_client` in `ai_client.py` is the upgrade hook — swap in Phase 2 with zero changes to generators.

---

## 15. Full Data Flow

```
Market hours (Mon–Fri, 9:15 AM–3:30 PM IST)
└── main.yml (every 5 min)
    └── trading_bot.py v13.4 → AlertLog → TSL → Telegram alerts

7:00 AM daily
└── daily_reel.yml (morning job)
    └── generate_reel_morning.py  → output/morning_reel_YYYYMMDD.mp4
    └── upload_youtube.py --type morning → YouTube ✅
    └── upload_facebook.py --meta-prefix morning → Facebook Page ✅

7:30 AM / 9:30 AM daily
└── daily-videos.yml
    └── generate_analysis.py  → renders + uploads internally → YouTube ✅
    └── generate_education.py → renders + uploads internally → YouTube ✅

10:00 AM / 11:30 AM daily
└── daily-articles.yml
    └── generate_articles.py → 4 articles → GitHub Pages ✅ → Facebook ✅

11:30 AM / 1:30 PM daily
└── daily-shorts.yml
    └── generate_shorts.py → Short 2 (Madhur) + Short 3 (Neerja)
        └── uploads both internally → YouTube ✅
        └── share_to_facebook() → Facebook Page ✅
    └── generate_community_post.py → YouTube Community Tab ✅ (if 500+ subs)

8:30 PM daily
└── daily_reel.yml (evening job)
    └── generate_reel.py → output/reel_YYYYMMDD.mp4 + meta_YYYYMMDD.json
    └── upload_youtube.py --type reel → YouTube ✅
    └── upload_facebook.py → Facebook Page ✅
    └── Instagram → MANUAL (download artifact, post from phone)
```

---

## 16. Website

- **URL:** `ai360trading.in`
- **Hosting:** GitHub Pages (Jekyll, `master` branch `_posts/`)
- **Publishing:** Auto-commit by `daily-articles.yml`
- **SEO Indexing:** Instant via `GCP_SERVICE_ACCOUNT_JSON`
- **Revenue:** Google AdSense (USA/UK English readers = highest CPM)
- **Content pillars:** Stock Market, Bitcoin/Crypto, Personal Finance, AI Trading
- **Market coverage:** India (Nifty50, BankNifty), USA (S&P500, NASDAQ), UK (FTSE100), Brazil (IBOVESPA), Crypto (BTC, ETH)

---

## 17. Social Media Links

| Platform | Handle/Link |
| --- | --- |
| 🌐 Website | ai360trading.in |
| 📣 Telegram (Free) | @ai360trading |
| 📣 Telegram (Advance) | ai360trading\_Advance — ₹499/month |
| 📣 Telegram (Premium) | ai360trading\_Premium — bundle |
| ▶️ YouTube | @ai360trading |
| 📸 Instagram | @ai360trading |
| 👥 Facebook Group | facebook.com/groups/ai360trading |
| 📘 Facebook Page | facebook.com/ai360trading |
| 🐦 Twitter/X | @ai360trading |

---

## 18. Phase Roadmap

### Phase 1 ✅ Complete
`ai_client.py`, `human_touch.py`, `token_refresh.py`, `generate_reel_morning.py`

### Phase 2 ✅ Complete
`generate_articles.py`, `generate_analysis.py`, `generate_education.py`, `generate_reel.py`, `generate_shorts.py`, `generate_community_post.py` — all upgraded to ai\_client + human\_touch

### Phase 3 🔄 In Progress

| Item | File | Priority |
| --- | --- | --- |
| English channel shorts | `generate_english.py` | 🟡 Medium |
| English channel upload | `upload_youtube_english.py` | 🟡 Medium |
| Fix Facebook Group token | Manual config task | 🔴 High |
| Fix Facebook Kids page token | Add `FACEBOOK_KIDS_PAGE_TOKEN` secret | 🔴 High |
| Fix Kids image generation | Update HF model IDs in `generate_kids_video.py` | 🔴 High |
| Top up OpenAI for DALL-E 3 | OpenAI billing | 🟡 Medium |
| YouTube Playlists | Create in Studio → add secrets → wire in upload\_youtube.py | 🟡 Medium (after 500+ subs) |
| Disney 3D reel upgrade | `ai_client.py` img\_client Phase 2 | 🔵 Future |

### Phase 4 📋 Planned — Dhan Live Trading

| Item | Dependency | Notes |
| --- | --- | --- |
| Backtest validation | 30–40 live paper trades, win rate >35% | Currently running paper trades |
| Dhan API connection | `DHAN_API_KEY` secrets already added | Auto-execute on WAITING→TRADED |
| Options CE execution | Dhan API + lot size data | CE flag already in alerts (informational) |
| Live capital deployment | After backtest confirms system | ₹45,000 max deployed (₹5k buffer) |

---

## 19. How to Test Everything

### Test a workflow manually
GitHub Actions → select workflow → **Run workflow** → set `content_mode` dropdown → watch logs.

### Verify no duplicate uploads
Each video appears only once:
- Analysis/Education: uploaded in generator logs only (no `upload_youtube.py` step in `daily-videos.yml`)
- Shorts: uploaded in `generate_shorts.py` logs only (no `upload_youtube.py` step in `daily-shorts.yml`)
- ZENO reel: `upload_youtube.py --type reel` logs only
- Morning reel: `upload_youtube.py --type morning` logs only

### Verify distinct voices
- Short 2 log: `hi-IN-MadhurNeural`
- Short 3 log: `en-IN-NeerjaNeural`
- ZENO reel / Morning reel / Analysis / Education: `hi-IN-SwaraNeural`

### Verify ai\_client fallback chain
In logs: `✅ AI generated via groq` (or gemini/claude/openai if Groq down)

### Force each content mode
```
workflow_dispatch → content_mode = market
workflow_dispatch → content_mode = weekend
workflow_dispatch → content_mode = holiday
```

### Automation on/off switch
Google Sheet → AlertLog → cell T2 → set "YES" to enable, anything else to disable.

---

*Documentation maintained by AI360Trading automation.*
*Last full audit: April 21, 2026 — Claude Sonnet 4.6*
*Based on live repo read at: github.com/systronics/ai360trading*
*April 2026 fixes applied: duplicate-upload fix, upload_youtube.py --type morning support, Short 3 voice → en-IN-NeerjaNeural, PLAYLIST env vars removed, Facebook Kids token issue documented*
*Trading bot: AppScript v13.3 + Python v13.4 — paper trading, Google Sheets, Dhan Phase 4*
*Phase 3 remaining: English channel, Facebook Group token, Facebook Kids token, Kids image fix, YouTube playlists*
*Phase 4 planned: Dhan live trading after backtest validation*
*Update this file whenever architecture, secrets, platform status, or file logic changes.*
