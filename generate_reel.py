"""
generate_reel.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generates ZENO evening reel (8:30 PM) — 45-60 second Hinglish reel.

VOICE: hi-IN-SwaraNeural (Swara — wise female, ZENO character)

Upload chain (DO NOT upload from here — upload_youtube.py handles it):
  generate_reel.py → output/reel_YYYYMMDD.mp4
                   → output/meta_YYYYMMDD.json  ← for upload chain
  upload_youtube.py → YouTube upload + writes youtube_video_id to meta
  upload_facebook.py → Facebook upload + overwrites public_video_url
  upload_instagram.py → reads public_video_url → Instagram upload

SEO: All tags from seo.get_video_tags() — never hardcoded here.
Mode: market / weekend / holiday via CONTENT_MODE env var.

Last updated: April 2026 — duplicate-upload fix + full SEO meta
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
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip

from human_touch import ht, seo

# ─── Content Mode ─────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")
print(f"[MODE] generate_reel.py running in mode: {CONTENT_MODE.upper()}")

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OUT = Path("output")
IMAGE_DIR = Path("public/image")
MUSIC_DIR = Path("public/music")
SW, SH = 1080, 1920
FPS = 30
IST = pytz.timezone("Asia/Kolkata")
VOICE = "hi-IN-SwaraNeural"  # ZENO voice — wise female

os.makedirs(OUT, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE = (255, 255, 255)


def get_font(path, size):
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def get_bg_music():
    day = datetime.now().weekday()
    music_map = {
        0: "bgmusic1.mp3", 1: "bgmusic2.mp3", 2: "bgmusic3.mp3",
        3: "bgmusic1.mp3", 4: "bgmusic2.mp3", 5: "bgmusic3.mp3",
        6: "bgmusic1.mp3"
    }
    f = MUSIC_DIR / music_map[day]
    if f.exists():
        return f
    for f in MUSIC_DIR.glob("*.mp3"):
        return f
    return None


def generate_script():
    """Generate fresh daily Hinglish ZENO script via Groq through ai_client."""
    from ai_client import ai

    today = datetime.now(IST).strftime("%A, %d %B %Y")

    # Topic selection based on CONTENT_MODE
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
        # Use hook from human_touch for the opening line
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
  "audio_script": "full spoken Hinglish script 80-100 words — what ZENO will say aloud",
  "display_text": "one powerful Hindi/Hinglish line shown on screen (max 12 words)",
  "emotion": "one of: happy, sad, fear, angry, thinking, greed, celebrating",
  "sentiment": "one of: positive, negative, fearful, motivated, greedy, angry, neutral",
  "description": "2-3 sentence English/Hinglish description for YouTube and Instagram with key insight"
}}"""

    print("🤖 Generating ZENO reel script via ai_client...")
    try:
        data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
        # Humanize the audio script
        raw_script = data.get("audio_script", "")
        if raw_script:
            data["audio_script"] = ht.humanize(raw_script, lang="hi")
        print(f"✅ ZENO script ready — emotion: {data.get('emotion')} | title: {data.get('title')}")
        return data
    except Exception as e:
        print(f"⚠️ Script generation error: {e} — using fallback script")
        return {
            "title": "CONTROL YOUR EMOTIONS",
            "audio_script": "दोस्तों ट्रेडिंग में सबसे बड़ा दुश्मन मार्केट नहीं आपका डर है। पेशेंस रखिए। हर loss एक lesson है। Discipline रखो, success जरूर मिलेगी।",
            "display_text": "मार्केट नहीं आपका डर है। पेशेंस रखिए।",
            "emotion": "fear",
            "sentiment": "fearful",
            "description": "ZENO ki baat: Trading mein patience aur discipline sabse zaroori hai. Apne emotions ko control karo."
        }


