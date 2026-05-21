"""
generate_shorts.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generates Short 2 (Trade Setup) + Short 3 (Global Market Pulse).

VOICE ASSIGNMENTS:
  Short 2: hi-IN-MadhurNeural  — authoritative Hindi male, trade setups
  Short 3: en-IN-NeerjaNeural  — Indian English female, market pulse
  ZENO reel uses hi-IN-SwaraNeural (in generate_reel.py — separate)

v3.1 FIXES (May 2026):
  FIX 1 — Background music removed
    REMOVED: MUSIC_DIR, get_bg_music(), mix_audio()
    REMOVED: CompositeAudioClip, concatenate_audioclips imports
    All mix_audio() calls replaced with voice_clip directly
    Reason: public/music/ deleted — Meta was muting videos

  FIX 2 — Facebook page token fix
    get_fb_page_token() uses FACEBOOK_PAGE_ID from GitHub secrets
    Falls back to user token only if page not found

Mode: market / weekend / holiday via CONTENT_MODE env var.
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from pathlib import Path

import pytz
import requests
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont
import edge_tts
# v3.1 FIX: Removed CompositeAudioClip, concatenate_audioclips — no longer needed
from moviepy.editor import ImageClip, AudioFileClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from human_touch import ht, seo

# ─── Content Mode ─────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")
print(f"[MODE] generate_shorts.py running in mode: {CONTENT_MODE.upper()}")

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OUT = Path("output")
# v3.1 FIX: MUSIC_DIR removed — public/music/ deleted
SW, SH = 1080, 1920
FPS = 30
IST = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(IST)

os.makedirs(OUT, exist_ok=True)

VOICE_SHORT2 = "hi-IN-MadhurNeural"
VOICE_SHORT3 = "en-IN-NeerjaNeural"

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

FB_RETRY = 3
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
    px = img.load()
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

# v3.1 FIX: get_bg_music() and mix_audio() REMOVED
# All audio is TTS voice only — no background music
# Prevents Meta muting videos in countries without music rights


# ─── MARKET DATA ──────────────────────────────────────────────────────────────

def fetch_market_data():
    print("📡 Fetching LIVE market data for Shorts...")
    if CONTENT_MODE in ("holiday", "weekend"):
        print(f"📅 {CONTENT_MODE.upper()} mode — educational placeholders")
        return {
            "nifty":  {"val": "Market Closed", "chg": "Holiday",  "up": True, "raw": 0},
            "btc":    {"val": "Learn Today",   "chg": "Grow",     "up": True, "raw": 0},
            "gold":   {"val": "Plan Smart",    "chg": "Invest",   "up": True, "raw": 0},
            "usdinr": {"val": "Stay Calm",     "chg": "Patience", "up": True, "raw": 0},
            "sp500":  {"val": "Build Wealth",  "chg": "Steady",   "up": True, "raw": 0},
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
            last = t_obj.fast_info["last_price"]
            prev = t_obj.fast_info["previous_close"]
            chg  = ((last - prev) / prev) * 100
            if name == "usdinr":
                val = f"{curr}{last:.2f}"
            elif name in ("btc", "sp500"):
                val = f"{curr}{last:,.0f}"
            else:
                val = f"{curr}{last:,.2f}"
            data[name] = {"val": val, "chg": f"{chg:+.2f}%", "up": chg >= 0, "raw": last}
            print(f"  ✅ {name}: {val} ({chg:+.2f}%)")
        except Exception as e:
            print(f"  ⚠️ {name} failed: {e}")
            data[name] = {"val": "N/A", "chg": "0.00%", "up": True, "raw": 0}
    return data


def get_part1_url():
    id_path = OUT / "analysis_video_id.txt"
    if id_path.exists():
        vid_id = id_path.read_text(encoding="utf-8").strip()
        if vid_id and vid_id != "UPLOAD_FAILED":
            url = f"https://youtube.com/watch?v={vid_id}"
            print(f"🔗 Part 1 linked: {url}")
            return url
    print("⚠️ No Part 1 video ID found")
    return ""


# ══════════════════════════════════════════════════════════════════════════════
# SHORT 2 — TRADE SETUP / EDUCATION CARD
# ══════════════════════════════════════════════════════════════════════════════

def make_short2_frame(script_data, market):
    sentiment = script_data.get("sentiment", "bullish").lower()
    accent = GOLD if CONTENT_MODE in ("holiday", "weekend") else (
        BULL_GREEN if sentiment == "bullish" else
        BEAR_RED   if sentiment == "bearish" else GOLD)

    img  = gradient_bg((8, 12, 28), (15, 25, 50))
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle([(0, 0), (SW, 12)], fill=accent)
    draw.rectangle([(0, SH-12), (SW, SH)], fill=accent)
    draw_text_outlined(draw, "AI360TRADING", SW//2, 80, get_font(FONT_BOLD_PATHS, 62), accent, outline=2)

    header_label = {"holiday": "HOLIDAY LEARNING", "weekend": "WEEKEND EDUCATION"}.get(CONTENT_MODE, "TRADE SETUP")
    draw.text((SW//2, 145), header_label, font=get_font(FONT_BOLD_PATHS, 38), fill=SOFT_WHITE, anchor="mm")
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
            ("🎯 ACTION",  script_data.get("sl",      "Learn and Apply"),     GOLD),
            ("⏱ HORIZON", script_data.get("horizon", "Long Term"),            ACCENT_BLUE),
        ]
    else:
        levels = [
            ("🎯 ENTRY",   script_data.get("entry",   "Market Price"),  WHITE),
            ("📊 TARGET",  script_data.get("target",  "See Desc."),     BULL_GREEN),
            ("🛑 SL",      script_data.get("sl",      "Risk Managed"),  BEAR_RED),
            ("⏱ HORIZON", script_data.get("horizon", "Intraday"),      GOLD),
        ]

    ly = box_top + 60
    for label, value, color in levels:
        draw.text((120, ly),    label,     font=get_font(FONT_BOLD_PATHS, 36), fill=(150, 170, 210), anchor="lm")
        draw.text((SW-120, ly), str(value),font=get_font(FONT_BOLD_PATHS, 42), fill=color,           anchor="rm")
        ly += 88

    strip_y = 930
    draw.rounded_rectangle([(60, strip_y), (SW-60, strip_y+100)], radius=20, fill=(0, 0, 0, 100))
    if CONTENT_MODE in ("holiday", "weekend"):
        draw.text((SW//2, strip_y+50), "📚 EDUCATION MODE", font=get_font(FONT_BOLD_PATHS, 44), fill=GOLD, anchor="mm")
    else:
        nc = BULL_GREEN if market["nifty"]["up"] else BEAR_RED
        draw.text((120, strip_y+50),   "NIFTY",                 font=get_font(FONT_BOLD_PATHS, 38), fill=(160, 180, 220), anchor="lm")
        draw.text((SW//2, strip_y+50), market["nifty"]["val"],   font=get_font(FONT_BOLD_PATHS, 44), fill=WHITE,           anchor="mm")
        draw.text((SW-120, strip_y+50),market["nifty"]["chg"],  font=get_font(FONT_BOLD_PATHS, 40), fill=nc,              anchor="rm")

    insight = script_data.get("insight", "Learn, invest, grow — with discipline.")
    insight_lines, words, line = [], insight.split(), ""
    for w in words:
        test = (line + " " + w).strip()
        bbox = draw.textbbox((0,0), test, font=get_font(FONT_REG_PATHS, 34))
        if bbox[2]-bbox[0] > SW-140:
            if line: insight_lines.append(line)
            line = w
        else:
            line = test
    if line: insight_lines.append(line)
    iy = 1070
    for il in insight_lines[:3]:
        draw.text((SW//2, iy), il, font=get_font(FONT_REG_PATHS, 34), fill=(170, 190, 220), anchor="mm")
        iy += 48

    draw.text((SW//2, SH-200), "📱 t.me/ai360trading", font=get_font(FONT_BOLD_PATHS, 38), fill=accent, anchor="mm")
    draw.text((SW//2, SH-140), "🌐 ai360trading.in",   font=get_font(FONT_REG_PATHS, 34),  fill=SOFT_WHITE, anchor="mm")
    draw.text((SW//2, SH-80),  "⚠️ Educational Only — Not SEBI Advice",
              font=get_font(FONT_REG_PATHS, 28), fill=(100, 120, 160), anchor="mm")

    path = OUT / f"short2_{now_ist.strftime('%Y%m%d')}.png"
    img.save(str(path))
    return path


# ══════════════════════════════════════════════════════════════════════════════
# SHORT 3 — GLOBAL MARKET PULSE
# ══════════════════════════════════════════════════════════════════════════════

def make_short3_frame(script_data, market):
    sentiment = script_data.get("sentiment", "neutral").lower()
    accent = GOLD if sentiment == "neutral" else (
        BULL_GREEN if sentiment in ("bullish", "positive") else BEAR_RED)

    img  = gradient_bg((5, 10, 22), (12, 22, 45))
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle([(0, 0), (SW, 12)], fill=accent)
    draw.rectangle([(0, SH-12), (SW, SH)], fill=accent)
    draw_text_outlined(draw, "GLOBAL MARKET PULSE", SW//2, 80, get_font(FONT_BOLD_PATHS, 52), accent, outline=2)
    draw.text((SW//2, 150), now_ist.strftime("%d %b %Y • %I:%M %p IST"),
              font=get_font(FONT_REG_PATHS, 32), fill=(140, 160, 200), anchor="mm")
    draw.rectangle([(60, 180), (SW-60, 183)], fill=accent)

    markets_data = [
        ("🇮🇳 NIFTY",    market.get("nifty",  {})),
        ("₿ BTC",         market.get("btc",    {})),
        ("🥇 GOLD",       market.get("gold",   {})),
        ("💵 USD/INR",    market.get("usdinr", {})),
        ("🇺🇸 S&P 500",  market.get("sp500",  {})),
    ]

    my = 230
    for label, mkt in markets_data:
        val   = mkt.get("val", "N/A")
        chg   = mkt.get("chg", "0%")
        is_up = mkt.get("up", True)
        color = BULL_GREEN if is_up else BEAR_RED
        icon  = "▲" if is_up else "▼"

        draw.rounded_rectangle([(60, my), (SW-60, my+90)], radius=16, fill=(255,255,255,8))
        draw.text((110, my+45), label, font=get_font(FONT_BOLD_PATHS, 34), fill=(160,180,220), anchor="lm")
        draw.text((SW//2, my+45), val,  font=get_font(FONT_BOLD_PATHS, 42), fill=WHITE,        anchor="mm")
        draw.text((SW-110, my+45), f"{icon}{chg}", font=get_font(FONT_BOLD_PATHS, 38), fill=color, anchor="rm")
        my += 100

    insight = script_data.get("insight", "Global markets shaping India's trading day.")
    ilines, words, line = [], insight.split(), ""
    for w in words:
        test = (line + " " + w).strip()
        bbox = draw.textbbox((0,0), test, font=get_font(FONT_REG_PATHS, 34))
        if bbox[2]-bbox[0] > SW-140:
            if line: ilines.append(line)
            line = w
        else:
            line = test
    if line: ilines.append(line)
    iy = my + 30
    for il in ilines[:3]:
        draw.text((SW//2, iy), il, font=get_font(FONT_REG_PATHS, 34), fill=(170,190,220), anchor="mm")
        iy += 48

    draw.text((SW//2, SH-200), "📱 t.me/ai360trading", font=get_font(FONT_BOLD_PATHS, 38), fill=accent,    anchor="mm")
    draw.text((SW//2, SH-140), "🌐 ai360trading.in",   font=get_font(FONT_REG_PATHS, 34),  fill=SOFT_WHITE, anchor="mm")
    draw.text((SW//2, SH-80),  "⚠️ Educational Only — Not SEBI Advice",
              font=get_font(FONT_REG_PATHS, 28), fill=(100,120,160), anchor="mm")

    path = OUT / f"short3_{now_ist.strftime('%Y%m%d')}.png"
    img.save(str(path))
    return path


# ══════════════════════════════════════════════════════════════════════════════
# SCRIPT GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_short2_script(market: dict, part1_url: str) -> dict:
    from ai_client import ai
    nifty_val = market.get("nifty", {}).get("val", "N/A")
    nifty_chg = market.get("nifty", {}).get("chg", "0%")

    if CONTENT_MODE == "holiday":
        topic = f"Market holiday special — {HOLIDAY_NAME}. Motivational investing lesson. No live data."
    elif CONTENT_MODE == "weekend":
        topic = "Weekend trading education — patience, discipline, risk management. No live signals."
    else:
        topic = f"Today's Nifty: {nifty_val} ({nifty_chg}). Top Nifty200 swing trade setup or learning."

    cta = f"Full analysis: {part1_url}" if part1_url else "Subscribe for daily signals!"

    prompt = f"""Create a 45-second Hindi trading short script for Indian retail traders.
