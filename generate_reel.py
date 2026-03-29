"""
generate_reel.py — AI360Trading ZENO Evening Reel (8:30 PM)
============================================================
Generates 60s ZENO character reel in Hinglish.
Uses: ai_client (Groq→Gemini→Claude→OpenAI→Templates fallback)
Uses: human_touch (hooks, TTS speed, humanize)
Mode-aware: market / weekend / holiday
Output: output/reel_YYYYMMDD.mp4 + output/meta_YYYYMMDD.json
Upload: handled by upload_youtube.py → upload_facebook.py → upload_instagram.py
Author: AI360Trading Automation
Last Updated: March 2026 — Phase 2 Upgrade
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

# ─── Phase 2: ai_client + human_touch ────────────────────────────────────────
from ai_client import ai
from human_touch import ht, seo

# ─── Content Mode ─────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")

print(f"[MODE] generate_reel.py running in mode: {CONTENT_MODE.upper()}")
print(f"[AI]   Using ai_client fallback chain: Groq→Gemini→Claude→OpenAI→Templates")

# ─── CONFIG ──────────────────────────────────────────────────────────────────
OUT       = Path("output")
IMAGE_DIR = Path("public/image")
MUSIC_DIR = Path("public/music")
SW, SH    = 1080, 1920
FPS       = 30
IST       = pytz.timezone("Asia/Kolkata")

os.makedirs(OUT, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE     = (255, 255, 255)

def get_font(path, size):
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def get_bg_music():
    day = datetime.now().weekday()
    music_map = {0:"bgmusic1.mp3", 1:"bgmusic2.mp3", 2:"bgmusic3.mp3",
                 3:"bgmusic1.mp3", 4:"bgmusic2.mp3", 5:"bgmusic3.mp3", 6:"bgmusic1.mp3"}
    f = MUSIC_DIR / music_map[day]
    if f.exists():
        return f
    for f in MUSIC_DIR.glob("*.mp3"):
        return f
    return None

# ─── SCRIPT GENERATION via ai_client ─────────────────────────────────────────
def generate_script():
    today    = datetime.now(IST).strftime("%A, %d %B %Y")
    ht_hook  = ht.get_hook(mode=CONTENT_MODE)
    ht_phrase = ht.get_personal_phrase(lang="hi")

    if CONTENT_MODE == "holiday":
        topic = (
            f"special {HOLIDAY_NAME} message — inspire viewers to use this market holiday "
            "to learn, plan investments, and grow financially. "
            "Motivational and educational. Global appeal: India, US, UK, Brazil."
        )
    elif CONTENT_MODE == "weekend":
        topic = (
            "emotional life lesson about patience, discipline or money mindset — no market data. "
            "Motivational and educational for global audience: India, US, UK, Brazil."
        )
    else:
        topic = "stock market trading wisdom, psychology, or risk management lesson for Indian traders"

    prompt = f"""You are ZENO — a wise animated kid character teaching trading wisdom in Hinglish to Indian traders.

Today is {today}.
Content Mode: {CONTENT_MODE.upper()}
Topic: {topic}

HOOK TO OPEN WITH (adapt naturally — do not copy verbatim):
{ht_hook}

PERSONAL PHRASE (inject naturally once):
{ht_phrase}

Rules:
- Hinglish only (natural Hindi + English mix)
- Simple enough for a 10-year-old to understand
- Emotional, relatable, human touch
- One clear lesson only
- End with strong CTA: subscribe + t.me/ai360trading

