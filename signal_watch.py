"""
signal_watch.py v1.0 (2026-11-12 NEW) - OBSERVATION-ONLY forward tracker `SignalWatch` (tab). Never read by trading_bot.py / appscript.gs / any gate, alert or ledger.
WHY (owner 2026-11-12, after TECHM-style rallies in PNB / PHOENIXLTD / KALYANKJIL / PAYTM etc. were not taken): three questions had only a historical (daily-bar, survivor) answer.
It logs, once per stock + date + category, what each idea WOULD have flagged, and scores the real forward result (buy next session's open, cost 0.25%, close after 1/3/5/10/20 sessions):
  RSI75_BLOCKED  = the 'Top picks' breakout (first close above the 50-day closing high, close>EMA50>EMA200, volume>=1.5x 20d avg, RS35>=5, NIFTY>EMA50) with RSI(14) > 75 -
                   the case the live RSI hard block (>75) refuses.   TOP_PICK = the same signal with RSI <= 75 (control).
  DEEP_RECOVERY  = stock was >=40% below its 252-day high at some point in the last 60 sessions and TODAY first shows RS35>=5 and close>EMA50.
  H1_V4          = hourly EMA9>21>50>200 with close>EMA21 turned true during the last session, daily close>EMA50>EMA200, that hourly close above the previous 140 hourly highs
                   (~20 sessions) and daily RS35>=5 (the one 1H variant that beat random in the 2024-26 test; n=236, 7 variants tried - may be luck, hence forward tracking).
Backtest background (daily/1H, 2018/2024-2026, survivors only): RS>=5 breakouts by RSI: <=65 +2.27%, 65-75 +2.46%, >75 +2.72% (20d); deep discount ex-2020 = no edge; plain 1H EMA alignment = random.
  SLOT_LOST      = (added 2026-11-13) stock that PASSED every per-stock gate in the live appscript scan but lost the WAITING slot (2-per-sector cap counted with open trades, or slot limit) - read from the ScanReasons tab; measures what the sector/slot cap costs.
USAGE: python signal_watch.py            dry-run (prints)       python signal_watch.py --write      log + score      python signal_watch.py --report
"""
import os
import sys
import json
import time
import datetime as dt

import pytz

IST = pytz.timezone("Asia/Kolkata")
VERSION = "v1.0"
SHEET = "Ai360tradingAlgo"
TAB = "SignalWatch"
HEAD = ["Logged_On", "Signal_Date", "Symbol", "Category", "Signal_Close", "RSI14", "RS35", "Vol_x", "Entry_Open", "R1_%", "R3_%", "R5_%", "R10_%", "R20_%", "Scored"]
HORIZONS = (1, 3, 5, 10, 20)
COST = 0.25


# ---------------- pure logic (unit-tested) ----------------

def ema(vals, span):
    k = 2.0 / (span + 1)
    out, e = [], None
    for v in vals:
        e = v if e is None else v * k + e * (1 - k)
        out.append(e)
    return out


def rsi14(closes):
    if len(closes) < 16:
        return None
    ch = [closes[i] - closes[i - 1] for i in range(len(closes) - 14, len(closes))]
    up = sum(x for x in ch if x > 0) / 14.0
    dn = sum(-x for x in ch if x < 0) / 14.0
    return 100.0 if dn == 0 else 100.0 - 100.0 / (1.0 + up / dn)


def rs35(stock_closes, bench_closes, dates, bench_dates, i):
    """RS = stock 35-calendar-day % return minus benchmark's, as of daily index i. None when history is short."""
    d = dates[i] - dt.timedelta(days=35)
    def at(cl, ds):
        j = None
        for k in range(len(ds) - 1, -1, -1):
            if ds[k] <= d:
                j = k
                break
        return None if j is None else cl[j]
    sb, bb = at(stock_closes, dates), at(bench_closes, bench_dates)
    bn = None
    for k in range(len(bench_dates) - 1, -1, -1):
        if bench_dates[k] <= dates[i]:
            bn = bench_closes[k]
            break
    if not (sb and bb and bn):
        return None
    return (stock_closes[i] / sb - 1) * 100 - (bn / bb - 1) * 100


