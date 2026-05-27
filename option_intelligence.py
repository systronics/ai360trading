"""
AI360 OPTION INTELLIGENCE — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pure-Python option strike + risk module for Indian equity options.
Used by trading_bot.py to upgrade the scanner's option signal with:
  • ITM strike recommendation (~0.7 delta — moves 70% with stock, low theta)
  • IV-regime gate (via 20-day historical volatility from yfinance — IV proxy)
  • Earnings-window block (reads NSE earnings cache in BotMemory)
  • Stock-anchored exit (exit option when underlying −1.5%, NOT option −40%)
  • PE side for bearish regime (was: skip everything in bearish — left money on table)

Design constraints (per feedback_free_forever_self_repair memory):
  1. ₹0/month forever. Only free sources (yfinance + NSE official + BotMemory).
  2. Self-repair: every external call wrapped, fails open (returns permissive
     default on error). One slow yfinance call cannot stall a tick.
  3. No hardcoded year-locked logic. Strike step computed from price; expiry
     read from upstream (AppScript already computes last-Tuesday dynamically).
  4. Caching: HV results cached in-process (module-level dict) for the run.
     BotMemory is the cross-run persistence layer (used by fetch_earnings.py).
"""

import os
from datetime import datetime, timedelta

# In-process cache — saves repeated yfinance calls within the same tick when
# multiple stocks need IV checks. Cleared naturally when the process exits.
_HV_CACHE = {}


# ════════════════════════════════════════════════════════════════════════════
# STRIKE STEP TABLE — NSE standard intervals per price band
# ════════════════════════════════════════════════════════════════════════════

def strike_step(price: float) -> int:
    """
    NSE option strike interval is price-dependent. Pure math — no API.
    Bands match exchange spec; if NSE changes intervals this function is
    the single update point.
    """
    if price < 100:    return 1
    if price < 250:    return 2
    if price < 500:    return 5
    if price < 1000:   return 10
    if price < 2000:   return 20
    if price < 5000:   return 50
    return 100


def round_to_step(price: float, step: int) -> int:
    return int(round(price / step) * step)


# ════════════════════════════════════════════════════════════════════════════
# STRIKE RECOMMENDATION — ITM vs ATM vs OTM
# ════════════════════════════════════════════════════════════════════════════
# Delta approximation by moneyness (no Black-Scholes — empirical for ~30d expiry):
#   2 strikes ITM  → delta ~0.75 (sweet spot for swing trades)
#   1 strike ITM   → delta ~0.65
#   ATM            → delta ~0.50
#   1 strike OTM   → delta ~0.35
#   2 strikes OTM  → delta ~0.20 (theta bleed, retail trap)
#
# Top traders' rule: trend trades = ITM (0.6–0.8 delta) so option moves like
# the stock, theta is small, time decay survivable. OTM only on confirmed
# breakouts with explosive volume.

def compute_itm_strike(cp: float, direction: str = "CE", depth: int = 2) -> int:
    """
    Returns the strike `depth` steps in-the-money relative to current price.

    For CE (call) at ₹3155 with depth=2, step=50 → strike = 3050 (2 strikes ITM).
    For PE (put) at ₹3155 with depth=2, step=50 → strike = 3250 (2 strikes ITM).
    """
    step = strike_step(cp)
    atm  = round_to_step(cp, step)
    if direction.upper().startswith("C"):
        return atm - (depth * step)
    return atm + (depth * step)


def compute_otm_strike(cp: float, direction: str = "CE", depth: int = 1) -> int:
    step = strike_step(cp)
    atm  = round_to_step(cp, step)
    if direction.upper().startswith("C"):
        return atm + (depth * step)
    return atm - (depth * step)


def compute_atm_strike(cp: float) -> int:
    return round_to_step(cp, strike_step(cp))


# ════════════════════════════════════════════════════════════════════════════
# HISTORICAL VOLATILITY — IV proxy via yfinance
# ════════════════════════════════════════════════════════════════════════════
# Why HV not IV: NSE option chain IV requires authenticated session + cookie
# dance that breaks every few months when NSE rotates protection. HV is
# computable from public OHLC data and is highly correlated with IV regime
# (when IV is high, HV is also high — both reflect realised + expected volatility).

