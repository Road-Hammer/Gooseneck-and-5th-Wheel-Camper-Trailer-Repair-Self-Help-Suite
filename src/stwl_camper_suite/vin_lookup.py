"""
Optional VIN validation / decode — UNIT technical info only.

Offline: ISO 3779-style check digit (17-character VIN).
Online (optional): free U.S. NHTSA vPIC DecodeVinValues API — no API key,
no registration. See https://vpic.nhtsa.dot.gov/api/

PRIVACY RULE (STWL):
  Never request, store, or display owner names, personal addresses, or other PII.
  Only vehicle / unit technical attributes. Plant street addresses from vPIC are
  discarded; we keep no owner identity fields.

Credit: U.S. Department of Transportation / National Highway Traffic Safety
Administration (NHTSA) — Vehicle Product Information Catalog (vPIC).
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

# Free public NHTSA vPIC endpoint (no key)
NHTSA_DECODE_URL = (
    "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"
)

NHTSA_CREDIT = (
    "Publisher / data source: U.S. Department of Transportation, "
    "National Highway Traffic Safety Administration (NHTSA) — "
    "Vehicle Product Information Catalog (vPIC) API "
    "(https://vpic.nhtsa.dot.gov/api/). Free public service; not affiliated with STWL."
)

# Map vPIC flat keys → our unit-only field names (whitelist)
# Anything not listed is dropped (including PlantCity, PlantState, error messages noise).
_UNIT_FIELD_MAP = {
    "Make": "make",
    "Model": "model",
    "ModelYear": "year",
    "Trim": "trim",
    "Series": "series",
    "BodyClass": "body_class",
    "VehicleType": "vehicle_type",
    "DriveType": "drivetrain",
    "EngineModel": "engine",
    "EngineCylinders": "engine_cylinders",
    "DisplacementL": "engine_displacement_l",
    "FuelTypePrimary": "fuel_type",
    "TransmissionStyle": "transmission",
    "GVWR": "gvwr_text",  # often a class string, not lb
    "TrailerTypeConnection": "trailer_connection",
    "PlantCountry": "plant_country",  # country only — not street address
    "Manufacturer": "manufacturer",
    "ErrorCode": "error_code",
    "ErrorText": "error_text",
    "AdditionalErrorText": "additional_error_text",
}

# Explicit denylist fragments (case-insensitive) — never pass through
_DENY_KEYS = re.compile(
    r"name|address|street|city|state|zip|postal|phone|email|owner|person|"
    r"contact|ssn|license|registration",
    re.I,
)

_VIN_RE = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$", re.I)

# Transliteration for check digit (ISO 3779)
_TRANSLIT = {
    **{str(i): i for i in range(10)},
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8,
    "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "P": 7, "R": 9,
    "S": 2, "T": 3, "U": 4, "V": 5, "W": 6, "X": 7, "Y": 8, "Z": 9,
}
_WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]


@dataclass
class VinResult:
    vin: str
    ok_format: bool
    check_digit_ok: bool | None  # None if not 17-char modern VIN
    offline_notes: list[str] = field(default_factory=list)
    online: bool = False
    online_error: str | None = None
    unit: dict[str, Any] = field(default_factory=dict)
    credits: list[str] = field(default_factory=list)
    # Fields safe to prefill power-unit form (unit only)
    suggest: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "vin": self.vin,
            "ok_format": self.ok_format,
            "check_digit_ok": self.check_digit_ok,
            "offline_notes": self.offline_notes,
            "online": self.online,
            "online_error": self.online_error,
            "unit": self.unit,
            "credits": self.credits,
            "suggest": self.suggest,
        }


def normalize_vin(raw: str) -> str:
    return re.sub(r"[\s\-]", "", (raw or "").strip().upper())


def validate_check_digit(vin: str) -> bool | None:
    """Return True/False for 17-char VIN check digit; None if not applicable."""
    vin = normalize_vin(vin)
    if len(vin) != 17:
        return None
    if not _VIN_RE.match(vin):
        return False
    total = 0
    for i, ch in enumerate(vin):
        if ch not in _TRANSLIT:
            return False
        total += _TRANSLIT[ch] * _WEIGHTS[i]
    remainder = total % 11
    expect = "X" if remainder == 10 else str(remainder)
    return vin[8] == expect


def offline_vin_check(vin_raw: str) -> VinResult:
    vin = normalize_vin(vin_raw)
    notes: list[str] = []
    credits = [
        "Offline check-digit validation: STWL implementation of ISO 3779 VIN check digit.",
        "No personal names or addresses are collected for VIN checks.",
    ]
    if not vin:
        return VinResult(
            vin="",
            ok_format=False,
            check_digit_ok=None,
            offline_notes=["No VIN entered."],
            credits=credits,
        )
    if len(vin) < 17:
        notes.append(
            f"Length {len(vin)} (modern road vehicles use 17 characters). "
            "Pre-1981 or non-standard serials may be shorter — unit serial only; no online decode assumed."
        )
        return VinResult(
            vin=vin,
            ok_format=bool(re.match(r"^[A-HJ-NPR-Z0-9]+$", vin, re.I)),
            check_digit_ok=None,
            offline_notes=notes,
            credits=credits,
        )
    if len(vin) > 17:
        notes.append("Longer than 17 characters — not a standard VIN.")
        return VinResult(
            vin=vin,
            ok_format=False,
            check_digit_ok=False,
            offline_notes=notes,
            credits=credits,
        )
    if not _VIN_RE.match(vin):
        notes.append("Invalid characters (I, O, Q are not used in modern VINs).")
        return VinResult(
            vin=vin,
            ok_format=False,
            check_digit_ok=False,
            offline_notes=notes,
            credits=credits,
        )
    cd = validate_check_digit(vin)
    if cd is True:
        notes.append("Check digit OK (format valid).")
    elif cd is False:
        notes.append("Check digit FAILED — possible typo; still unit-only, no personal data.")
    return VinResult(
        vin=vin,
        ok_format=True,
        check_digit_ok=cd,
        offline_notes=notes,
        credits=credits,
    )


def _sanitize_unit_fields(raw: dict[str, Any]) -> dict[str, str]:
    """Whitelist unit fields only; drop names/addresses/PII-like keys."""
    out: dict[str, str] = {}
    for k, v in raw.items():
        if v is None:
            continue
        key = str(k)
        if _DENY_KEYS.search(key):
            continue
        # Drop plant city/state (address-like)
        if key.lower() in (
            "plantcity",
            "plantstate",
            "plantcompanyname",
            "destinationmarket",
        ):
            continue
        if key not in _UNIT_FIELD_MAP and key not in _UNIT_FIELD_MAP.values():
            # only allow known unit map keys
            if key not in _UNIT_FIELD_MAP:
                continue
        val = str(v).strip()
        if not val or val.upper() in ("NULL", "NOT APPLICABLE", "N/A", ""):
            continue
        # Reject values that look like street addresses
        if re.search(r"\b\d{1,5}\s+\w+\s+(st|street|ave|road|rd|blvd|drive|dr)\b", val, re.I):
            continue
        mapped = _UNIT_FIELD_MAP.get(key, key)
        if _DENY_KEYS.search(mapped):
            continue
        out[mapped] = val
    return out


def decode_vin_nhtsa(vin_raw: str, timeout: float = 8.0) -> VinResult:
    """
    Offline check + optional NHTSA vPIC decode (requires network).
    Returns unit technical fields only.
    """
    base = offline_vin_check(vin_raw)
    if not base.vin or len(base.vin) != 17 or not base.ok_format:
        base.online_error = "Online decode skipped — need a 17-character valid-format VIN."
        return base

    url = NHTSA_DECODE_URL.format(vin=base.vin)
    base.credits.append(NHTSA_CREDIT)
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "STWL-CamperSuite/0.2 (unit-info-only; offline-first)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        base.online_error = f"Network unavailable or NHTSA unreachable: {e.reason!s}"
        return base
    except TimeoutError:
        base.online_error = "NHTSA request timed out."
        return base
    except Exception as e:  # noqa: BLE001
        base.online_error = f"Decode failed: {e}"
        return base

    results = payload.get("Results") or []
    if not results:
        base.online_error = "NHTSA returned no results."
        return base
    row = results[0]
    if not isinstance(row, dict):
        base.online_error = "Unexpected NHTSA payload."
        return base

    unit = _sanitize_unit_fields(row)
    # Prefer cleaner suggest map for form prefill
    suggest: dict[str, str] = {}
    if unit.get("make"):
        suggest["make"] = unit["make"]
    if unit.get("model"):
        suggest["model"] = unit["model"]
    if unit.get("year"):
        suggest["year"] = unit["year"]
    if unit.get("trim"):
        suggest["trim"] = unit["trim"]
    eng_bits = [
        unit.get("engine"),
        unit.get("engine_cylinders") and f"{unit['engine_cylinders']} cyl",
        unit.get("engine_displacement_l") and f"{unit['engine_displacement_l']}L",
        unit.get("fuel_type"),
    ]
    eng = " ".join(x for x in eng_bits if x)
    if eng:
        suggest["engine"] = eng
    if unit.get("drivetrain"):
        suggest["drivetrain"] = unit["drivetrain"]
    cfg = " · ".join(
        x
        for x in (
            unit.get("body_class"),
            unit.get("vehicle_type"),
            unit.get("series"),
            unit.get("transmission"),
            unit.get("gvwr_text") and f"GVWR class: {unit['gvwr_text']}",
        )
        if x
    )
    if cfg:
        suggest["config_notes"] = cfg

    err = unit.get("error_text") or unit.get("error_code")
    if err and str(err) not in ("0", "0,"):
        base.offline_notes.append(f"NHTSA message: {err}")

    base.online = True
    base.unit = unit
    base.suggest = suggest
    base.offline_notes.append(
        "Online decode: unit technical fields only (no owner names or addresses)."
    )
    return base


def lookup_vin(vin_raw: str, *, online: bool = True) -> VinResult:
    """Public entry: offline always; online NHTSA if online=True."""
    if online:
        return decode_vin_nhtsa(vin_raw)
    return offline_vin_check(vin_raw)
