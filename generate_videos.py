"""
AI360Trading — Global Daily Video Generator
============================================
Covers ALL markets, ALL audiences, ALL countries.
Part 1: Live Market Analysis — Nifty + S&P500 + Bitcoin + Gold
Part 2: Education — Universal topics that rank in US, UK, Brazil, India
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
    "Accept": "application/json", "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/", "Connection": "keep-alive",
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
    img = Image.new("RGB", (W, H)); px = img.load()
    for y in range(H):
        c = lerp(top, bot, y/H)
        for x in range(W): px[x, y] = c
    return img

# ══════════════════════════════════════════════════════════
# MARKET DATA — GLOBAL
# ══════════════════════════════════════════════════════════
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
        "current":round(last,2), "prev_close":round(prev,2),
        "change":round(chg,2), "change_pct":round(chg/prev*100,2),
        "open":round(float(df["Open"].iloc[-1]),2),
        "high":round(float(h.iloc[-1]),2), "low":round(float(l.iloc[-1]),2),
        "volume":int(v.iloc[-1]), "avg_volume":int(v.rolling(20).mean().iloc[-1]),
        "ema20":round(float(e20.iloc[-1]),2), "ema50":round(float(e50.iloc[-1]),2),
        "ema200":round(float(e200.iloc[-1]),2), "rsi":round(float(rsi.iloc[-1]),2),
        "macd":round(float(macd.iloc[-1]),4), "macd_signal":round(float(sig.iloc[-1]),4),
        "macd_hist":round(float((macd-sig).iloc[-1]),4),
        "bb_upper":round(float((s20+2*sd20).iloc[-1]),2),
        "bb_lower":round(float((s20-2*sd20).iloc[-1]),2),
        "bb_mid":round(float(s20.iloc[-1]),2),
        "atr":round(float(tr.rolling(14).mean().iloc[-1]),2),
        "pivot":round(piv,2),
        "r1":round(2*piv-yl,2),"r2":round(piv+(yh-yl),2),"r3":round(yh+2*(piv-yl),2),
        "s1":round(2*piv-yh,2),"s2":round(piv-(yh-yl),2),"s3":round(yl-2*(yh-piv),2),
    }

def quick_price(ticker):
    """Fetch just price and change for display tickers."""
    try:
        df = flatten(yf.download(ticker, period="5d", interval="1d",
                                  progress=False, auto_adjust=True))
        if len(df) >= 2:
            last = round(float(df["Close"].iloc[-1]), 2)
            prev = round(float(df["Close"].iloc[-2]), 2)
            return {"last": last, "chg_pct": round((last-prev)/prev*100, 2)}
    except Exception:
        pass
    return {"last": "N/A", "chg_pct": "N/A"}

def nse_session():
    s = requests.Session(); s.headers.update(NSE_HEADERS)
    try: s.get("https://www.nseindia.com", timeout=10); time.sleep(1)
    except: pass
    return s

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
        return {"pcr":pcr, "max_pain":mp,
                "max_ce":max(sk,key=lambda x:sk[x]["ce"],default=0),
                "max_pe":max(sk,key=lambda x:sk[x]["pe"],default=0)}
    except Exception as e:
        print(f"  ⚠ Options:{e}")
        return {"pcr":1.0,"max_pain":0,"max_ce":0,"max_pe":0}

def fetch_fii(ses):
    try:
        r = ses.get("https://www.nseindia.com/api/fiidiiTradeReact", timeout=15)
        data = r.json()
        fii = next((x for x in data if x.get("category")=="FII/FPI"), {})
        dii = next((x for x in data if x.get("category")=="DII"), {})
        def v(d,k): return float(str(d.get(k,"0")).replace(",",""))
        return {"fii_net":v(fii,"netValue"),"fii_buy":v(fii,"buyValue"),"fii_sell":v(fii,"sellValue"),
                "dii_net":v(dii,"netValue"),"dii_buy":v(dii,"buyValue"),"dii_sell":v(dii,"sellValue")}
    except Exception as e:
        print(f"  ⚠ FII:{e}")
        return {k:0.0 for k in ["fii_net","fii_buy","fii_sell","dii_net","dii_buy","dii_sell"]}

def fetch_all():
    print("📡 Fetching global market data...")
    ses = nse_session(); md = {}

    # Indian indices — full indicators
    for nm, tk, pd_ in [("nifty","^NSEI","250d"), ("banknifty","^NSEBANK","60d")]:
        try:
            df = flatten(yf.download(tk, period=pd_, interval="1d",
                                      progress=False, auto_adjust=True))
            md[nm] = compute_indicators(df)
            print(f"  ✓ {nm}: {md[nm]['current']} ({md[nm]['change_pct']:+.2f}%)")
        except Exception as e:
            print(f"  ✗ {nm}: {e}"); md[nm] = {}

    # Global markets — price + change
    global_tickers = {
        "sp500":    "^GSPC",
        "nasdaq":   "^IXIC",
        "dow":      "^DJI",
        "bitcoin":  "BTC-USD",
        "ethereum": "ETH-USD",
        "gold":     "GC=F",
        "oil":      "CL=F",
        "india_vix":"^INDIAVIX",
        "vix":      "^VIX",
        "ftse":     "^FTSE",
        "nikkei":   "^N225",
        "eurusd":   "EURUSD=X",
        "gbpusd":   "GBPUSD=X",
        "usdinr":   "INR=X",
    }
    md["global"] = {}
    for nm, tk in global_tickers.items():
        result = quick_price(tk)
        if result["last"] != "N/A":
            md["global"][nm] = result
            print(f"  ✓ {nm}: {result['last']} ({result['chg_pct']:+.2f}%)")

    md["options"] = fetch_options(ses)
    md["fii_dii"] = fetch_fii(ses)
    print(f"  ✓ PCR={md['options']['pcr']} | FII={md['fii_dii']['fii_net']}Cr")
    return md

# ══════════════════════════════════════════════════════════
# PROMPTS
# ══════════════════════════════════════════════════════════
def analysis_prompt(md):
    n=md.get("nifty",{}); bn=md.get("banknifty",{}); gl=md.get("global",{})
    opt=md.get("options",{}); fii=md.get("fii_dii",{})
    def g(d,k): return d.get(k,"N/A")
    def gl_val(k): return gl.get(k,{}).get("last","N/A")
    def gl_chg(k): return gl.get(k,{}).get("chg_pct","N/A")

    return f"""You are a senior global markets analyst covering Indian and international markets.
