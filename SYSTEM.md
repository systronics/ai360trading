# AI360 TRADING — SYSTEM.md
# Complete System Reference — Updated May 2026
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## SECTION 1 — CURRENT VERSIONS (DEPLOYED)

| Component | Version | Status |
|---|---|---|
| AppScript | v15.4 | ✅ Deployed — Base Entry + Options |
| Python Bot | v14.0 | ⚠️ Local only — v13.5 still on GitHub |
| Google Sheet | Live | ✅ Ai360tradingAlgo |
| Website | Live | ✅ ai360trading.in |
| Kids Channel | Live | ✅ HerooQuest |

**Repo:** https://github.com/systronics/ai360trading
**Sheet:** https://docs.google.com/spreadsheets/d/1fPNGL6AHs-7M-oC22zILg9FlyWi-7DF9NoVVqZQs2vk

---

## SECTION 2 — SYSTEM OVERVIEW

AI360Trading is a fully automated trading signal system for Indian markets (Nifty200 universe). It scans 200+ stocks every 5 minutes, applies 11 gates of quality filtering, and delivers signals to 3 Telegram channels (Basic/Advance/Premium) with different detail levels.

**Two entry types (v15.4):**

### 1. Breakout Entry (original)
- Enter when stock breaks out of base at momentum
- Stage: BREAKOUT ALERT or BREAKOUT CONFIRMED
- SL = 2×ATR | Target = 4×ATR | RR = 2.0
- Options: BUY CE if F&O liquid + VIX < 18 + 20+ days expiry

### 2. Base Entry (new v15.4)
- Enter BEFORE breakout — at the accumulation base
- Stage: Correction Base / Building Momentum / Near Breakout
- 3× more profit potential than breakout entry
- No ATH fear — stock is far below ATH
- No reversal risk — FII is accumulating, trend intact
- SL = 1.5×ATR | Target = 5×ATR | RR = ~3.3
- Options:
  - Non-F&O stock → Equity only (no options) — PERFECT base entry
  - F&O stock → BASE CE with stricter rules (VIX < 16, 40+ days expiry, ATM only)

**Key insight:** Non-F&O stocks are the BEST base entry candidates
because equity trade alone captures full move without options complexity.
Options need liquidity and momentum — breakout stocks. Base stocks = equity.

---

## SECTION 3 — APPSCRIPT v15.4 GATES

Stock must pass ALL 11 gates to enter AlertLog as WAITING:

| Gate | Rule | Breakout | Base Entry |
|---|---|---|---|
| 1 | FII ≠ SELLING | Required | Required |
| 2 | Market Regime | Bearish→Leaders only | Bullish only |
| 3 | Late Entry (RS≥5) | Applied | N/A (not breakout) |
| 4 | Price validity (CMP>0, ATR>0) | Required | Required |
| 4b | Result/Event day skip (>6%) | Required | Required |
| 5 | Extension filter (Retest≥-8%) | Applied | EXEMPT |
| 6 | Pivot resistance buffer | Applied | EXEMPT |
| 7 | Volume filter (>120% or >40% base) | Applied | Relaxed (40%) |
| 8 | ATH buffer (>1%) | Applied | EXEMPT |
| 9 | Trade type not AVOID | Required | Required |
| 10 | Sector concentration (≤2) | Required | Required |
| 11 | Base quality check (NEW v15.4) | N/A | FII+VCP+Days+SMA+ATH gap |

**Gate 11 — Base Quality (ALL must be true):**
1. FII = "Accumulation Zone" (smart money buying quietly)
2. VCP < 0.05 (tight base — volatility contracting)
3. DaysLow ≥ 15 (base mature — at least 3 weeks)
4. SMA = "Strong Bull" or "Bull" (long term trend intact)
5. Stock > 5% below ATH (room to run)
6. Market = Bullish regime (base entries blocked in bearish)

---

## SECTION 4 — CONFIG VALUES (AppScript v15.4)

