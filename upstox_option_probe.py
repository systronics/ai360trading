"""
upstox_option_probe.py v1.0 (2026-11-07) - READ-ONLY probe: which option-chain fields does Upstox return to our free Analytics Token?
Prints the field NAMES and one ATM strike for RELIANCE and NIFTY (current expiry): OI, previous OI, volume, bid/ask, IV, greeks (delta/theta/vega/gamma), per-strike PCR.
Writes nothing, trades nothing. Used once to decide what an observation-only option-data logger can record. Needs env UPSTOX_ANALYTICS_TOKEN (never printed).
"""
import gzip
import json
import os
import sys
from datetime import datetime, timezone

import requests

TOKEN = os.environ.get("UPSTOX_ANALYTICS_TOKEN", "").strip()
H = {"Accept": "application/json", "Authorization": f"Bearer {TOKEN}"}


def keys_of(d, depth=0, maxd=3):
    out = []
    if isinstance(d, dict):
        for k, v in d.items():
            out.append("  " * depth + str(k) + (f" = {v}" if not isinstance(v, (dict, list)) else ""))
            if isinstance(v, (dict, list)) and depth < maxd:
                out += keys_of(v, depth + 1, maxd)
    elif isinstance(d, list) and d:
        out += keys_of(d[0], depth, maxd)
    return out


def main():
    if not TOKEN:
        print("no token")
        return 1
    r = requests.get("https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz", timeout=40)
    data = json.loads(gzip.decompress(r.content).decode("utf-8"))
    now_ms = datetime.now(timezone.utc).timestamp() * 1000
    for under, ukey in (("RELIANCE", None), ("NIFTY", "NSE_INDEX|Nifty 50")):
        if ukey is None:
            ukey = next(x["instrument_key"] for x in data if x.get("segment") == "NSE_EQ" and x.get("trading_symbol") == under and x.get("instrument_type") == "EQ")
        exps = sorted({x["expiry"] for x in data if x.get("segment") == "NSE_FO" and x.get("underlying_symbol") == under
                       and x.get("instrument_type") in ("CE", "PE") and x.get("expiry", 0) >= now_ms - 86400000})
        print(f"\n=== {under} key={ukey} upcoming option expiries (ms->date): {[datetime.fromtimestamp(e / 1000, timezone.utc).strftime('%Y-%m-%d') for e in exps[:3]]}")
        if not exps:
            print("no expiries found")
            continue
        exp = datetime.fromtimestamp(exps[0] / 1000, timezone.utc).strftime("%Y-%m-%d")
        rr = requests.get("https://api.upstox.com/v2/option/chain", params={"instrument_key": ukey, "expiry_date": exp}, headers=H, timeout=25)
        print("HTTP", rr.status_code, "expiry", exp)
        if rr.status_code != 200:
            print(rr.text[:300].replace(TOKEN, "***"))
            continue
        j = rr.json()
        rows = j.get("data") or []
        print("strikes returned:", len(rows))
        if rows:
            spot = rows[0].get("underlying_spot_price")
            atm = min(rows, key=lambda x: abs((x.get("strike_price") or 0) - (spot or 0)))
            print("underlying_spot_price:", spot, "| ATM strike:", atm.get("strike_price"))
            print("FIELD TREE of one strike row:")
            print("\n".join(keys_of(atm)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
