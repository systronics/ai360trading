import trading_bot as T


def test_ema_above_basic():
    up = [100 + i for i in range(80)]
    down = [200 - i for i in range(80)]
    assert T.ema_above(up) is True
    assert T.ema_above(down) is False


def test_ema_above_needs_history():
    assert T.ema_above([1, 2, 3]) is None
    assert T.ema_above(None) is None


def test_ema_above_dip_then_recovery():
    s = [100.0] * 60 + [90.0] * 10 + [101.0]            # just recovered above the EMA
    assert T.ema_above(s) is True
    s2 = [100.0] * 60 + [110.0] * 10 + [99.0]           # just fell below it
    assert T.ema_above(s2) is False


def test_switch_exists():
    assert T.CASH_REGIME_GATE is True
