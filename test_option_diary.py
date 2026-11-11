import option_diary as D


def test_defaults_and_rounding():
    s, t = D.defaults(100.0, "", "")
    assert s == 75.0 and t == 150.0
    s, t = D.defaults(333.95, "300", "")
    assert s == 300.0 and t == D.r5(333.95 * 1.5)
    assert D.r5(250.37) == 250.35


def test_decide_exit_order_and_time():
    assert D.decide_exit(100, 75, 150, 120, "10:30") is None
    assert D.decide_exit(100, 75, 150, 74.9, "10:30")[0] == "STOP"
    assert D.decide_exit(100, 75, 150, 150, "10:30")[0] == "TARGET"
    assert D.decide_exit(100, 75, 150, 120, "15:15")[0] == "TIME EXIT"        # time exit at 15:15 even if no level was hit
    assert D.decide_exit(100, 75, 150, None, "10:30") is None                  # no bid = no decision before the close
    assert D.decide_exit(100, 75, 150, None, "15:16")[0] == "TIME EXIT"        # but the close always exits


def test_pnl_includes_costs():
    net, pct = D.pnl(100.0, 110.0, 20)
    assert round(net, 2) == round(200 - (40 + 0.0014 * (2000 + 2200)), 2)
    assert pct == round(net / 2000 * 100, 2)
    assert D.pnl(100.0, 0.0, 20)[0] < -2000          # worthless: full premium plus costs


def test_row_inputs_and_dates():
    assert D.row_inputs({"Underlying": "", "Strike": "400"}) is None
    r = D.row_inputs({"Underlying": "nse:coalindia", "Strike": "400", "Lots": "2", "Expiry": "23/11/2026"})
    assert r["und"] == "COALINDIA" and r["strike"] == 400.0 and r["lots"] == 2 and r["expiry"] == "2026-11-23"
    assert D.row_inputs({"Underlying": "SENSEX", "Strike": "82,600"})["strike"] == 82600.0
    assert D.pdate("11-Nov-2026") == "2026-11-11" and D.pdate("junk") is None


def test_nearest_expiry_and_window():
    c = {("SENSEX", 82600.0, "2026-11-12"): ("k1", 20), ("SENSEX", 82600.0, "2026-11-19"): ("k2", 20), ("SENSEX", 82600.0, "2026-11-05"): ("k0", 20)}
    assert D.nearest_expiry(c, "SENSEX", "2026-11-11") == "2026-11-12"
    assert D.nearest_expiry(c, "SENSEX", "2026-11-20") is None
    assert D.entry_window("09:16") and D.entry_window("15:00") and not D.entry_window("15:01") and not D.entry_window("09:15")


def test_stats_group_by_reason_and_ignore_open():
    rows = [
        {"Status": "TARGET", "Reason": "Bottom catch", "Underlying": "SENSEX", "PnL_Rs": "1000", "PnL_%": "10"},
        {"Status": "STOP", "Reason": "bottom catch ", "Underlying": "SENSEX", "PnL_Rs": "-500", "PnL_%": "-5"},
        {"Status": "OPEN", "Reason": "bottom catch", "Underlying": "SENSEX", "PnL_Rs": "", "PnL_%": ""},
        {"Status": "TIME EXIT", "Reason": "trend", "Underlying": "NIFTY", "PnL_Rs": "200", "PnL_%": "2"},
        {"Status": "EXAMPLE", "Reason": "x", "Underlying": "SENSEX", "PnL_Rs": "999", "PnL_%": "9"},
    ]
    s = D.stats(rows)
    assert s["ALL"]["n"] == 3 and s["ALL"]["net"] == 700
    assert s["by_reason"]["bottom catch"]["n"] == 2 and s["by_reason"]["bottom catch"]["win_pct"] == 50
    assert s["by_underlying"]["NIFTY"]["n"] == 1


def test_atm_and_expiry_rules():
    assert D.atm_strike([82400.0, 82500.0, 82600.0], 82540.0) == 82500.0
    assert D.atm_strike([], 100) is None and D.atm_strike([100.0], None) is None
    c = {("NIFTY", 25400.0, "2026-11-11"): ("a", 75), ("NIFTY", 25400.0, "2026-11-17"): ("b", 75),
         ("TCS", 2500.0, "2026-11-13"): ("c", 175), ("TCS", 2500.0, "2026-11-24"): ("d", 175), ("TCS", 2500.0, "2026-12-29"): ("e", 175)}
    assert D.pick_expiry(c, "NIFTY", "2026-11-11", True) == "2026-11-11"          # index: nearest, even the same day
    assert D.pick_expiry(c, "TCS", "2026-11-11", False) == "2026-11-24"           # stock: skips the one that is only 2 days away (rollover rule)
    assert D.pick_expiry(c, "TCS", "2026-12-25", False) == "2026-12-29"
    assert D.pick_expiry(c, "TCS", "2027-01-05", False) is None


def test_plan_picks_and_auto_guard():
    wp = [{"Date": "2026-11-11", "Symbol": "NHPC", "Score": "6", "Option_OK": "YES", "Trigger": "81.38"},
          {"Date": "2026-11-11", "Symbol": "TRENT", "Score": "5", "Option_OK": "YES", "Trigger": "3133.5"},
          {"Date": "2026-11-11", "Symbol": "TCS", "Score": "5", "Option_OK": "NO", "Trigger": "2499.9"},
          {"Date": "2026-11-10", "Symbol": "OLD", "Score": "9", "Option_OK": "YES", "Trigger": "10"},
          {"Date": "2026-11-11", "Symbol": "HCLTECH", "Score": "5", "Option_OK": "YES", "Trigger": "1432"},
          {"Date": "2026-11-11", "Symbol": "WIPRO", "Score": "4", "Option_OK": "YES", "Trigger": "199"}]
    assert D.plan_picks(wp, "2026-11-11") == [("NHPC", 81.38), ("HCLTECH", 1432.0), ("TRENT", 3133.5)]   # best score first, ties by name, max 3, only today, only YES
    assert D.has_auto_today([{"Reason": "auto: index baseline NIFTY", "Date": "2026-11-11"}], "2026-11-11")
    assert not D.has_auto_today([{"Reason": "auto: index baseline NIFTY", "Date": "2026-11-10"}], "2026-11-11")
    assert not D.has_auto_today([{"Reason": "bottom catch", "Date": "2026-11-11"}], "2026-11-11")
