import os
import pytz
import requests
import random
import json
import time
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
MAX_POSTS    = 60  # 4 articles/day — keep 15 days

# ─── 4 PILLAR TOPICS ─────────────────────────────────────────────────────────
PILLARS = [
    {
        "id": "stock-market",
        "name": "Stock Market",
        "permalink_base": "stock-market",
        "category": "Stock-Market",
        "tag": "stock-market",
        "primary_keywords": ["S&P 500", "NIFTY", "NASDAQ", "SENSEX", "IBOVESPA", "stock market today"],
        "us_keywords": ["stock market today", "S&P 500 forecast", "best stocks to buy today", "NASDAQ outlook"],
        "uk_keywords": ["FTSE 100 today", "UK stock market", "London stock exchange today"],
        "brazil_keywords": ["IBOVESPA hoje", "bolsa de valores hoje", "mercado financeiro"],
        "india_keywords": ["nifty analysis today", "trading signals India", "nifty support resistance"],
        "news_queries": [
            "S%26P+500+stock+market+today",
            "NASDAQ+outlook+today",
            "NIFTY+50+SENSEX+Indian+market",
            "IBOVESPA+Brazil+stock+market",
            "FTSE+100+UK+market+today",
            "global+stock+market+rally+crash",
            "Fed+interest+rate+stocks",
            "FII+DII+India+flows+today",
        ],
        "title_templates": [
            "NIFTY {direction} — Here Is What I Think Happens Next",
            "S&P 500 & NIFTY Today: The Level Nobody Is Watching ({date})",
            "{trend}: Why This Move Is Different From What Media Is Saying",
            "I Was Wrong About {trend} — Here Is What the Chart Actually Shows",
            "NIFTY {nifty} | The Trade Setup I Am Looking at Right Now",
            "Why Smart Money Is {direction} While Retail Panics — {date}",
            "The One Chart That Explains Today's Market Crash — {date}",
            "NIFTY Support & Resistance Today: Exact Levels for {date}",
        ],
        "article_focus": """Write a comprehensive stock market analysis covering:
- S&P 500 and NASDAQ deep technical and fundamental analysis
- NIFTY 50 and SENSEX India market analysis with FII/DII flows
- IBOVESPA Brazil market analysis and EM correlation
- FTSE 100 UK market overview
- Support/resistance levels for all major indices
- Sector rotation analysis — which sector is moving and why
- What smart money is doing vs retail traders""",
    },
    {
        "id": "bitcoin",
        "name": "Bitcoin & Crypto",
        "permalink_base": "bitcoin",
        "category": "Bitcoin-Crypto",
        "tag": "bitcoin",
        "primary_keywords": ["Bitcoin", "Ethereum", "crypto market today", "BTC price", "cryptocurrency"],
        "us_keywords": ["bitcoin price today", "crypto market today", "is bitcoin going up", "BTC USD today"],
        "uk_keywords": ["bitcoin price GBP", "crypto UK today", "bitcoin today pound"],
        "brazil_keywords": ["bitcoin hoje", "criptomoedas hoje", "bitcoin real hoje"],
        "india_keywords": ["bitcoin price INR today", "crypto India today", "bitcoin rupees today"],
        "news_queries": [
            "Bitcoin+price+today+2026",
            "crypto+market+today+2026",
            "Ethereum+price+today",
            "Bitcoin+ETF+institutional+buying",
            "crypto+regulation+SEC+2026",
            "altcoin+rally+today",
            "Bitcoin+price+prediction+2026",
            "DeFi+blockchain+crypto+news",
        ],
        "title_templates": [
            "Bitcoin ${btc} — Crypto Market Analysis {date}",
            "{trend}: Is Bitcoin Going Up or Down Today? {date} Analysis",
            "Bitcoin & Crypto {direction} | {trend} — {date} Report",
            "BTC at ${btc} — What Smart Money Is Doing Now | {date}",
            "{trend} Drives Crypto Markets — Bitcoin Analysis {date}",
            "Fear & Greed {fg}: Bitcoin {direction} — {date} Crypto Signals",
            "Bitcoin Price Today: {btc} — {date} Analysis for US, India and Brazil",
            "Crypto Market {direction} | Bitcoin ${btc} — {date} Intelligence",
        ],
        "article_focus": """Write a comprehensive crypto market analysis covering:
- Bitcoin price action, technical levels, support/resistance with exact numbers
- Ethereum and major altcoin analysis
- Crypto Fear & Greed Index interpretation and what it signals
- Institutional vs retail sentiment analysis
- Bitcoin correlation with S&P 500 and risk assets
- Regulatory news impact for US, India, and Brazil crypto markets
- DeFi developments and their market impact
- Bitcoin price prediction framework with specific levels for next 24-48 hours""",
    },
    {
        "id": "personal-finance",
        "name": "Personal Finance",
        "permalink_base": "personal-finance",
        "category": "Personal-Finance",
        "tag": "personal-finance",
        "primary_keywords": ["term life insurance", "best investment 2026", "retirement planning", "tax saving", "personal finance"],
        "us_keywords": ["best term life insurance USA 2026", "401k investing 2026", "mortgage rates today", "personal finance tips USA"],
        "uk_keywords": ["best ISA 2026 UK", "UK pension 2026", "life insurance UK", "best savings account UK"],
        "brazil_keywords": ["previdencia privada 2026", "seguro de vida Brasil", "melhores investimentos 2026"],
        "india_keywords": ["best term insurance India 2026", "SIP investment returns", "PPF vs ELSS 2026", "NPS pension India"],
        "news_queries": [
            "best+term+life+insurance+2026",
            "personal+finance+tips+2026",
            "mortgage+rates+today+2026",
            "401k+retirement+investing+2026",
            "best+savings+account+interest+2026",
            "income+tax+saving+India+2026",
            "SIP+mutual+fund+returns+2026",
            "health+insurance+comparison+2026",
        ],
        "title_templates": [
            "Best Term Life Insurance 2026 — US, UK & India Complete Guide",
            "{trend}: Personal Finance Guide for {date}",
            "I Ran the Numbers on SIP vs Lump Sum — The Answer Surprised Me",
            "Why Most Indians Are Getting Their Term Insurance Wrong in 2026",
            "{trend}: What This Means for Your SIP and Savings Right Now",
            "The Rs.10,000/Month Investment Plan That Actually Works in 2026",
            "Stop Waiting for the Perfect Time — Here Is What the Data Says",
            "Your Emergency Fund Is Probably Wrong — Here Is the Right Size",
            "How to Protect Your Money When Markets Are Crashing Like Today",
            "401k vs NPS vs ISA — Which Retirement Plan Wins in 2026?",
        ],
        "article_focus": """Write a comprehensive personal finance guide covering:
- Term life insurance comparison across US, UK, India, Brazil with actual rates
- Investment options compared: stocks, mutual funds/SIP, ETFs, bonds, real estate
- Tax saving strategies specific to each country with actionable steps
- Retirement planning: 401k (US), pension (UK), NPS/PPF (India)
- Emergency fund building and best savings account rates in 2026
- Credit score improvement tips for US and India
- How current market conditions affect personal finance decisions
- Practical advice readers can implement today — not generic advice""",
    },
    {
        "id": "ai-trading",
        "name": "AI & Trading Technology",
        "permalink_base": "ai-trading",
        "category": "AI-Trading",
        "tag": "ai-trading",
        "primary_keywords": ["AI trading 2026", "algorithmic trading", "fintech", "AI stock market", "trading technology"],
        "us_keywords": ["AI stock trading 2026", "best AI trading algorithm", "fintech stocks today", "AI investing USA"],
        "uk_keywords": ["AI trading UK 2026", "algorithmic trading London", "fintech UK stocks"],
        "brazil_keywords": ["trading automatizado Brasil", "inteligencia artificial investimentos", "fintech brasil 2026"],
        "india_keywords": ["algo trading India NSE", "AI trading bot India", "automated trading NSE BSE", "quant trading India"],
        "news_queries": [
            "AI+trading+algorithm+2026",
            "artificial+intelligence+stock+market+2026",
            "Nvidia+AI+chips+stocks+2026",
            "algorithmic+trading+India+NSE",
            "machine+learning+finance+2026",
            "AI+fintech+investment+2026",
            "ChatGPT+finance+trading+2026",
            "AI+hedge+fund+performance+2026",
        ],
        "title_templates": [
            "The AI Signal on NIFTY That I Almost Missed Today ({date})",
            "{trend}: What My Algorithm Is Showing vs What I Actually Think",
            "I Backtested This Strategy 5 Years — Here Are the Real Results",
            "Free AI Tools That Are Actually Useful for Trading in 2026",
            "Why AI Got {trend} Wrong — And What It Means for Your Trades",
            "The Algorithm Spotted This Pattern Before the Move — Here Is How",
            "AI vs Human Trader: Who Called {trend} Better? ({date})",
            "How I Use AI to Filter 90% of Bad Trades Before They Happen",
        ],
        "article_focus": """Write a comprehensive AI and algorithmic trading analysis covering:
- How AI and machine learning algorithms are reading current market signals
- Specific AI trading strategies working in today's market conditions
- Algorithmic trading setups for S&P 500, NIFTY, and Bitcoin with exact levels
- Fintech and AI company stocks: Nvidia, Microsoft, Google, OpenAI impact
- How retail traders can use free AI tools for better trading decisions today
- Statistical patterns and backtested edges in current market structure
- Risk management using algorithmic approaches
- AI-generated prediction for next 24-48 hours with specific price targets""",
    },
]

