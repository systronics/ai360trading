"""
swing_bt3.py v1.0 (2026-11-07) - does a WEEKLY-trend alignment improve the daily 'Top picks' swing signal? Research only.
Same signal, universe (207 current Nifty200 stocks, 2018-26), hold-20 exit, cost 0.25% and TRAIN <= 2023 / TEST 2024+ as swing_bt.py.
PRE-REGISTERED (written before the run): SW = the base signal AND the previous COMPLETED week's weekly EMA20 > weekly EMA50 AND that week's close > its weekly EMA10.
IMPROVEMENT only if TEST average % per trade >= base + 0.3 AND TRAIN average >= base + 0.3 AND SW keeps at least 50% of the base trades. Otherwise the weekly filter adds nothing and can be dropped.
USAGE: python swing_bt3.py --run
"""
import sys

import numpy as np
import pandas as pd

import swing_bt as S


def weekly_flag(close):
    """Series indexed like `close` (daily): True when the previous COMPLETED week's EMA20 > EMA50 and its close > EMA10. Pure."""
    wc = close.resample("W-FRI").last().dropna()
    wf = (wc.ewm(span=20, adjust=False).mean() > wc.ewm(span=50, adjust=False).mean()) & (wc > wc.ewm(span=10, adjust=False).mean())
    out = []
    for d in close.index:
        prev_friday = d - pd.Timedelta(days=d.weekday() + 3)
        w = wf[wf.index <= prev_friday]
        out.append(bool(w.iloc[-1]) if len(w) else False)
    return pd.Series(out, index=close.index)


def run(data, nifty):
    nc = nifty["c"]
    nifty_ok = nc > nc.ewm(span=50, adjust=False).mean()
    nifty_r25 = nc / nc.shift(25) - 1
    rows = []
    for sym, df in data.items():
        df = df.dropna(subset=["o", "h", "l", "c"]).copy()
        if len(df) < 300:
            continue
        sig = S.signals_for(df, nifty_ok, nifty_r25)
        wf = weekly_flag(df["c"])
        a = S.atr14(df["h"], df["l"], df["c"])
        idx = df.index
        o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("o", "h", "l", "c"))
        free = {"BASE": -1, "SW": -1}
        for t in np.flatnonzero(sig.to_numpy()):
            i0 = t + 1
            if i0 >= len(df) or not np.isfinite(a.iloc[t]) or a.iloc[t] <= 0 or o[i0] <= 0 or abs(o[i0] / c[t] - 1) > 0.20:
                continue
            for name in ("BASE", "SW"):
                if name == "SW" and not wf.iloc[t]:
                    continue
                if i0 <= free[name]:
                    continue
                j, px = S.simulate_exit("X1 HOLD20", o, h, l, c, i0, a.iloc[t])
                free[name] = j
                rows.append({"variant": name, "sym": sym, "date": idx[t], "year": idx[t].year, "pct": (px / o[i0] - 1) * 100 - S.COST_PCT, "days": j - i0 + 1})
    return pd.DataFrame(rows)


def report(tr):
    lines, m = [], {}
    for v in ("BASE", "SW"):
        t = tr[tr.variant == v]
        a, b = t[t.year <= S.TRAIN_END], t[t.year > S.TRAIN_END]
        lines.append(f"{v:5} ALL {S.stats(t)}")
        lines.append(f"      TRAIN {S.stats(a)}")
        lines.append(f"      TEST  {S.stats(b)}")
        m[v] = (a.pct.mean(), b.pct.mean(), len(t))
    ok = m["SW"][1] >= m["BASE"][1] + 0.3 and m["SW"][0] >= m["BASE"][0] + 0.3 and m["SW"][2] >= 0.5 * m["BASE"][2]
    lines.append(f"\nVERDICT: SW train {m['SW'][0]:+.2f}% (base {m['BASE'][0]:+.2f}), test {m['SW'][1]:+.2f}% (base {m['BASE'][1]:+.2f}), trades kept {m['SW'][2]}/{m['BASE'][2]} -> {'IMPROVEMENT' if ok else 'no improvement'}")
    return "\n".join(lines)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--run" not in argv:
        print(__doc__)
        return 0
    data, nifty = S.load_data()
    print(f"[SWING3] {len(data)} stocks\n")
    print(report(run(data, nifty)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
