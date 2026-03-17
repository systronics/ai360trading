import os
import sys
import json
import re
import asyncio
from datetime import datetime
from groq import Groq

# Try-except for all libraries to prevent crashes
try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    import edge_tts
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
except ImportError:
    print("Ensure all libraries from requirements.txt are installed!")

# --- Configuration ---
W, H = 1280, 720
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
DATE_NOW = datetime.now().strftime("%d %b %Y")

THEME = {"bg": (10, 15, 30), "accent": (52, 152, 219), "text": (255, 255, 255), "muted": (160, 170, 190)}

# --- Intelligence Logic (Human Research Style) ---
def get_research_script():
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    prompt = f"Act as a professional market researcher for AI360Trading. Provide a 4-slide technical analysis for {DATE_NOW}. Slides: 1. Sentiment, 2. Nifty Levels, 3. Stock of the Day, 4. Expert Advice. Return JSON only: {{'slides': [{{'title': '', 'content': ''}}]}}"
    try:
        chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-70b-8192", response_format={"type": "json_object"})
        return json.loads(chat.choices[0].message.content)['slides']
    except:
        return [{"title": "Market View", "content": "Analyzing current price action and volume patterns for the Indian market."}]

# --- Visual Engine ---
def make_slide(title, content, idx, total, path):
    img = Image.new("RGB", (W, H), THEME["bg"])
    draw = ImageDraw.Draw(img)
    try:
        f_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        f_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except:
        f_h = f_b = ImageFont.load_default()

    draw.text((60, 140), title.upper(), fill=THEME["text"], font=f_h)
    draw.rectangle([60, 200, 200, 205], fill=THEME["accent"])
    
    # Simple line wrapping
    y, words = 260, content.split()
    line = ""
    for w in words:
        if draw.textbbox((0,0), line + w, font=f_b)[2] < W-120: line += w + " "
        else:
            draw.text((60, y), line, fill=THEME["text"], font=f_b)
            y += 45
            line = w + " "
    draw.text((60, y), line, fill=THEME["text"], font=f_b)
    img.save(path)

# --- Video & Upload Assembly ---
async def create_and_upload():
    slides = get_research_script()
    clips = []
    for i, s in enumerate(slides):
        img_p, aud_p = f"{OUTPUT_DIR}/s{i}.png", f"{OUTPUT_DIR}/s{i}.mp3"
        make_slide(s['title'], s['content'], i+1, len(slides), img_p)
        await edge_tts.Communicate(s['content'], "en-IN-PrabhatNeural").save(aud_p)
        audio = AudioFileClip(aud_p)
        clips.append(ImageClip(img_p).set_duration(audio.duration + 1).set_audio(audio))
    
    video_file = f"{OUTPUT_DIR}/final.mp4"
    concatenate_videoclips(clips, method="compose").write_videofile(video_file, fps=24)
    
    # --- YouTube Logic ---
    creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
    if creds_json:
        cj = json.loads(creds_json)
        creds = Credentials(token=cj['token'], refresh_token=cj['refresh_token'], token_uri="https://oauth2.googleapis.com/token", client_id=cj['client_id'], client_secret=cj['client_secret'])
        if not creds.valid: creds.refresh(Request())
        
        yt = build('youtube', 'v3', credentials=creds)
        yt.videos().insert(part="snippet,status", body={"snippet": {"title": f"Market Research: {DATE_NOW}", "categoryId": "27"}, "status": {"privacyStatus": "public"}}, media_body=MediaFileUpload(video_file)).execute()
        print("🔥 Video is LIVE on YouTube!")

if __name__ == "__main__":
    asyncio.run(create_and_upload())
