---
id: wiring-pin-charts-hoppy-j560
title: Trailer Wiring Pin Charts — Hopkins/Hoppy Light-Duty & SAE J560 CMV
category: electrical
rig_types: [bumper_pull, travel_trailer, fifth_wheel, gooseneck, cargo_trailer, utility_trailer, equine_trailer, stock_trailer]
difficulty: 2
safety_level: warning
tools:
  - 12V test light or multimeter
  - Wire colors reference (this chart)
  - Connector pin probe (careful — do not short pins)
tags: [wiring, pinout, 7-way, hoppy, hopkins, j560, cmv, sae]
status: published
scope: >-
  Standard pin/function charts for common North American light-vehicle trailer
  connectors as published/used by Hopkins (Hoppy) style aftermarket products
  and SAE J2863 blade conventions, plus the SAE J560 seven-conductor connector
  used on commercial motor vehicles. Not a substitute for measuring your harness
  or reading your vehicle OEM diagram. Wire colors can vary by harness brand.
credits:
  - "Publisher & teaching layout: Susquehanna Timberwolf Lines, LLC (STWL)"
sources:
  - "Hopkins Towing Solutions / Hoppy — trailer wiring diagrams and connector product literature (aftermarket light-vehicle connectors; Hoppy is a Hopkins brand line)"
  - "SAE International — SAE J2863 Automotive Trailer Tow Connector (7-way blade light-vehicle convention)"
  - "SAE International — SAE J560 Primary and Auxiliary Seven Conductor Electrical Connector for Truck-Trailer Jumper Cable (CMV / heavy-duty 7-way round)"
  - "Wikipedia summary of North American trailer connectors citing SAE J560 and SAE J2863 (cross-check only; prefer SAE/Hopkins primary docs)"
  - "CURT Manufacturing public towing electrical wiring education (notes traditional RV blade color schemes vs SAE J2863 colors)"
  - "Erich Jaeger and industry SAE J560 contact allocation tables (commercial 7-pin function/color summaries)"
---

# Trailer Wiring Pin Charts — Hopkins/Hoppy Light-Duty & SAE J560 CMV

**Two different worlds:**

| World | Typical plug | Standard / practice | Electric trailer brakes? |
|-------|--------------|---------------------|---------------------------|
| **Light vehicle / RV / most horse & cargo trailers** | Flat 4-way; 7-way **blade** (“RV 7-way”) | Industry practice + **SAE J2863**; aftermarket **Hopkins / Hoppy** kits | **Yes** — blue wire to controller |
| **CMV / heavy truck & semi trailer** | 7-way **round** (large metal/nylon) | **SAE J560** (U.S. commercial standard) | **No electric-brake pin** — service brakes are **air**; pin 7 is ABS/aux power |

**Never assume** a “7-way” on a pickup is the same as a “7-way” on a semi. They are **different shapes** and **different pin functions**.

**Wire colors are not law.** Always meter the circuit. Some harnesses use “traditional RV” colors that differ from SAE J2863 color names.

---

## Part A — Light duty (Hopkins / Hoppy style & SAE J2863)

### A1. Flat 4-way (most common light utility)

Common on small utility trailers and as a light-only subset of larger plugs.

| Function | Typical wire color | Notes |
|----------|-------------------|--------|
| Ground | **White** | Bond to clean frame metal |
| Tail / marker / plate | **Brown** | Running lights |
| Left turn + stop | **Yellow** | Combined turn/stop (U.S. style) |
| Right turn + stop | **Green** | Combined turn/stop |

**Credit:** Industry-common flat-4 convention; Hopkins/Hoppy and etrailer-style aftermarket diagrams; SAE J2863 family documentation for light-vehicle trailer tow connectors.

### A2. Flat 5-way

Same as 4-way **plus** one more circuit, often:

| Function | Typical wire color |
|----------|-------------------|
| Reverse / surge-brake unlock | **Purple** (sometimes red) |

Used so **surge brakes** do not apply when backing (when wired for that purpose).

### A3. 7-way blade — SAE J2863 style (modern light / RV “Hoppy” world)

Physical style: **flat blades** in a round housing (common Hoppy/Hopkins 7-way RV blade).

| Function | Typical color (SAE J2863-style naming) | Notes |
|----------|----------------------------------------|--------|
| Ground | **White** | Must be solid |
| Left turn + stop | **Yellow** | |
| Tail / markers | **Brown** | |
| Battery / +12 V charge or aux | **Black** (J2863) | Often ignition or battery feed — fuse properly |
| Right turn + stop | **Green** | |
| Electric brakes | **Blue** | From **brake controller** only |
| Reverse lamps | **Purple** | |

**Credit:** SAE J2863 *Automotive Trailer Tow Connector*; Hopkins Towing Solutions / Hoppy product wiring literature; Wikipedia North America connector summary citing J2863.

