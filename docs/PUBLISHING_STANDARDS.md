# Publishing standards — STWL Camper Suite

**Copyright 2026 Susquehanna Timberwolf Lines, LLC**

These rules apply before any guide appears on GitHub, in the app, or on Hugging Face.

## Hard rules

1. **No empty categories in the published catalog.**  
   `content/catalog.yaml` lists only categories that already have finished guides.  
   Future topics go in `docs/AUTHORING.md` only — never as empty cards in the UI.

2. **No placeholder guides.**  
   Do not publish “Coming soon”, “TBD”, outline-only, or half-written articles under `content/guides/` or `content/wisdom/`.

3. **No invented specifications.**  
   Do not publish torque values, wire pinouts, fuse ratings, magnet amperages, or OEM procedures unless they come from:
   - the user’s own placard / owner manual (instruct them to read *their* plate), or  
   - a cited public government source, or  
   - a measured procedure the guide teaches *how to measure* (not a guessed number).

4. **No “baked” generic repair recipes that pretend to be model-specific.**  
   Prefer inspection, recognition, stop conditions, and when to use a pro.  
   If a step depends on model/year, say so and send the reader to OEM data.

5. **Scope every guide.**  
   Frontmatter must include what systems and rig types the guide actually covers.  
   If a system is excluded (e.g. surge vs electric brakes), say so in the first screen of text.

6. **Safety-critical guides require:**
   - `safety_level` of `warning` or `stop` when appropriate  
   - **Stop conditions**  
   - **Pro help triggers**  
   - Clear statement that this is educational, not a substitute for OEM or a certified tech  

7. **Indexer enforces completeness.**  
   `stwl-camper index` rejects guides missing required frontmatter or required sections.

8. **Research is not publish.**  
   Authoring notes are never shown as library content until rewritten to these standards.

9. **Credit every publisher.**  
   Any fact, framework, standard, or material that is not pure STWL original experience **must** name the publisher/agency/manufacturer.  
   STWL original text is still credited: *Publisher: Susquehanna Timberwolf Lines, LLC (STWL)*.  
   Indexer **rejects** guides with neither `credits` nor `sources`.

## Required frontmatter (published guides)

```yaml
id: unique-kebab-id
title: Human title
category: must-match-catalog-id
rig_types: [list]
difficulty: 1-5
safety_level: info|caution|warning|stop
tools: []
tags: []
status: published
scope: One sentence — what this guide does and does not cover
credits:
  - "Publisher & original instructional text: Susquehanna Timberwolf Lines, LLC (STWL)"
sources:
  - "Named publisher / agency / manufacturer and what was used (no bare URLs without a name)"
```

## Required body sections

- Opening that states scope  
- Safety / applicability where needed  
- Actionable content (inspection or judgment) that is accurate as far as STWL states it  
- **Stop conditions** (for caution/warning/stop)  
- **Pro help triggers** (for caution/warning/stop)  

## Accuracy bar

If you are not sure a fact is true for most rigs, either:

- qualify it (“on many electric-brake trailers…”), or  
- remove it.

Better a short true guide than a long confident wrong one.

---

*Not legal advice.*