Today is {datetime.now().strftime('%A, %d %B %Y')}.

LIVE MARKET DATA — use only these real numbers, never invent any:

NIFTY 50: {g(n,'current')} | Change: {g(n,'change')} ({g(n,'change_pct')}%)
Open:{g(n,'open')} High:{g(n,'high')} Low:{g(n,'low')}
EMA20:{g(n,'ema20')} EMA50:{g(n,'ema50')} EMA200:{g(n,'ema200')}
RSI:{g(n,'rsi')} | MACD:{g(n,'macd')} Signal:{g(n,'macd_signal')}
BB Upper:{g(n,'bb_upper')} Mid:{g(n,'bb_mid')} Lower:{g(n,'bb_lower')} ATR:{g(n,'atr')}
Pivot:{g(n,'pivot')} R1:{g(n,'r1')} R2:{g(n,'r2')} R3:{g(n,'r3')}
S1:{g(n,'s1')} S2:{g(n,'s2')} S3:{g(n,'s3')}

BANK NIFTY: {g(bn,'current')} ({g(bn,'change_pct')}%) RSI:{g(bn,'rsi')} EMA20:{g(bn,'ema20')}

GLOBAL MARKETS:
S&P 500: {gl_val('sp500')} ({gl_chg('sp500')}%)
Nasdaq: {gl_val('nasdaq')} ({gl_chg('nasdaq')}%)
Dow Jones: {gl_val('dow')} ({gl_chg('dow')}%)
Bitcoin: {gl_val('bitcoin')} ({gl_chg('bitcoin')}%)
Ethereum: {gl_val('ethereum')} ({gl_chg('ethereum')}%)
Gold: {gl_val('gold')} ({gl_chg('gold')}%)
Crude Oil: {gl_val('oil')} ({gl_chg('oil')}%)
India VIX: {gl_val('india_vix')} | US VIX: {gl_val('vix')}
FTSE 100: {gl_val('ftse')} ({gl_chg('ftse')}%)
USD/INR: {gl_val('usdinr')} | EUR/USD: {gl_val('eurusd')}

OPTION CHAIN:
PCR:{g(opt,'pcr')} MaxPain:{g(opt,'max_pain')}
Max CE OI Strike (Resistance):{g(opt,'max_ce')}
Max PE OI Strike (Support):{g(opt,'max_pe')}

FII/DII: FII Net Rs{g(fii,'fii_net')}Cr | DII Net Rs{g(fii,'dii_net')}Cr

Write EXACTLY 22 slides in json format. Each slide needs:
"title" (max 6 words, engaging — written for global YouTube audience),
"content" (6 sentences, every sentence contains a specific number from data above),
"sentiment" (bullish/bearish/neutral)

SLIDE TOPICS IN ORDER:
1. Global Markets Overview Today
2. US Markets S&P500 Nasdaq Impact on India
3. Bitcoin and Crypto Market Update
4. Gold and Oil — Commodity Signals
5. Nifty 50 Opening Analysis
6. Key Support Levels Nifty (use S1 S2 S3)
7. Key Resistance Levels Nifty (use R1 R2 R3)
8. EMA 20 50 200 Trend Analysis
9. RSI Momentum Reading
10. MACD Signal Analysis
11. Bollinger Bands Squeeze or Expansion
12. Volume Analysis
13. India VIX Fear Index
14. Bank Nifty Analysis
15. FII DII Smart Money Flow
16. Option Chain PCR Analysis
17. Max Pain and Options Strategy
18. Sector in Focus Today
19. Intraday Trade Setup (specific entry, target, stop-loss using real Nifty levels)
20. Positional Swing Setup (specific entry, target, stop-loss)
21. Option Trade of the Day (specific strike, expiry, entry price)
22. Market Outlook Summary

Tone: Professional global analyst. Confident. Every sentence has a specific number.
This video is watched by traders in India, USA, UK, and Brazil — write accordingly.
Respond in json format only: {{"slides":[...]}}"""


def education_prompt(topic):
    slides_info = "\n".join([
        f"Slide {i+1}: {s['heading']} — Key points: {'; '.join(s['points'])}"
        for i, s in enumerate(topic['slides'])
    ])
    return f"""You are a world-class financial educator. Your videos are watched in India, USA, UK, and Brazil.
Your style: clear, engaging, uses real examples from global markets.

TODAY'S TOPIC: {topic['title']}
CATEGORY: {topic['category']}
LEVEL: {topic['level']}
TARGET AUDIENCE: {topic.get('target_audience', 'Global')}

SLIDES TO WRITE:
{slides_info}

For each slide write:
- "title": exact heading shown above
- "content": 6 sentences that:
  * Explain the concept so simply a 16-year-old understands it
  * Use real examples: Apple, Tesla, Bitcoin, Reliance, TCS, S&P 500, Nifty, Gold
  * Include actual numbers to make examples concrete
  * Connect to how this works in MULTIPLE countries (India + USA + UK or Brazil)
  * End with one clear actionable takeaway the viewer can use TODAY
