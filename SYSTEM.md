# AI360Trading — Master System Documentation

**Last Updated:** May 2026 — Verified against actual code + all 9 workflows + AppScript v14.0
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Infrastructure Complete | Phase 3 🔄 In Progress | Phase 4 📋 Planned
**Primary Audience:** Bilingual Hindi + English — Indian retail traders + global investors

> ⚠️ **Read this file completely before making ANY changes.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT).
> Always read the actual source file before editing — do NOT assume this document is current.

---

## 1. Real Mission

> This system is built to run **forever, fully automated**, generating passive income for the owner's family — even without active involvement. Built on ₹0/month infrastructure. No employees. No office. Pure automation.

### Monetisation Streams

| Stream | Platform | High-CPM Target Countries |
|---|---|---|
| Video Ad Revenue | YouTube (Hindi) | USA, UK, Canada, Australia, UAE |
| Video Ad Revenue | YouTube (English) | USA, UK, Canada, Australia — 3–5x higher CPM |
| Shorts / Reels Bonus | YouTube, Facebook | USA, UK, Brazil, India |
| Website Ad Revenue | GitHub Pages (ai360trading.in) | USA, UK, Canada |
| In-Stream Video Ads | Facebook Page | USA, UK, Brazil, India |
| Paid Signal Subscriptions | Telegram (Advance + Premium) | India, UAE, Global |
| Public Signal Pages | /swing-dashboard/ + /positional-picks/ | India, Global |

### Target Countries by CPM Priority
1. 🇺🇸 USA 2. 🇬🇧 UK 3. 🇦🇺 Australia 4. 🇦🇪 UAE 5. 🇨🇦 Canada 6. 🇧🇷 Brazil 7. 🇮🇳 India

> USA/UK prime time = 11 PM–1 AM IST. All content optimised for these markets.

---

## 2. Platform Status (Verified May 2026)

| Platform | Status | Notes |
|---|---|---|
| YouTube Hindi | ✅ Auto | Analysis + Education + Shorts + Reels |
| YouTube English | 🔄 Phase 3 | Separate channel, credentials added |
| YouTube Shorts | ✅ Auto | Short 2 (Madhur) + Short 3 (Neerja) |
| YouTube Community Posts | ✅ Built | generate_community_post.py — 12:00 PM daily |
| YouTube ZENO Reel | ✅ Auto | 8:30 PM daily |
| YouTube Morning Reel | ✅ Auto | 7:00 AM daily |
| YouTube Kids (HerooQuest) | ✅ Auto | kids-daily.yml — 8:00 AM daily |
| Facebook Page | ✅ Auto | Posts, reels, article shares |
| Facebook Group | ❌ Permanently Removed | Requires Meta App Review, zero ad revenue |
| Instagram | ❌ API Removed | Manual post only — download artifact from GitHub Actions |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | Signal alerts to 3 channels (paper trading) |
| Swing Dashboard | ✅ Live | ai360trading.in/swing-dashboard/ |
| Positional Picks | ✅ Live | ai360trading.in/positional-picks/ |

> **Instagram and Facebook Group permanently removed. Do not add back.**
> Instagram: download artifact from GitHub Actions → post manually from phone.

---

## 3. Public Signal Pages on Website

### Swing Dashboard — ai360trading.in/swing-dashboard/
- Embeds live AlertLog data — shows WAITING + TRADED rows from Nifty200 Google Sheet
- Shows entry zone, target, stop-loss, signal type for each active swing trade
- Audience: free users and active traders who want swing signals (3–15 day holds)
- Updates: daily before market open (8 AM IST) and after close (4 PM IST)
- Linked from website footer under "Platform"

### Positional Picks — ai360trading.in/positional-picks/
- Separate Google Sheet (NOT the Nifty200/AlertLog sheet) — embedded on website
- Shows fundamental + technical research signals: BUY and SELL signals
- Audience: **safe, conservative, positional traders** — longer holds (weeks to months)
- These traders check this page periodically rather than monitoring daily
- Mobile-friendly: swipe left/right to see full table data
- Linked from website footer under "Platform"

> **Content AI rule:** When generating articles, scripts, or Telegram messages about signals, mention both pages. Active swing traders → /swing-dashboard/. Conservative/positional traders → /positional-picks/. Both are live and public — no login required.

---

## 4. Content Mode System

| Mode | When | Content Strategy |
|---|---|---|
| `market` | Mon–Fri (excluding Indian holidays) | Live Nifty50/Global data, trade setups, signals |
| `weekend` | Saturday–Sunday | Educational, wealth-building, global audience focus |
| `holiday` | Indian Market Holidays | Motivational, "Market band hai par seekhna chalu" |

