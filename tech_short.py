"""
tech_short.py v1.0 (2026-11-01) — Hindi "how everyday technology works" Shorts (NEW channel/page line, NOT the trading channel).

Owner brief 2026-11-01: real, animated explainers that hold the public: shock question in the first 3 seconds, an easy
analogy, then a one-line takeaway / next-video hook. 5 scenes, each a Pillow-animated diagram (thermometer, particles
through a chip, bars, battery, tick cards) + natural spoken Hindi (hand-written, fact-checked) + loudness-normalised voice
+ a soft whoosh on every scene change. On-screen words are Roman (Hinglish) so every font renders.

SAMPLE ONLY for now: `python tech_short.py --sample phone_heat` writes to output/tech/. It never uploads; wiring to a
channel/page is a separate owner-approved step (the new channel + page do not exist yet).
"""
import os
import sys
import json
import math
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import emotion_story as E

W, H, FPS = 1080, 1920, 24
BG_TOP, BG_BOT = (10, 14, 32), (22, 30, 64)
WHITE, GOLD, MUTED = (255, 255, 255), (255, 200, 50), (170, 180, 205)
RED, ORANGE, BLUE, GREEN, CYAN = (255, 80, 70), (255, 150, 40), (90, 160, 255), (0, 210, 120), (70, 220, 240)

# ───────────────────────────── topics (hand-written, facts checked) ───────────────────────────────
TOPICS = {
    "phone_heat": {
        "title": "Phone Garam Kyun Hota Hai?",
        "yt_title": "Phone Garam Kyun Hota Hai? Andar Ki Asli Wajah #shorts",
        "thumb": "PHONE GARAM KYUN?",
        "tag": "HOW IT WORKS",
        "tags": ["phone garam kyun hota hai", "phone heating problem", "mobile heat hindi", "tech explained hindi", "how it works hindi", "shorts"],
        "lines": [
            "आपका फ़ोन गरम क्यों हो जाता है? अंदर देखते हैं।",
            "फ़ोन की चिप में बिजली पतली तारों से गुज़रती है, और तारें उसे थोड़ा रोकती हैं। जैसे भीड़ भरी गली में धक्का-मुक्की होती है, वैसे ही बिजली रगड़ खाती है, और वही रगड़ गरमी बन जाती है।",
            "जब आप गेम खेलते हैं, तो चिप बहुत तेज़ काम करती है। ज़्यादा काम, ज़्यादा बिजली, ज़्यादा रगड़, और ज़्यादा गरमी।",
            "चार्जिंग में भी यही होता है। बैटरी में बिजली भरते वक़्त कुछ बिजली गरमी बन जाती है, और तेज़ चार्जर में ज़्यादा।",
            "इसलिए धूप में चार्ज मत कीजिए, मोटा कवर हटाइए, और चार्जिंग में भारी गेम मत खेलिए। निचोड़ यह कि गरमी बिजली की रगड़ है। अगली बार: बैटरी जल्दी ख़त्म क्यों होती है?",
        ],
        "caps": ["PHONE GARAM KYUN?", "BIJLI KI RAGAD = GARMI", "ZYADA KAAM = ZYADA GARMI", "CHARGING MEIN BHI GARMI", "RAGAD HI GARMI HAI"],
        "scenes": ["thermo", "chip", "bars", "battery", "tips"],
        "tips": ["DHOOP MEIN CHARGE NAHI", "MOTA COVER HATAO", "CHARGING + GAME NAHI"],
    },
}

_FONT_CACHE = {}


def font(sz):
    if sz not in _FONT_CACHE:
        _FONT_CACHE[sz] = E._font(sz)
    return _FONT_CACHE[sz]


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, k):
    return a + (b - a) * k


def mix(c1, c2, k):
    return tuple(int(lerp(c1[i], c2[i], k)) for i in range(3))


_BG = None


