"""
generate_kids_video.py — HerooQuest v3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v3.0 (2026-06-08) — VARIETY + INTEREST + BRIGHTNESS (owner feedback):
    Owner: "conversation lines are similar in all videos, repetitive… stories
    not interesting… and the in-video image is too bright (thumbnail is fine)."
    1. STORY: generate_script() now injects a randomised per-episode RECIPE
       (way-in / story-shape / tone / viewer-game) AND makes the topic's REAL
       characters (Akbar, Birbal, Einstein, the astronauts…) the speaking stars,
       with Heroo/Arya as the explorers who arrive and react. Fresh catchphrase
       per episode; no more canned "Oh no/Wow/Yay" sameness. → varied, on-topic,
       genuinely educational stories instead of the same two kids every time.
    2. VOICES: real story characters get distinct guest-pool voices (hashed by
       name) instead of one flat "default" → multi-character stories sound real.
    3. BRIGHTNESS: the video ran an eq pass ON TOP of enhance_image_cinematic()
       → washed-out/too-bright frames (the thumbnail skips eq, so it looked fine).
       Trimmed enhance (bright 1.18→1.08, sat 1.40→1.25) and neutralised the eq
       (brightness 0.05→0, sat 1.30→1.06) so video matches the thumbnail. Still
       bright/cheerful — anti-scary grade intact.

v3.0b (2026-07-13, same day) — THUMBNAIL + TITLE like the winning channels:
    6. thumbnail_hook is now HINGLISH in English letters ('JADUI GAAY?!') —
       was English ('HE DID IT!') for a Hindi audience; two-tone title text
       (line 1 yellow, line 2 white).
    7. NEW thumbnail_question ('Lalchi padosi ka kya hua?') replaces the moral
       on the thumbnail strip — the moral SPOILED the ending; a question earns
       the click. Falls back to moral.
    8. Tofu fixes: 💡 prefix + brand ★ removed (DejaVu/Arial have no glyph —
       rendered as hollow boxes on every past thumbnail).
    9. AI titles must now be DRAMATIC (conflict/twist), not descriptive;
       upload_kids_youtube v2.6 leads the YouTube title with the Devanagari
       Hindi title + 'Hindi Kahaniya | Moral Stories' search phrases.

v3.0 (2026-07-13) — REAL STORIES + VARIETY (owner: "boring, repeated, same lines"):
    1. STORY SEED GROUNDING: kids_content_calendar v2.0 now supplies 128 real
       classic stories, each with a `story_seed` plot outline. The script
       prompt makes the AI retell THAT story faithfully and completely —
       no more thin invented plots that all feel the same.
    2. COLD OPEN: scene 1 must start inside the story at a dramatic/funny
       moment. Openers like "namaste dosto / aaj hum" are banned (retention).
    3. COMPLETENESS: max_tokens 6000→8000 + weak-script retry (fewer than 7
       scenes or a thin final scene → one regeneration with a fresh recipe)
       so stories stop ending abruptly.
    4. OUTRO VARIETY: the single hardcoded like/share/subscribe line (same
       words every video) is now a 6-variant pool rotated by day.
    5. NARRATOR VARIETY: narrator delivery (rate/pitch) rotates through 3
       presets by day — Hindi has only 2 neural voices, so freshness must
       come from delivery.

v2.9 (2026-06-05) — DIALOGUE + MULTI-VOICE (engagement / retention):
    Two upgrades so the story feels like a real cartoon, not a single-narrator
    audiobook (drives watch-time = the #1 YouTube reach signal):
    LAYER 1 — the script is now CONVERSATION-driven: each scene is a back-and-
      forth between Heroo, Arya (+ optional Mom/Dad) with a problem, emotions,
      a repeated catchphrase, and direct questions to the viewer.
    LAYER 2 — MULTI-VOICE render: each character speaks in a distinct voice
      (English uses true child voices Ana/Maisie; Hindi's 2 voices are split by
      pitch/rate per role). Per-line clips are concatenated into one per-scene
      mp3, so the existing video + subtitle pipeline is unchanged (low risk).
    Fully back-compatible + fail-open: a script without "dialogue", or any
    multi-voice error, falls back to the old single-voice narration path.

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
import shutil
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

# v2.9 — MULTI-VOICE DIALOGUE. Each character gets a distinct voice so the story
# feels like a real cartoon conversation. Hindi has only two hi-IN neural voices
# (Swara F / Madhur M), so roles are separated further by pitch + rate. English
# has TRUE child voices (Ana, Maisie) — perfect for the kid characters.
SPEAKER_VOICES = {
    "hi": {
        "Narrator": {"voice": "hi-IN-MadhurNeural", "rate": "-6%", "pitch": "+0Hz"},
        "Heroo":    {"voice": "hi-IN-MadhurNeural", "rate": "+8%", "pitch": "+30Hz"},   # bright young boy
        "Arya":     {"voice": "hi-IN-SwaraNeural",  "rate": "+8%", "pitch": "+35Hz"},   # young girl
        "Mom":      {"voice": "hi-IN-SwaraNeural",  "rate": "-4%", "pitch": "+0Hz"},
        "Dad":      {"voice": "hi-IN-MadhurNeural", "rate": "-2%", "pitch": "-12Hz"},
        "default":  {"voice": "hi-IN-SwaraNeural",  "rate": "+0%", "pitch": "+12Hz"},
    },
    "en": {
        "Narrator": {"voice": "en-IN-PrabhatNeural", "rate": "-6%", "pitch": "+0Hz"},
        "Heroo":    {"voice": "en-US-AnaNeural",     "rate": "+0%", "pitch": "+0Hz"},    # genuine child voice
        "Arya":     {"voice": "en-GB-MaisieNeural",  "rate": "+0%", "pitch": "+0Hz"},    # child girl voice
        "Mom":      {"voice": "en-US-JennyNeural",   "rate": "-2%", "pitch": "+0Hz"},
        "Dad":      {"voice": "en-US-GuyNeural",     "rate": "-2%", "pitch": "-12Hz"},
        "default":  {"voice": "en-US-JennyNeural",   "rate": "+0%", "pitch": "+0Hz"},
    },
}

# v3.0: rotate the Narrator's delivery daily so consecutive videos don't share
# the exact same narration feel (Hindi has only 2 neural voices — variety must
# come from delivery). Deterministic per day; both languages get the preset.
_NARRATOR_PRESETS = [
    {"rate": "-6%", "pitch": "+0Hz"},   # calm classic storyteller
    {"rate": "+2%", "pitch": "+6Hz"},   # bright & lively
    {"rate": "-3%", "pitch": "-8Hz"},   # deep & dramatic
]
_np = _NARRATOR_PRESETS[date.today().toordinal() % len(_NARRATOR_PRESETS)]
for _tbl in SPEAKER_VOICES.values():
    _tbl["Narrator"] = {**_tbl["Narrator"], "rate": _np["rate"], "pitch": _np["pitch"]}

# Story characters (Akbar, Birbal, Rama, Einstein, the astronauts...) are not in
# SPEAKER_VOICES. Instead of giving them all one flat "default" voice, assign each
# a distinct, CONSISTENT voice from a small pool (hashed by name) so a multi-
# character story actually sounds like different people. Hindi has only 2 neural
# voices, so we vary pitch/rate to differentiate; English has more true voices.
GUEST_VOICES = {
    "hi": [
        {"voice": "hi-IN-MadhurNeural", "rate": "-3%", "pitch": "-8Hz"},
        {"voice": "hi-IN-SwaraNeural",  "rate": "-2%", "pitch": "+4Hz"},
        {"voice": "hi-IN-MadhurNeural", "rate": "+2%", "pitch": "+12Hz"},
        {"voice": "hi-IN-SwaraNeural",  "rate": "+0%", "pitch": "-6Hz"},
    ],
    "en": [
        {"voice": "en-IN-PrabhatNeural",     "rate": "-2%", "pitch": "-6Hz"},
        {"voice": "en-US-GuyNeural",         "rate": "+0%", "pitch": "+4Hz"},
        {"voice": "en-US-ChristopherNeural", "rate": "-2%", "pitch": "+0Hz"},
        {"voice": "en-GB-RyanNeural",        "rate": "+0%", "pitch": "+2Hz"},
    ],
}

def _speaker_style(speaker: str, lang: str) -> dict:
    """Map a dialogue speaker name → {voice, rate, pitch}. Tolerant of messy
    names like 'Heroo (excited)' or 'narrator:'. Known cast → their fixed voice;
    a story's real characters (unknown names) → a distinct guest-pool voice."""
    table = SPEAKER_VOICES.get(lang, SPEAKER_VOICES["hi"])
    if not speaker:
        return table["default"]
    key = speaker.strip().split("(")[0].split(":")[0].strip().title()
    if key in table:
        return table[key]
    # Real story character → consistent distinct voice (hashed by name).
    import hashlib
    pool = GUEST_VOICES.get(lang, GUEST_VOICES["hi"])
    idx  = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) % len(pool)
    return pool[idx]

