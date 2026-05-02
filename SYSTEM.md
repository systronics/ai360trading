# AI360Trading — Master System Documentation

**Last Updated:** May 2, 2026 — Trading Bot v13.4 + AppScript v13.3
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
| YouTube Kids | 🔄 Building | Separate channel — credentials added, automation TBD |
| YouTube English | 🔄 Building | Phase 3 — auto-translated separate channel |
| YouTube Shorts | ✅ Auto | Short 2 + Short 3 working |
| YouTube Reels | ✅ Auto | ZENO reel (8:30 PM) working |
| YouTube Morning Reel | ✅ Auto | 7:00 AM reel (generate\_reel\_morning.py) working |
| Facebook Page (AI360Trading) | ✅ Auto | Posts, reels, article shares all working |
| Facebook Page (HerooQuest Kids) | ✅ Auto | Fixed May 2026 — separate `META_ACCESS_TOKEN_KIDS` Page token |
| Facebook Group (ai360trading) | ❌ Broken | Token missing `publish_to_groups` scope — see Section 12 |
| Instagram | 📲 Manual | Videos downloaded from GitHub Artifacts and posted manually |
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
| 5 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 6 | Short 4 English (9:16) | 11:30 AM (same workflow) | YouTube English Shorts | 🔄 Phase 3 |
| 7 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 8 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB | ✅ |
| 9 | Instagram | Manual | Instagram | 📲 Download artifact → post manually |
| **Total** | **11 pieces/day auto + Instagram manual** | — | — | — |

> **USA/UK prime time content:** Videos uploaded at IST times but SEO-optimised for 11 PM–1 AM IST peak.

---

## 5. GitHub Actions Workflows

| File | Trigger (IST) | Purpose | Mode-Aware |
| --- | --- | --- | --- |
| `trading_bot.yml` | Every 5 min (08:15–16:29, Mon–Fri) + 08:45, 12:58, 15:58 | `trading_bot.py` — Nifty200 signals + daily messages | ✅ Auto-skips weekends/holidays |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 (analysis) + Part 2 (education) | ✅ |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 | ✅ |
| `daily_reel.yml` | 8:30 PM daily | ZENO Reel | ✅ |
| `daily-morning-reel.yml` | 7:00 AM daily | Morning Reel | ✅ |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages | ✅ |
| `kids-daily.yml` | 8:00 AM daily | Kids video → YouTube + Facebook HerooQuest | ✅ |
| `token_refresh.yml` | 1st + 20th of month | Auto META token refresh | N/A |
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
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Swara) | ai\_client, human\_touch, Edge-TTS | ✅ Phase 2 |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ai\_client, human\_touch, MoviePy | ✅ Phase 2 |
| `generate_reel_morning.py` | Morning reel (7:00 AM) — day/country aware | ai\_client, human\_touch, MoviePy | ✅ |
| `generate_analysis.py` | 8-slide market analysis video (Part 1) | ai\_client, human\_touch, MoviePy | ✅ Phase 2 |
| `generate_education.py` | Educational deep-dive video (Part 2) | ai\_client, human\_touch, content\_calendar | ✅ Phase 2 |
| `generate_articles.py` | 4 SEO articles daily → Jekyll \_posts | ai\_client, human\_touch, Google Indexing | ✅ Phase 2 |

### Upload & Distribution

| File | Role | Status |
| --- | --- | --- |
| `upload_youtube.py` | Uploads reel; saves `youtube_video_id` + `public_video_url` to meta | ✅ |
| `upload_youtube_english.py` | Uploads to English channel (separate credentials) | 🔄 Phase 3 |
| `upload_facebook.py` | Uploads reel to FB Page; shares to Group; posts articles | ✅ |
| `upload_instagram.py` | Instagram upload script (API chain built; falls back to manual artifact) | 📲 Manual currently |

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
Anthropic Claude — claude-haiku-4-5-20251001 (tertiary — best human-touch writing)
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

> ⚠️ `generate_articles.py` uses `ai_client` — consistent with all other generators.