```javascript
MAX_TRADES    : 8        // max simultaneous trades
MAX_WAITING   : 10       // max WAITING slots
MIN_PRIORITY  : 15       // minimum master score for entry
MIN_RR        : 1.8      // minimum risk/reward ratio

// SL/Target multipliers
ATR_SL_INTRADAY      : 1.5
ATR_SL_SWING         : 2.0
ATR_SL_BASE          : 1.5   // NEW v15.4
ATR_SL_POSITIONAL    : 2.5
ATR_TGT_INTRADAY     : 2.0
ATR_TGT_SWING        : 3.0
ATR_TGT_SWING_LEADER : 4.0   // fixed v15.2 (was 3.5 → RR failed)
ATR_TGT_BASE         : 5.0   // NEW v15.4
ATR_TGT_POSITIONAL   : 4.0

// Key filters
RETEST_MAX_PULLBACK  : -0.08  // fixed v15.2 (was -0.03 → blocked everything)
BEARISH_LEADER_ONLY  : true   // bearish = sector leaders only
BEARISH_MIN_AF       : 5
BEARISH_MIN_MASTER   : 22

// Base entry thresholds (v15.4)
BASE_MAX_VCP         : 0.05   // tight base required
BASE_MIN_DAYS_LOW    : 15     // mature base required
BASE_MIN_ATH_GAP_PCT : 5.0    // must have room to run
BASE_MIN_SCORE       : 18     // lower score OK with FII confirm

// Capital tiers
CAPITAL_HIGH : 13000  // score≥28 + AF≥10
CAPITAL_MED  : 10000  // score≥22 or FII Accumulation
CAPITAL_STD  :  7000  // all others
MAX_DEPLOYED : 104000 // total portfolio cap
```

---

## SECTION 5 — OPTIONS SIGNAL SYSTEM (v15.4)

### Rules — Breakout CE (📊 BUY CE)
- Stage: BREAKOUT ALERT or BREAKOUT CONFIRMED only
- VIX < 18 → buy | VIX 18-22 → caution | VIX > 22 → skip
- Stock must be in F_AND_O_LIQUID_STOCKS (80+ stocks)
- Expiry: minimum 20 days remaining (current or next month)
- Strike: ATM or ATM+1×ATR (whichever best for momentum)
- Premium channel only — not sent to Basic or Advance

### Rules — Base CE (📦 BASE CE)
- Stage: Correction Base / Building Momentum / Near Breakout
- VIX < 16 (stricter — base trade takes 2-4 weeks)
- Stock must be in F_AND_O_LIQUID_STOCKS
- Expiry: minimum 40 days remaining (always next month+)
- Strike: ATM only (base moves slowly — need delta not leverage)
- Premium channel only

### Non-F&O Base Stocks
- Options column shows ⏸ SKIP
- This is CORRECT and BEST — equity trade captures full move
- No options complexity needed for non-liquid stocks
- Members understand: Base entry = patient equity trade

### Option Holding Rules (sent in Telegram)
- Breakout CE: hold up to 3 days, exit if -40% or target hit
- Base CE: hold up to 12 trading days, exit if stock sideways 3 days
- Exit if VIX spikes above 22 → exit all options same day
- Never average down on options
- Never hold past expiry week

### AlertLog Columns U-X
| Column | Header | Values |
|---|---|---|
| U (21) | Options Signal | 📊 BUY CE / 📦 BASE CE / ⏸ SKIP / ❌ VIX HIGH |
| V (22) | Strike | e.g. "400 CE Jun" |
| W (23) | Expiry | e.g. "25-Jun-2026" |
| X (24) | Theta Risk | 🟢 LOW (42d) / 🟡 MED / 🔴 HIGH |

---

## SECTION 6 — ALERTLOG COLUMN MAP (0-based)

```
A=0   Signal Time        B=1   Symbol
C=2   Live Price         D=3   Priority Score
E=4   Trade Type         F=5   Strategy
G=6   Breakout Stage     H=7   Initial SL
I=8   Target             J=9   RR Ratio
K=10  Trade Status       L=11  Entry Price
M=12  Entry Time         N=13  Days in Trade
O=14  Trailing SL        P=15  P/L %
Q=16  ATH Warning        R=17  Risk ₹
S=18  Position Size      T=19  SYSTEM CONTROL
U=20  Options Signal     V=21  Strike
W=22  Expiry             X=23  Theta Risk

T2 = automation switch (YES/NO)
T4 = Python bot state (TSL, MAX, LP, ATR, EXDT per stock)
```

---

## SECTION 7 — TELEGRAM CHANNELS

| Channel | Members | What They Get |
|---|---|---|
| Basic (Free) | All | Market mood, active count, membership CTA |
| Advance ₹699/mo | Paid | Entry/SL/Target/RR, trade type, daily summary |
| Premium ₹1,499/mo | Paid | Everything + Options signals (📊 BUY CE / 📦 BASE CE) |

**Message types by source:**
- AppScript → Regime alert, options signal, daily summary, weekly summary
- Python bot → Good morning, entry alert, TSL update, exit alert, market close

---

## SECTION 8 — PYTHON BOT v14.0

**10 key improvements vs v13.5:**
1. CHAT_ID swap fixed (Advance/Premium were reversed)
2. Advance gets full details, Premium gets details + CE flag
3. BotMemory sheet read (_CAP/_MODE/_SEC/_RANK)
4. Result day skip (>6% gap at open → skip entry)
5. NSE holiday check in Python
6. MAX_TRADES = 8 (matches AppScript)
7. Capital 3-tier fallback from BotMemory sheet
8. Mid-day pulse 12:28-12:38 (P/L snapshot)
9. Market close summary 15:15-15:45
10. CE flag gated by rank ≤5 (Sector Leaders only)

