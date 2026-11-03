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
TOPIC_ORDER = ["phone_heat", "otp_scam", "wifi_slow", "deleted_data_recover", "charge_overnight", "laptop_hang", "phone_wet", "hdd_click", "public_wifi", "pc_no_start", "fast_charging", "mixer_hot", "storage_full", "force_close_apps", "clear_cache", "laptop_plugged", "ssd_vs_hdd"]   # 2026-11-03: old + curiosity-first mix (tech_topics2); news_72h stays out
PUBLISH_UTC = (13, 0)   # 18:30 IST
CTA_FILE = Path("_data/tech_cta.txt")   # the owner's own lines for descriptions (service number/link); optional
DEFAULT_CTA = "PC ya data ki problem? Google par 'ai360services Haridwar' search karo."
CRED_ENV = "YOUTUBE_CREDENTIALS_TECH"
TRADING_DONE = Path("_data/tech_trading_done.json")   # topics already sent to the TRADING channel (one-off news fact-checks)
TRADING_PUBLISH_UTC = (13, 30)                       # 19:00 IST


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


def next_publish(now=None, at=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    at = at or PUBLISH_UTC
    cand = now.replace(hour=at[0], minute=at[1], second=0, microsecond=0)
    if cand <= now + dt.timedelta(hours=2):
        cand += dt.timedelta(days=1)
    return cand


def cta_line():
    try:
        t = CTA_FILE.read_text(encoding="utf-8").strip()
        return t or DEFAULT_CTA
    except Exception:
        return DEFAULT_CTA


def youtube_upload(mp4, title, desc, tags, thumb, publish_at=None, cred_env=None):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    cred_env = cred_env or CRED_ENV
    raw = os.environ.get(cred_env, "")
    if not raw:
        raise RuntimeError(f"no {cred_env}")
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


def run_trading(mode, out_dir, topic):
    """ONE news fact-check Short to the AI360 TRADING channel (owner 2026-11-01): private + publishAt, with the market caveat and the
    Telegram funnel. Uses YOUTUBE_CREDENTIALS (the trading channel). Never posts to Facebook/Instagram."""
    try:
        import tech_short as TS
        try:
            done = json.loads(TRADING_DONE.read_text(encoding="utf-8"))
        except Exception:
            done = []
        if topic in {d.get("topic") for d in done}:
            print(f"[TECH->TRADING] {topic} already sent, nothing to do")
            return 0
        mp4, thumb, meta = TS.build(topic, out_dir, real=True)
        if meta["duration_s"] > 59.0:
            _tg(f"AI360 Trading: '{topic}' is {meta['duration_s']}s (over 59s), NOT uploaded.")
            return 0
        from human_touch import ai_disclosure
        try:
            import money_funnel as mf
            funnel = mf.funnel_block("hi", compact=True)
        except Exception:
            funnel = "Telegram: https://t.me/ai360trading" + chr(10) + "Website: https://ai360trading.in"
        NL = chr(10)
        caveat = ("Market par asar: is tarah ki khabar ka market par seedha asar dikhna zaroori nahi. Sirf headlines dekhkar trade mat karo. "
                  "Ye salah ya prediction nahi hai. AI360Trading SEBI registered nahi hai, sirf shiksha ke liye.")
        desc = meta["description"] + NL + NL + caveat + NL + NL + funnel + NL + NL + ai_disclosure("hi")
        Path(out_dir, f"{topic}_meta.json").write_text(json.dumps(dict(meta, description_full=desc), indent=1, ensure_ascii=False), encoding="utf-8")
        if mode == "dry":
            print(f"[TECH->TRADING] DRY RUN: {meta['title']} ({meta['duration_s']}s)")
            return 0
        pat = Path(out_dir) / f"{topic}_thumb_pattern.jpg"
        thumb_s = str(pat) if pat.exists() else (str(thumb) if thumb else "")
        tags = (meta.get("tags") or []) + ["AI360Trading"]
        if mode == "private-test":
            vid = youtube_upload(str(mp4), "[TEST - private] " + meta["title"], desc, tags, thumb_s, None, cred_env="YOUTUBE_CREDENTIALS")
            print(f"[TECH->TRADING] PRIVATE TEST: https://youtu.be/{vid}")
            return 0
        when = next_publish(at=TRADING_PUBLISH_UTC)
        vid = youtube_upload(str(mp4), meta["title"], desc, tags, thumb_s, when, cred_env="YOUTUBE_CREDENTIALS")
        print(f"[TECH->TRADING] scheduled {vid} for {when.isoformat()}")
        done.append({"topic": topic, "video": vid, "publish_at": when.isoformat()})
        TRADING_DONE.parent.mkdir(parents=True, exist_ok=True)
        TRADING_DONE.write_text(json.dumps(done, indent=1, ensure_ascii=False), encoding="utf-8")
        _tg("<b>AI360 Trading: new sach-check Short scheduled</b>: " + meta["title"] + chr(10) + "Goes live " + when.strftime("%a %d %b, %H:%M")
            + " UTC (cancel in YouTube Studio if needed)" + chr(10) + "https://youtu.be/" + vid)
    except Exception as e:
        import traceback
        traceback.print_exc()
        _tg(f"AI360 Trading sach-check Short: pipeline error: {str(e)[:160]}. Nothing published.")
    return 0


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
    ap.add_argument("--channel", default="tech", choices=["tech", "trading"])
    a = ap.parse_args()
    if a.run and a.channel == "trading":
        sys.exit(run_trading(a.mode, a.out, a.topic or "news_72h"))
    if a.run:
        sys.exit(run(a.mode, a.out, a.topic))
    print("usage: python tech_daily.py --run --mode dry|private-test|scheduled")
