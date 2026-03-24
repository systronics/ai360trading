"""
AI360Trading — Part 2: Education Video
=======================================
Smart topic rotation from content_calendar.py
Uploads to YouTube, links back to Part 1 analysis video
Best SEO: ranks for beginner trading education searches worldwide
"""

import os, sys, json, asyncio, textwrap, re
from datetime import datetime

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from groq import Groq
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from content_calendar import get_todays_education_topic

OUT  = "output"
W, H = 1920, 1080
os.makedirs(OUT, exist_ok=True)

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
    "Options":              {"bg_top":(20,5,35),"bg_bot":(35,10,60),"accent":(180,100,255),"text":(248,240,255),"subtext":(195,165,235)},
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

def make_edu_slide(slide, idx, total, topic_title, category, level, path):
    th = ET.get(category, DEFAULT_THEME)
    img = gbg(th["bg_top"], th["bg_bot"]); draw = ImageDraw.Draw(img, "RGBA")
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
    draw.text((W//2,H-32),"Educational only. Not financial advice.",fill=(*th["subtext"][:3],100),font=font(FONT_REG,20),anchor="mm")
    img.save(path,quality=95)

def make_outro_slide(topic, analysis_url, path):
    th = ET.get(topic["category"], DEFAULT_THEME)
    img = gbg(th["bg_top"], th["bg_bot"]); draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0,0),(W,7)],fill=th["accent"])
    draw.text((W//2,160),"AI360Trading",fill=th["accent"],font=font(FONT_BOLD,88),anchor="mm")
    draw.rectangle([(W//2-320,220),(W//2+320,226)],fill=th["accent"])
    draw.text((W//2,295),"LIKE  •  SUBSCRIBE  •  SHARE",fill=(215,230,255),font=font(FONT_BOLD,44),anchor="mm")
    draw.text((W//2,378),"New education topic every weekday",fill=(135,175,238),font=font(FONT_REG,30),anchor="mm")
    draw.text((W//2,438),f"Watch Part 1: {analysis_url}",fill=(*th["accent"][:3],200),font=font(FONT_REG,26),anchor="mm")
    draw.text((W//2,510),"#StockMarket #TradingEducation #FinancialFreedom #AI360Trading",fill=(60,105,165),font=font(FONT_REG,24),anchor="mm")
    draw.text((W//2,H-32),"Disclaimer: Educational only. Not financial advice.",fill=(55,78,118),font=font(FONT_REG,20),anchor="mm")
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
    draw.rectangle([(0,0),(TW,14)],fill=th["accent"])
    draw.rectangle([(0,TH-14),(TW,TH)],fill=th["accent"])
    draw.text((50,45),"AI360Trading",fill=(255,255,255),font=font(FONT_BOLD,52),anchor="lm")
    draw.text((TW-40,45),datetime.now().strftime("%d %b %Y"),fill=(180,200,240),font=font(FONT_REG,32),anchor="rm")
    lc={"Beginner":(0,200,100),"Intermediate":(255,170,0),"Advanced":(255,70,70),"All Levels":(80,180,255)}.get(topic["level"],(100,180,255))
    draw.rounded_rectangle([(40,120),(260,165)],radius=10,fill=lc)
    draw.text((150,142),topic["level"].upper(),fill=(10,10,10),font=font(FONT_BOLD,26),anchor="mm")
    ty=200
    for line in textwrap.wrap(topic["title"],width=22)[:2]:
        draw.text((50,ty),line,fill=(255,255,255),font=font(FONT_BOLD,64)); ty+=78
    draw.text((50,ty+10),topic["category"],fill=th["accent"],font=font(FONT_BOLD,36))
    draw.text((50,ty+58),f"Target: {topic.get('target_audience','Global')[:40]}",fill=(180,210,240),font=font(FONT_REG,24))
    draw.text((TW//2,TH-32),"LIKE  •  SUBSCRIBE  •  LEARN TO TRADE",fill=(*th["accent"][:3],200),font=font(FONT_BOLD,24),anchor="mm")
    img.save(path,quality=98)

def build_title(topic):
    cat=topic["category"]; lvl=topic["level"]
    title_raw=re.sub(r'[^a-zA-Z0-9 \-]','',topic["title"]).strip()[:55]
    date_str=datetime.now().strftime("%d %b %Y")
    title=f"{title_raw} | {cat} | {lvl} | {date_str}"
    return title.strip()[:100]

def build_description(topic, analysis_url):
    return f"""📚 Trading Education — {datetime.now().strftime('%d %B %Y')}

TODAY'S TOPIC: {topic['title']}
Category: {topic['category']} | Level: {topic['level']}
Who should watch: {topic.get('target_audience','All traders and investors worldwide')}

📈 WHAT YOU WILL LEARN:
{chr(10).join(f"✅ {s.get('heading','')}" for s in topic['slides'][:6])}

🎯 This education series covers:
✅ Options Trading (Calls, Puts, Greeks, Strategies)
✅ Technical Analysis (Candlesticks, RSI, MACD, Support/Resistance)
✅ Trading Psychology and Risk Management
✅ Fundamental Analysis and Global Macro
✅ Swing Trading and Intraday Strategies
✅ Crypto, Gold, Commodities

📊 Watch Part 1 (Today's Market Analysis): {analysis_url}

🌐 Website: https://ai360trading.in
📱 Telegram: https://t.me/ai360trading

This education series is designed for viewers in India, USA, UK, Brazil, UAE, and worldwide.
New topic every weekday — Monday Options, Tuesday Technical Analysis,
Wednesday Global Macro, Thursday Strategies, Friday Psychology & Risk.

⚠️ DISCLAIMER: Educational purposes only. Not financial advice.
Consult a SEBI-registered advisor (India) or regulated advisor in your country.

#TradingEducation #{topic['category'].replace(' ','')} #StockMarket #TechnicalAnalysis
#OptionsTrading #TradingStrategy #FinancialFreedom #LearnToTrade
#StockMarketForBeginners #InvestingForBeginners #AI360Trading
#TradingPsychology #RiskManagement #GlobalMarkets #Trading2025
#{topic['level'].replace(' ','')} #FinancialEducation #MoneyManagement"""

def build_prompt(topic):
    slides_info="\n".join([f"Slide {i+1}: {s.get('heading','')} — Points: {'; '.join(s.get('points',[]))}"
                            for i,s in enumerate(topic["slides"])])
    # ADDED THE WORD 'JSON' EXPLICITLY TO COMPLY WITH GROQ RULES
    return f"""You are a world-class financial educator. 
Style: clear, engaging, uses real examples.

TOPIC: {topic['title']}
CATEGORY: {topic['category']} | LEVEL: {topic['level']}

SLIDES:
{slides_info}

For each slide write:
- "title": exact heading
- "content": 6 sentences with real numbers and global examples.
- "sentiment": "neutral"

CRITICAL: Return the output as a valid JSON object.
Total: {len(topic['slides'])} slides.
Respond ONLY with JSON: {{"slides":[...]}}"""

async def tts(text, path):
    voices=["en-IN-PrabhatNeural","en-IN-NeerjaNeural"]
    import random; voice=random.choice(voices)
    await edge_tts.Communicate(text, voice).save(path)

def upload_video(video_path, topic, analysis_url, analysis_video_id):
    if not os.path.exists("token.json"):
        print("❌ token.json missing"); return None
    title = build_title(topic)
    description = build_description(topic, analysis_url)
    tags = [
        "trading education","stock market for beginners","how to trade",
        "technical analysis","options trading","trading strategy",
        "financial education","invest for beginners","stock market basics",
        "trading psychology","risk management","how to invest",
        topic["category"].lower(),topic["level"].lower(),
        "ai360trading","learn trading","trading tutorial",
        "stock market india","global markets","nifty","s&p 500",
        "trading 2025","financial freedom","passive income",
        "swing trading","intraday trading","cryptocurrency",
    ]
    try:
        creds = Credentials.from_authorized_user_file("token.json")
        yt = build("youtube","v3",credentials=creds)
        req = yt.videos().insert(
            part="snippet,status",
            body={
                "snippet":{"title":title,"description":description,"tags":tags,
                           "categoryId":"27","defaultLanguage":"en","defaultAudioLanguage":"en"},
                "status":{"privacyStatus":"public","selfDeclaredMadeForKids":False},
            },
            media_body=MediaFileUpload(video_path,chunksize=-1,resumable=True),
        )
        resp=req.execute(); vid_id=resp["id"]
        edu_url=f"https://youtube.com/watch?v={vid_id}"
        print(f"✅ Education video: {edu_url}")
        with open(f"{OUT}/education_video_id.txt","w") as f: f.write(vid_id)
        if analysis_video_id:
            try:
                vid_resp=yt.videos().list(part="snippet",id=analysis_video_id).execute()
                if vid_resp["items"]:
                    snippet=vid_resp["items"][0]["snippet"]
                    snippet["description"]+=f"\n\n▶️ WATCH PART 2 (Education): {edu_url}"
                    yt.videos().update(part="snippet",body={"id":analysis_video_id,"snippet":snippet}).execute()
                    print(f"✅ Analysis video updated with Part 2 link")
            except Exception as e:
                print(f"  Could not update Part 1 description: {e}")
        thumb=f"{OUT}/thumbnail_education.png"
        if os.path.exists(thumb):
            yt.thumbnails().set(videoId=vid_id,
                media_body=MediaFileUpload(thumb,mimetype="image/png")).execute()
        return vid_id
    except Exception as e:
        print(f"❌ Upload failed: {e}"); return None

async def run():
    topic = get_todays_education_topic()
    print(f"\n📚 Topic: {topic['title']} ({topic['category']}, {topic['level']})")

    analysis_video_id = None
    analysis_url = "https://youtube.com/@ai360trading"
    try:
        with open(f"{OUT}/analysis_video_id.txt") as f:
            analysis_video_id = f.read().strip()
            analysis_url = f"https://youtube.com/watch?v={analysis_video_id}"
        print(f"  Linking to Part 1: {analysis_url}")
    except:
        print("  Part 1 video ID not found — linking to channel")

    gkey = os.environ.get("GROQ_API_KEY")
    if not gkey: sys.exit("❌ GROQ_API_KEY not set")
    client = Groq(api_key=gkey)

    print("\n🤖 Generating education script...")
    # UPDATED SYSTEM MESSAGE TO INCLUDE THE WORD 'JSON'
    resp = client.chat.completions.create(
        messages=[
            {"role":"system", "content": "You are a helpful assistant that outputs financial education content in JSON format."},
            {"role":"user","content":build_prompt(topic)}
        ],
        model="llama-3.3-70b-versatile",
        response_format={"type":"json_object"},
        temperature=0.7, max_tokens=5000)
    slides = json.loads(resp.choices[0].message.content)["slides"]
    print(f"  ✓ {len(slides)} slides")

    clips = []

    ip,ap=f"{OUT}/intro_e.png",f"{OUT}/intro_e.mp3"
    make_intro_slide(topic, ip)
    intro_txt=(f"Welcome to AI360Trading education. "
               f"Today is {datetime.now().strftime('%A, %d %B %Y')}. "
               f"Today's topic is {topic['title']}. "
               f"This is a {topic['level']} level guide for {topic.get('target_audience','traders worldwide')}. "
               f"If you want today's live market analysis, check Part 1 in the description. Let us begin.")
    await tts(intro_txt, ap)
    ia=AudioFileClip(ap)
    clips.append(ImageClip(ip).set_duration(max(ia.duration+2,16)).set_audio(ia))

    print("\n🎬 Rendering slides...")
    for i,s in enumerate(slides):
        ip,ap=f"{OUT}/e{i:02d}.png",f"{OUT}/e{i:02d}.mp3"
        make_edu_slide(s, i+1, len(slides), topic["title"], topic["category"], topic["level"], ip)
        await tts(f"{s.get('title',s.get('heading',''))}. {s['content']}", ap)
        au=AudioFileClip(ap); dur=max(au.duration+2,32)
        clips.append(ImageClip(ip).set_duration(dur).set_audio(au))
        print(f"  ✓ [{i+1:02d}/{len(slides)}] {s.get('title','')[:40]:<40} {dur:.0f}s")

    op,oap=f"{OUT}/outro_e.png",f"{OUT}/outro_e.mp3"
    make_outro_slide(topic, analysis_url, op)
    outro_txt=(f"That completes today's education on {topic['title']}. "
               f"Watch Part 1 — today's live market analysis — link is in the description. "
               f"If this was useful please like, subscribe, and share with someone learning to trade. "
               f"New education topic every weekday. See you tomorrow. Keep learning, keep growing.")
    await tts(outro_txt, oap)
    oa=AudioFileClip(oap)
    clips.append(ImageClip(op).set_duration(max(oa.duration+2,16)).set_audio(oa))

    final=f"{OUT}/education_video.mp4"
    total_mins=sum(c.duration for c in clips)/60
    print(f"\n🎥 Rendering {len(clips)} clips — {total_mins:.1f} minutes...")
    concatenate_videoclips(clips,method="compose").write_videofile(
        final,fps=24,codec="libx264",audio_codec="aac",bitrate="4000k",logger=None)
    print(f"✅ {final} ({os.path.getsize(final)/1e6:.1f} MB) {total_mins:.1f} min")

    make_thumbnail(topic, f"{OUT}/thumbnail_education.png")
    upload_video(final, topic, analysis_url, analysis_video_id)

if __name__ == "__main__":
    asyncio.run(run())
