from __future__ import annotations

import unittest

from stwl_camper_suite.vin_lookup import (
    normalize_vin,
    offline_vin_check,
    validate_check_digit,
    _sanitize_unit_fields,
)


class VinUnitOnlyTests(unittest.TestCase):
    def test_normalize(self) -> None:
        self.assertEqual(normalize_vin(" 1hgcm 82633-a004352 "), "1HGCM82633A004352")

    def test_check_digit_known_valid(self) -> None:
        # Public example VIN used widely in decoder demos (Honda)
        vin = "1HGCM82633A004352"
        self.assertTrue(validate_check_digit(vin))

    def test_offline_bad_char(self) -> None:
        r = offline_vin_check("1HGCM82633A00435I")  # I invalid
        self.assertFalse(r.ok_format)

    def test_sanitize_keeps_plant_drops_owner(self) -> None:
        raw = {
            "Make": "FORD",
            "Model": "F-350",
            "ModelYear": "2018",
            "PlantCity": "Louisville",
            "PlantState": "Kentucky",
            "PlantCountry": "UNITED STATES (USA)",
            "PlantCompanyName": "Kentucky Truck Plant",
            "OwnerName": "SHOULD DROP",
            "DriveType": "4WD",
        }
        unit = _sanitize_unit_fields(raw)
        self.assertEqual(unit.get("make"), "FORD")
        self.assertEqual(unit.get("model"), "F-350")
        self.assertEqual(unit.get("plant_city"), "Louisville")
        self.assertEqual(unit.get("plant_state"), "Kentucky")
        self.assertEqual(unit.get("plant_company"), "Kentucky Truck Plant")
        self.assertNotIn("OwnerName", unit)
        self.assertTrue(all("owner" not in k.lower() for k in unit))


if __name__ == "__main__":
    unittest.main()
