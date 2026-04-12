"""
token_refresh.py — Auto META Token Refresh
==========================================
Runs every 50 days via GitHub Actions.
Exchanges current META token for new 60-day token.
Updates GitHub Secret automatically.
Sends Telegram alert on success or failure.

Author: AI360Trading Automation
Last Updated: April 2026
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

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

META_TOKEN         = os.environ.get("META_ACCESS_TOKEN", "")
META_TOKEN_KIDS    = os.environ.get("META_ACCESS_TOKEN_KIDS", "")   # ← ADDED
META_APP_ID        = os.environ.get("META_APP_ID", "")
META_APP_SECRET    = os.environ.get("META_APP_SECRET", "")
GH_TOKEN           = os.environ.get("GH_TOKEN", "")
GH_REPO            = os.environ.get("GITHUB_REPOSITORY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")

# ─────────────────────────────────────────────
# STEP 1: Exchange for new long-lived token
# ─────────────────────────────────────────────

def refresh_meta_token(current_token: str, app_id: str, app_secret: str) -> str:
    url = "https://graph.facebook.com/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": current_token,
    }
    logger.info("🔄 Requesting new META long-lived token...")
    response = requests.get(url, params=params, timeout=30)
    if response.status_code != 200:
        raise Exception(f"META token refresh failed: {response.status_code} — {response.text}")
    data = response.json()
    if "access_token" not in data:
        raise Exception(f"No access_token in response: {data}")
    new_token = data["access_token"]
    expires_in = data.get("expires_in", "unknown")
    logger.info(f"✅ New token received. Expires in: {expires_in} seconds")
    return new_token

# ─────────────────────────────────────────────
# STEP 2: Verify new token permissions
# ─────────────────────────────────────────────

def verify_token_permissions(token: str) -> dict:
    url = "https://graph.facebook.com/me/permissions"
    params = {"access_token": token}
    response = requests.get(url, params=params, timeout=30)
    data = response.json()
    permissions = {}
    for perm in data.get("data", []):
        permissions[perm["permission"]] = perm["status"]

    required = [
        "pages_show_list",
        "pages_read_engagement",
        "pages_manage_posts",
        # REMOVED: publish_to_groups — Facebook Group removed from project
    ]
    missing = [p for p in required if permissions.get(p) != "granted"]
    if missing:
        logger.warning(f"⚠️ Missing permissions: {missing}")
    else:
        logger.info("✅ All required permissions present")
    return {"permissions": permissions, "missing": missing}

# ─────────────────────────────────────────────
# STEP 3: Update GitHub Secret
# ─────────────────────────────────────────────

def get_repo_public_key(repo: str, gh_token: str) -> tuple:
    url = f"https://api.github.com/repos/{repo}/actions/secrets/public-key"
    headers = {
        "Authorization": f"token {gh_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers, timeout=30)
    data = response.json()
    return data["key_id"], data["key"]

def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    try:
        from nacl import encoding, public
    except ImportError:
        raise ImportError("PyNaCl not installed. Run: pip install PyNaCl")
    public_key_bytes = base64.b64decode(public_key_b64)
    sealed_box = public.SealedBox(public.PublicKey(public_key_bytes))
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def update_github_secret(repo: str, gh_token: str, secret_name: str, secret_value: str) -> bool:
    try:
        key_id, public_key = get_repo_public_key(repo, gh_token)
        encrypted_value = encrypt_secret(public_key, secret_value)
        url = f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}"
        headers = {
            "Authorization": f"token {gh_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        payload = {
            "encrypted_value": encrypted_value,
            "key_id": key_id,
        }
        response = requests.put(url, headers=headers, json=payload, timeout=30)
        if response.status_code in [201, 204]:
            logger.info(f"✅ GitHub Secret '{secret_name}' updated successfully")
            return True
        else:
            logger.error(f"❌ Failed to update secret: {response.status_code} — {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ GitHub secret update error: {e}")
        return False

# ─────────────────────────────────────────────
# STEP 4: Send Telegram Alert
# ─────────────────────────────────────────────

def send_telegram_alert(message: str, success: bool = True) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram not configured — skipping alert")
        return
    emoji = "✅" if success else "❌"
    now_ist = datetime.now(IST).strftime("%d %b %Y %I:%M %p IST")
    full_message = (
        f"{emoji} *AI360Trading — Token Refresh*\n\n"
        f"{message}\n\n"
        f"🕐 {now_ist}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": full_message,
        "parse_mode": "Markdown",
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("✅ Telegram alert sent")
        else:
            logger.warning(f"Telegram alert failed: {response.status_code}")
    except Exception as e:
        logger.warning(f"Telegram alert error: {e}")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    logger.info("=" * 60)
    logger.info("AI360Trading — META Token Auto-Refresh")
    logger.info("=" * 60)

    missing_vars = []
    if not META_TOKEN:
        missing_vars.append("META_ACCESS_TOKEN")
    if not META_APP_ID:
        missing_vars.append("META_APP_ID")
    if not META_APP_SECRET:
        missing_vars.append("META_APP_SECRET")
    if not GH_TOKEN:
        missing_vars.append("GH_TOKEN")
    if not GH_REPO:
        missing_vars.append("GITHUB_REPOSITORY")

    if missing_vars:
        msg = f"Missing required secrets: {', '.join(missing_vars)}"
        logger.error(f"❌ {msg}")
        send_telegram_alert(
            f"Token refresh FAILED!\n\nMissing secrets: `{', '.join(missing_vars)}`\n\n"
            f"⚠️ Please add these to GitHub Secrets immediately!",
            success=False
        )
        sys.exit(1)

    results = []

    # ── Refresh Trading Page Token ──
    try:
        logger.info("── Refreshing Trading Page token ──")
        new_token = refresh_meta_token(META_TOKEN, META_APP_ID, META_APP_SECRET)
        perm_result = verify_token_permissions(new_token)
        missing_perms = perm_result.get("missing", [])
        secret_updated = update_github_secret(GH_REPO, GH_TOKEN, "META_ACCESS_TOKEN", new_token)
        if not secret_updated:
            raise Exception("GitHub Secret update failed for META_ACCESS_TOKEN")
        perm_status = "✅ All OK" if not missing_perms else f"⚠️ Missing: {', '.join(missing_perms)}"
        results.append(f"🔑 Trading Page token: ✅ Refreshed\n   Permissions: {perm_status}")
        logger.info("✅ Trading Page token refreshed")
    except Exception as e:
        results.append(f"🔑 Trading Page token: ❌ FAILED — {e}")
        logger.error(f"❌ Trading Page token refresh failed: {e}")

    # ── Refresh Kids Page Token ──
    if META_TOKEN_KIDS:
        try:
            logger.info("── Refreshing Kids Page token ──")
            new_token_kids = refresh_meta_token(META_TOKEN_KIDS, META_APP_ID, META_APP_SECRET)
            perm_result_kids = verify_token_permissions(new_token_kids)
            missing_perms_kids = perm_result_kids.get("missing", [])
            secret_updated_kids = update_github_secret(GH_REPO, GH_TOKEN, "META_ACCESS_TOKEN_KIDS", new_token_kids)
            if not secret_updated_kids:
                raise Exception("GitHub Secret update failed for META_ACCESS_TOKEN_KIDS")
            perm_status_kids = "✅ All OK" if not missing_perms_kids else f"⚠️ Missing: {', '.join(missing_perms_kids)}"
            results.append(f"👶 Kids Page token: ✅ Refreshed\n   Permissions: {perm_status_kids}")
            logger.info("✅ Kids Page token refreshed")
        except Exception as e:
            results.append(f"👶 Kids Page token: ❌ FAILED — {e}")
            logger.error(f"❌ Kids Page token refresh failed: {e}")
    else:
        results.append("👶 Kids Page token: ⏭ Skipped (META_ACCESS_TOKEN_KIDS not set)")
        logger.warning("META_ACCESS_TOKEN_KIDS not set — skipping kids token refresh")

    # ── Send Summary Alert ──
    summary = "\n\n".join(results)
    all_ok = all("✅" in r for r in results if "⏭" not in r)
    send_telegram_alert(
        f"Token Refresh Complete!\n\n{summary}\n\n⏳ Next auto-refresh: in 50 days",
        success=all_ok
    )

    logger.info("=" * 60)
    logger.info("✅ Token refresh complete!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
