"""
story_motion.py v1.0 (2026-10-27) — real-motion story Shorts built from a "clip bank".

WHY
  Real 3D motion beats zoom-on-a-still. The free route: scene image (Pixar-style, Cloudflare FLUX via emotion_story)
  -> Wan 2.2 image-to-video on the free Hugging Face ZeroGPU Space (zerogpu-aoti/wan2-2-fp8da-aoti-faster).
  Free quota is small (measured 2026-10-27: 8 clips per day-window WITH the HF_TOKEN secret, ~3 without), so ONE story
  is built over a day or two: every run makes as many clips as the quota allows and keeps them in a bank (a git branch
  'motion-bank'); when every scene has its two clips, the Short is assembled and uploaded PRIVATE with a publishAt time.

HOW A STORY COMPLETES
  per scene i: clip A = image -> 3.5s motion; clip B = last frame of A -> 3.5s continuation (chaining a 2nd short
  clip instead of one long one limits drift). Phase 1 makes every A, phase 2 every B. Complete = all A and all B.

SAFETY (never-break doctrine)
  * Fully fail-open: a quota/Space failure stops the run quietly and keeps what exists; nothing is published half-made.
  * Uses the same upload path, title/description/tags, thumbnail and disclosure as emotion_story.py.
  * Shares _data/stories_done.json with emotion_story.py so a story is never published twice.
  * Visuals are AI-generated and fictional; description says so.

Usage:  python story_motion.py --run --mode dry|private-test|scheduled [--bank bank] [--out output/motion] [--story fear]
"""
import os
import sys
import json
import time
import shutil
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

import emotion_story as E

SPACE = "zerogpu-aoti/wan2-2-fp8da-aoti-faster"
CLIP_SECONDS = 3.5
W, H = E.W, E.H
FOLLOW = "continue the same motion naturally, subtle camera push in, keep the same characters and clothes, cinematic Pixar-style 3D animation"
QUOTA_MARKERS = ("exceeded your ZeroGPU", "ZeroGPU runs limit", "GPU quota")


class QuotaExceeded(Exception):
    pass


def motion_prompt(story, i):
    st = E.STORIES[story]
    return (f"{st['who']}, {st['scenes'][i][2]}, natural expressive movement, subtle camera push in, "
            "cinematic Pixar-style 3D animation")


def get_client():
    from gradio_client import Client
    tok = os.environ.get("HF_TOKEN") or None
    try:
        return Client(SPACE, token=tok)
    except TypeError:
        return Client(SPACE, hf_token=tok)


def animate(client, src, prompt, out_path):
    """One clip. Returns Path, or None on a non-quota failure. Raises QuotaExceeded to stop the whole run."""
    from gradio_client import handle_file
    if out_path.exists() and out_path.stat().st_size > 10000:
        return out_path
    for k in range(2):
        try:
            r = client.predict(input_image=handle_file(str(src)), prompt=prompt, steps=6,
                               duration_seconds=CLIP_SECONDS, api_name="/generate_video")
            vid = r[0]["video"] if isinstance(r[0], dict) else r[0]
            shutil.copy(vid, out_path)
            return out_path
        except Exception as e:
            msg = str(e)
            if any(m in msg for m in QUOTA_MARKERS):
                raise QuotaExceeded(msg[:160])
            print(f"  [WAN] attempt {k + 1} failed: {msg[:140]}")
            time.sleep(6)
    return None


def last_frame(mp4, png):
    from moviepy.editor import VideoFileClip
    v = VideoFileClip(str(mp4))
    Image.fromarray(v.get_frame(max(0, v.duration - 0.06))).save(png)
    v.close()
    return png


def paths(d, story, i):
    return d / f"{story}_{i}.jpg", d / f"{story}_{i}_a.mp4", d / f"{story}_{i}_b.mp4"


def status(d, story, n):
    a = sum(1 for i in range(n) if paths(d, story, i)[1].exists())
    b = sum(1 for i in range(n) if paths(d, story, i)[2].exists())
    return a, b


