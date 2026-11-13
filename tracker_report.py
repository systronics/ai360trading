"""
tracker_report.py v1.0 (2026-11-13 NEW) - ONE weekly plain-text summary of every observation tracker, sent to the PREMIUM Telegram chat (owner), so the evidence
can be read without any AI and without typing commands. Built for the period after the Claude plan ended (18 Nov 2026).
It only RUNS the existing read-only `--report` modes (signal_watch, result_watch, gainers_log, fetch_fo_buildup, swing_shadow, gate_audit, result_runup)
and forwards their last lines; it never writes to any sheet, never touches a gate/alert/ledger. Fail-open: a report that errors or times out is listed as 'not available'.
Rule printed in the message: fewer than 30 scored rows per group = NO conclusion; any rule change needs >= 4 weeks of data AND the owner's decision.
Mode env TRACKER_REPORT_MODE: dry (default, prints) | scheduled (sends to PREMIUM).   USAGE: python tracker_report.py
"""
import os
import subprocess
import sys
import datetime as dt

import requests

REPORTS = [
    ("SignalWatch (RSI>75 blocked vs normal, deep recovery, 1H, slot lost)", ["signal_watch.py", "--report"]),
    ("Result Watch hit-rate (lean vs real reaction)", ["result_watch.py", "--report"]),
    ("Top gainers log (what we missed)", ["gainers_log.py", "--report"]),
    ("Futures buildup labels", ["fetch_fo_buildup.py", "--report"]),
    ("Swing exits vs plain hold", ["swing_shadow.py", "--report"]),
    ("Gate audit (RS/trend/RSI pass vs blocked)", ["gate_audit.py", "--report"]),
    ("Result run-up paper list", ["result_runup.py", "--report"]),
]
PER_REPORT_LINES = 9
MAX_CHARS = 3800


def run_one(args, timeout=170):
    try:
        r = subprocess.run([sys.executable] + args, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        lines = [x.rstrip() for x in (r.stdout or "").splitlines() if x.strip() and not x.startswith(("[CAL]", "  📅"))]
        return lines[-PER_REPORT_LINES:] if lines else ["(no output)"]
    except Exception as e:                                       # fail-open
        return [f"(not available: {str(e)[:60]})"]


def run_health(days=7):
    """Read-only GitHub Actions health of the last `days` days: failures and 'cancelled at timeout' runs per workflow (a silent loop crash looks like 'cancelled', not 'failure')."""
    tok, repo = os.environ.get("GITHUB_TOKEN", ""), os.environ.get("GITHUB_REPOSITORY", "systronics/ai360trading")
    if not tok:
        return ["(no token - skipped)"]
    try:
        since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%d")
        bad, total, ok = {}, 0, 0
        for page in (1, 2, 3, 4, 5):
            r = requests.get(f"https://api.github.com/repos/{repo}/actions/runs", params={"per_page": 100, "page": page, "created": f">={since}"},
                             headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}, timeout=30)
            runs = (r.json() or {}).get("workflow_runs", [])
            if not runs:
                break
            for x in runs:
                total += 1
                c = x.get("conclusion")
                if c == "success":
                    ok += 1
                    continue
                if c not in ("failure", "timed_out", "cancelled"):
                    continue
                name = x.get("name", "?")
                if name in ("pages-build-deployment", "CodeQL"):
                    continue
                try:
                    a = dt.datetime.fromisoformat(x["run_started_at"].replace("Z", "+00:00"))
                    b = dt.datetime.fromisoformat(x["updated_at"].replace("Z", "+00:00"))
                    mins = (b - a).total_seconds() / 60
                except Exception:
                    mins = 0
                key = name + (" (cancelled after >3h = timeout)" if (c == "cancelled" and mins > 180) else (" (cancelled)" if c == "cancelled" else f" ({c})"))
                bad[key] = bad.get(key, 0) + 1
        lines = [f"{total} runs in {days} days, {ok} success"]
        for k, v in sorted(bad.items(), key=lambda kv: -kv[1])[:8]:
            lines.append(f"  {v}x {k}")
        return lines
    except Exception as e:
        return [f"(not available: {str(e)[:60]})"]


def build(today):
    out = [f"TRACKER REPORT | {today:%d-%b-%Y}",
           "Internal research status (paper, not advice). Fewer than 30 scored rows in a group = NO conclusion. "
           "Change a rule only after 4+ weeks of data AND your decision. Plan: review fully on/after 11-Dec-2026."]
    for title, args in REPORTS:
        out.append("")
        out.append(f"== {title}")
        out += run_one(args)
    text = "\n".join(out)
    return text if len(text) <= MAX_CHARS else text[:MAX_CHARS - 40] + "\n...(cut, run the report for the rest)"


def send(text):
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN", ""), os.environ.get("CHAT_ID_PREMIUM", "")
    if not (tok and chat):
        print("[TG] no token/chat - not sent")
        return False
    r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", data={"chat_id": chat, "text": text}, timeout=20)
    print(f"[TG] premium status {r.status_code}")
    return r.status_code == 200


def main():
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30))).date()
    text = build(today)
    print(text)
    if os.environ.get("TRACKER_REPORT_MODE", "dry").lower() == "scheduled":
        send(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
