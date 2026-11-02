"""fix_descriptions.py (one-off, 2026-11-02): replace the generic meta description ('... Insights for US, UK, India and Brazil investors.') of
existing posts with one built from the post's own first paragraph (seo_desc.from_body), and turn the LLM artifact 'SandP' into 'S&P' everywhere
in a post. Touches only: front-matter description/excerpt lines, the JSON-LD Article description line, and the 'SandP' spelling. Never URLs/permalinks.
Usage: python fix_descriptions.py            (dry-run, prints samples)
       python fix_descriptions.py --write"""
import re
import sys
import json
import glob
import seo_desc

WRITE = "--write" in sys.argv
GENERIC = "for US, UK, India and Brazil investor"
changed_desc = changed_sandp = skipped = 0
samples = []
for path in sorted(glob.glob("_posts/*.md")):
    raw = open(path, encoding="utf-8", newline="").read()
    txt = raw
    if "SandP" in txt:
        txt = txt.replace("SandP", "S&P")
        changed_sandp += 1
    m = re.match(r"(---\r?\n)(.*?)(\r?\n---\r?\n)(.*)\Z", txt, flags=re.S)
    if m and GENERIC in m.group(2):
        fm, body = m.group(2), m.group(4)
        t = re.search(r'^title:\s*"(.*)"\s*$', fm, flags=re.M)
        new = seo_desc.from_body(body, t.group(1) if t else "")
        if new:
            new = new.replace('"', "'")
            fm2 = re.sub(r'^description:.*$', lambda _: f'description: "{new}"', fm, count=1, flags=re.M)
            fm2 = re.sub(r'^excerpt:.*$', lambda _: f'excerpt: "{new}"', fm2, count=1, flags=re.M)
            body2 = re.sub(r'^(\s*"description": ).*(,?)\s*$', lambda mm: mm.group(1) + json.dumps(new) + ",", body, count=1, flags=re.M)
            txt = m.group(1) + fm2 + m.group(3) + body2
            changed_desc += 1
            if len(samples) < 6:
                samples.append((path.split("/")[-1][:60], new))
        else:
            skipped += 1
    if WRITE and txt != raw:
        open(path, "w", encoding="utf-8", newline="").write(txt)
print(f"descriptions rewritten: {changed_desc} | could not build one (left as is): {skipped} | posts with SandP fixed: {changed_sandp} | mode={'WRITE' if WRITE else 'DRY-RUN'}")
for p, d in samples:
    print(f"\n{p}\n  -> {d}  ({len(d)} chars)")