---

## 8. Trading Bot Architecture

### Overview

The trading system is split across two components that work together:

| Component | File | Role |
| --- | --- | --- |
| AppScript v13.3 | Google Sheets bound script | Scans Nifty200 sheet, applies filters, writes WAITING candidates to AlertLog, stores memory in BotMemory sheet |
| Python Bot v13.4 | `trading_bot.py` | Monitors AlertLog every 5 min, manages WAITING→TRADED transition, TSL updates, exit logic, Telegram alerts |

**Current status:** Paper trading. Followers receive Telegram signals and take manual entry. Dhan API integration planned for Phase 4 after backtest validation.

### Google Sheets Structure

| Sheet | Purpose |
| --- | --- |
| `Nifty200` | Live data for all 200 stocks — CMP, DMAs, FII data, signals, scores (34 cols) |
| `AlertLog` | Active + waiting trades — 15 rows, 19 cols. T2=YES/NO automation switch. T4=memory string (legacy ref — memory now in BotMemory sheet) |
| `BotMemory` | Persistent key=value memory store replacing T4 cell — stores TSL, MAX, ATR, CAP, MODE, SEC, exit dates, daily flags per stock |
| `History` | Closed trade log — 18 cols A–R |

> ⚠️ **Memory system note:** Memory was previously stored in AlertLog T4 cell as a comma-separated string. It has been migrated to a dedicated `BotMemory` sheet. SYSTEM.md references to T4 memory are legacy — always use BotMemory sheet for current state.

### AlertLog Column Map (0-based)

```
A=0  Signal Time    B=1  Symbol        C=2  Live Price     D=3  Priority Score
E=4  Trade Type     F=5  Strategy      G=6  Breakout Stage H=7  Initial SL
I=8  Target         J=9  RR Ratio      K=10 Trade Status   L=11 Entry Price
M=12 Entry Time     N=13 Days in Trade O=14 Trailing SL    P=15 P/L%
Q=16 ATH Warning    R=17 Risk ₹        S=18 Position Size  T=19 SYSTEM CONTROL
```

**T2** = automation on/off switch (set YES to enable)

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
r[30] 52W_Breakout_Score(AE) r[31] Sector_Rotation_Score (AF)
r[32] FII_Buying_Signal(AG) r[33] Master_Score (AH)
r[34] Sector_Rank (AI)    ← =RANK(AF, FILTER by same sector) — rank within sector by AF score
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

**Trade modes (stored as \_MODE in BotMemory):**

* VCP — AB<0.04 + pre-breakout stage
* MOM — Strong Bull + RS≥6
* STD — everything else (default in bear market)

**Memory keys written per stock (to BotMemory sheet):**

* `{sym}_CAP` — capital tier (7000/10000/13000)
* `{sym}_MODE` — trade mode (VCP/MOM/STD)
* `{sym}_SEC` — sector name (for Good Morning sector context)
* `{sym}_TSL` — current trailing SL price
* `{sym}_MAX` — highest price seen since entry
* `{sym}_ATR` — ATR at entry
* `{sym}_EXDT` — exit date (for 5-day cooldown)

**Sort order:** finalScore DESC, then ATR% ASC as tiebreaker within ±2 score points (minimum SL preference).

### Python Bot v13.4 — Key Logic

**TSL Parameters (mode-aware) — current values:**

```python
TSL_PARAMS = {
    "VCP": { "breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0 },
    "MOM": { "breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0 },
    "STD": { "breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0 },
}
```

> **v13.3 STD change:** trail widened from 6→10, atr\_mult from 1.5→2.5. Reason: let swing trades run longer rather than being stopped out on normal pullbacks. VCP and MOM unchanged.

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

**Telegram channels and content per channel:**

