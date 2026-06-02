"""
generate_kids_video.py — HerooQuest v2.8
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v2.8 (2026-06-02) — EDGE-TTS 503 RETRY (self-heal in-run):
    edge_tts (wss://speech.platform.bing.com) intermittently returns 503 /
    WSServerHandshakeError, which killed the whole kids-english-full job
    (run 26784484850 attempt 1; auto-heal re-ran it an hour later). generate_tts_async
    now retries up to 4x with 5/15/30s backoff and verifies non-empty audio,
    so a transient TTS blip no longer needs a full workflow re-run.

v2.7 (2026-05-31) — SPOKEN LIKE/SHARE/SUBSCRIBE CTA:
    The last scene's narration now ends with a warm, kid-friendly spoken
    like/share/subscribe line (KIDS_CTA, hi/en), voiced in the same soft kids
    voice. Because it's part of the narration, the auto-translate .srt caption
    follows it automatically. Drives subscribers/engagement on the kids channel.

v2.6 (2026-05-31) — AUTO-TRANSLATE SUBTITLES (global reach, ₹0):
    The kids video already declared defaultAudioLanguage, but had NO exact
    caption track — so YouTube only had its own machine captions to translate.
    Now `_build_kids_subtitles()` writes a per-scene .srt timed to the final
    xfade timeline (Σ max(audio,30) − i×0.5 per scene), stored as meta
    "subtitle_srt"; upload_kids_youtube.py uploads it after the video. This
    lets YouTube auto-translate our EXACT captions into the viewer's language
    (US/UK/Brazil/India). FULLY FAIL-OPEN — never blocks the render or upload.
    NOTE: the caption upload needs the youtube.force-ssl scope on the kids
    token; without it the uploader logs a re-auth hint and skips (fail-open),
    while defaultAudioLanguage still gives YouTube auto-captions.

v2.5 (2026-05-31) — IMAGE FIX ("only one image / not related to story"):
    ROOT CAUSE (from run logs): images were NOT placeholders — Pollinations
    succeeded every scene — but `full_prompt = "{SCENE_STYLE} Scene: {prompt}"`
    put the ~870-char fixed style/character prefix FIRST, longer than the
    800-char Pollinations limit, so the scene-specific part was truncated off
    → all 10 images near-identical / off-topic.
    FIX 1: lead with the scene action → `"{prompt}. Main character:{HEROO}.{STYLE_3D}"`
           + raised Pollinations truncation 800 → 1000.
    FIX 2: ADD Layer 0 = Cloudflare Workers AI FLUX.1-schnell (FREE, reliable
           API) tried first; activates when CLOUDFLARE_ACCOUNT_ID +
           CLOUDFLARE_API_TOKEN secrets exist.
    FIX 3: Gemini model name `gemini-2.5-flash-preview-image` (404 every call)
           → `gemini-2.5-flash-image-preview`.

v2.4 (2026-05-31) — NOT-SCARY FIX (kids were frightened by the thumbnails):
  The old output looked dark, red and ominous. Three causes fixed:
    1. STYLE_3D prompt dropped "octane/volumetric/rim/ray-traced/photorealistic"
       (dark dramatic uncanny lighting) → now BRIGHT soft cartoon + explicit
       "NOT scary, no dark/ominous, no creepy faces, daytime".
    2. enhance_image_cinematic() removed the dark edge VIGNETTE + warm-RED
       channel push, and raised brightness → bright cheerful frames.
       make_video_ffmpeg_cinematic() likewise dropped its ffmpeg vignette and
       flipped brightness -0.02 → +0.05 (the video re-darkened every frame).
    3. make_thumbnail_multitext() dark overlay 155 → 80 so the bright happy
       scene shows through (title/moral text still readable via shadows).
  NOTE: only affects NEWLY generated videos; already-uploaded thumbnails are
  unchanged (would need re-upload / Studio thumbnail swap).

v2.3 CHANGES (May 2026) — CINEMATIC VIDEO EFFECTS:

The key insight:
  3D Pixar-style IMAGE + cinematic ffmpeg effects = looks like 3D VIDEO
  Top Indian kids channels use this exact technique
  Viewers cannot tell the difference between animated video and
  a well-produced cinematic slideshow with the right effects

CINEMATIC EFFECTS ADDED (ffmpeg + PIL):
  1. Ken Burns zoom — slow zoom in/out on each scene (already working)
  2. Scene transitions — xfade: fade/dissolve/wipeleft between scenes
  3. Color grading — warm cinematic look (brightness, contrast, saturation)
  4. Vignette — dark edges = cinema feel
  5. Sharpness boost — makes Pixar images crisp and vibrant
  6. Dynamic zoom direction — alternate zoom-in/zoom-out each scene
  7. Pan movement — slow horizontal drift adds depth
  8. Fade in/out — smooth entry and exit on each scene

IMAGE QUALITY IMPROVED:
  Layer 1: Gemini 2.5 (when quota available)
  Layer 2: Pollinations.ai flux-pro (FREE, Pixar quality, always works)
  Layer 3: HuggingFace FLUX.1-schnell
  Layer 4: DALL-E 2
  Layer 5: PIL placeholder with Heroo character

THUMBNAIL IMPROVED:
  Full dramatic scene as background
  Multi-text format (like competitor thumbnails that get clicks)
  Story title + moral + episode badge + character visible

META DATE FORMAT FIXED:
  date.today().strftime("%Y%m%d") — matches upload_kids_youtube.py
"""