# ─── Writing Personas — 8 total, 2 pillar-specific ───────────────────────────
PERSONAS = [
    {
        "name": "Senior Derivatives Trader",
        "tone": "confident and contrarian",
        "style": "uses F&O terminology naturally, references open interest and PCR ratios, draws parallels with specific historical dates, references Wall Street desk conversations",
        "opening_hook": "leads with the most surprising data point of the day that mainstream financial press missed",
        "signature_phrase": "The options market never lies.",
    },
    {
        "name": "Macro Economist",
        "tone": "analytical and precise",
        "style": "references RBI/Fed policy decisions, bond yield spreads, draws macro cycles from 2008, 2013, 2020, quotes Treasury data directly",
        "opening_hook": "starts with a macro paradox hidden in today's data that challenges the consensus view",
        "signature_phrase": "The macro picture tells a different story than the headlines.",
    },
    {
        "name": "Quantitative Analyst",
        "tone": "methodical and number-heavy",
        "style": "references standard deviation moves, beta correlations, volatility clustering, RSI/MACD readings, cites statistical anomalies with precise decimals",
        "opening_hook": "opens with a striking statistical fact about today's market move that most retail traders will never see",
        "signature_phrase": "The numbers are telling us something the narrative is missing.",
    },
    {
        "name": "Veteran Market Commentator",
        "tone": "conversational and passionate",
        "style": "uses vivid metaphors, explains complex concepts with everyday analogies, occasionally sarcastic about Fed or SEBI policy, deeply human voice",
        "opening_hook": "opens with a relatable real-world analogy that immediately makes the market move feel personal and urgent",
        "signature_phrase": "This market is teaching us a lesson we should have already known.",
    },
    {
        "name": "Institutional Flow Analyst",
        "tone": "sharp and urgent",
        "style": "focuses on FII/DII data, block deals, bulk trades, short punchy sentences mixed with detailed flow analysis, references specific sector rotations",
        "opening_hook": "opens with a specific institutional flow anomaly spotted today that retail traders are completely unaware of",
        "signature_phrase": "Follow the money, not the noise.",
    },
    {
        "name": "Technical Price Action Specialist",
        "tone": "bold and opinionated",
        "style": "references candlestick patterns by name, Fibonacci levels, volume profile, market structure HH/HL/LH/LL, takes strong directional views",
        "opening_hook": "opens with a specific chart pattern forming right now across multiple timeframes signaling a high-probability move",
        "signature_phrase": "Price is the only truth in this market.",
    },
    # Pillar-specific personas
    {
        "name": "Certified Financial Planner",
        "tone": "warm, practical and trustworthy",
        "style": "speaks like a trusted advisor sitting across the table, uses real family finance examples, compares options with actual numbers and percentages, never condescending, references real Indian middle-class and US working-class financial situations, uses terms like 'your money', 'your family', 'your future' naturally",
        "opening_hook": "opens with a relatable personal finance situation that thousands of families face right now — something specific to current market or economic conditions",
        "signature_phrase": "The best financial plan is one you will actually follow.",
    },
    {
        "name": "AI and Technology Strategist",
        "tone": "sharp, forward-thinking and data-driven",
        "style": "explains how AI algorithms actually work in simple language, references specific models and tools retail traders can use today, connects tech company earnings to market movements, uses precise technical language but always explains it, references GitHub repos, trading APIs, and free tools available to everyone",
        "opening_hook": "opens with a specific AI signal or algorithmic pattern that most traders are missing right now — something data-driven and immediately actionable",
        "signature_phrase": "The algorithm already knows. The question is whether you're listening.",
    },
]

