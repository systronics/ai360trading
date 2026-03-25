import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# ─── CONFIG ──────────────────────────────────────────────────────────────────
META_ACCESS_TOKEN    = os.environ.get("META_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")
OUTPUT_DIR = Path("output")
GRAPH_BASE = "https://graph.facebook.com/v21.0"

# Professional, clean hashtag set
IG_HASHTAGS = (
    "#ZenoKiBaat #ai360trading #StockMarketIndia #TradingWisdom "
    "#Nifty50 #PriceAction #Hinglish #FinancialLiteracy #ReelsIndia"
)

def build_caption(meta: dict) -> str:
    """Creates a human-style caption using the AI-generated wisdom."""
    wisdom = meta.get("description", "Aaj ka special trading lesson.")
    # Cleaning description if it has existing hashtags
    wisdom_clean = wisdom.split('#')[0].strip()
    
    today = datetime.now().strftime("%d %b %Y")
    
    # Building a 'Manual' looking caption
    caption = (
        f"✨ ZENO KI BAAT — {today}\n\n"
        f"💡 {wisdom_clean}\n\n"
        f"Consistency and discipline are the keys to the market. 📈\n\n"
        f"🔗 Learn more: https://ai360trading.in\n"
        f"📢 Join us: t.me/ai360trading\n\n"
        f"{IG_HASHTAGS}"
    )
    return caption

def save_caption(caption: str):
    """Saves the caption for manual posting if API fails or URL is missing."""
    caption_path = OUTPUT_DIR / "instagram_caption.txt"
    caption_path.write_text(caption, encoding="utf-8")
    print(f"✅ Caption saved for manual use: {caption_path}")

def upload_to_instagram(video_url: str, caption: str) -> bool:
    """Attempts auto-upload via Meta Graph API."""
    if not INSTAGRAM_ACCOUNT_ID or not META_ACCESS_TOKEN or not video_url:
        print("❌ Missing credentials or Public Video URL for Instagram API.")
        return False

    print("\n📱 Attempting Instagram API upload...")
    try:
        # Step 1: Create Media Container
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": True,
            "access_token": META_ACCESS_TOKEN
        }
        resp = requests.post(f"{GRAPH_BASE}/{INSTAGRAM_ACCOUNT_ID}/media", data=payload, timeout=60)
        resp.raise_for_status()
        container_id = resp.json()["id"]

        # Step 2: Wait for processing (Instagram needs time to process HD video)
        for i in range(20): # Increased retry count
            time.sleep(30) # 30s intervals
            status_resp = requests.get(
                f"{GRAPH_BASE}/{container_id}",
                params={"fields": "status_code", "access_token": META_ACCESS_TOKEN},
                timeout=15
            ).json()
            status = status_resp.get("status_code", "")
            print(f"   Status Check: {status} ({(i+1)*30}s)")
            
            if status == "FINISHED":
                # Step 3: Publish
                pub = requests.post(
                    f"{GRAPH_BASE}/{INSTAGRAM_ACCOUNT_ID}/media_publish",
                    data={"creation_id": container_id, "access_token": META_ACCESS_TOKEN},
                    timeout=30
                )
                pub.raise_for_status()
                print(f"✅ Instagram published! ID: {pub.json()['id']}")
                return True
            elif status == "ERROR":
                print(f"❌ Instagram processing error: {status_resp}")
                return False
        
        print("⌛ Instagram processing timed out.")
        return False
    except Exception as e:
        print(f"❌ Instagram API error: {e}")
        return False

def main():
    today = datetime.now().strftime("%Y%m%d")
    
    # 1. Robust Metadata Detection
    meta_path = OUTPUT_DIR / f"meta_{today}.json"
    if not meta_path.exists():
        # Fallback: Find newest meta file
        meta_files = sorted(OUTPUT_DIR.glob("meta_*.json"), key=os.path.getmtime, reverse=True)
        if meta_files:
            meta_path = meta_files[0]
            print(f"⚠️ Exact date meta not found. Using: {meta_path.name}")
        else:
            print("❌ No meta file found in output folder.")
            return

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    caption = build_caption(meta)
    save_caption(caption)

    # 2. Instagram API Constraint Check
    # Important: Instagram API requires the video to be accessible via a public URL.
    # Files sitting inside a GitHub Runner are not 'public'.
    public_video_url = meta.get("public_video_url", "")
    
    if public_video_url:
        upload_to_instagram(public_video_url, caption)
    else:
        print("\n📲 No public URL found (Instagram API limitation).")
        print("💡 TIP: Download the .mp4 and instagram_caption.txt from GitHub Artifacts for manual posting.")
        print("💡 TIP: To automate this, host your video on a public cloud and update the meta 'public_video_url'.")

if __name__ == "__main__":
    main()
