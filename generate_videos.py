"""
AI360Trading — YouTube Video Automation Bot v2.0
=================================================
IMPROVEMENTS in v2:
- No box-style text — all slides use modern card/layer design
- Gradient backgrounds with depth — no flat dark rectangles
- Animated-feel static frames with diagonal lines, dots, circles
- Chart slides use real matplotlib candlestick + volume bars
- Education slides use large emoji-backed icon cards
- Personal finance slides use visual bar/pie charts with real numbers
- Thumbnail: person photo + bold Hinglish headline + dramatic colors
- TTS script cleaned — no AI phrases, natural Hinglish tone
- Script prompt completely rewritten to avoid robotic language
"""

import os, sys, json, time, math, random, textwrap, requests, asyncio, pytz, re, base64
from datetime import datetime
from io import BytesIO
from groq import Groq

import asyncio
try:
    import edge_tts
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import matplotlib.ticker as mticker
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
    LIBS_OK = True
except ImportError as e:
    print(f"Missing: {e}")
    LIBS_OK = False

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    YOUTUBE_OK = True
except ImportError:
    YOUTUBE_OK = False

# ── Config ────────────────────────────────────────────────────────────────────
ist          = pytz.timezone('Asia/Kolkata')
now          = datetime.now(ist)
date_str     = now.strftime("%Y-%m-%d")
date_display = now.strftime("%B %d, %Y")
day_name     = now.strftime("%A")
weekday      = now.weekday()
client       = Groq(api_key=os.environ.get("GROQ_API_KEY"))
OUTPUT_DIR   = "/tmp/ai360_video"
os.makedirs(OUTPUT_DIR, exist_ok=True)
W, H         = 1280, 720

# ── Brand palette ─────────────────────────────────────────────────────────────
C = {
    "dark":    (10, 14, 28),
    "dark2":   (15, 22, 45),
    "blue":    (0, 98, 255),
    "green":   (46, 204, 113),
    "red":     (231, 76, 60),
    "orange":  (247, 147, 26),
    "purple":  (139, 92, 246),
    "gold":    (251, 191, 36),
    "white":   (255, 255, 255),
    "muted":   (100, 116, 139),
    "card":    (20, 30, 55),
    "accent":  (30, 45, 80),
}

def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb2f(t): return tuple(x/255 for x in t)

# ── Live data ─────────────────────────────────────────────────────────────────
def get_prices():
    syms = {"NIFTY 50":"^NSEI","S&P 500":"^GSPC","Bitcoin":"BTC-USD",
            "Gold":"GC=F","NASDAQ":"^IXIC","Ethereum":"ETH-USD","Bank Nifty":"^NSEBANK"}
    out = {}
    for name, sym in syms.items():
        try:
            r = requests.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d",
                headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
            m = r.json()["chart"]["result"][0]["meta"]
            p = m.get("regularMarketPrice", 0)
            prev = m.get("chartPreviousClose", p)
            pct = ((p-prev)/prev*100) if prev else 0
            out[name] = {"price":p,"prev":prev,"pct":round(pct,2),
                         "display":f"{p:,.2f} ({'+'if pct>=0 else ''}{pct:.2f}%)"}
        except:
            out[name] = {"price":0,"prev":0,"pct":0,"display":"N/A"}
        time.sleep(0.2)
    return out

def get_fg():
    try:
        d = requests.get("https://api.alternative.me/fng/?limit=1",timeout=8).json()
        v = int(d["data"][0]["value"])
        return v, d["data"][0]["value_classification"]
    except:
        return 50, "Neutral"

# ── Video topics ──────────────────────────────────────────────────────────────
TOPICS = {
    0: {"type":"nifty","color":C["blue"],"tags":["nifty today","nifty levels","stock market India","trading today","nifty analysis"],
        "title":"{direction} — NIFTY {nifty} का अगला कदम क्या? | {date}",
        "desc":"NIFTY 50 analysis {date} — key support, resistance, and today's trading levels.\n\n📊 Reports: https://ai360trading.in/topics/stock-market/\n📣 Telegram: https://t.me/ai360trading\n\n#NIFTY #StockMarket #AI360Trading"},
    1: {"type":"bitcoin","color":C["orange"],"tags":["bitcoin today","BTC price","crypto analysis","bitcoin 2026","crypto today"],
        "title":"Bitcoin ${btc} — {direction} | Crypto Analysis {date}",
        "desc":"Bitcoin price analysis {date}.\n\n₿ Reports: https://ai360trading.in/topics/bitcoin/\n📣 Telegram: https://t.me/ai360trading\n\n#Bitcoin #BTC #CryptoToday #AI360Trading"},
    2: {"type":"education","color":C["green"],"tags":["candlestick patterns","technical analysis","trading education","stock market basics","how to trade"],
        "title":"Candlestick Patterns — Every Trader Must Know These | Trading Education",
        "desc":"Master candlestick patterns with real NIFTY examples.\n\n📚 More: https://ai360trading.in/topics/ai-trading/\n📣 Telegram: https://t.me/ai360trading\n\n#CandlestickPatterns #TechnicalAnalysis #TradingEducation #AI360Trading"},
    3: {"type":"finance","color":C["green"],"tags":["SIP investment","mutual funds India","personal finance 2026","SIP vs lump sum","invest India"],
        "title":"SIP vs Lump Sum — सही जवाब कौन सा? | Personal Finance {year}",
        "desc":"SIP vs Lump Sum — which wins in {year}? Real numbers, real examples.\n\n💰 More: https://ai360trading.in/topics/personal-finance/\n📣 Telegram: https://t.me/ai360trading\n\n#SIP #MutualFunds #PersonalFinance #AI360Trading"},
    4: {"type":"weekly","color":C["blue"],"tags":["weekly market outlook","nifty next week","market this week","trading week ahead","weekly analysis"],
        "title":"Next Week Markets — क्या होगा? | NIFTY Outlook {date}",
        "desc":"Weekly market outlook {date}.\n\n📊 Full: https://ai360trading.in\n📣 Telegram: https://t.me/ai360trading\n\n#WeeklyOutlook #NIFTY #AI360Trading"},
    5: {"type":"support","color":C["purple"],"tags":["support resistance trading","price action","technical analysis India","how to trade levels","trading strategy"],
        "title":"Support-Resistance — Professional Traders का Secret | {date}",
        "desc":"Support and resistance levels explained simply.\n\n🤖 More: https://ai360trading.in/topics/ai-trading/\n📣 Telegram: https://t.me/ai360trading\n\n#SupportResistance #PriceAction #AI360Trading"},
    6: {"type":"stocks","color":C["blue"],"tags":["stocks to watch","top stocks this week","nifty stocks 2026","stock picks India","best stocks today"],
        "title":"5 Stocks I'm Watching This Week | {date} | NIFTY Picks",
        "desc":"Top 5 stocks to watch this week — {date}.\n\n📊 Analysis: https://ai360trading.in/topics/stock-market/\n📣 Telegram: https://t.me/ai360trading\n\n#StockPicks #TopStocks #NIFTY #AI360Trading"},
}

