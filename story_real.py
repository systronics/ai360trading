"""
story_real.py v1.0 (2026-10-29) — REALISTIC story Shorts built from real stock footage (Pexels), not AI video.

WHY
  Owner 2026-10-29: "realistic, 3D like a real video, must not look AI". Free image/video AI (FLUX + Wan) looks AI
  (changing faces, plastic skin). Real licensed footage (Pexels, free, no attribution needed) looks real. So:
  real portrait footage per scene + English narration (worldwide audience) + captions + the same story/emotion
  structure as emotion_story.py.

WHAT IS REAL AND WHAT IS NOT (disclosed in the description)
  * Footage: real stock video from Pexels (queries lean on hands, screens, silhouettes, city — NOT on a named person,
    because Pexels' licence forbids showing an identifiable person in a bad light and our stories are about losses).
  * Narration: synthetic voice (edge-tts) — said so in the description.
  * Story: fictional and illustrative — said so on screen and in the description.

SAFETY (never-break doctrine)
  * Fail-open: any failure (no key, no footage, TTS down) = nothing published + a Telegram note, exit 0.
  * No digits in narration or captions (owner: evergreen, no numbers). A story with a digit is refused.
  * No entry / stop / target, no stock names; educational wording only (SEBI-safe: not a recommendation).
  * Shares _data/stories_done.json and the upload path with emotion_story.py, so a story is never published twice.

Usage:  python story_real.py --run --mode dry|private-test|scheduled [--out output/story] [--story fear] [--cache bank_real]
"""
import os
import re
import sys
import json
import asyncio
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import emotion_story as E

if not hasattr(Image, "ANTIALIAS"):          # moviepy 1.0.3 still calls the old Pillow name (same shim as generate_reel.py)
    Image.ANTIALIAS = Image.LANCZOS

W, H = E.W, E.H
FPS = 24
VOICES_EN = ["en-US-AndrewNeural", "en-US-GuyNeural", "en-IN-PrabhatNeural"]
EN_PROFILES = [("+2%", "+0Hz"), ("+6%", "+4Hz"), ("+8%", "+6Hz"), ("-2%", "-4Hz"), ("+0%", "+0Hz")]

# English narration (no names: real footage shows different people, so a name would not match the screen).
EN = {
    "fear": [
        "It was the middle of the night. He couldn't sleep. The screen was nothing but red.",
        "The market kept falling, and so did his nerve. He thought, I can't take any more.",
        "He sold everything. On the exact day the price hit its lowest point.",
        "A few days later, the market started climbing again. And he could only watch.",
        "The lesson: a decision made in fear is often the most expensive one. Decide your stop-loss before you trade. Follow AI360Trading.",
    ],
    "greed": [
        "His first trade turned green in minutes. He thought, this is easy.",
        "He thought, a little more. He doubled his size. Then doubled it again.",
        "Then the market turned. One big red candle, and all the profit vanished.",
        "Months of gains, gone in a few minutes.",
        "The lesson: raising your size out of greed is the fastest way to wipe out an account. Decide your risk in advance. Follow AI360Trading.",
    ],
    "patience": [
        "Every day he watched the chart. But he didn't trade. His setup wasn't complete yet.",
        "Everyone else jumped at every small move. He just kept waiting.",
        "Days later, the price closed above its previous high. That was his signal.",
        "In our backtest, fewer than half of such breakouts won. But the winners were bigger than the losers.",
        "The lesson: waiting for the right setup is also a position. This is a story, not advice. Follow AI360Trading.",
    ],
    "fomo": [
        "He saw a stock jump sharply. Everyone was talking about it.",
        "He felt left behind. And he bought without thinking.",
        "The moment he bought, the price reversed. What had gone up started coming back down.",
        "The chance was gone. But the market offers new chances every day.",
        "The lesson: waiting for the next setup beats chasing. Follow AI360Trading.",
    ],
    "revenge": [
        "One of his trades hit its stop-loss. A small loss. But it stung.",
        "He thought, I'll earn it right back. With no setup, he took another trade immediately.",
        "That one lost too. Then he raised his size and took a third.",
        "One small loss became a big loss.",
        "The lesson: take a break after a loss. Take the next trade only when the setup is complete. Follow AI360Trading.",
    ],
    "averaging": [
        "He bought a stock. The price dipped a little. He thought, it's cheaper now.",
        "He bought more. The price fell further. He bought more again.",
        "Now his loss was big. But he refused to admit he had made a mistake.",
        "In the end he had to sell, with a far bigger loss than before.",
        "The lesson: adding money to a loss only digs the hole deeper. Set your stop-loss in advance. Follow AI360Trading.",
    ],
    "tip": [
        "A message in a group said: this stock will double tomorrow, buy now.",
        "He didn't think. No plan, no stop-loss. He put in all his money.",
        "The stock rose a little. Then suddenly reversed. In the group, nobody was saying anything.",
        "The tip-giver lost nothing. Only he took the loss.",
        "The lesson: never take a tip without your own plan. Your setup, your stop-loss. Follow AI360Trading.",
    ],
    "overtrade": [
        "He hated sitting idle. He felt that if he didn't trade, the chance was gone.",
        "From morning to evening, one trade after another. Some lasted minutes, some less.",
        "Each trade made a little or lost a little. But brokerage was cut every single time.",
        "In the evening he checked the results. The market had been fine, but his account was down.",
        "The lesson: more trades don't mean more profit. Choose fewer, better setups. Follow AI360Trading.",
    ],
    "nostop": [
        "He always said, I don't need a stop-loss. I trust myself.",
        "A few trades even worked that way. The price came back. His confidence grew.",
        "Then one day bad news arrived. The stock opened far below the previous close.",
        "There was no stop. So the loss kept growing until he finally stopped it himself.",
        "The lesson: a stop-loss is the price of staying in the game. Place it in advance. Follow AI360Trading.",
    ],
    "leverage": [
        "He learned that margin let him take a trade many times bigger than his capital.",
        "He used the full margin. Even small moves made his account swing up and down.",
        "Then the market moved just slightly against him. And a warning appeared on his account.",
        "The broker closed his position automatically. One small move wiped out most of his capital.",
        "The lesson: keep your size small enough to survive one wrong trade. If you survive, there is a next chance. Follow AI360Trading.",
    ],
}