# v2.7: warm, kid-friendly spoken outro (like/share/subscribe) added to the last
# scene's narration so it's voiced in the same soft kids voice + caption follows.
# v3.0: was ONE hardcoded line — every video ended with identical words (owner:
# "same lines on all videos"). Now a pool rotated by day (deterministic, so the
# full video + short rendered the same day match).
KIDS_CTA_POOL = {
    "hi": [
        (" Dosto, agar aapko Heroo ki yeh kahani achhi lagi toh, please LIKE karo, "
         "apne doston ke saath SHARE karo, aur channel SUBSCRIBE karna mat bhoolna! "
         "Milte hain agli kahani mein!"),
        (" Toh dosto, kahani mein maza aaya? Neeche LIKE dabao, apne best friend ko "
         "SHARE karo, aur nayi kahaniyon ke liye SUBSCRIBE zaroor karna. Kal phir "
         "milenge ek nayi kahani ke saath!"),
        (" Bolo dosto, aaj ki kahani se aapne kya seekha? Comment mein zaroor batana! "
         "LIKE aur SUBSCRIBE karna mat bhoolna — Heroo kal phir aayega ek aur "
         "zabardast kahani lekar!"),
        (" Agar aap chahte ho ki Heroo aur kahaniyan laaye, toh jaldi se LIKE karo "
         "aur SUBSCRIBE dabao! Apni family ke saath SHARE karna mat bhoolna. "
         "Milte hain agli kahani mein, tab tak muskurate raho!"),
        (" Kahani achhi lagi ho toh ek pyara sa LIKE toh banta hai dosto! SUBSCRIBE "
         "karke bell dabao taaki koi kahani miss na ho. Kal ki kahani aur bhi "
         "mazedaar hai — zaroor aana!"),
        (" Shabash dosto! Aaj ki seekh yaad rakhna. LIKE, SHARE aur SUBSCRIBE karke "
         "Heroo ka hausla badhao — agli kahani mein phir mulaqat hogi!"),
    ],
    "en": [
        (" Friends, if you loved Heroo's story, please give it a big LIKE, SHARE it "
         "with your friends, and don't forget to SUBSCRIBE! See you in the next story!"),
        (" So friends, did you enjoy the story? Hit LIKE, SHARE it with your best "
         "friend, and SUBSCRIBE for a brand-new story tomorrow!"),
        (" Tell me friends, what did you learn today? Write it in the comments! "
         "And don't forget to LIKE and SUBSCRIBE — Heroo returns tomorrow with "
         "another amazing story!"),
        (" If you want Heroo to bring more stories, quickly press LIKE and "
         "SUBSCRIBE! Share it with your family too. See you in the next story — "
         "keep smiling!"),
        (" If you liked the story, a big LIKE would make Heroo's day! SUBSCRIBE and "
         "press the bell so you never miss a story. Tomorrow's story is even more "
         "fun — do come!"),
        (" Well done friends! Remember today's lesson. LIKE, SHARE and SUBSCRIBE to "
         "cheer for Heroo — we meet again in the next story!"),
    ],
}

