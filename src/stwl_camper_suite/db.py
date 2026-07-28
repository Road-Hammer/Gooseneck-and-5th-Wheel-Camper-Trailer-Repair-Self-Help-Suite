from __future__ import annotations

import sqlite3
from pathlib import Path

from .paths import db_path


SCHEMA = """
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS guides (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    path TEXT NOT NULL,
    difficulty INTEGER,
    safety_level TEXT,
    rig_types TEXT,
    tags TEXT,
    tools TEXT,
    body_md TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS guides_fts USING fts5(
    id UNINDEXED,
    title,
    category,
    tags,
    body_md,
    content='guides',
    content_rowid='rowid'
);

CREATE TABLE IF NOT EXISTS rigs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rig_type TEXT,
    vin TEXT,
    notes TEXT,
    make TEXT,
    model TEXT,
    year INTEGER,
    plate TEXT,
    gvwr REAL,
    status TEXT DEFAULT 'active',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    trade TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    specialties TEXT,
    notes TEXT,
    preferred INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vendor_guide_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL,
    guide_id TEXT,
    category TEXT,
    note TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS service_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rig_id INTEGER,
    vendor_id INTEGER,
    guide_id TEXT,
    wo_number TEXT,
    performed_at TEXT NOT NULL,
    completed_at TEXT,
    category TEXT,
    title TEXT NOT NULL,
    details TEXT,
    status TEXT NOT NULL DEFAULT 'completed',
    priority TEXT NOT NULL DEFAULT 'normal',
    performed_by TEXT,
    miles REAL,
    labor_hours REAL,
    labor_cost REAL,
    parts_cost REAL,
    cost REAL,
    parts TEXT,
    invoice_ref TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    FOREIGN KEY (rig_id) REFERENCES rigs(id) ON DELETE SET NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_service_log_rig ON service_log(rig_id);
CREATE INDEX IF NOT EXISTS idx_service_log_date ON service_log(performed_at);
CREATE INDEX IF NOT EXISTS idx_vendors_name ON vendors(name);
CREATE INDEX IF NOT EXISTS idx_vendor_guide_vendor ON vendor_guide_links(vendor_id);
CREATE INDEX IF NOT EXISTS idx_vendor_guide_guide ON vendor_guide_links(guide_id);
"""

# Created after migrate() so upgraded DBs have columns first
POST_MIGRATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_service_log_status ON service_log(status);
CREATE INDEX IF NOT EXISTS idx_service_log_vendor ON service_log(vendor_id);
"""

# Columns to add when upgrading older DBs created by v0.1
_MIGRATIONS: dict[str, list[tuple[str, str]]] = {
    "rigs": [
        ("make", "TEXT"),
        ("model", "TEXT"),
        ("year", "INTEGER"),
        ("plate", "TEXT"),
        ("gvwr", "REAL"),
        ("status", "TEXT DEFAULT 'active'"),
    ],
    "service_log": [
        ("vendor_id", "INTEGER"),
        ("guide_id", "TEXT"),
        ("wo_number", "TEXT"),
        ("completed_at", "TEXT"),
        ("status", "TEXT NOT NULL DEFAULT 'completed'"),
        ("priority", "TEXT NOT NULL DEFAULT 'normal'"),
        ("performed_by", "TEXT"),
        ("labor_hours", "REAL"),
        ("labor_cost", "REAL"),
        ("parts_cost", "REAL"),
        ("invoice_ref", "TEXT"),
        ("updated_at", "TEXT"),
    ],
}


def connect(path: Path | None = None) -> sqlite3.Connection:
    p = path or db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=DELETE")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {r[1] for r in rows}


def migrate(conn: sqlite3.Connection) -> None:
    for table, cols in _MIGRATIONS.items():
        existing = _table_columns(conn, table)
        if not existing:
            continue
        for name, decl in cols:
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {decl}")


def init_db(path: Path | None = None) -> Path:
    p = path or db_path()
    with connect(p) as conn:
        conn.executescript(SCHEMA)
        migrate(conn)
        conn.executescript(POST_MIGRATE_INDEXES)
        conn.executescript(
            """
            CREATE TRIGGER IF NOT EXISTS guides_ai AFTER INSERT ON guides BEGIN
              INSERT INTO guides_fts(rowid, id, title, category, tags, body_md)
              VALUES (new.rowid, new.id, new.title, new.category, new.tags, new.body_md);
            END;
            CREATE TRIGGER IF NOT EXISTS guides_ad AFTER DELETE ON guides BEGIN
              INSERT INTO guides_fts(guides_fts, rowid, id, title, category, tags, body_md)
              VALUES ('delete', old.rowid, old.id, old.title, old.category, old.tags, old.body_md);
            END;
            CREATE TRIGGER IF NOT EXISTS guides_au AFTER UPDATE ON guides BEGIN
              INSERT INTO guides_fts(guides_fts, rowid, id, title, category, tags, body_md)
              VALUES ('delete', old.rowid, old.id, old.title, old.category, old.tags, old.body_md);
              INSERT INTO guides_fts(rowid, id, title, category, tags, body_md)
              VALUES (new.rowid, new.id, new.title, new.category, new.tags, new.body_md);
            END;
            """
        )
        conn.commit()
    return p