def background():
    global _BG
    if _BG is None:
        ys = np.linspace(0, 1, H)[:, None, None]
        top, bot = np.array(BG_TOP)[None, None, :], np.array(BG_BOT)[None, None, :]
        arr = (top * (1 - ys) + bot * ys) * np.ones((H, W, 3))
        im = Image.fromarray(arr.astype(np.uint8))
        d = ImageDraw.Draw(im, "RGBA")
        for x in range(0, W, 90):
            d.line([(x, 0), (x, H)], fill=(255, 255, 255, 10), width=1)
        for y in range(0, H, 90):
            d.line([(0, y), (W, y)], fill=(255, 255, 255, 10), width=1)
        _BG = im
    return _BG.copy()


def glow(d, cx, cy, r, color, strength=1.0):
    for i in range(7):
        k = i / 7
        rr = r * (1.6 - k * 1.2)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=color + (int(16 * strength * (0.4 + k)),))


def text_c(d, xy, s, f, fill=WHITE, outline=(0, 0, 0), width=4):
    x, y = xy
    for dx in range(-width, width + 1, 2):
        for dy in range(-width, width + 1, 2):
            d.text((x + dx, y + dy), s, font=f, fill=outline + (255,), anchor="mm")
    d.text((x, y), s, font=f, fill=fill + (255,), anchor="mm")


def waves(d, cx, base_y, width, t, heat, color=ORANGE, n=4):
    """Rising wavy heat lines; heat 0..1 controls how many and how bright."""
    for i in range(n):
        x0 = cx - width / 2 + width * (i + 0.5) / n
        pts = []
        for k in range(24):
            y = base_y - k * 14 - (t * 90) % 40
            x = x0 + math.sin(k * 0.55 + t * 4 + i) * 12
            pts.append((x, y))
        a = int(190 * heat * (0.6 + 0.4 * math.sin(t * 3 + i)))
        d.line(pts, fill=color + (max(0, a),), width=7, joint="curve")


# ───────────────────────────── scene painters: (d, t, dur) ───────────────────────────────

def sc_thermo(d, t, dur):
    k = ease(t / max(dur * 0.85, 0.1))
    temp = lerp(31, 46, k)
    col = mix(BLUE, RED, k)
    cx, cy = 540, 880
    glow(d, cx, cy, 340, col, 0.6 + k)
    d.rounded_rectangle((cx - 200, cy - 340, cx + 200, cy + 340), radius=56, fill=(18, 22, 44, 255), outline=col + (255,), width=10)
    d.rounded_rectangle((cx - 170, cy - 300, cx + 170, cy + 300), radius=30, fill=mix((20, 40, 90), (120, 20, 20), k) + (255,))
    d.rounded_rectangle((cx - 40, cy - 322, cx + 40, cy - 308), radius=7, fill=(0, 0, 0, 255))
    text_c(d, (cx, cy - 40), f"{temp:.0f}°C", font(190), fill=WHITE, width=5)
    text_c(d, (cx, cy + 120), "TEMPERATURE", font(40), fill=MUTED, width=2)
    waves(d, cx, cy - 360, 300, t, k)
    # thermometer
    tx, ty0, ty1 = 880, 620, 1150
    d.rounded_rectangle((tx - 24, ty0, tx + 24, ty1), radius=24, fill=(255, 255, 255, 40), outline=WHITE + (200,), width=4)
    fh = (ty1 - ty0 - 10) * k
    d.rounded_rectangle((tx - 14, ty1 - 8 - fh, tx + 14, ty1 - 8), radius=14, fill=col + (255,))
    d.ellipse((tx - 42, ty1 - 20, tx + 42, ty1 + 64), fill=col + (255,))