def _kids_cta(lang: str) -> str:
    pool = KIDS_CTA_POOL.get(lang, KIDS_CTA_POOL["hi"])
    return pool[date.today().toordinal() % len(pool)]

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
    import random
    # ── Per-episode STORY RECIPE — randomised so no two episodes feel the same.
    # The old prompt was identical every time (same arc, same "Oh no/Wow/Yay",
    # same catchphrase mechanic), so every video sounded alike. These knobs force
    # a fresh plot, tone and viewer-game each episode.
    portal = random.choice([
        "a glowing time-portal that drops Heroo and Arya right into the story",
        "a magical flying book whose pages open into the real place",
        "Heroo's wrist-gadget that zooms them down into the scene",
        "a friendly talking guide (an animal or spirit) who leads them through the tale",
        "a vivid dream where the whole story comes alive around them",
    ])
    shape = random.choice([
        "a mystery they solve clue by clue",
        "a race against time to help someone in need",
        "a funny misunderstanding that turns sweet by the end",
        "a brave rescue with a tense (but never scary) obstacle",
        "a friendly contest or challenge with a surprising winner",
        "a quiet, heart-warming journey about a big feeling",
    ])
    game = random.choice([
        "ask kids to shout the catchphrase along with Heroo",
        "ask kids to count something on screen out loud",
        "ask kids to guess what happens next before the reveal",
        "ask kids to copy an action — clap, roar, or jump",
        "ask kids to spot a hidden object in the scene",
    ])
    tone = random.choice([
        "funny and giggly", "exciting and adventurous",
        "warm and emotional", "curious and full of wonder",
    ])

    # v3.0: the calendar now supplies the REAL story outline — the AI's job is
    # to retell a beloved classic faithfully, not invent a thin plot. Fail-open
    # for topics without a seed.
    story_seed_block = ""
    if topic.get("story_seed"):
        story_seed_block = f"""
THE REAL STORY (a beloved classic — retell THIS story, faithfully and COMPLETELY):
{topic['story_seed']}
- Keep its actual events, characters, twist and ending exactly. Expand it with
  rich dialogue, feelings and detail — but do NOT replace the plot with an
  invented one and do NOT stop before its real ending.
- The "Story shape" in the recipe below only flavours HOW it is told (pacing,
  humour, suspense) — the events above always win.
"""

    prompt = f"""
You are a master children's cartoon writer (think Bluey, Gattu Battu, ChuChu TV).
Create a bilingual (Hindi + English) animated EPISODE.

Topic (Hindi): {topic['hindi_title']}
Topic (English): {topic['english_title']}
Category: {topic['category']}
Audience: children 4-12 years.
{story_seed_block}
THIS EPISODE'S UNIQUE RECIPE (follow it so this story is NOTHING like the last one):
- Way in: {portal}
- Story shape: {shape}
- Overall tone: {tone}
- Viewer moment: at least twice, {game}

COLD OPEN (scene 1 — the first 3 seconds decide if a child stays):
- Scene 1 must start INSIDE the story at its most dramatic, funny or mysterious
  moment — a shout, a gasp, a question, a problem ALREADY happening.
- The very FIRST spoken line must plant a question in the child's mind
  (e.g. "Rukooo! Woh gaay sone ke sikke de rahi hai?!").
- NEVER open with "hello", "namaste dosto", "aaj hum", "welcome", or the
  Narrator introducing the topic. Jump straight in; explain later.

WHO SPEAKS — make the TOPIC'S OWN CHARACTERS the heart of the story:
- The REAL figures from this topic MUST appear and SPEAK, using their real names
  as the "speaker" (e.g. Akbar/Birbal → "Akbar","Birbal"; Apollo 11 → "Neil",
  "Buzz"; Young Einstein → "Albert"; a volcano science topic → a "Professor" or
  the kids' own discovery). THEY drive the story — not Heroo.
- "Heroo": the brave, kind 10-year-old who ARRIVES via the way-in above to watch,
  ask, react and help. He is always on screen (he's the channel's hero) but he
  does NOT take over the real characters' story.
- "Arya": Heroo's curious 8-year-old friend who often comes along.
- "Narrator": warm storyteller — used SPARINGLY, just to set a scene.
- Use the real characters' names freely; each gets its own voice automatically.

MAKE IT FEEL ALIVE (most important):
- Tell the story through real CONVERSATION, mostly between the topic's own characters.
- Give every scene a small problem, question or surprise so kids lean in.
- Let feelings show through what characters SAY and DO — vary it, don't repeat the
  same few exclamations in every scene.
- Invent a FRESH catchphrase that fits THIS episode's tone ({tone}); do not reuse a
  generic one. Heroo can echo it a couple of times.
- Each dialogue line is a NATURAL full sentence or two (not 2-3 words), with real
  detail and feeling — and, for historical/religious/biography topics, faithful to
  the real story so kids actually LEARN something true.
- The story must feel COMPLETE: a proper beginning, a real middle with ups and
  downs, and a happy, well-earned ending. NEVER end abruptly. End with a clear,
  kind moral shown through ACTION.

Output ONLY valid JSON, no markdown:
{{
  "title_hi": "DRAMATIC Hindi title (Devanagari), 5-9 words, naming the story's conflict or twist so a child MUST click — like 'जादुई गाय और लालची पड़ोसी का अंत' — never a flat description",
  "title_en": "DRAMATIC English title, 5-9 words, same conflict/curiosity energy — like 'The Magical Cow and the Greedy Neighbour' — never a flat description",
  "thumbnail_hook": "2-4 word ULTRA-punchy HINGLISH hook (Hindi words in ENGLISH letters) for the thumbnail — e.g. 'JADUI GAAY?!', 'LALACH KI SAZA!', 'KAUN JEETEGA?', 'SONE KA RAAZ!' — emotion or question, NOT the full title",
  "thumbnail_question": "ONE short Hinglish curiosity question (max 6 words, English letters) that teases the story WITHOUT revealing the ending — e.g. 'Lalchi padosi ka kya hua?', 'Kya Heroo bacha payega?'",
  "scenes": [
    {{
      "id": 1,
      "dialogue": [
        {{"speaker": "Narrator", "hi": "1 short Hindi line", "en": "1 short English line"}},
        {{"speaker": "Heroo", "hi": "short Hindi line", "en": "short English line", "emotion": "excited"}},
        {{"speaker": "Arya", "hi": "short Hindi line", "en": "short English line"}}
      ],
      "image_prompt": "Specific visual: the topic's real characters AND Heroo (plus Arya) together in this scene's setting — their poses, expressions and the background. Very detailed for AI image generation.",
      "emotion": "excited",
      "transition": "fade"
    }}
  ],
  "moral_hi": "1 sentence Hindi moral",
  "moral_en": "1 sentence English moral",
  "seo_description_en": "60 word YouTube description with keywords mentioning Heroo"
}}

Rules:
- Create EXACTLY 8 scenes. Arc: arrive into the world (2), the problem/quest (2), the adventure (2), solve + moral (2).
- Each scene has 6-8 dialogue lines (a rich, real back-and-forth), about 55-75 seconds aloud.
  (The 3-line example above is ONLY a format sample — every real scene needs 6-8 lines.)
- The FINAL scene must give a clear, happy ENDING + the moral — never stop early.
- The topic's REAL characters speak the most; Heroo reacts/asks/helps in every scene;
  Arya joins often; Narrator rarely. Aim for 3-5 distinct speaking characters per episode.
- BOTH "hi" and "en" are required for EVERY dialogue line, each a full natural sentence.
- "thumbnail_hook" must be a 2-4 word punchy HINGLISH hook in ENGLISH letters
  (never Devanagari — the thumbnail font can't draw it); "thumbnail_question"
  likewise Hinglish in English letters, and it must NOT spoil the ending.
- Give the scene with the biggest moment a strong "emotion" (e.g. "shocked",
  "amazed", "scared", "excited") — the thumbnail is built from the most emotional scene.
"""
    # max_tokens raised so all 8 bilingual scenes (6-8 lines each) fit without
    # truncation — a cut-off last scene was making the story feel "half".
    # v3.0: 6000→8000 (richer dialogue + the story-seed block need headroom).
    return ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi", max_tokens=8000)


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
        img = ImageEnhance.Contrast(img).enhance(1.08)
        # 2. Saturation boost — vibrant but not blown-out candy
        img = ImageEnhance.Color(img).enhance(1.25)
        # 3. Brightness — cheerful but NOT washed out. The video also runs an
        #    eq pass, so this stays modest to avoid the over-bright look.
        img = ImageEnhance.Brightness(img).enhance(1.08)
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

        # KID-FRIENDLY colour: NEUTRAL pass — enhance_image_cinematic() already
        # grades each frame, so this no longer adds extra brightness/saturation
        # (that double pass made the in-video frames look washed-out / too bright,
        # while the thumbnail — which skips this eq — looked correct). Kept very
        # gentle so the video matches the thumbnail; NOT dark (anti-scary intact).
        color_filter = "eq=contrast=1.03:brightness=0.0:saturation=1.06:gamma=1.0"

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

