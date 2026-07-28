"""Offline CMMS / repair-shop tracking: assets (rigs), work orders, vendors."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .db import connect, init_db
from .paths import db_path

# Shared constants for forms / CLI
RIG_TYPES = [
    "bumper_pull",
    "travel_trailer",
    "fifth_wheel",
    "gooseneck",
    "toy_hauler",
    "cargo_trailer",
    "utility_trailer",
    "equine_trailer",
    "stock_trailer",
    "cattle_trailer",
    "livestock_trailer",
    "horse_livestock_trailer",
    "other",
]

WORK_STATUSES = [
    "open",
    "in_progress",
    "waiting_parts",
    "waiting_vendor",
    "completed",
    "cancelled",
]

PRIORITIES = ["low", "normal", "high", "urgent"]

VENDOR_TRADES = [
    "full_service_trailer_shop",
    "mobile_tech",
    "brakes_axles",
    "welding_fabrication",
    "electrical",
    "hitch_tow",
    "tires_wheels",
    "body_paint",
    "equine_stock_specialist",
    "parts_supplier",
    "towing_recovery",
    "other",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _today() -> str:
    return _now()[:10]


def _opt_float(value: str | float | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _opt_int(value: str | int | None) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


# ---------------------------------------------------------------------------
# Assets (rigs)
# ---------------------------------------------------------------------------

def add_rig(
    name: str,
    *,
    rig_type: str | None = None,
    vin: str | None = None,
    notes: str | None = None,
    make: str | None = None,
    model: str | None = None,
    year: int | None = None,
    plate: str | None = None,
    gvwr: float | None = None,
    status: str = "active",
    database: Path | None = None,
) -> int:
    init_db(database)
    with connect(database or db_path()) as conn:
        cur = conn.execute(
            """
            INSERT INTO rigs (
                name, rig_type, vin, notes, make, model, year, plate, gvwr, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name.strip(),
                rig_type,
                vin,
                notes,
                make,
                model,
                year,
                plate,
                gvwr,
                status or "active",
                _now(),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_rigs(database: Path | None = None, active_only: bool = False) -> list[dict[str, Any]]:
    init_db(database)
    with connect(database or db_path()) as conn:
        if active_only:
            rows = conn.execute(
                "SELECT * FROM rigs WHERE COALESCE(status, 'active') != 'retired' ORDER BY name"
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM rigs ORDER BY name").fetchall()
        return [dict(r) for r in rows]


def get_rig(rig_id: int, database: Path | None = None) -> dict[str, Any] | None:
    init_db(database)
    with connect(database or db_path()) as conn:
        row = conn.execute("SELECT * FROM rigs WHERE id = ?", (rig_id,)).fetchone()
        return dict(row) if row else None


# ---------------------------------------------------------------------------
# Vendors
# ---------------------------------------------------------------------------

def add_vendor(
    name: str,
    *,
    trade: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    website: str | None = None,
    address: str | None = None,
    city: str | None = None,
    state: str | None = None,
    zip_code: str | None = None,
    specialties: str | None = None,
    notes: str | None = None,
    preferred: bool = False,
    database: Path | None = None,
) -> int:
    init_db(database)
    ts = _now()
    with connect(database or db_path()) as conn:
        cur = conn.execute(
            """
            INSERT INTO vendors (
                name, trade, phone, email, website, address, city, state, zip,
                specialties, notes, preferred, active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                name.strip(),
                trade,
                phone,
                email,
                website,
                address,
                city,
                state,
                zip_code,
                specialties,
                notes,
                1 if preferred else 0,
                ts,
                ts,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_vendors(
    database: Path | None = None,
    active_only: bool = True,
    guide_id: str | None = None,
    category: str | None = None,
) -> list[dict[str, Any]]:
    init_db(database)
    with connect(database or db_path()) as conn:
        if guide_id:
            rows = conn.execute(
                """
                SELECT DISTINCT v.*
                FROM vendors v
                JOIN vendor_guide_links l ON l.vendor_id = v.id
                WHERE l.guide_id = ?
                  AND (? = 0 OR v.active = 1)
                ORDER BY v.preferred DESC, v.name
                """,
                (guide_id, 1 if active_only else 0),
            ).fetchall()
        elif category:
            rows = conn.execute(
                """
                SELECT DISTINCT v.*
                FROM vendors v
                JOIN vendor_guide_links l ON l.vendor_id = v.id
                WHERE l.category = ?
                  AND (? = 0 OR v.active = 1)
                ORDER BY v.preferred DESC, v.name
                """,
                (category, 1 if active_only else 0),
            ).fetchall()
        elif active_only:
            rows = conn.execute(
                "SELECT * FROM vendors WHERE active = 1 ORDER BY preferred DESC, name"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM vendors ORDER BY preferred DESC, name"
            ).fetchall()
        return [dict(r) for r in rows]


def get_vendor(vendor_id: int, database: Path | None = None) -> dict[str, Any] | None:
    init_db(database)
    with connect(database or db_path()) as conn:
        row = conn.execute("SELECT * FROM vendors WHERE id = ?", (vendor_id,)).fetchone()
        return dict(row) if row else None


def link_vendor_to_guide(
    vendor_id: int,
    *,
    guide_id: str | None = None,
    category: str | None = None,
    note: str | None = None,
    database: Path | None = None,
) -> int:
    if not guide_id and not category:
        raise ValueError("link requires guide_id and/or category")
    init_db(database)
    with connect(database or db_path()) as conn:
        cur = conn.execute(
            """
            INSERT INTO vendor_guide_links (vendor_id, guide_id, category, note, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (vendor_id, guide_id, category, note, _now()),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_vendor_links(
    vendor_id: int | None = None,
    guide_id: str | None = None,
    database: Path | None = None,
) -> list[dict[str, Any]]:
    init_db(database)
    with connect(database or db_path()) as conn:
        if vendor_id is not None:
            rows = conn.execute(
                """
                SELECT l.*, v.name AS vendor_name
                FROM vendor_guide_links l
                JOIN vendors v ON v.id = l.vendor_id
                WHERE l.vendor_id = ?
                ORDER BY l.id DESC
                """,
                (vendor_id,),
            ).fetchall()
        elif guide_id is not None:
            rows = conn.execute(
                """
                SELECT l.*, v.name AS vendor_name, v.phone AS vendor_phone,
                       v.trade AS vendor_trade, v.preferred AS vendor_preferred
                FROM vendor_guide_links l
                JOIN vendors v ON v.id = l.vendor_id
                WHERE l.guide_id = ? AND v.active = 1
                ORDER BY v.preferred DESC, v.name
                """,
                (guide_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT l.*, v.name AS vendor_name
                FROM vendor_guide_links l
                JOIN vendors v ON v.id = l.vendor_id
                ORDER BY l.id DESC
                LIMIT 200
                """
            ).fetchall()
        return [dict(r) for r in rows]


def vendors_for_guide_or_category(
    guide_id: str,
    category: str | None = None,
    database: Path | None = None,
) -> list[dict[str, Any]]:
    """Vendors linked to this guide id or its category (for repair-guide sidebar)."""
    init_db(database)
    with connect(database or db_path()) as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT v.*
            FROM vendors v
            JOIN vendor_guide_links l ON l.vendor_id = v.id
            WHERE v.active = 1
              AND (l.guide_id = ? OR (? IS NOT NULL AND l.category = ?))
            ORDER BY v.preferred DESC, v.name
            """,
            (guide_id, category, category),
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Work orders / service log
# ---------------------------------------------------------------------------

def next_wo_number(database: Path | None = None) -> str:
    init_db(database)
    year = datetime.now().year
    prefix = f"WO-{year}-"
    with connect(database or db_path()) as conn:
        row = conn.execute(
            """
            SELECT wo_number FROM service_log
            WHERE wo_number LIKE ?
            ORDER BY id DESC LIMIT 1
            """,
            (f"{prefix}%",),
        ).fetchone()
    if not row or not row["wo_number"]:
        return f"{prefix}0001"
    try:
        n = int(str(row["wo_number"]).split("-")[-1]) + 1
    except ValueError:
        n = 1
    return f"{prefix}{n:04d}"


def add_entry(
    title: str,
    *,
    rig_id: int | None = None,
    vendor_id: int | None = None,
    guide_id: str | None = None,
    wo_number: str | None = None,
    performed_at: str | None = None,
    completed_at: str | None = None,
    category: str | None = None,
    details: str | None = None,
    status: str = "completed",
    priority: str = "normal",
    performed_by: str | None = None,
    miles: float | None = None,
    labor_hours: float | None = None,
    labor_cost: float | None = None,
    parts_cost: float | None = None,
    cost: float | None = None,
    parts: str | None = None,
    invoice_ref: str | None = None,
    database: Path | None = None,
) -> int:
    init_db(database)
    st = status if status in WORK_STATUSES else "completed"
    pr = priority if priority in PRIORITIES else "normal"
    ts = _now()
    # Auto total cost if not provided
    if cost is None and (labor_cost is not None or parts_cost is not None):
        cost = (labor_cost or 0.0) + (parts_cost or 0.0)
    if not wo_number and st in ("open", "in_progress", "waiting_parts", "waiting_vendor"):
        wo_number = next_wo_number(database)
    if st == "completed" and not completed_at:
        completed_at = performed_at or _today()
    with connect(database or db_path()) as conn:
        cur = conn.execute(
            """
            INSERT INTO service_log (
                rig_id, vendor_id, guide_id, wo_number, performed_at, completed_at,
                category, title, details, status, priority, performed_by,
                miles, labor_hours, labor_cost, parts_cost, cost, parts,
                invoice_ref, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rig_id,
                vendor_id,
                guide_id,
                wo_number,
                performed_at or _today(),
                completed_at,
                category,
                title.strip(),
                details,
                st,
                pr,
                performed_by,
                miles,
                labor_hours,
                labor_cost,
                parts_cost,
                cost,
                parts,
                invoice_ref,
                ts,
                ts,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def update_entry_status(
    entry_id: int,
    status: str,
    *,
    completed_at: str | None = None,
    database: Path | None = None,
) -> None:
    init_db(database)
    st = status if status in WORK_STATUSES else status
    ts = _now()
    done = completed_at
    if st == "completed" and not done:
        done = _today()
    with connect(database or db_path()) as conn:
        conn.execute(
            """
            UPDATE service_log
            SET status = ?, completed_at = COALESCE(?, completed_at), updated_at = ?
            WHERE id = ?
            """,
            (st, done, ts, entry_id),
        )
        conn.commit()


def list_entries(
    rig_id: int | None = None,
    vendor_id: int | None = None,
    status: str | None = None,
    open_only: bool = False,
    limit: int = 100,
    database: Path | None = None,
) -> list[dict[str, Any]]:
    init_db(database)
    clauses: list[str] = []
    params: list[Any] = []
    if rig_id is not None:
        clauses.append("s.rig_id = ?")
        params.append(rig_id)
    if vendor_id is not None:
        clauses.append("s.vendor_id = ?")
        params.append(vendor_id)
    if status:
        clauses.append("s.status = ?")
        params.append(status)
    if open_only:
        clauses.append("s.status NOT IN ('completed', 'cancelled')")
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    params.append(limit)
    sql = f"""
        SELECT s.*,
               r.name AS rig_name,
               v.name AS vendor_name
        FROM service_log s
        LEFT JOIN rigs r ON r.id = s.rig_id
        LEFT JOIN vendors v ON v.id = s.vendor_id
        {where}
        ORDER BY
          CASE s.status
            WHEN 'urgent' THEN 0
            WHEN 'open' THEN 1
            WHEN 'in_progress' THEN 2
            WHEN 'waiting_parts' THEN 3
            WHEN 'waiting_vendor' THEN 4
            ELSE 5
          END,
          s.performed_at DESC,
          s.id DESC
        LIMIT ?
    """
    with connect(database or db_path()) as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def shop_summary(database: Path | None = None) -> dict[str, Any]:
    init_db(database)
    with connect(database or db_path()) as conn:
        open_count = conn.execute(
            """
            SELECT COUNT(*) AS n FROM service_log
            WHERE status NOT IN ('completed', 'cancelled')
            """
        ).fetchone()["n"]
        by_status = {
            r["status"]: r["n"]
            for r in conn.execute(
                "SELECT status, COUNT(*) AS n FROM service_log GROUP BY status"
            ).fetchall()
        }
        asset_count = conn.execute("SELECT COUNT(*) AS n FROM rigs").fetchone()["n"]
        vendor_count = conn.execute(
            "SELECT COUNT(*) AS n FROM vendors WHERE active = 1"
        ).fetchone()["n"]
        spend = conn.execute(
            """
            SELECT COALESCE(SUM(cost), 0) AS total
            FROM service_log
            WHERE status = 'completed' AND cost IS NOT NULL
            """
        ).fetchone()["total"]
    return {
        "open_work_orders": open_count,
        "by_status": by_status,
        "assets": asset_count,
        "vendors": vendor_count,
        "completed_spend": spend,
    }
