"""
story_short.py — real-data "chart story" Shorts (animated chart of the ACTUAL stock/index)
=========================================================================================
v1.0 (2026-10-18)

WHY
  The old Shorts were a static info card + AI voice (a 20-second still image with text).
  Retention data (avg watch ~0:17) and the 1-view reality say a still card does not hold
  attention. This module builds a real story from real data, free:
    * Hindi Short  : "STOCK STORY" — a stock from our own public breakout list
                     (publish_signal_lists.py -> _data/signal_lists.json) that just closed
                     above its 50-day closing high. The chart DRAWS ITSELF (real daily
                     closes from yfinance), the broken level appears, a marker pulses.
    * English Short: "MARKET STORY" — NIFTY's real last ~90 sessions against its own
                     50-day average, so viewers see exactly what the market is doing.
  No paid service: Pillow draws every frame, moviepy assembles it (already used), edge_tts
  speaks (already used), AI script via ai_client (Groq/Gemini free) with a deterministic
  real-number fallback script if AI is down.

SAFETY / DOCTRINE
  * FULLY FAIL-OPEN: pick_story()/clip factory/script builders raise or return None on any
    problem; generate_shorts.py then runs the previous info-card flow unchanged.
  * TEASER ONLY: never an entry price, stop-loss or target in the video — the chart shows a
    LEVEL that was broken, not a trade plan. Scripts end with the honest "watchlist, not
    advice" framing. (Trade details stay in Telegram for paid members.)
  * No emoji inside Pillow text (DejaVu has no emoji glyphs on the runner) and rupee shown
    as "Rs".
"""

import os, json, math
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BG_TOP, BG_BOT = (6, 9, 22), (16, 22, 56)
GOLD   = (255, 200, 50)
GREEN  = (0, 210, 100)
RED    = (235, 70, 70)
WHITE  = (240, 244, 252)
MUTED  = (150, 165, 195)
BLUE   = (90, 160, 255)

DEFAULT_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]

SIGNAL_JSON = Path("_data/signal_lists.json")
STORY_HISTORY = Path("_data/story_history.json")
STORY_COOLDOWN_DAYS = 21      # a stock is not told twice within three weeks


# ───────────────────────────── data ─────────────────────────────────────────

def _load_signal_lists():
    try:
        return json.loads(SIGNAL_JSON.read_text(encoding="utf-8"))
    except Exception:
        return None


def _closes(ticker, days=130):
    """Real daily closes, oldest first: [(date, close)]. Raises on failure."""
    import yfinance as yf
    d = yf.download(ticker, period="9mo", interval="1d", progress=False, auto_adjust=False)
    d.columns = d.columns.get_level_values(0)
    c = d["Close"].dropna()
    if len(c) < 60:
        raise RuntimeError(f"only {len(c)} closes for {ticker}")
    c = c.iloc[-days:]
    return [(i.date(), float(v)) for i, v in c.items()]


def _ema(vals, span):
    a = 2.0 / (span + 1)
    out, e = [], vals[0]
    for v in vals:
        e = a * v + (1 - a) * e
        out.append(e)
    return out


def _recent_symbols(now, days=STORY_COOLDOWN_DAYS):
    try:
        items = json.loads(STORY_HISTORY.read_text(encoding="utf-8")).get("items", [])
    except Exception:
        return set()
    cutoff = now.toordinal() - days
    out = set()
    for it in items:
        try:
            if datetime.fromisoformat(it["date"]).toordinal() >= cutoff:
                out.add(it["symbol"])
        except Exception:
            continue
    return out


def record_story(symbol, now=None):
    """Remember a stock we just published a story about (keeps the last 60). Fail-open."""
    try:
        now = now or datetime.now()
        try:
            items = json.loads(STORY_HISTORY.read_text(encoding="utf-8")).get("items", [])
        except Exception:
            items = []
        items.append({"symbol": symbol, "date": now.strftime("%Y-%m-%d")})
        STORY_HISTORY.parent.mkdir(parents=True, exist_ok=True)
        STORY_HISTORY.write_text(json.dumps({"items": items[-60:]}, indent=1), encoding="utf-8")
    except Exception as e:
        print(f"[STORY] history not saved (fail-open): {e}")


