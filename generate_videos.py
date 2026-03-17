import os
import sys
import json
import asyncio
import random
import textwrap
from datetime import datetime
from groq import Groq
from PIL import Image, ImageDraw, ImageFont, ImageOps
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# ─────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

IMG_W, IMG_H = 1280, 720

# Font paths — tries multiple locations so it works locally & on Ubuntu CI
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
]
FONT_BODY_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
]

def find_font(candidates, size):
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    print("⚠️  No system font found, using PIL default.")
    return ImageFont.load_default()

# ─────────────────────────────────────────────────
# YOUTUBE — loads token.json from env secret
# ─────────────────────────────────────────────────
def upload_to_youtube(video_path: str, title: str):
    """
    Expects the GitHub secret YOUTUBE_CREDENTIALS to contain the
    full JSON content of token.json (OAuth2 refresh token).
    The workflow writes it to token.json before running this script.
    """
    token_path = "token.json"
    if not os.path.exists(token_path):
        print("❌ token.json not found — skipping YouTube upload.")
        return

    try:
        creds = Credentials.from_authorized_user_file(token_path)
        youtube = build("youtube", "v3", credentials=creds)

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": (
                        "📊 Daily AI-powered Nifty Technical Analysis.\n"
                        "Powered by AI360Trading | #Nifty #StockMarket #TechnicalAnalysis"
                    ),
                    "tags": ["Nifty", "Technical Analysis", "Stock Market", "AI Trading"],
                    "categoryId": "27",          # Education
                    "defaultLanguage": "en",
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                },
            },
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True),
        )
        response = request.execute()
        print(f"\n✅ VIDEO LIVE: https://www.youtube.com/watch?v={response['id']}\n")
    except Exception as e:
        print(f"❌ YouTube Upload Error: {e}")
        raise


# ─────────────────────────────────────────────────
# SLIDE RENDERER — no external images required
# ─────────────────────────────────────────────────

# Gradient palettes: (top_color, bottom_color, accent)
BULLISH_PALETTES = [
    ((10, 30, 20),  (5, 55, 35),   (0, 220, 110)),
    ((8, 25, 45),   (5, 50, 30),   (50, 200, 80)),
    ((15, 40, 15),  (10, 60, 40),  (20, 240, 120)),
]
BEARISH_PALETTES = [
    ((45, 10, 10),  (80, 20, 20),  (255, 80, 60)),
    ((30, 15, 5),   (70, 30, 10),  (255, 120, 40)),
    ((40, 5, 25),   (80, 15, 35),  (240, 60, 100)),
]
NEUTRAL_PALETTES = [
    ((10, 15, 40),  (20, 30, 70),  (80, 140, 255)),
    ((5, 20, 45),   (15, 35, 75),  (100, 160, 255)),
]

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def make_gradient_bg(top_color, bottom_color):
    img = Image.new("RGB", (IMG_W, IMG_H))
    for y in range(IMG_H):
        t = y / IMG_H
        color = lerp_color(top_color, bottom_color, t)
        ImageDraw.Draw(img).line([(0, y), (IMG_W, y)], fill=color)
    return img

def draw_grid_overlay(draw):
    """Subtle grid lines for a professional chart-like look."""
    grid_color = (255, 255, 255, 18)
    for x in range(0, IMG_W, 80):
        draw.line([(x, 0), (x, IMG_H)], fill=(255, 255, 255, 18))
    for y in range(0, IMG_H, 60):
        draw.line([(0, y), (IMG_W, y)], fill=(255, 255, 255, 18))

def draw_accent_bar(draw, accent_color, slide_num, total):
    """Top accent bar with progress indicator."""
    bar_h = 6
    draw.rectangle([(0, 0), (IMG_W, bar_h)], fill=accent_color)
    progress = int(IMG_W * slide_num / total)
    draw.rectangle([(0, 0), (progress, bar_h)], fill=(255, 255, 255))

def draw_slide_number(draw, slide_num, total, font):
    text = f"{slide_num} / {total}"
    draw.text((IMG_W - 80, IMG_H - 45), text, fill=(200, 200, 200), font=font)

def draw_watermark(draw, font):
    draw.text((30, IMG_H - 45), "AI360Trading", fill=(180, 180, 180), font=font)

