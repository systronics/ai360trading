"""
generate_reel.py -- AI360Trading
======================================================
Generates the evening reel (8:30 PM) -- 45-60 second Hinglish reel.

VOICE: hi-IN-SwaraNeural (Swara -- wise female voice)

v2.5 (2026-07-22) -- ZENO RETIRED, DATA-GROUNDED, REBRANDED TO AMIT:
  Owner ("Amit"): "zeno character not fit for serious traders... use my
  name Amit instead... content for serious traders... live and real data."
  - Persona: prompt no longer casts the narrator as "ZENO, an animated kid
    character." It now writes in Amit'''s voice -- an experienced trader
    speaking directly to serious traders, not a mascot teaching children.
  - Real data: this reel used to be 100% generic "trading wisdom" with zero
    market data (the topic prompt literally said "no live market data" for
    weekend/holiday modes and never pulled a real number on market days
    either). Added fetch_eod_snapshot() (yfinance, fail-open) -- a real
    NIFTY close + %change is now fetched and required to appear in the
    script on market days, so the lesson is anchored to something that
    actually happened today, not detached generic advice.
  - Visuals: apply_zeno_effect() and all zeno_*.png character compositing
    removed from both the thumbnail and the in-video frame. Replaced with
    a bold live-data stat block (NIFTY level + %change, color-coded) -- the
    same "specific real number stops the scroll" principle already proven
    in the morning reel, now applied here too. No new character art needed.
  - Branding: "ZENO Ki Baat" -> "Amit Ki Baat" across titles, descriptions,
    hashtags, on-screen badge, and log lines.

v2.4 (2026-06-02):
  ADD — Edge TTS 503 retry in generate_tts() (4x, 5/15/30s backoff + non-empty
    check). Transient wss://speech.platform.bing.com 503 now self-heals in-run.

v2.3 (2026-05-31):
  ADD — bold-text HOOK intro frame (via hook_helper.py) prepended to the
  reel so the in-feed cover stops the scroll on YouTube/Instagram/Facebook.
  Narration shifts to start after the hook so captions stay synced.
  Fully fail-open → any error falls back to the hook-less reel.

v2.2 (2026-05-31):
  ADD — burned-in captions via caption_helper.py (Pillow-rendered,
  proportionally timed, fully fail-open → never breaks the daily reel).

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

# Money funnel (free Telegram → membership + broker referrals + comment prompt).
try:
    import money_funnel as mf
except Exception:
    mf = None


def _funnel(lang="hi", compact=False):
    try:
        return mf.funnel_block(lang=lang, compact=compact) if mf else ""
    except Exception:
        return ""

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


# v2.5: real EOD market snapshot -- fail-open (returns all-zero dict on any
# error so the reel still generates; the prompt/visuals just skip the
# data-anchor line when nifty_cmp is 0).
def fetch_eod_snapshot() -> dict:
    try:
        import yfinance as yf
        t = yf.Ticker("^NSEI")
        df = t.history(period="5d", interval="1d")
        if len(df) >= 2:
            prev = float(df["Close"].iloc[-2])
            cmp  = float(df["Close"].iloc[-1])
            if prev > 0 and cmp > 0:
                pct = round(((cmp - prev) / prev) * 100, 2)
                return {"nifty_cmp": round(cmp, 0), "nifty_pct": pct}
    except Exception as e:
        print(f"[EOD] snapshot fetch failed (fail-open): {e}")
    return {"nifty_cmp": 0, "nifty_pct": 0.0}


# ─── SCRIPT GENERATION ────────────────────────────────────────────────────────

def generate_script():
    from ai_client import ai

    today = datetime.now(IST).strftime("%A, %d %B %Y")
    snap  = fetch_eod_snapshot() if CONTENT_MODE == "market" else {"nifty_cmp": 0, "nifty_pct": 0.0}
    data_line = (
        f"REAL DATA (must be referenced naturally in the script): NIFTY closed today at "
        f"{snap['nifty_cmp']:.0f} ({snap['nifty_pct']:+.2f}%)."
        if snap["nifty_cmp"] > 0 else ""
    )

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
            "emotional life lesson about patience, discipline or money mindset, grounded in a real "
            "trading example (not a fabricated one). "
            "Motivational and educational for global audience: India, US, UK, Brazil."
        )
    else:
        hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")
        topic = (
            f"stock market trading wisdom, psychology, or risk management lesson for serious Indian "
            f"traders, tied to today's actual market move. "
            f"Start with this hook: '{hook}'"
        )

    prompt = f"""You are Amit, an experienced Indian trader and the founder of AI360Trading, speaking directly
to serious traders in Hinglish -- not a cartoon, not a kid's character. First person, confident,
grounded in real experience.

Today is {today}. {data_line}

Create a 45-60 second reel script on: {topic}

