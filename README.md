# AI360Trading — Global Market Intelligence + HerooQuest Kids

> Daily AI-powered market intelligence for NIFTY, S&P 500, FTSE 100, IBOVESPA and Bitcoin.
> Built for retail traders in India, US, UK, UAE and Brazil.
> **HerooQuest** — Daily animated kids stories with Heroo & Arya.

🌐 **Live Site:** [https://ai360trading.in](https://ai360trading.in)

---

## ⚠️ Signal Service — NOT Auto-Trading

This system **does not execute live trades**. Every alert is a **signal** that you (and our subscribers) act on manually — choosing your own broker, lot size, and timing. The paper-trading P&L tracked internally is for performance reporting only.

> "Currently no auto trade — only proper signal. Me and my followers take trade entry, exit, trail, option buying, cash stocks etc. ourselves." — Owner, May 2026

Phase 4 (Dhan API live execution) is planned but not active. Every signal in Telegram is for **educational purposes** and you decide whether to take it.

---

## What This Repo Powers

### 📈 AI360Trading — Trading Channel

| Module | What it does |
|---|---|
| `trading_bot.py` | Every 5 min — monitors WAITING→TRADED, trails SL, fires exits + Telegram alerts |
| `appscript.gs` | Google Sheets scanner — Nifty 200 universe → AlertLog (large-cap signals) |
| `option_intelligence.py` | Smart options module — ITM strike picker, HV-based IV gate, earnings block, PE side for bearish regime |
| `institutional_edges.py` | Five "smart money" filters — relative strength, volume, FII regime, PCR, delivery % |
| `fetch_fii_dii.py` | Daily NSE FII/DII cash flow → BotMemory + Telegram digest |
| `fetch_earnings.py` | Daily NSE event calendar → blocks options entries near earnings |
| `fetch_bhavcopy.py` | Daily NSE bhavcopy + option-chain → delivery % + PCR cache |
| `fetch_smallmidcap.py` | Daily small/mid cap momentum scanner (outside Nifty 200) — 0-3 selective picks/day |
| `fetch_holidays.py` | Annual NSE holiday refresh (1 Dec each year) → BotMemory |
| `generate_longterm.py` | Weekly positional picks for the LongTermSignals tab |
| `refresh_cashwatchlist.py` | Weekly cash-intraday watchlist refresh |
| `token_refresh.py` | Auto-rotate Facebook/Instagram tokens (1st + 15th of each month) |

### 📝 Content Engine (₹0/month, fully automated)

| Module | Output |
|---|---|
| `generate_articles.py` | 4 daily SEO articles (2 Hindi + 2 English) |
| `generate_education.py` | 22-slide educational deep-dive video |
| `generate_shorts.py` | Short 2 (Trade Setup) + Short 3 daily |
| `generate_reel.py` + `generate_reel_morning.py` | Morning + ZENO 9:16 reels |
| `generate_analysis.py` | 10-15 min combined market analysis video |
| `human_touch.py` | Adds Hinglish flow + 12% non-English words for engagement |
| `ai_client.py` | AI gateway with Groq → Gemini → Claude → OpenAI → templates fallback |

### 👶 HerooQuest — Kids Channel

- `generate_kids_video.py` — Daily animated story starring Heroo & Arya
- Pixar/Disney 3D CGI via 5-layer AI image fallback
- Bilingual: Hindi story + English moral
- `selfDeclaredMadeForKids: True` — appears in YouTube Kids recommendations

---

## Signal Quality Gates — what every entry passes through

Every WAITING → TRADED promotion goes through **11 gates** before reaching Telegram:

```
 1. Re-entry cooldown   — no entry within 5d of prior target-hit
 2. Time window         — 9:15-2:30 PM bull / 9:15-11:00 AM bear
 3. Daily entry limit   — max 3 swing / 1 bearish entries/day
 4. Nifty direction     — index agreeing with regime
 5. India VIX           — block new entries if VIX > 22
 6. RSI                 — bull: RSI < 65, bear: RSI < 58
 7. Relative Strength   — sheet RS score ≥ 5 (institutional leader)
 8. Volume              — ≥ 1.5× avg, OR price up 3%+ (price = proof of volume)
 9. FII regime          — block longs if FII net ≤ −₹2000 Cr
10. PCR                 — soft / informational (contrarian indicator)
11. Delivery %          — ≥ 40% (institutional accumulation vs jobbing)
```

Profit protection on every open trade:
- **1R breakeven** — SL moves to entry once gain ≥ initial-risk distance
- **Chandelier trail** — trail anchored to highest-price-reached, only rises
- **Partial book alert @ +5%** — Telegram nudge to book 50%, trail the rest
- **Time stop @ 5d + no +3%** — exit dead-capital trades automatically
- **Stock-anchored option exit** — SL = stock −1.5% (not option −40%)

---

## Market Coverage

| Market | Index | Coverage |
|---|---|---|
| 🇮🇳 India | NIFTY 50, Bank Nifty, SENSEX | Daily signals + FII/DII flow |
| 🇺🇸 United States | S&P 500, NASDAQ, Dow Jones | Daily analysis + Fed tracking |
| 🇬🇧 United Kingdom | FTSE 100 | Daily overview + GBP/USD |
| 🇧🇷 Brazil | IBOVESPA | Daily analysis + BRL/USD |
| 🇦🇪 UAE | Gulf markets + NRI investors | Weekly outlook |
| ₿ Crypto | Bitcoin, Ethereum | Daily + Fear & Greed Index |

---

## Daily Automation Schedule

### Trading data (auto-refresh, no manual ops)

| Time IST | Cron | Purpose |
|---|---|---|
| 9:15-15:30 (every 5 min, Mon-Fri) | `trading_bot.yml` | Monitor signals, trail SL, fire entries/exits |
| 18:30 daily | `fetch_earnings.yml` | NSE event calendar → blocks earnings-week options |
| 18:45 Mon-Fri | `fetch_fii_dii.yml` | FII/DII cash flow → regime gate |
| 20:00 Mon-Fri | `fetch_bhavcopy.yml` | Delivery % + PCR cache |
| 20:30 Mon-Fri | `fetch_smallmidcap.yml` | Small/mid cap momentum digest (0-3 picks) |
| 1 Dec yearly | `fetch_holidays.yml` | Auto-refresh NSE holiday calendar |
| 1st + 15th monthly | `token_refresh.yml` | Auto-rotate FB/IG tokens |

### Content (auto-publish)

| Time IST | Content | Platform |
|---|---|---|
| 7:00 AM | Morning Reel (9:16) | YouTube + Facebook |
| 10:00 AM | 4 SEO Articles | GitHub Pages + Facebook |
| 4:30 PM wkday / 10 AM wkend | Kids Story (HerooQuest) | YouTube Kids + Facebook |
| 6:00 PM Mon–Fri | Analysis + Education Video | YouTube Hindi |
| 7:00 PM | Short 2 (Trade Setup) | YouTube Shorts |
| 7:30 PM | Community Poll | YouTube |
| 8:30 PM | ZENO Reel (9:16) | YouTube + Facebook |

---

## Telegram Channels

| Channel | Audience | Content |
|---|---|---|
| [@ai360trading](https://t.me/ai360trading) | Free | Market mood, daily summary, basic signals |
| ai360trading_Advance | Swing + Positional | Full entry/SL/target/RR/qty + TSL updates + exit alerts |
| ai360trading_Premium | Intraday + Options | Everything in Advance + smart option strike (ITM, Δ ≈ 0.7) + earnings block + stock-anchored exit |

All signals come with: entry price, initial stop loss, target, risk-reward, position size for ₹7k/10k/13k tiers. **Subscribers manually decide whether/how to take each trade.**

---

## Self-Repair / Free-Forever Architecture

The system is engineered to run ₹0/month, auto-update, and self-repair:

1. **Free data only** — yfinance, NSE public APIs, BSE public APIs, GitHub Actions free tier, Google Sheets free tier, Telegram free API.
2. **Every external call fails open** — a yfinance timeout, an NSE 403, an empty bhavcopy all return permissive defaults so one outage cannot stall a tick.
3. **Auto-updating data** — holidays refresh annually, FII data daily, earnings daily, tokens every 2 weeks, bhavcopy daily — no manual ops.
4. **Module-level isolation** — `option_intelligence`, `institutional_edges`, etc. are imported with try/except. If any module is broken or missing, the bot falls back to the previous version's logic.
5. **Workflow failure alerts** — every cron job has an `if: failure()` step that posts a "System Notice" to the Basic Telegram channel so the operator sees problems within minutes.
6. **Self-healing sheet I/O** — Nifty200 column lookups match by header name (not index) so AppScript can add columns without breaking the bot.
7. **Stale-data bypass** — known stale columns (e.g. Volume_vs_Avg_%) are bypassed when a stronger signal (price > +3%) confirms the underlying state.
8. **Auto-archive** — History sheet auto-archives every Monday morning when it exceeds 500 rows.

---

## Tech Stack

| Component | Technology |
|---|---|
| Website | Jekyll + GitHub Pages |
| AI Generation | Groq (primary) → Gemini → Claude → OpenAI → Templates |
| Image Generation (Kids) | Gemini 2.5 → DALL-E 3 → HuggingFace → Stability AI → Placeholder |
| Video Rendering | MoviePy + FFmpeg + Ken Burns zoom |
| Voice (TTS) | Edge TTS (SwaraNeural, MadhurNeural, NeerjaNeural) |
| Market Data | Yahoo Finance (yfinance) + NSE public APIs + BSE public APIs |
| Trading State | Google Sheets (`Ai360tradingAlgo` workbook) via gspread |
| Memory | `BotMemory` sheet — runtime state, caches, flags |
| Scheduler | GitHub Actions (cron) |
| Telegram | python-telegram-bot API |

---

## Content Pillars

- 📊 **Stock Market** — `/topics/stock-market/`
- ₿ **Bitcoin & Crypto** — `/topics/bitcoin/`
- 💰 **Personal Finance** — `/topics/personal-finance/`
- 🤖 **AI Trading** — `/topics/ai-trading/`

---

## Broker Partner Links

- [Open account in Zerodha](https://bit.ly/2VK6k5F)
- [Open account in Dhan](https://invite.dhan.co/?invite=MSIVC45309)

---

## Social Media

| Platform | Link |
|---|---|
| 🌐 Website | [ai360trading.in](https://ai360trading.in) |
| 📣 Telegram | [@ai360trading](https://telegram.me/ai360trading) |
| 🐦 Twitter / X | [@ai360trading](https://x.com/ai360trading) |
| ▶️ YouTube Trading | [@ai360trading](https://www.youtube.com/@ai360trading) |
| ▶️ YouTube Kids | HerooQuest channel |
| 📸 Instagram | [@ai360trading](https://www.instagram.com/ai360trading) |
| 👥 Facebook Group | [ai360trading](https://www.facebook.com/groups/ai360trading) |
| 📘 Facebook Trading | [ai360trading.official](https://www.facebook.com/ai360trading.official) |
| 📘 Facebook Kids | HerooQuest Kids Page |

---

## For AI Assistants

Read `CLAUDE.md`, `.internal-ops.md` and `SESSION.md` before making any changes.
These files contain the complete system architecture, rules, and pending tasks.

---

## Legal

All content is for **educational purposes only**. AI360Trading is not a SEBI registered investment advisor.
Read full disclaimer: [ai360trading.in/disclaimer/](https://ai360trading.in/disclaimer/)

See `LICENSE.md` for intellectual property terms.

---

**Admin:** admin@ai360trading.in | Haridwar, Uttarakhand, India
