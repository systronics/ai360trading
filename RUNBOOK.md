# 🛟 AI360Trading — Family Runbook (No-Developer Guide)

**For:** Amit ji and family — to keep the system running if no developer is available.
**Golden rule:** The system is built to **fail safe**. If something breaks, it stops sending signals/posts — it will **not** lose money (paper trading) or do anything harmful. So **don't panic**. Most issues wait safely until fixed.

You will get a Telegram message on the **Basic channel** when something needs attention. It always starts with 🔴 **AI360 System Alert**. Every Monday you also get a ✅ **Weekly Health Check** — that just means "all good, nothing to do."

> If you ever get **no** Monday ✅ message for 2 weeks in a row, the watchdog itself may be off — see issue **G** below.

---

## How to do the 3 basic things (you'll need these below)

**A) Open the Google Sheet**
- Open the bookmark to the **Ai360tradingAlgo** Google Sheet (or Google Drive → it's there).
- The important tab is **AlertLog**.

**B) Turn automation ON/OFF (cell T2)**
- In the **AlertLog** tab, click cell **T2** (column "SYSTEM CONTROL", row 2).
- Type **YES** to turn the bot ON. Type **NO** to pause it. Press Enter.

**C) Re-run / check a GitHub job**
- Open the bookmark to **GitHub → Actions** (github.com/systronics/ai360trading/actions).
- A **green ✓** = working. A **red ✗** = failed.
- To run one again: click the workflow name on the left → button **"Run workflow"** → **Run**.

---

## What each alert means and what to do

The alert tells you the issue title. Find it below.

### 1. "Automation is OFF"
- **Meaning:** Cell **T2** is not "YES", so the bot is paused.
- **Fix (you can do this):** Do step **B** above → set **T2 = YES**. Done.

### 2. "Trading bot not running"
- **Meaning:** The bot didn't run on the last market day.
- **Fix (you can try):** Do step **C** → open Actions → check **"Trading Bot — Market Session Loop"** and **"Trading Bot — Signal Monitor"**.
  - If you see red ✗ → click it → if it says a clear reason you understand (rare), fix it; otherwise this needs a developer.
  - Quick safe try: click **"Run workflow"** on "Trading Bot — Signal Monitor". If it turns green ✓, it's working again.
- **If still red:** needs a developer. The system stays safe meanwhile (no wrong trades).

### 3. "NSE data feed stale"
- **Meaning:** The free NSE website probably changed how it shares data, so market data stopped updating. This needs a small code change.
- **What you can do:** Nothing to fix yourself — but **it's safe**. The bot simply won't take new trades on stale data.
- **What to tell a developer:** *"NSE bhavcopy / FII-DII download URL likely changed — update `fetch_bhavcopy.py` and `fetch_fii_dii.py` to the new NSE URL format."*

### 4. "Workflow(s) failing"
- **Meaning:** One of the automated jobs failed in the last 24 hours. The alert lists which one(s).
- **Fix (you can try):** Do step **C** → open the failing job → **"Run workflow"** once. Many failures are temporary (internet/API hiccup) and pass on retry.
- **If it keeps failing for 2+ days:** needs a developer. Tell them the **exact workflow name** from the alert.

### 5. "Python libraries broken" / build errors
- **Meaning:** An automatic software update broke the code.
- **What to tell a developer:** *"A dependency broke the build — `requirements.txt` is pinned; revert to the last known-good version and re-run."* (The file already lists the exact working versions, so this is a quick fix for them.)
- **Safe meanwhile:** yes — jobs just fail without doing harm.

### 6. "Google key missing" / "Cannot open Google Sheet"
- **Meaning:** The secret key that lets the system read/write the Google Sheet expired or lost access.
- **What to tell a developer:** *"The Google service-account key (GitHub secret `GCP_SERVICE_ACCOUNT_JSON`) needs renewing, and the Sheet must be shared with the service-account email again."*

### 7. "Telegram token missing/invalid"
- **Meaning:** The Telegram bot key is wrong — alerts/signals can't be sent.
- **What to tell a developer:** *"Regenerate the Telegram bot token via @BotFather and update the GitHub secret `TELEGRAM_BOT_TOKEN`."*

### F. Facebook / Instagram stopped posting
- **Meaning:** Social media access tokens expire every ~2 months. This is the most common recurring task.
- **What happens:** Trading signals are **unaffected**. Only auto-posting to FB/Instagram pauses.
- **What to tell a developer:** *"Refresh the Meta (Facebook/Instagram) long-lived access token and update the GitHub secret. Check `publish_to_groups` scope for the FB group."*

### H. "GitHub access token (GH_TOKEN) expiring soon / invalid"
- **Meaning:** A GitHub password-key (called `GH_TOKEN`) is used to (1) auto-refresh the Facebook/Instagram token and (2) auto-restart failed jobs. If it expires, FB/Instagram posting will stop in a few weeks and auto-repair will stop. You get this alert **~3 weeks early** so there's plenty of time.
- **What's safe:** Trading signals are **unaffected**. Nothing breaks immediately.
- **Fix (best done with whoever set it up, ~5 min):**
  1. Go to **GitHub → top-right photo → Settings → Developer settings → Personal access tokens**.
  2. Find the token used for this repo, **regenerate** it — and set **Expiration = No expiration** (so this never happens again).
  3. Copy the new token, then go to the repo → **Settings → Secrets and variables → Actions → `GH_TOKEN` → Update** → paste → Save.
- **If unsure:** hand this section to a developer — it's a quick, well-known task.

### G. No weekly ✅ message for 2 weeks
- **Meaning:** The watchdog itself may have stopped (GitHub disables jobs after long inactivity, though KeepAlive should prevent this).
- **Fix (you can try):** Do step **C** → open **"System Watchdog — Daily Health Check"** → **"Run workflow"** with **test_alert = true**. If you get a ✅ message, it's alive again.

---

## Test that alerts still reach you (do this anytime)
- Step **C** → **"System Watchdog — Daily Health Check"** → **Run workflow** → set **test_alert** = **true** → Run.
- Within ~2 minutes you should get a ✅ message on Telegram. If yes, the safety net works.

---

## What is fully automatic (you never touch these)
- Daily trading signals, monitoring, exits (market days).
- Daily content: articles, reels, shorts, education + kids videos, YouTube/Facebook posting.
- Yearly NSE holiday refresh (every December).
- Token refresh attempts (1st & 15th monthly).
- Weekly health check + problem alerts (this runbook).

## Money & cost
- **₹0/month forever** — everything uses free tiers (public GitHub repo = free).
- **Paper trading only** — no real money is at risk in the current phase.

---
*Keep this file. If you hire any developer, give them this repo + `.internal-ops.md` (full technical doc) + `SESSION.md` (current state).*
