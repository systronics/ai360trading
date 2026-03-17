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

# Third-party libraries
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

# ── Configuration & Constants ────────────────────────────────────────────────
W, H = 1280, 720
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

now = datetime.now()
date_display = now.strftime("%d %b %Y")
date_str = now.strftime("%Y%m%d")
weekday = now.weekday()

C = {
    "dark": (10, 15, 30),
    "dark2": (18, 25, 45),
    "card": (25, 35, 60),
    "accent": (50, 80, 150),
    "white": (245, 245, 250),
    "muted": (160, 170, 190),
    "green": (46, 204, 113),
    "red": (231, 76, 60),
    "gold": (241, 196, 15)
}

TOPICS = [
    {"type": "nifty", "color": (52, 152, 219), "title": "NIFTY ANALYSIS: {direction} | {date}", "desc": "Daily Nifty levels and market view for {date}.", "tags": ["nifty", "trading", "stockmarket"]},
    {"type": "stocks", "color": (155, 89, 182), "title": "TOP STOCKS TO WATCH | {date}", "desc": "Key stocks for your watchlist today.", "tags": ["stocks", "investing", "india"]},
    {"type": "education", "color": (46, 204, 113), "title": "TRADING STRATEGY: Master {direction} | {year}", "desc": "Educational guide on trading patterns.", "tags": ["education", "learn", "trading"]},
    {"type": "finance", "color": (241, 196, 15), "title": "PERSONAL FINANCE: Wealth Secret {year}", "desc": "How to grow your money effectively.", "tags": ["finance", "money", "investing"]},
    {"type": "bitcoin", "color": (243, 156, 18), "title": "BITCOIN UPDATE: {direction} | {btc}", "desc": "Crypto market analysis for {date}.", "tags": ["bitcoin", "crypto", "btc"]},
    {"type": "support", "color": (52, 73, 94), "title": "S&P 500 & GLOBAL CUES | {date}", "desc": "Global market impact on Nifty.", "tags": ["globalmarket", "sp500", "nifty"]},
    {"type": "weekly", "color": (230, 126, 34), "title": "WEEKLY MARKET RECAP | {date}", "desc": "What happened this week and what next?", "tags": ["weekly", "marketnews", "analysis"]}
]

def rgb2f(rgb): return tuple(x/255 for x in rgb)

def get_font(size, bold=False):
    try:
        path = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# ── Mock/Helper Data Functions ───────────────────────────────────────────────
def get_prices():
    # In production, replace with real API calls (yfinance/binance)
    return {
        "NIFTY 50": {"price": 24250.5, "pct": 0.85, "display": "24,250 (+0.85%)"},
        "S&P 500": {"price": 5620.1, "pct": -0.12, "display": "5,620 (-0.12%)"},
        "Bitcoin": {"price": 68420.0, "pct": 2.4, "display": "$68,420 (+2.4%)"}
    }

def get_fg(): return 65, "Greed"

def generate_script(topic, prices, fg_val, fg_label):
    # Simulated script generation logic
    return [
        {"slide": "Market Overview", "narrator": "Market aaj bullish dikh raha hai, indicators neutral to greed ki taraf shift ho rahe hain."},
        {"slide": "Nifty Levels", "narrator": "Nifty ke liye 24,100 ek strong support hai. Resistance 24,400 par ban raha hai."},
        {"slide": "Strategy", "narrator": "Wait for a pullback to the 20-period EMA before entering new long positions."}
    ]

def parse_script(script): return script

# ── Visual Components ────────────────────────────────────────────────────────
def new_canvas(): return Image.new("RGB", (W, H), C["dark"]), ImageDraw.Draw(Image.new("RGB", (W, H)))

def gradient_bg(img, c1, c2, vertical=True):
    draw = ImageDraw.Draw(img)
    for i in range(H if vertical else W):
        r = int(c1[0] + (c2[0] - c1[0]) * i / (H if vertical else W))
        g = int(c1[1] + (c2[1] - c1[1]) * i / (H if vertical else W))
        b = int(c1[2] + (c2[2] - c1[2]) * i / (H if vertical else W))
        if vertical: draw.line([(0, i), (W, i)], fill=(r, g, b))
        else: draw.line([(i, 0), (i, H)], fill=(r, g, b))

def rounded_rect(draw, x1, y1, x2, y2, r, fill):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=fill)

