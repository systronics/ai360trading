"""
AI360Trading — Daily Reels Generator
====================================
Features: 9:16 Vertical, Zeno Expression Logic, Looped .mp3 Background Music
This script creates the high-engagement "Manual" look for Instagram/FB Reels.
"""

import os, sys, json, asyncio, textwrap, random
from datetime import datetime
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, afx
from groq import Groq

# --- CONFIGURATION ---
OUT = "output"
W, H = 1080, 1920 # Fixed Reel Resolution
os.makedirs(OUT, exist_ok=True)

# Path to your background music
BG_MUSIC_PATH = "assets/music/trading_vibes.mp3" 

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

FONT_BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
             "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"]
FONT_REG  = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
             "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"]

def font(c, s):
    for p in c:
        if os.path.exists(p): return ImageFont.truetype(p, s)
    return ImageFont.load_default()

def lerp(c1, c2, t): return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

def gbg(top, bot):
    img = Image.new("RGB", (W, H)); px = img.load()
    for y in range(H):
        c = lerp(top, bot, y/H)
        for x in range(W): px[x, y] = c
    return img

# Theme Mapping based on Reel Tone
THEMES = {
    "bullish": {"bg_top":(10,40,20),"bg_bot":(20,80,40),"accent":(0,255,150),"text":(240,255,250)},
    "bearish": {"bg_top":(40,10,10),"bg_bot":(90,20,20),"accent":(255,60,60),"text":(255,245,245)},
    "neutral": {"bg_top":(15,15,35),"bg_bot":(30,30,70),"accent":(0,180,255),"text":(245,250,255)}
}

def get_zeno_overlay(sentiment):
    mapping = {
        "bullish": "zeno_happy.png",
        "bearish": "zeno_sad.png",
        "neutral": "zeno_thinking.png"
    }
    img_name = mapping.get(sentiment.lower(), "zeno_thinking.png")
    full_path = f"public/image/{img_name}"
    if os.path.exists(full_path):
        return Image.open(full_path).convert("RGBA")
    return None

def make_reel_frame(slide, path):
    snt = slide.get("sentiment", "neutral").lower()
    th = THEMES.get(snt, THEMES["neutral"])
    img = gbg(th["bg_top"], th["bg_bot"])
    draw = ImageDraw.Draw(img, "RGBA")
    
    # 1. Top Header (Date & Brand)
    date_str = datetime.now().strftime("%d %b %Y").upper()
    draw.text((W//2, 150), f"AI360TRADING • {date_str}", fill=th["accent"], font=font(FONT_BOLD, 35), anchor="mm")
    
    # 2. Main Title
    f_head = font(FONT_BOLD, 85)
    ty = 350
    for line in textwrap.wrap(slide["title"].upper(), width=15):
        draw.text((W//2, ty), line, fill=th["text"], font=f_head, anchor="mm")
        ty += 100
        
    # 3. Content Text
    f_body = font(FONT_REG, 48)
    ty += 80
    for line in textwrap.wrap(slide["content"], width=28):
        draw.text((W//2, ty), line, fill=th["text"], font=f_body, anchor="mm")
        ty += 65

    # 4. Inject Zeno (The Star of the Reel)
    zeno = get_zeno_overlay(snt)
    if zeno:
        zeno.thumbnail((750, 750), Image.LANCZOS)
        # Positioned slightly higher for Reel visibility
        img.paste(zeno, (W//2 - 375, H - 900), zeno)
        
    # 5. Bottom Call to Action
    draw.rounded_rectangle([(W//2 - 300, H - 200), (W//2 + 300, H - 120)], radius=40, fill=th["accent"])
    draw.text((W//2, H - 160), "CHECK LINK IN BIO", fill=(0,0,0), font=font(FONT_BOLD, 35), anchor="mm")

    img.save(path, quality=95)

async def generate_voice(text, path):
    communicate = edge_tts.Communicate(text, "en-IN-PrabhatNeural")
    await communicate.save(path)

async def run_reels():
    gkey = os.environ.get("GROQ_API_KEY")
    if not gkey: sys.exit("❌ GROQ_API_KEY missing")
    client = Groq(api_key=gkey)

    # Prompt designed for a high-impact single message Reel
    prompt = "Give me one powerful trading insight or market update for today. Title (max 3 words), Content (2 punchy sentences), Sentiment. Return JSON."
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "You are a professional trader. Return JSON only."},
                  {"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    slide = json.loads(completion.choices[0].message.content)
    
    img_p = f"{OUT}/reel_frame.png"
    aud_p = f"{OUT}/reel_voice.mp3"
    
    make_reel_frame(slide, img_p)
    await generate_voice(slide["content"], aud_p)
    
    # --- AUDIO ASSEMBLY ---
    voice_audio = AudioFileClip(aud_p)
    video_duration = voice_audio.duration + 1.5
    
    # Video Clip
    video_clip = ImageClip(img_p).set_duration(video_duration)
    
    # Background Music (.mp3) logic
    if os.path.exists(BG_MUSIC_PATH):
        bg_audio = AudioFileClip(BG_MUSIC_PATH).volumex(0.15) # Set volume to 15%
        # Loop music to match video length
        bg_audio = afx.audio_loop(bg_audio, duration=video_duration)
        # Combine voice and background music
        final_audio = CompositeAudioClip([voice_audio, bg_audio])
    else:
        final_audio = voice_audio
        print("⚠️ Background music not found, using voice only.")

    # Final Render
    final_reel = f"{OUT}/daily_reel.mp4"
    video_clip.set_audio(final_audio).write_videofile(
        final_reel, fps=24, codec="libx264", audio_codec="aac"
    )
    print(f"✅ Reel Complete: {final_reel}")

if __name__ == "__main__":
    asyncio.run(run_reels())
