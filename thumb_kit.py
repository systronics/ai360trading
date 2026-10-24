"""
thumb_kit.py v1.0 (2026-10-23) — real-chart thumbnails and share cards, free (Pillow + yfinance only).

Why: the old thumbnails were plain text on a dark background (clipped labels, overlapping numbers,
empty half-frames, no chart). Every card here shows a REAL price line, the stock / index NAME and ONE
big message. Rules baked in:
  * text is always shrink-to-fit (no clipping, no overlaps) and never contains emoji
    (DejaVu on the CI runner has no emoji glyphs — see CLAUDE.md invariant);
  * no entry / stop-loss / target on any public image — only descriptive facts;
  * fail-open: every public function returns None on error so callers keep their old thumbnail.

Layouts
  vertical   1080x1920  Shorts / reels
  landscape  1280x720   YouTube lessons, article hero / social share
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

GOLD, GREEN, RED = (255, 200, 50), (0, 214, 110), (240, 72, 72)
WHITE, MUTED, BLUE = (244, 247, 252), (150, 166, 196), (96, 165, 255)
BG_TOP, BG_BOT = (5, 8, 20), (14, 22, 58)

_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def _font(size):
    for p in _FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _fit(draw, text, max_w, start, floor=28):
    size = start
    while size > floor:
        f = _font(size)
        if draw.textbbox((0, 0), text, font=f)[2] <= max_w:
            return f
        size -= 4
    return _font(floor)


def _wrap_fit(draw, text, max_w, start, floor=44, max_lines=2):
    """Largest font at which `text` wraps into <= max_lines lines. Returns (font, lines)."""
    words = text.split()
    size = start
    while size >= floor:
        f = _font(size)
        lines, cur = [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textbbox((0, 0), t, font=f)[2] <= max_w:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        if len(lines) <= max_lines and all(draw.textbbox((0, 0), l, font=f)[2] <= max_w for l in lines):
            return f, lines
        size -= 4
    return _font(floor), [text]


def _bg(w, h, accent):
    img = Image.new("RGB", (w, h))
    px = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        px.line([(0, y), (w, y)], fill=tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([(w * 0.35, h * 0.30), (w * 1.25, h * 0.95)], fill=accent + (60,))
    glow = glow.filter(ImageFilter.GaussianBlur(max(w, h) // 8))
    return Image.alpha_composite(img.convert("RGBA"), glow)


def _ema(vals, span):
    a, e, out = 2.0 / (span + 1), vals[0], []
    for v in vals:
        e = a * v + (1 - a) * e
        out.append(e)
    return out


_CLOSE_CACHE = {}


def get_closes(ticker, days=90):
    """Real daily closes, oldest first (cached per run). Raises on failure (callers wrap)."""
    key = (ticker, days)
    if key in _CLOSE_CACHE:
        return _CLOSE_CACHE[key]
    import yfinance as yf
    d = yf.Ticker(ticker).history(period="9mo", interval="1d")["Close"].dropna()
    if len(d) < 40:
        raise RuntimeError(f"only {len(d)} closes for {ticker}")
    out = [float(v) for v in d.iloc[-days:]]
    _CLOSE_CACHE[key] = out
    return out


def _chart(img, box, closes, accent, level=None, ema_span=None, level_label=""):
    """Draw a real price line (area fill + glow + end marker) inside box=(x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    n = len(closes)
    ema = _ema(closes, ema_span) if ema_span else None
    allv = list(closes) + ([level] if level else []) + (ema or [])
    lo, hi = min(allv), max(allv)
    pad = (hi - lo) * 0.10 or 1.0
    lo, hi = lo - pad, hi + pad

    def px(i):
        return x0 + (x1 - x0) * i / (n - 1)

    def py(v):
        return y1 - (y1 - y0) * (v - lo) / (hi - lo)

    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k in range(5):
        y = y0 + (y1 - y0) * k / 4
        d.line([(x0, y), (x1, y)], fill=(255, 255, 255, 22), width=2)
    pts = [(px(i), py(c)) for i, c in enumerate(closes)]
    d.polygon(pts + [(pts[-1][0], y1), (pts[0][0], y1)], fill=accent + (50,))
    if ema:
        d.line([(px(i), py(v)) for i, v in enumerate(ema)], fill=BLUE + (255,), width=max(5, (x1 - x0) // 150))
    if level:
        y, x = py(level), x0
        while x < x1:
            d.line([(x, y), (min(x + 22, x1), y)], fill=GOLD + (255,), width=max(4, (x1 - x0) // 200))
            x += 38
        if level_label:
            d.text((x0 + 8, y - 12), level_label, font=_font(max(24, (x1 - x0) // 28)), fill=GOLD + (255,), anchor="ls")
    lw = max(5, min((x1 - x0) // 110, (y1 - y0) // 45))
    d.line(pts, fill=(255, 255, 255, 70), width=lw * 2, joint="curve")
    d.line(pts, fill=WHITE + (255,), width=lw, joint="curve")
    hx, hy = pts[-1]
    r = max(10, min((x1 - x0) // 60, (y1 - y0) // 14))
    d.ellipse([(hx - r * 2, hy - r * 2), (hx + r * 2, hy + r * 2)], fill=accent + (70,))
    d.ellipse([(hx - r, hy - r), (hx + r, hy + r)], fill=accent + (255,), outline=WHITE + (255,), width=4)
    return Image.alpha_composite(img, ov)


def _pill(d, cx, cy, text, fill, fg=(10, 10, 10), size=44, pad=26):
    f = _font(size)
    tw = d.textbbox((0, 0), text, font=f)[2]
    d.rounded_rectangle([(cx - tw // 2 - pad, cy - size // 2 - 14), (cx + tw // 2 + pad, cy + size // 2 + 14)],
                        radius=(size + 28) // 2, fill=fill)
    d.text((cx, cy), text, font=f, fill=fg, anchor="mm")


def _pill_left(d, x, cy, text, fill, fg=(10, 10, 10), size=44, pad=26):
    tw = d.textbbox((0, 0), text, font=_font(size))[2]
    _pill(d, x + pad + tw // 2, cy, text, fill, fg=fg, size=size, pad=pad)


def _arrow(d, cx, cy, up, color, s=22):
    pts = [(cx, cy - s), (cx - s, cy + s), (cx + s, cy + s)] if up else [(cx, cy + s), (cx - s, cy - s), (cx + s, cy - s)]
    d.polygon(pts, fill=color)


# ───────────────────────────── public cards ─────────────────────────────────

def stock_card(name, headline, closes, level=None, level_label="50-DAY HIGH", series="CHART STORY",
               chips=None, accent=GREEN, size="vertical"):
    """Chart story card. name = stock name (big), headline = one short sentence.
    chips = [(label, value), ...] descriptive facts only (max 3). Returns a PIL RGB image."""
    try:
        v = size == "vertical"
        W, H = (1080, 1920) if v else (1280, 720)
        img = _bg(W, H, accent)
        d = ImageDraw.Draw(img, "RGBA")
        d.rectangle([(0, 0), (W, 14)], fill=accent + (255,))
        d.rectangle([(0, H - 14), (W, H)], fill=accent + (255,))
        m = 70 if v else 60
        _pill_left(d, m, 120 if v else 70, series, GOLD, size=40 if v else 30, pad=24)
        f = _fit(d, name, W - 2 * m, 230 if v else 150, 90)
        ty = 330 if v else 165
        d.text((m, ty), name, font=f, fill=WHITE, anchor="lm")
        hf, hl = _wrap_fit(d, headline, W - 2 * m, 74 if v else 52, 40, 2)
        hy = ty + (150 if v else 100)
        for k, line in enumerate(hl):
            d.text((m, hy + k * (hf.size + 10)), line, font=hf, fill=accent, anchor="lm")
        box = (m, 640, W - m, 1330) if v else (m, 345, W - m, 555)
        img = _chart(img, box, closes, accent, level=level, level_label=level_label)
        d = ImageDraw.Draw(img, "RGBA")
        chips = (chips or [])[:3]
        if chips:
            cy0, ch = (1420, 190) if v else (580, 70)
            gap = 20
            cw = (W - 2 * m - gap * (len(chips) - 1)) // len(chips)
            for k, (lab, val) in enumerate(chips):
                x = m + k * (cw + gap)
                d.rounded_rectangle([(x, cy0), (x + cw, cy0 + ch)], radius=22, fill=(26, 36, 74, 255), outline=(62, 76, 118, 255), width=2)
                if v:
                    d.text((x + cw // 2, cy0 + 46), lab, font=_font(32), fill=MUTED, anchor="mm")
                    d.text((x + cw // 2, cy0 + 126), val, font=_fit(d, val, cw - 30, 60, 30), fill=WHITE, anchor="mm")
                else:
                    d.text((x + cw // 2, cy0 + ch // 2), f"{lab}  {val}", font=_fit(d, f"{lab}  {val}", cw - 24, 34, 20), fill=WHITE, anchor="mm")
        d.text((W // 2, H - 70 if v else H - 24), "ai360trading.in", font=_font(36 if v else 22), fill=(120, 136, 172), anchor="mm")
        return img.convert("RGB")
    except Exception as e:
        print(f"[THUMB_KIT] stock_card failed (fail-open): {e}")
        return None


def market_card(level, pct, closes, mood, tickers=None, series="MORNING BRIEF", ema_span=50, size="vertical"):
    """Morning/evening market card: NIFTY level big, real index line with its 50-day average,
    one mood pill and up to 3 compact ticker rows [(label, value_str, pct), ...]."""
    try:
        v = size == "vertical"
        up = pct >= 0
        accent = GREEN if mood == "BULLISH" else RED if mood == "BEARISH" else GOLD
        W, H = (1080, 1920) if v else (1280, 720)
        img = _bg(W, H, accent)
        d = ImageDraw.Draw(img, "RGBA")
        d.rectangle([(0, 0), (W, 14)], fill=accent + (255,))
        d.rectangle([(0, H - 14), (W, H)], fill=accent + (255,))
        m = 70 if v else 60
        _pill_left(d, m, 120 if v else 70, series, GOLD, size=40 if v else 30, pad=24)
        d.text((m, 300 if v else 175), "NIFTY 50", font=_font(60 if v else 40), fill=MUTED, anchor="lm")
        lvl = f"{level:,.0f}"
        f = _fit(d, lvl, W - 2 * m, 250 if v else 150, 90)
        ly = 450 if v else 270
        d.text((m, ly), lvl, font=f, fill=WHITE, anchor="lm")
        sign = f"{pct:+.2f}%"
        ry = 640 if v else 365
        _arrow(d, m + 30, ry, up, GREEN if up else RED, s=26 if v else 18)
        d.text((m + 80, ry), sign, font=_font(84 if v else 52), fill=GREEN if up else RED, anchor="lm")
        _pill(d, W - m - (170 if v else 130), ry, mood, accent, fg=(10, 10, 10) if mood != "BEARISH" else (255, 255, 255), size=48 if v else 34)
        box = (m, 740, W - m, 1280) if v else (m, 410, W - m, 600)
        img = _chart(img, box, closes, accent, ema_span=ema_span)
        d = ImageDraw.Draw(img, "RGBA")
        d.text((m, 1310 if v else 612), "-- 50-day average", font=_font(34 if v else 22), fill=BLUE, anchor="lm")
        if tickers:
            ty, rh = (1390, 120) if v else (645, 0)
            for k, (lab, val, tp) in enumerate(tickers[:3]):
                if v:
                    y = ty + k * (rh + 14)
                    d.rounded_rectangle([(m, y), (W - m, y + rh)], radius=22, fill=(26, 36, 74, 255))
                    d.text((m + 30, y + rh // 2), lab, font=_font(44), fill=MUTED, anchor="lm")
                    d.text((W // 2 + 40, y + rh // 2), val, font=_font(48), fill=WHITE, anchor="lm")
                    c = GREEN if tp >= 0 else RED
                    _arrow(d, W - m - 215, y + rh // 2, tp >= 0, c, s=14)
                    d.text((W - m - 30, y + rh // 2), f"{tp:+.1f}%", font=_font(46), fill=c, anchor="rm")
                else:
                    x = m + k * ((W - 2 * m) // 3)
                    c = GREEN if tp >= 0 else RED
                    d.text((x, ty), f"{lab} {val} ", font=_font(26), fill=MUTED, anchor="lm")
                    d.text((x + 215, ty), f"{tp:+.1f}%", font=_font(26), fill=c, anchor="lm")
        d.text((W // 2, H - 70 if v else H - 22), "ai360trading.in", font=_font(36 if v else 22), fill=(120, 136, 172), anchor="mm")
        return img.convert("RGB")
    except Exception as e:
        print(f"[THUMB_KIT] market_card failed (fail-open): {e}")
        return None


def concept_card(title, subtitle, closes, series="TRADER'S NOTEBOOK", accent=GOLD, ema_span=None,
                 big_number=None, size="vertical", face=None):
    """Evergreen concept card (indicator / rule / book idea): big title (and optional big number)
    over a real index chart. Used for Trader's Notebook, lessons and article share images."""
    try:
        v = size == "vertical"
        W, H = (1080, 1920) if v else ((1200, 630) if size == "og" else (1280, 720))
        img = _bg(W, H, accent)
        d = ImageDraw.Draw(img, "RGBA")
        d.rectangle([(0, 0), (W, 14)], fill=accent + (255,))
        d.rectangle([(0, H - 14), (W, H)], fill=accent + (255,))
        m = 70 if v else 60
        _pill_left(d, m, 120 if v else 70, series, GOLD, size=40 if v else 30, pad=24)
        # optional presenter cut-out (landscape/og only): text + chart use the left ~62%, the face fills the right
        fimg = None
        if face and not v:
            try:
                fimg = Image.open(face).convert("RGBA")
                fh = int(H * 0.93)
                fimg = fimg.resize((int(fimg.width * fh / fimg.height), fh), Image.LANCZOS)
            except Exception:
                fimg = None
        rpad = (fimg.width + 30) if fimg else 0
        top = 270 if v else 150
        if big_number:
            f = _fit(d, big_number, W - 2 * m, 300 if v else 170, 120)
            d.text((m, top + (130 if v else 60)), big_number, font=f, fill=accent, anchor="lm")
            top += 380 if v else 190
        tf, tl = _wrap_fit(d, title, W - 2 * m - rpad, 120 if v else 76, 52, 3 if v else 2)
        for k, line in enumerate(tl):
            d.text((m, top + k * (tf.size + 12)), line, font=tf, fill=WHITE, anchor="lm")
        yb = top + len(tl) * (tf.size + 12)
        sf, sl = _wrap_fit(d, subtitle, W - 2 * m - rpad, 52 if v else 34, 28, 2)
        for k, line in enumerate(sl):
            d.text((m, yb + 30 + k * (sf.size + 8)), line, font=sf, fill=MUTED, anchor="lm")
        ytop = max(yb + 40 + len(sl) * (sf.size + 8) + 20, 880 if v else 400)
        box = (m, ytop, W - m - rpad, 1700 if v else H - 70)
        img = _chart(img, box, closes, accent, ema_span=ema_span)
        if fimg is not None:
            img.alpha_composite(fimg, (W - fimg.width - 10, H - fimg.height - 14))
        d = ImageDraw.Draw(img, "RGBA")
        d.text(((W - rpad) // 2, H - 60 if v else H - 28), "ai360trading.in", font=_font(34 if v else 22), fill=(120, 136, 172), anchor="mm")
        return img.convert("RGB")
    except Exception as e:
        print(f"[THUMB_KIT] concept_card failed (fail-open): {e}")
        return None


def save(img, path):
    """Save a card; returns the Path or None (fail-open)."""
    try:
        if img is None:
            return None
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(p), quality=95)
        return p
    except Exception as e:
        print(f"[THUMB_KIT] save failed: {e}")
        return None
