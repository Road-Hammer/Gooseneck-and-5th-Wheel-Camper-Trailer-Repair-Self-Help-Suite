# STWL Camper / Trailer Self-Help Suite

**Gooseneck, 5th Wheel, Equine & Stock Trailer Repair + Offline Shop CMMS**

Chilton-style self-help for campers and trailers — **bumper pull, 5th wheel, gooseneck, equine, cattle/stock** — with a **service log / work-order system** and **vendor directory** linked to repair guides. Written for entry-level DIY, informed by 30+ years trucker judgment, copyright **STWL**.

**Copyright 2026 Susquehanna Timberwolf Lines, LLC (STWL)**

> Offline first. No cell tower required after install.

| Surface | Link |
|---------|------|
| **GitHub** | https://github.com/Road-Hammer/Gooseneck-and-5th-Wheel-Camper-Trailer-Repair-Self-Help-Suite |
| **Deploy guide** | [docs/DEPLOY_GITHUB_HUGGINGFACE.md](docs/DEPLOY_GITHUB_HUGGINGFACE.md) |
| **HF Space template** | [huggingface/README.md](huggingface/README.md) |

## Features

- **Repair library** — Markdown guides, full-text search (SQLite FTS5)
- **Equine & stock** — floors/mats, gates/dividers, livestock-aware categories
- **CMMS / shop desk** — assets, work orders (open → completed), labor/parts cost
- **Vendors** — phone book linked to guides & categories (shows on guide pages)
- **GitHub CI + Docker** — clone-and-run, or demo on Hugging Face Spaces

## Quick start (from GitHub)

```powershell
git clone https://github.com/Road-Hammer/Gooseneck-and-5th-Wheel-Camper-Trailer-Repair-Self-Help-Suite.git
cd Gooseneck-and-5th-Wheel-Camper-Trailer-Repair-Self-Help-Suite
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
stwl-camper index
stwl-camper serve --open
```

Open **http://127.0.0.1:8765**

### CLI

```text
stwl-camper index
stwl-camper search equine
stwl-camper serve
stwl-camper log add-rig "Cattle pot" --type stock_trailer
stwl-camper log add "Gate latch weld" --status open --category equine_stock
stwl-camper log summary
stwl-camper vendor add "Mobile Trailer Tech" --trade mobile_tech --phone 555-0100 --preferred
stwl-camper vendor list
```

## Hugging Face (online demo)

1. Create a **Docker** Space on Hugging Face  
2. Point it at this repo’s root `Dockerfile` (port **7860**)  
3. Use `huggingface/README.md` as the Space card  
4. Full steps: **[docs/DEPLOY_GITHUB_HUGGINGFACE.md](docs/DEPLOY_GITHUB_HUGGINGFACE.md)**

```bash
docker build -t stwl-camper-suite .
docker run --rm -p 7860:7860 -e STWL_DATA_DIR=/data -v stwl-data:/data stwl-camper-suite
```

**Campsite rule:** HF Spaces need internet. For dead zones, run the GitHub install locally.

## Layout

```text
content/                 # guides, wisdom, catalog (equine_stock, etc.)
src/stwl_camper_suite/   # FastAPI UI, CMMS, search
docs/                    # design, content policy, deploy
Dockerfile               # HF Spaces + local Docker
.github/workflows/       # CI + optional GHCR publish
huggingface/README.md    # Space card YAML + blurb
data/                    # local SQLite (gitignored runtime DB)
```

## Content policy

See [docs/CONTENT_POLICY.md](docs/CONTENT_POLICY.md). Original STWL writing + lawful public sources — **no pirated commercial manuals**.

## Copyright & license

| Layer | Terms |
|-------|--------|
| Software | [Apache-2.0](LICENSE) |
| Original STWL content | [COPYRIGHT.md](COPYRIGHT.md), [NOTICE](NOTICE) |

## Safety

Educational self-help only. Not a substitute for OEM procedures or qualified technicians. Brakes, hitching, floors under livestock, propane, and cargo errors can kill.
