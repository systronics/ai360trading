"""
emotion_story.py v1.0 (2026-10-25) — cinematic "trader psychology" story Shorts (fear, greed, patience, FOMO, revenge).

WHY
  Real-data chart Shorts inform; stories hold attention. A viewer stays for a person they recognise (the 2 AM
  panic, the "just one more lot"), and the lesson lands because it is felt, not lectured. Each story is five
  scenes: cinematic 3D-render-style image (free FLUX: Cloudflare when keys exist, else Pollinations), slow
  camera move, short English caption on screen, Hindi (Devanagari) narration so the voice is pronounced right.

HONEST BY DESIGN
  * Characters are FICTIONAL and the description says so. No invented statistics. The one number used
    (patience story) is from our own 5-year backtest and is worded with its limit.
  * Brand voice: AI360Trading only — no personal name on screen or in the narration.
  * No entry/stop/target, no tips. Educational, AI-generated visuals disclosed in the description.
  * No emoji or Devanagari inside Pillow text (font coverage); captions are Latin only.

SAFETY
  * LOCAL SAMPLE ONLY today:  python emotion_story.py --sample fear      (output in _drafts_local/story_sample/)
    It never uploads and is not wired into any workflow; wiring is a separate owner-approved step.
  * Fail-open image layer: if every image source fails, a drawn fallback scene is used so a story always renders.
"""

import os
import sys
import json
import time
import asyncio
import urllib.parse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FPS = 24
VOICE = "hi-IN-MadhurNeural"
VOICE_RATE = "+12%"   # owner 2026-10-25: voice was too slow
VOICE_PITCH = "+8Hz"
OUT_DIR = Path("_drafts_local/story_sample")
FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
STYLE = ("Pixar-style 3D animated movie still, stylized CGI characters with big expressive eyes and smooth skin, "
         "soft cinematic lighting, rich vibrant colors, sharp focus, highly detailed, vertical composition, "
         "no text, no letters, no logos, no watermark")


def _font(size):
    for p in FONTS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


# ───────────────────────────── the stories ──────────────────────────────────
# narration = Devanagari (unambiguous for the hi-IN voice); brand written in Latin is converted by safe_tts_par.
# caption = short Latin on-screen line. prompt = scene description (character descriptor is prepended).

