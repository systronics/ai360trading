import os, sys, json, asyncio, textwrap, random
from datetime import datetime
from pathlib import Path

import edge_tts
import yfinance as yf
import pytz
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, concatenate_audioclips
from groq import Groq

# YouTube upload
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── CONFIG ──────────────────────────────────────────────────────────────────
IST = pytz.timezone("Asia/Kolkata")
OUT       = Path("output")
MUSIC_DIR = Path("public/music")
W, H      = 1920, 1080   # Horizontal — full YouTube video
FPS       = 24
VOICE     = "hi-IN-SwaraNeural"   # Hinglish female voice
os.makedirs(OUT, exist_ok=True)

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

# ─── FONTS ───────────────────────────────────────────────────────────────────
FONT_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
]
FONT_REG_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

# ─── THEME ───────────────────────────────────────────────────────────────────
THEMES = {
    "bullish": {
        "bg_top": (5, 30, 15), "bg_bot": (10, 60, 30),
        "accent": (0, 220, 110), "text": (235, 255, 245),
        "subtext": (160, 220, 180), "bar": (0, 180, 90)
    },
    "bearish": {
        "bg_top": (35, 10, 10), "bg_bot": (70, 20, 20),
        "accent": (255, 60, 60), "text": (255, 240, 240),
        "subtext": (220, 160, 160), "bar": (200, 40, 40)
    },
    "neutral": {
        "bg_top": (10, 20, 40), "bg_bot": (20, 40, 80),
        "accent": (0, 180, 255), "text": (240, 250, 255),
        "subtext": (160, 200, 230), "bar": (0, 140, 210)
    },
}

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ─── MARKET DATA FETCHING ────────────────────────────────────────────────────
def get_live_market_summary():
    """Fetches real-time price summary for Groq to ensure accurate scripts."""
    try:
        # Nifty, BankNifty, and S&P500 for global context
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "S&P 500": "^GSPC"}
        summary_parts = []
        
        for name, sym in symbols.items():
            ticker = yf.Ticker(sym)
            df = ticker.history(period="1d")
            if not df.empty:
                last_price = df['Close'].iloc[-1]
                prev_close = df['Open'].iloc[-1]
                change_pct = ((last_price - prev_close) / prev_close) * 100
                summary_parts.append(f"{name}: {last_price:.2f} ({change_pct:+.2f}%)")
        
        return " | ".join(summary_parts) if summary_parts else "Live data unavailable"
    except Exception as e:
        print(f"⚠️ Market data fetch error: {e}")
        return "Live data unavailable"

# ─── BACKGROUND MUSIC ────────────────────────────────────────────────────────
def get_bg_music():
    day = datetime.now(IST).weekday()
    music_map = {
        0: "bgmusic1.mp3", 1: "bgmusic2.mp3", 2: "bgmusic3.mp3",
        3: "bgmusic1.mp3", 4: "bgmusic2.mp3", 5: "bgmusic3.mp3", 6: "bgmusic1.mp3"
    }
    f = MUSIC_DIR / music_map[day]
    if f.exists():
        return f
    for f in MUSIC_DIR.glob("*.mp3"):
        return f
    return None

# ─── GROQ SCRIPT GENERATION ──────────────────────────────────────────────────
def generate_slides(client):
    # Detect Mode from GitHub Environment
    mode = os.environ.get("CONTENT_MODE", "market").lower()
    holiday_name = os.environ.get("HOLIDAY_NAME", "")
    
    today_dt = datetime.now(IST)
    today_readable = today_dt.strftime("%A, %d %B %Y")
    today_iso = today_dt.strftime("%Y-%m-%d")

    # Fetch Real Data for the AI to use
    live_info = ""
    if mode == "market":
        print("📊 Fetching live prices for accurate video content...")
        live_info = get_live_market_summary()
        market_context = f"Today's LIVE Indian and global market levels: {live_info}. Focus on these levels for Nifty and BankNifty analysis."
    elif mode == "holiday":
        market_context = f"Indian Markets are CLOSED today for {holiday_name}. Create educational content about market holidays and wealth building."
    else:
        market_context = "Weekend special: Evergreen educational content about the Indian stock market."

    prompt = f"""You are an expert Indian market analyst for ai360trading channel.
Today's Date: {today_readable}
Context: {market_context}

Generate exactly 8 slides in Hinglish (Hindi + English mix). Use the LIVE prices provided in the context for slides 1, 2, and 3.

Respond ONLY with valid JSON:
{{
  "video_title": "compelling Hinglish title max 70 chars with {today_iso}",
  "video_description": "3-4 sentence Hinglish description, include ai360trading.in",
  "overall_sentiment": "bullish or bearish or neutral",
  "slides": [
    {{
      "title": "slide heading max 8 words",
      "content": "spoken content 40-60 words in Hinglish — BE SPECIFIC about levels if provided",
      "sentiment": "bullish or bearish or neutral",
      "key_points": ["point 1", "point 2", "point 3"]
    }}
  ]
}}

Topics: 1.Overview, 2.Nifty, 3.BankNifty, 4.Global, 5.FII/DII, 6.Sectors, 7.Stocks, 8.Plan."""

    print("🤖 Requesting AI Script...")
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        data = json.loads(resp.choices[0].message.content)
        return data
    except Exception as e:
        print(f"⚠️ Groq error: {e} — using fallback")
        return _fallback_slides()

