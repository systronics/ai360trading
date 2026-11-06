"""
announce_videos.py v1.0 (2026-11-06) - posts the link of every new AI360 TRADING YouTube video/Short to the BASIC Telegram channel, once, when it is really public.

WHY (owner 2026-11-06: 'short aur video ka link basic channel me send hona chahiye'): videos are uploaded PRIVATE with a publishAt time, and the old pipeline notes went out at upload time
(a link that did not work yet, with owner-only text like 'cancel in YouTube Studio'). Those notes now go to Premium (the owner); this script sends the public announcement.

How: reads the done-lists of the trading-channel pipelines (lessons, story Shorts, case-study Shorts, news fact-check), and for every video whose publish time has passed and that YouTube's
public oEmbed endpoint serves (private videos are refused), sends 'title + link' to Basic and records the id in _data/announced_videos.json. First run: videos older than 3 days are only
recorded (no old-video spam). The AI360 Technology channel is NOT announced here (different audience) - add its done-list to SOURCES if wanted.
Fail-open: any error = nothing sent, nothing recorded for that video (it is retried on the next run).
USAGE: python announce_videos.py [--dry]
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

DATA = Path("_data")
STATE = DATA / "announced_videos.json"
MAX_AGE_DAYS = 3


def collect(data_dir=DATA):
    """[(video_id, publish_at_datetime_utc)] from the trading-channel done-lists. Tolerant of missing/odd files."""
    out = []

    def add(vid, pub):
        try:
            t = datetime.fromisoformat(str(pub))
            if t.tzinfo is None:
                t = t.replace(tzinfo=timezone.utc)
            if vid:
                out.append((str(vid), t))
        except Exception:
            pass

    def load(name):
        try:
            return json.loads((Path(data_dir) / name).read_text(encoding="utf-8"))
        except Exception:
            return None

    d = load("lessons_done.json")
    if isinstance(d, dict):
        for ed in d.values():
            if isinstance(ed, dict):
                for rec in ed.values():
                    if isinstance(rec, dict):
                        add(rec.get("video"), rec.get("publish_at"))
    d = load("stories_done.json")
    for rec in (d.get("done", []) if isinstance(d, dict) else []):
        add(rec.get("video"), rec.get("publish_at"))
    for name in ("tech_trading_done.json",):
        d = load(name)
        for rec in (d if isinstance(d, list) else []):
            add(rec.get("video"), rec.get("publish_at"))
    d = load("case_history.json")
    for rec in (d if isinstance(d, list) else []):
        add(rec.get("video"), rec.get("publish_at") or rec.get("date"))
    return out


def due(items, announced, now):
    """Videos to consider now: not announced, publish time passed, not older than MAX_AGE_DAYS. Also returns the old ones to just record."""
    fresh, stale = [], []
    for vid, t in items:
        if vid in announced or t > now:
            continue
        (fresh if now - t <= timedelta(days=MAX_AGE_DAYS) else stale).append((vid, t))
    return fresh, stale


def oembed_title(vid):
    """Title when the video is publicly viewable, else None (private/unknown)."""
    try:
        url = f"https://www.youtube.com/oembed?url={quote('https://youtu.be/' + vid, safe='')}&format=json"
        with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=15) as r:
            if r.status == 200:
                return json.loads(r.read().decode("utf-8")).get("title") or ""
    except Exception:
        return None
    return None


def send_basic(msg):
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN", ""), os.environ.get("CHAT_ID_BASIC", "")
    if not (tok and chat):
        print("[ANNOUNCE] telegram creds missing, not sent")
        return False
    req = Request(f"https://api.telegram.org/bot{tok}/sendMessage",
                  data=json.dumps({"chat_id": chat, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": False}).encode(),
                  headers={"Content-Type": "application/json"})
    urlopen(req, timeout=20).read()
    return True


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    dry = "--dry" in argv
    now = datetime.now(timezone.utc)
    try:
        announced = set(json.loads(STATE.read_text(encoding="utf-8")))
    except Exception:
        announced = set()
    first_run = not STATE.exists()
    fresh, stale = due(collect(), announced, now)
    changed = False
    for vid, t in stale:
        announced.add(vid)
        changed = True
    if stale:
        print(f"[ANNOUNCE] {len(stale)} old video(s) recorded without sending")
    for vid, t in sorted(fresh, key=lambda x: x[1]):
        title = oembed_title(vid)
        if title is None:
            print(f"[ANNOUNCE] {vid}: not public yet, will retry")
            continue
        msg = f"🎬 <b>{title.replace('<', '').replace('>', '')}</b>\nhttps://youtu.be/{vid}"
        print(f"[ANNOUNCE] {'DRY ' if dry else ''}{vid}: {title}")
        if dry:
            continue
        try:
            if send_basic(msg):
                announced.add(vid)
                changed = True
        except Exception as e:
            print(f"[ANNOUNCE] send failed for {vid}: {str(e)[:100]}")
    if changed and not dry:
        DATA.mkdir(exist_ok=True)
        STATE.write_text(json.dumps(sorted(announced), indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
