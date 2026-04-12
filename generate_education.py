"""
generate_education.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Educational deep-dive video (Part 2) — 16:9 format
Target: 10–12 minutes (safely above 8-min mid-roll ad threshold)
Slide count: 22 slides minimum @ ~80-100 words each = ~10-14 min raw
Phase 2 — Mode-aware, bilingual SEO, ai_client + human_touch

Last updated: April 2026 — expanded from 12→22 slides for mid-roll ads
"""

import os
import sys
import json
import asyncio
import textwrap
from datetime import datetime
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip,
    concatenate_videoclips, concatenate_audioclips
)

from ai_client import ai
from human_touch import ht, seo
from content_calendar import get_todays_education_topic

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── CONFIG ───────────────────────────────────────────────────────────────────

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "")

OUT       = Path("output")
MUSIC_DIR = Path("public/music")
W, H      = 1920, 1080
FPS       = 24
VOICE     = "hi-IN-SwaraNeural"

# ✅ KEY FIX: 22 slides minimum, 80-100 words each = 10-12 min
MIN_SLIDES   = 22
WORDS_TARGET = "110-130"

os.makedirs(OUT, exist_ok=True)

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

print(f"[MODE] generate_education.py running in mode: {CONTENT_MODE.upper()}")

# ─── FONTS ────────────────────────────────────────────────────────────────────

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

# ─── THEMES ───────────────────────────────────────────────────────────────────

LEVEL_THEMES = {
    "Beginner":     {"bg_top": (10, 20, 50),  "bg_bot": (20, 40, 90),  "accent": (80, 180, 255),  "text": (240, 250, 255), "subtext": (160, 200, 230)},
    "Intermediate": {"bg_top": (20, 15, 45),  "bg_bot": (40, 30, 80),  "accent": (180, 120, 255), "text": (245, 240, 255), "subtext": (190, 160, 230)},
    "Advanced":     {"bg_top": (15, 30, 20),  "bg_bot": (30, 60, 40),  "accent": (80, 220, 140),  "text": (240, 255, 245), "subtext": (160, 220, 180)},
    "All Levels":   {"bg_top": (30, 20, 15),  "bg_bot": (60, 40, 25),  "accent": (255, 180, 60),  "text": (255, 248, 235), "subtext": (220, 190, 140)},
}
DEFAULT_THEME = LEVEL_THEMES["Beginner"]

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ─── BACKGROUND MUSIC ─────────────────────────────────────────────────────────

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

# ─── SLIDE EXPANSION HEADINGS ─────────────────────────────────────────────────
# Used to pad topics that have fewer than 22 slide headings

EXPANSION_SLIDES = [
    "Common Mistakes Traders Make",
    "Risk Management Is Key",
    "Psychology Angle — Why Most Fail",
    "Real Indian Stock Example",
    "Step-by-Step Guide Part 1",
    "Step-by-Step Guide Part 2",
    "Global Market Context (USA/UK)",
    "Advanced Tip for Experienced Traders",
    "Q&A — Aapko Kya Lagta Hai?",
    "Action Plan — This Week",
    "Quick Quiz for Viewers",
    "Summary of Key Points",
    "Outro — Subscribe + Telegram CTA",
]

# ─── SCRIPT GENERATION ────────────────────────────────────────────────────────