**T4 cell usage (Python only):**
```
NSE_SYMBOL_TSL_  → Trailing SL price ×100
NSE_SYMBOL_MAX_  → Max price seen ×100
NSE_SYMBOL_LP_   → Last price ×100
NSE_SYMBOL_ATR_  → ATR at entry ×100
NSE_SYMBOL_EXDT_ → Exit date string
date_AM/PM flags → Good morning / market close sent
```

**BotMemory sheet (AppScript writes, Python reads):**
```
NSE_SYMBOL_CAP   → Capital tier (7000/10000/13000)
NSE_SYMBOL_MODE  → Trade mode (VCP/MOM/STD)
NSE_SYMBOL_SEC   → Sector
NSE_SYMBOL_RANK  → Sector rank
NSE_SYMBOL_BASE  → "1" if base entry (v15.4 new)
```

---

## SECTION 9 — TSL PARAMETERS

| Mode | Breakeven | Lock1 | Trail | ATR Mult | Gap Lock |
|---|---|---|---|---|---|
| VCP | 3.0% | 5.0% | 8.0% | 2.0 | 9.0% |
| MOM | 2.5% | 4.5% | 7.0% | 1.8 | 8.0% |
| STD | 2.0% | 4.0% | 10.0% | 2.5 | 8.0% |

Gap lock fraction: 0.5 (locks halfway to current price)
Min hold: Swing=2 days, Positional=3 days
Hard loss: 5% max loss without TSL override

---

## SECTION 10 — CONTENT SYSTEM

| Generator | Output | Upload Time | Status |
|---|---|---|---|
| generate_analysis.py | Analysis video (14 slides, ~8 min) | 6:00 PM IST | ✅ Working |
| generate_education.py | Education video (22 slides, ~10 min) | 6:30 PM IST | ✅ Working |
| generate_reel_morning.py | Morning reel (Hindi short) | 6:30 AM IST | ✅ Working |
| generate_shorts.py | 2 YouTube Shorts daily | 11:30 AM IST | ✅ Working |
| generate_articles.py | 4 SEO articles daily | 7:30 AM IST | ✅ Working |
| generate_kids_video.py | HerooQuest story video | 4:30 PM weekdays / 10 AM weekends | ✅ Working |

**human_touch.py v2.1:** format_article_tags + get_youtube_safe_tags in SEO class
**YouTube tags:** get_youtube_safe_tags() removes Hindi/non-ASCII + enforces 480 char total limit
**Articles:** clean_ai_title() fixes "SandP" → "S&P 500" in all titles
**Facebook:** upload_facebook.py + generate_shorts.py both use get_page_token() → fixes #200 error

---

## SECTION 11 — WEBSITE SEO

| File | Fix Applied |
|---|---|
| head.html | Schema type conditional (NewsArticle for market, Article for evergreen) |
| head.html | dateModified = site.time (builds fresh daily — signals freshness to Google) |
| robots.txt | Single Disallow:/page (covers all pagination dynamically) |
| generate_articles.py | Uses ai_client fallback chain (not direct Groq) |
| generate_articles.py | clean_ai_title() fixes encoding; safe_title removes &→and only for Jekyll YAML |

---

## SECTION 12 — MEMBERSHIP

| Plan | Price | Annual |
|---|---|---|
| Advance | ₹699/month | ₹5,588/year (save ₹2,800) |
| Premium | ₹1,499/month | ₹11,988/year (save ₹6,000) |

Payment: UPI 9634759528@upi
Activation: WhatsApp 9634759528 with payment screenshot + Telegram username

**Advance includes:** Daily signals, TradingView indicator, Chartink screener, private videos
**Premium adds:** Options signals, live sessions 2×/month, Nifty200 Google Sheet access, 1:1 portfolio review

---

## SECTION 13 — LIVE TRADING STATUS (May 14, 2026)

**Market Regime:** BEARISH — Nifty ₹23,412 vs 20DMA ₹24,101

**Current Paper Trades (7 open from May 13):**
| Stock | Entry | TSL | Status |
|---|---|---|---|
| NSE:IDEA | ₹12.45 | ₹12.45 | +2.49% |
| NSE:ONGC | ₹298.35 | ₹293.45 | -0.34% |
| NSE:BSE | ₹3,880 | ₹3,805 | +0.23% |
| NSE:ADANIPORTS | ₹1,716.90 | ₹1,674.10 | +1.18% |
| NSE:BHEL | ₹396.95 | ₹382.75 | +1.59% |
| NSE:BHARATFORG | ₹1,962.20 | ₹1,888.40 | -0.52% |
| NSE:TATASTEEL | ₹216.72 | ₹210.18 | +1.47% |

