"""
media_helper.py — Image + YouTube embed helpers for SEO articles
================================================================
v1.1 (2026-05-30) — IMAGE FIX: articles were showing BROKEN images.
  Two bugs: (1) daily-articles.yml never passed PEXELS_API_KEY into the job,
  so the working Pexels source was skipped; (2) the fallback source.unsplash.com
  was discontinued by Unsplash in 2024 and emitted dead <img> URLs. Fixed the
  workflow env, and replaced Unsplash Source with LoremFlickr — which is now
  VERIFIED to resolve to a real image before use (else falls to Picsum), so a
  dead image URL can never be written again.

v1.0 (2026-05-28) — first cut for SEO audit fix
  Adds hero images + inline images + YouTube embeds to generated articles.
  All sources are free, no-copyright, no-fees:
    - Pexels API (free, 200 req/hr with free signup) — primary
    - Unsplash Source API (no key, deprecated but still works) — fallback
    - Picsum (random images) — final fallback
    - YouTube RSS feed (no API key needed) — for own-channel embeds

Why this exists:
  SEO audit 2026-05-28 found generated articles had ZERO images, ZERO video
  embeds. Dwell time + visual engagement = both 0. Google ranks based on
  these signals. Adding media fixes 2 of the top 5 ranking issues at once.

Functions:
  get_hero_image(pillar_id, fallback_query=None) -> dict
    Returns {"url": ..., "alt": ..., "credit": ...} for a pillar-relevant
    hero image. Used at the top of every article.

  get_inline_image(pillar_id, position_seed=0) -> dict
    Returns a SECOND pillar-relevant image, different from hero. Used mid-
    article. position_seed varies the image so consecutive articles don't
    repeat.

  get_youtube_embed_html(pillar_id=None, recent_index=0) -> str
    Returns ready-to-paste HTML for a responsive YouTube embed of one of
    your channel's recent videos. recent_index 0 = latest, 1 = previous,
    etc. Picks from RSS feed (no API key required).

  build_article_media(pillar_id) -> dict
    Convenience: returns hero + inline + youtube_embed in one call. Use
    this from generate_articles.py.

All functions are FAIL-OPEN: if a network call fails or a service is down,
they return empty dict / empty string. Article still generates, just
without that media. Never raises.
"""

import os
import random
import re
import time
import xml.etree.ElementTree as ET

import requests

# ─────────────────────────────────────────────
# Pillar → image search query mapping
# ─────────────────────────────────────────────
PILLAR_QUERIES = {
    "stock-market":     ["stock market chart", "trading desk monitor", "wall street",
                          "candlestick chart", "stock exchange screen", "financial charts"],
    "bitcoin":          ["cryptocurrency", "bitcoin coin", "blockchain technology",
                          "crypto trading", "digital currency", "btc chart"],
    "personal-finance": ["family savings money", "personal budget planner", "indian rupees",
                          "piggy bank savings", "financial planning", "money jar coins"],
    "ai-trading":       ["artificial intelligence trading", "algorithm code screen",
                          "data analytics dashboard", "machine learning chart",
                          "ai technology abstract", "neural network data"],
}

YOUTUBE_CHANNEL_ID = "UC9dAJakbfPXk8zL31AVuTfA"  # @ai360trading
YOUTUBE_RSS = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "").strip()
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "").strip()

# Module-level cache so multiple articles in one run reuse the RSS fetch
_VIDEO_CACHE = {"ts": 0, "items": []}
_CACHE_TTL = 1800  # 30 minutes


def _pick_query(pillar_id: str, position_seed: int = 0) -> str:
    queries = PILLAR_QUERIES.get(pillar_id, PILLAR_QUERIES["stock-market"])
    idx = (position_seed + random.randint(0, len(queries) - 1)) % len(queries)
    return queries[idx]


