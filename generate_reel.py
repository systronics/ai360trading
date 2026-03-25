import os
import sys
import json
import asyncio
import random
from datetime import datetime
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip,
    concatenate_videoclips, VideoFileClip
)
from groq import Groq

# ─── CONFIG ──────────────────────────────────────────────────────────────────
W, H       = 1080, 1920
FPS        = 24
OUT        = Path("output")
IMG_DIR    = Path("public/image")
MUSIC_DIR  = Path("public/music")
VOICE      = "hi-IN-SwaraNeural"   # Female voice — sounds like kid when reading Hinglish
TARGET_DUR = 60                    # Target ~60 seconds

os.makedirs(OUT, exist_ok=True)

# ─── COLORS ──────────────────────────────────────────────────────────────────
COLORS = {
    "bg_dark":      (8, 8, 24),
    "bg_mid":       (15, 15, 45),
    "gold":         (255, 200, 50),
    "white":        (255, 255, 255),
    "soft_white":   (230, 230, 255),
    "black":        (0, 0, 0),
    "green":        (50, 220, 100),
    "red":          (220, 60, 60),
    "purple":       (140, 80, 220),
    "orange":       (255, 140, 30),
}

SENTIMENT_COLORS = {
    "positive":  COLORS["green"],
    "negative":  COLORS["red"],
    "neutral":   COLORS["gold"],
    "fearful":   COLORS["orange"],
    "motivated": COLORS["purple"],
}

# ─── ZENO EMOTION MAP ────────────────────────────────────────────────────────
EMOTION_ARC = {
    "positive":  ["zeno_happy",       "zeno_thinking",     "zeno_celebrating"],
    "negative":  ["zeno_sad",         "zeno_thinking",     "zeno_celebrating"],
    "fearful":   ["zeno_fear",        "zeno_thinking",     "zeno_celebrating"],
    "motivated": ["zeno_celebrating", "zeno_happy",        "zeno_celebrating"],
    "greedy":    ["zeno_greed",       "zeno_thinking",     "zeno_celebrating"],
    "angry":     ["zeno_angry",       "zeno_thinking",     "zeno_celebrating"],
    "neutral":   ["zeno_thinking",    "zeno_happy",        "zeno_celebrating"],
}

KEN_BURNS = ["zoom_in", "pan_left", "zoom_out"]  # one per segment

# ─── BACKGROUND MUSIC ROTATION ───────────────────────────────────────────────
def get_bg_music() -> Path | None:
    """Day-based rotation: Mon=1, Tue=2, Wed=3, Thu=1, Fri=2, Sat=3, Sun=1"""
    day = datetime.now().weekday()  # 0=Mon, 6=Sun
    music_map = {0: "bgmusic1.mp3", 1: "bgmusic2.mp3", 2: "bgmusic3.mp3",
                 3: "bgmusic1.mp3", 4: "bgmusic2.mp3", 5: "bgmusic3.mp3", 6: "bgmusic1.mp3"}
    music_file = MUSIC_DIR / music_map[day]
    if music_file.exists():
        print(f"🎵 Background music: {music_file.name}")
        return music_file
    # Fallback: try any music file
    for f in MUSIC_DIR.glob("*.mp3"):
        print(f"🎵 Fallback music: {f.name}")
        return f
    print("⚠️ No background music found — continuing without music.")
    return None

# ─── WEEKEND DETECTION ───────────────────────────────────────────────────────
def is_weekend() -> bool:
    return datetime.now().weekday() >= 5