import os
import json
import asyncio
import time
import urllib.parse
import urllib.request
import subprocess
from pathlib import Path
from datetime import date

import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from ai_client import ai
from human_touch import ht, seo
from kids_content_calendar import get_today_topic

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market")
LANG         = os.environ.get("KIDS_LANG", "hi")
KIDS_OUTPUT  = os.environ.get("KIDS_OUTPUT", "full").lower()

# v2.2 FIX: Unified date format
TODAY     = date.today().strftime("%Y%m%d")
TODAY_ISO = date.today().isoformat()

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

VOICES = {
    "hi": "hi-IN-SwaraNeural",
    "en": "en-US-JennyNeural",
}

# v2.7: warm, kid-friendly spoken outro (like/share/subscribe) added to the last
# scene's narration so it's voiced in the same soft kids voice + caption follows.
KIDS_CTA = {
    "hi": (" Dosto, agar aapko Heroo ki yeh kahani achhi lagi toh, "
           "please LIKE karo, apne doston ke saath SHARE karo, aur humara "
           "channel SUBSCRIBE karna mat bhoolna! Milte hain agli kahani mein!"),
    "en": (" Friends, if you loved Heroo's story, please give it a big LIKE, "
           "SHARE it with your friends, and don't forget to SUBSCRIBE to our "
           "channel! See you in the next story!"),
}

# ── HEROO + ARYA descriptions ─────────────────────────────────────────────────
HEROO = (
    "Heroo — brave confident 10-year-old Indian boy, "
    "spiky jet-black hair, warm brown skin, big expressive brown eyes, "
    "bright red and blue superhero suit with golden H emblem on chest, "
    "golden flowing cape, always smiling or showing curiosity, "
    "always the main character centered in frame"
)
ARYA = (
    "Arya — cheerful 8-year-old Indian girl, big curious brown eyes, "
    "dark hair in two braids with golden star clips, bright orange kurta"
)

# Kid-friendly 3D prompt prefix.
# IMPORTANT: kids were scared by the old output. The previous prompt used
# "octane volumetric cinematic lighting / rim lighting / ray-traced shadows /
# photorealistic" which produced dark, dramatic, uncanny faces. This version
# forces BRIGHT, soft, cheerful, cartoon lighting and explicitly bans scary,
# dark or ominous moods.
STYLE_3D = (
    "cute 3D cartoon animation, Pixar Disney Dreamworks quality, "
    "inspired by Encanto Moana Bluey Coco animation style, "
    "BRIGHT even daylight, soft cheerful lighting, no harsh shadows, "
    "rounded friendly character design, big happy smiles, "
    "warm friendly Indian skin tones, colourful storybook background, "
    "vibrant candy-bright saturated colours, wholesome joyful child-friendly mood, "
    "NOT scary, no dark or ominous atmosphere, no horror, no creepy faces, daytime, "
    "16:9 wide shot, high resolution, professional animation studio quality"
)

SCENE_STYLE = f"{STYLE_3D}. Main character: {HEROO}. Supporting character: {ARYA}."

topic = get_today_topic()
print(f"[TOPIC] {topic['hindi_title']} / {topic['english_title']}")


# ── SCRIPT GENERATION ─────────────────────────────────────────────────────────

def generate_script(topic: dict) -> dict:
    prompt = f"""
You are a master kids storyteller. Create a bilingual animated story starring Heroo.
Topic (Hindi): {topic['hindi_title']}
Topic (English): {topic['english_title']}
Category: {topic['category']}
Target: children 4-12 years

IMPORTANT: Heroo is the MAIN CHARACTER in every scene.
Arya is his curious friend.

Output ONLY valid JSON, no markdown:
{{
  "title_hi": "Hindi title max 10 words",
  "title_en": "English title max 10 words",
  "scenes": [
    {{
      "id": 1,
      "narration_hi": "8-10 simple Hindi sentences spoken by Heroo. 40-50 seconds when read aloud.",
      "narration_en": "8-10 simple English sentences spoken by Heroo. 40-50 seconds when read aloud.",
      "image_prompt": "Specific visual: what Heroo and Arya are doing, their exact poses and expressions, detailed magical background. Very specific for AI image generation.",
      "emotion": "excited",
      "transition": "fade"
    }}
  ],
  "moral_hi": "1 sentence Hindi moral from Heroo",
  "moral_en": "1 sentence English moral from Heroo",
  "seo_description_en": "60 word YouTube description with keywords mentioning Heroo"
}}
Create exactly 10 scenes. Build: introduce (2), develop (2), adventure (4), moral (2).
Each narration 8-10 sentences = 40-50 seconds = ~7.5 min total.
"""
    return ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")


# ── IMAGE GENERATION — 5 LAYER FALLBACK CHAIN ────────────────────────────────

