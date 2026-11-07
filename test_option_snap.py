import option_snap as S
from datetime import datetime, timezone


def row(k, coi, poi, cltp=10, pltp=10):
    return {"strike_price": k, "underlying_spot_price": 100,
            "call_options": {"market_data": {"ltp": cltp, "oi": coi, "prev_oi": coi / 2 if coi else None, "volume": 5, "bid_price": cltp - 0.5, "ask_price": cltp + 0.5},
                             "option_greeks": {"iv": 20, "theta": -0.5}},
            "put_options": {"market_data": {"ltp": pltp, "oi": poi, "prev_oi": poi, "volume": 7, "bid_price": pltp - 1, "ask_price": pltp + 1},
                            "option_greeks": {"iv": 22, "theta": -0.4}}}


def test_max_pain_simple():
    # calls heavy at 110, puts heavy at 90 -> writers' pain smallest in between
    assert S.max_pain([(90, 0, 1000), (100, 100, 100), (110, 1000, 0)]) == 100
    assert S.max_pain([]) is None


def test_chain_metrics():
    rows = [row(90, 100, 900), row(100, 500, 500), row(110, 900, 100)]
    m = S.chain_metrics(rows)
    assert m["atm"] == 100 and m["spot"] == 100
    assert m["pcr"] == round((900 + 500 + 100) / (100 + 500 + 900), 2) == 1.0
    assert m["call_wall"] == 110 and m["put_wall"] == 90
    assert m["ce"]["oi_chg"] == 100.0 and m["pe"]["oi_chg"] == 0.0
    assert m["ce"]["theta_pct"] == 5.0 and m["ce"]["spread_pct"] == 10.0
    assert S.chain_metrics([]) is None
    assert S.chain_metrics([{"strike_price": 1}]) is None


def test_pick_expiry_rollover():
    now = datetime(2026, 11, 7, tzinfo=timezone.utc)
    ms = lambda y, m, d: int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)
    assert S.pick_expiry([ms(2026, 11, 10), ms(2026, 11, 23), ms(2026, 12, 29)], now) == ("2026-11-23", 16)     # 3 days away is skipped (rollover rule)
    assert S.pick_expiry([ms(2026, 11, 10)], now) == (None, None)
