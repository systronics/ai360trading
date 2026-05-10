# AI360Trading — Master System Documentation

**Last Updated:** May 11, 2026 — Trading Bot v14.0 + AppScript v15.1
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 🔄 In Progress | Phase 4 (Dhan Live) Planned
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
| YouTube English | 🔄 Building | Phase 3 — auto-translated separate channel |
| YouTube Shorts | ✅ Auto | Short 2 + Short 3 working |
| YouTube Community Posts | ✅ Built | generate_community_post.py — 12:00 PM daily |
| YouTube Reels | ✅ Auto | ZENO reel (8:30 PM) working |
| YouTube Morning Reel | ✅ Auto | 7:00 AM reel (generate_reel_morning.py) working |
| Facebook Page | ✅ Auto | Posts, reels, article shares all working |
| Facebook Group | ❌ Broken | Missing `publish_to_groups` token scope — see Section 11 |
| Instagram | ⚠️ Partial | Upload chain built; `INSTAGRAM_ACCOUNT_ID` secret needed |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | 3-channel system — Basic/Advance/Premium (paper trading) |

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
| **Total** | **12 pieces/day** | — | — | — |

---

## 5. GitHub Actions Workflows

| File | Trigger (IST) | Purpose | Mode-Aware |
|---|---|---|---|
| `main.yml` | Every 5 min, 08:15–16:29, Mon–Fri | `trading_bot.py` — Nifty200 signals | ✅ Auto-skips weekends/holidays |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 (analysis) + Part 2 (education) | ✅ |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 + Community Post | ✅ |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning Reel + ZENO Reel | ✅ |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages | ✅ |
| `token_refresh.yml` | Every 50 days | Auto META token refresh | N/A |
| `keepalive.yml` | Periodic | Prevents GitHub disabling inactive workflows | N/A |

### GitHub Secrets (as of May 2026)

| Secret | Used By | Purpose |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | trading_bot.py + AppScript | Bot token for all Telegram messages |
| `CHAT_ID_BASIC` | trading_bot.py | Free channel — market mood only |
| `CHAT_ID_ADVANCE` | trading_bot.py | ₹1000/mo — full trade details |
| `CHAT_ID_PREMIUM` | trading_bot.py | ₹3000/mo — Advance + CE candidate flag |
| `GCP_SERVICE_ACCOUNT_JSON` | trading_bot.py | Google Sheets access |
| `ANTHROPIC_API_KEY` | ai_client.py | Claude fallback |
| `GEMINI_API_KEY` | ai_client.py | Gemini secondary AI |
| `GROQ_API_KEY` | ai_client.py | Primary AI (fastest, free) |
| `OPENAI_API_KEY` | ai_client.py | GPT-4o-mini quaternary fallback |
| `DHAN_API_KEY` | Phase 4 | Live order placement (not active yet) |
| `DHAN_API_SECRET` | Phase 4 | Live order placement (not active yet) |
| `META_ACCESS_TOKEN` | upload_facebook.py, upload_instagram.py | Facebook + Instagram upload |
| `YOUTUBE_CREDENTIALS` | upload_youtube.py | Hindi channel upload |
| `YOUTUBE_CREDENTIALS_KIDS` | upload_youtube_english.py | English channel upload |

> ⚠️ AppScript uses Script Properties (not GitHub secrets) — set via Extensions → Apps Script → Project Settings → Script Properties. Keys: `TELEGRAM_BOT_TOKEN`, `CHAT_ID_BASIC`, `CHAT_ID_ADVANCE`, `CHAT_ID_PREMIUM`

---

## 6. Complete File Map

### Core Infrastructure

| File | Role | Status |
|---|---|---|
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates fallback | ✅ |
| `human_touch.py` | Anti-AI-penalty layer — 50+ hooks, personal phrases, TTS variation, SEO tags | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update + Telegram alert | ✅ |

### Core Content Generation

