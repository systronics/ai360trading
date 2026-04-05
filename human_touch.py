"""
human_touch.py — Anti-AI-Penalty Human Touch Engine
=====================================================
Makes all AI-generated content feel human-written.
Used by: ALL content generators

Techniques:
- 50+ rotating hooks (no two videos start the same)
- Personal voice phrases injection
- Sentence structure variation
- Natural imperfection patterns
- TTS speed variation
- Emoji placement variation
- Day/country/audience-aware tone shifts

Author: AI360Trading Automation
Last Updated: March 2026
"""

import random
import re
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")


# ─────────────────────────────────────────────
# HOOK LIBRARIES
# ─────────────────────────────────────────────

HOOKS_HINDI_MARKET = [
    "Yaar, aaj market ne kuch aisa kiya jo bahut log miss kar gaye —",
    "Seedha baat — aaj ka sabse important chart pattern yeh hai:",
    "Maine aaj subah ek cheez notice ki jo aapko bhi dekhni chahiye:",
    "Ek baat jo har trader ko aaj samajhni chahiye —",
    "Bahut log pooch rahe the — toh aaj main clear kar deta hoon:",
    "Sach batayein toh, aaj ka market ek interesting signal de raha hai:",
    "15 saal ke trading experience mein aisi setup bahut kam dekhi hai —",
    "Agar aap ye video skip karte hain toh shayad ek opportunity miss kar sakte hain:",
    "Simple question — kya aapne aaj ke Nifty movement ko dekha?",
    "Chaliye aaj directly kaam ki baat karte hain:",
    "Jo log Telegram pe the, unhe pehle pata tha — yeh watch karo:",
    "Honest review — aaj market ne kya kiya aur kyon:",
    "Subah se ek cheez mera dhyan kheench rahi thi — share karta hoon:",
    "Smart traders aaj yeh kar rahe hain. Kya aap?",
    "Bina time waste kiye — aaj ka key level yeh hai:",
    "Chart kabhi jhooth nahi bolta — dekho yeh setup:",
    "Risk sirf woh lete hain jo samjhe nahi — yeh dekhkar samjho:",
    "Aaj ek trade setup hai jo mujhe personally pasand aaya:",
    "Market hamesha signal deta hai — sunna aata ho toh:",
    "Yeh video sirf unke liye hai jo seriously trade karna chahte hain:",
]

HOOKS_HINDI_WEEKEND = [
    "Weekend ho ya weekday — seekhna kabhi band mat karo:",
    "Aaj market band hai, par aapki growth nahi honi chahiye:",
    "Jo traders weekends mein bhi padhte hain — woh alag hote hain:",
    "2 din ka time hai — ek naya concept seekhte hain:",
    "Ek baat jo market kholne se pehle zaroori hai samajhna:",
    "Weekend special — yeh ek concept aapki trading badal sakta hai:",
    "Charts se break lo, par seekhne se nahi:",
    "Successful traders ka secret? Weekends mein yeh karte hain:",
    "Aaj kuch aisa share karna chahta hoon jo normally nahi batata:",
    "Market band hai — perfect time apni mistakes review karne ka:",
]

HOOKS_HINDI_HOLIDAY = [
    "Aaj {holiday} hai — market band, par kuch zaroori baat:",
    "Holiday mein bhi smart traders kuch karte hain — dekhte hain:",
    "{holiday} ki shubhkamnayein! Ek quick trading lesson ke saath:",
    "Aaj rest karo, par yeh ek baat zaroor yaad rakhna:",
    "Market band hai aaj — perfect time reflection ka:",
    "Happy {holiday}! Trading lesson ke saath celebrate karte hain:",
]

