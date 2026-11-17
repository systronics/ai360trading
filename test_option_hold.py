import datetime as dt

import pytz

import trading_bot as B

IST = pytz.timezone("Asia/Kolkata")


def _now(y, m, d, h=11):
    return IST.localize(dt.datetime(y, m, d, h, 0))


def test_option_time_rule_profit_runs_loser_exits():
    ent = "2026-11-17 10:00:00"           # Tuesday
    far = "29-Dec-2026"                    # expiry far away: only the time rule can fire
    f = B._option_ledger_exit
    # day 1 / day 2: never a time exit (only SL / cap / targets elsewhere)
    assert f(-1.0, 6, "", far, ent, _now(2026, 11, 17, 15)) == ""
    assert f(-1.0, 6, "", far, ent, _now(2026, 11, 18)) == ""
    # day 3: not in profit -> exit, in profit -> hold
    assert "not in profit" in f(-0.5, 6, "", far, ent, _now(2026, 11, 20))
    assert f(1.2, 6, "", far, ent, _now(2026, 11, 20)) == ""
    # hard cap: even a winner leaves at 5 trading days
    assert "5 trading days" in f(3.0, 6, "", far, ent, _now(2026, 11, 25))


def test_expiry_week_backstop_and_loss_cap_still_come_first():
    ent = "2026-11-17 10:00:00"
    f = B._option_ledger_exit
    assert "EXPIRY WEEK" in f(2.0, 6, "", "23-Nov-2026", ent, _now(2026, 11, 18))      # <= 5 calendar days to expiry
    assert "LOSS CAP" in f(-4.0, 6, "", "29-Dec-2026", ent, _now(2026, 11, 17, 14))   # est -24% <= -20%
