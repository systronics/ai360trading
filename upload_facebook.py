import os
import json
import time
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
META_ACCESS_TOKEN   = os.environ.get("META_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID    = os.environ.get("FACEBOOK_PAGE_ID", "")
FACEBOOK_GROUP_ID   = os.environ.get("FACEBOOK_GROUP_ID", "")
WEBSITE_RSS_URL     = "https://ai360trading.in/feed/"
OUTPUT_DIR          = Path("output")
GRAPH_BASE          = "https://graph.facebook.com/v21.0"

# ─── STEP A: Upload ZENO Reel ────────────────────────────────────────────────
def upload_reel_to_facebook(video_path: Path, meta: dict):
    """Uploads the ZENO video as an official Facebook Reel."""
    print(f"\n🎬 Processing Facebook Reel: {video_path.name}")

    # Use the AI-generated wisdom for the caption
    wisdom = meta.get("description", "Daily Trading Wisdom by Zeno.")
    wisdom_clean = wisdom.split('#')[0].strip()
    
    caption = (
        f"🎭 ZENO KI BAAT ✨\n\n"
        f"💡 {wisdom_clean}\n\n"
        f"Market dynamics ko samjhein aur discipline banaye rakhein. 📈\n\n"
        f"🌐 Website: https://ai360trading.in\n"
        f"📱 Telegram: t.me/ai360trading\n\n"
        f"#Reels #ZenoKiBaat #ai360trading #StockMarketIndia #TradingMotivation"
    )

    # 1. Start Upload Session
    init_url = f"{GRAPH_BASE}/{FACEBOOK_PAGE_ID}/video_reels"
    resp = requests.post(init_url, data={
        "upload_phase": "start",
        "access_token": META_ACCESS_TOKEN
    }, timeout=30).json()
    
    video_id = resp.get("video_id")
    upload_url = resp.get("upload_url")

    # 2. Upload Bytes
    with open(video_path, "rb") as f:
        video_data = f.read()
    
    requests.post(upload_url, headers={
        "Authorization": f"OAuth {META_ACCESS_TOKEN}",
        "offset": "0",
        "file_size": str(len(video_data))
    }, data=video_data, timeout=300).raise_for_status()

    # 3. Publish Reel
    publish_resp = requests.post(init_url, data={
        "upload_phase": "finish",
        "video_id": video_id,
        "video_state": "PUBLISHED",
        "description": caption,
        "access_token": META_ACCESS_TOKEN
    }, timeout=30).json()

    if "success" in str(publish_resp).lower() or video_id:
        print(f"✅ Facebook Reel Published! ID: {video_id}")
        return video_id
    return None

# ─── STEP B: Fetch & Post Articles ──────────────────────────────────────────
def post_articles():
    """Fetches top 4 articles and posts them as a summary list."""
    print(f"\n📰 Fetching latest from {WEBSITE_RSS_URL}")
    try:
        resp = requests.get(WEBSITE_RSS_URL, timeout=20)
        root = ET.fromstring(resp.content)
        articles = []
        for item in root.findall(".//item")[:4]:
            articles.append({
                "title": item.findtext("title"),
                "link": item.findtext("link")
            })
        
        if not articles: return

        # Build human-style post
        post_msg = "🚀 Aaj ki Top Trading Updates — Must Read!\n\n"
        for i, art in enumerate(articles, 1):
            post_msg += f"{i}️⃣ {art['title']}\n🔗 {art['link']}\n\n"
        
        post_msg += "Keep learning, keep trading! 📊\n#ai360trading #StockMarket #Updates"

        # Post to Page
        requests.post(f"{GRAPH_BASE}/{FACEBOOK_PAGE_ID}/feed", data={
            "message": post_msg,
            "access_token": META_ACCESS_TOKEN
        }, timeout=30)
        
        # Post to Group
        if FACEBOOK_GROUP_ID:
            requests.post(f"{GRAPH_BASE}/{FACEBOOK_GROUP_ID}/feed", data={
                "message": post_msg,
                "access_token": META_ACCESS_TOKEN
            }, timeout=30)
            
        print(f"✅ Articles shared to Page and Group.")
    except Exception as e:
        print(f"⚠️ Article sharing skipped: {e}")

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    today = datetime.now().strftime("%Y%m%d")
    meta_path = OUTPUT_DIR / f"meta_{today}.json"

    if not meta_path.exists():
        print("❌ Meta file not found. Run generator first.")
        return

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    video_path = Path(meta.get("video_path", ""))

    # 1. Video Reel Upload
    if video_path.exists():
        upload_reel_to_facebook(video_path, meta)
    
    # 2. Automated Article Summary (Human-style hard work look)
    post_articles()

if __name__ == "__main__":
    main()