def _try_pexels(query: str) -> dict:
    """Returns dict with url/alt/credit if Pexels API key set + call succeeds."""
    if not PEXELS_API_KEY:
        return {}
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 15, "orientation": "landscape"},
            headers={"Authorization": PEXELS_API_KEY},
            timeout=8,
        )
        if not r.ok:
            return {}
        photos = r.json().get("photos", [])
        if not photos:
            return {}
        p = random.choice(photos)
        return {
            "url":    p["src"]["large"],
            "alt":    p.get("alt") or query,
            "credit": f"Photo by {p['photographer']} on Pexels",
            "source": "pexels",
        }
    except Exception:
        return {}


def _try_pixabay(query: str) -> dict:
    """Returns dict if Pixabay API key set + call succeeds."""
    if not PIXABAY_API_KEY:
        return {}
    try:
        r = requests.get(
            "https://pixabay.com/api/",
            params={
                "key":         PIXABAY_API_KEY,
                "q":           query,
                "image_type":  "photo",
                "orientation": "horizontal",
                "safesearch":  "true",
                "per_page":    15,
            },
            timeout=8,
        )
        if not r.ok:
            return {}
        hits = r.json().get("hits", [])
        if not hits:
            return {}
        h = random.choice(hits)
        return {
            "url":    h["largeImageURL"],
            "alt":    h.get("tags", query),
            "credit": f"Image by {h.get('user', 'Pixabay')} on Pixabay",
            "source": "pixabay",
        }
    except Exception:
        return {}


