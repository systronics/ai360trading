"""
option_paper.py v1.0 (2026-11-07) - REALISTIC PAPER LEDGER for the owner's intraday option plan (new `OptionPaper` tab). Paper only: no order, no Telegram message, no gate or alert reads it.

OWNER PLAN (2026-11-07): capital Rs 1 lakh, Rs 20-30k for intraday options; 3-5 entries before 11:30, and ONE extra entry 14:20-15:20 only for a 'perfect' setup; target 1:3-1:5 OR trail; same-day profit booking.
WHY A NEW LEDGER: the existing History ledger estimates option P/L from the stock move (leverage guess). This one follows the REAL option contract: it buys at the ASK, sells at the BID (Upstox quotes), applies approximate costs,
and records the quality numbers at entry (spread %, theta % of premium, IV) so that, after 20-30 trades, the plan's real expectancy is known BEFORE real money is sized up.

SIGNAL SOURCE: the system's own option alerts - an AlertLog row with Options Signal 'BUY CE' whose Trade Status is TRADED (it already passed every gate). Nothing here creates a signal.
RULES (all constants below; change only on the owner's word):
  entries      09:20-11:30 up to MAX_EARLY (5); 14:20-15:15 up to MAX_LATE (1) and only when AlertLog Priority >= LATE_MIN_PRIORITY; no new entry once today's realized loss <= -DAILY_LOSS_STOP (Rs 4,000)
  size         premium budget PREMIUM_BUDGET (Rs 10,000 = about Rs 2,500 risk at a 25% stop = 2.5% of Rs 1 lakh); total open premium capped at MAX_OPEN_PREMIUM (Rs 30,000); 1 lot allowed up to 1.5x the budget, else skipped ('too expensive')
  liquidity    skipped when the bid-ask spread is wider than MAX_SPREAD_PCT (6%)
  stop         SL_PCT 25% below the entry ask (checked on the BID)
  profit       sell half the quantity at +PARTIAL_AT_PCT (50%, i.e. 1:2), then stop moves to breakeven and trails TRAIL_PCT (25%) below the peak bid; the rest runs until the trail or the time exit
  time exit    TIME_EXIT 15:15 (intraday). The next trading day's bid of the same contract is recorded for the 'does it continue next day' question (carry study), not traded.
Paper convention: the half-quantity partial is fractional (a real 1-lot position cannot be split). Costs are approximate: Rs 40 per round trip + 0.14% of the traded value.
Fail-open everywhere. Usage: python option_paper.py [--write] [--check] [--force]    (--check prints what the signals would do, writes nothing; --force ignores market hours)
"""
import gzip
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone

import pytz

IST = pytz.timezone("Asia/Kolkata")
TAB = "OptionPaper"
HEAD = ["ID", "Date", "Symbol", "Strike", "Expiry", "Key", "LotSize", "Lots", "EntryTime", "EntryAsk", "QtyTotal", "QtyOpen", "SL", "Peak", "PartialDone",
        "Spread_%", "Theta_%", "IV", "Status", "ExitTime", "ExitBid", "Realized_Rs", "Reason", "NextDay_Bid"]
PREMIUM_BUDGET = 10000.0          # 2026-11-07: a lot of most liquid stocks costs Rs 8-12k at the money (the owner's Airtel lots: Rs 9.4k and Rs 12.2k); Rs 6k skipped nearly everything
MAX_OPEN_PREMIUM = 30000.0       # owner's intraday-option bucket (Rs 20-30k): total premium open at any time
MAX_BUDGET_MULT = 1.5
SL_PCT = 25.0
PARTIAL_AT_PCT = 50.0
TRAIL_PCT = 25.0
MAX_SPREAD_PCT = 6.0
MAX_EARLY, MAX_LATE = 5, 1
EARLY_FROM, EARLY_TO = "09:20", "11:30"
LATE_FROM, LATE_TO = "14:20", "15:15"
LATE_MIN_PRIORITY = 30.0
DAILY_LOSS_STOP = 4000.0
TIME_EXIT = "15:15"
FO_CACHE = os.path.join(tempfile.gettempdir(), "upstox_fo_contracts.json")


def _f(x):
    try:
        v = float(str(x).replace(",", ""))
        return v if v == v else None
    except Exception:
        return None


def cost_rs(buy_value, sell_value):
    return 40.0 + 0.0014 * (buy_value + sell_value)


