import os
import pytz
import requests
import random
import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from groq import Groq

# Import SEO seeds from content calendar
# These bias article titles and content toward specific long-tail, high-CPC keywords
# that actually rank on Google vs broad generic terms that Bloomberg already dominates
try:
    from content_calendar import get_article_seo_seeds
    _CALENDAR_AVAILABLE = True
except ImportError:
    _CALENDAR_AVAILABLE = False
    print("[WARN] content_calendar.py not found — SEO seeds skipped")

# ─── Content Mode ─────────────────────────────────────────────────────────────
# "market"  → normal weekday — live market data + analysis articles
# "weekend" → Saturday/Sunday — educational/beginner articles
# "holiday" → Indian market holiday — motivational/savings/storytelling articles

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")

print(f"[MODE] generate_articles.py running in mode: {CONTENT_MODE.upper()}")

# ─── Affiliate Links (country-aware) ─────────────────────────────────────────
# Free referral programs — earn per lead or per policy/account opened
# Replace placeholder URLs with your actual affiliate tracking links after signup:
#   India insurance : partners.policybazaar.com  (instant approval)
#   USA insurance   : policygenius.com/partners  (instant approval)
#   UK insurance    : comparethemarket.com/affiliates (instant approval)
#   India broker    : already in README — Zerodha + Dhan links
#   USA broker      : webull.com/activity/register (instant approval)
#   UK broker       : trading212.com/refer        (instant approval)
#   India loans     : paisabazaar.com/partner     (instant approval)
#   USA loans       : lendingtree.com/affiliates  (instant approval)
#   UK loans        : moneysupermarket.com/affiliates (instant approval)

AFFILIATE_LINKS = {
    "insurance": {
        "india": os.environ.get("AFFILIATE_INSURANCE_IN", "https://www.policybazaar.com/"),
        "usa":   os.environ.get("AFFILIATE_INSURANCE_US", "https://www.policygenius.com/"),
        "uk":    os.environ.get("AFFILIATE_INSURANCE_UK", "https://www.comparethemarket.com/"),
    },
    "broker": {
        "india": os.environ.get("AFFILIATE_BROKER_IN", "https://zerodha.com/open-account/"),
        "usa":   os.environ.get("AFFILIATE_BROKER_US", "https://webull.com/"),
        "uk":    os.environ.get("AFFILIATE_BROKER_UK", "https://www.trading212.com/"),
    },
    "loans": {
        "india": os.environ.get("AFFILIATE_LOANS_IN", "https://www.paisabazaar.com/"),
        "usa":   os.environ.get("AFFILIATE_LOANS_US", "https://www.lendingtree.com/"),
        "uk":    os.environ.get("AFFILIATE_LOANS_UK", "https://www.moneysupermarket.com/"),
    },
    "investing": {
        "india": os.environ.get("AFFILIATE_INVEST_IN", "https://zerodha.com/open-account/"),
        "usa":   os.environ.get("AFFILIATE_INVEST_US", "https://webull.com/"),
        "uk":    os.environ.get("AFFILIATE_INVEST_UK", "https://www.trading212.com/"),
    },
}

# ─── Affiliate link helper ────────────────────────────────────────────────────
def get_affiliate_block(pillar_id):
    """
    Returns a prompt instruction block telling the AI which affiliate links
    to insert naturally for this pillar. AI decides placement — never forced.
    NOTE: Insurance/finance affiliates are country-specific by law.
          India links for India readers, USA links for USA readers, UK for UK.
          China is excluded — closed market, no foreign finance affiliates work there.
    """
    if pillar_id == "personal-finance":
        return f"""
AFFILIATE LINKS — insert naturally inside the article body, maximum 3 total across the whole article.
Never use the word "sponsored" or "affiliate". Insert as natural recommendations only.

Rules:
- Only insert when the paragraph directly discusses that product category
- Write naturally: "You can compare term plans at [PolicyBazaar](link)" or
  "US readers can compare plans at [Policygenius](link)" etc.
- Never insert more than one link per section
- Never force a link where it does not fit the paragraph

Available links by country:
- India insurance comparison: {AFFILIATE_LINKS['insurance']['india']}
- USA insurance comparison:   {AFFILIATE_LINKS['insurance']['usa']}
- UK insurance comparison:    {AFFILIATE_LINKS['insurance']['uk']}
- India investing/broker:     {AFFILIATE_LINKS['broker']['india']}
- India loans/credit:         {AFFILIATE_LINKS['loans']['india']}
- USA investing/broker:       {AFFILIATE_LINKS['broker']['usa']}
- UK investing/broker:        {AFFILIATE_LINKS['broker']['uk']}
"""
    elif pillar_id == "stock-market":
        return f"""
AFFILIATE LINKS — insert naturally, maximum 2 total, only where discussing opening a trading account.
- India broker: {AFFILIATE_LINKS['broker']['india']}
- USA broker:   {AFFILIATE_LINKS['broker']['usa']}
- UK broker:    {AFFILIATE_LINKS['broker']['uk']}
Write naturally: "Indian traders can open a free account at [Zerodha](link)" etc.
Never force — only insert if the paragraph naturally leads to it.
"""
    elif pillar_id == "ai-trading":
        return f"""
AFFILIATE LINKS — insert naturally, maximum 2 total, only where discussing starting to trade.
- India broker: {AFFILIATE_LINKS['broker']['india']}
- USA broker:   {AFFILIATE_LINKS['broker']['usa']}
- UK broker:    {AFFILIATE_LINKS['broker']['uk']}
"""
    else:
        # bitcoin — no broker link forced, too risky legally
        return ""


