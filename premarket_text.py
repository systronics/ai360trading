"""
premarket_text.py v1.0 (2026-11-18) - the same pre-market global read as the reel, as ONE short Hinglish TEXT for the PREMIUM Telegram channel only.
Owner 2026-11-18: the reel (Facebook/Instagram) shows US/crude/Asia/VIX and a POSITIVE/NEGATIVE/MIXED verdict, but Telegram only had the Nifty-vs-DMA Good Morning.
INFORMATION ONLY: no entry/SL/target, no gate reads it, no GIFT Nifty number (no free source). Free Yahoo data via premarket_brief.fetch_rows(). Fail-open: any problem = nothing is sent.
Once a day: _data/premarket_text_done.json (date), written by this script after a successful send; the workflow commits it.
Mode: sends only when env MODE == 'scheduled' (same repo variable PREMARKET_MODE as the reel) or with --force; otherwise prints.
"""
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from urllib.request import Request, urlopen

import premarket_brief as PB

DONE = "_data/premarket_text_done.json"
IT_MOVE = 0.7   # Nasdaq move (%) from which an IT-sector remark is added


def _arrow(p):
    return "🟢" if p > 0.05 else ("🔴" if p < -0.05 else "⚪")


def _fmt(rows, key, label=None):
    r = rows.get(key)
    return f"{_arrow(r['pct'])} {label or key} {r['pct']:+.2f}%" if r else None


def build_text(rows, v, results, day):
    """Pure. Returns the HTML message text or '' when there is not enough data (fewer than 4 key rows)."""
    keys = ("NASDAQ", "S&P 500", "DOW", "NIKKEI", "HANG SENG", "CRUDE WTI")
    if sum(1 for k in keys if k in rows) < 4:
        return ""
    head = {"POSITIVE": "🟢 Global cues POSITIVE - Nifty ka khulna upar ki taraf ho sakta hai",
            "NEGATIVE": "🔴 Global cues KAMZOR - Nifty halka neeche / cautious khul sakta hai",
            "MIXED": "⚪ Global cues MILE-JULE - Nifty flat / mila-jula khul sakta hai"}[v]
    lines = [f"🌍 <b>Pre-market global read — {day.strftime('%d %b')}</b>", head, ""]
    us = [x for x in (_fmt(rows, "NASDAQ"), _fmt(rows, "S&P 500"), _fmt(rows, "DOW")) if x]
    asia = [x for x in (_fmt(rows, "NIKKEI"), _fmt(rows, "HANG SENG")) if x]
    cm = [x for x in (_fmt(rows, "CRUDE WTI", "Crude"), _fmt(rows, "GOLD", "Gold")) if x]
    if us:
        lines.append("US: " + "  ".join(us))
    if asia:
        lines.append("Asia: " + "  ".join(asia))
    if cm:
        lines.append("Commodity: " + "  ".join(cm))
    vx, inr = rows.get("INDIA VIX"), rows.get("USD/INR")
    extra = []
    if vx:
        extra.append(f"India VIX {vx['last']:.1f} ({'kam darr' if vx['last'] < 15 else ('normal' if vx['last'] < 20 else 'ooncha - jhatke zyada')})")
    if inr:
        extra.append(f"USD/INR {inr['last']:.2f} ({inr['pct']:+.2f}%)")
    if extra:
        lines.append(" | ".join(extra))
    nq = rows.get("NASDAQ")
    if nq and nq["pct"] <= -IT_MOVE:
        lines.append("")
        lines.append("💻 US tech kamzor tha - aaj IT stocks (INFY/TCS...) par dabav ho sakta hai, IT me long se savdhan.")
    elif nq and nq["pct"] >= IT_MOVE:
        lines.append("")
        lines.append("💻 US tech mazboot tha - IT stocks ko support mil sakta hai.")
    cr = rows.get("CRUDE WTI")
    if cr and cr["pct"] <= -1.5:
        lines.append("🛢 Crude me tez giravat - aam taur par India ke liye rahat, par saath me global risk-off bhi ho sakta hai.")
    elif cr and cr["pct"] >= 1.5:
        lines.append("🛢 Crude me tez tezi - India ke liye dabav (OMC/paint/aviation).")
    if results:
        lines.append("")
        lines.append("📅 Aaj result: " + ", ".join(results[:10]) + (" ..." if len(results) > 10 else "") + " (result wale din option mat lo)")
    lines += ["", "ℹ️ Ye sirf jaankari hai, entry signal nahi. Asli faisla pehle 15-30 min ka move dekh kar. GIFT Nifty apne chart par dekho.",
              "<i>Educational, SEBI advice nahi.</i>"]
    return "\n".join(lines)


def ist_now(now_utc=None):
    return (now_utc or datetime.now(timezone.utc)) + timedelta(hours=5, minutes=30)


def already_sent(today_iso):
    try:
        return json.load(open(DONE, encoding="utf-8")).get("date") == today_iso
    except Exception:
        return False


def send(text):
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN", ""), os.environ.get("CHAT_ID_PREMIUM", "")
    if not tok or not chat:
        print("[PM-TEXT] no token/chat - not sent")
        return False
    body = json.dumps({"chat_id": chat, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}).encode()
    r = json.loads(urlopen(Request(f"https://api.telegram.org/bot{tok}/sendMessage", data=body, headers={"Content-Type": "application/json"}), timeout=20).read().decode())
    return bool(r.get("ok"))


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    force = "--force" in argv
    now = ist_now()
    today = now.date()
    try:
        if not force and already_sent(today.isoformat()):
            print("[PM-TEXT] already sent today")
            return 0
        rows = PB.fetch_rows()
        text = build_text(rows, PB.verdict(rows), PB.results_for(today), today)
        if not text:
            print("[PM-TEXT] not enough data - nothing sent")
            return 0
        if os.environ.get("MODE") != "scheduled" and not force:
            print("[PM-TEXT] dry mode - would send:\n" + text)
            return 0
        if send(text):
            os.makedirs("_data", exist_ok=True)
            json.dump({"date": today.isoformat()}, open(DONE, "w", encoding="utf-8"))
            print("[PM-TEXT] sent to Premium")
        else:
            print("[PM-TEXT] Telegram did not accept it")
    except Exception as e:
        print("[PM-TEXT] failed (fail-open):", str(e)[:120])
    return 0


if __name__ == "__main__":
    sys.exit(main())
