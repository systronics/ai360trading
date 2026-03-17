"""
AI360Trading — Daily NIFTY Technical Analysis Video Generator
=============================================================
- Fetches REAL live market data (yfinance + NSE API)
- Computes all indicators locally (RSI, MACD, BB, EMA, ATR, Pivot)
- Passes real numbers to Groq — human-like commentary, zero invented data
- Professional broadcast-quality slides (no AI branding, no grid lines)
- Dual TTS voices for natural human feel
- Auto-uploads to YouTube with SEO-optimised title & description
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

# ══════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════
OUT  = "output"
W, H = 1920, 1080
os.makedirs(OUT, exist_ok=True)

NSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
}

FONT_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
]
FONT_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
]

def font(candidates, size):
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


# ══════════════════════════════════════════════════════════
# LIVE MARKET DATA
# ══════════════════════════════════════════════════════════

def nse_session():
    s = requests.Session()
    s.headers.update(NSE_HEADERS)
    try:
        s.get("https://www.nseindia.com", timeout=10)
        time.sleep(1)
    except Exception:
        pass
    return s

def compute_indicators(df: pd.DataFrame) -> dict:
    close = df["Close"]
    high  = df["High"]
    low   = df["Low"]
    vol   = df["Volume"]

    ema20  = close.ewm(span=20,  adjust=False).mean()
    ema50  = close.ewm(span=50,  adjust=False).mean()
    ema200 = close.ewm(span=200, adjust=False).mean()

    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rsi   = 100 - (100 / (1 + gain / loss.replace(0, 1e-9)))

    ema12  = close.ewm(span=12, adjust=False).mean()
    ema26  = close.ewm(span=26, adjust=False).mean()
    macd   = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist_m = macd - signal

    sma20  = close.rolling(20).mean()
    std20  = close.rolling(20).std()
    bb_up  = sma20 + 2 * std20
    bb_lo  = sma20 - 2 * std20

    tr     = pd.concat([high - low,
                        (high - close.shift()).abs(),
                        (low  - close.shift()).abs()], axis=1).max(axis=1)
    atr    = tr.rolling(14).mean()

    yh = float(high.iloc[-2]); yl = float(low.iloc[-2]); yc = float(close.iloc[-2])
    pivot = (yh + yl + yc) / 3
    r1 = 2 * pivot - yl;  s1 = 2 * pivot - yh
    r2 = pivot + (yh - yl); s2 = pivot - (yh - yl)
    r3 = yh + 2 * (pivot - yl); s3 = yl - 2 * (yh - pivot)

    last = float(close.iloc[-1]); prev = float(close.iloc[-2])
    chg  = last - prev

    return {
        "current":    round(last, 2),
        "prev_close": round(prev, 2),
        "change":     round(chg, 2),
        "change_pct": round((chg / prev) * 100, 2),
        "open":       round(float(df["Open"].iloc[-1]), 2),
        "high":       round(float(df["High"].iloc[-1]), 2),
        "low":        round(float(df["Low"].iloc[-1]), 2),
        "volume":     int(vol.iloc[-1]),
        "avg_volume": int(vol.rolling(20).mean().iloc[-1]),
        "ema20":      round(float(ema20.iloc[-1]),  2),
        "ema50":      round(float(ema50.iloc[-1]),  2),
        "ema200":     round(float(ema200.iloc[-1]), 2),
        "rsi":        round(float(rsi.iloc[-1]),    2),
        "macd":       round(float(macd.iloc[-1]),   4),
        "macd_signal":round(float(signal.iloc[-1]), 4),
        "macd_hist":  round(float(hist_m.iloc[-1]), 4),
        "bb_upper":   round(float(bb_up.iloc[-1]),  2),
        "bb_lower":   round(float(bb_lo.iloc[-1]),  2),
        "bb_mid":     round(float(sma20.iloc[-1]),  2),
        "atr":        round(float(atr.iloc[-1]),    2),
        "pivot": round(pivot,2),
        "r1": round(r1,2), "r2": round(r2,2), "r3": round(r3,2),
        "s1": round(s1,2), "s2": round(s2,2), "s3": round(s3,2),
    }

def fetch_option_chain(session, symbol="NIFTY") -> dict:
    try:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        r   = session.get(url, timeout=15)
        records = r.json()["records"]["data"]
        ce_oi = pe_oi = 0
        strikes = {}
        for rec in records:
            k  = rec.get("strikePrice", 0)
            co = rec.get("CE", {}).get("openInterest", 0)
            po = rec.get("PE", {}).get("openInterest", 0)
            ce_oi += co; pe_oi += po
            strikes[k] = {"ce": co, "pe": po}
        pcr = round(pe_oi / max(ce_oi, 1), 2)
        max_pain = min(
            strikes,
            key=lambda s: sum(
                max(0, s - k) * v["ce"] + max(0, k - s) * v["pe"]
                for k, v in strikes.items()
            ),
            default=0
        )
        max_ce = max(strikes, key=lambda x: strikes[x]["ce"], default=0)
        max_pe = max(strikes, key=lambda x: strikes[x]["pe"], default=0)
        return {"pcr": pcr, "max_pain": max_pain,
                "max_ce_strike": max_ce, "max_pe_strike": max_pe,
                "total_ce_oi": ce_oi, "total_pe_oi": pe_oi}
    except Exception as e:
        print(f"  ⚠ Option chain: {e}")
        return {"pcr": 1.0, "max_pain": 0, "max_ce_strike": 0,
                "max_pe_strike": 0, "total_ce_oi": 0, "total_pe_oi": 0}

def fetch_fii_dii(session) -> dict:
    try:
        r    = session.get("https://www.nseindia.com/api/fiidiiTradeReact", timeout=15)
        data = r.json()
        fii  = next((x for x in data if x.get("category") == "FII/FPI"), {})
        dii  = next((x for x in data if x.get("category") == "DII"), {})
        def v(d, k): return float(str(d.get(k, "0")).replace(",", ""))
        return {
            "fii_buy": v(fii,"buyValue"),  "fii_sell": v(fii,"sellValue"),
            "fii_net": v(fii,"netValue"),  "dii_buy":  v(dii,"buyValue"),
            "dii_sell":v(dii,"sellValue"), "dii_net":  v(dii,"netValue"),
        }
    except Exception as e:
        print(f"  ⚠ FII/DII: {e}")
        return {k: 0.0 for k in
                ["fii_buy","fii_sell","fii_net","dii_buy","dii_sell","dii_net"]}

def fetch_all() -> dict:
    print("📡 Fetching live market data...")
    session = nse_session()
    data    = {}

    for name, ticker, period in [
        ("nifty",     "^NSEI",    "250d"),
        ("banknifty", "^NSEBANK", "60d"),
    ]:
        try:
            df = yf.download(ticker, period=period, interval="1d",
                             progress=False, auto_adjust=True)
            data[name] = compute_indicators(df)
            print(f"  ✓ {name}: {data[name]['current']} "
                  f"({data[name]['change_pct']:+.2f}%)")
        except Exception as e:
            print(f"  ✗ {name}: {e}"); data[name] = {}

    data["global"] = {}
    for name, ticker in [("dow","^DJI"),("nasdaq","^IXIC"),
                          ("sp500","^GSPC"),("india_vix","^INDIAVIX")]:
        try:
            h = yf.download(ticker, period="5d", interval="1d",
                            progress=False, auto_adjust=True)
            if len(h) >= 2:
                last = float(h["Close"].iloc[-1])
                prev = float(h["Close"].iloc[-2])
                data["global"][name] = {
                    "last":    round(last, 2),
                    "chg_pct": round((last - prev) / prev * 100, 2),
                }
        except Exception:
            pass
    print(f"  ✓ Global: {list(data['global'].keys())}")

    data["options"] = fetch_option_chain(session)
    print(f"  ✓ PCR={data['options']['pcr']}, "
          f"MaxPain={data['options']['max_pain']}")

    data["fii_dii"] = fetch_fii_dii(session)
    print(f"  ✓ FII={data['fii_dii']['fii_net']} Cr, "
          f"DII={data['fii_dii']['dii_net']} Cr")
    return data


# ══════════════════════════════════════════════════════════
# GROQ PROMPT — REAL NUMBERS INJECTED
# ══════════════════════════════════════════════════════════

def build_prompt(md: dict) -> str:
    n   = md.get("nifty", {})
    bn  = md.get("banknifty", {})
    gl  = md.get("global", {})
    opt = md.get("options", {})
    fii = md.get("fii_dii", {})

    def gv(d, k): return d.get(k, "N/A")

    return f"""You are a senior SEBI-registered technical analyst at a top Indian brokerage.
