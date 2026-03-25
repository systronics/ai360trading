import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
import pytz
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip
)

# --- CONFIGURATION & PATHS ---
OUT = Path("output")
# FIXED: Points to your actual folder structure seen in your screenshots
IMAGE_DIR = Path("public/image") 
MUSIC_DIR = Path("public/music")
SW, SH = 1080, 1920  # 9:16 Vertical
FPS = 30
os.makedirs(OUT, exist_ok=True)

# --- FONTS ---
# Standard Linux paths for GitHub Actions runners
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE = (255, 255, 255)

def get_font(path, size):
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()

# --- DISNEY 3D EFFECT ENGINE ---
def apply_zeno_disney_effect(base_img, emotion="thinking"):
    """
    Renders Zeno with depth and a soft cinematic shadow.
    """
    # FIXED: Uses your actual subfolder and the 'zeno_' prefix
    zeno_path = IMAGE_DIR / f"zeno_{emotion}.png"
    if not zeno_path.exists():
        print(f"⚠️ Zeno image missing: {zeno_path}")
        # Fallback to a generic zeno if the specific emotion is missing
        zeno_path = IMAGE_DIR / "zeno_thinking.png"
        if not zeno_path.exists(): return base_img

    zeno = Image.open(str(zeno_path)).convert("RGBA")

    # 1. HERO SCALING (85% width for Disney impact)
    target_w = int(SW * 0.85)
    w_ratio = target_w / float(zeno.size[0])
    target_h = int(float(zeno.size[1]) * float(w_ratio))
    zeno = zeno.resize((target_w, target_h), Image.LANCZOS)

    # 2. 3D DEPTH SHADOW (The 'Human Touch' effect)
    shadow_layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    zeno_mask = zeno.split()[3] 
    
    shadow_offset = (15, 15) 
    shadow_pos = ((SW - zeno.width)//2 + shadow_offset[0], SH - zeno.height - 180 + shadow_offset[1])
    
    shadow_img = Image.new("RGBA", zeno.size, (0, 0, 0, 110)) 
    shadow_layer.paste(shadow_img, shadow_pos, zeno_mask)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=15))

    # 3. COMPOSITE
    temp_bg = base_img.convert("RGBA")
    combined = Image.alpha_composite(temp_bg, shadow_layer)
    
    zeno_pos = ((SW - zeno.width)//2, SH - zeno.height - 200)
    combined.paste(zeno, zeno_pos, zeno)

    return combined.convert("RGB")

# --- REEL FRAME BUILDER ---
def build_reel_frame(title_text, emotion="thinking"):
    """Creates the cinematic background with Zeno."""
    img = Image.new("RGB", (SW, SH))
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Cinematic Gradient (Dark blue depth)
    for y in range(SH):
        top_color, bot_color = (5, 10, 25), (15, 30, 70)
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * (y / SH))
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * (y / SH))
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * (y / SH))
        draw.line([(0, y), (SW, y)], fill=(r, g, b))

    # Text Area Glow
    draw.ellipse([100, 100, SW-100, 600], fill=(60, 140, 255, 30))

    # Apply your 3D Disney logic
    img = apply_zeno_disney_effect(img, emotion)
    
    # Render Title Text
    draw_text = ImageDraw.Draw(img)
    font_title = get_font(FONT_BOLD, 85)
    
    text_y = 350
    words = title_text.split()
    line1 = " ".join(words[:len(words)//2])
    line2 = " ".join(words[len(words)//2:])
    
    for line, offset in [(line1, 0), (line2, 100)]:
        # Black Outline
        for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
            draw_text.text((SW//2 + dx, text_y + offset + dy), line, font=font_title, fill=(0,0,0), anchor="mm")
        # Main Text
        draw_text.text((SW//2, text_y + offset), line, font=font_title, fill=WHITE, anchor="mm")

    path = OUT / "zeno_reel_frame.png"
    img.save(path)
    return path

# --- MAIN REEL GENERATOR ---
async def generate_reel():
    print("🎬 Starting 3D Zeno Reel Generation...")
    
    # 1. SCRIPT FIX: Hindi Script + Space Trick for "Dar" (Fear) pronunciation
    display_text = "मार्केट नहीं आपका डर है। पेशेंस रखिए।"
    audio_script = "दोस्तों ट्रेडिंग में सबसे बड़ा दुश्मन मार्केट नहीं आपका ड र है। पेशेंस रखिए।"
    title = "CONTROL YOUR EMOTIONS"
    
    # 2. AUDIO GENERATION
    audio_path = OUT / "zeno_speech.mp3"
    print("🎙️ Generating Voice...")
    await edge_tts.Communicate(audio_script, "hi-IN-SwaraNeural", rate="+0%").save(str(audio_path))
    
    # 3. FRAME GENERATION (Emotion set to 'fear' to match the script)
    frame_path = build_reel_frame(title, emotion="fear")
    
    # 4. VIDEO ASSEMBLY
    print("🎞️ Rendering Final 3D Reel...")
    voice_clip = AudioFileClip(str(audio_path))
    
    # Optional Background Music
    music_file = MUSIC_DIR / "bgmusic2.mp3"
    if music_file.exists():
        bg_m = AudioFileClip(str(music_file)).volumex(0.12).set_duration(voice_clip.duration)
        final_audio = CompositeAudioClip([voice_clip, bg_m])
    else:
        final_audio = voice_clip

    video = (ImageClip(str(frame_path))
             .set_duration(voice_clip.duration + 0.5)
             .set_audio(final_audio))
    
    output_file = OUT / "final_zeno_reel.mp4"
    video.write_videofile(str(output_file), fps=FPS, codec="libx264", audio_codec="aac", logger=None)

    # --- LOGS FOR YOUR CHANNEL ---
    print("\n" + "="*50)
    print(f"✅ REEL SUCCESS: {output_file}")
    print(f"TITLE: ZENO Ki Baat - {title}")
    print(f"DESC: {display_text}\n\n🔗 Telegram: t.me/ai360trading\n🌐 Web: https://ai360trading.in")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(generate_reel())
