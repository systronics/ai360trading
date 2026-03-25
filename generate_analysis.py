"""
AI360Trading — Part 1: Market Analysis Video
===========================================
Generates Daily Market Analysis (16:9) and Shorts (9:16)
Features: Zeno character injection for Shorts, Dynamic Sentiment Colors
"""

import os, sys, json, asyncio, textwrap, re, random
from datetime import datetime
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from groq import Groq

# --- CONFIGURATION & ENV DETECTION ---
OUT = "output"
os.makedirs(OUT, exist_ok=True)

# Detect if the script is being called for a Short (9:16) or Video (16:9)
IS_SHORT = os.environ.get("VIDEO_TYPE") == "SHORT"
W, H = (1080, 1920) if IS_SHORT else (1920, 1080)

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

# Font Paths (Standard Linux/GitHub Actions paths)
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

# Theme Mapping based on Sentiment
AT = {
    "bullish": {"bg_top":(5,30,15),"bg_bot":(10,60,30),"accent":(0,255,130),"text":(235,255,245)},
    "bearish": {"bg_top":(35,10,10),"bg_bot":(70,20,20),"accent":(255,50,50),"text":(255,240,240)},
    "neutral": {"bg_top":(10,20,35),"bg_bot":(20,40,70),"accent":(0,180,255),"text":(240,250,255)}
}

def get_zeno_overlay(sentiment):
    """Fetches Zeno PNG based on market sentiment"""
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

def make_slide(slide, idx, total, path):
    snt = slide.get("sentiment", "neutral").lower()
    th = AT.get(snt, AT["neutral"])
    img = gbg(th["bg_top"], th["bg_bot"])
    draw = ImageDraw.Draw(img, "RGBA")
    
    if IS_SHORT:
        # --- VERTICAL SHORT LAYOUT (Zeno Logic) ---
        draw.rectangle([(0,0),(W,12)], fill=th["accent"])
        
        # Heading
        f_head = font(FONT_BOLD, 70)
        ty = 250
        for line in textwrap.wrap(slide["title"].upper(), width=18):
            draw.text((W//2, ty), line, fill=th["text"], font=f_head, anchor="mm")
            ty += 85
            
        # Body Content
        f_body = font(FONT_REG, 45)
        ty += 60
        clean_content = slide["content"].split(".")[0] + "." # Keep it punchy for Shorts
        for line in textwrap.wrap(clean_content, width=30):
            draw.text((W//2, ty), line, fill=th["text"], font=f_body, anchor="mm")
            ty += 60

        # Inject Zeno Character
        zeno = get_zeno_overlay(snt)
        if zeno:
            zeno.thumbnail((650, 650), Image.LANCZOS)
            # Positioned at bottom center
            img.paste(zeno, (W//2 - 325, H - 850), zeno)
            
        # Watermark
        draw.text((W//2, H-120), "ai360trading.in", fill=(255,255,255,120), font=font(FONT_REG, 30), anchor="mm")

    else:
        # --- ORIGINAL 16:9 LANDSCAPE LAYOUT ---
        draw.rectangle([(0,0),(W,10)], fill=th["accent"])
        draw.text((80, 100), slide["title"].upper(), fill=th["text"], font=font(FONT_BOLD, 65))
        draw.rectangle([(80, 180), (600, 188)], fill=th["accent"])
        
        ty = 280
        for line in textwrap.wrap(slide["content"], width=50):
            draw.text((80, ty), line, fill=th["text"], font=font(FONT_REG, 35))
            ty += 55
            
        # Progress bar for long videos
        prog_w = int((W - 160) * (idx / total))
        draw.rectangle([(80, H-100), (W-80, H-90)], fill=(255,255,255,40))
        draw.rectangle([(80, H-100), (80+prog_w, H-90)], fill=th["accent"])

    img.save(path, quality=95)

async def tts(text, path):
    """Generate voiceover using Edge-TTS"""
    communicate = edge_tts.Communicate(text, "en-IN-PrabhatNeural")
    await communicate.save(path)

async def run_analysis():
    gkey = os.environ.get("GROQ_API_KEY")
    if not gkey: sys.exit("❌ GROQ_API_KEY missing")
    client = Groq(api_key=gkey)

    # Simplified Prompt for Daily Market Analysis
    prompt = "Analyze Nifty, BankNifty and top 3 Global Stocks. Provide 5 slides with 'title', 'content', and 'sentiment' (bullish/bearish/neutral). Return JSON."
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "You are a financial analyst. Return JSON only."},
                  {"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    data = json.loads(completion.choices[0].message.content)
    slides = data.get("slides", [])
    
    clips = []
    for i, s in enumerate(slides):
        img_p = f"{OUT}/frame_{i}.png"
        aud_p = f"{OUT}/voice_{i}.mp3"
        
        make_slide(s, i+1, len(slides), img_p)
        await tts(s["content"], aud_p)
        
        audio = AudioFileClip(aud_p)
        clip = ImageClip(img_p).set_duration(audio.duration + 1).set_audio(audio)
        clips.append(clip)
        print(f"✓ Rendered Slide {i+1}")

    final_video = f"{OUT}/analysis_video.mp4"
    concatenate_videoclips(clips, method="compose").write_videofile(
        final_video, fps=24, codec="libx264", audio_codec="aac"
    )
    print(f"✅ Video Complete: {final_video}")

if __name__ == "__main__":
    asyncio.run(run_analysis())
