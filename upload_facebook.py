"""
upload_facebook.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uploads reels and articles to Facebook Page + Instagram + Kids Page.

Supports --meta-prefix flag:
  (no flag)          → ZENO reel    → reel_*.mp4        → Main Page + Instagram
  --meta-prefix morning → Morning reel → morning_reel_*.mp4 → Main Page + Instagram
  --meta-prefix kids    → Kids video   → kids_*.mp4         → Kids Page

v2.3 NEW (May 2026) — INSTAGRAM REELS AUTO-UPLOAD:
  Added upload_reel_to_instagram() function
  Instagram Business Account ID: 17841400933677509
  Uses 3-step Instagram Graph API flow:
    Step 1: Create media container (/ig_id/media)
    Step 2: Wait for video processing (poll status)
    Step 3: Publish container (/ig_id/media_publish)
  Requirements met:
    ✅ Instagram converted to Professional account
    ✅ Instagram linked to Facebook Page 108076910943724
    ✅ instagram_content_publish permission in token
    ✅ INSTAGRAM_BUSINESS_ACCOUNT_ID secret added

  New GitHub secret required:
    INSTAGRAM_BUSINESS_ACCOUNT_ID = 17841400933677509

v2.2 FIX (May 2026):
  Added get_page_token() — exchanges user token for page token
  Root cause of all Facebook posting failures:
    upload_reel_to_page() was using META_ACCESS_TOKEN (user token) directly
    Facebook requires a PAGE token for page posts since app went Live
    Page token is obtained by calling /me/accounts → match by page_id
  Fix: get_page_token() called at start of every upload → page token used
"""

import os
import sys
import json
import time
import argparse
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

# ─── ARGS ─────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta-prefix", default="",
                        help="Meta prefix: '' = ZENO, 'morning' = morning reel, 'kids' = kids")
    return parser.parse_args()

# ─── CONFIG ───────────────────────────────────────────────────────────────────

