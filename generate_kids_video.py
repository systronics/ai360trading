"""
generate_kids_video.py — HerooQuest v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v2.0 CHANGES vs v1.0:
1. Dual language: Hindi (Swara) + English (Jenny) — same story
2. Short script is DIFFERENT from main video — cliffhanger only
3. "Did You Know?" short — separate fun fact, pure viral
4. Heroo character visible in FIRST FRAME (thumbnail fix)
5. Story series auto-advances through 52-week calendar
6. Age-appropriate content for under-14 (India + USA/UK)

Story format:
  Main video (5-8 min): Full story — adventure + moral lesson
  Short 1 (45 sec)    : Cliffhanger from story → drives to full video
  Short 2 (30 sec)    : "Did You Know?" fun fact — pure viral

HEROO character:
  Placed large (60% frame height) in first frame of every video
  Ensures YouTube auto-thumbnail shows Heroo face
  Custom thumbnail upload now works after phone verification
"""

import os
import json
import asyncio
import textwrap
from datetime import datetime, date
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from human_touch import ht, seo
from ai_client import ai

# ─── CONFIG ───────────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
LANG         = os.environ.get("KIDS_LANG", "hi")     # "hi" or "en"
OUTPUT_TYPE  = os.environ.get("KIDS_OUTPUT", "full")  # "full", "short", "didyouknow"

print(f"[HEROOQUEST v2.0] lang={LANG.upper()} output={OUTPUT_TYPE.upper()}")

OUT       = Path("output")
IMAGE_DIR = Path("public/image")
W_FULL, H_FULL = 1920, 1080   # 16:9 full video
W_SHORT, H_SHORT = 1080, 1920  # 9:16 shorts
FPS       = 24

VOICE_HI = "hi-IN-SwaraNeural"
VOICE_EN = "en-US-JennyNeural"
VOICE    = VOICE_HI if LANG == "hi" else VOICE_EN

os.makedirs(OUT, exist_ok=True)

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

# ─── STORY SERIES CALENDAR — 52 weeks ────────────────────────────────────────
STORY_START = date(2026, 5, 15)

