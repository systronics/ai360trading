"""
upload_facebook.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uploads ZENO Reel to Facebook Page + Group, and shares articles.

Facebook Group posting requires:
  - Token must have: publish_to_groups permission scope
  - Bot account must be an ADMIN of the group (not just member)
  - App must be approved for Groups API by Meta
  - Group must allow posts from apps (Group Settings → Advanced)

Token refresh: Every 60 days via Meta Developer Console.
Last updated: March 2026
"""

import os
import json
import time
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID  = os.environ.get("FACEBOOK_PAGE_ID", "")
FACEBOOK_GROUP_ID = os.environ.get("FACEBOOK_GROUP_ID", "")
CONTENT_MODE      = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME      = os.environ.get("HOLIDAY_NAME", "")
WEBSITE_RSS_URL   = "https://ai360trading.in/feed/"
OUTPUT_DIR        = Path("output")
GRAPH_BASE        = "https://graph.facebook.com/v21.0"
MAX_RETRIES       = 3
RETRY_DELAY       = 10  # seconds between retries


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def post_to_entity(entity_id: str, label: str, data: dict) -> bool:
    """
    Posts to a Facebook Page or Group feed with retry logic.
    Returns True on success, False on failure.
    Logs the full API error response so failures are visible in GitHub Actions.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(
                f"{GRAPH_BASE}/{entity_id}/feed",
                data={**data, "access_token": META_ACCESS_TOKEN},
                timeout=30
            )
            result = resp.json()

            if "id" in result:
                print(f"  ✅ {label} posted successfully — Post ID: {result['id']}")
                return True
            else:
                # Surface the exact Meta error — critical for diagnosing Group issues
                error = result.get("error", {})
                code    = error.get("code", "?")
                subcode = error.get("error_subcode", "")
                msg     = error.get("message", str(result))
                fbt     = error.get("fbtrace_id", "")
                print(f"  ❌ {label} post failed (attempt {attempt}/{MAX_RETRIES})")
                print(f"     Error {code}/{subcode}: {msg}")
                if fbt:
                    print(f"     fbtrace_id: {fbt}  ← paste this to Meta Support")
                if code == 200:
                    print(f"     💡 FIX: Token missing 'publish_to_groups' permission.")
                    print(f"        Re-generate token at developers.facebook.com with this scope.")
                    break  # Retrying won't help for permission errors
                if code == 100 and "group" in msg.lower():
                    print(f"     💡 FIX: Bot account must be an ADMIN of the group.")
                    print(f"        Also check: Group Settings → Advanced → Allow content from apps.")
                    break  # Retrying won't help

        except requests.exceptions.Timeout:
            print(f"  ⏱️  {label} request timed out (attempt {attempt}/{MAX_RETRIES})")
        except Exception as e:
            print(f"  ⚠️  {label} unexpected error (attempt {attempt}/{MAX_RETRIES}): {e}")

        if attempt < MAX_RETRIES:
            print(f"     Retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)

    print(f"  ✗ {label} — all {MAX_RETRIES} attempts failed.")
    return False


def verify_token_permissions():
    """
    Checks if the token has the required permissions.
    Prints a clear warning if publish_to_groups is missing.
    """
    if not META_ACCESS_TOKEN:
        print("❌ META_ACCESS_TOKEN is not set — all Facebook posts will fail.")
        return False
    try:
        resp = requests.get(
            f"{GRAPH_BASE}/me/permissions",
            params={"access_token": META_ACCESS_TOKEN},
            timeout=15
        ).json()
        perms = {p["permission"]: p["status"] for p in resp.get("data", [])}
        required = ["pages_manage_posts", "pages_read_engagement"]
        if FACEBOOK_GROUP_ID:
            required.append("publish_to_groups")

        all_ok = True
        for perm in required:
            status = perms.get(perm, "MISSING")
            if status != "granted":
                print(f"  ⚠️  Permission '{perm}' — {status}")
                if perm == "publish_to_groups":
                    print(f"     💡 This is why Facebook Group posting fails.")
                    print(f"        Regenerate token at developers.facebook.com")
                    print(f"        and add 'publish_to_groups' scope.")
                all_ok = False
            else:
                print(f"  ✅ Permission '{perm}' — granted")
        return all_ok
    except Exception as e:
        print(f"  ⚠️  Could not verify token permissions: {e}")
        return True  # Proceed anyway


# ─── STEP A: Upload ZENO Reel to Facebook Page ────────────────────────────────
def upload_reel_to_facebook(video_path: Path, meta: dict) -> str | None:
    """
    Uploads the ZENO video as an official Facebook Reel to the Page.
    Returns video_id on success, None on failure.
    Uses 3-phase upload: start → binary upload → finish.
    """
    print(f"\n🎬 Uploading Facebook Reel: {video_path.name}")

    wisdom = meta.get("description", "Daily Trading Wisdom by Zeno.")
    wisdom_clean = wisdom.split('#')[0].strip()

    # Mode-aware caption
    if CONTENT_MODE == "holiday":
        label = f"🎉 {HOLIDAY_NAME}" if HOLIDAY_NAME else "🎉 Market Holiday"
        caption_intro = f"{label} Special — Market band hai, par seekhna chalu rakho! 📚"
    elif CONTENT_MODE == "weekend":
        caption_intro = "🌟 Weekend Wisdom — Patience aur discipline hi success hai!"
    else:
        caption_intro = "🎭 ZENO KI BAAT ✨"

    caption = (
        f"{caption_intro}\n\n"
        f"💡 {wisdom_clean}\n\n"
        f"Market dynamics ko samjhein aur discipline banaye rakhein. 📈\n\n"
        f"🌐 Website: https://ai360trading.in\n"
        f"📱 Telegram: t.me/ai360trading\n\n"
        f"#Reels #ZenoKiBaat #ai360trading #StockMarketIndia #TradingMotivation"
    )

    video_id  = None
    upload_url = None

    # Phase 1: Start upload session
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            init_resp = requests.post(
                f"{GRAPH_BASE}/{FACEBOOK_PAGE_ID}/video_reels",
                data={"upload_phase": "start", "access_token": META_ACCESS_TOKEN},
                timeout=30
            ).json()
            video_id   = init_resp.get("video_id")
            upload_url = init_resp.get("upload_url")
            if video_id and upload_url:
                print(f"  ✅ Upload session started — video_id: {video_id}")
                break
            else:
                print(f"  ⚠️  Phase 1 failed (attempt {attempt}): {init_resp}")
        except Exception as e:
            print(f"  ⚠️  Phase 1 error (attempt {attempt}): {e}")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    if not video_id or not upload_url:
        print("  ❌ Could not start upload session — aborting reel upload.")
        return None

    # Phase 2: Binary upload
    try:
        with open(video_path, "rb") as f:
            video_data = f.read()
        file_size = len(video_data)
        print(f"  📤 Uploading {file_size / 1_000_000:.1f} MB...")

        upload_resp = requests.post(
            upload_url,
            headers={
                "Authorization": f"OAuth {META_ACCESS_TOKEN}",
                "offset": "0",
                "file_size": str(file_size)
            },
            data=video_data,
            timeout=300
        )
        upload_resp.raise_for_status()
        print(f"  ✅ Binary upload complete")
    except Exception as e:
        print(f"  ❌ Phase 2 binary upload failed: {e}")
        return None

    # Phase 3: Finish + publish (with retry)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            finish_resp = requests.post(
                f"{GRAPH_BASE}/{FACEBOOK_PAGE_ID}/video_reels",
                data={
                    "upload_phase": "finish",
                    "video_id": video_id,
                    "video_state": "PUBLISHED",
                    "description": caption,
                    "access_token": META_ACCESS_TOKEN
                },
                timeout=30
            ).json()

            if "success" in str(finish_resp).lower() or finish_resp.get("video_id"):
                print(f"  ✅ Facebook Reel Published! video_id: {video_id}")
                return video_id
            else:
                print(f"  ⚠️  Phase 3 publish failed (attempt {attempt}): {finish_resp}")
        except Exception as e:
            print(f"  ⚠️  Phase 3 error (attempt {attempt}): {e}")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    print(f"  ❌ Reel publish failed after {MAX_RETRIES} attempts.")
    return None


# ─── STEP B: Share reel link to Facebook Group ────────────────────────────────
def share_reel_to_group(video_id: str, meta: dict):
    """
    After the reel is published on the Page, shares the reel link to the Group.
    This uses a text post with the video link — avoids the Groups video API
    which has stricter permissions than feed posting.
    """
    if not FACEBOOK_GROUP_ID:
        print("\n⚠️  FACEBOOK_GROUP_ID not set — skipping Group share.")
        return

    print(f"\n👥 Sharing reel to Facebook Group...")

    wisdom = meta.get("description", "Daily Trading Wisdom by Zeno.")
    wisdom_clean = wisdom.split('#')[0].strip()

    # Build the Page video URL from video_id
    page_video_url = f"https://www.facebook.com/watch/?v={video_id}"

    if CONTENT_MODE == "holiday":
        label = f"🎉 {HOLIDAY_NAME}" if HOLIDAY_NAME else "🎉 Market Holiday"
        msg = (
            f"📚 {label} Special\n\n"
            f"💡 {wisdom_clean}\n\n"
            f"Market band hai, par seekhna chalu rakho! 🔥\n\n"
            f"▶️ Full Reel: {page_video_url}\n"
            f"🌐 https://ai360trading.in\n\n"
            f"#ZenoKiBaat #ai360trading #HolidayLearning"
        )
    elif CONTENT_MODE == "weekend":
        msg = (
            f"🌟 Weekend Wisdom by ZENO\n\n"
            f"💡 {wisdom_clean}\n\n"
            f"▶️ Full Reel: {page_video_url}\n"
            f"🌐 https://ai360trading.in\n\n"
            f"#ZenoKiBaat #ai360trading #WeekendLearning"
        )
    else:
        msg = (
            f"🎭 ZENO KI BAAT — Aaj ka wisdom!\n\n"
            f"💡 {wisdom_clean}\n\n"
            f"▶️ Full Reel: {page_video_url}\n"
            f"🌐 https://ai360trading.in\n\n"
            f"#ZenoKiBaat #ai360trading #StockMarketIndia"
        )

    post_to_entity(FACEBOOK_GROUP_ID, "Facebook Group", {"message": msg})


# ─── STEP C: Post articles from RSS ───────────────────────────────────────────
def post_articles():
    """
    Fetches top 4 articles from RSS and posts a summary to Page + Group.
    Includes full error logging — no more silent failures.
    """
    print(f"\n📰 Fetching articles from RSS: {WEBSITE_RSS_URL}")
    try:
        session = requests.Session()
        resp = session.get(WEBSITE_RSS_URL, timeout=20)
        resp.raise_for_status()

        try:
            root  = ET.fromstring(resp.content)
            items = root.findall(".//item")
        except ET.ParseError as e:
            print(f"  ⚠️  RSS XML parse error: {e} — skipping article post")
            return

        articles = []
        for item in items[:4]:
            title = item.findtext("title", "").strip()
            link  = item.findtext("link", "").strip()
            if title and link:
                articles.append({"title": title, "link": link})

        if not articles:
            print("  ⚠️  No articles found in RSS feed.")
            return

        print(f"  ✅ Found {len(articles)} articles")

        # Mode-aware article post
        if CONTENT_MODE == "holiday":
            label = f"🎉 {HOLIDAY_NAME}" if HOLIDAY_NAME else "🎉 Market Holiday"
            header = f"📚 {label} Special — Aaj market band hai, par learning nahi!\n\n"
        elif CONTENT_MODE == "weekend":
            header = "📚 Weekend Learning — Market se zyada important hai education!\n\n"
        else:
            header = "🚀 Aaj ki Top Trading Updates — Must Read!\n\n"

        post_msg = header
        for i, art in enumerate(articles, 1):
            post_msg += f"{i}️⃣ {art['title']}\n🔗 {art['link']}\n\n"
        post_msg += (
            "Keep learning, keep trading! 📊\n"
            "🌐 https://ai360trading.in\n"
            "#ai360trading #StockMarket #Updates"
        )

        post_to_entity(FACEBOOK_PAGE_ID,  "Facebook Page (articles)",  {"message": post_msg})
        post_to_entity(FACEBOOK_GROUP_ID, "Facebook Group (articles)", {"message": post_msg})

    except requests.exceptions.HTTPError as e:
        print(f"  ❌ RSS fetch HTTP error: {e}")
    except Exception as e:
        print(f"  ❌ Article sharing failed: {e}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 55)
    print(f"  upload_facebook.py — MODE: {CONTENT_MODE.upper()}")
    print("=" * 55)

    if not META_ACCESS_TOKEN:
        print("❌ META_ACCESS_TOKEN not set — exiting.")
        return

    # ── Token permission check ─────────────────────────────────────────────
    print("\n🔑 Checking token permissions...")
    verify_token_permissions()

    # ── Find latest reel video + meta ─────────────────────────────────────
    today = datetime.now().strftime("%Y%m%d")

    meta_files  = sorted(OUTPUT_DIR.glob("meta_*.json"),  key=os.path.getmtime, reverse=True)
    video_files = sorted(OUTPUT_DIR.glob("reel_*.mp4"),   key=os.path.getmtime, reverse=True)

    if not meta_files:
        print("❌ No meta_*.json found in output/ — skipping reel upload.")
    elif not video_files:
        print("❌ No reel_*.mp4 found in output/ — skipping reel upload.")
    else:
        meta      = json.loads(meta_files[0].read_text(encoding="utf-8"))
        video_id  = upload_reel_to_facebook(video_files[0], meta)

        # Save video_id back to meta for Instagram to use as public_video_url
        if video_id:
            page_video_url = f"https://www.facebook.com/watch/?v={video_id}"
            meta["public_video_url"] = page_video_url
            meta["facebook_video_id"] = video_id
            meta_files[0].write_text(
                json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"  💾 Saved public_video_url to meta: {page_video_url}")

            # Share reel link to Group as a text post
            share_reel_to_group(video_id, meta)
        else:
            print("  ⚠️  Reel upload failed — skipping Group share.")

    # ── Post articles ──────────────────────────────────────────────────────
    post_articles()

    print("\n" + "=" * 55)
    print("  upload_facebook.py — DONE")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    import os
    main()
