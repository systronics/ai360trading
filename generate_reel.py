import os
import asyncio
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
import edge_tts

# --- CONFIGURATION FOR GITHUB ACTIONS ---
# This tells MoviePy exactly where the ImageMagick binary is located on Ubuntu
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

async def generate_voiceover(text, output_path):
    """Generates the Hindi voiceover using edge-tts."""
    print(f"🎙️ Generating voice for: {text[:50]}...")
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save(output_path)
    print(f"✅ Voice generated at: {output_path}")
    return output_path

def create_video(voice_file, script_text):
    """
    Combines voiceover with background and text.
    Uses MoviePy 1.0.3 syntax (set_opacity, fontsize).
    """
    print("🎬 Starting video synthesis...")
    try:
        # 1. Load Audio and determine duration
        audio = AudioFileClip(voice_file)
        duration = audio.duration

        # 2. Load Background Video
        # Path assumes your background is in an 'assets' folder
        bg_video = VideoFileClip("assets/background.mp4").subclip(0, duration)
        
        # 3. Create Branding Clip (Top/Bottom Branding)
        branding = (TextClip(
                        "ai360trading.in", 
                        fontsize=40, 
                        color='white', 
                        font='Arial-Bold',
                        method='caption'
                    )
                    .set_opacity(0.6)
                    .set_duration(duration)
                    .set_position(('center', 1600))) # Positioned near the bottom

        # 4. Create Main Script Text (Subtitles)
        # size=(width, None) ensures text wraps within the reel width
        content_text = (TextClip(
                            script_text,
                            fontsize=60,
                            color='yellow',
                            font='Arial-Bold',
                            method='caption',
                            size=(bg_video.w * 0.8, None)
                        )
                        .set_duration(duration)
                        .set_position('center'))

        # 5. Combine everything
        final_video = CompositeVideoClip([bg_video, branding, content_text])
        final_video.audio = audio

        # 6. Define Output Path
        if not os.path.exists("output"):
            os.makedirs("output")
            
        output_filename = f"output/reel_{os.path.basename(voice_file).replace('.mp3', '.mp4')}"

        # 7. Write the File
        final_video.write_videofile(
            output_filename,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            threads=4 # Faster processing on GitHub Runners
        )

        print(f"🚀 Success! Reel created: {output_filename}")
        return output_filename

    except Exception as e:
        print(f"❌ Error during video creation: {e}")
        # Fallback: Save video with just audio if TextClip fails
        print("⚠️ Attempting fallback (Video + Audio only)...")
        bg_video = VideoFileClip("assets/background.mp4").subclip(0, duration)
        bg_video.audio = audio
        fallback_name = f"output/fallback_{os.path.basename(voice_file).replace('.mp3', '.mp4')}"
        bg_video.write_videofile(fallback_name, fps=24, codec="libx264")
        return fallback_name

async def main():
    # Example Script - In a real run, you might fetch this from Groq/API
    script = "Mujhe lagta hai ki trading mein sabse badi cheez hai patience aur discipline, kyunki agar aap in dono ko follow karte hain to aapke losses kam honge."
    
    # Generate Audio
    voice_path = "output/voice.mp3"
    if not os.path.exists("output"):
        os.makedirs("output")
        
    await generate_voiceover(script, voice_path)
    
    # Generate Video
    create_video(voice_path, script)

if __name__ == "__main__":
    asyncio.run(main())
