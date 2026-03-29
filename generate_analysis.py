"""
generate_analysis.py — AI360Trading Market Analysis Video (Part 1)
==================================================================
Generates 8-slide 16:9 market analysis video in Hinglish.
Uses: ai_client (Groq→Gemini→Claude→OpenAI→Templates fallback)
Uses: human_touch (anti-AI-penalty hooks, TTS speed variation)
Mode-aware: market / weekend / holiday
Upload: handled by upload_youtube.py (separate step in workflow)
Author: AI360Trading Automation
Last Updated: March 2026 — Phase 2 Upgrade
"""

import os
import sys
import json
import asyncio
import textwrap
import random
import requests
from datetime import datetime
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip,
    concatenate_videoclips, concatenate_audioclips
)
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── Phase 2: ai_client + human_touch ────────────────────────────────────────
from ai_client import ai
from human_touch import ht, seo

# ─── CONFIG ──────────────────────────────────────────────────────────────────
OUT       = Path("output")
MUSIC_DIR = Path("public/music")
W, H      = 1920, 1080
FPS       = 24
VOICE     = "hi-IN-SwaraNeural"

# ─── Content Mode ─────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")

print(f"[MODE] generate_analysis.py running in mode: {CONTENT_MODE.upper()}")
print(f"[AI]   Using ai_client fallback chain: Groq→Gemini→Claude→OpenAI→Templates")

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
    "holiday": {
        "bg_top": (30, 15, 45), "bg_bot": (60, 30, 80),
        "accent": (255, 160, 60), "text": (255, 248, 235),
        "subtext": (220, 190, 140), "bar": (200, 130, 40)
    },
}

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ─── LIVE DATA FETCHING ──────────────────────────────────────────────────────
def fetch_market_data():
    """Fetch live global data to prevent AI hallucinations."""
    if CONTENT_MODE in ("holiday", "weekend"):
        print("  📅 Holiday/Weekend mode — skipping live market fetch")
        return "Market closed today — educational content mode."

    print("  📈 Fetching live market data...")
    data_summary = ""
    symbols = {
        "Nifty 50": "^NSEI",
        "S&P 500":  "^GSPC",
        "Bitcoin":  "BTC-USD",
        "Gold":     "GC=F",
        "USD/INR":  "INR=X",
    }
    for name, sym in symbols.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=2d"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
            meta  = r.json()['chart']['result'][0]['meta']
            price = round(meta.get('regularMarketPrice', 0), 2)
            prev  = round(meta.get('chartPreviousClose', price), 2)
            pct   = round(((price - prev) / prev) * 100, 2) if prev else 0
            data_summary += f"- {name}: {price:,} ({pct:+.2f}%)\n"
        except Exception as e:
            data_summary += f"- {name}: Data Unavailable\n"
    return data_summary if data_summary else "Live data unavailable — focus on general technical structure."

# ─── BACKGROUND MUSIC ────────────────────────────────────────────────────────
def get_bg_music():
    day = datetime.now().weekday()
    music_map = {0: "bgmusic1.mp3", 1: "bgmusic2.mp3", 2: "bgmusic3.mp3",
                 3: "bgmusic1.mp3", 4: "bgmusic2.mp3", 5: "bgmusic3.mp3", 6: "bgmusic1.mp3"}
    f = MUSIC_DIR / music_map[day]
    if f.exists():
        return f
    for f in MUSIC_DIR.glob("*.mp3"):
        return f
    return None

