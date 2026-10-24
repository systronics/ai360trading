"""
title_seo.py v1.0 (2026-10-24) — real search phrases for lesson titles, descriptions, tags and hashtags.

What people actually type is available free: Google / YouTube autocomplete (the same endpoint trending_keywords.py
uses). A "long-tail" phrase is a longer, more specific search ("breakout trading strategy", "swing trading kya hai")
— fewer people search it than "trading", but the viewer knows exactly what they want and far fewer videos compete.

This module (1) picks the best long-tail phrases for a lesson from its seed topics, (2) adds the phrase to the
YouTube title only when the title does not already say it and it fits in 100 characters, (3) leads the description
with it (search reads the first words most), (4) adds it to the tags, (5) builds the 3 hashtags YouTube shows above
the title (topic first, then discovery terms), and (6) refreshes `_data/lesson_ideas.json` — a list of real search
phrases to choose the NEXT lessons from.

Honesty rules: a phrase is used only if it contains a whole-word seed of that lesson (so it matches the content);
phrases that imply things we do not provide (pdf, book, reddit, course, free download) are dropped. Everything is
fail-open: on any error the lesson uses its original title/description/tags unchanged.
"""
import json
import re
import time
from collections import Counter
from pathlib import Path

try:
    import trending_keywords as _tk
except Exception:                      # pragma: no cover
    _tk = None

SEEDS = {
    # `seeds` are what we ask autocomplete about; `allow` are the ONLY phrases that may go public — curated
    # because raw autocomplete is noisy (prop-firm, colour-trading, broker names) and a title must match the
    # lesson. A phrase is used only if live autocomplete still shows it (proof people search it).
    "rc01": {"en": ["breakout trading", "breakout trading strategy"],
             "hi": ["breakout trading kaise kare"],
             "allow": {"en": ["breakout trading strategy", "breakout stocks strategy"],
                       "hi": ["breakout trading kaise kare"]},
             "tag": "BreakoutTrading"},
    "rm01": {"en": ["how to deal with trading losses", "how to get over trading losses"],
             "hi": ["trading loss recover kaise kare"],
             "allow": {"en": ["how to deal with trading losses", "how to get over trading losses"],
                       "hi": ["trading loss recover kaise kare"]},
             "tag": "RiskManagement"},
    "rs01": {"en": ["buy the dip", "buy the dip strategy"],
             "hi": ["dip me stock kharidna"],
             "allow": {"en": ["buy the dip strategy", "buy the dip stocks meaning"], "hi": []},
             "tag": "BuyTheDip"},
    "au01": {"en": ["does swing trading work", "swing trading strategy"],
             "hi": ["swing trading kaise kare"],
             "allow": {"en": ["does swing trading work", "swing trading strategy backtest"],
                       "hi": ["swing trading kaise kare"]},
             "tag": "SwingTrading"},
}
_DROP = {"pdf", "book", "books", "reddit", "course", "courses", "download", "free", "youtube", "ebook",
         "amazon", "telegram", "whatsapp", "app", "software", "crack", "signals", "signal", "tips", "calls",
         # time-bound / pick-seeking queries: our lessons teach a rule, they do NOT promise tomorrow's stocks
         "today", "tomorrow", "recommendation", "recommendations", "prediction", "predictions", "live",
         "best", "target", "targets", "buy", "sell", "now", "tonight", "week", "jackpot", "guaranteed",
         "screener", "scanner", "journal", "review",
         # other languages / other markets that do not match our lesson
         "telugu", "tamil", "malayalam", "kannada", "marathi", "gujarati", "bengali", "urdu", "punjabi",
         "forex", "crypto", "bitcoin", "options", "futures", "mt4", "mt5",
         "quotex", "binomo", "olymp", "pocket", "iq", "binary", "nse", "bse"}
# learning-intent words: phrases containing these rank first
_LEARN = {"strategy", "strategies", "explained", "beginners", "beginner", "meaning", "rules", "rule", "guide",
          "tutorial", "kaise", "kya", "hai", "hota", "example", "examples", "works", "work", "basics", "hindi"}
# idea seeds for choosing future lessons
IDEA_SEEDS = ["swing trading for beginners", "how to find breakout stocks", "what is stop loss", "position sizing",
              "how to read candlestick charts", "rsi indicator explained", "moving average strategy",
              "support and resistance trading", "volume analysis trading", "trading psychology",
              "swing trading kya hai", "stock market basics kaise seekhe"]
IDEAS_FILE = Path("_data/lesson_ideas.json")


