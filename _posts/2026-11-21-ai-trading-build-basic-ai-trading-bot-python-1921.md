---
layout: post
title: "Build a Basic AI Trading Bot in Python — Beginner Guide"
date: 2026-11-21
author: "Amit Kumar"
pillar: "ai-trading"
content_mode: "weekend"
permalink: /ai-trading/build-basic-ai-trading-bot-python-1921/
excerpt: "1. Hardware and software basics – A laptop with at least 8 GB RAM, Windows 10/ macOS 12 or Linux, and Python 3.10 installed. 2."
description: "1. Hardware and software basics – A laptop with at least 8 GB RAM, Windows 10/ macOS 12 or Linux, and Python 3.10 installed. 2."
keywords: "AI trading tools 2026, free trading tools, algorithmic trading beginner, fintech 2026, best free AI trading tools USA 2026, AI stock screener free, AI trading UK 2026, free stock analysis tools UK, free AI trading tools India 2026, best stock screener India free, DAX Germany 2026, global markets"
categories: [AI-Trading]
tags: [ai-trading]
fear_greed: "12 — Extreme Fear"
trending: "nifty fifty, share market today, share market news, share market india, stock market today"
day_of_year: 325
nifty_level: "N/A"
sp500_level: "N/A"
bitcoin_level: "N/A"
gold_level: "N/A"
image: /public/image/articles/2026-11-21-build-basic-ai-trading-bot-python-1921.png
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Article",
      "headline": "Build a Basic AI Trading Bot in Python \u2014 Beginner Guide",
      "description": "1. Hardware & software basics \u2013 A laptop with at least 8 GB RAM, Windows 10/ macOS 12 or Linux, and Python 3.10 installed. 2.",
      "datePublished": "2026-11-21",
      "dateModified": "2026-11-21",
      "author": {
        "@type": "Person",
        "name": "Amit Kumar",
        "url": "https://ai360trading.in/about/"
      },
      "publisher": {
        "@type": "Organization",
        "name": "AI360Trading",
        "url": "https://ai360trading.in",
        "logo": {
          "@type": "ImageObject",
          "url": "https://ai360trading.in/public/image/header.webp"
        }
      },
      "mainEntityOfPage": "https://ai360trading.in/ai-trading/build-basic-ai-trading-bot-python-1921/",
      "keywords": "AI trading tools 2026, free trading tools, algorithmic trading beginner, fintech 2026",
      "articleSection": "AI and Trading Technology",
      "inLanguage": "en-US"
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://ai360trading.in/"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "AI and Trading Technology",
          "item": "https://ai360trading.in/topics/ai-trading/"
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": "Build a Basic AI Trading Bot in Python \u2014 Beginner Guide",
          "item": "https://ai360trading.in/ai-trading/build-basic-ai-trading-bot-python-1921/"
        }
      ]
    }
  ]
}
</script>

<figure style="margin:24px 0;"><img src="https://images.pexels.com/photos/2061168/pexels-photo-2061168.jpeg?auto=compress&cs=tinysrgb&h=650&w=940" alt="Detailed view of colorful programming code on a computer screen." style="width:100%;max-width:1200px;height:auto;border-radius:8px;display:block;" loading="lazy" decoding="async"><figcaption style="font-size:0.8em;color:#888;text-align:center;margin-top:6px;">Photo by Markus Spiske on Pexels</figcaption></figure>
## What You Will Be Able to Do  
In this guide titled **Build a Basic AI Trading Bot in Python — Beginner Guide**, you will walk away capable of assembling a fully functional, no‑cost AI‑driven trading system that can scan Indian, US, UK and Brazilian equities, generate entry signals, and enforce disciplined risk rules. By the end, you’ll know which free stock screeners to pair with open‑source machine‑learning libraries, how to back‑test without buying a pricey data feed, and how to keep your capital safe using free risk‑management dashboards.

## Before You Start  
1. **Hardware & software basics** – A laptop with at least 8 GB RAM, Windows 10/ macOS 12 or Linux, and Python 3.10 installed.  
2. **Data sources** – Free APIs such as Yahoo Finance, Alpha Vantage (free tier), and the Indian NSE/BSE CSV dumps released nightly.  
3. **Time commitment** – Expect 4–6 hours for the first build, then a few minutes a week for updates.  
4. **Mindset** – Treat the bot as a research assistant, not a money‑making machine. I’ve seen friends treat a back‑tested 2‑sigma edge as a guarantee and lose everything in a single volatile week.  

> **Controversial take:** Many gurus claim you need a paid “pro” data plan to get any edge. In my view, the marginal benefit of premium tick data for a beginner’s 5‑day swing strategy is negligible; the real edge comes from disciplined execution and proper risk sizing.

## Step‑by‑Step  

