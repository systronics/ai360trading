import chart_reader as C


def _series():
    # 80 flat bars around 100 (resistance ~105 touched 3x), then breakout to 112, then pullback to ~105.5
    closes, highs, lows = [], [], []
    base = [100, 101, 102, 103, 104, 102, 101, 100, 99, 100]
    for r in range(6):
        for b in base:
            closes.append(float(b))
    # make 3 swing highs ~105
    for i in (8, 28, 48):
        closes[i] = 105.0
    closes += [106, 108, 110, 112, 111, 109, 107, 106, 105.6]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    return closes, highs, lows


def test_zones_cluster():
    z = C.zones([105.0, 105.3, 104.8, 90.0])
    assert z[0][1] == 3 and 104.5 < z[0][0] < 105.5


def test_retest_detected():
    closes, highs, lows = _series()
    r = C.retest_state(closes, highs, lows, [105.5])
    assert r["status"] == "RETEST" and r["bars_since_breakout"] >= 1


def test_extended_and_failed():
    closes, highs, lows = _series()
    assert C.retest_state(closes[:-4], highs[:-4], lows[:-4], [105.5])["status"] == "EXTENDED"
    f = closes[:-1] + [103.0]
    assert C.retest_state(f, highs, lows, [105.5])["status"] == "FAILED"


def test_read_needs_60_bars_and_runs():
    closes, highs, lows = _series()
    assert C.read(closes, highs, lows, closes[:30]) is None
    r = C.read(closes, highs, lows, closes)
    assert r and r["trend"] in ("UP", "DOWN", "MIXED") and "retest" in r
    assert "close" in C.describe("X", r)


def test_trendline_slope():
    m, c = C.trendline([(0, 10.0), (5, 15.0), (10, 20.0)])
    assert abs(m - 1.0) < 1e-9
