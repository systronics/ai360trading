# generate_kids_video.py v2.1
# Memory-safe version for GitHub Actions free runner
# Uses Ken Burns zoom — real uploadable video, no crash
#
# v2.1 FIXES (May 2026):
# FIX 1 — Full story 1.8 min → 7+ min
#   6 scenes × 15 sec = 1.5 min (BROKEN)
#   10 scenes × 45 sec = 7.5 min (FIXED)
#   Changed: scenes 6→10, narration 4 sentences→8-10 sentences
# FIX 2 — Thumbnail with big text + Heroo visible
#   Added make_thumbnail() function using heroo.png
#   Thumbnail = first scene image + heroo.png overlay + big text
# FIX 3 — KIDS_OUTPUT support (full/short/didyouknow)
#   Added cliffhanger short and did you know outputs

import os, json, asyncio, time, re
from pathlib import Path
from datetime import date
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from ai_client import ai
from human_touch import ht, seo
from kids_content_calendar import get_today_topic

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market")
LANG         = os.environ.get("KIDS_LANG", "hi")
KIDS_OUTPUT  = os.environ.get("KIDS_OUTPUT", "full").lower()  # full | short | didyouknow
TODAY        = date.today().isoformat()
OUTPUT_DIR   = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

VOICES = {
    "hi": "hi-IN-SwaraNeural",
    "en": "en-US-JennyNeural",
}

# ── HEROO — Main character locked for every scene ────────────────────────
HEROO = (
    "Heroo — brave confident 10-year-old Indian boy, "
    "spiky jet-black hair, warm brown skin, big expressive brown eyes, "
    "bright red and blue superhero suit with golden H emblem on chest, "
    "golden flowing cape, always smiling or showing curiosity, "
    "always the main character centered in frame"
)

# ── 3D Pixar/Disney style prefix ────────────────────────────────────────
STYLE_3D = (
    "3D CGI animation render, Pixar and Disney quality, "
    "volumetric cinematic lighting, subsurface scattering skin, "
    "ray-traced shadows, photorealistic textures, depth of field, "
    "ultra-detailed background, vibrant saturated colors, "
    "child-friendly magical atmosphere, 16:9 cinematic wide shot"
)

# ── Arya — secondary character ───────────────────────────────────────────
ARYA = (
    "Arya — cheerful 8-year-old Indian girl, big curious brown eyes, "
    "dark hair in two braids with golden star clips, bright orange kurta"
)

SCENE_STYLE = f"{STYLE_3D}. Main character: {HEROO}. Supporting character: {ARYA}."

# ── TOPIC ────────────────────────────────────────────────────────────────
topic = get_today_topic()
print(f"[TOPIC] {topic['hindi_title']} / {topic['english_title']}")

