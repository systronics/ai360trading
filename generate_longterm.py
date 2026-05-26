"""
AI360 Long-Term Investment Signals — v1.6
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v1.6 CHANGES vs v1.5 (2026-05-26 audit BUG-3 + BUG-4):
  BUG-3 FIX — _rsi() returned NaN on flat 14-day windows (no down days OR
              both gain and loss zero) because `gain / loss` → 0/0 = NaN.
              NaN then propagated into make_signal() corrupting classification.
              FIX: divide by `loss.replace(0, 1e-10)` (same pattern as
              trading_bot.py get_rsi at line 357) and clamp NaN → 50.0.

  BUG-4 FIX — make_signal() ladder evaluated `score >= 3` (HOLD) BEFORE the
              BOOK PARTIAL condition, so a stock at 95% of 52W high with
              moderate score was tagged HOLD instead of BOOK PARTIAL —
              contradicting the file's own header comment ("BOOK PARTIAL —
              near 52W high / RSI ≥ 72"). FIX: insert BOOK PARTIAL check
              between ACCUMULATE and HOLD so it fires whenever pos_pct >= 85
              OR rsi >= 72 (regardless of score). STRONG BUY / ACCUMULATE
              still take precedence because a high score requires near-52W-low
              conditions that cannot coexist with near-high status.

v1.5 CHANGES vs v1.4:
  - Weekly P&L cutoff widened from 7 → 8 days to capture Friday-edge trades
    on Sunday morning run (avoids missing trades exited late Friday).

v1.4 CHANGES vs v1.3:
  - Decoupled price/52w from yfinance .info. CMP/52W now come from hist
    (always reliable), .info is best-effort for fundamentals only. yfinance
    .info is heavily throttled and returns null for many Indian-stock fields;
    this way FundScore quality may degrade but signals always have correct
    price/52W/RSI.
  - LTWatchlist update uses batch_update (1 API call) instead of 25 sequential
    update_cell + 25 cell reads. Saves ~30s per Sunday run.
  - Notes column now pre-fetched in _load_watchlist (avoids per-row read inside
    the update loop).

v1.3 CHANGES vs v1.2:
  - Cred validation: clear "GCP credentials missing" error instead of cryptic
    FileNotFoundError when GCP_SERVICE_ACCOUNT_JSON env var is empty AND
    no local service_account.json exists.

v1.2 CHANGES vs v1.1:
  - Weekly P&L performance report added (runs before investment picks)
    Basic: Hinglish wins/losses/₹ — drives upgrades
    Advance+Premium: full breakdown with best/worst trade
  - PositionalLatest tab: public-facing, cleared+rewritten each Sunday
  - Auto-archive: LongTermSignals >600 rows → SignalsArchive (forever)

v1.1 CHANGES vs v1.0:
  - FundScore now AUTO-CALCULATED from yfinance ratios (ROE, margins, debt, growth)
  - FIIChange% now AUTO-CALCULATED from institutionPercentHeld delta (stored in sheet)
  - LTWatchlist auto-seeded with quality stocks if tab is empty
  - LTWatchlist updated every run with fresh FundScore + FIIChange%
  - Zero manual input required — fully autonomous after first run

Signal logic:
  STRONG BUY  — near 52W low + oversold RSI + institutional buying + strong fundamentals
  ACCUMULATE  — attractive dip, quality intact, add in tranches
  HOLD        — keep existing; no fresh entry
  BOOK PARTIAL— near 52W high / RSI overbought
  WAIT        — fair-valued, no clear signal

Free channel (CHAT_ID_BASIC): stock + signal only → drives upgrades to Advance/Premium.
Advance+Premium: full entry zone, SL, 12m target, reasons.

Runs: Every Sunday 9:00 AM IST (longterm_signals.yml)
Sheet: "Ai360tradingAlgo" — reads/writes LTWatchlist, writes LongTermSignals
"""

import os, json, time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import yfinance as yf
import requests
from datetime import datetime
import pytz

IST        = pytz.timezone("Asia/Kolkata")
VERSION    = "v1.6"
SHEET_NAME = "Ai360tradingAlgo"

LT_WATCHLIST    = "LTWatchlist"
LT_SIGNALS      = "LongTermSignals"
POSITIONAL_LIVE = "PositionalLatest"   # public-facing tab — cleared + rewritten every Sunday

