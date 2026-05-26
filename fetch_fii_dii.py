"""
fetch_fii_dii.py — Daily NSE FII / DII Cash market flow tracker — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Runs Mon-Fri at 6:45 PM IST (NSE publishes daily activity by ~6:00 PM).

WHY THIS EXISTS:
  The Nifty200 sheet's "FII_*" columns are NOT real FII data — they are
  technical strength indicators with misleading FII labels (formulas compute
  from SMA + 52W position + volume; no institutional flow input).

  This script adds REAL Foreign Institutional Investor (FII) and Domestic
  Institutional Investor (DII) market-level data, fetched directly from
  NSE's free public API. Stored in BotMemory under MKT_* prefix to avoid
  collision with existing FII_* technical signals.

DATA SOURCE:
  https://www.nseindia.com/api/fiidiiTradeReact  (NSE official, free)
  Fallback: moneycontrol.com scrape (planned — not yet implemented)

BOTMEMORY KEYS WRITTEN:
  MKT_FII_CASH_NET_<YYYY-MM-DD>  — today's FII Cash net (₹ Cr; + = buying, - = selling)
  MKT_DII_CASH_NET_<YYYY-MM-DD>  — today's DII Cash net
  MKT_FII_BUY_<YYYY-MM-DD>       — today's FII Cash gross buy value
  MKT_FII_SELL_<YYYY-MM-DD>      — today's FII Cash gross sell value
  MKT_DII_BUY_<YYYY-MM-DD>       — today's DII gross buy
  MKT_DII_SELL_<YYYY-MM-DD>      — today's DII gross sell
  MKT_FII_TREND_5D               — rolling 5-day sum of FII net (₹ Cr)
  MKT_FII_REGIME                 — text: "BUYING" / "SELLING" / "NEUTRAL"

TELEGRAM OUTPUT:
  - Basic channel: short Hinglish summary (FII +1,234 Cr buying signal)
  - Advance + Premium: full breakdown (cash flow + 5-day trend + interpretation)

ROADMAP (Phase 2):
  - F&O FII data: index futures position, options call/put bought
  - Stock-level FII (paid service required; deferred)
  - Integration into AppScript scanner as second-layer entry filter
"""

import os, sys, json, time
import requests
from datetime import datetime, timedelta
from typing import Optional
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz

IST          = pytz.timezone("Asia/Kolkata")
VERSION      = "v1.0"
SHEET_NAME   = "Ai360tradingAlgo"
BM_TAB       = "BotMemory"
TREND_DAYS   = 5      # rolling window for MKT_FII_TREND_5D

NSE_API_URL  = "https://www.nseindia.com/api/fiidiiTradeReact"
NSE_HOME     = "https://www.nseindia.com"

# ── Telegram ──────────────────────────────────────────────────────────────────
BOT_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_BASIC  = os.environ.get("CHAT_ID_BASIC", "")
CHAT_ADV    = os.environ.get("CHAT_ID_ADVANCE", "")
CHAT_PREM   = os.environ.get("CHAT_ID_PREMIUM", "")


def _tg(chat_id: str, msg: str):
    if not chat_id or not BOT_TOKEN:
        return
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
            timeout=12,
        )
        if not r.ok:
            print(f"[TG] {chat_id[-4:]}: {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"[TG] {chat_id[-4:]}: {e}")
    time.sleep(0.5)


# ── Google Sheets ─────────────────────────────────────────────────────────────
def _connect():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        try:
            with open("service_account.json") as f:
                raw = f.read().strip()
        except FileNotFoundError:
            raise SystemExit("[CREDS] GCP_SERVICE_ACCOUNT_JSON env var not set "
                             "and service_account.json not found locally")
    try:
        creds_dict = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"[CREDS] Failed to parse GCP credentials JSON: {e}")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    gc    = gspread.authorize(creds)
    return gc.open(SHEET_NAME)


def _bm_set(bm_sheet, key: str, value, ktype: str = "MARKET"):
    """Write or update key in BotMemory sheet."""
    now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    val_str = str(value)
    try:
        data = bm_sheet.get_all_values()
        for i, row in enumerate(data[1:], start=2):
            if row and row[0].strip() == key:
                bm_sheet.update(f"A{i}:E{i}", [[key, val_str, now_str, "", ktype]])
                return
        bm_sheet.append_row([key, val_str, now_str, "", ktype])
    except Exception as e:
        print(f"[BM] set {key}: {e}")


def _bm_get(bm_sheet, key: str) -> Optional[str]:
    try:
        data = bm_sheet.get_all_values()
        for row in data[1:]:
            if row and row[0].strip() == key:
                return row[1].strip() if len(row) > 1 else ""
    except Exception:
        pass
    return None