- "sentiment": "neutral"

Total: {len(topic['slides'])} slides.
Respond in json format only: {{"slides":[...]}}"""


# ══════════════════════════════════════════════════════════
# SLIDE THEMES
# ══════════════════════════════════════════════════════════
AT = {
    "bullish": {
        "bg_top":(6,16,10),"bg_bot":(4,32,18),
        "accent":(0,210,100),"accent2":(0,160,75),
        "text":(238,255,244),"subtext":(150,210,175),
        "badge_bg":(0,175,85),"badge_txt":(0,28,14),"badge":"▲ BULLISH"},
    "bearish": {
        "bg_top":(22,6,6),"bg_bot":(42,10,10),
        "accent":(255,70,50),"accent2":(195,45,35),
        "text":(255,244,240),"subtext":(225,165,155),
        "badge_bg":(215,45,35),"badge_txt":(255,238,235),"badge":"▼ BEARISH"},
    "neutral": {
        "bg_top":(6,10,28),"bg_bot":(10,18,52),
        "accent":(75,145,255),"accent2":(55,115,205),
        "text":(238,244,255),"subtext":(155,180,225),
        "badge_bg":(55,115,200),"badge_txt":(228,238,255),"badge":"◆ NEUTRAL"},
}
ET = {
    "Options":             {"bg_top":(20,5,35),"bg_bot":(35,10,60),"accent":(180,100,255),"text":(248,240,255),"subtext":(195,165,235)},
    "Technical Analysis":  {"bg_top":(5,20,35),"bg_bot":(8,35,65),"accent":(0,180,255),"text":(235,248,255),"subtext":(155,195,230)},
    "Fundamental Analysis":{"bg_top":(5,30,15),"bg_bot":(8,55,25),"accent":(0,220,130),"text":(235,255,245),"subtext":(150,215,180)},
    "Trading Strategy":    {"bg_top":(30,20,5),"bg_bot":(55,35,8),"accent":(255,170,0),"text":(255,250,235),"subtext":(230,200,150)},
    "Psychology":          {"bg_top":(30,5,20),"bg_bot":(55,8,35),"accent":(255,80,150),"text":(255,238,248),"subtext":(230,165,200)},
    "Risk Management":     {"bg_top":(35,10,5),"bg_bot":(60,20,8),"accent":(255,120,50),"text":(255,245,238),"subtext":(230,185,160)},
    "Global Macro":        {"bg_top":(5,25,40),"bg_bot":(8,45,70),"accent":(0,200,255),"text":(230,248,255),"subtext":(145,200,235)},
    "Crypto":              {"bg_top":(25,10,5),"bg_bot":(50,20,8),"accent":(255,150,0),"text":(255,248,235),"subtext":(230,195,145)},
    "Commodities":         {"bg_top":(25,20,5),"bg_bot":(50,40,8),"accent":(220,190,0),"text":(255,252,230),"subtext":(225,205,140)},
    "Personal Finance":    {"bg_top":(5,30,25),"bg_bot":(8,55,45),"accent":(0,230,180),"text":(235,255,250),"subtext":(150,215,200)},
    "Sector Analysis":     {"bg_top":(5,25,30),"bg_bot":(8,45,55),"accent":(0,210,200),"text":(235,255,254),"subtext":(150,210,205)},
    "News & Events":       {"bg_top":(25,25,5),"bg_bot":(45,45,8),"accent":(220,220,0),"text":(255,255,235),"subtext":(215,215,150)},
    "IPO & New Listings":  {"bg_top":(20,5,30),"bg_bot":(38,8,55),"accent":(200,120,255),"text":(248,235,255),"subtext":(195,160,235)},
    "Trading Plan":        {"bg_top":(5,25,30),"bg_bot":(8,45,55),"accent":(80,200,255),"text":(235,250,255),"subtext":(155,200,230)},
}
DEFAULT_EDU_THEME = {"bg_top":(5,20,35),"bg_bot":(8,35,65),"accent":(0,180,255),"text":(235,248,255),"subtext":(155,195,230)}

def mini_candles(draw, th, x0=1025, y0=160, cw=30, gap=50, ch=185):
    data=[(0.2,0.7,0.25,0.65),(0.4,0.85,0.6,0.78),(0.5,0.9,0.45,0.7),
          (0.3,0.78,0.6,0.75),(0.55,0.92,0.5,0.88),(0.6,0.95,0.55,0.9),(0.58,0.98,0.62,0.96)]
    for i,(lo,hi,o,c) in enumerate(data):
        x=x0+i*gap; bull=c>=o; clr=th["accent"] if bull else th.get("accent2",th["accent"])
        draw.line([(x+cw//2,int(y0+(1-hi)*ch)),(x+cw//2,int(y0+(1-lo)*ch))],fill=clr,width=2)
        bt=int(y0+(1-max(o,c))*ch); bb=int(y0+(1-min(o,c))*ch)
        draw.rounded_rectangle([(x,bt),(x+cw,bt+max(bb-bt,5))],radius=3,fill=clr)

def global_ticker_bar(draw, md):
    """Scrolling global ticker across bottom of analysis slides."""
    gl = md.get("global", {})
    items = [
        ("S&P500", "sp500"), ("NASDAQ", "nasdaq"), ("BTC", "bitcoin"),
        ("GOLD", "gold"), ("OIL", "oil"), ("FTSE", "ftse"), ("VIX", "vix"),
    ]
    f = font(FONT_BOLD, 20)
    draw.rectangle([(0, H-52),(W, H-1)], fill=(0,0,0,200))
    x = 30
    for label, key in items:
        d = gl.get(key, {})
        last = d.get("last","N/A"); chg = d.get("chg_pct","N/A")
        if last == "N/A": continue
        clr = (0,220,110) if isinstance(chg,float) and chg>=0 else (255,80,60)
        sign = "▲" if isinstance(chg,float) and chg>=0 else "▼"
        text = f"{label}: {last}  {sign}{abs(float(chg)) if isinstance(chg,float) else chg}%"
        draw.text((x, H-32), text, fill=clr, font=f, anchor="lm")
        x += len(text)*11 + 30
        if x > W - 100: break

def make_analysis_slide(slide, idx, total, n, md, path):
    snt = slide.get("sentiment","neutral").lower()
    if snt not in AT: snt = "neutral"
    th = AT[snt]
    img = gbg(th["bg_top"], th["bg_bot"]); draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle([(0,0),(870,H)], fill=(*th["bg_top"],130))
    draw.rectangle([(0,0),(W,7)], fill=th["accent"])

    fS=font(FONT_REG,24); fB=font(FONT_BOLD,22)
    fT=font(FONT_BOLD,54); fBd=font(FONT_REG,28)
    fSL=font(FONT_REG,19); fSV=font(FONT_BOLD,21)
    fP=font(FONT_BOLD,62); fC=font(FONT_BOLD,30); fD=font(FONT_REG,17)

    draw.text((50,24), datetime.now().strftime("%d %B %Y  |  %A"), fill=th["subtext"], font=fS)
    draw.text((820,24), f"ANALYSIS {idx}/{total}", fill=th["subtext"], font=fS, anchor="rm")
    bw=155; draw.rounded_rectangle([(680,14),(680+bw,50)], radius=7, fill=th["badge_bg"])
    draw.text((680+bw//2,32), th["badge"], fill=th["badge_txt"], font=fB, anchor="mm")

    ty = 80
    for line in textwrap.wrap(slide["title"].upper(), width=22)[:2]:
        draw.text((50,ty), line, fill=th["text"], font=fT); ty += 68
    draw.rectangle([(50,ty+4),(460,ty+8)], fill=th["accent"]); ty += 26

    for sent in [s.strip() for s in slide["content"].split(".") if s.strip()][:6]:
        for ln in textwrap.wrap(sent+".", width=45):
            if ty > H-110: break
            draw.text((50,ty), ln, fill=th["text"], font=fBd); ty += 45
        ty += 4

    draw.text((50,H-62), "AI360Trading  •  Global Markets Analysis",
              fill=(*th["subtext"][:3],160), font=fD)
    draw.text((50,H-38), "Educational only. Not financial advice.",
              fill=(*th["subtext"][:3],110), font=fD)

    draw.rectangle([(872,0),(876,H)], fill=(*th["accent"][:3],50))
    mini_candles(draw, th)

    price=n.get("current",""); chg=n.get("change",0); chg_pct=n.get("change_pct",0)
    clr=th["accent"] if float(chg)>=0 else th.get("accent2",th["accent"])
    sign="▲" if float(chg)>=0 else "▼"
    draw.rounded_rectangle([(900,415),(1890,560)], radius=14, fill=(0,0,0,90))
    draw.text((1395,450), "NIFTY 50", fill=th["subtext"], font=fS, anchor="mm")
    draw.text((1395,508), f"{price:,}", fill=th["text"], font=fP, anchor="mm")
    draw.text((1395,582), f"{sign} {abs(float(chg)):,.2f}  ({float(chg_pct):+.2f}%)", fill=clr, font=fC, anchor="mm")

    # Stats
    stats = [("Open",n.get("open","")),("High",n.get("high","")),("Low",n.get("low","")),
             ("EMA20",n.get("ema20","")),("EMA50",n.get("ema50","")),("EMA200",n.get("ema200","")),
             ("RSI",n.get("rsi","")),("ATR",n.get("atr",""))]
    for i,(lbl,val) in enumerate(stats):
        x=920+(i%2)*480; y=625+(i//2)*52
        draw.text((x,y), str(lbl), fill=th["subtext"], font=fSL)
        draw.text((x+148,y), str(val), fill=th["text"], font=fSV)

    # Key levels
    lx,ly=1520,625; fSR=font(FONT_BOLD,20); fSL2=font(FONT_REG,18)
    draw.text((lx,ly), "KEY LEVELS", fill=th["accent"], font=fSR); ly+=30
    for lbl,val,c2 in [
        ("R3",n.get("r3",""),th["accent"]),("R2",n.get("r2",""),th["accent"]),
        ("R1",n.get("r1",""),th["accent"]),("Pivot",n.get("pivot",""),th["subtext"]),
        ("S1",n.get("s1",""),th.get("accent2",th["accent"])),
        ("S2",n.get("s2",""),th.get("accent2",th["accent"])),
        ("S3",n.get("s3",""),th.get("accent2",th["accent"]))]:
        draw.text((lx,ly), lbl, fill=th["subtext"], font=fSL2)
        draw.text((lx+78,ly), str(val), fill=c2, font=fSR); ly+=26

    global_ticker_bar(draw, md)
    img.save(path, quality=95)


def make_edu_slide(slide, idx, total, topic_title, category, level, path):
    th = ET.get(category, DEFAULT_EDU_THEME)
    img = gbg(th["bg_top"], th["bg_bot"]); draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0,0),(920,H)], fill=(*th["bg_top"],140))
    draw.rectangle([(0,0),(W,7)], fill=th["accent"])

    fCat=font(FONT_BOLD,20); fS=font(FONT_REG,24); fBdg=font(FONT_BOLD,20)
    fT=font(FONT_BOLD,50); fBd=font(FONT_REG,29); fD=font(FONT_REG,17); fPt=font(FONT_REG,24)

    lc={"Beginner":(0,200,100),"Intermediate":(255,170,0),
        "Advanced":(255,70,70),"All Levels":(80,180,255)}.get(level,(100,180,255))

    draw.text((50,24), f"EDUCATION  •  {category.upper()}", fill=th["subtext"], font=fCat)
    draw.rounded_rectangle([(680,14),(860,50)], radius=7, fill=lc)
    draw.text((770,32), level.upper(), fill=(10,10,10), font=fBdg, anchor="mm")
    draw.text((50,56), topic_title, fill=(*th["subtext"][:3],180), font=font(FONT_REG,20))

    heading = slide.get("title", slide.get("heading",""))
    ty = 88
    for line in textwrap.wrap(heading.upper(), width=24)[:2]:
        draw.text((50,ty), line, fill=th["text"], font=fT); ty += 64
    draw.rectangle([(50,ty+4),(500,ty+8)], fill=th["accent"]); ty += 24

    for sent in [s.strip() for s in slide["content"].split(".") if s.strip()][:6]:
        for ln in textwrap.wrap(sent+".", width=47):
            if ty > H-110: break
            draw.text((50,ty), ln, fill=th["text"], font=fBd); ty += 45
        ty += 4

    draw.text((50,H-62), "AI360Trading  •  Global Financial Education",
              fill=(*th["subtext"][:3],160), font=fD)
    draw.text((50,H-38), "Educational only. Not financial advice.",
              fill=(*th["subtext"][:3],110), font=fD)

    draw.rectangle([(922,0),(926,H)], fill=(*th["accent"][:3],50))

    # Right panel
    draw.text((1450,145), f"{idx}", fill=(*th["accent"][:3],28),
              font=font(FONT_BOLD,220), anchor="mm")
    draw.rounded_rectangle([(960,375),(1900,795)], radius=20, fill=(0,0,0,100))
    draw.text((1430,415), "KEY TAKEAWAYS", fill=th["accent"],
              font=font(FONT_BOLD,24), anchor="mm")
    nums = "①②③④⑤"
    pts = [s.strip() for s in slide["content"].split(".") if s.strip()][:4]
    pt_y = 458
    for i, pt in enumerate(pts):
        short = (pt[:62]+"…") if len(pt)>62 else pt
        draw.rounded_rectangle([(978,pt_y-6),(1882,pt_y+44)], radius=8,
                                fill=(*th["accent"][:3],20))
        draw.text((1000,pt_y+18), f"{nums[i]}  {short}",
                  fill=th["text"], font=fPt, anchor="lm")
        pt_y += 72

    prog = int(860*(idx/total))
    draw.rectangle([(960,835),(1820,852)], fill=(255,255,255,30))
    draw.rectangle([(960,835),(960+prog,852)], fill=th["accent"])
    draw.text((1390,872), f"Lesson {idx} of {total}",
              fill=th["subtext"], font=fS, anchor="mm")

    img.save(path, quality=95)


def make_divider(title, sub, accent, path):
    img = gbg((4,7,22),(7,14,46)); draw = ImageDraw.Draw(img)
    draw.rectangle([(0,0),(W,7)], fill=accent)
    draw.rectangle([(0,H-7),(W,H)], fill=accent)
    draw.text((W//2,H//2), title.upper(), fill=(*accent[:3],18),
              font=font(FONT_BOLD,160), anchor="mm")
    draw.rounded_rectangle([(W//2-480,H//2-98),(W//2+480,H//2+98)], radius=20, fill=(0,0,0,120))
    draw.text((W//2,H//2-28), title, fill=accent, font=font(FONT_BOLD,58), anchor="mm")
    draw.text((W//2,H//2+44), sub, fill=(200,220,255), font=font(FONT_REG,30), anchor="mm")
    img.save(path, quality=95)


def make_intro(n, md, edu, path):
    img = gbg((4,7,22),(7,14,46)); draw = ImageDraw.Draw(img)
    gl = md.get("global",{})
    draw.rectangle([(0,0),(W,7)], fill=(0,200,110))

    draw.text((W//2,148), "AI360Trading", fill=(0,218,118),
              font=font(FONT_BOLD,96), anchor="mm")
    draw.rectangle([(W//2-340,208),(W//2+340,215)], fill=(0,200,110))
    draw.text((W//2,278), "Global Markets Analysis + Education",
              fill=(215,230,255), font=font(FONT_BOLD,42), anchor="mm")
    draw.text((W//2,342), datetime.now().strftime("%A, %d %B %Y"),
              fill=(135,175,238), font=font(FONT_REG,34), anchor="mm")

    # Nifty price
    price=n.get("current",""); chg=n.get("change",0); chg_pct=n.get("change_pct",0)
    clr=(0,218,118) if float(chg)>=0 else (255,75,55)
    sign="▲" if float(chg)>=0 else "▼"
    draw.rounded_rectangle([(W//2-400,395),(W//2+400,510)], radius=16, fill=(0,0,0,110))
    draw.text((W//2,430), "NIFTY 50", fill=(135,175,238), font=font(FONT_REG,26), anchor="mm")
    draw.text((W//2,482),
              f"{price:,}  {sign} {abs(float(chg)):,.2f}  ({float(chg_pct):+.2f}%)",
              fill=clr, font=font(FONT_BOLD,48), anchor="mm")

    # Global mini row
    gl_items=[("S&P 500","sp500"),("Bitcoin","bitcoin"),("Gold","gold"),("VIX","vix")]
    gx = 240
    for lbl,key in gl_items:
        d=gl.get(key,{}); last=d.get("last","N/A"); cp=d.get("chg_pct","N/A")
        if last=="N/A": gx+=360; continue
        gc=(0,210,100) if isinstance(cp,float) and cp>=0 else (255,75,55)
        gs="▲" if isinstance(cp,float) and cp>=0 else "▼"
        draw.text((gx,558), lbl, fill=(135,175,238), font=font(FONT_REG,20), anchor="mm")
        draw.text((gx,590), f"{last}", fill=(220,235,255), font=font(FONT_BOLD,26), anchor="mm")
        draw.text((gx,618), f"{gs}{abs(float(cp)) if isinstance(cp,float) else cp}%", fill=gc, font=font(FONT_REG,20), anchor="mm")
        gx += 360

    draw.text((W//2,668), f"Today's Education:  {edu['title']}",
              fill=(160,200,255), font=font(FONT_BOLD,24), anchor="mm")
    draw.text((W//2,708),
              f"{edu['category']}  •  {edu['level']}  •  {edu.get('target_audience','Global')}",
              fill=(110,150,210), font=font(FONT_REG,22), anchor="mm")
    draw.text((W//2,H-42),
              "For educational purposes only. Not financial advice. Consult a registered financial advisor.",
              fill=(65,90,130), font=font(FONT_REG,20), anchor="mm")
    img.save(path, quality=95)


def make_outro(edu, path):
    img = gbg((4,7,22),(7,14,46)); draw = ImageDraw.Draw(img)
    draw.rectangle([(0,0),(W,7)], fill=(0,200,110))
    draw.text((W//2,185), "AI360Trading", fill=(0,218,118),
              font=font(FONT_BOLD,88), anchor="mm")
    draw.rectangle([(W//2-340,248),(W//2+340,254)], fill=(0,200,110))
    draw.text((W//2,328), "LIKE  •  SUBSCRIBE  •  SHARE",
              fill=(215,230,255), font=font(FONT_BOLD,44), anchor="mm")
    draw.text((W//2,415),
              "Daily global markets analysis + education — every weekday morning",
              fill=(135,175,238), font=font(FONT_REG,28), anchor="mm")
    draw.text((W//2,488), "Drop your market view in the comments!",
              fill=(100,155,210), font=font(FONT_REG,28), anchor="mm")
    draw.text((W//2,570),
              "Viewers from India  🇮🇳   USA  🇺🇸   UK  🇬🇧   Brazil  🇧🇷   UAE  🇦🇪",
              fill=(80,130,190), font=font(FONT_REG,26), anchor="mm")
    draw.text((W//2,650),
              "#StockMarket #TechnicalAnalysis #Bitcoin #Nifty #SP500 #Trading #AI360Trading",
              fill=(60,105,165), font=font(FONT_REG,24), anchor="mm")
    draw.text((W//2,H-42),
              "Disclaimer: Educational only. Not financial advice. Consult a registered financial advisor.",
              fill=(55,78,118), font=font(FONT_REG,20), anchor="mm")
    img.save(path, quality=95)


# ══════════════════════════════════════════════════════════
# YOUTUBE UPLOAD — Global SEO
# ══════════════════════════════════════════════════════════
def upload(video_path, n, md, edu):
    if not os.path.exists("token.json"):
        print("❌ token.json missing."); return

    gl = md.get("global",{})
    price=n.get("current",""); chg_pct=n.get("change_pct",0)
    btc=gl.get("bitcoin",{}).get("last","N/A")
    sp=gl.get("sp500",{}).get("last","N/A")
    sign="UP" if float(chg_pct)>=0 else "DOWN"

    # SEO-optimised title for global search
    title = (
        f"Stock Market Analysis {datetime.now().strftime('%d %b %Y')} | "
        f"Nifty {price} {sign} | S&P500 {sp} | BTC {btc} | {edu['title'][:35]}"
    )

    description = f"""📊 Global Stock Market Analysis — {datetime.now().strftime('%d %B %Y')}

