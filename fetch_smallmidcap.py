"""
AI360 SMALL/MID CAP MOMENTUM SCANNER — v1.2

v1.2 (2026-05-31) — AUTO-TRIM:
  The SmallMidCap tab appends a row (or rows) every scan and grew without
  bound. v1.2 trims it to the header + most-recent SMC_MAX_ROWS (365) data
  rows after each write (keeps the workbook lean under the 10M-cell cap).
  Fail-open: a trim error never blocks the scan.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Daily scanner for institutional-grade small/mid cap winners NOT in Nifty200
universe. Catches the +10–15% movers (GUJTHEM, TVSSRICHAK, MANCREDIT class)
that the existing scanner ignores because they aren't large-cap.

Design philosophy (per Amit ji 2026-05-27): "few signals, long ride, max
momentum profit, no loss tolerance". So this is HIGHLY SELECTIVE — typically
0–3 signals/day, biased toward stocks already showing institutional
accumulation + momentum, not lottery-ticket upper-circuit hits.

OUTPUTS:
  1. Sheet tab `SmallMidCap` — auto-created on first run; a status row is
     written EVERY scan (even on 0-pick days) so the run is always observable.
  2. BotMemory keys `SMC_{YYYY-MM-DD}_RANK{N}_{SYM}` — for downstream tracking
  3. Telegram digest to Advance + Premium (Hinglish, actionable)

SOURCE: NSE cash bhavcopy CSV `sec_bhavdata_full_DDMMYYYY.csv` — same file
        used by fetch_bhavcopy.py, no new API needed.

SCHEDULE: Mon-Fri 20:30 IST (after bhavcopy publishes ~18:30, after
          fetch_bhavcopy.py at 20:00).

FILTERS (all must pass — strict by design):
  • Series == EQ
  • Symbol NOT in Nifty200 (small/mid cap universe only)
  • Today's % change between +4% and +13%        — momentum, not circuit
  • Turnover ≥ ₹20 Cr                            — minimum liquidity
  • Delivery % ≥ 50%                             — institutional accumulation
  • REAL volume multiple (today vs prior 5-day average) ≥ 3×

SCORE (top 3 only):
  score = pct_change × delivery_pct × min(volume_multiple, 6) / 100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v1.1 (2026-05-30) — TRUST + OBSERVABILITY FIXES:
  • REAL VOLUME FILTER. v1.0 used a fake proxy `turnover_cr / TURNOVER_MIN_CR`
    (i.e. just "turnover ≥ ₹60 Cr") but DISPLAYED it to subscribers as
    "Vol 3.0×" — misleading. v1.1 downloads the prior 5 trading days of
    bhavcopy and computes a genuine today-volume ÷ 5-day-average-volume
    multiple per symbol. The "Vol X×" shown is now true. A symbol with
    fewer than VOL_HISTORY_MIN_DAYS of prior data is EXCLUDED (cannot
    confirm momentum → no signal, per "no loss tolerance").
  • ALWAYS-OBSERVABLE TAB. v1.0 only created/wrote the SmallMidCap tab when
    picks existed, so on every 0-pick day the system was silent and the tab
    never appeared — impossible to verify the scan ran. v1.1 always ensures
    the tab and writes a dated scan-status row (picks, or "NO CANDIDATES").
    Idempotent: a re-run for the same bhav date does not duplicate rows.
  • SAFER BOTMEMORY WRITE. v1.0 did `bm.clear()` + full rewrite every run,
    even with 0 picks and nothing to purge — a crash between clear and
    rewrite would WIPE the shared BotMemory the trading bot depends on.
    v1.1 only touches BotMemory when there are picks to add OR stale SMC_
    keys to purge; otherwise it leaves BotMemory untouched.

SELF-REPAIR:
  • Walks back up to 8 calendar days to assemble the needed trading days
  • Auto-creates SmallMidCap tab via gspread if absent
  • Fails SAFE: NO signals (and a clear status row) on bad-data day rather
    than bad/fake signals
  • Stale SMC_* memory keys (>14 days) purged each run that touches BotMemory
"""

