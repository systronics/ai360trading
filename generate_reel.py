import os, json, random, asyncio
from pathlib import Path
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, ColorClip

OUT = Path("output")
OUT.mkdir(exist_ok=True)

async def generate_zeno_script(client):
    """
    Generates a 60-second emotional storytelling script for Zeno.
    Focuses on human emotions, investment psychology, and saving ideas.
    """
    # Daily variety to ensure content never looks AI-generated/repetitive
    topics = [
        "The Emotional Pain of a Revenge Trade (and how to heal)",
        "The 50-30-20 Saving Rule: How to build wealth while living your life",
        "Why 'Patience' is the most expensive skill in the Stock Market",
        "A Story of a trader who lost it all by ignoring his family's advice",
        "Investment Logic: Why your first 1 Lakh is the hardest to save"
    ]
    theme = random.choice(topics)
    
    # Specific emotions mapped to your public/image assets
    emotions = ["zeno_thinking", "zeno_happy", "zeno_neutral"]
    chosen_emotion = random.choice(emotions)
    
    prompt = f"""You are Zeno, the wise and warm 3D Trading Mentor for ai360trading.in.
    Theme: {theme}. 
    
    TASK: Write a 60-second heart-touching Hinglish Storytelling script.
    
    STRICT RULES (For Human Touch & 60s Duration):
    1. WORD COUNT: Exactly 150 words. This is vital to hit the 60-second mark.
    2. START: Hook the audience immediately with 'Doston, ek sach bataun?' or 'Kya aapne kabhi socha hai...'
    3. NO LISTS: Do not use bullet points or 'Firstly/Secondly'. Tell a real-world human story with emotions.
    4. VIBE: Talk like a human elder brother (Bade Bhai). Use words like 'Ehsaas', 'Zimmedari', 'Sapne'.
    5. END: Give a deep life lesson that makes people want to save and invest properly.
    6. NO AI-SPEAK: Avoid 'Conclusion', 'In summary', or generic 'Happy Trading' closers.

    Respond ONLY with JSON: 
    {{ 
      "content": "150 words of emotional storytelling...", 
      "emotion": "{chosen_emotion}",
      "short_caption": "A viral 5-word Hinglish caption"
    }}"""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

async def main_reel(client):
    """Processes the Zeno script into a high-retention vertical reel."""
    print(f"[PROCESS] Generating 60-Second Zeno Wisdom...")
    script_data = await generate_zeno_script(client)
    
    aud_p = OUT / "zeno_reel.mp3"
    # Using Swara for a soft, storytelling feel or Madhur for authoritative wisdom
    voice_name = "hi-IN-SwaraNeural" if script_data['emotion'] == "zeno_happy" else "hi-IN-MadhurNeural"
    
    print(f"[PROGRESS] Generating Voiceover ({voice_name})...")
    comm = edge_tts.Communicate(script_data['content'], voice_name)
    await comm.save(str(aud_p))
    
    voice = AudioFileClip(str(aud_p))
    
    # 1. Background Layer (9:16)
    bg = ColorClip(size=(1080, 1920), color=(15, 15, 20)).set_duration(voice.duration + 0.5)
    
    # 2. Zeno Character Overlay
    img_path = Path(f"public/image/{script_data['emotion']}.png")
    if not img_path.exists():
        # Fallback if specific emotion image is missing
        img_path = Path("public/image/zeno_neutral.png")
        
    print(f"[PROGRESS] Using Character Asset: {img_path.name}")
    img = (ImageClip(str(img_path))
           .set_duration(voice.duration + 0.5)
           .resize(height=1100)
           .set_position(('center', 'center')))
    
    # 3. Assemble Final Reel
    final = CompositeVideoClip([bg, img], size=(1080, 1920)).set_audio(voice)
    
    output_filename = str(OUT / "final_zeno_reel.mp4")
    final.write_videofile(output_filename, fps=24, codec="libx264")
    print(f"✅ Zeno Reel Complete: {output_filename}")

if __name__ == "__main__":
    # This integrates with your existing Groq client setup
    pass
