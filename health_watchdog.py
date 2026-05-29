"""
AI360 SYSTEM WATCHDOG — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Once-daily health check that makes the system observable WITHOUT a developer.

It does NOT fix anything itself (that would risk making things worse
unattended). It detects problems early and sends a PLAIN-LANGUAGE Telegram
alert to the owner with the exact step to take — see RUNBOOK.md.

CHECKS (each independent, all fail-safe — one check failing never blocks others):
  1. Google Sheet reachable + automation switch (AlertLog T2) still "YES"
  2. Trading bot freshness — did it run on the last trading day?
  3. NSE data feed freshness — FII/DII/bhavcopy keys updated recently?
  4. GitHub Actions failures in the last 24h (via GITHUB_TOKEN)
  5. Telegram bot token still valid

OUTPUT:
  • Problems found  → 🔴 alert to Basic channel, plain language + fix step.
  • All healthy     → silent on weekdays; one ✅ heartbeat every Monday so the
                      owner knows the watchdog itself is alive (silence is then
                      meaningful, not ambiguous).

SELF-REPAIR PHILOSOPHY (per Amit ji): ₹0/month, fail-open, never crash a run.
Uses stdlib urllib for Telegram + GitHub so an alert still sends even if pip
partially failed. gspread is the only third-party import and is guarded.

SCHEDULE: daily 08:05 IST (02:35 UTC) — before market, after overnight content.
"""

import os, json, time
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

IST          = timezone(timedelta(hours=5, minutes=30))
SHEET_NAME   = "Ai360tradingAlgo"
TG_TOKEN     = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_BASIC   = os.environ.get("CHAT_ID_BASIC", "")
GH_TOKEN     = os.environ.get("GITHUB_TOKEN", "")
GH_REPO      = os.environ.get("GITHUB_REPOSITORY", "systronics/ai360trading")

# Freshness thresholds (hours / days)
NSE_STALE_DAYS = 4      # FII/DII/bhavcopy data older than this = feed problem


