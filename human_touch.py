"""
human_touch.py — Anti-AI-Penalty Human Touch Engine
=====================================================
Makes all AI-generated content feel human-written.
Used by: ALL content generators (trading + kids)

Techniques:
- 50+ rotating hooks (no two videos start the same)
- Personal voice phrases injection
- Sentence structure variation
- Natural imperfection patterns
- TTS speed variation (wider range 0.90–1.10)
- Emoji placement variation
- Day/country/audience-aware tone shifts
- Hinglish SEO tags (trading + kids)
- Thumbnail text generator

v2.0 CHANGES:
- SEO tags: added Hinglish + stock-specific + kids tags
- Hooks: added stock-name hooks + number hooks (viral formula)
- TTS: wider speed range 0.90–1.10
- NEW: get_thumbnail_text() for high-CTR thumbnails
- NEW: get_kids_hook() for story channel
- NEW: get_kids_tags() for kids SEO
- NEW: seo.get_video_tags() updated with Hinglish keywords

Author: AI360Trading Automation
Last Updated: May 2026
"""

import random
import re
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")


# ─────────────────────────────────────────────
# HOOK LIBRARIES — TRADING
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
    # v2.0: Stock-name + number hooks (higher CTR — people search stock names)
    "Aaj ka most important breakout stock — yeh level cross hua toh rocket:",
    "₹10,000 se yeh 3 stocks mein 30% return possible hai — dekho kaise:",
    "Is ek stock ne aaj 52-week high toda — entry kahan milegi?",
    "FII aaj yeh sector mein bhaari kharid kar rahe hain — kya aap ready hain?",
    "Yeh candlestick pattern aaj bana — agle 3 din mein kya hoga?",
    "Top 3 swing trade stocks aaj — entry, SL, target sab batata hoon:",
    "Nifty aaj is level pe hai — yahan se upar jayega ya neeche?",
    "Aaj ke 2 stocks jo kisi analyst ne nahi bataye — lekin chart bol raha hai:",
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
    # v2.0: New weekend hooks
    "Yeh galti maine ki thi — aap mat karna. Weekend lesson:",
    "Warren Buffett ka yeh rule — Indian market mein kaise apply karein:",
    "₹500/month se shuru karke ₹50 lakh kaise banate hain — sach mein:",
    "Agle hafte yeh 3 stocks watch list mein rakhna — kyon batata hoon:",
]

HOOKS_HINDI_HOLIDAY = [
    "Aaj {holiday} hai — market band, par kuch zaroori baat:",
    "Holiday mein bhi smart traders kuch karte hain — dekhte hain:",
    "{holiday} ki shubhkamnayein! Ek quick trading lesson ke saath:",
    "Aaj rest karo, par yeh ek baat zaroor yaad rakhna:",
    "Market band hai aaj — perfect time reflection ka:",
    "Happy {holiday}! Trading lesson ke saath celebrate karte hain:",
    # v2.0
    "{holiday} par ek gift — yeh concept seekho, paise bachao:",
    "Aaj {holiday} hai — market band par portfolio review karo yeh 5 min mein:",
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
    # v2.0: Number + specific hooks for global audience
    "3 Indian stocks breaking out this week — here's the data:",
    "Why smart money is quietly buying this sector right now:",
    "This pattern gave 80% win rate in backtesting — today's setup:",
    "Nifty50 vs S&P500 this week — which is better to trade?",
    "One chart. One trade. Everything you need in 60 seconds:",
]

# ─────────────────────────────────────────────
# KIDS STORY HOOKS — NEW v2.0
# ─────────────────────────────────────────────

