"""
threads_setup.py v1.0 (2026-11-10) - ONE-TIME helper the OWNER runs on his own PC to connect Threads. It never prints a token and never writes a token to a file.
You paste (the input is hidden): (1) the short-lived Threads token from the Meta app dashboard (valid only 1 hour, so run this right after you generate it) and (2) the Threads app secret.
It then: exchanges the short token for a 60-day token (GET graph.threads.com/access_token, grant_type=th_exchange_token), reads your Threads user id (GET /me), and stores THREADS_ACCESS_TOKEN and
THREADS_USER_ID as GitHub secrets with the `gh` CLI that is already logged in on this PC (the value goes through stdin, not the command line).
After it succeeds, switch posting on with:   gh variable set THREADS_MODE --body scheduled
USAGE: python threads_setup.py
"""
import getpass
import subprocess
import sys

import requests

GRAPH = "https://graph.threads.com"


def exchange(short_token, app_secret):
    """(long_token, expires_in) or raises. Pure network call."""
    r = requests.get(f"{GRAPH}/access_token", params={"grant_type": "th_exchange_token", "client_secret": app_secret, "access_token": short_token}, timeout=30)
    j = r.json()
    if "access_token" not in j:
        raise RuntimeError("exchange failed: " + str(j.get("error", j))[:200])
    return j["access_token"], j.get("expires_in")


def whoami(token):
    r = requests.get(f"{GRAPH}/v1.0/me", params={"fields": "id,username", "access_token": token}, timeout=30)
    j = r.json()
    if "id" not in j:
        raise RuntimeError("could not read the Threads user: " + str(j.get("error", j))[:200])
    return j["id"], j.get("username", "")


def set_secret(name, value):
    p = subprocess.run(["gh", "secret", "set", name], input=value, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"gh secret set {name} failed: " + (p.stderr or "")[:200])


def main():
    short = getpass.getpass("Short-lived Threads token (hidden): ").strip()
    secret = getpass.getpass("Threads app secret (hidden): ").strip()
    if not short or not secret:
        print("Both values are needed. Nothing was changed.")
        return 1
    try:
        long_token, expires = exchange(short, secret)
        uid, uname = whoami(long_token)
        set_secret("THREADS_ACCESS_TOKEN", long_token)
        set_secret("THREADS_USER_ID", uid)
    except Exception as e:
        print("Stopped:", str(e).replace(short, "***").replace(secret, "***"))
        return 1
    print(f"Done. Threads account @{uname} connected, token valid about {int(expires or 0) // 86400} days (refreshed automatically every 2 weeks).")
    print("Now run:  gh variable set THREADS_MODE --body scheduled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
