"""
upload_youtube.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uploads videos/reels/shorts to YouTube.

Supports multiple content types via --type flag:
  --type reel          → ZENO reel (generate_reel.py)       → PLAYLIST_ZENO_WISDOM
  --type morning_reel  → Morning reel (generate_reel_morning.py) → PLAYLIST_ZENO_WISDOM
  --type analysis      → Part 1 analysis (generate_analysis.py) → PLAYLIST_NIFTY_ANALYSIS
  --type education     → Part 2 education (generate_education.py) → PLAYLIST_WEEKLY_OUTLOOK
  --type short         → Shorts (generate_shorts.py)        → PLAYLIST_SWING_TRADE
  (no flag / default)  → ZENO reel (backward compatible)

Critical chain:
  generate_reel.py → upload_youtube.py → upload_facebook.py
  generate_reel_morning.py → upload_youtube.py --type morning_reel → upload_facebook.py
  generate_analysis.py → upload_youtube.py --type analysis
  generate_education.py → upload_youtube.py --type education
  generate_shorts.py → upload_youtube.py --type short

After upload, this script:
  1. Saves video_id into meta JSON (needed by upload_facebook.py)
  2. Saves output/youtube_video_id.txt (used by other scripts if needed)
  3. Adds video to correct playlist via playlistItems().insert()

Playlist secrets (GitHub Secrets):
  PLAYLIST_ZENO_WISDOM     → reels + morning reels
  PLAYLIST_NIFTY_ANALYSIS  → market analysis videos
  PLAYLIST_WEEKLY_OUTLOOK  → educational videos
  PLAYLIST_SWING_TRADE     → shorts

SEO strategy:
  - Tags cover India, USA, UK, Brazil, UAE for maximum CPM
  - Category 27 = Education (best for finance content monetisation)
  - Titles are mode-aware (market / weekend / holiday)

Last updated: April 2026
"""

import os
import sys
import json
import datetime
import argparse
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── ARGS ─────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="Upload video to YouTube with playlist assignment")
    parser.add_argument(
        "--type",
        choices=["reel", "morning_reel", "analysis", "education", "short"],
        default="reel",
        help="Content type — determines which meta file, video file, and playlist to use"
    )
    return parser.parse_args()

# ─── CONFIG ───────────────────────────────────────────────────────────────────

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "")
OUTPUT_DIR = Path("output")

# Playlist IDs from GitHub Secrets — None if not set (playlist step is skipped gracefully)
PLAYLIST_IDS = {
    "reel":         os.environ.get("PLAYLIST_ZENO_WISDOM"),
    "morning_reel": os.environ.get("PLAYLIST_ZENO_WISDOM"),
    "analysis":     os.environ.get("PLAYLIST_NIFTY_ANALYSIS"),
    "education":    os.environ.get("PLAYLIST_WEEKLY_OUTLOOK"),
    "short":        os.environ.get("PLAYLIST_SWING_TRADE"),
}

# Meta file prefixes by type
META_PREFIXES = {
    "reel":         "meta_",
    "morning_reel": "morning_reel_meta_",
    "analysis":     "analysis_meta_",
    "education":    "education_meta_",
    "short":        "short_meta_",
}

# Video file patterns by type (in priority order)
VIDEO_PATTERNS = {
    "reel":         ["reel_{today}.mp4", "reel_*.mp4"],
    "morning_reel": ["morning_reel_{today}.mp4", "morning_reel_*.mp4"],
    "analysis":     ["analysis_{today}.mp4", "analysis_*.mp4", "part1_*.mp4"],
    "education":    ["education_{today}.mp4", "education_*.mp4", "part2_*.mp4"],
    "short":        ["short_{today}.mp4", "short_*.mp4", "shorts_*.mp4"],
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

ANALYSIS_TAGS = BASE_TAGS + [
    "NiftyAnalysis", "MarketAnalysis", "Nifty50Analysis",
    "MarketOutlook", "TechnicalAnalysis", "NiftyPrediction"
]

EDUCATION_TAGS = BASE_TAGS + [
    "StockMarketEducation", "TradingBasics", "InvestmentStrategy",
    "LearnTrading", "WeeklyOutlook", "MarketEducation"
]

SHORT_TAGS = BASE_TAGS + [
    "SwingTrade", "SwingTrading", "TradingSignal",
    "StockPick", "Breakout", "TradingTips"
]

MORNING_TAGS = BASE_TAGS + [
    "MorningBrief", "TradingMorning", "MarketOpen",
    "MorningMotivation", "TradingInsights", "DailyBrief"
]

TAGS_BY_TYPE = {
    "reel":         {"market": MARKET_TAGS, "weekend": WEEKEND_TAGS, "holiday": HOLIDAY_TAGS},
    "morning_reel": {"market": MORNING_TAGS, "weekend": MORNING_TAGS, "holiday": MORNING_TAGS},
    "analysis":     {"market": ANALYSIS_TAGS, "weekend": ANALYSIS_TAGS, "holiday": ANALYSIS_TAGS},
    "education":    {"market": EDUCATION_TAGS, "weekend": EDUCATION_TAGS, "holiday": EDUCATION_TAGS},
    "short":        {"market": SHORT_TAGS, "weekend": SHORT_TAGS, "holiday": SHORT_TAGS},
}

# ─── AUTH ─────────────────────────────────────────────────────────────────────

def get_service():
    """Authenticates using YOUTUBE_CREDENTIALS environment variable."""
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json:
            # Fallback to local token file for development
            if os.path.exists("token.json"):
                with open("token.json") as f:
                    creds_json = f.read()
            else:
                print("❌ YOUTUBE_CREDENTIALS secret not set.")
                return None

        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        service = build("youtube", "v3", credentials=creds)
        print("✅ YouTube authenticated")
        return service
    except Exception as e:
        print(f"❌ YouTube auth error: {e}")
        return None

# ─── UPLOAD VIDEO ─────────────────────────────────────────────────────────────

def upload_video(video_path: Path, title: str, description: str, tags: list) -> tuple:
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
            "tags": tags[:30],  # YouTube max 30 tags
            "categoryId": "27"  # Education — best for finance monetisation
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"🚀 Uploading to YouTube: {title[:70]}...")

    try:
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  {int(status.progress() * 100)}%")

        video_id = response["id"]
        video_url = f"https://youtube.com/shorts/{video_id}"
        print(f"✅ YouTube upload success!")
        print(f"   Video ID : {video_id}")
        print(f"   URL      : {video_url}")
        return video_id, video_url

    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        return None, None

