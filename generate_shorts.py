"""
generate_shorts.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v3.12 (2026-07-19): hook prompts now STRONGLY PREFER a real number from the
  data as the hook's first word (never invented) — number-first hooks stop
  the scroll better than word-first. Captions gain a rotating free-calculator
  plug automatically via money_funnel v1.1 (no code change here).

v3.11 (2026-07-14): RETENTION PACK — completion-rate is the Shorts algorithm's
  #1 signal and our avg watch time was stuck at ~0:17 on ~45s videos.
  1. SCRIPTS CUT to ~20-25s (55-70 words, was 80-100): a short people FINISH
     beats a long one they abandon.
  2. PAYOFF-AT-END structure: the hook opens a question; the prompt now forces
     the answer/most-valuable line to be the FINAL sentence (hold to the end).
  3. MOTION on the frame: slow Ken Burns zoom (1.0→1.08 over the video) on the
     previously 100% static info-card — screen now visibly moves the whole time.
     Fully fail-open → any error renders the old static frame.
  4. Spoken CTA tightened to ~2s (long like/share/subscribe tail was where
     viewers swiped out; the description/pinned comment still carry the funnel).

v3.10 (2026-06-08): Weekend shorts used ONE hardcoded prompt → near-identical
  "patience/discipline" videos every weekend. Added _WEEKEND_THEMES rotation
  (by ISO week); short2 and short3 now teach different weekly themes for variety.

Generates Short 2 (Trade Setup) + Short 3 (Global Market Pulse).

VOICE ASSIGNMENTS:
  Short 2: hi-IN-MadhurNeural  — authoritative Hindi male, trade setups
  Short 3: en-IN-NeerjaNeural  — Indian English female, market pulse
  ZENO reel uses hi-IN-SwaraNeural (in generate_reel.py — separate)

UPLOAD TARGETS:
  Short 2 (Hindi):   YouTube ✅ | Facebook AI360Trading Page ✅ | Instagram ✅
  Short 3 (English): YouTube ✅ | Facebook AI360Trading Page ✅ | Instagram ✅

v3.9 (2026-06-07):
  ADD — Real CURIOSITY HOOK on the in-feed cover (retention fix). The AI now
    returns a dedicated "hook" field (max 6 words, curiosity gap — number/result/
    bold question/mistake, NOT a label); main() feeds it to the hook frame instead
    of the "STOCK SENTIMENT" label. Falls back to the old label if absent.
    Pairs with hook_helper HOOK_SECONDS 1.4→2.0 so the hook is readable.
    Goal: lift the ~2-5s average watch time that was killing reach.

v3.8 (2026-06-02):
  ADD — Edge TTS 503 retry in gen_tts_async() (4x, 5/15/30s backoff + non-empty
    check). Transient wss://speech.platform.bing.com 503 now self-heals in-run.

v3.7 (2026-05-31):
  FIX — English Short 3 was leaking markdown (a literal "**" got spoken by TTS
    and shown in captions) and mixing Hindi. Now: scripts run through
    _sanitize_script() → ht.humanize() (strips markdown) before TTS/captions/
    frame/SEO, and the Short 3 prompt is ENGLISH-ONLY (no Hindi/Devanagari).

v3.6 (2026-05-31):
  ADD — bold-text HOOK intro frame (via hook_helper.py) on Short 2 + Short 3.
    Prepends a ~1.4s stop-scroll hook card; narration shifts to start after
    the hook so burned-in captions stay synced. Fully fail-open → any error
    falls back to the hook-less render. Makes the in-feed cover (YouTube/IG/FB)
    a bold hook instead of the busy info-card.

v3.5 (2026-05-31):
  ADD — bold-text stop-scroll thumbnail for Short 2 + Short 3.
    Minimal cover (1 huge headline + 1 punch line + sentiment colour),
    set as the YouTube custom thumbnail. Fully fail-open: a thumbnail error
    never blocks the render or the upload. Drives CTR on Search / channel
    Shorts grid / Browse / shared links.

v3.4 (2026-05-31):
  ADD — burned-in captions on Short 2 + Short 3 via caption_helper.py
    (Pillow-rendered, proportionally timed, fully fail-open → never breaks render).

v3.3 (May 2026):
  ADD — Instagram Reels upload for Short 2 + Short 3
    Uses same resumable upload flow as upload_facebook.py v2.5
    INSTAGRAM_BUSINESS_ACCOUNT_ID from GitHub Secrets
    Polls until FINISHED (max 5 min) then publishes
    On failure: saves caption to output/instagram_short_caption.txt

v3.2 FIX (May 2026):
  FIX — get_fb_page_token() updated to match upload_facebook.py v2.5
    Primary: GET /{page_id}?fields=access_token (direct — avoids pagination)
    Fallback: /me/accounts with limit=200

v3.1 FIXES (May 2026):
  FIX 1 — Background music removed
    REMOVED: MUSIC_DIR, get_bg_music(), mix_audio()
    Reason: public/music/ deleted — Meta was muting videos

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
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from human_touch import ht, seo, ai_disclosure

# Money funnel (free Telegram → membership + broker referrals + comment prompt).
# Fail-open: if the module is missing, descriptions just skip the extra block.
try:
    import money_funnel as mf
except Exception:
    mf = None


def _funnel(lang="hi", compact=False):
    """Return the income CTA block, or '' on any problem (never breaks a post)."""
    try:
        return mf.funnel_block(lang=lang, compact=compact) if mf else ""
    except Exception:
        return ""

# ─── Content Mode ─────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")
print(f"[MODE] generate_shorts.py running in mode: {CONTENT_MODE.upper()}")

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OUT = Path("output")
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

FB_RETRY      = 3
FB_RETRY_WAIT = 8
GRAPH_BASE    = "https://graph.facebook.com/v21.0"

INSTAGRAM_BUSINESS_ACCOUNT_ID = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "17841400933677509")
IG_POLL_MAX  = 30
IG_POLL_WAIT = 10


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


# ─── BOLD-TEXT THUMBNAIL (stop-scroll cover for Shorts) ──────────────────────
# v3.5 (2026-05-31): The video frame is a busy info-card — poor at stopping a
# scroll. This builds a deliberately MINIMAL bold-text thumbnail (1 huge headline
# + 1 punch line) used as the YouTube custom thumbnail. In the in-feed Shorts
# player YouTube still shows a video frame, but this cover drives CTR on Search,
# the channel Shorts grid, Browse and shared links (Telegram/WhatsApp/Facebook).
# Fully fail-open: any error here is caught by the caller and never breaks render.

def _wrap_to_width(draw, text, font, max_w):
    words, lines, line = text.split(), [], ""
    for w in words:
        test = (line + " " + w).strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines


def build_short_thumbnail(headline: str, subline: str, accent, badge: str, out_name: str) -> Path:
    """Clean bold-text stop-scroll thumbnail. Saved as JPEG (well under YouTube's
    2 MB thumbnail limit). Caller wraps this fail-open."""
    img  = gradient_bg((6, 10, 26), (14, 26, 54))
    draw = ImageDraw.Draw(img, "RGBA")

    # Accent frame top + bottom
    draw.rectangle([(0, 0), (SW, 18)], fill=accent)
    draw.rectangle([(0, SH-18), (SW, SH)], fill=accent)

    # Brand badge — top
    draw.rounded_rectangle([(40, 50), (470, 132)], radius=18, fill=accent)
    draw.text((255, 91), "AI360TRADING", font=get_font(FONT_BOLD_PATHS, 50),
              fill=(0, 0, 0), anchor="mm")

    # Category badge
    draw.text((SW//2, 205), badge, font=get_font(FONT_BOLD_PATHS, 46),
              fill=(185, 205, 240), anchor="mm")

    # Headline — huge, centered, auto-fit to max 3 lines
    size   = 150
    f_head = get_font(FONT_BOLD_PATHS, size)
    lines  = _wrap_to_width(draw, headline.upper(), f_head, SW - 120)
    while len(lines) > 3 and size > 90:
        size  -= 12
        f_head = get_font(FONT_BOLD_PATHS, size)
        lines  = _wrap_to_width(draw, headline.upper(), f_head, SW - 120)

    total_h = len(lines) * (size + 18)
    ty = (SH - total_h) // 2 - 60
    for line in lines[:3]:
        for dx, dy in [(-4, 4), (4, -4), (-4, -4), (4, 4)]:
            draw.text((SW//2+dx, ty+dy), line, font=f_head, fill=(0, 0, 0, 220), anchor="mm")
        draw.text((SW//2, ty), line, font=f_head, fill=(255, 210, 0), anchor="mm")
        ty += size + 18

    # Supporting line — white on dark strip
    if subline:
        f_sub     = get_font(FONT_BOLD_PATHS, 54)
        sub_lines = _wrap_to_width(draw, subline, f_sub, SW - 160)[:2]
        strip_top = ty + 30
        strip_h   = len(sub_lines) * 68 + 30
        draw.rounded_rectangle([(50, strip_top), (SW-50, strip_top+strip_h)],
                               radius=20, fill=(0, 0, 0, 150))
        sy = strip_top + 48
        for sl in sub_lines:
            draw.text((SW//2, sy), sl, font=f_sub, fill=(255, 255, 255), anchor="mm")
            sy += 68

    # Footer CTA
    draw.text((SW//2, SH-95), "▶  Watch • Learn • Subscribe",
              font=get_font(FONT_BOLD_PATHS, 40), fill=accent, anchor="mm")

    path = OUT / out_name
    img.convert("RGB").save(str(path), "JPEG", quality=85)
    print(f"  🖼️  Thumbnail built: {path.name}")
    return path


def short2_thumb_text(script_data: dict):
    """Pick a punchy headline/subline/accent/badge for the Short 2 thumbnail."""
    if CONTENT_MODE in ("holiday", "weekend"):
        return ("WEEKEND TRADING LESSON",
                script_data.get("insight", "Patience + discipline = profit"),
                GOLD, "📚 LEARN TODAY")
    stock  = script_data.get("stock", "NIFTY")
    sent   = script_data.get("sentiment", "bullish").lower()
    accent = BULL_GREEN if sent == "bullish" else BEAR_RED if sent == "bearish" else GOLD
    arrow  = "📈" if sent == "bullish" else "📉" if sent == "bearish" else "⚖️"
    return (f"{stock} {sent.upper()}",
            script_data.get("insight", "Today's trade setup inside"),
            accent, f"{arrow} TRADE SETUP")


def short3_thumb_text(script_data: dict):
    """Pick headline/subline/accent/badge for the Short 3 (global pulse) thumbnail."""
    sent   = script_data.get("sentiment", "neutral").lower()
    accent = BULL_GREEN if sent in ("bullish", "positive") else \
             BEAR_RED if sent in ("bearish", "negative") else GOLD
    return ("GLOBAL MARKETS TODAY",
            script_data.get("insight", "Nifty • Gold • Bitcoin • S&P 500"),
            accent, "🌍 MARKET PULSE")


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
        draw.text((120, ly),    label,      font=get_font(FONT_BOLD_PATHS, 36), fill=(150, 170, 210), anchor="lm")
        draw.text((SW-120, ly), str(value), font=get_font(FONT_BOLD_PATHS, 42), fill=color,           anchor="rm")
        ly += 88

    strip_y = 930
    draw.rounded_rectangle([(60, strip_y), (SW-60, strip_y+100)], radius=20, fill=(0, 0, 0, 100))
    if CONTENT_MODE in ("holiday", "weekend"):
        draw.text((SW//2, strip_y+50), "📚 EDUCATION MODE", font=get_font(FONT_BOLD_PATHS, 44), fill=GOLD, anchor="mm")
    else:
        nc = BULL_GREEN if market["nifty"]["up"] else BEAR_RED
        draw.text((120, strip_y+50),    "NIFTY",                 font=get_font(FONT_BOLD_PATHS, 38), fill=(160, 180, 220), anchor="lm")
        draw.text((SW//2, strip_y+50),  market["nifty"]["val"],  font=get_font(FONT_BOLD_PATHS, 44), fill=WHITE,           anchor="mm")
        draw.text((SW-120, strip_y+50), market["nifty"]["chg"],  font=get_font(FONT_BOLD_PATHS, 40), fill=nc,              anchor="rm")

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

    draw.text((SW//2, SH-200), "📱 t.me/ai360trading", font=get_font(FONT_BOLD_PATHS, 38), fill=accent,    anchor="mm")
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
        ("🇮🇳 NIFTY",   market.get("nifty",  {})),
        ("₿ BTC",        market.get("btc",    {})),
        ("🥇 GOLD",      market.get("gold",   {})),
        ("💵 USD/INR",   market.get("usdinr", {})),
        ("🇺🇸 S&P 500", market.get("sp500",  {})),
    ]

    my = 230
    for label, mkt in markets_data:
        val   = mkt.get("val", "N/A")
        chg   = mkt.get("chg", "0%")
        is_up = mkt.get("up", True)
        color = BULL_GREEN if is_up else BEAR_RED
        icon  = "▲" if is_up else "▼"

        draw.rounded_rectangle([(60, my), (SW-60, my+90)], radius=16, fill=(255,255,255,8))
        draw.text((110, my+45),    label,          font=get_font(FONT_BOLD_PATHS, 34), fill=(160,180,220), anchor="lm")
        draw.text((SW//2, my+45),  val,            font=get_font(FONT_BOLD_PATHS, 42), fill=WHITE,         anchor="mm")
        draw.text((SW-110, my+45), f"{icon}{chg}", font=get_font(FONT_BOLD_PATHS, 38), fill=color,         anchor="rm")
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

# Weekend shorts used ONE hardcoded prompt → every weekend produced near-identical
# "patience/discipline" videos (visible as duplicate "PATIENCE IS KEY" shorts).
# Rotate a small curriculum by ISO week so each weekend covers a fresh theme.
_WEEKEND_THEMES = [
    "risk management — position sizing and where to place a stop-loss",
    "the psychology of patience — why overtrading destroys returns",
    "compounding — how small, consistent gains build real wealth",
    "reading candlestick charts — what each candle is telling you",
    "support and resistance — the foundation under every trade",
    "trend following vs trying to catch tops and bottoms",
    "building a simple written trading plan and actually sticking to it",
    "diversification — why one trade should never sink your account",
    "FOMO and revenge trading — the two costliest beginner mistakes",
    "keeping a trade journal — how disciplined traders keep improving",
]

def _weekend_theme(offset: int = 0) -> str:
    import datetime as _dt
    wk = _dt.date.today().isocalendar()[1]
    return _WEEKEND_THEMES[(wk + offset) % len(_WEEKEND_THEMES)]


def generate_short2_script(market: dict, part1_url: str) -> dict:
    from ai_client import ai
    nifty_val = market.get("nifty", {}).get("val", "N/A")
    nifty_chg = market.get("nifty", {}).get("chg", "0%")

    if CONTENT_MODE == "holiday":
        topic = f"Market holiday special — {HOLIDAY_NAME}. Motivational investing lesson. No live data."
    elif CONTENT_MODE == "weekend":
        topic = f"Weekend trading education on: {_weekend_theme()}. Teach this ONE theme clearly. No live signals."
    else:
        topic = f"Today's Nifty: {nifty_val} ({nifty_chg}). Top Nifty200 swing trade setup or learning."

    # Ride live search demand — hint trending terms to the AI (fail-open).
    try:
        from trending_keywords import get_trending
        _tr = get_trending("finance", 5)
        if _tr:
            topic += f" Trending searches to reference if relevant: {', '.join(_tr)}."
    except Exception:
        pass

    cta = f"Full analysis: {part1_url}" if part1_url else "Subscribe for daily signals!"

    prompt = f"""Create a 20-25 second HINGLISH trading short script for Indian retail traders.
