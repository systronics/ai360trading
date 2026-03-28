"""
upload_youtube.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uploads ZENO Reel to YouTube.

Critical chain:
  generate_reel.py → upload_youtube.py → upload_facebook.py → upload_instagram.py

After upload, this script:
  1. Saves video_id into meta_YYYYMMDD.json (needed by upload_instagram.py)
  2. Saves output/youtube_video_id.txt (used by other scripts if needed)

SEO strategy:
  - Tags cover India, USA, UK, Brazil, UAE for maximum CPM
  - Category 27 = Education (best for finance content monetisation)
  - Titles are mode-aware (market / weekend / holiday)

Last updated: March 2026
"""

import os
import json
import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── CONFIG ───────────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "")
OUTPUT_DIR   = Path("output")

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


# ─── UPLOAD ───────────────────────────────────────────────────────────────────
def upload_video(video_path: Path, title: str, description: str, tags: list) -> str | None:
    """
    Uploads a video to YouTube with resumable upload.
    Returns the video URL on success, None on failure.
    """
    youtube = get_service()
    if not youtube:
        return None

    body = {
        "snippet": {
            "title":       title[:100],
            "description": description,
            "tags":        tags[:30],   # YouTube max 30 tags
            "categoryId":  "27"         # Education — best for finance monetisation
        },
        "status": {
            "privacyStatus":           "public",
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


# ─── BUILD TITLE + DESCRIPTION ────────────────────────────────────────────────
def build_metadata(meta: dict, today: str) -> tuple[str, str, list]:
    """Returns (title, description, tags) based on CONTENT_MODE."""

    base_title = meta.get("title", f"ZENO Ki Baat — {today}")
    base_desc  = meta.get("description", "Daily trading wisdom by ZENO.")
    desc_clean = base_desc.split("#")[0].strip()

    if CONTENT_MODE == "holiday":
        label = f"🎉 {HOLIDAY_NAME}" if HOLIDAY_NAME else "🎉 Market Holiday"
        title = f"{label} Special — ZENO Ki Baat #{today[-4:]} #Shorts"
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
        title = f"📚 Weekend Wisdom — ZENO Ki Baat #{today[-4:]} #Shorts"
        desc  = (
            f"📚 Weekend Learning Special\n\n"
            f"💡 {desc_clean}\n\n"
            f"🌍 For investors in India, USA, UK, Brazil & UAE\n"
            f"🌐 Website: https://ai360trading.in\n"
            f"📱 Telegram: https://t.me/ai360trading\n\n"
            f"#ZenoKiBaat #ai360trading #WeekendLearning #FinancialLiteracy"
        )
        tags = WEEKEND_TAGS

    else:  # market mode
        title = f"🎯 ZENO Ki Baat — Trading Wisdom #{today[-4:]} #Shorts"
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

    return title, desc, tags


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 55)
    print(f"  upload_youtube.py — MODE: {CONTENT_MODE.upper()}")
    print("=" * 55)

    today = datetime.datetime.now().strftime("%Y%m%d")

    # ── Find meta file ─────────────────────────────────────────────────────
    meta_files = sorted(OUTPUT_DIR.glob("meta_*.json"), key=os.path.getmtime, reverse=True)
    if meta_files:
        meta_path = meta_files[0]
        meta      = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"📄 Meta file: {meta_path.name}")
    else:
        meta_path = None
        meta      = {}
        print("⚠️  No meta file found — using defaults")

    # ── Find video file ────────────────────────────────────────────────────
    video_path = None
    for pattern in [f"reel_{today}.mp4", "reel_*.mp4", "*.mp4"]:
        candidates = sorted(OUTPUT_DIR.glob(pattern), key=os.path.getmtime, reverse=True)
        if candidates:
            video_path = candidates[0]
            break

    if not video_path:
        print(f"❌ No video file found in {OUTPUT_DIR}/ — aborting.")
        return

    print(f"🎥 Video file: {video_path.name}")

    # ── Build title + description + tags ──────────────────────────────────
    title, description, tags = build_metadata(meta, today)

    # ── Upload ────────────────────────────────────────────────────────────
    video_id, video_url = upload_video(video_path, title, description, tags)

    if video_id:
        # ── Save video_id to meta — CRITICAL for Instagram chain ──────────
        if meta_path:
            meta["youtube_video_id"]  = video_id
            meta["youtube_video_url"] = video_url
            # Instagram needs a public URL — YouTube URL works perfectly
            # upload_facebook.py will overwrite this with FB URL if needed
            if not meta.get("public_video_url"):
                meta["public_video_url"] = video_url
            meta_path.write_text(
                json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"💾 Saved youtube_video_id to meta: {video_id}")

        # ── Save video_id to txt — used by daily-shorts workflow ──────────
        id_path = OUTPUT_DIR / "youtube_video_id.txt"
        id_path.write_text(video_id, encoding="utf-8")
        print(f"💾 Saved video ID to: {id_path.name}")

    print("\n" + "=" * 55)
    print(f"  upload_youtube.py — {'SUCCESS' if video_id else 'FAILED'}")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
