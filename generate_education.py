import os, sys, json, asyncio, textwrap, logging
from datetime import datetime
from pathlib import Path
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, concatenate_audioclips

# YouTube upload
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ── Bug 1: Log suppression — no more 50-line JSON dumps ──────────────────────
logging.getLogger("moviepy").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)

# ── Bug 3 + Bug 4: Use ai_client fallback chain — no direct Groq import ──────
from ai_client import ai
from human_touch import ht, seo
from content_calendar import get_todays_education_topic

# ─── CONFIG ──────────────────────────────────────────────────────────────────
OUT          = Path("output")
MUSIC_DIR    = Path("public/music")
W, H         = 1920, 1080
FPS          = 24
VOICE        = "hi-IN-SwaraNeural"
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()

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
    "Beginner":     {"bg_top": (10, 20, 50),  "bg_bot": (20, 40, 90),  "accent": (80, 180, 255),  "text": (240, 250, 255), "subtext": (160, 200, 230)},
    "Intermediate": {"bg_top": (20, 15, 45),  "bg_bot": (40, 30, 80),  "accent": (180, 120, 255), "text": (245, 240, 255), "subtext": (190, 160, 230)},
    "Advanced":     {"bg_top": (15, 30, 20),  "bg_bot": (30, 60, 40),  "accent": (80, 220, 140),  "text": (240, 255, 245), "subtext": (160, 220, 180)},
    "All Levels":   {"bg_top": (30, 20, 15),  "bg_bot": (60, 40, 25),  "accent": (255, 180, 60),  "text": (255, 248, 235), "subtext": (220, 190, 140)},
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

# ─── SCRIPT GENERATION ───────────────────────────────────────────────────────
def generate_edu_slides(topic, part1_url):
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

    print(f"🤖 Generating education script: {topic['title']} via ai_client...")
    data = ai.generate_json(
        prompt=prompt,
        content_mode=CONTENT_MODE,
        lang="hi"
    )

    if not data or not data.get("slides"):
        print(f"⚠️ JSON generation failed — using topic slides directly")
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

    # Apply human touch to each slide's content
    for slide in data.get("slides", []):
        slide["content"] = ht.humanize(slide.get("content", ""), lang="hi")

    print(f"✅ {len(data.get('slides', []))} education slides generated via {ai.active_provider}")
    return data