Mode auto-detected by `indian_holidays.py` → written to `$GITHUB_ENV` at workflow start.
`HOLIDAY_NAME` env var written alongside `CONTENT_MODE` when mode is `holiday`.

---

## 5. Daily Content Output

| # | Content | Time (IST) | Workflow |
|---|---|---|---|
| 1 | Morning Reel (9:16) | 7:00 AM | daily-morning-reel.yml |
| 2 | Part 1 Analysis (16:9) | 7:30 AM weekday / 9:30 AM weekend | daily-videos.yml |
| 3 | Part 2 Education (16:9, 10+ min) | Same workflow | daily-videos.yml |
| 4 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | daily-articles.yml |
| 5 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | daily-shorts.yml |
| 6 | Short 3 English (9:16) | Same workflow | daily-shorts.yml |
| 7 | YouTube Community Post | 12:00 PM | daily-shorts.yml (same run) |
| 8 | Kids Video (HerooQuest) | 8:00 AM | kids-daily.yml |
| 9 | ZENO Reel (9:16) | 8:30 PM | daily_reel.yml |

---

## 6. GitHub Actions Workflows — Verified

| File | Trigger (IST) | Purpose |
|---|---|---|
| `trading_bot.yml` | Every 5 min, 08:15–16:29, Mon–Fri | trading_bot.py — signal monitor |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 + Part 2 videos |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 + Community Post |
| `daily_reel.yml` | 8:30 PM daily | ZENO Reel → YouTube + Facebook |
| `daily-morning-reel.yml` | 7:00 AM daily | Morning Reel → YouTube + Facebook |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages + Facebook |
| `kids-daily.yml` | 8:00 AM daily | HerooQuest video → YouTube + Facebook Kids Page |
| `token_refresh.yml` | 1st + 20th of every month | Auto META token refresh (main + kids) |
| `keepalive.yml` | 11:59 PM IST Sun–Thu | Prevents GitHub disabling inactive workflows |

**Verified facts from workflow files:**
- `push` trigger REMOVED from trading_bot.yml — was causing midnight Telegram messages on commits
- Facebook Group removed from ALL workflows permanently
- Instagram removed from ALL workflows — artifact saved for manual post
- `daily-videos.yml` has a duration check — workflow FAILS if education video < 8 minutes
- Kids workflow uses separate secrets: `YOUTUBE_CREDENTIALS_KIDS`, `META_ACCESS_TOKEN_KIDS`, `FACEBOOK_KIDS_PAGE_ID`
- `token_refresh.yml` refreshes BOTH `META_ACCESS_TOKEN` and `META_ACCESS_TOKEN_KIDS`

---

## 7. File Map

### Core Infrastructure

| File | Role | Status |
|---|---|---|
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates | ✅ |
| `human_touch.py` | Anti-AI-penalty — 50+ hooks, phrases, TTS variation, SEO tags | ✅ |
| `token_refresh.py` | Auto META token refresh + GitHub Secret update + Telegram alert | ✅ |
| `indian_holidays.py` | Mode detection — NSE API + fallback | ✅ |
| `content_calendar.py` | Rotates topics: Options, Technical Analysis, Psychology | ✅ |

### Content Generators

| File | Role | Voice | Format | ai_client? | human_touch? |
|---|---|---|---|---|---|
| `generate_analysis.py` | 8-slide market analysis (Part 1) | Swara | 16:9 | ❌ Direct Groq | ❌ |
| `generate_education.py` | Education video (Part 2, 10+ min) | Swara | 16:9 | Unverified | Unverified |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | Swara | 9:16 | ❌ Direct Groq | ❌ |
| `generate_reel_morning.py` | Morning reel (7:00 AM) | Swara | 9:16 | Unverified | Unverified |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Neerja) | Madhur/Neerja | 9:16 | ❌ Direct Groq | ❌ |
| `generate_articles.py` | 4 SEO articles → Jekyll _posts | N/A | Jekyll MD | Unverified | Unverified |
| `generate_community_post.py` | YouTube community post | N/A | Text | Unverified | Unverified |
| `generate_kids_video.py` | HerooQuest kids video | Various | 16:9 | Unverified | N/A |

### Upload & Distribution

| File | Role | Status |
|---|---|---|
| `upload_youtube.py` | Uploads reel; `--type reel/morning` | ✅ |
| `upload_youtube_english.py` | English channel upload | 🔄 Phase 3 |
| `upload_facebook.py` | FB Page; `--meta-prefix morning/kids` | ✅ |
| `upload_kids_youtube.py` | HerooQuest YouTube upload | ✅ |

