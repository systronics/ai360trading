"""
AI360Trading — Daily Shorts Generator
======================================
Short 2: Best slide clip from today's analysis video (cropped vertical)
Short 3: Live market pulse — Nifty/BTC/Gold with Hinglish voice

Runs after generate_analysis.py has already uploaded today's video.
Both upload to same @ai360trading YouTube channel.
"""

import os, sys, json, asyncio, re, time
from datetime import datetime
from pathlib import Path

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

# ── Setup ──
OUT  = "output"
SW, SH = 1080, 1920   # vertical shorts format
os.makedirs(OUT, exist_ok=True)

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

FONT_BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
             "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
             "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"]
FONT_REG  = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
             "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
             "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"]

def font(c, s):
    for p in c:
        if os.path.exists(p): return ImageFont.truetype(p, s)
    return ImageFont.load_default()

def lerp(c1, c2, t):
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

def gbg(top, bot, w=SW, h=SH):
    img = Image.new("RGB", (w, h)); px = img.load()
    for y in range(h):
        c = lerp(top, bot, y/h)
        for x in range(w): px[x, y] = c
    return img


# ══════════════════════════════════════════════════════════
# MARKET DATA
# ══════════════════════════════════════════════════════════
def quick_price(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1d",
                         progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if len(df) >= 2:
            last = round(float(df["Close"].iloc[-1]), 2)
            prev = round(float(df["Close"].iloc[-2]), 2)
            chg  = round((last-prev)/prev*100, 2)
            return {"price": last, "chg": chg, "up": chg >= 0}
    except: pass
    return {"price": "N/A", "chg": 0, "up": True}

def fetch_market():
    print("📡 Fetching live market data...")
    data = {}
    tickers = {
        "nifty":   ("^NSEI",    "₹",  True),
        "bitcoin": ("BTC-USD",  "$",  False),
        "gold":    ("GC=F",     "$",  False),
        "sp500":   ("^GSPC",    "$",  False),
        "usdinr":  ("INR=X",    "₹",  False),
    }
    for name, (tk, curr, is_inr) in tickers.items():
        d = quick_price(tk)
        if d["price"] != "N/A":
            price = d["price"]
            if is_inr:
                formatted = f"₹{price:,.0f}"
            elif name == "bitcoin":
                formatted = f"${price:,.0f}"
            elif name == "usdinr":
                formatted = f"₹{price:.2f}"
            else:
                formatted = f"${price:,.2f}"
            data[name] = {
                "formatted": formatted,
                "chg":       f"{'+' if d['up'] else ''}{d['chg']:.2f}%",
                "up":        d["up"],
                "raw":       price,
            }
            arrow = "▲" if d["up"] else "▼"
            print(f"  ✓ {name}: {formatted} {arrow}{d['chg']:+.2f}%")
    return data


# ══════════════════════════════════════════════════════════
# SHORT 2 — ANALYSIS SLIDE CLIP
# ══════════════════════════════════════════════════════════
def make_short2_frame(market: dict, analysis_url: str) -> Path:
    """
    Create a vertical 1080x1920 frame showing today's best trade setup.
    Uses live market data — no dependency on analysis video file.
    """
    nifty  = market.get("nifty",   {})
    btc    = market.get("bitcoin", {})
    gold   = market.get("gold",    {})
    sp500  = market.get("sp500",   {})

    is_bull = nifty.get("up", True)
    bg_top  = (6,16,10)  if is_bull else (22,6,6)
    bg_bot  = (4,32,18)  if is_bull else (42,10,10)
    accent  = (0,210,100) if is_bull else (255,70,50)
    accent2 = (0,160,75)  if is_bull else (195,45,35)

    img  = gbg(bg_top, bg_bot)
    draw = ImageDraw.Draw(img, "RGBA")

    # Top bar
    draw.rectangle([(0,0),(SW,10)], fill=accent)

    # AI360Trading branding
    draw.text((SW//2, 60), "AI360Trading",
              fill=accent, font=font(FONT_BOLD, 52), anchor="mm")
    draw.rectangle([(SW//2-220, 90),(SW//2+220, 97)], fill=accent)

    # Date
    draw.text((SW//2, 120), datetime.now().strftime("%d %B %Y  |  %A"),
              fill=(150,200,170) if is_bull else (200,150,150),
              font=font(FONT_REG, 28), anchor="mm")

    # Nifty big display
    draw.rounded_rectangle([(60, 160),(SW-60, 380)], radius=20, fill=(0,0,0,100))
    draw.text((SW//2, 210), "NIFTY 50",
              fill=(150,200,170) if is_bull else (200,150,150),
              font=font(FONT_REG, 32), anchor="mm")
    draw.text((SW//2, 295), nifty.get("formatted","N/A"),
              fill=(255,255,255), font=font(FONT_BOLD, 96), anchor="mm")
    chg_clr = accent
    draw.text((SW//2, 355), nifty.get("chg",""),
              fill=chg_clr, font=font(FONT_BOLD, 44), anchor="mm")

    # Global markets grid
    draw.text((SW//2, 420), "Global Markets",
              fill=(180,210,200) if is_bull else (210,180,180),
              font=font(FONT_BOLD, 30), anchor="mm")

    markets = [
        ("S&P 500", sp500),
        ("Bitcoin", btc),
        ("Gold",    gold),
    ]
    grid_y = 460
    for i, (label, mkt) in enumerate(markets):
        x = 80 + i * 310
        clr = (0,210,100) if mkt.get("up",True) else (255,70,50)
        draw.rounded_rectangle([(x, grid_y),(x+280, grid_y+130)],
                               radius=12, fill=(0,0,0,80))
        draw.text((x+140, grid_y+30), label,
                  fill=(180,200,220), font=font(FONT_REG, 22), anchor="mm")
        draw.text((x+140, grid_y+72), str(mkt.get("formatted","N/A")),
                  fill=(255,255,255), font=font(FONT_BOLD, 32), anchor="mm")
        draw.text((x+140, grid_y+105), str(mkt.get("chg","")),
                  fill=clr, font=font(FONT_BOLD, 26), anchor="mm")

    # Trade setup box
    draw.rounded_rectangle([(60, 620),(SW-60, 980)], radius=20, fill=(0,0,0,110))
    draw.text((SW//2, 665), "TODAY'S TRADE SETUP",
              fill=accent, font=font(FONT_BOLD, 34), anchor="mm")
    draw.rectangle([(120, 685),(SW-120, 690)], fill=(*accent[:3], 100))

    setup_lines = [
        ("Direction",  "BULLISH" if is_bull else "BEARISH"),
        ("Entry zone", f"{nifty.get('formatted','N/A')} area"),
        ("Target",     "Previous resistance"),
        ("Stop loss",  "Below today's low"),
        ("Strategy",   "Swing / Positional"),
    ]
    sy = 710
    for label, value in setup_lines:
        draw.text((120, sy), label,
                  fill=(150,190,170) if is_bull else (190,150,150),
                  font=font(FONT_REG, 26))
        draw.text((SW-120, sy), value,
                  fill=(255,255,255), font=font(FONT_BOLD, 26), anchor="ra")
        sy += 52
        draw.rectangle([(120, sy-4),(SW-120, sy-3)],
                       fill=(255,255,255,20))

    # Watch full video CTA
    draw.rounded_rectangle([(60, 1010),(SW-60, 1120)], radius=16,
                           fill=(*accent[:3], 180))
    draw.text((SW//2, 1050), "Watch full analysis video",
              fill=(0,30,15) if is_bull else (30,0,0),
              font=font(FONT_BOLD, 32), anchor="mm")
    draw.text((SW//2, 1090), "Link in description",
              fill=(0,50,25) if is_bull else (50,0,0),
              font=font(FONT_REG, 26), anchor="mm")

    # Hashtags
    tags = "#Nifty #StockMarket #Trading #Shorts #AI360Trading"
    draw.text((SW//2, 1160), tags,
              fill=(80,130,100) if is_bull else (130,80,80),
              font=font(FONT_REG, 24), anchor="mm")

    # ZENO placeholder (simple character silhouette)
    draw.rounded_rectangle([(SW//2-160, 1220),(SW//2+160, 1620)],
                           radius=20, fill=(0,0,0,60))
    draw.text((SW//2, 1410), "ZENO",
              fill=(*accent[:3], 100), font=font(FONT_BOLD, 80), anchor="mm")
    draw.text((SW//2, 1490), "ai360trading.in",
              fill=(*accent[:3], 80), font=font(FONT_REG, 28), anchor="mm")

    # ZENO image if available
    zeno_dir = Path("public/image")
    if zeno_dir.exists():
        zeno_files = list(zeno_dir.glob("zeno_happy*.png")) + \
                     list(zeno_dir.glob("zeno_celebrating*.png")) + \
                     list(zeno_dir.glob("zeno_confident*.png"))
        if not zeno_files:
            zeno_files = list(zeno_dir.glob("zeno_*.png"))
        if zeno_files:
            try:
                zeno = Image.open(str(zeno_files[0])).convert("RGBA")
                zw   = 280
                zh   = int(zw * zeno.height / zeno.width)
                zeno = zeno.resize((zw, zh), Image.LANCZOS)
                img.paste(zeno, (SW//2 - zw//2, 1230), zeno)
            except: pass

    # Bottom bar
    draw.rectangle([(0,SH-10),(SW,SH)], fill=accent)
    draw.text((SW//2, SH-35), "Educational only. Not financial advice.",
              fill=(80,120,100) if is_bull else (120,80,80),
              font=font(FONT_REG, 22), anchor="mm")

    path = Path(OUT) / f"short2_frame_{datetime.now().strftime('%Y%m%d')}.png"
    img.save(str(path), quality=95)
    return path


def make_short2_script(market: dict, groq_client) -> str:
    nifty  = market.get("nifty",   {})
    btc    = market.get("bitcoin", {})
    gold   = market.get("gold",    {})
    is_bull = nifty.get("up", True)

    prompt = f"""You are a sharp Hinglish trading analyst. Write a 45-50 second YouTube Shorts script.

LIVE DATA:
Nifty: {nifty.get('formatted','N/A')} ({nifty.get('chg','')})
Bitcoin: {btc.get('formatted','N/A')} ({btc.get('chg','')})
Gold: {gold.get('formatted','N/A')} ({gold.get('chg','')})
Market direction: {'BULLISH' if is_bull else 'BEARISH'}

Rules:
- Hinglish only (Hindi + English mix)
- Start with shocking hook: "Aaj Nifty ne kuch aisa kiya..."
- Mention exact Nifty price and change
- Give one specific trade idea (entry zone, target, stop loss)
- End with: "Full analysis ke liye description mein link hai!"
- Total: 90-100 words exactly
- Energetic, fast-paced, confident tone

Return ONLY the script text, nothing else."""

    resp = groq_client.chat.completions.create(
        messages=[{"role":"user","content":prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.7, max_tokens=300)
    return resp.choices[0].message.content.strip()


async def generate_short2(market: dict, analysis_url: str,
                           groq_client, yt_client) -> str:
    """Generate and upload Short 2 — analysis trade setup clip."""
    print("\n📊 Generating Short 2 — Analysis Trade Setup...")
    today = datetime.now().strftime("%Y%m%d")

    # Frame
    frame_path = make_short2_frame(market, analysis_url)
    print(f"  ✓ Frame created: {frame_path}")

    # Script + voice
    script = make_short2_script(market, groq_client)
    print(f"  ✓ Script: {script[:60]}...")
    audio_path = Path(OUT) / f"short2_voice_{today}.mp3"
    await edge_tts.Communicate(script, "hi-IN-SwaraNeural",
                                rate="+8%").save(str(audio_path))
    print(f"  ✓ Voice saved")

    # Video assembly
    audio  = AudioFileClip(str(audio_path))
    dur    = max(audio.duration + 1, 45)
    frame  = (ImageClip(str(frame_path))
              .set_duration(dur)
              .fx(fadein, 0.3))
    final  = CompositeVideoClip([frame], size=(SW, SH)).set_audio(audio)

    video_path = Path(OUT) / f"short2_{today}.mp4"
    final.write_videofile(str(video_path), fps=30, codec="libx264",
                          audio_codec="aac", bitrate="3000k",
                          verbose=False, logger=None)
    print(f"  ✓ Video: {video_path}")

    # Upload
    nifty   = market.get("nifty", {})
    is_bull = nifty.get("up", True)
    title   = (f"Nifty {nifty.get('formatted','')}"
               f" {'UP' if is_bull else 'DOWN'} {nifty.get('chg','')} — "
               f"Trade Setup {datetime.now().strftime('%d %b %Y')} #Shorts")
    title   = title[:100]

    description = f"""📊 Nifty Trade Setup — {datetime.now().strftime('%d %B %Y')}

Nifty 50: {nifty.get('formatted','N/A')} ({nifty.get('chg','')})
Bitcoin: {market.get('bitcoin',{}).get('formatted','N/A')}
Gold: {market.get('gold',{}).get('formatted','N/A')}

Watch full market analysis: {analysis_url}

🌐 ai360trading.in | 📱 t.me/ai360trading

#Nifty #StockMarket #Trading #TechnicalAnalysis #Shorts
#NiftyAnalysis #IntradayTrading #SwingTrading #AI360Trading
#StockMarketIndia #NSE #ShareMarket #NiftyPrediction"""

    tags = ["nifty","stock market","trading","shorts","nifty analysis",
            "intraday","swing trading","technical analysis","ai360trading",
            "nifty today","stock market india","nse","share market",
            "nifty prediction","market analysis"]

    req = yt_client.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title":title,"description":description,"tags":tags,
                        "categoryId":"27","defaultLanguage":"hi",
                        "defaultAudioLanguage":"hi"},
            "status":  {"privacyStatus":"public","selfDeclaredMadeForKids":False},
        },
        media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True),
    )
    resp = req.execute()
    vid_id = resp["id"]
    url = f"https://youtube.com/shorts/{vid_id}"
    print(f"  ✅ Short 2 uploaded: {url}")
    return url


# ══════════════════════════════════════════════════════════
# SHORT 3 — MARKET PULSE
# ══════════════════════════════════════════════════════════
def make_short3_frame(market: dict) -> Path:
    """Create animated market pulse card — vertical 1080x1920."""
    nifty  = market.get("nifty",   {})
    btc    = market.get("bitcoin", {})
    gold   = market.get("gold",    {})
    sp500  = market.get("sp500",   {})
    usdinr = market.get("usdinr",  {})

    is_bull = nifty.get("up", True)
    bg_top  = (4, 8, 24)
    bg_bot  = (8, 16, 48)
    accent  = (0,210,100) if is_bull else (255,70,50)

    img  = gbg(bg_top, bg_bot)
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle([(0,0),(SW,12)], fill=accent)
    draw.rectangle([(0,SH-12),(SW,SH)], fill=accent)

    # Header
    draw.text((SW//2, 70), "AI360Trading",
              fill=accent, font=font(FONT_BOLD, 56), anchor="mm")
    draw.text((SW//2, 120), "Live Market Pulse",
              fill=(180,200,230), font=font(FONT_BOLD, 32), anchor="mm")
    draw.text((SW//2, 158), datetime.now().strftime("%d %B %Y  •  %I:%M %p IST"),
              fill=(120,150,190), font=font(FONT_REG, 26), anchor="mm")
    draw.rectangle([(80,180),(SW-80,185)], fill=(*accent[:3],60))

    # Nifty hero
    draw.rounded_rectangle([(50,200),(SW-50,460)], radius=24, fill=(0,0,0,100))
    nifty_clr = (0,220,110) if is_bull else (255,70,50)
    draw.text((SW//2, 255), "NIFTY 50",
              fill=(160,200,230), font=font(FONT_REG, 34), anchor="mm")
    draw.text((SW//2, 345), nifty.get("formatted","N/A"),
              fill=(255,255,255), font=font(FONT_BOLD, 100), anchor="mm")
    draw.text((SW//2, 420), nifty.get("chg",""),
              fill=nifty_clr, font=font(FONT_BOLD, 48), anchor="mm")

    # Market cards grid
    cards = [
        ("S&P 500", sp500,  (0, 490),   (SW//2-10, 690)),
        ("Bitcoin", btc,    (SW//2+10,490), (SW-50,  690)),
        ("Gold",    gold,   (0, 710),   (SW//2-10, 910)),
        ("USD/INR", usdinr, (SW//2+10,710), (SW-50,  910)),
    ]
    for label, mkt, tl, br in cards:
        clr = (0,210,100) if mkt.get("up",True) else (255,70,50)
        draw.rounded_rectangle([tl, br], radius=16, fill=(0,0,0,90))
        mx = (tl[0]+br[0])//2; my = (tl[1]+br[1])//2
        draw.text((mx, tl[1]+38), label,
                  fill=(160,190,220), font=font(FONT_REG, 24), anchor="mm")
        draw.text((mx, my+10), str(mkt.get("formatted","N/A")),
                  fill=(255,255,255), font=font(FONT_BOLD, 34), anchor="mm")
        draw.text((mx, br[1]-30), str(mkt.get("chg","")),
                  fill=clr, font=font(FONT_BOLD, 28), anchor="mm")

    # Sentiment bar
    sent_txt = "MARKET BULLISH TODAY" if is_bull else "MARKET BEARISH TODAY"
    draw.rounded_rectangle([(50,930),(SW-50,1010)], radius=14,
                           fill=(*accent[:3],180))
    draw.text((SW//2, 970), sent_txt,
              fill=(0,30,15) if is_bull else (255,240,240),
              font=font(FONT_BOLD, 34), anchor="mm")

    # ZENO character
    zeno_dir = Path("public/image")
    zeno_placed = False
    if zeno_dir.exists():
        mood_files = (list(zeno_dir.glob("zeno_happy*.png")) +
                      list(zeno_dir.glob("zeno_celebrating*.png"))) if is_bull else \
                     (list(zeno_dir.glob("zeno_sad*.png")) +
                      list(zeno_dir.glob("zeno_fear*.png")))
        if not mood_files:
            mood_files = list(zeno_dir.glob("zeno_*.png"))
        if mood_files:
            try:
                zeno = Image.open(str(mood_files[0])).convert("RGBA")
                zw   = 380
                zh   = int(zw * zeno.height / zeno.width)
                zeno = zeno.resize((zw, zh), Image.LANCZOS)
                paste_y = 1040
                if paste_y + zh > SH - 200:
                    zh_new = SH - 200 - paste_y
                    zw_new = int(zw * zh_new / zh)
                    zeno   = zeno.resize((zw_new, zh_new), Image.LANCZOS)
                    zw, zh = zw_new, zh_new
                img.paste(zeno, (SW//2 - zw//2, paste_y), zeno)
                zeno_placed = True
            except: pass

    if not zeno_placed:
        draw.text((SW//2, 1300), "ZENO",
                  fill=(*accent[:3],60), font=font(FONT_BOLD,100), anchor="mm")

    # CTA
    draw.rounded_rectangle([(50,1640),(SW-50,1760)], radius=16, fill=(0,0,0,100))
    draw.text((SW//2, 1680), "Subscribe for daily signals",
              fill=(180,210,230), font=font(FONT_BOLD, 32), anchor="mm")
    draw.text((SW//2, 1720), "ai360trading.in | t.me/ai360trading",
              fill=(120,160,200), font=font(FONT_REG, 26), anchor="mm")

    draw.text((SW//2, 1810),
              "#Nifty #Bitcoin #Gold #StockMarket #Shorts #AI360Trading",
              fill=(80,110,150), font=font(FONT_REG, 22), anchor="mm")
    draw.text((SW//2, 1850), "Educational only. Not financial advice.",
              fill=(60,90,130), font=font(FONT_REG, 20), anchor="mm")

    path = Path(OUT) / f"short3_frame_{datetime.now().strftime('%Y%m%d')}.png"
    img.save(str(path), quality=95)
    return path


def make_short3_script(market: dict, groq_client) -> str:
    nifty  = market.get("nifty",   {})
    btc    = market.get("bitcoin", {})
    gold   = market.get("gold",    {})
    usdinr = market.get("usdinr",  {})

    prompt = f"""You are ZENO — a friendly Hinglish market commentator.
Write a 35-40 second YouTube Shorts market pulse script.

LIVE DATA (use exact numbers):
Nifty: {nifty.get('formatted','N/A')} ({nifty.get('chg','')})
Bitcoin: {btc.get('formatted','N/A')} ({btc.get('chg','')})
Gold: {gold.get('formatted','N/A')} ({gold.get('chg','')})
USD/INR: {usdinr.get('formatted','N/A')}

Rules:
- Pure Hinglish — natural Hindi + English mix
- Start with: "Bhai sun, aaj ka market update!"
- Mention ALL 4 numbers naturally in conversation
- One line market sentiment at end
- End with: "Like karo aur subscribe karo daily updates ke liye!"
- Total: 70-80 words exactly
- Energetic, like telling a friend market news

Return ONLY the script, nothing else."""

    resp = groq_client.chat.completions.create(
        messages=[{"role":"user","content":prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.8, max_tokens=200)
    return resp.choices[0].message.content.strip()


async def generate_short3(market: dict, groq_client, yt_client) -> str:
    """Generate and upload Short 3 — market pulse."""
    print("\n📈 Generating Short 3 — Market Pulse...")
    today = datetime.now().strftime("%Y%m%d")

    frame_path = make_short3_frame(market)
    print(f"  ✓ Frame created: {frame_path}")

    script = make_short3_script(market, groq_client)
    print(f"  ✓ Script: {script[:60]}...")

    audio_path = Path(OUT) / f"short3_voice_{today}.mp3"
    await edge_tts.Communicate(script, "hi-IN-MadhurNeural",
                                rate="+5%").save(str(audio_path))
    print(f"  ✓ Voice saved")

    audio = AudioFileClip(str(audio_path))
    dur   = max(audio.duration + 1, 35)
    frame = (ImageClip(str(frame_path))
             .set_duration(dur)
             .fx(fadein, 0.3))
    final = CompositeVideoClip([frame], size=(SW, SH)).set_audio(audio)

    video_path = Path(OUT) / f"short3_{today}.mp4"
    final.write_videofile(str(video_path), fps=30, codec="libx264",
                          audio_codec="aac", bitrate="3000k",
                          verbose=False, logger=None)
    print(f"  ✓ Video: {video_path}")

    nifty   = market.get("nifty",{})
    is_bull = nifty.get("up", True)
    title   = (f"Nifty {nifty.get('formatted','')} | "
               f"Bitcoin {market.get('bitcoin',{}).get('formatted','')} | "
               f"Gold {market.get('gold',{}).get('formatted','')} | "
               f"{datetime.now().strftime('%d %b')} #Shorts")
    title   = title[:100]

    description = f"""🔴 LIVE Market Pulse — {datetime.now().strftime('%d %B %Y')}

📊 Nifty 50: {nifty.get('formatted','N/A')} ({nifty.get('chg','')})
₿ Bitcoin: {market.get('bitcoin',{}).get('formatted','N/A')} ({market.get('bitcoin',{}).get('chg','')})
🥇 Gold: {market.get('gold',{}).get('formatted','N/A')} ({market.get('gold',{}).get('chg','')})
💵 USD/INR: {market.get('usdinr',{}).get('formatted','N/A')}

Market is {'BULLISH' if is_bull else 'BEARISH'} today.

🌐 ai360trading.in | 📱 t.me/ai360trading

#Nifty #Bitcoin #Gold #StockMarket #Shorts #MarketUpdate
#NiftyToday #CryptoUpdate #GoldPrice #AI360Trading
#StockMarketIndia #GlobalMarkets #TradingUpdate"""

    tags = ["nifty today","bitcoin price","gold price","market update",
            "shorts","stock market","nifty","bitcoin","gold","ai360trading",
            "market pulse","live market","nifty analysis","crypto update",
            "trading update","global markets"]

    req = yt_client.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title":title,"description":description,"tags":tags,
                        "categoryId":"27","defaultLanguage":"hi",
                        "defaultAudioLanguage":"hi"},
            "status":  {"privacyStatus":"public","selfDeclaredMadeForKids":False},
        },
        media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True),
    )
    resp   = req.execute()
    vid_id = resp["id"]
    url    = f"https://youtube.com/shorts/{vid_id}"
    print(f"  ✅ Short 3 uploaded: {url}")
    return url


# ══════════════════════════════════════════════════════════
# FACEBOOK SHARE — both shorts
# ══════════════════════════════════════════════════════════
def share_to_facebook(short2_url: str, short3_url: str, market: dict):
    META_TOKEN = os.environ.get("META_ACCESS_TOKEN","")
    PAGE_ID    = os.environ.get("FACEBOOK_PAGE_ID","")
    GROUP_ID   = os.environ.get("FACEBOOK_GROUP_ID","")
    GRAPH      = "https://graph.facebook.com/v21.0"

    if not META_TOKEN:
        print("⚠️  META_ACCESS_TOKEN not set — skipping Facebook")
        return

    nifty   = market.get("nifty",{})
    today   = datetime.now().strftime("%d %B %Y")
    is_bull = nifty.get("up", True)

    msg = (
        f"📊 Aaj ke market shorts — {today}\n\n"
        f"Nifty: {nifty.get('formatted','N/A')} {nifty.get('chg','')}\n\n"
        f"🎬 Trade Setup Short:\n{short2_url}\n\n"
        f"📈 Market Pulse Short:\n{short3_url}\n\n"
        f"{'📈 Market bullish hai aaj!' if is_bull else '📉 Market bearish hai aaj!'}\n\n"
        f"🌐 ai360trading.in | 📱 t.me/ai360trading\n\n"
        f"#Nifty #StockMarket #Shorts #AI360Trading #Trading"
    )

    for entity_id in [PAGE_ID, GROUP_ID]:
        if entity_id:
            try:
                r = requests.post(
                    f"{GRAPH}/{entity_id}/feed",
                    data={"message":msg,"link":short2_url,
                          "access_token":META_TOKEN},
                    timeout=15)
                label = "Page" if entity_id==PAGE_ID else "Group"
                print(f"  ✅ Facebook {label}: {r.json().get('id','error')}")
            except Exception as e:
                print(f"  ❌ Facebook failed: {e}")


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
async def main():
    gkey = os.environ.get("GROQ_API_KEY")
    if not gkey: sys.exit("❌ GROQ_API_KEY not set")

    if not os.path.exists("token.json"):
        sys.exit("❌ token.json missing")

    groq_client = Groq(api_key=gkey)
    creds       = Credentials.from_authorized_user_file("token.json")
    yt_client   = build("youtube","v3",credentials=creds)

    # Get analysis video URL (created by generate_analysis.py earlier today)
    analysis_url = "https://youtube.com/@ai360trading"
    try:
        with open(f"{OUT}/analysis_video_id.txt") as f:
            vid_id = f.read().strip()
            analysis_url = f"https://youtube.com/watch?v={vid_id}"
        print(f"✅ Linking to today's analysis: {analysis_url}")
    except:
        print("⚠️  Analysis video ID not found — using channel URL")

    # Fetch market data once — used by both shorts
    market = fetch_market()

    # Generate both shorts
    short2_url = await generate_short2(market, analysis_url, groq_client, yt_client)
    short3_url = await generate_short3(market, groq_client, yt_client)

    # Share to Facebook
    print("\n📢 Sharing to Facebook...")
    share_to_facebook(short2_url, short3_url, market)

    # Save IDs for SYSTEM reference
    today = datetime.now().strftime("%Y%m%d")
    with open(f"{OUT}/shorts_{today}.json","w") as f:
        json.dump({"short2":short2_url,"short3":short3_url,"date":today},f)

    print(f"\n🎉 Both shorts complete!")
    print(f"   Short 2 (Trade Setup): {short2_url}")
    print(f"   Short 3 (Market Pulse): {short3_url}")


if __name__ == "__main__":
    asyncio.run(main())
