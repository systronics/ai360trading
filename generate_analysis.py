"""
generate_analysis.py — Part 1: Daily Market Analysis Video
===========================================================
Fixes applied (April 2026):
  Fix 1 — Searchable YouTube titles: Topic + Date + Channel name enforced in prompt
  Fix 2 — 14 slides (~9-11 min video) for mid-roll ad eligibility (needs 8+ min)
  Fix 3 — 200+ word structured description with keywords
  Fix 4 — Auto playlist assignment after upload
  Fix 5 — End screen added to every video (subscribe + latest video + Telegram)

Self-healing AI chain (no single point of failure):
  Groq → Gemini → Claude → OpenAI → Template fallback
  Family can never be locked out due to one API going down.

This system is built to run forever. Do not break this chain.
"""

import os, sys, json, asyncio, textwrap, time
from datetime import datetime
from pathlib import Path

import edge_tts
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip,
    concatenate_videoclips, concatenate_audioclips
)

# YouTube upload
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── CONFIG ──────────────────────────────────────────────────────────────────

OUT       = Path("output")
MUSIC_DIR = Path("public/music")
W, H      = 1920, 1080
FPS       = 24
VOICE     = "hi-IN-SwaraNeural"
CHANNEL   = "AI360 Trading"
NUM_SLIDES = 14          # Fix 2: 14 slides × ~45s each ≈ 10+ minutes

os.makedirs(OUT, exist_ok=True)
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

# ─── PLAYLIST IDs ────────────────────────────────────────────────────────────
# Fix 4: Set these to your actual YouTube playlist IDs.
# Go to YouTube Studio → Playlists → click a playlist → copy ID from URL.
# If a playlist doesn't exist yet, create it manually once in YouTube Studio,
# then paste the ID here. The system will add every video automatically forever.
PLAYLIST_IDS = {
    "analysis":  os.environ.get("PLAYLIST_NIFTY_ANALYSIS", ""),   # "Nifty50 Daily Analysis"
    "swing":     os.environ.get("PLAYLIST_SWING_TRADE", ""),       # "Swing Trade Setups"
    "weekly":    os.environ.get("PLAYLIST_WEEKLY_OUTLOOK", ""),    # "Weekly Outlook"
    "zeno":      os.environ.get("PLAYLIST_ZENO_WISDOM", ""),       # "ZENO Market Wisdom"
}

# ─── FONTS ───────────────────────────────────────────────────────────────────

FONT_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
]
FONT_REG_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

# ─── THEME ───────────────────────────────────────────────────────────────────

THEMES = {
    "bullish": {
        "bg_top": (5, 30, 15),  "bg_bot": (10, 60, 30),
        "accent": (0, 220, 110), "text": (235, 255, 245),
        "subtext": (160, 220, 180), "bar": (0, 180, 90)
    },
    "bearish": {
        "bg_top": (35, 10, 10), "bg_bot": (70, 20, 20),
        "accent": (255, 60, 60), "text": (255, 240, 240),
        "subtext": (220, 160, 160), "bar": (200, 40, 40)
    },
    "neutral": {
        "bg_top": (10, 20, 40), "bg_bot": (20, 40, 80),
        "accent": (0, 180, 255), "text": (240, 250, 255),
        "subtext": (160, 200, 230), "bar": (0, 140, 210)
    },
}

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ─── LIVE DATA FETCHING ──────────────────────────────────────────────────────

