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
MAX_POSTS    = 30   # increased to keep more history for SEO

# ─── Writing Personas (rotated daily) ────────────────────────────────────────
# Each persona has distinct vocabulary, sentence patterns, and analytical focus
PERSONAS = [
    {
        "name": "Senior Derivatives Trader",
        "tone": "confident and contrarian",
        "style": "uses F&O terminology naturally, references open interest and PCR ratios, "
                 "draws parallels between today's price action and specific historical dates, "
                 "occasionally uses Hindi trading phrases like 'bazaar' and 'bhav'",
        "opening_hook": "leads with the most surprising data point of the day",
        "signature_phrase": "The options market never lies.",
    },
    {
        "name": "Macro Economist",
        "tone": "analytical and precise",
        "style": "references specific RBI policy decisions, bond yield spreads, "
                 "current account deficit implications, uses economic jargon naturally, "
                 "draws macro cycles from 2008, 2013, 2020 corrections",
        "opening_hook": "starts with a macro paradox or contradiction in today's data",
        "signature_phrase": "The macro picture tells a different story than the headlines.",
    },
    {
        "name": "Quantitative Analyst",
        "tone": "methodical and number-heavy",
        "style": "references standard deviation moves, beta correlations, "
                 "volatility clustering, specific technical indicator readings like RSI and MACD, "
                 "uses precise percentage calculations, cites statistical anomalies",
        "opening_hook": "opens with a striking statistical fact about today's market move",
        "signature_phrase": "The numbers are telling us something the narrative is missing.",
    },
    {
        "name": "Veteran Market Commentator",
        "tone": "conversational and passionate",
        "style": "uses vivid metaphors comparing markets to cricket matches and monsoons, "
                 "explains complex concepts with everyday Indian analogies, "
                 "occasionally sarcastic about SEBI or Fed policy, "
                 "writes like speaking to a friend over chai",
        "opening_hook": "opens with a relatable real-world analogy for today's market",
        "signature_phrase": "This market is teaching us a lesson we should have already known.",
    },
    {
        "name": "Institutional Flow Analyst",
        "tone": "sharp and urgent",
        "style": "focuses on FII/DII data, block deals, bulk trades, "
                 "short punchy sentences mixed with detailed flow analysis, "
                 "references specific sector rotations and institutional positioning, "
                 "always asks what the smart money is actually doing vs what it is saying",
        "opening_hook": "opens with a specific institutional flow anomaly spotted today",
        "signature_phrase": "Follow the money, not the noise.",
    },
    {
        "name": "Global Macro Strategist",
        "tone": "calm and educational",
        "style": "connects global dots — explains how US Treasury moves affect Indian IT stocks, "
                 "how China PMI impacts commodity prices and Indian metals, "
                 "patient explanations suitable for serious retail investors, "
                 "references specific global economic data releases and their market impact",
        "opening_hook": "opens by connecting an unexpected global event to Indian markets",
        "signature_phrase": "In a connected world, no market is an island.",
    },
    {
        "name": "Technical Price Action Specialist",
        "tone": "bold and opinionated",
        "style": "references candlestick patterns by name, Fibonacci levels, "
                 "volume profile analysis, market structure concepts like HH/HL/LH/LL, "
                 "takes strong directional views with specific entry/exit logic, "
                 "challenges consensus with price action evidence",
        "opening_hook": "opens with a specific chart pattern forming right now",
        "signature_phrase": "Price is the only truth in this market.",
    },
]
persona = PERSONAS[now.weekday() % len(PERSONAS)]

# ─── Varied Article Structures (rotated) ─────────────────────────────────────
ARTICLE_STRUCTURES = [
    "standard",      # Normal top-down global → India flow
    "india_first",   # Lead with India, then global context
    "theme_driven",  # One dominant theme weaves through entire piece
    "contrarian",    # Challenge the mainstream narrative throughout
]
structure = ARTICLE_STRUCTURES[now.day % len(ARTICLE_STRUCTURES)]

