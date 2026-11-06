import trading_bot as T

H = ["Symbol", "Entry Date", "Entry Price", "Exit Date", "Exit Price", "P/L %", "Result", "Strategy", "Exit Reason", "Trade Type"]


def row(pl, tt="🔥 Cash Intraday", day="2026-11-06"):
    return ["NSE:X", day, "100", day, "99", pl, "", "", "", tt]


def test_counts_only_real_losses_of_today():
    rows = [H, row("-0.89%"), row("-2.63%"), row("0.00%"), row("1.14%"), row("-0.49%"), row("-0.50%")]
    assert T.count_intraday_losses(rows, "2026-11-06") == (3, 6)      # -0.50 counts, -0.49 and 0.00 do not


def test_swing_positional_never_counted():
    rows = [H, row("-6.0%", "📈 Positional"), row("-4.0%", "🎯 SWING (Breakout)"), row("-1.0%")]
    assert T.count_intraday_losses(rows, "2026-11-06") == (1, 1)


def test_options_count_and_other_days_do_not():
    rows = [H, row("-20.0%", "📊 Options Alert"), row("-3%", day="2026-11-05"), row("-3%")]
    assert T.count_intraday_losses(rows, "2026-11-06") == (2, 2)


def test_bad_data_is_ignored():
    assert T.count_intraday_losses([], "2026-11-06") == (0, 0)
    assert T.count_intraday_losses([["a", "b"]], "2026-11-06") == (0, 0)
    assert T.count_intraday_losses([H, ["short"], row("abc")], "2026-11-06") == (0, 0)


class FakeWS:
    def __init__(self, v): self.v = v
    def get_all_values(self): return self.v


class FakeSS:
    def __init__(self, v): self.v = v
    def worksheet(self, n): return FakeWS(self.v)


class FakeLog:
    def __init__(self, v): self.spreadsheet = FakeSS(v)


def test_state_threshold():
    two = FakeLog([H, row("-1%"), row("-2%")])
    three = FakeLog([H, row("-1%"), row("-2%"), row("-0.6%")])
    assert T.intraday_pause_state(two, "2026-11-06")[0] is False
    assert T.intraday_pause_state(three, "2026-11-06") == (True, 3, 3)


def test_state_fail_open_and_switch():
    class Boom:
        @property
        def spreadsheet(self): raise RuntimeError("quota")
    assert T.intraday_pause_state(Boom(), "2026-11-06") == (False, 0, 0)
    T.INTRADAY_PAUSE = False
    try:
        assert T.intraday_pause_state(FakeLog([H] + [row("-5%")] * 5), "2026-11-06")[0] is False
    finally:
        T.INTRADAY_PAUSE = True