🌍 Covering: Indian Markets (Nifty, Bank Nifty) + US Markets (S&P 500, Nasdaq) + Bitcoin + Gold + Forex

🔴 TODAY'S MARKET ANALYSIS:
• Nifty 50: {price} ({'+' if float(chg_pct)>=0 else ''}{chg_pct}%)
• S&P 500: {sp} | Bitcoin: {btc} | Gold: {gl.get('gold',{}).get('last','N/A')}
• Support & Resistance Levels • EMA 20/50/200 • RSI • MACD
• Bollinger Bands • Volume • India VIX • US VIX
• Bank Nifty • FII/DII Activity
• Option Chain PCR & Max Pain
• Intraday Trade Setup (Entry, Target, Stop-Loss)
• Positional Swing Setup
• Option Trade of the Day

📚 TODAY'S EDUCATION: {edu['title']}
Level: {edu['level']} | Category: {edu['category']}
Who should watch: {edu.get('target_audience', 'All traders and investors worldwide')}

🌐 This channel covers global markets for viewers in India, USA, UK, Brazil, UAE, Singapore and worldwide.

⏰ New video every weekday morning — like and subscribe to never miss an analysis!

⚠️ DISCLAIMER: This video is for educational and informational purposes only.
It does not constitute financial advice or investment recommendations.
Please consult a SEBI-registered advisor (India) or regulated financial advisor in your country before making any investment decisions.