# ─── 1. Google Trends ─────────────────────────────────────────────────────────
def get_google_trends():
    url = "https://trends.google.com/trends/api/dailytrends?hl=en-US&tz=-330&geo=US"
    try:
        r = requests.get(url, timeout=10)
        clean_json = r.text.replace(")]}',\n", "")
        data = json.loads(clean_json)
        trends = []
        for day in data['default']['trendingSearchesDays']:
            for item in day['trendingSearches']:
                trends.append(item['title']['query'])
        return trends[:10]
    except:
        return [
            "Stock Market Today", "NIFTY Analysis", "Fed Interest Rates",
            "Nvidia AI Earnings", "Global Macro", "Bitcoin Price",
            "Oil Prices Today", "Gold Rally", "China Economy", "S&P 500 Forecast"
        ]

# ─── 2. Live News Headlines ───────────────────────────────────────────────────
def get_live_news():
    all_headlines = []
    queries = [
        "NASDAQ+Nvidia+AI+tech+earnings+today",
        "Fed+interest+rate+inflation+CPI+2026",
        "China+stimulus+market+economy",
        "Crude+Oil+Gold+geopolitical+supply",
        "Crypto+Bitcoin+ETF+regulation",
        "NIFTY+SENSEX+FII+Indian+market+today",
        "European+market+FTSE+ECB+rate",
        "RBI+India+monetary+policy+rupee",
    ]
    for query in queries:
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        try:
            r = requests.get(url, timeout=8)
            root = ET.fromstring(r.content)
            items = root.findall('.//item')
            for item in items[:2]:
                title = item.find('title').text
                pub   = item.find('pubDate')
                date_text = pub.text[:16] if pub is not None else ""
                all_headlines.append(f"[{date_text}] {title}")
        except:
            continue
    random.shuffle(all_headlines)
    return "\n".join(all_headlines[:18]) if all_headlines else "Global markets active today."