import os, json, csv, io, time
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz

IST          = pytz.timezone("Asia/Kolkata")
SHEET_NAME   = "Ai360tradingAlgo"
BM_TAB       = "BotMemory"
SMC_TAB      = "SmallMidCap"
NIFTY200_TAB = "Nifty200"
TG_TOKEN     = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ADVANCE = os.environ.get("CHAT_ID_ADVANCE")
CHAT_PREMIUM = os.environ.get("CHAT_ID_PREMIUM")
CHAT_BASIC   = os.environ.get("CHAT_ID_BASIC")

# Filter thresholds — tweakable
PCT_MIN              = 4.0     # min today %change (excludes flat stocks)
PCT_MAX              = 13.0    # max today %change (excludes upper-circuit).
                               # Bumped from 12 → 13 on 2026-05-27 to catch
                               # TVSSRICHAK-class +12.05% movers visible in
                               # screenshot 6 that were just over the old cap.
                               # Most NSE circuits are 10/15/20% — 13 stays
                               # well below upper-circuit triggers.
TURNOVER_MIN_CR      = 20.0    # ₹20 Cr min turnover (liquidity floor)
DELIVERY_MIN_PCT     = 50.0    # institutional accumulation threshold
VOLUME_MULT_MIN      = 3.0     # today vol vs prior 5-day avg (REAL — v1.1)
VOL_HISTORY_DAYS     = 5       # how many prior trading days form the average
VOL_HISTORY_MIN_DAYS = 3       # need at least this many prior days to trust it
TOP_N                = 3       # max signals per day (selective)
STALE_DAYS           = 14      # purge SMC_* memory rows older than this

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/csv, application/octet-stream, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}


# ════════════════════════════════════════════════════════════════════════════
# BHAVCOPY FETCH (multi-day window for real volume average)
# ════════════════════════════════════════════════════════════════════════════

def _fetch_csv(url: str, retries: int = 2, timeout: int = 25) -> str:
    last = None
    for i in range(retries):
        try:
            req = Request(url, headers=DEFAULT_HEADERS)
            with urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            last = e
            print(f"[CSV] {url} attempt {i+1}: {e}")
            time.sleep(2)
    raise RuntimeError(f"All retries failed for {url}: {last}")


def fetch_bhavcopy_window(need: int = 6, max_days: int = 12) -> list:
    """
    Returns up to `need` most-recent trading days of bhavcopy as a list of
    (date_iso, rows) tuples, NEWEST FIRST. rows is a list-of-dicts from the CSV.
    `need` defaults to 6 = today + VOL_HISTORY_DAYS prior days.
    Walks back up to `max_days` calendar days, skipping weekends and any day
    whose file is missing (holidays / not yet published).
    """
    today = datetime.now(IST).date()
    out = []
    for back in range(0, max_days):
        d = today - timedelta(days=back)
        if d.weekday() >= 5:   # Sat/Sun — no bhavcopy
            continue
        url = (f"https://archives.nseindia.com/products/content/"
               f"sec_bhavdata_full_{d.strftime('%d%m%Y')}.csv")
        try:
            text = _fetch_csv(url)
            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
            if rows:
                out.append((d.isoformat(), rows))
                print(f"[BHAVCOPY] {d.isoformat()} loaded ({len(rows)} rows)")
                if len(out) >= need:
                    break
        except Exception as e:
            print(f"[BHAVCOPY] {d.isoformat()}: {e}")
            continue
    return out


# ════════════════════════════════════════════════════════════════════════════
# GSPREAD CONNECT
# ════════════════════════════════════════════════════════════════════════════

def _connect():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        try:
            with open("service_account.json") as f:
                raw = f.read().strip()
        except FileNotFoundError:
            raise SystemExit("[CREDS] GCP_SERVICE_ACCOUNT_JSON not set + no local service_account.json")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)
    return gspread.authorize(creds).open(SHEET_NAME)


