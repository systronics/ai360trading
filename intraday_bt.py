"""
intraday_bt.py v1.0 (2026-11-07) - honest INTRADAY BACKTEST on real NSE 5-minute candles (Upstox free Analytics Token, 2022-04 -> today). Research only: writes nothing to the sheet, trades nothing.

WHY (owner 2026-11-07): the owner wants the best intraday / next-day setups and a plan for intraday options. Opinions and guru win-rate claims are not evidence (a video that day showed 70-90% claims were 29-42% on 11 years of data with costs).
This measures rules on real candles, with costs, split into TRAIN (<= 2024) and TEST (2025+), and against a RANDOM-ENTRY CONTROL with the same stop/target structure.

PRE-REGISTERED RULES (written BEFORE the first run; no tuning loops - run once, read once). All long-only (buy-side), one trade per symbol per day per rule, entry only on completed 5-minute bars, exit by 15:15.
  R1 ORB-2R     opening range = first 3 bars (09:15-09:29). First bar close above the range high (09:30-11:30) -> buy next bar open. Stop = range midpoint. Target 2R.
  R2 ORB-3R     same as R1 with target 3R.
  R3 PDH-2R     first 5-min close above the previous day's high (09:30-14:00) while the previous close is above its own 50-day average -> buy next open. Stop = 0.5 x daily ATR(14). Target 2R.
  R4 EMA5-3R    'alert candle' (Subhash Pani's 5-EMA idea, long mirror): a bar whose HIGH is below EMA5. If a later bar (within 3 bars, 09:30-14:30) trades above the alert high -> buy at the alert high (or the open if it gaps above). Stop = alert low. Target 3R.
  R5 PIN-2R     (Mayank Raj idea) EMA9 > EMA15 and both rising vs 3 bars ago; a pin bar (lower wick >= 2 x body and >= 60% of the range) whose low is at/below EMA9; buy when a later bar (within 3 bars) trades above the pin high. Stop = pin low. Target 2R.
  R6 WATCH-2R   our own morning-watch-plan trigger: a 15-minute bar closes above the previous day's high (09:45-14:00) while the previous close is above its 50-day average -> buy next 5-min open. Stop = signal 15-min bar low. Target 2R.
  C0 CONTROL    random entry bar (09:30-14:00, seeded) with stop = 0.5 x daily ATR(14) and target 2R. If a real rule does not beat this, it has no edge.
  CARRY-A/B     'does a strong day continue tomorrow?': day closes in the top 20% of its range with volume >= 1.5 x its 20-day average and close above the previous high.
                A: buy at that day's last bar close, sell next day's 15:15 close.  B: buy next day's open, sell next day's 15:15 close.
Costs: round trip COST_PCT = 0.10% of price (STT + charges + slippage), expressed in R through the stop distance. If a bar touches both stop and target, the STOP is assumed to hit first (conservative).
Universe: NIFTY, BANKNIFTY and 30 liquid F&O stocks. Days with a >20% overnight jump are skipped (split/bonus artefacts).

BATCH 2 (pre-registered 2026-11-07 AFTER batch 1 lost everywhere; run ONCE, judged mainly on TEST). Same costs/split. Context filter F (all must hold, all known BEFORE the day):
  market up = NIFTY's previous close is above its own 50-day average;  stock trend = the stock's previous close is above its 50-day average;  relative strength = the stock's 20-day return is above NIFTY's 20-day return.
  B1 GAP-GO     F and the day opens 0.5%-3% above the previous close; first 5-min close (09:30-11:00) above the opening-range (first 3 bars) high -> buy next open. Stop = opening-range low. Target 3R.
  B2 TREND-VWAP F; first bar (10:00-11:30) that closes above VWAP, above the opening-range high and above the day's open -> buy next open. Stop = 1.0 x daily ATR(14). Target 2R.
  B3 PDH-F      F; first 5-min close above the previous day's high (09:30-14:00) -> buy next open. Stop = 1.0 x daily ATR(14) (wider than batch 1's 0.5). Target 2R.
  B4 CARRY-F    F and the day closes in the top 20% of its range with volume >= 1.5 x its 20-day average and a close above the previous high -> buy the last bar's close, sell next day's 15:10 close (percent, costs included).
  BC1 CONTROL   F and a random entry bar (09:30-14:00), stop 1.0 x daily ATR, target 2R (the control for B2/B3).   BC2 CONTROL  F, gap-up day, random entry after the opening range, stop = opening-range low, target 3R (the control for B1).
  SUCCESS CRITERION (fixed now): a rule shows an edge only if its average R is > 0 AND beats its control by >= 0.05R in BOTH train and test AND it has >= 300 trades in TEST. Anything else = no edge found.
USAGE: python intraday_bt.py --fetch [--from 2022-04-01]     download/cache candles (needs UPSTOX_ANALYTICS_TOKEN)
       python intraday_bt.py --run                            run the rules on the cached candles and print the tables
"""
import gzip
import json
import os
import random
import sys
import time
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

