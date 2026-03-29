"""
generate_community_post.py — AI360Trading YouTube Community Tab
===============================================================
Posts a daily text + emoji community post to YouTube Community Tab at 12:00 PM IST.
Boosts algorithm by signalling active channel between video uploads.
Uses: ai_client (Groq→Gemini→Claude→OpenAI→Templates fallback)
Uses: human_touch (hooks, emojis, CTAs)
Mode-aware: market / weekend / holiday
Author: AI360Trading Automation
Last Updated: March 2026 — Phase 2 Build
"""

import os
import json
import pytz
from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# ─── Phase 2: ai_client + human_touch ────────────────────────────────────────
from ai_client import ai
from human_touch import ht, seo

# ─── Content Mode ─────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")

IST = pytz.timezone("Asia/Kolkata")
now = datetime.now(IST)

print(f"[MODE] generate_community_post.py running in mode: {CONTENT_MODE.upper()}")
print(f"[AI]   Using ai_client fallback chain: Groq→Gemini→Claude→OpenAI→Templates")

# ─── YOUTUBE SERVICE ─────────────────────────────────────────────────────────
def get_youtube_service():
    try:
        creds_json = os.environ.get("YOUTUBE_CREDENTIALS")
        if not creds_json and os.path.exists("token.json"):
            with open("token.json") as f:
                creds_json = f.read()
        if not creds_json:
            print("  ❌ No YouTube credentials found")
            return None
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"  ❌ YouTube auth error: {e}")
        return None

# ─── POST GENERATION via ai_client ───────────────────────────────────────────
def generate_post_text():
    today     = now.strftime("%A, %d %B %Y")
    day_name  = now.strftime("%A")
    ht_hook   = ht.get_hook(mode=CONTENT_MODE)
    ht_phrase = ht.get_personal_phrase(lang="hi")
    emojis    = ht.get_emoji_set()  # day-seeded emoji rotation

    if CONTENT_MODE == "holiday":
        context = (f"Today is {HOLIDAY_NAME}. Indian stock market is closed. "
                   "Write a motivational community post about using market holidays productively — "
                   "learning, reviewing trades, planning finances.")
    elif CONTENT_MODE == "weekend":
        context = (f"Today is {day_name}. Market is closed for the weekend. "
                   "Write an educational/inspirational community post about weekend preparation "
                   "for traders — chart study, journaling, mindset.")
    else:
        context = (f"Today is {day_name}. Indian market is open. "
                   "Write an engaging community post with today's market vibe, "
                   "a quick insight or question to boost engagement, "
                   "and a teaser for today's videos.")

    prompt = f"""You are Amit Kumar of AI360Trading writing a YouTube Community Tab post in Hinglish.

Today: {today}
Mode: {CONTENT_MODE.upper()}
Context: {context}

HOOK TO OPEN WITH (adapt naturally — do not copy verbatim):
{ht_hook}

PERSONAL PHRASE (inject naturally once):
{ht_phrase}

Write a community post that:
1. Opens with a strong hook (use ht_hook inspiration)
2. Gives one valuable insight or asks one engaging question
3. Has a clear CTA — watch today's video OR join Telegram OR comment below
4. Uses emojis naturally (these: {' '.join(emojis[:5])})
5. Ends with: "📱 t.me/ai360trading | 🌐 ai360trading.in"
6. Length: 80-120 words in Hinglish
7. Feels human — NOT like a bot wrote it

Return ONLY the post text. No JSON. No markdown. Just the raw community post text."""

    system_prompt = (
        "You are Amit Kumar, founder of AI360Trading — a real person from Haridwar, India. "
        "Your community posts are warm, direct, and genuinely helpful. "
        "Natural Hinglish. Never robotic. Never start with 'Certainly' or 'Here is your post'. "
        "Return ONLY the post text — nothing else."
    )

    print("  🤖 Generating community post via ai_client...")
    try:
        raw = ai.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            content_mode=CONTENT_MODE,
            lang="hi",
            max_tokens=400,
            temperature=0.9,
        )
        # humanize through human_touch
        post_text = ht.humanize(raw, lang="hi")
        print(f"  ✅ Community post generated via {ai.active_provider} ({len(post_text)} chars)")
        return post_text
    except Exception as e:
        print(f"  ⚠️ ai_client error: {e} — using fallback post")
        return _fallback_post()


