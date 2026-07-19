"""
token_refresh.py — Auto META Token Refresh
==========================================
v2.2 FIX (May 2026):
  CHAT_ID single → list of [CHAT_ID_BASIC, CHAT_ID_ADVANCE]
  Reason: v2.1 added CHAT_ID_BASIC env var to the workflow, but the script
          still only read CHAT_ID_ADVANCE — so Basic channel never received
          token refresh alerts. v2.2 sends to both channels so Amit ji sees
          token status on whichever channel he's monitoring.

v2.1 FIX (May 2026):
  TELEGRAM_CHAT_ID → CHAT_ID_BASIC env var added to workflow
  Reason: TELEGRAM_CHAT_ID secret does not exist in GitHub
          CHAT_ID_BASIC is the correct secret name

2026-07-19: HerooQuest Kids Meta-token refresh removed (kids channel retired).

Runs 1st + 15th of every month via GitHub Actions.
Exchanges current META token for new 60-day token.
Updates GitHub Secret automatically.
Sends Telegram alert on success or failure.
"""

import os
import sys
import json
import requests
import base64
import logging
from datetime import datetime
import pytz

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")

# ─── CONFIG ───────────────────────────────────────────────────────────────────

META_TOKEN         = os.environ.get("META_ACCESS_TOKEN", "")
META_APP_ID        = os.environ.get("META_APP_ID", "")
META_APP_SECRET    = os.environ.get("META_APP_SECRET", "")
GH_TOKEN           = os.environ.get("GH_TOKEN", "")
GH_REPO            = os.environ.get("GITHUB_REPOSITORY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
# v2.2: Token alerts go to BOTH Basic and Advance — Amit ji monitors both
CHAT_ID_BASIC      = os.environ.get("CHAT_ID_BASIC", "")
CHAT_ID_ADVANCE    = os.environ.get("CHAT_ID_ADVANCE", "")
CHAT_IDS           = [cid for cid in (CHAT_ID_BASIC, CHAT_ID_ADVANCE) if cid]


# ─── STEP 1: Exchange for new long-lived token ────────────────────────────────

def refresh_meta_token(current_token: str, app_id: str, app_secret: str) -> str:
    if not current_token:
        raise Exception("No token provided — skipping")
    url = "https://graph.facebook.com/oauth/access_token"
    params = {
        "grant_type":       "fb_exchange_token",
        "client_id":        app_id,
        "client_secret":    app_secret,
        "fb_exchange_token": current_token,
    }
    logger.info("🔄 Requesting new META long-lived token...")
    response = requests.get(url, params=params, timeout=30)
    if response.status_code != 200:
        raise Exception(f"META token refresh failed: {response.status_code} — {response.text}")
    data = response.json()
    if "access_token" not in data:
        raise Exception(f"No access_token in response: {data}")
    new_token  = data["access_token"]
    expires_in = data.get("expires_in", "unknown")
    logger.info(f"✅ New token received. Expires in: {expires_in} seconds")
    return new_token


# ─── STEP 2: Verify token permissions ────────────────────────────────────────

def verify_token_permissions(token: str) -> dict:
    url      = "https://graph.facebook.com/me/permissions"
    params   = {"access_token": token}
    response = requests.get(url, params=params, timeout=30)
    data     = response.json()
    permissions = {}
    for perm in data.get("data", []):
        permissions[perm["permission"]] = perm["status"]

    required = [
        "pages_show_list",
        "pages_read_engagement",
        "pages_manage_posts",
        "pages_manage_engagement",
        "pages_manage_metadata",
    ]
    missing = [p for p in required if permissions.get(p) != "granted"]
    if missing:
        logger.warning(f"⚠️ Missing permissions: {missing}")
    else:
        logger.info("✅ All required permissions present")
    return {"permissions": permissions, "missing": missing}


# ─── STEP 3: Update GitHub Secret ────────────────────────────────────────────

def get_repo_public_key(repo: str, gh_token: str) -> tuple:
    url     = f"https://api.github.com/repos/{repo}/actions/secrets/public-key"
    headers = {"Authorization": f"token {gh_token}", "Accept": "application/vnd.github.v3+json"}
    data    = requests.get(url, headers=headers, timeout=30).json()
    return data["key_id"], data["key"]

def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    try:
        from nacl import encoding, public
    except ImportError:
        raise ImportError("PyNaCl not installed. Run: pip install PyNaCl")
    public_key_bytes = base64.b64decode(public_key_b64)
    sealed_box       = public.SealedBox(public.PublicKey(public_key_bytes))
    encrypted        = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def update_github_secret(repo: str, gh_token: str, secret_name: str, secret_value: str) -> bool:
    try:
        key_id, public_key = get_repo_public_key(repo, gh_token)
        encrypted_value    = encrypt_secret(public_key, secret_value)
        url     = f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}"
        headers = {"Authorization": f"token {gh_token}", "Accept": "application/vnd.github.v3+json"}
        payload = {"encrypted_value": encrypted_value, "key_id": key_id}
        r       = requests.put(url, headers=headers, json=payload, timeout=30)
        if r.status_code in [201, 204]:
            logger.info(f"✅ GitHub Secret '{secret_name}' updated")
            return True
        else:
            logger.error(f"❌ Secret update failed: {r.status_code} — {r.text}")
            return False
    except Exception as e:
        logger.error(f"❌ GitHub secret error: {e}")
        return False


