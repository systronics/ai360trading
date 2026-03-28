"""
upload_instagram.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uploads ZENO Reel to Instagram via Meta Graph API.

How public_video_url works:
  - upload_facebook.py runs FIRST and uploads the reel to Facebook Page
  - It saves the Facebook watch URL into meta_YYYYMMDD.json
  - This script reads that URL and gives it to Instagram API
  - Instagram fetches the video from that public Facebook URL
  - This means NO separate video hosting is needed

Flow:
  generate_reel.py → upload_youtube.py → upload_facebook.py → upload_instagram.py

If Instagram API fails:
  - Caption is saved to output/instagram_caption.txt
  - Video is in GitHub Artifacts (zeno-reel-package)
  - Download artifact → post manually to Instagram app

Last updated: March 2026
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
META_ACCESS_TOKEN    = os.environ.get("META_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")
CONTENT_MODE         = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME         = os.environ.get("HOLIDAY_NAME", "")
OUTPUT_DIR           = Path("output")
GRAPH_BASE           = "https://graph.facebook.com/v21.0"
MAX_STATUS_CHECKS    = 24   # 24 × 15s = 6 minutes max wait
STATUS_INTERVAL      = 15   # seconds between status checks

IG_HASHTAGS = (
    "#ZenoKiBaat #ai360trading #StockMarketIndia #TradingWisdom "
    "#Nifty50 #PriceAction #Hinglish #FinancialLiteracy #ReelsIndia "
    "#USStocks #UKInvesting #BrazilMarket #GlobalInvesting"
)


# ─── CAPTION BUILDER ──────────────────────────────────────────────────────────
def build_caption(meta: dict) -> str:
    """
    Builds a human-style, mode-aware Instagram caption.
    """
    wisdom = meta.get("description", "Aaj ka special trading lesson.")
    wisdom_clean = wisdom.split('#')[0].strip()
    today = datetime.now().strftime("%d %b %Y")

    if CONTENT_MODE == "holiday":
        label = f"🎉 {HOLIDAY_NAME}" if HOLIDAY_NAME else "🎉 Market Holiday"
        intro = f"✨ ZENO KI BAAT — {label} Special"
        body  = (
            f"💡 {wisdom_clean}\n\n"
            f"Market band hai, par learning band nahi! 📚\n\n"
            f"💰 Best time to plan your next trade. 📊"
        )
    elif CONTENT_MODE == "weekend":
        intro = f"✨ ZENO KI BAAT — Weekend Wisdom"
        body  = (
            f"💡 {wisdom_clean}\n\n"
            f"Weekends are for learning, not forgetting! 📚\n\n"
            f"Consistency aur discipline hi success ka raasta hai. 🎯"
        )
    else:
        intro = f"✨ ZENO KI BAAT — {today}"
        body  = (
            f"💡 {wisdom_clean}\n\n"
            f"Market dynamics ko samjhein aur discipline banaye rakhein. 📈\n\n"
            f"Aaj ka lesson yaad rakho — kal ka profit ensure karo! 💰"
        )

    caption = (
        f"{intro}\n\n"
        f"{body}\n\n"
        f"🔗 Learn more: https://ai360trading.in\n"
        f"📢 Join us: t.me/ai360trading\n\n"
        f"{IG_HASHTAGS}"
    )
    return caption


def save_caption_for_manual(caption: str):
    """Saves caption to file — always, as backup for manual posting."""
    path = OUTPUT_DIR / "instagram_caption.txt"
    path.write_text(caption, encoding="utf-8")
    print(f"  💾 Caption saved: {path}")


# ─── INSTAGRAM UPLOAD ─────────────────────────────────────────────────────────
def upload_to_instagram(video_url: str, caption: str) -> bool:
    """
    Uploads reel to Instagram via Meta Graph API.

    Requires:
      - INSTAGRAM_ACCOUNT_ID: your IG Business/Creator account ID
      - META_ACCESS_TOKEN: with instagram_basic + instagram_content_publish scopes
      - video_url: a publicly accessible video URL (Facebook watch URL works)

    Returns True on success, False on failure.
    """
    if not INSTAGRAM_ACCOUNT_ID:
        print("  ❌ INSTAGRAM_ACCOUNT_ID not set in GitHub Secrets.")
        print("  💡 Add it: GitHub → Settings → Secrets → INSTAGRAM_ACCOUNT_ID")
        return False

    if not META_ACCESS_TOKEN:
        print("  ❌ META_ACCESS_TOKEN not set.")
        return False

    if not video_url:
        print("  ❌ No public video URL provided.")
        return False

    print(f"\n📱 Starting Instagram upload...")
    print(f"  Video URL: {video_url[:80]}...")

    # Step 1: Create media container
    try:
        print("  Step 1/3: Creating media container...")
        resp = requests.post(
            f"{GRAPH_BASE}/{INSTAGRAM_ACCOUNT_ID}/media",
            data={
                "media_type":    "REELS",
                "video_url":     video_url,
                "caption":       caption,
                "share_to_feed": True,
                "access_token":  META_ACCESS_TOKEN
            },
            timeout=60
        )
        result = resp.json()

        if "id" not in result:
            error = result.get("error", {})
            code  = error.get("code", "?")
            msg   = error.get("message", str(result))
            print(f"  ❌ Container creation failed — Error {code}: {msg}")
            if code == 10:
                print("  💡 FIX: Token missing 'instagram_content_publish' permission.")
                print("     Regenerate at developers.facebook.com with IG publish scope.")
            if code == 24:
                print("  💡 FIX: Instagram account not connected to a Facebook Page.")
                print("     Connect at: Instagram → Settings → Account → Linked Accounts")
            return False

        container_id = result["id"]
        print(f"  ✅ Container created — ID: {container_id}")

    except Exception as e:
        print(f"  ❌ Container creation error: {e}")
        return False

    # Step 2: Poll for processing completion
    print(f"  Step 2/3: Waiting for Instagram to process video...")
    print(f"            (Checking every {STATUS_INTERVAL}s, max {MAX_STATUS_CHECKS * STATUS_INTERVAL // 60} min)")

    for check in range(1, MAX_STATUS_CHECKS + 1):
        time.sleep(STATUS_INTERVAL)
        try:
            status_resp = requests.get(
                f"{GRAPH_BASE}/{container_id}",
                params={
                    "fields":       "status_code,status",
                    "access_token": META_ACCESS_TOKEN
                },
                timeout=15
            ).json()

            status_code = status_resp.get("status_code", "")
            status_msg  = status_resp.get("status", "")
            elapsed     = check * STATUS_INTERVAL

            print(f"  [{elapsed:>3}s] Status: {status_code} {status_msg}")

            if status_code == "FINISHED":
                print(f"  ✅ Processing complete!")
                break
            elif status_code == "ERROR":
                print(f"  ❌ Instagram processing error: {status_resp}")
                print(f"  💡 Common causes:")
                print(f"     - Video codec not supported (need H.264)")
                print(f"     - Video too short (min 3s) or too long (max 15min)")
                print(f"     - URL not publicly accessible")
                return False
            elif status_code == "IN_PROGRESS":
                continue
            else:
                print(f"  ⚠️  Unknown status: {status_resp}")

        except Exception as e:
            print(f"  ⚠️  Status check error: {e}")
    else:
        print(f"  ⌛ Timed out after {MAX_STATUS_CHECKS * STATUS_INTERVAL}s")
        print(f"  💡 The video may still be processing. Check your Instagram account.")
        return False

    # Step 3: Publish
    try:
        print(f"  Step 3/3: Publishing to Instagram...")
        pub_resp = requests.post(
            f"{GRAPH_BASE}/{INSTAGRAM_ACCOUNT_ID}/media_publish",
            data={
                "creation_id":  container_id,
                "access_token": META_ACCESS_TOKEN
            },
            timeout=30
        )
        pub_result = pub_resp.json()

        if "id" in pub_result:
            post_id = pub_result["id"]
            print(f"  ✅ Instagram Reel Published! Post ID: {post_id}")
            return True
        else:
            error = pub_result.get("error", {})
            print(f"  ❌ Publish failed: {error.get('message', str(pub_result))}")
            return False

    except Exception as e:
        print(f"  ❌ Publish error: {e}")
        return False


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 55)
    print(f"  upload_instagram.py — MODE: {CONTENT_MODE.upper()}")
    print("=" * 55)

    # ── Find latest meta file ──────────────────────────────────────────────
    today = datetime.now().strftime("%Y%m%d")
    meta_path = OUTPUT_DIR / f"meta_{today}.json"

    if not meta_path.exists():
        meta_files = sorted(OUTPUT_DIR.glob("meta_*.json"), key=os.path.getmtime, reverse=True)
        if meta_files:
            meta_path = meta_files[0]
            print(f"  ⚠️  Using most recent meta: {meta_path.name}")
        else:
            print("  ❌ No meta_*.json found in output/ — nothing to post.")
            return

    meta    = json.loads(meta_path.read_text(encoding="utf-8"))
    caption = build_caption(meta)

    # Always save caption as backup
    save_caption_for_manual(caption)

    # ── Get public video URL ───────────────────────────────────────────────
    # upload_facebook.py saves this after uploading the reel to FB Page.
    # If it's empty, Instagram API cannot work (needs public URL).
    public_video_url = meta.get("public_video_url", "").strip()

    if not public_video_url:
        print("\n  ⚠️  No public_video_url in meta file.")
        print("  This means upload_facebook.py either:")
        print("    (a) Did not run yet, or")
        print("    (b) Failed to upload the reel to Facebook Page")
        print("\n  📲 MANUAL POST INSTRUCTIONS:")
        print("    1. Go to GitHub Actions → This run → Artifacts")
        print("    2. Download 'zeno-reel-*' artifact")
        print("    3. Open instagram_caption.txt for the caption")
        print("    4. Post the .mp4 manually to Instagram")
        return

    # ── Attempt Instagram API upload ───────────────────────────────────────
    success = upload_to_instagram(public_video_url, caption)

    if not success:
        print("\n  📲 AUTO-POST FAILED — Use manual posting instead:")
        print("    1. GitHub Actions → Artifacts → Download 'zeno-reel-*'")
        print("    2. Use the saved instagram_caption.txt for the caption")

    print("\n" + "=" * 55)
    print("  upload_instagram.py — DONE")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
