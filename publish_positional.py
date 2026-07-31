# ══════════════════════════════════════════════════════════════════════════════
# publish_positional.py — v1.0 (2026-07-31)
# ══════════════════════════════════════════════════════════════════════════════
# Reads the LIVE PositionalLatest tab (public-facing teaser, rewritten every
# Sunday by generate_longterm.py) and writes it to _data/positional.json for
# positional-picks.html — the same doctrine as publish_swing_board.py's
# _data/swing_board.json: a static Jekyll data file, not a live client-side
# fetch against a Google Sheets "Publish to web" link.
#
# WHY (2026-07-31 full-system audit): positional-picks.html was still running
# on the exact same "Publish to web" CSV mechanism that broke silently for
# SwingPublic on 2026-07-23 (no API to fix it, needs a manual Sheets-UI
# republish step every time a NEW tab/gid is involved). It happened to still
# be working when checked, but it's the same class of single point of failure
# already proven to fail once, unnoticed, on a live page. This closes that gap
# proactively, BEFORE it breaks, not after.
#
# SAFETY — "never break what works" (owner explicitly asked nothing on the
# live page break): this does NOT remove the existing CSV fetch or the iframe
# fallback in positional-picks.html. The page tries this JSON file FIRST; if
# it's missing or empty, it falls through to the exact same CSV fetch it
# already had, which falls through to the exact same iframe it already had.
# Three independent layers, none removed.
#
# DESIGN RULES (same as publish_swing_board.py / performance_stats.py):
#   • FAIL-OPEN: any read error → leaves the existing _data/positional.json
#     untouched (carry-forward doctrine) rather than wiping a working page.
#   • Read-only against PositionalLatest — writes nothing back to the sheet.
#   • ₹0 — same GCP service account every other script already uses.
# ══════════════════════════════════════════════════════════════════════════════

import os
import json
import pytz
from datetime import datetime

SHEET_NAME = "Ai360tradingAlgo"
TAB_NAME = "PositionalLatest"
IST = pytz.timezone("Asia/Kolkata")


def _open_positional():
    """Connect read-only to the PositionalLatest tab. Raises on failure (caller catches)."""
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds",
              "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        with open("service_account.json") as f:
            raw = f.read().strip()
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)
    return gspread.authorize(creds).open(SHEET_NAME).worksheet(TAB_NAME)


def get_public_rows():
    """
    Returns [header_row, data_row, data_row, ...] — same shape the page's
    existing CSV parser already produces, so the front-end render() function
    does not need to change. Header comes straight from the sheet (already
    the 5-column teaser: Stock/Company/Sector/Signal/CMP ₹). Skips fully
    blank rows.
    """
    values = _open_positional().get_all_values()
    rows = [r for r in values if any(str(c).strip() for c in r)]
    return rows


def write_data_json(path="_data/positional.json"):
    """
    Dumps get_public_rows() to a Jekyll _data JSON file. FAIL-OPEN: on any
    error, the OLD file is left untouched rather than wiped.
    Returns True if it wrote a fresh file, False if left untouched.
    """
    try:
        rows = get_public_rows()
        out = {
            "generated_at": datetime.now(IST).strftime("%d %B %Y, %I:%M %p IST"),
            "rows": rows,
        }
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"[POSITIONAL] wrote {path} — {max(0, len(rows) - 1)} pick(s)")
        return True
    except Exception as e:
        print(f"[POSITIONAL] write skipped ({e}) — leaving existing file untouched")
        return False


if __name__ == "__main__":
    # Read-only self-test against the live sheet (writes nothing to the sheet).
    rows = get_public_rows()
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    write_data_json()