# ─── SCRIPT GENERATION via ai_client ─────────────────────────────────────────
def generate_slides():
    today      = datetime.now().strftime("%A, %d %B %Y")
    today_str  = datetime.now().strftime("%Y-%m-%d")
    live_data  = fetch_market_data()

    # ── Phase 2: human_touch hook for intro slide ────────────────────────────
    ht_hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")

    if CONTENT_MODE == "holiday":
        market_context = (
            f"Today is {HOLIDAY_NAME} — Indian market is closed. "
            "Create an inspirational and educational video about wealth-building, trading mindset, "
            "or investment lessons. Make it motivational and globally relevant."
        )
    elif CONTENT_MODE == "weekend":
        market_context = (
            "Weekend — market is closed. Create an educational video about "
            "technical analysis concepts, trading psychology, or investment strategies. "
            "Evergreen content suitable for Indian and global audiences."
        )
    else:
        market_context = (
            f"Today's live market levels:\n{live_data}\n"
            "Analyze these specific levels for Nifty, S&P 500, Bitcoin, and Gold. "
            "Give concrete support/resistance levels and trade setups."
        )

    prompt = f"""You are an expert Indian market analyst creating a professional YouTube video script in Hinglish for ai360trading.

Today is {today}.
Content Mode: {CONTENT_MODE.upper()}

LIVE DATA / CONTEXT:
{market_context}

HOOK TO OPEN THE FIRST SLIDE (adapt naturally — do not copy verbatim):
{ht_hook}

Generate exactly 8 slides in valid JSON:
{{
  "video_title": "Hinglish YouTube title max 70 chars, include {today_str}",
  "video_description": "3-4 sentence Hinglish description with key insights, include ai360trading.in link",
  "overall_sentiment": "bullish or bearish or neutral or holiday",
  "slides": [
    {{
      "title": "slide heading max 8 words",
      "content": "spoken Hinglish content 40-60 words — natural, specific data if available",
      "sentiment": "bullish or bearish or neutral or holiday",
      "key_points": ["point 1", "point 2", "point 3"]
    }}
  ]
}}

RULES:
- Slide 1: strong hook opening with ht_hook inspiration + today's context
- Slides 2-6: deep analysis / education content
- Slide 7: risk warning and key levels to watch
- Slide 8: CTA — subscribe, Telegram, ai360trading.in
- Hinglish = natural Hindi-English mix, NOT transliterated Hindi
- If weekend/holiday: educational content, no live price speculation
- DO NOT mention Nifty at 17,000 or any obviously outdated level"""

    system_prompt = (
        "You are an expert Hinglish financial content creator for AI360Trading. "
        "Write natural, engaging Hinglish — the way an experienced Indian trader actually speaks. "
        "Specific data points preferred over generic statements. "
        "Respond ONLY with valid JSON — no markdown, no extra text."
    )

    print("  🤖 Generating market analysis script via ai_client...")

    try:
        data = ai.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            content_mode=CONTENT_MODE,
            lang="hi",
        )
        if not data or not data.get("slides"):
            raise ValueError("Empty response from ai_client")
        print(f"  ✅ {len(data['slides'])} slides generated via {ai.active_provider}")
        return data
    except Exception as e:
        print(f"  ⚠️ ai_client error: {e} — using fallback slides")
        return _fallback_slides()


