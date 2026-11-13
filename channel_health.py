"""
channel_health.py v1.0 (2026-11-13 NEW) - READ-ONLY health check of the Facebook Pages, Instagram accounts and YouTube channels (trading + tech).
Prints (never writes anywhere, never posts, never prints a token): followers, the last posts/videos with their numbers, scheduled items and any
abnormal flag (rejected/failed upload, 'made for kids', a scheduled video whose time has passed but is still private, a Page insight call that is refused).
Run by .github/workflows/channel-health.yml (manual). Env: META_ACCESS_TOKEN, FACEBOOK_PAGE_ID(_TECH), INSTAGRAM_BUSINESS_ACCOUNT_ID, INSTAGRAM_ID_TECH,
YOUTUBE_CREDENTIALS(_TECH).
"""
import json
import os
from datetime import datetime, timezone

import requests

G = "https://graph.facebook.com/v21.0"


def gget(path, tok, **p):
    p["access_token"] = tok
    try:
        r = requests.get(f"{G}/{path}", params=p, timeout=30)
        return r.json()
    except Exception as e:
        return {"error": {"message": str(e)[:100]}}


def err(j):
    return (j.get("error") or {}).get("message", "")[:110] if isinstance(j, dict) else ""


def page_token(page_id, user_tok):
    j = gget(page_id, user_tok, fields="access_token")
    return j.get("access_token") or user_tok


def facebook(label, page_id, user_tok):
    print(f"\n===== FACEBOOK PAGE: {label}")
    if not page_id:
        print("  (no page id secret)")
        return
    tok = page_token(page_id, user_tok)
    info = gget(page_id, tok, fields="name,followers_count,fan_count,about,link")
    more = gget(page_id, tok, fields="username,category,verification_status,is_published,is_community_page,is_unclaimed,has_transitioned_to_new_page_experience,name_with_location_descriptor,rating_count")
    print("  page details:", {k: v for k, v in more.items() if k != "id"} if not err(more) else "not readable: " + err(more))
    if err(info):
        print("  page read failed:", err(info))
        return
    print(f"  {info.get('name')} | followers {info.get('followers_count')} | likes {info.get('fan_count')} | {info.get('link')}")
    ins = gget(f"{page_id}/insights", tok, metric="page_impressions_unique,page_post_engagements,page_video_views", period="days_28")
    if err(ins):
        print("  insights not available:", err(ins))
    else:
        for m in ins.get("data", []):
            vals = m.get("values") or []
            print(f"  28-day {m.get('name')}: {vals[-1].get('value') if vals else '?'}")
    posts = gget(f"{page_id}/posts", tok, fields="created_time,message,reactions.summary(true).limit(0),comments.summary(true).limit(0),shares", limit=12)
    if err(posts):
        print("  posts not readable:", err(posts))
    else:
        print("  last posts (date | reactions/comments/shares | text):")
        for x in posts.get("data", []):
            rx = (x.get("reactions") or {}).get("summary", {}).get("total_count", 0)
            cm = (x.get("comments") or {}).get("summary", {}).get("total_count", 0)
            sh = (x.get("shares") or {}).get("count", 0)
            print(f"   {x.get('created_time', '')[:10]} | {rx}/{cm}/{sh} | {(x.get('message') or '')[:50]!r}")
    reels = gget(f"{page_id}/video_reels", tok, fields="created_time,length,post_id", limit=12)
    if not err(reels):
        print(f"  reels returned: {len(reels.get('data', []))}; newest {(reels.get('data') or [{}])[0].get('created_time', '?')[:16]}")
    sch = gget(f"{page_id}/scheduled_posts", tok, fields="scheduled_publish_time,message", limit=10)
    if not err(sch):
        print(f"  scheduled posts waiting: {len(sch.get('data', []))}")
        for x in sch.get("data", [])[:5]:
            print(f"   scheduled {x.get('scheduled_publish_time')} {(x.get('message') or '')[:40]!r}")


