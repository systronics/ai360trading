"""
AI360 BHAVCOPY CACHE — v1.1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Daily NSE bhavcopy fetcher. Populates BotMemory cache used by
institutional_edges.py for delivery % and Put-Call Ratio filters.

Data sources (₹0 / month, no API key):
  1. NSE Cash market sec_bhavdata_full_{DDMMYYYY}.csv (full delivery file)
     → DLV_{SYM} = delivery % per symbol
  2. NSE official F&O bhavcopy archive (BANKNIFTY + NIFTY index options, end-of-day OI)
     → MKT_PCR_NIFTY     = today's Nifty options PCR (OI)
     → MKT_PCR_BANKNIFTY = today's BankNifty options PCR (OI)

Schedule: daily 20:00 IST (Mon-Fri) — bhavcopy publishes ~6:30 PM.

Self-repair (per feedback_free_forever_self_repair memory):
  • NSE cash bhavcopy URL retries with 2 attempts + 2s sleep; if both fail
    the script continues to PCR fetch (delivery skipped this tick).
  • PCR fetch is independent — failure does not affect delivery write.
  • Existing cache (DLV_*, MKT_PCR_*) continues to serve when source is
    down. Soft Basic-channel notice if BOTH sub-fetchers fail.
  • Stale-clean: DLV_* rows replaced wholesale each day (not accumulated)
    so the sheet stays under control.
"""

import os, json, csv, io, time
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz

IST        = pytz.timezone("Asia/Kolkata")
SHEET_NAME = "Ai360tradingAlgo"
BM_TAB     = "BotMemory"
TG_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_BASIC = os.environ.get("CHAT_ID_BASIC")

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}


# ════════════════════════════════════════════════════════════════════════════
# 1. CASH MARKET DELIVERY  — sec_bhavdata_full
# ════════════════════════════════════════════════════════════════════════════

def _fetch_url(url: str, retries: int = 2, timeout: int = 25) -> bytes:
    """Plain GET with retry — used for NSE bhavcopy CSV."""
    last_err = None
    for attempt in range(retries):
        try:
            req = Request(url, headers=DEFAULT_HEADERS)
            with urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last_err = e
            print(f"[FETCH] {url} attempt {attempt+1}: {e}")
            time.sleep(2)
    raise RuntimeError(f"All retries failed for {url}: {last_err}")


def fetch_delivery_percent() -> dict:
    """
    Returns dict {SYMBOL: deliv_pct_float}.  Empty dict on failure.
    NSE publishes the file as sec_bhavdata_full_DDMMYYYY.csv. We try today
    then walk back up to 5 days to handle holidays.
    """
    today = datetime.now(IST).date()
    for back in range(0, 6):
        d = today - timedelta(days=back)
        if d.weekday() >= 5:    # Saturday=5, Sunday=6
            continue
        date_str = d.strftime("%d%m%Y")
        url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"
        try:
            raw = _fetch_url(url)
            text = raw.decode("utf-8", errors="replace")
            print(f"[DLV] using bhavcopy for {d.isoformat()}")
            return _parse_delivery_csv(text)
        except Exception as e:
            print(f"[DLV] {date_str}: {e}")
            continue
    print("[DLV] no bhavcopy available in last 5 trading days")
    return {}


def _parse_delivery_csv(text: str) -> dict:
    """sec_bhavdata_full columns include SYMBOL, SERIES, DELIV_PER."""
    out = {}
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        sym    = (row.get("SYMBOL") or row.get(" SYMBOL") or "").strip().upper()
        series = (row.get("SERIES") or row.get(" SERIES") or "").strip().upper()
        if series and series != "EQ":      # only EQ series (regular equity)
            continue
        dlv = (row.get("DELIV_PER") or row.get(" DELIV_PER") or "").strip()
        try:
            pct = float(dlv)
        except ValueError:
            continue
        if sym and pct > 0:
            out[sym] = round(pct, 2)
    print(f"[DLV] parsed {len(out)} symbols")
    return out


