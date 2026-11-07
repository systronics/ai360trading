"""
tech_keywords.py v1.0 (2026-11-07) - what people REALLY type on YouTube/Google for the AI360 Technology topics (free autocomplete), saved to _data/tech_keywords.json.
Owner: 'are the topics what people check daily / ask AI?'. Autocomplete suggestions are real searches (the same free endpoint trending_keywords.py uses). Used to (1) choose the next topics, (2) add the most-typed phrases
to a Short's tags. Read-only, fail-open (a failed request just skips that seed). USAGE: python tech_keywords.py
"""
import json
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

OUT = Path("_data/tech_keywords.json")
SEEDS = ["phone garam kyun hota hai", "phone hang kyun hota hai", "wifi slow kyun chalta hai", "laptop slow kaise theek kare", "otp scam", "upi fraud se kaise bache", "digital arrest scam",
         "phone ki battery jaldi khatam", "phone storage full kaise khali kare", "deleted photos wapas kaise laye", "pendrive format kaise kare", "phone charge karne ka sahi tarika",
         "ai se paise kaise kamaye", "chatgpt kaise use kare", "whatsapp hack kaise pata kare", "fake call kaise pehchane", "mobile virus kaise hataye", "laptop battery jaldi khatam",
         "internet speed kaise badhaye", "pc on nahi ho raha", "ssd vs hdd", "phone me ads kyun aate hai", "sim swap fraud", "aadhaar se fraud"]


def suggest(q, kind="yt"):
    url = "https://suggestqueries.google.com/complete/search?client=firefox&" + ("ds=yt&" if kind == "yt" else "") + "hl=hi&q=" + quote(q)
    with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=15) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))[1]


def main():
    out = {}
    for s in SEEDS:
        try:
            out[s] = {"youtube": suggest(s, "yt")[:8], "google": suggest(s, "g")[:6]}
        except Exception as e:
            print(f"[KW] {s}: skipped ({str(e)[:60]})")
        time.sleep(0.4)
    if out:
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for s, v in list(out.items())[:24]:
        print(f"{s:38} -> " + " | ".join(v["youtube"][:4]))
    print(f"[KW] {len(out)} seeds saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