| File | Role | Status |
|---|---|---|
| `trading_bot.py` | Signal monitor + TSL manager + 3-channel Telegram alerts | ✅ v14.0 |
| `generate_shorts.py` | Short 2 + Short 3 | ✅ |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ✅ |
| `generate_reel_morning.py` | Morning reel (7:00 AM) | ✅ |
| `generate_analysis.py` | 8-slide market analysis video (Part 1) | ✅ |
| `generate_education.py` | Educational deep-dive video (Part 2) | ✅ |
| `generate_articles.py` | 4 SEO articles daily → Jekyll _posts | ✅ |
| `generate_community_post.py` | YouTube daily community text post | ✅ |

### Upload & Distribution

| File | Role | Status |
|---|---|---|
| `upload_youtube.py` | Uploads reel; saves youtube_video_id + public_video_url to meta | ✅ |
| `upload_youtube_english.py` | Uploads to English channel | 🔄 Phase 3 |
| `upload_facebook.py` | Uploads reel to FB Page; shares to Group; posts articles | ✅ |
| `upload_instagram.py` | Auto-uploads via Meta API | ✅ |

---

## 7. AI Fallback Chain

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

---

## 8. Trading Bot Architecture

### Overview

| Component | File | Version | Role |
|---|---|---|---|
| AppScript | Google Sheets bound script | v15.1 | Scans Nifty200, applies 10 gates, writes WAITING candidates to AlertLog, stores BotMemory |
| Python Bot | `trading_bot.py` | v14.0 | Monitors AlertLog every 5 min, WAITING→TRADED, TSL updates, exit logic, 3-channel Telegram |

**Current status:** Paper trading. Followers receive Telegram signals and take manual entry.
**Phase 4:** Dhan API integration after 30–40 paper trades validated in History sheet.

---

### Google Sheets Structure

| Sheet | Purpose |
|---|---|
| `Nifty200` | Live data for ~211 stocks — CMP, DMAs, FII data, signals, scores (35 cols A–AI) |
| `AlertLog` | Active + waiting trades — 21 rows, 19 cols. T2=YES/NO switch. T4=Python-only state string |
| `History` | Closed trade log — 18 cols A–R |
| `BotMemory` | Key-value store — AppScript writes _CAP/_MODE/_SEC/_RANK per stock. Python reads from here |

> ⚠️ PriceCache and TempPriceCalc sheets deleted in v15.0 freshCleanStart — do not recreate them.

---

### AlertLog Column Map (0-based)

```
A=0  Signal Time    B=1  Symbol        C=2  Live Price     D=3  Priority Score
E=4  Trade Type     F=5  Strategy      G=6  Breakout Stage H=7  Initial SL
I=8  Target         J=9  RR Ratio      K=10 Trade Status   L=11 Entry Price
M=12 Entry Time     N=13 Days in Trade O=14 Trailing SL    P=15 P/L%
Q=16 ATH Warning    R=17 Risk ₹        S=18 Position Size  T=19 SYSTEM CONTROL
```

**T2** = automation on/off switch (set YES to enable)
**T4** = Python-only memory string (TSL, MAX, LP, ATR, EXDT, AM/PM/MD flags)
**BotMemory SHEET** = _CAP, _MODE, _SEC, _RANK per stock (written by AppScript, read by Python)

---

