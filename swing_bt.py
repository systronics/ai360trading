"""
swing_bt.py v1.0 (2026-11-07) - SWING backtest: which EXIT rule is best for the 'Top picks' swing signal? Research only (writes nothing to the sheet, trades nothing).

WHY (owner 2026-11-07, after two intraday batches found no edge): the only rule with evidence is the daily swing 'Top picks' signal (+3.58% per trade over 20 days vs +1.14% random, test 2025-26 +1.55% vs +0.12%).
Entries are therefore left alone; this asks how to HOLD it: fixed holds, ATR stop, the live system's stop/target, or a trailing stop. Also tests the live system's own swing parameters (ATR_SL_SWING 2.0, ATR_TGT_SWING 3.8).

PRE-REGISTERED (written before the first run; run once):
  SIGNAL (daily, known at the close, as in publish_signal_lists.py): close > highest close of the prior 50 sessions AND close > EMA50 > EMA200 AND volume >= 1.5 x its prior-20-day average
         AND stock 25-day return minus NIFTY 25-day return >= 5 percentage points AND NIFTY close > its EMA50 AND average traded value (20d volume x close) >= Rs 10 Cr.  Entry = NEXT day's open. One open trade per stock at a time.
  EXITS (all include the Rs/percent cost COST_PCT = 0.25% round trip; daily bars; a day touching both stop and target counts as STOP; a gap through a stop fills at the open):
    X1 HOLD20         sell at the close of day 20 (the baseline behind the +3.58% figure)
    X2 HOLD10         sell at the close of day 10
    X3 HOLD40         sell at the close of day 40
    X4 ATR2+HOLD20    stop = entry - 2.0 x ATR14 (known at the signal), else sell at the close of day 20
    X5 LIVE-RULE      stop = entry - 2.0 x ATR14, target = entry + 3.8 x ATR14 (the live ATR_SL_SWING / ATR_TGT_SWING), else sell at the close of day 20
    X6 TRAIL          initial stop entry - 2.0 x ATR14; the stop then trails up to (highest high since entry - 2.5 x ATR14), never down; sell on a stop hit, else at the close of day 40
  UNIVERSE: current Nifty200 members (survivorship bias: today's constituents), daily data 2018-2026 from yfinance. TRAIN = signals through 2023, TEST = 2024 onwards.
  DECISION RULE (fixed now): an exit rule is recommended over X1 only if its TEST average % per trade is >= 0.3 points higher than X1's AND its TRAIN average is also higher AND its 10th-percentile trade is not worse than X1's by more than 2 points.
BATCH 2 (pre-registered 2026-11-07 AFTER batch 1 showed that tight stops/targets cut most of the profit; same signal, universe, costs, TRAIN/TEST; run once; X1 and X3 are re-run as baselines):
    Y1 WIDE3      stop = entry - 3.0 x ATR14, no target, else sell at the close of day 20
    Y2 WIDE4      stop = entry - 4.0 x ATR14, no target, else sell at the close of day 20
    Y3 WIDE3-40   stop = entry - 3.0 x ATR14, no target, else sell at the close of day 40
    Y4 PCT10      fixed stop 10% below the entry, else sell at the close of day 20
    Y5 BE-TRAIL   stop = entry - 3.0 x ATR14; once a close reaches entry + 2.0 x ATR14 the stop moves to at least the entry and then trails (highest close - 3.0 x ATR14), never down; else sell at the close of day 40
  DECISION RULE (fixed now). A 20-day variant (Y1, Y2, Y4) is compared with X1, a 40-day variant (Y3, Y5) with X3, on TEST and TRAIN:
    TAIL-SAVER   = TEST average within 0.3 points of the baseline (or higher) AND TEST 10th-percentile trade at least 1.5 points BETTER than the baseline AND TRAIN shows the same two relations.
    RETURN-BOOST = TEST average >= baseline + 0.3 AND TEST 10th percentile not worse than the baseline by more than 2 points AND TRAIN average also higher.
    Anything else = not better.
USAGE: python swing_bt.py --run        python swing_bt.py --run2
"""
import json
import os
import sys

import numpy as np
import pandas as pd

COST_PCT = 0.25
TRAIN_END = 2023
VARIANTS = ["X1 HOLD20", "X2 HOLD10", "X3 HOLD40", "X4 ATR2+HOLD20", "X5 LIVE-RULE", "X6 TRAIL"]
VARIANTS2 = ["X1 HOLD20", "X3 HOLD40", "Y1 WIDE3", "Y2 WIDE4", "Y3 WIDE3-40", "Y4 PCT10", "Y5 BE-TRAIL"]


def atr14(h, l, c):
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(14).mean()