def generate_scene_image(prompt: str, scene_id: int) -> Path:
    img_path = OUTPUT_DIR / f"kids_scene_{scene_id:02d}.png"
    if img_path.exists():
        print(f"  [CACHE] Scene {scene_id}")
        return img_path

    # Lead with the SCENE-SPECIFIC action so every image is DISTINCT and ON-topic.
    # (Bug: the fixed SCENE_STYLE prefix is ~870 chars — longer than the 800-char
    #  Pollinations limit — so the scene part was truncated off and all 10 images
    #  came out near-identical / unrelated to the story. Scene first fixes it.)
    full_prompt = f"{prompt}. Main character: {HEROO}. {STYLE_3D}"

    # Layer 0: Cloudflare Workers AI — FLUX.1-schnell (FREE, reliable, automatable)
    # Activates automatically once CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN
    # secrets are set. ~ free daily quota; returns JSON with base64 image.
    try:
        cf_account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
        cf_token   = os.environ.get("CLOUDFLARE_API_TOKEN", "")
        if cf_account and cf_token:
            import requests as req, base64
            cf_url = (f"https://api.cloudflare.com/client/v4/accounts/{cf_account}"
                      f"/ai/run/@cf/black-forest-labs/flux-1-schnell")
            r = req.post(cf_url,
                         headers={"Authorization": f"Bearer {cf_token}"},
                         json={"prompt": full_prompt[:2048], "steps": 8},
                         timeout=90)
            if r.status_code == 200:
                b64 = ((r.json().get("result") or {}).get("image", "")) or ""
                if b64:
                    img_path.write_bytes(base64.b64decode(b64))
                    Image.open(img_path).convert("RGB").resize((1280, 720), Image.LANCZOS).save(img_path, quality=95)
                    print(f"  [IMG-0] Scene {scene_id} via Cloudflare FLUX ✓")
                    return img_path
                print(f"  [WARN-0] Cloudflare: 200 but no image in response")
            else:
                print(f"  [WARN-0] Cloudflare {r.status_code}: {r.text[:120]}")
    except Exception as e:
        print(f"  [WARN-0] Cloudflare: {str(e)[:80]}")

    # Layer 1: Gemini 2.5 Flash Image
    try:
        from google import genai
        from google.genai import types
        client   = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=full_prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE","TEXT"])
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                img_path.write_bytes(part.inline_data.data)
                Image.open(img_path).resize((1280,720),Image.LANCZOS).save(img_path)
                print(f"  [IMG-1] Scene {scene_id} via Gemini 2.5 ✓")
                return img_path
    except Exception as e:
        print(f"  [WARN-1] Gemini 2.5: {str(e)[:80]}")

    time.sleep(2)

    # Layer 2: Pollinations.ai FLUX Pro (FREE — no API key)
    try:
        import requests as req
        clean    = full_prompt.replace('"','').replace("'",'')[:1000]
        encoded  = urllib.parse.quote(clean)
        for model in ["flux-pro", "flux", "flux-realism"]:
            try:
                url = (f"https://image.pollinations.ai/prompt/{encoded}"
                       f"?model={model}&width=1280&height=720"
                       f"&seed={scene_id*42}&nologo=true&enhance=true")
                r   = req.get(url, timeout=60, stream=True)
                ct  = r.headers.get("content-type","")
                if r.status_code == 200 and (
                    "image" in ct or
                    r.content[:4] in [b'\xff\xd8\xff\xe0',b'\xff\xd8\xff\xe1',b'\x89PNG']
                ):
                    img_path.write_bytes(r.content)
                    img = Image.open(img_path).convert("RGB").resize((1280,720),Image.LANCZOS)
                    img.save(img_path, quality=95)
                    print(f"  [IMG-2] Scene {scene_id} via Pollinations ({model}) ✓")
                    return img_path
            except Exception as pe:
                print(f"  [POLL] {model}: {pe}")
            time.sleep(3)
    except Exception as e:
        print(f"  [WARN-2] Pollinations: {e}")

    time.sleep(2)

    # Layer 3: HuggingFace FLUX.1-schnell
    try:
        hf_token = os.environ.get("HF_TOKEN")
        if hf_token:
            import requests as req
            headers = {"Authorization": f"Bearer {hf_token}"}
            payload = {"inputs": f"3D Pixar Disney animation style, {full_prompt[:400]}, vibrant colors, cinematic lighting",
                       "parameters": {"guidance_scale": 7.5, "num_inference_steps": 30, "width": 1280, "height": 720}}
            for hf_model in ["black-forest-labs/FLUX.1-schnell",
                              "stabilityai/stable-diffusion-xl-base-1.0",
                              "runwayml/stable-diffusion-v1-5"]:
                try:
                    r = req.post(f"https://api-inference.huggingface.co/models/{hf_model}",
                                 headers=headers, json=payload, timeout=90)
                    if r.status_code == 200 and "image" in r.headers.get("content-type",""):
                        img_path.write_bytes(r.content)
                        Image.open(img_path).convert("RGB").resize((1280,720),Image.LANCZOS).save(img_path,quality=95)
                        print(f"  [IMG-3] Scene {scene_id} via HuggingFace ✓")
                        return img_path
                    elif r.status_code == 503:
                        time.sleep(15)
                        r2 = req.post(f"https://api-inference.huggingface.co/models/{hf_model}",
                                      headers=headers, json=payload, timeout=90)
                        if r2.status_code == 200 and "image" in r2.headers.get("content-type",""):
                            img_path.write_bytes(r2.content)
                            Image.open(img_path).convert("RGB").resize((1280,720),Image.LANCZOS).save(img_path,quality=95)
                            print(f"  [IMG-3] Scene {scene_id} via HuggingFace (retry) ✓")
                            return img_path
                except Exception as he:
                    print(f"  [HF] {hf_model}: {he}")
    except Exception as e:
        print(f"  [WARN-3] HuggingFace: {e}")

    time.sleep(2)

    # Layer 4: DALL-E 2 (PAID) — gated behind ALLOW_PAID_AI for the ₹0 invariant.
    # Off by default → cascade skips straight to the free PIL placeholder (Layer 5).
    try:
        openai_key = os.environ.get("OPENAI_API_KEY")
        _allow_paid = os.environ.get("ALLOW_PAID_AI", "").strip().lower() in ("1", "true", "yes", "on")
        if openai_key and _allow_paid:
            from openai import OpenAI
            client_oai = OpenAI(api_key=openai_key)
            dalle_prompt = f"3D Pixar animation. {HEROO}. {prompt[:200]}. Vibrant colors, child-friendly."[:1000]
            response     = client_oai.images.generate(model="dall-e-2", prompt=dalle_prompt,
                                                       size="1024x1024", quality="standard", n=1)
            urllib.request.urlretrieve(response.data[0].url, str(img_path))
            Image.open(img_path).convert("RGB").resize((1280,720),Image.LANCZOS).save(img_path,quality=95)
            print(f"  [IMG-4] Scene {scene_id} via DALL-E 2 ✓")
            return img_path
    except Exception as e:
        print(f"  [WARN-4] DALL-E 2: {e}")

    # Layer 5: PIL placeholder with Heroo
    colors = ["#1a1a2e","#16213e","#0f3460","#533483","#e94560",
              "#2b2d42","#1b4332","#023e8a","#7b2d8b","#b5451b"]
    img    = Image.new("RGB", (1280,720), color=colors[scene_id % len(colors)])
    draw   = ImageDraw.Draw(img)
    draw.rectangle([10,10,1270,710], outline="#FFD700", width=5)
    heroo_path = Path("public/image/heroo.png")
    if heroo_path.exists():
        try:
            heroo = Image.open(str(heroo_path)).convert("RGBA")
            hh    = int(720*0.85); hw = int(heroo.width*(hh/heroo.height))
            heroo = heroo.resize((hw,hh),Image.LANCZOS)
            img.paste(heroo,(1280-hw-10,720-hh),heroo)
        except: pass
    try:
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",72)
        fm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",42)
    except:
        fb = fm = ImageFont.load_default()
    draw.ellipse([560,240,700,360],fill="#FFD700",outline="#FF6B35",width=4)
    draw.text((630,300),"H",fill="#1a1a2e",anchor="mm",font=fb)
    draw.text((640,420),f"Scene {scene_id}",fill="#FFD700",anchor="mm",font=fm)
    img.save(img_path)
    print(f"  [LAYER-5] Scene {scene_id} — placeholder")
    return img_path


