"""
option_watch.py v1.0 (2026-11-13/14 NEW) - "OPTION WATCH": ONE daily PREMIUM Telegram text (paper / for knowledge, NOT advice, NOT a prediction) with the F&O stocks whose
CHART and OPTION CONTRACT both look acceptable for a CALL buyer, built from public daily bars + the free read-only Upstox Analytics Token (live bid/ask, IV, theta, OI).
Observation + watch only: no order, no gate, no ledger read by the trading bot; every row is logged in the `OptionWatch` tab and scored later.

WHY these rules (own 2017-2026 study on 207 stocks, 5-day forward move, 13 Nov 2026): P(stock reaches +4% within 5 days) = 37.3% on any day, 34.5% when ADX<20
(sideways), 42.9% after a 20-day-high breakout with volume >= 1.5x, 45.7% when that breakout also has ADX>=25 and +DI>-DI (the best group; but a drop of -4% is also
more likely, 38%). A Bollinger SQUEEZE did NOT help (40.0%, and +0.01% in 2024+), so it is not used. An option buyer needs the stock to move MORE than the break-even,
so the contract must also be cheap to hold: spread, IV vs the stock's own HV-20, theta per day and the break-even move versus the stock's daily range.

HARD rules (all must pass or the stock is not listed): F&O stock; daily ADX>=25 with +DI>-DI; today a 20-day-high breakout with volume>=1.5x (BREAKOUT) or within 1.5% below
that high (NEAR); no result within +-3 trading days; contract with >=15 days to expiry (the owner's decay rule); ATM call bid-ask spread <= 6%.
SOFT (green/yellow/red dots, used to rank): spread <=3% green; IV <= 1.1x HV-20 green; theta <= 2.5% of premium per day green; break-even move <= 1.0x daily ATR% green;
volume >= 1000 contracts green.
USAGE: python option_watch.py            dry-run (prints, needs UPSTOX_ANALYTICS_TOKEN)
       python option_watch.py --send     send to PREMIUM + log + score old rows
       python option_watch.py --auto     for the price-feed loop: runs ONCE per trading day in the 14:40-15:25 IST window, else exits at once
       python option_watch.py --report   hit-rate of past rows
       --force                           test run on a holiday/weekend (uses the last trading day's data)
"""
import gzip
import json
import math
import os
import sys
import tempfile
import time
import datetime as dt

import pytz
import requests

import option_snap as S
import result_runup as RU

IST = pytz.timezone("Asia/Kolkata")
VERSION = "v1.0"
TAB = "OptionWatch"
HEAD = ["Date", "Symbol", "Setup", "Spot", "Expiry", "DTE", "Strike", "Ask", "Bid", "Spread_%", "IV", "HV20", "IV_vs_HV", "Theta_%/day", "BE_move_%", "ADX", "Vol_x",
        "Greens", "BE_Price", "Max_up_5d_%", "BE_reached_5d", "Scored"]
CHAIN = "https://api.upstox.com/v2/option/chain"
MIN_DTE = 8      # 2026-11-17 owner order (was 15), same as trading_bot.OPTION_MIN_DAYS_LEFT
MAX_SPREAD = 6.0
MAX_LISTED = 3
NEAR_PCT = 1.5
WINDOW = ((14, 40), (15, 25))
G, Y, R = "\U0001F7E2", "\U0001F7E1", "\U0001F534"
META_CACHE = os.path.join(tempfile.gettempdir(), "option_watch_fo_meta.json")


# ---------------- pure logic (unit-tested) ----------------

def hv20(closes):
    """Annualised % historical volatility of the last 20 daily log returns. None when too short."""
    if len(closes) < 22:
        return None
    r = [math.log(closes[i] / closes[i - 1]) for i in range(len(closes) - 20, len(closes)) if closes[i - 1] > 0 and closes[i] > 0]
    if len(r) < 15:
        return None
    m = sum(r) / len(r)
    var = sum((x - m) ** 2 for x in r) / (len(r) - 1)
    return round(math.sqrt(var) * math.sqrt(252) * 100, 1)


def atr_pct(highs, lows, closes, n=14):
    if len(closes) < n + 2:
        return None
    trs = [max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])) for i in range(len(closes) - n, len(closes))]
    return round(sum(trs) / n / closes[-1] * 100, 2) if closes[-1] else None


