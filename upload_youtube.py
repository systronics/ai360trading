"""
upload_youtube.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uploads videos to YouTube. Pass --type to select the right file.

Supported types:
  reel      → output/reel_YYYYMMDD.mp4         + meta_YYYYMMDD.json
  morning   → output/morning_reel_YYYYMMDD.mp4 + morning_reel_meta_YYYYMMDD.json
  analysis  → output/analysis_video.mp4        + analysis_meta_YYYYMMDD.json
  education → output/education_video.mp4       + education_meta_YYYYMMDD.json
  short     → output/short_YYYYMMDD.mp4        + short_meta_YYYYMMDD.json
             (also matches short2_*, short3_*, shorts_*)

Critical chain:
  generate_*.py → upload_youtube.py --type X → upload_facebook.py → upload_instagram.py

After upload, this script:
  1. Saves video_id into the matched meta_*.json (needed by upload_instagram.py)
  2. Saves output/youtube_video_id.txt (used by other scripts if needed)

SEO strategy:
  - Tags cover India, USA, UK, Brazil, UAE for maximum CPM
  - Category 22 = People & Blogs for Shorts; 27 = Education for long-form
  - Titles are mode-aware (market / weekend / holiday)

Last updated: April 2026 — added --type short support
"""

import os
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
OUTPUT_DIR = Path("output")

# ─── File resolution map — type → (video_patterns, meta_patterns) ─────────────
# Patterns are tried in order; first match wins.
TYPE_CONFIG = {
    "reel": {
        "video": ["reel_{today}.mp4", "reel_*.mp4"],
        "meta":  ["meta_{today}.json", "meta_*.json"],
        "is_short": True,
        "label": "ZENO Reel",
    },
    "morning": {
        "video": ["morning_reel_{today}.mp4", "morning_reel_*.mp4", "morning_*.mp4"],
        "meta":  ["morning_reel_meta_{today}.json", "morning_reel_meta_*.json", "morning_meta_*.json"],
        "is_short": True,
        "label": "Morning Reel",
    },
    "analysis": {
        "video": ["analysis_video_{today}.mp4", "analysis_video.mp4", "analysis_*.mp4"],
        "meta":  ["analysis_meta_{today}.json", "analysis_meta_*.json"],
        "is_short": False,
        "label": "Market Analysis",
    },
    "education": {
        "video": ["education_video_{today}.mp4", "education_video.mp4", "education_*.mp4"],
        "meta":  ["education_meta_{today}.json", "education_meta_*.json"],
        "is_short": False,
        "label": "Education",
    },
    "short": {
        "video": [
            "short_{today}.mp4",
            "short2_{today}.mp4", "short3_{today}.mp4",
            "shorts_{today}.mp4",
            "short2_*.mp4", "short3_*.mp4",
            "short_*.mp4", "shorts_*.mp4",
        ],
        "meta": [
            "short_meta_{today}.json",
            "short2_meta_{today}.json", "short3_meta_{today}.json",
            "shorts_meta_{today}.json",
            "short2_meta_*.json", "short3_meta_*.json",
            "short_meta_*.json", "shorts_meta_*.json",
        ],
        "is_short": True,
        "label": "Short",
    },
}

# ─── SEO Tags ─────────────────────────────────────────────────────────────────

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
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json:
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

# ─── UPLOAD ───────────────────────────────────────────────────────────────────

def upload_video(video_path: Path, title: str, description: str, tags: list, is_short: bool):
    youtube = get_service()
    if not youtube:
        return None, None

    # Shorts use category 22 (People & Blogs) — better for Shorts algorithm
    # Long-form use category 27 (Education) — better for finance monetisation
    category = "22" if is_short else "27"

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags[:30],
            "categoryId": category,
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
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
        # Shorts get the /shorts/ URL, long-form get /watch?v=
        if is_short:
            video_url = f"https://youtube.com/shorts/{video_id}"
        else:
            video_url = f"https://youtube.com/watch?v={video_id}"

        print(f"✅ YouTube upload success!")
        print(f"   Video ID : {video_id}")
        print(f"   URL      : {video_url}")
        return video_id, video_url

    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        return None, None

# ─── FIND FILE HELPER ─────────────────────────────────────────────────────────

def find_file(patterns: list, today: str) -> Path | None:
    for pattern in patterns:
        resolved = pattern.replace("{today}", today)
        candidates = sorted(OUTPUT_DIR.glob(resolved), key=os.path.getmtime, reverse=True)
        if candidates:
            return candidates[0]
    return None

