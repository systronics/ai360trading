import os
import json
import asyncio
import datetime
import random
import numpy as np
from pathlib import Path
from moviepy.editor import *
import PIL.Image

# 🟢 MANDATORY FIX: This stops the 'ANTIALIAS' error you just saw
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# ─── CONFIG & PATHS ──────────────────────────────────────────────────────────
OUTPUT_DIR = Path("output")
ASSETS_DIR = Path("public/image")
MUSIC_DIR = Path("public/music")
OUTPUT_DIR.mkdir(exist_ok=True)

async def generate_voice(script: str, output_path: Path):
    import edge_tts
    communicate = edge_tts.Communicate(script, "hi-IN-MadhurNeural", rate="+5%", pitch="+2Hz")
    await communicate.save(str(output_path))
    print(f"✅ Voice generated at: {output_path}")

def create_video(voice_path: Path):
    today = datetime.datetime.now().strftime("%Y%m%d")
    video_path = OUTPUT_DIR / f"reel_{today}.mp4"
    meta_path = OUTPUT_DIR / f"meta_{today}.json"

    voice_audio = AudioFileClip(str(voice_path))

    # 🎵 Background Music
    final_audio = voice_audio
    valid_music = ["bgmusic1.mp3", "bgmusic2.mp3", "bgmusic3.mp3"]
    music_files = [MUSIC_DIR / m for m in valid_music if (MUSIC_DIR / m).exists()]
    
    if music_files:
        try:
            bg_file = random.choice(music_files)
            print(f"🎵 Adding Music: {bg_file.name}")
            bg_music = AudioFileClip(str(bg_file)).volumex(0.12).set_duration(voice_audio.duration).audio_fadeout(2)
            final_audio = CompositeAudioClip([voice_audio, bg_music])
        except Exception as e:
            print(f"⚠️ Music error: {e}")

    # 🖼️ Image & Zoom (Human-like)
    img_path = ASSETS_DIR / "zeno_happy.png"
    if not img_path.exists():
        img_path = list(ASSETS_DIR.glob("*.png"))[0]
    
    image_clip = ImageClip(str(img_path)).set_duration(voice_audio.duration)
    # Slow 10% Zoom
    video = image_clip.fx(vfx.resize, lambda t: 1 + 0.1 * (t / voice_audio.duration))
    video = video.set_audio(final_audio)

    # 🏷️ Yellow Subtitle
    subtitle = TextClip(
        "ZENO KI BAAT ✨",
        fontsize=75, color='yellow', font='Arial-Bold',
        stroke_color='black', stroke_width=2, method='caption',
        size=(850, None), align='center'
    ).set_position(('center', 1420)).set_duration(video.duration)

    # 🚀 Export
    final_video = CompositeVideoClip([video, subtitle]).set_fps(24)
    final_video.write_videofile(str(video_path), codec="libx264", audio_codec="aac", fps=24, preset="ultrafast")

    metadata = {"title": f"ZENO Wisdom | {today}", "description": "Market Wisdom", "video_path": str(video_path)}
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f)
    print(f"✅ Success! Metadata saved to {meta_path}")

async def main():
    voice_file = OUTPUT_DIR / "voice.mp3"
    daily_script = "Trading mein sabse bada dushman jaldbaazi hai. Sabr rakho, mauka apne aap aayega."
    await generate_voice(daily_script, voice_file)
    create_video(voice_file)

if __name__ == "__main__":
    asyncio.run(main())