def sc_chip(d, t, dur):
    k = ease(t / max(dur * 0.9, 0.1))
    cx, cy, s = 540, 900, 190
    heat = 0.25 + 0.75 * k
    glow(d, cx, cy, 260, ORANGE, heat * 1.4)
    d.rounded_rectangle((cx - s, cy - s, cx + s, cy + s), radius=30, fill=(25, 30, 56, 255), outline=mix(CYAN, ORANGE, k) + (255,), width=8)
    d.rounded_rectangle((cx - 90, cy - 90, cx + 90, cy + 90), radius=18, fill=mix((30, 60, 90), (150, 60, 20), k) + (255,))
    text_c(d, (cx, cy), "CHIP", font(70), fill=WHITE, width=3)
    for i in range(-3, 4):
        d.line([(cx + i * 50, cy - s - 40), (cx + i * 50, cy - s)], fill=MUTED + (255,), width=6)
        d.line([(cx + i * 50, cy + s), (cx + i * 50, cy + s + 40)], fill=MUTED + (255,), width=6)
        d.line([(cx - s - 40, cy + i * 50), (cx - s, cy + i * 50)], fill=MUTED + (255,), width=6)
        d.line([(cx + s, cy + i * 50), (cx + s + 40, cy + i * 50)], fill=MUTED + (255,), width=6)
    # electricity particles flowing in from the left along 5 traces
    rows = [-2, -1, 0, 1, 2]
    for ri, r in enumerate(rows):
        y = cy + r * 50
        d.line([(60, y), (cx - s - 40, y)], fill=(255, 255, 255, 40), width=5)
        for j in range(7):
            p = ((t * 0.55 + j / 7 + ri * 0.13) % 1.0)
            x = lerp(60, cx - s - 40, p)
            d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=GOLD + (255,))
    # sparks (friction) inside / around chip, more with time
    rnd = np.random.RandomState(int(t * 12) % 997)
    for _ in range(int(4 + 26 * k)):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(40, s + 20)
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=ORANGE + (230,))
    waves(d, cx, cy - s - 60, 300, t, heat, n=5)
    text_c(d, (170, cy - 170), "BIJLI", font(54), fill=GOLD, width=3)
    text_c(d, (540, cy + s + 150), "RAGAD  =  GARMI", font(64), fill=ORANGE, width=3)


def sc_bars(d, t, dur):
    k1 = ease(t / max(dur * 0.8, 0.1))
    k2 = ease((t - 0.35) / max(dur * 0.8, 0.1))
    x0, x1 = 120, 960
    for y, label, k, col in ((620, "KAAM  (GAME)", k1, BLUE), (900, "GARMI", k2, RED)):
        text_c(d, (540, y - 80), label, font(60), fill=WHITE, width=3)
        d.rounded_rectangle((x0, y - 38, x1, y + 38), radius=38, fill=(255, 255, 255, 30), outline=(255, 255, 255, 90), width=3)
        d.rounded_rectangle((x0 + 5, y - 33, x0 + 5 + (x1 - x0 - 10) * k, y + 33), radius=33, fill=col + (255,))
        text_c(d, (x1 - 10, y - 80), f"{int(k * 100)}%", font(48), fill=MUTED, width=2)
    # flame
    fx, fy, fs = 540, 1215, 70 + 80 * k2
    flick = math.sin(t * 9) * 8
    d.polygon([(fx, fy - fs * 1.5), (fx + fs * 0.7 + flick, fy - fs * 0.3), (fx + fs * 0.45, fy + fs * 0.6),
               (fx, fy + fs * 0.75), (fx - fs * 0.45, fy + fs * 0.6), (fx - fs * 0.7 - flick, fy - fs * 0.3)], fill=ORANGE + (255,))
    d.polygon([(fx, fy - fs * 0.6), (fx + fs * 0.3, fy + fs * 0.2), (fx, fy + fs * 0.55), (fx - fs * 0.3, fy + fs * 0.2)], fill=GOLD + (255,))


