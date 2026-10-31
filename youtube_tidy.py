"""
youtube_tidy.py v1.0 (2026-10-31) — set OLD, near-zero-view public videos to PRIVATE (reversible; nothing is deleted).

WHY  The channel has 960 public videos but only 55 subscribers; 576 of them are older than 45 days with <=5 views
     (together 625 of 11,777 views = 5%). A clean channel shows the viewer only content that earns attention. Owner
     delegated the decision ("jo karna hai tum karna hai") on 2026-10-31.
RULES hide only: public AND views <= MAX_VIEWS (5) AND older than MIN_AGE_DAYS (45). Never touches newer videos or videos with views.
QUOTA videos.update costs 50 units; the daily API quota is 10,000, so each run hides at most BATCH (150) videos.
UNDO  every hidden id is recorded in _data/youtube_hidden.json; `python youtube_tidy.py --restore` makes them public again.
Modes: dry (list only) | live. Run by .github/workflows/youtube-tidy.yml (daily until nothing is left).
"""
import os
import sys
import json
import datetime as dt
from pathlib import Path

MAX_VIEWS = 5
MIN_AGE_DAYS = 45
BATCH = 150
LOG = Path("_data/youtube_hidden.json")


def service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=Credentials.from_authorized_user_info(json.loads(os.environ["YOUTUBE_CREDENTIALS"])))


def all_videos(yt):
    up = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=up, maxResults=50, pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        tok = r.get("nextPageToken")
        if not tok:
            break
    out = []
    for k in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,statistics,status", id=",".join(ids[k:k + 50])).execute()
        out += r["items"]
    return out


def load_log():
    try:
        return json.loads(LOG.read_text(encoding="utf-8"))
    except Exception:
        return {"hidden": []}


def set_privacy(yt, v, privacy):
    st = dict(v["status"])
    st["privacyStatus"] = privacy
    st.pop("publishAt", None)
    yt.videos().update(part="status", body={"id": v["id"], "status": st}).execute()


def main(mode, restore=False):
    yt = service()
    log = load_log()
    if restore:
        ids = [h["id"] for h in log["hidden"]]
        vids = {v["id"]: v for v in all_videos(yt)}
        n = 0
        for i in ids:
            if i in vids and vids[i]["status"]["privacyStatus"] == "private":
                set_privacy(yt, vids[i], "public")
                n += 1
        log["hidden"] = []
        LOG.write_text(json.dumps(log, indent=1), encoding="utf-8")
        print(f"[TIDY] restored {n} videos to public")
        return
    today = dt.date.today()
    vids = all_videos(yt)
    cand = []
    for v in vids:
        if v["status"]["privacyStatus"] != "public":
            continue
        views = int(v["statistics"].get("viewCount", 0))
        age = (today - dt.date.fromisoformat(v["snippet"]["publishedAt"][:10])).days
        if views <= MAX_VIEWS and age > MIN_AGE_DAYS:
            cand.append((views, -age, v))
    cand.sort(key=lambda x: (x[0], x[1]))
    print(f"[TIDY] public videos {sum(1 for v in vids if v['status']['privacyStatus'] == 'public')}, eligible to hide {len(cand)}, mode={mode}")
    done = 0
    for views, _, v in cand[:BATCH]:
        if mode == "live":
            try:
                set_privacy(yt, v, "private")
                log["hidden"].append({"id": v["id"], "title": v["snippet"]["title"][:80], "views": views, "date": today.isoformat()})
                done += 1
            except Exception as e:
                print(f"[TIDY] stopped at {v['id']}: {str(e)[:140]}")
                break
        else:
            print(f"  would hide {views} views  {v['snippet']['title'][:70]}")
    LOG.parent.mkdir(exist_ok=True)
    LOG.write_text(json.dumps(log, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[TIDY] hidden this run: {done}; still eligible after this run: {max(0, len(cand) - done)}")


if __name__ == "__main__":
    main(os.environ.get("TIDY_MODE", "dry"), restore="--restore" in sys.argv)
