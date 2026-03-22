"""
Instagram Uploader
- Tries Content Publishing API if INSTAGRAM_ACCOUNT_ID is set
- Saves caption to output/instagram_caption.txt for manual posting
- No Telegram — download video + caption from GitHub Actions artifacts
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

META_ACCESS_TOKEN    = os.environ.get("META_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
GRAPH_BASE = "https://graph.facebook.com/v21.0"

IG_HASHTAGS = (
    "#reels #ai360trading #ZenoKiBaat #hinglish #motivation "
    "#stockmarket #nifty #india #education #moralstory "
    "#trading #shorts #viral #trending"
)


def build_caption(meta: dict) -> str:
    topic   = meta.get("topic", "Aaj ka lesson")
    nifty   = meta.get("market", {}).get("nifty", {})
    yt_url  = meta.get("youtube_url", "")
    today   = datetime.now().strftime("%d %B %Y")
    weekend = datetime.now().weekday() >= 5

    if weekend:
        caption = (
            f"ZENO ki baat — {topic.title()}\n"
            f"{today} | Weekend Special\n\n"
            f"Aaj ka life lesson jo aapki zindagi badal sakta hai!\n\n"
        )
    else:
        caption = (
            f"ZENO ki baat — {topic.title()}\n"
            f"{today}\n\n"
            f"Nifty: {nifty.get('price','N/A')} {nifty.get('change','')}\n\n"
            f"Apni life ka ek important lesson jo aaj zaroor kaam aayega!\n\n"
        )
    if yt_url:
        caption += f"YouTube: {yt_url}\n\n"
    caption += f"ai360trading.in | t.me/ai360trading\n\n{IG_HASHTAGS}"
    return caption


def save_caption(caption: str):
    caption_path = OUTPUT_DIR / "instagram_caption.txt"
    caption_path.write_text(caption, encoding="utf-8")
    print(f"✅ Caption saved: {caption_path}")
    print(f"\n📋 Preview:\n{caption[:200]}...")


def upload_to_instagram(video_url: str, caption: str) -> bool:
    if not INSTAGRAM_ACCOUNT_ID or not META_ACCESS_TOKEN:
        print("⚠️  Instagram credentials not set — skipping API upload.")
        return False
    print("\n📱 Attempting Instagram API upload...")
    try:
        resp = requests.post(
            f"{GRAPH_BASE}/{INSTAGRAM_ACCOUNT_ID}/media",
            data={"media_type": "REELS", "video_url": video_url,
                  "caption": caption, "share_to_feed": True,
                  "access_token": META_ACCESS_TOKEN},
            timeout=60
        )
        resp.raise_for_status()
        container_id = resp.json()["id"]
        print(f"   Container: {container_id}")
        for i in range(12):
            time.sleep(10)
            s = requests.get(f"{GRAPH_BASE}/{container_id}",
                params={"fields": "status_code", "access_token": META_ACCESS_TOKEN},
                timeout=15).json().get("status_code", "")
            print(f"   Status: {s} ({(i+1)*10}s)")
            if s == "FINISHED": break
            if s == "ERROR": return False
        pub = requests.post(
            f"{GRAPH_BASE}/{INSTAGRAM_ACCOUNT_ID}/media_publish",
            data={"creation_id": container_id, "access_token": META_ACCESS_TOKEN},
            timeout=30)
        pub.raise_for_status()
        print(f"✅ Instagram published! ID: {pub.json()['id']}")
        return True
    except Exception as e:
        print(f"❌ Instagram API error: {e}")
        return False


def main():
    today     = datetime.now().strftime("%Y%m%d")
    meta_path = OUTPUT_DIR / f"meta_{today}.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"No metadata: {meta_path}")

    meta    = json.loads(meta_path.read_text())
    caption = build_caption(meta)
    save_caption(caption)

    public_video_url = meta.get("public_video_url", "")
    if public_video_url and INSTAGRAM_ACCOUNT_ID:
        upload_to_instagram(public_video_url, caption)
    else:
        print("\n📲 Download video + instagram_caption.txt from artifacts → post manually.")


if __name__ == "__main__":
    main()
