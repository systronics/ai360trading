"""
gate_audit.py v1.0 (2026-11-02) — OBSERVATION-ONLY research log: which of our gates help, and which cost us good stocks?

WHY (owner question 2026-11-02): top-gainer lists are hindsight. To judge a gate fairly you need EVERY candidate, whether it passed or was
blocked, and what it did afterwards. This writes one row per (date, stock) for the universe Nifty200 + F&O stocks (~233) to a new `GateAudit`
tab: features at that day's close, which gates would pass, and the forward 1/3/5/10-day returns (filled in later as the days pass).

NEVER read by trading_bot.py, appscript.gs, any gate, alert or ledger (informational/research only; same doctrine as ShadowLedger/BuildupWatch).
Fail-open: any error = nothing written/changed. Idempotent per (date, symbol). Gate flags are DAILY-bar approximations of the live gates
(the live system also uses intraday volume pace etc.), so this measures the idea behind each gate, not the exact live code path.

USAGE
  python gate_audit.py                    # dry-run: prints what it would log for the latest trading day
  python gate_audit.py --write            # log the latest day (+ score older rows)
  python gate_audit.py --backfill 30 --write   # also log the previous 30 trading days (their returns are known immediately)
  python gate_audit.py --report           # read-only summary of the tab (pass vs blocked per gate, RS quintile spread, top-gainer capture)
"""
import os
import sys
import json
import time
import warnings
import statistics
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytz

warnings.filterwarnings("ignore")
IST = pytz.timezone("Asia/Kolkata")
VERSION = "v1.0"
SHEET_NAME = "Ai360tradingAlgo"
TAB = "GateAudit"
HEAD = ["Date", "Symbol", "In_N200", "FO", "Close", "Day_%", "Gap_%", "RS35", "RS63", "RS35_Rank", "RSI14", "Above_50DMA", "Above_200DMA",
        "Down_52wH_%", "Range_20D_%", "CH50_5D", "VolRatio", "Buildup", "Nifty_Day_%", "G_RS", "G_Trend", "G_RSI", "G_Leader",
        "Ret_1d_%", "Ret_3d_%", "Ret_5d_%", "Ret_10d_%"]
FWD = {"Ret_1d_%": 1, "Ret_3d_%": 3, "Ret_5d_%": 5, "Ret_10d_%": 10}
KEEP_DAYS = 250   # rows older than this are pruned (the sheet stays well under Google's cell limit)


# ───────────────────────────── pure logic (unit-tested) ─────────────────────────────

def rsi14(c):
    dl = c.diff()
    return 100 - 100 / (1 + dl.clip(lower=0).rolling(14).mean() / (-dl.clip(upper=0)).rolling(14).mean())


def ret_cal(c, days):
    """% return over `days` CALENDAR days (same definition as the sheet's RS: fetch_rs.py LOOKBACK_D=35)."""
    past = c.reindex(c.index - pd.Timedelta(days=days), method="ffill")
    past.index = c.index
    return (c / past - 1) * 100


def gates(rs35, above50, rsi, day_pct):
    """Daily-bar approximations of our live gates: RS>=5 (locked), trend (above 50-DMA), RSI band (<=65, or <=75 when the stock is up on the
    day: the calibrated hot-leader exception), and 'leader' = all three."""
    g_rs = rs35 >= 5
    g_tr = bool(above50)
    g_rsi = (rsi <= 65) or (rsi <= 75 and day_pct > -0.3)
    return bool(g_rs), g_tr, bool(g_rsi), bool(g_rs and g_tr and g_rsi)


def fwd_close_ret(closes, i, k):
    """Close-to-close return in % from position i to i+k, or None when not available yet."""
    if i + k >= len(closes) or not closes[i]:
        return None
    return round((closes[i + k] / closes[i] - 1) * 100.0, 2)


