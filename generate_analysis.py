import os, sys, json, asyncio, textwrap, random
from datetime import datetime
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, concatenate_audioclips
from groq import Groq

# YouTube upload
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── CONFIG ──────────────────────────────────────────────────────────────────
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

# ─── BACKGROUND MUSIC ────────────────────────────────────────────────────────
def get_bg_music():
    """Day-based rotation — same logic as generate_reel.py for consistency."""
    day = datetime.now().weekday()
    music_map = {
        0: "bgmusic1.mp3", 1: "bgmusic2.mp3", 2: "bgmusic3.mp3",
        3: "bgmusic1.mp3", 4: "bgmusic2.mp3", 5: "bgmusic3.mp3", 6: "bgmusic1.mp3"
    }
    f = MUSIC_DIR / music_map[day]
    if f.exists():
        print(f"🎵 Background music: {f.name}")
        return f
    for f in MUSIC_DIR.glob("*.mp3"):
        print(f"🎵 Fallback music: {f.name}")
        return f
    print("⚠️ No background music found — voice only")
    return None

# ─── WEEKEND DETECTION ───────────────────────────────────────────────────────
def is_weekend():
    return datetime.now().weekday() >= 5

# ─── GROQ SCRIPT ─────────────────────────────────────────────────────────────
def generate_slides(client):
    today     = datetime.now().strftime("%A, %d %B %Y")
    weekend   = is_weekend()
    today_str = datetime.now().strftime("%Y-%m-%d")

    if weekend:
        market_context = "evergreen educational content about Indian and global markets — no live data needed"
    else:
        market_context = "today's Indian and global market analysis — Nifty, BankNifty, global indices, FII/DII activity, key levels"

    prompt = f"""You are an expert Indian market analyst creating a professional YouTube video script in Hinglish (natural Hindi + English mix) for ai360trading channel.

Today is {today}. Create analysis for: {market_context}

Generate exactly 8 slides. Each slide should be educational, clear, and actionable.

Respond ONLY with valid JSON, no markdown, no extra text:
{{
  "video_title": "compelling Hinglish YouTube title max 70 chars with today's date {today_str}",
  "video_description": "3-4 sentence Hinglish description with key insights, include ai360trading.in link",
  "overall_sentiment": "bullish or bearish or neutral",
  "slides": [
    {{
      "title": "slide heading max 8 words",
      "content": "spoken content 40-60 words in Hinglish — clear, simple, actionable",
      "sentiment": "bullish or bearish or neutral",
      "key_points": ["point 1", "point 2", "point 3"]
    }}
  ]
}}

Slide topics must cover:
1. Market Overview — overall sentiment today
2. Nifty 50 Analysis — key levels support resistance
3. BankNifty Analysis — banking sector outlook
4. Global Markets — US S&P500, Asia, Europe impact
5. FII DII Activity — foreign and domestic flows
6. Sector Rotation — which sectors to watch
7. Key Stocks — 2-3 stocks with setups
8. Trading Plan — actionable levels for tomorrow"""

    print("🤖 Generating market analysis script via Groq...")
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000
        )
        data = json.loads(resp.choices[0].message.content)
        slides = data.get("slides", [])
        if not slides:
            raise ValueError("No slides in response")
        print(f"✅ {len(slides)} slides generated — sentiment: {data.get('overall_sentiment')}")
        return data
    except Exception as e:
        print(f"⚠️ Groq error: {e} — using fallback")
        return _fallback_slides()

def _fallback_slides():
    return {
        "video_title": f"Aaj Ka Market Analysis — {datetime.now().strftime('%d %B %Y')}",
        "video_description": "Aaj ke market ki poori analysis — Nifty, BankNifty, global markets aur trading plan. Visit ai360trading.in",
        "overall_sentiment": "neutral",
        "slides": [
            {"title": "Market Overview", "content": "Aaj market mein mixed signals dikh rahe hain. Traders ko patience rakhni chahiye aur key levels ka wait karna chahiye.", "sentiment": "neutral", "key_points": ["Mixed signals", "Wait for clarity", "Key levels important"]},
            {"title": "Nifty Analysis", "content": "Nifty ke liye 22000 strong support hai. Agar yeh level hold karta hai toh 22500 tak bounce possible hai.", "sentiment": "neutral", "key_points": ["22000 support", "22500 target", "Watch volume"]},
            {"title": "BankNifty Outlook", "content": "BankNifty banking sector pe focus karo. 46000 pe strong support hai. Break hone pe 45000 tak correction possible.", "sentiment": "neutral", "key_points": ["46000 support", "Banking sector", "Monitor closely"]},
            {"title": "Global Markets", "content": "US markets mein stability dikh rahi hai. Asian markets mixed hain. Global cues positive hain overall.", "sentiment": "neutral", "key_points": ["US stable", "Asia mixed", "Watch Fed"]},
            {"title": "FII DII Activity", "content": "FII net sellers hain aaj. DII buying support de rahe hain market ko. Domestic flows positive hain.", "sentiment": "neutral", "key_points": ["FII selling", "DII buying", "Net neutral"]},
            {"title": "Sector Watch", "content": "IT sector mein momentum dikh raha hai. Banking consolidation mein hai. Pharma defensive play ke liye accha hai.", "sentiment": "neutral", "key_points": ["IT positive", "Banking neutral", "Pharma defensive"]},
            {"title": "Key Stocks", "content": "Infosys aur TCS IT sector mein strong hain. HDFC Bank support pe hai. Reliance breakout ke liye watch karo.", "sentiment": "neutral", "key_points": ["Infosys", "HDFC Bank", "Reliance"]},
            {"title": "Tomorrow Trading Plan", "content": "Kal ke liye — Nifty 22000 hold kare toh buy on dips. Stop loss 21800. Target 22300. Risk management zaroori hai.", "sentiment": "neutral", "key_points": ["Buy on dips", "SL 21800", "Target 22300"]},
        ]
    }