# ── v2.3 NEW: CINEMATIC IMAGE ENHANCEMENT ────────────────────────────────────

def enhance_image_cinematic(img_path: Path) -> Path:
    """
    Apply cinematic color grading and effects to any image.
    Makes Pixar-style images look more professional and filmic.

    KID-FRIENDLY grade (was making faces dark/red/scary before):
    1. Gentle contrast — pops without going harsh
    2. Saturation boost — vibrant candy-bright colours
    3. Brightness up — bright and cheerful
    4. Light sharpness — crisp but soft
    (No warm-red push, no dark vignette — those caused the scary look.)

    Works on placeholder images too — even PIL placeholders look better.
    """
    try:
        enhanced_path = OUTPUT_DIR / f"enhanced_{img_path.name}"
        img = Image.open(img_path).convert("RGB")

        # KID-FRIENDLY grade — bright, vibrant, NO dark vignette, NO red push.
        # (The old dark edge vignette + warm-red channel push made the faces
        #  look dark, red and ominous — kids were scared by it.)
        # 1. Gentle contrast (soft, not harsh)
        img = ImageEnhance.Contrast(img).enhance(1.10)
        # 2. Saturation boost — fun, candy-bright colours
        img = ImageEnhance.Color(img).enhance(1.40)
        # 3. Brightness UP — bright and cheerful
        img = ImageEnhance.Brightness(img).enhance(1.18)
        # 4. Light sharpness
        img = ImageEnhance.Sharpness(img).enhance(1.25)
        # (Removed: warm-red channel push + dark vignette — both made the
        #  kids content look dark/red/scary.)

        img.save(str(enhanced_path), quality=95)
        return enhanced_path

    except Exception as e:
        print(f"  [ENHANCE] Enhancement failed: {e} — using original")
        return img_path


# ── v2.6 NEW: AUTO-TRANSLATE SUBTITLE TRACK ──────────────────────────────────