Today is {datetime.now().strftime('%A, %d %B %Y')}.

=== LIVE MARKET DATA (use ONLY these numbers, never invent) ===

NIFTY 50:
Current={gv(n,'current')} | Change={gv(n,'change')} ({gv(n,'change_pct')}%)
Open={gv(n,'open')} High={gv(n,'high')} Low={gv(n,'low')}
EMA20={gv(n,'ema20')} EMA50={gv(n,'ema50')} EMA200={gv(n,'ema200')}
RSI={gv(n,'rsi')} ATR={gv(n,'atr')}
MACD={gv(n,'macd')} Signal={gv(n,'macd_signal')} Hist={gv(n,'macd_hist')}
BB_Upper={gv(n,'bb_upper')} BB_Mid={gv(n,'bb_mid')} BB_Lower={gv(n,'bb_lower')}
Pivot={gv(n,'pivot')} R1={gv(n,'r1')} R2={gv(n,'r2')} R3={gv(n,'r3')}
S1={gv(n,'s1')} S2={gv(n,'s2')} S3={gv(n,'s3')}
Volume={gv(n,'volume')} AvgVol20={gv(n,'avg_volume')}

BANK NIFTY:
Current={gv(bn,'current')} Change={gv(bn,'change_pct')}%
High={gv(bn,'high')} Low={gv(bn,'low')}
EMA20={gv(bn,'ema20')} EMA50={gv(bn,'ema50')} RSI={gv(bn,'rsi')}