CACHE = "bt_cache"
COST_PCT = 0.10
EXIT_HM = "15:10"            # the bar that starts at 15:10 closes at 15:15; its close is the forced exit
TRAIN_END = 2024
UNIVERSE_STOCKS = ["RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "SBIN", "AXISBANK", "KOTAKBANK", "LT", "ITC", "BHARTIARTL", "MARUTI", "M&M", "TATASTEEL", "BAJFINANCE",
                   "SUNPHARMA", "HCLTECH", "WIPRO", "NTPC", "ONGC", "TECHM", "TITAN", "ADANIPORTS", "COALINDIA", "HINDALCO", "JSWSTEEL", "BPCL", "ETERNAL", "TRENT", "BEL"]
INDEX_KEYS = {"NIFTY": "NSE_INDEX|Nifty 50", "BANKNIFTY": "NSE_INDEX|Nifty Bank"}


# ───────────────────────────── data ─────────────────────────────
def _month_chunks(start, end):
    d = date(start.year, start.month, 1)
    while d <= end:
        nxt = date(d.year + (d.month == 12), (d.month % 12) + 1, 1)
        yield max(d, start), min(nxt - timedelta(days=1), end)
        d = nxt


def fetch_symbol(token, key, start, end, session=None):
    import requests
    http = session or requests
    rows = []
    for a, b in _month_chunks(start, end):
        url = f"https://api.upstox.com/v3/historical-candle/{key}/minutes/5/{b.isoformat()}/{a.isoformat()}"
        for attempt in range(4):
            r = http.get(url, headers={"Accept": "application/json", "Authorization": f"Bearer {token}"}, timeout=40)
            if r.status_code == 200:
                rows += ((r.json() or {}).get("data") or {}).get("candles") or []
                break
            if r.status_code in (429, 500, 502, 503):
                time.sleep(2 * (attempt + 1))
                continue
            break
        time.sleep(0.15)
    if not rows:
        return None
    df = pd.DataFrame(rows, columns=["ts", "o", "h", "l", "c", "v", "oi"])
    df["ts"] = pd.to_datetime(df["ts"], utc=True).dt.tz_convert("Asia/Kolkata")
    return df.drop(columns=["oi"]).drop_duplicates("ts").sort_values("ts").reset_index(drop=True)


def fetch_all(start):
    token = os.environ.get("UPSTOX_ANALYTICS_TOKEN", "").strip()
    if not token:
        raise SystemExit("UPSTOX_ANALYTICS_TOKEN not set")
    import live_prices_upstox as UP
    instr = UP.load_instruments()
    os.makedirs(CACHE, exist_ok=True)
    end = date.today()
    keys = dict(INDEX_KEYS)
    for s in UNIVERSE_STOCKS:
        if instr.get(s):
            keys[s] = instr[s]
        else:
            print(f"[BT] {s}: no instrument key, skipped")
    for name, key in keys.items():
        path = os.path.join(CACHE, name.replace("&", "_") + ".csv.gz")
        if os.path.exists(path):
            print(f"[BT] {name}: cached")
            continue
        df = fetch_symbol(token, key, start, end)
        if df is None or len(df) < 1000:
            print(f"[BT] {name}: no/low data ({0 if df is None else len(df)} bars)")
            continue
        df.to_csv(path, index=False, compression="gzip")
        print(f"[BT] {name}: {len(df)} bars {df.ts.iloc[0].date()} -> {df.ts.iloc[-1].date()}")