def _fallback_slides():
    """Template fallback — guaranteed content when all AI providers fail."""
    # Uses human_touch fallback hooks
    hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")
    mode_label = {"market": "Market Analysis", "weekend": "Weekend Education", "holiday": "Holiday Special"}.get(CONTENT_MODE, "Market Analysis")
    return {
        "video_title": f"Aaj Ka {mode_label} — {datetime.now().strftime('%d %B %Y')}",
        "video_description": f"Aaj ke market ki poori analysis. Visit ai360trading.in | Telegram: t.me/ai360trading",
        "overall_sentiment": "neutral",
        "slides": [
            {"title": "Aaj Ka Market Overview", "content": hook, "sentiment": "neutral", "key_points": ["Risk management first", "Follow the trend", "Patience key hai"]},
            {"title": "Nifty Analysis", "content": "Nifty ke key support aur resistance levels pe nazar rakhein. Intraday mein volatility expected hai.", "sentiment": "neutral", "key_points": ["Support zone watch", "Resistance level key", "Volume confirm karo"]},
            {"title": "Global Markets", "content": "S&P 500 aur global cues Nifty ko directly impact karte hain. US market ka trend follow karo.", "sentiment": "neutral", "key_points": ["S&P 500 watch", "Dollar index", "FII flows important"]},
            {"title": "Trade Setup", "content": "Aaj ke liye clean trade setup identify karo. Bina confirmation ke entry mat lo.", "sentiment": "neutral", "key_points": ["Entry confirmation", "Stop loss set karo", "Target realistic rakho"]},
            {"title": "Risk Management", "content": "Har trade mein 1-2% se zyada risk mat lo. Capital preservation first priority hai.", "sentiment": "neutral", "key_points": ["1-2% max risk", "Stop loss mandatory", "Position sizing crucial"]},
            {"title": "Sector Watch", "content": "Strong sectors mein momentum trading better results deta hai. Weak sectors se door raho.", "sentiment": "neutral", "key_points": ["Bank Nifty watch", "IT sector check", "Midcap momentum"]},
            {"title": "Key Levels Today", "content": "Intraday mein in levels ko mark karo. Breakout ya breakdown pe action lo.", "sentiment": "neutral", "key_points": ["Mark support levels", "Resistance zones", "Volume on breakout"]},
            {"title": "Subscribe and Learn", "content": "Daily market analysis ke liye subscribe karo. Telegram join karo live signals ke liye. ai360trading.in visit karo.", "sentiment": "neutral", "key_points": ["Subscribe karo", "Telegram join karo", "ai360trading.in"]},
        ]
    }

