import fetch_opt_trend as T


def _series(n=80, step=1.0, base=100.0, wiggle=0.0):
    c = [base + i * step + (wiggle if i % 2 else -wiggle) for i in range(n)]
    h = [x + 1.0 for x in c]
    l = [x - 1.0 for x in c]
    return h, l, c


def test_strong_uptrend_is_ok():
    h, l, c = _series(step=1.0)
    adx, flag = T.trend_flag(h, l, c)
    assert flag == "OK" and adx >= 25


def test_downtrend_is_no():
    h, l, c = _series(step=-1.0, base=300.0)
    assert T.trend_flag(h, l, c)[1] == "NO"


def test_sideways_is_no():
    h, l, c = _series(step=0.0, wiggle=1.5)
    assert T.trend_flag(h, l, c)[1] == "NO"


def test_short_history_is_blank():
    h, l, c = _series(n=10)
    assert T.trend_flag(h, l, c) == (None, "")


def test_a1_columns():
    assert T._a1(1) == "A" and T._a1(26) == "Z" and T._a1(27) == "AA" and T._a1(44) == "AR"


def test_hv20_matches_option_intelligence_maths_and_needs_21_closes():
    import fetch_opt_trend as F
    closes = [100 * (1.01 if i % 2 else 0.995) ** i for i in range(30)]
    hv = F.hv20(closes)
    assert hv is not None and hv > 0
    assert F.hv20([1, 2, 3]) is None
    # flat prices -> zero volatility, still a number (not None)
    assert F.hv20([100.0] * 25) == 0.0
