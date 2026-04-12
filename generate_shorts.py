"""
generate_shorts.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generates Short 2 (Trade Setup) + Short 3 (Global Market Pulse).

Short 2: Madhur voice (authoritative male) — trade setup or education card
Short 3: Swara voice (energetic female) — market pulse or weekend wisdom

Data source: yfinance fast_info['last_price'] — real-time, no 1-day lag
Mode switching: market / weekend / holiday via CONTENT_MODE env var
Platforms: YouTube Shorts (auto) + Facebook Trading Page (auto)
Target countries for ads: India, USA, UK, Brazil, UAE, Canada, Australia

Last updated: April 2026
"""

import os
import sys
import json
import time
import asyncio
import logging
import warnings
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

# ── Bug 1 Fix: Suppress noisy logs ──────────────────────────────────────────
logging.getLogger("moviepy").setLevel(logging.ERROR)
logging.getLogger("imageio").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

# ── Bug 4 Fix: Use ai_client instead of Groq directly ───────────────────────
from ai_client import ai
from human_touch import ht, seo

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# ─── Content Mode ─────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")

print(f"[MODE] generate_shorts.py running in mode: {CONTENT_MODE.upper()}")

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OUT      = Path("output")
MUSIC_DIR = Path("public/music")
SW, SH   = 1080, 1920
FPS      = 30
IST      = pytz.timezone("Asia/Kolkata")
now_ist  = datetime.now(IST)

os.makedirs(OUT, exist_ok=True)

BULL_GREEN  = (0, 210, 100)
BEAR_RED    = (220, 55, 55)
GOLD        = (255, 200, 50)
WHITE       = (255, 255, 255)
SOFT_WHITE  = (230, 240, 255)
ACCENT_BLUE = (60, 140, 255)

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

# ─── Global SEO tags ──────────────────────────────────────────────────────────
BASE_TAGS    = ["ai360trading","StockMarket","Investing","Finance","Shorts",
                "GlobalInvesting","USStocks","UKInvesting","BrazilMarket",
                "IndiaInvesting","UAEInvesting","FinancialLiteracy","Hinglish"]
MARKET_TAGS  = BASE_TAGS + ["Nifty50","TradingIndia","TradeSetup","TechnicalAnalysis","PriceAction"]
WEEKEND_TAGS = BASE_TAGS + ["WeekendLearning","PersonalFinance","WealthBuilding","MoneyMindset"]
HOLIDAY_TAGS = BASE_TAGS + ["HolidayLearning","MarketHoliday","InvestmentTips","FinancialFreedom"]

FB_RETRY      = 3
FB_RETRY_WAIT = 8

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def gradient_bg(top, bot):
    img = Image.new("RGB", (SW, SH))
    px  = img.load()
    for y in range(SH):
        c = lerp(top, bot, y / SH)
        for x in range(SW): px[x, y] = c
    return img

def draw_text_outlined(draw, text, x, y, font, fill, outline=3, anchor="mm"):
    for dx in range(-outline, outline + 1):
        for dy in range(-outline, outline + 1):
            if dx != 0 or dy != 0:
                draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0), anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)

def get_bg_music():
    day = datetime.now().weekday()
    music_map = {0:"bgmusic1.mp3", 1:"bgmusic2.mp3", 2:"bgmusic3.mp3",
                 3:"bgmusic1.mp3", 4:"bgmusic2.mp3", 5:"bgmusic3.mp3", 6:"bgmusic1.mp3"}
    f = MUSIC_DIR / music_map[day]
    if f.exists(): return f
    for f in MUSIC_DIR.glob("*.mp3"): return f
    return None

def mix_audio(voice_clip, duration):
    bg_path = get_bg_music()
    if not bg_path: return voice_clip
    try:
        bg = AudioFileClip(str(bg_path))
        if bg.duration < duration:
            loops = int(duration / bg.duration) + 1
            bg    = concatenate_audioclips([bg] * loops)
        bg = bg.subclip(0, duration).volumex(0.08)
        return CompositeAudioClip([voice_clip, bg])
    except Exception:
        return voice_clip

