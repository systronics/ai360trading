"""
generate_education.py — Part 2: Daily Education Video
======================================================
Fixes applied (April 2026):
  Fix 1 — Searchable YouTube titles: Topic + Date + Channel name enforced
  Fix 2 — 12 slides (~8-10 min video) for mid-roll ad eligibility
  Fix 3 — 200+ word structured description with keywords
  Fix 4 — Auto playlist assignment after upload
  Fix 5 — End screen on every video

Self-healing AI chain: Groq → Gemini → Claude → OpenAI → Template fallback.
This system is built to run forever for the AI360 Trading family.
"""

import os, sys, json, asyncio, textwrap, time
from datetime import datetime
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip,
    concatenate_videoclips, concatenate_audioclips
)

from content_calendar import get_todays_education_topic, get_holiday_topic

# YouTube upload
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── CONFIG ──────────────────────────────────────────────────────────────────

OUT        = Path("output")
MUSIC_DIR  = Path("public/music")
W, H       = 1920, 1080
FPS        = 24
VOICE      = "hi-IN-SwaraNeural"
CHANNEL    = "AI360 Trading"
NUM_SLIDES = 12    # Fix 2: 12 slides × ~45s each ≈ 9+ minutes

os.makedirs(OUT, exist_ok=True)
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

# ─── PLAYLIST IDs ────────────────────────────────────────────────────────────
# Fix 4: These are read from GitHub Secrets for security.
# Set PLAYLIST_NIFTY_ANALYSIS, PLAYLIST_SWING_TRADE, PLAYLIST_ZENO_WISDOM,
# PLAYLIST_WEEKLY_OUTLOOK in your GitHub Actions Secrets.
# Create playlists once in YouTube Studio, paste their IDs into Secrets.
PLAYLIST_IDS = {
    "education": os.environ.get("PLAYLIST_EDUCATION", ""),         # "Trading Education"
    "swing":     os.environ.get("PLAYLIST_SWING_TRADE", ""),       # "Swing Trade Setups"
    "zeno":      os.environ.get("PLAYLIST_ZENO_WISDOM", ""),       # "ZENO Market Wisdom"
    "weekly":    os.environ.get("PLAYLIST_WEEKLY_OUTLOOK", ""),    # "Weekly Outlook"
}

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
    day       = datetime.now().weekday()
    music_map = {0: "bgmusic1.mp3", 1: "bgmusic2.mp3", 2: "bgmusic3.mp3",
                 3: "bgmusic1.mp3", 4: "bgmusic2.mp3", 5: "bgmusic3.mp3", 6: "bgmusic1.mp3"}
    f = MUSIC_DIR / music_map[day]
    if f.exists():
        return f
    for f in MUSIC_DIR.glob("*.mp3"):
        return f
    return None

# ─── SELF-HEALING AI CLIENT ──────────────────────────────────────────────────

def _try_groq(prompt, max_tokens=3500):
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        resp   = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.75,
            max_tokens=max_tokens
        )
        data = json.loads(resp.choices[0].message.content)
        print("✅ AI generated via Groq")
        return data
    except Exception as e:
        print(f"⚠️ Groq failed: {e}")
        return None

def _try_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        resp  = model.generate_content(
            f"Respond ONLY with valid JSON, no markdown, no backticks:\n\n{prompt}"
        )
        text = resp.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text.strip())
        print("✅ AI generated via Gemini")
        return data
    except Exception as e:
        print(f"⚠️ Gemini failed: {e}")
        return None

def _try_claude(prompt):
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg    = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=3500,
            messages=[{
                "role":    "user",
                "content": f"Respond ONLY with valid JSON, no markdown:\n\n{prompt}"
            }]
        )
        text = msg.content[0].text.strip()
        data = json.loads(text)
        print("✅ AI generated via Claude")
        return data
    except Exception as e:
        print(f"⚠️ Claude failed: {e}")
        return None

def _try_openai(prompt):
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp   = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.75,
            max_tokens=3500
        )
        data = json.loads(resp.choices[0].message.content)
        print("✅ AI generated via OpenAI")
        return data
    except Exception as e:
        print(f"⚠️ OpenAI failed: {e}")
        return None

def generate_with_fallback(prompt):
    """Try all 4 AI providers. Never fails the workflow."""
    for fn in [_try_groq, _try_gemini, _try_claude, _try_openai]:
        result = fn(prompt)
        if result and isinstance(result, dict) and result.get("slides"):
            return result
    print("⚠️ All AI providers failed — using topic slides directly")
    return None