STORIES = {
    "fear": {
        "charts": ["down","down","down","up","flat"],
        "accent": (235, 70, 70),
        "tag": "FEAR",
        "title": "He Sold The Exact Bottom | A Trader's Story #shorts",
        "who": "an Indian man in his 30s with short black hair wearing a white shirt",
        "scenes": [
            ("रात के दो बजे थे। राजेश की आँखों में नींद नहीं थी। स्क्रीन पर बस लाल रंग।",
             "2 AM. EVERYTHING IS RED.",
             "sitting alone in a dark room at night, face lit by a glowing red falling stock chart on a monitor"),
            ("मार्केट गिरता गया, और उसका डर बढ़ता गया। उसने सोचा, अब और नहीं सह सकता।",
             "FEAR TAKES OVER",
             "close-up of a worried sweating face, trembling hand over a mouse, red light reflecting in his eyes"),
            ("उसने सब बेच दिया। ठीक उसी दिन, जब भाव सबसे नीचे था।",
             "HE SOLD THE BOTTOM",
             "pressing the sell button on a laptop, the screen shows a deep red chart touching its lowest point"),
            ("कुछ दिन बाद मार्केट वापस ऊपर चढ़ने लगा। और राजेश बस देखता रह गया।",
             "THEN IT RECOVERED",
             "standing by a window at dawn with his young daughter hugging his leg, a green rising chart glowing on a screen behind him, regretful look"),
            ("सबक यह है: डर में लिया गया फ़ैसला अक्सर सबसे महंगा होता है। स्टॉप लॉस पहले से तय करो। AI360Trading को फ़ॉलो करो।",
             "DECIDE BEFORE YOU PANIC",
             "calm man writing a plan in a notebook in morning sunlight while his wife serves tea, a steady chart on the monitor"),
        ],
        "desc": "Fear makes traders sell at the worst price. Decide your stop-loss before the trade, not during the panic.",
    },
    "greed": {
        "charts": ["up","upsteep","spike","down","flat"],
        "accent": (255, 200, 50),
        "tag": "GREED",
        "title": "'Just One More Lot' Cost Him Everything | A Trader's Story #shorts",
        "who": "an Indian man in his 30s with short black hair wearing a blue shirt",
        "scenes": [
            ("सुरेश का पहला ट्रेड बीस मिनट में हरा हो गया। उसे लगा, यह तो बहुत आसान है।",
             "FIRST WIN. TOO EASY.",
             "smiling at a monitor showing a small green profit, golden warm light, coffee on the desk"),
            ("उसने सोचा, थोड़ा और। उसने साइज़ दोगुना कर दिया। फिर चार गुना।",
             "JUST ONE MORE LOT",
             "eyes wide with excitement, two cheering colleagues behind him, golden coins and rising numbers floating around the desk"),
            ("फिर मार्केट पलटा। एक बड़ा लाल कैंडल, और सारा मुनाफ़ा गायब।",
             "THE MARKET TURNED",
             "a huge red candle crashing down on the monitor, the golden coins turning dark and falling"),
            ("सुरेश का महीनों का फ़ायदा, कुछ ही मिनटों में चला गया।",
             "MONTHS OF GAINS. GONE.",
             "head in hands at the desk, a dimly lit room, empty coffee cup, red glow on the wall"),
            ("सबक यह है: लालच में साइज़ बढ़ाना, अकाउंट ख़त्म करने का सबसे तेज़ रास्ता है। पहले से तय करो, कितना रिस्क लेना है। AI360Trading को फ़ॉलो करो।",
             "SIZE FIRST. PROFIT LATER.",
             "the same man calmly looking at a risk plan on a screen, balanced scale of green and red on the desk"),
        ],
        "desc": "Greed makes traders increase size after a win. Fix your risk per trade before you enter, not after.",
    },
    "patience": {
        "charts": ["flat","flat","break","break","up"],
        "accent": (0, 210, 100),
        "tag": "PATIENCE",
        "title": "He Waited 12 Days For One Trade | A Trader's Story #shorts",
        "who": "an Indian man in his 40s with short grey-black hair wearing a light green shirt",
        "scenes": [
            ("अनिल हर रोज़ चार्ट देखता था। लेकिन ट्रेड नहीं करता था। क्योंकि उसका सेटअप अभी पूरा नहीं हुआ था।",
             "HE JUST WATCHED",
             "sitting calmly at a desk with a cup of tea, a sideways-moving chart on the monitor, morning light"),
            ("बाकी लोग हर छोटी हलचल में कूद रहे थे। अनिल बस इंतज़ार करता रहा।",
             "OTHERS KEPT CHASING",
             "in the background blurred traders shouting and tapping phones, in the foreground Anil sits still and calm"),
            ("बारह दिन बाद, भाव अपने पचास दिन के ऊँचे स्तर के ऊपर बंद हुआ। यही उसका इशारा था।",
             "THE SIGNAL ARRIVED",
             "a green candle closing above a glowing horizontal line on the monitor, his eyes sharp and focused"),
            ("हमारे बैकटेस्ट में ऐसे ब्रेकआउट में सिर्फ़ करीब बयालीस प्रतिशत ट्रेड जीते। लेकिन जीतने वाले ट्रेड बड़े थे।",
             "ONLY 42% WON. WINNERS RAN.",
             "a rising green trendline glowing with golden light over a city skyline at sunrise, hopeful mood"),
            ("सबक यह है: सही मौके का इंतज़ार भी एक पोज़िशन है। यह कहानी है, सलाह नहीं। AI360Trading को फ़ॉलो करो।",
             "WAITING IS A POSITION",
             "peaceful man smiling slightly in front of a calm screen, golden sunrise through the window"),
        ],
        "desc": "Patience is part of the strategy. Backtest note: 50-day-high closing breakouts won about 42% of trades; "
                "winners were larger than losers (past results, not a promise).",
    },
    "fomo": {
        "charts": ["upsteep","upsteep","spike","flat","flat"],
        "accent": (255, 140, 0),
        "tag": "FOMO",
        "title": "He Bought At The Top (FOMO) | A Trader's Story #shorts",
        "who": "an Indian man in his 30s with short black hair wearing an orange shirt",
        "scenes": [
            ("विकास ने देखा कि एक शेयर आठ प्रतिशत उछल गया। सब उसी की बात कर रहे थे।",
             "EVERYONE IS TALKING ABOUT IT",
             "looking at a phone with a stock soaring on a green screen, notification bubbles glowing around"),
            ("उसे लगा, मैं पीछे रह गया। और उसने बिना सोचे ख़रीद लिया।",
             "FOMO HITS",
             "rushing to the laptop, hand slamming the buy button, intense orange light on his face"),
            ("ख़रीदते ही भाव पलट गया। जो ऊपर गया था, वह वापस नीचे आने लगा।",
             "BOUGHT THE TOP",
             "the chart on the monitor curving down sharply right after a peak, his expression freezing in shock"),
            ("मौका निकल गया था, पर बाज़ार में मौके रोज़ आते हैं।",
             "THERE IS ALWAYS ANOTHER SETUP",
             "calmer evening scene, the man closing his laptop and looking out at city lights, thoughtful"),
            ("सबक यह है: पीछा करने से बेहतर है, अगले सेटअप का इंतज़ार करना। AI360Trading को फ़ॉलो करो।",
             "DON'T CHASE. WAIT.",
             "man calmly marking a level on a chart in a notebook, a green line on the screen, soft light"),
        ],
        "desc": "FOMO makes traders buy after the move. A missed move is cheaper than a chased one.",
    },
    "revenge": {
        "charts": ["down","down","down","down","flat"],
        "accent": (200, 60, 255),
        "tag": "REVENGE",
        "title": "He Tried To Win It Back | Revenge Trading Story #shorts",
        "who": "an Indian man in his 30s with short black hair wearing a dark grey shirt",
        "scenes": [
            ("मोहित का एक ट्रेड स्टॉप लॉस पर लग गया। छोटा सा नुकसान था। पर उसे चुभ गया।",
             "ONE SMALL LOSS",
             "staring at a monitor showing a stop-loss hit marker in red, jaw tight, dark moody room"),
            ("उसने सोचा, अभी वापस कमाता हूँ। बिना सेटअप के उसने तुरंत दूसरा ट्रेड ले लिया।",
             "I'LL WIN IT BACK",
             "angrily typing an order on the keyboard, purple and red lights flickering on his face"),
            ("दूसरा ट्रेड भी हारा। फिर उसने साइज़ बढ़ाकर तीसरा लिया।",
             "BIGGER SIZE. SAME ANGER.",
             "a pile of crumpled papers on the desk, the monitor showing a larger red loss, sweat on his forehead"),
            ("एक छोटा नुकसान, एक बड़ा नुकसान बन गया।",
             "SMALL LOSS BECAME BIG",
             "overhead view of the man slumped over the desk, the room cold and dark, red numbers glowing"),
            ("सबक यह है: नुकसान के बाद ब्रेक लो। अगला ट्रेड तभी लो जब सेटअप पूरा हो। AI360Trading को फ़ॉलो करो।",
             "TAKE A BREAK AFTER A LOSS",
             "the man stepping outside for fresh air at sunset, calm expression, phone left on the desk"),
        ],
        "desc": "Revenge trading turns a small loss into a big one. After a loss, pause; trade only complete setups.",
    },
}


