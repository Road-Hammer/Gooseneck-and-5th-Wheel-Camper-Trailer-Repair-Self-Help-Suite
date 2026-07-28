# Deploy & run from GitHub + Hugging Face

**Copyright 2026 Susquehanna Timberwolf Lines, LLC (STWL)**

This suite is **offline-first**. GitHub and Hugging Face are for **distribution, CI, and optional online demos** — not required at the campsite.

---

## Architecture (what goes where)

| Place | Role | Online needed? |
|-------|------|----------------|
| **GitHub repo** | Source of truth: code, guides, CI, releases | To clone/update only |
| **GitHub Releases / GHCR** | Versioned zip + Docker image | To download only |
| **Hugging Face Space (Docker)** | Public demo UI / always-on shop desk when you have net | Yes for the Space |
| **Hugging Face Dataset (optional)** | Large content packs / research dumps | Download once, then offline |
| **Your laptop / shop PC** | Real offline CMMS + full library | No after install |

```text
GitHub (code + content/)
    │
    ├─► git clone / pip install -e .     ──► local offline app
    │
    ├─► Docker image (GHCR)              ──► laptop / NAS / HF Space
    │
    └─► HF Dataset content packs (opt)   ──► STWL_CONTENT_DIR=...
```

---

## A) Run from GitHub (recommended for offline owners)

### 1. One-time auth (if private later)

```powershell
gh auth login
```

Public clone works without auth:

```powershell
cd $env:USERPROFILE\Python_Projects
git clone https://github.com/Road-Hammer/Gooseneck-and-5th-Wheel-Camper-Trailer-Repair-Self-Help-Suite.git
cd Gooseneck-and-5th-Wheel-Camper-Trailer-Repair-Self-Help-Suite
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
stwl-camper index
stwl-camper serve --open
```

Open **http://127.0.0.1:8765** — disconnect the network; it still works.

### 2. Update later (when you have signal)

```powershell
git pull
pip install -e .
stwl-camper index
```

### 3. Push your STWL work (maintainer)

```powershell
gh auth login
git add -A
git commit -m "Describe change"
git push origin master
```

CI (`.github/workflows/ci.yml`) runs tests on every push.

### 4. Docker from GitHub (optional)

```powershell
docker build -t stwl-camper-suite .
docker run --rm -p 8765:7860 -v ${PWD}/data:/data -e STWL_DATA_DIR=/data stwl-camper-suite
```

Then open http://127.0.0.1:8765 (mapped from container 7860).

On tag `v*`, workflow can publish to **ghcr.io/Road-Hammer/...** (see `docker-publish.yml`).

---

## B) Run / demo on Hugging Face Spaces

### Why HF?

- Share a **live demo** with family or shops who have internet  
- Same Docker image as local  
- Optional **persistent `/data`** for service log on the Space (not a substitute for USB backup)

### Create a Docker Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)  
2. SDK: **Docker**  
3. Space name e.g. `stwl-camper-suite`  
4. Visibility: public or private  

### Connect Space to this GitHub repo

**Option 1 — HF “Duplicate from GitHub” / sync**

- In Space settings, link the GitHub repository  
- HF builds the `Dockerfile` at the repo root  

**Option 2 — push repo into a Space git remote**

```powershell
# after creating the Space, HF shows a git URL like:
# https://huggingface.co/spaces/YOUR_USER/stwl-camper-suite
cd Gooseneck-and-5th-Wheel-Camper-Trailer-Repair-Self-Help-Suite
git remote add hf https://huggingface.co/spaces/YOUR_USER/stwl-camper-suite
git push hf master:main
```

Use a [HF access token](https://huggingface.co/settings/tokens) with **write** when prompted.

### Space settings

| Setting | Value |
|---------|--------|
| SDK | Docker |
| Port | **7860** (Dockerfile `EXPOSE 7860`, app uses `$PORT`) |
| Persistent storage | Enable if you want service log/vendors to survive rebuilds → mount as `/data` |
| Env | `STWL_DATA_DIR=/data` (already default in Dockerfile) |

### README for the Space

Copy `huggingface/README.md` front-matter into the Space README (or keep `huggingface/README.md` as the Space card template).

### Important offline note for HF users

A Space **requires internet** to open. For campsite use:

1. Clone from GitHub (or download a Release zip) while online  
2. Run `stwl-camper serve` offline  
3. Optionally download a **content pack** from HF Dataset once and point `STWL_CONTENT_DIR` at it  

---

## C) Optional: Hugging Face Dataset for content packs

Use a **Dataset** repo (not a Space) for large guide packs:

```text
Road-Hammer/stwl-camper-content
  packs/
    core-v0.1.zip
    equine-stock-v0.1.zip
```

Local use:

```powershell
# after download + unzip
$env:STWL_CONTENT_DIR = "C:\path\to\unpacked\content"
stwl-camper index
stwl-camper serve
```

Do **not** put private vendor phone lists or personal service logs in a public Dataset.

---

## D) Environment variables

| Variable | Meaning | Default |
|----------|---------|---------|
| `STWL_DATA_DIR` | Where `stwl_camper.db` lives | `./data` |
| `STWL_CONTENT_DIR` | Markdown library root | `./content` |
| `STWL_HOST` | Bind host | `127.0.0.1` |
| `STWL_PORT` / `PORT` | Bind port | `8765` / HF `7860` |

---

## E) Security notes

- Default local bind is **localhost** only.  
- Docker/HF bind **0.0.0.0** — do not expose a shop CMMS to the public internet without auth.  
- HF public Spaces are **demo** surfaces; keep real customer data local.  
- Service log DB may contain personal/business info — back up privately.

---

## F) Checklist: “it works from GitHub and Hugging Face”

- [ ] Repo pushed to GitHub; CI green  
- [ ] `git clone` + `pip install -e .` + `stwl-camper serve` works offline  
- [ ] Docker build succeeds  
- [ ] HF Docker Space builds and opens UI  
- [ ] (Optional) GHCR image published on version tag  
- [ ] (Optional) HF Dataset content pack download tested with `STWL_CONTENT_DIR`  

---

*Not legal advice. Copyright STWL — see COPYRIGHT.md / NOTICE.*
