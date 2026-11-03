import datetime as dt
import result_runup as R


def test_trading_days():
    assert R.trading_days_between(dt.date(2026, 11, 3), dt.date(2026, 11, 4)) == 1
    assert R.trading_days_between(dt.date(2026, 11, 3), dt.date(2026, 11, 9)) == 4          # Wed 4,5,6, Mon 9
    assert R.trading_days_between(dt.date(2026, 11, 3), dt.date(2026, 11, 9), {dt.date(2026, 11, 5)}) == 3
    assert R.trading_days_between(dt.date(2026, 11, 3), dt.date(2026, 11, 3)) == 0


def test_grade():
    assert R.grade(True, 6, 60) == "A"
    assert R.grade(True, 4.9, 60) == "B"
    assert R.grade(True, 6, 66) == "B"
    assert R.grade(False, 20, 40) == ""
    assert R.grade(True, None, None) == "B"


def test_rsi():
    assert R.rsi14([1.0] * 10) is None
    up = [float(i) for i in range(1, 30)]
    assert R.rsi14(up) == 100.0
    down = [float(30 - i) for i in range(30)]
    assert R.rsi14(down) == 0.0


def test_prev_trading_day():
    assert R.prev_trading_day(dt.date(2026, 11, 9)) == dt.date(2026, 11, 6)                   # Monday -> Friday
    assert R.prev_trading_day(dt.date(2026, 11, 6), {dt.date(2026, 11, 5)}) == dt.date(2026, 11, 4)
