"""owner_chat_setup.py v1.0 (2026-11-15) - one-time helper: find the private owner Telegram channel and (only when asked) store its id.

Reads the bot's updates, looks for a channel whose title contains OWNER_CHAT_TITLE (default 'owner alerts'),
sends ONE test message to it and prints only the title + the LAST 4 DIGITS of the id (this repo is public, so the
full id is never printed). With SET_SECRET=yes it stores the full id as the repo secret CHAT_ID_OWNER via the gh CLI.
Read-only otherwise. Needs the bot to be ADMIN of the channel and a message posted AFTER that.
"""
import json
import os
import subprocess
import sys
from urllib.request import Request, urlopen

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TITLE = os.environ.get("OWNER_CHAT_TITLE", "owner alerts").lower()


def api(method, payload=None):
    req = Request(
        f"https://api.telegram.org/bot{TOKEN}/{method}",
        data=json.dumps(payload or {}).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(urlopen(req, timeout=20).read().decode())


def find_channel():
    upd = api("getUpdates", {"allowed_updates": ["channel_post", "my_chat_member", "message"]})
    found = {}
    for u in upd.get("result", []):
        for key in ("channel_post", "my_chat_member", "message"):
            chat = (u.get(key) or {}).get("chat") or {}
            if chat.get("type") == "channel" and TITLE in (chat.get("title") or "").lower():
                found[chat["id"]] = chat.get("title")
    return found


def main():
    if not TOKEN:
        print("no bot token in env"); return 1
    found = find_channel()
    if not found:
        print("NOT FOUND: make the bot an ADMIN of the channel, then post a new message in the channel, then run again.")
        return 1
    if len(found) > 1:
        print("More than one matching channel:", {str(k)[-4:]: v for k, v in found.items()}); return 1
    cid, title = next(iter(found.items()))
    print(f"FOUND channel '{title}' id ends with ...{str(cid)[-4:]}")
    try:
        api("sendMessage", {"chat_id": cid, "text": "AI360 owner chat connected. Health, token and error reports will arrive here."})
        print("test message sent")
    except Exception as e:  # noqa: BLE001
        print("could not send (is the bot an admin with Post Messages?):", type(e).__name__)
        return 1
    if os.environ.get("SET_SECRET", "").lower() == "yes":
        repo = os.environ.get("GITHUB_REPOSITORY", "")
        r = subprocess.run(["gh", "secret", "set", "CHAT_ID_OWNER", "--repo", repo, "--body", str(cid)],
                           capture_output=True, text=True)
        print("secret set OK" if r.returncode == 0 else "secret set FAILED: " + r.stderr[:200])
        return r.returncode
    print("secret NOT set (run again with set_secret=yes after the owner confirms)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
