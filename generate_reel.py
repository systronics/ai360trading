import os
import json
import asyncio
import datetime
import random
import requests
import numpy as np
from pathlib import Path
from moviepy.editor import *
import PIL.Image

# 🟢 HD FIX: Ensuring the sharpest possible image scaling
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# ─── CONFIG & PATHS ──────────────────────────────────────────────────────────
OUTPUT_DIR = Path("output")
ASSETS_DIR = Path("public/image")
MUSIC_DIR = Path("public/music")
OUTPUT_DIR.mkdir(exist_ok=True)

# ─── STEP 1: AI SCRIPT GENERATOR (HUMAN-STYLE) ───────────────────────────────
async def get_groq_script():
    """Fetches a fresh, kid-friendly trading tip from Groq AI."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Dost, trading mein sabr hi sabse badi kamai hai. Jaldbazi mat karo."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = (
        "Write a 1-sentence trading wisdom tip in Hinglish (Hindi + English). "
        "Character: Zeno, a smart and friendly 10-year-old boy. "
        "Tone: Simple, professional, and very human. "
        "Strictly 1 sentence only. No hashtags or emojis in the text."
    )

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8 # Higher temperature for more 'human' variety
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        script = result['choices'][0]['message']['content'].strip().replace('"', '')
        print(f"🤖 Zeno's Script: {script}")
        return script
    except Exception as e:
        print(f"⚠️ Groq Error: {e}. Using fallback.")
        return "Market mein discipline hi aapko ek safal trader banayega."

# ─── STEP 2: VOICE GENERATION (KID VOICE) ────────────────────────────────────
async def generate_voice(script: str, output_path: Path):
    import edge_tts
    # Swara (Female) provides the perfect high-pitched 'Smart Kid' energy
    communicate = edge_tts.Communicate(script, "hi-IN-SwaraNeural", rate="+10%", pitch="+5Hz")
    await communicate.save(str(output_path))
    print(f"✅ Kid Voice Generated: {output_path}")

# ─── STEP 3: HD VIDEO ASSEMBLY (HD + CLEAN LOGS) ─────────────────────────────
def create_video(voice_path: Path, script: str):
    today_folder = datetime.datetime.now().strftime("%Y%m%d")
    today_display = datetime.datetime.now().strftime("%d %b %Y")
    video_path = OUTPUT_DIR / f"reel_{today_folder}.mp4"
    meta_path = OUTPUT_DIR / f"meta_{today_folder}.json"

    voice_audio = AudioFileClip(str(voice_path))
    final_audio = voice_audio

    # 🎵 Studio-Quality Music Mix
    valid_music = ["bgmusic1.mp3", "bgmusic2.mp3", "bgmusic3.mp3"]
    music_files = [MUSIC_DIR / m for m in valid_music if (MUSIC_DIR / m).exists()]
    if music_files:
        try:
            bg_file = random.choice(music_files)
            bg_music = AudioFileClip(str(bg_file)).volumex(0.12).set_duration(voice_audio.duration).audio_fadeout(2)
            final_audio = CompositeAudioClip([voice_audio, bg_music])
        except: pass

    # 🖼️ Full HD Vertical (1080x1920)
    img_path = ASSETS_DIR / "zeno_happy.png"
    if not img_path.exists():
        png_files = list(ASSETS_DIR.glob("*.png"))
        img_path = png_files[0] if png_files else None

    if not img_path:
        print("❌ Error: No images found!")
        return

    image_clip = ImageClip(str(img_path)).set_duration(voice_audio.duration)
    
    # Fill Frame (9:16)
    w, h = image_clip.size
    if w/h > 1080/1920:
        image_clip = image_clip.resize(height=1920)
    else:
        image_clip = image_clip.resize(width=1080)
        
    video = image_clip.crop(x_center=image_clip.w/2, y_center=image_clip.h/2, width=1080, height=1920)
    
    # 🎬 Human Motion (Cinematic Zoom)
    video = video.fx(vfx.resize, lambda t: 1 + 0.05 * (t / voice_audio.duration))
    video = video.set_audio(final_audio)

    # 🏷️ TEXT OVERLAYS
    # Main Title (Top)
    title = TextClip(
        "ZENO KI BAAT ✨",
        fontsize=85, color='yellow', font='Arial-Bold',
        stroke_color='black', stroke_width=3, method='caption',
        size=(950, None), align='center'
    ).set_position(('center', 220)).set_duration(video.duration)

    # Branding Watermark (Bottom)
    branding = TextClip(
        "@ai360trading.in",
        fontsize=45, color='white', font='Arial',
        opacity=0.5
    ).set_position(('center', 1780)).set_duration(video.duration)

    # 🚀 HD EXPORT (CLEAN LOGS)
    final_video = CompositeVideoClip([video, title, branding], size=(1080, 1920)).set_fps(24)
    final_video.write_videofile(
        str(video_path), 
        codec="libx264", 
        audio_codec="aac", 
        fps=24, 
        bitrate="5000k",
        preset="slow",
        logger=None # ⬅️ Hides the long progress logs for cleaner sharing
    )

    # 📝 GENERATE SEO METADATA
    metadata = {
        "title": f"ZENO ki Baat: {today_display} #Shorts",
        "description": f"{script}\n\nDaily Trading Wisdom from Zeno.\n🌐 Website: https://ai360trading.in\n📢 Telegram: t.me/ai360trading\n\n#ai360trading #ZenoKiBaat #TradingWisdom #Hinglish #MarketPsychology",
        "video_path": str(video_path)
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f)
    print(f"✅ Reel Published locally: {video_path}")

# ─── EXECUTION ───────────────────────────────────────────────────────────────
async def main():
    voice_file = OUTPUT_DIR / "voice.mp3"
    script = await get_groq_script()
    await generate_voice(script, voice_file)
    create_video(voice_file, script)

if __name__ == "__main__":
    asyncio.run(main())
