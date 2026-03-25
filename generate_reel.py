import os
import sys
import json
import asyncio
import random
import shutil
import numpy as np
from datetime import datetime
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip,
    concatenate_videoclips, VideoFileClip, concatenate_audioclips
)
from groq import Groq

# ─── CONFIG ──────────────────────────────────────────────────────────────────
W, H       = 1080, 1920
FPS        = 24
OUT        = Path("output")
IMG_DIR    = Path("public/image")
MUSIC_DIR  = Path("public/music")
VOICE      = "hi-IN-SwaraNeural"  # Zeno's Voice
os.makedirs(OUT, exist_ok=True)

# ─── COLORS & EMOTIONS ───────────────────────────────────────────────────────
COLORS = {
    "bg_dark": (8, 8, 24), "bg_mid": (15, 15, 45), "gold": (255, 200, 50),
    "white": (255, 255, 255), "black": (0, 0, 0), "green": (50, 220, 100),
    "red": (220, 60, 60), "purple": (140, 80, 220), "orange": (255, 140, 30),
}

SENTIMENT_COLORS = {
    "positive": COLORS["green"], "negative": COLORS["red"], "neutral": COLORS["gold"],
    "fearful": COLORS["orange"], "motivated": COLORS["purple"], "greedy": COLORS["orange"], "angry": COLORS["red"]
}

EMOTION_ARC = {
    "positive":  ["zeno_happy", "zeno_thinking", "zeno_celebrating"],
    "negative":  ["zeno_sad", "zeno_thinking", "zeno_celebrating"],
    "fearful":   ["zeno_fear", "zeno_thinking", "zeno_celebrating"],
    "motivated": ["zeno_celebrating", "zeno_happy", "zeno_celebrating"],
    "greedy":    ["zeno_greed", "zeno_thinking", "zeno_celebrating"],
    "angry":     ["zeno_angry", "zeno_thinking", "zeno_celebrating"],
    "neutral":   ["zeno_thinking", "zeno_happy", "zeno_celebrating"],
}

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def is_weekend() -> bool:
    return datetime.now().weekday() >= 5

def get_bg_music() -> Path | None:
    day = datetime.now().weekday()
    music_map = {0: "bgmusic1.mp3", 1: "bgmusic2.mp3", 2: "bgmusic3.mp3",
                 3: "bgmusic1.mp3", 4: "bgmusic2.mp3", 5: "bgmusic3.mp3", 6: "bgmusic1.mp3"}
    f = MUSIC_DIR / music_map[day]
    if f.exists(): return f
    return next(MUSIC_DIR.glob("*.mp3"), None)

def get_font(size: int):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp): return ImageFont.truetype(fp, size)
    return ImageFont.load_default()