# ─── SLIDE RENDERER ──────────────────────────────────────────────────────────
def make_slide(slide, idx, total, path):
    snt = slide.get("sentiment", "neutral").lower()
    if snt not in THEMES:
        snt = "neutral"
    th = THEMES[snt]

    # Gradient background
    img = Image.new("RGB", (W, H))
    px  = img.load()
    for y in range(H):
        c = lerp(th["bg_top"], th["bg_bot"], y / H)
        for x in range(W):
            px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")

    # Top accent bar
    draw.rectangle([(0, 0), (W, 10)], fill=th["accent"])

    # Brand watermark top-right
    draw.text(
        (W - 40, 30), "ai360trading.in",
        fill=(*th["subtext"], 180),
        font=get_font(FONT_REG_PATHS, 28),
        anchor="ra"
    )

    # Slide counter top-left
    draw.text(
        (40, 35), f"{idx} / {total}",
        fill=(*th["subtext"], 200),
        font=get_font(FONT_BOLD_PATHS, 32),
        anchor="la"
    )

    # Title
    title_font = get_font(FONT_BOLD_PATHS, 72)
    title_lines = textwrap.wrap(slide["title"].upper(), width=28)
    ty = 140
    for line in title_lines[:2]:
        draw.text((W // 2, ty), line, fill=th["text"], font=title_font, anchor="mm")
        ty += 88

    # Accent divider
    draw.rectangle([(80, ty + 20), (W - 80, ty + 24)], fill=th["accent"])
    ty += 60

    # Content
    content_font = get_font(FONT_REG_PATHS, 42)
    content_lines = textwrap.wrap(slide["content"], width=55)
    for line in content_lines[:6]:
        draw.text((80, ty), line, fill=th["text"], font=content_font)
        ty += 58

    # Key points bullets
    if slide.get("key_points"):
        ty += 30
        bullet_font = get_font(FONT_BOLD_PATHS, 38)
        for pt in slide["key_points"][:3]:
            draw.text((80, ty), f"▶  {pt}", fill=th["accent"], font=bullet_font)
            ty += 52

    # Bottom accent bar
    draw.rectangle([(0, H - 10), (W, H)], fill=th["accent"])

    # Bottom sentiment badge
    badge_text = f"  {snt.upper()}  "
    badge_font = get_font(FONT_BOLD_PATHS, 30)
    draw.text((W // 2, H - 40), badge_text, fill=th["accent"], font=badge_font, anchor="mm")

    img.save(str(path), quality=95)

# ─── VOICE ───────────────────────────────────────────────────────────────────
async def gen_voice(text, path):
    await edge_tts.Communicate(text, VOICE).save(str(path))

# ─── YOUTUBE UPLOAD ──────────────────────────────────────────────────────────
def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json:
            # Fallback: try token.json file written by workflow
            if os.path.exists("token.json"):
                with open("token.json") as f:
                    creds_json = f.read()
            else:
                print("❌ No YouTube credentials found")
                return None
        info  = json.loads(creds_json)
        creds = Credentials.from_authorized_user_info(info)
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"❌ YouTube auth error: {e}")
        return None

def upload_to_youtube(video_path, title, description, tags):
    youtube = get_youtube_service()
    if not youtube:
        return None

    body = {
        "snippet": {
            "title":       title[:100],
            "description": description,
            "tags":        tags,
            "categoryId":  "27"   # Education
        },
        "status": {
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"🚀 Uploading to YouTube: {title[:60]}...")

    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   Uploaded {int(status.progress() * 100)}%")
        video_id  = response["id"]
        video_url = f"https://youtube.com/watch?v={video_id}"
        print(f"✅ YouTube upload success! ID: {video_id}")
        print(f"🔗 URL: {video_url}")
        return video_id
    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        return None

def update_video_description(video_id, new_description):
    """Updates a video's description — used to add Part 2 link to Part 1."""
    youtube = get_youtube_service()
    if not youtube or not video_id:
        return
    try:
        resp = youtube.videos().list(part="snippet", id=video_id).execute()
        if not resp.get("items"):
            return
        snippet = resp["items"][0]["snippet"]
        snippet["description"] = new_description
        youtube.videos().update(
            part="snippet",
            body={"id": video_id, "snippet": snippet}
        ).execute()
        print(f"✅ Part 1 description updated with Part 2 link")
    except Exception as e:
        print(f"⚠️ Could not update description: {e}")

# ─── MAIN ────────────────────────────────────────────────────────────────────
async def run():
    today   = datetime.now().strftime("%Y%m%d")
    client  = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # 1. Generate script
    data      = generate_slides(client)
    slides    = data["slides"]
    sentiment = data.get("overall_sentiment", "neutral")
    vid_title = data.get("video_title", f"Aaj Ka Market Analysis — {today}")
    vid_desc  = data.get("video_description", "Daily market analysis by ai360trading.in")

    # Full SEO description
    full_desc = (
        f"{vid_desc}\n\n"
        f"📊 Topics: Nifty | BankNifty | Global Markets | FII/DII | Sector Analysis\n"
        f"🌐 Website: https://ai360trading.in\n"
        f"📱 Telegram: https://t.me/ai360trading\n"
        f"📺 Subscribe for daily market analysis!\n\n"
        f"#Nifty #BankNifty #StockMarket #Trading #ai360trading #MarketAnalysis "
        f"#NSE #BSE #TradingIndia #Hinglish #StockMarketIndia"
    )

    # 2. Build slides and voice
    print(f"\n🎬 Building {len(slides)} slides...")
    clips = []
    for i, s in enumerate(slides):
        img_path   = OUT / f"analysis_{i}.png"
        audio_path = OUT / f"analysis_{i}.mp3"

        make_slide(s, i + 1, len(slides), img_path)
        await gen_voice(s["content"], audio_path)

        voice_clip = AudioFileClip(str(audio_path))
        duration   = voice_clip.duration + 0.8   # small pause between slides

        # Add background music to each slide
        bg_music_path = get_bg_music()
        if bg_music_path:
            try:
                bg = AudioFileClip(str(bg_music_path))
                if bg.duration < duration:
                    loops = int(duration / bg.duration) + 1
                    bg    = concatenate_audioclips([bg] * loops)
                bg          = bg.subclip(0, duration).volumex(0.07)   # 7% volume
                slide_audio = CompositeAudioClip([voice_clip, bg])
            except Exception as e:
                print(f"⚠️ Music error slide {i}: {e}")
                slide_audio = voice_clip
        else:
            slide_audio = voice_clip

        clip = ImageClip(str(img_path)).set_duration(duration).set_audio(slide_audio)
        clips.append(clip)
        print(f"   Slide {i+1}/{len(slides)} ready")

    # 3. Render video
    video_path = OUT / "analysis_video.mp4"
    print(f"\n🎥 Rendering analysis video...")
    concatenate_videoclips(clips, method="compose").write_videofile(
        str(video_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(OUT / "temp_analysis_audio.mp3"),
        remove_temp=True,
        logger=None
    )
    print(f"✅ Video rendered: {video_path}")

    # 4. Upload to YouTube
    tags = [
        "Nifty", "BankNifty", "Stock Market", "Trading", "ai360trading",
        "Market Analysis", "NSE", "BSE", "Trading India", "Hinglish",
        "Stock Market India", "Nifty Analysis", "Indian Market"
    ]
    video_id = upload_to_youtube(video_path, vid_title, full_desc, tags)

    # 5. Save video ID for generate_education.py and generate_shorts.py
    if video_id:
        id_path = OUT / "analysis_video_id.txt"
        id_path.write_text(video_id, encoding="utf-8")
        print(f"✅ Video ID saved: {id_path}")

        # Also save metadata for Facebook sharing
        meta = {
            "title":       vid_title,
            "description": full_desc,
            "video_id":    video_id,
            "video_url":   f"https://youtube.com/watch?v={video_id}",
            "sentiment":   sentiment,
            "date":        today
        }
        (OUT / f"analysis_meta_{today}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"✅ Analysis meta saved")
    else:
        print("⚠️ Upload failed — saving placeholder video ID")
        (OUT / "analysis_video_id.txt").write_text("UPLOAD_FAILED", encoding="utf-8")

if __name__ == "__main__":
    asyncio.run(run())
