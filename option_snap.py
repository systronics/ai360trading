"""
option_snap.py v1.0 (2026-11-07) - OBSERVATION-ONLY option-chain recorder (new `OptionSnap` tab) from Upstox's free, read-only Analytics Token.

WHY (owner 2026-11-07: 'now that the API is linked, can we take the option data (volume, max pain, theta, PCR, OI change) for better and timely intraday signals, ideally with next-day continuation'):
the chain gives per strike: ltp, volume, oi, prev_oi, bid/ask + qty, iv, delta, theta, vega, gamma, pop (probe 2026-11-07). Nobody yet knows which of these actually predicts a good intraday option entry here,
so this only RECORDS them (about hourly in market hours) for the most option-relevant stocks + NIFTY; outcomes are scored later, and only a feature that beats the baseline over 3-4 weeks may be proposed as a soft alert line.
It never reads or writes AlertLog/History/BotMemory, never sends a Telegram message, and no gate/alert reads this tab (see CLAUDE.md doctrine: ShadowLedger/BuildupWatch/GateAudit).

Per snapshot row: time, symbol, expiry, days to expiry, spot, ATM strike, ATM CE/PE premium, IV, theta as % of premium, bid-ask spread %, volume, OI change % (OI vs prev OI), total PCR (put OI / call OI),
max pain strike, call wall (largest call OI above spot), put wall (largest put OI below spot), day % of the stock.
Fail-open: any problem = nothing written. Usage: python option_snap.py [--write] [--max 20] [--symbols RELIANCE,TCS] [--force]   (--force ignores the market-hours guard)
"""
import gzip
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone

import pytz

IST = pytz.timezone("Asia/Kolkata")
TAB = "OptionSnap"
HEAD = ["Time", "Symbol", "Expiry", "DTE", "Spot", "Day_%", "ATM_Strike", "CE_Prem", "PE_Prem", "CE_IV", "PE_IV", "CE_Theta_%", "PE_Theta_%", "CE_Spread_%", "PE_Spread_%",
        "CE_Vol", "PE_Vol", "CE_OI_Chg_%", "PE_OI_Chg_%", "PCR", "Max_Pain", "Call_Wall", "Put_Wall", "Next_Day_Stock_%", "Scored"]
FO_CACHE = os.path.join(tempfile.gettempdir(), "upstox_fo_expiries.json")
MIN_GAP_MIN = 55          # per symbol, at most one snapshot every ~hour
ROLLOVER_DAYS = 5          # same rule as the rest of the system: <=5 days to expiry -> next month's expiry
KEEP_DAYS = 120


def _f(x):
    try:
        v = float(x)
        return v if v == v else None
    except Exception:
        return None


def max_pain(strikes):
    """strikes: list of (strike, call_oi, put_oi). Strike where option writers' total payout is smallest. None when empty."""
    pts = [(k, c or 0.0, p or 0.0) for k, c, p in strikes if k is not None]
    if not pts:
        return None
    best, best_pain = None, None
    for k, _, _ in pts:
        pain = sum(c * max(0.0, k - kk) + p * max(0.0, kk - k) for kk, c, p in pts)
        if best_pain is None or pain < best_pain:
            best, best_pain = k, pain
    return best


