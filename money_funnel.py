"""
money_funnel.py — single source of truth for every income CTA + link.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v1.2 (2026-07-20):
  ADD — article_cta_html() now plugs a rotating calculator (same TOOL_PAGES
    pool as video/comment funnels). It was the only funnel surface skipped by
    v1.1's tool_plug() rollout — the site's own traffic data shows articles
    are the highest-traffic surface, so this was the biggest gap to close.

v1.1 (2026-07-19):
  ADD — TOOL_PAGES + tool_plug(): every caption/description now plugs ONE free
    calculator page (rotates daily). Traffic loop: video viewer → website tool
    → ad impressions + demat/membership funnel. Wired into funnel_block() and
    comment_text() so all generators pick it up with zero changes.

v1.0 (2026-05-31). Goal = QUICK monthly income on ₹0 investment.

The real money path is NOT ad views — it is:
    free Telegram (lead magnet) → ₹699/₹1,499 membership + broker referrals.

So every video description + article must funnel viewers into that path AND
ask for a comment (comments are the #1 signal that makes YouTube / Instagram
hand you more FREE reach). This module centralises all of that so the links
are correct everywhere and only have to be updated in ONE place.

Everything here is plain strings — importing it can never fail a render, and
callers should still wrap usage in try/except to stay fail-open.
"""

from datetime import date

# ── Live links (update ONLY here) ───────────────────────────────────────────
LINKS = {
    "telegram": "https://t.me/ai360trading",
    "website":  "https://ai360trading.in",
    "zerodha":  "https://zerodha.com/open-account?c=YS3694",
    "dhan":     "https://join.dhan.co/?invite=MSIVC45309",
    "groww":    "https://app.groww.in/v3cO/gdbyojxy",
    "coindcx":  "https://invite.coindcx.com/13383200",
}
MEMBERSHIP = "₹699 Advance / ₹1,499 Premium"

# ── Free tools — the traffic loop (video → website → ads/affiliate) ─────────
# (teaser_hi, teaser_en, url). Teasers use only evergreen, honest math.
TOOL_PAGES = [
    ("₹5,000/month ki SIP kitna banegi? Khud dekho",
     "What a ₹5,000/month SIP grows into — check yourself",
     "https://ai360trading.in/tools/sip-calculator/"),
    ("SIP har saal 10% badhao — farak dekho",
     "Step up your SIP 10% yearly — see the difference",
     "https://ai360trading.in/tools/step-up-sip-calculator/"),
    ("Aapki EMI mein kitna interest chhupa hai?",
     "How much interest hides inside your EMI?",
     "https://ai360trading.in/tools/emi-calculator/"),
    ("₹1 lakh 10 saal baad kitne ka rahega?",
     "What will ₹1 lakh be worth in 10 years?",
     "https://ai360trading.in/tools/inflation-calculator/"),
    ("PPF maturity par kitna milega? 10 second mein",
     "Your PPF maturity amount in 10 seconds",
     "https://ai360trading.in/tools/ppf-calculator/"),
    ("Ek baar invest karo — kitna banega? Dekho",
     "Invest once — see what it becomes",
     "https://ai360trading.in/tools/lumpsum-calculator/"),
    ("NPS se pension kitni banegi? Calculate karo",
     "How big will your NPS pension be? Calculate",
     "https://ai360trading.in/tools/nps-calculator/"),
    ("FD vs inflation — sach jaano",
     "FD vs inflation — know the truth",
     "https://ai360trading.in/tools/fd-calculator/"),
]


def tool_plug(lang: str = "hi") -> str:
    """One-line free-calculator plug; rotates daily (traffic → ads/affiliate)."""
    t = TOOL_PAGES[date.today().timetuple().tm_yday % len(TOOL_PAGES)]
    teaser = t[0] if lang == "hi" else t[1]
    return f"🧮 FREE: {teaser} → {t[2]}"

# ── Engagement prompts — drive COMMENTS (biggest free-reach lever) ───────────
_ENGAGE = {
    "hi": [
        "💬 Comment 'NIFTY' agar kal ka FREE signal chahiye 👇",
        "💬 Aapka favourite stock comment karo — kal usi pe video 👇",
        "💬 Yeh setup pasand aaya? Comment 'YES' 👇",
        "💬 Aap bullish ho ya bearish? Comment karo 👇",
        "💬 Kaunsa stock next cover karein? Comment 👇",
    ],
    "en": [
        "💬 Comment 'PROFIT' if you want tomorrow's FREE signal 👇",
        "💬 Which stock should we cover next? Comment below 👇",
        "💬 Found this useful? Comment 'YES' 👇",
        "💬 Are you bullish or bearish today? Comment 👇",
        "💬 Drop your watchlist stock in the comments 👇",
    ],
}


def engagement_prompt(lang: str = "hi") -> str:
    """A comment-driving line; rotates daily so it never feels stale."""
    pool = _ENGAGE.get(lang, _ENGAGE["en"])
    return pool[date.today().timetuple().tm_yday % len(pool)]


def broker_lines(lang: str = "en", bullet: str = "•") -> str:
    """Free-demat referral lines (direct ₹ per signup)."""
    head = ("📈 In setups pe trade karne ke liye FREE demat kholo:"
            if lang == "hi" else
            "📈 Open a FREE demat to trade these setups:")
    return (
        f"{head}\n"
        f"   {bullet} Zerodha: {LINKS['zerodha']}\n"
        f"   {bullet} Dhan: {LINKS['dhan']}\n"
        f"   {bullet} Groww: {LINKS['groww']}\n"
        f"   {bullet} Crypto (CoinDCX): {LINKS['coindcx']}"
    )


