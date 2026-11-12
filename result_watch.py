"""
result_watch.py v1.0 (2026-11-12 NEW) - "RESULT WATCH": a daily PREMIUM Telegram text (paper / learning, not advice) naming the Nifty200 stocks whose
quarterly result is TODAY or in the next 1-2 trading days, with what the PUBLIC data shows: trend (50-DMA, RS, RSI), the stock FUTURES buildup (OI + price,
our own EOD F&O file = the only free positioning data that exists per stock), delivery %, and chart_reader's levels / retest status.
It then gives a plain "lean" (positive / mixed / weak) by counting those facts. IT IS NOT A PREDICTION OF THE RESULT:
  * no free source shows what FIIs/DIIs hold per stock day by day (shareholding is quarterly, bulk/block deals are after the fact); we have NO inside information
    and none may be used (insider trading is a crime) - the lean only reads what the chart and futures market already show;
  * every lean is logged (tab ResultLean) and later scored against the real reaction (close after the result vs close before), so its true hit-rate becomes known.
Options: stocks with a result inside the window are blocked for options by option_intelligence (IV crush) - this text is for CASH / SWING thinking only, and always says
"never hold through the result day".
NEVER read by trading_bot.py / appscript.gs / any gate or ledger. Fail-open. Mode env RESULT_WATCH_MODE: dry (default, prints) | scheduled (sends to PREMIUM + logs).
USAGE: python result_watch.py            (dry, prints the message)
       python result_watch.py --send     (same as scheduled)
       python result_watch.py --report   (hit-rate of past leans)
"""
import os
import sys
import time
import datetime as dt

import requests

import result_runup as RU

VERSION = "v1.0"
TAB = "ResultLean"
HEAD = ["Logged_On", "Symbol", "Result_Date", "Days_Left", "Lean", "Score", "Why", "Price_At_Log", "Reaction_%", "Scored"]
WINDOW = (0, 2)          # trading days to the result: 0 = today ... 2
MAX_STOCKS = 8
POS_BUILD = ("Long Buildup", "Short Covering")
NEG_BUILD = ("Short Buildup", "Long Unwinding")


# ---------------- pure logic (unit-tested) ----------------

def lean_score(above50, rs, rsi, buildup, ret5=None):
    """Count public facts. Returns (score, [reasons]). Each fact is worth +-1."""
    s, why = 0, []
    if above50 is True:
        s += 1; why.append("50-DMA ke upar")
    elif above50 is False:
        s -= 1; why.append("50-DMA ke neeche")
    if rs is not None:
        if rs >= 5:
            s += 1; why.append(f"RS {rs:.0f}")
        elif rs < 0:
            s -= 1; why.append(f"RS {rs:.0f}")
    if rsi is not None:
        if rsi > 70:
            s -= 1; why.append(f"RSI {rsi:.0f} garam")
        elif 45 <= rsi <= 65:
            s += 1; why.append(f"RSI {rsi:.0f} theek")
    if buildup in POS_BUILD:
        s += 1; why.append(f"futures {buildup}")
    elif buildup in NEG_BUILD:
        s -= 1; why.append(f"futures {buildup}")
    if ret5 is not None:
        if ret5 >= 6:
            s -= 1; why.append(f"5 din me {ret5:+.0f}% (pehle hi bhaag chuka)")
    return s, why


def lean_label(score):
    return "POSITIVE" if score >= 3 else ("NEGATIVE" if score <= -1 else "MIXED")


G, Y, R = "🟢", "🟡", "🔴"       # green / yellow / red dot
LEAN_DOT = {"POSITIVE": G, "MIXED": Y, "NEGATIVE": R}


def factor_dots(above50, rs, rsi, buildup, ret5):
    """One compact line of coloured dots (same facts and thresholds as lean_score): green = fine, yellow = in between / unknown, red = weak."""
    t = Y if above50 is None else (G if above50 else R)
    r = Y if rs is None else (G if rs >= 5 else (R if rs < 0 else Y))
    i = Y if rsi is None else (G if 45 <= rsi <= 65 else (R if rsi > 70 else Y))
    f = G if buildup in POS_BUILD else (R if buildup in NEG_BUILD else Y)
    m = Y if ret5 is None else (R if ret5 >= 6 else (Y if ret5 >= 4 else G))
    return f"50DMA{t} RS{r} RSI{i} Fut{f} 5d{m}"


def when_word(E, today):
    d = (E - today).days
    return "TODAY" if d == 0 else ("TOMORROW" if d == 1 else f"{E:%a %d-%b}")