# ════════════════════════════════════════════════════════════════════════════
# 2. PUT-CALL RATIO — official F&O bhavcopy archive (v1.1)
# ════════════════════════════════════════════════════════════════════════════
# v1.1 (2026-10-23): the old source was NSE's cookie-protected option-chain API, which fails
# from GitHub runners — MKT_PCR_NIFTY/BANKNIFTY were NEVER cached (verified in BotMemory), so
# the PCR check in institutional_edges.py silently always said "not yet cached". Now computed
# from the official end-of-day F&O bhavcopy archive file (static download, no session cookie,
# same family as the cash bhavcopy above): total PUT open interest / total CALL open interest
# across all expiries of the index options. End-of-day, i.e. yesterday's positioning.

_FO_CACHE = {}


def _fo_rows():
    """Rows (dicts) of the latest available F&O bhavcopy, walking back up to 6 days. [] on failure."""
    if "rows" in _FO_CACHE:
        return _FO_CACHE["rows"]
    import zipfile
    today = datetime.now(IST).date()
    for back in range(0, 7):
        d = today - timedelta(days=back)
        if d.weekday() >= 5:
            continue
        url = ("https://nsearchives.nseindia.com/content/fo/"
               f"BhavCopy_NSE_FO_0_0_0_{d.strftime('%Y%m%d')}_F_0000.csv.zip")
        try:
            raw = _fetch_url(url, retries=2, timeout=40)
            z = zipfile.ZipFile(io.BytesIO(raw))
            text = z.read(z.namelist()[0]).decode("utf-8", errors="replace")
            rows = list(csv.DictReader(io.StringIO(text)))
            print(f"[PCR] using F&O bhavcopy for {d.isoformat()} ({len(rows):,} rows)")
            _FO_CACHE["rows"] = rows
            return rows
        except Exception as e:
            print(f"[PCR] {d.isoformat()}: {e}")
    _FO_CACHE["rows"] = []
    return []


def fetch_pcr(symbol: str = "NIFTY") -> float:
    """PCR (open interest) for an index from the official F&O bhavcopy. 0.0 on any failure."""
    try:
        ce = pe = 0.0
        for r in _fo_rows():
            if (r.get("TckrSymb") or "").strip() != symbol or (r.get("FinInstrmTp") or "").strip() != "IDO":
                continue
            oi = float((r.get("OpnIntrst") or "0").strip() or 0)
            tp = (r.get("OptnTp") or "").strip()
            if tp == "CE":
                ce += oi
            elif tp == "PE":
                pe += oi
        if ce <= 0:
            return 0.0
        pcr = pe / ce
        print(f"[PCR] {symbol}: {pcr:.3f}  (OI PUT {pe:,.0f} / CALL {ce:,.0f})")
        return round(pcr, 3)
    except Exception as e:
        print(f"[PCR] {symbol}: {e}")
        return 0.0


# ════════════════════════════════════════════════════════════════════════════
# BOTMEMORY WRITE
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
            raise SystemExit("[CREDS] GCP_SERVICE_ACCOUNT_JSON not set and no local service_account.json")
    creds_dict = json.loads(raw)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds).open(SHEET_NAME)