def add_top_bar(draw, color, text=""):
    draw.rectangle([0, 0, W, 48], fill=C["dark2"])
    draw.rectangle([0, 48, W, 52], fill=color)
    draw.text((30, 15), "AI360TRADING", fill=color, font=get_font(18, True))
    draw.text((W-30, 15), text, fill=C["muted"], font=get_font(16), anchor="ra")

def add_bottom_bar(draw):
    draw.rectangle([0, H-40, W, H], fill=C["dark2"])
    draw.text((W//2, H-20), "ai360trading.in | Join our Telegram for real-time alerts", 
              fill=C["muted"], font=get_font(14), anchor="mm")

def draw_text_wrapped(draw, text, x, y, max_w, font, fill, spacing=10):
    lines = []
    words = text.split()
    while words:
        line = ''
        while words and draw.textbbox((0,0), line + words[0], font=font)[2] < max_w:
            line += (words.pop(0) + ' ')
        lines.append(line.strip())
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + spacing
    return y

# ── Slide Generation Functions ───────────────────────────────────────────────
def slide_title(title, subtitle, brand_color, path):
    img = Image.new("RGB", (W, H), C["dark"])
    gradient_bg(img, C["dark"], (15, 30, 60))
    draw = ImageDraw.Draw(img)
    add_top_bar(draw, brand_color, date_display)
    draw.text((W//2, H//2 - 40), title.upper(), fill=C["white"], font=get_font(50, True), anchor="mm")
    draw.text((W//2, H//2 + 40), subtitle, fill=brand_color, font=get_font(30, True), anchor="mm")
    add_bottom_bar(draw)
    img.save(path)

def slide_fear_greed(val, label, prices, brand_color, path):
    img = Image.new("RGB", (W, H), C["dark"])
    draw = ImageDraw.Draw(img)
    add_top_bar(draw, brand_color, "MARKET SENTIMENT")
    # Simple Gauge
    draw.arc([W//2-150, 150, W//2+150, 450], start=180, end=360, fill=C["accent"], width=20)
    angle = 180 + (val/100)*180
    draw.text((W//2, 300), f"{val}", fill=C["white"], font=get_font(80, True), anchor="mm")
    draw.text((W//2, 380), label.upper(), fill=brand_color, font=get_font(30, True), anchor="mm")
    add_bottom_bar(draw)
    img.save(path)

def slide_candlestick_chart(prices, title_label, brand_color, path):
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor(rgb2f(C["dark"]))
    ax.set_facecolor(rgb2f(C["dark2"]))
    # Mock data for chart
    x = np.arange(20)
    y = np.random.randn(20).cumsum() + 24000
    ax.plot(x, y, color=rgb2f(brand_color), lw=3)
    ax.fill_between(x, y, y.min(), color=rgb2f(brand_color), alpha=0.1)
    ax.set_title(title_label, color="white", fontsize=20, pad=20)
    ax.tick_params(colors="white")
    for spine in ax.spines.values(): spine.set_color(rgb2f(C["accent"]))
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close()

# ... [Include other slide functions: slide_sr_table, slide_content, slide_education_icon, slide_finance_chart, slide_outro, create_thumbnail] ...
# (Functions remain as provided in your snippet)

# ── TTS & Video Assembly ─────────────────────────────────────────────────────
async def _tts(text, path, voice="en-IN-PrabhatNeural"):
    comm = edge_tts.Communicate(text=text, voice=voice)
    await comm.save(path)

def tts(text, path):
    clean = re.sub(r'[*#]', '', text).strip()
    if len(clean) < 2: return False
    try:
        asyncio.run(_tts(clean, path))
        return os.path.exists(path)
    except: return False

def assemble(slide_paths, narrators, out_path):
    clips = []
    for i, (sp, nar) in enumerate(zip(slide_paths, narrators)):
        ap = os.path.join(OUTPUT_DIR, f"a_{i}.mp3")
        if tts(nar, ap):
            ac = AudioFileClip(ap)
            clip = ImageClip(sp).set_duration(ac.duration + 0.5).set_audio(ac)
            clips.append(clip)
    if not clips: return False
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(out_path, fps=24, codec='libx264', audio_codec='aac', logger=None)
    return True

# ── GitHub Secret updater (CRITICAL) ──────────────────────────────────────────
def _save_token_to_github(cd):
    """Auto-saves refreshed YOUTUBE_CREDENTIALS back to GitHub Secrets"""
    try:
        gh_token = os.environ.get("GH_TOKEN")
        repo = os.environ.get("GITHUB_REPOSITORY")
        if not gh_token or not repo:
            print("  ⚠️ GH_TOKEN or REPO not set — token not saved back.")
            return

        import nacl.encoding, nacl.public
        headers = {"Authorization": f"token {gh_token}", "Accept": "application/vnd.github+json"}

        # Get repo public key
        key_resp = requests.get(f"https://api.github.com/repos/{repo}/actions/secrets/public-key", 
                                headers=headers, timeout=10).json()
        pub_key_b64 = key_resp["key"]
        key_id = key_resp["key_id"]

        # Encrypt new value
        public_key = nacl.public.PublicKey(pub_key_b64, nacl.encoding.Base64Encoder)
        sealed_box = nacl.public.SealedBox(public_key)
        encrypted = sealed_box.encrypt(json.dumps(cd).encode())
        encrypted_b64 = base64.b64encode(encrypted).decode()

        # Push to GitHub
        r = requests.put(f"https://api.github.com/repos/{repo}/actions/secrets/YOUTUBE_CREDENTIALS",
                         headers=headers, json={"encrypted_value": encrypted_b64, "key_id": key_id}, timeout=10)
        
        if r.status_code in (201, 204):
            print("  ✅ YouTube token refreshed and saved to GitHub Secrets.")
    except Exception as e:
        print(f"  ⚠️ Secret update failed: {e}")

# ── YouTube upload (CRITICAL) ─────────────────────────────────────────────────
def upload_yt(video_path, title, description, tags, thumb_path=None):
    try:
        cj = os.environ.get("YOUTUBE_CREDENTIALS")
        if not cj: return None
        cd = json.loads(cj)

        creds = Credentials(
            token=cd.get("token"),
            refresh_token=cd.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cd.get("client_id"),
            client_secret=cd.get("client_secret")
        )

        if not creds.valid:
            print("  Refreshing YouTube token...")
            creds.refresh(Request())
            cd["token"] = creds.token
            _save_token_to_github(cd) # Save new token back to GitHub

        yt = build('youtube', 'v3', credentials=creds)
        body = {
            'snippet': {
                'title': title[:100],
                'description': description,
                'tags': tags,
                'categoryId': '27'
            },
            'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}
        }
        
        req = yt.videos().insert(part=','.join(body.keys()), body=body,
                                 media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True))
        
        resp = None
        while resp is None:
            status, resp = req.next_chunk()
            if status: print(f"  Upload: {int(status.progress()*100)}%")

        vid_id = resp['id']
        if thumb_path and os.path.exists(thumb_path):
            yt.thumbnails().set(videoId=vid_id, media_body=MediaFileUpload(thumb_path)).execute()
        
        return vid_id
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

# ── Main Loop ────────────────────────────────────────────────────────────────
def main():
    if not LIBS_OK: print("Missing libraries"); sys.exit(1)
    
    topic = TOPICS[weekday]
    prices = get_prices()
    fg_val, fg_label = get_fg()
    
    title = topic["title"].format(direction="Recovery", date=date_display, year=now.year, btc="68K")
    desc = topic["desc"].format(date=date_display, year=now.year)
    
    print(f"--- AI360 Bot: Starting {topic['type']} ---")
    
    img_paths = []
    narrators = []
    
    # 1. Title Slide
    p1 = os.path.join(OUTPUT_DIR, "s1.png")
    slide_title(title, "Daily Analysis", topic["color"], p1)
    img_paths.append(p1); narrators.append(f"Welcome to AI360Trading. Today is {date_display} and we are looking at {title}.")
    
    # 2. Chart Slide
    p2 = os.path.join(OUTPUT_DIR, "s2.png")
    slide_candlestick_chart(prices, "NIFTY 50 Trend", topic["color"], p2)
    img_paths.append(p2); narrators.append("Looking at the chart, Nifty is showing strength above the previous support levels.")
    
    # Assemble and Upload
    video_file = os.path.join(OUTPUT_DIR, f"vid_{date_str}.mp4")
    if assemble(img_paths, narrators, video_file):
        vid_id = upload_yt(video_file, title, desc, topic["tags"])
        if vid_id: print(f"SUCCESS: https://www.youtube.com/watch?v={vid_id}")

if __name__ == "__main__":
    main()
