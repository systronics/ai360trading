import datetime as dt
import gainers_log as G


def test_categorize():
    assert G.categorize(8.0, "Y", "Y") == "LEADER"
    assert G.categorize(-6.0, "N", "N") == "LAGGARD-BOUNCE"
    assert G.categorize(3.0, "Y", "N") == "TREND-OTHER"
    assert G.categorize(None, "N", "N") == "TREND-OTHER"


def test_result_near():
    ev = {"MARICO": [dt.date(2026, 11, 2)], "BSE": [dt.date(2026, 11, 4)]}
    day = dt.date(2026, 11, 3)
    assert G.result_near(ev, "MARICO", day) is True
    assert G.result_near(ev, "BSE", day) is True
    assert G.result_near(ev, "TCS", day) is False
    assert G.result_near({"X": [dt.date(2026, 10, 20)]}, "X", day) is False


def test_top_gainers_and_rows():
    ga = [{"Date": "2026-11-02", "Symbol": "AAA", "RS35": "8", "Above_50DMA": "Y", "RSI14": "55", "G_RS": "Y", "G_Trend": "Y", "G_RSI": "Y", "G_Leader": "Y", "Day_%": "1"},
          {"Date": "2026-11-02", "Symbol": "BBB", "RS35": "-9", "Above_50DMA": "N", "RSI14": "30", "G_RS": "N", "G_Trend": "N", "G_RSI": "Y", "G_Leader": "N", "Day_%": "1"},
          {"Date": "2026-11-03", "Symbol": "AAA", "Day_%": "2.5", "Gap_%": "0.5"},
          {"Date": "2026-11-03", "Symbol": "BBB", "Day_%": "7.1", "Gap_%": "1.0"}]
    rows = G.build_rows(ga, "2026-11-03", "2026-11-02", {}, {"AAA": [("2026-11-03", "2026-11-03")]})
    assert [r[2] for r in rows] == ["BBB", "AAA"]
    assert rows[0][12] == "LAGGARD-BOUNCE" and rows[1][12] == "LEADER"
    assert rows[1][15] == "Y" and rows[0][15] == "N"


def test_scan_cols():
    import gainers_log as G
    scan = {"A": {"Date": "2026-11-06", "First_Status": "GATE 3: RS", "Last_Status": "QUEUED", "Gate_Counts": '{"GATE 3":4}'},
            "B": {"Date": "2026-11-05", "First_Status": "x", "Last_Status": "y", "Gate_Counts": "{}"}}
    assert G.scan_cols(scan, "A", "2026-11-06") == ["GATE 3: RS", "QUEUED", '{"GATE 3":4}']
    assert G.scan_cols(scan, "B", "2026-11-06")[0].startswith("no scan data for this day")
    assert G.scan_cols(scan, "Z", "2026-11-06")[0].startswith("not in the live scan")
    assert len(G.HEAD) == 22
    assert G.scan_cols({}, "A", "2026-11-06")[0] == "scan history not recorded yet"
