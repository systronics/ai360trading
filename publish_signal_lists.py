"""
publish_signal_lists.py — public SIP-accumulation + breakout lists for the website
=================================================================================
v1.0 (2026-10-18)

Reads the BottomScanner tab (built by fetch_bottom_levels.py) and writes a
public-safe static file, _data/signal_lists.json, for the Jekyll pages
/sip-accumulation/ and /breakout-signals/. Same doctrine as publish_swing_board.py /
performance_stats.write_data_json:

  * TEASER ONLY — symbol, sector, price, a few descriptive numbers and a level.
    Never an entry price, stop-loss, target or position size (those stay in Telegram
    for Advance/Premium members).
  * FAIL-OPEN — any read/compute error leaves the existing JSON untouched; an empty
    result never overwrites a good file.
  * INFORMATIONAL — nothing in trading_bot.py / appscript.gs reads these lists.

Lists
  SIP accumulation : BottomScanner SIP_Zone == "ACCUMULATION ZONE" (>=25%... see below)
                     = deep correction + tight 20-day base + liquid. An INVESTING list
                     (buy in tranches), NOT a timing signal — the backtest found no
                     reliable timing edge in buying drawdowns.
  Breakout         : BottomScanner Breakout_Signal != "-" = 50-day closing-high breakout
                     or Pine trendline breakout, above EMA50, liquid. The only rules that
                     beat random entry in the 5-year / 194-stock daily backtest
                     (+3.3% / +2.9% avg per trade vs +1.7% random; win rate ~41%;
                     median trade is a small loss, profit comes from the few big winners).

Usage:  python publish_signal_lists.py          (writes _data/signal_lists.json)
        python publish_signal_lists.py --dry    (prints, writes nothing)
"""

import os, sys, json, re
from datetime import datetime, timedelta
import pytz

IST        = pytz.timezone("Asia/Kolkata")
SHEET_NAME = "Ai360tradingAlgo"
TAB        = "BottomScanner"
OUT_PATH   = "_data/signal_lists.json"
SIP_MAX      = 10
BREAKOUT_MAX = 15
TOP_MAX      = 8
# v1.2 (2026-11-06, owner: 'less and perfect entries, easy to understand'). Evidence (5y, ~200 large stocks, daily bars, entry = next open, 0.25% cost, train<=2024 / test 2025-26):
#   TOP PICK rule  = 50-day closing-high breakout TODAY + uptrend (close > EMA50 > EMA200) + volume >= 1.5x its 20-day average + RS vs Nifty >= 5 + NIFTY above its 50-EMA
#                    -> +3.58%/trade after 20 days, 59% win, ~3 signals/day (all breakouts: +1.66%, 55%, 17/day; random stock: +1.14%); test period +1.55% vs +0.12% random; 2026 so far -0.8% (small sample).
#   Adding 'RSI <= 70' made it WORSE (+1.7%), so it is not used here (the trading bot's own RSI gates are untouched).
#   SIP list       = 15-35% below the 52-week high BUT still above the 50- and 200-day averages (a dip inside an uptrend), liquid, ranked by dividend yield.
#                    60-day return +5.8% vs +5.5% for a random stock: no timing edge, but it avoids falling knives. The old rule (>=25% below high + tight base) did WORSE than random (+2.2%).
TOP_MIN_VOL_X  = 1.5
TOP_MIN_RS     = 5.0
TOP_MIN_LIQ_CR = 10.0


def _connect():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        with open("service_account.json") as f:
            raw = f.read().strip()
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)
    return gspread.authorize(creds).open(SHEET_NAME).worksheet(TAB)


def _f(v):
    try:
        return float(v)
    except Exception:
        return None