def chart_setup(closes, volumes, adx, pdi, mdi):
    """-> ('BREAKOUT'|'NEAR'|None, vol_x). Needs the trend (ADX>=25, +DI>-DI) and a 20-day closing high."""
    if len(closes) < 25 or adx is None or not (adx >= 25 and pdi is not None and mdi is not None and pdi > mdi):
        return None, None
    hh = max(closes[-21:-1])
    avg20 = sum(volumes[-21:-1]) / 20.0
    volx = (volumes[-1] / avg20) if avg20 else 0.0
    if closes[-1] > hh and volx >= 1.5:
        return "BREAKOUT", round(volx, 2)
    if closes[-1] <= hh and closes[-1] >= hh * (1 - NEAR_PCT / 100.0) and volx >= 0.8:
        return "NEAR", round(volx, 2)
    return None, round(volx, 2)


def dot_spread(p):
    return None if p is None else (G if p <= 3 else (Y if p <= MAX_SPREAD else R))


def dot_iv(iv, hv):
    if iv is None or not hv:
        return Y
    ratio = iv / hv
    return G if ratio <= 1.1 else (Y if ratio <= 1.4 else R)


def dot_theta(t):
    return Y if t is None else (G if t <= 2.5 else (Y if t <= 5 else R))


def dot_be(be_move_pct, atrp):
    if be_move_pct is None or not atrp:
        return Y
    r = be_move_pct / atrp
    return G if r <= 1.0 else (Y if r <= 1.8 else R)


def dot_liq(volume, oi):
    v = volume or 0
    o = oi or 0
    return G if (v >= 1000 or o >= 10000) else (Y if (v >= 100 or o >= 2000) else R)


def pick_expiry(expiries_ms, today, min_dte=MIN_DTE):
    """First expiry with >= min_dte days left -> (YYYY-MM-DD, dte) or (None, None)."""
    for e in sorted(expiries_ms):
        d = dt.datetime.fromtimestamp(e / 1000, dt.timezone.utc).date()
        dte = (d - today).days
        if dte >= min_dte:
            return d.isoformat(), dte
    return None, None


def contract_from_chain(rows, spot):
    """ATM CALL numbers from the Upstox chain rows. None when unusable."""
    if not rows or not spot:
        return None
    atm = min(rows, key=lambda r: abs((S._f(r.get("strike_price")) or 0) - spot))
    o = atm.get("call_options") or {}
    md, g = o.get("market_data") or {}, o.get("option_greeks") or {}
    ltp, bid, ask = S._f(md.get("ltp")), S._f(md.get("bid_price")), S._f(md.get("ask_price"))
    strike = S._f(atm.get("strike_price"))
    if not (strike and ask and ask > 0):
        return None
    theta = S._f(g.get("theta"))
    be = strike + ask
    return {"strike": strike, "ask": ask, "bid": bid, "ltp": ltp,
            "spread": round((ask - bid) / ask * 100, 2) if (bid is not None and ask >= bid) else None,
            "iv": S._f(g.get("iv")), "theta_pct": round(abs(theta) / ltp * 100, 2) if (theta is not None and ltp) else None,
            "volume": S._f(md.get("volume")), "oi": S._f(md.get("oi")), "be": round(be, 2), "be_move": round((be - spot) / spot * 100, 2),
            "instrument_key": o.get("instrument_key")}


def judge(setup, cont, hv, atrp, dte):
    """Hard rules + dots for one stock. Returns dict(listed bool, why str, dots dict, greens int)."""
    if not setup:
        return {"listed": False, "why": "no breakout/near-breakout with ADX>=25", "dots": {}, "greens": 0}
    if not cont:
        return {"listed": False, "why": "no usable option quote", "dots": {}, "greens": 0}
    if dte is None or dte < MIN_DTE:
        return {"listed": False, "why": f"expiry only {dte}d", "dots": {}, "greens": 0}
    if cont["spread"] is None or cont["spread"] > MAX_SPREAD:
        return {"listed": False, "why": f"spread {cont['spread']}% too wide", "dots": {}, "greens": 0}
    dots = {"spread": dot_spread(cont["spread"]), "iv": dot_iv(cont["iv"], hv), "theta": dot_theta(cont["theta_pct"]),
            "be": dot_be(cont["be_move"], atrp), "liq": dot_liq(cont["volume"], cont["oi"])}
    greens = sum(1 for d in dots.values() if d == G)
    return {"listed": True, "why": "", "dots": dots, "greens": greens}


