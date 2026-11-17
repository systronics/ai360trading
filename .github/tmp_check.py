"""one-off read-only check (deleted after use): did the deployed appscript v15.46 run and relabel the option rows?"""
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
sh = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")
al = sh.worksheet("AlertLog").get_all_values()
print("ALERTLOG rows:")
for r in al[1:]:
    if len(r) > 22 and r[1]:
        print(" ", r[0], "|", r[1], "|", r[4], "|", r[5][:22], "|", r[10], "|", r[20], "|", r[21], "|", r[22])
print("DONE")