# ─── TITLE BUILDER ───────────────────────────────────────────────────────────
# Fix 1: Searchable title format.
# "Mahavir Jayanti 2026 — Stock Market Closed? Best Stocks to Watch | AI360 Trading"
# Not "ZENO Wisdom | 20260324"

def build_searchable_edu_title(topic_title, date_fmt, category, level):
    """
    Build a searchable YouTube education title.
    Format: "[Topic] [Date] | [Category] for [Level] | AI360 Trading"
    People search "RSI explained" or "swing trading strategy" — title must match.
    """
    # Shorten topic if needed
    topic_short = topic_title[:45] if len(topic_title) > 45 else topic_title
    base = f"{topic_short} {date_fmt} | {category} | AI360 Trading"

    if len(base) > 95:
        base = f"{topic_short} | {category} | AI360 Trading"

    return base[:100]

# ─── DESCRIPTION BUILDER ─────────────────────────────────────────────────────
# Fix 3: Rich 200+ word structured description.

def build_full_description(ai_desc, topic, date_fmt, part1_url, part2_id):
    """Build structured 200+ word description for education video."""
    part1_section = f"\n▶️ Part 1 — Market Analysis: {part1_url}\n" if part1_url else ""
    part2_section = f"\n▶️ This video: https://youtube.com/watch?v={part2_id}\n" if part2_id else ""

    category_tags = {
        "Options":            "#Options #OptionsTrading #OptionsStrategy",
        "Technical Analysis": "#TechnicalAnalysis #CandlestickPatterns #RSI #MACD",
        "Global Macro":       "#GlobalMarkets #MacroEconomics #FedReserve",
        "Trading Strategy":   "#TradingStrategy #SwingTrading #PriceAction",
        "Psychology":         "#TradingPsychology #MindsetTrading",
        "Risk Management":    "#RiskManagement #StopLoss #PositionSizing",
        "Personal Finance":   "#PersonalFinance #Investing #WealthBuilding",
        "Fundamental Analysis": "#FundamentalAnalysis #StockAnalysis",
        "Crypto":             "#Bitcoin #Crypto #CryptoTrading",
        "Commodities":        "#Gold #CrudeOil #Commodities",
        "Motivational":       "#TradingMotivation #TradingMindset",
        "Savings and Investment": "#SIP #IndexFund #WealthBuilding",
        "Market Emotions":    "#FearAndGreed #MarketPsychology",
        "Storytelling":       "#WallStreet #TradingStories #InvestingLessons",
    }.get(topic["category"], "#Trading #Finance #Investing")

    desc = f"""{ai_desc}

📚 Topic: {topic['title']}
🎯 Level: {topic['level']} | Category: {topic['category']}
📅 Date: {date_fmt}

{part1_section}

🎓 WHAT YOU WILL LEARN:
  • Complete explanation of {topic['title']}
  • Real examples using Indian and global markets
  • Practical application for retail traders at {topic['level']} level
  • How to use this knowledge for Nifty50, stocks, and global markets
  • Common mistakes and how to avoid them

This is Part 2 of today's AI360 Trading daily video series.
Part 1 covers live market analysis. This video covers education and strategy.
Together they give you a complete daily trading education.

🔔 SUBSCRIBE for daily trading education — posted every morning.
📱 FREE Telegram signals: https://t.me/ai360trading
📊 Advance signals (₹499/month): https://t.me/ai360trading_Advance
🌐 Website + articles: https://ai360trading.in
📘 Facebook: https://facebook.com/ai360trading

⚠️ DISCLAIMER: Educational purposes only. Not SEBI registered. Do your own research.

#TradingEducation #LearnTrading #AI360Trading #StockMarketIndia #TradingIndia
#TradingHindi #NSE #BSE #Nifty50 #ShareMarket {category_tags}
#FinancialLiteracy #Investing #Finance #GlobalInvesting"""

    return desc

# ─── SCRIPT GENERATOR ────────────────────────────────────────────────────────

