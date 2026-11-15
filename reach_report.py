"""
reach_report.py v1.0 (2026-11-15 NEW) - plain-text REACH summary from the data the daily growth snapshot already collects (`_data/video_stats.json`, `_data/growth_history.json`), so the
owner (and any AI helper) can see what actually gets views WITHOUT a developer. Read-only, no network, no tokens; fail-open (a missing/odd file = a short 'not available' line).
Printed in the Saturday Tracker report (tracker_report.py) and usable by hand:  python reach_report.py
It answers: views per channel in the last 14 days, the best and worst recent videos, for the tech channel which TOPIC GROUP (everyday device problem vs scam/security) does better,
and the follower trend (YouTube subs, Facebook, Instagram, Telegram members). Small samples are labelled: under 8 videos in a group = no conclusion.
"""
import json
import sys
from pathlib import Path

STATS = Path("_data/video_stats.json")
GROWTH = Path("_data/growth_history.json")
SECURITY_WORDS = ("scam", "hack", "virus", "otp", "fraud", "phishing", "link", "apk", "password", "privacy", "kyc", "lottery", "sim_block", "courier", "digital_arrest",
                  "spam", "antivirus", "two_step", "public_wifi", "wifi_chori", "gmail", "cookies", "incognito", "fake", "permission", "forgot_lock", "screen_share", "qr_")


def is_security(topic):
    t = (topic or "").lower()
    return any(w in t for w in SECURITY_WORDS)


def _load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def channel_lines(name, rows, days=14):
    recent = [r for r in rows if r.get("age_days", 999) <= days]
    old = [r for r in rows if 3 <= r.get("age_days", 0) <= 90]
    lines = [f"{name}: {len(recent)} videos in the last {days} days, {sum(r.get('views', 0) for r in recent)} views"]
    if old:
        vs = sorted(r.get("views", 0) for r in old)
        lines.append(f"  videos older than 3 days: {len(old)}, median {vs[len(vs) // 2]} views, best {vs[-1]}")
    best = sorted([r for r in rows if r.get("age_days", 0) >= 1], key=lambda r: -r.get("views_per_day", 0))[:3]
    for r in best:
        lines.append(f"  top: {r.get('views_per_day', 0)}/day ({r.get('views', 0)} views, {round(r.get('age_days', 0))}d) {r.get('title', '')[:60]}")
    return lines


def tech_groups(rows):
    """Everyday device problems vs scam/security topics, by average views per day of videos at least 1 day old."""
    g = {"device": [], "security": []}
    for r in rows:
        if r.get("age_days", 0) < 1 or not r.get("topic"):
            continue
        g["security" if is_security(r["topic"]) else "device"].append(r.get("views_per_day", 0))
    out = []
    for k, v in g.items():
        if v:
            out.append(f"  {k}: {len(v)} videos, average {round(sum(v) / len(v), 1)} views/day" + ("  (under 8 videos = no conclusion)" if len(v) < 8 else ""))
    return out


def trend_lines(rows):
    if not rows:
        return ["(no growth history)"]
    a, b = rows[0], rows[-1]
    keys = (("yt_subs", "YouTube subs"), ("fb_followers", "Facebook followers"), ("ig_followers", "Instagram followers"),
            ("tg_basic", "Telegram Basic"), ("tg_advance", "Telegram Advance"), ("tg_premium", "Telegram Premium"))
    out = [f"{a.get('date')} -> {b.get('date')}:"]
    for k, label in keys:
        if k in a and k in b:
            out.append(f"  {label}: {a[k]} -> {b[k]} ({b[k] - a[k]:+d})")
    return out


def build():
    out = ["REACH (from the daily snapshot; small numbers, read the trend not one day)"]
    st = _load(STATS)
    if not st or "channels" not in st:
        out.append("(video stats not available)")
    else:
        for name, v in st["channels"].items():
            rows = v.get("videos", []) if isinstance(v, dict) else v
            out += channel_lines(name, rows)
            if name == "tech":
                out.append("tech topic groups:")
                out += tech_groups(rows)
    gr = _load(GROWTH)
    out.append("Follower trend:")
    out += trend_lines((gr or {}).get("rows", []) if isinstance(gr, dict) else (gr or []))
    return out


def main():
    print("\n".join(build()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
