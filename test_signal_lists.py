import publish_signal_lists as P


def _series(n=260, up=0.3):
    return [100 + i * up for i in range(n)]


def test_top_pick_passes_on_clean_breakout():
    c = _series(); v = [1_000_000] * 259 + [2_000_000]
    c[-1] = c[-2] + 3                        # new 50-day closing high, uptrend
    r = P.top_pick_check(c, v, 8.0, True)
    assert r and r["vol_x"] == 2.0


def test_top_pick_each_condition_blocks():
    c = _series(); v = [1_000_000] * 259 + [2_000_000]; c[-1] = c[-2] + 3
    assert P.top_pick_check(c, v, 8.0, False) is None                    # NIFTY below 50-EMA
    assert P.top_pick_check(c, v, 4.9, True) is None                     # RS below 5
    assert P.top_pick_check(c, [1_000_000] * 259 + [1_400_000], 8.0, True) is None # volume 1.4x
    c2 = list(c); c2[-1] = c2[-2] - 1
    assert P.top_pick_check(c2, v, 8.0, True) is None                    # not a breakout
    assert P.top_pick_check(c[:100], v[:100], 8.0, True) is None         # too little history
    assert P.top_pick_check(c, [1] * 259 + [2], 8.0, True) is None       # illiquid (<Rs 10 Cr)


def test_top_pick_needs_uptrend():
    c = [200 - i * 0.3 for i in range(259)] + [200]     # long downtrend then a spike above 50-day closing high? no: still below EMAs
    v = [1_000_000] * 259 + [3_000_000]
    assert P.top_pick_check(c, v, 9.0, True) is None


def test_sip_rule():
    assert P.sip_ok(-20, 120, 110, 100, 50) is True
    assert P.sip_ok(-40, 120, 110, 100, 50) is False      # too deep
    assert P.sip_ok(-10, 120, 110, 100, 50) is False      # not a dip
    assert P.sip_ok(-20, 105, 110, 100, 50) is False      # below 50-DMA
    assert P.sip_ok(-20, 120, 110, 130, 50) is False      # below 200-DMA
    assert P.sip_ok(-20, 120, 110, 100, 5) is False       # illiquid
    assert P.sip_ok(None, 120, 110, 100, 50) is False
