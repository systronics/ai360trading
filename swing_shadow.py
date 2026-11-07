"""
swing_shadow.py v1.0 (2026-11-07) - OBSERVATION-ONLY shadow tracker (new `SwingShadow` tab): what would a plain 20-day / 40-day hold have done on every LIVE swing/positional paper trade?

WHY: the 2018-26 swing backtest (swing_bt.py, commits 6d0c198c / b6c975a3) found that for the Top-picks signal a plain time exit beat every stop/target variant (hold-20 +2.10%/trade, the live-like 2-ATR stop + 3.8-ATR target only +0.52%),
and that stops did not shrink the worst trades. The live bot exits with its own TSL / time stop / DMA stop, so the backtest cannot say how the LIVE exits compare. This records, per live trade, the live P/L next to the plain-hold P/L
(same entry price, close of trading day 20 / 40 counting the entry day as day 1) and how far the stock rose in the 10 sessions after the live exit ('left on the table'). After 20+ trades the comparison is real-world evidence.
It reads History (closed trades) and AlertLog (open trades) and writes ONLY the SwingShadow tab. No gate, alert, exit or ledger reads it. Fail-open. Percentages are gross (no costs) on both sides.
USAGE: python swing_shadow.py [--write]      |      python swing_shadow.py --report
"""
import json
import os
import sys
from datetime import date, datetime, timedelta

TAB = "SwingShadow"
HEAD = ["Symbol", "Entry_Date", "Entry_Price", "Type", "Status", "Live_Exit_Date", "Live_Exit_Price", "Live_PnL_%", "Live_Reason", "Hold20_Date", "Hold20_Close", "Hold20_%",
        "Hold40_Date", "Hold40_Close", "Hold40_%", "PostExit10d_High_%", "Updated"]


def _f(x):
    try:
        v = float(str(x).replace(",", "").replace("%", "").strip())
        return v if v == v else None
    except Exception:
        return None