STORY_SERIES = [
    # (week, series, episode, title_hi, title_en, moral)
    ( 1, "Heroo aur Jungle ka Raaz", 1, "Sona Hiran",          "The Golden Deer",         "Patience wins over greed"),
    ( 2, "Heroo aur Jungle ka Raaz", 2, "Toota Ped",            "The Broken Tree",         "Even broken things have value"),
    ( 3, "Heroo aur Jungle ka Raaz", 3, "Baarish ki Raat",      "The Rainy Night",         "Helping others is true strength"),
    ( 4, "Heroo aur Jungle ka Raaz", 4, "Pahaad ki Chhoti",     "Top of the Mountain",     "Big goals need small steps"),
    ( 5, "Heroo aur Jungle ka Raaz", 5, "Jaadu ki Nadi",        "The Magic River",         "Sharing makes everything grow"),
    ( 6, "Heroo aur Jungle ka Raaz", 6, "Andhere ki Roshni",    "Light in the Dark",       "Courage comes from inside"),
    ( 7, "Heroo aur Jungle ka Raaz", 7, "Ek Naya Dost",         "A New Friend",            "Different is not wrong"),
    ( 8, "Heroo aur Jungle ka Raaz", 8, "Jungle ka Raja",       "King of the Jungle",      "True leaders protect others"),
    ( 9, "Heroo ki Space Journey",   1, "Sitaaron ki Duniya",   "World of Stars",          "Curiosity opens new worlds"),
    (10, "Heroo ki Space Journey",   2, "Chaand ka Safar",      "Journey to the Moon",     "Hard work reaches the sky"),
    (11, "Heroo ki Space Journey",   3, "Alien Dost",           "Alien Friend",            "Kindness speaks every language"),
    (12, "Heroo ki Space Journey",   4, "Gravity ka Khel",      "The Gravity Game",        "Rules exist for a reason"),
    (13, "Heroo ki Space Journey",   5, "Supernova",            "The Supernova",           "Big changes bring new beginnings"),
    (14, "Heroo ki Space Journey",   6, "Vaapsi",               "The Return",              "Home is where love lives"),
    (15, "Heroo ki Space Journey",   7, "Robot Dost",           "Robot Friend",            "Technology helps, humans lead"),
    (16, "Heroo ki Space Journey",   8, "Galaxy ka Raaz",       "Secret of the Galaxy",    "The universe has answers for those who look"),
    (17, "Heroo aur Time Machine",   1, "Dinosaur Zamaana",     "Dinosaur Age",            "Change is natural"),
    (18, "Heroo aur Time Machine",   2, "Akbar ka Darbaar",     "Akbar's Court",           "Wisdom solves what force cannot"),
    (19, "Heroo aur Time Machine",   3, "Taj Mahal ka Raaz",    "Secret of Taj Mahal",     "Love leaves marks forever"),
    (20, "Heroo aur Time Machine",   4, "Gandhi Ji ke Saath",   "With Gandhi Ji",          "One person can change the world"),
    (21, "Heroo aur Time Machine",   5, "Future City",          "Future City",             "Today's choices build tomorrow"),
    (22, "Heroo aur Time Machine",   6, "Ice Age",              "The Ice Age",             "Adapt or perish — stay flexible"),
    (23, "Heroo aur Time Machine",   7, "First School",         "The First School",        "Education is the greatest adventure"),
    (24, "Heroo aur Time Machine",   8, "2050 ka Heroo",        "Heroo in 2050",           "The future belongs to the curious"),
    (25, "Heroo aur Magic School",   1, "Pehla Din",            "First Day",               "New beginnings are exciting"),
    (26, "Heroo aur Magic School",   2, "Invisible Ink",        "Invisible Ink",           "Knowledge is a superpower"),
    (27, "Heroo aur Magic School",   3, "Maths ka Jaadu",       "Magic of Maths",          "Numbers explain everything"),
    (28, "Heroo aur Magic School",   4, "Science Fair",         "Science Fair",            "Try, fail, learn, succeed"),
    (29, "Heroo aur Magic School",   5, "Art Class",            "Art Class",               "Everyone creates differently"),
    (30, "Heroo aur Magic School",   6, "Library ka Raaz",      "Library Secret",          "Books are time machines"),
    (31, "Heroo aur Magic School",   7, "Sports Day",           "Sports Day",              "Winning is not everything"),
    (32, "Heroo aur Magic School",   8, "Graduation Day",       "Graduation Day",          "Every ending is a new beginning"),
    (33, "Heroo aur Dost ki Mushkil",1, "Bimaar Dost",          "Sick Friend",             "Being there matters most"),
    (34, "Heroo aur Dost ki Mushkil",2, "Jhooth ki Saza",       "The Lie",                 "Truth is always lighter"),
    (35, "Heroo aur Dost ki Mushkil",3, "Naya Ladka",           "The New Kid",             "Include, don't exclude"),
    (36, "Heroo aur Dost ki Mushkil",4, "Bully ka Saamna",      "Facing the Bully",        "Courage is not the absence of fear"),
    (37, "Heroo aur Dost ki Mushkil",5, "Online Dost",          "Online Friend",           "Be careful online, stay safe"),
    (38, "Heroo aur Dost ki Mushkil",6, "Saccha Dost",          "True Friend",             "Quality over quantity in friendship"),
    (39, "Heroo aur Dost ki Mushkil",7, "Maafi",                "Forgiveness",             "Forgiving is braver than holding grudges"),
    (40, "Heroo aur Dost ki Mushkil",8, "Dosti ka Jashan",      "Friendship Celebration",  "Good friendships last forever"),
    (41, "Heroo aur Dinosaur World", 1, "T-Rex se Dosti",       "Friends with T-Rex",      "Don't judge by appearance"),
    (42, "Heroo aur Dinosaur World", 2, "Pterodactyl ki Udaan", "Pterodactyl Flight",      "Help others reach their potential"),
    (43, "Heroo aur Dinosaur World", 3, "Samudr ka Raaz",       "Ocean Secret",            "There is always more to explore"),
    (44, "Heroo aur Dinosaur World", 4, "Volcano ka Darr",      "Volcano Fear",            "Face fears with friends"),
    (45, "Heroo aur Dinosaur World", 5, "Ice Dino",             "Ice Dinosaur",            "Adapt to survive and thrive"),
    (46, "Heroo aur Dinosaur World", 6, "Vaapsi Ghar",          "Coming Home",             "Adventure is great but home is best"),
    (47, "Heroo Saves the Planet",   1, "Plastic ka Dushman",   "Enemy of Plastic",        "Small actions change the world"),
    (48, "Heroo Saves the Planet",   2, "Paani Bachao",         "Save Water",              "Resources are precious"),
    (49, "Heroo Saves the Planet",   3, "Pedh Lagao",           "Plant Trees",             "Give back to nature"),
    (50, "Heroo Saves the Planet",   4, "Solar Heroo",          "Solar Hero",              "Clean energy is the future"),
    (51, "Heroo Saves the Planet",   5, "Ocean Warrior",        "Ocean Warrior",           "The ocean needs our help"),
    (52, "Heroo Saves the Planet",   6, "Earth Day",            "Earth Day",               "We are all guardians of Earth"),
]

