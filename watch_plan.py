"""
watch_plan.py — pre-market WATCH PLAN for intraday / option ideas + higher-timeframe context  (v1.0, 2026-10-19)
==============================================================================================
WHY (owner decision 2026-10-19)
  Free infrastructure cannot send instant alerts: the live price file refreshes every 5 minutes, the scanner
  queues, and the bot checks every 5 minutes, so an intraday / option alert can be ~10-15 minutes old in the worst
  case. Instead of pretending to be fast, members get a PLAN before the market opens (what to watch, where the
  trigger and the chase limit are, what cancels the idea) and use their OWN live chart (TradingView + the
  ai360trading indicator, zero delay) to take the entry.

WHAT IT BUILDS (everything computed fresh from completed daily bars, so it never depends on a stale sheet column)
  * candidate pool from the Nifty200 sheet: option-eligible / liquid stocks, strongest relative strength first
  * HIGHER-TIMEFRAME CHECKLIST per stock (7 points):
        1 daily close above 50-day EMA        2 50-day EMA above 200-day EMA     3 weekly close above 10-week EMA
        4 weekly RSI >= 50                    5 daily RSI between 50 and 68       6 ADX >= 18 with +DI above -DI
        7 yesterday's volume >= 1.0x its 20-day average
  * levels: trigger = previous-day high (act on a 15-minute CLOSE above it), chase limit, cancel level
  * market context (NIFTY daily and weekly trend, RSI) and a NO-PLAN day when the bot's regime is bearish
  * logs every plan to a WatchPlan sheet tab and scores it the next morning (did the trigger hit, how did the
    day close vs the trigger) so the plan's real hit-rate becomes visible evidence.

DOCTRINE: informational only. Nothing here is a gate for trading_bot.py's entry/exit logic, paper ledger or
position sizing. FULLY FAIL-OPEN: any error -> no plan message, the rest of the bot is untouched.
Buy-side only (CE ideas); never a PE/short idea.
"""

import math
from datetime import datetime, timedelta

import pytz

IST = pytz.timezone("Asia/Kolkata")
WP_TAB = "WatchPlan"
WP_HEADER = ["Date", "Symbol", "Score", "Setup", "Option_OK", "Trigger", "Chase_Limit", "Cancel_Below", "Support", "Resistance",
             "Scored", "Triggered", "Day_High", "Day_Low", "Day_Close", "Close_vs_Trigger_%"]
MAX_ITEMS = 5
MIN_SCORE = 5
POOL = 40


# ───────────────────────────── indicators (pure) ────────────────────────────

def _rsi(closes, n=14):
    if len(closes) < n + 2:
        return None
    gains = losses = 0.0
    for i in range(1, n + 1):
        d = closes[i] - closes[i - 1]
        gains += max(d, 0)
        losses += max(-d, 0)
    ag, al = gains / n, losses / n
    for i in range(n + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        ag = (ag * (n - 1) + max(d, 0)) / n
        al = (al * (n - 1) + max(-d, 0)) / n
    if al == 0:
        return 100.0
    return 100 - 100 / (1 + ag / al)


def _ema(vals, span):
    a = 2.0 / (span + 1)
    e, out = vals[0], []
    for v in vals:
        e = a * v + (1 - a) * e
        out.append(e)
    return out


def _adx(highs, lows, closes, n=14):
    """Wilder ADX/DI. Returns (adx, plus_di, minus_di) or None."""
    if len(closes) < 2 * n + 2:
        return None
    tr, pdm, mdm = [], [], []
    for i in range(1, len(closes)):
        up, dn = highs[i] - highs[i - 1], lows[i - 1] - lows[i]
        pdm.append(up if (up > dn and up > 0) else 0.0)
        mdm.append(dn if (dn > up and dn > 0) else 0.0)
        tr.append(max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])))
    atr, p, m = sum(tr[:n]), sum(pdm[:n]), sum(mdm[:n])
    dxs = []
    pdi = mdi = 0.0
    for i in range(n, len(tr)):
        if i > n:
            atr = atr - atr / n + tr[i]
            p = p - p / n + pdm[i]
            m = m - m / n + mdm[i]
        pdi = 100 * p / atr if atr else 0.0
        mdi = 100 * m / atr if atr else 0.0
        dxs.append(100 * abs(pdi - mdi) / (pdi + mdi) if (pdi + mdi) else 0.0)
    if len(dxs) < n:
        return None
    adx = sum(dxs[:n]) / n
    for d in dxs[n:]:
        adx = (adx * (n - 1) + d) / n
    return adx, pdi, mdi


