"""
collect_problem.py v1.0 (2026-11-15 NEW) - ONE-CLICK PROBLEM REPORT for the day no AI helper has the project in its head.
Collects, from GitHub (needs the `gh` CLI that is already logged in on the owner's PC), the recent FAILED runs and the last lines of their logs
into ONE text file `problem_report.txt` (a few KB) that the owner pastes into any AI together with AI_START_HERE.md.
Read-only: it changes nothing anywhere. Secrets are already masked (***) by GitHub in the logs.
USAGE:  python collect_problem.py              (last 3 days of failures)
        python collect_problem.py 7            (last 7 days)
        python collect_problem.py 3 tech-daily.yml   (also the last 3 runs of that one workflow, even if green)
"""
import datetime as dt
import json
import subprocess
import sys

REPO = "systronics/ai360trading"
NOISE = ("pages build and deployment", "pages-build-deployment", "CodeQL")
MAX_FAILS = 5
LOG_LINES = 45
LOG_CHARS = 3500


def gh(args, timeout=90):
    try:
        r = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return (r.stdout or "") + (("\n" + r.stderr) if r.returncode and r.stderr else "")
    except Exception as e:
        return f"(gh not available: {str(e)[:120]})"


def runs(extra, limit=100):
    out = gh(["run", "list", "--repo", REPO, "--limit", str(limit), "--json",
              "databaseId,name,conclusion,status,createdAt,event,workflowName,url"] + extra)
    try:
        return json.loads(out)
    except Exception:
        return []


def tail_failed_log(run_id):
    out = gh(["run", "view", str(run_id), "--repo", REPO, "--log-failed"], timeout=120)
    lines = [x for x in out.splitlines() if x.strip()]
    keep = [x.split("\t", 2)[-1][:240] for x in lines[-LOG_LINES:]]
    text = "\n".join(keep)
    return text[-LOG_CHARS:]


def main(argv):
    days = int(argv[0]) if argv and argv[0].isdigit() else 3
    one = argv[1] if len(argv) > 1 else ""
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).isoformat()
    out = [f"PROBLEM REPORT | {dt.datetime.now():%Y-%m-%d %H:%M} | last {days} day(s) | repo {REPO}",
           "Paste this whole text into the AI together with AI_START_HERE.md and say what you saw (e.g. 'no Good Morning message today')."]
    allr = runs([])
    bad = [r for r in allr if r.get("createdAt", "") >= since and r.get("conclusion") in ("failure", "timed_out")
           and not any(n.lower() in (r.get("name") or "").lower() for n in NOISE)]
    seen, picked = set(), []
    for r in bad:
        key = r.get("workflowName") or r.get("name")
        if key in seen:
            continue
        seen.add(key)
        picked.append(r)
    out.append("")
    out.append(f"== FAILED workflows (distinct, newest first): {len(picked)} of {len(bad)} failed runs")
    if not picked:
        out.append("(none failed in this period - check the schedule/kill switches instead; see AI_START_HERE.md 'Nothing arrived')")
    for r in picked[:MAX_FAILS]:
        out.append("")
        out.append(f"-- {r.get('workflowName') or r.get('name')} | {r.get('createdAt')} | {r.get('event')} | {r.get('conclusion')} | {r.get('url')}")
        out.append(tail_failed_log(r["databaseId"]))
    long_cancel = [r for r in allr if r.get("createdAt", "") >= since and r.get("conclusion") == "cancelled"
                   and not any(n.lower() in (r.get("name") or "").lower() for n in NOISE)]
    if long_cancel:
        names = sorted({(r.get("workflowName") or r.get("name")) for r in long_cancel})
        out.append("")
        out.append("== CANCELLED runs (usually harmless: a newer run replaced it; a session loop cancelled after ~4h = timeout): " + ", ".join(names[:12]))
    if one:
        out.append("")
        out.append(f"== Last 3 runs of {one}")
        for r in runs(["--workflow", one], limit=3):
            out.append(f"{r.get('createdAt')} | {r.get('event')} | {r.get('status')} | {r.get('conclusion')} | {r.get('url')}")
    out.append("")
    out.append("== Repo switches (variables)")
    out.append(gh(["variable", "list", "--repo", REPO]).strip()[:1800])
    text = "\n".join(out)
    with open("problem_report.txt", "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)
    print("\n[written to problem_report.txt - paste it into the AI]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
