import os
import pytz
import requests
import random
import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from groq import Groq

# ─── Content Mode ─────────────────────────────────────────────────────────────
# "market"  → normal weekday — live market data + analysis articles
# "weekend" → Saturday/Sunday — educational/beginner articles
# "holiday" → Indian market holiday — motivational/savings/storytelling articles
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")
print(f"[MODE] generate_articles.py running in mode: {CONTENT_MODE.upper()}")

# ─── Google Indexing API ─────────────────────────────────────────────────────
def submit_urls_to_google(urls: list):
    try:
        import json as _json
        sa_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "")
        if not sa_json:
            print("  ⚠️  GCP_SERVICE_ACCOUNT_JSON not set — skipping indexing API")
            return

        sa = _json.loads(sa_json)

        import time as _time
        import base64

        header  = base64.urlsafe_b64encode(
            _json.dumps({"alg":"RS256","typ":"JWT"}).encode()
        ).rstrip(b'=').decode()

        now_ts  = int(_time.time())
        payload = base64.urlsafe_b64encode(_json.dumps({
            "iss":   sa["client_email"],
            "scope": "https://www.googleapis.com/auth/indexing",
            "aud":   "https://oauth2.googleapis.com/token",
            "exp":   now_ts + 3600,
            "iat":   now_ts,
        }).encode()).rstrip(b'=').decode()

        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding

            private_key = serialization.load_pem_private_key(
                sa["private_key"].encode(), password=None
            )
            signing_input = f"{header}.{payload}".encode()
            signature = private_key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
            sig_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
            jwt_token = f"{header}.{payload}.{sig_b64}"
        except ImportError:
            print("  ⚠️  cryptography library not available — skipping indexing API")
            return

        token_resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion":  jwt_token,
            },
            timeout=15
        )
        if not token_resp.ok:
            print(f"  ⚠️  Token error: {token_resp.text[:100]}")
            return

        access_token = token_resp.json().get("access_token", "")
        if not access_token:
            print("  ⚠️  No access token received")
            return

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type":  "application/json",
        }
        success_count = 0
        for url in urls:
            try:
                resp = requests.post(
                    "https://indexing.googleapis.com/v3/urlNotifications:publish",
                    headers=headers,
                    json={"url": url, "type": "URL_UPDATED"},
                    timeout=10
                )
                if resp.ok:
                    print(f"  ✅ Indexed: {url}")
                    success_count += 1
                else:
                    print(f"  ⚠️  Index failed ({resp.status_code}): {url}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  ⚠️  Index error for {url}: {e}")

        print(f"  📡 Google Indexing API: {success_count}/{len(urls)} URLs submitted")

    except Exception as e:
        print(f"  ⚠️  Indexing API error: {e} — articles still published normally")


SITE_URL = "https://ai360trading.in"

client       = Groq(api_key=os.environ.get("GROQ_API_KEY"))
ist          = pytz.timezone('Asia/Kolkata')
now          = datetime.now(ist)
date_str     = now.strftime("%Y-%m-%d")
date_display = now.strftime("%B %d, %Y")
day_name     = now.strftime("%A")
POSTS_DIR    = os.path.join(os.getcwd(), '_posts')
MAX_POSTS    = 60