def _atr(highs, lows, closes, n=14):
    trs = [max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])) for i in range(1, len(closes))]
    if len(trs) < n:
        return None
    a = sum(trs[:n]) / n
    for t in trs[n:]:
        a = (a * (n - 1) + t) / n
    return a


def analyse(rows):
    """rows = list of (date, open, high, low, close, volume), oldest first, COMPLETED sessions only.
    Returns a dict of context + levels + checklist score, or None if there is too little history."""
    if len(rows) < 220:
        return None
    d = [r[0] for r in rows]
    h = [float(r[2]) for r in rows]
    l = [float(r[3]) for r in rows]
    c = [float(r[4]) for r in rows]
    v = [float(r[5] or 0) for r in rows]
    last = c[-1]
    e20, e50, e200 = _ema(c, 20)[-1], _ema(c, 50)[-1], _ema(c, 200)[-1]
    rsi_d = _rsi(c)
    ax = _adx(h, l, c)
    atr = _atr(h, l, c)
    if rsi_d is None or ax is None or atr is None:
        return None
    # weekly closes: last close of each ISO week
    wk = {}
    for dt_, cl in zip(d, c):
        iso = dt_.isocalendar()
        wk[(iso[0], iso[1])] = cl
    wc = [wk[k] for k in sorted(wk)]
    if len(wc) < 30:
        return None
    w_e10 = _ema(wc, 10)[-1]
    rsi_w = _rsi(wc)
    avgv = sum(v[-21:-1]) / 20 if sum(v[-21:-1]) else 0
    vol_x = (v[-1] / avgv) if avgv else None
    pdh, pdl = h[-1], l[-1]
    sup5, sup20, res20 = min(l[-5:]), min(l[-20:]), max(h[-20:])
    checks = [
        last > e50,
        e50 > e200,
        wc[-1] > w_e10,
        (rsi_w or 0) >= 50,
        50 <= rsi_d <= 68,
        ax[0] >= 18 and ax[1] > ax[2],
        (vol_x or 0) >= 1.0,
    ]
    near_pdh = (pdh / last - 1) * 100
    if last >= max(h[-21:-1]) * 0.999:
        setup = "breakout day, wait for a pullback or a 15m close above the high"
    elif abs(last / e20 - 1) <= 0.015:
        setup = "pullback to the 20-day average"
    elif near_pdh <= 1.5:
        setup = "close to the previous-day high"
    else:
        setup = "building, needs a push above the previous-day high"
    return {
        "date": d[-1], "close": last, "ema20": e20, "ema50": e50, "ema200": e200, "rsi_d": rsi_d, "rsi_w": rsi_w,
        "adx": ax[0], "pdi": ax[1], "mdi": ax[2], "atr": atr, "vol_x": vol_x, "weekly_up": wc[-1] > w_e10,
        "pdh": pdh, "pdl": pdl, "sup5": sup5, "sup20": sup20, "res20": res20, "score": sum(1 for x in checks if x),
        "checks": checks, "setup": setup, "extended": last > e20 * 1.06 or rsi_d > 72,
    }


def plan_item(sym, a):
    """Trigger / chase / cancel levels from an analysis dict."""
    trig = a["pdh"]
    return {
        "symbol": sym, "score": a["score"], "setup": a["setup"], "trigger": round(trig, 2),
        "chase": round(trig + 0.3 * a["atr"], 2), "cancel": round(a["pdl"], 2),
        "support": round(a["sup5"], 2), "resistance": round(a["res20"], 2), "a": a,
    }


