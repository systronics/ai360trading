"""
upload_youtube.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uploads videos to YouTube (Reel, Analysis, Education, Morning Reel).

Critical chain:
  generate_reel.py → upload_youtube.py → upload_facebook.py → upload_instagram.py

After upload, this script:
  1. Saves video_id into meta_YYYYMMDD.json (needed by upload_instagram.py)
  2. Saves output/youtube_video_id.txt (used by other scripts if needed)

--type argument controls which meta + video file to target:
  reel        → meta_YYYYMMDD.json       + reel_YYYYMMDD.mp4
  analysis    → analysis_meta_YYYYMMDD.json + analysis_video.mp4
  education   → education_meta_YYYYMMDD.json + education_video.mp4
  morning     → morning_reel_meta_YYYYMMDD.json + morning_reel_YYYYMMDD.mp4

FIX — Playlist 403 Error:
  Added youtube.force-ssl to OAuth scopes so playlist assignment works.
  Token must be regenerated after adding this scope (delete token.json locally
  or re-run the OAuth flow via GitHub Actions token_refresh.yml).

SEO strategy:
  - Tags cover India, USA, UK, Brazil, UAE for maximum CPM
  - Category 27 = Education (best for finance content monetisation)
  - Titles are mode-aware (market / weekend / holiday)

Last updated: April 6, 2026 17:59 IST
"""

import os
import sys
import json
import argparse
import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── CONFIG ───────────────────────────────────────────────────────────────────

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "")
OUTPUT_DIR   = Path("output")

# FIX: Added youtube.force-ssl scope — required for playlist assignment (was 403)
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

# ─── Playlist IDs per type (set your real playlist IDs here) ─────────────────
PLAYLIST_IDS = {
    "reel":      os.environ.get("YOUTUBE_PLAYLIST_REEL", ""),
    "analysis":  os.environ.get("YOUTUBE_PLAYLIST_ANALYSIS", ""),
    "education": os.environ.get("YOUTUBE_PLAYLIST_EDUCATION", ""),
    "morning":   os.environ.get("YOUTUBE_PLAYLIST_MORNING", ""),
}

# ─── Global SEO tags — covers all high-CPM target countries ──────────────────

BASE_TAGS = [
    "ai360trading", "ZenoKiBaat", "StockMarketIndia", "TradingWisdom",
    "Nifty50", "TradingIndia", "USStocks", "UKInvesting", "BrazilMarket",
    "GlobalInvesting", "FinancialLiteracy", "InvestmentEducation",
    "StockMarket", "Investing", "Finance", "Hinglish", "Shorts"
]

MARKET_TAGS = BASE_TAGS + [
    "Nifty", "BankNifty", "TradingSetup", "TradeSignal",
    "PriceAction", "TechnicalAnalysis", "IndianStockMarket"
]

WEEKEND_TAGS = BASE_TAGS + [
    "WeekendLearning", "PersonalFinance", "WealthBuilding",
    "MoneyMindset", "FinanceTips", "InvestSmart"
]

HOLIDAY_TAGS = BASE_TAGS + [
    "HolidayLearning", "MarketHoliday", "InvestmentTips",
    "FinancialFreedom", "WealthCreation", "LearnInvesting"
]


# ─── AUTH ─────────────────────────────────────────────────────────────────────

def get_service():
    """Authenticates using YOUTUBE_CREDENTIALS environment variable."""
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json:
            if os.path.exists("token.json"):
                with open("token.json") as f:
                    creds_json = f.read()
            else:
                print("❌ No YouTube credentials found")
                return None

        creds = Credentials.from_authorized_user_info(
            json.loads(creds_json),
            scopes=SCOPES  # FIX: pass scopes so force-ssl is respected
        )
        service = build("youtube", "v3", credentials=creds)
        print("✅ YouTube authenticated")
        return service

    except Exception as e:
        print(f"❌ YouTube auth error: {e}")
        return None


# ─── UPLOAD ───────────────────────────────────────────────────────────────────