Rules:
- Hinglish only (natural Hindi + English mix)
- Written for a serious adult trader, not simplified for children
- If real data is given above, reference the actual number naturally — never invent a number
- Direct, credible, no exaggerated claims or guaranteed-profit language
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

    print("Generating reel script (Amit persona)...")
    try:
        data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
        raw  = data.get("audio_script", "")
        if raw:
            data["audio_script"] = ht.humanize(raw, lang="hi")
        data["nifty_cmp"] = snap["nifty_cmp"]
        data["nifty_pct"] = snap["nifty_pct"]
        print(f"Script ready — emotion: {data.get('emotion')} | title: {data.get('title')}")
        return data
    except Exception as e:
        print(f"Script error: {e} — using fallback")
        return {
            "title": "CONTROL YOUR EMOTIONS",
            "audio_script": "Doston trading mein sabse bada dushman market nahi aapka dar hai. Patience rakhiye. Har loss ek lesson hai. Discipline rakho success zaroor milegi.",
            "display_text": "Market nahi aapka dar hai. Patience rakhiye.",
            "emotion": "fear",
            "sentiment": "fearful",
            "description": "Amit ki baat: Trading mein patience aur discipline sabse zaroori hai.",
            "nifty_cmp": snap["nifty_cmp"],
            "nifty_pct": snap["nifty_pct"],
        }


# ─── LIVE DATA STAT BLOCK (v2.5 — replaces ZENO character) ────────────────────
# Owner ("Amit") does not want a cartoon fronting content for serious traders.
# A real NIFTY number in the frame is the credibility play a mascot can't be.

