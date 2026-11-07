import option_paper as P


def pos(entry=10.0):
    return {"entry": entry, "qty_open": 100.0, "sl": entry * 0.75, "peak": entry, "partial": False}


def test_lots_for():
    assert P.lots_for(10, 500) == 1            # one lot = 5000 <= budget
    assert P.lots_for(2, 500) == 6             # 1000 per lot -> 6 lots
    assert P.lots_for(15, 500) == 1            # 7500 <= 1.5x budget -> still 1 lot
    assert P.lots_for(25, 500) == 0            # 12500 > 9000 -> too expensive
    assert P.lots_for(None, 500) == 0


def test_entry_windows_and_limits():
    assert P.entry_allowed("09:30", 0, 0, 0, 10) == (True, "")
    assert P.entry_allowed("11:31", 0, 0, 0, 99)[0] is False            # between windows
    assert P.entry_allowed("10:00", 5, 0, 0, 99)[0] is False            # 5 early entries used
    assert P.entry_allowed("14:30", 0, 0, 0, 35)[0] is True             # perfect late setup
    assert P.entry_allowed("14:30", 0, 0, 0, 20)[0] is False            # not perfect
    assert P.entry_allowed("14:30", 0, 1, 0, 40)[0] is False            # late slot used
    assert P.entry_allowed("09:30", 0, 0, -3000, 99)[0] is False        # daily loss stop
    assert P.entry_allowed("09:30", 0, 0, -2999, 99)[0] is True


def test_stop_loss():
    p, sells = P.step_position(pos(), 7.4, "10:00")
    assert sells == [(100.0, 7.4, "STOP")]
    p, sells = P.step_position(pos(), 7.6, "10:00")
    assert sells == [] and p["sl"] == 7.5


def test_partial_then_breakeven_and_trail():
    p, sells = P.step_position(pos(), 15.0, "10:00")                       # +50% -> sell half
    assert sells == [(50.0, 15.0, "PARTIAL +50%")] and p["qty_open"] == 50.0 and p["partial"] is True
    assert p["sl"] == max(10.0, 15.0 * 0.75)                              # 11.25, above breakeven
    p, sells = P.step_position(p, 20.0, "10:30")                          # peak 20 -> trail 15
    assert sells == [] and p["sl"] == 15.0
    p, sells = P.step_position(p, 14.9, "10:35")                          # trail hit
    assert sells == [(50.0, 14.9, "BREAKEVEN/TRAIL STOP")]


def test_time_exit_and_no_bid():
    p, sells = P.step_position(pos(), 11.0, "15:15")
    assert sells == [(100.0, 11.0, "TIME 15:15")]
    p, sells = P.step_position(pos(), None, "11:00")
    assert sells == []
    p, sells = P.step_position(pos(), None, "15:20")
    assert sells[0][1] == 0.0


def test_parsers_and_cost():
    assert P.parse_strike("2300 CE Nov") == 2300.0 and P.parse_strike("-") is None
    assert P.parse_expiry("23-Nov-2026") == "2026-11-23" and P.parse_expiry("2026-11-23") == "2026-11-23" and P.parse_expiry("—") is None
    assert round(P.cost_rs(5000, 6000), 2) == round(40 + 0.0014 * 11000, 2)
