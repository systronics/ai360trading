"""
lesson_runner.py — weekly evergreen lesson pipeline: pick -> build -> gate -> render -> schedule upload
=====================================================================================================
v1.0 (2026-10-18)

Replaces the old DAILY slide-style education videos with ONE lesson per week per language edition:
    US / global English  : publishes Saturday 14:00 UTC (10:00 AM New York, 7:30 PM India, 3 PM London)
    India Hindi          : publishes Sunday   13:30 UTC (7:00 PM India)
The workflow runs once a week and uploads the videos PRIVATE with a publishAt time, so YouTube
itself publishes at the exact minute (GitHub's schedule delays never change the audience time)
and the owner has a few days to glance at / cancel in YouTube Studio.

SAFETY (never-break-what-works doctrine)
  * lesson_bank.quality_gate() must PASS on the English master, translations must keep every number
  * any failure -> nothing is uploaded, a Telegram note goes to the owner, exit code 0 (never red-flags
    the repo); the lesson is NOT marked done so it is retried next week
  * `--mode private-test` uploads PRIVATE with no publishAt, no announcement, and does not mark done
  * kill switch: set the GitHub Actions variable LESSONS_ENABLED to anything but "true" to pause
  * ₹0: edge_tts, yfinance, Pillow/moviepy; YouTube API quota ~1,700 units per upload (10,000/day)
  * No AI call is needed (scripts are deterministic from our own data) so AI limits cannot stop it

Usage:  python lesson_runner.py --region us --lang en --mode scheduled|private-test [--out DIR]
"""

import os, sys, re, json, argparse, asyncio, datetime as dt
from pathlib import Path

import lesson_bank as bank
import lesson_engine as E
import lesson_builders as B
import lesson_visuals as lv

DONE_FILE = Path("_data/lessons_done.json")
PUBLISH_SLOT = {("us", "en"): (5, "14:00"), ("in", "hi"): (6, "13:30")}   # (weekday Mon=0, UTC HH:MM)
CHAPTER_NAMES = {"title": "Intro", "rule": "The rule", "winner": "Example 1: a winner", "loser": "Example 2: a stop-out", "chop": "Example 3: a trade that went nowhere",
                 "bars": "What the data says", "limits": "What this does not prove", "idea": "The idea", "need": "The numbers", "streak": "Ten losses in a row",
                 "avg": "Average returns", "risk": "The risk side", "best": "Our best trade", "worst": "Our worst trade", "ledger": "The whole ledger"}


def tg(msg):
    try:
        import requests
        tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN", ""), os.environ.get("CHAT_ID_BASIC", "")
        if tok and chat:
            requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", data={"chat_id": chat, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": "false"}, timeout=20)
    except Exception as e:
        print(f"[RUNNER] telegram skipped: {e}")


def owner_note(msg):
    """Short plain note to the owner channel (basic channel is the only one every environment has)."""
    print(f"[RUNNER] {msg}")
    tg(f"AI360 lesson pipeline: {msg}")