def load_cached():
    out = {}
    for fn in sorted(os.listdir(CACHE)) if os.path.isdir(CACHE) else []:
        if fn.endswith(".csv.gz"):
            df = pd.read_csv(os.path.join(CACHE, fn))
            df["ts"] = pd.to_datetime(df["ts"], utc=True).dt.tz_convert("Asia/Kolkata")
            out[fn[:-7]] = df
    return out


# ───────────────────────────── preparation ─────────────────────────────
def prepare(df):
    """Adds day, hm, EMAs, and daily aggregates (prev high/close, 50-day mean, daily ATR14, 20-day avg volume). Returns (df, dayinfo dict date->dict)."""
    d = df.copy()
    d["day"] = d.ts.dt.date
    d["hm"] = d.ts.dt.strftime("%H:%M")
    for n in (5, 9, 15):
        d[f"e{n}"] = d.c.ewm(span=n, adjust=False).mean()
    g = d.groupby("day")
    daily = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "v": g.v.sum()})
    pc = daily.c.shift(1)
    tr = pd.concat([daily.h - daily.l, (daily.h - pc).abs(), (daily.l - pc).abs()], axis=1).max(axis=1)
    daily["atr"] = tr.rolling(14).mean().shift(1)           # ATR known BEFORE the day
    daily["pc"], daily["ph"] = pc, daily.h.shift(1)
    daily["ma50"] = daily.c.rolling(50).mean().shift(1)
    daily["avgv20"] = daily.v.rolling(20).mean().shift(1)
    daily["gap"] = (daily.o / pc - 1).abs()
    return d, daily


def simulate(o, h, l, c, hm, i_entry, entry, stop, mult, cost_pct=COST_PCT):
    """One long trade on the day's bars. Entry at price `entry` inside bar i_entry (stop-order or next-open fill). Returns (R_after_costs, exit_hm, exit_price) or None.
    A bar that touches both stop and target counts as STOP first. Forced exit at the close of the bar starting at EXIT_HM."""
    risk = entry - stop
    if risk <= 0 or entry <= 0:
        return None
    target = entry + mult * risk
    n = len(o)
    for i in range(i_entry, n):
        if l[i] <= stop:
            px = min(stop, o[i]) if i > i_entry else stop      # a gap below the stop fills at the open
            return (px - entry) / risk - cost_pct / (risk / entry * 100.0), hm[i], px
        if h[i] >= target and i >= i_entry:
            return mult - cost_pct / (risk / entry * 100.0), hm[i], target
        if hm[i] >= EXIT_HM:
            return (c[i] - entry) / risk - cost_pct / (risk / entry * 100.0), hm[i], c[i]
    return None


# ───────────────────────────── rules ─────────────────────────────
def _ok(x):
    return x is not None and isinstance(x, (int, float, np.floating)) and bool(np.isfinite(x)) and x > 0


def rule_orb(day, mult):
    o, h, l, c, hm = day["o"], day["h"], day["l"], day["c"], day["hm"]
    if len(o) < 20 or hm[0] != "09:15":
        return None
    hi, lo = max(h[:3]), min(l[:3])
    if hi <= lo:
        return None
    for i in range(3, len(o) - 1):
        if "09:30" <= hm[i] <= "11:30" and c[i] > hi:
            return i + 1, o[i + 1], (hi + lo) / 2.0, mult
    return None


