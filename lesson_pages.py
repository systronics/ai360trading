"""
lesson_pages.py v1.0 (2026-11-15 NEW) - one evergreen WEBSITE page per weekly trading lesson (the long video), for search (SEO) and as a real link target: the full English transcript
(the lesson's own scene texts, no AI call), the embedded YouTube video, the one-line 'Rule', a Hindi-version link when a Hindi edition exists, share links (WhatsApp / Telegram / Facebook),
the not-advice line and a hub `/trading-lessons/` fed by `_data/lesson_pages.json` (Liquid loop, no per-lesson edit). Pages are created ONLY for lessons that have a published-or-scheduled
English video in `_data/lessons_done.json` AND a PURE builder (no network: rm01, rm02, rm03, rm04, sw01, ct01, sv01); lessons whose builder needs live market data are skipped.
Every transcript is unique to its lesson; VideoObject JSON-LD uses the real video id and publish time. Idempotent, fail-open, no network, no secrets.
USAGE: python lesson_pages.py   |   python lesson_pages.py --dry
"""
import html
import json
import re
import sys
import urllib.parse
from pathlib import Path

SITE = "https://ai360trading.in"
DONE = Path("_data/lessons_done.json")
PURE = ("rm01", "rm02", "rm03", "rm04", "sw01", "ct01", "sv01")


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:70].rstrip("-")


def page_url(slug):
    return f"{SITE}/trading-lessons/{slug}/"


def english_video(rec):
    for ed in ("us-en", "in-en"):
        v = (rec or {}).get(ed, {})
        if v.get("video"):
            return v["video"], v.get("publish_at", "")
    return None, ""


def render(pack, video, publish_at, hindi_video=None):
    title = pack["title"]["en"]
    scenes = [s["text"]["en"].strip() for s in pack["scenes"]]
    text = " ".join(scenes) + title
    if not scenes or not video or any(x in text for x in ("{{", "{%", "}}", "%}")):
        return None
    slug = slugify(title)
    url = page_url(slug)
    desc = (pack.get("desc", {}).get("en") or scenes[0])[:155].strip()
    rule = ""
    for sc in scenes:
        m = re.search(r"Rule:[^.]*\.", sc)
        if m:
            rule = m.group(0)
    fm = ["---", "layout: default", f"title: {json.dumps(title + ' | AI360Trading Lessons', ensure_ascii=False)}",
          f"description: {json.dumps(desc, ensure_ascii=False)}", f"permalink: /trading-lessons/{slug}/", f"canonical: {url}",
          f"meta-og:title: {json.dumps(title, ensure_ascii=False)}", f"meta-og:description: {json.dumps(desc, ensure_ascii=False)}",
          f"meta-og:image: https://i.ytimg.com/vi/{video}/hqdefault.jpg", "---", ""]
    ld = {"@context": "https://schema.org", "@type": "VideoObject", "name": title, "description": desc,
          "thumbnailUrl": f"https://i.ytimg.com/vi/{video}/hqdefault.jpg", "uploadDate": publish_at,
          "embedUrl": f"https://www.youtube-nocookie.com/embed/{video}", "inLanguage": "en"}
    paras = "\n".join(f"  <p>{html.escape(s)}</p>" for s in scenes)
    q_url = urllib.parse.quote(url, safe="")
    share = (f'<a href="https://wa.me/?text={urllib.parse.quote(title + " " + url, safe="")}" rel="noopener nofollow" target="_blank">WhatsApp</a> &middot; '
             f'<a href="https://t.me/share/url?url={q_url}&amp;text={urllib.parse.quote(title, safe="")}" rel="noopener nofollow" target="_blank">Telegram</a> &middot; '
             f'<a href="https://www.facebook.com/sharer/sharer.php?u={q_url}" rel="noopener nofollow" target="_blank">Facebook</a>')
    rule_html = f'  <div class="ls-rule"><strong>The rule to remember</strong><br>{html.escape(rule)}</div>\n' if rule else ""
    hi_html = (f'  <p class="ls-small">Hindi mein dekhein: <a href="https://www.youtube.com/watch?v={hindi_video}" rel="noopener" target="_blank">AI360Trading Hindi lesson</a></p>\n'
               if hindi_video else "")
    body = f"""<style>
  .ls-wrap{{max-width:760px;margin:0 auto;padding:0 4px}}
  .ls-wrap h1{{font-size:26px;font-weight:900;line-height:1.3;color:#1e293b;margin:6px 0 10px}}
  .ls-wrap p{{font-size:16px;line-height:1.75;color:#334155}}
  .ls-vid{{position:relative;padding-top:56.25%;margin:14px 0;border-radius:12px;overflow:hidden;background:#000}}
  .ls-vid iframe{{position:absolute;inset:0;width:100%;height:100%;border:0}}
  .ls-rule{{background:#ecfdf5;border:1px solid #a7f3d0;border-radius:12px;padding:14px 16px;margin:18px 0;color:#065f46;font-size:15px;line-height:1.6}}
  .ls-note{{background:#fffbeb;border:1px solid #fde68a;border-radius:12px;padding:12px 15px;font-size:13px;color:#78500a;line-height:1.6;margin:18px 0}}
  .ls-small{{font-size:13px;color:#64748b;line-height:1.6}}
</style>
<div class="ls-wrap">
  <h1>{html.escape(title)}</h1>
  <div class="ls-vid"><iframe src="https://www.youtube-nocookie.com/embed/{video}" title="{html.escape(title)}" loading="lazy" allowfullscreen></iframe></div>
{rule_html}  <h2 style="font-size:19px;margin:18px 0 6px">The lesson, in words</h2>
{paras}
  <div class="ls-note">Education only, not investment advice. AI360Trading is not a SEBI-registered adviser. Numbers come from our own past-data tests and paper results; they carry limits and do not promise future returns. This lesson was prepared with AI assistance and the video uses a synthetic voice.</div>
{hi_html}  <p class="ls-small"><strong>Know a trader who should see this?</strong> {share}</p>
  <p class="ls-small"><a href="/trading-lessons/">More weekly trading lessons</a> &middot; <a href="https://t.me/ai360trading" rel="noopener" target="_blank">Free Telegram updates</a></p>
</div>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
"""
    return "\n".join(fm) + body, {"slug": slug, "title": title, "video": video, "date": publish_at[:10]}


