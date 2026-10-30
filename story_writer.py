"""
story_writer.py v1.0 (2026-10-29) — writes NEW evergreen story scripts automatically when the queue runs low.

WHY
  Owner: "when the queue is empty, don't ask me to ask Claude — do it automatically", and: no repetition.
  The 10 hand-written stories (emotion_story.py + story_real.py) last ~5 weeks. This module tops the queue up
  with new ones, written by the free AI chain (ai_client: Groq -> Gemini -> Cloudflare), into `_data/stories_extra.json`,
  which story_real.py loads at start-up.

HOW REPETITION IS PREVENTED
  * A hand-picked THEME BANK (each theme is a different trader mistake). A theme is used once, ever; the AI never picks
    its own topic, so it cannot drift back to "fear / greed / revenge".
  * Every generated story must pass `validate()` or it is thrown away (never published half-checked).

SAFETY / DOCTRINE (same rules as the hand-written stories)
  * No digits (except the brand), no personal names, no stock names, no entry/stop/target, no hype or advice words.
  * 5 scenes, caption per scene, 5 stock-footage search phrases (hands / screens / silhouettes / city — not faces).
  * Fully fail-open: any problem = nothing is added, the run reports it, the old queue keeps working.
  * Visible in the YouTube upload as PRIVATE-first (publishAt 19:30 IST), so the owner can cancel in Studio.

Usage:  python story_writer.py --n 3 [--print]        (writes _data/stories_extra.json unless --print)
"""
import re
import sys
import json
import argparse
from pathlib import Path

EXTRA_FILE = Path("_data/stories_extra.json")

ACCENTS = {"red": (235, 70, 70), "gold": (255, 200, 50), "green": (0, 210, 100), "blue": (90, 160, 255),
           "orange": (255, 140, 40), "purple": (170, 110, 255), "pink": (255, 100, 170), "teal": (0, 200, 190)}

# One theme = one trader mistake. Never reused. Add more here any time; the writer works through them in order.
THEMES = [
    ("winstreak", "overconfidence after a winning streak: he started to feel he could not lose and stopped following his rules"),
    ("riskreward", "risking a lot to win a little: his possible loss on every trade was bigger than his possible gain"),
    ("checking", "checking the account every minute: constant watching made every small move feel like an emergency"),
    ("headlines", "trading on news headlines: he bought and sold on every headline and was always one step late"),
    ("comparing", "comparing himself with other traders' profits online: it pushed him into bigger and riskier trades"),
    ("nojournal", "never keeping a trade journal: he repeated the same mistake for years without noticing the pattern"),
    ("holdlosers", "holding a loser and hoping it returns: he sold his small winners fast and kept the losers"),
    ("tired", "trading while tired or angry: the worst decisions came after a bad night or a bad day"),
    ("noplan", "having no plan before the trade: he decided his exit only after the price had already moved"),
    ("bigevent", "taking a big position before a big event: one result announcement decided his whole month"),
    ("movestop", "moving the stop-loss further away: each time the price came close he gave the trade more room"),
    ("strategyhop", "changing strategy after every two losses: he never stayed with any method long enough to learn it"),
    ("againsttrend", "fighting the trend: he kept trying to catch the exact top in a strong uptrend"),
    ("pennystock", "chasing tiny low-priced stocks for quick money: thin trading made it easy to get in and hard to get out"),
    ("rentmoney", "trading with money needed for rent and bills: fear of losing it made every decision worse"),
    ("copycat", "copying a famous trader without understanding the plan: the same trade did not fit his capital or his nerves"),
    ("quitearly", "quitting right before his method started working: a normal losing stretch felt like proof it was broken"),
    ("paperreal", "great results on paper, shaky hands with real money: the fear of real loss changed how he traded"),
    ("noexit", "knowing when to buy but never when to sell: he watched a good profit slip away with no exit rule"),
    ("overlearn", "watching endless videos but never practising: more information did not become a better trade"),
]

SYSTEM = ("You write very short, fictional, emotional stories about trader mistakes for a finance EDUCATION channel with a "
          "worldwide audience. Plain English. Never give advice to buy or sell anything, never mention a stock name, never "
          "use a person's name (the story is about 'he'), never use digits. Output ONLY the JSON requested.")

BAD_WORDS = ("guarantee", "sure shot", "surefire", "risk-free", "risk free", "buy now", "sell now", "accumulate now",
             "get rich", "double your money", "100%", "profit assured", "tip", "multibagger", "target price")
BRAND = re.compile(r"AI360Trading", re.I)


