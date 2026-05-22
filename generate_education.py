"""
generate_education.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v1.1 FIXES (May 2026):

FIX 1 — CONTENT_MODE empty bug
  Problem: [EDUCATION] mode= lang=HI — mode was empty string
  Fix: auto-detect from weekday if CONTENT_MODE env var is empty

FIX 2 — Stray percentage in title ("Week 1: Stock Market Kya Hai? 5%")
  Fix: clean_edu_title() strips all digit+% patterns from title

FIX 3 — Video too short (3.3 min instead of 10+ min)
  Fix: expand_slide_content() ensures every slide >= 80 words
       22 slides x ~100 words x ~0.5s/word = ~11 min video

FIX 4 — LANG from EDUCATION_LANG env var (was hardcoded hi)
  Fix: LANG = os.environ.get("EDUCATION_LANG", "hi").lower()
       VOICE auto-selected by LANG
       YouTube credentials auto-selected by LANG

FIX 5 — Week number from content_calendar v2.1
  Fix: get_todays_education_topic() now returns week number
       Title: "Stock Market Kya Hai | Week 1 | AI360 Trading"
       Week auto-advances every Monday from COURSE_START = May 15 2026

Target duration: 10-12 min (above 8-min mid-roll ad threshold)
Slide count: 22 slides minimum @ 100+ words each
"""

import os
import re
import sys
import json
import asyncio
import textwrap
from datetime import datetime
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ImageClip, AudioFileClip,
    concatenate_videoclips,
)

from ai_client import ai
from human_touch import ht, seo
from content_calendar import get_todays_education_topic

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── CONFIG ───────────────────────────────────────────────────────────────────

# v1.1 FIX 1: Auto-detect CONTENT_MODE when empty string
_raw_mode = os.environ.get("CONTENT_MODE", "").lower().strip()
if not _raw_mode:
    _day = datetime.now().weekday()  # 0=Mon, 6=Sun
    CONTENT_MODE = "weekend" if _day >= 5 else "market"
    print(f"[EDUCATION] CONTENT_MODE was empty — auto-detected: {CONTENT_MODE}")
else:
    CONTENT_MODE = _raw_mode

HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "")

# v1.2: Single bilingual (Hinglish) video — works for Hindi + English audience
# No separate Hindi/English runs needed. Saves GitHub Actions minutes.
# Hinglish = English concepts + Hindi explanation = understood by both audiences.
LANG  = "bi"                   # bilingual Hinglish — replaces per-language runs
VOICE = "hi-IN-SwaraNeural"    # natural for Hinglish TTS

OUT = Path("output")
W, H = 1920, 1080
FPS  = 24

MIN_SLIDES      = 22
MIN_WORDS_SLIDE = 80   # enforce minimum words per slide for duration

os.makedirs(OUT, exist_ok=True)
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

print(f"[EDUCATION] mode={CONTENT_MODE.upper()} lang=BILINGUAL (Hinglish — Hindi+English)")

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
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

# ─── THEMES ───────────────────────────────────────────────────────────────────

LEVEL_THEMES = {
    "Beginner":     {"bg_top":(10,20,50),  "bg_bot":(20,40,90),  "accent":(80,180,255),  "text":(240,250,255),"subtext":(160,200,230)},
    "Intermediate": {"bg_top":(20,15,45),  "bg_bot":(40,30,80),  "accent":(180,120,255), "text":(245,240,255),"subtext":(190,160,230)},
    "Advanced":     {"bg_top":(15,30,20),  "bg_bot":(30,60,40),  "accent":(80,220,140),  "text":(240,255,245),"subtext":(160,220,180)},
    "All Levels":   {"bg_top":(30,20,15),  "bg_bot":(60,40,25),  "accent":(255,180,60),  "text":(255,248,235),"subtext":(220,190,140)},
}
DEFAULT_THEME = LEVEL_THEMES["Beginner"]

def lerp(c1, c2, t):
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

# ─── TITLE CLEANER — v1.1 FIX 2 ──────────────────────────────────────────────

