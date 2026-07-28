---
title: STWL Camper Trailer Self-Help Suite
emoji: 🚛
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
license: apache-2.0
---

# STWL Camper / Trailer Self-Help Suite

**Copyright 2026 Susquehanna Timberwolf Lines, LLC (STWL)**

Offline-first repair guides + shop CMMS for campers, 5th wheels, goosenecks, **equine**, and **cattle/stock** trailers.

This Hugging Face **Docker Space** is a **demo / online desk**. For campsite use with no cell service, install from GitHub and run locally:

https://github.com/Road-Hammer/Gooseneck-and-5th-Wheel-Camper-Trailer-Repair-Self-Help-Suite

```bash
git clone https://github.com/Road-Hammer/Gooseneck-and-5th-Wheel-Camper-Trailer-Repair-Self-Help-Suite.git
cd Gooseneck-and-5th-Wheel-Camper-Trailer-Repair-Self-Help-Suite
pip install -e .
stwl-camper index
stwl-camper serve --open
```

## Features

- Repair guide library (entry-level DIY + trucker wisdom)
- Full-text search (SQLite FTS5)
- Service log / work orders (CMMS-style)
- Vendor directory linked to guides
- Equine & stock trailer categories

## Safety

Educational self-help only. Not a substitute for OEM manuals or qualified technicians.

## Deploy

See `docs/DEPLOY_GITHUB_HUGGINGFACE.md` in the GitHub repository.
