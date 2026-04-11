# AI360Trading — Master System Documentation

**Last Updated:** April 11, 2026 — Trading Bot v13.4 + AppScript v13.3
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
| YouTube English | 🔄 Building | Phase 3 — English scripts from scratch (not translated) |
| YouTube Shorts | ✅ Auto | Short 2 + Short 3 working |
| YouTube Community Posts | ✅ Built | generate\_community\_post.py — 12:00 PM daily |
| YouTube Reels | ✅ Auto | ZENO reel (8:30 PM) working |
| YouTube Morning Reel | ✅ Auto | 7:00 AM reel (generate\_reel\_morning.py) working |
| Facebook Page | ✅ Auto | Reels + article shares working. Group posting = manual for now. |
| Facebook Group | 🤚 Manual | Owner posts manually. Auto-posting deferred to future phase. |
| Instagram | 🤚 Manual | Owner posts manually. Auto-posting deferred to future phase. |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | Signal alerts to all 3 channels (paper trading — followers take manual entry) |

> **Manual posting note:** Facebook Group and Instagram are intentionally manual until automation is re-prioritised.
> `upload_facebook.py` posts to FB Page only. `upload_instagram.py` is not called in any workflow until re-enabled.

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
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + FB Page | ✅ |
| 2 | Part 1 Video (16:9) | 7:30 AM weekday / 9:30 AM weekend | YouTube | ✅ |
| 3 | Part 2 Video (16:9) | 7:30 AM (same workflow) | YouTube | ✅ |
| 4 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | ✅ |
| 5 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 6 | Short 4 English (9:16) | 11:30 AM (same workflow) | YouTube English Shorts | 🔄 Phase 3 |
| 7 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook Page | ✅ |
| 8 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB Page | ✅ |
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

**Failure alerting (to be added — see Section 20, Item 4):** All workflows should send a Telegram alert on failure. Not yet implemented.

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
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Swara) | ai\_client, human\_touch, Edge-TTS | ✅ Phase 2 |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ai\_client, human\_touch, MoviePy | ✅ Phase 2 |
| `generate_reel_morning.py` | Morning reel (7:00 AM) — day/country aware | ai\_client, human\_touch, MoviePy | ✅ |
| `generate_analysis.py` | 8-slide market analysis video (Part 1) | ai\_client, human\_touch, MoviePy | ✅ Phase 2 |
| `generate_education.py` | Educational deep-dive video (Part 2) | ai\_client, human\_touch, content\_calendar | ✅ Phase 2 |
| `generate_articles.py` | 4 SEO articles daily → Jekyll \_posts | ai\_client, human\_touch, Google Indexing | ✅ Phase 2 |
| `generate_community_post.py` | YouTube daily community text post — 12:00 PM | ai\_client, human\_touch | ✅ Phase 2 |

> ⚠️ **Verify:** `generate_community_post.py` must exist in repo root. If missing, `daily-shorts.yml` will fail silently. Check and add if absent — see Section 20, Item 3.

### Upload & Distribution

| File | Role | Status |
| --- | --- | --- |
| `upload_youtube.py` | Uploads reel; saves `youtube_video_id` + `public_video_url` to meta | ✅ |
| `upload_youtube_english.py` | Uploads to English channel (separate credentials) | 🔄 Phase 3 |
| `upload_facebook.py` | Uploads reel to FB Page + posts articles to FB Page only. Group posting removed. | ✅ |
| `upload_instagram.py` | Built but NOT called in any workflow. Manual posting only until re-enabled. | 🤚 Manual |

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
**T4** = memory string

> ⚠️ **Known fragility:** T4 currently stores raw `key=value,key=value` CSV in a single cell. This breaks if a value contains a comma or equals sign. Migration to JSON planned — see Section 20, Item 2.

**Current T4 memory keys per stock:**
- `{sym}_TSL` — current trailing SL price
- `{sym}_MAX` — max price seen since entry
- `{sym}_ATR` — ATR at entry
- `{sym}_CAP` — capital tier (7000/10000/13000)
- `{sym}_MODE` — trade mode (VCP/MOM/STD)
- `{sym}_SEC` — sector name

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

* Leader\_Type = "Sector Leader"
* AF ≥ 5 (RS≥2.5 with sector tailwind)
* Master\_Score ≥ 22
* FII signal ≠ "FII CAUTION" or "FII SELLING"

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