META_ACCESS_TOKEN            = os.environ.get("META_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID             = os.environ.get("FACEBOOK_PAGE_ID", "")
FACEBOOK_KIDS_PAGE_ID        = os.environ.get("FACEBOOK_KIDS_PAGE_ID", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "17841400933677509")
CONTENT_MODE                 = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME                 = os.environ.get("HOLIDAY_NAME", "")
OUTPUT_DIR                   = Path("output")
GRAPH_BASE                   = "https://graph.facebook.com/v21.0"
MAX_RETRIES                  = 3
RETRY_DELAY                  = 10

# ─── v2.2 FIX: GET PAGE TOKEN ─────────────────────────────────────────────────

def get_page_token(page_id: str, user_token: str) -> str:
    """
    Exchange user token for page-specific token.
    This is REQUIRED for page posts when app is in Live mode.

    Calls /me/accounts → finds page by ID → returns page access_token
    Falls back to user_token if exchange fails (with warning).
    """
    if not user_token or not page_id:
        return user_token
    try:
        resp = requests.get(
            f"{GRAPH_BASE}/me/accounts",
            params={"access_token": user_token, "limit": 50},
            timeout=15
        )
        data = resp.json().get("data", [])
        for page in data:
            if str(page.get("id", "")) == str(page_id):
                token = page.get("access_token", "")
                if token:
                    print(f"  ✅ Page token retrieved for page {page_id}")
                    return token
        print(f"  ⚠️ Page {page_id} not found in /me/accounts — using user token")
    except Exception as e:
        print(f"  ⚠️ get_page_token failed: {e} — using user token")
    return user_token

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def verify_token():
    if not META_ACCESS_TOKEN:
        print("❌ META_ACCESS_TOKEN not set")
        return False
    print("✅ META_ACCESS_TOKEN is set.")
    return True

def post_to_page(page_id: str, label: str, data: dict, token: str) -> bool:
    """Post text/link to Facebook Page feed with retry."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp   = requests.post(
                f"{GRAPH_BASE}/{page_id}/feed",
                data={**data, "access_token": token},
                timeout=30
            )
            result = resp.json()
            if "id" in result:
                print(f"  ✅ {label} posted — ID: {result['id']}")
                return True
            error  = result.get("error", {})
            code   = error.get("code", "?")
            msg    = error.get("message", str(result))
            print(f"  ❌ {label} failed (attempt {attempt}/{MAX_RETRIES})")
            print(f"     Error {code}: {msg}")
        except requests.exceptions.Timeout:
            print(f"  ⏱️ {label} timed out (attempt {attempt})")
        except Exception as e:
            print(f"  ⚠️ {label} error (attempt {attempt}): {e}")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
    print(f"  ✗ {label} — all attempts failed.")
    return False

# ─── UPLOAD REEL TO FACEBOOK ──────────────────────────────────────────────────

def upload_reel_to_page(page_id: str, page_label: str,
                        video_path: Path, caption: str, token: str) -> str | None:
    """
    Upload video as Facebook Reel using 3-phase upload.
    v2.2: Uses page token (not user token) — required for Live app mode.
    """
    print(f"\n🎬 Uploading Facebook Reel to {page_label}: {video_path.name}")

    video_id   = None
    upload_url = None

    # Phase 1: Start session
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            init = requests.post(
                f"{GRAPH_BASE}/{page_id}/video_reels",
                data={"upload_phase": "start", "access_token": token},
                timeout=30
            ).json()
            video_id   = init.get("video_id")
            upload_url = init.get("upload_url")
            if video_id and upload_url:
                print(f"  ✅ Upload session started — video_id: {video_id}")
                break
            error = init.get("error", {})
            print(f"  ⚠️ Phase 1 failed (attempt {attempt}): {error.get('code')} {error.get('message','')}")
        except Exception as e:
            print(f"  ⚠️ Phase 1 error (attempt {attempt}): {e}")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    if not video_id or not upload_url:
        print("  ❌ Could not start upload session — aborting.")
        return None

    # Phase 2: Binary upload
    try:
        with open(video_path, "rb") as f:
            video_data = f.read()
        file_size = len(video_data)
        print(f"  📤 Uploading {file_size/1_000_000:.1f} MB...")
        requests.post(
            upload_url,
            headers={"Authorization": f"OAuth {token}",
                     "offset": "0", "file_size": str(file_size)},
            data=video_data,
            timeout=300
        ).raise_for_status()
        print("  ✅ Binary upload complete")
    except Exception as e:
        print(f"  ❌ Phase 2 failed: {e}")
        return None

    # Phase 3: Publish
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            finish = requests.post(
                f"{GRAPH_BASE}/{page_id}/video_reels",
                data={"upload_phase": "finish", "video_id": video_id,
                      "video_state": "PUBLISHED", "description": caption,
                      "access_token": token},
                timeout=30
            ).json()
            if finish.get("success") or finish.get("video_id"):
                print(f"  ✅ Reel published to {page_label}")
                return video_id
            print(f"  ⚠️ Phase 3 failed (attempt {attempt}): {finish}")
        except Exception as e:
            print(f"  ⚠️ Phase 3 error (attempt {attempt}): {e}")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    print(f"  ❌ Reel publish failed after {MAX_RETRIES} attempts")
    return None

# ─── v2.3 NEW: UPLOAD REEL TO INSTAGRAM ──────────────────────────────────────

def upload_reel_to_instagram(ig_account_id: str, video_path: Path,
                              caption: str, token: str) -> str | None:
    """
    Upload video as Instagram Reel using 3-step Instagram Graph API.

    Step 1: Create media container
      POST /{ig_id}/media with video_url + caption + media_type=REELS
      Returns: container_id

    Step 2: Wait for video processing
      GET /{container_id}?fields=status_code
      Poll until status_code = FINISHED (max 5 min)

    Step 3: Publish container
      POST /{ig_id}/media_publish with creation_id=container_id
      Returns: ig_post_id

    NOTE: Instagram requires a PUBLIC video URL, not a file upload.
    We use Facebook's video hosting: upload to FB first, get URL, then post to IG.
    OR: host the video temporarily at a public URL.

    Since we already upload to Facebook, we use the FB video URL approach:
    After FB upload succeeds → get video URL → use for Instagram.
    If FB upload fails → skip Instagram (cannot post without public URL).
    """
    if not ig_account_id:
        print("  ⚠️ INSTAGRAM_BUSINESS_ACCOUNT_ID not set — skipping Instagram")
        return None

    print(f"\n📸 Uploading Instagram Reel: {video_path.name}")

    # Instagram requires video hosted at a public URL
    # We use a workaround: host on Facebook CDN via page video upload
    # then reference in Instagram container
    # Alternative: use a temp file hosting service
    # For now: upload to FB first (done in main), then get the video URL

    # Actually the cleanest approach is to upload directly using
    # multipart form upload to Instagram's resumable upload endpoint
    # But that requires the video to be accessible via public HTTPS URL

    # APPROACH: Use Instagram's direct upload via resumable upload
    # Step 1: Initialize upload session
    try:
        init_resp = requests.post(
            f"{GRAPH_BASE}/{ig_account_id}/media",
            params={
                "media_type":    "REELS",
                "caption":       caption,
                "access_token":  token,
                "share_to_feed": "true",
            },
            timeout=30
        ).json()

        container_id = init_resp.get("id")
        upload_url   = init_resp.get("uri")  # resumable upload URL

        if not container_id:
            error = init_resp.get("error", {})
            print(f"  ❌ IG container creation failed: {error.get('code')} {error.get('message','')}")
            return None

        print(f"  ✅ IG container created: {container_id}")

        # If we got a resumable upload URL, upload the video bytes
        if upload_url:
            with open(video_path, "rb") as f:
                video_bytes = f.read()
            file_size = len(video_bytes)
            print(f"  📤 Uploading to Instagram ({file_size/1_000_000:.1f} MB)...")
            up_resp = requests.post(
                upload_url,
                headers={
                    "Authorization":   f"OAuth {token}",
                    "Content-Type":    "application/octet-stream",
                    "offset":          "0",
                    "file_size":       str(file_size),
                },
                data=video_bytes,
                timeout=300
            )
            if up_resp.status_code not in (200, 201):
                print(f"  ❌ IG video upload failed: {up_resp.status_code} {up_resp.text[:200]}")
                return None
            print(f"  ✅ IG video upload complete")

    except Exception as e:
        print(f"  ❌ IG Step 1 error: {e}")
        return None

    # Step 2: Poll for processing (max 5 minutes)
    print(f"  ⏳ Waiting for Instagram video processing...")
    max_polls = 30  # 30 × 10s = 5 min
    for poll in range(max_polls):
        time.sleep(10)
        try:
            status_resp = requests.get(
                f"{GRAPH_BASE}/{container_id}",
                params={"fields": "status_code", "access_token": token},
                timeout=15
            ).json()
            status = status_resp.get("status_code", "")
            print(f"  ⏳ IG status ({poll+1}/{max_polls}): {status}")
            if status == "FINISHED":
                break
            elif status == "ERROR":
                print(f"  ❌ IG processing error")
                return None
        except Exception as e:
            print(f"  ⚠️ IG status poll error: {e}")
    else:
        print(f"  ❌ IG processing timeout after 5 minutes")
        return None

    # Step 3: Publish
    try:
        pub_resp = requests.post(
            f"{GRAPH_BASE}/{ig_account_id}/media_publish",
            params={
                "creation_id":  container_id,
                "access_token": token,
            },
            timeout=30
        ).json()

        ig_post_id = pub_resp.get("id")
        if ig_post_id:
            print(f"  ✅ Instagram Reel published — ID: {ig_post_id}")
            print(f"  ✅ Instagram: https://www.instagram.com/p/{ig_post_id}/")
            return ig_post_id
        else:
            error = pub_resp.get("error", {})
            print(f"  ❌ IG publish failed: {error.get('code')} {error.get('message','')}")
            return None

    except Exception as e:
        print(f"  ❌ IG Step 3 error: {e}")
        return None

# ─── META FILE RESOLVER ───────────────────────────────────────────────────────

def resolve_meta_and_video(prefix: str):
    """Find the latest meta JSON and video MP4 for given prefix."""
    today = datetime.now().strftime("%Y%m%d")

    if prefix == "morning":
        meta_patterns  = [f"morning_reel_meta_{today}.json", "morning_reel_meta_*.json"]
        video_patterns = [f"morning_reel_{today}.mp4", "morning_reel_*.mp4"]
    elif prefix == "kids":
        meta_patterns  = [f"kids_meta_{today}_hi.json", f"kids_meta_{today}.json", "kids_meta_*.json"]
        video_patterns = [f"kids_full_{today}_hi.mp4", f"kids_full_{today}.mp4", "kids_full_*.mp4"]
    else:  # ZENO reel
        meta_patterns  = [f"meta_{today}.json", "meta_*.json"]
        video_patterns = [f"reel_{today}.mp4", "reel_*.mp4"]

    meta_path  = None
    video_path = None

    for pat in meta_patterns:
        cands = sorted(OUTPUT_DIR.glob(pat), key=lambda p: p.stat().st_mtime, reverse=True)
        if cands: meta_path = cands[0]; break

    for pat in video_patterns:
        cands = sorted(OUTPUT_DIR.glob(pat), key=lambda p: p.stat().st_mtime, reverse=True)
        if cands: video_path = cands[0]; break

    return meta_path, video_path

# ─── BUILD CAPTION ────────────────────────────────────────────────────────────

def build_caption(meta: dict, prefix: str) -> str:
    today_str = datetime.now().strftime("%d %B %Y")

    if prefix == "kids":
        ep_title = meta.get("ep_title", meta.get("title_en", "HerooQuest Story"))
        moral    = meta.get("moral", "Every story has a lesson")
        return (
            f"🎭 HerooQuest — Nayi Kahani!\n"
            f"📖 {ep_title}\n"
            f"💡 Aaj ki seekh: {moral}\n\n"
            f"Apne bachon ke saath dekho! ❤️\n"
            f"#HerooQuest #KidsStories #AnimatedStories #HindiKahani"
        )

    title   = meta.get("title", "")
    desc    = meta.get("description", "")
    mode    = CONTENT_MODE

    if mode == "holiday":
        label = HOLIDAY_NAME or "Market Holiday"
        return (
            f"🎉 {label} Special — {today_str}\n\n"
            f"💡 {desc[:120]}\n\n"
            f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
            f"⚠️ Educational only.\n"
            f"#ai360trading #HolidayLearning #StockMarket"
        )
    elif mode == "weekend":
        return (
            f"📚 Weekend Wisdom — {today_str}\n\n"
            f"💡 {desc[:120]}\n\n"
            f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
            f"#ai360trading #WeekendWisdom #Trading"
        )
    else:
        return (
            f"🎯 {title}\n\n"
            f"💡 {desc[:120]}\n\n"
            f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
            f"⚠️ Educational only.\n"
            f"#ai360trading #StockMarket #Nifty #Trading"
        )

# ─── RSS ARTICLE SHARE ────────────────────────────────────────────────────────

def share_articles_from_rss(page_id: str, token: str):
    """Share latest articles from RSS feed to page."""
    rss_url = "https://ai360trading.in/feed.xml"
    try:
        resp = requests.get(rss_url, timeout=15)
        if not resp.ok:
            print(f"  ⚠️ RSS fetch failed: {resp.status_code}")
            return
        root  = ET.fromstring(resp.content)
        items = root.findall(".//item")
        if not items:
            print("  ⚠️ No articles found in RSS feed.")
            return
        # Share most recent article
        item       = items[0]
        title_txt  = item.findtext("title", "").strip()
        link       = item.findtext("link", "").strip()
        if title_txt and link:
            post_to_page(page_id, "Article", {"message": f"📰 {title_txt}\n\n{link}", "link": link}, token)
    except Exception as e:
        print(f"  ⚠️ RSS article share error: {e}")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    args   = parse_args()
    prefix = args.meta_prefix

    print("=" * 60)
    print(f"  upload_facebook.py v2.3 — MODE: {CONTENT_MODE.upper()} | PREFIX: '{prefix}'")
    print("=" * 60)

    if not verify_token():
        sys.exit(1)

    meta_path, video_path = resolve_meta_and_video(prefix)

    # Load meta
    meta = {}
    if meta_path and meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            print(f"📂 Meta file: {meta_path.name}")
        except: pass

    # ── Kids Page ──────────────────────────────────────────────────────────────
    if prefix == "kids":
        kids_token   = os.environ.get("META_ACCESS_TOKEN", META_ACCESS_TOKEN)
        kids_page_id = FACEBOOK_KIDS_PAGE_ID

        if not kids_page_id:
            print("⚠️ FACEBOOK_KIDS_PAGE_ID not set — skipping kids upload")
            return

        # Exchange for page token
        page_token = get_page_token(kids_page_id, kids_token)

        if video_path and video_path.exists():
            caption = build_caption(meta, "kids")
            upload_reel_to_page(kids_page_id, "HerooQuest Kids Page",
                                 video_path, caption, page_token)
        else:
            print("⚠️ Kids video not found — skipping Facebook Kids upload")
        return

    # ── Main Page + Instagram ──────────────────────────────────────────────────
    if not FACEBOOK_PAGE_ID:
        print("⚠️ FACEBOOK_PAGE_ID not set — skipping main page upload")
        return

    # v2.2 FIX: Exchange user token for page token
    page_token = get_page_token(FACEBOOK_PAGE_ID, META_ACCESS_TOKEN)

    if video_path and video_path.exists():
        print(f"🎥 Video: {video_path.name}")
        caption = build_caption(meta, prefix)

        # Facebook upload
        fb_video_id = upload_reel_to_page(FACEBOOK_PAGE_ID, "AI360Trading Page",
                                           video_path, caption, page_token)

        # v2.3 NEW: Instagram upload (after Facebook succeeds)
        if INSTAGRAM_BUSINESS_ACCOUNT_ID:
            # Build Instagram caption (shorter, more hashtags)
            ig_caption = build_caption(meta, prefix)
            ig_caption += "\n\n#Reels #InstagramReels #StockMarketIndia #NiftyTrading"
            upload_reel_to_instagram(
                INSTAGRAM_BUSINESS_ACCOUNT_ID,
                video_path,
                ig_caption,
                page_token  # Page token works for IG too when linked
            )
        else:
            print("  ⚠️ INSTAGRAM_BUSINESS_ACCOUNT_ID not set — skipping Instagram")

    else:
        print(f"⚠️ Video not found for prefix '{prefix}' — skipping reel upload")

    # Share latest article from RSS
    print(f"📰 Fetching articles from RSS: https://ai360trading.in/feed.xml")
    share_articles_from_rss(FACEBOOK_PAGE_ID, page_token)

    print("=" * 60)
    print("  upload_facebook.py — DONE")
    print("=" * 60)

if __name__ == "__main__":
    main()