def _example():
    return {
        "title": "He Sold The Exact Bottom",
        "tag": "FEAR",
        "accent": "red",
        "desc": "Fear makes traders sell at the worst price. Decide your stop-loss before the trade, not during the panic.",
        "thumb_text": "SOLD THE BOTTOM",
        "seo_phrase": "why traders sell at the bottom",
        "topic_tag": "TradingPsychology",
        "narration": [
            "It was the middle of the night. He couldn't sleep. The screen was nothing but red.",
            "The market kept falling, and so did his nerve. He thought, I can't take any more.",
            "He sold everything. On the exact day the price hit its lowest point.",
            "A few days later, the market started climbing again. And he could only watch.",
            "The lesson: a decision made in fear is often the most expensive one. Decide your stop-loss before you trade. Follow AI360Trading.",
        ],
        "narration_hi": [
            "रात के दो बजे थे। उसकी आँखों में नींद नहीं थी। स्क्रीन पर बस लाल रंग।",
            "मार्केट गिरता गया, और उसका डर बढ़ता गया। उसने सोचा, अब और नहीं सह सकता।",
            "उसने सब बेच दिया। ठीक उसी दिन, जब भाव सबसे नीचे था।",
            "कुछ दिन बाद मार्केट वापस ऊपर चढ़ने लगा। और वह बस देखता रह गया।",
            "सबक यह है: डर में लिया गया फ़ैसला अक्सर सबसे महंगा होता है। स्टॉप लॉस पहले से तय करो। AI360Trading को फ़ॉलो करो।",
        ],
        "captions": ["2 AM. EVERYTHING IS RED.", "FEAR TAKES OVER", "HE SOLD THE BOTTOM", "THEN IT RECOVERED", "DECIDE BEFORE YOU PANIC"],
        "queries": ["man silhouette alone dark room night laptop glow", "hand trembling over computer mouse red screen",
                    "finger pressing laptop keyboard", "sunrise through window city morning", "hand writing in notebook morning coffee"],
    }


def build_prompt(theme_key, theme_text):
    return (
        f"Write ONE new short story. Mistake to dramatise: {theme_text}.\n"
        "Rules: five scenes; the hero is only 'he'; past tense; emotional but simple; no digits in narration or description (spell numbers as words); a small story count such as '3 losses' or '12 days' (at most two digits, no % or currency) is allowed ONLY in the title, thumb_text and captions; no names; "
        "no stock names; no advice to buy or sell; scene 5 must start with 'The lesson:' and end with 'Follow AI360Trading.'; "
        "each narration is at most 22 words (scene 5 at most 32); each caption is 2-5 UPPERCASE words, at most 32 characters; "
        "'queries' are 5 stock-video search phrases (3-9 words) showing hands, screens, charts, silhouettes, city or objects, NOT faces; "
        "'seo_phrase' is a 3-7 word lowercase phrase people really search on YouTube about this mistake; "
        "'accent' is one of: red, gold, green, blue, orange, purple, pink, teal; 'tag' is ONE uppercase word up to 12 letters; "
        "'thumb_text' is 2-4 UPPERCASE words; 'topic_tag' is one CamelCase hashtag word; 'title' is a hook of at most 60 characters.\n"
        "'narration_hi' is the SAME five scenes in simple spoken Hindi written in Devanagari (no digits, no English words except AI360Trading in scene 5, same meaning as narration). "
        "Return JSON with exactly these keys: title, tag, accent, desc, thumb_text, seo_phrase, topic_tag, narration (5 strings), "
        "narration_hi (5 strings), captions (5 strings), queries (5 strings). Example of the style and shape:\n"
        + json.dumps(_example(), ensure_ascii=False)
    )


def _count_ok(t):
    """Small story counts (e.g. '12 days', '3 losses') are evergreen and allowed in title/thumb_text/captions only."""
    t = BRAND.sub("", t)
    if re.search(r"[%$\u20b9,]", t):
        return False
    return all(len(n) <= 2 for n in re.findall(r"\d+", t))


