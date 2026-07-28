"""
Vehicle / axle configuration catalogs (1920–present).

These are *selection lists and discovery indexes*, not invented tow or axle
rating tables. Ratings always come from labels / manufacturer literature
entered by the user, with publisher credit.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .paths import content_dir, project_root

YEAR_MIN = 1920
YEAR_MAX = 2026  # update as calendar advances

# Axle count labels (1 = single … 5 = quint)
AXLE_COUNT_OPTIONS = [
    (1, "Single axle (1)"),
    (2, "Tandem (2)"),
    (3, "Triple (3)"),
    (4, "Quad (4)"),
    (5, "Quint (5)"),
]

WHEEL_END_OPTIONS = [
    ("single", "Single wheel (one tire per side per axle)"),
    ("dual", "Dual wheel / dually (two tires per side per axle)"),
]

BRAKE_TYPE_OPTIONS = [
    ("none", "No brakes (where lawful — light only)"),
    ("electric", "Electric (magnet drum — common light/medium trailer)"),
    ("electric_over_hydraulic", "Electric-over-hydraulic (EoH)"),
    ("hydraulic_surge", "Hydraulic surge"),
    ("air", "Air brakes (medium / heavy duty, often Class 6–8 power units)"),
    ("air_disc", "Air disc"),
    ("other", "Other / mixed (describe in notes)"),
]

HITCH_STYLE_OPTIONS = [
    ("conventional", "Conventional / bumper pull / gooseneck ball on bumper-style"),
    ("weight_distribution", "Weight-distribution hitch (ball)"),
    ("fifth_wheel", "Fifth wheel"),
    ("gooseneck", "Gooseneck"),
    ("pintle", "Pintle"),
    ("other", "Other"),
]

# Common trailer axle brand names for dropdown (user still enters GAWR from plate)
AXLE_MANUFACTURERS = [
    "Dexter Axle",
    "Lippert / LCI",
    "AL-KO / AL-KO Kober",
    "Hayes Axle",
    "Rockwell American",
    "Timbren",
    "Quality Trailer Products",
    "UFP / Unique Functional Products",
    "Tie Down Engineering",
    "Meritor (commercial)",
    "Hendrickson (commercial / suspension)",
    "SAF-Holland (commercial)",
    "Ingersoll (specialty)",
    "Homemade / unknown",
    "Other (specify in notes)",
]

# Truck make families spanning ~1920–present for power-unit picker (not ratings)
POWER_UNIT_MAKES = [
    "Ford",
    "Chevrolet",
    "GMC",
    "Dodge",
    "Ram",
    "Plymouth (legacy)",
    "Jeep",
    "International / Navistar",
    "Kenworth",
    "Peterbilt",
    "Freightliner",
    "Mack",
    "Volvo Trucks",
    "Western Star",
    "Autocar",
    "Hino",
    "Isuzu",
    "Mitsubishi Fuso",
    "Toyota",
    "Nissan",
    "Honda",
    "Studebaker (legacy)",
    "Willys (legacy)",
    "Reo (legacy)",
    "Diamond T (legacy)",
    "White (legacy)",
    "Brockway (legacy)",
    "Custom / Homemade power unit",
    "Other",
]

POWER_UNIT_CLASSES = [
    ("light", "Light duty (approx. Class 1–2)"),
    ("medium", "Medium duty (approx. Class 3–6)"),
    ("heavy", "Heavy duty / Class 7–8"),
    ("unknown", "Unknown / mixed"),
]


def year_choices(lo: int = YEAR_MIN, hi: int = YEAR_MAX) -> list[int]:
    return list(range(hi, lo - 1, -1))


def _yaml_path(*parts: str) -> Path:
    p = content_dir().joinpath(*parts)
    if p.is_file():
        return p
    return project_root().joinpath("content", *parts)


def load_truck_era_index() -> list[dict[str, Any]]:
    path = _yaml_path("oem_tow_reference", "truck_eras.yaml")
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    eras = data.get("eras") or []
    return [e for e in eras if isinstance(e, dict)]


def load_axle_manufacturer_index() -> list[dict[str, Any]]:
    path = _yaml_path("oem_tow_reference", "axle_manufacturers.yaml")
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    items = data.get("manufacturers") or []
    return [m for m in items if isinstance(m, dict) and m.get("name")]
