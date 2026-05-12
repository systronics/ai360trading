"""
upload_facebook.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v2.1 FIX: All API calls now use Page Access Token (not User Token).
          Root cause of (#200) error: user token cannot post videos
          to a Page — must exchange for page-specific token first.

Supports --meta-prefix flag:
  (no flag)             → ZENO reel    → meta_*.json         → Main Page
  --meta-prefix morning → Morning reel → morning_reel_meta_* → Main Page
  --meta-prefix kids    → Kids video   → kids_meta_*.json    → Kids Page

Facebook Group posting: PERMANENTLY REMOVED.
Token refresh: Every 50 days via token_refresh.yml (auto).
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
    parser = argparse.ArgumentParser(description="Upload video/reel to Facebook")
    parser.add_argument("--meta-prefix", default="",
        help="Meta file prefix: '' = ZENO reel, 'morning' = morning reel, 'kids' = kids video")
    return parser.parse_args()

# ─── CONFIG ───────────────────────────────────────────────────────────────────

META_ACCESS_TOKEN     = os.environ.get("META_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID      = os.environ.get("FACEBOOK_PAGE_ID", "")
FACEBOOK_KIDS_PAGE_ID = os.environ.get("FACEBOOK_KIDS_PAGE_ID", "")
CONTENT_MODE          = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME          = os.environ.get("HOLIDAY_NAME", "")
WEBSITE_RSS_URL       = "https://ai360trading.in/feed.xml"
OUTPUT_DIR            = Path("output")
GRAPH_BASE            = "https://graph.facebook.com/v21.0"
MAX_RETRIES           = 3
RETRY_DELAY           = 10

# ─── PAGE TOKEN EXCHANGE — THE FIX ───────────────────────────────────────────

def get_page_token(user_token: str, page_id: str) -> str:
    """
    Exchange user access token for page access token.

    WHY THIS IS NEEDED:
    Facebook Graph API (#200) error occurs when you post videos to a Page
    using a User Access Token. Even if the token has pages_manage_posts
    permission, video uploads require a Page-specific Access Token.

    The page token is derived FROM the user token via /me/accounts endpoint.
    It does not expire separately — tied to the user token expiry.

    Returns page token on success, falls back to user token (with warning).
    """
    try:
        resp = requests.get(
            f"{GRAPH_BASE}/me/accounts",
            params={"access_token": user_token, "limit": 20},
            timeout=15
        )
        if resp.ok:
            for page in resp.json().get("data", []):
                if str(page.get("id")) == str(page_id):
                    page_token = page.get("access_token", "")
                    if page_token:
                        print(f"  ✅ Page token obtained for: {page.get('name', page_id)}")
                        return page_token
            # Page not found in accounts list
            print(f"  ⚠️ Page {page_id} not found in /me/accounts — check page admin role")
        else:
            print(f"  ⚠️ /me/accounts returned {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        print(f"  ⚠️ Page token exchange failed: {e}")

    print("  ⚠️ Falling back to user token — upload may fail with #200 error")
    return user_token


# Cache page tokens so we don't call /me/accounts multiple times per run
_PAGE_TOKEN_CACHE: dict = {}

def get_cached_page_token(page_id: str) -> str:
    """Get page token, using cache to avoid repeated API calls."""
    if page_id not in _PAGE_TOKEN_CACHE:
        _PAGE_TOKEN_CACHE[page_id] = get_page_token(META_ACCESS_TOKEN, page_id)
    return _PAGE_TOKEN_CACHE[page_id]

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def post_to_page(page_id: str, label: str, data: dict) -> bool:
    """Posts to Facebook Page feed with retry. Uses page token."""
    page_token = get_cached_page_token(page_id)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp   = requests.post(
                f"{GRAPH_BASE}/{page_id}/feed",
                data={**data, "access_token": page_token},
                timeout=30
            )
            result = resp.json()
            if "id" in result:
                print(f"  ✅ {label} posted — Post ID: {result['id']}")
                return True
            else:
                error   = result.get("error", {})
                code    = error.get("code", "?")
                subcode = error.get("error_subcode", "")
                msg     = error.get("message", str(result))
                fbt     = error.get("fbtrace_id", "")
                print(f"  ❌ {label} failed (attempt {attempt}/{MAX_RETRIES})")
                print(f"     Error {code}/{subcode}: {msg}")
                if fbt:
                    print(f"     fbtrace_id: {fbt}")
        except requests.exceptions.Timeout:
            print(f"  ⏱️ {label} timed out (attempt {attempt}/{MAX_RETRIES})")
        except Exception as e:
            print(f"  ⚠️ {label} unexpected error (attempt {attempt}/{MAX_RETRIES}): {e}")
        if attempt < MAX_RETRIES:
            print(f"  Retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
    print(f"  ✗ {label} — all {MAX_RETRIES} attempts failed.")
    return False


def verify_token():
    """Checks token is set."""
    if not META_ACCESS_TOKEN:
        print("❌ META_ACCESS_TOKEN is not set — all Facebook posts will fail.")
        return False
    print("✅ META_ACCESS_TOKEN is set.")
    return True

# ─── UPLOAD REEL TO PAGE ──────────────────────────────────────────────────────

def upload_reel_to_page(page_id: str, page_label: str,
                         video_path: Path, caption: str) -> str | None:
    """
    Uploads a video as a Facebook Reel to a Page.
    Uses 3-phase upload: start → binary → finish.

    v2.1 FIX: All 3 phases now use page_token instead of META_ACCESS_TOKEN.
    This resolves the (#200) OAuthException error.
    """
    print(f"\n🎬 Uploading Facebook Reel to {page_label}: {video_path.name}")

    # Get page-specific token (THE FIX)
    page_token = get_cached_page_token(page_id)

    video_id   = None
    upload_url = None

    # Phase 1: Start upload session
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            init_resp = requests.post(
                f"{GRAPH_BASE}/{page_id}/video_reels",
                data={
                    "upload_phase": "start",
                    "access_token": page_token   # ← page token, not user token
                },
                timeout=30
            ).json()
            video_id   = init_resp.get("video_id")
            upload_url = init_resp.get("upload_url")
            if video_id and upload_url:
                print(f"  ✅ Upload session started — video_id: {video_id}")
                break
            else:
                error = init_resp.get("error", {})
                print(f"  ⚠️ Phase 1 failed (attempt {attempt}): "
                      f"code={error.get('code','?')} msg={error.get('message', init_resp)}")
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
        print(f"  📤 Uploading {file_size / 1_000_000:.1f} MB...")
        upload_resp = requests.post(
            upload_url,
            headers={
                "Authorization": f"OAuth {page_token}",  # ← page token
                "offset":        "0",
                "file_size":     str(file_size)
            },
            data=video_data,
            timeout=300
        )
        upload_resp.raise_for_status()
        print("  ✅ Binary upload complete")
    except Exception as e:
        print(f"  ❌ Phase 2 binary upload failed: {e}")
        return None

    # Phase 3: Finish + publish
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            finish_resp = requests.post(
                f"{GRAPH_BASE}/{page_id}/video_reels",
                data={
                    "upload_phase": "finish",
                    "video_id":     video_id,
                    "video_state":  "PUBLISHED",
                    "description":  caption,
                    "access_token": page_token   # ← page token
                },
                timeout=30
            ).json()
            if "success" in str(finish_resp).lower() or finish_resp.get("video_id"):
                print(f"  ✅ Facebook Reel Published! video_id: {video_id}")
                return video_id
            else:
                error = finish_resp.get("error", {})
                print(f"  ⚠️ Phase 3 failed (attempt {attempt}): "
                      f"code={error.get('code','?')} msg={error.get('message', finish_resp)}")
        except Exception as e:
            print(f"  ⚠️ Phase 3 error (attempt {attempt}): {e}")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    print(f"  ❌ Reel publish failed after {MAX_RETRIES} attempts.")
    return None

# ─── BUILD CAPTIONS ───────────────────────────────────────────────────────────

def build_main_caption(meta: dict) -> str:
    wisdom       = meta.get("description", "Daily Trading Wisdom by Zeno.")
    wisdom_clean = wisdom.split('#')[0].strip()
    if CONTENT_MODE == "holiday":
        label = f"🎉 {HOLIDAY_NAME}" if HOLIDAY_NAME else "🎉 Market Holiday"
        intro = f"{label} Special — Market band hai, par seekhna chalu rakho! 📚"
    elif CONTENT_MODE == "weekend":
        intro = "🌟 Weekend Wisdom — Patience aur discipline hi success hai!"
    else:
        reel_type = meta.get("type", "reel")
        if reel_type == "morning_reel":
            intro = "🌅 MORNING BRIEF — Aaj ka trading insight!"
        else:
            intro = "🎭 ZENO KI BAAT ✨"
    return (
        f"{intro}\n\n"
        f"💡 {wisdom_clean}\n\n"
        f"Market dynamics ko samjhein aur discipline banaye rakhein. 📈\n\n"
        f"🌐 Website: https://ai360trading.in\n"
        f"📱 Telegram: t.me/ai360trading\n\n"
        f"#Reels #ZenoKiBaat #ai360trading #StockMarketIndia #TradingMotivation"
    )


def build_kids_caption(meta: dict) -> str:
    title       = meta.get("title", "HerooQuest Story")
    description = meta.get("description", "A fun educational story for kids!")
    desc_clean  = description.split('#')[0].strip()
    return (
        f"🦸 {title}\n\n"
        f"✨ {desc_clean}\n\n"
        f"🌍 Fun learning for kids everywhere!\n"
        f"📱 YouTube: youtube.com/@HerooQuest\n\n"
        f"#HerooQuest #KidsStories #EducationForKids #MoralStories #KidsLearning"
    )

# ─── POST ARTICLES FROM RSS ───────────────────────────────────────────────────

def post_articles():
    """Fetches top 4 articles from RSS and posts to Main Page."""
    print(f"\n📰 Fetching articles from RSS: {WEBSITE_RSS_URL}")
    try:
        resp = requests.get(WEBSITE_RSS_URL, timeout=20)
        resp.raise_for_status()
        try:
            root  = ET.fromstring(resp.content)
            items = root.findall(".//item")
        except ET.ParseError as e:
            print(f"  ⚠️ RSS XML parse error: {e} — skipping article post")
            return
        articles = []
        for item in items[:4]:
            title = item.findtext("title", "").strip()
            link  = item.findtext("link",  "").strip()
            if title and link:
                articles.append({"title": title, "link": link})
        if not articles:
            print("  ⚠️ No articles found in RSS feed.")
            return
        print(f"  ✅ Found {len(articles)} articles")
        if CONTENT_MODE == "holiday":
            label  = f"🎉 {HOLIDAY_NAME}" if HOLIDAY_NAME else "🎉 Market Holiday"
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
        post_to_page(FACEBOOK_PAGE_ID, "Facebook Page (articles)", {"message": post_msg})
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ RSS fetch HTTP error: {e}")
    except Exception as e:
        print(f"  ❌ Article sharing failed: {e}")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    args        = parse_args()
    meta_prefix = args.meta_prefix.lower().strip()

    print("\n" + "=" * 60)
    print(f"  upload_facebook.py v2.1 — MODE: {CONTENT_MODE.upper()} | PREFIX: '{meta_prefix}'")
    print("=" * 60)

    if not verify_token():
        sys.exit(1)

    today   = datetime.now().strftime("%Y%m%d")
    is_kids = (meta_prefix == "kids")

    # ── KIDS MODE ─────────────────────────────────────────────────────────────
    if is_kids:
        if not FACEBOOK_KIDS_PAGE_ID:
            print("❌ FACEBOOK_KIDS_PAGE_ID not set — skipping kids upload.")
            return

        meta_path = None
        for pattern in [f"kids_meta_{today}.json", "kids_meta_*.json"]:
            candidates = sorted(OUTPUT_DIR.glob(pattern), key=os.path.getmtime, reverse=True)
            if candidates:
                meta_path = candidates[0]; break

        if not meta_path:
            print("❌ No kids_meta_*.json found — skipping kids FB upload.")
            return

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"📄 Meta file: {meta_path.name}")

        video_path = None
        for pattern in [f"kids_video_{today}.mp4", "kids_video_*.mp4", "kids_*.mp4"]:
            candidates = sorted(OUTPUT_DIR.glob(pattern), key=os.path.getmtime, reverse=True)
            if candidates:
                video_path = candidates[0]; break

        if not video_path:
            print("❌ No kids video found in output/ — skipping kids FB upload.")
            return

        print(f"🎥 Video: {video_path.name}")
        caption  = build_kids_caption(meta)
        video_id = upload_reel_to_page(FACEBOOK_KIDS_PAGE_ID, "HerooQuest Kids Page",
                                        video_path, caption)
        if video_id:
            meta["facebook_kids_video_id"] = video_id
            meta["facebook_kids_url"]      = f"https://www.facebook.com/watch/?v={video_id}"
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"💾 Saved facebook_kids_video_id to meta: {video_id}")
        else:
            print("⚠️  Kids FB upload failed — video saved to output/ for manual upload.")

    # ── MAIN PAGE MODE ────────────────────────────────────────────────────────
    else:
        if not FACEBOOK_PAGE_ID:
            print("❌ FACEBOOK_PAGE_ID not set — skipping main page upload.")
            return

        if meta_prefix == "morning":
            file_prefix = "morning_reel_meta_"
            video_glob  = ["morning_reel_*.mp4"]
        else:
            file_prefix = "meta_"
            video_glob  = [f"reel_{today}.mp4", "reel_*.mp4"]

        meta_path = None
        for pattern in [f"{file_prefix}{today}.json", f"{file_prefix}*.json"]:
            candidates = sorted(OUTPUT_DIR.glob(pattern), key=os.path.getmtime, reverse=True)
            if candidates:
                meta_path = candidates[0]; break

        if not meta_path:
            all_meta = sorted(OUTPUT_DIR.glob("meta_*.json"), key=os.path.getmtime, reverse=True)
            if all_meta:
                meta_path = all_meta[0]
                print(f"⚠️  No {file_prefix}*.json — using fallback: {meta_path.name}")
            else:
                print("❌ No meta file found — skipping FB upload.")
                return

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"📄 Meta file: {meta_path.name}")

        video_path = None
        for pattern in video_glob + ["*.mp4"]:
            candidates = sorted(OUTPUT_DIR.glob(pattern), key=os.path.getmtime, reverse=True)
            if candidates:
                video_path = candidates[0]; break

        if not video_path:
            print("❌ No video found in output/ — skipping FB reel upload.")
        else:
            print(f"🎥 Video: {video_path.name}")
            caption  = build_main_caption(meta)
            video_id = upload_reel_to_page(FACEBOOK_PAGE_ID, "Main Page",
                                            video_path, caption)
            if video_id:
                meta["public_video_url"]  = f"https://www.facebook.com/watch/?v={video_id}"
                meta["facebook_video_id"] = video_id
                meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"💾 Saved facebook_video_id to meta: {video_id}")
            else:
                print("⚠️  FB reel upload failed — video saved to output/ for manual upload.")

        if meta_prefix == "":
            post_articles()

    print("\n" + "=" * 60)
    print("  upload_facebook.py — DONE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
