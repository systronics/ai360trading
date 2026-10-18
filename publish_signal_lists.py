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

import os, sys, json
from datetime import datetime
import pytz

IST        = pytz.timezone("Asia/Kolkata")
SHEET_NAME = "Ai360tradingAlgo"
TAB        = "BottomScanner"
OUT_PATH   = "_data/signal_lists.json"
SIP_MAX      = 15
BREAKOUT_MAX = 15


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


def build():
    ws = _connect()
    vals = ws.get_all_values(value_render_option="UNFORMATTED_VALUE")
    head = vals[0]
    rows = [dict(zip(head, r)) for r in vals[1:] if str(r[0]).startswith("NSE:")]
    if len(rows) < 100:
        raise RuntimeError(f"only {len(rows)} scanner rows — refusing to publish")

    def name(r):
        return str(r["NSE_SYMBOL"]).replace("NSE:", "")

    sip = []
    for r in rows:
        if str(r.get("SIP_Zone", "")) != "ACCUMULATION ZONE":
            continue
        dd, base, sup, cmp_ = _f(r.get("%down_from_52W_High")), _f(r.get("Base_Range_20D_%")), _f(r.get("Support_1")), _f(r.get("CMP"))
        if None in (dd, base, cmp_):
            continue
        sip.append({
            "symbol": name(r), "sector": str(r.get("SECTOR", "")), "cmp": round(cmp_, 2),
            "down_from_high": round(dd, 1), "base_range": round(base, 1),
            "support": round(sup, 2) if sup else None,
            "sector_trend": str(r.get("Sector_Trend", "")),
            "_k": (base, dd),
        })
    sip.sort(key=lambda x: x["_k"])          # tightest base first
    sip = sip[:SIP_MAX]

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
    return {
        "generated_at": now.strftime("%d %B %Y, %I:%M %p IST"),
        "market": _market_trend(),
        "sip": sip, "breakout": brk,
        "counts": {"sip_total_zone": sum(1 for r in rows if str(r.get("SIP_Zone", "")) == "ACCUMULATION ZONE"),
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