# ─── HOLIDAY / WEEKEND ARTICLE PILLARS ───────────────────────────────────────
# Used when CONTENT_MODE is "holiday" or "weekend"
# These replace live market analysis with evergreen global-audience content
HOLIDAY_PILLARS = [
    {
        "id": "stock-market",
        "name": "Stock Market",
        "permalink_base": "stock-market",
        "category": "Stock-Market",
        "tag": "stock-market",
        "primary_keywords": ["stock market basics", "how to invest", "index fund", "S&P 500", "NIFTY"],
        "us_keywords": ["how to invest in stocks USA", "best index fund 2026", "S&P 500 investing"],
        "uk_keywords": ["how to invest UK 2026", "FTSE 100 beginner guide"],
        "brazil_keywords": ["como investir na bolsa 2026", "IBOVESPA iniciantes"],
        "india_keywords": ["how to invest in share market India", "Nifty 50 beginner guide", "SIP vs lump sum"],
        "article_focus": """Write a comprehensive beginner-friendly stock market education article covering:
- How stock markets work globally (India NSE/BSE, US NYSE/NASDAQ, UK LSE, Brazil B3)
- Why index fund investing beats stock picking for most people
- How to start investing with small amounts in each country
- Compound interest examples with real numbers
- Common beginner mistakes and how to avoid them
- Actionable steps readers can take today
Target: complete beginners in US, UK, Brazil and India""",
        "title_templates": [
            "How to Start Investing in the Stock Market — Complete 2026 Guide for US, UK, India and Brazil",
            "Index Funds vs Stock Picking — The Data Will Surprise You ({date})",
            "The Biggest Mistake New Investors Make — And the Simple Fix",
            "How Compound Interest Really Works — Numbers That Change Everything ({date})",
            "Stock Market Basics in 2026 — Everything a Beginner Needs to Know",
        ],
        "news_queries": ["stock+market+beginner+investing+2026", "index+fund+returns+2026", "how+to+invest+money+2026"],
        "india_keywords": ["stock market India beginner", "NSE BSE guide 2026"],
    },
    {
        "id": "bitcoin",
        "name": "Bitcoin and Crypto",
        "permalink_base": "bitcoin",
        "category": "Bitcoin-Crypto",
        "tag": "bitcoin",
        "primary_keywords": ["Bitcoin explained", "how to buy crypto safely", "crypto beginner guide 2026"],
        "us_keywords": ["how to buy bitcoin USA 2026", "crypto investing guide", "bitcoin safe investment"],
        "uk_keywords": ["how to buy bitcoin UK 2026", "crypto regulation UK"],
        "brazil_keywords": ["como comprar bitcoin 2026", "criptomoedas guia Brasil"],
        "india_keywords": ["how to buy bitcoin India 2026", "crypto tax India", "bitcoin INR guide"],
        "article_focus": """Write a comprehensive beginner crypto education article covering:
- What Bitcoin and Ethereum actually are in simple terms
- How to buy crypto safely in US, UK, Brazil and India (step by step)
- How much to invest — risk management for beginners
- Cold wallet vs exchange — what new investors need to know
- Bitcoin halving cycle explained simply
- Common crypto scams and how to avoid them
- Tax implications in each country
Target: complete beginners worldwide who keep hearing about crypto""",
        "title_templates": [
            "Bitcoin Explained Simply — Complete Beginner Guide 2026 for US, UK, India and Brazil",
            "How to Buy Crypto Safely in 2026 — Step by Step Guide",
            "Is Bitcoin a Safe Investment? — Honest Answer for Beginners ({date})",
            "Crypto Beginner Mistakes That Cost People Money — And How to Avoid Them",
            "Bitcoin Halving Cycle Explained — What Every New Investor Should Know",
        ],
        "news_queries": ["bitcoin+beginner+guide+2026", "how+to+buy+crypto+safely+2026", "bitcoin+halving+explained"],
    },
    {
        "id": "personal-finance",
        "name": "Personal Finance",
        "permalink_base": "personal-finance",
        "category": "Personal-Finance",
        "tag": "personal-finance",
        "primary_keywords": ["personal finance tips 2026", "how to save money", "emergency fund", "term life insurance"],
        "us_keywords": ["best savings account USA 2026", "401k guide", "term life insurance USA"],
        "uk_keywords": ["best ISA 2026", "UK pension guide", "how to save money UK"],
        "brazil_keywords": ["como economizar dinheiro 2026", "previdencia privada Brasil"],
        "india_keywords": ["how to save money India 2026", "best term insurance India", "PPF vs ELSS", "emergency fund India"],
        "article_focus": """Write a comprehensive personal finance guide covering:
- The 50-30-20 rule explained with real examples for each country
- Emergency fund: how much, where to keep it (India, US, UK, Brazil)
- Best term life insurance comparison with real numbers 2026
- SIP/401k/ISA — retirement savings starter guide per country
- How to get out of debt — practical steps
- The one financial habit that changes everything
- Actionable steps for today — not generic advice
Target: working adults aged 25-45 in US, UK, Brazil and India who feel behind on finances""",
        "title_templates": [
            "Personal Finance Complete Guide 2026 — US, UK, India and Brazil",
            "Why 80% of People Never Build Wealth — And the Simple Fix",
            "Emergency Fund: How Much You Actually Need in 2026",
            "Best Term Life Insurance 2026 — US, UK and India Compared",
            "The 50-30-20 Rule — Does It Actually Work? Real Numbers Inside",
        ],
        "news_queries": ["personal+finance+tips+2026", "emergency+fund+guide", "term+life+insurance+2026"],
    },
    {
        "id": "ai-trading",
        "name": "AI and Trading Technology",
        "permalink_base": "ai-trading",
        "category": "AI-Trading",
        "tag": "ai-trading",
        "primary_keywords": ["AI trading tools 2026", "free trading tools", "algorithmic trading beginner", "fintech 2026"],
        "us_keywords": ["best free AI trading tools USA 2026", "AI stock screener free"],
        "uk_keywords": ["AI trading UK 2026", "free stock analysis tools UK"],
        "brazil_keywords": ["ferramentas gratuitas trading 2026", "inteligencia artificial bolsa"],
        "india_keywords": ["free AI trading tools India 2026", "best stock screener India free", "algo trading beginner India"],
        "article_focus": """Write a comprehensive guide to free AI and trading tools covering:
- Best completely free stock screeners for India, US, UK and Brazil
- How retail traders can use AI tools for better decisions today
- Free technical analysis tools vs paid ones — honest comparison
- How algorithmic trading works without coding knowledge
- AI tools that actually work vs overhyped ones
- How to build a simple trading system using free tools
- Risk management tools that are free and effective
Target: retail traders of all levels looking for an edge without paying""",
        "title_templates": [
            "Best Free AI Trading Tools 2026 — Complete Guide for US, UK, India and Brazil",
            "How to Use AI for Stock Market Analysis — Free Tools That Actually Work",
            "Free vs Paid Trading Tools — Honest Comparison 2026",
            "Algorithmic Trading for Beginners — No Coding Required 2026 Guide",
            "The Free Stock Screeners That Professional Traders Actually Use",
        ],
        "news_queries": ["free+AI+trading+tools+2026", "best+stock+screener+free+2026", "algorithmic+trading+beginner+2026"],
    },
]