### Static Assets
- `public/image/` — `zeno_happy.png`, `zeno_sad.png`, `zeno_greed.png`, `zeno_thinking.png`
- `public/music/` — `bgmusic1.mp3`, `bgmusic2.mp3`, `bgmusic3.mp3` — rotated by weekday

---

## 8. AI Fallback Chain (Target — Partially Implemented)

```
Groq — llama-3.3-70b-versatile   (primary — fastest, free)
    ↓ fails
Google Gemini — gemini-2.0-flash  (secondary)
    ↓ fails
Claude — claude-haiku-4-5          (tertiary — best human-touch writing)
    ↓ fails
OpenAI — gpt-4o-mini               (quaternary)
    ↓ all fail
human_touch.py templates            (always works — zero downtime)
```

**Current reality:** `generate_analysis.py`, `generate_reel.py`, `generate_shorts.py` all call Groq directly. No fallback if Groq is down.

**Target pattern for all generators:**
```python
from ai_client import ai, img_client
from human_touch import ht, seo

response = ai.generate(prompt, content_mode=CONTENT_MODE, lang="hi")
data     = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
hook     = ht.get_hook(mode=CONTENT_MODE, lang="hi")
clean    = ht.humanize(raw_output, lang="hi")
tags     = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")
speed    = ht.get_tts_speed()   # pass to edge_tts rate param
```

---

## 9. Voice Assignments

| Voice ID | Gender | Used For |
|---|---|---|
| `hi-IN-MadhurNeural` | Male | Short 2 — authoritative trade setups |
| `hi-IN-SwaraNeural` | Female | ZENO Reel, Morning Reel, Analysis, Education |
| `en-IN-NeerjaNeural` | Female | Short 3 — Indian English, global macro pulse |
| `en-US-JennyNeural` | Female | English channel (Phase 3) |
| `en-US-GuyNeural` | Male | English Short 2 alternative (Phase 3) |

**TTS Speed — current state (hardcoded, not using human_touch):**
- `generate_shorts.py` — `+10%` (Madhur), `+12%` (Neerja)
- `generate_reel.py` — `+0%`
- `generate_analysis.py` — no rate param (TTS default)
- **Target:** replace all with `ht.get_tts_speed()` (0.95–1.05x variation)

---

## 10. Trading Bot — AppScript v14.0 + Python v13.4

### Overview

| Component | Role |
|---|---|
| AppScript v14.0 | Scans Nifty200, 10-gate filter, writes WAITING to AlertLog, stores memory in BotMemory sheet |
| trading_bot.py v13.4 | Monitors AlertLog every 5 min, WAITING→TRADED, TSL, exits, Telegram alerts |

**Status:** Paper trading. Followers take manual entry from Telegram signals.

---

### CRITICAL: v14.0 Migration — T4 Cell → BotMemory Sheet

**Breaking change from v13.x.** T4 cell in AlertLog is NO LONGER used for memory. All memory is in a dedicated `BotMemory` Google Sheet tab.

> ⚠️ AppScript v14.0 and trading_bot.py MUST be deployed together. Never upgrade one without the other. If you see T4 references in either file, that file is still v13.x.

**BotMemory sheet structure (columns A–E, row 1 = header):**

| Col | Field | Description |
|---|---|---|
| A | Key | Unique key string |
| B | Value | Stored value |
| C | UpdatedAt | IST timestamp |
| D | Symbol | NSE symbol (TRADE keys only, else blank) |
| E | KeyType | `FLAG` / `TRADE` / `STATE` |

**KeyType values:**
- `FLAG` — one-time daily flags (e.g. `2026-05-03_CLEANED`, `2026-05-03_BULLISH`) — auto-purged after 14 days
- `TRADE` — per-symbol keys: `{SYM}_CAP`, `{SYM}_MODE`, `{SYM}_SEC` — written by AppScript, read by trading_bot.py
- `STATE` — batch state: `_BATCH_START`, `_BATCH_CANDS`

**BotMemory helper functions (AppScript v14.0):**
```javascript
_bmLoad(ss)                          // load all rows → {key: {value, row}}
_bmGet(bm, key)                      // get value or ""
_bmSet(ss, bm, key, val, sym, ktype) // write or update in-place (no row shift)
_bmDel(ss, bm, key)                  // clear row content (no delete — avoids row-shift bugs)
_bmExists(bm, key)                   // boolean
_bmPurge(ss)                         // remove FLAG entries older than BM_PURGE_DAYS (14)
```

