import os
import json
import random
import asyncio
import requests
import numpy as np
from pathlib import Path
from datetime import datetime
from PIL import Image as PilImage

# ─── CONFIG ───────────────────────────────────────────────────────────────────
GROQ_API_KEY    = os.environ.get("GROQ_API_KEY")
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

# ─── STEP 4: VIDEO ENGINE (STATIC & FAST) ─────────────────────────────────────
def make_static_frame(image_path: Path, seg_duration: float):
    from moviepy.editor import ImageClip
    from moviepy.video.fx.all import fadein, fadeout
    
    img = PilImage.open(str(image_path)).convert("RGBA")
    canvas_w, canvas_h = 1080, 1920
    
    new_w = 850 
    new_h = int(new_w * (img.height / img.width))
    img = img.resize((new_w, new_h), PilImage.LANCZOS)

    canvas = PilImage.new("RGBA", (canvas_w, canvas_h), (18, 20, 35, 255))
    paste_y = (canvas_h - new_h) // 2 - 100
    canvas.paste(img, ((canvas_w - new_w) // 2, paste_y), img)
    
    frame_array = np.array(canvas.convert("RGB"))
    return ImageClip(frame_array).set_duration(seg_duration).fx(fadein, 0.4).fx(fadeout, 0.4)

def assemble_video(zeno_images, voice_path, subtitles, market_data, output_path, topic):
    from moviepy.editor import (ImageClip, AudioFileClip, CompositeVideoClip, 
                                TextClip, ColorClip, CompositeAudioClip)
    from moviepy.audio.fx.all import volumex

    voice_audio = AudioFileClip(str(voice_path))
    duration = voice_audio.duration
    bg = ColorClip(size=(1080, 1920), color=[15, 18, 30], duration=duration)
    
    seg_dur = duration / len(zeno_images)
    zeno_clips = []
    for i, img_path in enumerate(zeno_images):
        clip = make_static_frame(img_path, seg_dur).set_start(i * seg_dur)
        zeno_clips.append(clip)

    nifty = market_data.get('nifty', {'price': 'N/A', 'change': ''})
    ticker_text = f"NIFTY 50: {nifty['price']} ({nifty['change']})  |  ai360trading.in"
    ticker = TextClip(ticker_text, fontsize=28, color="#00FF99", bg_color="black", 
                      size=(1080, 50)).set_position(("center", 0)).set_duration(duration)

    main_title = TextClip(f"✨ {topic.upper()}", fontsize=60, color="#FFD700", 
                          method="caption", size=(900, None)).set_position(("center", 180)).set_duration(duration)
    
    sub_clips = []
    if subtitles:
        sub_gap = duration / len(subtitles)
        for i, text in enumerate(subtitles):
            s = TextClip(text, fontsize=65, color="white", stroke_color="black", stroke_width=2, 
                         method="caption", size=(950, 450)).set_position(("center", 1400)).set_start(i * sub_gap).set_duration(sub_gap)
            sub_clips.append(s)

    final_audio_list = [voice_audio]
    if BACKGROUND_MUSIC_DIR.exists():
        music_files = list(BACKGROUND_MUSIC_DIR.glob("*.mp3"))
        if music_files:
            bg_music = AudioFileClip(str(random.choice(music_files))).subclip(0, duration).fx(volumex, 0.12)
            final_audio_list.append(bg_music.audio_fadeout(2))
    
    final_video = CompositeVideoClip([bg] + zeno_clips + [ticker, main_title] + sub_clips, size=(1080, 1920))
    final_video = final_video.set_audio(CompositeAudioClip(final_audio_list))
    
    final_video.write_videofile(str(output_path), fps=24, codec="libx264", audio_codec="aac", preset="ultrafast", logger=None)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
async def main():
    try:
        today = datetime.now().strftime("%Y%m%d")
        if not GROQ_API_KEY:
            print("❌ GROQ_API_KEY missing!")
            return

        m_data = get_live_market_data()
        topic_list = TOPICS_WEEKEND if is_weekend() else TOPICS_WEEKDAY
        topic = random.choice(topic_list)
        
        script = generate_script(topic, m_data)
        v_path = OUTPUT_DIR / f"voice_{today}.mp3"
        await generate_voice(script["script"], v_path)
        
        all_imgs = list(ZENO_IMAGE_DIR.glob("*.png"))
        if not all_imgs:
            print("❌ No images in public/image!")
            return
        zeno_imgs = [random.choice(all_imgs) for _ in range(3)] 
        
        out_video = OUTPUT_DIR / f"reel_{today}.mp4"
        assemble_video(zeno_imgs, v_path, script.get("subtitles", []), m_data, out_video, topic)

        # SAVE METADATA (This fixes your FileNotFoundError)
        meta_path = OUTPUT_DIR / f"meta_{today}.json"
        meta_content = {
            "title": f"{topic.capitalize()} | AI360 ZENO #Shorts #Trading",
            "description": f"ZENO says: {topic}\nMarket: {m_data.get('nifty',{}).get('price','')}\n#AI360",
            "topic": topic,
            "date": today,
            "video_path": str(out_video)
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_content, f, indent=4)
            
        print(f"🎉 Process Complete. Metadata saved to {meta_path}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
