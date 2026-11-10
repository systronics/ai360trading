"""
site_posts.py v1.0 (2026-11-10) - tiny, dependency-free reader of the Jekyll posts in _posts/ for the auto-distribution scripts (threads_post.py, pin_feed.py).
Reads only the front matter keys we need (title, permalink, excerpt/description, date, content_mode, pillar, image). Never writes anything. Pure functions + one directory reader.
"""
import re
from datetime import date, datetime
from pathlib import Path

SITE = "https://ai360trading.in"
KEYS = ("title", "permalink", "excerpt", "description", "date", "content_mode", "pillar", "image")


def parse_front_matter(text):
    """dict of the wanted front-matter keys (strings, quotes stripped), or {} when there is no front matter. Pure."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if km and km.group(1) in KEYS:
            v = km.group(2).strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            out[km.group(1)] = v.replace('\\"', '"')
    return out


def post_url(fm):
    """Absolute URL of a post from its permalink, or '' when missing. Pure."""
    p = (fm.get("permalink") or "").strip()
    if not p.startswith("/"):
        return ""
    return SITE + p


def recent_posts(posts_dir="_posts", max_age_days=3, today=None):
    """Newest first: [{title, url, excerpt, date, content_mode, pillar, image, slug}] for posts not older than max_age_days (and not in the future). Fail-open -> []."""
    today = today or date.today()
    out = []
    try:
        for p in sorted(Path(posts_dir).glob("*.md"), reverse=True):
            fm = parse_front_matter(p.read_text(encoding="utf-8", errors="replace"))
            try:
                d = datetime.strptime(str(fm.get("date", ""))[:10], "%Y-%m-%d").date()
            except Exception:
                continue
            age = (today - d).days
            if age < 0 or age > max_age_days:
                if age > max_age_days:
                    break          # sorted newest first (file names start with the date), nothing older can qualify
                continue
            url = post_url(fm)
            if not (fm.get("title") and url):
                continue
            out.append({"title": fm["title"], "url": url, "excerpt": fm.get("excerpt") or fm.get("description") or "", "date": d.isoformat(),
                        "content_mode": fm.get("content_mode", ""), "pillar": fm.get("pillar", ""), "image": fm.get("image", ""), "slug": p.stem})
    except Exception:
        return []
    return out
