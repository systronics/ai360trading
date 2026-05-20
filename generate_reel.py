"""
generate_reel.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generates ZENO evening reel (8:30 PM) — 45-60 second Hinglish reel.

VOICE: hi-IN-SwaraNeural (Swara — wise female, ZENO character)

v2.1 FIXES (May 2026):
  FIX 1 — Background music removed
    Reason: Meta mutes videos in many countries for copyright
    Fix: TTS voice only — no bgmusic files needed
    public/music/ folder deleted — safe

  FIX 2 — Proper thumbnail with big text + ZENO
    Old: ZENO + small 85px text = low CTR
    New: ZENO 70% height + 130px bold yellow title + stock/topic badge
    Result: Readable in 2 seconds on mobile feed

Upload chain:
  generate_reel.py → output/reel_YYYYMMDD.mp4 + meta_YYYYMMDD.json
  upload_youtube.py → YouTube
  upload_facebook.py → Facebook Page

Mode: market / weekend / holiday via CONTENT_MODE env var.
"""

import os
import json
import asyncio
import shutil
from datetime import datetime
from pathlib import Path

import pytz
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip

from human_touch import ht, seo

# ─── Content Mode ─────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")
print(f"[MODE] generate_reel.py running in mode: {CONTENT_MODE.upper()}")

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OUT       = Path("output")
IMAGE_DIR = Path("public/image")
SW, SH    = 1080, 1920
FPS       = 30
IST       = pytz.timezone("Asia/Kolkata")
VOICE     = "hi-IN-SwaraNeural"