# ── FONTS ────────────────────────────────────────────────────────────────
FONT_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
]
FONT_REG_PATHS = [
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


# ── HEROO PNG LOADER ─────────────────────────────────────────────────────
def load_heroo_png():
    """Load heroo.png with fallback chain."""
    candidates = [
        Path("public/image/heroo.png"),
        Path("public/image/heroo_happy.png"),
        Path("public/image/heroo_character.png"),
        Path("heroo.png"),
    ]
    for p in candidates:
        if p.exists():
            try:
                img = Image.open(str(p)).convert("RGBA")
                print(f"[HEROO] Loaded: {p}")
                return img
            except: continue
    print("[HEROO] ⚠️ No Heroo PNG found")
    return None


# ── v2.1 FIX 2: THUMBNAIL with big text + heroo.png ─────────────────────
def make_thumbnail(title_hi: str, title_en: str, scene_img_path: Path,
                   thumb_path: Path, heroo_img=None):
    """
    Proper thumbnail that drives CTR:
    - Bright colourful background
    - Heroo character visible (65% height)
    - Big bold yellow title text
    - Episode/brand badge

    YouTube thumbnail best practices:
    1. Face visible → Heroo character
    2. Large text → 100px+ bold yellow
    3. High contrast → dark bg + yellow text
    4. Clear topic → title text
    """
    W, H = 1280, 720
    accent = (255, 200, 0)   # bright yellow — best for kids thumbnails

    # Base: use scene image if available, else gradient
    if scene_img_path and scene_img_path.exists():
        try:
            base = Image.open(str(scene_img_path)).resize((W, H), Image.LANCZOS).convert("RGB")
            # Darken slightly for text contrast
            overlay = Image.new("RGBA", (W, H), (0, 0, 0, 100))
            base.paste(overlay, mask=overlay)
        except:
            base = Image.new("RGB", (W, H))
            px = base.load()
            for y in range(H):
                c = lerp((10, 20, 60), (30, 60, 130), y/H)
                for x in range(W): px[x, y] = c
    else:
        base = Image.new("RGB", (W, H))
        px = base.load()
        for y in range(H):
            c = lerp((10, 20, 60), (30, 60, 130), y/H)
            for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(base, "RGBA")

    # Accent bars
    draw.rectangle([(0, 0), (W, 12)], fill=accent)
    draw.rectangle([(0, H-12), (W, H)], fill=accent)

    # Heroo character — right side, 65% height
    if heroo_img is not None:
        try:
            hh = int(H * 0.72)
            hw = int(heroo_img.width * (hh / heroo_img.height))
            hr = heroo_img.resize((hw, hh), Image.LANCZOS)
            hx = W - hw - 10
            hy = H - hh
            base.paste(hr, (hx, hy), hr)
        except Exception as e:
            print(f"[THUMB] Heroo paste error: {e}")

    # Title text — left side, big yellow bold
    use_title = title_hi if LANG == "hi" else title_en
    safe_title = re.sub(r'[\u0900-\u097F]+', '', use_title).strip() or use_title[:15]

    import textwrap
    f_title = get_font(FONT_BOLD_PATHS, 90)
    f_sub   = get_font(FONT_BOLD_PATHS, 48)
    f_badge = get_font(FONT_REG_PATHS,  36)

    lines = textwrap.wrap(safe_title.upper(), width=14)
    ty = 80
    for line in lines[:2]:
        # Drop shadow
        for dx, dy in [(-3, 3), (3, -3), (-3, -3), (3, 3)]:
            draw.text((60+dx, ty+dy), line, font=f_title, fill=(0, 0, 0, 200), anchor="la")
        draw.text((60, ty), line, font=f_title, fill=accent, anchor="la")
        ty += 105

    # Subtitle
    if title_en and title_en != use_title:
        draw.text((60, ty), title_en[:30].upper(), font=f_sub,
                  fill=(255, 255, 255, 220), anchor="la")

    # HerooQuest badge — top left
    draw.rounded_rectangle([(20, 20), (260, 70)], radius=12, fill=(220, 30, 30))
    draw.text((140, 45), "HerooQuest ★", font=f_badge, fill=(255, 255, 255), anchor="mm")

    base.save(str(thumb_path), quality=95)
    print(f"[THUMB] ✅ Thumbnail saved: {thumb_path.name}")
    return thumb_path


# ── v2.1 FIX 1: SCRIPT GENERATION — 10 scenes × 45 sec each ────────────
def generate_script(topic: dict) -> dict:
    prompt = f"""
You are a master kids storyteller. Create a bilingual animated story starring Heroo.
Topic (Hindi): {topic['hindi_title']}
Topic (English): {topic['english_title']}
Category: {topic['category']}
Target: children 4-12 years

IMPORTANT: Heroo (brave 10-year-old Indian boy in red-blue superhero suit) is the
MAIN CHARACTER in every scene. He discovers, learns, and explains everything.
Arya (8-year-old Indian girl, orange kurta) is his curious friend.

Output ONLY valid JSON, no markdown, no extra text:
{{
  "title_hi": "Hindi title max 10 words",
  "title_en": "English title max 10 words",
  "scenes": [
    {{
      "id": 1,
      "narration_hi": "8-10 simple Hindi sentences spoken by Heroo. 40-50 seconds when read aloud. Engage children fully with excitement and emotion.",
      "narration_en": "8-10 simple English sentences spoken by Heroo. 40-50 seconds when read aloud. Engage children fully with excitement and emotion.",
      "image_prompt": "Describe exactly what Heroo and Arya are doing in this scene. Be specific about their poses, expressions, and the background environment.",
      "emotion": "excited"
    }}
  ],
  "moral_hi": "1 sentence Hindi moral from Heroo",
  "moral_en": "1 sentence English moral from Heroo",
  "seo_description_en": "60 word YouTube description with keywords mentioning Heroo"
}}
Create exactly 10 scenes. Build the story properly: introduce characters (2 scenes),
develop problem (2 scenes), adventure and challenge (4 scenes), resolution and moral (2 scenes).
Simple language for children. Each narration MUST be 8-10 sentences (40-50 seconds).
"""
    return ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")


def generate_cliffhanger_script(topic: dict) -> dict:
    """Short cliffhanger script — different from full story."""
    if LANG == "hi":
        prompt = f"""Write a 35-45 second cliffhanger YouTube Short script for kids.
Topic: {topic['hindi_title']}
Heroo discovers something amazing but do NOT reveal what happens next.
End with a suspense question to make kids watch the full video.
Return ONLY JSON:
{{"title_hi": "Heroo: [topic] 😱 Kya hua? | HerooQuest #Shorts",
  "title_en": "Heroo: [topic] 😱 What happened? | HerooQuest #Shorts",
  "narration_hi": "35-45 second Hinglish script — exciting, max 80 words, ends with question",
  "narration_en": "35-45 second English script — exciting, max 80 words, ends with question"}}"""
    else:
        prompt = f"""Write a 35-45 second cliffhanger YouTube Short for kids.
Topic: {topic['english_title']}
Heroo discovers something amazing but do NOT reveal what happens next.
Return ONLY JSON:
{{"title_hi": "Heroo Short | HerooQuest #Shorts",
  "title_en": "Heroo: {topic['english_title']} 😱 | HerooQuest #Shorts",
  "narration_hi": "short Hindi script",
  "narration_en": "35-45 second English script — exciting, max 80 words"}}"""

    data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang=LANG)
    if data and data.get("narration_hi"):
        return data
    return {
        "title_hi": f"Heroo: {topic['hindi_title']} 😱 | HerooQuest #Shorts",
        "title_en": f"Heroo: {topic['english_title']} 😱 | HerooQuest #Shorts",
        "narration_hi": "Doston! Heroo ke saath kuch aisa hua jo aapne socha bhi nahi hoga! Poori kahani dekhne ke liye full video dekho! Subscribe karo nayi kahaniyaan ke liye!",
        "narration_en": "Friends! Something incredible happened to Heroo today! Watch the full video to find out! Subscribe for more exciting stories!",
    }


