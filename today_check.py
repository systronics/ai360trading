"""today_check.py - one-off read-only check (2026-11-17): today's top Nifty200 gainers vs what the system did (ScanReasons / AlertLog / option alerts). Prints stock symbols and numbers only."""
import json
import os
import datetime as dt

import gspread
import pytz
from oauth2client.service_account import ServiceAccountCredentials

IST = pytz.timezone("Asia/Kolkata")
today = dt.datetime.now(IST).date().isoformat()
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
sh = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")
print("TODAY", today)

n = sh.worksheet("Nifty200").get_all_values()
h = [x.strip() for x in n[0]]
print("HEAD", h[:6], "...", h[35] if len(h) > 35 else "")
rows = []
for r in n[2:]:
    if not r or not r[0]:
        continue
    try:
        pct = float(str(r[3]).replace("%", "").replace(",", ""))
    except Exception:
        continue
    opt = r[35] if len(r) > 35 else ""
    rows.append((pct, r[0].replace("NSE:", ""), r[2], opt))
rows.sort(reverse=True)
top = rows[:15]
print("NIFTY row:", n[1][:4])

sr = {}
try:
    for r in sh.worksheet("ScanReasons").get_all_values()[1:]:
        if len(r) > 3:
            sr[r[1].replace("NSE:", "").strip()] = (r[0], r[2][:50], r[3][:90])
except Exception as e:
    print("ScanReasons error", str(e)[:80])

al = sh.worksheet("AlertLog").get_all_values()
alog = {}
for r in al[1:]:
    if len(r) > 22 and r[1]:
        alog[r[1].replace("NSE:", "").strip()] = (r[4], r[10], r[20], r[21], r[22])

print("--- TOP 15 GAINERS TODAY (Nifty200 sheet, live %Change)")
for pct, s, cmp_, opt in top:
    a = alog.get(s)
    q = sr.get(s)
    print(f"{s:12s} {pct:+6.2f}%  F&O:{opt or '-':4s} | AlertLog: {a[0] + ' / ' + a[1] if a else 'not queued'} | scan: {q[2] if q else 'no row'}")

print("--- ALERTLOG option rows (all)")
for s, a in alog.items():
    if "options alert" in a[0].lower():
        print(f"{s:12s} {a[0]} | {a[1]} | signal {a[2]} | {a[3]} | {a[4]}")

bm = sh.worksheet("BotMemory").get_all_values()
keys = [r[0] for r in bm[1:] if r and r[0]]
opt_flags = sorted(k for k in keys if k.startswith(today) and "_OPT_" in k)
print("--- OPTION ALERT FLAGS sent today (Premium OPTIONS SIGNAL):", opt_flags or "none")
ent = sorted(k for k in keys if today in k and ("_ENTRY_" in k or "_CASH_" in k))
print("--- ENTRY/CASH flags today:", ent[:20] or "none")

hist = sh.worksheet("History").get_all_values()
print("--- HISTORY last 5 rows (symbol | cols 1-4)")
for r in hist[-5:]:
    print(" ", r[:5])
print("DONE")