async def _tts_one(text: str, voice: str, rate: str, pitch: str, out_path: Path):
    """Render ONE line in a specific voice/rate/pitch, with 503 retry.
    Edge TTS (wss://speech.platform.bing.com) intermittently returns 503 /
    WSServerHandshakeError; retry with backoff so a transient blip does not
    kill the whole workflow job (was causing hourly auto-heal re-runs)."""
    last_err = None
    for attempt in range(1, 5):  # 4 tries: ~0s, 5s, 15s, 30s backoff
        try:
            await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(str(out_path))
            if out_path.exists() and out_path.stat().st_size > 0:
                return
            raise RuntimeError("edge_tts produced empty audio file")
        except Exception as e:
            last_err = e
            print(f"  [TTS] attempt {attempt}/4 failed ({voice}): {e}")
            if attempt < 4:
                await asyncio.sleep([5, 15, 30][attempt - 1])
    raise RuntimeError(f"TTS failed after 4 attempts ({voice}): {last_err}")


async def generate_tts_async(text: str, lang: str, out_path: Path):
    """Single-voice render — fallback for non-dialogue scenes / safety path."""
    await _tts_one(text, VOICES.get(lang, VOICES["hi"]), "-10%", "+0Hz", out_path)

def generate_tts(text: str, lang: str, out_path: Path):
    asyncio.run(generate_tts_async(text, lang, out_path))


