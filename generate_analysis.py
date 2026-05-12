"""
generate_analysis.py — AI360Trading v2.1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v2.1 FIX: IndentationError on slide_audio and video_id lines
v2.0 CHANGES: Stock-name title, 14 slides, no bgmusic,
              YouTube safe tags, longer content per slide
"""

import os
import json
import asyncio
import textwrap
from datetime import datetime
from pathlib import Path

import edge_tts
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from human_touch import ht, seo

# ─── CONFIG ───────────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")
print(f"[MODE] generate_analysis.py v2.1 running in mode: {CONTENT_MODE.upper()}")

OUT        = Path("output")
W, H       = 1920, 1080
FPS        = 24
VOICE      = "hi-IN-SwaraNeural"
NUM_SLIDES = 14   # 14 × ~35sec = ~8 min (mid-roll ads enabled)

os.makedirs(OUT, exist_ok=True)

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

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

THEMES = {
    "bullish": {"bg_top":(5,30,15),  "bg_bot":(10,60,30),  "accent":(0,220,110),  "text":(235,255,245), "subtext":(160,220,180)},
    "bearish": {"bg_top":(35,10,10), "bg_bot":(70,20,20),  "accent":(255,60,60),  "text":(255,240,240), "subtext":(220,160,160)},
    "neutral": {"bg_top":(10,20,40), "bg_bot":(20,40,80),  "accent":(0,180,255),  "text":(240,250,255), "subtext":(160,200,230)},
}

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ─── LIVE DATA ────────────────────────────────────────────────────────────────
def fetch_market_data():
    print("📈 Fetching live market data...")
    data_summary = ""
    try:
        tickers = {"Nifty 50":"^NSEI","S&P 500":"^GSPC","Bitcoin":"BTC-USD"}
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

# ─── SCRIPT GENERATION ───────────────────────────────────────────────────────
def generate_slides():
    from ai_client import ai
    today     = datetime.now().strftime("%A, %d %B %Y")
    today_str = datetime.now().strftime("%d %b %Y")
    hook      = ht.get_hook(mode=CONTENT_MODE, lang="hi")
    cta       = ht.get_cta(lang="hi")

    if CONTENT_MODE == "weekend":
        market_context    = "evergreen educational content about Indian and global markets."
        extra_instruction = "Focus on one technical concept or wealth-building lesson. Make it beginner-friendly."
    elif CONTENT_MODE == "holiday":
        holiday_label     = HOLIDAY_NAME if HOLIDAY_NAME else "Indian Market Holiday"
        market_context    = f"special {holiday_label} educational content. Market is closed."
        extra_instruction = f"Reference {holiday_label} naturally. Keep festive but educational tone."
    else:
        live_data         = fetch_market_data()
        market_context    = f"today's live market levels:\n{live_data}"
        extra_instruction = (
            "Identify 2-3 specific breakout stocks with entry, SL, target levels. "
            "Use real NSE symbols like CGPOWER, BHEL etc."
        )

    prompt = f"""You are an expert Indian market analyst creating a combined 10-12 minute YouTube video in Hinglish for ai360trading.

Today is {today}.
Market context: {market_context}
{extra_instruction}

TITLE RULES: Put most exciting stock name FIRST.
Example: "CGPOWER BREAKOUT — Rs1000 Target? | Nifty50 {today_str} | AI360 Trading"
Max 95 characters. End with "| AI360 Trading".

Start slide 1 with: "{hook}"
Use this CTA: "{cta}"
Slide 4 must end: "Comment karo — A agar bullish hain, B agar bearish!"
Slide 9 must end: "Subscribe karo aur bell icon dabao!"

Generate exactly {NUM_SLIDES} slides in valid JSON:
{{
  "video_title": "STOCK ACTION — Result? | Nifty50 {today_str} | AI360 Trading",
  "main_insight": "One key insight — max 20 words",
  "top_stocks": ["STOCK1","STOCK2","STOCK3"],
  "overall_sentiment": "bullish or bearish or neutral",
  "slides": [
    {{
      "title": "slide heading max 6 words",
      "content": "spoken content 100-120 words in Hinglish. Explain the WHY not just WHAT.",
      "sentiment": "bullish or bearish or neutral",
      "key_points": ["point 1","point 2","point 3"],
      "slide_type": "intro or analysis or education or cta"
    }}
  ]
}}"""

    print("🤖 Generating combined analysis+education script via ai_client...")
    try:
        data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
        for slide in data.get("slides", []):
            if slide.get("content"):
                slide["content"] = ht.humanize(slide["content"], lang="hi")
        print(f"✅ Script ready: {data.get('video_title','')[:70]}")
        return data
    except Exception as e:
        print(f"⚠️ Script generation error: {e}")
        return _fallback_slides()