def _market_trend():
    """NIFTY close vs its own 50-day EMA (daily). Fail-open -> None."""
    try:
        import yfinance as yf
        d = yf.download("^NSEI", period="9mo", interval="1d", progress=False, auto_adjust=False)
        d.columns = d.columns.get_level_values(0)
        c = d["Close"].dropna()
        ema50 = c.ewm(span=50, adjust=False).mean()
        last, e = float(c.iloc[-1]), float(ema50.iloc[-1])
        return {"up": last > e, "close": round(last), "ema50": round(e),
                "label": "NIFTY is above its 50-day average" if last > e else "NIFTY is below its 50-day average"}
    except Exception as ex:
        print(f"[SIGNALS] market trend skipped: {ex}")
        return None


def top_pick_check(closes, volumes, rs, market_up, min_liq_cr=TOP_MIN_LIQ_CR):
    """Pure rule check on COMPLETED daily bars (oldest first). Returns a dict of the numbers when every condition holds, else None.
    Conditions: close > highest close of the prior 50 sessions; close > EMA50 > EMA200; volume >= 1.5x the prior-20-session average; RS >= 5; NIFTY above its 50-EMA; liquid (>= Rs 10 Cr/day)."""
    try:
        n = len(closes)
        if n < 210 or len(volumes) != n or not market_up or rs is None or rs < TOP_MIN_RS:
            return None
        c = [float(x) for x in closes]
        v = [float(x) for x in volumes]
        lvl = max(c[-51:-1])
        if not c[-1] > lvl:
            return None

        def ema(vals, span):
            k, e = 2.0 / (span + 1), vals[0]
            for x in vals[1:]:
                e = x * k + e * (1 - k)
            return e
        e50, e200 = ema(c, 50), ema(c, 200)
        if not (c[-1] > e50 > e200):
            return None
        avg20 = sum(v[-21:-1]) / 20.0
        if avg20 <= 0:
            return None
        volx = v[-1] / avg20
        if volx < TOP_MIN_VOL_X or avg20 * c[-1] / 1e7 < min_liq_cr:
            return None
        return {"level": round(lvl, 2), "close": round(c[-1], 2), "vol_x": round(volx, 1), "ext_pct": round((c[-1] / lvl - 1) * 100, 1)}
    except Exception:
        return None