* ₹13,000 — MasterScore≥28 AND AF≥10 (high conviction)
* ₹10,000 — MasterScore≥22 OR Accumulation Zone (medium conviction)
* ₹7,000 — standard

**Trade modes (stored as \_MODE in T4 memory):**

* VCP — AB<0.04 + pre-breakout stage
* MOM — Strong Bull + RS≥6
* STD — everything else (default in bear market)

**Sort order:** finalScore DESC, then ATR% ASC as tiebreaker within ±2 score points (minimum SL preference).

### Python Bot v13.4 — Key Logic

**Circuit breaker (to be added — see Section 20, Item 1):** No automatic halt exists today. T2="YES/NO" is the only stop.

**TSL Parameters (mode-aware):**

```python
TSL_PARAMS = {
    "VCP": { "breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0 },
    "MOM": { "breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0 },
    "STD": { "breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0 },
}
```

STD trail widened in v13.3 (6→10, atr\_mult 1.5→2.5) to support full-ride vision on swing trades.

**TSL progression (STD example):**

* Gain < 2% → hold initial SL
* Gain 2–4% → move to breakeven
* Gain 4–10% → lock at entry +2%
* Gain > 10% → ATR trail (2.5× ATR below CMP)
* Gain > 8% gap-up → lock 50% of gap

**Daily message schedule:**

* 08:45–09:15 → Good Morning (open trades P/L + waiting count + sector context)
* 09:15–15:30 → Market hours (entry alerts, TSL updates, exit alerts)
* 12:28–12:38 → Mid-day pulse
* 15:15–15:45 → Market close summary

**Telegram channels:**

* Basic (free) → market mood, signal closed result only
* Advance (₹499/mo) → full entry/exit details, TSL updates, mid-day pulse
* Premium (bundle) → same as Advance + options CE candidate flag

**CE candidate flag (v13.4 — informational only):**
Fires when market is bullish AND stock ATR% > 1.5%. Shows in Advance + Premium entry alerts only. Uses existing ATR14 (col AC) and CMP — no new data needed. Currently informational — Dhan API connection needed for live CE execution.

```
ATR% < 1.5%    → no flag (premium decay risk)
ATR% 1.5–2.5%  → normal mover: target +65%, SL -40% on premium
ATR% > 2.5%    → fast mover: target +50%, SL -35% on premium
```

**Hard exit rules:**

* Loss > 5% → hard loss exit (immediate, no min-hold check)
* Min hold: 2 days swing, 3 days positional (prevents TSL whipsaw on day 1)
* 5 trading day cooldown after exit before same stock re-enters

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

Scripts must run in this exact order. Each one feeds data to the next:

### Evening ZENO Reel (8:30 PM)

```
generate_reel.py
    └── output/reel_YYYYMMDD.mp4
    └── output/meta_YYYYMMDD.json  ← created here (public_video_url = "")

upload_youtube.py
    └── Uploads reel to YouTube
    └── Writes to meta → youtube_video_id, youtube_video_url, public_video_url

upload_facebook.py
    └── Uploads reel to Facebook Page only
    └── Posts articles from RSS feed to Page
    └── NOTE: Group posting removed — manual only
    └── NOTE: public_video_url in meta is NOT overwritten (FB URL no longer needed for Instagram)
```

> **Instagram:** `upload_instagram.py` is NOT called in this chain. Post manually from the downloaded reel artifact.
> GitHub Actions → Run → Artifacts → download → post to Instagram manually.

### Morning Reel (7:00 AM)

```
generate_reel_morning.py
    └── output/morning_reel_YYYYMMDD.mp4
    └── output/morning_reel_meta_YYYYMMDD.json

upload_youtube.py (morning mode)
upload_facebook.py (morning mode — FB Page only)
```

### Daily Videos (7:30 AM)

```
generate_analysis.py
    └── output/analysis_video.mp4
    └── output/analysis_video_id.txt       ← Part 1 ID for Part 2 linking
    └── output/analysis_meta_YYYYMMDD.json

generate_education.py
    └── Reads analysis_video_id.txt → links Part 1 in description
    └── output/education_video.mp4
    └── output/education_video_id.txt
    └── output/education_meta_YYYYMMDD.json
    └── Updates Part 1 YouTube description with Part 2 URL
```

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