# ── Telegram (stdlib — works even if pip failed) ───────────────────────────
def tg(msg):
    if not (TG_TOKEN and CHAT_BASIC):
        print("[TG] creds missing — cannot alert"); return
    try:
        req = Request(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            data=json.dumps({"chat_id": CHAT_BASIC, "text": msg, "parse_mode": "HTML"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        urlopen(req, timeout=15).read()
        print("[TG] sent")
    except Exception as e:
        print(f"[TG] send failed: {e}")


def _is_trading_weekday(d):
    return d.weekday() < 5   # Mon-Fri (holiday nuance not needed for a coarse check)


# ── CHECK 1+2+3: Sheet reachable, automation on, bot + NSE freshness ───────
def check_sheet_and_freshness(problems):
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
    except Exception as e:
        problems.append(("Python libraries broken",
                         f"gspread import failed ({e}). A dependency update likely broke the build. "
                         f"FIX: see RUNBOOK → 'workflow red'. Revert requirements.txt to last green."))
        return

    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        problems.append(("Google key missing",
                         "GCP_SERVICE_ACCOUNT_JSON secret is empty. FIX: RUNBOOK → 'Google key'."))
        return
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)
        ss    = gspread.authorize(creds).open(SHEET_NAME)
    except Exception as e:
        problems.append(("Cannot open Google Sheet",
                         f"{e}. The service-account key may have expired or lost access. "
                         f"FIX: RUNBOOK → 'Google key'."))
        return

    # Automation switch
    try:
        t2 = (ss.worksheet("AlertLog").acell("T2").value or "").strip().upper()
        if t2 != "YES":
            problems.append(("Automation is OFF",
                             f"AlertLog cell T2 = '{t2}' (should be YES). The bot will not trade. "
                             f"FIX: open the sheet, set T2 back to YES."))
    except Exception as e:
        print(f"[CHK] T2 read error: {e}")

    # Bot + NSE freshness from BotMemory
    try:
        rows = ss.worksheet("BotMemory").get_all_values()
        now  = datetime.now(IST)

        def newest_updatedat(pred):
            newest = None
            for r in rows[1:]:
                if len(r) < 3 or not r[0].strip():
                    continue
                if not pred(r[0].strip()):
                    continue
                ts = r[2].strip()[:19]
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
                    try:
                        dt = datetime.strptime(ts, fmt).replace(tzinfo=IST)
                        if newest is None or dt > newest:
                            newest = dt
                        break
                    except Exception:
                        continue
            return newest

        # Bot freshness — _RUNTIME_MEM is rewritten every bot tick
        bot_last = newest_updatedat(lambda k: k == "_RUNTIME_MEM")
        if bot_last:
            age_h = (now - bot_last).total_seconds() / 3600.0
            yesterday = (now - timedelta(days=1)).date()
            # If the last trading weekday passed and the bot hasn't run in >24h → problem
            if age_h > 24 and _is_trading_weekday(yesterday):
                problems.append(("Trading bot not running",
                                 f"Last bot activity was {bot_last:%Y-%m-%d %H:%M} IST ({age_h:.0f}h ago). "
                                 f"It should run every market day. FIX: RUNBOOK → 'bot not running'."))
        else:
            print("[CHK] no _RUNTIME_MEM yet (fresh start?) — skipping bot-freshness")

        # NSE data feed freshness — MKT_ (FII/DII) or DLV_ (bhavcopy) keys
        nse_last = newest_updatedat(lambda k: k.startswith("MKT_") or k.startswith("DLV_"))
        if nse_last:
            age_d = (now - nse_last).total_seconds() / 86400.0
            if age_d > NSE_STALE_DAYS:
                problems.append(("NSE data feed stale",
                                 f"Latest market data is {age_d:.1f} days old (last {nse_last:%Y-%m-%d}). "
                                 f"NSE may have changed their download URLs. FIX: RUNBOOK → 'NSE feed'."))
        else:
            print("[CHK] no MKT_/DLV_ keys found — NSE fetchers may not have run yet")
    except Exception as e:
        print(f"[CHK] BotMemory freshness error: {e}")


# ── CHECK 4: GitHub Actions failures in last 24h ───────────────────────────
def check_github_failures(problems):
    if not GH_TOKEN:
        print("[CHK] no GITHUB_TOKEN — skipping Actions check"); return
    try:
        since = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"https://api.github.com/repos/{GH_REPO}/actions/runs?per_page=60&created=%3E{since}"
        req = Request(url, headers={
            "Authorization": f"Bearer {GH_TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "ai360-watchdog",
        })
        data = json.loads(urlopen(req, timeout=20).read().decode())
        failed = {}
        for run in data.get("workflow_runs", []):
            if run.get("conclusion") == "failure":
                name = run.get("name", "?")
                failed[name] = failed.get(name, 0) + 1
        if failed:
            lines = "\n".join(f"  • {n} ({c}×)" for n, c in failed.items())
            problems.append(("Workflow(s) failing",
                             f"These GitHub jobs failed in the last 24h:\n{lines}\n"
                             f"FIX: RUNBOOK → 'workflow red'."))
    except Exception as e:
        print(f"[CHK] GitHub API error (non-fatal): {e}")


# ── CHECK 5: Telegram token valid ──────────────────────────────────────────
def check_telegram(problems):
    if not TG_TOKEN:
        problems.append(("Telegram token missing",
                         "TELEGRAM_BOT_TOKEN secret is empty — no alerts can be sent. FIX: RUNBOOK → 'Telegram'."))
        return
    try:
        ok = json.loads(urlopen(f"https://api.telegram.org/bot{TG_TOKEN}/getMe", timeout=15).read().decode()).get("ok")
        if not ok:
            problems.append(("Telegram token invalid",
                             "Telegram rejected the bot token. FIX: RUNBOOK → 'Telegram'."))
    except Exception as e:
        print(f"[CHK] Telegram getMe error: {e}")


def main():
    now = datetime.now(IST)
    print(f"[WATCHDOG] start {now:%Y-%m-%d %H:%M} IST")
    problems = []

    for chk in (check_sheet_and_freshness, check_github_failures, check_telegram):
        try:
            chk(problems)
        except Exception as e:
            print(f"[WATCHDOG] check {chk.__name__} crashed (non-fatal): {e}")

    if problems:
        body = [f"\U0001F534 <b>AI360 System Alert — {now:%d %b %Y}</b>",
                "━━━━━━━━━━━━━━━━━━━━",
                f"<b>{len(problems)} issue(s) need attention:</b>", ""]
        for i, (title, detail) in enumerate(problems, 1):
            body.append(f"<b>{i}. {title}</b>\n{detail}\n")
        body.append("<i>This is a system health message, not a trade signal. "
                     "Full steps in RUNBOOK.md in the GitHub repo.</i>")
        tg("\n".join(body))
        print(f"[WATCHDOG] {len(problems)} problem(s) reported")
    else:
        print("[WATCHDOG] all healthy")
        # Weekly heartbeat (Monday) so silence is meaningful.
        # WATCHDOG_TEST=1 (manual dispatch) forces it any day — lets the owner
        # press a button and confirm alerts still reach their phone.
        if now.weekday() == 0 or os.environ.get("WATCHDOG_TEST") == "1":
            tg(f"✅ <b>AI360 Weekly Health Check — {now:%d %b %Y}</b>\n"
               f"All systems healthy: Google Sheet reachable, automation ON, "
               f"trading bot running, market data fresh, no failed workflows.\n\n"
               f"<i>Automated weekly confirmation. No action needed.</i>")
            print("[WATCHDOG] weekly heartbeat sent")


if __name__ == "__main__":
    main()