def clean_edu_title(title: str, week: int, topic_name: str, lang: str = "hi") -> str:
    """
    Remove AI-generated stray percentages from title.
    Enforce format: "Topic | Week N | AI360 Trading"
    """
    # Remove stray percentages like "5%", "10%?", "50%", "-5%"
    cleaned = re.sub(r'-?\d+(\.\d+)?%\??!?', '', title)
    # Remove multiple spaces and artifacts
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().strip('?! ')
    # Remove bad trailing chars before pipe
    cleaned = re.sub(r'[?!]+\s*\|', ' |', cleaned)

    channel = "AI360 Trading"

    # If cleaned title is too short or broken — use safe format
    if len(cleaned) < 15:
        cleaned = f"{topic_name} | Week {week} | {channel}"

    # Ensure Week N appears in title
    if f"Week {week}" not in cleaned:
        parts = cleaned.split("|")
        if len(parts) >= 2:
            cleaned = f"{parts[0].strip()} | Week {week} | {channel}"
        else:
            cleaned = f"{cleaned} | Week {week} | {channel}"

    return cleaned[:100]

# ─── SLIDE CONTENT EXPANDER — v1.1 FIX 3 ─────────────────────────────────────

EXTRA_CONTENT_HI = [
    (
        " Yeh concept Indian stock market mein bahut important role play karta hai. "
        "NSE aur BSE dono exchanges par yeh principle equally apply hota hai. "
        "Agar aap isko practically apply karna chahte hain toh pehle paper trading se shuru karo. "
        "Apne trades ko track karo, journal banao, aur har trade se kuch na kuch seekho. "
        "Discipline aur patience do cheezein hain jo successful traders ko average se alag karti hain."
    ),
    (
        " Is concept ko global markets mein bhi dekha gaya hai — USA aur UK ke traders bhi yehi follow karte hain. "
        "Indian market ki apni characteristics hain — FII activity, sector rotation, aur Nifty ka 20DMA "
        "yeh sab factors aapko samajhne chahiye taaki aap better decisions le sako. "
        "Regular study aur consistent practice se yeh skill naturally develop hoti hai."
    ),
]

EXTRA_CONTENT_EN = [
    (
        " This concept plays an important role in the Indian stock market and applies to both NSE and BSE. "
        "If you want to apply this practically, start with paper trading first. "
        "Track all your trades in a journal and learn something from every single trade you make. "
        "Discipline and patience are the two qualities that separate successful traders from average ones."
    ),
    (
        " This concept also applies in global markets — traders in the USA and UK follow the same principles. "
        "The Indian market has unique characteristics — FII activity, sector rotation, and the Nifty 20DMA "
        "are all factors you need to understand to make better decisions. "
        "Regular study and consistent practice will help these skills develop naturally."
    ),
]

def expand_slide_content(content: str, heading: str, topic_name: str, lang: str) -> str:
    """Ensure slide content is at least MIN_WORDS_SLIDE words."""
    words = len(content.split())
    if words >= MIN_WORDS_SLIDE:
        return content
    extras = EXTRA_CONTENT_EN if lang == "en" else EXTRA_CONTENT_HI
    for ext in extras:
        content = content + ext
        if len(content.split()) >= MIN_WORDS_SLIDE:
            break
    return content.strip()

# ─── EXPANSION SLIDE HEADINGS ─────────────────────────────────────────────────

EXPANSION_SLIDES_HI = [
    "Common Galtiyan Jo Traders Karte Hain",
    "Risk Management — Kyun Zaroori Hai",
    "Real Indian Stock Example",
    "Step-by-Step Guide — Part 1",
    "Step-by-Step Guide — Part 2",
    "Global Market Context — USA UK India",
    "Advanced Tip For Experienced Traders",
    "Summary of Key Points",
    "Action Plan — Aaj Se Shuru Karo",
    "Quick Quiz For Viewers",
    "Outro — Subscribe Aur Telegram Join Karo",
]

EXPANSION_SLIDES_EN = [
    "Common Mistakes Traders Make",
    "Risk Management — Why It Matters",
    "Real Indian Stock Market Example",
    "Step-by-Step Guide Part 1",
    "Step-by-Step Guide Part 2",
    "Global Market Context USA UK India",
    "Advanced Tip For Experienced Traders",
    "Summary of Key Points",
    "Action Plan — Start Today",
    "Quick Quiz For Viewers",
    "Outro — Subscribe and Join Telegram",
]

