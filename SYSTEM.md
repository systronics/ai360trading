# AI360Trading — Master System Documentation

**Last Updated:** May 2026 — Verified against actual code + all 9 workflows
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Mostly Complete (see gaps) | Phase 3 🔄 In Progress | Phase 4 📋 Planned
**Primary Audience:** Bilingual Hindi + English — Indian retail traders + global investors

> ⚠️ **Read this file completely before making ANY changes.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT).
> All facts here are verified against actual code. Do NOT assume SYSTEM.md is correct — always read the actual file before editing it.

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

---

## 2. Platform Status (Verified May 2026)

| Platform | Status | Notes |
|---|---|---|
| YouTube Hindi | ✅ Auto | Analysis + Education + Shorts + Reels working |
| YouTube English | 🔄 Building | Phase 3 — separate channel, credentials added |
| YouTube Shorts | ✅ Auto | Short 2 (Madhur) + Short 3 (Neerja) working |
| YouTube Community Posts | ✅ Built | generate_community_post.py — 12:00 PM daily |
| YouTube ZENO Reel | ✅ Auto | 8:30 PM daily (generate_reel.py) |
| YouTube Morning Reel | ✅ Auto | 7:00 AM daily (generate_reel_morning.py) |
| YouTube Kids (HerooQuest) | ✅ Auto | kids-daily.yml — 8:00 AM daily |
| Facebook Page | ✅ Auto | Posts, reels, article shares working |
| Facebook Group | ❌ Permanently Removed | Requires Meta App Review, zero ad revenue — not worth pursuing |
| Instagram | ❌ API Removed | Manual post only — download artifact from GitHub Actions, post from phone |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | Signal alerts to all 3 channels (paper trading) |

> **Instagram and Facebook Group are permanently removed from all workflows. Do not add them back.**
> Instagram: Download video artifact from GitHub Actions → post manually from phone.

---

## 3. Content Mode System

Mode is **auto-detected** by `indian_holidays.py` at the start of every workflow and written to `$GITHUB_ENV`. All scripts read `CONTENT_MODE` environment variable.

| Mode | When | Content Strategy |
|---|---|---|
| `market` | Mon–Fri (excluding Indian holidays) | Live Nifty50/Global data, trade setups, signals |
| `weekend` | Saturday–Sunday | Educational, wealth-building, global audience focus |
| `holiday` | Indian Market Holidays | Motivational, "Market band hai par seekhna chalu", holiday name shown |

**Detection logic:** `indian_holidays.py` → NSE API (primary) → hardcoded fallback dates
**`HOLIDAY_NAME` env var** is written alongside `CONTENT_MODE` when mode is `holiday`.

---

## 4. Daily Content Output (Fully Automated)

| # | Content | Time (IST) | Workflow | Status |
|---|---|---|---|---|
| 1 | Morning Reel (9:16) | 7:00 AM | daily-morning-reel.yml | ✅ |
| 2 | Part 1 Analysis (16:9) | 7:30 AM weekday / 9:30 AM weekend | daily-videos.yml | ✅ |
| 3 | Part 2 Education (16:9, 10+ min) | 7:30 AM (same workflow) | daily-videos.yml | ✅ |
| 4 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | daily-articles.yml | ✅ |
| 5 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | daily-shorts.yml | ✅ |
| 6 | Short 3 English (9:16) | 11:30 AM (same workflow) | daily-shorts.yml | ✅ |
| 7 | ZENO Reel (9:16) | 8:30 PM | daily_reel.yml | ✅ |
| 8 | Kids Video (HerooQuest) | 8:00 AM | kids-daily.yml | ✅ |
| 9 | YouTube Community Post | 12:00 PM | daily-shorts.yml (same run) | ✅ |
| **Total** | **~12 pieces/day** | — | — | — |

---

## 5. GitHub Actions Workflows — Verified

