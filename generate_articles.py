import os
import pytz
import requests
import random
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from groq import Groq

# ─── Init ────────────────────────────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
ist       = pytz.timezone('Asia/Kolkata')
now       = datetime.now(ist)
date_str  = now.strftime("%Y-%m-%d")
date_display = now.strftime("%B %d, %Y")
day_name  = now.strftime("%A")
POSTS_DIR = os.path.join(os.getcwd(), '_posts')

# ─── Human writer personas (rotated daily so style never repeats) ─────────────
PERSONAS = [
    {
        "name": "Arjun Mehta",
        "title": "Senior Market Strategist, 14 years on Dalal Street",
        "style": "direct, data-driven, uses trading floor slang, references Indian market nuances",
        "tone": "confident and slightly contrarian"
    },
    {
        "name": "Priya Nair",
        "title": "Global Macro Analyst, ex-Goldman Sachs Mumbai desk",
        "style": "analytical, uses academic references, draws historical parallels",
        "tone": "measured, precise, occasionally alarmed by macro risks"
    },
    {
        "name": "Rohit Sharma",
        "title": "Derivatives Trader & Independent Researcher",
        "style": "conversational, uses vivid metaphors, breaks down complex concepts simply",
        "tone": "passionate, sometimes sarcastic about Fed policy, relatable"
    },
    {
        "name": "Kavita Iyer",
        "title": "Quantitative Analyst & Algorithmic Trading Specialist",
        "style": "precise, number-heavy, references quant models and volatility patterns",
        "tone": "cool, methodical, occasionally drops jaw-dropping statistics"
    },
]
persona = PERSONAS[now.weekday() % len(PERSONAS)]

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
            "Stock Market Pulse", "Fed Interest Rates", "Nvidia AI", "Global Macro",
            "Bitcoin ETF", "Oil Prices", "China Economy", "S&P 500", "Inflation CPI", "Gold Rally"
        ]

# ─── 2. Live News Headlines ───────────────────────────────────────────────────
def get_live_news():
    """Pull headlines across ALL major market themes for richer context."""
    all_headlines = []
    queries = [
        "NASDAQ+Nvidia+AI+tech+earnings+today",
        "Fed+interest+rate+inflation+CPI+2026",
        "China+stimulus+market+economy",
        "Crude+Oil+Gold+geopolitical",
        "Crypto+Bitcoin+ETF+regulation",
        "NIFTY+SENSEX+Indian+market+today",
        "European+market+FTSE+ECB",
    ]
    for query in queries:
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        try:
            r = requests.get(url, timeout=8)
            root = ET.fromstring(r.content)
            items = root.findall('.//item')
            for item in items[:3]:
                title = item.find('title').text
                pub_date = item.find('pubDate')
                date_text = pub_date.text[:16] if pub_date is not None else ""
                all_headlines.append(f"[{date_text}] {title}")
        except:
            continue
    random.shuffle(all_headlines)
    return "\n".join(all_headlines[:20]) if all_headlines else "Global markets in focus today."

# ─── 3. Live Market Prices via Yahoo Finance ──────────────────────────────────
def get_live_prices():
    """Fetch real-time prices for key instruments."""
    symbols = {
        "NIFTY 50":     "^NSEI",
        "SENSEX":       "^BSESN",
        "S&P 500":      "^GSPC",
        "NASDAQ":       "^IXIC",
        "FTSE 100":     "^FTSE",
        "Nikkei 225":   "^N225",
        "Hang Seng":    "^HSI",
        "Gold":         "GC=F",
        "Crude Oil WTI":"CL=F",
        "Bitcoin":      "BTC-USD",
        "USD/INR":      "INR=X",
        "DXY (Dollar)": "DX-Y.NYB",
    }
    prices = {}
    for name, symbol in symbols.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, timeout=8)
            data = r.json()
            result = data['chart']['result'][0]
            meta = result['meta']
            current = round(meta.get('regularMarketPrice', 0), 2)
            prev    = round(meta.get('chartPreviousClose', current), 2)
            change  = round(current - prev, 2)
            pct     = round((change / prev) * 100, 2) if prev else 0
            arrow   = "▲" if change >= 0 else "▼"
            prices[name] = f"{current:,} {arrow} {abs(pct)}%"
        except:
            prices[name] = "N/A"
    return prices

