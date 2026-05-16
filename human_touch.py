"""
human_touch.py — Anti-AI-Penalty Human Touch Engine
=====================================================
v2.2 CHANGES (May 2026):
- Education hooks added — fixes wrong "chart/setup" language in education videos
- get_hook(mode="education") now works correctly
- safe_thumbnail_text() — strips Devanagari only, keeps Rs. and numbers
- safe_tts_price() — TTS-friendly price format, no Rs. symbol confusion
- get_prompt_rules() — standard AI rules injected into ALL generators
- get_video_description() — proper description builder for all content types
- SEOTags improved — education tags, shorts tags, proper global mix
- All fixes permanent — every generator that imports human_touch gets them

PERMANENT FIXES (all generators, all stocks, forever):
  1. Thumbnail text = English only (Hindi in audio only)
  2. Numbers = exact from Google Sheet, AI must not change
  3. Education videos = education hooks (no chart/trading language)
  4. TTS = no Rs. symbol in spoken script
  5. Description = proper links, tags, disclaimer for every video

Author: AI360Trading Automation
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

HOOKS_HINDI_EDUCATION = [
    "Aaj ek cheez seekhenge jo har successful investor jaanta hai:",
    "Stock market mein kamyaab hone ka ek simple concept hai —",
    "Yeh concept main chahta hoon aap bilkul clear kar lo:",
    "Ek cheez jo main karta toh losses hote — aaj share karta hoon:",
    "Beginners yeh galti karte hain — aap mat karna:",
    "Is ek concept ko samjh lo — baaki sab aasaan ho jayega:",
    "Jo log sirf tip follow karte hain, woh yeh kabhi nahi seekhte:",
    "Investing ka sabse important rule — jo koi nahi batata:",
    "Aaj ek concept jo aapki financial life badal sakta hai:",
    "Agar yeh ek cheez samajh lo — market aapko dar nahi sakti:",
    "Mere hisaab se yeh sabse important financial concept hai:",
    "Trading sikhni hai? Pehle yeh samjho:",
    "Is hafta hum seekhenge — aur yeh lifetime kaam aayega:",
    "Ek concept — do examples — aur aap expert ban jaoge:",
    "Aaj ki seekh simple hai lekin powerful hai:",
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

HOOKS_ENGLISH_EDUCATION = [
    "One concept that every investor needs to understand:",
    "This is the simplest explanation of this topic you'll find:",
    "Most people learn this the hard way — you won't have to:",
    "If you're new to investing, start right here:",
    "This one concept will change how you think about money:",
    "Let me break down something most teachers overcomplicate:",
    "Week by week, we're building your complete trading knowledge:",
    "Here's what schools never teach you about money:",
    "No jargon, no confusion — just the concept, clearly explained:",
    "This is the foundation — everything else builds on this:",
    "Understanding this separates investors from speculators:",
    "In the next few minutes, you'll understand what took me years:",
    "The most important financial concept of this week:",
    "Simple concept, powerful results — let's learn together:",
    "Your financial education starts here — one topic at a time:",
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
    "Comment mein batao — aap kya sochte ho is topic ke baare mein? 💬",
    "Telegram link bio mein hai — wahan live signals milte hain! 📱",
    "Agar ek bhi cheez useful lagi toh like zaroor karo! 👍",
    "Agle video mein aur detail mein baat karenge — subscribe karo! 🔔",
    "Apna view share karo comment mein — community se seekhte hain! 💡",
]

CTAS_HINDI_EDUCATION = [
    "Next week ka topic bhi equally important hai — subscribe karo! 🔔",
    "Yeh concept apne dost ko bhi batao — share karo! 📤",
    "Comment mein batao — kya yeh clear hua? 💬",
    "Like karo agar is series se seekh rahe ho! 👍",
    "Week 2 mein aur depth mein jaayenge — subscribe zaroor karo! 🔔",
    "Telegram join karo — wahan live examples milte hain! 📱",
    "Aapka sawal hai? Comment karo — main personally jawab dunga! 💬",
    "Is 52-week course mein sab kuch cover hoga — subscribe free hai! ✅",
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

CTAS_ENGLISH_EDUCATION = [
    "Subscribe for the full 52-week investing course — it's free! 🔔",
    "Share this with someone who needs to start their investing journey! 📤",
    "Next week's topic builds on this — don't miss it! 🔔",
    "Drop a question in the comments — I'll answer every one! 💬",
    "Like if this cleared up a concept you were confused about! 👍",
    "Join our Telegram for live trading examples! 📱",
    "This is Week {week} of 52 — catch up on what you missed! ✅",
    "Save this video — you'll want to refer back to it! 📌",
]


# ─────────────────────────────────────────────
# MORNING REEL TOPICS BY DAY
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# MAIN HumanTouch CLASS
# ─────────────────────────────────────────────

class HumanTouch:
    """
    Injects human-like qualities into AI-generated content.
    v2.2: Education mode added. Permanent fixes for Hindi/TTS/numbers.

    Usage:
        from human_touch import ht, seo
        hook  = ht.get_hook(mode="education", lang="hi", week=1)
        rules = ht.get_prompt_rules(lang="hi", cmp=1446, sl=1380, target=1550)
    """

    def __init__(self):
        self.now_ist = datetime.now(IST)
        self.weekday = self.now_ist.weekday()
        self.seed    = int(self.now_ist.strftime("%Y%m%d"))
        random.seed(self.seed)

    def get_hook(self, mode: str = "market", lang: str = "hi",
                 holiday_name: str = "", week: int = 0) -> str:
        """
        Get a unique hook for today's content.
        mode: "market", "education", "weekend", "holiday"
        week: used for education mode to vary hooks by week number
        """
        if lang == "en":
            if mode == "education":
                hooks = HOOKS_ENGLISH_EDUCATION
            else:
                hooks = HOOKS_ENGLISH
        elif mode == "education":
            hooks = HOOKS_HINDI_EDUCATION
        elif mode == "holiday":
            hooks = HOOKS_HINDI_HOLIDAY
        elif mode == "weekend":
            hooks = HOOKS_HINDI_WEEKEND
        else:
            hooks = HOOKS_HINDI_MARKET

        # Use week number as seed offset for education so each week is different
        seed_offset = week if week > 0 else 0
        hook = hooks[(self.seed + seed_offset) % len(hooks)]

        if "{holiday}" in hook:
            hook = hook.replace("{holiday}", holiday_name or "aaj")

        return hook

    def get_cta(self, lang: str = "hi", mode: str = "market", week: int = 0) -> str:
        """Get a CTA variation. Education mode gets education-specific CTAs."""
        if lang == "en":
            ctas = CTAS_ENGLISH_EDUCATION if mode == "education" else CTAS_ENGLISH
        else:
            ctas = CTAS_HINDI_EDUCATION if mode == "education" else CTAS_HINDI

        cta = ctas[(self.seed + 3) % len(ctas)]
        if "{week}" in cta:
            cta = cta.replace("{week}", str(week or 1))
        return cta

    def get_personal_phrase(self, lang: str = "hi") -> str:
        phrases = PERSONAL_PHRASES_ENGLISH if lang == "en" else PERSONAL_PHRASES_HINDI
        return random.choice(phrases)

    def get_tts_speed(self) -> float:
        speeds = [0.95, 0.97, 1.00, 1.02, 1.05]
        return speeds[self.seed % len(speeds)]

    def get_searchable_title(self, content_type: str, topic_keyword: str,
                             date_str: str = "", mode: str = "market",
                             holiday_name: str = "") -> str:
        """Central YouTube title builder for ALL generators."""
        if not date_str:
            date_str = datetime.now(IST).strftime("%d %b %Y")
        channel = "AI360 Trading"
        if mode == "holiday" and holiday_name:
            base = f"{holiday_name} {datetime.now(IST).year} | {topic_keyword} | {channel}"
        elif content_type == "analysis":
            base = f"Nifty50 Analysis {date_str} | {topic_keyword} | {channel}"
        elif content_type == "education":
            base = f"{topic_keyword} | Trading Education | {channel}"
        elif content_type == "reel":
            base = f"{topic_keyword} | {channel} Shorts"
        elif content_type == "short":
            base = f"{topic_keyword} | {channel} #Shorts"
        else:
            base = f"{topic_keyword} {date_str} | {channel}"
        if len(base) > 95:
            suffix = f" | {channel}"
            base   = base[:95 - len(suffix)].rstrip(" |") + suffix
        return base[:100]

    def get_morning_reel_topic(self) -> dict:
        return MORNING_REEL_TOPICS[self.weekday]

    def get_video_description(self, mode: str = "market", lang: str = "hi",
                               stock: str = "", week: int = 0,
                               topic: str = "") -> str:
        """
        Standard description builder for ALL generators.
        Includes proper links, hashtags, disclaimer.
        Never empty. Always SEO-optimised.
        """
        tg_link   = "https://t.me/ai360trading"
        site_link = "https://ai360trading.in"
        disclaimer = (
            "Educational content only. Not SEBI registered. "
            "Not financial advice. Invest at your own risk."
            if lang == "en" else
            "Sirf educational content. SEBI registered nahi. "
            "Financial advice nahi. Apne risk pe invest karein."
        )

        if mode == "education":
            if lang == "en":
                desc = (
                    f"Week {week} of our free 52-week investing course.\n"
                    f"Today's topic: {topic}\n\n"
                    f"Complete investing education — from basics to advanced.\n"
                    f"New video every week. Subscribe and never miss a lesson.\n\n"
                    f"Join our Telegram for live trading signals: {tg_link}\n"
                    f"Website: {site_link}\n\n"
                    f"{disclaimer}"
                )
            else:
                desc = (
                    f"52-week free investing course — Week {week}.\n"
                    f"Aaj ka topic: {topic}\n\n"
                    f"Beginner se advanced tak — poori investing education.\n"
                    f"Har week nayi video. Subscribe karo aur ek bhi miss mat karo.\n\n"
                    f"Live trading signals ke liye Telegram join karo: {tg_link}\n"
                    f"Website: {site_link}\n\n"
                    f"{disclaimer}"
                )
        elif mode in ("weekend", "holiday"):
            if lang == "en":
                desc = (
                    f"Weekend learning — build your trading knowledge.\n"
                    f"Join our free Telegram for daily signals: {tg_link}\n"
                    f"Website: {site_link}\n\n{disclaimer}"
                )
            else:
                desc = (
                    f"Weekend learning — trading knowledge build karo.\n"
                    f"Free Telegram join karo daily signals ke liye: {tg_link}\n"
                    f"Website: {site_link}\n\n{disclaimer}"
                )
        else:
            # Market mode
            stock_str = f"\nStock: {stock}" if stock else ""
            if lang == "en":
                desc = (
                    f"Daily market analysis and trading signals.{stock_str}\n\n"
                    f"Free Telegram for live signals: {tg_link}\n"
                    f"Membership (Advance + Premium): {site_link}/membership\n"
                    f"Website: {site_link}\n\n{disclaimer}"
                )
            else:
                desc = (
                    f"Daily market analysis aur trading signals.{stock_str}\n\n"
                    f"Free Telegram live signals ke liye: {tg_link}\n"
                    f"Membership (Advance + Premium): {site_link}/membership\n"
                    f"Website: {site_link}\n\n{disclaimer}"
                )
        return desc

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
            "market":    ["📈","📊","🎯","💹","🔔","⚡","🚀","💡","🔥","✅"],
            "education": ["📚","🧠","💡","🌟","✏️","📖","✨","🏆","💪","🎓"],
            "weekend":   ["📚","🧠","💡","🌟","🎯","📖","✨","🏆","💪","🌱"],
            "holiday":   ["🎉","🌟","✨","🙏","💫","🎊","❤️","🌈","🌸","🎈"],
        }
        emoji_set = sets.get(mode, sets["market"])
        start = self.seed % len(emoji_set)
        return emoji_set[start:] + emoji_set[:start]

    def get_posting_time_tag(self, target_countries: list) -> str:
        if any(c in ["USA","UK","Canada","Australia"] for c in target_countries):
            return "#USStocks #UKInvesting #GlobalInvesting #FinanceWorld"
        elif "UAE" in target_countries:
            return "#UAEInvesting #NRIInvestors #DubaiFinance #GlobalStocks"
        elif "Brazil" in target_countries:
            return "#BrazilMarket #BrazilFinance #GlobalInvesting"
        return "#Nifty50 #TradingIndia #StockMarketIndia #BankNifty"

    # ── PRIVATE HELPERS ───────────────────────────────────────────────────────

    def _remove_robotic_patterns(self, text: str) -> str:
        replacements = {
            "Certainly! ":"","Absolutely! ":"","Of course! ":"",
            "Sure! ":"","Great! ":"","Indeed, ":"",
            "It's important to note that ":"",
            "It is worth noting that ":"",
            "In conclusion, ":"Toh basically, ",
            "In summary, ":"Short mein bolunga toh, ",
            "Furthermore, ":"Iske alawa, ",
            "Additionally, ":"Saath hi, ",
            "However, ":"Lekin, ",
            "Therefore, ":"Isliye, ",
            "It's important to":"Remember to",
            "You should consider":"Think about",
            "As an AI":"",
            "I'm an AI":"",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def _vary_connectors(self, text: str, lang: str) -> str:
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
        text = re.sub(r'(\d+)\s+(percent|%)', r'\1 \2,', text)
        text = text.replace(" — ", ", ")
        return text

    def _get_filler(self, lang: str) -> str:
        fillers_hi = ["Chaliye aage badhte hain.","Ab doosri important baat.",
                      "Yeh toh tha ek angle.","Ek aur cheez dhyan mein rakhna."]
        fillers_en = ["Now, here's the next part.","Moving on to something important.",
                      "Let me show you another angle.","Keep this in mind as well."]
        fillers = fillers_en if lang == "en" else fillers_hi
        return random.choice(fillers) if random.random() > 0.5 else ""


# ═════════════════════════════════════════════════════════════════════════════
# PERMANENT FIX FUNCTIONS — v2.2
# Used by ALL generators. Fixes Hindi, TTS, numbers FOREVER.
# ═════════════════════════════════════════════════════════════════════════════

def safe_thumbnail_text(text: str, fallback: str = "") -> str:
    """
    Strip Devanagari Hindi characters from thumbnail text.
    Keeps: English, numbers, Rs., %, +, -, punctuation.
    Prevents "पा" artifact in PIL rendering.

    Usage in any generator:
        line1 = safe_thumbnail_text(ai_output["line1"], sym)
        line2 = safe_thumbnail_text(ai_output["line2"], "BREAKOUT!")
    """
    cleaned = re.sub(r'[\u0900-\u097F]+', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned if cleaned else (fallback or text[:10])


def safe_tts_price(val: float, lang: str = "hi") -> str:
    """
    Format price for TTS — no Rs. symbol (causes reading issues in edge-tts).

    Hindi: "1457 rupaye"
    English: "1457 rupees"

    Usage in any generator:
        sl_tts  = safe_tts_price(sl, lang=LANG)
        tgt_tts = safe_tts_price(target, lang=LANG)
        # Use sl_tts in spoken script — NOT "Rs.1457"
    """
    if val <= 0:
        return "market price pe" if lang == "hi" else "at market price"
    rounded = int(round(val))
    return f"{rounded} rupaye" if lang == "hi" else f"{rounded} rupees"


def validate_stock_numbers(sl: float, target: float, cmp: float) -> dict:
    """
    Validate SL and Target from Google Sheet (AlertLog col H and I).
    These come from AppScript (2xATR for SL, 4xATR for target) — trusted source.
    Only basic sanity checks needed — not range estimation.

    Checks:
      - SL > 0 and SL < CMP (SL must be below entry)
      - Target > 0 and Target > CMP (target must be above entry)

    Returns validated dict with any warnings printed.
    Does NOT guess or recalculate — trusts Sheet values.

    Usage in any generator:
        v  = validate_stock_numbers(sl, target, cmp)
        sl = v["sl"]
        target = v["target"]
    """
    warnings = []
    result   = {"sl": sl, "target": target, "warnings": []}

    if cmp <= 0:
        return result

    # SL must be below CMP
    if sl > 0 and sl >= cmp:
        warnings.append(f"SL {sl} >= CMP {cmp} — Sheet data may be stale, using 3%")
        sl = round(cmp * 0.97, 2)

    # Target must be above CMP
    if target > 0 and target <= cmp:
        warnings.append(f"Target {target} <= CMP {cmp} — clearing")
        target = 0

    result["sl"]       = sl
    result["target"]   = target
    result["warnings"] = warnings
    for w in warnings:
        print(f"[VALIDATE] ⚠️ {w}")

    return result


def get_prompt_rules(lang: str = "hi", sym: str = "",
                     cmp: float = 0, sl: float = 0,
                     target: float = 0, mode: str = "market") -> str:
    """
    Standard rules injected into EVERY AI prompt in every generator.
    Permanently fixes: Hindi in thumbnail, wrong numbers, TTS symbol issues.

    Usage in any generator (add to end of every prompt):
        rules  = get_prompt_rules(lang=LANG, sym=sym, cmp=cmp, sl=sl, target=target)
        prompt = f"...your prompt...\n\n{rules}"
    """
    cmp_disp = f"Rs.{int(round(cmp))}"    if cmp > 0    else "live price"
    sl_disp  = f"Rs.{int(round(sl))}"     if sl > 0     else "see chart"
    tgt_disp = f"Rs.{int(round(target))}" if target > 0 else "next level"
    cmp_tts  = safe_tts_price(cmp, lang)
    sl_tts   = safe_tts_price(sl, lang)
    tgt_tts  = safe_tts_price(target, lang)

    if mode == "education":
        return f"""