def load_done():
    try:
        return json.loads(DONE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_done(done):
    DONE_FILE.parent.mkdir(parents=True, exist_ok=True)
    DONE_FILE.write_text(json.dumps(done, indent=2, ensure_ascii=False), encoding="utf-8")


def next_publish(weekday, hhmm, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    h, m = (int(x) for x in hhmm.split(":"))
    cand = now.replace(hour=h, minute=m, second=0, microsecond=0)
    cand += dt.timedelta(days=(weekday - cand.weekday()) % 7)
    if cand <= now + dt.timedelta(hours=2):
        cand += dt.timedelta(days=7)
    return cand


def pick_lesson(region, lang, done):
    ed = f"{region}-{lang}"
    for lid in B.QUEUE:
        if region in B.LESSON_REGIONS[lid] and ed not in done.get(lid, {}):
            return lid
    return None


# ───────────────────────────── render ───────────────────────────────────────

def render_lesson(L, lang, voice, out_dir, region):
    from moviepy.editor import VideoClip, AudioFileClip, concatenate_videoclips
    from PIL import Image
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    clips, srt, chapters, t0, n = [], [], [], 0.0, 1
    for k, sc in enumerate(L["scenes"]):
        text = sc["text"][lang]
        mp3 = str(out_dir / f"scene{k}.mp3")
        try:
            asyncio.run(E._tts(text, voice, mp3))
        except Exception:
            alt = [x for x in E.VOICES[(region, lang)] if x != voice]
            asyncio.run(E._tts(text, alt[0], mp3))
        aud = AudioFileClip(mp3)
        dur = aud.duration + 0.7
        sents = [s.strip() for s in re.split(r"(?<=[.?!।])\s+", text) if s.strip()]
        total = sum(len(s) for s in sents) or 1
        tt = t0
        for s in sents:
            seg = aud.duration * len(s) / total
            srt.append(f"{n}\n{E._srt_time(tt)} --> {E._srt_time(tt + seg)}\n{s}\n")
            n += 1
            tt += seg
        chapters.append((t0, CHAPTER_NAMES.get(sc["kind"], sc["kind"].title())))
        t0 += dur
        mf = sc["visual"](dur)
        if k == 0:
            Image.fromarray(lv.title_scene(L["heading"], L["sub"], tag="TRADING LESSON")(3.5)).convert("RGB").save(str(out_dir / "thumbnail.jpg"), quality=90)
        clips.append(VideoClip(mf, duration=dur).set_audio(aud))
    final = concatenate_videoclips(clips, method="compose")
    name = f"lesson_{L['id']}_{region}_{lang}"
    mp4 = str(out_dir / f"{name}.mp4")
    final.write_videofile(mp4, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    srt_path = out_dir / f"{name}.srt"
    srt_path.write_text("\n".join(srt), encoding="utf-8")
    return mp4, str(srt_path), str(out_dir / "thumbnail.jpg"), chapters, final.duration


def description(L, lang, chapters):
    import money_funnel as mf
    from human_touch import ai_disclosure
    ch = "\n".join(f"{int(t // 60)}:{int(t % 60):02d} {name}" for t, name in chapters)
    try:
        funnel = mf.funnel_block(lang, compact=False)
    except Exception:
        funnel = "Free daily updates: https://t.me/ai360trading" + chr(10) + "Website: https://ai360trading.in"
    # weekly lessons make no next-day promise, so drop any "video tomorrow" line from the shared funnel text
    funnel = chr(10).join(ln for ln in funnel.splitlines() if "kal usi" not in ln.lower() and "tomorrow" not in ln.lower())
    hi = lang == "hi"
    foot = "शिक्षा के लिए, निवेश सलाह नहीं। हम SEBI-पंजीकृत सलाहकार नहीं हैं।" if hi else "Educational only, not investment advice. We are not a registered adviser."
    return f"{L['desc'][lang]}\n\n{ch}\n\n{funnel}\n\n{foot}\n{ai_disclosure(lang)}"


# ───────────────────────────── upload ───────────────────────────────────────

def youtube_service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    raw = os.environ.get("YOUTUBE_CREDENTIALS") or (open("token.json").read() if os.path.exists("token.json") else "")
    if not raw:
        raise RuntimeError("no YouTube credentials")
    return build("youtube", "v3", credentials=Credentials.from_authorized_user_info(json.loads(raw)))


def upload(mp4, title, desc, tags, lang, thumb, srt, publish_at=None):
    from googleapiclient.http import MediaFileUpload
    yt = youtube_service()
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False}
    if publish_at:
        status["publishAt"] = publish_at.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    body = {"snippet": {"title": title[:100], "description": desc[:4900], "tags": tags[:15], "categoryId": "27",
                        "defaultLanguage": lang, "defaultAudioLanguage": lang}, "status": status}
    req = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(mp4, mimetype="video/mp4", resumable=True, chunksize=8 * 1024 * 1024))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    vid = resp["id"]
    try:
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(thumb, mimetype="image/jpeg")).execute()
    except Exception as e:
        print(f"[RUNNER] thumbnail skipped: {e}")
    try:
        from subtitle_helper import upload_caption
        upload_caption(yt, vid, srt, lang)
    except Exception as e:
        print(f"[RUNNER] captions skipped: {e}")
    return vid


