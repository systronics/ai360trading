import os
import json
import asyncio
import random
from datetime import datetime
from groq import Groq

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    import edge_tts
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
except ImportError:
    print("CRITICAL: Install requirements: pip install pillow moviepy google-api-python-client edge-tts groq")

# --- Configuration & Assets ---
W, H = 1280, 720
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
DATE_NOW = datetime.now().strftime("%d %b %Y")

# Professional Image Assets from your /public folder
IMG_DIR = "public"
AUTHOR_IMG = os.path.join(IMG_DIR, "person_author.jpg")
CRASH_IMGS = [os.path.join(IMG_DIR, f"person_crash_{i}.jpg") for i in range(1, 5)]
GREEN_IMGS = [os.path.join(IMG_DIR, f"person_green_{i}.jpg") for i in range(1, 4)]

# --- Strategy for 5+ Minute Watch Time ---
# 12 slides at 30 seconds each = 360 seconds (6 Minutes Total)
MIN_SLIDE_DURATION = 30 
TOTAL_REQUIRED_SLIDES = 12 

def get_pro_script():
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    prompt = f"""
    Create a 12-slide high-depth Technical Analysis for {DATE_NOW}.
    Structure: 1.Intro, 2.Nifty Daily, 3.Nifty Hourly, 4.BankNifty, 5.Global Impact, 
    6.FII/DII Data, 7.Stock Pick 1, 8.Stock Pick 2, 9.Stock Pick 3, 10.Support/Resistance, 
    11.Trading Psychology, 12.Final Summary & Subscribe.
    Each content block MUST be at least 5-6 long sentences.
    Return JSON: {{'slides': [{{'title': '', 'content': '', 'sentiment': 'bullish/bearish'}}]}}
    """
    try:
        chat = client.chat.completions.create(
            messages=[{"role":"user","content":prompt}], 
            model="llama3-70b-8192", 
            response_format={"type":"json_object"}
        )
        data = json.loads(chat.choices[0].message.content)['slides']
        return data[:TOTAL_REQUIRED_SLIDES]
    except Exception:
        # Emergency backup to prevent short videos
        return [{"title": f"Market Analysis Part {i+1}", 
                 "content": "Analyzing deep liquidity pockets and order block theory to identify where the big institutions are placing their bets for the upcoming weekly expiry. We are focusing on high-probability setups that offer a minimum 1:3 risk-to-reward ratio for our subscribers.", 
                 "sentiment": "bullish"} for i in range(TOTAL_REQUIRED_SLIDES)]

def make_pro_slide(slide, idx, path):
    # Select background based on market mood
    bg_pool = GREEN_IMGS if slide['sentiment'] == 'bullish' else CRASH_IMGS
    bg_path = random.choice(bg_pool)
    
    img = Image.open(bg_path).convert("RGB") if os.path.exists(bg_path) else Image.new("RGB", (W, H), (10, 20, 40))
    img = ImageOps.fit(img, (W, H))
    
    # Professional Dark Overlay (Glassmorphism effect)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 185))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))
    
    draw = ImageDraw.Draw(img)
    try:
        f_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        f_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
    except: f_h = f_b = ImageFont.load_default()

    # Title & Text
    draw.text((70, 70), f"{idx}. {slide['title'].upper()}", fill=(0, 160, 255), font=f_h)
    
    y, words = 190, slide['content'].split()
    line = ""
    for w in words:
        if draw.textbbox((0,0), line + w, font=f_b)[2] < 1100: line += w + " "
        else:
            draw.text((70, y), line, fill=(255, 255, 255), font=f_b)
            y += 55
            line = w + " "
    draw.text((70, y), line, fill=(255, 255, 255), font=f_b)
    
    # Branding Footer
    draw.text((W-70, H-60), "AI360TRADING RESEARCH", fill=(120, 120, 120), font=f_b, anchor="ra")
    img.save(path)

async def build_6min_production():
    slides = get_pro_script()
    clips = []
    
    print(f"🎬 Starting Production: Generating {len(slides)} High-Depth Slides...")
    for i, s in enumerate(slides):
        img_p, aud_p = f"{OUTPUT_DIR}/slide_{i}.png", f"{OUTPUT_DIR}/slide_{i}.mp3"
        make_pro_slide(s, i+1, img_p)
        
        # Indian-accented professional voice
        await edge_tts.Communicate(s['content'], "en-IN-PrabhatNeural").save(aud_p)
        
        audio = AudioFileClip(aud_p)
        # FORCE LENGTH: Guarantees watch time
        duration = max(audio.duration + 3, MIN_SLIDE_DURATION)
        clips.append(ImageClip(img_p).set_duration(duration).set_audio(audio))
    
    final_video = f"{OUTPUT_DIR}/monetize_full_6min.mp4"
    concatenate_videoclips(clips, method="compose").write_videofile(final_video, fps=24, threads=4)
    print(f"✅ FINAL VIDEO READY: {final_video} (Length: ~6:00)")

if __name__ == "__main__":
    asyncio.run(build_6min_production())