# ── Script generation ─────────────────────────────────────────────────────────
def generate_script(topic, prices, fg_val, fg_label):
    nifty = prices.get("NIFTY 50",{})
    sp500 = prices.get("S&P 500",{})
    btc   = prices.get("Bitcoin",{})
    gold  = prices.get("Gold",{})
    bnk   = prices.get("Bank Nifty",{})
    np_   = nifty.get("price",24000)
    npct  = nifty.get("pct",0)
    bp_   = btc.get("price",65000)
    s1n   = int(np_*0.986); r1n = int(np_*1.014)
    s2n   = int(np_*0.972); r2n = int(np_*1.028)
    s1b   = int(bp_*0.95);  r1b = int(bp_*1.05)
    mood  = "gir raha hai" if npct<-1 else "daba hua hai" if npct<0 else "upar ja raha hai" if npct>1 else "flat hai"
    t     = topic["type"]

    SYSTEM = """Tu Amit Kumar hai — AI360Trading founder, Haridwar, India.
Tu YouTube par ek real trader ki tarah bolta hai — camera ke saamne, seedha.
Audience: Indian traders 25-45 saal ke, beginners aur intermediate mix.

TU KAISE BOLTA HAI:
- Hinglish natural — "NIFTY ka jo level hai" "main kya soch raha hoon" "ye trap hai bhai"
- Short punchy sentences mix with longer analytical ones
- Express real opinions: "Main personally nahi kharidta yahaan" "Mujhe ye setup pasand hai"
- Admit uncertainty: "Honestly, main 100% sure nahi hoon" "Market ne surprise diya tha"
- Trader language: "tape ye bol raha hai" "smart money yahaan hai" "retail phans jayega"

BANNED PHRASES — kabhi mat bol:
"In conclusion", "Furthermore", "Moving on", "As we can see", "Welcome to",
"Today we will cover", "Without further ado", "In today's video",
"This highlights", "It is important to note", "Let us dive into"

SCRIPT FORMAT:
NARRATOR: [jo TTS bolega — natural Hinglish]
SLIDE: [English only — visual ke liye, no Hindi characters]

Har NARRATOR block = ek slide. 10-14 blocks likho."""

    if t == "nifty":
        focus = f"""LIVE DATA:
NIFTY {nifty.get('display','N/A')} | S1={s1n} S2={s2n} R1={r1n} R2={r2n}
Bank Nifty {bnk.get('display','N/A')}
S&P 500 {sp500.get('display','N/A')}
Fear & Greed: {fg_val} — {fg_label}
Gold: {gold.get('display','N/A')}

7 minute NIFTY analysis video likho. 820-900 spoken words, 12-13 NARRATOR blocks.

ARC:
1. HOOK — aaj kya hua, tension create karo (e.g. "NIFTY {mood} — aur main ek cheez dekh raha hoon jo zyaadatar log miss kar rahe hain")
2. GLOBAL PICTURE — S&P ka aaj kya matlab hai NIFTY ke liye
3. CHART STORY — price action kya bol raha hai, sirf numbers nahi
4. KEY LEVELS — {s1n} aur {r1n} ke peeche logic deep dive
5. BANK NIFTY — confirm karta hai ya contradict
6. FEAR & GREED — {fg_val} historically kya matlab rakhta hai
7. PERSONAL VIEW — tera actual view, honest reh, uncertainty include kar
8. BULL SCENARIO — target levels agar {r1n} toot gaya
9. BEAR SCENARIO — kya hoga agar {s1n} toot gaya
10. RISK MANAGEMENT — aaj ke market mein position size advice
11. TOMORROW — kal kya dekhna hai
12. CLOSE — ek memorable line jo unhe kal wapas laaye

Ek historical parallel zaroor add kar (March 2020/Oct 2021/June 2022/Dec 2023 mein se ek).
Total: 820-900 words spoken."""

    elif t == "bitcoin":
        focus = f"""LIVE DATA:
Bitcoin {btc.get('display','N/A')} | S1=${s1b:,} S2=${int(bp_*0.90):,} R1=${r1b:,} R2=${int(bp_*1.10):,}
Fear & Greed: {fg_val} — {fg_label}
S&P 500 {sp500.get('display','N/A')}

7 minute Bitcoin analysis video. 820-900 words, 12-13 NARRATOR blocks.

ARC:
1. HOOK — aaj BTC kahan hai, ye kyun important hai
2. RISK ENVIRONMENT — S&P {sp500.get('pct',0):+.1f}% — risk-on ya risk-off
3. FEAR & GREED {fg_val} — last 3 baar jab ye level tha kya hua
4. CHART STORY — price action ka emotional meaning
5. SUPPORT LEVELS — ${s1b:,} pe buyers aane chahiye, agar nahi aaye?
6. RESISTANCE — ${r1b:,} toot gaya toh kya hoga
7. HONEST VIEW — tera actual position/view, uncertainty ke saath
8. ON-CHAIN — whale movement, exchange flows estimate karo
9. ALTCOIN SIGNAL — BTC dominance upar ya neeche
10. BULL CASE — target with reasoning
11. BEAR CASE — where things break
12. RISK MANAGEMENT — stop placement aaj ke levels pe
13. CLOSE — memorable line

Historical reference zaroor (March 2020 $4k/Nov 2021 $69k/Nov 2022 FTX/Jan 2024 ETF).
Total: 820-900 words."""

    elif t == "education":
        focus = f"""Market context: NIFTY {mood} at {np_:,.0f} aaj.

9 minute candlestick education video. 1000-1100 words, 14-16 NARRATOR blocks.

HOOK (aaj ke market se connect karo):
"NIFTY aaj ek interesting candle bana raha hai. Agar tum ye pattern samajhte ho — toh tum exactly jaante ho ke iska matlab kya hai. Agar nahi samajhte — ye video tumhare liye hai."

PART 1 — WHY CANDLESTICKS WORK (2 min):
Har candle = buyers vs sellers ki ladaai. Body batata hai kaun jeeta. Wick batata hai kisne koshish ki. Ye sirf technical analysis nahi — ye human emotion padhna hai.

PATTERN 1 — DOJI:
Definition, psychology, real NIFTY example with date, trade karo kaise, beginners ki galti.

[SOFT CTA mid-video — natural, 1 sentence]

PATTERN 2 — HAMMER AND HANGING MAN:
Ek hi shape — opposite meaning depending on where it is. March 2020 NIFTY bottom example.

PATTERN 3 — ENGULFING:
Sabse reliable pattern. Sentiment complete reversal. Real example.

PATTERN 4 — MORNING STAR:
3 candle story — doubt, decision, confirmation.

PATTERN 5 — SHOOTING STAR:
Quick but powerful. Fake shooting stars se bachao.

CLOSE — homework:
"Aaj apna NIFTY chart kholo. Aaj ke video se ek pattern dhundho. Screenshot lo. Kal wapas aao aur comments mein batao — prediction sahi nikli ya nahi."

Total: 1000-1100 words."""

    elif t == "finance":
        focus = f"""Market today: NIFTY {mood}, Fear & Greed = {fg_val}.

8 minute SIP vs Lump Sum video. 900-1000 words, 13-15 NARRATOR blocks.

TONE: Warm, honest, CA dost jaise chai pe explain kar raha ho. No sales pitch.

HOOK:
Agar market gir raha hai: "Markets red hain aaj. Tumhara SIP humse lower price pe units khareed raha hai. Tumhara dost jo last month lump sum de gaya tha — woh abhi panic mein hai. Ye video batayega — dono mein se kaun smart tha."
Agar upar: "Market green hai aaj. Aur tum soch rahe ho 'main miss ho gaya'. Ye video batayega kyun SIP waale actually better position mein hain."

PART 1 — SAHI SAWAAL (2 min):
Zyaadatar log poochte hain "kaun zyaada return deta hai?" — yeh galat sawaal hai.
Sahi sawaal: "Kaun si strategy pe main tika rahunga jab market 40% giregi?"
Real story: Rahul (lump sum Rs 6L Jan 2022) vs Priya (SIP Rs 5000/month Jan 2022). Dec 2022 mein kya hua dono ke saath?

[SOFT CTA]

PART 2 — NUMBERS (2 min):
SIP Rs 5000/month x 10 years at 12% CAGR = Rs 23.2 lakh (Rs 6L invest kiya)
Lump Sum Rs 6L x 10 years at 12% CAGR = Rs 18.6 lakh
HONEST TRUTH: Lump sum March 2020 bottom pe dia hota toh Rs 40+ lakh hota. Par koi bottom time nahi kar paata. Yahi poora argument hai.

PART 3 — KAB KAUN JEETTA (2 min):
SIP jeetta jab: salary income hai, market volatile hai, tum emotional ho apne paiso ke baare mein
Lump sum jeetta jab: market 40%+ gir chuka ho, tum disciplined ho, emergency fund intact ho
Abhi Fear & Greed {fg_val} pe — kaun sa camp hai? Share your opinion.

PART 4 — PRACTICAL (1.5 min):
Aaj SIP start karo — specific steps
Kitna enough hai — 15-15-15 rule (Rs 15k/month, 15% return, 15 years = Rs 1 crore)
Common mistakes — market crash mein SIP band karna (sabse badi galti)

CLOSE:
"Shuru karne ka best time 10 saal pehle tha. Doosra best time aaj hai. Next month nahi jab market recover ho. Aur zyaada save karne ke baad nahi. Aaj."

Total: 920-1000 words."""

    elif t == "weekly":
        focus = f"""LIVE DATA:
NIFTY {nifty.get('display','N/A')} | S1={s1n} S2={s2n} R1={r1n} R2={r2n}
S&P 500 {sp500.get('display','N/A')}
Bitcoin {btc.get('display','N/A')} | S1=${s1b:,} R1=${r1b:,}
Fear & Greed: {fg_val} — {fg_label}

8 minute weekly outlook. 900-1000 words, 13-15 NARRATOR blocks.

HOOK: "Is hafte markets ne kuch important bataya. Sirf price ke baare mein nahi — ye bigger cycle ke baare mein tha. Main tumhe walk through karta hoon kya dekha maine, aur next week ke liye kya soch raha hoon."

PART 1 — WEEK RECAP (2 min): Kya hua NIFTY ke saath. Global mein kya hua. Ek cheez jo surprise kiya. Ek cheez jo view confirm hua.

[SOFT CTA]

PART 2 — FEAR & GREED {fg_val} (1 min): Ye reading kya bol rahi hai. Last 3 baar ye level Friday pe tha — Monday kya hua.

PART 3 — NIFTY NEXT WEEK (2 min): Range {s2n} to {r2n}. Monday ke liye key level {s1n}. Bull/bear scenarios. Key events this week.

PART 4 — BTC & GLOBAL (1 min): BTC {btc.get('display','N/A')} — leading ya lagging equities.

PART 5 — PERSONAL PLAN (1.5 min): Kya dekh raha hoon. Risk management. One trade idea with entry/stop/target.

CLOSE: "Ye mera view hai next week ke liye. Main galat bhi ho sakta hoon — market ne surprise diya hai mujhe pehle bhi. Par ye levels hain jinke saath main kaam kar raha hoon. Monday morning mil te hain daily analysis ke saath. Weekend enjoy karo."

Total: 920-1000 words."""

    elif t == "support":
        focus = f"""Market today: NIFTY {mood} at {np_:,.0f}. S1={s1n}, R1={r1n}.

9 minute support-resistance education. 1000-1100 words, 14-16 NARRATOR blocks.

HOOK: "NIFTY abhi {np_:,.0f} pe hai. Aur just neeche ek level hai {s1n} pe jo har serious trader dekh raha hai. Agar tum support-resistance nahi jaante — ya theory jaante ho par trade nahi kar paate — ye video tumhare liye hai."

PART 1 — YE LEVELS KYA HAIN ACTUALLY (2 min):
Support = ek price jahan pehle buyers ne sellers ko haraaya tha. Bas itna. Koi magic nahi.
Resistance = jahan sellers ne buyers ko roka tha. Memory se bana ceiling.
Same levels kaam kyun karte hain baar baar? Kyunki traders yaad rakhte hain. Institutions ke orders wahaan hain.

[SOFT CTA]

PART 2 — LEVELS KAISE IDENTIFY KARO (2.5 min):
Method 1: Previous swing highs/lows — sabse reliable. Today's NIFTY pe: {s2n} tha previous swing low.
Method 2: Round numbers — 24000, 23500, 23000 — psychological magnets. Round numbers pe institutional orders hote hain.
Method 3: High volume zones — jahan price sabse zyaada time spend kiya.
Common mistake: bahut saare levels kheechna. 2-3 key levels chahiye, 20 nahi.

PART 3 — TRADE KARO KAISE (2.5 min):
Bounce trade: price {s1n} ke paas aaye — turant mat kharido.
Wait karo confirmation ke liye — green candle level ke upar close ho level test ke baad.
Entry: confirmation candle high ke upar. Stop: test candle ke wick ke neeche. Target: {r1n}.
Breakout trade: price {s1n} ke neeche close ho volume pe.
Fake breakout trap — yahi se beginners paisa zyaada gawate hain.

PART 4 — AAJ KA LIVE EXAMPLE (1.5 min):
Today's NIFTY chart walkthrough {s1n} aur {r1n} use karke. Tera personal view kya hai.

CLOSE — homework: "Apna NIFTY chart kholo — Zerodha Kite, Groww, TradingView — koi bhi. {s1n} pe ek horizontal line kheeecho. {r1n} pe dusri. 3 trading days dekhna in levels ko. Comments mein aao batao kya dekha. Main har comment padhta hoon."

Total: 1000-1100 words."""

    else:  # stocks
        focus = f"""LIVE DATA:
NIFTY {nifty.get('display','N/A')} | Fear & Greed {fg_val} — {fg_label}

8 minute top 5 stocks video. 900-1000 words, 13-15 NARRATOR blocks.

STOCK SELECTION in {mood} market:
2 defensive stocks (FMCG, pharma, IT)
2 momentum/relative strength stocks
1 contrarian (beaten down but fundamental reason to recover)
Pick 5 real stocks from NIFTY 200 — real names.

HOOK: "NIFTY {mood} is hafte. Zyaadatar retail traders ya frozen hain ya panic mein. Par markets mein hamesha strength aur weakness ke pockets hote hain. Ye hain 5 stocks jo main closely dekh raha hoon is hafte, aur exactly kyun."

CONTEXT (1 min): Current NIFTY level. Kaun sa sector strong vs weak. Ek macro factor this week.

[SOFT CTA]

STOCKS 1-5 (5-6 min total):
Varied openers: "Pehla jo mujhe interesting laga—", "Ab ye wala interesting hai—",
"Ye mera contrarian pick hai—", "Ye high risk hai par setup clean hai—",
"Aur yeh ek jo zyaadatar ignore kar rahe hain—"

Har stock ke liye: kya ho raha hai abhi, specific level (entry trigger, SL, target), genuine opinion with doubts, ek risk factor.

CLOSE: "Ye hain mere paanch is hafte ke liye. Mujhe batao comments mein — kaun sa tumhe sabse interesting lagta hai. Aur agar tum koi paper trade karo — agli Sunday wapas aao batao kya hua. Kal morning milte hain NIFTY levels ke saath."

Total: 920-1000 words."""

    try:
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":SYSTEM},{"role":"user","content":focus}],
            temperature=0.92, max_tokens=2500,
            frequency_penalty=0.45, presence_penalty=0.35)
        return r.choices[0].message.content
    except Exception as e:
        print(f"Script failed: {e}")
        return None