# ───────────────────────────── main ─────────────────────────────────────────

def run(region, lang, mode, out_dir, lesson=None):
    done = load_done()
    lid = lesson or pick_lesson(region, lang, done)
    if not lid:
        owner_note(f"lesson queue is EMPTY for {region}-{lang}. Nothing was published this week. Ask Claude to add more lessons.")
        return 0
    print(f"[RUNNER] edition {region}-{lang} -> lesson {lid} (mode={mode})")
    L = B.BUILDERS[lid](region)
    if lang not in L["langs"]:
        print(f"[RUNNER] lesson {lid} has no {lang} edition for {region}")
        return 0
    master = " ".join(s["text"]["en"] for s in L["scenes"])
    ok, why = bank.quality_gate(master, L["facts"], min_words=200)
    if not ok:
        owner_note(f"quality gate FAILED for {lid} ({region}-{lang}): {'; '.join(why)}. Nothing published.")
        return 0
    if lang != "en":
        okn, miss = E.numbers_preserved(master, " ".join(s["text"][lang] for s in L["scenes"]))
        if not okn:
            owner_note(f"translation check FAILED for {lid} ({lang}), missing numbers {miss}. Nothing published.")
            return 0
    voice = E.VOICES[(region, lang)][0]
    mp4, srt, thumb, chapters, dur = render_lesson(L, lang, voice, out_dir, region)
    print(f"[RUNNER] rendered {mp4} ({dur:.0f}s)")
    title, desc = L["title"][lang], description(L, lang, chapters)
    if mode == "dry":
        print(f"[RUNNER] DRY RUN, nothing uploaded.{chr(10)}TITLE: {title}{chr(10)}DESC:{chr(10)}{desc}")
        return 0
    if mode == "private-test":
        vid = upload(mp4, "[TEST - private] " + title, desc, L["tags"][lang], lang, thumb, srt, publish_at=None)
        print(f"[RUNNER] PRIVATE TEST uploaded: https://youtu.be/{vid}  (not announced, not marked done)")
        return 0
    wd, hhmm = PUBLISH_SLOT[(region, lang)]
    when = next_publish(wd, hhmm)
    vid = upload(mp4, title, desc, L["tags"][lang], lang, thumb, srt, publish_at=when)
    print(f"[RUNNER] scheduled {vid} for {when.isoformat()}")
    done.setdefault(lid, {})[f"{region}-{lang}"] = {"video": vid, "publish_at": when.isoformat()}
    save_done(done)
    link = f"https://youtu.be/{vid}"
    if lang == "hi":
        tg(f"<b>नया लेसन</b>: {title}\nलाइव: {when.strftime('%a %d %b, %H:%M')} UTC\n{link}\n\nTelegram: https://t.me/ai360trading")
    else:
        tg(f"<b>New lesson</b>: {title}\nGoes live {when.strftime('%a %d %b, %H:%M')} UTC\n{link}\n\nWebsite: https://ai360trading.in")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", required=True, choices=list(E.REGIONS))
    ap.add_argument("--lang", required=True, choices=["en", "hi"])
    ap.add_argument("--mode", default="scheduled", choices=["scheduled", "private-test", "dry"])
    ap.add_argument("--lesson", default=None)
    ap.add_argument("--out", default="output/lesson")
    a = ap.parse_args()
    try:
        return run(a.region, a.lang, a.mode, a.out, a.lesson)
    except Exception as e:
        owner_note(f"pipeline error for {a.region}-{a.lang}: {str(e)[:200]}. Nothing published; it will retry next week.")
        import traceback
        traceback.print_exc()
        return 0


if __name__ == "__main__":
    sys.exit(main())
