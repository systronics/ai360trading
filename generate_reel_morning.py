"""
generate_reel_morning.py — Morning Reel Generator (7:00 AM IST)
===============================================================
2nd daily reel — different from 8:30 PM ZENO reel.
Topic auto-selected by day of week + target country.
Style: motivational, educational, global audience focused.
Voice: hi-IN-SwaraNeural (Hindi) or en-US-JennyNeural (English version)

Schedule: 7:00 AM IST daily (separate from 8:30 PM ZENO reel)

Author: AI360Trading Automation
Last Updated: March 2026
"""

import os
import sys
import json
import asyncio
import logging
import random
from datetime import datetime
from pathlib import Path

import pytz
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import moviepy.editor as mp
import numpy as np

# AI360Trading modules
from ai_client import ai, img_client
from human_touch import ht, seo, MORNING_REEL_TOPICS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")


# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

ASSETS_DIR = Path("public")
MUSIC_DIR = ASSETS_DIR / "music"
IMAGE_DIR = ASSETS_DIR / "image"

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market")
LANG = os.environ.get("LANG_MODE", "hi")  # "hi" or "en"

TODAY = datetime.now(IST)
DATE_STR = TODAY.strftime("%Y%m%d")
WEEKDAY = TODAY.weekday()

# Video specs — 9:16 vertical for Shorts/Reels
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30
DURATION = 55  # seconds — slightly under 60 for reel eligibility

# Voice selection
VOICE_HI = "hi-IN-SwaraNeural"
VOICE_EN = "en-US-JennyNeural"


# ─────────────────────────────────────────────
# COLOR PALETTES — rotate by day for visual variety
# ─────────────────────────────────────────────

PALETTES = [
    {"bg": (15, 20, 40), "accent": (0, 200, 255), "text": (255, 255, 255), "name": "midnight_blue"},
    {"bg": (20, 40, 15), "accent": (50, 220, 100), "text": (255, 255, 255), "name": "forest_green"},
    {"bg": (40, 15, 15), "accent": (255, 80, 80), "text": (255, 255, 255), "name": "deep_red"},
    {"bg": (30, 20, 50), "accent": (180, 100, 255), "text": (255, 255, 255), "name": "royal_purple"},
    {"bg": (40, 30, 10), "accent": (255, 180, 0), "text": (255, 255, 255), "name": "golden"},
    {"bg": (10, 35, 45), "accent": (0, 180, 200), "text": (255, 255, 255), "name": "teal"},
    {"bg": (35, 15, 35), "accent": (255, 100, 200), "text": (255, 255, 255), "name": "magenta"},
]

TODAY_PALETTE = PALETTES[WEEKDAY % len(PALETTES)]


# ─────────────────────────────────────────────
# STEP 1: Generate Script
# ─────────────────────────────────────────────

def generate_morning_script() -> dict:
    """Generate morning reel script based on day/country/topic."""
    topic_data = MORNING_REEL_TOPICS[WEEKDAY]
    topic = topic_data["topic"]
    angle = topic_data["angle"]
    target_countries = topic_data["target_country"]

    hook = topic_data["hook_hi"] if LANG == "hi" else topic_data["hook_en"]
    cta = ht.get_cta(LANG)

    prompt = f"""
Create a 55-second morning reel script for AI360Trading.

Topic: {topic}
Angle: {angle}
Target Countries: {', '.join(target_countries)}
Language: {"Hindi-English mix (Hinglish)" if LANG == "hi" else "English"}
Time: 7:00 AM — morning motivation + market prep

Hook (already decided, use this exactly): {hook}

Script requirements:
- 8-10 short punchy lines (each line = 5-7 words max)
- Line 1: The hook above
- Lines 2-7: Key insight, 2-3 actionable points
- Line 8: Personal touch — real trader perspective
- Line 9-10: Strong CTA: {cta}
- Total reading time: ~50-55 seconds at normal pace
- Tone: Morning energy — motivating, clear, confident
- {"Include 2-3 English words naturally (Hinglish)" if LANG == "hi" else "Sound natural, not robotic"}

Return as JSON:
{{
  "title": "video title for YouTube (max 70 chars, SEO optimized)",
  "lines": ["line1", "line2", ...],
  "description": "YouTube description (200 chars, include global keywords)",
  "topic": "{topic}",
  "target_countries": {json.dumps(target_countries)}
}}
"""

    logger.info(f"🎬 Generating morning reel script — Topic: {topic}, Day: {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][WEEKDAY]}")

    result = ai.generate_json(
        prompt=prompt,
        content_mode=CONTENT_MODE,
        lang=LANG
    )

    # Fallback if JSON generation failed
    if not result or "lines" not in result:
        logger.warning("⚠️ JSON generation failed — using fallback script")
        result = _fallback_script(topic, hook, cta, target_countries)

    # Apply human touch to lines
    result["lines"] = ht.humanize_script_lines(result.get("lines", []), LANG)

    logger.info(f"✅ Script generated: {len(result.get('lines', []))} lines via {ai.active_provider}")
    return result


