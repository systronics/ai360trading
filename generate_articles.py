import os
import pytz
import requests
import random
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from groq import Groq

# ─── Init ────────────────────────────────────────────────────────────────────
client       = Groq(api_key=os.environ.get("GROQ_API_KEY"))
ist          = pytz.timezone('Asia/Kolkata')
now          = datetime.now(ist)
date_str     = now.strftime("%Y-%m-%d")
date_display = now.strftime("%B %d, %Y")
day_name     = now.strftime("%A")
POSTS_DIR    = os.path.join(os.getcwd(), '_posts')
MAX_POSTS    = 30

# ─── Writing Personas ────────────────────────────────────────────────────────
PERSONAS = [
    {
        "name": "Senior Derivatives Trader",
        "tone": "confident and contrarian",
        "style": "uses F&O terminology naturally, references open interest and PCR ratios, draws parallels with specific historical dates, occasionally uses Hindi trading phrases",
        "opening_hook": "leads with the most surprising data point of the day",
        "signature_phrase": "The options market never lies.",
    },
    {
        "name": "Macro Economist",
        "tone": "analytical and precise",
        "style": "references RBI policy decisions, bond yield spreads, current account deficit implications, draws macro cycles from 2008, 2013, 2020",
        "opening_hook": "starts with a macro paradox in today's data",
        "signature_phrase": "The macro picture tells a different story than the headlines.",
    },
    {
        "name": "Quantitative Analyst",
        "tone": "methodical and number-heavy",
        "style": "references standard deviation moves, beta correlations, volatility clustering, RSI and MACD readings, cites statistical anomalies",
        "opening_hook": "opens with a striking statistical fact about today's market move",
        "signature_phrase": "The numbers are telling us something the narrative is missing.",
    },
    {
        "name": "Veteran Market Commentator",
        "tone": "conversational and passionate",
        "style": "uses vivid metaphors comparing markets to cricket and monsoons, explains complex concepts with everyday Indian analogies, occasionally sarcastic about Fed or SEBI policy",
        "opening_hook": "opens with a relatable real-world analogy for today's market",
        "signature_phrase": "This market is teaching us a lesson we should have already known.",
    },
    {
        "name": "Institutional Flow Analyst",
        "tone": "sharp and urgent",
        "style": "focuses on FII/DII data, block deals, bulk trades, short punchy sentences mixed with detailed flow analysis, references specific sector rotations",
        "opening_hook": "opens with a specific institutional flow anomaly spotted today",
        "signature_phrase": "Follow the money, not the noise.",
    },
    {
        "name": "Global Macro Strategist",
        "tone": "calm and educational",
        "style": "connects global dots, explains how US Treasury moves affect Indian IT stocks, how China PMI impacts Indian metals, patient explanations for serious retail investors",
        "opening_hook": "opens by connecting an unexpected global event to Indian markets",
        "signature_phrase": "In a connected world, no market is an island.",
    },
    {
        "name": "Technical Price Action Specialist",
        "tone": "bold and opinionated",
        "style": "references candlestick patterns by name, Fibonacci levels, volume profile, market structure HH/HL/LH/LL, takes strong directional views with specific entry/exit logic",
        "opening_hook": "opens with a specific chart pattern forming right now",
        "signature_phrase": "Price is the only truth in this market.",
    },
]
persona = PERSONAS[now.weekday() % len(PERSONAS)]

ARTICLE_STRUCTURES = ["standard", "india_first", "theme_driven", "contrarian"]
structure = ARTICLE_STRUCTURES[now.day % len(ARTICLE_STRUCTURES)]

