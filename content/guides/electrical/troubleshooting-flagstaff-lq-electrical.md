---
id: troubleshooting-flagstaff-lq-electrical
title: Electrical Troubleshooting — Full-Size Flagstaff LQ (Test Model)
category: electrical
rig_types: [travel_trailer, fifth_wheel, toy_hauler, bumper_pull]
difficulty: 3
safety_level: stop
tools:
  - Multimeter / 12V test light
  - Flashlight / inspection mirror
  - Screwdrivers / panel tools
  - Battery hydrometer or monitor (if lead-acid)
  - Camera for damage photos
  - Gloves / mask if rodent debris present
tags: [troubleshooting, electrical, flagstaff, forest-river, mice, rodent, 12v, 120v, living-quarters]
status: published
scope: >-
  Stepwise electrical troubleshooting for a full-size living-quarters travel
  trailer using Forest River Flagstaff (and similar Flagstaff Super Lite /
  Classic-class coaches) as the worked test model. Includes suspected mice
  damage. Not a floorplan-specific wiring book — use the Flagstaff/Forest River
  owner manual and schematics for your VIN. Not a substitute for a licensed
  RV tech or electrician when 120 V or fire risk is involved.
credits:
  - "Publisher & troubleshooting method: Susquehanna Timberwolf Lines, LLC (STWL)"
sources:
  - "Forest River Inc. — Flagstaff brand travel trailers (full-size Super Lite / Classic and related lines) owner materials at forestriverinc.com; floorplans and systems vary by model year"
  - "Industry RV 12 V / 120 V architecture (battery, converter/charger, distribution panels, GFCI) as taught in coach OEM manuals generally"
  - "Hopkins / Hoppy and SAE J2863 pin conventions for tow connector side — see STWL pin-chart guide"
  - "Public wildlife/RV damage practice — rodents chew insulation and nest in walls, under floors, and in looms; treat as fire and short risk"
  - "NFPA / general electrical safety: de-energize before opening panels; GFCI and shore power hazards"
---

# Electrical Troubleshooting — Full-Size Flagstaff LQ (Test Model)

## Test model (how we use “Flagstaff”)

**Test coach:** full-size **Forest River Flagstaff** living-quarters travel trailer  
(examples of the family: **Flagstaff Super Lite**, **Flagstaff Classic**, and similar full-size Flagstaff towables with kitchen/bath/120 V systems).

| Field | STWL test-model assumption |
|-------|----------------------------|
| Brand | **Flagstaff** (Forest River) |
| Class | Full-size travel trailer with **living quarters** |
| Power | **12 V DC** house battery + **120 V AC** shore / generator / inverter (as equipped) |
| Tow plug | Light-vehicle **7-way blade** (not SAE J560 CMV) |
| Scenario | Owner reports intermittent lights / dead 12 V / blown fuses; **mice suspected** |

**Your real unit may differ.** Always open the **owner manual for your exact Flagstaff model year and floorplan**. STWL is not Forest River and does not publish Flagstaff OEM schematics.

---

## Safety first (stop-level)

1. **Unplug shore power** before opening distribution panels or converter.  
2. **Turn off battery disconnect** (if equipped) when probing 12 V looms.  
3. **Do not** smell for gas with ignition sources while chasing wires near propane appliances.  
4. **Rodent nests** can hold urine/droppings — mask, gloves; avoid stirring dust.  
5. **Chewed wires + insulation = fire risk** — if you smell burning plastic or see charring, stop and get a pro.

---

## Split the problem: 12 V house vs 120 V house vs tow lights

| Symptom cluster | Start here |
|-----------------|------------|
| Interior lights, pump, furnace fan, slides (12 V) | **12 V house** path below |
| Outlets, microwave, A/C, converter plug-in side | **120 V / shore** path |
| Running lights / brakes only when hitched | **Tow plug / 7-way** (see pin charts + 7-way basics) |
| Everything random after storage | **Rodent damage sweep** first |

---

## Path 1 — 12 V house dead or weak (Flagstaff LQ)

Work top-down:

1. **Battery**  
   - Voltage at rest (healthy lead-acid often ~12.6 V+ fully charged — use your battery type’s chart).  
   - Corroded terminals, loose lugs, damaged cables (mice love soft insulation near battery boxes).  

2. **Battery disconnect / cut-off**  
   - Confirm switch is ON for house loads.  

3. **Converter / charger**  
   - On shore power, does converter put charge voltage on battery?  
   - Cooling fan, smell of burnt electronics → stop, pro.  

4. **12 V distribution / fuse panel**  
   - Note **which fuse** is blown.  
   - Replace once with correct amp; if it blows again → short (often chewed pair).  

