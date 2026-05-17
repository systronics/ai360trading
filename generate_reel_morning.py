"""
generate_reel_morning.py — Morning Reel Generator (7:00 AM IST)
===============================================================
v2.1 FIXES (May 2026):

FIX 1 — Background music removed
  public/music/ deleted — no bgmusic files exist anymore
  TTS voice only — no copyright issues on any platform

FIX 2 — Live Nifty data injected before prompt
  Prevents AI using Nifty 18500 (2022-2023 training data)
  yfinance fetches ^NSEI live level before building prompt
  If yfinance fails: AI blocked from mentioning any specific level

FIX 3 — Proper thumbnail with big text
  Old: text lines on gradient — tiny on mobile
  New: ZENO 65% height + 120px bold yellow topic text
       Stock/topic name visible in 2 seconds on mobile feed

Schedule: 7:00 AM IST daily
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path

import pytz
from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mp
import numpy as np

from ai_client import ai, img_client
from human_touch import ht, seo, MORNING_REEL_TOPICS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

IMAGE_DIR = Path("public/image")

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market")
LANG         = os.environ.get("LANG_MODE", "hi")

TODAY    = datetime.now(IST)
DATE_STR = TODAY.strftime("%Y%m%d")
WEEKDAY  = TODAY.weekday()

VIDEO_WIDTH  = 1080
VIDEO_HEIGHT = 1920
FPS          = 30
DURATION     = 55

VOICE_HI = "hi-IN-SwaraNeural"
VOICE_EN = "en-US-JennyNeural"

PALETTES = [
    {"bg": (15, 20, 40),  "accent": (0, 200, 255),  "text": (255, 255, 255)},
    {"bg": (20, 40, 15),  "accent": (50, 220, 100),  "text": (255, 255, 255)},
    {"bg": (40, 15, 15),  "accent": (255, 80, 80),   "text": (255, 255, 255)},
    {"bg": (30, 20, 50),  "accent": (180, 100, 255), "text": (255, 255, 255)},
    {"bg": (40, 30, 10),  "accent": (255, 180, 0),   "text": (255, 255, 255)},
    {"bg": (10, 35, 45),  "accent": (0, 180, 200),   "text": (255, 255, 255)},
    {"bg": (35, 15, 35),  "accent": (255, 100, 200), "text": (255, 255, 255)},
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


# ─── v2.1 FIX 2: Live Nifty ───────────────────────────────────────────────────

def get_live_nifty_data() -> str:
    try:
        import yfinance as yf
        info = yf.Ticker("^NSEI").fast_info
        cmp  = info.get('last_price', 0)
        prev = info.get('previous_close', 0)
        if cmp > 15000 and prev > 0:
            pct     = round(((cmp-prev)/prev)*100, 2)
            cmp_int = int(round(cmp, 0))
            logger.info(f"[NIFTY] Live: {cmp_int} ({pct:+.2f}%)")
            return (
                f"\nLIVE MARKET DATA — use ONLY these numbers:\n"
                f"  Nifty 50 level: {cmp_int}\n"
                f"  Nifty change: {pct:+.2f}%\n"
                f"  CRITICAL: Never use 18500 or any level from memory. Use {cmp_int} only.\n"
            )
        raise ValueError(f"Unrealistic: {cmp}")
    except Exception as e:
        logger.warning(f"[NIFTY] Failed ({e}) — blocking hallucination")
        return (
            "\nCRITICAL: Do NOT mention any specific Nifty numbers. "
            "Say 'current market levels' only — never specify a number.\n"
        )


# ─── SCRIPT GENERATION ────────────────────────────────────────────────────────

def generate_morning_script() -> dict:
    topic_data       = MORNING_REEL_TOPICS[WEEKDAY]
    topic            = topic_data["topic"]
    angle            = topic_data["angle"]
    target_countries = topic_data["target_country"]
    hook             = topic_data["hook_hi"] if LANG == "hi" else topic_data["hook_en"]
    cta              = ht.get_cta(LANG)
    nifty_data       = get_live_nifty_data()

    prompt = f"""
Create a 55-second morning reel script for AI360Trading.
Topic: {topic}
Angle: {angle}
Target: {', '.join(target_countries)}
Language: {"Hinglish" if LANG == "hi" else "English"}
Hook (use exactly as line 1): {hook}

