from datetime import datetime
import premarket_brief as PB
import premarket_gate as G


def _r(pcts):
    ks = ["NASDAQ", "S&P 500", "DOW", "NIKKEI", "HANG SENG"]
    return {k: {"pct": p, "last": 100.0} for k, p in zip(ks, pcts)}


def test_verdict_rules():
    assert PB.verdict(_r([1, 1, 1, 1, 1])) == "POSITIVE"
    assert PB.verdict(_r([-1, -1, -1, -1, -1])) == "NEGATIVE"
    assert PB.verdict(_r([1, -1, 1, -1, 0.1])) == "MIXED"
    assert PB.verdict(_r([0.1, 0.1, 0.1, 0.1, 0.1])) == "MIXED"      # all up but average below +0.3% -> not a strong claim
    assert PB.verdict({"NASDAQ": {"pct": 2, "last": 1}}) == "MIXED"   # missing data -> never a strong claim


def test_pct_change():
    assert abs(PB.pct_change([100, 110])[2] - 10.0) < 1e-6
    assert PB.pct_change([100]) is None and PB.pct_change([0, 5]) is None


def test_narration_has_no_prediction_and_no_gift_number():
    rows = _r([1, 1, 1, 1, 1])
    rows["NIFTY"] = {"pct": 0.1, "last": 25044.65}
    t = " ".join(PB.narration_parts(rows, "POSITIVE", ["TATAPOWER"], None))
    assert "GIFT Nifty apne broker" in t and "salah nahi" in t and "TATAPOWER" in t
    assert "jarur" not in t.lower() and "guarantee" not in t.lower()


def test_gate():
    mk = lambda h, m: datetime(2026, 11, 11, h, m)
    assert G.decide(mk(8, 45), "scheduled", False, None, False)[0] is True
    assert G.decide(mk(9, 11), "scheduled", False, None, False)[0] is False            # too late
    assert G.decide(mk(8, 45), "scheduled", False, "2026-11-11", False)[0] is False    # already posted
    assert G.decide(mk(8, 45), "dry", False, "2026-11-11", False)[0] is True           # dry runs may repeat
    assert G.decide(mk(8, 45), "scheduled", False, None, True)[0] is False            # holiday
    assert G.decide(mk(11, 0), "scheduled", True, "2026-11-11", False)[0] is True      # forced test
