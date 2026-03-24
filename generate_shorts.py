import os, sys, json, asyncio, re, time
from datetime import datetime
from pathlib import Path
import pytz

import requests
import yfinance as yf
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip,
    ColorClip, TextClip, concatenate_videoclips
)
from moviepy.video.fx.all import fadein, fadeout
from groq import Groq
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# ── CONFIG & STYLE ──
OUT = "output"
SW, SH = 1080, 1920  # Vertical 9:16
os.makedirs(OUT, exist_ok=True)

# Colors for "Human Manual" look
BULL_GREEN = (0, 210, 100)
BEAR_RED = (255, 70, 50)
GOLD_COLOR = (255, 215, 0)
DARK_BG = (10, 15, 30)

# Timezone Setup
IST = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(IST)

def get_font(size, bold=False):
    """Robust font loader for Ubuntu/GitHub Actions environments."""
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/FreeSans.ttf"
    ]
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def lerp(c1, c2, t):
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

def draw_gradient_bg(top, bot, w=SW, h=SH):
    img = Image.new("RGB", (w, h)); px = img.load()
    for y in range(h):
        c = lerp(top, bot, y/h)
        for x in range(w): px[x, y] = c
    return img

# ══════════════════════════════════════════════════════════
# MARKET DATA ENGINE
# ══════════════════════════════════════════════════════════
def fetch_market_data():
    print("📡 Fetching real-time market pulse...")
    tickers = {
        "nifty": ("^NSEI", "₹"),
        "btc": ("BTC-USD", "$"),
        "gold": ("GC=F", "$"),
        "usdinr": ("INR=X", "₹")
    }
    data = {}
    for name, (sym, curr) in tickers.items():
        try:
            df = yf.download(sym, period="2d", interval="1d", progress=False)
            last = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2])
            chg = ((last - prev) / prev) * 100
            data[name] = {
                "val": f"{curr}{last:,.2f}" if name != "usdinr" else f"{curr}{last:.2f}",
                "chg": f"{chg:+.2f}%",
                "up": chg >= 0,
                "raw_val": last
            }
        except Exception as e:
            print(f"⚠️ Error fetching {name}: {e}")
            data[name] = {"val": "N/A", "chg": "0%", "up": True}
    return data