# Fun facts for "Did You Know?" shorts
DID_YOU_KNOW = [
    ("Giraffe", "Giraffes sirf 30 minutes sote hain puri raat mein! 🦒",
     "Giraffes sleep only 30 minutes in a whole night! 🦒"),
    ("Octopus", "Octopus ke teen dil hote hain! 🐙",
     "Octopuses have THREE hearts! 🐙"),
    ("Honey",   "Shahad kabhi kharab nahi hota — 3000 saal purana shahad bhi khaane layak hai! 🍯",
     "Honey never spoils — 3000-year-old honey is still edible! 🍯"),
    ("Banana",  "Kela ek berry hai, lekin strawberry berry nahi hai! 🍌",
     "A banana is a berry, but a strawberry is not! 🍌"),
    ("Dolphin", "Dolphin aankhein khol ke soti hai! 🐬",
     "Dolphins sleep with one eye open! 🐬"),
    ("Sun",     "Suraj ki roshni dharti tak pahunchne mein 8 minute lagte hain! ☀️",
     "Sunlight takes 8 minutes to reach Earth! ☀️"),
    ("Ant",     "Cheenti apne wazan se 50 guna zyada uthaa sakti hai! 🐜",
     "Ants can carry 50 times their own body weight! 🐜"),
    ("Butterfly","Titliyan apne pairon se taste karti hain! 🦋",
     "Butterflies taste with their feet! 🦋"),
    ("Water",   "Ek boond paani mein 1 crore se zyada chhote jaanvar hote hain! 💧",
     "One drop of water contains over 1 million tiny creatures! 💧"),
    ("Brain",   "Insaan ka dimag 24 ghante kaam karta hai — neend mein bhi! 🧠",
     "Your brain works 24 hours — even while you sleep! 🧠"),
    ("Lightning","Bijli ek second mein 10 baar girti hai poori duniya mein! ⚡",
     "Lightning strikes Earth 10 times every second! ⚡"),
    ("Penguin", "Penguins ek saath hi shadi karte hain — sirf ek partner! 🐧",
     "Penguins mate for life — just one partner! 🐧"),
]

