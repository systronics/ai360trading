"""
ai_client.py — Universal AI Client for AI360Trading
====================================================
Fallback chain: Groq → Gemini → Claude → OpenAI → Templates
Supports: text generation, future image/video generation (Gemini Veo roadmap)
Used by: ALL content generators — generate_reel.py, generate_shorts.py, etc.

Author: AI360Trading Automation
Last Updated: March 2026
"""

import os
import json
import time
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# PROVIDER CONFIG
# ─────────────────────────────────────────────

PROVIDERS = ["groq", "gemini", "claude", "openai"]

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
]

GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]

CLAUDE_MODELS = [
    "claude-haiku-4-5-20251001",   # fastest + cheapest
    "claude-sonnet-4-6",
]

OPENAI_MODELS = [
    "gpt-4o-mini",
    "gpt-3.5-turbo",
]


# ─────────────────────────────────────────────
# FALLBACK TEMPLATES
# ─────────────────────────────────────────────
# Used when ALL AI providers fail — guarantees content is always generated

FALLBACK_TEMPLATES = {
    "market": {
        "hook": [
            "Aaj ka market kuch interesting signal de raha hai!",
            "Smart money kahan ja raha hai? Dekhte hain!",
            "Nifty50 ka next move samajhna zaroori hai!",
            "Aaj ke trade setup pe nazar daalni chahiye!",
        ],
        "body": [
            "Market analysis ke liye apni strategy ready rakhein. Risk management sabse pehle.",
            "Technical levels pe nazar rakhein. Support aur resistance key hain.",
            "Volume confirm kare tab hi entry lein. Patience is key.",
        ],
        "cta": [
            "Like karo agar helpful laga! Telegram join karo signals ke liye.",
            "Share karo apne trading friends ke saath!",
            "Subscribe karo daily market updates ke liye!",
        ],
    },
    "weekend": {
        "hook": [
            "Weekend mein bhi seekhna band mat karo!",
            "Market band hai, but your growth nahi!",
            "Successful traders weekends mein bhi prepare karte hain!",
        ],
        "body": [
            "Is weekend ek naya concept seekho. Trading psychology bahut important hai.",
            "Charts study karo, mistakes review karo, next week ready raho.",
            "Wealth building ek marathon hai, sprint nahi. Consistent raho.",
        ],
        "cta": [
            "Apna feedback comments mein do!",
            "Telegram join karo exclusive content ke liye!",
            "Share karo — ek aur trader ki madad karo!",
        ],
    },
    "holiday": {
        "hook": [
            "Market band hai aaj — perfect time seekhne ka!",
            "Holiday mein bhi smart traders prepare karte hain!",
            "Rest karo, recharge karo, market kal phir aayega!",
        ],
        "body": [
            "Aaj apni trading journal review karo. Kya kaam kiya, kya nahi.",
            "Books padho, webinars dekho, fundamentals strong karo.",
            "Mental health trading success ka base hai. Aaj break lo!",
        ],
        "cta": [
            "Family ke saath time spend karo! Kal fresh mind se trade karo.",
            "Comment karo — aaj kya seekha?",
            "Subscribe karo regular updates ke liye!",
        ],
    },
    "english": {
        "hook": [
            "The market is sending signals — are you listening?",
            "Smart money is moving. Here's what you need to know.",
            "One chart pattern that changes everything today.",
            "Most traders miss this. Don't be one of them.",
        ],
        "body": [
            "Risk management is the foundation of every successful trade. Never risk more than 1-2% per trade.",
            "The trend is your friend until it ends. Always confirm with volume.",
            "Patience and discipline separate profitable traders from the rest.",
        ],
        "cta": [
            "Like and subscribe for daily market updates!",
            "Join our Telegram for live trading signals!",
            "Share this with a fellow trader!",
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
    """

    def __init__(self):
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.claude_key = os.environ.get("ANTHROPIC_API_KEY")
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.active_provider = None
        self.stats = {p: {"success": 0, "fail": 0} for p in PROVIDERS}

    # ── PUBLIC METHOD ──────────────────────────

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
        """
        Generate text with automatic fallback.
        Returns generated text or fallback template string.
        """
        # Build system prompt if not provided
        if system_prompt is None:
            system_prompt = self._default_system_prompt(lang, content_mode)

        # Try each provider in order
        for provider in PROVIDERS:
            try:
                result = self._try_provider(
                    provider, prompt, system_prompt,
                    max_tokens, temperature, json_mode
                )
                if result:
                    self.active_provider = provider
                    self.stats[provider]["success"] += 1
                    logger.info(f"✅ AI generated via {provider}")
                    return result
            except Exception as e:
                self.stats[provider]["fail"] += 1
                logger.warning(f"⚠️ {provider} failed: {e}")
                time.sleep(1)  # Brief pause before next provider
                continue

        # All providers failed — use template
        logger.error("❌ ALL AI providers failed. Using fallback template.")
        self.active_provider = "template"
        return self._get_fallback_template(content_mode, lang)

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        content_mode: str = "market",
        lang: str = "hi",
    ) -> dict:
        """Generate and parse JSON response."""
        raw = self.generate(
            prompt, system_prompt, content_mode, lang,
            json_mode=True, max_tokens=2000
        )
        try:
            # Strip markdown code fences if present
            clean = raw.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean.strip())
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed: {e}")
            return {}

    def get_status(self) -> dict:
        """Return current provider status for logging."""
        return {
            "active_provider": self.active_provider,
            "stats": self.stats,
            "available": {
                "groq": bool(self.groq_key),
                "gemini": bool(self.gemini_key),
                "claude": bool(self.claude_key),
                "openai": bool(self.openai_key),
            }
        }

    # ── PROVIDER METHODS ──────────────────────

    def _try_provider(self, provider, prompt, system_prompt, max_tokens, temperature, json_mode):
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
            raise ImportError("groq package not installed")

        client = Groq(api_key=self.groq_key)

        kwargs = {
            "model": GROQ_MODELS[0],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        # Try each Groq model in order
        for model in GROQ_MODELS:
            try:
                kwargs["model"] = model
                response = client.chat.completions.create(**kwargs)
                text = response.choices[0].message.content.strip()
                if text:
                    return text
            except Exception as e:
                logger.warning(f"Groq model {model} failed: {e}")
                continue
        raise Exception("All Groq models failed")

    def _gemini(self, prompt, system_prompt, max_tokens, temperature, json_mode):
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY not set")
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package not installed")

        genai.configure(api_key=self.gemini_key)

        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        full_prompt = f"{system_prompt}\n\n{prompt}"

        for model_name in GEMINI_MODELS:
            try:
                model = genai.GenerativeModel(
                    model_name,
                    generation_config=generation_config
                )
                response = model.generate_content(full_prompt)
                text = response.text.strip()
                if text:
                    return text
            except Exception as e:
                logger.warning(f"Gemini model {model_name} failed: {e}")
                continue
        raise Exception("All Gemini models failed")

    def _claude(self, prompt, system_prompt, max_tokens, temperature):
        if not self.claude_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package not installed")

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
                logger.warning(f"Claude model {model_name} failed: {e}")
                continue
        raise Exception("All Claude models failed")

    def _openai(self, prompt, system_prompt, max_tokens, temperature, json_mode):
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not set")
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed")

        client = OpenAI(api_key=self.openai_key)

        for model_name in OPENAI_MODELS:
            try:
                kwargs = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}

                response = client.chat.completions.create(**kwargs)
                text = response.choices[0].message.content.strip()
                if text:
                    return text
            except Exception as e:
                logger.warning(f"OpenAI model {model_name} failed: {e}")
                continue
        raise Exception("All OpenAI models failed")

    # ── HELPERS ───────────────────────────────

    def _default_system_prompt(self, lang: str, content_mode: str) -> str:
        if lang == "en":
            return (
                "You are a professional financial content creator for AI360Trading. "
                "Target audience: USA, UK, Australia, UAE, Canada, Brazil investors. "
                "Write in fluent, natural English. Sound like a knowledgeable human trader, "
                "not a robot. Use casual but professional tone. Include specific data points. "
                "Never use generic filler phrases. Every sentence must add value."
            )
        else:
            return (
                "Tum AI360Trading ke liye ek professional financial content creator ho. "
                "Target audience: Indian retail traders aur global NRI investors. "
                "Hindi-English mix (Hinglish) mein likho — natural aur conversational. "
                "Ek experienced trader ki tarah baat karo, robot ki tarah nahi. "
                "Specific data points use karo. Har sentence valuable hona chahiye."
            )

    def _get_fallback_template(self, content_mode: str, lang: str) -> str:
        mode = content_mode if content_mode in FALLBACK_TEMPLATES else "market"
        templates = FALLBACK_TEMPLATES["english"] if lang == "en" else FALLBACK_TEMPLATES[mode]

        hook = random.choice(templates["hook"])
        body = random.choice(templates["body"])
        cta = random.choice(templates["cta"])

        return f"{hook}\n\n{body}\n\n{cta}"


# ─────────────────────────────────────────────
# FUTURE: IMAGE & VIDEO GENERATION
# ─────────────────────────────────────────────
# Roadmap for Disney-style 3D reels:
#
# Phase 2 (3-6 months): Gemini Veo API
#   client.generate_video(prompt, style="cinematic")
#
# Phase 3 (6-12 months): Stable Diffusion + AnimateDiff
#   client.generate_frames(prompt, style="3d_disney", frames=30)
#
# Phase 4 (12-18 months): Google Veo 2 / OpenAI Sora
#   client.generate_video_hd(prompt, style="disney_3d", duration=60)
#
# All will be added as methods here — zero changes needed in generators.

class ImageVideoClient:
    """
    Placeholder for future image/video generation.
    Currently uses PIL-based generation via existing generators.
    Will be upgraded to Gemini Veo / Stable Diffusion when APIs stabilize.
    """

    def __init__(self):
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.phase = self._detect_phase()

    def _detect_phase(self) -> int:
        """Auto-detect which generation phase is available."""
        try:
            import google.generativeai as genai
            # Check if Veo is available
            return 2
        except ImportError:
            pass
        return 1  # PIL only

    def generate_thumbnail(self, title: str, mode: str = "market") -> Optional[str]:
        """
        Generate thumbnail image.
        Phase 1: PIL (current)
        Phase 2: Gemini Imagen (future)
        Returns path to generated image.
        """
        # Currently returns None — existing PIL code in generators handles this
        # TODO Phase 2: Implement Gemini Imagen generation
        logger.info(f"ImageVideoClient phase={self.phase} — using existing PIL pipeline")
        return None

    def generate_video_clip(self, prompt: str, duration: int = 5) -> Optional[str]:
        """
        Generate short video clip.
        Phase 2: Gemini Veo API
        Phase 3: Stable Diffusion + AnimateDiff
        Returns path to generated video clip.
        """
        # TODO Phase 2: Implement when Gemini Veo free tier available
        logger.info("Video generation not yet available — using PIL+MoviePy pipeline")
        return None


# ─────────────────────────────────────────────
# SINGLETON INSTANCE
# ─────────────────────────────────────────────
# Import this in all generators:
#   from ai_client import ai, img_client

ai = AIClient()
img_client = ImageVideoClient()


# ─────────────────────────────────────────────
# TEST / DEBUG
# ─────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("AI360Trading — AI Client Test")
    print("=" * 60)

    client = AIClient()

    # Test Hindi generation
    print("\n[TEST 1] Hindi market content:")
    result = client.generate(
        prompt="Aaj Nifty50 ke liye ek 3-line trading insight likho.",
        content_mode="market",
        lang="hi"
    )
    print(result)

    # Test English generation
    print("\n[TEST 2] English global content:")
    result = client.generate(
        prompt="Write a 3-line trading insight for today's global market.",
        content_mode="market",
        lang="en"
    )
    print(result)

    # Test JSON generation
    print("\n[TEST 3] JSON generation:")
    result = client.generate_json(
        prompt='Return a JSON with keys "hook", "body", "cta" for a trading reel script.',
        content_mode="market",
        lang="hi"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Status
    print("\n[STATUS]")
    print(json.dumps(client.get_status(), indent=2))
