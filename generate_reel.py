"""
generate_reel.py — AI360Trading ZENO Evening Reel (8:30 PM IST)
================================================================
UPGRADED: Groq → ai_client (Groq→Gemini→Claude→OpenAI→Templates fallback)
UPGRADED: human_touch hook + TTS speed variation + CTA rotation
PRESERVED: All ZENO visual logic, meta JSON structure, output filenames

Output files (unchanged — upload scripts depend on these):
  output/final_zeno_reel.mp4
  output/reel_YYYYMMDD.mp4
  output/meta_YYYYMMDD.json

Author: AI360Trading Automation
Last Updated: March 2026
"""

import os
import json
import asyncio
import shutil
from datetime import datetime
from pathlib import Path
import pytz
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip
)

# ── AI Fallback Chain (replaces direct Groq import) ──────────────────────────
from ai_client import ai
from human_touch import ht

# ─── Content Mode ─────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")
print(f"[MODE] generate_reel.py running in mode: {CONTENT_MODE.upper()}")

# --- CONFIGURATION & PATHS ---
OUT = Path("output")
IMAGE_DIR = Path("public/image")
MUSIC_DIR = Path("public/music")
SW, SH = 1080, 1920
FPS = 30
IST = pytz.timezone("Asia/Kolkata")

