# AI360Trading — Master System Documentation

**Last Updated:** April 16, 2026 — Duplicate-upload fix + Voice fix + SEO meta fix
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
| Facebook Group | ❌ Broken | Missing `publish_to_groups` token scope — see Section 11 |
| Instagram | ⚠️ Partial | Upload chain built; `INSTAGRAM_ACCOUNT_ID` secret needed |
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
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + FB + Instagram | ✅ |
| 2 | Part 1 Video (16:9) | 7:30 AM weekday / 9:30 AM weekend | YouTube | ✅ |
| 3 | Part 2 Video (16:9) | 7:30 AM (same workflow) | YouTube | ✅ |
| 4 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | ✅ |
| 5 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 6 | Short 4 English (9:16) | 11:30 AM (same workflow) | YouTube English Shorts | 🔄 Phase 3 |
| 7 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 8 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB + Instagram | ✅ |
| 9 | YouTube Community Post | 12:00 PM | YouTube Community Tab | ✅ |
| **Total** | **12 pieces/day** | — | — | — |

> **USA/UK prime time content:** Videos uploaded at IST times but SEO-optimised for 11 PM–1 AM IST peak.

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
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Neerja) | ai\_client, human\_touch, Edge-TTS | ✅ Fixed Apr 2026 |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ai\_client, human\_touch, MoviePy | ✅ Fixed Apr 2026 |
| `generate_reel_morning.py` | Morning reel (7:00 AM) — day/country aware | ai\_client, human\_touch, MoviePy | ✅ |
| `generate_analysis.py` | 8-slide market analysis video (Part 1) | ai\_client, human\_touch, MoviePy | ✅ Fixed Apr 2026 |
| `generate_education.py` | Educational deep-dive video (Part 2) | ai\_client, human\_touch, content\_calendar | ✅ Phase 2 |
| `generate_articles.py` | 4 SEO articles daily → Jekyll \_posts | ai\_client, human\_touch, Google Indexing | ✅ Phase 2 |
| `generate_community_post.py` | YouTube daily community text post — 12:00 PM | ai\_client, human\_touch | ✅ Phase 2 |

### Upload & Distribution

| File | Role | Status |
| --- | --- | --- |
| `upload_youtube.py` | Uploads ZENO reel ONLY; saves `youtube_video_id` + `public_video_url` to meta | ✅ Fixed Apr 2026 |
| `upload_youtube_english.py` | Uploads to English channel (separate credentials) | 🔄 Phase 3 |
| `upload_facebook.py` | Uploads reel to FB Page; shares to Group; posts articles | ✅ |
| `upload_instagram.py` | Auto-uploads via Meta API using `public_video_url` from meta | ✅ |

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
Google Gemini — gemini-2.0-flash (secondary — best image/video roadmap for Disney 3D)
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
# Text generation
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang="hi")

# JSON generation
data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")

# Humanize raw output
clean = ht.humanize(raw_output, lang="hi")

# Get rotating hook
hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")

# Get SEO tags
tags = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")

