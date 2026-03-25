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
VOICE      = "hi-IN-SwaraNeural"
os.makedirs(OUT, exist_ok=True)

# ─── COLORS & EMOTIONS (Keeping your existing logic) ────────────────────────
COLORS = {
    "bg_dark": (8, 8, 24), "bg_mid": (15, 15, 45), "gold": (255, 200, 50),
    "white": (255, 255, 255), "black": (0, 0, 0), "green": (50, 220, 100),
    "red": (220, 60, 60), "purple": (140, 80, 220), "orange": (255, 140, 30),
}

SENTIMENT_COLORS = {
    "positive": COLORS["green"], "negative": COLORS["red"], "neutral": COLORS["gold"],
    "fearful": COLORS["orange"], "motivated": COLORS["purple"],
}

EMOTION_ARC = {
    "positive":  ["zeno_happy", "zeno_thinking", "zeno_celebrating"],
    "negative":  ["zeno_sad", "zeno_thinking", "zeno_celebrating"],
    "motivated": ["zeno_celebrating", "zeno_happy", "zeno_celebrating"],
    "neutral":   ["zeno_thinking", "zeno_happy", "zeno_celebrating"],
}

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def get_bg_music() -> Path | None:
    day = datetime.now().weekday()
    music_map = {0: "bgmusic1.mp3", 1: "bgmusic2.mp3", 2: "bgmusic3.mp3",
                 3: "bgmusic1.mp3", 4: "bgmusic2.mp3", 5: "bgmusic3.mp3", 6: "bgmusic1.mp3"}
    f = MUSIC_DIR / music_map[day]
    return f if f.exists() else next(MUSIC_DIR.glob("*.mp3"), None)

def get_font(size: int):
    for fp in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
               "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
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
            if dx != 0 or dy != 0: draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0), anchor="mm")
    draw.text((x, y), text, font=font, fill=fill, anchor="mm")

# ─── BUILD FRAME ─────────────────────────────────────────────────────────────
def build_frame(slide: dict, zeno_emotion: str, sentiment: str, segment_idx: int) -> str:
    img = Image.new("RGB", (W, H), COLORS["bg_dark"])
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Gradient BG
    for y in range(H):
        r = int(COLORS["bg_dark"][0] + (COLORS["bg_mid"][0] - COLORS["bg_dark"][0]) * (y/H))
        g = int(COLORS["bg_dark"][1] + (COLORS["bg_mid"][1] - COLORS["bg_dark"][1]) * (y/H))
        b = int(COLORS["bg_dark"][2] + (COLORS["bg_mid"][2] - COLORS["bg_dark"][2]) * (y/H))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    sent_color = SENTIMENT_COLORS.get(sentiment, COLORS["gold"])
    draw.rectangle([(0, 0), (W, 10)], fill=sent_color) # Top accent

    # Brand & Title
    draw_text_outlined(draw, "✨ ai360trading.in", W//2, 60, get_font(38), COLORS["gold"], 2)
    title_lines = wrap_text(slide.get("title", "ZENO").upper(), get_font(72), W-100)
    for i, line in enumerate(title_lines[:2]):
        draw_text_outlined(draw, line, W//2, 140 + (i*85), get_font(72), COLORS["white"], 3)

    # ZENO Image (Centered)
    zeno_path = IMG_DIR / f"{zeno_emotion}.png"
    if zeno_path.exists():
        zeno = Image.open(zeno_path).convert("RGBA")
        zeno.thumbnail((850, 850), Image.LANCZOS)
        img.paste(zeno, ((W - zeno.width)//2, H - zeno.height - 250), zeno)

    # Subtitle Bar
    draw.rectangle([(0, H-220), (W, H)], fill=(0,0,0,180))
    content = [slide.get("hook",""), slide.get("lesson",""), slide.get("cta","")][segment_idx]
    sub_lines = wrap_text(content, get_font(48), W-100)
    for i, line in enumerate(sub_lines[:3]):
        draw_text_outlined(draw, line, W//2, (H-175) + (i*60), get_font(48), COLORS["white"], 2)

    path = str(OUT / f"frame_{segment_idx}.png")
    img.save(path)
    return path

# ─── MAIN ────────────────────────────────────────────────────────────────────
async def run_reel():
    today = datetime.now().strftime("%Y%m%d")
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # 1. Script
    from generate_reel_logic import generate_script # Assuming logic is in main or helper
    slide = generate_script(client) 
    sentiment = slide.get("sentiment", "neutral")
    
    # 2. Voice
    full_text = f"{slide['hook']} {slide['lesson']} {slide['cta']}"
    voice_path = str(OUT / f"voice_{today}.mp3")
    communicate = edge_tts.Communicate(full_text, VOICE)
    await communicate.save(voice_path)
    voice_clip = AudioFileClip(voice_path)
    
    # 3. Frames
    arc = EMOTION_ARC.get(sentiment, EMOTION_ARC["neutral"])
    seg_durs = [voice_clip.duration * 0.2, voice_clip.duration * 0.6, voice_clip.duration * 0.2]
    
    clips = []
    for i, (zeno_img, dur) in enumerate(zip(arc, seg_durs)):
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

    # 5. Render
    reel_output = str(OUT / f"reel_{today}.mp4")
    print(f"🎥 Rendering Final Reel...")
    final_video.write_videofile(
        reel_output,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(OUT/"temp_audio.m4a"),
        remove_temp=True,
        threads=2,
        logger=None
    )
    
    shutil.copy2(reel_output, str(OUT / "daily_reel.mp4"))
    
    # Save Meta for social scripts
    meta = {
        "title": f"{slide['title']} #Shorts",
        "description": f"{slide['description']}\n\n{slide['hashtags']}"
    }
    (OUT / f"meta_{today}.json").write_text(json.dumps(meta, indent=2))
    print(f"✅ DONE: {reel_output}")

if __name__ == "__main__":
    asyncio.run(run_reel())