# ─── MARKET DATA ──────────────────────────────────────────────────────────────
def fetch_market_data():
    print("📡 Fetching LIVE market data for Shorts...")

    if CONTENT_MODE in ("holiday", "weekend"):
        print(f"📅 {CONTENT_MODE.upper()} mode — educational placeholders")
        return {
            "nifty":  {"val": "Market Closed", "chg": "Holiday", "up": True,  "raw": 0},
            "btc":    {"val": "Learn Today",   "chg": "Grow",    "up": True,  "raw": 0},
            "gold":   {"val": "Plan Smart",    "chg": "Invest",  "up": True,  "raw": 0},
            "usdinr": {"val": "Stay Calm",     "chg": "Patience","up": True,  "raw": 0},
            "sp500":  {"val": "Build Wealth",  "chg": "Steady",  "up": True,  "raw": 0},
        }

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
            t_obj = yf.Ticker(sym)
            last  = t_obj.fast_info["last_price"]
            prev  = t_obj.fast_info["previous_close"]
            chg   = ((last - prev) / prev) * 100
            if name == "usdinr":
                val = f"{curr}{last:.2f}"
            elif name in ("btc", "sp500"):
                val = f"{curr}{last:,.0f}"
            else:
                val = f"{curr}{last:,.2f}"
            data[name] = {"val": val, "chg": f"{chg:+.2f}%", "up": chg >= 0, "raw": last}
            print(f"  ✅ {name}: {val} ({chg:+.2f}%)")
        except Exception:
            try:
                import pandas as pd
                df   = yf.download(sym, period="2d", interval="1d", progress=False)
                last = float(df["Close"].iloc[-1])
                prev = float(df["Close"].iloc[-2])
                chg  = ((last - prev) / prev) * 100
                val  = f"{curr}{last:.2f}"
                data[name] = {"val": val, "chg": f"{chg:+.2f}%", "up": chg >= 0, "raw": last}
                print(f"  ✅ {name} (historical fallback): {val}")
            except Exception:
                data[name] = {"val": "N/A", "chg": "0.00%", "up": True, "raw": 0}
                print(f"  ⚠️ {name}: data unavailable — using placeholder")
    return data

def get_part1_url():
    id_path = OUT / "analysis_video_id.txt"
    if id_path.exists():
        vid_id = id_path.read_text(encoding="utf-8").strip()
        if vid_id and vid_id != "UPLOAD_FAILED":
            url = f"https://youtube.com/watch?v={vid_id}"
            print(f"🔗 Part 1 linked: {url}")
            return url
    print("⚠️ No Part 1 video ID found — running without link")
    return ""

# ══════════════════════════════════════════════════════════════════════════════
# SHORT 2 — TRADE SETUP / EDUCATION CARD
# Voice: Madhur (authoritative male)
# ══════════════════════════════════════════════════════════════════════════════

