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
        "style": "uses F&O terminology naturally, references open interest and PCR ratios, draws parallels with specific historical dates, occasionally uses Hindi trading phrases, references Wall Street desk conversations",
        "opening_hook": "leads with the most surprising data point of the day — something the mainstream financial press missed",
        "signature_phrase": "The options market never lies.",
        "us_angle": "connects Indian derivatives market structure to CME futures positioning and US options expiry cycles",
    },
    {
        "name": "Macro Economist",
        "tone": "analytical and precise",
        "style": "references RBI policy decisions, bond yield spreads, current account deficit implications, draws macro cycles from 2008, 2013, 2020, quotes Fed minutes and Treasury data directly",
        "opening_hook": "starts with a macro paradox hidden in today's data that challenges the consensus view",
        "signature_phrase": "The macro picture tells a different story than the headlines.",
        "us_angle": "explains Fed policy transmission mechanism into Indian bond markets and FII flows with specific yield spread analysis",
    },
    {
        "name": "Quantitative Analyst",
        "tone": "methodical and number-heavy",
        "style": "references standard deviation moves, beta correlations, volatility clustering, RSI and MACD readings, cites statistical anomalies, uses precise decimal places",
        "opening_hook": "opens with a striking statistical fact about today's market move that most retail traders will never see",
        "signature_phrase": "The numbers are telling us something the narrative is missing.",
        "us_angle": "correlates S&P 500 implied volatility (VIX) with India VIX, shows statistical relationship between NASDAQ momentum and Nifty IT sector",
    },
    {
        "name": "Veteran Market Commentator",
        "tone": "conversational and passionate",
        "style": "uses vivid metaphors comparing markets to cricket and monsoons, explains complex concepts with everyday Indian analogies, occasionally sarcastic about Fed or SEBI policy, deeply human voice",
        "opening_hook": "opens with a relatable real-world analogy that immediately makes the market move feel personal and urgent",
        "signature_phrase": "This market is teaching us a lesson we should have already known.",
        "us_angle": "explains how decisions made in Washington DC and on Wall Street at 2:30am IST determine what happens on Dalal Street at 9:15am",
    },
    {
        "name": "Institutional Flow Analyst",
        "tone": "sharp and urgent",
        "style": "focuses on FII/DII data, block deals, bulk trades, short punchy sentences mixed with detailed flow analysis, references specific sector rotations, names real institutional patterns",
        "opening_hook": "opens with a specific institutional flow anomaly spotted today that retail traders are completely unaware of",
        "signature_phrase": "Follow the money, not the noise.",
        "us_angle": "tracks global fund flows from US pension funds and hedge funds into emerging markets, explains why Brazil and India move together on risk-off days",
    },
    {
        "name": "Global Macro Strategist",
        "tone": "calm and educational",
        "style": "connects global dots, explains how US Treasury moves affect Indian IT stocks, how China PMI impacts Indian metals, patient explanations with clear cause-and-effect chains for serious investors worldwide",
        "opening_hook": "opens by connecting an unexpected global event to Indian markets in a way that makes the reader say 'I never thought of it that way'",
        "signature_phrase": "In a connected world, no market is an island.",
        "us_angle": "builds complete picture from Fed decision → Dollar Index → Emerging Market capital flows → India/Brazil currency impact → equity market consequences",
    },
    {
        "name": "Technical Price Action Specialist",
        "tone": "bold and opinionated",
        "style": "references candlestick patterns by name, Fibonacci levels, volume profile, market structure HH/HL/LH/LL, takes strong directional views with specific entry/exit logic, never vague",
        "opening_hook": "opens with a specific chart pattern forming right now across multiple timeframes that signals a high-probability move",
        "signature_phrase": "Price is the only truth in this market.",
        "us_angle": "draws technical confluence between S&P 500 key levels and NIFTY 50, shows how US overnight price action sets up Indian market open structure",
    },
]
persona = PERSONAS[now.weekday() % len(PERSONAS)]

ARTICLE_STRUCTURES = ["standard", "india_first", "theme_driven", "contrarian", "us_focus"]
structure = ARTICLE_STRUCTURES[now.day % len(ARTICLE_STRUCTURES)]

