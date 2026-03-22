"""
YouTube Shorts Uploader
Uploads the daily ZENO reel to YouTube Shorts section
Uses YouTube Data API v3 with OAuth2 (service account or refresh token)
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime

# Google API
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# ─── CONFIG ───────────────────────────────────────────────────────────────────
YT_CLIENT_ID      = os.environ["YT_CLIENT_ID"]
YT_CLIENT_SECRET  = os.environ["YT_CLIENT_SECRET"]
YT_REFRESH_TOKEN  = os.environ["YT_REFRESH_TOKEN"]   # get via OAuth2 flow once

OUTPUT_DIR = Path("output")

SHORTS_HASHTAGS = "#Shorts #ai360trading #ZenoKiBaat #HinglishMotivation #StockMarket #NiftyToday"

DESCRIPTION_TEMPLATE = """
🎭 ZENO ki baat — aaj ka lesson: {topic}

📊 Aaj ka market:
• Nifty: {nifty_price} ({nifty_change})
• Bitcoin: {btc_price} ({btc_change})

💡 Agar ye video helpful laga toh like karo, share karo, aur channel subscribe karo!

🔔 Daily stock signals aur moral lessons ke liye follow karo:
🌐 Website: https://ai360trading.in
📱 Telegram: https://t.me/ai360trading

{hashtags}
"""


def get_youtube_client():
    """Build authenticated YouTube API client using refresh token."""
    creds = Credentials(
        token         = None,
        refresh_token = YT_REFRESH_TOKEN,
        token_uri     = "https://oauth2.googleapis.com/token",
        client_id     = YT_CLIENT_ID,
        client_secret = YT_CLIENT_SECRET,
        scopes        = ["https://www.googleapis.com/auth/youtube.upload"],
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def build_description(meta: dict) -> str:
    market = meta.get("market", {})
    nifty  = market.get("nifty",   {"price": "N/A", "change": "N/A"})
    btc    = market.get("bitcoin", {"price": "N/A", "change": "N/A"})
    return DESCRIPTION_TEMPLATE.format(
        topic        = meta.get("topic", "Aaj ka lesson"),
        nifty_price  = nifty["price"],
        nifty_change = nifty["change"],
        btc_price    = btc["price"],
        btc_change   = btc["change"],
        hashtags     = SHORTS_HASHTAGS,
    ).strip()


def upload_to_youtube(video_path: Path, meta: dict) -> str:
    """Upload video to YouTube Shorts. Returns video ID."""

    print("🔐 Authenticating with YouTube...")
    yt = get_youtube_client()

    title = f"ZENO ki baat: {meta['topic']} | {datetime.now().strftime('%d %b %Y')} | #Shorts"
    title = title[:100]  # YouTube title limit

    description = build_description(meta)
    hook = meta.get("hook", "")
    if hook:
        description = f"{hook}\n\n{description}"

    body = {
        "snippet": {
            "title":       title,
            "description": description,
            "tags": [
                "shorts", "ai360trading", "zeno", "hinglish",
                "motivation", "nifty", "stockmarket", "moralstory",
                "education", "india",
            ],
            "categoryId":        "27",  # Education
            "defaultLanguage":   "hi",
            "defaultAudioLanguage": "hi",
        },
        "status": {
            "privacyStatus":          "public",
            "selfDeclaredMadeForKids": False,
            "madeForKids":             False,
        },
    }

    media = MediaFileUpload(
        str(video_path),
        mimetype   = "video/mp4",
        resumable  = True,
        chunksize  = 4 * 1024 * 1024,  # 4MB chunks
    )

    print(f"📤 Uploading to YouTube Shorts: {title}")
    request = yt.videos().insert(
        part        = "snippet,status",
        body        = body,
        media_body  = media,
    )

    response = None
    retry    = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"   Upload progress: {pct}%")
        except Exception as e:
            retry += 1
            if retry > 5:
                raise
            wait = 2 ** retry
            print(f"   Upload error (retry {retry}/5 in {wait}s): {e}")
            time.sleep(wait)

    video_id = response["id"]
    url = f"https://youtube.com/shorts/{video_id}"
    print(f"✅ YouTube Shorts uploaded: {url}")
    return video_id


def main():
    today     = datetime.now().strftime("%Y%m%d")
    meta_path = OUTPUT_DIR / f"meta_{today}.json"
    video_path_key = f"video_path"

    if not meta_path.exists():
        raise FileNotFoundError(f"No metadata found: {meta_path}. Run generate_reel.py first.")

    meta  = json.loads(meta_path.read_text())
    video = Path(meta["video_path"])

    if not video.exists():
        raise FileNotFoundError(f"Video not found: {video}")

    video_id = upload_to_youtube(video, meta)

    # Save video ID back to metadata for other uploaders to use
    meta["youtube_video_id"] = video_id
    meta["youtube_url"]      = f"https://youtube.com/shorts/{video_id}"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    print(f"\n🎉 YouTube upload complete!")
    print(f"   URL: {meta['youtube_url']}")


if __name__ == "__main__":
    main()
