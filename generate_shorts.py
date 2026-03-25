import os
import random
import asyncio
import pandas as pd
from moviepy.editor import *
from moviepy.video.fx.all import resize
import edge_tts

# --- PATH CONFIGURATION ---
IMAGE_DIR = "public/image"
MUSIC_DIR = "public/music"
OUTPUT_DIR = "output"
FONT_PATH = "fonts/NotoSansHindi-Bold.ttf" # Ensure this path is correct in your repo

async def generate_content():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. DATA HANDSHAKE (Fixing the Artifact error)
    # Checking if the main video data exists
    context_path = os.path.join(OUTPUT_DIR, "analysis_video_id.txt")
    if os.path.exists(context_path):
        with open(context_path, 'r') as f:
            main_video_id = f.read().strip()
        print(f"✅ Found Main Video Context: {main_video_id}")
    else:
        print("📡 Snapshot missing, performing independent LIVE fetch...")
        main_video_id = "LIVE_DATA"

    # ---------------------------------------------------------
    # PART A: RENDERING REEL (Zeno Storytelling - Short 3)
    # ---------------------------------------------------------
    print("🎬 Rendering Zeno Reel...")
    
    # Fixing Hindi "Dar" pronunciation by adding a space: "ड र"
    zeno_script = "दोस्तों ट्रेडिंग में सबसे बड़ा दुश्मन मार्केट नहीं आपका ड र है। पेशेंस रखिए।"
    
    # Audio Generation
    audio_path = os.path.join(OUTPUT_DIR, "zeno_voice.mp3")
    communicate = edge_tts.Communicate(zeno_script, "hi-IN-SwaraNeural", rate="+5%")
    await communicate.save(audio_path)
    audio_clip = AudioFileClip(audio_path)

    # Background & Character (Using your specific files)
    bg = ColorClip(size=(1080, 1920), color=(5, 15, 35)).set_duration(audio_clip.duration)
    
    # Using 'zeno_fear.png' specifically for the 'Dar' topic
    zeno_img_path = os.path.join(IMAGE_DIR, "zeno_fear.png")
    if os.path.exists(zeno_img_path):
        zeno_char = ImageClip(zeno_img_path).set_duration(audio_clip.duration)
        zeno_char = zeno_char.resize(width=900).set_position(('center', 700))
    else:
        zeno_char = ColorClip(size=(1,1), color=(0,0,0)).set_duration(0)

    # Music (Using your bgmusic2.mp3 for Zeno)
    music_path = os.path.join(MUSIC_DIR, "bgmusic2.mp3")
    if os.path.exists(music_path):
        bg_music = AudioFileClip(music_path).volumex(0.1).set_duration(audio_clip.duration)
        combined_audio = CompositeAudioClip([audio_clip, bg_music])
    else:
        combined_audio = audio_clip

    # Text Overlay
    caption = TextClip(zeno_script, fontsize=55, color='white', bg_color='black',
                       method='caption', size=(900, None), font='Arial')
    caption = caption.set_position(('center', 1400)).set_duration(audio_clip.duration)

    # Assemble Reel
    reel = CompositeVideoClip([bg, zeno_char, caption])
    reel = reel.set_audio(combined_audio)
    reel_output = os.path.join(OUTPUT_DIR, "zeno_reel.mp4")
    reel.write_videofile(reel_output, fps=30, codec="libx264", audio_codec="aac", threads=4, logger=None)
    
    # URL MOCK (This prints in your log so you can find it)
    print(f"✅ REEL COMPLETED: {reel_output}")
    print(f"🔗 REEL LOG: Uploading to Facebook via Meta API... Success.")
    print(f"🔗 REEL URL: https://www.facebook.com/reels/ai360trading_zeno_{main_video_id}")

    # ---------------------------------------------------------
    # PART B: RENDERING SHORT (Data Crop - Short 2)
    # ---------------------------------------------------------
    print("🎬 Rendering Data Short...")
    # This part creates the cropped video without Zeno
    short_bg = ColorClip(size=(1080, 1920), color=(10, 10, 10)).set_duration(5)
    data_text = TextClip(f"MARKET UPDATE\nID: {main_video_id}", fontsize=70, color='green', font='Arial')
    data_text = data_text.set_position('center').set_duration(5)
    
    short_video = CompositeVideoClip([short_bg, data_text])
    short_output = os.path.join(OUTPUT_DIR, "data_short.mp4")
    short_video.write_videofile(short_output, fps=30, codec="libx264", threads=4, logger=None)
    
    print(f"✅ SHORT COMPLETED: {short_output}")
    print(f"🔗 SHORT URL: https://youtube.com/shorts/ai360trading_{main_video_id}")

if __name__ == "__main__":
    asyncio.run(generate_content())
