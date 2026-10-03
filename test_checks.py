import argparse
import unittest
from decimal import Decimal as D

from checks import check_total, number, percent_change, speed_change


class ArithmeticChecks(unittest.TestCase):
    def test_wrong_total_is_not_hidden(self):
        self.assertEqual(check_total([D("700"), D("800")], D("1800")), (D("1500"), D("300")))

    def test_decimal_amounts_and_negative_adjustment(self):
        self.assertEqual(check_total([D("0.1"), D("0.2")], D("0.3")), (D("0.3"), D("0")))
        self.assertEqual(check_total([D("10"), D("-2.5")], D("7.5")), (D("7.5"), D("0")))

    def test_points_are_different_from_relative_percent(self):
        self.assertEqual(percent_change(D("2"), D("3")), (D("1"), D("50")))
        self.assertEqual(percent_change(D("3"), D("2"))[0], D("-1"))

    def test_zero_baseline_has_no_relative_percent(self):
        self.assertEqual(percent_change(D("0"), D("3")), (D("3"), None))

    def test_share_bounds(self):
        for before, after in [("-1", "2"), ("2", "101")]:
            with self.assertRaises(ValueError):
                percent_change(D(before), D(after))

    def test_one_fast_stage_does_not_make_everything_eight_times_faster(self):
        before, after, reduction, multiplier = speed_change(D("8"), D("32"), D("8"))
        self.assertEqual((before, after, reduction), (D("40"), D("33"), D("17.5")))
        self.assertEqual(multiplier, D("40") / D("33"))

    def test_unchanged_stage_and_slower_stage(self):
        self.assertEqual(speed_change(D("0"), D("32"), D("8")), (D("32"), D("32"), D("0"), D("1")))
        self.assertEqual(speed_change(D("8"), D("32"), D("0.5"))[:3], (D("40"), D("48"), D("-20")))

    def test_invalid_times_and_factor(self):
        for generation, other, factor in [("-1", "1", "8"), ("1", "-1", "8"), ("0", "0", "8"), ("1", "1", "0")]:
            with self.assertRaises(ValueError):
                speed_change(D(generation), D(other), D(factor))

    def test_nonfinite_and_nonnumber_cli_input(self):
        for text in ["NaN", "Infinity", "-Infinity", "hello"]:
            with self.assertRaises(argparse.ArgumentTypeError):
                number(text)


if __name__ == "__main__":
    unittest.main()