# Pillar-to-persona mapping — ensures right persona for right topic
PILLAR_PERSONA_MAP = {
    "stock-market":     [0, 1, 2, 3, 4, 5],   # all trading personas
    "bitcoin":          [2, 3, 4, 5, 0, 1],   # quant/technical first
    "personal-finance": [6, 1, 3, 6, 1, 3],   # CFP persona dominant
    "ai-trading":       [7, 2, 5, 7, 2, 5],   # AI strategist dominant
}

# ─── 1. Live Prices ───────────────────────────────────────────────────────────
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
        "DAX":           "^GDAXI",
        "IBOVESPA":      "^BVSP",
        "Gold":          "GC=F",
        "Silver":        "SI=F",
        "Crude Oil WTI": "CL=F",
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

# ─── 2. Google Trends ─────────────────────────────────────────────────────────
def get_google_trends():
    all_trends = []
    regions = [("US", "-330"), ("IN", "-330"), ("GB", "0"), ("BR", "-180")]
    finance_keywords = [
        'stock', 'market', 'nifty', 'sensex', 'nasdaq', 'bitcoin', 'crypto',
        'gold', 'oil', 'fed', 'inflation', 'economy', 'bank', 'finance',
        'invest', 'trade', 'dollar', 'rupee', 'earnings', 'ipo', 'gdp',
        'recession', 'rally', 'crash', 'rate', 'rbi', 'sebi', 'nvidia',
        'apple', 'tesla', 'google', 'amazon', 'meta', 'ai', 'tech',
        'insurance', 'loan', 'mortgage', 'retirement', 'savings', 'pension',
        'ibovespa', 'bovespa', 'brazil', 's&p', 'sp500', 'dow', 'powell',
        'ethereum', 'blockchain', 'defi', 'altcoin', 'fintech', 'algo',
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
            "S&P 500 Today", "Bitcoin Price Today", "Best Term Insurance 2026",
            "AI Trading Signals", "NIFTY Analysis Today", "NASDAQ Forecast",
            "Fed Rate Decision", "Bitcoin Rally 2026", "Gold Price Today",
            "Crypto Market Today", "IBOVESPA Today", "AI Stocks 2026",
        ]
    seen = set()
    unique = []
    for t in all_trends:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique.append(t)
    return unique[:15]

