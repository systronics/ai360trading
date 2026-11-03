"""
result_runup.py v1.0 (2026-11-03) — OBSERVATION-ONLY "Result Run-up" list + paper tracker.

WHY (owner 2026-11-03: big movers keep escaping our trend gates; "how do we catch the run-up before results?"): a 2022-2026 test on 152 result
reaction days (dates inferred from volume spikes, so approximate) showed that holding 3-5 trading days BEFORE the result and selling the day
BEFORE it averaged +1.25% / +1.50% (win 67%) when the stock was above its 50-DMA, vs +0.38% for a random 5-day hold, and about 0 / -0.4% when it
was below the 50-DMA. RS>=5 added a little. Small, noisy sample; costs ~0.2-0.3%. So this module only LISTS and PAPER-TRACKS it to build real evidence.

NEVER read by trading_bot.py, appscript.gs, any gate, alert or ledger. Fail-open. Rules (all checked on yesterday's/live data, nothing predicted):
  candidate = result date 2-5 trading days away (BotMemory EARNINGS_<SYM>_<date>, from fetch_earnings.py) AND CMP above the 50-DMA
  Grade A = candidate + RS >= 5 + RSI(14) <= 65     Grade B = candidate only
  plan = look at the chart; planned exit = close of the trading day BEFORE the result day; NEVER hold through the result (reaction day averages 7% either way)
Tabs: `ResultRunup` (today's list, overwritten) and `RunupWatch` (paper log, appended once per symbol+result date, scored after the result date).

USAGE: python result_runup.py            dry-run (prints)
       python result_runup.py --write    write both tabs
       python result_runup.py --report   read-only summary of RunupWatch
"""
import os
import re
import sys
import json
import time
import datetime as dt

import pytz

IST = pytz.timezone("Asia/Kolkata")
VERSION = "v1.0"
SHEET = "Ai360tradingAlgo"
LIST_TAB, WATCH_TAB = "ResultRunup", "RunupWatch"
MIN_D, MAX_D = 2, 5
WATCH_HEAD = ["Logged_On", "Symbol", "Result_Date", "Grade", "Days_To_Result", "Entry_Price", "RS", "RSI14", "Exit_Date", "Exit_Price",
              "Runup_%", "Result_Day_%", "Scored"]
LIST_HEAD = ["Symbol", "Result_Date", "Trading_Days_Left", "Grade", "CMP", "%Chg", "RS", "RSI14", "%_above_50DMA", "F&O?", "Sector", "Why"]


# ──────────────── pure logic (unit-tested) ────────────────

def rsi14(closes):
    """Simple-mean RSI(14) of a list of closes (same definition as our other tools). None if too short."""
    if len(closes) < 16:
        return None
    ch = [closes[i] - closes[i - 1] for i in range(len(closes) - 14, len(closes))]
    up = sum(x for x in ch if x > 0) / 14.0
    dn = sum(-x for x in ch if x < 0) / 14.0
    return 100.0 if dn == 0 else 100.0 - 100.0 / (1.0 + up / dn)


def trading_days_between(d0, d1, holidays=frozenset()):
    """Number of trading days after d0 up to and including d1 (Mon-Fri, minus holidays). d1 <= d0 -> 0."""
    n, d = 0, d0
    while d < d1:
        d += dt.timedelta(days=1)
        if d.weekday() < 5 and d not in holidays:
            n += 1
    return n


def grade(above50, rs, rsi):
    """A = above 50-DMA + RS>=5 + RSI<=65;  B = above 50-DMA only;  '' = not a candidate."""
    if not above50:
        return ""
    if rs is not None and rs >= 5 and rsi is not None and rsi <= 65:
        return "A"
    return "B"


def prev_trading_day(d, holidays=frozenset()):
    d = d - dt.timedelta(days=1)
    while d.weekday() >= 5 or d in holidays:
        d -= dt.timedelta(days=1)
    return d


# ──────────────── sheet / data ────────────────

def _connect():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        raw = open("service_account.json").read()
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open(SHEET)