def draw_stat_block(img, nifty_cmp, nifty_pct):
    if not nifty_cmp:
        return img
    draw  = ImageDraw.Draw(img, "RGBA")
    up    = nifty_pct >= 0
    color = (0, 210, 100) if up else (220, 70, 70)
    box_y = SH - 560
    draw.rounded_rectangle([(80, box_y), (SW - 80, box_y + 260)], radius=24,
                            fill=(255, 255, 255, 22))
    f_label = get_font(FONT_BOLD, 44)
    f_val   = get_font(FONT_BOLD, 110)
    f_pct   = get_font(FONT_BOLD, 56)
    draw.text((SW // 2, box_y + 60), "NIFTY TODAY", font=f_label,
              fill=(190, 205, 230), anchor="mm")
    draw.text((SW // 2, box_y + 155), f"{nifty_cmp:,.0f}", font=f_val,
              fill=(255, 255, 255), anchor="mm")
    arrow = "UP" if up else "DOWN"
    draw.rounded_rectangle([(SW // 2 - 160, box_y + 205), (SW // 2 + 160, box_y + 250)],
                            radius=14, fill=color)
    draw.text((SW // 2, box_y + 228), f"{arrow} {abs(nifty_pct):.2f}%", font=f_pct,
              fill=(0, 0, 0) if up else (255, 255, 255), anchor="mm")
    return img


# ─── v2.1 FIX 2: PROPER THUMBNAIL ────────────────────────────────────────────

def build_thumbnail(title_text, display_text, emotion="thinking", nifty_cmp=0, nifty_pct=0.0):
    """
    Proper thumbnail that drives CTR.

    Layout (v2.5 — ZENO retired):
      - Dark gradient background
      - Live NIFTY stat block (real number, color-coded) — replaces the
        cartoon character; a serious trader stops for a real number, not
        a mascot
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

    # v2.5: live NIFTY stat block, bottom half — replaces the ZENO character
    img  = draw_stat_block(img, nifty_cmp, nifty_pct)
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

def build_reel_frame(title_text, display_text, emotion="thinking", nifty_cmp=0, nifty_pct=0.0):
    img  = Image.new("RGB", (SW, SH))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(SH):
        top_color, bot_color = (5, 10, 25), (15, 30, 70)
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * (y / SH))
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * (y / SH))
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * (y / SH))
        draw.line([(0, y), (SW, y)], fill=(r, g, b))

    draw.ellipse([100, 100, SW - 100, 600], fill=(60, 140, 255, 30))
    img       = draw_stat_block(img, nifty_cmp, nifty_pct)  # v2.5: replaces ZENO
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

    path = OUT / "zeno_reel_frame.png"  # internal output filename, unchanged
    img.save(str(path))
    return path


# ─── YOUTUBE TITLE + DESC ─────────────────────────────────────────────────────

def build_youtube_title(script_data, today_str):
    title_word = script_data.get("title", "TRADING WISDOM")
    date_tag   = datetime.now(IST).strftime("%d %b %Y")
    nifty_cmp  = script_data.get("nifty_cmp", 0)
    nifty_tag  = f"Nifty {nifty_cmp:,.0f} | " if nifty_cmp else ""
    if CONTENT_MODE == "holiday":
        label = HOLIDAY_NAME if HOLIDAY_NAME else "Market Holiday"
        return f"🎉 {label} — Amit Ki Baat #{today_str[-4:]} #Shorts"
    elif CONTENT_MODE == "weekend":
        return f"📚 Weekend Wisdom — Amit Ki Baat #{today_str[-4:]} #Shorts"
    else:
        return f"🎯 {nifty_tag}Amit Ki Baat: {title_word.title()} — {date_tag} #Shorts"


def build_youtube_description(script_data, today_str):
    desc_clean  = script_data.get("description", "Daily trading insight by Amit.")
    display     = script_data.get("display_text", "")
    nifty_cmp   = script_data.get("nifty_cmp", 0)
    nifty_pct   = script_data.get("nifty_pct", 0.0)
    nifty_line  = f"📊 Nifty closed today at {nifty_cmp:,.0f} ({nifty_pct:+.2f}%)\n\n" if nifty_cmp else ""
    tags        = seo.get_video_tags(mode=CONTENT_MODE, is_short=True)
    hashtag_str = " ".join([f"#{t}" for t in tags[:15]])
    _fn         = _funnel(lang="hi")
    funnel      = f"{_fn}\n" if _fn else "🌐 https://ai360trading.in\n📱 https://t.me/ai360trading\n"

    if CONTENT_MODE == "holiday":
        label = HOLIDAY_NAME if HOLIDAY_NAME else "Market Holiday"
        desc  = (
            f"🎉 {label} Special — Market band hai, learning nahi!\n\n"
            f"💡 {desc_clean}\n\n"
            f'✦ "{display}"\n\n'
            f"🌍 For investors: India, USA, UK, Brazil & UAE\n"
            f"{funnel}"
            f"⚠️ Educational only. Not financial advice.\n\n"
            f"👍 Like • 🔔 Subscribe • 📤 Share with a friend\n"
            f"#AmitKiBaat #ai360trading #HolidayLearning {hashtag_str}"
        )
    elif CONTENT_MODE == "weekend":
        desc = (
            f"📚 Weekend Learning Special\n\n"
            f"💡 {desc_clean}\n\n"
            f'✦ "{display}"\n\n'
            f"🌍 For investors: India, USA, UK, Brazil & UAE\n"
            f"{funnel}"
            f"⚠️ Educational only. Not financial advice.\n\n"
            f"👍 Like • 🔔 Subscribe • 📤 Share with a friend\n"
            f"#AmitKiBaat #WeekendWisdom #ai360trading {hashtag_str}"
        )
    else:
        desc = (
            f"🎯 Amit Ki Baat — Daily trading insight\n\n"
            f"{nifty_line}"
            f"💡 {desc_clean}\n\n"
            f'✦ "{display}"\n\n'
            f"🌍 For traders: India, USA, UK, Brazil & UAE\n"
            f"{funnel}"
            f"⚠️ Educational only. Not SEBI registered.\n\n"
            f"👍 Like • 🔔 Subscribe • 📤 Share with a trader friend\n"
            f"#AmitKiBaat #StockMarket #ai360trading {hashtag_str}"
        )
    return desc


# ─── TTS ──────────────────────────────────────────────────────────────────────

async def generate_tts(text, output_path):
    # Edge TTS (wss://speech.platform.bing.com) intermittently returns 503 /
    # WSServerHandshakeError. Retry with backoff so a transient blip self-heals
    # in-run instead of failing the whole job.
    last_err = None
    for attempt in range(1, 5):  # 4 tries: 5/15/30s backoff
        try:
            await edge_tts.Communicate(text, VOICE, rate="+5%").save(str(output_path))
            if os.path.exists(str(output_path)) and os.path.getsize(str(output_path)) > 0:
                return
            raise RuntimeError("edge_tts produced empty audio file")
        except Exception as e:
            last_err = e
            print(f"  [TTS] attempt {attempt}/4 failed: {e}")
            if attempt < 4:
                await asyncio.sleep([5, 15, 30][attempt - 1])
    raise RuntimeError(f"TTS failed after 4 attempts: {last_err}")

# Spoken engagement CTA appended to the voiced script (shares + subs lift reach).
_AUDIO_CTA_HI = " Video pasand aaye toh like, share aur subscribe zaroor karein."
def _with_cta(text: str) -> str:
    s   = (text or "").strip()
    low = s.lower()
    if "like" in low and ("share" in low or "subscribe" in low):
        return s
    return (s + _AUDIO_CTA_HI).strip()


# ─── VIDEO COMPOSITION — NO BACKGROUND MUSIC ──────────────────────────────────

def compose_video(frame_path, audio_path, output_path, spoken_text="", hook_text=""):
    """
    Compose final reel — TTS voice only, no background music.
    Music removed in v2.1 to prevent Meta muting in countries
    where Meta does not have music rights.

    v2.3: optional bold-text HOOK intro (fail-open) so the in-feed cover
    stops the scroll on YouTube/Instagram/Facebook. Narration is shifted to
    start after the hook so burned-in captions stay synced.
    """
    audio_clip = AudioFileClip(str(audio_path))
    duration   = audio_clip.duration + 0.5

    video = ImageClip(str(frame_path)).set_duration(duration)

    # Build an .srt subtitle track (for YouTube auto-translate), offset by the
    # hook so it stays synced with the shifted narration. Fail-open.
    if spoken_text:
        try:
            from subtitle_helper import build_srt
            from hook_helper import HOOK_SECONDS
            build_srt(spoken_text, audio_clip.duration,
                      str(Path(output_path).with_suffix(".srt")),
                      start_offset=(HOOK_SECONDS if hook_text else 0.0))
        except Exception as e:
            print(f"  subtitle skipped (fail-open): {e}")

    _cap_fonts = [FONT_BOLD,
                  "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                  "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", FONT_REG]

    # Burned-in captions (muted-autoplay retention + accessibility). Fail-open:
    # any caption error leaves the original caption-less reel untouched.
    if spoken_text:
        try:
            from caption_helper import add_captions
            video = add_captions(video, spoken_text, audio_clip.duration, (SW, SH), _cap_fonts)
        except Exception as e:
            print(f"  captions unavailable, rendering without (fail-open): {e}")

    # Bold-text HOOK intro (fail-open → falls back to the hook-less reel).
    final = None
    if hook_text:
        try:
            from hook_helper import build_hook_frame, prepend_hook
            hook_png = build_hook_frame(
                hook_text, (SW, SH), _cap_fonts, accent=(255, 200, 0),
                out_path=str(OUT / "zeno_reel_hook.png"))
            final = prepend_hook(video, audio_clip, hook_png, (SW, SH))
            print("  ✅ Hook intro prepended (evening reel)")
        except Exception as e:
            print(f"  ⚠️ Hook intro skipped (fail-open): {e}")
            final = None
    if final is None:
        final = video.set_audio(audio_clip)

    # NOTE: No bgmusic — TTS only
    final.write_videofile(
        str(output_path), fps=FPS, codec="libx264",
        audio_codec="aac", verbose=False, logger=None
    )
    print(f"Reel exported: {output_path} — voice only, no bgmusic")


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
        "srt_path":     str(OUT / f"reel_{today_str}.srt"),
        "srt_lang":     "hi",
        "emotion":      script_data.get("emotion", "thinking"),
        "content_mode": CONTENT_MODE,
        "music":        "none — TTS voice only",
        "sentiment":    script_data.get("sentiment", "neutral"),
        "nifty_level":  script_data.get("nifty_cmp", 0),
        "nifty_pct":    script_data.get("nifty_pct", 0.0),
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

    print(f"Generating evening reel (Amit) — {today_str} | Mode: {CONTENT_MODE.upper()}")

    # Step 1: Script (includes a real NIFTY snapshot — see fetch_eod_snapshot())
    script     = generate_script()
    emotion    = script.get("emotion", "thinking")
    title      = script.get("title", "TRADING WISDOM")
    display    = script.get("display_text", "Patience + Discipline = Success")
    audio_script = script.get("audio_script", "")
    nifty_cmp  = script.get("nifty_cmp", 0)
    nifty_pct  = script.get("nifty_pct", 0.0)

    print(f"Script ready | title: {title} | emotion: {emotion} | Nifty: {nifty_cmp or 'n/a'}")

    # Step 2: TTS audio
    spoken = _with_cta(audio_script)
    await generate_tts(spoken, audio_path)

    # Step 3: Build video frame (v2.5 — real NIFTY stat block, no ZENO)
    frame_path = build_reel_frame(title, display, emotion, nifty_cmp=nifty_cmp, nifty_pct=nifty_pct)

    # Step 4: Build thumbnail — proper CTR thumbnail, real data not a mascot
    thumb_path = build_thumbnail(title, display, emotion, nifty_cmp=nifty_cmp, nifty_pct=nifty_pct)
    print(f"Thumbnail built: {thumb_path}")

    # Step 5: Compose video — TTS only, no music (bold-text hook intro, fail-open)
    compose_video(frame_path, audio_path, video_path, spoken_text=spoken, hook_text=title)

    # Step 6: Save meta
    save_meta(script, today_str, thumb_path)

    print("=" * 50)
    print(f"EVENING REEL DONE")
    print(f"  Video:     {video_path}")
    print(f"  Thumbnail: {thumb_path}")
    print(f"  Emotion:   {emotion}")
    print(f"  Nifty:     {nifty_cmp or 'n/a'} ({nifty_pct:+.2f}%)" if nifty_cmp else "  Nifty:     n/a")
    print(f"  Music:     none (no copyright risk)")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
