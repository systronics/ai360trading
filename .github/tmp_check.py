"""one-off read-only check (2026-11-17, deleted after use): which F&O breakout-stage stocks are in a pullback (retest) today, and the FINAL_ACTION values."""
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
rows = [r for r in n[2:] if r and r[0]]
ix = {k: h.index(k) for k in ("FINAL_ACTION", "Breakout_Stage", "Retest %", "Trade_Type", "Priority_Score", "Options", "RS", "%Change", "Opt_Trend", "Opt_HV20", "%Distance_from_20_DMA", "%down_from_52W_UP")}
print("FINAL_ACTION values:", dict(Counter(r[ix["FINAL_ACTION"]] for r in rows).most_common(12)))
print("F&O rows:", sum(1 for r in rows if r[ix["Options"]] in ("N50", "YES")))
print("sym | stage | retest | final_action | trade_type | prio | RS | %chg | dist20DMA | optTrend | HV20")
for r in rows:
    if r[ix["Options"]] not in ("N50", "YES"):
        continue
    st = r[ix["Breakout_Stage"]]
    if "BREAKOUT" not in st and "Near" not in st:
        continue
    print(r[0].replace("NSE:", ""), "|", st, "|", r[ix["Retest %"]], "|", r[ix["FINAL_ACTION"]], "|", r[ix["Trade_Type"]], "|", r[ix["Priority_Score"]], "|", r[ix["RS"]], "|", r[ix["%Change"]], "|", r[ix["%Distance_from_20_DMA"]], "|", r[ix["Opt_Trend"]], "|", r[ix["Opt_HV20"]])
print("DONE")