def chain_metrics(rows, spot=None):
    """rows = the 'data' list of /v2/option/chain. Returns a dict of the snapshot numbers or None when unusable. Pure function."""
    if not rows:
        return None
    spot = spot or _f(rows[0].get("underlying_spot_price"))
    if not spot:
        return None
    atm = min(rows, key=lambda r: abs((_f(r.get("strike_price")) or 0) - spot))
    ce, pe = atm.get("call_options") or {}, atm.get("put_options") or {}

    def side(o):
        md, g = o.get("market_data") or {}, o.get("option_greeks") or {}
        ltp, bid, ask, oi, poi = _f(md.get("ltp")), _f(md.get("bid_price")), _f(md.get("ask_price")), _f(md.get("oi")), _f(md.get("prev_oi"))
        theta = _f(g.get("theta"))
        return {"prem": ltp, "iv": _f(g.get("iv")), "vol": _f(md.get("volume")),
                "theta_pct": round(abs(theta) / ltp * 100, 2) if (theta is not None and ltp) else None,
                "spread_pct": round((ask - bid) / ltp * 100, 2) if (ask and bid and ltp and ask >= bid) else None,
                "oi_chg": round((oi - poi) / poi * 100, 1) if (oi is not None and poi) else None}
    c, p = side(ce), side(pe)
    strikes = [(_f(r.get("strike_price")), _f((r.get("call_options") or {}).get("market_data", {}).get("oi")),
                _f((r.get("put_options") or {}).get("market_data", {}).get("oi"))) for r in rows]
    tot_c = sum(x[1] or 0 for x in strikes)
    tot_p = sum(x[2] or 0 for x in strikes)
    above = [x for x in strikes if x[0] and x[0] > spot and x[1]]
    below = [x for x in strikes if x[0] and x[0] < spot and x[2]]
    return {"spot": spot, "atm": _f(atm.get("strike_price")), "ce": c, "pe": p,
            "pcr": round(tot_p / tot_c, 2) if tot_c else None, "max_pain": max_pain(strikes),
            "call_wall": max(above, key=lambda x: x[1])[0] if above else None,
            "put_wall": max(below, key=lambda x: x[2])[0] if below else None}


def pick_expiry(expiries_ms, now_utc=None):
    """Monthly expiry per the system rule: the nearest expiry that is more than ROLLOVER_DAYS away. Returns (YYYY-MM-DD, dte) or (None, None)."""
    now_utc = now_utc or datetime.now(timezone.utc)
    for e in sorted(expiries_ms):
        d = datetime.fromtimestamp(e / 1000, timezone.utc)
        dte = (d.date() - now_utc.date()).days
        if dte > ROLLOVER_DAYS:
            return d.strftime("%Y-%m-%d"), dte
    return None, None


def load_fo_expiries(today=None):
    """{underlying_symbol: [expiry_ms,...]} for NSE option contracts, cached per day. {} on any problem."""
    today = today or datetime.now().strftime("%Y-%m-%d")
    try:
        if os.path.exists(FO_CACHE):
            c = json.load(open(FO_CACHE, encoding="utf-8"))
            if c.get("date") == today and c.get("map"):
                return c["map"]
    except Exception:
        pass
    try:
        import requests
        r = requests.get("https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz", timeout=40)
        r.raise_for_status()
        data = json.loads(gzip.decompress(r.content).decode("utf-8"))
        m = {}
        for x in data:
            if x.get("segment") == "NSE_FO" and x.get("instrument_type") in ("CE", "PE") and x.get("underlying_symbol") and x.get("expiry"):
                m.setdefault(x["underlying_symbol"], set()).add(x["expiry"])
        m = {k: sorted(v) for k, v in m.items()}
        if len(m) < 100:
            return {}
        json.dump({"date": today, "map": m}, open(FO_CACHE, "w", encoding="utf-8"))
        return m
    except Exception as e:
        print(f"[SNAP] F&O instruments failed ({str(e)[:80]})")
        return {}