CRITICAL RULES — follow exactly:

RULE 1 — THIS IS AN EDUCATION VIDEO, NOT A TRADING SETUP:
  - Do NOT mention specific stocks, charts, or trading setups
  - Do NOT use "aaj ka market" or "chart pattern" language
  - Write as a teacher explaining a concept to a student

RULE 2 — THUMBNAIL TEXT (thumbnail_text_line1, thumbnail_text_line2):
  - English characters ONLY — no Hindi/Devanagari script
  - line1: topic name — max 10 chars, ALL CAPS (e.g. "BASICS", "RSI", "SIP")
  - line2: benefit phrase — max 18 English chars (e.g. "START HERE", "WEEK 1")
  - NEVER write Hindi words like "पाइए", "पर", "है" in thumbnail lines

RULE 3 — TITLE:
  - Format: "Topic Name | Week N | AI360 Trading"
  - No random percentages, no question marks unless meaningful
  - Examples: "Stock Market Basics | Week 1 | AI360 Trading"
"""
    else:
        return f"""
CRITICAL RULES — follow exactly:

RULE 1 — THUMBNAIL TEXT (thumbnail_text_line1, thumbnail_text_line2):
  - English characters ONLY — no Hindi/Devanagari script in these two fields
  - line1: stock name or % move — max 10 chars, ALL CAPS
  - line2: short phrase — max 18 English chars
  - NEVER write: "पाइए", "पर", "है", or any Hindi/Devanagari word in thumbnail

