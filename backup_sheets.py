"""
backup_sheets.py v1.0 (2026-11-06) - daily CSV copy of EVERY tab of the Ai360tradingAlgo Google Sheet, so a corrupted/deleted sheet can be rebuilt.
Writes <out_dir>/<tab>.csv (raw values as stored; formulas are not exported, their results are). Read-only on the sheet. The workflow commits the folder
to the PRIVATE repo systronics/ai360trading-backup (never this public repo - the sheet holds trade data). Fail-loud: any tab that cannot be read exits 1 so the run shows red.
USAGE: python backup_sheets.py <out_dir>
"""
import csv
import json
import os
import re
import sys
import time


def main(out):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
    sh = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")
    os.makedirs(out, exist_ok=True)
    bad, total = [], 0
    for ws in sh.worksheets():
        name = re.sub(r"[^A-Za-z0-9_.-]+", "_", ws.title)
        for attempt in range(4):
            try:
                rows = ws.get_all_values()
                break
            except Exception as e:
                rows = None
                time.sleep(20 * (attempt + 1))
        if rows is None:
            bad.append(ws.title)
            continue
        with open(os.path.join(out, name + ".csv"), "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(rows)
        total += len(rows)
        print(f"[BACKUP] {ws.title}: {len(rows)} rows")
        time.sleep(1.2)
    print(f"[BACKUP] {len(sh.worksheets()) - len(bad)} tabs, {total} rows, failed: {bad or 'none'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "backup_out"))
