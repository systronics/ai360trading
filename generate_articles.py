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
MAX_POSTS    = 15   # keep only latest 15 articles

# ─── Writing style rotated daily (no real person names) ──────────────────────
STYLES = [
    {
        "tone":  "confident and contrarian",
        "style": "direct, data-driven, uses trading floor language, references Indian market nuances"
    },
    {
        "tone":  "analytical and precise",
        "style": "measured, draws historical market parallels, references macro cycles"
    },
    {
        "tone":  "conversational and passionate",
        "style": "uses vivid metaphors, breaks down complex concepts simply, occasionally sarcastic about Fed policy"
    },
    {
        "tone":  "methodical and number-heavy",
        "style": "references volatility patterns, quant signals, drops jaw-dropping statistics"
    },
    {
        "tone":  "urgent and sharp",
        "style": "short punchy sentences, focuses on what traders must act on TODAY"
    },
    {
        "tone":  "calm and educational",
        "style": "explains WHY things are moving, great for retail investors new to macro"
    },
    {
        "tone":  "bold and opinionated",
        "style": "takes strong positions, backs them with data, challenges mainstream narrative"
    },
]
style = STYLES[now.weekday() % len(STYLES)]

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
                pub   = item.find('pubDate')
                date_text = pub.text[:16] if pub is not None else ""
                all_headlines.append(f"[{date_text}] {title}")
        except:
            continue
    random.shuffle(all_headlines)
    return "\n".join(all_headlines[:20]) if all_headlines else "Global markets in focus today."

# ─── 3. Live Market Prices via Yahoo Finance ──────────────────────────────────
def get_live_prices():
    symbols = {
        "NIFTY 50":      "^NSEI",
        "SENSEX":        "^BSESN",
        "S&P 500":       "^GSPC",
        "NASDAQ":        "^IXIC",
        "FTSE 100":      "^FTSE",
        "Nikkei 225":    "^N225",
        "Hang Seng":     "^HSI",
        "Gold":          "GC=F",
        "Crude Oil WTI": "CL=F",
        "Bitcoin":       "BTC-USD",
        "USD/INR":       "INR=X",
        "DXY (Dollar)":  "DX-Y.NYB",
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
            prices[name] = f"{current:,} {arrow} {abs(pct)}%"
        except:
            prices[name] = "N/A"
    return prices

# ─── 4. Fear & Greed Index ────────────────────────────────────────────────────
def get_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=6)
        d = r.json()['data'][0]
        return f"{d['value']} — {d['value_classification']}"
    except:
        return "Unavailable"

# ─── 5. Keep only latest MAX_POSTS articles ───────────────────────────────────
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