def make_short2_frame(script_data, market):
    sentiment = script_data.get("sentiment", "bullish").lower()
    accent    = GOLD if CONTENT_MODE in ("holiday", "weekend") else (
                BULL_GREEN if sentiment == "bullish" else
                BEAR_RED   if sentiment == "bearish" else GOLD)

    img  = gradient_bg((8, 12, 28), (15, 25, 50))
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle([(0, 0), (SW, 12)],     fill=accent)
    draw.rectangle([(0, SH-12), (SW, SH)], fill=accent)

    draw_text_outlined(draw, "AI360TRADING", SW//2, 80, get_font(FONT_BOLD_PATHS, 62), accent, outline=2)

    header_label = {"holiday": "HOLIDAY LEARNING", "weekend": "WEEKEND EDUCATION"}.get(CONTENT_MODE, "TRADE SETUP")
    draw.text((SW//2, 145), header_label,
              font=get_font(FONT_BOLD_PATHS, 38), fill=SOFT_WHITE, anchor="mm")
    draw.text((SW//2, 200), now_ist.strftime("%d %b %Y • %I:%M %p IST"),
              font=get_font(FONT_REG_PATHS, 32), fill=(140, 160, 200), anchor="mm")
    draw.rectangle([(60, 230), (SW-60, 233)], fill=accent)

    stock = script_data.get("stock", "FINANCIAL EDUCATION" if CONTENT_MODE in ("holiday", "weekend") else "NIFTY 50")
    draw_text_outlined(draw, stock.upper(), SW//2, 310, get_font(FONT_BOLD_PATHS, 90), WHITE, outline=2)

    badge_icon = "📚" if CONTENT_MODE in ("holiday", "weekend") else (
                 "📈" if sentiment == "bullish" else "📉" if sentiment == "bearish" else "⚖️")
    badge = f" {badge_icon} {sentiment.upper()} "
    draw.rounded_rectangle([(SW//2-160, 360), (SW//2+160, 420)], radius=20, fill=(*accent, 40))
    draw.text((SW//2, 390), badge, font=get_font(FONT_BOLD_PATHS, 36), fill=accent, anchor="mm")

    box_top = 460
    draw.rounded_rectangle([(60, box_top), (SW-60, box_top+420)], radius=30, fill=(255, 255, 255, 12))

    if CONTENT_MODE in ("holiday", "weekend"):
        levels = [
            ("📖 TOPIC",   script_data.get("entry",   "Financial Education"), WHITE),
            ("💡 LESSON",  script_data.get("target",  "See Description"),     BULL_GREEN),
            ("🎯 ACTION",  script_data.get("sl",       "Learn and Apply"),     GOLD),
            ("⏱ HORIZON", script_data.get("horizon", "Long Term"),            ACCENT_BLUE),
        ]
    else:
        levels = [
            ("🎯 ENTRY",   script_data.get("entry",   "Market Price"),   WHITE),
            ("📊 TARGET",  script_data.get("target",  "See Desc."),      BULL_GREEN),
            ("🛑 SL",      script_data.get("sl",       "Risk Managed"),   BEAR_RED),
            ("⏱ HORIZON", script_data.get("horizon", "Intraday"),        GOLD),
        ]

    ly = box_top + 60
    for label, value, color in levels:
        draw.text((120, ly),   label,        font=get_font(FONT_BOLD_PATHS, 36), fill=(150, 170, 210), anchor="lm")
        draw.text((SW-120, ly), str(value),  font=get_font(FONT_BOLD_PATHS, 42), fill=color,           anchor="rm")
        ly += 88

    strip_y = 930
    draw.rounded_rectangle([(60, strip_y), (SW-60, strip_y+100)], radius=20, fill=(0, 0, 0, 100))
    if CONTENT_MODE in ("holiday", "weekend"):
        draw.text((SW//2, strip_y+50), "📚 EDUCATION MODE",
                  font=get_font(FONT_BOLD_PATHS, 44), fill=GOLD, anchor="mm")
    else:
        nc = BULL_GREEN if market["nifty"]["up"] else BEAR_RED
        draw.text((120, strip_y+50),   "NIFTY",                    font=get_font(FONT_BOLD_PATHS, 38), fill=(160, 180, 220), anchor="lm")
        draw.text((SW//2, strip_y+50), market["nifty"]["val"],     font=get_font(FONT_BOLD_PATHS, 44), fill=WHITE,           anchor="mm")
        draw.text((SW-120, strip_y+50), market["nifty"]["chg"],    font=get_font(FONT_BOLD_PATHS, 40), fill=nc,              anchor="rm")

    insight       = script_data.get("insight", "Learn, invest, grow — with discipline.")
    insight_lines = []
    words, line   = insight.split(), ""
    for w in words:
        test = (line + " " + w).strip()
        if get_font(FONT_REG_PATHS, 36).getbbox(test)[2] < SW - 160: line = test
        else: insight_lines.append(line); line = w
    if line: insight_lines.append(line)

    iy = 1090
    for ln in insight_lines[:4]:
        draw.text((SW//2, iy), ln, font=get_font(FONT_REG_PATHS, 36), fill=SOFT_WHITE, anchor="mm")
        iy += 50

    draw.text((SW//2, 1340), "📺 Full video link in description",
              font=get_font(FONT_REG_PATHS, 34), fill=(140, 170, 220), anchor="mm")
    draw.rounded_rectangle([(60, 1400), (SW-60, 1480)], radius=15, fill=(255, 180, 0, 20))
    draw.text((SW//2, 1440), "⚠️ Educational content. Not financial advice.",
              font=get_font(FONT_REG_PATHS, 30), fill=(200, 180, 100), anchor="mm")

    draw.rounded_rectangle([(100, SH-350), (SW-100, SH-250)], radius=25, fill=accent)
    cta = "📲 SUBSCRIBE FOR DAILY LEARNING" if CONTENT_MODE in ("holiday", "weekend") else "📲 SUBSCRIBE FOR DAILY SIGNALS"
    draw_text_outlined(draw, cta, SW//2, SH-300, get_font(FONT_BOLD_PATHS, 36), (0, 0, 0), outline=1)
    draw.text((SW//2, SH-190), "ai360trading.in • t.me/ai360trading",
              font=get_font(FONT_REG_PATHS, 32), fill=(120, 150, 200), anchor="mm")

    path = OUT / f"short2_{now_ist.strftime('%Y%m%d')}.png"
    img.save(str(path), quality=95)
    return path

def generate_short2_script(market):
    if CONTENT_MODE == "holiday":
        context = (f"Today is {HOLIDAY_NAME} — Indian market holiday. "
                   f"Create educational investment lesson. Global audience: India, US, UK, Brazil, UAE.")
    elif CONTENT_MODE == "weekend":
        context = "Weekend — market closed. Educational investment lesson. No live trading data. Global audience."
    else:
        context = (f"Live market: Nifty {market['nifty']['val']} ({market['nifty']['chg']}), "
                   f"BTC {market['btc']['val']}, Gold {market['gold']['val']}, "
                   f"S&P500 {market['sp500']['val']}, USD/INR {market['usdinr']['val']}")

    if CONTENT_MODE in ("holiday", "weekend"):
        prompt = f"""Financial educator creating YouTube Shorts in Hinglish for ai360trading. Global audience: India, US, UK, Brazil.

{context}

Respond ONLY with valid JSON:
{{"stock":"FINANCIAL EDUCATION","sentiment":"positive","entry":"one key learning max 5 words","target":"what viewer gains max 5 words","sl":"one action max 5 words","horizon":"Long Term Wealth","insight":"inspiring Hinglish line max 15 words","script":"40-second Hinglish educational script. Hook. Lesson. CTA. Max 80 words."}}"""
    else:
        prompt = f"""Expert Indian stock market trader creating YouTube Shorts trade setup in Hinglish for ai360trading.

{context}

Respond ONLY with valid JSON:
{{"stock":"stock or index name","sentiment":"bullish or bearish or neutral","entry":"entry price","target":"target price","sl":"stop loss","horizon":"Intraday or Swing or Positional","insight":"one key Hinglish insight max 15 words","script":"40-second energetic Hinglish script. Hook. Setup. Subscribe CTA. Max 80 words."}}"""

    print("🤖 Generating Short 2 script (Madhur voice) via ai_client...")
    try:
        data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
        if data and "script" in data:
            print(f"  ✅ Short 2: {data.get('stock')} — {data.get('sentiment')} | via {ai.active_provider}")
            return data
        raise ValueError("Empty response")
    except Exception:
        print("  ⚠️ Script generation failed — using fallback")
        return {
            "stock": "FINANCIAL EDUCATION", "sentiment": "positive",
            "entry": "Learn Investing", "target": "Build Wealth",
            "sl": "Start Today", "horizon": "Long Term",
            "insight": "Har din kuch seekho, financially grow karo.",
            "script": "Bhaiyo! Aaj ka lesson — patience se wealth banao. Subscribe karo ai360trading!"
        }

# ══════════════════════════════════════════════════════════════════════════════
# SHORT 3 — MARKET PULSE / WEEKEND WISDOM
# Voice: Swara (energetic female)
# ══════════════════════════════════════════════════════════════════════════════

def make_short3_frame(script_data, market):
    overall_up = market["nifty"]["up"]
    accent     = GOLD if CONTENT_MODE in ("holiday", "weekend") else (BULL_GREEN if overall_up else BEAR_RED)

    img  = gradient_bg((15, 20, 40), (5, 8, 20))
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle([(0, 0), (SW, 12)],     fill=accent)
    draw.rectangle([(0, SH-12), (SW, SH)], fill=accent)

    header = {"holiday": "HOLIDAY SPECIAL", "weekend": "WEEKEND WISDOM"}.get(CONTENT_MODE, "MARKET PULSE")
    draw_text_outlined(draw, header, SW//2, 85, get_font(FONT_BOLD_PATHS, 70), accent, outline=2)
    draw.text((SW//2, 155), now_ist.strftime("%d %B %Y • %I:%M %p IST"),
              font=get_font(FONT_REG_PATHS, 34), fill=(160, 185, 220), anchor="mm")
    draw.text((SW//2, 205), "ai360trading.in",
              font=get_font(FONT_BOLD_PATHS, 30), fill=(100, 130, 180), anchor="mm")
    draw.rectangle([(60, 230), (SW-60, 233)], fill=accent)
    draw.rounded_rectangle([(60, 255), (SW-60, 560)], radius=35, fill=(255, 255, 255, 12))

    if CONTENT_MODE in ("holiday", "weekend"):
        draw.text((SW//2, 315), "TODAY'S LESSON",
                  font=get_font(FONT_BOLD_PATHS, 48), fill=(180, 205, 240), anchor="mm")
        draw_text_outlined(draw, script_data.get("mood_summary", "LEARN"), SW//2, 430, get_font(FONT_BOLD_PATHS, 80), WHITE, outline=2)
        draw_text_outlined(draw, "& GROW",                                  SW//2, 520, get_font(FONT_BOLD_PATHS, 65), accent, outline=2)
    else:
        draw.text((SW//2, 315), "NIFTY 50",
                  font=get_font(FONT_BOLD_PATHS, 48), fill=(180, 205, 240), anchor="mm")
        draw_text_outlined(draw, market["nifty"]["val"], SW//2, 430, get_font(FONT_BOLD_PATHS, 110), WHITE,  outline=2)
        draw_text_outlined(draw, market["nifty"]["chg"], SW//2, 520, get_font(FONT_BOLD_PATHS, 65),  accent, outline=2)

    if CONTENT_MODE in ("holiday", "weekend"):
        edu_items = [
            ("📚 TOPIC",  script_data.get("key_level", "Investment Basics"), 580),
            ("🌍 FOR",    "India • US • UK • Brazil • UAE",                  760),
            ("💡 TODAY",  "Use this time to plan finances",                   940),
            ("🎯 ACTION", "Subscribe for daily education",                   1120),
        ]
        for label, value, y in edu_items:
            draw.rounded_rectangle([(60, y), (SW-60, y+155)], radius=22, fill=(0, 0, 0, 90))
            draw.text((120, y+78),   label, font=get_font(FONT_BOLD_PATHS, 40), fill=(140, 165, 205), anchor="lm")
            draw.text((SW-120, y+78), value, font=get_font(FONT_BOLD_PATHS, 34), fill=GOLD,            anchor="rm")
    else:
        assets = [
            ("BITCOIN", market["btc"],    580),
            ("GOLD",    market["gold"],   760),
            ("S&P 500", market["sp500"],  940),
            ("USD/INR", market["usdinr"], 1120),
        ]
        for label, mdata, y in assets:
            uc = BULL_GREEN if mdata["up"] else BEAR_RED
            draw.rounded_rectangle([(60, y), (SW-60, y+155)], radius=22, fill=(0, 0, 0, 90))
            draw.text((120, y+78),    label,          font=get_font(FONT_BOLD_PATHS, 40), fill=(140, 165, 205), anchor="lm")
            draw.text((SW-120, y+52), mdata["val"],   font=get_font(FONT_BOLD_PATHS, 44), fill=WHITE,           anchor="rm")
            draw.text((SW-120, y+108), mdata["chg"],  font=get_font(FONT_BOLD_PATHS, 38), fill=uc,              anchor="rm")

    mood_text = script_data.get("mood_summary", "Seekho, invest karo, grow karo.")
    mood_y    = 1310
    draw.rounded_rectangle([(60, mood_y), (SW-60, mood_y+110)], radius=20, fill=(*accent, 25))
    draw.text((SW//2, mood_y+55), f"💬 {mood_text}",
              font=get_font(FONT_REG_PATHS, 33), fill=SOFT_WHITE, anchor="mm")

    key_level = script_data.get("key_level", "")
    if key_level and CONTENT_MODE == "market":
        draw.text((SW//2, 1460), f"🎯 Key Level: {key_level}",
                  font=get_font(FONT_BOLD_PATHS, 36), fill=GOLD, anchor="mm")

    draw.rounded_rectangle([(100, SH-350), (SW-100, SH-250)], radius=25, fill=accent)
    cta = "🔔 SUBSCRIBE FOR DAILY LEARNING" if CONTENT_MODE in ("holiday", "weekend") else "🔔 SUBSCRIBE FOR DAILY UPDATES"
    draw_text_outlined(draw, cta, SW//2, SH-300, get_font(FONT_BOLD_PATHS, 35), (0, 0, 0), outline=1)
    draw.text((SW//2, SH-190), "ai360trading.in • t.me/ai360trading",
              font=get_font(FONT_REG_PATHS, 32), fill=(110, 140, 190), anchor="mm")

    path = OUT / f"short3_{now_ist.strftime('%Y%m%d')}.png"
    img.save(str(path), quality=95)
    return path

def generate_short3_script(market):
    if CONTENT_MODE == "holiday":
        context = (f"Today is {HOLIDAY_NAME} — Indian market holiday. "
                   f"Educational overview short. What should investors do on holidays? Global audience: India, US, UK, Brazil, UAE.")
    elif CONTENT_MODE == "weekend":
        context = "Weekend — market closed. What should traders prepare for next week? Global educational content."
    else:
        context = (f"Live data: Nifty {market['nifty']['val']} ({market['nifty']['chg']}), "
                   f"BTC {market['btc']['val']} ({market['btc']['chg']}), "
                   f"Gold {market['gold']['val']} ({market['gold']['chg']}), "
                   f"S&P500 {market['sp500']['val']} ({market['sp500']['chg']}), "
                   f"USD/INR {market['usdinr']['val']}")

    if CONTENT_MODE in ("holiday", "weekend"):
        prompt = f"""Educational Indian market commentator for ai360trading YouTube Shorts. Global audience.

{context}

Respond ONLY with valid JSON:
{{"mood_summary":"inspiring Hinglish message max 8 words","key_level":"one investment action or topic max 5 words","script":"40-second inspiring Hinglish script. Hook Bhaiyo! What to learn. Subscribe CTA. Max 80 words."}}"""
    else:
        prompt = f"""Energetic Indian market commentator for ai360trading YouTube Shorts.

{context}

Respond ONLY with valid JSON:
{{"mood_summary":"overall market mood Hinglish max 10 words","key_level":"most important Nifty level today","script":"40-second energetic Hinglish script. Hook Bhaiyo! Nifty global cues. Subscribe CTA. Max 80 words."}}"""

    print("🤖 Generating Short 3 script (Swara voice) via ai_client...")
    try:
        data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
        if data and "script" in data:
            print(f"  ✅ Short 3: {data.get('mood_summary')} | via {ai.active_provider}")
            return data
        raise ValueError("Empty response")
    except Exception:
        print("  ⚠️ Script generation failed — using fallback")
        return {
            "mood_summary": "Seekho, grow karo, invest karo",
            "key_level":    "Financial Education",
            "script":       "Bhaiyo! Aaj market band hai. Perfect time to plan investments. Subscribe karo ai360trading!"
        }

# ─── YOUTUBE AUTH ─────────────────────────────────────────────────────────────
def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json:
            if os.path.exists("token.json"):
                with open("token.json") as f: creds_json = f.read()
            else:
                print("❌ No YouTube credentials"); return None
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        return build("youtube", "v3", credentials=creds)
    except Exception:
        return None

def upload_short(youtube, video_path, title, description, tags):
    if not youtube: return None
    body = {
        "snippet": {
            "title":       title[:100],
            "description": description,
            "tags":        tags[:30],
            "categoryId":  "27"
        },
        "status": {
            "privacyStatus":            "public",
            "selfDeclaredMadeForKids":  False
        }
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"🚀 Uploading: {title[:60]}...")
    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status: print(f"  {int(status.progress() * 100)}%")
        vid_id  = response["id"]
        vid_url = f"https://youtube.com/shorts/{vid_id}"
        print(f"  ✅ YouTube: {vid_url}")
        return vid_url
    except Exception:
        print("  ⚠️ YouTube upload failed — skipping")
        return None

# ─── FACEBOOK SHARE — Trading Page ONLY (Group removed — no followers) ────────
def share_to_facebook(short2_url, short3_url, market):
    """Posts short links to Facebook Trading Page only. Group removed."""
    token   = os.environ.get("META_ACCESS_TOKEN", "")
    page_id = os.environ.get("FACEBOOK_PAGE_ID", "")

    if not token or not page_id:
        print("⚠️ Facebook credentials missing — skipping share")
        return

    if CONTENT_MODE == "holiday":
        label = f"🎉 {HOLIDAY_NAME}" if HOLIDAY_NAME else "🎉 Market Holiday"
        msg   = (f"📚 {label} — Market band hai, learning nahi!\n\nAaj ke educational shorts:\n\n")
    elif CONTENT_MODE == "weekend":
        msg = "📖 Weekend Learning Shorts — Financial education for everyone!\n\n"
    else:
        emoji = "📈" if market["nifty"]["up"] else "📉"
        msg   = (f"{emoji} Aaj ke Market Shorts — Must Watch! 🔥\n\n"
                 f"Nifty: {market['nifty']['val']} ({market['nifty']['chg']})\n"
                 f"BTC: {market['btc']['val']} ({market['btc']['chg']})\n\n")

    if short2_url: msg += f"📊 Trade Setup Short:\n{short2_url}\n\n"
    if short3_url: msg += f"💹 Market Pulse Short:\n{short3_url}\n\n"

    if CONTENT_MODE in ("holiday", "weekend"):
        msg += ("💡 Best time to learn and plan your next investment!\n"
                "🌍 For investors: India, US, UK, Brazil, UAE\n"
                "🌐 https://ai360trading.in\n📱 https://t.me/ai360trading\n\n"
                "#ai360trading #InvestmentEducation #GlobalInvesting #Shorts")
    else:
        msg += ("Daily signals ke liye subscribe karo! 🔔\n"
                "🌐 https://ai360trading.in\n📱 https://t.me/ai360trading\n\n"
                "#ai360trading #Nifty #StockMarket #TradingIndia #Shorts")

    # Post to Trading Page ONLY — Group removed (no followers)
    for attempt in range(1, FB_RETRY + 1):
        try:
            resp   = requests.post(
                f"https://graph.facebook.com/v21.0/{page_id}/feed",
                data={"message": msg, "access_token": token},
                timeout=30
            )
            result = resp.json()
            if "id" in result:
                print(f"  ✅ Facebook Trading Page shared [{CONTENT_MODE}] — Post ID: {result['id']}")
                break
            else:
                error = result.get("error", {})
                code  = error.get("code", "?")
                emsg  = error.get("message", str(result))
                print(f"  ⚠️ Facebook Page failed (attempt {attempt}/{FB_RETRY}) — Error {code}: {emsg}")
        except Exception:
            print(f"  ⚠️ Facebook Page error (attempt {attempt}/{FB_RETRY}) — trying next")
        if attempt < FB_RETRY:
            time.sleep(FB_RETRY_WAIT)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
async def main():
    today   = now_ist.strftime("%Y%m%d")
    youtube = get_youtube_service()
    part1_url = get_part1_url()
    market    = fetch_market_data()

    tags = (HOLIDAY_TAGS if CONTENT_MODE == "holiday" else
            WEEKEND_TAGS if CONTENT_MODE == "weekend" else MARKET_TAGS)

    # ── SHORT 2 — Trade Setup (Madhur voice) ──────────────────────────────────
    print("\n─── SHORT 2 ─────────────────────────────")
    s2_data       = generate_short2_script(market)
    s2_frame      = make_short2_frame(s2_data, market)
    s2_audio_path = OUT / f"short2_voice_{today}.mp3"

    await edge_tts.Communicate(
        s2_data.get("script", "Aaj ka lesson dekhte hain!"),
        "hi-IN-MadhurNeural", rate="+10%"
    ).save(str(s2_audio_path))

    s2_voice      = AudioFileClip(str(s2_audio_path))
    s2_duration   = s2_voice.duration + 0.5
    s2_audio      = mix_audio(s2_voice, s2_duration)
    s2_video_path = OUT / f"short2_{today}.mp4"

    (ImageClip(str(s2_frame))
     .set_duration(s2_duration)
     .set_audio(s2_audio)
     .write_videofile(str(s2_video_path), fps=FPS, codec="libx264", audio_codec="aac", logger=None))
    print(f"✅ Short 2 rendered: {s2_video_path.name}")

    if CONTENT_MODE in ("holiday", "weekend"):
        label    = f"{HOLIDAY_NAME} " if CONTENT_MODE == "holiday" and HOLIDAY_NAME else "Weekend "
        s2_title = f"📚 {label}Investing Lesson — ai360trading #{today[-4:]} #Shorts"
        s2_desc  = (f"📚 {label}Special — {s2_data.get('insight', '')}\n\n"
                    f"🌍 For investors: India, USA, UK, Brazil, UAE\n"
                    + (f"📊 Full video: {part1_url}\n" if part1_url else "")
                    + "🌐 https://ai360trading.in\n📱 https://t.me/ai360trading\n"
                    "⚠️ Educational content only. Not financial advice.\n"
                    "#Education #Investing #ai360trading #GlobalInvesting #Shorts")
    else:
        s2_title = (f"{'📈' if market['nifty']['up'] else '📉'} "
                    f"{s2_data.get('stock', 'Nifty')} Trade Setup — {now_ist.strftime('%d %b')} #Shorts")
        s2_desc  = (f"Trade Setup: {s2_data.get('stock', 'Nifty')}\n"
                    f"Entry: {s2_data.get('entry', '')} | Target: {s2_data.get('target', '')} | SL: {s2_data.get('sl', '')}\n\n"
                    f"🌍 For traders: India, USA, UK, Brazil, UAE\n"
                    + (f"📊 Full Analysis: {part1_url}\n" if part1_url else "")
                    + "🌐 https://ai360trading.in\n📱 https://t.me/ai360trading\n"
                    "⚠️ Educational only. Not financial advice.\n"
                    "#Trading #Nifty #StockMarket #ai360trading #TradingIndia #Shorts")

    short2_url = upload_short(youtube, s2_video_path, s2_title, s2_desc, tags)

    # ── SHORT 3 — Market Pulse (Swara voice) ──────────────────────────────────
    print("\n─── SHORT 3 ─────────────────────────────")
    s3_data       = generate_short3_script(market)
    s3_frame      = make_short3_frame(s3_data, market)
    s3_audio_path = OUT / f"short3_voice_{today}.mp3"

    await edge_tts.Communicate(
        s3_data.get("script", "Bhaiyo! Aaj ka update!"),
        "hi-IN-SwaraNeural", rate="+12%"
    ).save(str(s3_audio_path))

    s3_voice      = AudioFileClip(str(s3_audio_path))
    s3_duration   = s3_voice.duration + 0.5
    s3_audio      = mix_audio(s3_voice, s3_duration)
    s3_video_path = OUT / f"short3_{today}.mp4"

    (ImageClip(str(s3_frame))
     .set_duration(s3_duration)
     .set_audio(s3_audio)
     .write_videofile(str(s3_video_path), fps=FPS, codec="libx264", audio_codec="aac", logger=None))
    print(f"✅ Short 3 rendered: {s3_video_path.name}")

    if CONTENT_MODE in ("holiday", "weekend"):
        label    = f"{HOLIDAY_NAME} " if CONTENT_MODE == "holiday" and HOLIDAY_NAME else "Weekend "
        s3_title = f"📚 {label}Market Wisdom — ai360trading #{today[-4:]} #Shorts"
        s3_desc  = (f"📚 {label}Special — {s3_data.get('mood_summary', '')}\n\n"
                    f"🌍 For investors: India, USA, UK, Brazil, UAE\n"
                    + (f"📊 Full video: {part1_url}\n" if part1_url else "")
                    + "🌐 https://ai360trading.in\n📱 https://t.me/ai360trading\n"
                    "#InvestmentEducation #GlobalInvesting #ai360trading #Shorts")
    else:
        s3_title = (f"Market Pulse — Nifty {market['nifty']['val']} "
                    f"{market['nifty']['chg']} | {now_ist.strftime('%d %b')} #Shorts")
        s3_desc  = (f"Market Pulse — {now_ist.strftime('%d %B %Y')}\n\n"
                    f"Nifty: {market['nifty']['val']} ({market['nifty']['chg']})\n"
                    f"BTC: {market['btc']['val']} | Gold: {market['gold']['val']}\n"
                    f"S&P500: {market['sp500']['val']} | Key Level: {s3_data.get('key_level', '')}\n\n"
                    f"🌍 For traders: India, USA, UK, Brazil, UAE\n"
                    + (f"📊 Full Analysis: {part1_url}\n" if part1_url else "")
                    + "🌐 https://ai360trading.in\n📱 https://t.me/ai360trading\n"
                    "#MarketPulse #Nifty #StockMarket #ai360trading #TradingIndia #Shorts")

    short3_url = upload_short(youtube, s3_video_path, s3_title, s3_desc, tags)

    share_to_facebook(short2_url, short3_url, market)

    print(f"\n{'='*50}")
    print(f"✅ SHORTS DONE — {today} [{CONTENT_MODE.upper()}]")
    print(f"  Short 2: {short2_url or 'upload failed'}")
    print(f"  Short 3: {short3_url or 'upload failed'}")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    asyncio.run(main())