def pick_story(now=None):
    """Return {'stock': {...} or None, 'index': {...} or None, 'market_label': str} or None.
    Stock = a 50-day closing-high breakout from our own public list, rotated by date so
    consecutive posts differ. Index = NIFTY vs its 50-day EMA. Any failure -> that part None."""
    now = now or datetime.now()
    story = {"stock": None, "index": None, "market_label": ""}
    sl = _load_signal_lists() or {}
    story["market_label"] = (sl.get("market") or {}).get("label", "")

    try:
        cands = [b for b in (sl.get("breakout") or [])
                 if str(b.get("signal", "")).startswith("50-day") and b.get("level") and b.get("cmp")]
        if cands:
            recent = _recent_symbols(now)
            fresh = [c for c in cands[:10] if c["symbol"] not in recent]
            # strongest fresh candidate first; if every candidate was used recently, rotate the top 5
            pick = fresh[0] if fresh else cands[:5][now.toordinal() % len(cands[:5])]
            sym = pick["symbol"]
            series = _closes(sym + ".NS")
            story["stock"] = {
                "symbol": sym, "sector": pick.get("sector", ""), "cmp": float(series[-1][1]),
                "level": float(pick["level"]), "rs": pick.get("rs"),
                "sector_trend": pick.get("sector_trend", ""), "series": series,
            }
            st = story["stock"]
            st["pct_above"] = round((st["cmp"] / st["level"] - 1) * 100, 1)
    except Exception as e:
        print(f"[STORY] stock story skipped: {e}")

    try:
        ser = _closes("^NSEI")
        closes = [v for _, v in ser]
        ema = _ema(closes, 50)
        last, e50 = closes[-1], ema[-1]
        ch30 = (closes[-1] / closes[-22] - 1) * 100 if len(closes) > 22 else 0.0
        story["index"] = {"series": ser, "ema": ema, "close": last, "ema50": e50,
                          "pct_vs_ema": round((last / e50 - 1) * 100, 1),
                          "chg_1m": round(ch30, 1), "above": last > e50}
    except Exception as e:
        print(f"[STORY] index story skipped: {e}")

    if not story["stock"] and not story["index"]:
        return None
    return story


# ───────────────────────────── scripts ──────────────────────────────────────

def _fmt(v):
    return f"{v:,.0f}" if v >= 1000 else f"{v:,.1f}"


def stock_script(ai, st, market_label, content_mode="market"):
    """Hinglish story script for the stock breakout Short. Returns a dict with the same keys
    generate_shorts.py already consumes. AI first, deterministic real-number fallback."""
    sym, lvl, cmp_, pct = st["symbol"], st["level"], st["cmp"], st["pct_above"]
    sec = st.get("sector", "")
    facts = (f"Stock {sym} ({sec}). Price Rs {_fmt(cmp_)}. It just closed above its 50-day closing high of "
             f"Rs {_fmt(lvl)}, now {pct}% above that level. Relative strength vs Nifty: {st.get('rs')}%. "
             f"Sector trend: {st.get('sector_trend')}. Market: {market_label}.")
    prompt = f"""Write a 20-25 second HINGLISH (Hindi in Roman script + English trading words) YouTube Short STORY for Indian retail traders.
The video shows the REAL price chart of the stock drawing itself, a line for the level it broke, and a pulsing marker at today's price.
FACTS (use only these, never invent numbers): {facts}

RULES: tell it as a mini story (what happened, why it matters, what to be careful about). NO buy/sell instruction, NO target, NO stop-loss price, NO entry price. Say it is a watchlist idea, not advice. The most valuable / surprising line must be LAST. 55-70 words.
Return ONLY valid JSON:
{{"hook": "MAX 6 words, Hinglish, starts with a real number from the facts, creates curiosity",
 "title": "YouTube title max 8 words with a real number, e.g. '{sym} ne todha 50 din ka high'",
 "stock": "{sym}", "sentiment": "bullish",
 "entry": "Level broken", "target": "-", "sl": "-", "horizon": "Watchlist",
 "insight": "one English sentence max 15 words",
 "script": "the 55-70 word Hinglish story",
 "hashtags": "#{sym} #Breakout #Nifty200 #StockMarketIndia #ai360trading"}}"""
    data = {}
    try:
        data = ai.generate_json(prompt, content_mode=content_mode, lang="hi") or {}
    except Exception as e:
        print(f"[STORY] stock script AI error: {e}")
    if not data.get("script"):
        data = {
            "hook": f"{pct}% upar nikla {sym}",
            "title": f"{sym} ne todha 50 din ka closing high",
            "stock": sym, "sentiment": "bullish", "entry": "Level broken", "target": "-", "sl": "-",
            "horizon": "Watchlist",
            "insight": f"{sym} closed {pct}% above its 50-day closing high.",
            "script": (f"{sym} ne pichhle 50 din ka closing high, Rs {_fmt(lvl)}, paar kar liya. Ab ye Rs {_fmt(cmp_)} par hai, "
                       f"yaani level se {pct} percent upar. Breakout ka matlab pakka jeet nahi hota, kai breakout fail bhi hote hain. "
                       f"Isliye ise watchlist ki idea samjho, advice nahi. Asli sawal ye hai: kya ye level ab support ban payega?"),
            "hashtags": f"#{sym} #Breakout #Nifty200 #StockMarketIndia #ai360trading",
        }
    data["stock"] = sym
    data.setdefault("sentiment", "bullish")
    return data


