import os, sys, json, asyncio, textwrap
from datetime import datetime
from pathlib import Path

import pytz
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip
from groq import Groq

# ─── CONFIG ──────────────────────────────────────────────────────────────────
OUT       = Path("output")
SW, SH    = 1080, 1920
FPS       = 30
IST       = pytz.timezone("Asia/Kolkata")
now_ist   = datetime.now(IST)
os.makedirs(OUT, exist_ok=True)

# ─── COLORS ──────────────────────────────────────────────────────────────────
BULL_GREEN  = (0, 210, 100)
BEAR_RED    = (220, 55, 55)
GOLD        = (255, 200, 50)
WHITE       = (255, 255, 255)

# ─── FONTS ───────────────────────────────────────────────────────────────────
FONT_BOLD_PATHS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
FONT_REG_PATHS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

# ─── DATA HANDSHAKE (SYNC WITH MAIN VIDEO) ───────────────────────────────────
def get_synced_market_data():
    """Tries to load snapshot from generate_analysis.py first for 100% sync."""
    snap_path = OUT / f"market_snapshot_{now_ist.strftime('%Y%m%d')}.json"
    if snap_path.exists():
        print("🔗 Syncing with Main Video Data...")
        return json.loads(snap_path.read_text())
    
    # Fallback to your Live Fetch if snapshot is missing
    print("📡 Snapshot missing, performing independent LIVE fetch...")
    tickers = {"nifty": "^NSEI", "btc": "BTC-USD"}
    data = {}
    for name, sym in tickers.items():
        df = yf.download(sym, period="1d", interval="1m", progress=False)
        last = float(df["Close"].iloc[-1])
        prev = float(df["Open"].iloc[0])
        chg = ((last - prev) / prev) * 100
        data[name] = {"price": round(last, 2), "change": f"{chg:+.2f}%", "up": chg >= 0}
    return data

# ─── 3D ZENO EFFECT (ENHANCED RIM LIGHT) ─────────────────────────────────────
def apply_3d_zeno(base_img, emotion="thinking"):
    zeno_file = f"public/zeno_{emotion}.png"
    if not os.path.exists(zeno_file): return base_img
    
    zeno = Image.open(zeno_file).convert("RGBA")
    target_w = int(SW * 0.85)
    z_h = int(zeno.height * (target_w / zeno.width))
    zeno = zeno.resize((target_w, z_h), Image.LANCZOS)
    
    # Shadow
    shadow_layer = Image.new("RGBA", base_img.size, (0,0,0,0))
    mask = zeno.split()[3]
    pos = ((SW - target_w)//2, SH - z_h - 150)
    shadow_layer.paste((0,0,0,120), (pos[0]+20, pos[1]+20), mask)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(15))
    
    # Composite
    base_rgba = base_img.convert("RGBA")
    combined = Image.alpha_composite(base_rgba, shadow_layer)
    combined.paste(zeno, pos, zeno)
    return combined.convert("RGB")

# ─── DYNAMIC FRAME RENDERER ──────────────────────────────────────────────────
def render_short_frame(market, title, is_zeno=False):
    img = Image.new("RGB", (SW, SH), (10, 15, 30))
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Gradient
    for y in range(SH):
        draw.line([(0, y), (SW, y)], fill=(10, 15+int(20*y/SH), 30+int(40*y/SH)))
    
    accent = BULL_GREEN if market["nifty"]["up"] else BEAR_RED
    
    if is_zeno:
        img = apply_3d_zeno(img, "happy" if market["nifty"]["up"] else "thinking")
        draw = ImageDraw.Draw(img, "RGBA")
        draw.text((SW//2, 300), title, font=get_font(FONT_BOLD_PATHS, 80), fill=WHITE, anchor="mm")
    else:
        draw.text((SW//2, 200), "TRADE SETUP", font=get_font(FONT_BOLD_PATHS, 90), fill=WHITE, anchor="mm")
        # Nifty Price Box
        draw.rounded_rectangle([100, 400, SW-100, 650], radius=40, fill=(255,255,255,15))
        draw.text((SW//2, 480), "NIFTY 50", font=get_font(FONT_BOLD_PATHS, 50), fill=accent, anchor="mm")
        draw.text((SW//2, 570), f"{market['nifty']['price']} ({market['nifty']['change']})", font=get_font(FONT_BOLD_PATHS, 85), fill=WHITE, anchor="mm")

    path = OUT / f"frame_{'zeno' if is_zeno else 'setup'}.png"
    img.save(path)
    return path

async def main():
    market = get_synced_market_data()
    
    # 1. Young Trader Short (No Zeno)
    f1 = render_short_frame(market, "Fast Trade", False)
    a1 = OUT / "v1.mp3"
    await edge_tts.Communicate("Market alert! Nifty levels are active. Check description.", "hi-IN-MadhurNeural").save(str(a1))
    ImageClip(str(f1)).set_duration(15).set_audio(AudioFileClip(str(a1))).write_videofile(str(OUT / "short_setup.mp4"), fps=FPS, logger=None)

    # 2. Beginner Reel (3D Zeno)
    f2 = render_short_frame(market, "Zeno's Wisdom", True)
    a2 = OUT / "v2.mp3"
    await edge_tts.Communicate("Doston, trading mein sabr hi sabse bada hathyaar hai.", "hi-IN-SwaraNeural").save(str(a2))
    ImageClip(str(f2)).set_duration(15).set_audio(AudioFileClip(str(a2))).write_videofile(str(OUT / "reel_zeno.mp4"), fps=FPS, logger=None)

if __name__ == "__main__":
    asyncio.run(main())
