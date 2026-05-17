"""
generate_reel_morning.py — Morning Reel Generator (7:00 AM IST)
===============================================================
v2.1 FIXES (May 2026):

FIX 1 — Background music muted by Meta
  Problem: bgmusic*.mp3 files are copyrighted — Meta mutes video in many countries
           "Your video is muted in certain countries where Meta does not have music rights"
           Result: video plays silently = zero watch time on Facebook
  Fix: Background music completely removed
       TTS voice only — clear and professional
       No copyright issues ever

FIX 2 — Stale Nifty level (18500 from 2022-2023 training data)
  Problem: AI prompt had no live data → AI used training memory → Nifty 18500 shown
           Current Nifty = 23,643 — wrong data looks unprofessional
  Fix: Fetch live Nifty from yfinance before building prompt
       Inject live level + % change into prompt
       If yfinance fails: block AI from mentioning any specific level

2nd daily reel — different from 8:30 PM ZENO reel.
Topic auto-selected by day of week + target country.
Style: motivational, educational, global audience focused.
Voice: hi-IN-SwaraNeural (Hindi) or en-US-JennyNeural (English)
Schedule: 7:00 AM IST daily
"""

import os
import json
import asyncio
import logging
import random
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

ASSETS_DIR = Path("public")
IMAGE_DIR  = ASSETS_DIR / "image"

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


# ─────────────────────────────────────────────
# v2.1 FIX 2: Fetch live Nifty data
# ─────────────────────────────────────────────

def get_live_nifty_data() -> str:
    """
    Fetch live Nifty 50 level from yfinance.
    Returns string injected into AI prompt.

    Prevents AI from using stale training data levels like 18500.
    """
    try:
        import yfinance as yf
        ticker = yf.Ticker("^NSEI")
        info   = ticker.fast_info
        cmp    = info.get('last_price', 0)
        prev   = info.get('previous_close', 0)

        if cmp > 15000 and prev > 0:
            pct     = round(((cmp - prev) / prev) * 100, 2)
            cmp_int = int(round(cmp, 0))
            logger.info(f"[NIFTY] Live: {cmp_int} ({pct:+.2f}%)")
            return (
                f"\nLIVE MARKET DATA — use ONLY these numbers:\n"
                f"  Nifty 50 level today: {cmp_int}\n"
                f"  Nifty change: {pct:+.2f}%\n"
                f"  CRITICAL: Never use 18500, 22000, or any other Nifty level from memory.\n"
                f"  If you mention Nifty, always say {cmp_int} only.\n"
            )
        raise ValueError(f"Unrealistic Nifty value: {cmp}")

    except Exception as e:
        logger.warning(f"[NIFTY] yfinance failed ({e}) — blocking hallucination")
        return (
            "\nCRITICAL RULE: Do NOT mention any specific Nifty or index numbers. "
            "You have no live data. Say 'current market' or 'today's levels' "
            "without ever specifying any number.\n"
        )


# ─────────────────────────────────────────────
# STEP 1: Generate Script
# ─────────────────────────────────────────────

def generate_morning_script() -> dict:
    """Generate morning reel script — with live Nifty data injected."""
    topic_data       = MORNING_REEL_TOPICS[WEEKDAY]
    topic            = topic_data["topic"]
    angle            = topic_data["angle"]
    target_countries = topic_data["target_country"]
    hook             = topic_data["hook_hi"] if LANG == "hi" else topic_data["hook_en"]
    cta              = ht.get_cta(LANG)

    # v2.1 FIX: Get live Nifty data BEFORE building prompt
    nifty_data = get_live_nifty_data()

    prompt = f"""
Create a 55-second morning reel script for AI360Trading.

Topic: {topic}
Angle: {angle}
Target Countries: {', '.join(target_countries)}
Language: {"Hindi-English mix (Hinglish)" if LANG == "hi" else "English"}
Time: 7:00 AM — morning motivation + market prep

Hook (use this exactly as line 1): {hook}

Script requirements:
- 8-10 short punchy lines (each line = 5-7 words max)
- Line 1: The hook above
- Lines 2-7: Key insight, 2-3 actionable points
- Line 8: Personal touch — real trader perspective
- Line 9-10: Strong CTA: {cta}
- Total reading time: ~50-55 seconds at normal pace
- Tone: Morning energy — motivating, clear, confident
- {"Hinglish (Hindi + English mix)" if LANG == "hi" else "Natural English"}

{nifty_data}

Return as JSON:
{{
  "title": "SEO-optimised YouTube title max 70 chars",
  "lines": ["line1", "line2", ...],
  "description": "YouTube description 200 chars with global keywords",
  "topic": "{topic}",
  "target_countries": {json.dumps(target_countries)}
}}
"""

    logger.info(f"Generating morning reel — {topic} | {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][WEEKDAY]}")

    result = ai.generate_json(prompt=prompt, content_mode=CONTENT_MODE, lang=LANG)

    if not result or "lines" not in result:
        logger.warning("JSON generation failed — using fallback")
        result = _fallback_script(topic, hook, cta, target_countries)

    result["lines"] = ht.humanize_script_lines(result.get("lines", []), LANG)
    logger.info(f"Script ready: {len(result.get('lines', []))} lines via {ai.active_provider}")
    return result


