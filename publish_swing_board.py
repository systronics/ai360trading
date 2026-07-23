# ══════════════════════════════════════════════════════════════════════════════
# publish_swing_board.py — v1.0 (2026-07-23)
# ══════════════════════════════════════════════════════════════════════════════
# Reads the LIVE AlertLog tab (the real trade sheet) and writes a PUBLIC-SAFE
# subset to _data/swing_board.json for the swing-dashboard.html page — a free
# teaser (symbol/type/status only) to attract visitors toward Telegram/
# membership, same funnel purpose the old (broken) SwingPublic sheet-tab embed
# served, rebuilt on the same doctrine as performance_stats.py's
# _data/performance.json: a static Jekyll data file, never a live client-side
# fetch against a Google Sheets "Publish to web" link (that's what broke —
# publishing a NEW tab needs a manual Sheets-UI step with no API, see the
# SwingPublic incident, 2026-07-23).
#
# NEVER include: Initial SL, Target, RR Ratio, Entry Price, Trailing SL,
# P/L %, Risk ₹, Position Size, Strike, Expiry, Theta Risk — those stay
# premium-only per the membership funnel (Advance/Premium get exact levels
# in Telegram). Only Symbol / Trade Type / Strategy / Breakout Stage /
# Trade Status / Days in Trade are public.
#
# DESIGN RULES (same as performance_stats.py / prices_cache.json):
#   • FAIL-OPEN: any read error → leaves the existing _data/swing_board.json
#     untouched (carry-forward doctrine) rather than wiping a working page.
#   • Read-only against AlertLog — writes nothing back to the sheet.
#   • ₹0 — same GCP service account every other script already uses.
# ══════════════════════════════════════════════════════════════════════════════

import os
import json
import pytz
from datetime import datetime

SHEET_NAME = "Ai360tradingAlgo"
IST = pytz.timezone("Asia/Kolkata")

# AlertLog column indices (0-based) — confirmed live 2026-07-23:
# 0 Time | 1 Symbol | 2 Live Price | 3 Priority Score | 4 Trade Type |
# 5 Strategy | 6 Breakout Stage | 7 Initial SL | 8 Target | 9 RR Ratio |
# 10 Trade Status | 11 Entry Price | 12 Entry Time | 13 Days in Trade | ...
COL_SYMBOL   = 1
COL_TYPE     = 4
COL_STRATEGY = 5
COL_STAGE    = 6
COL_STATUS   = 10
COL_DAYS     = 13


def _open_alertlog():
    """Connect read-only to the AlertLog tab. Raises on failure (caller catches)."""
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds",
              "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        with open("service_account.json") as f:
            raw = f.read().strip()
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)
    return gspread.authorize(creds).open(SHEET_NAME).worksheet("AlertLog")


def get_public_setups():
    """
    Returns a list of public-safe setup dicts, or None on failure.
    Each dict: symbol, trade_type, strategy, stage, status, days_in_trade.
    Skips rows with no Symbol (empty template slots).
    """
    rows = _open_alertlog().get_all_values()[1:]
    setups = []
    for r in rows:
        while len(r) < 14:
            r.append("")
        symbol = str(r[COL_SYMBOL]).replace("NSE:", "").strip()
        status = str(r[COL_STATUS]).strip()
        if not symbol or not status:
            continue
        setups.append({
            "symbol":       symbol,
            "trade_type":   str(r[COL_TYPE]).strip() or "—",
            "strategy":     str(r[COL_STRATEGY]).strip() or "—",
            "stage":        str(r[COL_STAGE]).strip() or "—",
            "status":       status,
            "days_in_trade": str(r[COL_DAYS]).strip() or "—",
        })
    return setups


def write_data_json(path="_data/swing_board.json"):
    """
    Dumps get_public_setups() to a Jekyll _data JSON file so swing-dashboard.html
    can render it via site.data.swing_board at build time — no client-side fetch,
    no Google Sheets "Publish to web" dependency. FAIL-OPEN: on any error, the
    OLD file is left untouched rather than wiped.
    Returns True if it wrote a fresh file, False if left untouched.
    """
    try:
        setups = get_public_setups()
        out = {
            "generated_at": datetime.now(IST).strftime("%d %B %Y, %I:%M %p IST"),
            "setups": setups,
        }
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"[SWING_BOARD] wrote {path} — {len(setups)} setup(s)")
        return True
    except Exception as e:
        print(f"[SWING_BOARD] write skipped ({e}) — leaving existing file untouched")
        return False


if __name__ == "__main__":
    # Read-only self-test against the live sheet (writes nothing to the sheet).
    setups = get_public_setups()
    print(json.dumps(setups, ensure_ascii=False, indent=2))
    write_data_json()
