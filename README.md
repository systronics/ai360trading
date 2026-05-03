# AI360Trading — Global Market Intelligence

> Daily AI-powered market intelligence for NIFTY, S&P 500, FTSE 100, IBOVESPA and Bitcoin.
> Built for retail traders in India, US, UK and Brazil.

🌐 **Live Site:** [https://ai360trading.in](https://ai360trading.in)

---

## What This Repo Powers

- **Jekyll site** hosted on GitHub Pages at `ai360trading.in`
- **AI article bot** (`generate_articles.py`) — generates 4 daily market intelligence articles using live prices, Google Trends and Groq LLM
- **Trading bot** (`trading_bot.py`) — runs every 5 minutes via GitHub Actions, monitors signals, sends Telegram alerts to 3 channels

---

## Market Coverage

| Market | Index | Coverage |
|--------|-------|----------|
| 🇮🇳 India | NIFTY 50, Bank Nifty, SENSEX | Daily signals + FII/DII flow |
| 🇺🇸 United States | S&P 500, NASDAQ, Dow Jones | Daily analysis + Fed tracking |
| 🇬🇧 United Kingdom | FTSE 100 | Daily overview + GBP/USD |
| 🇧🇷 Brazil | IBOVESPA | Daily analysis + BRL/USD |
| ₿ Crypto | Bitcoin, Ethereum | Daily + Fear & Greed Index |

---

## Content Pillars

- 📊 **Stock Market** — `/topics/stock-market/`
- ₿ **Bitcoin & Crypto** — `/topics/bitcoin/`
- 💰 **Personal Finance** — `/topics/personal-finance/`
- 🤖 **AI Trading** — `/topics/ai-trading/`

---

## Telegram Channels

| Channel | Audience | Content |
|---------|----------|---------|
| [@ai360trading](https://t.me/ai360trading) | Free | Market mood, daily summary |
| ai360trading_Advance | Swing and positional | Full signals, entry/exit/TSL alerts |
| ai360trading_Premium | advance, intraday and option | Everything + options hints |

---

## Broker Partner Links

- [Open account in Zerodha](https://bit.ly/2VK6k5F)
- [Open account in Dhan](https://invite.dhan.co/?invite=MSIVC45309)

---

## Social Media

| Platform | Link |
|----------|------|
| 🌐 Website | [ai360trading.in](https://ai360trading.in) |
| 📣 Telegram | [@ai360trading](https://telegram.me/ai360trading) |
| 🐦 Twitter / X | [@ai360trading](https://x.com/ai360trading) |
| ▶️ YouTube | [@ai360trading](https://www.youtube.com/@ai360trading) |
| 📸 Instagram | [@ai360trading](https://www.instagram.com/ai360trading) |
| 👥 Facebook Group | [ai360trading](https://www.facebook.com/groups/ai360trading) |
| 📘 Facebook Page | [ai360trading](https://www.facebook.com/ai360trading.official) |

---

## Tech Stack

- **Site:** Jekyll + GitHub Pages
- **Hosting:** GitHub Pages (free, auto-deploys on push)
- **Article Bot:** Python + Groq LLM (llama-3.3-70b) + Yahoo Finance API
- **Trading Bot:** Python + gspread + Google Sheets + Telegram Bot API
- **Scheduler:** GitHub Actions (cron every 5 min, Mon–Fri)
- **Data:** Yahoo Finance, Google Trends, Fear & Greed API, Google News RSS

---

## Legal

All content is for **educational purposes only**. AI360Trading is not a SEBI registered investment advisor.
Read full disclaimer: [ai360trading.in/disclaimer/](https://ai360trading.in/disclaimer/)

---

**Admin:** admin@ai360trading.in | Haridwar, Uttarakhand, India