def _fallback_script(topic, hook, cta, countries):
    lines = [
        hook,
        "Aaj ka market ek important message de raha hai." if LANG == "hi" else "Today's market has an important message.",
        "Smart traders yeh pehle se jaante hain." if LANG == "hi" else "Smart money knows this before the open.",
        "Har successful trade ke peeche ek plan hota hai." if LANG == "hi" else "Every successful trade starts with a plan.",
        "Risk manage karo — profit automatically aayega." if LANG == "hi" else "Manage risk first — profits follow naturally.",
        "Patience aur discipline — yeh do cheezein zaroori hain." if LANG == "hi" else "Patience and discipline beat any indicator.",
        ht.get_personal_phrase(LANG) + (" consistent traders hi jeette hain." if LANG == "hi" else " consistent traders always win."),
        cta,
    ]
    return {
        "title": f"{topic} — AI360Trading Morning Brief",
        "lines": lines,
        "description": f"Morning trading insight: {topic}. For {', '.join(countries)} investors.",
        "topic": topic,
        "target_countries": countries,
    }


# ─────────────────────────────────────────────
# STEP 2: Generate TTS Audio
# ─────────────────────────────────────────────

async def generate_tts(lines: list, output_path: str) -> bool:
    """Generate TTS audio — voice only, no background music."""
    try:
        import edge_tts
    except ImportError:
        logger.error("edge-tts not installed")
        return False

    voice    = VOICE_HI if LANG == "hi" else VOICE_EN
    speed    = ht.get_tts_speed()
    rate_str = f"+{int((speed - 1) * 100)}%" if speed >= 1 else f"{int((speed - 1) * 100)}%"
    full_text = ". ".join(lines)

    logger.info(f"TTS: voice={voice}, speed={speed}")
    communicate = edge_tts.Communicate(full_text, voice, rate=rate_str)
    await communicate.save(output_path)

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        logger.info(f"TTS saved: {output_path}")
        return True

    logger.error("TTS failed")
    return False


# ─────────────────────────────────────────────
# STEP 3: Create Video Frames
# ─────────────────────────────────────────────

