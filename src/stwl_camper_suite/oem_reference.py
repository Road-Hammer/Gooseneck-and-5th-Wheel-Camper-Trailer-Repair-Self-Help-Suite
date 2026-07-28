"""Load credited OEM tow publisher index (no invented ratings)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .paths import content_dir, project_root


def oem_publishers_path() -> Path:
    return content_dir() / "oem_tow_reference" / "publishers.yaml"


def load_oem_publishers() -> list[dict[str, Any]]:
    path = oem_publishers_path()
    if not path.is_file():
        # fallback if content rooted differently
        alt = project_root() / "content" / "oem_tow_reference" / "publishers.yaml"
        path = alt if alt.is_file() else path
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    pubs = data.get("publishers") or []
    return [p for p in pubs if isinstance(p, dict) and p.get("publisher")]