# ─── 6. Main Article Generator ───────────────────────────────────────────────
def generate_full_report():
    news       = get_live_news()
    trends     = get_google_trends()
    prices     = get_live_prices()
    fear_greed = get_fear_greed()

    price_lines = "\n".join([f"  - {k}: {v}" for k, v in prices.items()])

    slug_options = [
        "nifty-global-market-analysis",
        "market-intelligence-report",
        "global-macro-market-update",
        "stock-market-technical-analysis",
        "nifty-support-resistance-today",
        "indian-market-preopen-analysis",
        "global-macro-indian-stocks",
    ]
    chosen_slug = f"{date_str}-{random.choice(slug_options)}-{now.strftime('%H%M')}"
    file_path   = os.path.join(POSTS_DIR, f"{chosen_slug}.md")

    prompt = f"""
You are the AI360Trading Intelligence Desk — an institutional-grade market
analysis team based in India. Tone: {style['tone']}. Style: {style['style']}.

Today is {day_name}, {date_display}.
Write a COMPLETE, ORIGINAL 1,600-word Global Market Intelligence Report
for ai360trading.in — a premium Indian financial analysis platform.

ALL analysis must be 100% original. Do NOT copy, paraphrase, or closely
mirror any news headline. Use headlines ONLY as background context to
form your OWN independent views and analysis.

═══════════════════════════════════════
LIVE MARKET DATA — USE THESE EXACT NUMBERS IN YOUR ANALYSIS:
{price_lines}

Crypto Fear & Greed Index: {fear_greed}
═══════════════════════════════════════

TODAY'S NEWS CONTEXT (use for context only — write YOUR OWN analysis):
{news}

TOP GOOGLE TRENDS (weave naturally into narrative):
{', '.join(trends)}
═══════════════════════════════════════

WRITING RULES — FOLLOW STRICTLY:
1. Write like a HUMAN expert team — use "we believe", "our view is",
   "what concerns us today", "the real story here is",
   "here is what smart money is doing".
2. NEVER sound like AI. Vary sentence length dramatically.
   Mix short punchy lines. With longer analytical ones.
3. Use vivid metaphors — markets as weather, battles, living organisms.
4. Include at least ONE contrarian view challenging mainstream consensus.
5. Reference EXACT live prices with commentary on what they mean RIGHT NOW.
6. First sentence MUST contain "Global Market Intelligence Report" naturally.
7. Always include India-specific angle — NIFTY, SENSEX, RBI, FII/DII flows.
8. Use transitions: "Here's the thing...", "What nobody is talking about...",
   "Let us be blunt...", "Frankly speaking...", "The real story is..."
9. DO NOT copy or closely reword any headline. Write YOUR OWN analysis.
10. Author is always "AI360Trading Intelligence Desk" — never a real person's name.
11. NO image tags or image markdown anywhere in the article.

SEO RULES:
- First output line: META_DESCRIPTION: <exactly 150-155 characters summarizing today's key market move>
- Use trending keywords naturally — never stuffed.

HEADING STRUCTURE — NEVER SKIP LEVELS:
- NO H1 (page title already set as H1)
- ## for major sections (H2)
- ### for sub-sections within H2 only (H3)
- #### only within H3 (H4)
- NEVER jump from ## to ####

ARTICLE STRUCTURE:
1. META_DESCRIPTION: <150-155 char summary>

2. ## Market Snapshot — {date_display}
   First sentence MUST say "Global Market Intelligence Report".
   Narrative around live prices — what story do they tell TOGETHER today?

3. ## Incident of the Day
   Original deep-dive on the most market-moving event.
   Your own analysis — NOT a news summary. What does it really mean for traders?

4. ## NIFTY 50 & Indian Market Outlook
   ### FII/DII Sentiment & Flows
   ### Key Levels to Watch Today
   (Calculate S/R from live NIFTY price using standard pivot point formula)

5. ## Wall Street & Global Tech
   ### NASDAQ & AI Sector Momentum
   ### Earnings & Corporate Signals

6. ## European & Asian Markets
   ### FTSE 100 Analysis
   ### China, Japan & Emerging Markets

7. ## Commodities & Safe Havens
   ### Crude Oil Outlook
   ### Gold & Dollar Dynamics

8. ## Crypto Corner
   (Live Bitcoin price + Fear & Greed = {fear_greed} — what does this signal?)

9. ## What Smart Money Is Doing
   (Contrarian institutional take — what retail traders always miss)

10. ## Global Pivot Table
    ### Support & Resistance Levels
    | Instrument | Current Price | Support 1 | Support 2 | Resistance 1 | Resistance 2 |
    |------------|--------------|-----------|-----------|--------------|--------------|
    (Use ACTUAL live prices above. Calculate using standard pivot point formula.)

11. ## AI360Trading Desk Final View
    Bold 2-paragraph actionable opinion based on today's live data.
    End with exactly this line:
    *Trade smart. Stay informed. — AI360Trading Intelligence Desk*

12. ## 🌍 Trending Hashtags
    #GlobalMarketIntelligence #StockMarket #NIFTY50 #ai360trading
    {' '.join(['#' + t.replace(' ', '') for t in trends[:6]])}

---
*Published by AI360Trading Intelligence Desk | {date_display} | {now.strftime('%I:%M %p')} IST*
*Disclaimer: For educational and informational purposes only. Not financial advice. Trade at your own risk.*

END WITH THIS EXACT HTML — do not modify a single character:
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
                        "You are the AI360Trading Intelligence Desk — an institutional-grade "
                        "Indian market analysis team. "
                        f"Tone: {style['tone']}. Style: {style['style']}. "
                        "You write 100% original, human-sounding financial analysis. "
                        "You NEVER copy or paraphrase news sources — news is background context only. "
                        "You form your OWN independent views backed by the live price data provided. "
                        "You NEVER sound like AI. Vary sentence structure dramatically. "
                        "Heading hierarchy is sacred: H2 → H3 → H4 only, never skip levels. "
                        "Author is always 'AI360Trading Intelligence Desk'. "
                        "Never include image tags or image markdown in the article."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            max_tokens=4096,
        )
        content = completion.choices[0].message.content

        # Extract META_DESCRIPTION and strip from body
        meta_description = (
            f"{date_display} Global Market Intelligence Report — "
            "live NIFTY, NASDAQ, Gold & Crypto analysis with trading signals by AI360Trading."
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

        # Front matter — no image field
        header = (
            "---\n"
            "layout: post\n"
            f"title: \"{date_display} | Global Market Intelligence Report\"\n"
            f"date: {date_str}\n"
            "author: \"AI360Trading Intelligence Desk\"\n"
            f"permalink: /analysis/{chosen_slug}/\n"
            f"description: \"{meta_description}\"\n"
            f"keywords: \"global market intelligence report, nifty analysis today, "
            f"{', '.join(trends[:4]).lower()}\"\n"
            "categories: [Market-Intelligence]\n"
            "tags: [NIFTY, NASDAQ, Gold, Bitcoin, GlobalMacro, IndianMarket]\n"
            "---\n\n"
        )

        if not os.path.exists(POSTS_DIR):
            os.makedirs(POSTS_DIR)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header + content)

        print(f"✅ Report created : /analysis/{chosen_slug}/")
        print(f"   Author         : AI360Trading Intelligence Desk")
        print(f"   Meta           : {meta_description}")
        print(f"   NIFTY          : {prices.get('NIFTY 50', 'N/A')}")
        print(f"   Bitcoin        : {prices.get('Bitcoin', 'N/A')}")
        print(f"   Fear & Greed   : {fear_greed}")

        # Cleanup — remove posts beyond MAX_POSTS after successful generation
        cleanup_old_posts()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    generate_full_report()
