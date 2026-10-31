"""
life_stories.py v1.0 (2026-10-31) — Hindi-first emotional / moral micro-stories (TEST line, NOT wired to the trading channel).

WHY
  Our own YouTube audit (2026-10-31): the best-ever videos on the channel were the retired "life wisdom" Shorts (patience,
  family, values), not trading. Search results say emotional story Shorts are the easiest AI format that holds watch time.
  This module writes such stories with the free AI chain and feeds them to story_real.py (real stock footage + Hindi voice
  for Facebook/Instagram, English edition for YouTube) — only when env LIFE_STORIES=1, and into its OWN file
  (_data/life_extra.json) so they can never leak into the AI360Trading story queue.

RULES (same safety doctrine as story_writer.py)
  * fictional, no names, no digits in narration, no religion/politics/real people, no advice, 5 scenes, footage queries without faces.
  * every story passes validate() or is thrown away.

Usage:  python life_stories.py --n 3 [--print | --save]
"""
import re
import sys
import json
import argparse
from pathlib import Path

LIFE_FILE = Path("_data/life_extra.json")
ACCENTS = {"red": (235, 70, 70), "gold": (255, 200, 50), "green": (0, 210, 100), "blue": (90, 160, 255),
           "orange": (255, 140, 40), "purple": (170, 110, 255), "pink": (255, 100, 170), "teal": (0, 200, 190)}

THEMES = [
    ("maa", "a mother's silent sacrifice: she gave up her own comfort every day so her child could study, and the child understood only years later"),
    ("imaandari", "honesty rewarded: he returned something valuable he found, lost a quick gain, and was trusted with something much bigger later"),
    ("sabr", "patience pays: he kept working quietly while others laughed, and results came only after a long wait"),
    ("chhota", "never judge someone as small: a person everyone ignored turned out to be the one who helped when it mattered"),
    ("mehnat", "hard work has no shortcut: he watched a friend take an easy path that collapsed, while his slow steady path held"),
    ("shukriya", "gratitude: he complained about what he lacked until a small event showed him how much he already had"),
    ("rishte", "forgiveness: two siblings stopped talking over a small quarrel, and one simple sentence mended years of silence"),
    ("waqt", "time over money: a busy father chased money and missed his child growing up, then chose to change"),
    ("galti", "admitting a mistake: he hid an error, it grew bigger, and only honesty fixed it"),
    ("baap", "a father's quiet lesson: he never lectured, he simply showed through his own habits what a good life looks like"),
    ("dost", "a true friend: the friend who stayed when luck ran out mattered more than the many who left"),
    ("wapsi", "comeback: after a big failure he almost quit, then took one small step the next morning, and then another"),
    ("lalach", "greed has a price: he wanted more than he needed and lost the peace he already had"),
    ("madad", "helping without waiting for credit: a small help given quietly came back in an unexpected way"),
    ("ghamand", "pride falls: he looked down on others for his success, and a single setback taught him humility"),
]

SYSTEM = ("You write very short, fictional, emotional moral stories for Indian family audiences in simple spoken Hindi, plus an English "
          "version. Never use a person's name (the story is about 'he', 'she', 'a mother', 'a boy'), never use digits in the narration, "
          "no religion, no politics, no real people, no advice to buy or sell anything. Output ONLY the JSON requested.")
BAD_WORDS = ("guarantee", "sure shot", "buy now", "sell now", "get rich", "double your money", "100%", "multibagger")


def _example():
    return {
        "title": "Maa Ki Aakhri Roti",
        "tag": "MAA", "accent": "pink",
        "desc": "A mother's quiet sacrifice, and the day her child finally understood it.",
        "thumb_text": "MAA KA TYAAG",
        "seo_phrase": "maa ki kahani hindi",
        "topic_tag": "HindiKahani",
        "narration": [
            "Every night she served him the last roti and said she had already eaten.",
            "He believed her. He thought mothers simply did not get hungry.",
            "Years later, he found her old empty steel plate and finally understood.",
            "He sat on the floor and cried like a child, holding that plate.",
            "The lesson: some love is so quiet that we notice it only when it is gone. Thank your parents today. Follow for more stories.",
        ],
        "narration_hi": [
            "हर रात वो उसे आख़िरी रोटी खिला देती थी और कहती थी कि उसने खा लिया।",
            "उसने यक़ीन कर लिया। उसे लगा माँओं को भूख लगती ही नहीं।",
            "सालों बाद उसे उसकी पुरानी ख़ाली थाली मिली, और तब उसे सब समझ आया।",
            "वो फ़र्श पर बैठकर बच्चे की तरह रो पड़ा, उसी थाली को पकड़े हुए।",
            "सीख यह है: कुछ प्यार इतना चुप होता है कि उसकी क़ीमत उसके जाने के बाद पता चलती है। आज अपने माता-पिता का शुक्रिया कहिए। और कहानियों के लिए फ़ॉलो कीजिए।",
        ],
        "captions": ["THE LAST ROTI", "SHE ALWAYS SAID SHE ATE", "THE EMPTY PLATE", "NOW HE UNDERSTOOD", "SAY THANK YOU TODAY"],
        "queries": ["hands serving roti on steel plate", "old steel plate on kitchen shelf", "empty plate on floor close up", "man sitting alone on floor", "hands holding old photograph warm light"],
    }