# ─── 3. News by Pillar ────────────────────────────────────────────────────────
def get_live_news(queries):
    all_headlines = []
    for query in queries:
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        try:
            r    = requests.get(url, timeout=8)
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:2]:
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
    return "\n".join(all_headlines[:20]) if all_headlines else "Market active today."

# ─── 4. Fear & Greed ─────────────────────────────────────────────────────────
def get_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=6)
        d = r.json()['data'][0]
        return f"{d['value']} — {d['value_classification']}"
    except:
        return "50 — Neutral"

# ─── 5. Cleanup old posts ─────────────────────────────────────────────────────
def cleanup_old_posts():
    try:
        files = sorted([f for f in os.listdir(POSTS_DIR) if f.endswith('.md')])
        if len(files) > MAX_POSTS:
            for fname in files[:len(files) - MAX_POSTS]:
                os.remove(os.path.join(POSTS_DIR, fname))
                print(f"  Removed: {fname}")
    except Exception as e:
        print(f"  Cleanup warning: {e}")

# ─── 6. Get recent posts for internal linking ─────────────────────────────────
def get_recent_posts(pillar_id, limit=3):
    try:
        files = sorted([f for f in os.listdir(POSTS_DIR) if f.endswith('.md')], reverse=True)
        recent = []
        for fname in files[:30]:
            if pillar_id in fname:
                fpath = os.path.join(POSTS_DIR, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    for line in content.split('\n'):
                        if line.startswith('title:'):
                            title = line.replace('title:', '').strip().strip('"')
                            slug  = fname.replace('.md', '')
                            recent.append({"title": title, "slug": slug})
                            break
                except:
                    pass
            if len(recent) >= limit:
                break
        return recent
    except:
        return []

# ─── 7. Schema Markup ─────────────────────────────────────────────────────────
def generate_schema(title, description, pillar, url_slug):
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "headline": title,
                "description": description,
                "datePublished": date_str,
                "dateModified": date_str,
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
                "mainEntityOfPage": f"https://ai360trading.in/{pillar['permalink_base']}/{url_slug}/",
                "keywords": ", ".join(pillar['primary_keywords']),
                "articleSection": pillar['name'],
                "inLanguage": "en-US"
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://ai360trading.in/"},
                    {"@type": "ListItem", "position": 2, "name": pillar['name'], "item": f"https://ai360trading.in/topics/{pillar['tag']}/"},
                    {"@type": "ListItem", "position": 3, "name": title, "item": f"https://ai360trading.in/{pillar['permalink_base']}/{url_slug}/"}
                ]
            }
        ]
    }
    return json.dumps(schema, indent=2)

