from __future__ import annotations

import unittest

from stwl_camper_suite.tow_physics import Light, grade_combination


class TowTrafficLightTests(unittest.TestCase):
    def test_green_comfortable_margins(self) -> None:
        r = grade_combination(
            truck_as_weighed=7000,
            truck_gvwr=10000,
            truck_gcwr=25000,
            truck_payload_capacity=3000,
            max_trailer_weight_rating=14000,
            max_tongue_or_pin_rating=1400,
            trailer_as_weighed=8000,
            trailer_gvwr=12000,
            tongue_or_pin_weight=1000,  # 12.5% of 8000
            hitch_style="conventional",
            passengers_and_cargo_in_truck=400,
        )
        self.assertEqual(r.overall, Light.GREEN)

    def test_red_over_gcwr(self) -> None:
        r = grade_combination(
            truck_as_weighed=9000,
            truck_gvwr=10000,
            truck_gcwr=15000,
            truck_payload_capacity=2000,
            max_trailer_weight_rating=14000,
            max_tongue_or_pin_rating=1500,
            trailer_as_weighed=8000,
            tongue_or_pin_weight=1000,
            hitch_style="conventional",
            passengers_and_cargo_in_truck=200,
        )
        self.assertEqual(r.overall, Light.RED)
        self.assertTrue(any(c.id == "gcwr" and c.light == Light.RED for c in r.checks))

    def test_red_over_max_trailer(self) -> None:
        r = grade_combination(
            truck_as_weighed=7000,
            truck_gvwr=10000,
            truck_gcwr=30000,
            max_trailer_weight_rating=5000,
            trailer_as_weighed=8000,
            tongue_or_pin_weight=900,
            truck_payload_capacity=3000,
            max_tongue_or_pin_rating=1500,
        )
        self.assertEqual(r.overall, Light.RED)

    def test_incomplete_without_weights(self) -> None:
        r = grade_combination(truck_gcwr=20000, max_trailer_weight_rating=10000)
        self.assertEqual(r.overall, Light.GRAY)
        self.assertTrue(r.credits)


if __name__ == "__main__":
    unittest.main()
