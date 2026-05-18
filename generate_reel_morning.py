"""
generate_reel_morning.py — Morning Reel Generator (7:00 AM IST)
===============================================================
v2.3 CHANGES (May 2026) — SEO + THUMBNAIL FIX:

FIX 1 — SEO Title (was generic, now searchable)
  Old: "Morning Market Brief NEUTRAL — AI360Trading"
  New: "Nifty 23,645 📉 BEARISH | 19 May Morning Brief | AI360Trading"
  Why: Traders search "Nifty today", "stock market 19 May" → now matched

FIX 2 — Description (was 200 chars, now 500+ with hashtags IN BODY)
  Old: AI returned 200 char description → bad SEO, no hashtags visible
  New: Full description with story, links, disclaimer + hashtags in text
  Why: YouTube shows first 125 chars in search → must hook viewer
       First 3 hashtags in description appear ON video page

FIX 3 — Thumbnail (Nifty level added)
  Old: "MORNING BRIEF" + sentiment badge + ZENO
  New: "MORNING BRIEF" + "NIFTY 23,645" + sentiment badge + ZENO
  Why: Trader sees specific number → stops scrolling → reads → clicks
       Competitor format: "NIFTY 23250 — 18 MAY 2026 | VOLATILE"

v2.2 features fully preserved:
  - Live market intelligence (Nifty, Oil, Gold, BTC, S&P500 + news)
  - Sentiment-aware script (BULLISH/BEARISH/NEUTRAL)
  - TTS voice only (no music)
  - Proper ZENO thumbnail
"""

import os
import json
import asyncio
import logging
import re
from datetime import datetime
from pathlib import Path

import pytz
from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mp
import numpy as np

from ai_client import ai
from human_touch import ht, seo, MORNING_REEL_TOPICS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

IMAGE_DIR = Path("public/image")

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market")
LANG = os.environ.get("LANG_MODE", "hi")

TODAY    = datetime.now(IST)
DATE_STR = TODAY.strftime("%Y%m%d")
WEEKDAY  = TODAY.weekday()

VIDEO_WIDTH  = 1080
VIDEO_HEIGHT = 1920
FPS      = 30
DURATION = 55

VOICE_HI = "hi-IN-SwaraNeural"
VOICE_EN = "en-US-JennyNeural"

PALETTES = [
    {"bg": (15, 20, 40),  "accent": (0, 200, 255),   "text": (255, 255, 255)},
    {"bg": (20, 40, 15),  "accent": (50, 220, 100),   "text": (255, 255, 255)},
    {"bg": (40, 15, 15),  "accent": (255, 80, 80),    "text": (255, 255, 255)},
    {"bg": (30, 20, 50),  "accent": (180, 100, 255),  "text": (255, 255, 255)},
    {"bg": (40, 30, 10),  "accent": (255, 180, 0),    "text": (255, 255, 255)},
    {"bg": (10, 35, 45),  "accent": (0, 180, 200),    "text": (255, 255, 255)},
    {"bg": (35, 15, 35),  "accent": (255, 100, 200),  "text": (255, 255, 255)},
]

TODAY_PALETTE = PALETTES[WEEKDAY % len(PALETTES)]

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
    if isinstance(paths, str): paths = [paths]
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def lerp(c1, c2, t):
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))


# ══════════════════════════════════════════════════════════════════════════════
# MARKET INTELLIGENCE ENGINE (v2.2 — unchanged)
# ══════════════════════════════════════════════════════════════════════════════

def fetch_prices() -> dict:
    prices = {}
    symbols = {
        "nifty":  "^NSEI",
        "crude":  "CL=F",
        "dxy":    "DX-Y.NYB",
        "gold":   "GC=F",
        "btc":    "BTC-USD",
        "sp500":  "^GSPC",
        "usdinr": "INR=X",
    }
    try:
        import yfinance as yf
        for name, sym in symbols.items():
            try:
                ticker = yf.Ticker(sym)
                info   = ticker.fast_info
                cmp    = info.get("last_price", 0)
                prev   = info.get("previous_close", 0)
                if cmp > 0 and prev > 0:
                    pct = ((cmp - prev) / prev) * 100
                    prices[name] = {"cmp": round(cmp, 2), "pct": round(pct, 2), "up": pct >= 0}
                    logger.info(f"[PRICE] {name}: {cmp:.2f} ({pct:+.2f}%)")
                else:
                    prices[name] = {"cmp": 0, "pct": 0, "up": True}
            except Exception as e:
                logger.warning(f"[PRICE] {name} failed: {e}")
                prices[name] = {"cmp": 0, "pct": 0, "up": True}
    except ImportError:
        logger.warning("[PRICE] yfinance not installed")
    return prices