def upload_video(video_path: Path, title: str, description: str, tags: list):
    """
    Uploads a video to YouTube with resumable upload.
    Returns (video_id, video_url) on success, (None, None) on failure.
    """
    youtube = get_service()
    if not youtube:
        return None, None

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags[:30],      # YouTube max 30 tags
            "categoryId": "27"      # Education — best for finance monetisation
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"🚀 Uploading to YouTube: {title[:70]}...")

    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   {int(status.progress() * 100)}%")

        video_id  = response["id"]
        video_url = f"https://youtube.com/shorts/{video_id}"
        print(f"✅ YouTube upload success!")
        print(f"   Video ID : {video_id}")
        print(f"   URL      : {video_url}")
        return video_id, video_url

    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        return None, None


# ─── PLAYLIST ─────────────────────────────────────────────────────────────────

def assign_to_playlist(video_id: str, video_type: str):
    """
    Assigns video to playlist.
    Requires youtube.force-ssl scope — now included in SCOPES above.
    """
    playlist_id = PLAYLIST_IDS.get(video_type, "")
    if not playlist_id:
        print(f"📋 Playlist: skipped (no playlist ID configured for type '{video_type}')")
        return

    youtube = get_service()
    if not youtube:
        return

    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        ).execute()
        print(f"📋 Playlist: ✅ Added to {video_type} playlist")
    except Exception as e:
        print(f"📋 Playlist: ⚠️  Skipped (non-critical): {e}")


# ─── META + VIDEO FILE RESOLUTION ────────────────────────────────────────────

def resolve_files(video_type: str, today: str):
    """
    Returns (meta_path, video_path) for the given upload type.
    Supports: reel, analysis, education, morning
    """
    patterns = {
        "reel":      (f"meta_{today}.json",                f"reel_{today}.mp4"),
        "analysis":  (f"analysis_meta_{today}.json",       "analysis_video.mp4"),
        "education": (f"education_meta_{today}.json",      "education_video.mp4"),
        "morning":   (f"morning_reel_meta_{today}.json",   f"morning_reel_{today}.mp4"),
    }

    meta_name, video_name = patterns.get(video_type, patterns["reel"])

    # Meta file
    meta_path = OUTPUT_DIR / meta_name
    if not meta_path.exists():
        # Fallback: latest matching meta
        candidates = sorted(
            OUTPUT_DIR.glob(meta_name.replace(today, "*")),
            key=os.path.getmtime, reverse=True
        )
        meta_path = candidates[0] if candidates else None

    # Video file
    video_path = OUTPUT_DIR / video_name
    if not video_path.exists():
        candidates = sorted(
            OUTPUT_DIR.glob(video_name.replace(today, "*")),
            key=os.path.getmtime, reverse=True
        )
        video_path = candidates[0] if candidates else None

    return meta_path, video_path


# ─── BUILD TITLE + DESCRIPTION ────────────────────────────────────────────────

