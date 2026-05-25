"""
AI360 CashWatchlist Auto-Refresh — v1.1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fully automates the CashWatchlist tab. No manual work ever needed.

What this does:
  1. Seeds CashWatchlist with 35 curated high-volatility stocks (first run)
  2. Sets GOOGLEFINANCE formulas for CMP, Change%, Volume (auto-live data)
  3. Auto-calculates AvgVol30d from yfinance history (no manual entry)
  4. Marks stocks INACTIVE if CMP > ₹500 (outside cash intraday range)
  5. Re-activates stocks if CMP drops back into range

Curated stock types (can give 10-20% in one day):
  - PSU Banks: react 10%+ on RBI policy, quarterly results, govt news
  - PSU Infrastructure: RVNL, IRFC, IRCON — budget/project news
  - Defence PSU: BEL, Cochin Shipyard — defence order news
  - Power: NHPC, SJVN, RPOWER — policy/tariff news
  - Pharma Smallcap: Granules, Laurus — result season plays
  - Others: SUZLON, NMDC — sector/commodity driven

Runs: 1st of every month via refresh_watchlists.yml
Also: workflow_dispatch for first-time setup
"""

import os, json, time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import yfinance as yf
from datetime import datetime
import pytz

IST        = pytz.timezone("Asia/Kolkata")
SHEET_NAME = "Ai360tradingAlgo"
CW_TAB     = "CashWatchlist"
CASH_MAX   = 500  # same as AppScript CONFIG.CASH_MAX_CMP
CASH_MIN   = 30

# ── 35 curated high-volatility stocks ─────────────────────────────────────────
# (Symbol, Name, Sector, Circuit%)
# Circuit% = typical circuit limit for that stock (10 or 20)
CURATED_STOCKS = [
    # PSU Banks — result/news driven 10%+ moves
    ("NSE:UCOBK",      "UCO Bank",                 "PSU Bank",    20),
    ("NSE:MAHABANK",   "Bank of Maharashtra",       "PSU Bank",    10),
    ("NSE:BANKINDIA",  "Bank of India",             "PSU Bank",    10),
    ("NSE:CANBK",      "Canara Bank",               "PSU Bank",    10),
    ("NSE:UNIONBANK",  "Union Bank of India",       "PSU Bank",    10),
    ("NSE:IOB",        "Indian Overseas Bank",      "PSU Bank",    20),
    ("NSE:CENTRALBK",  "Central Bank of India",     "PSU Bank",    20),
    ("NSE:IDFCFIRSTB", "IDFC First Bank",           "Pvt Bank",    10),

    # PSU Infrastructure — order/budget news
    ("NSE:RVNL",       "Rail Vikas Nigam",          "Infra",       10),
    ("NSE:IRFC",       "Indian Railway Finance",    "Infra",       10),
    ("NSE:IRCON",      "IRCON International",       "Infra",       10),
    ("NSE:RAILTEL",    "Railtel Corporation",       "Telecom",     10),
    ("NSE:RITES",      "RITES",                     "Infra",       10),
    ("NSE:NBCC",       "NBCC India",                "Infra",       20),
    ("NSE:COCHINSHIP", "Cochin Shipyard",           "Defence",     10),

    # Power / Energy
    ("NSE:NHPC",       "NHPC",                      "Power",       10),
    ("NSE:SJVN",       "SJVN",                      "Power",       10),
    ("NSE:RPOWER",     "Reliance Power",            "Power",       20),
    ("NSE:SUZLON",     "Suzlon Energy",             "Renewable",   10),
    ("NSE:JPPOWER",    "JP Power Ventures",         "Power",       20),
    ("NSE:INOXWIND",   "Inox Wind",                 "Renewable",   10),

    # Defence PSU
    ("NSE:BEL",        "Bharat Electronics",        "Defence",     10),

    # Pharma / Chemicals Smallcap — result season moves
    ("NSE:GRANULES",   "Granules India",            "Pharma",      10),
    ("NSE:LAURUSLABS", "Laurus Labs",               "Pharma",      10),
    ("NSE:DEEPAKNITR", "Deepak Nitrite",            "Chemicals",   10),
    ("NSE:GNFC",       "Gujarat Narmada Fertiliser","Chemicals",   10),

    # Metals / Mining
    ("NSE:NMDC",       "NMDC",                      "Mining",      10),
    ("NSE:MOIL",       "MOIL",                      "Mining",      10),

    # Telecom / Media
    ("NSE:ZEEL",       "Zee Entertainment",         "Media",       10),
    ("NSE:HFCL",       "HFCL",                      "Telecom",     20),

    # Consumer / Real Estate
    ("NSE:PCBL",       "PCBL",                      "Chemicals",   10),
    ("NSE:YESBANK",    "Yes Bank",                  "Pvt Bank",    10),

    # Special situations
    ("NSE:IDEA",       "Vodafone Idea",             "Telecom",     20),
    ("NSE:DELTACORP",  "Delta Corp",                "Gaming",      20),
]

# CashWatchlist columns (1-based for gspread)
# A=1:Symbol  B=2:Name  C=3:Sector  D=4:Circuit%  E=5:Notes
# F=6:Active  G=7:CMP   H=8:Change% I=9:Volume    J=10:AvgVol30d
CW_HEADERS = ["Symbol", "Name", "Sector", "Circuit%", "Notes",
               "Active", "CMP", "Change%", "Volume", "AvgVol30d"]

