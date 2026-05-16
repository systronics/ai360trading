"""
ai_client.py — Universal AI Client for AI360Trading
====================================================
Fallback chain: Groq → Gemini → Claude → OpenAI → Templates

v2.2 CHANGES (May 2026):
- _default_system_prompt() — education mode added
  Education prompts get teacher/educator persona, NOT trading persona
  Fixes: education video starting with "chart kabhie jhooth nahi bolta"
- _education_system_prompt() — dedicated clean education persona
- generate_with_stock_data() — new method that locks stock numbers
  AI receives numbers as "EXACT — DO NOT CHANGE"
  Fixes: SL 1457 being written as 145.7 in AI output
- ImageVideoClient — Stability AI image generation added
  generate_background() uses STABILITY_API_KEY for 3D-style backgrounds
  Used by generate_shorts.py for premium-looking visuals

Author: AI360Trading Automation
Last Updated: May 2026
"""

import os
import json
import time
import random
import logging
import base64
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
    "education": {
        "hook": [
            "Aaj ek zaroori concept seekhte hain jo har investor ko pata hona chahiye.",
            "Is video mein ek simple lekin powerful investing lesson hai.",
        ],
        "body": [
            "Stock market ko samajhna mushkil nahi hai — ek step at a time.",
            "Yeh concept samjh lo — baaki sab aasaan ho jayega.",
        ],
        "cta": [
            "Subscribe karo — har week ek naya investing concept!",
            "Comment mein batao — kya yeh helpful tha?",
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
    "english_education": {
        "hook": [
            "One concept every investor must understand.",
            "Here's what schools never teach about money.",
        ],
        "body": [
            "Building wealth is simple — but not easy. Let's start with the basics.",
            "This concept will change how you think about investing forever.",
        ],
        "cta": [
            "Subscribe for the full 52-week investing course — free!",
            "Share this with someone starting their investing journey.",
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
        from ai_client import ai
        response = ai.generate(prompt, content_mode="market", lang="hi")
        data     = ai.generate_json(prompt, lang="en")
        data     = ai.generate_with_stock_data(prompt, lang="hi",
                       sym="NESTLE", cmp=1446, sl=1380, target=1550)
    """

    def __init__(self):
        self.groq_key    = os.environ.get("GROQ_API_KEY")
        self.gemini_key  = os.environ.get("GEMINI_API_KEY")
        self.claude_key  = os.environ.get("ANTHROPIC_API_KEY")
        self.openai_key  = os.environ.get("OPENAI_API_KEY")
        self.active_provider = None
        self.stats = {p: {"success": 0, "fail": 0} for p in PROVIDERS}

    # ── PUBLIC METHODS ─────────────────────────────────────────────────────────

    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 content_mode: str = "market", lang: str = "hi",
                 max_tokens: int = 1500, temperature: float = 0.85,
                 json_mode: bool = False) -> str:
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

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None,
                      content_mode: str = "market", lang: str = "hi") -> dict:
        """Generate and parse a JSON response."""
        raw = self.generate(
            prompt, system_prompt, content_mode, lang,
            json_mode=True,
            max_tokens=4000,
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

    def generate_with_stock_data(
        self,
        prompt: str,
        lang: str = "hi",
        content_mode: str = "market",
        sym: str = "",
        cmp: float = 0,
        sl: float = 0,
        target: float = 0,
        system_prompt: Optional[str] = None,
    ) -> dict:
        """
        v2.2 NEW: Generate JSON with stock numbers locked.
        Numbers come from Google Sheet (AlertLog) — trusted source.
        AI is explicitly told not to change them.

        This permanently fixes: SL 1457 being written as 145.7 by AI.

        Usage:
            data = ai.generate_with_stock_data(
                prompt=prompt, lang=LANG,
                sym="NESTLE", cmp=1446.90, sl=1380.10, target=1550.40
            )
        """
        # Format prices for display and TTS
        cmp_disp = f"Rs.{int(round(cmp))}"    if cmp > 0    else "live"
        sl_disp  = f"Rs.{int(round(sl))}"     if sl > 0     else "N/A"
        tgt_disp = f"Rs.{int(round(target))}" if target > 0 else "N/A"

        # TTS format (no Rs. symbol)
        cmp_tts = f"{int(round(cmp))} rupaye"    if lang == "hi" and cmp > 0    else f"{int(round(cmp))} rupees"
        sl_tts  = f"{int(round(sl))} rupaye"     if lang == "hi" and sl > 0     else f"{int(round(sl))} rupees"
        tgt_tts = f"{int(round(target))} rupaye" if lang == "hi" and target > 0 else f"{int(round(target))} rupees"

        locked_numbers = f"""
LOCKED NUMBERS — from live Google Sheet (AlertLog) — DO NOT CHANGE:
  Stock:  {sym}
  Entry:  {cmp_disp}  (use EXACTLY this in script, no rounding or decimals)
  SL:     {sl_disp}   (use EXACTLY this in script)
  Target: {tgt_disp}  (use EXACTLY this in script)

For SPOKEN SCRIPT (TTS audio — no Rs. symbol):
  Entry spoken: "{cmp_tts}"
  SL spoken:    "{sl_tts}"
  Target spoken: "{tgt_tts}"

RULE: These numbers come from a live trading system. Never change, divide, or round them differently.
RULE: Thumbnail text = English only. No Hindi/Devanagari in thumbnail_text_line1 or line2.
"""
        full_prompt = f"{prompt}\n\n{locked_numbers}"
        return self.generate_json(full_prompt, system_prompt, content_mode, lang)

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

    # ── PROVIDER DISPATCH ──────────────────────────────────────────────────────

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

    # ── GROQ ──────────────────────────────────────────────────────────────────

    def _groq(self, prompt, system_prompt, max_tokens, temperature, json_mode):
        if not self.groq_key:
            raise ValueError("GROQ_API_KEY not set")
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("groq package not installed")

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

    # ── GEMINI ────────────────────────────────────────────────────────────────

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
        gen_config  = types.GenerateContentConfig(max_output_tokens=max_tokens, temperature=temperature)
        if json_mode:
            gen_config.response_mime_type = "application/json"
        for model_name in GEMINI_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name, contents=full_prompt, config=gen_config)
                text = response.text.strip()
                if text: return text
            except Exception as e:
                logger.warning(f"Gemini new {model_name}: {e}")
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
                if text: return text
            except Exception as e:
                logger.warning(f"Gemini old {model_name}: {e}")
        raise Exception("All Gemini models failed (old SDK)")

    # ── CLAUDE ────────────────────────────────────────────────────────────────

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
                    model=model_name, max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = message.content[0].text.strip()
                if text: return text
            except Exception as e:
                logger.warning(f"Claude {model_name}: {e}")
        raise Exception("All Claude models failed")

    # ── OPENAI ────────────────────────────────────────────────────────────────

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
                        {"role": "user",   "content": prompt},
                    ],
                    "max_tokens": max_tokens, "temperature": temperature,
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                resp = client.chat.completions.create(**kwargs)
                text = resp.choices[0].message.content.strip()
                if text: return text
            except Exception as e:
                logger.warning(f"OpenAI {model_name}: {e}")
        raise Exception("All OpenAI models failed")

    # ── SYSTEM PROMPTS ────────────────────────────────────────────────────────

    def _default_system_prompt(self, lang: str, content_mode: str) -> str:
        """
        v2.2 FIX: Education mode gets a TEACHER persona, not a TRADER persona.
        This fixes education videos starting with "chart kabhie jhooth nahi bolta".
        """
        if content_mode == "education":
            return self._education_system_prompt(lang)

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

    def _education_system_prompt(self, lang: str) -> str:
        """
        v2.2 NEW: Clean teacher persona for education videos.
        NO chart/setup/trading signal language.
        NO "aaj ka market" or "chart kabhie jhooth nahi bolta".
        This is a 52-week course — each video teaches one concept clearly.
        """
        if lang == "en":
            return (
                "You are a friendly financial educator teaching a free 52-week investing course. "
                "Your audience: beginners who know nothing about investing. "
                "Write like a patient teacher, not a trader. "
                "Simple language. Real-world examples. No jargon without explanation. "
                "Do NOT use: 'today's market', 'chart pattern', 'setup', 'signal', 'breakout'. "
                "DO use: 'this concept', 'let me explain', 'for example', 'think of it this way'. "
                "Every video covers ONE concept completely. No rushed content."
            )
        return (
            "Tum ek friendly financial teacher ho jo ek free 52-week investing course padhate ho. "
            "Audience: beginners jo investing ke baare mein kuch nahi jaante. "
            "Ek patient teacher ki tarah likho — trader ki tarah nahi. "
            "Simple language. Real-life examples. Koi jargon bina explanation ke mat use karo. "
            "IN cheezein MAT likho: 'aaj ka market', 'chart pattern', 'setup', 'breakout', 'signal'. "
            "YEH likho: 'yeh concept', 'samjhao mujhe', 'example ke taur pe', 'sochte hain'. "
            "Har video sirf EK concept clearly cover kare. Rush mat karo."
        )

    def _get_fallback_template(self, content_mode: str, lang: str) -> str:
        if lang == "en":
            mode      = "english_education" if content_mode == "education" else "english"
            templates = FALLBACK_TEMPLATES.get(mode, FALLBACK_TEMPLATES["english"])
        else:
            mode      = content_mode if content_mode in FALLBACK_TEMPLATES else "market"
            templates = FALLBACK_TEMPLATES[mode]
        hook = random.choice(templates["hook"])
        body = random.choice(templates["body"])
        cta  = random.choice(templates["cta"])
        return f"{hook}\n\n{body}\n\n{cta}"


# ─────────────────────────────────────────────
# IMAGE & VIDEO CLIENT
# v2.2: Stability AI background generation added
# ─────────────────────────────────────────────

class ImageVideoClient:
    """
    Image generation for premium-looking video backgrounds.

    Phase 1 (now): PIL-based via existing generators.
    Phase 1.5 (now): Stability AI for 3D-style backgrounds (STABILITY_API_KEY).
    Phase 2 (planned): Gemini Imagen / Veo when APIs stabilise.

    3D-style shorts: generate_background() creates a Pixar-style scene
    which is used as background in generate_shorts.py with ZENO overlay.
    Result looks semi-3D — professional quality, free tier.
    """

    def __init__(self):
        self.gemini_key    = os.environ.get("GEMINI_API_KEY")
        self.stability_key = os.environ.get("STABILITY_API_KEY")

    def generate_background(
        self,
        stock: str = "",
        sentiment: str = "bullish",
        style: str = "3d_pixar",
        out_path: str = "output/bg_generated.png",
    ) -> Optional[str]:
        """
        Generate a background image using Stability AI.

        3D Pixar style: "3d Pixar animated style Indian stock market,
        bullish/bearish mood, no text, clean background"

        Returns: path to saved image, or None if failed.

        Stability free tier: ~25 credits/month.
        One image = ~1-3 credits. Budget: ~10-15 images/month.
        """
        if not self.stability_key:
            logger.info("[IMG] No STABILITY_API_KEY — skipping background generation")
            return None

        sentiment_desc = (
            "energetic green upward arrows, golden light, celebration"
            if sentiment == "bullish" else
            "cool blue downward trend, calm analytical mood"
        )

        prompt_map = {
            "3d_pixar": (
                f"3D Pixar animated style, Indian stock market backdrop, "
                f"{sentiment_desc}, "
                f"clean professional background, no text, no numbers, "
                f"bokeh effect, studio lighting, 9:16 vertical format"
            ),
            "abstract": (
                f"abstract financial background, {sentiment_desc}, "
                f"geometric patterns, premium dark theme, "
                f"no text, vertical 9:16 format"
            ),
            "minimal": (
                f"minimal dark gradient background, subtle stock chart lines, "
                f"{sentiment_desc}, clean professional, no text, 9:16"
            ),
        }

        img_prompt = prompt_map.get(style, prompt_map["3d_pixar"])

        try:
            import requests
            resp = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Authorization": f"Bearer {self.stability_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json={
                    "text_prompts": [
                        {"text": img_prompt, "weight": 1.0},
                        {"text": "text, watermark, logo, numbers, letters", "weight": -1.0},
                    ],
                    "cfg_scale": 7,
                    "height": 1344,
                    "width":  768,
                    "samples": 1,
                    "steps":   25,
                },
                timeout=60,
            )

            if resp.status_code == 200:
                data    = resp.json()
                img_b64 = data["artifacts"][0]["base64"]
                img_bytes = base64.b64decode(img_b64)
                os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                logger.info(f"[IMG] ✅ Background generated: {out_path}")
                return out_path
            else:
                logger.warning(f"[IMG] Stability API error {resp.status_code}: {resp.text[:200]}")
                return None

        except Exception as e:
            logger.warning(f"[IMG] Background generation failed: {e}")
            return None

    def generate_thumbnail(self, title: str, mode: str = "market") -> Optional[str]:
        logger.info("ImageVideoClient: using existing PIL pipeline")
        return None

    def generate_video_clip(self, prompt: str, duration: int = 5) -> Optional[str]:
        logger.info("Video generation — Phase 2 planned (Gemini Veo)")
        return None


# ─────────────────────────────────────────────
# SINGLETON INSTANCES
# from ai_client import ai, img_client
# ─────────────────────────────────────────────

ai         = AIClient()
img_client = ImageVideoClient()


# ─────────────────────────────────────────────
# TEST / DEBUG
# ─────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=" * 60)
    print("AI360Trading — AI Client v2.2 Test")
    print("=" * 60)

    client = AIClient()

    print("\n[TEST 1] Hindi market content:")
    print(client.generate("Aaj Nifty50 ke liye ek 3-line trading insight likho.",
                          content_mode="market", lang="hi"))

    print("\n[TEST 2] Hindi education content (should NOT say 'chart kabhie jhooth nahi bolta'):")
    print(client.generate("Stock market kya hai — Week 1 education video ke liye 3 lines likho.",
                          content_mode="education", lang="hi"))

    print("\n[TEST 3] English education content:")
    print(client.generate("Write 3 lines about what is a stock market for Week 1 education video.",
                          content_mode="education", lang="en"))

    print("\n[TEST 4] generate_with_stock_data (numbers should stay exact):")
    result = client.generate_with_stock_data(
        prompt='Create a short script for this stock. Return JSON with "full_script" and "thumbnail_text_line1".',
        lang="hi",
        sym="NESTLE",
        cmp=1446.90,
        sl=1380.10,
        target=1550.40,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n[STATUS]")
    print(json.dumps(client.get_status(), indent=2))