def fetch_market_data():
    """Fetch live global market data to ground the AI script in real numbers."""
    print("📈 Fetching live market data...")
    summary = {}
    try:
        tickers = {
            "Nifty50":   "^NSEI",
            "BankNifty": "^NSEBANK",
            "S&P500":    "^GSPC",
            "Bitcoin":   "BTC-USD",
            "Gold":      "GC=F",
            "Crude Oil": "CL=F",
        }
        for name, sym in tickers.items():
            try:
                t    = yf.Ticker(sym)
                hist = t.history(period="2d")
                if not hist.empty and len(hist) >= 2:
                    price  = hist["Close"].iloc[-1]
                    prev   = hist["Close"].iloc[-2]
                    change = price - prev
                    pct    = (change / prev) * 100
                    summary[name] = {"price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2)}
                else:
                    summary[name] = {"price": "N/A", "change": 0, "pct": 0}
            except Exception as e:
                print(f"  ⚠️ {name} fetch failed: {e}")
                summary[name] = {"price": "N/A", "change": 0, "pct": 0}
    except Exception as e:
        print(f"⚠️ Market data error: {e}")

    lines = []
    for name, d in summary.items():
        if d["price"] != "N/A":
            arrow = "▲" if d["pct"] >= 0 else "▼"
            lines.append(f"- {name}: {d['price']} ({arrow}{abs(d['pct']):.2f}%)")
        else:
            lines.append(f"- {name}: Data unavailable")
    return "\n".join(lines), summary

# ─── SELF-HEALING AI CLIENT ──────────────────────────────────────────────────
# This chain tries every AI provider in order.
# If all fail, it uses a template. The system NEVER goes down.

def _try_groq(prompt, max_tokens=3000):
    """Primary: Groq llama-3.3-70b (fastest, free)"""
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=max_tokens
        )
        data = json.loads(resp.choices[0].message.content)
        print("✅ AI generated via Groq")
        return data
    except Exception as e:
        print(f"⚠️ Groq failed: {e}")
        return None

def _try_gemini(prompt):
    """Secondary: Google Gemini 2.0 Flash"""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        resp  = model.generate_content(
            f"Respond ONLY with valid JSON, no markdown, no backticks:\n\n{prompt}"
        )
        text = resp.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text.strip())
        print("✅ AI generated via Gemini")
        return data
    except Exception as e:
        print(f"⚠️ Gemini failed: {e}")
        return None

def _try_claude(prompt):
    """Tertiary: Anthropic Claude Haiku"""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": f"Respond ONLY with valid JSON, no markdown:\n\n{prompt}"
            }]
        )
        text = msg.content[0].text.strip()
        data = json.loads(text)
        print("✅ AI generated via Claude")
        return data
    except Exception as e:
        print(f"⚠️ Claude failed: {e}")
        return None

def _try_openai(prompt):
    """Quaternary: OpenAI GPT-4o-mini"""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=3000
        )
        data = json.loads(resp.choices[0].message.content)
        print("✅ AI generated via OpenAI")
        return data
    except Exception as e:
        print(f"⚠️ OpenAI failed: {e}")
        return None

def generate_with_fallback(prompt):
    """Try all 4 AI providers in order. Never fails."""
    for fn in [_try_groq, _try_gemini, _try_claude, _try_openai]:
        result = fn(prompt) if fn != _try_groq else fn(prompt, 3500)
        if result and isinstance(result, dict) and result.get("slides"):
            return result
    print("⚠️ All AI providers failed — using template fallback")
    return None

# ─── TITLE BUILDER ────────────────────────────────────────────────────────────
# Fix 1: Central searchable title builder.
# Format: "[Topic keyword] [DD Month YYYY] | [Hook] | AI360 Trading"
# People search "Nifty analysis today" or "best stocks this week" — not "ZENO Wisdom".

def build_searchable_title(topic_keyword, date_str, hook, is_weekend=False):
    """
    Builds a YouTube-SEO-optimised title.
    Max 100 chars (YouTube limit).
    Always ends with | AI360 Trading so the channel is searchable.
    """
    if is_weekend:
        base = f"{topic_keyword} {date_str} | {hook} | AI360 Trading"
    else:
        base = f"Nifty50 Analysis {date_str} | {hook} | AI360 Trading"

    # Hard truncate at 95 chars to leave buffer, keeping channel name
    if len(base) > 95:
        # Shorten the hook, keep channel name
        max_hook = 95 - len(f"Nifty50 Analysis {date_str} |  | AI360 Trading")
        hook_short = hook[:max(10, max_hook)]
        base = f"Nifty50 Analysis {date_str} | {hook_short} | AI360 Trading"

    return base[:100]

# ─── DESCRIPTION BUILDER ─────────────────────────────────────────────────────
# Fix 3: Rich 200+ word structured description for every video.