| Channel | Secret | Audience | Content |
| --- | --- | --- | --- |
| Basic (free) | `TELEGRAM_CHAT_ID` | Free followers | Market mood, signal closed result only |
| Advance | `CHAT_ID_ADVANCE` | ₹499/month | Full entry/exit details, TSL updates, mid-day pulse, CE candidate flag |
| Premium | `CHAT_ID_PREMIUM` | Bundle subscribers | Everything in Advance + **options buying logic** (strike, target%, SL%) |

> ⚠️ **Known bug — Telegram channel variables are swapped in code:**
> In `trading_bot.py`, `CHAT_ADVANCE` reads `CHAT_ID_PREMIUM` secret and `CHAT_PREMIUM` reads `CHAT_ID_ADVANCE` secret. This means both channels currently receive the same message content. Fix required:
>
> ```python
> # WRONG (current):
> CHAT_ADVANCE = os.environ.get('CHAT_ID_PREMIUM')
> CHAT_PREMIUM = os.environ.get('CHAT_ID_ADVANCE')
>
> # CORRECT (fix to):
> CHAT_ADVANCE = os.environ.get('CHAT_ID_ADVANCE')
> CHAT_PREMIUM = os.environ.get('CHAT_ID_PREMIUM')
> ```
>
> Also: `trading_bot.py` reads `TELEGRAM_TOKEN` but the GitHub Secret is named `TELEGRAM_BOT_TOKEN`. Verify which name is actually set in GitHub Secrets and make both match.

**Desired Premium-only content (to implement after fixing channel swap):**

Premium channel should get everything Advance gets, PLUS a dedicated options buying block showing:
* CE strike price recommendation
* Entry trigger condition
* Target % on premium
* SL % on premium
* Suggested lot sizing note

This block is separate from the CE candidate flag shown in Advance — Premium gets full actionable options advisory.

**CE candidate flag (v13.4 — shown in Advance + Premium entry alerts):**

Fires when market is bullish AND stock ATR% > 1.5%. Informational flag only. Uses ATR14 (col AC) and CMP — no new data needed. Currently uses estimated ATR derived from target/SL spread, not actual ATR14 from Nifty200 sheet. Real ATR14 integration planned for Phase 4.

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
    └── Uploads reel to Facebook Page
    └── Posts link to Facebook Group (when fixed)
    └── Overwrites meta → public_video_url (Facebook watch URL)
    └── Posts articles from RSS feed to Page + Group

upload_instagram.py
    └── Reads public_video_url from meta
    └── Attempts Instagram API → polls until FINISHED → publishes
    └── On failure: saves caption to output/instagram_caption.txt for manual posting
```

### Morning Reel (7:00 AM)

```
generate_reel_morning.py
    └── output/morning_reel_YYYYMMDD.mp4
    └── output/morning_reel_meta_YYYYMMDD.json

upload_youtube.py (morning mode)
upload_facebook.py (morning mode)
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

> **Instagram posting (manual):** GitHub Actions → Run → Artifacts → download reel → post manually to Instagram. Caption saved to `output/instagram_caption.txt` in same artifact.

---

## 10. Environment Variables & Secrets

All stored in **GitHub Actions Secrets**. Never hardcode any of these values.
This list is verified against actual GitHub Secrets as of May 2026.

### Telegram

| Secret | Purpose | Notes |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | Bot authentication token | ✅ Confirmed secret name |
| `TELEGRAM_CHAT_ID` | Free channel (@ai360trading) | ✅ |
| `CHAT_ID_ADVANCE` | Advance signals channel (₹499/month) | ✅ |
| `CHAT_ID_PREMIUM` | Premium signals channel (bundle) | ✅ |

> ⚠️ **Bug:** `trading_bot.py` reads `os.environ.get('TELEGRAM_TOKEN')` but the secret is named `TELEGRAM_BOT_TOKEN`. Fix: change code to `os.environ.get('TELEGRAM_BOT_TOKEN')`.

### Social Platforms — Main (AI360Trading)

