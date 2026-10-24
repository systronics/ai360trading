"""
weekly_scorecard.py v1.0 (2026-10-24) — honest WEEKLY scorecard of our paper trades.

Why: almost nobody in this niche publishes the losses. A short, regular, true scorecard (wins AND losses, open
positions with their live P/L) is the cheapest trust-builder we have and gives every week a fresh, real story.
Sent to the three Telegram channels and written to _data/scorecard.json for the website.

Rules: paper-trading wording on every message; compact (owner rule — signal and numbers, no essay); percentages
are averages per trade, never a summed "return"; fail-open (any error prints and exits 0, nothing is sent half-made).
Usage:  python weekly_scorecard.py            # build + send + write json
        python weekly_scorecard.py --dry      # print only
"""
import json
import os
import sys
from datetime import datetime, timedelta

import pytz
import requests

import performance_stats as ps

IST = pytz.timezone("Asia/Kolkata")
SHEET_NAME = ps.SHEET_NAME
OUT_JSON = "_data/scorecard.json"


def _fmt_pct(x):
    return f"{x:+.1f}%"


def _closed_this_week(today):
    rows = ps._open_history().get_all_values()[1:]
    start = (today - timedelta(days=6)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    out = []
    for r in rows:
        if len(r) < 17:
            continue
        xd = str(r[3])[:10]
        if not (start <= xd <= end):
            continue
        pl = ps._to_float(r[5])
        if pl is None:
            continue
        out.append({"sym": r[0].replace("NSE:", ""), "pl": pl, "inr": ps._to_float(r[16]) or 0.0,
                    "cat": ps._category(str(r[9])), "win": "WIN" in str(r[6]).upper()})
    return out, start, end


def _open_positions():
    """Open paper trades from AlertLog: [(symbol, live P/L %)]. [] on any problem."""
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
        if not raw:
            raw = open("service_account.json").read().strip()
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)
        ws = gspread.authorize(creds).open(SHEET_NAME).worksheet("AlertLog")
        vals = ws.get_all_values()
        h = vals[0]
        i_sym, i_st, i_pl = h.index("Symbol"), h.index("Trade Status"), h.index("P/L %")
        out = []
        for r in vals[1:]:
            if len(r) > max(i_sym, i_st, i_pl) and "TRADED" in r[i_st].upper() and "EXITED" not in r[i_st].upper():
                p = ps._to_float(r[i_pl])
                if p is not None:
                    out.append((r[i_sym].replace("NSE:", ""), p))
        return out
    except Exception as e:
        print(f"[SCORECARD] open positions skipped: {e}")
        return []


def build(today=None):
    today = today or datetime.now(IST).date()
    closed, start, end = _closed_this_week(today)
    opens = _open_positions()
    s_d = datetime.strptime(start, "%Y-%m-%d").strftime("%d %b")
    e_d = datetime.strptime(end, "%Y-%m-%d").strftime("%d %b")
    n = len(closed)
    wins = sum(1 for t in closed if t["win"])
    avg = sum(t["pl"] for t in closed) / n if n else 0.0
    net_inr = sum(t["inr"] for t in closed)
    cats = {}
    for t in closed:
        c = cats.setdefault(t["cat"], [0, 0, 0.0])
        c[0] += 1
        c[1] += 1 if t["win"] else 0
        c[2] += t["pl"]
    lines = [f"📊 <b>WEEK SCORECARD</b> ({s_d} - {e_d}) — paper trades"]
    if n:
        lines.append(f"Closed: {n} | Won {wins} | Lost {n - wins} | Avg per trade {_fmt_pct(avg)} | Net ₹{net_inr:,.0f}")
        for name in ps._CAT_ORDER:
            if name in cats:
                c = cats[name]
                lines.append(f"• {name}: {c[0]} closed, {c[1]}W/{c[0] - c[1]}L, avg {_fmt_pct(c[2] / c[0])}")
        best = max(closed, key=lambda t: t["pl"])
        worst = min(closed, key=lambda t: t["pl"])
        lines.append(f"Best: {best['sym']} {_fmt_pct(best['pl'])} | Worst: {worst['sym']} {_fmt_pct(worst['pl'])}")
    else:
        lines.append("No trade closed this week.")
    if opens:
        top = sorted(opens, key=lambda x: -x[1])[:4]
        lines.append("Open now: " + ", ".join(f"{s} {_fmt_pct(p)}" for s, p in top) + (f" (+{len(opens) - 4} more)" if len(opens) > 4 else ""))
    lines.append("Wins and losses both shown. Paper trading, educational only. Full ledger: ai360trading.in/membership")
    data = {"week_start": start, "week_end": end, "closed": n, "wins": wins, "avg_pct": round(avg, 2),
            "net_inr": round(net_inr), "open": len(opens), "updated": datetime.now(IST).strftime("%Y-%m-%d %H:%M")}
    return "\n".join(lines), data


def send(msg):
    tok = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    sent = 0
    for key in ("CHAT_ID_BASIC", "CHAT_ID_ADVANCE", "CHAT_ID_PREMIUM"):
        chat = os.environ.get(key, "")
        if not tok or not chat:
            continue
        try:
            r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                              json={"chat_id": chat, "text": msg, "parse_mode": "HTML"}, timeout=20)
            print(f"[SCORECARD] {key}: {r.status_code}")
            sent += 1 if r.status_code == 200 else 0
        except Exception as e:
            print(f"[SCORECARD] {key}: {e}")
    return sent


def main():
    dry = "--dry" in sys.argv
    try:
        msg, data = build()
    except Exception as e:
        print(f"[SCORECARD] build failed (fail-open, nothing sent): {e}")
        return 0
    print(msg)
    if dry:
        return 0
    if send(msg):
        os.makedirs("_data", exist_ok=True)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
        print(f"[SCORECARD] wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