# LTWatchlist column indices (0-based after get_all_values)
# Row 1 = headers. Script manages columns A-H.
# A=Symbol B=Company C=Sector D=FundScore E=FIIChange% F=Active G=Notes H=InstHeld%
COL_SYM      = 0   # A
COL_COMPANY  = 1   # B
COL_SECTOR   = 2   # C
COL_FUND     = 3   # D — auto-updated each run
COL_FII      = 4   # E — auto-updated each run (institutionPercentHeld delta)
COL_ACTIVE   = 5   # F
COL_NOTES    = 6   # G
COL_INSTHELD = 7   # H — auto-updated: last seen institutionPercentHeld (for delta calc)

# 25 quality Indian stocks — pre-seeded on first run if LTWatchlist is empty
DEFAULT_WATCHLIST = [
    # (Symbol, Company, Sector)
    ("NSE:TCS",        "TCS",             "IT"),
    ("NSE:INFY",       "Infosys",         "IT"),
    ("NSE:HDFCBANK",   "HDFC Bank",       "Banking"),
    ("NSE:ICICIBANK",  "ICICI Bank",      "Banking"),
    ("NSE:RELIANCE",   "Reliance",        "Energy"),
    ("NSE:ASIANPAINT", "Asian Paints",    "FMCG"),
    ("NSE:BAJFINANCE", "Bajaj Finance",   "NBFC"),
    ("NSE:HINDUNILVR", "HUL",             "FMCG"),
    ("NSE:KOTAKBANK",  "Kotak Bank",      "Banking"),
    ("NSE:AXISBANK",   "Axis Bank",       "Banking"),
    ("NSE:HCLTECH",    "HCL Tech",        "IT"),
    ("NSE:TITAN",      "Titan",           "Consumer"),
    ("NSE:NESTLEIND",  "Nestle India",    "FMCG"),
    ("NSE:PIDILITIND", "Pidilite",        "Chemicals"),
    ("NSE:ITC",        "ITC",             "FMCG"),
    ("NSE:LT",         "L&T",             "Infra"),
    ("NSE:ULTRACEMCO", "Ultratech Cement","Cement"),
    ("NSE:DIVISLAB",   "Divi's Lab",      "Pharma"),
    ("NSE:DRREDDY",    "Dr Reddy's",      "Pharma"),
    ("NSE:SUNPHARMA",  "Sun Pharma",      "Pharma"),
    ("NSE:MARUTI",     "Maruti Suzuki",   "Auto"),
    ("NSE:M&M",        "Mahindra",        "Auto"),
    ("NSE:POWERGRID",  "Power Grid",      "Utilities"),
    ("NSE:COALINDIA",  "Coal India",      "Energy"),
    ("NSE:WIPRO",      "Wipro",           "IT"),
]

# ── Telegram ──────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
BASIC     = os.environ.get("CHAT_ID_BASIC", "")
ADVANCE   = os.environ.get("CHAT_ID_ADVANCE", "")
PREMIUM   = os.environ.get("CHAT_ID_PREMIUM", "")

def _tg(chat_id, msg):
    if not chat_id or not BOT_TOKEN:
        return
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
            timeout=12,
        )
        if not r.ok:
            print(f"[TG] {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"[TG] {e}")
    time.sleep(0.6)

def _tg_chunked(chat_id, lines, max_chars=3900):
    msg, chunk = "", ""
    for line in lines:
        if len(chunk) + len(line) + 1 > max_chars:
            _tg(chat_id, chunk)
            chunk = line
        else:
            chunk = (chunk + "\n" + line) if chunk else line
    if chunk:
        _tg(chat_id, chunk)

# ── Google Sheets ─────────────────────────────────────────────────────────────
def _connect():
    # v1.3: explicit cred validation — fails with clear message instead of cryptic FileNotFoundError
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        try:
            with open("service_account.json") as f:
                raw = f.read().strip()
        except FileNotFoundError:
            raise SystemExit("[CREDS] GCP_SERVICE_ACCOUNT_JSON env var not set and service_account.json not found locally")
    try:
        creds_dict = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"[CREDS] Failed to parse GCP credentials JSON: {e}")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    gc    = gspread.authorize(creds)
    return gc.open(SHEET_NAME)

def _get_or_create(wb, name, headers):
    try:
        return wb.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = wb.add_worksheet(title=name, rows=500, cols=max(len(headers), 10))
        ws.append_row(headers)
        print(f"[SHEET] Created tab: {name}")
        return ws

