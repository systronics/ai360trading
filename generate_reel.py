import os, json, random, asyncio
from pathlib import Path
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip

OUT = Path("output")

async def generate_zeno_script(client):
    # Rotating Human Topics: Emotional Story, Savings, Logic
    topics = ["Pain of Overtrading", "50-30-20 Saving Rule", "Market Psychology during War"]
    theme = random.choice(topics)
    
    prompt = f"""You are Zeno, a wise 3D Trading Mentor.
    Theme: {theme}. Generate a 60-second heart-touching Hinglish Storytelling script.
    
    REQUIREMENTS:
    - Exactly 150 words (Essential for 60s watch time).
    - Start with a Hook: 'Doston, kya aapne kabhi socha hai...'
    - No lists. Tell a real-world human story.
    - End with a life lesson for traders.

    Respond ONLY with JSON: {{ "content": "150 words...", "emotion": "zeno_thinking" }}"""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

async def main_reel(client):
    script_data = await generate_zeno_script(client)
    aud_p = OUT / "zeno_reel.mp3"
    comm = edge_tts.Communicate(script_data['content'], "hi-IN-SwaraNeural")
    await comm.save(str(aud_p))
    
    voice = AudioFileClip(str(aud_p))
    # Overlay Zeno Image (e.g., zeno_thinking.png)
    img_path = Path(f"public/image/{script_data['emotion']}.png")
    img = ImageClip(str(img_path)).set_duration(voice.duration).resize(height=1200).set_position(('center', 'center'))
    
    final = CompositeVideoClip([img], size=(1080, 1920)).set_audio(voice)
    final.write_videofile(str(OUT / "final_zeno_reel.mp4"), fps=24)

if __name__ == "__main__":
    pass