# ── v2.9 MULTI-VOICE DIALOGUE ──────────────────────────────────────────────────
_SILENCE_PATH = OUTPUT_DIR / "kids_gap_silence.mp3"

def _ensure_silence(gap: float = 0.32) -> bool:
    """A tiny silence clip inserted between speakers for natural dialogue rhythm."""
    if _SILENCE_PATH.exists() and _SILENCE_PATH.stat().st_size > 0:
        return True
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
             "-t", str(gap), "-c:a", "libmp3lame", "-q:a", "4", str(_SILENCE_PATH)],
            capture_output=True)
        return _SILENCE_PATH.exists() and _SILENCE_PATH.stat().st_size > 0
    except Exception:
        return False

def _concat_audio(parts: list, out_path: Path, gap: float = 0.32):
    """Concatenate per-line mp3s into one scene mp3 (re-encoded for a uniform
    stream), with a short pause between speakers."""
    parts = [p for p in parts if p and Path(p).exists() and Path(p).stat().st_size > 0]
    if not parts:
        raise RuntimeError("no audio parts to concat")
    if len(parts) == 1:
        r = subprocess.run(["ffmpeg", "-y", "-i", str(parts[0]),
                            "-c:a", "libmp3lame", "-q:a", "4", str(out_path)],
                           capture_output=True)
        if not (out_path.exists() and out_path.stat().st_size > 0):
            shutil.copyfile(parts[0], out_path)
        return
    use_gap = _ensure_silence(gap)
    listf = OUTPUT_DIR / f"{out_path.stem}_concat.txt"
    lines = []
    for i, p in enumerate(parts):
        if i > 0 and use_gap:
            lines.append(f"file '{_SILENCE_PATH.resolve().as_posix()}'")
        lines.append(f"file '{Path(p).resolve().as_posix()}'")
    listf.write_text("\n".join(lines), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf),
                    "-c:a", "libmp3lame", "-q:a", "4", str(out_path)], capture_output=True)
    if not (out_path.exists() and out_path.stat().st_size > 0):
        raise RuntimeError("ffmpeg concat produced no output")