> Dhan integration planned for Phase 4 after backtest validation. Needs full spec before connecting — see Section 20, Item 9.

### Social Platforms

| Secret | Purpose | Status |
| --- | --- | --- |
| `META_ACCESS_TOKEN` | Facebook Page API | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` | Facebook App ID — needed for auto token refresh | ✅ Added |
| `META_APP_SECRET` | Facebook App Secret — needed for auto token refresh | ✅ Added |
| `FACEBOOK_PAGE_ID` | Target Facebook Page ID | ✅ |
| `FACEBOOK_GROUP_ID` | Facebook Group ID — kept for future use | ✅ (not used currently) |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business/Creator numeric ID — kept for future use | ✅ (not used currently) |
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

## 12. Known Issues & Current Status

### Facebook Group Posting — Manual (by choice)
Auto-posting to Facebook Group is intentionally deferred. Owner posts manually. `upload_facebook.py` posts to FB Page only. When ready to re-enable, see Section 20 for the token scope fix steps.

### Instagram — Manual (by choice)
Auto-posting to Instagram is intentionally deferred. Owner posts manually using downloaded artifacts from GitHub Actions runs. `upload_instagram.py` exists but is not called in any workflow.

### META\_ACCESS\_TOKEN Expiry — Automated ✅
`token_refresh.yml` runs every 50 days automatically. Refreshes token + updates GitHub Secret + sends Telegram alert. Requires `META_APP_ID` and `META_APP_SECRET` (both added).

### YouTube Community Tab ⚠️
Community Tab requires **500+ subscribers** to be enabled.
If channel is below 500 subs, `generate_community_post.py` will:
* Print a clear warning explaining why
* Save post text to `output/community_post_YYYYMMDD.txt` for manual posting
* Not crash the workflow

**Enable:** YouTube Studio → Customization → Layout → Community Tab → ON

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

> ⚠️ **Pin all packages** — "Latest" on CI can silently break on a new release. Pinning requirements.txt is a pending improvement — see Section 20, Item 7.

### Voice Assignments

| Voice ID | Gender | Used For |
| --- | --- | --- |
| `hi-IN-MadhurNeural` | Male | Short 2 — authoritative trade setups |
| `hi-IN-SwaraNeural` | Female | Short 3, ZENO Reel, Morning Reel, Analysis, Education |
| `en-US-JennyNeural` | Female | English channel — all English content |
| `en-US-GuyNeural` | Male | English Short 2 alternative |

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

* India: `Nifty50`, `TradingIndia`, `StockMarketIndia`, `BankNifty`
* Global: `USStocks`, `UKInvesting`, `BrazilMarket`, `UAEInvesting`, `GlobalInvesting`
* Universal: `Finance`, `Investing`, `FinancialLiteracy`, `Shorts`

---

## 14. Disney 3D Reel Roadmap

| Phase | Tool | Quality | Timeline | Status |
| --- | --- | --- | --- | --- |
| 1 (Now) | PIL + MoviePy + ZENO PNG | 2D animated slides | Current | ✅ Active |
| 2 | Gemini Veo API (free tier) | AI video clips | 3–6 months | Hooks in ai\_client.py |
| 3 | Stable Diffusion + AnimateDiff | 3D style frames | 6–12 months | Planned |
| 4 | Google Veo 2 / Sora (when free) | True Disney-style 3D | 12–18 months | Planned |

> `img_client` in `ai_client.py` is the upgrade hook — swap in Phase 2 generation with zero changes to generators.

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

AppScript v13.3 (Google Sheets bound — triggered manually or on schedule)
└── Nifty200 sheet scan (batched 60 rows per run)
└── 10-gate filter → bearish or bullish path
└── Conviction bonus + capital tier + trade mode
└── ATR% tiebreaker sort (min SL preference)
└── Write WAITING rows to AlertLog
└── Write _CAP, _MODE, _SEC keys to T4 memory
└── Bearish alert with top sector context → Telegram

7:00 AM daily
└── daily_reel.yml (morning job)
    └── generate_reel_morning.py → upload_youtube.py → upload_facebook.py (Page only) ✅

7:30 AM / 9:30 AM daily
└── daily-videos.yml
    └── generate_analysis.py → Part 1 → YouTube ✅
    └── generate_education.py → Part 2 → YouTube ✅

10:00 AM / 11:30 AM daily
└── daily-articles.yml
    └── generate_articles.py → 4 articles → GitHub Pages ✅ → Facebook Page ✅

11:30 AM / 1:30 PM daily
└── daily-shorts.yml
    └── generate_shorts.py → Short 2 + Short 3 → YouTube ✅
    └── generate_community_post.py → Community Tab ✅

8:30 PM daily
└── daily_reel.yml (evening job)
    └── generate_reel.py → ZENO reel
    └── upload_youtube.py ✅ → upload_facebook.py (Page only) ✅
```

