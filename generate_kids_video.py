# generate_kids_video.py
# Memory-safe version for GitHub Actions free runner
# Uses simple Ken Burns zoom — real uploadable video, no crash
# Phase 2: swap make_scene_clip() for Wan2.2 Colab clips

import os, json, asyncio, textwrap, time
from pathlib import Path
from datetime import date
import edge_tts
from PIL import Image, ImageDraw
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

PIXAR_STYLE = (
    "Pixar 3D animation style, Disney quality, cinematic lighting, "
    "vibrant colors, soft shadows, expressive cartoon characters, "
    "ultra-detailed, child-friendly, magical atmosphere, "
    "Arya — cheerful 8-year-old Indian girl, big curious brown eyes, "
    "dark hair in two braids with golden star clips, bright orange kurta"
)

# ── TOPIC ────────────────────────────────────────────────────────────────
topic = get_today_topic()
print(f"[TOPIC] {topic['hindi_title']} / {topic['english_title']}")

# ── SCRIPT ───────────────────────────────────────────────────────────────
def generate_script(topic: dict) -> dict:
    prompt = f"""
You are a master kids storyteller. Create a bilingual animated story.
Topic (Hindi): {topic['hindi_title']}
Topic (English): {topic['english_title']}
Category: {topic['category']}
Target: children 4-12 years

Output ONLY valid JSON, no markdown, no extra text:
{{
  "title_hi": "Hindi title max 10 words",
  "title_en": "English title max 10 words",
  "scenes": [
    {{
      "id": 1,
      "narration_hi": "2 simple Hindi sentences",
      "narration_en": "2 simple English sentences",
      "image_prompt": "{PIXAR_STYLE}. Scene: describe what is happening",
      "emotion": "happy"
    }}
  ],
  "moral_hi": "1 sentence Hindi moral",
  "moral_en": "1 sentence English moral",
  "seo_description_en": "60 word YouTube description with keywords"
}}
Create exactly 6 scenes. Simple language for children.
"""
    return ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")

# ── IMAGE ────────────────────────────────────────────────────────────────
def generate_scene_image(prompt: str, scene_id: int) -> Path:
    img_path = OUTPUT_DIR / f"kids_scene_{scene_id:02d}.png"
    if img_path.exists():
        print(f"  [CACHE] Scene {scene_id}")
        return img_path
    try:
        import google.generativeai as genai
        import base64
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")
        response = model.generate_content(
            f"Generate single image: {prompt}",
            generation_config={"response_modalities": ["IMAGE"]}
        )
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                img_path.write_bytes(base64.b64decode(part.inline_data.data))
                print(f"  [IMG] Scene {scene_id} via Gemini")
                return img_path
    except Exception as e:
        print(f"  [WARN] Gemini failed scene {scene_id}: {e}")

    # Fallback placeholder
    colors = ["#FFD700","#FF6B35","#6B8DD6","#4ECDC4","#FF4757","#A29BFE"]
    img = Image.new("RGB", (1280, 720), color=colors[scene_id % len(colors)])
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 1260, 700], outline="#FFFFFF", width=6)
    draw.text((640, 360), f"Scene {scene_id}", fill="white", anchor="mm")
    img.save(img_path)
    print(f"  [FALLBACK] Scene {scene_id} placeholder saved")
    return img_path

# ── TTS ──────────────────────────────────────────────────────────────────
async def generate_tts_async(text: str, lang: str, out_path: Path):
    voice = VOICES.get(lang, VOICES["hi"])
    comm  = edge_tts.Communicate(text, voice, rate="-10%")
    await comm.save(str(out_path))

def generate_tts(text: str, lang: str, out_path: Path):
    asyncio.run(generate_tts_async(text, lang, out_path))

