"""
human_touch.py — Anti-AI-Penalty Human Touch Engine
=====================================================
v2.1 CHANGES (May 2026):
- SEOTags.get_video_tags() — added channel, lang params (fixes TypeError)
- SEOTags.get_youtube_safe_tags() — new (ASCII-only, 480 char limit)
- SEOTags.format_article_tags() — new (Jekyll frontmatter format)
Last Updated: May 2026
"""

import random
import re
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

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

MORNING_REEL_TOPICS = {
    0: {"topic": "US/UK Weekend Market Recap",
        "angle": "What happened globally while Indian markets were closed",
        "target_country": ["USA", "UK", "India"],
        "hook_en": "While you were sleeping, global markets made a big move:",
        "hook_hi": "Weekend mein global markets mein yeh hua — dekhna zaroori hai:"},
    1: {"topic": "Trading Psychology",
        "angle": "One mindset shift that separates winners from losers",
        "target_country": ["India", "UAE"],
        "hook_en": "The real reason most traders fail has nothing to do with charts:",
        "hook_hi": "90% traders yeh galti karte hain — aur yeh chart se related nahi hai:"},
    2: {"topic": "Global Market Update",
        "angle": "Mid-week global picture — US, UK, Brazil, India",
        "target_country": ["USA", "UK", "Brazil", "India"],
        "hook_en": "Mid-week check — here's what global markets are telling us:",
        "hook_hi": "Hafte ke beech mein global market ka ek quick scan karte hain:"},
    3: {"topic": "Wealth Mindset",
        "angle": "One wealth principle successful investors follow",
        "target_country": ["UAE", "Canada", "Australia"],
        "hook_en": "One wealth principle that compound investors never break:",
        "hook_hi": "Ek rule jo sab successful investors follow karte hain — seriously:"},
    4: {"topic": "Weekend Strategy Preview",
        "angle": "What to watch, what to prepare before next week",
        "target_country": ["India", "USA", "UK"],
        "hook_en": "Before markets close today — here's your weekend prep list:",
        "hook_hi": "Weekend se pehle yeh 3 cheezein prepare kar lo — trading ke liye:"},
    5: {"topic": "Motivation + Lessons",
        "angle": "One trading lesson from a real market mistake",
        "target_country": ["Global"],
        "hook_en": "The lesson I learned the hard way — so you don't have to:",
        "hook_hi": "Ek galti jo maine ki — taaki aap na karein:"},
    6: {"topic": "Next Week Strategy",
        "angle": "Key levels, sector focus, and what to watch Monday",
        "target_country": ["USA", "UK", "India"],
        "hook_en": "Sunday prep: here's exactly what I'm watching for next week:",
        "hook_hi": "Kal market kholega — yeh levels aur sectors ready rakhna:"},
}


