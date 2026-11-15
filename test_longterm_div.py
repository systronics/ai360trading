import generate_longterm as G


def test_div_yield_is_percent_not_times_hundred():
    assert round(G._div_yield_pct({"dividendRate": 48.0, "currentPrice": 2407.5, "dividendYield": 1.99}), 2) == 1.99
    assert round(G._div_yield_pct({"dividendYield": 5.61}), 2) == 5.61          # already percent (yfinance 1.x), never x100
    assert G._div_yield_pct({"dividendYield": 561.0}) == 0.0                     # bad data above 25 percent is ignored
    assert G._div_yield_pct({}) == 0.0


def test_dividend_payer_no_longer_gets_high_div_bonus_by_mistake():
    base = dict(cmp=100.0, h52=150.0, l52=90.0, rsi=50.0, fund_score=5, fii_change=0.0)
    sig_low = G.make_signal(dict(base, div=0.95))[0]
    sig_inflated = G.make_signal(dict(base, div=95.0))[0]
    assert sig_low != "ACCUMULATE 🟡" or sig_inflated == sig_low
