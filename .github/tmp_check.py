"""one-off (deleted after use): re-seed the option cells U-X of the PHOENIXLTD TRADED row that the old scan had wiped, then print the AlertLog option columns."""
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
sh = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")
ws = sh.worksheet("AlertLog")
al = ws.get_all_values()
for i, r in enumerate(al[1:], start=2):
    if len(r) > 10 and r[1].replace("NSE:", "") == "PHOENIXLTD" and "TRADED" in r[10].upper() and not (len(r) > 20 and r[20].strip()):
        ws.update(range_name=f"U{i}:X{i}", values=[["📊 BUY CE", "2200 CE Dec", "29-Dec-2026", "🟢 LOW (42d left)"]])
        print("seeded row", i)
al = ws.get_all_values()
for r in al[1:]:
    if len(r) > 22 and r[1]:
        print(" ", r[0][-8:], "|", r[1], "|", r[4], "|", r[10], "|", r[20], "|", r[21], "|", r[22])
print("DONE")