# ─── 8. Build Dynamic Title ───────────────────────────────────────────────────
def build_title(pillar, trends, prices, fear_greed):
    top_trend   = trends[0] if trends else pillar['primary_keywords'][0]
    nifty_price = prices.get("NIFTY 50", {}).get("price", 24000)
    sp500_price = prices.get("S&P 500",  {}).get("price", 5500)
    btc_price   = prices.get("Bitcoin",  {}).get("price", 65000)
    sp500_pct   = prices.get("S&P 500",  {}).get("pct", 0)
    nifty_pct   = prices.get("NIFTY 50", {}).get("pct", 0)
    btc_pct     = prices.get("Bitcoin",  {}).get("pct", 0)

    if pillar['id'] == 'bitcoin':
        pct = btc_pct
    else:
        pct = sp500_pct if abs(sp500_pct) > abs(nifty_pct) else nifty_pct

    if pct > 1.0:
        direction = random.choice(["Surges", "Rallies", "Breaks Out", "Climbs"])
    elif pct < -1.0:
        direction = random.choice(["Drops", "Falls", "Slides", "Tumbles"])
    else:
        direction = random.choice(["Mixed", "At Crossroads", "In Focus", "Holds Key Levels"])

    # Offset by pillar index position to guarantee different template per pillar each day
    pillar_offset = ["stock-market","bitcoin","personal-finance","ai-trading"].index(pillar['id']) if pillar['id'] in ["stock-market","bitcoin","personal-finance","ai-trading"] else 0
    template = pillar['title_templates'][(now.day + pillar_offset * 2) % len(pillar['title_templates'])]
    fg_short  = fear_greed.split(' — ')[1] if ' — ' in fear_greed else fear_greed

    title = template.format(
        trend=top_trend,
        date=date_display,
        direction=direction,
        nifty=f"{nifty_price:,}",
        sp500=f"{sp500_price:,}",
        btc=f"{int(btc_price):,}",
        fg=fg_short,
    )
    return title, direction, top_trend

