"""
threads_post.py v1.0 (2026-11-10) - automatic Threads posts for new website articles, and the 60-day token refresh.
Owner 2026-11-10: 'do threads and pinterest auto'. Threads (Meta) has a free official publishing API (docs read 2026-11-10): create a container (POST /{user}/threads, media_type TEXT, text <= 500 chars, link_attachment
= the article, is_made_with_ai=true because articles are AI-assisted and we disclose that), wait ~30 s, publish (POST /{user}/threads_publish). Limit 250 API posts / 24 h; we post at most ONE article a day.
Needs two GitHub secrets that only the owner can create (see the setup steps in the final report / CLAUDE.md): THREADS_USER_ID and THREADS_ACCESS_TOKEN (long-lived, 60 days). Without them this script prints
'no token' and exits 0 (fail-open); with THREADS_MODE != 'scheduled' it only PRINTS what it would post (dry).
USAGE: python threads_post.py --run        post (or print, in dry mode) the newest not-yet-posted article from the last 3 days
       python threads_post.py --refresh    refresh the long-lived token (needs >= 24 h old, not expired) and store the new one in the GitHub secret THREADS_ACCESS_TOKEN (needs GH_TOKEN, as token_refresh.py)
Never prints a token. State: _data/threads_posted.json {"urls": [...]} (committed by the workflow).
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

import site_posts

GRAPH = "https://graph.threads.com/v1.0"
STATE = Path("_data/threads_posted.json")
MAX_CHARS = 480          # the API limit is 500 characters; keep a margin (emojis count as bytes)


def build_text(title, excerpt):
    """Post text: title, one short excerpt line, disclosure. The URL goes in link_attachment (the first URL in the text becomes the preview too, so none is written here). Always <= MAX_CHARS. Pure."""
    title = " ".join(str(title).split())
    ex = " ".join(str(excerpt).split())
    tail = "\n\nAI-assisted. Educational only, not investment advice."
    room = MAX_CHARS - len(title) - len(tail) - 2
    body = ""
    if ex and room > 40:
        body = "\n\n" + (ex if len(ex) <= room else ex[:room - 1].rsplit(" ", 1)[0].rstrip(",;:- ") + "...")
    text = title + body + tail
    return text[:MAX_CHARS]


def pick_article(posts, posted_urls):
    """The newest recent post that was not posted yet. Pure."""
    for p in posts:
        if p["url"] not in set(posted_urls):
            return p
    return None


def load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8")).get("urls", [])
    except Exception:
        return []


def save_state(urls):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps({"urls": urls[-200:]}, indent=1), encoding="utf-8")


def post_text(user_id, token, text, link):
    """Create + publish one TEXT post with a link preview. Returns the media id or None. Never raises."""
    try:
        r = requests.post(f"{GRAPH}/{user_id}/threads", data={"media_type": "TEXT", "text": text, "link_attachment": link, "is_made_with_ai": "true", "access_token": token}, timeout=30)
        cid = r.json().get("id")
        if not cid:
            print("[THREADS] container failed:", str(r.text)[:200].replace(token, "***"))
            return None
        time.sleep(30)                                                     # Meta recommends about 30 s before publishing
        r2 = requests.post(f"{GRAPH}/{user_id}/threads_publish", data={"creation_id": cid, "access_token": token}, timeout=30)
        mid = r2.json().get("id")
        if not mid:
            print("[THREADS] publish failed:", str(r2.text)[:200].replace(token, "***"))
        return mid
    except Exception as e:
        print("[THREADS] error:", str(e)[:150].replace(token, "***"))
        return None


def run():
    user_id = os.environ.get("THREADS_USER_ID", "").strip()
    token = os.environ.get("THREADS_ACCESS_TOKEN", "").strip()
    mode = os.environ.get("THREADS_MODE", "dry").strip().lower()
    posts = site_posts.recent_posts(max_age_days=3)
    art = pick_article(posts, load_state())
    if not art:
        print(f"[THREADS] nothing new to post ({len(posts)} recent articles, all already posted or none)")
        return 0
    text = build_text(art["title"], art["excerpt"])
    print(f"[THREADS] next article: {art['url']}\n{text}")
    if mode != "scheduled":
        print("[THREADS] dry mode (THREADS_MODE is not 'scheduled'): nothing posted")
        return 0
    if not (user_id and token):
        print("[THREADS] no THREADS_USER_ID / THREADS_ACCESS_TOKEN: nothing posted (owner has not created the secrets yet)")
        return 0
    mid = post_text(user_id, token, text, art["url"])
    if mid:
        save_state(load_state() + [art["url"]])
        print("[THREADS] posted", mid)
    return 0


def refresh():
    token = os.environ.get("THREADS_ACCESS_TOKEN", "").strip()
    if not token:
        print("[THREADS] no token to refresh")
        return 0
    try:
        r = requests.get("https://graph.threads.com/refresh_access_token", params={"grant_type": "th_refresh_token", "access_token": token}, timeout=30)
        j = r.json()
        new = j.get("access_token")
        if not new:
            print("[THREADS] refresh failed:", str(r.text)[:200].replace(token, "***"))
            return 0
        import token_refresh as T
        ok = T.update_github_secret(os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("GH_TOKEN", ""), "THREADS_ACCESS_TOKEN", new)
        print("[THREADS] token refreshed, expires_in", j.get("expires_in"), "| secret updated:", ok)
    except Exception as e:
        print("[THREADS] refresh error:", str(e)[:150].replace(token, "***"))
    return 0


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--refresh" in argv:
        return refresh()
    if "--run" in argv:
        return run()
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
