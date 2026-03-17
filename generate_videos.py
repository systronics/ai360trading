import os
import json
import asyncio
import random
from datetime import datetime
from groq import Groq
from PIL import Image, ImageDraw, ImageFont, ImageOps
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# YouTube API Imports
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# --- 1. CONFIG & ASSETS ---
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
IMG_DIR = "public"
GREEN_IMGS = [os.path.join(IMG_DIR, f"person_green_{i}.jpg") for i in range(1, 4)]
CRASH_IMGS = [os.path.join(IMG_DIR, f"person_crash_{i}.jpg") for i in range(1, 5)]

# --- 2. YOUTUBE UPLOADER ---
def upload_to_youtube(video_path, title):
    try:
        creds = Credentials.from_authorized_user_file('token.json')
        youtube = build('youtube', 'v3', credentials=creds)
        
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": "Daily Technical Analysis by AI360Trading #Nifty",
                    "categoryId": "27"
                },
                "status": {"privacyStatus": "public"}
            },
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
        )
        response = request.execute()
        print(f"\n✅ VIDEO LIVE: https://www.youtube.com/watch?v={response['id']}\n")
    except Exception as e:
        print(f"❌ YouTube Error: {e}")

# --- 3. PRO SLIDE GENERATOR ---
def make_pro_slide(slide, idx, path):
    bg_pool = GREEN_IMGS if slide.get('sentiment') == 'bullish' else CRASH_IMGS
    bg_path = random.choice(bg_pool)
    
    img = Image.open(bg_path).convert("RGB") if os.path.exists(bg_path) else Image.new("RGB", (1280, 720), (20, 20, 20))
    img = ImageOps.fit(img, (1280, 720))
    
    overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 195))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))
    
    draw = ImageDraw.Draw(img)
    try:
        f_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
        f_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except: f_h = f_b = ImageFont.load_default()

    draw.text((60, 60), f"{idx}. {slide['title'].upper()}", fill=(0, 180, 255), font=f_h)
    
    y, words = 170, slide['content'].split()
    line = ""
    for w in words:
        if draw.textbbox((0,0), line + w, font=f_b)[2] < 1100: line += w + " "
        else:
            draw.text((60, y), line, fill=(255, 255, 255), font=f_b)
            y += 50
            line = w + " "
    draw.text((60, y), line, fill=(255, 255, 255), font=f_b)
    img.save(path)

# --- 4. ENGINE ---
async def run_bot():
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Model updated to llama-3.3-70b-versatile to fix decommissioning error
    prompt = "Create a 12-slide market analysis JSON. Each content piece must be 5 sentences. JSON: {'slides': [{'title': '', 'content': '', 'sentiment': 'bullish'}]}"
    
    try:
        chat = client.chat.completions.create(
            messages=[{"role":"user","content":prompt}], 
            model="llama-3.3-70b-versatile", 
            response_format={"type":"json_object"}
        )
        slides = json.loads(chat.choices[0].message.content)['slides']
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return

    clips = []
    print(f"🎬 Creating 5+ minute video...")
    
    for i, s in enumerate(slides):
        img_p, aud_p = f"{OUTPUT_DIR}/s{i}.png", f"{OUTPUT_DIR}/s{i}.mp3"
        make_pro_slide(s, i+1, img_p)
        await edge_tts.Communicate(s['content'], "en-IN-PrabhatNeural").save(aud_p)
        
        audio = AudioFileClip(aud_p)
        # 12 slides * 26s = 312s (5.2 mins)
        duration = max(audio.duration + 2, 26)
        clips.append(ImageClip(img_p).set_duration(duration).set_audio(audio))

    final_v = f"{OUTPUT_DIR}/final_video.mp4"
    # logger=None stops the massive log output
    concatenate_videoclips(clips, method="compose").write_videofile(final_v, fps=24, logger=None)
    
    title = f"NIFTY Technical Analysis | {datetime.now().strftime('%d %b %Y')}"
    upload_to_youtube(final_v, title)

if __name__ == "__main__":
    asyncio.run(run_bot())