# Pexels search per scene (portrait). Prefer hands / screens / silhouettes / city over faces (licence + realism).
QUERIES = {
    "fear": ["man silhouette alone dark room night laptop glow", "hand trembling over computer mouse red screen",
             "finger pressing laptop keyboard", "sunrise through window city morning", "hand writing in notebook morning coffee"],
    "greed": ["green stock chart rising on screen", "stack of money cash close up", "hands typing on laptop trading",
              "red candlestick chart falling on screen", "empty office desk laptop night"],
    "patience": ["person sitting calmly at laptop morning coffee", "stock chart on screen sideways",
                 "crowd walking fast city street blur", "green candlestick chart breakout screen", "sunrise city skyline calm"],
    "fomo": ["stock market screen green candles", "phone notifications messages scrolling", "finger tapping smartphone screen",
             "stock chart red falling on screen", "city traffic night lights"],
    "revenge": ["stock chart red screen", "hand tapping keyboard fast frustrated", "laptop screens at night red light",
                "stock chart steep fall red", "person walking outdoors park fresh air"],
    "averaging": ["stock price board numbers red", "shopping price tag sale discount", "hands counting money worried",
                  "stock ticker board falling red", "notebook planning desk morning light"],
    "tip": ["phone group chat messages scrolling", "finger tapping smartphone screen night", "stock chart reversing red screen",
            "phone screen dark empty chat", "notebook and pen plan on desk"],
    "overtrade": ["person bored waiting at desk", "multiple trading screens charts", "calculator and receipts bills",
                  "evening city skyline desk lamp", "tidy desk single monitor calm"],
    "nostop": ["confident businessman walking office", "stock chart rising on screen green", "breaking news on television screen",
               "stock chart gap down red screen", "red stop sign on road"],
    "leverage": ["trading terminal many screens", "hands clicking mouse trading screen", "stock chart dropping red warning",
                 "red alert warning light screen", "hands writing risk plan notebook calm"],
}

EN_SEO = {
    "fear": ("why traders sell at the bottom", "TradingPsychology"), "greed": ("greed in trading", "GreedInTrading"),
    "patience": ("patience in trading", "PatienceInTrading"), "fomo": ("fomo in trading", "FOMO"),
    "revenge": ("revenge trading", "RevengeTrading"), "averaging": ("averaging down in stocks", "AveragingDown"),
    "tip": ("why stock tips fail", "StockTips"), "overtrade": ("overtrading in trading", "Overtrading"),
    "nostop": ("why stop loss is important", "StopLoss"), "leverage": ("margin trading risk", "MarginTrading"),
}


