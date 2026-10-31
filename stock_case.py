"""
stock_case.py v1.0 (2026-10-31) — Hindi "case study" Short: a PAST breakout of a large Indian stock and what happened next.

WHY
  Owner wants Hindi stock-pattern Shorts (the Page audience is 97.5% India) using words like breakout / support / volume /
  pattern, and they must follow SEBI guidance. A PAST, completed example with its honest outcome (worked / failed / sideways)
  is educational, not a recommendation: no live pick, no entry, no stop-loss, no target, no "buy now".

WHAT IT BUILDS
  * Picks a big stock from a fixed liquid list, finds its latest 50-day closing-high breakout whose WHOLE chart window is older than 3 months,
    classifies the outcome from the real daily closes, and rotates the outcomes (failed / worked / failed / worked / sideways)
    so the series stays honest (most breakouts do NOT work: our own backtest won fewer than half).
  * Animated real-data chart (story_short.make_clip_factory) + Hindi narration (hi-IN-MadhurNeural) + soft bed.
  * Description discloses: past example, not advice, synthetic AI voice, not SEBI registered.

SAFETY (never-break doctrine)
  * Fail-open: any failure = nothing published + Telegram note + exit 0.
  * No prices / levels on screen or in speech; only words (breakout, volume, support, pattern).
  * A symbol is not reused within 60 days (_data/case_history.json).

Usage:  python stock_case.py --run --mode dry|private-test|scheduled [--out output/case] [--symbol TCS]
"""
import os
import sys
import json
import hashlib
import argparse
import datetime as dt
from pathlib import Path

import numpy as np
from PIL import Image

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

import emotion_story as E

HIST = Path("_data/case_history.json")
COOLDOWN_DAYS = 60
AGE_DAYS = 92      # shown data must be at least ~3 months old (see find_event)
PATTERN = ["failed", "worked", "failed", "worked", "flat"]    # honest mix: breakouts fail often

# symbol -> (display name, sector for the screen, sector word in Hindi)
STOCKS = {
    "RELIANCE": ("RELIANCE", "Energy & Retail", "ऊर्जा और रिटेल"), "TCS": ("TCS", "IT", "आईटी"),
    "HDFCBANK": ("HDFC BANK", "Banking", "बैंकिंग"), "INFY": ("INFOSYS", "IT", "आईटी"),
    "ICICIBANK": ("ICICI BANK", "Banking", "बैंकिंग"), "SBIN": ("SBI", "Banking", "बैंकिंग"),
    "BHARTIARTL": ("BHARTI AIRTEL", "Telecom", "टेलीकॉम"), "ITC": ("ITC", "FMCG", "एफएमसीजी"),
    "LT": ("L&T", "Infrastructure", "इन्फ्रास्ट्रक्चर"), "HINDUNILVR": ("HUL", "FMCG", "एफएमसीजी"),
    "KOTAKBANK": ("KOTAK BANK", "Banking", "बैंकिंग"), "AXISBANK": ("AXIS BANK", "Banking", "बैंकिंग"),
    "BAJFINANCE": ("BAJAJ FINANCE", "Finance", "फाइनेंस"), "MARUTI": ("MARUTI", "Auto", "ऑटो"),
    "SUNPHARMA": ("SUN PHARMA", "Pharma", "फार्मा"), "TITAN": ("TITAN", "Consumer", "कंज्यूमर"),
    "ULTRACEMCO": ("ULTRATECH", "Cement", "सीमेंट"), "ASIANPAINT": ("ASIAN PAINTS", "Paints", "पेंट"),
    "NESTLEIND": ("NESTLE", "FMCG", "एफएमसीजी"), "WIPRO": ("WIPRO", "IT", "आईटी"),
    "HCLTECH": ("HCL TECH", "IT", "आईटी"), "TECHM": ("TECH MAHINDRA", "IT", "आईटी"),
    "M&M": ("M&M", "Auto", "ऑटो"), "TATASTEEL": ("TATA STEEL", "Metals", "मेटल"),
    "NTPC": ("NTPC", "Power", "पावर"), "POWERGRID": ("POWER GRID", "Power", "पावर"),
    "ONGC": ("ONGC", "Oil & Gas", "तेल और गैस"), "COALINDIA": ("COAL INDIA", "Mining", "माइनिंग"),
    "DRREDDY": ("DR REDDYS", "Pharma", "फार्मा"), "CIPLA": ("CIPLA", "Pharma", "फार्मा"),
    "EICHERMOT": ("EICHER MOTORS", "Auto", "ऑटो"), "HEROMOTOCO": ("HERO MOTOCORP", "Auto", "ऑटो"),
    "BAJAJ-AUTO": ("BAJAJ AUTO", "Auto", "ऑटो"), "GRASIM": ("GRASIM", "Diversified", "डाइवर्सिफाइड"),
    "JSWSTEEL": ("JSW STEEL", "Metals", "मेटल"), "HINDALCO": ("HINDALCO", "Metals", "मेटल"),
    "BRITANNIA": ("BRITANNIA", "FMCG", "एफएमसीजी"), "APOLLOHOSP": ("APOLLO HOSPITALS", "Healthcare", "हेल्थकेयर"),
    "TRENT": ("TRENT", "Retail", "रिटेल"), "INDIGO": ("INDIGO", "Aviation", "एविएशन"),
    "HAL": ("HAL", "Defence", "डिफेंस"), "BEL": ("BEL", "Defence", "डिफेंस"),
    "COFORGE": ("COFORGE", "IT", "आईटी"), "DIVISLAB": ("DIVIS LABS", "Pharma", "फार्मा"),
    "ADANIPORTS": ("ADANI PORTS", "Ports", "पोर्ट"), "PIDILITIND": ("PIDILITE", "Chemicals", "केमिकल"),
}


