# generate_kids_video.py
# Full kids Pixar-style video generator — plugs into ai_client + human_touch
import os, json, asyncio, textwrap
from pathlib import Path
from datetime import date
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Reuse your existing infra — no new API keys needed
from ai_client import ai
from human_touch import ht, seo
from kids_content_calendar import get_today_topic

try:
    from moviepy.editor import (ImageClip, AudioFileClip, concatenate_videoclips,
                                  CompositeVideoClip, TextClip, CompositeAudioClip)
    import moviepy.editor as mpe
except ImportError:
    raise SystemExit("pip install moviepy==1.0.3 imageio==2.9.0")

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ── VOICES ──────────────────────────────────────────────────────────────
VOICES = {
    "hi": "hi-IN-SwaraNeural",    # warm female Hindi — same as ZENO reel
    "en": "en-US-JennyNeural",    # warm female English
}
SCENE_DURATION = 7  # seconds per scene image
BG_MUSIC_DIR = Path("public/music")
PIXAR_STYLE   = (
    "Pixar 3D animation style, Disney quality, cinematic lighting, "
    "vibrant colors, soft shadows, expressive cartoon characters, "
    "ultra-detailed, 4K render, child-friendly, magical atmosphere"
)

# ── STEP 1: Get today's topic ────────────────────────────────────────────
topic = get_today_topic()
print(f"[TOPIC] {topic['hindi_title']} / {topic['english_title']}")

# ── STEP 2: Generate dual-language script ────────────────────────────────
def generate_script(topic: dict) -> dict:
    prompt = f"""
You are a master kids storyteller. Create a bilingual animated story.

Topic (Hindi): {topic['hindi_title']}
Topic (English): {topic['english_title']}
Category: {topic['category']}
Target: children 4–12 years, audiences in {', '.join(topic['target_countries'])}

Output ONLY a JSON object (no markdown, no extra text):
{{
  "title_hi": "Hindi title (max 10 words)",
  "title_en": "English title (max 10 words)",
  "hook_hi": "First 2 sentences in Hindi to hook kids instantly",
  "hook_en": "First 2 sentences in English to hook kids instantly",
  "scenes": [
    {{
      "id": 1,
      "narration_hi": "Hindi narration for this scene (2–3 sentences, simple words)",
      "narration_en": "English narration for this scene (2–3 sentences)",
      "image_prompt": "Detailed Pixar 3D scene description for AI image generation. {PIXAR_STYLE}. Scene details: ...",
      "emotion": "happy/excited/sad/curious/brave/wonder"
    }}
  ],
  "moral_hi": "Moral of the story in Hindi (1 sentence)",
  "moral_en": "Moral of the story in English (1 sentence)",
  "seo_description_en": "90-word YouTube description in English with keywords"
}}
Create 7 scenes. Keep language very simple for children. Make it magical and emotional.
"""
    data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
    return data

# ── STEP 3: Generate scene images (Gemini free tier) ─────────────────────
def generate_scene_image(prompt: str, scene_id: int, lang: str = "hi") -> Path:
    img_path = OUTPUT_DIR / f"kids_scene_{scene_id:02d}.png"
    if img_path.exists():
        print(f"  [CACHE] Scene {scene_id} already generated")
        return img_path

    try:
        import google.generativeai as genai
        import base64
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")
        response = model.generate_content(
            f"Generate single image: {prompt}",
            generation_config={"response_modalities": ["IMAGE"]}
        )
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                img_path.write_bytes(base64.b64decode(part.inline_data.data))
                print(f"  [IMG] Scene {scene_id} generated via Gemini")
                return img_path
    except Exception as e:
        print(f"  [WARN] Gemini image failed: {e} — using placeholder")

    # Fallback: colored placeholder with text (always works)
    colors = {
        "happy":    "#FFD700", "excited": "#FF6B35",
        "sad":      "#6B8DD6", "curious": "#4ECDC4",
        "brave":    "#FF4757", "wonder":  "#A29BFE"
    }
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (1920, 1080), color=colors.get("happy", "#FFD700"))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 1880, 1040], outline="#FFFFFF", width=8)
    draw.text((960, 540), f"Scene {scene_id}", fill="white",
              anchor="mm", font_size=80)
    img.save(img_path)
    return img_path

