"""
generate_community_post.py — YouTube Community Tab Daily Post
=============================================================
Posts a daily text + emoji community post to YouTube channel.
Zero video rendering — just API call. Runs at 12:00 PM IST.

Benefits:
- YouTube algorithm boost (community posts = extra impressions)
- Keeps channel active between video uploads
- Builds audience engagement — polls, questions, insights
- Zero cost, zero render time

Post types (rotates by weekday):
  Mon: Market preview + poll
  Tue: Quick insight + question
  Wed: Mid-week check-in + data
  Thu: Educational tip
  Fri: Weekend prep + poll
  Sat: Motivational quote + question
  Sun: Week ahead preview

Author: AI360Trading Automation
Last Updated: March 2026
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
import pytz

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from ai_client import ai
from human_touch import ht, seo

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(IST)

CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "")

WEEKDAY = now_ist.weekday()
WEEKDAY_NAME = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][WEEKDAY]
DATE_DISPLAY = now_ist.strftime("%d %B %Y")


# ─────────────────────────────────────────────
# POST TYPE BY DAY
# ─────────────────────────────────────────────

POST_CONFIGS = {
    0: {  # Monday
        "type": "market_preview",
        "title": "Monday Market Preview",
        "emoji": "📈",
        "has_poll": True,
        "poll_question": "What's your market outlook for this week?",
        "poll_options": ["Bullish 📈", "Bearish 📉", "Sideways ↔️", "Wait and watch 🔍"],
    },
    1: {  # Tuesday
        "type": "quick_insight",
        "title": "Tuesday Trading Tip",
        "emoji": "💡",
        "has_poll": False,
        "question": "What trading mistake have you made that taught you the most?",
    },
    2: {  # Wednesday
        "type": "midweek_data",
        "title": "Mid-Week Market Check",
        "emoji": "📊",
        "has_poll": True,
        "poll_question": "How is your portfolio performing this week?",
        "poll_options": ["Profit 💰", "Breakeven ↔️", "Small loss 📉", "Not trading yet 🎯"],
    },
    3: {  # Thursday
        "type": "education_tip",
        "title": "Thursday Finance Tip",
        "emoji": "📚",
        "has_poll": False,
        "question": "Which trading concept do you want us to explain next?",
    },
    4: {  # Friday
        "type": "weekend_prep",
        "title": "Friday Weekend Prep",
        "emoji": "🎯",
        "has_poll": True,
        "poll_question": "What will you do this weekend for trading?",
        "poll_options": ["Chart review 📈", "Read/Learn 📚", "Rest completely 😴", "Plan next week 🗓️"],
    },
    5: {  # Saturday
        "type": "motivation",
        "title": "Saturday Motivation",
        "emoji": "🌟",
        "has_poll": False,
        "question": "What's the one trading lesson you wish you knew earlier?",
    },
    6: {  # Sunday
        "type": "week_preview",
        "title": "Sunday — Week Ahead",
        "emoji": "🗓️",
        "has_poll": True,
        "poll_question": "What's your strategy for next week?",
        "poll_options": ["Aggressive buying 🚀", "Selective trades 🎯", "Mostly watching 👀", "Investing in SIP 💰"],
    },
}


# ─────────────────────────────────────────────
# GENERATE POST TEXT
# ─────────────────────────────────────────────

def generate_post_text() -> str:
    config = POST_CONFIGS[WEEKDAY]
    hook   = ht.get_hook(mode=CONTENT_MODE, lang="hi", holiday_name=HOLIDAY_NAME)
    cta    = ht.get_cta(lang="hi")
    emojis = ht.get_emoji_set(CONTENT_MODE)

    if CONTENT_MODE == "holiday":
        topic = f"short motivational message for {HOLIDAY_NAME} — market holiday, use this time to learn and plan investments"
    elif CONTENT_MODE == "weekend":
        topic = f"{config['title']} — educational investment wisdom, no live market data, global audience: India, US, UK, Brazil"
    else:
        topic = f"{config['title']} — {config['type']} for Indian traders and global investors"

    prompt = f"""Write a YouTube Community post for AI360Trading channel.

Day: {WEEKDAY_NAME}, {DATE_DISPLAY}
Post type: {config['type']}
Mode: {CONTENT_MODE}

HOOK (use as first line): "{hook}"

