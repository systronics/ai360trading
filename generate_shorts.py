import os, sys, json, asyncio
from datetime import datetime
from pathlib import Path

import pytz
import requests
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip,
    concatenate_audioclips
)
from groq import Groq
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# ─── CONFIG ──────────────────────────────────────────────────────────────────
OUT       = Path("output")
MUSIC_DIR = Path("public/music")
SW, SH    = 1080, 1920   # Vertical 9:16
FPS       = 30
IST       = pytz.timezone("Asia/Kolkata")
now_ist   = datetime.now(IST)
os.makedirs(OUT, exist_ok=True)

# ─── COLORS ──────────────────────────────────────────────────────────────────
BULL_GREEN  = (0, 210, 100)
BEAR_RED    = (220, 55, 55)
GOLD        = (255, 200, 50)
WHITE       = (255, 255, 255)
DARK_BG     = (10, 15, 30)
SOFT_WHITE  = (230, 240, 255)
ACCENT_BLUE = (60, 140, 255)

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

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def gradient_bg(top, bot):
    img = Image.new("RGB", (SW, SH))
    px  = img.load()
    for y in range(SH):
        c = lerp(top, bot, y / SH)
        for x in range(SW):
            px[x, y] = c
    return img

def draw_text_outlined(draw, text, x, y, font, fill, outline=3, anchor="mm"):
    for dx in range(-outline, outline + 1):
        for dy in range(-outline, outline + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0), anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)

# ─── WEEKEND DETECTION ───────────────────────────────────────────────────────
def is_weekend():
    return datetime.now().weekday() >= 5

# ─── BACKGROUND MUSIC ────────────────────────────────────────────────────────
def get_bg_music():
    day = datetime.now().weekday()
    music_map = {
        0: "bgmusic1.mp3", 1: "bgmusic2.mp3", 2: "bgmusic3.mp3",
        3: "bgmusic1.mp3", 4: "bgmusic2.mp3", 5: "bgmusic3.mp3", 6: "bgmusic1.mp3"
    }
    f = MUSIC_DIR / music_map[day]
    if f.exists():
        print(f"🎵 Music: {f.name}")
        return f
    for f in MUSIC_DIR.glob("*.mp3"):
        return f
    return None

def mix_audio(voice_clip, duration):
    """Mix voice with background music at low volume."""
    bg_path = get_bg_music()
    if not bg_path:
        return voice_clip
    try:
        bg = AudioFileClip(str(bg_path))
        if bg.duration < duration:
            loops = int(duration / bg.duration) + 1
            bg    = concatenate_audioclips([bg] * loops)
        bg = bg.subclip(0, duration).volumex(0.08)
        return CompositeAudioClip([voice_clip, bg])
    except Exception as e:
        print(f"⚠️ Music error: {e}")
        return voice_clip

# ─── MARKET DATA ─────────────────────────────────────────────────────────────
def fetch_market_data():
    """Fetch live market data — returns fallback on weekend or error."""
    print("📡 Fetching market data...")
    weekend = is_weekend()

    tickers = {
        "nifty":  ("^NSEI",   "₹"),
        "btc":    ("BTC-USD", "$"),
        "gold":   ("GC=F",    "$"),
        "usdinr": ("INR=X",   "₹"),
        "sp500":  ("^GSPC",   "$"),
    }

    data = {}
    for name, (sym, curr) in tickers.items():
        try:
            df   = yf.download(sym, period="2d", interval="1d", progress=False)
            last = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2])
            chg  = ((last - prev) / prev) * 100
            if name == "usdinr":
                val = f"{curr}{last:.2f}"
            elif name in ("btc", "sp500"):
                val = f"{curr}{last:,.0f}"
            else:
                val = f"{curr}{last:,.2f}"
            data[name] = {"val": val, "chg": f"{chg:+.2f}%", "up": chg >= 0, "raw": last}
        except Exception as e:
            print(f"⚠️ {name} fetch error: {e}")
            data[name] = {"val": "N/A", "chg": "0.00%", "up": True, "raw": 0}

    if weekend:
        print("📅 Weekend mode — market data may be stale")

    return data

