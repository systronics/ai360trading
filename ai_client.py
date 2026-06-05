"""
ai_client.py — Universal AI Client for AI360Trading
====================================================
Fallback chain (default): Groq → Gemini → FREE Templates.
Claude/OpenAI (PAID) only added when ALLOW_PAID_AI=true.

v2.5 CHANGES (2026-05-31) — FREE-TIER HARDENING (₹0/month invariant):
  Paid providers (Claude, OpenAI) are now OFF by default. The chain only uses
  the free providers (Groq, Gemini) then free templates, guaranteeing zero
  spend. Set env/Secret ALLOW_PAID_AI=true to re-enable paid last-resort
  fallback. Each paid call (when enabled) logs a clear cost warning.
  get_status() now reports allow_paid_ai + hides paid keys when disabled.

v2.4 CHANGES (May 2026):
  Fixed decommissioned Groq models:
    REMOVED: llama-3.1-70b-versatile (decommissioned)
    REMOVED: mixtral-8x7b-32768 (decommissioned)
    ADDED:   llama-3.1-8b-instant (fast, free, current)
    ADDED:   gemma2-9b-it (Google model via Groq, free)
    ADDED:   qwen-qwq-32b (strong reasoning, free)

  Also added Gemini 2.5 models (better rate limits):
    ADDED:   gemini-2.5-flash (new, higher free tier)
    ADDED:   gemini-2.5-flash-8b

  These fixes prevent the cascading failure where all
  4 providers fail and system falls back to generic templates.

v2.3 CHANGES:
  Added real video generation to ImageVideoClient
  Added education system prompt (no trading language)

Author: AI360Trading Automation
Last Updated: May 2026
"""

import os
import json
import time
import random
import logging
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# PROVIDER CONFIG
# ─────────────────────────────────────────────

PROVIDERS = ["groq", "gemini", "claude", "openai"]

# ─── FREE-TIER HARDENING (₹0/month invariant) ───────────────────────────────
# Groq + Gemini are FREE. Claude + OpenAI are PAID. To guarantee zero spend by
# default, paid providers are OFF unless ALLOW_PAID_AI is explicitly enabled.
# With paid off, the chain is Groq → Gemini → free templates (still fail-open,
# content always publishes, just template-quality on the rare day both free
# providers are down). Set GitHub Secret/env ALLOW_PAID_AI=true to re-enable
# Claude/OpenAI as a last-resort paid fallback.
FREE_PROVIDERS = ("groq", "gemini")
PAID_PROVIDERS = ("claude", "openai")
ALLOW_PAID_AI  = os.environ.get("ALLOW_PAID_AI", "").strip().lower() in ("1", "true", "yes", "on")

# v2.4: Updated Groq models — removed decommissioned ones
GROQ_MODELS = [
    "llama-3.3-70b-versatile",   # Primary — best quality, free
    "llama-3.1-8b-instant",       # Fast fallback — free, current
    "gemma2-9b-it",               # Google model via Groq — free, current
    "qwen-qwq-32b",               # Strong reasoning — free, current
]

# v2.4: Added Gemini 2.5 models with higher free tier limits
GEMINI_MODELS = [
    "gemini-2.5-flash",           # New — higher free limits
    "gemini-2.0-flash",           # Existing
    "gemini-2.5-flash-8b",        # Fast fallback
]

CLAUDE_MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
]

OPENAI_MODELS = [
    "gpt-4o-mini",
    "gpt-3.5-turbo",
]

# HuggingFace video models — free, in order of quality
HF_VIDEO_MODELS = [
    "Wan-AI/Wan2.2-T2V-14B",
    "Wan-AI/Wan2.1-T2V-14B",
    "Lightricks/LTX-Video",
]

# ─────────────────────────────────────────────
# FALLBACK TEMPLATES
# ─────────────────────────────────────────────