def _build_kids_subtitles(narrations: list, audio_paths: list, lang: str):
    """
    Build a per-scene .srt synced to the FINAL xfade-concatenated timeline so
    YouTube can auto-translate the kids captions into the viewer's language.

    Mirrors the timing model of make_video_ffmpeg_cinematic + _concat_with_xfade:
      • each scene clip is held for its narration length (ffmpeg -shortest), and
        _concat_with_xfade uses max(clip, 30)s as its offset unit;
      • neighbouring clips overlap by trans_dur = 0.5s.
    So scene i starts at  Σ_{k<i} max(audio_dur_k, 30) − i×0.5, and its caption
    spans that scene's own narration audio length.

    FULLY FAIL-OPEN → returns the .srt path, or None on any problem (no caption).
    """
    try:
        from subtitle_helper import build_srt_segments
        TRANS, MIN_CLIP = 0.5, 30.0

        audio_durs = []
        for ap in audio_paths:
            try:
                probe = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                     "-of", "csv=p=0", str(ap)],
                    capture_output=True, text=True)
                audio_durs.append(float((probe.stdout or "").strip() or "0"))
            except Exception:
                audio_durs.append(0.0)

        # offset unit per scene = exactly what _concat_with_xfade probes
        clip_units = [max(d, MIN_CLIP) for d in audio_durs]

        segments, start = [], 0.0
        for i, narr in enumerate(narrations):
            if i > 0:
                start += clip_units[i - 1] - TRANS
            window = audio_durs[i] if audio_durs[i] > 0 else clip_units[i]
            if narr and narr.strip():
                segments.append((narr, start, window))

        if not segments:
            return None
        out = OUTPUT_DIR / f"kids_subs_{TODAY}_{lang}.srt"
        srt = build_srt_segments(segments, out)
        if srt:
            print(f"  [SUBS] Caption track built ({lang}, {len(segments)} scenes) → {Path(srt).name}")
        return srt
    except Exception as e:
        print(f"  ⚠️ kids subtitle build skipped (fail-open): {e}")
        return None


# ── v2.3 NEW: CINEMATIC VIDEO GENERATION ─────────────────────────────────────