# ─── MARKET DAY PILLARS (unchanged from original) ────────────────────────────
MARKET_PILLARS = [
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
            "S&P 500 and NIFTY Today: The Level Nobody Is Watching ({date})",
            "{trend}: Why This Move Is Different From What Media Is Saying",
            "I Was Wrong About {trend} — Here Is What the Chart Actually Shows",
            "NIFTY {nifty} | The Trade Setup I Am Looking at Right Now",
            "Why Smart Money Is {direction} While Retail Panics — {date}",
            "The One Chart That Explains Today's Market Move — {date}",
            "NIFTY Support and Resistance Today: Exact Levels for {date}",
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
        "name": "Bitcoin and Crypto",
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
            "Is Bitcoin Going Up or Down Today? {date} Analysis",
            "Bitcoin and Crypto {direction} — {date} Report",
            "BTC at ${btc} — What Smart Money Is Doing Now | {date}",
            "What Is Driving Crypto Markets Today — Bitcoin Analysis {date}",
            "Fear and Greed {fg}: Bitcoin {direction} — {date} Crypto Signals",
            "Bitcoin Price Today: ${btc} — {date} US, India and Brazil",
            "Crypto Market {direction} | Bitcoin ${btc} — {date} Intelligence",
        ],
        "article_focus": """Write a comprehensive crypto market analysis covering:
- Bitcoin price action, technical levels, support/resistance with exact numbers
- Ethereum and major altcoin analysis
- Crypto Fear and Greed Index interpretation and what it signals
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
            "Best Term Life Insurance 2026 — US, UK and India Complete Guide",
            "Personal Finance Guide for {date}: What the Data Says Right Now",
            "I Ran the Numbers on SIP vs Lump Sum — The Answer Surprised Me",
            "Why Most Indians Are Getting Their Term Insurance Wrong in 2026",
            "What {trend} Means for Your SIP and Savings Right Now",
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
        "name": "AI and Trading Technology",
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
            "What My Algorithm Is Showing vs What I Actually Think — {date}",
            "I Backtested This Strategy 5 Years — Here Are the Real Results",
            "Free AI Tools That Are Actually Useful for Trading in 2026",
            "Why AI Got the {direction} Call Wrong — And What It Means for Your Trades",
            "The Algorithm Spotted This Pattern Before the Move — Here Is How",
            "AI vs Human Trader: Who Called It Better This Week? ({date})",
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

# ─── Select correct pillar set based on mode ─────────────────────────────────
PILLARS = HOLIDAY_PILLARS if CONTENT_MODE in ("holiday", "weekend") else MARKET_PILLARS

# ─── Writing Personas ─────────────────────────────────────────────────────────
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
    {
        "name": "Certified Financial Planner",
        "tone": "warm, practical and trustworthy",
        "style": "speaks like a trusted advisor sitting across the table, uses real family finance examples, compares options with actual numbers and percentages, never condescending",
        "opening_hook": "opens with a relatable personal finance situation that thousands of families face right now",
        "signature_phrase": "The best financial plan is one you will actually follow.",
    },
    {
        "name": "AI and Technology Strategist",
        "tone": "sharp, forward-thinking and data-driven",
        "style": "explains how AI algorithms actually work in simple language, references specific models and tools retail traders can use today",
        "opening_hook": "opens with a specific AI signal or algorithmic pattern that most traders are missing right now",
        "signature_phrase": "The algorithm already knows. The question is whether you're listening.",
    },
]

PILLAR_PERSONA_MAP = {
    "stock-market":     [0, 1, 2, 3, 4, 5],
    "bitcoin":          [2, 3, 4, 5, 0, 1],
    "personal-finance": [6, 1, 3, 6, 1, 3],
    "ai-trading":       [7, 2, 5, 7, 2, 5],
}

# ─── Live Prices (market mode only) ──────────────────────────────────────────
def get_live_prices():
    if CONTENT_MODE in ("holiday", "weekend"):
        print("  📅 Holiday/Weekend mode — skipping live price fetch")
        return {}

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
    return "\n".join(all_headlines[:20]) if all_headlines else "Educational content day — no live news needed."

def get_fear_greed():
    if CONTENT_MODE in ("holiday", "weekend"):
        return "N/A — Holiday/Weekend"
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=6)
        d = r.json()['data'][0]
        return f"{d['value']} — {d['value_classification']}"
    except:
        return "50 — Neutral"

def cleanup_old_posts():
    try:
        files = sorted([f for f in os.listdir(POSTS_DIR) if f.endswith('.md')])
        if len(files) > MAX_POSTS:
            for fname in files[:len(files) - MAX_POSTS]:
                os.remove(os.path.join(POSTS_DIR, fname))
                print(f"  Removed: {fname}")
    except Exception as e:
        print(f"  Cleanup warning: {e}")

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
                    title = None
                    url_slug_match = None
                    for line in content.split('\n'):
                        if line.startswith('title:'):
                            title = line.replace('title:', '').strip().strip('"')
                        if line.startswith('permalink:'):
                            parts = line.strip().rstrip('/').split('/')
                            if len(parts) >= 2:
                                url_slug_match = parts[-1]
                        if title and url_slug_match:
                            break
                    if title and url_slug_match:
                        recent.append({"title": title, "slug": url_slug_match})
                except:
                    pass
            if len(recent) >= limit:
                break
        return recent
    except:
        return []

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

def build_title(pillar, trends, prices, fear_greed):
    # For holiday/weekend — use simple template from the pillar
    if CONTENT_MODE in ("holiday", "weekend"):
        template = pillar['title_templates'][now.day % len(pillar['title_templates'])]
        title = template.format(date=date_display, trend="investing", direction="grows", nifty="N/A", sp500="N/A", btc="N/A", fg="N/A")
        return title, "educational", "financial education"

    pillar_trend_keywords = {
        "stock-market":     ['stock', 'nifty', 'sensex', 'nasdaq', 's&p', 'market', 'dow', 'ftse', 'ibovespa'],
        "bitcoin":          ['bitcoin', 'crypto', 'btc', 'ethereum', 'defi', 'altcoin', 'blockchain'],
        "personal-finance": ['insurance', 'loan', 'mortgage', 'retirement', 'savings', 'pension', 'invest', 'finance'],
        "ai-trading":       ['ai', 'algo', 'fintech', 'nvidia', 'tech', 'algorithm', 'machine learning'],
    }
    relevant_keywords = pillar_trend_keywords.get(pillar['id'], [])
    top_trend = next(
        (t for t in trends if any(kw in t.lower() for kw in relevant_keywords)),
        pillar['primary_keywords'][0]
    )

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

def generate_article(pillar, prices, trends, fear_greed, persona, article_index):
    print(f"\n  [{article_index}/4] Generating: {pillar['name']} [{CONTENT_MODE} mode]...")

    news = get_live_news(pillar['news_queries'])

    # Build market context — empty on holiday/weekend
    if CONTENT_MODE in ("holiday", "weekend"):
        price_lines = "Market closed today — educational content mode"
        mode_note   = f"This is a {'holiday' if CONTENT_MODE == 'holiday' else 'weekend'} article. Write educational, evergreen content. No live market data. Focus on timeless investment wisdom applicable to US, UK, Brazil and India readers."
        if CONTENT_MODE == "holiday":
            mode_note += f" Today is {HOLIDAY_NAME} — a market holiday. Content should be educational and globally appealing."
    else:
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
        mode_note    = ""

    article_title, direction, top_trend = build_title(pillar, trends, prices, fear_greed)

    import re as _re
    _title_clean = article_title.lower()
    _title_clean = _title_clean.replace('s&p', 'sp').replace('s-and-p', 'sp')
    _title_clean = _title_clean.replace('&', '-').replace('$', '').replace('/', '-')
    _title_clean = _title_clean.replace(' ', '-').replace('|', '-').replace(':', '-')
    _title_clean = _title_clean.replace('?', '').replace('!', '').replace("'", '')
    _title_clean = _title_clean.replace('"', '').replace(',', '').replace('(', '').replace(')', '')
    _title_clean = _title_clean.replace('₹', 'rs').replace('%', 'pct')
    _title_clean = _re.sub(r'[^a-z0-9\-]', '', _title_clean)
    _title_clean = _re.sub(r'-+', '-', _title_clean).strip('-')

    _stop = {'the','a','an','and','or','but','in','on','at','to','for','of',
             'with','is','are','was','were','its','this','that','i','my','we',
             'you','he','she','they','what','why','how','when','where','from',
             'by','as','so','if','just','vs','im','heres','thats','dont'}
    _words = [w for w in _title_clean.split('-') if w and w not in _stop]

    title_slug  = '-'.join(_words[:6])
    file_slug   = f"{date_str}-{pillar['id']}-{title_slug}"
    chosen_slug = title_slug
    file_path   = os.path.join(POSTS_DIR, f"{file_slug}.md")

    recent_posts = get_recent_posts(pillar['id'])
    internal_links_text = ""
    if recent_posts:
        internal_links_text = "\nINTERNAL LINKS TO INCLUDE NATURALLY IN BODY:\n"
        for post in recent_posts:
            internal_links_text += f'- [{post["title"]}](/{pillar["permalink_base"]}/{post["slug"]}/)\n'

    FORMAT_TYPES = [
        "story_led", "contrarian", "trader_notebook",
        "macro_driver", "chart_story", "question_led",
    ]
    _pillar_idx = ["stock-market","bitcoin","personal-finance","ai-trading"].index(pillar["id"]) if pillar["id"] in ["stock-market","bitcoin","personal-finance","ai-trading"] else 0
    fmt = FORMAT_TYPES[(now.day + article_index + _pillar_idx) % len(FORMAT_TYPES)]

    FORMAT_INSTRUCTIONS = {
        "story_led":      "Start with a specific observation — a fact, a number, or a situation that real readers face today.",
        "contrarian":     "Open with the view most people have wrong right now. State it bluntly. Then prove it with data.",
        "trader_notebook":"Write like a personal finance diary entry. Use 'I'm watching...', 'The number that matters today is...'",
        "macro_driver":   "Identify the single biggest force affecting personal finances or markets today and build the whole article around it.",
        "chart_story":    "Describe what the data is telling you in plain language. Then connect to actionable advice.",
        "question_led":   "Open with the exact question your target reader is googling right now. Answer it directly in paragraph 1.",
    }

    SECTION_STRUCTURES = {
        "story_led":      ["The Setup", "What the Data Actually Says", "How This Affects Each Country", "Key Numbers to Know", "The Risk Nobody's Talking About", "My Take", "Quick Answers"],
        "contrarian":     ["The Consensus View (And Why It's Wrong)", "What the Data Shows Instead", "Country By Country Breakdown", "The Numbers That Actually Matter", "What Smart Investors Are Doing", "Bottom Line", "Reader Questions"],
        "trader_notebook":["Today's Observations", "India View", "Global Context", "The Numbers I'm Using", "What Could Go Wrong", "Action Steps", "Common Questions"],
        "macro_driver":   ["The Big Force Today", "How It Affects Each Market", "India's Position", "US and Global Impact", "Numbers to Watch", "Scenario Analysis", "Key Questions Answered"],
        "chart_story":    ["What the Data Is Saying", "Confirming Signals", "Country By Country View", "The Numbers That Matter", "Best Case vs Worst Case", "My Recommendation", "Trader FAQs"],
        "question_led":   ["The Direct Answer", "The Deeper Context", "India View", "US, UK and Brazil View", "Numbers and Levels", "What Happens Next", "More Questions"],
    }

    sections = SECTION_STRUCTURES[fmt]
    opening_instruction = FORMAT_INSTRUCTIONS[fmt]

    prompt = f"""You are Amit Kumar, founder of AI360Trading — independent market analyst from Haridwar, India.

