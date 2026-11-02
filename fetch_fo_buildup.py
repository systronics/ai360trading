"""
fetch_fo_buildup.py — EOD futures buildup columns + Sector_Board tab — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT (owner task 2026-11-01):
  For every Nifty200 stock that has F&O, show the end-of-day FUTURES buildup next to the stock, and add a sector-level board.
  INFORMATIONAL ONLY — never read by trading_bot.py, appscript.gs, Master_Score, Trade_Type, any GATE, alert or ledger
  (see CLAUDE.md 🔒 NEVER CHANGE, same doctrine as fetch_ath.py / fetch_dividends.py / ShadowLedger).

DATA: the official NSE F&O bhavcopy archive (nsearchives, the same file fetch_bhavcopy.py already downloads on GitHub Actions).
  No cookie API, no paid service, no new key. Rows with FinInstrmTp == 'STF' (stock futures).

CLASSIFY (price = NEAR-month future change %, OI = change % summed over ALL expiries so rollover cannot fake a 'Long Unwinding'):
  price up  & OI up   -> Long Buildup        price up   & OI down -> Short Covering
  price down & OI up  -> Short Buildup       price down & OI down -> Long Unwinding      else Neutral    (no STF rows -> No F&O)
  (buy-side-only system: on the sheet 'Short Buildup' just means 'avoid'; nothing here suggests shorting.)

WRITES (all by HEADER NAME, appended at the END of Nifty200, never touching other columns; ONE batched write; fail-open):
  Fut_Price_Chg_%  Fut_OI_Chg_%  Buildup  Buildup_Streak  Buildup_Date      + a rebuilt 'Sector_Board' tab (median-based).
  Idempotent: a row whose Buildup_Date already equals the bhavcopy date is skipped (a re-run never double-counts a streak).

USAGE:
  python fetch_fo_buildup.py                 # dry-run for the latest available bhavcopy (prints, writes nothing)
  python fetch_fo_buildup.py --date 2026-10-30 [--write]
  python fetch_fo_buildup.py --write
"""

import os
import io
import sys
import csv
import json
import time
import zipfile
import statistics
from datetime import datetime, timedelta, date
from urllib.request import Request, urlopen

import pytz

IST = pytz.timezone("Asia/Kolkata")
VERSION = "v1.0"
SHEET_NAME = "Ai360tradingAlgo"
NIFTY200 = "Nifty200"
BOARD_TAB = "Sector_Board"

# thresholds (owner spec) — named constants
PRICE_EPS_PCT = 0.20   # |price change| below or equal to this = flat
OI_EPS_PCT = 1.00      # |OI change| below or equal to this = flat
SEND_TELEGRAM_SUMMARY = False   # owner turns this on later; message text only, Basic channel only, no entry/SL/target

SYM_HEADER, SECTOR_HEADER, PCT_HEADER, OPTIONS_HEADER, N200_HEADER = "NSE_SYMBOL", "SECTOR", "%Change", "Options", "N200"
H_PRICE, H_OI, H_LABEL, H_STREAK, H_DATE = "Fut_Price_Chg_%", "Fut_OI_Chg_%", "Buildup", "Buildup_Streak", "Buildup_Date"
NEW_HEADERS = [H_PRICE, H_OI, H_LABEL, H_STREAK, H_DATE]

LONG_B, SHORT_C, SHORT_B, LONG_U, NEUTRAL, NO_FO = "Long Buildup", "Short Covering", "Short Buildup", "Long Unwinding", "Neutral", "No F&O"
FOUR = (LONG_B, SHORT_C, SHORT_B, LONG_U)

