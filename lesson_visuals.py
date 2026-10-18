"""
lesson_visuals.py — landscape (1280x720) scene renderers for the lesson engine (v1.0, 2026-10-18)
================================================================================================
Pure Pillow + numpy. Each scene function returns a make_frame(t) closure for a given duration;
lesson_engine.py wraps them in moviepy VideoClips. No emoji (DejaVu has no emoji glyphs on the
GitHub runner), rupee written as "Rs". Everything is deterministic and needs no network.
"""

import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
BG_TOP, BG_BOT = (7, 11, 26), (14, 22, 52)
WHITE, MUTED = (240, 244, 252), (150, 165, 195)
GOLD, GREEN, RED, BLUE, ORANGE = (255, 200, 50), (0, 210, 110), (235, 70, 70), (90, 160, 255), (255, 150, 60)

FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
_cache = {}


def font(size, extra=None):
    key = (size, tuple(extra or ()))
    if key in _cache:
        return _cache[key]
    f = None
    for p in list(extra or []) + FONTS:
        if os.path.exists(p):
            try:
                f = ImageFont.truetype(p, size)
                break
            except Exception:
                continue
    f = f or ImageFont.load_default()
    _cache[key] = f
    return f


def _bg():
    top, bot = np.array(BG_TOP, float), np.array(BG_BOT, float)
    t = np.linspace(0, 1, H)[:, None]
    col = (top + (bot - top) * t).astype(np.uint8)
    return Image.fromarray(np.repeat(col[:, None, :], W, axis=1))


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def fade(t, start, length=0.6):
    return int(255 * ease((t - start) / length))