PERSONA TODAY: {persona['name']} | {persona['tone']}
WRITING STYLE: {persona['style']}

Today is {day_name}, {date_display}.
ARTICLE FORMAT TYPE: {fmt}
OPENING INSTRUCTION: {opening_instruction}
{mode_note}

TOPIC: {pillar['name']}
{pillar['article_focus']}

LIVE DATA:
{price_lines}
Fear and Greed: {fear_greed}

NEWS TODAY (use as context only — write YOUR OWN analysis):
{news}

TRENDING SEARCHES: {', '.join(trends[:8])}
{internal_links_text}

=== HUMAN WRITING RULES (CRITICAL) ===
1. VARY SENTENCE LENGTH aggressively.
2. EXPRESS GENUINE OPINIONS with reasoning.
3. SHOW UNCERTAINTY where real.
4. USE NATURAL LANGUAGE — no jargon overload.
5. ADD ONE REAL HISTORICAL PARALLEL with exact month/year.
6. BREAK PARAGRAPH SYMMETRY.
7. BANNED WORDS: "In conclusion", "Furthermore", "Moreover", "This underscores",
   "Navigating", "Landscape", "Delve into", "Robust", "Game-changer", "Paradigm shift",
   "Deep dive", "Shed light", "It's worth noting", "It is important to note"
