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
        CompositeVideoClip, ColorClip
    )
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import matplotlib.ticker
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
    LIBS_OK = True
except ImportError as e:
    print(f"Missing library: {e}")
    print("Run: pip install gtts moviepy==1.0.3 matplotlib numpy pillow")
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
        "title_template": "NIFTY Just Dropped {pct}% — Is This a Crash or a Buying Opportunity? | {date}",
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
        "title_template": "What Will Markets Do Next Week? NIFTY & Global Outlook | {date}",
        "duration_target": 240,
        "color": BRAND_BLUE,
        "tags": ["weekly market outlook", "nifty next week", "stock market this week", "market prediction", "trading week ahead"],
        "description_template": "Weekly market outlook for the week of {date}. NIFTY, S&P 500, Bitcoin — key levels and what to watch this week.\n\n🔔 Subscribe for weekly market analysis\n📊 Full reports: https://ai360trading.in\n📣 Telegram: https://t.me/ai360trading\n\n#WeeklyOutlook #StockMarket #NIFTY #Trading #AI360Trading"
    },
    5: {  # Saturday
        "type": "education_patterns",
        "title_template": "The Support Level NIFTY Hit Today — And What Happens Next",
        "duration_target": 300,
        "color": BRAND_PURPLE,
        "tags": ["support resistance", "technical analysis", "trading education", "price action", "how to trade stocks"],
        "description_template": "Support and resistance levels explained simply. How professional traders identify and trade these key price levels on NIFTY, S&P 500 and stocks.\n\n🔔 Subscribe for trading education\n🤖 More: https://ai360trading.in/topics/ai-trading/\n📣 Telegram: https://t.me/ai360trading\n\n#SupportResistance #TechnicalAnalysis #TradingEducation #PriceAction #AI360Trading"
    },
    6: {  # Sunday
        "type": "top5_stocks",
        "title_template": "5 Stocks I Am Watching This Week — {date} | NIFTY Market Picks",
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
    gold    = prices.get("Gold", {})

    topic_type = topic["type"]
    nifty_p    = nifty.get("price", 24000)
    nifty_pct  = nifty.get("pct", 0)
    sp500_p    = sp500.get("price", 5500)
    btc_p      = btc.get("price", 65000)
    s1_nifty   = int(nifty_p * 0.986)
    r1_nifty   = int(nifty_p * 1.014)
    s1_btc     = int(btc_p * 0.95)
    r1_btc     = int(btc_p * 1.05)

    # Mood words based on market
    mood       = "crashing" if nifty_pct < -2 else "falling" if nifty_pct < 0 else "recovering" if nifty_pct < 1 else "surging"
    crash_word = "biggest drop in months" if nifty_pct < -3 else f"{abs(nifty_pct):.1f}% drop today" if nifty_pct < 0 else f"{nifty_pct:.1f}% gain today"
    fear_context = "Everyone is panicking right now." if fg_val < 25 else "Fear is rising fast." if fg_val < 40 else "Markets are uncertain." if fg_val < 55 else "Greed is back in the market."

    SYSTEM_PROMPT = """You are Amit Kumar — founder of AI360Trading, independent market analyst from Haridwar, India.
You have been tracking Indian and global markets for years.
Your YouTube channel speaks directly to Indian retail traders and investors.

YOUR VOICE IS:
- Direct and confident — you have strong opinions and you share them
- Human and conversational — like talking to a fellow trader, not reading a report
- Emotionally engaging — you create tension, curiosity, risk awareness
- Never robotic — vary sentence length, mix short punchy lines with deeper explanations

BANNED PHRASES (never use):
"Here is the chart", "Now let us dive into", "Moving on to", "As we can see",
"In conclusion", "It is important to note", "This highlights", "Let us explore",
"Welcome to AI360Trading. Today's report", "Subscribe to our channel for daily market analysis"

SCRIPT FORMAT RULES:
- Write NARRATOR: before each spoken line (English with Indian accent)
- Write SLIDE: before each visual description (in English)
- Write HINDI_SUB: after each SLIDE — 3-6 Hindi words summarizing the slide (shown as subtitle on screen)
  Examples: "HINDI_SUB: आज का सबसे जरूरी Level" or "HINDI_SUB: क्या यह Crash है?" or "HINDI_SUB: Support टूटा तो गिरावट तय"
- Hook must create CURIOSITY or TENSION in first 10 seconds
- Place SOFT CTA naturally around 60-90 seconds
- End with STRONG close that makes viewer want tomorrow's video
- Vary sentence length — short punchy lines mixed with deeper analysis
- Total spoken words: stated below per video type"""

    if topic_type == "nifty_analysis":
        focus = f"""
LIVE DATA RIGHT NOW:
- NIFTY 50: {nifty.get('display','N/A')} ({nifty_pct:+.2f}%)
- Bank Nifty: {bnifty.get('display','N/A')}
- S&P 500: {sp500.get('display','N/A')}
- Fear & Greed Index: {fg_val} — {fg_label}
- NIFTY S1: {s1_nifty} | R1: {r1_nifty}

Create a 3-minute NIFTY analysis video script.

STRUCTURE (follow this emotional arc):

HOOK (first 15 seconds) — START with the market reality, create tension:
Example style: "NIFTY just had its {crash_word}. And right now the index is sitting on a level that could decide whether this becomes a full crash — or a sharp recovery. Let me show you exactly what I am watching."

CONTEXT (30 seconds) — Why is this happening:
- Connect S&P 500 move to NIFTY
- One sentence on global trigger (Fed, dollar, oil — whatever fits)
- {fear_context}

SOFT CTA (natural, 1 sentence) — insert here:
Example: "If you trade NIFTY regularly, we post these levels every morning before market opens — subscribe and hit the bell so you never miss them."

KEY LEVELS — The most important part:
- NIFTY support at {s1_nifty} — explain WHY this level matters (previous high, round number, etc.)
- NIFTY resistance at {r1_nifty} — what happens if this breaks up
- The RISK: what happens if {s1_nifty} breaks down — be specific and create tension
- Bank Nifty key level — one sentence, sharp

TRADE SCENARIO (create narrative tension):
- Bull case: "If buyers defend {s1_nifty}, we could see a quick bounce to..."
- Bear case: "But if {s1_nifty} breaks on volume, the next stop is..."

STRONG CLOSE — Make them want tomorrow's video:
Example style: "Tomorrow morning I will update these levels based on US market close tonight. Watch what happens at {s1_nifty} today — that level tells us everything."

Total spoken words: 380-420 words.
"""

    elif topic_type == "bitcoin_analysis":
        focus = f"""
LIVE DATA:
- Bitcoin: {btc.get('display','N/A')} ({btc.get('pct',0):+.2f}%)
- Fear & Greed: {fg_val} — {fg_label}
- S&P 500: {sp500.get('display','N/A')} (risk signal)
- BTC S1: ${s1_btc:,} | R1: ${r1_btc:,}

Create a 3-minute Bitcoin analysis video script.

STRUCTURE:

HOOK — Bitcoin reality check, create curiosity:
Example style: "Bitcoin is at ${btc_p:,.0f} right now. And the Fear and Greed index just hit {fg_val} — {fg_label}. The last time we saw readings this extreme was just before a major move. Here is what the chart is telling me."

CONTEXT:
- Is S&P falling too? Risk-off environment — explain in simple terms
- On-chain signal or options sentiment in one sentence
- {fear_context}

SOFT CTA (natural): "We track Bitcoin levels daily at ai360trading.in — link in description. Subscribe if you want these updates before the market moves."

KEY LEVELS with narrative:
- Support at ${s1_btc:,} — what happens here matters (explain psychologically)
- Resistance at ${r1_btc:,} — the breakout level everyone is watching
- The real question: is this a buying opportunity or a falling knife?

CONTRARIAN VIEW — say something unexpected:
- Example: "Everyone is saying buy the dip. But I want to see confirmation before I trust this level."

STRONG CLOSE — leave them thinking:
Example: "Bitcoin at these levels is either a gift or a trap. Tomorrow we will know which one it was."

Total spoken words: 380-420 words.
"""

    elif topic_type == "education_candlestick":
        focus = f"""
Create a 5-minute educational video script about candlestick patterns.
Current market context: NIFTY {nifty.get('display','N/A')}, {mood} today.

STRUCTURE:

HOOK — connect to TODAY's market:
Example: "NIFTY just formed a specific candlestick pattern on the daily chart today. And if you know what this pattern means — you already know what might happen tomorrow. Let me teach you the 5 patterns every trader must know."

PATTERN 1 — DOJI (tension and uncertainty):
Explain it feels like the market is holding its breath. Real NIFTY example.

SOFT CTA here: "If you want daily candlestick breakdowns before market opens, subscribe — we post every morning."

PATTERN 2 — HAMMER (hope after a fall):
Explain the psychology — sellers tried to push down but buyers fought back. Real example.

PATTERN 3 — ENGULFING (the power shift):
Explain this is when one side completely takes over. Most reliable pattern.

PATTERN 4 — MORNING/EVENING STAR (the 3-candle warning):
Explain why 3 candles together tell a complete story. Very visual.

PATTERN 5 — SHOOTING STAR (the rejection):
The pattern that says "this level was tested and rejected." Common on NIFTY tops.

STRONG CLOSE — practical homework:
"Open your NIFTY chart right now and see if you can spot any of these 5 patterns from this week. Tell me in the comments what you found."

Total spoken words: 560-600 words.
"""

    elif topic_type == "personal_finance":
        focus = f"""
Create a 4-minute personal finance video — SIP vs Lump Sum.
Market context: NIFTY is {mood} today, Fear & Greed at {fg_val}.

STRUCTURE:

HOOK — connect to TODAY's market crash/rally:
Example if market falling: "Markets are down today. And if you have money sitting in your bank account right now — this video will help you decide what to do with it."
Example if market rising: "If you missed today's market rally — this video explains how SIP investors are actually benefiting from missing moves like this."

RELATABLE STORY — open with a real scenario:
"Imagine you have ₹6 lakhs saved up. Your friend says put it all in now. Your father says start SIP. Who is right? Let me show you what the numbers actually say."

SOFT CTA: "We cover personal finance every week at AI360Trading — subscribe for free guides that actually help you build wealth."

THE NUMBERS (make them feel real):
- SIP ₹5,000/month × 10 years at 12% CAGR = ₹23.2 lakhs
- Lump Sum ₹6 lakhs × 10 years at 12% CAGR = ₹18.6 lakhs
- BUT — show when lump sum wins (crash bottom)
- AND — show when SIP wins (volatile market like today)

THE HONEST TRUTH — add your opinion:
"Personally, for most salaried Indians, SIP wins. Not because returns are better — but because most people cannot handle seeing a lump sum drop 30% and staying invested."

STRONG CLOSE:
"The best investment is the one you actually stick with. That is SIP for most people. Start with whatever amount you can — even ₹500 matters more than waiting for the perfect time."

Total spoken words: 460-500 words.
"""

    elif topic_type == "weekly_outlook":
        focus = f"""
LIVE DATA:
- NIFTY: {nifty.get('display','N/A')} | S&P 500: {sp500.get('display','N/A')}
- Bitcoin: {btc.get('display','N/A')} | Fear & Greed: {fg_val} — {fg_label}
- NIFTY levels: S1={s1_nifty}, R1={r1_nifty}

Create a 4-minute weekly market outlook script for {date_display}.

STRUCTURE:

HOOK — what defined this week:
Example: "This was one of the most volatile weeks of 2026 so far. NIFTY dropped sharply. Bitcoin got hit. And one number — the Fear and Greed index at {fg_val} — is telling us something important about what happens next week."

WEEK RECAP (what actually happened — based on live prices):
- NIFTY reality: current level, what drove the move
- Global picture: S&P 500, Dollar, what macro event mattered most
- One surprising thing from this week

SOFT CTA: "Every Sunday we post this weekly outlook before markets open Monday — subscribe so you are prepared, not reactive."

NEXT WEEK SETUP:
- Key events to watch: RBI meeting / Fed / earnings / global data
- NIFTY levels that matter for the week ahead
- Bitcoin weekly outlook — is the trend changing?

THE BIG QUESTION for next week — create suspense:
Example: "The one thing I will be watching next week is {s1_nifty} on NIFTY. If that level holds on Monday open — bulls are back in control. If it breaks — things could get much worse before they get better."

STRONG CLOSE:
"See you Monday morning with the daily levels. Have a good weekend — and keep your stops in place."

Total spoken words: 460-500 words.
"""

    elif topic_type == "education_patterns":
        focus = f"""
Create a 5-minute educational video about Support and Resistance levels.
Market context today: NIFTY {nifty.get('display','N/A')}, {mood}.

STRUCTURE:

HOOK — use today's market to make it real:
Example: "NIFTY hit a major support level today. And what happened there — either a bounce or a break — is exactly what support and resistance is about. Let me explain this concept using today's chart as the example."

WHAT IS SUPPORT — keep it real, not textbook:
"Support is not a magic number. It is a price where enough buyers showed up before to stop the fall. Think of it like a floor — it can hold, or it can break."
Use {s1_nifty} as live example from today.

SOFT CTA: "We mark these levels every morning for NIFTY and Bitcoin — subscribe and you will have them before market opens."

WHAT IS RESISTANCE — the mirror:
"Resistance is where sellers showed up before and stopped the rally. It is a ceiling. And ceilings can either reject price — or break and become new floors."
Use {r1_nifty} as live example.

3 WAYS TO IDENTIFY LEVELS:
1. Previous highs and lows — most reliable
2. Round numbers — psychological magnets (24000, 25000)
3. Volume nodes — where most trading happened

THE PSYCHOLOGY — why they work:
"These levels work because thousands of traders are watching the same chart. When price hits a known level, everyone reacts — and that reaction creates the bounce or the break."

TRADING THE LEVELS — practical:
- Bounce trade: wait for confirmation candle at support, stop just below
- Breakout trade: wait for candle CLOSE above resistance, not just a wick

COMMON MISTAKE:
"The biggest mistake is buying exactly at support. Wait. Let the market show you it is holding first."

STRONG CLOSE:
"Look at today's NIFTY chart right now. Find {s1_nifty}. That is a live support level. Watch what price does there — and you will understand support and resistance better than any textbook can teach you."

Total spoken words: 560-600 words.
"""

    else:  # top5_stocks
        focus = f"""
LIVE DATA:
- NIFTY: {nifty.get('display','N/A')} ({nifty_pct:+.2f}%)
- S&P 500: {sp500.get('display','N/A')}
- Fear & Greed: {fg_val} — {fg_label}

Create a 4-minute Top 5 Stocks to Watch video script for {date_display}.

STRUCTURE:

HOOK — create urgency:
Example: "NIFTY is {mood} right now. In a market like this, most stocks are getting hit. But 5 specific stocks are showing setups that serious traders should not ignore this week. Here they are."

MARKET CONTEXT (brief — 20 seconds):
One line on why market is doing what it is doing today.
One line on what kind of stocks do well in this environment.

SOFT CTA: "Every Sunday we post the top stocks for the week — subscribe so you get them before Monday open."

STOCK 1 — build narrative tension:
Format: "Stock name, sector. Here is why it is interesting — [specific reason: breakout, volume, sector rotation]. The level I am watching is [specific price]. If it holds/breaks — [what happens]."
Do NOT say "Stock 1 is X". Say "First up —" or "The one that caught my eye this week —"

STOCKS 2-5 — same narrative format, vary the opening phrase each time.
Use these openers: "Next —", "This one surprised me —", "Contrarian pick —", "High risk high reward —"

Add one genuine opinion per stock — "Personally I think..." or "I would wait for..." or "This one worries me because..."

STRONG CLOSE — weekly challenge:
"Pick one of these five stocks and paper trade it this week. Come back next Sunday and tell me in the comments how it went. See you tomorrow morning with the daily NIFTY levels."

Total spoken words: 460-500 words.
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": focus}
            ],
            temperature=0.92,
            max_tokens=2200,
            frequency_penalty=0.45,
            presence_penalty=0.35,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Script generation failed: {e}")
        return None

# ─── 3. Parse Script into Slides ─────────────────────────────────────────────
def parse_script(script_text):
    """Parse script into slides — handles NARRATOR/SLIDE tags and plain paragraphs"""
    slides = []
    current_narrator = ""
    current_slide = ""

    # ── Method 1: try NARRATOR/SLIDE tag parsing ─────────────────────────────
    has_tags = "NARRATOR:" in script_text

    if has_tags:
        current_hindi = ""
        for line in script_text.split("\n"):
            line = line.strip()
            if line.startswith("NARRATOR:"):
                if current_narrator:
                    slides.append({
                        "narrator": current_narrator.strip(),
                        "slide": current_slide.strip() if current_slide else _extract_slide_title(current_narrator),
                        "hindi_sub": current_hindi.strip()
                    })
                current_narrator = line.replace("NARRATOR:", "").strip()
                current_slide = ""
                current_hindi = ""
            elif line.startswith("SLIDE:"):
                current_slide = line.replace("SLIDE:", "").strip()
            elif line.startswith("HINDI_SUB:"):
                current_hindi = line.replace("HINDI_SUB:", "").strip()
            elif line and not line.startswith("#") and not line.startswith("---"):
                if current_narrator:
                    current_narrator += " " + line

        if current_narrator:
            slides.append({
                "narrator": current_narrator.strip(),
                "slide": current_slide.strip() if current_slide else _extract_slide_title(current_narrator),
                "hindi_sub": current_hindi.strip()
            })

    # ── Method 2: paragraph-based fallback ───────────────────────────────────
    if len(slides) < 3:
        slides = []
        # Split by double newline or section headers
        paragraphs = [p.strip() for p in script_text.split("\n\n") if p.strip()]
        # Also split on lines starting with ** or ## (section headers)
        all_chunks = []
        for para in paragraphs:
            lines = para.split("\n")
            chunk = ""
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # New section header = new slide
                if (line.startswith("**") and line.endswith("**")) or line.startswith("##"):
                    if chunk:
                        all_chunks.append(chunk.strip())
                    chunk = line.lstrip("#").strip("*").strip() + ": "
                else:
                    chunk += " " + line
            if chunk.strip():
                all_chunks.append(chunk.strip())

        for chunk in all_chunks:
            if len(chunk) > 30:  # skip very short lines
                slides.append({
                    "narrator": chunk,
                    "slide": _extract_slide_title(chunk),
                    "hindi_sub": ""
                })

    # ── Final fallback: split into ~100 word chunks ───────────────────────────
    if len(slides) < 3:
        words = script_text.split()
        chunk_size = 80
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            if chunk:
                slides.append({
                    "narrator": chunk,
                    "slide": _extract_slide_title(chunk),
                    "hindi_sub": ""
                })

    return slides[:12]  # max 12 slides


def _extract_slide_title(text):
    """Extract a short title from narrator text for the slide header"""
    # Take first sentence or first 8 words
    sentences = text.replace("?", ".").replace("!", ".").split(".")
    first = sentences[0].strip() if sentences else text
    words = first.split()
    title = " ".join(words[:8])
    # Clean markdown
    title = title.replace("**", "").replace("##", "").strip()
    return title if title else "AI360Trading Analysis"

# ─── 4. Generate Slide Images ─────────────────────────────────────────────────
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

def save_fig(fig, path):
    fig.savefig(path, dpi=100, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)

def fetch_person_photo(is_crash):
    """Download person photo from GitHub repo"""
    base = "https://raw.githubusercontent.com/systronics/ai360trading/master/public/image/"
    options = ["person_crash_1.jpg","person_crash_2.jpg","person_crash_3.jpg","person_crash_4.jpg"] if is_crash else ["person_green_1.jpg","person_green_2.jpg","person_green_3.jpg"]
    choice = options[datetime.now().timetuple().tm_yday % len(options)]
    try:
        resp = requests.get(base + choice, timeout=10)
        if resp.status_code == 200:
            from io import BytesIO
            from PIL import Image as PILImg
            return PILImg.open(BytesIO(resp.content)).convert("RGBA")
    except Exception as e:
        print(f"Photo fetch failed: {e}")
    return None

def process_person_photo(photo_img, is_crash=True):
    """Blur+tint background, keep face sharp"""
    from PIL import ImageEnhance as IE
    arr = np.array(photo_img).astype(np.float32)
    h, w = arr.shape[:2]
    cx, cy = w*0.50, h*0.44
    rx, ry = w*0.35, h*0.48
    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt(((X-cx)/rx)**2 + ((Y-cy)/ry)**2)
    person_mask = np.clip(1-(dist-0.75)/0.40, 0, 1)
    photo_rgb = photo_img.convert("RGB")
    blurred   = photo_rgb.filter(ImageFilter.GaussianBlur(radius=22))
    tint      = Image.new("RGB",(w,h),(180,20,20) if is_crash else (10,120,30))
    bg_tinted = Image.blend(blurred, tint, alpha=0.55)
    pm        = Image.fromarray((person_mask*255).astype(np.uint8),"L")
    pm        = pm.filter(ImageFilter.GaussianBlur(radius=18))
    result    = Image.composite(photo_rgb, bg_tinted, pm)
    result    = IE.Brightness(result).enhance(1.15)
    result    = IE.Contrast(result).enhance(1.10)
    result_rgba = result.convert("RGBA")
    fa = np.ones((h,w),dtype=np.float32)*255
    for x in range(min(60,w)):  fa[:,x] *= x/60
    for x in range(max(0,w-40),w): fa[:,x] *= (w-x)/40
    result_rgba.putalpha(Image.fromarray(fa.astype(np.uint8)))
    return result_rgba

def create_thumbnail(title, prices, pct_change, color, output_path):
    """Create eye-catching YouTube thumbnail with person photo"""
    from PIL import Image, ImageDraw as PILDraw, ImageFont, ImageFilter
    is_crash = pct_change < 0
    W, H = 1280, 720
    bg1 = (155,0,0) if is_crash else (0,120,20)
    bg2 = (8,0,0)   if is_crash else (0,12,3)
    canvas = Image.new("RGB",(W,H))
    d = PILDraw.Draw(canvas)
    for x in range(W):
        t=x/W; col=tuple(int(bg1[i]*(1-t)+bg2[i]*t) for i in range(3))
        d.line([(x,0),(x,H)],fill=col)
    # Candle watermark
    cl = Image.new("RGBA",(W,H),(0,0,0,0)); dc=PILDraw.Draw(cl); p=24500
    for i in range(18):
        o=p; c=o+random.uniform(-200,200)
        hh=max(o,c)+random.uniform(40,130); ll=min(o,c)-random.uniform(40,130)
        x=500+i*44; bull=c>=o; col=(80,220,80,45) if bull else (220,80,80,45)
        yo=int(560-(o-24100)*0.016); yc=int(560-(c-24100)*0.016)
        yh=int(560-(hh-24100)*0.016); yl=int(560-(ll-24100)*0.016)
        dc.line([(x,yh),(x,yl)],fill=col,width=2)
        dc.rectangle([x-9,min(yo,yc),x+9,max(yo,yc)+1],fill=col); p=c
    canvas = Image.alpha_composite(canvas.convert("RGBA"),cl).convert("RGB")
    # Person
    photo_img = fetch_person_photo(is_crash)
    if photo_img:
        person=process_person_photo(photo_img,is_crash)
        pw,ph=person.size; p_h=int(H*0.98); p_w=int(pw*(p_h/ph))
        person=person.resize((p_w,p_h),Image.LANCZOS)
        px_=W-p_w-5; py_=H-p_h
        sa=person.getchannel("A"); dark=Image.new("RGBA",(p_w,p_h),(0,0,0,160))
        dark.putalpha(sa); dark_b=dark.filter(ImageFilter.GaussianBlur(radius=20))
        sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.paste(dark_b,(px_+20,py_+20),dark_b)
        ca=canvas.convert("RGBA"); ca=Image.alpha_composite(ca,sh)
        ca.paste(person,(px_,py_),person); canvas=ca.convert("RGB")
    # Left overlay
    lo=Image.new("RGBA",(W,H),(0,0,0,0)); ld=PILDraw.Draw(lo)
    for x in range(650): a=int(100*(1-x/650)); ld.line([(x,0),(x,H)],fill=(0,0,0,a))
    canvas=Image.alpha_composite(canvas.convert("RGBA"),lo).convert("RGB")
    # Text
    draw=PILDraw.Draw(canvas)
    def pfont(size,bold=True):
        try:
            p="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            return ImageFont.truetype(p,size)
        except: return ImageFont.load_default()
    def sh_text(d,xy,txt,f,fill):
        d.text((xy[0]+5,xy[1]+5),txt,font=f,fill=(0,0,0,190)); d.text(xy,txt,font=f,fill=fill)
    headline2="CRASH !" if is_crash else "SURGING !"
    arrow_txt="▼" if is_crash else "▲"
    badge_col=(200,0,0) if is_crash else (0,150,20)
    txt_col2=(255,215,0) if is_crash else (120,255,100)
    sh_text(draw,(38,25),"NIFTY",pfont(105),(255,255,255))
    sh_text(draw,(38,128),headline2,pfont(122),txt_col2)
    draw.rounded_rectangle([38,272,435,340],radius=10,fill=badge_col)
    draw.text((55,280),f"{arrow_txt} {abs(pct_change):.2f}%  TODAY",font=pfont(37),fill=(255,255,255))
    draw.text((38,358),date_display,font=pfont(34,bold=False),fill=(210,210,210))
    topic="SUPPORT & RESISTANCE" if is_crash else "BUY OPPORTUNITY"
    draw.rounded_rectangle([38,408,38+len(topic)*17+30,474],radius=10,fill=(200,85,0))
    draw.text((55,416),topic,font=pfont(33),fill=(255,255,255))
    draw.text((38,490),"ai360trading.in",font=pfont(28,bold=False),fill=(120,180,255))
    draw.rectangle([0,666,W,H],fill=(0,0,0))
    draw.text((22,675),"AI360TRADING  |  Daily NIFTY & Market Analysis  |  @ai360trading",font=pfont(25),fill=(80,160,255))
    canvas.save(output_path,quality=96)
    print(f"  Thumbnail saved: {output_path}")

def create_candlestick_chart_slide(prices, title_label, color, output_path):
    """Create a real-looking candlestick chart with SR levels drawn"""
    price_data = prices.get('NIFTY 50', {})
    base  = price_data.get('price', 24000)
    pct   = price_data.get('pct', 0)

    # Generate 20 realistic OHLC candles
    np.random.seed(int(base) % 1000)
    opens, highs, lows, closes = [], [], [], []
    p = base * (1 - pct/100 * 3)
    for i in range(20):
        o = p
        c = o + np.random.normal(0, base * 0.004)
        h = max(o, c) + abs(np.random.normal(0, base * 0.002))
        l = min(o, c) - abs(np.random.normal(0, base * 0.002))
        opens.append(o); closes.append(c)
        highs.append(h); lows.append(l)
        p = c

    # Force last close to match live price
    closes[-1] = base
    highs[-1]  = max(opens[-1], base) * 1.003
    lows[-1]   = min(opens[-1], base) * 0.997

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(hex_to_rgb(BRAND_DARK))
    ax.set_facecolor('#1e293b')

    # Draw candles
    for i in range(20):
        bull = closes[i] >= opens[i]
        clr  = '#2ecc71' if bull else '#e74c3c'
        # Wick
        ax.plot([i, i], [lows[i], highs[i]], color=clr, linewidth=1.5, zorder=2)
        # Body
        body_h = abs(closes[i] - opens[i])
        body_y = min(opens[i], closes[i])
        rect = mpatches.Rectangle((i - 0.35, body_y), 0.7, max(body_h, base*0.001),
                                   color=clr, alpha=0.9, zorder=3)
        ax.add_patch(rect)

    # Support level
    s1 = base * 0.986
    ax.axhline(s1, color='#2ecc71', linewidth=2, linestyle='--', alpha=0.8, zorder=4)
    ax.text(20.2, s1, f'S1  {s1:,.0f}', color='#2ecc71',
            fontsize=11, fontweight='bold', va='center')

    # Resistance level
    r1 = base * 1.014
    ax.axhline(r1, color='#e74c3c', linewidth=2, linestyle='--', alpha=0.8, zorder=4)
    ax.text(20.2, r1, f'R1  {r1:,.0f}', color='#e74c3c',
            fontsize=11, fontweight='bold', va='center')

    # Current price line
    ax.axhline(base, color='white', linewidth=1.5, linestyle=':', alpha=0.6, zorder=4)
    ax.text(20.2, base, f'NOW {base:,.0f}', color='white',
            fontsize=11, fontweight='bold', va='center')

    # Shaded support zone
    ax.axhspan(s1 * 0.997, s1 * 1.003, alpha=0.08, color='#2ecc71')

    ax.set_xlim(-1, 23)
    ax.set_ylim(min(lows) * 0.997, max(highs) * 1.005)
    ax.spines['bottom'].set_color('#334155')
    ax.spines['left'].set_color('#334155')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#64748b', labelsize=9)
    ax.set_xticks([])
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))

    # Header
    pct_color = '#2ecc71' if pct >= 0 else '#e74c3c'
    arrow = '▲' if pct >= 0 else '▼'
    fig.text(0.04, 0.95, 'AI360TRADING', fontsize=12,
             fontweight='bold', color=hex_to_rgb(color), va='top')
    fig.text(0.5, 0.96, title_label, fontsize=16,
             fontweight='bold', color='white', ha='center', va='top')
    fig.text(0.96, 0.95, f'NIFTY  {arrow} {abs(pct):.2f}%',
             fontsize=14, fontweight='bold', color=pct_color,
             ha='right', va='top')
    fig.text(0.5, 0.02,
             'ai360trading.in  |  Subscribe for daily NIFTY analysis',
             fontsize=10, color='#475569', ha='center', va='bottom')

    plt.tight_layout(rect=[0, 0.04, 1, 0.93])
    save_fig(fig, output_path)

def create_sr_levels_slide(prices, color, output_path):
    """Create a clean support/resistance levels card — easy to read"""
    nifty = prices.get('NIFTY 50', {})
    btc   = prices.get('Bitcoin', {})
    sp500 = prices.get('S&P 500', {})
    base  = nifty.get('price', 24000)

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(hex_to_rgb(BRAND_DARK))
    ax.set_facecolor(hex_to_rgb(BRAND_DARK))

    # Title
    ax.text(0.5, 0.93, 'KEY LEVELS TO WATCH TODAY',
            transform=ax.transAxes, fontsize=20, fontweight='bold',
            color='white', ha='center', va='top')
    ax.text(0.03, 0.93, 'AI360TRADING', transform=ax.transAxes,
            fontsize=11, fontweight='bold',
            color=hex_to_rgb(color), ha='left', va='top')

    # NIFTY levels table
    levels = [
        ('NIFTY 50',  f"{base:,.0f}",     f"{base*0.986:,.0f}", f"{base*1.014:,.0f}", nifty.get('pct',0)),
        ('S&P 500',   f"{sp500.get('price',5500):,.0f}", f"{sp500.get('price',5500)*0.986:,.0f}", f"{sp500.get('price',5500)*1.014:,.0f}", sp500.get('pct',0)),
        ('Bitcoin',   f"${btc.get('price',65000):,.0f}", f"${btc.get('price',65000)*0.95:,.0f}",  f"${btc.get('price',65000)*1.05:,.0f}",  btc.get('pct',0)),
    ]

    headers = ['INSTRUMENT', 'PRICE', 'SUPPORT', 'RESISTANCE', 'CHANGE']
    col_x   = [0.08, 0.30, 0.48, 0.66, 0.84]
    y_hdr   = 0.76

    # Header row
    for h, x in zip(headers, col_x):
        ax.text(x, y_hdr, h, transform=ax.transAxes,
                fontsize=12, fontweight='bold', color='#94a3b8',
                ha='left', va='center')

    # Divider
    ax.plot([0.04, 0.96], [0.71, 0.71],
               color='#334155', linewidth=1, transform=ax.transAxes)

    # Data rows
    for i, (name, price_s, sup, res, pct) in enumerate(levels):
        y = 0.60 - i * 0.17
        pct_color = '#2ecc71' if pct >= 0 else '#e74c3c'
        arrow     = '▲' if pct >= 0 else '▼'

        # Row background
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.04, y - 0.06), 0.92, 0.12,
            boxstyle="round,pad=0.01",
            color='#1e293b', transform=ax.transAxes, zorder=1
        ))

        ax.text(col_x[0], y, name,  transform=ax.transAxes, fontsize=15,
                fontweight='bold', color='white',   ha='left', va='center')
        ax.text(col_x[1], y, price_s, transform=ax.transAxes, fontsize=15,
                fontweight='bold', color='white',   ha='left', va='center')
        ax.text(col_x[2], y, sup,   transform=ax.transAxes, fontsize=15,
                color='#2ecc71', ha='left', va='center', fontweight='bold')
        ax.text(col_x[3], y, res,   transform=ax.transAxes, fontsize=15,
                color='#e74c3c', ha='left', va='center', fontweight='bold')
        ax.text(col_x[4], y, f'{arrow} {abs(pct):.2f}%',
                transform=ax.transAxes, fontsize=15,
                color=pct_color, ha='left', va='center', fontweight='bold')

    # Legend
    ax.text(0.08, 0.10, '🟢 Support = BUY ZONE    🔴 Resistance = WATCH FOR REJECTION',
            transform=ax.transAxes, fontsize=12, color='#64748b',
            ha='left', va='center')
    ax.text(0.5, 0.03, f'ai360trading.in  |  {date_display}',
            transform=ax.transAxes, fontsize=10,
            color='#475569', ha='center', va='center')

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout(pad=0)
    save_fig(fig, output_path)

def create_fear_greed_slide(fg_val, fg_label, prices, color, output_path):
    """Create Fear & Greed gauge slide"""
    fig, (ax_gauge, ax_info) = plt.subplots(1, 2, figsize=(12.8, 7.2), dpi=100,
                                             gridspec_kw={'width_ratios': [1, 1]})
    fig.patch.set_facecolor(hex_to_rgb(BRAND_DARK))

    # ── Left: Gauge ──
    ax_gauge.set_facecolor(hex_to_rgb(BRAND_DARK))
    theta = np.linspace(np.pi, 0, 200)

    # Color arcs
    zones = [(0,25,'#e74c3c'), (25,45,'#e67e22'),
             (45,55,'#f1c40f'), (55,75,'#2ecc71'), (75,100,'#27ae60')]
    for lo, hi, zc in zones:
        t = np.linspace(np.pi * (1 - lo/100), np.pi * (1 - hi/100), 50)
        ax_gauge.plot(np.cos(t), np.sin(t), color=zc, linewidth=18, alpha=0.85)

    # Needle
    angle = np.pi * (1 - fg_val / 100)
    ax_gauge.annotate('', xy=(0.72*np.cos(angle), 0.72*np.sin(angle)),
                      xytext=(0, 0),
                      arrowprops=dict(arrowstyle='->', color='white', lw=3))

    # Value
    needle_color = '#e74c3c' if fg_val < 35 else '#f1c40f' if fg_val < 55 else '#2ecc71'
    ax_gauge.text(0, -0.25, str(fg_val), fontsize=48, fontweight='black',
                  color=needle_color, ha='center', va='center')
    ax_gauge.text(0, -0.5, fg_label.upper(), fontsize=16, fontweight='bold',
                  color=needle_color, ha='center', va='center')
    ax_gauge.text(0, 0.15, 'FEAR & GREED INDEX', fontsize=12,
                  color='#94a3b8', ha='center', va='center', fontweight='bold')
    ax_gauge.set_xlim(-1.2, 1.2); ax_gauge.set_ylim(-0.7, 1.1)
    ax_gauge.axis('off')

    # ── Right: Market data ──
    ax_info.set_facecolor(hex_to_rgb(BRAND_DARK))
    ax_info.text(0.5, 0.93, 'LIVE MARKET SNAPSHOT',
                 transform=ax_info.transAxes, fontsize=16,
                 fontweight='bold', color='white', ha='center', va='top')

    items = [
        ('NIFTY 50',  prices.get('NIFTY 50',  {}).get('display','N/A'), prices.get('NIFTY 50',{}).get('pct',0)),
        ('S&P 500',   prices.get('S&P 500',   {}).get('display','N/A'), prices.get('S&P 500',{}).get('pct',0)),
        ('Bitcoin',   prices.get('Bitcoin',   {}).get('display','N/A'), prices.get('Bitcoin',{}).get('pct',0)),
        ('Gold',      prices.get('Gold',       {}).get('display','N/A'), prices.get('Gold',{}).get('pct',0)),
    ]
    for i, (name, disp, pct) in enumerate(items):
        y = 0.74 - i * 0.155
        clr = '#2ecc71' if pct >= 0 else '#e74c3c'
        ax_info.add_patch(mpatches.FancyBboxPatch(
            (0.04, y - 0.055), 0.92, 0.11,
            boxstyle="round,pad=0.01", color='#1e293b',
            transform=ax_info.transAxes, zorder=1))
        ax_info.text(0.10, y, name, transform=ax_info.transAxes,
                     fontsize=14, color='#94a3b8', ha='left', va='center')
        ax_info.text(0.90, y, disp, transform=ax_info.transAxes,
                     fontsize=14, fontweight='bold', color=clr,
                     ha='right', va='center')

    ax_info.text(0.5, 0.04, f'ai360trading.in  |  {date_display}',
                 transform=ax_info.transAxes, fontsize=10,
                 color='#475569', ha='center', va='bottom')
    ax_info.set_xlim(0,1); ax_info.set_ylim(0,1)
    ax_info.axis('off')

    fig.text(0.5, 0.97, 'AI360TRADING  —  DAILY MARKET INTELLIGENCE',
             fontsize=13, fontweight='bold', color=hex_to_rgb(color),
             ha='center', va='top')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    save_fig(fig, output_path)

def create_content_slide(slide_text, narrator_text, color, slide_num, total, output_path, hindi_sub=""):
    """Content slide — English heading + Hindi subtitle"""
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(hex_to_rgb(BRAND_DARK))
    ax.set_facecolor(hex_to_rgb(BRAND_DARK))

    # Left accent bar
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.0, 0.0), 0.007, 1.0,
        boxstyle="round,pad=0", color=hex_to_rgb(color),
        transform=ax.transAxes, zorder=2))

    # Top bar
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.0, 0.92), 1.0, 0.08,
        boxstyle="round,pad=0", color='#0f1c2e',
        transform=ax.transAxes, zorder=1))
    ax.text(0.04, 0.96, 'AI360TRADING', transform=ax.transAxes,
            fontsize=12, fontweight='bold', color=hex_to_rgb(color),
            ha='left', va='center')
    ax.text(0.96, 0.96, f'{slide_num} / {total}', transform=ax.transAxes,
            fontsize=11, color='#475569', ha='right', va='center')

    # Main text — heading + body
    lines = slide_text.strip().split('\n')
    heading = lines[0] if lines else slide_text
    body    = '\n'.join(lines[1:]) if len(lines) > 1 else ''

    # Heading box
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.04, 0.62), 0.92, 0.26,
        boxstyle="round,pad=0.02", color='#1e293b',
        transform=ax.transAxes, zorder=1))
    ax.text(0.5, 0.75, textwrap.fill(heading, 50),
            transform=ax.transAxes, fontsize=24, fontweight='bold',
            color='white', ha='center', va='center', linespacing=1.2)

    # Body text
    if body:
        wrapped_body = textwrap.fill(body, 70)
        ax.text(0.08, 0.58, wrapped_body, transform=ax.transAxes,
                fontsize=15, color='#cbd5e1', ha='left', va='top',
                linespacing=1.5)

    # Hindi subtitle bar — orange accent, Hindi/Hinglish text
    if hindi_sub:
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.0, 0.16), 1.0, 0.10,
            boxstyle="round,pad=0", color='#1a0a00',
            transform=ax.transAxes, zorder=1))
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.0, 0.16), 0.004, 0.10,
            boxstyle="round,pad=0", color='#f97316',
            transform=ax.transAxes, zorder=2))
        ax.text(0.5, 0.21, hindi_sub, transform=ax.transAxes,
                fontsize=18, fontweight='bold',
                color='#fed7aa', ha='center', va='center')

    # Narrator quote bottom
    quote = narrator_text[:100] + '...' if len(narrator_text) > 100 else narrator_text
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.04, 0.03), 0.92, 0.12,
        boxstyle="round,pad=0.02", color='#0f1c2e',
        transform=ax.transAxes, zorder=1))
    ax.text(0.5, 0.09, f'"{quote}"', transform=ax.transAxes,
            fontsize=11, color='#64748b', ha='center', va='center',
            style='italic')

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout(pad=0)
    save_fig(fig, output_path)

def create_title_slide(title, subtitle, color, output_path):
    """Create branded title card"""
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(hex_to_rgb(BRAND_DARK))
    ax.set_facecolor(hex_to_rgb(BRAND_DARK))

    # Background gradient effect via stacked rectangles
    for i in range(20):
        alpha = 0.03 * (1 - i/20)
        ax.add_patch(mpatches.FancyBboxPatch(
            (0, i/20), 1, 0.05,
            boxstyle="round,pad=0", color=hex_to_rgb(color),
            transform=ax.transAxes, alpha=alpha))

    # Top accent bar
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.0, 0.91), 1.0, 0.09,
        boxstyle="round,pad=0", color=hex_to_rgb(color),
        transform=ax.transAxes, alpha=0.15))
    ax.text(0.5, 0.95, 'AI360TRADING', transform=ax.transAxes,
            fontsize=16, fontweight='bold', color=hex_to_rgb(color),
            ha='center', va='center')

    # Main title — very large
    wrapped = textwrap.fill(title, width=35)
    ax.text(0.5, 0.62, wrapped, transform=ax.transAxes,
            fontsize=32, fontweight='black', color='white',
            ha='center', va='center', linespacing=1.2)

    # Subtitle
    ax.text(0.5, 0.36, subtitle, transform=ax.transAxes,
            fontsize=17, color='#94a3b8', ha='center', va='center')

    # Date pill
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.35, 0.20), 0.30, 0.08,
        boxstyle="round,pad=0.02", color=hex_to_rgb(color),
        transform=ax.transAxes, alpha=0.2))
    ax.text(0.5, 0.24, f'📅 {date_display}', transform=ax.transAxes,
            fontsize=13, color=hex_to_rgb(color),
            ha='center', va='center', fontweight='bold')

    # Bottom bar
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.0, 0.0), 1.0, 0.10,
        boxstyle="round,pad=0", color='#0f1c2e',
        transform=ax.transAxes))
    ax.text(0.5, 0.05, 'ai360trading.in  |  t.me/ai360trading  |  @ai360trading',
            transform=ax.transAxes, fontsize=11,
            color='#475569', ha='center', va='center')

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout(pad=0)
    save_fig(fig, output_path)

def create_outro_slide(color, output_path):
    """Subscribe CTA outro"""
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(hex_to_rgb(BRAND_DARK))
    ax.set_facecolor(hex_to_rgb(BRAND_DARK))

    # Glow circle behind brand
    circle = plt.Circle((0.5, 0.72), 0.22, color=hex_to_rgb(color),
                         alpha=0.08, transform=ax.transAxes)
    ax.add_patch(circle)

    ax.text(0.5, 0.82, 'AI360TRADING', transform=ax.transAxes,
            fontsize=40, fontweight='black', color=hex_to_rgb(color),
            ha='center', va='center')
    ax.text(0.5, 0.65, '🔔  SUBSCRIBE for Daily Market Intelligence',
            transform=ax.transAxes, fontsize=20, fontweight='bold',
            color='white', ha='center', va='center')

    # 4 pillars
    pillars = [('📊', 'Stock Market'), ('₿', 'Bitcoin'),
               ('💰', 'Personal Finance'), ('🤖', 'AI Trading')]
    for i, (icon, label) in enumerate(pillars):
        x = 0.14 + i * 0.24
        ax.add_patch(mpatches.FancyBboxPatch(
            (x-0.09, 0.42), 0.18, 0.13,
            boxstyle="round,pad=0.02", color='#1e293b',
            transform=ax.transAxes))
        ax.text(x, 0.52, icon,  transform=ax.transAxes,
                fontsize=18, ha='center', va='center')
        ax.text(x, 0.45, label, transform=ax.transAxes,
                fontsize=11, color='#94a3b8', ha='center', va='center',
                fontweight='bold')

    ax.text(0.5, 0.32, '📣  Telegram: t.me/ai360trading',
            transform=ax.transAxes, fontsize=16,
            color=hex_to_rgb(BRAND_GREEN), ha='center', va='center',
            fontweight='bold')
    ax.text(0.5, 0.21, '🌐  ai360trading.in',
            transform=ax.transAxes, fontsize=16,
            color=hex_to_rgb(color), ha='center', va='center',
            fontweight='bold')
    ax.text(0.5, 0.09,
            '⚠️ Educational content only. Not financial advice.',
            transform=ax.transAxes, fontsize=11,
            color='#475569', ha='center', va='center')

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout(pad=0)
    save_fig(fig, output_path)

# ─── 5. Text to Speech ────────────────────────────────────────────────────────
def text_to_speech(text, output_path, lang='en', tld='co.in'):
    """Convert text to MP3 using gTTS — Indian English accent"""
    try:
        clean = text.replace("₹", "rupees ").replace("$", "dollars ")
        clean = clean.replace("%", " percent").replace("&", " and ")
        clean = clean.replace("|", ". ").replace("→", " ")
        clean = clean.replace("▲", "up ").replace("▼", "down ")
        clean = clean.replace("—", ", ").replace("...", ". ")
        clean = clean.replace("**", "").replace("##", "").replace("*", "")
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
    nifty_pct_abs = abs(prices.get("NIFTY 50", {}).get("pct", 0))
    btc_price_fmt = f"{int(prices.get('Bitcoin', {}).get('price', 65000)):,}"
    title = topic["title_template"].format(
        date=date_display,
        year=now.year,
        pct=f"{nifty_pct_abs:.1f}",
        btc=btc_price_fmt,
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

    # Slide 1 — Fear & Greed + live snapshot (all topics)
    fg_slide_path = os.path.join(OUTPUT_DIR, "slide_01_fg.png")
    create_fear_greed_slide(fg_val, fg_label, prices, color, fg_slide_path)
    slide_image_paths.append(fg_slide_path)
    script_slides.insert(1, {
        "narrator": f"Before we dive in — the Fear and Greed index is currently at {fg_val}, showing {fg_label}. NIFTY is at {prices.get('NIFTY 50',{}).get('display','N/A')}, S&P 500 at {prices.get('S&P 500',{}).get('display','N/A')}, and Bitcoin at {prices.get('Bitcoin',{}).get('display','N/A')}.",
        "slide": "Fear & Greed"
    })

    # Slide 2 — Candlestick chart (for market topics)
    if topic["type"] in ["nifty_analysis", "weekly_outlook", "top5_stocks"]:
        chart_path = os.path.join(OUTPUT_DIR, "slide_02_chart.png")
        create_candlestick_chart_slide(prices, f"NIFTY 50 — {date_display}", color, chart_path)
        slide_image_paths.append(chart_path)
        script_slides.insert(2, {
            "narrator": f"Here is the NIFTY 50 candlestick chart. Current price is {prices.get('NIFTY 50',{}).get('display','N/A')}. The green dashed line is support and the red dashed line is resistance. Watch these levels closely today.",
            "slide": "NIFTY Chart"
        })

    # Slide 3 — SR Levels table (market topics)
    if topic["type"] in ["nifty_analysis", "bitcoin_analysis", "weekly_outlook"]:
        sr_path = os.path.join(OUTPUT_DIR, "slide_03_sr.png")
        create_sr_levels_slide(prices, color, sr_path)
        slide_image_paths.append(sr_path)
        script_slides.insert(3, {
            "narrator": f"Here are the exact key levels for today. NIFTY support at {prices.get('NIFTY 50',{}).get('price',24000)*0.986:,.0f} and resistance at {prices.get('NIFTY 50',{}).get('price',24000)*1.014:,.0f}. Bitcoin support at {prices.get('Bitcoin',{}).get('price',65000)*0.95:,.0f} and resistance at {prices.get('Bitcoin',{}).get('price',65000)*1.05:,.0f}.",
            "slide": "Key Levels"
        })

    # Content slides from script
    for i, slide in enumerate(script_slides[4:], start=4):
        img_path = os.path.join(OUTPUT_DIR, f"slide_{i:02d}_content.png")
        create_content_slide(
            slide.get("slide", slide.get("narrator","")[:80]),
            slide.get("narrator", ""),
            color, i, len(script_slides), img_path,
            hindi_sub=slide.get("hindi_sub", "")
        )
        slide_image_paths.append(img_path)

    # Outro slide
    outro_path = os.path.join(OUTPUT_DIR, "slide_outro.png")
    create_outro_slide(color, outro_path)
    slide_image_paths.append(outro_path)
    script_slides.append({
        "narrator": "That is all for today's analysis from AI360Trading. If you found this helpful please subscribe and hit the bell icon for daily market intelligence. Visit ai360trading.in for full written reports and join our Telegram at t.me/ai360trading. See you tomorrow.",
        "slide": "Outro"
    })

    # Generate thumbnail — separate high-quality image
    nifty_pct    = prices.get('NIFTY 50', {}).get('pct', 0)
    thumb_path   = os.path.join(OUTPUT_DIR, "thumbnail.png")
    create_thumbnail(title, prices, nifty_pct, color, thumb_path)
    print(f"  ✅ Thumbnail created")

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
        thumbnail_path=thumb_path
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