# ── NSE fetch ─────────────────────────────────────────────────────────────────
def fetch_fii_dii() -> Optional[dict]:
    """
    Fetch FII/DII cash market data from NSE.
    Returns dict with keys: fii_buy, fii_sell, fii_net, dii_buy, dii_sell,
    dii_net, date — all values in ₹ Crores. None on failure.

    NSE blocks requests without proper session cookies — must hit homepage first.
    """
    try:
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept":          "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer":         "https://www.nseindia.com/reports/fii-dii",
        }

        # Step 1: hit homepage to get session cookie
        session.get(NSE_HOME, headers=headers, timeout=10)
        time.sleep(1)

        # Step 2: hit FII/DII API
        r = session.get(NSE_API_URL, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"[NSE] API returned {r.status_code}")
            return None

        data = r.json()
        # API returns array of dicts — one per category
        # Categories may be "FII/FPI **", "DII **" or similar variations
        result = {
            "fii_buy": 0.0, "fii_sell": 0.0, "fii_net": 0.0,
            "dii_buy": 0.0, "dii_sell": 0.0, "dii_net": 0.0,
            "date": "",
        }

        for entry in data:
            cat = (entry.get("category") or "").upper()
            buy = float(entry.get("buyValue") or 0)
            sell = float(entry.get("sellValue") or 0)
            net = float(entry.get("netValue") or (buy - sell))
            date = entry.get("date", "")
            if not result["date"] and date:
                result["date"] = date

            if "FII" in cat or "FPI" in cat:
                result["fii_buy"]  = buy
                result["fii_sell"] = sell
                result["fii_net"]  = net
            elif "DII" in cat:
                result["dii_buy"]  = buy
                result["dii_sell"] = sell
                result["dii_net"]  = net

        if result["fii_buy"] == 0 and result["dii_buy"] == 0:
            print(f"[NSE] Got response but no FII/DII rows parsed. Raw: {str(data)[:200]}")
            return None

        return result

    except Exception as e:
        print(f"[NSE] Fetch error: {e}")
        return None


# ── Trend calculation ─────────────────────────────────────────────────────────
def calc_5d_trend(bm_sheet, today_net: float, today_str: str) -> float:
    """
    Sum FII net over last 5 trading days including today.
    Reads MKT_FII_CASH_NET_* keys from BotMemory.
    """
    total = today_net
    days_included = 1
    cutoff = (datetime.strptime(today_str, "%Y-%m-%d").date() - timedelta(days=10)).isoformat()

    try:
        data = bm_sheet.get_all_values()
        for row in data[1:]:
            if not row or not row[0]:
                continue
            key = row[0].strip()
            if not key.startswith("MKT_FII_CASH_NET_"):
                continue
            date_part = key.replace("MKT_FII_CASH_NET_", "")
            if date_part == today_str:    # don't double-count today
                continue
            if date_part < cutoff:        # too old
                continue
            try:
                total += float(row[1])
                days_included += 1
                if days_included >= TREND_DAYS:
                    break
            except (ValueError, IndexError):
                pass
    except Exception as e:
        print(f"[TREND] read error: {e}")

    return round(total, 1)


def classify_regime(trend_5d: float) -> str:
    """Convert 5-day FII net into regime label."""
    if trend_5d >= 5000:    return "STRONG BUYING"
    if trend_5d >=  1500:   return "BUYING"
    if trend_5d >= -1500:   return "NEUTRAL"
    if trend_5d >= -5000:   return "SELLING"
    return "STRONG SELLING"


# ── Telegram messages ─────────────────────────────────────────────────────────
def fmt_cr(val: float) -> str:
    """Format a Crore value with sign and thousands separator."""
    return f"₹{val:+,.0f} Cr"


def build_basic_msg(d: dict, trend: float, regime: str) -> str:
    fii_emoji = "🟢" if d["fii_net"] >= 0 else "🔴"
    dii_emoji = "🟢" if d["dii_net"] >= 0 else "🔴"

    regime_emoji = {
        "STRONG BUYING":   "🚀",
        "BUYING":          "📈",
        "NEUTRAL":         "⚖️",
        "SELLING":         "📉",
        "STRONG SELLING":  "⛔",
    }.get(regime, "ℹ️")

    return (
        f"💼 <b>FII / DII REPORT — {d['date']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{fii_emoji} <b>FII Cash:</b> {fmt_cr(d['fii_net'])}\n"
        f"{dii_emoji} <b>DII Cash:</b> {fmt_cr(d['dii_net'])}\n\n"
        f"{regime_emoji} <b>5-day FII Trend: {regime}</b>\n"
        f"   ({fmt_cr(trend)} net over last {TREND_DAYS} sessions)\n\n"
        f"<i>Source: NSE Official Data</i>\n"
        f"📈 Full analysis → Advance/Premium\n"
        f"🌐 ai360trading.in/membership"
    )