def build_all(done_path=DONE, out_dir="_pages", data_path="_data/lesson_pages.json", dry=False):
    try:
        done = json.loads(Path(done_path).read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[LESSON-PAGES] no done-list ({str(e)[:60]}), nothing to do")
        return 0
    import lesson_builders as B
    entries, wrote = [], 0
    for lid in PURE:
        rec = done.get(lid)
        vid, when = english_video(rec)
        if not vid or lid not in B.BUILDERS:
            continue
        try:
            pack = B.BUILDERS[lid]("us")
            r = render(pack, vid, when, (rec or {}).get("in-hi", {}).get("video"))
        except Exception as e:
            print(f"[LESSON-PAGES] {lid} skipped: {str(e)[:60]}")
            continue
        if not r:
            continue
        text, entry = r
        entries.append(entry)
        p = Path(out_dir) / f"ls-{entry['slug']}.html"
        if dry:
            print(f"[LESSON-PAGES] would write {p} ({len(text)} chars)")
            continue
        if not p.exists() or p.read_text(encoding="utf-8") != text:
            p.write_text(text, encoding="utf-8")
            wrote += 1
    entries.sort(key=lambda e: e["date"], reverse=True)
    if not dry:
        new = json.dumps(entries, indent=1, ensure_ascii=False) + "\n"
        pd = Path(data_path)
        if not pd.exists() or pd.read_text(encoding="utf-8") != new:
            pd.write_text(new, encoding="utf-8")
    print(f"[LESSON-PAGES] {len(entries)} pages, {wrote} written/updated")
    return 0


if __name__ == "__main__":
    sys.exit(build_all(dry="--dry" in sys.argv))
