"""
AI360Trading — Complete Daily Video Generator
=============================================
Every video has TWO parts:
  PART 1 — Live Market Analysis (20 slides, real data)
  PART 2 — Education Capsule (smart topic by day-of-week)

ALL audiences covered every day:
  Beginners | Intraday | Options | Positional | Investors | News followers
"""

import os, sys, json, asyncio, textwrap, time
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
from content_calendar import get_todays_education_topic

# ══════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════
OUT  = "output"
W, H = 1920, 1080
os.makedirs(OUT, exist_ok=True)

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json","Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/","Connection": "keep-alive",
}
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
    img=Image.new("RGB",(W,H)); px=img.load()
    for y in range(H):
        c=lerp(top,bot,y/H)
        for x in range(W): px[x,y]=c
    return img

# ══════════════════════════════════════════════════════════
# MARKET DATA
# ══════════════════════════════════════════════════════════
def nse_session():
    s=requests.Session(); s.headers.update(NSE_HEADERS)
    try: s.get("https://www.nseindia.com",timeout=10); time.sleep(1)
    except: pass
    return s

def flatten_df(df):
    """Fix yfinance multi-level column issue in newer versions."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def compute_indicators(df):
    df = flatten_df(df)
    c=df["Close"]; h=df["High"]; l=df["Low"]; v=df["Volume"]
    e20=c.ewm(span=20,adjust=False).mean(); e50=c.ewm(span=50,adjust=False).mean(); e200=c.ewm(span=200,adjust=False).mean()
    d=c.diff(); g=d.clip(lower=0).rolling(14).mean(); ls=(-d.clip(upper=0)).rolling(14).mean()
    rsi=100-(100/(1+g/ls.replace(0,1e-9)))
    m12=c.ewm(span=12,adjust=False).mean(); m26=c.ewm(span=26,adjust=False).mean()
    macd=m12-m26; sig=macd.ewm(span=9,adjust=False).mean()
    s20=c.rolling(20).mean(); sd20=c.rolling(20).std()
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    yh=float(h.iloc[-2]); yl=float(l.iloc[-2]); yc=float(c.iloc[-2]); piv=(yh+yl+yc)/3
    last=float(c.iloc[-1]); prev=float(c.iloc[-2]); chg=last-prev
    return {"current":round(last,2),"prev_close":round(prev,2),"change":round(chg,2),
            "change_pct":round(chg/prev*100,2),"open":round(float(df["Open"].iloc[-1]),2),
            "high":round(float(h.iloc[-1]),2),"low":round(float(l.iloc[-1]),2),
            "volume":int(v.iloc[-1]),"avg_volume":int(v.rolling(20).mean().iloc[-1]),
            "ema20":round(float(e20.iloc[-1]),2),"ema50":round(float(e50.iloc[-1]),2),
            "ema200":round(float(e200.iloc[-1]),2),"rsi":round(float(rsi.iloc[-1]),2),
            "macd":round(float(macd.iloc[-1]),4),"macd_signal":round(float(sig.iloc[-1]),4),
            "macd_hist":round(float((macd-sig).iloc[-1]),4),
            "bb_upper":round(float((s20+2*sd20).iloc[-1]),2),
            "bb_lower":round(float((s20-2*sd20).iloc[-1]),2),"bb_mid":round(float(s20.iloc[-1]),2),
            "atr":round(float(tr.rolling(14).mean().iloc[-1]),2),
            "pivot":round(piv,2),"r1":round(2*piv-yl,2),"r2":round(piv+(yh-yl),2),"r3":round(yh+2*(piv-yl),2),
            "s1":round(2*piv-yh,2),"s2":round(piv-(yh-yl),2),"s3":round(yl-2*(yh-piv),2)}

def fetch_options(ses):
    try:
        r=ses.get("https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY",timeout=15)
        recs=r.json()["records"]["data"]; ce=pe=0; sk={}
        for rec in recs:
            k=rec.get("strikePrice",0); co=rec.get("CE",{}).get("openInterest",0); po=rec.get("PE",{}).get("openInterest",0)
            ce+=co; pe+=po; sk[k]={"ce":co,"pe":po}
        pcr=round(pe/max(ce,1),2)
        mp=min(sk,key=lambda s:sum(max(0,s-k)*v["ce"]+max(0,k-s)*v["pe"] for k,v in sk.items()),default=0)
        return {"pcr":pcr,"max_pain":mp,"max_ce":max(sk,key=lambda x:sk[x]["ce"],default=0),"max_pe":max(sk,key=lambda x:sk[x]["pe"],default=0)}
    except Exception as e: print(f"  ⚠ Options:{e}"); return {"pcr":1.0,"max_pain":0,"max_ce":0,"max_pe":0}

def fetch_fii(ses):
    try:
        r=ses.get("https://www.nseindia.com/api/fiidiiTradeReact",timeout=15); data=r.json()
        fii=next((x for x in data if x.get("category")=="FII/FPI"),{})
        dii=next((x for x in data if x.get("category")=="DII"),{})
        def v(d,k): return float(str(d.get(k,"0")).replace(",",""))
        return {"fii_net":v(fii,"netValue"),"fii_buy":v(fii,"buyValue"),"fii_sell":v(fii,"sellValue"),
                "dii_net":v(dii,"netValue"),"dii_buy":v(dii,"buyValue"),"dii_sell":v(dii,"sellValue")}
    except Exception as e: print(f"  ⚠ FII:{e}"); return {k:0.0 for k in ["fii_net","fii_buy","fii_sell","dii_net","dii_buy","dii_sell"]}

def fetch_all():
    print("📡 Fetching live market data..."); ses=nse_session(); md={}
    for nm,tk,pd_ in [("nifty","^NSEI","250d"),("banknifty","^NSEBANK","60d")]:
        try:
            df=flatten_df(yf.download(tk,period=pd_,interval="1d",progress=False,auto_adjust=True))
            md[nm]=compute_indicators(df); print(f"  ✓ {nm}: {md[nm]['current']} ({md[nm]['change_pct']:+.2f}%)")
        except Exception as e: print(f"  ✗ {nm}: {e}"); md[nm]={}
    md["global"]={}
    for nm,tk in [("dow","^DJI"),("nasdaq","^IXIC"),("sp500","^GSPC"),("india_vix","^INDIAVIX")]:
        try:
            h=flatten_df(yf.download(tk,period="5d",interval="1d",progress=False,auto_adjust=True))
            if len(h)>=2:
                last=float(h["Close"].iloc[-1]); prev=float(h["Close"].iloc[-2])
                md["global"][nm]={"last":round(last,2),"chg_pct":round((last-prev)/prev*100,2)}
        except: pass
    md["options"]=fetch_options(ses); md["fii_dii"]=fetch_fii(ses)
    print(f"  ✓ PCR={md['options']['pcr']} | FII={md['fii_dii']['fii_net']}Cr"); return md

# ══════════════════════════════════════════════════════════
# PROMPTS
# ══════════════════════════════════════════════════════════
def analysis_prompt(md):
    n=md.get("nifty",{}); bn=md.get("banknifty",{}); gl=md.get("global",{})
    opt=md.get("options",{}); fii=md.get("fii_dii",{})
    def g(d,k): return d.get(k,"N/A")
    return f"""Senior Indian stock market analyst. {datetime.now().strftime('%A, %d %B %Y')}.