Respond ONLY with valid JSON — no markdown, no extra text:
{{
  "title": "SHORT ENGLISH TITLE MAX 4 WORDS IN CAPS",
  "audio_script": "full spoken Hinglish script 80-100 words — what ZENO says aloud",
  "display_text": "one powerful Hindi/Hinglish line shown on screen max 12 words",
  "emotion": "one of: happy, sad, fear, angry, thinking, greed, celebrating",
  "sentiment": "one of: positive, negative, fearful, motivated, greedy, angry, neutral",
  "description": "2 sentence English/Hinglish description for YouTube and Instagram"
}}"""

    system_prompt = (
        "You are ZENO, a wise and relatable animated character for AI360Trading. "
        "Your Hinglish is natural, warm, and emotionally resonant. "
        "Never robotic. Never generic. Always one clear lesson per reel. "
        "Respond ONLY with valid JSON."
    )

    print("  🤖 Generating ZENO reel script via ai_client...")

    try:
        data = ai.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            content_mode=CONTENT_MODE,
            lang="hi",
        )
        if not data or not data.get("audio_script"):
            raise ValueError("Empty script from ai_client")
        # Humanize the audio script through human_touch
        data["audio_script"] = ht.humanize(data["audio_script"], lang="hi")
        print(f"  ✅ ZENO script ready — emotion: {data.get('emotion')} | via {ai.active_provider}")
        return data
    except Exception as e:
        print(f"  ⚠️ ai_client error: {e} — using fallback script")
        return _fallback_script()


def _fallback_script():
    """Template fallback — guaranteed content when all AI providers fail."""
    hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")
    scripts = {
        "market":  "Doston, trading mein sabse bada dushman market nahi — aapka darr hai. Patience rakho. Har loss ek lesson hai. Discipline rakho, success zaroor milegi. Subscribe karo ai360trading!",
        "weekend": "Doston, weekend mein bhi smart traders prepare karte hain. Apni journal review karo, charts study karo. Next week ready raho. ai360trading ke saath seekhte raho!",
        "holiday": f"{HOLIDAY_NAME} mubarak! Market band hai, par aapki growth nahi rukni chahiye. Aaj apna financial plan review karo. ai360trading ke saath milkar grow karo!",
    }
    display = {
        "market":  "Patience hi success hai।",
        "weekend": "Weekend = Preparation time!",
        "holiday": "Market band, seekhna chalu!",
    }
    return {
        "title":        "CONTROL YOUR MIND",
        "audio_script": scripts.get(CONTENT_MODE, scripts["market"]),
        "display_text": display.get(CONTENT_MODE, display["market"]),
        "emotion":      "thinking",
        "sentiment":    "motivated",
        "description":  "ZENO ki baat: Trading mein patience aur discipline sabse zaroori hai. Follow ai360trading.",
    }

# ─── VISUAL RENDERER ─────────────────────────────────────────────────────────
def apply_zeno_disney_effect(base_img, emotion="thinking"):
    zeno_path = IMAGE_DIR / f"zeno_{emotion}.png"
    if not zeno_path.exists():
        print(f"  ⚠️ Zeno image missing: {zeno_path} — using fallback")
        zeno_path = IMAGE_DIR / "zeno_thinking.png"
    if not zeno_path.exists():
        return base_img
    zeno     = Image.open(str(zeno_path)).convert("RGBA")
    target_w = int(SW * 0.85)
    w_ratio  = target_w / float(zeno.size[0])
    target_h = int(float(zeno.size[1]) * float(w_ratio))
    zeno     = zeno.resize((target_w, target_h), Image.LANCZOS)

    shadow_layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    zeno_mask    = zeno.split()[3]
    shadow_pos   = ((SW - zeno.width) // 2 + 15, SH - zeno.height - 165)
    shadow_img   = Image.new("RGBA", zeno.size, (0, 0, 0, 110))
    shadow_layer.paste(shadow_img, shadow_pos, zeno_mask)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=15))

    temp_bg  = base_img.convert("RGBA")
    combined = Image.alpha_composite(temp_bg, shadow_layer)
    zeno_pos = ((SW - zeno.width) // 2, SH - zeno.height - 200)
    combined.paste(zeno, zeno_pos, zeno)
    return combined.convert("RGB")


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

    # Mode badge
    if CONTENT_MODE in ("holiday", "weekend"):
        badge = f"🎯 {HOLIDAY_NAME.upper()[:20]}" if CONTENT_MODE == "holiday" else "📚 WEEKEND WISDOM"
        draw.text((SW // 2, 60), badge, font=get_font(FONT_BOLD, 38),
                  fill=(255, 200, 60), anchor="mm")

    img = apply_zeno_disney_effect(img, emotion)

    draw_text  = ImageDraw.Draw(img)
    font_title = get_font(FONT_BOLD, 85)
    text_y     = 300
    words      = title_text.split()
    mid        = max(1, len(words) // 2)
    line1      = " ".join(words[:mid])
    line2      = " ".join(words[mid:])

    for line, offset in [(line1, 0), (line2, 105)]:
        if not line:
            continue
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            draw_text.text((SW // 2 + dx, text_y + offset + dy),
                           line, font=font_title, fill=(0, 0, 0), anchor="mm")
        draw_text.text((SW // 2, text_y + offset),
                       line, font=font_title, fill=WHITE, anchor="mm")

    font_display = get_font(FONT_BOLD, 44)
    display_y    = SH - 340
    draw_text.rectangle([(0, display_y - 30), (SW, display_y + 90)], fill=(0, 0, 0, 140))

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
    draw_text.text((SW // 2, SH - 220), "✨ ai360trading.in",
                   font=font_brand, fill=(160, 200, 255), anchor="mm")
    draw_text.text((SW // 2, SH - 160), "📱 t.me/ai360trading",
                   font=font_brand, fill=(140, 180, 240), anchor="mm")

    path = OUT / "zeno_reel_frame.png"
    img.save(str(path))
    return path

# ─── MAIN ─────────────────────────────────────────────────────────────────────
async def generate_reel():
    print("  🎬 Starting ZENO Reel Generation...")
    today  = datetime.now().strftime("%Y%m%d")
    script = generate_script()

    title        = script.get("title", "TRADING WISDOM")
    audio_script = script.get("audio_script", "Trading mein patience sabse zaroori hai.")
    display_text = script.get("display_text", "Patience hi success hai।")
    emotion      = script.get("emotion", "thinking")
    sentiment    = script.get("sentiment", "neutral")
    description  = script.get("description", "Daily trading wisdom by ZENO. Follow ai360trading.")

    # ── Phase 2: TTS speed from human_touch ─────────────────────────────────
    tts_speed = ht.get_tts_speed()
    rate_pct  = int((tts_speed - 1.0) * 100)
    rate_str  = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"

    audio_path = OUT / "zeno_speech.mp3"
    print("  🎙️ Generating ZENO voice...")
    try:
        await edge_tts.Communicate(audio_script, "hi-IN-SwaraNeural", rate=rate_str).save(str(audio_path))
    except Exception:
        await edge_tts.Communicate(audio_script, "hi-IN-SwaraNeural").save(str(audio_path))

    frame_path = build_reel_frame(title, display_text, emotion)

    print("  🎞️ Rendering final reel...")
    voice_clip  = AudioFileClip(str(audio_path))
    music_file  = get_bg_music()
    if music_file:
        try:
            bg_m        = AudioFileClip(str(music_file)).volumex(0.12).set_duration(voice_clip.duration)
            final_audio = CompositeAudioClip([voice_clip, bg_m])
            print(f"  🎵 Music: {music_file.name}")
        except Exception as e:
            print(f"  ⚠️ Music error: {e}")
            final_audio = voice_clip
    else:
        final_audio = voice_clip

    video = (
        ImageClip(str(frame_path))
        .set_duration(voice_clip.duration + 0.5)
        .set_audio(final_audio)
    )
    output_file = OUT / "final_zeno_reel.mp4"
    video.write_videofile(str(output_file), fps=FPS, codec="libx264",
                          audio_codec="aac", logger=None)

    reel_dated = OUT / f"reel_{today}.mp4"
    shutil.copy2(str(output_file), str(reel_dated))
    print(f"  ✅ Video saved: {output_file.name} + {reel_dated.name}")

    # ── Phase 2: SEO tags from human_touch ──────────────────────────────────
    ht_tags   = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")
    tags_str  = " ".join([f"#{t}" for t in ht_tags[:10]])

    meta = {
        "title":          f"ZENO Ki Baat - {title}",
        "description":    description + " 🔗 t.me/ai360trading | ai360trading.in",
        "sentiment":      sentiment,
        "content_mode":   CONTENT_MODE,
        "hashtags":       f"#ZenoKiBaat #ai360trading #StockMarketIndia #TradingWisdom #Hinglish #FinancialLiteracy {tags_str}",
        "public_video_url": "",
        "ai_provider":    ai.active_provider,
    }
    meta_path = OUT / f"meta_{today}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅ Meta saved: {meta_path.name}")

    print("\n" + "=" * 50)
    print(f"  ✅ REEL SUCCESS: {output_file}")
    print(f"  TITLE   : ZENO Ki Baat - {title}")
    print(f"  MODE    : {CONTENT_MODE.upper()}")
    print(f"  EMOTION : {emotion} | SENTIMENT: {sentiment}")
    print(f"  AI      : {ai.active_provider}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(generate_reel())