# ───────────────────────────── images ───────────────────────────────────────

def _cf_image(prompt, seed):
    acct, tok = os.environ.get("CLOUDFLARE_ACCOUNT_ID", ""), os.environ.get("CLOUDFLARE_API_TOKEN", "")
    if not (acct and tok):
        return None
    import requests, base64
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    for body in ({"prompt": prompt[:2048], "steps": 8, "seed": seed}, {"prompt": prompt[:2048], "steps": 8}):
        try:
            r = requests.post(url, headers={"Authorization": f"Bearer {tok}"}, json=body, timeout=90)
            if r.status_code == 200:
                b64 = ((r.json().get("result") or {}).get("image", "")) or ""
                if b64:
                    return base64.b64decode(b64)
            print(f"  [IMG] Cloudflare {r.status_code}: {r.text[:120]}")
        except Exception as e:
            print(f"  [IMG] Cloudflare error: {str(e)[:80]}")
    return None


def _poll_image(prompt, seed, w=768, h=1344):
    import requests
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
           + f"?model=flux&width={w}&height={h}&nologo=true&seed={seed}")
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("image") and len(r.content) > 5000:
                return r.content
        except Exception as e:
            print(f"  [IMG] Pollinations try {attempt + 1}: {str(e)[:60]}")
        time.sleep(6 * (attempt + 1))
    return None