HOOKS_ENGLISH = [
    "Most traders overlook this — and it costs them dearly:",
    "Let me be direct with you about today's market setup:",
    "I noticed something this morning that you need to see:",
    "Quick question — did you catch today's Nifty signal?",
    "No fluff, no theory — here's what the chart is saying right now:",
    "The smart money is moving. Here's where:",
    "This one pattern has shown up 3 times this week:",
    "I've been trading for years, and setups like this don't come often:",
    "Before the market opens tomorrow, you need to know this:",
    "The chart never lies — this is what it's telling us today:",
    "Stop guessing. Here's the actual data:",
    "What the news won't tell you about today's market:",
    "One level. One plan. Let's break it down:",
    "If you're serious about trading, watch this carefully:",
    "I'll show you exactly what I'm watching today:",
    "Global markets are sending a clear signal right now:",
    "This is the kind of setup that changes your trading month:",
    "Most retail traders will miss this. You won't:",
    "Simple, clear, actionable — today's best trade setup:",
    "The only market analysis you need today:",
]


# ─────────────────────────────────────────────
# PERSONAL VOICE PHRASES
# ─────────────────────────────────────────────

PERSONAL_PHRASES_HINDI = [
    "Mera personal experience hai ki",
    "Maine khud dekha hai ki",
    "Honestly bolunga toh",
    "Mere hisaab se",
    "Bahut baar observe kiya hai maine ki",
    "Yeh main apne experience se bol raha hoon",
    "Chart study karte waqt maine notice kiya ki",
    "Jo main personally follow karta hoon woh hai",
    "Seedha experience se bolunga",
    "Traders se baat karke pata chala ki",
]

PERSONAL_PHRASES_ENGLISH = [
    "In my experience,",
    "What I've personally observed is",
    "To be completely honest,",
    "From my own trading,",
    "I've seen this pattern enough times to know",
    "What I actually do in this situation is",
    "After years of watching markets,",
    "The thing most people don't tell you is",
    "I've made this mistake myself, so",
    "Real talk —",
]


# ─────────────────────────────────────────────
# CTA VARIATIONS
# ─────────────────────────────────────────────

CTAS_HINDI = [
    "Agar helpful laga toh like karo aur Telegram join karo signals ke liye! 🔔",
    "Apne trading friends ke saath share karo — unki bhi madad hogi! 📤",
    "Subscribe karo daily market updates ke liye — free hai! ✅",
    "Comment mein batao — aap kya sochte ho is setup ke baare mein? 💬",
    "Telegram link bio mein hai — wahan live signals milte hain! 📱",
    "Agar ek bhi cheez useful lagi toh like zaroor karo! 👍",
    "Agle video mein aur detail mein baat karenge — subscribe karo! 🔔",
    "Apna view share karo comment mein — community se seekhte hain! 💡",
]

CTAS_ENGLISH = [
    "If this helped, hit like and subscribe for daily updates! 🔔",
    "Share this with a trader friend who needs to see this! 📤",
    "Join our Telegram for live signals — link in bio! 📱",
    "Drop your thoughts in the comments — I read every one! 💬",
    "Subscribe so you never miss a market setup! ✅",
    "Follow for daily market insights from India's Nifty50! 🇮🇳",
    "Like if you found this useful — it really helps the channel! 👍",
    "Tag a friend who needs to see this setup! 🎯",
]


# ─────────────────────────────────────────────
# MORNING REEL TOPICS BY DAY
# ─────────────────────────────────────────────