8. NEVER use headers: "Core Analysis", "Country Analysis", "Brand View"
9. NUMBERS must connect to decisions.
10. DELETE fake authority lines.

=== ARTICLE STRUCTURE ===
Use EXACTLY these section names:
{chr(10).join(f"## {s}" for s in sections)}

Include ONE FAQ block with 3 questions people actually search on Google.
Include 2-3 internal links naturally in body text if provided above.

=== FORMAT ===
First line: META_DESCRIPTION: <150-160 chars with specific data and date>
Then the article starting with ## {sections[0]}

CRITICAL SEO RULE:
The article title is: "{article_title}"
Use exact key words from this title in:
1. The very first sentence of ## {sections[0]}
2. At least 2 more times naturally throughout the article body
3. FAQ questions must reference the title topic directly

Target length: 2000-2200 words. Minimum 1800 words — never less.
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

        meta_description = f"{article_title} | {pillar['name']} — {date_display}. Insights for US, UK, India and Brazil investors."[:155]
        cleaned_lines = []
        for line in content.split("\n"):
            if line.strip().startswith("META_DESCRIPTION:"):
                extracted = line.replace("META_DESCRIPTION:", "").strip().strip('"')
                if 130 <= len(extracted) <= 160:
                    meta_description = extracted
                elif 100 < len(extracted) < 130:
                    meta_description = (extracted + f" | {pillar['name']} {date_display}.")[:160]
            else:
                cleaned_lines.append(line)
        content = "\n".join(cleaned_lines).lstrip("\n")

        _primary_kw = pillar['primary_keywords'][0]
        article_excerpt = (
            f"{article_title} — {pillar['name']} for {date_display}. "
            f"Insights on {_primary_kw} for US, UK, India and Brazil investors."
        )[:200]

        schema_json = generate_schema(article_title, meta_description, pillar, chosen_slug)

        safe_title = (article_title
            .replace('"', "'").replace('&', 'and').replace('<', '')
            .replace('>', '').replace('₹', 'Rs.').replace('\n', ' ').strip())
        safe_excerpt = (article_excerpt
            .replace('"', "'").replace('&', 'and').replace('<', '').replace('>', '').strip())
        safe_desc = (meta_description
            .replace('"', "'").replace('&', 'and').replace('<', '').replace('>', '').strip())

        header = (
            "---\n"
            "layout: post\n"
            f"title: \"{safe_title}\"\n"
            f"date: {date_str}\n"
            "author: \"Amit Kumar\"\n"
            f"pillar: \"{pillar['id']}\"\n"
            f"content_mode: \"{CONTENT_MODE}\"\n"
            f"permalink: /{pillar['permalink_base']}/{chosen_slug}/\n"
            f"excerpt: \"{safe_excerpt}\"\n"
            f"description: \"{safe_desc}\"\n"
            f"keywords: \"{', '.join(pillar['primary_keywords'])}, {', '.join(pillar.get('us_keywords', [])[:2])}, {', '.join(pillar.get('india_keywords', [])[:2])}\"\n"
            f"categories: [{pillar['category']}]\n"
            f"tags: [{pillar['tag']}]\n"
            f"fear_greed: \"{fear_greed}\"\n"
            f"trending: \"{', '.join(trends[:5])}\"\n"
            "---\n\n"
        )

        schema_block = f'<script type="application/ld+json">\n{schema_json}\n</script>\n\n'

        if not os.path.exists(POSTS_DIR):
            os.makedirs(POSTS_DIR)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header + schema_block + content)

        article_url = f"{SITE_URL}/{pillar['permalink_base']}/{chosen_slug}/"
        print(f"  ✅ /{pillar['permalink_base']}/{chosen_slug}/")
        print(f"     {article_title[:70]}...")
        return True, article_url

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False, None


