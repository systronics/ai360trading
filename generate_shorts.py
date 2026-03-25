import os, sys, json, asyncio
from datetime import datetime
from pathlib import Path

import pytz
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip
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
FONT_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
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

# ─── MARKET DATA (FIXED SERIES ERROR) ────────────────────────────────────────
def get_synced_market_data():
    """Tries to load snapshot first; fallbacks to LIVE 1m fetch."""
    snap_file = OUT / f"market_snapshot_{now_ist.strftime('%Y%m%d')}.json"
    if snap_file.exists():
        print("🔗 Loading Synced Market Snapshot...")
        return json.loads(snap_file.read_text())

    print("📡 Snapshot missing, performing independent LIVE fetch...")
    tickers = {"nifty": "^NSEI", "btc": "BTC-USD", "gold": "GC=F", "sp500": "^GSPC"}
    data = {}
    for name, sym in tickers.items():
        try:
            # interval='1m' ensures fresh data
            df = yf.download(sym, period="1d", interval="1m", progress=False)
            if df.empty:
                df = yf.download(sym, period="5d", interval="1d", progress=False)
            
            # Use .iloc[-1] and .item() to ensure we get a single float value, not a Series
            last = float(df["Close"].iloc[-1].item())
            prev = float(df["Open"].iloc[0].item())
            chg  = ((last - prev) / prev) * 100
            
            data[name] = {"val": f"{last:,.2f}", "chg": f"{chg:+.2f}%", "up": chg >= 0}
        except Exception as e:
            print(f"⚠️ Error fetching {name}: {e}")
            data[name] = {"val": "N/A", "chg": "0.00%", "up": True}
    return data

# ─── 3D ZENO EFFECT ──────────────────────────────────────────────────────────
def apply_3d_zeno(base_img, emotion="thinking"):
    zeno_file = f"public/zeno_{emotion}.png"
    if not os.path.exists(zeno_file): return base_img
    
    zeno = Image.open(zeno_file).convert("RGBA")
    target_w = int(SW * 0.85)
    target_h = int(zeno.height * (target_w / zeno.width))
    zeno = zeno.resize((target_w, target_h), Image.LANCZOS)
    
    shadow_layer = Image.new("RGBA", base_img.size, (0,0,0,0))
    mask = zeno.split()[3]
    pos = ((SW - target_w)//2, SH - target_h - 150)
    
    # 3D Shadow Offset
    shadow_layer.paste((0, 0, 0, 100), (pos[0]+15, pos[1]+15), mask)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=10))
    
    final_img = Image.alpha_composite(base_img.convert("RGBA"), shadow_layer)
    final_img.paste(zeno, pos, zeno)
    return final_img.convert("RGB")

# ─── FRAME RENDERER ──────────────────────────────────────────────────────────
def make_frame(script_data, market, is_zeno=False):
    img = Image.new("RGB", (SW, SH), (10, 15, 30))
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Background Gradient
    for y in range(SH):
        draw.line([(0, y), (SW, y)], fill=(10, 15+int(20*y/SH), 30+int(40*y/SH)))

    nifty_data = market.get("nifty", {"val": "N/A", "chg": "0.00%", "up": True})
    accent = BULL_GREEN if nifty_data["up"] else BEAR_RED
    
    draw_text_outlined(draw, "AI360TRADING", SW//2, 100, get_font(FONT_BOLD_PATHS, 70), accent)
    
    if is_zeno:
        img = apply_3d_zeno(img, emotion=script_data.get("emotion", "thinking"))
        draw = ImageDraw.Draw(img, "RGBA")
        draw_text_outlined(draw, script_data.get("title", "Wisdom"), SW//2, 300, get_font(FONT_BOLD_PATHS, 80), WHITE)
    else:
        draw_text_outlined(draw, "LIVE SETUP", SW//2, 250, get_font(FONT_BOLD_PATHS, 90), WHITE)
        draw.rounded_rectangle([100, 400, SW-100, 600], radius=30, fill=(255,255,255,20))
        draw.text((SW//2, 460), "NIFTY 50", font=get_font(FONT_BOLD_PATHS, 40), fill=accent, anchor="mm")
        draw.text((SW//2, 530), f"{nifty_data['val']} ({nifty_data['chg']})", font=get_font(FONT_BOLD_PATHS, 70), fill=WHITE, anchor="mm")

    path = OUT / f"frame_{datetime.now().strftime('%H%M%S')}.png"
    img.save(path)
    return path

async def main():
    market = get_synced_market_data()
    
    # Short 2: Trade Setup
    print("🎬 Rendering Short 2...")
    s_data = {"script": "Bhaiyo! Nifty fire mode mein hai. Entry levels description mein check karo!", "emotion": "happy"}
    s_frame = make_frame(s_data, market, is_zeno=False)
    s_audio = OUT / "s2.mp3"
    await edge_tts.Communicate(s_data["script"], "hi-IN-MadhurNeural", rate="+15%").save(str(s_audio))
    
    clip2 = ImageClip(str(s_frame)).set_duration(15).set_audio(AudioFileClip(str(s_audio)))
    clip2.write_videofile(str(OUT / "short2.mp4"), fps=FPS, logger=None)

    # Short 3: Zeno Wisdom
    print("🎬 Rendering Short 3...")
    r_data = {"script": "Namaste! Market mein sabr hi asli paisa hai. Jaldbazi mat kijiye.", "emotion": "thinking", "title": "Zeno Wisdom"}
    r_frame = make_frame(r_data, market, is_zeno=True)
    r_audio = OUT / "s3.mp3"
    await edge_tts.Communicate(r_data["script"], "hi-IN-SwaraNeural", rate="+5%").save(str(r_audio))
    
    clip3 = ImageClip(str(r_frame)).set_duration(15).set_audio(AudioFileClip(str(r_audio)))
    clip3.write_videofile(str(OUT / "short3.mp4"), fps=FPS, logger=None)

    print("🚀 Process Complete.")

if __name__ == "__main__":
    asyncio.run(main())
