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

# ─── Content Mode ─────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")
print(f"[MODE] generate_reel.py running in mode: {CONTENT_MODE.upper()}")

# --- CONFIGURATION & PATHS ---
OUT       = Path("output")
IMAGE_DIR = Path("public/image")
MUSIC_DIR = Path("public/music")
SW, SH    = 1080, 1920
FPS       = 30
IST       = pytz.timezone("Asia/Kolkata")
os.makedirs(OUT, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE     = (255, 255, 255)
YELLOW    = (255, 220, 80)

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

def generate_script():
    """Generate viral SEO-optimized Hinglish script via Groq."""
    client  = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
    today   = datetime.now(IST).strftime("%A, %d %B %Y")

    if CONTENT_MODE == "holiday":
        topic = f"special {HOLIDAY_NAME} message — why learning is better than trading on holidays."
    elif CONTENT_MODE == "weekend":
        topic = "life lesson on compounding, patience, or money mindset."
    else:
        topic = "trading psychology, risk management, or 'bhed chaal' (herd mentality) warning."

    prompt = f"""You are ZENO — a wise animated kid character. 
Create a 45-second viral reel script for {today} about: {topic}

Rules:
- Language: Hinglish (Natural Indian conversation)
- Target: Global traders (India, US, UK, Brazil)
- Style: Emotional, 10-year-old wisdom, very relatable.
- End with: "Follow ai360trading for more wisdom."

Respond ONLY with valid JSON:
{{
  "title": "4 WORD UPPERCASE TITLE",
  "audio_script": "80-100 words Hinglish speech",
  "display_text": "One powerful line for screen (max 10 words)",
  "emotion": "happy/sad/fear/angry/thinking/greed/celebrating",
  "sentiment": "positive/negative/motivated",
  "seo_description": "Viral description with emojis and CTA for Telegram t.me/ai360trading",
  "hashtags": "8 viral hashtags including #ai360trading #ZenoKiBaat"
}}"""

    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        print(f"⚠️ Groq error: {e}")
        return {"title": "BE DISCIPLINED", "audio_script": "Trading discipline hi sab kuch hai...", "display_text": "Discipline hi profit hai.", "emotion": "thinking", "hashtags": "#trading #discipline"}

def apply_zeno_disney_effect(base_img, emotion="thinking"):
    zeno_path = IMAGE_DIR / f"zeno_{emotion}.png"
    if not zeno_path.exists(): zeno_path = IMAGE_DIR / "zeno_thinking.png"
    if not zeno_path.exists(): return base_img

    zeno = Image.open(str(zeno_path)).convert("RGBA")
    target_w = int(SW * 0.85)
    w_ratio  = target_w / float(zeno.size[0])
    target_h = int(float(zeno.size[1]) * float(w_ratio))
    zeno     = zeno.resize((target_w, target_h), Image.LANCZOS)

    # Shadow logic (Manual work feel)
    shadow_layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    zeno_mask = zeno.split()[3]
    shadow_pos = ((SW - zeno.width) // 2 + 15, SH - zeno.height - 180 + 15)
    shadow_img = Image.new("RGBA", zeno.size, (0, 0, 0, 110))
    shadow_layer.paste(shadow_img, shadow_pos, zeno_mask)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=15))

    temp_bg = base_img.convert("RGBA")
    combined = Image.alpha_composite(temp_bg, shadow_layer)
    zeno_pos = ((SW - zeno.width) // 2, SH - zeno.height - 200)
    combined.paste(zeno, zeno_pos, zeno)
    return combined.convert("RGB")

def build_reel_frame(title_text, display_text, emotion="thinking"):
    img  = Image.new("RGB", (SW, SH))
    draw = ImageDraw.Draw(img, "RGBA")

    # Background Gradient
    for y in range(SH):
        r = int(5 + (15 - 5) * (y / SH))
        g = int(10 + (30 - 10) * (y / SH))
        b = int(25 + (70 - 25) * (y / SH))
        draw.line([(0, y), (SW, y)], fill=(r, g, b))

    img = apply_zeno_disney_effect(img, emotion)
    draw_text = ImageDraw.Draw(img)
    
    # Title Rendering (Double Line)
    font_title = get_font(FONT_BOLD, 85)
    words = title_text.split()
    mid = max(1, len(words) // 2)
    l1, l2 = " ".join(words[:mid]), " ".join(words[mid:])
    
    for line, offset in [(l1, 300), (l2, 405)]:
        if not line: continue
        draw_text.text((SW//2, offset), line, font=font_title, fill=WHITE, anchor="mm", stroke_width=2, stroke_fill=(0,0,0))

    # Caption Box (Viral Style)
    font_display = get_font(FONT_BOLD, 46)
    display_y = SH - 380
    draw_text.rectangle([(50, display_y - 40), (SW-50, display_y + 100)], fill=(0, 0, 0, 160))
    draw_text.text((SW // 2, display_y + 30), display_text, font=font_display, fill=YELLOW, anchor="mm")

    # Brand Footer
    font_brand = get_font(FONT_BOLD, 38)
    draw_text.text((SW // 2, SH - 200), "✨ AI360TRADING.IN", font=font_brand, fill=(255, 165, 0), anchor="mm")
    draw_text.text((SW // 2, SH - 140), "📱 t.me/ai360trading", font=font_brand, fill=(140, 180, 240), anchor="mm")

    path = OUT / "zeno_reel_frame.png"
    img.save(str(path))
    return path

async def generate_reel():
    script = generate_script()
    today = datetime.now().strftime("%Y%m%d")
    
    audio_path = OUT / "zeno_speech.mp3"
    await edge_tts.Communicate(script["audio_script"], "hi-IN-SwaraNeural").save(str(audio_path))
    
    frame_path = build_reel_frame(script["title"], script["display_text"], script["emotion"])
    voice_clip = AudioFileClip(str(audio_path))
    
    # Music integration
    bg_file = get_bg_music()
    audio = CompositeAudioClip([voice_clip, AudioFileClip(str(bg_file)).volumex(0.15).set_duration(voice_clip.duration)]) if bg_file else voice_clip

    video = ImageClip(str(frame_path)).set_duration(voice_clip.duration + 0.5).set_audio(audio)
    output_file = OUT / f"reel_{today}.mp4"
    video.write_videofile(str(output_file), fps=FPS, codec="libx264", audio_codec="aac", logger=None)

    # Viral SEO Export
    meta = {
        "title": f"ZENO Ki Baat: {script['title']}",
        "description": f"{script['seo_description']}\n\n{script['hashtags']}",
        "tags": script['hashtags']
    }
    (OUT / f"meta_{today}.json").write_text(json.dumps(meta, indent=2))
    print(f"✅ Reel Generated: {output_file}")

if __name__ == "__main__":
    asyncio.run(generate_reel())