# Bilingual slides — English headings (readable by all), Hinglish explanation
EXPANSION_SLIDES_BI = [
    "Common Mistakes Traders Make — Aur Kaise Bachein",
    "Risk Management — Why It Is The Most Important",
    "Real Indian Stock Example — Reliance, TCS, HDFC",
    "Step-by-Step Guide — Part 1",
    "Step-by-Step Guide — Part 2",
    "Global Market Context — India, USA, UK",
    "Advanced Tip — For Serious Investors",
    "Key Points Summary — Quick Revision",
    "Action Plan — Start Karo Aaj Se",
    "Quick Quiz — Test Your Knowledge",
    "Subscribe Karo — Weekly Free Education",
]

# ─── SCRIPT GENERATION ────────────────────────────────────────────────────────

def generate_edu_slides(topic, week):
    today = datetime.now().strftime("%A, %d %B %Y")

    topic_slides   = topic.get("slides", [])
    slide_headings = [s.get("heading", f"Topic {i+1}") for i, s in enumerate(topic_slides)]
    if   LANG == "en": expansion = EXPANSION_SLIDES_EN
    elif LANG == "hi": expansion = EXPANSION_SLIDES_HI
    else:              expansion = EXPANSION_SLIDES_BI   # "bi" bilingual
    while len(slide_headings) < MIN_SLIDES:
        idx = len(slide_headings) - len(topic_slides)
        slide_headings.append(expansion[idx % len(expansion)])

    # v1.2: Always bilingual hook (Hinglish — works for Hindi + English audience)
    hook = ht.get_hook(mode="education", lang="hi", week=week)

    if LANG == "bi":
        lang_rules = (
            "Write in Hinglish — natural mix of Hindi + English so BOTH Hindi speakers AND NRI/English viewers understand. "
            "Use English words for key concepts (market, stock, investment, returns, portfolio, compound interest). "
            "Use Hindi for warm explanation: 'samjhate hain', 'yeh important hai kyunki', 'sochte hain ek example'. "
            "Slide TEXT must be English-dominant so any audience can READ it — voice explains in Hinglish. "
            "Pattern for each slide: Start with English concept → explain in Hinglish → give Indian example (Reliance, TCS, HDFC). "
            "NEVER use: 'aaj ka market', 'chart pattern', 'breakout signal', 'trade setup'. "
            "DO use: 'yeh concept', 'for example', 'iska matlab hai', 'think of it this way'."
        )
        cta = (
            "Subscribe karo aur bell icon dabao — har week free education video! "
            "Telegram join karo t.me/ai360trading for daily signals. "
            "Like karo agar helpful laga — share karo apne friends aur family ke saath!"
        )
        title_format = f"{topic['title']} | Week {week} | AI360 Trading"
    elif LANG == "hi":
        lang_rules = (
            "Write in natural Hinglish — Hindi + English mix like a teacher explaining to a student. "
            "NEVER use: 'aaj ka market', 'chart pattern', 'breakout signal', 'trade setup'. "
            "DO use: 'yeh concept', 'samjhate hain', 'example ke taur pe', 'sochte hain'."
        )
        cta = (
            "Subscribe karo aur bell icon dabao — har week nayi education video! "
            "Telegram join karo t.me/ai360trading free daily signals ke liye. "
            "Like karo agar helpful laga aur apne trader dost ko share karo!"
        )
        title_format = f"{topic['title']} | Week {week} | AI360 Trading"
    else:
        lang_rules = (
            "Write in clear simple English like a friendly teacher. "
            "NEVER use: 'today's market', 'chart pattern', 'breakout signal', 'trade setup'. "
            "DO use: 'this concept', 'let me explain', 'for example', 'think of it this way'."
        )
        cta = (
            "Subscribe and hit the bell — a new lesson every week! "
            "Join our Telegram at t.me/ai360trading for free daily signals. "
            "Like this video and share it with someone who needs this!"
        )
        title_format = f"{topic.get('title_en', topic['title'])} | Week {week} | AI360 Trading"

    # Fallback content for padding
    fallback_content = (
        "Yeh concept trading mein bahut useful hai. "
        "Agar aap isko consistently apply karo toh results zaroor aayenge. "
        "Practice aur patience se sab possible hai. "
        "Agli slide mein aur detail mein dekhenge."
    ) if LANG == "hi" else (
        "This concept is very useful in trading. "
        "If you apply it consistently, results will follow. "
        "Practice and patience make everything possible. "
        "Let us look at more detail in the next slide."
    )

    prompt = f"""You are a friendly financial educator teaching a free 52-week investing course on YouTube.
Today: {today}
Course Week: {week}
Topic: {topic['title']}
Category: {topic['category']}
Level: {topic['level']}
Language rules: {lang_rules}

Opening hook for slide 1: "{hook}"

Generate EXACTLY {MIN_SLIDES} slides using these headings IN ORDER:
{json.dumps(slide_headings, ensure_ascii=False)}

CRITICAL RULES:
1. Each slide content = MINIMUM 100 words. Count every word. Short slides = rejected.
2. video_title must be EXACTLY: "{title_format}" — no changes, no percentages
3. Last slide = CTA: "{cta}"
4. NO trading signal language — pure education only
5. Include at least one real Indian company example (Reliance, TCS, HDFC, Infosys)
6. Slide 17 must reference USA/UK global investing context

Return ONLY valid JSON, no markdown:
{{
  "video_title": "{title_format}",
  "video_description": "3-4 sentences about what viewers will learn",
  "slides": [
    {{
      "title": "slide heading max 8 words",
      "content": "spoken content minimum 100 words",
      "key_takeaway": "one line max 12 words"
    }}
  ]
}}"""

    print(f"🤖 Generating {LANG.upper()} education script — Week {week}: {topic['title']}...")
    data = ai.generate_json(prompt, content_mode="education", lang=LANG)

    if data and data.get("slides") and len(data["slides"]) >= 10:
        slides = data["slides"]

        # Pad to MIN_SLIDES
        while len(slides) < MIN_SLIDES:
            idx     = len(slides)
            heading = slide_headings[idx] if idx < len(slide_headings) else "Key Lesson"
            slides.append({
                "title": heading,
                "content": expand_slide_content(fallback_content, heading, topic["title"], LANG),
                "key_takeaway": "Seekhte raho, consistent raho" if LANG == "hi" else "Keep learning, stay consistent"
            })

        data["slides"] = slides[:MIN_SLIDES]

        # FIX 3: Expand any slide under MIN_WORDS
        expanded_count = 0
        for i, slide in enumerate(data["slides"]):
            orig_words = len(slide["content"].split())
            data["slides"][i]["content"] = expand_slide_content(
                slide["content"], slide["title"], topic["title"], LANG
            )
            new_words = len(data["slides"][i]["content"].split())
            if new_words > orig_words:
                expanded_count += 1

        total_words = sum(len(s["content"].split()) for s in data["slides"])
        if expanded_count > 0:
            print(f"  [EXPAND] {expanded_count} slides expanded")
        print(f"  Total: {total_words} words across {len(data['slides'])} slides (~{total_words//130:.0f}-{total_words//80:.0f} min)")
        return data

    else:
        print("⚠️ AI returned insufficient slides — using fallback")
        fallback_slides = []
        for i, heading in enumerate(slide_headings):
            content = ""
            if i < len(topic_slides):
                pts = topic_slides[i].get("points", [])
                content = " ".join(pts)
            content = expand_slide_content(content, heading, topic["title"], LANG)
            fallback_slides.append({
                "title": heading,
                "content": content,
                "key_takeaway": f"{heading} — remember this"
            })
        return {
            "video_title": title_format,
            "video_description": f"Week {week}: {topic['title']} — complete investing education.",
            "slides": fallback_slides
        }