def plan_line(E, today):
    if E == today:
        return "result aaj: naya entry/hold nahi, reaction kal dekho"
    return "result se pehle ke din ke close tak hi, result ke saath mat raho"


def build_message(items, today):
    """items: dicts sym,k,E,score,why,label,cmp,chg,chart(str),dlv,fo. Pure text, compact, easy Hinglish."""
    if not items:
        return None
    L = [f"RESULT WATCH | {today:%d-%b}", "(Only for knowledge / paper trade - not a prediction of the result)",
         f"{G} Positive  {Y} Mixed  {R} Negative"]
    for it in items:
        L.append("")
        L.append(f"{it['sym']} - result {when_word(it['E'], today)} | {LEAN_DOT.get(it['label'], Y)} {it['label']} ({it['score']:+d})")
        L.append(f"  CMP {it['cmp']:g} ({it['chg']:+.1f}%)" + (f" | delivery {it['dlv']:.0f}%" if it.get("dlv") else "") + (" | F&O" if it.get("fo") else ""))
        L.append("  " + it.get("dots", ""))
        if it.get("chart"):
            L.append("  chart: " + it["chart"])
    L += ["", "Options are blocked around results (IV crush). Result-day move can be about 7% either way."]
    return "\n".join(L)


def chart_line(sym):
    try:
        import chart_reader as C
        r = C.read(*C.fetch(sym))
        if not r:
            return ""
        rt = r["retest"]
        bits = [f"trend {r['trend']}"]
        if r["support"]:
            bits.append(f"support {r['support'][0][0]:g}")
        if r["resistance"]:
            bits.append(f"resistance {r['resistance'][0][0]:g}")
        if rt["status"] == "RETEST":
            bits.append(f"RETEST of {rt['level']:g}")
        elif rt["status"] == "EXTENDED":
            bits.append("already ran up after breakout")
        elif rt["status"] == "FAILED":
            bits.append("failed breakout")
        return ", ".join(bits)
    except Exception:
        return ""


# ---------------- data ----------------

def gather(sh, today, hol):
    n = sh.worksheet("Nifty200").get_all_values()
    h = [x.strip() for x in n[0]]

    def col(name):
        return h.index(name) if name in h else None
    ix = {k: col(k) for k in ("CMP", "%Change", "50_DMA", "RS", "Options", "Buildup")}
    ev = RU.load_events(sh)
    dlv = {}
    for r in sh.worksheet("BotMemory").get_all_values():
        if r and r[0].startswith("DLV_"):
            dlv[r[0][4:]] = RU._num(r[1] if len(r) > 1 else "")
    raw = []
    for r in n[2:]:
        s = r[0].replace("NSE:", "").strip()
        for e in ev.get(s, []):
            k = RU.trading_days_between(today, e, hol) if e >= today else -1
            if WINDOW[0] <= k <= WINDOW[1]:
                g = lambda name: (r[ix[name]] if ix.get(name) is not None and ix[name] < len(r) else "")
                raw.append(dict(sym=s, E=e, k=k, cmp=RU._num(g("CMP")), chg=RU._num(g("%Change")) or 0.0, dma=RU._num(g("50_DMA")),
                                rs=RU._num(g("RS")), fo=g("Options") in ("N50", "YES"), buildup=g("Buildup").strip(), dlv=dlv.get(s)))
    cl = RU._closes(sorted({x["sym"] for x in raw}))
    out = []
    for x in raw:
        if not x["cmp"]:
            continue
        c = cl.get(x["sym"])
        closes = [float(v) for v in c["Close"].tolist()] if (c is not None and len(c)) else []
        rsi = RU.rsi14(closes) if closes else None
        ret5 = (closes[-1] / closes[-6] - 1) * 100 if len(closes) >= 6 else None
        above = (x["cmp"] > x["dma"]) if x["dma"] else None
        sc, why = lean_score(above, x["rs"], rsi, x["buildup"], ret5)
        gate = bool(above and x["rs"] is not None and x["rs"] >= 5 and rsi is not None and rsi <= 65)     # our bullish entry gates (above 50-DMA, RS>=5, RSI ok)
        x.update(score=sc, why=why, label=lean_label(sc), gate=gate, dots=factor_dots(above, x["rs"], rsi, x["buildup"], ret5))
        out.append(x)
    return pick(out)


def pick(items, cap=MAX_STOCKS):
    """Bullish project: stocks that pass our gates first, then F&O names, then the rest (mixed/negative) by score; at most `cap` in total."""
    return sorted(items, key=lambda z: (not z.get("gate"), not z.get("fo"), -z["score"], z["k"]))[:cap]


