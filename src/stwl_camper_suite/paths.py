from __future__ import annotations

import os
from pathlib import Path


def package_root() -> Path:
    return Path(__file__).resolve().parent


def project_root() -> Path:
    """Repo root: .../Gooseneck-.../ (parent of src/)."""
    return package_root().parent.parent


def content_dir() -> Path:
    """Markdown library. Override with STWL_CONTENT_DIR (HF mount / content pack)."""
    override = os.environ.get("STWL_CONTENT_DIR", "").strip()
    if override:
        return Path(override)
    return project_root() / "content"


def data_dir() -> Path:
    """
    User database directory (service log, vendors).
    Override with STWL_DATA_DIR for Hugging Face Spaces persistent storage (/data).
    """
    override = os.environ.get("STWL_DATA_DIR", "").strip()
    d = Path(override) if override else project_root() / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def db_path() -> Path:
    return data_dir() / "stwl_camper.db"


def catalog_path() -> Path:
    return content_dir() / "catalog.yaml"