def _top_picks(rows, market):
    """Strict daily list. Prefilter on the sheet (RS >= 5, price above EMA50), then confirm each candidate on its own completed daily bars from yfinance.
    Fail-open: any download problem -> empty list (the page then says so), never an exception."""
    if not market or not market.get("up"):
        return []
    try:
        import yfinance as yf
        now = datetime.now(IST)
        cand = []
        for r in rows:
            rs, cmp_, e50 = _f(r.get("RS")), _f(r.get("CMP")), _f(r.get("EMA50"))
            if rs is not None and rs >= TOP_MIN_RS and cmp_ and e50 and cmp_ > e50:
                cand.append((str(r["NSE_SYMBOL"]).replace("NSE:", ""), rs, str(r.get("SECTOR", "")), str(r.get("Sector_Trend", ""))))
        if not cand:
            return []
        raw = yf.download([c[0] + ".NS" for c in cand], period="2y", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
        out = []
        for sym, rs, sector, st in cand:
            try:
                df = raw[sym + ".NS"].dropna(subset=["Close", "Volume"])
                if len(df) and df.index[-1].date() == now.date() and now.hour * 60 + now.minute < 15 * 60 + 45:
                    df = df.iloc[:-1]             # today's bar is still forming
                res = top_pick_check(df["Close"].tolist(), df["Volume"].tolist(), rs, True)
                if res:
                    res.update({"symbol": sym, "sector": sector, "rs": round(rs, 1), "sector_trend": st})
                    out.append(res)
            except Exception:
                continue
        out.sort(key=lambda x: -x["rs"])
        return out[:TOP_MAX]
    except Exception as ex:
        print(f"[SIGNALS] top picks skipped (fail-open): {ex}")
        return []


def sip_ok(down, cmp_, dma50, dma200, liq_cr):
    """SIP candidate: 15-35% below the 52-week high but still above BOTH the 50- and 200-day averages, and liquid."""
    try:
        return down is not None and -35 <= down <= -15 and cmp_ > dma50 > 0 and cmp_ > dma200 > 0 and (liq_cr or 0) >= TOP_MIN_LIQ_CR
    except Exception:
        return False


def _nifty_dmas(ws):
    """{symbol: (50_DMA, 200_DMA)} from Nifty200 (UNFORMATTED). Empty dict on any problem."""
    try:
        n = ws.spreadsheet.worksheet("Nifty200").get_all_values(value_render_option="UNFORMATTED_VALUE")
        h = n[0]
        i50, i200 = h.index("50_DMA"), h.index("200_DMA")
        return {str(r[0]).replace("NSE:", "").strip(): (_f(r[i50]), _f(r[i200])) for r in n[2:] if r and r[0]}
    except Exception as ex:
        print(f"[SIGNALS] DMA read skipped: {ex}")
        return {}


def _serial_to_date(x):
    """Google Sheets date serial (days since 1899-12-30) -> date; None when not a number."""
    try:
        return (datetime(1899, 12, 30) + timedelta(days=int(float(x)))).date()
    except Exception:
        return None


def _events(ws, today):
    """v1.1 (2026-11-05): a news-style events block for /market-events/: results due in the next 10 days (BotMemory EARNINGS_<SYM>_<date>, fed by fetch_earnings.py),
    ex-dividend dates of the last 30 days and bonus/split dates of the last 120 days (trailing columns from fetch_dividends.py). Descriptive only, no advice.
    Returns (events dict, {symbol: dividend yield %}); ({}, {}) on any problem (fail-open)."""
    try:
        sp = ws.spreadsheet
        n = sp.worksheet("Nifty200").get_all_values(value_render_option="UNFORMATTED_VALUE")
        h = n[0]
        ix = {k: h.index(k) for k in ("Div_Yield_%_TTM", "Last_Div_Date", "Last_Bonus_Split_Date", "Last_Bonus_Split_Ratio", "SECTOR")}
        yld, sector, div_rows, bon_rows = {}, {}, [], []
        for r in n[2:]:
            sym = str(r[0]).replace("NSE:", "").strip()
            if not sym:
                continue
            sector[sym] = str(r[ix["SECTOR"]])
            y = _f(r[ix["Div_Yield_%_TTM"]])
            if y is not None:
                yld[sym] = round(y, 2)
            d = _serial_to_date(r[ix["Last_Div_Date"]])
            if d and 0 <= (today - d).days <= 30 and y is not None:
                div_rows.append({"symbol": sym, "sector": sector[sym], "date": d.isoformat(), "date_label": d.strftime("%d %b %Y"), "yield": round(y, 2)})
            b = _serial_to_date(r[ix["Last_Bonus_Split_Date"]])
            ratio = _f(r[ix["Last_Bonus_Split_Ratio"]])
            if b and ratio and 0 <= (today - b).days <= 120:
                bon_rows.append({"symbol": sym, "sector": sector[sym], "date": b.isoformat(), "date_label": b.strftime("%d %b %Y"), "ratio": ("%g" % ratio)})
        res_rows = []
        for r in sp.worksheet("BotMemory").get_all_values():
            m = re.match(r"EARNINGS_(.+)_(\d{4}-\d{2}-\d{2})$", r[0] if r else "")
            if not m or m.group(1) not in sector:
                continue
            d = datetime.strptime(m.group(2), "%Y-%m-%d").date()
            if 0 <= (d - today).days <= 10:
                res_rows.append({"symbol": m.group(1), "sector": sector[m.group(1)], "date": d.isoformat(), "date_label": d.strftime("%a %d %b"), "days_left": (d - today).days})
        res_rows.sort(key=lambda x: (x["date"], x["symbol"]))
        div_rows.sort(key=lambda x: (x["date"], x["symbol"]), reverse=True)
        bon_rows.sort(key=lambda x: (x["date"], x["symbol"]), reverse=True)
        return {"results": res_rows[:25], "dividends": div_rows[:20], "bonus_split": bon_rows[:15]}, yld
    except Exception as ex:
        print(f"[SIGNALS] events skipped (fail-open): {ex}")
        return {}, {}


def build():
    ws = _connect()
    vals = ws.get_all_values(value_render_option="UNFORMATTED_VALUE")
    head = vals[0]
    rows = [dict(zip(head, r)) for r in vals[1:] if str(r[0]).startswith("NSE:")]
    if len(rows) < 100:
        raise RuntimeError(f"only {len(rows)} scanner rows — refusing to publish")

    def name(r):
        return str(r["NSE_SYMBOL"]).replace("NSE:", "")

    dmas = _nifty_dmas(ws)
    sip, sip_total = [], 0
    for r in rows:
        dd, cmp_, liq = _f(r.get("%down_from_52W_High")), _f(r.get("CMP")), _f(r.get("Liquidity_Cr"))
        d50, d200 = dmas.get(name(r), (None, None))
        if cmp_ is None or d50 is None or d200 is None or not sip_ok(dd, cmp_, d50, d200, liq):
            continue
        sip_total += 1
        base, sup = _f(r.get("Base_Range_20D_%")), _f(r.get("Support_1"))
        sip.append({
            "symbol": name(r), "sector": str(r.get("SECTOR", "")), "cmp": round(cmp_, 2),
            "down_from_high": round(dd, 1), "base_range": round(base, 1) if base is not None else None,
            "support": round(sup, 2) if sup else None,
            "sector_trend": str(r.get("Sector_Trend", "")),
        })
    # dividend yield is attached further below; then ranked: highest yield first, then the smallest 20-day range

    brk = []
    for r in rows:
        sig = str(r.get("Breakout_Signal", ""))
        if sig in ("", "-"):
            continue
        cmp_, rs, vol, lvl = _f(r.get("CMP")), _f(r.get("RS")), _f(r.get("Volume_vs_Avg %")), _f(r.get("Close_High_50D"))
        if cmp_ is None:
            continue
        brk.append({
            "symbol": name(r), "sector": str(r.get("SECTOR", "")), "cmp": round(cmp_, 2),
            "signal": "50-day closing-high breakout" if sig.startswith("50D") else "Trendline breakout",
            "level": round(lvl, 2) if (lvl and sig.startswith("50D")) else None,   # only the closing-high rule has a clean "level broken"
            "rs": round(rs, 1) if rs is not None else None,
            "volume": round(vol, 0) if vol is not None else None,
            "sector_trend": str(r.get("Sector_Trend", "")),
            "_k": -(rs if rs is not None else -999),
        })
    brk.sort(key=lambda x: x["_k"])
    brk = brk[:BREAKOUT_MAX]

    for lst in (sip, brk):
        for x in lst:
            x.pop("_k", None)

    now = datetime.now(IST)
    events, yld = _events(ws, now.date())
    for x in sip:
        if x["symbol"] in yld:
            x["div_yield"] = yld[x["symbol"]]
    sip.sort(key=lambda x: (-(x.get("div_yield") or 0), x["base_range"] if x["base_range"] is not None else 99))
    sip = sip[:SIP_MAX]
    market = _market_trend()
    top = _top_picks(rows, market)
    return {
        "events": events,
        "generated_at": now.strftime("%d %B %Y, %I:%M %p IST"),
        "market": market,
        "top_picks": top,
        "sip": sip, "breakout": brk,
        "counts": {"sip_total_zone": sip_total,
                   "breakout_total": sum(1 for r in rows if str(r.get("Breakout_Signal", "")) not in ("", "-"))},
    }


def main():
    dry = "--dry" in sys.argv
    try:
        out = build()
    except Exception as e:
        print(f"[SIGNALS] skipped (fail-open, existing file untouched): {e}")
        return 0
    print(f"[SIGNALS] sip={len(out['sip'])} breakout={len(out['breakout'])} market={out['market']}")
    if dry:
        print(json.dumps(out, ensure_ascii=False, indent=1)[:2500])
        return 0
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[SIGNALS] wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
