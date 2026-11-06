"""
gainers_log.py v1.0 (2026-11-05) — OBSERVATION-ONLY daily record of the day's top gainers and WHY our system did or did not catch them.

WHY (owner 2026-11-05: 'are you checking the top gainers daily, so later we can build the automation better'): until now this was done by hand when asked.
Every trading day this appends the day's top-15 gainers (Nifty200 + F&O universe, from the GateAudit tab) to the new `GainersLog` tab with what we knew the evening before:
RS35, above 50-DMA, RSI, which gates they passed, a category (LEADER / LAGGARD-BOUNCE / TREND-OTHER), whether a result was due within +-5 days (BotMemory EARNINGS_*),
and whether the paper system took a trade in it that day (History). `--report` gives the rolling split so that later rule changes rest on 4-6 weeks of real days, not one screenshot.

Never read by trading_bot.py / appscript.gs / any gate or alert. Idempotent per (date, symbol). Fail-open (any error = nothing written).
USAGE: python gainers_log.py [--date YYYY-MM-DD] [--backfill N] [--write]      |      python gainers_log.py --report
"""
import os
import re
import sys
import json
import time
import datetime as dt

TAB = "GainersLog"
HEAD = ["Date", "Rank", "Symbol", "Day_%", "Gap_%", "Prev_RS35", "Prev_Above_50DMA", "Prev_RSI14", "G_RS", "G_Trend", "G_RSI", "G_Leader", "Category",
        "Result_Within_5d", "Prev_Buildup", "Taken_By_System", "Universe_Avg_Day_%", "Sector", "Sector_Avg_Day_%",
        "Scan_First_Status", "Scan_Last_Status", "Scan_Gate_Counts"]
TOP_N = 15


def _f(x):
    try:
        return float(str(x).replace(",", "").replace("%", ""))
    except Exception:
        return None


def categorize(rs, above50, g_leader):
    """LEADER = passed our full leader filter the evening before; LAGGARD-BOUNCE = RS < 0 and below its 50-DMA; TREND-OTHER = everything else."""
    if g_leader == "Y":
        return "LEADER"
    if rs is not None and rs < 0 and above50 == "N":
        return "LAGGARD-BOUNCE"
    return "TREND-OTHER"


def result_near(events, sym, day, window=5):
    return any(abs((d - day).days) <= window for d in events.get(sym, []))


def scan_cols(scan, sym, day):
    """[first, last, gate counts] from the live scanner's ScanReasons tab for this symbol and day. 'not in scanner' when the stock is outside the Nifty200 scan,
    'no scan data for this day' when the tab holds another date (it keeps only the latest market day)."""
    if not scan:
        return ["scan history not recorded yet", "", ""]
    r = scan.get(sym)
    if r is None:
        return ["not in the live scan (outside Nifty200 or none recorded)", "", ""]
    if str(r.get("Date", "")) != day:
        return ["no scan data for this day (tab holds " + str(r.get("Date", "?")) + ")", "", ""]
    return [r.get("First_Status", ""), r.get("Last_Status", ""), r.get("Gate_Counts", "")]


def top_gainers(rows, day, n=TOP_N):
    """rows: list of dicts for one date. Returns the n biggest Day_% (descending)."""
    ok = [r for r in rows if _f(r.get("Day_%")) is not None]
    return sorted(ok, key=lambda r: -_f(r["Day_%"]))[:n]


def _connect():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")


def _events(sh):
    ev = {}
    for r in sh.worksheet("BotMemory").get_all_values():
        m = re.match(r"EARNINGS_(.+)_(\d{4}-\d{2}-\d{2})$", r[0] if r else "")
        if m:
            ev.setdefault(m.group(1), []).append(dt.date.fromisoformat(m.group(2)))
    return ev


def _taken(sh):
    """{symbol: [(entry_date, exit_date)]} from History (closed paper trades)."""
    out = {}
    try:
        v = sh.worksheet("History").get_all_values()
        h = v[0]
        for r in v[1:]:
            try:
                s = r[h.index("Symbol")].replace("NSE:", "").strip()
                out.setdefault(s, []).append((r[h.index("Entry Date")][:10], r[h.index("Exit Date")][:10]))
            except Exception:
                continue
    except Exception:
        pass
    return out


