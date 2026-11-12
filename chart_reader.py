"""
chart_reader.py v1.0 (2026-11-12 NEW) - READ-ONLY automatic chart reader. Replaces "send me a TradingView screenshot":
from plain daily OHLC bars (yfinance, free) it finds swing pivots, support / resistance zones, a trend line, the EMA trend
and whether a stock is in a RETEST of a level it recently broke out above (the owner's favourite option setup).
INFORMATIONAL ONLY: prints text, writes nothing, sends nothing, nothing in the trading system reads it (same doctrine as
watch_plan / GateAudit / fetch_ath). Never an entry/SL/target - only "levels the chart shows".
USAGE: python chart_reader.py DLF [PRESTIGE ...]
Pure functions (read, zones, trendline, retest) take lists so they are unit-testable without any network.
"""
import sys

PIVOT_K = 3            # a swing high/low = highest/lowest of 2*K+1 bars
ZONE_TOL = 0.012       # pivots within 1.2% of each other form one zone
BREAKOUT_BUFFER = 0.003
RETEST_LOOKBACK = 15   # breakout must be within the last 15 bars
RETEST_BAND = (-0.01, 0.02)   # price within -1%..+2% of the broken level = retest area


def ema(vals, span):
    k = 2.0 / (span + 1)
    out, e = [], None
    for v in vals:
        e = v if e is None else v * k + e * (1 - k)
        out.append(e)
    return out


def pivots(highs, lows, k=PIVOT_K):
    """Indices of swing highs and swing lows (confirmed: needs k bars after)."""
    ph, pl = [], []
    for i in range(k, len(highs) - k):
        if highs[i] == max(highs[i - k:i + k + 1]):
            ph.append(i)
        if lows[i] == min(lows[i - k:i + k + 1]):
            pl.append(i)
    return ph, pl


def zones(prices, tol=ZONE_TOL):
    """Cluster pivot prices into zones -> [(level, touches)], strongest first."""
    out = []
    for p in sorted(prices):
        if out and abs(p - out[-1][0] / out[-1][1]) / p <= tol:    # [sum, n]
            out[-1][0] += p
            out[-1][1] += 1
        else:
            out.append([p, 1])
    res = [(round(s / n, 2), n) for s, n in out]
    return sorted(res, key=lambda z: -z[1])


def trendline(idx_vals):
    """Least-squares line through the last 3 pivot points -> (slope_per_bar, intercept) or None."""
    pts = idx_vals[-3:]
    if len(pts) < 2:
        return None
    n = len(pts)
    mx = sum(i for i, _ in pts) / n
    my = sum(v for _, v in pts) / n
    den = sum((i - mx) ** 2 for i, _ in pts)
    if den == 0:
        return None
    m = sum((i - mx) * (v - my) for i, v in pts) / den
    return m, my - m * mx


def retest_state(closes, highs, lows, res_levels):
    """Did price break a resistance zone in the last RETEST_LOOKBACK bars and is it now back at that level?
    -> dict(status, level, bars_since_breakout, dist_pct). status: RETEST / EXTENDED / FAILED / NONE."""
    n = len(closes)
    last = closes[-1]
    best = None
    for lvl in res_levels:
        brk = None
        for i in range(max(1, n - RETEST_LOOKBACK), n):
            if closes[i] > lvl * (1 + BREAKOUT_BUFFER) and closes[i - 1] <= lvl * (1 + BREAKOUT_BUFFER):
                brk = i
        if brk is None:
            continue
        dist = (last / lvl - 1)
        since = n - 1 - brk
        if dist < RETEST_BAND[0]:
            st = "FAILED"            # back under the level: breakout failed
        elif dist <= RETEST_BAND[1]:
            st = "RETEST" if since >= 1 else "NONE"
        else:
            st = "EXTENDED"          # running away from the level, not a retest
        cand = {"status": st, "level": lvl, "bars_since_breakout": since, "dist_pct": round(dist * 100, 2)}
        if best is None or since < best["bars_since_breakout"]:
            best = cand
    return best or {"status": "NONE", "level": None, "bars_since_breakout": None, "dist_pct": None}