def build_message(items, today, n_scanned):
    L = [f"OPTION WATCH LIST | {today:%d-%b}", "THIS IS NOT A TRADE CALL. No entry, stop-loss or exit is given. Do NOT buy from this list.",
         "It only shows what we are studying (paper / knowledge, not advice). A real call comes as 'OPTIONS SIGNAL' with the exact contract, stop and exit.", f"{G} good  {Y} ok  {R} weak"]
    if not items:
        L += ["", f"No clean call-option setup today ({n_scanned} F&O stocks checked: trend + breakout + fair contract all needed).",
              "No setup is also a result: waiting costs nothing, a theta-heavy option costs every day."]
        return "\n".join(L)
    for k, it in enumerate(items, 1):
        c, d = it["cont"], it["j"]["dots"]
        L.append("")
        L.append(f"{k}) {it['sym']} - {it['setup']}  CMP {it['spot']:g} | ADX {it['adx']:.0f} | vol {it['volx']:.1f}x")
        L.append(f"   {c['strike']:g} CE exp {it['expiry'][8:]}-{it['expiry'][5:7]} ({it['dte']}d) ask {c['ask']:g} | needs +{c['be_move']:.1f}% to break even"
                 + (f" | lot cost ~Rs {it['lot_cost']:,.0f}" if it.get("lot_cost") else ""))
        L.append(f"   Spread{d['spread']} {c['spread']:.1f}%  IV{d['iv']} {c['iv'] if c['iv'] is not None else '?'} vs HV {it['hv'] if it['hv'] else '?'}  "
                 f"Theta{d['theta']} {c['theta_pct'] if c['theta_pct'] is not None else '?'}%/day  BEmove{d['be']}  Liquidity{d['liq']}")
    L += ["", "A call option earns only if the stock moves MORE than the break-even before expiry. Keep size small; if the trend breaks, the idea is over.",
          "Paper/watch list - rank = number of green dots. Results are logged in the OptionWatch tab."]
    return "\n".join(L)


def be_scored(highs_after, be_price, spot):
    """Max high of the next 5 sessions vs the break-even price -> (max_up_pct, 'Y'/'N'); None if < 5 sessions."""
    if len(highs_after) < 5:
        return None
    mx = max(highs_after[:5])
    return round((mx / spot - 1) * 100, 2), ("Y" if mx >= be_price else "N")


# ---------------- data ----------------

def load_fo_meta(today):
    """{symbol: {expiry_ms: lot}} for NSE option contracts (cached per day). {} on any problem."""
    try:
        if os.path.exists(META_CACHE):
            c = json.load(open(META_CACHE, encoding="utf-8"))
            if c.get("date") == today.isoformat() and c.get("map"):
                return {k: {int(e): l for e, l in v.items()} for k, v in c["map"].items()}
    except Exception:
        pass
    try:
        r = requests.get("https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz", timeout=60)
        r.raise_for_status()
        data = json.loads(gzip.decompress(r.content).decode("utf-8"))
        m = {}
        for x in data:
            if x.get("segment") == "NSE_FO" and x.get("instrument_type") == "CE" and x.get("underlying_symbol") and x.get("expiry"):
                m.setdefault(x["underlying_symbol"], {}).setdefault(int(x["expiry"]), int(x.get("lot_size") or 0) or None)
        if len(m) < 100:
            return {}
        json.dump({"date": today.isoformat(), "map": {k: {str(e): l for e, l in v.items()} for k, v in m.items()}}, open(META_CACHE, "w", encoding="utf-8"))
        return m
    except Exception as e:
        print(f"[OW] F&O instrument file failed ({str(e)[:80]})")
        return {}


