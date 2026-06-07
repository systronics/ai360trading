"""
upload_kids_youtube.py v2.5 — HerooQuest YouTube Upload
  v2.5 (2026-06-05): build_title() is now LANGUAGE-AWARE — the English video no
    longer gets the "Hindi Moral Story" suffix (was hardcoded). EN → "Heroo's
    Story | … | English Moral Story for Kids"; HI unchanged.
=========================================================
v2.4 (2026-05-31): AUTO-TRANSLATE SUBTITLES
  After the full video uploads, also upload the per-scene .srt caption track
  (built by generate_kids_video.py v2.6, path in meta["subtitle_srt"]) via
  subtitle_helper.upload_caption → YouTube auto-translates the captions into
  the viewer's language (US/UK/Brazil/India). Fully fail-open; needs the
  youtube.force-ssl scope on the kids token (else it logs a re-auth hint and
  skips — defaultAudioLanguage auto-captions still work).

v2.3 CHANGES (May 2026):

SEO FIX 1 — Title format improved
  Old: "Heroo: {ep_title} | Episode {ep_num} | HerooQuest #KidsStories"
  New: "{ep_title} | Heroo Ki Kahani | HerooQuest | Hindi Moral Story 2026"
  Why: "Hindi Moral Story 2026" = what parents search on YouTube
       Specific story title first = algorithm picks up search intent

SEO FIX 2 — Tags expanded from 16 to 30
  Added: HindiCartoon, BachonKiKahani, CartoonInHindi, BalKahani,
         ShortStoryForKids, HindiStories, KidsVideoHindi, MoralKahani,
         IndianKidsStories, AnimatedHindiStory, BedtimeStoryHindi
  Why: These are exactly what Indian parents search for kids content

SEO FIX 3 — Description rewritten
  First 2 lines = CTA (YouTube shows first 100 chars in search)
  Timestamps added for 7.5 min video (chapters help algorithm)
  15 hashtags at bottom (was only 5)
  Website link added

THUMBNAIL FIX — Story-specific title instead of generic
  Old: "HEROO KI KAHANI" (same every day)
  New: Today's specific story title e.g. "GURU NANAK" or "SONA HIRAN"
  Why: Specific = curiosity = more clicks
       Generic = viewer has seen before = scroll past

All v2.2 features retained (thumbnail upload, Heroo character, etc.)
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
from googleapiclient.http import MediaFileUpload

TODAY     = date.today().isoformat()
DATE_STR  = date.today().strftime("%Y%m%d")
YEAR      = date.today().year
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
    candidates = sorted(OUT.glob("kids_meta_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        meta = json.loads(candidates[0].read_text(encoding="utf-8"))
        print(f"[META] Loaded latest: {candidates[0].name}")
        return meta
    print("[META] No meta file found — using defaults")
    return {}


def get_ep_info(meta: dict) -> dict:
    return {
        "ep_title": meta.get("ep_title", meta.get("title_en", "Heroo Ki Kahani")),
        "ep_title_hi": meta.get("title_hi", ""),
        "series":   meta.get("series",   "HerooQuest"),
        "episode":  meta.get("episode",  1),
        "moral":    meta.get("moral",    "Every story has a lesson"),
        "moral_hi": meta.get("moral_hi", ""),
        "lang":     meta.get("lang",     "hi"),
        "topic_hi": meta.get("topic_hi", ""),
        "topic_en": meta.get("topic_en", ""),
    }


def get_video_path(meta: dict) -> str:
    if meta.get("video_path") and Path(meta["video_path"]).exists():
        return meta["video_path"]
    for pat in [f"kids_full_{DATE_STR}_hi.mp4", f"kids_full_{DATE_STR}.mp4", "kids_full_*.mp4", "kids_*.mp4"]:
        cands = sorted(OUT.glob(pat), key=lambda p: p.stat().st_mtime, reverse=True)
        if cands: return str(cands[0])
    return ""


def get_short_path(meta: dict) -> str:
    if meta.get("short_path") and Path(meta.get("short_path","")).exists():
        return meta["short_path"]
    cands = sorted(OUT.glob("kids_cliffhanger_*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    return str(cands[0]) if cands else ""


# ─── SEO v2.3 ─────────────────────────────────────────────────────────────────

def build_title(ep_info: dict) -> str:
    """
    v2.5: SEO-optimised, LANGUAGE-AWARE title (was hardcoded "Hindi" on the
    English video too). Structure:
      EN \u2192 {Story} | Heroo's Story | HerooQuest | English Moral Story for Kids 2026
      HI \u2192 {Story} | Heroo Ki Kahani | HerooQuest | Hindi Moral Story 2026
    Story name first = algorithm catches specific search intent.
    """
    ep_title = ep_info["ep_title"]
    # Clean Hindi chars for YouTube title (use English version)
    safe = re.sub(r'[\u0900-\u097F]+', '', ep_title).strip()
    if not safe:
        safe = ep_info.get("topic_en", "Heroo Story")[:25]
    if (ep_info.get("lang") or "hi").lower() == "en":
        return f"{safe} | Heroo's Story | HerooQuest | English Moral Story for Kids {YEAR}"[:100]
    return f"{safe} | Heroo Ki Kahani | HerooQuest | Hindi Moral Story {YEAR}"[:100]


def build_tags(ep_info: dict) -> list:
    """
    v2.3: Expanded to 30 tags.
    Mix of: brand + genre + language + specific topic
    """
    ep_title = ep_info["ep_title"]
    safe_ep  = re.sub(r'[\u0900-\u097F]+', '', ep_title).strip().replace(" ","")

    return [
        # Brand
        "HerooQuest", "HerooKiKahani", "HerooStories",
        # Genre
        "KidsStories", "MoralStories", "AnimatedStories",
        "BedtimeStories", "ChildrenStories", "ShortStoryForKids",
        # Language specific (high search volume in India)
        "HindiKahani", "HindiCartoon", "CartoonInHindi",
        "BachonKiKahani", "BalKahani", "HindiStories",
        "KidsVideoHindi", "MoralKahani", "IndianKidsStories",
        "AnimatedHindiStory", "BedtimeStoryHindi",
        # Audience
        "KidsCartoon", "ChildrenEducation", "FamilyFriendly",
        "PixarStyle", "KidsAnimation",
        # Platform
        "YouTubeKids", "KidsShorts",
        # Topic specific
        safe_ep[:30] if safe_ep else "HerooAdventure",
        f"MoralStory{YEAR}",
    ][:30]


def build_description(ep_info: dict, video_duration_min: int = 8) -> str:
    """
    v2.3: Description rewritten for CTR and algorithm.
    First 100 chars = what YouTube shows in search = must have CTA.
    Timestamps = YouTube chapters = algorithm boost.
    15 hashtags = maximum allowed for discoverability.
    """
    ep_title   = ep_info["ep_title"]
    moral      = ep_info["moral"]
    moral_hi   = ep_info.get("moral_hi", "")
    series     = ep_info["series"]
    ep_num     = ep_info["episode"]
    topic_en   = ep_info.get("topic_en", ep_title)

    # First line = appears in search results (100 char limit shown)
    first_line = f"🌟 {ep_title} — Heroo Ki Nai Kahani! Subscribe karo agar pasand aaye 🔔"

    # Timestamps for chapters (algorithm loves chapters)
    timestamps = (
        f"0:00 — Story Starts: {ep_title}\n"
        f"0:45 — Adventure Begins\n"
        f"2:30 — The Challenge\n"
        f"5:00 — Turning Point\n"
        f"7:00 — Life Lesson\n"
        f"7:30 — Moral of the Story"
    )

    hashtags = (
        "#HerooQuest #KidsStories #HindiKahani #MoralStories #AnimatedStories "
        "#BachonKiKahani #HindiCartoon #ChildrenEducation #BedtimeStories "
        "#KidsAnimation #FamilyFriendly #YouTubeKids #PixarStyle #IndianKids "
        f"#HerooKiKahani"
    )

    return (
        f"{first_line}\n\n"
        f"📖 Aaj ki Kahani: {ep_title}\n"
        f"💡 Moral: {moral}\n"
        f"{f'💭 Seekh: {moral_hi}' if moral_hi else ''}\n\n"
        f"⏱️ CHAPTERS:\n{timestamps}\n\n"
        f"🔔 Subscribe karo aur bell icon dabao — Heroo ki nayi kahani har roz!\n"
        f"📱 HerooQuest: https://youtube.com/@HerooQuest\n"
        f"🌐 Website: https://ai360trading.in\n\n"
        f"Yeh video bachon ke liye ek animated moral story hai jisme Heroo — "
        f"ek brave 10-saal-ka ladka — {topic_en} ke baare mein seekhta hai. "
        f"Har episode mein ek nayi seekh hai jo aapke bachon ko life mein help karegi.\n\n"
        f"🤖 AI tools se banayi gayi animated kahani · Family-friendly\n\n"
        f"{hashtags}"
    )[:5000]


# ─── THUMBNAIL BUILDER v2.3 ───────────────────────────────────────────────────

def build_thumbnail_full(ep_info: dict) -> Path:
    """
    v2.3: Story-specific title on thumbnail.
    Old: "HEROO KI KAHANI" (generic every day)
    New: Today's specific story e.g. "GURU NANAK" or "SONA HIRAN"
    Viewer recognises different story = curiosity = clicks

    Layout (proven by competitor analysis):
    Left: Story title HUGE yellow + moral hook + Ep badge
    Right: Heroo character 88% height
    """
    W, H = 1280, 720
    thumb = Image.new("RGB", (W, H))
    px    = thumb.load()
    for y in range(H):
        c = lerp((8, 12, 35), (20, 15, 50), y/H)
        for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(thumb, "RGBA")
    for i in range(0, H, 40):
        draw.line([(0, i), (60, i+40)], fill=(255, 180, 0, 40), width=8)
    draw.rectangle([(0, 0), (W, 10)], fill=(255, 180, 0))
    draw.rectangle([(0, H-10), (W, H)], fill=(255, 180, 0))

    # Heroo character
    heroo_path = IMAGE_DIR / "heroo.png"
    if heroo_path.exists():
        try:
            heroo   = Image.open(str(heroo_path)).convert("RGBA")
            heroo_h = int(H * 0.88)
            heroo_w = int(heroo.width * (heroo_h / heroo.height))
            heroo   = heroo.resize((heroo_w, heroo_h), Image.LANCZOS)
            thumb.paste(heroo, (W - heroo_w + 20, H - heroo_h), heroo)
        except Exception as e:
            print(f"[THUMB] Heroo: {e}")

    draw = ImageDraw.Draw(thumb, "RGBA")

    f_big   = get_font(FONT_BOLD, 95)
    f_sub   = get_font(FONT_BOLD, 46)
    f_moral = get_font(FONT_BOLD, 42)
    f_badge = get_font(FONT_BOLD, 36)
    f_brand = get_font(FONT_BOLD, 34)

    # HerooQuest brand
    draw.rounded_rectangle([(15, 15), (260, 65)], radius=14, fill=(220, 30, 30))
    draw.text((137, 40), "HerooQuest ★", font=f_brand, fill=(255,255,255), anchor="mm")

    # Episode badge
    draw.rounded_rectangle([(W-160, 15), (W-10, 65)], radius=14, fill=(255, 200, 0))
    draw.text((W-85, 40), f"Ep {ep_info['episode']}", font=f_badge, fill=(0,0,0), anchor="mm")

    # v2.3: STORY-SPECIFIC title (not generic)
    # Use topic name — the actual story e.g. "GURU NANAK" not "HEROO KI KAHANI"
    ep_title = ep_info["ep_title"]
    # Try to get the subject/topic — strip "Heroo's" and "Story" suffixes
    clean = re.sub(r"(?i)(heroo'?s?\s+|ki\s+kahani|story|ki\s+story)", "", ep_title).strip()
    safe  = re.sub(r'[\u0900-\u097F]+', '', clean).strip().upper()
    if not safe or len(safe) < 3:
        safe = re.sub(r'[\u0900-\u097F]+', '', ep_title).strip().upper()
    if not safe:
        safe  = ep_info.get("topic_en", "HEROO STORY")[:20].upper()

    title_lines = textwrap.wrap(safe, width=12)
    ty = 80
    for line in title_lines[:2]:
        for dx, dy in [(-4,4),(4,-4),(-4,-4),(4,4),(-4,0),(4,0),(0,4),(0,-4)]:
            draw.text((50+dx, ty+dy), line, font=f_big, fill=(0,0,0,230), anchor="la")
        draw.text((50, ty), line, font=f_big, fill=(255, 200, 0), anchor="la")
        ty += 110

    # Subtitle: series name
    draw.text((50, ty), ep_info["series"].upper(), font=f_sub, fill=(200,200,255), anchor="la")
    ty += 65

    # Moral strip (curiosity hook)
    safe_moral = re.sub(r'[\u0900-\u097F]+', '', ep_info["moral"]).strip()[:45]
    if safe_moral:
        strip_y = min(ty + 10, H - 100)
        draw.rectangle([(40, strip_y), (int(W*0.60), strip_y+55)], fill=(0,0,0,180))
        draw.rectangle([(40, strip_y), (46, strip_y+55)], fill=(255, 200, 0))
        draw.text((58, strip_y+27), f"💡 {safe_moral}", font=f_moral,
                  fill=(255,255,255), anchor="lm")

    path = OUT / f"kids_thumb_full_{DATE_STR}.png"
    thumb.save(str(path), quality=95)
    print(f"[THUMB] Full thumbnail: {path.name} | Title: {safe}")
    return path


def build_thumbnail_short(ep_info: dict, is_cliffhanger: bool = True) -> Path:
    """9:16 vertical thumbnail for shorts — story-specific title."""
    W, H  = 1080, 1920
    thumb = Image.new("RGB", (W, H))
    px    = thumb.load()
    for y in range(H):
        c = lerp((15, 35, 90), (30, 70, 160), y/H)
        for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(thumb, "RGBA")
    draw.rectangle([(0,0),(W,14)],   fill=(255, 200, 0))
    draw.rectangle([(0,H-14),(W,H)], fill=(255, 200, 0))

    heroo_path = IMAGE_DIR / "heroo.png"
    if heroo_path.exists():
        try:
            heroo   = Image.open(str(heroo_path)).convert("RGBA")
            heroo_h = int(H * 0.65)
            heroo_w = int(heroo.width * (heroo_h / heroo.height))
            heroo   = heroo.resize((heroo_w, heroo_h), Image.LANCZOS)
            thumb.paste(heroo, ((W-heroo_w)//2, H-heroo_h-30), heroo)
        except: pass

    draw = ImageDraw.Draw(thumb, "RGBA")

    f_big  = get_font(FONT_BOLD, 130)
    f_sub  = get_font(FONT_BOLD, 64)
    f_hook = get_font(FONT_BOLD, 52)
    f_br   = get_font(FONT_REG,  36)

    # Story-specific title
    ep_title = ep_info["ep_title"]
    clean    = re.sub(r"(?i)(heroo'?s?\s+|ki\s+kahani|story)", "", ep_title).strip()
    safe     = re.sub(r'[\u0900-\u097F]+', '', clean).strip().upper()
    if not safe: safe = re.sub(r'[\u0900-\u097F]+', '', ep_title).strip().upper()[:14]

    lines = textwrap.wrap(safe, width=9)
    ty = 80
    for line in lines[:2]:
        for dx, dy in [(-4,4),(4,-4),(-4,-4),(4,4)]:
            draw.text((W//2+dx, ty+dy), line, font=f_big, fill=(0,0,0,200), anchor="mm")
        draw.text((W//2, ty), line, font=f_big, fill=(255, 200, 0), anchor="mm")
        ty += 150

    badge = "😱 KYA HUA?" if is_cliffhanger else "🤔 KYA TUM JAANTE HO?"
    draw.rounded_rectangle([(80, ty+10), (W-80, ty+90)], radius=16, fill=(220,30,30))
    draw.text((W//2, ty+50), badge, font=f_sub, fill=(255,255,255), anchor="mm")
    ty += 110

    safe_m = re.sub(r'[\u0900-\u097F]+', '', ep_info["moral"]).strip()[:35]
    if safe_m:
        draw.text((W//2, ty+20), safe_m, font=f_hook, fill=(200,230,255), anchor="mm")

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
            print("❌ YOUTUBE_CREDENTIALS_KIDS not set"); return None
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"❌ YouTube Kids auth: {e}"); return None


def upload_thumbnail(youtube, video_id: str, thumb_path: Path) -> bool:
    if not thumb_path or not Path(str(thumb_path)).exists():
        print(f"[THUMB] Not found: {thumb_path}"); return False
    try:
        media = MediaFileUpload(str(thumb_path), mimetype="image/png", resumable=False)
        youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
        print(f"  ✅ Thumbnail uploaded: {video_id}")
        return True
    except Exception as e:
        print(f"  ⚠️ Thumbnail failed: {e}"); return False


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    meta     = read_meta()
    ep_info  = get_ep_info(meta)
    youtube  = get_service()

    if not youtube:
        print("❌ No YouTube credentials"); return

    print(f"[YT-KIDS] {ep_info['ep_title']} | {ep_info['series']}")

    # v2.3: Build thumbnails with story-specific title
    thumb_full  = build_thumbnail_full(ep_info)
    thumb_short = build_thumbnail_short(ep_info, is_cliffhanger=True)

    # v2.3: SEO-optimised title, description, tags
    title       = build_title(ep_info)
    description = build_description(ep_info)
    tags        = build_tags(ep_info)
    lang        = ep_info["lang"]

    print(f"[YT-KIDS] Title: {title[:70]}")
    print(f"[YT-KIDS] Tags: {len(tags)} | Desc: {len(description)} chars")

    # Upload full story
    video_path = get_video_path(meta)
    if video_path and Path(video_path).exists():
        body = {
            "snippet": {
                "title":                title,
                "description":          description,
                "tags":                 tags,
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
        media = MediaFileUpload(video_path, resumable=True, chunksize=10*1024*1024)
        try:
            req  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            resp = None
            while resp is None:
                status, resp = req.next_chunk()
                if status: print(f"  {int(status.progress()*100)}%")
            vid_id = resp["id"]
            print(f"  ✅ Uploaded: https://youtube.com/watch?v={vid_id}")
            upload_thumbnail(youtube, vid_id, thumb_full)
            # v2.4: upload the per-scene .srt so YouTube auto-translates the
            # kids captions per country. Fail-open (needs youtube.force-ssl;
            # if the token lacks it, defaultAudioLanguage auto-captions remain).
            srt_path = meta.get("subtitle_srt", "")
            if srt_path and Path(srt_path).exists():
                try:
                    from subtitle_helper import upload_caption
                    upload_caption(youtube, vid_id, srt_path,
                                   meta.get("subtitle_lang", lang))
                except Exception as e:
                    print(f"  ⚠️ Caption upload skipped (fail-open): {e}")
            # Auto-post the channel's own top comment with the Telegram funnel.
            try:
                import money_funnel as _mf
                _mf.post_first_comment(youtube, vid_id, lang, made_for_kids=True)
            except Exception:
                pass
            meta["youtube_video_id"]  = vid_id
            meta["youtube_video_url"] = f"https://www.youtube.com/watch?v={vid_id}"
        except Exception as e:
            print(f"  ❌ Upload failed: {e}")
    else:
        print(f"[YT-KIDS] Video not found: {video_path}")

    # Upload short
    short_path = get_short_path(meta)
    if short_path and Path(short_path).exists():
        ep_title   = ep_info["ep_title"]
        short_title= f"😱 {ep_title} — Kya Hua? | HerooQuest #Shorts #HindiKahani"[:100]
        short_desc = (
            f"😱 Kya hua Heroo ke saath? Full story dekho channel pe!\n"
            f"💡 Moral: {ep_info['moral']}\n\n"
            f"🤖 AI tools se banayi gayi animated kahani · Family-friendly\n\n"
            f"#HerooQuest #KidsShorts #HindiKahani #MoralStories #BachonKiKahani"
        )
        short_body = {
            "snippet": {
                "title":       short_title,
                "description": short_desc,
                "tags":        tags[:20] + ["Shorts", "KidsShorts", "HindiShorts"],
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
            print(f"  ✅ Short: https://youtube.com/shorts/{s_id}")
            upload_thumbnail(youtube, s_id, thumb_short)
        except Exception as e:
            print(f"  ❌ Short failed: {e}")

    # Save meta
    for mp in [OUT/f"kids_meta_{DATE_STR}_hi.json", OUT/f"kids_meta_{TODAY}.json"]:
        if mp.exists():
            try: mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            except: pass

    print("[YT-KIDS] Done ✅")


if __name__ == "__main__":
    main()
