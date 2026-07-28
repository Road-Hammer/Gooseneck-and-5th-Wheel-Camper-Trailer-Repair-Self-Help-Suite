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
from .content_loader import (
    get_guide,
    list_guides,
    load_catalog,
    published_categories,
    rebuild_index,
    search_guides,
)
from .db import init_db
from .oem_reference import load_oem_publishers
from .paths import package_root
from .power_units import (
    add_power_unit,
    get_power_unit,
    list_power_unit_maintenance,
    list_power_units,
)
from .tow_physics import grade_combination

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
        cats = published_categories()
        return {
            "version": __version__,
            "copyright": __copyright__,
            "catalog": catalog,
            "categories": cats,
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
        if not guides:
            return HTMLResponse(
                "<h1>Category not published</h1>"
                "<p>This suite only lists categories that have finished guides.</p>"
                "<p><a href='/'>Home</a></p>",
                status_code=404,
            )
        cat_meta = next(
            (c for c in published_categories() if c.get("id") == category_id),
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

    # ----- Power units + traffic-light tow grade -----

    @app.get("/power-units", response_class=HTMLResponse)
    def power_units_page(request: Request):
        return TEMPLATES.TemplateResponse(
            request,
            "power_units.html",
            base_ctx(
                power_units=list_power_units(),
                maintenance=list_power_unit_maintenance(limit=50),
                vendors=list_vendors(),
            ),
        )

    @app.post("/power-units/add")
    def power_units_add(
        name: str = Form(...),
        make: str = Form(""),
        model: str = Form(""),
        year: str = Form(""),
        trim: str = Form(""),
        vin: str = Form(""),
        engine: str = Form(""),
        drivetrain: str = Form(""),
        curb_weight: str = Form(""),
        gvwr: str = Form(""),
        gcwr: str = Form(""),
        payload_capacity: str = Form(""),
        max_trailer_weight: str = Form(""),
        max_tongue_weight: str = Form(""),
        hitch_receiver_rating: str = Form(""),
        rating_publisher: str = Form(...),
        rating_source: str = Form(""),
        notes: str = Form(""),
    ):
        add_power_unit(
            name,
            make=make or None,
            model=model or None,
            year=_int_or_none(year),
            trim=trim or None,
            vin=vin or None,
            engine=engine or None,
            drivetrain=drivetrain or None,
            curb_weight=_float_or_none(curb_weight),
            gvwr=_float_or_none(gvwr),
            gcwr=_float_or_none(gcwr),
            payload_capacity=_float_or_none(payload_capacity),
            max_trailer_weight=_float_or_none(max_trailer_weight),
            max_tongue_weight=_float_or_none(max_tongue_weight),
            hitch_receiver_rating=_float_or_none(hitch_receiver_rating),
            rating_publisher=rating_publisher or None,
            rating_source=rating_source or None,
            notes=notes or None,
        )
        return RedirectResponse("/power-units", status_code=303)

    @app.post("/power-units/maintenance")
    def power_units_maintenance(
        power_unit_id: str = Form(...),
        title: str = Form(...),
        performed_at: str = Form(""),
        status: str = Form("completed"),
        miles: str = Form(""),
        category: str = Form("power_unit_maintenance"),
        vendor_id: str = Form(""),
        details: str = Form(""),
        labor_cost: str = Form(""),
        parts_cost: str = Form(""),
    ):
        add_entry(
            title,
            power_unit_id=_int_or_none(power_unit_id),
            vendor_id=_int_or_none(vendor_id),
            performed_at=performed_at or None,
            status=status or "completed",
            miles=_float_or_none(miles),
            category=category or "power_unit_maintenance",
            details=details or None,
            labor_cost=_float_or_none(labor_cost),
            parts_cost=_float_or_none(parts_cost),
        )
        return RedirectResponse("/power-units", status_code=303)

    def _tow_form_defaults(pu: dict | None = None) -> dict:
        d = {
            "truck_as_weighed": "",
            "truck_curb": "",
            "passengers_cargo": "",
            "truck_gvwr": "",
            "truck_gcwr": "",
            "payload": "",
            "max_trailer": "",
            "max_tongue": "",
            "hitch_rating": "",
            "rating_publisher": "",
            "trailer_weight": "",
            "trailer_gvwr": "",
            "tongue": "",
            "hitch_style": "conventional",
        }
        if pu:
            d["truck_curb"] = "" if pu.get("curb_weight") is None else str(pu["curb_weight"])
            d["truck_gvwr"] = "" if pu.get("gvwr") is None else str(pu["gvwr"])
            d["truck_gcwr"] = "" if pu.get("gcwr") is None else str(pu["gcwr"])
            d["payload"] = "" if pu.get("payload_capacity") is None else str(pu["payload_capacity"])
            d["max_trailer"] = (
                "" if pu.get("max_trailer_weight") is None else str(pu["max_trailer_weight"])
            )
            d["max_tongue"] = (
                "" if pu.get("max_tongue_weight") is None else str(pu["max_tongue_weight"])
            )
            d["hitch_rating"] = (
                "" if pu.get("hitch_receiver_rating") is None else str(pu["hitch_receiver_rating"])
            )
            d["rating_publisher"] = pu.get("rating_publisher") or ""
        return d

    @app.get("/tow-check", response_class=HTMLResponse)
    def tow_check_get(request: Request, pu: str = Query("")):
        selected = get_power_unit(int(pu)) if pu.isdigit() else None
        return TEMPLATES.TemplateResponse(
            request,
            "tow_check.html",
            base_ctx(
                result=None,
                form=_tow_form_defaults(selected),
                power_units=list_power_units(),
                selected_pu=selected,
                oem_publishers=load_oem_publishers(),
            ),
        )

    @app.post("/tow-check", response_class=HTMLResponse)
    def tow_check_post(
        request: Request,
        power_unit_id: str = Form(""),
        truck_as_weighed: str = Form(""),
        truck_curb: str = Form(""),
        passengers_cargo: str = Form(""),
        truck_gvwr: str = Form(""),
        truck_gcwr: str = Form(""),
        payload: str = Form(""),
        max_trailer: str = Form(""),
        max_tongue: str = Form(""),
        hitch_rating: str = Form(""),
        rating_publisher: str = Form(""),
        trailer_weight: str = Form(""),
        trailer_gvwr: str = Form(""),
        tongue: str = Form(""),
        hitch_style: str = Form("conventional"),
    ):
        selected = get_power_unit(int(power_unit_id)) if power_unit_id.isdigit() else None
        form = {
            "truck_as_weighed": truck_as_weighed,
            "truck_curb": truck_curb,
            "passengers_cargo": passengers_cargo,
            "truck_gvwr": truck_gvwr,
            "truck_gcwr": truck_gcwr,
            "payload": payload,
            "max_trailer": max_trailer,
            "max_tongue": max_tongue,
            "hitch_rating": hitch_rating,
            "rating_publisher": rating_publisher,
            "trailer_weight": trailer_weight,
            "trailer_gvwr": trailer_gvwr,
            "tongue": tongue,
            "hitch_style": hitch_style,
        }
        result = grade_combination(
            truck_as_weighed=_float_or_none(truck_as_weighed),
            truck_curb_or_empty=_float_or_none(truck_curb),
            passengers_and_cargo_in_truck=_float_or_none(passengers_cargo),
            truck_gvwr=_float_or_none(truck_gvwr),
            truck_gcwr=_float_or_none(truck_gcwr),
            truck_payload_capacity=_float_or_none(payload),
            max_trailer_weight_rating=_float_or_none(max_trailer),
            max_tongue_or_pin_rating=_float_or_none(max_tongue),
            hitch_receiver_rating=_float_or_none(hitch_rating),
            trailer_as_weighed=_float_or_none(trailer_weight),
            trailer_gvwr=_float_or_none(trailer_gvwr),
            tongue_or_pin_weight=_float_or_none(tongue),
            hitch_style=hitch_style,
        )
        # Attach user-entered publisher credit into display
        if rating_publisher.strip():
            result.credits.insert(
                0,
                f"Ratings for this grade entered as credited to: {rating_publisher.strip()}",
            )
        return TEMPLATES.TemplateResponse(
            request,
            "tow_check.html",
            base_ctx(
                result=result.to_dict(),
                form=form,
                power_units=list_power_units(),
                selected_pu=selected,
                oem_publishers=load_oem_publishers(),
            ),
        )

    @app.post("/admin/reindex")
    def reindex():
        rebuild_index()
        return RedirectResponse("/", status_code=303)

    return app
