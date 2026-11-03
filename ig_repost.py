"""ig_repost.py v1.0 (2026-11-03) — ONE-OFF/manual: post a Facebook Page Reel to the linked Instagram account only (no new video is made, no Facebook post).
Used when the Instagram step of the normal upload failed. It downloads the Reel's own video file from the Page (Graph `source`) and reuses
upload_facebook.upload_reel_to_instagram. Env: META_ACCESS_TOKEN, FB_VIDEO_ID, FACEBOOK_PAGE_ID_TECH, INSTAGRAM_ID_TECH. Never prints a token.
Usage: python ig_repost.py"""
import os
import sys
import tempfile
from pathlib import Path

import requests

import upload_facebook as U


def main():
    vid = os.environ.get("FB_VIDEO_ID", "").strip()
    pid = os.environ.get("FACEBOOK_PAGE_ID_TECH", "").strip()
    igid = os.environ.get("INSTAGRAM_ID_TECH", "").strip()
    if not (vid and pid and igid and U.META_ACCESS_TOKEN):
        print("missing FB_VIDEO_ID / FACEBOOK_PAGE_ID_TECH / INSTAGRAM_ID_TECH / META_ACCESS_TOKEN, nothing done")
        return 0
    tok = U.get_page_token(pid, U.META_ACCESS_TOKEN)
    r = requests.get(f"{U.GRAPH_BASE}/{vid}", params={"fields": "source,description,length", "access_token": tok}, timeout=30).json()
    if "error" in r or not r.get("source"):
        print("could not read the Reel source:", (r.get("error") or {}).get("message", "no source field"))
        return 0
    caption = r.get("description") or ""
    print(f"Reel length {r.get('length')}s, caption {len(caption)} chars")
    path = Path(tempfile.mkdtemp()) / "reel.mp4"
    with requests.get(r["source"], stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with open(path, "wb") as fh:
            for chunk in resp.iter_content(1 << 20):
                fh.write(chunk)
    print(f"downloaded {path.stat().st_size / 1e6:.1f} MB")
    out = U.upload_reel_to_instagram(igid, path, caption, tok)
    print("Instagram result:", out or "FAILED (see lines above)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
