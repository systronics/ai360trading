import os, sys, json, asyncio, textwrap
from datetime import datetime
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, concatenate_audioclips
from groq import Groq
from content_calendar import get_todays_education_topic

# YouTube upload
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── CONFIG ──────────────────────────────────────────────────────────────────
OUT       = Path("output")
MUSIC_DIR = Path("public/music")
W, H      = 1920, 1080
FPS       = 24
VOICE     = "hi-IN-SwaraNeural"
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
LEVEL_THEMES = {
    "Beginner":     {"bg_top": (10, 20, 50), "bg_bot": (20, 40, 90),  "accent": (80, 180, 255),  "text": (240, 250, 255), "subtext": (160, 200, 230)},
    "Intermediate": {"bg_top": (20, 15, 45), "bg_bot": (40, 30, 80),  "accent": (180, 120, 255), "text": (245, 240, 255), "subtext": (190, 160, 230)},
    "Advanced":     {"bg_top": (15, 30, 20), "bg_bot": (30, 60, 40),  "accent": (80, 220, 140),  "text": (240, 255, 245), "subtext": (160, 220, 180)},
    "All Levels":   {"bg_top": (30, 20, 15), "bg_bot": (60, 40, 25),  "accent": (255, 180, 60),  "text": (255, 248, 235), "subtext": (220, 190, 140)},
}

DEFAULT_THEME = LEVEL_THEMES["Beginner"]

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ─── BACKGROUND MUSIC ────────────────────────────────────────────────────────
def get_bg_music():
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

# ─── GROQ SCRIPT ─────────────────────────────────────────────────────────────
def generate_edu_slides(client, topic, part1_url):
    today = datetime.now().strftime("%A, %d %B %Y")

    prompt = f"""You are an expert trading educator creating a YouTube education video in Hinglish (natural Hindi + English mix) for ai360trading channel.

Today is {today}.
Topic: {topic['title']}
Category: {topic['category']}
Level: {topic['level']}
Target audience: {topic.get('target_audience', 'Indian traders of all levels')}

Use the slide structure below as a guide for content (expand each point into spoken content):
{json.dumps(topic.get('slides', []), ensure_ascii=False)}

Generate exactly {len(topic.get('slides', []))} slides matching the structure above.

Respond ONLY with valid JSON, no markdown, no extra text:
{{
  "video_title": "educational Hinglish YouTube title max 70 chars",
  "video_description": "3-4 sentence Hinglish description with key learning points",
  "slides": [
    {{
      "title": "slide heading max 8 words",
      "content": "spoken Hinglish content 50-70 words — clear, simple, with examples",
      "key_takeaway": "one line summary of this slide"
    }}
  ]
}}"""

    print(f"🤖 Generating education script: {topic['title']}...")
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.75,
            max_tokens=2500
        )
        data   = json.loads(resp.choices[0].message.content)
        slides = data.get("slides", [])
        if not slides:
            raise ValueError("No slides in response")
        print(f"✅ {len(slides)} education slides generated")
        return data
    except Exception as e:
        print(f"⚠️ Groq error: {e} — using topic slides directly")
        fallback_slides = []
        for s in topic.get("slides", []):
            fallback_slides.append({
                "title":        s.get("heading", "Trading Lesson"),
                "content":      " ".join(s.get("points", ["Important trading concept hai yeh."])),
                "key_takeaway": s.get("points", ["Learn and apply"])[0]
            })
        return {
            "video_title":       f"{topic['title']} — ai360trading",
            "video_description": f"Aaj hum seekhenge {topic['title']} ke baare mein. Visit ai360trading.in",
            "slides":            fallback_slides
        }