---

## 16. Website

* **URL:** `ai360trading.in`
* **Hosting:** GitHub Pages (Jekyll, `master` branch `_posts/`)
* **Publishing:** Auto-commit by `daily-articles.yml`
* **SEO Indexing:** Instant via `GCP_SERVICE_ACCOUNT_JSON`
* **Revenue:** Google AdSense (USA/UK English readers = highest CPM)
* **Content pillars:** Stock Market, Bitcoin/Crypto, Personal Finance, AI Trading
* **Market coverage:** India (Nifty50, BankNifty), USA (S&P500, NASDAQ), UK (FTSE100), Brazil (IBOVESPA), Crypto (BTC, ETH)

> **SEO improvement (pending):** Internal linking between articles is not yet implemented. See Section 20, Item 5.

---

## 17. Social Media Links

| Platform | Handle/Link |
| --- | --- |
| 🌐 Website | ai360trading.in |
| 📣 Telegram (Free) | @ai360trading |
| 📣 Telegram (Advance) | ai360trading\_Advance — ₹499/month |
| 📣 Telegram (Premium) | ai360trading\_Premium — bundle |
| ▶️ YouTube | @ai360trading |
| 📸 Instagram | @ai360trading (manual posting) |
| 👥 Facebook Group | facebook.com/groups/ai360trading (manual posting) |
| 📘 Facebook Page | facebook.com/ai360trading (auto) |
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
| English channel shorts (written from scratch, not translated) | `generate_english.py` | 🟡 Medium |
| English channel upload | `upload_youtube_english.py` | 🟡 Medium |
| Instagram auto-post re-enable | `upload_instagram.py` + workflow | 🔵 Deferred |
| Facebook Group auto-post re-enable | `upload_facebook.py` scope fix | 🔵 Deferred |
| Disney 3D reel upgrade | `ai_client.py` img\_client Phase 2 | 🔵 Future |

### Phase 4 📋 Planned — Dhan Live Trading

| Item | Dependency | Notes |
| --- | --- | --- |
| Backtest validation | 30–40 live paper trades, win rate >35% | Currently running paper trades |
| Dhan API connection | `DHAN_API_KEY` secrets already added | Needs full spec first — see Section 20, Item 9 |
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
If Groq is down: `⚠️ groq failed` → `✅ AI generated via gemini`

### Verify human\_touch is active
In logs:
```
✅ ZENO script ready — emotion: thinking | via groq
✅ Community post generated via groq (112 chars)
```

### Verify trading bot
In logs (`main.yml`):
```
[REGIME] Nifty CMP ₹22679 vs 20DMA ₹23547 → BEARISH
[INFO] Active trades: 4/5
[TSL] NSE:ONGC [STD]: ₹280.60→₹285.20
[DONE] 15:20:01 IST | mem=842 chars
```

### Verify AppScript
Open Google Sheet → AI360 TRADING menu → MANUAL SYNC → check Logger output:
```
[REGIME] CMP=22679 20DMA=23547 Bullish=false
[CAND] NSE:ADANIPOWER | Score=24 | ATR%=2.1 | ₹10000 | STD | AF=8.2 | Qty=64
[DONE] Traded=4 | Waiting=3 | Bullish=false
```

### Force each content mode
```
workflow_dispatch → content_mode = market   # weekday content
workflow_dispatch → content_mode = weekend  # weekend content
workflow_dispatch → content_mode = holiday  # holiday content
```

### Automation on/off switch
Google Sheet → AlertLog → cell T2 → set "YES" to enable, anything else to disable.

---

## 20. Improvement Backlog

This section tracks all planned improvements. Work through these one by one. Each item has a clear spec so any AI assistant can implement it immediately.

---

### Item 1 — Trading Bot Circuit Breaker
**Priority:** 🔴 High
**File:** `trading_bot.py`
**Status:** ⬜ Not started