def index_script(ai, ix, market_label, content_mode="market"):
    """English story script for the NIFTY market story Short."""
    rel = "above" if ix["above"] else "below"
    facts = (f"NIFTY closed at {_fmt(ix['close'])}. Its 50-day average is {_fmt(ix['ema50'])}, so the index is {abs(ix['pct_vs_ema'])}% "
             f"{rel} it. Change over the last month: {ix['chg_1m']}%.")
    prompt = f"""Write a 20-25 second ENGLISH-ONLY YouTube Short STORY about what NIFTY is doing, for Indian retail investors.
The video shows the REAL NIFTY chart drawing itself with its 50-day average line.
FACTS (use only these, never invent numbers): {facts}

RULES: mini story (what the chart shows, why traders watch the 50-day average, what to be careful about). NO buy/sell instructions, NO targets. English only, plain text, no markdown. 55-70 words. The most useful line comes LAST.
Return ONLY valid JSON:
{{"hook": "MAX 6 words, English, starts with a real number from the facts, curiosity gap",
 "title": "YouTube title max 8 words with a real number",
 "sentiment": "{'bullish' if ix['above'] else 'bearish'}",
 "insight": "one sentence max 15 words",
 "script": "the 55-70 word English story",
 "hashtags": "#Nifty50 #StockMarket #India #MarketStory #ai360trading"}}"""
    data = {}
    try:
        data = ai.generate_json(prompt, content_mode=content_mode, lang="en") or {}
    except Exception as e:
        print(f"[STORY] index script AI error: {e}")
    if not data.get("script"):
        if ix["above"]:
            tail = "That is the kind of trend traders like, but a strong trend can still pull back, so size positions with care."
        else:
            tail = "Until it climbs back above that line, many traders stay selective and keep positions small."
        data = {
            "hook": f"NIFTY is {abs(ix['pct_vs_ema'])}% {rel} its trend line",
            "title": f"NIFTY {_fmt(ix['close'])}: {abs(ix['pct_vs_ema'])}% {rel} its 50-day average",
            "sentiment": "bullish" if ix["above"] else "bearish",
            "insight": f"NIFTY is {abs(ix['pct_vs_ema'])}% {rel} its 50-day average.",
            "script": (f"NIFTY closed at {_fmt(ix['close'])}. Its 50-day average sits at {_fmt(ix['ema50'])}, so the index is "
                       f"{abs(ix['pct_vs_ema'])} percent {rel} it. Over the last month it moved {ix['chg_1m']} percent. {tail} "
                       f"The line to watch is the 50-day average."),
            "hashtags": "#Nifty50 #StockMarket #India #MarketStory #ai360trading",
        }
    return data


# ───────────────────────────── drawing ──────────────────────────────────────

def _font(paths, size):
    for p in list(paths or []) + DEFAULT_FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _gradient():
    top, bot = np.array(BG_TOP, float), np.array(BG_BOT, float)
    t = np.linspace(0, 1, H)[:, None]
    col = (top + (bot - top) * t).astype(np.uint8)          # H x 3
    return np.repeat(col[:, None, :], W, axis=1)              # H x W x 3


def _fit_text(draw, text, fonts, max_w, start, floor=44):
    size = start
    while size > floor:
        f = _font(fonts, size)
        if draw.textbbox((0, 0), text, font=f)[2] <= max_w:
            return f
        size -= 4
    return _font(fonts, floor)