# ── LTWatchlist: auto-seed + auto-update ─────────────────────────────────────
LT_HEADERS = ["Symbol", "Company", "Sector", "FundScore", "FIIChange%",
               "Active", "Notes", "InstHeld%"]

def _ensure_instheld_col(ws):
    """Add InstHeld% column header if missing (backwards-compat for v1.0 sheets)."""
    try:
        h = ws.row_values(1)
        if len(h) < 8 or h[7] != "InstHeld%":
            ws.update_cell(1, 8, "InstHeld%")
    except Exception:
        pass

def _seed_watchlist(ws):
    """Populate LTWatchlist with DEFAULT_WATCHLIST. FundScore/FIIChange% will be
    filled on first scan pass below. InstHeld% starts blank (computed later)."""
    rows = [
        [sym, co, sec, "", "0", "TRUE", "", ""]
        for sym, co, sec in DEFAULT_WATCHLIST
    ]
    ws.append_rows(rows)
    print(f"[LT] Seeded {len(rows)} stocks into {LT_WATCHLIST}")

def _load_watchlist(ws):
    """Return list of dicts. Ensures headers are correct."""
    _ensure_instheld_col(ws)
    all_rows = ws.get_all_values()
    if len(all_rows) < 2:
        _seed_watchlist(ws)
        all_rows = ws.get_all_values()
    stocks = []
    for i, r in enumerate(all_rows[1:], start=2):  # row index for update
        while len(r) < 8:
            r.append("")
        sym = r[COL_SYM].strip()
        if not sym:
            continue
        if r[COL_ACTIVE].strip().upper() == "FALSE":
            continue
        stocks.append({
            "sym":       sym,
            "company":   r[COL_COMPANY] or sym,
            "sector":    r[COL_SECTOR]  or "",
            "fund":      r[COL_FUND],       # may be empty — will be auto-filled
            "fii":       r[COL_FII],        # may be empty
            "notes":     r[COL_NOTES],      # v1.4: pre-fetched for batch update (avoids per-row cell read)
            "instheld":  r[COL_INSTHELD],   # previous institutionPercentHeld
            "row_idx":   i,                 # 1-based gspread row index
        })
    return stocks

# ── yfinance data ─────────────────────────────────────────────────────────────
def _ticker(sym):
    return sym.replace("NSE:", "").replace("BSE:", "") + ".NS"

def _rsi(closes, period=14):
    # v1.6 (BUG-3 fix): `gain / loss` was 0/0 = NaN on flat windows. Divide by
    # loss.replace(0, 1e-10) and clamp final NaN to 50.0 (neutral) so signals
    # never see NaN downstream.
    delta = closes.diff()
    gain  = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss  = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs    = gain / loss.replace(0, 1e-10)
    val   = 100 - (100 / (1 + rs.iloc[-1]))
    if val != val:   # NaN guard (NaN != NaN)
        return 50.0
    return round(float(val), 1)

def _calc_fund_score(info):
    """
    Auto-calculate FundScore 1-10 from yfinance financial ratios.
    No manual input needed.
    """
    score = 3.0

    roe = float(info.get("returnOnEquity") or 0)
    if roe >= 0.20:  score += 2.0
    elif roe >= 0.12: score += 1.0

    margin = float(info.get("profitMargins") or 0)
    if margin >= 0.18:  score += 1.5
    elif margin >= 0.08: score += 0.5

    rev_g = float(info.get("revenueGrowth") or 0)
    if rev_g >= 0.15:  score += 1.5
    elif rev_g >= 0.05: score += 0.5

    de = float(info.get("debtToEquity") or 0)
    if 0 <= de <= 20:   score += 1.5
    elif de <= 50:       score += 0.5
    elif de > 150:       score -= 1.0

    mcap = float(info.get("marketCap") or 0) / 1e7  # Crores
    if mcap >= 100000: score += 1.0   # ₹1 lakh Cr+ = largecap
    elif mcap >= 20000: score += 0.5  # ₹20k Cr+ = midcap

    dy = float(info.get("dividendYield") or 0) * 100
    if dy >= 2.0: score += 0.5

    return min(10.0, max(1.0, round(score, 1)))