def generate_all_articles():
    print("=" * 60)
    print(f"  AI360Trading Daily Bot — {date_display}")
    print(f"  Mode: {CONTENT_MODE.upper()}")
    if CONTENT_MODE == "holiday":
        print(f"  Holiday: {HOLIDAY_NAME}")
    print("=" * 60)

    print("\nFetching data...")
    prices     = get_live_prices()
    trends     = get_google_trends()
    fear_greed = get_fear_greed()

    if CONTENT_MODE == "market":
        print(f"  S&P 500  : {prices.get('S&P 500',{}).get('display','N/A')}")
        print(f"  NIFTY    : {prices.get('NIFTY 50',{}).get('display','N/A')}")
        print(f"  Bitcoin  : {prices.get('Bitcoin',{}).get('display','N/A')}")
        print(f"  Gold     : {prices.get('Gold',{}).get('display','N/A')}")
        print(f"  F&G      : {fear_greed}")
    print(f"  Trending : {', '.join(trends[:3])}")

    results        = []
    published_urls = []

    for i, pillar in enumerate(PILLARS):
        already_exists = False
        if os.path.exists(POSTS_DIR):
            pillar_today = [
                f for f in os.listdir(POSTS_DIR)
                if f.endswith('.md') and f.startswith(date_str) and pillar['id'] in f
            ]
            if pillar_today:
                print(f"\n  [{i+1}/4] ⏭️  Skipping {pillar['name']} — already exists today")
                results.append((pillar['name'], True))
                already_exists = True

        if already_exists:
            continue

        persona_pool = PILLAR_PERSONA_MAP.get(pillar['id'], [0,1,2,3,4,5])
        persona_idx  = persona_pool[now.weekday() % len(persona_pool)]
        persona      = PERSONAS[persona_idx]
        success, article_url = generate_article(
            pillar, prices, trends, fear_greed, persona, i + 1
        )
        results.append((pillar['name'], success))
        if success and article_url:
            published_urls.append(article_url)
        if i < len(PILLARS) - 1:
            time.sleep(3)

    print("\n" + "=" * 60)
    print("  DAILY PUBLISH SUMMARY")
    print("=" * 60)
    for name, success in results:
        print(f"  {'✅' if success else '❌'} {name}")

    if published_urls:
        print(f"\n📡 Submitting {len(published_urls)} new URLs to Google Indexing API...")
        submit_urls_to_google(published_urls)
    else:
        print("\n  No new articles to submit to Google.")

    cleanup_old_posts()
    print(f"\n  Done. Mode was: {CONTENT_MODE.upper()}")


if __name__ == "__main__":
    generate_all_articles()