FALLBACK_TEMPLATES = {
    "market": {
        "hook": [
            "Aaj ka market kuch interesting signal de raha hai!",
            "Smart money kahan ja raha hai? Dekhte hain!",
            "Nifty50 ka next move samajhna zaroori hai!",
        ],
        "body": [
            "Market analysis ke liye apni strategy ready rakhein. Risk management sabse pehle.",
            "Technical levels pe nazar rakhein. Support aur resistance key hain.",
        ],
        "cta": [
            "Like karo agar helpful laga! Telegram join karo signals ke liye.",
            "Share karo apne trading friends ke saath!",
        ],
    },
    "weekend": {
        "hook": [
            "Weekend mein bhi seekhna band mat karo!",
            "Market band hai, but your growth nahi!",
        ],
        "body": [
            "Is weekend ek naya concept seekho. Trading psychology bahut important hai.",
            "Charts study karo, mistakes review karo, next week ready raho.",
        ],
        "cta": [
            "Apna feedback comments mein do!",
            "Telegram join karo exclusive content ke liye!",
        ],
    },
    "holiday": {
        "hook": [
            "Market band hai aaj — perfect time seekhne ka!",
            "Holiday mein bhi smart traders prepare karte hain!",
        ],
        "body": [
            "Aaj apni trading journal review karo. Kya kaam kiya, kya nahi.",
            "Mental health trading success ka base hai. Aaj break lo!",
        ],
        "cta": [
            "Family ke saath time spend karo! Kal fresh mind se trade karo.",
            "Subscribe karo regular updates ke liye!",
        ],
    },
    "english": {
        "hook": [
            "The market is sending signals — are you listening?",
            "Smart money is moving. Here's what you need to know.",
        ],
        "body": [
            "Risk management is the foundation of every successful trade.",
            "The trend is your friend until it ends. Confirm with volume.",
        ],
        "cta": [
            "Like and subscribe for daily market updates!",
            "Join our Telegram for live trading signals!",
        ],
    },
}


# ─────────────────────────────────────────────
# CORE AI CLIENT CLASS
# ─────────────────────────────────────────────

