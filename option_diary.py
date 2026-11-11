"""
option_diary.py v1.0 (2026-11-11) - the OWNER'S OPTION PAPER DIARY (learning tool, paper only, observation only).
The owner types ONE line in the `OptionDiary` tab (underlying, strike, reason, optional stop / target / lots); this script then does the rest with real Upstox bid/ask (free read-only token):
  * entry = the ASK at the first tick inside 09:16-15:00 IST on the row's date (blank date = today),
  * every tick: updates the highest / lowest bid seen; exits at the BID on STOP (bid <= Stop), TARGET (bid >= Target) or TIME EXIT at 15:15 IST (intraday only, never held overnight),
  * P/L in Rs after approximate costs (Rs 40 + 0.14% of buy+sell value, same as option_paper.py),
  * `OptionDiaryStats` tab = results grouped by REASON / underlying, so a belief like 'bottom catch works' gets a real record after 30-50 trades.
Defaults when left blank: Stop = entry - 25%, Target = entry + 50%, Lots = 1, Expiry = the nearest expiry on or after the entry day.
Limits (be honest): checked once per ~5-minute tick, so a very fast spike can pass a level between ticks; call options only (the system is buy-side only).
NEVER reads or writes AlertLog / History / BotMemory, never sends a message, never places an order. Fail-open: any problem = a log line and exit 0.
USAGE: python option_diary.py --init   (creates the tabs)   |   python option_diary.py --write   (one tick; run by the price-feed session loop)   |   --force (ignore market hours)
"""
import gzip
import json
import os
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone

import pytz

import option_paper as P

IST = pytz.timezone("Asia/Kolkata")
TAB, STATS_TAB = "OptionDiary", "OptionDiaryStats"
HEAD = ["Date", "Underlying", "Strike", "Expiry", "Reason", "Lots", "Stop", "Target",
        "Status", "Entry_Time", "Entry_Ask", "Lot_Size", "Max_Seen", "Min_Seen", "Exit_Time", "Exit_Bid", "Exit_Reason", "PnL_Rs", "PnL_%", "Note"]
ENTRY_FROM, ENTRY_TO, TIME_EXIT = "09:16", "15:00", "15:15"
DEFAULT_STOP_PCT, DEFAULT_TARGET_PCT = 25.0, 50.0
CACHE = os.path.join(tempfile.gettempdir(), "upstox_diary_contracts.json")
MAX_ROWS_PER_TICK = 12


def f(x):
    return P._f(x)


def r5(x):
    """Round a premium to the 0.05 tick."""
    return round(round(x / 0.05) * 0.05, 2)


def defaults(entry_ask, stop, target):
    s = f(stop)
    t = f(target)
    if s is None:
        s = r5(entry_ask * (1 - DEFAULT_STOP_PCT / 100.0))
    if t is None:
        t = r5(entry_ask * (1 + DEFAULT_TARGET_PCT / 100.0))
    return s, t


def decide_exit(entry, stop, target, bid, hm):
    """Pure. Returns (status, reason) when an OPEN row must close at this BID, else None. hm = 'HH:MM' IST."""
    if hm >= TIME_EXIT:
        return "TIME EXIT", f"time exit {TIME_EXIT}"
    if bid is None or bid <= 0:
        return None
    if bid <= stop:
        return "STOP", "stop hit"
    if bid >= target:
        return "TARGET", "target hit"
    return None


def pnl(entry_ask, exit_bid, qty):
    """(net Rs, net % of the premium paid). Costs as in option_paper.cost_rs."""
    buy, sell = entry_ask * qty, exit_bid * qty
    net = sell - buy - P.cost_rs(buy, sell)
    return round(net, 2), (round(net / buy * 100.0, 2) if buy else 0.0)


def nearest_expiry(contracts, underlying, today):
    ex = sorted({k[2] for k in contracts if k[0] == underlying and k[2] >= today})
    return ex[0] if ex else None


def entry_window(hm):
    return ENTRY_FROM <= hm <= ENTRY_TO


