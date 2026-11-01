"""
tech_daily.py v1.0 (2026-11-01) — the daily pipeline for the AI360 Technology channel/page (NOT the trading channel).

picks the next unused topic from tech_short.TOPICS -> builds the Short (real footage, Hinglish voice, thumbnails) -> checks it
(<= 59 s) -> uploads to the NEW YouTube channel PRIVATE with a publishAt time (so the owner can cancel in Studio), writes the done-list.
A separate workflow step then posts the same Short to the new Facebook Page + Instagram (upload_facebook.py --meta-prefix tech).

MODES:  dry (build only) | private-test (YouTube private, not marked done) | scheduled (real, publishAt, marked done)
Needs (scheduled): secrets YOUTUBE_CREDENTIALS_TECH, PEXELS_API_KEY, GEMINI_API_KEY (optional, Edge voice otherwise).
Never raises; always exit 0 (a failed run just retries next time). Owner-approved wiring only: the workflow stays dry until
the repo variable TECH_MODE is set to 'scheduled'.
"""
import os
import sys
import json
import argparse
import datetime as dt
from pathlib import Path

DONE_FILE = Path("_data/tech_done.json")
TOPIC_ORDER = ["phone_heat", "wifi_slow", "laptop_hang", "pc_no_start", "mixer_hot", "news_72h"]
PUBLISH_UTC = (13, 0)   # 18:30 IST
CTA_FILE = Path("_data/tech_cta.txt")   # the owner's own lines for descriptions (service number/link); optional
DEFAULT_CTA = "PC ya data ki problem? Google par 'ai360services Haridwar' search karo."
CRED_ENV = "YOUTUBE_CREDENTIALS_TECH"


def _tg(msg):
    try:
        import emotion_story as E
        E._tg(msg)
    except Exception:
        print("[TECH] telegram skipped:", msg[:80])


def load_done():
    try:
        return json.loads(DONE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_done(items):
    DONE_FILE.parent.mkdir(parents=True, exist_ok=True)
    DONE_FILE.write_text(json.dumps(items, indent=1, ensure_ascii=False), encoding="utf-8")


def next_publish(now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    cand = now.replace(hour=PUBLISH_UTC[0], minute=PUBLISH_UTC[1], second=0, microsecond=0)
    if cand <= now + dt.timedelta(hours=2):
        cand += dt.timedelta(days=1)
    return cand


def cta_line():
    try:
        t = CTA_FILE.read_text(encoding="utf-8").strip()
        return t or DEFAULT_CTA
    except Exception:
        return DEFAULT_CTA


def youtube_upload(mp4, title, desc, tags, thumb, publish_at=None):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    raw = os.environ.get(CRED_ENV, "")
    if not raw:
        raise RuntimeError(f"no {CRED_ENV}")
    yt = build("youtube", "v3", credentials=Credentials.from_authorized_user_info(json.loads(raw)))
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False}
    if publish_at:
        status["publishAt"] = publish_at.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    body = {"snippet": {"title": title[:100], "description": desc[:4900], "tags": tags[:15], "categoryId": "28",
                        "defaultLanguage": "hi", "defaultAudioLanguage": "hi"}, "status": status}
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(mp4, mimetype="video/mp4", resumable=True, chunksize=8 * 1024 * 1024))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    vid = resp["id"]
    if thumb and Path(thumb).exists():
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(thumb, mimetype="image/jpeg")).execute()
        except Exception as e:
            print(f"[TECH] custom thumbnail skipped (fail-open): {str(e)[:100]}")
    return vid


def run(mode, out_dir, topic=None):
    try:
        import tech_short as TS
        done = load_done()
        used = {d.get("topic") for d in done}
        key = topic or next((k for k in TOPIC_ORDER if k in TS.TOPICS and k not in used), None)
        if not key:
            _tg("AI360 Technology: the topic queue is EMPTY, nothing published. Ask Claude to add topics.")
            print("[TECH] queue empty")
            return 0
        print(f"[TECH] topic = {key} (mode={mode})")
        mp4, thumb, meta = TS.build(key, out_dir, real=True)
        if meta["duration_s"] > 59.0:
            _tg(f"AI360 Technology: '{key}' is {meta['duration_s']}s (over 59s), NOT uploaded.")
            print("[TECH] too long, not uploaded")
            return 0
        from human_touch import ai_disclosure
        NL = chr(10)
        desc = (meta["description"] + NL + NL + cta_line() + NL + NL + "Follow karo: roz ek nayi tech problem ka solution." + NL + NL +
                ai_disclosure("hi"))
        # the same text for the Facebook/Instagram step (it reads this json)
        caption = meta["title"].replace(" #shorts", "") + NL + NL + cta_line() + NL + NL + "#Tech #TechTips #Hinglish #AI360Technology"
        meta.update({"description_full": desc, "caption": caption, "topic": key})
        Path(out_dir, f"{key}_meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
        if mode == "dry":
            print(f"[TECH] DRY RUN, nothing uploaded: {meta['title']} ({meta['duration_s']}s)")
            return 0
        tags = meta.get("tags") or ["tech", "hinglish", "shorts"]
        pat = Path(out_dir) / f"{key}_thumb_pattern.jpg"
        thumb_s = str(pat) if pat.exists() else (str(thumb) if thumb else "")
        if mode == "private-test":
            vid = youtube_upload(str(mp4), "[TEST - private] " + meta["title"], desc, tags, thumb_s, None)
            print(f"[TECH] PRIVATE TEST uploaded: https://youtu.be/{vid} (not announced, not marked done)")
            return 0
        when = next_publish()
        vid = youtube_upload(str(mp4), meta["title"], desc, tags, thumb_s, when)
        print(f"[TECH] scheduled {vid} for {when.isoformat()}")
        done.append({"topic": key, "video": vid, "publish_at": when.isoformat()})
        save_done(done)
        _tg("<b>New AI360 Technology Short</b>: " + meta["title"] + chr(10) + "Goes live " + when.strftime("%a %d %b, %H:%M")
            + " UTC (cancel in YouTube Studio if needed)" + chr(10) + "https://youtu.be/" + vid)
    except Exception as e:
        import traceback
        traceback.print_exc()
        _tg(f"AI360 Technology: pipeline error: {str(e)[:160]}. Nothing published; it will retry next run.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--mode", default="dry", choices=["dry", "private-test", "scheduled"])
    ap.add_argument("--topic", default=None)
    ap.add_argument("--out", default="output/tech")
    a = ap.parse_args()
    if a.run:
        sys.exit(run(a.mode, a.out, a.topic))
    print("usage: python tech_daily.py --run --mode dry|private-test|scheduled")
