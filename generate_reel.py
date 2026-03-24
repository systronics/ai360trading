import os
import json
import datetime
import random
import numpy as np
from pathlib import Path
from moviepy.editor import *
from moviepy.video.fx.all import resize

# ─── CONFIG & PATHS ──────────────────────────────────────────────────────────
OUTPUT_DIR = Path("output")
ASSETS_DIR = Path("public/image")
MUSIC_DIR = Path("public/music")
OUTPUT_DIR.mkdir(exist_ok=True)

def get_dynamic_hook(today_topic):
    """Translates the AI topic into a catchy 'Human' Headline."""
    hooks = {
        "patience": "SABR KA PHAL ✨",
        "risk": "RISK MANAGEMENT 📊",
        "discipline": "DISCIPLINE IS KEY 🔑",
        "market": "MARKET KI BAAT 📈",
        "family": "FAMILY FIRST ❤️",
        "default": "ZENO KI BAAT 🤖"
    }
    # Looks for a keyword in your script topic, else uses default
    for key in hooks:
        if key in today_topic.lower():
            return hooks[key]
    return hooks["default"]

def get_random_music():
    """Pick between your 3 uploaded tracks."""
    valid_music = ["bgmusic1.mp3", "bgmusic2.mp3", "bgmusic3.mp3"]
    music_files = [MUSIC_DIR / m for m in valid_music if (MUSIC_DIR / m).exists()]
    return random.choice(music_files) if music_files else None

def generate_video():
    today = datetime.datetime.now().strftime("%Y%m%d")
    video_path = OUTPUT_DIR / f"reel_{today}.mp4"
    meta_path = OUTPUT_DIR / f"meta_{today}.json"
    voice_path = OUTPUT_DIR / f"voice_{today}.mp3"
    
    # 1. Load Voice
    if not voice_path.exists():
        print("❌ Voice missing!")
        return
    voice_audio = AudioFileClip(str(voice_path))

    # 2. Setup Dynamic Hook (Subtitle)
    # This simulates a human picking the best title for the video
    raw_topic = "patience" # In your full script, this comes from the Groq AI step
    hook_text = get_dynamic_hook(raw_topic)

    # 3. Add Background Music
    bg_file = get_random_music()
    if bg_file:
        bg_music = AudioFileClip(str(bg_file)).volumex(0.12)
        bg_music = bg_music.set_duration(voice_audio.duration).audio_fadeout(2)
        final_audio = CompositeAudioClip([voice_audio, bg_music])
    else:
        final_audio = voice_audio

    # 4. Background Image & "Lite" Ken Burns
    img_path = ASSETS_DIR / "zeno_happy.png"
    if not img_path.exists(): img_path = list(ASSETS_DIR.glob("*.png"))[0]
    
    image_clip = ImageClip(str(img_path)).set_duration(voice_audio.duration)
    # Slow 10% Zoom for 'Human' motion
    video = image_clip.fx(vfx.resize, lambda t: 1 + 0.1 * (t / voice_audio.duration))
    video = video.set_audio(final_audio)

    # 5. The "Human-Styled" Subtitle
    subtitle = TextClip(
        hook_text,
        fontsize=75,
        color='yellow',
        font='Arial-Bold',
        stroke_color='black',
        stroke_width=3,
        method='caption',
        size=(850, None),
        align='center'
    ).set_position(('center', 1420)).set_duration(voice_audio.duration)

    # 6. Final Composite
    final_video = CompositeVideoClip([video, subtitle])
    final_video = final_video.set_fps(24)

    # 7. Write File
    final_video.write_videofile(
        str(video_path),
        codec="libx264",
        audio_codec="aac",
        fps=24,
        preset="ultrafast",
        threads=4
    )

    # 8. Meta for Uploader
    metadata = {
        "title": f"{hook_text} | ZENO {today} #Shorts",
        "description": f"Zeno ki daily wisdom. \n#AI360Trading #Hinglish",
        "video_path": str(video_path)
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f)

    print(f"✅ Reel Generated with Music and Hook: {hook_text}")

if __name__ == "__main__":
    generate_video()
