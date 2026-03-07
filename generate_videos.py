"""
AI360Trading — YouTube Video Automation Bot
============================================
Runs daily via GitHub Actions at 7:30 AM IST (30 min after articles)
Generates educational stock market videos and uploads to YouTube
automatically — zero manual work.

VIDEO TYPES (rotates daily):
Day 1 — NIFTY Support & Resistance Chart Video
Day 2 — Bitcoin Price Analysis Chart Video
Day 3 — Stock Market Education (Candlestick patterns)
Day 4 — Personal Finance Tips (SIP/401k)
Day 5 — AI Trading Signals Overview
Day 6 — Weekly Market Outlook
Day 0 (Sun) — Top 5 Stocks of the Week

STACK (all free):
- groq          → generate script from live data
- gTTS          → text to speech (Google, free, natural voice)
- matplotlib    → generate charts and graphs
- moviepy       → combine frames + audio into MP4
- google-api-python-client → upload to YouTube
- requests      → fetch live prices
"""

import os
import sys
import json
import time
import math
import random
import textwrap
import requests
import pytz
from datetime import datetime, timedelta
from groq import Groq

# ── Try importing video/audio libraries ──────────────────────────────────────
try:
    from gtts import gTTS
    from moviepy.editor import (
        ImageClip, AudioFileClip, concatenate_videoclips,
        CompositeVideoClip, TextClip, ColorClip
    )
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    LIBS_OK = True
except ImportError as e:
    print(f"Missing library: {e}")
    print("Run: pip install gtts moviepy matplotlib numpy pillow")
    LIBS_OK = False

# ── Try importing YouTube upload library ─────────────────────────────────────
try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    YOUTUBE_OK = True
except ImportError:
    YOUTUBE_OK = False
    print("YouTube upload disabled. Run: pip install google-api-python-client")

# ─── Configuration ────────────────────────────────────────────────────────────
ist          = pytz.timezone('Asia/Kolkata')
now          = datetime.now(ist)
date_str     = now.strftime("%Y-%m-%d")
date_display = now.strftime("%B %d, %Y")
day_name     = now.strftime("%A")
weekday      = now.weekday()  # 0=Mon, 6=Sun

client       = Groq(api_key=os.environ.get("GROQ_API_KEY"))
OUTPUT_DIR   = "/tmp/ai360_video"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Video dimensions — YouTube standard
W, H = 1280, 720

# Brand colors
BRAND_BLUE   = "#0062ff"
BRAND_GREEN  = "#2ecc71"
BRAND_DARK   = "#0f172a"
BRAND_LIGHT  = "#f8fafc"
BRAND_ORANGE = "#f7931a"
BRAND_PURPLE = "#8b5cf6"

# ─── 1. Fetch Live Market Data ────────────────────────────────────────────────
def get_live_prices():
    instruments = {
        "NIFTY 50":  "^NSEI",
        "S&P 500":   "^GSPC",
        "Bitcoin":   "BTC-USD",
        "Gold":      "GC=F",
        "NASDAQ":    "^IXIC",
        "Ethereum":  "ETH-USD",
        "Bank Nifty":"^NSEBANK",
    }
    prices = {}
    headers = {"User-Agent": "Mozilla/5.0"}
    for name, sym in instruments.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d"
            r = requests.get(url, headers=headers, timeout=10)
            d = r.json()
            meta  = d["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice", 0)
            prev  = meta.get("chartPreviousClose", price)
            pct   = ((price - prev) / prev * 100) if prev else 0
            prices[name] = {
                "price":   price,
                "prev":    prev,
                "pct":     round(pct, 2),
                "display": f"{price:,.2f} ({'+' if pct>=0 else ''}{pct:.2f}%)"
            }
        except:
            prices[name] = {"price": 0, "prev": 0, "pct": 0, "display": "N/A"}
        time.sleep(0.3)
    return prices

def get_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=8)
        d = r.json()
        val   = int(d["data"][0]["value"])
        label = d["data"][0]["value_classification"]
        return val, label
    except:
        return 50, "Neutral"