def generate_edu_slides(topic, part1_url):
    """
    Generate 22-slide education script via ai_client full fallback chain.
    Never calls Groq/Gemini/Claude/OpenAI directly.
    """
    today = datetime.now().strftime("%A, %d %B %Y")

    # Build 22-slide heading list from topic + expansion
    topic_slides   = topic.get("slides", [])
    slide_headings = [s.get("heading", f"Slide {i+1}") for i, s in enumerate(topic_slides)]
    while len(slide_headings) < MIN_SLIDES:
        idx = len(slide_headings) - len(topic_slides)
        slide_headings.append(EXPANSION_SLIDES[idx % len(EXPANSION_SLIDES)])

    # Get rotating hook from human_touch — anti-AI-penalty
    hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")

    prompt = f"""You are an expert trading educator creating a YouTube education video in Hinglish (natural Hindi + English mix) for ai360trading channel.

Today is {today}.
Topic: {topic['title']}
Category: {topic['category']}
Level: {topic['level']}
Target audience: {topic.get('target_audience', 'Indian traders of all levels')}
Content mode: {CONTENT_MODE}

Opening hook for slide 1: "{hook}"

Generate EXACTLY {MIN_SLIDES} slides using these headings in order:
{json.dumps(slide_headings, ensure_ascii=False)}

IMPORTANT RULES:
- Each slide content MUST be EXACTLY {WORDS_TARGET} words of spoken Hinglish. Count every word carefully before writing. Slides under 100 words are REJECTED. This is non-negotiable — the video must be 10+ minutes.
- Natural conversational Hinglish — Hindi + English mix like a real trader speaks
- Include real Indian stock/market examples where relevant
- Slide 17 must include USA/UK/global market context for international viewers
- Slide {MIN_SLIDES} must end with: "Subscribe karo, Telegram join karo t.me/ai360trading, aur Part 1 dekhna mat bhoolna!"
- Holiday/weekend mode: keep educational, no live market specifics
- Market mode: include Nifty/NSE context naturally

Respond ONLY with valid JSON, no markdown, no extra text:
{{
  "video_title": "Hinglish YouTube title max 70 chars",
  "video_description": "3-4 sentence Hinglish description with key learning points",
  "slides": [
    {{
      "title": "slide heading max 8 words",
      "content": "spoken Hinglish content {WORDS_TARGET} words",
      "key_takeaway": "one line summary max 12 words"
    }}
  ]
}}"""

    print(f"🤖 Generating {MIN_SLIDES}-slide education script via ai_client: {topic['title']}...")

    data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")

    if data and data.get("slides") and len(data["slides"]) >= 10:
        slides = data["slides"]
        # Pad if AI returned fewer than MIN_SLIDES
        while len(slides) < MIN_SLIDES:
            idx = len(slides) - len(topic_slides)
            heading = slide_headings[len(slides)] if len(slides) < len(slide_headings) else "Key Lesson"
            slides.append({
                "title": heading,
                "content": (
                    "Trading mein sabse important cheez hai discipline aur patience. "
                    "Jo trader apni emotions control karta hai, woh long term mein zaroor profitable hota hai. "
                    "Market mein ups and downs aate rehte hain, lekin jo log consistent rehte hain woh aakhir mein jeette hain. "
                    "Risk management seekho, position sizing samjho, aur har trade se kuch na kuch seekhte raho. "
                    "Yahi hai successful trading ka asli raaz."
                ),
                "key_takeaway": "Discipline aur patience — trading ka asli secret"
            })
        data["slides"] = slides[:MIN_SLIDES]
        print(f"✅ {len(data['slides'])} education slides generated via {ai.active_provider}")
        return data

    else:
        print("⚠️ AI returned insufficient slides — building from topic calendar")
        fallback_slides = []
        for i, heading in enumerate(slide_headings):
            if i < len(topic_slides):
                s = topic_slides[i]
                content = " ".join(s.get("points", []))
                if len(content.split()) < 40:
                    content += (
                        f" {heading} ke baare mein aur gehraai se samjhte hain. "
                        "Yeh concept Indian stock market mein bahut important role play karta hai. "
                        "Practical examples se samjhenge kaise yeh apni trading mein apply kar sakte hain. "
                        "Systematic approach aur consistent practice se yeh skill develop hoti hai."
                    )
            else:
                content = (
                    f"{heading} trading ka ek bahut important aspect hai. "
                    "Sabse pehle yeh samajhna hoga ki successful traders kaise sochte hain aur apne decisions kaise lete hain. "
                    "Indian market mein yeh concept specially important hai kyunki humari market global markets se connect hai. "
                    "Practice aur consistency se yeh skill develop hoti hai, aur har din kuch na kuch seekhte raho."
                )
            fallback_slides.append({
                "title": heading,
                "content": content,
                "key_takeaway": f"{heading} — zaroor yaad rakhein"
            })
        return {
            "video_title": f"{topic['title']} — ai360trading Education",
            "video_description": f"Aaj hum seekhenge {topic['title']} ke baare mein. Visit ai360trading.in for more.",
            "slides": fallback_slides
        }