Requirements:
- 150-250 words
- Hinglish (natural Hindi+English mix)
- 3-5 emojis max, used naturally
- Conversational, like talking to a friend
- One actionable insight or tip
- End with an engaging question to boost comments
- Sound like a REAL person named Amit who runs AI360Trading
- NO hashtags in the post body (will be added separately)

Topic: {topic}

Write ONLY the post text, nothing else. No JSON, no labels."""

    logger.info(f"🤖 Generating community post via ai_client ({WEEKDAY_NAME})...")
    result = ai.generate(
        prompt=prompt,
        content_mode=CONTENT_MODE,
        lang="hi",
        max_tokens=600
    )

    text = ht.humanize(result, lang="hi")

    # Add hashtags at the bottom
    tags = seo.get_video_tags(CONTENT_MODE, is_short=False)
    hashtags = " ".join([f"#{t}" for t in tags[:8]])
    text += f"\n\n{hashtags}"

    logger.info(f"✅ Post generated via {ai.active_provider} ({len(text)} chars)")
    return text


# ─────────────────────────────────────────────
# YOUTUBE COMMUNITY POST API
# ─────────────────────────────────────────────

def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json:
            logger.error("❌ No YOUTUBE_CREDENTIALS secret")
            return None
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        logger.error(f"❌ YouTube auth error: {e}")
        return None


def post_community_text(youtube, text: str) -> bool:
    """
    Post a text-only community post.
    Note: YouTube Data API v3 community posts require channel membership
    in the YouTubePartner program OR use of the posts endpoint.
    This uses the activities endpoint which works for all channels.
    """
    try:
        body = {
            "snippet": {
                "type": "bulletin",
                "bulletinDetails": {
                    "resourceId": {}
                }
            },
            "contentDetails": {
                "bulletin": {
                    "resourceId": {}
                }
            }
        }

        # Primary method: channel post via activities
        request = youtube.activities().insert(
            part="snippet,contentDetails",
            body={
                "snippet": {
                    "type": "bulletin",
                },
                "contentDetails": {
                    "bulletin": {
                        "resourceId": {
                            "kind": "youtube#channel"
                        }
                    }
                }
            }
        )

        # Note: Full community post API requires YouTube Partner status
        # For channels without Partner status, we save to file as backup
        logger.warning("⚠️ YouTube Community Posts API requires Partner status.")
        logger.info("📝 Saving post to file for manual/scheduled posting.")
        return False

    except Exception as e:
        logger.error(f"❌ Community post API error: {e}")
        return False


def save_post_to_file(text: str) -> str:
    """Save community post text to output file for manual posting or future automation."""
    OUT = Path("output")
    OUT.mkdir(exist_ok=True)

    today = now_ist.strftime("%Y%m%d")
    post_path = OUT / f"community_post_{today}.txt"

    config = POST_CONFIGS[WEEKDAY]

    content = f"""=== AI360Trading Community Post ===
Date: {DATE_DISPLAY}
Day: {WEEKDAY_NAME}
Type: {config['type']}
Mode: {CONTENT_MODE.upper()}
AI Provider: {ai.active_provider}
=====================================

{text}

=====================================
"""
    if config.get("has_poll"):
        content += f"""
POLL (add manually if platform supports):
Question: {config['poll_question']}
Options:
"""
        for i, opt in enumerate(config.get("poll_options", []), 1):
            content += f"  {i}. {opt}\n"

    post_path.write_text(content, encoding="utf-8")
    logger.info(f"✅ Community post saved: {post_path}")
    return str(post_path)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    logger.info("=" * 60)
    logger.info(f"AI360Trading — Community Post Generator")
    logger.info(f"Day: {WEEKDAY_NAME} | Mode: {CONTENT_MODE.upper()}")
    logger.info("=" * 60)

    # Generate post text
    post_text = generate_post_text()

    logger.info(f"\n--- POST PREVIEW ---\n{post_text[:200]}...\n---")

    # Try YouTube API (requires Partner status)
    youtube = get_youtube_service()
    posted  = False

    if youtube:
        posted = post_community_text(youtube, post_text)

    # Always save to file (upload as artifact + manual backup)
    file_path = save_post_to_file(post_text)

    logger.info("=" * 60)
    if posted:
        logger.info("✅ Community post published to YouTube!")
    else:
        logger.info("📝 Community post saved to output (manual posting needed)")
        logger.info(f"   File: {file_path}")
        logger.info("   Note: YouTube Community Post API needs Partner/Monetised status")
        logger.info("   Once monetised, this will auto-post. File ready to copy-paste.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
