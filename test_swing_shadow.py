from datetime import date, timedelta
import swing_shadow as W


def days(n, start=date(2026, 1, 5)):
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def test_score_hold():
    ds = days(30)
    cl = [100.0 + i for i in range(30)]
    r = W.score_hold(ds, cl, ds[2], 102.0, 20)                 # entry day index 2 -> day 20 is index 21 -> close 121
    assert r == (ds[21], 121.0, round((121 / 102 - 1) * 100, 2))
    assert W.score_hold(ds, cl, ds[15], 115.0, 20) is None      # not enough days yet
    assert W.score_hold(ds, cl, ds[2], 0, 20) is None
    assert W.score_hold(ds, cl, date(2030, 1, 1), 100.0, 5) is None


def test_entry_on_non_trading_day_uses_next_session():
    ds = days(30)
    sat = ds[4] + timedelta(days=1)                             # a Saturday -> first session on/after it is the next Monday
    r = W.score_hold(ds, [100.0] * 30, sat, 100.0, 1)
    assert r[0] >= sat and r[2] == 0.0


def test_post_exit_high():
    ds = days(15)
    hi = [100.0] * 15
    hi[6] = 110.0
    assert W.post_exit_high(ds, hi, ds[3], 100.0) == 10.0
    assert W.post_exit_high(ds, hi, ds[14], 100.0) is None
    assert W.post_exit_high(ds, hi, ds[3], 0) is None
    hi[3 + 11] = 150.0                                          # beyond the 10-session window
    assert W.post_exit_high(ds, hi, ds[3], 100.0) == 10.0


def test_weekly_flag_rising_series():
    import pandas as pd
    import swing_bt3 as W3
    idx = pd.bdate_range("2023-01-02", periods=400)
    c = pd.Series(range(100, 500), index=idx, dtype=float)
    f = W3.weekly_flag(c)
    assert bool(f.iloc[-1]) and not bool(f.iloc[2])           # early days have no completed week
