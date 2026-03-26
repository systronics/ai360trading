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
from groq import Groq

# --- CONFIGURATION & PATHS ---
OUT       = Path("output")
IMAGE_DIR = Path("public/image")
MUSIC_DIR = Path("public/music")
SW, SH    = 1080, 1920   # 9:16 Vertical
FPS       = 30
IST       = pytz.timezone("Asia/Kolkata")
os.makedirs(OUT, exist_ok=True)

# --- FONTS ---
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE     = (255, 255, 255)

def get_font(path, size):
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()

# --- WEEKEND DETECTION ---
def is_weekend():
    return datetime.now().weekday() >= 5

# --- BACKGROUND MUSIC (day-based rotation) ---
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

# --- GROQ SCRIPT GENERATION ---
def generate_script():
    """Generate fresh daily Hinglish script via Groq."""
    client  = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
    weekend = is_weekend()
    today   = datetime.now(IST).strftime("%A, %d %B %Y")

    if weekend:
        topic = "emotional life lesson about patience, discipline or money mindset — no market data"
    else:
        topic = "stock market trading wisdom, psychology, or risk management lesson for Indian traders"

    prompt = f"""You are ZENO — a wise animated kid character teaching trading wisdom in Hinglish to Indian traders.

Today is {today}. Create a 45-60 second reel script on: {topic}

Rules:
- Hinglish only (natural Hindi + English mix)
- Simple enough for a 10-year-old to understand
- Emotional, relatable, human touch
- One clear lesson only
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

    print("🤖 Generating daily script via Groq...")
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.85,
            max_tokens=500
        )
        data = json.loads(resp.choices[0].message.content)
        print(f"✅ Script ready — emotion: {data.get('emotion')} | title: {data.get('title')}")
        return data
    except Exception as e:
        print(f"⚠️ Groq error: {e} — using fallback script")
        return {
            "title":        "CONTROL YOUR EMOTIONS",
            "audio_script": "दोस्तों ट्रेडिंग में सबसे बड़ा दुश्मन मार्केट नहीं आपका ड र है। पेशेंस रखिए। हर loss एक lesson है। Discipline रखो, success जरूर मिलेगी।",
            "display_text": "मार्केट नहीं आपका डर है। पेशेंस रखिए।",
            "emotion":      "fear",
            "sentiment":    "fearful",
            "description":  "ZENO ki baat: Trading mein patience aur discipline sabse zaroori hai. Apne emotions ko control karo."
        }

# --- DISNEY 3D EFFECT ENGINE ---
def apply_zeno_disney_effect(base_img, emotion="thinking"):
    """Renders Zeno with depth and a soft cinematic shadow."""
    zeno_path = IMAGE_DIR / f"zeno_{emotion}.png"
    if not zeno_path.exists():
        print(f"⚠️ Zeno image missing: {zeno_path} — using fallback")
        zeno_path = IMAGE_DIR / "zeno_thinking.png"
        if not zeno_path.exists():
            return base_img

    zeno = Image.open(str(zeno_path)).convert("RGBA")

    # 1. HERO SCALING (85% width for Disney impact)
    target_w = int(SW * 0.85)
    w_ratio  = target_w / float(zeno.size[0])
    target_h = int(float(zeno.size[1]) * float(w_ratio))
    zeno     = zeno.resize((target_w, target_h), Image.LANCZOS)

    # 2. 3D DEPTH SHADOW (The 'Human Touch' effect)
    shadow_layer  = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    zeno_mask     = zeno.split()[3]
    shadow_offset = (15, 15)
    shadow_pos    = (
        (SW - zeno.width) // 2 + shadow_offset[0],
        SH - zeno.height - 180 + shadow_offset[1]
    )
    shadow_img = Image.new("RGBA", zeno.size, (0, 0, 0, 110))
    shadow_layer.paste(shadow_img, shadow_pos, zeno_mask)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=15))

    # 3. COMPOSITE
    temp_bg  = base_img.convert("RGBA")
    combined = Image.alpha_composite(temp_bg, shadow_layer)
    zeno_pos = ((SW - zeno.width) // 2, SH - zeno.height - 200)
    combined.paste(zeno, zeno_pos, zeno)

    return combined.convert("RGB")

# --- REEL FRAME BUILDER ---
def build_reel_frame(title_text, display_text, emotion="thinking"):
    """Creates the cinematic background with Zeno + title + display text."""
    img  = Image.new("RGB", (SW, SH))
    draw = ImageDraw.Draw(img, "RGBA")

    # Cinematic Gradient (Dark blue depth)
    for y in range(SH):
        top_color, bot_color = (5, 10, 25), (15, 30, 70)
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * (y / SH))
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * (y / SH))
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * (y / SH))
        draw.line([(0, y), (SW, y)], fill=(r, g, b))

    # Text Area Glow
    draw.ellipse([100, 100, SW - 100, 600], fill=(60, 140, 255, 30))

    # Apply 3D Disney Zeno
    img = apply_zeno_disney_effect(img, emotion)

    # --- Title text (top, English caps) ---
    draw_text  = ImageDraw.Draw(img)
    font_title = get_font(FONT_BOLD, 85)
    text_y     = 300
    words      = title_text.split()
    mid        = max(1, len(words) // 2)
    line1      = " ".join(words[:mid])
    line2      = " ".join(words[mid:])

    for line, offset in [(line1, 0), (line2, 105)]:
        if not line:
            continue
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            draw_text.text((SW // 2 + dx, text_y + offset + dy),
                           line, font=font_title, fill=(0, 0, 0), anchor="mm")
        draw_text.text((SW // 2, text_y + offset),
                       line, font=font_title, fill=WHITE, anchor="mm")

    # --- Display text (Hinglish/Hindi line at bottom above CTA) ---
    font_display = get_font(FONT_BOLD, 44)
    display_y    = SH - 340
    # Semi-transparent bar behind display text
    draw_text.rectangle([(0, display_y - 30), (SW, display_y + 90)],
                         fill=(0, 0, 0, 140))
    # Wrap display text
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

    # --- Brand + CTA ---
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

# --- MAIN REEL GENERATOR ---
async def generate_reel():
    print("🎬 Starting 3D Zeno Reel Generation...")
    today = datetime.now().strftime("%Y%m%d")

    # 1. Generate fresh daily script via Groq
    script = generate_script()

    title        = script.get("title",        "TRADING WISDOM")
    audio_script = script.get("audio_script", "Trading mein patience sabse zaroori hai.")
    display_text = script.get("display_text", "Patience hi success hai।")
    emotion      = script.get("emotion",      "thinking")
    sentiment    = script.get("sentiment",    "neutral")
    description  = script.get("description", "Daily trading wisdom by ZENO. Follow ai360trading.")

    # 2. Audio generation
    audio_path = OUT / "zeno_speech.mp3"
    print("🎙️ Generating Voice...")
    await edge_tts.Communicate(
        audio_script, "hi-IN-SwaraNeural", rate="+0%"
    ).save(str(audio_path))

    # 3. Frame generation
    frame_path = build_reel_frame(title, display_text, emotion)

    # 4. Video assembly
    print("🎞️ Rendering Final 3D Reel...")
    voice_clip = AudioFileClip(str(audio_path))

    # Background music — day-based rotation
    music_file = get_bg_music()
    if music_file:
        try:
            bg_m       = AudioFileClip(str(music_file)).volumex(0.12).set_duration(voice_clip.duration)
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

    # Save as final_zeno_reel.mp4 — upload_youtube finds this via *.mp4 fallback
    output_file = OUT / "final_zeno_reel.mp4"
    video.write_videofile(
        str(output_file), fps=FPS,
        codec="libx264", audio_codec="aac", logger=None
    )

    # FIX 1: Also save as reel_{today}.mp4 — upload_facebook glob reel_*.mp4
    reel_dated = OUT / f"reel_{today}.mp4"
    shutil.copy2(str(output_file), str(reel_dated))
    print(f"✅ Video saved: {output_file.name} + {reel_dated.name}")

    # FIX 2: Save meta_{today}.json — upload_facebook + upload_instagram need this
    meta = {
        "title":            f"ZENO Ki Baat - {title}",
        "description":      description + " 🔗 t.me/ai360trading | ai360trading.in",
        "sentiment":        sentiment,
        "hashtags":         "#ZenoKiBaat #ai360trading #StockMarketIndia #TradingWisdom #Hinglish #FinancialLiteracy",
        "public_video_url": ""
    }
    meta_path = OUT / f"meta_{today}.json"
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"✅ Meta saved: {meta_path.name}")

    # --- LOGS ---
    print("\n" + "=" * 50)
    print(f"✅ REEL SUCCESS: {output_file}")
    print(f"TITLE: ZENO Ki Baat - {title}")
    print(f"DESC: {display_text}")
    print(f"EMOTION: {emotion} | SENTIMENT: {sentiment}")
    print(f"🔗 Telegram: t.me/ai360trading")
    print(f"🌐 Web: https://ai360trading.in")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    asyncio.run(generate_reel())
