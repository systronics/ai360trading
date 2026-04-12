import os, sys, json, asyncio, textwrap, random
import logging, warnings
from datetime import datetime
from pathlib import Path
import edge_tts
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, concatenate_audioclips

# ── Bug 1 Fix: Suppress noisy logs ──────────────────────────────────────────
logging.getLogger("moviepy").setLevel(logging.ERROR)
logging.getLogger("imageio").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

from ai_client import ai
from human_touch import ht, seo

# YouTube upload
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── CONFIG ──────────────────────────────────────────────────────────────────
OUT       = Path("output")
MUSIC_DIR = Path("public/music")
W, H      = 1920, 1080  # Horizontal — full YouTube video
FPS       = 24
VOICE     = "hi-IN-SwaraNeural"  # Hinglish female voice

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")

os.makedirs(OUT, exist_ok=True)

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

print(f"[MODE] generate_analysis.py running in mode: {CONTENT_MODE.upper()}")

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
        "bg_top": (5, 30, 15),   "bg_bot": (10, 60, 30),
        "accent": (0, 220, 110), "text": (235, 255, 245),
        "subtext": (160, 220, 180), "bar": (0, 180, 90)
    },
    "bearish": {
        "bg_top": (35, 10, 10),  "bg_bot": (70, 20, 20),
        "accent": (255, 60, 60), "text": (255, 240, 240),
        "subtext": (220, 160, 160), "bar": (200, 40, 40)
    },
    "neutral": {
        "bg_top": (10, 20, 40),   "bg_bot": (20, 40, 80),
        "accent": (0, 180, 255),  "text": (240, 250, 255),
        "subtext": (160, 200, 230), "bar": (0, 140, 210)
    },
}

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ─── LIVE DATA FETCHING ──────────────────────────────────────────────────────
def fetch_market_data():
    """Fetches live global data to prevent AI hallucinations."""
    print("📈 Fetching live market data...")
    data_summary = ""
    try:
        tickers = {"Nifty 50": "^NSEI", "S&P 500": "^GSPC", "Bitcoin": "BTC-USD"}
        for name, sym in tickers.items():
            try:
                t = yf.Ticker(sym)
                hist = t.history(period="2d")
                if not hist.empty:
                    price  = hist['Close'].iloc[-1]
                    change = price - hist['Close'].iloc[-2]
                    pct    = (change / hist['Close'].iloc[-2]) * 100
                    data_summary += f"- {name}: {price:.2f} ({pct:+.2f}%)\n"
                else:
                    data_summary += f"- {name}: Data Unavailable\n"
            except Exception:
                data_summary += f"- {name}: Data Unavailable\n"
    except Exception:
        data_summary = "Live data unavailable, focus on general technical structure."
    return data_summary

# ─── BACKGROUND MUSIC ────────────────────────────────────────────────────────
def get_bg_music():
    day = datetime.now().weekday()
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

def is_weekend():
    return datetime.now().weekday() >= 5

# ─── SCRIPT GENERATION via ai_client ─────────────────────────────────────────
def generate_slides():
    today     = datetime.now().strftime("%A, %d %B %Y")
    weekend   = is_weekend()
    today_str = datetime.now().strftime("%Y-%m-%d")

    live_data = fetch_market_data()

    if CONTENT_MODE == "holiday":
        market_context = f"Today is {HOLIDAY_NAME} — market holiday. Create motivational educational content."
    elif weekend or CONTENT_MODE == "weekend":
        market_context = "evergreen educational content about Indian and global markets."
    else:
        market_context = f"today's live market levels:\n{live_data}\nAnalyze these specific levels for Nifty, S&P 500, and BTC."

    prompt = f"""You are an expert Indian market analyst creating a professional YouTube video script in Hinglish for ai360trading.

Today is {today}.

USE THIS LIVE DATA FOR THE SCRIPT:
{market_context}

IMPORTANT: Nifty is currently around 22,000-23,000. DO NOT mention 17,000 or old data.

Generate exactly 8 slides in valid JSON:
{{
  "video_title": "Hinglish title max 70 chars with {today_str}",
  "video_description": "Hinglish description with key insights, include ai360trading.in link",
  "overall_sentiment": "bullish or bearish or neutral",
  "slides": [
    {{
      "title": "slide heading",
      "content": "spoken content 40-60 words in Hinglish using the LIVE DATA provided.",
      "sentiment": "bullish or bearish or neutral",
      "key_points": ["point 1", "point 2", "point 3"]
    }}
  ]
}}"""

    print("🤖 Generating market analysis script via ai_client...")

    try:
        data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
        if data and "slides" in data:
            print(f"✅ Script generated via {ai.active_provider}")
            return data
        raise ValueError("No slides in response")
    except Exception:
        print("⚠️ ai_client failed — using fallback slides")
        return _fallback_slides()

def _fallback_slides():
    return {
        "video_title":        f"Aaj Ka Market Analysis — {datetime.now().strftime('%d %B %Y')}",
        "video_description":  "Aaj ke market ki poori analysis. Visit ai360trading.in",
        "overall_sentiment":  "neutral",
        "slides": [{"title": "Market Overview", "content": "Market levels are updating. Please check back for live analysis.", "sentiment": "neutral", "key_points": ["Loading data"]}]
    }

