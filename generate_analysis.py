"""
generate_analysis.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generates Part 1 — 8-slide market analysis video (16:9, YouTube).

VOICE: hi-IN-SwaraNeural (Swara female voice — consistent with education)

Upload: This script uploads directly to YouTube after render.
        Saves output/analysis_video_id.txt for generate_education.py to link.
        Saves output/analysis_meta_YYYYMMDD.json with full SEO meta.

SEO: All tags from seo.get_video_tags() — never hardcoded here.
Mode: market / weekend / holiday via CONTENT_MODE env var.

Last updated: April 2026 — SEO meta fix, seo.get_video_tags(), human_touch
"""

import os
import sys
import json
import asyncio
import textwrap
import random
from datetime import datetime
from pathlib import Path

import edge_tts
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip,
    concatenate_videoclips, concatenate_audioclips
)

# YouTube upload
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from human_touch import ht, seo

# ─── CONFIG ──────────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")
print(f"[MODE] generate_analysis.py running in mode: {CONTENT_MODE.upper()}")

OUT      = Path("output")
MUSIC_DIR= Path("public/music")
W, H     = 1920, 1080   # Horizontal — full YouTube video
FPS      = 24
VOICE    = "hi-IN-SwaraNeural"  # Swara female — analysis + education

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
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