def instagram(label, ig_id, user_tok, page_id):
    print(f"\n===== INSTAGRAM: {label}")
    if not ig_id:
        print("  (no id secret)")
        return
    tok = page_token(page_id, user_tok) if page_id else user_tok
    info = gget(ig_id, tok, fields="username,followers_count,media_count")
    if err(info):
        print("  read failed:", err(info))
        return
    print(f"  @{info.get('username')} | followers {info.get('followers_count')} | posts {info.get('media_count')}")
    media = gget(f"{ig_id}/media", tok, fields="timestamp,media_product_type,like_count,comments_count,caption", limit=10)
    if err(media):
        print("  media not readable:", err(media))
        return
    print("  last posts (date | type | likes/comments | caption):")
    for x in media.get("data", []):
        print(f"   {x.get('timestamp', '')[:10]} | {x.get('media_product_type')} | {x.get('like_count')}/{x.get('comments_count')} | {(x.get('caption') or '')[:40]!r}")


def youtube(label, raw):
    print(f"\n===== YOUTUBE: {label}")
    if not raw:
        print("  (no credentials secret)")
        return
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    yt = build("youtube", "v3", credentials=Credentials.from_authorized_user_info(json.loads(raw)))
    ch = yt.channels().list(part="snippet,contentDetails,statistics,status", mine=True).execute()["items"][0]
    st = ch["statistics"]
    print(f"  {ch['snippet']['title']} | subs {st.get('subscriberCount')} | views {st.get('viewCount')} | videos {st.get('videoCount')} | status {ch.get('status', {}).get('privacyStatus')}")
    up = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids = [i["contentDetails"]["videoId"] for i in yt.playlistItems().list(part="contentDetails", playlistId=up, maxResults=15).execute()["items"]]
    vs = yt.videos().list(part="snippet,statistics,status,contentDetails", id=",".join(ids)).execute()["items"] if ids else []
    now = datetime.now(timezone.utc)
    flags = []
    print("  last uploads (date | privacy/publishAt | views likes | length | title):")
    for v in sorted(vs, key=lambda v: v["snippet"]["publishedAt"], reverse=True):
        s, stt = v["status"], v["statistics"]
        pa = s.get("publishAt", "")
        print(f"   {v['snippet']['publishedAt'][:10]} | {s.get('privacyStatus')} {pa[:16]} | {stt.get('viewCount')} {stt.get('likeCount')} | {v['contentDetails']['duration']} | {v['snippet']['title'][:45].encode('ascii', 'replace').decode()}")
        if s.get("uploadStatus") not in ("processed", "uploaded", None):
            flags.append(f"{v['id']} uploadStatus={s.get('uploadStatus')} {s.get('failureReason') or s.get('rejectionReason') or ''}")
        if s.get("selfDeclaredMadeForKids"):
            flags.append(f"{v['id']} MADE FOR KIDS (limits comments/ads)")
        if pa and s.get("privacyStatus") == "private":
            try:
                if datetime.fromisoformat(pa.replace("Z", "+00:00")) < now:
                    flags.append(f"{v['id']} scheduled time passed but still PRIVATE")
            except Exception:
                pass
    print("  FLAGS:", flags or "none")


def main():
    t = os.environ.get("META_ACCESS_TOKEN", "")
    facebook("AI360 Trading", os.environ.get("FACEBOOK_PAGE_ID", ""), t)
    facebook("AI360 Technology", os.environ.get("FACEBOOK_PAGE_ID_TECH", ""), t)
    instagram("trading", os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", ""), t, os.environ.get("FACEBOOK_PAGE_ID", ""))
    instagram("tech", os.environ.get("INSTAGRAM_ID_TECH", ""), t, os.environ.get("FACEBOOK_PAGE_ID_TECH", ""))
    for lab, key in (("AI360 Trading", "YOUTUBE_CREDENTIALS"), ("AI360 Technology", "YOUTUBE_CREDENTIALS_TECH")):
        try:
            youtube(lab, os.environ.get(key, ""))
        except Exception as e:
            print(f"\n===== YOUTUBE: {lab}\n  failed: {str(e)[:150]}")


if __name__ == "__main__":
    main()