def generate_did_you_know_script(topic: dict) -> dict:
    """Fun fact short — separate from story."""
    prompt = f"""Write a 20-30 second Did You Know YouTube Short for kids aged 6-10.
Topic theme: {topic['english_title']}
Pick ONE amazing animal or science fact related to the theme.
Return ONLY JSON:
{{"title_hi": "Kya Tum Jaante Ho? [Topic] 🤔 | HerooQuest #Shorts",
  "title_en": "Did You Know? [Topic] 🤔 | HerooQuest #Shorts",
  "fact_subject": "subject name",
  "narration_hi": "20-30 second Hinglish fact — simple, amazing, max 60 words",
  "narration_en": "20-30 second English fact — simple, amazing, max 60 words"}}"""

    data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang=LANG)
    if data and data.get("narration_hi"):
        return data
    return {
        "title_hi": "Kya Tum Jaante Ho? Octopus 🤔 | HerooQuest #Shorts",
        "title_en": "Did You Know? Octopus 🤔 | HerooQuest #Shorts",
        "fact_subject": "Octopus",
        "narration_hi": "Kya tum jaante ho? Octopus ke teen dil hote hain! Haan, teen! Aur uska khoon neela hota hai! Kitna amazing hai na? Like karo agar yeh nahi pata tha!",
        "narration_en": "Did you know? An octopus has THREE hearts! Yes, three! And its blood is blue! How amazing is that? Like this if you didn't know!",
    }


