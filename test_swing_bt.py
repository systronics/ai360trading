import numpy as np
import swing_bt as S


def arrs(n=60, px=100.0):
    a = np.full(n, px)
    return a.copy(), a.copy(), a.copy(), a.copy()


def test_hold_exits():
    o, h, l, c = arrs()
    c[19] = 110.0
    j, px = S.simulate_exit("X1 HOLD20", o, h, l, c, 0, 2.0)
    assert j == 19 and px == 110.0                           # day 20 counting the entry day as day 1
    j, px = S.simulate_exit("X2 HOLD10", o, h, l, c, 0, 2.0)
    assert j == 9


def test_stop_gap_and_target():
    o, h, l, c = arrs()
    l[3] = 95.0                                              # stop = 100 - 2*2 = 96 -> hit at 96 (no gap)
    j, px = S.simulate_exit("X4 ATR2+HOLD20", o, h, l, c, 0, 2.0)
    assert j == 3 and px == 96.0
    o2, h2, l2, c2 = arrs()
    o2[4], l2[4] = 90.0, 89.0                                # gap through the stop fills at the open
    j, px = S.simulate_exit("X4 ATR2+HOLD20", o2, h2, l2, c2, 0, 2.0)
    assert j == 4 and px == 90.0
    o3, h3, l3, c3 = arrs()
    h3[5] = 108.0                                            # live target = 100 + 3.8*2 = 107.6
    j, px = S.simulate_exit("X5 LIVE-RULE", o3, h3, l3, c3, 0, 2.0)
    assert j == 5 and abs(px - 107.6) < 1e-9
    o4, h4, l4, c4 = arrs()
    h4[5], l4[5] = 108.0, 95.0                               # both on the same day -> stop first
    j, px = S.simulate_exit("X5 LIVE-RULE", o4, h4, l4, c4, 0, 2.0)
    assert px == 96.0


def test_trail_moves_up_only():
    o, h, l, c = arrs()
    for k in range(1, 8):
        h[k] = 100 + 3 * k                                   # climbing highs and lows
        c[k] = h[k]
        l[k] = h[k] - 1
    for k in range(1, 9):
        o[k] = c[k - 1] if k < 8 else 121.0               # realistic opens (no artificial gap)
    h[8], l[8] = 121.0, 114.0                                # trail = 121? highest high so far 121 at day 8? stop = hi - 5
    j, px = S.simulate_exit("X6 TRAIL", o, h, l, c, 0, 2.0)
    assert j == 8 and abs(px - 116.0) < 1e-9                 # trail = 121 - 5 = 116, hit on day 9 of the loop (index 8)


def test_stats_and_signals_shape():
    import pandas as pd
    t = pd.DataFrame({"pct": [10.0, -5.0, 5.0, -5.0], "days": [10, 5, 8, 4]})
    s = S.stats(t)
    assert "win 50.0%" in s and "PF 1.50" in s
    assert S.stats(pd.DataFrame({"pct": [], "days": []})) == "no trades"