def rule_pdh(day, info):
    o, h, l, c, hm = day["o"], day["h"], day["l"], day["c"], day["hm"]
    if not (_ok(info.get("ph")) and _ok(info.get("atr")) and _ok(info.get("ma50")) and _ok(info.get("pc"))) or info["pc"] <= info["ma50"]:
        return None
    for i in range(3, len(o) - 1):
        if "09:30" <= hm[i] <= "14:00" and c[i] > info["ph"]:
            entry = o[i + 1]
            return i + 1, entry, entry - 0.5 * info["atr"], 2.0
    return None


def rule_alert5(day):
    o, h, l, c, hm, e5 = day["o"], day["h"], day["l"], day["c"], day["hm"], day["e5"]
    for i in range(1, len(o) - 4):
        if "09:30" <= hm[i] <= "14:30" and h[i] < e5[i]:
            for j in range(i + 1, min(i + 4, len(o))):
                if h[j] > h[i]:
                    entry = max(h[i], o[j])
                    return j, entry, l[i], 3.0
    return None


def rule_pin(day):
    o, h, l, c, hm, e9, e15 = day["o"], day["h"], day["l"], day["c"], day["hm"], day["e9"], day["e15"]
    for i in range(3, len(o) - 4):
        if not ("09:30" <= hm[i] <= "14:30"):
            continue
        body, rng = abs(c[i] - o[i]), h[i] - l[i]
        lower = min(o[i], c[i]) - l[i]
        if rng <= 0 or lower < 0.6 * rng or lower < 2 * max(body, 1e-9):
            continue
        if not (e9[i] > e15[i] and e9[i] > e9[i - 3] and e15[i] > e15[i - 3] and l[i] <= e9[i]):
            continue
        for j in range(i + 1, min(i + 4, len(o))):
            if h[j] > h[i]:
                return j, max(h[i], o[j]), l[i], 2.0
    return None


def rule_watch(day, info):
    o, h, l, c, hm = day["o"], day["h"], day["l"], day["c"], day["hm"]
    if not (_ok(info.get("ph")) and _ok(info.get("ma50")) and _ok(info.get("pc"))) or info["pc"] <= info["ma50"]:
        return None
    n = len(o)
    for k in range(0, n - 3, 3):                                   # 15-minute blocks of three 5-minute bars, aligned from 09:15
        end = k + 2
        if end >= n - 1 or not ("09:30" <= hm[k] <= "13:45") or int(hm[k][-2:]) % 15 != 0:
            continue
        blk_close, blk_low = c[end], min(l[k:end + 1])
        if blk_close > info["ph"]:
            return end + 1, o[end + 1], blk_low, 2.0
    return None


def rule_control(day, info, rng):
    o, hm = day["o"], day["hm"]
    if not _ok(info.get("atr")):
        return None
    cand = [i for i in range(len(o) - 1) if "09:30" <= hm[i] <= "14:00"]
    if not cand:
        return None
    i = rng.choice(cand) + 1
    return i, o[i], o[i] - 0.5 * info["atr"], 2.0


RULES = ["R1 ORB-2R", "R2 ORB-3R", "R3 PDH-2R", "R4 EMA5-3R", "R5 PIN-2R", "R6 WATCH-2R", "C0 CONTROL"]


def run_rules(data, seed=7):
    trades = []
    rng = random.Random(seed)
    for sym, raw in data.items():
        df, daily = prepare(raw)
        for dy, idx in df.groupby("day").indices.items():
            info = daily.loc[dy].to_dict()
            if not np.isfinite(info.get("gap", 0)) or info.get("gap", 0) > 0.20:
                continue
            sub = df.iloc[idx]
            day = {k: sub[k].to_numpy() for k in ("o", "h", "l", "c", "hm", "e5", "e9", "e15")}
            cands = {"R1 ORB-2R": rule_orb(day, 2.0), "R2 ORB-3R": rule_orb(day, 3.0), "R3 PDH-2R": rule_pdh(day, info), "R4 EMA5-3R": rule_alert5(day),
                     "R5 PIN-2R": rule_pin(day), "R6 WATCH-2R": rule_watch(day, info), "C0 CONTROL": rule_control(day, info, rng)}
            for name, sig in cands.items():
                if not sig:
                    continue
                i, entry, stop, mult = sig
                res = simulate(day["o"], day["h"], day["l"], day["c"], day["hm"], i, entry, stop, mult)
                if res:
                    trades.append({"rule": name, "sym": sym, "day": dy, "year": dy.year, "R": res[0], "stop_pct": (entry - stop) / entry * 100})
    return pd.DataFrame(trades)