# ─── Google Indexing API ──────────────────────────────────────────────────────
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
        header = base64.urlsafe_b64encode(
            _json.dumps({"alg": "RS256", "typ": "JWT"}).encode()
        ).rstrip(b'=').decode()
        now_ts = int(_time.time())
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
                "assertion": jwt_token,
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
                    print(f"    ✅ Indexed: {url}")
                    success_count += 1
                else:
                    print(f"    ⚠️  Index failed ({resp.status_code}): {url}")
                time.sleep(0.5)
            except Exception as e:
                print(f"    ⚠️  Index error for {url}: {e}")
        print(f"  📡 Google Indexing API: {success_count}/{len(urls)} URLs submitted")
    except Exception as e:
        print(f"  ⚠️  Indexing API error: {e} — articles still published normally")


SITE_URL = "https://ai360trading.in"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

ist     = pytz.timezone('Asia/Kolkata')
now     = datetime.now(ist)
date_str     = now.strftime("%Y-%m-%d")
date_display = now.strftime("%B %d, %Y")
day_name     = now.strftime("%A")
day_of_year  = now.timetuple().tm_yday   # 1-365 — used everywhere instead of now.day

POSTS_DIR = os.path.join(os.getcwd(), '_posts')
MAX_POSTS = 60


# ─── HOLIDAY / WEEKEND ARTICLE PILLARS ───────────────────────────────────────
# Used when CONTENT_MODE is "holiday" or "weekend"
# Title templates are now style guides only — AI generates the actual title from live data
# Target countries: India, USA, UK, UAE, Canada, Australia, Brazil
# China is excluded — closed market, no foreign finance affiliates or meaningful traffic

