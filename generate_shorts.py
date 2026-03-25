import os
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, TextClip

# --- PILLOW/MOVIEPY COMPATIBILITY ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# --- CONFIG ---
OUT = Path("output")
IMAGE_DIR = Path("public/image")
MUSIC_DIR = Path("public/music")
SW, SH = 1080, 1920
os.makedirs(OUT, exist_ok=True)

# --- DISNEY 3D EFFECT ---
def apply_3d_effect(base_img, emotion="thinking"):
    zeno_path = IMAGE_DIR / f"zeno_{emotion}.png"
    if not zeno_path.exists():
        return base_img
    
    zeno = Image.open(str(zeno_path)).convert("RGBA")
    target_w = int(SW * 0.85)
    w_ratio = target_w / float(zeno.size[0])
    target_h = int(float(zeno.size[1]) * float(w_ratio))
    zeno = zeno.resize((target_w, target_h), Image.LANCZOS)

    shadow_layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    zeno_mask = zeno.split()[3]
    shadow_pos = ((SW - zeno.width)//2 + 15, SH - zeno.height - 180 + 15)
    shadow_img = Image.new("RGBA", zeno.size, (0, 0, 0, 110))
    shadow_layer.paste(shadow_img, shadow_pos, zeno_mask)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=15))

    temp_bg = base_img.convert("RGBA")
    combined = Image.alpha_composite(temp_bg, shadow_layer)
    zeno_pos = ((SW - zeno.width)//2, SH - zeno.height - 200)
    combined.paste(zeno, zeno_pos, zeno)
    return combined.convert("RGB")

async def generate_content():
    print("🎬 Starting Master Generation...")
    
    # 1. TEXT & AUDIO (Fixing "Dar" pronunciation)
    display_text = "मार्केट नहीं आपका डर है। पेशेंस रखिए।"
    audio_script = "दोस्तों ट्रेडिंग में सबसे बड़ा दुश्मन मार्केट नहीं आपका ड र है। पेशेंस रखिए।"
    
    audio_path = OUT / "voice.mp3"
    await edge_tts.Communicate(audio_script, "hi-IN-SwaraNeural").save(str(audio_path))
    audio_clip = AudioFileClip(str(audio_path))

    # 2. FRAME BUILDER
    bg = Image.new("RGB", (SW, SH))
    draw = ImageDraw.Draw(bg)
    # Gradient
    for y in range(SH):
        r = int(5 + (15 - 5) * (y / SH))
        g = int(10 + (30 - 10) * (y / SH))
        b = int(25 + (70 - 25) * (y / SH))
        draw.line([(0, y), (SW, y)], fill=(r, g, b))
    
    final_frame_img = apply_3d_effect(bg, emotion="fear")
    frame_path = OUT / "final_frame.png"
    final_frame_img.save(frame_path)

    # 3. VIDEO ASSEMBLY (Fixing the Font Error)
    # Using 'DejaVu-Sans' because 'Arial' does not exist on Ubuntu
    try:
        txt = TextClip(display_text, fontsize=60, color='white', bg_color='black', 
                       method='caption', size=(900, None), font='DejaVu-Sans')
    except:
        txt = TextClip(display_text, fontsize=60, color='white', bg_color='black', 
                       method='caption', size=(900, None))

    video = ImageClip(str(frame_path)).set_duration(audio_clip.duration + 0.5)
    txt_clip = txt.set_position(('center', 1400)).set_duration(audio_clip.duration)
    
    final_video = CompositeVideoClip([video, txt_clip]).set_audio(audio_clip)
    final_video.write_videofile(str(OUT / "zeno_reel.mp4"), fps=30, codec="libx264", logger=None)

    print(f"\n✅ SUCCESS\nTelegram: t.me/ai360trading\nWeb: ai360trading.in\n")

if __name__ == "__main__":
    from moviepy.video.VideoClip import CompositeVideoClip
    asyncio.run(generate_content())
