"""
AI360Trading — Part 1: Global Market Analysis Video
====================================================
12 focused slides — 15 min video — uploads to YouTube
Covers: Nifty + Global Markets + Trade Setups
Best SEO: ranks for daily market analysis searches worldwide
"""

import os, sys, json, asyncio, textwrap, time, re
from datetime import datetime

import requests
import yfinance as yf
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from groq import Groq
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

OUT  = "output"
W, H = 1920, 1080
os.makedirs(OUT, exist_ok=True)

# ── PIL fix ──
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

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json", "Referer": "https://www.nseindia.com/",
}

def flatten(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def compute_indicators(df):
    df = flatten(df)
    c=df["Close"]; h=df["High"]; l=df["Low"]; v=df["Volume"]
    e20=c.ewm(span=20,adjust=False).mean()
    e50=c.ewm(span=50,adjust=False).mean()
    e200=c.ewm(span=200,adjust=False).mean()
    d=c.diff(); g=d.clip(lower=0).rolling(14).mean()
    ls=(-d.clip(upper=0)).rolling(14).mean()
    rsi=100-(100/(1+g/ls.replace(0,1e-9)))
    m12=c.ewm(span=12,adjust=False).mean(); m26=c.ewm(span=26,adjust=False).mean()
    macd=m12-m26; sig=macd.ewm(span=9,adjust=False).mean()
    s20=c.rolling(20).mean(); sd20=c.rolling(20).std()
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    yh=float(h.iloc[-2]); yl=float(l.iloc[-2]); yc=float(c.iloc[-2])
    piv=(yh+yl+yc)/3
    last=float(c.iloc[-1]); prev=float(c.iloc[-2]); chg=last-prev
    return {
        "current":round(last,2),"prev_close":round(prev,2),
        "change":round(chg,2),"change_pct":round(chg/prev*100,2),
        "open":round(float(df["Open"].iloc[-1]),2),
        "high":round(float(h.iloc[-1]),2),"low":round(float(l.iloc[-1]),2),
        "volume":int(v.iloc[-1]),"avg_volume":int(v.rolling(20).mean().iloc[-1]),
        "ema20":round(float(e20.iloc[-1]),2),"ema50":round(float(e50.iloc[-1]),2),
        "ema200":round(float(e200.iloc[-1]),2),"rsi":round(float(rsi.iloc[-1]),2),
        "macd":round(float(macd.iloc[-1]),4),"macd_signal":round(float(sig.iloc[-1]),4),
        "bb_upper":round(float((s20+2*sd20).iloc[-1]),2),
        "bb_lower":round(float((s20-2*sd20).iloc[-1]),2),
        "atr":round(float(tr.rolling(14).mean().iloc[-1]),2),
        "pivot":round(piv,2),
        "r1":round(2*piv-yl,2),"r2":round(piv+(yh-yl),2),"r3":round(yh+2*(piv-yl),2),
        "s1":round(2*piv-yh,2),"s2":round(piv-(yh-yl),2),"s3":round(yl-2*(yh-piv),2),
    }

def quick_price(ticker):
    try:
        df = flatten(yf.download(ticker, period="5d", interval="1d",
                                  progress=False, auto_adjust=True))
        if len(df) >= 2:
            last = round(float(df["Close"].iloc[-1]), 2)
            prev = round(float(df["Close"].iloc[-2]), 2)
            return {"last": last, "chg_pct": round((last-prev)/prev*100, 2)}
    except: pass
    return {"last": "N/A", "chg_pct": "N/A"}

def fetch_options(ses):
    try:
        r = ses.get("https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY", timeout=15)
        recs = r.json()["records"]["data"]
        ce = pe = 0; sk = {}
        for rec in recs:
            k=rec.get("strikePrice",0)
            co=rec.get("CE",{}).get("openInterest",0)
            po=rec.get("PE",{}).get("openInterest",0)
            ce+=co; pe+=po; sk[k]={"ce":co,"pe":po}
        pcr = round(pe/max(ce,1), 2)
        mp = min(sk, key=lambda s: sum(
            max(0,s-k)*v["ce"]+max(0,k-s)*v["pe"] for k,v in sk.items()), default=0)
        return {"pcr":pcr,"max_pain":mp,
                "max_ce":max(sk,key=lambda x:sk[x]["ce"],default=0),
                "max_pe":max(sk,key=lambda x:sk[x]["pe"],default=0)}
    except Exception as e:
        print(f"  Options: {e}")
        return {"pcr":1.0,"max_pain":0,"max_ce":0,"max_pe":0}

def fetch_fii(ses):
    try:
        r = ses.get("https://www.nseindia.com/api/fiidiiTradeReact", timeout=15)
        data = r.json()
        fii = next((x for x in data if x.get("category")=="FII/FPI"), {})
        dii = next((x for x in data if x.get("category")=="DII"), {})
        def v(d,k): return float(str(d.get(k,"0")).replace(",",""))
        return {"fii_net":v(fii,"netValue"),"dii_net":v(dii,"netValue")}
    except Exception as e:
        print(f"  FII: {e}")
        return {"fii_net":0.0,"dii_net":0.0}

def fetch_all():
    print("📡 Fetching market data...")
    ses = requests.Session(); ses.headers.update(NSE_HEADERS)
    try: ses.get("https://www.nseindia.com", timeout=10); time.sleep(1)
    except: pass
    md = {}
    for nm, tk, pd_ in [("nifty","^NSEI","250d"),("banknifty","^NSEBANK","60d")]:
        try:
            df = flatten(yf.download(tk, period=pd_, interval="1d", progress=False, auto_adjust=True))
            md[nm] = compute_indicators(df)
            print(f"  ✓ {nm}: {md[nm]['current']} ({md[nm]['change_pct']:+.2f}%)")
        except Exception as e:
            print(f"  ✗ {nm}: {e}"); md[nm] = {}
    global_tickers = {
        "sp500":"^GSPC","nasdaq":"^IXIC","bitcoin":"BTC-USD",
        "gold":"GC=F","oil":"CL=F","india_vix":"^INDIAVIX",
        "vix":"^VIX","ftse":"^FTSE","usdinr":"INR=X",
    }
    md["global"] = {}
    for nm, tk in global_tickers.items():
        result = quick_price(tk)
        if result["last"] != "N/A":
            md["global"][nm] = result
    md["options"] = fetch_options(ses)
    md["fii_dii"] = fetch_fii(ses)
    return md

# ── THEMES ──
AT = {
    "bullish": {"bg_top":(6,16,10),"bg_bot":(4,32,18),"accent":(0,210,100),
                "accent2":(0,160,75),"text":(238,255,244),"subtext":(150,210,175),
                "badge_bg":(0,175,85),"badge_txt":(0,28,14),"badge":"BULLISH"},
    "bearish": {"bg_top":(22,6,6),"bg_bot":(42,10,10),"accent":(255,70,50),
                "accent2":(195,45,35),"text":(255,244,240),"subtext":(225,165,155),
                "badge_bg":(215,45,35),"badge_txt":(255,238,235),"badge":"BEARISH"},
    "neutral": {"bg_top":(6,10,28),"bg_bot":(10,18,52),"accent":(75,145,255),
                "accent2":(55,115,205),"text":(238,244,255),"subtext":(155,180,225),
                "badge_bg":(55,115,200),"badge_txt":(228,238,255),"badge":"NEUTRAL"},
}

def global_ticker_bar(draw, md):
    gl = md.get("global", {})
    items = [("S&P500","sp500"),("NASDAQ","nasdaq"),("BTC","bitcoin"),
             ("GOLD","gold"),("OIL","oil"),("VIX","vix"),("USD/INR","usdinr")]
    f = font(FONT_BOLD, 20)
    draw.rectangle([(0, H-52),(W, H-1)], fill=(0,0,0))
    x = 30
    for label, key in items:
        d = gl.get(key, {})
        last = d.get("last","N/A"); chg = d.get("chg_pct","N/A")
        if last == "N/A": continue
        clr = (0,220,110) if isinstance(chg,float) and chg>=0 else (255,80,60)
        sign = "+" if isinstance(chg,float) and chg>=0 else ""
        text = f"{label}: {last}  {sign}{chg}%   "
        draw.text((x, H-32), text, fill=clr, font=f, anchor="lm")
        x += len(text)*11
        if x > W-100: break

def make_slide(slide, idx, total, n, md, path):
    snt = slide.get("sentiment","neutral").lower()
    if snt not in AT: snt = "neutral"
    th = AT[snt]
    img = gbg(th["bg_top"], th["bg_bot"]); draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0,0),(W,7)], fill=th["accent"])
    draw.rectangle([(0,0),(820,H)], fill=(*th["bg_top"],120))

    fS=font(FONT_REG,24); fB=font(FONT_BOLD,22)
    fT=font(FONT_BOLD,52); fBd=font(FONT_REG,28)
    fP=font(FONT_BOLD,60); fC=font(FONT_BOLD,28)
    fSL=font(FONT_REG,19); fSV=font(FONT_BOLD,20)
    fD=font(FONT_REG,17)

    draw.text((50,24), datetime.now().strftime("%d %B %Y  |  %A"), fill=th["subtext"], font=fS)
    draw.text((780,24), f"{idx}/{total}", fill=th["subtext"], font=fS, anchor="rm")
    draw.rounded_rectangle([(620,14),(780,50)], radius=7, fill=th["badge_bg"])
    draw.text((700,32), th["badge"], fill=th["badge_txt"], font=fB, anchor="mm")

    ty = 78
    for line in textwrap.wrap(slide["title"].upper(), width=22)[:2]:
        draw.text((50,ty), line, fill=th["text"], font=fT); ty += 65
    draw.rectangle([(50,ty+4),(430,ty+8)], fill=th["accent"]); ty += 24

    for sent in [s.strip() for s in slide["content"].split(".") if s.strip()][:6]:
        for ln in textwrap.wrap(sent+".", width=44):
            if ty > H-110: break
            draw.text((50,ty), ln, fill=th["text"], font=fBd); ty += 44
        ty += 3

    draw.text((50,H-60),"AI360Trading  •  ai360trading.in",fill=(*th["subtext"][:3],150),font=fD)
    draw.text((50,H-38),"Educational only. Not financial advice.",fill=(*th["subtext"][:3],100),font=fD)

    price=n.get("current",""); chg=n.get("change",0); chg_pct=n.get("change_pct",0)
    clr=th["accent"] if float(chg)>=0 else th.get("accent2",th["accent"])
    sign="+" if float(chg)>=0 else "-"
    draw.rounded_rectangle([(840,60),(1880,220)], radius=12, fill=(0,0,0,80))
    draw.text((1360,95), "NIFTY 50", fill=th["subtext"], font=fS, anchor="mm")
    draw.text((1360,150), f"{price:,}", fill=th["text"], font=fP, anchor="mm")
    draw.text((1360,198), f"{sign} {abs(float(chg)):,.2f}  ({float(chg_pct):+.2f}%)", fill=clr, font=fC, anchor="mm")

    stats = [("Open",n.get("open","")),("High",n.get("high","")),
             ("Low",n.get("low","")),("EMA20",n.get("ema20","")),
             ("EMA50",n.get("ema50","")),("EMA200",n.get("ema200","")),
             ("RSI",n.get("rsi","")),("ATR",n.get("atr",""))]
    for i,(lbl,val) in enumerate(stats):
        x=860+(i%4)*260; y=240+(i//4)*48
        draw.text((x,y), str(lbl), fill=th["subtext"], font=fSL)
        draw.text((x+110,y), str(val), fill=th["text"], font=fSV)

    lx,ly=1520,350
    draw.text((lx,ly),"KEY LEVELS",fill=th["accent"],font=font(FONT_BOLD,20)); ly+=28
    for lbl,val,c2 in [
        ("R3",n.get("r3",""),th["accent"]),("R2",n.get("r2",""),th["accent"]),
        ("R1",n.get("r1",""),th["accent"]),("Pivot",n.get("pivot",""),th["subtext"]),
        ("S1",n.get("s1",""),th.get("accent2",th["accent"])),
        ("S2",n.get("s2",""),th.get("accent2",th["accent"])),
        ("S3",n.get("s3",""),th.get("accent2",th["accent"]))]:
        draw.text((lx,ly),lbl,fill=th["subtext"],font=font(FONT_REG,18))
        draw.text((lx+72,ly),str(val),fill=c2,font=font(FONT_BOLD,19)); ly+=25

    global_ticker_bar(draw, md)
    img.save(path, quality=95)

def make_intro_slide(n, md, path):
    img = gbg((4,7,22),(7,14,46)); draw = ImageDraw.Draw(img, "RGBA")
    gl = md.get("global",{})
    draw.rectangle([(0,0),(W,7)], fill=(0,200,110))
    draw.text((W//2,120),"AI360Trading",fill=(0,218,118),font=font(FONT_BOLD,90),anchor="mm")
    draw.rectangle([(W//2-320,185),(W//2+320,192)], fill=(0,200,110))
    draw.text((W//2,250),"Daily Global Market Analysis",fill=(215,230,255),font=font(FONT_BOLD,40),anchor="mm")
    draw.text((W//2,308),datetime.now().strftime("%A, %d %B %Y"),fill=(135,175,238),font=font(FONT_REG,32),anchor="mm")

    price=n.get("current",""); chg=n.get("change",0); chg_pct=n.get("change_pct",0)
    clr=(0,218,118) if float(chg)>=0 else (255,75,55)
    sign="+" if float(chg)>=0 else "-"
    draw.rounded_rectangle([(W//2-420,375),(W//2+420,500)], radius=16, fill=(0,0,0,110))
    draw.text((W//2,408),"NIFTY 50",fill=(135,175,238),font=font(FONT_REG,26),anchor="mm")
    draw.text((W//2,468),f"{price:,}  {sign} {abs(float(chg)):,.2f}  ({float(chg_pct):+.2f}%)",fill=clr,font=font(FONT_BOLD,46),anchor="mm")

    gl_items=[("S&P 500","sp500"),("Bitcoin","bitcoin"),("Gold","gold"),("USD/INR","usdinr")]
    gx = 220
    for lbl,key in gl_items:
        d=gl.get(key,{}); last=d.get("last","N/A"); cp=d.get("chg_pct","N/A")
        if last=="N/A": gx+=370; continue
        gc=(0,210,100) if isinstance(cp,float) and cp>=0 else (255,75,55)
        gs="+" if isinstance(cp,float) and cp>=0 else ""
        draw.text((gx,545),lbl,fill=(135,175,238),font=font(FONT_REG,20),anchor="mm")
        draw.text((gx,578),f"{last}",fill=(220,235,255),font=font(FONT_BOLD,26),anchor="mm")
        draw.text((gx,608),f"{gs}{cp}%",fill=gc,font=font(FONT_REG,20),anchor="mm")
        gx+=370

    draw.text((W//2,H-42),"Educational purposes only. Not financial advice.",fill=(65,90,130),font=font(FONT_REG,20),anchor="mm")
    img.save(path, quality=95)

def make_outro_slide(path):
    img = gbg((4,7,22),(7,14,46)); draw = ImageDraw.Draw(img)
    draw.rectangle([(0,0),(W,7)], fill=(0,200,110))
    draw.text((W//2,185),"AI360Trading",fill=(0,218,118),font=font(FONT_BOLD,88),anchor="mm")
    draw.rectangle([(W//2-320,248),(W//2+320,254)], fill=(0,200,110))
    draw.text((W//2,328),"LIKE  •  SUBSCRIBE  •  SHARE",fill=(215,230,255),font=font(FONT_BOLD,44),anchor="mm")
    draw.text((W//2,415),"New market analysis every weekday morning",fill=(135,175,238),font=font(FONT_REG,28),anchor="mm")
    draw.text((W//2,488),"Watch Part 2: Today's Education Video",fill=(100,155,210),font=font(FONT_REG,28),anchor="mm")
    draw.text((W//2,558),"#StockMarket #Nifty #SP500 #Bitcoin #Trading #AI360Trading",fill=(60,105,165),font=font(FONT_REG,24),anchor="mm")
    draw.text((W//2,H-42),"Disclaimer: Educational only. Not financial advice.",fill=(55,78,118),font=font(FONT_REG,20),anchor="mm")
    img.save(path, quality=95)

def make_thumbnail(n, md, path):
    TW, TH = 1280, 720
    gl = md.get("global",{})
    price=n.get("current",""); chg_pct=n.get("change_pct",0)
    is_bull=float(chg_pct)>=0
    accent=(0,210,100) if is_bull else (255,70,50)
    bg_top=(6,16,10) if is_bull else (22,6,6)
    bg_bot=(4,32,18) if is_bull else (42,10,10)
    img = Image.new("RGB",(TW,TH)); px=img.load()
    for y in range(TH):
        c=lerp(bg_top,bg_bot,y/TH)
        for x in range(TW): px[x,y]=c
    draw = ImageDraw.Draw(img,"RGBA")
    draw.rectangle([(0,0),(18,TH)],fill=accent)
    draw.rectangle([(0,0),(TW,14)],fill=accent)
    draw.rectangle([(0,TH-14),(TW,TH)],fill=accent)
    draw.text((50,45),"AI360Trading",fill=(255,255,255),font=font(FONT_BOLD,52),anchor="lm")
    draw.text((TW-40,45),datetime.now().strftime("%d %b %Y"),fill=(180,200,240),font=font(FONT_REG,32),anchor="rm")
    draw.text((50,160),"NIFTY",fill=(180,210,255),font=font(FONT_BOLD,60))
    draw.text((50,228),f"{price:,}",fill=(255,255,255),font=font(FONT_BOLD,110))
    sign="+" if is_bull else "-"
    draw.text((50,352),f"{sign} {abs(float(chg_pct))}%  TODAY",fill=accent,font=font(FONT_BOLD,56))
    draw.rounded_rectangle([(40,448),(900,548)],radius=12,fill=(*accent[:3],40))
    draw.text((60,498),"  Market Analysis + Trade Setups",fill=(220,240,255),font=font(FONT_BOLD,30),anchor="lm")
    gl_items=[("S&P 500","sp500"),("BTC","bitcoin"),("GOLD","gold")]
    gy=148
    for lbl,key in gl_items:
        d=gl.get(key,{}); last=d.get("last","N/A"); cp=d.get("chg_pct","N/A")
        if last=="N/A": gy+=138; continue
        gc=(0,210,100) if isinstance(cp,float) and cp>=0 else (255,75,55)
        gs="+" if isinstance(cp,float) and cp>=0 else ""
        draw.text((980,gy),lbl,fill=(180,205,240),font=font(FONT_BOLD,30),anchor="lm")
        draw.text((980,gy+38),f"{last}",fill=(255,255,255),font=font(FONT_BOLD,42),anchor="lm")
        draw.text((980,gy+82),f"{gs}{cp}%",fill=gc,font=font(FONT_BOLD,28),anchor="lm")
        gy+=138
    draw.text((TW//2,TH-32),"LIKE  •  SUBSCRIBE  •  GLOBAL MARKETS DAILY",fill=(*accent[:3],200),font=font(FONT_BOLD,24),anchor="mm")
    img.save(path,quality=98)

def safe_str(val, fallback=""):
    if val is None or val=="N/A" or val=="": return fallback
    s=str(val).strip(); s=re.sub(r'[<>]','',s)
    return s if s else fallback

def build_title(n, md):
    gl=md.get("global",{}); price=safe_str(n.get("current"),"Live")
    chg_pct=n.get("change_pct",0); sp=safe_str(gl.get("sp500",{}).get("last"),"Live")
    btc=safe_str(gl.get("bitcoin",{}).get("last"),"Live")
    sign="UP" if float(chg_pct)>=0 else "DOWN"
    date_str=datetime.now().strftime("%d %b %Y")
    title=f"Nifty {price} {sign} | S&P {sp} | BTC {btc} | Market Analysis {date_str}"
    return title.strip()[:100]

def build_description(n, md):
    gl=md.get("global",{}); opt=md.get("options",{}); fii=md.get("fii_dii",{})
    price=safe_str(n.get("current"),"N/A"); chg_pct=n.get("change_pct",0)
    btc=safe_str(gl.get("bitcoin",{}).get("last"),"N/A")
    sp=safe_str(gl.get("sp500",{}).get("last"),"N/A")
    gold=safe_str(gl.get("gold",{}).get("last"),"N/A")
    date_str=datetime.now().strftime("%d %B %Y")
    return f"""📊 Global Stock Market Analysis — {date_str}

🇮🇳 NIFTY 50: {price} ({'+' if float(chg_pct)>=0 else ''}{chg_pct}%)
🇺🇸 S&P 500: {sp} | ₿ Bitcoin: {btc} | 🥇 Gold: {gold}
PCR: {opt.get('pcr','N/A')} | FII: ₹{fii.get('fii_net','N/A')}Cr | DII: ₹{fii.get('dii_net','N/A')}Cr

📈 WHAT'S COVERED IN THIS VIDEO:
✅ Global Markets Overview — US, India, Crypto, Gold, Oil
✅ Nifty 50 Complete Technical Analysis
✅ Support & Resistance Levels (S1 S2 S3 R1 R2 R3)
✅ EMA 20, 50, 200 Trend Analysis
✅ RSI + MACD + Bollinger Bands
✅ Bank Nifty Analysis
✅ FII DII Smart Money Flow
✅ Option Chain PCR + Max Pain
✅ Intraday Trade Setup (Entry, Target, Stop-Loss)
✅ Positional Swing Setup
✅ Market Outlook for Today

🌐 Website: https://ai360trading.in
📱 Telegram: https://t.me/ai360trading

⚠️ DISCLAIMER: This video is for educational purposes only.
Not financial advice. Consult a SEBI-registered advisor before investing.

#StockMarket #NiftyAnalysis #TechnicalAnalysis #MarketAnalysis
#Nifty50 #BankNifty #SP500 #Bitcoin #Gold #Trading #Investing
#IntradayTrading #SwingTrading #OptionsTrading #StockMarketToday
#MarketOutlook #NiftyPrediction #AI360Trading #GlobalMarkets
#NSE #BSE #ShareMarket #StockMarketIndia #TradingStrategy"""

ANALYSIS_SLIDES = [
    "Global Markets Overview — US, Crypto, Gold, Oil impact on India today",
    "Nifty 50 Opening Analysis — Price action, trend, and key levels",
    "Support Levels — S1 S2 S3 with exact Nifty levels for today",
    "Resistance Levels — R1 R2 R3 with exact Nifty levels for today",
    "EMA 20 50 200 — Trend direction and what it means for traders",
    "RSI and MACD — Momentum reading and signal analysis",
    "Bank Nifty — Analysis, levels, and correlation with Nifty",
    "FII DII Smart Money — Who is buying and who is selling today",
    "Option Chain PCR and Max Pain — What options data is signaling",
    "Intraday Trade Setup — Entry, target, and stop-loss with exact levels",
    "Positional Swing Setup — Multi-day trade opportunity today",
    "Market Outlook — Summary and what to expect for the session",
]

def build_prompt(md):
    n=md.get("nifty",{}); bn=md.get("banknifty",{}); gl=md.get("global",{})
    opt=md.get("options",{}); fii=md.get("fii_dii",{})
    def g(d,k): return d.get(k,"N/A")
    def glv(k): return gl.get(k,{}).get("last","N/A")
    def glc(k): return gl.get(k,{}).get("chg_pct","N/A")
    slides_list="\n".join([f"{i+1}. {s}" for i,s in enumerate(ANALYSIS_SLIDES)])
    return f"""You are a senior global markets analyst. Today is {datetime.now().strftime('%A, %d %B %Y')}.

LIVE DATA — use ONLY these real numbers:
Nifty:{g(n,'current')} Change:{g(n,'change')} ({g(n,'change_pct')}%)
Open:{g(n,'open')} High:{g(n,'high')} Low:{g(n,'low')}
EMA20:{g(n,'ema20')} EMA50:{g(n,'ema50')} EMA200:{g(n,'ema200')}
RSI:{g(n,'rsi')} MACD:{g(n,'macd')} Signal:{g(n,'macd_signal')}
BB_Upper:{g(n,'bb_upper')} BB_Lower:{g(n,'bb_lower')} ATR:{g(n,'atr')}
Pivot:{g(n,'pivot')} R1:{g(n,'r1')} R2:{g(n,'r2')} R3:{g(n,'r3')}
S1:{g(n,'s1')} S2:{g(n,'s2')} S3:{g(n,'s3')}
BankNifty:{g(bn,'current')} ({g(bn,'change_pct')}%) RSI:{g(bn,'rsi')}
S&P500:{glv('sp500')} ({glc('sp500')}%) Nasdaq:{glv('nasdaq')}
Bitcoin:{glv('bitcoin')} ({glc('bitcoin')}%) Gold:{glv('gold')} Oil:{glv('oil')}
VIX:{glv('vix')} IndiaVIX:{glv('india_vix')} USDINR:{glv('usdinr')}
PCR:{g(opt,'pcr')} MaxPain:{g(opt,'max_pain')} FII:{g(fii,'fii_net')}Cr DII:{g(fii,'dii_net')}Cr

Write EXACTLY 12 slides in JSON. Each slide:
- "title": max 6 words, engaging
- "content": 6 sentences, every sentence has a specific number from data above
- "sentiment": bullish/bearish/neutral

SLIDES IN ORDER:
{slides_list}

Respond ONLY: {{"slides":[...]}}"""

async def tts(text, path):
    voices=["en-IN-PrabhatNeural","en-IN-NeerjaNeural"]
    import random; voice=random.choice(voices)
    await edge_tts.Communicate(text, voice).save(path)

def upload_video(video_path, n, md, edu_video_id=None):
    if not os.path.exists("token.json"):
        print("❌ token.json missing"); return None
    title = build_title(n, md)
    description = build_description(n, md)
    if edu_video_id:
        description += f"\n\n▶️ WATCH PART 2 (Education): https://youtube.com/watch?v={edu_video_id}"
    tags = [
        "stock market analysis today","nifty analysis","technical analysis",
        "nifty 50","bank nifty","s&p 500","bitcoin","gold price today",
        "intraday trading","swing trading","options trading","market analysis",
        "trading strategy","support resistance","ema rsi macd","fii dii",
        "india stock market","global markets","ai360trading","share market",
        "nifty prediction","market outlook","stock market india","nse bse",
        "trading for beginners","how to trade stocks",
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
        print(f"✅ Analysis video: https://youtube.com/watch?v={vid_id}")
        # Save video ID for education video to link back
        with open(f"{OUT}/analysis_video_id.txt","w") as f: f.write(vid_id)
        # Upload thumbnail
        thumb=f"{OUT}/thumbnail_analysis.png"
        if os.path.exists(thumb):
            yt.thumbnails().set(videoId=vid_id,
                media_body=MediaFileUpload(thumb,mimetype="image/png")).execute()
        return vid_id
    except Exception as e:
        print(f"❌ Upload failed: {e}"); return None

async def run():
    md = fetch_all(); n = md.get("nifty",{})
    gkey = os.environ.get("GROQ_API_KEY")
    if not gkey: sys.exit("❌ GROQ_API_KEY not set")
    client = Groq(api_key=gkey)

    print("\n🤖 Generating 12-slide analysis script...")
    resp = client.chat.completions.create(
        messages=[{"role":"user","content":build_prompt(md)}],
        model="llama-3.3-70b-versatile",
        response_format={"type":"json_object"},
        temperature=0.55, max_tokens=5000)
    slides = json.loads(resp.choices[0].message.content)["slides"][:12]
    print(f"  ✓ {len(slides)} slides generated")

    clips = []
    gl=md.get("global",{})
    sp=safe_str(gl.get("sp500",{}).get("last"),"N/A")
    btc=safe_str(gl.get("bitcoin",{}).get("last"),"N/A")

    # Intro
    ip,ap=f"{OUT}/intro_a.png",f"{OUT}/intro_a.mp3"
    make_intro_slide(n, md, ip)
    intro_txt=(f"Welcome to AI360Trading — global markets analysis for {datetime.now().strftime('%A, %d %B %Y')}. "
               f"Nifty 50 is at {n.get('current','')} — {'up' if float(n.get('change',0))>=0 else 'down'} "
               f"{abs(float(n.get('change',0)))} points. "
               f"S and P 500 at {sp}. Bitcoin at {btc} dollars. "
               f"We cover complete analysis with trade setups in this video. Let us begin.")
    await tts(intro_txt, ap)
    ia=AudioFileClip(ap)
    clips.append(ImageClip(ip).set_duration(max(ia.duration+2,18)).set_audio(ia))

    # Analysis slides
    print("\n🎬 Rendering slides...")
    for i,s in enumerate(slides):
        ip,ap=f"{OUT}/a{i:02d}.png",f"{OUT}/a{i:02d}.mp3"
        make_slide(s, i+1, len(slides), n, md, ip)
        await tts(f"{s['title']}. {s['content']}", ap)
        au=AudioFileClip(ap); dur=max(au.duration+2,30)
        clips.append(ImageClip(ip).set_duration(dur).set_audio(au))
        print(f"  ✓ [{i+1:02d}/{len(slides)}] {s['title'][:40]:<40} {dur:.0f}s")

    # Outro
    op,oap=f"{OUT}/outro_a.png",f"{OUT}/outro_a.mp3"
    make_outro_slide(op)
    outro_txt=(f"That is our complete market analysis for today. "
               f"We covered Nifty, global markets, FII DII data, options chain, and trade setups. "
               f"Watch Part 2 — today's education video — for deep learning on trading concepts. "
               f"Like this video, subscribe, and share with fellow traders. "
               f"Comment your Nifty view for today. See you tomorrow morning. Trade safe.")
    await tts(outro_txt, oap)
    oa=AudioFileClip(oap)
    clips.append(ImageClip(op).set_duration(max(oa.duration+2,18)).set_audio(oa))

    # Render
    final=f"{OUT}/analysis_video.mp4"
    total_mins=sum(c.duration for c in clips)/60
    print(f"\n🎥 Rendering {len(clips)} clips — {total_mins:.1f} minutes...")
    concatenate_videoclips(clips,method="compose").write_videofile(
        final,fps=24,codec="libx264",audio_codec="aac",bitrate="4000k",logger=None)
    print(f"✅ {final} ({os.path.getsize(final)/1e6:.1f} MB) {total_mins:.1f} min")

    make_thumbnail(n, md, f"{OUT}/thumbnail_analysis.png")
    vid_id = upload_video(final, n, md)
    if vid_id:
        with open(f"{OUT}/analysis_video_id.txt","w") as f: f.write(vid_id)

if __name__ == "__main__":
    asyncio.run(run())
