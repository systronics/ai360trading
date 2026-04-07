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
from ai_client import ai          # ✅ FIXED: use ai_client fallback chain
from human_touch import ht, seo   # ✅ FIXED: anti-AI-penalty layer

# ─── Content Mode ─────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")
print(f"[MODE] generate_reel.py running in mode: {CONTENT_MODE.upper()}")

# --- CONFIGURATION & PATHS ---
OUT       = Path("output")
IMAGE_DIR = Path("public/image")
MUSIC_DIR = Path("public/music")
SW, SH    = 1080, 1920      # ✅ 9:16 portrait — never change
FPS       = 30
MAX_AUDIO_SECS = 58         # ✅ FIXED: trim to 58s — YouTube Shorts limit is 60s
IST       = pytz.timezone("Asia/Kolkata")

os.makedirs(OUT, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
WHITE     = (255, 255, 255)

def get_font(path, size):
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def get_bg_music():
    day = datetime.now().weekday()
    music_map = {0:"bgmusic1.mp3",1:"bgmusic2.mp3",2:"bgmusic3.mp3",
                 3:"bgmusic1.mp3",4:"bgmusic2.mp3",5:"bgmusic3.mp3",6:"bgmusic1.mp3"}
    f = MUSIC_DIR / music_map[day]
    if f.exists():
        return f
    for f in MUSIC_DIR.glob("*.mp3"):
        return f
    return None

def generate_script():
    """Generate Hinglish ZENO reel script via ai_client (full fallback chain)."""
    today = datetime.now(IST).strftime("%A, %d %B %Y")

    # Get rotating hook from human_touch
    hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")

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

Opening hook: "{hook}"

Rules:
- Hinglish only (natural Hindi + English mix)
- Simple enough for a 10-year-old to understand
- Emotional, relatable, human touch
- One clear lesson only
- STRICT word limit: audio_script must be 80-100 words MAX (at 140 wpm = 60-70 seconds before trimming to 58s)
- End with strong message

Respond ONLY with valid JSON, no markdown:
{{
  "title": "SHORT ENGLISH TITLE MAX 4 WORDS IN CAPS (for display on screen)",
  "audio_script": "full spoken Hinglish script 80-100 words — what ZENO will say aloud",
  "display_text": "one powerful Hindi/Hinglish line shown on screen (max 12 words)",
  "emotion": "one of: happy, sad, fear, angry, thinking, greed, celebrating",
  "sentiment": "one of: positive, negative, fearful, motivated, greedy, angry, neutral",
  "description": "2 sentence English/Hinglish description for YouTube and Instagram"
}}"""

    print("🤖 Generating ZENO reel script via ai_client...")
    data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")

    if data and data.get("audio_script"):
        # ✅ Humanize the output — strip robotic patterns
        data["audio_script"] = ht.humanize(data["audio_script"], lang="hi")
        print(f"✅ Script ready — emotion: {data.get('emotion')} | title: {data.get('title')}")
        return data
    else:
        print("⚠️ AI failed — using fallback script")
        return {
            "title": "CONTROL YOUR EMOTIONS",
            "audio_script": "दोस्तों ट्रेडिंग में सबसे बड़ा दुश्मन मार्केट नहीं आपका डर है। पेशेंस रखिए। हर loss एक lesson है। Discipline रखो, success जरूर मिलेगी। ZENO ke saath seekhte raho, ai360trading pe aate raho.",
            "display_text": "मार्केट नहीं, आपका डर है दुश्मन।",
            "emotion": "fear",
            "sentiment": "fearful",
            "description": "ZENO ki baat: Trading mein patience aur discipline sabse zaroori hai. Apne emotions ko control karo."
        }

def apply_zeno_disney_effect(base_img, emotion="thinking"):
    zeno_path = IMAGE_DIR / f"zeno_{emotion}.png"
    if not zeno_path.exists():
        print(f"⚠️ Zeno image missing: {zeno_path} — using fallback")
        zeno_path = IMAGE_DIR / "zeno_thinking.png"
    if not zeno_path.exists():
        return base_img

    zeno = Image.open(str(zeno_path)).convert("RGBA")
    target_w = int(SW * 0.85)
    w_ratio  = target_w / float(zeno.size[0])
    target_h = int(float(zeno.size[1]) * float(w_ratio))
    zeno     = zeno.resize((target_w, target_h), Image.LANCZOS)

    shadow_layer  = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    zeno_mask     = zeno.split()[3]
    shadow_offset = (15, 15)
    zeno_x = (SW - zeno.width) // 2
    zeno_y = SH - zeno.height - 60
    shadow_pos = (zeno_x + shadow_offset[0], zeno_y + shadow_offset[1])

    shadow = Image.new("RGBA", zeno.size, (0, 0, 0, 100))
    shadow_layer.paste(shadow, shadow_pos, zeno_mask)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=8))

    result = base_img.convert("RGBA")
    result = Image.alpha_composite(result, shadow_layer)
    result.paste(zeno, (zeno_x, zeno_y), zeno)
    return result.convert("RGB")

def build_frame(script):
    emotion   = script.get("emotion", "thinking")
    sentiment = script.get("sentiment", "neutral")

    color_map = {
        "positive":  {"top": (5, 20, 60),    "bot": (10, 60, 120), "accent": (80, 200, 120)},
        "motivated": {"top": (10, 30, 10),    "bot": (20, 80, 30),  "accent": (100, 220, 80)},
        "fearful":   {"top": (60, 10, 10),    "bot": (120, 20, 20), "accent": (255, 80, 60)},
        "greedy":    {"top": (60, 50, 5),     "bot": (120, 100, 10),"accent": (255, 200, 40)},
        "negative":  {"top": (40, 10, 50),    "bot": (80, 20, 100), "accent": (200, 80, 220)},
        "angry":     {"top": (80, 5, 5),      "bot": (160, 10, 10), "accent": (255, 60, 40)},
        "neutral":   {"top": (10, 20, 50),    "bot": (20, 40, 90),  "accent": (80, 160, 255)},
    }
    colors = color_map.get(sentiment, color_map["neutral"])

    img = Image.new("RGB", (SW, SH))
    px  = img.load()
    for y in range(SH):
        t = y / SH
        c = tuple(int(colors["top"][i] + (colors["bot"][i] - colors["top"][i]) * t) for i in range(3))
        for x in range(SW):
            px[x, y] = c

    img  = apply_zeno_disney_effect(img, emotion)
    draw = ImageDraw.Draw(img, "RGBA")

    # Top bar
    draw.rectangle([(0, 0), (SW, 8)], fill=colors["accent"])

    # Brand watermark
    draw.text((SW // 2, 45), "ai360trading.in",
              fill=(255, 255, 255, 160), font=get_font(FONT_REG, 32), anchor="mm")

    # Title
    title = script.get("title", "TRADING WISDOM")
    draw.text((SW // 2, 130), title,
              fill=colors["accent"], font=get_font(FONT_BOLD, 58), anchor="mm")

    # Display text box
    display = script.get("display_text", "")
    if display:
        box_y = int(SH * 0.62)
        draw.rectangle([(30, box_y - 10), (SW - 30, box_y + 100)], fill=(0, 0, 0, 160))
        import textwrap
        lines = textwrap.wrap(display, width=22)
        ty = box_y + 15
        for line in lines[:3]:
            draw.text((SW // 2, ty), line, fill=WHITE,
                      font=get_font(FONT_BOLD, 52), anchor="mm")
            ty += 62

    # Telegram CTA — bottom (above the YouTube subscribe overlay zone)
    draw.rectangle([(0, SH - 140), (SW, SH - 10)], fill=(0, 0, 0, 180))
    draw.text((SW // 2, SH - 95), "📱 Join: t.me/ai360trading",
              fill=(255, 220, 60), font=get_font(FONT_BOLD, 36), anchor="mm")
    draw.text((SW // 2, SH - 45), "🌐 ai360trading.in",
              fill=(200, 220, 255), font=get_font(FONT_REG, 30), anchor="mm")

    draw.rectangle([(0, SH - 8), (SW, SH)], fill=colors["accent"])
    return img

async def generate_reel():
    today  = datetime.now(IST).strftime("%Y%m%d")
    script = generate_script()

    # Build frame
    frame_path = OUT / f"reel_frame_{today}.png"
    frame      = build_frame(script)
    frame.save(str(frame_path), quality=95)
    print(f"✅ Reel frame saved: {frame_path}")

    # Generate TTS voice with human_touch speed variation
    audio_path = OUT / f"reel_audio_{today}.mp3"
    tts_speed  = ht.get_tts_speed()
    rate_pct   = int((tts_speed - 1.0) * 100)
    rate_str   = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
    await edge_tts.Communicate(
        script["audio_script"], "hi-IN-SwaraNeural", rate=rate_str
    ).save(str(audio_path))
    print(f"✅ TTS audio saved: {audio_path}")

    # ✅ FIXED: Check and trim audio if over 58 seconds
    voice_clip = AudioFileClip(str(audio_path))
    print(f"⏱️ Audio duration: {voice_clip.duration:.1f}s")
    if voice_clip.duration > MAX_AUDIO_SECS:
        print(f"⚠️ Audio too long ({voice_clip.duration:.1f}s) — trimming to {MAX_AUDIO_SECS}s")
        voice_clip = voice_clip.subclip(0, MAX_AUDIO_SECS)

    duration = voice_clip.duration + 0.5  # 0.5s tail buffer

    # Mix with background music
    bg_path = get_bg_music()
    if bg_path:
        try:
            from moviepy.editor import concatenate_audioclips
            bg = AudioFileClip(str(bg_path))
            if bg.duration < duration:
                loops = int(duration / bg.duration) + 1
                bg = concatenate_audioclips([bg] * loops)
            bg    = bg.subclip(0, duration).volumex(0.08)
            audio = CompositeAudioClip([voice_clip, bg])
        except Exception as e:
            print(f"⚠️ Music error: {e}")
            audio = voice_clip
    else:
        audio = voice_clip

    # Render video
    video_path = OUT / f"reel_{today}.mp4"
    clip       = ImageClip(str(frame_path)).set_duration(duration).set_audio(audio)
    clip.write_videofile(
        str(video_path), fps=FPS, codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(OUT / "temp_reel_audio.aac"),
        remove_temp=True, logger=None
    )
    print(f"✅ Reel video: {video_path} ({duration:.1f}s)")

    # ✅ SEO tags from human_touch
    tags = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")

    # Save metadata
    meta = {
        "title":            script.get("title", "ZENO Trading Wisdom"),
        "audio_script":     script.get("audio_script", ""),
        "description":      script.get("description", ""),
        "emotion":          script.get("emotion", "thinking"),
        "sentiment":        script.get("sentiment", "neutral"),
        "tags":             tags,
        "video_path":       str(video_path),
        "content_mode":     CONTENT_MODE,
        "target_countries": ["India", "USA", "UK", "Brazil", "UAE", "Canada", "Australia"],
        "date":             today
    }
    meta_path = OUT / f"meta_{today}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Meta saved: {meta_path}")
    return meta

if __name__ == "__main__":
    asyncio.run(generate_reel())