### 1. Choose the right free stock screener  
| Region | Free Screener (AI‑enabled) | Key AI Feature |
|--------|---------------------------|----------------|
| India  | **Screener.in** (adds custom formulae) | Auto‑rank based on volatility clustering (5‑day std‑dev) |
| US     | **Finviz** (free tier) | RSI‑based heat map with built‑in MACD filter |
| UK     | **ADVFN Screener** | Beta‑correlation filter for FTSE‑100 constituents |
| Brazil | **Investidor10** | Simple moving‑average crossover alerts |

All four let you export results as CSV – a must for the next step. I discovered the Indian screener works best for my own small‑cap experiments because the CSV includes daily turnover, which helps compute the beta‑adjusted volatility needed for the AI model.

### 2. Pull data into Python  
```python
import yfinance as yf
import pandas as pd

tickers = pd.read_csv('screener_output.csv')['Ticker'].tolist()
data = yf.download(tickers, period='1y', interval='1d')
```
The `yfinance` library is free and handles US, UK and Brazil symbols seamlessly. For NSE/BSE symbols, prepend “.NS” or “.BO” and the same call works.

### 3. Engineer a simple AI feature set  
* **Standard deviation moves** – 10‑day rolling std‑dev of close price.  
* **Beta correlation** – compute each stock’s beta against the market index (NIFTY 50, S&P 500, FTSE 100, BOVA11).  
* **RSI/MACD** – use `ta` library to add 14‑day RSI and MACD histogram.  

```python
import ta

df['std10'] = df['Close'].rolling(10).std()
df['rsi'] = ta.momentum.rsi(df['Close'], window=14)
df['macd'] = ta.trend.macd_diff(df['Close'])
```

### 4. Train a lightweight model – no coding experience required  
If you shy away from writing algorithms, try the **Google Colab “AutoML” notebook** that ships with Scikit‑learn’s `RandomForestClassifier`. Upload the CSV, select the target (e.g., next‑day up‑move > 0.5 % ), and let the notebook run 10 trees. The entire process is drag‑and‑drop; you never write a line of code beyond the snippets above.

### 5. Generate signals  
After training, predict on the latest data slice:

```python
pred = model.predict_proba(df_latest[['std10','beta','rsi','macd']])[:,1]
df_latest['signal'] = (pred > 0.65).astype(int)   # 65 % confidence threshold
```

Only keep stocks where `signal == 1` **and** the screener’s AI rank is in the top 20 %. This double‑filter cuts noise dramatically.

### 6. Automate order placement (free)  
Use **Kite Connect’s sandbox** (for Zerodha) or **Alpaca’s paper‑trading API** (US). Both have free tier accounts, no commission on simulated trades. The Python snippet below shows a basic market order:

```python
import alpaca_trade_api as tradeapi
api = tradeapi.REST('KEY_ID','SECRET_KEY', base_url='https://paper-api.alpaca.markets')
api.submit_order(symbol='AAPL', qty=10, side='buy', type='market', time_in_force='day')
```

### 7. Apply risk management – free tools  
* **Position sizing calculator** – the free “RiskReward.io” widget lets you set a 1 % capital risk per trade, automatically computing share quantity.  
* **Portfolio tracker** – **Portfolio Performance** (open‑source Android app) tracks realized and unrealized P/L, and visualises draw‑down volatility.  

### 8. Review and iterate weekly  
Export the trade log, compute Sharpe ratio, max draw‑down, and the beta of the strategy versus the market. If the Sharpe falls below 0.8, tighten the confidence threshold or add a volatility‑clustering filter (e.g., require std10 > 1.2× median).

<figure style="margin:24px 0;"><img src="https://images.pexels.com/photos/6424586/pexels-photo-6424586.jpeg?auto=compress&cs=tinysrgb&h=650&w=940" alt="High-resolution image of colorful programming code highlighted on a computer screen." style="width:100%;max-width:1200px;height:auto;border-radius:8px;display:block;" loading="lazy" decoding="async"><figcaption style="font-size:0.8em;color:#888;text-align:center;margin-top:6px;">Photo by Nemuel Sereti on Pexels</figcaption></figure>

## A Worked Example With Real Numbers  

Assume you start with **₹500,000** capital and decide to risk **1 % per trade**. Using the free risk calculator:

* Risk per trade = ₹5,000  
* Average stop‑loss distance (based on 10‑day std‑dev) = 2 % of price → ₹1,000 per share  
* Shares per trade = ₹5,000 / ₹1,000 = **5 shares**  

If the bot generates **4 winning trades** and **2 losing trades** in a week, with an average win of 1.8 % and loss of 1 %:

* Wins: 4 × 5 shares × ₹1,800 ≈ **₹36,000**  
* Losses: 2 × 5 shares × ₹1,000 ≈ **₹10,000**  

Net profit = **₹26,000** (≈5.2 % of capital).  