REAL DATA ONLY — never invent numbers:
Nifty:{g(n,'current')} Chg:{g(n,'change')}({g(n,'change_pct')}%) O:{g(n,'open')} H:{g(n,'high')} L:{g(n,'low')}
EMA20:{g(n,'ema20')} EMA50:{g(n,'ema50')} EMA200:{g(n,'ema200')}
RSI:{g(n,'rsi')} MACD:{g(n,'macd')} Sig:{g(n,'macd_signal')} Hist:{g(n,'macd_hist')}
BB_Up:{g(n,'bb_upper')} Mid:{g(n,'bb_mid')} Lo:{g(n,'bb_lower')} ATR:{g(n,'atr')}
Piv:{g(n,'pivot')} R1:{g(n,'r1')} R2:{g(n,'r2')} R3:{g(n,'r3')} S1:{g(n,'s1')} S2:{g(n,'s2')} S3:{g(n,'s3')}
BankNifty:{g(bn,'current')}({g(bn,'change_pct')}%) RSI:{g(bn,'rsi')} EMA20:{g(bn,'ema20')} EMA50:{g(bn,'ema50')}
PCR:{g(opt,'pcr')} MaxPain:{g(opt,'max_pain')} MaxCE_Strike:{g(opt,'max_ce')} MaxPE_Strike:{g(opt,'max_pe')}
FII_Net:Rs{g(fii,'fii_net')}Cr DII_Net:Rs{g(fii,'dii_net')}Cr
Dow:{gl.get('dow',{{}}).get('last','N/A')}({gl.get('dow',{{}}).get('chg_pct','N/A')}%)
Nasdaq:{gl.get('nasdaq',{{}}).get('last','N/A')} IndiaVIX:{gl.get('india_vix',{{}}).get('last','N/A')}

