import trading_bot as T


def test_ema_above_basic():
    up = [100 + i for i in range(80)]
    down = [200 - i for i in range(80)]
    assert T.ema_above(up) is True
    assert T.ema_above(down) is False


def test_ema_above_needs_history():
    assert T.ema_above([1, 2, 3]) is None
    assert T.ema_above(None) is None


def test_ema_above_dip_then_recovery():
    s = [100.0] * 60 + [90.0] * 10 + [101.0]            # just recovered above the EMA
    assert T.ema_above(s) is True
    s2 = [100.0] * 60 + [110.0] * 10 + [99.0]           # just fell below it
    assert T.ema_above(s2) is False


def test_switch_exists():
    assert T.CASH_REGIME_GATE is True


def test_cash_row_is_live():
    from datetime import datetime
    import pytz
    now = datetime(2026, 11, 6, 9, 30, tzinfo=pytz.timezone("Asia/Kolkata"))
    assert T._cash_row_is_live("2026-11-06 09:25:10", now) is True
    assert T._cash_row_is_live("2026-11-06 09:20:00", now) is True
    assert T._cash_row_is_live("2026-11-06 07:48:32", now) is False      # pre-market scan = yesterday's data
    assert T._cash_row_is_live("2026-11-05 14:00:00", now) is False      # yesterday
    assert T._cash_row_is_live("not a time", now) is True                # fail-open
    assert T.CASH_REQUIRE_LIVE_SCAN is True


def test_split_matches_and_detect():
    from datetime import datetime
    import pytz
    import pandas as pd
    now = datetime(2026, 11, 6, 9, 30, tzinfo=pytz.timezone("Asia/Kolkata"))
    sp = pd.Series([5.0], index=[pd.Timestamp("2026-11-06")])
    # 5:1 split, entered before, price fell to about one fifth
    assert T.detect_split("NSE:TEST", 1000.0, 205.0, "2026-11-04 09:51:00", now, splits=sp) == 5.0
    # an ordinary -25% fall with a split on file that does NOT match the ratio -> not adjusted
    assert T.detect_split("NSE:TEST", 1000.0, 750.0, "2026-11-04 09:51:00", now, splits=sp) == 0.0
    # split happened BEFORE the entry -> entry price is already post-split -> not adjusted
    assert T.detect_split("NSE:TEST", 200.0, 100.0, "2026-11-07 09:51:00", now, splits=pd.Series([2.0], index=[pd.Timestamp("2026-11-06")])) == 0.0
    # old split (more than 7 days ago) -> ignored
    assert T.detect_split("NSE:TEST", 1000.0, 205.0, "2026-10-01 09:51:00", now, splits=pd.Series([5.0], index=[pd.Timestamp("2026-10-20")])) == 0.0
    # no fall -> no network call, 0.0
    assert T.detect_split("NSE:TEST", 100.0, 99.0, "2026-11-04 09:51:00", now) == 0.0


def test_rescale_mem_and_columns():
    mem = "NSE_X_TSL_95000,NSE_X_MAX_105000,NSE_X_LP_100000,NSE_X_ATR_2500,NSE_Y_TSL_5000,2026-11-05_ENTRY_NSE_X"
    out = T._rescale_mem(mem, "NSE_X", 5.0).split(",")
    assert "NSE_X_TSL_19000" in out and "NSE_X_MAX_21000" in out and "NSE_X_LP_20000" in out and "NSE_X_ATR_500" in out
    assert "NSE_Y_TSL_5000" in out and "2026-11-05_ENTRY_NSE_X" in out          # other symbols / flags untouched
    assert T._col_letter(0) == "A" and T._col_letter(11) == "L" and T._col_letter(14) == "O" and T._col_letter(18) == "S"
    assert T.CORP_ACTION_GUARD is True