# ───────────────────────────── data & picking ─────────────────────────────────

def load_hist():
    try:
        return json.loads(HIST.read_text(encoding="utf-8")).get("items", [])
    except Exception:
        return []


def save_hist(items):
    HIST.parent.mkdir(parents=True, exist_ok=True)
    HIST.write_text(json.dumps({"items": items[-80:]}, indent=1, ensure_ascii=False), encoding="utf-8")


def find_event(c, v):
    """Latest first-in-cluster 50-day closing-high breakout 24-90 sessions old, with outcome. c, v = pandas Series."""
    hi = c.rolling(50).max().shift(1)
    brk = (c > hi)
    n = len(c)
    # SEBI (Jan 2025 circular on educational content by unregistered persons, as reported): market data used in education
    # must be at least ~3 months old. Everything shown (the whole chart window) therefore ends before today - 92 days.
    limit = dt.date.today() - dt.timedelta(days=AGE_DAYS)
    cut = max((k for k in range(n) if c.index[k].date() <= limit), default=-1)
    if cut < 80:
        return None
    for i in range(cut - 21, max(50, cut - 130), -1):
        if not bool(brk.iloc[i]) or bool(brk.iloc[max(0, i - 10):i].any()) or i + 21 > cut:
            continue
        level = float(hi.iloc[i])
        close_i = float(c.iloc[i])
        after = c.iloc[i + 1:i + 21]
        end = float(c.iloc[i + 20])
        if end < level * 0.99:
            outcome = "failed"
        elif end > close_i * 1.03 and float(after.min()) >= level * 0.985:
            outcome = "worked"
        else:
            outcome = "flat"
        vr = float(v.iloc[i]) / max(1.0, float(v.iloc[max(0, i - 20):i].mean()))
        volume = "high" if vr >= 1.5 else ("low" if vr < 1.0 else "average")
        s, e = max(0, i - 45), min(cut + 1, i + 26)
        return {"outcome": outcome, "volume": volume, "level": level, "idx": i - s,
                "closes": [float(x) for x in c.iloc[s:e].tolist()], "date": str(c.index[i].date())}
    return None


def pick_case(today, only=None):
    import yfinance as yf
    hist = load_hist()
    recent = {h["symbol"] for h in hist if (today - dt.date.fromisoformat(h["date"])).days < COOLDOWN_DAYS}
    want = PATTERN[len(hist) % len(PATTERN)]
    syms = [only] if only else sorted(STOCKS, key=lambda s: hashlib.md5((s + str(today.toordinal())).encode()).hexdigest())
    tick = {s: s + ".NS" for s in syms}
    data = yf.download(list(tick.values()), period="1y", interval="1d", group_by="ticker", auto_adjust=False,
                       progress=False, threads=True)
    fallback = None
    for s in syms:
        if s in recent and not only:
            continue
        try:
            d = data[tick[s]].dropna()
            if len(d) < 120:
                continue
            ev = find_event(d["Close"], d["Volume"])
        except Exception:
            continue
        if not ev:
            continue
        ev["symbol"] = s
        if ev["outcome"] == want or only:
            return ev, want
        fallback = fallback or ev
    return fallback, want


# ───────────────────────────── script ─────────────────────────────────────────

