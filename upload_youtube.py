"""
upload_youtube.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uploads ZENO Evening Reel to YouTube.

This script is ONLY for the ZENO evening reel (generate_reel.py output).
- Short 2 and Short 3: uploaded directly inside generate_shorts.py
- Analysis video:      uploaded directly inside generate_analysis.py
- Education video:     uploaded directly inside generate_education.py

Critical chain:
  generate_reel.py → upload_youtube.py → upload_facebook.py → upload_instagram.py

This script reads ALL metadata (title, description, tags) from the meta JSON
file written by generate_reel.py — it does NOT build its own title/description.
This keeps SEO logic in one place (generate_reel.py).

After upload, this script:
1. Writes youtube_video_id and youtube_video_url to meta JSON (needed by upload chain)
2. Writes output/youtube_video_id.txt (used by other scripts if needed)

Last updated: April 2026 — reads full meta from generate_reel.py, no hardcoded tags
"""

import os
import json
import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── CONFIG ───────────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
OUTPUT_DIR   = Path("output")


# ─── AUTH ─────────────────────────────────────────────────────────────────────
def get_service():
    """Authenticates using YOUTUBE_CREDENTIALS environment variable."""
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


# ─── UPLOAD ───────────────────────────────────────────────────────────────────
def upload_video(video_path: Path, title: str, description: str, tags: list):
    """
    Uploads a video to YouTube with resumable upload.
    Returns (video_id, video_url) on success, (None, None) on failure.
    """
    youtube = get_service()
    if not youtube:
        return None, None

    body = {
        "snippet": {
            "title":       title[:100],
            "description": description,
            "tags":        tags[:30],   # YouTube max effective tags
            "categoryId":  "27"         # Education — best for finance monetisation
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
        print(f"✅ YouTube upload success!")
        print(f"   Video ID : {video_id}")
        print(f"   URL      : {video_url}")
        return video_id, video_url

    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        return None, None


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 55)
    print(f" upload_youtube.py — MODE: {CONTENT_MODE.upper()}")
    print("=" * 55)

    today = datetime.datetime.now().strftime("%Y%m%d")

    # ── Find meta file (from generate_reel.py) ────────────────────────────────
    # Look for today's meta first, then most recent
    meta_path = OUTPUT_DIR / f"meta_{today}.json"
    if not meta_path.exists():
        meta_files = sorted(OUTPUT_DIR.glob("meta_*.json"), key=os.path.getmtime, reverse=True)
        meta_path  = meta_files[0] if meta_files else None

    if meta_path and meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"📄 Meta file: {meta_path.name}")
    else:
        meta      = {}
        meta_path = OUTPUT_DIR / f"meta_{today}.json"
        print("⚠️ No meta file found — will create one on upload")

    # ── Find video file ────────────────────────────────────────────────────────
    # Only look for reel files — shorts and analysis have their own upload logic
    video_path = None
    for pattern in [f"reel_{today}.mp4", "reel_*.mp4", "final_zeno_reel.mp4"]:
        candidates = sorted(OUTPUT_DIR.glob(pattern), key=os.path.getmtime, reverse=True)
        if candidates:
            video_path = candidates[0]
            break

    if not video_path:
        print(f"❌ No reel video file found in {OUTPUT_DIR}/ — aborting.")
        print("   Expected: reel_YYYYMMDD.mp4 or final_zeno_reel.mp4")
        return

    print(f"🎥 Video file: {video_path.name}")

    # ── Get title, description, tags from meta (set by generate_reel.py) ──────
    title       = meta.get("title", f"🎯 ZENO Ki Baat — {today} #Shorts")
    description = meta.get("description", "Daily trading wisdom by ZENO. Follow ai360trading.")
    tags        = meta.get("tags", [
        "ai360trading", "ZenoKiBaat", "StockMarket", "Investing",
        "Nifty50", "TradingIndia", "GlobalInvesting", "Shorts"
    ])

    print(f"📝 Title: {title[:60]}...")
    print(f"🏷️  Tags ({len(tags)}): {', '.join(tags[:5])}...")

    # ── Upload ────────────────────────────────────────────────────────────────
    video_id, video_url = upload_video(video_path, title, description, tags)

    if video_id:
        # ── Save video_id to meta — CRITICAL for Instagram chain ──────────────
        meta["youtube_video_id"]  = video_id
        meta["youtube_video_url"] = video_url

        # Instagram needs a public URL — YouTube URL works.
        # upload_facebook.py will overwrite this with FB URL if needed.
        if not meta.get("public_video_url"):
            meta["public_video_url"] = video_url

        meta_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"💾 Saved youtube_video_id to meta: {video_id}")

        # ── Save video_id to txt — used by other workflows if needed ──────────
        id_path = OUTPUT_DIR / "youtube_video_id.txt"
        id_path.write_text(video_id, encoding="utf-8")
        print(f"💾 Saved video ID to: {id_path.name}")

    print("\n" + "=" * 55)
    print(f" upload_youtube.py — {'SUCCESS' if video_id else 'FAILED'}")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