HOOKS_KIDS_HINDI = [
    "Ek tha raja, ek thi rani — aaj unki kahani sunoge?",
    "Aaj main tumhe ek aisi kahani sunaunga jo tum kabhi nahi bhuloge:",
    "Suno suno suno — aaj ki kahani bahut khaas hai!",
    "Ek baar ki baat hai — ek chota sa baccha tha jisko ek badi problem thi:",
    "Kya tum ready ho ek jadui kahani sunne ke liye?",
    "Aaj ek aisi kahani hai jo tumhe hasayegi bhi aur seekhna bhi degi:",
    "Dosto, aaj ki kahani mein miloge ek bahut pyare dost se:",
    "Duniya mein bahut saari cheezein hain — par yeh kahani hai sabse special:",
    "Ek jungle tha, ek gadha tha, aur ek bahut hi badi mushkil thi —",
    "Aaj ki kahani mein ek chhota sa hero hai — sirf 5 saal ka!",
]

HOOKS_KIDS_ENGLISH = [
    "Once upon a time, in a land far away, there lived a very special child:",
    "Are you ready for the most amazing story you've ever heard?",
    "Today's story has magic, friendship, and a big surprise ending:",
    "In a tiny village under a rainbow sky, something wonderful happened:",
    "What if animals could talk? Today's story will show you:",
    "Close your eyes and imagine — a world where dreams come true:",
    "Today's hero is just like you — small, curious, and very brave:",
    "Deep in an enchanted forest, a little girl made an amazing discovery:",
    "Have you ever wondered what happens when stars fall to earth?",
    "Every great adventure starts with one brave step — just like today's story:",
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
    # v2.0: Poll CTAs (higher engagement)
    "Comment karo — A agar BULLISH lagta hai, B agar BEARISH! 📊",
    "Yeh stock aapke watchlist mein hai? Comment karo YES ya NO! 👇",
    "Pehle like karo, phir subscribe — aaj ka setup miss mat karo! 🎯",
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
    # v2.0: Poll CTAs
    "Comment BULL or BEAR — what's your view for this week? 📊",
    "Is this stock on your watchlist? Comment YES or NO! 👇",
    "Subscribe for the English trading series — new videos every day! 🌍",
]

CTAS_KIDS_HINDI = [
    "Kaisi lagi kahani? Comment mein batao! 💬",
    "Subscribe karo aur bell daba do — roz nayi kahani aayegi! 🔔",
    "Apne dost ko bhi dikhao yeh kahani — share karo! 📤",
    "Agar pasand aayi toh like karo — hum aur kahaniyaan laayenge! ❤️",
    "Agla episode dekhna hai? Subscribe karo abhi! ✨",
]

CTAS_KIDS_ENGLISH = [
    "Did you like the story? Give us a thumbs up! 👍",
    "Subscribe for a new story every day! 🔔",
    "Share this with your friends — they'll love it too! 📤",
    "What was your favourite part? Tell us in the comments! 💬",
    "Press the bell so you never miss a story! 🔔✨",
]


# ─────────────────────────────────────────────
# THUMBNAIL TEXT — NEW v2.0
# High-CTR thumbnail text formula
# ─────────────────────────────────────────────

THUMBNAIL_TEMPLATES_TRADING = [
    # Format: (line1, line2, line3) — line1 is biggest text
    ("{stock} 🚀",      "BREAKOUT!",         "Entry: {entry}"),
    ("₹{target}",       "TARGET?",           "{stock} Analysis"),
    ("3 STOCKS",        "BREAKOUT TODAY",    "Watch Now"),
    ("{pct}% GAIN",     "POSSIBLE?",         "{stock} Setup"),
    ("BUY NOW?",        "{stock}",           "Target: ₹{target}"),
    ("NIFTY ALERT",     "{level}",           "Kya karein?"),
    ("52W HIGH",        "{stock}",           "Aage kya?"),
    ("FII BUYING",      "{sector}",          "Opportunity!"),
    ("TODAY's",         "BEST TRADE",        "{stock} {entry}"),
    ("MARKET",          "{mood}",            "Aaj kya karein?"),
]