| File | Trigger (IST) | Purpose | Mode-Aware |
|---|---|---|---|
| `trading_bot.yml` | Every 5 min, 08:15–16:29, Mon–Fri | `trading_bot.py` — Nifty200 signals | ✅ (bot handles internally) |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 (analysis) + Part 2 (education) | ✅ |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 + Community Post | ✅ |
| `daily_reel.yml` | 8:30 PM daily | ZENO Reel → YouTube + Facebook | ✅ |
| `daily-morning-reel.yml` | 7:00 AM daily | Morning Reel → YouTube + Facebook | ✅ |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages + Facebook | ✅ |
| `kids-daily.yml` | 8:00 AM daily | HerooQuest kids video → YouTube + Facebook Kids Page | N/A |
| `token_refresh.yml` | 1st + 20th of every month | Auto META token refresh (main + kids) | N/A |
| `keepalive.yml` | 11:59 PM IST Sun–Thu | Prevents GitHub disabling inactive workflows | N/A |

**Key facts verified from workflow files:**
- `push` trigger is REMOVED from trading_bot.yml — was causing midnight Telegram messages on every commit
- Facebook Group is removed from ALL workflows permanently
- Instagram is removed from ALL workflows permanently — artifact saved for manual post
- `daily-videos.yml` has a duration check — fails if education video is under 8 minutes (mid-roll ad threshold)
- Kids workflow uses separate secrets: `YOUTUBE_CREDENTIALS_KIDS`, `META_ACCESS_TOKEN_KIDS`, `FACEBOOK_KIDS_PAGE_ID`
- `token_refresh.yml` refreshes BOTH `META_ACCESS_TOKEN` and `META_ACCESS_TOKEN_KIDS`

---

## 6. Complete File Map

### Core Infrastructure

| File | Role | Status |
|---|---|---|
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates fallback | ✅ |
| `human_touch.py` | Anti-AI-penalty layer — 50+ hooks, personal phrases, TTS variation, SEO tags | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update + Telegram alert | ✅ |
| `indian_holidays.py` | Mode detection — NSE API + fallback; shared by ALL workflows | ✅ |
| `content_calendar.py` | Rotates topics: Options, Technical Analysis, Psychology | ✅ |

### Content Generators

| File | Role | Voice | Format | AI Client? | human_touch? | Status |
|---|---|---|---|---|---|---|
| `generate_analysis.py` | 8-slide market analysis video (Part 1) | Swara | 16:9 | ❌ Direct Groq | ❌ | ⚠️ Needs upgrade |
| `generate_education.py` | Educational deep-dive video (Part 2, 10+ min) | Swara | 16:9 | Unknown | Unknown | ⚠️ Verify |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | Swara | 9:16 | ❌ Direct Groq | ❌ | ⚠️ Needs upgrade |
| `generate_reel_morning.py` | Morning reel (7:00 AM) | Swara | 9:16 | Unknown | Unknown | ⚠️ Verify |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Neerja) | Madhur / Neerja | 9:16 | ❌ Direct Groq | ❌ | ⚠️ Needs upgrade |
| `generate_articles.py` | 4 SEO articles daily → Jekyll _posts | N/A | Jekyll MD | Unknown | Unknown | ⚠️ Verify |
| `generate_community_post.py` | YouTube daily community text post | N/A | Text | Unknown | Unknown | ⚠️ Verify |
| `generate_kids_video.py` | HerooQuest kids video (Hindi + English) | Various | 16:9 | Unknown | N/A | ✅ Running |

### Upload & Distribution

| File | Role | Status |
|---|---|---|
| `upload_youtube.py` | Uploads reel; saves `youtube_video_id` + `public_video_url` to meta; supports `--type reel/morning` | ✅ |
| `upload_youtube_english.py` | Uploads to English channel (separate credentials) | 🔄 Phase 3 |
| `upload_facebook.py` | Uploads reel to FB Page; supports `--meta-prefix morning/kids` | ✅ |
| `upload_kids_youtube.py` | Uploads kids video to HerooQuest YouTube channel | ✅ |

### Static Assets

| Path | Contents |
|---|---|
| `public/image/` | `zeno_happy.png`, `zeno_sad.png`, `zeno_greed.png`, `zeno_thinking.png` |
| `public/music/` | `bgmusic1.mp3`, `bgmusic2.mp3`, `bgmusic3.mp3` — rotated by weekday |

---

## 7. AI Fallback Chain (INTENDED — Partially Implemented)

All content generation SHOULD use `ai_client.py`. **The goal is: never call Groq/Gemini/Claude/OpenAI directly in generators.**

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