# ════════════════════════════════════════════════════════════════════════════
# NIFTY200 UNIVERSE READ
# ════════════════════════════════════════════════════════════════════════════

def read_nifty200_universe(ss) -> set:
    """Returns set of NSE symbols (without 'NSE:' prefix, upper-case)."""
    try:
        sheet = ss.worksheet(NIFTY200_TAB)
        rows = sheet.get_all_values()
        out = set()
        for row in rows[1:]:
            if row and row[0].strip():
                sym = row[0].replace("NSE:", "").strip().upper()
                if sym:
                    out.add(sym)
        print(f"[NIFTY200] loaded {len(out)} symbols")
        return out
    except Exception as e:
        print(f"[NIFTY200] read error: {e} — universe empty (every stock will be considered)")
        return set()


# ════════════════════════════════════════════════════════════════════════════
# CSV PARSER + SCORE
# ════════════════════════════════════════════════════════════════════════════

def _f(x) -> float:
    try:
        return float(str(x).replace(",", "").strip())
    except Exception:
        return 0.0


def _g(row: dict, key: str) -> str:
    """CSV column lookup with leading-space tolerance (NSE quirk)."""
    return (row.get(key) or row.get(" " + key) or "").strip()


def build_avg_volume(window: list) -> tuple:
    """
    Build per-symbol average traded quantity from the PRIOR days only (i.e.
    every day in `window` except the newest, which is 'today').

    `window` is the list from fetch_bhavcopy_window() — (date, rows) newest
    first. Returns (avg_map, prior_days) where avg_map = {SYMBOL: avg_qty}
    and prior_days = number of days that contributed.
    """
    prior = window[1:1 + VOL_HISTORY_DAYS]   # skip newest (today), take up to 5
    acc = {}                                 # sym -> [count, sum_qty]
    for _date, rows in prior:
        for r in rows:
            if _g(r, "SERIES").upper() != "EQ":
                continue
            sym = _g(r, "SYMBOL").upper()
            qty = _f(_g(r, "TTL_TRD_QNTY"))
            if sym and qty > 0:
                cell = acc.setdefault(sym, [0, 0.0])
                cell[0] += 1
                cell[1] += qty
    avg_map = {s: (v[1] / v[0]) for s, v in acc.items() if v[0] > 0}
    print(f"[VOLAVG] built {len(avg_map)} symbol averages from {len(prior)} prior day(s)")
    return avg_map, len(prior)