HOLIDAY_PILLARS = [
    {
        "id": "stock-market",
        "name": "Stock Market",
        "permalink_base": "stock-market",
        "category": "Stock-Market",
        "tag": "stock-market",
        "primary_keywords": ["stock market basics", "how to invest", "index fund", "S&P 500", "NIFTY"],
        "us_keywords":     ["how to invest in stocks USA", "best index fund 2026", "S&P 500 investing"],
        "uk_keywords":     ["how to invest UK 2026", "FTSE 100 beginner guide"],
        "brazil_keywords": ["como investir na bolsa 2026", "IBOVESPA iniciantes"],
        "india_keywords":  ["how to invest in share market India", "Nifty 50 beginner guide", "SIP vs lump sum"],
        "title_style_examples": [
            "How to Start Investing in the Stock Market — Complete 2026 Guide for US, UK and India",
            "Index Funds vs Stock Picking — The Data Will Surprise You",
            "The Biggest Mistake New Investors Make — And the Simple Fix",
            "How Compound Interest Really Works — Numbers That Change Everything",
            "Stock Market Basics — Everything a Beginner Needs to Know Right Now",
            "Why Dollar-Cost Averaging Beats Timing the Market — Proof with Numbers",
            "NIFTY vs S&P 500 — Which Index Should You Invest In?",
            "How to Invest ₹5000 a Month and Retire Comfortably",
            "Dividend Investing vs Growth Investing — The Honest Comparison",
            "What Buffett's Portfolio Tells Us About Investing in 2026",
        ],
        "article_focus": """Write a comprehensive beginner-friendly stock market education article covering:
- How stock markets work globally (India NSE/BSE, US NYSE/NASDAQ, UK LSE, Brazil B3)
- Why index fund investing beats stock picking for most people
- How to start investing with small amounts in each country
- Compound interest examples with real numbers
- Common beginner mistakes and how to avoid them
- Actionable steps readers can take today
Target: complete beginners in US, UK, Brazil and India""",
        "news_queries": ["stock+market+beginner+investing+2026", "index+fund+returns+2026", "how+to+invest+money+2026"],
    },
    {
        "id": "bitcoin",
        "name": "Bitcoin and Crypto",
        "permalink_base": "bitcoin",
        "category": "Bitcoin-Crypto",
        "tag": "bitcoin",
        "primary_keywords": ["Bitcoin explained", "how to buy crypto safely", "crypto beginner guide 2026"],
        "us_keywords":     ["how to buy bitcoin USA 2026", "crypto investing guide", "bitcoin safe investment"],
        "uk_keywords":     ["how to buy bitcoin UK 2026", "crypto regulation UK"],
        "brazil_keywords": ["como comprar bitcoin 2026", "criptomoedas guia Brasil"],
        "india_keywords":  ["how to buy bitcoin India 2026", "crypto tax India", "bitcoin INR guide"],
        "title_style_examples": [
            "Bitcoin Explained Simply — Complete Beginner Guide for US, UK, India and Brazil",
            "How to Buy Crypto Safely — Step by Step Guide",
            "Is Bitcoin a Safe Investment? — Honest Answer for Beginners",
            "Crypto Beginner Mistakes That Cost People Money — And How to Avoid Them",
            "Bitcoin Halving Cycle Explained — What Every New Investor Should Know",
            "Ethereum vs Bitcoin — Which Should a Beginner Buy First?",
            "How Much of Your Portfolio Should Be in Crypto? The Answer May Surprise You",
            "Bitcoin Wallets Explained — Cold vs Hot and Which Is Safer",
            "Crypto Taxes in India, USA and UK — What You Must Know",
            "5 Crypto Scams Targeting Beginners Right Now — And How to Spot Them",
        ],
        "article_focus": """Write a comprehensive beginner crypto education article covering:
- What Bitcoin and Ethereum actually are in simple terms
- How to buy crypto safely in US, UK, Brazil and India (step by step)
- How much to invest — risk management for beginners
- Cold wallet vs exchange — what new investors need to know
- Bitcoin halving cycle explained simply
- Common crypto scams and how to avoid them
- Tax implications in each country
Target: complete beginners worldwide who keep hearing about crypto""",
        "news_queries": ["bitcoin+beginner+guide+2026", "how+to+buy+crypto+safely+2026", "bitcoin+halving+explained"],
    },
    {
        "id": "personal-finance",
        "name": "Personal Finance",
        "permalink_base": "personal-finance",
        "category": "Personal-Finance",
        "tag": "personal-finance",
        "primary_keywords": ["personal finance tips 2026", "how to save money", "emergency fund", "term life insurance"],
        "us_keywords":     ["best savings account USA 2026", "401k guide", "term life insurance USA", "Policygenius review"],
        "uk_keywords":     ["best ISA 2026", "UK pension guide", "how to save money UK", "CompareTheMarket insurance"],
        "brazil_keywords": ["como economizar dinheiro 2026", "previdencia privada Brasil"],
        "india_keywords":  ["how to save money India 2026", "best term insurance India", "PPF vs ELSS", "PolicyBazaar review"],
        "title_style_examples": [
            "Personal Finance Complete Guide — US, UK, India and Brazil",
            "Why 80% of People Never Build Wealth — And the Simple Fix",
            "Emergency Fund: How Much You Actually Need Right Now",
            "Best Term Life Insurance — US, UK and India Compared with Real Numbers",
            "The 50-30-20 Rule — Does It Actually Work? Real Numbers Inside",
            "How to Build Your First Investment Portfolio on ₹5000 a Month",
            "Retirement Planning at 30 vs 40 — The Numbers Are Shocking",
            "Mutual Funds vs Fixed Deposit vs Gold — Honest 2026 Comparison",
            "How to Get Out of Debt Faster — Step by Step Plan That Works",
            "The One Financial Habit Rich People Never Skip",
            "SIP vs Lump Sum — Data-Driven Answer for Indian Investors",
            "Credit Score Guide — US, UK and India Compared",
            "Tax Saving Investments — India, US and UK 2026",
            "How to Save Your First ₹1 Lakh — Realistic Plan for Beginners",
            "Health Insurance vs Term Insurance — Which Comes First?",
            "What Happens to Your Money When Inflation Rises — and How to Fight Back",
            "Best Savings Accounts — US, UK, India Interest Rates Compared",
            "How to Invest When You Are in Debt — Honest Advice",
            "Passive Income Ideas That Actually Work — No Hype",
            "ULIP vs Term Plus Mutual Fund — The Math Nobody Shows You",
            "LIC vs HDFC vs ICICI Term Insurance — Which One Is Right for You",
            "How Much Life Cover Do You Actually Need — Calculator with Real Numbers",
            "Family Health Insurance Plans — India, USA and UK Compared",
            "NPS vs PPF vs EPF — Which Retirement Account Wins in India?",
        ],
        "article_focus": """Write a comprehensive personal finance guide covering:
- Term life insurance comparison across US, UK, India, Brazil with actual rates
- Investment options compared: stocks, mutual funds/SIP, ETFs, bonds, real estate
- Tax saving strategies specific to each country with actionable steps
- Retirement planning: 401k (US), pension (UK), NPS/PPF (India)
- Emergency fund building and best savings account rates
- Credit score improvement tips for US and India
- How current conditions affect personal finance decisions
- Practical advice readers can implement today — not generic advice
IMPORTANT: Insurance referral context — readers from India can compare plans at PolicyBazaar,
US readers at Policygenius, UK readers at CompareTheMarket. Mention naturally when relevant.""",
        "news_queries": ["personal+finance+tips+2026", "emergency+fund+guide", "term+life+insurance+2026", "best+savings+account+2026"],
    },
    {
        "id": "ai-trading",
        "name": "AI and Trading Technology",
        "permalink_base": "ai-trading",
        "category": "AI-Trading",
        "tag": "ai-trading",
        "primary_keywords": ["AI trading tools 2026", "free trading tools", "algorithmic trading beginner", "fintech 2026"],
        "us_keywords":     ["best free AI trading tools USA 2026", "AI stock screener free"],
        "uk_keywords":     ["AI trading UK 2026", "free stock analysis tools UK"],
        "brazil_keywords": ["ferramentas gratuitas trading 2026", "inteligencia artificial bolsa"],
        "india_keywords":  ["free AI trading tools India 2026", "best stock screener India free", "algo trading beginner India"],
        "title_style_examples": [
            "Best Free AI Trading Tools — Complete Guide for US, UK, India and Brazil",
            "How to Use AI for Stock Market Analysis — Free Tools That Actually Work",
            "Free vs Paid Trading Tools — Honest Comparison",
            "Algorithmic Trading for Beginners — No Coding Required Guide",
            "The Free Stock Screeners That Professional Traders Actually Use",
            "How AI Is Changing Retail Trading in 2026 — What You Need to Know",
            "ChatGPT for Trading — What It Can and Cannot Do Honestly",
            "5 Free Tools That Help You Spot Breakouts Before They Happen",
            "Machine Learning in Trading — Explained Simply for Non-Coders",
            "How I Use AI to Filter 90% of Bad Trades Before They Happen",
        ],
        "article_focus": """Write a comprehensive guide to free AI and trading tools covering:
- Best completely free stock screeners for India, US, UK and Brazil
- How retail traders can use AI tools for better decisions today
- Free technical analysis tools vs paid ones — honest comparison
- How algorithmic trading works without coding knowledge
- AI tools that actually work vs overhyped ones
- How to build a simple trading system using free tools
- Risk management tools that are free and effective
Target: retail traders of all levels looking for an edge without paying""",
        "news_queries": ["free+AI+trading+tools+2026", "best+stock+screener+free+2026", "algorithmic+trading+beginner+2026"],
    },
]