def daily_bars(symbols):
    import yfinance as yf
    df = yf.download([s + ".NS" for s in symbols], period="1y", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
    out = {}
    for s in symbols:
        try:
            x = df[s + ".NS"].dropna(subset=["Close"])
            if len(x) >= 60:
                out[s] = ([float(v) for v in x.High], [float(v) for v in x.Low], [float(v) for v in x.Close], [float(v) for v in x.Volume])
        except Exception:
            continue
    return out


def fetch_chain(token, ukey, expiry):
    r = requests.get(CHAIN, params={"instrument_key": ukey, "expiry_date": expiry}, headers={"Accept": "application/json", "Authorization": f"Bearer {token}"}, timeout=25)
    return (r.json() or {}).get("data") or [] if r.status_code == 200 else []


def scan(sh, today, token):
    import watch_plan as WP
    import live_prices_upstox as UP
    n = sh.worksheet("Nifty200").get_all_values()
    h = [x.strip() for x in n[0]]
    ix = h.index("Options")
    fo = [r[0].replace("NSE:", "").strip() for r in n[2:] if r and r[0] and len(r) > ix and r[ix].strip() in ("N50", "YES")]
    ev = RU.load_events(sh)
    hol = RU._holidays()
    bars = daily_bars(fo)
    meta = load_fo_meta(today)
    inst = UP.load_instruments()
    cands = []
    for s, (hi, lo, cl, vo) in bars.items():
        ax = WP._adx(hi, lo, cl)
        if not ax:
            continue
        setup, volx = chart_setup(cl, vo, ax[0], ax[1], ax[2])
        if not setup:
            continue
        if any(0 <= RU.trading_days_between(today, e, hol) <= 3 or 0 <= RU.trading_days_between(e, today, hol) <= 3 for e in ev.get(s, [])):
            print(f"[OW] {s}: result within 3 trading days - skipped")
            continue
        cands.append((s, setup, volx, ax, hi, lo, cl))
    cands.sort(key=lambda c: (c[1] != "BREAKOUT", -(c[3][0])))
    items = []
    for s, setup, volx, ax, hi, lo, cl in cands[:12]:
        try:
            exps = sorted((meta.get(s) or {}).keys())
            expiry, dte = pick_expiry(exps, today)
            ukey = inst.get(s)
            if not (expiry and ukey):
                continue
            rows = fetch_chain(token, ukey, expiry)
            spot = S._f(rows[0].get("underlying_spot_price")) if rows else cl[-1]
            cont = contract_from_chain(rows, spot)
            hv = hv20(cl)
            j = judge(setup, cont, hv, atr_pct(hi, lo, cl), dte)
            print(f"[OW] {s}: {setup} ADX {ax[0]:.0f} -> {'LISTED ' + str(j['greens']) + 'G' if j['listed'] else j['why']}")
            if j["listed"]:
                lot = {dt.datetime.fromtimestamp(e / 1000, dt.timezone.utc).date().isoformat(): l for e, l in (meta.get(s) or {}).items()}.get(expiry)
                items.append({"sym": s, "setup": setup, "spot": spot, "adx": ax[0], "volx": volx, "expiry": expiry, "dte": dte, "cont": cont, "j": j, "hv": hv,
                              "lot_cost": (cont["ask"] * lot) if lot else None})
        except Exception as e:
            print(f"[OW] {s} skipped ({str(e)[:80]})")
    items.sort(key=lambda z: (-z["j"]["greens"], z["setup"] != "BREAKOUT", -(z["cont"]["volume"] or 0)))
    return items[:MAX_LISTED], len(fo)


# ---------------- sheet / telegram ----------------

def tg_send(text):
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN", ""), os.environ.get("CHAT_ID_PREMIUM", "")
    if not (tok and chat):
        print("[TG] no token/chat - not sent")
        return False
    r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", data={"chat_id": chat, "text": text}, timeout=20)
    print(f"[TG] premium status {r.status_code}")
    return r.status_code == 200


def tab(sh, create):
    import gspread
    try:
        return sh.worksheet(TAB)
    except gspread.WorksheetNotFound:
        if not create:
            return None
        ws = sh.add_worksheet(TAB, rows=600, cols=len(HEAD))
        ws.update(range_name="A1", values=[HEAD])
        return ws


def log_rows(ws, items, today):
    v = ws.get_all_values()
    rows = []
    for it in items:
        c = it["cont"]
        rows.append([today.isoformat(), it["sym"], it["setup"], round(it["spot"], 2), it["expiry"], it["dte"], c["strike"], c["ask"], c["bid"], c["spread"], c["iv"], it["hv"],
                     round(c["iv"] / it["hv"], 2) if (c["iv"] and it["hv"]) else "", c["theta_pct"], c["be_move"], round(it["adx"], 1), it["volx"], it["j"]["greens"], c["be"],
                     "", "", ""])
    if not rows:
        rows = [[today.isoformat(), "(none)", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 0, "", "", "", "Y"]]
    start = len(v) + 1
    if ws.row_count < start + len(rows) + 3:
        ws.add_rows(start + len(rows) + 3 - ws.row_count)
    ws.update(range_name=f"A{start}", values=rows, value_input_option="USER_ENTERED")


def score_old(ws, today, hol):
    import yfinance as yf
    v = ws.get_all_values()
    todo = [(i, r) for i, r in enumerate(v[1:], start=2) if len(r) >= 22 and r[21] != "Y" and r[1] != "(none)" and r[0] and dt.date.fromisoformat(r[0]) < today]
    if not todo:
        return
    syms = sorted({r[1] for _, r in todo})
    df = yf.download([s + ".NS" for s in syms], period="2mo", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
    body = []
    for i, r in todo:
        try:
            x = df[r[1] + ".NS"].dropna(subset=["Close"]) if len(syms) > 1 else df.dropna(subset=["Close"])
            sig = dt.date.fromisoformat(r[0])
            after = [float(q) for d, q in zip(x.index, x.High) if d.date() > sig]
            res = be_scored(after, float(r[18]), float(r[3]))
            if res:
                body.append({"range": f"T{i}:V{i}", "values": [[res[0], res[1], "Y"]]})
        except Exception:
            continue
    for k in range(0, len(body), 100):
        ws.batch_update(body[k:k + 100], value_input_option="USER_ENTERED")
        time.sleep(1)
    print(f"[OW] scored {len(body)} rows")


def report(sh):
    ws = tab(sh, False)
    if not ws:
        print("no OptionWatch tab yet")
        return
    v = ws.get_all_values()
    rows = [r for r in v[1:] if len(r) >= 22 and r[1] != "(none)"]
    sc = [r for r in rows if r[21] == "Y"]
    print(f"[OPTIONWATCH REPORT] {len(rows)} listed, {len(sc)} scored")
    if sc:
        y = sum(1 for r in sc if r[20] == "Y")
        mx = [float(r[19]) for r in sc if r[19] != ""]
        print(f"  break-even reached within 5 days: {y}/{len(sc)} ({y * 100 // len(sc)}%) | avg max-up {sum(mx) / len(mx):+.2f}% (fewer than 30 rows = no conclusion)")


def in_window(now):
    return WINDOW[0] <= (now.hour, now.minute) <= WINDOW[1]


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    now = dt.datetime.now(IST)
    auto = "--auto" in argv
    if auto and (now.weekday() >= 5 or not in_window(now)):
        return 0                                                  # the loop calls this every tick: leave at once outside the window
    token = os.environ.get("UPSTOX_ANALYTICS_TOKEN", "").strip()
    if not token and "--report" not in argv:
        print("[OW] no UPSTOX_ANALYTICS_TOKEN - nothing to do")
        return 0
    sh = RU._connect()
    if "--report" in argv:
        return report(sh)
    today = now.date()
    if S._is_holiday() and "--force" not in argv:
        print("[OW] market holiday - nothing to do (use --force for a test run)")
        return 0
    scheduled = os.environ.get("OPTION_WATCH_MODE", "dry").lower() == "scheduled"
    if auto and not scheduled:
        return 0                                                  # kill switch: the loop hook does nothing unless OPTION_WATCH_MODE=scheduled
    send = "--send" in argv or scheduled
    ws = tab(sh, send)
    if auto and ws is not None and any(r and r[0] == today.isoformat() for r in ws.get_all_values()[1:]):
        return 0                                                  # already done today
    items, n = scan(sh, today, token)
    text = build_message(items, today, n)
    print(text)
    if send and ws is not None:
        ok = tg_send(text)
        if ok or not os.environ.get("TELEGRAM_BOT_TOKEN"):
            log_rows(ws, items, today)
        score_old(ws, today, RU._holidays())
    return 0


if __name__ == "__main__":
    sys.exit(main())