def build_frames(daily, universe, bench, fo_set, n200_set):
    """daily: dict sym -> DataFrame(Open,High,Low,Close,Volume) indexed by date. Returns one DataFrame with a row per (date, symbol)."""
    nrs35 = ret_cal(bench, 35)
    nrs63 = ret_cal(bench, 63)
    nday = bench.pct_change() * 100
    frames = []
    for s in universe:
        x = daily.get(s)
        if x is None or len(x) < 120:
            continue
        c, o, h, l, v = x["Close"], x["Open"], x["High"], x["Low"], x["Volume"]
        f = pd.DataFrame(index=c.index)
        f["Close"] = c
        f["Day"] = c.pct_change() * 100
        f["Gap"] = (o / c.shift(1) - 1) * 100
        f["RS35"] = ret_cal(c, 35) - nrs35.reindex(c.index).ffill()
        f["RS63"] = ret_cal(c, 63) - nrs63.reindex(c.index).ffill()
        f["RSI"] = rsi14(c)
        f["A50"] = c > c.rolling(50).mean()
        f["A200"] = c > c.rolling(200).mean()
        f["Down52"] = (c / h.rolling(252, min_periods=120).max() - 1) * 100
        f["Range20"] = (h.rolling(20).max() - l.rolling(20).min()) / c * 100
        f["CH50"] = (c >= c.rolling(50).max().shift(1)).rolling(5).max() > 0
        f["VolRatio"] = v / v.rolling(20).mean().shift(1)
        f["NiftyDay"] = nday.reindex(c.index).ffill()
        cl = c.values.tolist()
        for name, k in FWD.items():
            f[name] = [fwd_close_ret(cl, i, k) for i in range(len(cl))]
        f["Symbol"] = s
        f["Date"] = f.index
        f["In_N200"] = "Y" if s in n200_set else "N"
        f["FO"] = "Y" if s in fo_set else "N"
        f.index.name = None
        frames.append(f.dropna(subset=["RS35", "RSI"]))
    a = pd.concat(frames, ignore_index=True)
    a["Rank"] = a.groupby("Date")["RS35"].rank(pct=True)
    return a


# ───────────────────────────── data + sheet ─────────────────────────────

def _connect():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        try:
            with open("service_account.json") as fh:
                raw = fh.read().strip()
        except FileNotFoundError:
            raise SystemExit("[CREDS] GCP_SERVICE_ACCOUNT_JSON not set and no local service_account.json")
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open(SHEET_NAME)


def _universe(sh):
    import fetch_fo_buildup as F
    n = sh.worksheet("Nifty200").get_all_values()
    n200 = {r[0].replace("NSE:", "").strip() for r in n[2:] if r and r[0].strip()}
    rows, tdate = F.load_rows(None)
    fo, labels = set(), {}
    if rows:
        data = F.summarize(rows)
        fo = set(data)
        labels = {s: F.classify(d["price_pct"], d["oi_pct"]) for s, d in data.items()}
    return sorted(n200 | fo), n200, fo, labels, tdate


