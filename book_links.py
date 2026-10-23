"""
book_links.py v1.0 (2026-10-23) — "Further reading" book block for articles and video descriptions.

Reads _data/book_refs.json. A book is shown ONLY when the owner has filled its `link` field with his own
referral / affiliate URL — with every link empty (today) every function returns "" and nothing on any
page or video changes. Matching is by topic keywords found in the article title/body text.

Rules (CLAUDE.md money rules): summaries are in OUR words (the `idea` field), the book + author are credited,
no copied text; whenever a link is shown the affiliate disclosure line is shown with it; fail-open — any
error returns "".
"""
import json
import re
from pathlib import Path

_REFS = Path(__file__).parent / "_data" / "book_refs.json"


def _load():
    try:
        return json.loads(_REFS.read_text(encoding="utf-8"))
    except Exception:
        return {"books": [], "disclosure": ""}


def pick_books(text, n=2):
    """Up to n books (with a filled link) whose topic keywords appear in `text`, best match first."""
    try:
        data = _load()
        low = " " + re.sub(r"[^a-z0-9 ]", " ", str(text).lower()) + " "
        scored = []
        for b in data.get("books", []):
            if not str(b.get("link", "")).strip():
                continue
            hits = sum(1 for t in b.get("topics", []) if f" {t.lower()} " in low)
            if hits:
                scored.append((hits, b))
        scored.sort(key=lambda x: -x[0])
        return [b for _, b in scored[:n]], data.get("disclosure", "")
    except Exception:
        return [], ""


def article_block_html(text, n=2):
    """Markdown/HTML 'Further reading' block for the end of an article, or ''."""
    try:
        books, disc = pick_books(text, n)
        if not books:
            return ""
        items = "".join(
            f'<li><a href="{b["link"]}" rel="sponsored noopener" target="_blank">{b["title"]}</a> by {b["author"]} — {b["idea"]}</li>'
            for b in books)
        return (f'\n\n<div class="book-refs"><h3>Further reading</h3><ul>{items}</ul>'
                f'<p style="font-size:0.85em;color:#666;">{disc}</p></div>\n')
    except Exception:
        return ""


def description_lines(text, n=2):
    """Plain-text lines for a YouTube/Facebook description, or ''."""
    try:
        books, disc = pick_books(text, n)
        if not books:
            return ""
        lines = ["Further reading:"] + [f"- {b['title']} by {b['author']}: {b['link']}" for b in books] + [disc]
        return "\n".join(lines)
    except Exception:
        return ""
