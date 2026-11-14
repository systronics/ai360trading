"""
fetch_opt_trend.py v1.0 (2026-11-14 NEW) - feeds two columns at the END of the Nifty200 tab for the OPTION gates (owner order 2026-11-14: "ADX is needed for options, I accept the risk
if it only affects the option signal"):
    Opt_ADX    = daily ADX(14) of the last COMPLETED daily bar (Wilder)
    Opt_Trend  = "OK" when ADX >= 25 AND +DI > -DI (an up-trend with strength), else "NO"; blank when there is not enough history
Read by appscript.gs v15.42 (an Options Alert / BUY CE needs Opt_Trend != "NO"; blank = fail-open) and by trading_bot.py option_entry_gate (same rule).
WHY: an option buyer is paying theta every day, so a sideways stock (ADX < 25 or -DI above +DI) is the wrong place for it. Own 2017-2026 study (207 stocks, 5-day forward):
P(stock reaches +4% within 5 days) 37.3% on any day, 34.5% when ADX<20, 45.7% after a volume breakout with ADX>=25 and +DI>-DI.
Columns are found/created BY HEADER NAME at the end of the sheet (nothing shifts), one batched write, fail-open (a failed run leaves the old values). Runs as a continue-on-error
step in fetch_rs.yml (08:45 + 12:30 IST). USAGE: python fetch_opt_trend.py (dry-run)   python fetch_opt_trend.py --write
"""
import os
import sys
import json
import datetime as dt

import pytz

import watch_plan as WP

IST = pytz.timezone("Asia/Kolkata")
VERSION = "v1.0"
ADX_MIN = 25.0
H_ADX, H_TREND = "Opt_ADX", "Opt_Trend"


def trend_flag(highs, lows, closes):
    """-> (adx, 'OK'|'NO'|'') ; '' when there is not enough history."""
    ax = WP._adx(highs, lows, closes)
    if not ax:
        return None, ""
    adx, pdi, mdi = ax
    return round(adx, 1), ("OK" if (adx >= ADX_MIN and pdi > mdi) else "NO")


def _a1(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _connect():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
    return gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    write = "--write" in argv
    now = dt.datetime.now(IST)
    print(f"[fetch_opt_trend {VERSION}] {now:%Y-%m-%d %H:%M IST} mode={'WRITE' if write else 'DRY-RUN'}")
    try:
        import yfinance as yf
        sh = _connect()
        ws = sh.worksheet("Nifty200")
        vals = ws.get_all_values()
        header = [x.strip() for x in vals[0]]
        syms = [(i, r[0].replace("NSE:", "").strip()) for i, r in enumerate(vals) if i >= 2 and r and r[0]]
        df = yf.download([s + ".NS" for _, s in syms], period="8mo", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
        drop_today = now.hour * 60 + now.minute < 15 * 60 + 35
        out = {}
        for _, s in syms:
            try:
                x = df[s + ".NS"].dropna(subset=["Close"])
                if drop_today and len(x) and x.index[-1].date() == now.date():
                    x = x.iloc[:-1]
                out[s] = trend_flag([float(v) for v in x.High], [float(v) for v in x.Low], [float(v) for v in x.Close])
            except Exception:
                out[s] = (None, "")
        ok = sum(1 for v in out.values() if v[1] == "OK")
        no = sum(1 for v in out.values() if v[1] == "NO")
        print(f"[OPT-TREND] {len(out)} stocks: OK {ok}, NO {no}, blank {len(out) - ok - no}")
        if not write:
            return 0
        need = [h for h in (H_ADX, H_TREND) if h not in header]
        if need:
            if ws.col_count < len(header) + len(need):
                ws.add_cols(len(header) + len(need) - ws.col_count)
            ws.update(range_name=f"{_a1(len(header) + 1)}1", values=[need])
            header += need
        c_adx, c_tr = header.index(H_ADX), header.index(H_TREND)
        body = []
        for i, s in syms:
            adx, flag = out.get(s, (None, ""))
            body.append({"range": f"{_a1(c_adx + 1)}{i + 1}:{_a1(c_tr + 1)}{i + 1}", "values": [["" if adx is None else adx, flag]]})
        for k in range(0, len(body), 150):
            ws.batch_update(body[k:k + 150], value_input_option="USER_ENTERED")
        try:                                                          # the column can inherit a DATE format from its neighbours: force a plain number
            ws.format(f"{_a1(c_adx + 1)}3:{_a1(c_adx + 1)}{len(vals) + 5}", {"numberFormat": {"type": "NUMBER", "pattern": "0.0"}})
        except Exception as e:
            print(f"[OPT-TREND] number format skipped: {str(e)[:80]}")
        print(f"[OPT-TREND] wrote {len(body)} rows to columns {H_ADX}/{H_TREND}")
    except Exception as e:                                           # fail-open: old values stay
        print(f"[fetch_opt_trend] skipped (fail-open): {str(e)[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
