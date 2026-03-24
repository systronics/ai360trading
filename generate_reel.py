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
from pathlib import Path
from datetime import datetime
import numpy as np
from PIL import Image as PilImage

# ─── CONFIG ───────────────────────────────────────────────────────────────────
GROQ_API_KEY    = os.environ["GROQ_API_KEY"]
ZENO_IMAGE_DIR  = Path("public/image")          
OUTPUT_DIR      = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

BACKGROUND_MUSIC_DIR = Path("assets/music")     
FONT_PATH        = Path("assets/fonts/Kalpana.ttf")  

TOPICS_WEEKDAY = ["patience aur mehnat ka phal", "sach bolne ki takat", "dosto ki ahmiyat", "asafalta se seekhna", "khud par bharosa"]
TOPICS_WEEKEND = ["apni feelings samjho", "galti karna zaroori hai", "paisa sikhata hai", "zindagi mein patience"]

def is_weekend() -> bool:
    return datetime.now().weekday() >= 5

# ─── STEP 1: MARKET DATA ──────────────────────────────────────────────────────
def get_live_market_data():
    data = {}
    try:
        symbols = {"nifty": ("^NSEI", "₹"), "bitcoin": ("BTC-USD", "$"), "sp500": ("^GSPC", "$")}
        for name, (symbol, curr) in symbols.items():
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla"})
            if r.ok:
                res = r.json()["chart"]["result"][0]
                price = res["meta"]["regularMarketPrice"]
                prev = res["meta"]["previousClose"]
                pct = ((price - prev) / prev) * 100
                data[name] = {"price": f"{curr}{price:,.0f}", "change": f"{pct:+.2f}%", "up": pct >= 0}
    except:
        data = {"nifty": {"price": "₹24,000", "change": "+0.5%", "up": True}}
    return data

# ─── STEP 2: GROQ SCRIPT ──────────────────────────────────────────────────────
def generate_script(topic: str, market_data: dict) -> dict:
    nifty_line = f"Nifty {market_data['nifty']['price']} pe hai" if "nifty" in market_data else ""
    prompt = f"Create a 60s Hinglish ZENO reel script about {topic}. {nifty_line}. Return ONLY JSON: {{'script':'...', 'subtitles':[], 'emotion':'...'}}"
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "llama-3.3-70b-versatile",
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "You are ZENO, a wise pixel-art kid. Output JSON ONLY."},
            {"role": "user", "content": prompt}
        ]
    }
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    return json.loads(r.json()["choices"][0]["message"]["content"])

# ─── STEP 3: VOICE ────────────────────────────────────────────────────────────
async def generate_voice(script: str, output_path: Path):
    import edge_tts
    await edge_tts.Communicate(script, "hi-IN-MadhurNeural").save(str(output_path))

# ─── STEP 5: VIDEO ENGINE ─────────────────────────────────────────────────────
def make_ken_burns(image_path: Path, seg_duration: float, effect: str):
    from moviepy.editor import ImageClip
    from moviepy.video.fx.all import fadein, fadeout
    
    img = PilImage.open(str(image_path)).convert("RGBA")
    canvas_w, canvas_h = 1080, 1920
    img_ratio = img.width / img.height
    new_h = 900
    new_w = int(new_h * img_ratio)
    img = img.resize((new_w, new_h), PilImage.LANCZOS)

    canvas = PilImage.new("RGBA", (canvas_w, canvas_h), (18, 20, 35, 255))
    canvas.paste(img, ((canvas_w - new_w) // 2, 400), img)
    frame = np.array(canvas.convert("RGB"))

    def get_frame(t):
        progress = t / seg_duration
        scale = 1.0 + (0.1 * progress if effect == "zoom_in" else 0.1 * (1 - progress))
        h, w = frame.shape[:2]
        resized = PilImage.fromarray(frame).resize((int(w*scale), int(h*scale)), PilImage.LANCZOS)
        res_arr = np.array(resized)
        # Crop to original size
        y_start = (res_arr.shape[0] - h) // 2
        x_start = (res_arr.shape[1] - w) // 2
        return res_arr[y_start:y_start+h, x_start:x_start+w]

    return ImageClip(get_frame(0)).set_duration(seg_duration).fx(fadein, 0.5).fx(fadeout, 0.5)

def assemble_video(zeno_images, voice_path, subtitles, market_data, output_path, topic):
    from moviepy.editor import (ImageClip, AudioFileClip, CompositeVideoClip, 
                                TextClip, ColorClip, CompositeAudioClip)
    from moviepy.audio.fx.all import volumex

    # 1. Load Audio
    voice_audio = AudioFileClip(str(voice_path))
    duration = voice_audio.duration

    # 2. Background & ZENO
    bg = ColorClip(size=(1080, 1920), color=[18, 20, 35], duration=duration)
    effects = ["zoom_in", "zoom_out", "zoom_in"]
    seg_dur = duration / len(zeno_images)
    clips = [bg]

    for i, img_path in enumerate(zeno_images):
        seg = make_ken_burns(img_path, seg_dur, effects[i % 3]).set_start(i * seg_dur)
        clips.append(seg)

    # 3. Background Music (Ducking Logic)
    final_audio_tracks = [voice_audio]
    if BACKGROUND_MUSIC_DIR.exists():
        music_files = list(BACKGROUND_MUSIC_DIR.glob("*.mp3"))
        if music_files:
            # Music volume is 10% (0.1) so voice is clear
            bg_music = AudioFileClip(str(random.choice(music_files))).subclip(0, duration).fx(volumex, 0.1)
            final_audio_tracks.append(bg_music)
    
    final_audio = CompositeAudioClip(final_audio_tracks)

    # 4. Text Overlays (Subtitles & Title)
    try:
        title = TextClip(f"✨ {topic.upper()}", fontsize=50, color="#FFD700", size=(900, None), method="caption").set_position(("center", 150)).set_duration(duration)
        clips.append(title)
        
        if subtitles:
            sub_dur = duration / len(subtitles)
            for i, line in enumerate(subtitles):
                s = TextClip(line, fontsize=60, color="white", size=(950, None), method="caption", stroke_color="black", stroke_width=2).set_position(("center", 1500)).set_start(i * sub_dur).set_duration(sub_dur)
                clips.append(s)
    except Exception as e:
        print(f"Overlay error: {e}")

    # 5. Export
    final_video = CompositeVideoClip(clips, size=(1080, 1920)).set_audio(final_audio)
    final_video.write_videofile(str(output_path), fps=24, codec="libx264", audio_codec="aac", logger=None)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
async def main():
    today = datetime.now().strftime("%Y%m%d")
    m_data = get_live_market_data()
    topic = random.choice(TOPICS_WEEKDAY)
    script = generate_script(topic, m_data)
    
    v_path = OUTPUT_DIR / f"voice_{today}.mp3"
    await generate_voice(script["script"], v_path)
    
    # Assuming zeno_images logic from your previous script
    all_imgs = list(ZENO_IMAGE_DIR.glob("*.png"))
    zeno_imgs = [random.choice(all_imgs) for _ in range(3)] 
    
    out_video = OUTPUT_DIR / f"reel_{today}.mp4"
    assemble_video(zeno_imgs, v_path, script.get("subtitles", []), m_data, out_video, topic)

if __name__ == "__main__":
    asyncio.run(main())
