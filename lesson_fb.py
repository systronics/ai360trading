"""
lesson_fb.py v1.0 (2026-11-10) - post the weekly HINDI lesson to the trading Facebook Page as a normal (landscape) video, SCHEDULED for the same minute the YouTube version goes public.

Why only Hindi: the Page audience is ~97% India; the English edition would be a second post of the same lesson in the same week.
No duplicates, by design:
  * one post per lesson id (the post id is stored in _data/lessons_done.json under the lesson's "in-hi" entry as "fb_video"; a lesson that already has one is never posted again),
  * only region "in" + language "hi",
  * the video is created UNPUBLISHED with scheduled_publish_time; if the schedule time is not valid (needs 10 minutes to 70 days ahead) or Meta rejects it, NOTHING is posted - never an immediate post,
  * OFF unless the repo variable LESSON_FB is "on" (kill switch: gh variable set LESSON_FB --body off).
Fail-open: any problem returns None and the YouTube pipeline is not affected.
"""
import os
import time

import requests

GRAPH = "https://graph.facebook.com/v21.0"
MIN_AHEAD_S = 10 * 60 + 30            # Meta: at least 10 minutes ahead (30 s margin)
MAX_AHEAD_S = 70 * 24 * 3600          # Meta: at most 75 days ahead (margin kept)


def enabled(region, lang, env=None):
    env = os.environ if env is None else env
    return str(env.get("LESSON_FB", "")).strip().lower() == "on" and region == "in" and lang == "hi"


def already_posted(done, lid):
    return bool(((done or {}).get(lid, {}).get("in-hi", {}) or {}).get("fb_video"))


def schedule_ok(publish_epoch, now_epoch=None):
    now_epoch = time.time() if now_epoch is None else now_epoch
    return MIN_AHEAD_S <= (publish_epoch - now_epoch) <= MAX_AHEAD_S


def caption(title, short_desc, disclosure, footer):
    """Plain caption: title, 1-2 line idea, honest footer, AI disclosure, 2 hashtags. No YouTube chapters/funnel block."""
    short = " ".join(str(short_desc or "").split())[:300]
    parts = [str(title).strip(), short, footer, disclosure, "#AI360Trading #ShareMarketHindi"]
    return "\n\n".join(p for p in parts if p)


def _page_token(page_id, user_token):
    try:
        j = requests.get(f"{GRAPH}/{page_id}", params={"fields": "access_token", "access_token": user_token}, timeout=20).json()
        return j.get("access_token") or ""
    except Exception:
        return ""


def post_scheduled(mp4, title, text, publish_dt, page_id=None, user_token=None, now_epoch=None):
    """Return the Facebook video id, or None. Never publishes immediately."""
    page_id = page_id or os.environ.get("FACEBOOK_PAGE_ID", "")
    user_token = user_token or os.environ.get("META_ACCESS_TOKEN", "")
    if not (page_id and user_token and mp4 and os.path.exists(mp4)):
        print("[LESSON-FB] missing page id / token / file - skipped")
        return None
    when = int(publish_dt.timestamp())
    if not schedule_ok(when, now_epoch):
        print("[LESSON-FB] publish time is outside Meta's 10 min - 70 days window - skipped (no immediate post)")
        return None
    token = _page_token(page_id, user_token)
    if not token:
        print("[LESSON-FB] could not get a Page token - skipped")
        return None
    try:
        with open(mp4, "rb") as fh:
            r = requests.post(
                f"{GRAPH}/{page_id}/videos",
                data={"access_token": token, "title": str(title)[:100], "description": text[:4900], "published": "false",
                      "scheduled_publish_time": str(when), "unpublished_content_type": "SCHEDULED"},
                files={"source": fh}, timeout=900)
        j = r.json()
    except Exception as e:
        print(f"[LESSON-FB] upload error (fail-open): {e}")
        return None
    vid = j.get("id")
    if not vid:
        print(f"[LESSON-FB] Meta refused the scheduled video (nothing posted): {str(j.get('error', j))[:200]}")
        return None
    print(f"[LESSON-FB] scheduled Facebook video {vid} for {publish_dt.isoformat()}")
    return vid