**CURRENT REALITY (verified May 2026):**
- `generate_analysis.py` — calls Groq directly, no fallback chain
- `generate_reel.py` — calls Groq directly, no fallback chain
- `generate_shorts.py` — calls Groq directly, no fallback chain
- `generate_education.py`, `generate_reel_morning.py`, `generate_articles.py` — status unverified

**Target import pattern for ALL generators (once upgraded):**
```python
from ai_client import ai, img_client
from human_touch import ht, seo

response = ai.generate(prompt, content_mode=CONTENT_MODE, lang="hi")
data     = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
hook     = ht.get_hook(mode=CONTENT_MODE, lang="hi")
clean    = ht.humanize(raw_output, lang="hi")
tags     = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")
speed    = ht.get_tts_speed()  # pass to edge_tts rate param
```

---

## 8. Voice Assignments (Verified from Code)

| Voice ID | Gender | Used For |
|---|---|---|
| `hi-IN-MadhurNeural` | Male | Short 2 — authoritative trade setups |
| `hi-IN-SwaraNeural` | Female | Short 3 was Swara; ZENO Reel; Morning Reel; Analysis |
| `en-IN-NeerjaNeural` | Female | Short 3 (current) — Indian English female — global macro pulse |
| `en-US-JennyNeural` | Female | English channel — all English content (Phase 3) |
| `en-US-GuyNeural` | Male | English Short 2 alternative (Phase 3) |

> ⚠️ **Short 3 voice discrepancy:** SYSTEM.md previously said Swara (Hindi female). Workflow comment and code say `en-IN-NeerjaNeural` (Indian English female). Current live code uses NeerjaNeural. Update any future prompts accordingly.

**TTS Speed:**
- `generate_shorts.py` uses hardcoded `rate="+10%"` (Madhur) and `rate="+12%"` (Neerja)
- `generate_reel.py` uses hardcoded `rate="+0%"`
- `generate_analysis.py` uses no rate param (TTS default)
- **Target:** Use `ht.get_tts_speed()` from human_touch.py for variation (0.95–1.05x) — not yet implemented

---

## 9. Trading Bot Architecture

### Overview

| Component | File | Role |
|---|---|---|
| AppScript v13.3 | Google Sheets bound script | Scans Nifty200 sheet, applies filters, writes WAITING candidates to AlertLog, stores memory in T4 |
| Python Bot v13.4 | `trading_bot.py` | Monitors AlertLog every 5 min, manages WAITING→TRADED transition, TSL updates, exit logic, Telegram alerts |

**Current status:** Paper trading. Followers receive Telegram signals and take manual entry. Dhan API integration planned for Phase 4 after backtest validation.

### Google Sheets Structure

| Sheet | Purpose |
|---|---|
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

### Nifty200 Column Map (0-based)

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
- Leader_Type = "Sector Leader"
- AF ≥ 5 (RS≥2.5 with sector tailwind)
- Master_Score ≥ 22
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

**Trade modes (stored as _MODE in T4 memory):**
- VCP — AB<0.04 + pre-breakout stage
- MOM — Strong Bull + RS≥6
- STD — everything else (default in bear market)

**Memory keys written per stock:**
- `{sym}_CAP` — capital tier (7000/10000/13000)
- `{sym}_MODE` — trade mode (VCP/MOM/STD)
- `{sym}_SEC` — sector name (for Good Morning sector context)

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
Fires when market is bullish AND stock ATR% > 1.5%.
```
ATR% < 1.5%    → no flag
ATR% 1.5–2.5%  → normal mover: target +65%, SL -40% on premium
ATR% > 2.5%    → fast mover: target +50%, SL -35% on premium
```

**Hard exit rules:**
- Loss > 5% → hard loss exit (immediate)
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

## 10. Critical Upload Chain

### Evening ZENO Reel (8:30 PM) — daily_reel.yml
```
generate_reel.py
    └── output/reel_YYYYMMDD.mp4
    └── output/meta_YYYYMMDD.json  ← public_video_url = ""

upload_youtube.py --type reel
    └── Writes youtube_video_id, youtube_video_url, public_video_url to meta

upload_facebook.py
    └── Posts to Facebook Page only (Group permanently removed)

Instagram → MANUAL: download artifact from GitHub Actions, post from phone
```