### Nifty200 Column Map (0-based)

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
r[30] 52W_Breakout_Score   r[31] Sector_Rotation_Score (AF)
r[32] FII_Buying_Signal    r[33] Master_Score
r[34] Sector_Rank (AI)     ← added v14.1/v15.0
```

**Stock list:** ~211 rows (rows 3–213). All Sector_Rank formulas use `$500` range to handle future additions without hardcoded row limits.

---

### Nifty200 Formula Reference

All formulas audited and fixed May 2026. Key formulas:

| Column | Formula Pattern | Notes |
|---|---|---|
| C (CMP) | `GOOGLEFINANCE(A3,"price")` with previousclose fallback | ✅ |
| D (%Change) | `GOOGLEFINANCE(A3,"changepct")` | ✅ |
| E (20_DMA) | `AVERAGE(INDEX(GOOGLEFINANCE(...,TODAY()-35,TODAY()),0,2))` | -35 days (was -30, fixed for holiday buffer) |
| F (50_DMA) | Same pattern, `-80` days | Fixed from -70 |
| G (200_DMA) | Same pattern, `-320` days | Fixed from -300 |
| N (Avg_Vol) | `AVERAGE(INDEX(GOOGLEFINANCE(A3,"volume",...),0,2))` | Index col 2 only — fixed Bug 1 (date serial number contamination) |
| O (Vol_vs_Avg%) | `(GOOGLEFINANCE(A3,"volume")-N3)/N3*100` | Negative = below average (correct — handled by Gate 7) |
| P (FII_Buy_Zone) | Overheated checked BEFORE Mild Correction | Fixed Bug 2 (Overheated was unreachable) |
| AC (ATR14) | `AVERAGE(ARRAYFORMULA(INDEX(high,2,2,14)-INDEX(low,2,2,14)))` | 21 calendar days → 14 trading days |
| AI (Sector_Rank) | `RANK(AF3, FILTER(AF$3:AF$500, B$3:B$500=B3, AF$3:AF$500<>""), 0)` | $500 — no hardcoded row limit |

---

### AppScript v15.1 — Key Logic

**Scan capacity:** MAX_TRADES=8, MAX_WAITING=10, MAX_MOM_SLOTS=3, LOG_ROWS=21

**Configuration changes vs v13.x:**

| Setting | Old | New | Reason |
|---|---|---|---|
| MIN_PRIORITY | 18 | 15 | More stocks qualify |
| MAX_CMP | ₹5,000 | ₹8,000 | CUMMINSIND, HAL eligible |
| ATH_BUFFER_PCT | 3.0% | 1.0% | Breakout stages exempt anyway |
| BASE_STAGE_MIN_VOL | 60% | 40% | More accumulation stocks qualify |
| LATE_ENTRY_MIN_RS | 7 | 5 | Less strict for breakout confirmed |
| LOG_ROWS | 15→18 | 21 | 8 traded + 10 waiting + 3 momentum |
| MORNING_VOL_BYPASS_UNTIL | — | 10:30 | New — bypass volume gate before 10:30 AM |

**Market regime:** Nifty50 CMP ≥ 20DMA → BULLISH. Below → BEARISH.

**10 scan gates (in order):**

| Gate | Condition | v15.1 Change |
|---|---|---|
| 1 | FII SELLING → skip always | Unchanged |
| 2 | Market regime filter | Unchanged |
| 3 | Late entry: BREAKOUT CONFIRMED needs RS≥5 | Relaxed from 7 |
| 4 | Price validity: CMP>0, ATR>0, CMP≤₹8000 | MAX_CMP raised from 5000 |
| 4b | Result/Event day: skip if \|%Change\|>6% (result) or >15% (corp action) | NEW v15.0 |
| 5 | Extension: breakout→retest check, non-breakout→distDMA≤8% | Unchanged |
| 6 | Pivot resistance buffer — EXEMPT for breakout stages | FIXED v15.0 |
| 7 | Volume filter — BYPASS before 10:30 AM, breakout stages always exempt | FIXED v15.1 |
| 8 | ATH buffer 1% — EXEMPT for breakout stages | FIXED v15.0 |
| 9 | Trade type: AVOID/NO TRADE → skip | Unchanged |
| 10 | Sector concentration: max 2 per sector | Unchanged |

> **Critical Gate 7 fix (v15.1):** `isMorning` computed OUTSIDE `volVsAvg > 0` check. Before 10:30 AM entire volume gate skipped. After 10:30 AM: breakout stages exempt, base stages need ≥40%, others need ≥120%. Negative volume after 10:30 = below average = correctly blocked.

**Gate 6 + Gate 8 fix (v15.0):** BREAKOUT CONFIRMED and BREAKOUT ALERT stages exempt from both pivot resistance and ATH buffer checks. These stocks ARE supposed to be near 52W high breaking through resistance. This fix unlocked BHEL, CGPOWER, FEDERALBNK, NTPC, JSWENERGY, TITAN etc. which were previously blocked.

**Signal inference (#N/A fallback):** When Google Sheet formulas return #N/A (refresh lag), AppScript infers signal from Breakout_Stage and FII_Buy_Zone. Prevents all stocks being blocked by Gate 2 on formula errors.

**Sector rank integration (v14.1+):**
- Rank written to BotMemory as `{sym}_RANK` (read by Python for CE flag gating)
- Rank 1–3 → +2 conviction bonus, wider swing target (ATR×3.5 vs 3.0)
- Rank 1–5 → preferred tiebreaker in sort

**Momentum scan (v15.0 NEW):** Runs after main scan, bullish market + before 11:30 AM only:
- Stock must be up >2.5% on day with volume >200% of 20D average
- Strong Bull or Bull SMA structure
- Result day filter applied (skip if >6% change)
- Max 3 momentum slots (separate from main 10 waiting slots)
- Capital: CAPITAL_STD (₹7,000), mode: MOM

**NSE Holiday list (2026):** Hardcoded in AppScript. Skip scan on holidays and weekends.

**Capital tiers:**
- ₹13,000 — MasterScore≥28 AND AF≥10 (high conviction)
- ₹10,000 — MasterScore≥22 OR Accumulation Zone (medium conviction)
- ₹7,000 — standard

**Trade modes (written to BotMemory):**
- VCP — VCP<0.04 + pre-breakout stage (Near Breakout/Building Momentum/Correction Base)
- MOM — Strong Bull + RS≥6
- STD — everything else (default in bear market)

**BotMemory keys per stock (written by AppScript, read by Python):**
- `{sym}_CAP` — capital tier
- `{sym}_MODE` — trade mode (VCP/MOM/STD)
- `{sym}_SEC` — sector name
- `{sym}_RANK` — sector rank (1–N within sector)

**Sort order:** finalScore DESC → rank 1–5 preferred at tie (within ±2 pts) → ATR% ASC tiebreaker.

**Telegram (AppScript sends):** Regime alert (once/day) + Weekly summary → ADVANCE + PREMIUM channels only. Basic channel not used by AppScript.

**testTelegram() function:** Added to menu as 📡 TEST TELEGRAM. Sends labelled test message to all 3 channels regardless of market hours. Use to verify channel connectivity anytime.

---

### Python Bot v14.0 — Key Logic

**TSL Parameters (mode-aware — unchanged):**

```python
TSL_PARAMS = {
    "VCP": { "breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0 },
    "MOM": { "breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0 },
    "STD": { "breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0 },
}
```

**TSL progression (STD):**
- Gain < 2% → hold initial SL
- Gain 2–4% → move to breakeven
- Gain 4–10% → lock at entry +2%
- Gain > 10% → ATR trail (2.5× ATR below CMP)
- Gain > 8% gap-up → lock 50% of gap

**v14.0 Critical Fixes:**

| Fix | Old | New |
|---|---|---|
| Telegram channel swap | CHAT_ADVANCE read CHAT_ID_PREMIUM env | FIXED — correct env var mapping |
| Channel differentiation | Same message to Advance and Premium | Advance = full details, Premium = Advance + CE flag |
| BotMemory source | Read _CAP/_MODE from T4 string | Read from BotMemory SHEET (AppScript writes here) |
| MAX_TRADES | 5 | 8 (matches AppScript) |
| Result day filter | None | Skip entry if \|%Change\|>6% on that stock |
| Holiday check | Relied on cron only | Python checks NSE_HOLIDAYS_2026 set independently |
| BOT_MODE handling | Not implemented | test_telegram / daily_summary / weekly_summary modes added |

**Env var names (MUST match GitHub secrets exactly):**
```
TELEGRAM_BOT_TOKEN  ← not TELEGRAM_TOKEN
CHAT_ID_BASIC       ← not TELEGRAM_CHAT_ID
CHAT_ID_ADVANCE     ← correct
CHAT_ID_PREMIUM     ← correct
GCP_SERVICE_ACCOUNT_JSON ← correct
```

**3-channel message differentiation:**

| Channel | Good Morning | Entry Alert | Exit Alert | CE Flag |
|---|---|---|---|---|
| Basic | Market mood + count only | ❌ | Result only (WIN/LOSS%) | ❌ |
| Advance | Full trade P/L + SL/Target | Full entry details | Full exit details | ❌ |
| Premium | Same as Advance | Same + CE candidate | Same as Advance | ✅ rank≤5 only |

**CE candidate flag:** Informational only (not live execution). Shows on Premium entry alerts when:
- Market is bullish
- ATR% > 1.5%
- BotMemory _RANK ≤ 5 (sector leaders only)
- ATR% < 1.5% → no flag (premium decay risk)
- ATR% 1.5–2.5% → normal mover: target +65%, SL -40%
- ATR% > 2.5% → fast mover: target +50%, SL -35%

**T4 Python-only state (comma-separated key=value):**
- `{sym}_TSL_NNNN` — trailing SL × 100
- `{sym}_MAX_NNNN` — max price seen × 100
- `{sym}_LP_NNNN` — last price × 100
- `{sym}_ATR_NNNN` — ATR at entry × 100
- `{sym}_EXDT_YYYY-MM-DD` — exit date (for 5-day cooldown)
- `{TODAY}_AM` — good morning sent flag
- `{TODAY}_MD` — mid-day pulse sent flag
- `{TODAY}_PM` — market close sent flag

**Daily message schedule:**
- 08:45–09:29 → Good Morning (open trades P/L + waiting count + sector context)
- 09:15–15:30 → Market hours (entry alerts, TSL updates, exit alerts, min-hold warnings)
- 12:28–12:38 → Mid-day pulse (P/L snapshot of all open trades)
- 15:15–15:45 → Market close summary (exits today + overnight holds)

**Hard exit rules:**
- Loss > 5% → hard loss exit (immediate, no min-hold check)
- Min hold: 2 days swing, 3 days positional (prevents TSL whipsaw)
- 5 trading day cooldown after exit before re-entry same stock

**BOT_MODE (GitHub Actions workflow_dispatch):**
- `trade` → normal trading cycle (default)
- `test_telegram` → sends labelled test to all 3 channels (works outside market hours)
- `daily_summary` → sends trade count summary (works outside market hours)
- `weekly_summary` → sends manual weekly trigger

---

### History Sheet Columns (A–R)

```
A  Symbol      B  Entry Date   C  Entry Price  D  Exit Date
E  Exit Price  F  P/L%         G  Result        H  Strategy
I  Exit Reason J  Trade Type   K  Initial SL    L  TSL at Exit
M  Max Price   N  ATR at Entry O  Days Held     P  Capital ₹
Q  Profit/Loss ₹               R  Options Note
```

**Phase 4 readiness rule:** Minimum 30 completed trades in History sheet before enabling Dhan live API.
**Current count:** 1 (SBIN, -7.30% loss, May 8 2026 — result day entry, prevented by v15.0 filter going forward)

---

## 9. Critical Upload Chain

Scripts must run in this exact order. Each one feeds data to the next:

### Evening ZENO Reel (8:30 PM)

```
generate_reel.py
    └── output/reel_YYYYMMDD.mp4
    └── output/meta_YYYYMMDD.json  ← created here (public_video_url written after upload)
         ↓
upload_youtube.py
    └── uploads to Hindi channel
    └── writes youtube_video_id + public_video_url to meta JSON
         ↓
upload_facebook.py
    └── reads public_video_url from meta JSON
    └── uploads to FB Page as reel
    └── shares article links to FB Group (if token has publish_to_groups scope)
         ↓
upload_instagram.py
    └── reads public_video_url from meta JSON
    └── posts to Instagram via Meta Graph API
```

---

## 10. Deployment Checklist (After Any Code Change)

### AppScript Changes
1. Open Google Sheet → Extensions → Apps Script
2. Replace all code with new version
3. Save (Ctrl+S)
4. Run `freshCleanStart` from 🚀 AI360 TRADING menu (if AlertLog structure changed)
5. Set T2 = YES in AlertLog cell T2
6. Run `testTelegram` → verify all 3 channels receive labelled messages
7. Run `MANUAL SYNC` → verify AlertLog fills with WAITING candidates
8. Check Apps Script Executions log for `[CAND]` lines

### trading_bot.py Changes
1. Push to GitHub master branch
2. Go to Actions → Trading Bot workflow → Run workflow → mode: `test_telegram`
3. Check all 3 channels receive messages
4. Check Actions log for `[MODE] test_telegram` and `[TEST] ✅`
5. Next market day: check Good Morning message arrives at 8:45 AM IST

### Full System Check (After Major Update)
1. Nifty200 sheet → find CGPOWER → verify all 35 columns have values
2. Column AI (Sector_Rank) = 1 for CGPOWER ✅
3. Column AC (ATR14) = ₹40 approx ✅
4. Column O (Vol_vs_Avg%) = number (not 46000+) ✅
5. Column P (FII_Buy_Zone) shows "Momentum Zone" for stocks 5% above 20DMA ✅
6. Run MANUAL SYNC → check CGPOWER, BHEL, BANDHANBNK appear in WAITING
7. Run testTelegram → all 3 channels ✅
8. GitHub Actions test_telegram mode ✅

---

## 11. Known Issues & Planned Fixes

| Issue | Status | Fix |
|---|---|---|
| Facebook Group token missing `publish_to_groups` scope | ❌ Open | Re-authorize META app with group scope |
| Instagram live verify | ⚠️ Untested | Run upload_instagram.py manually once |
| YouTube English channel (generate_english.py) | 🔄 Phase 3 | Highest ROI next step — USA/UK CPM 3–5x |
| Dhan API live trading | 📋 Phase 4 | Need 30+ paper trades in History first |
| Zerodha API | 📋 Phase 4 | Alternative to Dhan — credentials ready |
| NSE Corporate Actions API | 📋 Planned | Auto-detect result/event days via NSE event-calendar API |

---

## 12. Emergency Procedures (For Family)

> If the system stops sending Telegram messages:

**Step 1:** Open Google Sheet → Check cell T2 = YES
**Step 2:** Run 📡 TEST TELEGRAM from menu → if no message → check Script Properties tokens
**Step 3:** Go to GitHub → Actions → check for red ❌ failed runs → click to see error
**Step 4:** If error says "quota exceeded" → wait 1 hour, system auto-retries
**Step 5:** If error says "token expired" → run token_refresh.py workflow manually
**Step 6:** If completely stuck → Telegram message will arrive from bot with error details

> The system sends its own error alerts to the Advance channel automatically when trading_bot.py crashes. Your family doesn't need to check GitHub logs.

**To verify system is alive:** Run 📡 TEST TELEGRAM from Google Sheet menu anytime, any day, market open or closed.

---

## 13. Phase Roadmap

| Phase | Status | Description |
|---|---|---|
| Phase 1 | ✅ Complete | Core infrastructure — AI client, content gen, all platforms |
| Phase 2 | ✅ Complete | All content upgraded — Hindi channel fully automated |
| Phase 3 | 🔄 In Progress | English channel + Instagram verify + Facebook Group fix |
| Phase 4 | 📋 Planned | Dhan/Zerodha live API — after 30+ paper trades validated |
| Phase 5 | 💭 Future | Options auto-execution (CE/PE) when CE flag triggers |

---

*AI360 Trading — Built to run forever. Zero maintenance. Pure automation.*
*Last updated by Claude Sonnet 4.6 on May 11, 2026*