def pdate(text):
    """Owner-typed date -> 'YYYY-MM-DD' (also dd/mm/yyyy as Indian sheets show it) or None."""
    t = str(text).strip()
    d = P.parse_expiry(t)
    if d:
        return d
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y"):
        try:
            return datetime.strptime(t, fmt).strftime("%Y-%m-%d")
        except Exception:
            pass
    return None


def row_inputs(rec):
    """Pure: clean the owner's typed cells. Returns None when the row is not a usable new row."""
    und = str(rec.get("Underlying", "")).strip().upper().replace("NSE:", "")
    strike = f(rec.get("Strike"))
    if not und or strike is None:
        return None
    lots = f(rec.get("Lots"))
    return {"und": und, "strike": strike, "expiry": pdate(rec.get("Expiry", "")) if str(rec.get("Expiry", "")).strip() else None,
            "lots": int(lots) if lots and lots >= 1 else 1, "stop": rec.get("Stop"), "target": rec.get("Target")}


def stats(rows):
    """Pure. rows = list of dicts with Status, Reason, Underlying, PnL_Rs, PnL_%. Closed rows only (STOP/TARGET/TIME EXIT)."""
    closed = [r for r in rows if str(r.get("Status")) in ("STOP", "TARGET", "TIME EXIT") and f(r.get("PnL_Rs")) is not None]

    def block(items):
        n = len(items)
        if not n:
            return None
        w = [x for x in items if f(x["PnL_Rs"]) > 0]
        return {"n": n, "win_pct": round(len(w) / n * 100), "avg_pct": round(sum(f(x["PnL_%"]) or 0 for x in items) / n, 2),
                "net": round(sum(f(x["PnL_Rs"]) for x in items))}
    out = {"ALL": block(closed), "by_reason": {}, "by_underlying": {}}
    g1, g2 = defaultdict(list), defaultdict(list)
    for r in closed:
        g1[str(r.get("Reason", "")).strip().lower() or "(no reason)"].append(r)
        g2[str(r.get("Underlying", "")).strip().upper()].append(r)
    out["by_reason"] = {k: block(v) for k, v in g1.items()}
    out["by_underlying"] = {k: block(v) for k, v in g2.items()}
    return out


def load_contracts(today):
    """{(underlying, strike, 'YYYY-MM-DD'): (instrument_key, lot_size)} for NSE + BSE call options (stocks, NIFTY, BANKNIFTY, SENSEX, BANKEX), cached per day."""
    try:
        if os.path.exists(CACHE):
            c = json.load(open(CACHE, encoding="utf-8"))
            if c.get("date") == today and c.get("map"):
                return {tuple(json.loads(k)): tuple(v) for k, v in c["map"].items()}
    except Exception:
        pass
    import requests
    m = {}
    for exch, seg in (("NSE", "NSE_FO"), ("BSE", "BSE_FO")):
        try:
            r = requests.get(f"https://assets.upstox.com/market-quote/instruments/exchange/{exch}.json.gz", timeout=60)
            r.raise_for_status()
            for x in json.loads(gzip.decompress(r.content).decode("utf-8")):
                if x.get("segment") == seg and x.get("instrument_type") == "CE" and x.get("underlying_symbol") and x.get("expiry") and x.get("strike_price") is not None:
                    d = datetime.fromtimestamp(x["expiry"] / 1000, timezone.utc).strftime("%Y-%m-%d")
                    m[(x["underlying_symbol"], float(x["strike_price"]), d)] = (x["instrument_key"], int(x.get("lot_size") or 0))
        except Exception as e:
            print(f"[DIARY] {exch} contracts failed ({str(e)[:80]})")
    if len(m) < 1000:
        return {}
    json.dump({"date": today, "map": {json.dumps(list(k)): list(v) for k, v in m.items()}}, open(CACHE, "w", encoding="utf-8"))
    return m