# ─── 1. Multi-Region Google Trends ───────────────────────────────────────────
def get_google_trends():
    all_trends = []
    regions = [("US", "-330"), ("IN", "-330"), ("GB", "0")]
    finance_keywords = [
        'stock', 'market', 'nifty', 'sensex', 'nasdaq', 'bitcoin', 'crypto',
        'gold', 'oil', 'fed', 'inflation', 'economy', 'bank', 'finance',
        'invest', 'trade', 'dollar', 'rupee', 'earnings', 'ipo', 'gdp',
        'recession', 'rally', 'crash', 'bull', 'bear', 'rate', 'rbi', 'sebi',
        'nvidia', 'apple', 'tesla', 'google', 'amazon', 'meta', 'ai', 'tech',
        'equity', 'bond', 'yield', 'hedge', 'fund', 'etf', 'crypto'
    ]
    for geo, tz in regions:
        url = f"https://trends.google.com/trends/api/dailytrends?hl=en-US&tz={tz}&geo={geo}"
        try:
            r = requests.get(url, timeout=10)
            clean_json = r.text.replace(")]}',\n", "")
            data = json.loads(clean_json)
            for day in data['default']['trendingSearchesDays']:
                for item in day['trendingSearches']:
                    query = item['title']['query']
                    if any(kw in query.lower() for kw in finance_keywords):
                        all_trends.append(query)
        except:
            continue

    if len(all_trends) < 5:
        all_trends = [
            "Stock Market Today", "NIFTY Analysis", "NASDAQ Forecast",
            "Bitcoin Price", "Gold Rally 2026", "Fed Rate Decision",
            "Indian Stock Market", "S&P 500 Outlook", "Crude Oil Price",
            "AI Stocks 2026", "Emerging Markets", "Global Market Crash"
        ]

    seen = set()
    unique = []
    for t in all_trends:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique.append(t)
    return unique[:12]

# ─── 2. Multi-Source News ────────────────────────────────────────────────────
def get_live_news():
    all_headlines = []
    queries = [
        "NASDAQ+Nvidia+AI+tech+earnings+today",
        "Fed+interest+rate+inflation+CPI+Powell+2026",
        "S%26P+500+market+outlook+today",
        "global+stock+market+crash+rally+today",
        "NIFTY+50+SENSEX+Indian+market+today",
        "RBI+monetary+policy+rupee+India+2026",
        "FII+DII+foreign+institutional+India+flows",
        "Indian+IPO+NSE+BSE+listing+today",
        "Crude+Oil+OPEC+price+today+2026",
        "Gold+Silver+commodities+rally+2026",
        "Bitcoin+Ethereum+crypto+market+today",
        "Dollar+Index+DXY+currency+market",
        "China+economy+stimulus+market+2026",
        "European+market+ECB+FTSE+today",
        "Japan+Nikkei+Bank+of+Japan+2026",
        "geopolitical+risk+market+impact+2026",
    ]
    for query in queries:
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        try:
            r = requests.get(url, timeout=8)
            root = ET.fromstring(r.content)
            items = root.findall('.//item')
            for item in items[:2]:
                title_el  = item.find('title')
                pub_el    = item.find('pubDate')
                source_el = item.find('source')
                if title_el is not None:
                    title     = title_el.text
                    date_text = pub_el.text[:16] if pub_el is not None else ""
                    source    = source_el.text if source_el is not None else "News"
                    all_headlines.append(f"[{date_text}] [{source}] {title}")
        except:
            continue
    random.shuffle(all_headlines)
    selected = all_headlines[:25] if all_headlines else ["Global markets active today."]
    return "\n".join(selected)

# ─── 3. Live Market Prices ────────────────────────────────────────────────────
def get_live_prices():
    symbols = {
        "NIFTY 50":      "^NSEI",
        "SENSEX":        "^BSESN",
        "Bank Nifty":    "^NSEBANK",
        "India VIX":     "^INDIAVIX",
        "S&P 500":       "^GSPC",
        "NASDAQ":        "^IXIC",
        "Dow Jones":     "^DJI",
        "US 10Y Yield":  "^TNX",
        "FTSE 100":      "^FTSE",
        "Nikkei 225":    "^N225",
        "Hang Seng":     "^HSI",
        "DAX":           "^GDAXI",
        "Gold":          "GC=F",
        "Silver":        "SI=F",
        "Crude Oil WTI": "CL=F",
        "Natural Gas":   "NG=F",
        "Bitcoin":       "BTC-USD",
        "Ethereum":      "ETH-USD",
        "USD/INR":       "INR=X",
        "DXY (Dollar)":  "DX-Y.NYB",
        "EUR/USD":       "EURUSD=X",
    }
    prices = {}
    for name, symbol in symbols.items():
        try:
            url     = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d"
            headers = {"User-Agent": "Mozilla/5.0"}
            r       = requests.get(url, headers=headers, timeout=8)
            data    = r.json()
            meta    = data['chart']['result'][0]['meta']
            current = round(meta.get('regularMarketPrice', 0), 2)
            prev    = round(meta.get('chartPreviousClose', current), 2)
            change  = round(current - prev, 2)
            pct     = round((change / prev) * 100, 2) if prev else 0
            arrow   = "▲" if change >= 0 else "▼"
            prices[name] = {
                "price":   current,
                "change":  change,
                "pct":     pct,
                "display": f"{current:,} {arrow} {abs(pct)}%"
            }
        except:
            prices[name] = {"price": 0, "change": 0, "pct": 0, "display": "N/A"}
    return prices

