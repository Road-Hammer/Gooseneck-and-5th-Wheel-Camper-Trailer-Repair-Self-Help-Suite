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

REQUIRED_FRONTMATTER = ("id", "title", "category", "status", "scope", "safety_level")
REQUIRED_BODY_MARKERS_WARNING = ("stop conditions", "pro help triggers")


class GuideValidationError(ValueError):
    """Raised when a guide fails publishing standards."""


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
    status: str = "published"
    scope: str = ""
    credits: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    body_md: str = ""


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return [str(value).strip()]


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


def validate_guide(meta: dict[str, Any], body: str, path: Path) -> list[str]:
    """Return list of validation errors (empty if OK)."""
    errors: list[str] = []
    for key in REQUIRED_FRONTMATTER:
        if not meta.get(key):
            errors.append(f"{path.name}: missing required frontmatter '{key}'")
    status = str(meta.get("status", "")).lower()
    if status and status != "published":
        errors.append(f"{path.name}: status must be 'published' to ship (got {status!r})")
    credits = _as_str_list(meta.get("credits") or meta.get("credit"))
    sources = _as_str_list(meta.get("sources") or meta.get("sources_consulted"))
    if not credits and not sources:
        errors.append(
            f"{path.name}: must list publisher credits and/or sources "
            "(frontmatter 'credits' and/or 'sources')"
        )
    body_l = body.lower()
    safety = str(meta.get("safety_level") or "").lower()
    if safety in ("caution", "warning", "stop"):
        for marker in REQUIRED_BODY_MARKERS_WARNING:
            if marker not in body_l:
                errors.append(f"{path.name}: safety_level={safety} requires section '{marker}'")
    # Ban obvious placeholder language in published body
    banned = (
        "coming soon",
        "todo:",
        "tbd",
        "lorem ipsum",
        "placeholder",
        "write this later",
        "fill in later",
    )
    for b in banned:
        if b in body_l:
            errors.append(f"{path.name}: banned placeholder language found ({b!r})")
    return errors


def load_guide(path: Path, content_root: Path | None = None, *, strict: bool = True) -> GuideDoc:
    root = content_root or content_dir()
    raw = path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(raw)
    if strict:
        errs = validate_guide(meta, body, path)
        if errs:
            raise GuideValidationError("\n".join(errs))
    rel = str(path.relative_to(root)).replace("\\", "/")
    gid = str(meta.get("id") or path.stem)
    title = str(meta.get("title") or path.stem.replace("-", " ").title())
    category = str(meta.get("category") or path.parent.name)
    difficulty = meta.get("difficulty")
    try:
        difficulty_i = int(difficulty) if difficulty is not None else None
    except (TypeError, ValueError):
        difficulty_i = None
    rig_types = _as_str_list(meta.get("rig_types"))
    tags = _as_str_list(meta.get("tags"))
    tools = _as_str_list(meta.get("tools"))
    credits = _as_str_list(meta.get("credits") or meta.get("credit"))
    sources = _as_str_list(meta.get("sources") or meta.get("sources_consulted"))
    return GuideDoc(
        id=gid,
        title=title,
        category=category,
        path=rel,
        difficulty=difficulty_i,
        safety_level=str(meta["safety_level"]) if meta.get("safety_level") else None,
        rig_types=rig_types,
        tags=tags,
        tools=tools,
        status=str(meta.get("status") or "published"),
        scope=str(meta.get("scope") or "").strip(),
        credits=credits,
        sources=sources,
        body_md=body.strip() + "\n",
    )


def load_catalog(root: Path | None = None) -> dict[str, Any]:
    cat = (root or content_dir()) / "catalog.yaml"
    if not cat.is_file():
        return {}
    data = yaml.safe_load(cat.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def published_categories(
    database: Path | None = None,
    root: Path | None = None,
) -> list[dict[str, Any]]:
    """Catalog categories that have at least one indexed guide (no empty shells)."""
    catalog = load_catalog(root)
    by_id = {c["id"]: c for c in (catalog.get("categories") or []) if c.get("id")}
    guides = list_guides(database=database)
    seen: dict[str, int] = {}
    for g in guides:
        seen[g["category"]] = seen.get(g["category"], 0) + 1
    out: list[dict[str, Any]] = []
    for cat_id, count in sorted(seen.items(), key=lambda x: by_id.get(x[0], {}).get("title", x[0])):
        meta = by_id.get(cat_id) or {
            "id": cat_id,
            "title": cat_id.replace("_", " ").title(),
            "description": "",
        }
        item = dict(meta)
        item["guide_count"] = count
        out.append(item)
    return out


def rebuild_index(database: Path | None = None) -> int:
    """Scan content markdown and rebuild guides + FTS tables. Returns guide count."""
    init_db(database)
    paths = discover_markdown()
    docs: list[GuideDoc] = []
    errors: list[str] = []
    for p in paths:
        try:
            docs.append(load_guide(p, strict=True))
        except GuideValidationError as e:
            errors.append(str(e))
    if errors:
        raise GuideValidationError(
            "Publishing standards failed — fix before index:\n" + "\n".join(errors)
        )

    catalog = load_catalog()
    catalog_ids = {c["id"] for c in (catalog.get("categories") or []) if c.get("id")}
    for d in docs:
        if catalog_ids and d.category not in catalog_ids:
            errors.append(
                f"{d.id}: category {d.category!r} not in content/catalog.yaml published categories"
            )
    # Empty catalog categories
    guide_cats = {d.category for d in docs}
    for cid in catalog_ids:
        if cid not in guide_cats:
            errors.append(
                f"catalog category {cid!r} has zero guides — remove from catalog.yaml or add a finished guide"
            )
    if errors:
        raise GuideValidationError(
            "Catalog/publish mismatch:\n" + "\n".join(errors)
        )

    now = datetime.now(timezone.utc).isoformat()
    with connect(database or db_path()) as conn:
        # Ensure credits columns exist (migrate light)
        cols = {r[1] for r in conn.execute("PRAGMA table_info(guides)").fetchall()}
        for col, decl in (
            ("scope", "TEXT"),
            ("credits", "TEXT"),
            ("sources", "TEXT"),
            ("status", "TEXT"),
        ):
            if col not in cols:
                conn.execute(f"ALTER TABLE guides ADD COLUMN {col} {decl}")

        conn.execute("DELETE FROM guides")
        for d in docs:
            conn.execute(
                """
                INSERT INTO guides (
                    id, title, category, path, difficulty, safety_level,
                    rig_types, tags, tools, body_md, updated_at,
                    scope, credits, sources, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    d.scope,
                    " | ".join(d.credits),
                    " | ".join(d.sources),
                    d.status,
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
        if not row:
            return None
        d = dict(row)
        d["credits_list"] = [c.strip() for c in (d.get("credits") or "").split("|") if c.strip()]
        d["sources_list"] = [c.strip() for c in (d.get("sources") or "").split("|") if c.strip()]
        return d


def search_guides(query: str, database: Path | None = None, limit: int = 50) -> list[dict]:
    init_db(database)
    q = query.strip()
    if not q:
        return []
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
            like = f"%{q}%"
            rows = conn.execute(
                """
                SELECT *, substr(body_md, 1, 160) AS snippet
                FROM guides
                WHERE title LIKE ? OR body_md LIKE ? OR tags LIKE ?
                   OR IFNULL(credits,'') LIKE ? OR IFNULL(sources,'') LIKE ?
                ORDER BY title
                LIMIT ?
                """,
                (like, like, like, like, like, limit),
            ).fetchall()
        return [dict(r) for r in rows]