# ─── SLIDE RENDERER ──────────────────────────────────────────────────────────
def make_edu_slide(slide, idx, total, topic, path):
    level = topic.get("level", "Beginner")
    th    = LEVEL_THEMES.get(level, DEFAULT_THEME)

    img = Image.new("RGB", (W, H))
    px  = img.load()
    for y in range(H):
        c = lerp(th["bg_top"], th["bg_bot"], y / H)
        for x in range(W):
            px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0, 0), (W, 10)], fill=th["accent"])

    draw.text((40, 35), f"📚 {topic['category'].upper()}",
              fill=(*th["subtext"], 220), font=get_font(FONT_BOLD_PATHS, 30), anchor="la")
    draw.text((W - 40, 35), f"● {level}",
              fill=(*th["accent"], 200), font=get_font(FONT_BOLD_PATHS, 28), anchor="ra")
    draw.text((W // 2, 38), "ai360trading.in",
              fill=(*th["subtext"], 160), font=get_font(FONT_REG_PATHS, 26), anchor="mm")
    draw.text((W // 2, 80), f"{idx} of {total}",
              fill=(*th["subtext"], 180), font=get_font(FONT_REG_PATHS, 28), anchor="mm")

    title_font  = get_font(FONT_BOLD_PATHS, 68)
    title_lines = textwrap.wrap(slide["title"].upper(), width=30)
    ty = 150
    for line in title_lines[:2]:
        draw.text((W // 2, ty), line, fill=th["text"], font=title_font, anchor="mm")
        ty += 84

    draw.rectangle([(80, ty + 15), (W - 80, ty + 19)], fill=th["accent"])
    ty += 55

    content_font  = get_font(FONT_REG_PATHS, 40)
    content_lines = textwrap.wrap(slide["content"], width=58)
    for line in content_lines[:7]:
        draw.text((80, ty), line, fill=th["text"], font=content_font)
        ty += 54

    if slide.get("key_takeaway"):
        ty      += 20
        box_top  = ty
        box_bot  = ty + 70
        draw.rectangle([(60, box_top), (W - 60, box_bot)], fill=(*th["accent"], 30))
        draw.rectangle([(60, box_top), (63, box_bot)], fill=th["accent"])
        draw.text((90, box_top + 35), f"💡 {slide['key_takeaway']}",
                  fill=th["accent"], font=get_font(FONT_BOLD_PATHS, 34), anchor="lm")

    draw.rectangle([(0, H - 10), (W, H)], fill=th["accent"])
    img.save(str(path), quality=95)

# ─── VOICE ───────────────────────────────────────────────────────────────────
async def gen_voice(text, path):
    tts_speed = ht.get_tts_speed()
    rate_pct  = int((tts_speed - 1.0) * 100)
    rate_str  = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
    await edge_tts.Communicate(text, VOICE, rate=rate_str).save(str(path))

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
                print(f"  Uploaded {int(status.progress() * 100)}%")
        video_id = response["id"]
        print(f"✅ YouTube upload success! ID: {video_id}")
        print(f"🔗 URL: https://youtube.com/watch?v={video_id}")
        return video_id
    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        return None


def update_part1_description(part1_id, part1_desc, part2_url):
    """Adds Part 2 link to Part 1 video description."""
    youtube = get_youtube_service()
    if not youtube or not part1_id or part1_id == "UPLOAD_FAILED":
        return
    try:
        resp = youtube.videos().list(part="snippet", id=part1_id).execute()
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
    today = datetime.now().strftime("%Y%m%d")

    # 1. Read Part 1 video ID (saved by generate_analysis.py)
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

    # 2. Get today's education topic
    topic = get_todays_education_topic()
    print(f"📚 Topic: {topic['title']} | {topic['category']} | {topic['level']}")

    # 3. Generate script
    data     = generate_edu_slides(topic, part1_url)
    slides   = data["slides"]
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

    # 4. Build slides and voice
    print(f"\n🎬 Building {len(slides)} education slides...")
    clips = []
    for i, s in enumerate(slides):
        img_path   = OUT / f"edu_{i}.png"
        audio_path = OUT / f"edu_{i}.mp3"

        make_edu_slide(s, i + 1, len(slides), topic, img_path)
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
                bg          = bg.subclip(0, duration).volumex(0.07)
                slide_audio = CompositeAudioClip([voice_clip, bg])
            except Exception as e:
                print(f"⚠️ Music error slide {i}: {e}")
                slide_audio = voice_clip
        else:
            slide_audio = voice_clip

        clip = ImageClip(str(img_path)).set_duration(duration).set_audio(slide_audio)
        clips.append(clip)
        print(f"  Slide {i+1}/{len(slides)} ready")

    # 5. Render video
    video_path = OUT / "education_video.mp4"
    print(f"\n🎥 Rendering education video...")
    concatenate_videoclips(clips, method="compose").write_videofile(
        str(video_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(OUT / "temp_edu_audio.aac"),
        remove_temp=True,
        logger=None
    )
    print(f"✅ Video rendered: {video_path}")

    # 6. Upload to YouTube
    tags    = seo.get_video_tags(mode=CONTENT_MODE)
    tag_list = [topic["title"], topic["category"], "Trading Education", "ai360trading",
                "Stock Market India", "Learn Trading", "NSE", "BSE",
                "Hinglish", "Trading India", topic["level"]]

    part2_id = upload_to_youtube(video_path, vid_title, full_desc, tag_list)

    # 7. Save Part 2 ID and update Part 1 description
    if part2_id:
        (OUT / "education_video_id.txt").write_text(part2_id, encoding="utf-8")
        part2_url = f"https://youtube.com/watch?v={part2_id}"
        print(f"✅ Education video ID saved")
        print(f"   AI: {ai.active_provider}")

        if part1_id and part1_id != "UPLOAD_FAILED":
            update_part1_description(part1_id, full_desc, part2_url)

        meta = {
            "title":       vid_title,
            "description": full_desc,
            "video_id":    part2_id,
            "video_url":   part2_url,
            "part1_url":   part1_url,
            "topic":       topic["title"],
            "category":    topic["category"],
            "level":       topic["level"],
            "ai_provider": ai.active_provider,
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