def run_carry(data):
    out = []
    for sym, raw in data.items():
        df, daily = prepare(raw)
        days = list(daily.index)
        by_day = {dy: idx for dy, idx in df.groupby("day").indices.items()}
        for k in range(len(days) - 1):
            dy, nd = days[k], days[k + 1]
            r = daily.loc[dy]
            if not (r.h > r.l and r.avgv20 and r.v >= 1.5 * r.avgv20 and r.ph and r.c > r.ph and (r.c - r.l) / (r.h - r.l) >= 0.8):
                continue
            if (nd - dy).days > 5:
                continue
            nxt = df.iloc[by_day[nd]]
            exit_row = nxt[nxt.hm >= EXIT_HM].head(1)
            if exit_row.empty:
                continue
            exit_px, nopen = float(exit_row.c.iloc[0]), float(nxt.o.iloc[0])
            out.append({"rule": "CARRY-A buy close", "sym": sym, "day": dy, "year": dy.year, "pct": (exit_px / r.c - 1) * 100 - COST_PCT})
            out.append({"rule": "CARRY-B buy next open", "sym": sym, "day": dy, "year": dy.year, "pct": (exit_px / nopen - 1) * 100 - COST_PCT})
    return pd.DataFrame(out)


# ───────────────────────────── batch 2 (context-filtered) ─────────────────────────────
def _vwap(h, l, c, v):
    tp = (h + l + c) / 3.0
    cv = np.cumsum(v)
    return np.where(cv > 0, np.cumsum(tp * v) / np.where(cv > 0, cv, 1), c)


def market_context(data):
    """{day: (market_up, nifty_r20)} from the NIFTY candles: previous close above the 50-day average, and the 20-day return, both known before the day."""
    raw = data.get("NIFTY")
    if raw is None:
        return {}
    _, dly = prepare(raw)
    c = dly.c
    out = {}
    pc = c.shift(1)
    ma = dly.ma50
    r20 = c.shift(1) / c.shift(21) - 1
    for dy in dly.index:
        if np.isfinite(pc[dy]) and np.isfinite(ma[dy]) and np.isfinite(r20[dy]):
            out[dy] = (bool(pc[dy] > ma[dy]), float(r20[dy]))
    return out