def build_full_description(ai_desc, market_summary, date_str, sentiment, is_weekend):
    """
    Builds a structured 200+ word YouTube description.
    Includes keywords for India + global audience SEO.
    """
    mood_emoji = {"bullish": "📈", "bearish": "📉", "neutral": "📊"}.get(sentiment, "📊")
    mood_text  = {"bullish": "Bullish", "bearish": "Bearish", "neutral": "Neutral"}.get(sentiment, "Neutral")

    # Build market data lines
    market_lines = []
    for name, d in market_summary.items():
        if d["price"] != "N/A":
            arrow = "▲" if d["pct"] >= 0 else "▼"
            market_lines.append(f"  • {name}: {d['price']} ({arrow}{abs(d['pct']):.2f}%)")
    market_block = "\n".join(market_lines) if market_lines else "  • Live data not available today"

    if is_weekend:
        context = "Weekend special: Global markets + wealth-building strategies for Indian retail investors."
    else:
        context = "Daily Nifty50 market analysis with live data, key levels, swing trade setups, and FII activity."

    desc = f"""{ai_desc}

{mood_emoji} Today's Market Mood: {mood_text} | Date: {date_str}

📊 LIVE MARKET SNAPSHOT:
{market_block}

🎯 WHAT YOU WILL LEARN IN THIS VIDEO:
  • Nifty50 key support and resistance levels for today
  • Best swing trade setups from Nifty200 stocks
  • Global market impact on Indian stocks (US, UK, Bitcoin)
  • FII and DII activity analysis
  • Risk management for retail traders

{context}

🔔 SUBSCRIBE for daily market analysis — posted every morning before market opens.
📱 FREE Telegram signals: https://t.me/ai360trading
📊 Advance signals (₹499/month): https://t.me/ai360trading_Advance
🌐 Website + articles: https://ai360trading.in
📘 Facebook: https://facebook.com/ai360trading

⚠️ DISCLAIMER: This channel is for educational purposes only. AI360 Trading is not a SEBI registered investment advisor. Do your own research before investing. Past performance is not a guarantee of future results.

#Nifty50 #NiftyAnalysis #StockMarketIndia #TradingIndia #SwingTrading #BankNifty #NSE #BSE #MarketAnalysis #AI360Trading #TradingHindi #ShareMarket #StockMarket #Investing #Finance #TechnicalAnalysis #USStocks #GlobalMarkets #FII #Nifty"""

    return desc

# ─── SCRIPT GENERATOR ────────────────────────────────────────────────────────

def generate_slides(market_data_str, market_summary):
    today       = datetime.now().strftime("%A, %d %B %Y")
    date_str    = datetime.now().strftime("%d %B %Y")
    today_fmt   = datetime.now().strftime("%d %b %Y")  # for title
    is_weekend  = datetime.now().weekday() >= 5

    if is_weekend:
        market_context = "Weekend global market recap and wealth-building education for Indian and global traders."
        title_keyword  = "Global Market Weekend"
        hook_hint      = "Weekend Market Review"
    else:
        market_context = f"Today's live Nifty50 and global market data:\n{market_data_str}\nAnalyse these exact levels — do not invent numbers."
        title_keyword  = "Nifty50 Market"
        hook_hint      = "Best Swing Trade Setups Today"

    # Fix 1 instruction baked into the prompt
    title_instruction = f"""
"video_title" MUST follow this EXACT format (max 95 chars):
  "Nifty50 Analysis {today_fmt} | [2-4 word market insight] | AI360 Trading"
Examples of GOOD titles:
  "Nifty50 Analysis {today_fmt} | Best Swing Setups Today | AI360 Trading"
  "Nifty50 Analysis {today_fmt} | Market at Key Support | AI360 Trading"
  "Nifty50 Analysis {today_fmt} | Breakout or Breakdown? | AI360 Trading"
NEVER generate titles like "ZENO Wisdom" or "Aaj Ka Update" — those are unsearchable.
People search "Nifty analysis today" — your title must match that search intent.
"""

    # Fix 3 instruction for description
    desc_instruction = """
"video_description" must be 3-5 sentences, 80-100 words, in Hinglish.
Cover: what the video analyses, who it is for, what they will learn.
Do NOT include links — they are added automatically.
"""

    prompt = f"""You are an expert Indian market analyst creating a professional YouTube video script in Hinglish for AI360 Trading channel.

Today is {today}.

USE THIS LIVE DATA — do not invent market prices:
{market_context}

{title_instruction}

{desc_instruction}

Generate exactly {NUM_SLIDES} slides covering: market overview, global signals, Nifty key levels, sector analysis, FII/DII activity, top stock setups (3-4 stocks), risk management, and a motivational close.

Respond ONLY with valid JSON:
{{
  "video_title": "exact format shown above",
  "video_description": "80-100 word Hinglish description",
  "overall_sentiment": "bullish or bearish or neutral",
  "slides": [
    {{
      "title": "slide heading max 8 words",
      "content": "spoken Hinglish content 55-70 words — use the live data numbers above",
      "sentiment": "bullish or bearish or neutral",
      "key_points": ["point 1", "point 2", "point 3"]
    }}
  ]
}}"""

    print("🤖 Generating market analysis script...")
    data = generate_with_fallback(prompt)

    if not data:
        data = _fallback_slides(date_str, is_weekend)

    # Fix 1: Override title with our builder regardless of what AI returned
    raw_title   = data.get("video_title", "")
    # Check if AI followed the format; if not, rebuild
    if "AI360 Trading" not in raw_title or date_str[:6] not in raw_title:
        sentiment   = data.get("overall_sentiment", "neutral")
        hooks       = {
            "bullish": "Breakout Stocks to Watch",
            "bearish": "Key Support Levels Today",
            "neutral": "Best Swing Trade Setups"
        }
        hook        = hooks.get(sentiment, "Market Analysis Today")
        data["video_title"] = build_searchable_title(title_keyword, today_fmt, hook, is_weekend)

    print(f"📌 Title: {data['video_title']}")
    return data, is_weekend, date_str, market_summary

