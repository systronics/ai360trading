import os
import asyncio
from moviepy.editor import *
import edge_tts

# --- PATH CONFIGURATION ---
IMAGE_DIR = "public/image"
MUSIC_DIR = "public/music"
OUTPUT_DIR = "output"

async def generate_content():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. RETRIEVE DATA CONTEXT
    context_path = os.path.join(OUTPUT_DIR, "analysis_video_id.txt")
    main_video_id = "LIVE_DATA"
    if os.path.exists(context_path):
        with open(context_path, 'r') as f:
            main_video_id = f.read().strip()

    # ---------------------------------------------------------
    # PART A: ZENO REEL (STORYTELLING)
    # ---------------------------------------------------------
    # PRONUNCIATION FIX: Using "ड र" and "D-urr" phonetic trick
    display_text = "दोस्तों ट्रेडिंग में सबसे बड़ा दुश्मन मार्केट नहीं आपका डर है। पेशेंस रखिए।"
    audio_script = "दोस्तों ट्रेडिंग में सबसे बड़ा दुश्मन मार्केट नहीं आपका ड र है। पेशेंस रखिए।"
    
    # Audio Generation
    audio_path = os.path.join(OUTPUT_DIR, "zeno_voice.mp3")
    communicate = edge_tts.Communicate(audio_script, "hi-IN-SwaraNeural", rate="+5%")
    await communicate.save(audio_path)
    audio_clip = AudioFileClip(audio_path)

    # Visuals - Using your specific files from 'public/image'
    bg = ColorClip(size=(1080, 1920), color=(5, 15, 35)).set_duration(audio_clip.duration)
    
    zeno_img = os.path.join(IMAGE_DIR, "zeno_fear.png") # Match from your uploaded image
    if os.path.exists(zeno_img):
        zeno_char = ImageClip(zeno_img).set_duration(audio_clip.duration).resize(width=900).set_position(('center', 700))
    else:
        zeno_char = ColorClip(size=(1,1), color=(0,0,0)).set_duration(0)

    # Music - Using your bgmusic2.mp3
    music_file = os.path.join(MUSIC_DIR, "bgmusic2.mp3")
    if os.path.exists(music_file):
        bg_music = AudioFileClip(music_file).volumex(0.15).set_duration(audio_clip.duration)
        final_audio = CompositeAudioClip([audio_clip, bg_music])
    else:
        final_audio = audio_clip

    # Caption
    caption = TextClip(display_text, fontsize=55, color='white', bg_color='black', method='caption', size=(900, None), font='Arial')
    caption = caption.set_position(('center', 1400)).set_duration(audio_clip.duration)

    # Export Reel
    reel = CompositeVideoClip([bg, zeno_char, caption]).set_audio(final_audio)
    reel_path = os.path.join(OUTPUT_DIR, "zeno_reel.mp4")
    reel.write_videofile(reel_path, fps=30, codec="libx264", threads=4, logger=None)

    # ---------------------------------------------------------
    # PART B: DATA SHORT (CROP)
    # ---------------------------------------------------------
    short_bg = ColorClip(size=(1080, 1920), color=(0, 0, 0)).set_duration(5)
    short_text = TextClip(f"TRADING LEVELS\n{main_video_id}", fontsize=80, color='gold', font='Arial')
    short_text = short_text.set_position('center').set_duration(5)
    
    short_v = CompositeVideoClip([short_bg, short_text])
    short_path = os.path.join(OUTPUT_DIR, "market_short.mp4")
    short_v.write_videofile(short_path, fps=30, codec="libx264", threads=4, logger=None)

    # ---------------------------------------------------------
    # PRINT LOGS (Title, Desc, Links)
    # ---------------------------------------------------------
    print("\n" + "="*50)
    print("🚀 CONTENT GENERATION COMPLETE")
    print("="*50)
    
    # REEL LOGS
    print("\n📺 [REEL DETAILS - FACEBOOK/INSTAGRAM]")
    print("TITLE: ZENO Ki Baat - Control Your Emotions #TradingPsychology")
    print(f"DESC: {display_text}\n\nJoin for Daily Alerts:\n🔗 Telegram: t.me/ai360trading\n🌐 Web: www.ai360trading.com")
    print("HASHTAGS: #TradingTips #Nifty #Sensex #Zeno #Investing")
    print(f"FILE: {reel_path}")

    # SHORT LOGS
    print("\n📺 [SHORT DETAILS - YOUTUBE]")
    print(f"TITLE: Market Levels Today | {main_video_id} #Shorts")
    print(f"DESC: Quick update on market levels. Full analysis in main video.\n\n🔗 Website: www.ai360trading.com\n#StockMarket #Shorts #Trading")
    print(f"FILE: {short_path}")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(generate_content())