**Migration checklist (one-time — already done):**
1. T2 = NO (pause bot)
2. Clear all data rows in BotMemory (keep header A1:E1)
3. Deploy AppScript v14.0
4. Deploy new trading_bot.py
5. T2 = YES (resume)

---

### Google Sheets Structure

| Sheet | Purpose |
|---|---|
| `Nifty200` | Live data — 35 columns A–AI (see map below) |
| `AlertLog` | Active trades — 15 rows, 19 cols. T2=YES/NO switch |
| `History` | Closed trades — 18 cols A–R |
| `BotMemory` | Key-value memory — 5 cols A–E. Replaced T4 cell (v14.0) |

---

### Nifty200 Column Map (0-based, verified from AppScript v14.0)

```
r[0]  NSE_SYMBOL           r[1]  SECTOR
r[2]  CMP                  r[3]  %Change
r[4]  20_DMA               r[5]  50_DMA
r[6]  200_DMA              r[7]  SMA_Structure
r[8]  52W_Low              r[9]  52W_High
r[10] %up_52W_Low          r[11] %down_52W_High
r[12] %dist_20DMA          r[13] Avg_Volume_20D
r[14] Volume_vs_Avg%       r[15] FII_Buy_Zone
r[16] FII_Rating           r[17] Leader_Type
r[18] Signal_Score         r[19] FINAL_ACTION
r[20] RS                   r[21] Sector_Trend
r[22] Breakout_Stage       r[23] Retest%
r[24] Trade_Type           r[25] Priority_Score
r[26] Pivot_Resistance     r[27] VCP_Status
r[28] ATR14                r[29] Days_Since_Low
r[30] 52W_Breakout_Score   r[31] Sector_Rotation_Score (AF/col AF)
r[32] FII_Buying_Signal    r[33] Master_Score (col AH)
r[34] Sector_Rank (col AI) ← NEW column, added May 2026
```

**Column AI — Sector_Rank (r[34]):**
- Sheet formula: `=IFERROR(RANK(AF3, FILTER(AF$3:AF$179, B$3:B$179=B3), 0), "")`
- Meaning: Ranks each stock by Sector_Rotation_Score (AF) within its own sector. Rank 1 = strongest stock in that sector.
- **Current status: NOT used anywhere** — AppScript v14.0 reads up to r[33] only. trading_bot.py does not read Nifty200 directly. Not referenced in any Python file.
- **Potential future use:** Add conviction bonus `+1` for Sector_Rank=1 in `_convictionBonus()`, OR prefer Sector_Rank=1 in GATE 10 sector-concentration logic. Do NOT implement without explicit owner instruction.

---

### AlertLog Column Map (0-based)

```
A=0  Signal Time    B=1  Symbol        C=2  Live Price    D=3  Priority
E=4  Trade Type     F=5  Strategy      G=6  Stage         H=7  Initial SL
I=8  Target         J=9  RR Ratio      K=10 Status        L=11 Entry Price
M=12 Entry Time     N=13 Days in Trade O=14 Trailing SL   P=15 P/L%
Q=16 ATH Warning    R=17 Risk ₹        S=18 Position Size T=19 SYSTEM CONTROL
```

**T2 cell** = automation switch (YES = enabled) — still in AlertLog, NOT moved to BotMemory.

---

### CONFIG Values (AppScript v14.0)

```javascript
MAX_TRADES      : 5        // Max simultaneous TRADED rows
MAX_WAITING     : 10       // Max WAITING rows in AlertLog
MIN_PRIORITY    : 18       // Minimum score for Gate 2
MIN_RR          : 1.8      // Minimum reward:risk ratio
ATH_BUFFER_PCT  : 3.0      // Skip if within 3% of 52W high
MAX_CMP         : 5000     // Skip stocks above ₹5000

CAPITAL_HIGH    : 13000    // MasterScore≥28 AND AF≥10
CAPITAL_MED     : 10000    // MasterScore≥22 OR Accumulation Zone
CAPITAL_STD     :  7000    // Standard
MAX_DEPLOYED    : 45000    // Hard cap on total capital deployed

ATR_SL_INTRADAY   : 1.5   ATR_TGT_INTRADAY  : 2.0
ATR_SL_SWING      : 2.0   ATR_TGT_SWING     : 3.0
ATR_SL_POSITIONAL : 2.5   ATR_TGT_POSITIONAL: 4.0

BATCH_SIZE      : 60       // Rows per 5-min automated scan
LOG_ROWS        : 15       // Total rows in AlertLog data area
BM_PURGE_DAYS   : 14       // Auto-purge FLAG entries after 14 days
```

