"""upstox_candle_probe.py (2026-11-07) - READ-ONLY: how far back does Upstox serve intraday candles to the free Analytics Token? Prints counts only; writes nothing."""
import os
import sys

import requests

TOKEN = os.environ.get("UPSTOX_ANALYTICS_TOKEN", "").strip()
H = {"Accept": "application/json", "Authorization": f"Bearer {TOKEN}"}
KEY = "NSE_INDEX|Nifty 50"


def get(unit, interval, to_d, from_d, key=KEY):
    url = f"https://api.upstox.com/v3/historical-candle/{key}/{unit}/{interval}/{to_d}/{from_d}"
    r = requests.get(url, headers=H, timeout=30)
    if r.status_code != 200:
        return r.status_code, r.text[:160].replace(TOKEN, "***")
    c = ((r.json() or {}).get("data") or {}).get("candles") or []
    return 200, (len(c), c[-1][0] if c else None, c[0][0] if c else None)


def main():
    if not TOKEN:
        print("no token")
        return 1
    tests = [("minutes", 5, "2026-11-06", "2026-10-07"), ("minutes", 15, "2026-11-06", "2026-08-07"), ("minutes", 5, "2025-06-30", "2025-06-02"),
             ("minutes", 5, "2023-06-30", "2023-06-02"), ("minutes", 1, "2022-03-31", "2022-03-01"), ("hours", 1, "2024-12-31", "2024-01-01"), ("days", 1, "2026-11-06", "2016-01-01")]
    for u, i, to_d, fr in tests:
        print(f"{u} x{i} {fr}..{to_d}:", get(u, i, to_d, fr))
    print("stock sample RELIANCE 5min 2025-06:", get("minutes", 5, "2025-06-30", "2025-06-02", "NSE_EQ|INE002A01018"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