OPTION CHAIN:
PCR={gv(opt,'pcr')} MaxPain={gv(opt,'max_pain')}
MaxCE_OI_Strike={gv(opt,'max_ce_strike')} (resistance)
MaxPE_OI_Strike={gv(opt,'max_pe_strike')} (support)

FII/DII:
FII Net=Rs {gv(fii,'fii_net')} Cr (Buy={gv(fii,'fii_buy')} Sell={gv(fii,'fii_sell')})
DII Net=Rs {gv(fii,'dii_net')} Cr (Buy={gv(fii,'dii_buy')} Sell={gv(fii,'dii_sell')})

GLOBAL:
Dow={gl.get('dow',{}).get('last','N/A')} ({gl.get('dow',{}).get('chg_pct','N/A')}%)
Nasdaq={gl.get('nasdaq',{}).get('last','N/A')} ({gl.get('nasdaq',{}).get('chg_pct','N/A')}%)
SP500={gl.get('sp500',{}).get('last','N/A')} ({gl.get('sp500',{}).get('chg_pct','N/A')}%)
IndiaVIX={gl.get('india_vix',{}).get('last','N/A')} ({gl.get('india_vix',{}).get('chg_pct','N/A')}%)

=== SCRIPT REQUIREMENTS ===
Write EXACTLY 18 slides using ONLY the real data above. Never invent numbers.
Each slide: "title" (max 5 words), "content" (exactly 6 sentences with specific
numbers from the data above), "sentiment" (bullish/bearish/neutral).
Tone: Confident, professional, like a CNBC-TV18 senior analyst. No vague sentences.
Every sentence must mention at least one specific number.

SLIDE ORDER:
1. Today Market Overview
2. Opening Gap & Price Action
3. Key Support Levels (use S1 S2 S3)
4. Key Resistance Levels (use R1 R2 R3)
5. EMA Trend (20 50 200)
6. RSI Momentum Analysis
7. MACD Signal
8. Bollinger Bands
9. Volume Analysis
10. India VIX & Fear
11. Bank Nifty Analysis
12. FII DII Activity
13. Global Market Cues
14. Option Chain PCR Analysis
15. Max Pain & Strategy
16. Intraday Setup (entry target SL using real levels)
17. Positional Swing Setup (real levels)
18. Final Outlook