MORNING_REEL_TOPICS = {
    0: {  # Monday
        "topic": "US/UK Weekend Market Recap",
        "angle": "What happened globally while Indian markets were closed",
        "target_country": ["USA", "UK", "India"],
        "hook_en": "While you were sleeping, global markets made a big move:",
        "hook_hi": "Weekend mein global markets mein yeh hua — dekhna zaroori hai:",
    },
    1: {  # Tuesday
        "topic": "Trading Psychology",
        "angle": "One mindset shift that separates winners from losers",
        "target_country": ["India", "UAE"],
        "hook_en": "The real reason most traders fail has nothing to do with charts:",
        "hook_hi": "90% traders yeh galti karte hain — aur yeh chart se related nahi hai:",
    },
    2: {  # Wednesday
        "topic": "Global Market Update",
        "angle": "Mid-week global picture — US, UK, Brazil, India",
        "target_country": ["USA", "UK", "Brazil", "India"],
        "hook_en": "Mid-week check — here's what global markets are telling us:",
        "hook_hi": "Hafte ke beech mein global market ka ek quick scan karte hain:",
    },
    3: {  # Thursday
        "topic": "Wealth Mindset",
        "angle": "One wealth principle successful investors follow",
        "target_country": ["UAE", "Canada", "Australia"],
        "hook_en": "One wealth principle that compound investors never break:",
        "hook_hi": "Ek rule jo sab successful investors follow karte hain — seriously:",
    },
    4: {  # Friday
        "topic": "Weekend Strategy Preview",
        "angle": "What to watch, what to prepare before next week",
        "target_country": ["India", "USA", "UK"],
        "hook_en": "Before markets close today — here's your weekend prep list:",
        "hook_hi": "Weekend se pehle yeh 3 cheezein prepare kar lo — trading ke liye:",
    },
    5: {  # Saturday
        "topic": "Motivation + Lessons",
        "angle": "One trading lesson from a real market mistake",
        "target_country": ["Global"],
        "hook_en": "The lesson I learned the hard way — so you don't have to:",
        "hook_hi": "Ek galti jo maine ki — taaki aap na karein:",
    },
    6: {  # Sunday
        "topic": "Next Week Strategy",
        "angle": "Key levels, sector focus, and what to watch Monday",
        "target_country": ["USA", "UK", "India"],
        "hook_en": "Sunday prep: here's exactly what I'm watching for next week:",
        "hook_hi": "Kal market kholega — yeh levels aur sectors ready rakhna:",
    },
}


# ─────────────────────────────────────────────
# MAIN HumanTouch CLASS
# ─────────────────────────────────────────────

