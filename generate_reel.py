import os, json, asyncio
from datetime import datetime
from pathlib import Path
import pytz
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip, 
    concatenate_audioclips
)
from groq import Groq

# ─── CONFIG ──────────────────────────────────────────────────────────────────
OUT       = Path("output")
MUSIC_DIR = Path("public/music")
SW, SH    = 1080, 1920   # 9:16 Vertical
FPS       = 30
os.makedirs(OUT, exist_ok=True)

# ─── FONTS & COLORS ──────────────────────────────────────────────────────────
WHITE       = (255, 255, 255)
SOFT_BLUE   = (100, 180, 255)
FONT_BOLD   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def get_font(path, size):
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()

# ─── DISNEY 3D EFFECT ENGINE ─────────────────────────────────────────────────
def apply_zeno_disney_effect(base_img, emotion="thinking"):
    """
    Renders Zeno with depth, scaling, and a 'Human Touch' shadow.
    Makes him look like he's popping out of the screen.
    """
    zeno_path = f"public/zeno_{emotion}.png"
    if not os.path.exists(zeno_path):
        print(f"⚠️ Zeno image missing: {zeno_path}")
        return base_img

    zeno = Image.open(zeno_path).convert("RGBA")

    # 1. HERO SCALING: Make Zeno 85% of screen width for 'Disney' impact
    target_w = int(SW * 0.85)
    w_ratio = target_w / float(zeno.size[0])
    target_h = int(float(zeno.size[1]) * float(w_ratio))
    zeno = zeno.resize((target_w, target_h), Image.LANCZOS)

    # 2. 3D DEPTH SHADOW: Create a blurred silhouette layer
    # This creates the 'Human Touch' by simulating light depth
    shadow_layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    zeno_mask = zeno.split()[3] # Alpha channel
    
    # Position shadow slightly down and to the right
    shadow_offset = (15, 15) 
    shadow_pos = ((SW - zeno.width)//2 + shadow_offset[0], SH - zeno.height - 180 + shadow_offset[1])
    
    # Draw soft shadow
    shadow_img = Image.new("RGBA", zeno.size, (0, 0, 0, 110)) # Soft black
    shadow_layer.paste(shadow_img, shadow_pos, zeno_mask)
    
    # Blur the shadow for a cinematic feel
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=15))

    # 3. COMPOSITE: Layer the background, then shadow, then Zeno
    temp_bg = base_img.convert("RGBA")
    combined = Image.alpha_composite(temp_bg, shadow_layer)
    
    # Paste the 'Real' Zeno on top
    zeno_pos = ((SW - zeno.width)//2, SH - zeno.height - 200)
    combined.paste(zeno, zeno_pos, zeno)

    return combined.convert("RGB")

# ─── REEL FRAME BUILDER ─────────────────────────────────────────────────────
def build_reel_frame(title_text, emotion="thinking"):
    """Creates a high-end cinematic background for the Zeno Reel."""
    # Create a Deep Blue Cinematic Gradient
    img = Image.new("RGB", (SW, SH))
    draw = ImageDraw.Draw(img, "RGBA")
    
    for y in range(SH):
        # Dark top to slightly lighter bottom
        top_color = (5, 10, 25)
        bot_color = (15, 30, 70)
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * (y / SH))
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * (y / SH))
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * (y / SH))
        draw.line([(0, y), (SW, y)], fill=(r, g, b))

    # Draw Glow behind the text area
    draw.ellipse([100, 100, SW-100, 600], fill=(60, 140, 255, 30))

    # Add the 3D Zeno
    img = apply_zeno_disney_effect(img, emotion)
    
    # Render the Teaching Title (Hinglish/English mix)
    draw_draw = ImageDraw.Draw(img)
    font_title = get_font(FONT_BOLD, 85)
    
    # Text Outline for readability
    text_y = 350
    words = title_text.split()
    line1 = " ".join(words[:len(words)//2])
    line2 = " ".join(words[len(words)//2:])
    
    for line, offset in [(line1, 0), (line2, 100)]:
        # Outline
        for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
            draw_draw.text((SW//2 + dx, text_y + offset + dy), line, font=font_title, fill=(0,0,0), anchor="mm")
        # Main Text
        draw_draw.text((SW//2, text_y + offset), line, font=font_title, fill=WHITE, anchor="mm")

    path = OUT / f"reel_frame_{datetime.now().strftime('%M%S')}.png"
    img.save(path)
    return path

# ─── MAIN REEL GENERATOR ────────────────────────────────────────────────────
async def generate_reel():
    print("🎬 Starting 3D Zeno Reel Generation...")
    
    # 1. SCRIPT (Evergreen Wisdom)
    # Voice: hi-IN-SwaraNeural (Gentle, Wise, for Beginners)
    script = "Dosto, trading mein sabse bada dushman market nahi, aapka dar hai. Patience rakhiye, logic par focus kijiye."
    title  = "CONTROL YOUR EMOTIONS"
    
    # 2. AUDIO (Zeno Voice + Low Music)
    audio_path = OUT / "zeno_speech.mp3"
    print("🎙️ Generating Swara's Voice...")
    await edge_tts.Communicate(script, "hi-IN-SwaraNeural", rate="+0%").save(str(audio_path))
    
    # 3. FRAME (The 3D Visual)
    frame_path = build_reel_frame(title, emotion="happy")
    
    # 4. VIDEO ASSEMBLY
    print("🎞️ Rendering Final 3D Reel...")
    voice_clip = AudioFileClip(str(audio_path))
    duration = voice_clip.duration + 1.0
    
    video = (ImageClip(str(frame_path))
             .set_duration(duration)
             .set_audio(voice_clip)
             .write_videofile(str(OUT / "final_zeno_reel.mp4"), fps=FPS, codec="libx264", audio_codec="aac", logger=None))

    print(f"✅ Reel Complete: output/final_zeno_reel.mp4")

if __name__ == "__main__":
    asyncio.run(generate_reel())