# ── VIDEO — lightweight ffmpeg, no MoviePy in memory ────────────────────
def make_video_ffmpeg(scenes: list, audio_paths: list, out_path: Path):
    """
    Uses ffmpeg directly — 10x less memory than MoviePy.
    Each scene: static image with Ken Burns zoom + TTS audio.
    Concatenates all scenes into final MP4.
    """
    import subprocess

    clip_paths = []

    for i, (scene_img, audio_path) in enumerate(zip(scenes, audio_paths)):
        clip_path = OUTPUT_DIR / f"clip_{i:02d}.mp4"

        # Get audio duration
        probe = subprocess.run([
            "ffprobe", "-v", "quiet", "-show_entries",
            "format=duration", "-of", "csv=p=0", str(audio_path)
        ], capture_output=True, text=True)
        duration = max(float(probe.stdout.strip() or "6"), 6.0)

        # Ken Burns zoom using ffmpeg zoompan filter — zero extra RAM
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
            "-preset", "ultrafast",  # fastest encoding — saves memory
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
            print(f"  [CLIP] Scene {i} rendered ✓")
            clip_paths.append(clip_path)

    if not clip_paths:
        raise RuntimeError("No clips generated")

    # Write concat list
    concat_file = OUTPUT_DIR / "concat.txt"
    concat_file.write_text(
        "\n".join([f"file '{p.resolve()}'" for p in clip_paths])
    )

    # Concatenate all clips
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
    print(f"[VIDEO] Final video: {out_path}")
    return out_path

def make_short_ffmpeg(video_path: Path, short_path: Path):
    """Crop center 60s to 9:16 for Shorts"""
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
    print(f"[SHORT] {short_path}")

# ── MAIN ─────────────────────────────────────────────────────────────────
def main():
    print("[SCRIPT] Generating story...")
    script = generate_script(topic)

    # Save script
    script_path = OUTPUT_DIR / f"kids_script_{TODAY}.json"
    script_path.write_text(json.dumps(script, ensure_ascii=False, indent=2))
    print(f"[SCRIPT] Title: {script.get('title_en', '')}")

    scenes     = script.get("scenes", [])
    img_paths  = []
    audio_paths = []

    for i, scene in enumerate(scenes):
        sid       = scene.get("id", i + 1)
        narr_hi   = scene.get("narration_hi", "")
        narr_en   = scene.get("narration_en", "")
        img_prompt = scene.get("image_prompt", f"Scene {sid}")

        # Narration language
        if LANG == "en":
            narr_text = narr_en
            tts_lang  = "en"
        else:
            narr_text = narr_hi
            tts_lang  = "hi"

        print(f"[SCENE {sid}] Generating image...")
        img_path = generate_scene_image(img_prompt, sid)
        img_paths.append(img_path)
        time.sleep(4)  # Gemini free tier rate limit

        print(f"[SCENE {sid}] Generating TTS...")
        tts_path = OUTPUT_DIR / f"kids_tts_{sid}.mp3"
        generate_tts(narr_text, tts_lang, tts_path)
        audio_paths.append(tts_path)

    # Render video using ffmpeg directly — no MoviePy
    title_slug = topic["hindi_title"][:25].replace(" ", "_").replace("/", "-")
    video_path = OUTPUT_DIR / f"kids_video_{TODAY}.mp4"
    short_path = OUTPUT_DIR / f"kids_short_{TODAY}.mp4"

    print("[RENDER] Building video with ffmpeg...")
    make_video_ffmpeg(img_paths, audio_paths, video_path)
    make_short_ffmpeg(video_path, short_path)

    # Save meta for upload step
    meta = {
        "date":             TODAY,
        "category":         topic["category"],
        "title_hi":         script.get("title_hi", topic["hindi_title"]),
        "title_en":         script.get("title_en", topic["english_title"]),
        "description_en":   script.get("seo_description_en", ""),
        "moral_hi":         script.get("moral_hi", ""),
        "moral_en":         script.get("moral_en", ""),
        "seo_tags":         topic["seo_tags"] + ["kids","children","animation","Pixar","cartoon","HerooQuest"],
        "target_countries": topic["target_countries"],
        "video_path":       str(video_path),
        "short_path":       str(short_path),
        "public_video_url": "",
        "youtube_video_id": "",
    }
    meta_path = OUTPUT_DIR / f"kids_meta_{TODAY}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))

    print(f"[DONE] Video: {video_path}")
    print(f"[DONE] Short: {short_path}")
    print(f"[DONE] Meta:  {meta_path}")

if __name__ == "__main__":
    main()
