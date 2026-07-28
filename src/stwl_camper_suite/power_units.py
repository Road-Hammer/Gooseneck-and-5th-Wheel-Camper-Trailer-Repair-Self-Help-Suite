"""Power unit (tow vehicle) registry + maintenance via service log link."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .db import connect, init_db
from .paths import db_path
from .vehicle_catalog import YEAR_MAX, YEAR_MIN


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def add_power_unit(
    name: str,
    *,
    make: str | None = None,
    model: str | None = None,
    year: int | None = None,
    trim: str | None = None,
    vin: str | None = None,
    engine: str | None = None,
    drivetrain: str | None = None,
    duty_class: str | None = None,
    config_notes: str | None = None,
    gvwr: float | None = None,
    gcwr: float | None = None,
    payload_capacity: float | None = None,
    max_trailer_weight: float | None = None,
    max_tongue_weight: float | None = None,
    hitch_receiver_rating: float | None = None,
    curb_weight: float | None = None,
    rating_publisher: str | None = None,
    rating_source: str | None = None,
    prior_owner_count: int | None = None,
    prior_owner_count_source: str | None = None,
    notes: str | None = None,
    database: Path | None = None,
) -> int:
    if year is not None and (year < YEAR_MIN or year > YEAR_MAX + 1):
        raise ValueError(f"year must be {YEAR_MIN}–{YEAR_MAX + 1}")
    if prior_owner_count is not None and prior_owner_count < 0:
        raise ValueError("prior_owner_count cannot be negative")
    init_db(database)
    with connect(database or db_path()) as conn:
        cur = conn.execute(
            """
            INSERT INTO power_units (
                name, make, model, year, trim, vin, engine, drivetrain,
                duty_class, config_notes,
                gvwr, gcwr, payload_capacity, max_trailer_weight, max_tongue_weight,
                hitch_receiver_rating, curb_weight, rating_publisher, rating_source,
                prior_owner_count, prior_owner_count_source,
                notes, status, created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'active', ?, ?)
            """,
            (
                name.strip(),
                make,
                model,
                year,
                trim,
                vin,
                engine,
                drivetrain,
                duty_class,
                config_notes,
                gvwr,
                gcwr,
                payload_capacity,
                max_trailer_weight,
                max_tongue_weight,
                hitch_receiver_rating,
                curb_weight,
                rating_publisher,
                rating_source,
                prior_owner_count,
                prior_owner_count_source,
                notes,
                _now(),
                _now(),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_power_units(database: Path | None = None) -> list[dict[str, Any]]:
    init_db(database)
    with connect(database or db_path()) as conn:
        rows = conn.execute("SELECT * FROM power_units ORDER BY name").fetchall()
        return [dict(r) for r in rows]


def get_power_unit(pu_id: int, database: Path | None = None) -> dict[str, Any] | None:
    init_db(database)
    with connect(database or db_path()) as conn:
        row = conn.execute("SELECT * FROM power_units WHERE id = ?", (pu_id,)).fetchone()
        return dict(row) if row else None


def list_power_unit_maintenance(
    power_unit_id: int | None = None,
    limit: int = 100,
    database: Path | None = None,
) -> list[dict[str, Any]]:
    init_db(database)
    with connect(database or db_path()) as conn:
        if power_unit_id is not None:
            rows = conn.execute(
                """
                SELECT s.*, p.name AS power_unit_name, v.name AS vendor_name
                FROM service_log s
                LEFT JOIN power_units p ON p.id = s.power_unit_id
                LEFT JOIN vendors v ON v.id = s.vendor_id
                WHERE s.power_unit_id = ?
                ORDER BY s.performed_at DESC, s.id DESC
                LIMIT ?
                """,
                (power_unit_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT s.*, p.name AS power_unit_name, v.name AS vendor_name
                FROM service_log s
                LEFT JOIN power_units p ON p.id = s.power_unit_id
                LEFT JOIN vendors v ON v.id = s.vendor_id
                WHERE s.power_unit_id IS NOT NULL
                ORDER BY s.performed_at DESC, s.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