def _fallback_slides(date_str, is_weekend):
    """Emergency fallback — system never stops."""
    slides = []
    topics = [
        ("Market Overview", "Aaj ke market ka overview dekhte hain. Global markets mixed hain aur Nifty key levels pe trade kar raha hai. FII activity neutral hai aaj. Important hai ki hum key support aur resistance levels pe dhyan rakhein."),
        ("Global Signals", "US markets kal mixed close hue. S&P 500 stable raha. Bitcoin aur Gold pe bhi nazar rakhni chahiye kyunki yeh Indian sentiment ko affect karte hain. Global uncertainty mein Gold safe haven hai."),
        ("Nifty Key Levels", "Nifty ke liye aaj key support 22000 pe hai aur resistance 22500 pe. In levels ko tod ke close hona important hai trend confirm karne ke liye. Volume confirmation zaroori hai."),
        ("Bank Nifty Analysis", "Bank Nifty financial stocks ke saath strongly correlated hai. RBI policy aur banking sector results pe nazar rakhein. Support aur resistance levels ke paas trade setup dhundhe."),
        ("Sector Analysis", "IT, Pharma, aur Banking sectors pe focus karo aaj. IT stocks US dollar ke saath correlated hain. Pharma defensive play hai bear market mein. Banking sector rate sensitive hai."),
        ("FII DII Activity", "Foreign Institutional Investors ka flow market direction determine karta hai. Net buying bearish market mein bullish signal hai. DII domestic support dete hain volatility mein."),
        ("Top Stock Setup 1", "Swing trade setup ke liye stocks dhundhne ka best tarika: 52-week high ke paas stocks, strong fundamentals ke saath. Entry, stop loss aur target pehle decide karo."),
        ("Top Stock Setup 2", "Second setup: Support pe rebound karne wale stocks. Volume increase ke saath price bounce chahiye. Risk-reward ratio 1:2 se kam ka trade avoid karo."),
        ("Top Stock Setup 3", "Third setup: Sector rotation play. Strong sector mein leader stock. Relative strength index 50 se upar hona chahiye. Trend follow karo, counter trend avoid karo."),
        ("Options Setup", "Option buyers ke liye: ATM strike, 30+ days expiry. Option sellers: OTM strike, collect premium. Greeks samajhna zaroori hai. Expiry week mein extra caution rakhein."),
        ("Risk Management", "Har trade mein stop loss mandatory hai. Account ka 1-2% se zyada risk mat lo ek trade mein. Consecutive losses pe position size reduce karo. Capital preservation sabse pehle."),
        ("Weekly Outlook", "Is hafte ke liye key events: macroeconomic data, FII flows. Weekend pe apni watchlist update karo. Next week ke liye positions plan karo calmly without market pressure."),
        ("Telegram Signals", "AI360 Trading ke free Telegram channel pe daily signals milte hain. Advance channel pe full entry exit aur TSL alerts milte hain. Link description mein hai."),
        ("Closing Thoughts", "Trading ek marathon hai sprint nahi. Consistent process follow karo. Ek buri trade se discourage mat ho. Subscribe karo daily analysis ke liye. Apna dhyan rakhein, market phir aayega."),
    ]
    slides_data = []
    for title, content in topics[:NUM_SLIDES]:
        slides_data.append({
            "title": title,
            "content": content,
            "sentiment": "neutral",
            "key_points": ["Analysis", "Setup", "Risk Management"]
        })
    return {
        "video_title": f"Nifty50 Analysis {date_str} | Market Overview Today | AI360 Trading",
        "video_description": f"Aaj {date_str} ka complete Nifty50 market analysis. Key levels, swing trade setups, aur risk management ke saath. AI360 Trading pe daily analysis milta hai.",
        "overall_sentiment": "neutral",
        "slides": slides_data
    }

