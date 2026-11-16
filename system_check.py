"""system_check.py - one-off read-only sheet health check (2026-11-16). Prints counts / freshness only (no tokens, no secrets)."""
import json
import os
import datetime as dt

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
sh = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")
tot = 0
for ws in sh.worksheets():
    tot += ws.row_count * ws.col_count
    print(f"TAB {ws.title:22s} rows {ws.row_count:6d} cols {ws.col_count:3d}")
print("TOTAL CELLS", tot, f"({tot / 10_000_000 * 100:.1f}% of the 10M limit)")

n = sh.worksheet("Nifty200").get_all_values()
h = [x.strip() for x in n[0]]


def col(name):
    return h.index(name) if name in h else -1


print("NIFTY200 rows", len(n) - 2, "| header has Opt_Trend/Opt_ADX/Opt_HV20:", [col(x) >= 0 for x in ("Opt_Trend", "Opt_ADX", "Opt_HV20")])
r2 = n[1]
print("NIFTY row2:", r2[:6])
for nm in ("Opt_Trend", "Opt_HV20", "Opt_ADX"):
    c = col(nm)
    if c >= 0:
        vals = [r[c] for r in n[2:] if len(r) > c and r[0]]
        filled = [v for v in vals if v not in ("", None)]
        print(f"  {nm}: filled {len(filled)}/{len(vals)}", ("OK=%d NO=%d" % (filled.count("OK"), filled.count("NO"))) if nm == "Opt_Trend" else "")
cmp_i = next((i for i, x in enumerate(h) if "CMP" in x.upper() or x.upper().startswith("PRICE")), None)
print("  CMP col index", cmp_i, "blank CMP count", sum(1 for r in n[2:] if r and r[0] and (len(r) <= (cmp_i or 0) or r[cmp_i] in ("", "#N/A", "N/A"))) if cmp_i is not None else "")

a = sh.worksheet("AlertLog").get_all_values()
print("ALERTLOG rows", len(a) - 1, "| T2 master switch:", a[1][19] if len(a) > 1 and len(a[1]) > 19 else "?")
st = {}
for r in a[1:]:
    if len(r) > 10 and r[1]:
        st[r[10]] = st.get(r[10], 0) + 1
print("  status counts:", st)
times = [r[0] for r in a[1:] if r and r[0]]
print("  latest signal times:", sorted(times)[-3:] if times else None)

hist = sh.worksheet("History").get_all_values()
print("HISTORY rows", len(hist) - 1, "| last row exit-date col sample:", hist[-1][:3] if len(hist) > 1 else None)

bm = sh.worksheet("BotMemory").get_all_values()
print("BOTMEMORY rows", len(bm) - 1)
keys = {r[0]: (r[1] if len(r) > 1 else "") for r in bm[1:] if r}
for k in ("MKT_PCR_NIFTY", "MKT_FII_REGIME", "MKT_FII_DATE"):
    print("  ", k, "=", keys.get(k, "(missing)"))
print("  EARNINGS_ keys:", sum(1 for k in keys if k.startswith("EARNINGS_")), "| DLV_ keys:", sum(1 for k in keys if k.startswith("DLV_")))
print("CHECK DONE", dt.datetime.utcnow().isoformat(timespec="seconds"), "UTC")