# ── Script parser ─────────────────────────────────────────────────────────────
def parse_script(text):
    slides = []
    if "NARRATOR:" in text:
        cur_n, cur_s = "", ""
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("NARRATOR:"):
                if cur_n:
                    slides.append({"narrator":cur_n.strip(),"slide":cur_s.strip() or _title(cur_n)})
                cur_n = line[9:].strip(); cur_s = ""
            elif line.startswith("SLIDE:"):
                cur_s = line[6:].strip()
            elif line and cur_n and not line.startswith("HINDI_SUB:"):
                cur_n += " " + line
        if cur_n:
            slides.append({"narrator":cur_n.strip(),"slide":cur_s.strip() or _title(cur_n)})
    if len(slides) < 3:
        slides = []
        for para in text.split("\n\n"):
            para = para.strip()
            if len(para) > 40:
                slides.append({"narrator":para,"slide":_title(para)})
    if len(slides) < 3:
        words = text.split()
        for i in range(0, len(words), 80):
            chunk = " ".join(words[i:i+80])
            if chunk:
                slides.append({"narrator":chunk,"slide":_title(chunk)})
    return slides[:12]

def _title(t):
    t = re.sub(r'[*#\-]','',t)
    words = t.strip().split()[:7]
    return " ".join(words) if words else "AI360Trading"

# ── Drawing helpers ───────────────────────────────────────────────────────────
def new_canvas(bg=None):
    img = Image.new("RGB",(W,H), bg or C["dark"])
    return img, ImageDraw.Draw(img)

def gradient_bg(img, c1, c2, vertical=True):
    draw = ImageDraw.Draw(img)
    steps = H if vertical else W
    for i in range(steps):
        t = i/steps
        r = int(c1[0]*(1-t)+c2[0]*t)
        g = int(c1[1]*(1-t)+c2[1]*t)
        b = int(c1[2]*(1-t)+c2[2]*t)
        if vertical:
            draw.line([(0,i),(W,i)], fill=(r,g,b))
        else:
            draw.line([(i,0),(i,H)], fill=(r,g,b))

