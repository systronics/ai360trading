import os
import sys
import json
import time
import re
import math
import random
import asyncio
import base64
import requests
from datetime import datetime
from io import BytesIO

# --- Libraries ---
try:
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import edge_tts
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    LIBS_OK = True
except ImportError:
    LIBS_OK = False

# --- Configuration & Constants ---
W, H = 1280, 720
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

now = datetime.now()
date_display = now.strftime("%d %b %Y")
date_str = now.strftime("%Y%m%d")
weekday = now.weekday()

# Colors for the "TradingView" Professional Look
C = {
    "dark": (10, 15, 30),      # Deep navy background
    "dark2": (18, 25, 45),     # Card/Chart background
    "card": (25, 35, 60),      # Secondary elements
    "accent": (50, 80, 150),   # UI Borders
    "white": (245, 245, 250),
    "muted": (160, 170, 190),  # Text/Labels
    "green": (46, 204, 113),   # Bullish
    "red": (231, 76, 60),      # Bearish
    "gold": (241, 196, 15)
}

TOPICS = [
    {"type": "nifty", "color": (52, 152, 219), "title": "NIFTY ANALYSIS: {direction} | {date}", "desc": "Daily Nifty levels and market view for {date}.", "tags": ["nifty", "trading"]},
    {"type": "stocks", "color": (155, 89, 182), "title": "TOP STOCKS TO WATCH | {date}", "desc": "Key stocks for your watchlist today.", "tags": ["stocks", "investing"]},
    {"type": "education", "color": (46, 204, 113), "title": "TRADING STRATEGY: Master {direction} | {year}", "desc": "Educational guide.", "tags": ["education", "learn"]},
    {"type": "finance", "color": (241, 196, 15), "title": "PERSONAL FINANCE: Wealth Secret {year}", "desc": "Grow your money.", "tags": ["finance", "money"]},
    {"type": "bitcoin", "color": (243, 156, 18), "title": "BITCOIN UPDATE: {direction} | {btc}", "desc": "Crypto analysis.", "tags": ["bitcoin", "crypto"]},
    {"type": "support", "color": (52, 73, 94), "title": "GLOBAL CUES | {date}", "desc": "Global market impact.", "tags": ["sp500", "nifty"]},
    {"type": "weekly", "color": (230, 126, 34), "title": "WEEKLY MARKET RECAP | {date}", "desc": "Weekly summary.", "tags": ["weekly", "market"]}
]

# --- Helper Functions ---
def rgb2f(rgb): return tuple(x/255 for x in rgb)

def get_font(size, bold=False):
    try:
        path = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def clean_text_for_screen(text):
    # This removes NARRATOR:, SLIDE:, etc. so they don't show on screen
    text = re.sub(r'(SLIDE|NARRATOR|HINDI_SUB):', '', text).strip()
    return text

def rounded_rect(draw, x1, y1, x2, y2, r, fill):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=fill)

def gradient_bg(img, c1, c2, vertical=True):
    draw = ImageDraw.Draw(img)
    for i in range(H if vertical else W):
        r = int(c1[0] + (c2[0] - c1[0]) * i / (H if vertical else W))
        g = int(c1[1] + (c2[1] - c1[1]) * i / (H if vertical else W))
        b = int(c1[2] + (c2[2] - c1[2]) * i / (H if vertical else W))
        if vertical: draw.line([(0, i), (W, i)], fill=(r, g, b))
        else: draw.line([(i, 0), (i, H)], fill=(r, g, b))

# --- Visual Components ---
def add_top_bar(draw, color, text=""):
    draw.rectangle([0, 0, W, 48], fill=C["dark2"])
    draw.rectangle([0, 48, W, 52], fill=color)
    draw.text((30, 15), "AI360TRADING", fill=color, font=get_font(18, True))
    draw.text((W-30, 15), text, fill=C["muted"], font=get_font(16), anchor="ra")