def bank_step(story, bank_root):
    """Make images (cached), then as many clips as the free quota allows. Returns True when the story is complete."""
    st = E.STORIES[story]
    n = len(st["scenes"])
    d = Path(bank_root) / story
    d.mkdir(parents=True, exist_ok=True)
    for i, (narr, cap, prompt) in enumerate(st["scenes"]):
        img, _, _ = paths(d, story, i)
        if not img.exists():
            E.get_scene_image(story, i, st["who"], prompt, st["accent"], d)   # caches d/<story>_<i>.jpg
    if not all(paths(d, story, i)[0].exists() for i in range(n)):
        print("[MOTION] some scene images are missing (image service down?) - will retry next run")
        return False
    a0, b0 = status(d, story, n)
    if a0 == n and b0 == n:
        return True
    try:
        client = get_client()
        for i in range(n):                                   # phase 1: every A
            img, a, _ = paths(d, story, i)
            if not a.exists():
                print(f"[MOTION] clip A scene {i + 1}/{n}")
                animate(client, img, motion_prompt(story, i), a)
        for i in range(n):                                   # phase 2: every B (needs the last frame of A)
            _, a, b = paths(d, story, i)
            if a.exists() and not b.exists():
                print(f"[MOTION] clip B scene {i + 1}/{n}")
                lf = last_frame(a, d / f"{story}_{i}_a_last.png")
                animate(client, lf, FOLLOW, b)
    except QuotaExceeded as q:
        print(f"[MOTION] free quota used up for now: {q}")
    except Exception as e:
        print(f"[MOTION] clip step stopped (fail-open): {str(e)[:200]}")
    a1, b1 = status(d, story, n)
    print(f"[MOTION] {story}: clips A {a1}/{n}, B {b1}/{n} (this run added {a1 - a0 + b1 - b0})")
    return a1 == n and b1 == n


def ambient(duration, sr=44100, mood="tense"):
    """Quiet synthetic bed (two low sines, slow tremolo) so the track is never empty; narration stays on top."""
    t = np.linspace(0, duration, int(duration * sr), endpoint=False)
    f1, f2 = (55.0, 82.5) if mood == "tense" else (65.4, 98.0)
    sig = 0.5 * np.sin(2 * np.pi * f1 * t) + 0.3 * np.sin(2 * np.pi * f2 * t)
    sig *= (0.75 + 0.25 * np.sin(2 * np.pi * 0.25 * t))
    fade = np.minimum(1, np.minimum(t / 1.5, (duration - t) / 1.5))
    return (sig * fade * 0.06).astype(np.float32)


def assemble(story, bank_root, out_dir):
    from moviepy.editor import (VideoClip, VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip)
    from moviepy.audio.AudioClip import AudioArrayClip
    import moviepy.video.fx.all as vfx
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    d = Path(bank_root) / story
    st = E.STORIES[story]
    n = len(st["scenes"])
    scenes = []
    mood = "calm" if story == "patience" else "tense"
    for i, (narr, cap, prompt) in enumerate(st["scenes"]):
        img, a, b = paths(d, story, i)
        rate, pitch = E.VOICE_PROFILES[mood][i]
        ap = out_dir / f"{story}_{i}.mp3"
        E.make_voice(narr, ap, rate, pitch)
        voice = AudioFileClip(str(ap))
        dur = voice.duration + 0.5
        raw = concatenate_videoclips([VideoFileClip(str(a)), VideoFileClip(str(b))])
        raw = raw.fx(vfx.speedx, final_duration=dur) if raw.duration < dur * 0.98 else raw.subclip(0, dur)
        first = Image.fromarray(raw.get_frame(0)).convert("RGB")
        bg = first.resize((int(first.width * H / first.height) + 1, H), Image.LANCZOS)
        left = (bg.width - W) // 2
        bg = np.array(bg.crop((left, 0, left + W, H)).filter(ImageFilter.GaussianBlur(28)), dtype=np.float32) * 0.45
        rgb, alpha = E._static_overlay(st["accent"], st["tag"], cap, i, n)

        def make(t, raw=raw, bg=bg, rgb=rgb, alpha=alpha):
            frame = bg.copy()
            fg = np.array(Image.fromarray(raw.get_frame(min(t, raw.duration - 0.05))).resize((W, W), Image.BILINEAR), dtype=np.float32)
            frame[150:150 + W, :, :] = fg
            frame = frame * (1 - alpha) + rgb * alpha
            return frame.clip(0, 255).astype(np.uint8)

        bed = ambient(dur, mood=mood)
        bed = AudioArrayClip(np.stack([bed, bed], axis=1), fps=44100)
        sc = VideoClip(make, duration=dur).set_fps(24)
        sc = sc.set_audio(CompositeAudioClip([bed, voice.set_start(0)]).set_duration(dur))
        scenes.append(sc)
    final = concatenate_videoclips(scenes, method="compose")
    mp4 = out_dir / f"{story}_motion.mp4"
    final.write_videofile(str(mp4), fps=24, codec="libx264", audio_codec="aac", preset="medium", logger=None)
    dur_total = final.duration
    face = None
    try:
        if E.STORY_ORDER.index(story) % 2 == 1 and os.path.exists("public/image/amit_cutout.png"):
            face = "public/image/amit_cutout.png"
    except ValueError:
        pass
    thumb = out_dir / f"{story}_thumb.jpg"
    E.build_thumbnail(story, Image.open(paths(d, story, 1)[0]).convert("RGB"), thumb, face=face)
    meta = E.make_meta(story, dur_total)
    print(f"[MOTION] assembled {mp4} ({dur_total:.1f}s)")
    return mp4, thumb, meta


