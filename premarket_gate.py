"""
premarket_gate.py v1.0 (2026-11-10) - decides whether the pre-market brief workflow should run today, and records that it was posted.
Run:  python premarket_gate.py            -> writes run=yes|no to $GITHUB_OUTPUT (and prints why)
      python premarket_gate.py --mark-done -> writes _data/premarket_done.json {"date": today IST}
Rules (all fail-open to RUN except 'already posted' and 'too late', which are the whole point of the gate):
  * not a trading day (NSE holiday / weekend per indian_holidays.py) -> no
  * after 09:10 IST -> no (a pre-market brief after the open is useless)
  * mode == scheduled and _data/premarket_done.json already has today's date -> no (never post twice)
  * env FORCE=yes (manual tests only) skips ALL rules, holiday included.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

DONE = "_data/premarket_done.json"


def ist_now(now_utc=None):
    return (now_utc or datetime.now(timezone.utc)) + timedelta(hours=5, minutes=30)


def decide(now_ist, mode, force, done_date, is_non_market_day):
    """(run: bool, why: str). Pure."""
    if force:                                   # manual test runs only (workflow_dispatch input force=yes) - never set by the schedule or the bot kick
        return True, "forced"
    if is_non_market_day:
        return False, "not a trading day"
    if (now_ist.hour, now_ist.minute) > (9, 10):
        return False, "after 09:10 IST (a pre-market brief no longer makes sense)"
    if mode == "scheduled" and done_date == now_ist.date().isoformat():
        return False, "already posted today"
    return True, "ok"


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    now = ist_now()
    if "--mark-done" in argv:
        os.makedirs("_data", exist_ok=True)
        with open(DONE, "w", encoding="utf-8") as f:
            json.dump({"date": now.date().isoformat()}, f)
        print("[GATE] marked done", now.date().isoformat())
        return 0
    non_market = False
    try:
        import indian_holidays as H
        non_market = bool(H.is_non_market_day())          # takes no argument: it checks today's date in IST itself
    except Exception as e:
        print("[GATE] holiday check failed, continuing:", str(e)[:80])
    try:
        done_date = json.load(open(DONE, encoding="utf-8")).get("date")
    except Exception:
        done_date = None
    run, why = decide(now, os.environ.get("MODE", "dry"), os.environ.get("FORCE") == "yes", done_date, non_market)
    print("[GATE]", "RUN" if run else "SKIP", "-", why)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write("run=" + ("yes" if run else "no") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