def add_grid_lines(img, color=(255,255,255), alpha=8):
    overlay = Image.new("RGBA",(W,H),(0,0,0,0))
    d = ImageDraw.Draw(overlay)
    for x in range(0,W,40):
        for y in range(0,H,40):
            d.ellipse([x-1,y-1,x+1,y+1], fill=(*color, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def add_diagonal_lines(img, color, alpha=12, gap=60):
    overlay = Image.new("RGBA",(W,H),(0,0,0,0))
    d = ImageDraw.Draw(overlay)
    for i in range(-H, W+H, gap):
        d.line([(i,0),(i+H,H)], fill=(*color, alpha), width=1)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def add_glow_circle(img, cx, cy, radius, color, alpha=30):
    overlay = Image.new("RGBA",(W,H),(0,0,0,0))
    d = ImageDraw.Draw(overlay)
    for r in range(radius, 0, -10):
        a = int(alpha * (1-r/radius))
        d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(*color, a))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def add_top_bar(draw, brand_color, right_text=""):
    draw.rectangle([0,0,W,56], fill=(*C["dark2"],))
    draw.rectangle([0,52,W,56], fill=brand_color)
    draw.text((24,14), "AI360TRADING", fill=brand_color,
              font=get_font(22, bold=True))
    if right_text:
        draw.text((W-24,14), right_text, fill=C["muted"],
                  font=get_font(16), anchor="ra")

def add_bottom_bar(draw):
    draw.rectangle([0,H-44,W,H], fill=(*C["dark2"],))
    draw.text((W//2, H-22), "ai360trading.in  |  t.me/ai360trading  |  @ai360trading",
              fill=C["muted"], font=get_font(14), anchor="mm")

def rounded_rect(draw, x1, y1, x2, y2, r, fill, outline=None, width=1):
    draw.rounded_rectangle([x1,y1,x2,y2], radius=r, fill=fill,
                            outline=outline, width=width)

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def draw_text_wrapped(draw, text, x, y, max_width, font, fill, spacing=8):
    words = text.split()
    lines = []
    line = ""
    for w in words:
        test = (line+" "+w).strip()
        bbox = draw.textbbox((0,0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    for i, ln in enumerate(lines):
        draw.text((x, y + i*(font.size+spacing)), ln, fill=fill, font=font)
    return y + len(lines)*(font.size+spacing)

# ── Slide generators ──────────────────────────────────────────────────────────

def slide_title(title, subtitle, brand_color, path):
    img, draw = new_canvas()
    gradient_bg(img, C["dark"], (5,10,30))
    img = add_diagonal_lines(img, brand_color, alpha=15, gap=55)
    img = add_glow_circle(img, W//2, H//2, 400, brand_color, alpha=18)
    draw = ImageDraw.Draw(img)
    add_top_bar(draw, brand_color)
    draw.rectangle([0,56,6,H-44], fill=brand_color)
    lines = textwrap.wrap(title, 32)
    y = 130
    for ln in lines:
        bbox = draw.textbbox((0,0), ln, font=get_font(52, bold=True))
        tw = bbox[2]-bbox[0]
        draw.text((W//2-tw//2+3, y+3), ln, fill=(0,0,0), font=get_font(52,bold=True))
        draw.text((W//2-tw//2, y), ln, fill=C["white"], font=get_font(52,bold=True))
        y += 68
    if subtitle:
        sbbox = draw.textbbox((0,0), subtitle, font=get_font(20))
        sw = sbbox[2]-sbbox[0]+40
        sx = W//2 - sw//2
        rounded_rect(draw, sx, y+16, sx+sw, y+52, 8, fill=(*brand_color,60))
        draw.text((W//2, y+34), subtitle, fill=brand_color,
                  font=get_font(20,bold=True), anchor="mm")
        y += 70
    date_text = f"  {date_display}  "
    dbbox = draw.textbbox((0,0), date_text, font=get_font(18))
    dw = dbbox[2]-dbbox[0]+20
    rounded_rect(draw, W//2-dw//2, y+14, W//2+dw//2, y+46, 6,
                 fill=(*C["dark2"],200), outline=brand_color, width=1)
    draw.text((W//2, y+30), date_text, fill=brand_color,
              font=get_font(18,bold=True), anchor="mm")
    add_bottom_bar(draw)
    img.save(path, quality=96)


def slide_fear_greed(fg_val, fg_label, prices, brand_color, path):
    img, draw = new_canvas()
    gradient_bg(img, C["dark"], (8,15,35))
    img = add_grid_lines(img, C["blue"])
    draw = ImageDraw.Draw(img)
    add_top_bar(draw, brand_color, date_display)
    fig, ax = plt.subplots(figsize=(5.5,4.5), dpi=100)
    fig.patch.set_facecolor((10/255,14/255,28/255))
    ax.set_facecolor((10/255,14/255,28/255))
    zones = [(0,25,'#e74c3c'),(25,45,'#e67e22'),(45,55,'#f1c40f'),(55,75,'#2ecc71'),(75,100,'#27ae60')]
    for lo,hi,zc in zones:
        th = np.linspace(np.pi*(1-lo/100), np.pi*(1-hi/100), 50)
        ax.plot(np.cos(th), np.sin(th), color=zc, linewidth=22, alpha=0.9, solid_capstyle='round')
    angle = np.pi*(1-fg_val/100)
    ax.annotate('', xy=(0.68*np.cos(angle),0.68*np.sin(angle)), xytext=(0,0),
                arrowprops=dict(arrowstyle='->', color='white', lw=3))
    ax.add_patch(plt.Circle((0,0),0.06,color='white'))
    nc = '#e74c3c' if fg_val<35 else '#f1c40f' if fg_val<55 else '#2ecc71'
    ax.text(0,-0.22,str(fg_val),fontsize=52,fontweight='black',color=nc,ha='center',va='center')
    ax.text(0,-0.48,fg_label.upper(),fontsize=15,fontweight='bold',color=nc,ha='center',va='center')
    ax.text(0,0.16,'FEAR & GREED',fontsize=12,color='#94a3b8',ha='center',fontweight='bold')
    ax.set_xlim(-1.2,1.2); ax.set_ylim(-0.7,1.1); ax.axis('off')
    plt.tight_layout(pad=0)
    buf = BytesIO(); plt.savefig(buf,format='png',dpi=100,bbox_inches='tight',
                                  facecolor=fig.get_facecolor()); plt.close()
    buf.seek(0)
    gauge_img = Image.open(buf).convert("RGB").resize((550,390))
    img.paste(gauge_img,(30,80))
    items = [
        ("NIFTY 50",   prices.get("NIFTY 50",{}).get("display","N/A"),  prices.get("NIFTY 50",{}).get("pct",0)),
        ("S&P 500",    prices.get("S&P 500",{}).get("display","N/A"),   prices.get("S&P 500",{}).get("pct",0)),
        ("Bitcoin",    prices.get("Bitcoin",{}).get("display","N/A"),   prices.get("Bitcoin",{}).get("pct",0)),
        ("Gold",       prices.get("Gold",{}).get("display","N/A"),      prices.get("Gold",{}).get("pct",0)),
    ]
    draw = ImageDraw.Draw(img)
    rx = 620
    draw.text((rx+220, 75), "LIVE MARKET", fill=C["white"],
              font=get_font(22,bold=True), anchor="mm")
    for i,(name,disp,pct) in enumerate(items):
        ry = 112 + i*138
        clr = C["green"] if pct>=0 else C["red"]
        arrow = "▲" if pct>=0 else "▼"
        rounded_rect(draw, rx, ry, W-30, ry+120, 14, fill=C["card"])
        draw.rectangle([rx,ry,rx+5,ry+120], fill=clr)
        draw.text((rx+22, ry+24), name, fill=C["muted"], font=get_font(16,bold=True))
        draw.text((rx+22, ry+50), disp, fill=C["white"], font=get_font(24,bold=True))
        draw.text((rx+22, ry+86), f"{arrow} {abs(pct):.2f}% today",
                  fill=clr, font=get_font(18,bold=True))
    add_bottom_bar(draw)
    img.save(path, quality=96)


def slide_candlestick_chart(prices, title_label, brand_color, path):
    fig, axes = plt.subplots(2, 1, figsize=(12.8,7.2), dpi=100,
                             gridspec_kw={'height_ratios':[3,1],'hspace':0.04})
    fig.patch.set_facecolor(rgb2f(C["dark"]))
    ax, vax = axes
    base  = prices.get('NIFTY 50',{}).get('price',24000)
    pct   = prices.get('NIFTY 50',{}).get('pct',0)
    np.random.seed(int(base)%999)
    n = 25
    opens,highs,lows,closes,vols = [],[],[],[],[]
    p = base*(1-pct/100*4)
    for i in range(n):
        o=p; c=o+np.random.normal(0,base*0.005)
        h=max(o,c)+abs(np.random.normal(0,base*0.003))
        l=min(o,c)-abs(np.random.normal(0,base*0.003))
        v=np.random.randint(8000,22000)
        opens.append(o);closes.append(c);highs.append(h);lows.append(l);vols.append(v)
        p=c
    closes[-1]=base; highs[-1]=max(opens[-1],base)*1.003; lows[-1]=min(opens[-1],base)*0.997
    ax.set_facecolor(rgb2f(C["dark2"]))
    vax.set_facecolor(rgb2f(C["dark2"]))
    for i in range(n):
        bull=closes[i]>=opens[i]
        clr='#2ecc71' if bull else '#e74c3c'
        ax.plot([i,i],[lows[i],highs[i]],color=clr,lw=1.5,zorder=2)
        bh=max(abs(closes[i]-opens[i]),base*0.001)
        rect=mpatches.Rectangle((i-0.38,min(opens[i],closes[i])),0.76,bh,
                                  color=clr,alpha=0.9,zorder=3)
        ax.add_patch(rect)
        vax.bar(i,vols[i],color=clr,alpha=0.6,width=0.7)
    s1=base*0.986; s2=base*0.972; r1=base*1.014; r2=base*1.028
    for level,color_,label_ in [(s2,'#f59e0b',f'S2  {s2:,.0f}'),
                                   (s1,'#2ecc71',f'S1  {s1:,.0f}'),
                                   (base,'#ffffff',f'NOW {base:,.0f}'),
                                   (r1,'#e74c3c',f'R1  {r1:,.0f}'),
                                   (r2,'#f59e0b',f'R2  {r2:,.0f}')]:
        ls = ':' if level==base else '--'
        ax.axhline(level,color=color_,lw=1.8,linestyle=ls,alpha=0.85,zorder=4)
        ax.text(n+0.4, level, label_, color=color_, fontsize=10,
                fontweight='bold', va='center')
    ax.axhspan(s1*0.998,s1*1.002,alpha=0.07,color='#2ecc71')
    ax.axhspan(r1*0.998,r1*1.002,alpha=0.07,color='#e74c3c')
    ax.set_xlim(-1,n+5); ax.set_ylim(min(lows)*0.997,max(highs)*1.007)
    vax.set_xlim(-1,n+5)
    for spine in ax.spines.values(): spine.set_color(rgb2f(C["accent"]))
    for spine in vax.spines.values(): spine.set_color(rgb2f(C["accent"]))
    ax.tick_params(colors=rgb2f(C["muted"]),labelsize=9); ax.set_xticks([])
    vax.tick_params(colors=rgb2f(C["muted"]),labelsize=8); vax.set_xticks([])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_:f'{x:,.0f}'))
    vax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_:f'{x//1000:.0f}K'))
    vax.set_ylabel('Volume',color=rgb2f(C["muted"]),fontsize=9)
    pc = rgb2f(C["green"] if pct>=0 else C["red"])
    arrow = '▲' if pct>=0 else '▼'
    fig.text(0.03,0.97,'AI360TRADING',fontsize=12,fontweight='bold',
             color=rgb2f(brand_color),va='top')
    fig.text(0.5,0.97,title_label,fontsize=16,fontweight='bold',
             color=rgb2f(C["white"]),ha='center',va='top')
    fig.text(0.97,0.97,f'NIFTY  {arrow} {abs(pct):.2f}%',
             fontsize=14,fontweight='bold',color=pc,ha='right',va='top')
    fig.text(0.5,0.01,'ai360trading.in  |  Subscribe for daily NIFTY analysis',
             fontsize=10,color=rgb2f(C["muted"]),ha='center',va='bottom')
    plt.tight_layout(rect=[0,0.03,1,0.94])
    fig.savefig(path,dpi=100,bbox_inches='tight',facecolor=fig.get_facecolor())
    plt.close()


def slide_sr_table(prices, brand_color, path):
    img, draw = new_canvas()
    gradient_bg(img, C["dark"], (5,12,30))
    img = add_grid_lines(img, brand_color, alpha=6)
    draw = ImageDraw.Draw(img)
    add_top_bar(draw, brand_color, date_display)
    draw.text((W//2, 80), "KEY LEVELS TO WATCH", fill=C["white"],
              font=get_font(32,bold=True), anchor="mm")
    rows = [
        ("NIFTY 50",   prices.get("NIFTY 50",{}).get("price",24000),   prices.get("NIFTY 50",{}).get("pct",0),   ""),
        ("S&P 500",    prices.get("S&P 500",{}).get("price",5500),     prices.get("S&P 500",{}).get("pct",0),    ""),
        ("Bitcoin",    prices.get("Bitcoin",{}).get("price",65000),    prices.get("Bitcoin",{}).get("pct",0),    "$"),
    ]
    headers = ["INSTRUMENT","PRICE","SUPPORT","RESISTANCE","CHANGE"]
    col_x   = [60, 310, 520, 730, 950]
    hy = 120
    for h,x in zip(headers,col_x):
        draw.text((x,hy), h, fill=C["muted"], font=get_font(15,bold=True))
    draw.line([(40,148),(W-40,148)], fill=C["accent"], width=1)
    for i,(name,price,pct,prefix) in enumerate(rows):
        ry = 170 + i*148
        clr = C["green"] if pct>=0 else C["red"]
        arrow = "▲" if pct>=0 else "▼"
        rounded_rect(draw, 40, ry, W-40, ry+128, 12, fill=C["card"])
        draw.rectangle([40,ry,48,ry+128], fill=clr)
        s1 = price*0.986; s2 = price*0.972
        r1 = price*1.014
        p_fmt = f"{prefix}{price:,.0f}"
        s1_fmt = f"{prefix}{s1:,.0f}"
        r1_fmt = f"{prefix}{r1:,.0f}"
        draw.text((col_x[0]+8, ry+44), name,   fill=C["white"],  font=get_font(20,bold=True))
        draw.text((col_x[1],   ry+44), p_fmt,  fill=C["white"],  font=get_font(20,bold=True))
        draw.text((col_x[2],   ry+44), s1_fmt, fill=C["green"],  font=get_font(20,bold=True))
        draw.text((col_x[3],   ry+44), r1_fmt, fill=C["red"],    font=get_font(20,bold=True))
        draw.text((col_x[4],   ry+44), f"{arrow} {abs(pct):.2f}%", fill=clr, font=get_font(20,bold=True))
    draw.text((W//2, H-70),
              "🟢 Support = Buying zone    🔴 Resistance = Watch for rejection",
              fill=C["muted"], font=get_font(15), anchor="mm")
    add_bottom_bar(draw)
    img.save(path, quality=96)


def slide_content(slide_text, narrator_text, brand_color, num, total, path):
    img, draw = new_canvas()
    gradient_bg(img, C["dark"], (8,14,32), vertical=True)
    img = add_diagonal_lines(img, brand_color, alpha=10, gap=70)
    img = add_glow_circle(img, 80, H//2, 320, brand_color, alpha=20)
    draw = ImageDraw.Draw(img)
    add_top_bar(draw, brand_color, f"{num} / {total}")
    draw.rectangle([0,56,5,H-44], fill=brand_color)
    prog_w = int((num/total)*(W-80))
    draw.rectangle([40,H-52,40+prog_w,H-48], fill=brand_color)
    heading = slide_text.strip().split('\n')[0] if slide_text else narrator_text[:60]
    heading = re.sub(r'[*#]','',heading).strip()[:60]
    draw.rectangle([6,74,40,74+56], fill=brand_color)   # left colored strip (FIXED)
    y = draw_text_wrapped(draw, heading, 50, 82,
                          W-80, get_font(36, bold=True), C["white"], spacing=10)
    y += 20
    draw.line([(50,y),(W-50,y)], fill=(*brand_color, 80), width=1)
    y += 24
    body = narrator_text[:220] + ("..." if len(narrator_text)>220 else "")
    body = re.sub(r'(SLIDE|NARRATOR|HINDI_SUB):[^\n]*','',body).strip()
    draw_text_wrapped(draw, body, 50, y, W-80, get_font(22), C["white"], spacing=12)
    quote = narrator_text[:90].strip()
    quote = re.sub(r'\s+',' ',quote)
    rounded_rect(draw, 40, H-110, W-40, H-52, 8, fill=(*C["dark2"],180))
    draw.text((W//2, H-81), f'"{quote}..."', fill=(*C["muted"],),
              font=get_font(14), anchor="mm")
    add_bottom_bar(draw)
    img.save(path, quality=96)


def slide_education_icon(topic_title, points, brand_color, path):
    img, draw = new_canvas()
    gradient_bg(img, (8,20,18) if brand_color==C["green"] else C["dark"], C["dark"])
    img = add_grid_lines(img, brand_color, alpha=8)
    img = add_glow_circle(img, W//2, 120, 300, brand_color, alpha=15)
    draw = ImageDraw.Draw(img)
    add_top_bar(draw, brand_color)
    draw.text((W//2, 84), topic_title, fill=C["white"],
              font=get_font(28,bold=True), anchor="mm")
    if len(points) <= 4:
        cols = 2
    else:
        cols = 3
    rows = math.ceil(len(points)/cols)
    card_w = (W - 80 - (cols-1)*16) // cols
    card_h = min(160, (H - 160 - (rows-1)*14) // rows)
    icons = ["📊","📈","📉","💡","⚡","🎯","🔑","💰","📌","✅","⚠️","🔄"]
    for i, pt in enumerate(points[:cols*rows]):
        col = i % cols; row = i // cols
        x1 = 40 + col*(card_w+16)
        y1 = 110 + row*(card_h+14)
        x2 = x1 + card_w; y2 = y1 + card_h
        rounded_rect(draw, x1, y1, x2, y2, 14, fill=C["card"])
        draw.rectangle([x1,y1,x1+4,y2], fill=brand_color)
        ic = icons[i % len(icons)]
        draw.text((x1+22, y1+card_h//2-20), ic, fill=brand_color,
                  font=get_font(26))
        draw_text_wrapped(draw, pt, x1+60, y1+16, card_w-70,
                         get_font(16,bold=True), C["white"], spacing=6)
    add_bottom_bar(draw)
    img.save(path, quality=96)


def slide_finance_chart(data_type, prices, brand_color, path):
    fig, ax = plt.subplots(figsize=(12.8,7.2), dpi=100)
    fig.patch.set_facecolor(rgb2f(C["dark"]))
    ax.set_facecolor(rgb2f(C["dark2"]))
    if data_type == "sip_growth":
        years = list(range(0,11))
        sip_monthly = 5000
        lump = 600000
        rate = 0.12
        sip_vals = []
        sip_total = 0
        for y in years:
            if y > 0: sip_total = sip_total*(1+rate/12)**12 + sip_monthly*12
            sip_vals.append(sip_total)
        lump_vals = [lump*(1+rate)**y for y in years]
        ax.fill_between(years, sip_vals, alpha=0.25, color='#2ecc71')
        ax.fill_between(years, lump_vals, alpha=0.20, color='#0062ff')
        ax.plot(years, sip_vals, color='#2ecc71', lw=3, label=f'SIP ₹5k/month', marker='o', markersize=6)
        ax.plot(years, lump_vals, color='#0062ff', lw=3, label=f'Lump Sum ₹6L', marker='s', markersize=6)
        ax.annotate(f'₹{sip_vals[-1]/100000:.1f}L', xy=(10,sip_vals[-1]),
                    xytext=(9.2,sip_vals[-1]*1.06),
                    color='#2ecc71', fontsize=12, fontweight='bold',
                    arrowprops=dict(arrowstyle='-',color='#2ecc71',lw=1.5))
        ax.annotate(f'₹{lump_vals[-1]/100000:.1f}L', xy=(10,lump_vals[-1]),
                    xytext=(9.0,lump_vals[-1]*0.92),
                    color='#0062ff', fontsize=12, fontweight='bold',
                    arrowprops=dict(arrowstyle='-',color='#0062ff',lw=1.5))
        ax.set_xlabel('Years', color=rgb2f(C["muted"]), fontsize=11)
        ax.set_ylabel('Portfolio Value (₹)', color=rgb2f(C["muted"]), fontsize=11)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_:f'₹{x/100000:.0f}L'))
        ax.legend(loc='upper left', facecolor=rgb2f(C["card"]),
                  labelcolor='white', fontsize=12, framealpha=0.9)
        fig.text(0.5,0.97,'SIP vs Lump Sum — 10 Year Growth at 12% CAGR',
                 fontsize=16,fontweight='bold',color='white',ha='center',va='top')
    else:
        labels = ['Year 5','Year 10','Year 15']
        monthly_15k = [15000*12*5*1.15, 15000*12*10*1.25, 10000000]
        colors_ = ['#378ADD','#2ecc71','#f59e0b']
        bars = ax.bar(labels, [v/100000 for v in monthly_15k],
                      color=colors_, alpha=0.85, width=0.5)
        for bar,val in zip(bars,monthly_15k):
            ax.text(bar.get_x()+bar.get_width()/2,
                    bar.get_height()+0.5,
                    f'₹{val/100000:.0f}L',
                    ha='center',color='white',fontsize=14,fontweight='bold')
        ax.set_ylabel('Value (₹ Lakh)', color=rgb2f(C["muted"]), fontsize=11)
        fig.text(0.5,0.97,'15-15-15 Rule — ₹15k/Month SIP @ 15% Return',
                 fontsize=16,fontweight='bold',color='white',ha='center',va='top')
    for spine in ax.spines.values(): spine.set_color(rgb2f(C["accent"]))
    ax.tick_params(colors=rgb2f(C["muted"]), labelsize=10)
    fig.text(0.5,0.01,'ai360trading.in  |  Not financial advice — educational only',
             fontsize=10,color=rgb2f(C["muted"]),ha='center',va='bottom')
    plt.tight_layout(rect=[0,0.04,1,0.94])
    fig.savefig(path,dpi=100,bbox_inches='tight',facecolor=fig.get_facecolor())
    plt.close()


def slide_outro(brand_color, path):
    img, draw = new_canvas()
    gradient_bg(img, C["dark"], (5,10,28))
    img = add_glow_circle(img, W//2, H//2-60, 380, brand_color, alpha=22)
    img = add_diagonal_lines(img, brand_color, alpha=8)
    draw = ImageDraw.Draw(img)
    draw.ellipse([W//2-90, 60, W//2+90, 240], fill=(*brand_color, 25),
                 outline=brand_color, width=2)
    draw.text((W//2, 150), "AI360", fill=brand_color,
              font=get_font(44,bold=True), anchor="mm")
    draw.text((W//2, 268), "TRADING", fill=C["muted"],
              font=get_font(20,bold=True), anchor="mm")
    draw.text((W//2, 316), "Subscribe for Daily Market Intelligence",
              fill=C["white"], font=get_font(26,bold=True), anchor="mm")
    pillars = [("📊","Stock Market"),("₿","Bitcoin"),("💰","Personal Finance"),("🤖","AI Trading")]
    pw = 240; gap = 20; sx = (W - 4*pw - 3*gap) // 2
    for i,(ic,lb) in enumerate(pillars):
        px = sx + i*(pw+gap)
        rounded_rect(draw, px, 360, px+pw, 470, 12, fill=C["card"])
        draw.text((px+pw//2, 400), ic, fill=brand_color,
                  font=get_font(28), anchor="mm")
        draw.text((px+pw//2, 440), lb, fill=C["white"],
                  font=get_font(16,bold=True), anchor="mm")
    draw.text((W//2, 508), "📣  t.me/ai360trading",
              fill=C["green"], font=get_font(20,bold=True), anchor="mm")
    draw.text((W//2, 548), "🌐  ai360trading.in",
              fill=brand_color, font=get_font(20,bold=True), anchor="mm")
    draw.text((W//2, 590),
              "⚠️  Educational content only — not SEBI registered investment advice",
              fill=C["muted"], font=get_font(13), anchor="mm")
    add_bottom_bar(draw)
    img.save(path, quality=96)


def create_thumbnail(title, prices, pct_change, brand_color, path):
    is_crash = pct_change < -0.5
    img, draw = new_canvas()
    c1 = (140,0,0) if is_crash else (0,100,15)
    c2 = (8,0,0) if is_crash else (0,10,3)
    gradient_bg(img, c1, c2, vertical=False)
    img = add_diagonal_lines(img, C["white"], alpha=6)
    draw = ImageDraw.Draw(img)
    np.random.seed(42)
    overlay = Image.new("RGBA",(W,H),(0,0,0,0))
    od = ImageDraw.Draw(overlay)
    p = 24500
    for i in range(18):
        o=p; c=o+random.uniform(-180,180)
        hh=max(o,c)+random.uniform(40,120); ll=min(o,c)-random.uniform(40,120)
        x=460+i*46; bull=c>=o; col=(70,200,70,40) if bull else (200,70,70,40)
        yo=int(560-(o-24100)*0.018); yc=int(560-(c-24100)*0.018)
        yh=int(560-(hh-24100)*0.018); yl=int(560-(ll-24100)*0.018)
        od.line([(x,yh),(x,yl)],fill=col,width=2)
        od.rectangle([x-9,min(yo,yc),x+9,max(yo,yc)+1],fill=col)
        p=c
    img = Image.alpha_composite(img.convert("RGBA"),overlay).convert("RGB")

    # Person photo from GitHub
    base_url = "https://raw.githubusercontent.com/systronics/ai360trading/master/public/image/"
    options = ["person_crash_1.jpg","person_crash_2.jpg","person_crash_3.jpg","person_crash_4.jpg"] if is_crash else ["person_green_1.jpg","person_green_2.jpg","person_green_3.jpg"]
    photo_choice = options[now.timetuple().tm_yday % len(options)]
    try:
        resp = requests.get(base_url+photo_choice, timeout=10)
        if resp.status_code == 200:
            person_img = Image.open(BytesIO(resp.content)).convert("RGBA")
            pw,ph = person_img.size
            p_h = int(H*0.98); p_w = int(pw*(p_h/ph))
            person_img = person_img.resize((p_w,p_h),Image.LANCZOS)
            px_ = W-p_w-8; py_ = H-p_h
            # Left fade
            fa = np.ones((p_h,p_w),dtype=np.float32)*255
            for x in range(min(80,p_w)): fa[:,x] *= x/80
            person_img.putalpha(Image.fromarray(fa.astype(np.uint8)))
            # Shadow
            shadow = Image.new("RGBA",(W,H),(0,0,0,0))
            alpha_blur = person_img.getchannel("A").filter(ImageFilter.GaussianBlur(20))
            shadow.paste(Image.new("RGBA",(p_w+30,p_h),(0,0,0,120)),(px_+15,py_+20),alpha_blur)
            img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
            # Paste person — convert to RGBA first
            img_rgba = img.convert("RGBA")
            img_rgba.paste(person_img, (px_, py_), person_img)
            img = img_rgba.convert("RGB")
    except Exception as e:
        print(f"Photo fetch: {e}")

    lo = Image.new("RGBA",(W,H),(0,0,0,0))
    ld = ImageDraw.Draw(lo)
    for x in range(700):
        a = int(120*(1-x/700))
        ld.line([(x,0),(x,H)],fill=(0,0,0,a))
    img = Image.alpha_composite(img.convert("RGBA"),lo).convert("RGB")
    draw = ImageDraw.Draw(img)
    h1 = "NIFTY" if "nifty" in title.lower() or "stock" in title.lower() else "BITCOIN" if "bitcoin" in title.lower() else "MARKET"
    h2 = "गिरा !" if is_crash else "उठा !"
    badge = f"{'▼' if is_crash else '▲'} {abs(pct_change):.2f}% TODAY"
    badge_c = (200,0,0) if is_crash else (0,150,20)
    txt_c2 = (255,215,0) if is_crash else (100,255,100)
    subtitle = "देखो Level तोड़ा ?" if is_crash else "Buy करें या Wait ?"
    def sh(d,xy,t,f,fill):
        d.text((xy[0]+4,xy[1]+4),t,font=f,fill=(0,0,0,180))
        d.text(xy,t,font=f,fill=fill)
    sh(draw,(36,22),h1,get_font(108,bold=True),C["white"])
    sh(draw,(36,126),h2,get_font(118,bold=True),txt_c2)
    bb = draw.textbbox((0,0),badge,font=get_font(36,bold=True))
    bw = bb[2]-bb[0]+32
    draw.rounded_rectangle([36,270,36+bw,318],radius=12,fill=badge_c)
    draw.text((52,284),badge,fill=C["white"],font=get_font(36,bold=True))
    draw.text((36,330),date_display,fill=(200,200,200),font=get_font(32,bold=False))
    sb = draw.textbbox((0,0),subtitle,font=get_font(30,bold=True))
    sw2 = sb[2]-sb[0]+32
    draw.rounded_rectangle([36,376,36+sw2,418],radius=10,fill=(200,80,0))
    draw.text((52,388),subtitle,fill=C["white"],font=get_font(30,bold=True))
    draw.text((36,432),"ai360trading.in",fill=(120,180,255),font=get_font(26,bold=False))
    draw.rectangle([0,668,W,H],fill=(0,0,0))
    draw.text((W//2,684),
              "AI360TRADING  |  Daily Market Analysis  |  @ai360trading",
              fill=(80,160,255),font=get_font(24,bold=True),anchor="mm")
    img.save(path, quality=96)


# ── TTS ───────────────────────────────────────────────────────────────────────
VOICE     = "en-IN-PrabhatNeural"
VOICE_ALT = "en-IN-NeerjaNeural"

def clean_tts(text):
    text = text.replace("₹"," rupees ").replace("$"," dollars ").replace("%"," percent")
    text = text.replace("&"," and ").replace("|",". ").replace("→"," to ")
    text = text.replace("▲"," up ").replace("▼"," down ")
    text = text.replace("—",", ").replace("–",", ")
    text = text.replace("**","").replace("##","").replace("*","")
    text = text.replace("NIFTY","Nifty").replace("S&P","S and P")
    text = re.sub(r"(SLIDE|NARRATOR|HINDI_SUB):[^\n]*","",text)
    text = re.sub(r"\d{1,3}(,\d{3})+", lambda m: m.group(0).replace(",",""), text)
    text = re.sub(r"\s+"," ",text).strip()
    return text

async def _tts(text, path, voice):
    comm = edge_tts.Communicate(text=text, voice=voice, rate="+0%", pitch="+0Hz", volume="+10%")
    await comm.save(path)

def tts(text, path):
    try:
        c = clean_tts(text)
        if not c or len(c)<5: return False
        asyncio.run(_tts(c, path, VOICE))
        return os.path.exists(path) and os.path.getsize(path)>1000
    except Exception as e:
        print(f"TTS fallback: {e}")
        try:
            asyncio.run(_tts(clean_tts(text), path, VOICE_ALT))
            return os.path.exists(path) and os.path.getsize(path)>1000
        except:
            return False

# ── Video assembly ────────────────────────────────────────────────────────────
def assemble(slide_paths, narrators, out_path):
    clips = []
    for i,(sp,nar) in enumerate(zip(slide_paths, narrators)):
        if not nar: continue
        ap = os.path.join(OUTPUT_DIR, f"a_{i}.mp3")
        ok = tts(nar, ap)
        if ok:
            ac = AudioFileClip(ap)
            clip = ImageClip(sp).set_duration(ac.duration+0.4).set_audio(ac)
        else:
            clip = ImageClip(sp).set_duration(5)
        clips.append(clip)
        time.sleep(0.15)
    if not clips: return False
    vid = concatenate_videoclips(clips, method="compose")
    vid.write_videofile(out_path, fps=24, codec='libx264', audio_codec='aac',
                        temp_audiofile=os.path.join(OUTPUT_DIR,'_tmp.m4a'),
                        remove_temp=True, logger=None)
    return True


# ── GitHub Secret updater ─────────────────────────────────────────────────────
def _save_token_to_github(cd):
    """Auto-saves refreshed YOUTUBE_CREDENTIALS back to GitHub Secrets"""
    try:
        gh_token = os.environ.get("GH_TOKEN")
        repo     = os.environ.get("GITHUB_REPOSITORY")
        if not gh_token or not repo:
            print("  ⚠️  GH_TOKEN not set — token not saved back to secrets")
            return
        import nacl.encoding, nacl.public
        headers = {
            "Authorization": f"token {gh_token}",
            "Accept": "application/vnd.github+json"
        }
        # Get repo public key
        key_resp = requests.get(
            f"https://api.github.com/repos/{repo}/actions/secrets/public-key",
            headers=headers, timeout=10).json()
        pub_key_b64 = key_resp["key"]
        key_id      = key_resp["key_id"]
        # Encrypt new value
        public_key  = nacl.public.PublicKey(pub_key_b64, nacl.encoding.Base64Encoder)
        sealed_box  = nacl.public.SealedBox(public_key)
        encrypted   = sealed_box.encrypt(json.dumps(cd).encode())
        encrypted_b64 = base64.b64encode(encrypted).decode()
        # Push to GitHub
        r = requests.put(
            f"https://api.github.com/repos/{repo}/actions/secrets/YOUTUBE_CREDENTIALS",
            headers=headers,
            json={"encrypted_value": encrypted_b64, "key_id": key_id},
            timeout=10)
        if r.status_code in (201, 204):
            print("  ✅ YouTube token refreshed and saved to GitHub Secrets automatically")
        else:
            print(f"  ⚠️  Secret update failed: {r.status_code}")
    except Exception as e:
        print(f"  ⚠️  Could not save token to GitHub: {e}")


# ── YouTube upload ────────────────────────────────────────────────────────────
def upload_yt(video_path, title, description, tags, thumb_path=None):
    if not YOUTUBE_OK: return None
    try:
        cj = os.environ.get("YOUTUBE_CREDENTIALS")
        if not cj: return None
        cd = json.loads(cj)

        creds = Credentials(
            token=cd.get("token"),
            refresh_token=cd.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cd.get("client_id"),
            client_secret=cd.get("client_secret")
        )

        # ── Auto-refresh if token expired ─────────────────────────
        if not creds.valid:
            print("  Refreshing YouTube token...")
            creds.refresh(Request())
            cd["token"] = creds.token
            _save_token_to_github(cd)
        # ──────────────────────────────────────────────────────────

        yt = build('youtube', 'v3', credentials=creds)
        body = {
            'snippet': {
                'title': title[:100],
                'description': description,
                'tags': tags,
                'categoryId': '27',
                'defaultLanguage': 'en'
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False
            }
        }
        req = yt.videos().insert(
            part=','.join(body.keys()), body=body,
            media_body=MediaFileUpload(video_path, chunksize=-1,
                                       resumable=True, mimetype='video/mp4'))
        resp = None
        while resp is None:
            status, resp = req.next_chunk()
            if status: print(f"  Upload: {int(status.progress()*100)}%")

        vid_id = resp['id']
        # if thumb_path and os.path.exists(thumb_path):
        #     yt.thumbnails().set(
        #         videoId=vid_id,
        #         media_body=MediaFileUpload(thumb_path)).execute()
        return vid_id

    except Exception as e:
        print(f"Upload failed: {e}")
        return None


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    if not LIBS_OK:
        print("Missing libraries"); sys.exit(1)

    topic = TOPICS[weekday]
    tt = topic["type"]
    bc = topic["color"]

    print("="*60)
    print(f"  AI360Trading Video Bot v2 — {date_display}  [{tt}]")
    print("="*60)

    prices = get_prices()
    fg_val, fg_label = get_fg()
    np_  = prices.get("NIFTY 50",{}).get("price",24000)
    npct = prices.get("NIFTY 50",{}).get("pct",0)
    bp_  = prices.get("Bitcoin",{}).get("price",65000)
    bpct = prices.get("Bitcoin",{}).get("pct",0)

    print(f"  NIFTY  : {prices.get('NIFTY 50',{}).get('display','N/A')}")
    print(f"  BTC    : {prices.get('Bitcoin',{}).get('display','N/A')}")
    print(f"  F&G    : {fg_val} — {fg_label}")

    direction = ("Market Crash" if npct<-2 else "Big Fall" if npct<-1 else
                 "Recovery" if npct>1 else "Big Rally" if npct>2 else "At Key Levels")
    title = topic["title"].format(
        date=date_display, year=now.year,
        nifty=f"{np_:,.0f}", btc=f"{int(bp_):,}",
        direction=direction)
    desc = topic["desc"].format(date=date_display, year=now.year)

    print("\n  Generating script...")
    script = generate_script(topic, prices, fg_val, fg_label)
    if not script: sys.exit(1)
    script_slides = parse_script(script)
    print(f"  Script: {len(script)} chars | {len(script_slides)} slides")

    print("\n  Building slides...")
    img_paths = []; narrators = []

    # 0. Title
    p = os.path.join(OUTPUT_DIR,"s00_title.png")
    slide_title(title, tt.replace('_',' ').title(), bc, p)
    img_paths.append(p)
    narrators.append(f"Aaj AI360Trading par — {title}. Mere saath bane rahiye.")

    # 1. Fear & Greed
    p = os.path.join(OUTPUT_DIR,"s01_fg.png")
    slide_fear_greed(fg_val, fg_label, prices, bc, p)
    img_paths.append(p)
    narrators.append(
        f"Shuru karne se pehle — Fear and Greed index abhi {fg_val} pe hai, "
        f"matlab {fg_label}. NIFTY {prices.get('NIFTY 50',{}).get('display','N/A')}, "
        f"S&P 500 {prices.get('S&P 500',{}).get('display','N/A')}, "
        f"aur Bitcoin {prices.get('Bitcoin',{}).get('display','N/A')} pe chal raha hai.")

    # 2. Chart
    if tt in ["nifty","weekly","stocks"]:
        p = os.path.join(OUTPUT_DIR,"s02_chart.png")
        slide_candlestick_chart(prices, f"NIFTY 50 — {date_display}", bc, p)
        img_paths.append(p)
        s1n = int(np_*0.986); r1n = int(np_*1.014)
        mood = "pressure mein" if npct<-1 else "recovery mein" if npct>0 else "flat"
        narrators.append(
            f"NIFTY abhi {prices.get('NIFTY 50',{}).get('display','N/A')} pe hai — {mood}. "
            f"Jo level main dekhna chahta hoon neeche {s1n:,} hai, aur upar {r1n:,} hai. "
            f"In dono ke beech jo hoga woh batayega market kis direction mein ja rahi hai.")

    # 3. SR Table
    if tt in ["nifty","bitcoin","weekly"]:
        p = os.path.join(OUTPUT_DIR,"s03_sr.png")
        slide_sr_table(prices, bc, p)
        img_paths.append(p)
        narrators.append(
            f"Ye hain aaj ke key levels. NIFTY ke liye {int(np_*0.986):,} support pe nazar rakhna. "
            f"Bitcoin ke liye ${int(bp_*0.95):,} woh zone hai jahan buyers dikhne chahiye. "
            f"S&P 500 {prices.get('S&P 500',{}).get('display','N/A')} pe hai — "
            f"yeh raat ko kahan band hota hai kal ke NIFTY ka tone set karega.")

    # 4. Topic-specific slides
    if tt == "education":
        p = os.path.join(OUTPUT_DIR,"s04_edu.png")
        slide_education_icon("5 Must-Know Candlestick Patterns",
            ["Doji — Indecision Signal","Hammer — Reversal Bottom",
             "Hanging Man — Reversal Top","Engulfing — Strong Signal",
             "Morning Star — 3 Candle Reversal","Shooting Star — Rejection"],
            bc, p)
        img_paths.append(p)
        narrators.append("Ye hain 5 patterns jo har trader ko aane chahiye. Aaj inhe ek-ek karke samjhenge.")

    if tt == "finance":
        p = os.path.join(OUTPUT_DIR,"s04_fin.png")
        slide_finance_chart("sip_growth", prices, bc, p)
        img_paths.append(p)
        narrators.append(
            "Ye chart dekho. SIP rupees 5 hazar per month, aur lump sum rupees 6 lakh ek saath. "
            "10 saal baad SIP ne rupees 23 lakh bana diya. Lump sum ne sirf rupees 18 lakh. "
            "Iska matlab hai SIP ne zyaada returns diye? Haan — par honest answer aur complicated hai.")

    if tt == "support":
        p = os.path.join(OUTPUT_DIR,"s04_sup.png")
        slide_education_icon("Support & Resistance — Key Concepts",
            [f"S1 = {int(np_*0.986):,} — Previous swing low",
             f"R1 = {int(np_*1.014):,} — Previous swing high",
             "Round numbers = Psychological magnets",
             "Volume confirms the level",
             "Bounce trade — wait for confirmation",
             "Fake breakout = Biggest beginner trap"],
            bc, p)
        img_paths.append(p)
        narrators.append(
            f"Ye levels hain jo main aaj use kar raha hoon. {int(np_*0.986):,} support, "
            f"{int(np_*1.014):,} resistance. Inhe mark kar lo apne chart pe.")

    # Script content slides
    for i, sl in enumerate(script_slides[:8], start=len(img_paths)):
        p = os.path.join(OUTPUT_DIR,f"s{i:02d}_content.png")
        slide_content(sl.get("slide",""),sl.get("narrator",""),
                      bc, i+1, len(script_slides)+4, p)
        img_paths.append(p)
        narrators.append(sl.get("narrator",""))

    # Outro
    p = os.path.join(OUTPUT_DIR,"s_outro.png")
    slide_outro(bc, p)
    img_paths.append(p)
    narrators.append(
        "Ye the aaj ke key levels aur mera personal view. "
        "Agar ye useful laga — subscribe karo, aur kal subah market khulne se pehle milte hain.")

    # Thumbnail
    thumb_pct = bpct if tt=="bitcoin" else (abs(npct) if tt in ["education","finance","support"] else npct)
    tp = os.path.join(OUTPUT_DIR,"thumbnail.png")
    create_thumbnail(title, prices, thumb_pct, bc, tp)
    print("  Thumbnail created")

    # Assemble
    print("\n  Assembling video...")
    vp = os.path.join(OUTPUT_DIR,f"ai360_{date_str}_{tt}.mp4")
    ok = assemble(img_paths, narrators, vp)
    if not ok: sys.exit(1)
    print(f"  Video ready: {os.path.getsize(vp)/1024/1024:.1f} MB")

    # Upload
    print("\n  Uploading to YouTube...")
    vid_id = upload_yt(vp, title, desc, topic["tags"], tp)
    if vid_id:
        print(f"\n  LIVE: https://www.youtube.com/watch?v={vid_id}")
    else:
        print(f"  Saved: {vp}")
        print("  Set YOUTUBE_CREDENTIALS in GitHub Secrets to enable upload")

if __name__ == "__main__":
    main()