# ─── 4. Fear & Greed Index ────────────────────────────────────────────────────
def get_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=6)
        d = r.json()['data'][0]
        return f"{d['value']} — {d['value_classification']}"
    except:
        return "Unavailable"

# ─── 5. Identify Top Story ────────────────────────────────────────────────────
def identify_top_story(prices, trends, news):
    stories = []
    for name, data in prices.items():
        if abs(data.get('pct', 0)) >= 1.5:
            direction = "surging" if data['pct'] > 0 else "falling"
            stories.append(f"{name} {direction} {abs(data['pct'])}%")
    if trends:
        stories.append(f"Top trending: {trends[0]}")
    first_headline = news.split('\n')[0] if news else ""
    if first_headline:
        stories.append(f"News: {first_headline}")
    return "\n".join(stories[:3]) if stories else "Mixed global market session today."

# ─── 6. Cleanup old posts ────────────────────────────────────────────────────
def cleanup_old_posts():
    try:
        files = sorted([f for f in os.listdir(POSTS_DIR) if f.endswith('.md')])
        if len(files) > MAX_POSTS:
            for fname in files[:len(files) - MAX_POSTS]:
                os.remove(os.path.join(POSTS_DIR, fname))
                print(f"Removed: {fname}")
    except Exception as e:
        print(f"Cleanup warning: {e}")