def draw_sentiment_badge(draw, sentiment, accent, font_small):
    labels = {"bullish": ("▲ BULLISH", (0, 200, 100)), "bearish": ("▼ BEARISH", (255, 80, 60))}
    label, color = labels.get(sentiment.lower(), ("◆ NEUTRAL", (100, 160, 255)))
    bw, bh = 140, 36
    bx, by = IMG_W - bw - 30, 24
    draw.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=8, fill=color)
    draw.text((bx + bw // 2, by + bh // 2), label, fill=(0, 0, 0), font=font_small, anchor="mm")

def make_pro_slide(slide: dict, idx: int, total: int, path: str):
    sentiment = slide.get("sentiment", "neutral").lower()
    if sentiment == "bullish":
        pal = random.choice(BULLISH_PALETTES)
    elif sentiment == "bearish":
        pal = random.choice(BEARISH_PALETTES)
    else:
        pal = random.choice(NEUTRAL_PALETTES)

    top_c, bot_c, accent = pal
    img = make_gradient_bg(top_c, bot_c)

    # Draw semi-transparent overlay for better text contrast
    overlay = Image.new("RGBA", (IMG_W, IMG_H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    # Left panel: darker for text readability
    ov_draw.rectangle([(0, 0), (840, IMG_H)], fill=(0, 0, 0, 120))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(img)
    draw_grid_overlay(draw)
    draw_accent_bar(draw, accent, idx, total)

    f_title  = find_font(FONT_CANDIDATES,      54)
    f_body   = find_font(FONT_BODY_CANDIDATES, 30)
    f_small  = find_font(FONT_BODY_CANDIDATES, 22)
    f_num    = find_font(FONT_BODY_CANDIDATES, 20)

    # Slide number pill
    num_text = f"SLIDE {idx}"
    draw.text((50, 38), num_text, fill=accent, font=f_small)

    # Title — word-wrap at ~28 chars
    title_lines = textwrap.wrap(slide["title"].upper(), width=28)
    ty = 90
    for line in title_lines[:2]:
        draw.text((50, ty), line, fill=(255, 255, 255), font=f_title)
        ty += 68

    # Divider
    draw.rectangle([(50, ty + 8), (50 + 400, ty + 12)], fill=accent)
    ty += 30

    # Body — word-wrap at ~55 chars, max 10 lines
    body_lines = textwrap.wrap(slide["content"], width=55)
    for line in body_lines[:10]:
        draw.text((50, ty), line, fill=(230, 230, 230), font=f_body)
        ty += 46

    draw_sentiment_badge(draw, sentiment, accent, f_small)
    draw_slide_number(draw, idx, total, f_num)
    draw_watermark(draw, f_num)

    img.save(path)


# ─────────────────────────────────────────────────
# INTRO SLIDE (branding)
# ─────────────────────────────────────────────────
def make_intro_slide(path: str):
    img = make_gradient_bg((5, 10, 30), (10, 25, 60))
    draw = ImageDraw.Draw(img)
    f_big   = find_font(FONT_CANDIDATES,      72)
    f_mid   = find_font(FONT_BODY_CANDIDATES, 38)
    f_small = find_font(FONT_BODY_CANDIDATES, 26)

    draw.rectangle([(0, 0), (IMG_W, 8)], fill=(0, 200, 110))

    title = "AI360Trading"
    subtitle = "Daily NIFTY Technical Analysis"
    date_str = datetime.now().strftime("%A, %d %B %Y")

    # Centre text vertically
    draw.text((IMG_W // 2, 220), title,    fill=(0, 220, 120), font=f_big,   anchor="mm")
    draw.text((IMG_W // 2, 330), subtitle, fill=(255, 255, 255), font=f_mid,  anchor="mm")
    draw.rectangle([(440, 370), (840, 374)], fill=(0, 200, 110))
    draw.text((IMG_W // 2, 420), date_str, fill=(180, 220, 255), font=f_small, anchor="mm")
    draw.text((IMG_W // 2, 600), "Powered by AI  •  Not Financial Advice",
              fill=(120, 120, 140), font=f_small, anchor="mm")
    img.save(path)


# ─────────────────────────────────────────────────
# OUTRO SLIDE
# ─────────────────────────────────────────────────
def make_outro_slide(path: str):
    img = make_gradient_bg((5, 10, 30), (10, 25, 60))
    draw = ImageDraw.Draw(img)
    f_big   = find_font(FONT_CANDIDATES,      60)
    f_mid   = find_font(FONT_BODY_CANDIDATES, 34)
    f_small = find_font(FONT_BODY_CANDIDATES, 26)

    draw.rectangle([(0, 0), (IMG_W, 8)], fill=(0, 200, 110))
    draw.text((IMG_W // 2, 240), "Like  •  Subscribe  •  Share",
              fill=(0, 220, 120), font=f_big, anchor="mm")
    draw.text((IMG_W // 2, 360), "For daily market analysis powered by AI",
              fill=(255, 255, 255), font=f_mid, anchor="mm")
    draw.text((IMG_W // 2, 460), "AI360Trading  |  #Nifty #StockMarket",
              fill=(150, 180, 220), font=f_small, anchor="mm")
    draw.text((IMG_W // 2, 600), "Disclaimer: Educational only. Not financial advice.",
              fill=(120, 120, 140), font=f_small, anchor="mm")
    img.save(path)


# ─────────────────────────────────────────────────
# MAIN ENGINE
# ─────────────────────────────────────────────────
PROMPT = """You are an expert Indian stock market technical analyst.
Create a 16-slide JSON for a YouTube video about today's NIFTY 50 technical analysis.

Requirements:
- Slide 1: Market Overview & Opening Summary
- Slides 2-3: Key Support & Resistance Levels
- Slide 4: Moving Averages (20, 50, 200 EMA)
- Slide 5: RSI & Momentum Analysis
- Slide 6: MACD Signal
- Slide 7: Bollinger Bands
- Slide 8: Volume Analysis
- Slide 9: FII/DII Activity
- Slide 10: Global Cues (SGX Nifty, Dow, Nasdaq)
- Slide 11: Sector Rotation
- Slide 12: Option Chain Analysis (PCR, Max Pain)
- Slide 13: Intraday Trade Setup
- Slide 14: Positional Trade Setup
- Slide 15: Risk Management
- Slide 16: Conclusion & Outlook

Each slide MUST have:
- "title": concise title (max 6 words)
- "content": exactly 6 sentences of detailed analysis with specific numbers/levels
- "sentiment": one of "bullish", "bearish", or "neutral"

Respond ONLY with valid JSON: {"slides": [...]}"""


async def generate_tts(text: str, voice: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


async def run_bot():
    # ── 1. Generate script via Groq ──────────────────
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        print("❌ GROQ_API_KEY not set.")
        sys.exit(1)

    client = Groq(api_key=groq_key)
    print("🤖 Generating market analysis script...")

    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": PROMPT}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=4000,
        )
        slides = json.loads(chat.choices[0].message.content)["slides"]
        print(f"✅ Generated {len(slides)} slides.")
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        sys.exit(1)

    total_slides = len(slides)

    # ── 2. Intro slide ───────────────────────────────
    intro_img = f"{OUTPUT_DIR}/intro.png"
    intro_aud = f"{OUTPUT_DIR}/intro.mp3"
    make_intro_slide(intro_img)

    intro_text = (
        f"Welcome to AI360Trading. Today is {datetime.now().strftime('%A, %d %B %Y')}. "
        "In this video, we bring you a comprehensive technical analysis of the Nifty 50 index, "
        "powered by artificial intelligence. Stay tuned for detailed support and resistance levels, "
        "momentum indicators, and trade setups for today's session."
    )
    await generate_tts(intro_text, "en-IN-PrabhatNeural", intro_aud)
    intro_audio = AudioFileClip(intro_aud)
    clips = [ImageClip(intro_img).set_duration(max(intro_audio.duration + 1, 12)).set_audio(intro_audio)]

    # ── 3. Content slides ────────────────────────────
    # Alternate between two voices for variety
    voices = ["en-IN-PrabhatNeural", "en-IN-NeerjaNeural"]
    print("🎬 Rendering slides...")

    for i, slide in enumerate(slides):
        img_p = f"{OUTPUT_DIR}/slide_{i:02d}.png"
        aud_p = f"{OUTPUT_DIR}/slide_{i:02d}.mp3"

        make_pro_slide(slide, i + 1, total_slides, img_p)

        voice = voices[i % 2]
        tts_text = f"{slide['title']}. {slide['content']}"
        await generate_tts(tts_text, voice, aud_p)

        audio = AudioFileClip(aud_p)
        # Each slide: audio duration + 1.5s buffer, minimum 30s for 10-min target
        duration = max(audio.duration + 1.5, 30)
        clips.append(ImageClip(img_p).set_duration(duration).set_audio(audio))
        print(f"  ✓ Slide {i+1}/{total_slides} — {duration:.1f}s")

    # ── 4. Outro slide ───────────────────────────────
    outro_img = f"{OUTPUT_DIR}/outro.png"
    outro_aud = f"{OUTPUT_DIR}/outro.mp3"
    make_outro_slide(outro_img)

    outro_text = (
        "Thank you for watching AI360Trading. If you found this analysis helpful, "
        "please like, subscribe, and hit the notification bell so you never miss our daily updates. "
        "Remember, this video is for educational purposes only and does not constitute financial advice. "
        "Trade wisely and manage your risk. See you tomorrow!"
    )
    await generate_tts(outro_text, "en-IN-PrabhatNeural", outro_aud)
    outro_audio = AudioFileClip(outro_aud)
    clips.append(ImageClip(outro_img).set_duration(max(outro_audio.duration + 2, 20)).set_audio(outro_audio))

    # ── 5. Render final video ────────────────────────
    final_path = f"{OUTPUT_DIR}/final_video.mp4"
    total_duration = sum(c.duration for c in clips)
    print(f"🎥 Rendering video — {len(clips)} clips, ~{total_duration/60:.1f} minutes...")

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        final_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        bitrate="2000k",
        logger=None,
    )
    print(f"✅ Video saved: {final_path} ({os.path.getsize(final_path) / 1e6:.1f} MB)")

    # ── 6. Upload ────────────────────────────────────
    title = f"NIFTY Technical Analysis | {datetime.now().strftime('%d %b %Y')} | AI360Trading"
    upload_to_youtube(final_path, title)


if __name__ == "__main__":
    asyncio.run(run_bot())
