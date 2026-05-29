"""
AI360 AUTO-HEAL — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Self-healing remediation loop. Runs every ~30 min. Finds failed GitHub
Actions jobs and AUTOMATICALLY re-runs them — most failures are transient
(API timeout, NSE/Telegram hiccup, runner blip) and pass on a retry. The
family never has to touch anything.

LOGIC (safe + bounded):
  • Look at workflow runs in the last RECENT_HOURS.
  • Group by workflow; only consider each workflow's MOST RECENT run — a stale
    failure that a later scheduled run already replaced is ignored (no wasted
    retries; this matters for frequent jobs like the trading bot).
  • If that latest run FAILED and has been retried fewer than MAX_ATTEMPTS
    times (run_attempt) → auto re-run its failed jobs.
  • If it already hit MAX_ATTEMPTS → STOP retrying and send ONE Telegram alert
    (this is a real problem a human must look at — see RUNBOOK.md).
  • Never re-runs the monitoring workflows themselves (auto-heal, watchdog,
    keepalive) to avoid loops.

Resolves errors "one by one, as early as possible" with zero human action,
and only escalates what it genuinely cannot fix. ₹0 (public repo).
"""

import os, json
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError

GH_TOKEN   = os.environ.get("GITHUB_TOKEN", "")
GH_REPO    = os.environ.get("GITHUB_REPOSITORY", "systronics/ai360trading")
TG_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_BASIC = os.environ.get("CHAT_ID_BASIC", "")

MAX_ATTEMPTS = 3      # original attempt + 2 auto-retries, then escalate
RECENT_HOURS = 6      # only look at recent runs

# Monitoring/infra workflows we must NOT auto-rerun (avoid loops / pointless retries)
SKIP_WORKFLOWS = {"System Watchdog — Daily Health Check",
                  "AI360 Auto-Heal",
                  "KeepAlive",
                  "pages-build-deployment"}


def _api(method, path):
    url = f"https://api.github.com{path}"
    req = Request(url, method=method, headers={
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai360-autoheal",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urlopen(req, timeout=25) as r:
        body = r.read().decode()
        return json.loads(body) if body.strip() else {}


def tg(msg):
    if not (TG_TOKEN and CHAT_BASIC):
        print("[TG] creds missing"); return
    try:
        req = Request(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                      data=json.dumps({"chat_id": CHAT_BASIC, "text": msg, "parse_mode": "HTML"}).encode(),
                      headers={"Content-Type": "application/json"})
        urlopen(req, timeout=15).read()
        print("[TG] escalation sent")
    except Exception as e:
        print(f"[TG] send failed: {e}")


def main():
    print(f"[AUTOHEAL] start {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC")
    if not GH_TOKEN:
        print("[AUTOHEAL] no GITHUB_TOKEN — cannot run"); return

    since = (datetime.now(timezone.utc) - timedelta(hours=RECENT_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        data = _api("GET", f"/repos/{GH_REPO}/actions/runs?per_page=100&created=%3E{since}")
    except Exception as e:
        print(f"[AUTOHEAL] list runs failed: {e}"); return

    # Keep only the most recent run per workflow
    latest = {}
    for run in data.get("workflow_runs", []):
        wid = run.get("workflow_id")
        if wid is None:
            continue
        if wid not in latest or run.get("created_at", "") > latest[wid].get("created_at", ""):
            latest[wid] = run

    retried, escalated, healthy = [], [], 0
    for run in latest.values():
        name    = run.get("name", "?")
        status  = run.get("status")
        concl   = run.get("conclusion")
        attempt = int(run.get("run_attempt", 1))
        run_id  = run.get("id")

        if name in SKIP_WORKFLOWS:
            continue
        if status != "completed":
            continue                      # still running — leave it alone
        if concl != "failure":
            healthy += 1; continue        # latest run is green/cancelled/skipped — fine

        if attempt < MAX_ATTEMPTS:
            try:
                _api("POST", f"/repos/{GH_REPO}/actions/runs/{run_id}/rerun-failed-jobs")
                retried.append(f"{name} (attempt {attempt+1}/{MAX_ATTEMPTS})")
                print(f"[AUTOHEAL] re-running {name} — attempt {attempt+1}")
            except HTTPError as e:
                # 403 = jobs no longer re-runnable, etc. — escalate
                print(f"[AUTOHEAL] rerun {name} failed: {e}")
                escalated.append(f"{name} (could not auto-retry)")
            except Exception as e:
                print(f"[AUTOHEAL] rerun {name} error: {e}")
        else:
            escalated.append(f"{name} (failed {attempt}× — auto-retry exhausted)")
            print(f"[AUTOHEAL] {name} exhausted {attempt} attempts — escalating")

    print(f"[AUTOHEAL] healthy={healthy} retried={len(retried)} escalated={len(escalated)}")

    if escalated:
        lines = "\n".join(f"  • {e}" for e in escalated)
        tg(f"\U0001F534 <b>AI360 Auto-Heal — needs you</b>\n"
           f"━━━━━━━━━━━━━━━━━━━━\n"
           f"I auto-retried these jobs but they still fail:\n{lines}\n\n"
           f"They likely need a small fix (see RUNBOOK.md → 'workflow red'). "
           f"The system stays SAFE meanwhile — no wrong trades.\n"
           f"<i>System message, not a trade signal.</i>")


if __name__ == "__main__":
    main()