### Morning Reel (7:00 AM) — daily-morning-reel.yml
```
generate_reel_morning.py
    └── output/morning_reel_YYYYMMDD.mp4
    └── output/morning_reel_meta_YYYYMMDD.json

upload_youtube.py --type morning
upload_facebook.py --meta-prefix morning

Instagram → MANUAL
```

### Daily Videos (7:30 AM / 9:30 AM) — daily-videos.yml
```
generate_analysis.py
    └── output/analysis_video.mp4
    └── output/analysis_video_id.txt   ← Part 1 ID for Part 2 linking
    └── output/analysis_meta_YYYYMMDD.json

generate_education.py
    └── Reads analysis_video_id.txt → links Part 1 in description
    └── output/education_video.mp4  (must be 8+ min for mid-roll ads)
    └── output/education_video_id.txt
    └── output/education_meta_YYYYMMDD.json
```

### Shorts (11:30 AM / 1:30 PM) — daily-shorts.yml
```
generate_shorts.py
    └── Generates Short 2 (Madhur) + Short 3 (Neerja) + uploads to YouTube internally
    └── Shares links to Facebook Page
    └── Reads output/analysis_video_id.txt for Part 1 link (if present)
```

---

## 11. Environment Variables & Secrets

All stored in **GitHub Actions Secrets**. Never hardcode.

### AI Providers

| Secret | Purpose | Priority |
|---|---|---|
| `GROQ_API_KEY` | Groq — Llama 3.3 70B (primary) | ✅ |
| `GEMINI_API_KEY` | Google Gemini 2.0 Flash | ✅ |
| `ANTHROPIC_API_KEY` | Claude Haiku | ✅ |
| `OPENAI_API_KEY` | GPT-4o-mini | ✅ |
| `HF_TOKEN` | Hugging Face — used by kids video generator | ✅ |

### Social Platforms (Main Channel)

