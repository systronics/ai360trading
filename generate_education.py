"""
generate_education.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Replaces generate_analysis.py.
Produces ONE education video per day in BOTH Hindi and English.
- Hindi  : hi-IN-SwaraNeural  → YouTube Hindi channel
- English: en-US-JennyNeural  → YouTube English channel (Phase 3)

Course calendar: 52 weeks, Week 1 = Stock market basics.
Week is auto-calculated from a fixed START_DATE so the course
never repeats and always progresses forward.

Weekend mode  : Fundamental / base-prepared stock deep-dive.
Holiday mode  : Motivational investing lesson.

Upload: writes output/education_video_hi.mp4
               output/education_video_en.mp4
               output/education_meta_YYYYMMDD.json
"""

import os
import json
import asyncio
import textwrap
from datetime import datetime, date
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from human_touch import ht, seo
from ai_client import ai

# ─── CONFIG ───────────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")
LANG         = os.environ.get("EDUCATION_LANG", "hi")   # "hi" or "en"

print(f"[EDUCATION] mode={CONTENT_MODE.upper()} lang={LANG.upper()}")

OUT   = Path("output")
W, H  = 1920, 1080
FPS   = 24
NUM_SLIDES = 14   # 14 × ~40 sec ≈ 9–10 min (mid-roll eligible)

VOICE_HI = "hi-IN-SwaraNeural"
VOICE_EN = "en-US-JennyNeural"
VOICE    = VOICE_HI if LANG == "hi" else VOICE_EN

os.makedirs(OUT, exist_ok=True)

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

# ─── COURSE CALENDAR — 52 weeks, auto-advances ───────────────────────────────
# Fixed start date — Week 1 began here. Never change this.
COURSE_START = date(2026, 5, 15)

COURSE = [
    # Week : Topic : Subtitle
    ( 1, "Stock Market Kya Hai?",             "Basics: Shares, NSE, BSE explained simply"),
    ( 2, "Demat Account Kaise Kholein?",       "Step-by-step account opening guide"),
    ( 3, "Bull Market vs Bear Market",         "Market moods and how to trade them"),
    ( 4, "Index Kya Hota Hai?",               "Nifty50, Sensex, Bank Nifty decoded"),
    ( 5, "Candlestick Charts Basics",          "Reading price candles for beginners"),
    ( 6, "Support aur Resistance",             "The most important concept in trading"),
    ( 7, "Breakout Trading Strategy",          "How to catch stocks at the right moment"),
    ( 8, "Volume Ka Raaz",                     "Why volume confirms everything"),
    ( 9, "Moving Averages — 20DMA, 50DMA",     "Trend confirmation the simple way"),
    (10, "RSI — Relative Strength Index",      "Is a stock overbought or oversold?"),
    (11, "MACD — Momentum Indicator",          "When two moving averages talk"),
    (12, "FII vs DII — Smart Money",           "Follow the big players, not news"),
    (13, "Swing Trading Complete System",      "Entry, SL, Target — step by step"),
    (14, "Positional Trading vs Intraday",     "Which is better for you?"),
    (15, "Risk Management — Trade Size",       "How much to risk per trade"),
    (16, "Stop Loss — Types and Usage",        "Protect capital before profit"),
    (17, "Trailing Stop Loss Strategy",        "Lock profits while the trend runs"),
    (18, "Sector Rotation — FII Style",        "Which sector is smart money entering?"),
    (19, "Options Basics — CE and PE",         "What is a call option, simply"),
    (20, "Options Buying vs Selling",          "Risk profile of each side"),
    (21, "VIX — Fear Index",                   "How market fear affects options"),
    (22, "Expiry Strategy — Monthly vs Weekly","Theta decay explained simply"),
    (23, "ATR — Average True Range",           "Measure volatility, set better SL"),
    (24, "VCP — Volatility Contraction",       "Mark Minervini's setup explained"),
    (25, "Base Building — Stage Analysis",     "Enter before breakout, not after"),
    (26, "52-Week High Breakout Strategy",     "Simple, powerful, works globally"),
    (27, "Cup and Handle Pattern",             "Most reliable chart pattern"),
    (28, "Double Bottom — Reversal Setup",     "Catching bottoms safely"),
    (29, "Gap Up / Gap Down Strategy",         "How to trade morning gaps"),
    (30, "Earnings Season — Trade or Avoid?",  "Result day risk management"),
    (31, "Global Markets Effect on India",     "USA, UK, Japan — what to watch"),
    (32, "Dollar Index and Indian Market",     "DXY and Nifty relationship"),
    (33, "Gold vs Stock Market",               "Safe haven vs growth assets"),
    (34, "Mutual Funds vs Direct Stocks",      "Which is right for you?"),
    (35, "SIP vs Lump Sum Investment",         "Time in market vs timing market"),
    (36, "Annual Report Reading Basics",       "Key numbers every investor needs"),
    (37, "PE Ratio — Value Investing Intro",   "Is a stock cheap or expensive?"),
    (38, "ROE and ROCE Explained",             "Quality of business metrics"),
    (39, "Debt-to-Equity Ratio",               "How much debt is too much?"),
    (40, "Promoter Holding — What It Means",   "Skin in the game matters"),
    (41, "IPO — How to Apply and Analyse",     "Grey market, allotment, listing"),
    (42, "Bonus, Split, Buyback Explained",    "Corporate actions decoded"),
    (43, "Dividend Investing Strategy",        "Build passive income from stocks"),
    (44, "Portfolio Diversification",          "How many stocks is enough?"),
    (45, "Taxes on Stock Trading",             "STCG, LTCG, ITR basics"),
    (46, "Trading Psychology — Part 1",        "Why smart people lose money"),
    (47, "Trading Psychology — Part 2",        "Fear and greed control"),
    (48, "Trading Journal — Why and How",      "The habit that changes results"),
    (49, "Building a Watchlist System",        "Like our Nifty200 — step by step"),
    (50, "Complete Swing Trade Plan",          "From scan to exit — full system"),
    (51, "Common Beginner Mistakes",           "Learn from others' losses"),
    (52, "Your 1-Year Trading Roadmap",        "What to do next — full plan"),
]