def read(opens, highs, lows, closes):
    """Pure: everything the reader says about one daily series (oldest first, >= 60 bars)."""
    n = len(closes)
    if n < 60:
        return None
    last = closes[-1]
    e20, e50 = ema(closes, 20)[-1], ema(closes, 50)[-1]
    e200 = ema(closes, 200)[-1] if n >= 200 else None
    ph, pl = pivots(highs, lows)
    res_all = zones([highs[i] for i in ph if i >= n - 120])
    sup_all = zones([lows[i] for i in pl if i >= n - 120])
    above = sorted([z for z in res_all if z[0] > last * 1.002], key=lambda z: z[0])
    below = sorted([z for z in sup_all if z[0] < last * 0.998], key=lambda z: -z[0])
    broken = [z[0] for z in res_all if z[0] < last * 1.02 and z[1] >= 2]   # resistance zones with >=2 touches that price is at/above
    rt = retest_state(closes, highs, lows, broken)
    tl_low = trendline([(i, lows[i]) for i in pl if i >= n - 90])
    tl_high = trendline([(i, highs[i]) for i in ph if i >= n - 90])
    trend = "UP" if (last > e20 > e50) else ("DOWN" if (last < e20 < e50) else "MIXED")
    hi52 = max(highs[-250:])
    return {
        "close": round(last, 2), "ema20": round(e20, 2), "ema50": round(e50, 2), "ema200": round(e200, 2) if e200 else None,
        "trend": trend, "from_52w_high_pct": round((last / hi52 - 1) * 100, 2),
        "resistance": above[:2], "support": below[:2], "retest": rt,
        "uptrend_line_today": round(tl_low[0] * (n - 1) + tl_low[1], 2) if tl_low and tl_low[0] > 0 else None,
        "downtrend_line_today": round(tl_high[0] * (n - 1) + tl_high[1], 2) if tl_high and tl_high[0] < 0 else None,
    }


def describe(sym, r):
    if not r:
        return f"{sym}: not enough data"
    rt = r["retest"]
    lines = [f"{sym}: close {r['close']} | trend {r['trend']} (EMA20 {r['ema20']}, EMA50 {r['ema50']}, EMA200 {r['ema200']}) | {r['from_52w_high_pct']}% from 52-week high"]
    lines.append("  resistance above: " + (", ".join(f"{l} ({t} touches)" for l, t in r["resistance"]) or "none found (open sky / near high)"))
    lines.append("  support below: " + (", ".join(f"{l} ({t} touches)" for l, t in r["support"]) or "none found"))
    if r["uptrend_line_today"]:
        lines.append(f"  rising trend line (through recent swing lows) is at about {r['uptrend_line_today']} today")
    if r["downtrend_line_today"]:
        lines.append(f"  falling trend line (through recent swing highs) is at about {r['downtrend_line_today']} today")
    word = {"RETEST": "RETEST of a broken level - price is back at {level} ({dist_pct}% from it), breakout was {bars_since_breakout} bars ago",
            "EXTENDED": "broke {level} {bars_since_breakout} bars ago and has run {dist_pct}% above it - NOT a retest, extended",
            "FAILED": "broke {level} {bars_since_breakout} bars ago but is back BELOW it ({dist_pct}%) - failed breakout",
            "NONE": "no recent breakout/retest pattern"}[rt["status"]]
    lines.append("  retest: " + word.format(**{k: v for k, v in rt.items()}))
    return "\n".join(lines)


def fetch(sym, period="1y"):
    import yfinance as yf
    df = yf.Ticker(sym + ".NS").history(period=period, interval="1d", auto_adjust=False).dropna()
    return ([float(x) for x in df["Open"]], [float(x) for x in df["High"]], [float(x) for x in df["Low"]], [float(x) for x in df["Close"]])


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("usage: python chart_reader.py SYMBOL [SYMBOL ...]")
        return 0
    for s in argv:
        s = s.upper().replace("NSE:", "")
        try:
            print(describe(s, read(*fetch(s))))
        except Exception as e:                      # fail-open
            print(f"{s}: skipped ({str(e)[:100]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
