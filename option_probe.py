"""
option_probe.py v1.0 (2026-11-10) - READ-ONLY look at ONE option contract with the free Upstox Analytics Token (the same read-only token option_snap.py uses).
Prints (never writes anywhere, never sends a message, never prints a token): premium, bid/ask spread, IV, delta, theta, volume, OI, lot size, cost of one lot, break-even and the stock move needed,
plus the chain's PCR, call/put walls and max pain, for the nearest two expiries. Informational only; nothing in the trading system reads it.
USAGE (CI): python option_probe.py COALINDIA 400 CE
"""
import gzip
import json
import os
import sys
from datetime import datetime, timezone

import requests

import option_snap as S

CHAIN = "https://api.upstox.com/v2/option/chain"


def _row_for(rows, strike):
    best = None
    for r in rows or []:
        k = S._f(r.get("strike_price"))
        if k is not None and (best is None or abs(k - strike) < abs(S._f(best.get("strike_price")) - strike)):
            best = r
    return best


def contract_summary(row, side, lot, spot):
    """Pure: numbers for one side ('CE'/'PE') of a chain row. Returns a dict (values None when unknown)."""
    o = (row.get("call_options") if side == "CE" else row.get("put_options")) or {}
    md, g = o.get("market_data") or {}, o.get("option_greeks") or {}
    strike = S._f(row.get("strike_price"))
    ltp, bid, ask = S._f(md.get("ltp")), S._f(md.get("bid_price")), S._f(md.get("ask_price"))
    theta = S._f(g.get("theta"))
    be = (strike + ltp) if (side == "CE" and ltp is not None) else ((strike - ltp) if ltp is not None else None)
    return {
        "strike": strike, "ltp": ltp, "bid": bid, "ask": ask,
        "spread_pct": round((ask - bid) / ltp * 100, 2) if (ask and bid and ltp and ask >= bid) else None,
        "iv": S._f(g.get("iv")), "delta": S._f(g.get("delta")), "theta_per_day": theta,
        "theta_pct_of_premium": round(abs(theta) / ltp * 100, 2) if (theta is not None and ltp) else None,
        "volume": S._f(md.get("volume")), "oi": S._f(md.get("oi")), "prev_oi": S._f(md.get("prev_oi")),
        "lot": lot, "cost_one_lot": round(ltp * lot, 2) if (ltp is not None and lot) else None,
        "breakeven": round(be, 2) if be is not None else None,
        "move_needed_pct": round((be - spot) / spot * 100, 2) if (be is not None and spot and side == "CE") else (
            round((spot - be) / spot * 100, 2) if (be is not None and spot) else None),
    }


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) < 2:
        print("usage: python option_probe.py SYMBOL STRIKE [CE|PE]")
        return 0
    sym, strike = argv[0].upper(), float(argv[1])
    side = (argv[2] if len(argv) > 2 else "CE").upper()
    token = os.environ.get("UPSTOX_ANALYTICS_TOKEN", "").strip()
    if not token:
        print("[PROBE] no UPSTOX_ANALYTICS_TOKEN - nothing to do")
        return 0
    try:
        import live_prices_upstox as UP
        # 2026-11-10 v1.1: index options too (SENSEX is a BSE contract, NIFTY/BANKNIFTY are NSE)
        INDEX = {"SENSEX": ("BSE_INDEX|SENSEX", "BSE", "BSE_FO"), "NIFTY": ("NSE_INDEX|Nifty 50", "NSE", "NSE_FO"),
                 "BANKNIFTY": ("NSE_INDEX|Nifty Bank", "NSE", "NSE_FO")}
        if sym in INDEX:
            ukey, exch, seg = INDEX[sym]
        else:
            ukey, exch, seg = UP.load_instruments().get(sym), "NSE", "NSE_FO"
        r = requests.get(f"https://assets.upstox.com/market-quote/instruments/exchange/{exch}.json.gz", timeout=60)
        r.raise_for_status()
        data = json.loads(gzip.decompress(r.content).decode("utf-8"))
        lots, exps = {}, set()
        for x in data:
            if x.get("segment") == seg and x.get("underlying_symbol") == sym and x.get("instrument_type") in ("CE", "PE"):
                exps.add(x["expiry"])
                if S._f(x.get("strike_price")) == strike and x.get("instrument_type") == side:
                    lots[x["expiry"]] = int(x.get("lot_size") or 0) or None
        if not ukey or not exps:
            print(f"[PROBE] {sym}: no F&O contracts found")
            return 0
        today = datetime.now(timezone.utc).date()
        coming = [e for e in sorted(exps) if datetime.fromtimestamp(e / 1000, timezone.utc).date() >= today][:2]
        print(f"[PROBE] {sym} {strike:g} {side}  (data time {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC; after market hours values are the last traded)")
        for e in coming:
            d = datetime.fromtimestamp(e / 1000, timezone.utc)
            exp = d.strftime("%Y-%m-%d")
            dte = (d.date() - today).days
            rr = requests.get(CHAIN, params={"instrument_key": ukey, "expiry_date": exp},
                              headers={"Accept": "application/json", "Authorization": f"Bearer {token}"}, timeout=25)
            if rr.status_code != 200:
                print(f"[PROBE] expiry {exp}: HTTP {rr.status_code}")
                continue
            rows = (rr.json() or {}).get("data") or []
            spot = S._f(rows[0].get("underlying_spot_price")) if rows else None
            row = _row_for(rows, strike)
            if not row:
                print(f"[PROBE] expiry {exp}: strike not in the chain")
                continue
            cs = contract_summary(row, side, lots.get(e), spot)
            m = S.chain_metrics(rows, spot) or {}
            print(f"[PROBE] --- expiry {exp} ({dte} days left), stock {spot}")
            for k in ("strike", "ltp", "bid", "ask", "spread_pct", "iv", "delta", "theta_per_day", "theta_pct_of_premium", "volume", "oi", "prev_oi", "lot", "cost_one_lot", "breakeven", "move_needed_pct"):
                print(f"[PROBE]   {k}: {cs[k]}")
            print(f"[PROBE]   chain: PCR {m.get('pcr')}, call wall {m.get('call_wall')}, put wall {m.get('put_wall')}, max pain {m.get('max_pain')}")
    except Exception as e:
        print(f"[PROBE] skipped (fail-open): {str(e)[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