**Problem:** No automatic halt exists. If Sheets is unreachable, the bot crashes mid-run and can leave WAITING rows stuck. No guard against running too many signals in one cycle.

**What to build:**
Add these checks at the TOP of `main()` before any sheet operations:

```python
# 1. Sheets connectivity check
try:
    sheet = get_sheets()
except Exception as e:
    send_telegram(TELEGRAM_CHAT_ID, f"⚠️ Bot startup failed — Sheets unreachable: {e}")
    sys.exit(1)

# 2. Max signals per run guard (prevents runaway on data anomaly)
MAX_NEW_SIGNALS_PER_RUN = 3
new_signals_this_run = 0
# increment new_signals_this_run each time a WAITING→TRADED transition fires
# if new_signals_this_run >= MAX_NEW_SIGNALS_PER_RUN: break out of loop, log warning

# 3. T2 switch check (already exists — confirm it runs before any trade logic)
```

Also add at end of `main()`:
```python
# Log run completion with memory size for debugging
print(f"[DONE] {ist_now()} | mem={len(t4_string)} chars | signals={new_signals_this_run}")
```

---

### Item 2 — T4 Memory: Migrate from CSV String to JSON
**Priority:** 🟡 Medium-High
**Files:** `trading_bot.py` (Python read/write) + AppScript (Google Sheets bound script)
**Status:** ⬜ Not started

**Problem:** T4 stores `ONGC_TSL=285.20,ONGC_MAX=291.00,...` as plain text. A symbol containing a comma (none currently, but possible) or a malformed write corrupts ALL memory for that row. JSON is safer and easier to debug.

**Migration plan:**

In `trading_bot.py`, replace the T4 read/write helpers:
```python
# OLD read
def read_t4(t4_string):
    mem = {}
    for pair in t4_string.split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            mem[k.strip()] = v.strip()
    return mem

# NEW read (handles both old CSV format and new JSON — safe migration)
def read_t4(t4_string):
    t4_string = t4_string.strip()
    if t4_string.startswith("{"):
        try:
            return json.loads(t4_string)
        except json.JSONDecodeError:
            return {}
    # fallback: parse old CSV format
    mem = {}
    for pair in t4_string.split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            mem[k.strip()] = v.strip()
    return mem

# NEW write
def write_t4(mem_dict):
    return json.dumps(mem_dict, separators=(',', ':'))
```

In AppScript, replace T4 write:
```javascript
// OLD
sheet.getRange("T4").setValue(memoryString);  // "ONGC_TSL=285,ONGC_MAX=291"

// NEW
sheet.getRange("T4").setValue(JSON.stringify(memoryObj));
```

**Rollout:** Deploy Python side first (with CSV fallback). Then update AppScript. No data loss — old CSV is still readable during transition.

---

### Item 3 — Verify generate\_community\_post.py Exists
**Priority:** 🔴 High (workflow will fail if missing)
**File:** `generate_community_post.py`
**Status:** ⬜ Not verified

**Problem:** SYSTEM.md lists this file as ✅ complete but it does not appear in the visible repo file listing. If it's missing, `daily-shorts.yml` will throw an ImportError or FileNotFoundError at runtime.

**Steps:**
1. Check repo root: does `generate_community_post.py` exist?
2. If missing: create it. It should follow the same pattern as other generators:
   - Import `ai_client`, `human_touch`, `indian_holidays`
   - Read `CONTENT_MODE` from environment
   - Generate a short community post text (100–200 chars) using `ai.generate()`
   - Pass through `ht.humanize()`
   - If YouTube Community Tab is unavailable (sub count check or API error): save to `output/community_post_YYYYMMDD.txt` and exit 0
   - Otherwise: post via YouTube Data API community post endpoint
3. If it exists but is not in root: move it to root or fix the import path in the workflow.

---

### Item 4 — Workflow Failure Alerts via Telegram
**Priority:** 🟡 High
**Files:** All `.github/workflows/*.yml` files
**Status:** ⬜ Not started

**Problem:** When a workflow fails at 3 AM, there is no notification. You only notice when content is missing for that day.

**What to add to every workflow YAML** — add this as the last job step in each workflow (runs even if earlier steps fail):

```yaml
- name: Notify on failure
  if: failure()
  env:
    TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
  run: |
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="${TELEGRAM_CHAT_ID}" \
      -d text="⚠️ GitHub Actions FAILED%0AWorkflow: ${{ github.workflow }}%0AJob: ${{ github.job }}%0ARun: ${{ github.run_id }}%0ACheck: https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}"
```