def tg_send(text):
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN", ""), os.environ.get("CHAT_ID_PREMIUM", "")
    if not (tok and chat):
        print("[TG] no token/chat - not sent")
        return False
    r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", data={"chat_id": chat, "text": text}, timeout=20)
    print(f"[TG] premium status {r.status_code}")
    return r.status_code == 200


def log_and_score(sh, items, today, hol, write):
    import gspread
    try:
        ws = sh.worksheet(TAB)
    except gspread.WorksheetNotFound:
        if not write:
            return False
        ws = sh.add_worksheet(TAB, rows=500, cols=len(HEAD))
        ws.update(range_name="A1", values=[HEAD])
    v = ws.get_all_values()
    sent_today = any(r and r[0] == today.isoformat() for r in v[1:])
    if write:
        have = {(r[1], r[2]) for r in v[1:] if len(r) > 2}
        fresh = [[today.isoformat(), x["sym"], x["E"].isoformat(), x["k"], x["label"], x["score"], "; ".join(x["why"]), x["cmp"], "", ""]
                 for x in items if (x["sym"], x["E"].isoformat()) not in have]
        if fresh:
            start = len(v) + 1
            if ws.row_count < start + len(fresh) + 5:
                ws.add_rows(start + len(fresh) + 5 - ws.row_count)
            ws.update(range_name=f"A{start}", values=fresh, value_input_option="USER_ENTERED")
            print(f"[LOG] {len(fresh)} lean(s) logged")
        v = ws.get_all_values()
        todo = [(i, r) for i, r in enumerate(v[1:], start=2) if len(r) >= 10 and r[9] == "" and r[2] and dt.date.fromisoformat(r[2]) < today]
        if todo:
            cl = RU._closes(sorted({r[1] for _, r in todo}))
            body = []
            for i, r in todo:
                x = cl.get(r[1])
                if x is None:
                    continue
                E = dt.date.fromisoformat(r[2])
                try:
                    pre = float(x.loc[RU.pd_ts(RU.prev_trading_day(E, hol)), "Close"])
                    nxt = E + dt.timedelta(days=1)
                    while nxt.weekday() >= 5 or nxt in hol:
                        nxt += dt.timedelta(days=1)
                    if RU.pd_ts(nxt) not in x.index:
                        continue
                    react = (float(x.loc[RU.pd_ts(nxt), "Close"]) / pre - 1) * 100
                    body.append({"range": f"I{i}:J{i}", "values": [[round(react, 2), "Y"]]})
                except Exception:
                    continue
            for k in range(0, len(body), 100):
                ws.batch_update(body[k:k + 100], value_input_option="USER_ENTERED")
                time.sleep(1)
            print(f"[SCORE] {len(body)} scored")
    return sent_today


def report(sh):
    v = sh.worksheet(TAB).get_all_values()
    rows = [r for r in v[1:] if len(r) >= 10 and r[9] == "Y" and r[8] != ""]
    print(f"[REPORT] {len(v) - 1} logged, {len(rows)} scored (reaction = close day after result vs close day before)")
    for lab in ("POSITIVE", "MIXED", "NEGATIVE"):
        x = [float(r[8]) for r in rows if r[4] == lab]
        if x:
            print(f"  {lab}: n={len(x)} avg {sum(x) / len(x):+.2f}% up {sum(1 for t in x if t > 0) * 100 // len(x)}%")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    send = "--send" in argv or os.environ.get("RESULT_WATCH_MODE", "dry").lower() == "scheduled"
    sh = RU._connect()
    if "--report" in argv:
        return report(sh)
    today = dt.datetime.now(RU.IST).date()
    if "--date" in argv and not send:                                    # preview what a given morning's message would look like (dry only)
        today = dt.date.fromisoformat(argv[argv.index("--date") + 1])
    hol = RU._holidays()
    print(f"[result_watch {VERSION}] {today} mode={'SEND' if send else 'DRY'}")
    if today.weekday() >= 5 or today in hol:
        print("[result_watch] not a trading day - nothing to do")
        return 0
    try:
        items = gather(sh, today, hol)
        for it in items:
            it["chart"] = chart_line(it["sym"])
        msg = build_message(items, today)
        print(msg or "[result_watch] no results in the window")
        if send:
            done_today = log_and_score(sh, items, today, hol, write=False)      # read-only: was a message already sent today?
            ok = False
            if msg and not done_today:
                ok = tg_send(msg)
            elif msg:
                print("[result_watch] already sent today - not sending again")
            log_and_score(sh, items if ok else [], today, hol, write=True)      # log only what was really sent; scoring of old rows always runs
    except Exception as e:
        print(f"[result_watch] skipped (fail-open): {str(e)[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
