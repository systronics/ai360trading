import os
import asyncio
import json
import datetime
from moviepy.editor import ColorClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
import edge_tts

# --- CONFIGURATION ---
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

async def generate_voiceover(text, output_path):
    print(f"🎙️ Generating voice...")
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save(output_path)
    return output_path

def create_video(voice_file, script_text):
    print("🎬 Starting video synthesis...")
    audio = AudioFileClip(voice_file)
    duration = audio.duration
    
    # Create background
    bg_clip = ColorClip(size=(1080, 1920), color=(10, 20, 35), duration=duration)

    # Branding
    branding = (TextClip("ai360trading.in", fontsize=45, color='gray', font='Arial-Bold', method='caption')
                .set_opacity(0.5).set_duration(duration).set_position(('center', 1700)))

    # Main Text
    content_text = (TextClip(script_text, fontsize=70, color='yellow', font='Arial-Bold', method='caption', size=(900, None))
                    .set_duration(duration).set_position('center'))

    final_video = CompositeVideoClip([bg_clip, branding, content_text])
    final_video.audio = audio

    output_filename = f"output/reel_voice.mp4"
    final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac", remove_temp=True, threads=4)
    
    return output_filename

async def main():
    if not os.path.exists("output"): os.makedirs("output")
    
    today = datetime.datetime.now().strftime("%Y%m%d")
    script = "Trading mein sabse badi cheez patience aur discipline hai. Jab aap setup ka wait karte hain, tabhi profit banta hai."
    
    # 1. Generate Voice
    voice_path = "output/voice.mp3"
    await generate_voiceover(script, voice_path)
    
    # 2. Generate Video
    video_path = create_video(voice_path, script)
    
    # 3. CRITICAL FIX: Save the Meta file for FB/IG/YT
    meta_data = {
        "title": f"ZENO Ki Baat - {today} #Shorts",
        "description": f"{script} #ZenoKiBaat #TradingIndia #ai360trading",
        "video_path": video_path,
        "date": today
    }
    
    meta_path = f"output/meta_{today}.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=4)
    
    print(f"✅ Metadata saved at: {meta_path}")

if __name__ == "__main__":
    asyncio.run(main())