def get_course_week() -> tuple:
    """Auto-calculate current week number from course start date."""
    today     = date.today()
    delta     = (today - COURSE_START).days
    week_num  = (delta // 7) % 52   # loops after 52 weeks
    return COURSE[week_num]


# ─── FONTS ────────────────────────────────────────────────────────────────────
FONT_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
]
FONT_REG_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()


# ─── THEME ────────────────────────────────────────────────────────────────────
# Education uses a consistent deep-blue professional theme
THEME = {
    "bg_top"  : (8, 15, 40),
    "bg_bot"  : (15, 35, 80),
    "accent"  : (0, 200, 255),
    "text"    : (240, 250, 255),
    "subtext" : (160, 200, 230),
    "gold"    : (255, 210, 0),
    "green"   : (0, 220, 110),
}

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ─── SCRIPT GENERATION ────────────────────────────────────────────────────────
def generate_script(week_num: int, topic: str, subtitle: str) -> dict:
    today   = datetime.now().strftime("%A, %d %B %Y")
    hook    = ht.get_hook(mode=CONTENT_MODE, lang=LANG)
    cta     = ht.get_cta(lang=LANG)

    if LANG == "hi":
        language_instruction = (
            "Write in Hinglish (Hindi + English mix). "
            "Simple language, like explaining to a friend. "
            "Use Hindi script where natural, English for technical terms."
        )
        channel_tag = "ai360trading"
    else:
        language_instruction = (
            "Write in clear simple English. "
            "Explain as if teaching a complete beginner from India or globally. "
            "Avoid jargon — define every term when first used."
        )
        channel_tag = "AI360 Trading"

    if CONTENT_MODE == "weekend":
        context = f"Weekend deep-dive on: {topic} — {subtitle}. Focus on fundamentals."
    elif CONTENT_MODE == "holiday":
        holiday = HOLIDAY_NAME or "Market Holiday"
        context = f"{holiday} special lesson on: {topic}. Keep it festive but educational."
    else:
        context = f"Today's course lesson: Week {week_num} — {topic} — {subtitle}."

    prompt = f"""You are an expert Indian stock market educator creating a YouTube education video for {channel_tag}.

Today: {today}
Course: Week {week_num} of 52 — {topic}
Subtitle: {subtitle}
Context: {context}
Language: {language_instruction}

Start slide 1 with this hook: "{hook}"
End last slide with this CTA: "{cta}"
Slide 7 must include: "Comment mein batao — kya yeh concept clear hua? 👇"

TITLE RULES:
- Put the topic name + week number FIRST
- Include a curiosity question or number
- End with "| AI360 Trading"
- Max 95 characters

Generate exactly {NUM_SLIDES} slides as valid JSON:
{{
  "video_title": "Week {week_num}: {topic} — clear example title | AI360 Trading",
  "video_description": "3-4 sentence description with key learning points. Include ai360trading.in",
  "week_number": {week_num},
  "topic": "{topic}",
  "key_takeaway": "One sentence — the single most important thing to remember",
  "slides": [
    {{
      "title": "slide heading max 6 words",
      "content": "spoken content 80-100 words. Teach one clear concept per slide. Use real examples.",
      "key_points": ["point 1", "point 2", "point 3"],
      "slide_type": "intro|concept|example|practice|summary|cta"
    }}
  ]
}}"""

    print(f"🤖 Generating {LANG.upper()} education script — Week {week_num}: {topic}")
    try:
        data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang=LANG)
        for slide in data.get("slides", []):
            if slide.get("content"):
                slide["content"] = ht.humanize(slide["content"], lang=LANG)
        print(f"✅ Script ready: {data.get('video_title','')[:70]}")
        return data
    except Exception as e:
        print(f"⚠️ Script error: {e}")
        return _fallback_script(week_num, topic, subtitle)


