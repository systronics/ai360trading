import os
import asyncio
import random
from moviepy.editor import ColorClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
import edge_tts

# --- CONFIGURATION FOR GITHUB ACTIONS ---
# Ensures MoviePy finds ImageMagick on Ubuntu runners
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

async def generate_voiceover(text, output_path):
    """Generates Hindi voiceover using edge-tts."""
    print(f"🎙️ Generating voice for: {text[:50]}...")
    # Using Madhur (Male) or Swara (Female) - both sound natural
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save(output_path)
    print(f"✅ Voice generated at: {output_path}")
    return output_path

def create_video(voice_file, script_text):
    """
    Creates a 1080x1920 Reel. 
    Uses a solid color background if background.mp4 is missing.
    """
    print("🎬 Starting video synthesis...")
    try:
        # 1. Load Audio
        audio = AudioFileClip(voice_file)
        duration = audio.duration

        # 2. Create/Load Background
        # If you ever upload assets/background.mp4, it will use that. 
        # Otherwise, it creates a professional dark blue background.
        bg_path = "assets/background.mp4"
        if os.path.exists(bg_path):
            from moviepy.editor import VideoFileClip
            bg_clip = VideoFileClip(bg_path).subclip(0, duration)
        else:
            print("ℹ️ background.mp4 not found. Generating a solid background...")
            # Create a 1080x1920 (9:16) dark background
            bg_clip = ColorClip(size=(1080, 1920), color=(10, 20, 35), duration=duration)

        # 3. Create Branding (Bottom)
        branding = (TextClip(
                        "ai360trading.in", 
                        fontsize=45, 
                        color='gray', 
                        font='Arial-Bold',
                        method='caption'
                    )
                    .set_opacity(0.5)
                    .set_duration(duration)
                    .set_position(('center', 1700)))

        # 4. Create Main Script Text (Subtitles)
        # We use 'caption' method to ensure Hindi text wraps properly
        content_text = (TextClip(
                            script_text,
                            fontsize=70,
                            color='yellow',
                            font='Arial-Bold',
                            method='caption',
                            size=(900, None) # Wraps text within 900px width
                        )
                        .set_duration(duration)
                        .set_position('center'))

        # 5. Composite
        final_video = CompositeVideoClip([bg_clip, branding, content_text])
        final_video.audio = audio

        # 6. Output Handling
        if not os.path.exists("output"):
            os.makedirs("output")
            
        output_filename = f"output/reel_{os.path.basename(voice_file).replace('.mp3', '.mp4')}"

        # 7. Write File
        # Using 'libx264' for maximum compatibility with Instagram/YouTube
        final_video.write_videofile(
            output_filename,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            threads=4
        )

        print(f"🚀 Success! Reel created: {output_filename}")
        return output_filename

    except Exception as e:
        print(f"❌ Error during video creation: {e}")
        return None

async def main():
    # Folder Setup
    if not os.path.exists("output"):
        os.makedirs("output")
    if not os.path.exists("assets"):
        os.makedirs("assets")

    # The Script (You can replace this with Groq output later)
    script = "Mujhe lagta hai ki trading mein sabse badi cheez hai patience aur discipline, kyunki agar aap in dono ko follow karte hain to aapke losses kam honge."
    
    voice_path = "output/voice.mp3"
    
    # Run Steps
    await generate_voiceover(script, voice_path)
    create_video(voice_path, script)

if __name__ == "__main__":
    asyncio.run(main())
