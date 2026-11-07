import numpy as np
import pandas as pd
import intraday_bt3 as T


def fake5(days=3):
    rows = []
    px = 100.0
    for d in pd.bdate_range("2024-01-01", periods=days):
        t0 = pd.Timestamp(d.date()).tz_localize("Asia/Kolkata") + pd.Timedelta(hours=9, minutes=15)
        for k in range(75):
            px *= 1.0004
            rows.append([t0 + pd.Timedelta(minutes=5 * k), px, px * 1.001, px * 0.999, px, 1000])
    return pd.DataFrame(rows, columns=["ts", "o", "h", "l", "c", "v"])


def test_htf_flags_use_only_completed_bars():
    f = T.htf_flags(fake5(4))
    assert set(["a15", "a60", "a240"]).issubset(f.columns) and len(f) == 300
    # steadily rising price: once a bar has completed, close > EMA50 is true; the very first bars of the data have no completed HTF bar -> False
    assert not f["a60"].iloc[0] and bool(f["a15"].iloc[-1]) and bool(f["a240"].iloc[-1])


def test_daily_weekly_flags_rising_market():
    d = pd.DataFrame({"c": np.linspace(100, 200, 400)}, index=[x.date() for x in pd.bdate_range("2023-01-02", periods=400)])
    fl = T.daily_weekly_flags(d)
    last = list(d.index)[-1]
    assert fl[last] == (True, True)