# ─── 2. Generate Script via GROQ ─────────────────────────────────────────────
VIDEO_TOPICS = {
    0: {  # Monday
        "type": "nifty_analysis",
        "title_template": "NIFTY Support & Resistance Today — {date} | Key Levels for Indian Traders",
        "duration_target": 180,  # 3 minutes
        "color": BRAND_BLUE,
        "tags": ["nifty today", "nifty support resistance", "nifty analysis", "stock market India", "trading levels today"],
        "description_template": "NIFTY 50 support and resistance levels for {date}. Key price levels, trend direction, and what to watch today. Daily market analysis by AI360Trading.\n\n🔔 Subscribe for daily NIFTY analysis\n📊 Full reports: https://ai360trading.in/topics/stock-market/\n📣 Telegram: https://t.me/ai360trading\n\n#NIFTY #StockMarket #TradingToday #NiftyLevels #AI360Trading"
    },
    1: {  # Tuesday
        "type": "bitcoin_analysis",
        "title_template": "Bitcoin Price Analysis {date} — BTC Levels, Trend & What's Next",
        "duration_target": 180,
        "color": BRAND_ORANGE,
        "tags": ["bitcoin today", "bitcoin price analysis", "BTC price", "crypto today", "bitcoin 2026"],
        "description_template": "Bitcoin price analysis for {date}. Key BTC support/resistance, Fear & Greed index reading, and what to expect next. Daily crypto analysis by AI360Trading.\n\n🔔 Subscribe for daily crypto analysis\n₿ Full reports: https://ai360trading.in/topics/bitcoin/\n📣 Telegram: https://t.me/ai360trading\n\n#Bitcoin #BTC #CryptoToday #BitcoinPrice #AI360Trading"
    },
    2: {  # Wednesday
        "type": "education_candlestick",
        "title_template": "Candlestick Patterns Every Trader Must Know — Stock Market Education",
        "duration_target": 300,  # 5 minutes
        "color": BRAND_GREEN,
        "tags": ["candlestick patterns", "stock market education", "trading basics", "technical analysis", "how to trade"],
        "description_template": "Learn the most important candlestick patterns used by professional traders. Visual explanation with real examples from NIFTY and S&P 500 charts.\n\n🔔 Subscribe for daily trading education\n📚 More guides: https://ai360trading.in/topics/ai-trading/\n📣 Telegram: https://t.me/ai360trading\n\n#CandlestickPatterns #TechnicalAnalysis #StockMarket #TradingEducation #AI360Trading"
    },
    3: {  # Thursday
        "type": "personal_finance",
        "title_template": "SIP vs Lump Sum — Which Is Better in {year}? Personal Finance Guide",
        "duration_target": 240,
        "color": BRAND_GREEN,
        "tags": ["SIP investment", "mutual funds India", "personal finance", "SIP vs lump sum", "invest in India"],
        "description_template": "SIP vs Lump Sum investment — which gives better returns in {year}? Complete guide for Indian investors with real numbers and examples.\n\n🔔 Subscribe for personal finance tips\n💰 More guides: https://ai360trading.in/topics/personal-finance/\n📣 Telegram: https://t.me/ai360trading\n\n#SIP #MutualFunds #PersonalFinance #Investment #AI360Trading"
    },
    4: {  # Friday
        "type": "weekly_outlook",
        "title_template": "Weekly Market Outlook — NIFTY & Global Markets | Week of {date}",
        "duration_target": 240,
        "color": BRAND_BLUE,
        "tags": ["weekly market outlook", "nifty next week", "stock market this week", "market prediction", "trading week ahead"],
        "description_template": "Weekly market outlook for the week of {date}. NIFTY, S&P 500, Bitcoin — key levels and what to watch this week.\n\n🔔 Subscribe for weekly market analysis\n📊 Full reports: https://ai360trading.in\n📣 Telegram: https://t.me/ai360trading\n\n#WeeklyOutlook #StockMarket #NIFTY #Trading #AI360Trading"
    },
    5: {  # Saturday
        "type": "education_patterns",
        "title_template": "Support & Resistance Explained — How Pro Traders Use These Levels",
        "duration_target": 300,
        "color": BRAND_PURPLE,
        "tags": ["support resistance", "technical analysis", "trading education", "price action", "how to trade stocks"],
        "description_template": "Support and resistance levels explained simply. How professional traders identify and trade these key price levels on NIFTY, S&P 500 and stocks.\n\n🔔 Subscribe for trading education\n🤖 More: https://ai360trading.in/topics/ai-trading/\n📣 Telegram: https://t.me/ai360trading\n\n#SupportResistance #TechnicalAnalysis #TradingEducation #PriceAction #AI360Trading"
    },
    6: {  # Sunday
        "type": "top5_stocks",
        "title_template": "Top 5 Stocks to Watch This Week — {date} | AI360Trading Picks",
        "duration_target": 240,
        "color": BRAND_BLUE,
        "tags": ["stocks to buy", "top stocks this week", "nifty stocks", "best stocks India", "stock picks 2026"],
        "description_template": "Top 5 stocks to watch this week — {date}. Institutional setups, volume breakouts, and key levels to monitor.\n\n🔔 Subscribe for weekly stock picks\n📊 Full analysis: https://ai360trading.in/topics/stock-market/\n📣 Telegram: https://t.me/ai360trading\n\n#StockPicks #TopStocks #NIFTY #StockMarket #AI360Trading"
    },
}

