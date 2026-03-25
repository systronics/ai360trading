import os, sys, json, asyncio, textwrap
from datetime import datetime
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, afx
from groq import Groq

OUT = "output"
W, H = 1080, 1920 
BG_MUSIC = "bg_music.mp3" # Your exact file
os.makedirs(OUT, exist_ok=True)

async def run_reels():
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":"One trading insight JSON (title, content, sentiment)."}], response_format={"type":"json_object"})
    slide = json.loads(resp.choices[0].message.content)
    
    img_p, aud_p = f"{OUT}/r.png", f"{OUT}/r.mp3"
    img = Image.new("RGB", (W,H), (10,10,30)); draw = ImageDraw.Draw(img, "RGBA")
    draw.text((W//2, 400), slide["title"].upper(), fill=(255,255,255), font=ImageFont.load_default(), anchor="mm")
    
    z_path = f"public/image/zeno_happy.png"
    if os.path.exists(z_path):
        zeno = Image.open(z_path).convert("RGBA"); zeno.thumbnail((700,700))
        img.paste(zeno, (W//2-350, H-900), zeno)
    img.save(img_p)
    
    await edge_tts.Communicate(slide["content"], "en-IN-PrabhatNeural").save(aud_p)
    voice = AudioFileClip(aud_p)
    video = ImageClip(img_p).set_duration(voice.duration + 1)
    
    if os.path.exists(BG_MUSIC):
        bg = AudioFileClip(BG_MUSIC).volumex(0.1).set_duration(video.duration)
        final_aud = CompositeAudioClip([voice, bg])
    else: final_aud = voice

    video.set_audio(final_aud).write_videofile(f"{OUT}/daily_reel.mp4", fps=24)

if __name__ == "__main__": asyncio.run(run_reels())
