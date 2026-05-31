"""
money_funnel.py — single source of truth for every income CTA + link.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
    "coindcx":  "https://invite.coindcx.com/13383200",
}
MEMBERSHIP = "₹699 Advance / ₹1,499 Premium"

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
        demat = ("📈 FREE demat (Zerodha/Dhan): " + site
                 if lang == "hi" else
                 "📈 Free demat (Zerodha/Dhan): " + site)
        return "\n".join([free, prem, demat, engagement_prompt(lang)])

    free = (f"🎯 FREE daily trading signals → Telegram: {tg}")
    prem = (f"💎 Premium signals (exact entry / SL / target): "
            f"{MEMBERSHIP} — DM on Telegram")
    return "\n".join([
        free,
        prem,
        broker_lines(lang),
        f"🌐 {site}",
        engagement_prompt(lang),
    ])


def article_cta_html() -> str:
    """A styled conversion CTA box appended to the end of each website article.
    Turns blog readers into Telegram subscribers + broker signups (the income)."""
    L = LINKS
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
        f'<a href="{L["coindcx"]}">CoinDCX (crypto)</a></p>\n'
        '<p style="margin:6px 0;font-size:0.9em;color:#555">💬 Found this useful? '
        'Share it with a trader friend. <i>Educational only — not SEBI registered.</i></p>\n'
        '</div>\n'
    )
