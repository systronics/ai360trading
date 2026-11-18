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
    assert "सलाह नहीं" in t and "गिफ्ट निफ्टी अपने चार्ट" in t                  # honest: GIFT Nifty is not shown, viewers are sent to their own chart
    assert "ओपनिंग ऊपर" in t                                                  # trend signal, not a list of numbers
    assert not any(ch.isdigit() for ch in t)                                  # numbers are on screen, never spoken
    assert "TATAPOWER" not in t                                               # Latin symbols are not read by the Hindi voice; the list is on screen
    assert "गारंटी" not in t


def test_gate():
    mk = lambda h, m: datetime(2026, 11, 11, h, m)
    assert G.decide(mk(8, 45), "scheduled", False, None, False)[0] is True
    assert G.decide(mk(9, 11), "scheduled", False, None, False)[0] is False            # too late
    assert G.decide(mk(8, 45), "scheduled", False, "2026-11-11", False)[0] is False    # already posted
    assert G.decide(mk(8, 45), "dry", False, "2026-11-11", False)[0] is True           # dry runs may repeat
    assert G.decide(mk(8, 45), "scheduled", False, None, True)[0] is False            # holiday
    assert G.decide(mk(11, 0), "scheduled", True, "2026-11-11", False)[0] is True      # forced test


def test_premarket_text_builds_and_is_information_only():
    import premarket_text as T
    from datetime import date
    rows = _r([-1, -1, -1.6, -0.5, -0.8])
    rows["CRUDE WTI"] = {"pct": -2.0, "last": 80.0}
    rows["INDIA VIX"] = {"pct": 0, "last": 15.5}
    t = T.build_text(rows, PB.verdict(rows), ["ABC"], date(2026, 11, 18))
    assert "KAMZOR" in t and "IT stocks" in t and "ABC" in t and "entry signal nahi" in t
    assert "GIFT" in t and not any(w in t.lower() for w in ("buy ", "target", "stoploss"))
    assert T.build_text({"NASDAQ": {"pct": 1, "last": 1}}, "MIXED", [], date(2026, 11, 18)) == ""   # too little data -> nothing
