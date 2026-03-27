import os, sys, json, asyncio, textwrap, random
from datetime import datetime
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, concatenate_audioclips
from groq import Groq

# ─── CONFIG & ASSETS ────────────────────────────────────────────────────────
OUT       = Path("output")
MUSIC_DIR = Path("public/music")
W, H      = 1920, 1080
FPS       = 24
# Swara for Beginner/Intermediate, Madhur for Advanced
VOICES    = {"Beginner": "hi-IN-SwaraNeural", "Advanced": "hi-IN-MadhurNeural"}
os.makedirs(OUT, exist_ok=True)

# ─── THEME ENGINE ────────────────────────────────────────────────────────────
LEVEL_THEMES = {
    "Beginner":     {"bg_top": (10, 20, 50), "bg_bot": (20, 40, 90),  "accent": (80, 180, 255),  "text": (240, 250, 255), "subtext": (160, 200, 230)},
    "Intermediate": {"bg_top": (20, 15, 45), "bg_bot": (40, 30, 80),  "accent": (180, 120, 255), "text": (245, 240, 255), "subtext": (190, 160, 230)},
    "Advanced":     {"bg_top": (15, 30, 20), "bg_bot": (30, 60, 40),  "accent": (80, 220, 140),  "text": (240, 255, 245), "subtext": (160, 220, 180)},
}

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ─── UPDATED SCRIPT GENERATOR (15-MIN LOGIC) ────────────────────────────────
def generate_edu_slides(client, topic, part1_url):
    """
    Forces the AI to generate deep, 15-minute worth of content.
    Word count requirement: 250-300 words per slide.
    """
    today = datetime.now().strftime("%A, %d %B %Y")
    
    prompt = f"""You are a Master Trading Mentor at ai360trading.in.
    Topic: {topic['title']}. Level: {topic['level']}. Mode: Educational Deep-Dive.
    
    TASK: Generate 8 slides for a 15-MINUTE MASTERCLASS in Hinglish.
    
    STRICT CONTENT RULES (Human Touch & Duration):
    1. WORD COUNT: Each slide 'content' MUST be at least 250-300 words. (Total 2,000+ words).
    2. STRUCTURE: 
       - Start with a real-life analogy (e.g., 'Jaise aap grocery shopping karte hain...').
       - Explain the technical logic deeply.
       - Give a concrete 'Nifty/BankNifty' example for each point.
    3. HUMAN EMOTION: Use 'Doston', 'Mera experience kehta hai', 'Retailers yahan galti karte hain'.
    4. NO AI-SPEAK: Strictly avoid 'In conclusion', 'Moreover', 'Firstly'. Talk like a mentor.
    5. LINKING: Mention that today's Market Analysis (Part 1) shows this concept in action: {part1_url}

    Respond ONLY with valid JSON:
    {{
      "video_title": "Deep Analysis: {topic['title']} (Masterclass)",
      "video_description": "15-minute deep-dive into {topic['title']} for Indian traders...",
      "slides": [
        {{
          "title": "Slide Title",
          "content": "300 words of deep Hinglish mentoring, stories, and examples...",
          "key_takeaway": "The one thing to remember from this slide"
        }}
      ]
    }}"""

    print(f"🤖 Generating 15-Minute Masterclass: {topic['title']}...")
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

# ─── DYNAMIC RENDERER (IMAGE LOGIC) ──────────────────────────────────────────
def make_edu_slide(slide, idx, total, topic, path):
    """Renders high-quality 1080p slides with your custom branding."""
    th = LEVEL_THEMES.get(topic['level'], LEVEL_THEMES["Beginner"])
    img = Image.new("RGB", (W, H))
    px = img.load()
    
    # Render Gradient
    for y in range(H):
        c = lerp(th["bg_top"], th["bg_bot"], y / H)
        for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")
    
    # Drawing Header/Footer accents
    draw.rectangle([(0, 0), (W, 12)], fill=th["accent"]) # Top
    draw.rectangle([(0, H-12), (W, H)], fill=th["accent"]) # Bottom

    # Overlay specific text from your existing font paths
    # (Using the helper logic from your shared code)
    # ... [Title, Content, and Branding logic remains same as your original] ...
    
    img.save(str(path), quality=95)

# ─── UPDATED ASYNC RUNNER ────────────────────────────────────────────────────
async def run_masterclass(client, topic):
    # 1. Fetch Part 1 URL from Artifact Bridge
    part1_url = ""
    id_path = OUT / "analysis_video_id.txt"
    if id_path.exists():
        p1_id = id_path.read_text().strip()
        if p1_id and p1_id != "PENDING_ID":
            part1_url = f"https://youtube.com/watch?v={p1_id}"

    # 2. Generate Deep Content
    data = generate_edu_slides(client, topic, part1_url)
    
    clips = []
    voice_key = "Advanced" if topic['level'] == "Advanced" else "Beginner"
    
    for i, s in enumerate(data['slides']):
        print(f"[PROGRESS] Building Slide {i+1}/8 (Deep Content)...")
        
        img_path = OUT / f"edu_{i}.png"
        aud_path = OUT / f"edu_{i}.mp3"
        
        # Build the Visual
        make_edu_slide(s, i+1, 8, topic, img_path)
        
        # Build the Voice (Longer text = longer duration)
        comm = edge_tts.Communicate(s['content'], VOICES[voice_key])
        await comm.save(str(aud_path))
        
        voice_clip = AudioFileClip(str(aud_path))
        
        # Add background music (7% volume as per your logic)
        # ... [Your existing music mixing logic] ...
        
        slide_clip = ImageClip(str(img_path)).set_duration(voice_clip.duration + 1).set_audio(voice_clip)
        clips.append(slide_clip)

    # 3. Final Render
    print(f"🎥 Rendering 15-Minute Masterclass Video...")
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(str(OUT / "education_video.mp4"), fps=24, codec="libx264")
    
    # 4. YouTube Upload Logic (using your shared helpers)
    # ... [upload_to_youtube calls] ...
