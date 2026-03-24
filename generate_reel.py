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

# 🟢 HD FIX: Ensuring sharpest possible image scaling for 2026 standards
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# ─── CONFIG & PATHS ──────────────────────────────────────────────────────────
OUTPUT_DIR = Path("output")
ASSETS_DIR = Path("public/image")
MUSIC_DIR = Path("public/music")
OUTPUT_DIR.mkdir(exist_ok=True)

# ─── STEP 1: AI SCRIPT GENERATOR (GROQ) ──────────────────────────────────────
async def get_groq_script():
    """Fetches a fresh, human-like trading tip from Groq AI."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("⚠️ No GROQ_API_KEY found. Using fallback script.")
        return "Dost, trading mein sabr hi sabse badi kamai hai. Jaldbazi mat karo."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Prompt tuned for ZENO (The wise trading kid)
    prompt = (
        "Write a 1-sentence trading wisdom tip in Hinglish (Hindi + English). "
        "Character: Zeno, a smart 10-year-old boy. "
        "Topic: Random (Stop Loss, Risk Management, Emotions, or Patience). "
        "Tone: Friendly, professional, and human-like. "
        "Strictly 1 sentence only. No hashtags or emojis in text."
    )

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        script = result['choices'][0]['message']['content'].strip().replace('"', '')
        print(f"🤖 Groq Generated: {script}")
        return script
    except Exception as e:
        print(f"⚠️ Groq Error: {e}. Using fallback.")
        return "Market mein discipline hi aapko ek safal trader banayega."

# ─── STEP 2: VOICE GENERATION (KID VOICE) ────────────────────────────────────
async def generate_voice(script: str, output_path: Path):
    import edge_tts
    # Swara (Female) = Perfect high-energy voice for a 10-year-old boy character
    communicate = edge_tts.Communicate(script, "hi-IN-SwaraNeural", rate="+10%", pitch="+5Hz")
    await communicate.save(str(output_path))
    print(f"✅ HD Kid Voice Generated: {output_path}")

# ─── STEP 3: HD VIDEO ASSEMBLY ───────────────────────────────────────────────
def create_video(voice_path: Path):
    today = datetime.datetime.now().strftime("%Y%m%d")
    video_path = OUTPUT_DIR / f"reel_{today}.mp4"
    meta_path = OUTPUT_DIR / f"meta_{today}.json"

    voice_audio = AudioFileClip(str(voice_path))
    final_audio = voice_audio

    # 🎵 Background Music Mix
    valid_music = ["bgmusic1.mp3", "bgmusic2.mp3", "bgmusic3.mp3"]
    music_files = [MUSIC_DIR / m for m in valid_music if (MUSIC_DIR / m).exists()]
    if music_files:
        try:
            bg_file = random.choice(music_files)
            bg_music = AudioFileClip(str(bg_file)).volumex(0.10).set_duration(voice_audio.duration).audio_fadeout(2)
            final_audio = CompositeAudioClip([voice_audio, bg_music])
            print(f"🎵 Mixed with: {bg_file.name}")
        except: pass

    # 🖼️ Full HD Vertical (1080x1920)
    img_path = ASSETS_DIR / "zeno_happy.png"
    if not img_path.exists():
        # Fallback to any png in the folder if zeno_happy is missing
        png_files = list(ASSETS_DIR.glob("*.png"))
        img_path = png_files[0] if png_files else None

    if not img_path:
        print("❌ No images found in public/image!")
        return

    image_clip = ImageClip(str(img_path)).set_duration(voice_audio.duration)
    
    # Smart Crop/Resize to 9:16 vertical
    w, h = image_clip.size
    if w/h > 1080/1920:
        image_clip = image_clip.resize(height=1920)
    else:
        image_clip = image_clip.resize(width=1080)
        
    video = image_clip.crop(x_center=image_clip.w/2, y_center=image_clip.h/2, width=1080, height=1920)
    
    # 🎬 Human Cinematic Motion (Slow Zoom)
    video = video.fx(vfx.resize, lambda t: 1 + 0.06 * (t / voice_audio.duration))
    video = video.set_audio(final_audio)

    # 🏷️ Yellow Pro Headlines
    subtitle = TextClip(
        "ZENO KI BAAT ✨",
        fontsize=72, color='yellow', font='Arial-Bold',
        stroke_color='black', stroke_width=3, method='caption',
        size=(950, None), align='center'
    ).set_position(('center', 1450)).set_duration(video.duration)

    # 🚀 HD Export
    final_video = CompositeVideoClip([video, subtitle], size=(1080, 1920)).set_fps(24)
    final_video.write_videofile(
        str(video_path), 
        codec="libx264", 
        audio_codec="aac", 
        fps=24, 
        bitrate="5000k", # High Bitrate for HD clarity
        preset="slow"    # High quality encoding
    )

    # 📝 Meta for Social Uploaders
    metadata = {
        "title": f"ZENO ki Baat | {today} #Shorts",
        "description": "Daily Trading Wisdom for the Indian Market.",
        "video_path": str(video_path)
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f)
    print(f"✅ Success! HD Reel and Metadata ready.")

# ─── MAIN ENGINE ─────────────────────────────────────────────────────────────
async def main():
    voice_file = OUTPUT_DIR / "voice.mp3"
    
    # 🤖 1. Get AI Script
    script = await get_groq_script()
    
    # 🎙️ 2. Generate Voice
    await generate_voice(script, voice_file)
    
    # 🎥 3. Create HD Video
    create_video(voice_file)

if __name__ == "__main__":
    asyncio.run(main())
