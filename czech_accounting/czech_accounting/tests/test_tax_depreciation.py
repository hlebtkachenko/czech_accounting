# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""Czech tax depreciation (§ 31 rovnoměrné / § 32 zrychlené) produces statutory amounts,
not a straight line. Values checked against Act 586/1992 Annex 1 + the worked KB examples.
"""
import unittest

from czech_accounting.assets.tax_depreciation import (
    MIN_PERIOD_YEARS,
    accelerated_schedule,
    linear_schedule,
    tax_depreciation_schedule,
)


class TestTaxDepreciation(unittest.TestCase):
    def test_group2_linear_matches_statute(self):
        # KB: group 2 (car), cost 500 000 -> year 1 at 11 %, years 2-5 at 22.25 %.
        self.assertEqual(
            linear_schedule(500_000, 2), [55_000, 111_250, 111_250, 111_250, 111_250]
        )

    def test_group2_accelerated_matches_statute(self):
        # KB: 500 000 / 5, then 2*ZC / (6 - n).
        self.assertEqual(
            accelerated_schedule(500_000, 2), [100_000, 160_000, 120_000, 80_000, 40_000]
        )

    def test_year1_differs_from_later_years(self):
        s = linear_schedule(500_000, 2)
        self.assertLess(s[0], s[1])  # the § 31 point: year-1 rate is lower than year-2+

    def test_accelerated_front_loads_then_declines(self):
        s = accelerated_schedule(500_000, 2)
        self.assertGreater(s[1], s[0])
        self.assertGreater(s[1], s[-1])

    def test_every_group_and_method_sums_to_cost(self):
        for group in MIN_PERIOD_YEARS:
            for method in ("linear", "accelerated"):
                s = tax_depreciation_schedule(1_234_567, group, method)
                self.assertEqual(len(s), MIN_PERIOD_YEARS[group])
                self.assertEqual(sum(s), 1_234_567)

    def test_not_a_straight_line(self):
        # regression: the old CZ-Daňové book used ERPNext straight line (flat) — wrong.
        for method in ("linear", "accelerated"):
            self.assertGreater(len(set(tax_depreciation_schedule(300_000, 2, method))), 1)

    def test_unknown_group_or_method_raises(self):
        with self.assertRaises(ValueError):
            tax_depreciation_schedule(100_000, 7, "linear")
        with self.assertRaises(ValueError):
            tax_depreciation_schedule(100_000, 2, "double-declining")


if __name__ == "__main__":
    unittest.main()