def hindi_script(name, sector_hi, ev, seed):
    k = int(hashlib.md5((name + ev["date"]).encode()).hexdigest(), 16)
    intro = [
        f"यह {name} का एक पुराना उदाहरण है। {sector_hi} सेक्टर की यह बड़ी कंपनी है। यह कोई सलाह नहीं है।",
        f"चलिए {name} का एक पुराना चार्ट देखते हैं। यह सिर्फ़ सीखने के लिए है, कोई सलाह नहीं।",
        f"{name}, {sector_hi} की एक बड़ी कंपनी। आज इसका एक पुराना ब्रेकआउट देखते हैं। यह कोई सिफ़ारिश नहीं है।",
    ][k % 3]
    brk = [
        "कुछ हफ़्ते पहले इसने अपने पचास दिन के सबसे ऊँचे बंद भाव को पार किया। चार्ट की भाषा में इसे ब्रेकआउट कहते हैं।",
        "उस दिन भाव पचास दिन के ऊँचे स्तर के ऊपर बंद हुआ। यही ब्रेकआउट का पैटर्न है।",
        "इसने अपने पिछले पचास दिन के ऊँचे बंद स्तर को तोड़ा। इसे ब्रेकआउट कहते हैं।",
    ][(k // 3) % 3]
    vol = {
        "high": "उस दिन वॉल्यूम सामान्य से काफ़ी ज़्यादा था। यानी बड़े खरीदारों की दिलचस्पी दिखी।",
        "average": "उस दिन वॉल्यूम लगभग सामान्य था। ज़्यादा जोश नहीं दिखा।",
        "low": "उस दिन वॉल्यूम सामान्य से कम था। यह कमज़ोर संकेत माना जाता है।",
    }[ev["volume"]]
    res = {
        "worked": "इसके बाद भाव उस स्तर के ऊपर टिका रहा। पुराना ऊँचा स्तर सपोर्ट बन गया, और भाव आगे बढ़ा।",
        "failed": "लेकिन कुछ ही दिनों में भाव उस स्तर के नीचे लौट आया। यह एक फ़ेल हुआ ब्रेकआउट था, और ऐसा अक्सर होता है।",
        "flat": "इसके बाद भाव कई दिन उसी स्तर के आसपास घूमता रहा। न ज़्यादा चढ़ा, न ज़्यादा गिरा।",
    }[ev["outcome"]]
    lesson = ("सबक: हर ब्रेकआउट नहीं चलता। वॉल्यूम, सपोर्ट और अपना स्टॉप लॉस पहले से तय रखो। "
              "यह सलाह नहीं है। AI360Trading को फ़ॉलो करो।")
    return [intro, brk, vol, res, lesson]


# ───────────────────────────── build ──────────────────────────────────────────

def build(ev, out_dir):
    from moviepy.editor import AudioFileClip, CompositeAudioClip
    from moviepy.audio.AudioClip import AudioArrayClip
    import story_short as SS
    import story_motion as SM
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    sym = ev["symbol"]
    name, sector, sector_hi = STOCKS.get(sym, (sym, "", ""))
    lines = hindi_script(name, sector_hi, ev, 0)
    text = " ".join(lines)
    ap = out_dir / f"{sym}_case.mp3"
    E.make_voice(text, ap, "+22%", "+4Hz")
    voice = AudioFileClip(str(ap))
    dur = voice.duration + 1.0
    draw = round(dur * 0.8, 1)   # the chart draws along the narration, not in the first few seconds
    res_word = {"worked": "HELD ABOVE", "failed": "FELL BACK", "flat": "SIDEWAYS"}[ev["outcome"]]
    vol_word = ev["volume"].upper()
    spec = {
        "tag": "PAST CASE STUDY", "title": name, "subtitle": f"{sector} | a past breakout, not advice",
        "closes": ev["closes"], "overlay": ("level", ev["level"]), "overlay_label": "50-DAY HIGH",
        "accent": SS.GREEN if ev["outcome"] == "worked" else (SS.RED if ev["outcome"] == "failed" else SS.GOLD),
        "end_tag": res_word, "draw_secs": draw,
        "chips": [["PATTERN", "BREAKOUT"], ["VOLUME", vol_word], ["RESULT", res_word]],
    }
    clip = SS.make_clip_factory(spec, E.FONTS)(dur)
    bed = SM.ambient(dur, mood="calm")
    bed = AudioArrayClip(np.stack([bed, bed], axis=1), fps=44100)
    clip = clip.set_audio(CompositeAudioClip([bed, voice.set_start(0.4)]).set_duration(dur)).set_fps(24)
    mp4 = out_dir / f"{sym}_case.mp4"
    clip.write_videofile(str(mp4), fps=24, codec="libx264", audio_codec="aac", preset="medium", logger=None)
    thumb = out_dir / f"{sym}_thumb.jpg"
    try:
        import thumb_kit as tk
        img = tk.stock_card(name, "A past breakout: did it hold?", ev["closes"], level=ev["level"], level_label="50-DAY HIGH",
                            series="CASE STUDY", chips=[("Pattern", "Breakout"), ("Volume", ev["volume"].title()), ("Result", res_word.title())],
                            accent=spec["accent"])
        tk.save(img, str(thumb))
    except Exception as e:
        print(f"[CASE] thumbnail skipped (fail-open): {e}")
        thumb = None
    title = f"{name}: Ye Breakout Chala Ya Fail Hua? | Breakout Stocks Hindi #shorts"[:100]
    NL = chr(10)
    desc = ("यह एक पुराना (historical) शैक्षणिक उदाहरण है, कोई सलाह या सिफ़ारिश नहीं। कोई एंट्री, स्टॉप लॉस या टार्गेट नहीं दिया गया है। " + NL +
            "In our own 5-year backtest of 50-day closing-high breakouts, fewer than half of the trades won. "
            "Past example only. Not investment advice or a recommendation to buy or sell. The voice is a synthetic (AI) voice. "
            "AI360Trading is not SEBI registered." + NL + NL +
            "More free lessons: https://ai360trading.in/tutorial-videos/" + NL + NL +
            "#BreakoutStocks #StockMarketIndia #ChartPattern #AI360Trading #Hindi")
    tags = ["breakout stocks hindi", "stock market india", "chart pattern", "volume breakout", "support resistance hindi",
            "share market sikhe", "AI360Trading", "shorts"]
    caption = (f"{name}: एक पुराना ब्रेकआउट, आगे क्या हुआ?" + NL + NL + lines[3] + NL + NL + lines[4])
    meta = {"title": title, "description": desc, "tags": tags, "caption": caption, "duration_s": round(clip.duration, 1),
            "symbol": sym, "outcome": ev["outcome"]}
    (out_dir / f"{sym}_meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[CASE] built {mp4} ({meta['duration_s']}s) {sym} outcome={ev['outcome']} volume={ev['volume']}")
    return mp4, thumb, meta


def run(mode, out_dir, symbol=None):
    """Never raises; always returns 0."""
    try:
        today = dt.date.today()
        ev, want = pick_case(today, symbol)
        if not ev:
            E._tg("AI360 stock case Short: no suitable past breakout found today, nothing published.")
            print("[CASE] no event found")
            return 0
        print(f"[CASE] wanted outcome={want}; picked {ev['symbol']} outcome={ev['outcome']} date={ev['date']}")
        mp4, thumb, meta = build(ev, out_dir)
        if meta["duration_s"] > 59.0:
            E._tg(f"AI360 stock case Short: {ev['symbol']} is {meta['duration_s']}s (over 59s), NOT uploaded.")
            return 0
        if mode == "dry":
            print(f"[CASE] DRY RUN, nothing uploaded: {meta['title']}")
            return 0
        from human_touch import ai_disclosure
        try:
            import money_funnel as mf
            funnel = mf.funnel_block("hi", compact=True)
        except Exception:
            funnel = "Telegram: https://t.me/ai360trading" + chr(10) + "Website: https://ai360trading.in"
        NL = chr(10)
        desc = meta["description"] + NL + NL + funnel + NL + NL + ai_disclosure("hi")
        if mode == "private-test":
            vid = E._upload(str(mp4), "[TEST - private] " + meta["title"], desc, meta["tags"], str(thumb) if thumb else "", None, lang="hi")
            print(f"[CASE] PRIVATE TEST uploaded: https://youtu.be/{vid}")
            return 0
        when = E._next_publish()
        vid = E._upload(str(mp4), meta["title"], desc, meta["tags"], str(thumb) if thumb else "", when, lang="hi")
        print(f"[CASE] scheduled {vid} for {when.isoformat()}")
        hist = load_hist()
        hist.append({"symbol": ev["symbol"], "date": today.isoformat(), "outcome": ev["outcome"], "video": vid})
        save_hist(hist)
        E._tg("<b>New Hindi case-study Short</b>: " + meta["title"] + chr(10) + "Goes live " + when.strftime("%a %d %b, %H:%M")
              + " UTC" + chr(10) + "https://youtu.be/" + vid)
    except Exception as e:
        import traceback
        traceback.print_exc()
        E._tg(f"AI360 stock case Short: pipeline error: {str(e)[:160]}. Nothing published; it will retry next run.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--mode", default="dry", choices=["dry", "private-test", "scheduled"])
    ap.add_argument("--out", default="output/case")
    ap.add_argument("--symbol", default=None)
    a = ap.parse_args()
    if a.run:
        sys.exit(run(a.mode, a.out, a.symbol))
    print("usage: python stock_case.py --run --mode dry|private-test|scheduled")