RULE 2 — EXACT NUMBERS from Google Sheet — NEVER change these:
  - Entry (CMP): {cmp_disp} — use exactly this value
  - Stop Loss:   {sl_disp}  — use exactly this value
  - Target:      {tgt_disp} — use exactly this value
  - Do NOT divide, do NOT add decimals, do NOT invent new prices

RULE 3 — SPOKEN SCRIPT (full_script for TTS audio):
  - No Rs. symbol — write prices as words: {cmp_tts}, SL {sl_tts}, target {tgt_tts}
  - Hindi is fine in full_script — this goes to audio only, NOT thumbnail
  - full_script can be natural Hindi/English — thumbnail must be English
"""


# ─────────────────────────────────────────────
# SEO TAGS CLASS
# ─────────────────────────────────────────────

class SEOTags:
    """
    v2.2: Proper tags for market, education, shorts, kids.
    Education videos get education-specific tags (not trading tags).
    Shorts get viral/Shorts-specific tags.
    All tags include India + Global mix for CPM.
    """

    BASE_TAGS = [
        "AI360Trading","StockMarket","Trading","Investing",
        "Nifty50","TradingIndia","StockMarketIndia","BankNifty",
        "Finance","FinancialLiteracy","SwingTrading","TechnicalAnalysis",
    ]
    GLOBAL_TAGS = [
        "USStocks","UKInvesting","GlobalInvesting","BrazilMarket",
        "UAEInvesting","FinanceWorld","StockMarketNews","InvestingTips",
        "NRIInvestors","IndianStockMarket",
    ]
    MARKET_TAGS = [
        "NiftyAnalysis","MarketToday","BreakoutStocks","TradingSignals",
        "SwingTrade","Nifty50Analysis","StockPicks","MarketUpdate",
        "FIIData","BullMarket","TradingSetup","NiftyPrediction",
        "Nifty500","Sensex","NSEIndia","BSEIndia",
    ]
    EDUCATION_TAGS = [
        "TradingEducation","LearnTrading","TradingForBeginners",
        "InvestmentTips","WealthBuilding","PersonalFinance",
        "TradingPsychology","StockMarketBasics","FinancialFreedom",
        "PassiveIncome","MoneyManagement","InvestingForBeginners",
        "StockMarketCourse","FreeInvestingCourse","LearnInvesting",
        "FinancialEducation","WealthCreation","MoneyMindset",
    ]
    SHORTS_TAGS = [
        "Shorts","YouTubeShorts","StockMarketShorts","TradingShorts",
        "NiftyShorts","ViralFinance","FinanceShorts","StocksShorts",
        "MarketShorts","TradingTips",
    ]
    KIDS_TAGS = [
        "KidsStories","AnimatedStories","ChildrenEducation","MoralStories",
        "KidsCartoon","HindiKahani","KidsEnglish","HerooQuest",
        "PixarStyle","EducationalKids","KidsLearning","FamilyFriendly",
    ]

    def get_video_tags(self, mode: str = "market", is_short: bool = False,
                       channel: str = "trading", lang: str = "both") -> list:
        """
        Get SEO tags. Mode determines tag mix.
        channel="kids" returns kids-specific tags.
        is_short=True adds Shorts-specific tags.
        """
        if channel == "kids":
            tags = list(self.KIDS_TAGS) + ["AI360Trading","Finance","Education"]
            return tags[:40]

        tags = list(self.BASE_TAGS)

        if mode == "education":
            tags += self.EDUCATION_TAGS
        else:
            tags += self.MARKET_TAGS

        tags += self.GLOBAL_TAGS

        if is_short:
            tags += self.SHORTS_TAGS

        seen, result = set(), []
        for t in tags:
            if t not in seen:
                seen.add(t)
                result.append(t)
        return result[:40]

    def get_youtube_safe_tags(self, tags: list) -> list:
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

    def format_article_tags(self, tags: list, max_tags: int = 15) -> str:
        """Format tags for Jekyll article frontmatter YAML."""
        safe = [t for t in tags if t.isascii()][:max_tags]
        return "[" + ", ".join(f'"{t}"' for t in safe) + "]"

    def get_description_tags(self, mode: str = "market", lang: str = "hi") -> str:
        """Get hashtag string for video descriptions."""
        tags = self.get_video_tags(mode=mode, is_short=False)
        safe = self.get_youtube_safe_tags(tags)
        return " ".join(f"#{t}" for t in safe[:12])


# ─────────────────────────────────────────────
# SINGLETON INSTANCES
# from human_touch import ht, seo
# ─────────────────────────────────────────────
ht  = HumanTouch()
seo = SEOTags()
