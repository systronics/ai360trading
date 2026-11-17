"""
pinned_rules.py v1.0 (2026-11-05) — the ONE pinned 'rules + kaise trade kare' message per Telegram channel.

WHY (owner 2026-11-05: 'telegram message too long ... ek message bna do each channel k liye taki use pin kar do aur baar baar na aaye'): every alert used to repeat the
same rules / how-to / TradingView lines. They now live here, once per channel; alerts carry only the data plus a one-line pointer to the pinned message.

USAGE (workflow `pin-rules.yml`, manual only; needs TELEGRAM_BOT_TOKEN + CHAT_ID_BASIC/ADVANCE/PREMIUM):
  python pinned_rules.py --print                 print the three texts
  python pinned_rules.py --preview               send all three to the PREMIUM channel only (owner reviews them), nothing is pinned
  python pinned_rules.py --post [--pin]          send each text to its own channel (+ pin it; needs the bot to be channel admin with 'pin messages')
  python pinned_rules.py --update-premium        v1.1 (2026-11-17): EDIT the already pinned PREMIUM message in place (no duplicate, nothing new is pinned); does nothing if the pinned message is not the PREMIUM rules text
Facts used here must match the system: Cash Intraday is force-exited at 3:10 PM; options (owner rules 2026-11-17) = buy-side CE, retest only, expiry >= 8 days,
exit at 3 trading days if not in profit / max 5 trading days, hard cap 20%, expiry-week exit.
"""
import os
import sys
import json
from urllib.request import Request, urlopen

BASIC = """📌 <b>AI360Trading — FREE channel (kaise padhein)</b>

Yahan roz: 🌅 Good Morning (market ka mood), 1 teaser signal, aur hafte ka honest scorecard (jeet aur haar dono).
Poore signals (Entry, SL, Target) Advance/Premium me aate hain.

<b>Har signal ke 5 niyam</b>
1️⃣ Ye educational / paper-trading hai. SEBI advice nahi. Faisla aur risk aapka.
2️⃣ Signal 5-10 min purana ho sakta hai. Price "chase limit" se upar ho to SKIP.
3️⃣ SL ke bina kabhi trade nahi.
4️⃣ Ek trade me capital ka 1-2% se zyada risk nahi.
5️⃣ Entry tab tak valid jab tak price SL ke upar hai.

<i>AI360Trading SEBI registered nahi hai. Ye educational analysis hai, investment advice nahi. Apni research aur apna risk.
Is message ko pin rakha hai, baar baar nahi aayega.</i>"""

ADVANCE = """📌 <b>ADVANCE — rules (ek baar padhein)</b>

<b>Signal ke type</b>
🔄 Swing / 📦 Base = 2-4 hafte → CASH ya MTF me kharide. Chart: DAILY
💰 Positional = hafte-mahine → CASH ya accumulate. Chart: WEEKLY
🔥 Cash Intraday = usi din ka trade, 3:10 PM tak nikal jao (overnight nahi). Chart: 15m

<b>Har alert me</b>: Entry, SL, Target, RR aur "chase limit" (us price ke upar ho to skip).
✅ Entry valid jab tak price SL ke upar hai (agle din bhi le sakte ho)
🛑 SL tode to exit. Trailing SL update aaye to SL upar kar do.

<b>Subah</b>: 8:45 Good Morning + Watch Plan = sirf idea (entry signal nahi), chart par khud confirm karo.
<b>Raat ka scan</b> "kal ke close ka data" hota hai: subah 9:30 ke baad confirm karo, red khule to skip.

Risk: ek trade me capital ka 1-2% se zyada nahi. Educational only, SEBI advice nahi.
<i>AI360Trading SEBI registered nahi hai. Ye educational analysis hai, investment advice nahi. Apni research aur apna risk.
Pinned: baar baar nahi aayega.</i>"""