def simulate_exit(variant, o, h, l, c, i0, atr):
    """Entry at o[i0] (the day after the signal). Returns (exit_index, exit_price). atr = ATR14 known at the signal. Pure function on numpy arrays."""
    entry = o[i0]
    n = len(o)
    last = lambda k: min(i0 + k - 1, n - 1)           # the k-th trading day counting the entry day as day 1
    if variant in ("X1 HOLD20", "X2 HOLD10", "X3 HOLD40"):
        k = {"X1 HOLD20": 20, "X2 HOLD10": 10, "X3 HOLD40": 40}[variant]
        j = last(k)
        return j, c[j]
    if variant in ("Y1 WIDE3", "Y2 WIDE4", "Y3 WIDE3-40", "Y4 PCT10", "Y5 BE-TRAIL"):
        mult = {"Y1 WIDE3": 3.0, "Y2 WIDE4": 4.0, "Y3 WIDE3-40": 3.0, "Y5 BE-TRAIL": 3.0}.get(variant)
        stop = entry * 0.90 if variant == "Y4 PCT10" else entry - mult * atr
        horizon = 40 if variant in ("Y3 WIDE3-40", "Y5 BE-TRAIL") else 20
        hi_close, armed = entry, False
        for j in range(i0, last(horizon) + 1):
            if l[j] <= stop:
                return j, (min(stop, o[j]) if j > i0 else stop)
            if variant == "Y5 BE-TRAIL":
                hi_close = max(hi_close, c[j])
                if c[j] >= entry + 2.0 * atr:
                    armed = True
                if armed:
                    stop = max(stop, entry, hi_close - 3.0 * atr)
        j = last(horizon)
        return j, c[j]
    stop = entry - 2.0 * atr
    target = entry + 3.8 * atr if variant == "X5 LIVE-RULE" else None
    horizon = 40 if variant == "X6 TRAIL" else 20
    hi = entry
    for j in range(i0, last(horizon) + 1):
        if variant == "X6 TRAIL" and j > i0:
            stop = max(stop, hi - 2.5 * atr)
        if l[j] <= stop:
            return j, (min(stop, o[j]) if j > i0 else stop)
        if target is not None and h[j] >= target:
            return j, target
        hi = max(hi, h[j])
    j = last(horizon)
    return j, c[j]


def signals_for(sym_df, nifty_ok, nifty_r25):
    """Boolean Series of signal days (known at the close) for one stock. sym_df has o,h,l,c,v indexed by date."""
    c, v = sym_df["c"], sym_df["v"]
    e50, e200 = c.ewm(span=50, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    hi50 = c.shift(1).rolling(50).max()
    avgv = v.shift(1).rolling(20).mean()
    r25 = c / c.shift(25) - 1
    sig = (c > hi50) & (c > e50) & (e50 > e200) & (v >= 1.5 * avgv) & ((r25 - nifty_r25.reindex(c.index)) >= 0.05) & nifty_ok.reindex(c.index).fillna(False) & (avgv * c >= 1e8)
    return sig.fillna(False)


def run(data, nifty, variants=None):
    variants = variants or VARIANTS
    nc = nifty["c"]
    nifty_ok = nc > nc.ewm(span=50, adjust=False).mean()
    nifty_r25 = nc / nc.shift(25) - 1
    rows = []
    for sym, df in data.items():
        df = df.dropna(subset=["o", "h", "l", "c"]).copy()
        if len(df) < 300:
            continue
        sig = signals_for(df, nifty_ok, nifty_r25)
        a = atr14(df["h"], df["l"], df["c"])
        idx = df.index
        o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("o", "h", "l", "c"))
        free_until = {v: -1 for v in variants}                      # one open trade per stock PER VARIANT
        for t in np.flatnonzero(sig.to_numpy()):
            i0 = t + 1
            if i0 >= len(df) or not np.isfinite(a.iloc[t]) or a.iloc[t] <= 0 or o[i0] <= 0:
                continue
            if abs(o[i0] / c[t] - 1) > 0.20:                          # split/bonus artefact
                continue
            for v in variants:
                if i0 <= free_until[v]:
                    continue
                j, px = simulate_exit(v, o, h, l, c, i0, a.iloc[t])
                free_until[v] = j
                pct = (px / o[i0] - 1) * 100 - COST_PCT
                risk_pct = 2.0 * a.iloc[t] / o[i0] * 100
                rows.append({"variant": v, "sym": sym, "date": idx[t], "year": idx[t].year, "pct": pct, "R": pct / risk_pct, "days": j - i0 + 1})
    return pd.DataFrame(rows)


def stats(t):
    if not len(t):
        return "no trades"
    w = t.pct > 0
    gp, gl = t.loc[w, "pct"].sum(), -t.loc[~w, "pct"].sum()
    return f"n={len(t):5d} win {100 * w.mean():4.1f}% avg {t.pct.mean():+.2f}% med {t.pct.median():+.2f}% p10 {t.pct.quantile(0.1):+.1f}% PF {gp / gl if gl > 0 else float('inf'):4.2f} avg days {t.days.mean():4.1f}"


