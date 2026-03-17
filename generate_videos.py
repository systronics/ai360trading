import os
import sys
import json
import time
import re
import asyncio
import base64
import requests
from datetime import datetime

# --- Libraries ---
try:
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    from PIL import Image, ImageDraw, ImageFont
    import edge_tts
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from groq import Groq
    LIBS_OK = True
except ImportError:
    LIBS_OK = False

# --- Configuration ---
W, H = 1280, 720
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

now = datetime.now()
date_display = now.strftime("%d %b %Y")
date_str = now.strftime("%Y%m%d")

C = {
    "dark": (10, 15, 30),
    "dark2": (18, 25, 45),
    "white": (245, 245, 250),
    "muted": (160, 170, 190),
    "accent": (52, 152, 219),
    "green": (46, 204, 113),
    "red": (231, 76, 60)
}

# --- Helper Functions ---
def get_font(size, bold=False):
    try:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def clean_text(text):
    return re.sub(r'(SLIDE|NARRATOR|HINDI_SUB|VOICE):', '', text).strip()

# --- Visual Generation ---
def create_professional_slide(heading, body, brand_color, slide_num, total, path):
    img = Image.new("RGB", (W, H), C["dark"])
    draw = ImageDraw.Draw(img)
    
    # Top Bar
    draw.rectangle([0, 0, W, 60], fill=C["dark2"])
    draw.text((40, 15), "AI360TRADING ANALYSIS", fill=brand_color, font=get_font(24, True))
    draw.text((W-40, 15), date_display, fill=C["muted"], font=get_font(20), anchor="ra")

    # Content
    clean_h = clean_text(heading)
    clean_b = clean_text(body)
    
    draw.text((60, 120), clean_h.upper(), fill=C["white"], font=get_font(45, True))
    draw.rectangle([60, 180, 250, 185], fill=brand_color)
    
    # Text Wrap Logic
    y_pos = 240
    words = clean_b.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if draw.textbbox((0,0), test_line, font=get_font(28))[2] < W-120:
            line = test_line
        else:
            draw.text((60, y_pos), line, fill=C["white"], font=get_font(28))
            y_pos += 45
            line = word + " "
    draw.text((60, y_pos), line, fill=C["white"], font=get_font(28))

    # Bottom Progress
    prog_w = int((slide_num/total) * W)
    draw.rectangle([0, H-8, prog_w, H], fill=brand_color)
    img.save(path)

# --- Groq Script Generation ---
def generate_ai_script(topic):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    prompt = f"Create a 4-slide YouTube script for {topic} analysis for {date_display}. For each slide, give a 'heading' and a 'body'. Keep it professional, focused on price levels and market sentiment. Output in JSON format only."
    
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        return json.loads(chat.choices[0].message.content).get("slides", [])
    except:
        return [
            {"heading": "Market Update", "body": "Analyzing current stock trends and key resistance levels for today."},
            {"heading": "Key Levels", "body": "Watch the major support zones closely as volatility remains high."},
            {"heading": "Conclusion", "body": "Subscribe to AI360Trading for daily automated market intelligence."}
        ]

# --- Core Engine ---
async def tts_engine(text, path):
    comm = edge_tts.Communicate(text=clean_text(text), voice="en-IN-PrabhatNeural")
    await comm.save(path)

def build_video(script_data, brand_color, output_path):
    clips = []
    for i, slide in enumerate(script_data):
        img_p = os.path.join(OUTPUT_DIR, f"s_{i}.png")
        aud_p = os.path.join(OUTPUT_DIR, f"s_{i}.mp3")
        
        create_professional_slide(slide['heading'], slide['body'], brand_color, i+1, len(script_data), img_p)
        asyncio.run(tts_engine(slide['body'], aud_p))
        
        audio = AudioFileClip(aud_p)
        clip = ImageClip(img_p).set_duration(audio.duration + 0.5).set_audio(audio)
        clips.append(clip)
        
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

# --- YouTube & GitHub Security (As previously configured) ---
def upload_video(path, title):
    creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
    if not creds_json: return
    cd = json.loads(creds_json)
    creds = Credentials(token=cd['token'], refresh_token=cd['refresh_token'], token_uri="https://oauth2.googleapis.com/token", client_id=cd['client_id'], client_secret=cd['client_secret'])
    if not creds.valid:
        creds.refresh(Request())
        # Add logic to save updated token to GH here
    
    yt = build('youtube', 'v3', credentials=creds)
    request = yt.videos().insert(
        part="snippet,status",
        body={"snippet": {"title": title, "description": "Automated Market Analysis", "categoryId": "27"}, "status": {"privacyStatus": "public"}},
        media_body=MediaFileUpload(path)
    )
    res = request.execute()
    return res.get("id")

def main():
    topic = "Nifty and Top Stocks"
    print(f"🚀 Generating AI-Powered Script for: {topic}")
    script = generate_ai_script(topic)
    
    video_path = os.path.join(OUTPUT_DIR, f"final_{date_str}.mp4")
    build_video(script, C["accent"], video_path)
    
    print("🎥 Video Ready. Uploading...")
    vid_id = upload_video(video_path, f"Market Analysis: {date_display}")
    if vid_id: print(f"🔥 LIVE: https://youtube.com/watch?v={vid_id}")

if __name__ == "__main__":
    main()