Respond ONLY with: {{"slides": [...]}}"""


# ══════════════════════════════════════════════════════════
# SLIDE DESIGN — BROADCAST QUALITY
# ══════════════════════════════════════════════════════════

THEMES = {
    "bullish": {
        "bg_top":   (6, 16, 10),   "bg_bot":   (4, 32, 18),
        "accent":   (0, 210, 100), "accent2":  (0, 160, 75),
        "text":     (238, 255, 244),"subtext":  (150, 210, 175),
        "badge_bg": (0, 175, 85),  "badge_txt":(0, 28, 14),
        "badge_lbl":"  BULLISH",
    },
    "bearish": {
        "bg_top":   (22, 6, 6),    "bg_bot":   (42, 10, 10),
        "accent":   (255, 70, 50), "accent2":  (195, 45, 35),
        "text":     (255, 244, 240),"subtext":  (225, 165, 155),
        "badge_bg": (215, 45, 35), "badge_txt":(255, 238, 235),
        "badge_lbl":"  BEARISH",
    },
    "neutral": {
        "bg_top":   (6, 10, 28),   "bg_bot":   (10, 18, 52),
        "accent":   (75, 145, 255),"accent2":  (55, 115, 205),
        "text":     (238, 244, 255),"subtext":  (155, 180, 225),
        "badge_bg": (55, 115, 200),"badge_txt":(228, 238, 255),
        "badge_lbl":"  NEUTRAL",
    },
}

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def gradient_image(top, bot):
    img = Image.new("RGB", (W, H))
    px  = img.load()
    for y in range(H):
        c = lerp(top, bot, y / H)
        for x in range(W):
            px[x, y] = c
    return img

def draw_mini_candles(draw, th, x0=1020, y0=160, n=7, cw=32, gap=52, ch=200):
    """Decorative mini candlestick chart — right panel visual."""
    candles = [
        (0.25,0.75,0.30,0.68), (0.40,0.85,0.60,0.80),
        (0.55,0.90,0.50,0.72), (0.35,0.80,0.65,0.78),
        (0.50,0.92,0.48,0.85), (0.60,0.95,0.55,0.90),
        (0.58,0.98,0.60,0.95),
    ]
    for i, (lo, hi, o, c) in enumerate(candles[:n]):
        x    = x0 + i * gap
        bull = c >= o
        clr  = th["accent"] if bull else th["accent2"]
        # wick
        draw.line([(x+cw//2, int(y0+(1-hi)*ch)),
                   (x+cw//2, int(y0+(1-lo)*ch))], fill=clr, width=2)
        # body
        bt = int(y0 + (1-max(o,c))*ch)
        bb = int(y0 + (1-min(o,c))*ch)
        draw.rounded_rectangle([(x,bt),(x+cw, bt+max(bb-bt,5))],
                                radius=3, fill=clr)

def make_slide(slide: dict, idx: int, total: int, n: dict, path: str):
    snt = slide.get("sentiment","neutral").lower()
    if snt not in THEMES: snt = "neutral"
    th  = THEMES[snt]

    img  = gradient_image(th["bg_top"], th["bg_bot"])
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Left panel background ──────────────────────────
    draw.rectangle([(0,0),(870,H)], fill=(*th["bg_top"],130))

    # Top accent bar
    draw.rectangle([(0,0),(W,7)], fill=th["accent"])

    # Fonts
    f_tiny  = font(FONT_REG,  22)
    f_small = font(FONT_REG,  26)
    f_badge = font(FONT_BOLD, 23)
    f_title = font(FONT_BOLD, 58)
    f_body  = font(FONT_REG,  30)
    f_stat_l= font(FONT_REG,  21)
    f_stat_v= font(FONT_BOLD, 23)
    f_price = font(FONT_BOLD, 66)
    f_chg   = font(FONT_BOLD, 34)
    f_disc  = font(FONT_REG,  19)

    # Header row
    draw.text((50, 24), datetime.now().strftime("%d %B %Y  |  %A"),
              fill=th["subtext"], font=f_small)

    # Slide counter — right of left panel
    draw.text((820, 24), f"{idx}/{total}",
              fill=th["subtext"], font=f_small, anchor="rm")

    # Sentiment badge
    bw = 155
    draw.rounded_rectangle([(680,14),(680+bw,50)],
                            radius=7, fill=th["badge_bg"])
    draw.text((680+bw//2, 32), th["badge_lbl"],
              fill=th["badge_txt"], font=f_badge, anchor="mm")

    # Title
    title_lines = textwrap.wrap(slide["title"].upper(), width=22)
    ty = 80
    for line in title_lines[:2]:
        draw.text((50, ty), line, fill=th["text"], font=f_title)
        ty += 72

    # Accent rule
    draw.rectangle([(50, ty+6),(470, ty+10)], fill=th["accent"])
    ty += 28

    # Body sentences
    sentences = [s.strip() for s in slide["content"].split(".") if s.strip()]
    for sent in sentences[:6]:
        for ln in textwrap.wrap(sent + ".", width=44):
            if ty > H - 110: break
            draw.text((50, ty), ln, fill=th["text"], font=f_body)
            ty += 47
        ty += 6

    # Disclaimer
    draw.text((50, H-32),
              "For educational purposes only. Not financial advice.",
              fill=(*th["subtext"][:3], 130), font=f_disc)

    # ── Separator ──────────────────────────────────────
    draw.rectangle([(872,0),(876,H)], fill=(*th["accent"][:3], 55))

    # ── Right panel ────────────────────────────────────
    draw_mini_candles(draw, th)

    # Price display
    price   = n.get("current","")
    chg     = n.get("change", 0)
    chg_pct = n.get("change_pct", 0)
    clr     = th["accent"] if float(chg) >= 0 else th["accent2"]
    sign    = "▲" if float(chg) >= 0 else "▼"

    draw.rounded_rectangle([(900,420),(1890,570)],
                            radius=14, fill=(0,0,0,90))
    draw.text((1395, 460), "NIFTY 50",
              fill=th["subtext"], font=f_small, anchor="mm")
    draw.text((1395, 520), f"{price:,}",
              fill=th["text"], font=f_price, anchor="mm")
    draw.text((1395, 600),
              f"{sign} {abs(float(chg)):,.2f}   ({float(chg_pct):+.2f}%)",
              fill=clr, font=f_chg, anchor="mm")

    # Stats grid
    stats = [
        ("Open",   n.get("open","")),   ("High",  n.get("high","")),
        ("Low",    n.get("low","")),    ("EMA 20",n.get("ema20","")),
        ("EMA 50", n.get("ema50","")),  ("EMA 200",n.get("ema200","")),
        ("RSI",    n.get("rsi","")),    ("ATR",   n.get("atr","")),
    ]
    sx, sy, col_w = 920, 660, 480
    for i, (lbl, val) in enumerate(stats):
        x = sx + (i % 2) * col_w
        y = sy + (i // 2) * 56
        draw.text((x,      y), str(lbl), fill=th["subtext"], font=f_stat_l)
        draw.text((x+160,  y), str(val), fill=th["text"],    font=f_stat_v)

    # S/R levels
    f_sr = font(FONT_BOLD, 21)
    f_sl = font(FONT_REG,  20)
    lx, ly = 1520, 650
    draw.text((lx, ly), "KEY LEVELS", fill=th["accent"], font=f_sr)
    ly += 32
    lvls = [
        ("R3", n.get("r3",""), th["accent"]),
        ("R2", n.get("r2",""), th["accent"]),
        ("R1", n.get("r1",""), th["accent"]),
        ("Pivot", n.get("pivot",""), th["subtext"]),
        ("S1", n.get("s1",""), th["accent2"]),
        ("S2", n.get("s2",""), th["accent2"]),
        ("S3", n.get("s3",""), th["accent2"]),
    ]
    for lbl, val, clr2 in lvls:
        draw.text((lx,     ly), lbl,     fill=th["subtext"], font=f_sl)
        draw.text((lx+80,  ly), str(val),fill=clr2,          font=f_sr)
        ly += 28

    img.save(path, quality=95)


def make_intro(n: dict, path: str):
    img  = gradient_image((4, 7, 22), (7, 14, 46))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0,0),(W,7)], fill=(0, 200, 110))

    f_logo  = font(FONT_BOLD, 100)
    f_sub   = font(FONT_BOLD,  46)
    f_date  = font(FONT_REG,   34)
    f_price = font(FONT_BOLD,  52)
    f_small = font(FONT_REG,   26)
    f_disc  = font(FONT_REG,   20)

    draw.text((W//2, 185), "AI360Trading",
              fill=(0, 218, 118), font=f_logo, anchor="mm")
    draw.rectangle([(W//2-350, 248),(W//2+350, 255)], fill=(0, 200, 110))
    draw.text((W//2, 318), "Daily NIFTY 50 Technical Analysis",
              fill=(215, 230, 255), font=f_sub, anchor="mm")
    draw.text((W//2, 395), datetime.now().strftime("%A, %d %B %Y"),
              fill=(135, 175, 238), font=f_date, anchor="mm")

    price   = n.get("current","")
    chg     = n.get("change", 0)
    chg_pct = n.get("change_pct", 0)
    clr     = (0, 218, 118) if float(chg) >= 0 else (255, 75, 55)
    sign    = "▲" if float(chg) >= 0 else "▼"

    draw.rounded_rectangle([(W//2-330,455),(W//2+330,580)],
                            radius=18, fill=(0,0,0,110))
    draw.text((W//2, 496), "NIFTY 50",
              fill=(135,175,238), font=f_small, anchor="mm")
    draw.text((W//2, 545),
              f"{price:,}   {sign} {abs(float(chg)):,.2f}  ({float(chg_pct):+.2f}%)",
              fill=clr, font=f_price, anchor="mm")

    draw.text((W//2, 660),
              "Support & Resistance  •  RSI  •  MACD  •  FII/DII  •  Option Chain  •  Trade Setups",
              fill=(95, 140, 200), font=f_small, anchor="mm")
    draw.text((W//2, H-46),
              "For educational purposes only. Not financial advice. Consult your registered advisor.",
              fill=(70, 95, 135), font=f_disc, anchor="mm")

    img.save(path, quality=95)


def make_outro(path: str):
    img  = gradient_image((4, 7, 22), (7, 14, 46))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0,0),(W,7)], fill=(0, 200, 110))

    f_logo  = font(FONT_BOLD, 90)
    f_mid   = font(FONT_BOLD, 44)
    f_small = font(FONT_REG,  28)
    f_tag   = font(FONT_REG,  24)
    f_disc  = font(FONT_REG,  20)

    draw.text((W//2, 200), "AI360Trading",
              fill=(0, 218, 118), font=f_logo, anchor="mm")
    draw.rectangle([(W//2-350,262),(W//2+350,268)], fill=(0,200,110))
    draw.text((W//2, 360), "LIKE   •   SUBSCRIBE   •   SHARE",
              fill=(215, 230, 255), font=f_mid, anchor="mm")
    draw.text((W//2, 458),
              "New analysis every morning before market opens  —  never miss a session",
              fill=(135, 175, 238), font=f_small, anchor="mm")
    draw.text((W//2, 545),
              "What is your view on tomorrow's market? Comment below!",
              fill=(100, 155, 210), font=f_small, anchor="mm")
    draw.text((W//2, 650),
              "#Nifty  #Nifty50  #TechnicalAnalysis  #StockMarket  #Intraday  #BankNifty",
              fill=(65, 108, 165), font=f_tag, anchor="mm")
    draw.text((W//2, H-46),
              "Disclaimer: Educational only. Not financial advice. Please consult a SEBI-registered advisor.",
              fill=(55, 78, 118), font=f_disc, anchor="mm")

    img.save(path, quality=95)


# ══════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ══════════════════════════════════════════════════════════
def upload(video_path: str, n: dict):
    if not os.path.exists("token.json"):
        print("❌ token.json missing — skipping upload.")
        return
    price   = n.get("current","")
    chg_pct = n.get("change_pct", 0)
    sign    = "UP" if float(chg_pct) >= 0 else "DOWN"

    title = (
        f"NIFTY Analysis {datetime.now().strftime('%d %b %Y')} | "
        f"{price} | {sign} {abs(float(chg_pct))}% | "
        f"Support Resistance Trade Setup"
    )
    desc = f"""📊 NIFTY 50 Technical Analysis — {datetime.now().strftime('%d %B %Y')}