os.makedirs(OUT, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
WHITE     = (255, 255, 255)


def get_font(path, size):
    if os.path.exists(path):
        try: return ImageFont.truetype(path, size)
        except: pass
    return ImageFont.load_default()


# ─── SCRIPT GENERATION ────────────────────────────────────────────────────────

def generate_script():
    from ai_client import ai

    today = datetime.now(IST).strftime("%A, %d %B %Y")

    if CONTENT_MODE == "holiday":
        holiday_label = HOLIDAY_NAME if HOLIDAY_NAME else "Indian Market Holiday"
        topic = (
            f"special {holiday_label} message — inspire viewers to use this market holiday "
            f"to learn, plan investments, and grow financially. "
            f"Motivational, educational, no live market data. "
            f"Global appeal: relevant to viewers in India, US, UK and Brazil."
        )
    elif CONTENT_MODE == "weekend":
        topic = (
            "emotional life lesson about patience, discipline or money mindset — no market data. "
            "Motivational and educational for global audience: India, US, UK, Brazil."
        )
    else:
        hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")
        topic = (
            f"stock market trading wisdom, psychology, or risk management lesson for Indian traders. "
            f"Start with this hook: '{hook}'"
        )

    prompt = f"""You are ZENO — a wise animated kid character teaching trading wisdom in Hinglish to Indian traders.

Today is {today}. Create a 45-60 second reel script on: {topic}

Rules:
- Hinglish only (natural Hindi + English mix)
- Simple enough for a 10-year-old to understand
- Emotional, relatable, human touch
- One clear lesson only
- End with strong CTA to subscribe

Respond ONLY with valid JSON, no markdown:
{{
  "title": "SHORT ENGLISH TITLE MAX 4 WORDS IN CAPS (for display on screen)",
  "audio_script": "full spoken Hinglish script 80-100 words",
  "display_text": "one powerful Hindi/Hinglish line shown on screen (max 12 words)",
  "emotion": "one of: happy, sad, fear, angry, thinking, greed, celebrating",
  "sentiment": "one of: positive, negative, fearful, motivated, greedy, angry, neutral",
  "description": "2-3 sentence English/Hinglish description for YouTube with key insight"
}}"""

    print("Generating ZENO reel script...")
    try:
        data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
        raw  = data.get("audio_script", "")
        if raw:
            data["audio_script"] = ht.humanize(raw, lang="hi")
        print(f"ZENO script ready — emotion: {data.get('emotion')} | title: {data.get('title')}")
        return data
    except Exception as e:
        print(f"Script error: {e} — using fallback")
        return {
            "title": "CONTROL YOUR EMOTIONS",
            "audio_script": "Doston trading mein sabse bada dushman market nahi aapka dar hai. Patience rakhiye. Har loss ek lesson hai. Discipline rakho success zaroor milegi.",
            "display_text": "Market nahi aapka dar hai. Patience rakhiye.",
            "emotion": "fear",
            "sentiment": "fearful",
            "description": "ZENO ki baat: Trading mein patience aur discipline sabse zaroori hai."
        }


# ─── ZENO EFFECT ──────────────────────────────────────────────────────────────

def apply_zeno_effect(base_img, emotion="thinking"):
    zeno_path = IMAGE_DIR / f"zeno_{emotion}.png"
    if not zeno_path.exists():
        zeno_path = IMAGE_DIR / "zeno_thinking.png"
    if not zeno_path.exists():
        return base_img

    zeno     = Image.open(str(zeno_path)).convert("RGBA")
    target_w = int(SW * 0.85)
    w_ratio  = target_w / float(zeno.size[0])
    target_h = int(float(zeno.size[1]) * float(w_ratio))
    zeno     = zeno.resize((target_w, target_h), Image.LANCZOS)

    # Shadow
    shadow_layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    zeno_mask    = zeno.split()[3]
    shadow_pos   = ((SW - zeno.width) // 2 + 15, SH - zeno.height - 180 + 15)
    shadow_img   = Image.new("RGBA", zeno.size, (0, 0, 0, 110))
    shadow_layer.paste(shadow_img, shadow_pos, zeno_mask)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=15))

    combined  = Image.alpha_composite(base_img.convert("RGBA"), shadow_layer)
    zeno_pos  = ((SW - zeno.width) // 2, SH - zeno.height - 200)
    combined.paste(zeno, zeno_pos, zeno)
    return combined.convert("RGB")


# ─── v2.1 FIX 2: PROPER THUMBNAIL ────────────────────────────────────────────

def build_thumbnail(title_text, display_text, emotion="thinking"):
    """
    Proper thumbnail that drives CTR.

    Layout:
      - Dark gradient background
      - ZENO 70% frame height — visible on mobile feed
      - Title: 130px bold YELLOW — readable in 2 seconds
      - Display text: 52px white with dark backing
      - Accent bars top and bottom
      - AI360Trading badge
    """
    img  = Image.new("RGB", (SW, SH))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradient background
    for y in range(SH):
        t  = y / SH
        bg = (int(5 + t*10), int(10 + t*20), int(25 + t*45))
        draw.line([(0, y), (SW, y)], fill=bg)

    # Accent bars
    draw.rectangle([(0, 0), (SW, 14)], fill=(255, 200, 0))
    draw.rectangle([(0, SH-14), (SW, SH)], fill=(255, 200, 0))

    # ZENO — 70% height, centered bottom
    zeno_path = IMAGE_DIR / f"zeno_{emotion}.png"
    if not zeno_path.exists():
        zeno_path = IMAGE_DIR / "zeno_thinking.png"
    if zeno_path.exists():
        try:
            zeno     = Image.open(str(zeno_path)).convert("RGBA")
            zeno_h   = int(SH * 0.70)
            zeno_w   = int(zeno.width * (zeno_h / zeno.height))
            zeno     = zeno.resize((zeno_w, zeno_h), Image.LANCZOS)
            zeno_x   = (SW - zeno_w) // 2
            zeno_y   = SH - zeno_h - 60
            img.paste(zeno, (zeno_x, zeno_y), zeno)
        except Exception as e:
            print(f"ZENO thumbnail paste: {e}")

    draw = ImageDraw.Draw(img, "RGBA")

    # Title — 130px bold yellow — top area
    f_title = get_font(FONT_BOLD, 130)
    f_disp  = get_font(FONT_BOLD, 52)
    f_badge = get_font(FONT_BOLD, 40)

    import textwrap
    safe_title   = title_text.upper()
    title_lines  = textwrap.wrap(safe_title, width=10)
    ty = 100
    for line in title_lines[:2]:
        # Shadow
        for dx, dy in [(-3,3),(3,-3),(-3,-3),(3,3)]:
            draw.text((SW//2+dx, ty+dy), line, font=f_title,
                      fill=(0, 0, 0, 200), anchor="mm")
        draw.text((SW//2, ty), line, font=f_title,
                  fill=(255, 200, 0), anchor="mm")
        ty += 148

    # Display text — white with dark bg strip
    safe_display = display_text
    strip_y = ty + 20
    draw.rectangle([(0, strip_y), (SW, strip_y + 80)], fill=(0, 0, 0, 160))
    disp_lines = textwrap.wrap(safe_display, width=22)
    for i, dl in enumerate(disp_lines[:2]):
        draw.text((SW//2, strip_y + 40 + i*58), dl,
                  font=f_disp, fill=(255, 255, 255), anchor="mm")

    # AI360Trading badge — top left
    draw.rounded_rectangle([(20, 20), (320, 80)], radius=14, fill=(255, 200, 0))
    draw.text((170, 50), "AI360TRADING", font=f_badge, fill=(0, 0, 0), anchor="mm")

    thumb_path = OUT / "zeno_reel_thumb.png"
    img.save(str(thumb_path))
    return thumb_path


# ─── REEL FRAME (for video) ───────────────────────────────────────────────────

def build_reel_frame(title_text, display_text, emotion="thinking"):
    img  = Image.new("RGB", (SW, SH))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(SH):
        top_color, bot_color = (5, 10, 25), (15, 30, 70)
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * (y / SH))
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * (y / SH))
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * (y / SH))
        draw.line([(0, y), (SW, y)], fill=(r, g, b))

    draw.ellipse([100, 100, SW - 100, 600], fill=(60, 140, 255, 30))
    img       = apply_zeno_effect(img, emotion)
    draw_text = ImageDraw.Draw(img)

    font_title  = get_font(FONT_BOLD, 85)
    text_y      = 300
    words       = title_text.split()
    mid         = max(1, len(words) // 2)
    line1       = " ".join(words[:mid])
    line2       = " ".join(words[mid:])

    for line, offset in [(line1, 0), (line2, 105)]:
        if not line: continue
        for dx, dy in [(-2,-2),(2,-2),(-2,2),(2,2)]:
            draw_text.text((SW//2+dx, text_y+offset+dy),
                           line, font=font_title, fill=(0,0,0), anchor="mm")
        draw_text.text((SW//2, text_y+offset),
                       line, font=font_title, fill=WHITE, anchor="mm")

    font_display = get_font(FONT_BOLD, 44)
    display_y    = SH - 340
    draw_text.rectangle([(0, display_y-30), (SW, display_y+90)], fill=(0,0,0,140))

    words_d, line_d, disp_lines = display_text.split(), "", []
    for w in words_d:
        test = (line_d + " " + w).strip()
        bbox = font_display.getbbox(test)
        if bbox[2] - bbox[0] < SW - 80:
            line_d = test
        else:
            disp_lines.append(line_d); line_d = w
    if line_d: disp_lines.append(line_d)

    for i, dl in enumerate(disp_lines[:2]):
        draw_text.text((SW//2, display_y + i*55),
                       dl, font=font_display, fill=(255, 220, 80), anchor="mm")

    font_brand = get_font(FONT_BOLD, 36)
    draw_text.text((SW//2, SH-220), "✦ ai360trading.in",
                   font=font_brand, fill=(160, 200, 255), anchor="mm")
    draw_text.text((SW//2, SH-160), "📱 t.me/ai360trading",
                   font=font_brand, fill=(140, 180, 240), anchor="mm")

    path = OUT / "zeno_reel_frame.png"
    img.save(str(path))
    return path


# ─── YOUTUBE TITLE + DESC ─────────────────────────────────────────────────────

def build_youtube_title(script_data, today_str):
    title_word = script_data.get("title", "TRADING WISDOM")
    date_tag   = datetime.now(IST).strftime("%d %b %Y")
    if CONTENT_MODE == "holiday":
        label = HOLIDAY_NAME if HOLIDAY_NAME else "Market Holiday"
        return f"🎉 {label} — ZENO Ki Baat #{today_str[-4:]} #Shorts"
    elif CONTENT_MODE == "weekend":
        return f"📚 Weekend Wisdom — ZENO Ki Baat #{today_str[-4:]} #Shorts"
    else:
        return f"🎯 ZENO Ki Baat: {title_word.title()} — {date_tag} #Shorts"


def build_youtube_description(script_data, today_str):
    desc_clean  = script_data.get("description", "Daily trading wisdom by ZENO.")
    display     = script_data.get("display_text", "")
    tags        = seo.get_video_tags(mode=CONTENT_MODE, is_short=True)
    hashtag_str = " ".join([f"#{t}" for t in tags[:15]])

    if CONTENT_MODE == "holiday":
        label = HOLIDAY_NAME if HOLIDAY_NAME else "Market Holiday"
        desc  = (
            f"🎉 {label} Special — Market band hai, learning nahi!\n\n"
            f"💡 {desc_clean}\n\n"
            f'✦ "{display}"\n\n'
            f"🌍 For investors: India, USA, UK, Brazil & UAE\n"
            f"🌐 https://ai360trading.in\n"
            f"📱 https://t.me/ai360trading\n"
            f"⚠️ Educational only. Not financial advice.\n\n"
            f"#ZenoKiBaat #ai360trading #HolidayLearning {hashtag_str}"
        )
    elif CONTENT_MODE == "weekend":
        desc = (
            f"📚 Weekend Learning Special\n\n"
            f"💡 {desc_clean}\n\n"
            f'✦ "{display}"\n\n'
            f"🌍 For investors: India, USA, UK, Brazil & UAE\n"
            f"🌐 https://ai360trading.in\n"
            f"📱 https://t.me/ai360trading\n"
            f"⚠️ Educational only. Not financial advice.\n\n"
            f"#ZenoKiBaat #WeekendWisdom #ai360trading {hashtag_str}"
        )
    else:
        desc = (
            f"🎯 ZENO Ki Baat — Daily trading wisdom\n\n"
            f"💡 {desc_clean}\n\n"
            f'✦ "{display}"\n\n'
            f"🌍 For traders: India, USA, UK, Brazil & UAE\n"
            f"🌐 https://ai360trading.in\n"
            f"📱 https://t.me/ai360trading\n"
            f"⚠️ Educational only. Not SEBI registered.\n\n"
            f"#ZenoKiBaat #StockMarket #ai360trading {hashtag_str}"
        )
    return desc


# ─── TTS ──────────────────────────────────────────────────────────────────────

async def generate_tts(text, output_path):
    communicate = edge_tts.Communicate(text, VOICE, rate="+5%")
    await communicate.save(str(output_path))


# ─── VIDEO COMPOSITION — NO BACKGROUND MUSIC ──────────────────────────────────

def compose_video(frame_path, audio_path, output_path):
    """
    Compose final reel — TTS voice only, no background music.
    Music removed in v2.1 to prevent Meta muting in countries
    where Meta does not have music rights.
    """
    audio_clip = AudioFileClip(str(audio_path))
    duration   = audio_clip.duration + 0.5

    video = ImageClip(str(frame_path)).set_duration(duration)
    video = video.set_audio(audio_clip)
    # NOTE: No CompositeAudioClip, no bgmusic — TTS only
    video.write_videofile(
        str(output_path), fps=FPS, codec="libx264",
        audio_codec="aac", verbose=False, logger=None
    )
    print(f"Reel exported: {output_path} ({duration:.1f}s) — voice only, no bgmusic")


# ─── SAVE META ────────────────────────────────────────────────────────────────

def save_meta(script_data, today_str, thumb_path=None):
    tags      = seo.get_video_tags(mode=CONTENT_MODE, is_short=True)
    yt_tags   = seo.get_youtube_safe_tags(tags)
    meta_path = OUT / f"meta_{today_str}.json"

    meta = {
        "title":        build_youtube_title(script_data, today_str),
        "description":  build_youtube_description(script_data, today_str),
        "tags":         yt_tags,
        "video_path":   str(OUT / f"reel_{today_str}.mp4"),
        "thumb_path":   str(thumb_path) if thumb_path else "",
        "emotion":      script_data.get("emotion", "thinking"),
        "content_mode": CONTENT_MODE,
        "music":        "none — TTS voice only",
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"Meta saved: {meta_path}")
    return str(meta_path)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

async def main():
    today_str  = datetime.now(IST).strftime("%Y%m%d")
    video_path = OUT / f"reel_{today_str}.mp4"
    audio_path = OUT / f"reel_audio_{today_str}.mp3"

    # Check if already generated today (duplicate prevention)
    if video_path.exists() and video_path.stat().st_size > 100_000:
        print(f"Reel already exists for today: {video_path} — skipping")
        return

    print(f"Generating ZENO reel — {today_str} | Mode: {CONTENT_MODE.upper()}")

    # Step 1: Script
    script  = generate_script()
    emotion = script.get("emotion", "thinking")
    title   = script.get("title", "TRADING WISDOM")
    display = script.get("display_text", "Patience + Discipline = Success")
    audio_script = script.get("audio_script", "")

    print(f"Script ready | title: {title} | emotion: {emotion}")

    # Step 2: TTS audio
    await generate_tts(audio_script, audio_path)

    # Step 3: Build video frame
    frame_path = build_reel_frame(title, display, emotion)

    # Step 4: Build thumbnail (v2.1 FIX — proper CTR thumbnail)
    thumb_path = build_thumbnail(title, display, emotion)
    print(f"Thumbnail built: {thumb_path}")

    # Step 5: Compose video — TTS only, no music
    compose_video(frame_path, audio_path, video_path)

    # Step 6: Save meta
    save_meta(script, today_str, thumb_path)

    print("=" * 50)
    print(f"ZENO REEL DONE")
    print(f"  Video:     {video_path}")
    print(f"  Thumbnail: {thumb_path}")
    print(f"  Emotion:   {emotion}")
    print(f"  Music:     none (no copyright risk)")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