def daily_signals(closes, highs, volumes, rs, nifty_above_ema50):
    """Categories flagged by the LAST daily bar: TOP_PICK / RSI75_BLOCKED / DEEP_RECOVERY."""
    n = len(closes)
    out = []
    if n < 260 or rs is None:
        return out
    e50, e200 = ema(closes, 50), ema(closes, 200)
    r = rsi14(closes)
    hh = max(closes[n - 51:n - 1])
    hh_prev = max(closes[n - 52:n - 2])
    first_break = closes[-1] > hh and closes[-2] <= hh_prev
    avg20 = sum(volumes[n - 21:n - 1]) / 20.0
    volx = volumes[-1] / avg20 if avg20 else 0
    if first_break and closes[-1] > e50[-1] > e200[-1] and volx >= 1.5 and rs >= 5 and nifty_above_ema50:
        out.append("RSI75_BLOCKED" if (r is not None and r > 75) else "TOP_PICK")
    # deep discount recovery: >=40% below the 252d high at some point in the last 60 sessions, first flip to RS>=5 and >EMA50 today
    flipped = rs >= 5 and closes[-1] > e50[-1]
    if flipped:
        was_deep = False
        for k in range(n - 60, n):
            hi = max(highs[max(0, k - 251):k + 1])
            if closes[k] <= hi * 0.60:
                was_deep = True
                break
        if was_deep:
            out.append("DEEP_RECOVERY")
    return out


def h1_flip_v4(h_close, h_high, bars_last_session, daily_ok, rs):
    """True when the hourly alignment turned true inside the last session AND that bar broke the previous 140 hourly highs AND daily trend ok AND RS>=5."""
    n = len(h_close)
    if n < 360 or not daily_ok or rs is None or rs < 5:
        return False
    e9, e21, e50, e200 = ema(h_close, 9), ema(h_close, 21), ema(h_close, 50), ema(h_close, 200)
    cond = [(e9[i] > e21[i] > e50[i] > e200[i]) and h_close[i] > e21[i] for i in range(n)]
    for i in range(n - bars_last_session, n):
        if cond[i] and not cond[i - 1] and h_close[i] > max(h_high[i - 140:i]):
            return True
    return False


def fwd_returns(entry_open, closes_after, horizons=HORIZONS, cost=COST):
    """closes_after[k-1] = close of the k-th session from the entry session. Returns {k: pct or None}."""
    return {k: (round((closes_after[k - 1] / entry_open - 1) * 100 - cost, 2) if len(closes_after) >= k else None) for k in horizons}


# ---------------- data / sheet ----------------

def _connect():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open(SHEET)


def _universe(sh):
    n = sh.worksheet("Nifty200").get_all_values()
    return [r[0].replace("NSE:", "").strip() for r in n[2:] if r and r[0] and "NIFTY" not in r[0].upper()]


def _dl(symbols, period, interval):
    import yfinance as yf
    return yf.download([s + ".NS" for s in symbols] + (["^NSEI"] if interval == "1d" else []), period=period, interval=interval,
                       group_by="ticker", auto_adjust=False, progress=False, threads=True)


def slot_lost_symbols(sh):
    """{symbol} that PASSED every per-stock gate in the live scanner but lost the WAITING slot (sector cap / slot limit), from the ScanReasons tab (holds the last scanned day)."""
    out, day = set(), None
    try:
        for r in sh.worksheet("ScanReasons").get_all_values()[1:]:
            if len(r) > 3 and "lost the WAITING slot" in r[3]:
                out.add(r[1].replace("NSE:", "").strip())
                day = r[0]
    except Exception:
        pass
    return out, day


def scan(symbols, slot_lost=(), slot_day=None):
    """-> list of (symbol, signal_date, category, close, rsi, rs, volx)."""
    D = _dl(symbols, "2y", "1d")
    nb = D["^NSEI"].dropna(subset=["Close"])
    bdates = [d.date() for d in nb.index]
    bcl = [float(x) for x in nb.Close]
    nb_e50 = ema(bcl, 50)
    nifty_ok = bcl[-1] > nb_e50[-1]
    H = None
    found = []
    for s in symbols:
        try:
            x = D[s + ".NS"].dropna(subset=["Close"])
            if len(x) < 260:
                continue
            dates = [d.date() for d in x.index]
            c = [float(v) for v in x.Close]
            h = [float(v) for v in x.High]
            v = [float(w) for w in x.Volume]
            rs = rs35(c, bcl, dates, bdates, len(c) - 1)
            cats = daily_signals(c, h, v, rs, nifty_ok)
            e50, e200 = ema(c, 50), ema(c, 200)
            daily_ok = c[-1] > e50[-1] > e200[-1]
            avg20 = sum(v[-21:-1]) / 20.0
            volx = round(v[-1] / avg20, 2) if avg20 else None
            if s in slot_lost and slot_day == dates[-1].isoformat():
                cats = cats + ["SLOT_LOST"]
            for cat in cats:
                found.append((s, dates[-1], cat, c[-1], rsi14(c), rs, volx))
            if daily_ok and rs is not None and rs >= 5:
                if H is None:
                    H = _dl(symbols, "60d", "1h")
                try:
                    y = H[s + ".NS"].dropna(subset=["Close"])
                    last_day = y.index[-1].date()
                    nlast = sum(1 for t in y.index if t.date() == last_day)
                    if h1_flip_v4([float(q) for q in y.Close], [float(q) for q in y.High], nlast, daily_ok, rs):
                        found.append((s, dates[-1], "H1_V4", c[-1], rsi14(c), rs, volx))
                except Exception:
                    pass
        except Exception:
            continue
    return found


