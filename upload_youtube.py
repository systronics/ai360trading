import os
import json
import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── AUTHENTICATION ──────────────────────────────────────────────────────────
def get_service():
    """Authenticates using the YOUTUBE_CREDENTIALS environment variable."""
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json:
            print("❌ Error: YOUTUBE_CREDENTIALS secret is empty.")
            return None
            
        info = json.loads(creds_json)
        creds = Credentials.from_authorized_user_info(info)
        return build('youtube', 'v3', credentials=creds)
    except Exception as e:
        print(f"❌ Auth Error: {e}")
        return None

def upload_video(video_path, title, description):
    youtube = get_service()
    if not youtube: return

    # Category 27 is Education; perfect for Trading Wisdom
    body = {
        'snippet': {
            'title': title[:100], # YouTube limit is 100 chars
            'description': description,
            'tags': ['AI360Trading', 'ZenoKiBaat', 'StockMarketIndia', 'Shorts'],
            'categoryId': '27' 
        },
        'status': {
            'privacyStatus': 'public', 
            'selfDeclaredMadeForKids': False # Essential for comments/reach
        }
    }

    media = MediaFileUpload(str(video_path), mimetype='video/mp4', resumable=True)
    print(f"🚀 Uploading to YouTube: {title}")
    
    try:
        request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")
        
        video_id = response['id']
        shorts_url = f"https://youtube.com/shorts/{video_id}"
        
        print(f"✅ Success! Video ID: {video_id}")
        print(f"🔗 LIVE LINK: {shorts_url}") 
        return shorts_url
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
        return None

# ─── MAIN ENGINE ─────────────────────────────────────────────────────────────
def main():
    today = datetime.datetime.now().strftime("%Y%m%d")
    output_dir = Path("output")
    
    # Robust file detection
    meta_path = output_dir / f"meta_{today}.json"
    video_path = output_dir / f"reel_{today}.mp4"

    # Fallback: if exact date file isn't found, grab the first .mp4 in output
    if not video_path.exists():
        video_files = list(output_dir.glob("*.mp4"))
        if video_files:
            video_path = video_files[0]
            print(f"⚠️ Exact date match not found. Using: {video_path.name}")
        else:
            print(f"❌ No video found in {output_dir}")
            return

    # Load Metadata
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        title = meta.get("title", f"ZENO Ki Baat - {today}")
        description = meta.get("description", "Daily Trading Wisdom by @ai360trading.in")
    else:
        # Emergency Fallback description
        title = f"ZENO Ki Baat - {today} #Shorts"
        description = "Expert trading insights for the Indian Market. \nVisit: ai360trading.in"

    upload_video(video_path, title, description)

if __name__ == "__main__":
    main()