# ─── 4. Fear & Greed approximation via crypto + VIX ──────────────────────────
def get_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=6)
        d = r.json()['data'][0]
        return f"{d['value']} — {d['value_classification']}"
    except:
        return "Unavailable"

# ─── 5. Main Article Generator ───────────────────────────────────────────────
def generate_full_report():
    news   = get_live_news()
    trends = get_google_trends()
    prices = get_live_prices()
    fear_greed = get_fear_greed()

    # Build live price table string for the prompt
    price_lines = "\n".join([f"  - {k}: {v}" for k, v in prices.items()])

    # Unique slug with timestamp to prevent collision
    slug_options = [
        "nifty-global-market-analysis",
        "market-intelligence-report",
        "global-macro-market-update",
        "stock-market-technical-analysis",
        "nifty-support-resistance-today",
    ]
    chosen_slug = f"{date_str}-{random.choice(slug_options)}-{now.strftime('%H%M')}"
    file_path   = os.path.join(POSTS_DIR, f"{chosen_slug}.md")

    # Reliable daily image
    img_seed = int(now.strftime("%j")) + now.year  # same image per calendar day
    img_url  = f"https://picsum.photos/seed/{img_seed}/800/420"
    img_tag  = f"![Global Market Intelligence Report — {date_display}]({img_url})"

    # ── The Prompt ──────────────────────────────────────────────────────────
    prompt = f"""
You are {persona['name']}, {persona['title']}.
Your writing style: {persona['style']}.
Your tone: {persona['tone']}.

Today is {day_name}, {date_display}. Write a COMPLETE 1,600-word Global Market Intelligence Report
for ai360trading.in — a premium Indian financial analysis platform.

═══════════════════════════════════════
LIVE MARKET DATA RIGHT NOW (use these EXACT numbers in your analysis):
{price_lines}

Crypto Fear & Greed Index: {fear_greed}
═══════════════════════════════════════

TODAY'S BREAKING NEWS HEADLINES (analyze these, don't just list them):
{news}

TOP GOOGLE TRENDS (weave these into the narrative):
{', '.join(trends)}
═══════════════════════════════════════

WRITING RULES — READ CAREFULLY:
1. Write like a HUMAN expert analyst — use "I think", "in my view", "what concerns me", personal anecdotes from trading experience.
2. NEVER sound like AI. Vary sentence length. Use short punchy sentences AND longer analytical ones.
3. Use vivid metaphors: markets as weather, battles, living organisms.
4. Include at least ONE contrarian view that challenges mainstream consensus.
5. Reference the EXACT live prices above with your own commentary on what they mean.
6. First sentence MUST contain "Global Market Intelligence Report" naturally.
7. Include at least one India-specific angle (NIFTY/SENSEX/RBI/FII flows).
8. Use conversational transitions: "Here's the thing...", "What nobody is talking about...", "Let me be blunt...", "The real story is..."

SEO RULES:
- First line output: META_DESCRIPTION: <exactly 150-155 characters summarizing today's key market move>
- Use trending keywords naturally — not stuffed.
- Never repeat the same opening two articles in a row.

HEADING STRUCTURE (strictly follow — never skip levels):
- NO H1 (title is already set)
- ## for major sections (H2)
- ### for sub-sections within H2 only (H3)
- #### only within H3 (H4)

ARTICLE STRUCTURE:
1. META_DESCRIPTION: <150-155 char summary>
2. {img_tag}
3. Opening paragraph — hook the reader, mention "Global Market Intelligence Report", reference today's biggest price move from the live data.

## Market Snapshot: {date_display}
(Use the live prices — build a narrative around the numbers. What story do they tell together?)

## Incident of the Day
(The single most market-moving event from today's headlines — deep analysis, not just summary. What does it REALLY mean for traders?)

## NIFTY 50 & Indian Market Outlook
### FII/DII Activity & Sentiment
### Key Levels to Watch Today
(Derive support/resistance from NIFTY price above using standard pivot calculation)

## Wall Street & Global Tech
### NASDAQ & AI Sector Momentum
### Earnings & Corporate Signals

## European & Asian Market Pulse
### FTSE 100 Analysis
### China, Japan & Emerging Markets

## Commodities & Safe Havens
### Crude Oil Outlook
### Gold & Dollar Dynamics

## Crypto Corner
(Bitcoin price from live data, Fear & Greed = {fear_greed}, what it signals)

## What The Smart Money Is Doing
(Contrarian take — what institutional traders are doing that retail ignores)

## Global Pivot Table
### Support & Resistance Levels

| Instrument | Current Price | Support 1 | Support 2 | Resistance 1 | Resistance 2 |
|------------|--------------|-----------|-----------|--------------|--------------|
(Fill using actual prices from live data. Calculate S/R using standard pivot point formula)

## {persona['name']}'s Final Take
(Personal 2-paragraph opinion — bold, memorable, actionable. What should a trader DO based on today's analysis?)

## 🌍 Trending Market Hashtags
#GlobalMarketIntelligence #StockMarket #NIFTY50 #Trading {' '.join(['#' + t.replace(' ','') for t in trends[:6]])}

---
*Analysis by {persona['name']}, {persona['title']}. Published {date_display} at {now.strftime('%I:%M %p')} IST.*
*Disclaimer: This report is for educational purposes only and does not constitute financial advice.*

END WITH THIS EXACT HTML (do not modify):
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
                        f"You are {persona['name']}, {persona['title']}. "
                        f"Style: {persona['style']}. Tone: {persona['tone']}. "
                        "You write human, opinionated, data-rich financial analysis. "
                        "You NEVER sound like AI. You vary sentence structure dramatically. "
                        "You have strong views and defend them with real data. "
                        "You follow heading hierarchy strictly: H2 → H3 → H4 only. "
                        "You NEVER skip heading levels."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            max_tokens=4096,
        )
        content = completion.choices[0].message.content

        # Extract and remove META_DESCRIPTION from body
        meta_description = (
            f"{date_display} Global Market Intelligence Report — "
            "NIFTY, NASDAQ, Gold & Crypto analysis with live prices and trading signals."
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

        # Build front matter
        header = (
            "---\n"
            "layout: post\n"
            f"title: \"{date_display} | Global Market Intelligence Report\"\n"
            f"date: {date_str}\n"
            f"author: \"{persona['name']}\"\n"
            f"author_title: \"{persona['title']}\"\n"
            f"permalink: /analysis/{chosen_slug}/\n"
            f"description: \"{meta_description}\"\n"
            f"image: {img_url}\n"
            f"keywords: \"global market intelligence report, nifty analysis, {', '.join(trends[:4]).lower()}\"\n"
            "categories: [Market-Intelligence]\n"
            "tags: [NIFTY, NASDAQ, Gold, Bitcoin, GlobalMacro]\n"
            "---\n\n"
        )

        if not os.path.exists(POSTS_DIR):
            os.makedirs(POSTS_DIR)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header + content)

        print(f"✅ Report created: /analysis/{chosen_slug}/")
        print(f"   Author  : {persona['name']} ({persona['title']})")
        print(f"   Meta    : {meta_description}")
        print(f"   Prices  : NIFTY={prices.get('NIFTY 50','N/A')}  BTC={prices.get('Bitcoin','N/A')}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    generate_full_report()