# ─── SLIDE RENDERER ──────────────────────────────────────────────────────────
def make_slide(slide, idx, total, path):
    snt = slide.get("sentiment", "neutral").lower()
    if snt not in THEMES: snt = "neutral"
    th = THEMES[snt]

    img = Image.new("RGB", (W, H))
    px  = img.load()
    for y in range(H):
        c = lerp(th["bg_top"], th["bg_bot"], y / H)
        for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0, 0), (W, 10)], fill=th["accent"])
    draw.text((W - 40, 30),  "ai360trading.in", fill=(*th["subtext"], 180), font=get_font(FONT_REG_PATHS, 28),  anchor="ra")
    draw.text((40, 35),      f"{idx} / {total}", fill=(*th["subtext"], 200), font=get_font(FONT_BOLD_PATHS, 32), anchor="la")

    title_font  = get_font(FONT_BOLD_PATHS, 72)
    title_lines = textwrap.wrap(slide["title"].upper(), width=28)
    ty = 140
    for line in title_lines[:2]:
        draw.text((W // 2, ty), line, fill=th["text"], font=title_font, anchor="mm")
        ty += 88

    draw.rectangle([(80, ty + 20), (W - 80, ty + 24)], fill=th["accent"])
    ty += 60

    content_font  = get_font(FONT_REG_PATHS, 42)
    content_lines = textwrap.wrap(slide["content"], width=55)
    for line in content_lines[:6]:
        draw.text((80, ty), line, fill=th["text"], font=content_font)
        ty += 58

    if slide.get("key_points"):
        ty += 30
        bullet_font = get_font(FONT_BOLD_PATHS, 38)
        for pt in slide["key_points"][:3]:
            draw.text((80, ty), f"▶ {pt}", fill=th["accent"], font=bullet_font)
            ty += 52

    draw.rectangle([(0, H - 10), (W, H)], fill=th["accent"])
    img.save(str(path), quality=95)

# ─── VOICE ───────────────────────────────────────────────────────────────────
async def gen_voice(text, path):
    await edge_tts.Communicate(text, VOICE).save(str(path))

# ─── YOUTUBE UPLOAD ──────────────────────────────────────────────────────────
def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json and os.path.exists("token.json"):
            with open("token.json") as f: creds_json = f.read()
        if not creds_json: return None
        info  = json.loads(creds_json)
        creds = Credentials.from_authorized_user_info(info)
        return build("youtube", "v3", credentials=creds)
    except Exception:
        return None

def upload_to_youtube(video_path, title, description, tags):
    youtube = get_youtube_service()
    if not youtube: return None
    body = {
        "snippet": {"title": title[:100], "description": description, "tags": tags, "categoryId": "27"},
        "status":  {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
        return response["id"]
    except Exception:
        return None

# ─── MAIN ────────────────────────────────────────────────────────────────────
async def run():
    today = datetime.now().strftime("%Y%m%d")

    data      = generate_slides()
    slides    = data["slides"]
    sentiment = data.get("overall_sentiment", "neutral")
    vid_title = data.get("video_title", f"Market Analysis — {today}")
    vid_desc  = data.get("video_description", "Daily market analysis by ai360trading.in")
    full_desc = f"{vid_desc}\n\n🌐 Website: https://ai360trading.in\n#Nifty #Trading #ai360trading"

    tags = seo.get_video_tags(CONTENT_MODE, lang="hi") + ["Nifty", "Trading", "ai360trading"]

    clips = []
    for i, s in enumerate(slides):
        img_path   = OUT / f"an_{i}.png"
        audio_path = OUT / f"an_{i}.mp3"
        make_slide(s, i + 1, len(slides), img_path)
        await gen_voice(s["content"], audio_path)

        voice_clip    = AudioFileClip(str(audio_path))
        duration      = voice_clip.duration + 0.8
        bg_music_path = get_bg_music()

        if bg_music_path:
            try:
                bg          = AudioFileClip(str(bg_music_path)).subclip(0, duration).volumex(0.07)
                slide_audio = CompositeAudioClip([voice_clip, bg])
            except Exception:
                slide_audio = voice_clip
        else:
            slide_audio = voice_clip

        clip = ImageClip(str(img_path)).set_duration(duration).set_audio(slide_audio)
        clips.append(clip)

    video_path = OUT / "analysis_video.mp4"
    concatenate_videoclips(clips, method="compose").write_videofile(
        str(video_path), fps=FPS, codec="libx264", audio_codec="aac", remove_temp=True, logger=None
    )

    video_id = upload_to_youtube(video_path, vid_title, full_desc, tags)
    if video_id:
        (OUT / "analysis_video_id.txt").write_text(video_id, encoding="utf-8")
        print(f"✅ Success! YouTube ID: {video_id}")
    else:
        (OUT / "analysis_video_id.txt").write_text("UPLOAD_FAILED", encoding="utf-8")
        print("⚠️ YouTube upload failed — ID saved as UPLOAD_FAILED")

if __name__ == "__main__":
    asyncio.run(run())
