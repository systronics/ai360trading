"""
entry_quality.py — "big profit, minimum loss, no reversal" scoring layer — v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pure functions only — NO network, NO sheet I/O. Every caller in trading_bot.py
wraps these in try/except and FAILS OPEN (a bug here = allow the trade / keep the
old order), so this module can never break the live income pipeline. Runs forever
on the existing crons, ₹0, no human or AI needed.

Four tools (the owner's ask: clear, safe, biggest target, no reversal):
  1. reversal_risk()          — 0-100; vetoes "big but about-to-reverse" entries.
  2. target_room()            — clean runway to next resistance, in ATR multiples
                                (bigger = bigger realistic target).
  3. composite_score()        — ranks multiple candidates: conviction × reward
                                × room ÷ reversal-risk → pick the ONE best.
  4. is_confirmed_accumulation() — distinguishes a real "buy-the-corrected-leader"
                                setup from a falling knife (sector up + FII
                                accumulating + reclaim of 20-DMA + leadership).

All thresholds are conservative and documented; tune in ONE place here.
"""

VERSION = "v1.0"

# A new long with reversal_risk at/above this is rejected (fail-open if uncomputable).
REVERSAL_RISK_VETO   = 70.0
# Minimum clean runway (in ATR) to bother — below this the "target" is too small.
MIN_TARGET_ROOM_ATR  = 1.5


def reversal_risk(rsi=0.0, pct_below_ath=None, dist_from_20dma=None,
                  rel_vol=0.0, is_bullish=True):
    """
    Likelihood (0-100) that a FRESH LONG reverses against us. Higher = worse.
    Built from the classic exhaustion tells — each capped so no single input
    dominates:
      • Overbought RSI            (> 65 bull / > 58 bear)
      • Too close to ATH          (|pct_below_ath| small = no room, reversal-prone)
      • Stretched above 20-DMA    (mean-reversion pull)
      • Blow-off volume while already stretched (climax/exhaustion)
    Any missing input simply contributes 0 (fail-open).
    """
    risk = 0.0
    if rsi and rsi > 0:
        thr = 65 if is_bullish else 58
        if rsi > thr:
            risk += min(30.0, (rsi - thr) * 2.0)
    if pct_below_ath is not None:
        d = abs(pct_below_ath)
        if d < 3:     risk += 25.0
        elif d < 7:   risk += 12.0
    if dist_from_20dma is not None and dist_from_20dma > 0:
        if dist_from_20dma > 12:   risk += 25.0
        elif dist_from_20dma > 8:  risk += 12.0
    if rel_vol and rel_vol >= 4 and dist_from_20dma and dist_from_20dma > 8:
        risk += 15.0   # climax volume on an already-extended move
    return round(min(100.0, risk), 1)


def target_room(cmp, resistance, atr):
    """
    Clean runway from CMP up to the next resistance, expressed in ATR multiples.
    Bigger = more room for a big SAFE target. Returns 0.0 if data is missing or
    price is already at/above resistance (no clean room → not a fresh-target buy).
    """
    try:
        if cmp <= 0 or atr <= 0 or resistance <= 0 or resistance <= cmp:
            return 0.0
        return round((resistance - cmp) / atr, 2)
    except Exception:
        return 0.0


def composite_score(priority=0.0, rr=0.0, rev_risk=0.0, room=0.0):
    """
    Rank candidates so the BEST fills the limited daily slots first.
    Rewards conviction (priority/Master_Score), reward:risk and clean room;
    penalises reversal risk. Higher = better.
    """
    try:
        base = max(priority, 0.0) * (1.0 + max(rr, 0.0) / 2.0) \
            * (1.0 + min(max(room, 0.0), 6.0) / 6.0)
        penalty = 1.0 + max(rev_risk, 0.0) / 40.0   # rev 0→×1, 80→×3
        return round(base / penalty, 3)
    except Exception:
        return 0.0


def is_confirmed_accumulation(leader_type="", fii_zone="", final_action="",
                              rs=0.0, cmp=0.0, dma20=0.0, sector_rotation=0.0):
    """
    True ONLY for a genuine 'buy the corrected sector leader' setup — never a
    falling knife. Requires ALL: sector leadership + FII accumulating + a
    value/base action + price has RECLAIMED its 20-DMA (the fall has stopped) +
    the sector itself is rotating up + RS not negative.
    Returns (bool, reason).
    """
    lt = str(leader_type or "").lower()
    fa = str(final_action or "")
    if "leader" not in lt:
        return False, f"not a leader ({leader_type})"
    if str(fii_zone or "").strip() != "Accumulation Zone":
        return False, f"FII not accumulating ({fii_zone})"
    if not any(k in fa for k in ("VALUE BUY", "BASE PREPARED")):
        return False, f"action '{fa}' not value/base"
    if not (cmp and dma20 and cmp >= dma20):
        return False, "price has not reclaimed 20-DMA"
    if (sector_rotation or 0) <= 0:
        return False, "sector not rotating up"
    if (rs or 0) < 0:
        return False, f"RS {rs} negative"
    return True, "confirmed accumulation"


# ── self-test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"entry_quality {VERSION} self-test")
    # reversal risk
    safe   = reversal_risk(rsi=55, pct_below_ath=-18, dist_from_20dma=3, rel_vol=1.6, is_bullish=True)
    risky  = reversal_risk(rsi=78, pct_below_ath=-1,  dist_from_20dma=14, rel_vol=5,  is_bullish=True)
    assert safe < REVERSAL_RISK_VETO <= risky, (safe, risky)
    print(f"  reversal_risk: safe={safe} risky={risky} (veto={REVERSAL_RISK_VETO}) OK")
    # target room
    r1 = target_room(cmp=100, resistance=115, atr=5)   # 3 ATR room
    r2 = target_room(cmp=100, resistance=99,  atr=5)   # above resistance → 0
    assert r1 == 3.0 and r2 == 0.0, (r1, r2)
    print(f"  target_room: 3ATR={r1}  no-room={r2} OK")
    # composite ranking — high conviction/RR/room + low reversal beats the opposite
    best  = composite_score(priority=40, rr=3.0, rev_risk=10, room=4)
    worst = composite_score(priority=18, rr=1.8, rev_risk=75, room=1)
    assert best > worst, (best, worst)
    print(f"  composite: best={best} worst={worst} OK")
    # accumulation gate
    ok, why = is_confirmed_accumulation("Sector Leader", "Accumulation Zone",
                                        "💰 VALUE BUY", rs=8, cmp=105, dma20=100, sector_rotation=4)
    bad, why2 = is_confirmed_accumulation("Trend Follower", "Deep Correction",
                                          "🔴 AVOID (Breakdown)", rs=-5, cmp=90, dma20=100, sector_rotation=0)
    assert ok and not bad, (ok, bad)
    print(f"  accumulation: leader→{ok} ({why}) | knife→{bad} ({why2}) OK")
    print("ALL TESTS PASSED")