def fetch_news_headlines() -> list:
    import requests
    import xml.etree.ElementTree as ET

    rss_feeds = [
        "https://news.google.com/rss/search?q=India+stock+market+Nifty&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=global+economy+markets+today&hl=en&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=crude+oil+price+dollar+index&hl=en&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=war+conflict+geopolitical+risk+markets&hl=en&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=RBI+Federal+Reserve+interest+rate&hl=en&gl=IN&ceid=IN:en",
    ]
    headlines = []
    for url in rss_feeds:
        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200: continue
            root  = ET.fromstring(resp.content)
            items = root.findall(".//item")
            for item in items[:3]:
                title = item.findtext("title", "").strip()
                if title and len(title) > 10:
                    title = re.sub(r'\s*-\s*[A-Z][a-zA-Z\s]+$', '', title).strip()
                    headlines.append(title)
        except Exception as e:
            logger.warning(f"[NEWS] Feed failed: {e}")
    logger.info(f"[NEWS] Fetched {len(headlines)} headlines")
    return headlines[:12]


def calculate_sentiment(prices: dict, headlines: list) -> dict:
    score   = 0
    factors = []
    warning = ""

    nifty = prices.get("nifty", {})
    crude = prices.get("crude", {})
    dxy   = prices.get("dxy",   {})
    gold  = prices.get("gold",  {})
    btc   = prices.get("btc",   {})
    sp500 = prices.get("sp500", {})

    if nifty.get("cmp", 0) > 0:
        nifty_pct = nifty.get("pct", 0)
        if nifty_pct > 0.5:
            score += 2; factors.append(f"Nifty {nifty_pct:+.1f}% — bullish open expected")
        elif nifty_pct < -0.5:
            score -= 2; factors.append(f"Nifty {nifty_pct:+.1f}% — bearish pressure")

    if crude.get("cmp", 0) > 0:
        crude_pct = crude.get("pct", 0); crude_cmp = crude.get("cmp", 0)
        if crude_pct > 2:
            score -= 1; warning = f"Crude Oil up {crude_pct:+.1f}% at ${crude_cmp:.0f}"
            factors.append(f"Oil {crude_pct:+.1f}% — import cost pressure")
        elif crude_pct < -2:
            score += 1; factors.append(f"Oil {crude_pct:+.1f}% — positive for India")

    if dxy.get("cmp", 0) > 0:
        dxy_pct = dxy.get("pct", 0)
        if dxy_pct > 0.5:
            score -= 1; factors.append(f"Dollar Index +{dxy_pct:.1f}% — FII outflow risk")
        elif dxy_pct < -0.5:
            score += 1; factors.append(f"Dollar Index {dxy_pct:.1f}% — FII inflow positive")

    if gold.get("cmp", 0) > 0:
        gold_pct = gold.get("pct", 0); gold_cmp = gold.get("cmp", 0)
        if gold_pct > 1.5:
            score -= 1; warning = warning or f"Gold surging {gold_pct:+.1f}%"
            factors.append(f"Gold {gold_pct:+.1f}% — safe haven demand")
        elif gold_pct < -0.5:
            score += 1; factors.append(f"Gold {gold_pct:.1f}% — risk-on sentiment")

    if btc.get("cmp", 0) > 0:
        btc_pct = btc.get("pct", 0)
        if btc_pct > 3:   score += 1; factors.append(f"Bitcoin {btc_pct:+.1f}% — risk-on")
        elif btc_pct < -3: score -= 1; factors.append(f"Bitcoin {btc_pct:.1f}% — risk-off")

    if sp500.get("cmp", 0) > 0:
        sp_pct = sp500.get("pct", 0)
        if sp_pct > 0.3:   score += 1; factors.append(f"S&P500 {sp_pct:+.1f}% — US positive")
        elif sp_pct < -0.3: score -= 1; factors.append(f"S&P500 {sp_pct:.1f}% — US negative")

    bullish_kw = ["rally","surge","gain","recover","positive","growth","rate cut","stimulus","boost","jump","soar","strong","bullish","upgrade"]
    bearish_kw = ["crash","fall","drop","recession","war","conflict","inflation","rate hike","hike","crisis","risk","fear","sanction","ban","attack","tension","slump","plunge","bearish","sell-off","downgrade"]

    news_score = 0; news_warnings = []
    for headline in headlines:
        hl = headline.lower()
        for kw in bullish_kw:
            if kw in hl: news_score += 1; break
        for kw in bearish_kw:
            if kw in hl:
                news_score -= 1
                if any(w in hl for w in ["war","conflict","attack","crisis"]):
                    news_warnings.append(headline[:60])
                break
    score += max(-3, min(3, news_score))
    if news_warnings and not warning:
        warning = f"Major news: {news_warnings[0]}"

    sentiment = "BULLISH" if score >= 3 else "BEARISH" if score <= -3 else "NEUTRAL"
    return {
        "sentiment":   sentiment,
        "score":       score,
        "key_factors": factors[:3] if factors else ["Market data being analysed"],
        "warning":     warning,
        "nifty_level": int(round(nifty.get("cmp", 0))) if nifty.get("cmp", 0) > 0 else 0,
        "nifty_pct":   nifty.get("pct", 0),
        "crude_level": crude.get("cmp", 0),
        "gold_level":  gold.get("cmp", 0),
        "btc_level":   int(btc.get("cmp", 0)) if btc.get("cmp", 0) > 0 else 0,
    }


