"""
AI360Trading — Part 2: Education Video (Updated with Zeno Shorts Logic)
=======================================
Smart topic rotation from content_calendar.py
Uploads to YouTube, links back to Part 1 analysis video
Handles both 16:9 Landscape and 9:16 Zeno-themed Shorts
"""

import os, sys, json, asyncio, textwrap, re, random
from datetime import datetime

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from groq import Groq
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from content_calendar import get_todays_education_topic

# --- CONFIGURATION & ENV DETECTION ---
OUT  = "output"
os.makedirs(OUT, exist_ok=True)

# Detect if the script is being called for a Short (9:16) or Video (16:9)
IS_SHORT = os.environ.get("VIDEO_TYPE") == "SHORT"
W, H = (1080, 1920) if IS_SHORT else (1920, 1080)

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

FONT_BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
             "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
             "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"]
FONT_REG  = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
             "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
             "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"]

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

ET = {
    "Options":            {"bg_top":(20,5,35),"bg_bot":(35,10,60),"accent":(180,100,255),"text":(248,240,255),"subtext":(195,165,235)},
    "Technical Analysis":    {"bg_top":(5,20,35),"bg_bot":(8,35,65),"accent":(0,180,255),"text":(235,248,255),"subtext":(155,195,230)},
    "Fundamental Analysis": {"bg_top":(5,30,15),"bg_bot":(8,55,25),"accent":(0,220,130),"text":(235,255,245),"subtext":(150,215,180)},
    "Trading Strategy":     {"bg_top":(30,20,5),"bg_bot":(55,35,8),"accent":(255,170,0),"text":(255,250,235),"subtext":(230,200,150)},
    "Psychology":           {"bg_top":(30,5,20),"bg_bot":(55,8,35),"accent":(255,80,150),"text":(255,238,248),"subtext":(230,165,200)},
    "Risk Management":      {"bg_top":(35,10,5),"bg_bot":(60,20,8),"accent":(255,120,50),"text":(255,245,238),"subtext":(230,185,160)},
    "Global Macro":         {"bg_top":(5,25,40),"bg_bot":(8,45,70),"accent":(0,200,255),"text":(230,248,255),"subtext":(145,200,235)},
    "Crypto":               {"bg_top":(25,10,5),"bg_bot":(50,20,8),"accent":(255,150,0),"text":(255,248,235),"subtext":(230,195,145)},
    "Commodities":          {"bg_top":(25,20,5),"bg_bot":(50,40,8),"accent":(220,190,0),"text":(255,252,230),"subtext":(225,205,140)},
    "Personal Finance":     {"bg_top":(5,30,25),"bg_bot":(8,55,45),"accent":(0,230,180),"text":(235,255,250),"subtext":(150,215,200)},
    "Sector Analysis":      {"bg_top":(5,25,30),"bg_bot":(8,45,55),"accent":(0,210,200),"text":(235,255,254),"subtext":(150,210,205)},
    "News & Events":        {"bg_top":(25,25,5),"bg_bot":(45,45,8),"accent":(220,220,0),"text":(255,255,235),"subtext":(215,215,150)},
}
DEFAULT_THEME = {"bg_top":(5,20,35),"bg_bot":(8,35,65),"accent":(0,180,255),"text":(235,248,255),"subtext":(155,195,230)}

def get_zeno_overlay(category):
    """Retrieves the Zeno image for vertical shorts"""
    mapping = {
        "Psychology": "zeno_thinking.png",
        "Risk Management": "zeno_thinking.png",
        "Options": "zeno_happy.png",
        "Technical Analysis": "zeno_happy.png"
    }
    img_name = mapping.get(category, "zeno_happy.png")
    full_path = f"public/image/{img_name}"
    if os.path.exists(full_path):
        return Image.open(full_path).convert("RGBA")
    return None