### A4. 7-way blade — “traditional RV” color names (same functions, different colors)

Some older harnesses and molded plugs use **different color labels** for the **same pin jobs**:

| Function | Traditional RV colors (common aftermarket) |
|----------|-----------------------------------------------|
| Ground | White |
| Left turn/stop | **Red** |
| Tail lights | **Green** |
| Right turn/stop | **Brown** |
| Electric brakes | Blue |
| +12 V | Black |
| Reverse | Yellow |

**Pin positions** for functions usually match; **colors do not**. Meter every wire.

**Credit:** CURT Manufacturing public towing electrical education (traditional vs SAE J2863 color configurations); Hopkins notes that color coding is not universal among all manufacturers.

### A5. Quick 6-way round (light/medium, less common)

Often: ground, tail, L stop/turn, R stop/turn, electric brakes, reverse — **no separate +12 V** on some versions. Confirm with the product sheet for the exact connector.

---

## Part B — CMV / heavy duty — SAE J560 (best industry standard)

For **commercial motor vehicles** and most **semi / heavy trailers**, the reviewed industry standard in the U.S. is **SAE J560** (seven-conductor electrical connector for truck–trailer jumper cables). This is the correct reference—not the light-vehicle blade plug.

### Critical CMV facts

1. **Shape:** Large **round pin** 7-way (not blade).  
2. **Brakes:** Service brakes are **pneumatic (air)**. J560 **does not** carry electric-brake controller PWM the way a light 7-way blue wire does.  
3. **Pin 7:** Power for **ABS** and auxiliary electrical loads (heavy wire).  
4. **Primary vs AUX:** SAE J560 defines **primary** (lighting/ABS-related) and **auxiliary** connectors; AUX is keyed/marked and **not** interchangeable with primary.  
5. **Voltage:** SAE J560 is **12 V** nominal with heavy conductors; do not confuse with European **24 V** ISO 1185 systems even though the shells look similar.

### SAE J560 function / color summary (common industry table)

| Contact | Function | Typical insulation color | Notes |
|---------|----------|--------------------------|--------|
| 1 | Ground return to tow vehicle | **White** | Heavy gauge |
| 2 | Clearance, side marker, ID lamps | **Black** | |
| 3 | Left turn / hazard | **Yellow** | |
| 4 | Stop lamps | **Red** | Brake-light signal |
| 5 | Right turn / hazard | **Green** | |
| 6 | Tail / plate lamps | **Brown** | |
| 7 | ABS / auxiliary power | **Blue** | **Not** light-duty “electric brake controller” |

**Credit:** SAE International **SAE J560**; industry contact-allocation summaries (e.g. Erich Jaeger SAE J560 tables); Wikipedia *Trailer connectors in North America* (secondary summary of J560).

### Why J560 is the CMV “best reviewed” choice

- Issued for the **U.S. commercial truck–trailer** industry (long-standing SAE standard; original commercial connector work dating to mid-20th century practice).  
- Widely required/expected on **air-brake** combinations.  
- Separate from light-vehicle **SAE J2863** blade connectors used on pickups and RVs.  
- STWL does **not** substitute a random “best Amazon 7-way” for CMV—**use SAE J560** hardware and wiring practice for commercial units.

---

## Adapters & gotchas

| Situation | Risk |
|-----------|------|
| Blade 7-way plugged into wrong adaptation to J560 | **Wrong functions / damage** — physical adapters exist but wiring must match |
| Assuming blue = brakes on a semi | On J560, blue/pin 7 is **ABS/aux**, not electric drum magnets |
| Mixing traditional RV colors with J2863 labels | Miswired lights/brakes |
| Bad ground | Dead or weird multi-circuit failures |

---

## How to use these charts in the field

1. Identify **plug family** (flat 4, blade 7, round J560).  
2. Pick the matching table above.  
3. **Meter** each pin before splicing.  
4. Log work in the **service log** with connector type.  
5. For CMV, use **J560** docs and OEM tractor/trailer schematics.

---

## Credits & sources

| Source | Role |
|--------|------|
| **Hopkins Towing Solutions / Hoppy** | Aftermarket light-vehicle connector product wiring diagrams |
| **SAE J2863** | Light-vehicle automotive trailer tow connector standard |
| **SAE J560** | CMV seven-conductor truck–trailer jumper connector standard |
| **CURT** | Public education on traditional vs J2863 color naming |
| **Erich Jaeger / industry J560 tables** | Commercial pin allocation summaries |
| **STWL** | This teaching guide |

## Stop conditions

- You cannot identify whether you have **blade** vs **J560** hardware  
- You are about to splice without metering  
- CMV air-brake unit being wired as if it were light electric-brake  

## Pro help triggers

- Multiplex truck wiring / body control modules  
- ABS faults after connector work  
- Any doubt on a commercial combination  