def generate_edu_slides(topic, part1_url, date_fmt):
    today    = datetime.now().strftime("%A, %d %B %Y")
    today_fmtshort = datetime.now().strftime("%d %b %Y")

    # Fix 1 instruction
    title_instruction = f"""
"video_title" MUST follow this EXACT format (max 95 chars):
  "[Topic] {today_fmtshort} | [Category] | AI360 Trading"
Examples of GOOD titles:
  "RSI Complete Guide {today_fmtshort} | Technical Analysis | AI360 Trading"
  "Options Trading Basics {today_fmtshort} | Beginner Guide | AI360 Trading"
  "Swing Trading Strategy {today_fmtshort} | How to Trade Nifty | AI360 Trading"
NEVER generate titles like "ZENO Wisdom" or generic titles without the topic name.
People search the topic name — the title must match that search intent.
"""

    desc_instruction = """
"video_description" must be 3-5 sentences, 80-100 words, in Hinglish.
Cover: what concept is taught, who it is for, what they will be able to do after watching.
"""

    # We request NUM_SLIDES but pass the calendar slides as content guide
    calendar_slides = topic.get("slides", [])

    prompt = f"""You are an expert trading educator creating a YouTube education video in Hinglish for AI360 Trading channel.

Today is {today}.
Topic: {topic['title']}
Category: {topic['category']}
Level: {topic['level']}
Target audience: {topic.get('target_audience', 'Indian traders of all levels')}

{title_instruction}

{desc_instruction}

Use the content calendar slides below as your content guide. EXPAND each slide into full spoken content. Add {NUM_SLIDES - len(calendar_slides)} additional slides covering: introduction, real-world examples, common mistakes, and a strong closing with a call to action.

Content calendar slides:
{json.dumps(calendar_slides, ensure_ascii=False)}

Generate exactly {NUM_SLIDES} slides total.

Respond ONLY with valid JSON:
{{
  "video_title": "exact format shown above",
  "video_description": "80-100 word Hinglish description",
  "slides": [
    {{
      "title": "slide heading max 8 words",
      "content": "spoken Hinglish content 55-70 words — clear, practical, with real examples",
      "key_takeaway": "one line summary"
    }}
  ]
}}"""

    print(f"🤖 Generating education script: {topic['title']}...")
    data = generate_with_fallback(prompt)

    if not data:
        data = _fallback_edu_slides(topic, date_fmt)

    # Fix 1: Override title if AI didn't follow format
    raw_title = data.get("video_title", "")
    if "AI360 Trading" not in raw_title:
        data["video_title"] = build_searchable_edu_title(
            topic["title"],
            datetime.now().strftime("%d %b %Y"),
            topic["category"],
            topic["level"]
        )

    # Ensure we have exactly NUM_SLIDES
    slides = data.get("slides", [])
    if len(slides) < NUM_SLIDES:
        # Pad with fallback slides
        fallback = _fallback_edu_slides(topic, date_fmt)
        extra    = fallback["slides"]
        while len(slides) < NUM_SLIDES and extra:
            slides.append(extra.pop(0))
        data["slides"] = slides
    elif len(slides) > NUM_SLIDES:
        data["slides"] = slides[:NUM_SLIDES]

    print(f"✅ {len(data['slides'])} education slides ready")
    print(f"📌 Title: {data['video_title']}")
    return data