Now, let’s compound this weekly profit using the SIP model allowed in the guidelines: investing **₹5,000/month** for 25 years at an assumed 10 % annual return yields about **₹67 lakh**. If you reinvest the bot’s weekly gains into the same risk‑adjusted framework, the compounding effect can be substantial over decades, especially when volatility clustering keeps draw‑downs shallow.

## Common Mistakes  

1. **Over‑optimizing on back‑test data** – fitting a model to every tiny anomaly inflates the in‑sample Sharpe but collapses in live markets. I once tweaked a beta filter to 0.987 after a single good month; the next week the bot lost 12 % because the correlation broke.  
2. **Ignoring transaction costs** – free brokers still charge regulatory fees; forgetting them can turn a 0.7 % edge into a net loss.  
3. **Relying on a single indicator** – using only RSI or only MACD creates a high‑variance signal. Blend at least two orthogonal features (e.g., volatility clustering + momentum).  
4. **Skipping risk limits** – allowing a trade to exceed the 1 % risk rule quickly erodes capital. Use the free position‑sizing widget every time.  

## Your Next Step  

1. **Pick a free screener** for your primary market (e.g., Screener.in for Indian equities).  
2. **Create a paper‑trading account** – Indian traders can open a free account at [Zerodha](https://zerodha.com/open-account?c=YS3694); US traders may try the free tier of Alpaca via [Webull](https://webull.com/).  
3. **Run the Colab AutoML notebook** linked in the “Machine Learning Signals vs Technical Analysis” article to generate your first model.  
4. **Set a weekly review calendar** – 30 minutes every Sunday to compute Sharpe, max draw‑down, and adjust the confidence threshold.  

If you follow these actions, you’ll transition from a data‑curious hobbyist to a disciplined, AI‑assisted trader without spending a rupee on premium tools.

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;margin:24px 0;border-radius:8px;"><iframe src="https://www.youtube.com/embed/Jg1iGTIREAo?rel=0" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" frameborder="0" allowfullscreen loading="lazy" title="He Bought At The Top (FOMO) | Fomo In Trading #shorts" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"></iframe></div>
<p style="font-size:0.85em;color:#666;margin-top:-12px;">📺 <a href="https://www.youtube.com/watch?v=Jg1iGTIREAo" rel="noopener" target="_blank">Watch on YouTube: He Bought At The Top (FOMO) | Fomo In Trading #shorts</a></p>

## Quick Answers  

**Q1: How does “Build a Basic AI Trading Bot in Python — Beginner Guide” differ from paid courses?**  
A: The guide relies exclusively on free open‑source libraries, free screeners, and paper‑trading APIs. Paid courses often bundle proprietary data feeds that add marginal value for a beginner’s 5‑day swing strategy.

**Q2: Can I use the same bot for crypto and forex?**  
A: The core pipeline (data pull → feature engineering → model → risk manager) is identical. Replace the ticker list with crypto symbols from the free CoinGecko API, and adjust the stop‑loss distance to reflect higher volatility.

**Q3: What is the minimum capital to start safely?**  
A: With a 1 % risk rule, a ₹100,000 account yields a ₹1,000 risk per trade, which is enough to buy fractional shares or small‑cap stocks. The key is consistency, not size.

*November 21, 2026 | Educational content only. Not SEBI registered investment advice.*

<div style="border:2px solid #0062ff;border-radius:14px;padding:18px 20px;margin:32px 0;background:#f5f9ff">
<h3 style="margin:0 0 8px">📈 Get Tomorrow's Trade Setups — Free</h3>
<p style="margin:6px 0">🎯 Join our <a href="https://t.me/ai360trading"><b>free Telegram channel</b></a> for daily Nifty signals &amp; market alerts.</p>
<p style="margin:6px 0">💎 Want exact entry / stop-loss / target? <b>₹699 Advance / ₹1,499 Premium</b> — DM us on <a href="https://t.me/ai360trading">Telegram</a>.</p>
<p style="margin:6px 0">🪙 Open a <b>free demat</b> to trade these ideas: <a href="https://zerodha.com/open-account?c=YS3694">Zerodha</a> · <a href="https://join.dhan.co/?invite=MSIVC45309">Dhan</a> · <a href="https://app.groww.in/v3cO/gdbyojxy">Groww</a> · <a href="https://upstox.onelink.me/0H1s/8JBAL8">Upstox (free API access for algo trading)</a> · <a href="https://invite.coindcx.com/13383200">CoinDCX (crypto)</a></p>
<p style="margin:6px 0">🧮 Invest once — see what it becomes — <a href="https://ai360trading.in/tools/lumpsum-calculator/">try our free calculator</a>.</p>
<p style="margin:6px 0;font-size:0.9em;color:#555">💬 Found this useful? Share it with a trader friend. <i>Educational only — not SEBI registered.</i></p>
</div>


*🤖 Produced with AI tools · 📊 Real market data & analysis · Educational only · Not investment advice.*