def make_video_ffmpeg_cinematic(
    scenes: list,
    audio_paths: list,
    out_path: Path,
    apply_transitions: bool = True
):
    """
    Generate cinematic video from images using ffmpeg.

    Effects per scene:
      1. Ken Burns zoom — alternating zoom-in/zoom-out + pan direction
      2. Color correction — contrast, saturation, warmth
      3. Vignette filter — cinema dark edges
      4. Sharpness — crisp and vibrant

    Transitions between scenes:
      xfade filter: fade, dissolve, wipeleft, wiperight, slideup
      Alternates between transition types for visual variety

    This combination makes static Pixar images look like
    actual animated video — indistinguishable to most viewers.
    """
    clip_paths  = []
    transitions = ["fade", "dissolve", "wipeleft", "wiperight", "slideup", "slidedown"]

    for i, (scene_img, audio_path) in enumerate(zip(scenes, audio_paths)):
        clip_path = OUTPUT_DIR / f"clip_{i:02d}.mp4"

        # Get audio duration
        probe = subprocess.run(
            ["ffprobe","-v","quiet","-show_entries","format=duration",
             "-of","csv=p=0", str(audio_path)],
            capture_output=True, text=True
        )
        duration = max(float(probe.stdout.strip() or "30"), 30.0)

        # Alternate zoom direction for visual variety
        # Even scenes: zoom in (1.0 → 1.06)
        # Odd scenes: zoom out (1.06 → 1.0) + slight pan
        if i % 4 == 0:
            # Zoom in — classic Ken Burns
            zoom_expr = "if(lte(zoom,1.0),1.0,max(1.001,zoom-0.0012))"
            x_expr    = "iw/2-(iw/zoom/2)"
            y_expr    = "ih/2-(ih/zoom/2)"
        elif i % 4 == 1:
            # Zoom out — reverse Ken Burns
            zoom_expr = "if(gte(zoom,1.06),1.06,min(1.059,zoom+0.0012))"
            x_expr    = "iw/2-(iw/zoom/2)"
            y_expr    = "ih/2-(ih/zoom/2)"
        elif i % 4 == 2:
            # Zoom in + pan left to right
            zoom_expr = "if(lte(zoom,1.0),1.04,max(1.001,zoom-0.001))"
            x_expr    = "if(lte(on,1),iw/2-(iw/zoom/2),x+1)"
            y_expr    = "ih/2-(ih/zoom/2)"
        else:
            # Zoom in + pan right to left
            zoom_expr = "if(lte(zoom,1.0),1.04,max(1.001,zoom-0.001))"
            x_expr    = "if(lte(on,1),iw/2-(iw/zoom/2),max(0,x-1))"
            y_expr    = "ih/2-(ih/zoom/2)"

        # KID-FRIENDLY colour: brighten slightly (was brightness=-0.02 darken)
        # and DROP the dark vignette — "cinema dark edges" made the kids content
        # look gloomy/scary. Keep vivid saturation for fun, friendly colours.
        color_filter = "eq=contrast=1.06:brightness=0.05:saturation=1.30:gamma=1.02"

        # Sharpness (gentle)
        sharpen_filter = "unsharp=5:5:0.6:3:3:0.3"

        # Combine zoom + colour + sharpness (NO vignette)
        zoom_filter = (
            f"zoompan=z='{zoom_expr}':d={int(duration*25)}"
            f":x='{x_expr}':y='{y_expr}':s=1280x720:fps=25"
            f",scale=1280:720"
            f",{color_filter}"
            f",{sharpen_filter}"
        )

        # Fade in (0.5s) and fade out (0.5s) on each clip
        fade_filter = f",fade=t=in:st=0:d=0.5,fade=t=out:st={duration-0.5:.1f}:d=0.5"
        full_filter = zoom_filter + fade_filter

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(scene_img),
            "-i", str(audio_path),
            "-vf", full_filter,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
            "-c:a", "aac", "-b:a", "128k",
            "-t", str(duration + 0.5),
            "-shortest", "-pix_fmt", "yuv420p",
            str(clip_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [ERR] ffmpeg scene {i}: {result.stderr[-200:]}")
        else:
            print(f"  [CLIP] Scene {i} ✓ ({duration:.1f}s) — cinematic effects applied")
            clip_paths.append(clip_path)

    if not clip_paths:
        raise RuntimeError("No clips generated")

    # Concatenate with XFADE transitions (smooth cinematic transitions)
    if apply_transitions and len(clip_paths) > 1:
        print("[VIDEO] Applying cinematic transitions between scenes...")
        result = _concat_with_xfade(clip_paths, out_path, transitions)
        if not result:
            # Fallback to simple concat
            _simple_concat(clip_paths, out_path)
    else:
        _simple_concat(clip_paths, out_path)

    print(f"[VIDEO] Cinematic video ready: {out_path}")
    return out_path


def _concat_with_xfade(clip_paths: list, out_path: Path, transitions: list) -> bool:
    """
    Concatenate clips with smooth xfade transitions.
    xfade makes cuts look like animated transitions — very professional.
    Alternates: fade → dissolve → wipeleft → wiperight → repeat
    """
    try:
        if len(clip_paths) < 2:
            return False

        # Get durations of all clips
        durations = []
        for cp in clip_paths:
            probe = subprocess.run(
                ["ffprobe","-v","quiet","-show_entries","format=duration",
                 "-of","csv=p=0", str(cp)],
                capture_output=True, text=True
            )
            d = max(float(probe.stdout.strip() or "30"), 30.0)
            durations.append(d)

        # Build complex filter for xfade chain
        # Each transition is 0.5 seconds
        trans_dur = 0.5
        inputs    = []
        for cp in clip_paths:
            inputs.extend(["-i", str(cp)])

        # Build xfade filter chain
        filter_complex = ""
        current_label  = "[0:v]"
        current_audio  = "[0:a]"
        offset         = 0.0

        for i in range(1, len(clip_paths)):
            trans_type   = transitions[(i-1) % len(transitions)]
            offset      += durations[i-1] - trans_dur
            next_v_label = f"[v{i}]" if i < len(clip_paths)-1 else "[outv]"
            next_a_label = f"[a{i}]" if i < len(clip_paths)-1 else "[outa]"

            filter_complex += (
                f"{current_label}[{i}:v]xfade=transition={trans_type}"
                f":duration={trans_dur}:offset={offset:.2f}{next_v_label};"
            )
            filter_complex += (
                f"{current_audio}[{i}:a]acrossfade=d={trans_dur}{next_a_label};"
            )
            current_label = next_v_label
            current_audio = next_a_label

        # Remove trailing semicolons
        filter_complex = filter_complex.rstrip(";")

        cmd = (
            ["ffmpeg", "-y"] + inputs +
            ["-filter_complex", filter_complex,
             "-map", "[outv]", "-map", "[outa]",
             "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
             "-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p",
             str(out_path)]
        )

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"  [XFADE] Cinematic transitions applied ✓")
            return True
        else:
            print(f"  [XFADE] Failed: {result.stderr[-200:]} — using simple concat")
            return False

    except Exception as e:
        print(f"  [XFADE] Error: {e} — fallback to simple concat")
        return False


def _simple_concat(clip_paths: list, out_path: Path):
    """Simple concatenation fallback."""
    concat_file = OUTPUT_DIR / "concat.txt"
    concat_file.write_text("\n".join([f"file '{p.resolve()}'" for p in clip_paths]))
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-c:a", "aac", "-pix_fmt", "yuv420p", str(out_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Concat failed: {result.stderr[-300:]}")


# ── TTS ───────────────────────────────────────────────────────────────────────

async def generate_tts_async(text: str, lang: str, out_path: Path):
    voice = VOICES.get(lang, VOICES["hi"])
    # Edge TTS (wss://speech.platform.bing.com) intermittently returns 503 /
    # WSServerHandshakeError. Retry with backoff so a transient blip does not
    # kill the whole workflow job (was causing hourly auto-heal re-runs).
    last_err = None
    for attempt in range(1, 5):  # 4 tries: ~0s, 5s, 15s, 30s backoff
        try:
            await edge_tts.Communicate(text, voice, rate="-10%").save(str(out_path))
            if out_path.exists() and out_path.stat().st_size > 0:
                return
            raise RuntimeError("edge_tts produced empty audio file")
        except Exception as e:
            last_err = e
            print(f"  [TTS] attempt {attempt}/4 failed ({lang}): {e}")
            if attempt < 4:
                await asyncio.sleep([5, 15, 30][attempt - 1])
    raise RuntimeError(f"TTS failed after 4 attempts ({lang}): {last_err}")