---

### Capital and Trade Count — Owner Decision Pending

**Current state (May 2026, after fresh clean start):** 0 open trades, full ₹45,000 available.

**Owner is considering:** increasing capital per trade and/or raising MAX_TRADES beyond 5.

Options to consider:
- **Option A — Raise capital tiers, keep MAX_TRADES=5:**
  Fewer, higher-conviction trades. E.g. CAPITAL_STD→₹10k, CAPITAL_MED→₹15k, CAPITAL_HIGH→₹20k. Still manageable TSL monitoring.
- **Option B — Raise MAX_TRADES to 7–8, keep similar capital per trade:**
  More diversification. Requires raising MAX_DEPLOYED to ₹70k–₹80k. More TSL monitoring load on bot.
- **Option C — MTF (Multi-Timeframe) split:**
  Separate capital pools for intraday (₹X) and positional (₹Y) with independent MAX_TRADES per type.

> 🔲 **Decision pending — owner to decide.** Do NOT change CONFIG values without explicit instruction. Once decided, update CONFIG in AppScript AND update this section AND update trading_bot.py if it has its own capital constants.

---

### AppScript v14.0 — 10 Scan Gates

**Market Regime:** Nifty50 CMP vs 20DMA → Bullish or Bearish.

**Bearish gate (all 4 required):** Leader_Type="Sector Leader" + AF≥5 + MasterScore≥22 + FII≠CAUTION/SELLING

**Gates (in order):**
1. FII SELLING → skip always
2. Market regime filter (bullish vs bearish path)
3. Late entry block (BREAKOUT CONFIRMED needs RS≥7)
4. Price validity (CMP>0, ATR>0, CMP≤₹5000)
5. Extension filter (breakout stages: check Retest%; others: %dist_20DMA≤8%)
6. Pivot resistance buffer (within 2% below pivot → skip; RETEST BUY exempt)
7. Volume filter (base stages ≥60%; others ≥120%; bullish only)
8. ATH buffer (within 3% of 52W high → skip)
9. Trade type (AVOID/NO TRADE → skip)
10. Sector concentration (max 2 per sector)

**Capital tiers:** ₹13k (MasterScore≥28 AND AF≥10) | ₹10k (MasterScore≥22 OR Accum.) | ₹7k (standard)

**Trade modes (BotMemory key `{SYM}_MODE`):** VCP | MOM | STD

**Sort order:** finalScore DESC, then ATR% ASC (prefer minimum SL within ±2 score points)

**Telegram from AppScript:** Regime alert (once/day, FLAG in BotMemory) + weekly summary + manual daily summary only. All trade alerts from trading_bot.py exclusively.

---

### Python Bot v13.4 — TSL Logic

**TSL Parameters (mode-aware, read from BotMemory):**
```python
TSL_PARAMS = {
    "VCP": {"breakeven":3.0, "lock1":5.0, "trail":8.0,  "atr_mult":2.0, "gap_lock":9.0},
    "MOM": {"breakeven":2.5, "lock1":4.5, "trail":7.0,  "atr_mult":1.8, "gap_lock":8.0},
    "STD": {"breakeven":2.0, "lock1":4.0, "trail":10.0, "atr_mult":2.5, "gap_lock":8.0},
}
```

**TSL progression (STD):** <2% gain → hold SL | 2–4% → breakeven | 4–10% → lock +2% | >10% → ATR trail | >8% gap → lock 50% of gap

**Hard exit rules:** Loss>5% → immediate exit | Min hold: 2 days swing, 3 days positional | 5-day cooldown after exit before same stock re-enters

**Daily message schedule (IST):**
- 08:45–09:15 → Good Morning (P/L + waiting count + sector context)
- 09:15–15:30 → Market hours (entry, TSL, exit alerts)
- 12:28–12:38 → Mid-day pulse
- 15:15–15:45 → Market close summary

**Telegram channels:**
- Basic (free) → market mood, closed signal result only
- Advance (₹499/mo) → full entry/exit, TSL, mid-day pulse
- Premium (bundle) → Advance + options CE candidate flag

**CE candidate flag (informational):** ATR%<1.5% → no flag | 1.5–2.5% → target +65%/SL -40% | >2.5% → target +50%/SL -35%

---

### History Sheet Columns (A–R)
```
A Symbol    B Entry Date  C Entry Price  D Exit Date   E Exit Price  F P/L%
G Result    H Strategy    I Exit Reason  J Trade Type  K Initial SL  L TSL at Exit
M Max Price N ATR@Entry   O Days Held    P Capital ₹   Q Profit/Loss ₹  R Options Note
```

