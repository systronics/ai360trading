import datetime as dt
import trading_bot as tb


def _gate(trend, spread, monkeypatch=None, expiry="29-Dec-2026"):
    tb._OPT_INTEL_AVAILABLE = False
    tb._read_opt_trend_from_nifty200 = lambda sh, sym: trend
    tb._option_atm_spread_pct = lambda sym, exp, now: spread
    return tb.option_entry_gate("NSE:DLF", expiry, dt.datetime(2026, 11, 16, 14, 50), {"MKT_PCR_NIFTY": "1.0"}, object())


def test_trend_ok_and_spread_ok_passes():
    ok, why = _gate("OK", 2.5)
    assert ok and any("trend OK" in w for w in why) and any("spread 2.5%" in w for w in why)


def test_sideways_blocks():
    ok, why = _gate("NO", 2.0)
    assert not ok and any("sideways" in w for w in why)


def test_wide_spread_blocks():
    ok, why = _gate("OK", 9.0)
    assert not ok and any("hidden cost" in w for w in why)


def test_unknown_trend_and_spread_allow():
    ok, why = _gate(None, None)
    assert ok and any("not available" in w for w in why)


def test_short_expiry_still_blocks():
    ok, _ = _gate("OK", 2.0, expiry="23-Nov-2026")
    assert not ok