def _fallback_edu_slides(topic, date_fmt):
    """Emergency fallback using content_calendar slides directly."""
    title_short = topic["title"][:40]
    fallback_slides = []

    # Intro slide
    fallback_slides.append({
        "title": f"Introduction: {title_short[:30]}",
        "content": f"Aaj hum seekhenge {topic['title']} ke baare mein. Yeh concept {topic['level']} level ke traders ke liye bahut important hai. AI360 Trading pe hum roz naya concept cover karte hain taaki aap ek complete trader ban sakein.",
        "key_takeaway": f"Aaj ka topic: {topic['title']}"
    })

    # Calendar slides as-is
    for s in topic.get("slides", []):
        heading = s.get("heading", "Trading Concept")
        points  = s.get("points", ["Important concept"])
        content = f"{heading}. " + " ".join(points[:3]) + " Yeh concept bahut important hai practical trading mein."
        fallback_slides.append({
            "title":        heading[:50],
            "content":      content[:300],
            "key_takeaway": points[0] if points else heading
        })

    # Closing slides
    fallback_slides.append({
        "title": "Common Mistakes to Avoid",
        "content": f"{topic['title']} seekhne ke baad log kuch common galtiyan karte hain. Sabse pehli galti hai theory samajhna aur practice skip karna. Hamesha paper trading se start karo. Apna stop loss kabhi remove mat karo. Risk management ke bina koi bhi strategy kaam nahi karti.",
        "key_takeaway": "Theory ke saath practice karo"
    })
    fallback_slides.append({
        "title": "How to Apply This Today",
        "content": f"Aaj se hi {topic['title']} apply karna shuru karo. Paper trading account pe pehle practice karo. Apni trading journal mein notes likho. Agle 30 din mein 10 trades is concept se karo aur results track karo. Consistency hi real learning hai.",
        "key_takeaway": "Aaj se paper trading mein apply karo"
    })
    fallback_slides.append({
        "title": "Quick Recap",
        "content": f"Aaj humne {topic['title']} ke baare mein seekha. Main points the: concept ki basic understanding, practical application, aur common mistakes. Yeh knowledge aapko better trader banayegi. AI360 Trading pe daily aisi education milti hai.",
        "key_takeaway": "Daily seekhna hi success ka raasta hai"
    })
    fallback_slides.append({
        "title": "Subscribe and Join Telegram",
        "content": "Agar aaj ka video helpful laga toh subscribe zaroor karo. Har din market analysis aur education videos milenge. Free Telegram channel pe live signals milte hain. Link description mein hai. AI360 Trading family ka hissa bano aur apni trading journey accelerate karo.",
        "key_takeaway": "Subscribe + Telegram join karo"
    })

    # Trim or pad to NUM_SLIDES
    while len(fallback_slides) < NUM_SLIDES:
        fallback_slides.append({
            "title": "Bonus Trading Tip",
            "content": "Har successful trader mein ek cheez common hai — discipline. Strategy se zyada important hai apni strategy follow karna consistently. Ek average strategy followed consistently beats an excellent strategy followed inconsistently. Yeh rule trading mein, investing mein, aur life mein kaam karta hai.",
            "key_takeaway": "Discipline + consistency = success"
        })

    title_fmt = datetime.now().strftime("%d %b %Y")
    return {
        "video_title": build_searchable_edu_title(
            topic["title"], title_fmt, topic["category"], topic["level"]
        ),
        "video_description": f"Aaj {date_fmt} ko hum {topic['title']} seekh rahe hain. {topic['level']} level content, practical examples ke saath. AI360 Trading pe daily trading education milti hai.",
        "slides": fallback_slides[:NUM_SLIDES]
    }

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

    # Top bar
    draw.rectangle([(0, 0), (W, 10)], fill=th["accent"])

    # Category badge
    draw.text((40, 35), f"📚 {topic['category'].upper()}",
              fill=(*th["subtext"], 220), font=get_font(FONT_BOLD_PATHS, 30), anchor="la")

    # Level badge
    draw.text((W - 40, 35), f"● {level}",
              fill=(*th["accent"], 200), font=get_font(FONT_BOLD_PATHS, 28), anchor="ra")

    # Channel watermark
    draw.text((W // 2, 38), "ai360trading.in",
              fill=(*th["subtext"], 160), font=get_font(FONT_REG_PATHS, 26), anchor="mm")

    # Slide counter
    draw.text((W // 2, 80), f"{idx} of {total}",
              fill=(*th["subtext"], 180), font=get_font(FONT_REG_PATHS, 28), anchor="mm")

    # Title
    title_font  = get_font(FONT_BOLD_PATHS, 68)
    title_lines = textwrap.wrap(slide["title"].upper(), width=30)
    ty = 150
    for line in title_lines[:2]:
        draw.text((W // 2, ty), line, fill=th["text"], font=title_font, anchor="mm")
        ty += 84

    # Divider
    draw.rectangle([(80, ty + 15), (W - 80, ty + 19)], fill=th["accent"])
    ty += 55

    # Content
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
        draw.rectangle([(60, box_top), (63, box_bot)],     fill=th["accent"])
        draw.text((90, box_top + 35), f"💡 {slide['key_takeaway']}",
                  fill=th["accent"], font=get_font(FONT_BOLD_PATHS, 34), anchor="lm")

    # Bottom bar
    draw.rectangle([(0, H - 10), (W, H)], fill=th["accent"])
    img.save(str(path), quality=95)

# ─── VOICE ───────────────────────────────────────────────────────────────────

async def gen_voice(text, path):
    await edge_tts.Communicate(text, VOICE).save(str(path))

# ─── YOUTUBE HELPERS ─────────────────────────────────────────────────────────

def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json and os.path.exists("token.json"):
            with open("token.json") as f:
                creds_json = f.read()
        if not creds_json:
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
            "description": description[:4900],
            "tags":        tags,
            "categoryId":  "27"
        },
        "status": {
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"🚀 Uploading: {title[:70]}...")
    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  Uploaded {int(status.progress() * 100)}%")
        video_id = response["id"]
        print(f"✅ YouTube upload success! ID: {video_id}")
        return video_id
    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        return None

def update_part1_description(part1_id, part1_desc, part2_url):
    """Add Part 2 link to Part 1 description."""
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

# ─── FIX 4: PLAYLIST ASSIGNMENT ──────────────────────────────────────────────

def add_to_playlist(youtube, video_id, playlist_id, playlist_name):
    """Add video to a YouTube playlist. Non-critical — never crashes workflow."""
    if not playlist_id or not video_id:
        print(f"⚠️ Playlist '{playlist_name}': ID not set in GitHub Secrets — skipping")
        return False
    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind":    "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        ).execute()
        print(f"✅ Added to playlist: {playlist_name}")
        return True
    except Exception as e:
        print(f"⚠️ Playlist '{playlist_name}' failed (non-critical): {e}")
        return False

def assign_to_playlists(youtube, video_id, topic):
    """Fix 4: Assign education video to relevant playlists."""
    if not youtube or not video_id:
        return
    # Always add to education playlist
    add_to_playlist(youtube, video_id, PLAYLIST_IDS["education"], "Trading Education")
    # Category-based playlist assignment
    cat = topic.get("category", "")
    if cat in ["Trading Strategy", "Technical Analysis"]:
        add_to_playlist(youtube, video_id, PLAYLIST_IDS["swing"], "Swing Trade Setups")
    if cat in ["Motivational", "Storytelling", "Market Emotions"]:
        add_to_playlist(youtube, video_id, PLAYLIST_IDS["zeno"], "ZENO Market Wisdom")
    # Weekly outlook on Fridays
    if datetime.now().weekday() == 4:
        add_to_playlist(youtube, video_id, PLAYLIST_IDS["weekly"], "Weekly Outlook")

# ─── FIX 5: END SCREEN ───────────────────────────────────────────────────────

def add_end_screen(youtube, video_id, video_duration_seconds):
    """
    Fix 5: 20-second end screen — subscribe + latest video.
    Non-critical — video is already live if this fails.
    """
    if not youtube or not video_id:
        return
    if video_duration_seconds < 25:
        print("⚠️ Video too short for end screen — skipping")
        return

    end_ms   = int(video_duration_seconds * 1000)
    start_ms = end_ms - 20000

    try:
        youtube.videos().update(
            part="endScreens",
            body={
                "id": video_id,
                "endScreens": {
                    "elements": [
                        {
                            "type":          "SUBSCRIBE",
                            "left":          0.4,
                            "top":           0.6,
                            "width":         0.2,
                            "startOffsetMs": start_ms,
                            "endOffsetMs":   end_ms
                        },
                        {
                            "type":          "RECENT_UPLOAD",
                            "left":          0.65,
                            "top":           0.4,
                            "width":         0.3,
                            "startOffsetMs": start_ms,
                            "endOffsetMs":   end_ms
                        }
                    ]
                }
            }
        ).execute()
        print("✅ End screen added (subscribe + latest video)")
    except Exception as e:
        print(f"⚠️ End screen failed (non-critical): {e}")
        print("   To fix: re-authorise YouTube OAuth with youtube.force-ssl scope")

# ─── MAIN ────────────────────────────────────────────────────────────────────

async def run():
    today_str = datetime.now().strftime("%Y%m%d")
    date_fmt  = datetime.now().strftime("%d %B %Y")
    date_fmtshort = datetime.now().strftime("%d %b %Y")

    # 1. Read Part 1 video ID
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
        print("⚠️ No analysis_video_id.txt — continuing without Part 1 link")

    # 2. Get today's education topic
    content_mode = os.environ.get("CONTENT_MODE", "market").lower()
    if content_mode == "holiday":
        from content_calendar import get_holiday_topic
        topic = get_holiday_topic()
        print(f"📚 Holiday topic: {topic['title']}")
    else:
        topic = get_todays_education_topic()
        print(f"📚 Topic: {topic['title']} | {topic['category']} | {topic['level']}")

    # 3. Generate script
    data       = generate_edu_slides(topic, part1_url, date_fmt)
    slides     = data["slides"]
    vid_title  = data["video_title"]
    ai_desc    = data.get("video_description", "")

    # Fix 3: Rich description (video_id added after upload)
    # We pass empty video_id now and it's fine — description still has all links
    full_desc = build_full_description(ai_desc, topic, date_fmt, part1_url, "")

    # SEO tags
    tags = [
        topic["title"][:50], topic["category"], "Trading Education", "AI360Trading",
        "StockMarketIndia", "LearnTrading", "NSE", "BSE",
        "TradingHindi", "TradingIndia", topic["level"],
        "Nifty50", "Finance", "Investing", "TechnicalAnalysis",
        "SwingTrading", "TradingStrategy", "USStocks", "GlobalMarkets",
        "FinancialLiteracy"
    ]
    tags = [t for t in tags if t][:20]  # clean and cap at 20

    # 4. Build slides + voice
    print(f"\n🎬 Building {len(slides)} education slides...")
    clips          = []
    total_duration = 0.0

    for i, s in enumerate(slides):
        img_path   = OUT / f"edu_{i}.png"
        audio_path = OUT / f"edu_{i}.mp3"

        make_edu_slide(s, i + 1, len(slides), topic, img_path)
        await gen_voice(s["content"], audio_path)

        voice_clip     = AudioFileClip(str(audio_path))
        slide_duration = voice_clip.duration + 0.8
        total_duration += slide_duration

        bg_path = get_bg_music()
        if bg_path:
            try:
                bg = AudioFileClip(str(bg_path))
                if bg.duration < slide_duration:
                    loops = int(slide_duration / bg.duration) + 1
                    bg    = concatenate_audioclips([bg] * loops)
                bg          = bg.subclip(0, slide_duration).volumex(0.07)
                slide_audio = CompositeAudioClip([voice_clip, bg])
            except Exception as e:
                print(f"⚠️ Music error slide {i}: {e}")
                slide_audio = voice_clip
        else:
            slide_audio = voice_clip

        clip = ImageClip(str(img_path)).set_duration(slide_duration).set_audio(slide_audio)
        clips.append(clip)
        print(f"  Slide {i+1}/{len(slides)} ready ({slide_duration:.1f}s)")

    print(f"\n⏱️ Total estimated duration: {total_duration:.0f}s ({total_duration/60:.1f} min)")
    if total_duration < 480:
        print("⚠️ WARNING: Video under 8 minutes — mid-roll ads will not activate")

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
    part2_id = upload_to_youtube(video_path, vid_title, full_desc, tags)

    # 7. Post-upload: playlists + end screen
    youtube = get_youtube_service()
    if part2_id and youtube:
        # Fix 4: Playlists
        assign_to_playlists(youtube, part2_id, topic)
        # Fix 5: End screen
        add_end_screen(youtube, part2_id, total_duration)

    # 8. Save ID and update Part 1 description
    if part2_id:
        (OUT / "education_video_id.txt").write_text(part2_id, encoding="utf-8")
        part2_url = f"https://youtube.com/watch?v={part2_id}"
        if part1_id and part1_id != "UPLOAD_FAILED":
            update_part1_description(part1_id, full_desc, part2_url)
    else:
        (OUT / "education_video_id.txt").write_text("UPLOAD_FAILED", encoding="utf-8")
        part2_url = ""

    # 9. Save metadata
    meta = {
        "title":       vid_title,
        "description": full_desc,
        "video_id":    part2_id or "UPLOAD_FAILED",
        "video_url":   part2_url,
        "part1_url":   part1_url,
        "topic":       topic["title"],
        "category":    topic["category"],
        "level":       topic["level"],
        "duration_s":  round(total_duration),
        "slides":      len(slides),
        "date":        today_str
    }
    (OUT / f"education_meta_{today_str}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"\n📋 Summary:")
    print(f"   Title:    {vid_title}")
    print(f"   Duration: {total_duration/60:.1f} min")
    print(f"   Slides:   {len(slides)}")
    print(f"   Video ID: {part2_id or 'FAILED'}")
    print(f"✅ generate_education.py complete")

if __name__ == "__main__":
    asyncio.run(run())