def _scene_dialogue_lines(scene: dict, lang: str) -> list:
    """Extract [(speaker, text), ...] from a scene. Prefers the new 'dialogue'
    array; falls back to the old single-narration field so older / templated
    scripts still render (fail-safe)."""
    out = []
    dlg = scene.get("dialogue")
    if isinstance(dlg, list) and dlg:
        for d in dlg:
            if not isinstance(d, dict):
                continue
            speaker = (d.get("speaker") or "Narrator").strip()
            text = (d.get(lang) or d.get(f"text_{lang}") or d.get("text")
                    or d.get("hi") or d.get("en") or "").strip()
            if text:
                out.append((speaker, text))
    if not out:
        narr = (scene.get(f"narration_{lang}") or scene.get("narration_hi")
                or scene.get("narration_en") or "").strip()
        if narr:
            out.append(("Heroo", narr))
    return out

async def _render_dialogue_async(lines: list, lang: str, out_path: Path):
    part_paths = []
    for j, (speaker, text) in enumerate(lines):
        if not text or not text.strip():
            continue
        st = _speaker_style(speaker, lang)
        p = OUTPUT_DIR / f"{out_path.stem}_l{j:02d}.mp3"
        await _tts_one(text.strip(), st["voice"], st["rate"], st["pitch"], p)
        part_paths.append(p)
    if not part_paths:
        raise RuntimeError("no spoken dialogue lines")
    _concat_audio(part_paths, out_path)

def generate_tts_dialogue(lines: list, lang: str, out_path: Path):
    """lines: list of (speaker, text). Renders each line in its character's
    voice and concatenates into one scene audio file."""
    asyncio.run(_render_dialogue_async(lines, lang, out_path))


