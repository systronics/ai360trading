"""
human_touch.py — Anti-AI-Penalty Human Touch Engine
=====================================================
v2.2 CHANGES (May 2026):
  ADDED: HOOKS_HINDI_EDUCATION, HOOKS_ENGLISH_EDUCATION
         Prevents education videos starting with trading hooks like
         "Chart kabhi jhooth nahi bolta" — wrong for education content

  ADDED: safe_thumbnail_text(text)
         Strips Devanagari chars from thumbnail text for PIL rendering
         Fixes "पा" artifact appearing in thumbnails

  ADDED: safe_tts_price(val, lang)
         Converts Rs.1457 → "1457 rupaye" for TTS
         Fixes TTS reading "rupee sign" out loud

  ADDED: get_video_description(mode, lang, week, topic)
         Generates YouTube description for education videos
         Prevents AttributeError crash in generate_education.py v1.1

  ADDED: get_prompt_rules(lang, sym, cmp, sl, target, mode)
         Injects 3 rules into every AI prompt:
         Rule 1: Thumbnail text = English only
         Rule 2: Exact numbers from Sheet — AI must not change
         Rule 3: No Rs. symbol in TTS script

  ADDED: humanize_script_lines(lines, lang)
         Light humanization of script line list

  ADDED: get_personal_phrase(lang)
         Returns random personal voice phrase

  ADDED: get_posting_time_tag(countries)
         Returns best posting time for target countries

All existing content preserved exactly.
Last Updated: May 2026
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

# v2.2 NEW — Education hooks (teacher tone, NOT trading tone)
HOOKS_HINDI_EDUCATION = [
    "Aaj ek cheez seekhenge jo har successful investor jaanta hai:",
    "Stock market mein pehla kadam — yeh video dhyan se dekho:",
    "Bahut log investing se darte hain kyunki samjha nahi gaya unhe —",
    "Aaj ka lesson simple hai — lekin bahut powerful hai:",
    "Ek baar yeh samajh gaye toh market aapko alag nazar aayega:",
    "Investing ki duniya mein welcome — aaj se shuru karte hain:",
    "Yeh ek concept hai jo school mein nahi padhaya jaata — par hona chahiye:",
    "Aaj main ek cheez itni simple tarah se samjhaunga ki aap kabhi nahi bhoolunga:",
    "Agar aap beginner hain — yeh video aapke liye hi bani hai:",
    "Seekhne ka sabse accha time abhi hai — chaliye shuru karte hain:",
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

# v2.2 NEW — Education hooks English
HOOKS_ENGLISH_EDUCATION = [
    "Today we learn one thing every successful investor knows:",
    "This is the concept school never taught you about money:",
    "If you are new to investing, this video is made for you:",
    "One lesson today that will change how you see the market:",
    "Simple, clear, and powerful — let's learn this together:",
    "Welcome to Week {week} — here is what we cover today:",
    "This concept sounds complex — but I will make it simple:",
    "The foundation of all investing — let's build it together:",
    "Most beginners skip this step — don't make that mistake:",
    "Today's lesson is short — but you will remember it forever:",
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
    "Agar helpful laga toh like karo aur Telegram join karo signals ke liye!",
    "Apne trading friends ke saath share karo — unki bhi madad hogi!",
    "Subscribe karo daily market updates ke liye — free hai!",
    "Comment mein batao — aap kya sochte ho is setup ke baare mein?",
    "Telegram link bio mein hai — wahan live signals milte hain!",
    "Agar ek bhi cheez useful lagi toh like zaroor karo!",
    "Agle video mein aur detail mein baat karenge — subscribe karo!",
]

CTAS_EDUCATION_HINDI = [
    "Agli week ek aur important lesson aayega — subscribe karo bell icon ke saath!",
    "Like karo agar helpful laga — apne dost ko bhi share karo!",
    "Comment mein batao — kya aapke koi sawaal hain?",
    "Poora 52-week course free hai is channel pe — subscribe karo!",
    "Apne pariwar ko bhi share karo yeh video — sabko investment seekhna chahiye!",
]

CTAS_ENGLISH = [
    "If this helped, hit like and subscribe for daily updates!",
    "Share this with a trader friend who needs to see this!",
    "Join our Telegram for live signals — link in bio!",
    "Drop your thoughts in the comments — I read every one!",
    "Subscribe so you never miss a market setup!",
    "Like if you found this useful — it really helps the channel!",
]


# ─────────────────────────────────────────────
# MORNING REEL TOPICS BY DAY
# ─────────────────────────────────────────────

MORNING_REEL_TOPICS = {
    0: {
        "topic": "US/UK Weekend Market Recap",
        "angle": "What happened globally while Indian markets were closed",
        "target_country": ["USA", "UK", "India"],
        "hook_en": "While you were sleeping, global markets made a big move:",
        "hook_hi": "Weekend mein global markets mein yeh hua — dekhna zaroori hai:",
    },
    1: {
        "topic": "Trading Psychology",
        "angle": "One mindset shift that separates winners from losers",
        "target_country": ["India", "UAE"],
        "hook_en": "The real reason most traders fail has nothing to do with charts:",
        "hook_hi": "90% traders yeh galti karte hain — aur yeh chart se related nahi hai:",
    },
    2: {
        "topic": "Global Market Update",
        "angle": "Mid-week global picture — US, UK, Brazil, India",
        "target_country": ["USA", "UK", "Brazil", "India"],
        "hook_en": "Mid-week check — here's what global markets are telling us:",
        "hook_hi": "Hafte ke beech mein global market ka ek quick scan karte hain:",
    },
    3: {
        "topic": "Wealth Mindset",
        "angle": "One wealth principle successful investors follow",
        "target_country": ["UAE", "Canada", "Australia"],
        "hook_en": "One wealth principle that compound investors never break:",
        "hook_hi": "Ek rule jo sab successful investors follow karte hain — seriously:",
    },
    4: {
        "topic": "Weekend Strategy Preview",
        "angle": "What to watch, what to prepare before next week",
        "target_country": ["India", "USA", "UK"],
        "hook_en": "Before markets close today — here's your weekend prep list:",
        "hook_hi": "Weekend se pehle yeh 3 cheezein prepare kar lo — trading ke liye:",
    },
    5: {
        "topic": "Motivation + Lessons",
        "angle": "One trading lesson from a real market mistake",
        "target_country": ["Global"],
        "hook_en": "The lesson I learned the hard way — so you don't have to:",
        "hook_hi": "Ek galti jo maine ki — taaki aap na karein:",
    },
    6: {
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
    def __init__(self):
        self._today = datetime.now(IST)

    def get_hook(self, mode: str = "market", lang: str = "hi",
                 week: int = 1, holiday: str = "") -> str:
        """
        Returns rotating opening hook based on mode and language.
        mode="education" → returns education-specific hook (teacher tone)
        mode="market"    → returns trading hook
        """
        if mode == "education":
            if lang == "hi":
                hooks = HOOKS_HINDI_EDUCATION
                return random.choice(hooks)
            else:
                hooks = HOOKS_ENGLISH_EDUCATION
                hook  = random.choice(hooks)
                return hook.replace("{week}", str(week))

        elif mode in ("weekend", "holiday"):
            if lang == "hi":
                if mode == "holiday" and holiday:
                    hooks = [h.format(holiday=holiday) for h in HOOKS_HINDI_HOLIDAY]
                else:
                    hooks = HOOKS_HINDI_WEEKEND
                return random.choice(hooks)
            else:
                return random.choice(HOOKS_ENGLISH)

        else:  # market
            if lang == "hi":
                return random.choice(HOOKS_HINDI_MARKET)
            else:
                return random.choice(HOOKS_ENGLISH)

    def get_cta(self, lang: str = "hi", mode: str = "market") -> str:
        """Returns rotating CTA based on language and mode."""
        if mode == "education":
            if lang == "hi":
                return random.choice(CTAS_EDUCATION_HINDI)
            else:
                return "Subscribe for next week's lesson — the full 52-week course is free on this channel!"
        if lang == "hi":
            return random.choice(CTAS_HINDI)
        return random.choice(CTAS_ENGLISH)

    def get_tts_speed(self) -> float:
        """Returns slightly varied TTS speed for natural feel."""
        return random.choice([0.95, 0.97, 1.0, 1.0, 1.02, 1.03, 1.05])

    def humanize(self, text: str, lang: str = "hi") -> str:
        """Light humanization — strip markdown + remove AI-sounding patterns.

        Markdown stripping matters because the AI often returns `**bold**`,
        `*italic*`, `### headers` or `` `code` ``. If left in, edge-TTS reads
        the symbols oddly and the burned-in captions literally show `**`.
        """
        if not text:
            return text

        # ── Strip markdown so it is neither spoken nor shown in captions ──
        text = re.sub(r"\*{1,3}", "", text)          # ** *** bold / * italic
        text = re.sub(r"_{2,3}", "", text)           # __ bold underscores
        text = re.sub(r"`+", "", text)               # `code` backticks
        text = re.sub(r"^\s*#{1,6}\s*", "", text)    # leading # headers
        text = re.sub(r"^\s*[-•]\s+", "", text)      # leading bullet markers

        # Remove "Certainly!", "Of course!", etc.
        ai_phrases = [
            r"^Certainly[,!.]?\s*",
            r"^Of course[,!.]?\s*",
            r"^Absolutely[,!.]?\s*",
            r"^Great[,!.]?\s*",
            r"^Sure[,!.]?\s*",
        ]
        for pattern in ai_phrases:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        return text.strip()

    def humanize_script_lines(self, lines: list, lang: str = "hi") -> list:
        """Light humanization of script line list."""
        return [self.humanize(line, lang) for line in lines if line.strip()]

    def get_personal_phrase(self, lang: str = "hi") -> str:
        """Returns random personal voice phrase."""
        if lang == "hi":
            return random.choice(PERSONAL_PHRASES_HINDI)
        return random.choice(PERSONAL_PHRASES_ENGLISH)

    def get_posting_time_tag(self, countries: list) -> str:
        """Returns optimal posting time note for target countries."""
        now_hour = datetime.now(IST).hour
        if "USA" in countries or "UK" in countries:
            return "US/UK prime time: post between 11 PM - 1 AM IST"
        if "UAE" in countries:
            return "UAE prime time: post between 8-10 PM IST"
        return "India prime time: post between 7-9 PM IST"

    def get_video_description(self, mode: str = "education", lang: str = "hi",
                               week: int = 1, topic: str = "") -> str:
        """
        Generate YouTube description for education videos.
        Called by generate_education.py v1.1.
        """
        base_url = "https://ai360trading.in"
        tg_url   = "https://t.me/ai360trading"

        if lang == "hi":
            desc = (
                f"📚 AI360 Trading — 52-Week Free Investing Course\n"
                f"Week {week}: {topic}\n\n"
                f"Yeh video ek complete free investing course ka hissa hai.\n"
                f"Har week ek naya lesson — beginners se advanced tak.\n\n"
                f"🔔 Subscribe karo taaki koi lesson miss na ho!\n"
                f"📱 Free daily signals: {tg_url}\n"
                f"🌐 Website: {base_url}\n\n"
                f"⚠️ Yeh educational content hai. SEBI registered nahi hain.\n"
                f"Invest karne se pehle apni research zaroor karein.\n\n"
                f"#StockMarket #InvestingForBeginners #ai360trading #HindiFinance #Nifty50"
            )
        else:
            desc = (
                f"📚 AI360 Trading — Free 52-Week Investing Course\n"
                f"Week {week}: {topic}\n\n"
                f"This video is part of a complete free investing course.\n"
                f"One new lesson every week — beginner to advanced.\n\n"
                f"🔔 Subscribe so you never miss a lesson!\n"
                f"📱 Free daily signals: {tg_url}\n"
                f"🌐 Website: {base_url}\n\n"
                f"⚠️ Educational content only. Not SEBI registered.\n"
                f"Always do your own research before investing.\n\n"
                f"#StockMarket #InvestingForBeginners #ai360trading #Nifty50 #India"
            )
        return desc

    def get_prompt_rules(self, lang: str = "hi", sym: str = "",
                          cmp: float = 0, sl: float = 0,
                          target: float = 0, mode: str = "market") -> str:
        """
        Inject 3 rules into every AI prompt for stock content.
        Prevents common AI mistakes in trading content.
        """
        rules = [
            "RULE 1: All thumbnail text must be in English characters only. "
            "Never use Devanagari script in the thumbnail_text field.",
        ]
        if sym and cmp and sl and target:
            rules.append(
                f"RULE 2: Use ONLY these exact numbers — do not change them: "
                f"Stock={sym}, CMP=Rs.{cmp}, SL=Rs.{sl}, Target=Rs.{target}. "
                f"These come directly from the trading system."
            )
        rules.append(
            "RULE 3: In all spoken/TTS script fields, never write 'Rs.' or '₹' symbols. "
            "Write amounts as numbers only (e.g., '1457 rupaye' or '1457 rupees'). "
            "TTS engines read symbols incorrectly."
        )
        return "\n".join(rules)


# ─────────────────────────────────────────────
# SEO CLASS
# ─────────────────────────────────────────────

class SEO:
    """SEO tag generation for all content types."""

    BASE_TAGS = [
        "AI360Trading", "StockMarket", "Trading", "Investing", "Nifty50",
        "NSE", "BSE", "SEBI", "IndianStockMarket", "SwingTrading",
        "TradingSignals", "StockMarketIndia", "ShareMarket", "NiftyTrading",
        "ai360trading",
    ]

    EDUCATION_TAGS = [
        "StockMarketForBeginners", "InvestingForBeginners", "LearnInvesting",
        "HindiFinance", "FinancialEducation", "PersonalFinance",
        "MutualFunds", "SIP", "IndexFund", "WealthBuilding",
        "MoneyManagement", "FinancialLiteracy", "IndianInvestor",
    ]

    GLOBAL_TAGS = [
        "GlobalMarkets", "SP500", "Bitcoin", "Gold", "FTSE100",
        "IBOVESPA", "NRIInvesting", "IndianDiaspora",
    ]

    KIDS_TAGS = [
        "HerooQuest", "KidsStories", "AnimatedStories", "ChildrenEducation",
        "MoralStories", "HindiKahani", "KidsCartoon", "BedtimeStories",
        "PixarStyle", "FamilyFriendly",
    ]

    def get_video_tags(self, mode: str = "market", is_short: bool = False,
                        channel: str = "main", lang: str = "hi") -> list:
        """Returns appropriate tag list for given content type."""
        if channel == "kids":
            return self.KIDS_TAGS + ["KidsAnimation", "ChildrenStories"]

        tags = self.BASE_TAGS.copy()

        if mode == "education":
            tags = tags + self.EDUCATION_TAGS + self.GLOBAL_TAGS
        elif mode in ("weekend", "holiday"):
            tags = tags + self.EDUCATION_TAGS
        else:
            tags = tags + self.GLOBAL_TAGS

        if is_short:
            tags = tags + ["Shorts", "YouTubeShorts", "TradingShorts"]

        return list(dict.fromkeys(tags))  # deduplicate preserving order

    def get_youtube_safe_tags(self, tags: list) -> list:
        """
        Returns YouTube-safe tags:
        - ASCII only (no Devanagari)
        - Max 500 chars total
        - Max 30 tags
        """
        safe  = []
        total = 0
        for tag in tags[:50]:
            clean = re.sub(r'[^\x00-\x7F]', '', tag).strip()
            if not clean:
                continue
            if total + len(clean) > 480:
                break
            safe.append(clean)
            total += len(clean) + 1
            if len(safe) >= 30:
                break
        return safe

    def format_article_tags(self, tags: list) -> str:
        """Format tags for Jekyll frontmatter."""
        return "[" + ", ".join(f'"{t}"' for t in tags[:15]) + "]"


# ─────────────────────────────────────────────
# v2.2 NEW UTILITY FUNCTIONS
# ─────────────────────────────────────────────

def safe_thumbnail_text(text: str) -> str:
    """
    Strip Devanagari characters from text for PIL thumbnail rendering.
    Keeps: English, numbers, Rs., %, +, -, spaces, common symbols.
    Fixes: "पा" artifact appearing in PIL-rendered thumbnails.

    Usage in any generator:
        from human_touch import safe_thumbnail_text
        title = safe_thumbnail_text(ai_generated_title)
    """
    if not text:
        return text
    # Remove Devanagari Unicode block (U+0900 to U+097F)
    cleaned = re.sub(r'[\u0900-\u097F]+', '', text)
    # Remove multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def safe_tts_price(val, lang: str = "hi") -> str:
    """
    Convert price value to TTS-safe spoken form.
    Prevents TTS reading "rupee sign" or "dollar sign" out loud.

    Usage:
        from human_touch import safe_tts_price
        spoken = safe_tts_price(1457.50, lang="hi")  # → "1457 rupaye"
        spoken = safe_tts_price(1457.50, lang="en")  # → "1457 rupees"
    """
    try:
        val = float(str(val).replace("Rs.", "").replace("₹", "").replace(",", "").strip())
        if val >= 10000:
            formatted = f"{int(val):,}"
        elif val >= 100:
            formatted = f"{val:.0f}"
        else:
            formatted = f"{val:.2f}"
        if lang == "hi":
            return f"{formatted} rupaye"
        return f"{formatted} rupees"
    except Exception:
        return str(val)


# ─────────────────────────────────────────────
# SINGLETON INSTANCES
# ─────────────────────────────────────────────

ht  = HumanTouch()
seo = SEO()
