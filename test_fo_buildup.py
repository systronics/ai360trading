"""Unit tests for fetch_fo_buildup.py (classification, rollover-aware OI, streak, board). Run: python -m unittest test_fo_buildup -v"""
import unittest
from fetch_fo_buildup import (fwd_ret, classify, summarize, next_streak, mood, sector_rows, PRICE_EPS_PCT, OI_EPS_PCT,
                              LONG_B, SHORT_C, SHORT_B, LONG_U, NEUTRAL)


def stf(sym, expiry, cls, prv, oi, chg, dt="2026-10-30"):
    return {"FinInstrmTp": "STF", "TckrSymb": sym, "XpryDt": expiry, "ClsPric": str(cls), "PrvsClsgPric": str(prv),
            "OpnIntrst": str(oi), "ChngInOpnIntrst": str(chg), "TradDt": dt}


class Classify(unittest.TestCase):
    def test_four_quadrants(self):
        self.assertEqual(classify(1.0, 5.0), LONG_B)
        self.assertEqual(classify(1.0, -5.0), SHORT_C)
        self.assertEqual(classify(-1.0, 5.0), SHORT_B)
        self.assertEqual(classify(-1.0, -5.0), LONG_U)

    def test_boundaries_are_neutral(self):
        self.assertEqual(classify(PRICE_EPS_PCT, 5.0), NEUTRAL)
        self.assertEqual(classify(-PRICE_EPS_PCT, 5.0), NEUTRAL)
        self.assertEqual(classify(1.0, OI_EPS_PCT), NEUTRAL)
        self.assertEqual(classify(1.0, -OI_EPS_PCT), NEUTRAL)
        self.assertEqual(classify(0.0, 0.0), NEUTRAL)

    def test_missing_values_neutral(self):
        self.assertEqual(classify(None, 5.0), NEUTRAL)
        self.assertEqual(classify(1.0, None), NEUTRAL)


class Summarize(unittest.TestCase):
    def test_real_itc_numbers_long_buildup(self):
        rows = [stf("ITC", "2026-12-29", 269.70, 268.20, 13524000, 331200),
                stf("ITC", "2027-01-25", 271.15, 269.80, 272550, 61225),
                stf("ITC", "2026-11-23", 268.10, 266.70, 200408775, 6487725)]
        d = summarize(rows)["ITC"]
        self.assertAlmostEqual(d["price_pct"], (268.10 - 266.70) / 266.70 * 100, places=6)   # near month = 2026-11-23
        self.assertEqual(classify(d["price_pct"], d["oi_pct"]), LONG_B)

    def test_real_hul_numbers_neutral(self):
        rows = [stf("HINDUNILVR", "2027-01-25", 1871.4, 1874.2, 28200, 2400),
                stf("HINDUNILVR", "2026-12-29", 1859.2, 1861.8, 1061400, -1500),
                stf("HINDUNILVR", "2026-11-23", 1846.6, 1852.0, 17947800, -99000)]
        d = summarize(rows)["HINDUNILVR"]
        self.assertLess(abs(d["oi_pct"]), OI_EPS_PCT)
        self.assertEqual(classify(d["price_pct"], d["oi_pct"]), NEUTRAL)

    def test_rollover_is_not_long_unwinding(self):
        # near month OI falls by 1,000,000 (rolled out) but next month rises by 1,100,000: total OI UP -> not 'Long Unwinding'
        rows = [stf("ABC", "2026-11-23", 99.0, 100.0, 4_000_000, -1_000_000),
                stf("ABC", "2026-12-29", 99.5, 100.4, 1_600_000, 1_100_000)]
        d = summarize(rows)["ABC"]
        self.assertGreater(d["oi_pct"], 0)
        self.assertNotEqual(classify(d["price_pct"], d["oi_pct"]), LONG_U)

    def test_non_futures_rows_ignored_and_zero_base_guard(self):
        rows = [{"FinInstrmTp": "STO", "TckrSymb": "XYZ"}, stf("QQQ", "2026-11-23", 10, 10, 0, 0)]
        out = summarize(rows)
        self.assertNotIn("XYZ", out)
        self.assertIsNone(out["QQQ"]["oi_pct"])