**Workflows to update:**
- `daily-videos.yml`
- `daily-shorts.yml`
- `daily_reel.yml`
- `daily-articles.yml`
- `main.yml`
- `token_refresh.yml`

---

### Item 5 — Internal Linking in Articles
**Priority:** 🟡 Medium
**File:** `generate_articles.py`
**Status:** ⬜ Not started

**Problem:** Each of the 4 daily articles is a standalone piece with no links to previous posts. Internal linking is one of the strongest on-page SEO signals for Google indexing.

**What to add in `generate_articles.py`:**

```python
import os, glob

def get_recent_post_links(posts_dir="_posts", count=5):
    """Return list of (title, url_slug) for the most recent posts."""
    files = sorted(glob.glob(f"{posts_dir}/*.md"), reverse=True)[:count]
    links = []
    for f in files:
        with open(f) as fp:
            content = fp.read()
        # Extract title from frontmatter
        for line in content.split("\n"):
            if line.startswith("title:"):
                title = line.replace("title:", "").strip().strip('"')
                # Build URL from filename: 2026-04-10-nifty-analysis.md → /2026/04/10/nifty-analysis/
                base = os.path.basename(f).replace(".md", "")
                parts = base.split("-", 3)
                slug = f"/{parts[0]}/{parts[1]}/{parts[2]}/{parts[3]}/"
                links.append((title, slug))
                break
    return links

# Then pass recent_links into the article prompt:
recent = get_recent_post_links()
link_context = "\n".join([f"- [{t}]({u})" for t, u in recent])
prompt = f"""
...your existing prompt...

At the end of the article body, naturally include 1-2 internal links to these recent posts where relevant:
{link_context}
Use markdown link format: [anchor text](url)
"""
```

---

### Item 6 — Article Deduplication (Title Hash Check)
**Priority:** 🟡 Medium
**File:** `generate_articles.py`
**Status:** ⬜ Not started

**Problem:** The same topic can be generated multiple times in the same week via topic rotation, resulting in near-duplicate headlines that hurt SEO.

**What to add:**

```python
import hashlib

def get_recent_titles(posts_dir="_posts", days=7):
    """Return set of normalised recent post titles for deduplication."""
    cutoff = datetime.now() - timedelta(days=days)
    titles = set()
    for f in glob.glob(f"{posts_dir}/*.md"):
        # Parse date from filename
        base = os.path.basename(f)
        try:
            date = datetime.strptime(base[:10], "%Y-%m-%d")
        except ValueError:
            continue
        if date >= cutoff:
            with open(f) as fp:
                for line in fp.read().split("\n"):
                    if line.startswith("title:"):
                        title = line.replace("title:", "").strip().strip('"').lower()
                        titles.add(title)
    return titles

# Add to article generation prompt:
recent_titles = get_recent_titles()
prompt = f"""
...existing prompt...

IMPORTANT: Do NOT generate articles with titles similar to these recent ones:
{chr(10).join(recent_titles)}
Pick a fresh angle or different market/topic.
"""
```

---

### Item 7 — Pin All requirements.txt Packages
**Priority:** 🟡 Medium
**File:** `requirements.txt`
**Status:** ⬜ Not started

**Problem:** Most packages in `requirements.txt` are unpinned ("Latest"). A new release of `gspread`, `anthropic`, or `google-generativeai` can silently break production on the next GitHub Actions runner.

**Steps:**
1. Run `pip freeze` locally (or in a test Action run) to get exact current versions.
2. Replace every unpinned line in `requirements.txt` with a pinned version.
3. Keep existing pins for `Pillow`, `imageio`, `moviepy`.
4. Example result:
```
Pillow>=10.3.0
imageio==2.9.0
moviepy==1.0.3
yfinance==0.2.38
gspread==6.1.2
oauth2client==4.1.3
anthropic==0.25.0
openai==1.30.1
google-generativeai==0.5.4
groq==0.7.0
pytz==2024.1
PyNaCl==1.5.0
edge-tts==6.1.9
requests==2.32.3
python-telegram-bot==21.3
```
5. Add a note at top of file: `# Pinned on YYYY-MM-DD — update quarterly or when upgrading a package`

---