# ─── PART 1 VIDEO LINK ───────────────────────────────────────────────────────
def get_part1_url():
    """Read analysis video ID saved by generate_analysis.py."""
    id_path = OUT / "analysis_video_id.txt"
    if id_path.exists():
        vid_id = id_path.read_text(encoding="utf-8").strip()
        if vid_id and vid_id != "UPLOAD_FAILED":
            url = f"https://youtube.com/watch?v={vid_id}"
            print(f"🔗 Part 1 linked: {url}")
            return url
    print("⚠️ No Part 1 video ID found — shorts will work without link")
    return ""

# ══════════════════════════════════════════════════════════════════════════════
# SHORT 2 — TRADE SETUP CARD
# Voice: hi-IN-MadhurNeural (male, authoritative)
# Content: specific trade setup with entry/target/SL
# ══════════════════════════════════════════════════════════════════════════════

def make_short2_frame(script_data, market):
    """1080x1920 trade setup card."""
    sentiment = script_data.get("sentiment", "bullish").lower()
    accent    = BULL_GREEN if sentiment == "bullish" else BEAR_RED if sentiment == "bearish" else GOLD

    img  = gradient_bg((8, 12, 28), (15, 25, 50))
    draw = ImageDraw.Draw(img, "RGBA")

    # Top/bottom accent bars
    draw.rectangle([(0, 0), (SW, 12)], fill=accent)
    draw.rectangle([(0, SH - 12), (SW, SH)], fill=accent)

    # Brand header
    draw_text_outlined(draw, "AI360TRADING", SW // 2, 80,
                       get_font(FONT_BOLD_PATHS, 62), accent, outline=2)
    draw.text((SW // 2, 145), "TRADE SETUP", font=get_font(FONT_BOLD_PATHS, 38),
              fill=SOFT_WHITE, anchor="mm")

    # Date + time
    draw.text((SW // 2, 200),
              now_ist.strftime("%d %b %Y • %I:%M %p IST"),
              font=get_font(FONT_REG_PATHS, 32), fill=(140, 160, 200), anchor="mm")

    # Divider
    draw.rectangle([(60, 230), (SW - 60, 233)], fill=accent)

    # Stock / instrument name
    stock = script_data.get("stock", "NIFTY 50")
    draw_text_outlined(draw, stock.upper(), SW // 2, 310,
                       get_font(FONT_BOLD_PATHS, 90), WHITE, outline=2)

    # Sentiment badge
    badge = f"  {'📈' if sentiment == 'bullish' else '📉' if sentiment == 'bearish' else '⚖️'} {sentiment.upper()}  "
    draw.rounded_rectangle([(SW // 2 - 160, 360), (SW // 2 + 160, 420)],
                            radius=20, fill=(*accent, 40))
    draw.text((SW // 2, 390), badge, font=get_font(FONT_BOLD_PATHS, 36),
              fill=accent, anchor="mm")

    # Trade levels box
    box_top = 460
    draw.rounded_rectangle([(60, box_top), (SW - 60, box_top + 420)],
                            radius=30, fill=(255, 255, 255, 12))

    levels = [
        ("🎯 ENTRY",  script_data.get("entry",  "Market Price"), WHITE),
        ("📊 TARGET", script_data.get("target", "See Description"), BULL_GREEN),
        ("🛑 SL",     script_data.get("sl",     "Risk Managed"), BEAR_RED),
        ("⏱ HORIZON", script_data.get("horizon","Intraday/Swing"), GOLD),
    ]
    ly = box_top + 60
    for label, value, color in levels:
        draw.text((120, ly), label, font=get_font(FONT_BOLD_PATHS, 36),
                  fill=(150, 170, 210), anchor="lm")
        draw.text((SW - 120, ly), str(value), font=get_font(FONT_BOLD_PATHS, 42),
                  fill=color, anchor="rm")
        ly += 88

    # Nifty live data strip
    strip_y = 930
    draw.rounded_rectangle([(60, strip_y), (SW - 60, strip_y + 100)],
                            radius=20, fill=(0, 0, 0, 100))
    nifty_color = BULL_GREEN if market["nifty"]["up"] else BEAR_RED
    draw.text((120, strip_y + 50), "NIFTY", font=get_font(FONT_BOLD_PATHS, 38),
              fill=(160, 180, 220), anchor="lm")
    draw.text((SW // 2, strip_y + 50), market["nifty"]["val"],
              font=get_font(FONT_BOLD_PATHS, 44), fill=WHITE, anchor="mm")
    draw.text((SW - 120, strip_y + 50), market["nifty"]["chg"],
              font=get_font(FONT_BOLD_PATHS, 40), fill=nifty_color, anchor="rm")

    # Key insight text
    insight = script_data.get("insight", "Market conditions favorable. Trade with discipline.")
    insight_lines = []
    words, line = insight.split(), ""
    for w in words:
        test = (line + " " + w).strip()
        if get_font(FONT_REG_PATHS, 36).getbbox(test)[2] < SW - 160:
            line = test
        else:
            insight_lines.append(line)
            line = w
    if line:
        insight_lines.append(line)

    iy = 1090
    for ln in insight_lines[:4]:
        draw.text((SW // 2, iy), ln, font=get_font(FONT_REG_PATHS, 36),
                  fill=SOFT_WHITE, anchor="mm")
        iy += 50

    # Part 1 link prompt
    draw.text((SW // 2, 1340),
              "📺 Full analysis link in description",
              font=get_font(FONT_REG_PATHS, 34), fill=(140, 170, 220), anchor="mm")

    # Risk disclaimer
    draw.rounded_rectangle([(60, 1400), (SW - 60, 1480)],
                            radius=15, fill=(255, 180, 0, 20))
    draw.text((SW // 2, 1440),
              "⚠️ Not financial advice. Trade responsibly.",
              font=get_font(FONT_REG_PATHS, 30), fill=(200, 180, 100), anchor="mm")

    # CTA button
    draw.rounded_rectangle([(100, SH - 350), (SW - 100, SH - 250)],
                            radius=25, fill=accent)
    draw_text_outlined(draw, "📲 SUBSCRIBE FOR DAILY SIGNALS",
                       SW // 2, SH - 300,
                       get_font(FONT_BOLD_PATHS, 36), (0, 0, 0), outline=1)

    # Website
    draw.text((SW // 2, SH - 190),
              "ai360trading.in  •  t.me/ai360trading",
              font=get_font(FONT_REG_PATHS, 32), fill=(120, 150, 200), anchor="mm")

    path = OUT / f"short2_{now_ist.strftime('%Y%m%d')}.png"
    img.save(str(path), quality=95)
    return path


def generate_short2_script(client, market):
    """Groq generates trade setup JSON."""
    weekend = is_weekend()
    if weekend:
        context = "Create an educational trade setup example — market is closed today. Use example levels."
    else:
        context = (
            f"Live market: Nifty {market['nifty']['val']} ({market['nifty']['chg']}), "
            f"BTC {market['btc']['val']}, Gold {market['gold']['val']}, "
            f"S&P500 {market['sp500']['val']}, USD/INR {market['usdinr']['val']}"
        )

    prompt = f"""You are an expert Indian stock market trader creating a YouTube Shorts trade setup in Hinglish for ai360trading.

{context}

Generate a specific trade setup. Respond ONLY with valid JSON:
{{
  "stock": "stock or index name (e.g. NIFTY 50, BANK NIFTY, RELIANCE, HDFC BANK)",
  "sentiment": "bullish or bearish or neutral",
  "entry": "entry price or range (e.g. 22150-22200)",
  "target": "target price (e.g. 22450)",
  "sl": "stop loss price (e.g. 21980)",
  "horizon": "Intraday or Swing (2-3 days) or Positional",
  "insight": "one key insight in Hinglish max 15 words why this trade",
  "script": "40-second Hinglish voice script — energetic, specific, actionable. Start with hook. End with subscribe CTA. Max 80 words."
}}"""

    print("🤖 Generating Short 2 trade setup script...")
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.8,
            max_tokens=500
        )
        data = json.loads(resp.choices[0].message.content)
        print(f"✅ Trade setup: {data.get('stock')} — {data.get('sentiment')}")
        return data
    except Exception as e:
        print(f"⚠️ Groq error Short 2: {e}")
        return {
            "stock": "NIFTY 50", "sentiment": "neutral",
            "entry": "Market Price", "target": "See Description",
            "sl": "Risk Managed", "horizon": "Intraday",
            "insight": "Market mein caution zaroori hai aaj.",
            "script": "Bhaiyo, aaj ka trade setup dekho! Nifty pe nazar rakho. Entry, target aur stop loss ke liye description check karo. Risk management sabse zaroori hai. Subscribe karo daily signals ke liye!"
        }


# ══════════════════════════════════════════════════════════════════════════════
# SHORT 3 — MARKET PULSE CARD
# Voice: hi-IN-SwaraNeural (female, energetic)
# Content: overall market mood dashboard
# ══════════════════════════════════════════════════════════════════════════════

def make_short3_frame(script_data, market):
    """1080x1920 market pulse dashboard."""
    overall_up = market["nifty"]["up"]
    accent     = BULL_GREEN if overall_up else BEAR_RED

    img  = gradient_bg((15, 20, 40), (5, 8, 20))
    draw = ImageDraw.Draw(img, "RGBA")

    # Top/bottom bars
    draw.rectangle([(0, 0), (SW, 12)], fill=accent)
    draw.rectangle([(0, SH - 12), (SW, SH)], fill=accent)

    # Header
    draw_text_outlined(draw, "MARKET PULSE", SW // 2, 85,
                       get_font(FONT_BOLD_PATHS, 70), accent, outline=2)
    draw.text((SW // 2, 155),
              now_ist.strftime("%d %B %Y • %I:%M %p IST"),
              font=get_font(FONT_REG_PATHS, 34), fill=(160, 185, 220), anchor="mm")
    draw.text((SW // 2, 205), "ai360trading.in",
              font=get_font(FONT_BOLD_PATHS, 30), fill=(100, 130, 180), anchor="mm")

    # Divider
    draw.rectangle([(60, 230), (SW - 60, 233)], fill=accent)

    # Hero — Nifty
    draw.rounded_rectangle([(60, 255), (SW - 60, 560)],
                            radius=35, fill=(255, 255, 255, 12))
    draw.text((SW // 2, 315), "NIFTY 50",
              font=get_font(FONT_BOLD_PATHS, 48), fill=(180, 205, 240), anchor="mm")
    draw_text_outlined(draw, market["nifty"]["val"], SW // 2, 430,
                       get_font(FONT_BOLD_PATHS, 110), WHITE, outline=2)
    draw_text_outlined(draw, market["nifty"]["chg"], SW // 2, 520,
                       get_font(FONT_BOLD_PATHS, 65), accent, outline=2)

    # Asset grid — 4 assets
    assets = [
        ("BITCOIN",  market["btc"],    580),
        ("GOLD",     market["gold"],   760),
        ("S&P 500",  market["sp500"],  940),
        ("USD/INR",  market["usdinr"], 1120),
    ]

    for label, mdata, y in assets:
        up_color = BULL_GREEN if mdata["up"] else BEAR_RED
        draw.rounded_rectangle([(60, y), (SW - 60, y + 155)],
                                radius=22, fill=(0, 0, 0, 90))
        # Left: label
        draw.text((120, y + 78), label,
                  font=get_font(FONT_BOLD_PATHS, 40), fill=(140, 165, 205), anchor="lm")
        # Right: value + change
        draw.text((SW - 120, y + 52), mdata["val"],
                  font=get_font(FONT_BOLD_PATHS, 44), fill=WHITE, anchor="rm")
        draw.text((SW - 120, y + 108), mdata["chg"],
                  font=get_font(FONT_BOLD_PATHS, 38), fill=up_color, anchor="rm")

    # Market mood summary
    mood_text = script_data.get("mood_summary", "Market mein cautious optimism dikh raha hai.")
    mood_y = 1310
    draw.rounded_rectangle([(60, mood_y), (SW - 60, mood_y + 110)],
                            radius=20, fill=(*accent, 25))
    draw.text((SW // 2, mood_y + 55), f"💬 {mood_text}",
              font=get_font(FONT_REG_PATHS, 33), fill=SOFT_WHITE, anchor="mm")

    # Key levels
    key_level = script_data.get("key_level", "")
    if key_level:
        draw.text((SW // 2, 1460),
                  f"🎯 Key Level: {key_level}",
                  font=get_font(FONT_BOLD_PATHS, 36), fill=GOLD, anchor="mm")

    # CTA
    draw.rounded_rectangle([(100, SH - 350), (SW - 100, SH - 250)],
                            radius=25, fill=accent)
    draw_text_outlined(draw, "🔔 SUBSCRIBE FOR DAILY UPDATES",
                       SW // 2, SH - 300,
                       get_font(FONT_BOLD_PATHS, 35), (0, 0, 0), outline=1)

    # Bottom links
    draw.text((SW // 2, SH - 190),
              "ai360trading.in  •  t.me/ai360trading",
              font=get_font(FONT_REG_PATHS, 32), fill=(110, 140, 190), anchor="mm")

    path = OUT / f"short3_{now_ist.strftime('%Y%m%d')}.png"
    img.save(str(path), quality=95)
    return path


def generate_short3_script(client, market):
    """Groq generates market pulse JSON."""
    weekend = is_weekend()
    if weekend:
        context = "Weekend — create an educational market overview. Explain what traders should prepare for next week."
    else:
        context = (
            f"Live data: Nifty {market['nifty']['val']} ({market['nifty']['chg']}), "
            f"BTC {market['btc']['val']} ({market['btc']['chg']}), "
            f"Gold {market['gold']['val']} ({market['gold']['chg']}), "
            f"S&P500 {market['sp500']['val']} ({market['sp500']['chg']}), "
            f"USD/INR {market['usdinr']['val']}"
        )

    prompt = f"""You are an energetic Indian market commentator for ai360trading YouTube Shorts.

{context}

Respond ONLY with valid JSON:
{{
  "mood_summary": "overall market mood in Hinglish max 10 words",
  "key_level": "most important Nifty level to watch today (e.g. 22200)",
  "script": "40-second energetic Hinglish script about today's market pulse. Start with 'Bhaiyo!' hook. Cover Nifty, global cues, what to watch. End with subscribe CTA. Max 80 words."
}}"""

    print("🤖 Generating Short 3 market pulse script...")
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.8,
            max_tokens=400
        )
        data = json.loads(resp.choices[0].message.content)
        print(f"✅ Market pulse: {data.get('mood_summary')}")
        return data
    except Exception as e:
        print(f"⚠️ Groq error Short 3: {e}")
        return {
            "mood_summary": "Market cautious, traders alert",
            "key_level": "22000",
            "script": "Bhaiyo! Aaj market mein mixed sentiment dikh raha hai. Nifty key levels pe hai. Global markets pe nazar rakho. Discipline ke saath trade karo. Subscribe karo daily updates ke liye!"
        }


# ─── YOUTUBE AUTH ────────────────────────────────────────────────────────────
def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json:
            if os.path.exists("token.json"):
                with open("token.json") as f:
                    creds_json = f.read()
            else:
                print("❌ No YouTube credentials")
                return None
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"❌ YouTube auth error: {e}")
        return None


def upload_short(youtube, video_path, title, description):
    """Upload a single Short to YouTube."""
    if not youtube:
        return None
    body = {
        "snippet": {
            "title":       title[:100],
            "description": description,
            "tags":        ["Nifty", "Trading", "Shorts", "ai360trading",
                            "StockMarket", "TradingIndia", "MarketPulse"],
            "categoryId":  "27"
        },
        "status": {
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media   = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"🚀 Uploading: {title[:60]}...")
    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   {int(status.progress() * 100)}%")
        vid_id  = response["id"]
        vid_url = f"https://youtube.com/shorts/{vid_id}"
        print(f"✅ Uploaded: {vid_url}")
        return vid_url
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None


# ─── FACEBOOK SHARE ──────────────────────────────────────────────────────────
def share_to_facebook(short2_url, short3_url, market):
    token    = os.environ.get("META_ACCESS_TOKEN", "")
    page_id  = os.environ.get("FACEBOOK_PAGE_ID", "")
    group_id = os.environ.get("FACEBOOK_GROUP_ID", "")

    if not token or not page_id:
        print("⚠️ Facebook credentials missing — skipping")
        return

    nifty_emoji = "📈" if market["nifty"]["up"] else "📉"
    msg = (
        f"{nifty_emoji} Aaj ke Market Shorts — Must Watch! 🔥\n\n"
        f"Nifty: {market['nifty']['val']} ({market['nifty']['chg']})\n"
        f"BTC: {market['btc']['val']} ({market['btc']['chg']})\n\n"
    )
    if short2_url:
        msg += f"📊 Trade Setup Short:\n{short2_url}\n\n"
    if short3_url:
        msg += f"💹 Market Pulse Short:\n{short3_url}\n\n"
    msg += (
        "Daily signals aur analysis ke liye subscribe karo! 🔔\n"
        "🌐 https://ai360trading.in\n"
        "📱 https://t.me/ai360trading\n\n"
        "#ai360trading #Nifty #StockMarket #TradingIndia #Shorts"
    )

    for target, target_id in [("Page", page_id), ("Group", group_id)]:
        if not target_id:
            continue
        try:
            resp = requests.post(
                f"https://graph.facebook.com/v21.0/{target_id}/feed",
                data={"message": msg, "access_token": token},
                timeout=30
            )
            resp.raise_for_status()
            print(f"✅ Shared to Facebook {target}")
        except Exception as e:
            print(f"⚠️ Facebook {target} share failed: {e}")


# ─── MAIN ────────────────────────────────────────────────────────────────────
async def main():
    today   = now_ist.strftime("%Y%m%d")
    client  = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
    youtube = get_youtube_service()
    part1_url = get_part1_url()

    # ── Market data ──
    market = fetch_market_data()

    # ════════════════════════════════
    # SHORT 2 — TRADE SETUP
    # Voice: hi-IN-MadhurNeural (male, authoritative)
    # ════════════════════════════════
    print("\n─── SHORT 2: TRADE SETUP ───")
    s2_data      = generate_short2_script(client, market)
    s2_frame     = make_short2_frame(s2_data, market)
    s2_audio_path = OUT / f"short2_voice_{today}.mp3"

    await edge_tts.Communicate(
        s2_data.get("script", "Aaj ka trade setup dekhte hain!"),
        "hi-IN-MadhurNeural",
        rate="+10%"
    ).save(str(s2_audio_path))

    s2_voice    = AudioFileClip(str(s2_audio_path))
    s2_duration = s2_voice.duration + 0.5
    s2_audio    = mix_audio(s2_voice, s2_duration)

    s2_video_path = OUT / f"short2_{today}.mp4"
    (ImageClip(str(s2_frame))
        .set_duration(s2_duration)
        .set_audio(s2_audio)
        .write_videofile(str(s2_video_path), fps=FPS, codec="libx264",
                         audio_codec="aac", logger=None))
    print(f"✅ Short 2 rendered: {s2_video_path}")

    s2_title = (
        f"{'📈' if market['nifty']['up'] else '📉'} "
        f"{s2_data.get('stock','Nifty')} Trade Setup — "
        f"{now_ist.strftime('%d %b')} #Shorts"
    )
    s2_desc = (
        f"Trade Setup: {s2_data.get('stock','Nifty')}\n"
        f"Entry: {s2_data.get('entry','')}\n"
        f"Target: {s2_data.get('target','')}\n"
        f"Stop Loss: {s2_data.get('sl','')}\n"
        f"Horizon: {s2_data.get('horizon','')}\n\n"
        f"{s2_data.get('insight','')}\n\n"
        f"⚠️ Not financial advice.\n\n"
        + (f"📊 Full Analysis: {part1_url}\n" if part1_url else "")
        + "🌐 https://ai360trading.in\n📱 https://t.me/ai360trading\n"
        "#Trading #Nifty #StockMarket #ai360trading #TradingIndia"
    )
    short2_url = upload_short(youtube, s2_video_path, s2_title, s2_desc)

    # ════════════════════════════════
    # SHORT 3 — MARKET PULSE
    # Voice: hi-IN-SwaraNeural (female, energetic)
    # ════════════════════════════════
    print("\n─── SHORT 3: MARKET PULSE ───")
    s3_data       = generate_short3_script(client, market)
    s3_frame      = make_short3_frame(s3_data, market)
    s3_audio_path = OUT / f"short3_voice_{today}.mp3"

    await edge_tts.Communicate(
        s3_data.get("script", "Bhaiyo! Aaj ka market pulse dekhte hain!"),
        "hi-IN-SwaraNeural",
        rate="+12%"
    ).save(str(s3_audio_path))

    s3_voice    = AudioFileClip(str(s3_audio_path))
    s3_duration = s3_voice.duration + 0.5
    s3_audio    = mix_audio(s3_voice, s3_duration)

    s3_video_path = OUT / f"short3_{today}.mp4"
    (ImageClip(str(s3_frame))
        .set_duration(s3_duration)
        .set_audio(s3_audio)
        .write_videofile(str(s3_video_path), fps=FPS, codec="libx264",
                         audio_codec="aac", logger=None))
    print(f"✅ Short 3 rendered: {s3_video_path}")

    s3_title = (
        f"Market Pulse — Nifty {market['nifty']['val']} "
        f"{market['nifty']['chg']} | {now_ist.strftime('%d %b')} #Shorts"
    )
    s3_desc = (
        f"Market Pulse — {now_ist.strftime('%d %B %Y')}\n\n"
        f"Nifty: {market['nifty']['val']} ({market['nifty']['chg']})\n"
        f"BTC: {market['btc']['val']} ({market['btc']['chg']})\n"
        f"Gold: {market['gold']['val']} ({market['gold']['chg']})\n"
        f"S&P500: {market['sp500']['val']} ({market['sp500']['chg']})\n"
        f"USD/INR: {market['usdinr']['val']}\n\n"
        f"Key Level: {s3_data.get('key_level','')}\n\n"
        + (f"📊 Full Analysis: {part1_url}\n" if part1_url else "")
        + "🌐 https://ai360trading.in\n📱 https://t.me/ai360trading\n"
        "#MarketPulse #Nifty #StockMarket #ai360trading #TradingIndia"
    )
    short3_url = upload_short(youtube, s3_video_path, s3_title, s3_desc)

    # ── Facebook share both ──
    share_to_facebook(short2_url, short3_url, market)

    print(f"\n🚀 DONE — {today}")
    print(f"   Short 2: {short2_url or 'upload failed'}")
    print(f"   Short 3: {short3_url or 'upload failed'}")


if __name__ == "__main__":
    asyncio.run(main())
