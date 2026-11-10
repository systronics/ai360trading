"""
pin_feed.py v1.0 (2026-11-10) - builds `pinterest.xml` (RSS 2.0) + one vertical 1000x1500 pin image per evergreen website article, for Pinterest's free 'auto-publish from RSS' (Pinterest business account + claimed
website; Pinterest accepts RSS 2.x / 1.x but NOT Atom, and every item link must be on the claimed domain; up to 200 pins/day; desktop setup only).
WHY our own feed: jekyll-feed only writes Atom (atom.xml) and most posts have no image. Owner 2026-11-10: 'do threads and pinterest auto'.
Rules: evergreen posts only (content_mode != 'market': the daily market-news posts are date-bound and noindex after 45 days), posts of the last 30 days, at most 20 items, images made only when missing
(public/image/pins/<slug>.jpg, served at https://ai360trading.in/public/image/pins/<slug>.jpg like the existing article share images). Pure Pillow, fail-open: on any error the existing feed is left untouched.
USAGE: python pin_feed.py        (writes pinterest.xml in the repo root and the pin images; the workflow commits them)
"""
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

import site_posts

MAX_ITEMS = 20
PIN_DIR = Path("public/image/pins")
FEED = Path("pinterest.xml")
THEMES = {"world-markets": ((16, 42, 92), (40, 120, 210)), "personal-finance": ((10, 70, 60), (30, 170, 120)), "default": ((40, 24, 92), (150, 60, 200))}
FONT_CANDIDATES = ["DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf", "LiberationSans-Bold.ttf"]


def _font(size):
    from PIL import ImageFont
    for name in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def wrap(draw, text, font, maxw, max_lines=7):
    """Greedy word wrap to at most max_lines (the last line gets '...' when text is cut). Pure on the draw object."""
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,;:- ") + "..."
    return lines


def make_pin(title, pillar, path):
    """1000x1500 JPEG: pillar-coloured gradient, big wrapped title, brand + domain. Returns True when written."""
    from PIL import Image, ImageDraw
    c1, c2 = THEMES.get(pillar, THEMES["default"])
    w, h = 1000, 1500
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        k = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3)))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((60, 60, 940, 130), radius=30, fill=(255, 255, 255, 40))
    d.text((500, 95), "AI360 TRADING", font=_font(38), fill=(255, 255, 255, 255), anchor="mm")
    size = 92
    f = _font(size)
    lines = wrap(d, title, f, 840)
    while len(lines) > 7 or (len(lines) > 5 and size > 66):
        size -= 6
        f = _font(size)
        lines = wrap(d, title, f, 840)
        if size <= 54:
            break
    lh = int(size * 1.22)
    y = 300
    for ln in lines:
        d.text((80, y), ln, font=f, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
        y += lh
    d.rounded_rectangle((60, 1290, 940, 1400), radius=40, fill=(255, 200, 50, 255))
    d.text((500, 1345), "Read the full guide: ai360trading.in", font=_font(40), fill=(20, 20, 40, 255), anchor="mm")
    d.text((500, 1450), "AI-assisted. Educational only.", font=_font(30), fill=(255, 255, 255, 200), anchor="mm")
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, quality=86)
    return True


def build_feed(items, now=None):
    """RSS 2.0 text for the items [{title, url, excerpt, date, image_url}]. Pure."""
    now = now or datetime.now(timezone.utc)
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">',
           "<channel>",
           "<title>AI360Trading - guides for Indian investors</title>",
           f"<link>{site_posts.SITE}</link>",
           "<description>Evergreen investing guides. AI-assisted, educational only, not investment advice.</description>",
           f"<lastBuildDate>{format_datetime(now)}</lastBuildDate>"]
    for it in items:
        try:
            pub = format_datetime(datetime.strptime(it["date"], "%Y-%m-%d").replace(hour=6, tzinfo=timezone.utc))
        except Exception:
            pub = format_datetime(now)
        desc = (it.get("excerpt") or "").strip()
        desc = (desc[:380].rsplit(" ", 1)[0] + "...") if len(desc) > 380 else desc
        desc = (desc + " AI-assisted. Educational only, not investment advice.").strip()
        out += ["<item>", f"<title>{escape(it['title'][:100])}</title>", f"<link>{escape(it['url'])}</link>", f'<guid isPermaLink="true">{escape(it["url"])}</guid>',
                f"<pubDate>{pub}</pubDate>",
                f'<description><![CDATA[<img src="{it["image_url"]}" alt="" /><p>{escape(desc)}</p>]]></description>',
                f'<enclosure url="{escape(it["image_url"])}" type="image/jpeg" length="0" />',
                f'<media:content url="{escape(it["image_url"])}" medium="image" type="image/jpeg" width="1000" height="1500" />', "</item>"]
    out += ["</channel>", "</rss>"]
    return "\n".join(out) + "\n"


def main():
    try:
        posts = [p for p in site_posts.recent_posts(max_age_days=30) if p.get("content_mode") != "market"][:MAX_ITEMS]
        if not posts:
            print("[PIN] no evergreen posts in the last 30 days - feed left as it is")
            return 0
        items = []
        for p in posts:
            img = PIN_DIR / f"{p['slug']}.jpg"
            if not img.exists():
                make_pin(p["title"], p.get("pillar", ""), img)
            items.append({**p, "image_url": f"{site_posts.SITE}/{img.as_posix()}"})
        FEED.write_text(build_feed(items), encoding="utf-8")
        print(f"[PIN] wrote {FEED} with {len(items)} items")
    except Exception as e:
        print("[PIN] skipped (fail-open):", str(e)[:150])
    return 0


if __name__ == "__main__":
    sys.exit(main())