def filter_and_score(today_rows: list, nifty200: set, avg_vol: dict, prior_days: int) -> list:
    """
    Returns sorted list of dicts (best score first), all entries that pass
    every filter. Each dict carries fields used for the alert message.
    Volume multiple is REAL (today qty ÷ prior 5-day average qty). A symbol
    without enough prior history (or zero average) is excluded — we never
    fabricate a volume number.
    """
    have_history = prior_days >= VOL_HISTORY_MIN_DAYS
    if not have_history:
        print(f"[VOLAVG] only {prior_days} prior day(s) (<{VOL_HISTORY_MIN_DAYS}) "
              f"— volume cannot be confirmed, scan will yield 0 picks")

    picks = []
    for r in today_rows:
        series = _g(r, "SERIES").upper()
        if series != "EQ":
            continue
        sym = _g(r, "SYMBOL").upper()
        if not sym or sym in nifty200:
            continue

        close      = _f(_g(r, "CLOSE_PRICE"))
        prev_close = _f(_g(r, "PREV_CLOSE"))
        if prev_close <= 0 or close <= 0:
            continue
        pct_change = (close - prev_close) / prev_close * 100
        if not (PCT_MIN <= pct_change <= PCT_MAX):
            continue

        # Turnover in lakhs in NSE CSV → convert to crores (÷100)
        turnover_lakhs = _f(_g(r, "TURNOVER_LACS"))
        turnover_cr    = turnover_lakhs / 100.0
        if turnover_cr < TURNOVER_MIN_CR:
            continue

        dlv_pct = _f(_g(r, "DELIV_PER"))
        if dlv_pct < DELIVERY_MIN_PCT:
            continue

        today_qty = _f(_g(r, "TTL_TRD_QNTY"))
        deliv_qty = _f(_g(r, "DELIV_QTY"))
        if today_qty <= 0:
            continue

        # REAL volume multiple (v1.1): today's traded quantity vs the prior
        # 5-day average for THIS symbol. If we don't have enough history or
        # the symbol has no prior average, we cannot confirm momentum → skip.
        if not have_history:
            continue
        avg_q = avg_vol.get(sym, 0.0)
        if avg_q <= 0:
            continue
        vol_mult = today_qty / avg_q
        if vol_mult < VOLUME_MULT_MIN:
            continue

        score = round(
            pct_change * dlv_pct * min(vol_mult, 6.0) / 100.0,
            2,
        )
        picks.append({
            "symbol":         sym,
            "close":          round(close, 2),
            "prev_close":     round(prev_close, 2),
            "pct_change":     round(pct_change, 2),
            "turnover_cr":    round(turnover_cr, 1),
            "delivery_pct":   round(dlv_pct, 1),
            "vol_mult":       round(vol_mult, 2),
            "deliv_qty":      int(deliv_qty),
            "today_qty":      int(today_qty),
            "score":          score,
        })

    picks.sort(key=lambda p: p["score"], reverse=True)
    return picks[:TOP_N]


# ════════════════════════════════════════════════════════════════════════════
# SHEET TAB MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════

SMC_HEADER = [
    "Date", "Rank", "Symbol", "Close ₹", "Prev Close ₹",
    "% Change", "Turnover ₹Cr", "Delivery %", "Vol Mult (5d real)",
    "Score", "Scan Time IST",
]

def _ensure_smc_tab(ss):
    """Create SmallMidCap tab if missing. Self-repair."""
    try:
        return ss.worksheet(SMC_TAB)
    except gspread.WorksheetNotFound:
        sheet = ss.add_worksheet(title=SMC_TAB, rows=500, cols=12)
        sheet.append_row(SMC_HEADER)
        print(f"[SHEET] created tab {SMC_TAB!r}")
        return sheet


# Auto-trim: this tab appends a row (or rows) every scan, so it grows forever
# without bound. Keep the header + the most recent SMC_MAX_ROWS data rows
# (~1 year of daily scans) and delete older ones. Sheets has a 10M-cell cap;
# this keeps the workbook lean. Fail-open: a trim error never blocks the scan.
SMC_MAX_ROWS = 365

def _trim_smc_tab(sheet):
    try:
        vals = sheet.get_all_values()
        excess = (len(vals) - 1) - SMC_MAX_ROWS   # -1 for header row
        if excess > 0:
            # delete the oldest data rows (rows 2 .. 1+excess); header row 1 kept
            sheet.delete_rows(2, 1 + excess)
            print(f"[SHEET] trimmed {excess} old {SMC_TAB} rows (cap {SMC_MAX_ROWS})")
    except Exception as e:
        print(f"[SHEET] trim skipped (non-fatal): {e}")