---

## 11. Upload Chain

### Evening ZENO Reel (8:30 PM) — daily_reel.yml
```
generate_reel.py → reel_YYYYMMDD.mp4 + meta_YYYYMMDD.json
upload_youtube.py --type reel
upload_facebook.py
Instagram → MANUAL (artifact, 7-day retention)
```

### Morning Reel (7:00 AM) — daily-morning-reel.yml
```
generate_reel_morning.py → morning_reel_YYYYMMDD.mp4
upload_youtube.py --type morning
upload_facebook.py --meta-prefix morning
Instagram → MANUAL
```

### Daily Videos (7:30 AM / 9:30 AM) — daily-videos.yml
```
generate_analysis.py → Part 1 → YouTube (saves analysis_video_id.txt)
generate_education.py → Part 2 → YouTube (reads analysis_video_id.txt)
Duration check: FAIL if Part 2 < 480s (8 min) — required for mid-roll ads
```

### Shorts (11:30 AM / 1:30 PM) — daily-shorts.yml
```
generate_shorts.py → Short 2 + Short 3 → YouTube + Facebook Page
generate_community_post.py → YouTube Community Tab
(reads analysis_video_id.txt if present for Part 1 link)
```

---

## 12. Environment Variables & Secrets

### AI Providers
| Secret | Priority |
|---|---|
| `GROQ_API_KEY` | Primary |
| `GEMINI_API_KEY` | Secondary |
| `ANTHROPIC_API_KEY` | Tertiary |
| `OPENAI_API_KEY` | Quaternary |
| `HF_TOKEN` | Hugging Face (kids video) |

### Social — Main Channel
| Secret | Notes |
|---|---|
| `META_ACCESS_TOKEN` | Auto-refreshed 1st+20th each month |
| `META_APP_ID` + `META_APP_SECRET` | For token refresh |
| `FACEBOOK_PAGE_ID` | Main trading page |
| `FACEBOOK_GROUP_ID` | Kept in secrets but unused in all workflows |
| `YOUTUBE_CREDENTIALS` | Hindi channel OAuth JSON |
| `YOUTUBE_CREDENTIALS_EN` | English channel OAuth JSON (Phase 3) |

### Social — Kids Channel (HerooQuest)
| Secret | Notes |
|---|---|
| `META_ACCESS_TOKEN_KIDS` | Auto-refreshed with main token |
| `FACEBOOK_KIDS_PAGE_ID` | Page ID: 1021152881090398 |
| `YOUTUBE_CREDENTIALS_KIDS` | HerooQuest channel OAuth JSON |

### Telegram
`TELEGRAM_BOT_TOKEN` | `TELEGRAM_CHAT_ID` (free) | `CHAT_ID_ADVANCE` (₹499) | `CHAT_ID_PREMIUM` (bundle)

### Google / GCP
`GCP_SERVICE_ACCOUNT_JSON` — Search Console Indexing API + gspread

### Trading — Phase 4 (Added, Not Connected)
`DHAN_API_KEY` | `DHAN_API_SECRET` | `DHAN_CLIENT_ID` | `DHAN_PIN` | `DHAN_TOTP_KEY`

### General
`GH_TOKEN` — GitHub API token for secret updates in token_refresh.py

---

## 13. Known Issues & Current State

| Issue | Status | Notes |
|---|---|---|
| Instagram API | ❌ Permanently removed | Manual post — download artifact, post from phone |
| Facebook Group | ❌ Permanently removed | `FACEBOOK_GROUP_ID` secret exists but unused |
| Short 3 voice | ✅ Corrected | `en-IN-NeerjaNeural` (not Swara) — gives global English appeal |
| generate_analysis.py `.history()` | ✅ Acceptable | Runs at 7:30 AM pre-market — previous day close is correct |
| 3 generators use direct Groq | ⚠️ No fallback | If Groq down, content fails — upgrade to ai_client is Task 1–3 |
| Column AI (Sector_Rank) | 🔵 Not yet used | Added to sheet, not read by any script yet — see Task 7 |
| Capital/MAX_TRADES config | 🔲 Decision pending | Owner to decide — do not change without instruction |
| YouTube Community Tab | ⚠️ Needs 500+ subs | Below threshold: saves to txt file, no crash |
| AppScript + bot version pair | ✅ v14.0 + v13.4 | Both must use BotMemory — never deploy one without the other |

---

## 14. Technical Standards

### The "Full Code" Rule
> Always provide the **complete file content** when modifying any file. No partial snippets or diffs. Write the entire file.

