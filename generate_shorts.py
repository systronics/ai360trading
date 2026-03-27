import os, sys, json, asyncio
from datetime import datetime
from pathlib import Path

import pytz
import requests
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip,
    concatenate_audioclips
)
from groq import Groq
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# ─── Content Mode ─────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")
print(f"[MODE] generate_shorts.py running in mode: {CONTENT_MODE.upper()}")

# ─── CONFIG ──────────────────────────────────────────────────────────────────
OUT       = Path("output")
MUSIC_DIR = Path("public/music")
SW, SH    = 1080, 1920
FPS       = 30
IST       = pytz.timezone("Asia/Kolkata")
now_ist   = datetime.now(IST)
os.makedirs(OUT, exist_ok=True)

BULL_GREEN  = (0, 210, 100)
BEAR_RED    = (220, 55, 55)
GOLD        = (255, 200, 50)
WHITE       = (255, 255, 255)
SOFT_WHITE  = (230, 240, 255)
ACCENT_BLUE = (60, 140, 255)

# Fonts
FONT_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
]
FONT_REG_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def gradient_bg(top, bot):
    img = Image.new("RGB", (SW, SH))
    px  = img.load()
    for y in range(SH):
        c = lerp(top, bot, y / SH)
        for x in range(SW): px[x, y] = c
    return img

def draw_text_outlined(draw, text, x, y, font, fill, outline=3, anchor="mm"):
    for dx in range(-outline, outline + 1):
        for dy in range(-outline, outline + 1):
            if dx != 0 or dy != 0:
                draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0), anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)

def get_bg_music():
    day = now_ist.weekday()
    music_map = {0:"bgmusic1.mp3",1:"bgmusic2.mp3",2:"bgmusic3.mp3",
                 3:"bgmusic1.mp3",4:"bgmusic2.mp3",5:"bgmusic3.mp3",6:"bgmusic1.mp3"}
    f = MUSIC_DIR / music_map[day]
    if f.exists(): return f
    for f in MUSIC_DIR.glob("*.mp3"): return f
    return None

def mix_audio(voice_clip, duration):
    bg_path = get_bg_music()
    if not bg_path: return voice_clip
    try:
        bg = AudioFileClip(str(bg_path))
        if bg.duration < duration:
            loops = int(duration / bg.duration) + 1
            bg = concatenate_audioclips([bg] * loops)
        bg = bg.subclip(0, duration).volumex(0.08)
        return CompositeAudioClip([voice_clip, bg])
    except Exception as e:
        print(f"⚠️ Music error: {e}")
        return voice_clip

# ─── MARKET DATA (Unified with Main Video) ───────────────────────────────────
def fetch_market_data():
    print("📡 Fetching market data...")
    # Impact: Try to load metadata from generate_analysis.py for consistency
    meta_path = OUT / f"analysis_meta_{now_ist.strftime('%Y%m%d')}.json"
    main_video_context = ""
    if meta_path.exists():
        try:
            m_data = json.loads(meta_path.read_text())
            main_video_context = m_data.get("title", "")
            print(f"✅ Consistent with Main Video: {main_video_context}")
        except: pass

    if CONTENT_MODE in ("holiday", "weekend"):
        return {
            "nifty":  {"val": "Market Holiday", "chg": "+Learn%", "up": True,  "raw": 0},
            "btc":    {"val": "Education Day",  "chg": "+Grow%",  "up": True,  "raw": 0},
            "gold":   {"val": "Plan Today",     "chg": "+Smart%", "up": True,  "raw": 0},
            "usdinr": {"val": "Invest Now",      "chg": "+₹",      "up": True,  "raw": 0},
            "sp500":  {"val": "Stay Calm",      "chg": "+Learn%", "up": True,  "raw": 0},
            "context": main_video_context
        }

    tickers = {
        "nifty":  ("^NSEI","₹"), "btc":("BTC-USD","$"),
        "gold":   ("GC=F","$"),  "usdinr":("INR=X","₹"), "sp500":("^GSPC","$"),
    }
    data = {"context": main_video_context}
    for name, (sym, curr) in tickers.items():
        try:
            df   = yf.download(sym, period="2d", interval="1d", progress=False)
            last = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2])
            chg  = ((last - prev) / prev) * 100
            val  = f"{curr}{last:.2f}" if name=="usdinr" else f"{curr}{last:,.0f}" if name in ("btc","sp500") else f"{curr}{last:,.2f}"
            data[name] = {"val": val, "chg": f"{chg:+.2f}%", "up": chg >= 0, "raw": last}
        except Exception as e:
            print(f"⚠️ {name}: {e}")
            data[name] = {"val": "N/A", "chg": "0.00%", "up": True, "raw": 0}
    return data