def write_smc_sheet(ss, picks: list, bhav_date: str):
    """
    Always ensures the SmallMidCap tab exists and records that the scan ran.
    Writes one row per pick, or a single 'NO CANDIDATES' status row on a
    0-pick day. Idempotent: if the most recent existing row is already for
    this bhav_date, nothing is written (prevents duplicates on re-runs and
    on weekday holidays that re-serve the last trading day's file).
    """
    sheet     = _ensure_smc_tab(ss)
    scan_time = datetime.now(IST).strftime("%Y-%m-%d %H:%M")

    # Idempotency guard — skip if last data row already covers this date.
    try:
        existing = sheet.get_all_values()
        for prev in reversed(existing[1:]):
            if prev and prev[0].strip():
                if prev[0].strip() == bhav_date:
                    print(f"[SHEET] {bhav_date} already recorded — skip duplicate write")
                    return
                break
    except Exception as e:
        print(f"[SHEET] existing-row check failed (proceeding): {e}")

    if not picks:
        sheet.append_row(
            [bhav_date, "—", "NO CANDIDATES", "", "", "", "", "", "", "", scan_time],
            value_input_option="USER_ENTERED",
        )
        print(f"[SHEET] {bhav_date} — 0 picks, status row written")
        _trim_smc_tab(sheet)
        return

    new_rows = []
    for rank, p in enumerate(picks, start=1):
        new_rows.append([
            bhav_date, rank, p["symbol"], p["close"], p["prev_close"],
            f'{p["pct_change"]:+.2f}%', p["turnover_cr"], p["delivery_pct"],
            f'{p["vol_mult"]:.2f}×', p["score"], scan_time,
        ])
    sheet.append_rows(new_rows, value_input_option="USER_ENTERED")
    print(f"[SHEET] appended {len(new_rows)} rows to {SMC_TAB}")
    _trim_smc_tab(sheet)


# ════════════════════════════════════════════════════════════════════════════
# BOTMEMORY WRITE + STALE CLEAN
# ════════════════════════════════════════════════════════════════════════════

def write_bm_keys(ss, picks: list, bhav_date: str):
    """
    Writes SMC_{date}_RANK{N}_{SYM} = "<close>|<deliv>%|<score>" rows in BotMemory.
    Purges SMC_* entries older than STALE_DAYS at the same time.

    SAFETY (v1.1): BotMemory is SHARED with trading_bot.py. v1.0 always did a
    bm.clear() + full rewrite — a crash mid-write would wipe the bot's state.
    v1.1 only performs the destructive clear+rewrite when there is something
    to change (new picks to add, or stale SMC_ keys to purge). On a normal
    0-pick day with no stale keys, BotMemory is left completely untouched.
    """
    bm = ss.worksheet(BM_TAB)
    existing = bm.get_all_values()
    headers  = existing[0] if existing else ["Key", "Value", "Updated", "", "Type"]
    today    = datetime.now(IST).date()
    now_str  = datetime.now(IST).strftime("%Y-%m-%d %H:%M")

    keep   = [headers]
    purged = 0
    for row in existing[1:]:
        if not row or not row[0].strip():
            continue
        k = row[0].strip()
        if k.startswith("SMC_"):
            try:
                d = datetime.strptime(k.split("_")[1], "%Y-%m-%d").date()
                if (today - d).days > STALE_DAYS:
                    purged += 1
                    continue
            except Exception:
                pass
        keep.append(row)

    # Nothing to add and nothing stale to remove → do NOT touch BotMemory.
    if not picks and purged == 0:
        print("[BM] no picks, nothing stale — BotMemory left untouched (safe)")
        return

    for rank, p in enumerate(picks, start=1):
        key = f"SMC_{bhav_date}_RANK{rank}_{p['symbol']}"
        val = f"{p['close']}|{p['delivery_pct']:.0f}%|score={p['score']}"
        keep.append([key, val, now_str, "", "SMC"])

    bm.clear()
    bm.update(range_name="A1", values=keep)
    print(f"[BM] purged {purged} stale SMC_, wrote {len(picks)} new")


# ════════════════════════════════════════════════════════════════════════════
# TELEGRAM
# ════════════════════════════════════════════════════════════════════════════

def _tg(chat_id, msg):
    if not (TG_TOKEN and chat_id):
        return
    try:
        import requests
        requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as e:
        print(f"[TG] {e}")