def ensure_tabs(sh):
    try:
        ws = sh.worksheet(TAB)
    except Exception:
        ws = sh.add_worksheet(TAB, rows=500, cols=len(HEAD))
        ws.update(range_name="A1", values=[HEAD])
        ws.update(range_name="A2", values=[["", "SENSEX", 82600, "", "example - delete this row", 1, "", "", "EXAMPLE", "", "", "", "", "", "", "", "",
                                            "", "", "Fill columns A-H only (Underlying and Strike are required). Everything from Status on is filled by the robot. Delete this row."]])
    try:
        sh.worksheet(STATS_TAB)
    except Exception:
        sh.add_worksheet(STATS_TAB, rows=60, cols=6)
    return ws


def write_stats(sh, rows):
    st = stats(rows)
    vals = [["OPTION DIARY RESULTS (paper, closed trades only)", "Trades", "Win %", "Avg % of premium", "Net Rs (after costs)"]]

    def line(label, b):
        return [label, b["n"], b["win_pct"], b["avg_pct"], b["net"]] if b else [label, 0, "", "", ""]
    vals.append(line("ALL", st["ALL"]))
    vals.append(["", "", "", "", ""])
    vals.append(["BY REASON", "Trades", "Win %", "Avg %", "Net Rs"])
    for k, b in sorted(st["by_reason"].items(), key=lambda kv: -(kv[1]["n"] if kv[1] else 0)):
        vals.append(line(k, b))
    vals.append(["", "", "", "", ""])
    vals.append(["BY UNDERLYING", "Trades", "Win %", "Avg %", "Net Rs"])
    for k, b in sorted(st["by_underlying"].items(), key=lambda kv: -(kv[1]["n"] if kv[1] else 0)):
        vals.append(line(k, b))
    vals.append(["", "", "", "", ""])
    vals.append(["Read this honestly: fewer than 30 trades per reason is NOT enough to call it an edge. Updated " + datetime.now(IST).strftime("%Y-%m-%d %H:%M") + " IST", "", "", "", ""])
    ws = sh.worksheet(STATS_TAB)
    ws.clear()
    ws.update(range_name="A1", values=vals)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    write, force, init = "--write" in argv, "--force" in argv, "--init" in argv
    now = datetime.now(IST)
    hm, today = now.strftime("%H:%M"), now.strftime("%Y-%m-%d")
    try:
        sh = P._connect()
        if init:
            ensure_tabs(sh)
            print("[DIARY] tabs ready")
            return 0
        if not force and (P._is_holiday() or not (now.weekday() < 5 and "09:15" <= hm <= "15:40")):
            print(f"[DIARY] {hm} IST outside market hours")
            return 0
        ws = sh.worksheet(TAB)
        vals = ws.get_all_values()
        if len(vals) < 2:
            return 0
        head = vals[0]
        col = {h: i for i, h in enumerate(head)}
        if any(h not in col for h in HEAD):
            print("[DIARY] header mismatch - nothing done")
            return 0
        recs = [(i + 2, {h: (r[col[h]] if col[h] < len(r) else "") for h in HEAD}) for i, r in enumerate(vals[1:])]
        todo = [(n, rec) for n, rec in recs if str(rec["Status"]).strip() == "" or str(rec["Status"]).strip() == "OPEN"]
        if not todo:
            return 0
        token = os.environ.get("UPSTOX_ANALYTICS_TOKEN", "").strip()
        if not token:
            print("[DIARY] no UPSTOX_ANALYTICS_TOKEN - nothing done")
            return 0
        contracts = load_contracts(today)
        if not contracts:
            print("[DIARY] no contract list - nothing done")
            return 0
        from gspread.utils import rowcol_to_a1
        updates, changed_exit = [], False

        def put(n, name, value):
            updates.append({"range": rowcol_to_a1(n, col[name] + 1), "values": [[value]]})

        done = 0
        for n, rec in todo:
            if done >= MAX_ROWS_PER_TICK:
                break
            status = str(rec["Status"]).strip()
            d = str(rec["Date"]).strip() or today
            d = pdate(d) or today
            if status == "":
                inp = row_inputs(rec)
                if not inp:
                    continue
                if d > today:
                    continue
                if d < today:
                    put(n, "Status", "SKIPPED: old date")
                    continue
                if not entry_window(hm) and not force:
                    if hm > ENTRY_TO:
                        put(n, "Status", "SKIPPED: missed the entry window today")
                    continue
                exp = inp["expiry"] or nearest_expiry(contracts, inp["und"], today)
                c = contracts.get((inp["und"], inp["strike"], exp)) if exp else None
                if not c:
                    put(n, "Status", "SKIPPED: no such contract")
                    put(n, "Note", f"{inp['und']} {inp['strike']:g} CE {exp or ''} not in the F&O list (strike or expiry wrong)")
                    continue
                q = P.quote_option(token, c[0])
                done += 1
                if not q or not q.get("ask") or q["ask"] <= 0:
                    continue          # retry next tick
                ask = q["ask"]
                stop, target = defaults(ask, inp["stop"], inp["target"])
                put(n, "Status", "OPEN")
                put(n, "Expiry", exp)
                put(n, "Date", today)
                put(n, "Lots", inp["lots"])
                put(n, "Stop", stop)
                put(n, "Target", target)
                put(n, "Entry_Time", now.strftime("%H:%M"))
                put(n, "Entry_Ask", ask)
                put(n, "Lot_Size", c[1])
                put(n, "Max_Seen", q.get("bid") or ask)
                put(n, "Min_Seen", q.get("bid") or ask)
                print(f"[DIARY] ENTRY {inp['und']} {inp['strike']:g} CE {exp} ask {ask} stop {stop} target {target} lots {inp['lots']}")
            else:   # OPEN
                inp = row_inputs(rec)
                if not inp:
                    continue
                if d < today:
                    put(n, "Status", "STALE")
                    put(n, "Note", "no exit was recorded on its day (not scored)")
                    continue
                exp = pdate(rec["Expiry"]) or inp["expiry"]
                c = contracts.get((inp["und"], inp["strike"], exp))
                if not c:
                    continue
                q = P.quote_option(token, c[0])
                done += 1
                bid = (q or {}).get("bid")
                entry, stop, target = f(rec["Entry_Ask"]), f(rec["Stop"]), f(rec["Target"])
                if entry is None or stop is None or target is None:
                    continue
                if bid and bid > 0:
                    mx, mn = f(rec["Max_Seen"]), f(rec["Min_Seen"])
                    if mx is None or bid > mx:
                        put(n, "Max_Seen", bid)
                    if mn is None or bid < mn:
                        put(n, "Min_Seen", bid)
                res = decide_exit(entry, stop, target, bid, hm)
                if res:
                    ex_bid = bid if (bid and bid > 0) else 0.0
                    qty = (int(f(rec["Lots"]) or 1)) * (int(f(rec["Lot_Size"]) or 0))
                    net, pct = pnl(entry, ex_bid, qty)
                    put(n, "Status", res[0])
                    put(n, "Exit_Time", now.strftime("%H:%M"))
                    put(n, "Exit_Bid", ex_bid)
                    put(n, "Exit_Reason", res[1])
                    put(n, "PnL_Rs", net)
                    put(n, "PnL_%", pct)
                    changed_exit = True
                    print(f"[DIARY] EXIT {inp['und']} {inp['strike']:g} CE {res[0]} bid {ex_bid} net Rs {net}")
        if updates and write:
            ws.batch_update(updates, value_input_option="RAW")
        elif updates:
            print(f"[DIARY] dry run: {len(updates)} cell update(s) not written (use --write)")
        if write and (changed_exit or "15:20" <= hm <= "15:29"):
            fresh = ws.get_all_values()
            hr = fresh[0]
            rows = [{h: (r[hr.index(h)] if hr.index(h) < len(r) else "") for h in HEAD} for r in fresh[1:]]
            write_stats(sh, rows)
    except Exception as e:
        print(f"[DIARY] skipped (fail-open): {str(e)[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
