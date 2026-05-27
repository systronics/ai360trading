"""
AI360 INSTITUTIONAL EDGES — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Five "smart money" filters that consistently-profitable traders + FIIs use
to confirm a setup. Each is a stand-alone check; trading_bot.py composes
them in check_all_entry_filters() to gate WAITING → TRADED promotion.

  1. RELATIVE STRENGTH  — stock outperforming Nifty intraday (RS = stk% - nifty%)
  2. VOLUME CONFIRMATION — today's relative volume > 1.5× (institutional footprint)
  3. FII REGIME GATE    — block longs when FII net selling > ₹2000 Cr
  4. PCR REGIME GATE    — Put-Call Ratio extremes flagged
  5. DELIVERY %         — > 40% indicates institutional accumulation (vs jobbing)

Design (per feedback_free_forever_self_repair memory):
  • Each check returns (allowed: bool, reason: str). Fail-open on any error.
  • Data sources: Nifty200 sheet (already populated), BotMemory MKT_* /
    DLV_* / PCR_* keys (populated by fetch_fii_dii.py and fetch_bhavcopy.py).
  • Module load wrapped in trading_bot's try/except — bot survives if this
    file is broken or missing. No hard dependencies beyond stdlib.

Tunables (top of file — edit and next cron picks them up):
"""

# ────────────────────────────────────────────────────────────────────────────
# THRESHOLDS — tweakable knobs
# ────────────────────────────────────────────────────────────────────────────

RS_MIN_PCT             = 1.0    # stock must beat Nifty by ≥ this % intraday
VOL_MULTIPLE_MIN       = 1.5    # today's volume / 20D-avg must be ≥ this
FII_NET_SELL_BLOCK_CR  = -2000  # block new longs if FII cash net < this (₹ Cr)
FII_NET_BUY_BLOCK_CR   = 2000   # block new shorts if FII cash net > this (₹ Cr)
PCR_BULLISH_MAX        = 1.4    # PCR > this = bearish bias, soft-warn
PCR_BEARISH_MIN        = 0.6    # PCR < this = bullish bias, soft-warn
DELIVERY_MIN_PCT       = 40.0   # delivery % minimum (institutional vs jobbing)


# ════════════════════════════════════════════════════════════════════════════
# 1. RELATIVE STRENGTH — stock vs Nifty intraday
# ════════════════════════════════════════════════════════════════════════════

def check_relative_strength(sym: str, cp: float, prev_close: float, nifty_pct: float,
                            min_rs: float = RS_MIN_PCT) -> tuple:
    """
    RS = stock_pct − nifty_pct.  Long entries require RS > min_rs.

    prev_close comes from BotMemory `{key}_LP_` (set each tick by trading_bot
    in step_b). On the very first entry tick for a symbol prev_close may be 0
    → fails open (entry allowed).
    """
    if prev_close <= 0 or cp <= 0:
        return True, "RS unavailable — entry allowed"
    stock_pct = ((cp - prev_close) / prev_close) * 100
    rs = stock_pct - nifty_pct
    if rs < min_rs:
        return False, f"RS {rs:+.2f}% < {min_rs:.1f}% (stock {stock_pct:+.2f}%, Nifty {nifty_pct:+.2f}%) — no leadership"
    return True, f"RS {rs:+.2f}% (stock {stock_pct:+.2f}% > Nifty {nifty_pct:+.2f}%) ✅"


# ════════════════════════════════════════════════════════════════════════════
# 2. VOLUME CONFIRMATION — relative volume from Nifty200 sheet
# ════════════════════════════════════════════════════════════════════════════
# The Nifty200 sheet's volume column holds the current relative-volume value
# already (AppScript scanner computes today_vol / avg_20d_vol on each row).
# Index varies between sheets — caller passes the parsed value to keep this
# module sheet-agnostic. trading_bot.py owns the column-index detail.

def check_volume_confirmation(sym: str, rel_vol: float, min_mult: float = VOL_MULTIPLE_MIN) -> tuple:
    """
    rel_vol = today's volume / 20-day average volume.  Entry requires ≥ 1.5×.
    Fail-open if rel_vol is 0 (means the data wasn't available at scan time).
    """
    if rel_vol <= 0:
        return True, "Volume data unavailable — entry allowed"
    if rel_vol < min_mult:
        return False, f"Volume {rel_vol:.2f}× < {min_mult}× — no institutional footprint"
    label = "huge" if rel_vol >= 3.0 else ("strong" if rel_vol >= 2.0 else "above avg")
    return True, f"Volume {rel_vol:.2f}× — {label} ✅"


# ════════════════════════════════════════════════════════════════════════════
# 3. FII REGIME GATE — uses keys from fetch_fii_dii.py
# ════════════════════════════════════════════════════════════════════════════
# Keys (set by fetch_fii_dii.py daily at 6:45 PM IST):
#   MKT_FII_CASH_NET_<date>  — today's FII cash net (₹ Cr; + buy, - sell)
#   MKT_FII_TREND_5D         — rolling 5-day sum of net (₹ Cr)
#   MKT_FII_REGIME           — text BUYING / SELLING / NEUTRAL