def get_story_week() -> tuple:
    today    = date.today()
    delta    = (today - STORY_START).days
    week_idx = (delta // 7) % 52
    return STORY_SERIES[week_idx]

def get_did_you_know() -> tuple:
    today    = date.today()
    idx      = (today - STORY_START).days % len(DID_YOU_KNOW)
    return DID_YOU_KNOW[idx]


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

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ─── THEME — bright, fun, kids ────────────────────────────────────────────────
KIDS_THEMES = [
    {"bg_top": (20, 10, 60),  "bg_bot": (80, 20, 120), "accent": (255, 180, 0),   "text": (255,255,255)},
    {"bg_top": (5, 40, 15),   "bg_bot": (10, 100, 40), "accent": (100, 255, 100), "text": (255,255,255)},
    {"bg_top": (40, 5, 5),    "bg_bot": (120, 20, 20), "accent": (255, 100, 100), "text": (255,255,255)},
    {"bg_top": (5, 30, 60),   "bg_bot": (10, 70, 140), "accent": (100, 200, 255), "text": (255,255,255)},
]

def get_theme(week_idx: int) -> dict:
    return KIDS_THEMES[week_idx % len(KIDS_THEMES)]


# ─── HEROO IMAGE LOADER ───────────────────────────────────────────────────────
def load_heroo(target_height: int) -> Image.Image | None:
    """Load Heroo character PNG. Try multiple filenames."""
    candidates = [
        IMAGE_DIR / "heroo.png",
        IMAGE_DIR / "hero.png",
        IMAGE_DIR / "heroo_happy.png",
        IMAGE_DIR / "heroo_character.png",
    ]
    for p in candidates:
        if p.exists():
            try:
                img = Image.open(str(p)).convert("RGBA")
                w   = int(img.width * (target_height / img.height))
                return img.resize((w, target_height), Image.LANCZOS)
            except Exception as e:
                print(f"[HEROO] Load error {p}: {e}")
    print("[HEROO] ⚠️ No Heroo PNG found — video will have no character. Upload heroo.png to public/image/")
    return None


# ─── SCRIPT GENERATION ────────────────────────────────────────────────────────
def generate_full_story(story_data: tuple) -> dict:
    week, series, ep, title_hi, title_en, moral = story_data
    today  = datetime.now().strftime("%d %b %Y")
    title  = title_hi if LANG == "hi" else title_en

    if LANG == "hi":
        lang_inst = (
            "Write in simple Hindi + Hinglish mix. "
            "Like a grandmother telling a story to a 10-year-old. "
            "Warm, exciting, age-appropriate. No complex words."
        )
        channel   = "HerooQuest"
    else:
        lang_inst = (
            "Write in simple, warm, engaging English for kids aged 6-14. "
            "Like a friendly teacher telling a story. Short sentences. Exciting moments. "
            "Global audience — relatable for Indian, American, and British kids."
        )
        channel = "HerooQuest"

    prompt = f"""You are creating a kids YouTube story video for {channel} channel (under-14 audience).

Story: Episode {ep} of series '{series}'
Title: {title}
Moral: {moral}
Language: {lang_inst}

IMPORTANT RULES:
- Age appropriate for 6-14 years
- No violence, no scary content, no adult themes
- Heroo is a brave, kind, curious boy who helps others
- Every story MUST have a clear moral lesson at the end
- Start with excitement to hook kids in first 3 seconds
- Include 1-2 funny moments to keep kids engaged

Generate exactly 10 slides as valid JSON (10 slides × ~40 sec = ~7 min):
{{
  "video_title": "Heroo: {title} | Episode {ep} | {channel} #KidsStories",
  "video_description": "Fun exciting story with a great lesson for kids! Heroo's adventure today...",
  "series": "{series}",
  "episode": {ep},
  "moral": "{moral}",
  "cliffhanger": "The most exciting 2-sentence moment from the story — used for the Short",
  "did_you_know_fact": "One related fun science/nature fact for a 30-sec Short",
  "slides": [
    {{
      "title": "slide heading — max 5 words",
      "content": "story narration 60-80 words. ONE scene per slide. Vivid, exciting, simple.",
      "scene_type": "intro|action|funny|scary_moment|lesson|moral|outro",
      "sound_cue": "optional: [THUNDER] or [LAUGH] or [SUSPENSE] — one word"
    }}
  ]
}}"""

    print(f"🤖 Generating {LANG.upper()} story: {title}")
    try:
        data = ai.generate_json(prompt, content_mode="market", lang=LANG)
        for slide in (data.get("slides") or []):
            if slide.get("content"):
                slide["content"] = ht.humanize(slide["content"], lang=LANG)
        print(f"✅ Story ready: {data.get('video_title','')[:60]}")
        return data
    except Exception as e:
        print(f"⚠️ Story error: {e}")
        return _fallback_story(title, moral, series, ep)

def _fallback_story(title, moral, series, ep):
    return {
        "video_title": f"Heroo: {title} | Episode {ep} | HerooQuest",
        "video_description": f"Heroo ki nayi kahani — {title}. Moral: {moral}",
        "series": series, "episode": ep, "moral": moral,
        "cliffhanger": f"Heroo ko ek bada khatraa aa gaya... kya hua aage?",
        "did_you_know_fact": "Honey never spoils — even 3000-year-old honey is edible!",
        "slides": [{
            "title": title, "content": f"Namaskar dosto! Aaj Heroo ki ek nayi kahani hai — {title}. Tayaar ho? Chalte hain!",
            "scene_type": "intro", "sound_cue": ""
        }] * 10
    }

def generate_short_script_kids(story_data: dict, story_info: tuple) -> str:
    """Generate SEPARATE cliffhanger short script — NOT same as main video."""
    week, series, ep, title_hi, title_en, moral = story_info
    title       = title_hi if LANG == "hi" else title_en
    cliffhanger = story_data.get("cliffhanger", f"Heroo ko ek bada khatraa aa gaya!")

    if LANG == "hi":
        return (
            f"Dosto, aaj Heroo ke saath kuch aisa hua jo aapne kabhi nahi socha hoga! "
            f"{cliffhanger} "
            f"Kya hua aage? Poori kahani dekhne ke liye upar swipe karo aur channel subscribe karo! "
            f"Heroo tumhara wait kar raha hai! 🦸"
        )
    else:
        return (
            f"Hey friends! Something incredible happened to Heroo today! "
            f"{cliffhanger} "
            f"What happened next? Swipe up to watch the full story and subscribe to never miss Heroo's adventures! "
            f"Heroo is waiting for you! 🦸"
        )

def generate_did_you_know_script(fact_data: tuple) -> str:
    """Generate 'Did You Know?' short script."""
    topic, fact_hi, fact_en = fact_data
    fact = fact_hi if LANG == "hi" else fact_en

    if LANG == "hi":
        return (
            f"Kya tum jaante ho? 🤔 "
            f"{fact} "
            f"Heroo ne aaj yeh seekha — aur tum? "
            f"Aaise hi amazing facts ke liye HerooQuest subscribe karo! 🌟"
        )
    else:
        return (
            f"Did you know? 🤔 "
            f"{fact} "
            f"Heroo learned this today — and now you know too! "
            f"Subscribe to HerooQuest for more amazing facts every day! 🌟"
        )


# ─── FRAME RENDERER — FULL VIDEO ─────────────────────────────────────────────
def make_full_slide(slide: dict, idx: int, total: int,
                    title: str, series: str, theme: dict,
                    path: Path, is_first: bool = False):
    th  = theme
    img = Image.new("RGB", (W_FULL, H_FULL))
    px  = img.load()
    for y in range(H_FULL):
        c = lerp(th["bg_top"], th["bg_bot"], y / H_FULL)
        for x in range(W_FULL): px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0, 0), (W_FULL, 10)], fill=th["accent"])

    # Channel watermark
    draw.text((W_FULL - 40, 35), "HerooQuest",
              fill=(*[220, 220, 220], 180), font=get_font(FONT_BOLD_PATHS, 32), anchor="ra")
    draw.text((40, 35), f"Ep {idx}/{total}",
              fill=(*[220, 220, 220], 160), font=get_font(FONT_REG_PATHS, 28), anchor="la")

    if is_first:
        # FIRST FRAME — Heroo big + title
        # Load Heroo character — right side of frame
        heroo = load_heroo(int(H_FULL * 0.80))
        if heroo:
            hx = W_FULL - heroo.width - 60
            hy = H_FULL - heroo.height
            img.paste(heroo, (hx, hy), heroo)

        # Title left side
        f_series = get_font(FONT_BOLD_PATHS, 36)
        f_title  = get_font(FONT_BOLD_PATHS, 90)
        f_moral  = get_font(FONT_REG_PATHS,  42)

        draw.text((80, 120), series, fill=(*th["accent"], 220), font=f_series)

        title_lines = textwrap.wrap(title.upper(), width=16)
        ty = 200
        for line in title_lines[:3]:
            # Shadow
            for dx, dy in [(-3, 0), (3, 0), (0, 3)]:
                draw.text((80 + dx, ty + dy), line, font=f_title, fill=(0, 0, 0))
            draw.text((80, ty), line, font=f_title, fill=(255, 220, 0))
            ty += 100

        draw.rectangle([(80, ty + 20), (600, ty + 24)], fill=th["accent"])
        ty += 60

        content_lines = textwrap.wrap(slide.get("content", ""), width=35)
        for line in content_lines[:3]:
            draw.text((80, ty), line, fill=th["text"], font=f_moral)
            ty += 56

    else:
        # Regular slide
        title_font  = get_font(FONT_BOLD_PATHS, 64)
        title_lines = textwrap.wrap(slide.get("title","").upper(), width=35)
        ty = 120
        for line in title_lines[:2]:
            draw.text((W_FULL//2, ty), line, fill=th["accent"],
                      font=title_font, anchor="mm")
            ty += 78

        draw.rectangle([(80, ty + 10), (W_FULL - 80, ty + 14)], fill=th["accent"])
        ty += 50

        content_font  = get_font(FONT_REG_PATHS, 44)
        content_lines = textwrap.wrap(slide.get("content", ""), width=55)
        for line in content_lines[:7]:
            draw.text((80, ty), line, fill=th["text"], font=content_font)
            ty += 58

        # Sound cue badge
        sound = slide.get("sound_cue", "")
        if sound:
            draw.text((W_FULL - 40, H_FULL - 50), f"[{sound}]",
                      fill=(*th["accent"], 180), font=get_font(FONT_BOLD_PATHS, 28), anchor="ra")

    draw.rectangle([(0, H_FULL - 10), (W_FULL, H_FULL)], fill=th["accent"])
    img.save(str(path), quality=95)


# ─── FRAME RENDERER — SHORT (9:16) ───────────────────────────────────────────
def make_short_frame_kids(text_line1: str, text_line2: str,
                          theme: dict, path: Path, is_did_you_know: bool = False):
    th  = theme
    img = Image.new("RGB", (W_SHORT, H_SHORT))
    px  = img.load()
    for y in range(H_SHORT):
        c = lerp(th["bg_top"], th["bg_bot"], y / H_SHORT)
        for x in range(W_SHORT): px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0, 0), (W_SHORT, 10)], fill=th["accent"])

    # Load Heroo — bottom 60% of frame
    heroo = load_heroo(int(H_SHORT * 0.60))
    if heroo:
        hx = (W_SHORT - heroo.width) // 2
        hy = H_SHORT - heroo.height
        img.paste(heroo, (hx, hy), heroo)

    # Text — top portion
    if is_did_you_know:
        f_q = get_font(FONT_BOLD_PATHS, 80)
        f_a = get_font(FONT_BOLD_PATHS, 56)
        draw.text((W_SHORT//2, 120), "KYA TUM" if LANG == "hi" else "DID YOU",
                  font=f_q, fill=(255, 220, 0), anchor="mm")
        draw.text((W_SHORT//2, 210), "JAANTE HO?" if LANG == "hi" else "KNOW?",
                  font=f_q, fill=(255, 220, 0), anchor="mm")
        draw.rectangle([(60, 270), (W_SHORT - 60, 276)], fill=th["accent"])
        fact_lines = textwrap.wrap(text_line1, width=28)
        ty = 310
        for line in fact_lines[:4]:
            draw.text((W_SHORT//2, ty), line, font=f_a, fill=(255,255,255), anchor="mm")
            ty += 66
    else:
        f1 = get_font(FONT_BOLD_PATHS, 100)
        f2 = get_font(FONT_BOLD_PATHS, 60)
        # Shadow
        for dx, dy in [(-4,0),(4,0),(0,-4),(0,4)]:
            draw.text((W_SHORT//2+dx, 150+dy), text_line1,
                      font=f1, fill=(0,0,0), anchor="mm")
        draw.text((W_SHORT//2, 150), text_line1,
                  font=f1, fill=(255, 220, 0), anchor="mm")
        draw.rectangle([(80, 240), (W_SHORT - 80, 246)], fill=th["accent"])
        l2_lines = textwrap.wrap(text_line2, width=28)
        ty = 280
        for line in l2_lines[:3]:
            draw.text((W_SHORT//2, ty), line, font=f2, fill=(255,255,255), anchor="mm")
            ty += 70

    # Channel tag bottom
    draw.text((W_SHORT//2, H_SHORT - 80), "HerooQuest",
              fill=(*th["accent"], 220), font=get_font(FONT_BOLD_PATHS, 48), anchor="mm")
    draw.rectangle([(0, H_SHORT - 10), (W_SHORT, H_SHORT)], fill=th["accent"])
    img.save(str(path), quality=95)


# ─── VOICE ────────────────────────────────────────────────────────────────────
async def gen_voice(text: str, path: Path, is_short: bool = False):
    tts_speed = ht.get_tts_speed()
    rate_pct  = int((tts_speed - 1.0) * 100)
    if is_short: rate_pct += 3   # slightly faster for shorts
    rate_str  = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
    await edge_tts.Communicate(text, VOICE, rate=rate_str).save(str(path))


# ─── YOUTUBE UPLOAD ───────────────────────────────────────────────────────────
def get_youtube_service():
    try:
        creds_key  = "YOUTUBE_CREDENTIALS_KIDS_EN" if LANG == "en" else "YOUTUBE_CREDENTIALS_KIDS"
        creds_json = os.environ.get(creds_key)
        if not creds_json:
            creds_json = os.environ.get("YOUTUBE_CREDENTIALS_KIDS")
        if not creds_json: return None
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        return build("youtube", "v3", credentials=creds)
    except Exception:
        return None

def upload_video(video_path: Path, title: str, description: str,
                 tags: list, is_short: bool = False, is_kids: bool = True):
    youtube = get_youtube_service()
    if not youtube:
        print(f"❌ YouTube Kids unavailable [{LANG}] — skipping")
        return None
    body = {
        "snippet": {
            "title":       title[:100],
            "description": description,
            "tags":        tags[:30],
            "categoryId":  "20"   # Gaming/Kids — best for kids animation
        },
        "status": {
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": is_kids
        }
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    vtype = "Short" if is_short else "Video"
    print(f"🚀 Uploading Kids {vtype} [{LANG.upper()}]: {title[:55]}...")
    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status: print(f"  {int(status.progress() * 100)}%")
        vid_id = response["id"]
        url = f"https://youtube.com/shorts/{vid_id}" if is_short else f"https://youtube.com/watch?v={vid_id}"
        print(f"✅ Uploaded: {url}")
        return vid_id
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None


# ─── MAIN ─────────────────────────────────────────────────────────────────────
async def run():
    today_str = datetime.now().strftime("%d %b %Y")
    today_fn  = datetime.now().strftime("%Y%m%d")

    story_info = get_story_week()
    week, series, ep, title_hi, title_en, moral = story_info
    title      = title_hi if LANG == "hi" else title_en
    theme      = get_theme(week)
    fact_data  = get_did_you_know()

    print(f"📖 Story: {series} — Ep {ep}: {title} | Moral: {moral}")

    # ── Generate story script ─────────────────────────────────────────────────
    story_data = generate_full_story(story_info)
    slides     = story_data.get("slides", [])

    # ── Full video ────────────────────────────────────────────────────────────
    if OUTPUT_TYPE in ("full", "all"):
        clips = []
        for i, s in enumerate(slides):
            img_path   = OUT / f"kids_full_{LANG}_{i}.png"
            audio_path = OUT / f"kids_full_{LANG}_{i}.mp3"

            make_full_slide(s, i+1, len(slides), title, series,
                            theme, img_path, is_first=(i == 0))
            await gen_voice(s.get("content", ""), audio_path)

            vc       = AudioFileClip(str(audio_path))
            duration = vc.duration + 1.0
            clip     = ImageClip(str(img_path)).set_duration(duration).set_audio(vc)
            clips.append(clip)

        video_path = OUT / f"kids_full_{LANG}_{today_fn}.mp4"
        concatenate_videoclips(clips, method="compose").write_videofile(
            str(video_path), fps=FPS, codec="libx264", audio_codec="aac",
            remove_temp=True, logger=None
        )
        total_dur = sum(c.duration for c in clips)
        print(f"✅ Full video [{LANG.upper()}]: {total_dur/60:.1f} min")

        tags    = seo.get_video_tags(mode="weekend", is_short=False)
        tags   += ["KidsStories", "HerooQuest", "KidsYoutube", "StoriesForKids",
                   "HindiKidsStories", "MoralStories", "BedtimeStories"]
        desc    = (
            f"🦸 {story_data.get('video_description','')}\n\n"
            f"✨ Moral: {moral}\n\n"
            f"📺 Series: {series} | Episode {ep}\n"
            f"👶 For kids aged 6-14\n\n"
            f"#HerooQuest #KidsStories #MoralStories"
        )
        vid_id = upload_video(video_path, story_data.get("video_title", f"Heroo: {title}"),
                              desc, [t for t in tags if t.isascii()], is_short=False)

    # ── Story cliffhanger short ───────────────────────────────────────────────
    if OUTPUT_TYPE in ("short", "all"):
        short_script = generate_short_script_kids(story_data, story_info)
        short_img    = OUT / f"kids_short_{LANG}_{today_fn}.png"
        short_audio  = OUT / f"kids_short_{LANG}_{today_fn}.mp3"

        make_short_frame_kids(
            title.upper()[:12],
            story_data.get("cliffhanger", "Kya hua aage? 😱")[:50],
            theme, short_img, is_did_you_know=False
        )
        await gen_voice(short_script, short_audio, is_short=True)

        vc_short   = AudioFileClip(str(short_audio))
        dur_short  = min(vc_short.duration + 0.3, 59.0)
        clip_short = ImageClip(str(short_img)).set_duration(dur_short).set_audio(vc_short)

        short_path = OUT / f"kids_short_{LANG}_{today_fn}.mp4"
        clip_short.write_videofile(
            str(short_path), fps=30, codec="libx264", audio_codec="aac",
            remove_temp=True, logger=None
        )
        print(f"✅ Cliffhanger Short [{LANG.upper()}]: {dur_short:.1f}s")

        short_title = f"Heroo: {title} 😱 Kya hua? | HerooQuest #Shorts"[:100]
        upload_video(short_path, short_title,
                     f"Watch full story! 👆\n{moral}\n#HerooQuest #KidsShorts",
                     ["HerooQuest","KidsShorts","Shorts"], is_short=True)

    # ── Did You Know short ────────────────────────────────────────────────────
    if OUTPUT_TYPE in ("didyouknow", "all"):
        dyk_topic, dyk_fact_hi, dyk_fact_en = fact_data
        dyk_fact   = dyk_fact_hi if LANG == "hi" else dyk_fact_en
        dyk_script = generate_did_you_know_script(fact_data)
        dyk_img    = OUT / f"kids_dyk_{LANG}_{today_fn}.png"
        dyk_audio  = OUT / f"kids_dyk_{LANG}_{today_fn}.mp3"

        make_short_frame_kids(
            dyk_fact[:40], "", theme, dyk_img, is_did_you_know=True
        )
        await gen_voice(dyk_script, dyk_audio, is_short=True)

        vc_dyk   = AudioFileClip(str(dyk_audio))
        dur_dyk  = min(vc_dyk.duration + 0.3, 59.0)
        clip_dyk = ImageClip(str(dyk_img)).set_duration(dur_dyk).set_audio(vc_dyk)

        dyk_path = OUT / f"kids_dyk_{LANG}_{today_fn}.mp4"
        clip_dyk.write_videofile(
            str(dyk_path), fps=30, codec="libx264", audio_codec="aac",
            remove_temp=True, logger=None
        )
        print(f"✅ Did You Know Short [{LANG.upper()}]: {dur_dyk:.1f}s")

        if LANG == "hi":
            dyk_title = f"Kya Tum Jaante Ho? {dyk_topic} 🤔 | HerooQuest #Shorts"[:100]
        else:
            dyk_title = f"Did You Know? {dyk_topic} 🤔 | HerooQuest #Shorts"[:100]

        upload_video(dyk_path, dyk_title,
                     f"Amazing fact about {dyk_topic}!\n#HerooQuest #DidYouKnow #KidsFacts",
                     ["HerooQuest","DidYouKnow","KidsFacts","Shorts"], is_short=True)

    # ── Save meta ─────────────────────────────────────────────────────────────
    meta = {
        "series":       series,
        "episode":      ep,
        "title":        title,
        "moral":        moral,
        "lang":         LANG,
        "output_type":  OUTPUT_TYPE,
        "date":         today_str,
    }
    meta_path = OUT / f"kids_meta_{today_fn}_{LANG}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 Saved: {meta_path.name}")

    print(f"\n{'='*60}")
    print(f"✅ HEROOQUEST DONE — {title} | {LANG.upper()} | {today_str}")
    print(f"   Series  : {series} Ep {ep}")
    print(f"   Moral   : {moral}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(run())