#StockMarket #TechnicalAnalysis #Nifty #SP500 #Bitcoin #Trading #Investing
#OptionsTrading #SwingTrading #IntradayTrading #StockMarketToday
#NiftyAnalysis #MarketAnalysis #AI360Trading #FinancialEducation
#{edu['category'].replace(' ','')} #GlobalMarkets #Nasdaq #BankNifty #Gold"""

    tags = [
        "stock market analysis", "technical analysis", "Nifty analysis",
        "S&P 500 analysis", "Bitcoin analysis", "options trading",
        "intraday trading", "swing trading", "stock market today",
        "Nifty 50", "Bank Nifty", "RSI", "MACD", "support resistance",
        "trading strategy", "market analysis today", "AI360Trading",
        edu['category'], edu['level'], "global markets",
        "stock market India", "US stock market", "crypto trading",
        "gold price", "forex trading", "financial education",
        "stock market for beginners", "how to trade stocks",
    ]

    try:
        creds = Credentials.from_authorized_user_file("token.json")
        youtube = build("youtube", "v3", credentials=creds)
        req = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": "27",
                    "defaultLanguage": "en",
                    "defaultAudioLanguage": "en",
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                },
            },
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True),
        )
        resp = req.execute()
        vid_id = resp["id"]
        print(f"\n✅ LIVE: https://www.youtube.com/watch?v={vid_id}")

        # Upload custom thumbnail
        thumb_path = f"{OUT}/thumbnail.png"
        if os.path.exists(thumb_path):
            youtube.thumbnails().set(
                videoId=vid_id,
                media_body=MediaFileUpload(thumb_path, mimetype="image/png")
            ).execute()
            print("✅ Thumbnail uploaded.")

    except Exception as e:
        print(f"❌ Upload failed: {e}"); raise