def fetch_data(sym, prev_instheld_str):
    """Fetch yfinance data. Returns data dict or None on failure.

    v1.4: Decoupled price/52w from .info. Critical price data now comes from
    hist (always available), while .info is best-effort for fundamentals only.
    yfinance .info is heavily throttled and returns null for many Indian-stock
    fields, but hist is reliable. This way FundScore quality may degrade
    silently, but signals always have correct CMP/52W/RSI.
    """
    try:
        t    = yf.Ticker(_ticker(sym))
        hist = t.history(period="1y", interval="1d")
        if hist.empty or len(hist) < 20:
            return None

        # v1.4: price/52w come directly from hist (always available)
        cmp = float(hist["Close"].iloc[-1])
        h52 = float(hist["Close"].max())
        l52 = float(hist["Close"].min())

        # Fundamentals — best-effort via .info (often null for Indian stocks)
        try:
            info = t.info or {}
        except Exception as ie:
            print(f"[FETCH] {sym}: info unavailable ({ie}) — using hist-only data")
            info = {}

        pe   = float(info.get("trailingPE") or info.get("forwardPE") or 0)
        dy   = float(info.get("dividendYield") or 0) * 100
        mcap = float(info.get("marketCap") or 0) / 1e7

        # Auto FundScore — degrades gracefully if .info is empty (returns ~3.0 baseline)
        fund_score = _calc_fund_score(info)

        # Auto FIIChange% — institutionPercentHeld delta
        inst_now = float(info.get("institutionPercentHeld") or
                         info.get("heldPercentInstitutions") or 0) * 100
        try:
            inst_prev = float(prev_instheld_str) if prev_instheld_str else inst_now
        except ValueError:
            inst_prev = inst_now
        fii_change = round(inst_now - inst_prev, 2)

        rsi = _rsi(hist["Close"])

        return {
            "cmp": round(cmp, 2), "h52": round(h52, 2), "l52": round(l52, 2),
            "pe": round(pe, 1),   "div": round(dy, 2),  "mcap": round(mcap, 0),
            "rsi": rsi,
            "fund_score": fund_score,
            "fii_change": fii_change,
            "inst_held":  round(inst_now, 4),  # store for next delta calc
        }
    except Exception as e:
        print(f"[FETCH] {sym}: {e}")
        return None

# ── Signal generation ─────────────────────────────────────────────────────────
def make_signal(data):
    cmp, h52, l52 = data["cmp"], data["h52"], data["l52"]
    rsi, dy = data["rsi"], data["div"]
    fund_score  = data["fund_score"]
    fii_change  = data["fii_change"]

    rng     = h52 - l52
    pos_pct = ((cmp - l52) / rng * 100) if rng > 0 else 50.0

    score   = 0
    reasons = []

    if pos_pct <= 20:
        score += 4; reasons.append(f"Near 52W low ({pos_pct:.0f}%)")
    elif pos_pct <= 35:
        score += 2; reasons.append(f"Attractive zone ({pos_pct:.0f}%)")
    elif pos_pct >= 85:
        score -= 2; reasons.append(f"Near 52W high ({pos_pct:.0f}%)")

    if rsi <= 35:
        score += 3; reasons.append(f"Oversold RSI {rsi:.0f}")
    elif rsi <= 45:
        score += 1; reasons.append(f"RSI {rsi:.0f}")
    elif rsi >= 72:
        score -= 1

    if dy >= 3.0:
        score += 2; reasons.append(f"High div {dy:.1f}%")
    elif dy >= 1.5:
        score += 1; reasons.append(f"Div {dy:.1f}%")

    if fii_change >= 2.0:
        score += 3; reasons.append(f"Institutions buying ↑{fii_change:.1f}%")
    elif fii_change >= 0.5:
        score += 1; reasons.append("Institutions stable")
    elif fii_change <= -2.0:
        score -= 2; reasons.append(f"Institutions selling ↓{abs(fii_change):.1f}%")

    if fund_score >= 9:
        score += 2
    elif fund_score >= 7:
        score += 1

    # v1.6 (BUG-4 fix): BOOK PARTIAL moved BEFORE the score-3 HOLD branch so a
    # stock near 52W high (or RSI overbought) is correctly tagged BOOK PARTIAL
    # instead of being swallowed into HOLD. STRONG BUY/ACCUMULATE still take
    # precedence — high score requires near-52W-low conditions that cannot
    # coexist with near-52W-high status, so no conflict.
    if score >= 9:
        sig   = "STRONG BUY 🟢"
        tgt   = round(max(h52 * 1.05, cmp * 1.30), 2)
        sl    = round(cmp * 0.82, 2)
        entry = f"₹{cmp:.0f}–₹{cmp*1.02:.0f}"
    elif score >= 6:
        sig   = "ACCUMULATE 🟡"
        tgt   = round(max(h52, cmp * 1.22), 2)
        sl    = round(cmp * 0.84, 2)
        entry = f"₹{cmp*0.97:.0f}–₹{cmp*1.01:.0f}"
    elif pos_pct >= 85 or rsi >= 72:
        sig   = "BOOK PARTIAL 🔴"
        tgt   = round(h52, 2)
        sl    = round(cmp * 0.88, 2)
        entry = "—"
    elif score >= 3:
        sig   = "HOLD ⚪"
        tgt   = round(max(h52, cmp * 1.15), 2)
        sl    = round(cmp * 0.85, 2)
        entry = f"₹{cmp:.0f} (existing only)"
    else:
        sig   = "WAIT 🔵"
        tgt   = round(h52 * 0.95, 2)
        sl    = round(l52 * 0.97, 2)
        entry = f"₹{l52:.0f}–₹{cmp*0.95:.0f}"

    upside = round((tgt - cmp) / cmp * 100, 1)
    return sig, tgt, sl, entry, upside, round(pos_pct, 1), score, " | ".join(reasons)