THUMBNAIL_TEMPLATES_TRADING_EN = [
    ("{stock}",         "BREAKOUT",          "Entry: {entry}"),
    ("3 STOCKS",        "TO WATCH",          "This Week"),
    ("{pct}% TARGET",   "{stock}",           "Trade Setup"),
    ("BUY OR SELL?",    "{stock}",           "Today's Analysis"),
    ("SMART MONEY",     "IS BUYING",         "{sector}"),
    ("NIFTY50",         "{level}",           "Key Level Alert"),
    ("52-WEEK",         "HIGH ALERT",        "{stock}"),
    ("TODAY'S",         "BEST TRADE",        "Watch This"),
]

THUMBNAIL_TEMPLATES_KIDS = [
    # Bright, fun, large emoji
    ("🦁 SHER KI",      "KAHANI",            "Aaj ki Story!"),
    ("✨ JADUI",         "DUNIYA",            "Ek Naya Safar"),
    ("🐘 ELLY",         "KI DOSTI",          "Sweet Story"),
    ("🌈 RAINBOW",      "WORLD",             "Magic Story"),
    ("👑 PRINCESS",     "STORY",             "Magical Tale"),
    ("🦋 Tितली",       "KI UDAAN",          "Inspirational"),
    ("🏰 RAJA KI",      "KAHANI",            "Aaj Episode"),
    ("🌟 STAR",         "CHILDREN",          "Daily Story"),
    ("🎪 CIRCUS",       "ADVENTURE",         "Fun Story"),
    ("🦄 UNICORN",      "MAGIC",             "Bedtime Story"),
]


# ─────────────────────────────────────────────
# SEO TAGS — UPDATED v2.0
# Hinglish + stock-specific + global + kids
# ─────────────────────────────────────────────

# Trading — Hindi/Hinglish tags (high search volume in India)
TAGS_TRADING_HINDI = [
    "शेयर बाजार आज",
    "nifty50 aaj ka analysis",
    "swing trade setup hindi",
    "best stocks to buy today india",
    "nifty prediction today",
    "free trading signals india",
    "option trading hindi",
    "nifty50 breakout stocks",
    "technical analysis hindi",
    "stock market tips hindi",
    "intraday trading tips hindi",
    "sebi registered signals",
    "nifty bank nifty analysis",
    "share market kaise seekhein",
    "trading for beginners hindi",
    "nifty50 weekly analysis",
    "best swing trade stocks india",
    "fii buying stocks today",
    "positional trading hindi",
    "stock market chart analysis",
    "nifty support resistance",
    "breakout stocks india today",
    "trading signals telegram india",
    "ai360trading",
    "nifty50 live analysis",
]

# Trading — English tags (higher CPM — USA/UK/AU)
TAGS_TRADING_ENGLISH = [
    "nifty50 analysis",
    "indian stock market",
    "nse trading signals",
    "swing trading india",
    "nifty50 breakout",
    "technical analysis india",
    "best indian stocks 2026",
    "nifty prediction",
    "indian stock market tips",
    "trading strategy india",
    "nse bse analysis",
    "how to trade nifty",
    "nifty option trading",
    "indian market technical analysis",
    "stock market india today",
    "best stocks to buy india",
    "ai360trading",
    "nifty weekly outlook",
    "indian stocks breakout",
    "sensex nifty analysis",
]

# Trading — Weekend/Educational tags
TAGS_TRADING_EDUCATION = [
    "stock market education hindi",
    "trading psychology hindi",
    "how to read candlestick charts",
    "rsi indicator hindi",
    "moving average trading",
    "support resistance levels",
    "how to pick stocks india",
    "fundamental vs technical analysis",
    "warren buffett investing hindi",
    "wealth building india",
    "financial planning hindi",
    "mutual funds vs stocks",
    "trading mistakes to avoid",
    "stock market for beginners",
    "sip vs lumpsum investment",
    "compound interest hindi",
    "long term investing india",
    "ai360trading education",
    "passive income india",
    "financial freedom hindi",
]

