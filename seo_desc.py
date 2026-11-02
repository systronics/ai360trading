"""seo_desc.py v1.0 (2026-11-02) — builds a real, page-specific meta description from an article's own first paragraph.
Used by generate_articles.py when the AI did not return a usable META_DESCRIPTION line (the old fallback was the same sentence on every page:
'Insights for US, UK, India and Brazil investors.') and by the one-off bulk fix `fix_descriptions.py`. Pure text, fail-open (returns '' on trouble)."""
import re

MIN_LEN, MAX_LEN = 90, 155


def _plain(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", s)          # markdown links/images -> text
    s = re.sub(r"[*_`>#|]+", " ", s)
    s = s.replace("SandP", "S&P")
    return re.sub(r"\s+", " ", s).strip()


def from_body(body, title=""):
    """First substantive paragraph that is not just the title repeated, cut at a sentence end (or word boundary) within MAX_LEN."""
    try:
        body = re.sub(r"<script.*?</script>", " ", body, flags=re.S)
        body = chr(10).join(l for l in body.split(chr(10)) if not l.lstrip().startswith("#"))
        t = _plain(title).lower()
        for para in re.split(r"\n\s*\n|\n(?=#)", body):
            p = _plain(para)
            if len(p) < 80 or p.startswith(("Disclaimer", "Not investment", "Read more")):
                continue
            if t and t[:40] in p.lower()[:140]:                # opening that only restates the title tells Google nothing new
                continue
            if len(p) <= MAX_LEN:
                return p
            sents = re.split(r"(?<=[.!?])\s+", p)
            out = ""
            for x in sents:
                if len(out) + len(x) + (1 if out else 0) > MAX_LEN:
                    break
                out = (out + " " + x).strip()
            if len(out) >= 70:
                return out
            cut = p[:MAX_LEN]                                   # first sentence alone is too long: cut at the last comma, else last word
            k = cut.rfind(",")
            cut = cut[:k] if k >= 70 else cut[:MAX_LEN - 1].rsplit(" ", 1)[0]
            return cut.rstrip(",;:- ") + "."
        return ""
    except Exception:
        return ""
