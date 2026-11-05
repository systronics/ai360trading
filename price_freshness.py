"""
price_freshness.py v1.0 (2026-11-05) — does the sheet show LIVE prices during market hours? Tells the owner on Telegram when it does not.

WHY (owner 2026-11-05, after finding that Nifty200 CMP was yesterday's close until ~15:14 IST on 2, 3 and 4 Nov because the price-feed session started
hours late): 'workflow succeeded' is not proof that the DATA is fresh. This compares the sheet's CMP for a fixed sample of liquid stocks + NIFTY with
Yahoo's latest 1-minute price. It does not change any sheet, signal or trade; it only reads and warns. Fail-open: any error = exit 0, no message.

Rule: during 09:25-15:30 IST on a weekday, if >= 4 of the sample differ by more than 0.5% (or NIFTY differs by more than 0.25%) the feed is STALE.
Messages go to the PREMIUM channel only (the owner), at most one 'OK' per day (first check after 09:45) and a warning on every stale check.

USAGE: python price_freshness.py [--force] [--no-telegram]     (--force ignores the market-hours guard, for tests)
"""
import os
import sys
import json
import statistics
from datetime import datetime

import pytz

IST = pytz.timezone("Asia/Kolkata")
SAMPLE = ["RELIANCE", "HDFCBANK", "TCS", "INFY", "ICICIBANK", "SBIN", "ITC", "LT", "AXISBANK", "BHARTIARTL", "MARUTI", "KOTAKBANK"]
STOCK_TOL_PCT, NIFTY_TOL_PCT, MIN_BAD = 0.5, 0.25, 4


def pct_diff(sheet, live):
    if not sheet or not live:
        return None
    return abs(sheet / live - 1) * 100.0


def judge(diffs, nifty_diff):
    """diffs: list of % differences for the stock sample (None = unavailable). Returns (state, bad_count, usable_count)."""
    ok = [d for d in diffs if d is not None]
    if len(ok) < 6:
        return "UNKNOWN", 0, len(ok)
    bad = sum(1 for d in ok if d > STOCK_TOL_PCT)
    if bad >= MIN_BAD or (nifty_diff is not None and nifty_diff > NIFTY_TOL_PCT and bad >= 2):
        return "STALE", bad, len(ok)
    return "OK", bad, len(ok)


def _sheet_cmp():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
    sh = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")
    n = sh.worksheet("Nifty200").get_all_values()
    h = [x.strip() for x in n[0]]
    i = h.index("CMP")
    out = {}
    for r in n[1:]:
        if r and r[0]:
            try:
                out[r[0].replace("NSE:", "").strip()] = float(str(r[i]).replace(",", ""))
            except Exception:
                pass
    return out


def _yahoo_last(sym):
    import yfinance as yf
    t = sym + ".NS" if sym != "NIFTY50" else "^NSEI"
    df = yf.Ticker(t).history(period="1d", interval="1m")
    if df is None or not len(df):
        return None, None
    ts = df.index[-1]
    return float(df["Close"].iloc[-1]), ts


def _telegram(msg):
    from urllib.request import Request, urlopen
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN", ""), os.environ.get("CHAT_ID_PREMIUM", "")
    if not tok or not chat:
        print("[TG] creds missing, not sent")
        return
    req = Request(f"https://api.telegram.org/bot{tok}/sendMessage", data=json.dumps({"chat_id": chat, "text": msg, "parse_mode": "HTML"}).encode(),
                  headers={"Content-Type": "application/json"})
    urlopen(req, timeout=15).read()


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    now = datetime.now(IST)
    hm = now.strftime("%H:%M")
    if "--force" not in argv and not (now.weekday() < 5 and "09:25" <= hm <= "15:30"):
        print(f"[FRESH] {hm} IST is outside market hours, nothing to check")
        return 0
    ok_sent = False
    try:
        sheet = _sheet_cmp()
        diffs, rows = [], []
        for s in SAMPLE:
            live, ts = _yahoo_last(s)
            d = pct_diff(sheet.get(s), live)
            diffs.append(d)
            rows.append((s, sheet.get(s), live, d))
        nl, _ = _yahoo_last("NIFTY50")
        nd = pct_diff(sheet.get("NIFTY50"), nl)
        state, bad, usable = judge(diffs, nd)
        print(f"[FRESH] {hm} IST state={state} bad={bad}/{usable} nifty_diff={None if nd is None else round(nd, 2)}%")
        for s, a, b, d in rows:
            print(f"   {s:11} sheet {a} live {None if b is None else round(b, 2)} diff {None if d is None else round(d, 2)}%")
        if "--no-telegram" in argv:
            return 0
        if state == "STALE":
            worst = ", ".join(f"{s} {d:.1f}%" for s, a, b, d in sorted(rows, key=lambda r: -(r[3] or 0))[:3] if d is not None)
            _telegram(f"⚠️ <b>PRICE FEED CHECK {hm} IST</b>\nSheet prices look OLD: {bad} of {usable} sample stocks differ from live by more than {STOCK_TOL_PCT}% ({worst}).\n"
                      "Signals, entries and exits may use old prices right now. <i>System notice, not a trade signal.</i>")
        elif state == "OK" and hm >= "09:28" and "--no-ok" not in argv:   # first good check of the day (the loop then passes --no-ok)
            ok_sent = True
            _telegram(f"✅ <b>Price check {hm} IST</b>: {usable - bad} of {usable} sample stocks match the live price (NIFTY diff {nd:.2f}%). Feed is live.")
    except Exception as e:
        print(f"[FRESH] skipped (fail-open): {str(e)[:120]}")
    return 10 if ok_sent else 0


if __name__ == "__main__":
    sys.exit(main())
