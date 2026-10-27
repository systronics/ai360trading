"""
story_motion.py v0.1 (2026-10-27) — LOCAL EXPERIMENT: real-motion story Short.
  scene image (Pixar-style, from emotion_story) -> Wan 2.2 image-to-video on a free Hugging Face ZeroGPU Space
  (zerogpu-aoti/wan2-2-fp8da-aoti-faster, no key needed for a small test) -> 2 chained clips per scene ->
  9:16 frame (blurred background + sharp clip) + captions + Hindi narration + soft ambient bed.

NOT wired to any workflow. Fail-open idea for later: any clip that fails falls back to the Ken Burns image.
Usage:  python story_motion.py fear      (uses images in _drafts_local/cloud_fear2/fear_<i>.jpg)
Limits: clips are 640x640 / 16fps / ~3.5s; chaining can drift (clothes/pose) so each scene uses only 2 clips.
"""
import os, sys, time, shutil, asyncio
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

import emotion_story as E

SPACE = "zerogpu-aoti/wan2-2-fp8da-aoti-faster"
OUT = Path("_drafts_local/motion_sample")
W, H = E.W, E.H

PROMPTS = {
    "fear": [
        "the man sits at his desk at 2 AM, red falling chart light flickers on his face, he exhales and rubs his tired eyes, slow camera push in, cinematic 3D animation",
        "sweating worried face, trembling hand over the mouse, eyes darting nervously, friends behind him lean in anxiously, cinematic 3D animation",
        "he hesitates, then clicks the sell button, his shoulders drop in defeat, red light pulses on the screen, cinematic 3D animation",
        "he stands by the window at dawn, his young daughter hugs his leg, warm green light grows, he looks down with regret, cinematic 3D animation",
        "calm man writes a plan in his notebook, soft morning sunlight, a gentle smile slowly forms, his wife pours tea, cinematic 3D animation",
    ],
}
FOLLOW = "continue the same motion naturally, subtle camera push in, keep the same character and clothes, cinematic 3D animation"


def _client():
    from gradio_client import Client
    return Client(SPACE)


def animate(client, image_path_or_url, prompt, out_path, seconds=3.5, tries=3):
    """One clip. Returns Path or None (fail-open)."""
    from gradio_client import handle_file
    if out_path.exists() and out_path.stat().st_size > 10000:
        return out_path
    for k in range(tries):
        try:
            r = client.predict(input_image=handle_file(str(image_path_or_url)), prompt=prompt, steps=6,
                               duration_seconds=seconds, api_name="/generate_video")
            vid = r[0]["video"] if isinstance(r[0], dict) else r[0]
            shutil.copy(vid, out_path)
            return out_path
        except Exception as e:
            print(f"  [WAN] try {k + 1} failed: {str(e)[:120]}")
            time.sleep(8 * (k + 1))
    return None


def last_frame(mp4, png):
    from moviepy.editor import VideoFileClip
    v = VideoFileClip(str(mp4))
    Image.fromarray(v.get_frame(max(0, v.duration - 0.06))).save(png)
    v.close()
    return png


def scene_clips(client, story, i, img_path, out_dir):
    prompts = PROMPTS[story]
    a = animate(client, img_path, prompts[i], out_dir / f"{story}_{i}_a.mp4")
    if not a:
        return []
    lf = last_frame(a, out_dir / f"{story}_{i}_a_last.png")
    b = animate(client, lf, FOLLOW, out_dir / f"{story}_{i}_b.mp4")
    return [a] + ([b] if b else [])


def ambient(duration, sr=44100, mood="tense"):
    """Soft synthetic bed: two low sines with slow tremolo. Quiet on purpose; narration stays on top."""
    t = np.linspace(0, duration, int(duration * sr), endpoint=False)
    f1, f2 = (55.0, 82.5) if mood == "tense" else (65.4, 98.0)
    sig = 0.5 * np.sin(2 * np.pi * f1 * t) + 0.3 * np.sin(2 * np.pi * f2 * t)
    sig *= (0.75 + 0.25 * np.sin(2 * np.pi * 0.25 * t))
    fade = np.minimum(1, np.minimum(t / 1.5, (duration - t) / 1.5))
    return (sig * fade * 0.06).astype(np.float32)


def build(story="fear", img_dir="_drafts_local/cloud_fear2"):
    from moviepy.editor import (VideoClip, VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip,
                                concatenate_audioclips)
    from moviepy.audio.AudioClip import AudioArrayClip
    OUT.mkdir(parents=True, exist_ok=True)
    st = E.STORIES[story]
    n = len(st["scenes"])
    client = _client()
    scene_videos, voices = [], []
    for i, (narr, cap, prompt) in enumerate(st["scenes"]):
        print(f"[MOTION] scene {i + 1}/{n}")
        img = Path(img_dir) / f"{story}_{i}.jpg"
        rate, pitch = E.VOICE_PROFILES["calm" if story == "patience" else "tense"][i]
        ap = OUT / f"{story}_{i}.mp3"
        E.make_voice(narr, ap, rate, pitch)
        a = AudioFileClip(str(ap))
        dur = a.duration + 0.5
        clips = scene_clips(client, story, i, img, OUT)
        ov = E._static_overlay(st["accent"], st["tag"], cap, i, n)
        rgb, alpha = ov
        if clips:
            vc = [VideoFileClip(str(c)) for c in clips]
            raw = concatenate_videoclips(vc)
            raw = raw.fx(__import__("moviepy.video.fx.all", fromlist=["speedx"]).speedx, final_duration=dur) if raw.duration < dur * 0.98 else raw.subclip(0, dur)
            first = Image.fromarray(raw.get_frame(0)).convert("RGB")
        else:
            raw, first = None, Image.open(img).convert("RGB")
        bg = first.resize((int(first.width * H / first.height) + 1, H), Image.LANCZOS)
        left = (bg.width - W) // 2
        bg = bg.crop((left, 0, left + W, H)).filter(ImageFilter.GaussianBlur(28))
        bg = np.array(bg, dtype=np.float32) * 0.45

        def make(t, raw=raw, bg=bg, rgb=rgb, alpha=alpha, first=first):
            frame = bg.copy()
            src = raw.get_frame(min(t, raw.duration - 0.05)) if raw is not None else np.array(first)
            fg = np.array(Image.fromarray(src).resize((W, W), Image.BILINEAR), dtype=np.float32)
            frame[150:150 + W, :, :] = fg
            frame = frame * (1 - alpha) + rgb * alpha
            return frame.clip(0, 255).astype(np.uint8)

        sc = VideoClip(make, duration=dur).set_fps(24)
        mood = "calm" if story == "patience" else "tense"
        bed = ambient(dur, mood=mood)
        bed = AudioArrayClip(np.stack([bed, bed], axis=1), fps=44100)
        sc = sc.set_audio(CompositeAudioClip([bed, a.set_start(0)]).set_duration(dur))
        scene_videos.append(sc)
    final = concatenate_videoclips(scene_videos, method="compose")
    mp4 = OUT / f"{story}_motion.mp4"
    final.write_videofile(str(mp4), fps=24, codec="libx264", audio_codec="aac", preset="medium", logger=None)
    print(f"[MOTION] done: {mp4} ({final.duration:.1f}s)")
    return mp4


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "fear")