def _phrases_for(seeds, lang="en"):
    """Ranked, filtered autocomplete phrases (best first) for a list of seed queries. [] on failure."""
    if _tk is None:
        return []
    counter = Counter()
    for seed in seeds:
        seed_words = [w for w in re.split(r"\s+", seed.lower()) if w]
        for yt in (False, True):
            for sug in _tk._suggest(seed, youtube=yt):
                s = sug.strip().lower()
                words = s.split()
                if len(words) < 2 or s == seed.lower():
                    continue
                if any(w in _DROP and w not in seed_words for w in words):
                    continue
                if lang == "en" and "hindi" in words:
                    continue
                if any(w in getattr(_tk, "_OFFTOPIC", set()) for w in words):
                    continue
                # must still be about the seed (all seed words present)
                if not all(w in words for w in seed_words[:2]):
                    continue
                counter[s] += 1
            time.sleep(0.3)
    # prefer phrases that appear more often, then 3-5 words (specific but still searchable)
    ranked = sorted(counter, key=lambda p: (-sum(1 for w in p.split() if w in _LEARN) > 0 and 0 or 1,
                                            -counter[p], abs(len(p.split()) - 4)))
    return ranked


def long_tail(lid, lang, n=3):
    """Curated long-tail phrases for a lesson/language that live autocomplete still shows, or []."""
    try:
        cfg = SEEDS.get(lid) or {}
        key = "hi" if lang == "hi" else "en"
        seeds, allow = cfg.get(key, []), (cfg.get("allow") or {}).get(key, [])
        if not seeds or not allow:
            return []
        live = []
        for seed in seeds:
            for yt in (False, True):
                live += [x.strip().lower() for x in (_tk._suggest(seed, youtube=yt) if _tk else [])]
            time.sleep(0.3)
        seen = [a for a in allow if any(a in x for x in live)]
        return seen[:n]
    except Exception as e:
        print(f"[TITLE_SEO] long_tail failed (fail-open): {e}")
        return []


def _overlap(title, phrase):
    tw = set(re.findall(r"[a-z0-9]+", title.lower()))
    pw = re.findall(r"[a-z0-9]+", phrase.lower())
    return (sum(1 for w in pw if w in tw) / len(pw)) if pw else 1.0


def hashtags(lid):
    """3 hashtags YouTube shows above the title: topic first, then discovery terms."""
    tag = (SEEDS.get(lid) or {}).get("tag")
    base = ["SwingTrading", "StockMarketIndia", "Nifty50"]
    first = [tag] if tag else []
    out = list(dict.fromkeys(first + base))[:4]
    return " ".join("#" + t for t in out)


def apply(lid, lang, title, desc, tags):
    """Return (title, desc, tags, phrases). Any failure returns the inputs unchanged."""
    try:
        phrases = long_tail(lid, lang, 3)
        new_title, new_desc, new_tags = title, desc, list(tags)
        if phrases:
            best = phrases[0]
            ascii_best = re.sub(r"[^\x00-\x7F]", "", best).strip()
            # title: add the phrase only when the title does not already cover it and it fits
            if ascii_best and _overlap(title, ascii_best) < 0.6:
                cand = f"{title} | {ascii_best.title()}"
                if len(cand) <= 100:
                    new_title = cand
            # description: lead with the phrase (search reads the first words most)
            new_desc = f"{best.capitalize()}: {desc}"
            # tags: real phrases first (ASCII only)
            ascii_tags = [re.sub(r"[^\x00-\x7F]", "", p).strip() for p in phrases]
            new_tags = [t for t in ascii_tags if t] + [t for t in new_tags if t not in ascii_tags]
        tagline = hashtags(lid)
        if tagline and tagline not in new_desc:
            new_desc = f"{new_desc}\n\n{tagline}"
        return new_title, new_desc, new_tags, phrases
    except Exception as e:
        print(f"[TITLE_SEO] apply failed (fail-open): {e}")
        return title, desc, list(tags), []


def refresh_ideas():
    """Write real search phrases (per idea seed) to _data/lesson_ideas.json to choose future lessons from."""
    try:
        data = {}
        for seed in IDEA_SEEDS:
            ph = _phrases_for([seed])[:6]
            if ph:
                data[seed] = ph
        if data:
            IDEAS_FILE.parent.mkdir(parents=True, exist_ok=True)
            IDEAS_FILE.write_text(json.dumps({"updated": time.strftime("%Y-%m-%d"), "ideas": data}, indent=1,
                                             ensure_ascii=False), encoding="utf-8")
            print(f"[TITLE_SEO] wrote {len(data)} idea groups to {IDEAS_FILE}")
        return data
    except Exception as e:
        print(f"[TITLE_SEO] refresh_ideas failed (fail-open): {e}")
        return {}


if __name__ == "__main__":
    refresh_ideas()
