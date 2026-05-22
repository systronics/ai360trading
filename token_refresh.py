"""
token_refresh.py — Auto META Token Refresh
==========================================
v2.1 FIX (May 2026):
  TELEGRAM_CHAT_ID → CHAT_ID_BASIC
  Reason: TELEGRAM_CHAT_ID secret does not exist in GitHub
          All Telegram alerts were going nowhere
          CHAT_ID_BASIC is the correct secret name

Also: META_ACCESS_TOKEN_KIDS refresh added (was missing)
      Kids token now auto-refreshed same day as main token

Runs every 50 days via GitHub Actions (1st and 20th of month).
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
META_TOKEN_KIDS    = os.environ.get("META_ACCESS_TOKEN_KIDS", "")
META_APP_ID        = os.environ.get("META_APP_ID", "")
META_APP_SECRET    = os.environ.get("META_APP_SECRET", "")
GH_TOKEN           = os.environ.get("GH_TOKEN", "")
GH_REPO            = os.environ.get("GITHUB_REPOSITORY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
# System health alerts go to ADVANCE channel — not BASIC (trading followers don't need to see this)
CHAT_ID            = os.environ.get("CHAT_ID_ADVANCE", "")


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
    if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        logger.warning("Telegram not configured — skipping alert")
        return
    emoji    = "✅" if success else "❌"
    now_ist  = datetime.now(IST).strftime("%d %b %Y %I:%M %p IST")
    full_msg = (
        f"{emoji} *AI360Trading — Token Refresh*\n\n"
        f"{message}\n\n"
        f"🕐 {now_ist}"
    )
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": full_msg, "parse_mode": "Markdown"},
            timeout=10,
        )
        if r.status_code == 200:
            logger.info("✅ Telegram alert sent to Basic channel")
        else:
            logger.warning(f"Telegram alert failed: {r.status_code}")
    except Exception as e:
        logger.warning(f"Telegram alert error: {e}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    logger.info("=" * 55)
    logger.info("AI360Trading — META Token Refresh v2.1")
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

    # ── Refresh HerooQuest Kids token ─────────────────────────────────────────
    if META_TOKEN_KIDS:
        try:
            new_kids_token = refresh_meta_token(META_TOKEN_KIDS, META_APP_ID, META_APP_SECRET)
            kids_ok        = update_github_secret(GH_REPO, GH_TOKEN, "META_ACCESS_TOKEN_KIDS", new_kids_token)
            if kids_ok:
                results.append(("META_ACCESS_TOKEN_KIDS", True, "HerooQuest Kids token refreshed ✅"))
            else:
                results.append(("META_ACCESS_TOKEN_KIDS", False, "Kids token refresh — GitHub update failed"))
        except Exception as e:
            logger.error(f"Kids token refresh error: {e}")
            results.append(("META_ACCESS_TOKEN_KIDS", False, str(e)))
    else:
        logger.info("META_ACCESS_TOKEN_KIDS not set — skipping kids token")

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