# ── v3.0 THUMBNAIL — emotional frame + punchy hook (CTR upgrade) ──────────────

# How "scroll-stopping" each emotion is. The thumbnail is built from the scene
# with the highest score — a big emotive frame beats the calm opening scene.
_EMO_AROUSAL = {
    "shocked": 10, "surprised": 9, "amazed": 9, "astonished": 9, "scared": 8,
    "afraid": 8, "worried": 7, "nervous": 7, "excited": 7, "thrilled": 7,
    "angry": 6, "curious": 6, "determined": 5, "proud": 5, "hopeful": 4,
    "happy": 4, "joyful": 4, "relieved": 3, "sad": 3, "thoughtful": 2,
    "calm": 1, "peaceful": 1,
}

def _pick_thumb_scene(scenes: list) -> int:
    """Index of the most emotionally intense scene (for the thumbnail base)."""
    best_i, best_score = 0, -1
    for i, sc in enumerate(scenes or []):
        if not isinstance(sc, dict):
            continue
        score = _EMO_AROUSAL.get(str(sc.get("emotion", "")).lower().strip(), 2)
        for d in (sc.get("dialogue") or []):
            if isinstance(d, dict):
                score = max(score, _EMO_AROUSAL.get(
                    str(d.get("emotion", "")).lower().strip(), 0))
        if i == 0:           # the intro scene is usually calm — nudge it down
            score -= 1
        if score > best_score:
            best_score, best_i = score, i
    return best_i