# ─── SLIDE RENDERER ───────────────────────────────────────────────────────────

def make_edu_slide(slide, idx, total, topic, path):
    level = topic.get("level", "Beginner")
    th    = LEVEL_THEMES.get(level, DEFAULT_THEME)

    img = Image.new("RGB", (W, H))
    px  = img.load()
    for y in range(H):
        c = lerp(th["bg_top"], th["bg_bot"], y / H)
        for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0,0),(W,10)], fill=th["accent"])

    # Header
    draw.text((40,35), f"📚 {topic['category'].upper()}", fill=(*th["subtext"],220),
              font=get_font(FONT_BOLD_PATHS,30), anchor="la")
    draw.text((W//2,38), "ai360trading.in", fill=(*th["subtext"],160),
              font=get_font(FONT_REG_PATHS,26), anchor="mm")
    draw.text((W-40,35), f"● {level}", fill=(*th["accent"],200),
              font=get_font(FONT_BOLD_PATHS,28), anchor="ra")

    draw.text((W//2,80), f"Slide {idx} of {total}", fill=(*th["subtext"],180),
              font=get_font(FONT_REG_PATHS,28), anchor="mm")

    # Title
    title_font  = get_font(FONT_BOLD_PATHS,68)
    title_lines = textwrap.wrap(slide["title"].upper(), width=30)
    ty = 150
    for line in title_lines[:2]:
        draw.text((W//2,ty), line, fill=th["text"], font=title_font, anchor="mm")
        ty += 84

    draw.rectangle([(80,ty+15),(W-80,ty+19)], fill=th["accent"])
    ty += 55

    # Content
    content_font  = get_font(FONT_REG_PATHS,40)
    content_lines = textwrap.wrap(slide["content"], width=58)
    for line in content_lines[:7]:
        draw.text((80,ty), line, fill=th["text"], font=content_font)
        ty += 54

    # Takeaway
    if slide.get("key_takeaway"):
        ty += 20
        box_top = min(ty, H-100)
        box_bot = box_top + 70
        draw.rectangle([(60,box_top),(W-60,box_bot)], fill=(*th["accent"],30))
        draw.rectangle([(60,box_top),(63,box_bot)], fill=th["accent"])
        draw.text((90,box_top+35), f"💡 {slide['key_takeaway']}",
                  fill=th["accent"], font=get_font(FONT_BOLD_PATHS,34), anchor="lm")

    draw.text((40,H-45), "📱 t.me/ai360trading", fill=(*th["subtext"],180),
              font=get_font(FONT_REG_PATHS,26), anchor="la")
    draw.rectangle([(0,H-10),(W,H)], fill=th["accent"])
    img.save(str(path), quality=95)

# ─── TTS ──────────────────────────────────────────────────────────────────────

async def gen_voice(text, path):
    tts_speed = ht.get_tts_speed()
    rate_pct  = int((tts_speed - 1.0) * 100)
    rate_str  = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
    await edge_tts.Communicate(text, VOICE, rate=rate_str).save(str(path))

# ─── DURATION CHECK ───────────────────────────────────────────────────────────

def check_duration(video_path):
    try:
        from moviepy.editor import VideoFileClip
        v = VideoFileClip(str(video_path)); dur = v.duration; v.close()
        print(f"⏱️  Duration: {dur:.1f}s ({dur/60:.1f} min)")
        if dur < 480:
            print(f"⚠️  Under 8 min — mid-roll ads won't activate. Check word counts.")
        elif dur < 600:
            print(f"⚠️  {dur/60:.1f} min — above threshold but below 10 min target")
        else:
            print(f"✅ {dur/60:.1f} min — mid-roll ads WILL activate")
    except Exception as e:
        print(f"⚠️  Duration check: {e}")

# ─── YOUTUBE ──────────────────────────────────────────────────────────────────

def get_youtube_service():
    # v1.2: Always upload to main channel — single bilingual video
    creds_key = "YOUTUBE_CREDENTIALS"
    try:
        creds_json = os.environ.get(creds_key)
        if not creds_json and os.path.exists("token.json"):
            with open("token.json") as f: creds_json = f.read()
        if not creds_json:
            print(f"❌ YouTube service unavailable [{LANG}] — skipping")
            return None
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"❌ YouTube auth [{LANG}]: {e}")
        return None


def upload_to_youtube(video_path, title, description, tags):
    youtube = get_youtube_service()
    if not youtube: return None
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
    print(f"🚀 Uploading [BILINGUAL]: {title[:60]}...")
    try:
        req  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        resp = None
        while resp is None:
            status, resp = req.next_chunk()
            if status: print(f"  {int(status.progress()*100)}%")
        vid_id = resp["id"]
        print(f"✅ Uploaded [{LANG.upper()}]: https://youtube.com/watch?v={vid_id}")
        return vid_id
    except Exception as e:
        print(f"❌ Upload [{LANG}]: {e}")
        return None

# ─── MAIN ─────────────────────────────────────────────────────────────────────

async def run():
    today    = datetime.now().strftime("%Y%m%d")
    today_hr = datetime.now().strftime("%d %b %Y")

    # Get this week's topic + week number from content_calendar v2.1
    topic = get_todays_education_topic()
    week  = topic.get("week", 1)

    print(f"📖 Course Week {week}: {topic['title']} — {topic.get('description','')}")

    # Generate slides
    data   = generate_edu_slides(topic, week)
    slides = data["slides"]

    # FIX 2: Clean title
    raw_title = data.get("video_title", f"{topic['title']} | Week {week} | AI360 Trading")
    vid_title = clean_edu_title(raw_title, week, topic["title"], LANG)
    print(f"✅ Script ready: {vid_title}")
    print(f"📋 Title: {vid_title}")

    # SEO tags and description
    tags         = seo.get_video_tags(mode="education", is_short=False)
    youtube_tags = seo.get_youtube_safe_tags(tags)
    desc         = ht.get_video_description(
        mode="education", lang=LANG, week=week, topic=topic["title"]
    )
    hashtag_str = " ".join(f"#{t}" for t in youtube_tags[:12])
    full_desc   = f"{desc}\n\n{hashtag_str}"

    # Render all slides + audio
    clips = []
    for i, slide in enumerate(slides, start=1):
        slide_path = OUT / f"edu_slide_{LANG}_{today}_{i:02d}.png"
        audio_path = OUT / f"edu_audio_{LANG}_{today}_{i:02d}.mp3"

        make_edu_slide(slide, i, len(slides), topic, slide_path)
        await gen_voice(slide["content"], audio_path)

        try:
            audio_clip = AudioFileClip(str(audio_path))
            dur        = audio_clip.duration + 1.2  # 1.2s reading pause
            img_clip   = ImageClip(str(slide_path)).set_duration(dur).set_audio(audio_clip)
            clips.append(img_clip)
        except Exception as e:
            print(f"⚠️  Slide {i} clip error: {e}")

    if not clips:
        print("❌ No clips rendered — aborting")
        return

    # Combine and export
    video_path = OUT / f"education_video_bi.mp4"
    final      = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        str(video_path), fps=FPS, codec="libx264", audio_codec="aac",
        remove_temp=True, logger=None
    )

    dur_min = final.duration / 60
    print(f"✅ Video rendered [BILINGUAL]: {video_path.name} | {dur_min:.1f} min")
    check_duration(video_path)

    # Upload
    vid_id = upload_to_youtube(video_path, vid_title, full_desc, youtube_tags)

    # Save meta
    meta = {
        "title":        vid_title,
        "description":  full_desc,
        "tags":         tags,
        "week":         week,
        "topic":        topic["title"],
        "lang":         LANG,
        "duration_min": round(dur_min, 1),
        "youtube_video_id": vid_id or "",
        "youtube_url":  f"https://youtube.com/watch?v={vid_id}" if vid_id else "",
    }
    meta_path = OUT / f"education_meta_{today}_bi.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 Saved meta: {meta_path.name}")

    print(f"\n{'='*60}")
    print(f"✅ EDUCATION DONE — Week {week} | {LANG.upper()} | {today_hr}")
    print(f"   Topic    : {topic['title']}")
    print(f"   Duration : {dur_min:.1f} min")
    print(f"   Video ID : {vid_id or 'FAILED'}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(run())