# ── IMAGE — 5-layer fallback chain (unchanged from original) ─────────────
def generate_scene_image(prompt: str, scene_id: int) -> Path:
    img_path = OUTPUT_DIR / f"kids_scene_{scene_id:02d}.png"
    if img_path.exists():
        print(f"  [CACHE] Scene {scene_id}")
        return img_path

    full_prompt = f"{SCENE_STYLE} Scene: {prompt}"

    # ── LAYER 1: Gemini 2.5 Flash Image (500 free/day) ───────────────────
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=full_prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                img_path.write_bytes(part.inline_data.data)
                img = Image.open(img_path).resize((1280, 720), Image.LANCZOS)
                img.save(img_path)
                print(f"  [IMG-1] Scene {scene_id} via Gemini 2.5 Flash Image ✓")
                return img_path
    except Exception as e:
        print(f"  [WARN-1] Gemini 2.5 Flash Image: {e}")

    time.sleep(3)

    # ── LAYER 2: Gemini 2.0 Flash Exp ────────────────────────────────────
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=full_prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                img_path.write_bytes(part.inline_data.data)
                img = Image.open(img_path).resize((1280, 720), Image.LANCZOS)
                img.save(img_path)
                print(f"  [IMG-2] Scene {scene_id} via Gemini 2.0 Flash Exp ✓")
                return img_path
    except Exception as e:
        print(f"  [WARN-2] Gemini 2.0 Flash Exp: {e}")

    time.sleep(3)

    # ── LAYER 3: Hugging Face FLUX.1 ─────────────────────────────────────
    try:
        hf_token = os.environ.get("HF_TOKEN")
        if hf_token:
            import requests as req
            headers = {"Authorization": f"Bearer {hf_token}"}
            payload = {"inputs": full_prompt[:500]}
            for hf_model in [
                "black-forest-labs/FLUX.1-schnell",
                "stabilityai/stable-diffusion-xl-base-1.0",
                "runwayml/stable-diffusion-v1-5",
            ]:
                try:
                    r = req.post(f"https://api-inference.huggingface.co/models/{hf_model}",
                                 headers=headers, json=payload, timeout=60)
                    if r.status_code == 200 and r.headers.get("content-type","").startswith("image"):
                        img_path.write_bytes(r.content)
                        img = Image.open(img_path).resize((1280, 720), Image.LANCZOS)
                        img.save(img_path)
                        print(f"  [IMG-3] Scene {scene_id} via HuggingFace ✓")
                        return img_path
                    elif r.status_code == 503:
                        time.sleep(5)
                except Exception as he:
                    print(f"  [HF] {hf_model}: {he}")
        else:
            print("  [SKIP-3] HF_TOKEN not set")
    except Exception as e:
        print(f"  [WARN-3] HuggingFace: {e}")

    time.sleep(2)

    # ── LAYER 4: DALL-E 3 ────────────────────────────────────────────────
    try:
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            from openai import OpenAI
            import urllib.request
            c = OpenAI(api_key=openai_key)
            r = c.images.generate(model="dall-e-3", prompt=full_prompt[:1000],
                                   size="1792x1024", quality="standard", n=1)
            urllib.request.urlretrieve(r.data[0].url, str(img_path))
            img = Image.open(img_path).resize((1280, 720), Image.LANCZOS)
            img.save(img_path)
            print(f"  [IMG-4] Scene {scene_id} via DALL-E 3 ✓")
            return img_path
    except Exception as e:
        print(f"  [WARN-4] DALL-E 3: {e}")

    # ── LAYER 5: Branded placeholder with Heroo ───────────────────────────
    colors = ["#1a1a2e","#16213e","#0f3460","#533483","#e94560","#2b2d42"]
    img  = Image.new("RGB", (1280, 720), color=colors[scene_id % len(colors)])
    draw = ImageDraw.Draw(img)
    draw.rectangle([10,10,1270,710], outline="#FFD700", width=5)
    draw.rectangle([20,20,1260,700], outline="#FF6B35", width=2)

    # Try to paste heroo.png on placeholder
    heroo = load_heroo_png()
    if heroo:
        try:
            hh = int(720 * 0.80)
            hw = int(heroo.width * (hh / heroo.height))
            hr = heroo.resize((hw, hh), Image.LANCZOS)
            img.paste(hr, (1280 - hw - 10, 720 - hh), hr)
        except: pass

    try:
        fb = get_font(FONT_BOLD_PATHS, 72)
        fm = get_font(FONT_BOLD_PATHS, 42)
        fs = get_font(FONT_REG_PATHS,  28)
    except:
        fb = fm = fs = ImageFont.load_default()

    draw.ellipse([560,220,700,360], fill="#FFD700", outline="#FF6B35", width=4)
    draw.text((630, 290), "H",          fill="#1a1a2e", anchor="mm", font=fb)
    draw.text((630, 420), f"Scene {scene_id}", fill="#FFD700", anchor="mm", font=fm)
    draw.text((630, 480), "HerooQuest", fill="#FF6B35", anchor="mm", font=fs)
    img.save(img_path)
    print(f"  [LAYER-5] Scene {scene_id} — placeholder")
    return img_path


