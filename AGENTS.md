# AGENTS.md — STWL Camper / Trailer Self-Help Suite

## Mission

Build an **offline-first** “Chilton-style” self-help suite for campers, trailers, 5th wheels, goosenecks, and RVs: repair guides, systems knowledge, owner service log, safe operation, and cargo securement — written for **entry-level DIY**, informed by **30+ years trucker operational practice**, copyrighted by **STWL (Susquehanna Timberwolf Lines, LLC)**.

## Non-negotiables

1. **Offline first.** Full catalog browse, full-text search, and service log must work with no internet and no cellular.
2. **Entry-level DIY language.** Short steps, tool lists, torque/safety callouts, “when to stop and call a pro.”
3. **No piracy.** Never paste commercial manuals or scrape manufacturer paid literature. Original STWL writing + properly licensed / public sources only (`docs/CONTENT_POLICY.md`).
4. **Safety over cleverness.** Brakes, hitching, propane, electrical, and cargo securement get hard stop / pro warnings.
5. **STWL copyright** on original content; software under Apache-2.0 unless counsel changes that.
6. **Performance.** SQLite + FTS5, local FastAPI, static assets; no cloud dependency for core features.

## Stack (v0)

| Layer | Choice | Why |
|--------|--------|-----|
| Runtime | Python 3.11+ | Fast local tooling, matches STWL Python projects |
| App server | FastAPI + Uvicorn (localhost only) | Fast local UI without Electron bloat |
| Data | SQLite + FTS5 | Offline, portable, excellent search |
| Guides | Markdown + YAML frontmatter under `content/` | Human-editable legacy content |
| UI | Server-rendered Jinja + light CSS | Works on weak hardware, offline |

Future options (not required for v0): Tauri shell, PWA packaging, mobile export packs.

## Layout

```text
content/           # guides, wisdom, catalog taxonomy (source of truth)
data/              # local user DB (gitignored runtime; schema via code)
src/stwl_camper_suite/  # app, db, search, service log, CLI
docs/              # design, content policy, OSINT pipeline
tests/             # unit tests
```

## Commands

```bash
pip install -e .
stwl-camper index          # rebuild FTS index from content/
stwl-camper serve          # open offline UI on http://127.0.0.1:8765
stwl-camper log list       # service log CLI
pytest
```

## Content authoring rules

- Frontmatter: `id`, `title`, `category`, `rig_types`, `difficulty`, `tools`, `safety_level`, `tags`
- Categories match `content/catalog.yaml`
- Every safety-critical guide ends with **Stop conditions** and **Pro help triggers**
- Prefer checklists over walls of text

## OSINT / research

Use `docs/OSINT_PIPELINE.md`. Ingest notes into `content/research/` as citations and outlines; rewrite into original STWL DIY guides before promoting to `content/guides/`.