def _fallback_post():
    hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")
    posts = {
        "market": (
            f"{hook}\n\n"
            "Aaj ke market mein ek important level hai jisko miss nahi karna chahiye. "
            "Humara aaj ka video check karo — full analysis ke saath.\n\n"
            "Comment karo: aap aaj bullish ho ya bearish? 👇\n\n"
            "📱 t.me/ai360trading | 🌐 ai360trading.in"
        ),
        "weekend": (
            f"{hook}\n\n"
            "Weekend mein successful traders kya karte hain? Charts review karte hain, "
            "journal update karte hain, aur next week ki strategy banate hain.\n\n"
            "Aap kya prepare kar rahe ho aaj? Comment mein batao! 👇\n\n"
            "📱 t.me/ai360trading | 🌐 ai360trading.in"
        ),
        "holiday": (
            f"{hook}\n\n"
            f"{HOLIDAY_NAME} ki shubhkamnayein! Market band hai, par learning nahi rukti. "
            "Aaj apni trading journal review karo aur next plan banao.\n\n"
            "Kya seekha aapne is mahine? Comment mein share karo! 👇\n\n"
            "📱 t.me/ai360trading | 🌐 ai360trading.in"
        ),
    }
    return posts.get(CONTENT_MODE, posts["market"])

# ─── POST TO YOUTUBE COMMUNITY TAB ───────────────────────────────────────────
def post_to_community(post_text):
    youtube = get_youtube_service()
    if not youtube:
        print("  ❌ YouTube service unavailable — cannot post community update")
        return False

    try:
        # YouTube Community posts use the activities endpoint
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
        # Note: YouTube Data API v3 community posts use activities.insert
        # with kind = youtube#activity and type = bulletin
        request = youtube.activities().insert(
            part="snippet,contentDetails",
            body={
                "snippet": {
                    "description": post_text,
                    "type": "bulletin"
                },
                "contentDetails": {
                    "bulletin": {}
                }
            }
        )
        response = request.execute()
        print(f"  ✅ Community post published! Activity ID: {response.get('id', 'N/A')}")
        return True
    except Exception as e:
        err_str = str(e)
        if "bulletin" in err_str.lower() or "403" in err_str:
            print(f"  ⚠️ Community Tab API restricted (channel may need 500+ subscribers or tab not enabled): {e}")
            print("  💡 FIX: Enable Community Tab in YouTube Studio → Customization → Layout")
        else:
            print(f"  ❌ Community post failed: {e}")
        return False

# ─── SAVE POST TEXT (fallback — for manual posting) ──────────────────────────
def save_post_fallback(post_text, today_str):
    out_path = f"output/community_post_{today_str}.txt"
    os.makedirs("output", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(post_text)
    print(f"  📄 Post text saved to {out_path} (manual fallback)")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    today_str = now.strftime("%Y%m%d")
    print(f"\n{'=' * 50}")
    print(f"  AI360Trading Community Post — {now.strftime('%d %B %Y')}")
    print(f"  Mode: {CONTENT_MODE.upper()}")
    print(f"{'=' * 50}")

    post_text = generate_post_text()
    print(f"\n  📝 POST PREVIEW:\n{'─' * 40}")
    print(post_text)
    print(f"{'─' * 40}\n")

    success = post_to_community(post_text)
    save_post_fallback(post_text, today_str)  # Always save — useful for logs

    if success:
        print(f"  ✅ Community post done | AI: {ai.active_provider}")
    else:
        print(f"  ⚠️ Auto-post failed — text saved for manual posting")
        print(f"  📄 Copy from: output/community_post_{today_str}.txt")

    return success


if __name__ == "__main__":
    main()