# ── TTS ──────────────────────────────────────────────────────────────────
async def generate_tts_async(text: str, lang: str, out_path: Path):
    voice = VOICES.get(lang, VOICES["hi"])
    await edge_tts.Communicate(text, voice, rate="-10%").save(str(out_path))

def generate_tts(text: str, lang: str, out_path: Path):
    asyncio.run(generate_tts_async(text, lang, out_path))


# ── VIDEO (ffmpeg — unchanged from original) ──────────────────────────────
def make_video_ffmpeg(scenes: list, audio_paths: list, out_path: Path):
    import subprocess
    clip_paths = []
    for i, (scene_img, audio_path) in enumerate(zip(scenes, audio_paths)):
        clip_path = OUTPUT_DIR / f"clip_{i:02d}.mp4"
        probe = subprocess.run(
            ["ffprobe","-v","quiet","-show_entries","format=duration",
             "-of","csv=p=0", str(audio_path)],
            capture_output=True, text=True
        )
        duration = max(float(probe.stdout.strip() or "45"), 30.0)
        zoom_filter = (
            f"zoompan=z='if(lte(zoom,1.0),1.05,max(1.001,zoom-0.0015))':"
            f"d={int(duration*25)}:x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':s=1280x720:fps=25,scale=1280:720"
        )
        cmd = ["ffmpeg","-y","-loop","1","-i",str(scene_img),"-i",str(audio_path),
               "-vf",zoom_filter,"-c:v","libx264","-preset","ultrafast","-crf","28",
               "-c:a","aac","-b:a","128k","-t",str(duration+0.5),"-shortest",
               "-pix_fmt","yuv420p",str(clip_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [ERR] ffmpeg scene {i}: {result.stderr[-200:]}")
        else:
            print(f"  [CLIP] Scene {i} ✓  ({duration:.1f}s)")
            clip_paths.append(clip_path)

    if not clip_paths: raise RuntimeError("No clips generated")

    concat_file = OUTPUT_DIR / "concat.txt"
    concat_file.write_text("\n".join([f"file '{p.resolve()}'" for p in clip_paths]))
    cmd = ["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat_file),
           "-c:v","libx264","-preset","ultrafast","-crf","26","-c:a","aac",
           "-pix_fmt","yuv420p",str(out_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Concat failed: {result.stderr[-300:]}")
    print(f"[VIDEO] Full video: {out_path}")
    return out_path


def make_short_ffmpeg(video_path: Path, short_path: Path):
    import subprocess
    cmd = ["ffmpeg","-y","-i",str(video_path),"-t","60",
           "-vf","crop=405:720:437:0,scale=1080:1920",
           "-c:v","libx264","-preset","ultrafast","-crf","26","-c:a","aac",str(short_path)]
    subprocess.run(cmd, capture_output=True)
    print(f"[SHORT] YouTube Short: {short_path}")


def make_reel_ffmpeg(video_path: Path, reel_path: Path):
    import subprocess
    cmd = ["ffmpeg","-y","-i",str(video_path),"-t","90",
           "-vf","crop=405:720:437:0,scale=1080:1920",
           "-c:v","libx264","-preset","ultrafast","-crf","26",
           "-c:a","aac","-b:a","128k","-ar","44100",str(reel_path)]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode == 0: print(f"[REEL] Reel: {reel_path}")
    else: print(f"[REEL ERR] {result.stderr[-200:]}")


# ── YOUTUBE UPLOAD ────────────────────────────────────────────────────────
def upload_to_youtube(video_path: Path, title: str, description: str,
                      tags: list, is_short: bool = False, is_kids: bool = True):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS_KIDS")
        if not creds_json: print("❌ YOUTUBE_CREDENTIALS_KIDS not set"); return None
        creds   = Credentials.from_authorized_user_info(json.loads(creds_json))
        youtube = build("youtube", "v3", credentials=creds)
        body = {
            "snippet": {"title": title[:100], "description": description,
                        "tags": tags, "categoryId": "20"},
            "status":  {"privacyStatus": "public", "selfDeclaredMadeForKids": is_kids}
        }
        media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
        lbl   = "Short" if is_short else "Video"
        print(f"🚀 Uploading Kids {lbl}: {title[:60]}...")
        req   = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        resp  = None
        while resp is None:
            status, resp = req.next_chunk()
            if status: print(f"  {int(status.progress()*100)}%")
        vid_id = resp["id"]
        url = f"https://youtube.com/shorts/{vid_id}" if is_short else f"https://youtube.com/watch?v={vid_id}"
        print(f"✅ Uploaded: {url}")
        return vid_id
    except Exception as e:
        print(f"❌ Upload failed: {e}"); return None


# ── MAIN ─────────────────────────────────────────────────────────────────
def main():
    heroo_img = load_heroo_png()
    tags      = seo.get_video_tags(mode="weekend", is_short=False, channel="kids")
    yt_tags   = seo.get_youtube_safe_tags(tags)

    print(f"[KIDS_OUTPUT] {KIDS_OUTPUT}")

    # ── FULL STORY (10 scenes × 45 sec = ~7.5 min) ───────────────────────
    if KIDS_OUTPUT in ("full", ""):
        print("[SCRIPT] Generating story (10 scenes)...")
        script = generate_script(topic)
        script_path = OUTPUT_DIR / f"kids_script_{TODAY}.json"
        script_path.write_text(json.dumps(script, ensure_ascii=False, indent=2))
        print(f"[SCRIPT] Title EN: {script.get('title_en','')}")

        scenes      = script.get("scenes", [])
        img_paths   = []
        audio_paths = []

        for i, scene in enumerate(scenes):
            sid      = scene.get("id", i+1)
            narr     = scene.get(f"narration_{LANG}", scene.get("narration_hi",""))
            img_pr   = scene.get("image_prompt", f"Scene {sid}")

            print(f"[SCENE {sid}] Generating image + audio...")
            img_p    = generate_scene_image(img_pr, sid)
            audio_p  = OUTPUT_DIR / f"kids_audio_{sid:02d}.mp3"
            generate_tts(narr, LANG, audio_p)
            img_paths.append(img_p)
            audio_paths.append(audio_p)

        # v2.1 FIX 2: Proper thumbnail
        thumb_path = OUTPUT_DIR / f"kids_thumb_{TODAY}.png"
        make_thumbnail(
            script.get("title_hi",""), script.get("title_en",""),
            img_paths[0] if img_paths else None,
            thumb_path, heroo_img
        )

        title_hi = script.get("title_hi", topic["hindi_title"])
        title_en = script.get("title_en", topic["english_title"])
        vid_title = title_hi if LANG == "hi" else title_en
        moral_hi  = script.get("moral_hi", "")
        moral_en  = script.get("moral_en", "")
        desc = (
            f"HerooQuest — Heroo Ki Nayi Kahani!\n"
            f"{title_hi} / {title_en}\n"
            f"Aaj ki seekh: {moral_hi}\n\n"
            f"{script.get('seo_description_en','')}\n\n"
            f"Subscribe karo nayi kahaniyaan ke liye!\n"
            f"#HerooQuest #KidsStories #HindiKahani #ChildrenStories #Heroo"
        )

        out_video = OUTPUT_DIR / f"kids_full_{TODAY}.mp4"
        make_video_ffmpeg(img_paths, audio_paths, out_video)
        print(f"✅ Full video [HI]: {out_video.name}")

        vid_id = upload_to_youtube(out_video, vid_title, desc, yt_tags, False, True)
        print(f"✅ Uploaded: https://youtube.com/watch?v={vid_id}")

    # ── CLIFFHANGER SHORT ─────────────────────────────────────────────────
    elif KIDS_OUTPUT == "short":
        print("[SCRIPT] Generating cliffhanger short...")
        cliff   = generate_cliffhanger_script(topic)
        narr    = cliff.get(f"narration_{LANG}", cliff.get("narration_hi",""))
        title   = cliff.get(f"title_{LANG}", cliff.get("title_hi","HerooQuest #Shorts"))

        # Single placeholder image for short
        img_p   = generate_scene_image(f"Heroo looking shocked and surprised at something amazing. {topic['english_title']}", 0)
        audio_p = OUTPUT_DIR / f"kids_short_audio_{TODAY}.mp3"
        generate_tts(narr, LANG, audio_p)

        # Thumbnail for short
        thumb_path = OUTPUT_DIR / f"kids_short_thumb_{TODAY}.png"
        make_thumbnail(cliff.get("title_hi",""), cliff.get("title_en",""),
                       img_p, thumb_path, heroo_img)

        out_short = OUTPUT_DIR / f"kids_short_{TODAY}.mp4"
        import subprocess
        probe = subprocess.run(
            ["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0",str(audio_p)],
            capture_output=True, text=True
        )
        duration = max(float(probe.stdout.strip() or "40"), 35.0)
        cmd = ["ffmpeg","-y","-loop","1","-i",str(img_p),"-i",str(audio_p),
               "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
               "-c:v","libx264","-preset","ultrafast","-crf","26",
               "-c:a","aac","-t",str(duration+0.5),"-shortest","-pix_fmt","yuv420p",str(out_short)]
        subprocess.run(cmd, capture_output=True)
        print(f"✅ Cliffhanger Short: {out_short.name} | {duration:.1f}s")

        vid_id = upload_to_youtube(out_short, title, f"HerooQuest Short! {topic['english_title']}\nWatch full episode on channel!\n#HerooQuest #KidsShorts", yt_tags, True, True)
        print(f"✅ Uploaded: https://youtube.com/shorts/{vid_id}")

    # ── DID YOU KNOW ──────────────────────────────────────────────────────
    elif KIDS_OUTPUT == "didyouknow":
        print("[SCRIPT] Generating Did You Know...")
        dyk     = generate_did_you_know_script(topic)
        narr    = dyk.get(f"narration_{LANG}", dyk.get("narration_hi",""))
        title   = dyk.get(f"title_{LANG}", dyk.get("title_hi","HerooQuest #Shorts"))
        subject = dyk.get("fact_subject","Nature")

        img_p   = generate_scene_image(f"Heroo looking amazed and excited about {subject}. Child-friendly educational scene.", 99)
        audio_p = OUTPUT_DIR / f"kids_dyk_audio_{TODAY}.mp3"
        generate_tts(narr, LANG, audio_p)

        thumb_path = OUTPUT_DIR / f"kids_dyk_thumb_{TODAY}.png"
        make_thumbnail(dyk.get("title_hi",""), dyk.get("title_en",""),
                       img_p, thumb_path, heroo_img)

        out_dyk = OUTPUT_DIR / f"kids_dyk_{TODAY}.mp4"
        import subprocess
        probe = subprocess.run(
            ["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0",str(audio_p)],
            capture_output=True, text=True
        )
        duration = max(float(probe.stdout.strip() or "25"), 15.0)
        cmd = ["ffmpeg","-y","-loop","1","-i",str(img_p),"-i",str(audio_p),
               "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
               "-c:v","libx264","-preset","ultrafast","-crf","26",
               "-c:a","aac","-t",str(duration+0.5),"-shortest","-pix_fmt","yuv420p",str(out_dyk)]
        subprocess.run(cmd, capture_output=True)
        print(f"✅ Did You Know Short: {out_dyk.name} | {duration:.1f}s")

        vid_id = upload_to_youtube(out_dyk, title, f"HerooQuest Did You Know! {subject}\nSubscribe for daily facts!\n#HerooQuest #DidYouKnow #KidsFacts", yt_tags, True, True)
        print(f"✅ Uploaded: https://youtube.com/shorts/{vid_id}")

    print("\n✅ HEROOQUEST DONE")
    print(f"   Topic: {topic['hindi_title']} / {topic['english_title']}")
    print(f"   Lang:  {LANG.upper()} | Output: {KIDS_OUTPUT.upper()}")


if __name__ == "__main__":
    main()