def run_batch2(data, seed=11):
    mkt = market_context(data)
    rng = random.Random(seed)
    trades, carry = [], []
    for sym, raw in data.items():
        if sym in ("NIFTY", "BANKNIFTY"):
            continue
        df, daily = prepare(raw)
        daily["r20"] = daily.c.shift(1) / daily.c.shift(21) - 1
        days = list(daily.index)
        by_day = {dy: idx for dy, idx in df.groupby("day").indices.items()}
        for k, dy in enumerate(days):
            info = daily.loc[dy].to_dict()
            if dy not in mkt or not np.isfinite(info.get("gap", 0)) or info.get("gap", 0) > 0.20:
                continue
            up, nr20 = mkt[dy]
            if not (up and _ok(info.get("pc")) and _ok(info.get("ma50")) and info["pc"] > info["ma50"] and np.isfinite(info.get("r20", np.nan)) and info["r20"] > nr20):
                continue                                                   # context filter F
            sub = df.iloc[by_day[dy]]
            day = {c: sub[c].to_numpy() for c in ("o", "h", "l", "c", "v", "hm")}
            o, h, l, c, v, hm = day["o"], day["h"], day["l"], day["c"], day["v"], day["hm"]
            if len(o) < 20 or hm[0] != "09:15":
                continue
            vw = _vwap(h, l, c, v)
            orh, orl = max(h[:3]), min(l[:3])
            sigs = {}
            gap = o[0] / info["pc"] - 1
            if 0.005 <= gap <= 0.03:
                for i in range(3, len(o) - 1):
                    if "09:30" <= hm[i] <= "11:00" and c[i] > orh:
                        sigs["B1 GAP-GO"] = (i + 1, o[i + 1], orl, 3.0)
                        break
                cand = [i for i in range(3, len(o) - 1) if "09:30" <= hm[i] <= "14:00" and o[i + 1] > orl]
                if cand:
                    j = rng.choice(cand) + 1
                    sigs["BC2 CONTROL gap"] = (j, o[j], orl, 3.0)
            if _ok(info.get("atr")):
                for i in range(3, len(o) - 1):
                    if "10:00" <= hm[i] <= "11:30" and c[i] > vw[i] and c[i] > orh and c[i] > o[0]:
                        sigs["B2 TREND-VWAP"] = (i + 1, o[i + 1], o[i + 1] - info["atr"], 2.0)
                        break
                if _ok(info.get("ph")):
                    for i in range(3, len(o) - 1):
                        if "09:30" <= hm[i] <= "14:00" and c[i] > info["ph"]:
                            sigs["B3 PDH-F"] = (i + 1, o[i + 1], o[i + 1] - info["atr"], 2.0)
                            break
                cand = [i for i in range(len(o) - 1) if "09:30" <= hm[i] <= "14:00"]
                if cand:
                    j = rng.choice(cand) + 1
                    sigs["BC1 CONTROL"] = (j, o[j], o[j] - info["atr"], 2.0)
            for name, (i, entry, stop, mult) in sigs.items():
                res = simulate(o, h, l, c, hm, i, entry, stop, mult)
                if res:
                    trades.append({"rule": name, "sym": sym, "day": dy, "year": dy.year, "R": res[0], "stop_pct": (entry - stop) / entry * 100})
            # B4 carry
            if k + 1 < len(days) and info["h"] > info["l"] and info.get("avgv20") and info["v"] >= 1.5 * info["avgv20"] and _ok(info.get("ph")) and info["c"] > info["ph"] \
                    and (info["c"] - info["l"]) / (info["h"] - info["l"]) >= 0.8 and (days[k + 1] - dy).days <= 5:
                nxt = df.iloc[by_day[days[k + 1]]]
                ex = nxt[nxt.hm >= EXIT_HM].head(1)
                if not ex.empty:
                    carry.append({"rule": "B4 CARRY-F", "sym": sym, "day": dy, "year": dy.year, "pct": (float(ex.c.iloc[0]) / info["c"] - 1) * 100 - COST_PCT})
    return pd.DataFrame(trades), pd.DataFrame(carry)


BATCH2 = ["B1 GAP-GO", "BC2 CONTROL gap", "B2 TREND-VWAP", "B3 PDH-F", "BC1 CONTROL"]