def _holidays():
    try:
        import indian_holidays
        out = set()
        for h in indian_holidays._get_holiday_set():
            out.add(h if isinstance(h, dt.date) else dt.date.fromisoformat(str(h)[:10]))
        return out
    except Exception as e:
        print(f"[CAL] holiday list unavailable ({str(e)[:80]}), weekends only")
        return set()


def _num(x):
    try:
        return float(str(x).replace(",", ""))
    except Exception:
        return None


def load_events(sh):
    ev = {}
    for r in sh.worksheet("BotMemory").get_all_values():
        m = re.match(r"EARNINGS_(.+)_(\d{4}-\d{2}-\d{2})$", r[0] if r else "")
        if m:
            ev.setdefault(m.group(1), []).append(dt.date.fromisoformat(m.group(2)))
    return ev


def _closes(symbols):
    import yfinance as yf
    out = {}
    if not symbols:
        return out
    try:
        df = yf.download([s + ".NS" for s in symbols], period="4mo", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
        for s in symbols:
            try:
                x = df[s + ".NS"].dropna(subset=["Close"])
                x.index = (x.index.tz_localize(None) if x.index.tz is not None else x.index).normalize()
                out[s] = x
            except Exception:
                continue
    except Exception as e:
        print(f"[YF] unavailable (fail-open): {str(e)[:100]}")
    return out


def candidates(sh, today, hol):
    n = sh.worksheet("Nifty200").get_all_values()
    h = [x.strip() for x in n[0]]
    ix = {k: h.index(k) for k in ("CMP", "%Change", "50_DMA", "RS", "SECTOR", "Options")}
    ev = load_events(sh)
    raw = []
    for r in n[2:]:
        s = r[0].replace("NSE:", "").strip()
        for e in ev.get(s, []):
            k = trading_days_between(today, e, hol)
            if MIN_D <= k <= MAX_D:
                cmp_, dma = _num(r[ix["CMP"]]), _num(r[ix["50_DMA"]])
                if cmp_ and dma:
                    raw.append(dict(sym=s, E=e, k=k, cmp=cmp_, chg=_num(r[ix["%Change"]]), dma=dma, rs=_num(r[ix["RS"]]),
                                    sector=r[ix["SECTOR"]], fo=r[ix["Options"]]))
    cl = _closes(sorted({x["sym"] for x in raw if x["cmp"] > x["dma"]}))
    out = []
    for x in raw:
        above = x["cmp"] > x["dma"]
        c = cl.get(x["sym"])
        rsi = rsi14([float(v) for v in c["Close"].tolist()]) if (c is not None and len(c)) else None
        g = grade(above, x["rs"], rsi)
        if not g:
            continue
        x.update(rsi=rsi, grade=g, above_pct=(x["cmp"] / x["dma"] - 1) * 100)
        x["why"] = ("above 50-DMA, RS>=5, RSI<=65 (best bucket in the test)" if g == "A"
                    else "above 50-DMA only" + (" (RS<5)" if (x["rs"] is not None and x["rs"] < 5) else "") + (" (RSI>65)" if (rsi and rsi > 65) else ""))
        out.append(x)
    out.sort(key=lambda z: (z["E"], z["grade"], -(z["rs"] or -99)))
    return out


def write_list(sh, cands, today):
    import gspread
    try:
        ws = sh.worksheet(LIST_TAB)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(LIST_TAB, rows=80, cols=len(LIST_HEAD))
    note = ["RESULT RUN-UP LIST (sirf jaankari, entry signal NAHI). Result 2-5 trading din door + 50-DMA ke upar. Grade A = RS>=5 aur RSI<=65.",
            "Plan: chart dekho, result se ek din PEHLE nikal jao, result ke saath kabhi mat raho (result wale din ka औसत move 7%, dono taraf). "
            "2022-26 test: 50-DMA ke upar wale ka 5-din run-up औसत +1.5% (jeet 67%) vs random +0.4%; neeche wale ka -0.4%. Sample chhota (152), kharcha ~0.2-0.3%."]
    rows = [[c["sym"], c["E"].isoformat(), c["k"], c["grade"], c["cmp"], c["chg"], c["rs"], round(c["rsi"], 1) if c["rsi"] is not None else "",
             round(c["above_pct"], 1), c["fo"], c["sector"], c["why"]] for c in cands]
    ws.update(range_name="A1", values=[[note[0]], [note[1]], [f"Updated {dt.datetime.now(IST):%Y-%m-%d %H:%M IST} | {len(rows)} candidates"], LIST_HEAD] + rows)
    ws.format("A1:A3", {"textFormat": {"bold": True}})
    ws.format("A4:L4", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.88, "green": 0.92, "blue": 0.98}})
    print(f"[LIST] wrote {len(rows)} rows to {LIST_TAB}")