def generate_video_script(topic, prices, fg_val, fg_label):
    nifty   = prices.get("NIFTY 50", {})
    sp500   = prices.get("S&P 500", {})
    btc     = prices.get("Bitcoin", {})
    bnifty  = prices.get("Bank Nifty", {})

    topic_type = topic["type"]

    if topic_type == "nifty_analysis":
        focus = f"""
You are Amit Kumar from AI360Trading — a professional Indian market analyst.
Create a 3-minute video SCRIPT analyzing NIFTY 50 for today.

LIVE DATA:
- NIFTY 50: {nifty.get('display','N/A')}
- Bank Nifty: {bnifty.get('display','N/A')}
- S&P 500: {sp500.get('display','N/A')} (global cue)
- Fear & Greed: {fg_val} — {fg_label}

SCRIPT MUST INCLUDE (in order):
1. HOOK (15 sec) — one powerful opening line about today's market
2. GLOBAL PICTURE (30 sec) — how S&P 500 is affecting NIFTY
3. NIFTY LEVELS (60 sec) — exact support and resistance levels with reasoning
4. BANK NIFTY (30 sec) — key levels
5. WHAT TO DO (30 sec) — buy zone, avoid zone, what triggers to watch
6. CALL TO ACTION (15 sec) — subscribe, Telegram, website

Format: Write NARRATOR: before each spoken line.
Write SLIDE: before each visual description (what appears on screen).
Keep language simple — Indian retail traders are watching.
Total spoken words: 350-400 words maximum.
"""
    elif topic_type == "bitcoin_analysis":
        focus = f"""
You are Amit Kumar from AI360Trading — crypto market analyst.
Create a 3-minute video SCRIPT analyzing Bitcoin for today.

LIVE DATA:
- Bitcoin: {btc.get('display','N/A')}
- Fear & Greed: {fg_val} — {fg_label}
- S&P 500: {sp500.get('display','N/A')} (risk-on/off signal)

SCRIPT MUST INCLUDE:
1. HOOK (15 sec) — Bitcoin price right now and what it means
2. FEAR & GREED (30 sec) — explain the index reading and what it signals
3. KEY LEVELS (60 sec) — exact BTC support and resistance
4. ALTCOIN SIGNAL (30 sec) — is money rotating into alts?
5. TRADE SETUP (30 sec) — what to watch, entry triggers
6. CALL TO ACTION (15 sec) — subscribe, Telegram, website

Format: NARRATOR: for spoken lines. SLIDE: for visuals.
Total spoken words: 350-400 words maximum.
"""
    elif topic_type == "education_candlestick":
        focus = """
You are Amit Kumar from AI360Trading — trading educator.
Create a 5-minute educational video SCRIPT about candlestick patterns.

COVER THESE 5 PATTERNS (1 minute each):
1. Doji — what it means, when it matters
2. Hammer & Hanging Man — reversal signals
3. Engulfing Pattern — bullish and bearish
4. Morning Star / Evening Star — 3-candle reversals
5. Shooting Star — top rejection signal

For each pattern:
- Simple explanation in plain English/Hindi-friendly language
- Real example from NIFTY or stock chart
- How to trade it — entry, stop loss

Format: NARRATOR: for spoken lines. SLIDE: for visuals (describe chart/diagram).
Total spoken words: 550-600 words. Keep it simple for beginners.
"""
    elif topic_type == "personal_finance":
        focus = f"""
You are Amit Kumar from AI360Trading — certified financial planner.
Create a 4-minute video SCRIPT comparing SIP vs Lump Sum investment.

USE REAL NUMBERS:
- SIP ₹5000/month for 10 years at 12% CAGR = ₹11.6 lakhs invested, ₹23.2 lakhs returns
- Lump Sum ₹6 lakhs at 12% CAGR for 10 years = ₹18.6 lakhs

COVER:
1. What is SIP — simple explanation
2. What is Lump Sum — simple explanation
3. Real number comparison with examples
4. When to choose SIP (volatile market, salary income)
5. When to choose Lump Sum (market crash, bonus)
6. Final recommendation for Indian middle class

Format: NARRATOR: for spoken lines. SLIDE: for visuals/charts/numbers.
Language: Simple, friendly, like talking to a family member.
Total spoken words: 450-500 words.
"""
    elif topic_type == "weekly_outlook":
        focus = f"""
You are Amit Kumar from AI360Trading — market analyst.
Create a 4-minute weekly outlook video SCRIPT for the week of {date_display}.

LIVE DATA:
- NIFTY: {nifty.get('display','N/A')}
- S&P 500: {sp500.get('display','N/A')}
- Bitcoin: {btc.get('display','N/A')}
- Fear & Greed: {fg_val} — {fg_label}

COVER:
1. Last week recap — what happened (based on current prices)
2. This week key events to watch (RBI, Fed, earnings)
3. NIFTY weekly levels — support and resistance
4. S&P 500 weekly outlook
5. Bitcoin weekly outlook
6. Overall market mood and trader advice

Format: NARRATOR: for spoken. SLIDE: for visuals.
Total spoken words: 450-500 words.
"""
    elif topic_type == "education_patterns":
        focus = """
You are Amit Kumar from AI360Trading — trading educator.
Create a 5-minute educational video SCRIPT about Support & Resistance levels.

COVER:
1. What is Support — simple definition with visual
2. What is Resistance — simple definition with visual
3. How to identify these levels on a chart (3 methods)
4. Why these levels work — psychology of traders
5. How to trade a support bounce — entry, stop, target
6. How to trade a resistance breakout — entry, stop, target
7. Common mistakes beginners make

Format: NARRATOR: for spoken. SLIDE: for visuals/chart descriptions.
Language: Very simple — beginners watching.
Total spoken words: 550-600 words.
"""
    else:  # top5_stocks
        focus = f"""
You are Amit Kumar from AI360Trading — institutional analyst.
Create a 4-minute video SCRIPT covering 5 stocks to watch this week.

Pick 5 stocks from NIFTY 200 that are showing:
- Volume breakout or accumulation
- Clean support level nearby
- Strong sector momentum

Current market: NIFTY {nifty.get('display','N/A')}, S&P 500 {sp500.get('display','N/A')}

For each stock give:
- Stock name and sector
- Why it's interesting this week
- Key level to watch
- Risk reminder

Format: NARRATOR: for spoken. SLIDE: for visuals.
Total spoken words: 450-500 words.
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": focus}],
            temperature=0.8,
            max_tokens=2000,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Script generation failed: {e}")
        return None

# ─── 3. Parse Script into Slides ─────────────────────────────────────────────
def parse_script(script_text):
    """Parse NARRATOR/SLIDE pairs from script"""
    slides = []
    current_narrator = ""
    current_slide = ""

    for line in script_text.split("\n"):
        line = line.strip()
        if line.startswith("NARRATOR:"):
            if current_narrator and current_slide:
                slides.append({
                    "narrator": current_narrator.strip(),
                    "slide": current_slide.strip()
                })
            current_narrator = line.replace("NARRATOR:", "").strip()
            current_slide = ""
        elif line.startswith("SLIDE:"):
            current_slide = line.replace("SLIDE:", "").strip()
        elif line and current_narrator:
            current_narrator += " " + line

    if current_narrator:
        slides.append({
            "narrator": current_narrator.strip(),
            "slide": current_slide.strip() if current_slide else "AI360Trading Analysis"
        })

    # Ensure minimum slides
    if len(slides) < 3:
        slides = [{"narrator": script_text[:500], "slide": "AI360Trading Market Analysis"}]

    return slides

# ─── 4. Generate Slide Images ─────────────────────────────────────────────────
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

def create_title_slide(title, subtitle, color, output_path):
    """Create branded title card"""
    fig, ax = plt.subplots(1, 1, figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(hex_to_rgb(BRAND_DARK))
    ax.set_facecolor(hex_to_rgb(BRAND_DARK))

    # Accent bar
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.05, 0.85), 0.9, 0.006,
        boxstyle="round,pad=0", color=hex_to_rgb(color), transform=ax.transAxes
    ))

    # Logo text
    ax.text(0.5, 0.92, "AI360TRADING", transform=ax.transAxes,
            fontsize=14, fontweight='bold', color=hex_to_rgb(color),
            ha='center', va='center', alpha=0.9)

    # Main title
    wrapped = textwrap.fill(title, width=40)
    ax.text(0.5, 0.62, wrapped, transform=ax.transAxes,
            fontsize=28, fontweight='bold', color='white',
            ha='center', va='center', linespacing=1.3)

    # Subtitle
    ax.text(0.5, 0.38, subtitle, transform=ax.transAxes,
            fontsize=16, color='#94a3b8', ha='center', va='center')

    # Date badge
    ax.text(0.5, 0.25, f"📅 {date_display}", transform=ax.transAxes,
            fontsize=13, color=hex_to_rgb(color), ha='center', va='center',
            fontweight='bold')

    # Bottom bar
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.0, 0.0), 1.0, 0.08,
        boxstyle="round,pad=0", color=hex_to_rgb(color),
        transform=ax.transAxes, alpha=0.15
    ))
    ax.text(0.5, 0.04, "ai360trading.in  |  @ai360trading",
            transform=ax.transAxes, fontsize=11, color='#64748b',
            ha='center', va='center')

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=100, bbox_inches='tight',
                facecolor=hex_to_rgb(BRAND_DARK))
    plt.close()

def create_content_slide(slide_text, narrator_text, color, slide_num, total, output_path):
    """Create content slide with text"""
    fig, ax = plt.subplots(1, 1, figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(hex_to_rgb(BRAND_DARK))
    ax.set_facecolor(hex_to_rgb(BRAND_DARK))

    # Top accent
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.0, 0.93), 1.0, 0.005,
        boxstyle="round,pad=0", color=hex_to_rgb(color), transform=ax.transAxes
    ))

    # Slide number
    ax.text(0.97, 0.97, f"{slide_num}/{total}", transform=ax.transAxes,
            fontsize=10, color='#475569', ha='right', va='top')

    # Brand
    ax.text(0.03, 0.97, "AI360TRADING", transform=ax.transAxes,
            fontsize=10, fontweight='bold', color=hex_to_rgb(color),
            ha='left', va='top', alpha=0.8)

    # Main content text
    wrapped = textwrap.fill(slide_text, width=55)
    lines   = wrapped.split('\n')
    y_start = 0.78
    for i, line in enumerate(lines[:6]):
        fontsize = 22 if i == 0 else 18
        weight   = 'bold' if i == 0 else 'normal'
        ax.text(0.08, y_start - i * 0.10, line, transform=ax.transAxes,
                fontsize=fontsize, color='white' if i == 0 else '#cbd5e1',
                ha='left', va='top', fontweight=weight)

    # Bottom narrator preview (subtle)
    preview = narrator_text[:80] + "..." if len(narrator_text) > 80 else narrator_text
    ax.text(0.5, 0.08, f'"{preview}"', transform=ax.transAxes,
            fontsize=11, color='#475569', ha='center', va='center',
            style='italic', wrap=True)

    # Bottom bar
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.0, 0.0), 1.0, 0.06,
        boxstyle="round,pad=0", color=hex_to_rgb(color),
        transform=ax.transAxes, alpha=0.1
    ))
    ax.text(0.5, 0.03, "ai360trading.in  |  Subscribe for daily analysis",
            transform=ax.transAxes, fontsize=10, color='#64748b',
            ha='center', va='center')

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=100, bbox_inches='tight',
                facecolor=hex_to_rgb(BRAND_DARK))
    plt.close()

def create_price_chart_slide(prices, color, output_path):
    """Create live price data visualization slide"""
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(hex_to_rgb(BRAND_DARK))

    key_instruments = [
        ("NIFTY 50",  BRAND_BLUE),
        ("S&P 500",   BRAND_GREEN),
        ("Bitcoin",   BRAND_ORANGE),
    ]

    for idx, (name, inst_color) in enumerate(key_instruments):
        ax = axes[idx]
        ax.set_facecolor('#1e293b')
        data = prices.get(name, {})
        price = data.get('price', 0)
        pct   = data.get('pct', 0)
        prev  = data.get('prev', price)

        # Simulated intraday line (5 points)
        x = [0, 1, 2, 3, 4]
        base = prev
        y = [base,
             base + (price-base)*0.25 + random.uniform(-base*0.003, base*0.003),
             base + (price-base)*0.5  + random.uniform(-base*0.003, base*0.003),
             base + (price-base)*0.75 + random.uniform(-base*0.003, base*0.003),
             price]

        line_color = '#2ecc71' if pct >= 0 else '#e74c3c'
        ax.plot(x, y, color=line_color, linewidth=3, zorder=3)
        ax.fill_between(x, y, min(y)*0.999, alpha=0.15, color=line_color)

        # Price label
        ax.text(0.5, 0.88, name, transform=ax.transAxes,
                fontsize=13, fontweight='bold', color='white',
                ha='center', va='center')

        price_str = f"₹{price:,.0f}" if name in ["NIFTY 50","Bank Nifty"] else f"${price:,.0f}" if name=="Bitcoin" else f"{price:,.0f}"
        ax.text(0.5, 0.72, price_str, transform=ax.transAxes,
                fontsize=18, fontweight='bold', color=line_color,
                ha='center', va='center')

        arrow = "▲" if pct >= 0 else "▼"
        ax.text(0.5, 0.58, f"{arrow} {abs(pct):.2f}%", transform=ax.transAxes,
                fontsize=14, color=line_color, ha='center', va='center',
                fontweight='bold')

        ax.spines['bottom'].set_color('#334155')
        ax.spines['left'].set_color('#334155')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors='#64748b', labelsize=8)
        ax.set_xticks([])

    fig.suptitle(f"Live Market Data — {date_display}",
                 color='white', fontsize=16, fontweight='bold', y=0.97)

    plt.tight_layout(pad=1.5)
    plt.savefig(output_path, dpi=100, bbox_inches='tight',
                facecolor=hex_to_rgb(BRAND_DARK))
    plt.close()

def create_outro_slide(color, output_path):
    """Create subscribe/CTA outro slide"""
    fig, ax = plt.subplots(1, 1, figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(hex_to_rgb(BRAND_DARK))
    ax.set_facecolor(hex_to_rgb(BRAND_DARK))

    ax.text(0.5, 0.82, "AI360TRADING", transform=ax.transAxes,
            fontsize=36, fontweight='bold', color=hex_to_rgb(color),
            ha='center', va='center')

    ax.text(0.5, 0.65, "🔔 Subscribe for Daily Market Intelligence",
            transform=ax.transAxes, fontsize=20, color='white',
            ha='center', va='center', fontweight='bold')

    ax.text(0.5, 0.50, "📊 Stock Market  |  ₿ Bitcoin  |  💰 Finance  |  🤖 AI Trading",
            transform=ax.transAxes, fontsize=14, color='#94a3b8',
            ha='center', va='center')

    ax.text(0.5, 0.37, "📣 Telegram: t.me/ai360trading",
            transform=ax.transAxes, fontsize=15, color=hex_to_rgb(BRAND_GREEN),
            ha='center', va='center', fontweight='bold')

    ax.text(0.5, 0.25, "🌐 ai360trading.in",
            transform=ax.transAxes, fontsize=15, color=hex_to_rgb(color),
            ha='center', va='center', fontweight='bold')

    ax.text(0.5, 0.12, "⚠️ For educational purposes only. Not financial advice.",
            transform=ax.transAxes, fontsize=11, color='#475569',
            ha='center', va='center')

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=100, bbox_inches='tight',
                facecolor=hex_to_rgb(BRAND_DARK))
    plt.close()

# ─── 5. Text to Speech ────────────────────────────────────────────────────────
def text_to_speech(text, output_path, lang='en', tld='co.in'):
    """Convert text to MP3 using gTTS — Indian English accent"""
    try:
        # Clean text for TTS
        clean = text.replace("₹", "rupees ").replace("$", "dollars ")
        clean = clean.replace("%", " percent").replace("&", " and ")
        clean = clean.replace("|", ". ").replace("→", " ")
        clean = clean.replace("▲", "up ").replace("▼", "down ")

        tts = gTTS(text=clean, lang=lang, tld=tld, slow=False)
        tts.save(output_path)
        return True
    except Exception as e:
        print(f"TTS failed: {e}")
        return False

# ─── 6. Assemble Video ────────────────────────────────────────────────────────
def assemble_video(slides_data, script_slides, prices, topic, output_path):
    """Combine all image slides + audio into final MP4"""
    clips = []

    for i, (img_path, slide) in enumerate(zip(slides_data, script_slides)):
        narrator_text = slide.get("narrator", "")
        if not narrator_text:
            continue

        # Generate audio for this slide
        audio_path = os.path.join(OUTPUT_DIR, f"audio_{i}.mp3")
        success = text_to_speech(narrator_text, audio_path)

        if not success or not os.path.exists(audio_path):
            # Fallback: silent 5 second clip
            img_clip = ImageClip(img_path).set_duration(5)
            clips.append(img_clip)
            continue

        # Load audio and get duration
        audio_clip = AudioFileClip(audio_path)
        duration   = audio_clip.duration + 0.5  # 0.5s pause between slides

        # Create image clip matching audio duration
        img_clip = (ImageClip(img_path)
                    .set_duration(duration)
                    .set_audio(audio_clip))

        clips.append(img_clip)
        time.sleep(0.2)

    if not clips:
        print("No clips generated")
        return False

    # Concatenate all clips
    final_video = concatenate_videoclips(clips, method="compose")
    final_video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile=os.path.join(OUTPUT_DIR, 'temp_audio.m4a'),
        remove_temp=True,
        logger=None
    )
    return True

# ─── 7. Upload to YouTube ─────────────────────────────────────────────────────
def upload_to_youtube(video_path, title, description, tags, thumbnail_path=None):
    """Upload video to YouTube using OAuth2 credentials from environment"""
    if not YOUTUBE_OK:
        print("YouTube upload skipped — library not installed")
        return None

    try:
        # Load credentials from environment variable
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json:
            print("YOUTUBE_CREDENTIALS not set in GitHub Secrets")
            return None

        creds_data = json.loads(creds_json)
        creds = Credentials(
            token=creds_data.get("token"),
            refresh_token=creds_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=creds_data.get("client_id"),
            client_secret=creds_data.get("client_secret"),
        )

        youtube = build('youtube', 'v3', credentials=creds)

        body = {
            'snippet': {
                'title':       title[:100],
                'description': description,
                'tags':        tags,
                'categoryId':  '27',  # Education category
                'defaultLanguage': 'en',
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False,
            }
        }

        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True,
            mimetype='video/mp4'
        )

        request  = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  Upload progress: {int(status.progress() * 100)}%")

        video_id  = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"  ✅ Uploaded: {video_url}")

        # Upload custom thumbnail if provided
        if thumbnail_path and os.path.exists(thumbnail_path):
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("  ✅ Thumbnail uploaded")

        return video_id

    except Exception as e:
        print(f"  ❌ YouTube upload failed: {e}")
        return None

# ─── 8. Main ──────────────────────────────────────────────────────────────────
def generate_video():
    if not LIBS_OK:
        print("❌ Required libraries not installed. See requirements.")
        sys.exit(1)

    topic = VIDEO_TOPICS[weekday]

    print("=" * 60)
    print(f"  AI360Trading Video Bot — {date_display}")
    print(f"  Today: {topic['type']}")
    print("=" * 60)

    # Fetch live data
    print("\n  Fetching live market data...")
    prices   = get_live_prices()
    fg_val, fg_label = get_fear_greed()
    print(f"  NIFTY  : {prices.get('NIFTY 50',{}).get('display','N/A')}")
    print(f"  BTC    : {prices.get('Bitcoin',{}).get('display','N/A')}")
    print(f"  F&G    : {fg_val} — {fg_label}")

    # Build title and description
    title = topic["title_template"].format(
        date=date_display,
        year=now.year
    )
    description = topic["description_template"].format(
        date=date_display,
        year=now.year
    )

    # Generate script
    print("\n  Generating video script...")
    script_text = generate_video_script(topic, prices, fg_val, fg_label)
    if not script_text:
        print("❌ Script generation failed")
        sys.exit(1)
    print(f"  Script: {len(script_text)} chars")

    # Parse script into slides
    script_slides = parse_script(script_text)
    print(f"  Slides: {len(script_slides)} sections")

    # Generate slide images
    print("\n  Generating slide images...")
    slide_image_paths = []
    color = topic["color"]

    # Slide 0 — Title
    title_path = os.path.join(OUTPUT_DIR, "slide_00_title.png")
    create_title_slide(title, f"{topic['type'].replace('_',' ').title()} | AI360Trading", color, title_path)
    slide_image_paths.append(title_path)
    script_slides.insert(0, {"narrator": f"Welcome to AI360Trading. Today's report — {title}", "slide": "Title"})

    # Slide 1 — Live prices chart (for market topics)
    if topic["type"] in ["nifty_analysis", "bitcoin_analysis", "weekly_outlook", "top5_stocks"]:
        chart_path = os.path.join(OUTPUT_DIR, "slide_01_prices.png")
        create_price_chart_slide(prices, color, chart_path)
        slide_image_paths.append(chart_path)
        script_slides.insert(1, {
            "narrator": f"Here are the live market levels as of {date_display}. NIFTY at {prices.get('NIFTY 50',{}).get('display','N/A')}, S&P 500 at {prices.get('S&P 500',{}).get('display','N/A')}, and Bitcoin at {prices.get('Bitcoin',{}).get('display','N/A')}.",
            "slide": "Live Prices"
        })

    # Content slides
    for i, slide in enumerate(script_slides[2:], start=2):
        img_path = os.path.join(OUTPUT_DIR, f"slide_{i:02d}_content.png")
        create_content_slide(
            slide.get("slide", slide.get("narrator","")[:80]),
            slide.get("narrator", ""),
            color, i, len(script_slides), img_path
        )
        slide_image_paths.append(img_path)

    # Outro slide
    outro_path = os.path.join(OUTPUT_DIR, "slide_outro.png")
    create_outro_slide(color, outro_path)
    slide_image_paths.append(outro_path)
    script_slides.append({
        "narrator": "Subscribe to AI360Trading for daily market intelligence. Visit ai360trading.in for full written analysis. Join our Telegram at t.me/ai360trading. See you tomorrow.",
        "slide": "Outro"
    })

    # Assemble video
    print("\n  Assembling video...")
    video_path = os.path.join(OUTPUT_DIR, f"ai360trading_{date_str}_{topic['type']}.mp4")
    success = assemble_video(slide_image_paths, script_slides, prices, topic, video_path)

    if not success:
        print("❌ Video assembly failed")
        sys.exit(1)

    size_mb = os.path.getsize(video_path) / (1024*1024)
    print(f"  ✅ Video ready: {size_mb:.1f} MB")

    # Upload to YouTube
    print("\n  Uploading to YouTube...")
    video_id = upload_to_youtube(
        video_path,
        title,
        description,
        topic["tags"],
        thumbnail_path=slide_image_paths[0]
    )

    if video_id:
        print(f"\n{'='*60}")
        print(f"  ✅ VIDEO LIVE: https://www.youtube.com/watch?v={video_id}")
        print(f"  Title: {title[:70]}")
        print(f"  Channel: https://www.youtube.com/@ai360trading")
        print(f"{'='*60}")
    else:
        print(f"\n  Video saved locally: {video_path}")
        print("  Set YOUTUBE_CREDENTIALS in GitHub Secrets to enable auto-upload")

if __name__ == "__main__":
    generate_video()
