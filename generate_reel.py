"""
AI360 ZENO Reel Generator
Generates daily 60s moral/educational Hinglish reel with ZENO character
Pipeline: Groq script → edge-tts voice → moviepy video → upload
"""

import os
import json
import random
import asyncio
import requests
import subprocess
from pathlib import Path
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
GROQ_API_KEY    = os.environ["GROQ_API_KEY"]
ZENO_IMAGE_DIR  = Path("public/image")          # your ZENO mood images folder
OUTPUT_DIR      = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

BACKGROUND_MUSIC_DIR = Path("assets/music")     # optional: add .mp3 files here
FONT_PATH       = Path("assets/fonts/Kalpana.ttf")  # Hindi-compatible font

TOPICS_WEEKDAY = [
    "patience aur mehnat ka phal",
    "sach bolne ki takat",
    "dosto ki ahmiyat",
    "asafalta se seekhna",
    "khud par bharosa",
    "time management ki importance",
    "kindness badalta hai duniya",
    "curiosity hai sabse bada teacher",
    "family ki value",
    "positivity ka jaadu",
]

TOPICS_WEEKEND = [
    "apni feelings samjho — emotional intelligence",
    "galti karna zaroori hai — growth mindset",
    "paisa sikhata hai — financial basics for beginners",
    "zindagi mein patience ki shakti",
    "chote kadam bade sapne — consistency",
    "darr ko jeeto — fear of failure",
    "rishte aur paisa — balance in life",
    "bachat ki aadat kaise banaye",
    "apne aap se pyaar karo — self love",
    "haar maan lena bhi ek lesson hai",
]

def is_weekend() -> bool:
    return datetime.now().weekday() >= 5

MARKET_MOODS = {
    "bullish": ["happy", "excited", "confident"],
    "bearish": ["sad", "thinking", "worried"],
    "neutral": ["neutral", "curious", "calm"],
}


# ─── STEP 1: GET LIVE MARKET DATA ─────────────────────────────────────────────
def get_live_market_data():
    """Fetch live Nifty, Bitcoin, S&P500, Gold prices."""
    data = {}
    try:
        # Yahoo Finance (free, no auth)
        symbols = {
            "nifty":   ("^NSEI",  "₹"),
            "sensex":  ("^BSESN", "₹"),
            "bitcoin": ("BTC-USD","$"),
            "gold":    ("GC=F",   "$"),
            "sp500":   ("^GSPC",  "$"),
        }
        for name, (symbol, curr) in symbols.items():
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            if r.ok:
                result = r.json()["chart"]["result"]
                if result:
                    price = result[0]["meta"]["regularMarketPrice"]
                    prev  = result[0]["meta"]["previousClose"]
                    pct   = ((price - prev) / prev) * 100
                    data[name] = {
                        "price":   f"{curr}{price:,.0f}",
                        "change":  f"{pct:+.2f}%",
                        "up":      pct >= 0,
                    }
    except Exception as e:
        print(f"Market data warning: {e}")
        # Fallback placeholder
        data = {
            "nifty":   {"price": "₹24,000", "change": "+0.5%", "up": True},
            "bitcoin": {"price": "$67,000",  "change": "+1.2%", "up": True},
            "gold":    {"price": "$2,300",   "change": "-0.3%", "up": False},
            "sp500":   {"price": "$5,200",   "change": "+0.8%", "up": True},
        }
    return data


def market_mood(data):
    """Determine overall market mood from data."""
    ups = sum(1 for v in data.values() if v.get("up", True))
    total = len(data)
    if ups >= total * 0.7:  return "bullish"
    if ups <= total * 0.3:  return "bearish"
    return "neutral"


