# OSINT Research Pipeline (Level 10 ambition, legal rails)

**Goal:** Build the broadest *original* catalog possible for bumper-pull, 5th-wheel, gooseneck, cargo, and related RV systems — without piracy.

## Stages

### 1. Map the universe

- Maintain `content/catalog.yaml` categories and `roadmap_topics`.
- Track coverage in `content/research/coverage_matrix.md` (percent complete per node).

### 2. Collect publicly available signals

Prioritize:

- Federal / state safety materials (cargo securement concepts, tire consumer info, recall databases).
- NHTSA / FMCSA plain-language publications.
- Manufacturer **public** owner manuals excerpts *only if license allows*; otherwise citation-only.
- Industry association free checklists.
- Parts-diagram *taxonomy* (what systems exist), not scanned dealer microfiche.

Store raw notes under:

```text
content/research/
  notes/YYYY-MM-DD-topic.md
  citations/
  outlines/
```

### 3. Triage

For each fact:

| Can we ship it as STWL original teaching? | Action |
|-------------------------------------------|--------|
| Yes — general skill / inspection / safety | Draft guide |
| Yes — with government citation | Draft + cite |
| No — OEM proprietary procedure | “Recognize & when to pro” guide only |
| No — copyrighted manual text | Leave in research; do not copy |

### 4. Rewrite (mandatory)

- Entry-level language.
- Tools, time, difficulty, safety_level.
- Steps numbered; photos optional later.
- **Stop conditions** and **pro help triggers**.
- Trucker wisdom modules separate from pure repair steps when the value is judgment, not torque.

### 5. Index offline

```bash
stwl-camper index
```

FTS5 index lives in the local SQLite DB — no network.

### 6. Pack releases

When online is available at home:

- Build content pack zip (guides + index metadata).
- Users copy pack to USB / folder for campground use.
- App never *requires* the pack download to use already-installed content.

## Quality bar (“Chilton for campers”)

A topic is **v1 complete** when it has:

1. What it is / why it fails  
2. Symptoms  
3. Tools  
4. Inspection steps  
5. DIY fix *or* clear pro boundary  
6. Service-log fields to record  
7. Related systems  

## Ethics

Legacy for family means **truthful and lawful**. Speed of catalog growth never justifies pasting someone else’s manual.