def build_metadata(meta: dict, today: str, video_type: str) -> tuple:
    """Returns (title, description, tags) based on CONTENT_MODE and video_type."""

    # For analysis/education types, use whatever title/description is in meta
    if video_type in ("analysis", "education"):
        title = meta.get("title", f"AI360Trading — {video_type.capitalize()} {today}")
        desc  = meta.get("description", "Daily market insight by AI360Trading.")
        tags  = meta.get("tags", MARKET_TAGS)[:30]
        print(f"📝 Title: {title}")
        print(f"🏷️  Tags: {len(tags)} tags")
        return title, desc, tags

    # For reel / morning — build mode-aware title
    base_title = meta.get("title", f"ZENO Ki Baat — {today}")
    base_desc  = meta.get("description", "Daily trading wisdom by ZENO.")
    desc_clean = base_desc.split("#")[0].strip()

    prefix = "🌅 Morning Brief" if video_type == "morning" else "🎯 ZENO Ki Baat"

    if CONTENT_MODE == "holiday":
        label = f"🎉 {HOLIDAY_NAME}" if HOLIDAY_NAME else "🎉 Market Holiday"
        title = f"{label} Special — {prefix} #{today[-4:]} #Shorts"
        desc  = (
            f"🎉 {label} Special — Market band hai, par learning band nahi!\n\n"
            f"💡 {desc_clean}\n\n"
            f"🌍 For investors in India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n\n"
            f"#ZenoKiBaat #ai360trading #HolidayLearning #InvestmentEducation"
        )
        tags = HOLIDAY_TAGS

    elif CONTENT_MODE == "weekend":
        title = f"📚 Weekend Wisdom — {prefix} #{today[-4:]} #Shorts"
        desc  = (
            f"📚 Weekend Learning Special\n\n"
            f"💡 {desc_clean}\n\n"
            f"🌍 For investors in India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n\n"
            f"#ZenoKiBaat #ai360trading #WeekendLearning #FinancialLiteracy"
        )
        tags = WEEKEND_TAGS

    else:  # market
        title = f"{prefix} — Trading Wisdom #{today[-4:]} #Shorts"
        desc  = (
            f"🎯 Daily Trading Wisdom by ZENO\n\n"
            f"💡 {desc_clean}\n\n"
            f"📊 Live market analysis for Nifty50 traders\n"
            f"🌍 Investors: India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n\n"
            f"⚠️ Educational content only. Not financial advice.\n"
            f"#ZenoKiBaat #ai360trading #TradingWisdom #Nifty50"
        )
        tags = MARKET_TAGS

    print(f"📝 Title: {title}")
    print(f"🏷️  Tags: {len(tags)} tags")
    return title, desc, tags


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type",
        choices=["reel", "analysis", "education", "morning"],
        default="reel",
        help="Which video type to upload"
    )
    args = parser.parse_args()
    video_type = args.type

    print("\n" + "=" * 60)
    print(f"  upload_youtube.py — MODE: {CONTENT_MODE.upper()} | TYPE: {video_type.upper()}")
    print("=" * 60)

    today = datetime.datetime.now().strftime("%Y%m%d")

    # ── Resolve files ──────────────────────────────────────────────────────────
    meta_path, video_path = resolve_files(video_type, today)

    if meta_path and meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"📄 Meta file: {meta_path.name}")
    else:
        meta = {}
        print("⚠️ No meta file found — using defaults")

    if not video_path or not video_path.exists():
        print(f"❌ No video file found in {OUTPUT_DIR}/ — aborting.")
        sys.exit(1)

    print(f"🎥 Video file: {video_path.name}")

    # ── Build metadata ─────────────────────────────────────────────────────────
    title, description, tags = build_metadata(meta, today, video_type)

    # ── Upload ─────────────────────────────────────────────────────────────────
    video_id, video_url = upload_video(video_path, title, description, tags)

    if video_id:
        # ── Playlist assignment (now works — force-ssl scope added) ───────────
        assign_to_playlist(video_id, video_type)

        # ── Save video_id to meta — CRITICAL for Instagram upload chain ───────
        if meta_path and meta_path.exists():
            meta["youtube_video_id"]  = video_id
            meta["youtube_video_url"] = video_url
            if not meta.get("public_video_url"):
                meta["public_video_url"] = video_url
            meta_path.write_text(
                json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"💾 Saved youtube_video_id to meta: {video_id}")

        # ── Save video_id to txt — used by daily-shorts workflow ──────────────
        id_path = OUTPUT_DIR / "youtube_video_id.txt"
        id_path.write_text(video_id, encoding="utf-8")
        print(f"💾 Saved video ID to: {id_path.name}")

    print("\n" + "=" * 60)
    print(f"  upload_youtube.py — {'SUCCESS ✅' if video_id else 'FAILED ❌'}")
    print("=" * 60 + "\n")

    if not video_id:
        sys.exit(1)


if __name__ == "__main__":
    main()