# ══════════════════════════════════════════════════════════
# CUSTOM THUMBNAIL — Click-worthy design
# ══════════════════════════════════════════════════════════
def make_thumbnail(n, md, edu, path):
    """YouTube thumbnail: 1280x720, bold, click-worthy."""
    TW, TH = 1280, 720
    gl = md.get("global",{})
    price = n.get("current","")
    chg_pct = n.get("change_pct", 0)
    is_bull = float(chg_pct) >= 0
    sign = "▲" if is_bull else "▼"
    bg_top = (6,16,10) if is_bull else (22,6,6)
    bg_bot = (4,32,18) if is_bull else (42,10,10)
    accent = (0,210,100) if is_bull else (255,70,50)

    img = Image.new("RGB",(TW,TH)); px = img.load()
    for y in range(TH):
        c = lerp(bg_top, bg_bot, y/TH)
        for x in range(TW): px[x,y] = c
    draw = ImageDraw.Draw(img, "RGBA")

    # Accent bar left side
    draw.rectangle([(0,0),(18,TH)], fill=accent)
    draw.rectangle([(0,0),(TW,14)], fill=accent)
    draw.rectangle([(0,TH-14),(TW,TH)], fill=accent)

    # Channel name
    draw.text((50,45), "AI360Trading", fill=(255,255,255),
              font=font(FONT_BOLD,52), anchor="lm")

    # Date
    draw.text((TW-40,45), datetime.now().strftime("%d %b %Y"),
              fill=(180,200,240), font=font(FONT_REG,32), anchor="rm")

    # Big price
    draw.text((50,200), "NIFTY", fill=(180,210,255), font=font(FONT_BOLD,60))
    draw.text((50,270), f"{price:,}", fill=(255,255,255), font=font(FONT_BOLD,120))
    draw.text((50,400), f"{sign} {abs(float(chg_pct))}%  TODAY",
              fill=accent, font=font(FONT_BOLD,58))

    # Education topic teaser
    draw.rounded_rectangle([(40,480),(900,580)], radius=12, fill=(*accent[:3],40))
    edu_short = edu['title'][:52]
    draw.text((60,530), f"📚  {edu_short}", fill=(220,240,255),
              font=font(FONT_BOLD,28), anchor="lm")

    # Global prices right side
    gl_items=[("S&P 500","sp500"),("BTC","bitcoin"),("GOLD","gold")]
    gy = 160
    for lbl,key in gl_items:
        d=gl.get(key,{}); last=d.get("last","N/A"); cp=d.get("chg_pct","N/A")
        if last=="N/A": gy+=140; continue
        gc=(0,210,100) if isinstance(cp,float) and cp>=0 else (255,75,55)
        gs="▲" if isinstance(cp,float) and cp>=0 else "▼"
        draw.text((980,gy), lbl, fill=(180,205,240), font=font(FONT_BOLD,32), anchor="lm")
        draw.text((980,gy+42), f"{last}", fill=(255,255,255), font=font(FONT_BOLD,44), anchor="lm")
        draw.text((980,gy+90), f"{gs} {abs(float(cp)) if isinstance(cp,float) else cp}%", fill=gc, font=font(FONT_BOLD,30), anchor="lm")
        gy += 155

    # Bottom tag
    draw.text((TW//2, TH-32), "LIKE  •  SUBSCRIBE  •  GLOBAL MARKETS DAILY",
              fill=(*accent[:3],200), font=font(FONT_BOLD,24), anchor="mm")

    img.save(path, quality=98)


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
VOICES = ["en-IN-PrabhatNeural", "en-IN-NeerjaNeural"]

async def tts(text, voice, path):
    await edge_tts.Communicate(text, voice).save(path)

async def run():
    # 1. Fetch global market data
    md = fetch_all(); n = md.get("nifty",{})
    gl = md.get("global",{})

    # 2. Today's education topic
    edu = get_todays_education_topic()
    print(f"\n📚 Education: {edu['title']} ({edu['category']}, {edu['level']})")
    print(f"   Audience: {edu.get('target_audience','Global')}")

    # 3. Generate scripts
    gkey = os.environ.get("GROQ_API_KEY")
    if not gkey: sys.exit("❌ GROQ_API_KEY not set.")
    client = Groq(api_key=gkey)

    print("\n🤖 Generating analysis script (global)...")
    ar = client.chat.completions.create(
        messages=[{"role":"user","content": analysis_prompt(md)}],
        model="llama-3.3-70b-versatile",
        response_format={"type":"json_object"},
        temperature=0.55, max_tokens=8000)
    as_slides = json.loads(ar.choices[0].message.content)["slides"]
    print(f"  ✓ {len(as_slides)} analysis slides")

    print("🤖 Generating education script...")
    er = client.chat.completions.create(
        messages=[{"role":"user","content": education_prompt(edu)}],
        model="llama-3.3-70b-versatile",
        response_format={"type":"json_object"},
        temperature=0.7, max_tokens=5000)
    ed_slides = json.loads(er.choices[0].message.content)["slides"]
    print(f"  ✓ {len(ed_slides)} education slides")

    clips = []

    # 4. Intro
    ipath, iapath = f"{OUT}/intro.png", f"{OUT}/intro.mp3"
    make_intro(n, md, edu, ipath)
    btc_price = gl.get("bitcoin",{}).get("last","N/A")
    sp_price  = gl.get("sp500",{}).get("last","N/A")
    it = (f"Welcome to AI360Trading — your daily global markets analysis. "
          f"Today is {datetime.now().strftime('%A, %d %B %Y')}. "
          f"Nifty 50 is at {n.get('current','')} — "
          f"{'up' if float(n.get('change',0))>=0 else 'down'} "
          f"{abs(float(n.get('change',0)))} points. "
          f"S and P 500 is at {sp_price}. Bitcoin is at {btc_price} dollars. "
          f"In today's video we cover complete live analysis of Indian and global markets "
          f"with intraday, positional and options trade setups, "
          f"plus our education segment on {edu['title']}. "
          f"This video is for traders and investors worldwide. Let us begin.")
    await tts(it, VOICES[0], iapath)
    ia = AudioFileClip(iapath)
    clips.append(ImageClip(ipath).set_duration(max(ia.duration+2,20)).set_audio(ia))

    # 5. Analysis divider
    adp, adap = f"{OUT}/div_a.png", f"{OUT}/div_a.mp3"
    make_divider("GLOBAL MARKET ANALYSIS",
                 f"Nifty {n.get('current','')}  •  S&P {sp_price}  •  BTC {btc_price}",
                 (0,210,100), adp)
    await tts("Part One. Global Market Analysis.",VOICES[0], adap)
    ada = AudioFileClip(adap)
    clips.append(ImageClip(adp).set_duration(max(ada.duration+1,5)).set_audio(ada))

    # 6. Analysis slides
    print("\n🎬 Analysis slides...")
    an = len(as_slides)
    for i, s in enumerate(as_slides):
        ip, ap = f"{OUT}/a{i:02d}.png", f"{OUT}/a{i:02d}.mp3"
        make_analysis_slide(s, i+1, an, n, md, ip)
        await tts(f"{s['title']}. {s['content']}", VOICES[i%2], ap)
        au = AudioFileClip(ap); dur = max(au.duration+2, 32)
        clips.append(ImageClip(ip).set_duration(dur).set_audio(au))
        print(f"  ✓ [A{i+1:02d}/{an}] {s['title'][:38]:<38} {dur:.0f}s")

    # 7. Education divider
    eth = ET.get(edu['category'], DEFAULT_EDU_THEME)
    edp, edap = f"{OUT}/div_e.png", f"{OUT}/div_e.mp3"
    make_divider("TODAY'S EDUCATION",
                 f"{edu['title']}  |  {edu['level']}",
                 eth["accent"], edp)
    await tts(f"Part Two. Education. Today's topic is {edu['title']}. "
              f"This applies to markets worldwide — India, USA, UK, Brazil and everywhere.",
              VOICES[0], edap)
    eda = AudioFileClip(edap)
    clips.append(ImageClip(edp).set_duration(max(eda.duration+1,7)).set_audio(eda))

    # 8. Education slides
    print("\n🎬 Education slides...")
    en = len(ed_slides)
    for i, s in enumerate(ed_slides):
        ip, ap = f"{OUT}/e{i:02d}.png", f"{OUT}/e{i:02d}.mp3"
        make_edu_slide(s, i+1, en, edu['title'], edu['category'], edu['level'], ip)
        await tts(f"{s.get('title', s.get('heading',''))}. {s['content']}", VOICES[i%2], ap)
        au = AudioFileClip(ap); dur = max(au.duration+2, 35)
        clips.append(ImageClip(ip).set_duration(dur).set_audio(au))
        print(f"  ✓ [E{i+1:02d}/{en}] {s.get('title','')[:38]:<38} {dur:.0f}s")

    # 9. Outro
    op, oap = f"{OUT}/outro.png", f"{OUT}/outro.mp3"
    make_outro(edu, op)
    ot = (f"That is our complete global markets analysis and education for today. "
          f"We covered Nifty, S and P 500, Bitcoin, Gold, and complete trade setups, "
          f"plus education on {edu['title']}. "
          "If you found this valuable, please like this video and subscribe. "
          "Share it with any trader or investor who will benefit from this. "
          "We publish every weekday morning before market opens. "
          "Comment your market view below — see you tomorrow. Trade safe.")
    await tts(ot, VOICES[0], oap)
    oa = AudioFileClip(oap)
    clips.append(ImageClip(op).set_duration(max(oa.duration+3,22)).set_audio(oa))

    # 10. Render
    final = f"{OUT}/final_video.mp4"
    total_mins = sum(c.duration for c in clips)/60
    print(f"\n🎥 Rendering {len(clips)} clips — {total_mins:.1f} minutes...")
    concatenate_videoclips(clips, method="compose").write_videofile(
        final, fps=24, codec="libx264",
        audio_codec="aac", bitrate="4000k", logger=None)
    print(f"✅ {final}  ({os.path.getsize(final)/1e6:.1f} MB)  {total_mins:.1f} min")

    # 11. Make thumbnail
    thumb_path = f"{OUT}/thumbnail.png"
    make_thumbnail(n, md, edu, thumb_path)
    print("✅ Thumbnail created.")

    # 12. Upload with full global SEO
    upload(final, n, md, edu)


if __name__ == "__main__":
    asyncio.run(run())
