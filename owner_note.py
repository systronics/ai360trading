"""owner_note.py v1.0 (2026-11-17) - sends a plain-text note (file given as argv[1]) ONLY to the private owner channel (secret CHAT_ID_OWNER).
Messages in the file are separated by a line containing only '-----'. Never falls back to any subscriber channel. Prints no token/id.
"""
import json
import os
import sys
from urllib.request import Request, urlopen


def split_messages(text, limit=3800):
    out = []
    for part in text.split("\n-----\n"):
        part = part.strip()
        while len(part) > limit:
            cut = part.rfind("\n", 0, limit)
            cut = cut if cut > 0 else limit
            out.append(part[:cut].strip())
            part = part[cut:].strip()
        if part:
            out.append(part)
    return out


def main(argv):
    tok = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat = os.environ.get("CHAT_ID_OWNER", "").strip()
    if not tok or not chat:
        print("no TELEGRAM_BOT_TOKEN / CHAT_ID_OWNER - nothing sent")
        return 1
    msgs = split_messages(open(argv[1], encoding="utf-8").read())
    for i, m in enumerate(msgs, 1):
        req = Request(f"https://api.telegram.org/bot{tok}/sendMessage",
                      data=json.dumps({"chat_id": chat, "text": m, "disable_web_page_preview": True}).encode(),
                      headers={"Content-Type": "application/json"})
        urlopen(req, timeout=20).read()
        print(f"sent message {i}/{len(msgs)} ({len(m)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
