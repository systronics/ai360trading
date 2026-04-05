# upload_kids_youtube.py
# Uploads to a SEPARATE YouTube Kids channel (uses YOUTUBE_CREDENTIALS_KIDS secret)
import os, json
from pathlib import Path
from datetime import date
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

TODAY = date.today().isoformat()
META_PATH = Path(f"output/kids_meta_{TODAY}.json")
meta = json.loads(META_PATH.read_text())

creds_json = json.loads(os.environ["YOUTUBE_CREDENTIALS_KIDS"])
creds = Credentials.from_authorized_user_info(creds_json)
youtube = build("youtube", "v3", credentials=creds)

# Upload full video
print("[YT-KIDS] Uploading full video...")
body = {
    "snippet": {
        "title": meta["title_en"][:100],
        "description": (
            f"{meta['description_en']}\n\n"
            f"Hindi: {meta['title_hi']}\n\n"
            f"Moral: {meta['moral_en']}\n\n"
            "#KidsStories #AnimatedStories #PixarStyle #ChildrenEducation "
            "#KidsCartoon #HindiKahani #KidsEnglish #MoralStories"
        ),
        "tags": meta["seo_tags"],
        "categoryId": "27",           # Education
        "defaultLanguage": "en",
        "defaultAudioLanguage": "en",
    },
    "status": {
        "privacyStatus": "public",
        "selfDeclaredMadeForKids": True,   # CRITICAL — marks as kids content
        "madeForKids": True,
    }
}
media = MediaFileUpload(meta["video_path"], resumable=True, chunksize=10*1024*1024)
response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()

video_id = response["id"]
meta["youtube_video_id"] = video_id
meta["youtube_video_url"] = f"https://www.youtube.com/watch?v={video_id}"
meta["public_video_url"] = meta["youtube_video_url"]
META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
print(f"[YT-KIDS] Uploaded: https://youtu.be/{video_id}")

# Upload short (9:16) to same channel
print("[YT-KIDS] Uploading short...")
short_body = {
    "snippet": {
        "title": f"#{meta['title_en'][:80]} #Shorts #KidsStories",
        "description": meta["description_en"],
        "tags": meta["seo_tags"] + ["Shorts"],
        "categoryId": "27",
    },
    "status": {
        "privacyStatus": "public",
        "selfDeclaredMadeForKids": True,
        "madeForKids": True,
    }
}
short_media = MediaFileUpload(meta["short_path"], resumable=True)
short_resp = youtube.videos().insert(
    part="snippet,status", body=short_body, media_body=short_media
).execute()
print(f"[YT-KIDS] Short uploaded: https://youtu.be/{short_resp['id']}")