def _fallback_script(topic: str, hook: str, cta: str, countries: list) -> dict:
    """Fallback script when AI fails."""
    if LANG == "hi":
        lines = [
            hook,
            "Aaj ka market ek important message de raha hai.",
            "Smart traders yeh pehle se jaante hain.",
            "Har successful trade ke peeche ek plan hota hai.",
            "Risk manage karo — profit automatically aayega.",
            "Patience aur discipline — yeh do cheezein zaroori hain.",
            ht.get_personal_phrase("hi") + " consistent traders hi jeette hain.",
            cta,
        ]
    else:
        lines = [
            hook,
            "Today's market has an important message for traders.",
            "Smart money knows this before the open.",
            "Every successful trade starts with a clear plan.",
            "Manage your risk first — profits follow naturally.",
            "Patience and discipline are worth more than any indicator.",
            ht.get_personal_phrase("en") + " consistent traders always win long term.",
            cta,
        ]

    return {
        "title": f"{topic} — AI360Trading Morning Brief",
        "lines": lines,
        "description": f"Morning trading insight: {topic}. Daily market analysis for {', '.join(countries)} investors.",
        "topic": topic,
        "target_countries": countries,
    }


# ─────────────────────────────────────────────
# STEP 2: Generate TTS Audio
# ─────────────────────────────────────────────

async def generate_tts(lines: list, output_path: str) -> bool:
    """Generate TTS audio using Edge-TTS."""
    try:
        import edge_tts
    except ImportError:
        logger.error("edge-tts not installed")
        return False

    voice = VOICE_HI if LANG == "hi" else VOICE_EN
    speed = ht.get_tts_speed()
    rate_str = f"+{int((speed - 1) * 100)}%" if speed >= 1 else f"{int((speed - 1) * 100)}%"

    # Join lines with natural pauses
    full_text = ". ".join(lines)

    logger.info(f"🎤 TTS: voice={voice}, speed={speed}")

    communicate = edge_tts.Communicate(full_text, voice, rate=rate_str)
    await communicate.save(output_path)

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        logger.info(f"✅ TTS audio saved: {output_path}")
        return True

    logger.error("❌ TTS audio generation failed")
    return False


# ─────────────────────────────────────────────
# STEP 3: Create Video Frames
# ─────────────────────────────────────────────