def create_frame(line, line_index, total_lines, topic, palette, zeno_image=None):
    img  = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color=palette["bg"])
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(VIDEO_HEIGHT):
        alpha = y / VIDEO_HEIGHT
        r = int(palette["bg"][0] * (1 - alpha * 0.3))
        g = int(palette["bg"][1] * (1 - alpha * 0.3))
        b = int(palette["bg"][2] + alpha * 20)
        draw.line([(0, y), (VIDEO_WIDTH, y)],
                  fill=(min(255,max(0,r)), min(255,max(0,g)), min(255,max(0,b))))

    # Top accent bar
    draw.rectangle([(0, 0), (VIDEO_WIDTH, 8)], fill=palette["accent"])

    # Watermark
    try:
        wm_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        wm_font = ImageFont.load_default()
    draw.text((40, 30), "AI360Trading", font=wm_font, fill=palette["accent"])

    # Progress dots
    dot_y       = 90
    dot_spacing = 20
    dot_start_x = VIDEO_WIDTH // 2 - (total_lines * dot_spacing) // 2
    for i in range(total_lines):
        color = palette["accent"] if i <= line_index else (80, 80, 80)
        draw.ellipse([(dot_start_x + i*dot_spacing - 5, dot_y - 5),
                      (dot_start_x + i*dot_spacing + 5, dot_y + 5)], fill=color)

    # ZENO character
    if zeno_image:
        try:
            zeno_size    = 300
            zeno_resized = zeno_image.resize((zeno_size, zeno_size), Image.LANCZOS)
            zx = VIDEO_WIDTH - zeno_size - 40
            zy = VIDEO_HEIGHT // 2 - zeno_size - 100
            if zeno_resized.mode == "RGBA":
                img.paste(zeno_resized, (zx, zy), zeno_resized)
            else:
                img.paste(zeno_resized, (zx, zy))
        except Exception as e:
            logger.warning(f"ZENO paste failed: {e}")

    # Topic label
    try:
        topic_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        topic_font = ImageFont.load_default()
    draw.text((VIDEO_WIDTH // 2, VIDEO_HEIGHT // 3), topic.upper(),
              font=topic_font, fill=palette["accent"], anchor="mm")

    # Main text line
    try:
        main_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
    except:
        main_font = ImageFont.load_default()

    words         = line.split()
    wrapped_lines = []
    current       = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=main_font)
        if bbox[2] - bbox[0] > VIDEO_WIDTH - 120:
            if current: wrapped_lines.append(current)
            current = word
        else:
            current = test
    if current: wrapped_lines.append(current)

    text_y       = VIDEO_HEIGHT // 2
    line_height  = 70
    total_height = len(wrapped_lines) * line_height
    start_y      = text_y - total_height // 2

    for i, wl in enumerate(wrapped_lines):
        draw.text((VIDEO_WIDTH // 2, start_y + i * line_height),
                  wl, font=main_font, fill=palette["text"], anchor="mm")

    # Bottom bar
    draw.rectangle([(0, VIDEO_HEIGHT - 8), (VIDEO_WIDTH, VIDEO_HEIGHT)], fill=palette["accent"])

    # Morning badge
    try:
        badge_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        badge_font = ImageFont.load_default()
    draw.text((VIDEO_WIDTH // 2, VIDEO_HEIGHT - 50), "MORNING BRIEF",
              font=badge_font, fill=palette["accent"], anchor="mm")

    return np.array(img)


# ─────────────────────────────────────────────
# STEP 4: Compose Video
# v2.1 FIX: No background music — TTS voice only
# ─────────────────────────────────────────────

def create_morning_video(script, audio_path, output_path) -> bool:
    lines = script.get("lines", [])
    topic = script.get("topic", "Morning Brief")

    if not lines:
        logger.error("No script lines")
        return False

    # Load ZENO
    zeno_image = None
    zeno_path  = IMAGE_DIR / "zeno_happy.png"
    if zeno_path.exists():
        try:
            zeno_image = Image.open(zeno_path).convert("RGBA")
        except Exception as e:
            logger.warning(f"ZENO load failed: {e}")

    # Create frames
    seconds_per_line = DURATION / len(lines)
    frames_per_line  = int(FPS * seconds_per_line)
    all_frames       = []

    for i, line in enumerate(lines):
        frame = create_frame(line, i, len(lines), topic, TODAY_PALETTE, zeno_image)
        for _ in range(frames_per_line):
            all_frames.append(frame)

    logger.info(f"Created {len(all_frames)} frames for {len(lines)} lines")

    def make_frame(t):
        frame_idx = min(int(t * FPS), len(all_frames) - 1)
        return all_frames[frame_idx]

    video = mp.VideoClip(make_frame, duration=DURATION)

    # v2.1 FIX: TTS audio only — NO background music (prevents Meta muting)
    if os.path.exists(audio_path):
        try:
            tts_audio = mp.AudioFileClip(audio_path)
            tts_dur   = min(DURATION, tts_audio.duration)
            tts_audio = tts_audio.subclip(0, tts_dur)
            video     = video.set_audio(tts_audio)
            logger.info("Audio: TTS voice only (no background music — prevents Meta copyright muting)")
        except Exception as e:
            logger.warning(f"TTS audio attach failed: {e}")

    logger.info(f"Exporting: {output_path}")
    video.write_videofile(
        output_path, fps=FPS, codec="libx264", audio_codec="aac",
        verbose=False, logger=None
    )

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        logger.info(f"Morning reel exported: {output_path}")
        return True

    logger.error("Video export failed")
    return False


# ─────────────────────────────────────────────
# STEP 5: Save Meta
# ─────────────────────────────────────────────

def save_meta(script, video_path) -> str:
    meta_path = OUTPUT_DIR / f"morning_reel_meta_{DATE_STR}.json"
    tags      = seo.get_video_tags(CONTENT_MODE, is_short=True)

    target_countries = script.get("target_countries",
                       MORNING_REEL_TOPICS[WEEKDAY].get("target_country", ["Global"]))

    meta = {
        "title":            script.get("title", "Morning Brief — AI360Trading"),
        "description":      script.get("description", "Morning market insight."),
        "tags":             seo.get_youtube_safe_tags(tags),
        "topic":            script.get("topic", ""),
        "target_countries": target_countries,
        "lang":             LANG,
        "content_mode":     CONTENT_MODE,
        "date":             DATE_STR,
        "video_path":       str(video_path),
        "posting_tags":     ht.get_posting_time_tag(target_countries),
        "music":            "none — TTS voice only (no copyright issues)",
    }

    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    logger.info(f"Meta saved: {meta_path}")
    return str(meta_path)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

async def main():
    logger.info(f"Morning Reel v2.1 — {TODAY.strftime('%A %d %b %Y')} | Mode: {CONTENT_MODE} | Lang: {LANG}")

    # Step 1: Script (with live Nifty data)
    script = generate_morning_script()
    lines  = script.get("lines", [])
    logger.info(f"Script: {len(lines)} lines | Topic: {script.get('topic','')}")

    # Step 2: TTS
    audio_path = str(OUTPUT_DIR / f"morning_reel_audio_{DATE_STR}.mp3")
    tts_ok     = await generate_tts(lines, audio_path)
    if not tts_ok:
        logger.error("TTS failed — aborting")
        return

    # Step 3+4: Video
    video_path = str(OUTPUT_DIR / f"morning_reel_{DATE_STR}.mp4")
    video_ok   = create_morning_video(script, audio_path, video_path)
    if not video_ok:
        logger.error("Video creation failed")
        return

    # Step 5: Meta
    meta_path = save_meta(script, video_path)

    logger.info("=" * 55)
    logger.info(f"MORNING REEL DONE")
    logger.info(f"  Title: {script.get('title','')}")
    logger.info(f"  Topic: {script.get('topic','')}")
    logger.info(f"  Lines: {len(lines)}")
    logger.info(f"  Video: {video_path}")
    logger.info(f"  Music: none (no copyright risk)")
    logger.info("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