def add_bottom_bar(draw):
    draw.rectangle([0, H-40, W, H], fill=C["dark2"])
    draw.text((W//2, H-20), "ai360trading.in | Daily Market Intelligence", fill=C["muted"], font=get_font(14), anchor="mm")

# --- Specific Slide Generators ---
def slide_title(title, subtitle, brand_color, path):
    img = Image.new("RGB", (W, H), C["dark"])
    gradient_bg(img, C["dark"], (15, 30, 60))
    draw = ImageDraw.Draw(img)
    add_top_bar(draw, brand_color, date_display)
    draw.text((W//2, H//2 - 40), title.upper(), fill=C["white"], font=get_font(50, True), anchor="mm")
    draw.text((W//2, H//2 + 40), subtitle, fill=brand_color, font=get_font(30, True), anchor="mm")
    add_bottom_bar(draw)
    img.save(path)

def slide_candlestick_chart(title_label, brand_color, path):
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(rgb2f(C["dark"]))
    ax.set_facecolor(rgb2f(C["dark2"]))
    
    # Generate mock candles for TradingView look
    x = np.arange(25)
    y = np.random.randn(25).cumsum() + 24000
    ax.plot(x, y, color=rgb2f(brand_color), lw=3, alpha=0.8)
    ax.fill_between(x, y, y.min(), color=rgb2f(brand_color), alpha=0.1)
    
    ax.set_title(title_label, color="white", fontsize=20, pad=20)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.tick_params(colors=rgb2f(C["muted"]), labelsize=10)
    for s in ax.spines.values(): s.set_color(rgb2f(C["accent"]))
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close()

def slide_content(heading, body, brand_color, num, total, path):
    img = Image.new("RGB", (W, H), C["dark"])
    draw = ImageDraw.Draw(img)
    add_top_bar(draw, brand_color, f"Slide {num}/{total}")
    
    clean_h = clean_text_for_screen(heading)
    clean_b = clean_text_for_screen(body)
    
    draw.text((60, 100), clean_h, fill=C["white"], font=get_font(40, True))
    draw.rectangle([60, 155, 200, 160], fill=brand_color)
    
    # Wrap and draw body text
    y = 200
    words = clean_b.split()
    line = ""
    for word in words:
        if draw.textbbox((0,0), line + word, font=get_font(24))[2] < W-120:
            line += word + " "
        else:
            draw.text((60, y), line, fill=C["white"], font=get_font(24))
            y += 40
            line = word + " "
    draw.text((60, y), line, fill=C["white"], font=get_font(24))
    
    # Progress Bar
    prog_w = int((num/total) * W)
    draw.rectangle([0, H-5, prog_w, H], fill=brand_color)
    
    add_bottom_bar(draw)
    img.save(path)

# --- Video Engine ---
async def _run_tts(text, path):
    # Strips narrator tags so the AI doesn't say "Narrator says..."
    clean_audio_text = re.sub(r'(SLIDE|NARRATOR|HINDI_SUB):', '', text).strip()
    comm = edge_tts.Communicate(text=clean_audio_text, voice="en-IN-PrabhatNeural")
    await comm.save(path)

def generate_video(slides_data, brand_color, output_filename):
    clips = []
    total = len(slides_data)
    
    for i, s in enumerate(slides_data):
        img_p = os.path.join(OUTPUT_DIR, f"frame_{i}.png")
        aud_p = os.path.join(OUTPUT_DIR, f"voice_{i}.mp3")
        
        # Create image
        if i == 0:
            slide_title(s['heading'], "AI Daily Briefing", brand_color, img_p)
        elif "chart" in s['heading'].lower():
            slide_candlestick_chart(s['heading'], brand_color, img_p)
        else:
            slide_content(s['heading'], s['body'], brand_color, i+1, total, img_p)
        
        # Create audio
        asyncio.run(_run_tts(s['body'], aud_p))
        
        # Combine
        ac = AudioFileClip(aud_p)
        clip = ImageClip(img_p).set_duration(ac.duration + 0.5).set_audio(ac)
        clips.append(clip)
        
    final_video = concatenate_videoclips(clips, method="compose")
    final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    return output_filename

# --- GitHub & YouTube Automation ---
def _save_token_to_github(creds_dict):
    try:
        gh_token = os.environ.get("GH_TOKEN")
        repo = os.environ.get("GITHUB_REPOSITORY")
        if not gh_token or not repo: return
        
        import nacl.encoding, nacl.public
        headers = {"Authorization": f"token {gh_token}", "Accept": "application/vnd.github+json"}
        
        k_resp = requests.get(f"https://api.github.com/repos/{repo}/actions/secrets/public-key", headers=headers).json()
        pub_key = nacl.public.PublicKey(k_resp["key"], nacl.encoding.Base64Encoder)
        sealed_box = nacl.public.SealedBox(pub_key)
        encrypted = base64.b64encode(sealed_box.encrypt(json.dumps(creds_dict).encode())).decode()
        
        requests.put(f"https://api.github.com/repos/{repo}/actions/secrets/YOUTUBE_CREDENTIALS",
                     headers=headers, json={"encrypted_value": encrypted, "key_id": k_resp["key_id"]})
        print("✅ YouTube credentials updated in GitHub Secrets.")
    except Exception as e:
        print(f"Secret Update Error: {e}")

def upload_to_youtube(video_path, title, description, tags):
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json: return None
        cd = json.loads(creds_json)
        
        creds = Credentials(
            token=cd.get("token"), refresh_token=cd.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cd.get("client_id"), client_secret=cd.get("client_secret")
        )
        
        if not creds.valid:
            creds.refresh(Request())
            cd["token"] = creds.token
            _save_token_to_github(cd)
            
        yt = build('youtube', 'v3', credentials=creds)
        body = {
            'snippet': {'title': title[:100], 'description': description, 'tags': tags, 'categoryId': '27'},
            'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}
        }
        
        insert_request = yt.videos().insert(
            part=','.join(body.keys()), body=body,
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
        )
        
        res = insert_request.execute()
        return res.get("id")
    except Exception as e:
        print(f"YouTube Error: {e}")
        return None

# --- Main Entry Point ---
def main():
    if not LIBS_OK:
        print("Critical Error: Missing libraries. Check requirements.txt")
        return

    topic = TOPICS[weekday]
    print(f"🚀 Starting Video Bot: {topic['type'].upper()}")
    
    # Mock script - replace this with your LLM/Groq output
    script_data = [
        {"heading": topic['title'].format(direction="Market View", date=date_display, year=2026, btc="65K"), 
         "body": "NARRATOR: Welcome to AI360Trading. Let's look at the market signals for today."},
        {"heading": "NIFTY Technical Chart", 
         "body": "NARRATOR: The chart shows a strong consolidation pattern near 24,000."},
        {"heading": "Final Thoughts", 
         "body": "NARRATOR: Watch the levels we discussed. Subscribe for more daily analysis."}
    ]
    
    video_file = os.path.join(OUTPUT_DIR, f"final_video_{date_str}.mp4")
    generate_video(script_data, topic["color"], video_file)
    
    print("🎥 Video created. Starting upload...")
    vid_id = upload_to_youtube(video_file, script_data[0]['heading'], topic['desc'], topic['tags'])
    
    if vid_id:
        print(f"🔥 SUCCESS! Video LIVE: https://www.youtube.com/watch?v={vid_id}")
    else:
        print("❌ Upload failed or skipped. Check GitHub Secrets.")

if __name__ == "__main__":
    main()