# ─── MARKET DAY PILLARS ───────────────────────────────────────────────────────
MARKET_PILLARS = [
    {
        "id": "stock-market",
        "name": "Stock Market",
        "permalink_base": "stock-market",
        "category": "Stock-Market",
        "tag": "stock-market",
        "primary_keywords": ["S&P 500", "NIFTY", "NASDAQ", "SENSEX", "IBOVESPA", "stock market today"],
        "us_keywords":     ["stock market today", "S&P 500 forecast", "best stocks to buy today", "NASDAQ outlook"],
        "uk_keywords":     ["FTSE 100 today", "UK stock market", "London stock exchange today"],
        "brazil_keywords": ["IBOVESPA hoje", "bolsa de valores hoje", "mercado financeiro"],
        "india_keywords":  ["nifty analysis today", "trading signals India", "nifty support resistance"],
        "title_style_examples": [
            "NIFTY and S&P 500 Today — Here Is What I Think Happens Next",
            "S&P 500 and NIFTY: The Level Nobody Is Watching",
            "Why This Market Move Is Different From What Media Is Saying",
            "I Was Wrong About This — Here Is What the Chart Actually Shows",
            "NIFTY Support and Resistance — Exact Levels for Today",
            "Why Smart Money Is Moving While Retail Panics",
            "The One Chart That Explains Today's Market Move",
            "Sector Rotation Is Happening — Here Is Where Money Is Going",
            "FII Selling vs DII Buying — Who Wins This Battle?",
            "NIFTY at Key Level — Break Above or Reject?",
            "S&P 500 Divergence From NIFTY — What It Means for Indian Traders",
            "Bitcoin and Stocks Moving Together Again — Danger Signal or Opportunity?",
            "Global Markets Flash a Warning — India's Position Explained",
            "The Trade Setup I Am Looking at Right Now",
            "Bears vs Bulls Today — Which Side Has the Edge?",
        ],
        "article_focus": """Write a comprehensive stock market analysis covering:
- S&P 500 and NASDAQ deep technical and fundamental analysis
- NIFTY 50 and SENSEX India market analysis with FII/DII flows
- IBOVESPA Brazil market analysis and EM correlation
- FTSE 100 UK market overview
- Support/resistance levels for all major indices
- Sector rotation analysis — which sector is moving and why
- What smart money is doing vs retail traders""",
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
    },
    {
        "id": "bitcoin",
        "name": "Bitcoin and Crypto",
        "permalink_base": "bitcoin",
        "category": "Bitcoin-Crypto",
        "tag": "bitcoin",
        "primary_keywords": ["Bitcoin", "Ethereum", "crypto market today", "BTC price", "cryptocurrency"],
        "us_keywords":     ["bitcoin price today", "crypto market today", "is bitcoin going up", "BTC USD today"],
        "uk_keywords":     ["bitcoin price GBP", "crypto UK today", "bitcoin today pound"],
        "brazil_keywords": ["bitcoin hoje", "criptomoedas hoje", "bitcoin real hoje"],
        "india_keywords":  ["bitcoin price INR today", "crypto India today", "bitcoin rupees today"],
        "title_style_examples": [
            "Bitcoin Today — Crypto Market Analysis and Price Levels",
            "Is Bitcoin Going Up or Down? Analysis for Today",
            "Bitcoin and Crypto Market — What the Data Shows Right Now",
            "BTC at This Level — What Smart Money Is Doing Now",
            "What Is Driving Crypto Markets Today",
            "Fear and Greed Index Signals — Bitcoin Direction Analysis",
            "Bitcoin Price Today — US, India and Brazil Perspective",
            "Crypto Market Direction — Bitcoin Intelligence Report",
            "Altcoin Season or Bitcoin Dominance — What Today's Data Shows",
            "Ethereum vs Bitcoin — Which Is Stronger Right Now?",
            "Institutional Buying in Crypto — What the Flows Say Today",
            "Bitcoin On-Chain Data Reveals — What Retail Is Missing",
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
    },
    {
        "id": "personal-finance",
        "name": "Personal Finance",
        "permalink_base": "personal-finance",
        "category": "Personal-Finance",
        "tag": "personal-finance",
        "primary_keywords": ["term life insurance", "best investment 2026", "retirement planning", "tax saving", "personal finance"],
        "us_keywords":     ["best term life insurance USA 2026", "401k investing 2026", "mortgage rates today", "Policygenius"],
        "uk_keywords":     ["best ISA 2026 UK", "UK pension 2026", "life insurance UK", "CompareTheMarket"],
        "brazil_keywords": ["previdencia privada 2026", "seguro de vida Brasil", "melhores investimentos 2026"],
        "india_keywords":  ["best term insurance India 2026", "SIP investment returns", "PPF vs ELSS 2026", "PolicyBazaar"],
        "title_style_examples": [
            "Best Term Life Insurance — US, UK and India Complete Guide",
            "Personal Finance Guide for Today — What the Data Says Right Now",
            "I Ran the Numbers on SIP vs Lump Sum — The Answer Surprised Me",
            "Why Most Indians Are Getting Their Term Insurance Wrong",
            "What Today's Market Move Means for Your SIP and Savings",
            "The Rs.10,000 Per Month Investment Plan That Actually Works",
            "Stop Waiting for the Perfect Time — Here Is What the Data Says",
            "Your Emergency Fund Is Probably Wrong — Here Is the Right Size",
            "How to Protect Your Money When Markets Are Crashing",
            "401k vs NPS vs ISA — Which Retirement Plan Wins?",
            "How to Build Wealth When the Market Is Flat",
            "The Retirement Number Most People Never Calculate",
            "SIP During a Bear Market — Should You Stop, Pause or Double Up?",
            "Credit Card Debt vs Investment — Which to Tackle First",
            "How Rising Inflation Destroys Savings — And 3 Ways to Fight Back",
            "Gold vs Equity vs Real Estate — Where Is Money Safer Right Now?",
            "How to Build a ₹1 Crore Portfolio on a Salaried Income",
            "When Should You Buy Term Insurance? The Data Gives a Clear Answer",
            "LIC vs HDFC vs ICICI Term Insurance — Honest Comparison",
            "Family Floater Health Insurance — Best Plans Compared",
        ],
        "article_focus": """Write a comprehensive personal finance guide covering:
- Term life insurance comparison across US, UK, India, Brazil with actual rates
- Investment options compared: stocks, mutual funds/SIP, ETFs, bonds, real estate
- Tax saving strategies specific to each country with actionable steps
- Retirement planning: 401k (US), pension (UK), NPS/PPF (India)
- Emergency fund building and best savings account rates
- Credit score improvement tips for US and India
- How current market conditions affect personal finance decisions
- Practical advice readers can implement today — not generic advice
IMPORTANT: Insurance referral context — India readers can compare plans at PolicyBazaar,
US readers at Policygenius, UK readers at CompareTheMarket. Mention naturally when relevant.""",
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
    },
    {
        "id": "ai-trading",
        "name": "AI and Trading Technology",
        "permalink_base": "ai-trading",
        "category": "AI-Trading",
        "tag": "ai-trading",
        "primary_keywords": ["AI trading 2026", "algorithmic trading", "fintech", "AI stock market", "trading technology"],
        "us_keywords":     ["AI stock trading 2026", "best AI trading algorithm", "fintech stocks today", "AI investing USA"],
        "uk_keywords":     ["AI trading UK 2026", "algorithmic trading London", "fintech UK stocks"],
        "brazil_keywords": ["trading automatizado Brasil", "inteligencia artificial investimentos", "fintech brasil 2026"],
        "india_keywords":  ["algo trading India NSE", "AI trading bot India", "automated trading NSE BSE", "quant trading India"],
        "title_style_examples": [
            "The AI Signal on NIFTY I Almost Missed Today",
            "What My Algorithm Shows vs What I Actually Think",
            "I Backtested This Strategy 5 Years — Here Are the Real Results",
            "Free AI Tools That Are Actually Useful for Trading",
            "Why AI Got the Direction Wrong — And What It Means for Your Trades",
            "The Algorithm Spotted This Pattern Before the Move",
            "AI vs Human Trader — Who Called It Better This Week?",
            "How I Use AI to Filter 90% of Bad Trades Before They Happen",
            "Machine Learning Signals vs Technical Analysis — Which Works Better?",
            "The Free Screener That Caught This Week's Best Breakout",
            "How Retail Traders Can Use AI Without Writing a Single Line of Code",
            "Quantitative Analysis for Beginners — What the Numbers Say Today",
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
    "stock-market":    [0, 1, 2, 3, 4, 5],
    "bitcoin":         [2, 3, 4, 5, 0, 1],
    "personal-finance":[6, 1, 3, 6, 1, 3],
    "ai-trading":      [7, 2, 5, 7, 2, 5],
}


# ─── Live Prices ──────────────────────────────────────────────────────────────
def get_live_prices():
    if CONTENT_MODE in ("holiday", "weekend"):
        print("  📅 Holiday/Weekend mode — skipping live price fetch")
        return {}
    symbols = {
        "NIFTY 50":       "^NSEI",
        "SENSEX":         "^BSESN",
        "Bank Nifty":     "^NSEBANK",
        "India VIX":      "^INDIAVIX",
        "S&P 500":        "^GSPC",
        "NASDAQ":         "^IXIC",
        "Dow Jones":      "^DJI",
        "US 10Y Yield":   "^TNX",
        "FTSE 100":       "^FTSE",
        "Nikkei 225":     "^N225",
        "DAX":            "^GDAXI",
        "IBOVESPA":       "^BVSP",
        "Gold":           "GC=F",
        "Silver":         "SI=F",
        "Crude Oil WTI":  "CL=F",
        "Bitcoin":        "BTC-USD",
        "Ethereum":       "ETH-USD",
        "USD/INR":        "INR=X",
        "USD/BRL":        "BRL=X",
        "DXY (Dollar)":   "DX-Y.NYB",
        "EUR/USD":        "EURUSD=X",
    }
    prices = {}
    for name, symbol in symbols.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, timeout=8)
            data = r.json()
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
    # Target: India, USA, UK, UAE/Australia (no China — closed market)
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
        'term insurance', 'health insurance', 'life insurance', 'policybazaar',
        'policygenius', 'comparethemarket', 'lic', 'hdfc', 'icici',
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
            "PolicyBazaar term insurance", "Policygenius life insurance",
        ]
    seen   = set()
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
            r = requests.get(url, timeout=8)
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


def get_recent_posts(pillar_id, limit=5):
    try:
        files = sorted(
            [f for f in os.listdir(POSTS_DIR) if f.endswith('.md')],
            reverse=True
        )
        recent = []
        for fname in files[:40]:
            if pillar_id in fname:
                fpath = os.path.join(POSTS_DIR, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    title         = None
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


def get_recent_titles(pillar_id, days=14):
    """Return list of recent article titles for this pillar to help AI avoid repeating topics."""
    try:
        files = sorted(
            [f for f in os.listdir(POSTS_DIR) if f.endswith('.md') and pillar_id in f],
            reverse=True
        )
        titles = []
        for fname in files[:days]:
            fpath = os.path.join(POSTS_DIR, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('title:'):
                            titles.append(line.replace('title:', '').strip().strip('"'))
                            break
            except:
                pass
        return titles
    except:
        return []


def generate_schema(title, description, pillar, url_slug):
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type":           "Article",
                "headline":        title,
                "description":     description,
                "datePublished":   date_str,
                "dateModified":    date_str,
                "author": {
                    "@type": "Person",
                    "name":  "Amit Kumar",
                    "url":   "https://ai360trading.in/about/"
                },
                "publisher": {
                    "@type": "Organization",
                    "name":  "AI360Trading",
                    "url":   "https://ai360trading.in",
                    "logo":  {
                        "@type": "ImageObject",
                        "url":   "https://ai360trading.in/public/image/header.webp"
                    }
                },
                "mainEntityOfPage": f"https://ai360trading.in/{pillar['permalink_base']}/{url_slug}/",
                "keywords":         ", ".join(pillar['primary_keywords']),
                "articleSection":   pillar['name'],
                "inLanguage":       "en-US"
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home",          "item": "https://ai360trading.in/"},
                    {"@type": "ListItem", "position": 2, "name": pillar['name'],  "item": f"https://ai360trading.in/topics/{pillar['tag']}/"},
                    {"@type": "ListItem", "position": 3, "name": title,           "item": f"https://ai360trading.in/{pillar['permalink_base']}/{url_slug}/"}
                ]
            }
        ]
    }
    return json.dumps(schema, indent=2)