# ───────────────────────────── data ─────────────────────────────────────────

def _completed(df, now=None):
    """Drop today's partial candle if the market is still open."""
    now = now or datetime.now(IST)
    if len(df) and df.index[-1].date() == now.date() and (now.hour * 60 + now.minute) < 15 * 60 + 45:
        return df.iloc[:-1]
    return df


def _rows(df):
    out = []
    for ts, r in df.iterrows():
        out.append((ts.date(), r["Open"], r["High"], r["Low"], r["Close"], r.get("Volume", 0)))
    return out


def fetch_analyses(symbols, now=None):
    """{symbol: analysis} for NSE symbols (without the NSE: prefix). One batched yfinance call."""
    import yfinance as yf
    out = {}
    if not symbols:
        return out
    raw = yf.download([s + ".NS" for s in symbols], period="2y", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
    for s in symbols:
        try:
            df = raw[s + ".NS"].dropna(subset=["Close", "High", "Low"])
            a = analyse(_rows(_completed(df, now)))
            if a:
                out[s] = a
        except Exception:
            continue
    return out


def htf_line(sym, now=None):
    """One-line higher-timeframe check for a live entry alert (fail-open -> '')."""
    try:
        a = fetch_analyses([sym.replace("NSE:", "").strip()], now).get(sym.replace("NSE:", "").strip())
        if not a:
            return ""
        d = "UP" if (a["close"] > a["ema50"] and a["ema50"] > a["ema200"]) else "MIXED" if a["close"] > a["ema50"] else "DOWN"
        w = "UP" if a["weekly_up"] else "DOWN"
        vol = f"{a['vol_x']:.1f}x" if a["vol_x"] else "n/a"
        return (f"📊 Bade timeframe: Daily {d} | Weekly {w} | RSI d{a['rsi_d']:.0f}/w{a['rsi_w']:.0f} | ADX {a['adx']:.0f} | Vol {vol}"
                + chr(10))
    except Exception:
        return ""


# ───────────────────────────── market + sheet ───────────────────────────────

def market_context():
    """NIFTY daily/weekly trend dict, or None."""
    try:
        import yfinance as yf
        df = yf.download("^NSEI", period="2y", interval="1d", progress=False, auto_adjust=False)
        df.columns = df.columns.get_level_values(0)
        a = analyse(_rows(_completed(df.dropna(subset=["Close"]))))
        return a
    except Exception:
        return None


def candidates_from_sheet(nifty_ws):
    """Header-based read of the Nifty200 sheet -> [(symbol, option_ok, rs, sector, sector_trend)] strongest RS first."""
    vals = nifty_ws.get_all_values()
    head = [h.strip().lower() for h in vals[0]]

    def col(*names):
        for n in names:
            if n.lower() in head:
                return head.index(n.lower())
        return None

    cs, cr, cst, csec, copt, cn2 = col("nse_symbol"), col("rs"), col("sector_trend"), col("sector"), col("options"), col("n200")
    out = []
    for r in vals[1:]:
        try:
            sym = r[cs].replace("NSE:", "").strip()
            if not sym or "NIFTY" in sym.upper():
                continue
            rs = float(str(r[cr]).replace("%", "").replace(",", "")) if cr is not None and r[cr] not in ("", None) else None
            if rs is None:
                continue
            opt = (r[copt].strip().upper() in ("N50", "YES")) if copt is not None else False
            if cn2 is not None and r[cn2].strip().upper() == "EX":
                continue
            out.append((sym, opt, rs, r[csec] if csec is not None else "", r[cst] if cst is not None else ""))
        except Exception:
            continue
    out.sort(key=lambda x: x[2], reverse=True)
    return out[:POOL]


# ───────────────────────────── message ──────────────────────────────────────

def _fmt(v):
    return f"{v:,.0f}" if v >= 1000 else f"{v:,.2f}"


def _trend_word(a):
    if a["close"] > a["ema50"] and a["ema50"] > a["ema200"]:
        return "UP"
    return "MIXED" if a["close"] > a["ema50"] else "DOWN"


def build_messages(now, is_bullish, mkt, items, opt_flags, sector_by_sym, weak_mkt=False):
    date_s = now.strftime("%d %b %Y")
    if mkt:
        mline = (f"Nifty: Daily {_trend_word(mkt)} (50-DMA {'upar' if mkt['close'] > mkt['ema50'] else 'neeche'}) | "
                 f"Weekly {'UP' if mkt['weekly_up'] else 'DOWN'} | RSI d{mkt['rsi_d']:.0f}")
    else:
        mline = "Nifty context unavailable"
    if not is_bullish or not items:
        why = "market weak hai" if not is_bullish else "koi stock hamare 7-point checklist me pass nahi hua"
        adv = (f"📋 <b>MORNING WATCH PLAN — {date_s}</b>\n━━━━━━━━━━━━━━━━━━━━\n{mline}\n\n"
               f"🚫 Aaj intraday/option ka plan NAHI: {why}.\nIntezaar bhi ek position hai. Sirf swing watchlist par nazar rakhe.\n")
        basic = (f"📋 <b>Morning watch plan — {date_s}</b>\n{mline}\n🚫 Aaj intraday/option plan nahi ({why}).\n\n"
                 f"📈 Swing signals hamara main product hai — <b>ai360trading.in/membership</b>")
        return adv, basic
    caution = ["🟠 Market kamzor hai (Nifty daily + weekly dono neeche): sirf top 2 A+ setup, size aur chhota, jaldi book kare."] if weak_mkt else []
    lines = [f"📋 <b>MORNING WATCH PLAN — {date_s}</b>", "━━━━━━━━━━━━━━━━━━━━", mline] + caution + [
             "Rule: entry sirf 15m CANDLE CLOSE par. Level se CHASE mat karo. Alert/plan 5-10 min purana ho sakta hai — apna live chart dekhe.", ""]
    for k, it in enumerate(items, 1):
        a = it["a"]
        sec = sector_by_sym.get(it["symbol"], "")
        ce = " | CE idea (1-2 din hold)" if opt_flags.get(it["symbol"]) else ""
        vol = f"{a['vol_x']:.1f}x" if a["vol_x"] else "n/a"
        lines += [
            f"<b>{k}) {it['symbol']}</b> {('(' + sec + ') ') if sec else ''}— checklist {it['score']}/7{ce}",
            f"   Daily: {_trend_word(a)} | Weekly: {'UP' if a['weekly_up'] else 'DOWN'} | RSI d{a['rsi_d']:.0f}/w{a['rsi_w']:.0f} | ADX {a['adx']:.0f} | Vol {vol}",
            f"   Trigger: 15m close ₹{_fmt(it['trigger'])} ke upar (pichhle din ka high)",
            f"   Chase limit: ₹{_fmt(it['chase'])} ke upar ho to SKIP",
            f"   Cancel: 15m close ₹{_fmt(it['cancel'])} (pichhle din ka low) ke neeche | 5-din Support ₹{_fmt(it['support'])} | Resistance ₹{_fmt(it['resistance'])}",
            f"   Setup: {a['setup']}", ""]
    lines.append("⚠️ Option me sirf CE aur sirf 1-2 din hold. Size chhota rakhe, stop-loss ke bina trade nahi. Ye plan hai, advice nahi.")
    adv = "\n".join(lines)
    names = ", ".join(i["symbol"] for i in items)
    basic = (f"📋 <b>Morning watch plan — {date_s}</b>\n{mline}\n"
             f"{len(items)} stock(s) pass hue hamare 7-point higher-timeframe checklist me. Levels (trigger / chase limit / cancel) sirf Advance/Premium members ko bheje gaye.\n\n"
             f"📈 <b>Join Advance @ ₹699/month</b>\n📱 ai360trading.in/membership")
    return adv, basic


# ───────────────────────────── build + log + score ──────────────────────────

def build_plan(nifty_ws, is_bullish, now=None):
    """Return (advance_msg, basic_msg, items) or None on any failure (fail-open)."""
    now = now or datetime.now(IST)
    cands = candidates_from_sheet(nifty_ws)
    if not cands:
        return None
    syms = [c[0] for c in cands]
    an = fetch_analyses(syms, now)
    opt = {c[0]: c[1] for c in cands}
    sec = {c[0]: c[3] for c in cands}
    pool = []
    for s in syms:
        a = an.get(s)
        if not a or a["extended"] or a["score"] < MIN_SCORE:
            continue
        pool.append(plan_item(s, a))
    # best checklist first; among equals prefer option-eligible then stronger relative strength (pool is RS-ordered)
    pool.sort(key=lambda it: (-it["score"], 0 if opt.get(it["symbol"]) else 1))
    items = pool[:MAX_ITEMS]
    mkt = market_context()
    weak_mkt = bool(mkt and not mkt["weekly_up"] and mkt["close"] < mkt["ema50"])
    if weak_mkt:
        items = items[:2]          # in our backtest breakouts were weaker with the index under its 50-day average
    adv, basic = build_messages(now, is_bullish, mkt, items, opt, sec, weak_mkt)
    return adv, basic, items, opt


def log_plan(ss, items, opt, now):
    try:
        try:
            ws = ss.worksheet(WP_TAB)
        except Exception:
            ws = ss.add_worksheet(title=WP_TAB, rows=500, cols=len(WP_HEADER))
            ws.update(range_name="A1", values=[WP_HEADER])
        today = now.strftime("%Y-%m-%d")
        existing = {(r[0], r[1]) for r in ws.get_all_values()[1:] if len(r) > 1}
        rows = []
        for it in items:
            if (today, it["symbol"]) in existing:
                continue
            rows.append([today, it["symbol"], it["score"], it["setup"], "YES" if opt.get(it["symbol"]) else "", it["trigger"], it["chase"],
                         it["cancel"], it["support"], it["resistance"], "", "", "", "", "", ""])
        if rows:
            ws.append_rows(rows, value_input_option="USER_ENTERED")
        print(f"[WATCHPLAN] logged {len(rows)} rows")
    except Exception as e:
        print(f"[WATCHPLAN] log skipped: {e}")


def score_plan(ss, now=None):
    """Score earlier plans (trigger hit? close vs trigger?) once their session is complete. Fail-open."""
    try:
        import yfinance as yf
        now = now or datetime.now(IST)
        ws = ss.worksheet(WP_TAB)
        vals = ws.get_all_values()
        today = now.strftime("%Y-%m-%d")
        todo = [(i + 2, r) for i, r in enumerate(vals[1:]) if len(r) > 10 and r[10] != "YES" and r[0] < today]
        updates = []
        for rown, r in todo[:60]:
            d0 = datetime.strptime(r[0], "%Y-%m-%d").date()
            df = yf.download(r[1] + ".NS", start=str(d0), end=str(d0 + timedelta(days=4)), interval="1d", progress=False, auto_adjust=False)
            df.columns = df.columns.get_level_values(0)
            df = df.dropna(subset=["Close"])
            row = df[df.index.date == d0]
            if row.empty:
                continue
            hi, lo, cl = float(row["High"].iloc[0]), float(row["Low"].iloc[0]), float(row["Close"].iloc[0])
            trig = float(r[5])
            hit = hi > trig
            updates.append({"range": f"K{rown}:P{rown}", "values": [["YES", "YES" if hit else "NO", round(hi, 2), round(lo, 2), round(cl, 2),
                                                                      round((cl / trig - 1) * 100, 2) if hit else ""]]})
        for j in range(0, len(updates), 50):
            ws.batch_update(updates[j:j + 50], value_input_option="USER_ENTERED")
        print(f"[WATCHPLAN] scored {len(updates)} earlier plan rows")
    except Exception as e:
        print(f"[WATCHPLAN] scoring skipped: {e}")