os.makedirs(OUT, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE = (255, 255, 255)


def get_font(path, size):
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def get_bg_music():
    day = datetime.now().weekday()
    music_map = {
        0: "bgmusic1.mp3", 1: "bgmusic2.mp3", 2: "bgmusic3.mp3",
        3: "bgmusic1.mp3", 4: "bgmusic2.mp3", 5: "bgmusic3.mp3",
        6: "bgmusic1.mp3"
    }
    f = MUSIC_DIR / music_map[day]
    if f.exists():
        return f
    for f in MUSIC_DIR.glob("*.mp3"):
        return f
    return None


# ─────────────────────────────────────────────
# SCRIPT GENERATION — upgraded to ai_client
# ─────────────────────────────────────────────

def generate_script():
    """Generate fresh daily Hinglish script via ai_client fallback chain."""
    today = datetime.now(IST).strftime("%A, %d %B %Y")

    # Get rotating hook + personal phrase from human_touch
    hook = ht.get_hook(mode=CONTENT_MODE, lang="hi", holiday_name=HOLIDAY_NAME)
    personal_phrase = ht.get_personal_phrase(lang="hi")
    tts_speed = ht.get_tts_speed()

    # Topic selection based on CONTENT_MODE
    if CONTENT_MODE == "holiday":
        holiday_label = HOLIDAY_NAME if HOLIDAY_NAME else "Indian Market Holiday"
        topic = (
            f"special {holiday_label} message — inspire viewers to use this market holiday "
            f"to learn, plan investments, and grow financially. "
            f"Motivational, educational, no live market data. "
            f"Global appeal: relevant to viewers in India, US, UK and Brazil."
        )
    elif CONTENT_MODE == "weekend":
        topic = (
            "emotional life lesson about patience, discipline or money mindset — no market data. "
            "Motivational and educational for global audience: India, US, UK, Brazil."
        )
    else:
        topic = "stock market trading wisdom, psychology, or risk management lesson for Indian traders"

    prompt = f"""You are ZENO — a wise animated kid character teaching trading wisdom in Hinglish to Indian traders.

Today is {today}. Create a 45-60 second reel script on: {topic}

OPENING HOOK (use this exactly as your very first line): "{hook}"

PERSONAL VOICE (inject this naturally somewhere in the middle): "{personal_phrase}"

Rules:
- Hinglish only (natural Hindi + English mix)
- Simple enough for a 10-year-old to understand
- Emotional, relatable, human touch
- One clear lesson only
- End with strong message
- Sound like a REAL person, not an AI

Respond ONLY with valid JSON, no markdown:
{{
  "title": "SHORT ENGLISH TITLE MAX 4 WORDS IN CAPS (for display on screen)",
  "audio_script": "full spoken Hinglish script 80-100 words. Start with the hook above.",
  "display_text": "one powerful Hindi/Hinglish line shown on screen (max 12 words)",
  "emotion": "one of: happy, sad, fear, angry, thinking, greed, celebrating",
  "sentiment": "one of: positive, negative, fearful, motivated, greedy, angry, neutral",
  "description": "2 sentence English/Hinglish description for YouTube and Instagram"
}}"""

    print("🤖 Generating daily ZENO script via ai_client...")

    result = ai.generate_json(
        prompt=prompt,
        content_mode=CONTENT_MODE,
        lang="hi"
    )

    print(f"✅ Script ready via {ai.active_provider} — emotion: {result.get('emotion')} | title: {result.get('title')}")

    # Apply human touch to audio script
    if result.get("audio_script"):
        result["audio_script"] = ht.humanize(result["audio_script"], lang="hi")

    # Store tts_speed for use in generate_reel
    result["_tts_speed"] = tts_speed
    return result


# ─────────────────────────────────────────────
# ZENO VISUAL — unchanged from original
# ─────────────────────────────────────────────

def apply_zeno_disney_effect(base_img, emotion="thinking"):
    zeno_path = IMAGE_DIR / f"zeno_{emotion}.png"
    if not zeno_path.exists():
        print(f"⚠️ Zeno image missing: {zeno_path} — using fallback")
        zeno_path = IMAGE_DIR / "zeno_thinking.png"
    if not zeno_path.exists():
        return base_img

    zeno = Image.open(str(zeno_path)).convert("RGBA")
    target_w = int(SW * 0.85)
    w_ratio = target_w / float(zeno.size[0])
    target_h = int(float(zeno.size[1]) * float(w_ratio))
    zeno = zeno.resize((target_w, target_h), Image.LANCZOS)

    shadow_layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    zeno_mask = zeno.split()[3]
    shadow_offset = (15, 15)
    shadow_pos = (
        (SW - zeno.width) // 2 + shadow_offset[0],
        SH - zeno.height - 180 + shadow_offset[1]
    )
    shadow_img = Image.new("RGBA", zeno.size, (0, 0, 0, 110))
    shadow_layer.paste(shadow_img, shadow_pos, zeno_mask)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=15))

    temp_bg = base_img.convert("RGBA")
    combined = Image.alpha_composite(temp_bg, shadow_layer)
    zeno_pos = ((SW - zeno.width) // 2, SH - zeno.height - 200)
    combined.paste(zeno, zeno_pos, zeno)
    return combined.convert("RGB")


def build_reel_frame(title_text, display_text, emotion="thinking"):
    img = Image.new("RGB", (SW, SH))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(SH):
        top_color, bot_color = (5, 10, 25), (15, 30, 70)
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * (y / SH))
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * (y / SH))
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * (y / SH))
        draw.line([(0, y), (SW, y)], fill=(r, g, b))

    draw.ellipse([100, 100, SW - 100, 600], fill=(60, 140, 255, 30))
    img = apply_zeno_disney_effect(img, emotion)
    draw_text = ImageDraw.Draw(img)

    font_title = get_font(FONT_BOLD, 85)
    text_y = 300
    words = title_text.split()
    mid = max(1, len(words) // 2)
    line1 = " ".join(words[:mid])
    line2 = " ".join(words[mid:])

    for line, offset in [(line1, 0), (line2, 105)]:
        if not line:
            continue
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            draw_text.text((SW // 2 + dx, text_y + offset + dy),
                           line, font=font_title, fill=(0, 0, 0), anchor="mm")
        draw_text.text((SW // 2, text_y + offset),
                       line, font=font_title, fill=WHITE, anchor="mm")

    font_display = get_font(FONT_BOLD, 44)
    display_y = SH - 340
    draw_text.rectangle([(0, display_y - 30), (SW, display_y + 90)],
                         fill=(0, 0, 0, 140))

    words_d, line_d, disp_lines = display_text.split(), "", []
    for w in words_d:
        test = (line_d + " " + w).strip()
        bbox = font_display.getbbox(test)
        if bbox[2] - bbox[0] < SW - 80:
            line_d = test
        else:
            disp_lines.append(line_d)
            line_d = w
    if line_d:
        disp_lines.append(line_d)

    for i, dl in enumerate(disp_lines[:2]):
        draw_text.text((SW // 2, display_y + i * 55),
                       dl, font=font_display, fill=(255, 220, 80), anchor="mm")

    font_brand = get_font(FONT_BOLD, 36)
    draw_text.text((SW // 2, SH - 220),
                   "✨ ai360trading.in", font=font_brand,
                   fill=(160, 200, 255), anchor="mm")
    draw_text.text((SW // 2, SH - 160),
                   "📱 t.me/ai360trading", font=font_brand,
                   fill=(140, 180, 240), anchor="mm")

    path = OUT / "zeno_reel_frame.png"
    img.save(str(path))
    return path


# ─────────────────────────────────────────────
# MAIN REEL GENERATOR
# ─────────────────────────────────────────────

async def generate_reel():
    print("🎬 Starting ZENO Evening Reel Generation...")
    today = datetime.now().strftime("%Y%m%d")

    script = generate_script()

    title        = script.get("title", "TRADING WISDOM")
    audio_script = script.get("audio_script", "Trading mein patience sabse zaroori hai.")
    display_text = script.get("display_text", "Patience hi success hai।")
    emotion      = script.get("emotion", "thinking")
    sentiment    = script.get("sentiment", "neutral")
    description  = script.get("description", "Daily trading wisdom by ZENO. Follow ai360trading.")
    tts_speed    = script.get("_tts_speed", 1.0)

    # Human-touch TTS speed variation
    rate_str = f"+{int((tts_speed - 1) * 100)}%" if tts_speed >= 1.0 else f"{int((tts_speed - 1) * 100)}%"

    audio_path = OUT / "zeno_speech.mp3"
    print(f"🎙️ Generating Voice (speed: {rate_str})...")
    await edge_tts.Communicate(
        audio_script, "hi-IN-SwaraNeural", rate=rate_str
    ).save(str(audio_path))

    frame_path = build_reel_frame(title, display_text, emotion)

    print("🎞️ Rendering Final ZENO Reel...")
    voice_clip = AudioFileClip(str(audio_path))
    music_file = get_bg_music()

    if music_file:
        try:
            bg_m = AudioFileClip(str(music_file)).volumex(0.12).set_duration(voice_clip.duration)
            final_audio = CompositeAudioClip([voice_clip, bg_m])
            print(f"🎵 Music: {music_file.name}")
        except Exception as e:
            print(f"⚠️ Music error: {e}")
            final_audio = voice_clip
    else:
        final_audio = voice_clip

    video = (
        ImageClip(str(frame_path))
        .set_duration(voice_clip.duration + 0.5)
        .set_audio(final_audio)
    )

    output_file = OUT / "final_zeno_reel.mp4"
    video.write_videofile(
        str(output_file), fps=FPS,
        codec="libx264", audio_codec="aac", logger=None
    )

    reel_dated = OUT / f"reel_{today}.mp4"
    shutil.copy2(str(output_file), str(reel_dated))
    print(f"✅ Video saved: {output_file.name} + {reel_dated.name}")

    # Rotating CTA from human_touch
    cta = ht.get_cta(lang="hi")

    # Meta JSON — structure UNCHANGED (upload_youtube.py, upload_facebook.py, upload_instagram.py depend on this)
    meta = {
        "title": f"ZENO Ki Baat - {title}",
        "description": description + f" 🔗 t.me/ai360trading | ai360trading.in\n{cta}",
        "sentiment": sentiment,
        "content_mode": CONTENT_MODE,
        "hashtags": "#ZenoKiBaat #ai360trading #StockMarketIndia #TradingWisdom #Hinglish #FinancialLiteracy",
        "public_video_url": "",
        "ai_provider": ai.active_provider,
    }

    meta_path = OUT / f"meta_{today}.json"
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"✅ Meta saved: {meta_path.name}")

    print("\n" + "=" * 50)
    print(f"✅ REEL SUCCESS: {output_file}")
    print(f"TITLE: ZENO Ki Baat - {title}")
    print(f"MODE: {CONTENT_MODE.upper()}")
    print(f"DESC: {display_text}")
    print(f"EMOTION: {emotion} | SENTIMENT: {sentiment}")
    print(f"AI PROVIDER: {ai.active_provider}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(generate_reel())