# ─── BUILD TITLE + DESCRIPTION ────────────────────────────────────────────────

def build_metadata(meta: dict, today: str, upload_type: str) -> tuple:
    label = TYPE_CONFIG[upload_type]["label"]
    base_title = meta.get("title", f"{label} — {today}")
    base_desc = meta.get("description", f"Daily {label.lower()} by AI360Trading.")
    desc_clean = base_desc.split("#")[0].strip()

    if CONTENT_MODE == "holiday":
        holiday_label = f"🎉 {HOLIDAY_NAME}" if HOLIDAY_NAME else "🎉 Market Holiday"
        title = f"{holiday_label} Special — {label} #{today[-4:]} #Shorts"
        desc = (
            f"🎉 {holiday_label} Special — Market band hai, par learning band nahi!\n\n"
            f"💡 {desc_clean}\n\n"
            f"🌍 For investors in India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n\n"
            f"#ZenoKiBaat #ai360trading #HolidayLearning #InvestmentEducation"
        )
        tags = HOLIDAY_TAGS

    elif CONTENT_MODE == "weekend":
        title = f"📚 Weekend Wisdom — {label} #{today[-4:]} #Shorts"
        desc = (
            f"📚 Weekend Learning Special\n\n"
            f"💡 {desc_clean}\n\n"
            f"🌍 For investors in India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n\n"
            f"#ZenoKiBaat #ai360trading #WeekendLearning #FinancialLiteracy"
        )
        tags = WEEKEND_TAGS

    else:  # market
        title = f"🎯 {label} — AI360Trading #{today[-4:]} #Shorts"
        desc = (
            f"🎯 {label} by AI360Trading\n\n"
            f"💡 {desc_clean}\n\n"
            f"📊 Live market analysis for Nifty50 traders\n"
            f"🌍 Investors: India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n\n"
            f"⚠️ Educational content only. Not financial advice.\n"
            f"#ZenoKiBaat #ai360trading #TradingWisdom #Nifty50"
        )
        tags = MARKET_TAGS

    return title, desc, tags

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type",
        choices=["reel", "analysis", "education", "morning", "short"],
        default="reel",
        help="Type of video to upload",
    )
    args = parser.parse_args()
    upload_type = args.type
    cfg = TYPE_CONFIG[upload_type]

    print("\n" + "=" * 55)
    print(f" upload_youtube.py — TYPE: {upload_type.upper()} | MODE: {CONTENT_MODE.upper()}")
    print("=" * 55)

    today = datetime.datetime.now().strftime("%Y%m%d")

    # ── Find meta file ──────────────────────────────────────────────────────
    meta_path = find_file(cfg["meta"], today)
    if meta_path:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"📄 Meta file: {meta_path.name}")
    else:
        meta_path = None
        meta = {}
        print("⚠️  No meta file found — using defaults")

    # ── Find video file ─────────────────────────────────────────────────────
    video_path = find_file(cfg["video"], today)
    if not video_path:
        print(f"❌ No video file found for type '{upload_type}' in {OUTPUT_DIR}/ — aborting.")
        print(f"   Searched patterns: {cfg['video']}")
        return

    print(f"🎥 Video file: {video_path.name}")

    # ── Build title + description + tags ────────────────────────────────────
    title, description, tags = build_metadata(meta, today, upload_type)

    # ── Upload ───────────────────────────────────────────────────────────────
    video_id, video_url = upload_video(
        video_path, title, description, tags, cfg["is_short"]
    )

    if video_id:
        # ── Save video_id to meta — CRITICAL for Instagram chain ────────────
        if meta_path:
            meta["youtube_video_id"] = video_id
            meta["youtube_video_url"] = video_url
            if not meta.get("public_video_url"):
                meta["public_video_url"] = video_url
            meta_path.write_text(
                json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"💾 Saved youtube_video_id to meta: {video_id}")

        # ── Save video_id to txt ─────────────────────────────────────────────
        id_path = OUTPUT_DIR / "youtube_video_id.txt"
        id_path.write_text(video_id, encoding="utf-8")
        print(f"💾 Saved video ID to: {id_path.name}")

    print("\n" + "=" * 55)
    print(f" upload_youtube.py — {'SUCCESS' if video_id else 'FAILED'}")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
