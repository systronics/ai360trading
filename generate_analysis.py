import os, sys, json, asyncio, textwrap, random
from datetime import datetime
from pathlib import Path

import edge_tts
import yfinance as yf
import pytz
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
from groq import Groq

# YouTube upload
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── CONFIG ──────────────────────────────────────────────────────────────────
IST = pytz.timezone("Asia/Kolkata")
OUT       = Path("output")
MUSIC_DIR = Path("public/music")
W, H      = 1920, 1080
FPS       = 24
VOICE     = "hi-IN-SwaraNeural"
os.makedirs(OUT, exist_ok=True)

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

# ─── FONTS ───────────────────────────────────────────────────────────────────
FONT_BOLD_PATHS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"]
FONT_REG_PATHS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

# ─── THEMES ──────────────────────────────────────────────────────────────────
THEMES = {
    "bullish": {"bg_top": (5, 30, 15), "bg_bot": (10, 60, 30), "accent": (0, 220, 110), "text": (235, 255, 245)},
    "bearish": {"bg_top": (35, 10, 10), "bg_bot": (70, 20, 20), "accent": (255, 60, 60), "text": (255, 240, 240)},
    "neutral": {"bg_top": (10, 20, 40), "bg_bot": (20, 40, 80), "accent": (0, 180, 255), "text": (240, 250, 255)},
}

def lerp(c1, c2, t): return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ─── MARKET DATA (SEO Optimization) ──────────────────────────────────────────
def get_live_market_summary():
    """Enhanced worldwide market summary for Global SEO."""
    try:
        # Includes India (Nifty), US (S&P 500), and Crypto (BTC) for worldwide appeal
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "S&P 500": "^GSPC", "Bitcoin": "BTC-USD"}
        summary_parts = []
        for name, sym in symbols.items():
            ticker = yf.Ticker(sym)
            df = ticker.history(period="1d")
            if not df.empty:
                last = df['Close'].iloc[-1]
                change = ((last - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                summary_parts.append(f"{name}: {last:.2f} ({change:+.2f}%)")
        return " | ".join(summary_parts)
    except: return "Global markets are showing interesting volatility today."

# ─── GROQ SCRIPT GENERATION ──────────────────────────────────────────────────
def generate_slides(client):
    mode = os.environ.get("CONTENT_MODE", "market").lower()
    today_dt = datetime.now(IST)
    today_readable = today_dt.strftime("%d %B %Y")
    
    live_info = get_live_market_summary()
    
    prompt = f"""You are a Senior Global Market Strategist for ai360trading.
Date: {today_readable}. Mode: {mode}. 
Market Data: {live_info}

Generate 8 distinct slides in Hinglish. 
Rule: Each slide MUST have different content. 
SEO Target: Professional traders in India, USA, and UK.

Respond ONLY with valid JSON:
{{
  "video_title": "SEO OPTIMIZED TITLE (Hinglish + English) MAX 90 CHARS",
  "video_description": "Viral 3-paragraph description with keywords: Nifty, S&P500, Price Action, ai360trading",
  "overall_sentiment": "bullish/bearish/neutral",
  "slides": [
    {{
      "title": "Unique Heading",
      "content": "40-60 words spoken text using the live data provided",
      "sentiment": "bullish/bearish/neutral",
      "key_points": ["Specific Level 1", "Specific Level 2", "Logic"]
    }}
  ]
}}"""

    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content)
    except: return _human_fallback(today_readable)

def _human_fallback(date):
    """A 'Manual' style fallback that doesn't look like an error."""
    return {
        "video_title": f"Market Strategy & Levels for {date} | ai360trading",
        "video_description": "Today we analyze key psychological levels and global trends. Join our Telegram for live updates.",
        "overall_sentiment": "neutral",
        "slides": [{"title": f"Focus for {date}", "content": "Markets are at a crucial junction today. We are watching the previous day's high and low carefully for a breakout.", "sentiment": "neutral", "key_points": ["Watch Price Action", "Volume Analysis"]}] * 8
    }

# ─── RENDERER ────────────────────────────────────────────────────────────────
def make_slide(slide, idx, total, path):
    th = THEMES.get(slide.get("sentiment", "neutral").lower(), THEMES["neutral"])
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        c = lerp(th["bg_top"], th["bg_bot"], y / H)
        for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")
    draw.text((W - 60, 40), "AI360TRADING.IN", fill=(255, 255, 255, 120), font=get_font(FONT_REG_PATHS, 30), anchor="ra")
    
    # Title
    title_font = get_font(FONT_BOLD_PATHS, 80)
    draw.text((W // 2, 180), slide["title"].upper(), fill=th["text"], font=title_font, anchor="mm")
    
    # Content Box (The 'Manual' Work look)
    content_font = get_font(FONT_REG_PATHS, 44)
    lines = textwrap.wrap(slide["content"], width=55)
    y_text = 350
    for line in lines[:5]:
        draw.text((120, y_text), line, fill=th["text"], font=content_font)
        y_text += 65

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(path))

# ─── YOUTUBE UPLOAD (Worldwide Tags) ─────────────────────────────────────────
def upload_to_youtube(video_path, title, description):
    youtube = build("youtube", "v3", credentials=Credentials.from_authorized_user_info(json.loads(os.environ["YOUTUBE_CREDENTIALS"])))
    tags = ["Stock Market India", "Nifty50", "S&P 500", "Trading Psychology", "ai360trading", "Technical Analysis", "Price Action India"]
    body = {
        "snippet": {"title": title, "description": description, "tags": tags, "categoryId": "27", "defaultLanguage": "hi"},
        "status": {"privacyStatus": "public"}
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
    return response["id"]

async def run():
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    data = generate_slides(client)
    
    clips = []
    for i, s in enumerate(data["slides"]):
        img_p, aud_p = OUT/f"slide_{i}.png", OUT/f"slide_{i}.mp3"
        make_slide(s, i+1, 8, img_p)
        await edge_tts.Communicate(s["content"], VOICE).save(str(aud_p))
        
        voice = AudioFileClip(str(aud_p))
        clips.append(ImageClip(str(img_p)).set_duration(voice.duration + 0.5).set_audio(voice))

    final_path = OUT / "analysis_video_final.mp4"
    concatenate_videoclips(clips, method="compose").write_videofile(str(final_path), fps=FPS, codec="libx264", audio_codec="aac")
    
    video_id = upload_to_youtube(final_path, data["video_title"], data["video_description"])
    if video_id:
        (OUT / "analysis_video_id.txt").write_text(video_id)
        print(f"✅ Worldwide SEO Video Live: {video_id}")

if __name__ == "__main__":
    asyncio.run(run())
