"""
Combination tow acceptance — traffic-light grade.

Uses measured/entered weights and *user-supplied* OEM ratings (door sticker /
owner manual / official OEM tow guide for that exact config). Does not invent
manufacturer model charts.

Rule basis is documented in each CheckResult.basis for publisher credit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Light(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    GRAY = "gray"  # insufficient data for that check


# Severity order for overall grade
_LIGHT_RANK = {Light.GREEN: 0, Light.GRAY: 1, Light.YELLOW: 2, Light.RED: 3}


@dataclass
class CheckResult:
    id: str
    title: str
    light: Light
    detail: str
    basis: str  # credited rule / publisher basis


@dataclass
class TowGradeResult:
    overall: Light
    label: str
    summary: str
    checks: list[CheckResult] = field(default_factory=list)
    numbers: dict[str, Any] = field(default_factory=dict)
    credits: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall.value,
            "label": self.label,
            "summary": self.summary,
            "checks": [
                {
                    "id": c.id,
                    "title": c.title,
                    "light": c.light.value,
                    "detail": c.detail,
                    "basis": c.basis,
                }
                for c in self.checks
            ],
            "numbers": self.numbers,
            "credits": self.credits,
            "missing_inputs": self.missing_inputs,
        }


# Industry common tongue/pin fractions — advisory only (OEM/hitch maker may differ)
CONVENTIONAL_TONGUE_MIN = 0.10
CONVENTIONAL_TONGUE_MAX = 0.15
FIFTH_GOOSENECK_PIN_MIN = 0.15
FIFTH_GOOSENECK_PIN_MAX = 0.25

# Margin under a limit still treated as "tight" → yellow (fraction of headroom used)
TIGHT_MARGIN_FRACTION = 0.90  # using ≥90% of a limit is yellow if not over


CREDITS = [
    "Grading logic & original software: Susquehanna Timberwolf Lines, LLC (STWL)",
    "Rating definitions (GVWR, GCWR, payload, max trailer weight): vehicle manufacturer "
    "owner literature / door certification label — reader must use values for their exact vehicle",
    "Official OEM tow guides (examples of publisher portals, not copied tables): "
    "Ford Motor Company (ford.com towing / RV & Trailer Towing Guide); "
    "Ram Trucks (ramtrucks.com towing capacity guide); "
    "General Motors / Chevrolet / GMC trailering guides — consult current OEM PDF/tools for your model year",
    "Tongue-weight percentage bands used as advisory only: widely taught industry ranges "
    "(~10–15% conventional; higher pin-weight share typical for many 5th-wheel/gooseneck setups). "
    "Prefer hitch manufacturer and OEM guidance for your equipment.",
    "Axle GAWR / aggregate axle capacity: axle manufacturer certification (e.g. Dexter, Lippert, "
    "commercial axle makers) and trailer certification label — user-entered plate values only.",
]


def _f(v: Any) -> float | None:
    if v is None or v == "":
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    if x < 0:
        return None
    return x


def _worst(*lights: Light) -> Light:
    best = Light.GREEN
    for L in lights:
        if _LIGHT_RANK[L] > _LIGHT_RANK[best]:
            best = L
    return best


def _limit_light(used: float, limit: float) -> Light:
    if used > limit + 1e-6:
        return Light.RED
    if limit <= 0:
        return Light.GRAY
    if used / limit >= TIGHT_MARGIN_FRACTION:
        return Light.YELLOW
    return Light.GREEN


def grade_combination(
    *,
    # Power unit (truck) — as configured for the trip
    truck_as_weighed: float | None = None,  # scale weight of truck alone, ready to tow
    truck_gvwr: float | None = None,
    truck_gcwr: float | None = None,
    truck_payload_capacity: float | None = None,  # from door sticker
    truck_curb_or_empty: float | None = None,  # optional if payload derived
    max_trailer_weight_rating: float | None = None,  # OEM max trailer for this config
    max_tongue_or_pin_rating: float | None = None,  # truck/hitch max vertical load
    hitch_receiver_rating: float | None = None,  # optional second vertical limit
    # Trailer
    trailer_as_weighed: float | None = None,  # loaded trailer preferred
    trailer_gvwr: float | None = None,
    tongue_or_pin_weight: float | None = None,  # measured preferred
    hitch_style: str = "conventional",  # conventional | fifth_wheel | gooseneck
    # Axle system (homemade or OEM trailer) — ratings from axle/trailer plates
    axle_count: int | None = None,  # 1–5 (quint)
    aggregate_axle_gawr: float | None = None,  # sum of axle GAWRs when known
    # Cargo in truck bed/cab not already in truck_as_weighed (if truck is empty scale)
    passengers_and_cargo_in_truck: float | None = None,
) -> TowGradeResult:
    """
    Return traffic-light grade for whether this power unit is acceptable
    for the intended trailer combination.
    """
    hitch_style = (hitch_style or "conventional").strip().lower()
    if hitch_style in ("5th", "5th_wheel", "fifth", "5thwheel"):
        hitch_style = "fifth_wheel"
    if hitch_style in ("gn", "goose"):
        hitch_style = "gooseneck"

    checks: list[CheckResult] = []
    missing: list[str] = []

    # --- Derive truck trip weight ---
    truck_trip = truck_as_weighed
    if truck_trip is None and truck_curb_or_empty is not None:
        pac = passengers_and_cargo_in_truck or 0.0
        # Tongue is part of trailer scale if trailer_as_weighed is full trailer on scale;
        # vertical load on truck is added when we have tongue weight.
        truck_trip = truck_curb_or_empty + pac
    if truck_trip is None:
        missing.append("Truck weight (scale weight ready-to-tow, or curb + passengers/cargo)")

    trailer_trip = trailer_as_weighed
    if trailer_trip is None and trailer_gvwr is not None:
        # Conservative: assume trailer can be loaded to GVWR if not weighed
        trailer_trip = trailer_gvwr
        checks.append(
            CheckResult(
                id="trailer_weight_assumed",
                title="Trailer weight assumed at GVWR",
                light=Light.YELLOW,
                detail=(
                    f"No trailer scale weight entered; using trailer GVWR "
                    f"({trailer_gvwr:.0f} lb) as a conservative stand-in. "
                    "Weigh the loaded trailer for a real grade."
                ),
                basis="STWL conservative assumption when measured trailer weight is missing.",
            )
        )
    if trailer_trip is None:
        missing.append("Trailer weight (loaded scale weight preferred, or trailer GVWR)")

    # Combined
    combined = None
    if truck_trip is not None and trailer_trip is not None:
        # If tongue is known and truck_as_weighed was truck-only without tongue,
        # combined = truck + trailer is correct when trailer is full trailer weight
        # (tongue is part of trailer weight, not double-counted).
        combined = truck_trip + trailer_trip
        # If truck_as_weighed already included tongue (truck+trailer coupled on scale),
        # user should enter that as combined differently — we document: enter truck alone + trailer alone.

    numbers: dict[str, Any] = {
        "truck_trip_lb": truck_trip,
        "trailer_trip_lb": trailer_trip,
        "combined_lb": combined,
        "hitch_style": hitch_style,
        "tongue_or_pin_lb": tongue_or_pin_weight,
        "axle_count": axle_count,
        "aggregate_axle_gawr_lb": aggregate_axle_gawr,
    }

    # 1) GCWR
    if combined is not None and truck_gcwr is not None:
        L = _limit_light(combined, truck_gcwr)
        head = truck_gcwr - combined
        checks.append(
            CheckResult(
                id="gcwr",
                title="Gross Combined Weight Rating (GCWR)",
                light=L,
                detail=(
                    f"Combined ≈ {combined:.0f} lb vs GCWR {truck_gcwr:.0f} lb "
                    f"(headroom {head:.0f} lb)."
                    + (" OVER GCWR." if L == Light.RED else "")
                    + (" Tight margin (≥90% of GCWR)." if L == Light.YELLOW else "")
                ),
                basis=(
                    "GCWR is the manufacturer maximum for truck + trailer + cargo. "
                    "Definition as used in OEM tow literature (e.g. Ford RV & Trailer Towing Guide; "
                    "Ram / GM trailering materials). Value must come from your vehicle’s OEM data."
                ),
            )
        )
    elif truck_gcwr is None:
        missing.append("Truck GCWR (OEM)")
        checks.append(
            CheckResult(
                id="gcwr",
                title="Gross Combined Weight Rating (GCWR)",
                light=Light.GRAY,
                detail="GCWR not entered — cannot complete combined-weight check.",
                basis="OEM door sticker / owner manual / official tow guide for exact config.",
            )
        )

    # 2) Max trailer weight rating
    if trailer_trip is not None and max_trailer_weight_rating is not None:
        L = _limit_light(trailer_trip, max_trailer_weight_rating)
        checks.append(
            CheckResult(
                id="max_trailer",
                title="OEM maximum trailer weight",
                light=L,
                detail=(
                    f"Trailer ≈ {trailer_trip:.0f} lb vs OEM max trailer "
                    f"{max_trailer_weight_rating:.0f} lb."
                    + (" EXCEEDS OEM trailer rating." if L == Light.RED else "")
                ),
                basis=(
                    "Maximum trailer weight is config-specific (engine, axle, package, cab/bed). "
                    "Source: vehicle manufacturer tow guide or calculator for that VIN/config "
                    "(Ford, Ram, GM, Toyota, etc. — official publisher materials)."
                ),
            )
        )
    elif max_trailer_weight_rating is None:
        missing.append("OEM max trailer weight rating for this power unit config")
        checks.append(
            CheckResult(
                id="max_trailer",
                title="OEM maximum trailer weight",
                light=Light.GRAY,
                detail="No OEM max trailer rating entered.",
                basis="Required from official OEM tow data for the exact truck configuration.",
            )
        )

    # 3) Truck GVWR (truck alone as weighed for trip — without trailer tongue if truck-only scale)
    # If we have tongue weight, truck on road with trailer sees truck_trip + tongue for axle load estimate.
    truck_on_road = truck_trip
    if truck_trip is not None and tongue_or_pin_weight is not None:
        # If truck_as_weighed was truck-only, add vertical coupling load for on-road truck mass estimate
        truck_on_road = truck_trip + tongue_or_pin_weight
        numbers["truck_on_road_est_lb"] = truck_on_road

    if truck_on_road is not None and truck_gvwr is not None:
        L = _limit_light(truck_on_road, truck_gvwr)
        checks.append(
            CheckResult(
                id="gvwr",
                title="Truck GVWR (with coupling load if known)",
                light=L,
                detail=(
                    f"Estimated truck side load ≈ {truck_on_road:.0f} lb vs GVWR {truck_gvwr:.0f} lb."
                    + (
                        " Includes tongue/pin weight added to truck-only weight."
                        if tongue_or_pin_weight is not None
                        else " Enter tongue/pin weight for a better GVWR check."
                    )
                ),
                basis=(
                    "GVWR is the manufacturer maximum loaded weight of the tow vehicle. "
                    "Door certification label / OEM literature."
                ),
            )
        )
    elif truck_gvwr is None:
        missing.append("Truck GVWR")

    # 4) Payload vs tongue/pin + in-truck cargo
    # payload remaining ≈ payload_capacity - (truck_trip - curb) roughly;
    # simpler: if payload_capacity and tongue and passengers known:
    if truck_payload_capacity is not None and tongue_or_pin_weight is not None:
        in_truck = passengers_and_cargo_in_truck
        if in_truck is None and truck_as_weighed is not None and truck_curb_or_empty is not None:
            in_truck = max(0.0, truck_as_weighed - truck_curb_or_empty)
        if in_truck is None:
            in_truck = 0.0
            payload_note = " (assuming 0 lb extra cabin/bed cargo beyond truck weight entry)"
        else:
            payload_note = ""
        payload_used = in_truck + tongue_or_pin_weight
        L = _limit_light(payload_used, truck_payload_capacity)
        checks.append(
            CheckResult(
                id="payload",
                title="Payload vs people/cargo + tongue/pin",
                light=L,
                detail=(
                    f"Payload used ≈ {payload_used:.0f} lb "
                    f"(in-truck {in_truck:.0f} + tongue/pin {tongue_or_pin_weight:.0f}) "
                    f"vs payload capacity {truck_payload_capacity:.0f} lb.{payload_note}"
                ),
                basis=(
                    "Payload capacity from the tire/loading placard or OEM. "
                    "Tongue/pin weight counts against truck payload when coupled."
                ),
            )
        )
    else:
        if truck_payload_capacity is None:
            missing.append("Truck payload capacity")
        if tongue_or_pin_weight is None:
            missing.append("Tongue or pin weight (measure with scale/gauge)")
        checks.append(
            CheckResult(
                id="payload",
                title="Payload vs people/cargo + tongue/pin",
                light=Light.GRAY,
                detail="Need payload capacity and tongue/pin weight for this check.",
                basis="OEM payload + measured coupling load.",
            )
        )

    # 5) Hitch / max tongue rating
    vert_limit = None
    if max_tongue_or_pin_rating is not None and hitch_receiver_rating is not None:
        vert_limit = min(max_tongue_or_pin_rating, hitch_receiver_rating)
    elif max_tongue_or_pin_rating is not None:
        vert_limit = max_tongue_or_pin_rating
    elif hitch_receiver_rating is not None:
        vert_limit = hitch_receiver_rating

    if tongue_or_pin_weight is not None and vert_limit is not None:
        L = _limit_light(tongue_or_pin_weight, vert_limit)
        checks.append(
            CheckResult(
                id="hitch_vertical",
                title="Hitch / OEM max tongue or pin load",
                light=L,
                detail=(
                    f"Tongue/pin {tongue_or_pin_weight:.0f} lb vs limit {vert_limit:.0f} lb."
                ),
                basis=(
                    "Lesser of truck OEM max tongue/pin and hitch hardware rating. "
                    "Hitch manufacturer label + OEM tow guide."
                ),
            )
        )
    else:
        checks.append(
            CheckResult(
                id="hitch_vertical",
                title="Hitch / OEM max tongue or pin load",
                light=Light.GRAY,
                detail="Enter tongue/pin weight and hitch or OEM vertical rating.",
                basis="OEM + hitch manufacturer ratings.",
            )
        )

    # 6) Trailer GVWR
    if trailer_trip is not None and trailer_gvwr is not None:
        L = _limit_light(trailer_trip, trailer_gvwr)
        checks.append(
            CheckResult(
                id="trailer_gvwr",
                title="Trailer not over its own GVWR",
                light=L,
                detail=f"Trailer ≈ {trailer_trip:.0f} lb vs trailer GVWR {trailer_gvwr:.0f} lb.",
                basis=(
                    "Trailer manufacturer certification label / VIN plate. "
                    "Homemade: builder-declared GVWR must not exceed structure + tire + axle system."
                ),
            )
        )
    elif trailer_gvwr is None and trailer_trip is not None:
        missing.append("Trailer GVWR (plate or builder rating)")

    # 6b) Aggregate axle GAWR (single through quint)
    if axle_count is not None and (axle_count < 1 or axle_count > 5):
        checks.append(
            CheckResult(
                id="axle_count",
                title="Axle count",
                light=Light.YELLOW,
                detail=f"Axle count {axle_count} is outside supported 1–5 (quint) range.",
                basis="STWL suite supports single through quint axle configurations.",
            )
        )
    if trailer_trip is not None and aggregate_axle_gawr is not None:
        L = _limit_light(trailer_trip, aggregate_axle_gawr)
        ac_txt = f"{axle_count}-axle" if axle_count else "multi-axle"
        checks.append(
            CheckResult(
                id="axle_aggregate_gawr",
                title=f"Trailer weight vs sum of axle GAWR ({ac_txt})",
                light=L,
                detail=(
                    f"Trailer ≈ {trailer_trip:.0f} lb vs sum of axle GAWR "
                    f"{aggregate_axle_gawr:.0f} lb."
                    + (
                        " EXCEEDS combined axle ratings — red regardless of trailer GVWR claim."
                        if L == Light.RED
                        else ""
                    )
                ),
                basis=(
                    "Each axle GAWR comes from the axle manufacturer ID plate / literature "
                    "(Dexter, Lippert, Meritor, etc.). Sum of GAWRs is an upper bound on axle "
                    "system capacity; trailer GVWR must also respect tires and frame. "
                    "Single vs dual wheel does not change the math — use the GAWR stamped for that axle assembly."
                ),
            )
        )
        if trailer_gvwr is not None and trailer_gvwr > aggregate_axle_gawr + 1e-6:
            checks.append(
                CheckResult(
                    id="gvwr_vs_axles",
                    title="Trailer GVWR vs axle system",
                    light=Light.YELLOW,
                    detail=(
                        f"Trailer GVWR {trailer_gvwr:.0f} lb is higher than sum of axle GAWR "
                        f"{aggregate_axle_gawr:.0f} lb. Treat the lower figure as the real cap "
                        "unless plates are wrong — common homemade error."
                    ),
                    basis="STWL consistency check: structure rating cannot honestly exceed axle system rating.",
                )
            )
    elif aggregate_axle_gawr is None:
        missing.append("Axle GAWR ratings (each axle plate; sum used for aggregate check)")
        checks.append(
            CheckResult(
                id="axle_aggregate_gawr",
                title="Trailer weight vs sum of axle GAWR",
                light=Light.GRAY,
                detail="Enter per-axle GAWR (single or dual wheel) from axle manufacturer plates.",
                basis="Axle manufacturer certification.",
            )
        )

    # 7) Advisory tongue/pin percent of trailer weight
    if tongue_or_pin_weight is not None and trailer_trip is not None and trailer_trip > 0:
        pct = tongue_or_pin_weight / trailer_trip
        numbers["tongue_or_pin_fraction"] = pct
        if hitch_style in ("fifth_wheel", "gooseneck"):
            lo, hi = FIFTH_GOOSENECK_PIN_MIN, FIFTH_GOOSENECK_PIN_MAX
            band = f"{lo:.0%}–{hi:.0%} (common 5th/gooseneck pin-weight teaching band)"
        else:
            lo, hi = CONVENTIONAL_TONGUE_MIN, CONVENTIONAL_TONGUE_MAX
            band = f"{lo:.0%}–{hi:.0%} (common conventional tongue-weight teaching band)"
        if pct < lo or pct > hi:
            L = Light.YELLOW
            detail = (
                f"Coupling load is {pct:.1%} of trailer weight; outside advisory band {band}. "
                "Not an automatic fail — correct per OEM/hitch maker and fix loading if unstable."
            )
        else:
            L = Light.GREEN
            detail = f"Coupling load is {pct:.1%} of trailer weight (within advisory band {band})."
        checks.append(
            CheckResult(
                id="tongue_percent",
                title="Tongue/pin share of trailer weight (advisory)",
                light=L,
                detail=detail,
                basis=(
                    "Advisory industry ranges often cited for stability (~10–15% conventional; "
                    "higher share often discussed for 5th-wheel/gooseneck). "
                    "Not a substitute for OEM or hitch-manufacturer specifications. STWL teaching summary."
                ),
            )
        )

    # Overall
    if not any(c.light != Light.GRAY for c in checks) or (
        truck_trip is None or trailer_trip is None
    ):
        overall = Light.GRAY
        label = "INCOMPLETE DATA"
        summary = (
            "Not enough numbers to grade this combination. "
            "Enter truck & trailer weights plus OEM GCWR / max trailer / payload from your door sticker "
            "and official tow guide for that exact truck."
        )
    else:
        overall = _worst(*(c.light for c in checks if c.light != Light.GRAY))
        # Any gray on a critical check when we have weights still allows green/yellow/red from known checks
        critical_gray = any(
            c.id in ("gcwr", "max_trailer", "payload", "axle_aggregate_gawr", "trailer_gvwr")
            and c.light == Light.GRAY
            for c in checks
        )
        if critical_gray and overall == Light.GREEN:
            overall = Light.YELLOW
        labels = {
            Light.GREEN: "GREEN — Acceptable (on entered numbers)",
            Light.YELLOW: "YELLOW — Caution / tight or incomplete",
            Light.RED: "RED — Not acceptable on entered numbers",
            Light.GRAY: "INCOMPLETE DATA",
        }
        label = labels[overall]
        if overall == Light.GREEN:
            summary = (
                "No hard OEM/physics limit exceeded on the numbers you entered, "
                "and margins are not in the tight band. Still verify with scales and OEM literature."
            )
        elif overall == Light.YELLOW:
            summary = (
                "Combination is in a caution zone: tight margins, advisory tongue/pin band, "
                "assumed weights, or missing critical OEM fields. Do not treat as a free pass."
            )
        else:
            summary = (
                "At least one hard limit is exceeded (GCWR, max trailer, GVWR, payload, hitch, "
                "trailer GVWR, or axle GAWR total). Do not tow until weights/config change."
            )

    return TowGradeResult(
        overall=overall,
        label=label,
        summary=summary,
        checks=checks,
        numbers=numbers,
        credits=list(CREDITS),
        missing_inputs=missing,
    )