Nifty closed at {price} ({'+' if float(chg_pct)>=0 else ''}{chg_pct}%)

✅ Key Support & Resistance Levels (Pivot Points)
✅ EMA 20 / 50 / 200 Trend
✅ RSI & Momentum
✅ MACD Signal & Histogram
✅ Bollinger Bands
✅ Volume Analysis
✅ India VIX
✅ Bank Nifty Levels
✅ FII & DII Activity
✅ Global Cues — Dow, Nasdaq, S&P 500
✅ Option Chain — PCR & Max Pain
✅ Intraday Trade Setup with Entry, Target & Stop Loss
✅ Positional Swing Trade Setup

⚠️ Disclaimer: Educational only. Not financial advice.
Consult a SEBI-registered investment advisor before trading.

#Nifty #Nifty50 #TechnicalAnalysis #StockMarket #NSE #BankNifty
#Intraday #Positional #RSI #MACD #FIIDii #OptionChain #AI360Trading #Trading"""

    try:
        creds   = Credentials.from_authorized_user_file("token.json")
        youtube = build("youtube", "v3", credentials=creds)
        req = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title, "description": desc,
                    "tags": ["Nifty","Nifty50","Technical Analysis",
                             "Stock Market India","NSE","Bank Nifty",
                             "Trading","Intraday","RSI","MACD",
                             "Bollinger Bands","FII DII","Option Chain",
                             "PCR","Max Pain","AI360Trading"],
                    "categoryId": "27",
                    "defaultLanguage": "en",
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                },
            },
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True),
        )
        resp = req.execute()
        print(f"\n✅ LIVE: https://www.youtube.com/watch?v={resp['id']}\n")
    except Exception as e:
        print(f"❌ Upload failed: {e}"); raise


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
VOICES = ["en-IN-PrabhatNeural", "en-IN-NeerjaNeural"]

