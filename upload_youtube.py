import os
import json
import datetime
import glob
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
    if not youtube: 
        print("❌ Could not connect to YouTube Service.")
        return None

    # Category 27 is Education
    body = {
        'snippet': {
            'title': title[:100], 
            'description': description,
            'tags': ['AI360Trading', 'ZenoKiBaat', 'StockMarketIndia', 'Shorts'],
            'categoryId': '27' 
        },
        'status': {
            'privacyStatus': 'public', 
            'selfDeclaredMadeForKids': False 
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
    
    # 1. Look for the metadata file
    # Priority: meta_YYYYMMDD.json -> any meta_*.json
    meta_files = list(output_dir.glob(f"meta_{today}.json"))
    if not meta_files:
        meta_files = list(output_dir.glob("meta_*.json"))
    
    if meta_files:
        # Sort by creation time to get the newest
        meta_files.sort(key=os.path.getmtime, reverse=True)
        meta_path = meta_files[0]
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        title = meta.get("title", f"ZENO Ki Baat - {today} #Shorts")
        description = meta.get("description", "Daily Trading Wisdom by @ai360trading.in")
        print(f"📄 Using metadata from: {meta_path.name}")
    else:
        title = f"ZENO Ki Baat - {today} #Shorts"
        description = "Expert trading insights for the Indian Market. \nVisit: ai360trading.in"
        print("⚠️ No metadata file found. Using default text.")

    # 2. Look for the Video file
    # Priority: reel_YYYYMMDD.mp4 -> any reel_*.mp4 -> any .mp4
    video_path = None
    potential_videos = list(output_dir.glob(f"reel_{today}.mp4"))
    
    if not potential_videos:
        potential_videos = list(output_dir.glob("reel_*.mp4"))
    
    if not potential_videos:
        potential_videos = list(output_dir.glob("*.mp4"))

    if potential_videos:
        # Always pick the newest file in the folder
        potential_videos.sort(key=os.path.getmtime, reverse=True)
        video_path = potential_videos[0]
        print(f"🎥 Found video file: {video_path.name}")
    else:
        print(f"❌ Critical Error: No video found in {output_dir}")
        return

    # 3. Execute Upload
    upload_video(video_path, title, description)

if __name__ == "__main__":
    main()