def wrap(draw, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textbbox((0, 0), test, font=f)[2] <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _header(d, tag, title, accent=GOLD):
    d.rectangle([(0, 0), (W, 8)], fill=accent + (255,))
    d.text((60, 44), tag, font=font(24), fill=accent + (255,), anchor="lm")
    f = font(40)
    lines = wrap(d, title, f, W - 120)[:2]
    for i, ln in enumerate(lines):
        d.text((60, 88 + i * 46), ln, font=f, fill=WHITE + (255,), anchor="lm")
    d.text((W - 60, 44), "ai360trading.in", font=font(22), fill=MUTED + (255,), anchor="rm")


# ───────────────────────────── title scene ──────────────────────────────────

def title_scene(heading, sub, tag="LESSON"):
    base = _bg()
    d = ImageDraw.Draw(base, "RGBA")
    d.rectangle([(0, 0), (W, 8)], fill=GOLD + (255,))
    d.rectangle([(0, H - 8), (W, H)], fill=GOLD + (255,))
    d.text((W // 2, 150), tag, font=font(34), fill=GOLD + (255,), anchor="mm")
    f = font(78)
    lines = wrap(d, heading, f, W - 160)[:3]

    def make_frame(t):
        img = base.copy()
        o = ImageDraw.Draw(img, "RGBA")
        y = 300 - (len(lines) - 1) * 44
        for i, ln in enumerate(lines):
            o.text((W // 2, y + i * 92), ln, font=f, fill=WHITE + (fade(t, 0.2 + i * 0.35),), anchor="mm")
        o.text((W // 2, 560), sub, font=font(32), fill=MUTED + (fade(t, 1.4),), anchor="mm")
        return np.array(img.convert("RGB"))

    return make_frame


# ───────────────────────────── text / bullets scene ─────────────────────────

def text_scene(heading, items, tag="LESSON", accent=GOLD, rule=None):
    """items = list of strings shown one by one; rule = optional highlighted rule line."""
    base = _bg()
    d = ImageDraw.Draw(base, "RGBA")
    _header(d, tag, heading, accent)
    fi = font(34)
    laid = []
    y = 230
    for it in items:
        ls = wrap(d, it, fi, W - 190)
        laid.append((y, ls))
        y += len(ls) * 44 + 22
    rule_y = min(y + 10, 580)

    def make_frame(t):
        img = base.copy()
        o = ImageDraw.Draw(img, "RGBA")
        for k, (yy, ls) in enumerate(laid):
            a = fade(t, 0.6 + k * 1.4)
            o.ellipse([(70, yy + 10), (86, yy + 26)], fill=accent + (a,))
            for j, ln in enumerate(ls):
                o.text((110, yy + j * 44), ln, font=fi, fill=WHITE + (a,), anchor="lm")
        if rule:
            a = fade(t, 0.6 + len(laid) * 1.4 + 0.4)
            o.rounded_rectangle([(60, rule_y), (W - 60, rule_y + 96)], radius=18, fill=accent + (int(a * 0.16),), outline=accent + (a,), width=3)
            rl = wrap(o, rule, font(32), W - 170)[:2]
            for j, ln in enumerate(rl):
                o.text((90, rule_y + 30 + j * 38), ln, font=font(32), fill=accent + (a,), anchor="lm")
        return np.array(img.convert("RGB"))

    return make_frame


# ───────────────────────────── chart scene ──────────────────────────────────

def chart_scene(title, series, tag="REAL CHART", level=None, level_label="", ema=None, markers=None,
                trail=None, panel=None, accent=GREEN, reveal_to=None, date_fmt="%b %Y"):
    """series = [(date, close)], ema = list aligned to series, markers = [(idx, label, rgb)],
    trail = [(idx, value)] (drawn as a stepped orange line), panel = [(label, value, rgb)]
    shown on the right, reveal_to = last index to animate to (default: all)."""
    closes = [v for _, v in series]
    n = len(closes)
    last_idx = (n - 1) if reveal_to is None else min(reveal_to, n - 1)
    X0, X1, Y0, Y1 = 70, 880, 175, 600
    allv = list(closes)
    if level is not None:
        allv.append(level)
    if ema:
        allv += list(ema)
    if trail:
        allv += [v for _, v in trail]
    lo, hi = min(allv), max(allv)
    pad = (hi - lo) * 0.08 or 1.0
    lo, hi = lo - pad, hi + pad

    def px(i):
        return X0 + (X1 - X0) * i / max(n - 1, 1)

    def py(v):
        return Y1 - (Y1 - Y0) * (v - lo) / (hi - lo)

    base = _bg()
    d = ImageDraw.Draw(base, "RGBA")
    _header(d, tag, title, accent)
    for k in range(5):
        y = Y0 + (Y1 - Y0) * k / 4
        d.line([(X0, y), (X1, y)], fill=(255, 255, 255, 20), width=1)
    fd = font(22)
    d.text((X0, Y1 + 28), series[0][0].strftime(date_fmt), font=fd, fill=MUTED + (255,), anchor="lm")
    d.text((X1, Y1 + 28), series[-1][0].strftime(date_fmt), font=fd, fill=MUTED + (255,), anchor="rm")
    fl = font(24)
    fp = font(26)

    def make_frame(t, dur=[25.0]):
        draw_secs = max(2.0, dur[0] * 0.62)
        p = ease(t / draw_secs)
        kf = p * last_idx
        k = int(kf)
        frac = kf - k
        pts = [(px(i), py(closes[i])) for i in range(k + 1)]
        if k < last_idx:
            pts.append((px(k) + (px(k + 1) - px(k)) * frac, py(closes[k]) + (py(closes[k + 1]) - py(closes[k])) * frac))
        img = base.copy()
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        o = ImageDraw.Draw(ov)
        if len(pts) > 1:
            o.polygon(pts + [(pts[-1][0], Y1), (pts[0][0], Y1)], fill=accent + (40,))
        if level is not None:
            y = py(level)
            x = X0
            while x < X1:
                o.line([(x, y), (min(x + 16, X1), y)], fill=GOLD + (230,), width=3)
                x += 28
            o.text((X0 + 6, y - 20), level_label, font=fl, fill=GOLD + (255,), anchor="lm")
        if ema:
            ep = [(px(i), py(ema[i])) for i in range(min(k + 1, len(ema)))]
            if len(ep) > 1:
                o.line(ep, fill=BLUE + (255,), width=3)
        if trail:
            tp = []
            for idx, val in trail:
                if idx <= k:
                    tp.append((px(idx), py(val)))
            if len(tp) > 1:
                o.line(tp, fill=ORANGE + (255,), width=3)
        if len(pts) > 1:
            o.line(pts, fill=WHITE + (255,), width=4, joint="curve")
        for idx, label, col in (markers or []):
            if idx <= k:
                mx, my = px(idx), py(closes[idx])
                o.ellipse([(mx - 9, my - 9), (mx + 9, my + 9)], fill=col + (255,), outline=WHITE + (255,), width=2)
                above = my > (Y0 + Y1) / 2
                o.text((mx, my - 28 if above else my + 30), label, font=fl, fill=col + (255,), anchor="mm")
        # right panel
        for j, (lab, val, col) in enumerate(panel or []):
            a = fade(t, 0.8 + j * 0.9)
            y = 190 + j * 118
            o.rounded_rectangle([(930, y), (W - 50, y + 100)], radius=16, fill=(255, 255, 255, int(a * 0.08)), outline=(255, 255, 255, int(a * 0.25)), width=2)
            o.text((950, y + 28), lab, font=font(20), fill=MUTED + (a,), anchor="lm")
            o.text((950, y + 66), val, font=fp, fill=col + (a,), anchor="lm")
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        return np.array(img)

    def bind(duration):
        make_frame.__defaults__ = ([float(duration)],)
        return make_frame

    return bind


# ───────────────────────────── bars scene ───────────────────────────────────

def bars_scene(title, bars, note="", tag="THE EVIDENCE", accent=GOLD):
    """bars = [(label, value, rgb, suffix)]; positive bars grow right, negative left of a centre line."""
    base = _bg()
    d = ImageDraw.Draw(base, "RGBA")
    _header(d, tag, title, accent)
    cx, half = 760, 380
    vmax = max(abs(b[1]) for b in bars) or 1
    rows = len(bars)
    top = 230
    step = min(86, (560 - top) // rows)
    d.line([(cx, top - 20), (cx, top + rows * step)], fill=(255, 255, 255, 70), width=2)
    fl = font(28)
    for i, (lab, val, col, suf) in enumerate(bars):
        d.text((60, top + i * step + 28), lab, font=fl, fill=WHITE + (255,), anchor="lm")
    fv = font(30)

    def make_frame(t):
        img = base.copy()
        o = ImageDraw.Draw(img, "RGBA")
        for i, (lab, val, col, suf) in enumerate(bars):
            g = ease((t - 0.4 - i * 0.7) / 1.0)
            wlen = half * abs(val) / vmax * g
            y = top + i * step
            if val >= 0:
                o.rounded_rectangle([(cx, y + 6), (cx + max(wlen, 2), y + 52)], radius=8, fill=col + (255,))
                o.text((cx + wlen + 14, y + 29), f"{'+' if val > 0 else ''}{val:g}{suf}", font=fv, fill=WHITE + (int(255 * g),), anchor="lm")
            else:
                o.rounded_rectangle([(cx - wlen, y + 6), (cx, y + 52)], radius=8, fill=col + (255,))
                o.text((cx - wlen - 14, y + 29), f"{val:g}{suf}", font=fv, fill=WHITE + (int(255 * g),), anchor="rm")
        if note:
            a = fade(t, 0.4 + rows * 0.7 + 0.5)
            for j, ln in enumerate(wrap(o, note, font(26), W - 140)[:2]):
                o.text((60, 640 + j * 32), ln, font=font(26), fill=MUTED + (a,), anchor="lm")
        return np.array(img.convert("RGB"))

    return make_frame
