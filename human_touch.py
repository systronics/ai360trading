"""
human_touch.py — Anti-AI-Penalty Human Touch Engine
v2.1 FIX: format_article_tags + get_youtube_safe_tags now correctly in SEO class
          (v2.0 had them inside HumanTouch docstring — broken Python syntax)
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
    "3 Indian stocks breaking out this week — here's the data:",
    "Why smart money is quietly buying this sector right now:",
    "This pattern gave 80% win rate in backtesting — today's setup:",
    "Nifty50 vs S&P500 this week — which is better to trade?",
    "One chart. One trade. Everything you need in 60 seconds:",
]

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

PERSONAL_PHRASES_HINDI = [
    "Mera personal experience hai ki", "Maine khud dekha hai ki",
    "Honestly bolunga toh", "Mere hisaab se",
    "Bahut baar observe kiya hai maine ki",
    "Yeh main apne experience se bol raha hoon",
    "Chart study karte waqt maine notice kiya ki",
    "Jo main personally follow karta hoon woh hai",
    "Seedha experience se bolunga", "Traders se baat karke pata chala ki",
]

PERSONAL_PHRASES_ENGLISH = [
    "In my experience,", "What I've personally observed is",
    "To be completely honest,", "From my own trading,",
    "I've seen this pattern enough times to know",
    "What I actually do in this situation is",
    "After years of watching markets,",
    "The thing most people don't tell you is",
    "I've made this mistake myself, so", "Real talk —",
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

THUMBNAIL_TEMPLATES_TRADING = [
    ("{stock} 🚀","BREAKOUT!","Entry: {entry}"),
    ("₹{target}","TARGET?","{stock} Analysis"),
    ("3 STOCKS","BREAKOUT TODAY","Watch Now"),
    ("{pct}% GAIN","POSSIBLE?","{stock} Setup"),
    ("BUY NOW?","{stock}","Target: ₹{target}"),
    ("NIFTY ALERT","{level}","Kya karein?"),
    ("52W HIGH","{stock}","Aage kya?"),
    ("FII BUYING","{sector}","Opportunity!"),
    ("TODAY's","BEST TRADE","{stock} {entry}"),
    ("MARKET","{mood}","Aaj kya karein?"),
]

THUMBNAIL_TEMPLATES_TRADING_EN = [
    ("{stock}","BREAKOUT","Entry: {entry}"),
    ("3 STOCKS","TO WATCH","This Week"),
    ("{pct}% TARGET","{stock}","Trade Setup"),
    ("BUY OR SELL?","{stock}","Today's Analysis"),
    ("SMART MONEY","IS BUYING","{sector}"),
    ("NIFTY50","{level}","Key Level Alert"),
    ("52-WEEK","HIGH ALERT","{stock}"),
    ("TODAY'S","BEST TRADE","Watch This"),
]

THUMBNAIL_TEMPLATES_KIDS = [
    ("SHER KI","KAHANI","Aaj ki Story!"),
    ("JADUI","DUNIYA","Ek Naya Safar"),
    ("ELLY","KI DOSTI","Sweet Story"),
    ("RAINBOW","WORLD","Magic Story"),
    ("PRINCESS","STORY","Magical Tale"),
    ("Titli","KI UDAAN","Inspirational"),
    ("RAJA KI","KAHANI","Aaj Episode"),
    ("STAR","CHILDREN","Daily Story"),
    ("CIRCUS","ADVENTURE","Fun Story"),
    ("UNICORN","MAGIC","Bedtime Story"),
]

TAGS_TRADING_HINDI = [
    "nifty50 aaj ka analysis","swing trade setup hindi",
    "best stocks to buy today india","nifty prediction today",
    "free trading signals india","option trading hindi",
    "nifty50 breakout stocks","technical analysis hindi",
    "stock market tips hindi","intraday trading tips hindi",
    "nifty bank nifty analysis","share market kaise seekhein",
    "trading for beginners hindi","nifty50 weekly analysis",
    "best swing trade stocks india","fii buying stocks today",
    "positional trading hindi","stock market chart analysis",
    "nifty support resistance","breakout stocks india today",
    "trading signals telegram india","ai360trading","nifty50 live analysis",
]

TAGS_TRADING_ENGLISH = [
    "nifty50 analysis","indian stock market","nse trading signals",
    "swing trading india","nifty50 breakout","technical analysis india",
    "best indian stocks 2026","nifty prediction","indian stock market tips",
    "trading strategy india","nse bse analysis","how to trade nifty",
    "nifty option trading","indian market technical analysis",
    "stock market india today","best stocks to buy india","ai360trading",
    "nifty weekly outlook","indian stocks breakout","sensex nifty analysis",
]

TAGS_TRADING_EDUCATION = [
    "stock market education hindi","trading psychology hindi",
    "how to read candlestick charts","rsi indicator hindi",
    "moving average trading","support resistance levels",
    "how to pick stocks india","fundamental vs technical analysis",
    "warren buffett investing hindi","wealth building india",
    "financial planning hindi","mutual funds vs stocks",
    "trading mistakes to avoid","stock market for beginners",
    "sip vs lumpsum investment","compound interest hindi",
    "long term investing india","ai360trading education",
    "passive income india","financial freedom hindi",
]

TAGS_KIDS_HINDI = [
    "hindi kahani","bacchon ki kahani","moral story hindi",
    "fairy tale hindi","short story hindi","nani ki kahani",
    "panchatantra stories hindi","motivational story kids",
    "bedtime story hindi","cartoon kahani hindi","jungle ki kahani",
    "raja rani ki kahani","aesop fables hindi","hindi animated stories",
    "kids moral stories","children stories hindi","tenali rama stories",
    "akbar birbal hindi","good moral story","inspirational kids story hindi",
]

TAGS_KIDS_ENGLISH = [
    "kids stories in english","bedtime stories for kids",
    "moral stories for children","fairy tales for kids",
    "animated stories english","short stories for kids",
    "stories with moral lessons","children bedtime stories",
    "educational stories kids","indian stories for kids",
    "folklore stories english","kids learning stories",
    "character building stories","fun stories for children",
    "adventure stories kids","magical stories for children",
    "storytime for kids","read aloud stories",
    "story time hindi english","bilingual stories kids india",
]

MORNING_REEL_TOPICS = {
    0: {"topic":"US/UK Weekend Market Recap","angle":"What happened globally while Indian markets were closed","target_country":["USA","UK","India"],"hook_en":"While you were sleeping, global markets made a big move:","hook_hi":"Weekend mein global markets mein yeh hua — dekhna zaroori hai:"},
    1: {"topic":"Trading Psychology","angle":"One mindset shift that separates winners from losers","target_country":["India","UAE"],"hook_en":"The real reason most traders fail has nothing to do with charts:","hook_hi":"90% traders yeh galti karte hain — aur yeh chart se related nahi hai:"},
    2: {"topic":"Global Market Update","angle":"Mid-week global picture — US, UK, Brazil, India","target_country":["USA","UK","Brazil","India"],"hook_en":"Mid-week check — here's what global markets are telling us:","hook_hi":"Hafte ke beech mein global market ka ek quick scan karte hain:"},
    3: {"topic":"Wealth Mindset","angle":"One wealth principle successful investors follow","target_country":["UAE","Canada","Australia"],"hook_en":"One wealth principle that compound investors never break:","hook_hi":"Ek rule jo sab successful investors follow karte hain — seriously:"},
    4: {"topic":"Weekend Strategy Preview","angle":"What to watch, what to prepare before next week","target_country":["India","USA","UK"],"hook_en":"Before markets close today — here's your weekend prep list:","hook_hi":"Weekend se pehle yeh 3 cheezein prepare kar lo — trading ke liye:"},
    5: {"topic":"Motivation + Lessons","angle":"One trading lesson from a real market mistake","target_country":["Global"],"hook_en":"The lesson I learned the hard way — so you don't have to:","hook_hi":"Ek galti jo maine ki — taaki aap na karein:"},
    6: {"topic":"Next Week Strategy","angle":"Key levels, sector focus, and what to watch Monday","target_country":["USA","UK","India"],"hook_en":"Sunday prep: here's exactly what I'm watching for next week:","hook_hi":"Kal market kholega — yeh levels aur sectors ready rakhna:"},
}

KIDS_STORY_TOPICS = {
    0: {"theme":"Friendship","character":"Hathi aur Chuha","moral":"Dosti mein size matter nahi karta"},
    1: {"theme":"Bravery","character":"Chhoti Ladki","moral":"Himmat se badi koi taakat nahi"},
    2: {"theme":"Honesty","character":"Lalchi Saudagar","moral":"Sach bolna hamesha theek hota hai"},
    3: {"theme":"Kindness","character":"Magical Tree","moral":"Dene walo ko hamesha milta hai"},
    4: {"theme":"Hard Work","character":"Tembhi Keedey","moral":"Mehnat ka fal zaroor milta hai"},
    5: {"theme":"Imagination","character":"Star Children","moral":"Sapne dekhne wale hi unhe poora karte hain"},
    6: {"theme":"Family Love","character":"Jungle Family","moral":"Parivaar se bada koi nahi"},
}


# ═════════════════════════════════════════════════════════════════════════════
# SEO CLASS — contains format_article_tags + get_youtube_safe_tags
# ═════════════════════════════════════════════════════════════════════════════

class SEO:
    """SEO tag and description generator. Usage: from human_touch import seo"""

    def __init__(self):
        self.now_ist = datetime.now(IST)
        self.seed    = int(self.now_ist.strftime("%Y%m%d"))

    def get_video_tags(self, mode="market", is_short=False,
                        channel="trading", lang="both", extra_tags=None) -> list:
        extra = extra_tags or []
        if channel == "kids":
            base    = TAGS_KIDS_HINDI + TAGS_KIDS_ENGLISH
            rotated = base[self.seed % 5:] + base[:self.seed % 5]
            return (extra + rotated)[:30]
        if lang == "hi":
            base = TAGS_TRADING_HINDI
        elif lang == "en":
            base = TAGS_TRADING_ENGLISH
        else:
            base = TAGS_TRADING_HINDI[:12] + TAGS_TRADING_ENGLISH[:12]
        if mode in ("weekend","holiday"):
            base = TAGS_TRADING_EDUCATION[:15] + base[:10]
        if "ai360trading" not in base:
            base = ["ai360trading"] + base
        if is_short:
            return (extra + base[:15])[:20]
        return (extra + base[:25])[:30]

    def format_article_tags(self, tags: list) -> str:
        """
        Format tags as comma-separated string for meta/front matter use.
        Used by generate_reel_morning.py and other generators.
        Returns only ASCII-safe tags (YouTube API rejects non-ASCII).
        """
        safe = []
        for t in tags:
            cleaned = ''.join(c for c in str(t) if ord(c) < 128).strip()
            if cleaned and len(cleaned) > 2:
                safe.append(cleaned)
        return ', '.join(safe[:8])

    def get_youtube_safe_tags(self, tags: list) -> list:
    """
    Filter tags for YouTube API upload.
    Rules:
    - ASCII only (no Hindi/emoji)
    - Each tag: 3–30 chars
    - TOTAL chars across all tags: under 480 (YouTube hard limit = 500)
    - Max 20 tags
    """
    safe        = []
    total_chars = 0
    for t in tags:
        cleaned = ''.join(c for c in str(t) if ord(c) < 128).strip()
        cleaned = cleaned.replace('#', '').replace('@', '').strip()
        if not cleaned or not (2 < len(cleaned) <= 30):
            continue
        if total_chars + len(cleaned) + 1 >= 480:   # +1 for separator
            break
        safe.append(cleaned)
        total_chars += len(cleaned) + 1
    return safe[:20]

    def get_description_template(self, title, main_insight, mode="market",
                                  channel="trading", video_id_part1="",
                                  stocks=None, lang="hi") -> str:
        stocks   = stocks or []
        today    = datetime.now(IST).strftime("%d %B %Y")
        tags     = self.get_video_tags(mode=mode, channel=channel, lang=lang)
        hashtags = " ".join([f"#{t.replace(' ','')}" for t in tags[:12]
                             if all(ord(c) < 128 for c in t)])
        if channel == "kids":
            return self._kids_description(title, main_insight, hashtags, today)
        stock_line = f"Stocks covered: {', '.join(stocks[:5])}\n" if stocks else ""
        part1_line = (f"Part 1 Analysis: https://youtube.com/watch?v={video_id_part1}\n"
                      if video_id_part1 and video_id_part1 != "UPLOAD_FAILED" else "")
        if lang == "en":
            desc = (
                f"📈 {title}\n🎯 {main_insight}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"TIMESTAMPS:\n0:00 Market Overview\n1:30 Today's Key Levels\n"
                f"3:00 Top Trade Setups\n6:00 Entry / SL / Target\n"
                f"9:00 Options Insight\n11:00 Summary\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{stock_line}{part1_line}"
                f"Telegram (Live Signals): https://t.me/ai360trading\n"
                f"Website: https://ai360trading.in\n\n"
                f"Educational content only. Not SEBI registered advice.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n{hashtags}"
            )
        else:
            desc = (
                f"📈 {title}\n🎯 {main_insight}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"TIMESTAMPS:\n0:00 Market Overview — Nifty kahan hai\n"
                f"1:30 Aaj ke Key Levels\n3:00 Top Trade Setups\n"
                f"6:00 Entry, SL aur Target\n9:00 Options Hint\n11:00 Summary\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{stock_line}{part1_line}"
                f"Telegram (Live Signals): https://t.me/ai360trading\n"
                f"Website: https://ai360trading.in\n\n"
                f"Educational content only. SEBI registered advice nahi hai.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n{hashtags}"
            )
        return desc

    def _kids_description(self, title, main_insight, hashtags, today):
        return (
            f"🌟 {title}\n✨ {main_insight}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"0:00 Kahani shuru\n1:00 Main character\n"
            f"2:30 Badi mushkil\n4:00 Hero kya karta hai\n5:30 Moral\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Subscribe karo roz ki kahani ke liye!\n"
            f"Age: 3-10 years | Hindi + English\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n{hashtags}"
        )

    def get_thumbnail_text(self, channel="trading", stock="", entry="",
                            target="", pct="", sector="", mood="BULLISH",
                            level="", story_theme="", lang="hi") -> dict:
        if channel == "kids":
            t = THUMBNAIL_TEMPLATES_KIDS[
                int(datetime.now(IST).strftime("%Y%m%d")) % len(THUMBNAIL_TEMPLATES_KIDS)
            ]
            return {"line1":t[0],"line2":t[1],"line3":t[2],
                    "bg_color":(255,180,0),"text_color":(20,20,80),"style":"kids"}
        templates = THUMBNAIL_TEMPLATES_TRADING_EN if lang == "en" else THUMBNAIL_TEMPLATES_TRADING
        seed = int(datetime.now(IST).strftime("%Y%m%d")) % len(templates)
        t    = templates[seed]
        def fill(s):
            return (s.replace("{stock}", stock or "NIFTY")
                     .replace("{entry}", entry or "CMP")
                     .replace("{target}", target or "TGT")
                     .replace("{pct}", pct or "15")
                     .replace("{sector}", sector or "Market")
                     .replace("{mood}", mood or "ALERT")
                     .replace("{level}", level or "Key Level"))
        if mood.upper() in ("BULLISH","BUY"):
            bg, tc = (0,140,60), (255,255,255)
        elif mood.upper() in ("BEARISH","SELL"):
            bg, tc = (180,30,30), (255,255,255)
        else:
            bg, tc = (20,20,80), (255,220,0)
        return {"line1":fill(t[0]),"line2":fill(t[1]),"line3":fill(t[2]),
                "bg_color":bg,"text_color":tc,"style":"trading"}

    def get_searchable_title(self, content_type, topic_keyword, date_str="",
                              mode="market", holiday_name="", channel="trading",
                              stock="", lang="hi") -> str:
        if not date_str:
            date_str = datetime.now(IST).strftime("%d %b %Y")
        if channel == "kids":
            return f"{topic_keyword} | Hindi Kahani | Bacchon Ki Stories"[:100]
        tag = "AI360 Trading"
        if mode == "holiday" and holiday_name:
            base = f"{holiday_name} {datetime.now(IST).year} | {topic_keyword} | {tag}"
        elif content_type == "analysis":
            base = (f"{stock} {topic_keyword} | Nifty50 {date_str} | {tag}"
                    if stock else f"Nifty50 Analysis {date_str} | {topic_keyword} | {tag}")
        elif content_type == "education":
            base = f"{topic_keyword} {date_str} | Trading Education | {tag}"
        elif content_type == "reel":
            base = f"{topic_keyword} | {tag} Shorts"
        elif content_type == "short":
            base = (f"{stock} Trade Setup {date_str} | {tag}"
                    if stock else f"{topic_keyword} {date_str} | {tag}")
        else:
            base = f"{topic_keyword} {date_str} | {tag}"
        if len(base) > 100:
            suffix = f" | {tag}"
            base   = base[:100 - len(suffix)].rstrip(" |") + suffix
        return base[:100]

    def get_morning_reel_topic(self) -> dict:
        return MORNING_REEL_TOPICS[datetime.now(IST).weekday()]

    def get_kids_story_topic(self) -> dict:
        return KIDS_STORY_TOPICS[datetime.now(IST).weekday()]


# ═════════════════════════════════════════════════════════════════════════════
# HumanTouch CLASS
# ═════════════════════════════════════════════════════════════════════════════

class HumanTouch:
    """Injects human-like qualities into AI-generated content."""

    def __init__(self):
        self.now_ist = datetime.now(IST)
        self.weekday = self.now_ist.weekday()
        self.seed    = int(self.now_ist.strftime("%Y%m%d"))
        random.seed(self.seed)

    def get_hook(self, mode="market", lang="hi",
                 holiday_name="", channel="trading") -> str:
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

    def get_cta(self, lang="hi", channel="trading") -> str:
        if channel == "kids":
            ctas = CTAS_KIDS_ENGLISH if lang == "en" else CTAS_KIDS_HINDI
        else:
            ctas = CTAS_ENGLISH if lang == "en" else CTAS_HINDI
        return ctas[(self.seed + 3) % len(ctas)]

    def get_personal_phrase(self, lang="hi") -> str:
        phrases = PERSONAL_PHRASES_ENGLISH if lang == "en" else PERSONAL_PHRASES_HINDI
        return random.choice(phrases)

    def get_tts_speed(self) -> float:
        speeds = [0.90, 0.93, 0.95, 0.97, 1.00, 1.02, 1.05, 1.08, 1.10]
        return speeds[self.seed % len(speeds)]

    def get_kids_tts_speed(self) -> float:
        speeds = [0.85, 0.87, 0.90, 0.92, 0.95]
        return speeds[self.seed % len(speeds)]

    def get_kids_voice(self) -> str:
        voices = ["hi-IN-SwaraNeural", "en-IN-NeerjaNeural"]
        return voices[self.seed % len(voices)]

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
            "market":  ["📈","📊","🎯","💹","🔔","⚡","🚀","💡","🔥","✅"],
            "weekend": ["📚","🧠","💡","🌟","🎯","📖","✨","🏆","💪","🌱"],
            "holiday": ["🎉","🌟","✨","🙏","💫","🎊","❤️","🌈","🌸","🎈"],
            "kids":    ["🌟","✨","🎉","🦁","🐘","🌈","🏰","👑","🦋","💫"],
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

    def _remove_robotic_patterns(self, text: str) -> str:
        replacements = {
            "Certainly! ":"","Absolutely! ":"","Of course! ":"",
            "Sure! ":"","Great! ":"","Indeed, ":"",
            "It's important to note that ":"",
            "It is worth noting that ":"",
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
                "aur ": random.choice(["aur ","saath hi ","plus "]),
                "lekin ": random.choice(["lekin ","but ","par "]),
                "kyunki ": random.choice(["kyunki ","because ","isliye ki "]),
            }
        else:
            connector_map = {
                "and ": random.choice(["and ","plus ","also "]),
                "but ": random.choice(["but ","however, ","yet "]),
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
        pause_words = ["lekin","toh","aur","but","so","now","here"]
        for word in pause_words:
            text = re.sub(rf'\b{word}\b(?!,)', f'{word},', text, count=1)
        return text

    def _get_filler(self, lang: str) -> str:
        fillers_hi = ["","Suniye —","Dekho,","Sach mein,","Waise,"]
        fillers_en = ["","Now —","Look,","Here's the thing —","So,"]
        fillers    = fillers_en if lang == "en" else fillers_hi
        filler     = random.choice(fillers)
        return filler if filler else ""


# ── MODULE-LEVEL INSTANCES ────────────────────────────────────────────────────
ht  = HumanTouch()
seo = SEO()