def get_market_intelligence() -> dict:
    logger.info("[INTEL] Fetching market intelligence...")
    prices    = fetch_prices()
    headlines = fetch_news_headlines()
    sentiment = calculate_sentiment(prices, headlines)
    return {**sentiment, "headlines_summary": headlines[:5], "prices": prices}


def build_intelligence_prompt(intel: dict) -> str:
    sentiment   = intel.get("sentiment", "NEUTRAL")
    score       = intel.get("score", 0)
    factors     = intel.get("key_factors", [])
    warning     = intel.get("warning", "")
    nifty_level = intel.get("nifty_level", 0)
    nifty_pct   = intel.get("nifty_pct", 0)
    crude       = intel.get("crude_level", 0)
    gold        = intel.get("gold_level", 0)
    btc         = intel.get("btc_level", 0)
    headlines   = intel.get("headlines_summary", [])

    nifty_str = f"Nifty: {nifty_level} ({nifty_pct:+.2f}%)" if nifty_level > 0 else ""
    crude_str = f"Crude Oil: ${crude:.1f}"                   if crude       > 0 else ""
    gold_str  = f"Gold: ${gold:.0f}"                         if gold        > 0 else ""
    btc_str   = f"Bitcoin: ${btc:,}"                         if btc         > 0 else ""
    prices_line = " | ".join(filter(None, [nifty_str, crude_str, gold_str, btc_str]))
    factors_text  = "\n".join(f" • {f}" for f in factors) if factors else " • Market data analysed"
    headlines_text= "\n".join(f" • {h}" for h in headlines[:4]) if headlines else " • No major news"
    emoji_map     = {"BULLISH": "📈🟢", "BEARISH": "📉🔴", "NEUTRAL": "⚖️🟡"}
    emoji         = emoji_map.get(sentiment, "⚖️")
    warning_line  = f"\n⚠️ MAJOR RISK: {warning}" if warning else ""

    return f"""
TODAY'S MARKET INTELLIGENCE:

{emoji} SENTIMENT: {sentiment} (score: {score:+d})

📊 LIVE PRICES:
{prices_line}

🔑 KEY FACTORS:
{factors_text}

📰 NEWS:
{headlines_text}
{warning_line}

SCRIPT RULES:
1. Open with sentiment: "{sentiment} day ahead"
2. Mention 2-3 key factors naturally
3. BEARISH: warn caution, use SL, avoid FOMO
4. BULLISH: optimistic but risk management
5. NEUTRAL: wait for confirmation
6. NEVER recommend specific stocks
7. End with Telegram CTA
8. Use Nifty {nifty_level if nifty_level > 0 else "current level"} — NOT 18500
"""