PREMIUM = """📌 <b>PREMIUM — rules (ek baar padhein)</b>

Advance ke saare rules lagu hain (Swing / Base / Positional / Cash). Premium me ye bhi:

<b>📊 Options signal</b> (sirf buy-side CE)
🎯 Option call sirf RETEST par aati hai (stock breakout ke baad wapas breakout level par). Isliye roz 0-2 hi aayengi, kabhi koi na aaye to wo normal hai.
📅 Expiry kam se kam 8 din door. Alert me jo strike + expiry likhi hai WAHI lo, doosri nahi.
🕘 Kab: 9:30-9:45 (raat ka scan: subah confirm)
⏳ Hold: same day profit best. Profit me ho to max 5 trading din; 3 din tak profit na ho to nikal do
🛑 Exit: STOCK ka SL tode, ya STOCK target, ya premium me 20% loss (hard cap). Expiry se 5 din pehle sab nikal do
⚠️ Average down kabhi nahi. Chhota size rakho, poora premium ja sakta hai.
💧 Midcap chain: bid-ask dekho, limit order lagao

<b>🧾 F&O buildup</b> (sirf jaankari, signal nahi)
Long Buildup = futures price + OI dono badhe. Short Covering = price badhe, OI ghate.
Short Buildup / Long Unwinding = kamzor, avoid. Option ka P/L stock se alag hota hai (strike, expiry, theta).

Educational only, SEBI advice nahi.
<i>AI360Trading SEBI registered nahi hai. Ye educational analysis hai, investment advice nahi. Apni research aur apna risk.
Pinned: baar baar nahi aayega.</i>"""

TEXTS = {"basic": BASIC, "advance": ADVANCE, "premium": PREMIUM}


def _post(method, payload):
    tok = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not tok:
        raise RuntimeError("TELEGRAM_BOT_TOKEN missing")
    req = Request(f"https://api.telegram.org/bot{tok}/{method}", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urlopen(req, timeout=20).read().decode())


def send(chat_id, text, pin=False):
    r = _post("sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True})
    mid = r.get("result", {}).get("message_id")
    print(f"  sent to {chat_id}: message_id {mid}")
    if pin and mid:
        try:
            _post("pinChatMessage", {"chat_id": chat_id, "message_id": mid, "disable_notification": True})
            print("  pinned")
        except Exception as e:
            print(f"  pin failed (make the bot an admin with 'Pin messages'): {str(e)[:100]}")
    return mid


def update_premium(chat_id):
    """Edit the currently pinned PREMIUM rules message in place. Returns 0 on success or when nothing needed doing, 1 on a hard problem."""
    if not chat_id:
        print("no CHAT_ID_PREMIUM - nothing done")
        return 1
    try:
        pm = (_post("getChat", {"chat_id": chat_id}).get("result") or {}).get("pinned_message") or {}
    except Exception as e:
        print(f"getChat failed: {str(e)[:100]}")
        return 1
    mid, old = pm.get("message_id"), pm.get("text", "")
    if not mid or "PREMIUM" not in old or "rules" not in old:
        print("the pinned message is not the PREMIUM rules text - nothing edited (use --post --pin only if you really want a new one)")
        return 0
    if old.strip() == "".join(PREMIUM.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")).strip():
        print("pinned PREMIUM message is already up to date")
        return 0
    try:
        _post("editMessageText", {"chat_id": chat_id, "message_id": mid, "text": PREMIUM, "parse_mode": "HTML", "disable_web_page_preview": True})
        print(f"edited pinned PREMIUM message {mid} in place ({len(PREMIUM)} chars)")
        return 0
    except Exception as e:
        print(f"edit failed: {str(e)[:120]}")
        return 1


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--print" in argv:
        for k, v in TEXTS.items():
            print(f"=== {k} ({len(v)} chars) ===\n{v}\n")
        return 0
    ids = {"basic": os.environ.get("CHAT_ID_BASIC", ""), "advance": os.environ.get("CHAT_ID_ADVANCE", ""), "premium": os.environ.get("CHAT_ID_PREMIUM", "")}
    if "--preview" in argv:
        for k, v in TEXTS.items():
            send(ids["premium"], f"🔎 <b>PREVIEW — yeh {k.upper()} channel ka pinned message hoga</b> (abhi kahin pin nahi hua)\n\n{v}")
        return 0
    if "--update-premium" in argv:
        return update_premium(ids["premium"])
    if "--post" in argv:
        for k, v in TEXTS.items():
            if ids[k]:
                send(ids[k], v, pin="--pin" in argv)
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
