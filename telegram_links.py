"""
telegram_links.py v1.0 (2026-10-23) — one NAMED Telegram invite link per traffic source.

Why: we cannot tell which platform (Facebook, YouTube, website, ...) actually brings Telegram members, because
every post uses the same public t.me/ai360trading link. A named invite link lets Telegram itself count the people
who joined through it: in the Telegram app open the channel > Manage channel > Invite links — each link shows
"N joined". The bot API cannot read that count, so reading it stays a 10-second manual look.

Run in GitHub Actions (workflow telegram-links.yml, manual) because the bot token lives in secrets only.
Idempotent: only creates a source that has no link yet; writes _data/telegram_links.json {source: url}.
Fail-open: any problem prints the reason and leaves the existing file untouched (callers then keep the plain link).
Needs the bot to be an ADMIN of the channel with the 'invite users' right.
"""
import json
import os
import sys
from pathlib import Path

import requests

SOURCES = ["facebook", "youtube", "social", "website", "articles"]
OUT = Path("_data/telegram_links.json")


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat = os.environ.get("CHAT_ID_BASIC", "")
    if not token or not chat:
        print("[TGLINKS] token/chat missing — nothing done")
        return 0
    try:
        links = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    except Exception:
        links = {}
    changed = False
    for src in SOURCES:
        if links.get(src):
            continue
        try:
            r = requests.post(f"https://api.telegram.org/bot{token}/createChatInviteLink",
                              json={"chat_id": chat, "name": f"AI360-{src}"}, timeout=20)
            d = r.json()
            if d.get("ok"):
                links[src] = d["result"]["invite_link"]
                changed = True
                print(f"[TGLINKS] created {src}")
            else:
                print(f"[TGLINKS] {src}: {d.get('description')} (bot must be channel admin with invite right)")
                break
        except Exception as e:
            print(f"[TGLINKS] {src}: {e}")
            break
    if changed:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(links, indent=1), encoding="utf-8")
        print(f"[TGLINKS] saved {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