def get_historical_volatility(symbol: str, days: int = 20) -> float:
    """
    Annualised HV via close-to-close log returns. Returns 0.0 on any failure
    (caller treats 0 as "unavailable" and allows entry — fail-open).
    Cached for the duration of one tick to avoid duplicate yfinance hits.
    """
    cache_key = f"{symbol}:{days}"
    if cache_key in _HV_CACHE:
        return _HV_CACHE[cache_key]
    try:
        import yfinance as yf
        import math
        yf_sym = symbol.replace("NSE:", "").strip() + ".NS"
        df     = yf.Ticker(yf_sym).history(period=f"{days+10}d", interval="1d")
        if df.empty or len(df) < days + 1:
            _HV_CACHE[cache_key] = 0.0
            return 0.0
        closes = df["Close"].iloc[-(days + 1):].tolist()
        log_returns = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
        mean = sum(log_returns) / len(log_returns)
        var  = sum((r - mean) ** 2 for r in log_returns) / max(1, len(log_returns) - 1)
        hv_annual = math.sqrt(var) * math.sqrt(252) * 100  # % annualised
        hv = round(hv_annual, 1)
        _HV_CACHE[cache_key] = hv
        return hv
    except Exception as e:
        print(f"[HV] {symbol}: {e}")
        _HV_CACHE[cache_key] = 0.0
        return 0.0


def check_iv_regime(symbol: str) -> tuple:
    """
    Returns (allowed, hv_pct, label).

    Heuristic regime classification using HV-20:
       < 20%  → calm     → CE/PE both fine (cheap premium)
       20-35% → normal   → standard pick
       35-55% → elevated → prefer ITM (defends against IV crush)
       > 55%  → extreme  → block new CE/PE buying (premium too rich)

    Fail-open: hv=0 (fetch failed) → "data unavailable, entry allowed".
    """
    hv = get_historical_volatility(symbol)
    if hv <= 0:
        return True, 0.0, "HV unavailable — entry allowed"
    if hv < 20:    return True,  hv, f"HV {hv:.0f}% — calm regime ✅"
    if hv < 35:    return True,  hv, f"HV {hv:.0f}% — normal regime ✅"
    if hv < 55:    return True,  hv, f"HV {hv:.0f}% — elevated (prefer ITM)"
    return False, hv, f"HV {hv:.0f}% — extreme (skip option buying)"


# ════════════════════════════════════════════════════════════════════════════
# EARNINGS BLOCK — reads BotMemory cache populated by fetch_earnings.py
# ════════════════════════════════════════════════════════════════════════════

