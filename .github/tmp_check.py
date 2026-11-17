"""one-off read-only check (2026-11-17, deleted after use): PHOENIXLTD option call details + how the sheet marks RETEST candidates."""
import json
import os
from collections import Counter

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
sh = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")

n = sh.worksheet("Nifty200").get_all_values()
h = [x.strip() for x in n[0]]
print("NIFTY200 HEADERS:")
for i, x in enumerate(h):
    print(f"  {i}:{x}", end=" |")
print()
rows = [r for r in n[2:] if r and r[0]]
for i in (23,):
    print(f"col {i} ({h[i]}) sample:", [r[i] for r in rows[:5]])
# which columns hold a signal text / breakout stage?
for i, name in enumerate(h):
    if any(k in name.lower() for k in ("signal", "stage", "retest", "breakout", "setup")):
        c = Counter(r[i] for r in rows if len(r) > i and r[i] != "")
        print(f"COL {i} {name}: {dict(c.most_common(12))}")

print("--- PHOENIXLTD in Nifty200")
for r in rows:
    if r[0].replace("NSE:", "") == "PHOENIXLTD":
        print({h[i]: r[i] for i in range(min(len(h), len(r))) if r[i] not in ("", None)})

al = sh.worksheet("AlertLog").get_all_values()
print("--- ALERTLOG HEADER", al[0][:24])
for r in al[1:]:
    if len(r) > 5 and r[1].replace("NSE:", "") in ("PHOENIXLTD", "PNB"):
        print(r[:24])

for tab in ("OptionPaper",):
    try:
        v = sh.worksheet(tab).get_all_values()
        print(f"--- {tab} header:", v[0])
        for r in v[1:]:
            if "2026-11-17" in " ".join(r[:3]) or "PHOENIX" in " ".join(r[:6]).upper():
                print("  ", r[:24])
        print(f"  ({len(v) - 1} rows total)")
    except Exception as e:
        print(tab, "error", str(e)[:80])

hist = sh.worksheet("History").get_all_values()
print("--- HISTORY header:", hist[0])
for r in hist[1:]:
    if "PHOENIX" in " ".join(r[:3]).upper():
        print("  ", r[:19])
print("DONE")
