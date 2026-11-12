import datetime as dt
import result_watch as W


def test_lean_positive_and_weak():
    s, why = W.lean_score(True, 8, 55, "Long Buildup", 2)
    assert s == 4 and W.lean_label(s) == "POSITIVE lean"
    s2, _ = W.lean_score(False, -3, 75, "Short Buildup", 0)
    assert s2 <= -3 and W.lean_label(s2) == "WEAK lean"


def test_missing_data_is_mixed():
    s, why = W.lean_score(None, None, None, "", None)
    assert s == 0 and W.lean_label(s) == "MIXED" and why == []


def test_already_ran_up_penalised():
    s, why = W.lean_score(True, 8, 60, "", 9)
    assert s == 2 and any("bhaag" in w for w in why)


def test_message_text():
    it = dict(sym="TCS", k=1, E=dt.date(2026, 11, 13), score=3, why=["50-DMA ke upar"], label="POSITIVE lean", cmp=3200.0, chg=0.4, chart="trend UP", dlv=55.0, fo=True)
    m = W.build_message([it], dt.date(2026, 11, 12))
    assert "KAL" in m and "TCS" in m and "prediction nahi" in m and "Options" in m
    assert W.build_message([], dt.date(2026, 11, 12)) is None


def test_pick_priority_and_cap():
    mk = lambda n, gate, fo, sc: dict(sym=n, gate=gate, fo=fo, score=sc, k=1)
    items = [mk("W", False, False, -2), mk("F", False, True, 1), mk("G", True, False, 3), mk("GF", True, True, 3)] + [mk(f"X{i}", False, False, 0) for i in range(10)]
    out = W.pick(items)
    assert [x["sym"] for x in out[:3]] == ["GF", "G", "F"] and len(out) == 8


def test_when_word_weekend_result():
    d = dt.date(2026, 11, 13)
    assert W.when_word(d, d) == "AAJ" and W.when_word(dt.date(2026, 11, 14), d) == "KAL" and "Mon" in W.when_word(dt.date(2026, 11, 16), d)
