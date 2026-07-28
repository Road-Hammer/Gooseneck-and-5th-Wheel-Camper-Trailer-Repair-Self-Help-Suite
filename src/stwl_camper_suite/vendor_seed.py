"""Seed national vendor directory from content/vendors/seed_vendors.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .db import connect, init_db
from .paths import content_dir, db_path, project_root


def seed_yaml_path() -> Path:
    p = content_dir() / "vendors" / "seed_vendors.yaml"
    if p.is_file():
        return p
    return project_root() / "content" / "vendors" / "seed_vendors.yaml"


def load_seed_file() -> dict[str, Any]:
    path = seed_yaml_path()
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def _ensure_seed_key_column(conn) -> None:
    cols = {r[1] for r in conn.execute("PRAGMA table_info(vendors)").fetchall()}
    if "seed_key" not in cols:
        conn.execute("ALTER TABLE vendors ADD COLUMN seed_key TEXT")
    if "mobility" not in cols:
        conn.execute("ALTER TABLE vendors ADD COLUMN mobility TEXT")
    if "source_credit" not in cols:
        conn.execute("ALTER TABLE vendors ADD COLUMN source_credit TEXT")


def seed_vendors(
    *,
    database: Path | None = None,
    refresh: bool = False,
) -> dict[str, int]:
    """
    Insert seed vendors. Skip existing seed_key unless refresh=True (then update).
    Returns counts: inserted, updated, skipped, total_seed.
    """
    init_db(database)
    data = load_seed_file()
    vendors = data.get("vendors") or []
    inserted = updated = skipped = 0
    path = database or db_path()
    with connect(path) as conn:
        _ensure_seed_key_column(conn)
        for v in vendors:
            if not isinstance(v, dict) or not v.get("name"):
                continue
            key = str(v.get("seed_key") or v["name"]).strip()
            existing = conn.execute(
                "SELECT id FROM vendors WHERE seed_key = ?", (key,)
            ).fetchone()
            notes = v.get("notes") or ""
            credit = v.get("source_credit") or ""
            if credit:
                notes = (notes + "\n" if notes else "") + f"Source credit: {credit}"
            fields = (
                v["name"].strip(),
                v.get("trade"),
                v.get("phone"),
                v.get("email"),
                v.get("website"),
                v.get("address"),
                v.get("city"),
                v.get("state"),
                v.get("zip") or v.get("zip_code"),
                v.get("specialties"),
                notes or None,
                1 if v.get("preferred") else 0,
                key,
                v.get("mobility"),
                credit or None,
            )
            if existing and not refresh:
                skipped += 1
                continue
            if existing and refresh:
                conn.execute(
                    """
                    UPDATE vendors SET
                        name=?, trade=?, phone=?, email=?, website=?,
                        address=?, city=?, state=?, zip=?,
                        specialties=?, notes=?, preferred=?,
                        mobility=?, source_credit=?, active=1
                    WHERE seed_key=?
                    """,
                    (*fields[:-2], fields[-2], fields[-1], key)
                    if False
                    else (
                        fields[0],
                        fields[1],
                        fields[2],
                        fields[3],
                        fields[4],
                        fields[5],
                        fields[6],
                        fields[7],
                        fields[8],
                        fields[9],
                        fields[10],
                        fields[11],
                        fields[13],
                        fields[14],
                        key,
                    ),
                )
                updated += 1
            else:
                conn.execute(
                    """
                    INSERT INTO vendors (
                        name, trade, phone, email, website, address, city, state, zip,
                        specialties, notes, preferred, active, created_at, updated_at,
                        seed_key, mobility, source_credit
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1,datetime('now'),datetime('now'),?,?,?)
                    """,
                    (
                        fields[0],
                        fields[1],
                        fields[2],
                        fields[3],
                        fields[4],
                        fields[5],
                        fields[6],
                        fields[7],
                        fields[8],
                        fields[9],
                        fields[10],
                        fields[11],
                        key,
                        fields[13],
                        fields[14],
                    ),
                )
                inserted += 1
        conn.commit()
    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "total_seed": len(vendors),
    }


def ensure_seeded(database: Path | None = None) -> dict[str, int] | None:
    """If vendor table has zero rows, load national seed list once."""
    init_db(database)
    with connect(database or db_path()) as conn:
        n = conn.execute("SELECT COUNT(*) AS c FROM vendors").fetchone()["c"]
    if n == 0:
        return seed_vendors(database=database, refresh=False)
    return None