# ─── SLIDE RENDERER ──────────────────────────────────────────────────────────
def make_slide(slide, idx, total, path, overall_sentiment="neutral"):
    snt = slide.get("sentiment", overall_sentiment).lower()
    if snt not in THEMES:
        snt = "neutral"
    th  = THEMES[snt]
    img = Image.new("RGB", (W, H))
    px  = img.load()

    for y in range(H):
        c = lerp(th["bg_top"], th["bg_bot"], y / H)
        for x in range(W):
            px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0, 0), (W, 10)], fill=th["accent"])
    draw.text((W - 40, 30), "ai360trading.in", fill=(*th["subtext"], 180),
              font=get_font(FONT_REG_PATHS, 28), anchor="ra")
    draw.text((40, 35), f"{idx} / {total}", fill=(*th["subtext"], 200),
              font=get_font(FONT_BOLD_PATHS, 32), anchor="la")

    # Mode badge (holiday/weekend)
    if CONTENT_MODE in ("holiday", "weekend"):
        badge = "🎯 HOLIDAY SPECIAL" if CONTENT_MODE == "holiday" else "📚 WEEKEND EDUCATION"
        draw.text((W // 2, 35), badge, fill=(*th["accent"], 200),
                  font=get_font(FONT_BOLD_PATHS, 26), anchor="mm")

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
    # ── Phase 2: human_touch TTS speed variation ─────────────────────────────
    tts_speed = ht.get_tts_speed()
    voice = VOICE
    # edge_tts rate format: "+10%" or "-5%"
    rate_pct = int((tts_speed - 1.0) * 100)
    rate_str = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
    try:
        await edge_tts.Communicate(text, voice, rate=rate_str).save(str(path))
    except Exception:
        # Fallback: default speed
        await edge_tts.Communicate(text, voice).save(str(path))

# ─── YOUTUBE UPLOAD ──────────────────────────────────────────────────────────
def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json and os.path.exists("token.json"):
            with open("token.json") as f:
                creds_json = f.read()
        if not creds_json:
            return None
        info  = json.loads(creds_json)
        creds = Credentials.from_authorized_user_info(info)
        return build("youtube", "v3", credentials=creds)
    except Exception:
        return None


def upload_to_youtube(video_path, title, description, tags):
    youtube = get_youtube_service()
    if not youtube:
        print("  ❌ No YouTube credentials — skipping upload")
        return None
    body = {
        "snippet": {
            "title":       title[:100],
            "description": description,
            "tags":        tags,
            "categoryId":  "27",
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"  🚀 Uploading to YouTube: {title[:60]}...")
    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  Uploaded {int(status.progress() * 100)}%")
        video_id = response["id"]
        print(f"  ✅ YouTube ID: {video_id}")
        return video_id
    except Exception as e:
        print(f"  ❌ YouTube upload failed: {e}")
        return None

# ─── MAIN ────────────────────────────────────────────────────────────────────
async def run():
    today_str = datetime.now().strftime("%Y%m%d")

    # 1. Generate script via ai_client
    data      = generate_slides()
    slides    = data["slides"]
    sentiment = data.get("overall_sentiment", "neutral")
    vid_title = data.get("video_title", f"Aaj Ka Market Analysis — {datetime.now().strftime('%d %B %Y')}")
    vid_desc  = data.get("video_description", "Daily market analysis by ai360trading.in")

    # ── Phase 2: SEO tags from human_touch ──────────────────────────────────
    ht_tags  = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")
    base_tags = ["Nifty", "NiftyAnalysis", "Trading", "ai360trading",
                 "StockMarketIndia", "Hinglish", "TradingIndia", "NSE", "BSE"]
    all_tags  = list(dict.fromkeys(base_tags + ht_tags))  # deduplicated

    full_desc = (
        f"{vid_desc}\n\n"
        f"🌐 Website: https://ai360trading.in\n"
        f"📱 Telegram: https://t.me/ai360trading\n"
        f"📺 Subscribe for daily market analysis!\n\n"
        f"#Nifty #TradingIndia #ai360trading #StockMarketIndia #Hinglish"
    )

    # 2. Build slides and voice
    print(f"\n  🎬 Building {len(slides)} analysis slides...")
    clips = []
    for i, s in enumerate(slides):
        img_path   = OUT / f"an_{i}.png"
        audio_path = OUT / f"an_{i}.mp3"

        make_slide(s, i + 1, len(slides), img_path, overall_sentiment=sentiment)
        await gen_voice(s["content"], audio_path)

        voice_clip    = AudioFileClip(str(audio_path))
        duration      = voice_clip.duration + 0.8
        bg_music_path = get_bg_music()

        if bg_music_path:
            try:
                bg = AudioFileClip(str(bg_music_path))
                if bg.duration < duration:
                    loops = int(duration / bg.duration) + 1
                    bg = concatenate_audioclips([bg] * loops)
                bg = bg.subclip(0, duration).volumex(0.07)
                slide_audio = CompositeAudioClip([voice_clip, bg])
            except Exception as e:
                print(f"  ⚠️ Music error slide {i}: {e}")
                slide_audio = voice_clip
        else:
            slide_audio = voice_clip

        clip = ImageClip(str(img_path)).set_duration(duration).set_audio(slide_audio)
        clips.append(clip)
        print(f"  Slide {i+1}/{len(slides)} ready")

    # 3. Render video
    video_path = OUT / "analysis_video.mp4"
    print(f"\n  🎥 Rendering analysis video...")
    concatenate_videoclips(clips, method="compose").write_videofile(
        str(video_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(OUT / "temp_an_audio.aac"),
        remove_temp=True,
        logger=None,
    )
    print(f"  ✅ Video rendered: {video_path}")

    # 4. Upload to YouTube
    video_id = upload_to_youtube(video_path, vid_title, full_desc, all_tags)

    # 5. Save metadata for Part 2 (generate_education.py reads this)
    if video_id:
        (OUT / "analysis_video_id.txt").write_text(video_id, encoding="utf-8")
        meta = {
            "title":       vid_title,
            "description": full_desc,
            "video_id":    video_id,
            "video_url":   f"https://youtube.com/watch?v={video_id}",
            "sentiment":   sentiment,
            "mode":        CONTENT_MODE,
            "date":        today_str,
            "ai_provider": ai.active_provider,
        }
        (OUT / f"analysis_meta_{today_str}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  ✅ Analysis meta saved | AI provider: {ai.active_provider}")
    else:
        (OUT / "analysis_video_id.txt").write_text("UPLOAD_FAILED", encoding="utf-8")
        print("  ⚠️ Upload failed — saved placeholder ID")


if __name__ == "__main__":
    asyncio.run(run())