def make_thumbnail_multitext(
    title_hi: str, title_en: str, moral_en: str,
    episode_num: int, scene_img_path: Path, hook: str = "",
    question: str = ""
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

    # Robust bold font across CI (Linux DejaVu), Windows and macOS.
    _bold_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    def _kfont(sz):
        for p in _bold_paths:
            try:
                if os.path.exists(p):
                    return ImageFont.truetype(p, sz)
            except Exception:
                continue
        return ImageFont.load_default()
    f_brand, f_ep, f_title, f_sub, f_moral = _kfont(38), _kfont(34), _kfont(110), _kfont(64), _kfont(42)

    # HerooQuest brand (top left)
    draw.rounded_rectangle([(15,15),(260,65)], radius=14, fill=(220,30,30))
    # v3.0: "★" dropped — DejaVu/Arial Bold have no star glyph → hollow box
    draw.text((137,40), "HerooQuest", font=f_brand, fill=(255,255,255), anchor="mm")

    # Episode badge (top right area)
    ep_txt = f"Ep {episode_num}"
    draw.rounded_rectangle([(W-160,15),(W-15,65)], radius=14, fill=(255,200,0))
    draw.text((W-87,40), ep_txt, font=f_ep, fill=(0,0,0), anchor="mm")

    # Main title — HUGE yellow (most important element)
    # hook = short punchy thumbnail headline (falls back to the title)
    use_title = (hook or title_en or title_hi)
    safe_title= re.sub(r'[\u0900-\u097F]+','',use_title).strip().upper()
    if not safe_title: safe_title = "HEROOQUEST STORY"

    # Punchy hook → fewer words, BIGGER text (max 2 lines).
    title_lines = textwrap.wrap(safe_title, width=11)[:2]
    # v3.0: two-tone like the big kids channels — line 1 huge yellow, line 2
    # white — pops harder than a single-colour block.
    ty = 120
    for i, line in enumerate(title_lines):
        # Thick drop shadow for readability on any background
        for dx,dy in [(-4,4),(4,-4),(-4,-4),(4,4),(-4,0),(4,0),(0,4),(0,-4)]:
            draw.text((55+dx,ty+dy), line, font=f_title, fill=(0,0,0,235), anchor="la")
        draw.text((55,ty), line, font=f_title,
                  fill=(255,200,0) if i == 0 else (255,255,255), anchor="la")
        ty += 128

    # (Topic-name subtitle removed — it cluttered the frame and shrank the hook.)

    # v3.0: CURIOSITY QUESTION strip (Hinglish, from the AI) instead of the old
    # moral line - the moral SPOILED the ending right on the thumbnail
    # ('Patience wins over greed' tells the whole story); a question makes kids
    # click to find out. Falls back to the moral if no question. The lightbulb
    # emoji prefix was removed: DejaVu has no emoji glyphs - it rendered as a
    # hollow box on the CI runner.
    tease = re.sub(r'[\u0900-\u097F]+', '', (question or moral_en or '')).strip()[:50]
    if tease:
        strip_y = min(ty+10, H-100)
        draw.rectangle([(40,strip_y),(int(W*0.62),strip_y+58)], fill=(0,0,0,180))
        draw.rectangle([(40,strip_y),(46,strip_y+58)], fill=(255,60,60))
        draw.text((60,strip_y+29), tease, font=f_moral,
                  fill=(255,255,255), anchor='lm')

    thumb_path = OUTPUT_DIR / f"kids_thumb_{TODAY}.png"
    base.save(str(thumb_path), quality=95)
    print(f"[THUMB] ✅ Multi-text thumbnail: {thumb_path.name}")
    return thumb_path


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print(f"[HEROOQUEST v2.3] lang={LANG.upper()} output={KIDS_OUTPUT.upper()}")
    print(f"[TOPIC] {topic['hindi_title']} / {topic['english_title']}")

    # Generate script
    print("[SCRIPT] Generating story (8 scenes, seed-grounded)...")
    script = generate_script(topic)

    # v3.0: COMPLETENESS GUARD — a script with too few scenes or a thin final
    # scene reads as "story cut in half" (owner complaint). Retry ONCE with a
    # fresh random recipe; keep whichever attempt is stronger. Fail-open.
    def _script_strength(s):
        try:
            sc = s.get("scenes") or []
            return (len(sc), len((sc[-1].get("dialogue") or [])) if sc else 0)
        except Exception:
            return (0, 0)

    def _is_weak(s):
        n_scenes, last_lines = _script_strength(s)
        return n_scenes < 7 or last_lines < 3   # too short OR ending too thin

    if _is_weak(script):
        print(f"[SCRIPT] weak/incomplete script {_script_strength(script)} — retrying once with a fresh recipe")
        retry = generate_script(topic)
        if _script_strength(retry) > _script_strength(script):
            script = retry
            print(f"[SCRIPT] retry kept {_script_strength(script)}")

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
        is_last  = (_idx == len(scenes) - 1)

        # v2.9: build the spoken DIALOGUE lines for this scene (multi-voice).
        # Back-compat: a script with no "dialogue" falls back to narration.
        lines = _scene_dialogue_lines(scene, LANG)
        # v2.7: the soft spoken like/share/subscribe CTA on the LAST scene
        if is_last:
            lines.append(("Narrator", _kids_cta(LANG)))
        if not lines:
            lines = [("Heroo", "...")]
        # combined text drives the auto-translate .srt caption for the scene
        narr = " ".join(t for _, t in lines if t and t.strip())

        img_pr   = scene.get("image_prompt", "Heroo in an exciting adventure scene")
        print(f"[SCENE {sid}] {len(lines)} dialogue line(s) — generating image + voices...")
        img_p    = generate_scene_image(img_pr, sid)

        # v2.3: Enhance every image cinematically
        img_p    = enhance_image_cinematic(img_p)

        audio_p  = OUTPUT_DIR / f"kids_audio_{sid:02d}.mp3"
        try:
            generate_tts_dialogue(lines, LANG, audio_p)   # v2.9 multi-voice
        except Exception as e:
            print(f"  ⚠️ multi-voice render failed ({e}) — fallback to single voice")
            generate_tts(narr or "...", LANG, audio_p)
        img_paths.append(img_p)
        audio_paths.append(audio_p)
        narrations.append(narr)

    # v3.0: thumbnail from the MOST EMOTIONAL scene + Hinglish hook + a
    # curiosity question (never the spoiler moral).
    thumb_hook = (script.get("thumbnail_hook") or "").strip()
    thumb_q    = (script.get("thumbnail_question") or "").strip()
    thumb_idx  = _pick_thumb_scene(scenes)
    thumb_img  = img_paths[thumb_idx] if (img_paths and thumb_idx < len(img_paths)) else (img_paths[0] if img_paths else None)
    print(f"[THUMB] base = scene {thumb_idx+1} (most emotional) | hook = {thumb_hook or '(title)'} | q = {thumb_q or '(moral)'}")
    thumb_path = make_thumbnail_multitext(
        title_hi   = title_hi,
        title_en   = title_en,
        moral_en   = moral_en,
        episode_num= 1,
        scene_img_path = thumb_img,
        hook       = thumb_hook,
        question   = thumb_q,
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