class AIClient:
    """
    Universal AI client with automatic fallback chain.
    Usage:
        client = AIClient()
        response = client.generate(prompt, content_mode="market", lang="hi")
        data     = client.generate_json(prompt, system_prompt=..., lang="en")
    """

    def __init__(self):
        self.groq_key   = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.claude_key = os.environ.get("ANTHROPIC_API_KEY")
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.active_provider = None
        self.stats = {p: {"success": 0, "fail": 0} for p in PROVIDERS}

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        content_mode: str = "market",
        lang: str = "hi",
        max_tokens: int = 1500,
        temperature: float = 0.85,
        json_mode: bool = False,
    ) -> str:
        if system_prompt is None:
            system_prompt = self._default_system_prompt(lang, content_mode)

        # ₹0 invariant: only try paid providers if explicitly allowed.
        providers = list(FREE_PROVIDERS) + (list(PAID_PROVIDERS) if ALLOW_PAID_AI else [])

        for provider in providers:
            if provider in PAID_PROVIDERS:
                logger.warning(
                    f"Free AI providers exhausted — falling back to PAID provider "
                    f"'{provider}' (ALLOW_PAID_AI is enabled; this costs money)."
                )
            try:
                result = self._try_provider(
                    provider, prompt, system_prompt,
                    max_tokens, temperature, json_mode,
                )
                if result:
                    self.active_provider = provider
                    self.stats[provider]["success"] += 1
                    logger.info(f"AI generated via {provider}")
                    return result
            except Exception as e:
                self.stats[provider]["fail"] += 1
                logger.warning(f"{provider} failed: {e}")
                time.sleep(1)

        if not ALLOW_PAID_AI:
            logger.error("Free AI providers (Groq, Gemini) failed — using FREE template "
                         "(paid Claude/OpenAI disabled by default; set ALLOW_PAID_AI=true to enable).")
        else:
            logger.error("ALL AI providers failed — using fallback template.")
        self.active_provider = "template"
        return self._get_fallback_template(content_mode, lang)

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        content_mode: str = "market",
        lang: str = "hi",
        max_tokens: int = 4000,
    ) -> dict:
        # max_tokens is overridable (default 4000 — unchanged for existing
        # callers) so large structured outputs (e.g. a 8-scene bilingual kids
        # story with 6-8 dialogue lines each) don't get truncated mid-JSON.
        raw = self.generate(
            prompt, system_prompt, content_mode, lang,
            json_mode=True,
            max_tokens=max_tokens,
        )
        try:
            clean = raw.strip()
            if clean.startswith("```"):
                parts = clean.split("```")
                clean = parts[1] if len(parts) > 1 else clean
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean.strip())
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed: {e}\nRaw (first 300): {raw[:300]}")
            return {}

    def get_status(self) -> dict:
        return {
            "active_provider": self.active_provider,
            "allow_paid_ai": ALLOW_PAID_AI,
            "stats": self.stats,
            "available": {
                "groq":   bool(self.groq_key),
                "gemini": bool(self.gemini_key),
                "claude": bool(self.claude_key) if ALLOW_PAID_AI else False,
                "openai": bool(self.openai_key) if ALLOW_PAID_AI else False,
            },
        }

    def _try_provider(self, provider, prompt, system_prompt,
                      max_tokens, temperature, json_mode):
        if provider == "groq":
            return self._groq(prompt, system_prompt, max_tokens, temperature, json_mode)
        elif provider == "gemini":
            return self._gemini(prompt, system_prompt, max_tokens, temperature, json_mode)
        elif provider == "claude":
            return self._claude(prompt, system_prompt, max_tokens, temperature)
        elif provider == "openai":
            return self._openai(prompt, system_prompt, max_tokens, temperature, json_mode)
        return None

    def _groq(self, prompt, system_prompt, max_tokens, temperature, json_mode):
        if not self.groq_key:
            raise ValueError("GROQ_API_KEY not set")
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("groq not installed")

        client = Groq(api_key=self.groq_key)
        for model in GROQ_MODELS:
            try:
                kwargs = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": prompt},
                    ],
                    "max_tokens":  max_tokens,
                    "temperature": temperature,
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                resp = client.chat.completions.create(**kwargs)
                text = resp.choices[0].message.content.strip()
                if text:
                    return text
            except Exception as e:
                logger.warning(f"Groq {model}: {e}")
        raise Exception("All Groq models failed")

    def _gemini(self, prompt, system_prompt, max_tokens, temperature, json_mode):
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY not set")
        try:
            return self._gemini_new_sdk(prompt, system_prompt, max_tokens, temperature, json_mode)
        except ImportError:
            pass
        try:
            return self._gemini_old_sdk(prompt, system_prompt, max_tokens, temperature, json_mode)
        except ImportError:
            raise ImportError("Neither google-genai nor google-generativeai installed.")

    def _gemini_new_sdk(self, prompt, system_prompt, max_tokens, temperature, json_mode):
        from google import genai
        from google.genai import types

        client      = genai.Client(api_key=self.gemini_key)
        full_prompt = f"{system_prompt}\n\n{prompt}"
        config      = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        if json_mode:
            config.response_mime_type = "application/json"

        for model_name in GEMINI_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name, contents=full_prompt, config=config,
                )
                text = response.text.strip()
                if text:
                    return text
            except Exception as e:
                logger.warning(f"Gemini new SDK {model_name}: {e}")
        raise Exception("All Gemini models failed (new SDK)")

    def _gemini_old_sdk(self, prompt, system_prompt, max_tokens, temperature, json_mode):
        import warnings
        warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
        import google.generativeai as genai

        genai.configure(api_key=self.gemini_key)
        full_prompt = f"{system_prompt}\n\n{prompt}"
        gen_config  = {"max_output_tokens": max_tokens, "temperature": temperature}
        if json_mode:
            gen_config["response_mime_type"] = "application/json"

        for model_name in GEMINI_MODELS:
            try:
                model    = genai.GenerativeModel(model_name, generation_config=gen_config)
                response = model.generate_content(full_prompt)
                text     = response.text.strip()
                if text:
                    return text
            except Exception as e:
                logger.warning(f"Gemini old SDK {model_name}: {e}")
        raise Exception("All Gemini models failed (old SDK)")

    def _claude(self, prompt, system_prompt, max_tokens, temperature):
        if not self.claude_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic not installed")

        client = anthropic.Anthropic(api_key=self.claude_key)
        for model_name in CLAUDE_MODELS:
            try:
                message = client.messages.create(
                    model=model_name,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = message.content[0].text.strip()
                if text:
                    return text
            except Exception as e:
                logger.warning(f"Claude {model_name}: {e}")
        raise Exception("All Claude models failed")

    def _openai(self, prompt, system_prompt, max_tokens, temperature, json_mode):
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not set")
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai not installed")

        client = OpenAI(api_key=self.openai_key)
        for model_name in OPENAI_MODELS:
            try:
                kwargs = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": prompt},
                    ],
                    "max_tokens":  max_tokens,
                    "temperature": temperature,
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                resp = client.chat.completions.create(**kwargs)
                text = resp.choices[0].message.content.strip()
                if text:
                    return text
            except Exception as e:
                logger.warning(f"OpenAI {model_name}: {e}")
        raise Exception("All OpenAI models failed")

    def _default_system_prompt(self, lang: str, content_mode: str) -> str:
        if content_mode == "education":
            if lang == "hi":
                return (
                    "Tum AI360Trading ke liye ek friendly financial teacher ho — "
                    "52-week investing course YouTube pe padhate ho. "
                    "Simple Hinglish mein samjhao jaise ek dost samjhata hai. "
                    "KABHI USE MAT KARO: 'aaj ka market', 'chart pattern', 'breakout signal', 'trade setup'. "
                    "ZAROOR USE KARO: 'yeh concept', 'samjhate hain', 'example ke taur pe'. "
                    "Real Indian company examples do (Reliance, TCS, HDFC, Infosys)."
                )
            return (
                "You are a friendly financial educator for AI360Trading — "
                "teaching a 52-week investing course on YouTube. "
                "Explain like a knowledgeable friend, simple English for beginners. "
                "NEVER USE: 'today's market', 'chart pattern', 'breakout signal', 'trade setup'. "
                "DO USE: 'this concept', 'let me explain', 'for example'. "
                "Include real Indian company examples (Reliance, TCS, HDFC)."
            )
        if lang == "en":
            return (
                "You are a professional financial content creator for AI360Trading. "
                "Target audience: USA, UK, Australia, UAE, Canada investors. "
                "Write in fluent natural English. Sound like a knowledgeable human trader. "
                "Use casual but professional tone. Include specific data points. "
                "Never use generic filler. Every sentence must add value."
            )
        return (
            "Tum AI360Trading ke liye ek professional financial content creator ho. "
            "Target audience: Indian retail traders aur global NRI investors. "
            "Hindi-English mix (Hinglish) mein likho — natural aur conversational. "
            "Ek experienced trader ki tarah baat karo. Specific data points use karo."
        )

    def _get_fallback_template(self, content_mode: str, lang: str) -> str:
        mode      = content_mode if content_mode in FALLBACK_TEMPLATES else "market"
        templates = FALLBACK_TEMPLATES["english"] if lang == "en" else FALLBACK_TEMPLATES[mode]
        hook = random.choice(templates["hook"])
        body = random.choice(templates["body"])
        cta  = random.choice(templates["cta"])
        return f"{hook}\n\n{body}\n\n{cta}"


