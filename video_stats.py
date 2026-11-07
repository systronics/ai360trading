"""
video_stats.py v1.0 (2026-11-07) - per-video views for BOTH YouTube channels (AI360 Trading + AI360 Technology) into _data/video_stats.json, read-only.

WHY (owner 2026-11-07, tech Shorts): 'are the thumbnails / topics / hooks working?' With 4 videos nobody can know. This records, every day, each PUBLIC video's views, likes, comments, age and views per day,
joined with the topic of the tech Shorts (tech_done.json), so that after ~20 videos the numbers (not opinions) show which topics and hooks get views. Public statistics only (views/likes/comments): watch-time and retention need the
YouTube Analytics scope, which these tokens may not have, so they are NOT used here. Fail-open: any error leaves the existing file untouched. Never prints a token.
USAGE: python video_stats.py      (needs YOUTUBE_CREDENTIALS and/or YOUTUBE_CREDENTIALS_TECH)
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path("_data/video_stats.json")
TECH_DONE = Path("_data/tech_done.json")


def summarize(videos, now=None, topics=None):
    """videos: [{id,title,published,views,likes,comments}]. Adds age_days / views_per_day / topic and sorts by views per day (best first). Pure."""
    now = now or datetime.now(timezone.utc)
    topics = topics or {}
    out = []
    for v in videos:
        try:
            pub = datetime.fromisoformat(str(v["published"]).replace("Z", "+00:00"))
        except Exception:
            continue
        age = max((now - pub).total_seconds() / 86400.0, 0.0)
        views = int(v.get("views") or 0)
        out.append({"id": v["id"], "title": v.get("title", ""), "published": pub.date().isoformat(), "age_days": round(age, 1), "views": views,
                    "likes": int(v.get("likes") or 0), "comments": int(v.get("comments") or 0), "views_per_day": round(views / max(age, 0.5), 1),
                    "topic": topics.get(v["id"], "")})
    return sorted(out, key=lambda x: -x["views_per_day"])


def fetch_channel(cred_json, max_videos=200):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    yt = build("youtube", "v3", credentials=Credentials.from_authorized_user_info(json.loads(cred_json)), cache_discovery=False)
    ch = yt.channels().list(part="contentDetails,snippet", mine=True).execute()["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while len(ids) < max_videos:
        r = yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50, pageToken=token).execute()
        ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
        token = r.get("nextPageToken")
        if not token:
            break
    vids = []
    for k in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,statistics,status", id=",".join(ids[k:k + 50])).execute()
        for it in r.get("items", []):
            if it.get("status", {}).get("privacyStatus") != "public":
                continue                                           # scheduled/private videos have no views to learn from
            st = it.get("statistics", {})
            vids.append({"id": it["id"], "title": it["snippet"]["title"], "published": it["snippet"]["publishedAt"], "views": st.get("viewCount", 0),
                         "likes": st.get("likeCount", 0), "comments": st.get("commentCount", 0)})
    return ch["snippet"]["title"], vids


def main():
    topics = {}
    try:
        for d in json.loads(TECH_DONE.read_text(encoding="utf-8")):
            topics[d.get("video")] = d.get("topic", "")
    except Exception:
        pass
    result = {"generated": datetime.now(timezone.utc).isoformat(timespec="minutes"), "channels": {}}
    for label, env in (("trading", "YOUTUBE_CREDENTIALS"), ("tech", "YOUTUBE_CREDENTIALS_TECH")):
        raw = os.environ.get(env, "").strip()
        if not raw:
            continue
        try:
            name, vids = fetch_channel(raw)
            result["channels"][label] = {"name": name, "videos": summarize(vids, topics=topics)}
            top = result["channels"][label]["videos"][:3]
            print(f"[STATS] {label} ({name}): {len(vids)} public videos; best per day: " + ", ".join(f"{t['title'][:30]} {t['views_per_day']}/d" for t in top))
        except Exception as e:
            print(f"[STATS] {label} skipped (fail-open): {str(e)[:140]}")
    if not result["channels"]:
        print("[STATS] nothing fetched, file untouched")
        return 0
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[STATS] wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