Write EXACTLY 20 slides. "title"(max 5 words), "content"(6 sentences, every sentence has a real number), "sentiment"(bullish/bearish/neutral).
Topics: 1.Market Overview 2.Global Cues 3.Opening Gap 4.Support Levels(S1 S2 S3) 5.Resistance(R1 R2 R3) 6.EMA Trend 7.RSI 8.MACD 9.Bollinger Bands 10.Volume 11.India VIX 12.Bank Nifty 13.FII DII 14.Option Chain PCR 15.Max Pain 16.Sector Focus 17.Stock Focus 18.Intraday Setup(real entry/target/SL) 19.Positional Setup(real levels) 20.Option Setup(real strike/expiry)
Tone: CNBC-TV18. Confident. Specific numbers always. Respond in json format only: {{"slides":[...]}}"""

def education_prompt(topic):
    slides_info="\n".join([f"Slide {i+1}: {s['heading']} — {'; '.join(s['points'])}" for i,s in enumerate(topic['slides'])])
    return f"""Top Indian stock market educator. Like Pranjal Kamra meets Rachana Ranade.
Topic: {topic['title']} | Category: {topic['category']} | Level: {topic['level']}
Slides to write:
{slides_info}
For each slide: "title"(exact heading), "content"(5-6 sentences, simple Hindi-friendly English, real examples using Reliance/TCS/SBI/Nifty, practical numbers, one actionable takeaway at end), "sentiment":"neutral"
Total: {len(topic['slides'])} slides. Respond in json format only: {{"slides":[...]}}"""

# ══════════════════════════════════════════════════════════
# SLIDE THEMES
# ══════════════════════════════════════════════════════════
AT={"bullish":{"bg_top":(6,16,10),"bg_bot":(4,32,18),"accent":(0,210,100),"accent2":(0,160,75),"text":(238,255,244),"subtext":(150,210,175),"badge_bg":(0,175,85),"badge_txt":(0,28,14),"badge":"▲ BULLISH"},
    "bearish":{"bg_top":(22,6,6),"bg_bot":(42,10,10),"accent":(255,70,50),"accent2":(195,45,35),"text":(255,244,240),"subtext":(225,165,155),"badge_bg":(215,45,35),"badge_txt":(255,238,235),"badge":"▼ BEARISH"},
    "neutral":{"bg_top":(6,10,28),"bg_bot":(10,18,52),"accent":(75,145,255),"accent2":(55,115,205),"text":(238,244,255),"subtext":(155,180,225),"badge_bg":(55,115,200),"badge_txt":(228,238,255),"badge":"◆ NEUTRAL"}}
ET={"Options":{"bg_top":(20,5,35),"bg_bot":(35,10,60),"accent":(180,100,255),"text":(248,240,255),"subtext":(195,165,235)},
    "Technical Analysis":{"bg_top":(5,20,35),"bg_bot":(8,35,65),"accent":(0,180,255),"text":(235,248,255),"subtext":(155,195,230)},
    "Fundamental Analysis":{"bg_top":(5,30,15),"bg_bot":(8,55,25),"accent":(0,220,130),"text":(235,255,245),"subtext":(150,215,180)},
    "Trading Strategy":{"bg_top":(30,20,5),"bg_bot":(55,35,8),"accent":(255,170,0),"text":(255,250,235),"subtext":(230,200,150)},
    "Psychology":{"bg_top":(30,5,20),"bg_bot":(55,8,35),"accent":(255,80,150),"text":(255,238,248),"subtext":(230,165,200)},
    "Risk Management":{"bg_top":(35,10,5),"bg_bot":(60,20,8),"accent":(255,120,50),"text":(255,245,238),"subtext":(230,185,160)},
    "Sector Analysis":{"bg_top":(5,25,30),"bg_bot":(8,45,55),"accent":(0,210,200),"text":(235,255,254),"subtext":(150,210,205)},
    "News & Events":{"bg_top":(25,25,5),"bg_bot":(45,45,8),"accent":(220,220,0),"text":(255,255,235),"subtext":(215,215,150)},
    "Personal Finance":{"bg_top":(5,30,25),"bg_bot":(8,55,45),"accent":(0,230,180),"text":(235,255,250),"subtext":(150,215,200)},
    "IPO & New Listings":{"bg_top":(20,5,30),"bg_bot":(38,8,55),"accent":(200,120,255),"text":(248,235,255),"subtext":(195,160,235)},
    "Trading Plan":{"bg_top":(5,25,30),"bg_bot":(8,45,55),"accent":(80,200,255),"text":(235,250,255),"subtext":(155,200,230)}}

def mini_candles(draw,th,x0=1025,y0=160,cw=30,gap=50,ch=185):
    data=[(0.2,0.7,0.25,0.65),(0.4,0.85,0.6,0.78),(0.5,0.9,0.45,0.7),(0.3,0.78,0.6,0.75),(0.55,0.92,0.5,0.88),(0.6,0.95,0.55,0.9),(0.58,0.98,0.62,0.96)]
    for i,(lo,hi,o,c) in enumerate(data):
        x=x0+i*gap; bull=c>=o; clr=th["accent"] if bull else th.get("accent2",th["accent"])
        draw.line([(x+cw//2,int(y0+(1-hi)*ch)),(x+cw//2,int(y0+(1-lo)*ch))],fill=clr,width=2)
        bt=int(y0+(1-max(o,c))*ch); bb=int(y0+(1-min(o,c))*ch)
        draw.rounded_rectangle([(x,bt),(x+cw,bt+max(bb-bt,5))],radius=3,fill=clr)

def make_analysis_slide(slide,idx,total,n,path):
    snt=slide.get("sentiment","neutral").lower()
    if snt not in AT: snt="neutral"
    th=AT[snt]; img=gbg(th["bg_top"],th["bg_bot"]); draw=ImageDraw.Draw(img,"RGBA")
    draw.rectangle([(0,0),(870,H)],fill=(*th["bg_top"],130))
    draw.rectangle([(0,0),(W,7)],fill=th["accent"])
    fS=font(FONT_REG,24); fB=font(FONT_BOLD,22); fT=font(FONT_BOLD,56); fBd=font(FONT_REG,29)
    fSL=font(FONT_REG,20); fSV=font(FONT_BOLD,22); fP=font(FONT_BOLD,64); fC=font(FONT_BOLD,32); fD=font(FONT_REG,18)
    draw.text((50,24),datetime.now().strftime("%d %B %Y  |  %A"),fill=th["subtext"],font=fS)
    draw.text((820,24),f"ANALYSIS {idx}/{total}",fill=th["subtext"],font=fS,anchor="rm")
    bw=155; draw.rounded_rectangle([(680,14),(680+bw,50)],radius=7,fill=th["badge_bg"])
    draw.text((680+bw//2,32),th["badge"],fill=th["badge_txt"],font=fB,anchor="mm")
    ty=80
    for line in textwrap.wrap(slide["title"].upper(),width=22)[:2]:
        draw.text((50,ty),line,fill=th["text"],font=fT); ty+=70
    draw.rectangle([(50,ty+4),(460,ty+8)],fill=th["accent"]); ty+=26
    for sent in [s.strip() for s in slide["content"].split(".") if s.strip()][:6]:
        for ln in textwrap.wrap(sent+".",width=44):
            if ty>H-100: break
            draw.text((50,ty),ln,fill=th["text"],font=fBd); ty+=46
        ty+=5
    draw.text((50,H-30),"For educational purposes only. Not financial advice.",fill=(*th["subtext"][:3],115),font=fD)
    draw.rectangle([(872,0),(876,H)],fill=(*th["accent"][:3],50))
    mini_candles(draw,th)
    price=n.get("current",""); chg=n.get("change",0); chg_pct=n.get("change_pct",0)
    clr=th["accent"] if float(chg)>=0 else th.get("accent2",th["accent"])
    sign="▲" if float(chg)>=0 else "▼"
    draw.rounded_rectangle([(900,415),(1890,565)],radius=14,fill=(0,0,0,90))
    draw.text((1395,455),"NIFTY 50",fill=th["subtext"],font=fS,anchor="mm")
    draw.text((1395,515),f"{price:,}",fill=th["text"],font=fP,anchor="mm")
    draw.text((1395,595),f"{sign} {abs(float(chg)):,.2f}  ({float(chg_pct):+.2f}%)",fill=clr,font=fC,anchor="mm")
    for i,(lbl,val) in enumerate([("Open",n.get("open","")),("High",n.get("high","")),("Low",n.get("low","")),("EMA20",n.get("ema20","")),("EMA50",n.get("ema50","")),("EMA200",n.get("ema200","")),("RSI",n.get("rsi","")),("ATR",n.get("atr",""))]):
        x=920+(i%2)*480; y=660+(i//2)*55
        draw.text((x,y),str(lbl),fill=th["subtext"],font=fSL); draw.text((x+155,y),str(val),fill=th["text"],font=fSV)
    lx,ly=1520,650; fSR=font(FONT_BOLD,20); fSL2=font(FONT_REG,19)
    draw.text((lx,ly),"KEY LEVELS",fill=th["accent"],font=fSR); ly+=30
    for lbl,val,c2 in [("R3",n.get("r3",""),th["accent"]),("R2",n.get("r2",""),th["accent"]),("R1",n.get("r1",""),th["accent"]),("Pivot",n.get("pivot",""),th["subtext"]),("S1",n.get("s1",""),th.get("accent2",th["accent"])),("S2",n.get("s2",""),th.get("accent2",th["accent"])),("S3",n.get("s3",""),th.get("accent2",th["accent"]))]:
        draw.text((lx,ly),lbl,fill=th["subtext"],font=fSL2); draw.text((lx+78,ly),str(val),fill=c2,font=fSR); ly+=27
    img.save(path,quality=95)

def make_edu_slide(slide,idx,total,topic_title,category,level,path):
    cat=category if category in ET else "Technical Analysis"
    th=ET[cat]; img=gbg(th["bg_top"],th["bg_bot"]); draw=ImageDraw.Draw(img,"RGBA")
    draw.rectangle([(0,0),(920,H)],fill=(*th["bg_top"],140))
    draw.rectangle([(0,0),(W,7)],fill=th["accent"])
    fCat=font(FONT_BOLD,20); fS=font(FONT_REG,24); fBdg=font(FONT_BOLD,20)
    fT=font(FONT_BOLD,52); fBd=font(FONT_REG,30); fD=font(FONT_REG,18); fPt=font(FONT_REG,25)
    lc={"Beginner":(0,200,100),"Intermediate":(255,170,0),"Advanced":(255,70,70),"All Levels":(80,180,255)}.get(level,(100,180,255))
    draw.text((50,24),f"EDUCATION  •  {category.upper()}",fill=th["subtext"],font=fCat)
    draw.rounded_rectangle([(680,14),(860,50)],radius=7,fill=lc)
    draw.text((770,32),level.upper(),fill=(10,10,10),font=fBdg,anchor="mm")
    draw.text((50,58),topic_title,fill=(*th["subtext"][:3],180),font=font(FONT_REG,20))
    heading=slide.get("title",slide.get("heading",""))
    ty=90
    for line in textwrap.wrap(heading.upper(),width=24)[:2]:
        draw.text((50,ty),line,fill=th["text"],font=fT); ty+=66
    draw.rectangle([(50,ty+4),(500,ty+8)],fill=th["accent"]); ty+=26
    for sent in [s.strip() for s in slide["content"].split(".") if s.strip()][:6]:
        for ln in textwrap.wrap(sent+".",width=46):
            if ty>H-105: break
            draw.text((50,ty),ln,fill=th["text"],font=fBd); ty+=46
        ty+=5
    draw.text((50,H-30),"For educational purposes only. Not financial advice.",fill=(*th["subtext"][:3],115),font=fD)
    draw.rectangle([(922,0),(926,H)],fill=(*th["accent"][:3],50))
    # Right panel — big number + key points
    draw.text((1450,145),f"{idx}",fill=(*th["accent"][:3],30),font=font(FONT_BOLD,220),anchor="mm")
    draw.rounded_rectangle([(960,375),(1900,790)],radius=20,fill=(0,0,0,100))
    draw.text((1430,415),"KEY TAKEAWAYS",fill=th["accent"],font=font(FONT_BOLD,24),anchor="mm")
    nums="①②③④⑤"; pts=[s.strip() for s in slide["content"].split(".") if s.strip()][:4]
    pt_y=458
    for i,pt in enumerate(pts):
        short=(pt[:65]+"…") if len(pt)>65 else pt
        draw.rounded_rectangle([(978,pt_y-6),(1882,pt_y+44)],radius=8,fill=(*th["accent"][:3],20))
        draw.text((1000,pt_y+18),f"{nums[i]}  {short}",fill=th["text"],font=fPt,anchor="lm"); pt_y+=72
    prog=int(860*(idx/total))
    draw.rectangle([(960,835),(1820,852)],fill=(255,255,255,30))
    draw.rectangle([(960,835),(960+prog,852)],fill=th["accent"])
    draw.text((1390,872),f"Lesson {idx} of {total}",fill=th["subtext"],font=fS,anchor="mm")
    img.save(path,quality=95)

def make_divider(title,sub,accent,path):
    img=gbg((4,7,22),(7,14,46)); draw=ImageDraw.Draw(img)
    draw.rectangle([(0,0),(W,7)],fill=accent); draw.rectangle([(0,H-7),(W,H)],fill=accent)
    draw.text((W//2,H//2),title.upper(),fill=(*accent[:3],18),font=font(FONT_BOLD,160),anchor="mm")
    draw.rounded_rectangle([(W//2-460,H//2-95),(W//2+460,H//2+95)],radius=20,fill=(0,0,0,120))
    draw.text((W//2,H//2-28),title,fill=accent,font=font(FONT_BOLD,58),anchor="mm")
    draw.text((W//2,H//2+42),sub,fill=(200,220,255),font=font(FONT_REG,30),anchor="mm")
    img.save(path,quality=95)

def make_intro(n,edu,path):
    img=gbg((4,7,22),(7,14,46)); draw=ImageDraw.Draw(img)
    draw.rectangle([(0,0),(W,7)],fill=(0,200,110))
    draw.text((W//2,155),"AI360Trading",fill=(0,218,118),font=font(FONT_BOLD,96),anchor="mm")
    draw.rectangle([(W//2-340,213),(W//2+340,220)],fill=(0,200,110))
    draw.text((W//2,285),"Daily NIFTY Analysis + Education",fill=(215,230,255),font=font(FONT_BOLD,44),anchor="mm")
    draw.text((W//2,350),datetime.now().strftime("%A, %d %B %Y"),fill=(135,175,238),font=font(FONT_REG,34),anchor="mm")
    price=n.get("current",""); chg=n.get("change",0); chg_pct=n.get("change_pct",0)
    clr=(0,218,118) if float(chg)>=0 else (255,75,55); sign="▲" if float(chg)>=0 else "▼"
    draw.rounded_rectangle([(W//2-380,405),(W//2+380,515)],radius=16,fill=(0,0,0,110))
    draw.text((W//2,440),"NIFTY 50",fill=(135,175,238),font=font(FONT_REG,26),anchor="mm")
    draw.text((W//2,490),f"{price:,}  {sign} {abs(float(chg)):,.2f}  ({float(chg_pct):+.2f}%)",fill=clr,font=font(FONT_BOLD,50),anchor="mm")
    draw.text((W//2,560),f"Today's Education:  {edu['title']}",fill=(180,210,255),font=font(FONT_BOLD,24),anchor="mm")
    draw.text((W//2,608),f"{edu['category']}  •  {edu['level']}",fill=(120,155,210),font=font(FONT_REG,26),anchor="mm")
    draw.text((W//2,680),"Analysis  •  Trade Setups  •  Option Chain  •  FII/DII  •  Education",fill=(85,125,185),font=font(FONT_REG,26),anchor="mm")
    draw.text((W//2,H-42),"For educational purposes only. Not financial advice. Consult a SEBI-registered advisor.",fill=(65,90,130),font=font(FONT_REG,20),anchor="mm")
    img.save(path,quality=95)

def make_outro(path):
    img=gbg((4,7,22),(7,14,46)); draw=ImageDraw.Draw(img)
    draw.rectangle([(0,0),(W,7)],fill=(0,200,110))
    draw.text((W//2,195),"AI360Trading",fill=(0,218,118),font=font(FONT_BOLD,88),anchor="mm")
    draw.rectangle([(W//2-340,257),(W//2+340,263)],fill=(0,200,110))
    draw.text((W//2,345),"LIKE  •  SUBSCRIBE  •  SHARE",fill=(215,230,255),font=font(FONT_BOLD,44),anchor="mm")
    draw.text((W//2,435),"New analysis + education every morning before market opens",fill=(135,175,238),font=font(FONT_REG,28),anchor="mm")
    draw.text((W//2,510),"Drop your market view in the comments below!",fill=(100,155,210),font=font(FONT_REG,28),anchor="mm")
    draw.text((W//2,610),"#Nifty #Options #TechnicalAnalysis #StockMarket #Trading #AI360Trading",fill=(65,108,165),font=font(FONT_REG,24),anchor="mm")
    draw.text((W//2,H-42),"Disclaimer: Educational only. Not financial advice.",fill=(55,78,118),font=font(FONT_REG,20),anchor="mm")
    img.save(path,quality=95)

# ══════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ══════════════════════════════════════════════════════════
def upload(video_path,n,edu):
    if not os.path.exists("token.json"): print("❌ token.json missing."); return
    price=n.get("current",""); chg_pct=n.get("change_pct",0)
    sign="UP" if float(chg_pct)>=0 else "DOWN"
    title=f"NIFTY {datetime.now().strftime('%d %b %Y')} | {price} {sign} {abs(float(chg_pct))}% | {edu['title'][:38]}"
    desc=f"""📊 NIFTY 50 Daily Analysis + Education — {datetime.now().strftime('%d %B %Y')}