def _connect():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    now = datetime.now(IST)
    hm = now.strftime("%H:%M")
    if "--force" not in argv and not (now.weekday() < 5 and "09:30" <= hm <= "15:20"):
        print(f"[SNAP] {hm} IST outside market hours, nothing to do")
        return 0
    token = os.environ.get("UPSTOX_ANALYTICS_TOKEN", "").strip()
    if not token:
        print("[SNAP] no token - skipped")
        return 0
    try:
        import requests
        import live_prices_upstox as UP
        sh = _connect()
        n = sh.worksheet("Nifty200").get_all_values()
        h = n[0]
        iS, iO, iM, iP = h.index("NSE_SYMBOL"), h.index("Options"), h.index("Master_Score"), h.index("%Change")
        cands = []
        for r in n[2:]:
            if len(r) > max(iO, iM) and r[iO].strip() in ("N50", "YES") and _f(r[iM]) is not None:
                cands.append((_f(r[iM]), r[iS].replace("NSE:", "").strip(), _f(r[iP])))
        cands.sort(reverse=True)
        mx = int(argv[argv.index("--max") + 1]) if "--max" in argv else 20
        names = [(s, d) for _, s, d in cands[:mx]]
        if "--symbols" in argv:
            want = argv[argv.index("--symbols") + 1].split(",")
            names = [(s, d) for _, s, d in cands if s in want]
        names = [("NIFTY", None)] + names
        instr = UP.load_instruments()
        fo = load_fo_expiries()
        try:
            ws = sh.worksheet(TAB)
        except Exception:
            ws = sh.add_worksheet(TAB, rows=3000, cols=len(HEAD))
            ws.update(range_name="A1", values=[HEAD])
        existing = ws.get_all_values()
        last_seen = {}
        for r in existing[1:]:
            if len(r) > 1 and r[0]:
                last_seen[r[1]] = r[0]
        out = []
        for sym, day_pct in names:
            ts = last_seen.get(sym)
            if ts:
                try:
                    age = (now.replace(tzinfo=None) - datetime.strptime(ts, "%Y-%m-%d %H:%M")).total_seconds() / 60
                    if age < MIN_GAP_MIN and "--force" not in argv:
                        continue
                except Exception:
                    pass
            if sym == "NIFTY":
                ukey = "NSE_INDEX|Nifty 50"
                exps = fo.get("NIFTY", [])
                exp, dte = None, None
                for e in sorted(exps):             # index: nearest expiry that is at least 2 days away
                    d = datetime.fromtimestamp(e / 1000, timezone.utc)
                    dd = (d.date() - now.astimezone(timezone.utc).date()).days
                    if dd >= 2:
                        exp, dte = d.strftime("%Y-%m-%d"), dd
                        break
            else:
                ukey = instr.get(sym)
                exp, dte = pick_expiry(fo.get(sym, []))
            if not ukey or not exp:
                continue
            r = requests.get("https://api.upstox.com/v2/option/chain", params={"instrument_key": ukey, "expiry_date": exp},
                             headers={"Accept": "application/json", "Authorization": f"Bearer {token}"}, timeout=20)
            if r.status_code != 200:
                print(f"[SNAP] {sym}: HTTP {r.status_code}")
                continue
            m = chain_metrics((r.json() or {}).get("data") or [])
            if not m:
                continue
            c, p = m["ce"], m["pe"]
            out.append([now.strftime("%Y-%m-%d %H:%M"), sym, exp, dte, m["spot"], day_pct if day_pct is not None else "", m["atm"], c["prem"], p["prem"], c["iv"], p["iv"],
                        c["theta_pct"], p["theta_pct"], c["spread_pct"], p["spread_pct"], c["vol"], p["vol"], c["oi_chg"], p["oi_chg"], m["pcr"], m["max_pain"],
                        m["call_wall"], m["put_wall"], "", ""])
            time.sleep(0.4)
        print(f"[SNAP] {len(out)} snapshot row(s) for {len(names)} names at {hm} IST")
        for row in out[:4]:
            print("   ", row[:12])
        if "--write" in argv and out:
            start = len(existing) + 1
            if ws.row_count < start + len(out) + 5:
                ws.add_rows(start + len(out) + 5 - ws.row_count)
            ws.update(range_name=f"A{start}", values=out, value_input_option="USER_ENTERED")
            print(f"[SNAP] wrote {len(out)} rows at row {start}")
    except Exception as e:
        print(f"[SNAP] skipped (fail-open): {str(e)[:140]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
