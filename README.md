# AI360Trading — Global Market Intelligence + HerooQuest Kids

> Daily AI-powered market intelligence for NIFTY, S&P 500, FTSE 100, IBOVESPA and Bitcoin.
> Built for retail traders in India, US, UK, UAE and Brazil.
> **HerooQuest** — Daily animated kids stories with Heroo & Arya.

🌐 **Live Site:** [https://ai360trading.in](https://ai360trading.in)

---

## What This Repo Powers

### 📈 AI360Trading — Trading Channel

- **Jekyll website** hosted on GitHub Pages at `ai360trading.in`
- **Article bot** (`generate_articles.py`) — 4 daily SEO articles (2 Hindi + 2 English)
- **Analysis video** (`generate_analysis.py`) — 10-15 min combined market analysis video
- **Education video** (`generate_education.py`) — 22-slide educational deep-dive
- **Shorts** (`generate_shorts.py`) — Short 2 + Short 3 daily
- **Reels** (`generate_reel.py` + `generate_reel_morning.py`) — Morning + ZENO reels
- **Trading bot** (`trading_bot.py`) — Every 5 min, monitors signals, sends Telegram alerts

### 👶 HerooQuest — Kids Channel

- **Kids story** (`generate_kids_video.py`) — Daily animated story starring Heroo
- Pixar/Disney style 3D CGI via 5-layer AI image fallback
- Bilingual: Hindi story + English moral
- `selfDeclaredMadeForKids: True` — appears in YouTube Kids recommendations

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

| Time IST | Content | Platform |
|---|---|---|
| 7:00 AM | Morning Reel (9:16) | YouTube + Facebook |
| 6:00 PM Mon–Fri | Analysis + Education Video | YouTube Hindi |
| 7:00 PM | Short 2 (Trade Setup) | YouTube Shorts |
| 7:30 PM | Community Poll | YouTube |
| 8:30 PM | ZENO Reel (9:16) | YouTube + Facebook |
| 10:00 AM | 4 SEO Articles | GitHub Pages + Facebook |
| 4:30 PM wkday / 10 AM wkend | Kids Story (HerooQuest) | YouTube Kids + Facebook |

---

## Telegram Channels

| Channel | Audience | Content |
|---|---|---|
| [@ai360trading](https://t.me/ai360trading) | Free | Market mood, daily summary |
| ai360trading_Advance | Swing + Positional | Full signals, entry/exit/TSL alerts |
| ai360trading_Premium | Intraday + Options | Everything + options CE candidate hints |

---

## Tech Stack

| Component | Technology |
|---|---|
| Website | Jekyll + GitHub Pages |
| AI Generation | Groq (primary) → Gemini → Claude → OpenAI → Templates |
| Image Generation (Kids) | Gemini 2.5 → DALL-E 3 → HuggingFace → Stability AI → Placeholder |
| Video Rendering | MoviePy + FFmpeg + Ken Burns zoom |
| Voice (TTS) | Edge TTS (SwaraNeural, MadhurNeural, NeerjaNerual) |
| Market Data | Yahoo Finance (yfinance) |
| Trading Signals | Google Sheets + gspread |
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

Read `SYSTEM.md` and `REPO_STRUCTURE.md` before making any changes.
These files contain the complete system architecture, rules, and deployment checklist.

---

## Legal

All content is for **educational purposes only**. AI360Trading is not a SEBI registered investment advisor.
Read full disclaimer: [ai360trading.in/disclaimer/](https://ai360trading.in/disclaimer/)

See `LICENSE.md` for intellectual property terms.

---

**Admin:** admin@ai360trading.in | Haridwar, Uttarakhand, India