def build_prompt(key, text):
    return (
        f"Write ONE short moral story. Theme: {text}.\n"
        "Rules: five scenes; no names; past tense; emotional but simple; narration has no digits (spell numbers as words); a small count like "
        "'3 days' is allowed ONLY in title, thumb_text and captions (at most two digits, no % or currency); no religion, politics or real people; "
        "scene 5 must start with 'The lesson:' and end with 'Follow for more stories.'; "
        "each English narration is at most 22 words (scene 5 at most 32); each caption is 2-5 UPPERCASE words, at most 32 characters; "
        "'queries' are 5 stock-video search phrases (3-9 words) showing hands, objects, nature, city, homes or silhouettes, NOT faces; "
        "'title' is a hook in Roman-script Hindi (Hinglish) of at most 60 characters, 'thumb_text' is 2-4 UPPERCASE Hinglish words; "
        "'seo_phrase' is a 3-7 word lowercase Hinglish phrase people search for on YouTube; "
        "'accent' is one of: red, gold, green, blue, orange, purple, pink, teal; 'tag' is ONE uppercase Roman word up to 12 letters; "
        "'topic_tag' is one CamelCase hashtag word; 'narration_hi' is the SAME five scenes in simple spoken Hindi in Devanagari "
        "(no digits, same meaning, last scene ends by asking to follow for more stories).\n"
        "Return JSON with exactly these keys: title, tag, accent, desc, thumb_text, seo_phrase, topic_tag, narration (5), narration_hi (5), "
        "captions (5), queries (5). Example of the shape and style:\n" + json.dumps(_example(), ensure_ascii=False))


def _count_ok(t):
    if re.search(r"[%$₹,]", t):
        return False
    return all(len(n) <= 2 for n in re.findall(r"\d+", t))


def validate(s):
    try:
        for k in ("title", "tag", "accent", "desc", "thumb_text", "seo_phrase", "topic_tag", "narration", "narration_hi", "captions", "queries"):
            if k not in s:
                return False, f"missing {k}"
        for k in ("narration", "narration_hi", "captions", "queries"):
            if not isinstance(s[k], list) or len(s[k]) != 5 or not all(isinstance(x, str) and x.strip() for x in s[k]):
                return False, f"{k} must be 5 non-empty strings"
        if s["accent"] not in ACCENTS or not (2 <= len(s["tag"]) <= 12) or " " in s["tag"].strip():
            return False, "bad accent/tag"
        if not re.fullmatch(r"[A-Za-z]{3,30}", s["topic_tag"]):
            return False, "bad topic_tag"
        if not (8 <= len(s["title"]) <= 60):
            return False, "title length"
        for t in [s["title"], s["thumb_text"]] + s["captions"]:
            if not _count_ok(t):
                return False, f"number not allowed in {t[:40]!r}"
        for t in s["narration_hi"]:
            if not re.search(r"[ऀ-ॿ]", t):
                return False, "narration_hi must be Devanagari"
            if re.search(r"[0-9०-९]", t):
                return False, f"digit in Hindi {t[:30]!r}"
            if not (4 <= len(t.split()) <= 40):
                return False, "narration_hi length"
        for t in [s["desc"], s["seo_phrase"]] + s["narration"]:
            if re.search(r"\d", t):
                return False, f"digit in {t[:40]!r}"
            if any(w in t.lower() for w in BAD_WORDS):
                return False, "banned word"
        for i, t in enumerate(s["narration"]):
            n = len(t.split())
            if n < 5 or n > (32 if i == 4 else 24):
                return False, f"narration {i + 1} has {n} words"
        if not s["narration"][4].lower().startswith("the lesson") or "follow" not in s["narration"][4].lower():
            return False, "scene 5 must start 'The lesson' and ask to follow"
        for c in s["captions"]:
            if len(c) > 34 or c != c.upper():
                return False, f"caption {c!r}"
        if len(s["thumb_text"].split()) not in (2, 3, 4) or s["thumb_text"] != s["thumb_text"].upper():
            return False, "thumb_text"
        for q in s["queries"]:
            if not (2 <= len(q.split()) <= 10) or re.search(r"\b(face|portrait|smiling|crying)\b", q.lower()):
                return False, f"query {q!r}"
        for t in s["narration"]:
            for m in re.finditer(r"(?<=[a-z,] )([A-Z][a-z]+)", t):
                if m.group(1) != "I":
                    return False, f"possible name {m.group(1)!r}"
        return True, ""
    except Exception as e:
        return False, f"validator error {e}"


def _clean(x):
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


def load():
    try:
        return json.loads(LIFE_FILE.read_text(encoding="utf-8")).get("stories", [])
    except Exception:
        return []


def save(stories):
    LIFE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LIFE_FILE.write_text(json.dumps({"stories": stories}, indent=1, ensure_ascii=False), encoding="utf-8")


def write(n=3, verbose=False):
    from ai_client import ai
    taken = {s["key"] for s in load()}
    out = []
    for key, text in THEMES:
        if len(out) >= n:
            break
        k = "life_" + key
        if k in taken:
            continue
        story = None
        for attempt in range(3):
            try:
                data = ai.generate_json(build_prompt(key, text), system_prompt=SYSTEM, content_mode="education", lang="hi", max_tokens=2200) or {}
            except Exception as e:
                print(f"[LIFE] {key} attempt {attempt + 1} AI error: {str(e)[:100]}")
                continue
            data = _clean(data)
            ok, why = validate(data)
            if ok:
                story = data
                break
            print(f"[LIFE] {key} attempt {attempt + 1} rejected: {why}")
        if story:
            story["key"], story["theme"], story["series"] = k, text, "life"
            out.append(story)
            if verbose:
                print(json.dumps(story, indent=1, ensure_ascii=False))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--print", action="store_true")
    ap.add_argument("--save", action="store_true")
    a = ap.parse_args()
    new = write(a.n, verbose=a.print)
    if a.save and new:
        save(load() + new)
    print(f"[LIFE] {len(new)} story/stories {'saved' if a.save else 'shown'}: {[s['key'] for s in new]}")
    sys.exit(0)