def validate(s):
    """Return (ok, reason)."""
    try:
        for k in ("title", "tag", "accent", "desc", "thumb_text", "seo_phrase", "topic_tag", "narration", "narration_hi", "captions", "queries"):
            if k not in s:
                return False, f"missing {k}"
        for k in ("narration", "narration_hi", "captions", "queries"):
            if not isinstance(s[k], list) or len(s[k]) != 5 or not all(isinstance(x, str) and x.strip() for x in s[k]):
                return False, f"{k} must be 5 non-empty strings"
        if s["accent"] not in ACCENTS:
            return False, "bad accent"
        if not (2 <= len(s["tag"]) <= 12) or " " in s["tag"].strip():
            return False, "bad tag"
        if not re.fullmatch(r"[A-Za-z]{3,30}", s["topic_tag"]):
            return False, "bad topic_tag"
        if len(s["title"]) > 60 or len(s["title"]) < 8:
            return False, "title length"
        for t in [s["title"], s["thumb_text"]] + s["captions"]:
            if not _count_ok(t):
                return False, f"number not allowed in: {t[:50]!r}"
        for t in s["narration_hi"]:
            if not re.search(r"[\u0900-\u097F]", t):
                return False, "narration_hi must be Devanagari"
            if re.search(r"[0-9\u0966-\u096F]", BRAND.sub("", t)):
                return False, f"digit in Hindi: {t[:40]!r}"
            if not (4 <= len(t.split()) <= 34):
                return False, "narration_hi length"
        if "AI360Trading" not in s["narration_hi"][4]:
            return False, "narration_hi scene 5 must mention AI360Trading"
        everything = [s["title"], s["desc"], s["thumb_text"], s["seo_phrase"]] + s["narration"] + s["captions"]
        for t in everything:
            if t in s["captions"] or t in (s["title"], s["thumb_text"]):
                pass
            elif re.search(r"\d", BRAND.sub("", t)):
                return False, f"digit in: {t[:50]!r}"
            low = t.lower()
            for w in BAD_WORDS:
                if w in low:
                    return False, f"banned word {w!r}"
        for i, t in enumerate(s["narration"]):
            n = len(t.split())
            if n < 5 or n > (32 if i == 4 else 24):
                return False, f"narration {i + 1} has {n} words"
        if not s["narration"][4].lower().startswith("the lesson"):
            return False, "scene 5 must start with 'The lesson'"
        if "follow ai360trading" not in s["narration"][4].lower():
            return False, "scene 5 must end with the follow line"
        for c in s["captions"]:
            if len(c) > 34 or c != c.upper():
                return False, f"caption {c!r}"
        if len(s["thumb_text"].split()) not in (2, 3, 4) or s["thumb_text"] != s["thumb_text"].upper():
            return False, "thumb_text"
        for q in s["queries"]:
            if not (2 <= len(q.split()) <= 10) or re.search(r"\b(face|portrait|smiling|crying)\b", q.lower()):
                return False, f"query {q!r}"
        # names: any capitalised word in the middle of a sentence other than I / brand = suspicious
        for t in s["narration"]:
            for m in re.finditer(r"(?<=[a-z,] )([A-Z][a-z]+)", t):
                if m.group(1) not in ("I", "AI360Trading"):
                    return False, f"possible name {m.group(1)!r}"
        return True, ""
    except Exception as e:
        return False, f"validator error {e}"


def _clean(x):
    """Normalise typographic dashes/quotes the AI likes to emit (they can trip TTS and the caption font)."""
    if isinstance(x, str):
        for bad, good in (("‑", "-"), ("‐", "-"), ("–", "-"), ("—", ", "), ("’", "'"), ("‘", "'"),
                          ("“", '"'), ("”", '"'), ("…", "...")):
            x = x.replace(bad, good)
        return x
    if isinstance(x, list):
        return [_clean(i) for i in x]
    if isinstance(x, dict):
        return {k: _clean(v) for k, v in x.items()}
    return x


def load_extra():
    try:
        return json.loads(EXTRA_FILE.read_text(encoding="utf-8")).get("stories", [])
    except Exception:
        return []


def save_extra(stories):
    EXTRA_FILE.parent.mkdir(parents=True, exist_ok=True)
    EXTRA_FILE.write_text(json.dumps({"stories": stories}, indent=1, ensure_ascii=False), encoding="utf-8")


def write_stories(n=3, existing_keys=(), verbose=False):
    """Write up to n new validated stories from unused themes. Returns the list of NEW story dicts (not saved)."""
    from ai_client import ai
    taken = set(existing_keys) | {s["key"] for s in load_extra()}
    out = []
    for key, text in THEMES:
        if len(out) >= n:
            break
        if key in taken:
            continue
        story = None
        for attempt in range(3):
            try:
                data = ai.generate_json(build_prompt(key, text), system_prompt=SYSTEM, content_mode="education", lang="en",
                                        max_tokens=1800) or {}
            except Exception as e:
                print(f"[WRITER] {key} attempt {attempt + 1} AI error: {str(e)[:100]}")
                continue
            data = _clean(data)
            ok, why = validate(data)
            if ok:
                story = data
                break
            print(f"[WRITER] {key} attempt {attempt + 1} rejected: {why}")
        if story:
            story["key"] = key
            story["theme"] = text
            out.append(story)
            if verbose:
                print(json.dumps(story, indent=1, ensure_ascii=False))
    return out


def top_up(n=3, existing_keys=()):
    """Write n stories and save them. Returns the new stories (possibly empty). Never raises."""
    try:
        new = write_stories(n, existing_keys)
        if new:
            save_extra(load_extra() + new)
        return new
    except Exception as e:
        print(f"[WRITER] top-up failed (fail-open): {str(e)[:160]}")
        return []


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--print", action="store_true", help="show the stories, do not save")
    a = ap.parse_args()
    new = write_stories(a.n, verbose=a.print)
    if not a.print and new:
        save_extra(load_extra() + new)
    print(f"[WRITER] {len(new)} new stor{'y' if len(new) == 1 else 'ies'} {'shown' if a.print else 'saved'}")
    sys.exit(0)
