import price_freshness as P


def test_pct_diff():
    assert P.pct_diff(100.0, 100.0) == 0.0
    assert round(P.pct_diff(101.0, 100.0), 2) == 1.0
    assert P.pct_diff(None, 100.0) is None


def test_judge_ok_and_stale():
    ok = [0.1] * 12
    assert P.judge(ok, 0.05)[0] == "OK"
    stale = [2.0] * 5 + [0.1] * 7
    assert P.judge(stale, 0.1)[0] == "STALE"
    assert P.judge([0.1] * 12, 0.5)[0] == "OK"                      # only NIFTY off, stocks fine
    assert P.judge([0.7, 0.8] + [0.1] * 10, 0.4)[0] == "STALE"      # NIFTY off and two stocks off


def test_judge_unknown_when_data_missing():
    assert P.judge([None] * 12, None)[0] == "UNKNOWN"
    assert P.judge([0.1] * 5 + [None] * 7, 0.1)[0] == "UNKNOWN"
