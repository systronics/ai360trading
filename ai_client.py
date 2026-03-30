"""
ai_client.py — Universal AI Client for AI360Trading
====================================================
Fallback chain: Groq → Gemini → Claude → OpenAI → Templates
Supports: text generation, JSON generation.

FIX (March 2026):
  - Replaced deprecated google.generativeai with google.genai (new SDK)
  - generate_json() max_tokens bumped to 3000 for Dream11 5-team JSON
  - Gemini model list updated to latest available

Author: AI360Trading Automation
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
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
]

OPENAI_MODELS = [
    "gpt-4o-mini",
    "gpt-3.5-turbo",
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

    # ── PUBLIC METHODS ─────────────────────────

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
        """Generate text with automatic provider fallback."""
        if system_prompt is None:
            system_prompt = self._default_system_prompt(lang, content_mode)

        for provider in PROVIDERS:
            try:
                result = self._try_provider(
                    provider, prompt, system_prompt,
                    max_tokens, temperature, json_mode,
                )
                if result:
                    self.active_provider = provider
                    self.stats[provider]["success"] += 1
                    logger.info(f"✅ AI generated via {provider}")
                    return result
            except Exception as e:
                self.stats[provider]["fail"] += 1
                logger.warning(f"⚠️ {provider} failed: {e}")
                time.sleep(1)

        logger.error("❌ ALL AI providers failed — using fallback template.")
        self.active_provider = "template"
        return self._get_fallback_template(content_mode, lang)

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        content_mode: str = "market",
        lang: str = "hi",
    ) -> dict:
        """Generate and parse a JSON response."""
        raw = self.generate(
            prompt, system_prompt, content_mode, lang,
            json_mode=True,
            max_tokens=3000,   # bumped for 5-team Dream11 output
        )
        try:
            clean = raw.strip()
            # Strip markdown code fences if present
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
            "stats": self.stats,
            "available": {
                "groq":   bool(self.groq_key),
                "gemini": bool(self.gemini_key),
                "claude": bool(self.claude_key),
                "openai": bool(self.openai_key),
            },
        }

    # ── PROVIDER DISPATCH ─────────────────────

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

    # ── GROQ ──────────────────────────────────

    def _groq(self, prompt, system_prompt, max_tokens, temperature, json_mode):
        if not self.groq_key:
            raise ValueError("GROQ_API_KEY not set")
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("groq package not installed — pip install groq")

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

    # ── GEMINI ────────────────────────────────
    # FIX: uses new google.genai SDK instead of deprecated google.generativeai

    def _gemini(self, prompt, system_prompt, max_tokens, temperature, json_mode):
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY not set")

        # Try new SDK first (google.genai), fall back to old SDK
        try:
            return self._gemini_new_sdk(prompt, system_prompt, max_tokens, temperature, json_mode)
        except ImportError:
            pass

        try:
            return self._gemini_old_sdk(prompt, system_prompt, max_tokens, temperature, json_mode)
        except ImportError:
            raise ImportError(
                "Neither google-genai nor google-generativeai installed.\n"
                "Run: pip install google-genai"
            )

    def _gemini_new_sdk(self, prompt, system_prompt, max_tokens, temperature, json_mode):
        """Uses the new google.genai SDK (google-genai package)."""
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.gemini_key)
        full_prompt = f"{system_prompt}\n\n{prompt}"

        generate_config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        if json_mode:
            generate_config.response_mime_type = "application/json"

        for model_name in GEMINI_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                    config=generate_config,
                )
                text = response.text.strip()
                if text:
                    return text
            except Exception as e:
                logger.warning(f"Gemini (new SDK) {model_name}: {e}")

        raise Exception("All Gemini models failed (new SDK)")

    def _gemini_old_sdk(self, prompt, system_prompt, max_tokens, temperature, json_mode):
        """Fallback: old google.generativeai SDK (deprecated but still works)."""
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
                logger.warning(f"Gemini (old SDK) {model_name}: {e}")

        raise Exception("All Gemini models failed (old SDK)")

    # ── CLAUDE ────────────────────────────────

    def _claude(self, prompt, system_prompt, max_tokens, temperature):
        if not self.claude_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package not installed — pip install anthropic")

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

    # ── OPENAI ────────────────────────────────

    def _openai(self, prompt, system_prompt, max_tokens, temperature, json_mode):
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not set")
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed — pip install openai")

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

    # ── HELPERS ───────────────────────────────

    def _default_system_prompt(self, lang: str, content_mode: str) -> str:
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
# FUTURE: IMAGE & VIDEO GENERATION (placeholder)
# ─────────────────────────────────────────────

class ImageVideoClient:
    """
    Placeholder for future image/video generation.
    Phase 1 (now): PIL-based via existing generators.
    Phase 2: Gemini Imagen / Veo when APIs stabilise.
    """

    def __init__(self):
        self.gemini_key = os.environ.get("GEMINI_API_KEY")

    def generate_thumbnail(self, title: str, mode: str = "market") -> Optional[str]:
        logger.info("ImageVideoClient: using existing PIL pipeline")
        return None

    def generate_video_clip(self, prompt: str, duration: int = 5) -> Optional[str]:
        logger.info("Video generation not yet available — using PIL+MoviePy pipeline")
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
    print("AI360Trading — AI Client Test")
    print("=" * 60)

    client = AIClient()

    print("\n[TEST 1] Hindi market content:")
    print(client.generate("Aaj Nifty50 ke liye ek 3-line trading insight likho.",
                          content_mode="market", lang="hi"))

    print("\n[TEST 2] English global content:")
    print(client.generate("Write a 3-line trading insight for today's global market.",
                          content_mode="market", lang="en"))

    print("\n[TEST 3] JSON generation:")
    result = client.generate_json(
        prompt='Return JSON with keys "hook","body","cta" for a trading reel script.',
        content_mode="market", lang="hi",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n[STATUS]")
    print(json.dumps(client.get_status(), indent=2))
