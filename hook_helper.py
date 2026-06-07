"""
hook_helper.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v1.0 (2026-05-31):
  Builds a bold-text HOOK intro card and prepends it to a Short / reel so the
  IN-FEED cover (the first frame YouTube Shorts / Instagram Reels / Facebook
  Reels show while scrolling) is a stop-scroll hook instead of the busy
  info-card. The narration audio + burned-in captions start AFTER the hook,
  so caption sync is preserved (audio is offset by exactly the hook length).

  DESIGN — must never break the income-critical daily video:
    - build_hook_frame()  : pure Pillow, no moviepy. Returns a PNG path.
    - prepend_hook()       : moviepy composition. RAISES on any error so the
                             caller can fall back to the hook-less render.
  Both are meant to be wrapped in try/except by the caller (fail-open).
"""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# How long the hook card is shown before the main content (seconds).
# 2.0s (was 1.4s) so viewers can actually READ a ~6-word curiosity hook before
# the narration starts — too short and the hook can't do its job.
HOOK_SECONDS = 2.0


def _get_font(paths, size):
    """First existing font from `paths` at `size`; default font if none found."""
    if isinstance(paths, str):
        paths = [paths]
    for p in paths:
        if p and os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap(draw, text, font, max_w):
    words, lines, line = text.split(), [], ""
    for w in words:
        test = (line + " " + w).strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def build_hook_frame(headline, screen_size, fonts, accent=(255, 210, 0),
                     out_path="output/hook_frame.png", sub=""):
    """
    Render a bold, minimal hook card (vertical). One huge auto-fit headline,
    optional sub line, accent frame. Returns the saved PNG path.
    Pure Pillow — safe to call/test without moviepy.
    """
    SW, SH = screen_size
    img  = Image.new("RGB", (SW, SH))
    draw = ImageDraw.Draw(img, "RGBA")

    # Dark vertical gradient
    for y in range(SH):
        t = y / SH
        draw.line([(0, y), (SW, y)],
                  fill=(int(6 + t * 12), int(9 + t * 16), int(22 + t * 34)))

    # Accent frame top + bottom
    draw.rectangle([(0, 0), (SW, 16)], fill=accent)
    draw.rectangle([(0, SH - 16), (SW, SH)], fill=accent)

    # Headline — huge, centered, auto-fit to max 4 lines
    size = 168
    f    = _get_font(fonts, size)
    lines = _wrap(draw, headline.upper(), f, SW - 110)
    while len(lines) > 4 and size > 96:
        size -= 12
        f     = _get_font(fonts, size)
        lines = _wrap(draw, headline.upper(), f, SW - 110)

    total_h = len(lines) * (size + 16)
    ty = (SH - total_h) // 2
    for line in lines[:4]:
        for dx, dy in [(-5, 5), (5, -5), (-5, -5), (5, 5)]:
            draw.text((SW // 2 + dx, ty + dy), line, font=f, fill=(0, 0, 0, 230), anchor="mm")
        draw.text((SW // 2, ty), line, font=f, fill=(255, 235, 0), anchor="mm")
        ty += size + 16

    # Optional sub line
    if sub:
        fs = _get_font(fonts, 56)
        draw.text((SW // 2, ty + 24), sub, font=fs, fill=accent, anchor="mm")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return out_path


def prepend_hook(main_clip, audio_clip, hook_frame_path, screen_size, hook_secs=HOOK_SECONDS):
    """
    Return a clip = [silent hook card for `hook_secs`] + [main_clip], with the
    narration audio shifted to start AFTER the hook (so captions stay synced).

    RAISES on any failure — the caller is responsible for falling back to the
    hook-less render. (We import moviepy here so this module can be used for
    frame-only work without moviepy installed.)
    """
    from moviepy.editor import ImageClip, concatenate_videoclips, CompositeAudioClip

    SW, SH = screen_size
    hook = ImageClip(hook_frame_path).set_duration(hook_secs)

    # Drop any audio already on the main clip; we re-attach a single combined
    # track below so concatenation never has to merge mixed/None audio.
    main_v = main_clip.set_audio(None)

    visual = concatenate_videoclips([hook, main_v], method="compose")
    combined_audio = CompositeAudioClip([audio_clip.set_start(hook_secs)]).set_duration(visual.duration)
    return visual.set_audio(combined_audio)