# TTS speed
speed = ht.get_tts_speed()
```

---

## 8. Trading Bot Architecture

### Overview

The trading system is split across two components that work together:

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

**Market Regime:** Nifty50 CMP vs 20DMA → Bullish or Bearish. Controls which filter gate applies.

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

**Trade modes (stored as \_MODE in T4 memory):**
- VCP — AB<0.04 + pre-breakout stage
- MOM — Strong Bull + RS≥6
- STD — everything else (default in bear market)

**Memory keys written per stock:**
- `{sym}_CAP` — capital tier (7000/10000/13000)
- `{sym}_MODE` — trade mode (VCP/MOM/STD)
- `{sym}_SEC` — sector name (for Good Morning sector context)

**Sort order:** finalScore DESC, then ATR% ASC as tiebreaker within ±2 score points (minimum SL preference).

### Python Bot v13.4 — Key Logic

**TSL Parameters (mode-aware):**

```
TSL_PARAMS = {
    "VCP": { "breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0 },
    "MOM": { "breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0 },
    "STD": { "breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0 },
}
```

STD trail widened in v13.3 (6→10, atr\_mult 1.5→2.5) to support full-ride vision on swing trades.

**TSL progression (STD example):**
- Gain < 2% → hold initial SL
- Gain 2–4% → move to breakeven
- Gain 4–10% → lock at entry +2%
- Gain > 10% → ATR trail (2.5× ATR below CMP)
- Gain > 8% gap-up → lock 50% of gap

**Daily message schedule:**
- 08:45–09:15 → Good Morning (open trades P/L + waiting count + sector context)
- 09:15–15:30 → Market hours (entry alerts, TSL updates, exit alerts)
- 12:28–12:38 → Mid-day pulse
- 15:15–15:45 → Market close summary

**Telegram channels:**
- Basic (free) → market mood, signal closed result only
- Advance (₹499/mo) → full entry/exit details, TSL updates, mid-day pulse
- Premium (bundle) → same as Advance + options CE candidate flag

**CE candidate flag (v13.4 — informational only):**
Fires when market is bullish AND stock ATR% > 1.5%. Shows in Advance + Premium entry alerts only.

```
ATR% < 1.5%    → no flag (premium decay risk)
ATR% 1.5–2.5%  → normal mover: target +65%, SL -40% on premium
ATR% > 2.5%    → fast mover: target +50%, SL -35% on premium
```

**Hard exit rules:**
- Loss > 5% → hard loss exit (immediate, no min-hold check)
- Min hold: 2 days swing, 3 days positional (prevents TSL whipsaw on day 1)
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

Scripts must run in this exact order. Each one feeds data to the next.

> ⚠️ **CRITICAL: Each video type has its own upload path. Do NOT call upload_youtube.py for shorts or analysis.**

### Video Upload Responsibility Map

| Video Type | Who Uploads | Meta File |
| --- | --- | --- |
| ZENO Evening Reel | `upload_youtube.py` (called by workflow) | `meta_YYYYMMDD.json` |
| Morning Reel | `upload_youtube.py` (morning mode) | `morning_reel_meta_YYYYMMDD.json` |
| Analysis (Part 1) | `generate_analysis.py` (internal upload) | `analysis_meta_YYYYMMDD.json` |
| Education (Part 2) | `generate_education.py` (internal upload) | `education_meta_YYYYMMDD.json` |
| Short 2 | `generate_shorts.py` (internal upload) | No separate meta needed |
| Short 3 | `generate_shorts.py` (internal upload) | No separate meta needed |

### Evening ZENO Reel (8:30 PM)

```
generate_reel.py
    └── output/reel_YYYYMMDD.mp4
    └── output/meta_YYYYMMDD.json  ← created here with FULL SEO title/desc/tags
         (public_video_url = "" placeholder)

upload_youtube.py
    └── Reads title/description/tags FROM meta_YYYYMMDD.json (not hardcoded here)
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

### Daily Videos (7:30 AM)

```
generate_analysis.py
    └── Generates + UPLOADS directly to YouTube (internal upload_to_youtube())
    └── output/analysis_video.mp4
    └── output/analysis_video_id.txt       ← Part 1 ID for Part 2 linking
    └── output/analysis_meta_YYYYMMDD.json ← full SEO meta saved here

generate_education.py
    └── Reads analysis_video_id.txt → links Part 1 in description
    └── Generates + UPLOADS directly to YouTube (internal upload_to_youtube())
    └── output/education_video.mp4
    └── output/education_video_id.txt
    └── output/education_meta_YYYYMMDD.json
    └── Updates Part 1 YouTube description with Part 2 URL
```

### Shorts (11:30 AM)

```
generate_shorts.py
    └── Generates Short 2 + Short 3 + UPLOADS both directly to YouTube
    └── output/short2_YYYYMMDD.mp4  ← Short 2 (Madhur voice)
    └── output/short3_YYYYMMDD.mp4  ← Short 3 (Neerja voice)
    └── Posts links to Facebook Page + Group
```

> **Manual fallback for Instagram:** GitHub Actions → Run → Artifacts → download → post manually.

---

## 10. Environment Variables & Secrets

All stored in **GitHub Actions Secrets**. Never hardcode any of these values.

### Dhan Trading API (added — Phase 4 live trading)

| Secret | Purpose | Status |
| --- | --- | --- |
| `DHAN_API_KEY` | API key | ✅ Added — not connected yet |
| `DHAN_API_SECRET` | API secret | ✅ Added — not connected yet |
| `DHAN_CLIENT_ID` | Client ID | ✅ Added — not connected yet |
| `DHAN_PIN` | Account PIN | ✅ Added — not connected yet |
| `DHAN_TOTP_KEY` | 2FA TOTP key | ✅ Added — not connected yet |

> Dhan integration planned for Phase 4 after backtest validation.

### Social Platforms

| Secret | Purpose | Status |
| --- | --- | --- |
| `META_ACCESS_TOKEN` | Facebook + Instagram API | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` | Facebook App ID | ✅ Added |
| `META_APP_SECRET` | Facebook App Secret | ✅ Added |
| `FACEBOOK_PAGE_ID` | Target Facebook Page ID | ✅ |
| `FACEBOOK_GROUP_ID` | Target Facebook Group ID | ✅ (posting broken — token scope issue) |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business/Creator numeric ID | ✅ Added |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON (Hindi channel) | ✅ |
| `YOUTUBE_CREDENTIALS_EN` | YouTube OAuth JSON (English channel) | ✅ Added |

### AI Providers (Fallback Chain)

| Secret | Purpose | Priority | Status |
| --- | --- | --- | --- |
| `GROQ_API_KEY` | Groq — Llama 3.3 70B | Primary | ✅ |
| `GEMINI_API_KEY` | Google Gemini 2.0 Flash | Secondary | ✅ Added |
| `ANTHROPIC_API_KEY` | Claude Haiku | Tertiary | ✅ Added |
| `OPENAI_API_KEY` | GPT-4o-mini | Quaternary | ✅ Added |

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

**Root cause:** `generate_analysis.py` and `generate_shorts.py` both had their own YouTube upload code, AND `upload_youtube.py` was being called separately by the workflow — resulting in each video being uploaded twice with different titles.

**Fix applied:**
- `upload_youtube.py` now only handles the ZENO evening reel
- `generate_analysis.py` uploads its own video internally (single upload)
- `generate_shorts.py` uploads Short 2 and Short 3 internally (single upload each)
- Each generator is responsible for its own upload — no external script calls duplicate it

**Rule going forward:** Each video type has exactly ONE upload path. See Section 9 upload chain.

### ✅ FIXED April 2026 — Short 3 Same Audio as ZENO Reel

**Root cause:** Short 3 was using `hi-IN-SwaraNeural` — the same voice as the ZENO reel. Both also used similar Hinglish market scripts, making them sound identical.

**Fix applied:**
- Short 3 now uses `en-IN-NeerjaNeural` (energetic female voice, distinct from Swara)
- Short 3 script is explicitly about the GLOBAL MACRO picture (Nifty + BTC + Gold + S&P500)
- Short 2 remains `hi-IN-MadhurNeural` (authoritative male — specific trade setups)
- ZENO reel remains `hi-IN-SwaraNeural` (wise female — trading wisdom/philosophy)
- All three are now clearly different in voice AND content angle

**Voice assignment table — DO NOT change these:**

| Voice | Content | Character |
| --- | --- | --- |
| `hi-IN-MadhurNeural` | Short 2 — trade setup | Authoritative male analyst |
| `en-IN-NeerjaNeural` | Short 3 — global macro pulse | Energetic female commentator |
| `hi-IN-SwaraNeural` | ZENO reel + Morning reel + Analysis + Education | Wise female teacher (ZENO) |

### ✅ FIXED April 2026 — SEO/Hashtags Not Using seo.get_video_tags()

**Root cause:** `generate_reel.py` used hardcoded hashtag string in meta. `generate_analysis.py` used hardcoded `["Nifty", "Trading"]` tags. None were using `seo.get_video_tags()` from `human_touch.py`.

**Fix applied:**
- `generate_reel.py` now calls `seo.get_video_tags(mode=CONTENT_MODE, is_short=True)` and builds full SEO description with hashtags, stored in `meta_YYYYMMDD.json`
- `upload_youtube.py` reads title/description/tags directly from the meta JSON — no more hardcoded anything
- `generate_analysis.py` calls `seo.get_video_tags(mode=CONTENT_MODE, is_short=False)` and builds full SEO description
- All videos now have proper full descriptions with: insight text + website + Telegram + disclaimer + hashtags

**Rule going forward:** Tags always come from `seo.get_video_tags()`. Description is always built in the generator, not in the uploader.

### Facebook Group Posting ❌

**Root causes (check in order):**
1. `META_ACCESS_TOKEN` missing `publish_to_groups` scope
2. Bot account not **Admin** of the group
3. Group Settings → Advanced → "Allow content from apps" OFF
4. App not approved for Groups API by Meta

**Fix:** developers.facebook.com → App → Add `publish_to_groups` → regenerate token → update secret.
Token is auto-refreshed every 50 days by `token_refresh.yml` once scope is added.

### Instagram Auto-Post ⚠️

`INSTAGRAM_ACCOUNT_ID` is now added. If still failing:

```
https://graph.facebook.com/me/accounts?access_token=YOUR_META_TOKEN
```

Verify the numeric ID matches exactly. Upload chain: `upload_youtube.py` → `upload_facebook.py` → `upload_instagram.py` must run in order.

### YouTube Community Tab ⚠️

Community Tab requires **500+ subscribers** to be enabled. If below 500 subs, `generate_community_post.py` saves post text to `output/community_post_YYYYMMDD.txt` for manual posting without crashing.

### META\_ACCESS\_TOKEN Expiry — Automated ✅

`token_refresh.yml` runs every 50 days automatically. Refreshes token + updates GitHub Secret + sends Telegram alert.

---

## 13. Technical Standards

### The "Full Code" Rule

> AI assistants **must always provide the complete content** of any modified file. Partial snippets or diffs are strictly prohibited.

**Standard AI task prompt:**

```
Context: I am working on the ai360trading system. Refer to SYSTEM.md for architecture.
Task: [Your Task]
Note: Provide the full code for any file you modify.
```

### AI Client Usage Rule — No Exceptions

> **Never call AI APIs directly in generators.** Always use:

```python
from ai_client import ai, img_client
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang=LANG)
data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang=LANG)
```

### Human Touch Usage Rule — No Exceptions

> **Never use raw AI output.** Always pass through human\_touch:

```python
from human_touch import ht, seo
hook   = ht.get_hook(mode=CONTENT_MODE, lang=LANG)
clean  = ht.humanize(raw_script, lang=LANG)
tags   = seo.get_video_tags(mode=CONTENT_MODE, lang=LANG)
speed  = ht.get_tts_speed()  # pass to edge_tts rate param
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

| Voice ID | Gender | Used For |
| --- | --- | --- |
| `hi-IN-MadhurNeural` | Male | Short 2 — authoritative trade setups |
| `en-IN-NeerjaNeural` | Female | Short 3 — energetic global market pulse (Indian English — Hinglish-compatible) |
| `hi-IN-SwaraNeural` | Female | ZENO Reel, Morning Reel, Analysis, Education |
| `en-US-JennyNeural` | Female | English channel — all English content |
| `en-US-GuyNeural` | Male | English Short 2 alternative |

> **Rule:** Short 2, Short 3, and ZENO reel must always use THREE DISTINCT VOICES. Never assign the same voice to two different content types.

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
| Short 2, Short 3, Short 4, Morning Reel, ZENO Reel | 9:16 | YouTube Shorts / Reels / Instagram |

### SEO Tags Strategy

Every video includes both India-specific AND global tags via `seo.get_video_tags()`:
- India: `Nifty50`, `TradingIndia`, `StockMarketIndia`, `BankNifty`
- Global: `USStocks`, `UKInvesting`, `BrazilMarket`, `UAEInvesting`, `GlobalInvesting`
- Universal: `Finance`, `Investing`, `FinancialLiteracy`, `Shorts`

**Rule:** Tags ALWAYS come from `seo.get_video_tags()`. Never hardcode tag lists in generators or uploaders. Description is always built in the generator (with website + Telegram + disclaimer + hashtags), not in the uploader.

### Meta JSON Standard

Every generator must write a meta JSON file with at minimum:

```json
{
  "title": "Full SEO-optimised YouTube title",
  "description": "Full SEO description with website + Telegram + disclaimer + hashtags",
  "tags": ["tag1", "tag2", ...],
  "sentiment": "bullish/bearish/neutral",
  "content_mode": "market/weekend/holiday",
  "public_video_url": ""
}
```

`upload_youtube.py` reads `title`, `description`, `tags` from meta — it does NOT build its own.

---

## 14. Disney 3D Reel Roadmap

| Phase | Tool | Quality | Timeline | Status |
| --- | --- | --- | --- | --- |
| 1 (Now) | PIL + MoviePy + ZENO PNG | 2D animated slides | Current | ✅ Active |
| 2 | Gemini Veo API (free tier) | AI video clips | 3–6 months | Hooks in ai\_client.py |
| 3 | Stable Diffusion + AnimateDiff | 3D style frames | 6–12 months | Planned |
| 4 | Google Veo 2 / Sora (when free) | True Disney-style 3D | 12–18 months | Planned |

---

## 15. Full Data Flow

```
Market hours (Mon–Fri, 9:15 AM–3:30 PM IST)
└── main.yml (every 5 min)
    └── trading_bot.py v13.4
        └── get_sheets() → gspread → AlertLog + History + Nifty200
        └── get_market_regime() → Nifty CMP vs 20DMA → bullish/bearish
        └── Step A: WAITING→TRADED (entry alert → all 3 channels)
        └── Step B: Monitor TRADED (TSL update → Advance+Premium)
        └── Exit logic (TSL hit / target hit / hard loss)
        └── CE candidate flag in entry alert (bullish + ATR%>1.5%)
        └── History sheet append on exit
        └── T4 memory string updated each run

AppScript v13.3 (Google Sheets bound)
└── Nifty200 sheet scan (batched 60 rows per run)
└── 10-gate filter → bearish or bullish path
└── Conviction bonus + capital tier + trade mode
└── ATR% tiebreaker sort (min SL preference)
└── Write WAITING rows to AlertLog
└── Write _CAP, _MODE, _SEC keys to T4 memory
└── Bearish alert with top sector context → Telegram

7:00 AM daily
└── daily_reel.yml (morning job)
    └── generate_reel_morning.py → upload chain ✅

7:30 AM / 9:30 AM daily
└── daily-videos.yml
    └── generate_analysis.py → Part 1 → YouTube (uploads itself) ✅
    └── generate_education.py → Part 2 → YouTube (uploads itself) ✅

10:00 AM / 11:30 AM daily
└── daily-articles.yml
    └── generate_articles.py → 4 articles → GitHub Pages ✅ → Facebook ✅

11:30 AM / 1:30 PM daily
└── daily-shorts.yml
    └── generate_shorts.py → Short 2 (Madhur) + Short 3 (Neerja) → YouTube (uploads itself) ✅
    └── generate_community_post.py → Community Tab ✅

8:30 PM daily
└── daily_reel.yml (evening job)
    └── generate_reel.py → ZENO reel (renders only, writes meta with full SEO)
    └── upload_youtube.py → reads meta → YouTube upload ✅
    └── upload_facebook.py ✅
    └── upload_instagram.py ⚠️
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
| Instagram verify live | Test after `INSTAGRAM_ACCOUNT_ID` added | 🔴 High |
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

### Verify ai\_client fallback chain
In logs, look for:
```
[AI]   Using ai_client fallback chain: Groq→Gemini→Claude→OpenAI→Templates
✅ AI generated via groq
```

### Verify human\_touch is active
In logs, look for:
```
✅ ZENO script ready — emotion: thinking | title: CONTROL YOUR FEAR
✅ Community post generated via groq (112 chars)
```

### Verify no duplicate uploads
In logs, check that each video appears only ONCE in upload output:
- Analysis: uploaded in `generate_analysis.py` logs only
- Shorts: uploaded in `generate_shorts.py` logs only (Short 2 + Short 3)
- ZENO reel: uploaded in `upload_youtube.py` logs only

### Verify distinct voices
- Short 2 log: `(Madhur voice)` or `hi-IN-MadhurNeural`
- Short 3 log: `(Neerja voice)` or `en-IN-NeerjaNeural`
- ZENO reel log: `hi-IN-SwaraNeural`

### Verify SEO meta
Check `output/meta_YYYYMMDD.json` after generate\_reel.py runs — should contain:
- `"title"`: full YouTube title
- `"description"`: multi-line with website + Telegram + disclaimer + hashtags
- `"tags"`: array of 15-20 tags from seo.get_video_tags()

### Force each content mode
```
workflow_dispatch → content_mode = market   # weekday content
workflow_dispatch → content_mode = weekend  # weekend content
workflow_dispatch → content_mode = holiday  # holiday content
```

### Automation on/off switch
Google Sheet → AlertLog → cell T2 → set "YES" to enable, anything else to disable.

---

*Documentation maintained by AI360Trading automation.*
*Full audit: April 16, 2026 — Claude Sonnet 4.6*
*Phase 1 complete: ai\_client.py, human\_touch.py, token\_refresh.py, generate\_reel\_morning.py*
*Phase 2 complete: generate\_articles.py, generate\_analysis.py, generate\_education.py, generate\_reel.py, generate\_shorts.py, generate\_community\_post.py*
*April 2026 fixes: duplicate-upload fix, voice differentiation (Short 3 → Neerja), full SEO meta system*
*Trading bot: AppScript v13.3 + Python v13.4 — paper trading, Google Sheets, Dhan Phase 4*
*Phase 3 remaining: generate\_english.py, upload\_youtube\_english.py, Facebook Group fix, Instagram verify*
*Phase 4 planned: Dhan live trading after backtest validation*
*Update this file whenever architecture, secrets, platform status, or file logic changes.*