def _try_loremflickr(query: str) -> dict:
    """
    Keyless topical fallback (LoremFlickr — Flickr CC images by keyword).
    v1.1: replaces the dead source.unsplash.com (Unsplash shut that API down
    in 2024 — it was emitting BROKEN image URLs into every article that fell
    through to it). We GET the URL, follow redirects, and ONLY return it if it
    actually resolves to an image — so we can never emit a dead <img> again.
    """
    try:
        slug = re.sub(r"[^a-z0-9, ]", "", query.lower()).replace(", ", ",").replace(" ", ",")
        url  = f"https://loremflickr.com/1200/630/{slug}"
        r = requests.get(url, timeout=8, allow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0"})
        ctype = r.headers.get("Content-Type", "")
        if r.ok and ctype.startswith("image/"):
            return {
                "url":    r.url,          # final resolved image URL (no re-redirect on load)
                "alt":    query,
                "credit": "Photo via Flickr (Creative Commons)",
                "source": "loremflickr",
            }
        return {}
    except Exception:
        return {}


def _try_picsum(seed: int) -> dict:
    """Final fallback: random unrelated image (still better than no image at all)."""
    return {
        "url":    f"https://picsum.photos/seed/{seed}/1200/630",
        "alt":    "Featured image",
        "credit": "Image via Picsum",
        "source": "picsum",
    }


def _get_image(pillar_id: str, position_seed: int = 0) -> dict:
    """Cascade through providers — return first that works."""
    query = _pick_query(pillar_id, position_seed)
    for provider in (_try_pexels, _try_pixabay, _try_loremflickr):
        result = provider(query)
        if result.get("url"):
            return result
    return _try_picsum(position_seed + hash(pillar_id) % 1000)


def get_hero_image(pillar_id: str, fallback_query: str = None) -> dict:
    """Pick a pillar-relevant hero image. Returns {} only on total failure."""
    try:
        result = _get_image(pillar_id, position_seed=int(time.time()) % 100)
        return result or {}
    except Exception as e:
        print(f"  [media] hero image failed ({e}) — skipping")
        return {}


def get_inline_image(pillar_id: str, position_seed: int = 17) -> dict:
    """Pick a SECOND pillar-relevant image, different from hero."""
    try:
        # use a different seed so it picks a different query
        result = _get_image(pillar_id, position_seed=position_seed + 41)
        return result or {}
    except Exception as e:
        print(f"  [media] inline image failed ({e}) — skipping")
        return {}


def _fetch_recent_videos() -> list:
    """Fetch and cache the channel's RSS feed of recent videos."""
    now = time.time()
    if now - _VIDEO_CACHE["ts"] < _CACHE_TTL and _VIDEO_CACHE["items"]:
        return _VIDEO_CACHE["items"]
    try:
        r = requests.get(YOUTUBE_RSS, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        if not r.ok:
            return []
        root = ET.fromstring(r.content)
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "yt":   "http://www.youtube.com/xml/schemas/2015",
            "media":"http://search.yahoo.com/mrss/",
        }
        items = []
        for entry in root.findall("atom:entry", ns):
            vid_el   = entry.find("yt:videoId", ns)
            title_el = entry.find("atom:title", ns)
            if vid_el is not None and title_el is not None:
                items.append({"id": vid_el.text, "title": title_el.text})
        _VIDEO_CACHE["ts"]    = now
        _VIDEO_CACHE["items"] = items
        return items
    except Exception as e:
        print(f"  [media] YouTube RSS fetch failed ({e}) — skipping embeds")
        return []


def get_youtube_embed_html(pillar_id: str = None, recent_index: int = 0) -> str:
    """
    Return responsive HTML for a YouTube embed of a recent channel video.
    recent_index 0 = latest, higher = older.
    Returns "" on failure (article still works without it).
    """
    videos = _fetch_recent_videos()
    if not videos:
        return ""
    # Pick from a small window of recent videos so different articles get
    # different embeds within the same day's run.
    if recent_index >= len(videos):
        recent_index = recent_index % len(videos)
    v = videos[recent_index]
    return (
        '<div style="position:relative;padding-bottom:56.25%;height:0;'
        'overflow:hidden;max-width:100%;margin:24px 0;border-radius:8px;">'
        f'<iframe src="https://www.youtube.com/embed/{v["id"]}?rel=0" '
        'style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" '
        'frameborder="0" allowfullscreen loading="lazy" '
        f'title="{v["title"][:80]}" '
        'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
        'gyroscope; picture-in-picture; web-share">'
        '</iframe></div>\n'
        f'<p style="font-size:0.85em;color:#666;margin-top:-12px;">'
        f'📺 <a href="https://www.youtube.com/watch?v={v["id"]}" rel="noopener" '
        f'target="_blank">Watch on YouTube: {v["title"][:80]}</a></p>\n'
    )


def build_article_media(pillar_id: str, article_index: int = 0) -> dict:
    """
    One-call convenience used by generate_articles.py.
    Returns dict with:
      hero_html       — markdown/HTML to insert just below schema block
      inline_html     — to insert mid-article (after section 3 or so)
      youtube_html    — to insert near end (after section 5 or so)
    Each value is "" if its source failed. Article still works.
    """
    hero = get_hero_image(pillar_id)
    inline = get_inline_image(pillar_id, position_seed=article_index * 13)
    yt_html = get_youtube_embed_html(pillar_id, recent_index=article_index % 10)

    def img_block(img: dict) -> str:
        if not img.get("url"):
            return ""
        return (
            f'<figure style="margin:24px 0;">'
            f'<img src="{img["url"]}" alt="{img["alt"]}" '
            f'style="width:100%;max-width:1200px;height:auto;border-radius:8px;display:block;" '
            f'loading="lazy" decoding="async">'
            f'<figcaption style="font-size:0.8em;color:#888;text-align:center;margin-top:6px;">'
            f'{img["credit"]}</figcaption></figure>\n'
        )

    return {
        "hero_html":    img_block(hero),
        "inline_html":  img_block(inline),
        "youtube_html": yt_html,
    }


# ─────────────────────────────────────────────
# Smoke test (manual run only)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("media_helper.py smoke test")
    print("=" * 60)
    for pillar in ("stock-market", "bitcoin", "personal-finance", "ai-trading"):
        media = build_article_media(pillar, article_index=0)
        print(f"\nPillar: {pillar}")
        print(f"  Hero present:    {bool(media['hero_html'])}")
        print(f"  Inline present:  {bool(media['inline_html'])}")
        print(f"  YouTube present: {bool(media['youtube_html'])}")
        if media["hero_html"]:
            url = re.search(r'src="([^"]+)"', media["hero_html"])
            if url:
                print(f"  Hero URL: {url.group(1)[:80]}")