Nifty: {price} ({'+' if float(chg_pct)>=0 else ''}{chg_pct}%)

🔴 MARKET ANALYSIS: Support/Resistance • EMA • RSI • MACD • Bollinger Bands • Volume • India VIX • Bank Nifty • FII/DII • Option Chain PCR & Max Pain • Intraday Setup • Positional Setup • Option Trade Setup

📚 EDUCATION TODAY: {edu['title']} | {edu['level']} | {edu['category']}

⚠️ Educational only. Not financial advice. Consult SEBI-registered advisor.
#Nifty #Nifty50 #OptionsTrading #TechnicalAnalysis #StockMarket #Intraday #SwingTrading #FIIDii #OptionChain #AI360Trading #{edu['category'].replace(' ','')}"""
    try:
        creds=Credentials.from_authorized_user_file("token.json"); youtube=build("youtube","v3",credentials=creds)
        req=youtube.videos().insert(part="snippet,status",
            body={"snippet":{"title":title,"description":desc,
                             "tags":["Nifty","Options","Technical Analysis","Stock Market India","Intraday","Bank Nifty","RSI","MACD","FII DII","Option Chain","AI360Trading",edu['category'],edu['level']],"categoryId":"27"},
                  "status":{"privacyStatus":"public","selfDeclaredMadeForKids":False}},
            media_body=MediaFileUpload(video_path,chunksize=-1,resumable=True))
        resp=req.execute(); print(f"\n✅ LIVE: https://www.youtube.com/watch?v={resp['id']}\n")
    except Exception as e: print(f"❌ Upload: {e}"); raise

# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
VOICES=["en-IN-PrabhatNeural","en-IN-NeerjaNeural"]

async def tts(text,voice,path):
    await edge_tts.Communicate(text,voice).save(path)

async def run():
    md=fetch_all(); n=md.get("nifty",{})
    edu=get_todays_education_topic()
    print(f"\n📚 Today: {edu['title']} ({edu['category']}, {edu['level']})")

    gkey=os.environ.get("GROQ_API_KEY")
    if not gkey: sys.exit("❌ GROQ_API_KEY not set.")
    client=Groq(api_key=gkey)

    print("\n🤖 Generating scripts...")
    ar=client.chat.completions.create(messages=[{"role":"user","content":analysis_prompt(md)}],
        model="llama-3.3-70b-versatile",response_format={"type":"json_object"},temperature=0.55,max_tokens=7000)
    as_slides=json.loads(ar.choices[0].message.content)["slides"]
    print(f"  ✓ {len(as_slides)} analysis slides")

    er=client.chat.completions.create(messages=[{"role":"user","content":education_prompt(edu)}],
        model="llama-3.3-70b-versatile",response_format={"type":"json_object"},temperature=0.7,max_tokens=5000)
    ed_slides=json.loads(er.choices[0].message.content)["slides"]
    print(f"  ✓ {len(ed_slides)} education slides")

    clips=[]
    # Intro
    ip,iap=f"{OUT}/intro.png",f"{OUT}/intro.mp3"; make_intro(n,edu,ip)
    it=(f"Namaste and welcome to AI360Trading. Today is {datetime.now().strftime('%A, %d %B %Y')}. "
        f"Nifty 50 is at {n.get('current','')} — {'up' if float(n.get('change',0))>=0 else 'down'} "
        f"by {abs(float(n.get('change',0)))} points. "
        f"Today's video has complete live market analysis with trade setups for intraday, positional and options traders, "
        f"plus our education segment on {edu['title']} for {edu['level']} level. "
        "Something valuable for everyone. Let us begin.")
    await tts(it,VOICES[0],iap); ia=AudioFileClip(iap)
    clips.append(ImageClip(ip).set_duration(max(ia.duration+2,18)).set_audio(ia))

    # Analysis divider
    adp,adap=f"{OUT}/div_a.png",f"{OUT}/div_a.mp3"
    make_divider("LIVE MARKET ANALYSIS",f"NIFTY {n.get('current','')}  |  {datetime.now().strftime('%d %B %Y')}",(0,210,100),adp)
    await tts("Part One. Live Market Analysis with complete trade setups.",VOICES[0],adap); ada=AudioFileClip(adap)
    clips.append(ImageClip(adp).set_duration(max(ada.duration+1,5)).set_audio(ada))

    print("\n🎬 Analysis slides...")
    an=len(as_slides)
    for i,s in enumerate(as_slides):
        ip2,ap2=f"{OUT}/a{i:02d}.png",f"{OUT}/a{i:02d}.mp3"
        make_analysis_slide(s,i+1,an,n,ip2)
        await tts(f"{s['title']}. {s['content']}",VOICES[i%2],ap2)
        au=AudioFileClip(ap2); dur=max(au.duration+2,32)
        clips.append(ImageClip(ip2).set_duration(dur).set_audio(au))
        print(f"  ✓ [A{i+1:02d}/{an}] {s['title'][:38]:<38} {dur:.0f}s")

    # Education divider
    eth=ET.get(edu['category'],ET['Technical Analysis'])
    edp,edap=f"{OUT}/div_e.png",f"{OUT}/div_e.mp3"
    make_divider("TODAY'S EDUCATION",f"{edu['title']}  |  {edu['level']}",eth["accent"],edp)
    await tts(f"Part Two. Education. Today we learn about {edu['title']}. This is {edu['level']} level content.",VOICES[0],edap)
    eda=AudioFileClip(edap); clips.append(ImageClip(edp).set_duration(max(eda.duration+1,6)).set_audio(eda))

    print("\n🎬 Education slides...")
    en=len(ed_slides)
    for i,s in enumerate(ed_slides):
        ip3,ap3=f"{OUT}/e{i:02d}.png",f"{OUT}/e{i:02d}.mp3"
        make_edu_slide(s,i+1,en,edu['title'],edu['category'],edu['level'],ip3)
        await tts(f"{s.get('title',s.get('heading',''))}. {s['content']}",VOICES[i%2],ap3)
        au=AudioFileClip(ap3); dur=max(au.duration+2,35)
        clips.append(ImageClip(ip3).set_duration(dur).set_audio(au))
        print(f"  ✓ [E{i+1:02d}/{en}] {s.get('title','')[:38]:<38} {dur:.0f}s")

    # Outro
    op,oap=f"{OUT}/outro.png",f"{OUT}/outro.mp3"; make_outro(op)
    ot=(f"That is all for today's AI360Trading. We covered live Nifty analysis with intraday, positional and option setups, "
        f"and today's education on {edu['title']}. "
        "If this was helpful, please like, subscribe and share. "
        "Comment your market view below — we read every comment. "
        "See you tomorrow morning. Trade safe. Jai Hind.")
    await tts(ot,VOICES[0],oap); oa=AudioFileClip(oap)
    clips.append(ImageClip(op).set_duration(max(oa.duration+3,22)).set_audio(oa))

    final=f"{OUT}/final_video.mp4"
    total_mins=sum(c.duration for c in clips)/60
    print(f"\n🎥 Rendering {len(clips)} clips — {total_mins:.1f} minutes...")
    concatenate_videoclips(clips,method="compose").write_videofile(
        final,fps=24,codec="libx264",audio_codec="aac",bitrate="4000k",logger=None)
    print(f"✅ {final}  ({os.path.getsize(final)/1e6:.1f} MB)  {total_mins:.1f} min")
    upload(final,n,edu)

if __name__=="__main__":
    asyncio.run(run())