def _ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def make_clip_factory(spec, fonts=None):
    """spec: {title, subtitle, closes[list float], overlay: ('level', value) | ('ema', list),
              overlay_label, accent(rgb), chips[[label,value],...], tag(str)}
    Returns factory(duration) -> moviepy VideoClip (raises ImportError if moviepy missing)."""
    from moviepy.editor import VideoClip

    closes = spec["closes"]
    n = len(closes)
    ov_kind, ov_val = spec.get("overlay", (None, None))
    accent = spec.get("accent", GREEN)

    X0, X1 = 70, W - 70
    Y0, Y1 = 560, 1190
    allv = list(closes) + ([ov_val] if ov_kind == "level" else (list(ov_val) if ov_kind == "ema" else []))
    lo, hi = min(allv), max(allv)
    pad = (hi - lo) * 0.08 or 1.0
    lo -= pad
    hi += pad

    def px(i):
        return X0 + (X1 - X0) * i / (n - 1)

    def py(v):
        return Y1 - (Y1 - Y0) * (v - lo) / (hi - lo)

    # ── static layer (background, grid, title, chips) built once ─────────────
    base = Image.fromarray(_gradient())
    d = ImageDraw.Draw(base, "RGBA")
    d.rectangle([(0, 0), (W, 14)], fill=accent + (255,))
    d.rectangle([(0, H - 14), (W, H)], fill=accent + (255,))
    f_tag = _font(fonts, 40)
    d.text((W // 2, 150), spec.get("tag", "CHART STORY"), font=f_tag, fill=GOLD, anchor="mm")
    f_title = _fit_text(d, spec["title"], fonts, W - 120, 150)
    d.text((W // 2, 280), spec["title"], font=f_title, fill=WHITE, anchor="mm")
    f_sub = _fit_text(d, spec.get("subtitle", ""), fonts, W - 140, 56, 34)
    d.text((W // 2, 420), spec.get("subtitle", ""), font=f_sub, fill=MUTED, anchor="mm")
    for k in range(5):
        y = Y0 + (Y1 - Y0) * k / 4
        d.line([(X0, y), (X1, y)], fill=(255, 255, 255, 22), width=2)
    # chips
    chips = spec.get("chips", [])
    if chips:
        cw = (W - 140 - 20 * (len(chips) - 1)) // len(chips)
        for k, (lab, val) in enumerate(chips):
            x = 70 + k * (cw + 20)
            d.rounded_rectangle([(x, 1250), (x + cw, 1420)], radius=24, fill=(255, 255, 255, 20), outline=(255, 255, 255, 50), width=2)
            d.text((x + cw // 2, 1292), lab, font=_font(fonts, 30), fill=MUTED, anchor="mm")
            d.text((x + cw // 2, 1366), val, font=_fit_text(d, val, fonts, cw - 24, 54, 30), fill=WHITE, anchor="mm")
    d.text((W // 2, 1560), "ai360trading.in", font=_font(fonts, 38), fill=(120, 135, 170), anchor="mm")
    f_lbl = _font(fonts, 34)

    def make_frame(t):
        dur = factory_state["dur"]
        draw_secs = max(2.0, min(0.6 * dur, 9.0))
        p = _ease(t / draw_secs)
        kf = p * (n - 1)
        k = int(kf)
        frac = kf - k
        pts = [(px(i), py(closes[i])) for i in range(k + 1)]
        if k < n - 1:
            xi = px(k) + (px(k + 1) - px(k)) * frac
            yi = py(closes[k]) + (py(closes[k + 1]) - py(closes[k])) * frac
            pts.append((xi, yi))
        img = base.copy()
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        # area fill under the line
        if len(pts) > 1:
            od.polygon(pts + [(pts[-1][0], Y1), (pts[0][0], Y1)], fill=accent + (46,))
        # overlay line (EMA) drawn up to the same progress
        if ov_kind == "ema":
            ep = [(px(i), py(ov_val[i])) for i in range(min(len(pts), n))]
            if len(ep) > 1:
                od.line(ep, fill=BLUE + (255,), width=7)
        # level line appears after 30% of the draw
        if ov_kind == "level" and t > 0.3 * draw_secs:
            a = int(255 * _ease((t - 0.3 * draw_secs) / 1.0))
            y = py(ov_val)
            x = X0
            while x < X1:
                od.line([(x, y), (min(x + 26, X1), y)], fill=GOLD + (a,), width=6)
                x += 46
            od.text((X0 + 10, y - 34), spec.get("overlay_label", "LEVEL"), font=f_lbl, fill=GOLD + (a,), anchor="lm")
        if len(pts) > 1:
            od.line(pts, fill=(255, 255, 255, 60), width=18, joint="curve")
            od.line(pts, fill=WHITE + (255,), width=8, joint="curve")
        # pulsing marker at the head of the line once the chart is nearly drawn
        if p > 0.92 and pts:
            hx, hy = pts[-1]
            pulse = 0.5 + 0.5 * math.sin((t - draw_secs) * 5.0)
            r = 16 + 14 * pulse
            od.ellipse([(hx - r * 1.8, hy - r * 1.8), (hx + r * 1.8, hy + r * 1.8)], fill=accent + (60,))
            od.ellipse([(hx - 14, hy - 14), (hx + 14, hy + 14)], fill=accent + (255,), outline=WHITE + (255,), width=4)
            end_tag = spec.get("end_tag", "")
            if end_tag:
                tx = min(max(hx, 200), W - 200)
                od.text((tx, hy + 74), end_tag, font=_font(fonts, 44), fill=accent + (255,), anchor="mm")
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        return np.array(img)

    factory_state = {"dur": 25.0}

    def factory(duration):
        factory_state["dur"] = float(duration)
        return VideoClip(make_frame, duration=float(duration))

    return factory


# ───────────────────────────── thumbnails ───────────────────────────────────

def story_thumbnail(kind, obj, out_path):
    """2026-10-23: real-chart cover for a story Short (thumb_kit). kind = 'stock' | 'index';
    obj = the same dict stock_spec()/index_spec() receive. Returns the saved path or None
    (fail-open — the caller keeps its classic thumbnail)."""
    try:
        import thumb_kit as tk
        closes = [v for _, v in obj["series"]][-90:]
        if kind == "stock":
            pa = float(obj.get("pct_above", 0) or 0)
            head = "Closed above its 50-day closing high" if pa >= 0 else "Broke its 50-day high, now retesting it"
            img = tk.stock_card(
                obj["symbol"], head, closes, level=obj["level"],
                level_label="50-DAY HIGH", series="CHART STORY",
                chips=[("Close", f"Rs {_fmt(obj['cmp'])}"), ("vs level", f"{pa:+.1f}%")])
        else:
            pct = (closes[-1] / closes[-2] - 1) * 100 if len(closes) > 1 else 0.0
            img = tk.market_card(obj["close"], pct, closes, "BULLISH" if obj["above"] else "BEARISH",
                                 None, series="MARKET STORY")
        p = tk.save(img, out_path)
        return str(p) if p else None
    except Exception as e:
        print(f"[STORY] thumbnail skipped (fail-open): {e}")
        return None


# ───────────────────────────── specs ────────────────────────────────────────

def stock_spec(st, fonts=None):
    closes = [v for _, v in st["series"]][-90:]
    return {
        "tag": "STOCK STORY",
        "title": st["symbol"],
        "subtitle": f"{st.get('sector', '')} | closed above its 50-day closing high".strip(" |"),
        "closes": closes, "overlay": ("level", st["level"]),
        "overlay_label": f"50-DAY CLOSING HIGH  Rs {_fmt(st['level'])}",
        "accent": GREEN, "end_tag": "BREAKOUT",
        "chips": [["PRICE", f"Rs {_fmt(st['cmp'])}"], ["LEVEL BROKEN", f"Rs {_fmt(st['level'])}"],
                  ["ABOVE LEVEL", f"+{st['pct_above']}%"]],
    }


def index_spec(ix, fonts=None):
    closes = [v for _, v in ix["series"]][-90:]
    ema = ix["ema"][-len(closes):]
    return {
        "tag": "MARKET STORY",
        "title": "NIFTY 50",
        "subtitle": "The index vs its 50-day average (blue line)",
        "closes": closes, "overlay": ("ema", ema),
        "accent": GREEN if ix["above"] else RED, "end_tag": "TODAY",
        "chips": [["NIFTY", _fmt(ix["close"])], ["50-DAY AVG", _fmt(ix["ema50"])],
                  ["VS AVG", f"{'+' if ix['pct_vs_ema'] >= 0 else ''}{ix['pct_vs_ema']}%"]],
    }