def _fallback_script(week_num, topic, subtitle):
    today_str = datetime.now().strftime("%d %b %Y")
    return {
        "video_title": f"Week {week_num}: {topic} | AI360 Trading",
        "video_description": f"Learn {topic} with AI360 Trading. Visit ai360trading.in",
        "week_number": week_num,
        "topic": topic,
        "key_takeaway": subtitle,
        "slides": [{
            "title": f"Week {week_num}: {topic}",
            "content": f"Namaskar! Aaj hum seekhenge {topic} ke baare mein. {subtitle}. Subscribe karo daily lessons ke liye!",
            "key_points": ["Subscribe karo", "Like karo", "ai360trading.in"],
            "slide_type": "intro"
        }] * NUM_SLIDES
    }


# ─── SLIDE RENDERER ───────────────────────────────────────────────────────────
def make_slide(slide: dict, idx: int, total: int, week_num: int,
               topic: str, path: Path, is_first: bool = False):
    th  = THEME
    img = Image.new("RGB", (W, H))
    px  = img.load()

    # Gradient background
    for y in range(H):
        c = lerp(th["bg_top"], th["bg_bot"], y / H)
        for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")

    # Top accent bar
    draw.rectangle([(0, 0), (W, 8)], fill=th["accent"])

    # Week badge top-left
    draw.text((40, 30), f"Week {week_num} of 52",
              fill=(*th["gold"], 220), font=get_font(FONT_BOLD_PATHS, 30), anchor="la")

    # Channel watermark top-right
    draw.text((W - 40, 30), "ai360trading.in",
              fill=(*th["subtext"], 180), font=get_font(FONT_REG_PATHS, 28), anchor="ra")

    # Slide counter
    draw.text((W - 40, 65), f"{idx}/{total}",
              fill=(*th["subtext"], 150), font=get_font(FONT_REG_PATHS, 24), anchor="ra")

    if is_first:
        # Hero slide — large topic title
        t1 = get_font(FONT_BOLD_PATHS, 100)
        t2 = get_font(FONT_BOLD_PATHS, 52)
        t3 = get_font(FONT_REG_PATHS,  38)

        # Shadow effect
        for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
            draw.text((W//2 + dx, 220 + dy), topic,
                      font=t1, fill=(0, 0, 0), anchor="mm")
        draw.text((W//2, 220), topic, font=t1, fill=th["gold"], anchor="mm")

        # Subtitle from slide title
        title_lines = textwrap.wrap(slide["title"], width=50)
        ty = 340
        for line in title_lines[:2]:
            draw.text((W//2, ty), line, font=t2, fill=th["text"], anchor="mm")
            ty += 65

        draw.rectangle([(W//2 - 300, ty + 20), (W//2 + 300, ty + 24)], fill=th["accent"])
        ty += 60

        content_lines = textwrap.wrap(slide["content"], width=60)
        for line in content_lines[:4]:
            draw.text((80, ty), line, fill=th["subtext"], font=get_font(FONT_REG_PATHS, 38))
            ty += 52

    else:
        # Regular slide
        title_font  = get_font(FONT_BOLD_PATHS, 68)
        title_lines = textwrap.wrap(slide["title"].upper(), width=30)
        ty = 130
        for line in title_lines[:2]:
            draw.text((W//2, ty), line, fill=th["text"], font=title_font, anchor="mm")
            ty += 82

        # Accent divider
        draw.rectangle([(80, ty + 15), (W - 80, ty + 19)], fill=th["accent"])
        ty += 55

        # Content
        content_font  = get_font(FONT_REG_PATHS, 40)
        content_lines = textwrap.wrap(slide["content"], width=58)
        for line in content_lines[:6]:
            draw.text((80, ty), line, fill=th["text"], font=content_font)
            ty += 55

        # Key points
        if slide.get("key_points"):
            ty += 20
            bf = get_font(FONT_BOLD_PATHS, 36)
            for pt in slide["key_points"][:3]:
                draw.text((80, ty), f"✦ {pt}", fill=th["accent"], font=bf)
                ty += 50

    # Slide type badge bottom-right
    stype = slide.get("slide_type", "")
    if stype in ("concept", "example", "practice"):
        badge_colors = {"concept": th["accent"], "example": th["green"], "practice": th["gold"]}
        draw.text((W - 40, H - 45), f"[{stype.upper()}]",
                  fill=(*badge_colors.get(stype, th["accent"]), 200),
                  font=get_font(FONT_BOLD_PATHS, 26), anchor="ra")

    # Bottom bar
    draw.rectangle([(0, H - 8), (W, H)], fill=th["accent"])

    img.save(str(path), quality=95)


# ─── VOICE ────────────────────────────────────────────────────────────────────
async def gen_voice(text: str, path: Path):
    tts_speed = ht.get_tts_speed()
    rate_pct  = int((tts_speed - 1.0) * 100)
    rate_str  = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
    await edge_tts.Communicate(text, VOICE, rate=rate_str).save(str(path))


# ─── YOUTUBE UPLOAD ───────────────────────────────────────────────────────────
def get_youtube_service():
    try:
        # English channel uses different credentials in Phase 3
        creds_key  = "YOUTUBE_CREDENTIALS_EN" if LANG == "en" else "YOUTUBE_CREDENTIALS"
        creds_json = os.environ.get(creds_key)
        if not creds_json and os.path.exists("token.json"):
            with open("token.json") as f: creds_json = f.read()
        if not creds_json: return None
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        return build("youtube", "v3", credentials=creds)
    except Exception:
        return None


def upload_to_youtube(video_path: Path, title: str, description: str, tags: list):
    youtube = get_youtube_service()
    if not youtube:
        print(f"❌ YouTube service unavailable [{LANG}] — skipping")
        return None

    body = {
        "snippet": {
            "title":       title[:100],
            "description": description,
            "tags":        tags[:30],
            "categoryId":  "27"   # Education
        },
        "status": {
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"🚀 Uploading [{LANG.upper()}]: {title[:60]}...")
    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status: print(f"  {int(status.progress() * 100)}%")
        vid_id = response["id"]
        print(f"✅ Uploaded [{LANG.upper()}]: https://youtube.com/watch?v={vid_id}")
        return vid_id
    except Exception as e:
        print(f"❌ Upload failed [{LANG}]: {e}")
        return None


# ─── BUILD META ───────────────────────────────────────────────────────────────
def build_meta(data: dict, today_str: str):
    vid_title    = data.get("video_title", f"Week {data.get('week_number',1)}: {data.get('topic','')} | AI360 Trading")
    vid_desc_raw = data.get("video_description", "")
    week_num     = data.get("week_number", 1)
    topic        = data.get("topic", "")
    key_takeaway = data.get("key_takeaway", "")

    tags        = seo.get_video_tags(mode=CONTENT_MODE, is_short=False)
    hashtag_str = " ".join([f"#{t}" for t in tags[:15]])

    full_desc = (
        f"📚 {vid_desc_raw}\n\n"
        f"🎯 Key Takeaway: {key_takeaway}\n\n"
        f"📖 This is Week {week_num} of our complete 52-week stock market course.\n"
        f"   Start from Week 1: ai360trading.in/course\n\n"
        f"🌐 Website: https://ai360trading.in\n"
        f"📱 Telegram Signals: https://t.me/ai360trading\n"
        f"⚠️ Educational content only. Not financial advice.\n\n"
        f"#ai360trading #StockMarket #TradingEducation {hashtag_str}"
    )

    return vid_title, full_desc, tags


# ─── MAIN ─────────────────────────────────────────────────────────────────────
async def run():
    today_str = datetime.now().strftime("%d %b %Y")
    today_fn  = datetime.now().strftime("%Y%m%d")

    # Get this week's course topic
    week_num, topic, subtitle = get_course_week()
    print(f"📖 Course Week {week_num}: {topic} — {subtitle}")

    # Generate script
    data   = generate_script(week_num, topic, subtitle)
    slides = data["slides"]

    # Build meta
    vid_title, full_desc, tags = build_meta(data, today_str)
    print(f"📋 Title: {vid_title}")

    # ── Render slides + voice ─────────────────────────────────────────────────
    clips = []
    for i, s in enumerate(slides):
        img_path   = OUT / f"edu_{LANG}_{i}.png"
        audio_path = OUT / f"edu_{LANG}_{i}.mp3"

        make_slide(s, i + 1, len(slides), week_num, topic, img_path, is_first=(i == 0))
        await gen_voice(s["content"], audio_path)

        voice_clip  = AudioFileClip(str(audio_path))
        duration    = voice_clip.duration + 1.0
        clip        = ImageClip(str(img_path)).set_duration(duration).set_audio(voice_clip)
        clips.append(clip)

    # ── Render video ──────────────────────────────────────────────────────────
    video_path = OUT / f"education_video_{LANG}.mp4"
    concatenate_videoclips(clips, method="compose").write_videofile(
        str(video_path), fps=FPS, codec="libx264", audio_codec="aac",
        remove_temp=True, logger=None
    )

    total_duration = sum(c.duration for c in clips)
    print(f"✅ Video rendered [{LANG.upper()}]: {video_path.name} | {total_duration/60:.1f} min")

    if total_duration >= 480:
        print("✅ MID-ROLL ADS ENABLED (>8 minutes)")

    # ── Upload ────────────────────────────────────────────────────────────────
    youtube_tags = [t for t in tags if t.isascii()]
    video_id     = upload_to_youtube(video_path, vid_title, full_desc, youtube_tags)

    # ── Save meta JSON ────────────────────────────────────────────────────────
    meta = {
        "title":            vid_title,
        "description":      full_desc,
        "tags":             tags,
        "week_number":      week_num,
        "topic":            topic,
        "subtitle":         subtitle,
        "lang":             LANG,
        "content_mode":     CONTENT_MODE,
        "duration_minutes": round(total_duration / 60, 1),
        "mid_roll_eligible": total_duration >= 480,
        "youtube_video_id": video_id or "",
        "youtube_video_url": f"https://youtube.com/watch?v={video_id}" if video_id else "",
    }

    meta_path = OUT / f"education_meta_{today_fn}_{LANG}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 Saved meta: {meta_path.name}")

    print(f"\n{'='*60}")
    print(f"✅ EDUCATION DONE — Week {week_num} | {LANG.upper()} | {today_str}")
    print(f"   Topic    : {topic}")
    print(f"   Duration : {total_duration/60:.1f} min")
    print(f"   Video ID : {video_id or 'FAILED'}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(run())