def _d(x):
    try:
        return datetime.strptime(str(x).strip()[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def score_hold(dates, closes, entry_date, entry_price, k):
    """Close of trading day k (the entry day counts as day 1) vs the entry price. dates ascending (date objects). Returns (date, close, pct) or None when not enough days exist yet. Pure."""
    if not entry_price or entry_price <= 0:
        return None
    i0 = next((i for i, d in enumerate(dates) if d >= entry_date), None)
    if i0 is None or i0 + k - 1 >= len(dates):
        return None
    j = i0 + k - 1
    return dates[j], float(closes[j]), round((float(closes[j]) / entry_price - 1) * 100, 2)


def post_exit_high(dates, highs, exit_date, exit_price, n=10):
    """Highest high in the n sessions AFTER the exit date, as % above the exit price (how much the live exit left on the table). None when no later bars. Pure."""
    if not exit_price or exit_price <= 0:
        return None
    later = [h for d, h in zip(dates, highs) if d > exit_date][:n]
    return round((max(later) / exit_price - 1) * 100, 2) if later else None


def _connect():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")


def live_trades(sh):
    """[(symbol, entry_date, entry_price, type, status, exit_date, exit_price, pnl, reason)] for swing/positional trades (closed from History, open from AlertLog)."""
    out = []
    v = sh.worksheet("History").get_all_values()
    h = v[0]
    ix = {k: h.index(k) for k in ("Symbol", "Entry Date", "Entry Price", "Exit Date", "Exit Price", "P/L %", "Exit Reason", "Trade Type")}
    for r in v[1:]:
        r = r + [""] * (len(h) - len(r))
        tt = str(r[ix["Trade Type"]]).upper()
        if "SWING" in tt or "POSITIONAL" in tt:
            out.append((r[ix["Symbol"]].replace("NSE:", "").strip(), _d(r[ix["Entry Date"]]), _f(r[ix["Entry Price"]]), r[ix["Trade Type"]].strip(), "CLOSED",
                        _d(r[ix["Exit Date"]]), _f(r[ix["Exit Price"]]), _f(r[ix["P/L %"]]), r[ix["Exit Reason"]].strip()))
    a = sh.worksheet("AlertLog").get_all_values()
    ah = a[0]
    ci = {k: ah.index(k) for k in ("Symbol", "Trade Type", "Trade Status", "Entry Price", "Entry Time")}
    for r in a[1:22]:
        r = r + [""] * (len(ah) - len(r))
        tt, st = str(r[ci["Trade Type"]]).upper(), str(r[ci["Trade Status"]]).upper()
        if ("SWING" in tt or "POSITIONAL" in tt) and "TRADED" in st and "EXITED" not in st:
            out.append((r[ci["Symbol"]].replace("NSE:", "").strip(), _d(r[ci["Entry Time"]]), _f(r[ci["Entry Price"]]), r[ci["Trade Type"]].strip(), "OPEN", None, None, None, ""))
    return [t for t in out if t[0] and t[1] and t[2]]


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    try:
        sh = _connect()
        if "--report" in argv:
            return report(sh)
        import yfinance as yf
        trades = live_trades(sh)
        print(f"[SHADOW] {len(trades)} live swing/positional trades (closed + open)")
        try:
            ws = sh.worksheet(TAB)
        except Exception:
            ws = sh.add_worksheet(TAB, rows=500, cols=len(HEAD))
            ws.update(range_name="A1", values=[HEAD])
        existing = ws.get_all_values()
        have = {(r[0], r[1]): n + 2 for n, r in enumerate(existing[1:]) if len(r) > 1}
        today = date.today()
        rows_new, rows_upd = [], {}
        cache = {}
        for sym, ed, ep, tt, status, xd, xp, pnl, reason in trades:
            if sym not in cache:
                try:
                    df = yf.download(sym + ".NS", start=(ed - timedelta(days=10)).isoformat(), interval="1d", auto_adjust=False, progress=False)
                    df.columns = df.columns.get_level_values(0)
                    cache[sym] = ([d.date() for d in df.index], df["Close"].tolist(), df["High"].tolist())
                except Exception:
                    cache[sym] = None
            c = cache[sym]
            if not c:
                continue
            h20, h40 = score_hold(c[0], c[1], ed, ep, 20), score_hold(c[0], c[1], ed, ep, 40)
            px = post_exit_high(c[0], c[2], xd, xp) if (xd and xp) else None
            row = [sym, ed.isoformat(), ep, tt, status, xd.isoformat() if xd else "", xp if xp is not None else "", pnl if pnl is not None else "", reason,
                   h20[0].isoformat() if h20 else "", round(h20[1], 2) if h20 else "", h20[2] if h20 else "",
                   h40[0].isoformat() if h40 else "", round(h40[1], 2) if h40 else "", h40[2] if h40 else "", px if px is not None else "", today.isoformat()]
            key = (sym, ed.isoformat())
            if key in have:
                old = existing[have[key] - 1]
                if (old + [""] * len(HEAD))[:len(HEAD) - 1] != [str(x) for x in row][:len(HEAD) - 1]:
                    rows_upd[have[key]] = row
            else:
                rows_new.append(row)
        print(f"[SHADOW] {len(rows_new)} new rows, {len(rows_upd)} updates")
        if "--write" in argv:
            for rn, row in rows_upd.items():
                ws.update(range_name=f"A{rn}", values=[row], value_input_option="USER_ENTERED")
            if rows_new:
                start = len(existing) + 1
                if ws.row_count < start + len(rows_new) + 5:
                    ws.add_rows(start + len(rows_new) + 5 - ws.row_count)
                ws.update(range_name=f"A{start}", values=rows_new, value_input_option="USER_ENTERED")
            print("[SHADOW] written")
        else:
            for r in (rows_new + list(rows_upd.values()))[:5]:
                print("   ", r[:16])
    except Exception as e:
        print(f"[SHADOW] skipped (fail-open): {str(e)[:150]}")
    return 0


def report(sh):
    v = sh.worksheet(TAB).get_all_values()
    h = v[0]
    ix = {k: h.index(k) for k in HEAD}
    rows = [r + [""] * (len(h) - len(r)) for r in v[1:]]
    closed = [r for r in rows if r[ix["Status"]] == "CLOSED" and _f(r[ix["Live_PnL_%"]]) is not None]
    sc = [r for r in closed if _f(r[ix["Hold20_%"]]) is not None]
    print(f"[SHADOW REPORT] {len(rows)} rows, {len(closed)} closed, {len(sc)} with a scored 20-day hold")
    if sc:
        live = [_f(r[ix["Live_PnL_%"]]) for r in sc]
        h20 = [_f(r[ix["Hold20_%"]]) for r in sc]
        better = sum(1 for a, b in zip(live, h20) if b > a)
        print(f"  avg live P/L {sum(live) / len(live):+.2f}% vs plain hold-20 {sum(h20) / len(h20):+.2f}%; hold-20 was better on {better} of {len(sc)} trades")
    pe = [_f(r[ix["PostExit10d_High_%"]]) for r in closed if _f(r[ix["PostExit10d_High_%"]]) is not None]
    if pe:
        print(f"  after the live exit the stock rose a further {sum(pe) / len(pe):.1f}% (average best high in the next 10 sessions, n={len(pe)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
