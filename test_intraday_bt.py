import numpy as np
import intraday_bt as B


def bars(vals, start_h=9, start_m=15):
    """vals = list of (o,h,l,c); builds arrays and hm labels every 5 minutes."""
    o, h, l, c = (np.array([v[k] for v in vals], dtype=float) for k in range(4))
    hm = []
    t = start_h * 60 + start_m
    for _ in vals:
        hm.append(f"{t // 60:02d}:{t % 60:02d}")
        t += 5
    return o, h, l, c, np.array(hm, dtype=object)


def flat(n=75, px=100.0):
    return [(px, px, px, px)] * n


def test_simulate_target_stop_and_ambiguity():
    v = flat(); v[10] = (100, 103, 99.9, 102)          # target 2R above 100 with stop 98 -> target 104? make stop 99 -> risk1 -> target 102
    o, h, l, c, hm = bars(v)
    r, t, px = B.simulate(o, h, l, c, hm, 5, 100.0, 99.0, 2.0)
    assert t == hm[10] and abs(r - (2.0 - 0.10 / 1.0)) < 1e-9
    v2 = flat(); v2[10] = (100, 103, 98.5, 100)         # touches both stop and target -> stop first
    o, h, l, c, hm = bars(v2)
    r, t, px = B.simulate(o, h, l, c, hm, 5, 100.0, 99.0, 2.0)
    assert px == 99.0 and r < -1.0


def test_simulate_time_exit_and_gap_stop():
    v = flat(); v[20] = (100, 100.5, 99.5, 100.4)
    o, h, l, c, hm = bars(v)
    r, t, px = B.simulate(o, h, l, c, hm, 5, 100.0, 99.0, 3.0)
    assert t >= "15:10" and abs(px - c[-1]) < 1e-9 or t == hm[[i for i in range(len(hm)) if hm[i] >= "15:10"][0]]
    v = flat(); v[8] = (97.0, 97.5, 96.5, 97.0)         # gap below the stop: fills at the open, worse than the stop
    o, h, l, c, hm = bars(v)
    r, t, px = B.simulate(o, h, l, c, hm, 5, 100.0, 99.0, 2.0)
    assert px == 97.0


def test_orb_rule():
    v = [(100, 101, 99, 100)] * 3 + [(100, 100.5, 99.5, 100)] * 4 + [(100, 102, 100, 101.5)] + flat(70)   # bar 7 closes above the opening-range high 101
    o, h, l, c, hm = bars(v)
    day = {"o": o, "h": h, "l": l, "c": c, "hm": hm}
    sig = B.rule_orb(day, 2.0)
    assert sig is not None and sig[0] == 8 and sig[2] == 100.0 and sig[3] == 2.0


def test_summarize():
    import pandas as pd
    t = pd.DataFrame({"R": [2.0, -1.0, -1.0, 2.0]})
    s = B.summarize(t)
    assert "n=    4" in s and "win 50.0%" in s and "PF 2.00" in s
    assert B.summarize(pd.DataFrame({"R": []})) == "no trades"


def test_month_chunks():
    from datetime import date
    ch = list(B._month_chunks(date(2022, 4, 10), date(2022, 6, 5)))
    assert ch == [(date(2022, 4, 10), date(2022, 4, 30)), (date(2022, 5, 1), date(2022, 5, 31)), (date(2022, 6, 1), date(2022, 6, 5))]