def wrap_text(text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        if font.getbbox(test)[2] <= max_width: current = test
        else:
            if current: lines.append(current)
            current = word
    if current: lines.append(current)
    return lines

def draw_text_outlined(draw, text, x, y, font, fill, outline_width=3):
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0: 
                draw.text((x + dx, y + dy), text, font=font, fill=COLORS["black"], anchor="mm")
    draw.text((x, y), text, font=font, fill=fill, anchor="mm")

# ─── SCRIPT GENERATION ───────────────────────────────────────────────────────
def generate_script(client: Groq) -> dict:
    today = datetime.now().strftime("%A, %d %B %Y")
    weekend = is_weekend()
    topic_hint = "life lesson about money/patience" if weekend else "trading psychology/market sentiment"

    prompt = f"""You are ZENO — a wise, friendly kid character. Create a 60-second Hinglish reel script on: {topic_hint}.
    STRICT JSON ONLY:
    {{
      "title": "catchy title (max 8 words)",
      "hook": "attention grabber (20 words)",
      "lesson": "main teaching (90-100 words)",
      "cta": "closing call to action (20 words)",
      "description": "YouTube description in Hinglish",
      "sentiment": "positive/negative/motivated/neutral/fearful/greedy/angry",
      "hashtags": "#ZenoKiBaat #ai360trading #StockMarketIndia"
    }}
    Rules: Natural Hinglish. Total word count: 130-150 words."""

    print("🤖 Generating timed Hinglish script via Groq...")
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.8
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        print(f"⚠️ Groq error: {e}")
        return {
            "title": "Market Ka Asli Sach",
            "hook": "Kya aapko pata hai ki 90% traders fail kyun hote hain?",
            "lesson": "Trading sirf graphs dekhna nahi hai. Yeh apne emotions ko control karne ka game hai. ZENO kehta hai: emotions ko side mein rakho aur setup pe trust karo.",
            "cta": "Follow ai360trading for daily wisdom!",
            "sentiment": "motivated",
            "description": "ZENO explains trading discipline.",
            "hashtags": "#ZenoKiBaat #ai360trading"
        }

# ─── BUILD FRAME ─────────────────────────────────────────────────────────────
def build_frame(slide: dict, zeno_emotion: str, sentiment: str, segment_idx: int) -> str:
    img = Image.new("RGB", (W, H), COLORS["bg_dark"])
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Gradient Background
    for y in range(H):
        r = int(COLORS["bg_dark"][0] + (COLORS["bg_mid"][0] - COLORS["bg_dark"][0]) * (y/H))
        g = int(COLORS["bg_dark"][1] + (COLORS["bg_mid"][1] - COLORS["bg_dark"][1]) * (y/H))
        b = int(COLORS["bg_dark"][2] + (COLORS["bg_mid"][2] - COLORS["bg_dark"][2]) * (y/H))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    sent_color = SENTIMENT_COLORS.get(sentiment, COLORS["gold"])
    draw.rectangle([(0, 0), (W, 10)], fill=sent_color)

    # Brand Tag
    draw_text_outlined(draw, "✨ ai360trading.in", W//2, 60, get_font(38), COLORS["gold"], 2)

    # Title
    title_lines = wrap_text(slide.get("title", "").upper(), get_font(72), W-100)
    for i, line in enumerate(title_lines[:2]):
        draw_text_outlined(draw, line, W//2, 140 + (i*85), get_font(72), COLORS["white"], 3)

    # ZENO Character
    zeno_path = IMG_DIR / f"{zeno_emotion}.png"
    if not zeno_path.exists(): zeno_path = IMG_DIR / "zeno_happy.png"
    if zeno_path.exists():
        zeno = Image.open(zeno_path).convert("RGBA")
        zeno.thumbnail((850, 850), Image.LANCZOS)
        img.paste(zeno, ((W - zeno.width)//2, H - zeno.height - 250), zeno)

    # Subtitle Bar
    draw.rectangle([(0, H-240), (W, H)], fill=(0,0,0,190))
    content = [slide.get("hook",""), slide.get("lesson",""), slide.get("cta","")][segment_idx]
    sub_lines = wrap_text(content, get_font(48), W-100)
    for i, line in enumerate(sub_lines[:3]):
        draw_text_outlined(draw, line, W//2, (H-180) + (i*65), get_font(48), COLORS["white"], 2)

    path = str(OUT / f"frame_{segment_idx}.png")
    img.save(path)
    return path

# ─── MAIN ────────────────────────────────────────────────────────────────────
async def run_reel():
    today = datetime.now().strftime("%Y%m%d")
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # 1. Generate Script
    slide = generate_script(client)
    sentiment = slide.get("sentiment", "neutral")
    
    # 2. Generate Voice
    full_text = f"{slide['hook']} {slide['lesson']} {slide['cta']}"
    voice_path = str(OUT / f"voice_{today}.mp3")
    await edge_tts.Communicate(full_text, VOICE).save(voice_path)
    voice_clip = AudioFileClip(voice_path)
    
    # 3. Create Video Segments (No Ken Burns = No Crash)
    arc = EMOTION_ARC.get(sentiment, EMOTION_ARC["neutral"])
    durations = [voice_clip.duration * 0.15, voice_clip.duration * 0.70, voice_clip.duration * 0.15]
    
    clips = []
    for i, (zeno_img, dur) in enumerate(zip(arc, durations)):
        frame_path = build_frame(slide, zeno_img, sentiment, i)
        clips.append(ImageClip(frame_path).set_duration(dur))

    # 4. Final Assembly
    final_video = concatenate_videoclips(clips, method="compose")
    
    # Background Music
    bg_path = get_bg_music()
    if bg_path:
        bg = AudioFileClip(str(bg_path)).volumex(0.08)
        if bg.duration < voice_clip.duration:
            bg = concatenate_audioclips([bg] * (int(voice_clip.duration/bg.duration)+1))
        bg = bg.subclip(0, voice_clip.duration)
        final_audio = CompositeAudioClip([voice_clip, bg])
    else:
        final_audio = voice_clip

    final_video = final_video.set_audio(final_audio)

    # 5. Export (Optimized for GitHub Runner)
    reel_output = str(OUT / f"reel_{today}.mp4")
    print(f"🎥 Rendering Final Reel...")
    final_video.write_videofile(
        reel_output,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(OUT / "temp_audio.m4a"),
        remove_temp=True,
        threads=2, # Safe for Runner
        logger=None
    )
    
    shutil.copy2(reel_output, str(OUT / "daily_reel.mp4"))
    
    # Save Meta
    meta = {"title": f"{slide['title']} #Shorts", "description": f"{slide['description']}\n\n{slide['hashtags']}"}
    (OUT / f"meta_{today}.json").write_text(json.dumps(meta, indent=2))
    print(f"✅ DONE: {reel_output}")

if __name__ == "__main__":
    asyncio.run(run_reel())