# ─── SLIDE RENDERER (UPDATED FOR 3D DISNEY EFFECT) ──────────────────────────
def make_edu_slide(slide, idx, total, topic, path):
    level = topic.get("level", "Beginner")
    th    = LEVEL_THEMES.get(level, DEFAULT_THEME)

    # Gradient background
    img = Image.new("RGB", (W, H))
    px  = img.load()
    for y in range(H):
        c = lerp(th["bg_top"], th["bg_bot"], y / H)
        for x in range(W):
            px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")

    # 1. ADDING 3D ZENO CHARACTER (Disney Style)
    zeno_emotion = "happy" if idx % 2 == 0 else "thinking"
    zeno_path = Path(f"public/zeno_{zeno_emotion}.png")
    
    if zeno_path.exists():
        zeno = Image.open(zeno_path).convert("RGBA")
        # Scaling: Make him large for "Human Touch" (approx 45% of screen height)
        z_h = int(H * 0.45)
        z_w = int(zeno.width * (z_h / zeno.height))
        zeno = zeno.resize((z_w, z_h), Image.LANCZOS)

        # Create 3D Shadow/Glow
        shadow_layer = Image.new("RGBA", (W, H), (0,0,0,0))
        z_mask = zeno.split()[3]
        shadow_pos = (W - z_w - 60, H - z_h - 40) # Positioned bottom-right
        
        # Soft dark glow
        shadow_color = (0, 0, 0, 90)
        shadow_img = Image.new("RGBA", zeno.size, shadow_color)
        shadow_layer.paste(shadow_img, (shadow_pos[0]+15, shadow_pos[1]+15), z_mask)
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=12))
        
        # Composite Zeno
        img_rgba = img.convert("RGBA")
        img_rgba = Image.alpha_composite(img_rgba, shadow_layer)
        img_rgba.paste(zeno, shadow_pos, zeno)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img, "RGBA")

    # Top accent bar
    draw.rectangle([(0, 0), (W, 10)], fill=th["accent"])

    # Category badge top-left
    draw.text(
        (40, 35), f"📚 {topic['category'].upper()}",
        fill=(*th["subtext"], 220),
        font=get_font(FONT_BOLD_PATHS, 30),
        anchor="la"
    )

    # Level badge top-right
    draw.text(
        (W - 40, 35), f"● {level}",
        fill=(*th["accent"], 200),
        font=get_font(FONT_BOLD_PATHS, 28),
        anchor="ra"
    )

    # Brand watermark
    draw.text(
        (W // 2, 38), "ai360trading.in",
        fill=(*th["subtext"], 160),
        font=get_font(FONT_REG_PATHS, 26),
        anchor="mm"
    )

    # Slide counter
    draw.text(
        (W // 2, 80), f"{idx} of {total}",
        fill=(*th["subtext"], 180),
        font=get_font(FONT_REG_PATHS, 28),
        anchor="mm"
    )

    # Title (Shifted slightly left to accommodate Zeno)
    title_font  = get_font(FONT_BOLD_PATHS, 68)
    title_lines = textwrap.wrap(slide["title"].upper(), width=25)
    ty = 150
    for line in title_lines[:2]:
        draw.text((W // 2 - 100, ty), line, fill=th["text"], font=title_font, anchor="mm")
        ty += 84

    # Accent divider
    draw.rectangle([(80, ty + 15), (W - 400, ty + 19)], fill=th["accent"])
    ty += 55

    # Content (Wrapped narrower so it doesn't overlap Zeno)
    content_font  = get_font(FONT_REG_PATHS, 40)
    content_lines = textwrap.wrap(slide["content"], width=45)
    for line in content_lines[:7]:
        draw.text((80, ty), line, fill=th["text"], font=content_font)
        ty += 54

    # Key takeaway box
    if slide.get("key_takeaway"):
        ty += 20
        box_top = ty
        box_bot = ty + 70
        draw.rectangle([(60, box_top), (W - 450, box_bot)], fill=(*th["accent"], 30))
        draw.rectangle([(60, box_top), (63, box_bot)], fill=th["accent"])
        draw.text(
            (90, box_top + 35),
            f"💡 {slide['key_takeaway']}",
            fill=th["accent"],
            font=get_font(FONT_BOLD_PATHS, 34),
            anchor="lm"
        )

    # Bottom accent bar
    draw.rectangle([(0, H - 10), (W, H)], fill=th["accent"])

    img.save(str(path), quality=95)

# ─── VOICE ───────────────────────────────────────────────────────────────────
async def gen_voice(text, path):
    await edge_tts.Communicate(text, VOICE).save(str(path))

# ─── YOUTUBE HELPERS ─────────────────────────────────────────────────────────
def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json:
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
            "categoryId":  "27"
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
        video_id = response["id"]
        print(f"✅ YouTube upload success! ID: {video_id}")
        print(f"🔗 URL: https://youtube.com/watch?v={video_id}")
        return video_id
    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        return None

def update_part1_description(part1_id, part1_desc, part2_url):
    youtube = get_youtube_service()
    if not youtube or not part1_id or part1_id == "UPLOAD_FAILED":
        return
    try:
        resp    = youtube.videos().list(part="snippet", id=part1_id).execute()
        if not resp.get("items"):
            return
        snippet = resp["items"][0]["snippet"]
        snippet["description"] = (
            snippet.get("description", part1_desc) +
            f"\n\n▶️ Part 2 — Education Video: {part2_url}"
        )
        youtube.videos().update(
            part="snippet",
            body={"id": part1_id, "snippet": snippet}
        ).execute()
        print(f"✅ Part 1 description updated with Part 2 link")
    except Exception as e:
        print(f"⚠️ Could not update Part 1 description: {e}")

# ─── MAIN ────────────────────────────────────────────────────────────────────
async def run():
    today  = datetime.now().strftime("%Y%m%d")
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    part1_id  = ""
    part1_url = ""
    id_path   = OUT / "analysis_video_id.txt"
    if id_path.exists():
        part1_id = id_path.read_text(encoding="utf-8").strip()
        if part1_id and part1_id != "UPLOAD_FAILED":
            part1_url = f"https://youtube.com/watch?v={part1_id}"
            print(f"🔗 Part 1 linked: {part1_url}")
        else:
            print("⚠️ Part 1 upload failed — continuing without link")
    else:
        print("⚠️ No analysis_video_id.txt found — continuing without Part 1 link")

    topic = get_todays_education_topic()
    print(f"📚 Topic: {topic['title']} | {topic['category']} | {topic['level']}")

    data   = generate_edu_slides(client, topic, part1_url)
    slides = data["slides"]

    vid_title = data.get("video_title", f"{topic['title']} — ai360trading")
    vid_desc  = data.get("video_description", f"Learn {topic['title']} with ai360trading.in")

    part1_section = f"\n▶️ Part 1 — Market Analysis: {part1_url}\n" if part1_url else ""
    full_desc = (
        f"{vid_desc}\n\n"
        f"📚 Topic: {topic['title']}\n"
        f"🎯 Level: {topic['level']} | Category: {topic['category']}\n"
        f"{part1_section}"
        f"🌐 Website: https://ai360trading.in\n"
        f"📱 Telegram: https://t.me/ai360trading\n"
        f"📺 Subscribe for daily education!\n\n"
        f"#{topic['category'].replace(' ', '')} #TradingEducation #ai360trading "
        f"#StockMarketIndia #Hinglish #LearnTrading #NSE #BSE #TradingIndia"
    )

    print(f"\n🎬 Building {len(slides)} education slides with 3D Zeno...")
    clips = []
    for i, s in enumerate(slides):
        img_path   = OUT / f"edu_{i}.png"
        audio_path = OUT / f"edu_{i}.mp3"

        make_edu_slide(s, i + 1, len(slides), topic, img_path)
        await gen_voice(s["content"], audio_path)

        voice_clip = AudioFileClip(str(audio_path))
        duration   = voice_clip.duration + 0.8

        bg_music_path = get_bg_music()
        if bg_music_path:
            try:
                bg = AudioFileClip(str(bg_music_path))
                if bg.duration < duration:
                    loops = int(duration / bg.duration) + 1
                    bg    = concatenate_audioclips([bg] * loops)
                bg          = bg.subclip(0, duration).volumex(0.07)
                slide_audio = CompositeAudioClip([voice_clip, bg])
            except Exception as e:
                print(f"⚠️ Music error slide {i}: {e}")
                slide_audio = voice_clip
        else:
            slide_audio = voice_clip

        clip = ImageClip(str(img_path)).set_duration(duration).set_audio(slide_audio)
        clips.append(clip)
        print(f"   Slide {i+1}/{len(slides)} ready")

    video_path = OUT / "education_video.mp4"
    print(f"\n🎥 Rendering education video...")
    concatenate_videoclips(clips, method="compose").write_videofile(
        str(video_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(OUT / "temp_edu_audio.mp3"),
        remove_temp=True,
        logger=None
    )
    print(f"✅ Video rendered: {video_path}")

    tags = [
        topic["title"], topic["category"], "Trading Education", "ai360trading",
        "Stock Market India", "Learn Trading", "NSE", "BSE",
        "Hinglish", "Trading India", topic["level"]
    ]
    part2_id = upload_to_youtube(video_path, vid_title, full_desc, tags)

    if part2_id:
        (OUT / "education_video_id.txt").write_text(part2_id, encoding="utf-8")
        part2_url = f"https://youtube.com/watch?v={part2_id}"
        print(f"✅ Education video ID saved")

        if part1_id and part1_id != "UPLOAD_FAILED":
            update_part1_description(part1_id, full_desc, part2_url)

        meta = {
            "title":        vid_title,
            "description": full_desc,
            "video_id":    part2_id,
            "video_url":   part2_url,
            "part1_url":   part1_url,
            "topic":       topic["title"],
            "category":    topic["category"],
            "level":       topic["level"],
            "date":        today
        }
        (OUT / f"education_meta_{today}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"✅ Education meta saved")
    else:
        print("⚠️ Upload failed — saving placeholder")
        (OUT / "education_video_id.txt").write_text("UPLOAD_FAILED", encoding="utf-8")

if __name__ == "__main__":
    asyncio.run(run())