5. **Load test by branch**  
   - Lights only? Pump only? Slide? Maps to fuse labels on the Flagstaff panel (label text varies by year).  

6. **Grounds**  
   - Clean frame/battery grounds; rodent chew can leave a wire “looking connected” but copper gone.

---

## Path 2 — 120 V issues (outlets / A/C)

1. Shore cord seated; pedestal breaker on; **correct amp** cord for service (30 A vs 50 A as equipped).  
2. **EMS / surge protector** (if used) showing fault?  
3. Coach **main breaker** and branch breakers.  
4. **GFCI** outlets tripped (kitchen/bath/exterior) — reset; if immediate re-trip → wet or shorted device.  
5. Converter not running when on shore → check AC input breaker to converter.  

**Do not** open the converter case unless you are qualified.

---

## Path 3 — Tow lights / electric brakes only when hitched

1. Confirm **7-way blade** fully seated (not J560).  
2. Use pin chart: [wiring-pin-charts-hoppy-j560](/guide/wiring-pin-charts-hoppy-j560).  
3. Ground at tongue and frame.  
4. Test truck side vs trailer side.  
5. Brake magnet amp draw if brakes never apply (pro if unsure).  

Mice also chew **tongue harness** and **belly looms** forward of the axles.

---

## Suspected mice damage — inspection map (Flagstaff-class LQ)

Rodents enter through gaps at wet bay, underbelly, refrigerator roof vents, storage doors, and wire chases. On a full-size Flagstaff, prioritize:

| Zone | What to look for |
|------|------------------|
| **Underbelly / belly pan** | Droppings, shredded insulation, chewed loom tape |
| **Battery box / converter area** | Stripped 12 V cables, nest material |
| **Behind fridge / furnace** | Chewed AC/DC lines, foil insulation nests |
| **Under sinks / wet bay** | Soft PEX *and* nearby low-voltage control wires |
| **Slide rooms** | Flex looms at slide; intermittent when slide moves |
| **Ceiling / AC ducts** | Nest debris; do not run fan full blast into droppings |
| **Tongue / A-frame harness** | Tow plug pigtail chewed |

### Damage signatures

- Clean **V-shaped** chew marks on copper  
- Green corrosion powder on exposed copper  
- Fuse that only blows when a slide or pump runs  
- “Works until I hit a bump” → broken strand in chewed wire  

### Immediate actions if mice confirmed

1. Photograph damage for insurance / service log.  
2. Remove nests safely; sanitize hard surfaces (follow product labels).  
3. Repair **all** damaged conductors — do not tape over bare copper long-term.  
4. Seal entry points (steel wool + proper sealant where appropriate; avoid blocking required vents).  
5. Traps/bait **per label** and away from pets/kids; consider professional pest control.  
6. Recheck **propane lines** visually (if chewing near gas — **pro only** for gas fittings).  

---

## Decision tree (quick)

```
Symptom?
├─ Only when plugged to truck → 7-way / truck / tongue harness
├─ Only on shore power → 120 V pedestal / GFCI / converter AC
├─ 12 V house only → battery → disconnect → fuses → branch
└─ Random / after storage → rodent sweep → then above
```

---

## Flagstaff test-model log template (copy into service log)

```
Unit: Flagstaff (Forest River) — full-size LQ travel trailer
Model year / floorplan: ________
VIN (unit only): ________
Symptom: ________
Shore / battery / hitched: ________
Fuses found blown: ________
Mice evidence Y/N: zones ________
Repairs: ________
Parts: ________
Prior owner count (number only): ________
```

---

## Related STWL guides

- [7-way plug basics](/guide/7-way-plug-basics)  
- [Pin charts Hopkins/Hoppy + J560](/guide/wiring-pin-charts-hoppy-j560)  
- Plumbing troubleshooting (Flagstaff LQ) — separate section  

## Credits & sources

| Role | Credit |
|------|--------|
| Troubleshooting method & Flagstaff test framing | Susquehanna Timberwolf Lines, LLC (STWL) |
| Flagstaff brand / full-size towable product family | Forest River Inc. — Flagstaff lines (forestriverinc.com) |
| System architecture | Coach OEM manuals generally; your Flagstaff manual for this VIN |
| Tow connector standards | Hopkins/Hoppy; SAE J2863 |
| Rodent electrical risk | Field practice; treat as fire/short hazard |

## Stop conditions

- Burning smell, smoke, or charring  
- Repeated main fuse/breaker trips after proper reset  
- Chewed wires inside walls you cannot access safely  
- Any propane component disturbance  

## Pro help triggers

- Inverter/converter replacement  
- Full underbelly loom rewire  
- Slide harness damage  
- Insurance claim documentation needs certified shop  