def run(mode, bank_root, out_dir, story=None):
    """Never raises; always returns 0."""
    try:
        done = E._load_done()
        used = {x.get("story") for x in done}
        key = story or next((k for k in E.STORY_ORDER if k in E.STORIES and k not in used), None)
        if not key:
            E._tg("AI360 story Shorts (motion): the story queue is EMPTY. Ask Claude to add more stories.")
            print("[MOTION] queue empty")
            return 0
        print(f"[MOTION] story = {key} (mode={mode})")
        complete = bank_step(key, bank_root)
        if not complete:
            print("[MOTION] not complete yet - the bank keeps its clips, next run continues")
            return 0
        mp4, thumb, meta = assemble(key, bank_root, out_dir)
        if meta["duration_s"] > 59.0:
            E._tg(f"AI360 story Shorts (motion): '{key}' is {meta['duration_s']}s (over 59s), NOT uploaded.")
            return 0
        if mode == "dry":
            print(f"[MOTION] DRY RUN, nothing uploaded: {meta['title']}")
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
            vid = E._upload(str(mp4), "[TEST - private] " + meta["title"], desc, meta["tags"], str(thumb), None)
            print(f"[MOTION] PRIVATE TEST uploaded: https://youtu.be/{vid} (not announced, not marked done)")
            return 0
        when = E._next_publish()
        vid = E._upload(str(mp4), meta["title"], desc, meta["tags"], str(thumb), when)
        print(f"[MOTION] scheduled {vid} for {when.isoformat()}")
        done.append({"story": key, "video": vid, "publish_at": when.isoformat(), "kind": "motion"})
        E._save_done(done)
        E._tg("<b>New story Short (real motion)</b>: " + meta["title"] + chr(10) + "Goes live " + when.strftime("%a %d %b, %H:%M")
              + " UTC" + chr(10) + "https://youtu.be/" + vid)
        shutil.rmtree(Path(bank_root) / key, ignore_errors=True)      # keep the bank branch small
    except Exception as e:
        import traceback
        traceback.print_exc()
        E._tg(f"AI360 story Shorts (motion): pipeline error: {str(e)[:160]}. Nothing published; it will retry next run.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--mode", default="dry", choices=["dry", "private-test", "scheduled"])
    ap.add_argument("--bank", default="bank")
    ap.add_argument("--out", default="output/motion")
    ap.add_argument("--story", default=None)
    a = ap.parse_args()
    if a.run:
        sys.exit(run(a.mode, a.bank, a.out, a.story))
    print("usage: python story_motion.py --run --mode dry|private-test|scheduled")