# ─── STEP 2: GROQ SCRIPT GENERATION ──────────────────────────────────────────
def generate_script(topic: str, market_data: dict) -> dict:
    """Use Groq to generate Hinglish script + subtitles."""

    nifty_line = ""
    if "nifty" in market_data:
        n = market_data["nifty"]
        b = market_data.get("bitcoin", {})
        nifty_line = (
            f"Aaj Nifty {n['price']} pe hai, {n['change']} change ke saath. "
            f"Bitcoin {b.get('price','N/A')} pe chal raha hai."
        )

    weekend = is_weekend()

    if weekend:
        prompt = f"""You are ZENO, a wise and friendly pixel-art kid character who teaches emotional
and life lessons. Create a 55-60 second Hinglish reel script for a weekend audience.

TODAY'S TOPIC: {topic}

Rules:
- Mix Hindi + English naturally (Hinglish)
- NO market data or stock prices — this is a weekend emotional/educational reel
- Start with a strong emotional hook in first 3 seconds
- Make people feel something — inspired, emotional, motivated
- End with a call to action (like/follow/comment)
- Total ~130-150 words (for 55-60s at normal speech rate)
- Tone: warm, heartfelt, like a wise friend talking to you
- Topics: life lessons, emotional growth, money mindset, self-improvement

Return ONLY a JSON object with these exact keys:
{{
  "script": "full spoken script here",
  "subtitles": ["line1 max 7 words", "line2 max 7 words", ...],
  "hook": "first 1 line hook",
  "cta": "call to action line",
  "emotion": "happy/sad/excited/thinking/worried/confident/curious/angry/greedy/neutral"
}}"""
    else:
        prompt = f"""You are ZENO, a wise and friendly pixel-art kid character who teaches moral lessons 
mixed with real market wisdom. Create a 55-60 second Hinglish reel script.

TODAY'S TOPIC: {topic}
TODAY'S MARKET: {nifty_line}

Rules:
- Mix Hindi + English naturally (Hinglish)
- Start with a hook in first 3 seconds
- Include 1 market fact naturally woven into the moral lesson
- End with a call to action (like/follow/comment)
- Total ~130-150 words (for 55-60s at normal speech rate)
- Tone: warm, educational, like talking to a younger sibling
- Avoid financial advice — only general wisdom

Return ONLY a JSON object with these exact keys:
{{
  "script": "full spoken script here",
  "subtitles": ["line1 max 7 words", "line2 max 7 words", ...],
  "hook": "first 1 line hook",
  "cta": "call to action line",
  "emotion": "happy/sad/excited/thinking/worried/confident/curious/angry/greedy/neutral"
}}"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }
    body = {
        "model":       "llama-3.3-70b-versatile",
        "temperature": 0.8,
        "max_tokens":  1000,
        "messages":    [{"role": "user", "content": prompt}],
    }
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                      headers=headers, json=body, timeout=30)
    r.raise_for_status()

    raw = r.json()["choices"][0]["message"]["content"].strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


# ─── STEP 3: EDGE-TTS VOICE GENERATION ───────────────────────────────────────
async def generate_voice(script: str, output_path: Path):
    """Generate Hinglish voice using edge-tts (free forever)."""
    import edge_tts

    # Best Hindi voices available in edge-tts
    voices = [
        "hi-IN-SwaraNeural",    # Female Hindi — natural
        "hi-IN-MadhurNeural",   # Male Hindi
    ]
    voice = voices[0]  # Change to [1] for male voice

    communicate = edge_tts.Communicate(script, voice, rate="+5%", pitch="+2Hz")
    await communicate.save(str(output_path))
    print(f"✅ Voice saved: {output_path}")


# ─── STEP 4: SELECT ZENO IMAGES (3 images for story arc) ────────────────────
def get_image(keyword: str, all_images: list, fallback: str = "zeno_happy") -> Path:
    """Find image by keyword, fallback to another keyword."""
    matches = [img for img in all_images if keyword.lower() in img.stem.lower()]
    if matches:
        return matches[0]
    matches = [img for img in all_images if fallback.lower() in img.stem.lower()]
    if matches:
        return matches[0]
    return random.choice(all_images)


def select_zeno_images(emotion: str, mood: str) -> list:
    """
    Return 3 ZENO images for beginning → middle → end story arc.
    Images tell a mini emotional journey — never random or unrelated.
    """
    if not ZENO_IMAGE_DIR.exists():
        raise FileNotFoundError(f"ZENO image dir not found: {ZENO_IMAGE_DIR}")

    all_images = list(ZENO_IMAGE_DIR.glob("*.png")) + list(ZENO_IMAGE_DIR.glob("*.jpg"))
    if not all_images:
        raise FileNotFoundError(f"No images found in {ZENO_IMAGE_DIR}")

    # Story arc map: emotion → [hook image, lesson image, end image]
    # End is ALWAYS positive (celebrating/happy) — good CTA energy
    arc_map = {
        "happy":     ["zeno_happy",       "zeno_thinking",    "zeno_celebrating"],
        "excited":   ["zeno_celebrating", "zeno_happy",       "zeno_celebrating"],
        "sad":       ["zeno_sad",         "zeno_thinking",    "zeno_happy"],
        "worried":   ["zeno_fear",        "zeno_thinking",    "zeno_happy"],
        "thinking":  ["zeno_thinking",    "zeno_curious" ,    "zeno_celebrating"],
        "confident": ["zeno_happy",       "zeno_celebrating", "zeno_celebrating"],
        "curious":   ["zeno_thinking",    "zeno_happy",       "zeno_celebrating"],
        "angry":     ["zeno_angry",       "zeno_thinking",    "zeno_happy"],
        "greedy":    ["zeno_greed",       "zeno_thinking",    "zeno_celebrating"],
        "neutral":   ["zeno_thinking",    "zeno_happy",       "zeno_celebrating"],
    }

    # Market mood override for hook image on weekdays
    if mood == "bearish" and emotion in ["happy", "excited", "confident"]:
        arc_map[emotion][0] = "zeno_worried"
    elif mood == "bullish" and emotion in ["sad", "worried"]:
        arc_map[emotion][2] = "zeno_celebrating"

    keywords = arc_map.get(emotion, arc_map["neutral"])
    images = [get_image(kw, all_images) for kw in keywords]

    print(f"   Story arc: {' → '.join(Path(img).stem for img in images)}")
    return images


# ─── STEP 5: MOVIEPY VIDEO ASSEMBLY ──────────────────────────────────────────
def make_ken_burns(image_path: Path, seg_duration: float, effect: str) -> object:
    """
    Apply Ken Burns effect to a single image segment.
    effect: "zoom_in", "zoom_out", "pan_left", "pan_right"
    Returns a moviepy clip.
    """
    from moviepy.editor import ImageClip
    from moviepy.video.fx.all import fadein, fadeout
    import numpy as np
    from PIL import Image as PilImage

    if not hasattr(PilImage, "ANTIALIAS"):
        PilImage.ANTIALIAS = PilImage.LANCZOS

    # Load and resize image to 1080x1920 canvas
    img = PilImage.open(str(image_path)).convert("RGBA")

    # Fit ZENO on dark navy background
    canvas_w, canvas_h = 1080, 1920
    img_ratio = img.width / img.height
    new_h = 900
    new_w = int(new_h * img_ratio)
    img = img.resize((new_w, new_h), PilImage.LANCZOS)

    canvas = PilImage.new("RGBA", (canvas_w, canvas_h), (18, 20, 35, 255))
    x_off  = (canvas_w - new_w) // 2
    y_off  = 400
    canvas.paste(img, (x_off, y_off), img)
    frame  = np.array(canvas.convert("RGB"))

    def make_frame(t):
        progress = t / seg_duration  # 0.0 → 1.0
        if effect == "zoom_in":
            scale = 1.0 + 0.08 * progress
        elif effect == "zoom_out":
            scale = 1.08 - 0.08 * progress
        elif effect == "pan_left":
            scale = 1.05
        else:  # pan_right
            scale = 1.05

        h, w = frame.shape[:2]
        new_w2 = int(w * scale)
        new_h2 = int(h * scale)

        resized = PilImage.fromarray(frame).resize((new_w2, new_h2), PilImage.LANCZOS)
        resized = np.array(resized)

        if effect == "pan_left":
            x_start = int((new_w2 - w) * progress)
            y_start = (new_h2 - h) // 2
        elif effect == "pan_right":
            x_start = int((new_w2 - w) * (1 - progress))
            y_start = (new_h2 - h) // 2
        else:
            x_start = (new_w2 - w) // 2
            y_start = (new_h2 - h) // 2

        x_start = max(0, min(x_start, new_w2 - w))
        y_start = max(0, min(y_start, new_h2 - h))

        return resized[y_start:y_start+h, x_start:x_start+w]

    clip = (ImageClip(make_frame, duration=seg_duration)
            .fx(fadein, 0.4)
            .fx(fadeout, 0.4))
    return clip


def assemble_video(
    zeno_images: list,
    audio_path: Path,
    subtitles: list,
    market_data: dict,
    output_path: Path,
    topic: str,
):
    """Assemble final MP4 reel with Ken Burns multi-image story arc."""
    from moviepy.editor import (
        ImageClip, AudioFileClip, CompositeVideoClip,
        TextClip, ColorClip, concatenate_videoclips
    )
    from moviepy.video.fx.all import fadein, fadeout
    import numpy as np
    import PIL.Image
    if not hasattr(PIL.Image, "ANTIALIAS"):
        PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

    audio    = AudioFileClip(str(audio_path))
    duration = audio.duration

    # ── Ken Burns segments — 3 images, each ~1/3 of video ──
    effects   = ["zoom_in", "pan_left", "zoom_out"]
    n_images  = len(zeno_images)
    seg_dur   = duration / n_images

    zeno_segments = []
    for i, img_path in enumerate(zeno_images):
        effect = effects[i % len(effects)]
        try:
            seg = make_ken_burns(img_path, seg_dur, effect)
            seg = seg.set_start(i * seg_dur)
            zeno_segments.append(seg)
            print(f"   Segment {i+1}: {Path(img_path).stem} — {effect}")
        except Exception as e:
            print(f"   Segment {i+1} failed ({e}), using static fallback")
            seg = (ImageClip(str(img_path))
                   .set_duration(seg_dur)
                   .resize(height=900)
                   .set_position(("center", 400))
                   .set_start(i * seg_dur))
            zeno_segments.append(seg)

    # ── Background ──
    bg = ColorClip(size=(1080, 1920), color=[18, 20, 35], duration=duration)
    clips = [bg] + zeno_segments

    # ── Optional background music ──
    clips_audio = [audio]
    if BACKGROUND_MUSIC_DIR.exists():
        music_files = list(BACKGROUND_MUSIC_DIR.glob("*.mp3"))
        if music_files:
            from moviepy.editor import AudioFileClip as AFC
            from moviepy.audio.fx.all import volumex
            music = (AFC(str(random.choice(music_files)))
                     .subclip(0, duration)
                     .fx(volumex, 0.08))
            from moviepy.editor import CompositeAudioClip
            audio = CompositeAudioClip([audio, music])

    # ── Top bar: Market ticker ──
    if market_data:
        ticker_parts = []
        for name, info in list(market_data.items())[:3]:
            arrow = "▲" if info.get("up") else "▼"
            ticker_parts.append(f"{name.upper()} {info['price']} {arrow}{info['change']}")
        ticker_text = "  |  ".join(ticker_parts)

        try:
            ticker = (TextClip(ticker_text, fontsize=28, color="white",
                               font="DejaVu-Sans", bg_color="#1a1a2e",
                               size=(1080, 60))
                      .set_position(("center", 60))
                      .set_duration(duration))
            clips.append(ticker)
        except Exception as e:
            print(f"Ticker skipped: {e}")

    # ── Topic title (top) ──
    try:
        font = str(FONT_PATH) if FONT_PATH.exists() else "DejaVu-Sans"
        title = (TextClip(f"✨ {topic.title()}",
                          fontsize=48, color="#FFD700",
                          font=font, method="caption", size=(900, None))
                 .set_position(("center", 140))
                 .set_duration(duration)
                 .fx(fadein, 0.5))
        clips.append(title)
    except Exception as e:
        print(f"Title skipped: {e}")

    # ── Subtitles (synced, lower third) ──
    if subtitles:
        sub_duration = duration / len(subtitles)
        for i, line in enumerate(subtitles):
            start = i * sub_duration
            try:
                font = str(FONT_PATH) if FONT_PATH.exists() else "DejaVu-Sans"
                sub = (TextClip(line, fontsize=56, color="white",
                                font=font, method="caption",
                                size=(960, None), stroke_color="black",
                                stroke_width=2)
                       .set_position(("center", 1550))
                       .set_start(start)
                       .set_duration(sub_duration)
                       .fx(fadein, 0.2)
                       .fx(fadeout, 0.2))
                clips.append(sub)
            except Exception as e:
                print(f"Subtitle {i} skipped: {e}")

    # ── Branding (bottom) ──
    try:
        brand = (TextClip("@ai360trading.in", fontsize=36,
                          color="#888888", font="DejaVu-Sans")
                 .set_position(("center", 1820))
                 .set_duration(duration))
        clips.append(brand)
    except Exception as e:
        print(f"Branding skipped: {e}")

    # ── Compose + export ──
    final = (CompositeVideoClip(clips, size=(1080, 1920))
             .set_audio(final_audio))

    final.write_videofile(
        str(output_path),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="4000k",
        preset="fast",
        threads=4,
        verbose=False,
        logger=None,
    )
    print(f"✅ Video assembled: {output_path}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
async def main():
    today = datetime.now().strftime("%Y%m%d")

    weekend = is_weekend()
    print(f"📅 Mode: {'Weekend (educational)' if weekend else 'Weekday (market+moral)'}")

    print("📊 Step 1: Fetching market data...")
    if weekend:
        market_data = {}
        mood = "neutral"
        print("   Weekend mode — skipping live market data")
    else:
        market_data = get_live_market_data()
        mood = market_mood(market_data)
        print(f"   Market mood: {mood}")
        for k, v in market_data.items():
            print(f"   {k}: {v['price']} {v['change']}")

    print("\n🧠 Step 2: Generating Hinglish script with Groq...")
    topic = random.choice(TOPICS_WEEKEND if is_weekend() else TOPICS_WEEKDAY)
    print(f"   Topic: {topic}")
    script_data = generate_script(topic, market_data)
    print(f"   Script preview: {script_data['script'][:80]}...")
    print(f"   Emotion: {script_data['emotion']}")

    print("\n🎙️ Step 3: Generating voice with edge-tts...")
    audio_path = OUTPUT_DIR / f"voice_{today}.mp3"
    await generate_voice(script_data["script"], audio_path)

    print("\n🎭 Step 4: Selecting ZENO images (story arc)...")
    zeno_images = select_zeno_images(script_data["emotion"], mood)

    print("\n🎬 Step 5: Assembling video with Ken Burns effect...")
    video_path = OUTPUT_DIR / f"reel_{today}.mp4"
    assemble_video(
        zeno_images  = zeno_images,
        audio_path   = audio_path,
        subtitles    = script_data.get("subtitles", []),
        market_data  = market_data,
        output_path  = video_path,
        topic        = topic,
    )

    # Save metadata for upload scripts
    meta = {
        "date":        today,
        "topic":       topic,
        "hook":        script_data.get("hook", ""),
        "cta":         script_data.get("cta", ""),
        "script":      script_data["script"],
        "emotion":     script_data["emotion"],
        "video_path":  str(video_path),
        "zeno_images": [str(img) for img in zeno_images],
        "market":      market_data,
    }
    meta_path = OUTPUT_DIR / f"meta_{today}.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"\n✅ Metadata saved: {meta_path}")
    print(f"✅ Video ready: {video_path}")
    return meta


if __name__ == "__main__":
    result = asyncio.run(main())
    print("\n🚀 ZENO reel generated successfully!")
    print(f"   Video: {result['video_path']}")
