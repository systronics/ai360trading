"""
reauth_youtube.py — one-time YouTube token re-auth with youtube.force-ssl
=========================================================================
WHY: uploading our exact .srt caption tracks (captions().insert) and custom
thumbnails needs the `youtube.force-ssl` OAuth scope. The current tokens were
created with `youtube.upload` only, so caption upload skips (fail-open). Run
this ONCE per channel to mint a new refresh token that has force-ssl, then
paste the printed JSON into the matching GitHub Actions secret.

This is a LOCAL helper — it is NOT part of any automated workflow and touches
no production code. It reuses the OAuth client embedded in your CURRENT token
JSON, so you do NOT need to download anything from Google Cloud Console.

────────────────────────────────────────────────────────────────────────────
EASY STEPS
────────────────────────────────────────────────────────────────────────────
1. Get your current token JSON:
     GitHub → your repo → Settings → Secrets and variables → Actions.
     You cannot READ a secret's value there, so instead use the copy you
     already have, OR (easiest) just run this script — it will ask you to
     paste the JSON. If you don't have it saved, see "GETTING THE JSON" below.

2. Install the one extra library (one time):
     pip install google-auth-oauthlib

3. Run for the MAIN channel:
     python reauth_youtube.py --which main

4. Paste your current token JSON when asked (one line), press Enter.

5. A browser window opens → pick the RIGHT Google account → click "Allow".

6. The script prints a NEW token JSON and also saves it to
     output/new_token_<which>.json
   Copy the WHOLE JSON.

7. In GitHub → Settings → Secrets → Actions → update the secret:
     main  → YOUTUBE_CREDENTIALS
   Click the secret, "Update", paste the new JSON, Save. Done.

That's it — the next daily run will upload the exact .srt automatically.

────────────────────────────────────────────────────────────────────────────
GETTING THE JSON (only if you don't have your current token saved)
────────────────────────────────────────────────────────────────────────────
The token JSON looks like:
  {"client_id":"...apps.googleusercontent.com","client_secret":"...",
   "refresh_token":"...","token_uri":"https://oauth2.googleapis.com/token",
   "scopes":["https://www.googleapis.com/auth/youtube.upload"]}
If you have it in a file, run:  python reauth_youtube.py --which main --in path\to\token.json
If you genuinely cannot find client_id/client_secret, tell Claude — we'll
download a fresh OAuth "Desktop app" client from Google Cloud Console instead.
"""

import argparse
import json
import sys
from pathlib import Path

# Windows consoles default to cp1252 and choke on any non-ASCII output.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Both scopes: upload videos AND manage captions/thumbnails (force-ssl).
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

SECRET_NAME = {
    "main": "YOUTUBE_CREDENTIALS",
}


def load_current_token(args) -> dict:
    if args.infile:
        raw = Path(args.infile).read_text(encoding="utf-8")
    else:
        print("\nPaste your CURRENT token JSON (the whole thing, one line),")
        print("then press Enter:\n")
        raw = sys.stdin.readline()
    raw = raw.strip()
    if not raw:
        sys.exit("[ERROR] No JSON provided. Re-run and paste the token JSON.")
    try:
        data = json.loads(raw)
    except Exception as e:
        sys.exit(f"[ERROR] That wasn't valid JSON: {e}")
    cid = data.get("client_id")
    csec = data.get("client_secret")
    if not cid or not csec:
        sys.exit("[ERROR] The token JSON has no client_id/client_secret. "
                 "Tell Claude - we'll make a fresh Desktop OAuth client instead.")
    return data


def main():
    ap = argparse.ArgumentParser(description="Re-auth a YouTube token with force-ssl")
    ap.add_argument("--which", choices=["main"], default="main",
                    help="which channel/token to re-auth")
    ap.add_argument("--in", dest="infile", default="",
                    help="path to your current token JSON (optional; else paste)")
    args = ap.parse_args()

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        sys.exit("[ERROR] Missing library. Run:  pip install google-auth-oauthlib")

    cur = load_current_token(args)
    client_config = {
        "installed": {
            "client_id": cur["client_id"],
            "client_secret": cur["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": cur.get("token_uri", "https://oauth2.googleapis.com/token"),
            "redirect_uris": ["http://localhost"],
        }
    }

    print(f"\n[AUTH] Re-authorising the {args.which.upper()} channel with force-ssl...")
    print("   A browser will open - pick the correct Google account and click Allow.\n")

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    # access_type=offline + prompt=consent guarantees a NEW refresh_token.
    try:
        creds = flow.run_local_server(port=0, access_type="offline",
                                      prompt="consent",
                                      authorization_prompt_message="")
    except Exception as e:
        sys.exit(
            f"\n[!] Browser sign-in didn't complete ({e}).\n"
            "   Make sure you finished 'Allow' in the browser, then just re-run\n"
            f"   the same command:  python reauth_youtube.py --which {args.which} --in cred_{args.which}.json\n"
            "   (If your browser didn't open at all, tell Claude - we'll use the\n"
            "   Google Cloud Console route instead.)")

    new_json = creds.to_json()
    out = Path("output")
    out.mkdir(exist_ok=True)
    out_path = out / f"new_token_{args.which}.json"
    out_path.write_text(new_json, encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"[SUCCESS] new token has scopes: {', '.join(creds.scopes or SCOPES)}")
    print("=" * 70)
    print(f"\n[COPY] Copy the JSON below into GitHub secret  ->  {SECRET_NAME[args.which]}")
    print("   (GitHub > Settings > Secrets and variables > Actions > Update)\n")
    print(new_json)
    print(f"\n[SAVED] Also saved to: {out_path}")
    print("   After updating the secret, delete that file (it contains a token).")


if __name__ == "__main__":
    main()