def _download(universe):
    import yfinance as yf
    tick = [s + ".NS" for s in universe] + ["^NSEI"]
    raw = yf.download(tick, period="3y", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
    daily = {}
    for s in universe + ["^NSEI"]:
        try:
            x = raw[(s + ".NS") if s != "^NSEI" else "^NSEI"].dropna(subset=["Close"]).copy()
            x.index = (x.index.tz_localize(None) if x.index.tz is not None else x.index).normalize()
            daily[s] = x
        except Exception:
            continue
    return daily


def _row(r, labels, last_date):   # last_date = the F&O file's date: the buildup label is only valid for that exact day
    def num(x, nd=2):
        return "" if pd.isna(x) else round(float(x), nd)
    lab = labels.get(r.Symbol, "") if r.Date == last_date else ""
    g_rs, g_tr, g_rsi, g_lead = gates(r.RS35, r.A50, r.RSI, r.Day if not pd.isna(r.Day) else 0.0)
    out = [r.Date.strftime("%Y-%m-%d"), r.Symbol, r.In_N200, r.FO, num(r.Close), num(r.Day), num(r.Gap), num(r.RS35), num(r.RS63), num(r.Rank, 3),
           num(r.RSI, 1), "Y" if r.A50 else "N", "Y" if r.A200 else "N", num(r.Down52, 1), num(r.Range20, 1), "Y" if r.CH50 else "N", num(r.VolRatio),
           lab, num(r.NiftyDay), "Y" if g_rs else "N", "Y" if g_tr else "N", "Y" if g_rsi else "N", "Y" if g_lead else "N"]
    return out


def _fwd_values(r):
    return [("" if pd.isna(r[n]) else r[n]) for n in FWD]


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    write = "--write" in argv
    back = int(argv[argv.index("--backfill") + 1]) if "--backfill" in argv else 2   # default: re-check the last 3 trading days (idempotent), so a Yahoo lag self-heals
    sh = _connect()
    if "--report" in argv:
        return report(sh)
    print(f"[gate_audit {VERSION}] {datetime.now(IST):%Y-%m-%d %H:%M IST} | mode={'WRITE' if write else 'DRY-RUN'} | backfill={back}")
    universe, n200, fo, labels, tdate = _universe(sh)
    print(f"[UNIVERSE] {len(universe)} stocks (Nifty200 {len(n200)}, F&O {len(fo)}, F&O outside Nifty200 {len(fo - n200)}); bhavcopy date {tdate}")
    daily = _download(universe)
    bench = daily.get("^NSEI")
    if bench is None or not len(bench):
        print("[YF] benchmark missing, nothing written (fail-open)")
        return 0
    a = build_frames({s: daily[s] for s in universe if s in daily}, [s for s in universe if s in daily], bench["Close"], fo, n200)
    # never log an unfinished session: before 16:00 IST today's Yahoo bar is partial (market still open / not yet final)
    _now = datetime.now(IST)
    _cut = pd.Timestamp(_now.date()) if _now.hour >= 16 else pd.Timestamp(_now.date()) - pd.Timedelta(days=1)
    a = a[a.Date <= _cut]
    dates = sorted(a.Date.unique())
    last = pd.Timestamp(dates[-1])
    if tdate and pd.Timestamp(tdate) > last:
        print(f"[YF] prices only up to {last.date()} while the F&O file is for {tdate}: Yahoo lags; logging what exists (the next run fills the rest)")
    pick = dates[-(back + 1):] if back else [last]
    sel = a[a.Date.isin(pick)]
    print(f"[ROWS] {len(sel)} rows for {len(pick)} trading day(s), last day {last.date()}")
    try:
        import gspread
        try:
            ws = sh.worksheet(TAB)
        except Exception:
            if not write:
                print("[SHEET] tab does not exist yet (dry-run, not creating it)")
                return 0
            ws = sh.add_worksheet(TAB, rows=2000, cols=len(HEAD))
            ws.update(range_name="A1", values=[HEAD])
        existing = ws.get_all_values()
        have = {(r[0], r[1]) for r in existing[1:] if len(r) > 1}
        fresh = []
        for r in sel.itertuples():
            key = (r.Date.strftime("%Y-%m-%d"), r.Symbol)
            if key in have:
                continue
            fresh.append(_row(r, labels, pd.Timestamp(tdate) if tdate else last) + _fwd_values(sel.loc[(sel.Date == r.Date) & (sel.Symbol == r.Symbol)].iloc[0]))
        print(f"[NEW] {len(fresh)} rows not yet in {TAB}")
        if not write:
            for r in fresh[:5]:
                print("   ", r[:12])
            print("[DRY-RUN] nothing written.")
            return 0
        if fresh:
            start = len(existing) + 1
            need = start + len(fresh) + 10
            if ws.row_count < need:
                ws.add_rows(need - ws.row_count)
            for k in range(0, len(fresh), 1500):
                ws.update(range_name=f"A{start + k}", values=fresh[k:k + 1500], value_input_option="USER_ENTERED")
                time.sleep(1.0)
            print(f"[WRITE] appended {len(fresh)} rows")
        score_rows(ws, a)
        prune(ws)
    except Exception as e:
        print(f"[GATE_AUDIT] skipped (fail-open): {str(e)[:160]}")
    return 0


def score_rows(ws, a):
    """Fill the forward-return cells of older rows whose days have now passed. Touches only the four Ret_* cells of rows that were blank."""
    vals = ws.get_all_values()
    hd = vals[0]
    idx = {n: hd.index(n) for n in FWD}
    look = a.set_index(["Symbol", "Date"])
    body = []
    for i, r in enumerate(vals[1:], start=2):
        if len(r) < len(hd) or all(r[idx[n]] != "" for n in FWD):
            continue
        try:
            key = (r[1], pd.Timestamp(r[0]))
            row = look.loc[key]
        except Exception:
            continue
        for n in FWD:
            if r[idx[n]] == "" and not pd.isna(row[n]):
                body.append({"range": f"{_col(idx[n] + 1)}{i}", "values": [[float(row[n])]]})
    for k in range(0, len(body), 500):
        ws.batch_update(body[k:k + 500], value_input_option="USER_ENTERED")
        time.sleep(1.0)
    print(f"[SCORE] filled {len(body)} forward-return cells")


def _col(n):
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def prune(ws):
    vals = ws.get_all_values()
    cutoff = (datetime.now(IST).date() - timedelta(days=KEEP_DAYS)).isoformat()
    old = [i for i, r in enumerate(vals[1:], start=2) if r and r[0] and r[0] < cutoff]
    if old:
        ws.delete_rows(old[0], old[-1])
        print(f"[PRUNE] removed {len(old)} rows older than {KEEP_DAYS} days")


def report(sh):
    """Read-only: does each gate help? pass vs blocked average forward return, RS quintiles, and how many next-day top gainers each gate would have blocked."""
    ws = sh.worksheet(TAB)
    v = ws.get_all_values()
    df = pd.DataFrame(v[1:], columns=v[0])
    for c in ["Ret_1d_%", "Ret_5d_%", "RS35", "RS35_Rank", "Day_%"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    print(f"[REPORT] {len(df)} logged rows, {df.Date.nunique()} days, {df.Symbol.nunique()} stocks; rows with 5-day result: {int(df['Ret_5d_%'].notna().sum())}")
    d5 = df.dropna(subset=["Ret_5d_%"])
    if len(d5):
        print(f"\nBaseline 5-day return: {d5['Ret_5d_%'].mean():+.2f}% (win {(d5['Ret_5d_%'] > 0).mean() * 100:.0f}%)")
        for g in ("G_RS", "G_Trend", "G_RSI", "G_Leader", "CH50_5D", "FO"):
            p, b = d5[d5[g] == "Y"], d5[d5[g] == "N"]
            print(f"  {g:9} PASS n={len(p):5} avg {p['Ret_5d_%'].mean():+.2f}% win {(p['Ret_5d_%'] > 0).mean() * 100:4.0f}%   |  BLOCKED n={len(b):5} avg {b['Ret_5d_%'].mean():+.2f}% win {(b['Ret_5d_%'] > 0).mean() * 100:4.0f}%")
        hi, lo = d5[d5["RS35_Rank"] >= 0.8], d5[d5["RS35_Rank"] <= 0.2]
        print(f"  RS35 top 20% {hi['Ret_5d_%'].mean():+.2f}%  bottom 20% {lo['Ret_5d_%'].mean():+.2f}%  spread {hi['Ret_5d_%'].mean() - lo['Ret_5d_%'].mean():+.2f}%  (momentum works when this is clearly > 0)")
    d1 = df.dropna(subset=["Ret_1d_%"])
    if len(d1):
        top = d1.sort_values(["Date", "Ret_1d_%"], ascending=[True, False]).groupby("Date").head(15)
        print(f"\nOf the 15 biggest NEXT-DAY gainers each day (n={len(top)}), how many our gates would have BLOCKED the day before:")
        for g in ("G_RS", "G_Trend", "G_RSI", "G_Leader"):
            print(f"  {g:9} blocked {(top[g] == 'N').mean() * 100:4.0f}% of top gainers   (it blocks {(d1[g] == 'N').mean() * 100:4.0f}% of all stocks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