**Today's New WAITING (May 14):**
- NSE:JSWSTEEL — BREAKOUT ALERT, SL ₹1,238.90, T ₹1,352.30
- NSE:BANDHANBNK — Near Breakout, SL ₹187.55, T ₹209.03

**Phase 4 — Live API:** Dhan/Zerodha integration pending 30+ paper trades

---

## SECTION 14 — PENDING TASKS

| Task | Priority | Notes |
|---|---|---|
| Push trading_bot.py v14.0 to GitHub | High | Ready locally, not yet pushed |
| Fix YouTube tags (480 char limit) | High | human_touch.py get_youtube_safe_tags + generate_education extra_tags |
| Fix human_touch.py SEOTags error | High | TypeError in generate_analysis.py — deploy fixed human_touch.py |
| Verify HerooQuest YouTube channel thumbnails | Medium | studio.youtube.com → Settings → Feature eligibility → Verify phone |
| Fix Facebook Group posting | Low | publish_to_groups permission — known issue |
| Test v15.4 base entry in bullish market | When market turns | BASE_ENTRY_ENABLED = true, test with Manual Sync |

---

## SECTION 15 — FILE MAP

```
Trading System:
  trading_bot.py         Python bot v14.0 (local) / v13.5 (GitHub)
  appscript_v15.4.js     AppScript — deploy to Google Sheets
  content_calendar.py    Education topic rotation

Content:
  generate_analysis.py   v2.1 — 14-slide analysis video
  generate_education.py  v2.1 — 22-slide education video
  generate_reel_morning.py — Daily Hindi short
  generate_shorts.py     — 2 market shorts daily
  generate_articles.py   — 4 SEO articles daily
  generate_kids_video.py — HerooQuest story video
  upload_facebook.py     v2.1 — Page token fix
  upload_kids_youtube.py v2.1 — Broader thumbnail search
  upload_youtube.py      — Standard YouTube upload
  human_touch.py         v2.1 — SEO class with format_article_tags
  ai_client.py           — Groq→Gemini→Claude→OpenAI fallback chain

Config:
  .github/workflows/daily.yml     — Main content + trading bot
  .github/workflows/kids-daily.yml — HerooQuest 4:30PM weekdays / 10AM weekends

Jekyll/SEO:
  _includes/head.html    — Schema conditional + dateModified fix
  robots.txt             — Single /page pagination rule
  _pages/membership.md   — ₹699/₹1,499 pricing with UPI

Data:
  Google Sheet: Ai360tradingAlgo
    → AlertLog   (scanner output, 19 cols + 4 options cols U-X)
    → Nifty200   (200+ stock data with 35 columns)
    → History    (completed trades A-R)
    → BotMemory  (AppScript state per stock)
```

---

## SECTION 16 — SYSTEM LOGIC SUMMARY

```
Every 5 minutes (AppScript time trigger):
  1. Load Nifty200 data
  2. Check market regime (Nifty vs 20DMA)
  3. Fetch India VIX from Yahoo Finance
  4. For each stock, run Gates 1-11
     → Breakout stocks: Gates 1-10
     → Base stocks: Gates 1-4b + Gate 7 relaxed + Gate 11
  5. Sort candidates by FinalScore + Rank
  6. Cap at MAX_WAITING (10) with sector limits
  7. Write to AlertLog (19 columns)
  8. Write options signals to columns U-X
  9. Send regime alert (once/day) to Advance+Premium
  10. Send options alert to Premium only

Python bot (every 5 min via GitHub Actions):
  1. Read AlertLog
  2. For WAITING rows: check if CMP > entry → promote to TRADED
  3. For TRADED rows: check TSL, target, hard loss
  4. Update T4 cell with new TSL/MAX values
  5. Send entry/exit Telegram alerts
  6. Good morning at 8:45 AM (all channels)
  7. Mid-day pulse 12:30 PM (Advance+Premium)
  8. Market close summary 15:30 PM (all channels)

Options flow:
  AppScript → OPTIONS SIGNAL sent to Premium at scan time
  Python bot → Entry alert sent when stock triggers → includes CE reminder
  
Base entry flow (v15.4):
  AppScript → identifies base stock → runs Gate 11 → WAITING with 📦 tag
  Python bot → entry when price confirms → treated as swing (STD/VCP mode)
  Options → if F&O liquid + VIX<16 + 40+days → BASE CE to Premium
           → if non-F&O → equity only (best base trade — no option needed)
```

---

*Last updated: May 14, 2026 — AI360 Trading System v15.4*
