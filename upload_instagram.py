"""
Instagram Uploader
- Tries Content Publishing API (feed video — not Reels format officially)
- If that fails, sends Telegram notification to manually post
- Uses Meta Graph API with Instagram Business account

NOTE: Instagram Reels cannot be posted automatically via API.
      This script posts as a feed video (appears in feed + can be viewed as reel).
      For true Reels format, manual posting via phone is required.
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
META_ACCESS_TOKEN      = os.environ["META_ACCESS_TOKEN"]
INSTAGRAM_ACCOUNT_ID   = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")

OUTPUT_DIR    = Path("output")
GRAPH_BASE    = "https://graph.facebook.com/v21.0"

IG_HASHTAGS = (
    "#reels #ai360trading #ZenoKiBaat #hinglish #motivation "
    "#stockmarket #nifty #india #education #moralstory "
    "#trading #shorts #viral #trending"
)


# ─── INSTAGRAM CONTENT PUBLISHING API ────────────────────────────────────────
def upload_to_instagram(video_url: str, caption: str) -> bool:
    """
    Upload video to Instagram via Content Publishing API.
    video_url must be a PUBLIC URL (not a local file).
    Returns True if successful.
    """
    if not INSTAGRAM_ACCOUNT_ID:
        print("⚠️  INSTAGRAM_ACCOUNT_ID not set — skipping IG API upload.")
        return False

    print("\n📱 Attempting Instagram upload via API...")

    try:
        # Step 1: Create container
        container_data = {
            "media_type":       "REELS",
            "video_url":        video_url,
            "caption":          caption,
            "share_to_feed":    True,
            "access_token":     META_ACCESS_TOKEN,
        }
        resp = requests.post(
            f"{GRAPH_BASE}/{INSTAGRAM_ACCOUNT_ID}/media",
            data=container_data, timeout=60
        )
        resp.raise_for_status()
        container_id = resp.json()["id"]
        print(f"   Container created: {container_id}")

        # Step 2: Wait for processing (poll status)
        max_wait = 120  # seconds
        waited   = 0
        while waited < max_wait:
            time.sleep(10)
            waited += 10
            status_resp = requests.get(
                f"{GRAPH_BASE}/{container_id}",
                params={"fields": "status_code", "access_token": META_ACCESS_TOKEN},
                timeout=15
            )
            status = status_resp.json().get("status_code", "")
            print(f"   Processing status: {status} ({waited}s)")
            if status == "FINISHED":
                break
            if status == "ERROR":
                print("❌ Instagram processing failed.")
                return False

        # Step 3: Publish
        pub_resp = requests.post(
            f"{GRAPH_BASE}/{INSTAGRAM_ACCOUNT_ID}/media_publish",
            data={
                "creation_id":  container_id,
                "access_token": META_ACCESS_TOKEN,
            },
            timeout=30
        )
        pub_resp.raise_for_status()
        media_id = pub_resp.json()["id"]
        print(f"✅ Instagram published! Media ID: {media_id}")
        return True

    except Exception as e:
        print(f"❌ Instagram API error: {e}")
        return False


# ─── TELEGRAM MANUAL POST NOTIFICATION ───────────────────────────────────────
def save_caption_for_instagram(meta: dict, video_path: Path):
    """
    Save caption to output/instagram_caption.txt for manual Instagram posting.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Telegram config missing — skipping manual notification.")
        return

    print("\n📲 Sending manual post notification via Telegram...")

    topic   = meta.get("topic", "Aaj ka lesson")
    nifty   = meta.get("market", {}).get("nifty", {})
    yt_url  = meta.get("youtube_url", "")
    today   = datetime.now().strftime("%d %B %Y")
    weekend = datetime.now().weekday() >= 5

    if weekend:
        caption = (
            f"🎭 ZENO ki baat — {topic.title()}\n"
            f"📅 {today} | Weekend Special\n\n"
            f"💡 Aaj ka life lesson jo aapki zindagi badal sakta hai!\n\n"
        )
    else:
        caption = (
            f"🎭 ZENO ki baat — {topic.title()}\n"
            f"📅 {today}\n\n"
            f"📊 Nifty: {nifty.get('price','N/A')} {nifty.get('change','')}\n\n"
            f"💡 Apni life ka ek important lesson jo aaj zaroor kaam aayega!\n\n"
        )
    if yt_url:
        caption += f"🎬 YouTube: {yt_url}\n\n"
    caption += (
        f"🌐 ai360trading.in | 📱 t.me/ai360trading\n\n"
        f"{IG_HASHTAGS}"
    )

    notification = (
        f"🤖 *AI360 Daily Automation*\n\n"
        f"📹 Aaj ki Instagram Reel ready hai!\n"
        f"*Topic:* {topic}\n\n"
        f"👇 *Caption to copy:*\n\n"
        f"`{caption}`\n\n"
        f"⏰ Please post karo Instagram pe manually.\n"
        f"📁 Video GitHub Actions artifacts mein save hai."
    )

    # Send text notification
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id":    TELEGRAM_CHAT_ID,
                "text":       notification,
                "parse_mode": "Markdown",
            },
            timeout=15
        )
        resp.raise_for_status()
        print("✅ Telegram notification sent!")
    except Exception as e:
        print(f"❌ Telegram notification failed: {e}")

    # Send video file via Telegram (so you can forward directly to Instagram)
    if video_path.exists() and video_path.stat().st_size < 50_000_000:  # < 50MB
        try:
            with open(video_path, "rb") as f:
                resp = requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo",
                    data={"chat_id": TELEGRAM_CHAT_ID, "caption": "📱 Post this to Instagram Reels"},
                    files={"video": f},
                    timeout=120
                )
            resp.raise_for_status()
            print("✅ Video sent to Telegram!")
        except Exception as e:
            print(f"⚠️  Video send failed (file may be too large): {e}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    today     = datetime.now().strftime("%Y%m%d")
    meta_path = OUTPUT_DIR / f"meta_{today}.json"

    if not meta_path.exists():
        raise FileNotFoundError(f"No metadata: {meta_path}")

    meta      = json.loads(meta_path.read_text())
    video     = Path(meta["video_path"])
    yt_url    = meta.get("youtube_url", "")

    topic   = meta.get("topic", "Aaj ka lesson")
    nifty   = meta.get("market", {}).get("nifty", {})
    weekend = datetime.now().weekday() >= 5

    if weekend:
        caption = (
            f"🎭 ZENO ki baat — {topic.title()}\n"
            f"💡 Aaj ka life lesson jo apni zindagi badal dega!\n\n"
        )
    else:
        caption = (
            f"🎭 ZENO ki baat — {topic.title()}\n"
            f"📊 Nifty: {nifty.get('price','N/A')} {nifty.get('change','')}\n\n"
            f"💡 Aaj ka moral lesson jo apni life badal dega!\n\n"
        )
    if yt_url:
        caption += f"🎬 Full video: {yt_url}\n\n"
    caption += f"🌐 ai360trading.in\n\n{IG_HASHTAGS}"

    # Try API first — needs public video URL (e.g. from GitHub release or CDN)
    # If you host video publicly, set this URL:
    public_video_url = meta.get("public_video_url", "")

    ig_success = False
    if public_video_url and INSTAGRAM_ACCOUNT_ID:
        ig_success = upload_to_instagram(public_video_url, caption)

    # Always send Telegram notification for manual backup
    save_caption_for_instagram(meta, video)

    if ig_success:
        print("\n🎉 Instagram auto-post successful!")
    else:
        print("\n📲 Instagram: Video + caption sent to your Telegram for manual posting.")
        print("   TIP: Forward video from Telegram to Instagram directly!")


if __name__ == "__main__":
    main()