```
Standard prompt: "Refer to SYSTEM.md for architecture. Task: [X]. Provide FULL code for any modified file."
```

### Dependency Pins

| Package | Version | Reason |
|---|---|---|
| `Pillow` | `>=10.3.0` | LANCZOS resampling |
| `imageio` | `==2.9.0` | Prevents MoviePy crashes |
| `moviepy` | `==1.0.3` | Force reinstall — newer versions break audio |
| `yfinance` | Latest | `fast_info['last_price']` for live; `.history()` OK pre-market |
| `PyNaCl` | Latest | GitHub Secret encryption in token_refresh.py |
| `gspread` | Latest | Google Sheets access |
| `oauth2client` | Latest | GCP service account auth |
| `pytz` | Latest | IST timezone |
| `google-generativeai` | Latest | Gemini fallback |
| `anthropic` | Latest | Claude fallback |
| `openai` | Latest | OpenAI fallback |

### Video Formats
- **16:9** — 1920×1080 — Analysis + Education
- **9:16** — 1080×1920 — Shorts, Morning Reel, ZENO Reel

---

## 15. Priority Task List for Future AI

> Read the actual source file before editing. Do not rely on memory. Always provide full file content.

### 🔴 HIGH PRIORITY

**Task 1: Upgrade generate_analysis.py → ai_client + human_touch**
- Replace `from groq import Groq` + direct call with `from ai_client import ai` + `ai.generate_json()`
- Add `from human_touch import ht, seo`
- Apply `ht.humanize()` on slide content, `ht.get_hook()` for opening, `seo.get_video_tags()` for tags
- Replace default TTS with `ht.get_tts_speed()`
- Keep `.history()` for market data — correct at 7:30 AM pre-market

**Task 2: Upgrade generate_reel.py → ai_client + human_touch**
- Same pattern as Task 1
- Apply `ht.humanize()` on `audio_script`
- Replace `rate="+0%"` with `ht.get_tts_speed()`

**Task 3: Upgrade generate_shorts.py → ai_client + human_touch**
- Same pattern as Task 1
- Apply `ht.humanize()` on both Short 2 and Short 3 scripts
- Replace `rate="+10%"` and `rate="+12%"` with `ht.get_tts_speed()`
- Replace manual tag lists with `seo.get_video_tags()`

### 🟡 MEDIUM PRIORITY

**Task 4: Verify + upgrade generate_education.py**
- Read file first (not yet verified)
- Check ai_client + human_touch usage
- Confirm 22 slides × 80–100 words → 10–12 min
- Confirm reads `analysis_video_id.txt` and links Part 1

**Task 5: Verify + upgrade generate_reel_morning.py**
- Read file first, check and upgrade if needed

**Task 6: Verify generate_articles.py + generate_community_post.py**
- Read both, check ai_client + human_touch, upgrade if needed

**Task 7: Implement Column AI (Sector_Rank) — explicit owner approval required**
- r[34] = `RANK(AF, FILTER same sector, 0)` — Rank 1 = best stock in sector
- Option A: +1 conviction bonus for Sector_Rank=1 in `_convictionBonus()`
- Option B: GATE 10 logic — when sector already has 1 stock, only add Sector_Rank=1
- Read AppScript v14.0 before writing — do NOT implement without explicit instruction

**Task 8: Capital / MAX_TRADES config update — owner decision required**
- See Section 10 — Decision Points
- Once owner decides: update CONFIG in AppScript + update this doc + check trading_bot.py constants

### 🔵 FUTURE (Phase 3–4)

**Task 9: English Channel (Phase 3)**
- `generate_english.py` + `upload_youtube_english.py`
- Voices: `en-US-JennyNeural` (female) + `en-US-GuyNeural` (male)

**Task 10: Disney 3D Reel — Gemini Veo API (Phase 3)**
- Hook already in `ai_client.py` via `img_client` — swap in when Veo is accessible

**Task 11: Dhan Live Trading (Phase 4)**
- All secrets added, not connected
- Activate only after backtest: 30–40 paper trades, win rate >35%
- Max ₹45,000 deployment (₹5k buffer)
- CE execution requires Dhan API + lot size data

---

## 16. Data Flow

