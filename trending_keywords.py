"""
AI360 Trending Keywords Engine — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pulls what people are ACTUALLY searching right now (free, no API key) and caches
it so content generators can ride trending terms in titles, hashtags and topics.

Sources (all free, stdlib only — no pip install, no key):
  - Google autocomplete  (suggestqueries.google.com)
  - YouTube autocomplete  (same endpoint, ds=yt)

Design rules (₹0-forever, never-break):
  - FAIL-OPEN: any network error is swallowed; if everything fails we keep the
    PREVIOUS _data/trending.json untouched, so generators always have data.
  - No third-party packages (pytrends etc. are fragile) — only urllib stdlib.
  - Output: _data/trending.json  ->  {"generated": ..., "finance": [...], "kids": [...]}

Usage:
  python trending_keywords.py          # refresh the cache
  from trending_keywords import get_trending
  tags = get_trending("finance", 8)    # safe: returns [] if cache missing
"""

import json
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

CACHE = Path(__file__).parent / "_data" / "trending.json"

# Seed terms per category — autocomplete expands these into real trending queries.
SEEDS = {
    "finance": [
        "nifty", "share market", "stock market", "bank nifty", "ipo",
        "gold rate", "bitcoin", "mutual fund", "sensex", "intraday",
    ],
    "kids": [
        "moral story", "kids story", "bedtime story", "panchatantra",
        "short story for kids",
    ],
}

# Tokens we never want surfacing as a "trend" (noise / unsafe / off-brand).
_BLOCK = {"vs", "or", "the", "and", "for", "live", "news", "today", "tips"}

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def _suggest(query: str, youtube: bool = False) -> list:
    """One autocomplete call. Returns [] on any failure (fail-open)."""
    base = "https://suggestqueries.google.com/complete/search"
    params = {"client": "firefox", "q": query}
    if youtube:
        params["ds"] = "yt"
    url = base + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=8) as r:
            raw = r.read().decode("utf-8", "ignore")
        data = json.loads(raw)
        # Format: [query, [suggestion, suggestion, ...], ...]
        return [s for s in data[1] if isinstance(s, str)] if len(data) > 1 else []
    except Exception as e:
        print(f"[TREND] suggest fail ({query}, yt={youtube}): {e}")
        return []


def _collect(seeds: list) -> list:
    """Aggregate + rank suggestions across all seeds for one category."""
    counter = Counter()
    for seed in seeds:
        for yt in (False, True):
            for sug in _suggest(seed, youtube=yt):
                s = sug.strip().lower()
                # keep multi-word, drop pure noise / the seed itself
                if len(s) < 4 or s == seed.lower():
                    continue
                if all(w in _BLOCK for w in s.split()):
                    continue
                counter[s] += 1
            time.sleep(0.3)  # be gentle on the endpoint
    # most common first
    return [phrase for phrase, _ in counter.most_common(40)]


def refresh() -> dict:
    """Refresh the cache. On total failure, preserve the existing file."""
    out = {"generated": datetime.now(timezone.utc).isoformat()}
    any_ok = False
    for cat, seeds in SEEDS.items():
        terms = _collect(seeds)
        if terms:
            any_ok = True
        out[cat] = terms
        print(f"[TREND] {cat}: {len(terms)} terms")

    if not any_ok:
        print("[TREND] all sources failed — keeping previous cache")
        return _load_raw()

    try:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[TREND] wrote {CACHE}")
    except Exception as e:
        print(f"[TREND] write fail: {e}")
    return out


def _load_raw() -> dict:
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_trending(category: str = "finance", n: int = 8) -> list:
    """Safe reader for generators — returns [] if cache is missing/empty."""
    try:
        return _load_raw().get(category, [])[:n]
    except Exception:
        return []


if __name__ == "__main__":
    data = refresh()
    print("\n-- SAMPLE --")
    for cat in SEEDS:
        print(f"{cat}: {data.get(cat, [])[:8]}")
