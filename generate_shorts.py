import os, sys, json, asyncio, textwrap, random
from datetime import datetime
from pathlib import Path

import edge_tts
import yfinance as yf
import pytz
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
from groq import Groq

# ─── CONFIG ──────────────────────────────────────────────────────────────────
IST = pytz.timezone("Asia/Kolkata")
OUT = Path("output")
W, H = 1080, 1920  # Vertical for Shorts/Reels
FPS = 24
VOICE = "hi-IN-SwaraNeural"
os.makedirs(OUT, exist_ok=True)

# ─── THE LOCKER CHECK (Today's Main Change) ──────────────────────────────────
def get_morning_video_id():
    """Checks the 'locker' for the morning video link note."""
    id_file = OUT / "analysis_video_id.txt"
    if id_file.exists():
        v_id = id_file.read_text().strip()
        return f"https://youtube.com/watch?v={v_id}"
    return "https://ai360trading.in" # Fallback to website if no video found

# ─── MARKET DATA ─────────────────────────────────────────────────────────────
def get_midday_data():
    """Fetches real-time price for the mid-day pulse."""
    try:
        ticker = yf.Ticker("^NSEI") # Nifty 50
        df = ticker.history(period="1d", interval="5m")
        if not df.empty:
            current = df['Close'].iloc[-1]
            high = df['High'].max()
            low = df['Low'].min()
            return f"Nifty at {current:.2f} (H: {high:.2f}, L: {low:.2f})"
    except: pass
    return "Market is showing volatile action."

# ─── GROQ SCRIPT GENERATION ──────────────────────────────────────────────────
def generate_short_scripts(client):
    midday_info = get_midday_data()
    morning_link = get_morning_video_id()
    
    prompt = f"""Create 2 Viral Shorts (9:16) in Hinglish.
Mid-day Market Status: {midday_info}
Call to Action: Tell viewers to check the full analysis at {morning_link}

Short 1: Mid-day Trend Setup (Technical)
Short 2: Market Sentiment & Strategy (Psychology)

Respond ONLY with JSON:
{{
  "shorts": [
    {{
      "title": "Viral Title",
      "content": "40-50 words fast-paced Hinglish script",
      "description": "Viral description with tags and this link: {morning_link}"
    }}
  ]
}}"""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

# ─── RENDERER ────────────────────────────────────────────────────────────────
def make_vertical_slide(text, title, path):
    img = Image.new("RGB", (W, H), (10, 20, 30)) # Dark Blue Pro Theme
    draw = ImageDraw.Draw(img)
    
    # Simple Pro Layout
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        font_content = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
    except:
        font_title = font_content = ImageFont.load_default()

    # Draw Title
    draw.text((W//2, 300), title.upper(), fill=(0, 255, 150), font=font_title, anchor="mm")
    
    # Draw Wrapped Content
    lines = textwrap.wrap(text, width=25)
    y = 600
    for line in lines:
        draw.text((W//2, y), line, fill=(255, 255, 255), font=font_content, anchor="mm")
        y += 80
        
    img.save(str(path))

async def run():
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    data = generate_short_scripts(client)
    
    for idx, s in enumerate(data["shorts"]):
        img_p = OUT/f"short_v_{idx}.png"
        aud_p = OUT/f"short_v_{idx}.mp3"
        out_p = OUT/f"short{idx+2}_final.mp4" # Named short2 and short3 for your workflow
        
        make_vertical_slide(s["content"], s["title"], img_p)
        await edge_tts.Communicate(s["content"], VOICE).save(str(aud_p))
        
        audio = AudioFileClip(str(aud_p))
        clip = ImageClip(str(img_p)).set_duration(audio.duration).set_audio(audio)
        clip.write_videofile(str(out_p), fps=FPS, codec="libx264")
        
        # Save SEO metadata for the uploader
        (OUT / f"short{idx+2}_meta.txt").write_text(s["description"])

    print("✅ Mid-day Shorts with Morning Links are ready!")

if __name__ == "__main__":
    asyncio.run(run())
