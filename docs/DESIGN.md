# Design — STWL Camper / Trailer Self-Help Suite v0.1

## Problem

Camper and trailer owners (and small shops) need a **Chilton-style** companion that:

- Works **completely offline** (boondocking, dead zones, mountain passes).
- Covers bumper-pull through 5th-wheel and gooseneck systems.
- Teaches **entry-level DIY** without talking down to professionals.
- Captures **30+ years trucker** judgment on safe operation and cargo securement.
- Survives as a **STWL family legacy** with clean copyright.

## Product shape (combo)

| Surface | Role | Offline |
|---------|------|---------|
| Local web UI (`stwl-camper serve`) | Primary browse / search / log | Yes (localhost) |
| CLI | Index, log, export | Yes |
| Future: USB content packs | Update library at home | After install, yes |
| Future: desktop shell (Tauri) | Double-click app | Yes |

Cloud sync is **optional later**, never required for core.

## Architecture

```text
content/*.md  --index-->  SQLite (FTS5)  <--serve--  FastAPI + Jinja UI
user service log -------->  same SQLite (separate tables)
```

- **Single portable DB file** under `data/stwl_camper.db` (user machine).
- **Content stays files** so the library is git-friendly and human-editable for decades.
- **Search** is SQLite FTS5 (fast, zero network).

## Modules

1. **Catalog** — taxonomy + category browse  
2. **Guides** — Markdown repair / systems articles  
3. **Trucker wisdom** — operational judgment modules  
4. **Service log** — per-rig maintenance history  
5. **Search** — full-text across titles, tags, body  
6. **Export** — later: PDF pack / CSV log for kids’ archives  

## Performance choices

- No Electron for v0 (RAM and install size).
- No remote CDN fonts or scripts.
- Lazy render Markdown on request; optional cache in DB.
- Indexes rebuilt explicitly (`stwl-camper index`) so file edits are intentional.

## Security / liability posture

- Localhost bind default (`127.0.0.1`).
- Hard safety disclaimers in UI and safety-critical guides.
- Propane / structural / brake **pro boundaries** enforced in content standards.

## Roadmap (high level)

| Phase | Deliverable |
|-------|-------------|
| 0.1 | Scaffold, index, search UI, service log, seed guides |
| 0.2 | Full taxonomy stubs + coverage matrix |
| 0.3 | USB content pack builder |
| 0.4 | Per-rig profiles (VIN, axle ratings, tire sizes) |
| 0.5 | Desktop shell + optional mobile-friendly CSS polish |
| 1.0 | Catalog completeness review for “daily driver” DIY set |

## Copyright

Software: Apache-2.0.  
Original content: STWL copyright — see `COPYRIGHT.md`, `NOTICE`, `docs/CONTENT_POLICY.md`.