def create_frame(
    line: str,
    line_index: int,
    total_lines: int,
    topic: str,
    palette: dict,
    zeno_image=None
) -> np.ndarray:
    """Create a single video frame for a script line."""
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color=palette["bg"])
    draw = ImageDraw.Draw(img)

    # Background gradient effect
    for y in range(VIDEO_HEIGHT):
        alpha = y / VIDEO_HEIGHT
        r = int(palette["bg"][0] * (1 - alpha * 0.3))
        g = int(palette["bg"][1] * (1 - alpha * 0.3))
        b = int(palette["bg"][2] * (1 + alpha * 0.2))
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(
            min(255, max(0, r)),
            min(255, max(0, g)),
            min(255, max(0, b))
        ))

    # Accent line at top
    draw.rectangle([(0, 0), (VIDEO_WIDTH, 8)], fill=palette["accent"])

    # AI360Trading watermark
    watermark_text = "AI360Trading"
    try:
        wm_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        wm_font = ImageFont.load_default()
    draw.text((40, 30), watermark_text, font=wm_font, fill=palette["accent"])

    # Progress dots
    dot_y = 90
    dot_spacing = 20
    dot_start_x = VIDEO_WIDTH // 2 - (total_lines * dot_spacing) // 2
    for i in range(total_lines):
        color = palette["accent"] if i <= line_index else (80, 80, 80)
        draw.ellipse(
            [(dot_start_x + i * dot_spacing - 5, dot_y - 5),
             (dot_start_x + i * dot_spacing + 5, dot_y + 5)],
            fill=color
        )

    # ZENO character (if available)
    if zeno_image:
        try:
            zeno_size = 300
            zeno_resized = zeno_image.resize((zeno_size, zeno_size), Image.LANCZOS)
            zeno_x = VIDEO_WIDTH - zeno_size - 40
            zeno_y = VIDEO_HEIGHT // 2 - zeno_size - 100
            if zeno_resized.mode == "RGBA":
                img.paste(zeno_resized, (zeno_x, zeno_y), zeno_resized)
            else:
                img.paste(zeno_resized, (zeno_x, zeno_y))
        except Exception as e:
            logger.warning(f"ZENO image paste failed: {e}")

    # Topic label
    try:
        topic_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        topic_font = ImageFont.load_default()

    topic_y = VIDEO_HEIGHT // 3
    draw.text(
        (VIDEO_WIDTH // 2, topic_y),
        topic.upper(),
        font=topic_font,
        fill=palette["accent"],
        anchor="mm"
    )

    # Main script line
    try:
        main_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
    except:
        main_font = ImageFont.load_default()

    # Word wrap
    words = line.split()
    wrapped_lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=main_font)
        if bbox[2] - bbox[0] > VIDEO_WIDTH - 120:
            if current:
                wrapped_lines.append(current)
            current = word
        else:
            current = test
    if current:
        wrapped_lines.append(current)

    text_y = VIDEO_HEIGHT // 2
    line_height = 70
    total_height = len(wrapped_lines) * line_height
    start_y = text_y - total_height // 2

    for i, wl in enumerate(wrapped_lines):
        draw.text(
            (VIDEO_WIDTH // 2, start_y + i * line_height),
            wl,
            font=main_font,
            fill=palette["text"],
            anchor="mm"
        )

    # Bottom accent
    draw.rectangle(
        [(0, VIDEO_HEIGHT - 8), (VIDEO_WIDTH, VIDEO_HEIGHT)],
        fill=palette["accent"]
    )

    # Morning badge
    badge_text = "🌅 MORNING BRIEF"
    try:
        badge_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        badge_font = ImageFont.load_default()
    draw.text(
        (VIDEO_WIDTH // 2, VIDEO_HEIGHT - 50),
        badge_text,
        font=badge_font,
        fill=palette["accent"],
        anchor="mm"
    )

    return np.array(img)


# ─────────────────────────────────────────────
# STEP 4: Compose Final Video
# ─────────────────────────────────────────────

def create_morning_video(script: dict, audio_path: str, output_path: str) -> bool:
    """Compose video from frames + audio + music."""
    lines = script.get("lines", [])
    topic = script.get("topic", "Morning Brief")

    if not lines:
        logger.error("No script lines")
        return False

    # Load ZENO image
    zeno_image = None
    zeno_path = IMAGE_DIR / "zeno_happy.png"
    if zeno_path.exists():
        try:
            zeno_image = Image.open(zeno_path).convert("RGBA")
        except Exception as e:
            logger.warning(f"Could not load ZENO: {e}")

    # Create frames — each line shown for proportional duration
    seconds_per_line = DURATION / len(lines)
    frames_per_line = int(FPS * seconds_per_line)

    all_frames = []
    for i, line in enumerate(lines):
        frame = create_frame(line, i, len(lines), topic, TODAY_PALETTE, zeno_image)
        for _ in range(frames_per_line):
            all_frames.append(frame)

    logger.info(f"🎬 Created {len(all_frames)} frames for {len(lines)} lines")

    # Build video clip
    def make_frame(t):
        frame_idx = min(int(t * FPS), len(all_frames) - 1)
        return all_frames[frame_idx]

    video = mp.VideoClip(make_frame, duration=DURATION)

    # Add audio
    clips_to_combine = []

    # Background music
    music_files = list(MUSIC_DIR.glob("bgmusic*.mp3")) if MUSIC_DIR.exists() else []
    if music_files:
        music_file = music_files[WEEKDAY % len(music_files)]
        try:
            bg_music = mp.AudioFileClip(str(music_file)).subclip(0, DURATION)
            bg_music = bg_music.volumex(0.15)  # Low volume
            clips_to_combine.append(bg_music)
        except Exception as e:
            logger.warning(f"Background music failed: {e}")

    # TTS audio
    if os.path.exists(audio_path):
        try:
            tts_audio = mp.AudioFileClip(audio_path).subclip(0, min(DURATION, mp.AudioFileClip(audio_path).duration))
            clips_to_combine.append(tts_audio)
        except Exception as e:
            logger.warning(f"TTS audio failed: {e}")

    # Combine audio
    if clips_to_combine:
        if len(clips_to_combine) > 1:
            final_audio = mp.CompositeAudioClip(clips_to_combine)
        else:
            final_audio = clips_to_combine[0]
        video = video.set_audio(final_audio)

    # Export
    logger.info(f"💾 Exporting morning reel: {output_path}")
    video.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None,
    )

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        logger.info(f"✅ Morning reel exported: {output_path}")
        return True

    logger.error("❌ Video export failed")
    return False


# ─────────────────────────────────────────────
# STEP 5: Save Meta + Caption
# ─────────────────────────────────────────────

def save_meta(script: dict, video_path: str) -> str:
    """Save metadata for upload scripts."""
    meta_path = OUTPUT_DIR / f"morning_reel_meta_{DATE_STR}.json"

    topic_data = MORNING_REEL_TOPICS[WEEKDAY]
    tags = seo.get_video_tags(CONTENT_MODE, is_short=True)
    global_tag = ht.get_posting_time_tag(topic_data["target_countries"])

    meta = {
        "date": DATE_STR,
        "type": "morning_reel",
        "video_path": video_path,
        "title": script.get("title", f"Morning Brief — {script.get('topic', '')} | AI360Trading"),
        "description": (
            f"{script.get('description', '')}\n\n"
            f"🔔 Subscribe for daily trading insights!\n"
            f"📱 Telegram signals: t.me/ai360trading\n\n"
            f"{global_tag}\n"
            f"{seo.format_article_tags(tags[:8])}"
        ),
        "tags": tags,
        "topic": script.get("topic"),
        "target_countries": topic_data["target_countries"],
        "ai_provider": ai.active_provider,
        "lang": LANG,
        "palette": TODAY_PALETTE["name"],
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Meta saved: {meta_path}")
    return str(meta_path)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

async def main():
    logger.info("=" * 60)
    logger.info(f"AI360Trading — Morning Reel Generator")
    logger.info(f"Day: {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][WEEKDAY]} | Mode: {CONTENT_MODE} | Lang: {LANG}")
    logger.info("=" * 60)

    # File paths
    audio_path = str(OUTPUT_DIR / f"morning_reel_audio_{DATE_STR}.mp3")
    video_path = str(OUTPUT_DIR / f"morning_reel_{DATE_STR}.mp4")

    # Step 1: Generate script
    script = generate_morning_script()
    logger.info(f"Topic: {script.get('topic')}")
    logger.info(f"Lines: {len(script.get('lines', []))}")

    # Step 2: TTS
    tts_ok = await generate_tts(script.get("lines", []), audio_path)
    if not tts_ok:
        logger.warning("⚠️ TTS failed — video will be silent")

    # Step 3 + 4: Create video
    video_ok = create_morning_video(script, audio_path, video_path)
    if not video_ok:
        logger.error("❌ Video creation failed")
        sys.exit(1)

    # Step 5: Save meta
    meta_path = save_meta(script, video_path)

    logger.info("=" * 60)
    logger.info("✅ Morning reel complete!")
    logger.info(f"   Video: {video_path}")
    logger.info(f"   Meta:  {meta_path}")
    logger.info(f"   AI:    {ai.active_provider}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