def apply_zeno_disney_effect(base_img, emotion="thinking"):
    zeno_path = IMAGE_DIR / f"zeno_{emotion}.png"
    if not zeno_path.exists():
        print(f"⚠️ Zeno image missing: {zeno_path} — using fallback")
        zeno_path = IMAGE_DIR / "zeno_thinking.png"
    if not zeno_path.exists():
        return base_img

    zeno = Image.open(str(zeno_path)).convert("RGBA")
    target_w = int(SW * 0.85)
    w_ratio = target_w / float(zeno.size[0])
    target_h = int(float(zeno.size[1]) * float(w_ratio))
    zeno = zeno.resize((target_w, target_h), Image.LANCZOS)

    shadow_layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    zeno_mask = zeno.split()[3]
    shadow_offset = (15, 15)
    shadow_pos = (
        (SW - zeno.width) // 2 + shadow_offset[0],
        SH - zeno.height - 180 + shadow_offset[1]
    )
    shadow_img = Image.new("RGBA", zeno.size, (0, 0, 0, 110))
    shadow_layer.paste(shadow_img, shadow_pos, zeno_mask)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=15))

    temp_bg = base_img.convert("RGBA")
    combined = Image.alpha_composite(temp_bg, shadow_layer)
    zeno_pos = ((SW - zeno.width) // 2, SH - zeno.height - 200)
    combined.paste(zeno, zeno_pos, zeno)
    return combined.convert("RGB")


def build_reel_frame(title_text, display_text, emotion="thinking"):
    img = Image.new("RGB", (SW, SH))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(SH):
        top_color, bot_color = (5, 10, 25), (15, 30, 70)
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * (y / SH))
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * (y / SH))
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * (y / SH))
        draw.line([(0, y), (SW, y)], fill=(r, g, b))

    draw.ellipse([100, 100, SW - 100, 600], fill=(60, 140, 255, 30))

    img = apply_zeno_disney_effect(img, emotion)
    draw_text = ImageDraw.Draw(img)

    font_title = get_font(FONT_BOLD, 85)
    text_y = 300
    words = title_text.split()
    mid = max(1, len(words) // 2)
    line1 = " ".join(words[:mid])
    line2 = " ".join(words[mid:])

    for line, offset in [(line1, 0), (line2, 105)]:
        if not line:
            continue
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            draw_text.text((SW // 2 + dx, text_y + offset + dy),
                           line, font=font_title, fill=(0, 0, 0), anchor="mm")
        draw_text.text((SW // 2, text_y + offset),
                       line, font=font_title, fill=WHITE, anchor="mm")

    font_display = get_font(FONT_BOLD, 44)
    display_y = SH - 340
    draw_text.rectangle([(0, display_y - 30), (SW, display_y + 90)],
                         fill=(0, 0, 0, 140))

    words_d, line_d, disp_lines = display_text.split(), "", []
    for w in words_d:
        test = (line_d + " " + w).strip()
        bbox = font_display.getbbox(test)
        if bbox[2] - bbox[0] < SW - 80:
            line_d = test
        else:
            disp_lines.append(line_d)
            line_d = w
    if line_d:
        disp_lines.append(line_d)

    for i, dl in enumerate(disp_lines[:2]):
        draw_text.text((SW // 2, display_y + i * 55),
                       dl, font=font_display, fill=(255, 220, 80), anchor="mm")

    font_brand = get_font(FONT_BOLD, 36)
    draw_text.text((SW // 2, SH - 220),
                   "✨ ai360trading.in", font=font_brand,
                   fill=(160, 200, 255), anchor="mm")
    draw_text.text((SW // 2, SH - 160),
                   "📱 t.me/ai360trading", font=font_brand,
                   fill=(140, 180, 240), anchor="mm")

    path = OUT / "zeno_reel_frame.png"
    img.save(str(path))
    return path


def build_youtube_title(script_data, today_str):
    """Build SEO-optimised YouTube title for the reel."""
    title_word = script_data.get("title", "TRADING WISDOM")
    date_tag = datetime.now(IST).strftime("%d %b %Y")

    if CONTENT_MODE == "holiday":
        label = HOLIDAY_NAME if HOLIDAY_NAME else "Market Holiday"
        return f"🎉 {label} — ZENO Ki Baat #{today_str[-4:]} #Shorts"
    elif CONTENT_MODE == "weekend":
        return f"📚 Weekend Wisdom — ZENO Ki Baat #{today_str[-4:]} #Shorts"
    else:
        return f"🎯 ZENO Ki Baat: {title_word.title()} — {date_tag} #Shorts"


def build_youtube_description(script_data, today_str):
    """Build full SEO description with hashtags from seo system."""
    desc_clean = script_data.get("description", "Daily trading wisdom by ZENO.")
    display = script_data.get("display_text", "")

    # Get SEO tags as hashtag string
    tags = seo.get_video_tags(mode=CONTENT_MODE, is_short=True)
    hashtag_str = " ".join([f"#{t}" for t in tags[:15]])

    if CONTENT_MODE == "holiday":
        label = HOLIDAY_NAME if HOLIDAY_NAME else "Market Holiday"
        desc = (
            f"🎉 {label} Special — Market band hai, learning nahi!\n\n"
            f"💡 {desc_clean}\n\n"
            f"✨ \"{display}\"\n\n"
            f"🌍 For investors: India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n"
            f"⚠️ Educational content only. Not financial advice.\n\n"
            f"#ZenoKiBaat #ai360trading #HolidayLearning {hashtag_str}"
        )
    elif CONTENT_MODE == "weekend":
        desc = (
            f"📚 Weekend Learning Special\n\n"
            f"💡 {desc_clean}\n\n"
            f"✨ \"{display}\"\n\n"
            f"🌍 For investors: India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n"
            f"⚠️ Educational content only. Not financial advice.\n\n"
            f"#ZenoKiBaat #ai360trading #WeekendWisdom {hashtag_str}"
        )
    else:
        desc = (
            f"🎯 Daily Trading Wisdom by ZENO\n\n"
            f"💡 {desc_clean}\n\n"
            f"✨ \"{display}\"\n\n"
            f"📊 Daily analysis for Nifty50 traders\n"
            f"🌍 Investors: India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n"
            f"⚠️ Educational content only. Not financial advice.\n\n"
            f"#ZenoKiBaat #ai360trading #TradingWisdom {hashtag_str}"
        )
    return desc


async def generate_reel():
    print("🎬 Starting ZENO Reel Generation...")
    today = datetime.now(IST).strftime("%Y%m%d")

    script = generate_script()

    title = script.get("title", "TRADING WISDOM")
    audio_script = script.get("audio_script", "Trading mein patience sabse zaroori hai.")
    display_text = script.get("display_text", "Patience hi success hai।")
    emotion = script.get("emotion", "thinking")
    sentiment = script.get("sentiment", "neutral")

    # TTS speed from human_touch system
    tts_speed = ht.get_tts_speed()
    rate_pct = int((tts_speed - 1.0) * 100)
    rate_str = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"

    audio_path = OUT / "zeno_speech.mp3"
    print(f"🎙️ Generating Voice (Swara, rate={rate_str})...")
    await edge_tts.Communicate(
        audio_script, VOICE, rate=rate_str
    ).save(str(audio_path))

    frame_path = build_reel_frame(title, display_text, emotion)

    print("🎞️ Rendering Final Reel...")
    voice_clip = AudioFileClip(str(audio_path))
    music_file = get_bg_music()
    if music_file:
        try:
            bg_m = AudioFileClip(str(music_file)).volumex(0.12).set_duration(voice_clip.duration)
            final_audio = CompositeAudioClip([voice_clip, bg_m])
            print(f"🎵 Music: {music_file.name}")
        except Exception as e:
            print(f"⚠️ Music error: {e}")
            final_audio = voice_clip
    else:
        final_audio = voice_clip

    video = (
        ImageClip(str(frame_path))
        .set_duration(voice_clip.duration + 0.5)
        .set_audio(final_audio)
    )

    output_file = OUT / "final_zeno_reel.mp4"
    video.write_videofile(
        str(output_file), fps=FPS,
        codec="libx264", audio_codec="aac", logger=None
    )

    # Copy to dated filename (upload_youtube.py looks for reel_YYYYMMDD.mp4)
    reel_dated = OUT / f"reel_{today}.mp4"
    shutil.copy2(str(output_file), str(reel_dated))
    print(f"✅ Video saved: {output_file.name} + {reel_dated.name}")

    # Build full SEO title and description
    yt_title = build_youtube_title(script, today)
    yt_desc = build_youtube_description(script, today)

    # Get tags from seo system (not hardcoded)
    tags = seo.get_video_tags(mode=CONTENT_MODE, is_short=True)

    # ── Save meta JSON for upload chain ──────────────────────────────────────
    # upload_youtube.py reads this file — MUST include title, description, tags
    meta = {
        "title": yt_title,
        "description": yt_desc,
        "tags": tags,
        "sentiment": sentiment,
        "content_mode": CONTENT_MODE,
        "emotion": emotion,
        "display_text": display_text,
        "public_video_url": ""   # upload_youtube.py fills this in
    }

    meta_path = OUT / f"meta_{today}.json"
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"✅ Meta saved: {meta_path.name}")
    print(f"   Title: {yt_title}")
    print(f"   Tags ({len(tags)}): {', '.join(tags[:5])}...")

    print("\n" + "=" * 50)
    print(f"✅ REEL READY — {output_file}")
    print(f"   TITLE   : {yt_title}")
    print(f"   MODE    : {CONTENT_MODE.upper()}")
    print(f"   EMOTION : {emotion} | SENTIMENT: {sentiment}")
    print(f"   TTS RATE: {rate_str}")
    print("   → Run upload_youtube.py to publish")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(generate_reel())