def _fallback_slides():
    return {
        "video_title": f"Aaj Ka Market Analysis — {datetime.now(IST).strftime('%d %B %Y')}",
        "video_description": "Daily market analysis by ai360trading.in",
        "overall_sentiment": "neutral",
        "slides": [{"title": "Market Overview", "content": "Aaj market mein careful trading ki zaroorat hai. Levels ko respect karein.", "sentiment": "neutral", "key_points": ["Watch levels", "Stay cautious"]}] * 8
    }

# ─── RENDERER ────────────────────────────────────────────────────────────────
def make_slide(slide, idx, total, path):
    snt = slide.get("sentiment", "neutral").lower()
    th = THEMES.get(snt, THEMES["neutral"])

    img = Image.new("RGB", (W, H))
    px  = img.load()
    for y in range(H):
        c = lerp(th["bg_top"], th["bg_bot"], y / H)
        for x in range(W):
            px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0, 0), (W, 10)], fill=th["accent"])
    draw.text((W - 40, 30), "ai360trading.in", fill=(*th["subtext"], 180), font=get_font(FONT_REG_PATHS, 28), anchor="ra")
    draw.text((40, 35), f"{idx} / {total}", fill=(*th["subtext"], 200), font=get_font(FONT_BOLD_PATHS, 32), anchor="la")

    title_font = get_font(FONT_BOLD_PATHS, 72)
    title_lines = textwrap.wrap(slide["title"].upper(), width=28)
    ty = 140
    for line in title_lines[:2]:
        draw.text((W // 2, ty), line, fill=th["text"], font=title_font, anchor="mm")
        ty += 88

    draw.rectangle([(80, ty + 20), (W - 80, ty + 24)], fill=th["accent"])
    ty += 60

    content_font = get_font(FONT_REG_PATHS, 42)
    content_lines = textwrap.wrap(slide["content"], width=55)
    for line in content_lines[:6]:
        draw.text((80, ty), line, fill=th["text"], font=content_font)
        ty += 58

    if slide.get("key_points"):
        ty += 30
        bullet_font = get_font(FONT_BOLD_PATHS, 38)
        for pt in slide["key_points"][:3]:
            draw.text((80, ty), f"▶  {pt}", fill=th["accent"], font=bullet_font)
            ty += 52

    draw.rectangle([(0, H - 10), (W, H)], fill=th["accent"])
    img.save(str(path), quality=95)

async def gen_voice(text, path):
    await edge_tts.Communicate(text, VOICE).save(str(path))

# ─── YOUTUBE UPLOAD ──────────────────────────────────────────────────────────
def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json and os.path.exists("token.json"):
            with open("token.json") as f: creds_json = f.read()
        if not creds_json: return None
        return build("youtube", "v3", credentials=Credentials.from_authorized_user_info(json.loads(creds_json)))
    except: return None

def upload_to_youtube(video_path, title, description, tags):
    youtube = get_youtube_service()
    if not youtube: return None
    body = {
        "snippet": {"title": title[:100], "description": description, "tags": tags, "categoryId": "27"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    try:
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
        return response["id"]
    except: return None

# ─── MAIN RUNNER ─────────────────────────────────────────────────────────────
async def run():
    today_str = datetime.now(IST).strftime("%Y%m%d")
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    data = generate_slides(client)
    slides = data["slides"]
    vid_title = data.get("video_title", f"Market Analysis — {today_str}")
    vid_desc = data.get("video_description", "Daily analysis by ai360trading.in")

    full_desc = f"{vid_desc}\n\n🌐 Website: https://ai360trading.in\n📱 Telegram: https://t.me/ai360trading\n#Nifty #BankNifty #ai360trading"

    clips = []
    print(f"🎬 Rendering {len(slides)} slides...")
    for i, s in enumerate(slides):
        img_path, audio_path = OUT/f"analysis_{i}.png", OUT/f"analysis_{i}.mp3"
        make_slide(s, i+1, len(slides), img_path)
        await gen_voice(s["content"], audio_path)
        
        voice_clip = AudioFileClip(str(audio_path))
        duration = voice_clip.duration + 0.8
        
        bg_music_path = get_bg_music()
        if bg_music_path:
            bg = AudioFileClip(str(bg_music_path)).subclip(0, duration).volumex(0.07)
            slide_audio = CompositeAudioClip([voice_clip, bg])
        else:
            slide_audio = voice_clip

        clips.append(ImageClip(str(img_path)).set_duration(duration).set_audio(slide_audio))

    video_path = OUT / "analysis_video.mp4"
    concatenate_videoclips(clips, method="compose").write_videofile(
        str(video_path), fps=FPS, codec="libx264", audio_codec="aac", logger=None
    )

    tags = ["Nifty", "BankNifty", "ai360trading", "Market Analysis"]
    video_id = upload_to_youtube(video_path, vid_title, full_desc, tags)

    if video_id:
        (OUT / "analysis_video_id.txt").write_text(video_id, encoding="utf-8")
        meta = {"title": vid_title, "video_url": f"https://youtube.com/watch?v={video_id}", "date": today_str}
        (OUT / f"analysis_meta_{today_str}.json").write_text(json.dumps(meta, indent=2))
        print(f"✅ Uploaded: {video_id}")

if __name__ == "__main__":
    asyncio.run(run())