# ───────────────────────────── voice ──────────────────────────────────────────

def make_voice_en(text, path, rate, pitch):
    import edge_tts

    async def go():
        last = None
        for voice in VOICES_EN:
            for attempt in range(2):
                try:
                    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(str(path))
                    if path.exists() and path.stat().st_size > 1000:
                        return
                except Exception as e:
                    last = e
                    await asyncio.sleep(2)
        raise RuntimeError(f"TTS failed: {last}")

    asyncio.run(go())


# ───────────────────────────── footage (Pexels) ───────────────────────────────

def _pexels_search(query, key, per_page=15):
    import requests
    r = requests.get("https://api.pexels.com/videos/search", headers={"Authorization": key},
                     params={"query": query, "orientation": "portrait", "size": "medium", "per_page": per_page}, timeout=30)
    r.raise_for_status()
    return r.json().get("videos", [])


def _best_file(video):
    files = [f for f in video.get("video_files", [])
             if f.get("file_type") == "video/mp4" and f.get("height", 0) >= f.get("width", 0) and f.get("width", 0) >= 540]
    if not files:
        return None
    hd = [f for f in files if f["height"] >= 1280]
    pool = hd or files
    return sorted(pool, key=lambda f: abs(f["height"] - 1920))[0]


def get_footage(query, key, cache_dir, used, need_seconds, tries=3):
    """Download up to `tries` distinct clips for a query until they cover need_seconds. Returns [Path]."""
    import requests
    out, total = [], 0.0
    for v in _pexels_search(query, key):
        if v["id"] in used or v.get("duration", 0) < 3:
            continue
        f = _best_file(v)
        if not f:
            continue
        p = Path(cache_dir) / f"{v['id']}.mp4"
        if not (p.exists() and p.stat().st_size > 50000):
            with requests.get(f["link"], stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(p, "wb") as fh:
                    for chunk in r.iter_content(1 << 20):
                        fh.write(chunk)
        used.add(v["id"])
        out.append(p)
        total += min(6.0, float(v.get("duration", 4)))
        if total >= need_seconds or len(out) >= tries:
            break
    return out


# ───────────────────────────── frames ─────────────────────────────────────────

def overlay(accent, tag, caption, idx, n):
    """Bottom shade, brand chip, tag chip, caption in the safe zone (above the platform buttons), progress segments."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(H):
        a_bot = max(0.0, (y - H * 0.50) / (H * 0.50)) ** 1.5 * 215
        a_top = max(0.0, (H * 0.14 - y) / (H * 0.14)) * 120
        d.line([(0, y), (W, y)], fill=(0, 0, 0, int(min(215, a_bot + a_top))))
    f_b = E._font(40)
    d.rounded_rectangle((44, 52, 44 + 330, 52 + 66), radius=33, fill=(10, 14, 32, 205), outline=accent, width=3)
    d.text((44 + 165, 52 + 33), "AI360TRADING", font=f_b, fill=(255, 255, 255, 255), anchor="mm")
    f_t = E._font(46)
    tw = d.textlength(tag, font=f_t) + 56
    d.rounded_rectangle((W - 44 - tw, 52, W - 44, 118), radius=33, fill=accent + (230,))
    d.text((W - 44 - tw / 2, 85), tag, font=f_t, fill=(10, 10, 20, 255), anchor="mm")
    f_c = E._font(78)
    lines = E._wrap(d, caption, f_c, W - 140)
    y = H - 600 - 90 * len(lines)
    for ln in lines:
        for dx, dy in ((4, 4), (-3, 3), (3, -3)):
            d.text((W / 2 + dx, y + dy), ln, font=f_c, fill=(0, 0, 0, 255), anchor="mm")
        d.text((W / 2, y), ln, font=f_c, fill=(255, 255, 255, 255), anchor="mm")
        y += 90
    d.rectangle((W / 2 - 140, y + 2, W / 2 + 140, y + 10), fill=accent + (255,))
    d.text((W / 2, H - 360), "Fictional story | Stock footage | Educational, not advice", font=E._font(32),
           fill=(225, 230, 245, 255), anchor="mm")
    seg = (W - 160) / n
    for i in range(n):
        col = accent + (255,) if i <= idx else (255, 255, 255, 90)
        d.rounded_rectangle((80 + i * seg + 6, H - 330 + 36, 80 + (i + 1) * seg - 6, H - 330 + 46), radius=5, fill=col)
    arr = np.array(ov)
    return arr[..., :3].astype(np.uint8), (arr[..., 3].astype(np.float32) / 255.0)


def scene_video(paths, dur, overlay_rgb, overlay_alpha):
    """Cover-crop footage to 1080x1920, join clips to length, gentle push-in, then the caption overlay."""
    from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip
    import moviepy.video.fx.all as vfx
    parts = []
    for p in paths:
        c = VideoFileClip(str(p), audio=False)
        c = c.subclip(0, min(c.duration, 6.0))
        s = max(W / c.w, H / c.h)
        parts.append(c.resize(s))
    base = parts[0] if len(parts) == 1 else concatenate_videoclips(parts, method="compose")
    if base.duration < dur:
        base = vfx.loop(base, duration=dur) if base.duration >= 2.5 else base.fx(vfx.speedx, final_duration=dur)
    base = base.subclip(0, dur)
    zoom = base.resize(lambda t: 1.0 + 0.045 * t / max(dur, 0.1)).set_position("center")
    ov = ImageClip(overlay_rgb).set_duration(dur)
    ov = ov.set_mask(ImageClip(overlay_alpha, ismask=True).set_duration(dur))
    return CompositeVideoClip([zoom, ov], size=(W, H)).set_duration(dur).set_fps(FPS)


def ambient_bed(dur, sr=44100):
    from story_motion import ambient
    return ambient(dur, sr=sr, mood="tense")


# ───────────────────────────── build ──────────────────────────────────────────

def check_story(key):
    texts = list(EN[key]) + [c for _, c, _ in E.STORIES[key]["scenes"]] + [E.THUMB_TEXT.get(key, ""), E.STORIES[key]["title"].split(" | ")[0]]
    for t in texts:
        if re.search(r"\d", re.sub(r"AI360Trading", "", t, flags=re.I)):
            raise ValueError(f"digit in story '{key}': {t!r} (evergreen rule: no numbers)")
    if len(EN[key]) != len(E.STORIES[key]["scenes"]) or len(QUERIES[key]) != len(EN[key]):
        raise ValueError("scene count mismatch")


def build(key, out_dir, cache_dir):
    from moviepy.editor import AudioFileClip, concatenate_videoclips, CompositeAudioClip
    from moviepy.audio.AudioClip import AudioArrayClip
    key_env = os.environ.get("PEXELS_API_KEY", "")
    if not key_env:
        raise RuntimeError("PEXELS_API_KEY missing")
    check_story(key)
    out_dir, cache_dir = Path(out_dir), Path(cache_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    st = E.STORIES[key]
    n = len(EN[key])
    used, scenes, frame_for_thumb = set(), [], None
    for i in range(n):
        narr = EN[key][i]
        cap = st["scenes"][i][1]
        rate, pitch = EN_PROFILES[i]
        ap = out_dir / f"{key}_{i}.mp3"
        make_voice_en(narr, ap, rate, pitch)
        voice = AudioFileClip(str(ap))
        dur = voice.duration + 0.5
        paths = get_footage(QUERIES[key][i], key_env, cache_dir, used, dur)
        if not paths:
            raise RuntimeError(f"no footage for scene {i + 1}: {QUERIES[key][i]!r}")
        rgb, alpha = overlay(st["accent"], st["tag"], cap, i, n)
        sc = scene_video(paths, dur, rgb, alpha)
        if i == 1 or frame_for_thumb is None:
            frame_for_thumb = Image.fromarray(sc.get_frame(min(1.0, dur - 0.1))).convert("RGB")
        bed = ambient_bed(dur)
        bed = AudioArrayClip(np.stack([bed, bed], axis=1), fps=44100)
        sc = sc.set_audio(CompositeAudioClip([bed, voice.set_start(0)]).set_duration(dur))
        scenes.append(sc)
        print(f"[REAL:{key}] scene {i + 1}/{n} ok ({dur:.1f}s, {len(paths)} clip(s))")
    final = concatenate_videoclips(scenes, method="compose")
    mp4 = out_dir / f"{key}_story.mp4"
    final.write_videofile(str(mp4), fps=FPS, codec="libx264", audio_codec="aac", preset="medium", logger=None)
    thumb = out_dir / f"{key}_thumb.jpg"
    E.build_thumbnail(key, frame_for_thumb, thumb, face=None)
    meta = make_meta(key, final.duration)
    (out_dir / f"{key}_meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[REAL:{key}] done: {mp4} ({meta['duration_s']}s)")
    return mp4, thumb, meta


def make_meta(key, duration):
    st = E.STORIES[key]
    phrase, tag = EN_SEO.get(key, ("trading psychology", "TradingPsychology"))
    hook = st["title"].split(" | ")[0]
    title = f"{hook} | {phrase.title()} #shorts"
    if len(title) > 100:
        title = f"{hook} #shorts"[:100]
    NL = chr(10)
    desc = (phrase.capitalize() + ": " + st["desc"] + NL + NL +
            "This is a fictional, illustrative story. Footage: stock video from Pexels. The narration is a synthetic (AI) voice. "
            "Educational content only, not investment advice or a recommendation to buy or sell anything. "
            "AI360Trading is not SEBI registered." + NL + NL +
            "More free lessons: https://ai360trading.in/tutorial-videos/" + NL + NL +
            f"#{tag} #Trading #StockMarket #TradingPsychology #AI360Trading")
    tags = [phrase, "trading psychology", "stock market", "trader story", "trading mistakes", tag.lower(), "AI360Trading", "shorts"]
    return {"title": title, "description": desc, "tags": tags, "duration_s": round(duration, 1)}


def run(mode, out_dir, cache_dir, story=None):
    """Never raises; always returns 0."""
    try:
        done = E._load_done()
        used = {x.get("story") for x in done}
        key = story or next((k for k in E.STORY_ORDER if k in EN and k not in used), None)
        if not key:
            E._tg("AI360 story Shorts (real footage): the story queue is EMPTY. Ask Claude to add more stories.")
            print("[REAL] queue empty")
            return 0
        print(f"[REAL] story = {key} (mode={mode})")
        mp4, thumb, meta = build(key, out_dir, cache_dir)
        if meta["duration_s"] > 59.0:
            E._tg(f"AI360 story Shorts (real footage): '{key}' is {meta['duration_s']}s (over 59s), NOT uploaded.")
            return 0
        if mode == "dry":
            print(f"[REAL] DRY RUN, nothing uploaded: {meta['title']} ({meta['duration_s']}s)")
            return 0
        from human_touch import ai_disclosure
        try:
            import money_funnel as mf
            funnel = mf.funnel_block("en", compact=True)
        except Exception:
            funnel = "Telegram: https://t.me/ai360trading" + chr(10) + "Website: https://ai360trading.in"
        NL = chr(10)
        desc = meta["description"] + NL + NL + funnel + NL + NL + ai_disclosure("en")
        if mode == "private-test":
            vid = E._upload(str(mp4), "[TEST - private] " + meta["title"], desc, meta["tags"], str(thumb), None)
            print(f"[REAL] PRIVATE TEST uploaded: https://youtu.be/{vid} (not announced, not marked done)")
            return 0
        when = E._next_publish()
        vid = E._upload(str(mp4), meta["title"], desc, meta["tags"], str(thumb), when)
        print(f"[REAL] scheduled {vid} for {when.isoformat()}")
        done.append({"story": key, "video": vid, "publish_at": when.isoformat(), "kind": "real"})
        E._save_done(done)
        E._tg("<b>New story Short (real footage)</b>: " + meta["title"] + chr(10) + "Goes live " + when.strftime("%a %d %b, %H:%M")
              + " UTC" + chr(10) + "https://youtu.be/" + vid)
    except Exception as e:
        import traceback
        traceback.print_exc()
        E._tg(f"AI360 story Shorts (real footage): pipeline error: {str(e)[:160]}. Nothing published; it will retry next run.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--mode", default="dry", choices=["dry", "private-test", "scheduled"])
    ap.add_argument("--out", default="output/story")
    ap.add_argument("--cache", default="bank_real")
    ap.add_argument("--story", default=None)
    a = ap.parse_args()
    if a.run:
        sys.exit(run(a.mode, a.out, a.cache, a.story))
    print("usage: python story_real.py --run --mode dry|private-test|scheduled")
