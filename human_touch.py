# HUMAN_TOUCH.PY PATCH — ADD THESE LINES ONLY
# =============================================
# Find this exact line in human_touch.py (around line 290):
#
#     def get_morning_reel_topic(self) -> dict:
#
# ADD the get_searchable_title() method BEFORE that line.
# Copy exactly from START to END below.

# ---- START OF ADDITION ----

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

# ---- END OF ADDITION ----

# That's the only change to human_touch.py.
# No existing code is modified. Just insert the method above before get_morning_reel_topic().