# ─── 3. Live Market Prices via Yahoo Finance ──────────────────────────────────
def get_live_prices():
    symbols = {
        "NIFTY 50":        "^NSEI",
        "SENSEX":          "^BSESN",
        "Bank Nifty":      "^NSEBANK",
        "S&P 500":         "^GSPC",
        "NASDAQ":          "^IXIC",
        "Dow Jones":       "^DJI",
        "FTSE 100":        "^FTSE",
        "Nikkei 225":      "^N225",
        "Hang Seng":       "^HSI",
        "Gold":            "GC=F",
        "Silver":          "SI=F",
        "Crude Oil WTI":   "CL=F",
        "Natural Gas":     "NG=F",
        "Bitcoin":         "BTC-USD",
        "Ethereum":        "ETH-USD",
        "USD/INR":         "INR=X",
        "DXY (Dollar)":    "DX-Y.NYB",
        "US 10Y Yield":    "^TNX",
        "India VIX":       "^INDIAVIX",
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
                "price": current,
                "change": change,
                "pct": pct,
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

# ─── 5. Calculate Pivot Points ───────────────────────────────────────────────
def calculate_pivots(high, low, close):
    """Standard floor pivot point calculation"""
    pivot = round((high + low + close) / 3, 2)
    s1 = round((2 * pivot) - high, 2)
    s2 = round(pivot - (high - low), 2)
    r1 = round((2 * pivot) - low, 2)
    r2 = round(pivot + (high - low), 2)
    return {"pivot": pivot, "s1": s1, "s2": s2, "r1": r1, "r2": r2}

# ─── 6. Keep only latest MAX_POSTS articles ───────────────────────────────────
def cleanup_old_posts():
    try:
        files = sorted([
            f for f in os.listdir(POSTS_DIR)
            if f.endswith('.md')
        ])
        if len(files) > MAX_POSTS:
            to_delete = files[:len(files) - MAX_POSTS]
            for fname in to_delete:
                os.remove(os.path.join(POSTS_DIR, fname))
                print(f"🗑️  Removed old post: {fname}")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

# ─── 7. Main Article Generator ───────────────────────────────────────────────
def generate_full_report():
    news       = get_live_news()
    trends     = get_google_trends()
    prices     = get_live_prices()
    fear_greed = get_fear_greed()

    # Format prices for prompt
    price_lines = "\n".join([
        f"  - {k}: {v['display']}" for k, v in prices.items()
    ])

    # Get specific prices for pivot calculations
    nifty_price  = prices.get("NIFTY 50", {}).get("price", 24000)
    nifty_change = prices.get("NIFTY 50", {}).get("pct", 0)
    btc_price    = prices.get("Bitcoin", {}).get("price", 65000)
    gold_price   = prices.get("Gold", {}).get("price", 5200)

    # Varied slug options for URL diversity
    slug_options = [
        f"nifty-market-analysis-{date_str}",
        f"global-market-report-{date_str}",
        f"market-intelligence-{date_str}",
        f"indian-market-outlook-{date_str}",
        f"global-macro-update-{date_str}",
        f"nifty-technical-levels-{date_str}",
        f"stock-market-today-{date_str}",
    ]
    chosen_slug = random.choice(slug_options)
    file_path   = os.path.join(POSTS_DIR, f"{chosen_slug}.md")

    # Structure-specific instructions
    structure_instructions = {
        "standard": "Start with global picture, then zoom into India. Natural top-down macro flow.",
        "india_first": "Open with NIFTY and Indian market analysis first. Then explain global context driving it.",
        "theme_driven": f"Choose ONE dominant theme from today's data and weave it through the ENTIRE article. Every section connects back to this central theme.",
        "contrarian": "Challenge the mainstream market narrative. What is everyone getting wrong today? Back every contrarian view with specific data from the live prices provided.",
    }

    prompt = f"""
You are the AI360Trading Intelligence Desk — specifically writing today as a {persona['name']}.
Tone: {persona['tone']}. Style: {persona['style']}.
Opening approach: {persona['opening_hook']}.

Today is {day_name}, {date_display}.
Article structure approach: {structure_instructions[structure]}

Write a COMPLETE, ORIGINAL 1,800-word Global Market Intelligence Report
for ai360trading.in — a premium Indian financial analysis platform.

CRITICAL: This article must pass Google's Helpful Content System check.
It must contain UNIQUE INSIGHT that cannot be found by simply reading
the news headlines. Every section must add genuine analytical value.

ALL analysis must be 100% original. Use headlines ONLY as background
context. Form your OWN independent views backed by the live price data.

═══════════════════════════════════════
LIVE MARKET DATA — USE THESE EXACT NUMBERS:
{price_lines}

Crypto Fear & Greed Index: {fear_greed}
NIFTY current price: {nifty_price} ({'+' if nifty_change >= 0 else ''}{nifty_change}%)
Bitcoin current price: {btc_price}
Gold current price: {gold_price}
═══════════════════════════════════════

TODAY'S NEWS CONTEXT (background only — write YOUR OWN analysis):
{news}

TOP TRENDING SEARCHES (weave naturally — not forcefully):
{', '.join(trends)}
═══════════════════════════════════════

HUMAN WRITING RULES — CRITICAL:
1. VARY sentence length dramatically throughout.
   Mix: "Gold is surging." With longer analytical sentences that draw
   connections between multiple data points and explain the deeper
   market mechanism driving the move.
2. Use the {persona['name']} voice consistently. Think like this person.
3. Include at least ONE specific historical market parallel with exact date.
   Example: "This reminds us of the March 2020 situation when..."
4. Reference at least TWO specific India-only insights not in global news.
5. Use ONE specific technical indicator reading with its current value.
6. Include ONE specific sector within NIFTY outperforming or underperforming.
7. The contrarian view must be specific and data-backed, not vague.
8. NEVER use these AI giveaway phrases:
   - "In conclusion", "It is worth noting", "It is important to",
   - "This underscores", "This highlights", "Navigating", "Landscape",
   - "Delve into", "In today's fast-paced", "In the realm of"
9. DO use these natural analyst phrases sparingly:
   - "Here is what the data is actually telling us"
   - "What the market is pricing in right now"
   - "The number that has our attention today"
   - "Traders would do well to watch"
10. End sections with a forward-looking statement, not a summary.

GOOGLE HELPFUL CONTENT REQUIREMENTS:
- Every section must answer a question a trader would genuinely ask
- Include specific actionable information (key levels, what to watch)
- Original analysis beyond what news articles say
- Demonstrate expertise through specific, accurate market knowledge
- No filler paragraphs — every paragraph must earn its place

SEO RULES:
- First output line: META_DESCRIPTION: <exactly 150-155 characters>
- Primary keyword: naturally in first paragraph and 2-3 subheadings
- LSI keywords from trends woven naturally throughout
- No keyword stuffing anywhere

HEADING STRUCTURE — STRICT:
- NO H1 (page title is H1)
- ## for major sections (H2) only
- ### for sub-sections (H3) only within H2
- NEVER skip heading levels
- NO bold text as substitute for headings

ARTICLE STRUCTURE:
1. META_DESCRIPTION: <150-155 char summary with primary keyword>

2. ## Market Snapshot — {date_display}
   - Open with persona's {persona['opening_hook']}
   - Weave ALL live price data into a narrative — what story do they
     tell TOGETHER? Not just a list.
   - Include India VIX reading and what it signals

3. ## The Story Driving Markets Today
   - Your OWN deep analysis of the dominant market theme
   - Historical parallel with specific date
   - What this means specifically for Indian traders

4. ## NIFTY 50 & Indian Market Analysis
   ### FII and DII Activity Today
   - Specific flow analysis and what it signals medium-term
   ### Sector Performance Spotlight
   - ONE sector showing unusual strength or weakness, explain why
   ### Key Price Levels for NIFTY
   - Calculate S1, S2, R1, R2 from {nifty_price} using pivot formula
   - What happens at each level — specific scenario analysis

5. ## Wall Street and Global Technology
   ### NASDAQ Momentum and AI Valuations
   ### What Earnings Season Is Really Telling Us

6. ## European and Asian Market Signals
   ### FTSE 100 and European Divergence
   ### China, Japan and Emerging Market Flows

7. ## Commodities — Oil, Gold and the Dollar
   ### Crude Oil Supply and Demand Picture
   ### Gold at {gold_price} — Safe Haven or Something More?
   - Dollar Index {prices.get('DXY (Dollar)', {}).get('display', 'N/A')} implications

8. ## Crypto Market Pulse
   - Bitcoin at {btc_price} with Fear & Greed at {fear_greed}
   - Ethereum and altcoin market structure
   - What this sentiment reading has historically preceded

9. ## The Contrarian View — What the Crowd Is Missing
   - ONE specific data point that contradicts today's mainstream narrative
   - Back it with at least two pieces of evidence from the live data
   - Specific implication for Indian traders

10. ## Global Support and Resistance Levels
    ### Pivot Point Analysis
    | Instrument | Price | S2 | S1 | Pivot | R1 | R2 |
    |------------|-------|----|----|-------|----|----|
    (Calculate using ACTUAL live prices. Show your work in the pivot formula.)

11. ## AI360Trading Intelligence Desk — Final View
    - Bold 2-paragraph directional view
    - Specific levels to watch in next 48 hours
    - End with: *Trade smart. Stay informed. — AI360Trading Intelligence Desk*

12. ## Trending Market Topics Today
    {' '.join(['#' + t.replace(' ', '') for t in trends[:8]])}
    #GlobalMarketIntelligence #NIFTY50 #ai360trading #IndianStockMarket

---
*Published: {date_display} | {now.strftime('%I:%M %p')} IST | AI360Trading Intelligence Desk*
*⚠️ Educational content only. Not financial advice. Please read our [Legal Disclaimer](/disclaimer/) before trading.*

END WITH THIS EXACT HTML:
<h3>📢 Share this Analysis</h3>
<div class="share-bar">
  <a href="https://wa.me/?text={{{{ page.title }}}} - {{{{ site.url }}}}{{{{ page.url }}}}" class="share-btn btn-whatsapp">WhatsApp</a>
  <a href="https://twitter.com/intent/tweet?text={{{{ page.title }}}}&url={{{{ site.url }}}}{{{{ page.url }}}}" class="share-btn btn-twitter">Twitter</a>
  <a href="https://t.me/share/url?url={{{{ site.url }}}}{{{{ page.url }}}}&text={{{{ page.title }}}}" class="share-btn btn-telegram">Telegram</a>
</div>

<div class="sub-box">
  <h3>🚀 Global Trade Signals</h3>
  <p>Join our international community for real-time macro alerts.</p>
  <a href="https://t.me/{{{{ site.telegram_username }}}}">Join Telegram Now</a>
</div>
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are the AI360Trading Intelligence Desk, writing today as a {persona['name']}. "
                        f"Tone: {persona['tone']}. Style: {persona['style']}. "
                        f"Signature analytical approach: {persona['signature_phrase']} "
                        "You write 100% original, human-sounding financial analysis that passes "
                        "Google's Helpful Content System. "
                        "You NEVER copy or paraphrase news sources. News is background context only. "
                        "You form INDEPENDENT views backed by live price data. "
                        "You write like a real human expert — varied sentence length, specific data, "
                        "genuine insight that readers cannot find elsewhere. "
                        "Heading hierarchy is sacred: H2 → H3 only, never skip or reverse levels. "
                        "Never use AI giveaway phrases. Never include image tags. "
                        "Every paragraph must earn its place with genuine analytical value."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.88,
            max_tokens=4500,
            top_p=0.95,
            frequency_penalty=0.3,   # reduces repetitive phrases
            presence_penalty=0.2,    # encourages topic diversity
        )
        content = completion.choices[0].message.content

        # Extract and validate META_DESCRIPTION
        meta_description = (
            f"{date_display} Global Market Intelligence Report — "
            "NIFTY, NASDAQ, Gold and Crypto analysis with key levels by AI360Trading."
        )
        cleaned_lines = []
        for line in content.split("\n"):
            if line.strip().startswith("META_DESCRIPTION:"):
                extracted = line.replace("META_DESCRIPTION:", "").strip().strip('"')
                if 100 < len(extracted) <= 160:
                    meta_description = extracted
            else:
                cleaned_lines.append(line)
        content = "\n".join(cleaned_lines).lstrip("\n")

        # Build front matter with rich SEO data
        nifty_display = prices.get("NIFTY 50", {}).get("display", "N/A")
        btc_display   = prices.get("Bitcoin", {}).get("display", "N/A")

        header = (
            "---\n"
            "layout: post\n"
            f"title: \"{date_display} | Global Market Intelligence Report\"\n"
            f"date: {date_str}\n"
            "author: \"AI360Trading Intelligence Desk\"\n"
            f"permalink: /analysis/{chosen_slug}/\n"
            f"description: \"{meta_description}\"\n"
            f"keywords: \"global market intelligence report, nifty analysis {date_str}, "
            f"indian stock market today, {', '.join(trends[:3]).lower()}\"\n"
            "categories: [Market-Intelligence]\n"
            "tags: [NIFTY, NASDAQ, Gold, Bitcoin, GlobalMacro, IndianMarket, TechnicalAnalysis]\n"
            f"nifty_level: \"{nifty_display}\"\n"
            f"bitcoin_level: \"{btc_display}\"\n"
            f"fear_greed: \"{fear_greed}\"\n"
            "---\n\n"
        )

        if not os.path.exists(POSTS_DIR):
            os.makedirs(POSTS_DIR)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header + content)

        print(f"✅ Report created  : /analysis/{chosen_slug}/")
        print(f"   Persona         : {persona['name']}")
        print(f"   Structure       : {structure}")
        print(f"   Meta desc       : {meta_description}")
        print(f"   NIFTY           : {nifty_display}")
        print(f"   Bitcoin         : {btc_display}")
        print(f"   Fear & Greed    : {fear_greed}")

        cleanup_old_posts()

    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    generate_full_report()
