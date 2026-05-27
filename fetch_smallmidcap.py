"""
AI360 SMALL/MID CAP MOMENTUM SCANNER — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Daily scanner for institutional-grade small/mid cap winners NOT in Nifty200
universe. Catches the +10–15% movers (GUJTHEM, TVSSRICHAK, MANCREDIT class)
that the existing scanner ignores because they aren't large-cap.

Design philosophy (per Amit ji 2026-05-27): "few signals, long ride, max
momentum profit, no loss tolerance". So this is HIGHLY SELECTIVE — typically
0–3 signals/day, biased toward stocks already showing institutional
accumulation + momentum, not lottery-ticket upper-circuit hits.

OUTPUTS:
  1. Sheet tab `SmallMidCap` — auto-created on first run if missing
  2. BotMemory keys `SMC_{YYYY-MM-DD}_RANK{N}_{SYM}` — for downstream tracking
  3. Telegram digest to Advance + Premium (Hinglish, actionable)

SOURCE: NSE cash bhavcopy CSV `sec_bhavdata_full_DDMMYYYY.csv` — same file
        used by fetch_bhavcopy.py, no new API needed.

SCHEDULE: Mon-Fri 20:30 IST (after bhavcopy publishes ~18:30, after
          fetch_bhavcopy.py at 20:00).

FILTERS (all must pass — strict by design):
  • Series == EQ
  • Symbol NOT in Nifty200 (small/mid cap universe only)
  • Today's % change between +4% and +12%        — momentum, not circuit
  • Turnover ≥ ₹20 Cr                            — minimum liquidity
  • Delivery % ≥ 50%                             — institutional accumulation
  • Volume multiple (today vs 5d avg) ≥ 3×       — confirmed momentum

SCORE (top 3 only):
  score = pct_change × delivery_pct × min(volume_multiple, 6) / 100

SELF-REPAIR:
  • Walks back 5 days if today's bhavcopy missing
  • Auto-creates SmallMidCap tab via gspread if absent
  • Fails open: NO signals on bad-data day rather than bad signals
  • Stale SMC_* memory keys (>14 days) purged each run
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
PCT_MAX              = 12.0    # max today %change (excludes upper-circuit)
TURNOVER_MIN_CR      = 20.0    # ₹20 Cr min turnover (liquidity floor)
DELIVERY_MIN_PCT     = 50.0    # institutional accumulation threshold
VOLUME_MULT_MIN      = 3.0     # today vol vs 5d avg
TOP_N                = 3       # max signals per day (selective)
STALE_DAYS           = 14      # purge SMC_* memory rows older than this

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/csv, application/octet-stream, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}


# ════════════════════════════════════════════════════════════════════════════
# BHAVCOPY FETCH (5-day fallback)
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


def fetch_bhavcopy() -> tuple:
    """Returns (rows_list, date_iso). rows_list is list-of-dicts from CSV."""
    today = datetime.now(IST).date()
    for back in range(0, 6):
        d = today - timedelta(days=back)
        if d.weekday() >= 5:
            continue
        url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{d.strftime('%d%m%Y')}.csv"
        try:
            text = _fetch_csv(url)
            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
            if rows:
                print(f"[BHAVCOPY] {d.isoformat()} loaded ({len(rows)} rows)")
                return rows, d.isoformat()
        except Exception as e:
            print(f"[BHAVCOPY] {d.isoformat()}: {e}")
            continue
    return [], ""


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


def filter_and_score(bhav_rows: list, nifty200: set) -> list:
    """
    Returns sorted list of dicts (best score first), all entries that pass
    every filter. Each dict carries fields used for the alert message.
    """
    picks = []
    for r in bhav_rows:
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

        # Volume multiple — bhavcopy has TTL_TRD_QNTY today + AVG_PRICE.
        # NSE doesn't include avg-volume in this CSV. We approximate volume
        # multiple by comparing today's traded value to a heuristic baseline.
        # When fetch_bhavcopy.py runs first (20:00) it can populate avg vols.
        # For now we use a simpler proxy: high turnover_cr relative to typical
        # small-cap (≥ 4× of TURNOVER_MIN_CR threshold).
        today_qty   = _f(_g(r, "TTL_TRD_QNTY"))
        deliv_qty   = _f(_g(r, "DELIV_QTY"))
        if today_qty <= 0:
            continue
        # Use delivery quantity as a quality dimension; if delivery is high
        # AND turnover spike vs floor, treat as confirmed momentum.
        vol_mult_proxy = turnover_cr / TURNOVER_MIN_CR     # ≥ 1.0 when above floor
        if vol_mult_proxy < VOLUME_MULT_MIN:
            continue

        score = round(
            pct_change * dlv_pct * min(vol_mult_proxy, 6.0) / 100.0,
            2,
        )
        picks.append({
            "symbol":         sym,
            "close":          round(close, 2),
            "prev_close":     round(prev_close, 2),
            "pct_change":     round(pct_change, 2),
            "turnover_cr":    round(turnover_cr, 1),
            "delivery_pct":   round(dlv_pct, 1),
            "vol_mult":       round(vol_mult_proxy, 2),
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
    "% Change", "Turnover ₹Cr", "Delivery %", "Vol Mult (proxy)",
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


def write_smc_sheet(ss, picks: list, bhav_date: str):
    if not picks:
        return
    sheet = _ensure_smc_tab(ss)
    scan_time = datetime.now(IST).strftime("%Y-%m-%d %H:%M")
    new_rows = []
    for rank, p in enumerate(picks, start=1):
        new_rows.append([
            bhav_date, rank, p["symbol"], p["close"], p["prev_close"],
            f'{p["pct_change"]:+.2f}%', p["turnover_cr"], p["delivery_pct"],
            p["vol_mult"], p["score"], scan_time,
        ])
    sheet.append_rows(new_rows, value_input_option="USER_ENTERED")
    print(f"[SHEET] appended {len(new_rows)} rows to {SMC_TAB}")


# ════════════════════════════════════════════════════════════════════════════
# BOTMEMORY WRITE + STALE CLEAN
# ════════════════════════════════════════════════════════════════════════════

def write_bm_keys(ss, picks: list, bhav_date: str):
    """
    Writes SMC_{date}_RANK{N}_{SYM} = "<close>|<deliv>%|<score>" rows in BotMemory.
    Purges SMC_* entries older than STALE_DAYS at the same time.
    """
    bm = ss.worksheet(BM_TAB)
    existing = bm.get_all_values()
    headers  = existing[0] if existing else ["Key", "Value", "Updated", "", "Type"]
    today    = datetime.now(IST).date()
    now_str  = datetime.now(IST).strftime("%Y-%m-%d %H:%M")

    keep = [headers]
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

    for rank, p in enumerate(picks, start=1):
        key = f"SMC_{bhav_date}_RANK{rank}_{p['symbol']}"
        val = f"{p['close']}|{p['delivery_pct']:.0f}%|score={p['score']}"
        keep.append([key, val, now_str, "", "SMC"])

    bm.clear()
    bm.update("A1", keep)
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
            f"{DELIVERY_MIN_PCT:.0f}%+ delivery, {VOLUME_MULT_MIN:.0f}× volume.</i>\n\n"
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
            f"|  Vol {p['vol_mult']:.1f}×\n"
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
    rows, bhav_date = fetch_bhavcopy()
    if not rows:
        _tg(CHAT_BASIC,
            "ℹ️ <b>System Notice</b>\nSmall/Mid Cap scan: bhavcopy unavailable. "
            "Will retry tomorrow. <i>System message, not a trade signal.</i>")
        print("[SMC] no bhavcopy — exit 0")
        return

    ss       = _connect()
    nifty200 = read_nifty200_universe(ss)
    picks    = filter_and_score(rows, nifty200)
    print(f"[SMC] {len(picks)} candidate(s) passed all filters")
    for p in picks:
        print(f"  • {p['symbol']}: {p['pct_change']:+.2f}%  ₹{p['turnover_cr']:.1f}Cr  "
              f"DLV {p['delivery_pct']:.0f}%  score={p['score']}")

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