# ─── GROQ SCRIPT GENERATION ──────────────────────────────────────────────────
def generate_script(client: Groq) -> dict:
    """
    Generates a Hinglish trading reel script using Groq.
    Returns dict with: title, hook, lesson, cta, description, sentiment, hashtags
    """
    today = datetime.now().strftime("%A, %d %B %Y")
    weekend = is_weekend()

    if weekend:
        topic_hint = "emotional life lesson related to money, patience, or personal growth"
    else:
        topic_hint = "stock market education, trading psychology, or market sentiment for Indian traders"

    prompt = f"""You are ZENO — a wise, friendly animated kid character who teaches trading wisdom in Hinglish (mix of Hindi and English) to Indian traders of all ages, including kids.

Today is {today}. Create a 60-second Hinglish reel script on: {topic_hint}

Rules:
- Hinglish only (natural Hindi + English mix, like "Yaar, market ne aaj phir surprise kiya!")
- Hook must grab attention in first 3 seconds
- Teach one clear lesson — simple enough for a 10-year-old
- End with strong CTA to follow/like
- Sentiment must be one of: positive, negative, fearful, motivated, greedy, angry, neutral
- Total spoken content: 120-140 words (fits ~60 seconds)

Respond ONLY with valid JSON, no markdown, no extra text:
{{
  "title": "catchy Hinglish title max 8 words",
  "hook": "opening 1-2 sentences (grab attention, 15-20 words)",
  "lesson": "main teaching content (80-90 words, clear and simple)",
  "cta": "closing call to action (15-20 words)",
  "description": "YouTube/Instagram description 2-3 sentences in Hinglish with lesson summary",
  "sentiment": "one of: positive/negative/fearful/motivated/greedy/angry/neutral",
  "hashtags": "#ZenoKiBaat #ai360trading #StockMarketIndia #TradingWisdom #Hinglish #FinancialLiteracy #Nifty50 #ReelsIndia #TradingPsychology #MoneyMindset"
}}"""

    print("🤖 Generating Hinglish script via Groq...")
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.85,
            max_tokens=600
        )
        data = json.loads(resp.choices[0].message.content)
        print(f"✅ Script ready — sentiment: {data.get('sentiment', 'neutral')}")
        print(f"   Title: {data.get('title', '')}")
        return data
    except Exception as e:
        print(f"⚠️ Groq error: {e} — using fallback script")
        return {
            "title": "Market Ki Sachchi Baat",
            "hook": "Yaar, kya tumhe pata hai ki sabse bada trading mistake kya hai?",
            "lesson": "Bahut log market mein paisa lagate hain bina plan ke. Woh sochte hain — 'aaj profit hoga' — lekin bina strategy ke? Sirf luck pe depend rehna dangerous hai. ZENO kehta hai: pehle seekho, phir lagao. Ek achha trader woh hota hai jo loss se bhi seekhta hai. Patience rakho, discipline rakho — success zaroor milegi!",
            "cta": "Agar yeh baat helpful lagi, toh like karo aur follow karo ai360trading!",
            "description": "ZENO ki baat: Trading mein patience aur discipline sabse zaroori hai. Bina plan ke investment mat karo.",
            "sentiment": "motivated",
            "hashtags": "#ZenoKiBaat #ai360trading #StockMarketIndia #TradingWisdom #Hinglish"
        }

# ─── FONT HELPER ─────────────────────────────────────────────────────────────
def get_font(size: int):
    """Load font with multiple fallbacks."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()

# ─── DRAW TEXT WITH OUTLINE ───────────────────────────────────────────────────
def draw_text_outlined(draw, text, x, y, font, fill, outline_width=3, anchor="mm"):
    """Draws text with black outline for readability on any background."""
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=COLORS["black"], anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)

# ─── WRAP TEXT ───────────────────────────────────────────────────────────────
def wrap_text(text: str, font, max_width: int) -> list[str]:
    """Wraps text to fit within max_width pixels."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

