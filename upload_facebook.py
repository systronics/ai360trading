"""
upload_facebook.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v2.4 FIX (May 2026) — Instagram resumable upload corrected:
  Old: POST /{ig_id}/media with bytes → Error: video_url required
  New: Correct 3-step resumable upload flow:
    Step 1: POST /{ig_id}/media?media_type=REELS&upload_type=resumable
            → Returns: id (container_id) + uri (upload_url)
    Step 2: POST video bytes to uri with correct headers
    Step 3: Poll container status until FINISHED
    Step 4: POST /{ig_id}/media_publish?creation_id=container_id

v2.3 (May 2026):
  Added Instagram Reels upload
  Instagram Business Account ID: 17841400933677509

v2.2 (May 2026):
  Added get_page_token() — exchanges user token for page token
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

META_ACCESS_TOKEN             = os.environ.get("META_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID              = os.environ.get("FACEBOOK_PAGE_ID", "")
FACEBOOK_KIDS_PAGE_ID         = os.environ.get("FACEBOOK_KIDS_PAGE_ID", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "17841400933677509")
CONTENT_MODE                  = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME                  = os.environ.get("HOLIDAY_NAME", "")
OUTPUT_DIR                    = Path("output")
GRAPH_BASE                    = "https://graph.facebook.com/v21.0"
MAX_RETRIES                   = 3
RETRY_DELAY                   = 10

# ─── GET PAGE TOKEN ───────────────────────────────────────────────────────────

def get_page_token(page_id: str, user_token: str) -> str:
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
            error = result.get("error", {})
            print(f"  ❌ {label} failed (attempt {attempt}/{MAX_RETRIES})")
            print(f"     Error {error.get('code','?')}: {error.get('message', str(result))}")
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

# ─── v2.4 FIX: UPLOAD REEL TO INSTAGRAM (correct resumable upload) ────────────

def upload_reel_to_instagram(ig_account_id: str, video_path: Path,
                              caption: str, token: str) -> str | None:
    """
    Correct Instagram Reels upload using resumable upload protocol.

    v2.4 FIX:
      Old (wrong): POST /{ig_id}/media with video bytes → Error: video_url required
      New (correct): Use upload_type=resumable to get upload_url from Instagram
                     then POST video bytes to that upload_url
                     then poll status → publish

    Step 1: POST /{ig_id}/media with upload_type=resumable
            → Returns: id (container_id) + uri (upload_url from Instagram)
    Step 2: POST video bytes to uri with Authorization header
    Step 3: Poll container status until FINISHED (max 5 min)
    Step 4: POST /{ig_id}/media_publish
    """
    if not ig_account_id:
        print("  ⚠️ INSTAGRAM_BUSINESS_ACCOUNT_ID not set — skipping Instagram")
        return None

    print(f"\n📸 Uploading Instagram Reel: {video_path.name}")

    # Step 1: Create container with upload_type=resumable
    # This returns the upload_url (uri) without needing a public video_url
    try:
        init_resp = requests.post(
            f"{GRAPH_BASE}/{ig_account_id}/media",
            data={
                "media_type":   "REELS",
                "upload_type":  "resumable",   # v2.4 FIX: was missing this
                "caption":      caption,
                "share_to_feed": "true",
                "access_token": token,
            },
            timeout=30
        ).json()

        container_id = init_resp.get("id")
        upload_url   = init_resp.get("uri")  # Instagram returns upload URL here

        if not container_id:
            error = init_resp.get("error", {})
            print(f"  ❌ IG container creation failed: {error.get('code')} {error.get('message','')}")
            print(f"     Full response: {init_resp}")
            return None

        print(f"  ✅ IG container created: {container_id}")

        if not upload_url:
            print(f"  ❌ No upload_url (uri) returned from Instagram")
            return None

    except Exception as e:
        print(f"  ❌ IG Step 1 error: {e}")
        return None

    # Step 2: Upload video bytes to the Instagram upload URL
    try:
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
            print(f"  ❌ IG video upload failed: {up_resp.status_code} — {up_resp.text[:200]}")
            return None

        print(f"  ✅ IG video upload complete")

    except Exception as e:
        print(f"  ❌ IG Step 2 error: {e}")
        return None

    # Step 3: Poll status (max 5 minutes = 30 × 10s)
    print(f"  ⏳ Waiting for Instagram video processing...")
    for poll in range(30):
        time.sleep(10)
        try:
            status_resp = requests.get(
                f"{GRAPH_BASE}/{container_id}",
                params={"fields": "status_code,status", "access_token": token},
                timeout=15
            ).json()
            status = status_resp.get("status_code", "")
            print(f"  ⏳ IG processing ({poll+1}/30): {status}")
            if status == "FINISHED":
                break
            elif status == "ERROR":
                print(f"  ❌ IG processing error: {status_resp.get('status','')}")
                return None
        except Exception as e:
            print(f"  ⚠️ IG status poll error: {e}")
    else:
        print(f"  ❌ IG processing timeout after 5 minutes")
        return None

    # Step 4: Publish
    try:
        pub_resp = requests.post(
            f"{GRAPH_BASE}/{ig_account_id}/media_publish",
            data={
                "creation_id":  container_id,
                "access_token": token,
            },
            timeout=30
        ).json()

        ig_post_id = pub_resp.get("id")
        if ig_post_id:
            print(f"  ✅ Instagram Reel published — ID: {ig_post_id}")
            return ig_post_id
        else:
            error = pub_resp.get("error", {})
            print(f"  ❌ IG publish failed: {error.get('code')} {error.get('message','')}")
            return None

    except Exception as e:
        print(f"  ❌ IG Step 4 error: {e}")
        return None

# ─── META FILE RESOLVER ───────────────────────────────────────────────────────

def resolve_meta_and_video(prefix: str):
    today = datetime.now().strftime("%Y%m%d")

    if prefix == "morning":
        meta_patterns  = [f"morning_reel_meta_{today}.json", "morning_reel_meta_*.json"]
        video_patterns = [f"morning_reel_{today}.mp4", "morning_reel_*.mp4"]
    elif prefix == "kids":
        meta_patterns  = [f"kids_meta_{today}_hi.json", f"kids_meta_{today}.json", "kids_meta_*.json"]
        video_patterns = [f"kids_full_{today}_hi.mp4", f"kids_full_{today}.mp4", "kids_full_*.mp4"]
    else:
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

    title = meta.get("title", "")
    desc  = meta.get("description", "")
    mode  = CONTENT_MODE

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
        item      = items[0]
        title_txt = item.findtext("title", "").strip()
        link      = item.findtext("link", "").strip()
        if title_txt and link:
            post_to_page(page_id, "Article",
                         {"message": f"📰 {title_txt}\n\n{link}", "link": link}, token)
    except Exception as e:
        print(f"  ⚠️ RSS article share error: {e}")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    args   = parse_args()
    prefix = args.meta_prefix

    print("=" * 60)
    print(f"  upload_facebook.py v2.4 — MODE: {CONTENT_MODE.upper()} | PREFIX: '{prefix}'")
    print("=" * 60)

    if not verify_token():
        sys.exit(1)

    meta_path, video_path = resolve_meta_and_video(prefix)

    meta = {}
    if meta_path and meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            print(f"📂 Meta file: {meta_path.name}")
        except: pass

    # ── Kids Page ─────────────────────────────────────────────────────────────
    if prefix == "kids":
        kids_token   = os.environ.get("META_ACCESS_TOKEN", META_ACCESS_TOKEN)
        kids_page_id = FACEBOOK_KIDS_PAGE_ID

        if not kids_page_id:
            print("⚠️ FACEBOOK_KIDS_PAGE_ID not set — skipping kids upload")
            return

        page_token = get_page_token(kids_page_id, kids_token)

        if video_path and video_path.exists():
            caption = build_caption(meta, "kids")
            upload_reel_to_page(kids_page_id, "HerooQuest Kids Page",
                                video_path, caption, page_token)
        else:
            print("⚠️ Kids video not found — skipping Facebook Kids upload")
        return

    # ── Main Page + Instagram ─────────────────────────────────────────────────
    if not FACEBOOK_PAGE_ID:
        print("⚠️ FACEBOOK_PAGE_ID not set — skipping main page upload")
        return

    page_token = get_page_token(FACEBOOK_PAGE_ID, META_ACCESS_TOKEN)

    if video_path and video_path.exists():
        print(f"🎥 Video: {video_path.name}")
        caption = build_caption(meta, prefix)

        # Facebook upload
        upload_reel_to_page(FACEBOOK_PAGE_ID, "AI360Trading Page",
                            video_path, caption, page_token)

        # Instagram upload (v2.4: correct resumable upload)
        if INSTAGRAM_BUSINESS_ACCOUNT_ID:
            ig_caption = caption + "\n\n#Reels #InstagramReels #StockMarketIndia"
            upload_reel_to_instagram(
                INSTAGRAM_BUSINESS_ACCOUNT_ID,
                video_path,
                ig_caption,
                page_token
            )
        else:
            print("  ⚠️ INSTAGRAM_BUSINESS_ACCOUNT_ID not set — skipping Instagram")
    else:
        print(f"⚠️ Video not found for prefix '{prefix}' — skipping reel upload")

    # RSS articles
    print(f"📰 Fetching articles from RSS: https://ai360trading.in/feed.xml")
    share_articles_from_rss(FACEBOOK_PAGE_ID, page_token)

    print("=" * 60)
    print("  upload_facebook.py v2.4 — DONE")
    print("=" * 60)

if __name__ == "__main__":
    main()