def funnel_block(lang: str = "hi", compact: bool = False) -> str:
    """
    The full money funnel for a video description / article footer.
    compact=True → short version for Instagram / Facebook captions.
    """
    tg, site = LINKS["telegram"], LINKS["website"]
    if compact:
        free = ("🎯 FREE roz ke signals → " if lang == "hi"
                else "🎯 FREE daily signals → ") + tg
        prem = (f"💎 Premium signals: {MEMBERSHIP} — DM on Telegram")
        demat = ("📈 FREE demat (Zerodha/Dhan/Groww): " + site
                 if lang == "hi" else
                 "📈 Free demat (Zerodha/Dhan/Groww): " + site)
        return "\n".join([free, prem, demat, tool_plug(lang), engagement_prompt(lang)])

    free = (f"🎯 FREE daily trading signals → Telegram: {tg}")
    prem = (f"💎 Premium signals (exact entry / SL / target): "
            f"{MEMBERSHIP} — DM on Telegram")
    return "\n".join([
        free,
        prem,
        broker_lines(lang),
        tool_plug(lang),
        f"🌐 {site}",
        engagement_prompt(lang),
    ])


def comment_text(lang: str = "hi") -> str:
    """The channel's own top comment (links + engagement) auto-posted on upload."""
    L = LINKS
    if lang == "hi":
        head = "🎯 FREE daily signals yahan milte hain 👇"
    else:
        head = "🎯 Get FREE daily trading signals here 👇"
    return (
        f"{head}\n"
        f"📱 Telegram: {L['telegram']}\n"
        f"💎 Premium (entry/SL/target): {MEMBERSHIP} — DM on Telegram\n"
        f"📈 Free demat: Zerodha {L['zerodha']} | Dhan {L['dhan']} | Groww {L['groww']}\n"
        f"{tool_plug(lang)}\n"
        f"{engagement_prompt(lang)}"
    )


def post_first_comment(youtube, video_id: str, lang: str = "hi",
                       made_for_kids: bool = False) -> bool:
    """
    Auto-post the channel's own top comment with the money funnel right after a
    video uploads (the first comment is prime real estate for the Telegram link).
    NOTE: the YouTube Data API cannot programmatically PIN a comment — posting
    the channel's own comment is the practical equivalent. Needs youtube.force-ssl.
    made_for_kids=True → skip silently: YouTube DISABLES comments on "made for
    kids" content by policy, so the API always rejects it (HTTP 400). This is
    expected and unfixable — not an error worth alarming about.
    FAIL-OPEN — any problem (missing scope, API error) returns False, never raises.
    """
    if not youtube or not video_id:
        return False
    if made_for_kids:
        print("  ℹ️ Auto-comment skipped — comments are disabled on made-for-kids videos (by design)")
        return False
    try:
        body = {"snippet": {"videoId": video_id, "topLevelComment": {
            "snippet": {"textOriginal": comment_text(lang)}}}}
        youtube.commentThreads().insert(part="snippet", body=body).execute()
        print("  ✅ Posted pinned-style first comment (Telegram + funnel)")
        return True
    except Exception as e:
        msg = str(e).lower()
        if any(k in msg for k in ("scope", "insufficient", "forbidden", "403")):
            print("  ⚠️ Auto-comment needs youtube.force-ssl (skipped, fail-open)")
        else:
            print(f"  ⚠️ Auto-comment skipped (fail-open): {str(e)[:100]}")
        return False


def article_cta_html() -> str:
    """A styled conversion CTA box appended to the end of each website article.
    Turns blog readers into Telegram subscribers + broker signups (the income)."""
    L = LINKS
    t = TOOL_PAGES[date.today().timetuple().tm_yday % len(TOOL_PAGES)]
    tool_teaser, tool_url = t[1], t[2]
    return (
        '\n\n<div style="border:2px solid #0062ff;border-radius:14px;'
        'padding:18px 20px;margin:32px 0;background:#f5f9ff">\n'
        '<h3 style="margin:0 0 8px">📈 Get Tomorrow\'s Trade Setups — Free</h3>\n'
        f'<p style="margin:6px 0">🎯 Join our <a href="{L["telegram"]}">'
        '<b>free Telegram channel</b></a> for daily Nifty signals &amp; market alerts.</p>\n'
        f'<p style="margin:6px 0">💎 Want exact entry / stop-loss / target? '
        f'<b>{MEMBERSHIP}</b> — DM us on <a href="{L["telegram"]}">Telegram</a>.</p>\n'
        '<p style="margin:6px 0">🪙 Open a <b>free demat</b> to trade these ideas: '
        f'<a href="{L["zerodha"]}">Zerodha</a> · '
        f'<a href="{L["dhan"]}">Dhan</a> · '
        f'<a href="{L["groww"]}">Groww</a> · '
        f'<a href="{L["coindcx"]}">CoinDCX (crypto)</a></p>\n'
        f'<p style="margin:6px 0">🧮 {tool_teaser} — '
        f'<a href="{tool_url}">try our free calculator</a>.</p>\n'
        '<p style="margin:6px 0;font-size:0.9em;color:#555">💬 Found this useful? '
        'Share it with a trader friend. <i>Educational only — not SEBI registered.</i></p>\n'
        '</div>\n'
    )
