"""one-off final read-only health check (2026-11-17, deleted after use): option cells, shadow log, sheet size, scan freshness."""
import json
import os
import datetime as dt
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials

IST = pytz.timezone("Asia/Kolkata")
today = dt.datetime.now(IST).date().isoformat()
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
sh = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")
tot = 0
big = []
for ws in sh.worksheets():
    c = ws.row_count * ws.col_count
    tot += c
    big.append((c, ws.title, ws.row_count, ws.col_count))
big.sort(reverse=True)
print(f"TOTAL CELLS {tot} = {tot / 10_000_000 * 100:.1f}% of the 10M limit | tabs {len(big)}")
print("BIGGEST:", [(t, r, c) for _, t, r, c in big[:5]])

al = sh.worksheet("AlertLog").get_all_values()
print("ALERTLOG T2:", al[1][19] if len(al) > 1 and len(al[1]) > 19 else "?", "| rows", len(al) - 1)
times = sorted(r[0] for r in al[1:] if r and r[0])
print("  newest scan time:", times[-1] if times else None)
for r in al[1:]:
    if len(r) > 22 and r[1]:
        print("  ", r[1], "|", r[4], "|", r[10], "|", r[20], "|", r[21], "|", r[22])

bm = sh.worksheet("BotMemory").get_all_values()
keys = [r[0] for r in bm[1:] if r and r[0]]
print("BOTMEMORY filled rows:", len(keys), "| grid", len(bm))
print("  OPTSHADOW keys today:", sorted(k for k in keys if k.startswith(today + "_OPTSHADOW_")) or "none yet")
print("  OPT alert flags today:", sorted(k for k in keys if k.startswith(today + "_OPT_") and "SHADOW" not in k) or "none")
print("  OPT_RETEST_OFF switch row present:", "OPT_RETEST_OFF" in keys)

for tab in ("OptionPaper", "SignalWatch", "OptionWatch", "OptionSnap"):
    try:
        v = sh.worksheet(tab).get_all_values()
        extra = ""
        if tab == "SignalWatch":
            from collections import Counter
            extra = dict(Counter(r[3] for r in v[1:] if len(r) > 3 and r[3].startswith("OPT")))
        print(f"{tab}: {len(v) - 1} rows {extra}")
    except Exception as e:
        print(tab, "error", str(e)[:60])

n = sh.worksheet("Nifty200").get_all_values()
print("NIFTY row:", n[1][:4], "| Opt_Trend/HV20 filled:", sum(1 for r in n[2:] if r and r[0] and len(r) > 49 and r[49] not in ("",)), "(approx)")
print("DONE", dt.datetime.now(IST).strftime("%H:%M IST"))
