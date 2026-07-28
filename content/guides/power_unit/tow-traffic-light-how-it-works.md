---
id: tow-traffic-light-how-it-works
title: Tow Traffic Light — How the Grade Works
category: power_unit
rig_types: [bumper_pull, travel_trailer, fifth_wheel, gooseneck, toy_hauler, cargo_trailer, equine_trailer, stock_trailer]
difficulty: 2
safety_level: stop
tools:
  - Vehicle door certification label / tire placard
  - OEM tow guide or official calculator for your exact truck
  - CAT scale or other certified scale (preferred)
  - Tongue-weight scale or method
tags: [tow, traffic-light, gcwr, payload, power-unit]
status: published
scope: >-
  Explains the STWL green/yellow/red combination grade. Does not publish
  manufacturer model tow charts. You must enter OEM numbers for your truck.
credits:
  - "Publisher & grading software: Susquehanna Timberwolf Lines, LLC (STWL)"
sources:
  - "Ford Motor Company — official towing materials and RV & Trailer Towing Guide concepts (GCWR, max trailer weight definitions) at ford.com/towing and Ford towing calculator"
  - "Ram Trucks — official towing capacity guide at ramtrucks.com (config-specific capabilities; confirm on window sticker)"
  - "General Motors / Chevrolet / GMC — official trailering/towing owner materials for exact configs"
  - "Vehicle certification labels (GVWR, GAWR, payload) — affixed by the vehicle manufacturer"
  - "Tongue/pin percentage bands as advisory teaching ranges (industry common practice; OEM/hitch maker supersedes)"
---

# Tow Traffic Light — How the Grade Works

The suite grades a **power unit + trailer** combination like a traffic light:

| Light | Meaning |
|-------|---------|
| **GREEN** | No hard limit exceeded on the numbers you entered; margins not “tight” |
| **YELLOW** | Caution: tight margin, missing critical OEM fields, assumed trailer weight, or tongue/pin % outside advisory band |
| **RED** | At least one hard limit exceeded — do not treat as acceptable |
| **GRAY** (check-level) | That single check lacks data |

## What “hard limits” means here

Using **your** entered OEM ratings and weights, the engine checks:

1. **GCWR** — truck trip weight + trailer trip weight ≤ Gross Combined Weight Rating  
2. **OEM max trailer weight** — trailer trip weight ≤ manufacturer max for *that* truck config  
3. **GVWR** — estimated truck-side load (including tongue/pin when known) ≤ truck GVWR  
4. **Payload** — people/cargo in truck + tongue/pin ≤ payload capacity  
5. **Hitch / max tongue or pin** — vertical load ≤ lesser of OEM tongue/pin max and hitch rating  
6. **Trailer GVWR** — trailer not over its own plate  
7. **Tongue/pin %** — advisory band only (not an automatic red)

## Where numbers must come from

| Number | Source (publisher) |
|--------|---------------------|
| GVWR, GAWR, payload | Certification label / placard on **your** vehicle (vehicle manufacturer) |
| GCWR, max trailer, max tongue | Owner manual + **official** OEM tow guide or calculator for **year/engine/axle/package** |
| Truck & trailer weights | Scale tickets (best) |
| Tongue/pin | Measured (scale/gauge), not guessed |

STWL does **not** ship a scraped database of every Ford/Ram/GM/Toyota row. That would be incomplete, stale, and often wrong for your option codes. The app stores **your** ratings and credits the publisher you used.

## Official OEM discovery portals (credit)

See also in-app **Tow Light** page list and `content/oem_tow_reference/publishers.yaml`:

- **Ford Motor Company** — ford.com towing / towing calculator  
- **Ram Trucks** — ramtrucks.com towing capacity guide  
- **GM / Chevrolet / GMC** — official brand trailering materials  
- **Toyota, Nissan, Jeep** — official brand sites / owner literature  

Always prefer the **label on the truck** and the **current** OEM guide for that model year.

## How to run a grade

1. **Power Units** — save the truck with GCWR, max trailer, payload, and rating publisher credit.  
2. **Tow Light** — enter scale weights + tongue/pin + hitch style.  
3. Read the **overall lamp** and every check’s **basis/credit** line.  
4. **RED** or unknown critical fields → do not tow until fixed.

## Credits & sources

| Role | Credit |
|------|--------|
| Grading logic & this guide | Susquehanna Timberwolf Lines, LLC (STWL) |
| Rating definitions & config tables | Vehicle manufacturers (Ford, Ram, GM, Toyota, etc.) via official materials |
| Certification labels | Affixed by the vehicle manufacturer |

## Stop conditions

- Overall **RED**  
- GCWR or max trailer unknown and you are near typical heavy-trailer weights  
- No scale weight and you are guessing “it looks fine”  

## Pro help triggers

- Commercial combinations under FMCSA rules  
- Conflicting OEM documents  
- Unstable sway even when numbers look green  