class HumanTouch:
    """
    Injects human-like qualities into AI-generated content.

    Usage:
        ht = HumanTouch()
        hook = ht.get_hook(mode="market", lang="hi")
        script = ht.humanize(raw_script, lang="hi")
        tts_speed = ht.get_tts_speed()
    """

    def __init__(self):
        self.now_ist = datetime.now(IST)
        self.weekday = self.now_ist.weekday()  # 0=Mon, 6=Sun
        self.seed = int(self.now_ist.strftime("%Y%m%d"))
        random.seed(self.seed)  # Same day = same variation (consistent daily content)

    def get_hook(self, mode: str = "market", lang: str = "hi", holiday_name: str = "") -> str:
        """Get a unique hook for today's content."""
        if lang == "en":
            hooks = HOOKS_ENGLISH
        elif mode == "holiday":
            hooks = HOOKS_HINDI_HOLIDAY
        elif mode == "weekend":
            hooks = HOOKS_HINDI_WEEKEND
        else:
            hooks = HOOKS_HINDI_MARKET

        hook = hooks[self.seed % len(hooks)]

        # Replace {holiday} placeholder
        if "{holiday}" in hook:
            hook = hook.replace("{holiday}", holiday_name or "aaj")

        return hook

    def get_cta(self, lang: str = "hi") -> str:
        """Get a CTA variation for today."""
        ctas = CTAS_ENGLISH if lang == "en" else CTAS_HINDI
        return ctas[(self.seed + 3) % len(ctas)]

    def get_personal_phrase(self, lang: str = "hi") -> str:
        """Get a personal voice phrase."""
        phrases = PERSONAL_PHRASES_ENGLISH if lang == "en" else PERSONAL_PHRASES_HINDI
        return random.choice(phrases)

    def get_tts_speed(self) -> float:
        """
        Return a slightly varied TTS speed.
        Range: 0.95–1.05 — sounds natural, not robotic.
        """
        speeds = [0.95, 0.97, 1.00, 1.02, 1.05]
        return speeds[self.seed % len(speeds)]
 
    def get_searchable_title(
        self,
        content_type: str,      # "analysis", "education", "reel", "short"
        topic_keyword: str,     # Main topic e.g. "RSI Guide", "Swing Trade Setup"
        date_str: str = "",     # e.g. "05 Apr 2026" — leave blank to auto-fill today
        mode: str = "market",   # "market", "weekend", "holiday"
        holiday_name: str = ""  # e.g. "Mahavir Jayanti"
    ) -> str:
        """
        Central YouTube title builder for ALL generators.
 
        Format rules (YouTube SEO — what people actually search):
          analysis : "Nifty50 Analysis {date} | {topic} | AI360 Trading"
          education: "{topic} {date} | Trading Education | AI360 Trading"
          reel     : "{topic} | AI360 Trading Shorts"
          short    : "{topic} {date} | AI360 Trading"
          holiday  : "{holiday} 2026 | {topic} | AI360 Trading"
 
        Always ends with | AI360 Trading so channel is always searchable.
        Hard limit 95 chars — YouTube shows ~70 chars in search results.
 
        Examples of GOOD titles:
          "Nifty50 Analysis 05 Apr 2026 | Breakout Stocks Today | AI360 Trading"
          "RSI Complete Guide 05 Apr 2026 | Technical Analysis | AI360 Trading"
          "Mahavir Jayanti 2026 | Market Closed? Best Stocks to Watch | AI360 Trading"
 
        Examples of BAD titles (what we are fixing):
          "ZENO Wisdom | 20260405"           -- no topic, no channel, unsearchable
          "Aaj Ka Market"                    -- no date, no channel, too vague
          "Shri Mahavir Jayanti Lesson"      -- no year, no search keyword
        """
        if not date_str:
            date_str = datetime.now(IST).strftime("%d %b %Y")
 
        channel = "AI360 Trading"
 
        if mode == "holiday" and holiday_name:
            year  = datetime.now(IST).year
            base  = f"{holiday_name} {year} | {topic_keyword} | {channel}"
        elif content_type == "analysis":
            base  = f"Nifty50 Analysis {date_str} | {topic_keyword} | {channel}"
        elif content_type == "education":
            base  = f"{topic_keyword} {date_str} | Trading Education | {channel}"
        elif content_type == "reel":
            base  = f"{topic_keyword} | {channel} Shorts"
        elif content_type == "short":
            base  = f"{topic_keyword} {date_str} | {channel}"
        else:
            base  = f"{topic_keyword} {date_str} | {channel}"
 
        # Truncate to 95 chars max — keep channel name always
        if len(base) > 95:
            # Shorten topic_keyword, keep channel name
            suffix      = f" | {channel}"
            max_front   = 95 - len(suffix)
            base        = base[:max_front].rstrip(" |") + suffix
 
        return base[:100]

    def get_morning_reel_topic(self) -> dict:
        """Get today's morning reel topic based on day of week."""
        return MORNING_REEL_TOPICS[self.weekday]

    def humanize(self, text: str, lang: str = "hi") -> str:
        """
        Apply human touch transformations to AI-generated text.
        - Injects personal phrases
        - Varies sentence connectors
        - Adds natural pauses (for TTS)
        - Removes robotic patterns
        """
        text = self._remove_robotic_patterns(text)
        text = self._vary_connectors(text, lang)
        text = self._inject_personal_phrase(text, lang)
        text = self._add_tts_pauses(text)
        return text.strip()

    def humanize_script_lines(self, lines: list, lang: str = "hi") -> list:
        """Humanize a list of script lines."""
        result = []
        for i, line in enumerate(lines):
            line = self.humanize(line, lang)
            # Occasionally add a natural filler between lines
            if i > 0 and i % 3 == 0 and random.random() > 0.6:
                filler = self._get_filler(lang)
                if filler:
                    result.append(filler)
            result.append(line)
        return result

    def get_emoji_set(self, mode: str = "market") -> list:
        """Get contextually appropriate emojis — varied by day."""
        sets = {
            "market": ["📈", "📊", "🎯", "💹", "🔔", "⚡", "🚀", "💡", "🔥", "✅"],
            "weekend": ["📚", "🧠", "💡", "🌟", "🎯", "📖", "✨", "🏆", "💪", "🌱"],
            "holiday": ["🎉", "🌟", "✨", "🙏", "💫", "🎊", "❤️", "🌈", "🌸", "🎈"],
        }
        emoji_set = sets.get(mode, sets["market"])
        # Rotate which emojis are used each day
        start = self.seed % len(emoji_set)
        return emoji_set[start:] + emoji_set[:start]

    def get_posting_time_tag(self, target_countries: list) -> str:
        """
        Generate SEO-friendly time tag for descriptions.
        USA/UK prime time content gets special tags.
        """
        if any(c in ["USA", "UK", "Canada", "Australia"] for c in target_countries):
            return "#USStocks #UKInvesting #GlobalInvesting #FinanceWorld"
        elif "UAE" in target_countries:
            return "#UAEInvesting #NRIInvestors #DubaiFinance #GlobalStocks"
        elif "Brazil" in target_countries:
            return "#BrazilMarket #BrazilFinance #GlobalInvesting"
        else:
            return "#Nifty50 #TradingIndia #StockMarketIndia #BankNifty"

    # ── PRIVATE HELPERS ───────────────────────

    def _remove_robotic_patterns(self, text: str) -> str:
        """Remove common AI writing patterns that feel robotic."""
        replacements = {
            # Overly formal openings
            "Certainly! ": "",
            "Absolutely! ": "",
            "Of course! ": "",
            "Sure! ": "",
            "Great! ": "",
            "Indeed, ": "",
            "It's important to note that ": "",
            "It is worth noting that ": "",
            "In conclusion, ": "Toh basically, " if random.random() > 0.5 else "Ek baat clear hai — ",
            "In summary, ": "Short mein bolunga toh, ",
            "Furthermore, ": "Iske alawa, ",
            "Additionally, ": "Saath hi, ",
            "However, ": "Lekin, ",
            "Therefore, ": "Isliye, ",
            # English robotic patterns
            "It's important to": "Remember to",
            "You should consider": "Think about",
            "As an AI": "",
            "I'm an AI": "",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def _vary_connectors(self, text: str, lang: str) -> str:
        """Replace repetitive connectors with varied alternatives."""
        if lang == "hi":
            connector_map = {
                "aur ": random.choice(["aur ", "saath hi ", "plus "]),
                "lekin ": random.choice(["lekin ", "but ", "par "]),
                "kyunki ": random.choice(["kyunki ", "because ", "isliye ki "]),
            }
        else:
            connector_map = {
                "and ": random.choice(["and ", "plus ", "also "]),
                "but ": random.choice(["but ", "however, ", "yet "]),
                "because ": random.choice(["because ", "since ", "as "]),
            }
        # Only replace first occurrence to avoid over-modification
        for old, new in connector_map.items():
            text = text.replace(old, new, 1)
        return text

    def _inject_personal_phrase(self, text: str, lang: str) -> str:
        """Inject a personal phrase at a natural breakpoint."""
        if random.random() > 0.6:  # 40% chance to inject
            phrase = self.get_personal_phrase(lang)
            # Find a sentence break in the middle of the text
            sentences = text.split(". ")
            if len(sentences) > 2:
                mid = len(sentences) // 2
                sentences[mid] = f"{phrase} {sentences[mid].lower()}"
                text = ". ".join(sentences)
        return text

    def _add_tts_pauses(self, text: str) -> str:
        """
        Add natural pauses for TTS engines.
        Edge-TTS respects comma pauses.
        """
        # Add pause after strong statements
        text = re.sub(r'([.!?])\s+([A-Z\u0900-\u097F])', r'\1 \2', text)
        return text

    def _get_filler(self, lang: str) -> str:
        """Natural filler phrases used between sections."""
        if lang == "en":
            fillers = [
                "Now, here's the key part:",
                "And this is where it gets interesting —",
                "Pay attention to this:",
                "Here's what most people miss:",
            ]
        else:
            fillers = [
                "Ab yahan dhyan do —",
                "Yeh part important hai:",
                "Ab interesting part aata hai:",
                "Yahan zyada log galti karte hain:",
            ]
        return random.choice(fillers) if random.random() > 0.5 else ""


# ─────────────────────────────────────────────
# SEO TAG GENERATOR
# ─────────────────────────────────────────────

class SEOTags:
    """
    Generate optimised SEO tags for all content types.
    Always includes India + global tags.
    """

    INDIA_TAGS = [
        "Nifty50", "TradingIndia", "StockMarketIndia", "BankNifty",
        "NSE", "BSE", "IndianMarket", "TradingHindi", "ShareMarket",
        "NiftyAnalysis", "TradingTips", "StockMarket"
    ]

    GLOBAL_TAGS = [
        "USStocks", "UKInvesting", "BrazilMarket", "UAEInvesting",
        "GlobalInvesting", "Finance", "Investing", "FinancialLiteracy",
        "TradingSignals", "StockTrading", "ForexTrading", "WealthBuilding"
    ]

    SHORT_TAGS = ["Shorts", "TradingShorts", "FinanceShorts", "StocksShorts"]

    EDUCATION_TAGS = [
        "TradingEducation", "LearnTrading", "TradingForBeginners",
        "TradingPsychology", "TechnicalAnalysis", "CandlestickPatterns"
    ]

    @classmethod
    def get_video_tags(cls, mode: str = "market", is_short: bool = False) -> list:
        tags = cls.INDIA_TAGS[:6] + cls.GLOBAL_TAGS[:6]
        if is_short:
            tags += cls.SHORT_TAGS
        if mode in ["weekend", "holiday", "education"]:
            tags += cls.EDUCATION_TAGS[:3]
        random.shuffle(tags)
        return tags[:20]  # YouTube max effective tags

    @classmethod
    def get_article_tags(cls, topic: str = "") -> list:
        base = cls.INDIA_TAGS[:4] + cls.GLOBAL_TAGS[:4] + cls.EDUCATION_TAGS[:3]
        if topic:
            base = [topic.replace(" ", "")] + base
        return base[:15]

    @classmethod
    def format_youtube_tags(cls, tags: list) -> str:
        return ", ".join(tags)

    @classmethod
    def format_article_tags(cls, tags: list) -> str:
        return " ".join([f"#{t}" for t in tags])


# ─────────────────────────────────────────────
# SINGLETON INSTANCES
# ─────────────────────────────────────────────

ht = HumanTouch()
seo = SEOTags()


# ─────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    touch = HumanTouch()

    print("=" * 60)
    print("Human Touch Engine Test")
    print("=" * 60)

    print(f"\nToday's weekday: {touch.weekday} ({['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][touch.weekday]})")
    print(f"TTS Speed: {touch.get_tts_speed()}")

    print(f"\nHook (Hindi, market): {touch.get_hook('market', 'hi')}")
    print(f"Hook (English, market): {touch.get_hook('market', 'en')}")
    print(f"Hook (Hindi, weekend): {touch.get_hook('weekend', 'hi')}")

    print(f"\nCTA (Hindi): {touch.get_cta('hi')}")
    print(f"CTA (English): {touch.get_cta('en')}")

    print(f"\nMorning reel topic: {touch.get_morning_reel_topic()}")

    sample = "Certainly! It's important to note that Nifty50 aaj strong support pe hai. Furthermore, volume confirm kar raha hai yeh level."
    print(f"\nBefore humanize: {sample}")
    print(f"After humanize: {touch.humanize(sample, 'hi')}")

    print(f"\nSEO Tags (video): {SEOTags.get_video_tags('market')}")
    print(f"SEO Tags (short): {SEOTags.get_video_tags('market', is_short=True)}")