def send_digest(picks: list, bhav_date: str):
    if not picks:
        msg = (
            f"🔍 <b>Small/Mid Cap Scan — {bhav_date}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"No candidates passed today's strict filters.\n\n"
            f"<i>Filters: +{PCT_MIN:.0f}% to +{PCT_MAX:.0f}% move, ₹{TURNOVER_MIN_CR:.0f}Cr+ turnover, "
            f"{DELIVERY_MIN_PCT:.0f}%+ delivery, {VOLUME_MULT_MIN:.0f}× real 5-day volume.</i>\n\n"
            f"Cleaner setups tomorrow — quality over quantity."
        )
        _tg(CHAT_ADVANCE, msg)
        _tg(CHAT_PREMIUM, msg)
        return

    lines = [
        f"💎 <b>SMALL/MID CAP MOMENTUM PICKS — {bhav_date}</b>",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"<i>Highly selective scan — outside Nifty200, institutional buying confirmed.</i>",
        "",
    ]
    for rank, p in enumerate(picks, start=1):
        lines.append(
            f"<b>#{rank}  {p['symbol']}</b>  ₹{p['close']:.2f}  ({p['pct_change']:+.2f}%)\n"
            f"   Turnover ₹{p['turnover_cr']:.1f} Cr  |  Delivery {p['delivery_pct']:.0f}%  "
            f"|  Vol {p['vol_mult']:.1f}× (5d avg)\n"
            f"   <i>Score: {p['score']}</i>"
        )
    lines.append("")
    lines.append("📌 <b>Trade plan idea (manual entry):</b>")
    lines.append("   • Entry: tomorrow 9:30-10:00 AM if holding above today's close")
    lines.append("   • SL: today's low × 0.98  (max -3%)")
    lines.append("   • Target: ride with Chandelier trail — let momentum extend")
    lines.append("   • Position size: small (1-2% of capital) — small-caps swing wider")
    lines.append("")
    lines.append("⚠️ <i>Educational signals. Paper trading only — Phase 4 auto-trade not enabled.</i>")
    msg = "\n".join(lines)
    _tg(CHAT_ADVANCE, msg)
    _tg(CHAT_PREMIUM, msg)
    print(f"[TG] digest sent — {len(picks)} picks")


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    print(f"[SMC] start {datetime.now(IST).strftime('%Y-%m-%d %H:%M')} IST")

    # Fetch today + prior days in one window so we can compute a REAL volume
    # average. need = 1 (today) + VOL_HISTORY_DAYS prior.
    window = fetch_bhavcopy_window(need=1 + VOL_HISTORY_DAYS)
    if not window:
        _tg(CHAT_BASIC,
            "ℹ️ <b>System Notice</b>\nSmall/Mid Cap scan: bhavcopy unavailable. "
            "Will retry tomorrow. <i>System message, not a trade signal.</i>")
        print("[SMC] no bhavcopy — exit 0")
        return

    bhav_date, today_rows = window[0]
    avg_vol, prior_days   = build_avg_volume(window)

    ss       = _connect()
    nifty200 = read_nifty200_universe(ss)
    picks    = filter_and_score(today_rows, nifty200, avg_vol, prior_days)
    print(f"[SMC] {len(picks)} candidate(s) passed all filters "
          f"(today={bhav_date}, prior_days={prior_days})")
    for p in picks:
        print(f"  • {p['symbol']}: {p['pct_change']:+.2f}%  ₹{p['turnover_cr']:.1f}Cr  "
              f"DLV {p['delivery_pct']:.0f}%  Vol {p['vol_mult']:.2f}x  score={p['score']}")

    # Always record that the scan ran (picks or a status row) — observability.
    try:
        write_smc_sheet(ss, picks, bhav_date)
    except Exception as e:
        print(f"[SMC] sheet write error: {e}")

    try:
        write_bm_keys(ss, picks, bhav_date)
    except Exception as e:
        print(f"[SMC] BotMemory write error: {e}")

    send_digest(picks, bhav_date)


if __name__ == "__main__":
    main()