# ─── BUILD ONE FRAME (PIL Image) ──────────────────────────────────────────────
def build_frame(slide: dict, zeno_emotion: str, sentiment: str, segment: int) -> Image.Image:
    """
    Builds a single 1080x1920 frame.
    segment 0 = hook, 1 = lesson, 2 = cta
    """
    img = Image.new("RGB", (W, H), COLORS["bg_dark"])
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Gradient background ──
    for y in range(H):
        ratio = y / H
        r = int(COLORS["bg_dark"][0] + (COLORS["bg_mid"][0] - COLORS["bg_dark"][0]) * ratio)
        g = int(COLORS["bg_dark"][1] + (COLORS["bg_mid"][1] - COLORS["bg_dark"][1]) * ratio)
        b = int(COLORS["bg_dark"][2] + (COLORS["bg_mid"][2] - COLORS["bg_dark"][2]) * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # ── Top bar with sentiment color ──
    sent_color = SENTIMENT_COLORS.get(sentiment, COLORS["gold"])
    draw.rectangle([(0, 0), (W, 8)], fill=sent_color)

    # ── Logo / brand tag ──
    font_brand = get_font(36)
    draw_text_outlined(draw, "✨ ai360trading.in", W // 2, 55, font_brand, COLORS["gold"], outline_width=2)

    # ── Title ──
    font_title = get_font(68)
    title = slide.get("title", "ZENO Ki Baat").upper()
    title_lines = wrap_text(title, font_title, W - 80)
    title_y = 130
    for line in title_lines[:2]:
        draw_text_outlined(draw, line, W // 2, title_y, font_title, COLORS["white"], outline_width=3)
        title_y += 80

    # ── Sentiment badge ──
    font_badge = get_font(38)
    badge_text = f"● {sentiment.upper()}"
    draw_text_outlined(draw, badge_text, W // 2, title_y + 20, font_badge, sent_color, outline_width=2)

    # ── ZENO character (dominates center-bottom) ──
    zeno_file = IMG_DIR / f"{zeno_emotion}.png"
    if not zeno_file.exists():
        zeno_file = IMG_DIR / "zeno_happy.png"
    if zeno_file.exists():
        try:
            zeno = Image.open(zeno_file).convert("RGBA")
            zeno_size = 820
            zeno.thumbnail((zeno_size, zeno_size), Image.LANCZOS)
            zeno_x = (W - zeno.width) // 2
            zeno_y = H - zeno.height - 220
            img.paste(zeno, (zeno_x, zeno_y), zeno)
        except Exception as e:
            print(f"⚠️ ZENO image error: {e}")

    # ── Bottom content text (subtitle style) ──
    # Semi-transparent dark bar at bottom
    bar_top = H - 210
    draw.rectangle([(0, bar_top), (W, H)], fill=(0, 0, 0, 180))

    font_sub = get_font(46)
    content_texts = {
        0: slide.get("hook", ""),
        1: slide.get("lesson", ""),
        2: slide.get("cta", ""),
    }
    content = content_texts.get(segment, "")
    # Show first 2 lines of content in subtitle bar
    sub_lines = wrap_text(content, font_sub, W - 80)
    sub_y = bar_top + 35
    for line in sub_lines[:3]:
        draw_text_outlined(draw, line, W // 2, sub_y, font_sub, COLORS["white"], outline_width=3)
        sub_y += 58

    # ── Bottom strip ──
    draw.rectangle([(0, H - 8), (W, H)], fill=sent_color)

    return img

# ─── KEN BURNS EFFECT ────────────────────────────────────────────────────────
def apply_ken_burns(img: Image.Image, duration: float, effect: str) -> ImageClip:
    """
    Applies Ken Burns zoom/pan effect to a PIL image.
    Returns a moviepy ImageClip with the animation.
    """
    frames_count = int(duration * FPS)
    frames = []

    img_w, img_h = img.size

    for i in range(frames_count):
        t = i / max(frames_count - 1, 1)  # 0.0 to 1.0

        if effect == "zoom_in":
            scale = 1.0 + 0.08 * t
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            resized = img.resize((new_w, new_h), Image.LANCZOS)
            x = (new_w - img_w) // 2
            y = (new_h - img_h) // 2
            frame = resized.crop((x, y, x + img_w, y + img_h))

        elif effect == "zoom_out":
            scale = 1.08 - 0.08 * t
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            resized = img.resize((new_w, new_h), Image.LANCZOS)
            x = (new_w - img_w) // 2
            y = (new_h - img_h) // 2
            frame = resized.crop((x, y, x + img_w, y + img_h))

        elif effect == "pan_left":
            pan_range = int(img_w * 0.05)
            offset_x = int(pan_range * t)
            frame = img.crop((offset_x, 0, offset_x + img_w - pan_range, img_h))
            frame = frame.resize((img_w, img_h), Image.LANCZOS)

        else:
            frame = img.copy()

        frames.append(frame)

    # Save frames as temp video via ImageClip sequence
    # Use make_frame approach for efficiency
    import numpy as np
    frames_np = [np.array(f.convert("RGB")) for f in frames]

    def make_frame(t_sec):
        idx = min(int(t_sec * FPS), len(frames_np) - 1)
        return frames_np[idx]

    clip = ImageClip(frames_np[0]).set_duration(duration)
    clip = clip.fl(lambda gf, t: make_frame(t), apply_to=['mask'])

    # Better approach: use VideoClip with make_frame
    from moviepy.editor import VideoClip
    clip = VideoClip(make_frame, duration=duration)
    return clip

# ─── GENERATE VOICE ──────────────────────────────────────────────────────────
async def generate_voice(text: str, out_path: str):
    """Generates Hinglish voice using edge-tts."""
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(out_path)
    print(f"🎤 Voice saved: {out_path}")

# ─── SAVE META ───────────────────────────────────────────────────────────────
def save_meta(slide: dict, today: str):
    """Saves metadata JSON for upload_youtube, upload_facebook, upload_instagram."""
    meta = {
        "title": f"ZENO Ki Baat - {today} #Shorts",
        "description": slide.get("description", "Daily trading wisdom by ZENO. Follow @ai360trading"),
        "sentiment": slide.get("sentiment", "neutral"),
        "hashtags": slide.get("hashtags", "#ZenoKiBaat #ai360trading"),
        "hook": slide.get("hook", ""),
        "lesson": slide.get("lesson", ""),
        "cta": slide.get("cta", ""),
        "public_video_url": ""  # Placeholder — fill if hosting video publicly
    }
    meta_path = OUT / f"meta_{today}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Meta saved: {meta_path}")
    return meta

# ─── MAIN ────────────────────────────────────────────────────────────────────
async def run_reel():
    today = datetime.now().strftime("%Y%m%d")
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # 1. Generate script
    slide = generate_script(client)
    sentiment = slide.get("sentiment", "neutral")

    # 2. Save metadata (fixes Facebook + Instagram upload scripts)
    save_meta(slide, today)

    # 3. Select ZENO emotion arc (3 images)
    arc = EMOTION_ARC.get(sentiment, EMOTION_ARC["neutral"])
    print(f"🎭 ZENO arc: {arc[0]} → {arc[1]} → {arc[2]}")

    # 4. Build 3 frames (hook, lesson, cta)
    segments = ["hook", "lesson", "cta"]
    frame_paths = []
    for i, (seg, zeno_emotion) in enumerate(zip(segments, arc)):
        img = build_frame(slide, zeno_emotion, sentiment, i)
        path = str(OUT / f"frame_{i}.png")
        img.save(path)
        frame_paths.append(path)
        print(f"🖼️  Frame {i+1}/3 built — {zeno_emotion}")

    # 5. Generate voice for each segment
    voice_paths = []
    texts = [slide.get("hook", ""), slide.get("lesson", ""), slide.get("cta", "")]
    full_script = " ".join(t for t in texts if t)

    # Generate one continuous voice file for natural flow
    voice_path = str(OUT / f"voice_{today}.mp3")
    await generate_voice(full_script, voice_path)
    voice_clip = AudioFileClip(voice_path)
    total_duration = voice_clip.duration + 0.5

    # 6. Split duration across 3 segments (hook:20%, lesson:60%, cta:20%)
    seg_durations = [
        total_duration * 0.20,
        total_duration * 0.60,
        total_duration * 0.20,
    ]

    # 7. Build Ken Burns clips for each segment
    print("🎬 Building Ken Burns segments...")
    video_segments = []
    for i, (frame_path, effect, dur) in enumerate(zip(frame_paths, KEN_BURNS, seg_durations)):
        img = Image.open(frame_path).convert("RGB")
        clip = apply_ken_burns(img, dur, effect)
        video_segments.append(clip)
        print(f"   Segment {i+1}/3 — {effect} — {dur:.1f}s")

    # 8. Concatenate segments
    final_video = concatenate_videoclips(video_segments, method="compose")

    # 9. Add audio (voice + background music)
    bg_music_path = get_bg_music()
    if bg_music_path:
        try:
            bg = AudioFileClip(str(bg_music_path))
            # Loop music if shorter than video
            if bg.duration < total_duration:
                loops = int(total_duration / bg.duration) + 1
                from moviepy.editor import concatenate_audioclips
                bg = concatenate_audioclips([bg] * loops)
            bg = bg.subclip(0, total_duration).volumex(0.08)  # 8% volume — music subtle
            final_audio = CompositeAudioClip([voice_clip, bg])
        except Exception as e:
            print(f"⚠️ Music error: {e} — using voice only")
            final_audio = voice_clip
    else:
        final_audio = voice_clip

    final_video = final_video.set_audio(final_audio)

    # 10. Export — save as BOTH filenames for compatibility
    reel_path    = str(OUT / f"reel_{today}.mp4")    # for upload_facebook + upload_instagram
    daily_path   = str(OUT / "daily_reel.mp4")        # for upload_youtube (fallback)

    print(f"\n🎥 Rendering final video...")
    final_video.write_videofile(
        reel_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(OUT / "temp_audio.mp3"),
        remove_temp=True,
        logger=None
    )

    # Copy to daily_reel.mp4 for YouTube upload compatibility
    import shutil
    shutil.copy2(reel_path, daily_path)
    print(f"✅ Video saved: {reel_path}")
    print(f"✅ Video copied: {daily_path}")
    print(f"\n🚀 ZENO Reel ready — {today}")

if __name__ == "__main__":
    asyncio.run(run_reel())