| Secret | Purpose | Status |
| --- | --- | --- |
| `META_ACCESS_TOKEN` | Facebook Page (AI360Trading/Unofficial Amit Kumar) token | ✅ Auto-refreshed every 60 days |
| `META_APP_ID` | Facebook App ID — for token refresh | ✅ |
| `META_APP_SECRET` | Facebook App Secret — for token refresh | ✅ |
| `FACEBOOK_PAGE_ID` | Main trading Facebook Page ID | ✅ |
| `FACEBOOK_GROUP_ID` | Trading Facebook Group ID (ai360trading) | ✅ (posting broken — token scope issue) |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business/Creator numeric ID | ✅ |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON (Hindi trading channel) | ✅ |

> ⚠️ **Page rename in progress:** "Unofficial Amit Kumar" page is being renamed to "AI360 Algo Trading". Facebook review takes up to 7 days. Same Page ID, same token — nothing changes in the system.

### Social Platforms — Kids Channel (HerooQuest)

| Secret | Purpose | Status |
| --- | --- | --- |
| `FACEBOOK_KIDS_PAGE_ID` | HerooQuest Kids Facebook Page ID (1021152881090398) | ✅ |
| `META_ACCESS_TOKEN_KIDS` | HerooQuest Page Access Token — never expires | ✅ Fixed May 2026 |
| `YOUTUBE_CREDENTIALS_KIDS` | YouTube OAuth JSON (Kids channel) | ✅ |

> **Important:** `META_ACCESS_TOKEN_KIDS` is a **Page Access Token** (not User Token) — it never expires so no auto-refresh needed. If it ever stops working, regenerate via Graph API Explorer: `GET /{PAGE_ID}?fields=access_token` using a fresh User Token.

### AI Providers (Fallback Chain)

| Secret | Purpose | Priority | Status |
| --- | --- | --- | --- |
| `GROQ_API_KEY` | Groq — Llama 3.3 70B | Primary | ✅ |
| `GEMINI_API_KEY` | Google Gemini 2.0 Flash | Secondary | ✅ |
| `ANTHROPIC_API_KEY` | Claude — `claude-haiku-4-5-20251001` | Tertiary | ✅ |
| `OPENAI_API_KEY` | GPT-4o-mini | Quaternary | ✅ |
| `HF_TOKEN` | Hugging Face — image/model generation | ✅ Added recently |
| `STABILITY_API_KEY` | Stability AI — image generation | ✅ Added recently |

### YouTube Playlists

| Secret | Purpose |
| --- | --- |
| `PLAYLIST_NIFTY_ANALYSIS` | Playlist ID for Nifty analysis videos |
| `PLAYLIST_SWING_TRADE` | Playlist ID for swing trade videos |
| `PLAYLIST_WEEKLY_OUTLOOK` | Playlist ID for weekly outlook videos |
| `PLAYLIST_ZENO_WISDOM` | Playlist ID for ZENO reel series |

> These playlist IDs are injected into upload scripts so videos are automatically added to the correct playlist on upload.

### Affiliate Links

| Secret | Purpose |
| --- | --- |
| `AFFILIATE_INSURANCE_IN` | India insurance affiliate link/ID |
| `AFFILIATE_INSURANCE_UK` | UK insurance affiliate link/ID |
| `AFFILIATE_INSURANCE_US` | US insurance affiliate link/ID |

> Affiliate secrets used in article generation — injected into personal finance content for the relevant country audience.

### Dhan Trading API (Phase 4 — not connected yet)

| Secret | Purpose | Status |
| --- | --- | --- |
| `DHAN_API_KEY` | API key | ✅ Added — not connected yet |
| `DHAN_API_SECRET` | API secret | ✅ Added — not connected yet |
| `DHAN_CLIENT_ID` | Client ID | ✅ Added — not connected yet |
| `DHAN_PIN` | Account PIN | ✅ Added — not connected yet |
| `DHAN_TOTP_KEY` | 2FA TOTP key | ✅ Added — not connected yet |

> Dhan integration planned for Phase 4 after backtest validation. All 5 secrets ready.

### Google / GCP

| Secret | Purpose |
| --- | --- |
| `GCP_SERVICE_ACCOUNT_JSON` | Search Console Indexing API + Google Sheets (gspread) |