| Secret | Purpose | Status |
|---|---|---|
| `META_ACCESS_TOKEN` | Facebook Page API | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` | For token refresh | ✅ |
| `META_APP_SECRET` | For token refresh | ✅ |
| `FACEBOOK_PAGE_ID` | Main trading page | ✅ |
| `FACEBOOK_GROUP_ID` | Group ID (kept in secret but not used in workflows) | — |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON (Hindi channel) | ✅ |
| `YOUTUBE_CREDENTIALS_EN` | YouTube OAuth JSON (English channel) | ✅ Added |

### Social Platforms (Kids Channel — HerooQuest)

| Secret | Purpose | Status |
|---|---|---|
| `META_ACCESS_TOKEN_KIDS` | Kids Facebook Page API | ✅ |
| `FACEBOOK_KIDS_PAGE_ID` | HerooQuest Facebook Page ID (1021152881090398) | ✅ |
| `YOUTUBE_CREDENTIALS_KIDS` | YouTube OAuth JSON (HerooQuest channel) | ✅ |

### Telegram

| Secret | Purpose |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot authentication token |
| `TELEGRAM_CHAT_ID` | Free channel (ai360trading) |
| `CHAT_ID_ADVANCE` | Advance signals channel (₹499/month) |
| `CHAT_ID_PREMIUM` | Premium signals channel (bundle) |

### Google / GCP

| Secret | Purpose |
|---|---|
| `GCP_SERVICE_ACCOUNT_JSON` | Search Console Indexing API + Google Sheets (gspread) |

### Trading (Phase 4 — Not Connected Yet)

| Secret | Purpose |
|---|---|
| `DHAN_API_KEY` | Dhan trading API key |
| `DHAN_API_SECRET` | Dhan API secret |
| `DHAN_CLIENT_ID` | Dhan client ID |
| `DHAN_PIN` | Account PIN |
| `DHAN_TOTP_KEY` | 2FA TOTP key |

### General

| Secret | Purpose |
|---|---|
| `GH_TOKEN` | GitHub API token (for secret updates in token_refresh.py) |

---

## 12. Known Issues & Current State

### Instagram ❌ Permanently Removed
API integration removed from all workflows. Process: download artifact from GitHub Actions → post manually from phone. Do NOT re-add Instagram API unless explicitly asked.

### Facebook Group ❌ Permanently Removed
Requires Meta App Review, provides zero ad revenue benefit. Removed from all workflows permanently. `FACEBOOK_GROUP_ID` secret exists but is unused. Do NOT add Group posting back to any workflow.

### Short 3 Voice
Previously documented as `hi-IN-SwaraNeural`. Current workflow comment and code use `en-IN-NeerjaNeural` (Indian English female). This change gives Short 3 a global English appeal targeting UK/USA/Brazil audience. Correct voice is **NeerjaNeural**.

### generate_analysis.py uses `.history()` for market data
`fetch_market_data()` uses `t.history(period="2d")` instead of `fast_info['last_price']`. This is acceptable because it runs at 7:30 AM IST before market opens — `.history()` returns previous day's close which is the correct reference at that time. When market is live (shorts run at 11:30 AM), `generate_shorts.py` correctly uses `fast_info`. No change needed.

### YouTube Community Tab
Requires 500+ subscribers to be enabled. If below threshold, `generate_community_post.py` saves to `output/community_post_YYYYMMDD.txt` and does not crash.

### META Token Expiry
`token_refresh.yml` runs on 1st and 20th of every month. Refreshes both `META_ACCESS_TOKEN` and `META_ACCESS_TOKEN_KIDS`. Requires `META_APP_ID` and `META_APP_SECRET`.

---

## 13. Technical Standards

### The "Full Code" Rule
> AI assistants **must always provide the complete file content** when modifying any file. Partial snippets or diffs are strictly prohibited. Always write the entire file.

**Standard AI task prompt:**
```
Context: I am working on the ai360trading system. Refer to SYSTEM.md for architecture.
Task: [Your Task]
Note: Provide the FULL code for any file you modify. No partial snippets.
```

### AI Client Usage Rule (Target State — Not Yet Fully Implemented)
Never call AI APIs directly in generators. Use `ai_client.py`. See Section 7 for current reality.

### Dependency Pins

| Package | Version | Reason |
|---|---|---|
| `Pillow` | `>=10.3.0` | Required for LANCZOS resampling |
| `imageio` | `==2.9.0` | Prevents MoviePy rendering crashes |
| `moviepy` | `==1.0.3` | Force reinstall — newer versions break audio |
| `yfinance` | Latest | Use `fast_info['last_price']` for live prices; `.history()` acceptable for pre-market batch |
| `PyNaCl` | Latest | Required for GitHub Secret encryption in token_refresh.py |
| `google-generativeai` | Latest | Gemini fallback in ai_client.py |
| `anthropic` | Latest | Claude fallback in ai_client.py |
| `openai` | Latest | OpenAI fallback in ai_client.py |
| `gspread` | Latest | Google Sheets access in trading_bot.py |
| `oauth2client` | Latest | GCP service account auth for gspread |
| `pytz` | Latest | IST timezone handling |

### Video Formats

| Content | Ratio | Platform |
|---|---|---|
| Analysis + Education | 16:9 (1920×1080) | YouTube |
| Shorts, Morning Reel, ZENO Reel | 9:16 (1080×1920) | YouTube Shorts / Reels |

### Education Video Duration Check
`daily-videos.yml` runs a Python duration check after `generate_education.py`. If video < 480 seconds (8 min), the workflow **fails**. Mid-roll ads require 8+ minutes. Target is 10–12 minutes (22 slides).

### SEO Tags Strategy
Every video includes both India-specific AND global tags via `seo.get_video_tags()` (when human_touch is used):
- India: `Nifty50`, `TradingIndia`, `StockMarketIndia`, `BankNifty`
- Global: `USStocks`, `UKInvesting`, `BrazilMarket`, `UAEInvesting`, `GlobalInvesting`
- Universal: `Finance`, `Investing`, `FinancialLiteracy`, `Shorts`

---

## 14. Priority Task List for Future AI

> Read this section before starting any work. Tasks are ordered by impact. Complete higher-priority tasks first.

### 🔴 HIGH PRIORITY

**Task 1: Upgrade generate_analysis.py to use ai_client + human_touch**
- Replace `from groq import Groq` with `from ai_client import ai`
- Replace `from human_touch import ht, seo` 
- Replace direct `client.chat.completions.create()` call with `ai.generate_json()`
- Add `ht.humanize()` on script content before TTS
- Add `ht.get_hook()` for video opening
- Add `seo.get_video_tags()` for YouTube upload tags
- Replace hardcoded TTS default with `ht.get_tts_speed()`
- Keep `.history()` for market data — acceptable at 7:30 AM pre-market

**Task 2: Upgrade generate_reel.py to use ai_client + human_touch**
- Same pattern as Task 1
- Replace `from groq import Groq` + direct call
- Apply `ht.humanize()` on `audio_script` before TTS
- Replace hardcoded `rate="+0%"` with `ht.get_tts_speed()`

**Task 3: Upgrade generate_shorts.py to use ai_client + human_touch**
- Same pattern as Task 1
- Replace `from groq import Groq` + direct calls in `generate_short2_script()` and `generate_short3_script()`
- Apply `ht.humanize()` on both short scripts before TTS
- Replace hardcoded `rate="+10%"` and `rate="+12%"` with `ht.get_tts_speed()`
- Use `seo.get_video_tags()` instead of manual tag lists

### 🟡 MEDIUM PRIORITY

**Task 4: Verify and upgrade generate_education.py**
- Read the file first (not yet read/verified)
- Check if it uses ai_client + human_touch or direct Groq
- Upgrade if needed (same pattern as Tasks 1–3)
- Confirm it outputs 22 slides × 80–100 words = 10–12 min video
- Confirm it reads `analysis_video_id.txt` and cross-links Part 1

**Task 5: Verify and upgrade generate_reel_morning.py**
- Read the file first (not yet read/verified)
- Check if it uses ai_client + human_touch or direct Groq
- Upgrade if needed

**Task 6: Verify generate_articles.py and generate_community_post.py**
- Read both files
- Check ai_client + human_touch usage
- Upgrade if needed

### 🔵 FUTURE / PHASE 3

**Task 7: English Channel (Phase 3)**
- Create `generate_english.py` for English-language shorts
- Use `en-US-JennyNeural` (female) and `en-US-GuyNeural` (male)
- Use `upload_youtube_english.py` with `YOUTUBE_CREDENTIALS_EN`

**Task 8: Disney 3D Reel Upgrade (Phase 3)**
- Phase 2 (now): PIL + MoviePy + ZENO PNG — 2D animated slides
- Phase 3 (3–6 months): Gemini Veo API for AI video clips
- Phase 4 (6–12 months): Stable Diffusion + AnimateDiff for 3D frames
- Hook exists in `ai_client.py` via `img_client` — swap in when ready

**Task 9: Dhan Live Trading (Phase 4)**
- All secrets already added: `DHAN_API_KEY`, `DHAN_API_SECRET`, `DHAN_CLIENT_ID`, `DHAN_PIN`, `DHAN_TOTP_KEY`
- Activate only after backtest: 30–40 live paper trades, win rate >35%
- Max capital deployed: ₹45,000 (₹5k buffer)
- CE execution requires Dhan API + lot size data

---

## 15. Data Flow — Full System

```
Market hours (Mon–Fri, 9:15 AM–3:30 PM IST)
└── trading_bot.yml (every 5 min)
    └── trading_bot.py v13.4
        └── Monitors AlertLog → WAITING→TRADED → TSL → Exit → History

