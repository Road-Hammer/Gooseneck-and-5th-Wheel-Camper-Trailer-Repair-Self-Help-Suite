from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .db import connect, init_db
from .paths import content_dir, db_path


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)


@dataclass
class GuideDoc:
    id: str
    title: str
    category: str
    path: str
    difficulty: int | None = None
    safety_level: str | None = None
    rig_types: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    body_md: str = ""


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    meta = yaml.safe_load(m.group(1)) or {}
    if not isinstance(meta, dict):
        meta = {}
    return meta, m.group(2)


def discover_markdown(root: Path | None = None) -> list[Path]:
    base = root or content_dir()
    paths: list[Path] = []
    for sub in ("guides", "wisdom"):
        folder = base / sub
        if folder.is_dir():
            paths.extend(sorted(folder.rglob("*.md")))
    return paths


def load_guide(path: Path, content_root: Path | None = None) -> GuideDoc:
    root = content_root or content_dir()
    raw = path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(raw)
    rel = str(path.relative_to(root)).replace("\\", "/")
    gid = str(meta.get("id") or path.stem)
    title = str(meta.get("title") or path.stem.replace("-", " ").title())
    category = str(meta.get("category") or path.parent.name)
    difficulty = meta.get("difficulty")
    try:
        difficulty_i = int(difficulty) if difficulty is not None else None
    except (TypeError, ValueError):
        difficulty_i = None
    rig_types = meta.get("rig_types") or []
    tags = meta.get("tags") or []
    tools = meta.get("tools") or []
    if isinstance(rig_types, str):
        rig_types = [rig_types]
    if isinstance(tags, str):
        tags = [tags]
    if isinstance(tools, str):
        tools = [tools]
    return GuideDoc(
        id=gid,
        title=title,
        category=category,
        path=rel,
        difficulty=difficulty_i,
        safety_level=str(meta["safety_level"]) if meta.get("safety_level") else None,
        rig_types=list(rig_types),
        tags=list(tags),
        tools=list(tools),
        body_md=body.strip() + "\n",
    )


def load_catalog(root: Path | None = None) -> dict[str, Any]:
    cat = (root or content_dir()) / "catalog.yaml"
    if not cat.is_file():
        return {}
    data = yaml.safe_load(cat.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def rebuild_index(database: Path | None = None) -> int:
    """Scan content markdown and rebuild guides + FTS tables. Returns guide count."""
    init_db(database)
    docs = [load_guide(p) for p in discover_markdown()]
    now = datetime.now(timezone.utc).isoformat()
    with connect(database or db_path()) as conn:
        conn.execute("DELETE FROM guides")
        for d in docs:
            conn.execute(
                """
                INSERT INTO guides (
                    id, title, category, path, difficulty, safety_level,
                    rig_types, tags, tools, body_md, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    d.id,
                    d.title,
                    d.category,
                    d.path,
                    d.difficulty,
                    d.safety_level,
                    ",".join(d.rig_types),
                    ",".join(d.tags),
                    ",".join(d.tools),
                    d.body_md,
                    now,
                ),
            )
        conn.execute(
            "INSERT INTO meta(key, value) VALUES('last_index_at', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (now,),
        )
        conn.execute(
            "INSERT INTO meta(key, value) VALUES('guide_count', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (str(len(docs)),),
        )
        conn.commit()
    return len(docs)


def list_guides(
    category: str | None = None,
    database: Path | None = None,
) -> list[sqlite3.Row]:
    init_db(database)
    with connect(database or db_path()) as conn:
        if category:
            cur = conn.execute(
                "SELECT * FROM guides WHERE category = ? ORDER BY title",
                (category,),
            )
        else:
            cur = conn.execute("SELECT * FROM guides ORDER BY category, title")
        return list(cur.fetchall())


def get_guide(guide_id: str, database: Path | None = None) -> dict[str, Any] | None:
    init_db(database)
    with connect(database or db_path()) as conn:
        row = conn.execute("SELECT * FROM guides WHERE id = ?", (guide_id,)).fetchone()
        return dict(row) if row else None


def search_guides(query: str, database: Path | None = None, limit: int = 50) -> list[dict]:
    init_db(database)
    q = query.strip()
    if not q:
        return []
    # FTS5: quote multi-word as AND tokens
    tokens = [t for t in re.split(r"\s+", q) if t]
    fts_query = " ".join(tokens)
    with connect(database or db_path()) as conn:
        try:
            rows = conn.execute(
                """
                SELECT g.*, snippet(guides_fts, 4, '[', ']', '…', 12) AS snippet
                FROM guides_fts
                JOIN guides g ON g.rowid = guides_fts.rowid
                WHERE guides_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (fts_query, limit),
            ).fetchall()
        except Exception:
            # Fallback LIKE if FTS query syntax fails
            like = f"%{q}%"
            rows = conn.execute(
                """
                SELECT *, substr(body_md, 1, 160) AS snippet
                FROM guides
                WHERE title LIKE ? OR body_md LIKE ? OR tags LIKE ?
                ORDER BY title
                LIMIT ?
                """,
                (like, like, like, limit),
            ).fetchall()
        return [dict(r) for r in rows]