# ── Sheet connection ──────────────────────────────────────────────────────────
def _connect():
    # v1.1: explicit cred validation — fails with clear message instead of cryptic FileNotFoundError
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        try:
            with open("service_account.json") as f:
                raw = f.read().strip()
        except FileNotFoundError:
            raise SystemExit("[CREDS] GCP_SERVICE_ACCOUNT_JSON env var not set and service_account.json not found locally")
    try:
        creds_dict = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"[CREDS] Failed to parse GCP credentials JSON: {e}")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    gc    = gspread.authorize(creds)
    return gc.open(SHEET_NAME)

def _get_or_create(wb, name, headers):
    try:
        return wb.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = wb.add_worksheet(title=name, rows=100, cols=len(headers))
        ws.append_row(headers)
        print(f"[CW] Created tab: {name}")
        return ws

# ── yfinance: 30-day average volume ──────────────────────────────────────────
def _avg_vol30(sym):
    try:
        hist = yf.Ticker(sym.replace("NSE:", "").replace("BSE:", "") + ".NS"
                         ).history(period="35d", interval="1d")
        if hist.empty or len(hist) < 5:
            return 0
        return int(hist["Volume"].mean())
    except Exception as e:
        print(f"[CW] Vol fetch {sym}: {e}")
        return 0

def _current_price(sym):
    try:
        t   = yf.Ticker(sym.replace("NSE:", "").replace("BSE:", "") + ".NS")
        cmp = t.info.get("currentPrice") or t.info.get("regularMarketPrice") or 0
        return float(cmp)
    except Exception:
        return 0.0

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    now = datetime.now(IST)
    print(f"[CW] CashWatchlist Refresh — {now.strftime('%Y-%m-%d %H:%M IST')}")

    wb = _connect()
    cw = _get_or_create(wb, CW_TAB, CW_HEADERS)

    # Check existing rows — avoid re-seeding if already populated
    existing = cw.get_all_values()
    if len(existing) < 2:
        # First time: write all headers + seed all stocks (no formulas yet)
        print("[CW] Empty sheet — seeding with curated stocks...")
        seed_rows = []
        for sym, name, sector, circuit in CURATED_STOCKS:
            seed_rows.append([sym, name, sector, circuit, "", "TRUE", "", "", "", ""])
        cw.append_rows(seed_rows)
        print(f"[CW] Seeded {len(seed_rows)} stocks")
        # Reload
        existing = cw.get_all_values()

    # Build set of existing symbols for deduplication
    existing_syms = set()
    for r in existing[1:]:
        if r and r[0]:
            existing_syms.add(r[0].strip().upper())

    # Add any missing stocks from CURATED_STOCKS
    new_additions = []
    for sym, name, sector, circuit in CURATED_STOCKS:
        if sym.upper() not in existing_syms:
            new_additions.append([sym, name, sector, circuit, "", "TRUE", "", "", "", ""])
    if new_additions:
        cw.append_rows(new_additions)
        print(f"[CW] Added {len(new_additions)} new stocks")
        existing = cw.get_all_values()

    # ── Update GOOGLEFINANCE formulas + AvgVol30d for every row ──────────────
    # Reload after any additions
    total_rows = len(existing)
    print(f"[CW] Updating {total_rows - 1} stocks...")

    for row_i in range(2, total_rows + 1):  # 1-based, skip header
        try:
            r   = existing[row_i - 1]
            sym = r[0].strip() if r else ""
            if not sym:
                continue

            # Set GOOGLEFINANCE formulas (G, H, I columns — always refresh)
            # These auto-update every time the sheet is viewed in Google Sheets
            formula_g = f'=IFERROR(GOOGLEFINANCE("{sym}","price"),0)'
            formula_h = f'=IFERROR(GOOGLEFINANCE("{sym}","changepct"),0)'
            formula_i = f'=IFERROR(GOOGLEFINANCE("{sym}","volume"),0)'

            cw.update_cell(row_i, 7, formula_g)   # G: CMP
            cw.update_cell(row_i, 8, formula_h)   # H: Change%
            cw.update_cell(row_i, 9, formula_i)   # I: Volume

            # Fetch live CMP to check range + calculate AvgVol30d
            print(f"  [{row_i-1}/{total_rows-1}] {sym}...", end=" ", flush=True)
            cmp = _current_price(sym)
            avg_vol = _avg_vol30(sym)

            # Auto-mark INACTIVE if CMP outside cash range
            if cmp > 0:
                is_active = "TRUE" if CASH_MIN <= cmp <= CASH_MAX else "FALSE"
                cw.update_cell(row_i, 6, is_active)  # F: Active

            if avg_vol > 0:
                cw.update_cell(row_i, 10, avg_vol)   # J: AvgVol30d

            status = f"₹{cmp:.0f} | vol={avg_vol:,}" if cmp > 0 else "fetch failed"
            if cmp > CASH_MAX:
                status += " → INACTIVE (above ₹500)"
            print(status)

            time.sleep(2.0)  # yfinance rate limit

        except Exception as e:
            print(f"[CW] Row {row_i}: {e}")
            time.sleep(1)

    print(f"[CW] Done — {CW_TAB} fully refreshed. No manual work needed.")


if __name__ == "__main__":
    main()
