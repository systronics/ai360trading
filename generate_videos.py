import os
import json
import asyncio
import random
from datetime import datetime
from groq import Groq

try:
    import numpy as np
    import matplotlib.pyplot as plt
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    import edge_tts
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
except ImportError:
    print("Ensure matplotlib, pillow, and moviepy are in requirements.txt")

# --- Configuration ---
W, H = 1280, 720
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
DATE_NOW = datetime.now().strftime("%d %b %Y")

# Path to your professional images
IMG_DIR = "public" 
AUTHOR_IMG = os.path.join(IMG_DIR, "person_author.jpg")
CRASH_IMGS = [os.path.join(IMG_DIR, f"person_crash_{i}.jpg") for i in range(1, 4)]
GREEN_IMGS = [os.path.join(IMG_DIR, f"person_green_{i}.jpg") for i in range(1, 4)]

THEME = {
    "bg": (10, 15, 30),
    "panel": (20, 30, 50, 180), # Semi-transparent
    "accent": (0, 150, 255),
    "text": (255, 255, 255),
    "gold": (255, 215, 0)
}

# --- Research Logic ---
def get_monetization_script():
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    prompt = f"""
    Create a 10-slide high-retention YouTube script for {DATE_NOW}.
    Include technical levels for Nifty/BankNifty and 3 breakout stocks.
    Slides MUST include engagement hooks like 'Subscribe for daily wealth alerts'.
    Return JSON: {{'slides': [{{'title': '', 'content': '', 'sentiment': 'bullish/bearish'}}]}}
    """
    try:
        chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192", response_format={"type":"json_object"})
        return json.loads(chat.choices[0].message.content)['slides']
    except:
        return [{"title": "Market Alpha", "content": "Analyzing key breakout patterns for today's session.", "sentiment": "bullish"}] * 10

# --- Visual Engine ---
def make_engagement_slide(slide, idx, total, path):
    img = Image.new("RGB", (W, H), THEME["bg"])
    
    # Pick a relevant professional photo based on sentiment
    photo_list = GREEN_IMGS if slide['sentiment'] == 'bullish' else CRASH_IMGS
    bg_photo_path = random.choice(photo_list)
    
    if os.path.exists(bg_photo_path):
        bg_img = Image.open(bg_photo_path).convert("RGBA")
        bg_img = ImageOps.fit(bg_img, (W, H))
        # Darken the photo so text is readable
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 150))
        img = Image.alpha_composite(bg_img, overlay).convert("RGB")

    draw = ImageDraw.Draw(img)
    try:
        f_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)
        f_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except: f_h = f_b = ImageFont.load_default()

    # Glassmorphism Text Box
    draw.rectangle([50, 100, 750, 620], fill=(0, 0, 0, 100), outline=THEME["accent"], width=3)
    draw.text((80, 130), slide['title'].upper(), fill=THEME["gold"], font=f_h)
    
    y, words = 220, slide['content'].split()
    line = ""
    for w in words:
        if draw.textbbox((0,0), line + w, font=f_b)[2] < 620: line += w + " "
        else:
            draw.text((80, y), line, fill=THEME["text"], font=f_b)
            y += 55
            line = w + " "
    draw.text((80, y), line, fill=THEME["text"], font=f_b)
    
    img.save(path)

def create_pro_thumbnail():
    thumb = Image.new("RGB", (W, H), (15, 25, 45))
    if os.path.exists(AUTHOR_IMG):
        author = Image.open(AUTHOR_IMG).convert("RGBA")
        author = ImageOps.fit(author, (600, 720))
        thumb.paste(author, (680, 0), author if "A" in author.getbands() else None)
    
    draw = ImageDraw.Draw(thumb)
    try: f_l = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
    except: f_l = ImageFont.load_default()
    
    draw.text((50, 150), "URGENT\nMARKET\nLEVELS", fill=THEME["gold"], font=f_l)
    p = f"{OUTPUT_DIR}/thumbnail.jpg"
    thumb.save(p)
    return p

# --- Automation Pipeline ---
async def build_monetization_video():
    slides = get_monetization_script()
    clips = []
    for i, s in enumerate(slides):
        img_p, aud_p = f"{OUTPUT_DIR}/f_{i}.png", f"{OUTPUT_DIR}/f_{i}.mp3"
        make_engagement_slide(s, i+1, len(slides), img_p)
        await edge_tts.Communicate(s['content'], "en-IN-PrabhatNeural").save(aud_p)
        audio = AudioFileClip(aud_p)
        clips.append(ImageClip(img_p).set_duration(audio.duration + 1).set_audio(audio))
    
    v_path = f"{OUTPUT_DIR}/monetize_ready.mp4"
    concatenate_videoclips(clips, method="compose").write_videofile(v_path, fps=24)
    t_path = create_pro_thumbnail()
    
    # YouTube Upload Logic
    creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
    if creds_json:
        cj = json.loads(creds_json)
        creds = Credentials(token=cj['token'], refresh_token=cj['refresh_token'], token_uri="https://oauth2.googleapis.com/token", client_id=cj['client_id'], client_secret=cj['client_secret'])
        if not creds.valid: creds.refresh(Request())
        yt = build('youtube', 'v3', credentials=creds)
        res = yt.videos().insert(part="snippet,status", body={"snippet": {"title": f"Live Market Research: {DATE_NOW}", "categoryId": "27"}, "status": {"privacyStatus": "public"}}, media_body=MediaFileUpload(v_path)).execute()
        yt.thumbnails().set(videoId=res['id'], media_body=MediaFileUpload(t_path)).execute()
        print(f"✅ Production Finished! Video LIVE: https://youtube.com/watch?v={res['id']}")

if __name__ == "__main__":
    asyncio.run(build_monetization_video())
