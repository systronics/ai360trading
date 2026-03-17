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

# --- Config ---
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
IMG_DIR = "public"
# Using your professional assets from the /public folder
GREEN_IMGS = [os.path.join(IMG_DIR, f"person_green_{i}.jpg") for i in range(1, 4)]
CRASH_IMGS = [os.path.join(IMG_DIR, f"person_crash_{i}.jpg") for i in range(1, 5)]

# --- YouTube Uploader ---
def upload_to_youtube(video_path, title):
    # This uses your existing credentials setup
    creds = Credentials.from_authorized_user_file('token.json')
    youtube = build('youtube', 'v3', credentials=creds)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": "Daily Market Analysis by AI360Trading",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )
    response = request.execute()
    print(f"✅ VIDEO LIVE: https://www.youtube.com/watch?v={response['id']}")

# --- Slide Creator ---
def make_pro_slide(slide, idx, path):
    bg_path = random.choice(GREEN_IMGS if slide['sentiment'] == 'bullish' else CRASH_IMGS)
    img = Image.open(bg_path).convert("RGB") if os.path.exists(bg_path) else Image.new("RGB", (1280, 720), (20, 20, 20))
    img = ImageOps.fit(img, (1280, 720))
    
    overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 180))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))
    
    draw = ImageDraw.Draw(img)
    try:
        f_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        f_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except: f_h = f_b = ImageFont.load_default()

    draw.text((60, 60), f"{idx}. {slide['title'].upper()}", fill=(255, 215, 0), font=f_h)
    
    y, words = 160, slide['content'].split()
    line = ""
    for w in words:
        if draw.textbbox((0,0), line + w, font=f_b)[2] < 1100: line += w + " "
        else:
            draw.text((60, y), line, fill=(255, 255, 255), font=f_b)
            y += 50
            line = w + " "
    draw.text((60, y), line, fill=(255, 255, 255), font=f_b)
    img.save(path)

# --- Main Engine ---
async def run_bot():
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    # We ask for 12 slides to guarantee 5+ minutes
    prompt = "Create a 12-slide market analysis JSON: {'slides': [{'title': '', 'content': '4-5 sentences', 'sentiment': 'bullish'}]}"
    chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192", response_format={"type":"json_object"})
    slides = json.loads(chat.choices[0].message.content)['slides']

    clips = []
    print("🎬 Generating 5+ Minute Video...")
    for i, s in enumerate(slides):
        img_p, aud_p = f"{OUTPUT_DIR}/s{i}.png", f"{OUTPUT_DIR}/s{i}.mp3"
        make_pro_slide(s, i+1, img_p)
        await edge_tts.Communicate(s['content'], "en-IN-PrabhatNeural").save(aud_p)
        
        audio = AudioFileClip(aud_p)
        # Force each slide to be at least 26 seconds (12 slides * 26s = 312 seconds / 5.2 mins)
        duration = max(audio.duration + 2, 26)
        clips.append(ImageClip(img_p).set_duration(duration).set_audio(audio))

    final_v = f"{OUTPUT_DIR}/final.mp4"
    # logger=None hides those 573 lines of text
    concatenate_videoclips(clips, method="compose").write_videofile(final_v, fps=24, logger=None)
    
    title = f"NIFTY Analysis - {datetime.now().strftime('%d %b')}"
    upload_to_youtube(final_v, title)

if __name__ == "__main__":
    asyncio.run(run_bot())