### General

| Secret | Purpose |
| --- | --- |
| `GH_TOKEN` | GitHub API token — used by token\_refresh.py to update secrets |

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

### Telegram Channel Variable Swap ⚠️ CRITICAL

`CHAT_ADVANCE` and `CHAT_PREMIUM` variables are swapped in `trading_bot.py` — both channels currently receive the same content. Fix:

```python
# In trading_bot.py, change:
CHAT_ADVANCE = os.environ.get('CHAT_ID_ADVANCE')   # was reading CHAT_ID_PREMIUM
CHAT_PREMIUM = os.environ.get('CHAT_ID_PREMIUM')   # was reading CHAT_ID_ADVANCE
```

After fixing, Premium channel needs a dedicated options buying block (separate from CE flag in Advance). See Section 8 for desired Premium content spec.

### Telegram Token Name Mismatch ⚠️

`trading_bot.py` reads `os.environ.get('TELEGRAM_TOKEN')` but the GitHub Secret is confirmed as `TELEGRAM_BOT_TOKEN`. Bot will silently get `None` and all Telegram sends will fail. Fix in `trading_bot.py`:

```python
# WRONG (current):
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# CORRECT (fix to):
TG_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
```

### Facebook Group Posting ❌ (ai360trading group)

The code in `upload_facebook.py` already supports group posting — it posts the reel link + caption to `FACEBOOK_GROUP_ID` after Page upload succeeds. No code changes needed, just token fix.

**Root causes (check in order):**

1. `META_ACCESS_TOKEN` missing `publish_to_groups` scope — most likely
2. Bot account not **Admin** of the group (must be Admin, not just member)
3. Group Settings → Advanced → "Allow content from apps" OFF
4. App not approved for Groups API by Meta

**Fix:**
1. Graph API Explorer → add `publish_to_groups` to Permissions list → Generate Access Token → Edit Settings → grant access
2. Extend to long-lived token
3. Update `META_ACCESS_TOKEN` in GitHub Secrets
4. Verify Amit Kumar account is Admin of ai360trading group

### HerooQuest Kids Facebook Upload ✅ Fixed May 2026

Was failing with Error 200 (permission denied) because workflow was using `META_ACCESS_TOKEN` (AI360Trading token) instead of `META_ACCESS_TOKEN_KIDS`. Fixed by:
1. Generating a Page Access Token specifically for HerooQuest via Graph API Explorer
2. Extending to long-lived token via token debugger
3. Saving as `META_ACCESS_TOKEN_KIDS` in GitHub Secrets
4. `META_ACCESS_TOKEN_KIDS` is a Page token — never expires, no auto-refresh needed

### Instagram Posting 📲 Manual

Instagram is currently posted manually. Process:
1. GitHub Actions → completed run → Artifacts → download reel artifact
2. Open `instagram_caption.txt` from artifact for the caption
3. Post manually via Instagram app

`upload_instagram.py` API chain is built and will attempt auto-post if `public_video_url` is available in meta. Will become fully automatic once Facebook Group posting is fixed (Facebook URL feeds Instagram API).

### META\_ACCESS\_TOKEN Expiry — Automated ✅

`token_refresh.yml` runs every 50 days automatically. Refreshes token + updates GitHub Secret + sends Telegram alert. Requires `META_APP_ID` and `META_APP_SECRET` (both now added).

### CE Flag ATR — Estimated, Not Real ATR14

Current CE candidate flag uses estimated ATR derived from `(target - cp) / atr_tgt_mult`, not actual ATR14 from Nifty200 sheet column AC. This means ATR% calculation can be imprecise for stocks with unusual target multiples. Real ATR14 from sheet planned for Phase 4.

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
        └── CE candidate flag in entry alert (bullish + ATR%>1.5% — Advance+Premium)
        └── Options advisory block in entry alert (Premium only — after channel swap fix)
        └── History sheet append on exit
        └── BotMemory sheet updated each run