Topic: {topic}
Mode: {CONTENT_MODE}

Return ONLY valid JSON:
{{
  "title": "Short title max 8 words for YouTube",
  "stock": "Stock name or topic (max 3 words, English only)",
  "sentiment": "bullish or bearish or neutral",
  "entry":   "Entry price or topic point",
  "target":  "Target price or lesson",
  "sl":      "Stop loss or action",
  "horizon": "Timeframe",
  "insight": "One powerful insight sentence (English, max 15 words)",
  "script":  "45-second Hinglish spoken script 80-100 words — engaging",
  "hashtags": "#tag1 #tag2 #tag3 (5 relevant tags)"
}}"""

    print("🤖 Generating Short 2 script (Madhur voice)...")
    data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
    if data:
        print(f"  ✅ Short 2: {data.get('stock')} — {data.get('sentiment')}")
        return data
    return {
        "title": "Weekend Trading Education",
        "stock": "FINANCIAL EDUCATION",
        "sentiment": "positive",
        "entry": "Learning",
        "target": "Growth",
        "sl": "Stay Disciplined",
        "horizon": "Long Term",
        "insight": "Patience and discipline are the real edge in markets.",
        "script": "Doston, trading mein sabse important hai patience aur discipline. Market band ho ya open, seekhna kabhi band mat karo. Ek consistent trader hi long run mein jeetta hai. Subscribe karo aur join karo t.me/ai360trading.",
        "hashtags": "#Trading #StockMarket #NiftyTrading #Investing #ai360trading"
    }


def generate_short3_script(market: dict) -> dict:
    from ai_client import ai
    btc_val  = market.get("btc",   {}).get("val", "N/A")
    gold_val = market.get("gold",  {}).get("val", "N/A")
    sp5_val  = market.get("sp500", {}).get("val", "N/A")
    inr_val  = market.get("usdinr",{}).get("val", "N/A")
    nifty_val= market.get("nifty", {}).get("val", "N/A")

    if CONTENT_MODE in ("holiday", "weekend"):
        mkt_context = "Market holiday/weekend — global investing wisdom, no specific calls."
    else:
        mkt_context = f"Nifty:{nifty_val} | BTC:{btc_val} | Gold:{gold_val} | S&P500:{sp5_val} | USD/INR:{inr_val}"

    prompt = f"""Create a 45-second English/Hinglish global market pulse script for Indian traders.