# ─── ADD TO PLAYLIST ──────────────────────────────────────────────────────────

def add_to_playlist(video_id: str, playlist_id: str) -> bool:
    """
    Adds an uploaded video to a YouTube playlist.
    Returns True on success, False on failure.
    Never crashes the main upload chain — playlist failure is logged only.
    """
    if not playlist_id:
        print("⚠️  No playlist ID set for this content type — skipping playlist assignment.")
        return False

    if not video_id:
        print("⚠️  No video ID — skipping playlist assignment.")
        return False

    try:
        youtube = get_service()
        if not youtube:
            print("⚠️  Could not authenticate for playlist — skipping.")
            return False

        body = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }

        response = youtube.playlistItems().insert(
            part="snippet",
            body=body
        ).execute()

        playlist_item_id = response.get("id", "unknown")
        print(f"✅ Added to playlist: {playlist_id}")
        print(f"   Playlist item ID : {playlist_item_id}")
        return True

    except Exception as e:
        # Never crash the upload chain — playlist is a bonus, not critical
        print(f"⚠️  Playlist assignment failed (non-critical): {e}")
        return False

# ─── BUILD TITLE + DESCRIPTION ────────────────────────────────────────────────

def build_metadata(meta: dict, today: str, content_type: str) -> tuple:
    """Returns (title, description, tags) based on CONTENT_MODE and content_type."""

    base_title = meta.get("title", f"AI360Trading — {today}")
    base_desc = meta.get("description", "Daily trading insight by AI360Trading.")
    desc_clean = base_desc.split("#")[0].strip()

    tags_map = TAGS_BY_TYPE.get(content_type, TAGS_BY_TYPE["reel"])
    tags = tags_map.get(CONTENT_MODE, tags_map["market"])

    if CONTENT_MODE == "holiday":
        label = f"🎉 {HOLIDAY_NAME}" if HOLIDAY_NAME else "🎉 Market Holiday"

        if content_type == "morning_reel":
            title = f"{label} — Morning Brief | AI360Trading"
        elif content_type == "analysis":
            title = f"{label} — Market Analysis | AI360Trading"
        elif content_type == "education":
            title = f"{label} — Trading Education | AI360Trading"
        elif content_type == "short":
            title = f"{label} — Trading Insight #Shorts | AI360Trading"
        else:
            title = f"{label} Special — ZENO Ki Baat #{today[-4:]} #Shorts"

        desc = (
            f"🎉 {label} Special — Market band hai, par learning band nahi!\n\n"
            f"💡 {desc_clean}\n\n"
            f"🌍 For investors in India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n\n"
            f"#ZenoKiBaat #ai360trading #HolidayLearning #InvestmentEducation"
        )

    elif CONTENT_MODE == "weekend":

        if content_type == "morning_reel":
            title = base_title if base_title != f"AI360Trading — {today}" else f"📚 Weekend Morning Brief | AI360Trading"
        elif content_type == "analysis":
            title = base_title if base_title != f"AI360Trading — {today}" else f"📊 Weekend Market Analysis | AI360Trading"
        elif content_type == "education":
            title = base_title if base_title != f"AI360Trading — {today}" else f"📚 Weekend Learning — Trading Education | AI360Trading"
        elif content_type == "short":
            title = base_title if base_title != f"AI360Trading — {today}" else f"📚 Weekend Wisdom #Shorts | AI360Trading"
        else:
            title = f"📚 Weekend Wisdom — ZENO Ki Baat #{today[-4:]} #Shorts"

        desc = (
            f"📚 Weekend Learning Special\n\n"
            f"💡 {desc_clean}\n\n"
            f"🌍 For investors in India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n\n"
            f"#ZenoKiBaat #ai360trading #WeekendLearning #FinancialLiteracy"
        )

    else:  # market mode

        if content_type == "morning_reel":
            title = base_title if base_title != f"AI360Trading — {today}" else f"🌅 Morning Brief — Trading Insights | AI360Trading"
        elif content_type == "analysis":
            title = base_title if base_title != f"AI360Trading — {today}" else f"📊 Nifty Analysis Today | AI360Trading"
        elif content_type == "education":
            title = base_title if base_title != f"AI360Trading — {today}" else f"📚 Trading Education | AI360Trading"
        elif content_type == "short":
            title = base_title if base_title != f"AI360Trading — {today}" else f"🎯 Swing Trade Setup #Shorts | AI360Trading"
        else:
            title = f"🎯 ZENO Ki Baat — Trading Wisdom #{today[-4:]} #Shorts"

        desc = (
            f"🎯 Daily Trading Insight by AI360Trading\n\n"
            f"💡 {desc_clean}\n\n"
            f"📊 Live market analysis for Nifty50 traders\n"
            f"🌍 Investors: India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n\n"
            f"⚠️ Educational content only. Not financial advice.\n"
            f"#ai360trading #StockMarketIndia #Nifty50 #TradingWisdom"
        )

    return title, desc, tags