HEADERS_HTTP = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept": "*/*",
                "Referer": "https://www.nseindia.com/"}


# ───────────────────────────── pure logic (unit-tested) ─────────────────────────────

def _f(v):
    try:
        s = str(v).strip().replace(",", "")
        return float(s) if s else None
    except ValueError:
        return None


def classify(price_pct, oi_pct):
    """Label from near-month price change % and all-expiry OI change %. Boundaries are NEUTRAL (strict > / <)."""
    if price_pct is None or oi_pct is None:
        return NEUTRAL
    p_up, p_dn = price_pct > PRICE_EPS_PCT, price_pct < -PRICE_EPS_PCT
    o_up, o_dn = oi_pct > OI_EPS_PCT, oi_pct < -OI_EPS_PCT
    if p_up and o_up:
        return LONG_B
    if p_up and o_dn:
        return SHORT_C
    if p_dn and o_up:
        return SHORT_B
    if p_dn and o_dn:
        return LONG_U
    return NEUTRAL


def summarize(rows):
    """{symbol: {'price_pct','oi_pct','date'}} from bhavcopy rows (STF only). Near month = earliest XpryDt; OI summed over ALL expiries."""
    by = {}
    for r in rows:
        if (r.get("FinInstrmTp") or "").strip() != "STF":
            continue
        sym = (r.get("TckrSymb") or "").strip()
        if sym:
            by.setdefault(sym, []).append(r)
    out = {}
    for sym, lst in by.items():
        lst = sorted(lst, key=lambda r: (r.get("XpryDt") or ""))
        near = lst[0]
        cls, prv = _f(near.get("ClsPric")), _f(near.get("PrvsClsgPric"))
        price_pct = (cls - prv) / prv * 100.0 if (cls is not None and prv and prv > 0) else None
        oi = sum(_f(r.get("OpnIntrst")) or 0.0 for r in lst)
        chg = sum(_f(r.get("ChngInOpnIntrst")) or 0.0 for r in lst)
        base = oi - chg
        oi_pct = chg / base * 100.0 if base > 0 else None
        out[sym] = {"price_pct": price_pct, "oi_pct": oi_pct, "date": (near.get("TradDt") or "").strip()}
    return out


def _is_trading_day(d, holidays):
    return d.weekday() < 5 and d.strftime("%Y-%m-%d") not in holidays


def next_streak(prev_label, prev_date, prev_streak, new_label, new_date, holidays=frozenset()):
    """Returns the new streak, or None when the row must be SKIPPED (same/older date: idempotent re-run).
    Consecutive = same label AND no trading day between prev_date and new_date (a missed day resets to 1)."""
    if not prev_date:
        return 1
    try:
        pd_, nd = date.fromisoformat(prev_date), date.fromisoformat(new_date)
    except ValueError:
        return 1
    if nd <= pd_:
        return None
    if new_label != prev_label:
        return 1
    d = pd_ + timedelta(days=1)
    while d < nd:
        if _is_trading_day(d, holidays):
            return 1     # a trading day we did not record sits between: do not claim a streak
        d += timedelta(days=1)
    try:
        return int(float(prev_streak)) + 1
    except (TypeError, ValueError):
        return 1


def mood(bull_ratio, week_pct):
    if bull_ratio is None:
        return "🟡 Mixed"
    if bull_ratio >= 60 and week_pct is not None and week_pct > 0:
        return "🟢 Strong"
    if bull_ratio <= 40 and week_pct is not None and week_pct < 0:
        return "🔴 Weak"
    return "🟡 Mixed"


def sector_rows(stocks, labels, ret1d, ret1w, ret1m, updated):
    """stocks: [(symbol, sector)] (N200 YES only). Returns sorted board rows (list of lists)."""
    by = {}
    for sym, sec in stocks:
        by.setdefault(sec, []).append(sym)
    out = []
    for sec, syms in by.items():
        def med(d):
            vals = [d[s] for s in syms if d.get(s) is not None]
            return round(statistics.median(vals), 2) if vals else None
        cnt = {k: sum(1 for s in syms if labels.get(s) == k) for k in FOUR}
        tot = sum(cnt.values())
        bull = round((cnt[LONG_B] + cnt[SHORT_C]) / tot * 100.0, 1) if tot else None
        w = med(ret1w)
        out.append([sec, len(syms), med(ret1d), w, med(ret1m), cnt[LONG_B], cnt[SHORT_C], cnt[SHORT_B], cnt[LONG_U],
                    bull if bull is not None else "", mood(bull, w), updated])
    out.sort(key=lambda r: (r[9] == "", -(r[9] or 0)))
    return out


# ───────────────────────────── data download ─────────────────────────────

def _download(d):
    url = f"https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{d.strftime('%Y%m%d')}_F_0000.csv.zip"
    last = None
    for attempt in range(2):
        try:
            with urlopen(Request(url, headers=HEADERS_HTTP), timeout=40) as r:
                raw = r.read()
            z = zipfile.ZipFile(io.BytesIO(raw))
            text = z.read(z.namelist()[0]).decode("utf-8", errors="replace")
            return list(csv.DictReader(io.StringIO(text)))
        except Exception as e:
            last = e
            time.sleep(2)
    raise RuntimeError(f"{url}: {last}")


def load_rows(on_date=None):
    """(rows, trade_date). Walks back up to 6 days from today (or tries exactly on_date). ([], None) on failure."""
    if on_date:
        try:
            return _download(on_date), on_date
        except Exception as e:
            print(f"[FO] {on_date}: {e}")
            return [], None
    today = datetime.now(IST).date()
    for back in range(0, 7):
        d = today - timedelta(days=back)
        if d.weekday() >= 5:
            continue
        try:
            rows = _download(d)
            print(f"[FO] using F&O bhavcopy for {d.isoformat()} ({len(rows):,} rows)")
            return rows, d
        except Exception as e:
            print(f"[FO] {d.isoformat()}: {str(e)[:120]}")
    return [], None


# ───────────────────────────── sheet helpers ─────────────────────────────

def _a1_col(n):
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _connect():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        try:
            with open("service_account.json") as f:
                raw = f.read().strip()
        except FileNotFoundError:
            raise SystemExit("[CREDS] GCP_SERVICE_ACCOUNT_JSON not set and no local service_account.json")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)
    return gspread.authorize(creds).open(SHEET_NAME)


def _holidays():
    try:
        import indian_holidays
        return set(indian_holidays._get_holiday_set())
    except Exception as e:
        print(f"[CAL] holiday list unavailable ({str(e)[:80]}), weekends only")
        return set()


def _returns_yf(symbols):
    """(ret1w, ret1m) dicts of 5- and 21-trading-day close-to-close returns %, via ONE batched yfinance download. {} on failure."""
    try:
        import yfinance as yf
        tick = [s + ".NS" for s in symbols]
        df = yf.download(tick, period="3mo", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
        w, m = {}, {}
        for s in symbols:
            try:
                c = df[s + ".NS"]["Close"].dropna()
                if len(c) > 22:
                    w[s] = (float(c.iloc[-1]) / float(c.iloc[-6]) - 1) * 100.0
                    m[s] = (float(c.iloc[-1]) / float(c.iloc[-22]) - 1) * 100.0
            except Exception:
                continue
        return w, m
    except Exception as e:
        print(f"[YF] returns unavailable (fail-open, 1W/1M left blank): {str(e)[:100]}")
        return {}, {}


def _ensure_headers(ws, header, write):
    cols, nxt = {}, len(header)
    missing = [h for h in NEW_HEADERS if h not in [x.strip() for x in header]]
    if write and missing and len(header) + len(missing) > ws.col_count:
        ws.add_cols(len(header) + len(missing) - ws.col_count)
    for h in NEW_HEADERS:
        idx = next((j for j, x in enumerate(header) if x.strip() == h), None)
        if idx is None:
            idx = nxt
            nxt += 1
            if write:
                ws.update_cell(1, idx + 1, h)
            print(f"[HEADER] {'created' if write else 'would create'} '{h}' at col {_a1_col(idx + 1)}")
        cols[h] = idx
    return cols


def _add_formatting(sh, ws, col_idx, mapping, title):
    """Add background colours for exact-text matches once. Never fails the job."""
    try:
        meta = sh.fetch_sheet_metadata()
        for s in meta["sheets"]:
            if s["properties"]["sheetId"] == ws.id:
                for rule in s.get("conditionalFormats", []):
                    for rg in rule.get("ranges", []):
                        if rg.get("startColumnIndex") == col_idx:
                            print(f"[FORMAT] {title}: already formatted")
                            return
        reqs = []
        for text, (r, g, b) in mapping.items():
            reqs.append({"addConditionalFormatRule": {"index": 0, "rule": {
                "ranges": [{"sheetId": ws.id, "startRowIndex": 1, "startColumnIndex": col_idx, "endColumnIndex": col_idx + 1}],
                "booleanRule": {"condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": text}]},
                                "format": {"backgroundColor": {"red": r, "green": g, "blue": b}}}}}})
        sh.batch_update({"requests": reqs})
        print(f"[FORMAT] {title}: colours added")
    except Exception as e:
        print(f"[FORMAT] {title}: skipped ({str(e)[:100]})")


# ───────────────────────────── BuildupWatch (observation-only evidence) ─────────────────────────────
# Every label in FOUR plus Neutral (the baseline to compare against) is logged once per (date, symbol); 1/3/5-trading-day forward returns are filled in later from yfinance.
# It reads/writes ONLY its own tab: never AlertLog/History/BotMemory, never an alert, never any gate. Same doctrine as ShadowLedger.

WATCH_TAB = "BuildupWatch"
WATCH_HEAD = ["Date", "Symbol", "Label", "Streak", "Fut_Price_Chg_%", "Fut_OI_Chg_%", "Ret_1d_%", "Ret_3d_%", "Ret_5d_%"]


def fwd_ret(dates, closes, sig_date, n):
    """% return from the close ON sig_date to the close n trading days later; None if not available yet.
    dates: sorted list of 'YYYY-MM-DD'; closes: same length."""
    if sig_date not in dates:
        return None
    i = dates.index(sig_date)
    if i + n >= len(dates) or not closes[i]:
        return None
    return round((closes[i + n] / closes[i] - 1) * 100.0, 2)


def watch_append(sh, info, tdate):
    try:
        try:
            ws = sh.worksheet(WATCH_TAB)
        except Exception:
            ws = sh.add_worksheet(WATCH_TAB, rows=2000, cols=len(WATCH_HEAD))
            ws.update(range_name="A1", values=[WATCH_HEAD])
        existing = ws.get_all_values()
        have = {(r[0], r[1]) for r in existing[1:] if len(r) > 1}
        new = [[tdate, sym, v[2], v[3], v[0], v[1], "", "", ""] for sym, v in info.items() if v[2] in FOUR + (NEUTRAL,) and (tdate, sym) not in have]
        if new:
            start = len(existing) + 1   # explicit next row (append_rows could overwrite earlier rows: 2 rows went missing on 2026-11-01)
            if ws.row_count < start + len(new) + 5:
                ws.add_rows(len(new) + 500)
            ws.update(range_name=f"A{start}", values=new, value_input_option="USER_ENTERED")
        print(f"[WATCH] logged {len(new)} new rows in {WATCH_TAB}")
    except Exception as e:
        print(f"[WATCH] log skipped (fail-open): {str(e)[:120]}")


def watch_score(sh):
    try:
        ws = sh.worksheet(WATCH_TAB)
        vals = ws.get_all_values()
        todo = [(i + 2, r) for i, r in enumerate(vals[1:]) if len(r) >= 2 and r[0] and (len(r) < 9 or not r[8])]
        cutoff = (datetime.now(IST).date() - timedelta(days=3)).isoformat()
        todo = [(i, r) for i, r in todo if r[0] <= cutoff]
        if not todo:
            print("[WATCH] nothing to score yet")
            return
        import yfinance as yf
        syms = sorted({r[1] for _, r in todo})
        df = yf.download([s + ".NS" for s in syms], period="3mo", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
        body = []
        for i, r in todo:
            try:
                c = df[r[1] + ".NS"]["Close"].dropna()
                dts = [d.strftime("%Y-%m-%d") for d in c.index]
                cl = [float(x) for x in c.values]
                rets = [fwd_ret(dts, cl, r[0], n) for n in (1, 3, 5)]
                if any(x is not None for x in rets):
                    body.append({"range": f"G{i}:I{i}", "values": [["" if x is None else x for x in rets]]})
            except Exception:
                continue
        for k in range(0, len(body), 200):
            ws.batch_update(body[k:k + 200], value_input_option="USER_ENTERED")
        print(f"[WATCH] scored {len(body)} rows")
    except Exception as e:
        print(f"[WATCH] scoring skipped (fail-open): {str(e)[:120]}")


def watch_report(sh):
    """Per-label summary: how many signals, average forward return, share of winners (read-only)."""
    ws = sh.worksheet(WATCH_TAB)
    rows = [r + [""] * (9 - len(r)) for r in ws.get_all_values()[1:] if r and r[0]]
    print(f"[REPORT] {len(rows)} logged signals")
    for lab in FOUR + (NEUTRAL, "ALL"):
        sel = [r for r in rows if lab == "ALL" or r[2] == lab]
        line = f"  {lab:15} n={len(sel):4}"
        for j, nm in ((6, "1d"), (7, "3d"), (8, "5d")):
            v = [_f(r[j]) for r in sel if _f(r[j]) is not None]
            line += f" | {nm}: n={len(v):3} avg={statistics.mean(v):+.2f}% win={sum(1 for x in v if x > 0) / len(v) * 100:.0f}%" if v else f" | {nm}: n=0"
        print(line)


# ───────────────────────────── main ─────────────────────────────

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    write = "--write" in argv
    on_date = None
    if "--date" in argv:
        on_date = date.fromisoformat(argv[argv.index("--date") + 1])
    print(f"[fetch_fo_buildup {VERSION}] {datetime.now(IST):%Y-%m-%d %H:%M IST} | mode={'WRITE' if write else 'DRY-RUN'}")
    if "--report" in argv:
        watch_report(_connect())
        return 0

    rows, trade_date = load_rows(on_date)
    if not rows:
        print("[FO] no bhavcopy available, nothing touched (fail-open).")
        return 0
    data = summarize(rows)
    tdate = trade_date.isoformat()
    print(f"[FO] {len(data)} symbols with stock futures on {tdate}")

    sh = _connect()
    ws = sh.worksheet(NIFTY200)
    header = ws.row_values(1)
    cols = _ensure_headers(ws, header, write)
    all_vals = ws.get_all_values()
    hdr = [x.strip() for x in all_vals[0]]

    def ci(name):
        return hdr.index(name) if name in hdr else None

    sym_c, sec_c, pct_c, opt_c, n200_c = (ci(SYM_HEADER), ci(SECTOR_HEADER), ci(PCT_HEADER), ci(OPTIONS_HEADER), ci(N200_HEADER))
    if sym_c is None:
        print(f"[FATAL] column {SYM_HEADER} not found, aborting without writing")
        return 1
    holidays = _holidays()

    def cell(r, name):
        j = cols[name]
        return r[j] if (j is not None and len(r) > j) else ""

    labels, stocks, ret1d, updates, info = {}, [], {}, [], {}
    unmatched, fo_tag_missing = [], []
    for i, r in enumerate(all_vals[1:], start=2):
        if len(r) <= sym_c or not r[sym_c].strip():
            continue
        raw = r[sym_c].strip()
        sym = raw.replace("NSE:", "").strip()
        if "NIFTY" in raw.upper():
            continue
        d = data.get(sym)
        if d is None:
            label, price_c, oi_c = NO_FO, "", ""
            tag = (r[opt_c].strip().upper() if (opt_c is not None and len(r) > opt_c) else "")
            if tag in ("N50", "YES"):
                fo_tag_missing.append(sym)
        else:
            price_c = round(d["price_pct"], 2) if d["price_pct"] is not None else ""
            oi_c = round(d["oi_pct"], 2) if d["oi_pct"] is not None else ""
            label = classify(d["price_pct"], d["oi_pct"])
        labels[sym] = label
        if n200_c is not None and len(r) > n200_c and r[n200_c].strip().upper() == "YES" and sec_c is not None and len(r) > sec_c and r[sec_c].strip():
            stocks.append((sym, r[sec_c].strip()))
            v = _f(r[pct_c]) if (pct_c is not None and len(r) > pct_c) else None
            if v is not None:
                ret1d[sym] = v
        prev_label, prev_date, prev_streak = cell(r, H_LABEL), cell(r, H_DATE), cell(r, H_STREAK)
        if label == NO_FO:
            streak = "" if prev_date != tdate else None
            info[sym] = (price_c, oi_c, label, "")
            if prev_date == tdate:
                continue
        else:
            streak = next_streak(prev_label, prev_date, prev_streak, label, tdate, holidays)
            try:
                eff = streak if streak is not None else int(float(prev_streak))
            except (TypeError, ValueError):
                eff = 1
            info[sym] = (price_c, oi_c, label, eff)
        if streak is None:
            continue   # same/older date: idempotent
        updates.append((i, [price_c, oi_c, label, streak, tdate], sym))

    counts = {}
    for l in labels.values():
        counts[l] = counts.get(l, 0) + 1
    print("[LABELS]", counts)
    if fo_tag_missing:
        print(f"[WARN] {len(fo_tag_missing)} stocks tagged F&O in col AJ but without stock futures in this bhavcopy: {fo_tag_missing[:10]}")
    # preview
    show = [u for u in updates if u[2] in ("HINDUNILVR", "ITC")] + [u for u in updates if u[2] not in ("HINDUNILVR", "ITC")][:8]
    print("\n  symbol         fut_price%  fut_OI%   label            streak")
    for _, vals, sym in show:
        print(f"  {sym:14} {str(vals[0]):>9}  {str(vals[1]):>8}   {vals[2]:16} {vals[3]}")

    # sector board
    ret1w, ret1m = _returns_yf([s for s, _ in stocks]) if stocks else ({}, {})
    board = sector_rows(stocks, labels, ret1d, ret1w, ret1m, tdate)
    print(f"\n[BOARD] {len(board)} sectors")
    for b in board[:6]:
        print("  ", b)

    target = os.environ.get("FO_TELEGRAM", "").strip().lower()
    if "--tg-test" in argv and target not in ("premium", "basic"):
        target = "premium"
    if "--tg-test" in argv:
        _telegram(info, board, tdate, target, open_trades(sh))

    if not write:
        print("\n[DRY-RUN] nothing written. Re-run with --write to update the sheet.")
        return 0

    # ONE batched write for the Nifty200 columns (they are contiguous at the end)
    cs = sorted(cols.values())
    contiguous = cs == list(range(cs[0], cs[0] + len(cs))) and [cols[h] for h in NEW_HEADERS] == cs
    body = []
    for i, vals, _ in updates:
        if contiguous:
            body.append({"range": f"{_a1_col(cs[0] + 1)}{i}:{_a1_col(cs[-1] + 1)}{i}", "values": [vals]})
        else:
            for h, v in zip(NEW_HEADERS, vals):
                body.append({"range": f"{_a1_col(cols[h] + 1)}{i}", "values": [[v]]})
    for k in range(0, len(body), 200):
        ws.batch_update(body[k:k + 200], value_input_option="USER_ENTERED")
        time.sleep(1.0)
    print(f"[WRITE] {len(updates)} Nifty200 rows updated ({len(body)} ranges)")

    # Sector_Board (rebuilt in one write)
    try:
        try:
            bw = sh.worksheet(BOARD_TAB)
        except Exception:
            bw = sh.add_worksheet(BOARD_TAB, rows=40, cols=14)
        head = ["Sector", "Stocks", "1D_%", "1W_%", "1M_%", "Long_Buildup", "Short_Covering", "Short_Buildup", "Long_Unwinding",
                "Bull_Ratio", "Mood", "Updated"]
        bw.clear()
        bw.update(range_name="A1", values=[head] + board, value_input_option="USER_ENTERED")
        print(f"[BOARD] {BOARD_TAB} rebuilt with {len(board)} sectors")
        _add_formatting(sh, bw, 10, {"Strong": (0.80, 0.94, 0.80), "Weak": (0.96, 0.78, 0.78), "Mixed": (1.0, 0.95, 0.70)}, "Mood")
    except Exception as e:
        print(f"[BOARD] skipped ({str(e)[:120]})")

    _add_formatting(sh, ws, cols[H_LABEL], {LONG_B: (0.72, 0.90, 0.72), SHORT_C: (0.90, 0.96, 0.70), SHORT_B: (0.96, 0.70, 0.70),
                                              LONG_U: (0.99, 0.82, 0.62)}, "Buildup")
    refresh_trade_premiums(sh, rows, tdate)
    watch_append(sh, info, tdate)
    watch_score(sh)
    if (SEND_TELEGRAM_SUMMARY or target in ("premium", "basic")) and "--tg-test" not in argv:
        _telegram(info, board, tdate, target or "basic", open_trades(sh))
    return 0


def refresh_trade_premiums(sh, bhav_rows, tdate):
    """Fill Current_Premium (last traded price), NSE_Close_Settle and Premium_Date of every OPEN row in the owner's MyOptionTrades tab from
    the EOD STO rows of the bhavcopy, so the owner never has to type a price. Fail-open, touches only those three cells per row."""
    try:
        ws = sh.worksheet("MyOptionTrades")
        v = ws.get_all_values()
        hd = [x.strip() for x in v[0]]
        extra = [n for n in ("NSE_Close_Settle", "Premium_Date") if n not in hd]
        if extra:
            if len(hd) + len(extra) > ws.col_count:
                ws.add_cols(len(hd) + len(extra) - ws.col_count)
            for n in extra:
                hd.append(n)
                ws.update_cell(1, len(hd), n)
        col = lambda n: hd.index(n)
        body = []
        for i, r in enumerate(v[1:], start=2):
            g = lambda n: (r[col(n)] if n in hd and len(r) > col(n) else "").strip()
            if not g("Symbol") or g("Exit_Date"):
                continue
            strike, typ, exp = _f(g("Strike")), g("Type").upper(), g("Expiry")
            hit = [x for x in bhav_rows if (x.get("FinInstrmTp") or "").strip() in ("STO", "IDO") and (x.get("TckrSymb") or "").strip() == g("Symbol")
                   and (x.get("OptnTp") or "").strip() == typ and (x.get("XpryDt") or "").strip() == exp and _f(x.get("StrkPric")) == strike]
            if not hit:
                print(f"[TRADES] {g('Symbol')} {g('Strike')} {typ} {exp}: not found in today's option rows")
                continue
            x = hit[0]
            for name, val in (("Current_Premium", _f(x.get("LastPric")) or _f(x.get("ClsPric"))), ("NSE_Close_Settle", _f(x.get("ClsPric"))), ("Premium_Date", tdate)):
                if val is not None:
                    body.append({"range": f"{_a1_col(col(name) + 1)}{i}", "values": [[val]]})
        if body:
            ws.batch_update(body, value_input_option="USER_ENTERED")
        print(f"[TRADES] premiums refreshed for {len(body) // 3} open trade(s)")
    except Exception as e:
        print(f"[TRADES] premium refresh skipped (fail-open): {str(e)[:100]}")


def open_trades(sh):
    """Open rows of the owner's own MyOptionTrades tab (no Exit_Date): [(symbol, strike, type, expiry, lot, entry, current, date_in)]. [] if the tab is missing."""
    try:
        ws = sh.worksheet("MyOptionTrades")
        v = ws.get_all_values()
        hd = [x.strip() for x in v[0]]
        out = []
        for r in v[1:]:
            g = lambda n: (r[hd.index(n)] if n in hd and len(r) > hd.index(n) else "").strip()
            if g("Symbol") and not g("Exit_Date"):
                out.append((g("Symbol"), g("Strike"), g("Type"), g("Expiry"), _f(g("Lot_Size")), _f(g("Entry_Premium")), _f(g("Current_Premium")), g("Date_In"), _f(g("NSE_Close_Settle"))))
        return out
    except Exception as e:
        print(f"[TRADES] skipped: {str(e)[:80]}")
        return []


def _telegram(info, board, tdate, target="basic", trades=None):
    """One EOD text message (Premium or Basic channel). Informational, NO entry/SL/target. Never raises."""
    try:
        from urllib.parse import urlencode
        bull = [(s, v) for s, v in info.items() if v[2] in (LONG_B, SHORT_C)]
        bull.sort(key=lambda x: (x[1][2] != LONG_B, -(x[1][3] if isinstance(x[1][3], int) else 0), -(x[1][0] if isinstance(x[1][0], (int, float)) else 0)))
        lines = [f"<b>F&amp;O buildup (EOD {tdate})</b>", "Owner test, signal nahi.", ""]
        lines.append("<b>Bullish buildup, sirf WATCH ke liye:</b>")
        for s, v in bull[:6]:
            lines.append(f"- {s}: {v[2]} ({v[3]} din), fut {v[0]:+.1f}%, OI {v[1]:+.1f}%")
        if not bull:
            lines.append("- Aaj koi nahi.")
        strong = [b for b in board if "Strong" in str(b[10])][:3]
        if strong:
            lines += ["", "Mazboot sectors: " + ", ".join(f"{b[0]} ({b[9]}%)" for b in strong)]
        if trades and target == "premium":
            lines += ["", "<b>Tumhare khule option trade:</b>"]
            for sym, strike, typ, exp, lot, ent, cur, din, nse_close in trades:
                lab = info.get(sym)
                bu = f"{lab[2]} ({lab[3]} din)" if lab else ""
                pl = f", last price {cur} par P/L {((cur - ent) * lot):+,.0f} Rs" if (cur and ent and lot) else ""
                if nse_close and ent and lot:
                    pl += f" (NSE close {nse_close} par {((nse_close - ent) * lot):+,.0f} Rs)"
                held = ""
                try:
                    held = f", {(date.fromisoformat(tdate) - date.fromisoformat(din)).days} din se"
                except ValueError:
                    pass
                lines.append(f"- {sym} {strike} {typ} ({exp}): entry {ent}{pl}{held}. " + (f" Aaj ka buildup: {bu}." if bu else ""))
            lines.append("(Premium roz F&amp;O file se apne aap bharta hai; asli exit bhaav us waqt ka bid/ask hoga.)")
        lines += ["", "Sirf jaankari. Entry, SL, target nahi. Option premium ka P/L stock se alag hota hai (strike, expiry, time decay).",
                  "Informational only, not a trade signal."]
        tok = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat = os.environ.get("CHAT_ID_PREMIUM" if target == "premium" else "CHAT_ID_BASIC", "")
        if tok and chat:
            urlopen(Request(f"https://api.telegram.org/bot{tok}/sendMessage",
                            data=urlencode({"chat_id": chat, "text": "\n".join(lines), "parse_mode": "HTML"}).encode()), timeout=20)
            print(f"[TG] summary sent to {target}")
        else:
            print(f"[TG] skipped: token/chat id for {target} not set")
    except Exception as e:
        print(f"[TG] skipped: {str(e)[:100]}")


if __name__ == "__main__":
    sys.exit(main())