def _fallback_scene(accent, idx):
    """Drawn scene if no image service answers: dark gradient + glowing chart line."""
    img = Image.new("RGB", (768, 1344))
    px = np.zeros((1344, 768, 3), dtype=np.uint8)
    for y in range(1344):
        t = y / 1344
        px[y, :] = (int(8 + 14 * t), int(10 + 18 * t), int(26 + 40 * t))
    img = Image.fromarray(px)
    d = ImageDraw.Draw(img)
    rng = np.random.RandomState(idx + 3)
    ys = np.cumsum(rng.randn(40)) * 30
    ys = (ys - ys.min()) / max(1, np.ptp(ys)) * 500 + 400
    pts = [(int(i * 768 / 39), int(1344 - v - 200)) for i, v in enumerate(ys)]
    d.line(pts, fill=accent, width=8)
    return img.filter(ImageFilter.GaussianBlur(1.2))


def get_scene_image(story_key, idx, who, scene_prompt, accent, cache_dir):
    cache = cache_dir / f"{story_key}_{idx}.jpg"
    if cache.exists() and cache.stat().st_size > 5000:
        return Image.open(cache).convert("RGB")
    prompt = f"{STYLE}. {who}, {scene_prompt}"
    seed = 100 + sum(ord(c) for c in story_key)  # same seed per story = consistent look across scenes
    data = _cf_image(prompt, seed) or _poll_image(prompt, seed)
    if not data:  # second chance with a shorter prompt (long prompts are the usual failure)
        data = _poll_image(f"3D render, cinematic, {who}, {scene_prompt.split(',')[0]}, no text", seed + 1)
    if data:
        cache.write_bytes(data)
        return Image.open(cache).convert("RGB")
    print(f"  [IMG] scene {idx}: no image service answered, using drawn fallback")
    return _fallback_scene(accent, idx)


# ───────────────────────────── audio ────────────────────────────────────────

def make_voice(text, path):
    import edge_tts
    from human_touch import safe_tts_par

    async def go():
        last = None
        for attempt in range(3):
            try:
                await edge_tts.Communicate(safe_tts_par(text), VOICE, rate=VOICE_RATE, pitch=VOICE_PITCH).save(str(path))
                if path.exists() and path.stat().st_size > 1000:
                    return
            except Exception as e:
                last = e
                await asyncio.sleep(2 * (attempt + 1))
        raise RuntimeError(f"TTS failed: {last}")

    asyncio.run(go())


# ───────────────────────────── frames ───────────────────────────────────────

def _compose_square(img):
    """Square image -> 9:16 frame: blurred, darkened copy as background, sharp image full-width in the middle."""
    bg = img.resize((W, W), Image.LANCZOS)
    scale = H / W
    bgf = img.resize((int(img.width * scale) + 1, H), Image.LANCZOS)
    left = (bgf.width - W) // 2
    bgf = bgf.crop((left, 0, left + W, H)).filter(ImageFilter.GaussianBlur(28))
    bgf = Image.eval(bgf, lambda v: int(v * 0.45))
    bgf.paste(bg, (0, 150))
    return bgf


def _cover(img, pad=1.0):
    """Crop the bottom (service watermark), scale to cover the 1080x1920 frame (times pad)."""
    w, h = img.size
    if 0.85 <= w / h <= 1.18:
        img = _compose_square(img)
    else:
        img = img.crop((0, 0, w, int(h * 0.93)))   # trims the free service's corner watermark
    w, h = img.size
    s = max(W / w, H / h) * pad
    return img.resize((int(w * s) + 1, int(h * s) + 1), Image.LANCZOS)