Requirements:
- 8-10 punchy lines (5-7 words each)
- Line 1 = hook above
- Lines 2-8 = key insight + actionable points
- Last line = CTA: {cta}
- Tone: Morning energy, motivating
{nifty_data}

Return JSON:
{{
  "title": "SEO title max 70 chars",
  "lines": ["line1","line2",...],
  "topic_display": "2-4 word topic for thumbnail (English only, no Hindi chars)",
  "description": "200 char YouTube description",
  "topic": "{topic}",
  "target_countries": {json.dumps(target_countries)}
}}"""

    logger.info(f"Generating morning reel — {topic}")
    result = ai.generate_json(prompt=prompt, content_mode=CONTENT_MODE, lang=LANG)

    if not result or "lines" not in result:
        logger.warning("Fallback script")
        result = _fallback_script(topic, hook, cta, target_countries)

    result["lines"] = ht.humanize_script_lines(result.get("lines", []), LANG)
    return result


def _fallback_script(topic, hook, cta, countries):
    lines = [hook,
        "Aaj ka market ek important message de raha hai." if LANG=="hi" else "Today's market has an important message.",
        "Smart traders yeh pehle se jaante hain." if LANG=="hi" else "Smart money knows this before the open.",
        "Har successful trade ke peeche ek plan hota hai." if LANG=="hi" else "Every successful trade starts with a plan.",
        "Risk manage karo profit aayega." if LANG=="hi" else "Manage risk first profits follow.",
        "Patience aur discipline zaroori hain." if LANG=="hi" else "Patience and discipline beat any indicator.",
        cta]
    return {
        "title": f"{topic} — AI360Trading",
        "lines": lines,
        "topic_display": topic[:20],
        "description": f"Morning insight: {topic}. For {', '.join(countries)} investors.",
        "topic": topic,
        "target_countries": countries,
    }


# ─── v2.1 FIX 3: PROPER THUMBNAIL ────────────────────────────────────────────

def build_thumbnail(topic_display, palette):
    """
    Morning reel thumbnail — drives CTR.

    Layout:
      - Bright colourful gradient (day-based palette)
      - ZENO happy — 65% height, right side
      - Topic text — 120px bold yellow, left side
      - "MORNING BRIEF" badge — top left
      - Time badge "7:00 AM" — accent colour
      - Accent bars top and bottom

    Why this drives more clicks than the old design:
      Old: Just text lines on gradient — no face, no focal point
      New: ZENO face visible + large topic text = clear in 2 seconds
    """
    W, H    = VIDEO_WIDTH, VIDEO_HEIGHT
    accent  = palette["accent"]
    bg      = palette["bg"]

    img = Image.new("RGB", (W, H))
    px  = img.load()
    for y in range(H):
        c = lerp(bg, tuple(min(255, x+30) for x in bg), y/H)
        for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")

    # Accent bars
    draw.rectangle([(0, 0), (W, 14)],   fill=accent)
    draw.rectangle([(0, H-14), (W, H)], fill=accent)

    # ZENO — right side, 65% height
    zeno_path = IMAGE_DIR / "zeno_happy.png"
    if not zeno_path.exists():
        zeno_path = IMAGE_DIR / "zeno_thinking.png"
    if zeno_path.exists():
        try:
            zeno   = Image.open(str(zeno_path)).convert("RGBA")
            zeno_h = int(H * 0.65)
            zeno_w = int(zeno.width * (zeno_h / zeno.height))
            zeno   = zeno.resize((zeno_w, zeno_h), Image.LANCZOS)
            zeno_x = W - zeno_w - 10
            zeno_y = H - zeno_h - 60
            img.paste(zeno, (zeno_x, zeno_y), zeno)
        except Exception as e:
            logger.warning(f"Thumbnail ZENO: {e}")

    draw = ImageDraw.Draw(img, "RGBA")

    f_big   = get_font(FONT_BOLD_PATHS, 120)
    f_sub   = get_font(FONT_BOLD_PATHS, 54)
    f_badge = get_font(FONT_BOLD_PATHS, 44)
    f_time  = get_font(FONT_BOLD_PATHS, 52)

    import textwrap
    safe_topic  = topic_display.upper() if topic_display else "MORNING BRIEF"
    topic_lines = textwrap.wrap(safe_topic, width=10)
    ty = 120
    for line in topic_lines[:3]:
        for dx, dy in [(-3,3),(3,-3),(-3,-3),(3,3)]:
            draw.text((80+dx, ty+dy), line, font=f_big,
                      fill=(0,0,0,200), anchor="la")
        draw.text((80, ty), line, font=f_big,
                  fill=(255, 200, 0), anchor="la")
        ty += 138

    # 7:00 AM badge
    draw.rounded_rectangle([(80, ty+20), (340, ty+90)], radius=14, fill=(*accent, 180))
    draw.text((210, ty+55), "⏰ 7:00 AM", font=f_time,
              fill=(0, 0, 0), anchor="mm")

    # MORNING BRIEF badge — top left
    draw.rounded_rectangle([(20, 20), (360, 80)], radius=14, fill=(255, 200, 0))
    draw.text((190, 50), "☀️ MORNING BRIEF", font=f_badge,
              fill=(0, 0, 0), anchor="mm")

    # AI360Trading watermark — bottom
    f_wm = get_font(FONT_REG_PATHS, 36)
    draw.text((W//2, H-60), "AI360Trading.in",
              font=f_wm, fill=(200, 220, 255, 200), anchor="mm")

    thumb_path = OUTPUT_DIR / f"morning_reel_thumb_{DATE_STR}.png"
    img.save(str(thumb_path), quality=95)
    logger.info(f"Thumbnail saved: {thumb_path.name}")
    return thumb_path


# ─── TTS ──────────────────────────────────────────────────────────────────────

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


# ─── FRAMES ───────────────────────────────────────────────────────────────────

def create_frame(line, line_index, total_lines, topic, palette, zeno_image=None):
    img  = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color=palette["bg"])
    draw = ImageDraw.Draw(img)

    for y in range(VIDEO_HEIGHT):
        alpha = y / VIDEO_HEIGHT
        r = int(palette["bg"][0] * (1 - alpha * 0.3))
        g = int(palette["bg"][1] * (1 - alpha * 0.3))
        b = int(palette["bg"][2] + alpha * 20)
        draw.line([(0,y),(VIDEO_WIDTH,y)],fill=(
            min(255,max(0,r)), min(255,max(0,g)), min(255,max(0,b))))

    draw.rectangle([(0,0),(VIDEO_WIDTH,8)], fill=palette["accent"])

    # Watermark
    wm_font = get_font(FONT_BOLD_PATHS, 36)
    draw.text((40,30), "AI360Trading", font=wm_font, fill=palette["accent"])

    # Progress dots
    dot_y    = 90; dot_sp = 20
    dot_sx   = VIDEO_WIDTH//2 - (total_lines*dot_sp)//2
    for i in range(total_lines):
        col = palette["accent"] if i <= line_index else (80,80,80)
        draw.ellipse([(dot_sx+i*dot_sp-5,dot_y-5),(dot_sx+i*dot_sp+5,dot_y+5)], fill=col)

    # ZENO
    if zeno_image:
        try:
            zh = int(VIDEO_HEIGHT*0.45); zw = int(zeno_image.width*(zh/zeno_image.height))
            zr = zeno_image.resize((zw,zh),Image.LANCZOS)
            zx = VIDEO_WIDTH-zw-20; zy = VIDEO_HEIGHT-zh
            img.paste(zr,(zx,zy),zr)
        except: pass

    # Topic label
    tl_font = get_font(FONT_BOLD_PATHS, 38)
    draw     = ImageDraw.Draw(img)
    draw.text((VIDEO_WIDTH//2, VIDEO_HEIGHT//3), topic.upper(),
              font=tl_font, fill=palette["accent"], anchor="mm")

    # Main text
    main_font  = get_font(FONT_BOLD_PATHS, 62)
    words      = line.split(); wrapped = []; cur = ""
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
        draw.text((VIDEO_WIDTH//2, start_y+i*74),
                  wl, font=main_font, fill=palette["text"], anchor="mm")

    draw.rectangle([(0,VIDEO_HEIGHT-10),(VIDEO_WIDTH,VIDEO_HEIGHT)], fill=palette["accent"])
    draw.text((VIDEO_WIDTH//2, VIDEO_HEIGHT-55), "MORNING BRIEF",
              font=get_font(FONT_BOLD_PATHS,30), fill=palette["accent"], anchor="mm")

    return np.array(img)


# ─── VIDEO COMPOSITION — NO MUSIC ─────────────────────────────────────────────

def create_morning_video(script, audio_path, output_path) -> bool:
    lines = script.get("lines", [])
    topic = script.get("topic", "Morning Brief")
    if not lines: logger.error("No lines"); return False

    # Load ZENO
    zeno_image = None
    for zp in [IMAGE_DIR/"zeno_happy.png", IMAGE_DIR/"zeno_thinking.png"]:
        if zp.exists():
            try: zeno_image = Image.open(str(zp)).convert("RGBA"); break
            except: pass

    spl     = DURATION / len(lines)
    fpl     = int(FPS * spl)
    frames  = []
    for i, line in enumerate(lines):
        f = create_frame(line, i, len(lines), topic, TODAY_PALETTE, zeno_image)
        for _ in range(fpl): frames.append(f)

    def make_frame(t):
        idx = min(int(t*FPS), len(frames)-1)
        return frames[idx]

    video = mp.VideoClip(make_frame, duration=DURATION)

    # TTS only — NO background music (prevents Meta muting)
    if os.path.exists(audio_path):
        try:
            tts   = mp.AudioFileClip(audio_path)
            dur   = min(DURATION, tts.duration)
            tts   = tts.subclip(0, dur)
            video = video.set_audio(tts)
            logger.info("Audio: TTS only (no bgmusic — no copyright risk)")
        except Exception as e:
            logger.warning(f"Audio attach: {e}")

    video.write_videofile(
        output_path, fps=FPS, codec="libx264",
        audio_codec="aac", verbose=False, logger=None
    )
    ok = os.path.exists(output_path) and os.path.getsize(output_path) > 0
    if ok: logger.info(f"Video exported: {output_path}")
    else:  logger.error("Video export failed")
    return ok


# ─── META ─────────────────────────────────────────────────────────────────────

def save_meta(script, video_path, thumb_path) -> str:
    meta_path = OUTPUT_DIR / f"morning_reel_meta_{DATE_STR}.json"
    tags      = seo.get_video_tags(CONTENT_MODE, is_short=True)
    meta = {
        "title":            script.get("title", "Morning Brief — AI360Trading"),
        "description":      script.get("description", "Morning market insight."),
        "tags":             seo.get_youtube_safe_tags(tags),
        "topic":            script.get("topic", ""),
        "target_countries": script.get("target_countries", ["India","USA","UK"]),
        "lang":             LANG,
        "content_mode":     CONTENT_MODE,
        "date":             DATE_STR,
        "video_path":       str(video_path),
        "thumb_path":       str(thumb_path),
        "music":            "none — TTS voice only",
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    logger.info(f"Meta saved: {meta_path}")
    return str(meta_path)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

async def main():
    logger.info(f"Morning Reel v2.1 — {TODAY.strftime('%A %d %b %Y')} | {CONTENT_MODE.upper()} | {LANG.upper()}")

    script       = generate_morning_script()
    topic_display= script.get("topic_display", script.get("topic","Morning Brief")[:20])
    lines        = script.get("lines", [])
    logger.info(f"Script: {len(lines)} lines | Topic: {script.get('topic','')}")

    audio_path = str(OUTPUT_DIR / f"morning_reel_audio_{DATE_STR}.mp3")
    tts_ok     = await generate_tts(lines, audio_path)
    if not tts_ok:
        logger.error("TTS failed — aborting"); return

    video_path = str(OUTPUT_DIR / f"morning_reel_{DATE_STR}.mp4")
    video_ok   = create_morning_video(script, audio_path, video_path)
    if not video_ok:
        logger.error("Video failed"); return

    # v2.1 FIX: Build proper thumbnail
    thumb_path = build_thumbnail(topic_display, TODAY_PALETTE)

    save_meta(script, video_path, thumb_path)

    logger.info("=" * 55)
    logger.info(f"MORNING REEL DONE")
    logger.info(f"  Video:     {video_path}")
    logger.info(f"  Thumbnail: {thumb_path}")
    logger.info(f"  Music:     none (no copyright risk)")
    logger.info("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