class HumanTouch:
    def __init__(self):
        self.now_ist = datetime.now(IST)
        self.weekday = self.now_ist.weekday()
        self.seed    = int(self.now_ist.strftime("%Y%m%d"))
        random.seed(self.seed)

    def get_hook(self, mode="market", lang="hi", holiday_name=""):
        if lang == "en":        hooks = HOOKS_ENGLISH
        elif mode == "holiday": hooks = HOOKS_HINDI_HOLIDAY
        elif mode == "weekend": hooks = HOOKS_HINDI_WEEKEND
        else:                   hooks = HOOKS_HINDI_MARKET
        hook = hooks[self.seed % len(hooks)]
        if "{holiday}" in hook:
            hook = hook.replace("{holiday}", holiday_name or "aaj")
        return hook

    def get_cta(self, lang="hi"):
        ctas = CTAS_ENGLISH if lang == "en" else CTAS_HINDI
        return ctas[(self.seed + 3) % len(ctas)]

    def get_personal_phrase(self, lang="hi"):
        phrases = PERSONAL_PHRASES_ENGLISH if lang == "en" else PERSONAL_PHRASES_HINDI
        return random.choice(phrases)

    def get_tts_speed(self):
        speeds = [0.95, 0.97, 1.00, 1.02, 1.05]
        return speeds[self.seed % len(speeds)]

    def get_searchable_title(self, content_type, topic_keyword, date_str="", mode="market", holiday_name=""):
        if not date_str:
            date_str = datetime.now(IST).strftime("%d %b %Y")
        channel = "AI360 Trading"
        if mode == "holiday" and holiday_name:
            base = f"{holiday_name} {datetime.now(IST).year} | {topic_keyword} | {channel}"
        elif content_type == "analysis":
            base = f"Nifty50 Analysis {date_str} | {topic_keyword} | {channel}"
        elif content_type == "education":
            base = f"{topic_keyword} {date_str} | Trading Education | {channel}"
        elif content_type == "reel":
            base = f"{topic_keyword} | {channel} Shorts"
        elif content_type == "short":
            base = f"{topic_keyword} {date_str} | {channel}"
        else:
            base = f"{topic_keyword} {date_str} | {channel}"
        if len(base) > 95:
            suffix = f" | {channel}"
            base   = base[:95 - len(suffix)].rstrip(" |") + suffix
        return base[:100]

    def get_morning_reel_topic(self):
        return MORNING_REEL_TOPICS[self.weekday]

    def humanize(self, text, lang="hi"):
        text = self._remove_robotic_patterns(text)
        text = self._vary_connectors(text, lang)
        text = self._inject_personal_phrase(text, lang)
        text = self._add_tts_pauses(text)
        return text.strip()

    def humanize_script_lines(self, lines, lang="hi"):
        result = []
        for i, line in enumerate(lines):
            line = self.humanize(line, lang)
            if i > 0 and i % 3 == 0 and random.random() > 0.6:
                filler = self._get_filler(lang)
                if filler:
                    result.append(filler)
            result.append(line)
        return result

    def get_emoji_set(self, mode="market"):
        sets = {
            "market":  ["📈","📊","🎯","💹","🔔","⚡","🚀","💡","🔥","✅"],
            "weekend": ["📚","🧠","💡","🌟","🎯","📖","✨","🏆","💪","🌱"],
            "holiday": ["🎉","🌟","✨","🙏","💫","🎊","❤️","🌈","🌸","🎈"],
        }
        emoji_set = sets.get(mode, sets["market"])
        start = self.seed % len(emoji_set)
        return emoji_set[start:] + emoji_set[:start]

    def get_posting_time_tag(self, target_countries):
        if any(c in ["USA","UK","Canada","Australia"] for c in target_countries):
            return "#USStocks #UKInvesting #GlobalInvesting #FinanceWorld"
        elif "UAE" in target_countries:
            return "#UAEInvesting #NRIInvestors #DubaiFinance #GlobalStocks"
        elif "Brazil" in target_countries:
            return "#BrazilMarket #BrazilFinance #GlobalInvesting"
        return "#Nifty50 #TradingIndia #StockMarketIndia #BankNifty"

    def _remove_robotic_patterns(self, text):
        replacements = {
            "Certainly! ":"","Absolutely! ":"","Of course! ":"",
            "Sure! ":"","Great! ":"","Indeed, ":"",
            "It's important to note that ":"","It is worth noting that ":"",
            "In conclusion, ":"Toh basically, " if random.random()>0.5 else "Ek baat clear hai — ",
            "In summary, ":"Short mein bolunga toh, ",
            "Furthermore, ":"Iske alawa, ","Additionally, ":"Saath hi, ",
            "However, ":"Lekin, ","Therefore, ":"Isliye, ",
            "It's important to":"Remember to",
            "You should consider":"Think about",
            "As an AI":"","I'm an AI":"",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def _vary_connectors(self, text, lang):
        if lang == "hi":
            connector_map = {
                "aur ":    random.choice(["aur ","saath hi ","plus "]),
                "lekin ":  random.choice(["lekin ","but ","par "]),
                "kyunki ": random.choice(["kyunki ","because ","isliye ki "]),
            }
        else:
            connector_map = {
                "and ":     random.choice(["and ","plus ","also "]),
                "but ":     random.choice(["but ","however, ","yet "]),
                "because ": random.choice(["because ","since ","as "]),
            }
        for old, new in connector_map.items():
            text = text.replace(old, new, 1)
        return text

    def _inject_personal_phrase(self, text, lang):
        if random.random() > 0.6:
            phrase    = self.get_personal_phrase(lang)
            sentences = text.split(". ")
            if len(sentences) > 2:
                mid = len(sentences) // 2
                sentences[mid] = f"{phrase} {sentences[mid].lower()}"
                text = ". ".join(sentences)
        return text

    def _add_tts_pauses(self, text):
        text = re.sub(r'(\d+)\s+(percent|%)', r'\1 \2,', text)
        text = text.replace(" — ", ", ")
        return text

    def _get_filler(self, lang):
        fillers_hi = ["Chaliye aage badhte hain.","Ab doosri important baat.",
                      "Yeh toh tha ek angle.","Ek aur cheez dhyan mein rakhna."]
        fillers_en = ["Now, here's the next part.","Moving on to something important.",
                      "Let me show you another angle.","Keep this in mind as well."]
        fillers = fillers_en if lang == "en" else fillers_hi
        return random.choice(fillers) if random.random() > 0.5 else ""


class SEOTags:
    """
    v2.1: get_video_tags() now accepts channel + lang (fixes TypeError).
    New: get_youtube_safe_tags(), format_article_tags()
    """

    BASE_TAGS = [
        "AI360Trading","StockMarket","Trading","Investing",
        "Nifty50","TradingIndia","StockMarketIndia","BankNifty",
        "Finance","FinancialLiteracy","SwingTrading","TechnicalAnalysis",
    ]
    GLOBAL_TAGS = [
        "USStocks","UKInvesting","GlobalInvesting","BrazilMarket",
        "UAEInvesting","FinanceWorld","StockMarketNews","InvestingTips",
    ]
    MARKET_TAGS = [
        "NiftyAnalysis","MarketToday","BreakoutStocks","TradingSignals",
        "SwingTrade","Nifty50Analysis","StockPicks","MarketUpdate",
        "FIIData","BullMarket","TradingSetup","NiftyPrediction",
    ]
    EDUCATION_TAGS = [
        "TradingEducation","LearnTrading","TradingForBeginners",
        "InvestmentTips","WealthBuilding","PersonalFinance",
        "TradingPsychology","StockMarketBasics","FinancialFreedom",
        "PassiveIncome","MoneyManagement","InvestingForBeginners",
    ]
    SHORTS_TAGS = [
        "Shorts","YouTubeShorts","StockMarketShorts","TradingShorts",
        "NiftyShorts","ViralFinance","FinanceShorts",
    ]

    def get_video_tags(self, mode="market", is_short=False, channel="trading", lang="both"):
        """channel and lang accepted for compatibility — v2.1 fix."""
        tags = list(self.BASE_TAGS)
        tags += self.MARKET_TAGS if mode == "market" else self.EDUCATION_TAGS
        tags += self.GLOBAL_TAGS
        if is_short:
            tags += self.SHORTS_TAGS
        seen, result = set(), []
        for t in tags:
            if t not in seen:
                seen.add(t)
                result.append(t)
        return result[:40]

    def get_youtube_safe_tags(self, tags):
        """ASCII-only tags, total under 480 chars for YouTube API."""
        safe   = [t for t in tags if t.isascii()]
        result, total = [], 0
        for tag in safe:
            if total + len(tag) + 1 <= 480:
                result.append(tag)
                total += len(tag) + 1
            else:
                break
        return result

    def format_article_tags(self, tags, max_tags=15):
        """Format tags for Jekyll article frontmatter YAML."""
        safe = [t for t in tags if t.isascii()][:max_tags]
        return "[" + ", ".join(f'"{t}"' for t in safe) + "]"

    def get_description_tags(self, mode="market", lang="hi"):
        """Get hashtag string for video descriptions."""
        tags = self.get_video_tags(mode=mode, is_short=False)
        safe = self.get_youtube_safe_tags(tags)
        return " ".join(f"#{t}" for t in safe[:12])


# Singleton instances — import in all generators as:
# from human_touch import ht, seo
ht  = HumanTouch()
seo = SEOTags()