def generate_tts(text: str, lang: str, out_path: Path):
    asyncio.run(generate_tts_async(text, lang, out_path))


# ── v2.3 IMPROVED THUMBNAIL ───────────────────────────────────────────────────

def make_thumbnail_multitext(
    title_hi: str, title_en: str, moral_en: str,
    episode_num: int, scene_img_path: Path
) -> Path:
    """
    Multi-text thumbnail that drives CTR.
    Based on competitor analysis (Dark Fact, Stock Finance style).

    Viewers stop when they see:
    1. Dramatic/emotional image (tells them what the video is about)
    2. Large readable title text
    3. Moral/hook line (creates curiosity gap)
    4. Episode number (signals series = subscriber habit)

    Layout (like Dark Fact thumbnail that got 62 likes):
    ┌──────────────────────────────────────┐
    │ [Full dramatic scene as background] │
    │ Dark overlay for text contrast      │
    │                                      │
    │ HerooQuest ★    [Ep 1 badge]        │
    │                                      │
    │ SONA HIRAN  ← HUGE yellow 120px     │
    │ ka Raaz!    ← subtitle 70px white   │
    │                                      │
    │ 💡 Patience wins over greed         │
    │    ← moral = curiosity gap          │
    │                                      │
    │        [Heroo character right side] │
    └──────────────────────────────────────┘
    """
    import re, textwrap

    W, H   = 1280, 720

    # Use scene image as dramatic background
    if scene_img_path and scene_img_path.exists():
        try:
            base = Image.open(str(scene_img_path)).resize((W, H), Image.LANCZOS).convert("RGB")
            # Light overlay — keeps the bright happy scene visible (kid-friendly).
            # Title/moral text stay readable via their own drop-shadows + dark strip.
            # (Was 155 ≈ 60% black, which made the thumbnail dark and gloomy.)
            overlay = Image.new("RGBA", (W, H), (0, 0, 0, 80))
            base    = base.convert("RGBA")
            base    = Image.alpha_composite(base, overlay).convert("RGB")
        except:
            base = Image.new("RGB", (W, H), (8, 12, 30))
    else:
        base = Image.new("RGB", (W, H), (8, 12, 30))

    draw = ImageDraw.Draw(base, "RGBA")

    # Accent bars
    draw.rectangle([(0,0),(W,12)],   fill=(255,200,0))
    draw.rectangle([(0,H-12),(W,H)], fill=(255,200,0))

    # Heroo character — right side
    heroo_path = Path("public/image/heroo.png")
    if heroo_path.exists():
        try:
            heroo   = Image.open(str(heroo_path)).convert("RGBA")
            hh      = int(H * 0.92)
            hw      = int(heroo.width*(hh/heroo.height))
            heroo   = heroo.resize((hw,hh), Image.LANCZOS)
            base.paste(heroo, (W-hw-5, H-hh), heroo)
        except: pass

    draw = ImageDraw.Draw(base, "RGBA")

    try:
        f_brand  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  38)
        f_ep     = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  34)
        f_title  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 110)
        f_sub    = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  64)
        f_moral  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  42)
    except:
        f_brand = f_ep = f_title = f_sub = f_moral = ImageFont.load_default()

    # HerooQuest brand (top left)
    draw.rounded_rectangle([(15,15),(260,65)], radius=14, fill=(220,30,30))
    draw.text((137,40), "HerooQuest ★", font=f_brand, fill=(255,255,255), anchor="mm")

    # Episode badge (top right area)
    ep_txt = f"Ep {episode_num}"
    draw.rounded_rectangle([(W-160,15),(W-15,65)], radius=14, fill=(255,200,0))
    draw.text((W-87,40), ep_txt, font=f_ep, fill=(0,0,0), anchor="mm")

    # Main title — HUGE yellow (most important element)
    use_title = title_en or title_hi
    safe_title= re.sub(r'[\u0900-\u097F]+','',use_title).strip().upper()
    if not safe_title: safe_title = "HEROOQUEST STORY"

    title_lines = textwrap.wrap(safe_title, width=12)
    ty = 100
    for line in title_lines[:2]:
        # Drop shadow for readability
        for dx,dy in [(-4,4),(4,-4),(-4,-4),(4,4),(-4,0),(4,0),(0,4),(0,-4)]:
            draw.text((55+dx,ty+dy), line, font=f_title, fill=(0,0,0,230), anchor="la")
        draw.text((55,ty), line, font=f_title, fill=(255,200,0), anchor="la")
        ty += 125

    # Subtitle line
    topic_name = topic['english_title'][:25] if hasattr(topic,'get') else ""
    if topic_name:
        draw.text((55,ty), topic_name.upper(), font=f_sub, fill=(255,255,255), anchor="la")
        ty += 80

    # Moral line — curiosity gap
    safe_moral = re.sub(r'[\u0900-\u097F]+','',moral_en).strip()[:50]
    if safe_moral:
        # Dark strip background for moral text
        strip_y = min(ty+10, H-100)
        draw.rectangle([(40,strip_y),(int(W*0.62),strip_y+58)], fill=(0,0,0,180))
        draw.rectangle([(40,strip_y),(46,strip_y+58)], fill=(255,200,0))
        draw.text((60,strip_y+29), f"💡 {safe_moral}", font=f_moral,
                  fill=(255,255,255), anchor="lm")

    thumb_path = OUTPUT_DIR / f"kids_thumb_{TODAY}.png"
    base.save(str(thumb_path), quality=95)
    print(f"[THUMB] ✅ Multi-text thumbnail: {thumb_path.name}")
    return thumb_path


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print(f"[HEROOQUEST v2.3] lang={LANG.upper()} output={KIDS_OUTPUT.upper()}")
    print(f"[TOPIC] {topic['hindi_title']} / {topic['english_title']}")

    # Generate script
    print("[SCRIPT] Generating story (10 scenes)...")
    script = generate_script(topic)

    if not script or not script.get("scenes"):
        print("[ERR] Script generation failed"); return

    scenes    = script.get("scenes", [])
    title_hi  = script.get("title_hi", topic["hindi_title"])
    title_en  = script.get("title_en", topic["english_title"])
    moral_hi  = script.get("moral_hi", "")
    moral_en  = script.get("moral_en", "")
    seo_desc  = script.get("seo_description_en", "")
    print(f"[SCRIPT] Title EN: {title_en}")

    img_paths   = []
    audio_paths = []
    narrations  = []   # v2.6: keep per-scene spoken text for the .srt caption track

    for _idx, scene in enumerate(scenes):
        sid      = scene.get("id", len(img_paths)+1)
        narr     = scene.get(f"narration_{LANG}", scene.get("narration_hi",""))
        # v2.7: append the soft spoken like/share/subscribe CTA to the LAST scene
        if _idx == len(scenes) - 1:
            narr = (narr or "").rstrip() + KIDS_CTA.get(LANG, KIDS_CTA["hi"])
        img_pr   = scene.get("image_prompt", "Heroo in an exciting adventure scene")

        print(f"[SCENE {sid}] Generating image + audio...")
        img_p    = generate_scene_image(img_pr, sid)

        # v2.3: Enhance every image cinematically
        img_p    = enhance_image_cinematic(img_p)

        audio_p  = OUTPUT_DIR / f"kids_audio_{sid:02d}.mp3"
        generate_tts(narr, LANG, audio_p)
        img_paths.append(img_p)
        audio_paths.append(audio_p)
        narrations.append(narr)

    # v2.3: Multi-text thumbnail (scene 1 as dramatic background)
    thumb_path = make_thumbnail_multitext(
        title_hi   = title_hi,
        title_en   = title_en,
        moral_en   = moral_en,
        episode_num= 1,
        scene_img_path = img_paths[0] if img_paths else None
    )

    # v2.3: Cinematic video with transitions
    out_video = OUTPUT_DIR / f"kids_full_{TODAY}.mp4"
    print("[VIDEO] Rendering cinematic video with transitions...")
    make_video_ffmpeg_cinematic(img_paths, audio_paths, out_video, apply_transitions=True)
    print(f"✅ Full video [{LANG.upper()}]: {out_video.name}")

    # Short clip (9:16)
    out_short = OUTPUT_DIR / f"kids_short_{TODAY}.mp4"
    cmd = ["ffmpeg","-y","-i",str(out_video),"-t","60",
           "-vf","crop=405:720:437:0,scale=1080:1920",
           "-c:v","libx264","-preset","ultrafast","-crf","24","-c:a","aac",str(out_short)]
    subprocess.run(cmd, capture_output=True)

    # v2.6: build a per-scene .srt synced to the final timeline so YouTube can
    # AUTO-TRANSLATE the kids captions into the viewer's language (US/UK/Brazil).
    # Fully fail-open — a subtitle problem must never break the video pipeline.
    subtitle_srt = _build_kids_subtitles(narrations, audio_paths, LANG)

    # Save meta (unified date format)
    meta = {
        "title_hi":        title_hi,
        "title_en":        title_en,
        "moral_hi":        moral_hi,
        "moral_en":        moral_en,
        "seo_description": seo_desc,
        "lang":            LANG,
        "topic_hi":        topic["hindi_title"],
        "topic_en":        topic["english_title"],
        "video_path":      str(out_video),
        "short_path":      str(out_short),
        "thumb_path":      str(thumb_path),
        "subtitle_srt":    str(subtitle_srt) if subtitle_srt else "",
        "subtitle_lang":   LANG,
        "date":            TODAY,
        "scene_count":     len(scenes),
        "effects":         "cinematic: zoom+pan+fade+vignette+xfade transitions",
    }
    meta_path = OUTPUT_DIR / f"kids_meta_{TODAY}_{LANG}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 Saved: {meta_path.name}")

    print(f"\n{'='*60}")
    print(f"✅ HEROOQUEST DONE — {title_en} | {LANG.upper()} | {TODAY_ISO}")
    print(f"   Topic:   {topic['hindi_title']} / {topic['english_title']}")
    print(f"   Moral:   {moral_en}")
    print(f"   Scenes:  {len(scenes)}")
    print(f"   Effects: Ken Burns + Color Grade + Vignette + xFade Transitions")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