```
Market hours (Mon–Fri, 9:15–15:30 IST)
└── trading_bot.yml → trading_bot.py v13.4
    └── Reads BotMemory: {SYM}_CAP, {SYM}_MODE, {SYM}_SEC
    └── AlertLog: WAITING→TRADED → TSL → Exit → History

AppScript v14.0 (time trigger every 5 min OR manual)
└── Nifty200 scan (60 rows/run batched) → 10-gate filter
└── Writes WAITING to AlertLog
└── Writes {SYM}_CAP, {SYM}_MODE, {SYM}_SEC to BotMemory (KeyType=TRADE)
└── Regime alert → Telegram (FLAG in BotMemory, once/day)
└── Morning cleanup 9:05–9:15 IST (FLAG in BotMemory)
└── Weekly summary Friday 15:15 (FLAG in BotMemory)

7:00 AM → daily-morning-reel.yml → generate_reel_morning.py → YouTube + Facebook
7:30/9:30 AM → daily-videos.yml → generate_analysis.py + generate_education.py → YouTube
8:00 AM → kids-daily.yml → generate_kids_video.py → YouTube + Facebook Kids
10/11:30 AM → daily-articles.yml → generate_articles.py → GitHub Pages + Facebook
11:30/1:30 PM → daily-shorts.yml → generate_shorts.py + generate_community_post.py → YouTube + Facebook
8:30 PM → daily_reel.yml → generate_reel.py → YouTube + Facebook
11:59 PM Sun–Thu → keepalive.yml → commit .keepalive
1st + 20th monthly → token_refresh.yml → META tokens (main + kids)
```

---

## 17. Website

| Page | URL | Purpose |
|---|---|---|
| Home | ai360trading.in | Main landing |
| Swing Dashboard | /swing-dashboard/ | Live AlertLog — active swing signals (3–15 day holds) |
| Positional Picks | /positional-picks/ | Separate sheet — fundamental+technical positional signals (weeks–months) |
| Trading Academy | /tutorial-videos/ | Tutorial videos |
| Membership | /membership/ | Paid Telegram plans |

**Hosting:** GitHub Pages, Jekyll, master branch `_posts/`
**Auto-commit:** `daily-articles.yml` (git user: AI360-Automation)
**Instant indexing:** `GCP_SERVICE_ACCOUNT_JSON`

---

## 18. Social Media

| Platform | Handle | Notes |
|---|---|---|
| 📣 Telegram Free | @ai360trading | Market mood, signal results |
| 📣 Telegram Advance | ai360trading_Advance | ₹499/mo — full signals + TSL |
| 📣 Telegram Premium | ai360trading_Premium | Bundle — Advance + options hints |
| ▶️ YouTube | @ai360trading | |
| 📸 Instagram | @ai360trading | Manual post only |
| 📘 Facebook Page | facebook.com/ai360trading | |
| 🦸 Kids YouTube | HerooQuest | |
| 📘 Kids Facebook | HerooQuest Page (1021152881090398) | |

---

## 19. Phase Roadmap

| Phase | Status | Remaining Work |
|---|---|---|
| Phase 1 | ✅ Complete | ai_client.py, human_touch.py, token_refresh.py, generate_reel_morning.py |
| Phase 2 | ✅ Infrastructure done | Generator upgrades (Tasks 1–6) still pending |
| Phase 3 | 🔄 In Progress | English channel, Sector_Rank integration, Gemini Veo |
| Phase 4 | 📋 Planned | Dhan live trading after backtest validation |

---

## 20. Testing

```bash
# Force content mode via workflow_dispatch
content_mode = market | weekend | holiday

# Trading bot log patterns
[REGIME] Nifty CMP ₹22679 vs 20DMA ₹23547 → BEARISH
[TSL] NSE:ONGC [STD]: ₹280.60→₹285.20
[DONE] 15:20:01 IST

# AppScript Logger patterns
[REGIME] CMP=22679 20DMA=23547 Bullish=false
[CAND] NSE:ADANIPOWER | Score=24 | ATR%=2.1 | ₹10000 | STD | AF=8.2 | Qty=64
[BM PURGE] Removed old flag: 2026-04-15_BULLISH
[DONE] Traded=0 | Waiting=5 | Bullish=true

# BotMemory check
Open BotMemory sheet — TRADE keys should exist for each WAITING stock
e.g. ONGC_CAP=10000, ONGC_MODE=STD, ONGC_SEC=Energy
If missing → run MANUAL SYNC

# Automation switch
AlertLog → cell T2 → "YES" = enabled
```

---

*Verified: May 2026 — Claude Sonnet 4.6*
*Files verified: generate_analysis.py, generate_reel.py, generate_shorts.py, AppScript v14.0, all 9 workflow yml files, website pages (swing-dashboard, positional-picks)*
*Files not yet verified: generate_education.py, generate_reel_morning.py, generate_articles.py, generate_community_post.py, ai_client.py, human_touch.py, trading_bot.py*
*Update this file whenever architecture, secrets, platform status, or trading logic changes.*