# ─── SLIDE RENDERER ──────────────────────────────────────────────────────────

def make_slide(slide, idx, total, path):
    snt = slide.get("sentiment", "neutral").lower()
    if snt not in THEMES:
        snt = "neutral"
    th = THEMES[snt]

    img = Image.new("RGB", (W, H))
    px  = img.load()
    for y in range(H):
        c = lerp(th["bg_top"], th["bg_bot"], y / H)
        for x in range(W):
            px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")

    # Top accent bar
    draw.rectangle([(0, 0), (W, 10)], fill=th["accent"])

    # Channel watermark + slide counter
    draw.text((W - 40, 30), "ai360trading.in",
              fill=(*th["subtext"], 180), font=get_font(FONT_REG_PATHS, 28), anchor="ra")
    draw.text((40, 35), f"{idx} / {total}",
              fill=(*th["subtext"], 200), font=get_font(FONT_BOLD_PATHS, 32), anchor="la")

    # Title
    title_font  = get_font(FONT_BOLD_PATHS, 72)
    title_lines = textwrap.wrap(slide["title"].upper(), width=28)
    ty = 140
    for line in title_lines[:2]:
        draw.text((W // 2, ty), line, fill=th["text"], font=title_font, anchor="mm")
        ty += 88

    # Divider
    draw.rectangle([(80, ty + 20), (W - 80, ty + 24)], fill=th["accent"])
    ty += 60

    # Content
    content_font  = get_font(FONT_REG_PATHS, 42)
    content_lines = textwrap.wrap(slide["content"], width=55)
    for line in content_lines[:6]:
        draw.text((80, ty), line, fill=th["text"], font=content_font)
        ty += 58

    # Key points
    if slide.get("key_points"):
        ty += 30
        bullet_font = get_font(FONT_BOLD_PATHS, 38)
        for pt in slide["key_points"][:3]:
            draw.text((80, ty), f"▶ {pt}", fill=th["accent"], font=bullet_font)
            ty += 52

    # Bottom bar
    draw.rectangle([(0, H - 10), (W, H)], fill=th["accent"])
    img.save(str(path), quality=95)

# ─── VOICE ───────────────────────────────────────────────────────────────────

async def gen_voice(text, path):
    await edge_tts.Communicate(text, VOICE).save(str(path))

# ─── BACKGROUND MUSIC ────────────────────────────────────────────────────────

def get_bg_music():
    day       = datetime.now().weekday()
    music_map = {0: "bgmusic1.mp3", 1: "bgmusic2.mp3", 2: "bgmusic3.mp3",
                 3: "bgmusic1.mp3", 4: "bgmusic2.mp3", 5: "bgmusic3.mp3", 6: "bgmusic1.mp3"}
    f = MUSIC_DIR / music_map[day]
    if f.exists():
        return f
    for f in MUSIC_DIR.glob("*.mp3"):
        return f
    return None

# ─── YOUTUBE SERVICE ─────────────────────────────────────────────────────────

def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json and os.path.exists("token.json"):
            with open("token.json") as f:
                creds_json = f.read()
        if not creds_json:
            return None
        info  = json.loads(creds_json)
        creds = Credentials.from_authorized_user_info(info)
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"❌ YouTube auth error: {e}")
        return None

def upload_to_youtube(video_path, title, description, tags):
    youtube = get_youtube_service()
    if not youtube:
        return None

    body = {
        "snippet": {
            "title":       title[:100],
            "description": description[:4900],   # YouTube limit is 5000
            "tags":        tags,
            "categoryId":  "27"                  # 27 = Education
        },
        "status": {
            "privacyStatus":         "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"🚀 Uploading: {title[:70]}...")
    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  Uploaded {int(status.progress() * 100)}%")
        video_id = response["id"]
        print(f"✅ YouTube upload success! ID: {video_id}")
        return video_id
    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        return None

# ─── FIX 4: PLAYLIST ASSIGNMENT ──────────────────────────────────────────────

def add_to_playlist(youtube, video_id, playlist_id, playlist_name):
    """Add a video to a YouTube playlist. Safe — if it fails, video is still live."""
    if not playlist_id or not video_id:
        print(f"⚠️ Playlist '{playlist_name}': ID not set in GitHub Secrets — skipping")
        return False
    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind":    "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        ).execute()
        print(f"✅ Added to playlist: {playlist_name}")
        return True
    except Exception as e:
        print(f"⚠️ Playlist '{playlist_name}' failed (non-critical): {e}")
        return False

def assign_to_playlists(youtube, video_id, sentiment):
    """Fix 4: Assign every analysis video to the correct playlists."""
    if not youtube or not video_id:
        return
    # Always add to Nifty Analysis playlist
    add_to_playlist(youtube, video_id, PLAYLIST_IDS["analysis"], "Nifty50 Daily Analysis")
    # Add to swing trade playlist (analysis always has setups)
    add_to_playlist(youtube, video_id, PLAYLIST_IDS["swing"], "Swing Trade Setups")
    # Add to weekly outlook on Fridays
    if datetime.now().weekday() == 4:
        add_to_playlist(youtube, video_id, PLAYLIST_IDS["weekly"], "Weekly Outlook")

# ─── FIX 5: END SCREEN ───────────────────────────────────────────────────────

def add_end_screen(youtube, video_id, video_duration_seconds):
    """
    Fix 5: Add a 20-second end screen to every video.
    Shows: Subscribe button + promote latest video.
    End screen needs video to be at least 25 seconds long.
    YouTube API: endScreens.insert() requires OAuth with youtube.force-ssl scope.
    If it fails for any reason, video is already live — non-critical.
    """
    if not youtube or not video_id:
        return
    if video_duration_seconds < 25:
        print("⚠️ Video too short for end screen — skipping")
        return

    end_ms  = int(video_duration_seconds * 1000)
    start_ms = end_ms - 20000   # 20 seconds before end

    try:
        youtube.videos().update(
            part="endScreens",
            body={
                "id": video_id,
                "endScreens": {
                    "elements": [
                        {
                            "type":             "SUBSCRIBE",
                            "left":             0.4,
                            "top":              0.6,
                            "width":            0.2,
                            "startOffsetMs":    start_ms,
                            "endOffsetMs":      end_ms
                        },
                        {
                            "type":             "RECENT_UPLOAD",
                            "left":             0.65,
                            "top":              0.4,
                            "width":            0.3,
                            "startOffsetMs":    start_ms,
                            "endOffsetMs":      end_ms
                        }
                    ]
                }
            }
        ).execute()
        print("✅ End screen added (subscribe + latest video)")
    except Exception as e:
        # End screen API sometimes needs additional OAuth scope.
        # Non-critical — video is already live and earning.
        print(f"⚠️ End screen failed (non-critical): {e}")
        print("   To fix: re-authorise YouTube OAuth with youtube.force-ssl scope")

# ─── MAIN ────────────────────────────────────────────────────────────────────

async def run():
    today_str = datetime.now().strftime("%Y%m%d")
    date_fmt  = datetime.now().strftime("%d %B %Y")

    # 1. Fetch live market data
    market_data_str, market_summary = fetch_market_data()

    # 2. Generate script with self-healing AI chain
    data, is_weekend, date_str, market_sum = generate_slides(
        market_data_str, market_summary
    )

    slides    = data["slides"][:NUM_SLIDES]   # cap at NUM_SLIDES
    sentiment = data.get("overall_sentiment", "neutral")
    vid_title = data["video_title"]

    # Fix 3: Build rich structured description
    ai_desc  = data.get("video_description", "")
    full_desc = build_full_description(ai_desc, market_sum, date_fmt, sentiment, is_weekend)

    # SEO tags — India + global
    tags = [
        "Nifty50", "NiftyAnalysis", "StockMarketIndia", "BankNifty",
        "TradingIndia", "SwingTrading", "TechnicalAnalysis", "NSE", "BSE",
        "AI360Trading", "ShareMarket", "MarketAnalysis", "TradingHindi",
        "USStocks", "GlobalMarkets", "FII", "StockMarket", "Finance",
        "Investing", "FinancialLiteracy"
    ]

    # 3. Build slides + voice
    print(f"\n🎬 Building {len(slides)} slides...")
    clips          = []
    total_duration = 0.0

    for i, s in enumerate(slides):
        img_path   = OUT / f"an_{i}.png"
        audio_path = OUT / f"an_{i}.mp3"

        make_slide(s, i + 1, len(slides), img_path)
        await gen_voice(s["content"], audio_path)

        voice_clip     = AudioFileClip(str(audio_path))
        slide_duration = voice_clip.duration + 0.8
        total_duration += slide_duration

        bg_path = get_bg_music()
        if bg_path:
            try:
                bg = AudioFileClip(str(bg_path))
                if bg.duration < slide_duration:
                    loops = int(slide_duration / bg.duration) + 1
                    bg    = concatenate_audioclips([bg] * loops)
                bg           = bg.subclip(0, slide_duration).volumex(0.07)
                slide_audio  = CompositeAudioClip([voice_clip, bg])
            except Exception as e:
                print(f"⚠️ Music error slide {i}: {e}")
                slide_audio = voice_clip
        else:
            slide_audio = voice_clip

        clip = ImageClip(str(img_path)).set_duration(slide_duration).set_audio(slide_audio)
        clips.append(clip)
        print(f"  Slide {i+1}/{len(slides)} ready ({slide_duration:.1f}s)")

    print(f"\n⏱️ Total estimated duration: {total_duration:.0f}s ({total_duration/60:.1f} min)")
    if total_duration < 480:
        print("⚠️ WARNING: Video under 8 minutes — mid-roll ads will not activate")

    # 4. Render video
    video_path = OUT / "analysis_video.mp4"
    print(f"\n🎥 Rendering video...")
    concatenate_videoclips(clips, method="compose").write_videofile(
        str(video_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(OUT / "temp_an_audio.aac"),
        remove_temp=True,
        logger=None
    )
    print(f"✅ Video rendered: {video_path}")

    # 5. Upload to YouTube
    video_id = upload_to_youtube(video_path, vid_title, full_desc, tags)

    # 6. Post-upload: playlists + end screen + save meta
    youtube = get_youtube_service()
    if video_id and youtube:
        # Fix 4: Playlists
        assign_to_playlists(youtube, video_id, sentiment)
        # Fix 5: End screen
        add_end_screen(youtube, video_id, total_duration)

    # 7. Save video ID for generate_education.py
    if video_id:
        (OUT / "analysis_video_id.txt").write_text(video_id, encoding="utf-8")
        video_url = f"https://youtube.com/watch?v={video_id}"
    else:
        (OUT / "analysis_video_id.txt").write_text("UPLOAD_FAILED", encoding="utf-8")
        video_url = ""

    # 8. Save metadata
    meta = {
        "title":       vid_title,
        "description": full_desc,
        "video_id":    video_id or "UPLOAD_FAILED",
        "video_url":   video_url,
        "sentiment":   sentiment,
        "duration_s":  round(total_duration),
        "slides":      len(slides),
        "date":        today_str
    }
    (OUT / f"analysis_meta_{today_str}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n📋 Summary:")
    print(f"   Title:    {vid_title}")
    print(f"   Duration: {total_duration/60:.1f} min")
    print(f"   Slides:   {len(slides)}")
    print(f"   Video ID: {video_id or 'FAILED'}")
    print(f"✅ generate_analysis.py complete")

if __name__ == "__main__":
    asyncio.run(run())