# ─── THEME ───────────────────────────────────────────────────────────────────
THEMES = {
    "bullish": {
        "bg_top": (5, 30, 15),  "bg_bot": (10, 60, 30),
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

# ─── LIVE DATA ───────────────────────────────────────────────────────────────
def fetch_market_data():
    """Fetches live global data — prevents AI hallucinating old Nifty levels."""
    print("📈 Fetching live market data...")
    data_summary = ""
    try:
        tickers = {"Nifty 50": "^NSEI", "S&P 500": "^GSPC", "Bitcoin": "BTC-USD"}
        for name, sym in tickers.items():
            t = yf.Ticker(sym)
            try:
                last = t.fast_info["last_price"]
                prev = t.fast_info["previous_close"]
                pct  = ((last - prev) / prev) * 100
                data_summary += f"- {name}: {last:.2f} ({pct:+.2f}%)\n"
            except:
                hist = t.history(period="2d")
                if not hist.empty:
                    last = hist["Close"].iloc[-1]
                    prev = hist["Close"].iloc[-2]
                    pct  = ((last - prev) / prev) * 100
                    data_summary += f"- {name}: {last:.2f} ({pct:+.2f}%)\n"
                else:
                    data_summary += f"- {name}: Data Unavailable\n"
    except Exception as e:
        print(f"⚠️ Market data fetch error: {e}")
        data_summary = "Live data unavailable — focus on general technical structure."
    return data_summary

# ─── BACKGROUND MUSIC ────────────────────────────────────────────────────────
def get_bg_music():
    day = datetime.now().weekday()
    music_map = {
        0: "bgmusic1.mp3", 1: "bgmusic2.mp3", 2: "bgmusic3.mp3",
        3: "bgmusic1.mp3", 4: "bgmusic2.mp3", 5: "bgmusic3.mp3", 6: "bgmusic1.mp3"
    }
    f = MUSIC_DIR / music_map[day]
    if f.exists(): return f
    for f in MUSIC_DIR.glob("*.mp3"): return f
    return None

# ─── SCRIPT GENERATION ───────────────────────────────────────────────────────
def generate_slides():
    from ai_client import ai

    today    = datetime.now().strftime("%A, %d %B %Y")
    today_str= datetime.now().strftime("%Y-%m-%d")
    hook     = ht.get_hook(mode=CONTENT_MODE, lang="hi")

    if CONTENT_MODE == "weekend":
        market_context = "evergreen educational content about Indian and global markets."
    elif CONTENT_MODE == "holiday":
        holiday_label = HOLIDAY_NAME if HOLIDAY_NAME else "Indian Market Holiday"
        market_context = (
            f"special {holiday_label} educational content. Market is closed. "
            f"Focus on investment lessons, wealth-building, financial planning."
        )
    else:
        live_data = fetch_market_data()
        market_context = f"today's live market levels:\n{live_data}\nAnalyze these specific levels for Nifty, S&P 500, and BTC."

    prompt = f"""You are an expert Indian market analyst creating a professional YouTube video script in Hinglish for ai360trading.

Today is {today}.

USE THIS LIVE DATA FOR THE SCRIPT:
{market_context}

IMPORTANT: Nifty is currently around 22,000-24,000. DO NOT mention 17,000 or any outdated levels.
Start slide 1 with this hook: "{hook}"

Generate exactly 8 slides in valid JSON:
{{
  "video_title": "Hinglish title max 70 chars with {today_str}",
  "video_description": "3-4 sentence Hinglish description with key insights, include ai360trading.in link",
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
        # Humanize slide content
        for slide in data.get("slides", []):
            if slide.get("content"):
                slide["content"] = ht.humanize(slide["content"], lang="hi")
        print(f"✅ Analysis script ready: {data.get('video_title', '')[:60]}")
        return data
    except Exception as e:
        print(f"⚠️ Script generation error: {e}")
        return _fallback_slides()


def _fallback_slides():
    return {
        "video_title": f"Aaj Ka Market Analysis — {datetime.now().strftime('%d %B %Y')}",
        "video_description": "Aaj ke market ki poori analysis. Visit ai360trading.in",
        "overall_sentiment": "neutral",
        "slides": [
            {"title": "Market Overview", "content": "Market levels are updating. Please check back for live analysis.", "sentiment": "neutral", "key_points": ["Loading data"]}
        ]
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
    draw.text((W - 40, 30), "ai360trading.in", fill=(*th["subtext"], 180), font=get_font(FONT_REG_PATHS, 28), anchor="ra")
    draw.text((40, 35), f"{idx} / {total}", fill=(*th["subtext"], 200), font=get_font(FONT_BOLD_PATHS, 32), anchor="la")

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
    tts_speed = ht.get_tts_speed()
    rate_pct  = int((tts_speed - 1.0) * 100)
    rate_str  = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
    await edge_tts.Communicate(text, VOICE, rate=rate_str).save(str(path))

# ─── YOUTUBE UPLOAD ──────────────────────────────────────────────────────────
def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json and os.path.exists("token.json"):
            with open("token.json") as f: creds_json = f.read()
        if not creds_json: return None
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        return build("youtube", "v3", credentials=creds)
    except Exception:
        return None


def upload_to_youtube(video_path, title, description, tags):
    youtube = get_youtube_service()
    if not youtube:
        print("❌ YouTube service unavailable — skipping upload")
        return None
    body = {
        "snippet": {
            "title":       title[:100],
            "description": description,
            "tags":        tags[:30],
            "categoryId":  "27"  # Education — best for finance monetisation
        },
        "status": {
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"🚀 Uploading analysis video: {title[:60]}...")
    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status: print(f"  {int(status.progress() * 100)}%")
        vid_id = response["id"]
        print(f"✅ Analysis uploaded: https://youtube.com/watch?v={vid_id}")
        return vid_id
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None

# ─── BUILD SEO TITLE + DESCRIPTION ───────────────────────────────────────────
def build_video_meta(data, today):
    """Build full SEO title, description, and tags for the analysis video."""
    vid_title = data.get("video_title", f"Market Analysis — {today}")
    vid_desc  = data.get("video_description", "Daily market analysis by ai360trading.in")
    sentiment = data.get("overall_sentiment", "neutral")

    # Get tags from seo system
    tags       = seo.get_video_tags(mode=CONTENT_MODE, is_short=False)
    hashtag_str= " ".join([f"#{t}" for t in tags[:15]])

    if CONTENT_MODE == "holiday":
        label    = HOLIDAY_NAME if HOLIDAY_NAME else "Market Holiday"
        full_desc = (
            f"🎉 {label} Special — {vid_desc}\n\n"
            f"🌍 For investors: India, USA, UK, Brazil & UAE\n"
            f"📊 Daily market analysis | Nifty50 | S&P500 | BTC\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n"
            f"⚠️ Educational content only. Not financial advice.\n\n"
            f"#ai360trading #MarketAnalysis {hashtag_str}"
        )
    elif CONTENT_MODE == "weekend":
        full_desc = (
            f"📚 Weekend Learning — {vid_desc}\n\n"
            f"🌍 For investors: India, USA, UK, Brazil & UAE\n"
            f"📊 Weekly market recap and education\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n"
            f"⚠️ Educational content only. Not financial advice.\n\n"
            f"#ai360trading #WeekendLearning {hashtag_str}"
        )
    else:
        full_desc = (
            f"📊 {vid_desc}\n\n"
            f"🎯 Daily Nifty50 analysis with live data\n"
            f"🌍 For traders: India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n"
            f"⚠️ Educational content only. Not financial advice.\n\n"
            f"#ai360trading #Nifty50 #MarketAnalysis {hashtag_str}"
        )

    return vid_title, full_desc, tags, sentiment

# ─── MAIN ────────────────────────────────────────────────────────────────────
async def run():
    today = datetime.now().strftime("%Y%m%d")

    data      = generate_slides()
    slides    = data["slides"]

    # Build full SEO meta
    vid_title, full_desc, tags, sentiment = build_video_meta(data, today)

    # ── Render all slides + voices ────────────────────────────────────────────
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
                bg         = AudioFileClip(str(bg_music_path)).subclip(0, duration).volumex(0.07)
                slide_audio= CompositeAudioClip([voice_clip, bg])
            except:
                slide_audio= voice_clip
        else:
            slide_audio = voice_clip

        clip = ImageClip(str(img_path)).set_duration(duration).set_audio(slide_audio)
        clips.append(clip)

    # ── Render video ──────────────────────────────────────────────────────────
    video_path = OUT / "analysis_video.mp4"
    concatenate_videoclips(clips, method="compose").write_videofile(
        str(video_path), fps=FPS, codec="libx264", audio_codec="aac",
        remove_temp=True, logger=None
    )
    print(f"✅ Analysis video rendered: {video_path.name}")

    # ── Upload to YouTube ─────────────────────────────────────────────────────
    video_id = upload_to_youtube(video_path, vid_title, full_desc, tags)

    if video_id:
        # Save video ID for generate_education.py to link Part 1 → Part 2
        id_path = OUT / "analysis_video_id.txt"
        id_path.write_text(video_id, encoding="utf-8")
        print(f"💾 Saved analysis_video_id.txt: {video_id}")
    else:
        # Write UPLOAD_FAILED so education script doesn't try to use empty ID
        (OUT / "analysis_video_id.txt").write_text("UPLOAD_FAILED", encoding="utf-8")

    # ── Save meta JSON with full SEO data ────────────────────────────────────
    meta = {
        "title":            vid_title,
        "description":      full_desc,
        "tags":             tags,
        "sentiment":        sentiment,
        "content_mode":     CONTENT_MODE,
        "youtube_video_id": video_id or "",
        "youtube_video_url": f"https://youtube.com/watch?v={video_id}" if video_id else "",
    }
    meta_path = OUT / f"analysis_meta_{today}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 Saved analysis meta: {meta_path.name}")

    print(f"\n{'='*55}")
    print(f"✅ ANALYSIS DONE — {today} [{CONTENT_MODE.upper()}]")
    print(f"   Title    : {vid_title[:60]}")
    print(f"   Video ID : {video_id or 'FAILED'}")
    print(f"   Tags     : {', '.join(tags[:5])}...")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    asyncio.run(run())
