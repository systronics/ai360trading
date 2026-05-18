"""
upload_kids_youtube.py v2.2 — HerooQuest YouTube Upload
=========================================================
v2.2 FIXES (May 2026):

FIX 1 — Custom thumbnail upload ADDED
  Original had NO thumbnail upload → YouTube auto-picked placeholder frame
  "Scene 4" / "Scene 99" showing as thumbnail instead of Heroo character
  Fix: After video upload → immediately set custom thumbnail via API

FIX 2 — Meta key compatibility with generate_kids_video.py v2.1
  Old: meta["title_en"], meta["video_path"]
  New: meta["type"], meta["ep_title"], meta["series"]
  Fix: Reads both old and new format safely

FIX 3 — Thumbnail philosophy (Amit's requirement)
  Thumbnail must be IMAGE + TEXT that makes viewer STOP and READ
  Heroo character visible (creates emotional connection)
  Story title in HUGE yellow bold text (readable in 2 seconds)
  Moral or hook line visible in thumbnail
  This increases CTR + watch time + curiosity

  Examples of what works (from competitor analysis):
  - "NIFTY 23250 - 18 MAY 2026" huge text → viewer reads in feed
  - Dark Fact: dramatic image + bold story title → curiosity gap
  Same principle for HerooQuest:
  - Heroo + "Sona Hiran" huge text + "Patience wins!" moral snippet
  - Viewer reads it in feed → curious → clicks → watches fully
"""

import os
import json
import re
import textwrap
from pathlib import Path
from datetime import date

from PIL import Image, ImageDraw, ImageFont
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import io

TODAY     = date.today().isoformat()
DATE_STR  = date.today().strftime("%Y%m%d")
OUT       = Path("output")
IMAGE_DIR = Path("public/image")

FONT_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
]
FONT_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def lerp(c1, c2, t):
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))


# ─── READ META ────────────────────────────────────────────────────────────────