# Kids — Hindi story tags
TAGS_KIDS_HINDI = [
    "hindi kahani",
    "bacchon ki kahani",
    "moral story hindi",
    "fairy tale hindi",
    "short story hindi",
    "nani ki kahani",
    "panchatantra stories hindi",
    "motivational story kids",
    "bedtime story hindi",
    "cartoon kahani hindi",
    "jungle ki kahani",
    "raja rani ki kahani",
    "aesop fables hindi",
    "hindi animated stories",
    "kids moral stories",
    "children stories hindi",
    "tenali rama stories",
    "akbar birbal hindi",
    "good moral story",
    "inspirational kids story hindi",
]

# Kids — English story tags (higher CPM — global NRI audience)
TAGS_KIDS_ENGLISH = [
    "kids stories in english",
    "bedtime stories for kids",
    "moral stories for children",
    "fairy tales for kids",
    "animated stories english",
    "short stories for kids",
    "stories with moral lessons",
    "children bedtime stories",
    "educational stories kids",
    "indian stories for kids",
    "folklore stories english",
    "kids learning stories",
    "character building stories",
    "fun stories for children",
    "adventure stories kids",
    "magical stories for children",
    "storytime for kids",
    "read aloud stories",
    "story time hindi english",
    "bilingual stories kids india",
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

# Kids story topics by day (variety = subscribers watch daily)
KIDS_STORY_TOPICS = {
    0: {"theme": "Friendship",    "character": "Hathi aur Chuha",  "moral": "Dosti mein size matter nahi karta"},
    1: {"theme": "Bravery",       "character": "Chhoti Ladki",     "moral": "Himmat se badi koi taakat nahi"},
    2: {"theme": "Honesty",       "character": "Lalchi Saudagar",  "moral": "Sach bolna hamesha theek hota hai"},
    3: {"theme": "Kindness",      "character": "Magical Tree",     "moral": "Dene walo ko hamesha milta hai"},
    4: {"theme": "Hard Work",     "character": "Tembhi Keedey",    "moral": "Mehnat ka fal zaroor milta hai"},
    5: {"theme": "Imagination",   "character": "Star Children",    "moral": "Sapne dekhne wale hi unhe poora karte hain"},
    6: {"theme": "Family Love",   "character": "Jungle Family",    "moral": "Parivaar se bada koi nahi"},
}


# ─────────────────────────────────────────────
# SEO CLASS
# ─────────────────────────────────────────────

class SEO:
    """
    SEO tag and description generator.
    Used as: seo = SEO(); seo.get_video_tags(mode, is_short)
    """

    def __init__(self):
        self.now_ist = datetime.now(IST)
        self.seed    = int(self.now_ist.strftime("%Y%m%d"))

    def get_video_tags(
        self,
        mode: str = "market",
        is_short: bool = False,
        channel: str = "trading",
        lang: str = "both",
        extra_tags: list = None
    ) -> list:
        """
        Returns optimised tag list for YouTube upload.

        channel = "trading" or "kids"
        lang    = "hi", "en", or "both"
        mode    = "market", "weekend", "holiday"
        extra_tags = stock-specific tags to prepend (highest priority)
        """
        extra = extra_tags or []

        if channel == "kids":
            base = TAGS_KIDS_HINDI + TAGS_KIDS_ENGLISH
            # Rotate which tags lead based on day
            rotated = base[self.seed % 5:] + base[:self.seed % 5]
            return (extra + rotated)[:30]

        # Trading channel
        if lang == "hi":
            base = TAGS_TRADING_HINDI
        elif lang == "en":
            base = TAGS_TRADING_ENGLISH
        else:
            # Mix Hindi + English for maximum reach
            base = TAGS_TRADING_HINDI[:12] + TAGS_TRADING_ENGLISH[:12]

        if mode in ("weekend", "holiday"):
            base = TAGS_TRADING_EDUCATION[:15] + base[:10]

        # Always add ai360trading brand tag
        if "ai360trading" not in base:
            base = ["ai360trading"] + base

        # Shorts need fewer, punchier tags
        if is_short:
            return (extra + base[:15])[:20]

        return (extra + base[:25])[:30]

    def get_description_template(
        self,
        title: str,
        main_insight: str,
        mode: str = "market",
        channel: str = "trading",
        video_id_part1: str = "",
        stocks: list = None,
        lang: str = "hi"
    ) -> str:
        """
        Full YouTube description with timestamps, links, hashtags.
        YouTube shows first 2 lines before "Show More" — make them count.
        """
        stocks = stocks or []
        today  = datetime.now(IST).strftime("%d %B %Y")
        tags   = self.get_video_tags(mode=mode, channel=channel, lang=lang)
        hashtags = " ".join([f"#{t.replace(' ', '')}" for t in tags[:12]])

        if channel == "kids":
            return self._kids_description(title, main_insight, hashtags, today)

        # Trading description
        stock_line = ""
        if stocks:
            stock_line = f"📊 Stocks covered: {', '.join(stocks[:5])}\n"

        part1_line = ""
        if video_id_part1 and video_id_part1 != "UPLOAD_FAILED":
            part1_line = f"▶️ Part 1 Analysis: https://youtube.com/watch?v={video_id_part1}\n"

        if lang == "en":
            desc = (
                f"📈 {title}\n"
                f"🎯 {main_insight}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⏱️ TIMESTAMPS:\n"
                f"0:00 Market Overview\n"
                f"1:30 Today's Key Levels\n"
                f"3:00 Top Trade Setups\n"
                f"6:00 Entry / SL / Target\n"
                f"9:00 Options Insight\n"
                f"11:00 Summary + Next Steps\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{stock_line}"
                f"{part1_line}"
                f"📱 Telegram (Live Signals): https://t.me/ai360trading\n"
                f"🌐 Website: https://ai360trading.in\n"
                f"📊 Free Watchlist: https://ai360trading.in/watchlist\n\n"
                f"🌍 Viewers: India, USA, UK, UAE, Canada, Australia\n"
                f"📈 Daily Nifty50 Analysis | Free Trading Signals\n\n"
                f"⚠️ Educational content only. Not SEBI registered advice.\n"
                f"Invest based on your own research and risk tolerance.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{hashtags}"
            )
        else:
            desc = (
                f"📈 {title}\n"
                f"🎯 {main_insight}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⏱️ TIMESTAMPS:\n"
                f"0:00 Market Overview — Nifty kahan hai\n"
                f"1:30 Aaj ke Key Levels\n"
                f"3:00 Top Trade Setups\n"
                f"6:00 Entry, SL aur Target\n"
                f"9:00 Options Hint\n"
                f"11:00 Summary\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{stock_line}"
                f"{part1_line}"
                f"📱 Telegram (Live Signals): https://t.me/ai360trading\n"
                f"🌐 Website: https://ai360trading.in\n"
                f"📊 Free Watchlist: https://ai360trading.in/watchlist\n\n"
                f"🇮🇳 Daily Nifty50 Analysis | Free Trading Signals India\n"
                f"🌍 For: India, UAE, USA, UK — NRI investors welcome!\n\n"
                f"⚠️ Educational content only. SEBI registered advice nahi hai.\n"
                f"Apni research karke invest karein.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{hashtags}"
            )

        return desc

    def _kids_description(self, title, main_insight, hashtags, today):
        return (
            f"🌟 {title}\n"
            f"✨ {main_insight}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📖 Aaj ki kahani mein kya hai:\n"
            f"0:00 Kahani shuru\n"
            f"1:00 Main character milta hai\n"
            f"2:30 Badi mushkil aati hai\n"
            f"4:00 Hero kya karta hai\n"
            f"5:30 Moral of the story\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔔 Subscribe karo roz ki kahani ke liye!\n"
            f"👪 Parents: Safe, educational, ad-appropriate stories\n"
            f"🌈 Languages: Hindi + English\n"
            f"👶 Age: 3–10 years\n\n"
            f"⭐ New story every day!\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{hashtags}"
        )

    def get_thumbnail_text(
        self,
        channel: str = "trading",
        stock: str = "",
        entry: str = "",
        target: str = "",
        pct: str = "",
        sector: str = "",
        mood: str = "BULLISH",
        level: str = "",
        story_theme: str = "",
        lang: str = "hi"
    ) -> dict:
        """
        Returns thumbnail text (3 lines + background color hint).
        Use these as overlays when rendering slide images.

        Returns: {line1, line2, line3, bg_color, text_color}
        """
        if channel == "kids":
            template = THUMBNAIL_TEMPLATES_KIDS[
                int(datetime.now(IST).strftime("%Y%m%d")) % len(THUMBNAIL_TEMPLATES_KIDS)
            ]
            return {
                "line1": template[0],
                "line2": template[1],
                "line3": template[2],
                "bg_color": (255, 180, 0),   # Bright yellow — kids CTR
                "text_color": (20, 20, 80),   # Dark blue on yellow
                "style": "kids"
            }

        templates = THUMBNAIL_TEMPLATES_TRADING_EN if lang == "en" else THUMBNAIL_TEMPLATES_TRADING
        seed = int(datetime.now(IST).strftime("%Y%m%d")) % len(templates)
        t = templates[seed]

        def fill(s):
            return (s.replace("{stock}", stock or "NIFTY")
                     .replace("{entry}", entry or "CMP")
                     .replace("{target}", target or "TGT")
                     .replace("{pct}", pct or "15")
                     .replace("{sector}", sector or "Market")
                     .replace("{mood}", mood or "ALERT")
                     .replace("{level}", level or "Key Level"))

        # Color based on mood
        if mood.upper() in ("BULLISH", "BUY"):
            bg = (0, 140, 60)    # Green
            tc = (255, 255, 255)
        elif mood.upper() in ("BEARISH", "SELL"):
            bg = (180, 30, 30)   # Red
            tc = (255, 255, 255)
        else:
            bg = (20, 20, 80)    # Dark blue
            tc = (255, 220, 0)   # Yellow text

        return {
            "line1": fill(t[0]),
            "line2": fill(t[1]),
            "line3": fill(t[2]),
            "bg_color": bg,
            "text_color": tc,
            "style": "trading"
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
        thumb = ht.get_thumbnail_text(stock="CGPOWER", ...)
    """

    def __init__(self):
        self.now_ist = datetime.now(IST)
        self.weekday = self.now_ist.weekday()
        self.seed    = int(self.now_ist.strftime("%Y%m%d"))
        random.seed(self.seed)

    def get_hook(self, mode: str = "market", lang: str = "hi",
                 holiday_name: str = "", channel: str = "trading") -> str:
        """Get a unique hook for today's content."""
        if channel == "kids":
            hooks = HOOKS_KIDS_ENGLISH if lang == "en" else HOOKS_KIDS_HINDI
            return hooks[self.seed % len(hooks)]

        if lang == "en":
            hooks = HOOKS_ENGLISH
        elif mode == "holiday":
            hooks = HOOKS_HINDI_HOLIDAY
        elif mode == "weekend":
            hooks = HOOKS_HINDI_WEEKEND
        else:
            hooks = HOOKS_HINDI_MARKET

        hook = hooks[self.seed % len(hooks)]
        if "{holiday}" in hook:
            hook = hook.replace("{holiday}", holiday_name or "aaj")
        return hook

    def get_cta(self, lang: str = "hi", channel: str = "trading") -> str:
        """Get a CTA variation for today."""
        if channel == "kids":
            ctas = CTAS_KIDS_ENGLISH if lang == "en" else CTAS_KIDS_HINDI
        else:
            ctas = CTAS_ENGLISH if lang == "en" else CTAS_HINDI
        return ctas[(self.seed + 3) % len(ctas)]

    def get_personal_phrase(self, lang: str = "hi") -> str:
        phrases = PERSONAL_PHRASES_ENGLISH if lang == "en" else PERSONAL_PHRASES_HINDI
        return random.choice(phrases)

    def get_tts_speed(self) -> float:
        """
        v2.0: Wider range 0.90–1.10 (was 0.95–1.05)
        Sounds more human, less robotic between videos.
        """
        speeds = [0.90, 0.93, 0.95, 0.97, 1.00, 1.02, 1.05, 1.08, 1.10]
        return speeds[self.seed % len(speeds)]

    def get_kids_tts_speed(self) -> float:
        """Kids stories: slightly slower (0.85–0.95) for clarity."""
        speeds = [0.85, 0.87, 0.90, 0.92, 0.95]
        return speeds[self.seed % len(speeds)]

    def get_kids_voice(self) -> str:
        """
        Recommended voices for kids stories.
        Rotate between warm female voices for variety.
        """
        voices = [
            "hi-IN-SwaraNeural",   # Hindi female — warm, clear
            "en-IN-NeerjaNeural",  # English Indian female — friendly
        ]
        return voices[self.seed % len(voices)]

    def get_searchable_title(
        self,
        content_type: str,
        topic_keyword: str,
        date_str: str = "",
        mode: str = "market",
        holiday_name: str = "",
        channel: str = "trading",
        stock: str = "",
        lang: str = "hi"
    ) -> str:
        """
        Central YouTube title builder for ALL generators.

        v2.0: Added stock name injection + kids channel support.

        Format rules (YouTube SEO):
          analysis  : "{STOCK} 🚀 {ACTION} | Nifty50 {date} | AI360 Trading"
          education : "{topic} {date} | Trading Education | AI360 Trading"
          reel      : "{topic} | AI360 Trading Shorts"
          short     : "{STOCK} Setup {date} | AI360 Trading"
          kids      : "{Story Theme} 🌟 | Hindi Kahani | {channel name}"
          holiday   : "{holiday} {year} | {topic} | AI360 Trading"

        Hard limit: 100 chars
        """
        if not date_str:
            date_str = datetime.now(IST).strftime("%d %b %Y")

        if channel == "kids":
            base = f"{topic_keyword} 🌟 | Hindi Kahani | Bacchon Ki Stories"
            return base[:100]

        channel_tag = "AI360 Trading"

        if mode == "holiday" and holiday_name:
            year = datetime.now(IST).year
            base = f"{holiday_name} {year} | {topic_keyword} | {channel_tag}"
        elif content_type == "analysis":
            # v2.0: Put stock name FIRST — people search stock names
            if stock:
                base = f"{stock} 🚀 {topic_keyword} | Nifty50 {date_str} | {channel_tag}"
            else:
                base = f"Nifty50 Analysis {date_str} | {topic_keyword} | {channel_tag}"
        elif content_type == "education":
            base = f"{topic_keyword} {date_str} | Trading Education | {channel_tag}"
        elif content_type == "reel":
            base = f"{topic_keyword} | {channel_tag} Shorts"
        elif content_type == "short":
            if stock:
                base = f"{stock} Trade Setup {date_str} | {channel_tag}"
            else:
                base = f"{topic_keyword} {date_str} | {channel_tag}"
        else:
            base = f"{topic_keyword} {date_str} | {channel_tag}"

        if len(base) > 100:
            suffix   = f" | {channel_tag}"
            max_front = 100 - len(suffix)
            base     = base[:max_front].rstrip(" |") + suffix

        return base[:100]

    def get_morning_reel_topic(self) -> dict:
        return MORNING_REEL_TOPICS[self.weekday]

    def get_kids_story_topic(self) -> dict:
        return KIDS_STORY_TOPICS[self.weekday]

    def humanize(self, text: str, lang: str = "hi") -> str:
        text = self._remove_robotic_patterns(text)
        text = self._vary_connectors(text, lang)
        text = self._inject_personal_phrase(text, lang)
        text = self._add_tts_pauses(text)
        return text.strip()

    def humanize_script_lines(self, lines: list, lang: str = "hi") -> list:
        result = []
        for i, line in enumerate(lines):
            line = self.humanize(line, lang)
            if i > 0 and i % 3 == 0 and random.random() > 0.6:
                filler = self._get_filler(lang)
                if filler:
                    result.append(filler)
            result.append(line)
        return result

    def get_emoji_set(self, mode: str = "market") -> list:
        sets = {
            "market":  ["📈", "📊", "🎯", "💹", "🔔", "⚡", "🚀", "💡", "🔥", "✅"],
            "weekend": ["📚", "🧠", "💡", "🌟", "🎯", "📖", "✨", "🏆", "💪", "🌱"],
            "holiday": ["🎉", "🌟", "✨", "🙏", "💫", "🎊", "❤️", "🌈", "🌸", "🎈"],
            "kids":    ["🌟", "✨", "🎉", "🦁", "🐘", "🌈", "🏰", "👑", "🦋", "💫"],
        }
        emoji_set = sets.get(mode, sets["market"])
        start = self.seed % len(emoji_set)
        return emoji_set[start:] + emoji_set[:start]

    def get_posting_time_tag(self, target_countries: list) -> str:
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
        replacements = {
            "Certainly! ": "", "Absolutely! ": "", "Of course! ": "",
            "Sure! ": "", "Great! ": "", "Indeed, ": "",
            "It's important to note that ": "",
            "It is worth noting that ": "",
            "In conclusion, ": "Toh basically, " if random.random() > 0.5 else "Ek baat clear hai — ",
            "In summary, ": "Short mein bolunga toh, ",
            "Furthermore, ": "Iske alawa, ",
            "Additionally, ": "Saath hi, ",
            "However, ": "Lekin, ",
            "Therefore, ": "Isliye, ",
            "It's important to": "Remember to",
            "You should consider": "Think about",
            "As an AI": "", "I'm an AI": "",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def _vary_connectors(self, text: str, lang: str) -> str:
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
        for old, new in connector_map.items():
            text = text.replace(old, new, 1)
        return text

    def _inject_personal_phrase(self, text: str, lang: str) -> str:
        if random.random() > 0.6:
            phrase    = self.get_personal_phrase(lang)
            sentences = text.split(". ")
            if len(sentences) > 2:
                mid = len(sentences) // 2
                sentences[mid] = f"{phrase} {sentences[mid].lower()}"
                text = ". ".join(sentences)
        return text

    def _add_tts_pauses(self, text: str) -> str:
        """Add natural pauses for TTS — comma after key phrases."""
        pause_words = ["lekin", "toh", "aur", "but", "so", "now", "here"]
        for word in pause_words:
            text = re.sub(rf'\b{word}\b(?!,)', f'{word},', text, count=1)
        return text

    def _get_filler(self, lang: str) -> str:
        fillers_hi = ["", "Suniye —", "Dekho,", "Sach mein,", "Waise,"]
        fillers_en = ["", "Now —", "Look,", "Here's the thing —", "So,"]
        fillers    = fillers_en if lang == "en" else fillers_hi
        filler     = random.choice(fillers)
        return filler if filler else ""


# ─────────────────────────────────────────────
# MODULE-LEVEL INSTANCES
# Used as: from human_touch import ht, seo
# ─────────────────────────────────────────────
ht  = HumanTouch()
seo = SEO()