def build_rows(ga_rows, day, prev_day, events, taken, sectors=None, scan=None):
    today = [r for r in ga_rows if r["Date"] == day]
    prev = {r["Symbol"]: r for r in ga_rows if r["Date"] == prev_day}
    avg = [_f(r["Day_%"]) for r in today if _f(r["Day_%"]) is not None]
    uavg = round(sum(avg) / len(avg), 2) if avg else ""
    d0 = dt.date.fromisoformat(day)
    sectors = sectors or {}
    scan = scan or {}
    sec_moves = {}
    for r in today:      # average day move of each sector's stocks (Nifty200 members only) - shows whether the gainers cluster in one sector
        sc = sectors.get(r["Symbol"])
        v = _f(r.get("Day_%"))
        if sc and v is not None:
            sec_moves.setdefault(sc, []).append(v)
    out = []
    for rank, r in enumerate(top_gainers(today, day), start=1):
        s = r["Symbol"]
        p = prev.get(s, {})
        rs = _f(p.get("RS35"))
        cat = categorize(rs, p.get("Above_50DMA"), p.get("G_Leader")) if p else "NO-PRIOR-DATA"
        was = "Y" if any(a <= day <= b or a == day for a, b in taken.get(s, [])) else "N"
        out.append([day, rank, s, r["Day_%"], r.get("Gap_%", ""), p.get("RS35", ""), p.get("Above_50DMA", ""), p.get("RSI14", ""), p.get("G_RS", ""), p.get("G_Trend", ""),
                    p.get("G_RSI", ""), p.get("G_Leader", ""), cat, "Y" if result_near(events, s, d0) else "N", p.get("Buildup", ""), was, uavg,
                    sectors.get(s, ""), round(sum(sec_moves[sectors[s]]) / len(sec_moves[sectors[s]]), 2) if sectors.get(s) in sec_moves else "",
                    *scan_cols(scan, s, day)])
    return out


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    sh = _connect()
    if "--report" in argv:
        return report(sh)
    v = sh.worksheet("GateAudit").get_all_values()
    h = v[0]
    ga = [dict(zip(h, r)) for r in v[1:] if r and r[0]]
    dates = sorted({r["Date"] for r in ga})
    if "--date" in argv:
        pick = [argv[argv.index("--date") + 1]]
    else:
        n = int(argv[argv.index("--backfill") + 1]) if "--backfill" in argv else 1
        pick = dates[-n:]
    events, taken = _events(sh), _taken(sh)
    try:
        nv = sh.worksheet("Nifty200").get_all_values()
        sectors = {r[0].replace("NSE:", "").strip(): r[1] for r in nv[2:] if r and r[0] and len(r) > 1 and r[1]}
    except Exception:
        sectors = {}
    try:
        scan = {}
        sv = sh.worksheet("ScanReasons").get_all_values()
        sh_ = sv[0]
        for r in sv[1:]:
            if len(r) >= 2 and r[1]:
                scan[r[1].replace("NSE:", "").strip()] = dict(zip(sh_, r))
    except Exception:
        scan = {}
    try:
        ws = sh.worksheet(TAB)
    except Exception:
        if "--write" not in argv:
            ws = None
        else:
            ws = sh.add_worksheet(TAB, rows=2000, cols=len(HEAD))
            ws.update(range_name="A1", values=[HEAD])
    if ws is not None and "--write" in argv:
        try:
            hdr = ws.row_values(1)
            if len(hdr) < len(HEAD):
                if ws.col_count < len(HEAD):
                    ws.add_cols(len(HEAD) - ws.col_count)
                ws.update(range_name="A1", values=[HEAD])
        except Exception as e:
            print(f"[GAINERS] header update skipped: {e}")
    have = set()
    if ws is not None:
        existing = ws.get_all_values()
        have = {(r[0], r[2]) for r in existing[1:] if len(r) > 2}
    fresh = []
    for day in pick:
        i = dates.index(day) if day in dates else -1
        if i < 1:
            print(f"[GAINERS] {day}: no earlier day in GateAudit, skipped")
            continue
        for r in build_rows(ga, day, dates[i - 1], events, taken, sectors, scan):
            if (r[0], r[2]) not in have:
                fresh.append(r)
    print(f"[GAINERS] {len(fresh)} new rows for {pick}")
    for r in fresh[:6]:
        print("   ", r[:13])
    if "--write" in argv and fresh and ws is not None:
        start = len(ws.get_all_values()) + 1
        if ws.row_count < start + len(fresh) + 5:
            ws.add_rows(start + len(fresh) + 5 - ws.row_count)
        ws.update(range_name=f"A{start}", values=fresh, value_input_option="USER_ENTERED")
        print(f"[GAINERS] wrote {len(fresh)} rows")
    return 0


def report(sh):
    v = sh.worksheet(TAB).get_all_values()
    rows = v[1:]
    if not rows:
        print("[GAINERS] empty")
        return 0
    h = v[0]
    ix = {k: h.index(k) for k in HEAD if k in h}
    days = sorted({r[0] for r in rows})
    n = len(rows)
    print(f"[GAINERS REPORT] {len(days)} days, {n} top-gainer rows ({days[0]} .. {days[-1]})")
    for key, label in (("Category", "category"), ("Result_Within_5d", "result within 5 days"), ("Taken_By_System", "paper trade taken")):
        cnt = {}
        for r in rows:
            cnt[r[ix[key]]] = cnt.get(r[ix[key]], 0) + 1
        print(f"  by {label}: " + ", ".join(f"{k or '-'} {c} ({c * 100 // n}%)" for k, c in sorted(cnt.items(), key=lambda kv: -kv[1])))
    if "Sector" in ix:
        top = {}
        for r in rows:
            if r[ix["Sector"]]:
                top[r[ix["Sector"]]] = top.get(r[ix["Sector"]], 0) + 1
        tot = sum(top.values()) or 1
        print("  top-gainer rows by sector: " + ", ".join(f"{k} {c} ({c * 100 // tot}%)" for k, c in sorted(top.items(), key=lambda kv: -kv[1])[:6]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
