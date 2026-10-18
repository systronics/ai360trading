"""
fetch_bottom_levels.py — BottomScanner level feed (informational only)
=====================================================================
v1.0 (2026-10-18)

WHAT THIS DOES
  The BottomScanner tab used to hold ~44 pass-through formulas per row copying
  almost every Nifty200 column (heavy: ~13k formulas, ~295 rows incl. blanks).
  It is now slim:
    * a few columns that READ Nifty200 (CMP, structure, RS, 52w, volume...)
    * Python-fed LEVEL columns this script computes from yfinance daily bars:
        Prev_Day_High/Low, Prev_Week_High/Low, Support_1 (nearest swing low
        below price), Support_2 (60-day low), Resistance_1 (nearest swing high
        above price), Base_Range_20D_%, Retest_Level, Retest_Status
    * sheet formulas that combine the two into Bottom_Stage (swing/positional/
      SIP engine) and Intraday_Setup (intraday/options engine).

  DELIBERATELY INFORMATIONAL ONLY — same doctrine as fetch_ath.py /
  fetch_dividends.py / ShadowLedger: nothing in trading_bot.py or appscript.gs
  reads these columns; they are not gates. Promote to a gate only after the
  owner has seen backtested numbers and explicitly asks.

  Evidence behind the Intraday_Setup wording (2026-10-18, 74 real History
  trades): entries ABOVE the previous day's high lost (-₹910 net, 35% win) while
  entries below it made +₹4,436 (48% win) — so "above PDH" is flagged as
  CHASING, not as a buy signal. Above-previous-WEEK-high looked helpful for
  swing (80% win) but on only 5 trades — shown, not trusted.

USAGE
  python fetch_bottom_levels.py --build   # (re)create layout: header + formulas
  python fetch_bottom_levels.py --write   # fill the Python-fed level columns
  python fetch_bottom_levels.py           # dry-run: compute + print, no sheet write

FAIL-OPEN: a failed download/symbol leaves the existing cell untouched, never
blanked. Header-name lookups only (no hardcoded Nifty200 column letters).
"""

import os, sys, json
from datetime import datetime
import pytz

IST        = pytz.timezone("Asia/Kolkata")
VERSION    = "v1.0"
SHEET_NAME = "Ai360tradingAlgo"
NIFTY200   = "Nifty200"
TAB        = "BottomScanner"

PIVOT_K       = 3      # bars each side that must be higher/lower for a swing pivot
PIVOT_WINDOW  = 60     # completed sessions searched for swing pivots
BASE_WINDOW   = 20     # completed sessions for base-range tightness
BREAKOUT_BACK = 5      # sessions: "recent" breakout window for retest detection
RETEST_BAND   = 1.5    # % either side of the broken level counts as a retest zone
MIN_TRADED_CR = 10.0   # ₹ crore avg daily traded value treated as liquid

# Columns read from Nifty200 (our header -> Nifty200 header). Row-aligned
# formulas, exactly like the old tab (=Nifty200!X{row}); letters resolved by name.
NIFTY_PULL = [
    ("NSE_SYMBOL",       "NSE_SYMBOL"),
    ("SECTOR",           "SECTOR"),
    ("CMP",              "CMP"),
    ("%Change",          "%Change"),
    ("SMA_Structure",    "SMA_Structure"),
    ("%down_from_52W_High", "%down_from_52W_UP"),
    ("%up_from_52W_Low", "%up_from_52W_Low"),
    ("%_from_ATH",       "%_from_ATH"),
    ("RS",               "RS"),
    ("Volume_vs_Avg %",  "Volume_vs_Avg %"),
    ("Master_Score",     "Master_Score"),
    ("Breakout_Stage",   "Breakout_Stage"),
]
LEVEL_COLS = [
    "Prev_Day_High", "Prev_Day_Low", "Prev_Week_High", "Prev_Week_Low",
    "Support_1", "Support_2", "Resistance_1", "Base_Range_20D_%",
    "Retest_Level", "Retest_Status", "Levels_Updated",
]
# Formula columns (computed in-sheet from the two groups above).
FORMULA_COLS = [
    "Liquidity_Cr", "Above_Prev_Day_High", "Above_Prev_Week_High",
    "%_above_Support_1", "Bottom_Stage", "Intraday_Setup",
]


def _connect():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        try:
            with open("service_account.json") as f:
                raw = f.read().strip()
        except FileNotFoundError:
            raise SystemExit("[CREDS] GCP_SERVICE_ACCOUNT_JSON not set and service_account.json not found")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)
    return gspread.authorize(creds).open(SHEET_NAME)


def _a1(n):
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _yf_symbol(sym):
    return sym.strip().upper().replace("NSE:", "").strip() + ".NS"


