import os
import asyncio
import pandas as pd
from moviepy.editor import *
import edge_tts

# --- PATHS ---
IMAGE_DIR = "public/image"
MUSIC_DIR = "public/music"
OUTPUT_DIR = "output"

async def generate_content():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Handshake with main video data
    context_path = os.path.join(OUTPUT_DIR, "analysis_video_id.txt")
    main_id = "LIVE"
    if os.path.exists(context_path):
        with open(context_path, 'r') as f:
            main_id = f.read().strip()

    # 1. THE ZENO REEL (Storytelling)
    # Pronunciation: "ड र" (Space forces short 'a' sound)
    hindi_display = "मार्केट नहीं आपका डर है। पेशेंस रखिए।"
    hindi_audio = "दोस्तों ट्रेडिंग में सबसे बड़ा दुश्मन मार्केट नहीं आपका ड र है। पेशेंस रखिए।"
    
    # Generate Audio
    audio_path = os.path.join(OUTPUT_DIR, "zeno_voice.mp3")
    communicate = edge_tts.Communicate(hindi_audio, "hi-IN-SwaraNeural", rate="+5%")
    await communicate.save(audio_path)
    audio_clip = AudioFileClip(audio_path)

    # Build Visuals
    bg = ColorClip(size=(1080, 1920), color=(5, 15, 35)).set_duration(audio_clip.duration)
    
    # Use your specific file from public/image/
    zeno_file = os.path.join(IMAGE_DIR, "zeno_fear.png")
    if os.path.exists(zeno_file):
        zeno_char = ImageClip(zeno_file).set_duration(audio_clip.duration).resize(width=900).set_position(('center', 700))
    else:
        zeno_char = ColorClip(size=(1,1), color=(0,0,0)).set_duration(0)

    # Captions (Positioned low to avoid blocking Zeno)
    txt = TextClip(hindi_display, fontsize=55, color='white', bg_color='black', method='caption', size=(900, None), font='Arial')
    txt = txt.set_position(('center', 1400)).set_duration(audio_clip.duration)

    # Final Reel
    reel = CompositeVideoClip([bg, zeno_char, txt]).set_audio(audio_clip)
    reel_output = os.path.join(OUTPUT_DIR, "zeno_reel.mp4")
    reel.write_videofile(reel_output, fps=30, codec="libx264", threads=4, logger=None)

    # 2. THE MARKET SHORT (Data Crop)
    short_bg = ColorClip(size=(1080, 1920), color=(0, 0, 0)).set_duration(5)
    short_txt = TextClip(f"TRADING LEVELS\n{main_id}", fontsize=80, color='gold', font='Arial')
    short_v = CompositeVideoClip([short_bg, short_txt.set_position('center')]).set_duration(5)
    short_output = os.path.join(OUTPUT_DIR, "market_short.mp4")
    short_v.write_videofile(short_output, fps=30, codec="libx264", threads=4, logger=None)

    # --- LOGS FOR YOUR CHANNEL ---
    print("\n" + "="*50)
    print(f"✅ REEL: {reel_output}")
    print(f"TITLE: ZENO Ki Baat | #TradingPsychology")
    print(f"DESC: {hindi_display}\n\nJoin for Daily Alerts:\n🔗 Telegram: t.me/ai360trading\n🌐 Web: https://ai360trading.in")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(generate_content())
