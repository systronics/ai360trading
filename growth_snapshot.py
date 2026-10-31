"""
growth_snapshot.py v1.0 (2026-10-31) — one daily row of audience numbers, so growth is MEASURED not guessed.

Appends to _data/growth_history.json: YouTube subscribers/views/videos, Facebook Page followers, Instagram followers,
Telegram members for the three channels. Read-only API calls; every metric is fail-open (a missing one is stored as null).
No token is ever printed. Run by .github/workflows/growth-snapshot.yml (daily).
"""
import os
import json
import datetime as dt
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import quote

OUT = Path("_data/growth_history.json")
G = "https://graph.facebook.com/v21.0/"


def _get(url, headers=None):
    try:
        return json.loads(urlopen(Request(url, headers=headers or {}), timeout=30).read())
    except HTTPError as e:
        try:
            return {"error": json.loads(e.read()).get("error", {}).get("message", str(e))}
        except Exception:
            return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


def youtube():
    raw = os.environ.get("YOUTUBE_CREDENTIALS", "")
    if not raw:
        return {}
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        yt = build("youtube", "v3", credentials=Credentials.from_authorized_user_info(json.loads(raw)))
        r = yt.channels().list(part="statistics", mine=True).execute()
        s = r["items"][0]["statistics"]
        return {"yt_subs": int(s.get("subscriberCount", 0)), "yt_views": int(s.get("viewCount", 0)), "yt_videos": int(s.get("videoCount", 0))}
    except Exception as e:
        print(f"[GROWTH] youtube skipped: {str(e)[:120]}")
        return {}


def facebook_instagram():
    tok, page, ig = os.environ.get("META_ACCESS_TOKEN", ""), os.environ.get("FACEBOOK_PAGE_ID", ""), os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    out = {}
    if not (tok and page):
        return out
    r = _get(f"{G}{page}?fields=access_token&access_token={quote(tok)}")
    pt = r.get("access_token") or tok
    r = _get(f"{G}{page}?fields=followers_count,fan_count&access_token={quote(pt)}")
    if "error" not in r:
        out["fb_followers"] = r.get("followers_count") or r.get("fan_count")
    else:
        print(f"[GROWTH] facebook skipped: {r['error'][:100]}")
    if ig:
        r = _get(f"{G}{ig}?fields=followers_count,media_count&access_token={quote(pt)}")
        if "error" not in r:
            out["ig_followers"] = r.get("followers_count")
            out["ig_posts"] = r.get("media_count")
        else:
            print(f"[GROWTH] instagram skipped: {r['error'][:100]}")
    return out


def telegram():
    tok = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    out = {}
    if not tok:
        return out
    for key, env in (("tg_basic", "CHAT_ID_BASIC"), ("tg_advance", "CHAT_ID_ADVANCE"), ("tg_premium", "CHAT_ID_PREMIUM")):
        chat = os.environ.get(env, "")
        if not chat:
            continue
        r = _get(f"https://api.telegram.org/bot{tok}/getChatMemberCount?chat_id={quote(chat)}")
        if r.get("ok"):
            out[key] = r.get("result")
        else:
            print(f"[GROWTH] telegram {key} skipped")
    return out


def main():
    row = {"date": dt.date.today().isoformat()}
    for fn in (youtube, facebook_instagram, telegram):
        try:
            row.update(fn())
        except Exception as e:
            print(f"[GROWTH] {fn.__name__} failed (fail-open): {str(e)[:100]}")
    try:
        items = json.loads(OUT.read_text(encoding="utf-8")).get("rows", [])
    except Exception:
        items = []
    items = [x for x in items if x.get("date") != row["date"]] + [row]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"rows": items[-400:]}, indent=1), encoding="utf-8")
    print("[GROWTH]", {k: v for k, v in row.items()})


if __name__ == "__main__":
    main()
