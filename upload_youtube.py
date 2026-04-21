"""
upload_youtube.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uploads reels to YouTube. Handles two reel types:

  --type morning   →  morning_reel_YYYYMMDD.mp4
                      morning_reel_meta_YYYYMMDD.json

  --type reel      →  reel_YYYYMMDD.mp4  (ZENO evening reel)
      (default)        meta_YYYYMMDD.json

This script is ONLY for reels. Shorts and analysis/education videos
have their own upload logic inside their respective generator scripts.

Critical chain for ZENO reel:
  generate_reel.py → upload_youtube.py --type reel
                   → upload_facebook.py
                   → upload_instagram.py

Critical chain for morning reel:
  generate_reel_morning.py → upload_youtube.py --type morning
                           → upload_facebook.py --meta-prefix morning
                           → upload_instagram.py

Last updated: April 2026 — added --type morning support
"""

import os
import sys
import json
import argparse
import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
OUTPUT_DIR   = Path("output")


def parse_args():
    parser = argparse.ArgumentParser(description="Upload reel to YouTube")
    parser.add_argument(
        "--type",
        choices=["morning", "reel"],
        default="reel",
        help="Type of reel: 'morning' or 'reel' (default: reel)"
    )
    return parser.parse_args()


def resolve_files(reel_type: str):
    """Returns (video_path, meta_path) for the given reel type."""
    today = datetime.datetime.now().strftime("%Y%m%d")

    if reel_type == "morning":
        video_patterns = [f"morning_reel_{today}.mp4", "morning_reel_*.mp4"]
        meta_patterns  = [f"morning_reel_meta_{today}.json", "morning_reel_meta_*.json"]
    else:
        video_patterns = [f"reel_{today}.mp4", "final_zeno_reel.mp4", "reel_*.mp4"]
        meta_patterns  = [f"meta_{today}.json", "meta_*.json"]

    video_path = None
    for pattern in video_patterns:
        candidates = sorted(OUTPUT_DIR.glob(pattern), key=os.path.getmtime, reverse=True)
        if candidates:
            video_path = candidates[0]
            break

    meta_path = None
    for pattern in meta_patterns:
        candidates = sorted(OUTPUT_DIR.glob(pattern), key=os.path.getmtime, reverse=True)
        if candidates:
            meta_path = candidates[0]
            break

    return video_path, meta_path


def get_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json:
            if os.path.exists("token.json"):
                with open("token.json") as f:
                    creds_json = f.read()
            else:
                print("❌ YOUTUBE_CREDENTIALS secret not set.")
                return None
        creds   = Credentials.from_authorized_user_info(json.loads(creds_json))
        service = build("youtube", "v3", credentials=creds)
        print("✅ YouTube authenticated")
        return service
    except Exception as e:
        print(f"❌ YouTube auth error: {e}")
        return None


def upload_video(video_path: Path, title: str, description: str, tags: list):
    youtube = get_service()
    if not youtube:
        return None, None

    body = {
        "snippet": {
            "title":       title[:100],
            "description": description,
            "tags":        tags[:30],
            "categoryId":  "27"
        },
        "status": {
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"🚀 Uploading to YouTube: {title[:70]}...")

    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  {int(status.progress() * 100)}%")
        video_id  = response["id"]
        video_url = f"https://youtube.com/shorts/{video_id}"
        print(f"✅ YouTube upload success! ID: {video_id}")
        print(f"   URL: {video_url}")
        return video_id, video_url
    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        return None, None


def build_fallback_metadata(reel_type: str, today: str):
    """Last-resort metadata when no meta file found."""
    try:
        from human_touch import ht, seo
        tags = seo.get_video_tags(mode=CONTENT_MODE, is_short=True)
    except Exception:
        tags = ["ai360trading", "StockMarket", "Nifty50", "Investing", "Shorts"]

    hashtag_str = " ".join([f"#{t}" for t in tags[:12]])

    if reel_type == "morning":
        title = f"🌅 Morning Trading Brief — ai360trading #{today[-4:]} #Shorts"
        desc  = (
            f"🌅 Morning market update for traders\n\n"
            f"🌍 For investors: India, USA, UK, Brazil & UAE\n"
            f"🌐 https://ai360trading.in\n"
            f"📱 https://t.me/ai360trading\n"
            f"⚠️ Educational content only. Not financial advice.\n\n"
            f"#ai360trading #MorningBrief {hashtag_str}"
        )
    else:
        title = f"🎯 ZENO Ki Baat — Trading Wisdom #{today[-4:]} #Shorts"
        desc  = (
            f"🎯 Daily trading wisdom by ZENO\n\n"
            f"🌍 For investors: India, USA, UK, Brazil & UAE\n"
            f"🌐 https://ai360trading.in\n"
            f"📱 https://t.me/ai360trading\n"
            f"⚠️ Educational content only. Not financial advice.\n\n"
            f"#ZenoKiBaat #ai360trading {hashtag_str}"
        )
    return title, desc, tags


def main():
    args      = parse_args()
    reel_type = args.type
    today     = datetime.datetime.now().strftime("%Y%m%d")

    print("\n" + "=" * 55)
    print(f" upload_youtube.py — TYPE: {reel_type.upper()} | MODE: {CONTENT_MODE.upper()}")
    print("=" * 55)

    # ── Find files ────────────────────────────────────────────────────────────
    video_path, meta_path = resolve_files(reel_type)

    if not video_path:
        print(f"❌ No {reel_type} video file found in {OUTPUT_DIR}/ — aborting.")
        if reel_type == "morning":
            print("   Expected: morning_reel_YYYYMMDD.mp4")
        else:
            print("   Expected: reel_YYYYMMDD.mp4 or final_zeno_reel.mp4")
        sys.exit(1)

    print(f"🎥 Video file: {video_path.name}")

    # ── Load meta ─────────────────────────────────────────────────────────────
    if meta_path and meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"📄 Meta file: {meta_path.name}")
    else:
        meta = {}
        meta_path = OUTPUT_DIR / (
            f"morning_reel_meta_{today}.json" if reel_type == "morning"
            else f"meta_{today}.json"
        )
        print("⚠️ No meta file found — using fallback metadata")

    # ── Get title / description / tags ────────────────────────────────────────
    title       = meta.get("title")
    description = meta.get("description")
    tags        = meta.get("tags")

    if not title or not description or not tags:
        print("⚠️ Meta incomplete — building fallback")
        title, description, tags = build_fallback_metadata(reel_type, today)

    print(f"📝 Title: {title[:60]}...")
    print(f"🏷️  Tags ({len(tags)}): {', '.join(tags[:5])}...")

    # ── Upload ────────────────────────────────────────────────────────────────
    video_id, video_url = upload_video(video_path, title, description, tags)

    if video_id:
        meta["title"]             = title
        meta["description"]       = description
        meta["tags"]              = tags
        meta["youtube_video_id"]  = video_id
        meta["youtube_video_url"] = video_url
        if not meta.get("public_video_url"):
            meta["public_video_url"] = video_url

        meta_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"💾 Saved youtube_video_id to meta: {video_id}")

        id_path = OUTPUT_DIR / "youtube_video_id.txt"
        id_path.write_text(video_id, encoding="utf-8")
        print(f"💾 Saved video ID to: {id_path.name}")

    print("\n" + "=" * 55)
    print(f" upload_youtube.py — {'SUCCESS' if video_id else 'FAILED'}")
    print("=" * 55 + "\n")

    if not video_id:
        sys.exit(1)


if __name__ == "__main__":
    main()