# ── Weekly P&L Performance Report ────────────────────────────────────────────
def _weekly_pnl_report(wb):
    """
    Reads History sheet for last 7 days' closed trades.
    Runs every Sunday before investment picks — shows results to build trust.
    Basic: Hinglish simple summary → drives upgrades.
    Advance+Premium: full breakdown with best/worst trade.
    Zero manual task — runs forever automatically.
    """
    from datetime import date, timedelta
    try:
        hist = wb.worksheet("History")
        rows = hist.get_all_values()[1:]
    except Exception as e:
        print(f"[PNL] History read: {e}"); return

    # v1.5: 8 days (not 7) to capture Friday-edge trades on Sunday morning run
    cutoff = (date.today() - timedelta(days=8)).isoformat()
    wins = 0; losses = 0; total_pnl = 0.0; trades = []

    for r in rows:
        while len(r) < 17: r.append("")
        exit_dt = str(r[3]).strip()
        if not exit_dt or exit_dt < cutoff: continue
        sym = str(r[0]).replace("NSE:", "").strip()
        result = str(r[6]).upper()
        try: pnl_rs = float(str(r[16]).replace(",", ""))
        except: pnl_rs = 0.0
        try: pnl_pct = float(str(r[5]).replace("%", "").strip())
        except: pnl_pct = 0.0
        if "WIN" in result: wins += 1
        elif "LOSS" in result: losses += 1
        total_pnl += pnl_rs
        trades.append((sym, pnl_rs, pnl_pct))

    total = wins + losses
    if total == 0:
        print("[PNL] No closed trades this week — skipping report"); return

    win_rate   = round(wins / total * 100)
    pnl_emoji  = "💰" if total_pnl >= 0 else "📉"
    now_str    = datetime.now(IST).strftime("%d %b %Y")
    trades_s   = sorted(trades, key=lambda x: x[1], reverse=True)
    best       = trades_s[0] if trades_s else None
    worst      = trades_s[-1] if len(trades_s) > 1 and trades_s[-1][1] < 0 else None

    # Basic channel: Hinglish — simple, drives upgrades
    b_lines = [
        f"📊 <b>WEEKLY RESULTS — AI360Trading</b>",
        f"🗓 {now_str} | Paper Trading",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"\n{pnl_emoji} <b>Net P/L: ₹{total_pnl:+,.0f}</b>",
        f"✅ Jeet: {wins}  |  ❌ Haar: {losses}  |  Win Rate: {win_rate}%",
    ]
    if best and best[1] > 0:
        b_lines.append(f"🏆 Best trade: <b>{best[0]}</b> ₹{best[1]:+,.0f}")
    b_lines += [
        f"\n🔒 Poori detail sirf Advance/Premium members ko milti hai",
        f"📈 Upgrade karo ₹499/month → ai360trading.in/membership",
        f"🤖 AI360Trading — Algo Paper Trading",
    ]
    _tg(BASIC, "\n".join(b_lines))

    # Advance + Premium: full English breakdown
    a_lines = [
        f"📊 <b>WEEKLY PERFORMANCE REPORT</b>",
        f"🗓 {now_str} | Paper Trading Results",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"\n{pnl_emoji} <b>Net Realised P/L: ₹{total_pnl:+,.0f}</b>",
        f"Trades: {total}  |  Wins: {wins} ✅  |  Losses: {losses} ❌  |  Win Rate: {win_rate}%",
    ]
    if best:
        a_lines.append(f"🏆 Best: <b>{best[0]}</b> ₹{best[1]:+,.0f} ({best[2]:+.1f}%)")
    if worst:
        a_lines.append(f"📉 Worst: <b>{worst[0]}</b> ₹{worst[1]:+,.0f} ({worst[2]:+.1f}%)")
    a_lines += [
        "\n<i>Paper trading only — educational results, not financial advice</i>",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    _tg_chunked(ADVANCE, a_lines)
    _tg_chunked(PREMIUM, a_lines)
    print(f"[PNL] Week: {wins}W {losses}L ₹{total_pnl:+,.0f}")


# ── Auto-archive ──────────────────────────────────────────────────────────────
ARCHIVE_TAB     = "SignalsArchive"
ARCHIVE_TRIGGER = 600   # archive when main sheet exceeds this many data rows
KEEP_ROWS       = 300   # keep this many latest rows in main sheet after archiving

def _auto_archive_signals(wb, lt_sheet):
    """
    Fully automatic, runs every Sunday inside generate_longterm.py.
    When LongTermSignals exceeds ARCHIVE_TRIGGER rows, moves the oldest
    rows to SignalsArchive tab and keeps only the latest KEEP_ROWS rows.
    No manual task ever — preserves complete history in archive tab forever.
    """
    try:
        all_data = lt_sheet.get_all_values()  # includes header row
        total_data_rows = len(all_data) - 1   # exclude header
        if total_data_rows <= ARCHIVE_TRIGGER:
            print(f"[ARCHIVE] {total_data_rows} rows — no archive needed (threshold {ARCHIVE_TRIGGER})")
            return

        header     = all_data[0]
        data_rows  = all_data[1:]
        keep       = data_rows[-KEEP_ROWS:]    # latest KEEP_ROWS rows
        to_archive = data_rows[:-KEEP_ROWS]    # everything older

        # Get or create archive tab (append-only, never cleared)
        try:
            arc_sheet = wb.worksheet(ARCHIVE_TAB)
        except gspread.WorksheetNotFound:
            arc_sheet = wb.add_worksheet(title=ARCHIVE_TAB, rows=5000, cols=len(header))
            arc_sheet.append_row(header)
            print(f"[ARCHIVE] Created {ARCHIVE_TAB} tab")

        # Append old rows to archive
        arc_sheet.append_rows(to_archive)
        print(f"[ARCHIVE] Moved {len(to_archive)} rows to {ARCHIVE_TAB}")

        # Rewrite main sheet: header + latest KEEP_ROWS rows only
        lt_sheet.clear()
        lt_sheet.append_row(header)
        lt_sheet.append_rows(keep)
        print(f"[ARCHIVE] LongTermSignals trimmed to {len(keep)} rows")

    except Exception as e:
        print(f"[ARCHIVE] {e}")  # never crash main flow on archive failure


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    now   = datetime.now(IST)
    today = now.strftime("%Y-%m-%d")
    print(f"[LT] Long-Term Signals {VERSION} — {today}")

    wb = _connect()

    # ── Weekly P&L report — runs first, before investment picks ─────────────
    # Shows last 7 days trading results to build follower trust + drive upgrades
    _weekly_pnl_report(wb)

    # Ensure LongTermSignals tab exists (append-only history)
    lt_headers = [
        "Date", "Symbol", "Company", "Sector", "Signal",
        "CMP", "Entry Zone", "Target 12m", "SL", "Upside%",
        "Div Yield%", "PE", "RSI", "52W Pos%", "FII Change%",
        "Fund Score", "Score", "Reason", "MarketCap Cr",
    ]
    lt_sheet = _get_or_create(wb, LT_SIGNALS, lt_headers)

    # PositionalLatest tab: public-facing, cleared + rewritten each Sunday
    # Website iframe points here — always shows this week's fresh picks only
    pos_headers = [
        "Stock", "Company", "Sector", "Signal",
        "CMP ₹", "Entry Zone", "Target (12m) ₹", "Upside %",
        "Stop Loss ₹", "Div Yield %", "PE Ratio", "RSI",
        "Why Buy",
    ]
    pos_sheet = _get_or_create(wb, POSITIONAL_LIVE, pos_headers)

    # Load watchlist (auto-seeds if empty)
    try:
        wl_sheet = wb.worksheet(LT_WATCHLIST)
    except gspread.WorksheetNotFound:
        wl_sheet = _get_or_create(wb, LT_WATCHLIST, LT_HEADERS)
    watchlist = _load_watchlist(wl_sheet)
    print(f"[LT] {len(watchlist)} active stocks in {LT_WATCHLIST}")

    # ── Scan each stock ──────────────────────────────────────────────────────
    strong_buys = []
    accumulates = []
    holds       = []
    new_rows    = []
    wl_updates  = []  # (row_idx, fund_score, fii_change, inst_held)

    for stock in watchlist:
        sym = stock["sym"]
        print(f"[LT] {sym}...", end=" ", flush=True)
        data = fetch_data(sym, stock["instheld"])
        if not data:
            print("skip")
            continue

        sig, tgt, sl, entry, upside, pos_pct, score, reason = make_signal(data)
        print(f"{sig} score={score} fund={data['fund_score']} fii={data['fii_change']:+.1f}%")

        # Queue LTWatchlist row update (auto-maintain FundScore + FIIChange%)
        wl_updates.append((
            stock["row_idx"],
            round(data["fund_score"], 1),
            round(data["fii_change"], 2),
            round(data["inst_held"], 4),
        ))

        row = [
            today, sym, stock["company"], stock["sector"], sig,
            data["cmp"], entry, tgt, sl, upside,
            data["div"], data["pe"], data["rsi"], pos_pct,
            data["fii_change"], data["fund_score"], score, reason, data["mcap"],
        ]
        new_rows.append(row)

        t = (stock["company"], sym, data["cmp"], tgt, sl, upside, reason,
             data["div"], data["pe"], data["rsi"], entry)
        if "STRONG BUY" in sig:
            strong_buys.append(t)
        elif "ACCUMULATE" in sig:
            accumulates.append(t)
        elif "HOLD" in sig:
            holds.append(t)

        time.sleep(1.5)

    # ── Auto-update LTWatchlist with fresh FundScore, FIIChange%, InstHeld% ──
    # v1.4: single batch_update call instead of 25 sequential updates + 25 cell reads
    # for the Notes column. Notes are pre-fetched in _load_watchlist now.
    notes_by_row = {s["row_idx"]: s.get("notes", "") for s in watchlist}
    batch_data = []
    for row_idx, fs, fi, ih in wl_updates:
        batch_data.append({
            "range": f"D{row_idx}:H{row_idx}",
            "values": [[round(fs, 1), round(fi, 2), "TRUE",
                        notes_by_row.get(row_idx, ""), round(ih, 4)]],
        })
    if batch_data:
        try:
            wl_sheet.batch_update(batch_data)
            print(f"[LT] LTWatchlist batch-updated {len(batch_data)} rows")
        except Exception as e:
            print(f"[LT] WL batch update: {e}")

    # ── Write signals to LongTermSignals sheet (append history) ─────────────
    if new_rows:
        try:
            lt_sheet.append_rows(new_rows)
            print(f"[LT] Wrote {len(new_rows)} rows → {LT_SIGNALS}")
        except Exception as e:
            print(f"[LT] Sheet write: {e}")

    # ── Auto-archive old LongTermSignals rows (fully automatic, forever) ─────
    # Keeps last 300 rows in main sheet (~3 months of weekly scans).
    # Moves older rows to SignalsArchive tab — preserves all history forever.
    # Triggers when main sheet exceeds 600 rows (~6 months). No manual task ever.
    _auto_archive_signals(wb, lt_sheet)

    # ── Write to PositionalLatest (public website tab) ───────────────────────
    # Clear all rows (keep header row 1) then rewrite with this week's picks only.
    # Website iframe always shows fresh data — no stale history.
    if new_rows:
        try:
            # Sort: STRONG BUY first, then ACCUMULATE, then HOLD, then others
            signal_rank = {"STRONG BUY": 0, "ACCUMULATE": 1, "HOLD": 2, "BOOK": 3, "WAIT": 4}
            def _sig_rank(r):
                sig = str(r[4])  # Signal column in new_rows
                for k, v in signal_rank.items():
                    if k in sig: return v
                return 5
            sorted_rows = sorted(new_rows, key=_sig_rank)

            # Build public rows: reader-friendly columns (no internal scores/dates)
            pub_rows = []
            week_str = now.strftime("Week of %d %b %Y")
            for r in sorted_rows:
                sig_clean = str(r[4]).replace("🟢","").replace("🟡","").replace("⚪","").replace("🔴","").replace("🔵","").strip()
                pub_rows.append([
                    r[1],           # Symbol (NSE:XXXX)
                    r[2],           # Company
                    r[3],           # Sector
                    r[4],           # Signal (with emoji)
                    f"₹{r[5]:,.0f}" if isinstance(r[5], (int,float)) else r[5],   # CMP
                    r[6],           # Entry Zone
                    f"₹{r[7]:,.0f}" if isinstance(r[7], (int,float)) else r[7],   # Target
                    f"{r[9]}%" if r[9] else "",   # Upside%
                    f"₹{r[8]:,.0f}" if isinstance(r[8], (int,float)) else r[8],   # SL
                    f"{r[10]}%",    # Div Yield%
                    r[11],          # PE
                    r[12],          # RSI
                    r[17],          # Reason
                ])

            # Clear data rows (keep header) + rewrite
            last_row = pos_sheet.row_count
            if last_row > 1:
                pos_sheet.delete_rows(2, last_row)
            pos_sheet.append_rows(pub_rows)
            print(f"[LT] PositionalLatest refreshed — {len(pub_rows)} picks ({week_str})")
        except Exception as e:
            print(f"[LT] PositionalLatest write: {e}")

    # ── Telegram: FREE channel — teaser to grow followers ─────────────────────
    date_str = now.strftime("%d %b %Y")
    free_lines = [
        "📊 <b>WEEKLY INVESTMENT PICKS — AI360Trading</b>",
        f"🗓 {date_str} | Long-Term Portfolio",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    if strong_buys:
        free_lines.append("\n🟢 <b>STRONG BUY</b>")
        for co, sym, cmp, *_ in strong_buys[:3]:
            free_lines.append(f"  ✅ <b>{co}</b> ({sym.replace('NSE:','')}) — ₹{cmp:.0f}")
    if accumulates:
        free_lines.append("\n🟡 <b>ACCUMULATE</b>")
        for co, sym, cmp, *_ in accumulates[:3]:
            free_lines.append(f"  🟡 <b>{co}</b> ({sym.replace('NSE:','')}) — ₹{cmp:.0f}")
    if holds:
        free_lines.append("\n⚪ <b>HOLD (existing positions)</b>")
        for co, sym, cmp, *_ in holds[:3]:
            free_lines.append(f"  ⚪ <b>{co}</b> ({sym.replace('NSE:','')}) — ₹{cmp:.0f}")
    total_action = len(strong_buys) + len(accumulates)
    free_lines += [
        "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"🔍 <b>Is week {total_action} stocks mein buy signal hai</b>",
        "🔒 Entry zone, SL, 12-month target, Poori analysis",
        "   → Sirf Advance / Premium members ko milti hai",
        "\n📈 <b>Upgrade karo ₹499/month mein</b>",
        "   ✅ Daily intraday alerts",
        "   ✅ Long-term entry zones + SL",
        "   ✅ Options signals",
        "   📱 ai360trading.in/membership",
        f"\n🤖 AI360Trading {VERSION}",
    ]
    _tg(BASIC, "\n".join(free_lines))

    # ── Telegram: ADVANCE + PREMIUM — full analysis ────────────────────────────
    actionable = strong_buys + accumulates
    if actionable:
        adv_lines = [
            "📊 <b>LONG-TERM SIGNALS — FULL ANALYSIS</b>",
            f"🗓 {date_str} | AI360Trading {VERSION}",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]
        for co, sym, cmp, tgt, sl, up, reason, dy, pe, rsi, entry in actionable[:8]:
            sig_label = "🟢 STRONG BUY" if any(s[1] == sym for s in strong_buys) else "🟡 ACCUMULATE"
            adv_lines += [
                f"\n{sig_label}",
                f"<b>{co}</b> ({sym.replace('NSE:', '')})",
                f"CMP: ₹{cmp:.0f} | Entry: {entry}",
                f"Target (12m): ₹{tgt:.0f} (+{up}%) | SL: ₹{sl:.0f}",
                f"PE: {pe:.1f} | Div: {dy:.1f}% | RSI: {rsi:.0f}",
                f"Why: {reason}",
            ]
        adv_lines += [
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"Strong Buy: {len(strong_buys)} | Accumulate: {len(accumulates)} | Hold: {len(holds)}",
        ]
        _tg_chunked(ADVANCE, adv_lines)
        _tg_chunked(PREMIUM, adv_lines)

    print(f"[LT] Done — {len(strong_buys)} Strong Buy | {len(accumulates)} Accumulate | {len(holds)} Hold")


if __name__ == "__main__":
    main()