def _fallback_slides():
    today_str = datetime.now().strftime("%d %b %Y")
    return {
        "video_title": f"Nifty50 Analysis {today_str} | Breakout Stocks Today | AI360 Trading",
        "main_insight": "Aaj ke top breakout stocks with entry, SL and target levels.",
        "top_stocks": ["NIFTY50"],
        "overall_sentiment": "neutral",
        "slides": [{
            "title": f"Market Overview {today_str}",
            "content": "Namaskar! Aaj ka market analysis le ke aa gaya hoon. Live data load ho raha hai. Subscribe karo daily signals ke liye!",
            "sentiment": "neutral",
            "key_points": ["Subscribe karo","Telegram join karo","ai360trading.in"],
            "slide_type": "intro"
        }] * NUM_SLIDES
    }

# ─── SLIDE RENDERER ───────────────────────────────────────────────────────────
def make_slide(slide, idx, total, path, thumb_text=None):
    snt = slide.get("sentiment","neutral").lower()
    if snt not in THEMES: snt = "neutral"
    th  = THEMES[snt]

    img = Image.new("RGB", (W, H))
    px  = img.load()
    for y in range(H):
        c = lerp(th["bg_top"], th["bg_bot"], y / H)
        for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0,0),(W,12)], fill=th["accent"])
    draw.text((W-40,30), "ai360trading.in", fill=(*th["subtext"],180),
              font=get_font(FONT_REG_PATHS,28), anchor="ra")
    draw.text((40,35), f"{idx} / {total}", fill=(*th["subtext"],200),
              font=get_font(FONT_BOLD_PATHS,32), anchor="la")

    if idx == 1 and thumb_text:
        t1 = get_font(FONT_BOLD_PATHS, 110)
        t2 = get_font(FONT_BOLD_PATHS, 80)
        t3 = get_font(FONT_BOLD_PATHS, 60)
        for dx, dy in [(-3,0),(3,0),(0,-3),(0,3)]:
            draw.text((W//2+dx,200+dy), thumb_text.get("line1",""),
                      font=t1, fill=(0,0,0), anchor="mm")
        draw.text((W//2,200), thumb_text.get("line1",""),
                  font=t1, fill=(255,220,0), anchor="mm")
        draw.text((W//2,330), thumb_text.get("line2",""),
                  font=t2, fill=th["text"], anchor="mm")
        draw.text((W//2,420), thumb_text.get("line3",""),
                  font=t3, fill=th["accent"], anchor="mm")
        draw.rectangle([(80,460),(W-80,464)], fill=th["accent"])
        ty = 510
    else:
        title_font  = get_font(FONT_BOLD_PATHS, 72)
        title_lines = textwrap.wrap(slide["title"].upper(), width=28)
        ty = 140
        for line in title_lines[:2]:
            draw.text((W//2,ty), line, fill=th["text"], font=title_font, anchor="mm")
            ty += 88
        draw.rectangle([(80,ty+20),(W-80,ty+24)], fill=th["accent"])
        ty += 60

    content_font  = get_font(FONT_REG_PATHS, 42)
    content_lines = textwrap.wrap(slide["content"], width=55)
    for line in content_lines[:6]:
        draw.text((80,ty), line, fill=th["text"], font=content_font)
        ty += 58

    if slide.get("key_points"):
        ty += 30
        bf = get_font(FONT_BOLD_PATHS, 38)
        for pt in slide["key_points"][:3]:
            draw.text((80,ty), f"▶ {pt}", fill=th["accent"], font=bf)
            ty += 52

    draw.rectangle([(0,H-10),(W,H)], fill=th["accent"])
    img.save(str(path), quality=95)

# ─── VOICE ────────────────────────────────────────────────────────────────────
async def gen_voice(text, path):
    tts_speed = ht.get_tts_speed()
    rate_pct  = int((tts_speed - 1.0) * 100)
    rate_str  = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
    await edge_tts.Communicate(text, VOICE, rate=rate_str).save(str(path))

# ─── YOUTUBE UPLOAD ───────────────────────────────────────────────────────────
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
            "categoryId":  "25"   # News & Politics — higher CPM for finance
        },
        "status": {
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"🚀 Uploading analysis video: {title[:65]}...")
    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status: print(f"  {int(status.progress() * 100)}%")
        vid_id = response["id"]
        print(f"✅ Uploaded: https://youtube.com/watch?v={vid_id}")
        return vid_id
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None

# ─── BUILD META ───────────────────────────────────────────────────────────────
def build_video_meta(data, today_str):
    vid_title    = data.get("video_title", f"Nifty50 Analysis {today_str} | AI360 Trading")
    main_insight = data.get("main_insight", "Aaj ke top stocks with entry, SL and target.")
    top_stocks   = data.get("top_stocks", [])
    sentiment    = data.get("overall_sentiment", "neutral")

    tags = seo.get_video_tags(
        mode=CONTENT_MODE, is_short=False, channel="trading", lang="both",
        extra_tags=[s.replace("NSE:","")[:20] for s in top_stocks[:3]]
    )
    full_desc = seo.get_description_template(
        title=vid_title, main_insight=main_insight,
        mode=CONTENT_MODE, channel="trading", stocks=top_stocks, lang="hi"
    )
    return vid_title, full_desc, tags, sentiment

# ─── MAIN ─────────────────────────────────────────────────────────────────────
async def run():
    today_str = datetime.now().strftime("%d %b %Y")
    today_fn  = datetime.now().strftime("%Y%m%d")

    data       = generate_slides()
    slides     = data["slides"]
    top_stocks = data.get("top_stocks", [])
    sentiment  = data.get("overall_sentiment", "neutral")

    vid_title, full_desc, tags, sentiment = build_video_meta(data, today_str)

    stock1 = top_stocks[0] if top_stocks else ""
    thumb  = seo.get_thumbnail_text(channel="trading", stock=stock1, mood=sentiment.upper())

    print(f"📋 Title: {vid_title}")
    print(f"🏷️  Tags (first 5): {tags[:5]}")
    print(f"🖼️  Thumbnail: {thumb['line1']} | {thumb['line2']} | {thumb['line3']}")

    # ── Render slides + voices ────────────────────────────────────────────────
    clips = []
    for i, s in enumerate(slides):
        img_path   = OUT / f"an_{i}.png"
        audio_path = OUT / f"an_{i}.mp3"

        make_slide(s, i+1, len(slides), img_path, thumb_text=(thumb if i == 0 else None))
        await gen_voice(s["content"], audio_path)

        voice_clip  = AudioFileClip(str(audio_path))
        duration    = voice_clip.duration + 1.2
        slide_audio = voice_clip   # ← bgmusic removed — not required

        clip = ImageClip(str(img_path)).set_duration(duration).set_audio(slide_audio)
        clips.append(clip)

    # ── Render video ──────────────────────────────────────────────────────────
    video_path = OUT / "analysis_video.mp4"
    concatenate_videoclips(clips, method="compose").write_videofile(
        str(video_path), fps=FPS, codec="libx264", audio_codec="aac",
        remove_temp=True, logger=None
    )

    total_duration = sum(c.duration for c in clips)
    print(f"✅ Video rendered: {video_path.name} | Duration: {total_duration/60:.1f} min")
    if total_duration >= 480:
        print("✅ MID-ROLL ADS ENABLED (video > 8 minutes)")
    else:
        print(f"⚠️  Video {total_duration/60:.1f} min — mid-roll ads need 8+ min")

    # ── Upload to YouTube ─────────────────────────────────────────────────────
    youtube_tags = seo.get_youtube_safe_tags(tags)   # removes Hindi/non-ASCII
    video_id     = upload_to_youtube(video_path, vid_title, full_desc, youtube_tags)

    if video_id:
        id_path = OUT / "analysis_video_id.txt"
        id_path.write_text(video_id, encoding="utf-8")
        print(f"💾 Saved analysis_video_id.txt: {video_id}")
    else:
        (OUT / "analysis_video_id.txt").write_text("UPLOAD_FAILED", encoding="utf-8")

    # ── Save meta JSON ────────────────────────────────────────────────────────
    meta = {
        "title":             vid_title,
        "description":       full_desc,
        "tags":              tags,
        "sentiment":         sentiment,
        "top_stocks":        top_stocks,
        "content_mode":      CONTENT_MODE,
        "duration_minutes":  round(total_duration / 60, 1),
        "mid_roll_eligible": total_duration >= 480,
        "youtube_video_id":  video_id or "",
        "youtube_video_url": f"https://youtube.com/watch?v={video_id}" if video_id else "",
        "thumbnail_text":    thumb,
    }
    meta_path = OUT / f"analysis_meta_{today_fn}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 Saved meta: {meta_path.name}")

    print(f"\n{'='*60}")
    print(f"✅ ANALYSIS DONE — {today_str} [{CONTENT_MODE.upper()}]")
    print(f"   Title    : {vid_title[:65]}")
    print(f"   Duration : {total_duration/60:.1f} min")
    print(f"   Video ID : {video_id or 'FAILED'}")
    print(f"   Tags     : {', '.join(tags[:5])}...")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(run())
