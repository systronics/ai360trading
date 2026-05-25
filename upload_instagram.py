"""
upload_instagram.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v1.0 (May 2026) — Standalone Instagram Reels uploader.

Handles any video type via --type flag:
  --type reel    → reel_YYYYMMDD.mp4        (ZENO evening reel)
  --type morning → morning_reel_YYYYMMDD.mp4 (7:00 AM morning reel)
  --type short2  → short2_YYYYMMDD.mp4      (Madhur Hindi short)
  --type short3  → short3_YYYYMMDD.mp4      (Neerja English short)

Upload flow (same 4-step resumable as upload_facebook.py v2.6):
  Step 1: POST /{ig_id}/media with upload_type=resumable → container_id + upload_url
  Step 2: POST video bytes to upload_url with Authorization + offset + file_size headers
  Step 3: Poll container status every 10s until FINISHED (max 5 min = 30 polls)
  Step 4: POST /{ig_id}/media_publish with creation_id

On failure: saves caption to output/instagram_fallback_YYYYMMDD.txt for manual posting.
On success: writes ig_post_id to meta JSON.

Env vars required:
  META_ACCESS_TOKEN              — user token (exchanges for page token internally)
  FACEBOOK_PAGE_ID               — needed to get page token
  INSTAGRAM_BUSINESS_ACCOUNT_ID  — Instagram Business Account ID
  CONTENT_MODE                   — market / weekend / holiday (optional, defaults to market)
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime
import pytz

# ─── CONFIG ───────────────────────────────────────────────────────────────────

META_ACCESS_TOKEN             = os.environ.get("META_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID              = os.environ.get("FACEBOOK_PAGE_ID", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "17841400933677509")
CONTENT_MODE                  = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME                  = os.environ.get("HOLIDAY_NAME", "")

OUTPUT_DIR  = Path("output")
GRAPH_BASE  = "https://graph.facebook.com/v21.0"
MAX_RETRIES = 3
RETRY_DELAY = 10
IG_POLL_MAX = 30
IG_POLL_WAIT= 10

IST = pytz.timezone("Asia/Kolkata")


# ─── ARGS ─────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="Instagram Reels uploader — AI360Trading")
    parser.add_argument(
        "--type",
        choices=["reel", "morning", "short2", "short3"],
        default="reel",
        help="Video type to upload (default: reel)"
    )
    return parser.parse_args()


# ─── FILE RESOLVER ────────────────────────────────────────────────────────────

def resolve_files(video_type: str):
    """Find the latest video + meta JSON for the given type."""
    today = datetime.now(IST).strftime("%Y%m%d")

    patterns = {
        "reel":    (
            [f"reel_{today}.mp4",          "reel_*.mp4"],
            [f"meta_{today}.json",          "meta_*.json"]
        ),
        "morning": (
            [f"morning_reel_{today}.mp4",   "morning_reel_*.mp4"],
            [f"morning_reel_meta_{today}.json", "morning_reel_meta_*.json"]
        ),
        "short2":  (
            [f"short2_{today}.mp4",         "short2_*.mp4"],
            [f"meta_{today}.json",          "meta_*.json"]
        ),
        "short3":  (
            [f"short3_{today}.mp4",         "short3_*.mp4"],
            [f"meta_{today}.json",          "meta_*.json"]
        ),
    }

    video_pats, meta_pats = patterns[video_type]

    video_path = None
    for pat in video_pats:
        cands = sorted(OUTPUT_DIR.glob(pat), key=lambda p: p.stat().st_mtime, reverse=True)
        if cands:
            video_path = cands[0]
            break

    meta_path = None
    for pat in meta_pats:
        cands = sorted(OUTPUT_DIR.glob(pat), key=lambda p: p.stat().st_mtime, reverse=True)
        if cands:
            meta_path = cands[0]
            break

    return video_path, meta_path


# ─── PAGE TOKEN (matches upload_facebook.py v2.6 exactly) ────────────────────

def get_page_token() -> str:
    """Exchange user token for page token. Falls back to user token if unavailable."""
    if not META_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        return META_ACCESS_TOKEN

    # Primary: direct page token fetch
    try:
        resp = requests.get(
            f"{GRAPH_BASE}/{FACEBOOK_PAGE_ID}",
            params={"fields": "access_token", "access_token": META_ACCESS_TOKEN},
            timeout=15
        )
        data = resp.json()
        token = data.get("access_token", "")
        if token:
            print(f"  ✅ Page token retrieved for page {FACEBOOK_PAGE_ID}")
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
            params={"access_token": META_ACCESS_TOKEN, "limit": 200},
            timeout=15
        )
        data = resp.json().get("data", [])
        for page in data:
            if str(page.get("id", "")) == str(FACEBOOK_PAGE_ID):
                token = page.get("access_token", "")
                if token:
                    print(f"  ✅ Page token retrieved via /me/accounts")
                    return token
        found = [p.get("id") for p in data]
        print(f"  ⚠️ Page {FACEBOOK_PAGE_ID} not in /me/accounts — found: {found[:10] or 'none'}")
    except Exception as e:
        print(f"  ⚠️ /me/accounts lookup failed: {e}")

    print("  ⚠️ Falling back to user token")
    return META_ACCESS_TOKEN


# ─── CAPTION BUILDER ──────────────────────────────────────────────────────────

def build_caption(meta: dict, video_type: str) -> str:
    today_str = datetime.now(IST).strftime("%d %B %Y")
    title = meta.get("title", "")
    desc  = meta.get("description", "")

    if video_type == "morning":
        sentiment = meta.get("sentiment", "NEUTRAL").upper()
        nifty     = meta.get("nifty_level", 0)
        nifty_str = f"NIFTY {nifty:,}" if nifty else ""
        if CONTENT_MODE == "holiday":
            return (
                f"🎉 {HOLIDAY_NAME or 'Market Holiday'} — {today_str}\n\n"
                f"💡 {desc[:120]}\n\n"
                f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
                f"#MorningBrief #ai360trading #HolidayLearning"
            )
        return (
            f"☀️ Morning Market Brief — {today_str}\n"
            f"{nifty_str + ' ' if nifty_str else ''}{sentiment}\n\n"
            f"💡 {desc[:120]}\n\n"
            f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
            f"⚠️ Educational only.\n"
            f"#MorningBrief #Nifty #StockMarket #ai360trading #Reels"
        )

    if video_type == "short2":
        stock   = meta.get("stock", "Market")
        insight = meta.get("insight", "")
        if CONTENT_MODE in ("holiday", "weekend"):
            return (
                f"📚 Weekend Learning!\n\n"
                f"💡 {insight or desc[:100]}\n\n"
                f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
                f"#ai360trading #StockMarket #Trading #Investing"
            )
        sent = meta.get("sentiment", "").capitalize()
        return (
            f"📊 {stock} {sent} Setup!\n\n"
            f"💡 {insight or desc[:100]}\n\n"
            f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
            f"⚠️ Educational only.\n"
            f"#ai360trading #Nifty50 #StockMarket #TradingIndia #Reels"
        )

    if video_type == "short3":
        insight = meta.get("insight", "Global markets shaping India's trading day.")
        if CONTENT_MODE in ("holiday", "weekend"):
            return (
                f"🌍 Global Market Wisdom!\n\n"
                f"💡 {insight}\n\n"
                f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
                f"#GlobalMarkets #Bitcoin #Gold #SP500 #ai360trading"
            )
        return (
            f"🌍 Global Market Pulse!\n\n"
            f"💡 {insight}\n\n"
            f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
            f"⚠️ Educational only.\n"
            f"#GlobalMarkets #Bitcoin #Gold #Nifty #ai360trading #Reels"
        )

    # Default: ZENO evening reel
    if CONTENT_MODE == "holiday":
        return (
            f"🎉 {HOLIDAY_NAME or 'Market Holiday'} Special — {today_str}\n\n"
            f"💡 {desc[:120]}\n\n"
            f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
            f"#ai360trading #HolidayLearning #StockMarket #Reels"
        )
    elif CONTENT_MODE == "weekend":
        return (
            f"📚 Weekend Wisdom — {today_str}\n\n"
            f"💡 {desc[:120]}\n\n"
            f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
            f"#ai360trading #WeekendWisdom #Trading #Reels"
        )
    return (
        f"🎯 {title}\n\n"
        f"💡 {desc[:120]}\n\n"
        f"🌐 ai360trading.in | 📱 t.me/ai360trading\n"
        f"⚠️ Educational only.\n"
        f"#ai360trading #StockMarket #Nifty #Trading #Reels"
    )


# ─── FALLBACK: SAVE CAPTION FOR MANUAL POSTING ───────────────────────────────

def save_caption_fallback(caption: str, video_type: str):
    today = datetime.now(IST).strftime("%Y%m%d")
    path  = OUTPUT_DIR / f"instagram_fallback_{today}.txt"
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Type: {video_type} | {datetime.now(IST).strftime('%Y-%m-%d %H:%M IST')}\n")
            f.write(caption + "\n")
        print(f"  📝 Caption saved to {path.name} for manual posting")
    except Exception as e:
        print(f"  ⚠️ Could not save fallback caption: {e}")


# ─── 4-STEP INSTAGRAM RESUMABLE UPLOAD ───────────────────────────────────────

def upload_to_instagram(video_path: Path, caption: str, video_type: str) -> str | None:
    """
    4-step Instagram resumable upload (matches upload_facebook.py v2.6 exactly).
    Returns ig_post_id on success, None on failure.
    """
    ig_account_id = INSTAGRAM_BUSINESS_ACCOUNT_ID
    if not ig_account_id:
        print("  ❌ INSTAGRAM_BUSINESS_ACCOUNT_ID not set — cannot upload")
        return None

    token = get_page_token()
    if not token:
        print("  ❌ No access token — cannot upload to Instagram")
        return None

    print(f"\n📸 Uploading Instagram Reel ({video_type}): {video_path.name}")

    # Step 1: Create resumable container
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
            print(f"  ❌ IG Step 1 failed: {error.get('code')} {error.get('message','')}")
            save_caption_fallback(caption, video_type)
            return None

        print(f"  ✅ IG container created: {container_id}")

        if not upload_url:
            print("  ❌ No upload_url (uri) returned from Instagram")
            save_caption_fallback(caption, video_type)
            return None

    except Exception as e:
        print(f"  ❌ IG Step 1 error: {e}")
        save_caption_fallback(caption, video_type)
        return None

    # Step 2: Upload video bytes
    try:
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        file_size = len(video_bytes)
        print(f"  📤 Uploading {file_size / 1_000_000:.1f} MB to Instagram...")

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
            print(f"  ❌ IG Step 2 failed: {up_resp.status_code} — {up_resp.text[:200]}")
            save_caption_fallback(caption, video_type)
            return None

        print("  ✅ IG video bytes uploaded")

    except Exception as e:
        print(f"  ❌ IG Step 2 error: {e}")
        save_caption_fallback(caption, video_type)
        return None

    # Step 3: Poll until FINISHED (max 5 min)
    print("  ⏳ Waiting for Instagram to process video...")
    for poll in range(IG_POLL_MAX):
        time.sleep(IG_POLL_WAIT)
        try:
            status_resp = requests.get(
                f"{GRAPH_BASE}/{container_id}",
                params={"fields": "status_code,status", "access_token": token},
                timeout=15
            ).json()
            status = status_resp.get("status_code", "")
            print(f"  ⏳ Processing ({poll + 1}/{IG_POLL_MAX}): {status}")
            if status == "FINISHED":
                break
            if status == "ERROR":
                print(f"  ❌ IG processing error: {status_resp.get('status', '')}")
                save_caption_fallback(caption, video_type)
                return None
        except Exception as e:
            print(f"  ⚠️ IG poll error: {e}")
    else:
        print("  ❌ IG processing timeout after 5 minutes")
        save_caption_fallback(caption, video_type)
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

        error = pub_resp.get("error", {})
        print(f"  ❌ IG Step 4 failed: {error.get('code')} {error.get('message','')}")
        save_caption_fallback(caption, video_type)
        return None

    except Exception as e:
        print(f"  ❌ IG Step 4 error: {e}")
        save_caption_fallback(caption, video_type)
        return None


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    args       = parse_args()
    video_type = args.type

    print("=" * 60)
    print(f"  upload_instagram.py v1.0 — TYPE: {video_type.upper()} | MODE: {CONTENT_MODE.upper()}")
    print("=" * 60)

    if not META_ACCESS_TOKEN:
        print("❌ META_ACCESS_TOKEN not set — cannot continue")
        sys.exit(1)

    if not INSTAGRAM_BUSINESS_ACCOUNT_ID:
        print("❌ INSTAGRAM_BUSINESS_ACCOUNT_ID not set — cannot continue")
        sys.exit(1)

    video_path, meta_path = resolve_files(video_type)

    if not video_path or not video_path.exists():
        print(f"❌ No video found for type '{video_type}' in output/")
        sys.exit(1)

    print(f"🎥 Video: {video_path.name}")

    meta = {}
    if meta_path and meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            print(f"📄 Meta: {meta_path.name}")
        except Exception as e:
            print(f"⚠️ Could not read meta: {e}")

    caption    = build_caption(meta, video_type)
    ig_post_id = upload_to_instagram(video_path, caption, video_type)

    if ig_post_id and meta_path and meta_path.exists():
        try:
            meta["ig_post_id"] = ig_post_id
            meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
            print(f"  💾 ig_post_id saved to {meta_path.name}")
        except Exception as e:
            print(f"  ⚠️ Could not update meta: {e}")

    print("=" * 60)
    if ig_post_id:
        print(f"  upload_instagram.py — SUCCESS — ID: {ig_post_id}")
    else:
        print("  upload_instagram.py — FAILED (caption saved for manual posting)")
    print("=" * 60)

    if not ig_post_id:
        sys.exit(1)


if __name__ == "__main__":
    main()