def get_part1_url():
    id_path = OUT / "analysis_video_id.txt"
    if id_path.exists():
        vid_id = id_path.read_text(encoding="utf-8").strip()
        if vid_id and vid_id != "UPLOAD_FAILED":
            return f"https://youtube.com/watch?v={vid_id}"
    return ""

# ─── RENDERING & SCRIPTS (Zeno-Free) ──────────────────────────────────────────
def make_short2_frame(script_data, market):
    sentiment = script_data.get("sentiment", "bullish").lower()
    accent    = GOLD if CONTENT_MODE in ("holiday","weekend") else (
                BULL_GREEN if sentiment=="bullish" else BEAR_RED if sentiment=="bearish" else GOLD)

    img  = gradient_bg((8, 12, 28), (15, 25, 50))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0,0),(SW,12)], fill=accent)
    draw.rectangle([(0,SH-12),(SW,SH)], fill=accent)

    draw_text_outlined(draw, "AI360TRADING", SW//2, 80, get_font(FONT_BOLD_PATHS,62), accent, outline=2)

    header_label = {"holiday":"HOLIDAY LEARNING","weekend":"WEEKEND EDUCATION"}.get(CONTENT_MODE,"TRADE SETUP")
    draw.text((SW//2, 145), header_label, font=get_font(FONT_BOLD_PATHS,38), fill=SOFT_WHITE, anchor="mm")
    draw.text((SW//2, 200), now_ist.strftime("%d %b %Y • %I:%M %p IST"),
              font=get_font(FONT_REG_PATHS,32), fill=(140,160,200), anchor="mm")
    draw.rectangle([(60,230),(SW-60,233)], fill=accent)

    stock = script_data.get("stock", "FINANCIAL EDUCATION" if CONTENT_MODE in ("holiday","weekend") else "NIFTY 50")
    draw_text_outlined(draw, stock.upper(), SW//2, 310, get_font(FONT_BOLD_PATHS,90), WHITE, outline=2)

    badge_icon = "📚" if CONTENT_MODE in ("holiday","weekend") else ("📈" if sentiment=="bullish" else "📉" if sentiment=="bearish" else "⚖️")
    badge = f"  {badge_icon} {sentiment.upper()}  "
    draw.rounded_rectangle([(SW//2-160,360),(SW//2+160,420)], radius=20, fill=(*accent,40))
    draw.text((SW//2,390), badge, font=get_font(FONT_BOLD_PATHS,36), fill=accent, anchor="mm")

    box_top = 460
    draw.rounded_rectangle([(60,box_top),(SW-60,box_top+420)], radius=30, fill=(255,255,255,12))

    if CONTENT_MODE in ("holiday","weekend"):
        levels = [
            ("📖 TOPIC",  script_data.get("entry","Financial Education"), WHITE),
            ("💡 LESSON", script_data.get("target","See Description"),    BULL_GREEN),
            ("🎯 ACTION", script_data.get("sl","Learn and Apply"),        GOLD),
            ("⏱ HORIZON",script_data.get("horizon","Long Term"),          ACCENT_BLUE),
        ]
    else:
        levels = [
            ("🎯 ENTRY",  script_data.get("entry","Market Price"), WHITE),
            ("📊 TARGET", script_data.get("target","See Description"), BULL_GREEN),
            ("🛑 SL",     script_data.get("sl","Risk Managed"), BEAR_RED),
            ("⏱ HORIZON",script_data.get("horizon","Intraday/Swing"), GOLD),
        ]

    ly = box_top + 60
    for label, value, color in levels:
        draw.text((120,ly), label, font=get_font(FONT_BOLD_PATHS,36), fill=(150,170,210), anchor="lm")
        draw.text((SW-120,ly), str(value), font=get_font(FONT_BOLD_PATHS,42), fill=color, anchor="rm")
        ly += 88

    strip_y = 930
    draw.rounded_rectangle([(60,strip_y),(SW-60,strip_y+100)], radius=20, fill=(0,0,0,100))
    if CONTENT_MODE in ("holiday","weekend"):
        draw.text((SW//2, strip_y+50), "📚 EDUCATION MODE", font=get_font(FONT_BOLD_PATHS,44), fill=GOLD, anchor="mm")
    else:
        nc = BULL_GREEN if market["nifty"]["up"] else BEAR_RED
        draw.text((120,strip_y+50),"NIFTY",font=get_font(FONT_BOLD_PATHS,38),fill=(160,180,220),anchor="lm")
        draw.text((SW//2,strip_y+50),market["nifty"]["val"],font=get_font(FONT_BOLD_PATHS,44),fill=WHITE,anchor="mm")
        draw.text((SW-120,strip_y+50),market["nifty"]["chg"],font=get_font(FONT_BOLD_PATHS,40),fill=nc,anchor="rm")

    insight = script_data.get("insight","Learn, invest, grow — with discipline.")
    insight_lines, words, line = [], insight.split(), ""
    for w in words:
        test = (line+" "+w).strip()
        if get_font(FONT_REG_PATHS,36).getbbox(test)[2] < SW-160: line = test
        else: insight_lines.append(line); line = w
    if line: insight_lines.append(line)
    iy = 1090
    for ln in insight_lines[:4]:
        draw.text((SW//2,iy), ln, font=get_font(FONT_REG_PATHS,36), fill=SOFT_WHITE, anchor="mm")
        iy += 50

    draw.text((SW//2,1340),"📺 Full video link in description", font=get_font(FONT_REG_PATHS,34),fill=(140,170,220),anchor="mm")
    draw.rounded_rectangle([(60,1400),(SW-60,1480)],radius=15,fill=(255,180,0,20))
    draw.text((SW//2,1440),"⚠️ Educational content. Not financial advice.", font=get_font(FONT_REG_PATHS,30),fill=(200,180,100),anchor="mm")

    draw.rounded_rectangle([(100,SH-350),(SW-100,SH-250)],radius=25,fill=accent)
    cta = "📲 SUBSCRIBE FOR DAILY LEARNING" if CONTENT_MODE in ("holiday","weekend") else "📲 SUBSCRIBE FOR DAILY SIGNALS"
    draw_text_outlined(draw, cta, SW//2, SH-300, get_font(FONT_BOLD_PATHS,36),(0,0,0),outline=1)
    draw.text((SW//2,SH-190),"ai360trading.in  •  t.me/ai360trading", font=get_font(FONT_REG_PATHS,32),fill=(120,150,200),anchor="mm")

    path = OUT / f"short2_{now_ist.strftime('%Y%m%d')}.png"
    img.save(str(path), quality=95)
    return path

# ─── YOUTUBE & FACEBOOK UPLOAD ────────────────────────────────────────────────
def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json: return None
        return build("youtube","v3",credentials=Credentials.from_authorized_user_info(json.loads(creds_json)))
    except: return None

def upload_short(youtube, video_path, title, description):
    if not youtube: return None
    body = {
        "snippet":{"title":title[:100],"description":description,
                   "tags":["Nifty","Trading","Shorts","ai360trading","StockMarket"],"categoryId":"27"},
        "status":{"privacyStatus":"public","selfDeclaredMadeForKids":False}
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    try:
        request = youtube.videos().insert(part="snippet,status",body=body,media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
        return f"https://youtube.com/shorts/{response['id']}"
    except: return None

async def main():
    today = now_ist.strftime("%Y%m%d")
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    youtube = get_youtube_service()
    market = fetch_market_data()
    part1_url = get_part1_url()

    # Short 2 Generation (Trade Setup)
    context_str = f"Consistent with main video: {market['context']}. Mode: {CONTENT_MODE}."
    prompt = f"Expert Indian trader creating Hinglish YouTube Short. {context_str}. Respond ONLY with valid JSON: {{\"stock\":\"name\",\"sentiment\":\"bullish/bearish\",\"entry\":\"price\",\"target\":\"price\",\"sl\":\"price\",\"horizon\":\"Intraday\",\"insight\":\"10 words\",\"script\":\"40-sec Hinglish script energetic. Hook. End with CTA. Max 80 words.\"}}"
    
    resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}], response_format={"type":"json_object"})
    s2_data = json.loads(resp.choices[0].message.content)
    
    s2_frame = make_short2_frame(s2_data, market)
    s2_audio_path = OUT / f"short2_voice_{today}.mp3"
    await edge_tts.Communicate(s2_data["script"], "hi-IN-MadhurNeural", rate="+10%").save(str(s2_audio_path))
    
    voice = AudioFileClip(str(s2_audio_path))
    dur = voice.duration + 0.5
    final_audio = mix_audio(voice, dur)
    
    video_path = OUT / f"short2_{today}.mp4"
    ImageClip(str(s2_frame)).set_duration(dur).set_audio(final_audio).write_videofile(str(video_path), fps=FPS, codec="libx264", audio_codec="aac", logger=None)
    
    s2_url = upload_short(youtube, video_path, f"Setup: {s2_data['stock']} - {now_ist.strftime('%d %b')}", f"Full Analysis: {part1_url}")
    print(f"🚀 Short 2: {s2_url}")

if __name__ == "__main__":
    asyncio.run(main())