def make_edu_slide(slide, idx, total, topic_title, category, level, path):
    th = ET.get(category, DEFAULT_THEME)
    img = gbg(th["bg_top"], th["bg_bot"]); draw = ImageDraw.Draw(img, "RGBA")
    
    if IS_SHORT:
        # --- VERTICAL SHORT LAYOUT (Zeno Enabled) ---
        draw.rectangle([(0,0),(W,10)], fill=th["accent"])
        draw.text((W//2, 120), f"{category.upper()}", fill=th["subtext"], font=font(FONT_BOLD, 35), anchor="mm")
        
        heading = slide.get("title", slide.get("heading", ""))
        ty = 280
        for line in textwrap.wrap(heading.upper(), width=18):
            draw.text((W//2, ty), line, fill=th["text"], font=font(FONT_BOLD, 65), anchor="mm")
            ty += 75
        
        ty += 60
        content = slide["content"].split(".")[0] + "." # Shorter for reels/shorts
        for line in textwrap.wrap(content, width=32):
            draw.text((W//2, ty), line, fill=th["text"], font=font(FONT_REG, 42), anchor="mm")
            ty += 55

        zeno = get_zeno_overlay(category)
        if zeno:
            zeno.thumbnail((650, 650), Image.LANCZOS)
            img.paste(zeno, (W//2 - 325, H - 850), zeno)

        draw.text((W//2, H-100), "AI360Trading • ai360trading.in", fill=(*th["subtext"][:3], 150), font=font(FONT_REG, 28), anchor="mm")

    else:
        # --- ORIGINAL HORIZONTAL VIDEO LAYOUT ---
        draw.rectangle([(0,0),(920,H)], fill=(*th["bg_top"],140))
        draw.rectangle([(0,0),(W,7)], fill=th["accent"])
        lc={"Beginner":(0,200,100),"Intermediate":(255,170,0),
            "Advanced":(255,70,70),"All Levels":(80,180,255)}.get(level,(100,180,255))
        draw.text((50,24),f"EDUCATION  •  {category.upper()}",fill=th["subtext"],font=font(FONT_BOLD,20))
        draw.rounded_rectangle([(680,14),(860,50)],radius=7,fill=lc)
        draw.text((770,32),level.upper(),fill=(10,10,10),font=font(FONT_BOLD,20),anchor="mm")
        draw.text((50,56),topic_title,fill=(*th["subtext"][:3],180),font=font(FONT_REG,20))
        heading=slide.get("title",slide.get("heading",""))
        ty=88
        for line in textwrap.wrap(heading.upper(),width=24)[:2]:
            draw.text((50,ty),line,fill=th["text"],font=font(FONT_BOLD,50)); ty+=62
        draw.rectangle([(50,ty+4),(480,ty+8)],fill=th["accent"]); ty+=22
        for sent in [s.strip() for s in slide["content"].split(".") if s.strip()][:6]:
            for ln in textwrap.wrap(sent+".",width=46):
                if ty>H-110: break
                draw.text((50,ty),ln,fill=th["text"],font=font(FONT_REG,28)); ty+=44
            ty+=3
        draw.text((50,H-60),"AI360Trading  •  ai360trading.in",fill=(*th["subtext"][:3],150),font=font(FONT_REG,17))
        draw.text((50,H-38),"Educational only. Not financial advice.",fill=(*th["subtext"][:3],100),font=font(FONT_REG,17))
        draw.rectangle([(922,0),(926,H)],fill=(*th["accent"][:3],50))
        draw.text((1450,145),f"{idx}",fill=(*th["accent"][:3],28),font=font(FONT_BOLD,220),anchor="mm")
        draw.rounded_rectangle([(960,375),(1900,795)],radius=20,fill=(0,0,0,100))
        draw.text((1430,415),"KEY TAKEAWAYS",fill=th["accent"],font=font(FONT_BOLD,24),anchor="mm")
        nums="①②③④"
        pts=[s.strip() for s in slide["content"].split(".") if s.strip()][:4]
        pt_y=458
        for i,pt in enumerate(pts):
            short=(pt[:60]+"...") if len(pt)>60 else pt
            draw.rounded_rectangle([(978,pt_y-6),(1882,pt_y+44)],radius=8,fill=(*th["accent"][:3],20))
            draw.text((1000,pt_y+18),f"{nums[i]}  {short}",fill=th["text"],font=font(FONT_REG,24),anchor="lm")
            pt_y+=72
        prog=int(860*(idx/total))
        draw.rectangle([(960,835),(1820,852)],fill=(255,255,255,30))
        draw.rectangle([(960,835),(960+prog,852)],fill=th["accent"])
        draw.text((1390,872),f"Lesson {idx} of {total}",fill=th["subtext"],font=font(FONT_REG,24),anchor="mm")
    
    img.save(path,quality=95)

def make_intro_slide(topic, path):
    th = ET.get(topic["category"], DEFAULT_THEME)
    img = gbg(th["bg_top"], th["bg_bot"]); draw = ImageDraw.Draw(img, "RGBA")
    if IS_SHORT:
        draw.text((W//2, H//3), "AI360TRADING", fill=th["accent"], font=font(FONT_BOLD, 80), anchor="mm")
        draw.text((W//2, H//3 + 100), topic["title"].upper(), fill=th["text"], font=font(FONT_BOLD, 50), anchor="mm")
    else:
        draw.rectangle([(0,0),(W,7)], fill=th["accent"])
        draw.text((W//2,100),"AI360Trading",fill=th["accent"],font=font(FONT_BOLD,88),anchor="mm")
        draw.text((W//2,185),"Financial Education Series",fill=th["text"],font=font(FONT_BOLD,40),anchor="mm")
        draw.rectangle([(W//2-340,218),(W//2+340,225)],fill=th["accent"])
        lc={"Beginner":(0,200,100),"Intermediate":(255,170,0),"Advanced":(255,70,70),"All Levels":(80,180,255)}.get(topic["level"],(100,180,255))
        draw.rounded_rectangle([(W//2-180,255),(W//2+180,295)],radius=10,fill=lc)
        draw.text((W//2,275),f"{topic['level'].upper()}  •  {topic['category'].upper()}",fill=(10,10,10),font=font(FONT_BOLD,22),anchor="mm")
        ty=330
        for line in textwrap.wrap(topic["title"].upper(),width=28)[:2]:
            draw.text((W//2,ty),line,fill=th["text"],font=font(FONT_BOLD,62),anchor="mm"); ty+=72
        draw.text((W//2,ty+20),f"Target: {topic.get('target_audience','Global')}",fill=(*th["subtext"][:3],200),font=font(FONT_REG,28),anchor="mm")
        draw.text((W//2,H-60),datetime.now().strftime("%A, %d %B %Y"),fill=(*th["subtext"][:3],180),font=font(FONT_REG,28),anchor="mm")
    img.save(path,quality=95)

def make_outro_slide(topic, analysis_url, path):
    th = ET.get(topic["category"], DEFAULT_THEME)
    img = gbg(th["bg_top"], th["bg_bot"]); draw = ImageDraw.Draw(img, "RGBA")
    if IS_SHORT:
        draw.text((W//2, H//2), "SUBSCRIBE FOR MORE", fill=th["accent"], font=font(FONT_BOLD, 60), anchor="mm")
    else:
        draw.rectangle([(0,0),(W,7)],fill=th["accent"])
        draw.text((W//2,160),"AI360Trading",fill=th["accent"],font=font(FONT_BOLD,88),anchor="mm")
        draw.rectangle([(W//2-320,220),(W//2+320,226)],fill=th["accent"])
        draw.text((W//2,295),"LIKE  •  SUBSCRIBE  •  SHARE",fill=(215,230,255),font=font(FONT_BOLD,44),anchor="mm")
        draw.text((W//2,438),f"Watch Part 1: {analysis_url}",fill=(*th["accent"][:3],200),font=font(FONT_REG,26),anchor="mm")
    img.save(path,quality=95)

def make_thumbnail(topic, path):
    TW, TH = 1280, 720
    th = ET.get(topic["category"], DEFAULT_THEME)
    img = Image.new("RGB",(TW,TH)); px=img.load()
    for y in range(TH):
        c=lerp(th["bg_top"],th["bg_bot"],y/TH)
        for x in range(TW): px[x,y]=c
    draw = ImageDraw.Draw(img,"RGBA")
    draw.rectangle([(0,0),(18,TH)],fill=th["accent"])
    draw.text((50,45),"AI360Trading",fill=(255,255,255),font=font(FONT_BOLD,52),anchor="lm")
    ty=200
    for line in textwrap.wrap(topic["title"],width=22)[:2]:
        draw.text((50,ty),line,fill=(255,255,255),font=font(FONT_BOLD,64)); ty+=78
    img.save(path,quality=98)

def build_title(topic):
    cat=topic["category"]; lvl=topic["level"]
    title_raw=re.sub(r'[^a-zA-Z0-9 \-]','',topic["title"]).strip()[:55]
    date_str=datetime.now().strftime("%d %b %Y")
    return f"{title_raw} | {cat} | {lvl} | {date_str}"[:100]

def build_description(topic, analysis_url):
    return f"📚 Trading Education — {datetime.now().strftime('%d %B %Y')}\n\nTOPIC: {topic['title']}\nPart 1: {analysis_url}"

def build_prompt(topic):
    slides_info="\n".join([f"Slide {i+1}: {s.get('heading','')} — Points: {'; '.join(s.get('points',[]))}"
                            for i,s in enumerate(topic["slides"])])
    return f"""You are a world-class financial educator. 
TOPIC: {topic['title']} | CATEGORY: {topic['category']} | LEVEL: {topic['level']}
SLIDES: {slides_info}
Return a JSON object with "slides" list containing "title", "content" (6 sentences), and "sentiment": "neutral"."""

async def tts(text, path):
    voices=["en-IN-PrabhatNeural","en-IN-NeerjaNeural"]
    await edge_tts.Communicate(text, random.choice(voices)).save(path)

def upload_video(video_path, topic, analysis_url, analysis_video_id):
    if not os.path.exists("token.json"): return None
    try:
        creds = Credentials.from_authorized_user_file("token.json")
        yt = build("youtube","v3",credentials=creds)
        req = yt.videos().insert(
            part="snippet,status",
            body={
                "snippet":{"title":build_title(topic),"description":build_description(topic, analysis_url),"categoryId":"27"},
                "status":{"privacyStatus":"public","selfDeclaredMadeForKids":False},
            },
            media_body=MediaFileUpload(video_path,chunksize=-1,resumable=True),
        )
        resp=req.execute(); vid_id=resp["id"]
        print(f"✅ Uploaded: {vid_id}")
        return vid_id
    except Exception as e:
        print(f"❌ Upload failed: {e}"); return None

async def run():
    topic = get_todays_education_topic()
    gkey = os.environ.get("GROQ_API_KEY")
    if not gkey: sys.exit("❌ GROQ_API_KEY not set")
    client = Groq(api_key=gkey)

    resp = client.chat.completions.create(
        messages=[{"role":"system", "content": "Return JSON only."}, {"role":"user","content":build_prompt(topic)}],
        model="llama-3.3-70b-versatile", response_format={"type":"json_object"})
    slides = json.loads(resp.choices[0].message.content)["slides"]

    clips = []
    # Intro
    ip, ap = f"{OUT}/intro.png", f"{OUT}/intro.mp3"
    make_intro_slide(topic, ip)
    await tts(f"Welcome. Today's topic is {topic['title']}.", ap)
    ia=AudioFileClip(ap); clips.append(ImageClip(ip).set_duration(ia.duration+1).set_audio(ia))

    # Slides
    for i,s in enumerate(slides):
        ip,ap=f"{OUT}/e{i:02d}.png",f"{OUT}/e{i:02d}.mp3"
        make_edu_slide(s, i+1, len(slides), topic["title"], topic["category"], topic["level"], ip)
        await tts(f"{s.get('title','')}. {s['content']}", ap)
        au=AudioFileClip(ap); clips.append(ImageClip(ip).set_duration(au.duration+1).set_audio(au))

    # Outro
    op,oap=f"{OUT}/outro.png",f"{OUT}/outro.mp3"
    make_outro_slide(topic, "Channel", op)
    await tts("Thanks for watching. Subscribe for more.", oap)
    oa=AudioFileClip(oap); clips.append(ImageClip(op).set_duration(oa.duration+1).set_audio(oa))

    final=f"{OUT}/education_video.mp4"
    concatenate_videoclips(clips,method="compose").write_videofile(final,fps=24,codec="libx264",audio_codec="aac")
    
    if not IS_SHORT:
        make_thumbnail(topic, f"{OUT}/thumbnail_education.png")
        upload_video(final, topic, "https://youtube.com", None)

if __name__ == "__main__":
    asyncio.run(run())
