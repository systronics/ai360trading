import os, sys, json, asyncio, textwrap, re, random
from datetime import datetime
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from groq import Groq

OUT = "output"
os.makedirs(OUT, exist_ok=True)

# Detect if Short or Video
IS_SHORT = os.environ.get("VIDEO_TYPE") == "SHORT"
W, H = (1080, 1920) if IS_SHORT else (1920, 1080)

if not hasattr(Image, "ANTIALIAS"): Image.ANTIALIAS = Image.LANCZOS

FONT_BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
FONT_REG  = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]

def font(c, s):
    for p in c:
        if os.path.exists(p): return ImageFont.truetype(p, s)
    return ImageFont.load_default()

def lerp(c1, c2, t): return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))
def gbg(top, bot):
    img = Image.new("RGB", (W, H)); px = img.load()
    for y in range(H):
        c = lerp(top, bot, y/H)
        for x in range(W): px[x, y] = c
    return img

AT = {
    "bullish": {"bg_top":(5,30,15),"bg_bot":(10,60,30),"accent":(0,255,130),"text":(235,255,245)},
    "bearish": {"bg_top":(35,10,10),"bg_bot":(70,20,20),"accent":(255,50,50),"text":(255,240,240)},
    "neutral": {"bg_top":(10,20,35),"bg_bot":(20,40,70),"accent":(0,180,255),"text":(240,250,255)}
}

def get_zeno(sentiment):
    mapping = {"bullish": "zeno_happy.png", "bearish": "zeno_sad.png", "neutral": "zeno_thinking.png"}
    path = f"public/image/{mapping.get(sentiment.lower(), 'zeno_thinking.png')}"
    return Image.open(path).convert("RGBA") if os.path.exists(path) else None

def make_slide(slide, idx, total, path):
    snt = slide.get("sentiment", "neutral").lower()
    th = AT.get(snt, AT["neutral"])
    img = gbg(th["bg_top"], th["bg_bot"]); draw = ImageDraw.Draw(img, "RGBA")
    
    if IS_SHORT:
        draw.rectangle([(0,0),(W,12)], fill=th["accent"])
        ty = 250
        for line in textwrap.wrap(slide["title"].upper(), width=18):
            draw.text((W//2, ty), line, fill=th["text"], font=font(FONT_BOLD, 70), anchor="mm"); ty += 85
        ty += 60
        content = slide["content"].split(".")[0] + "."
        for line in textwrap.wrap(content, width=30):
            draw.text((W//2, ty), line, fill=th["text"], font=font(FONT_REG, 45), anchor="mm"); ty += 60
        zeno = get_zeno(snt)
        if zeno:
            zeno.thumbnail((650, 650), Image.LANCZOS)
            img.paste(zeno, (W//2 - 325, H - 850), zeno)
    else:
        draw.text((80, 100), slide["title"].upper(), fill=th["text"], font=font(FONT_BOLD, 65))
        ty = 280
        for line in textwrap.wrap(slide["content"], width=50):
            draw.text((80, ty), line, fill=th["text"], font=font(FONT_REG, 35)); ty += 55

    img.save(path, quality=95)

async def tts(text, path):
    await edge_tts.Communicate(text, "en-IN-PrabhatNeural").save(path)

async def run():
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":"Market analysis JSON (title, content, sentiment) for Nifty."}], response_format={"type":"json_object"})
    slides = json.loads(resp.choices[0].message.content)["slides"]
    clips = []
    for i, s in enumerate(slides):
        ip, ap = f"{OUT}/a{i}.png", f"{OUT}/a{i}.mp3"
        make_slide(s, i+1, len(slides), ip); await tts(s["content"], ap)
        clips.append(ImageClip(ip).set_duration(AudioFileClip(ap).duration + 1).set_audio(AudioFileClip(ap)))
    concatenate_videoclips(clips, method="compose").write_videofile(f"{OUT}/analysis_video.mp4", fps=24)

if __name__ == "__main__": asyncio.run(run())
