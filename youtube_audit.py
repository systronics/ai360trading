"""
youtube_audit.py v1.0 (2026-10-31) — READ-ONLY audit of every video on the channel: views, age, privacy.
Prints a summary and writes _data/youtube_audit.json (id, title, views, published, privacy) — nothing is changed on YouTube.
Run by .github/workflows/youtube-audit.yml (manual).
"""
import os
import json
import datetime as dt
from pathlib import Path


def main():
    raw = os.environ.get("YOUTUBE_CREDENTIALS", "")
    if not raw:
        print("no YOUTUBE_CREDENTIALS")
        return
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    yt = build("youtube", "v3", credentials=Credentials.from_authorized_user_info(json.loads(raw)))
    ch = yt.channels().list(part="contentDetails,statistics", mine=True).execute()["items"][0]
    up = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    print("channel stats:", ch["statistics"])
    ids, tok = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=up, maxResults=50, pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        tok = r.get("nextPageToken")
        if not tok:
            break
    rows = []
    for k in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,statistics,status,contentDetails", id=",".join(ids[k:k + 50])).execute()
        for v in r["items"]:
            rows.append({"id": v["id"], "title": v["snippet"]["title"][:90], "views": int(v["statistics"].get("viewCount", 0)),
                         "likes": int(v["statistics"].get("likeCount", 0)), "published": v["snippet"]["publishedAt"][:10],
                         "privacy": v["status"]["privacyStatus"], "dur": v["contentDetails"]["duration"]})
    Path("_data").mkdir(exist_ok=True)
    Path("_data/youtube_audit.json").write_text(json.dumps({"as_of": dt.date.today().isoformat(), "videos": rows}, ensure_ascii=False, indent=0), encoding="utf-8")
    pub = [x for x in rows if x["privacy"] == "public"]
    today = dt.date.today()
    age = lambda x: (today - dt.date.fromisoformat(x["published"])).days
    print(f"videos total {len(rows)}, public {len(pub)}, private/unlisted {len(rows) - len(pub)}")
    for lo, hi in ((0, 0), (1, 5), (6, 20), (21, 100), (101, 10 ** 9)):
        n = sum(1 for x in pub if lo <= x["views"] <= hi)
        print(f"  views {lo}-{hi if hi < 10 ** 9 else 'inf'}: {n} public videos")
    old_low = [x for x in pub if x["views"] <= 5 and age(x) > 45]
    print(f"public, <=5 views and older than 45 days: {len(old_low)}")
    print(f"total views on those: {sum(x['views'] for x in old_low)} of {sum(x['views'] for x in pub)} on all public")
    print("TOP 12 by views:")
    for x in sorted(pub, key=lambda x: -x["views"])[:12]:
        print(f"  {x['views']:5d} views {x['likes']:3d} likes {x['published']} {x['title']}")
    print("likes total:", sum(x["likes"] for x in rows))


if __name__ == "__main__":
    main()