def report_batch2(trades, carry):
    lines = []
    ctrl = {}
    for rule in BATCH2:
        t = trades[trades.rule == rule] if len(trades) else trades
        if not len(t):
            lines.append(f"{rule:16} no trades")
            continue
        tr, te = t[t.year <= TRAIN_END], t[t.year > TRAIN_END]
        ctrl[rule] = (tr.R.mean() if len(tr) else np.nan, te.R.mean() if len(te) else np.nan)
        per_year = " ".join(f"{y}:{g.R.mean():+.2f}({len(g)})" for y, g in t.groupby("year"))
        lines.append(f"{rule:16} ALL {summarize(t)} | TRAIN {summarize(tr)} | TEST {summarize(te)}")
        lines.append(f"{'':16} per year avg R (n): {per_year} | median stop {t.stop_pct.median():.2f}%")
    if len(carry):
        t = carry
        lines.append(f"{'B4 CARRY-F':16} ALL {summarize(t, 'pct', '%')} | TRAIN {summarize(t[t.year <= TRAIN_END], 'pct', '%')} | TEST {summarize(t[t.year > TRAIN_END], 'pct', '%')}")
    # verdict by the pre-registered criterion
    pairs = {"B1 GAP-GO": "BC2 CONTROL gap", "B2 TREND-VWAP": "BC1 CONTROL", "B3 PDH-F": "BC1 CONTROL"}
    lines.append("\nVERDICT (edge = avg R > 0 AND beats its control by >= 0.05R in BOTH train and test AND >= 300 TEST trades):")
    for r, cname in pairs.items():
        t = trades[trades.rule == r] if len(trades) else trades
        if not len(t) or r not in ctrl or cname not in ctrl:
            lines.append(f"  {r}: not enough data")
            continue
        tr, te = t[t.year <= TRAIN_END].R.mean(), t[t.year > TRAIN_END].R.mean()
        n_te = int((t.year > TRAIN_END).sum())
        ok = tr > 0 and te > 0 and tr - ctrl[cname][0] >= 0.05 and te - ctrl[cname][1] >= 0.05 and n_te >= 300
        lines.append(f"  {r}: train {tr:+.3f}R (control {ctrl[cname][0]:+.3f}), test {te:+.3f}R (control {ctrl[cname][1]:+.3f}), test trades {n_te} -> {'EDGE FOUND' if ok else 'no edge'}")
    return "\n".join(lines)


# ───────────────────────────── reporting ─────────────────────────────
def summarize(t, col="R", unit="R"):
    if t is None or not len(t):
        return "no trades"
    w = t[col] > 0
    gp, gl = t.loc[w, col].sum(), -t.loc[~w, col].sum()
    return f"n={len(t):5d} win {100 * w.mean():4.1f}% avg {t[col].mean():+.3f}{unit} PF {gp / gl if gl > 0 else float('inf'):4.2f}"


def report(trades, carry):
    lines = []
    for rule in RULES:
        t = trades[trades.rule == rule] if len(trades) else trades
        if not len(t):
            lines.append(f"{rule:14} no trades")
            continue
        tr, te = t[t.year <= TRAIN_END], t[t.year > TRAIN_END]
        per_year = " ".join(f"{y}:{g.R.mean():+.2f}({len(g)})" for y, g in t.groupby("year"))
        lines.append(f"{rule:14} ALL {summarize(t)} | TRAIN {summarize(tr)} | TEST {summarize(te)}")
        lines.append(f"{'':14} per year avg R (n): {per_year} | median stop {t.stop_pct.median():.2f}% | {len(t) / max(1, t.day.nunique()):.1f} trades per active day")
    for rule in sorted(carry.rule.unique()) if len(carry) else []:
        t = carry[carry.rule == rule]
        tr, te = t[t.year <= TRAIN_END], t[t.year > TRAIN_END]
        lines.append(f"{rule:22} ALL {summarize(t, 'pct', '%')} | TRAIN {summarize(tr, 'pct', '%')} | TEST {summarize(te, 'pct', '%')}")
    return "\n".join(lines)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--fetch" in argv:
        start = date.fromisoformat(argv[argv.index("--from") + 1]) if "--from" in argv else date(2022, 4, 1)
        fetch_all(start)
    if "--run2" in argv:
        data = load_cached()
        print(f"[BT2] {len(data)} symbols loaded; cost {COST_PCT}% round trip; TRAIN <= {TRAIN_END}, TEST > {TRAIN_END}\n")
        t2, c2 = run_batch2(data)
        print(report_batch2(t2, c2))
        t2.to_csv(os.path.join(CACHE, "trades_batch2.csv"), index=False)
    if "--run" in argv:
        data = load_cached()
        print(f"[BT] {len(data)} symbols loaded: {', '.join(data)}")
        trades = run_rules(data)
        carry = run_carry(data)
        print(f"[BT] cost assumption {COST_PCT}% round trip; stop-first on ambiguous bars; TRAIN <= {TRAIN_END}, TEST > {TRAIN_END}\n")
        print(report(trades, carry))
        trades.to_csv(os.path.join(CACHE, "trades.csv"), index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
