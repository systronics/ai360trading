"""
inspect_nifty200.py — One-time diagnostic script
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Tell us where the FII data in the Nifty200 tab is coming from.

Reads Google Sheet "Ai360tradingAlgo" → Nifty200 tab → prints the FORMULA
(not the displayed value) in columns:
  P  (FII_Buy_Zone)
  Q  (FII_Rating)
  R  (Leader_Type)
  AG (FII_Signal)

For rows 2-4 — gives a small sample so we can see the pattern.

Run on PC:
    python inspect_nifty200.py

Then paste the output back to Claude.

Read-only. Does not modify the sheet.
"""

import os, json, sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_NAME = "Ai360tradingAlgo"
TAB_NAME   = "Nifty200"

# Columns of interest (1-based for gspread)
COLS = {
    "A":  1,    # NSE_SYMBOL (for identifying the row)
    "P":  16,   # FII_Buy_Zone
    "Q":  17,   # FII_Rating
    "R":  18,   # Leader_Type
    "AG": 33,   # FII_Signal
}


def _connect():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        try:
            with open("service_account.json") as f:
                raw = f.read().strip()
        except FileNotFoundError:
            raise SystemExit("[CREDS] GCP_SERVICE_ACCOUNT_JSON env var not set "
                             "and service_account.json not found locally.\n"
                             "Set the env var or place service_account.json in this folder.")
    try:
        creds_dict = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"[CREDS] Failed to parse credentials JSON: {e}")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    gc    = gspread.authorize(creds)
    return gc.open(SHEET_NAME)


def main():
    print("=" * 70)
    print(" Nifty200 FII columns — formula vs displayed value inspector")
    print("=" * 70)

    wb = _connect()
    try:
        ws = wb.worksheet(TAB_NAME)
    except gspread.WorksheetNotFound:
        print(f"❌ Tab '{TAB_NAME}' not found in '{SHEET_NAME}'")
        sys.exit(1)

    print(f"\n📊 Opened: {SHEET_NAME} → {TAB_NAME}")

    # Headers (row 1)
    print("\n── HEADERS (row 1) ──")
    for label, col_num in COLS.items():
        try:
            header = ws.cell(1, col_num).value or "(empty)"
            print(f"  Column {label:>2} (col {col_num:>2}): header = '{header}'")
        except Exception as e:
            print(f"  Column {label}: header read error — {e}")

    # For rows 2, 3, 4 — read FORMULA and VALUE for each FII column
    for row in (2, 3, 4):
        print(f"\n── ROW {row} ──")
        try:
            symbol = ws.cell(row, COLS["A"]).value or "(blank)"
            print(f"  Symbol (col A): {symbol}")
        except Exception as e:
            print(f"  Symbol read error: {e}")

        for label, col_num in COLS.items():
            if label == "A":
                continue
            try:
                # gspread API: value_render_option=FORMULA returns the raw formula
                formula = ws.cell(row, col_num, value_render_option="FORMULA").value
                # Default render returns the computed/displayed value
                display = ws.cell(row, col_num).value
                print(f"  Col {label:>2} → formula: {formula!r}")
                print(f"        display:        {display!r}")
            except Exception as e:
                print(f"  Col {label}: read error — {e}")

    print("\n" + "=" * 70)
    print(" DONE. Copy the entire output above and paste it back to Claude.")
    print("=" * 70)


if __name__ == "__main__":
    main()