# ─── SLIDE RENDERER ───────────────────────────────────────────────────────────

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

    # Top accent bar
    draw.rectangle([(0, 0), (W, 10)], fill=th["accent"])

    # Header row: category | brand | level
    draw.text((40, 35), f"📚 {topic['category'].upper()}",
              fill=(*th["subtext"], 220), font=get_font(FONT_BOLD_PATHS, 30), anchor="la")
    draw.text((W // 2, 38), "ai360trading.in",
              fill=(*th["subtext"], 160), font=get_font(FONT_REG_PATHS, 26), anchor="mm")
    draw.text((W - 40, 35), f"● {level}",
              fill=(*th["accent"], 200), font=get_font(FONT_BOLD_PATHS, 28), anchor="ra")

    # Slide counter
    draw.text((W // 2, 80), f"Slide {idx} of {total}",
              fill=(*th["subtext"], 180), font=get_font(FONT_REG_PATHS, 28), anchor="mm")

    # Slide title
    title_font  = get_font(FONT_BOLD_PATHS, 68)
    title_lines = textwrap.wrap(slide["title"].upper(), width=30)
    ty = 150
    for line in title_lines[:2]:
        draw.text((W // 2, ty), line, fill=th["text"], font=title_font, anchor="mm")
        ty += 84

    # Divider
    draw.rectangle([(80, ty + 15), (W - 80, ty + 19)], fill=th["accent"])
    ty += 55

    # Slide content — up to 7 lines
    content_font  = get_font(FONT_REG_PATHS, 40)
    content_lines = textwrap.wrap(slide["content"], width=58)
    for line in content_lines[:7]:
        draw.text((80, ty), line, fill=th["text"], font=content_font)
        ty += 54

    # Key takeaway box
    if slide.get("key_takeaway"):
        ty += 20
        box_top = ty
        box_bot = ty + 70
        draw.rectangle([(60, box_top), (W - 60, box_bot)], fill=(*th["accent"], 30))
        draw.rectangle([(60, box_top), (63, box_bot)], fill=th["accent"])
        draw.text((90, box_top + 35), f"💡 {slide['key_takeaway']}",
                  fill=th["accent"], font=get_font(FONT_BOLD_PATHS, 34), anchor="lm")

    # Telegram CTA — bottom left
    draw.text((40, H - 45), "📱 t.me/ai360trading",
              fill=(*th["subtext"], 180), font=get_font(FONT_REG_PATHS, 26), anchor="la")

    # Bottom accent bar
    draw.rectangle([(0, H - 10), (W, H)], fill=th["accent"])

    img.save(str(path), quality=95)

# ─── TTS VOICE ────────────────────────────────────────────────────────────────

async def gen_voice(text, path):
    # ✅ human_touch TTS speed variation — anti-AI-penalty
    tts_speed = ht.get_tts_speed()
    rate_pct  = int((tts_speed - 1.0) * 100)
    rate_str  = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
    await edge_tts.Communicate(text, VOICE, rate=rate_str).save(str(path))

# ─── DURATION CHECK ───────────────────────────────────────────────────────────

def check_duration(video_path):
    """Fail hard if video is under 8 minutes — mid-roll ads require 8+ min."""
    try:
        from moviepy.editor import VideoFileClip
        v   = VideoFileClip(str(video_path))
        dur = v.duration
        v.close()
        print(f"⏱️  Education video duration: {dur:.1f}s ({dur/60:.1f} min)")
        if dur < 480:
            print(f"❌ CRITICAL: {dur:.0f}s — under 8 minutes! Mid-roll ads will NOT activate.")
            print("❌ Fix: Ensure 22 slides, 80-100 words per slide, 1.2s pause per slide.")
            sys.exit(1)
        elif dur < 600:
            print(f"⚠️  WARNING: {dur/60:.1f} min — above 8min threshold but below 10min target.")
        else:
            print(f"✅ Duration OK — {dur/60:.1f} min — mid-roll ads WILL activate.")
    except SystemExit:
        raise
    except Exception as e:
        print(f"⚠️  Duration check error: {e}")

# ─── YOUTUBE ──────────────────────────────────────────────────────────────────

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
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
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
            "categoryId":  "27"  # Education category — better for finance monetisation
        },
        "status": {
            "privacyStatus":          "public",
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


def update_part1_description(youtube_service, part1_id, part2_url):
    """Add Part 2 link to Part 1 video description."""
    if not youtube_service or not part1_id or part1_id == "UPLOAD_FAILED":
        return
    try:
        resp = youtube_service.videos().list(part="snippet", id=part1_id).execute()
        if not resp.get("items"):
            return
        snippet = resp["items"][0]["snippet"]
        existing_desc = snippet.get("description", "")
        if part2_url not in existing_desc:
            snippet["description"] = existing_desc + f"\n\n▶️ Part 2 — Education Video: {part2_url}"
            youtube_service.videos().update(
                part="snippet",
                body={"id": part1_id, "snippet": snippet}
            ).execute()
            print(f"✅ Part 1 description updated with Part 2 link")
    except Exception as e:
        print(f"⚠️  Could not update Part 1 description: {e}")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

async def run():
    today = datetime.now().strftime("%Y%m%d")

    # 1. Read Part 1 video ID (saved by generate_analysis.py / upload_youtube.py)
    part1_id  = ""
    part1_url = ""
    id_path   = OUT / "analysis_video_id.txt"
    if id_path.exists():
        part1_id = id_path.read_text(encoding="utf-8").strip()
        if part1_id and part1_id != "UPLOAD_FAILED":
            part1_url = f"https://youtube.com/watch?v={part1_id}"
            print(f"🔗 Part 1 linked: {part1_url}")
        else:
            print("⚠️  Part 1 upload failed — continuing without link")
    else:
        print("⚠️  No analysis_video_id.txt — continuing without Part 1 link")

    # 2. Get today's topic from content calendar
    topic = get_todays_education_topic()
    print(f"📚 Topic: {topic['title']} | {topic['category']} | {topic['level']}")

    # 3. Generate 22-slide script via ai_client
    data   = generate_edu_slides(topic, part1_url)
    slides = data["slides"]
    print(f"📊 Total slides: {len(slides)} (minimum required: {MIN_SLIDES})")

    # ✅ Humanize title via human_touch
    vid_title = ht.humanize(data.get("video_title", f"{topic['title']} — ai360trading"), lang="hi")[:100]
    vid_desc  = data.get("video_description", f"Learn {topic['title']} with ai360trading.in")

    # ✅ SEO tags from human_touch — India + Global combined
    seo_tags   = seo.get_video_tags(mode=CONTENT_MODE)
    extra_tags = [
        topic["title"], topic["category"], "Trading Education", "ai360trading",
        "Stock Market India", "Learn Trading", "NSE", "BSE", "Hinglish", topic["level"]
    ]
    all_tags = list(dict.fromkeys(seo_tags + extra_tags))

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

    # 4. Build slides + voice clips
    print(f"\n🎬 Building {len(slides)} slides...")
    clips = []
    for i, s in enumerate(slides):
        img_path   = OUT / f"edu_{i}.png"
        audio_path = OUT / f"edu_{i}.mp3"

        make_edu_slide(s, i + 1, len(slides), topic, img_path)
        await gen_voice(s["content"], audio_path)

        voice_clip = AudioFileClip(str(audio_path))
        # ✅ 1.2s pause — was 0.8s, gives viewers time to absorb each slide
        duration   = voice_clip.duration + 1.2

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
                print(f"⚠️  Music error slide {i}: {e}")
                slide_audio = voice_clip
        else:
            slide_audio = voice_clip

        clip = ImageClip(str(img_path)).set_duration(duration).set_audio(slide_audio)
        clips.append(clip)
        print(f"  Slide {i+1}/{len(slides)} — {voice_clip.duration:.1f}s voice + 1.2s pause = {duration:.1f}s total")

    # 5. Render video
    video_path = OUT / "education_video.mp4"
    print(f"\n🎥 Rendering education video ({len(slides)} slides)...")
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

    # 6. ✅ Duration check — fail workflow if under 8 minutes
    check_duration(video_path)

    # 7. Upload to YouTube
    youtube_service = get_youtube_service()
    part2_id        = upload_to_youtube(video_path, vid_title, full_desc, all_tags)

    # 8. Save IDs and cross-link Part 1 ↔ Part 2
    if part2_id:
        (OUT / "education_video_id.txt").write_text(part2_id, encoding="utf-8")
        part2_url = f"https://youtube.com/watch?v={part2_id}"
        print(f"✅ Education video ID saved: {part2_id}")

        if part1_id and part1_id != "UPLOAD_FAILED":
            update_part1_description(youtube_service, part1_id, part2_url)

        meta = {
            "title":        vid_title,
            "description":  full_desc,
            "video_id":     part2_id,
            "video_url":    part2_url,
            "part1_url":    part1_url,
            "topic":        topic["title"],
            "category":     topic["category"],
            "level":        topic["level"],
            "slide_count":  len(slides),
            "content_mode": CONTENT_MODE,
            "date":         today,
        }
        (OUT / f"education_meta_{today}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"✅ Education meta saved: education_meta_{today}.json")
    else:
        print("⚠️  Upload failed — saving placeholder")
        (OUT / "education_video_id.txt").write_text("UPLOAD_FAILED", encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(run())