def log_and_score(sh, found, today, write):
    import gspread
    ws = None
    try:
        ws = sh.worksheet(TAB)
    except gspread.WorksheetNotFound:
        if write:
            ws = sh.add_worksheet(TAB, rows=1000, cols=len(HEAD))
            ws.update(range_name="A1", values=[HEAD])
    v = ws.get_all_values() if ws is not None else [HEAD]
    have = {(r[1], r[2], r[3]) for r in v[1:] if len(r) > 3}
    fresh = [[today.isoformat(), d.isoformat(), s, cat, round(c, 2), round(r, 1) if r is not None else "", round(rs, 1) if rs is not None else "", vx if vx is not None else "",
              "", "", "", "", "", "", ""] for (s, d, cat, c, r, rs, vx) in found if (d.isoformat(), s, cat) not in have]
    print(f"[SIGNALS] {len(found)} flagged, {len(fresh)} new")
    for f in fresh:
        print("   ", f[1], f[2], f[3], "close", f[4], "RSI", f[5], "RS", f[6], "vol x", f[7])
    if not write:
        return
    if fresh:
        start = len(v) + 1
        if ws.row_count < start + len(fresh) + 5:
            ws.add_rows(start + len(fresh) + 5 - ws.row_count)
        ws.update(range_name=f"A{start}", values=fresh, value_input_option="USER_ENTERED")
    v = ws.get_all_values()
    todo = [(i, r) for i, r in enumerate(v[1:], start=2) if len(r) >= 15 and r[14] != "Y" and r[1] and dt.date.fromisoformat(r[1]) < today]
    if not todo:
        return
    import yfinance as yf
    syms = sorted({r[2] for _, r in todo})
    D = yf.download([s + ".NS" for s in syms], period="3mo", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
    body = []
    for i, r in todo:
        try:
            x = D[r[2] + ".NS"].dropna(subset=["Close"]) if len(syms) > 1 else D.dropna(subset=["Close"])
            sig = dt.date.fromisoformat(r[1])
            idx = [k for k, d in enumerate(x.index) if d.date() > sig]
            if not idx:
                continue
            e0 = idx[0]
            entry = float(x.Open.iloc[e0])
            after = [float(q) for q in x.Close.iloc[e0:]]
            fr = fwd_returns(entry, after)
            done = "Y" if fr[20] is not None else ""
            body.append({"range": f"I{i}:O{i}", "values": [[round(entry, 2)] + [("" if fr[k] is None else fr[k]) for k in HORIZONS] + [done]]})
        except Exception:
            continue
    for k in range(0, len(body), 100):
        ws.batch_update(body[k:k + 100], value_input_option="USER_ENTERED")
        time.sleep(1)
    print(f"[SCORE] updated {len(body)} rows")


def report(sh):
    v = sh.worksheet(TAB).get_all_values()
    print(f"[REPORT] {len(v) - 1} rows logged")
    for cat in ("TOP_PICK", "RSI75_BLOCKED", "DEEP_RECOVERY", "H1_V4", "SLOT_LOST"):
        rows = [r for r in v[1:] if len(r) >= 15 and r[3] == cat]
        out = [f"  {cat:14s} logged {len(rows):3d}"]
        for lab, col in (("R5", 11), ("R10", 12), ("R20", 13)):
            x = [float(r[col]) for r in rows if r[col] != ""]
            if x:
                out.append(f"{lab}: n={len(x)} avg {sum(x) / len(x):+.2f}% up {sum(1 for t in x if t > 0) * 100 // len(x)}%")
        print(" | ".join(out))


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    sh = _connect()
    if "--report" in argv:
        return report(sh)
    today = dt.datetime.now(IST).date()
    write = "--write" in argv
    print(f"[signal_watch {VERSION}] {today} mode={'WRITE' if write else 'DRY-RUN'}")
    try:
        lost, lday = slot_lost_symbols(sh)
        found = scan(_universe(sh), lost, lday)
        log_and_score(sh, found, today, write)
    except Exception as e:
        print(f"[signal_watch] skipped (fail-open): {str(e)[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