def sc_battery(d, t, dur):
    k = ease(t / max(dur * 0.9, 0.1))
    cx, cy = 540, 900
    heat = 0.2 + 0.8 * k
    glow(d, cx, cy, 300, mix(GREEN, ORANGE, k), 0.8)
    d.rounded_rectangle((cx - 230, cy - 130, cx + 230, cy + 130), radius=34, fill=(18, 22, 44, 255), outline=WHITE + (255,), width=9)
    d.rounded_rectangle((cx + 230, cy - 45, cx + 270, cy + 45), radius=10, fill=WHITE + (255,))
    fill_w = 440 * k
    d.rounded_rectangle((cx - 218, cy - 118, cx - 218 + fill_w, cy + 118), radius=24, fill=mix(GREEN, ORANGE, k) + (255,))
    text_c(d, (cx, cy), f"{int(k * 100)}%", font(110), fill=WHITE, width=4)
    # bolt
    bx, by = cx, cy - 330
    s = 1.0 + 0.08 * math.sin(t * 8)
    d.polygon([(bx + 20 * s, by - 90 * s), (bx - 55 * s, by + 15 * s), (bx - 5 * s, by + 15 * s), (bx - 25 * s, by + 95 * s),
               (bx + 55 * s, by - 20 * s), (bx + 5 * s, by - 20 * s)], fill=GOLD + (255,))
    waves(d, cx, cy - 150, 380, t, heat, n=5)
    text_c(d, (cx, cy + 270), "TEZ CHARGER = ZYADA GARMI", font(50), fill=ORANGE, width=3)


def sc_tips(d, t, dur, tips):
    for i, s in enumerate(tips):
        k = ease((t - 0.6 - i * 1.1) / 0.5)
        y = 640 + i * 250
        x = lerp(1300, 540, k)
        d.rounded_rectangle((x - 450, y - 90, x + 450, y + 90), radius=36, fill=(18, 24, 50, 235), outline=GREEN + (255,), width=6)
        d.line([(x - 400, y), (x - 360, y + 38), (x - 285, y - 38)], fill=GREEN + (255,), width=14, joint="curve")
        d.text((x + 40, y), s, font=font(46), fill=WHITE + (255,), anchor="mm")


PAINTERS = {"thermo": sc_thermo, "chip": sc_chip, "bars": sc_bars, "battery": sc_battery}


def frame_fn(topic, idx, n, dur):
    """Returns make_frame(t) for scene idx."""
    kind = topic["scenes"][idx]
    cap = topic["caps"][idx]
    accent = GOLD

    def mk(t):
        im = background()
        d = ImageDraw.Draw(im, "RGBA")
        # top chips
        d.rounded_rectangle((44, 52, 44 + 330, 52 + 66), radius=33, fill=(10, 14, 32, 215), outline=accent + (255,), width=3)
        d.text((44 + 165, 52 + 33), topic["tag"], font=font(36), fill=WHITE + (255,), anchor="mm")
        # scene body
        if kind == "tips":
            sc_tips(d, t, dur, topic["tips"])
        else:
            PAINTERS[kind](d, t, dur)
        # caption (safe zone above platform buttons), fade-in + tiny rise
        a = ease(t / 0.35)
        yy = H - 520 - (1 - a) * 24
        for dx, dy in ((4, 4), (-3, 3), (3, -3)):
            d.text((W / 2 + dx, yy + dy), cap, font=font(70), fill=(0, 0, 0, int(255 * a)), anchor="mm")
        d.text((W / 2, yy), cap, font=font(70), fill=WHITE + (int(255 * a),), anchor="mm")
        d.rectangle((W / 2 - 130, yy + 62, W / 2 + 130, yy + 70), fill=accent + (int(255 * a),))
        # progress segments
        seg = (W - 160) / n
        for i in range(n):
            col = accent + (255,) if i <= idx else (255, 255, 255, 90)
            d.rounded_rectangle((80 + i * seg + 6, H - 330, 80 + (i + 1) * seg - 6, H - 320), radius=5, fill=col)
        d.text((W / 2, H - 270), "Synthetic AI voice | Educational", font=font(30), fill=(210, 218, 238, 255), anchor="mm")
        return np.array(im)

    return mk