# ── pure level maths (unit-testable, no I/O) ───────────────────────────────────
def swing_lows(lows, k=PIVOT_K):
    return [(i, lows[i]) for i in range(k, len(lows) - k)
            if lows[i] == min(lows[i - k:i + k + 1])]


def swing_highs(highs, k=PIVOT_K):
    return [(i, highs[i]) for i in range(k, len(highs) - k)
            if highs[i] == max(highs[i - k:i + k + 1])]


def compute_levels(dates, highs, lows, closes, today):
    """dates: list of datetime.date (completed sessions only, oldest first).
    Returns dict of level values, or None when there is too little history."""
    n = len(closes)
    if n < 30:
        return None
    last = closes[-1]

    pdh, pdl = highs[-1], lows[-1]

    def wk(d):
        iso = d.isocalendar()
        return (iso[0], iso[1])
    cur_wk = wk(today)
    weeks = []
    for i, d in enumerate(dates):
        k = wk(d)
        if k == cur_wk:
            continue
        if not weeks or weeks[-1][0] != k:
            weeks.append([k, [i]])
        else:
            weeks[-1][1].append(i)
    if weeks:
        idx = weeks[-1][1]
        pwh = max(highs[i] for i in idx)
        pwl = min(lows[i] for i in idx)
    else:
        pwh = pwl = None

    w = slice(max(0, n - PIVOT_WINDOW), n)
    wl, wh = lows[w], highs[w]
    below = [v for _, v in swing_lows(wl) if v < last]
    above = [v for _, v in swing_highs(wh) if v > last]
    s1 = max(below) if below else min(lows[-20:])
    s2 = min(wl)
    r1 = min(above) if above else max(wh)

    bw = slice(n - BASE_WINDOW, n)
    base_rng = (max(highs[bw]) - min(lows[bw])) / last * 100.0

    # Retest: a level (highest high of the 20 sessions ending BREAKOUT_BACK ago)
    # that price closed above within the last BREAKOUT_BACK sessions, and price is
    # now back within ±RETEST_BAND% of it.
    ref = slice(max(0, n - BASE_WINDOW - BREAKOUT_BACK), n - BREAKOUT_BACK)
    level = max(highs[ref])
    broke = max(closes[-BREAKOUT_BACK:]) > level
    dist = (last / level - 1) * 100.0
    if broke and -RETEST_BAND <= dist <= RETEST_BAND * 1.5:
        status = "RETEST ZONE"
    elif broke and dist > RETEST_BAND * 1.5:
        status = "BROKE OUT (extended)"
    elif last >= level * 0.985 and not broke:
        status = "NEAR BREAKOUT"
    else:
        status = ""
    return dict(pdh=pdh, pdl=pdl, pwh=pwh, pwl=pwl, s1=s1, s2=s2, r1=r1,
                base=base_rng, retest_level=level, retest_status=status)


def _round(v, nd=2):
    return "" if v is None else round(float(v), nd)


def build_layout(ws, n_rows, header_map):
    """Write header + row-aligned Nifty200 pull formulas + in-sheet formulas.
    header_map: Nifty200 header -> column letter."""
    headers = [h for h, _ in NIFTY_PULL] + LEVEL_COLS + FORMULA_COLS
    col = {h: _a1(i + 1) for i, h in enumerate(headers)}
    rows = [headers]
    for r in range(2, n_rows + 2):
        row = []
        for ours, theirs in NIFTY_PULL:
            letter = header_map.get(theirs.lower())
            row.append(f"=Nifty200!{letter}{r}" if letter else "")
        row += [""] * len(LEVEL_COLS)
        c = lambda h: f"{col[h]}{r}"
        cmp_, vol, struct = c("CMP"), c("Volume_vs_Avg %"), c("SMA_Structure")
        row.append(  # Liquidity_Cr: Avg_Volume_(20D) x CMP / 1e7, read straight from Nifty200
            f"=IFERROR(Nifty200!{header_map.get('avg_volume_(20d)','N')}{r}*{cmp_}/10000000,\"\")")
        row.append(f'=IF({c("Prev_Day_High")}="","",IF({cmp_}>{c("Prev_Day_High")},"YES","NO"))')
        row.append(f'=IF({c("Prev_Week_High")}="","",IF({cmp_}>{c("Prev_Week_High")},"YES","NO"))')
        row.append(f'=IF({c("Support_1")}="","",ROUND(({cmp_}/{c("Support_1")}-1)*100,2))')
        deep = f'{c("%down_from_52W_High")}<=-25'
        tight = f'{c("Base_Range_20D_%")}<=15'
        row.append(
            f'=IF({c("Prev_Week_High")}="","",'
            f'IF(AND({deep},{tight},{cmp_}>{c("Prev_Week_High")}),"BOTTOM CONFIRMED",'
            f'IF(AND({deep},{tight}),"BASING",'
            f'IF({deep},"DEEP CORRECTION","-"))))')
        liq_ok = f'N({c("Liquidity_Cr")})>={MIN_TRADED_CR}'
        row.append(
            f'=IF({c("Prev_Day_High")}="","",'
            f'IF(NOT({liq_ok}),"ILLIQUID - SKIP",'
            f'IF({c("Retest_Status")}="RETEST ZONE","RETEST BUY ZONE",'
            f'IF(AND(ABS({c("%_above_Support_1")})<=1.5,{cmp_}>={c("Support_1")}),"AT SUPPORT",'
            f'IF({c("Above_Prev_Day_High")}="YES","ABOVE PDH - CHASING, WAIT PULLBACK","-")))))')
        rows.append(row)
    ws.clear()
    end_col = _a1(len(headers))
    ws.update(range_name=f"A1:{end_col}{len(rows)}", values=rows, value_input_option="USER_ENTERED")
    return headers