# ══════════════════════════════════════════════════════════════════════════════
# SCRIPT GENERATION (v2.2 — unchanged)
# ══════════════════════════════════════════════════════════════════════════════

def generate_morning_script(intel: dict) -> dict:
    topic_data       = MORNING_REEL_TOPICS[WEEKDAY]
    topic            = topic_data["topic"]
    angle            = topic_data["angle"]
    target_countries = topic_data["target_country"]
    hook             = topic_data["hook_hi"] if LANG == "hi" else topic_data["hook_en"]
    cta              = ht.get_cta(LANG)
    intel_prompt     = build_intelligence_prompt(intel)
    sentiment        = intel.get("sentiment", "NEUTRAL")

    prompt = f"""
Create a 55-second morning market briefing reel for AI360Trading.

Topic: {topic} — {angle}
Countries: {', '.join(target_countries)}
Language: {"Hinglish (natural Hindi + English mix)" if LANG == "hi" else "English"}
Hook line 1: {hook}

{intel_prompt}

Requirements:
- 8-10 punchy lines, 5-7 words each
- Line 1 = hook above
- Lines 2-7 = market intelligence points naturally
- Line 8 = sentiment advice
- Last line = CTA: {cta}
- Tone: energetic morning brief — trusted analyst friend

Return JSON:
{{
  "title": "SEO title max 70 chars with sentiment",
  "lines": ["line1", "line2", ...],
  "topic_display": "2-4 word topic English only for thumbnail",
  "sentiment_display": "{sentiment}",
  "description": "200 char market context description",
  "topic": "{topic}",
  "target_countries": {json.dumps(target_countries)}
}}"""

    logger.info(f"[SCRIPT] Morning reel — {sentiment} | {topic}")
    result = ai.generate_json(prompt=prompt, content_mode=CONTENT_MODE, lang=LANG)

    if not result or "lines" not in result:
        logger.warning("Fallback script used")
        result = _fallback_script(topic, hook, cta, target_countries, sentiment)

    result["lines"]     = ht.humanize_script_lines(result.get("lines", []), LANG)
    result["sentiment"] = sentiment
    return result


def _fallback_script(topic, hook, cta, countries, sentiment="NEUTRAL"):
    sent_line = {
        "BULLISH": "Aaj ka market bullish lag raha hai!" if LANG=="hi" else "Markets looking bullish today!",
        "BEARISH": "Aaj caution zaroori hai — SL zaroor lagao!" if LANG=="hi" else "Caution needed — always use your stop loss!",
        "NEUTRAL": "Confirmation ka wait karo!" if LANG=="hi" else "Wait for confirmation before entering!",
    }.get(sentiment, "")
    return {
        "title":           f"Morning Market Brief {sentiment} — AI360Trading",
        "lines":           [hook, "Market data analysis complete.", "Oil, dollar, global cues — all checked.", sent_line, "Risk management first.", "Discipline + patience = returns.", cta],
        "topic_display":   topic[:20],
        "sentiment_display": sentiment,
        "description":     f"Morning market intelligence: {topic}. Sentiment: {sentiment}.",
        "topic":           topic,
        "target_countries": countries,
        "sentiment":       sentiment,
    }


# ══════════════════════════════════════════════════════════════════════════════
# TTS (unchanged)
# ══════════════════════════════════════════════════════════════════════════════

async def generate_tts(lines: list, output_path: str) -> bool:
    try:
        import edge_tts
    except ImportError:
        logger.error("edge-tts not installed"); return False
    voice    = VOICE_HI if LANG == "hi" else VOICE_EN
    speed    = ht.get_tts_speed()
    rate_str = f"+{int((speed-1)*100)}%" if speed >= 1 else f"{int((speed-1)*100)}%"
    text     = ". ".join(lines)
    await edge_tts.Communicate(text, voice, rate=rate_str).save(output_path)
    ok = os.path.exists(output_path) and os.path.getsize(output_path) > 0
    if ok: logger.info(f"TTS saved: {output_path}")
    else:  logger.error("TTS failed")
    return ok


