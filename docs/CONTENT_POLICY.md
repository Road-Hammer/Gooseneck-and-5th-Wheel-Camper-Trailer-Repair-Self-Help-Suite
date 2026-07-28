# Content Policy — STWL Camper Suite

**Copyright 2026 Susquehanna Timberwolf Lines, LLC**

This suite aims for a **complete practical catalog**, not a warehouse of other people’s copyrighted books.

## Allowed

| Source type | How we use it |
|-------------|----------------|
| **Original STWL writing** | Primary voice: entry-level DIY + trucker operational wisdom |
| **U.S. government works** | Public domain (e.g. FMCSA cargo securement concepts, NHTSA consumer safety themes) — summarize in plain English; cite CFR / agency when relevant |
| **Open-licensed materials** | Only with compatible license + attribution in guide frontmatter or research notes |
| **Manufacturer public FAQs / recall pages** | Summarize facts; link or cite document ID; do not dump full OEM manuals |
| **Your firsthand experience** | Core differentiator — write it as STWL original instruction |

## Forbidden without written license

- Pasting or OCR’ing **commercial repair manuals** (Chilton, Haynes, OEM service manuals sold as product, etc.)
- Scraping paywalled dealer portals or subscription TSBs wholesale
- Copying YouTube transcripts or forum posts as if they were STWL text
- Using trademarks of other brands in a way that implies OEM endorsement

## “Level 10 OSINT” rule for this repo

1. **Research** freely into `content/research/` (notes, links, outlines, citation lists).
2. **Rewrite** into original STWL DIY guides before anything ships in `content/guides/` or `content/wisdom/`.
3. Every promoted guide lists **sources_consulted** (optional YAML) when facts came from public regs or standards.
4. Prefer **teach the principle + inspection steps** over proprietary torque tables when OEM data is copyrighted; tell the user to use **their placard / owner manual** for model-specific numbers.

## Safety disclaimer (required in product UI)

Educational self-help only. Not a substitute for OEM procedures, certified technicians, or applicable law. Brakes, hitching, propane, electrical, structural, and cargo securement errors can kill. When in doubt, stop and get qualified help.

## Hybrid content model

| Layer | Owner | Offline? |
|-------|--------|----------|
| Core guides + wisdom | STWL | Always shipped |
| User service log | User device SQLite | Always local |
| Optional content packs | STWL releases | Downloaded when online, then fully offline |
| Research inbox | Authoring only | Dev machine |

---

*Not legal advice.*
