"""Trailer / homemade config registry with per-axle ratings (up to quint)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .db import connect, init_db
from .paths import db_path
from .vehicle_catalog import AXLE_COUNT_OPTIONS


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def add_trailer(
    name: str,
    *,
    rig_type: str | None = None,
    is_homemade: bool = False,
    make: str | None = None,
    model: str | None = None,
    year: int | None = None,
    vin: str | None = None,
    plate: str | None = None,
    length_ft: float | None = None,
    width_ft: float | None = None,
    height_ft: float | None = None,
    axle_count: int | None = None,
    brake_type: str | None = None,
    hitch_style: str | None = None,
    empty_weight: float | None = None,
    cargo_weight: float | None = None,
    gvwr: float | None = None,
    notes: str | None = None,
    rating_publisher: str | None = None,
    rating_source: str | None = None,
    prior_owner_count: int | None = None,
    prior_owner_count_source: str | None = None,
    axles: list[dict[str, Any]] | None = None,
    database: Path | None = None,
) -> int:
    """
    Create trailer + optional axle rows (1–5).
    Each axle dict may include: manufacturer, model_or_part, wheel_end, gawr_lb,
    tire_size, brake_type, notes, rating_publisher, rating_source.
    """
    init_db(database)
    axles = axles or []
    if axle_count is None and axles:
        axle_count = len(axles)
    if axle_count is not None and (axle_count < 1 or axle_count > 5):
        raise ValueError("axle_count must be 1–5 (single through quint)")
    if len(axles) > 5:
        raise ValueError("at most 5 axles (quint)")
    if prior_owner_count is not None and prior_owner_count < 0:
        raise ValueError("prior_owner_count cannot be negative")

    agg = 0.0
    has_gawr = False
    for a in axles:
        g = a.get("gawr_lb")
        if g is not None and g != "":
            agg += float(g)
            has_gawr = True

    with connect(database or db_path()) as conn:
        cur = conn.execute(
            """
            INSERT INTO rigs (
                name, rig_type, vin, notes, make, model, year, plate,
                gvwr, empty_weight, cargo_weight, hitch_style, is_homemade,
                length_ft, width_ft, height_ft, axle_count, brake_type,
                aggregate_axle_rating, rating_publisher, rating_source,
                prior_owner_count, prior_owner_count_source,
                status, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'active', ?)
            """,
            (
                name.strip(),
                rig_type or ("homemade" if is_homemade else None),
                vin,
                notes,
                make or ("HOMEMADE / HOME BUILT" if is_homemade else None),
                model,
                year,
                plate,
                gvwr,
                empty_weight,
                cargo_weight,
                hitch_style,
                1 if is_homemade else 0,
                length_ft,
                width_ft,
                height_ft,
                axle_count,
                brake_type,
                agg if has_gawr else None,
                rating_publisher,
                rating_source,
                prior_owner_count,
                prior_owner_count_source,
                _now(),
            ),
        )
        rid = int(cur.lastrowid)
        for i, a in enumerate(axles, start=1):
            we = (a.get("wheel_end") or "single").strip().lower()
            if we not in ("single", "dual"):
                we = "single"
            gawr = a.get("gawr_lb")
            gawr_f = float(gawr) if gawr is not None and gawr != "" else None
            conn.execute(
                """
                INSERT INTO trailer_axles (
                    rig_id, position, manufacturer, model_or_part, axle_style, wheel_end,
                    gawr_lb, tire_size, brake_type, notes, rating_publisher, rating_source
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    rid,
                    int(a.get("position") or i),
                    a.get("manufacturer"),
                    a.get("model_or_part"),
                    a.get("axle_style"),
                    we,
                    gawr_f,
                    a.get("tire_size"),
                    a.get("brake_type") or brake_type,
                    a.get("notes"),
                    a.get("rating_publisher"),
                    a.get("rating_source"),
                ),
            )
        conn.commit()
        return rid


def list_trailers(database: Path | None = None) -> list[dict[str, Any]]:
    init_db(database)
    with connect(database or db_path()) as conn:
        rows = conn.execute(
            "SELECT * FROM rigs ORDER BY name"
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["axles"] = list_axles(d["id"], database=database)
            out.append(d)
        return out


def get_trailer(rig_id: int, database: Path | None = None) -> dict[str, Any] | None:
    init_db(database)
    with connect(database or db_path()) as conn:
        row = conn.execute("SELECT * FROM rigs WHERE id = ?", (rig_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["axles"] = list_axles(rig_id, database=database)
        return d


def list_axles(rig_id: int, database: Path | None = None) -> list[dict[str, Any]]:
    init_db(database)
    with connect(database or db_path()) as conn:
        rows = conn.execute(
            """
            SELECT * FROM trailer_axles
            WHERE rig_id = ?
            ORDER BY position ASC, id ASC
            """,
            (rig_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def axle_summary(rig: dict[str, Any]) -> dict[str, Any]:
    axles = rig.get("axles") or []
    gawrs = [float(a["gawr_lb"]) for a in axles if a.get("gawr_lb") is not None]
    return {
        "axle_count": rig.get("axle_count") or len(axles) or None,
        "aggregate_gawr": sum(gawrs) if gawrs else rig.get("aggregate_axle_rating"),
        "wheel_ends": sorted({a.get("wheel_end") or "single" for a in axles}),
        "manufacturers": sorted({a.get("manufacturer") for a in axles if a.get("manufacturer")}),
        "label": dict(AXLE_COUNT_OPTIONS).get(
            int(rig.get("axle_count") or len(axles) or 0),
            f"{len(axles)} axle(s)",
        )
        if (rig.get("axle_count") or axles)
        else "—",
    }