# ─── 7. Main Generator ───────────────────────────────────────────────────────
def generate_full_report():
    print("Fetching live data...")
    news       = get_live_news()
    trends     = get_google_trends()
    prices     = get_live_prices()
    fear_greed = get_fear_greed()
    top_story  = identify_top_story(prices, trends, news)

    print(f"Top story: {top_story[:80]}")
    print(f"Trending: {', '.join(trends[:5])}")

    price_lines  = "\n".join([f"  - {k}: {v['display']}" for k, v in prices.items()])
    nifty_price  = prices.get("NIFTY 50",  {}).get("price", 24000)
    nifty_pct    = prices.get("NIFTY 50",  {}).get("pct", 0)
    btc_price    = prices.get("Bitcoin",   {}).get("price", 65000)
    gold_price   = prices.get("Gold",      {}).get("price", 5200)
    dxy_display  = prices.get("DXY (Dollar)", {}).get("display", "N/A")
    vix_display  = prices.get("India VIX", {}).get("display", "N/A")

    top_trend_slug = trends[0].lower().replace(' ', '-').replace('/', '-')[:30] if trends else "market"
    slug_bases = [
        f"nifty-{top_trend_slug}",
        f"global-market-{top_trend_slug}",
        f"stock-market-{top_trend_slug}",
        f"market-analysis-{top_trend_slug}",
        f"trading-signals-{top_trend_slug}",
    ]
    chosen_slug = f"{date_str}-{random.choice(slug_bases)}"
    file_path   = os.path.join(POSTS_DIR, f"{chosen_slug}.md")

    structure_map = {
        "standard":    "Start global (US/Europe/Asia), then zoom into India with specific implications.",
        "india_first": "Lead with NIFTY/Indian market analysis. Then explain which global factors are causing it.",
        "theme_driven": f"The dominant theme today: {top_story}. Every section connects back to this theme.",
        "contrarian":  "Challenge the mainstream narrative throughout. What is everyone getting wrong? Back every view with live data.",
    }

    prompt = f"""
You are the AI360Trading Intelligence Desk writing as a {persona['name']}.
Tone: {persona['tone']}. Style: {persona['style']}.
Opening approach: {persona['opening_hook']}.
Core lens: {persona['signature_phrase']}

Today is {day_name}, {date_display}.
Structure: {structure_map[structure]}

TARGET READERS: Indian retail traders, US investors watching emerging markets,
global crypto traders, European investors, Southeast Asian traders.
Write so ALL these readers find genuine value.

TODAY'S BIGGEST STORY:
{top_story}

Write a COMPLETE ORIGINAL 2,000-word Global Market Intelligence Report
for ai360trading.in that ranks on Google worldwide.

LIVE MARKET DATA — USE EXACT NUMBERS:
{price_lines}

Crypto Fear & Greed: {fear_greed}
India VIX: {vix_display}
Dollar Index: {dxy_display}
NIFTY: {nifty_price} ({'+' if nifty_pct >= 0 else ''}{nifty_pct}%)
Bitcoin: {btc_price}
Gold: {gold_price}

NEWS CONTEXT (background only — write YOUR OWN original analysis):
{news}

WORLDWIDE TRENDING SEARCHES (weave naturally for SEO):
{', '.join(trends)}

WRITING RULES — FOLLOW STRICTLY:
1. VARY sentence length dramatically. Short punchy lines. Then longer analytical
   sentences connecting multiple data points to explain the mechanism behind
   a market move with genuine insight readers cannot find elsewhere.
2. BANNED PHRASES — never use:
   "In conclusion", "It is worth noting", "It is important to",
   "This underscores", "This highlights", "Navigating", "Landscape",
   "Delve into", "In today's fast-paced", "In the realm of",
   "It is clear that", "Furthermore", "Moreover", "To summarize",
   "As we can see", "One cannot deny", "It goes without saying"
3. Include ONE specific historical market parallel with exact month and year
4. Include ONE specific NIFTY sector performing unusually today with reason
5. Include ONE contrarian view backed by specific data from live prices
6. Reference India VIX reading and explain implications for options traders
7. Write questions as H3 subheadings where natural — Google loves these
8. Every paragraph must add value — delete any paragraph that just restates facts

SEO FOR WORLDWIDE TRAFFIC:
- Include naturally: "global market intelligence", "nifty analysis today",
  "stock market outlook {date_display}", "trading signals", "market report"
- Weave in: {', '.join(trends[:6])}
- Include long-tail phrases: "should I buy nifty today", "gold price forecast",
  "is bitcoin going up", "stock market going up or down"

OUTPUT FORMAT:
First line: META_DESCRIPTION: <150-155 characters including date and key data point>

Then article with this structure:

## Market Snapshot — {date_display}
(Open with {persona['opening_hook']}. Weave all major prices into one narrative.
Reference India VIX. Reference top trending topic. End with a hook.)

## {trends[0] if trends else 'The Story Driving Global Markets Today'}
(Deep original analysis. Historical parallel with specific date.
Specific implication for Indian AND global traders.)

## NIFTY 50 Analysis — {date_display}
### What FII and DII Flows Tell Us Today
### Which NIFTY Sector Is Moving and Why
### Key NIFTY Support and Resistance Levels
(S1={round(nifty_price*0.986,0)}, S2={round(nifty_price*0.972,0)}, R1={round(nifty_price*1.014,0)}, R2={round(nifty_price*1.028,0)})

## Wall Street and Global Technology
### Is the NASDAQ Rally Sustainable Right Now?
### What Earnings Season Is Really Signaling

## European and Asian Markets
### FTSE 100 and What It Signals for Emerging Markets
### China and Japan — The Data Most Traders Are Missing

## Gold, Oil and the Dollar
### Why Gold at {gold_price} Matters for Indian Investors
### Crude Oil and India's Trade Deficit

## Bitcoin and Crypto — Fear and Greed at {fear_greed}
### Is This a Buying Opportunity or Warning Sign?

## What Smart Money Is Doing Right Now
(Contrarian view. Specific evidence. ONE actionable insight.)

## Global Pivot Point Table — {date_display}
### Support and Resistance for Major Markets
| Instrument | Price | S2 | S1 | R1 | R2 |
|------------|-------|----|----|----|----|
(Fill with actual live prices. Calculate pivot points properly.)

## AI360Trading Final View — {date_display}
(Bold 2-paragraph directional view. Specific levels. Next 24-48 hours.
End with EXACTLY: *Trade smart. Stay informed. — AI360Trading Intelligence Desk*)

## Trending Market Topics
{' '.join(['#' + t.replace(' ', '').replace('/', '') for t in trends[:8]])}
#GlobalMarkets #NIFTY50 #StockMarket #ai360trading #TradingSignals #IndianStockMarket

---
*Published: {date_display} | {now.strftime('%I:%M %p')} IST | AI360Trading Intelligence Desk*
*Educational content only. Not SEBI registered financial advice. Read our [Legal Disclaimer](/disclaimer/) before trading.*

<h3>Share this Analysis</h3>
<div class="share-bar">
  <a href="https://wa.me/?text={{{{ page.title }}}} - {{{{ site.url }}}}{{{{ page.url }}}}" class="share-btn btn-whatsapp">WhatsApp</a>
  <a href="https://twitter.com/intent/tweet?text={{{{ page.title }}}}&url={{{{ site.url }}}}{{{{ page.url }}}}" class="share-btn btn-twitter">Twitter</a>
  <a href="https://t.me/share/url?url={{{{ site.url }}}}{{{{ page.url }}}}&text={{{{ page.title }}}}" class="share-btn btn-telegram">Telegram</a>
</div>

<div class="sub-box">
  <h3>Global Trade Signals</h3>
  <p>Join our international community for real-time macro alerts.</p>
  <a href="https://t.me/{{{{ site.telegram_username }}}}">Join Telegram Now</a>
</div>
"""

    try:
        print("Generating article...")
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are the AI360Trading Intelligence Desk writing as a {persona['name']}. "
                        f"Tone: {persona['tone']}. Style: {persona['style']}. "
                        f"Core lens: {persona['signature_phrase']} "
                        "You write 100% original human-sounding financial analysis. "
                        "News headlines are background context only — never copy or paraphrase them. "
                        "Form independent views backed by live price data. "
                        "Vary sentence length dramatically. Never use AI giveaway phrases. "
                        "Never include image tags. Every paragraph earns its place. "
                        "Goal: every worldwide reader — Indian trader, US investor, "
                        "European analyst — finds genuine value in this article."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.88,
            max_tokens=5000,
            top_p=0.95,
            frequency_penalty=0.35,
            presence_penalty=0.25,
        )
        content = completion.choices[0].message.content

        # Extract META_DESCRIPTION
        meta_description = (
            f"{date_display} Global Market Intelligence — NIFTY, Gold, Bitcoin "
            f"& worldwide market analysis by AI360Trading."
        )[:155]
        cleaned_lines = []
        for line in content.split("\n"):
            if line.strip().startswith("META_DESCRIPTION:"):
                extracted = line.replace("META_DESCRIPTION:", "").strip().strip('"')
                if 100 < len(extracted) <= 160:
                    meta_description = extracted
            else:
                cleaned_lines.append(line)
        content = "\n".join(cleaned_lines).lstrip("\n")

        # Front matter
        header = (
            "---\n"
            "layout: post\n"
            f"title: \"{date_display} | Global Market Intelligence Report\"\n"
            f"date: {date_str}\n"
            "author: \"AI360Trading Intelligence Desk\"\n"
            f"permalink: /analysis/{chosen_slug}/\n"
            f"description: \"{meta_description}\"\n"
            f"keywords: \"global market intelligence report, nifty analysis {date_str}, "
            f"stock market today, {', '.join(trends[:4]).lower()}, "
            f"indian market outlook, trading signals {date_str}\"\n"
            "categories: [Market-Intelligence]\n"
            "tags: [NIFTY, NASDAQ, Gold, Bitcoin, GlobalMacro, IndianMarket, TechnicalAnalysis, TradingSignals]\n"
            f"nifty_level: \"{prices.get('NIFTY 50',{}).get('display','N/A')}\"\n"
            f"bitcoin_level: \"{prices.get('Bitcoin',{}).get('display','N/A')}\"\n"
            f"gold_level: \"{prices.get('Gold',{}).get('display','N/A')}\"\n"
            f"fear_greed: \"{fear_greed}\"\n"
            f"trending: \"{', '.join(trends[:5])}\"\n"
            "---\n\n"
        )

        if not os.path.exists(POSTS_DIR):
            os.makedirs(POSTS_DIR)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header + content)

        print(f"\n✅ Published  : /analysis/{chosen_slug}/")
        print(f"   Persona   : {persona['name']}")
        print(f"   Structure : {structure}")
        print(f"   Trending  : {trends[0] if trends else 'N/A'}")
        print(f"   NIFTY     : {prices.get('NIFTY 50',{}).get('display','N/A')}")
        print(f"   Gold      : {prices.get('Gold',{}).get('display','N/A')}")
        print(f"   Bitcoin   : {prices.get('Bitcoin',{}).get('display','N/A')}")
        print(f"   F&G Index : {fear_greed}")
        print(f"   Meta      : {meta_description[:80]}...")

        cleanup_old_posts()

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    generate_full_report()