class Streak(unittest.TestCase):
    H = frozenset({"2026-11-10"})   # a made-up holiday

    def test_same_label_next_trading_day_adds_one(self):
        self.assertEqual(next_streak(LONG_B, "2026-10-29", 1, LONG_B, "2026-10-30", self.H), 2)

    def test_different_label_resets(self):
        self.assertEqual(next_streak(LONG_B, "2026-10-29", 4, SHORT_B, "2026-10-30", self.H), 1)

    def test_same_date_rerun_is_skipped(self):
        self.assertIsNone(next_streak(LONG_B, "2026-10-30", 3, LONG_B, "2026-10-30", self.H))
        self.assertIsNone(next_streak(LONG_B, "2026-10-30", 3, SHORT_B, "2026-10-29", self.H))

    def test_weekend_gap_still_consecutive(self):
        self.assertEqual(next_streak(LONG_B, "2026-10-30", 2, LONG_B, "2026-11-02", self.H), 3)   # Fri -> Mon

    def test_holiday_gap_still_consecutive(self):
        self.assertEqual(next_streak(LONG_B, "2026-11-09", 2, LONG_B, "2026-11-11", self.H), 3)   # Mon -> Wed, Tue is a holiday

    def test_missed_trading_day_resets(self):
        self.assertEqual(next_streak(LONG_B, "2026-10-28", 5, LONG_B, "2026-10-30", self.H), 1)   # Thu not recorded

    def test_no_previous_value(self):
        self.assertEqual(next_streak("", "", "", LONG_B, "2026-10-30", self.H), 1)


class Board(unittest.TestCase):
    def test_median_ratio_and_mood(self):
        stocks = [("A", "Auto"), ("B", "Auto"), ("C", "Auto"), ("D", "IT"), ("E", "IT")]
        labels = {"A": LONG_B, "B": SHORT_C, "C": SHORT_B, "D": SHORT_B, "E": LONG_U}
        r1d = {"A": 1.0, "B": 2.0, "C": 50.0, "D": -1.0, "E": -2.0}
        r1w = {"A": 3.0, "B": 2.0, "C": 1.0, "D": -3.0, "E": -2.0}
        rows = {r[0]: r for r in sector_rows(stocks, labels, r1d, r1w, {}, "2026-10-30")}
        self.assertEqual(rows["Auto"][2], 2.0)             # median, the 50% outlier does not dominate
        self.assertAlmostEqual(rows["Auto"][9], 66.7, places=1)
        self.assertEqual(rows["Auto"][10], "🟢 Strong")
        self.assertEqual(rows["IT"][10], "🔴 Weak")

    def test_mood_edges(self):
        self.assertEqual(mood(60, 0.1), "🟢 Strong")
        self.assertEqual(mood(60, 0.0), "🟡 Mixed")
        self.assertEqual(mood(40, -0.1), "🔴 Weak")
        self.assertEqual(mood(None, 1), "🟡 Mixed")


class Forward(unittest.TestCase):
    D = ["2026-10-27", "2026-10-28", "2026-10-29", "2026-10-30", "2026-11-02", "2026-11-03"]
    C = [100.0, 101.0, 102.0, 100.0, 105.0, 110.0]

    def test_returns(self):
        self.assertEqual(fwd_ret(self.D, self.C, "2026-10-30", 1), 5.0)
        self.assertEqual(fwd_ret(self.D, self.C, "2026-10-30", 2), 10.0)
        self.assertEqual(fwd_ret(self.D, self.C, "2026-10-28", 3), 3.96)   # 105 / 101 - 1

    def test_not_available_yet(self):
        self.assertIsNone(fwd_ret(self.D, self.C, "2026-10-30", 3))
        self.assertIsNone(fwd_ret(self.D, self.C, "2026-12-01", 1))


if __name__ == "__main__":
    unittest.main()
