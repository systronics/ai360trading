"""
Facebook Uploader + Article/Video Link Poster
- Uploads ZENO reel video to Facebook Page as Reel
- Posts article links (4 daily) to Page + Group
- Posts YouTube video link to Page + Group
Uses Meta Graph API (your Business account token)
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
META_ACCESS_TOKEN   = os.environ["META_ACCESS_TOKEN"]     # long-lived page token
FACEBOOK_PAGE_ID    = os.environ["FACEBOOK_PAGE_ID"]
FACEBOOK_GROUP_ID   = os.environ["FACEBOOK_GROUP_ID"]

# Your website RSS or API endpoint — adjust to your WordPress/site setup
WEBSITE_RSS_URL     = os.environ.get("WEBSITE_RSS_URL", "https://ai360trading.in/feed/")
YOUTUBE_CHANNEL_ID  = os.environ.get("YT_CHANNEL_ID", "")

OUTPUT_DIR = Path("output")

GRAPH_BASE = "https://graph.facebook.com/v21.0"

HEADERS = {
    "Authorization": f"Bearer {META_ACCESS_TOKEN}",
    "Content-Type":  "application/json",
}


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def api_post(endpoint: str, data: dict, files=None) -> dict:
    """POST to Meta Graph API with retries."""
    url = f"{GRAPH_BASE}/{endpoint}"
    for attempt in range(3):
        try:
            if files:
                # multipart form for video upload
                resp = requests.post(url, data=data, files=files, timeout=120)
            else:
                resp = requests.post(url, headers=HEADERS, json=data, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            wait = 2 ** (attempt + 1)
            print(f"   API error (retry {attempt+1}/3 in {wait}s): {e}")
            if attempt == 2:
                raise
            time.sleep(wait)


def api_get(endpoint: str, params: dict = None) -> dict:
    url    = f"{GRAPH_BASE}/{endpoint}"
    params = {**(params or {}), "access_token": META_ACCESS_TOKEN}
    resp   = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ─── STEP A: Upload ZENO reel to Facebook Page ───────────────────────────────
def upload_reel_to_facebook(video_path: Path, meta: dict):
    """Upload video as Facebook Reel to page."""
    print("\n📤 Uploading ZENO reel to Facebook Page...")

    topic   = meta.get("topic", "Aaj ka lesson")
    nifty   = meta.get("market", {}).get("nifty",   {})
    yt_url  = meta.get("youtube_url", "")

    caption = (
        f"🎭 ZENO ki baat — {topic}\n\n"
        f"📊 Aaj ka Nifty: {nifty.get('price','N/A')} {nifty.get('change','')}\n\n"
        f"💡 Iss reel mein seekho kuch naya aur apni life mein apply karo!\n\n"
    )
    if yt_url:
        caption += f"🎬 YouTube pe bhi dekho: {yt_url}\n\n"
    caption += (
        "🔔 Follow karo daily market updates + moral lessons ke liye!\n"
        "🌐 ai360trading.in | 📱 Telegram: t.me/ai360trading\n\n"
        "#Reels #ZenoKiBaat #Hinglish #StockMarket #Motivation #ai360trading"
    )

    # Step 1: Initialize upload session
    init_data = {
        "upload_phase":  "start",
        "access_token":  META_ACCESS_TOKEN,
    }
    init_resp = requests.post(
        f"{GRAPH_BASE}/{FACEBOOK_PAGE_ID}/video_reels",
        data=init_data, timeout=20
    )
    init_resp.raise_for_status()
    init_json  = init_resp.json()
    video_id   = init_json["video_id"]
    upload_url = init_json["upload_url"]
    print(f"   Video ID: {video_id}")

    # Step 2: Upload video file
    print("   Uploading video bytes...")
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    upload_headers = {
        "Authorization":  f"OAuth {META_ACCESS_TOKEN}",
        "offset":         "0",
        "file_size":      str(len(video_bytes)),
    }
    up_resp = requests.post(upload_url, headers=upload_headers, data=video_bytes, timeout=180)
    up_resp.raise_for_status()

    # Step 3: Publish
    print("   Publishing reel...")
    pub_data = {
        "upload_phase":  "finish",
        "video_id":      video_id,
        "video_state":   "PUBLISHED",
        "description":   caption,
        "access_token":  META_ACCESS_TOKEN,
    }
    pub_resp = requests.post(
        f"{GRAPH_BASE}/{FACEBOOK_PAGE_ID}/video_reels",
        data=pub_data, timeout=30
    )
    pub_resp.raise_for_status()
    print(f"✅ Facebook Reel published! Video ID: {video_id}")
    return video_id


# ─── STEP B: Fetch today's articles from website ─────────────────────────────
def fetch_today_articles(max_articles: int = 4) -> list:
    """Fetch latest articles from RSS feed."""
    import xml.etree.ElementTree as ET

    print(f"\n📰 Fetching articles from RSS: {WEBSITE_RSS_URL}")
    try:
        resp = requests.get(WEBSITE_RSS_URL, timeout=15,
                            headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        articles = []
        for item in root.findall(".//item")[:max_articles]:
            title = item.findtext("title", "").strip()
            link  = item.findtext("link", "").strip()
            desc  = item.findtext("description", "").strip()
            if title and link:
                # Strip HTML from description
                import re
                desc = re.sub(r"<[^>]+>", "", desc)[:200].strip()
                articles.append({
                    "title": title,
                    "link":  link,
                    "desc":  desc,
                })
        print(f"   Found {len(articles)} articles")
        return articles
    except Exception as e:
        print(f"   RSS fetch error: {e}")
        return []


# ─── STEP C: Post article links to Page + Group ──────────────────────────────
def post_article_links(articles: list):
    """Post article links to Facebook Page and Group."""

    if not articles:
        print("⚠️  No articles to post.")
        return

    today_str = datetime.now().strftime("%d %B %Y")

    # Build combined post message
    post_text = f"📰 Aaj ke top articles — {today_str}\n\n"
    for i, art in enumerate(articles, 1):
        post_text += f"{i}️⃣ {art['title']}\n{art['link']}\n\n"
    post_text += (
        "💡 Daily market insights aur trading signals ke liye visit karo:\n"
        "🌐 ai360trading.in | 📱 t.me/ai360trading\n\n"
        "#StockMarket #Nifty #Trading #ai360trading #India"
    )

    # Post to Page
    print(f"\n📢 Posting articles to Facebook Page...")
    try:
        resp = api_post(f"{FACEBOOK_PAGE_ID}/feed", {
            "message":      post_text,
            "link":         articles[0]["link"],  # primary link for preview
            "access_token": META_ACCESS_TOKEN,
        })
        print(f"✅ Page post ID: {resp.get('id')}")
    except Exception as e:
        print(f"❌ Page post failed: {e}")

    # Post to Group (text only — group API doesn't support link preview reliably)
    print(f"\n👥 Posting articles to Facebook Group...")
    try:
        group_text = post_text + f"\n\n👉 Poori list ke liye visit karo: https://ai360trading.in"
        resp = api_post(f"{FACEBOOK_GROUP_ID}/feed", {
            "message":      group_text,
            "access_token": META_ACCESS_TOKEN,
        })
        print(f"✅ Group post ID: {resp.get('id')}")
    except Exception as e:
        print(f"❌ Group post failed: {e}")


# ─── STEP D: Post YouTube video link to Page + Group ─────────────────────────
def post_youtube_link(yt_url: str, meta: dict):
    """Share YouTube video link to Page + Group."""

    if not yt_url:
        print("⚠️  No YouTube URL to share.")
        return

    topic     = meta.get("topic", "Aaj ka lesson")
    today_str = datetime.now().strftime("%d %B %Y")
    nifty     = meta.get("market", {}).get("nifty", {})

    message = (
        f"🎬 Dekho ZENO ki nai video — {today_str}!\n\n"
        f"📌 Topic: {topic.title()}\n"
        f"📊 Nifty aaj: {nifty.get('price','N/A')} {nifty.get('change','')}\n\n"
        f"👉 Video link: {yt_url}\n\n"
        f"💡 Like, share aur subscribe karo!\n"
        f"🌐 ai360trading.in | 📱 t.me/ai360trading\n\n"
        f"#YouTubeShorts #ZenoKiBaat #StockMarket #Motivation #ai360trading"
    )

    # Page
    print("\n📢 Sharing YouTube link to Facebook Page...")
    try:
        resp = api_post(f"{FACEBOOK_PAGE_ID}/feed", {
            "message":      message,
            "link":         yt_url,
            "access_token": META_ACCESS_TOKEN,
        })
        print(f"✅ Page YT post ID: {resp.get('id')}")
    except Exception as e:
        print(f"❌ Page YT post failed: {e}")

    # Group
    print("👥 Sharing YouTube link to Facebook Group...")
    try:
        resp = api_post(f"{FACEBOOK_GROUP_ID}/feed", {
            "message":      message,
            "link":         yt_url,
            "access_token": META_ACCESS_TOKEN,
        })
        print(f"✅ Group YT post ID: {resp.get('id')}")
    except Exception as e:
        print(f"❌ Group YT post failed: {e}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    today     = datetime.now().strftime("%Y%m%d")
    meta_path = OUTPUT_DIR / f"meta_{today}.json"

    if not meta_path.exists():
        raise FileNotFoundError(f"No metadata: {meta_path}. Run generate_reel.py first.")

    meta      = json.loads(meta_path.read_text())
    video     = Path(meta["video_path"])
    yt_url    = meta.get("youtube_url", "")

    # A: Upload ZENO reel to Facebook
    if video.exists():
        try:
            fb_video_id = upload_reel_to_facebook(video, meta)
            meta["facebook_video_id"] = fb_video_id
        except Exception as e:
            print(f"❌ Facebook reel upload failed: {e}")

    # B: Fetch articles
    articles = fetch_today_articles(max_articles=4)

    # C: Post article links
    post_article_links(articles)

    # D: Post YouTube link
    if yt_url:
        post_youtube_link(yt_url, meta)

    # Save updated meta
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print("\n🎉 Facebook posting complete!")


if __name__ == "__main__":
    main()