def main():
    do_build = "--build" in sys.argv
    do_write = "--write" in sys.argv
    mode = "BUILD+WRITE" if (do_build and do_write) else "BUILD" if do_build else "WRITE" if do_write else "DRY-RUN"
    now = datetime.now(IST)
    print(f"[fetch_bottom_levels {VERSION}] {now:%Y-%m-%d %H:%M IST} | mode={mode}")

    sh = _connect()
    n200 = sh.worksheet(NIFTY200)
    nh = n200.row_values(1)
    lower = [h.strip().lower() for h in nh]
    header_map = {}
    for i, h in enumerate(lower):          # first occurrence wins
        header_map.setdefault(h, _a1(i + 1))
    syms_all = n200.col_values(lower.index("nse_symbol") + 1)[1:]
    n_rows = len(syms_all)

    try:
        ws = sh.worksheet(TAB)
    except Exception:
        ws = sh.add_worksheet(title=TAB, rows=n_rows + 10, cols=len(NIFTY_PULL) + len(LEVEL_COLS) + len(FORMULA_COLS))
        do_build = True
    if do_build:
        hdrs = build_layout(ws, n_rows, header_map)
        print(f"[BUILD] layout written: {len(hdrs)} cols x {n_rows} rows")
        # trim empty grid
        ws.resize(rows=n_rows + 2, cols=len(hdrs))
    if not do_write and not mode == "DRY-RUN":
        return 0

    try:
        import yfinance as yf
    except Exception as e:
        print(f"[FATAL] yfinance unavailable: {e}")
        return 1

    head = ws.row_values(1)
    cidx = {h: i for i, h in enumerate(head)}
    missing = [h for h in LEVEL_COLS if h not in cidx]
    if missing:
        print(f"[FATAL] BottomScanner missing columns {missing} — run with --build")
        return 1
    syms = ws.col_values(1)
    targets = [(r + 1, s) for r, s in enumerate(syms) if r >= 1 and s.upper().startswith("NSE:")]
    print(f"[SYMS] {len(targets)} NSE symbols")

    import pandas as pd
    tick = [_yf_symbol(s) for _, s in targets]
    raw = yf.download(tick, period="9mo", interval="1d", group_by="ticker",
                      auto_adjust=False, progress=False, threads=True)
    today = now.date()
    drop_today = now.hour * 60 + now.minute < 15 * 60 + 45
    updates = {}
    ok = bad = 0
    for (row, s), t in zip(targets, tick):
        try:
            df = raw[t].dropna(subset=["High", "Low", "Close"])
            if drop_today and len(df) and df.index[-1].date() == today:
                df = df.iloc[:-1]
            lv = compute_levels([d.date() for d in df.index], df["High"].tolist(),
                                df["Low"].tolist(), df["Close"].tolist(), today)
            if not lv:
                bad += 1
                continue
            vals = [_round(lv["pdh"]), _round(lv["pdl"]), _round(lv["pwh"]), _round(lv["pwl"]),
                    _round(lv["s1"]), _round(lv["s2"]), _round(lv["r1"]), _round(lv["base"]),
                    _round(lv["retest_level"]), lv["retest_status"], f"{now:%Y-%m-%d %H:%M}"]
            updates[row] = vals
            ok += 1
        except Exception:
            bad += 1
    print(f"[CALC] ok={ok} skipped={bad}")
    if not do_write:
        sym_by_row = {r: x for r, x in targets}
        for row, v in list(updates.items())[:5]:
            print(sym_by_row[row], v)
        return 0

    first = cidx[LEVEL_COLS[0]]
    batch = []
    for row, vals in updates.items():
        a = f"{_a1(first + 1)}{row}:{_a1(first + len(LEVEL_COLS))}{row}"
        batch.append({"range": a, "values": [vals]})
    for i in range(0, len(batch), 100):
        ws.batch_update(batch[i:i + 100], value_input_option="USER_ENTERED")
    print(f"[WRITE] {len(batch)} rows updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