def build_advance_msg(d: dict, trend: float, regime: str) -> str:
    fii_arrow = "↑" if d["fii_net"] >= 0 else "↓"
    dii_arrow = "↑" if d["dii_net"] >= 0 else "↓"

    # Interpretation logic
    interp = []
    if d["fii_net"] > 0 and d["dii_net"] > 0:
        interp.append("Both FII and DII buying — strong bullish day, broad institutional interest.")
    elif d["fii_net"] < 0 and d["dii_net"] < 0:
        interp.append("Both FII and DII selling — distribution day, raise caution on new entries.")
    elif d["fii_net"] > 0 and d["dii_net"] < 0:
        interp.append("FII buying / DII profit-booking — foreign-led rally, watch for sector rotation.")
    elif d["fii_net"] < 0 and d["dii_net"] > 0:
        interp.append("FII selling / DII absorbing — typical correction phase, DII often defends levels.")
    else:
        interp.append("Flat day — wait for clearer institutional direction.")

    if regime in ("STRONG SELLING", "SELLING"):
        interp.append("⚠️ Multi-day FII selling — favor cash + tight stops + Sector Leaders only.")
    elif regime in ("STRONG BUYING", "BUYING"):
        interp.append("✅ Multi-day FII buying — risk-on environment, breakout setups have better odds.")

    return (
        f"💼 <b>FII / DII FLOW REPORT — {d['date']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>FII Cash Market</b>\n"
        f"   Buy:   {fmt_cr(d['fii_buy'])}\n"
        f"   Sell:  {fmt_cr(d['fii_sell'])}\n"
        f"   Net:   {fmt_cr(d['fii_net'])} {fii_arrow}\n\n"
        f"<b>DII Cash Market</b>\n"
        f"   Buy:   {fmt_cr(d['dii_buy'])}\n"
        f"   Sell:  {fmt_cr(d['dii_sell'])}\n"
        f"   Net:   {fmt_cr(d['dii_net'])} {dii_arrow}\n\n"
        f"<b>5-Day FII Trend:</b> {regime}\n"
        f"   Rolling sum: {fmt_cr(trend)}\n\n"
        f"<b>Interpretation:</b>\n• " + "\n• ".join(interp) + "\n\n"
        f"<i>Source: NSE official daily report.\n"
        f"AI360Trading {VERSION} — fully automated, ₹0/month.</i>"
    )


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    now       = datetime.now(IST)
    today_str = now.strftime("%Y-%m-%d")

    print(f"[FII] AI360Trading FII/DII Fetcher {VERSION} — {now.strftime('%Y-%m-%d %H:%M IST')}")

    # Skip weekends defensively (workflow cron already handles, but belt-and-braces)
    if now.weekday() >= 5:
        print(f"[FII] Weekend ({now.strftime('%A')}) — skip")
        return

    # Fetch from NSE
    data = fetch_fii_dii()
    if not data:
        print("[FII] No data fetched — exiting (likely NSE rate-limit or holiday)")
        return

    print(f"[FII] FII net: {fmt_cr(data['fii_net'])} | DII net: {fmt_cr(data['dii_net'])}")

    # Connect to Sheet
    try:
        wb = _connect()
        bm = wb.worksheet(BM_TAB)
    except Exception as e:
        print(f"[FII] Sheet connect failed: {e}")
        return

    # Write today's values
    _bm_set(bm, f"MKT_FII_CASH_NET_{today_str}",  data["fii_net"])
    _bm_set(bm, f"MKT_DII_CASH_NET_{today_str}",  data["dii_net"])
    _bm_set(bm, f"MKT_FII_BUY_{today_str}",       data["fii_buy"])
    _bm_set(bm, f"MKT_FII_SELL_{today_str}",      data["fii_sell"])
    _bm_set(bm, f"MKT_DII_BUY_{today_str}",       data["dii_buy"])
    _bm_set(bm, f"MKT_DII_SELL_{today_str}",      data["dii_sell"])

    # Calculate 5-day trend (after writing today so calc_5d_trend can exclude today)
    trend  = calc_5d_trend(bm, data["fii_net"], today_str)
    regime = classify_regime(trend)

    _bm_set(bm, "MKT_FII_TREND_5D", trend)
    _bm_set(bm, "MKT_FII_REGIME",   regime)

    print(f"[FII] 5d trend: {fmt_cr(trend)} → regime: {regime}")

    # Send Telegram alerts
    basic_msg   = build_basic_msg(data, trend, regime)
    advance_msg = build_advance_msg(data, trend, regime)

    _tg(CHAT_BASIC,  basic_msg)
    _tg(CHAT_ADV,    advance_msg)
    _tg(CHAT_PREM,   advance_msg)

    print(f"[FII] Done. Regime={regime} | Trend={fmt_cr(trend)}")


if __name__ == "__main__":
    main()