AppScript v13.3 (Google Sheets — manual trigger or scheduled)
└── Nifty200 scan → 10-gate filter → AlertLog → T4 memory

7:00 AM daily
└── daily-morning-reel.yml
    └── generate_reel_morning.py → upload_youtube.py --type morning
    └── upload_facebook.py --meta-prefix morning
    └── Instagram artifact saved for manual post

7:30 AM / 9:30 AM daily
└── daily-videos.yml
    └── generate_analysis.py → Part 1 → YouTube (saves analysis_video_id.txt)
    └── generate_education.py → Part 2 → YouTube (reads analysis_video_id.txt)
    └── Duration check: fail if < 8 min

10:00 AM / 11:30 AM daily
└── daily-articles.yml
    └── generate_articles.py → 4 articles → GitHub Pages (auto-commit)
    └── Facebook Page post (Group removed)

11:30 AM / 1:30 PM daily
└── daily-shorts.yml
    └── generate_shorts.py → Short 2 (Madhur) + Short 3 (Neerja) → YouTube
    └── Facebook Page share
    └── generate_community_post.py → YouTube Community Tab

8:00 AM daily
└── kids-daily.yml
    └── generate_kids_video.py → upload_kids_youtube.py → Facebook Kids Page

8:30 PM daily
└── daily_reel.yml
    └── generate_reel.py → upload_youtube.py --type reel
    └── upload_facebook.py
    └── Instagram artifact saved for manual post