def check_fii_regime(bm_data: dict, is_bullish: bool, now=None,
                     sell_block_cr: float = FII_NET_SELL_BLOCK_CR,
                     buy_block_cr:  float = FII_NET_BUY_BLOCK_CR) -> tuple:
    """
    For LONG entries:  block if today's FII net < sell_block_cr  (heavy selling).
    For SHORT entries: block if today's FII net > buy_block_cr   (heavy buying).
    Falls open if MKT_FII keys absent (first day, fetch failed, etc.).
    """
    if not bm_data:
        return True, "BotMemory unavailable — entry allowed"
    # Find today's net (or most recent)
    fii_net = None
    today_str = now.strftime("%Y-%m-%d") if now is not None else ""
    if today_str:
        key = f"MKT_FII_CASH_NET_{today_str}"
        if key in bm_data:
            fii_net = _to_float(bm_data[key])
    if fii_net is None:
        # walk recent dates backward by inspecting all keys
        latest_date, latest_val = "", None
        for k, v in bm_data.items():
            if k.startswith("MKT_FII_CASH_NET_"):
                d = k.replace("MKT_FII_CASH_NET_", "")
                if d > latest_date:
                    latest_date, latest_val = d, _to_float(v)
        fii_net = latest_val
    regime = bm_data.get("MKT_FII_REGIME", "").strip().upper()
    trend  = _to_float(bm_data.get("MKT_FII_TREND_5D", "0"))

    if fii_net is None:
        return True, f"FII data unavailable (regime={regime or '?'}) — entry allowed"

    if is_bullish:
        if fii_net <= sell_block_cr:
            return False, f"FII net ₹{fii_net:+,.0f} Cr ≤ ₹{sell_block_cr:,.0f} — heavy FII selling, skip longs"
        msg = f"FII net ₹{fii_net:+,.0f} Cr"
        if regime:    msg += f" | regime: {regime}"
        if trend:     msg += f" | 5d trend ₹{trend:+,.0f} Cr"
        return True, msg + " ✅"
    else:
        if fii_net >= buy_block_cr:
            return False, f"FII net ₹{fii_net:+,.0f} Cr ≥ ₹{buy_block_cr:,.0f} — heavy FII buying, skip shorts"
        return True, f"FII net ₹{fii_net:+,.0f} Cr (regime: {regime or 'unknown'}) ✅"


# ════════════════════════════════════════════════════════════════════════════
# 4. PCR REGIME — Put-Call Ratio extremes
# ════════════════════════════════════════════════════════════════════════════
# Populated by fetch_bhavcopy.py daily at 8 PM IST as MKT_PCR_NIFTY.
# Range guidance:
#   < 0.6  — extreme call-buying  → market often topping, risk for new longs
#   0.7-1.2 — normal
#   > 1.4  — extreme put-buying   → market often bottoming, risk for new shorts

def check_pcr_regime(bm_data: dict, is_bullish: bool,
                     bullish_max: float = PCR_BULLISH_MAX,
                     bearish_min: float = PCR_BEARISH_MIN) -> tuple:
    """Soft filter — does NOT block; returns a (True, reason) with context.
    Treated as informational because PCR extremes are contrarian indicators,
    not absolute blocks. trading_bot.py logs the reason and continues."""
    if not bm_data:
        return True, "PCR unavailable — entry allowed"
    pcr_str = bm_data.get("MKT_PCR_NIFTY", "")
    if not pcr_str:
        return True, "MKT_PCR_NIFTY not yet cached — entry allowed"
    pcr = _to_float(pcr_str)
    if pcr <= 0:
        return True, "PCR malformed — entry allowed"
    if is_bullish and pcr > bullish_max:
        return True, f"PCR {pcr:.2f} > {bullish_max} (heavy put-buying — contrarian bullish, but caution)"
    if not is_bullish and pcr < bearish_min:
        return True, f"PCR {pcr:.2f} < {bearish_min} (heavy call-buying — contrarian bearish, but caution)"
    return True, f"PCR {pcr:.2f} — neutral ✅"


# ════════════════════════════════════════════════════════════════════════════
# 5. DELIVERY % — institutional accumulation vs day-jobbing
# ════════════════════════════════════════════════════════════════════════════
# Populated by fetch_bhavcopy.py daily at 8 PM IST as DLV_{SYM_NO_NSE} = "47.3".
# > 40% generally = institutional/long-term buying; < 30% = day-trader churn.

def check_delivery_percent(sym: str, bm_data: dict,
                           min_pct: float = DELIVERY_MIN_PCT) -> tuple:
    """Fail-open if no DLV_ key for this symbol (first run, fetch error)."""
    if not bm_data:
        return True, "Delivery cache empty — entry allowed"
    clean = sym.replace("NSE:", "").strip().upper()
    val = bm_data.get(f"DLV_{clean}", "")
    if not val:
        return True, f"DLV_{clean} not cached — entry allowed"
    pct = _to_float(val)
    if pct <= 0:
        return True, "Delivery % malformed — entry allowed"
    if pct < min_pct:
        return False, f"Delivery {pct:.0f}% < {min_pct:.0f}% — mostly jobbing, not accumulation"
    label = "strong accumulation" if pct >= 60 else "healthy accumulation"
    return True, f"Delivery {pct:.0f}% — {label} ✅"


# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def _to_float(x) -> float:
    try:
        return float(str(x).replace(",", "").replace("₹", "").replace("%", "").strip())
    except Exception:
        return 0.0
