import datetime as dt
import option_watch as W


def _rise(n=60, step=0.5, start=100.0):
    return [start + i * step for i in range(n)]


def test_hv_and_atr():
    c = _rise()
    assert W.hv20(c[:10]) is None
    assert 0 < W.hv20(c) < 30
    h = [x + 1 for x in c]; l = [x - 1 for x in c]
    assert 1 < W.atr_pct(h, l, c) < 4


def test_chart_setup_breakout_near_and_trend_required():
    c = _rise()
    v = [1000.0] * 59 + [2000.0]
    assert W.chart_setup(c, v, 30, 25, 10) == ("BREAKOUT", 2.0)
    assert W.chart_setup(c, v, 18, 25, 10)[0] is None                    # ADX too low = sideways
    assert W.chart_setup(c, v, 30, 10, 25)[0] is None                    # -DI above +DI
    c2 = c[:-1] + [max(c[-21:-1]) * 0.995]
    assert W.chart_setup(c2, [1000.0] * 60, 30, 25, 10)[0] == "NEAR"


def test_dots():
    assert W.dot_spread(2.0) == W.G and W.dot_spread(5.0) == W.Y and W.dot_spread(8.0) == W.R
    assert W.dot_iv(25, 25) == W.G and W.dot_iv(45, 25) == W.R and W.dot_iv(None, 25) == W.Y
    assert W.dot_theta(1.0) == W.G and W.dot_theta(4.0) == W.Y and W.dot_theta(9.0) == W.R
    assert W.dot_be(1.5, 2.0) == W.G and W.dot_be(5.0, 2.0) == W.R
    assert W.dot_liq(5000, 0) == W.G and W.dot_liq(10, 100) == W.R


def test_expiry_and_judge():
    today = dt.date(2026, 11, 13)
    ms = lambda d: int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp() * 1000)
    e, dte = W.pick_expiry([ms(dt.date(2026, 11, 23)), ms(dt.date(2026, 12, 29))], today)
    assert e == "2026-12-29" and dte == 46
    cont = {"spread": 2.5, "iv": 26, "theta_pct": 1.0, "be_move": 3.0, "volume": 5000, "oi": 100000, "ask": 30, "strike": 770}
    j = W.judge("BREAKOUT", cont, 25, 2.0, 46)
    assert j["listed"] and j["greens"] >= 3
    assert not W.judge("BREAKOUT", dict(cont, spread=9), 25, 2.0, 46)["listed"]
    assert not W.judge("BREAKOUT", cont, 25, 2.0, 10)["listed"]
    assert not W.judge(None, cont, 25, 2.0, 46)["listed"]


def test_chain_contract_and_message():
    rows = [{"strike_price": 770, "underlying_spot_price": 769.3, "call_options": {"instrument_key": "NSE_FO|1", "market_data": {"ltp": 30.9, "bid_price": 30.0, "ask_price": 30.9, "volume": 23750, "oi": 28500},
            "option_greeks": {"iv": 27.5, "theta": -0.32}}}, {"strike_price": 780, "call_options": {}}]
    c = W.contract_from_chain(rows, 769.3)
    assert c and c["strike"] == 770 and c["be"] == 800.9 and c["spread"] is not None
    it = {"sym": "DLF", "setup": "BREAKOUT", "spot": 769.3, "adx": 41, "volx": 1.7, "expiry": "2026-12-29", "dte": 46, "cont": c, "j": W.judge("BREAKOUT", c, 25, 2.0, 46), "hv": 25.0, "lot_cost": 29355}
    m = W.build_message([it], dt.date(2026, 11, 14), 180)
    assert "DLF" in m and "not advice" in m and "break even" in m
    assert "No clean" in W.build_message([], dt.date(2026, 11, 14), 180)


def test_be_scored():
    assert W.be_scored([101, 102], 105, 100) is None
    assert W.be_scored([101, 106, 102, 103, 104], 105, 100) == (6.0, "Y")
    assert W.be_scored([101, 102, 102, 103, 104], 105, 100)[1] == "N"
