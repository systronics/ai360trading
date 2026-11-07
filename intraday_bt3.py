"""
intraday_bt3.py v1.0 (2026-11-07) - BATCH 3: (a) 'liquidity' ideas and (b) the TIMEFRAME question (does a higher-timeframe trend filter - 15m, 1H, 4H, daily, weekly - add anything?). Research only.
Uses the cached real 5-minute NSE candles from intraday_bt.py (Upstox free token, 2022-04 -> today), the same costs (0.10% round trip in R), TRAIN <= 2024 / TEST 2025+, stop-first on ambiguous bars.

WHY (owner 2026-11-07): (1) 'modern traders use liquidity logic' - batch 1/2 tested only plain price patterns; (2) 'do you check 5m, 15m, 1H, daily, weekly together? does 4H matter? if not, remove it from TradingView'.

PRE-REGISTERED (written before the first run, run once). Long-only, one trade per symbol per day per rule, entries on completed 5-minute bars, exit by 15:15. F = the batch-2 context filter (NIFTY above its 50-day average, stock above its 50-day average, stock 20-day return above NIFTY's).
 LIQUIDITY RULES (all with F; judged against the batch-2 control BC1 = random entry, stop 1.0 x daily ATR, target 2R):
  L1 SWEEP-RECLAIM  after 09:30 price trades below the PREVIOUS DAY'S LOW (a 'sweep'), then within 6 bars a 5-min bar closes back above that low -> buy next open (before 13:30). Stop = lowest low since the sweep began. Target 2R.
  L2 OPEN-VOLUME    volume of the first three bars >= 2.0 x its own 20-day average AND the first three bars close above the day's open -> buy at the 09:30 bar's open. Stop = opening-range low. Target 2R.
  L3 VWAP-RECLAIM   after 10:00 a bar closes above VWAP after six consecutive closes below it, with volume >= 1.5 x its prior-20-bar average -> buy next open. Stop = lowest low of the below-VWAP stretch. Target 2R.
 TIMEFRAME TEST (no F): base P0 = first 5-min close above the previous day's high (09:30-14:00) -> buy next open, stop = 1.0 x daily ATR(14), target 2R. Each variant adds ONE alignment, 'the last COMPLETED higher-timeframe bar closes above its own EMA50':
  P15 (15-minute)  P60 (1-hour)  P240 (4-hour; NSE session bars 09:15-13:15 and 13:15-15:30)  PD (daily: previous close above the daily EMA50)  PW (weekly: previous completed week's EMA20 > EMA50)  PALL (15m + 1H + D + W together).
 SUCCESS CRITERION (fixed now): a rule/alignment counts as an improvement only if its average R beats its reference (L1-L3: BC1; P-variants: P0) by >= 0.05R in BOTH train and test AND average R > 0 in both AND has >= 300 TEST trades.
 If P240 does not beat P0 (and does not beat P60) it has no demonstrated value in this system.
USAGE: python intraday_bt3.py --run      (needs bt_cache/ from `intraday_bt.py --fetch`)
"""
import os
import random
import sys

import numpy as np
import pandas as pd

import intraday_bt as B

HTF = {"15": 15, "60": 60, "240": 240}