# ─── 9. Generate Single Article ──────────────────────────────────────────────
def generate_article(pillar, prices, trends, fear_greed, persona, article_index):
    print(f"\n  [{article_index}/4] Generating: {pillar['name']}...")

    news = get_live_news(pillar['news_queries'])

    nifty_price  = prices.get("NIFTY 50",    {}).get("price", 24000)
    nifty_pct    = prices.get("NIFTY 50",    {}).get("pct", 0)
    sp500_price  = prices.get("S&P 500",     {}).get("price", 5500)
    sp500_pct    = prices.get("S&P 500",     {}).get("pct", 0)
    btc_price    = prices.get("Bitcoin",     {}).get("price", 65000)
    btc_pct      = prices.get("Bitcoin",     {}).get("pct", 0)
    gold_price   = prices.get("Gold",        {}).get("price", 2200)
    nasdaq_price = prices.get("NASDAQ",      {}).get("price", 17000)
    ibov_display = prices.get("IBOVESPA",    {}).get("display", "N/A")
    dxy_price    = prices.get("DXY (Dollar)",{}).get("price", 104)
    vix_display  = prices.get("India VIX",   {}).get("display", "N/A")
    eth_price    = prices.get("Ethereum",    {}).get("price", 3000)
    price_lines  = "\n".join([f"  - {k}: {v['display']}" for k, v in prices.items()])

    article_title, direction, top_trend = build_title(pillar, trends, prices, fear_greed)

    import re as _re
    # Use article title for slug — unique every day, good for SEO
    _title_clean = article_title.lower()
    _title_clean = _title_clean.replace('&', '-and-').replace('s&p', 'sp').replace('s-and-p', 'sp')
    _title_clean = _title_clean.replace('$', '').replace('/', '-').replace(' ', '-')
    _title_clean = _title_clean.replace('|', '-').replace(':', '-').replace('?', '').replace('!', '')
    _title_clean = _title_clean.replace("'", '').replace('"', '').replace(',', '')
    _title_clean = _title_clean.replace('₹', 'rs').replace('%', 'pct')
    _title_clean = _re.sub(r'[^a-z0-9\-]', '', _title_clean)
    _title_clean = _re.sub(r'-+', '-', _title_clean).strip('-')
    title_slug   = _title_clean[:45]  # longer slug = more descriptive URL
    chosen_slug  = f"{date_str}-{pillar['id']}-{title_slug}"
    file_path    = os.path.join(POSTS_DIR, f"{chosen_slug}.md")

    # Internal links
    recent_posts = get_recent_posts(pillar['id'])
    internal_links_text = ""
    if recent_posts:
        internal_links_text = "\nINTERNAL LINKS TO INCLUDE NATURALLY IN BODY:\n"
        for post in recent_posts:
            internal_links_text += f'- [{post["title"]}](/{pillar["permalink_base"]}/{post["slug"]}/)\n'

    # Levels
    s1_nifty = round(nifty_price * 0.986, 0)
    s2_nifty = round(nifty_price * 0.972, 0)
    r1_nifty = round(nifty_price * 1.014, 0)
    r2_nifty = round(nifty_price * 1.028, 0)
    s1_sp500 = round(sp500_price * 0.986, 0)
    s2_sp500 = round(sp500_price * 0.972, 0)
    r1_sp500 = round(sp500_price * 1.014, 0)
    r2_sp500 = round(sp500_price * 1.028, 0)
    s1_btc   = round(btc_price * 0.95, 0)
    s2_btc   = round(btc_price * 0.90, 0)
    r1_btc   = round(btc_price * 1.05, 0)
    r2_btc   = round(btc_price * 1.10, 0)

    # Rotating article formats — never same structure twice
    FORMAT_TYPES = [
        "story_led",        # starts with a real market moment/observation
        "contrarian",       # leads with unpopular view backed by data
        "trader_notebook",  # written like a trader's daily notes
        "macro_driver",     # starts with the big macro force driving everything
        "chart_story",      # chart pattern first, then what it means
        "question_led",     # starts with the question everyone is asking
    ]
    _pillar_idx = ["stock-market","bitcoin","personal-finance","ai-trading"].index(pillar["id"]) if pillar["id"] in ["stock-market","bitcoin","personal-finance","ai-trading"] else 0
    fmt = FORMAT_TYPES[(now.day + article_index + _pillar_idx) % len(FORMAT_TYPES)]

    # Format-specific opening instructions
    FORMAT_INSTRUCTIONS = {
        "story_led": "Start with a specific market observation — a price level, a candle pattern, or an unusual move you noticed today. Make it feel like you are talking to a friend trader.",
        "contrarian": "Open with the view most people have wrong right now. State it bluntly. Then prove it with data.",
        "trader_notebook": "Write like a trading diary entry. Use 'I'm watching...', 'The level that matters to me today is...', 'What worries me is...'. Raw and real.",
        "macro_driver": "Identify the single biggest macro force driving markets today — Fed, dollar, oil, war, earnings — and build the whole article around how it ripples into each market.",
        "chart_story": "Describe what the chart is telling you in plain language. What pattern, what level, what the last 5 candles mean. Then connect to fundamentals.",
        "question_led": "Open with the exact question traders are googling right now. Answer it directly in para 1. Then go deeper.",
    }

    # Varied section structures — never use the same one
    SECTION_STRUCTURES = {
        "story_led":      ["The Setup", "What the Data Actually Says", "How Each Market Is Playing It", "Key Levels I'm Watching", "The Risk Nobody's Talking About", "My Take", "Quick Answers"],
        "contrarian":     ["The Consensus View (And Why It's Wrong)", "What the Data Shows Instead", "Market By Market Breakdown", "The Levels That Actually Matter", "What Smart Money Is Doing", "Bottom Line", "Reader Questions"],
        "trader_notebook":["Morning Observations", "NIFTY & India — What I See", "US Markets — Reading the Tape", "Bitcoin — Where I Stand", "Levels I'm Using Today", "What Could Go Wrong", "Common Questions Today"],
        "macro_driver":   ["The Macro Driver Today", "How It's Moving Each Market", "India's Position", "US & Global Impact", "Technical Levels to Watch", "Scenario Analysis", "Key Questions Answered"],
        "chart_story":    ["What the Chart Is Saying", "Confirming Signals", "Country By Country View", "The Numbers That Matter", "Bull vs Bear Case", "My Positioning View", "Trader FAQs"],
        "question_led":   ["The Direct Answer", "The Deeper Context", "India View", "US & Crypto View", "Support & Resistance Map", "What Happens Next", "More Questions"],
    }

    sections = SECTION_STRUCTURES[fmt]
    opening_instruction = FORMAT_INSTRUCTIONS[fmt]

    prompt = f"""You are Amit Kumar, founder of AI360Trading — independent market analyst from Haridwar, India.

PERSONA TODAY: {persona['name']} | {persona['tone']}
WRITING STYLE: {persona['style']}

Today is {day_name}, {date_display}.
ARTICLE FORMAT TYPE: {fmt}
OPENING INSTRUCTION: {opening_instruction}

TOPIC: {pillar['name']}
{pillar['article_focus']}

LIVE MARKET DATA RIGHT NOW:
{price_lines}
Fear & Greed: {fear_greed} | India VIX: {vix_display}
NIFTY: {nifty_price} ({nifty_pct:+.2f}%) | S&P 500: {sp500_price} ({sp500_pct:+.2f}%)
Bitcoin: ${btc_price} ({btc_pct:+.2f}%) | Gold: ${gold_price} | ETH: ${eth_price}
IBOVESPA: {ibov_display} | DXY: {dxy_price}

CALCULATED KEY LEVELS:
NIFTY — S2:{s2_nifty} S1:{s1_nifty} [NOW:{nifty_price}] R1:{r1_nifty} R2:{r2_nifty}
S&P 500 — S2:{s2_sp500} S1:{s1_sp500} [NOW:{sp500_price}] R1:{r1_sp500} R2:{r2_sp500}
Bitcoin — S2:{s2_btc} S1:{s1_btc} [NOW:{btc_price}] R1:{r1_btc} R2:{r2_btc}

NEWS TODAY (use as context only — write YOUR OWN analysis):
{news}

TRENDING SEARCHES: {', '.join(trends[:8])}
{internal_links_text}

=== HUMAN WRITING RULES (CRITICAL) ===

1. VARY SENTENCE LENGTH aggressively. Mix short punchy sentences with longer analytical ones.
   Example: "The S&P is sitting at 6,740. That number matters more than people think right now."

2. EXPRESS GENUINE OPINIONS with reasoning:
   BAD: "Bitcoin may reach $70,000."
   GOOD: "Personally I think the $70K breakout fails the first attempt. Too many leveraged longs stacked just below that level — the market will hunt those stops first."

3. SHOW UNCERTAINTY where real:
   BAD: "The market will find support at 23,500."
   GOOD: "23,500 looks like support — but I'd be lying if I said I was confident here given the global backdrop."

4. USE TRADER LANGUAGE naturally:
   - "the tape is telling me..."
   - "what I'm watching for..."
   - "the level that matters today..."
   - "options flow shows..."
   - "smart money positioning suggests..."

5. ADD ONE REAL HISTORICAL PARALLEL with exact month/year:
   Example: "This setup reminds me of August 2023 when NIFTY bounced hard from exactly the same zone."

6. BREAK PARAGRAPH SYMMETRY — no two consecutive paragraphs same length.

7. BANNED WORDS & PHRASES (never use):
   "In conclusion", "Furthermore", "Moreover", "This underscores", "This highlights",
   "Navigating", "Landscape", "Delve into", "Robust", "Game-changer", "Paradigm shift",
   "Deep dive", "Shed light", "Bustling", "It's worth noting", "It is important to note",
   "As I analyze", "Core Analysis", "Country Analysis", "Brand View"

8. NEVER use these AI structure headers: "Core Analysis", "Country Analysis", "Brand View",
   "AI360Trading View" — use the section names from SECTIONS list below instead.

9. NUMBERS must connect to decisions:
   BAD: "RSI is at 64.21"
   GOOD: "RSI just hit 64 — entering overbought territory. Historically at this level NIFTY either consolidates 3-5 days or shakes out weak hands with a quick 1.5% dip first."

10. DELETE fake authority lines like "As I spoke with a Wall Street trader" — unless you have a specific name/firm.

=== ARTICLE STRUCTURE ===

Use EXACTLY these section names in this order:
{chr(10).join(f"## {s}" for s in sections)}

Also include ONE key levels table:
| Instrument | Price | S2 | S1 | R1 | R2 |
|---|---|---|---|---|---|

And ONE FAQ block with 3 questions that people actually search on Google (use exact search phrasing).
Include 2-3 internal links naturally in body text if provided above.

=== FORMAT ===
First line: META_DESCRIPTION: <150-160 chars with specific price data and date>
Then the article starting with ## {sections[0]}

Target length: 2000-2200 words.
End with:
*{date_display} | Educational content only. Not SEBI registered investment advice.*
"""
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are Amit Kumar of AI360Trading writing as a {persona['name']}. "
                        f"Tone: {persona['tone']}. Style: {persona['style']}. "
                        "Write 100% original human-sounding financial content. "
                        "Readers are in US, UK, Brazil and India — all four groups must find genuine value."
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
        meta_description = f"{article_title} | {pillar['name']} — {date_display}. Live prices, key levels and insights for US, UK, India and Brazil."[:155]
        cleaned_lines = []
        for line in content.split("\n"):
            if line.strip().startswith("META_DESCRIPTION:"):
                extracted = line.replace("META_DESCRIPTION:", "").strip().strip('"')
                if 100 < len(extracted) <= 160:
                    meta_description = extracted
            else:
                cleaned_lines.append(line)
        content = "\n".join(cleaned_lines).lstrip("\n")

        article_excerpt = (
    f"{article_title} — {pillar['name']} analysis for {date_display}. "
    f"Live data, key levels, actionable insights for US, UK, India and Brazil."
)[:200]

        schema_json = generate_schema(article_title, meta_description, pillar, chosen_slug)

        # Sanitize title — remove chars that break YAML/XML sitemap
        safe_title = (article_title
            .replace('"', "'")
            .replace('&', 'and')
            .replace('<', '')
            .replace('>', '')
            .replace('₹', 'Rs.')
            .replace('\n', ' ')
            .strip())
        safe_excerpt = (article_excerpt
            .replace('"', "'")
            .replace('&', 'and')
            .replace('<', '')
            .replace('>', '')
            .strip())
        safe_desc = (meta_description
            .replace('"', "'")
            .replace('&', 'and')
            .replace('<', '')
            .replace('>', '')
            .strip())

        header = (
            "---\n"
            "layout: post\n"
            f"title: \"{safe_title}\"\n"
            f"date: {date_str}\n"
            "author: \"Amit Kumar\"\n"
            f"pillar: \"{pillar['id']}\"\n"
            f"permalink: /{pillar['permalink_base']}/{chosen_slug}/\n"
            f"excerpt: \"{safe_excerpt}\"\n"
            f"description: \"{safe_desc}\"\n"
            f"keywords: \"{', '.join(pillar['primary_keywords'])}, {', '.join(pillar['us_keywords'][:2])}, {', '.join(pillar['india_keywords'][:2])}\"\n"
            f"categories: [{pillar['category']}]\n"
            f"tags: [{pillar['tag']}]\n"
            f"nifty_level: \"{prices.get('NIFTY 50',{}).get('display','N/A')}\"\n"
            f"sp500_level: \"{prices.get('S&P 500',{}).get('display','N/A')}\"\n"
            f"bitcoin_level: \"{prices.get('Bitcoin',{}).get('display','N/A')}\"\n"
            f"gold_level: \"{prices.get('Gold',{}).get('display','N/A')}\"\n"
            f"fear_greed: \"{fear_greed}\"\n"
            f"trending: \"{', '.join(trends[:5])}\"\n"
            "---\n\n"
        )

        schema_block = f'<script type="application/ld+json">\n{schema_json}\n</script>\n\n'

        if not os.path.exists(POSTS_DIR):
            os.makedirs(POSTS_DIR)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header + schema_block + content)

        print(f"  ✅ /{pillar['permalink_base']}/{chosen_slug}/")
        print(f"     {article_title[:70]}...")
        return True

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