# ─── STEP 4: Send Telegram Alert (to Basic channel) ──────────────────────────

def send_telegram_alert(message: str, success: bool = True) -> None:
    if not TELEGRAM_BOT_TOKEN or not CHAT_IDS:
        logger.warning("Telegram not configured — skipping alert")
        return
    emoji    = "✅" if success else "❌"
    now_ist  = datetime.now(IST).strftime("%d %b %Y %I:%M %p IST")
    full_msg = (
        f"{emoji} *AI360Trading — Token Refresh*\n\n"
        f"{message}\n\n"
        f"🕐 {now_ist}"
    )
    for cid in CHAT_IDS:
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": cid, "text": full_msg, "parse_mode": "Markdown"},
                timeout=10,
            )
            if r.status_code == 200:
                logger.info(f"✅ Telegram alert sent to chat {cid[-4:]}")
            else:
                logger.warning(f"Telegram alert failed for {cid[-4:]}: {r.status_code}")
        except Exception as e:
            logger.warning(f"Telegram alert error for {cid[-4:]}: {e}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    logger.info("=" * 55)
    logger.info("AI360Trading — META Token Refresh v2.2")
    logger.info("=" * 55)

    if not all([META_APP_ID, META_APP_SECRET, GH_TOKEN, GH_REPO]):
        msg = "❌ Missing required env vars: META_APP_ID, META_APP_SECRET, GH_TOKEN, GITHUB_REPOSITORY"
        logger.error(msg)
        send_telegram_alert(msg, success=False)
        sys.exit(1)

    results = []

    # ── Refresh main AI360Trading token ──────────────────────────────────────
    if META_TOKEN:
        try:
            new_token   = refresh_meta_token(META_TOKEN, META_APP_ID, META_APP_SECRET)
            perm_check  = verify_token_permissions(new_token)
            missing     = perm_check.get("missing", [])
            secret_ok   = update_github_secret(GH_REPO, GH_TOKEN, "META_ACCESS_TOKEN", new_token)

            if secret_ok:
                msg = "META_ACCESS_TOKEN refreshed ✅"
                if missing:
                    msg += f"\n⚠️ Missing permissions: {', '.join(missing)}"
                results.append(("META_ACCESS_TOKEN", True, msg))
                logger.info(msg)
            else:
                results.append(("META_ACCESS_TOKEN", False, "Token refreshed but GitHub update failed"))
        except Exception as e:
            logger.error(f"Main token refresh error: {e}")
            results.append(("META_ACCESS_TOKEN", False, str(e)))
    else:
        logger.warning("META_ACCESS_TOKEN not set — skipping main token")

    # (HerooQuest Kids Meta-token refresh removed 2026-07-19 — kids channel retired.)

    # ── Summary ───────────────────────────────────────────────────────────────
    all_ok  = all(r[1] for r in results)
    summary = "\n".join([f"{'✅' if r[1] else '❌'} {r[0]}: {r[2]}" for r in results])
    if not results:
        summary = "⚠️ No tokens were refreshed — check env vars"
        all_ok  = False

    send_telegram_alert(summary, success=all_ok)

    logger.info("=" * 55)
    logger.info("TOKEN REFRESH DONE")
    for name, ok, msg in results:
        logger.info(f"  {'✅' if ok else '❌'} {name}: {msg}")
    logger.info("=" * 55)

    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