async def tts(text: str, voice: str, path: str):
    await edge_tts.Communicate(text, voice).save(path)

async def run():
    # 1. Live data
    md = fetch_all()
    n  = md.get("nifty", {})

    # 2. Script
    gkey = os.environ.get("GROQ_API_KEY")
    if not gkey: sys.exit("❌ GROQ_API_KEY not set.")
    client = Groq(api_key=gkey)

    print("\n🤖 Generating script with real market data...")
    try:
        resp   = client.chat.completions.create(
            messages=[{"role":"user","content": build_prompt(md)}],
            model="llama-3.3-70b-versatile",
            response_format={"type":"json_object"},
            temperature=0.55, max_tokens=6000,
        )
        slides = json.loads(resp.choices[0].message.content)["slides"]
        print(f"✅ {len(slides)} slides generated.")
    except Exception as e:
        sys.exit(f"❌ Groq: {e}")

    total = len(slides)
    clips = []

    # 3. Intro
    ipath, iapath = f"{OUT}/intro.png", f"{OUT}/intro.mp3"
    make_intro(n, ipath)
    itext = (
        f"Welcome to AI360Trading. Today is "
        f"{datetime.now().strftime('%A, %d %B %Y')}. "
        f"Nifty 50 is at {n.get('current','')} — "
        f"{'up' if float(n.get('change',0))>=0 else 'down'} "
        f"by {abs(float(n.get('change',0)))} points, "
        f"or {n.get('change_pct','')} percent from yesterday. "
        "Today's analysis covers support and resistance, RSI, MACD, "
        "Bollinger Bands, FII DII flows, option chain data, "
        "and complete intraday and positional trade setups. Let us begin."
    )
    await tts(itext, VOICES[0], iapath)
    ia = AudioFileClip(iapath)
    clips.append(ImageClip(ipath).set_duration(max(ia.duration+2, 16)).set_audio(ia))

    # 4. Slides
    print("\n🎬 Rendering slides...")
    for i, s in enumerate(slides):
        ip = f"{OUT}/s{i:02d}.png"; ap = f"{OUT}/s{i:02d}.mp3"
        make_slide(s, i+1, total, n, ip)
        await tts(f"{s['title']}. {s['content']}", VOICES[i%2], ap)
        audio = AudioFileClip(ap)
        dur   = max(audio.duration + 2, 35)
        clips.append(ImageClip(ip).set_duration(dur).set_audio(audio))
        print(f"  ✓ [{i+1:02d}/{total}] {s['title'][:38]:<38} {dur:.0f}s")

    # 5. Outro
    op, oap = f"{OUT}/outro.png", f"{OUT}/outro.mp3"
    make_outro(op)
    otext = (
        "That is our complete Nifty technical analysis for today. "
        "If this helped you, please like this video and subscribe for daily updates "
        "every morning before market opens. "
        "Write your market view in the comments — we read every single one. "
        "Trade safe, manage your risk, and we will see you tomorrow."
    )
    await tts(otext, VOICES[0], oap)
    oa = AudioFileClip(oap)
    clips.append(ImageClip(op).set_duration(max(oa.duration+3, 22)).set_audio(oa))

    # 6. Render
    final  = f"{OUT}/final_video.mp4"
    total_mins = sum(c.duration for c in clips) / 60
    print(f"\n🎥 Rendering {len(clips)} clips — {total_mins:.1f} minutes...")

    concatenate_videoclips(clips, method="compose").write_videofile(
        final, fps=24, codec="libx264",
        audio_codec="aac", bitrate="4000k", logger=None,
    )
    print(f"✅ Saved: {final}  ({os.path.getsize(final)/1e6:.1f} MB)")

    # 7. Upload
    upload(final, n)


if __name__ == "__main__":
    asyncio.run(run())
