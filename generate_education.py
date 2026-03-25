import os, sys, json, asyncio, textwrap, random
from datetime import datetime
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from groq import Groq
from content_calendar import get_todays_education_topic

OUT = "output"
IS_SHORT = os.environ.get("VIDEO_TYPE") == "SHORT"
W, H = (1080, 1920) if IS_SHORT else (1920, 1080)
os.makedirs(OUT, exist_ok=True)

def font(c, s): return ImageFont.truetype(c[0], s) if os.path.exists(c[0]) else ImageFont.load_default()

def make_edu_slide(slide, idx, total, category, level, path):
    img = Image.new("RGB", (W,H), (20,20,40)); draw = ImageDraw.Draw(img, "RGBA")
    if IS_SHORT:
        draw.text((W//2, 120), category.upper(), fill=(180,180,255), font=font(["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"], 35), anchor="mm")
        ty = 280
        for line in textwrap.wrap(slide["title"].upper(), width=18):
            draw.text((W//2, ty), line, fill=(255,255,255), font=font(["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"], 65), anchor="mm"); ty += 75
        z_path = f"public/image/zeno_happy.png"
        if os.path.exists(z_path):
            zeno = Image.open(z_path).convert("RGBA")
            zeno.thumbnail((600,600)); img.paste(zeno, (W//2-300, H-800), zeno)
    else:
        draw.text((50,50), slide["title"], fill=(255,255,255), font=font(["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"], 50))
    img.save(path)

async def run():
    topic = get_todays_education_topic()
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Education JSON for {topic['title']}."}], response_format={"type":"json_object"})
    slides = json.loads(resp.choices[0].message.content)["slides"]
    clips = []
    for i, s in enumerate(slides):
        ip, ap = f"{OUT}/e{i}.png", f"{OUT}/e{i}.mp3"
        make_edu_slide(s, i+1, len(slides), topic["category"], topic["level"], ip)
        await edge_tts.Communicate(s["content"], "en-IN-PrabhatNeural").save(ap)
        clips.append(ImageClip(ip).set_duration(AudioFileClip(ap).duration+1).set_audio(AudioFileClip(ap)))
    concatenate_videoclips(clips, method="compose").write_videofile(f"{OUT}/education_video.mp4", fps=24)

if __name__ == "__main__": asyncio.run(run())