# ══════════════════════════════════════════════════════════
# SHORT 3: MARKET PULSE GENERATOR
# ══════════════════════════════════════════════════════════
def make_pulse_frame(market):
    """Creates a high-end, manual-look market dashboard."""
    is_bull = market['nifty']['up']
    accent = BULL_GREEN if is_bull else BEAR_RED
    
    # Background
    img = draw_gradient_bg((15, 20, 40), (5, 5, 15))
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Top/Bottom Bars
    draw.rectangle([0, 0, SW, 15], fill=accent)
    draw.rectangle([0, SH-15, SW, SH], fill=accent)

    # Header
    draw.text((SW//2, 120), "AI360TRADING", font=get_font(75, True), fill=accent, anchor="mm")
    draw.text((SW//2, 200), f"LIVE PULSE • {now_ist.strftime('%I:%M %p')}", font=get_font(40), fill=(180, 200, 230), anchor="mm")
    
    # Main Hero: Nifty
    draw.rounded_rectangle([80, 300, SW-80, 650], radius=40, fill=(255, 255, 255, 15))
    draw.text((SW//2, 380), "NIFTY 50", font=get_font(55), fill=(200, 220, 255), anchor="mm")
    draw.text((SW//2, 500), market['nifty']['val'], font=get_font(130, True), fill=(255, 255, 255), anchor="mm")
    draw.text((SW//2, 600), market['nifty']['chg'], font=get_font(70, True), fill=accent, anchor="mm")

    # Asset Grid
    assets = [
        ("BITCOIN", market['btc'], 720),
        ("GOLD", market['gold'], 950),
        ("USD/INR", market['usdinr'], 1180)
    ]
    
    for label, mdata, y in assets:
        draw.rounded_rectangle([100, y, SW-100, y+180], radius=25, fill=(0, 0, 0, 100))
        draw.text((150, y+90), label, font=get_font(45, True), fill=(150, 170, 200), anchor="lm")
        draw.text((SW-150, y+65), mdata['val'], font=get_font(50, True), fill=(255, 255, 255), anchor="rm")
        draw.text((SW-150, y+120), mdata['chg'], font=get_font(40), fill=BULL_GREEN if mdata['up'] else BEAR_RED, anchor="rm")

    # ZENO Placeholder or Branding
    draw.text((SW//2, 1500), "ZENO AI TRADER", font=get_font(40, True), fill=(255, 255, 255, 50), anchor="mm")
    
    # CTA
    draw.rounded_rectangle([150, SH-280, SW-150, SH-180], radius=20, fill=accent)
    draw.text((SW//2, SH-230), "SUBSCRIBE FOR SIGNALS", font=get_font(45, True), fill=(0, 0, 0), anchor="mm")

    path = Path(OUT) / f"pulse_{now_ist.strftime('%Y%m%d')}.png"
    img.save(path, quality=95)
    return path

# ══════════════════════════════════════════════════════════
# AI SCRIPT & VOICE ENGINE
# ══════════════════════════════════════════════════════════
async def get_ai_voice(market, groq_client):
    """Generates natural Hinglish script and converts to audio."""
    prompt = f"""
    Write a 40-second viral YouTube Shorts script in natural Hinglish.
    Market Data: Nifty {market['nifty']['val']} ({market['nifty']['chg']}), 
    BTC {market['btc']['val']}, Gold {market['gold']['val']}.
    Tone: Energetic, Fast, Human (not robotic). 
    Start: "Bhaiyo, market ka mood badal raha hai!"
    End: "Full level ke liye link description mein hai. Subscribe now!"
    Keep it strictly under 85 words.
    """
    
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    script = completion.choices[0].message.content.strip()
    
    audio_path = Path(OUT) / "voiceover.mp3"
    # Using Madhur for a realistic Indian male voice
    communicate = edge_tts.Communicate(script, "hi-IN-MadhurNeural", rate="+15%")
    await communicate.save(str(audio_path))
    return audio_path, script

# ══════════════════════════════════════════════════════════
# SOCIAL SHARING (FACEBOOK)
# ══════════════════════════════════════════════════════════
def share_to_meta(video_url, market):
    token = os.environ.get("META_ACCESS_TOKEN")
    page_id = os.environ.get("FACEBOOK_PAGE_ID")
    if not token or not page_id: return
    
    msg = (f"🚀 Market Pulse Update - {now_ist.strftime('%d %b')}\n\n"
           f"Nifty: {market['nifty']['val']} ({market['nifty']['chg']})\n"
           f"Bitcoin: {market['btc']['val']}\n\n"
           f"Watch full update: {video_url}\n"
           f"#Trading #Nifty #AI360Trading")
           
    requests.post(f"https://graph.facebook.com/v21.0/{page_id}/feed", 
                  data={"message": msg, "link": video_url, "access_token": token})

# ══════════════════════════════════════════════════════════
# MAIN PRODUCTION PIPELINE
# ══════════════════════════════════════════════════════════
async def main():
    # 1. Auth & Clients
    gkey = os.environ.get("GROQ_API_KEY")
    if not gkey: sys.exit("❌ Missing GROQ_API_KEY")
    
    groq_client = Groq(api_key=gkey)
    creds = Credentials.from_authorized_user_file("token.json")
    yt = build("youtube", "v3", credentials=creds)

    # 2. Data & Assets
    market = fetch_market_data()
    frame_path = make_pulse_frame(market)
    audio_path, script = await get_ai_voice(market, groq_client)

    # 3. Video Assembly
    print("🎬 Rendering Video...")
    audio = AudioFileClip(str(audio_path))
    # Add 0.5s buffer at end
    clip = ImageClip(str(frame_path)).set_duration(audio.duration + 0.5).set_audio(audio)
    
    video_path = Path(OUT) / "final_short.mp4"
    clip.write_videofile(str(video_path), fps=30, codec="libx264", audio_codec="aac", logger=None)

    # 4. YouTube Upload
    title = f"Nifty @ {now_ist.strftime('%I:%M %p')} | Trade Setup {now_ist.strftime('%d %b')} #Shorts"
    desc = f"Today's Market Pulse:\nNifty: {market['nifty']['val']}\nBTC: {market['btc']['val']}\n\n{script}\n\n#Trading #AI360Trading"
    
    print(f"⬆️ Uploading: {title}")
    request = yt.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": desc, "categoryId": "27", "tags": ["nifty", "trading", "shorts"]},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        },
        media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
    )
    response = request.execute()
    vid_url = f"https://youtube.com/shorts/{response['id']}"
    
    # 5. Share
    share_to_meta(vid_url, market)
    print(f"✅ Success! URL: {vid_url}")

if __name__ == "__main__":
    asyncio.run(main())