# ══════════════════════════════════════════════════════════════════════════════
# v2.3 FIX: THUMBNAIL — Added Nifty level text
# Competitor format: "MORNING BRIEF | NIFTY 23,645 | BEARISH"
# Trader reads specific number → stops scrolling → clicks
# ══════════════════════════════════════════════════════════════════════════════

def build_thumbnail(topic_display: str, sentiment: str, palette: dict, nifty_level: int = 0):
    import textwrap
    W, H   = VIDEO_WIDTH, VIDEO_HEIGHT
    accent = palette["accent"]
    bg     = palette["bg"]

    if sentiment == "BULLISH":  accent = (0, 210, 100)
    elif sentiment == "BEARISH": accent = (220, 55, 55)

    img = Image.new("RGB", (W, H))
    px  = img.load()
    for y in range(H):
        c = lerp(bg, tuple(min(255, x+30) for x in bg), y/H)
        for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0, 0), (W, 14)],   fill=accent)
    draw.rectangle([(0, H-14), (W, H)], fill=accent)

    # ZENO character
    zeno_path = IMAGE_DIR / ("zeno_sad.png" if sentiment=="BEARISH" else "zeno_happy.png")
    if not zeno_path.exists(): zeno_path = IMAGE_DIR / "zeno_thinking.png"
    if zeno_path.exists():
        try:
            zeno   = Image.open(str(zeno_path)).convert("RGBA")
            zeno_h = int(H * 0.65)
            zeno_w = int(zeno.width * (zeno_h / zeno.height))
            zeno   = zeno.resize((zeno_w, zeno_h), Image.LANCZOS)
            img.paste(zeno, (W - zeno_w - 10, H - zeno_h - 60), zeno)
        except Exception as e:
            logger.warning(f"Thumbnail ZENO: {e}")

    draw = ImageDraw.Draw(img, "RGBA")
    f_big   = get_font(FONT_BOLD_PATHS, 110)
    f_nifty = get_font(FONT_BOLD_PATHS, 90)
    f_sent  = get_font(FONT_BOLD_PATHS, 68)
    f_badge = get_font(FONT_BOLD_PATHS, 44)
    f_time  = get_font(FONT_BOLD_PATHS, 48)
    f_wm    = get_font(FONT_REG_PATHS,  34)

    # Morning Brief badge (top)
    draw.rounded_rectangle([(20, 20), (420, 78)], radius=14, fill=(255, 200, 0))
    draw.text((220, 49), "☀️ MORNING BRIEF", font=f_badge, fill=(0,0,0), anchor="mm")

    # Topic text (large yellow)
    safe_topic   = re.sub(r'[\u0900-\u097F]+', '', topic_display).strip().upper() or "MORNING BRIEF"
    topic_lines  = textwrap.wrap(safe_topic, width=10)
    ty = 110
    for line in topic_lines[:2]:
        for dx, dy in [(-3,3),(3,-3),(-3,-3),(3,3)]:
            draw.text((80+dx, ty+dy), line, font=f_big, fill=(0,0,0,200), anchor="la")
        draw.text((80, ty), line, font=f_big, fill=(255, 200, 0), anchor="la")
        ty += 130

    # v2.3 NEW: Nifty level — makes viewer stop to read specific number
    if nifty_level > 0:
        nifty_text = f"NIFTY {nifty_level:,}"
        for dx, dy in [(-3,3),(3,-3)]:
            draw.text((80+dx, ty+dx), nifty_text, font=f_nifty, fill=(0,0,0,180), anchor="la")
        draw.text((80, ty), nifty_text, font=f_nifty, fill=(255, 255, 255), anchor="la")
        ty += 110

    # Sentiment badge
    sent_emoji = {"BULLISH": "📈 BULLISH", "BEARISH": "📉 BEARISH", "NEUTRAL": "⚖️ NEUTRAL"}.get(sentiment, "⚖️ NEUTRAL")
    draw.rounded_rectangle([(80, ty+10), (80+380, ty+82)], radius=14, fill=accent)
    draw.text((270, ty+46), sent_emoji, font=f_sent,
              fill=(0,0,0) if sentiment=="BULLISH" else (255,255,255), anchor="mm")

    # Time + watermark
    draw.text((80, H-65), "7:00 AM IST",      font=f_time, fill=accent, anchor="la")
    draw.text((W//2, H-60), "AI360Trading.in", font=f_wm,  fill=(200,220,255,200), anchor="mm")

    thumb_path = OUTPUT_DIR / f"morning_reel_thumb_{DATE_STR}.png"
    img.save(str(thumb_path), quality=95)
    logger.info(f"Thumbnail saved: {thumb_path.name} (Nifty: {nifty_level})")
    return thumb_path


# ══════════════════════════════════════════════════════════════════════════════
# FRAMES + VIDEO (unchanged from v2.2)
# ══════════════════════════════════════════════════════════════════════════════

def create_frame(line, line_index, total_lines, topic, palette, intel=None, zeno_image=None):
    img  = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color=palette["bg"])
    draw = ImageDraw.Draw(img)
    for y in range(VIDEO_HEIGHT):
        alpha = y / VIDEO_HEIGHT
        r = int(palette["bg"][0] * (1 - alpha * 0.3))
        g = int(palette["bg"][1] * (1 - alpha * 0.3))
        b = int(palette["bg"][2] + alpha * 20)
        draw.line([(0,y),(VIDEO_WIDTH,y)], fill=(min(255,max(0,r)), min(255,max(0,g)), min(255,max(0,b))))

    draw.rectangle([(0,0),(VIDEO_WIDTH,8)], fill=palette["accent"])
    wm_font = get_font(FONT_BOLD_PATHS, 36)
    draw.text((40,30), "AI360Trading", font=wm_font, fill=palette["accent"])

    if intel:
        sentiment    = intel.get("sentiment", "NEUTRAL")
        sent_colour  = (0,210,100) if sentiment=="BULLISH" else (220,55,55) if sentiment=="BEARISH" else (255,180,0)
        sent_emoji   = {"BULLISH":"📈","BEARISH":"📉","NEUTRAL":"⚖️"}.get(sentiment,"⚖️")
        draw.text((VIDEO_WIDTH-40, 40), f"{sent_emoji} {sentiment}",
                  font=get_font(FONT_BOLD_PATHS,32), fill=sent_colour, anchor="ra")

    dot_y = 90; dot_sp = 20
    dot_sx = VIDEO_WIDTH//2 - (total_lines*dot_sp)//2
    for i in range(total_lines):
        col = palette["accent"] if i <= line_index else (80,80,80)
        draw.ellipse([(dot_sx+i*dot_sp-5,dot_y-5),(dot_sx+i*dot_sp+5,dot_y+5)], fill=col)

    if zeno_image:
        try:
            zh = int(VIDEO_HEIGHT*0.42); zw = int(zeno_image.width*(zh/zeno_image.height))
            zr = zeno_image.resize((zw,zh),Image.LANCZOS)
            img.paste(zr,(VIDEO_WIDTH-zw-10,VIDEO_HEIGHT-zh),zr)
        except: pass

    tl_font = get_font(FONT_BOLD_PATHS, 38)
    draw = ImageDraw.Draw(img)
    draw.text((VIDEO_WIDTH//2, VIDEO_HEIGHT//3), topic.upper(), font=tl_font, fill=palette["accent"], anchor="mm")

    main_font = get_font(FONT_BOLD_PATHS, 62)
    words = line.split(); wrapped = []; cur = ""
    for w in words:
        test = (cur+" "+w).strip()
        bbox = draw.textbbox((0,0),test,font=main_font)
        if bbox[2]-bbox[0] > VIDEO_WIDTH-120:
            if cur: wrapped.append(cur)
            cur = w
        else: cur = test
    if cur: wrapped.append(cur)

    text_y  = VIDEO_HEIGHT//2
    tot_h   = len(wrapped)*74
    start_y = text_y - tot_h//2
    for i, wl in enumerate(wrapped[:5]):
        draw.text((VIDEO_WIDTH//2, start_y+i*74), wl, font=main_font, fill=palette["text"], anchor="mm")

    draw.rectangle([(0,VIDEO_HEIGHT-10),(VIDEO_WIDTH,VIDEO_HEIGHT)], fill=palette["accent"])
    draw.text((VIDEO_WIDTH//2, VIDEO_HEIGHT-55), "MORNING BRIEF",
              font=get_font(FONT_BOLD_PATHS,30), fill=palette["accent"], anchor="mm")

    return np.array(img)


def create_morning_video(script, audio_path, output_path, intel=None) -> bool:
    lines     = script.get("lines", [])
    topic     = script.get("topic", "Morning Brief")
    if not lines: logger.error("No lines"); return False

    sentiment = intel.get("sentiment", "NEUTRAL") if intel else "NEUTRAL"
    zeno_file = "zeno_happy.png" if sentiment=="BULLISH" else "zeno_sad.png" if sentiment=="BEARISH" else "zeno_thinking.png"

    zeno_image = None
    for zp in [IMAGE_DIR/zeno_file, IMAGE_DIR/"zeno_thinking.png"]:
        if zp.exists():
            try: zeno_image = Image.open(str(zp)).convert("RGBA"); break
            except: pass

    spl    = DURATION / len(lines)
    fpl    = int(FPS * spl)
    frames = []
    for i, line in enumerate(lines):
        f = create_frame(line, i, len(lines), topic, TODAY_PALETTE, intel, zeno_image)
        for _ in range(fpl): frames.append(f)

    def make_frame(t):
        idx = min(int(t*FPS), len(frames)-1)
        return frames[idx]

    video = mp.VideoClip(make_frame, duration=DURATION)
    if os.path.exists(audio_path):
        try:
            tts = mp.AudioFileClip(audio_path)
            dur = min(DURATION, tts.duration)
            tts = tts.subclip(0, dur)
            video = video.set_audio(tts)
        except Exception as e:
            logger.warning(f"Audio attach: {e}")

    video.write_videofile(output_path, fps=FPS, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    ok = os.path.exists(output_path) and os.path.getsize(output_path) > 0
    if ok: logger.info(f"Video exported: {output_path}")
    else:  logger.error("Video export failed")
    return ok


# ══════════════════════════════════════════════════════════════════════════════
# v2.3 FIX: save_meta — Full SEO title + description + hashtags in body
# ══════════════════════════════════════════════════════════════════════════════

def save_meta(script, video_path, thumb_path, intel) -> str:
    meta_path = OUTPUT_DIR / f"morning_reel_meta_{DATE_STR}.json"

    sentiment   = intel.get("sentiment", "NEUTRAL")
    nifty       = intel.get("nifty_level", 0)
    nifty_pct   = intel.get("nifty_pct", 0)
    factors     = intel.get("key_factors", [])
    date_str    = TODAY.strftime("%d %B %Y")
    date_short  = TODAY.strftime("%d %b")

    # ── v2.3 SEO TITLE: Nifty level + sentiment + date (searchable) ──────────
    sent_emoji = {"BULLISH": "📈", "BEARISH": "📉", "NEUTRAL": "⚖️"}.get(sentiment, "⚖️")
    nifty_str  = f"Nifty {nifty:,}" if nifty > 0 else "Nifty Update"
    title      = f"{nifty_str} {sent_emoji} {sentiment} | {date_short} Morning Brief | AI360Trading"
    title      = title[:100]

    # ── v2.3 SEO DESCRIPTION: 500+ chars + hashtags in body ──────────────────
    # First line = preview in YouTube search (125 chars max shown)
    # Hashtags IN description body = shown on video page (first 3)
    factors_text = " | ".join(factors[:2]) if factors else "Market intelligence ready"
    nifty_line   = f"Nifty {nifty:,} ({nifty_pct:+.2f}%)" if nifty > 0 else "Nifty update"

    description = f"""☀️ {date_str} | {nifty_line} | {sentiment} Market {sent_emoji}

🎯 Today's key factors: {factors_text}

📊 This morning reel covers:
• Live Nifty, Crude Oil, Gold, Bitcoin, S&P500 data
• Today's market sentiment: {sentiment}
• What traders must know before 9:15 AM open
• Risk management tip for today

🌍 For traders in: India 🇮🇳 | USA 🇺🇸 | UAE 🇦🇪 | UK 🇬🇧 | Brazil 🇧🇷 | Canada 🇨🇦

📱 Free live signals: https://t.me/ai360trading
🌐 Website: https://ai360trading.in
📚 Free 52-week investing course on this channel

⚠️ Educational content only. Not SEBI registered. Always do your own research before investing.

#NiftyToday #StockMarket #ai360trading #Nifty50 #ShareMarket
#IndiaStocks #TradingTips #MarketUpdate #MorningBrief #NiftyAnalysis
#InvestingIndia #{sentiment.capitalize()}Market #StockMarketIndia #Sensex
#FinancialEducation #TradingForBeginners #MarketIntelligence"""

    # ── v2.3 SEO TAGS (YouTube metadata, separate from description) ────────────
    tags = [
        "ai360trading", "Nifty50", "StockMarket", "NiftyToday",
        "ShareMarket", "IndiaStocks", "MarketUpdate", "MorningBrief",
        "TradingTips", "StockMarketIndia", "Sensex", "InvestingIndia",
        f"{sentiment.capitalize()}Market", "FinancialEducation",
        "NiftyAnalysis", "TradingForBeginners", "Shorts",
        "StockMarketShorts", "MarketIntelligence", "NiftyLive",
    ]

    meta = {
        "title":           title,
        "description":     description,
        "tags":            tags[:30],
        "topic":           script.get("topic", ""),
        "target_countries": script.get("target_countries", ["India","USA","UK"]),
        "lang":            LANG,
        "content_mode":    CONTENT_MODE,
        "date":            DATE_STR,
        "video_path":      str(video_path),
        "thumb_path":      str(thumb_path),
        "music":           "none — TTS voice only",
        "sentiment":       sentiment,
        "nifty_level":     nifty,
        "key_factors":     factors,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    logger.info(f"Meta saved: {meta_path}")
    logger.info(f"Title: {title}")
    return str(meta_path)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

async def main():
    logger.info(f"Morning Reel v2.3 — {TODAY.strftime('%A %d %b %Y')} | {CONTENT_MODE.upper()} | {LANG.upper()}")

    intel      = get_market_intelligence()
    sentiment  = intel.get("sentiment", "NEUTRAL")
    nifty      = intel.get("nifty_level", 0)
    key_factors= intel.get("key_factors", [])
    logger.info(f"Intelligence: {sentiment} | Nifty: {nifty} | Factors: {len(key_factors)}")

    script        = generate_morning_script(intel)
    topic_display = script.get("topic_display", script.get("topic","Morning Brief")[:20])
    lines         = script.get("lines", [])
    logger.info(f"Script: {len(lines)} lines | Sentiment: {sentiment}")

    audio_path = str(OUTPUT_DIR / f"morning_reel_audio_{DATE_STR}.mp3")
    tts_ok     = await generate_tts(lines, audio_path)
    if not tts_ok:
        logger.error("TTS failed — aborting"); return

    video_path = str(OUTPUT_DIR / f"morning_reel_{DATE_STR}.mp4")
    video_ok   = create_morning_video(script, audio_path, video_path, intel)
    if not video_ok:
        logger.error("Video failed"); return

    # v2.3: Pass nifty_level to thumbnail builder
    thumb_path = build_thumbnail(topic_display, sentiment, TODAY_PALETTE, nifty_level=nifty)

    save_meta(script, video_path, thumb_path, intel)

    logger.info("=" * 55)
    logger.info(f"MORNING REEL v2.3 DONE")
    logger.info(f"  Sentiment: {sentiment} | Nifty: {nifty}")
    logger.info(f"  Title: {script.get('title', '')[:60]}")
    logger.info(f"  Factors: {', '.join(key_factors[:2])}")
    logger.info(f"  Video: {video_path}")
    logger.info(f"  Thumb: {thumb_path} (Nifty shown: {nifty > 0})")
    logger.info("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
