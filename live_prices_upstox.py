"""
live_prices_upstox.py v1.0 (2026-11-06) - real-time prices for the Nifty200 feed from Upstox's free, READ-ONLY Analytics Token.

WHY (owner 2026-11-05/06: 'I want data without delay'): Yahoo's data was measured fresh (0-1 min) on 2026-11-06, but it is an unofficial source. Upstox's market-data API is the
broker's own feed, supports up to 500 instruments in ONE call, and the Analytics Token needs no daily login/TOTP (valid 1 year). The token CANNOT place, change or cancel
orders (Upstox: 'does not grant access to trading operations'); it only reads market data. It lives in the GitHub secret UPSTOX_ANALYTICS_TOKEN and is never printed.

Used by fetch_live_prices.py (UPSTOX_MODE = off | shadow | live). Fail-open everywhere: any problem returns {} and the caller keeps using Yahoo.
API facts (https://upstox.com/developer/api-documentation/get-full-market-quote-v3/): GET https://api.upstox.com/v3/market-quote/quotes?instrument_key=K1,K2 (max 500),
header Authorization: Bearer <token>; response data is keyed 'NSE_EQ:SYMBOL', each entry has last_price, volume, net_change, prev_close_price, instrument_token, ...
Instrument keys come from the public file https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz (cached per day).

USAGE: python live_prices_upstox.py --check     (needs UPSTOX_ANALYTICS_TOKEN; prints mapping + sample quotes, writes nothing)
"""
import gzip
import json
import os
import sys
import tempfile
from datetime import datetime

INSTR_URL = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz"
QUOTE_URL = "https://api.upstox.com/v3/market-quote/quotes"
INDEX_KEYS = {"NIFTY": "NSE_INDEX|Nifty 50"}          # sheet row 'NSE:NIFTY50' -> Nifty 50 index
CACHE = os.path.join(tempfile.gettempdir(), "upstox_nse_instruments.json")


def _num(x):
    try:
        v = float(x)
        return v if v == v else None
    except Exception:
        return None


def parse_quote(q):
    """One entry of the v3 'data' object -> {'cmp','pct','vol'} or None when there is no usable last price. Pure function.
    pct is computed from prev_close_price when present, else from net_change; never from a guess."""
    if not isinstance(q, dict):
        return None
    last = _num(q.get("last_price"))
    if not last or last <= 0:
        return None
    prev = _num(q.get("prev_close_price"))
    net = _num(q.get("net_change"))
    pct = None
    if prev and prev > 0:
        pct = (last - prev) / prev * 100.0
    elif net is not None and (last - net) > 0:
        pct = net / (last - net) * 100.0
    vol = _num(q.get("volume"))
    return {"cmp": round(last, 2), "pct": None if pct is None else round(pct, 2), "vol": None if vol is None else int(vol)}


def load_instruments(today=None, session=None):
    """{trading_symbol: instrument_key} for NSE_EQ equities, cached in the temp dir for the day (the file is ~2 MB and changes daily). {} on any problem."""
    today = today or datetime.now().strftime("%Y-%m-%d")
    try:
        if os.path.exists(CACHE):
            c = json.load(open(CACHE, encoding="utf-8"))
            if c.get("date") == today and c.get("map"):
                return c["map"]
    except Exception:
        pass
    try:
        import requests
        r = (session or requests).get(INSTR_URL, timeout=40)
        r.raise_for_status()
        data = json.loads(gzip.decompress(r.content).decode("utf-8"))
        m = {x["trading_symbol"]: x["instrument_key"] for x in data
             if x.get("segment") == "NSE_EQ" and x.get("instrument_type") == "EQ" and x.get("trading_symbol") and x.get("instrument_key")}
        if len(m) < 1000:
            print(f"[UPSTOX] instruments file looks wrong ({len(m)} equities) - ignored")
            return {}
        try:
            json.dump({"date": today, "map": m}, open(CACHE, "w", encoding="utf-8"))
        except Exception:
            pass
        return m
    except Exception as e:
        print(f"[UPSTOX] instruments download failed ({str(e)[:80]})")
        return {}


def key_for(nse_sym, instruments):
    """'NSE:RELIANCE' -> 'NSE_EQ|INE002A01018'; 'NSE:NIFTY50' -> the Nifty 50 index key; None when unknown."""
    s = str(nse_sym).replace("NSE:", "").strip().upper()
    if "NIFTY" in s:
        return INDEX_KEYS["NIFTY"]
    return instruments.get(s)


def fetch_quotes(token, sym_to_key, session=None, chunk=500):
    """{nse_sym: {'cmp','pct','vol'}} for every symbol the API answered with a usable price. {} on any failure (fail-open, no exception)."""
    out = {}
    if not token or not sym_to_key:
        return out
    try:
        import requests
        http = session or requests
        key_to_sym = {v: k for k, v in sym_to_key.items()}
        keys = list(key_to_sym)
        for i in range(0, len(keys), chunk):
            part = keys[i:i + chunk]
            r = http.get(QUOTE_URL, params={"instrument_key": ",".join(part)},
                         headers={"Accept": "application/json", "Authorization": f"Bearer {token}"}, timeout=20)
            if r.status_code != 200:
                print(f"[UPSTOX] quotes HTTP {r.status_code}: {r.text[:140].replace(token, '***')}")
                continue
            data = (r.json() or {}).get("data") or {}
            for dkey, q in data.items():
                k = (q or {}).get("instrument_token") or ""
                sym = key_to_sym.get(k)
                if sym is None:                                           # fallback: 'NSE_EQ:SYMBOL' -> match by trading symbol
                    tail = dkey.split(":", 1)[-1].strip().upper()
                    sym = next((s for s in sym_to_key if str(s).replace("NSE:", "").strip().upper() == tail), None)
                pq = parse_quote(q)
                if sym and pq:
                    out[sym] = pq
    except Exception as e:
        print(f"[UPSTOX] quotes failed ({str(e)[:100]})")
    return out


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    token = os.environ.get("UPSTOX_ANALYTICS_TOKEN", "").strip()
    if "--check" not in argv:
        print(__doc__)
        return 0
    if not token:
        print("[CHECK] UPSTOX_ANALYTICS_TOKEN is not set")
        return 1
    instr = load_instruments()
    print(f"[CHECK] instruments: {len(instr)} NSE equities")
    sample = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "BHARTIARTL", "TECHM", "M&M", "SBIN", "ITC", "ICICIBANK"]
    m = {f"NSE:{s}": key_for(s, instr) for s in sample}
    m["NSE:NIFTY50"] = key_for("NIFTY50", instr)
    m = {k: v for k, v in m.items() if v}
    q = fetch_quotes(token, m)
    print(f"[CHECK] asked {len(m)}, got {len(q)}")
    for s, v in q.items():
        print(f"   {s:14} {v}")
    return 0 if q else 1


if __name__ == "__main__":
    sys.exit(main())