def whoosh(dur_s=0.4, sr=44100):
    n = int(dur_s * sr)
    rnd = np.random.RandomState(7)
    noise = rnd.randn(n).astype(np.float32)
    # crude low-pass by moving average, sweep envelope
    k = 40
    noise = np.convolve(noise, np.ones(k) / k, mode="same")
    env = np.sin(np.linspace(0, math.pi, n)) ** 2
    out = noise * env
    out /= (np.abs(out).max() or 1.0)
    return (out * 0.35).astype(np.float32)


def build(key, out_dir):
    from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
    from moviepy.audio.AudioClip import AudioArrayClip
    from story_real import normalize_voice
    import story_motion as SM
    topic = TOPICS[key]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    n = len(topic["lines"])
    scenes = []
    for i, line in enumerate(topic["lines"]):
        ap = out_dir / f"{key}_{i}.mp3"
        # fast, energetic delivery; slightly lower pitch on the hook for weight
        rate, pitch = ("+26%", "+2Hz") if i == 0 else (("+20%", "+0Hz") if i < 4 else ("+18%", "+0Hz"))
        E.make_voice(line, ap, rate, pitch)
        voice = AudioFileClip(str(normalize_voice(ap)))
        dur = voice.duration + 0.35
        clip = VideoClip(frame_fn(topic, i, n, dur), duration=dur).set_fps(FPS)
        bed = SM.ambient(dur, mood="calm")
        rms = float(np.sqrt(np.mean(np.square(bed)))) or 1e-6
        bed = np.clip(bed * (0.02 / rms), -1, 1)
        bed = AudioArrayClip(np.stack([bed, bed], axis=1), fps=44100)
        w = whoosh()
        w = AudioArrayClip(np.stack([w, w], axis=1), fps=44100).set_start(0)
        clip = clip.set_audio(CompositeAudioClip([bed, w, voice.set_start(0.05)]).set_duration(dur))
        scenes.append(clip)
        print(f"[TECH:{key}] scene {i + 1}/{n} ok ({dur:.1f}s)")
    final = concatenate_videoclips(scenes, method="compose")
    mp4 = out_dir / f"{key}_tech.mp4"
    final.write_videofile(str(mp4), fps=FPS, codec="libx264", audio_codec="aac", preset="medium", logger=None)
    # thumbnail: hot-phone frame, big hook text
    thumb = out_dir / f"{key}_thumb.jpg"
    try:
        fr = Image.fromarray(frame_fn(topic, 0, n, 6.0)(5.0)).convert("RGB")
        crop = fr.crop((0, 380, W, 380 + int(W * 9 / 16))).resize((1280, 720))
        d = ImageDraw.Draw(crop, "RGBA")
        d.rectangle((0, 0, 1280, 720), fill=(0, 0, 0, 60))
        text_c(d, (640, 110), topic["thumb"], font(110), fill=GOLD, width=6)
        crop.save(thumb, quality=92)
    except Exception as e:
        print(f"[TECH] thumbnail skipped: {e}")
        thumb = None
    NL = chr(10)
    meta = {"title": topic["yt_title"], "tags": topic["tags"], "duration_s": round(final.duration, 1),
            "description": (topic["title"] + NL + NL + "Fixed analogy, simple Hindi. This is an educational explainer. The voice is a synthetic (AI) voice; "
                            "diagrams are simplified illustrations." + NL + NL + "#TechExplained #HowItWorks #Hindi")}
    (out_dir / f"{key}_meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[TECH:{key}] done: {mp4} ({meta['duration_s']}s)")
    return mp4, thumb, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", default=None)
    ap.add_argument("--out", default="output/tech")
    a = ap.parse_args()
    if a.sample:
        build(a.sample, a.out)
    else:
        print("usage: python tech_short.py --sample phone_heat")
