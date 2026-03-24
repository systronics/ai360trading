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

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['AI360Trading', 'Zeno', 'Shorts'],
            'categoryId': '27' # Education
        },
        'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}
    }

    media = MediaFileUpload(str(video_path), mimetype='video/mp4', resumable=True)
    print(f"🚀 Uploading: {title}")
    
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
    
    # --- CLICKABLE LINK LOGIC ---
    video_id = response['id']
    shorts_url = f"https://youtube.com/shorts/{video_id}"
    
    print(f"✅ Success! Video ID: {video_id}")
    print(f"🔗 LIVE LINK: {shorts_url}") # This will be clickable in GitHub Logs
    return shorts_url

# ─── MAIN ENGINE ─────────────────────────────────────────────────────────────
def main():
    today = datetime.datetime.now().strftime("%Y%m%d")
    output_dir = Path("output")
    meta_path = output_dir / f"meta_{today}.json"
    video_path = output_dir / f"reel_{today}.mp4"

    if not video_path.exists():
        print(f"❌ Video not found: {video_path}")
        return

    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        title = meta.get("title", f"ZENO Daily {today}")
        description = meta.get("description", "Daily Market Wisdom")
    else:
        title = f"ZENO Ki Baat - {today} #Shorts"
        description = "Automated trading wisdom by AI360."

    upload_video(video_path, title, description)

if __name__ == "__main__":
    main()
