import os, sys, json, asyncio, re, time
from datetime import datetime
from pathlib import Path

import requests
import yfinance as yf
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from moviepy.video.fx.all import fadein
from groq import Groq
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# ── CONFIG ──
OUT = "output"
SW, SH = 1080, 1920 # 9:16 Vertical
os.makedirs(OUT, exist_ok=True)

# Helper for consistent Branding Colors
BULL_GREEN = (0, 210, 100)
BEAR_RED = (255, 70, 50)
DARK_BG = (10, 15, 30)

def get_font(size, bold=False):
    """Fallback font loader for Linux/GitHub Actions environments."""
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

# ══════════════════════════════════════════════════════════
# MARKET DATA ENGINE
# ══════════════════════════════════════════════════════════
def fetch_market():
    """Fetches real-time data for Nifty, BTC, and Gold."""
    tickers = {"nifty": "^NSEI", "btc": "BTC-USD", "gold": "GC=F"}
    results = {}
    for name, sym in tickers.items():
        try:
            data = yf.download(sym, period="2d", interval="1d", progress=False)
            last = float(data['Close'].iloc[-1])
            prev = float(data['Close'].iloc[-2])
            chg = ((last - prev) / prev) * 100
            results[name] = {
                "val": f"{last:,.2f}",
                "chg": f"{chg:+.2f}%",
                "up": chg >= 0
            }
        except:
            results[name] = {"val": "N/A", "chg": "0%", "up": True}
    return results

# ══════════════════════════════════════════════════════════
# VISUAL FRAME GENERATOR (Short 3: Market Pulse)
# ══════════════════════════════════════════════════════════
def create_pulse_frame(market):
    """Creates a high-end dark mode market dashboard."""
    img = Image.new("RGB", (SW, SH), DARK_BG)
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Glow effect at top
    accent = BULL_GREEN if market['nifty']['up'] else BEAR_RED
    draw.rectangle([0, 0, SW, 20], fill=accent)
    
    # Branding
    draw.text((SW//2, 150), "AI360TRADING", font=get_font(80, True), fill=accent, anchor="mm")
    draw.text((SW//2, 230), "LIVE MARKET PULSE", font=get_font(40), fill=(200, 200, 200), anchor="mm")
    
    # Nifty Box
    draw.rounded_rectangle([100, 350, SW-100, 700], radius=30, fill=(20, 30, 50))
    draw.text((SW//2, 420), "NIFTY 50", font=get_font(50), fill=(150, 150, 150), anchor="mm")
    draw.text((SW//2, 530), market['nifty']['val'], font=get_font(120, True), fill=(255, 255, 255), anchor="mm")
    draw.text((SW//2, 630), market['nifty']['chg'], font=get_font(60, True), fill=accent, anchor="mm")
    
    # Crypto & Gold Row
    # BTC
    draw.rounded_rectangle([100, 750, 520, 1000], radius=20, fill=(20, 30, 50))
    draw.text((310, 800), "BITCOIN", font=get_font(30), fill=(150, 150, 150), anchor="mm")
    draw.text((310, 880), f"${market['btc']['val']}", font=get_font(45, True), fill=(255, 255, 255), anchor="mm")
    
    # GOLD
    draw.rounded_rectangle([560, 750, SW-100, 1000], radius=20, fill=(20, 30, 50))
    draw.text((770, 800), "GOLD", font=get_font(30), fill=(150, 150, 150), anchor="mm")
    draw.text((770, 880), f"${market['gold']['val']}", font=get_font(45, True), fill=(255, 255, 255), anchor="mm")
    
    # Footer CTA
    draw.text((SW//2, SH-200), "Subscribe for Daily Signals", font=get_font(40, True), fill=accent, anchor="mm")
    draw.text((SW//2, SH-130), "ai360trading.in", font=get_font(30), fill=(100, 100, 100), anchor="mm")

    path = Path(OUT) / "pulse_frame.png"
    img.save(path)
    return path

# ══════════════════════════════════════════════════════════
# MAIN EXECUTOR
# ══════════════════════════════════════════════════════════
async def generate_shorts():
    print("🚀 Starting Shorts Production...")
    market = fetch_market()
    
    # 1. Create Pulse Short (Short 3)
    frame = create_pulse_frame(market)
    
    # 2. Voiceover (Fast & Energetic)
    script = (f"Bhai suno, aaj ka market pulse! Nifty trade kar raha hai {market['nifty']['val']} par. "
              f"Bitcoin aur Gold mein bhi heavy movement hai. "
              "Check out the full analysis for tomorrow's targets. Like aur Subscribe karo!")
    
    audio_path = Path(OUT) / "short_voice.mp3"
    await edge_tts.Communicate(script, "hi-IN-MadhurNeural", rate="+15%").save(str(audio_path))
    
    # 3. Assemble Video
    audio = AudioFileClip(str(audio_path))
    clip = ImageClip(str(frame)).set_duration(audio.duration).set_audio(audio)
    
    video_path = Path(OUT) / "market_pulse_short.mp4"
    clip.write_videofile(str(video_path), fps=30, codec="libx264", audio_codec="aac", logger=None)
    
    print(f"✅ Short generated: {video_path}")

if __name__ == "__main__":
    asyncio.run(generate_shorts())