HINGLISH = Hindi + English mixed, written in Roman/Latin script (NOT Devanagari) —
the natural way Indian traders talk: Hindi sentence flow with English trading terms
(support, resistance, breakout, target, stop-loss, trend). This keeps the core
Indian audience engaged AND lets global viewers follow along.
Topic: {topic}
Mode: {CONTENT_MODE}

Return ONLY valid JSON:
{{
  "hook":    "SCROLL-STOPPING opening line for the in-feed cover frame. MAX 6 words. Hinglish (Roman script). STRONGLY PREFER a REAL number from the data above (a %, a ₹ amount, or a level) as the FIRST word when possible — never invent a number. Create a CURIOSITY GAP using that number, a result, a bold question, or a mistake — NEVER a plain label. GOOD: '18% bhaaga ye stock aaj', 'Ye galti 5000 le dubti hai', 'Nifty girega par ye chadhega'. BAD: 'TCS Bullish', 'Trade Setup', 'Market Update'.",
  "title": "UNIQUE YouTube title for TODAY, max 8 words — MUST contain one real number from the data (a level, ₹ or % move). NEVER a generic repeatable label like 'Trade Setup' or 'Market Update'.",
  "stock": "Stock name or topic (max 3 words, English only)",
  "sentiment": "bullish or bearish or neutral",
  "entry":   "Entry price or topic point",
  "target":  "Target price or lesson",
  "sl":      "Stop loss or action",
  "horizon": "Timeframe",
  "insight": "One powerful insight sentence (English, max 15 words)",
  "script":  "20-25 second Hinglish spoken script, 55-70 words MAX. STRUCTURE (completion-rate rules): (1) open with a punchy 1-line QUESTION or bold claim that creates suspense in the first 2 seconds; (2) 2-3 short value sentences; (3) THE ANSWER/PAYOFF to the opening question MUST be the FINAL sentence — the single most valuable line comes LAST so viewers hold to the end. ONE idea only, never three.",
  "hashtags": "exactly 5 sharp tags, mix broad + niche e.g. #Nifty50 #ShareMarket #Intraday #StockMarketIndia #ai360trading"
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
        "hook": "Market band? Phir bhi seekho",
        "insight": "Patience and discipline are the real edge in markets.",
        "script": "Doston, trading mein sabse important hai patience aur discipline. Market band ho ya open, seekhna kabhi band mat karo. Ek consistent trader hi long run mein jeetta hai. Subscribe karo aur join karo t.me/ai360trading.",
        "hashtags": "#Trading #StockMarket #NiftyTrading #Investing #ai360trading"
    }


def generate_short3_script(market: dict) -> dict:
    from ai_client import ai
    btc_val   = market.get("btc",    {}).get("val", "N/A")
    gold_val  = market.get("gold",   {}).get("val", "N/A")
    sp5_val   = market.get("sp500",  {}).get("val", "N/A")
    inr_val   = market.get("usdinr", {}).get("val", "N/A")
    nifty_val = market.get("nifty",  {}).get("val", "N/A")

    if CONTENT_MODE in ("holiday", "weekend"):
        mkt_context = f"Market holiday/weekend — global investing wisdom on: {_weekend_theme(offset=5)}. No specific calls."
    else:
        mkt_context = f"Nifty:{nifty_val} | BTC:{btc_val} | Gold:{gold_val} | S&P500:{sp5_val} | USD/INR:{inr_val}"

    prompt = f"""Create a 20-25 second ENGLISH global market pulse script for Indian traders.
Market data: {mkt_context}

LANGUAGE RULE: English ONLY. Do NOT use Hindi words or Devanagari script — this
video is voiced by an English (en-IN) speaker. No markdown, no asterisks.

Return ONLY valid JSON:
{{
  "hook":    "SCROLL-STOPPING opening line for the in-feed cover frame. MAX 6 words. ENGLISH only. STRONGLY PREFER a REAL number from the data above (a % move or a level) as the FIRST word when possible — never invent a number. Create a CURIOSITY GAP using that number, a result, or a bold question — NEVER a plain label. GOOD: '18% overnight — this moved', 'US markets just did this', 'Gold is flashing a warning'. BAD: 'Global Market Pulse', 'Market Update'.",
  "title": "UNIQUE YouTube title for TODAY, max 8 words, ENGLISH — MUST contain one real number from the data (an index level or % move). NEVER a generic repeatable label like 'Global Market Pulse' or 'Market Update'.",
  "sentiment": "bullish or bearish or neutral",
  "insight": "One key market insight sentence (English, max 15 words)",
  "script": "20-25 second ENGLISH-ONLY script, 55-70 words MAX (no Hindi words). STRUCTURE (completion-rate rules): (1) open with a punchy 1-line QUESTION or bold claim in the first 2 seconds; (2) 2-3 short value sentences; (3) THE ANSWER/PAYOFF to the opening question MUST be the FINAL sentence so viewers hold to the end. ONE idea only. Plain text only — no markdown or asterisks.",
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
        "hook": "Global markets just shifted",
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
    # Edge TTS (wss://speech.platform.bing.com) intermittently returns 503 /
    # WSServerHandshakeError. Retry with backoff so a transient blip self-heals
    # in-run instead of failing the whole job.
    last_err = None
    for attempt in range(1, 5):  # 4 tries: 5/15/30s backoff
        try:
            await edge_tts.Communicate(text, voice, rate=rate_str).save(path)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                return
            raise RuntimeError("edge_tts produced empty audio file")
        except Exception as e:
            last_err = e
            print(f"  [TTS] attempt {attempt}/4 failed: {e}")
            if attempt < 4:
                await asyncio.sleep([5, 15, 30][attempt - 1])
    raise RuntimeError(f"TTS failed after 4 attempts: {last_err}")

def gen_tts(text: str, voice: str, path: str):
    asyncio.run(gen_tts_async(text, voice, path))

# Spoken subscribe call-to-action appended to every voiced script.
# v3.11: tightened to ~2s — on a 25s short a 4-5s like/share/subscribe tail was
# where viewers swiped out (killing completion rate, the algorithm's #1 signal).
# The description + pinned comment still carry the full funnel.
_CTA_AUDIO = {
    "hi": " Roz ka setup chahiye? Subscribe karein.",
    "en": " Daily setups — subscribe.",
}
def _with_cta(script: str, lang: str = "hi") -> str:
    s   = (script or "").strip()
    low = s.lower()
    # Skip if the AI script already asks for like + (share/subscribe)
    if "like" in low and ("share" in low or "subscribe" in low):
        return s
    return (s + _CTA_AUDIO.get(lang, _CTA_AUDIO["hi"])).strip()


def _sanitize_script(data: dict, lang: str) -> dict:
    """Strip markdown / AI-isms from the AI text fields so nothing leaks into
    the spoken narration, the burned-in captions, the on-screen frame, or the
    YouTube/FB/IG title+description (e.g. a stray '**' the model returned)."""
    if not isinstance(data, dict):
        return data
    for k in ("hook", "script", "insight", "title", "stock", "entry", "target", "sl", "horizon"):
        v = data.get(k)
        if isinstance(v, str):
            data[k] = ht.humanize(v, lang)
    return data


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO RENDER — TTS ONLY
# ══════════════════════════════════════════════════════════════════════════════

def render_short(frame_path: Path, audio_path: str, out_path: str, spoken_text: str = "",
                 hook_text: str = "", hook_accent=GOLD, srt_path: str = "", srt_lang: str = "hi"):
    audio_clip = AudioFileClip(audio_path)
    duration   = audio_clip.duration + 0.5
    video      = ImageClip(str(frame_path)).set_duration(duration)

    # v3.11 MOTION (retention): slow Ken Burns zoom 1.0→1.08 across the video so
    # the previously 100% static info-card visibly moves the whole time — motion
    # is what stops the swipe reflex after the hook. Centered composite keeps the
    # frame edge-to-edge while it grows. FULLY FAIL-OPEN → static frame on error.
    try:
        # moviepy 1.0.3 resize still calls Image.ANTIALIAS (removed in Pillow 10+)
        from PIL import Image as _PILImage
        if not hasattr(_PILImage, "ANTIALIAS"):
            _PILImage.ANTIALIAS = _PILImage.LANCZOS
        _d = max(duration, 0.1)
        zoomed = video.resize(lambda t: 1.0 + 0.08 * (t / _d)).set_position(("center", "center"))
        video  = CompositeVideoClip([zoomed], size=(SW, SH)).set_duration(duration)
        print("  ✅ Ken Burns motion applied")
    except Exception as e:
        print(f"  ⚠️ motion skipped (fail-open, static frame): {e}")
        video = ImageClip(str(frame_path)).set_duration(duration)

    # Build an .srt subtitle track (for YouTube auto-translate). Cues are
    # offset by the hook length so they stay in sync with the shifted audio.
    if srt_path and spoken_text:
        try:
            from subtitle_helper import build_srt
            from hook_helper import HOOK_SECONDS
            build_srt(spoken_text, audio_clip.duration, srt_path,
                      start_offset=(HOOK_SECONDS if hook_text else 0.0))
        except Exception as e:
            print(f"  ⚠️ subtitle skipped (fail-open): {e}")

    # Burned-in captions (muted-autoplay retention + accessibility). Fail-open:
    # any caption error leaves the original caption-less video untouched.
    if spoken_text:
        try:
            from caption_helper import add_captions
            video = add_captions(video, spoken_text, audio_clip.duration, (SW, SH), FONT_BOLD_PATHS)
        except Exception as e:
            print(f"  ⚠️ captions unavailable, rendering without (fail-open): {e}")

    # Bold-text HOOK intro so the in-feed cover stops the scroll (YT/IG/FB).
    # Audio is shifted to start after the hook, so captions stay synced.
    # FULLY FAIL-OPEN: any error falls back to the plain (hook-less) render.
    final = None
    if hook_text:
        try:
            from hook_helper import build_hook_frame, prepend_hook
            hook_png = build_hook_frame(
                hook_text, (SW, SH), FONT_BOLD_PATHS, accent=hook_accent,
                out_path=str(OUT / f"{Path(out_path).stem}_hook.png"))
            final = prepend_hook(video, audio_clip, hook_png, (SW, SH))
            print(f"  ✅ Hook intro prepended ({Path(out_path).stem})")
        except Exception as e:
            print(f"  ⚠️ Hook intro skipped (fail-open): {e}")
            final = None
    if final is None:
        final = video.set_audio(audio_clip)

    final.write_videofile(out_path, fps=FPS, codec="libx264",
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


def upload_short(video_path: str, title: str, description: str, tags: list, thumb_path: str = "",
                 caption_srt: str = "", caption_lang: str = "hi") -> str:
    youtube = get_youtube_service()
    if not youtube: return ""
    body = {
        # defaultAudioLanguage lets YouTube auto-generate + auto-translate captions
        # per viewer country (works even without our own .srt).
        "snippet": {"title": title[:100], "description": description, "tags": tags,
                    "categoryId": "22", "defaultLanguage": caption_lang,
                    "defaultAudioLanguage": caption_lang},
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
        # Custom thumbnail (fail-open). Drives CTR on Search / channel grid /
        # Browse / shared links even though the in-feed Shorts player uses a frame.
        if thumb_path and os.path.exists(thumb_path):
            try:
                youtube.thumbnails().set(
                    videoId=vid_id,
                    media_body=MediaFileUpload(thumb_path, mimetype="image/jpeg", resumable=False)
                ).execute()
                print(f"  🖼️  Custom thumbnail set for {vid_id}")
            except Exception as e:
                print(f"  ⚠️ Thumbnail set skipped (fail-open): {e}")
        # Subtitle track for auto-translate (fail-open; needs force-ssl scope).
        if caption_srt and os.path.exists(caption_srt):
            try:
                from subtitle_helper import upload_caption
                upload_caption(youtube, vid_id, caption_srt, caption_lang)
            except Exception as e:
                print(f"  ⚠️ Caption upload skipped (fail-open): {e}")
        # Auto-post the channel's own top comment with the Telegram funnel.
        try:
            import money_funnel as _mf
            _mf.post_first_comment(youtube, vid_id, caption_lang or "hi")
        except Exception:
            pass
        return vid_id
    except Exception as e:
        print(f"  ❌ YouTube upload failed: {e}")
        return ""


# ══════════════════════════════════════════════════════════════════════════════
# FACEBOOK PAGE TOKEN — v3.2 matches upload_facebook.py v2.5
# ══════════════════════════════════════════════════════════════════════════════

def get_fb_page_token() -> str:
    user_token = os.environ.get("META_ACCESS_TOKEN", "")
    page_id    = os.environ.get("FACEBOOK_PAGE_ID", "")
    if not user_token or not page_id:
        return user_token

    try:
        resp = requests.get(
            f"{GRAPH_BASE}/{page_id}",
            params={"fields": "access_token", "access_token": user_token},
            timeout=15
        )
        data = resp.json()
        token = data.get("access_token", "")
        if token:
            print(f"  ✅ Page token retrieved for page {page_id}")
            return token
        err = data.get("error", {})
        if err:
            print(f"  ⚠️ Direct page token: {err.get('code')} {err.get('message','')}")
    except Exception as e:
        print(f"  ⚠️ Direct page token fetch failed: {e}")

    try:
        resp = requests.get(
            f"{GRAPH_BASE}/me/accounts",
            params={"access_token": user_token, "limit": 200},
            timeout=15
        )
        data = resp.json().get("data", [])
        for page in data:
            if str(page.get("id", "")) == str(page_id):
                token = page.get("access_token", "")
                if token:
                    print(f"  ✅ Page token retrieved via /me/accounts for page {page_id}")
                    return token
        found = [p.get("id") for p in data]
        print(f"  ⚠️ Page {page_id} not in /me/accounts — found: {found[:10] or 'none'}")
    except Exception as e:
        print(f"  ⚠️ /me/accounts lookup failed: {e}")

    print(f"  ⚠️ Falling back to user token")
    return user_token


def _fb_videos_fallback(page_id: str, page_token: str, video_path: str, caption: str) -> bool:
    print("  🔄 Trying /videos fallback...")
    try:
        with open(video_path, "rb") as f:
            video_data = f.read()
        resp = requests.post(
            f"{GRAPH_BASE}/{page_id}/videos",
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
    page_id = os.environ.get("FACEBOOK_PAGE_ID", "")
    if not page_id:
        print("⚠️ FACEBOOK_PAGE_ID not set — skipping Facebook share")
        return False

    page_token = get_fb_page_token()
    video_size = os.path.getsize(video_path)

    for attempt in range(1, FB_RETRY+1):
        try:
            init = requests.post(
                f"{GRAPH_BASE}/{page_id}/video_reels",
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
                    break
                time.sleep(FB_RETRY_WAIT)
                continue

            with open(video_path, "rb") as f:
                video_data = f.read()
            requests.post(
                upload_url,
                headers={"Authorization": f"OAuth {page_token}", "offset": "0", "file_size": str(video_size)},
                data=video_data, timeout=300
            )

            finish = requests.post(
                f"{GRAPH_BASE}/{page_id}/video_reels",
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

    return _fb_videos_fallback(page_id, page_token, video_path, caption)


# ══════════════════════════════════════════════════════════════════════════════
# v3.3 NEW: INSTAGRAM REELS UPLOAD
# ══════════════════════════════════════════════════════════════════════════════

def _save_ig_caption_fallback(caption: str, short_label: str = ""):
    fallback_path = OUT / "instagram_short_caption.txt"
    try:
        with open(fallback_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Short: {short_label} | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(caption + "\n")
        print(f"  📝 IG caption saved to {fallback_path.name} for manual posting")
    except Exception as e:
        print(f"  ⚠️ Could not save IG caption: {e}")


def upload_to_instagram(video_path: str, caption: str, short_label: str = "") -> bool:
    """
    Upload short to Instagram Reels.
    Uses same resumable upload flow as upload_facebook.py v2.5.
    Step 1: Create container with upload_type=resumable
    Step 2: Upload video bytes to upload_url
    Step 3: Poll status until FINISHED
    Step 4: Publish
    """
    ig_account_id = INSTAGRAM_BUSINESS_ACCOUNT_ID
    if not ig_account_id:
        print(f"  ⚠️ INSTAGRAM_BUSINESS_ACCOUNT_ID not set — skipping Instagram {short_label}")
        return False

    token = get_fb_page_token()
    print(f"\n📸 Uploading Instagram Reel {short_label}: {Path(video_path).name}")

    # Step 1: Create container
    try:
        ig_caption = caption + "\n\n#Reels #InstagramReels #StockMarketIndia #ai360trading"
        init_resp  = requests.post(
            f"{GRAPH_BASE}/{ig_account_id}/media",
            data={
                "media_type":    "REELS",
                "upload_type":   "resumable",
                "caption":       ig_caption,
                "share_to_feed": "true",
                "access_token":  token,
            },
            timeout=30
        ).json()

        container_id = init_resp.get("id")
        upload_url   = init_resp.get("uri")

        if not container_id:
            error = init_resp.get("error", {})
            print(f"  ❌ IG container failed: {error.get('code')} {error.get('message','')}")
            _save_ig_caption_fallback(caption, short_label)
            return False

        print(f"  ✅ IG container created: {container_id}")

        if not upload_url:
            print(f"  ❌ No upload_url from Instagram")
            _save_ig_caption_fallback(caption, short_label)
            return False

    except Exception as e:
        print(f"  ❌ IG Step 1 error: {e}")
        _save_ig_caption_fallback(caption, short_label)
        return False

    # Step 2: Upload video bytes
    try:
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        file_size = len(video_bytes)
        print(f"  📤 Uploading to Instagram ({file_size/1_000_000:.1f} MB)...")

        up_resp = requests.post(
            upload_url,
            headers={
                "Authorization": f"OAuth {token}",
                "Content-Type":  "video/mp4",
                "offset":        "0",
                "file_size":     str(file_size),
            },
            data=video_bytes,
            timeout=300
        )

        if up_resp.status_code not in (200, 201):
            print(f"  ❌ IG video upload failed: {up_resp.status_code} — {up_resp.text[:200]}")
            _save_ig_caption_fallback(caption, short_label)
            return False

        print(f"  ✅ IG video upload complete")

    except Exception as e:
        print(f"  ❌ IG Step 2 error: {e}")
        _save_ig_caption_fallback(caption, short_label)
        return False

    # Step 3: Poll status
    print(f"  ⏳ Waiting for Instagram processing...")
    for poll in range(IG_POLL_MAX):
        time.sleep(IG_POLL_WAIT)
        try:
            status_resp = requests.get(
                f"{GRAPH_BASE}/{container_id}",
                params={"fields": "status_code,status", "access_token": token},
                timeout=15
            ).json()
            status = status_resp.get("status_code", "")
            print(f"  ⏳ IG processing ({poll+1}/{IG_POLL_MAX}): {status}")
            if status == "FINISHED":
                break
            elif status == "ERROR":
                print(f"  ❌ IG processing error: {status_resp.get('status','')}")
                _save_ig_caption_fallback(caption, short_label)
                return False
        except Exception as e:
            print(f"  ⚠️ IG poll error: {e}")
    else:
        print(f"  ❌ IG processing timeout")
        _save_ig_caption_fallback(caption, short_label)
        return False

    # Step 4: Publish
    try:
        pub_resp = requests.post(
            f"{GRAPH_BASE}/{ig_account_id}/media_publish",
            data={"creation_id": container_id, "access_token": token},
            timeout=30
        ).json()

        ig_post_id = pub_resp.get("id")
        if ig_post_id:
            print(f"  ✅ Instagram Reel published {short_label} — ID: {ig_post_id}")
            return True
        else:
            error = pub_resp.get("error", {})
            print(f"  ❌ IG publish failed: {error.get('code')} {error.get('message','')}")
            _save_ig_caption_fallback(caption, short_label)
            return False

    except Exception as e:
        print(f"  ❌ IG Step 4 error: {e}")
        _save_ig_caption_fallback(caption, short_label)
        return False


# ══════════════════════════════════════════════════════════════════════════════
# BUILD TITLES + DESCRIPTIONS + CAPTIONS
# ══════════════════════════════════════════════════════════════════════════════

def _uniq_title(script_data: dict, fallback: str) -> str:
    """v3.12 GROWTH FIX: the upload title was a HARDCODED template — literally
    identical every day ("Global Market Pulse Today — Nifty, Gold & Bitcoin
    #Shorts" x30). Viewers read it as a repeat and YouTube reads it as
    duplicate content. Prefer the AI's title (it carries today's real numbers
    → unique daily); otherwise stamp the date into the template so two days
    NEVER share an identical title. Fail-open: any problem → dated fallback."""
    try:
        t = (script_data.get("title") or "").strip()
        low = t.lower()
        generic = ("market pulse" in low or "short title" in low
                   or "market update" in low or len(t) < 12)
        if not generic:
            return (t if "#shorts" in low else f"{t} #Shorts")[:100]
    except Exception:
        pass
    try:
        d = datetime.now(IST).strftime("%d %b")
    except Exception:
        d = ""
    if d and fallback.endswith(" #Shorts"):
        return fallback[:-len(" #Shorts")] + f" · {d} #Shorts"
    return fallback

def build_title_short2(script_data: dict) -> str:
    # Front-load the keyword/curiosity (YouTube shows ~first 40 chars); brand/date
    # moved to the description so the title earns the click.
    if CONTENT_MODE == "holiday":
        label = HOLIDAY_NAME if HOLIDAY_NAME else "Market Holiday"
        return _uniq_title(script_data, f"📚 {label} Special — Stock Market Lesson #Shorts")
    elif CONTENT_MODE == "weekend":
        return _uniq_title(script_data, f"📚 Weekend Trading Lesson — Stock Market for Beginners #Shorts")
    stock = script_data.get("stock", "Nifty")
    sent  = script_data.get("sentiment", "bullish").capitalize()
    # stock+sentiment already varies daily — keep it (SEO keyword pattern intact)
    return f"{stock} {sent} Setup Today 📈 Nifty Stock to Watch #Shorts"

def build_title_short3(script_data: dict) -> str:
    if CONTENT_MODE in ("holiday", "weekend"):
        return _uniq_title(script_data, f"🌍 Weekend Market Wisdom — Global Investing Tips #Shorts")
    return _uniq_title(script_data, f"🌍 Global Market Pulse Today — Nifty, Gold & Bitcoin #Shorts")

def build_desc(script_data: dict, short_num: int, part1_url: str) -> str:
    tags    = seo.get_video_tags(mode=CONTENT_MODE, is_short=True)
    yt_tags = seo.get_youtube_safe_tags(tags)
    htags   = " ".join(f"#{t}" for t in yt_tags[:12])
    insight = script_data.get("insight", "Daily market intelligence for Indian traders.")
    cta     = f"\n▶️ Full Analysis: {part1_url}" if part1_url else ""
    lang    = "hi" if short_num == 2 else "en"
    funnel  = _funnel(lang=lang)
    funnel  = f"{funnel}\n\n" if funnel else ""
    return (
        f"💡 {insight}\n\n"
        f"👍 Like • 🔔 Subscribe • 📤 Share this with a trader friend{cta}\n\n"
        f"{funnel}"
        f"⚠️ Educational only. Not SEBI registered.\n"
        f"{ai_disclosure(lang)}\n\n"
        f"{htags}"
    )

def build_fb_caption(script_data: dict, short_num: int) -> str:
    insight = script_data.get("insight", "Daily market intelligence.")
    lang    = "hi" if short_num == 2 else "en"
    funnel  = _funnel(lang=lang, compact=True)
    funnel  = f"{funnel}\n" if funnel else "🌐 ai360trading.in | 📱 t.me/ai360trading\n"
    if CONTENT_MODE in ("holiday", "weekend"):
        return (
            f"📚 Weekend Learning!\n\n"
            f"💡 {insight}\n\n"
            f"{funnel}"
            f"{ai_disclosure(lang)}\n"
            f"#ai360trading #StockMarket #Trading #WeekendLearning"
        )
    stock = script_data.get("stock", "Market")
    sent  = script_data.get("sentiment", "").capitalize()
    return (
        f"📊 {stock} {sent} Signal!\n\n"
        f"💡 {insight}\n\n"
        f"{funnel}"
        f"⚠️ Educational only.\n"
        f"{ai_disclosure(lang)}\n"
        f"#ai360trading #StockMarket #{stock.replace(' ','')}"
    )

def build_ig_caption_short2(script_data: dict) -> str:
    insight = script_data.get("insight", "Daily market intelligence.")
    stock   = script_data.get("stock", "Market")
    sent    = script_data.get("sentiment", "").capitalize()
    funnel  = _funnel(lang="hi", compact=True)
    funnel  = f"{funnel}\n" if funnel else "🌐 ai360trading.in | 📱 t.me/ai360trading\n"
    if CONTENT_MODE in ("holiday", "weekend"):
        return (
            f"📚 Weekend Learning!\n\n"
            f"💡 {insight}\n\n"
            f"{funnel}"
            f"{ai_disclosure('hi')}\n"
            f"#ai360trading #StockMarket #Trading #Investing"
        )
    return (
        f"📊 {stock} {sent} Setup!\n\n"
        f"💡 {insight}\n\n"
        f"{funnel}"
        f"⚠️ Educational only.\n"
        f"{ai_disclosure('hi')}\n"
        f"#ai360trading #Nifty50 #StockMarket #TradingIndia"
    )

def build_ig_caption_short3(script_data: dict) -> str:
    insight = script_data.get("insight", "Global markets shaping India's trading day.")
    funnel  = _funnel(lang="en", compact=True)
    funnel  = f"{funnel}\n" if funnel else "🌐 ai360trading.in | 📱 t.me/ai360trading\n"
    if CONTENT_MODE in ("holiday", "weekend"):
        return (
            f"🌍 Global Market Wisdom!\n\n"
            f"💡 {insight}\n\n"
            f"{funnel}"
            f"{ai_disclosure('en')}\n"
            f"#GlobalMarkets #Bitcoin #Gold #SP500 #ai360trading"
        )
    return (
        f"🌍 Global Market Pulse!\n\n"
        f"💡 {insight}\n\n"
        f"{funnel}"
        f"⚠️ Educational only.\n"
        f"{ai_disclosure('en')}\n"
        f"#GlobalMarkets #Bitcoin #Gold #Nifty #ai360trading"
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    today     = now_ist.strftime("%Y%m%d")
    market    = fetch_market_data()
    part1_url = get_part1_url()
    tags      = seo.get_video_tags(mode=CONTENT_MODE, is_short=True)
    yt_tags   = seo.get_youtube_safe_tags(tags)

    short2_id = ""
    short3_id = ""

    # ── SHORT 2 (Madhur — Hindi Trade Setup) ──────────────────────────────────
    print(f"\n─── SHORT 2 (Madhur) ────────────────────────")
    s2_data  = _sanitize_script(generate_short2_script(market, part1_url), "hi")
    s2_frame = make_short2_frame(s2_data, market)
    s2_audio = str(OUT / f"short2_audio_{today}.mp3")
    s2_video = str(OUT / f"short2_{today}.mp4")
    s2_spoken = _with_cta(s2_data.get("script", ""), "hi")
    gen_tts(s2_spoken, VOICE_SHORT2, s2_audio)
    s2_head, s2_sub, s2_acc, s2_badge = short2_thumb_text(s2_data)
    # In-feed cover = curiosity HOOK from the AI (falls back to the label if none).
    s2_hook = (s2_data.get("hook") or "").strip() or s2_head
    s2_srt = str(OUT / f"short2_{today}.srt")
    render_short(s2_frame, s2_audio, s2_video, spoken_text=s2_spoken,
                 hook_text=s2_hook, hook_accent=s2_acc, srt_path=s2_srt, srt_lang="hi")

    # Bold-text thumbnail (fail-open — never blocks upload)
    s2_thumb = ""
    try:
        s2_thumb = str(build_short_thumbnail(s2_head, s2_sub, s2_acc, s2_badge, f"short2_thumb_{today}.jpg"))
    except Exception as e:
        print(f"  ⚠️ Short 2 thumbnail skipped (fail-open): {e}")

    s2_title  = build_title_short2(s2_data)
    s2_desc   = build_desc(s2_data, 2, part1_url)
    short2_id = upload_short(s2_video, s2_title, s2_desc, yt_tags, s2_thumb,
                             caption_srt=s2_srt, caption_lang="hi")
    if short2_id:
        print(f"  ✅ YouTube: https://youtube.com/shorts/{short2_id}")

    print(f"  📘 Short 2 → Facebook...")
    share_to_facebook(s2_video, build_fb_caption(s2_data, 2))

    print(f"  📸 Short 2 → Instagram...")
    upload_to_instagram(s2_video, build_ig_caption_short2(s2_data), short_label="Short2")

    # ── SHORT 3 (Neerja — Global Market Pulse) ────────────────────────────────
    print(f"\n─── SHORT 3 (Neerja) ────────────────────────")
    s3_data  = _sanitize_script(generate_short3_script(market), "en")
    s3_frame = make_short3_frame(s3_data, market)
    s3_audio = str(OUT / f"short3_audio_{today}.mp3")
    s3_video = str(OUT / f"short3_{today}.mp4")
    s3_spoken = _with_cta(s3_data.get("script", ""), "en")
    gen_tts(s3_spoken, VOICE_SHORT3, s3_audio)
    s3_head, s3_sub, s3_acc, s3_badge = short3_thumb_text(s3_data)
    # In-feed cover = curiosity HOOK from the AI (falls back to the label if none).
    s3_hook = (s3_data.get("hook") or "").strip() or s3_head
    s3_srt = str(OUT / f"short3_{today}.srt")
    render_short(s3_frame, s3_audio, s3_video, spoken_text=s3_spoken,
                 hook_text=s3_hook, hook_accent=s3_acc, srt_path=s3_srt, srt_lang="en")

    # Bold-text thumbnail (fail-open — never blocks upload)
    s3_thumb = ""
    try:
        s3_thumb = str(build_short_thumbnail(s3_head, s3_sub, s3_acc, s3_badge, f"short3_thumb_{today}.jpg"))
    except Exception as e:
        print(f"  ⚠️ Short 3 thumbnail skipped (fail-open): {e}")

    s3_title  = build_title_short3(s3_data)
    s3_desc   = build_desc(s3_data, 3, part1_url)
    short3_id = upload_short(s3_video, s3_title, s3_desc, yt_tags, s3_thumb,
                             caption_srt=s3_srt, caption_lang="en")
    if short3_id:
        print(f"  ✅ YouTube: https://youtube.com/shorts/{short3_id}")

    print(f"  📘 Short 3 → Facebook...")
    share_to_facebook(s3_video, build_fb_caption(s3_data, 3))

    print(f"  📸 Short 3 → Instagram...")
    upload_to_instagram(s3_video, build_ig_caption_short3(s3_data), short_label="Short3")

    print(f"\n{'='*50}")
    print(f"✅ SHORTS DONE — {today} [{CONTENT_MODE.upper()}]")
    print(f"   Short 2 (Madhur): {'https://youtube.com/shorts/'+short2_id if short2_id else 'FAILED'}")
    print(f"   Short 3 (Neerja): {'https://youtube.com/shorts/'+short3_id if short3_id else 'FAILED'}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