# ─── 10. Main ─────────────────────────────────────────────────────────────────
def generate_all_articles():
    print("=" * 60)
    print(f"  AI360Trading Daily Bot — {date_display}")
    print("=" * 60)

    print("\nFetching live market data...")
    prices     = get_live_prices()
    trends     = get_google_trends()
    fear_greed = get_fear_greed()

    print(f"  S&P 500  : {prices.get('S&P 500',{}).get('display','N/A')}")
    print(f"  NIFTY    : {prices.get('NIFTY 50',{}).get('display','N/A')}")
    print(f"  Bitcoin  : {prices.get('Bitcoin',{}).get('display','N/A')}")
    print(f"  Gold     : {prices.get('Gold',{}).get('display','N/A')}")
    print(f"  F&G      : {fear_greed}")
    print(f"  Trending : {', '.join(trends[:3])}")

    results = []
    for i, pillar in enumerate(PILLARS):
        # Use pillar-specific persona map for human-sounding topic-appropriate writing
        persona_pool = PILLAR_PERSONA_MAP.get(pillar['id'], [0,1,2,3,4,5])
        persona_idx  = persona_pool[now.weekday() % len(persona_pool)]
        persona      = PERSONAS[persona_idx]
        success = generate_article(pillar, prices, trends, fear_greed, persona, i + 1)
        results.append((pillar['name'], success))
        if i < len(PILLARS) - 1:
            time.sleep(3)

    print("\n" + "=" * 60)
    print("  DAILY PUBLISH SUMMARY")
    print("=" * 60)
    for name, success in results:
        print(f"  {'✅' if success else '❌'} {name}")

    cleanup_old_posts()
    print("\n  Done. Bot will run again tomorrow.")


if __name__ == "__main__":
    generate_all_articles()