AppScript v13.3 (Google Sheets bound — triggered manually or on schedule)
└── Nifty200 sheet scan (batched 60 rows per run)
└── 10-gate filter → bearish or bullish path
└── Conviction bonus + capital tier + trade mode
└── ATR% tiebreaker sort (min SL preference)
└── Write WAITING rows to AlertLog
└── Write _CAP, _MODE, _SEC keys to BotMemory sheet
└── Bearish alert with top sector context → Telegram

7:00 AM daily
└── daily_reel.yml (morning job)
    └── generate_reel_morning.py → upload_youtube → upload_facebook ✅
    └── Instagram: manual

7:30 AM / 9:30 AM daily
└── daily-videos.yml
    └── generate_analysis.py → Part 1 → YouTube ✅
    └── generate_education.py → Part 2 → YouTube ✅

10:00 AM / 11:30 AM daily
└── daily-articles.yml
    └── generate_articles.py → 4 articles → GitHub Pages ✅ → Facebook ✅

11:30 AM / 1:30 PM daily
└── daily-shorts.yml
    └── generate_shorts.py → Short 2 + Short 3 → YouTube ✅

8:30 PM daily
└── daily_reel.yml (evening job)
    └── generate_reel.py → ZENO reel
    └── upload_youtube.py ✅ → upload_facebook.py ✅ → upload_instagram.py 📲 manual
```

---

## 16. Website

* **URL:** `ai360trading.in`
* **Hosting:** GitHub Pages (Jekyll, `master` branch `_posts/`)
* **Publishing:** Auto-commit by `daily-articles.yml`
* **SEO Indexing:** Instant via `GCP_SERVICE_ACCOUNT_JSON`
* **Revenue:** Google AdSense (USA/UK English readers = highest CPM)
* **Content pillars:** Stock Market, Bitcoin/Crypto, Personal Finance, AI Trading
* **Market coverage:** India (Nifty50, BankNifty), USA (S&P500, NASDAQ), UK (FTSE100), Brazil (IBOVESPA), Crypto (Bitcoin, Ethereum)
* **MAX\_POSTS:** 60 articles retained in `_posts/` — older ones auto-deleted

---

## 17. Broker Partner Links

* [Open account in Zerodha](https://bit.ly/2VK6k5F)
* [Open account in Dhan](https://invite.dhan.co/?invite=MSIVC45309)

---

## 18. Phase Roadmap

### Phase 1 ✅ — Infrastructure (Complete)

* Jekyll site live at ai360trading.in
* GitHub Actions automation (all workflows)
* ai\_client.py fallback chain
* human\_touch.py anti-AI-penalty system
* trading\_bot.py paper trading + Telegram alerts
* META token auto-refresh

### Phase 2 ✅ — Content Upgrade (Complete)

* All generators upgraded to use ai\_client + human\_touch
* generate\_articles.py — 4 articles/day with live prices, Google Trends, personas
* generate\_analysis.py + generate\_education.py — full video pipeline
* generate\_reel\_morning.py — 7 AM morning reel
* Trading bot v13.4 — CE candidate flag, mode-aware TSL, capital tiers

### Phase 3 🔄 — English Channel + Global Scale (Planned)

* YouTube English channel auto-upload (`upload_youtube_english.py`)
* Short 4 English — same workflow as Short 2/3
* Facebook Group posting fixed (token scope)
* Instagram fully automated (after Facebook fix)
* English content voice: `en-US-JennyNeural`

### Phase 4 📋 — Live Trading + Premium Options (Planned)

* Dhan API integration for live trade execution
* Premium channel real options advisory (after Telegram channel swap fix)
* Real ATR14 from Nifty200 sheet used for CE flag
* Backtest validation before going live
* BotMemory sheet fully migrated and documented

---

## 19. Contact & Admin

* **Admin email:** admin@ai360trading.in
* **Location:** Haridwar, Uttarakhand, India
* **Legal:** All content educational only. Not SEBI registered. Full disclaimer: ai360trading.in/disclaimer/