def report(tr):
    lines, summ = [], {}
    for v in VARIANTS:
        t = tr[tr.variant == v]
        a, b = t[t.year <= TRAIN_END], t[t.year > TRAIN_END]
        lines.append(f"{v:15} ALL {stats(t)}")
        lines.append(f"{'':15} TRAIN {stats(a)}")
        lines.append(f"{'':15} TEST  {stats(b)}")
        lines.append(f"{'':15} per year avg % (n): " + " ".join(f"{y}:{g.pct.mean():+.1f}({len(g)})" for y, g in t.groupby("year")))
        summ[v] = (a.pct.mean() if len(a) else np.nan, b.pct.mean() if len(b) else np.nan, b.pct.quantile(0.1) if len(b) else np.nan)
    base = summ["X1 HOLD20"]
    lines.append("\nDECISION (recommend over X1 only if TEST avg >= X1 + 0.3 AND TRAIN avg > X1 AND TEST p10 not worse than X1 by > 2 points):")
    for v in VARIANTS[1:]:
        tr_a, te_a, p10 = summ[v]
        ok = te_a - base[1] >= 0.3 and tr_a > base[0] and p10 >= base[2] - 2.0
        lines.append(f"  {v:15} train {tr_a:+.2f}% (X1 {base[0]:+.2f}), test {te_a:+.2f}% (X1 {base[1]:+.2f}), test p10 {p10:+.1f}% (X1 {base[2]:+.1f}) -> {'BETTER than X1' if ok else 'not better'}")
    return "\n".join(lines)


def report2(tr):
    lines, summ = [], {}
    for v in VARIANTS2:
        t = tr[tr.variant == v]
        a, b = t[t.year <= TRAIN_END], t[t.year > TRAIN_END]
        lines.append(f"{v:12} ALL {stats(t)}")
        lines.append(f"{'':12} TRAIN {stats(a)}")
        lines.append(f"{'':12} TEST  {stats(b)}")
        lines.append(f"{'':12} per year avg % (n): " + " ".join(f"{y}:{g.pct.mean():+.1f}({len(g)})" for y, g in t.groupby("year")))
        summ[v] = {"tr": a.pct.mean(), "te": b.pct.mean(), "tr10": a.pct.quantile(0.1), "te10": b.pct.quantile(0.1)}
    pairs = {"Y1 WIDE3": "X1 HOLD20", "Y2 WIDE4": "X1 HOLD20", "Y4 PCT10": "X1 HOLD20", "Y3 WIDE3-40": "X3 HOLD40", "Y5 BE-TRAIL": "X3 HOLD40"}
    lines.append("\nDECISION (TAIL-SAVER: test avg >= base - 0.3 and test p10 >= base p10 + 1.5, train same; RETURN-BOOST: test avg >= base + 0.3, p10 not worse by > 2, train avg higher):")
    for v, bname in pairs.items():
        x, bse = summ[v], summ[bname]
        tail = x["te"] >= bse["te"] - 0.3 and x["te10"] >= bse["te10"] + 1.5 and x["tr"] >= bse["tr"] - 0.3 and x["tr10"] >= bse["tr10"] + 1.5
        boost = x["te"] >= bse["te"] + 0.3 and x["te10"] >= bse["te10"] - 2.0 and x["tr"] > bse["tr"]
        verdict = "TAIL-SAVER" if tail else ("RETURN-BOOST" if boost else "not better")
        lines.append(f"  {v:12} vs {bname}: test {x['te']:+.2f}% (base {bse['te']:+.2f}), test p10 {x['te10']:+.1f}% (base {bse['te10']:+.1f}), train {x['tr']:+.2f}% (base {bse['tr']:+.2f}), train p10 {x['tr10']:+.1f}% (base {bse['tr10']:+.1f}) -> {verdict}")
    return "\n".join(lines)


def load_data():
    import yfinance as yf
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    sc = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
    sh = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), sc)).open("Ai360tradingAlgo")
    syms = [r[0].replace("NSE:", "").strip() for r in sh.worksheet("Nifty200").get_all_values()[2:] if r and r[0]]
    tick = [s + ".NS" for s in syms] + ["^NSEI"]
    dd = yf.download(tick, start="2018-01-01", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
    data = {}
    for s in syms:
        try:
            x = dd[s + ".NS"][["Open", "High", "Low", "Close", "Volume"]].dropna(subset=["Close"])
            x.columns = ["o", "h", "l", "c", "v"]
            x.index = pd.DatetimeIndex(x.index).tz_localize(None).normalize()
            data[s] = x
        except Exception:
            pass
    n = dd["^NSEI"][["Open", "High", "Low", "Close"]].dropna(subset=["Close"])
    n.columns = ["o", "h", "l", "c"]
    n.index = pd.DatetimeIndex(n.index).tz_localize(None).normalize()
    return data, n


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--run" not in argv and "--run2" not in argv:
        print(__doc__)
        return 0
    data, nifty = load_data()
    if "--run2" in argv:
        print(f"[SWING2] {len(data)} stocks; cost {COST_PCT}% round trip; TRAIN <= {TRAIN_END}\n")
        t2 = run(data, nifty, VARIANTS2)
        print(report2(t2))
        t2.to_csv("swing_bt_trades_batch2.csv", index=False)
        return 0
    print(f"[SWING] {len(data)} stocks, NIFTY {nifty.index[0].date()} -> {nifty.index[-1].date()}; cost {COST_PCT}% round trip; TRAIN <= {TRAIN_END}\n")
    tr = run(data, nifty)
    print(report(tr))
    tr.to_csv("swing_bt_trades.csv", index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