# ─── 1. Multi-Region Google Trends ───────────────────────────────────────────
def get_google_trends():
    all_trends = []
    regions = [("US", "-330"), ("IN", "-330"), ("GB", "0"), ("BR", "-180")]
    finance_keywords = [
        'stock', 'market', 'nifty', 'sensex', 'nasdaq', 'bitcoin', 'crypto',
        'gold', 'oil', 'fed', 'inflation', 'economy', 'bank', 'finance',
        'invest', 'trade', 'dollar', 'rupee', 'earnings', 'ipo', 'gdp',
        'recession', 'rally', 'crash', 'bull', 'bear', 'rate', 'rbi', 'sebi',
        'nvidia', 'apple', 'tesla', 'google', 'amazon', 'meta', 'ai', 'tech',
        'equity', 'bond', 'yield', 'hedge', 'fund', 'etf', 'crypto',
        'ibovespa', 'bovespa', 'brazil', 'real', 'selic', 'petrobras',
        's&p', 'sp500', 'dow', 'treasury', 'powell', 'fomc', 'cpi',
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
            "S&P 500 Today", "Stock Market Today", "NIFTY Analysis",
            "NASDAQ Forecast", "Bitcoin Price Today", "Gold Rally 2026",
            "Fed Rate Decision", "Indian Stock Market", "Crude Oil Price",
            "AI Stocks 2026", "Emerging Markets", "Brazil Stock Market",
            "IBOVESPA Today", "Dollar Index Today", "US Inflation Data",
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
        "Brazil+IBOVESPA+Bovespa+market+today",
        "emerging+markets+US+dollar+flows+2026",
        "S%26P500+support+resistance+today",
        "stock+market+crash+or+rally+today",
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
        "IBOVESPA":      "^BVSP",
        "Gold":          "GC=F",
        "Silver":        "SI=F",
        "Crude Oil WTI": "CL=F",
        "Natural Gas":   "NG=F",
        "Bitcoin":       "BTC-USD",
        "Ethereum":      "ETH-USD",
        "USD/INR":       "INR=X",
        "USD/BRL":       "BRL=X",
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

    price_lines   = "\n".join([f"  - {k}: {v['display']}" for k, v in prices.items()])
    nifty_price   = prices.get("NIFTY 50",    {}).get("price", 24000)
    nifty_pct     = prices.get("NIFTY 50",    {}).get("pct", 0)
    btc_price     = prices.get("Bitcoin",     {}).get("price", 65000)
    gold_price    = prices.get("Gold",        {}).get("price", 5200)
    sp500_price   = prices.get("S&P 500",     {}).get("price", 5500)
    sp500_pct     = prices.get("S&P 500",     {}).get("pct", 0)
    nasdaq_price  = prices.get("NASDAQ",      {}).get("price", 17000)
    ibov_display  = prices.get("IBOVESPA",    {}).get("display", "N/A")
    ibov_pct      = prices.get("IBOVESPA",    {}).get("pct", 0)
    dxy_display   = prices.get("DXY (Dollar)",{}).get("display", "N/A")
    dxy_price     = prices.get("DXY (Dollar)",{}).get("price", 104)
    vix_display   = prices.get("India VIX",   {}).get("display", "N/A")
    brl_display   = prices.get("USD/BRL",     {}).get("display", "N/A")

    top_trend_slug = trends[0].lower().replace(' ', '-').replace('/', '-')[:30] if trends else "market"
    slug_bases = [
        f"nifty-{top_trend_slug}",
        f"global-market-{top_trend_slug}",
        f"stock-market-{top_trend_slug}",
        f"market-analysis-{top_trend_slug}",
        f"trading-signals-{top_trend_slug}",
        f"sp500-nasdaq-{top_trend_slug}",
        f"wall-street-{top_trend_slug}",
        f"global-markets-today-{top_trend_slug}",
    ]
    chosen_slug = f"{date_str}-{random.choice(slug_bases)}"
    file_path   = os.path.join(POSTS_DIR, f"{chosen_slug}.md")

    structure_map = {
        "standard":    "Start with US/Wall Street overnight action and its direct impact on Asian and Indian markets. Then European context. Then deep India analysis.",
        "india_first": "Lead with NIFTY/Indian market analysis first. Then explain which global factors — Fed, Dollar, China — are the root cause behind today's Indian market move.",
        "theme_driven": f"The dominant theme today: {top_story}. Build every section around this central theme. Show how it ripples from Wall Street to Dalal Street to Bovespa.",
        "contrarian":  "Challenge the mainstream market narrative throughout. What is the crowd getting wrong today? Back every contrarian view with hard data from live prices. End each section with the view that smart money is actually taking.",
        "us_focus":    "Lead with S&P 500 and NASDAQ deep analysis. Explain the Fed/macro backdrop. Then show how this directly impacts Indian and Brazilian markets. US readers should feel this was written for them — Indian and Brazilian readers should understand exactly why their market moved the way it did.",
    }

    prompt = f"""
You are Amit Kumar, founder of AI360Trading — a respected independent market analyst
and algorithmic trading researcher based in India with deep knowledge of both Indian
and global financial markets.

You write as: {persona['name']}
Tone: {persona['tone']}
Style: {persona['style']}
Opening approach: {persona['opening_hook']}
Core lens: {persona['signature_phrase']}
Global connection: {persona['us_angle']}

Today is {day_name}, {date_display}.
Article structure today: {structure_map[structure]}

PRIMARY TARGET READERS (write so EACH group finds genuine value):
1. US retail investors and day traders searching Google for "stock market today",
   "S&P 500 outlook", "should I buy stocks today", "NASDAQ forecast today"
2. Brazilian investors searching "mercado financeiro hoje", "IBOVESPA hoje",
   "bolsa de valores hoje", "dolar hoje"
3. Indian traders searching "nifty analysis today", "trading signals today",
   "nifty support resistance", "best stocks to buy today"
4. Global macro investors searching "emerging markets outlook", "DXY impact",
   "Fed rate decision impact", "global market intelligence"

TODAY'S BIGGEST STORY:
{top_story}

Write a COMPLETE ORIGINAL 2,200-word Global Market Intelligence Report
that reads as if written by a seasoned human analyst — not AI.
Every paragraph must contain a specific data point, a specific insight,
or a specific implication that readers cannot find in generic market summaries.

LIVE MARKET DATA — USE EXACT NUMBERS THROUGHOUT:
{price_lines}

Crypto Fear & Greed: {fear_greed}
India VIX: {vix_display}
Dollar Index: {dxy_display}
S&P 500: {sp500_price} ({'+' if sp500_pct >= 0 else ''}{sp500_pct}%)
NASDAQ: {nasdaq_price}
NIFTY: {nifty_price} ({'+' if nifty_pct >= 0 else ''}{nifty_pct}%)
IBOVESPA: {ibov_display}
USD/BRL: {brl_display}
Bitcoin: {btc_price}
Gold: {gold_price}
DXY: {dxy_price}

NEWS CONTEXT (background only — write 100% YOUR OWN original analysis and views):
{news}

WORLDWIDE TRENDING SEARCHES (weave naturally — these are what people are Googling):
{', '.join(trends)}

═══════════════════════════════════════════════
CRITICAL WRITING RULES — EVERY RULE IS MANDATORY
═══════════════════════════════════════════════

RULE 1 — SOUND HUMAN, NOT AI:
- Vary sentence length dramatically. One sentence can be four words. The next
  can build a complete chain of cause-and-effect connecting a Fed statement to
  rupee depreciation to FII selling in Indian midcaps — and it should read as
  naturally as a veteran analyst dictating notes between trades.
- Use occasional first-person voice: "What I find interesting here...",
  "In my view...", "The data is telling me...", "I've seen this pattern before..."
- Include ONE moment of genuine uncertainty: "I'll be honest — this is not a
  clear setup." or "The data is mixed here and anyone claiming certainty is lying."
- Reference a specific time: "As of the 9:15am bell...", "At 2:30pm EST...",
  "Before the European open..."

RULE 2 — BANNED PHRASES (automatic fail if used even once):
"In conclusion", "It is worth noting", "It is important to",
"This underscores", "This highlights", "Navigating", "Landscape",
"Delve into", "In today's fast-paced", "In the realm of",
"It is clear that", "Furthermore", "Moreover", "To summarize",
"As we can see", "One cannot deny", "It goes without saying",
"Seasoned", "Bustling", "Robust growth", "Game-changer",
"Paradigm shift", "Deep dive", "Shed light", "Unlock",
"At the end of the day", "It's no secret", "The bottom line is"

RULE 3 — MANDATORY CONTENT ELEMENTS:
- ONE specific historical market parallel with exact month and year
  (e.g., "This mirrors what happened in September 2022 when...")
- ONE specific NIFTY sector performing unusually today with the reason why
- ONE contrarian view backed by specific data from the live prices above
- Reference India VIX {vix_display} and explain what it means for options traders RIGHT NOW
- Reference IBOVESPA {ibov_display} and explain the Brazil-India emerging market connection
- At least ONE specific support/resistance level for S&P 500 AND NIFTY
- ONE specific mention of DXY {dxy_price} and its impact on emerging markets

RULE 4 — SEO FOR US, BRAZIL AND INDIA:
Weave these naturally — never stuff them awkwardly:
US phrases: "stock market today {date_display}", "S&P 500 forecast",
"NASDAQ outlook today", "best stocks to buy today", "is stock market going up",
"Federal Reserve impact on markets", "stock market analysis today"
Brazil phrases: "IBOVESPA analysis", "Brazil stock market today",
"emerging markets outlook", "dollar impact on Brazil"
India phrases: "nifty analysis today", "trading signals India",
"nifty support resistance today", "indian stock market outlook"
Long-tail: "should I buy S&P 500 today", "is gold a good investment now",
"is bitcoin going up or down", "global market intelligence report"
Trending today: {', '.join(trends[:6])}

RULE 5 — STRUCTURE DISCIPLINE:
Write questions as H3 subheadings where natural — Google loves these.
Every paragraph earns its place. Delete any paragraph that just restates
known facts without adding original analysis or implication.

═══════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════

First line: META_DESCRIPTION: <150-155 characters, include date and a specific data point>

Then the article:

## Market Snapshot — {date_display}
(Open with {persona['opening_hook']}. Reference S&P 500 AND NIFTY in opening.
Weave in DXY, India VIX, IBOVESPA. End paragraph with a hook that makes
the reader want to keep reading.)

## {trends[0] if trends else 'The Story Every Trader Needs to Understand Today'}
(Deep original analysis. Historical parallel with specific date.
Specific implications for US investors, Indian traders, AND Brazilian investors.)

## S&P 500 and NASDAQ — What Wall Street Is Really Telling Us
### Is This Rally Built on Solid Ground or Borrowed Time?
### What the {sp500_price} Level Means for Global Risk Appetite
(US-focused section. Technical levels. Fed context. Connect to global markets.)

## NIFTY 50 Analysis — {date_display}
### What FII and DII Flows Are Signaling Right Now
### Which NIFTY Sector Is Moving and Why Most Traders Are Missing It
### Key NIFTY Support and Resistance Levels for Today
(S1={round(nifty_price*0.986,0)}, S2={round(nifty_price*0.972,0)}, R1={round(nifty_price*1.014,0)}, R2={round(nifty_price*1.028,0)})

## Brazil and Emerging Markets — The IBOVESPA Signal
### Why Brazil and India Move Together When the Dollar Moves
### What IBOVESPA at {ibov_display} Is Telling Global Fund Managers
(Brazil section — valuable for Brazilian readers AND global macro investors.
Explain EM correlation, DXY impact, capital flow dynamics.)

## European and Asian Markets
### FTSE 100 and DAX — Reading the Risk Appetite Signal
### China and Japan — The Data Most Traders Ignore at Their Peril

## Gold, Oil and the Dollar
### ### Why Gold at {gold_price} Matters Whether You Trade in Mumbai, New York or São Paulo
### Crude Oil and the Hidden Inflation Signal

## Bitcoin and Crypto — Fear and Greed at {fear_greed}
### Is the Smart Money Accumulating or Distributing Right Now?

## What Smart Money Is Doing That Retail Traders Are Not
(Contrarian view. Specific evidence from live prices. ONE actionable framework —
not a tip, but a way of thinking about the market right now.)

## Global Pivot Point Table — {date_display}
### Support and Resistance Levels Across Major Markets
| Instrument | Price | S2 | S1 | R1 | R2 |
|------------|-------|----|----|----|----|
(Fill with actual live prices. Calculate pivot points properly. Include
S&P 500, NASDAQ, NIFTY, IBOVESPA, Gold, Bitcoin, Crude Oil.)

## AI360Trading Final View — {date_display}
(Bold 2-paragraph directional view from Amit Kumar. Specific levels.
What to watch in the next 24-48 hours. One clear risk to this view.
End with EXACTLY: *Trade smart. Stay informed. — Amit Kumar, AI360Trading*)

## Trending Market Topics
{' '.join(['#' + t.replace(' ', '').replace('/', '') for t in trends[:8]])}
#GlobalMarkets #NIFTY50 #SP500 #IBOVESPA #StockMarket #ai360trading
#TradingSignals #IndianStockMarket #BrazilStocks #EmergingMarkets

---
*Published: {date_display} | {now.strftime('%I:%M %p')} IST | Amit Kumar — AI360Trading*
*Educational content only. Not SEBI registered financial advice. Read our [Legal Disclaimer](/disclaimer/) before trading.*
"""

    try:
        print("Generating article...")
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are Amit Kumar, founder of AI360Trading — an independent market analyst "
                        f"and researcher writing as a {persona['name']}. "
                        f"Tone: {persona['tone']}. Style: {persona['style']}. "
                        f"Core lens: {persona['signature_phrase']} "
                        "You write 100% original human-sounding financial analysis that reads like "
                        "it was written by a seasoned professional who has skin in the game. "
                        "News headlines are background context only — never copy or paraphrase them. "
                        "Form independent views backed by live price data. "
                        "Your readers include US investors, Brazilian traders, and Indian retail traders — "
                        "write so all three groups find genuine value and insight. "
                        "Vary sentence length dramatically. Never use AI giveaway phrases. "
                        "Never include image tags. Every paragraph earns its place. "
                        "Occasionally use first-person voice. Show genuine uncertainty where it exists. "
                        "Reference specific times, specific levels, specific historical dates. "
                        "The goal: a reader in New York, São Paulo, or Mumbai should finish this "
                        "article and feel they understand the market better than before they started."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.88,
            max_tokens=5500,
            top_p=0.95,
            frequency_penalty=0.40,
            presence_penalty=0.30,
        )
        content = completion.choices[0].message.content

        # Extract META_DESCRIPTION
        meta_description = (
            f"{date_display} Global Market Intelligence — S&P 500, NIFTY, IBOVESPA, Gold & Bitcoin "
            f"analysis by AI360Trading."
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
            "author: \"Amit Kumar\"\n"
            f"permalink: /analysis/{chosen_slug}/\n"
            f"description: \"{meta_description}\"\n"
            f"keywords: \"global market intelligence report, nifty analysis {date_str}, "
            f"stock market today, S&P 500 outlook, IBOVESPA today, "
            f"{', '.join(trends[:4]).lower()}, "
            f"indian market outlook, trading signals {date_str}, "
            f"emerging markets today, brazil stock market\"\n"
            "categories: [Market-Intelligence]\n"
            f"nifty_level: \"{prices.get('NIFTY 50',{}).get('display','N/A')}\"\n"
            f"sp500_level: \"{prices.get('S&P 500',{}).get('display','N/A')}\"\n"
            f"ibovespa_level: \"{prices.get('IBOVESPA',{}).get('display','N/A')}\"\n"
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
        print(f"   S&P 500   : {prices.get('S&P 500',{}).get('display','N/A')}")
        print(f"   NIFTY     : {prices.get('NIFTY 50',{}).get('display','N/A')}")
        print(f"   IBOVESPA  : {prices.get('IBOVESPA',{}).get('display','N/A')}")
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
