"""
upload_facebook.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v2.7 (2026-07-19):
  REMOVED — HerooQuest Kids page upload branch (kids channel retired).
    ZENO/morning/education/market paths unchanged.

v2.6 (May 2026):
  ADD — Facebook Group posting after Page upload succeeds
    Uses FACEBOOK_GROUP_ID secret (already in GitHub Secrets)
    Posts reel link + caption to Group after Page reel published
    Requires META_ACCESS_TOKEN to have publish_to_groups scope
    On permission error: logs clearly + skips (does not crash)
    Note: Token must have publish_to_groups scope — see SYSTEM.md Section 12

v2.5 FIX (May 2026):
  get_page_token: try GET /{page_id}?fields=access_token first
    (more reliable than /me/accounts which may be paginated/empty)
    Fall back to /me/accounts with limit=200 + show found IDs.
  Instagram upload: Content-Type changed to video/mp4
    (application/octet-stream causes ProcessingFailedError)

v2.4 FIX (May 2026) — Instagram resumable upload corrected:
  Old: POST /{ig_id}/media with bytes → Error: video_url required
  New: Correct 3-step resumable upload flow

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

# AI-content disclosure (Meta policy). Fail-open: if human_touch is unavailable
# for any reason, fall back to a plain English disclosure string so captions are
# always compliant.
try:
    from human_touch import ai_disclosure
except Exception:
    def ai_disclosure(lang="en"):
        return "🤖 Produced with AI tools · 📊 Real market data & analysis · Educational only"

# ─── ARGS ─────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta-prefix", default="",
                        help="Meta prefix: '' = ZENO, 'morning' = morning reel, 'education' = education")
    return parser.parse_args()

# ─── CONFIG ───────────────────────────────────────────────────────────────────

META_ACCESS_TOKEN             = os.environ.get("META_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID              = os.environ.get("FACEBOOK_PAGE_ID", "")
FACEBOOK_GROUP_ID             = os.environ.get("FACEBOOK_GROUP_ID", "")
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

    # Primary: direct page token fetch (avoids pagination gaps in /me/accounts)
    try:
        resp = requests.get(
            f"{GRAPH_BASE}/{page_id}",
            params={"fields": "access_token", "access_token": user_token},
            timeout=15
        )
        data = resp.json()
        token = data.get("access_token", "")
        if token:
            print(f"  ✅ Page token retrieved for page {page_id}")
            return token
        err = data.get("error", {})
        if err:
            print(f"  ⚠️ Direct page token: {err.get('code')} {err.get('message','')}")
    except Exception as e:
        print(f"  ⚠️ Direct page token fetch failed: {e}")

    # Fallback: list all pages
    try:
        resp = requests.get(
            f"{GRAPH_BASE}/me/accounts",
            params={"access_token": user_token, "limit": 200},
            timeout=15
        )
        data = resp.json().get("data", [])
        for page in data:
            if str(page.get("id", "")) == str(page_id):
                token = page.get("access_token", "")
                if token:
                    print(f"  ✅ Page token retrieved via /me/accounts for page {page_id}")
                    return token
        found = [p.get("id") for p in data]
        print(f"  ⚠️ Page {page_id} not in /me/accounts — found: {found[:10] or 'none'}")
    except Exception as e:
        print(f"  ⚠️ /me/accounts lookup failed: {e}")

    print(f"  ⚠️ Falling back to user token (page token unavailable)")
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

def _videos_fallback(page_id: str, page_label: str, video_path: Path, caption: str, token: str) -> str | None:
    """Fallback: POST to /videos endpoint when /video_reels returns permission error."""
    print(f"  🔄 {page_label}: trying /videos fallback...")
    try:
        with open(video_path, "rb") as f:
            video_data = f.read()
        resp = requests.post(
            f"{GRAPH_BASE}/{page_id}/videos",
            data={"description": caption, "access_token": token},
            files={"source": ("video.mp4", video_data, "video/mp4")},
            timeout=180
        ).json()
        if resp.get("id"):
            print(f"  ✅ {page_label} video posted via /videos — ID: {resp['id']}")
            return resp["id"]
        error = resp.get("error", {})
        print(f"  ❌ /videos also failed: {error.get('code')} {error.get('message','')}")
    except Exception as e:
        print(f"  ❌ /videos fallback error: {e}")
    return None


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
            code  = error.get("code", "")
            msg   = error.get("message", "")
            print(f"  ⚠️ Phase 1 failed (attempt {attempt}): {code} {msg}")
            if code in (200, "200") or "permission" in str(msg).lower():
                print(f"  ⚠️ Permission error on /video_reels — trying /videos fallback")
                return _videos_fallback(page_id, page_label, video_path, caption, token)
        except Exception as e:
            print(f"  ⚠️ Phase 1 error (attempt {attempt}): {e}")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    if not video_id or not upload_url:
        print("  ❌ Could not start upload session — trying /videos fallback")
        return _videos_fallback(page_id, page_label, video_path, caption, token)

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


# ─── v2.6 NEW: POST TO FACEBOOK GROUP ────────────────────────────────────────

def post_to_group(group_id: str, caption: str, video_url: str, user_token: str) -> bool:
    """
    Post reel link + caption to Facebook Group.
    v2.6: First time this code exists — was missing in all previous versions.

    Requirements (one-time manual setup — see SYSTEM.md Section 12):
      1. META_ACCESS_TOKEN must have publish_to_groups scope
      2. Amit Kumar account must be Admin of the group
      3. Group Settings → Advanced → Allow content from apps = ON
      4. App must be approved for Groups API by Meta

    Uses user token (not page token) — Groups API requires user token.
    On permission error: logs clearly, skips, does NOT crash workflow.
    """
    if not group_id:
        print("  ⚠️ FACEBOOK_GROUP_ID not set — skipping Group post")
        return False

    if not user_token:
        print("  ⚠️ No user token for Group post — skipping")
        return False

    print(f"\n👥 Posting to Facebook Group: {group_id}")

    # Build group message — include video link so group members can watch
    if video_url:
        message = f"{caption}\n\n🎬 Watch: {video_url}"
    else:
        message = caption

    try:
        resp = requests.post(
            f"{GRAPH_BASE}/{group_id}/feed",
            data={
                "message":      message,
                "access_token": user_token,
            },
            timeout=30
        ).json()

        if "id" in resp:
            print(f"  ✅ Group post published — ID: {resp['id']}")
            return True

        error = resp.get("error", {})
        code  = error.get("code", "?")
        msg   = error.get("message", str(resp))

        # Specific error messages for easier debugging
        if code in (200, "200") or "permission" in str(msg).lower():
            print(f"  ❌ Group post failed — permission error ({code})")
            print(f"     Fix: Add publish_to_groups scope to META_ACCESS_TOKEN")
            print(f"     See SYSTEM.md Section 12 for step-by-step fix")
        elif "admin" in str(msg).lower():
            print(f"  ❌ Group post failed — not admin of group")
            print(f"     Fix: Make Amit Kumar account Admin of ai360trading group")
        else:
            print(f"  ❌ Group post failed: {code} — {msg}")

    except Exception as e:
        print(f"  ⚠️ Group post error: {e}")

    return False


# ─── v2.4 FIX: UPLOAD REEL TO INSTAGRAM ──────────────────────────────────────

def upload_reel_to_instagram(ig_account_id: str, video_path: Path,
                              caption: str, token: str) -> str | None:
    """
    Correct Instagram Reels upload using resumable upload protocol.
    Step 1: POST /{ig_id}/media with upload_type=resumable → container_id + upload_url
    Step 2: POST video bytes to upload_url
    Step 3: Poll container status until FINISHED (max 5 min)
    Step 4: POST /{ig_id}/media_publish
    """
    if not ig_account_id:
        print("  ⚠️ INSTAGRAM_BUSINESS_ACCOUNT_ID not set — skipping Instagram")
        return None

    print(f"\n📸 Uploading Instagram Reel: {video_path.name}")

    # Step 1: Create container
    try:
        init_resp = requests.post(
            f"{GRAPH_BASE}/{ig_account_id}/media",
            data={
                "media_type":    "REELS",
                "upload_type":   "resumable",
                "caption":       caption,
                "share_to_feed": "true",
                "access_token":  token,
            },
            timeout=30
        ).json()

        container_id = init_resp.get("id")
        upload_url   = init_resp.get("uri")

        if not container_id:
            error = init_resp.get("error", {})
            print(f"  ❌ IG container creation failed: {error.get('code')} {error.get('message','')}")
            return None

        print(f"  ✅ IG container created: {container_id}")

        if not upload_url:
            print(f"  ❌ No upload_url (uri) returned from Instagram")
            return None

    except Exception as e:
        print(f"  ❌ IG Step 1 error: {e}")
        return None

    # Step 2: Upload video bytes
    try:
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        file_size = len(video_bytes)
        print(f"  📤 Uploading to Instagram ({file_size/1_000_000:.1f} MB)...")

        up_resp = requests.post(
            upload_url,
            headers={
                "Authorization": f"OAuth {token}",
                "Content-Type":  "video/mp4",
                "offset":        "0",
                "file_size":     str(file_size),
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

    # Step 3: Poll status (max 5 min = 30 x 10s)
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
            data={"creation_id": container_id, "access_token": token},
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
    elif prefix == "education":
        meta_patterns  = [f"education_meta_{today}_bi.json", "education_meta_*.json"]
        video_patterns = ["education_video_bi.mp4", "education_video_*.mp4"]
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

    if prefix == "education":
        edu_title = meta.get("title", "Stock Market Lesson")
        edu_desc  = (meta.get("description", "") or "")[:140]
        return (
            f"📚 {edu_title}\n\n"
            f"💡 {edu_desc}\n\n"
            f"🎯 FREE daily signals → t.me/ai360trading\n"
            f"🌐 ai360trading.in\n"
            f"⚠️ Educational only. Not SEBI registered.\n"
            f"{ai_disclosure('en')}\n"
            f"#ai360trading #StockMarket #TradingForBeginners #Investing #ShareMarket"
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
            f"{ai_disclosure('hi')}\n"
            f"#ai360trading #HolidayLearning #StockMarket"
        )
    elif mode == "weekend":
        return (
            f"📚 Weekend Wisdom — {today_str}\n\n"
            f"💡 {desc[:120]}\n\n"
            f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
            f"⚠️ Educational only.\n"
            f"{ai_disclosure('hi')}\n"
            f"#ai360trading #WeekendWisdom #Trading"
        )
    else:
        return (
            f"🎯 {title}\n\n"
            f"💡 {desc[:120]}\n\n"
            f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
            f"⚠️ Educational only.\n"
            f"{ai_disclosure('hi')}\n"
            f"#ai360trading #StockMarket #Nifty #Trading"
        )

# ─── RSS ARTICLE SHARE ────────────────────────────────────────────────────────

def share_articles_from_rss(page_id: str, token: str):
    rss_url = "https://ai360trading.in/feed.xml"
    ATOM_NS = "http://www.w3.org/2005/Atom"
    try:
        resp = requests.get(rss_url, timeout=15)
        if not resp.ok:
            print(f"  ⚠️ RSS fetch failed: {resp.status_code}")
            return
        root    = ET.fromstring(resp.content)
        entries = root.findall(f"{{{ATOM_NS}}}entry")
        if not entries:
            print("  ⚠️ No articles found in feed.")
            return
        entry     = entries[0]
        title_txt = (entry.findtext(f"{{{ATOM_NS}}}title", "") or "").strip()
        link_el   = entry.find(f"{{{ATOM_NS}}}link[@rel='alternate']") or entry.find(f"{{{ATOM_NS}}}link")
        link      = link_el.get("href", "").strip() if link_el is not None else ""
        if title_txt and link:
            print(f"  📰 Sharing: {title_txt[:60]}...")
            post_to_page(page_id, "Article",
                         {"message": f"📰 {title_txt}\n\n{link}", "link": link}, token)
        else:
            print(f"  ⚠️ Article missing title or link — skipping")
    except Exception as e:
        print(f"  ⚠️ RSS article share error: {e}")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    args   = parse_args()
    prefix = args.meta_prefix

    print("=" * 60)
    print(f"  upload_facebook.py v2.6 — MODE: {CONTENT_MODE.upper()} | PREFIX: '{prefix}'")
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

    # ── Education (landscape long-form → /videos, NOT Reels) ──────────────────
    if prefix == "education":
        if not FACEBOOK_PAGE_ID:
            print("⚠️ FACEBOOK_PAGE_ID not set — skipping education FB upload")
            return
        page_token = get_page_token(FACEBOOK_PAGE_ID, META_ACCESS_TOKEN)
        if video_path and video_path.exists():
            caption = build_caption(meta, "education")
            # Education is a ~10-min 16:9 video → post to /videos (reels reject it)
            _videos_fallback(FACEBOOK_PAGE_ID, "AI360Trading Page",
                             video_path, caption, page_token)
        else:
            print("⚠️ Education video not found — skipping Facebook education upload")
        return

    # ── Main Page + Group + Instagram ─────────────────────────────────────────
    if not FACEBOOK_PAGE_ID:
        print("⚠️ FACEBOOK_PAGE_ID not set — skipping main page upload")
        return

    page_token = get_page_token(FACEBOOK_PAGE_ID, META_ACCESS_TOKEN)

    if video_path and video_path.exists():
        print(f"🎥 Video: {video_path.name}")
        caption = build_caption(meta, prefix)

        # Facebook Page upload — get video_id for group post link
        video_id = upload_reel_to_page(FACEBOOK_PAGE_ID, "AI360Trading Page",
                                       video_path, caption, page_token)

        # v2.6 NEW: Facebook Group post — share reel link to Group
        if FACEBOOK_GROUP_ID:
            # Build Facebook video URL from video_id if available
            fb_video_url = f"https://www.facebook.com/watch/?v={video_id}" if video_id else ""
            # Group post uses USER token (not page token) — Groups API requirement
            post_to_group(FACEBOOK_GROUP_ID, caption, fb_video_url, META_ACCESS_TOKEN)
        else:
            print("  ⚠️ FACEBOOK_GROUP_ID not set — skipping Group post")

        # Instagram upload
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

    # RSS articles — Page only (not Group — avoid spam)
    print(f"📰 Fetching articles from RSS: https://ai360trading.in/feed.xml")
    share_articles_from_rss(FACEBOOK_PAGE_ID, page_token)

    print("=" * 60)
    print("  upload_facebook.py v2.6 — DONE")
    print("=" * 60)

if __name__ == "__main__":
    main()
