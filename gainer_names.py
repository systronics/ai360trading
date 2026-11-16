"""gainer_names.py - one-off read-only helper (2026-11-17): which F&O/Nifty200 stocks appear most often among the daily top-15 gainers in the GainersLog tab.
Used to pick the 30 symbols of the TradingView gainers dashboard so it covers the stocks most likely to be the day's top gainers. Prints symbols + counts only."""
import json
import os
from collections import Counter

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
sh = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")
v = sh.worksheet("GainersLog").get_all_values()
h = v[0]
i_d, i_s, i_r = h.index("Date"), h.index("Symbol"), h.index("Rank")
days = sorted({r[i_d] for r in v[1:] if r and r[i_d]})
c = Counter(r[i_s] for r in v[1:] if len(r) > i_s and r[i_s])
print("days", len(days), days[0], days[-1], "rows", len(v) - 1, "distinct symbols", len(c))
print("TOP", ",".join(f"{s}:{n}" for s, n in c.most_common(60)))