def lots_for(ask, lot_size, budget=PREMIUM_BUDGET):
    """Number of lots for the premium budget; 1 lot allowed up to MAX_BUDGET_MULT x the budget, else 0 (too expensive)."""
    if not ask or not lot_size or ask <= 0:
        return 0
    one = ask * lot_size
    n = int(budget // one)
    if n >= 1:
        return n
    return 1 if one <= budget * MAX_BUDGET_MULT else 0


def entry_allowed(hm, early_today, late_today, realized_today, priority):
    """(ok, reason). hm = 'HH:MM' IST. Pure."""
    if realized_today <= -DAILY_LOSS_STOP:
        return False, f"daily loss stop reached ({realized_today:.0f})"
    if EARLY_FROM <= hm <= EARLY_TO:
        return (early_today < MAX_EARLY), ("" if early_today < MAX_EARLY else f"already {MAX_EARLY} early entries today")
    if LATE_FROM <= hm <= LATE_TO:
        if late_today >= MAX_LATE:
            return False, "late-window entry already used today"
        if priority is None or priority < LATE_MIN_PRIORITY:
            return False, f"late entry needs a perfect setup (priority >= {LATE_MIN_PRIORITY:.0f})"
        return True, ""
    return False, "outside the entry windows"


def step_position(pos, bid, hm):
    """Advance one open position by one observation. pos: dict(entry, qty_open, sl, peak, partial). bid = current BID of the contract.
    Returns (pos, sells) where sells = [(qty, price, reason)]. Pure - no I/O."""
    p = dict(pos)
    sells = []
    if bid is None or bid <= 0:
        if hm >= TIME_EXIT:
            return p, [(p["qty_open"], 0.0, f"TIME {TIME_EXIT} (no bid)")]
        return p, sells
    p["peak"] = max(p["peak"], bid)
    entry = p["entry"]
    if hm >= TIME_EXIT:
        return p, [(p["qty_open"], bid, f"TIME {TIME_EXIT}")]
    if bid <= p["sl"]:
        reason = "STOP" if not p["partial"] else ("BREAKEVEN/TRAIL STOP")
        return p, [(p["qty_open"], bid, reason)]
    if not p["partial"] and bid >= entry * (1 + PARTIAL_AT_PCT / 100.0):
        half = p["qty_open"] / 2.0
        sells.append((half, bid, f"PARTIAL +{PARTIAL_AT_PCT:.0f}%"))
        p["qty_open"] -= half
        p["partial"] = True
    if p["partial"]:
        p["sl"] = max(p["sl"], entry, p["peak"] * (1 - TRAIL_PCT / 100.0))
    return p, sells


def parse_strike(text):
    """'2300 CE Nov' -> 2300.0 ; '' -> None."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*CE", str(text).upper())
    return float(m.group(1)) if m else None


def parse_expiry(text):
    """'23-Nov-2026' -> '2026-11-23'; also accepts '2026-11-23'. None otherwise."""
    t = str(text).strip()
    for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d-%B-%Y"):
        try:
            return datetime.strptime(t, fmt).strftime("%Y-%m-%d")
        except Exception:
            pass
    return None


def load_contracts(today=None):
    """{(underlying, strike, 'YYYY-MM-DD'): (instrument_key, lot_size)} for NSE call options, cached per day. {} on any problem."""
    today = today or datetime.now().strftime("%Y-%m-%d")
    try:
        if os.path.exists(FO_CACHE):
            c = json.load(open(FO_CACHE, encoding="utf-8"))
            if c.get("date") == today and c.get("map"):
                return {tuple(json.loads(k)): tuple(v) for k, v in c["map"].items()}
    except Exception:
        pass
    try:
        import requests
        r = requests.get("https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz", timeout=40)
        r.raise_for_status()
        data = json.loads(gzip.decompress(r.content).decode("utf-8"))
        m = {}
        for x in data:
            if x.get("segment") == "NSE_FO" and x.get("instrument_type") == "CE" and x.get("underlying_symbol") and x.get("expiry") and x.get("strike_price") is not None:
                d = datetime.fromtimestamp(x["expiry"] / 1000, timezone.utc).strftime("%Y-%m-%d")
                m[(x["underlying_symbol"], float(x["strike_price"]), d)] = (x["instrument_key"], int(x.get("lot_size") or 0))
        if len(m) < 1000:
            return {}
        json.dump({"date": today, "map": {json.dumps(list(k)): list(v) for k, v in m.items()}}, open(FO_CACHE, "w", encoding="utf-8"))
        return m
    except Exception as e:
        print(f"[PAPER] contracts download failed ({str(e)[:80]})")
        return {}


def quote_option(token, key):
    """{'bid','ask','ltp'} for one option contract from the v3 full quote, or None."""
    try:
        import requests
        r = requests.get("https://api.upstox.com/v3/market-quote/quotes", params={"instrument_key": key},
                         headers={"Accept": "application/json", "Authorization": f"Bearer {token}"}, timeout=15)
        if r.status_code != 200:
            return None
        d = (r.json() or {}).get("data") or {}
        q = next(iter(d.values()), None)
        if not q:
            return None
        dep = q.get("depth") or {}
        bid = _f((dep.get("buy") or [{}])[0].get("price"))
        ask = _f((dep.get("sell") or [{}])[0].get("price"))
        return {"bid": bid, "ask": ask, "ltp": _f(q.get("last_price"))}
    except Exception:
        return None


def _connect():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    write, check, force = "--write" in argv, "--check" in argv, "--force" in argv
    now = datetime.now(IST)
    hm, today = now.strftime("%H:%M"), now.strftime("%Y-%m-%d")
    if not force and not (now.weekday() < 5 and "09:15" <= hm <= "15:40"):
        print(f"[PAPER] {hm} IST outside market hours")
        return 0
    token = os.environ.get("UPSTOX_ANALYTICS_TOKEN", "").strip()
    if not token:
        print("[PAPER] no token - skipped")
        return 0
    try:
        sh = _connect()
        try:
            ws = sh.worksheet(TAB)
        except Exception:
            ws = sh.add_worksheet(TAB, rows=1000, cols=len(HEAD))
            ws.update(range_name="A1", values=[HEAD])
        vals = ws.get_all_values()
        hdr = vals[0] if vals else HEAD
        ix = {c: i for i, c in enumerate(hdr)}
        rows = [r + [""] * (len(hdr) - len(r)) for r in vals[1:]]
        updates = []
        realized_today = 0.0
        # 1) manage open positions
        for n, r in enumerate(rows):
            if r[ix["Status"]] == "OPEN":
                q = quote_option(token, r[ix["Key"]])
                bid = q["bid"] if q else None
                pos = {"entry": _f(r[ix["EntryAsk"]]), "qty_open": _f(r[ix["QtyOpen"]]), "sl": _f(r[ix["SL"]]), "peak": _f(r[ix["Peak"]]) or _f(r[ix["EntryAsk"]]),
                       "partial": str(r[ix["PartialDone"]]) == "Y"}
                if not all(pos[k] is not None for k in ("entry", "qty_open", "sl")):
                    continue
                newp, sells = step_position(pos, bid, hm)
                pnl = _f(r[ix["Realized_Rs"]]) or 0.0
                qty_total = _f(r[ix["QtyTotal"]]) or 0.0
                reason = r[ix["Reason"]]
                for qty, price, why in sells:
                    pnl += (price - pos["entry"]) * qty
                    reason = (reason + " | " if reason else "") + f"{why} @ {price:.2f}"
                closed = newp["qty_open"] <= 1e-9 or any(s[0] >= pos["qty_open"] - 1e-9 for s in sells)
                if closed:
                    buy_val = pos["entry"] * qty_total
                    sell_val = buy_val + pnl
                    pnl -= cost_rs(buy_val, max(sell_val, 0))
                    r[ix["Status"]], r[ix["ExitTime"]], r[ix["ExitBid"]] = "CLOSED", now.strftime("%Y-%m-%d %H:%M"), ("" if bid is None else bid)
                    newp["qty_open"] = 0.0
                r[ix["QtyOpen"]], r[ix["SL"]], r[ix["Peak"]] = round(newp["qty_open"], 4), round(newp["sl"], 2), round(newp["peak"], 2)
                r[ix["PartialDone"]] = "Y" if newp["partial"] else ""
                r[ix["Realized_Rs"]], r[ix["Reason"]] = round(pnl, 2), reason
                updates.append(n)
                print(f"[PAPER] {r[ix['Symbol']]} {r[ix['Strike']]} CE: bid {bid} sl {r[ix['SL']]} -> {r[ix['Status']]} {reason[-60:]}")
        for r in rows:                                                    # today's realized P/L (closed today + partial profits of open ones)
            if r[ix["Date"]] == today:
                realized_today += _f(r[ix["Realized_Rs"]]) or 0.0
        # 2) record next-day bid of yesterday's contracts (carry study)
        for n, r in enumerate(rows):
            if r[ix["Status"]] == "CLOSED" and not r[ix["NextDay_Bid"]] and r[ix["Date"]] < today and hm >= "09:45":
                q = quote_option(token, r[ix["Key"]])
                if q and q["bid"] is not None:
                    r[ix["NextDay_Bid"]] = q["bid"]
                    updates.append(n)
        # 3) new entries from the system's own option alerts
        al = sh.worksheet("AlertLog").get_all_values()
        ah = al[0]
        col = {c: i for i, c in enumerate(ah)}
        seen = {(r[ix["Date"]], r[ix["Symbol"]]) for r in rows}
        early = sum(1 for r in rows if r[ix["Date"]] == today and "09:20" <= r[ix["EntryTime"]][-5:] <= EARLY_TO)
        late = sum(1 for r in rows if r[ix["Date"]] == today and LATE_FROM <= r[ix["EntryTime"]][-5:] <= LATE_TO)
        contracts = None
        new_rows = []
        for r in al[1:22]:
            r = r + [""] * (len(ah) - len(r))
            sig, status = r[col["Options Signal"]], r[col["Trade Status"]].upper()
            if "BUY CE" not in sig.upper() or "EXITED" in status or not ("TRADED" in status or (check and "WAITING" in status)):
                continue
            sym = r[col["Symbol"]].replace("NSE:", "").strip()
            if (today, sym) in seen:
                continue
            strike, exp = parse_strike(r[col["Strike"]]), parse_expiry(r[col["Expiry"]])
            ok, why = entry_allowed(hm, early, late, realized_today, _f(r[col["Priority Score"]]))
            if not ok:
                print(f"[PAPER] {sym}: not entered - {why}")
                if not check:
                    continue
            if contracts is None:
                contracts = load_contracts()
            ck = contracts.get((sym, strike, exp)) if strike and exp else None
            if not ck:
                print(f"[PAPER] {sym}: contract {strike} CE {exp} not found - skipped")
                continue
            key, lot = ck
            q = quote_option(token, key)
            if not q or not q["ask"] or not q["bid"]:
                print(f"[PAPER] {sym}: no bid/ask - skipped")
                continue
            spread = (q["ask"] - q["bid"]) / q["ask"] * 100
            if spread > MAX_SPREAD_PCT:
                print(f"[PAPER] {sym}: spread {spread:.1f}% > {MAX_SPREAD_PCT}% - skipped (illiquid)")
                continue
            open_prem = sum((_f(x[ix["EntryAsk"]]) or 0) * (_f(x[ix["QtyOpen"]]) or 0) for x in rows if x[ix["Status"]] == "OPEN") + sum(nr[9] * nr[10] for nr in new_rows)
            lots = lots_for(q["ask"], lot)
            if lots >= 1 and open_prem + q["ask"] * lot * lots > MAX_OPEN_PREMIUM:
                lots = 0
                print(f"[PAPER] {sym}: open premium {open_prem:.0f} + this lot would pass the Rs {MAX_OPEN_PREMIUM:.0f} bucket - skipped")
                continue
            if lots < 1:
                print(f"[PAPER] {sym}: one lot costs {q['ask'] * lot:.0f} > {PREMIUM_BUDGET * MAX_BUDGET_MULT:.0f} - skipped (too expensive)")
                continue
            qty = lots * lot
            row = [f"{today}-{sym}", today, sym, strike, exp, key, lot, lots, now.strftime("%Y-%m-%d %H:%M"), q["ask"], qty, qty, round(q["ask"] * (1 - SL_PCT / 100), 2),
                   q["ask"], "", round(spread, 2), "", "", "OPEN", "", "", 0, "", ""]
            new_rows.append(row)
            if EARLY_FROM <= hm <= EARLY_TO:
                early += 1
            else:
                late += 1
            print(f"[PAPER] ENTER {sym} {strike} CE {exp}: {lots} lot x {lot} at ask {q['ask']} (bid {q['bid']}, spread {spread:.1f}%), SL {row[12]}")
        if check or not write:
            print(f"[PAPER] {'CHECK' if check else 'DRY-RUN'}: {len(new_rows)} would-be entries, {len(updates)} position updates, nothing written")
            return 0
        for n in sorted(set(updates)):
            ws.update(range_name=f"A{n + 2}", values=[rows[n][:len(hdr)]], value_input_option="USER_ENTERED")
        if new_rows:
            start = len(vals) + 1
            if ws.row_count < start + len(new_rows) + 5:
                ws.add_rows(start + len(new_rows) + 5 - ws.row_count)
            ws.update(range_name=f"A{start}", values=new_rows, value_input_option="USER_ENTERED")
        print(f"[PAPER] wrote {len(set(updates))} updates + {len(new_rows)} new rows")
    except Exception as e:
        print(f"[PAPER] skipped (fail-open): {str(e)[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