def check_earnings_window(symbol: str, mem: str, now: datetime, days: int = 3) -> tuple:
    """
    Returns (allowed, reason). Blocks if earnings announcement falls within
    `days` trading days of now (default 3).
    Memory key format: EARNINGS_{SYMBOL_NO_NSE}_{YYYY-MM-DD} = "FY2026Q4" or similar.
    Fail-open: no matching keys → allowed (assumes no earnings nearby).
    """
    if not mem:
        return True, "Earnings cache empty — entry allowed"
    sym_clean = symbol.replace("NSE:", "").strip().upper()
    horizon   = [(now + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(-1, days + 1)]
    prefix    = f"EARNINGS_{sym_clean}_"
    for piece in mem.split(","):
        piece = piece.strip()
        if not piece.startswith(prefix):
            continue
        # Extract date portion: "EARNINGS_TCS_2026-05-30=Q4FY26"
        head = piece.split("=", 1)[0]
        date_part = head[len(prefix):]
        if date_part in horizon:
            return False, f"Earnings on {date_part} (within {days}d) — skip CE/PE"
    return True, f"No earnings within {days}d — entry allowed ✅"


# ════════════════════════════════════════════════════════════════════════════
# COMBINED RECOMMENDATION
# ════════════════════════════════════════════════════════════════════════════

def recommend_option(symbol: str, cp: float, atr: float, stage: str,
                     is_bullish: bool, mem: str, now: datetime) -> dict:
    """
    Single entry point for trading_bot.py. Returns a dict with:
      action     : 'BUY_CE' | 'BUY_PE' | 'SKIP'
      strike     : int (e.g. 3050) | None if SKIP
      strike_label: "ITM-2" / "ITM-1" / "ATM" / "OTM-1"
      delta_est  : 0.20 to 0.80
      hv         : 0.0 if unavailable else annualised %
      reasons    : list of human-readable check results
      sl_pct     : recommended stock-anchored stop loss % (e.g. 1.5)
      tgt_pct    : recommended target on option premium %
    """
    reasons = []

    # 1. Direction: bullish ⇒ CE, bearish ⇒ PE. (was: bearish always skip)
    direction = "CE" if is_bullish else "PE"

    # 2. IV / HV regime check
    iv_ok, hv, iv_msg = check_iv_regime(symbol)
    reasons.append(f"[IV] {iv_msg}")
    if not iv_ok:
        return {"action": "SKIP", "strike": None, "strike_label": "",
                "delta_est": 0, "hv": hv, "reasons": reasons,
                "sl_pct": 0, "tgt_pct": 0}

    # 3. Earnings window
    earn_ok, earn_msg = check_earnings_window(symbol, mem, now)
    reasons.append(f"[EARN] {earn_msg}")
    if not earn_ok:
        return {"action": "SKIP", "strike": None, "strike_label": "",
                "delta_est": 0, "hv": hv, "reasons": reasons,
                "sl_pct": 0, "tgt_pct": 0}

    # 4. Strike depth selection:
    #    - High HV (35-55) → 2 strikes ITM (delta 0.75) — IV crush protection
    #    - Confirmed breakout → 1 strike ITM (delta 0.65) — better leverage
    #    - Anything else     → 2 strikes ITM (safe default)
    if hv > 0 and hv >= 35:
        depth, label, delta = 2, "ITM-2", 0.75
    elif "CONFIRMED" in stage.upper():
        depth, label, delta = 1, "ITM-1", 0.65
    else:
        depth, label, delta = 2, "ITM-2", 0.75

    strike = compute_itm_strike(cp, direction, depth)

    # 5. Stock-anchored SL/Target. Option premium reacts ~delta to stock move.
    #    Stock −1.5% × delta 0.7 ≈ option premium −15% (much earlier exit than
    #    the old "wait for option −40%" rule). Target: stock +3% to +5%.
    sl_pct  = 1.5
    tgt_pct = 50.0  # on premium — equates to roughly +5% stock move at delta 0.7

    return {
        "action": f"BUY_{direction}",
        "strike": strike,
        "strike_label": label,
        "delta_est": delta,
        "hv": hv,
        "reasons": reasons,
        "sl_pct": sl_pct,
        "tgt_pct": tgt_pct,
    }


# ════════════════════════════════════════════════════════════════════════════
# FORMATTER — used by trading_bot.ce_candidate_flag
# ════════════════════════════════════════════════════════════════════════════

def format_option_alert(symbol: str, cp: float, rec: dict, scanner_strike: str = "",
                        scanner_expiry: str = "", scanner_theta: str = "") -> str:
    """Build the option block appended to TRADE ENTRY alerts."""
    if rec["action"] == "SKIP":
        return (
            f"\n\n📊 <b>OPTIONS — SKIP THIS TRADE</b>\n"
            + "\n".join(f"   {r}" for r in rec["reasons"])
            + "\n   <i>Equity-only entry; revisit options when regime clears.</i>"
        )

    side    = "Call" if rec["action"] == "BUY_CE" else "Put"
    arrow   = "📈" if rec["action"] == "BUY_CE" else "📉"
    side_sm = rec["action"].split("_")[1]   # CE or PE
    scanner_note = ""
    if scanner_strike:
        scanner_note = (
            f"\n   <i>Scanner suggested: {scanner_strike} (kept in sheet for record).</i>"
        )

    return (
        f"\n\n{arrow} <b>SMART {side.upper()} SIGNAL</b>\n"
        f"   🎯 Buy: <b>{rec['strike']} {side_sm}</b>  ({rec['strike_label']}, Δ≈{rec['delta_est']})\n"
        f"   📅 Expiry: {scanner_expiry or 'current monthly'}"
        f"{scanner_note}\n"
        f"   📊 HV-20: {rec['hv']:.0f}%  |  Theta: {scanner_theta or 'see sheet'}\n"
        f"   ⚡ Entry: 9:30-9:45 AM after stock triggers\n"
        f"   🛑 SL: stock −{rec['sl_pct']}% (premium ≈ −{int(rec['sl_pct']*rec['delta_est']*10)}%)\n"
        f"   🎯 Target: option premium +{rec['tgt_pct']:.0f}% (≈ stock +5%)\n"
        + "\n".join(f"   {r}" for r in rec["reasons"])
        + "\n   <i>ITM strike = lower theta + better delta. Buy below your premium budget only.</i>"
    )
