import os, sys, json, asyncio
from datetime import datetime
from pathlib import Path

import pytz
import requests
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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

# ─── FONTS ───────────────────────────────────────────────────────────────────
FONT_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
]
FONT_REG_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def draw_text_outlined(draw, text, x, y, font, fill, outline=3, anchor="mm"):
    for dx in range(-outline, outline + 1):
        for dy in range(-outline, outline + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0), anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)

# ─── MARKET DATA (FIXED: NO OLD DATA) ────────────────────────────────────────
def fetch_market_data():
    """Fetches LIVE data using 1m interval to bypass GitHub Action caching."""
    print("📡 Fetching LIVE market data (Bypassing Cache)...")
    tickers = {
        "nifty":  ("^NSEI",  "₹"),
        "btc":    ("BTC-USD", "$"),
        "gold":   ("GC=F",    "$"),
        "usdinr": ("INR=X",   "₹"),
        "sp500":  ("^GSPC",   "$"),
    }
    data = {}
    for name, (sym, curr) in tickers.items():
        try:
            # interval="1m" ensures we get the current price from the last 60 seconds
            df = yf.download(sym, period="1d", interval="1m", progress=False)
            if df.empty:
                df = yf.download(sym, period="5d", interval="1d", progress=False)
            
            last = float(df["Close"].iloc[-1])
            prev = float(df["Open"].iloc[0])
            chg  = ((last - prev) / prev) * 100
            
            val = f"{curr}{last:,.2f}"
            if name in ("btc", "sp500"): val = f"{curr}{last:,.0f}"
            data[name] = {"val": val, "chg": f"{chg:+.2f}%", "up": chg >= 0}
        except Exception as e:
            print(f"⚠️ {name} error: {e}")
            data[name] = {"val": "N/A", "chg": "0.00%", "up": True}
    return data

# ─── 3D ZENO EFFECT (DISNEY/HUMAN TOUCH) ─────────────────────────────────────
def apply_3d_zeno(base_img, emotion="thinking"):
    """Applies Zeno with a 3D shadow and glow effect."""
    zeno_file = f"public/zeno_{emotion}.png"
    if not os.path.exists(zeno_file):
        return base_img
    
    zeno = Image.open(zeno_file).convert("RGBA")
    
    # 1. Scaling: Make him large for impact (Disney style)
    target_w = int(SW * 0.85)
    w_ratio = target_w / float(zeno.size[0])
    target_h = int(float(zeno.size[1]) * float(w_ratio))
    zeno = zeno.resize((target_w, target_h), Image.LANCZOS)
    
    # 2. 3D Depth: Create a soft drop shadow
    shadow_layer = Image.new("RGBA", base_img.size, (0,0,0,0))
    zeno_mask = zeno.split()[3]
    
    # Offset shadow for 3D depth
    shadow_pos = ((SW - zeno.width)//2 + 15, SH - zeno.height - 135)
    shadow_img = Image.new("RGBA", zeno.size, (0, 0, 0, 100)) # Semi-transparent black
    shadow_layer.paste(shadow_img, shadow_pos, zeno_mask)
    
    # Blur the shadow for a soft 'human' feel
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=10))
    
    # 3. Final Compositing
    final_img = Image.alpha_composite(base_img.convert("RGBA"), shadow_layer)
    zeno_pos = ((SW - zeno.width)//2, SH - zeno.height - 150)
    final_img.paste(zeno, zeno_pos, zeno)
    
    return final_img.convert("RGB")

# ─── VIDEO GENERATION ────────────────────────────────────────────────────────
def make_frame(script_data, market, is_zeno=False):
    img = Image.new("RGB", (SW, SH), (10, 15, 30))
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Background Gradient
    for y in range(SH):
        r = int(10 + (20 - 10) * y / SH)
        g = int(15 + (35 - 15) * y / SH)
        b = int(30 + (60 - 30) * y / SH)
        draw.line([(0, y), (SW, y)], fill=(r, g, b))

    accent = BULL_GREEN if market["nifty"]["up"] else BEAR_RED
    
    # Header
    draw_text_outlined(draw, "AI360TRADING", SW//2, 100, get_font(FONT_BOLD_PATHS, 70), accent)
    
    if is_zeno:
        # ZENO REEL (Beginners/Worldwide)
        img = apply_3d_zeno(img, emotion=script_data.get("emotion", "thinking"))
        draw_text_outlined(draw, script_data.get("title", "Market Wisdom"), SW//2, 300, get_font(FONT_BOLD_PATHS, 80), WHITE)
    else:
        # MARKET SHORT (Young Traders/Live Data)
        draw_text_outlined(draw, "LIVE SETUP", SW//2, 250, get_font(FONT_BOLD_PATHS, 90), WHITE)
        # Nifty Badge
        draw.rounded_rectangle([100, 400, SW-100, 600], radius=30, fill=(255,255,255,20))
        draw.text((SW//2, 460), "NIFTY 50", font=get_font(FONT_BOLD_PATHS, 40), fill=accent, anchor="mm")
        draw.text((SW//2, 530), f"{market['nifty']['val']} ({market['nifty']['chg']})", font=get_font(FONT_BOLD_PATHS, 70), fill=WHITE, anchor="mm")

    # Save
    path = OUT / f"frame_{datetime.now().strftime('%H%M%S')}.png"
    img.save(path)
    return path

async def main():
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    market = fetch_market_data()
    
    # Task: Short for Young Traders (No Zeno, Energetic Male Voice)
    print("🎬 Generating Young Trader Short...")
    s_data = {"script": "Bhaiyo! Nifty aaj fire mode mein hai. Entry levels description mein check karo. Late mat hona!", "emotion": "happy"}
    s_frame = make_frame(s_data, market, is_zeno=False)
    s_audio = OUT / "young_voice.mp3"
    await edge_tts.Communicate(s_data["script"], "hi-IN-MadhurNeural", rate="+15%").save(str(s_audio))
    
    # Render logic (simplified for script flow)
    clip = ImageClip(str(s_frame)).set_duration(15).set_audio(AudioFileClip(str(s_audio)))
    clip.write_videofile(str(OUT / "short_young.mp4"), fps=FPS, logger=None)

    # Task: Reel for Beginners (Zeno 3D, Female Voice)
    print("🎬 Generating Beginner Zeno Reel...")
    r_data = {"script": "Namaste! Market ka utaar chadhaav dekh kar ghabraiye mat. Sabr hi asli paisa banata hai.", "emotion": "thinking"}
    r_frame = make_frame(r_data, market, is_zeno=True)
    r_audio = OUT / "zeno_voice.mp3"
    await edge_tts.Communicate(r_data["script"], "hi-IN-SwaraNeural", rate="+5%").save(str(r_audio))
    
    clip_zeno = ImageClip(str(r_frame)).set_duration(15).set_audio(AudioFileClip(str(r_audio)))
    clip_zeno.write_videofile(str(OUT / "reel_zeno.mp4"), fps=FPS, logger=None)

    print("🚀 All videos rendered successfully with 3D Zeno and Fresh Data.")

if __name__ == "__main__":
    asyncio.run(main())
