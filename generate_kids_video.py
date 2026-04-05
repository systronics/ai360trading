# generate_kids_video.py
# Memory-safe version for GitHub Actions free runner
# Uses Ken Burns zoom — real uploadable video, no crash
# Phase 2: swap make_scene_clip() for Wan2.2 Colab clips

import os, json, asyncio, time, base64
from pathlib import Path
from datetime import date
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from ai_client import ai
from human_touch import ht, seo
from kids_content_calendar import get_today_topic

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market")
LANG         = os.environ.get("KIDS_LANG", "hi")
TODAY        = date.today().isoformat()
OUTPUT_DIR   = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

VOICES = {
    "hi": "hi-IN-SwaraNeural",
    "en": "en-US-JennyNeural",
}

# ── HEROO — Main character locked for every scene ────────────────────────
# Heroo is the STAR of this channel. Always present, always centered.
HEROO = (
    "Heroo — brave confident 10-year-old Indian boy, "
    "spiky jet-black hair, warm brown skin, big expressive brown eyes, "
    "bright red and blue superhero suit with golden 'H' emblem on chest, "
    "golden flowing cape, always smiling or showing curiosity, "
    "always the main character centered in frame"
)

# ── 3D Pixar/Disney style prefix for every image ────────────────────────
STYLE_3D = (
    "3D CGI animation render, Pixar and Disney quality, "
    "volumetric cinematic lighting, subsurface scattering skin, "
    "ray-traced shadows, photorealistic textures, depth of field, "
    "ultra-detailed background, vibrant saturated colors, "
    "child-friendly magical atmosphere, 16:9 cinematic wide shot, "
    "8K render quality"
)

# ── Arya — secondary character ───────────────────────────────────────────
ARYA = (
    "Arya — cheerful 8-year-old Indian girl, big curious brown eyes, "
    "dark hair in two braids with golden star clips, bright orange kurta"
)

# ── Combined style prompt used for every scene ──────────────────────────
SCENE_STYLE = f"{STYLE_3D}. Main character: {HEROO}. Supporting character: {ARYA}."

# ── TOPIC ────────────────────────────────────────────────────────────────
topic = get_today_topic()
print(f"[TOPIC] {topic['hindi_title']} / {topic['english_title']}")