11:59 PM IST Sun–Thu
└── keepalive.yml → commit .keepalive → prevent workflow disable

1st + 20th of month
└── token_refresh.yml → refresh META_ACCESS_TOKEN + META_ACCESS_TOKEN_KIDS
```

---

## 16. Website

- **URL:** `ai360trading.in`
- **Hosting:** GitHub Pages (Jekyll, `master` branch `_posts/`)
- **Publishing:** Auto-commit by `daily-articles.yml` (git user: AI360-Automation)
- **SEO Indexing:** Instant via `GCP_SERVICE_ACCOUNT_JSON`
- **Revenue:** Google AdSense (USA/UK English readers = highest CPM)
- **Content pillars:** Stock Market, Bitcoin/Crypto, Personal Finance, AI Trading
- **Market coverage:** India (Nifty50, BankNifty), USA (S&P500, NASDAQ), UK (FTSE100), Brazil (IBOVESPA), Crypto (BTC, ETH)

---

## 17. Social Media Links

| Platform | Handle/Link |
|---|---|
| 🌐 Website | ai360trading.in |
| 📣 Telegram (Free) | @ai360trading |
| 📣 Telegram (Advance) | ai360trading_Advance — ₹499/month |
| 📣 Telegram (Premium) | ai360trading_Premium — bundle |
| ▶️ YouTube | @ai360trading |
| 📸 Instagram | @ai360trading (manual post only) |
| 👥 Facebook Group | Removed permanently |
| 📘 Facebook Page | facebook.com/ai360trading |
| 🐦 Twitter/X | @ai360trading |
| 🦸 Kids YouTube | HerooQuest (@heroquest or similar) |
| 📘 Kids Facebook | HerooQuest Page (ID: 1021152881090398) |

---

## 18. Phase Roadmap

### Phase 1 ✅ Complete
`ai_client.py`, `human_touch.py`, `token_refresh.py`, `generate_reel_morning.py`

### Phase 2 ✅ Mostly Complete (Infrastructure done, generator upgrades pending)
All workflows operational. Content generation running daily. Generators still call Groq directly — upgrade to ai_client + human_touch is the remaining Phase 2 work (see Priority Task List Section 14).

### Phase 3 🔄 In Progress
- English channel shorts (`generate_english.py`) — Medium priority
- English channel upload (`upload_youtube_english.py`) — Medium priority
- Disney 3D reel via Gemini Veo — Future

### Phase 4 📋 Planned — Dhan Live Trading
- Backtest validation required first (30–40 paper trades, win rate >35%)
- All Dhan secrets already added
- CE flag already informational in Telegram alerts
- Max ₹45,000 deployment after validation

---

## 19. How to Test Everything

### Test a workflow manually
GitHub Actions → select workflow → **Run workflow** → set `content_mode` dropdown → watch logs.

### Verify ai_client fallback chain (once upgraded)
In logs, look for:
```
✅ AI generated via groq
⚠️ groq failed → trying gemini
✅ AI generated via gemini
```

### Verify trading bot
In logs (`trading_bot.yml`):
```
[REGIME] Nifty CMP ₹22679 vs 20DMA ₹23547 → BEARISH
[INFO] Active trades: 4/5
[TSL] NSE:ONGC [STD]: ₹280.60→₹285.20
[DONE] 15:20:01 IST | mem=842 chars
```

### Automation on/off switch
Google Sheet → AlertLog → cell T2 → set "YES" to enable, anything else to disable.

### Force each content mode
```
workflow_dispatch → content_mode = market   # weekday content
workflow_dispatch → content_mode = weekend  # weekend content
workflow_dispatch → content_mode = holiday  # holiday content
```

---

*Documentation maintained by AI360Trading automation.*
*Verified and updated: May 2026 — Claude Sonnet 4.6*
*Verified against: SYSTEM.md, generate_analysis.py, generate_reel.py, generate_shorts.py, all 9 workflow yml files*
*Next verification needed: generate_education.py, generate_reel_morning.py, generate_articles.py, generate_community_post.py, ai_client.py, human_touch.py*
*Update this file whenever architecture, secrets, platform status, or file logic changes.*