def _wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def _static_overlay(accent, tag, caption, idx, n):
    """Gradient shade, brand chip, emotion tag, caption block, progress dots. Returns (rgb, alpha) arrays."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(H):  # bottom shade + top shade
        a_bot = max(0.0, (y - H * 0.55) / (H * 0.45)) ** 1.4 * 235
        a_top = max(0.0, (H * 0.16 - y) / (H * 0.16)) * 150
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(min(235, a_bot + a_top))))
    f_b = _font(40)
    d.rounded_rectangle((44, 52, 44 + 330, 52 + 66), radius=33, fill=(10, 14, 32, 215), outline=accent, width=3)
    d.text((44 + 165, 52 + 33), "AI360TRADING", font=f_b, fill=(255, 255, 255, 255), anchor="mm")
    f_t = _font(46)
    tw = d.textlength(tag, font=f_t) + 56
    d.rounded_rectangle((W - 44 - tw, 52, W - 44, 118), radius=33, fill=accent + (235,))
    d.text((W - 44 - tw / 2, 85), tag, font=f_t, fill=(10, 10, 20, 255), anchor="mm")
    f_c = _font(84)
    lines = _wrap(d, caption, f_c, W - 130)
    y = H - 330 - 96 * len(lines)
    for ln in lines:
        for dx, dy in ((4, 4), (-3, 3), (3, -3)):
            d.text((W / 2 + dx, y + dy), ln, font=f_c, fill=(0, 0, 0, 255), anchor="mm")
        d.text((W / 2, y), ln, font=f_c, fill=(255, 255, 255, 255), anchor="mm")
        y += 96
    d.rectangle((W / 2 - 150, y + 4, W / 2 + 150, y + 12), fill=accent + (255,))
    f_s = _font(34)
    d.text((W / 2, H - 120), "Fictional story | AI visuals | Educational, not advice", font=f_s,
           fill=(215, 222, 240, 255), anchor="mm")
    seg = (W - 160) / n
    for i in range(n):
        col = accent + (255,) if i <= idx else (255, 255, 255, 90)
        d.rounded_rectangle((80 + i * seg + 6, H - 60, 80 + (i + 1) * seg - 6, H - 50), radius=5, fill=col)
    arr = np.array(ov)
    return arr[..., :3].astype(np.float32), arr[..., 3:].astype(np.float32) / 255.0


def _chart_points(kind, idx, n=64):
    """Deterministic price-like path in 0..1 (0 = low, 1 = high) for the on-screen mini chart."""
    rng = np.random.RandomState(40 + idx)
    x = np.linspace(0, 1, n)
    noise = np.cumsum(rng.randn(n)) * 0.018
    shape = {
        "down": 0.9 - 0.8 * x, "up": 0.15 + 0.75 * x, "upsteep": 0.1 + 0.85 * x ** 2.2,
        "flat": 0.5 + 0.04 * np.sin(x * 14), "spike": np.where(x < 0.62, 0.2 + 0.75 * (x / 0.62) ** 1.6, 0.95 - 0.8 * ((x - 0.62) / 0.38)),
        "break": np.where(x < 0.7, 0.45 + 0.05 * np.sin(x * 16), 0.45 + 0.5 * ((x - 0.7) / 0.3) ** 1.3),
    }[kind]
    if kind == "flat":
        return np.clip(0.5 + 0.05 * np.sin(x * 14) + noise * 0.25, 0.3, 0.7)
    y = shape + noise * (0.4 if kind == "break" else 1.0)
    y = (y - y.min()) / max(1e-6, np.ptp(y))
    return y


def _draw_chart(frame, pts, progress, accent, rising):
    """Glowing line chart that draws itself inside a translucent panel (above the caption)."""
    x0, x1, y0, y1 = 90, W - 90, 1010, 1290
    im = Image.fromarray(frame).convert("RGBA")
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 - 24, y0 - 24, x1 + 24, y1 + 24), radius=26, fill=(8, 12, 28, 150), outline=accent + (140,), width=2)
    for g in range(1, 4):
        gy = y0 + (y1 - y0) * g / 4
        d.line([(x0, gy), (x1, gy)], fill=(255, 255, 255, 28), width=1)
    k = max(2, int(len(pts) * min(1.0, progress)))
    xy = [(x0 + (x1 - x0) * i / (len(pts) - 1), y1 - (y1 - y0) * float(pts[i])) for i in range(k)]
    col = (0, 210, 100) if rising else (235, 70, 70)
    d.line(xy, fill=col + (255,), width=9, joint="curve")
    ex, ey = xy[-1]
    d.ellipse((ex - 14, ey - 14, ex + 14, ey + 14), fill=(255, 255, 255, 255), outline=col + (255,), width=5)
    return np.array(Image.alpha_composite(im, lay).convert("RGB"))


def _scene_clip(img, overlay, dur, idx, chart=None, accent=(255, 255, 255)):
    from moviepy.editor import VideoClip
    base = _cover(img, 1.0)
    bw, bh = base.size
    rgb, alpha = overlay
    cpts = _chart_points(chart, idx) if chart else None
    rising = bool(cpts is not None and cpts[-1] >= cpts[0])
    # alternate camera moves: push-in, pull-out, pan left, pan right, push-in
    mode = idx % 4

    def make(t):
        p = t / max(dur, 0.1)
        z = 1.0 + 0.12 * (p if mode in (0, 2) else (1 - p))
        cw, ch = W / z, H / z
        if mode == 2:
            cx = (bw - cw) * p
        elif mode == 3:
            cx = (bw - cw) * (1 - p)
        else:
            cx = (bw - cw) / 2
        cy = (bh - ch) / 2
        fr = base.crop((int(cx), int(cy), int(cx + cw), int(cy + ch))).resize((W, H), Image.BILINEAR)
        a = np.array(fr, dtype=np.float32)
        fade = min(1.0, t / 0.35)
        a = a * (1 - alpha) + rgb * alpha
        a *= min(1.0, 0.55 + 0.45 * fade) if t < 0.35 else 1.0
        out = a.clip(0, 255).astype(np.uint8)
        if cpts is not None:
            out = _draw_chart(out, cpts, min(1.0, t / max(dur * 0.85, 0.1)), accent, rising)
        return out

    return VideoClip(make, duration=dur).set_fps(FPS)


def build_thumbnail(story_key, img, path):
    st = STORIES[story_key]
    base = _cover(img, 1.0).crop((0, 0, W, H))
    th = base.resize((720, 1280), Image.LANCZOS).convert("RGB")
    d = ImageDraw.Draw(th, "RGBA")
    for y in range(640, 1280):
        d.line([(0, y), (720, y)], fill=(0, 0, 0, int(min(215, (y - 640) / 640 * 260))))
    f = _font(150)
    d.text((360, 900), st["tag"], font=f, fill=st["accent"], anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
    f2 = _font(62)
    d.text((360, 1040), "A TRADER'S STORY", font=f2, fill=(255, 255, 255), anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
    d.text((360, 1210), "AI360TRADING", font=_font(44), fill=(255, 255, 255, 230), anchor="mm")
    th.save(path, quality=90)


def build_story(story_key, out_dir=OUT_DIR):
    from moviepy.editor import AudioFileClip, concatenate_videoclips, concatenate_audioclips
    st = STORIES[story_key]
    out_dir.mkdir(parents=True, exist_ok=True)
    clips, auds, first_img = [], [], None
    n = len(st["scenes"])
    for i, (narr, cap, prompt) in enumerate(st["scenes"]):
        print(f"[STORY:{story_key}] scene {i + 1}/{n}")
        img = get_scene_image(story_key, i, st["who"], prompt, st["accent"], out_dir)
        first_img = first_img or img
        ap = out_dir / f"{story_key}_{i}.mp3"
        make_voice(narr, ap)
        a = AudioFileClip(str(ap))
        dur = a.duration + 0.5
        clips.append(_scene_clip(img, _static_overlay(st["accent"], st["tag"], cap, i, n), dur, i, st["charts"][i], st["accent"]))
        auds.append(a)
    video = concatenate_videoclips(clips, method="compose")
    audio = concatenate_audioclips([x for pair in zip(auds, [None] * n) for x in pair[:1]])
    # keep audio aligned: pad each scene's tail silence by building per-scene composite
    from moviepy.audio.AudioClip import AudioClip
    padded = []
    for a in auds:
        sil = AudioClip(lambda t: np.zeros((np.size(t), 2)), duration=0.5, fps=44100)
        padded += [a, sil]
    audio = concatenate_audioclips(padded)
    video = video.set_audio(audio)
    mp4 = out_dir / f"{story_key}_story.mp4"
    video.write_videofile(str(mp4), fps=FPS, codec="libx264", audio_codec="aac", preset="medium", logger=None)
    build_thumbnail(story_key, first_img, out_dir / f"{story_key}_thumb.jpg")
    meta = {"title": st["title"], "description": st["desc"] + "\n\nThis is a fictional illustrative story. Visuals are "
            "AI-generated. Educational content, not investment advice.\n\n#tradingpsychology #stockmarketindia "
            "#ai360trading", "duration_s": round(video.duration, 1)}
    (out_dir / f"{story_key}_meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[STORY:{story_key}] done: {mp4} ({meta['duration_s']}s)")
    return mp4


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--sample":
        build_story(sys.argv[2])
    else:
        print("usage: python emotion_story.py --sample <" + "|".join(STORIES) + ">  (local sample only, never uploads)")