Market data: {mkt_context}

Return ONLY valid JSON:
{{
  "title": "Global Market Pulse — short title",
  "sentiment": "bullish or bearish or neutral",
  "insight": "One key market insight sentence (English, max 15 words)",
  "script": "45-second Hinglish/English script 80-100 words — global context",
  "hashtags": "#GlobalMarkets #Bitcoin #Gold #SP500 #ai360trading"
}}"""

    print("🤖 Generating Short 3 script (Neerja voice)...")
    data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="en")
    if data:
        print(f"  ✅ Short 3: {data.get('sentiment')}")
        return data
    return {
        "title": "Weekend Market Wisdom",
        "sentiment": "neutral",
        "insight": "Global markets always reward the patient, disciplined investor.",
        "script": "Friends, global markets move every day. Gold, Bitcoin, S&P 500 — all connected to India. The smart trader watches globally and acts locally. Stay disciplined. Subscribe for daily insights at ai360trading.in.",
        "hashtags": "#GlobalMarkets #Bitcoin #Gold #SP500 #ai360trading"
    }


# ══════════════════════════════════════════════════════════════════════════════
# TTS
# ══════════════════════════════════════════════════════════════════════════════

async def gen_tts_async(text: str, voice: str, path: str):
    speed    = ht.get_tts_speed()
    rate_str = f"+{int((speed-1)*100)}%" if speed >= 1 else f"{int((speed-1)*100)}%"
    await edge_tts.Communicate(text, voice, rate=rate_str).save(path)

def gen_tts(text: str, voice: str, path: str):
    asyncio.run(gen_tts_async(text, voice, path))


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO RENDER — TTS ONLY (no background music)
# ══════════════════════════════════════════════════════════════════════════════

def render_short(frame_path: Path, audio_path: str, out_path: str):
    """
    Render short video — TTS voice only.
    v3.1 FIX: mix_audio() removed — no background music.
    Prevents Meta muting videos in countries without music rights.
    """
    audio_clip = AudioFileClip(audio_path)
    duration   = audio_clip.duration + 0.5
    video      = ImageClip(str(frame_path)).set_duration(duration)
    video      = video.set_audio(audio_clip)  # TTS only — no mix_audio()
    video.write_videofile(out_path, fps=FPS, codec="libx264",
                          audio_codec="aac", verbose=False, logger=None)
    print(f"✅ Short rendered: {Path(out_path).name}")
    return out_path


# ══════════════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ══════════════════════════════════════════════════════════════════════════════

def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json and os.path.exists("token.json"):
            creds_json = open("token.json").read()
        if not creds_json:
            print("❌ No YouTube credentials")
            return None
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"❌ YouTube auth: {e}")
        return None


def upload_short(video_path: str, title: str, description: str, tags: list) -> str:
    youtube = get_youtube_service()
    if not youtube: return ""
    body = {
        "snippet": {"title": title[:100], "description": description, "tags": tags, "categoryId": "22"},
        "status":  {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    print(f"🚀 Uploading: {title[:60]}...")
    try:
        req  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        resp = None
        while resp is None:
            status, resp = req.next_chunk()
            if status: print(f"  {int(status.progress()*100)}%")
        vid_id = resp["id"]
        print(f"  ✅ YouTube: https://youtube.com/shorts/{vid_id}")
        return vid_id
    except Exception as e:
        print(f"  ❌ YouTube upload failed: {e}")
        return ""


# ══════════════════════════════════════════════════════════════════════════════
# FACEBOOK PAGE TOKEN + SHARE
# ══════════════════════════════════════════════════════════════════════════════

def get_fb_page_token() -> str:
    """Exchange user token for page token using FACEBOOK_PAGE_ID."""
    user_token = os.environ.get("META_ACCESS_TOKEN", "")
    page_id    = os.environ.get("FACEBOOK_PAGE_ID", "")
    if not user_token or not page_id:
        return user_token

    try:
        resp = requests.get(
            "https://graph.facebook.com/v21.0/me/accounts",
            params={"access_token": user_token},
            timeout=15
        )
        data = resp.json().get("data", [])
        for page in data:
            if str(page.get("id")) == str(page_id):
                print(f"  ✅ Page token retrieved for page {page_id}")
                return page.get("access_token", user_token)
        print(f"  ⚠️ Page {page_id} not found in /me/accounts — using user token")
    except Exception as e:
        print(f"  ⚠️ Page token fetch failed: {e}")

    return user_token


def _fb_videos_fallback(page_id: str, page_token: str, video_path: str, caption: str) -> bool:
    """Fallback: POST to /videos endpoint (no Reels format, but no special permissions needed)."""
    print("  🔄 Trying /videos fallback...")
    try:
        with open(video_path, "rb") as f:
            video_data = f.read()
        resp = requests.post(
            f"https://graph.facebook.com/v21.0/{page_id}/videos",
            data={"description": caption, "access_token": page_token},
            files={"source": ("video.mp4", video_data, "video/mp4")},
            timeout=180
        ).json()
        if resp.get("id"):
            print(f"  ✅ Facebook video posted via /videos — ID: {resp['id']}")
            return True
        error = resp.get("error", {})
        print(f"  ❌ /videos also failed: {error.get('code')} {error.get('message','')}")
    except Exception as e:
        print(f"  ❌ /videos fallback error: {e}")
    return False


def share_to_facebook(video_path: str, caption: str) -> bool:
    """Share Hindi short to Facebook Main Page — tries /video_reels, falls back to /videos."""
    page_id = os.environ.get("FACEBOOK_PAGE_ID", "")
    if not page_id:
        print("⚠️ FACEBOOK_PAGE_ID not set — skipping Facebook share")
        return False

    page_token = get_fb_page_token()
    video_size = os.path.getsize(video_path)
    reels_perm_error = False

    for attempt in range(1, FB_RETRY+1):
        try:
            # Phase 1: Start upload session
            init = requests.post(
                f"https://graph.facebook.com/v21.0/{page_id}/video_reels",
                data={"upload_phase": "start", "access_token": page_token},
                timeout=30
            ).json()
            vid_id     = init.get("video_id")
            upload_url = init.get("upload_url")
            if not vid_id or not upload_url:
                code = init.get("error", {}).get("code", "?")
                msg  = init.get("error", {}).get("message", str(init))
                print(f"  ❌ Facebook /video_reels failed (attempt {attempt}/{FB_RETRY}): {code} — {msg}")
                if code in (200, "200") or "permission" in str(msg).lower():
                    reels_perm_error = True
                    break  # no point retrying permission errors
                time.sleep(FB_RETRY_WAIT)
                continue

            # Phase 2: Binary upload
            with open(video_path, "rb") as f:
                video_data = f.read()
            requests.post(
                upload_url,
                headers={"Authorization": f"OAuth {page_token}", "offset": "0", "file_size": str(video_size)},
                data=video_data, timeout=300
            )

            # Phase 3: Publish
            finish = requests.post(
                f"https://graph.facebook.com/v21.0/{page_id}/video_reels",
                data={"upload_phase": "finish", "video_id": vid_id,
                      "video_state": "PUBLISHED", "description": caption,
                      "access_token": page_token},
                timeout=30
            ).json()
            if finish.get("success") or finish.get("video_id"):
                print(f"  ✅ Facebook Page reel published")
                return True

        except Exception as e:
            print(f"  ⚠️ Facebook attempt {attempt}: {e}")
        time.sleep(FB_RETRY_WAIT)

    # Fallback to /videos if reels permission error
    return _fb_videos_fallback(page_id, page_token, video_path, caption)


# ══════════════════════════════════════════════════════════════════════════════
# BUILD TITLES + DESCRIPTIONS
# ══════════════════════════════════════════════════════════════════════════════

def build_title_short2(script_data: dict) -> str:
    date_tag = now_ist.strftime("#%m%d")
    if CONTENT_MODE == "holiday":
        label = HOLIDAY_NAME if HOLIDAY_NAME else "Market Holiday"
        return f"📚 {label} — ai360trading {date_tag} #Shorts"
    elif CONTENT_MODE == "weekend":
        return f"📚 Weekend Investing Lesson — ai360trading {date_tag} #Shorts"
    stock = script_data.get("stock", "Nifty")
    sent  = script_data.get("sentiment", "bullish").capitalize()
    return f"📊 {stock} {sent} Setup — ai360trading {date_tag} #Shorts"

def build_title_short3(script_data: dict) -> str:
    date_tag = now_ist.strftime("#%m%d")
    if CONTENT_MODE in ("holiday", "weekend"):
        return f"🌍 Weekend Market Wisdom — ai360trading {date_tag} #Shorts"
    return f"🌍 Global Market Pulse — ai360trading {date_tag} #Shorts"

def build_desc(script_data: dict, short_num: int, part1_url: str) -> str:
    tags   = seo.get_video_tags(mode=CONTENT_MODE, is_short=True)
    yt_tags= seo.get_youtube_safe_tags(tags)
    htags  = " ".join(f"#{t}" for t in yt_tags[:12])
    insight= script_data.get("insight", "Daily market intelligence for Indian traders.")
    cta    = f"\n▶️ Full Analysis: {part1_url}" if part1_url else ""
    return (
        f"💡 {insight}\n\n"
        f"🌐 https://ai360trading.in\n"
        f"📱 https://t.me/ai360trading{cta}\n\n"
        f"⚠️ Educational only. Not SEBI registered.\n\n"
        f"{htags}"
    )

def build_fb_caption(script_data: dict, short_num: int) -> str:
    insight = script_data.get("insight", "Daily market intelligence.")
    if CONTENT_MODE in ("holiday", "weekend"):
        return (
            f"📚 Weekend Learning!\n\n"
            f"💡 {insight}\n\n"
            f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
            f"#ai360trading #StockMarket #Trading #WeekendLearning"
        )
    stock = script_data.get("stock", "Market")
    sent  = script_data.get("sentiment", "").capitalize()
    return (
        f"📊 {stock} {sent} Signal!\n\n"
        f"💡 {insight}\n\n"
        f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
        f"⚠️ Educational only.\n"
        f"#ai360trading #StockMarket #{stock.replace(' ','')}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    today    = now_ist.strftime("%Y%m%d")
    market   = fetch_market_data()
    part1_url= get_part1_url()
    tags     = seo.get_video_tags(mode=CONTENT_MODE, is_short=True)
    yt_tags  = seo.get_youtube_safe_tags(tags)

    short2_id = ""
    short3_id = ""

    # ── SHORT 2 ───────────────────────────────────────────────────────────────
    print(f"\n─── SHORT 2 (Madhur) ────────────────────────")
    s2_data   = generate_short2_script(market, part1_url)
    s2_frame  = make_short2_frame(s2_data, market)
    s2_audio  = str(OUT / f"short2_audio_{today}.mp3")
    s2_video  = str(OUT / f"short2_{today}.mp4")
    gen_tts(s2_data.get("script", ""), VOICE_SHORT2, s2_audio)
    render_short(s2_frame, s2_audio, s2_video)

    s2_title  = build_title_short2(s2_data)
    s2_desc   = build_desc(s2_data, 2, part1_url)
    short2_id = upload_short(s2_video, s2_title, s2_desc, yt_tags)
    if short2_id:
        print(f"  ✅ YouTube: https://youtube.com/shorts/{short2_id}")
        # Facebook — Hindi only
        share_to_facebook(s2_video, build_fb_caption(s2_data, 2))

    # ── SHORT 3 ───────────────────────────────────────────────────────────────
    print(f"\n─── SHORT 3 (Neerja) ────────────────────────")
    s3_data  = generate_short3_script(market)
    s3_frame = make_short3_frame(s3_data, market)
    s3_audio = str(OUT / f"short3_audio_{today}.mp3")
    s3_video = str(OUT / f"short3_{today}.mp4")
    gen_tts(s3_data.get("script", ""), VOICE_SHORT3, s3_audio)
    render_short(s3_frame, s3_audio, s3_video)

    s3_title  = build_title_short3(s3_data)
    s3_desc   = build_desc(s3_data, 3, part1_url)
    short3_id = upload_short(s3_video, s3_title, s3_desc, yt_tags)
    if short3_id:
        print(f"  ✅ YouTube: https://youtube.com/shorts/{short3_id}")

    print(f"\n{'='*50}")
    print(f"✅ SHORTS DONE — {today} [{CONTENT_MODE.upper()}]")
    print(f"   Short 2 (Madhur): {'https://youtube.com/shorts/'+short2_id if short2_id else 'upload failed'}")
    print(f"   Short 3 (Neerja): {'https://youtube.com/shorts/'+short3_id if short3_id else 'upload failed'}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