def write_to_botmemory(delivery: dict, pcr_nifty: float, pcr_banknifty: float):
    if not delivery and pcr_nifty <= 0 and pcr_banknifty <= 0:
        print("[BM] nothing to write — both sources empty")
        return
    ss = _connect()
    bm = ss.worksheet(BM_TAB)
    existing = bm.get_all_values()
    headers  = existing[0] if existing else []
    now_str  = datetime.now(IST).strftime("%Y-%m-%d %H:%M")

    # Build new state — drop old DLV_*/MKT_PCR_* rows wholesale (daily refresh).
    keep_rows = [headers]
    purged = 0
    for row in existing[1:]:
        if not row or not row[0].strip():
            continue
        k = row[0].strip()
        if k.startswith("DLV_") or k in ("MKT_PCR_NIFTY", "MKT_PCR_BANKNIFTY"):
            purged += 1
            continue
        keep_rows.append(row)

    new_rows = []
    if delivery:
        # v1.2 (2026-10-23): the whole NSE cash file (~2,700 symbols) was being stored, but the delivery
        # filter only ever looks up the Nifty200 / CashWatchlist stocks the bot can trade — 2,694 of
        # BotMemory's 4,129 rows were unused weight read by every 5-minute bot tick. Keep only the
        # tradeable universe. Fail-open: if the universe can't be read, keep everything as before.
        try:
            universe = set()
            for tab in ("Nifty200", "CashWatchlist"):
                for v in ss.worksheet(tab).col_values(1)[1:]:
                    v = str(v).replace("NSE:", "").strip().upper()
                    if v:
                        universe.add(v)
            if len(universe) >= 100:
                before = len(delivery)
                delivery = {s: p for s, p in delivery.items() if s in universe}
                print(f"[BM] delivery trimmed to tradeable universe: {before} -> {len(delivery)}")
        except Exception as e:
            print(f"[BM] universe trim skipped (fail-open, storing all): {e}")
        for sym, pct in delivery.items():
            new_rows.append([f"DLV_{sym}", str(pct), now_str, "", "DELIVERY"])
    if pcr_nifty > 0:
        new_rows.append(["MKT_PCR_NIFTY", f"{pcr_nifty:.3f}", now_str, "", "MARKET"])
    if pcr_banknifty > 0:
        new_rows.append(["MKT_PCR_BANKNIFTY", f"{pcr_banknifty:.3f}", now_str, "", "MARKET"])

    final = keep_rows + new_rows
    bm.clear()
    bm.update("A1", final)
    print(f"[BM] purged {purged} old, wrote {len(new_rows)} new — sheet now {len(final)-1} rows")


# ════════════════════════════════════════════════════════════════════════════
# TELEGRAM (basic only — non-trade system notice)
# ════════════════════════════════════════════════════════════════════════════

def _tg(msg):
    if not (TG_TOKEN and CHAT_BASIC):
        return
    try:
        import requests
        requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": CHAT_BASIC, "text": msg, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as e:
        print(f"[TG] {e}")


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    print(f"[BHAVCOPY] start {datetime.now(IST).strftime('%Y-%m-%d %H:%M')} IST")
    delivery = {}
    pcr_nifty = pcr_banknifty = 0.0

    try:
        delivery = fetch_delivery_percent()
    except Exception as e:
        print(f"[DLV] outer error: {e}")

    try:
        pcr_nifty = fetch_pcr("NIFTY")
    except Exception as e:
        print(f"[PCR NIFTY] outer error: {e}")

    try:
        pcr_banknifty = fetch_pcr("BANKNIFTY")
    except Exception as e:
        print(f"[PCR BANKNIFTY] outer error: {e}")

    nothing = (not delivery) and pcr_nifty <= 0 and pcr_banknifty <= 0
    if nothing:
        _tg(
            "ℹ️ <b>System Notice</b>\n"
            "Bhavcopy cache could not refresh today (NSE archives + option-chain both failed). "
            "Existing cache continues to serve filters. Will retry tomorrow. "
            "<i>This is a system message, not a trade signal.</i>"
        )
        print("[BHAVCOPY] all sources failed — kept existing cache. exit 0.")
        return

    try:
        write_to_botmemory(delivery, pcr_nifty, pcr_banknifty)
    except Exception as e:
        print(f"[BHAVCOPY] BM write error: {e}")
        _tg(
            f"ℹ️ <b>System Notice</b>\nBhavcopy fetched but BotMemory write failed: "
            f"{type(e).__name__}. Will retry tomorrow."
        )


if __name__ == "__main__":
    main()
