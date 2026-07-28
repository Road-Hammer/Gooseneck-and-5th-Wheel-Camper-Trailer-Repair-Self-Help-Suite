---
id: using-shop-cmms
title: Using the Offline Shop CMMS
category: service_log
rig_types: [bumper_pull, fifth_wheel, gooseneck, equine_trailer, stock_trailer, cattle_trailer, cargo_trailer]
difficulty: 1
safety_level: info
tools: []
tags: [cmms, service-log, vendors, work-orders, shop]
status: published
scope: >-
  How to use this suite’s offline assets, work orders, and vendor directory.
  Not a third-party CMMS product manual.
credits:
  - "Publisher & original instructional text: Susquehanna Timberwolf Lines, LLC (STWL)"
sources:
  - "STWL Camper / Trailer Self-Help Suite software documentation (this repository)"
---

# Using the Offline Shop CMMS

This suite includes a lightweight **offline** maintenance tracker (assets, work orders, vendors). It is original STWL software documentation — not SAP, Maximo, or any other CMMS brand.

## Pieces

| Piece | Meaning |
|-------|---------|
| **Assets (rigs)** | Trailers/campers you track |
| **Work orders** | open → in progress → waiting parts/vendor → completed |
| **Service log** | History on your machine |
| **Vendors** | Shops/techs you enter |
| **Guide links** | Vendors can be linked to a published guide or category |

## Typical flow

1. Add an asset (name, type, VIN if known).  
2. Add vendors you actually use; mark preferred if desired.  
3. Link a vendor to a guide or category when they specialize in that work.  
4. Open a work order; attach asset, vendor, and guide when relevant.  
5. Log labor, parts cost, invoice reference.  
6. Set status to **completed** when finished.

## Data location

Local SQLite file under `data/` (or `STWL_DATA_DIR`). Back it up to USB when you can. Your vendor list and history are **yours** — not uploaded by this offline app.

## Credits & sources

| Role | Credit |
|------|--------|
| Publisher / software & this guide | Susquehanna Timberwolf Lines, LLC (STWL) |

## Stop conditions

Not a repair procedure.

## Pro help triggers

Use the repair guides and qualified shops for mechanical failures; this page only documents the log.