def htf_flags(df5):
    """Per 5-minute bar: bool columns a15/a60/a240 = the last COMPLETED higher-timeframe bar closed above its own EMA50. Pure on the dataframe."""
    d = df5[["ts", "c"]].copy()
    d["day"] = d.ts.dt.date.astype(str)
    mins = d.ts.dt.hour * 60 + d.ts.dt.minute - (9 * 60 + 15)
    out = pd.DataFrame({"ts": d.ts})
    for name, size in HTF.items():
        key = d["day"] + "_" + (mins // size).astype(str)
        g = d.groupby(key, sort=False)
        bars = pd.DataFrame({"end": g.ts.last() + pd.Timedelta(minutes=5), "c": g.c.last()}).reset_index(drop=True).sort_values("end")
        bars["flag"] = bars.c > bars.c.ewm(span=50, adjust=False).mean()
        m = pd.merge_asof(out[["ts"]].sort_values("ts"), bars[["end", "flag"]], left_on="ts", right_on="end", direction="backward")
        out["a" + name] = m["flag"].fillna(False).to_numpy(dtype=bool)
    return out


def daily_weekly_flags(daily):
    """{day: (daily_up, weekly_up)} known before each day. daily_up: previous close > daily EMA50. weekly_up: the previous COMPLETED week's EMA20 > EMA50."""
    c = daily.c
    dflag = (c.shift(1) > c.ewm(span=50, adjust=False).mean().shift(1))
    idx = pd.DatetimeIndex(pd.to_datetime(list(daily.index)))
    wc = pd.Series(c.to_numpy(), index=idx).resample("W-FRI").last().dropna()
    wup = (wc.ewm(span=20, adjust=False).mean() > wc.ewm(span=50, adjust=False).mean())
    out = {}
    for dy in daily.index:
        ts = pd.Timestamp(dy)
        prev_week_end = ts - pd.Timedelta(days=ts.weekday() + 3)          # the Friday before this day's week
        w = wup[wup.index <= prev_week_end]
        out[dy] = (bool(dflag.get(dy, False)) if pd.notna(dflag.get(dy, np.nan)) else False, bool(w.iloc[-1]) if len(w) else False)
    return out


def run_batch3(data, seed=23):
    mkt = B.market_context(data)
    rng = random.Random(seed)
    trades = []
    for sym, raw in data.items():
        if sym in ("NIFTY", "BANKNIFTY"):
            continue
        df, daily = B.prepare(raw)
        daily["r20"] = daily.c.shift(1) / daily.c.shift(21) - 1
        daily["pl"] = daily.l.shift(1)
        flags = htf_flags(raw)
        df = df.join(flags[["a15", "a60", "a240"]])
        dw = daily_weekly_flags(daily)
        first3v = df.groupby("day").apply(lambda x: float(x.v.iloc[:3].sum()))
        v3avg = first3v.rolling(20).mean().shift(1)
        by_day = {dy: idx for dy, idx in df.groupby("day").indices.items()}
        for dy in list(daily.index):
            if dy not in by_day:
                continue
            info = daily.loc[dy].to_dict()
            if not np.isfinite(info.get("gap", 0)) or info.get("gap", 0) > 0.20 or dy not in mkt:
                continue
            sub = df.iloc[by_day[dy]]
            o, h, l, c, v, hm = (sub[k].to_numpy() for k in ("o", "h", "l", "c", "v", "hm"))
            if len(o) < 20 or hm[0] != "09:15" or not B._ok(info.get("atr")):
                continue
            up, nr20 = mkt[dy]
            F = bool(up and B._ok(info.get("pc")) and B._ok(info.get("ma50")) and info["pc"] > info["ma50"] and np.isfinite(info.get("r20", np.nan)) and info["r20"] > nr20)
            a15, a60, a240 = sub["a15"].to_numpy(), sub["a60"].to_numpy(), sub["a240"].to_numpy()
            d_up, w_up = dw.get(dy, (False, False))
            vw = B._vwap(h, l, c, v)
            sigs = {}
            atr = info["atr"]
            # timeframe test (no F)
            if B._ok(info.get("ph")):
                for i in range(3, len(o) - 1):
                    if "09:30" <= hm[i] <= "14:00" and c[i] > info["ph"]:
                        ent, stp = o[i + 1], o[i + 1] - atr
                        for name, ok in (("P0", True), ("P15", a15[i]), ("P60", a60[i]), ("P240", a240[i]), ("PD", d_up), ("PW", w_up), ("PALL", a15[i] and a60[i] and d_up and w_up)):
                            if ok:
                                sigs[name] = (i + 1, ent, stp, 2.0)
                        break
            if F:
                cand = [i for i in range(len(o) - 1) if "09:30" <= hm[i] <= "14:00"]
                if cand:
                    j = rng.choice(cand) + 1
                    sigs["BC1 CONTROL"] = (j, o[j], o[j] - atr, 2.0)
                pl = info.get("pl")
                if B._ok(pl):                                                      # L1 sweep + reclaim
                    sw = None
                    for i in range(3, len(o) - 2):
                        if not ("09:30" <= hm[i] <= "13:30"):
                            continue
                        if sw is None and l[i] < pl:
                            sw = i                                                   # the sweep begins on this bar
                        if sw is not None:
                            if c[i] > pl:                                            # reclaim (the same bar counts: a wick below that closes back above)
                                sigs["L1 SWEEP-RECLAIM"] = (i + 1, o[i + 1], float(min(l[sw:i + 1])), 2.0)
                                break
                            if i - sw >= 6:
                                sw = None
                a3 = v3avg.get(dy, np.nan)
                if np.isfinite(a3) and a3 > 0 and float(v[:3].sum()) >= 2.0 * a3 and c[2] > o[0]:   # L2 open-volume surge
                    sigs["L2 OPEN-VOLUME"] = (3, o[3], float(min(l[:3])), 2.0)
                for i in range(26, len(o) - 1):                                    # L3 VWAP reclaim
                    if hm[i] < "10:00" or hm[i] > "14:00":
                        continue
                    if c[i] > vw[i] and all(c[i - k] < vw[i - k] for k in range(1, 7)) and v[i] >= 1.5 * float(np.mean(v[i - 20:i])):
                        sigs["L3 VWAP-RECLAIM"] = (i + 1, o[i + 1], float(min(l[i - 6:i + 1])), 2.0)
                        break
            for name, (i, entry, stop, mult) in sigs.items():
                res = B.simulate(o, h, l, c, hm, i, entry, stop, mult)
                if res:
                    trades.append({"rule": name, "sym": sym, "day": dy, "year": dy.year, "R": res[0], "stop_pct": (entry - stop) / entry * 100})
    return pd.DataFrame(trades)


def report3(trades):
    lines = []

    def block(rule):
        t = trades[trades.rule == rule]
        tr, te = t[t.year <= B.TRAIN_END], t[t.year > B.TRAIN_END]
        lines.append(f"{rule:18} ALL {B.summarize(t)} | TRAIN {B.summarize(tr)} | TEST {B.summarize(te)}")
        return (tr.R.mean() if len(tr) else np.nan, te.R.mean() if len(te) else np.nan, len(te))
    res = {r: block(r) for r in ["BC1 CONTROL", "L1 SWEEP-RECLAIM", "L2 OPEN-VOLUME", "L3 VWAP-RECLAIM", "P0", "P15", "P60", "P240", "PD", "PW", "PALL"] if (trades.rule == r).any()}
    lines.append("\nVERDICT (improvement = avg R beats its reference by >= 0.05R in BOTH train and test AND avg R > 0 in both AND >= 300 TEST trades):")
    for r, ref in (("L1 SWEEP-RECLAIM", "BC1 CONTROL"), ("L2 OPEN-VOLUME", "BC1 CONTROL"), ("L3 VWAP-RECLAIM", "BC1 CONTROL"), ("P15", "P0"), ("P60", "P0"), ("P240", "P0"), ("PD", "P0"), ("PW", "P0"), ("PALL", "P0")):
        if r not in res or ref not in res:
            lines.append(f"  {r}: not enough data")
            continue
        a, b = res[r], res[ref]
        ok = a[0] > 0 and a[1] > 0 and a[0] - b[0] >= 0.05 and a[1] - b[1] >= 0.05 and a[2] >= 300
        lines.append(f"  {r:17} vs {ref:11}: train {a[0]:+.3f}R ({b[0]:+.3f}), test {a[1]:+.3f}R ({b[1]:+.3f}), test trades {a[2]} -> {'IMPROVEMENT' if ok else 'no improvement'}")
    return "\n".join(lines)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--run" not in argv:
        print(__doc__)
        return 0
    data = B.load_cached()
    print(f"[BT3] {len(data)} symbols; cost {B.COST_PCT}% round trip; TRAIN <= {B.TRAIN_END}\n")
    t = run_batch3(data)
    print(report3(t))
    t.to_csv(os.path.join(B.CACHE, "trades_batch3.csv"), index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