# ─── AI Title Generator ───────────────────────────────────────────────────────
# This replaces the old template-index approach.
# The AI generates a completely fresh title every day based on:
#   - Today's live prices and market data
#   - Today's trending searches
#   - Today's news headlines
#   - Recent titles (to avoid repeating)
#   - Style examples (for tone guidance only — not to copy)
# Result: titles are unique FOREVER — not just 365 days.

def generate_ai_title(pillar, prices, trends, fear_greed, recent_titles, article_index):
    """
    Use Groq AI to generate a completely unique, data-driven title for today.
    Falls back to style-example rotation only if AI call fails.
    """

    # Build market context summary for the title prompt
    if CONTENT_MODE in ("holiday", "weekend"):
        market_context = f"Today is {day_name}, {date_display}. Markets are closed — this is an educational article."
        trending_context = f"Trending searches today: {', '.join(trends[:6])}"
    else:
        nifty  = prices.get("NIFTY 50",  {}).get("display", "N/A")
        sp500  = prices.get("S&P 500",   {}).get("display", "N/A")
        btc    = prices.get("Bitcoin",   {}).get("display", "N/A")
        gold   = prices.get("Gold",      {}).get("display", "N/A")
        nasdaq = prices.get("NASDAQ",    {}).get("display", "N/A")
        market_context = (
            f"Today is {day_name}, {date_display}. "
            f"NIFTY: {nifty} | S&P 500: {sp500} | Bitcoin: {btc} | "
            f"Gold: {gold} | NASDAQ: {nasdaq} | Fear & Greed: {fear_greed}"
        )
        trending_context = f"Trending searches right now: {', '.join(trends[:6])}"

    recent_titles_text = ""
    if recent_titles:
        recent_titles_text = (
            "\nDO NOT repeat or closely echo these recent titles from the last 14 days:\n"
            + "\n".join(f"- {t}" for t in recent_titles)
        )

    style_examples = "\n".join(f"- {t}" for t in pillar['title_style_examples'][:6])

    title_prompt = f"""You are writing a title for a financial article on AI360Trading (ai360trading.in).

Pillar: {pillar['name']}
Today: {day_name}, {date_display}
Market data: {market_context}
{trending_context}
{recent_titles_text}

Style examples (for tone guidance only — do NOT copy these, generate something fresh):
{style_examples}

Rules for the title:
1. Must reflect TODAY's actual market situation or trending topic — not generic
2. Must be specific — include real numbers, directions, or named assets when possible
3. Must appeal to readers in India, USA and UK simultaneously
4. Must be 8-15 words
5. Must NOT start with "The" or "How to" if the last 3 recent titles started that way
6. Must be unique — different angle from all recent titles listed above
7. No clickbait — must deliver on what it promises
8. No banned phrases: "Game-changer", "Deep dive", "Navigating", "Landscape", "Robust"

Respond with ONLY the title — nothing else. No quotes. No explanation."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You generate precise, data-driven financial article titles. Respond with only the title text."},
                {"role": "user",   "content": title_prompt}
            ],
            temperature=0.9,
            max_tokens=60,
            top_p=0.95,
        )
        ai_title = completion.choices[0].message.content.strip().strip('"').strip("'")
        # Sanity check — must be reasonable length
        if 5 <= len(ai_title.split()) <= 20:
            print(f"    [TITLE-AI] {ai_title}")
            return ai_title
        else:
            raise ValueError(f"AI title length out of range: {len(ai_title.split())} words")
    except Exception as e:
        print(f"    [TITLE-AI] AI title failed ({e}) — using style-example fallback")
        # Fallback: rotate through style examples using day_of_year
        # day_of_year (1-365) ensures no monthly repeat
        pillar_offset = ["stock-market","bitcoin","personal-finance","ai-trading"].index(pillar['id']) \
                        if pillar['id'] in ["stock-market","bitcoin","personal-finance","ai-trading"] else 0
        idx = (day_of_year + pillar_offset * 61 + article_index * 7) % len(pillar['title_style_examples'])
        # Avoid recently used titles
        for _ in range(len(pillar['title_style_examples'])):
            candidate = pillar['title_style_examples'][idx]
            if not any(candidate.lower()[:30] in rt.lower() for rt in recent_titles):
                break
            idx = (idx + 1) % len(pillar['title_style_examples'])
        fallback_title = pillar['title_style_examples'][idx]
        print(f"    [TITLE-FALLBACK] {fallback_title}")
        return fallback_title


# ─── Article Generator ────────────────────────────────────────────────────────
def generate_article(pillar, prices, trends, fear_greed, persona, article_index):
    print(f"\n  [{article_index}/4] Generating: {pillar['name']} [{CONTENT_MODE} mode]...")

    news = get_live_news(pillar['news_queries'])

    # Build market context
    if CONTENT_MODE in ("holiday", "weekend"):
        price_lines = "Market closed today — educational content mode"
        mode_note   = (
            f"This is a {'holiday' if CONTENT_MODE == 'holiday' else 'weekend'} article. "
            "Write educational, evergreen content. No live market data. "
            "Focus on timeless investment wisdom applicable to US, UK, Brazil and India readers."
        )
        if CONTENT_MODE == "holiday":
            mode_note += f" Today is {HOLIDAY_NAME} — a market holiday."
    else:
        price_lines = "\n".join([f"  - {k}: {v['display']}" for k, v in prices.items()])
        mode_note   = ""

    # Get recent titles for this pillar — AI uses these to avoid repetition
    recent_titles = get_recent_titles(pillar['id'], days=14)

    # Generate AI title — unique every day, forever
    article_title = generate_ai_title(pillar, prices, trends, fear_greed, recent_titles, article_index)

    # Build URL slug from title
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

    _stop = {
        'the','a','an','and','or','but','in','on','at','to','for','of',
        'with','is','are','was','were','its','this','that','i','my','we',
        'you','he','she','they','what','why','how','when','where','from',
        'by','as','so','if','just','vs','im','heres','thats','dont'
    }
    _words    = [w for w in _title_clean.split('-') if w and w not in _stop]
    title_slug = '-'.join(_words[:6])

    file_slug = f"{date_str}-{pillar['id']}-{title_slug}"
    chosen_slug = title_slug
    file_path   = os.path.join(POSTS_DIR, f"{file_slug}.md")

    # Internal links from recent posts
    recent_posts       = get_recent_posts(pillar['id'])
    internal_links_text = ""
    if recent_posts:
        internal_links_text = "\nINTERNAL LINKS TO INCLUDE NATURALLY IN BODY:\n"
        for post in recent_posts:
            internal_links_text += f'- [{post["title"]}](/{pillar["permalink_base"]}/{post["slug"]}/)\n'

    # Format type rotation — day_of_year ensures no monthly repeat
    FORMAT_TYPES = [
        "story_led", "contrarian", "trader_notebook",
        "macro_driver", "chart_story", "question_led",
    ]
    _pillar_idx = (
        ["stock-market","bitcoin","personal-finance","ai-trading"].index(pillar["id"])
        if pillar["id"] in ["stock-market","bitcoin","personal-finance","ai-trading"] else 0
    )
    fmt = FORMAT_TYPES[(day_of_year + article_index + _pillar_idx * 17) % len(FORMAT_TYPES)]

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

    sections          = SECTION_STRUCTURES[fmt]
    opening_instruction = FORMAT_INSTRUCTIONS[fmt]

    # Affiliate links block — country-aware, pillar-specific
    affiliate_block = get_affiliate_block(pillar['id'])

    # Recent titles block for AI article writer (avoid topic repetition)
    recent_titles_avoidance = ""
    if recent_titles:
        recent_titles_avoidance = (
            "\nRECENT ARTICLE TITLES TO AVOID REPEATING (do not cover the same specific angle):\n"
            + "\n".join(f"- {t}" for t in recent_titles[:7])
            + "\n"
        )

    # SEO seed block — long-tail high-CPC keyword guidance from content_calendar
    seo_seed_block = ""
    if _CALENDAR_AVAILABLE:
        try:
            calendar_seeds = get_article_seo_seeds(CONTENT_MODE)
            # Find the seed most relevant to this pillar
            pillar_seed = next(
                (s for s in calendar_seeds if s["primary_target"].lower() in
                 ["global", pillar["id"].split("-")[0]]),
                calendar_seeds[article_index % len(calendar_seeds)]
            )
            seo_seed_block = f"""