# ─────────────────────────────────────────────
# IMAGE & VIDEO GENERATION CLIENT
# ─────────────────────────────────────────────

class ImageVideoClient:
    """
    Image and video generation with fallback chain.

    Video fallback chain (v2.3+):
      1. Google Veo 2 via GEMINI_API_KEY (~50 free/day)
      2. HuggingFace Wan-2.2 via HF_TOKEN (free unlimited)
      3. Stability AI image-to-video via STABILITY_API_KEY
      4. PIL+MoviePy placeholder (always works)
    """

    def __init__(self):
        self.gemini_key    = os.environ.get("GEMINI_API_KEY")
        self.hf_token      = os.environ.get("HF_TOKEN")
        self.stability_key = os.environ.get("STABILITY_API_KEY")
        self.openai_key    = os.environ.get("OPENAI_API_KEY")

    def generate_thumbnail(self, title: str, mode: str = "market") -> Optional[str]:
        logger.info("Thumbnails generated by PIL pipeline in each generator")
        return None

    def generate_video_clip(
        self,
        prompt: str,
        duration: int = 8,
        aspect_ratio: str = "9:16",
        output_path: Optional[str] = None,
        reference_image_path: Optional[str] = None,
    ) -> Optional[str]:
        if output_path is None:
            output_path = str(Path("output") / f"clip_{int(time.time())}.mp4")

        style_prefix = (
            "3D CGI animation, Pixar Disney quality, cinematic lighting, "
            "vibrant colors, child-friendly, professional render. "
        )
        styled_prompt = style_prefix + prompt

        result = self._veo2(styled_prompt, duration, aspect_ratio, output_path)
        if result: return result

        result = self._huggingface_video(styled_prompt, duration, aspect_ratio, output_path)
        if result: return result

        if reference_image_path and os.path.exists(reference_image_path):
            result = self._stability_video(reference_image_path, output_path)
            if result: return result

        return self._pil_placeholder(prompt, duration, aspect_ratio, output_path)

    def _veo2(self, prompt, duration, aspect_ratio, output_path):
        if not self.gemini_key: return None
        try:
            from google import genai
            from google.genai import types

            client    = genai.Client(api_key=self.gemini_key)
            logger.info(f"[Veo2] Generating {duration}s {aspect_ratio} video...")
            operation = client.models.generate_video(
                model="veo-2.0-generate-001",
                prompt=prompt,
                config=types.GenerateVideoConfig(
                    duration_seconds=min(duration, 8),
                    aspect_ratio=aspect_ratio,
                    number_of_videos=1,
                ),
            )
            max_wait = 180; waited = 0
            while not operation.done and waited < max_wait:
                time.sleep(10); waited += 10
                operation = client.operations.get(operation)

            if not operation.done: return None

            video_bytes = operation.response.generated_videos[0].video.video_bytes
            with open(output_path, "wb") as f: f.write(video_bytes)
            if os.path.getsize(output_path) > 1000: return output_path
        except Exception as e:
            logger.warning(f"[Veo2] {e}")
        return None

    def _huggingface_video(self, prompt, duration, aspect_ratio, output_path):
        if not self.hf_token: return None
        try:
            import requests
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "num_frames": duration * 8,
                    "width":  1080 if aspect_ratio == "9:16" else 1280,
                    "height": 1920 if aspect_ratio == "9:16" else 720,
                }
            }
            for model in HF_VIDEO_MODELS:
                try:
                    r = requests.post(
                        f"https://api-inference.huggingface.co/models/{model}",
                        headers=headers, json=payload, timeout=300,
                    )
                    if r.status_code == 200:
                        ct = r.headers.get("content-type", "")
                        if "video" in ct or "octet" in ct:
                            with open(output_path, "wb") as f: f.write(r.content)
                            if os.path.getsize(output_path) > 1000: return output_path
                    elif r.status_code == 503:
                        time.sleep(20)
                except Exception as e:
                    logger.warning(f"[HF] {model}: {e}")
        except Exception as e:
            logger.warning(f"[HF] {e}")
        return None

    def _stability_video(self, image_path, output_path):
        if not self.stability_key: return None
        try:
            import requests
            with open(image_path, "rb") as f:
                r = requests.post(
                    "https://api.stability.ai/v2beta/image-to-video",
                    headers={"Authorization": f"Bearer {self.stability_key}"},
                    data={"seed": 0, "cfg_scale": 1.8, "motion_bucket_id": 127},
                    files={"image": f}, timeout=60,
                )
            if r.status_code != 200: return None
            gen_id = r.json().get("id")
            if not gen_id: return None

            for _ in range(18):
                time.sleep(10)
                poll = requests.get(
                    f"https://api.stability.ai/v2beta/image-to-video/result/{gen_id}",
                    headers={"Authorization": f"Bearer {self.stability_key}", "Accept": "video/*"},
                    timeout=30,
                )
                if poll.status_code == 200:
                    with open(output_path, "wb") as f: f.write(poll.content)
                    if os.path.getsize(output_path) > 1000: return output_path
                elif poll.status_code != 202:
                    break
        except Exception as e:
            logger.warning(f"[Stability] {e}")
        return None

    def _pil_placeholder(self, prompt, duration, aspect_ratio, output_path):
        try:
            from PIL import Image, ImageDraw, ImageFont
            from moviepy.editor import ImageClip

            W = 1080 if aspect_ratio == "9:16" else 1280
            H = 1920 if aspect_ratio == "9:16" else 720
            img  = Image.new("RGB", (W, H), (10, 20, 50))
            draw = ImageDraw.Draw(img)
            for y in range(H):
                t = y/H
                draw.line([(0,y),(W,y)], fill=(int(10+t*20),int(20+t*40),int(50+t*80)))
            draw.rectangle([(0,0),(W,12)], fill=(0,180,255))
            draw.rectangle([(0,H-12),(W,H)], fill=(0,180,255))
            try:
                fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
                fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
            except:
                fb = fs = ImageFont.load_default()
            draw.text((W//2, H//2-60), "AI360TRADING", font=fb, fill=(0,180,255), anchor="mm")
            draw.text((W//2, H//2+40), "Video generating...", font=fs, fill=(200,220,255), anchor="mm")
            img.save("/tmp/placeholder.png")
            ImageClip("/tmp/placeholder.png").set_duration(duration).write_videofile(
                output_path, fps=24, codec="libx264", audio=False, verbose=False, logger=None
            )
            return output_path
        except Exception as e:
            logger.error(f"[Placeholder] {e}")
        return None

    def generate_scene_image(self, prompt, scene_id, output_dir="output"):
        logger.info(f"[IMG] Scene {scene_id} — using generator's own pipeline")
        return None

    def generate_background(self, stock, sentiment="positive", style="3d"):
        if not self.stability_key: return None
        try:
            import requests, base64
            prompt = (
                f"Abstract financial trading background for {stock} stock. "
                f"Sentiment: {sentiment}. Style: {style} render. "
                f"Dark blue and gold, professional, no text, no people."
            )
            r = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={"Authorization": f"Bearer {self.stability_key}", "Content-Type": "application/json"},
                json={"text_prompts": [{"text": prompt, "weight": 1}],
                      "cfg_scale": 7, "width": 1024, "height": 1024, "samples": 1, "steps": 30},
                timeout=60,
            )
            if r.status_code == 200:
                out = f"/tmp/bg_{stock}_{int(time.time())}.png"
                with open(out, "wb") as f:
                    f.write(base64.b64decode(r.json()["artifacts"][0]["base64"]))
                return out
        except Exception as e:
            logger.warning(f"[BG] {e}")
        return None


# ─────────────────────────────────────────────
# SINGLETON INSTANCES
# ─────────────────────────────────────────────

ai         = AIClient()
img_client = ImageVideoClient()


# ─────────────────────────────────────────────
# TEST / DEBUG
# ─────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=" * 60)
    print("AI360Trading — AI Client v2.4 Test")
    print("=" * 60)

    client = AIClient()

    print("\n[TEST 1] Hindi market content:")
    print(client.generate("Aaj Nifty50 ke liye ek 3-line trading insight likho.",
                          content_mode="market", lang="hi"))

    print("\n[TEST 2] Education mode (no trading language):")
    print(client.generate("Stock market kya hai? 3 lines mein samjhao.",
                          content_mode="education", lang="hi"))

    print("\n[STATUS]")
    print(json.dumps(client.get_status(), indent=2))