# ── SCRIPT ───────────────────────────────────────────────────────────────
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
      "narration_hi": "4 simple Hindi sentences spoken by Heroo. 15-20 seconds when read aloud.",
      "narration_en": "4 simple English sentences spoken by Heroo. 15-20 seconds when read aloud.",
      "image_prompt": "Describe exactly what Heroo and Arya are doing in this scene. Be specific about their poses, expressions, and the background environment.",
      "emotion": "excited"
    }}
  ],
  "moral_hi": "1 sentence Hindi moral from Heroo",
  "moral_en": "1 sentence English moral from Heroo",
  "seo_description_en": "60 word YouTube description with keywords mentioning Heroo"
}}
Create exactly 6 scenes. Simple language for children. Each narration must be 4 sentences.
"""
    return ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")

# ── IMAGE — 3-layer fallback chain ───────────────────────────────────────
def generate_scene_image(prompt: str, scene_id: int) -> Path:
    img_path = OUTPUT_DIR / f"kids_scene_{scene_id:02d}.png"
    if img_path.exists():
        print(f"  [CACHE] Scene {scene_id}")
        return img_path

    # Full prompt = 3D style + Heroo character + scene description
    full_prompt = f"{SCENE_STYLE} Scene: {prompt}"

    # ── LAYER 1: Gemini Flash (free tier) ────────────────────────────────
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            )
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                img_path.write_bytes(part.inline_data.data)
                print(f"  [IMG-1] Scene {scene_id} via Gemini Flash 3D ✓")
                return img_path
    except Exception as e:
        print(f"  [WARN-1] Gemini failed scene {scene_id}: {e}")

    time.sleep(3)

    # ── LAYER 2: DALL-E 3 via OpenAI ─────────────────────────────────────
    try:
        from openai import OpenAI
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            import urllib.request
            client_oai = OpenAI(api_key=openai_key)
            dalle_prompt = full_prompt[:1000]
            response = client_oai.images.generate(
                model="dall-e-3",
                prompt=dalle_prompt,
                size="1792x1024",
                quality="standard",
                n=1,
            )
            img_url = response.data[0].url
            urllib.request.urlretrieve(img_url, str(img_path))
            img = Image.open(img_path).resize((1280, 720), Image.LANCZOS)
            img.save(img_path)
            print(f"  [IMG-2] Scene {scene_id} via DALL-E 3 3D ✓")
            return img_path
    except Exception as e:
        print(f"  [WARN-2] DALL-E 3 failed scene {scene_id}: {e}")

    time.sleep(2)

    # ── LAYER 3: Stability AI free tier ──────────────────────────────────
    try:
        import urllib.request
        stability_key = os.environ.get("STABILITY_API_KEY")
        if stability_key:
            headers = {
                "Authorization": f"Bearer {stability_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            payload = json.dumps({
                "text_prompts": [{"text": full_prompt[:500], "weight": 1}],
                "cfg_scale": 7,
                "height": 720,
                "width": 1280,
                "samples": 1,
                "steps": 20,
            }).encode()
            req = urllib.request.Request(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                data=payload,
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
                img_bytes = base64.b64decode(data["artifacts"][0]["base64"])
                img_path.write_bytes(img_bytes)
                img = Image.open(img_path).resize((1280, 720), Image.LANCZOS)
                img.save(img_path)
                print(f"  [IMG-3] Scene {scene_id} via Stability AI ✓")
                return img_path
    except Exception as e:
        print(f"  [WARN-3] Stability AI failed scene {scene_id}: {e}")

    # ── FALLBACK: Heroo branded placeholder ──────────────────────────────
    colors = ["#1a1a2e","#16213e","#0f3460","#533483","#e94560","#2b2d42"]
    img = Image.new("RGB", (1280, 720), color=colors[scene_id % len(colors)])
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 1270, 710], outline="#FFD700", width=5)
    draw.rectangle([20, 20, 1260, 700], outline="#FF6B35", width=2)
    try:
        font_big   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_med   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font_big = font_med = font_small = ImageFont.load_default()
    draw.ellipse([580, 240, 700, 360], fill="#FFD700", outline="#FF6B35", width=4)
    draw.text((640, 300), "H", fill="#1a1a2e", anchor="mm", font=font_big)
    draw.text((640, 420), f"Scene {scene_id}", fill="#FFD700", anchor="mm", font=font_med)
    draw.text((640, 480), "HerooQuest", fill="#FF6B35", anchor="mm", font=font_small)
    img.save(img_path)
    print(f"  [FALLBACK] Scene {scene_id} Heroo placeholder saved")
    return img_path

# ── TTS ──────────────────────────────────────────────────────────────────
async def generate_tts_async(text: str, lang: str, out_path: Path):
    voice = VOICES.get(lang, VOICES["hi"])
    comm  = edge_tts.Communicate(text, voice, rate="-10%")
    await comm.save(str(out_path))

def generate_tts(text: str, lang: str, out_path: Path):
    asyncio.run(generate_tts_async(text, lang, out_path))

# ── VIDEO — lightweight ffmpeg, no MoviePy ───────────────────────────────
def make_video_ffmpeg(scenes: list, audio_paths: list, out_path: Path):
    """
    ffmpeg directly — 10x less memory than MoviePy.
    Each scene: 3D image + Ken Burns zoom + TTS audio.
    Min 15 seconds per scene = ~90s total for 6 scenes.
    """
    import subprocess
    clip_paths = []

    for i, (scene_img, audio_path) in enumerate(zip(scenes, audio_paths)):
        clip_path = OUTPUT_DIR / f"clip_{i:02d}.mp4"

        probe = subprocess.run([
            "ffprobe", "-v", "quiet", "-show_entries",
            "format=duration", "-of", "csv=p=0", str(audio_path)
        ], capture_output=True, text=True)
        duration = max(float(probe.stdout.strip() or "15"), 15.0)

        zoom_filter = (
            f"zoompan=z='if(lte(zoom,1.0),1.05,max(1.001,zoom-0.0015))':"
            f"d={int(duration * 25)}:x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':s=1280x720:fps=25,"
            f"scale=1280:720"
        )

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(scene_img),
            "-i", str(audio_path),
            "-vf", zoom_filter,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "28",
            "-c:a", "aac",
            "-b:a", "128k",
            "-t", str(duration + 0.5),
            "-shortest",
            "-pix_fmt", "yuv420p",
            str(clip_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [ERR] ffmpeg scene {i}: {result.stderr[-200:]}")
        else:
            print(f"  [CLIP] Scene {i} rendered ✓  ({duration:.1f}s)")
            clip_paths.append(clip_path)

    if not clip_paths:
        raise RuntimeError("No clips generated")

    concat_file = OUTPUT_DIR / "concat.txt"
    concat_file.write_text(
        "\n".join([f"file '{p.resolve()}'" for p in clip_paths])
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264", "-preset", "ultrafast",
        "-crf", "26", "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        str(out_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Concat failed: {result.stderr[-300:]}")
    print(f"[VIDEO] Full video: {out_path}")
    return out_path

def make_short_ffmpeg(video_path: Path, short_path: Path):
    """YouTube Shorts — 9:16, max 60s"""
    import subprocess
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-t", "60",
        "-vf", "crop=405:720:437:0,scale=1080:1920",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-crf", "26", "-c:a", "aac",
        str(short_path)
    ]
    subprocess.run(cmd, capture_output=True)
    print(f"[SHORT] YouTube Short: {short_path}")

def make_reel_ffmpeg(video_path: Path, reel_path: Path):
    """Instagram Reel — 9:16, max 90s, 44.1kHz audio"""
    import subprocess
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-t", "90",
        "-vf", "crop=405:720:437:0,scale=1080:1920",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-crf", "26", "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        str(reel_path)
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode == 0:
        print(f"[REEL] Instagram Reel: {reel_path}")
    else:
        print(f"[REEL ERR] {result.stderr[-200:]}")

# ── MAIN ─────────────────────────────────────────────────────────────────
def main():
    print("[SCRIPT] Generating story...")
    script = generate_script(topic)

    script_path = OUTPUT_DIR / f"kids_script_{TODAY}.json"
    script_path.write_text(json.dumps(script, ensure_ascii=False, indent=2))
    print(f"[SCRIPT] Title: {script.get('title_en', '')}")

    scenes      = script.get("scenes", [])
    img_paths   = []
    audio_paths = []

    for i, scene in enumerate(scenes):
        sid        = scene.get("id", i + 1)
        narr_hi    = scene.get("narration_hi", "")
        narr_en    = scene.get("narration_en", "")
        img_prompt = scene.get("image_prompt", f"Scene {sid}")

        if LANG == "en":
            narr_text = narr_en
            tts_lang  = "en"
        elif LANG == "both":
            narr_text = narr_hi + " " + narr_en
            tts_lang  = "hi"
        else:
            narr_text = narr_hi
            tts_lang  = "hi"

        print(f"[SCENE {sid}] Generating image...")
        img_path = generate_scene_image(img_prompt, sid)
        img_paths.append(img_path)
        time.sleep(8)

        print(f"[SCENE {sid}] Generating TTS...")
        tts_path = OUTPUT_DIR / f"kids_tts_{sid}.mp3"
        generate_tts(narr_text, tts_lang, tts_path)
        audio_paths.append(tts_path)

    video_path = OUTPUT_DIR / f"kids_video_{TODAY}.mp4"
    short_path = OUTPUT_DIR / f"kids_short_{TODAY}.mp4"
    reel_path  = OUTPUT_DIR / f"kids_reel_{TODAY}.mp4"

    print("[RENDER] Building video with ffmpeg...")
    make_video_ffmpeg(img_paths, audio_paths, video_path)
    make_short_ffmpeg(video_path, short_path)
    make_reel_ffmpeg(video_path, reel_path)

    meta = {
        "date":             TODAY,
        "category":         topic["category"],
        "title_hi":         script.get("title_hi", topic["hindi_title"]),
        "title_en":         script.get("title_en", topic["english_title"]),
        "description_en":   script.get("seo_description_en", ""),
        "moral_hi":         script.get("moral_hi", ""),
        "moral_en":         script.get("moral_en", ""),
        "seo_tags":         topic["seo_tags"] + [
                                "kids","children","animation","Pixar","cartoon",
                                "HerooQuest","Heroo","3D","Disney","KidsStories"
                            ],
        "target_countries": topic["target_countries"],
        "video_path":       str(video_path),
        "short_path":       str(short_path),
        "reel_path":        str(reel_path),
        "public_video_url": "",
        "youtube_video_id": "",
    }
    meta_path = OUTPUT_DIR / f"kids_meta_{TODAY}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))

    print(f"[DONE] Video : {video_path}")
    print(f"[DONE] Short : {short_path}")
    print(f"[DONE] Reel  : {reel_path}")
    print(f"[DONE] Meta  : {meta_path}")

if __name__ == "__main__":
    main()