=== SEO KEYWORD STRATEGY (CRITICAL FOR GOOGLE RANKING) ===
DO NOT write about broad topics that Bloomberg and Reuters already dominate.
INSTEAD write about these SPECIFIC long-tail questions real people search:

Primary keyword seed: {pillar_seed['seo_seed']}
Long-tail keywords to naturally address in the article:
- {pillar_seed['long_tail'][0]}
- {pillar_seed['long_tail'][1] if len(pillar_seed['long_tail']) > 1 else pillar_seed['long_tail'][0]}

Primary audience for this article: {pillar_seed['primary_target']} readers
Affiliate/product context: {pillar_seed['affiliate_hint']}

KEYWORD RULES:
- Use the primary keyword seed in the first 100 words naturally
- Use at least one long-tail question as an H2 or FAQ question
- Every statistic and number must connect to a specific reader decision
- Specific beats generic always: "LIC Tech Term at ₹10,500/year" beats "term insurance is important"
- The person searching this has a specific problem — solve it with specific answers
"""
        except Exception as e:
            print(f"    [SEO-SEED] Skipped ({e})")
            seo_seed_block = ""

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

{affiliate_block}

{recent_titles_avoidance}

{seo_seed_block}

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

        meta_description = (
            f"{article_title} | {pillar['name']} — {date_display}. "
            f"Insights for US, UK, India and Brazil investors."
        )[:155]

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

        _primary_kw    = pillar['primary_keywords'][0]
        article_excerpt = (
            f"{article_title} — {pillar['name']} for {date_display}. "
            f"Insights on {_primary_kw} for US, UK, India and Brazil investors."
        )[:200]

        schema_json = generate_schema(article_title, meta_description, pillar, chosen_slug)

        safe_title   = (article_title
                        .replace('"', "'").replace('&', 'and').replace('<', '')
                        .replace('>', '').replace('₹', 'Rs.').replace('\n', ' ').strip())
        safe_excerpt = (article_excerpt
                        .replace('"', "'").replace('&', 'and').replace('<', '').replace('>', '').strip())
        safe_desc    = (meta_description
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
            f"day_of_year: {day_of_year}\n"
            "---\n\n"
        )

        schema_block = f'<script type="application/ld+json">\n{schema_json}\n</script>\n\n'

        if not os.path.exists(POSTS_DIR):
            os.makedirs(POSTS_DIR)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header + schema_block + content)

        article_url = f"{SITE_URL}/{pillar['permalink_base']}/{chosen_slug}/"
        print(f"  ✅ /{pillar['permalink_base']}/{chosen_slug}/")
        print(f"     {article_title[:80]}...")
        return True, article_url

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False, None


# ─── Main ─────────────────────────────────────────────────────────────────────
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
        print(f"  S&P 500  : {prices.get('S&P 500', {}).get('display', 'N/A')}")
        print(f"  NIFTY    : {prices.get('NIFTY 50', {}).get('display', 'N/A')}")
        print(f"  Bitcoin  : {prices.get('Bitcoin', {}).get('display', 'N/A')}")
        print(f"  Gold     : {prices.get('Gold', {}).get('display', 'N/A')}")
        print(f"  F&G      : {fear_greed}")
        print(f"  Trending : {', '.join(trends[:3])}")

    results       = []
    published_urls = []

    for i, pillar in enumerate(PILLARS):
        # Skip if already generated today for this pillar
        already_exists = False
        if os.path.exists(POSTS_DIR):
            pillar_today = [
                f for f in os.listdir(POSTS_DIR)
                if f.endswith('.md') and f.startswith(date_str) and pillar['id'] in f
            ]
            if pillar_today:
                print(f"\n  [{i+1}/4] Skipping {pillar['name']} — already generated today")
                already_exists = True

        if already_exists:
            results.append({"pillar": pillar['name'], "status": "skipped"})
            continue

        # Select persona — rotated by day_of_year + pillar offset
        persona_indices = PILLAR_PERSONA_MAP.get(pillar['id'], [0, 1, 2, 3])
        _pidx           = (day_of_year + i * 31) % len(persona_indices)
        persona         = PERSONAS[persona_indices[_pidx]]

        success, url = generate_article(pillar, prices, trends, fear_greed, persona, i + 1)
        results.append({
            "pillar":  pillar['name'],
            "status":  "success" if success else "failed",
            "url":     url or ""
        })
        if success and url:
            published_urls.append(url)
        time.sleep(2)

    # Google Indexing
    if published_urls:
        print(f"\n  Submitting {len(published_urls)} URLs to Google Indexing API...")
        submit_urls_to_google(published_urls)

    # Cleanup old posts
    cleanup_old_posts()

    # Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    success_count = sum(1 for r in results if r['status'] == 'success')
    skipped_count = sum(1 for r in results if r['status'] == 'skipped')
    failed_count  = sum(1 for r in results if r['status'] == 'failed')
    print(f"  ✅ Generated : {success_count}")
    print(f"  ⏭  Skipped   : {skipped_count}")
    print(f"  ❌ Failed    : {failed_count}")
    for r in results:
        icon = "✅" if r['status'] == 'success' else ("⏭" if r['status'] == 'skipped' else "❌")
        print(f"  {icon} {r['pillar']}")
        if r.get('url'):
            print(f"     {r['url']}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    generate_all_articles()