def watch_log_and_score(sh, cands, today, hol):
    import gspread
    try:
        ws = sh.worksheet(WATCH_TAB)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(WATCH_TAB, rows=500, cols=len(WATCH_HEAD))
        ws.update(range_name="A1", values=[WATCH_HEAD])
    v = ws.get_all_values()
    have = {(r[1], r[2]) for r in v[1:] if len(r) > 2}
    fresh = [[today.isoformat(), c["sym"], c["E"].isoformat(), c["grade"], c["k"], c["cmp"], c["rs"], round(c["rsi"], 1) if c["rsi"] is not None else "",
              "", "", "", "", ""] for c in cands if (c["sym"], c["E"].isoformat()) not in have]
    if fresh:
        start = len(v) + 1
        if ws.row_count < start + len(fresh) + 5:
            ws.add_rows(start + len(fresh) + 5 - ws.row_count)
        ws.update(range_name=f"A{start}", values=fresh, value_input_option="USER_ENTERED")
        print(f"[WATCH] logged {len(fresh)} new paper candidates")
    # score rows whose result date has passed
    v = ws.get_all_values()
    todo = [(i, r) for i, r in enumerate(v[1:], start=2) if len(r) >= 13 and r[12] == "" and r[2] and dt.date.fromisoformat(r[2]) < today]
    if not todo:
        return
    cl = _closes(sorted({r[1] for _, r in todo}))
    body = []
    for i, r in todo:
        x = cl.get(r[1])
        if x is None:
            continue
        E = dt.date.fromisoformat(r[2])
        ex = prev_trading_day(E, hol)
        try:
            ep = float(x.loc[pd_ts(ex), "Close"])
            res = float(x.loc[pd_ts(E), "Close"]) / ep * 100 - 100
            ent = float(r[5])
            body += [{"range": f"I{i}:M{i}", "values": [[ex.isoformat(), round(ep, 2), round((ep / ent - 1) * 100, 2), round(res, 2), "Y"]]}]
        except Exception:
            continue
    for k in range(0, len(body), 100):
        ws.batch_update(body[k:k + 100], value_input_option="USER_ENTERED")
        time.sleep(1)
    print(f"[WATCH] scored {len(body)} rows")


def pd_ts(d):
    import pandas as pd
    return pd.Timestamp(d)


def report(sh):
    v = sh.worksheet(WATCH_TAB).get_all_values()
    rows = [r for r in v[1:] if len(r) >= 13 and r[12] == "Y"]
    print(f"[REPORT] {len(v) - 1} logged, {len(rows)} scored")
    for g in ("A", "B"):
        x = [float(r[10]) for r in rows if r[3] == g and r[10] != ""]
        if x:
            print(f"  Grade {g}: n={len(x)} avg run-up {sum(x) / len(x):+.2f}% win {sum(1 for t in x if t > 0) * 100 // len(x)}%")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    sh = _connect()
    if "--report" in argv:
        return report(sh)
    today = dt.datetime.now(IST).date()
    hol = _holidays()
    print(f"[result_runup {VERSION}] {today} mode={'WRITE' if '--write' in argv else 'DRY-RUN'}")
    try:
        c = candidates(sh, today, hol)
        print(f"[CAND] {len(c)} candidates ({sum(1 for x in c if x['grade'] == 'A')} grade A)")
        for x in c[:25]:
            print(f"  {x['E']} k={x['k']} {x['sym']:12} {x['grade']} RS {x['rs']} RSI {None if x['rsi'] is None else round(x['rsi'])} {x['why']}")
        if "--write" in argv:
            write_list(sh, c, today)
            watch_log_and_score(sh, c, today, hol)
    except Exception as e:
        print(f"[result_runup] skipped (fail-open): {str(e)[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