# ── STEP 4: Ken Burns pan/zoom effect ────────────────────────────────────
def make_scene_clip(img_path: Path, duration: float, zoom_dir: str = "in") -> ImageClip:
    img = Image.open(img_path).convert("RGB")
    W, H = 1920, 1080  # 16:9

    # Resize and crop to exact 16:9
    iw, ih = img.size
    scale = max(W / iw, H / ih) * 1.12  # 12% extra for zoom travel
    new_w, new_h = int(iw * scale), int(ih * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    fps = 24
    frames = []
    n_frames = int(duration * fps)

    for i in range(n_frames):
        t = i / max(n_frames - 1, 1)
        if zoom_dir == "in":
            z = 1.0 + 0.08 * t          # gentle zoom in
            x_off = int((new_w - W * z) / 2)
            y_off = int((new_h - H * z) / 2)
        else:
            z = 1.08 - 0.08 * t         # gentle zoom out
            x_off = int((new_w - W) * t * 0.5)
            y_off = int((new_h - H) * t * 0.3)

        frame_w, frame_h = int(W * z), int(H * z)
        x_off = max(0, min(x_off, new_w - frame_w))
        y_off = max(0, min(y_off, new_h - frame_h))
        cropped = img.crop((x_off, y_off, x_off + frame_w, y_off + frame_h))
        frame = cropped.resize((W, H), Image.LANCZOS)
        frames.append(np.array(frame))

    clip = ImageClip(np.array(frames[0]))  # placeholder
    # Use make_frame for memory efficiency
    frames_list = frames
    def make_frame(t):
        idx = min(int(t * fps), len(frames_list) - 1)
        return frames_list[idx]
    return (ImageClip(make_frame=make_frame, duration=duration)
            .set_fps(fps)
            .set_duration(duration))

# ── STEP 5: TTS audio generation ─────────────────────────────────────────
async def generate_tts(text: str, lang: str, out_path: Path):
    voice = VOICES[lang]
    speed = ht.get_tts_speed()
    rate_pct = int((speed - 1.0) * 100)
    rate_str = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
    # Kids content: slightly slower for comprehension
    rate_str = "-10%"
    communicate = edge_tts.Communicate(text, voice, rate=rate_str)
    await communicate.save(str(out_path))

# ── STEP 6: Build subtitles overlay ──────────────────────────────────────
def add_subtitle_overlay(clip, text: str, lang: str) -> CompositeVideoClip:
    try:
        font = "Arial-Bold" if lang == "en" else "Arial-Bold"
        txt = TextClip(
            textwrap.fill(text, width=45),
            fontsize=48, color="white",
            stroke_color="black", stroke_width=3,
            font=font, method="caption",
            size=(1800, None), align="center"
        )
        txt = txt.set_position(("center", 0.82), relative=True).set_duration(clip.duration)
        return CompositeVideoClip([clip, txt])
    except Exception:
        return clip  # subtitles optional — never crash

# ── STEP 7: Background music ──────────────────────────────────────────────
def get_bg_music(duration: float) -> AudioFileClip:
    today_num = date.today().weekday()
    music_files = sorted(BG_MUSIC_DIR.glob("*.mp3"))
    if not music_files:
        return None
    music_path = music_files[today_num % len(music_files)]
    music = AudioFileClip(str(music_path)).volumex(0.12)  # very low for kids TTS clarity
    if music.duration < duration:
        loops = int(duration / music.duration) + 1
        music = concatenate_videoclips([music] * loops).subclip(0, duration)
    return music.subclip(0, duration)

# ── MAIN ──────────────────────────────────────────────────────────────────
def main():
    today = date.today().isoformat()
    lang = os.environ.get("KIDS_LANG", "hi")  # "hi" or "en" or "both"

    print("[SCRIPT] Generating story script...")
    script = generate_script(topic)

    # Save script for debugging
    script_path = OUTPUT_DIR / f"kids_script_{today}.json"
    script_path.write_text(json.dumps(script, ensure_ascii=False, indent=2))

    scenes = script.get("scenes", [])
    print(f"[SCENES] {len(scenes)} scenes to build")

    all_clips = []
    full_narration_hi = []
    full_narration_en = []

    for i, scene in enumerate(scenes):
        sid = scene.get("id", i + 1)
        narr_hi = scene.get("narration_hi", "")
        narr_en = scene.get("narration_en", "")
        img_prompt = scene.get("image_prompt", f"Scene {sid}")
        emotion = scene.get("emotion", "happy")
        zoom_dir = "in" if i % 2 == 0 else "out"

        print(f"  [SCENE {sid}] {emotion} — generating image...")
        img_path = generate_scene_image(img_prompt, sid)

        # TTS for this scene
        narr_text = narr_hi if lang == "hi" else narr_en
        tts_lang = "hi" if lang == "hi" else "en"
        tts_path = OUTPUT_DIR / f"kids_tts_{sid}_{tts_lang}.mp3"
        asyncio.run(generate_tts(narr_text, tts_lang, tts_path))

        audio_clip = AudioFileClip(str(tts_path))
        scene_dur = max(SCENE_DURATION, audio_clip.duration + 0.5)

        video_clip = make_scene_clip(img_path, scene_dur, zoom_dir)
        video_clip = video_clip.set_audio(audio_clip.set_start(0))
        video_clip = add_subtitle_overlay(video_clip, narr_text, tts_lang)
        all_clips.append(video_clip)

        full_narration_hi.append(narr_hi)
        full_narration_en.append(narr_en)

    # Concatenate all scenes
    final = concatenate_videoclips(all_clips, method="compose")

    # Add background music
    bg_music = get_bg_music(final.duration)
    if bg_music:
        final_audio = CompositeAudioClip([final.audio, bg_music])
        final = final.set_audio(final_audio)

    # Save full video (16:9)
    title_slug = topic["hindi_title"][:30].replace(" ", "_").replace("/", "-")
    video_path = OUTPUT_DIR / f"kids_video_{today}_{title_slug}.mp4"
    print(f"[RENDER] Rendering {final.duration:.1f}s video → {video_path}")
    final.write_videofile(
        str(video_path), fps=24, codec="libx264",
        audio_codec="aac", threads=4,
        ffmpeg_params=["-crf", "23", "-preset", "fast"]
    )

    # Save short (9:16) — first 60 seconds, cropped center
    short_path = OUTPUT_DIR / f"kids_short_{today}.mp4"
    short_clip = final.subclip(0, min(60, final.duration))
    # Crop to 9:16 (center 608px of 1080p)
    short_clip = short_clip.crop(x_center=960, width=608).resize((1080, 1920))
    short_clip.write_videofile(
        str(short_path), fps=24, codec="libx264",
        audio_codec="aac", threads=4
    )

    # Save meta
    meta = {
        "date": today,
        "category": topic["category"],
        "title_hi": script.get("title_hi", topic["hindi_title"]),
        "title_en": script.get("title_en", topic["english_title"]),
        "description_en": script.get("seo_description_en", ""),
        "moral_hi": script.get("moral_hi", ""),
        "moral_en": script.get("moral_en", ""),
        "seo_tags": topic["seo_tags"] + ["kids","children","animation","Pixar","cartoon"],
        "target_countries": topic["target_countries"],
        "video_path": str(video_path),
        "short_path": str(short_path),
        "public_video_url": "",
        "youtube_video_id": "",
    }
    meta_path = OUTPUT_DIR / f"kids_meta_{today}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"[DONE] Kids video ready: {video_path}")
    print(f"[DONE] Kids short ready: {short_path}")

if __name__ == "__main__":
    main()