def read_meta() -> dict:
    """Read kids meta — supports both v2.0 and v2.1 formats."""
    # Try today's date first
    for path in [
        OUT / f"kids_meta_{DATE_STR}_hi.json",
        OUT / f"kids_meta_{TODAY}.json",
        OUT / f"kids_meta_{DATE_STR}.json",
    ]:
        if path.exists():
            try:
                meta = json.loads(path.read_text(encoding="utf-8"))
                print(f"[META] Loaded: {path.name}")
                return meta
            except: pass

    # Search for most recent
    candidates = sorted(OUT.glob("kids_meta_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        meta = json.loads(candidates[0].read_text(encoding="utf-8"))
        print(f"[META] Loaded latest: {candidates[0].name}")
        return meta

    print("[META] No meta file found — using defaults")
    return {}


def get_title(meta: dict) -> str:
    """Extract title from meta — handles both old and new format."""
    # New format (v2.1)
    if meta.get("ep_title"):
        ep    = meta.get("ep_title", "Story")
        series = meta.get("series", "HerooQuest")
        ep_num = meta.get("episode", 1)
        return f"Heroo: {ep} | Episode {ep_num} | HerooQuest #KidsStories"
    # Old format
    if meta.get("title_en"):
        return meta["title_en"][:100]
    if meta.get("title_hi"):
        return meta["title_hi"][:100]
    return "HerooQuest — Heroo Ki Kahani | Kids Stories"


def get_video_path(meta: dict) -> str:
    """Get video file path from meta."""
    # New format
    if meta.get("video_id") and (OUT / f"kids_full_{DATE_STR}_hi.mp4").exists():
        return str(OUT / f"kids_full_{DATE_STR}_hi.mp4")
    # Old format
    if meta.get("video_path") and Path(meta["video_path"]).exists():
        return meta["video_path"]
    # Search
    candidates = sorted(OUT.glob("kids_full_*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        return str(candidates[0])
    candidates = sorted(OUT.glob("kids_*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    return str(candidates[0]) if candidates else ""


def get_short_path(meta: dict) -> str:
    """Get cliffhanger short path."""
    candidates = sorted(OUT.glob("kids_cliffhanger_*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates: return str(candidates[0])
    if meta.get("short_path") and Path(meta.get("short_path","")).exists():
        return meta["short_path"]
    return ""


def get_ep_info(meta: dict) -> dict:
    """Extract episode info from meta."""
    return {
        "ep_title": meta.get("ep_title", meta.get("title_en", "Heroo Ki Kahani")),
        "series":   meta.get("series",   "HerooQuest"),
        "episode":  meta.get("episode",  1),
        "moral":    meta.get("moral",    "Every story has a lesson"),
        "lang":     meta.get("lang",     "hi"),
    }


# ─── THUMBNAIL BUILDER ────────────────────────────────────────────────────────

def build_thumbnail_full(ep_info: dict) -> Path:
    """
    Build 16:9 thumbnail for full story video.
    Goal: viewer stops scrolling to READ it.

    Layout (based on competitor analysis):
    - Left half: Story title in HUGE yellow text (readable in feed)
                 Moral snippet below title (hook text)
                 Episode badge at bottom left
    - Right half: Heroo character (65% height, emotional expression)
    - Background: Dark gradient + colourful accent elements
    - Brand badge: HerooQuest red pill top left
    - Series name: below title in white

    Why this works:
    - Heroo face = emotional connection, viewer recognises character
    - "Sona Hiran" huge text = viewer reads it in feed without clicking
    - "Patience wins!" moral = curiosity, makes them want to know the full story
    - Dark background = text pops out clearly
    """
    W, H  = 1280, 720
    thumb = Image.new("RGB", (W, H))
    px    = thumb.load()

    # Background: deep dark blue-purple gradient
    for y in range(H):
        c = lerp((8, 12, 35), (20, 15, 50), y/H)
        for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(thumb, "RGBA")

    # Colourful accent element — diagonal stripe left side
    for i in range(0, H, 40):
        draw.line([(0, i), (60, i+40)], fill=(255, 180, 0, 40), width=8)

    # Accent bars
    draw.rectangle([(0, 0), (W, 10)], fill=(255, 180, 0))
    draw.rectangle([(0, H-10), (W, H)], fill=(255, 180, 0))

    # ── Heroo character (right side, large) ──────────────────────────────────
    heroo_path = IMAGE_DIR / "heroo.png"
    if heroo_path.exists():
        try:
            heroo   = Image.open(str(heroo_path)).convert("RGBA")
            heroo_h = int(H * 0.88)
            heroo_w = int(heroo.width * (heroo_h / heroo.height))
            heroo   = heroo.resize((heroo_w, heroo_h), Image.LANCZOS)
            # Right side, bottom-aligned
            hx      = W - heroo_w + 20
            hy      = H - heroo_h
            thumb.paste(heroo, (hx, hy), heroo)
            print("[THUMB] Heroo character added")
        except Exception as e:
            print(f"[THUMB] Heroo load error: {e}")

    draw = ImageDraw.Draw(thumb, "RGBA")

    # ── Text area (left 55% of frame) ────────────────────────────────────────
    f_ep_title = get_font(FONT_BOLD, 95)
    f_series   = get_font(FONT_BOLD, 38)
    f_moral    = get_font(FONT_BOLD, 46)
    f_ep_num   = get_font(FONT_BOLD, 36)
    f_brand    = get_font(FONT_BOLD, 34)

    # Series name (smaller, white)
    series_text = ep_info["series"].upper()
    draw.text((50, 30), series_text, font=f_series, fill=(200, 200, 200), anchor="la")

    # Episode title — HUGE yellow (main readable element)
    ep_title = ep_info["ep_title"].upper()
    # Strip Hindi chars for PIL
    safe_title = re.sub(r'[\u0900-\u097F]+', '', ep_title).strip() or ep_title[:12]
    title_lines = textwrap.wrap(safe_title, width=10)
    ty = 90
    for line in title_lines[:2]:
        # Drop shadow for readability
        for dx, dy in [(-3,3),(3,-3),(3,3),(-3,-3)]:
            draw.text((50+dx, ty+dy), line, font=f_ep_title, fill=(0,0,0,200), anchor="la")
        draw.text((50, ty), line, font=f_ep_title, fill=(255, 200, 0), anchor="la")
        ty += 108

    # Moral — white text with dark backing strip
    moral_text = ep_info["moral"].upper()
    safe_moral = re.sub(r'[\u0900-\u097F]+', '', moral_text).strip()[:40]
    moral_w_start = 30
    moral_y       = min(ty + 20, H - 180)
    draw.rounded_rectangle([(moral_w_start, moral_y), (int(W*0.56), moral_y+65)],
                            radius=12, fill=(0,0,0,160))
    draw.rectangle([(moral_w_start, moral_y), (moral_w_start+6, moral_y+65)],
                   fill=(255, 200, 0))
    draw.text((moral_w_start+20, moral_y+32), f"💡 {safe_moral}",
              font=f_moral, fill=(255, 255, 255), anchor="lm")

    # Episode number badge (bottom left)
    ep_num = ep_info["episode"]
    draw.rounded_rectangle([(50, H-80), (220, H-20)], radius=12, fill=(255, 200, 0))
    draw.text((135, H-50), f"Ep {ep_num}", font=f_ep_num, fill=(0,0,0), anchor="mm")

    # HerooQuest brand pill (top right)
    draw.rounded_rectangle([(W-250, 15), (W-10, 65)], radius=16, fill=(220, 30, 30))
    draw.text((W-130, 40), "HerooQuest ★", font=f_brand, fill=(255,255,255), anchor="mm")

    path = OUT / f"kids_thumb_full_{DATE_STR}.png"
    thumb.save(str(path), quality=95)
    print(f"[THUMB] Full video thumbnail: {path.name}")
    return path


def build_thumbnail_short(ep_info: dict, is_cliffhanger: bool = True) -> Path:
    """
    Build 9:16 (vertical) thumbnail for HerooQuest shorts.
    Same principle: large readable text + Heroo character.
    """
    W, H  = 1080, 1920
    thumb = Image.new("RGB", (W, H))
    px    = thumb.load()

    # Bright colourful background for kids
    bg_top = (15, 35, 90)
    bg_bot = (30, 70, 160)
    for y in range(H):
        c = lerp(bg_top, bg_bot, y/H)
        for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(thumb, "RGBA")
    draw.rectangle([(0, 0), (W, 14)],   fill=(255, 200, 0))
    draw.rectangle([(0, H-14), (W, H)], fill=(255, 200, 0))

    # Heroo — bottom centre, large
    heroo_path = IMAGE_DIR / "heroo.png"
    if heroo_path.exists():
        try:
            heroo   = Image.open(str(heroo_path)).convert("RGBA")
            heroo_h = int(H * 0.65)
            heroo_w = int(heroo.width * (heroo_h / heroo.height))
            heroo   = heroo.resize((heroo_w, heroo_h), Image.LANCZOS)
            thumb.paste(heroo, ((W-heroo_w)//2, H-heroo_h-30), heroo)
        except Exception as e:
            print(f"[THUMB] Short Heroo: {e}")

    draw = ImageDraw.Draw(thumb, "RGBA")

    f_big  = get_font(FONT_BOLD, 130)
    f_sub  = get_font(FONT_BOLD, 64)
    f_hook = get_font(FONT_BOLD, 52)
    f_br   = get_font(FONT_REG,  36)

    # Main title — HUGE yellow
    ep_title = ep_info["ep_title"].upper()
    safe     = re.sub(r'[\u0900-\u097F]+', '', ep_title).strip() or ep_title[:10]
    lines    = textwrap.wrap(safe, width=9)
    ty = 80
    for line in lines[:2]:
        for dx, dy in [(-4,4),(4,-4),(-4,-4),(4,4)]:
            draw.text((W//2+dx, ty+dy), line, font=f_big, fill=(0,0,0,200), anchor="mm")
        draw.text((W//2, ty), line, font=f_big, fill=(255, 200, 0), anchor="mm")
        ty += 150

    # Cliffhanger / DYK badge
    badge = "😱 KYA HUA?" if is_cliffhanger else "🤔 KYA TUM JAANTE HO?"
    draw.rounded_rectangle([(80, ty+10), (W-80, ty+90)], radius=16, fill=(220,30,30))
    draw.text((W//2, ty+50), badge, font=f_sub, fill=(255,255,255), anchor="mm")
    ty += 110

    # Moral (hook line that creates curiosity)
    moral = ep_info["moral"].upper()
    safe_m= re.sub(r'[\u0900-\u097F]+', '', moral).strip()[:35]
    if safe_m:
        draw.text((W//2, ty+20), safe_m, font=f_hook, fill=(200,230,255), anchor="mm")

    # Brand
    draw.rounded_rectangle([(W//2-200, H-120), (W//2+200, H-50)], radius=14, fill=(220,30,30))
    draw.text((W//2, H-85), "HerooQuest ★", font=f_br, fill=(255,255,255), anchor="mm")

    path = OUT / f"kids_thumb_short_{DATE_STR}.png"
    thumb.save(str(path), quality=95)
    return path


# ─── YOUTUBE SERVICE ──────────────────────────────────────────────────────────

def get_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS_KIDS")
        if not creds_json and (Path("output")/"token_kids.json").exists():
            creds_json = (Path("output")/"token_kids.json").read_text()
        if not creds_json:
            print("❌ YOUTUBE_CREDENTIALS_KIDS not set — skipping")
            return None
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"❌ YouTube Kids auth: {e}")
        return None


def upload_thumbnail(youtube, video_id: str, thumb_path: Path):
    """
    Upload custom thumbnail to YouTube video.
    This is the KEY fix — without this, YouTube auto-picks a random frame.
    """
    if not thumb_path or not thumb_path.exists():
        print(f"[THUMB] Thumbnail not found: {thumb_path}")
        return False
    try:
        media = MediaFileUpload(str(thumb_path), mimetype="image/png", resumable=False)
        youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
        print(f"  ✅ Thumbnail uploaded for video {video_id}")
        return True
    except Exception as e:
        print(f"  ⚠️ Thumbnail upload failed: {e}")
        return False


# ─── MAIN UPLOAD ──────────────────────────────────────────────────────────────

def main():
    meta    = read_meta()
    ep_info = get_ep_info(meta)
    youtube = get_service()

    if not youtube:
        print("❌ Cannot upload — no YouTube credentials")
        return

    print(f"[YT-KIDS] Episode: {ep_info['ep_title']} | Series: {ep_info['series']}")

    # Build thumbnails with proper text + character
    thumb_full  = build_thumbnail_full(ep_info)
    thumb_short = build_thumbnail_short(ep_info, is_cliffhanger=True)

    title    = get_title(meta)
    moral    = ep_info["moral"]
    series   = ep_info["series"]
    ep_num   = ep_info["episode"]
    ep_title = ep_info["ep_title"]
    lang     = ep_info["lang"]

    seo_tags = [
        "HerooQuest","KidsStories","AnimatedStories","PixarStyle","ChildrenEducation",
        "KidsCartoon","HindiKahani","KidsEnglish","MoralStories","BedtimeStories",
        "KidsAnimation","HerooKiKahani","ChildrenStories","FamilyFriendly","Educational",
        ep_title.replace(" ",""),
    ]

    description = (
        f"🌟 HerooQuest — {series}\n"
        f"Episode {ep_num}: {ep_title}\n"
        f"💡 Today's Moral: {moral}\n\n"
        f"Watch Heroo's exciting adventure and learn today's life lesson!\n"
        f"New story every day — Subscribe for more! 🔔\n\n"
        f"Subscribe: https://youtube.com/@HerooQuest\n\n"
        f"#HerooQuest #KidsStories #AnimatedStories #ChildrenEducation #MoralStories"
    )

    # ── Upload full story video ───────────────────────────────────────────────
    video_path = get_video_path(meta)
    if video_path and Path(video_path).exists():
        print(f"[YT-KIDS] Uploading full story: {title[:60]}")
        body = {
            "snippet": {
                "title":                title[:100],
                "description":          description,
                "tags":                 seo_tags,
                "categoryId":           "27",
                "defaultLanguage":      lang,
                "defaultAudioLanguage": lang,
            },
            "status": {
                "privacyStatus":           "public",
                "selfDeclaredMadeForKids": True,
                "madeForKids":             True,
            }
        }
        media  = MediaFileUpload(video_path, resumable=True, chunksize=10*1024*1024)
        try:
            req    = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            resp   = None
            while resp is None:
                status, resp = req.next_chunk()
                if status: print(f"  {int(status.progress()*100)}%")
            vid_id = resp["id"]
            print(f"  ✅ Full story uploaded: https://youtube.com/watch?v={vid_id}")

            # Set custom thumbnail immediately after upload
            upload_thumbnail(youtube, vid_id, thumb_full)

            meta["youtube_video_id"] = vid_id
            meta["youtube_video_url"] = f"https://www.youtube.com/watch?v={vid_id}"
        except Exception as e:
            print(f"  ❌ Full story upload failed: {e}")
    else:
        print(f"[YT-KIDS] Full story video not found: {video_path}")

    # ── Upload cliffhanger short ──────────────────────────────────────────────
    short_path = get_short_path(meta)
    if short_path and Path(short_path).exists():
        short_title = f"Heroo: {ep_title} 😱 Kya hua? | HerooQuest #Shorts"
        short_desc  = (
            f"🌟 {series} Ep {ep_num}: {ep_title}\n"
            f"Watch the full episode on HerooQuest channel!\n"
            f"💡 Moral: {moral}\n\n"
            f"#HerooQuest #KidsShorts #ChildrenStories #MoralStories"
        )
        short_body = {
            "snippet": {
                "title":       short_title[:100],
                "description": short_desc,
                "tags":        seo_tags + ["Shorts","KidsShorts"],
                "categoryId":  "27",
            },
            "status": {
                "privacyStatus":           "public",
                "selfDeclaredMadeForKids": True,
                "madeForKids":             True,
            }
        }
        try:
            s_media = MediaFileUpload(short_path, resumable=True)
            s_req   = youtube.videos().insert(part="snippet,status", body=short_body, media_body=s_media)
            s_resp  = None
            while s_resp is None:
                status, s_resp = s_req.next_chunk()
                if status: print(f"  {int(status.progress()*100)}%")
            s_id = s_resp["id"]
            print(f"  ✅ Short uploaded: https://youtube.com/shorts/{s_id}")

            # Set custom thumbnail for short too
            upload_thumbnail(youtube, s_id, thumb_short)
        except Exception as e:
            print(f"  ❌ Short upload failed: {e}")

    # Save updated meta
    for mp in [OUT/f"kids_meta_{DATE_STR}_hi.json", OUT/f"kids_meta_{TODAY}.json"]:
        if mp.exists():
            mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[YT-KIDS] Done")


if __name__ == "__main__":
    main()
