"""
caption_helper.py — v1.0 (2026-05-31)

Burned-in captions for Shorts / Reels.

WHY: spoken-only videos lose viewers who watch muted (most mobile feed
autoplay is muted) and hurt accessibility + watch-time. Burned-in captions
lift retention and reach.

HOW: renders the spoken script as bottom-third karaoke-style caption chunks,
timed PROPORTIONALLY across the audio (no speech-to-text alignment needed →
₹0, offline, deterministic). Rendered with Pillow only and overlaid as
moviepy ImageClips — deliberately NOT moviepy TextClip, which shells out to
ImageMagick and is the #1 cause of caption failures on GitHub Actions.

DESIGN PRINCIPLE (per project rule): FULLY FAIL-OPEN. Any error anywhere
returns an empty list / the original clip, so a caption problem can NEVER
break the income-critical daily video. Worst case = the old caption-less video.

Used by: generate_shorts.py, generate_reel.py.
(generate_reel_morning.py already burns the spoken lines onto its frames.)
"""

import os

try:
    import numpy as np
except Exception:  # pragma: no cover - numpy ships with moviepy
    np = None


def _load_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                from PIL import ImageFont
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    try:
        from PIL import ImageFont
        return ImageFont.load_default()
    except Exception:
        return None


def _wrap(draw, text, font, max_w):
    """Greedy word-wrap to a pixel width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        try:
            width = draw.textlength(test, font=font)
        except Exception:
            width = len(test) * (font.size * 0.55 if hasattr(font, "size") else 18)
        if width <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _render_band(text, size, font, y_ratio):
    """Full-frame transparent RGBA image with a captioned, backed text block."""
    from PIL import Image, ImageDraw
    W, H = size
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    lines = _wrap(draw, text, font, int(W * 0.86))[:3]
    try:
        asc, desc = font.getmetrics()
        lh = asc + desc + 14
    except Exception:
        lh = int(W * 0.075)
    block_h = lh * max(1, len(lines))

    y0 = int(H * y_ratio) - block_h // 2
    pad = 26

    # translucent rounded backing → readable over any frame
    try:
        draw.rounded_rectangle(
            [(int(W * 0.04), y0 - pad), (int(W * 0.96), y0 + block_h + pad)],
            radius=28, fill=(0, 0, 0, 150),
        )
    except Exception:
        draw.rectangle(
            [(int(W * 0.04), y0 - pad), (int(W * 0.96), y0 + block_h + pad)],
            fill=(0, 0, 0, 150),
        )

    # outlined, centered text
    cy = y0 + lh // 2
    for ln in lines:
        for dx in (-3, -2, 0, 2, 3):
            for dy in (-3, -2, 0, 2, 3):
                if dx or dy:
                    draw.text((W // 2 + dx, cy + dy), ln, font=font,
                              fill=(0, 0, 0, 255), anchor="mm")
        draw.text((W // 2, cy), ln, font=font, fill=(255, 255, 255, 255), anchor="mm")
        cy += lh
    return img


def build_caption_clips(script_text, duration, size, font_paths,
                        words_per_caption=4, y_ratio=0.74, font_size=None):
    """
    Return a list of timed moviepy ImageClips (with alpha mask) to overlay.
    Returns [] on ANY problem (fail-open).
    """
    if np is None:
        return []
    try:
        from moviepy.editor import ImageClip
    except Exception:
        return []
    try:
        W, H = size
        text = " ".join((script_text or "").split())
        if not text or not duration or duration <= 0:
            return []

        if font_size is None:
            font_size = max(28, int(W * 0.060))  # ~65px at 1080 wide
        font = _load_font(font_paths, font_size)
        if font is None:
            return []

        words = text.split()
        total = len(words)
        if total == 0:
            return []
        chunks = [" ".join(words[i:i + words_per_caption])
                  for i in range(0, total, words_per_caption)]

        clips, t = [], 0.0
        for idx, ch in enumerate(chunks):
            seg = duration * (len(ch.split()) / total)
            start = t
            end = duration if idx == len(chunks) - 1 else (t + seg)
            if end <= start:
                end = start + 0.4

            band = _render_band(ch, size, font, y_ratio)
            arr = np.array(band)              # H x W x 4 (RGBA)
            rgb = arr[:, :, :3]
            mask = arr[:, :, 3] / 255.0

            clip = (ImageClip(rgb)
                    .set_start(start)
                    .set_duration(end - start)
                    .set_position((0, 0)))
            mclip = (ImageClip(mask, ismask=True)
                     .set_start(start)
                     .set_duration(end - start))
            clips.append(clip.set_mask(mclip))
            t += seg
        return clips
    except Exception as e:
        print(f"  ⚠️ caption_helper: captions skipped (fail-open): {e}")
        return []


def add_captions(base_clip, spoken_text, caption_duration, size, font_paths, **kw):
    """
    Composite burned-in captions over base_clip.
    Fail-open: returns the ORIGINAL base_clip unchanged on any error.
    """
    try:
        clips = build_caption_clips(spoken_text, caption_duration, size, font_paths, **kw)
        if not clips:
            return base_clip
        from moviepy.editor import CompositeVideoClip
        comp = CompositeVideoClip([base_clip, *clips], size=size)
        return comp.set_duration(base_clip.duration)
    except Exception as e:
        print(f"  ⚠️ caption_helper.add_captions skipped (fail-open): {e}")
        return base_clip
