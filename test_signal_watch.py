import datetime as dt
import signal_watch as W


def _trend(n=300, step=0.3):
    return [100 + i * step for i in range(n)]


def test_rsi_and_fwd():
    assert W.rsi14([1.0] * 5) is None
    assert W.rsi14([float(i) for i in range(1, 40)]) == 100.0
    fr = W.fwd_returns(100.0, [101, 102, 103])
    assert fr[1] == round(1 - 0.25, 2) and fr[3] == round(3 - 0.25, 2) and fr[5] is None


def test_rs35_simple():
    ds = [dt.date(2026, 1, 1) + dt.timedelta(days=i) for i in range(60)]
    stock = [100 + i for i in range(60)]
    bench = [1000.0] * 60
    r = W.rs35(stock, bench, ds, ds, 59)
    assert r is not None and r > 20


def test_top_pick_and_rsi75_flags():
    c = _trend()
    h = [x + 0.5 for x in c]
    v = [1000.0] * 300
    c = c[:-1] + [c[-2] * 1.0 + 0.0]      # flat, no breakout
    assert W.daily_signals(c, h, v, 8.0, True) == []
    # a real breakout: consolidation then jump with volume
    base = [100 + i * 0.2 for i in range(250)] + [150.0] * 49
    c2 = base + [158.0]
    h2 = [x + 0.5 for x in c2]
    v2 = [1000.0] * 299 + [2500.0]
    out = W.daily_signals(c2, h2, v2, 8.0, True)
    assert out and out[0] in ("TOP_PICK", "RSI75_BLOCKED")
    assert W.daily_signals(c2, h2, v2, 3.0, True) == []        # RS below 5 -> nothing
    assert W.daily_signals(c2, h2, v2, 8.0, False) == []       # NIFTY below EMA50 -> no top pick


def test_h1_needs_data_and_filters():
    c = [100.0] * 300
    assert W.h1_flip_v4(c, c, 7, True, 8.0) is False
    assert W.h1_flip_v4(c, c, 7, False, 8.0) is False
    assert W.h1_flip_v4(c, c, 7, True, 2.0) is False


def test_option_alert_category_and_rows():
    import datetime as dt
    import signal_watch as S
    assert S.opt_category("🎯 RETEST | BREAKOUT CONFIRMED") == "OPT_RETEST"
    assert S.opt_category("🚀 BREAKOUT | BREAKOUT ALERT") == "OPT_BREAKOUT"
    assert S.opt_category(None) == "OPT_BREAKOUT"

    class WS:
        def get_all_values(self):
            return [["Time", "Symbol", "Price", "Prio", "Trade Type", "Strategy"],
                    ["2026-11-17 10:33", "NSE:DLF", "750.05", "40", "📊 Options Alert", "🎯 RETEST | x"],
                    ["2026-11-17 10:40", "NSE:TCS", "3500", "30", "🎯 SWING", "y"],
                    ["2026-11-16 10:40", "NSE:SBIN", "1090", "30", "📊 Options Alert", "z"],
                    ["2026-11-17 11:00", "NSE:BAD", "n/a", "30", "📊 Options Alert", "z"]]

    class SH:
        def worksheet(self, n):
            return WS()

    out = S.option_alert_signals(SH(), dt.date(2026, 11, 17))
    assert out == [("DLF", dt.date(2026, 11, 17), "OPT_RETEST", 750.05, None, None, None)]
    assert S.option_alert_signals(object(), dt.date(2026, 11, 17)) == []   # fail-open


def test_shadow_breakout_rows_come_from_botmemory_and_nifty200():
    import datetime as dt
    import signal_watch as S

    class BM:
        def get_all_values(self):
            return [["Key", "Value", "UpdatedAt", "Sym", "Type"],
                    ["2026-11-17_OPTSHADOW_NSE_PHOENIXLTD", "1", "", "NSE:PHOENIXLTD", "FLAG"],
                    ["2026-11-17_OPTSHADOW_NSE_M_M", "1", "", "NSE:M_M", "FLAG"],
                    ["2026-11-16_OPTSHADOW_NSE_DLF", "1", "", "NSE:DLF", "FLAG"],
                    ["2026-11-17_OPT_NSE_PNB", "1", "", "NSE:PNB", "FLAG"]]

    class N2:
        def get_all_values(self):
            return [["h"], ["h2"], ["NSE:PHOENIXLTD", "Realty", "2,229.00"], ["NSE:M_M", "Auto", "3100"], ["NSE:DLF", "Realty", "750"]]

    class SH:
        def worksheet(self, n):
            return BM() if n == "BotMemory" else N2()

    out = S.shadow_breakout_signals(SH(), dt.date(2026, 11, 17))
    assert [(o[0], o[2], o[3]) for o in out] == [("M_M", "OPT_BREAKOUT", 3100.0), ("PHOENIXLTD", "OPT_BREAKOUT", 2229.0)]
    assert S.shadow_breakout_signals(object(), dt.date(2026, 11, 17)) == []   # fail-open
