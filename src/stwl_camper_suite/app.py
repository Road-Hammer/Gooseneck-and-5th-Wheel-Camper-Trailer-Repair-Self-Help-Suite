from __future__ import annotations

import markdown
from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import __copyright__, __version__
from .cmms import (
    PRIORITIES,
    RIG_TYPES,
    VENDOR_TRADES,
    WORK_STATUSES,
    add_entry,
    add_rig,
    add_vendor,
    link_vendor_to_guide,
    list_entries,
    list_rigs,
    list_vendor_links,
    list_vendors,
    shop_summary,
    update_entry_status,
    vendors_for_guide_or_category,
)
from .content_loader import get_guide, list_guides, load_catalog, rebuild_index, search_guides
from .db import init_db
from .paths import package_root

TEMPLATES = Jinja2Templates(directory=str(package_root() / "templates"))
STATIC_DIR = package_root() / "static"


def _int_or_none(value: str) -> int | None:
    value = (value or "").strip()
    return int(value) if value.isdigit() else None


def _float_or_none(value: str) -> float | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def create_app() -> FastAPI:
    init_db()
    if not list_guides():
        rebuild_index()

    app = FastAPI(
        title="STWL Camper / Trailer Self-Help Suite",
        version=__version__,
        docs_url=None,
        redoc_url=None,
    )
    if STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    def base_ctx(**extra):
        catalog = load_catalog()
        return {
            "version": __version__,
            "copyright": __copyright__,
            "catalog": catalog,
            "categories": (catalog.get("categories") or []),
            "rig_types": RIG_TYPES,
            "work_statuses": WORK_STATUSES,
            "priorities": PRIORITIES,
            "vendor_trades": VENDOR_TRADES,
            **extra,
        }

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request):
        guides = list_guides()
        by_cat: dict[str, list] = {}
        for g in guides:
            by_cat.setdefault(g["category"], []).append(g)
        summary = shop_summary()
        return TEMPLATES.TemplateResponse(
            request,
            "home.html",
            base_ctx(
                guide_count=len(guides),
                by_cat=by_cat,
                recent_log=list_entries(limit=5),
                open_work=list_entries(open_only=True, limit=8),
                summary=summary,
            ),
        )

    @app.get("/search", response_class=HTMLResponse)
    def search(request: Request, q: str = Query("")):
        results = search_guides(q) if q.strip() else []
        return TEMPLATES.TemplateResponse(
            request,
            "search.html",
            base_ctx(q=q, results=results),
        )

    @app.get("/category/{category_id}", response_class=HTMLResponse)
    def category(request: Request, category_id: str):
        guides = list_guides(category=category_id)
        cat_meta = next(
            (c for c in (load_catalog().get("categories") or []) if c.get("id") == category_id),
            {"id": category_id, "title": category_id, "description": ""},
        )
        linked_vendors = list_vendors(category=category_id)
        return TEMPLATES.TemplateResponse(
            request,
            "category.html",
            base_ctx(cat=cat_meta, guides=guides, linked_vendors=linked_vendors),
        )

    @app.get("/guide/{guide_id}", response_class=HTMLResponse)
    def guide(request: Request, guide_id: str):
        doc = get_guide(guide_id)
        if not doc:
            return HTMLResponse("<h1>Guide not found</h1><p><a href='/'>Home</a></p>", status_code=404)
        html = markdown.markdown(
            doc["body_md"],
            extensions=["tables", "fenced_code", "nl2br"],
        )
        vendors = vendors_for_guide_or_category(guide_id, doc.get("category"))
        return TEMPLATES.TemplateResponse(
            request,
            "guide.html",
            base_ctx(guide=doc, body_html=html, guide_vendors=vendors),
        )

    # ----- Shop / CMMS -----

    @app.get("/shop", response_class=HTMLResponse)
    def shop_page(request: Request):
        return TEMPLATES.TemplateResponse(
            request,
            "shop.html",
            base_ctx(
                summary=shop_summary(),
                open_work=list_entries(open_only=True, limit=50),
                recent=list_entries(limit=15),
                rigs=list_rigs(),
                vendors=list_vendors(),
            ),
        )

    @app.get("/log", response_class=HTMLResponse)
    def log_page(request: Request, status: str = Query("")):
        if status == "open":
            entries = list_entries(open_only=True, limit=200)
        elif status:
            entries = list_entries(status=status, limit=200)
        else:
            entries = list_entries(limit=200)
        return TEMPLATES.TemplateResponse(
            request,
            "log.html",
            base_ctx(
                entries=entries,
                rigs=list_rigs(),
                vendors=list_vendors(),
                guides=list_guides(),
                filter_status=status,
                summary=shop_summary(),
            ),
        )

    @app.post("/log/rig")
    def log_add_rig(
        name: str = Form(...),
        rig_type: str = Form(""),
        vin: str = Form(""),
        notes: str = Form(""),
        make: str = Form(""),
        model: str = Form(""),
        year: str = Form(""),
        plate: str = Form(""),
        gvwr: str = Form(""),
    ):
        y = _int_or_none(year)
        add_rig(
            name,
            rig_type=rig_type or None,
            vin=vin or None,
            notes=notes or None,
            make=make or None,
            model=model or None,
            year=y,
            plate=plate or None,
            gvwr=_float_or_none(gvwr),
        )
        return RedirectResponse("/log", status_code=303)

    @app.post("/log/entry")
    def log_add_entry(
        title: str = Form(...),
        performed_at: str = Form(""),
        category: str = Form(""),
        details: str = Form(""),
        miles: str = Form(""),
        cost: str = Form(""),
        labor_hours: str = Form(""),
        labor_cost: str = Form(""),
        parts_cost: str = Form(""),
        parts: str = Form(""),
        rig_id: str = Form(""),
        vendor_id: str = Form(""),
        guide_id: str = Form(""),
        status: str = Form("completed"),
        priority: str = Form("normal"),
        performed_by: str = Form(""),
        invoice_ref: str = Form(""),
        wo_number: str = Form(""),
    ):
        add_entry(
            title,
            rig_id=_int_or_none(rig_id),
            vendor_id=_int_or_none(vendor_id),
            guide_id=guide_id.strip() or None,
            wo_number=wo_number.strip() or None,
            performed_at=performed_at or None,
            category=category or None,
            details=details or None,
            status=status or "completed",
            priority=priority or "normal",
            performed_by=performed_by or None,
            miles=_float_or_none(miles),
            labor_hours=_float_or_none(labor_hours),
            labor_cost=_float_or_none(labor_cost),
            parts_cost=_float_or_none(parts_cost),
            cost=_float_or_none(cost),
            parts=parts or None,
            invoice_ref=invoice_ref or None,
        )
        return RedirectResponse("/log", status_code=303)

    @app.post("/log/status")
    def log_set_status(
        entry_id: str = Form(...),
        status: str = Form(...),
    ):
        eid = _int_or_none(entry_id)
        if eid is not None:
            update_entry_status(eid, status)
        return RedirectResponse("/log", status_code=303)

    # ----- Vendors -----

    @app.get("/vendors", response_class=HTMLResponse)
    def vendors_page(request: Request):
        return TEMPLATES.TemplateResponse(
            request,
            "vendors.html",
            base_ctx(
                vendors=list_vendors(active_only=False),
                guides=list_guides(),
                links=list_vendor_links(),
            ),
        )

    @app.post("/vendors/add")
    def vendors_add(
        name: str = Form(...),
        trade: str = Form(""),
        phone: str = Form(""),
        email: str = Form(""),
        website: str = Form(""),
        address: str = Form(""),
        city: str = Form(""),
        state: str = Form(""),
        zip: str = Form(""),
        specialties: str = Form(""),
        notes: str = Form(""),
        preferred: str = Form(""),
        link_guide_id: str = Form(""),
        link_category: str = Form(""),
        link_note: str = Form(""),
    ):
        vid = add_vendor(
            name,
            trade=trade or None,
            phone=phone or None,
            email=email or None,
            website=website or None,
            address=address or None,
            city=city or None,
            state=state or None,
            zip_code=zip or None,
            specialties=specialties or None,
            notes=notes or None,
            preferred=bool(preferred),
        )
        if link_guide_id.strip() or link_category.strip():
            link_vendor_to_guide(
                vid,
                guide_id=link_guide_id.strip() or None,
                category=link_category.strip() or None,
                note=link_note or None,
            )
        return RedirectResponse("/vendors", status_code=303)

    @app.post("/vendors/link")
    def vendors_link(
        vendor_id: str = Form(...),
        guide_id: str = Form(""),
        category: str = Form(""),
        note: str = Form(""),
    ):
        vid = _int_or_none(vendor_id)
        if vid is not None and (guide_id.strip() or category.strip()):
            link_vendor_to_guide(
                vid,
                guide_id=guide_id.strip() or None,
                category=category.strip() or None,
                note=note or None,
            )
        return RedirectResponse("/vendors", status_code=303)

    @app.post("/admin/reindex")
    def reindex():
        rebuild_index()
        return RedirectResponse("/", status_code=303)

    return app
