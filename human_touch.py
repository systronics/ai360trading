"""
human_touch.py — Anti-AI-Penalty Human Touch Engine
=====================================================
v2.3 (2026-07-19) — RETENTION HOOK REWRITE:
  All hook libraries rewritten number-first/question-first (measured problem:
  viewers leave in 2-5s; old hooks warmed up slowly). Honesty rule: hooks carry
  NO invented stats — only evergreen math (SIP/72-rule/compounding) or promises
  the AI fills with real data. List names/sizes unchanged; {holiday}/{week}
  placeholders preserved.

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

# v2.3 (2026-07-19) RETENTION REWRITE — first 3 words must punch (measured
# problem: viewers leave in 2-5s). Number-first / question-first, payoff
# promised upfront. HONESTY RULE: no invented stats — numbers here are either
# evergreen math or filled by the AI from real data after the hook.
HOOKS_HINDI_MARKET = [
    "Aaj ka sabse bada number — yeh raha:",
    "Ek level. Ek plan. 30 second:",
    "Aaj market ne ek clear signal diya — dekho:",
    "Ye setup roz nahi banta — aaj bana hai:",
    "3 second do — aaj ka most important level:",
    "Aaj ka move samjhe bina kal trade mat karna:",
    "Chart pe aaj ek cheez chhupi hai — yeh:",
    "Kal ke liye sirf ek number yaad rakho:",
    "Aaj kya badla? Ek line mein — yeh:",
    "Trade plan ready hai — entry, SL, target:",
    "Nifty ka aaj ka sach — seedha point pe:",
    "Aaj ka chart ek kahani bata raha hai:",
    "Paisa plan se banta hai, tip se nahi — plan yeh:",
    "Aaj ka key level cross hua toh kya hoga?",
    "Ek pattern aaj phir dikha — matlab yeh:",
    "Market ka aaj ka message — 20 second mein:",
    "Aaj ke top mover ke peeche ki wajah:",
    "Kal subah se pehle yeh ek cheez dekh lo:",
    "Aaj ka setup — bina bakwas, seedha data:",
    "Yeh level toota toh scene badal jayega:",
]

HOOKS_HINDI_WEEKEND = [
    "72 ka rule — paisa kitne saal mein double? Dekho:",
    "₹500 se investing shuru hoti hai — kaise? Yeh:",
    "2 minute ka concept — poori trading badal sakta hai:",
    "Monday se pehle yeh ek cheez samajh lo:",
    "Ek galti jo naye trader baar baar karte hain:",
    "Weekend ka sabse valuable 30 second — yeh:",
    "Compounding ka asli magic — ek example mein:",
    "SIP vs FD — farak ek chart mein dekho:",
    "Market band hai — ab seekhne ka time hai:",
    "Ek concept jo school mein nahi padhaya — paisa:",
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
# v2.3 — number-first rewrite (evergreen math only, no invented stats)
HOOKS_HINDI_EDUCATION = [
    "₹5,000 ki SIP, 20 saal — kitna? Suno:",
    "₹500 se bhi shuru ho sakte ho — kaise? Yeh:",
    "72 ka rule — 10 second mein seekho:",
    "Ek concept — aur paisa samajh aa jayega:",
    "Compounding: duniya ka aathwan ajooba — example:",
    "Pehla demat account — 5 minute ka kaam, dekho:",
    "SIP kya hai? Ek chai ke price se samjho:",
    "Inflation aapka paisa roz khaata hai — bachao aise:",
    "Beginner ho? Pehli galti yeh mat karna:",
    "Aaj ka lesson chhota hai — fayda lifetime ka:",
]

# v2.3 RETENTION REWRITE — punch in the first 3 words, payoff promised
# upfront, no invented stats (real numbers come from the data after the hook).
HOOKS_ENGLISH = [
    "One number moved everything today — this one:",
    "One level. One plan. Thirty seconds:",
    "Today's chart says one clear thing:",
    "Remember one number for tomorrow — this:",
    "Stop guessing. Here's the actual data:",
    "This setup doesn't form every day — today it did:",
    "Three seconds — today's most important level:",
    "Before tomorrow's open, see this one thing:",
    "Today's move, explained in one line:",
    "Entry, stop, target — today's full plan:",
    "What changed today? Exactly this:",
    "The chart never lies — today it says:",
    "This level breaks, the picture changes:",
    "Today's top mover — and the real reason:",
    "Global markets sent one clear signal today:",
    "No fluff — straight to today's data:",
    "A pattern repeated today — here's what it means:",
    "The market's message today, in twenty seconds:",
    "Money follows a plan, not tips — today's plan:",
    "Don't trade tomorrow without seeing this:",
]

# v2.2 NEW — Education hooks English
# v2.3 — number-first rewrite (evergreen math only)
HOOKS_ENGLISH_EDUCATION = [
    "₹5,000 a month for 20 years — how much? Listen:",
    "You can start investing with ₹500 — here's how:",
    "The Rule of 72 — learn it in ten seconds:",
    "Compounding: the eighth wonder — one example:",
    "Your first demat account — a 5-minute job:",
    "Welcome to Week {week} — here is what we cover today:",
    "Inflation eats your money daily — stop it like this:",
    "One concept, and money finally makes sense:",
    "New to investing? Don't make this first mistake:",
    "Today's lesson is short — the benefit is lifelong:",
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

    def get_video_tags(self, mode: str = "market", is_short: bool = False,
                        channel: str = "main", lang: str = "hi") -> list:
        """Returns appropriate tag list for given content type."""
        # (kids channel removed 2026-07-19; `channel` kept for call-site compatibility)
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
# AI CONTENT DISCLOSURE  (Meta + YouTube policy compliance)
# ─────────────────────────────────────────────
# Both Meta (Facebook/Instagram) and YouTube now REQUIRE creators to disclose
# AI-assisted / synthetic content. Disclosing PROTECTS the account — hiding it
# is what triggers removal / demonetization. The wording below is deliberately
# subtle and trust-positive: it discloses the PRODUCTION METHOD while making
# clear the DATA and ANALYSIS are real, so the audience keeps trusting the
# content even though it is AI-produced.
AI_DISCLOSURE = {
    "hi": "🤖 AI tools se banaya gaya · 📊 Real market data aur analysis · Sirf shiksha ke liye",
    "en": "🤖 Produced with AI tools · 📊 Real market data & analysis · Educational only",
}


def ai_disclosure(lang: str = "en") -> str:
    """Return a one-line AI-content disclosure for captions / descriptions.

    Required by Meta + YouTube policy. Discloses that AI tools were used while
    affirming the market data + analysis are real — compliant AND keeps audience
    trust. Fail-safe: always returns a string (never raises)."""
    try:
        return AI_DISCLOSURE.get(lang, AI_DISCLOSURE["en"])
    except Exception:
        return AI_DISCLOSURE["en"]


# ─────────────────────────────────────────────
# FACEBOOK CAPTION VARIATION (2026-07-23)
# ─────────────────────────────────────────────
# Found while diagnosing why the Facebook Page lost recommendation eligibility:
# every post used a 100% fixed structural template (same opener line, same
# hashtag set, only title/description swapped) — a direct match for Meta's
# documented "mass-produced/templated content" signal under their
# Recommendations Guidelines. Rotating the opener + hashtag set gives real
# day-to-day surface variation. The functional lines (links, AI disclosure,
# disclaimer) stay fixed on purpose — those are compliance/trust text, not
# what triggered the flag.
FB_CAPTION_OPENERS = {
    "market": [
        "🎯 {title}",
        "📈 Aaj ka Signal — {title}",
        "🔔 Fresh Setup — {title}",
        "⚡ Aaj ka Update — {title}",
        "📊 {title}",
    ],
    "education": [
        "📚 {title}",
        "🎓 Aaj Seekho — {title}",
        "💡 {title}",
        "📖 Aaj ka Sabak — {title}",
    ],
    "weekend": [
        "📚 Weekend Wisdom",
        "🧠 Weekend Learning",
        "☕ Weekend Read",
        "🎯 Weekend Special",
    ],
    "holiday": [
        "🎉 {title} Special",
        "🎊 {title}",
        "🪔 {title} — Aaj Market Band",
    ],
    # "articles_*" — the daily articles-roundup post (daily-articles.yml),
    # a distinct voice from the single-signal/reel captions above.
    "articles_market": [
        "📰 Aaj ke Market Articles",
        "🗞️ Fresh Analysis — Live Now",
        "📊 Today's Market Reads",
        "🔍 Aaj ka Market Digest",
    ],
    "articles_weekend": [
        "📚 Weekend Special",
        "🧠 Weekend Reading List",
        "☕ Weekend Deep Dive",
    ],
    "articles_holiday": [
        "🎉 {title} — Holiday Reads",
        "📖 {title} Special",
    ],
}

FB_HASHTAG_SETS = {
    "market": [
        "#ai360trading #StockMarket #Nifty #Trading",
        "#StockMarketIndia #Nifty50 #TradingSignals #ai360trading",
        "#Nifty #BankNifty #StockMarket #ai360trading",
        "#ai360trading #Investing #ShareMarket #India",
    ],
    "education": [
        "#ai360trading #StockMarket #TradingForBeginners #Investing #ShareMarket",
        "#StockMarketIndia #LearnTrading #ai360trading #Investing",
        "#ai360trading #FinanceEducation #StockMarket #India",
    ],
    "weekend": [
        "#ai360trading #WeekendWisdom #Trading",
        "#WeekendLearning #Trading101 #ai360trading",
        "#ai360trading #FinanceTips #India",
    ],
    "holiday": [
        "#ai360trading #HolidayLearning #StockMarket",
        "#ai360trading #MarketHoliday #Investing",
    ],
    "articles_market": [
        "#StockMarket #Nifty #Trading #ai360trading #India",
        "#ai360trading #MarketNews #StockMarketIndia #Nifty50",
        "#Trading #StockMarket #ai360trading #FinanceIndia",
    ],
    "articles_weekend": [
        "#WeekendLearning #Trading101 #ai360trading #GlobalInvesting",
        "#ai360trading #WeekendReads #Investing #FinanceEducation",
    ],
    "articles_holiday": [
        "#HolidayLearning #InvestmentEducation #ai360trading #GlobalInvesting",
        "#ai360trading #MarketHoliday #GlobalInvesting",
    ],
}


def fb_caption_opener(mode: str, title: str = "") -> str:
    """Random (not fixed) opener line for a Facebook caption, filled with the
    real title/label. Fail-safe: falls back to a plain "🎯 {title}" line."""
    try:
        pool = FB_CAPTION_OPENERS.get(mode, FB_CAPTION_OPENERS["market"])
        return random.choice(pool).format(title=title)
    except Exception:
        return f"🎯 {title}".strip()


def fb_hashtags(mode: str) -> str:
    """Random (not fixed) hashtag line for a Facebook caption. Fail-safe:
    falls back to the original always-used tag set."""
    try:
        pool = FB_HASHTAG_SETS.get(mode, FB_HASHTAG_SETS["market"])
        return random.choice(pool)
    except Exception:
        return "#ai360trading #StockMarket #Nifty #Trading"


# ─────────────────────────────────────────────
# SINGLETON INSTANCES
# ─────────────────────────────────────────────

ht  = HumanTouch()
seo = SEO()
