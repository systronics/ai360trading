import datetime as dt
import signal_watch as W


def _trend(n=300, step=0.3):
    return [100 + i * step for i in range(n)]


def test_rsi_and_fwd():
    assert W.rsi14([1.0] * 5) is None
    assert W.rsi14([float(i) for i in range(1, 40)]) == 100.0
    fr = W.fwd_returns(100.0, [101, 102, 103])
    assert fr[1] == round(1 - 0.25, 2) and fr[3] == round(3 - 0.25, 2) and fr[5] is None


def test_rs35_simple():
    ds = [dt.date(2026, 1, 1) + dt.timedelta(days=i) for i in range(60)]
    stock = [100 + i for i in range(60)]
    bench = [1000.0] * 60
    r = W.rs35(stock, bench, ds, ds, 59)
    assert r is not None and r > 20


def test_top_pick_and_rsi75_flags():
    c = _trend()
    h = [x + 0.5 for x in c]
    v = [1000.0] * 300
    c = c[:-1] + [c[-2] * 1.0 + 0.0]      # flat, no breakout
    assert W.daily_signals(c, h, v, 8.0, True) == []
    # a real breakout: consolidation then jump with volume
    base = [100 + i * 0.2 for i in range(250)] + [150.0] * 49
    c2 = base + [158.0]
    h2 = [x + 0.5 for x in c2]
    v2 = [1000.0] * 299 + [2500.0]
    out = W.daily_signals(c2, h2, v2, 8.0, True)
    assert out and out[0] in ("TOP_PICK", "RSI75_BLOCKED")
    assert W.daily_signals(c2, h2, v2, 3.0, True) == []        # RS below 5 -> nothing
    assert W.daily_signals(c2, h2, v2, 8.0, False) == []       # NIFTY below EMA50 -> no top pick


def test_h1_needs_data_and_filters():
    c = [100.0] * 300
    assert W.h1_flip_v4(c, c, 7, True, 8.0) is False
    assert W.h1_flip_v4(c, c, 7, False, 8.0) is False
    assert W.h1_flip_v4(c, c, 7, True, 2.0) is False