# ─── FIND META FILE ───────────────────────────────────────────────────────────

def find_meta_file(content_type: str, today: str) -> tuple:
    """Find the correct meta JSON file for this content type."""
    prefix = META_PREFIXES.get(content_type, "meta_")

    # Try today's file first
    specific = OUTPUT_DIR / f"{prefix}{today}.json"
    if specific.exists():
        meta = json.loads(specific.read_text(encoding="utf-8"))
        print(f"📄 Meta file: {specific.name}")
        return specific, meta

    # Fall back to most recent matching file
    candidates = sorted(OUTPUT_DIR.glob(f"{prefix}*.json"), key=os.path.getmtime, reverse=True)
    if candidates:
        meta_path = candidates[0]
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"📄 Meta file (latest): {meta_path.name}")
        return meta_path, meta

    # Final fallback — any meta file
    all_meta = sorted(OUTPUT_DIR.glob("meta_*.json"), key=os.path.getmtime, reverse=True)
    if all_meta:
        meta_path = all_meta[0]
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"⚠️  No {prefix}*.json found — using fallback: {meta_path.name}")
        return meta_path, meta

    print("⚠️  No meta file found — using empty defaults")
    return None, {}

# ─── FIND VIDEO FILE ──────────────────────────────────────────────────────────

def find_video_file(content_type: str, today: str) -> Path | None:
    """Find the correct video file for this content type."""
    patterns = VIDEO_PATTERNS.get(content_type, VIDEO_PATTERNS["reel"])

    for pattern in patterns:
        resolved = pattern.replace("{today}", today)
        candidates = sorted(OUTPUT_DIR.glob(resolved), key=os.path.getmtime, reverse=True)
        if candidates:
            print(f"🎥 Video file: {candidates[0].name}")
            return candidates[0]

    # Last resort — any mp4
    all_mp4 = sorted(OUTPUT_DIR.glob("*.mp4"), key=os.path.getmtime, reverse=True)
    if all_mp4:
        print(f"⚠️  No specific video found — using latest: {all_mp4[0].name}")
        return all_mp4[0]

    return None

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    content_type = args.type

    print("\n" + "=" * 60)
    print(f"  upload_youtube.py — MODE: {CONTENT_MODE.upper()} | TYPE: {content_type.upper()}")
    print("=" * 60)

    today = datetime.datetime.now().strftime("%Y%m%d")

    # ── Find meta file ────────────────────────────────────────────────
    meta_path, meta = find_meta_file(content_type, today)

    # ── Find video file ───────────────────────────────────────────────
    video_path = find_video_file(content_type, today)

    if not video_path:
        print(f"❌ No video file found in {OUTPUT_DIR}/ for type={content_type} — aborting.")
        sys.exit(1)

    # ── Build title + description + tags ─────────────────────────────
    title, description, tags = build_metadata(meta, today, content_type)

    print(f"📝 Title: {title[:70]}")
    print(f"🏷️  Tags: {len(tags)} tags")

    # ── Upload ───────────────────────────────────────────────────────
    video_id, video_url = upload_video(video_path, title, description, tags)

    if video_id:
        # ── Add to correct playlist ───────────────────────────────────
        playlist_id = PLAYLIST_IDS.get(content_type)
        playlist_ok = add_to_playlist(video_id, playlist_id)
        if playlist_ok:
            print(f"📋 Playlist: ✅ Added to {content_type} playlist")
        else:
            print(f"📋 Playlist: ⚠️  Skipped (non-critical)")

        # ── Save video_id to meta — needed by upload_facebook.py ─────
        if meta_path:
            meta["youtube_video_id"] = video_id
            meta["youtube_video_url"] = video_url
            if not meta.get("public_video_url"):
                meta["public_video_url"] = video_url
            meta_path.write_text(
                json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"💾 Saved youtube_video_id to meta: {video_id}")

        # ── Save video_id to txt — used by workflows ──────────────────
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