### Item 8 — Add DRY\_RUN Mode to All Generators
**Priority:** 🟢 Nice-to-have
**Files:** All `generate_*.py` files + `upload_*.py` files
**Status:** ⬜ Not started

**Problem:** Every script needs live secrets to run. You cannot test prompt changes locally without uploading to YouTube or posting to Telegram.

**What to add:**

In each generator/uploader, read at the top:
```python
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
```

In upload functions:
```python
if DRY_RUN:
    print(f"[DRY RUN] Would upload to YouTube: {video_path}")
    print(f"[DRY RUN] Title: {title}")
    print(f"[DRY RUN] Description: {description[:200]}")
    return "dry_run_video_id"
```

In Telegram send functions:
```python
if DRY_RUN:
    print(f"[DRY RUN] Telegram → {channel}: {message[:200]}")
    return
```

**Usage:** `DRY_RUN=true python generate_reel.py` — generates the full video and logs everything, but makes no external calls.

---

### Item 9 — Dhan Live Trading Integration Spec
**Priority:** 🔵 Phase 4 — do not start until 30+ paper trades validated
**File:** New file `dhan_client.py`
**Status:** ⬜ Not started — needs spec first

**Pre-conditions before writing any code:**
- [ ] 30–40 paper trades completed with win rate >35%
- [ ] Max drawdown in paper trading <15%
- [ ] AppScript + Python bot running stably with zero crashes for 2 weeks

**Design decisions needed before starting:**
1. Order type: Market or Limit? (Limit is safer — needs slippage buffer logic)
2. Lot size: Fixed quantity or % of capital tier?
3. Position sizing check: Verify available margin before placing order
4. Live vs paper flag: Single env variable `LIVE_TRADING=true` that defaults to false
5. Error handling: If order placement fails, send Telegram alert and do NOT mark as TRADED in sheet

**Dhan API endpoints needed:**
- `POST /orders` — place order
- `GET /orders/{order_id}` — verify fill
- `GET /portfolio/positions` — check open positions
- `GET /funds` — check available margin

**Implementation approach:**
```python
# dhan_client.py
class DhanClient:
    def place_order(self, symbol, qty, order_type, side):
        if not LIVE_TRADING:
            print(f"[PAPER] {side} {qty} {symbol}")
            return {"status": "paper", "order_id": "PAPER_001"}
        # actual Dhan API call here
```

---

### Item 10 — English Channel Strategy Decision
**Priority:** 🟡 Phase 3
**File:** New `generate_english.py`
**Status:** ⬜ Decision needed first

**Decision required:** Two approaches are possible:

**Option A — Auto-translate Hindi scripts:**
- Fast to build (1–2 days)
- Lower quality — financial terms translate poorly
- CPM impact: moderate (translated content gets lower engagement → lower CPM)

**Option B — Generate English scripts from scratch using same market data:**
- Same market data (yfinance, Google Trends) → separate English prompt
- Separate topic angle (US/UK audience focus, not India-centric)
- 3–5× better CPM for USA/UK audience
- 3–4 days to build properly
- **Recommended approach**

**When ready to build (Option B):**
- New file: `generate_english.py` — same structure as `generate_shorts.py` but English prompt
- Uses `en-US-JennyNeural` voice
- Content focus: S&P 500, FTSE 100, Bitcoin — not Nifty
- Calls same `ai.generate(prompt, content_mode=CONTENT_MODE, lang="en")`
- Uploads via `upload_youtube_english.py` using `YOUTUBE_CREDENTIALS_EN`

---

*Documentation maintained by AI360Trading automation.*
*Last audit: April 11, 2026 — Updated by owner with improvement backlog added*
*Phase 1 complete: ai\_client.py, human\_touch.py, token\_refresh.py, generate\_reel\_morning.py*
*Phase 2 complete: generate\_articles.py, generate\_analysis.py, generate\_education.py, generate\_reel.py, generate\_shorts.py, generate\_community\_post.py*
*Trading bot: AppScript v13.3 + Python v13.4 — paper trading, Google Sheets, Dhan Phase 4*
*Phase 3 remaining: generate\_english.py, upload\_youtube\_english.py*
*Phase 4 planned: Dhan live trading after backtest validation*
*FB Group + Instagram: Manual posting by owner until re-prioritised*
*Update this file whenever architecture, secrets, platform status, or file logic changes.*
