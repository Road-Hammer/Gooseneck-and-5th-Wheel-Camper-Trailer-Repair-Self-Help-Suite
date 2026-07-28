from __future__ import annotations

import argparse
import os
import sys
import webbrowser

from . import __copyright__, __version__
from .cmms import add_vendor, list_vendors, shop_summary
from .content_loader import list_guides, rebuild_index, search_guides
from .db import init_db
from .paths import db_path, project_root
from .service_log import add_entry, add_rig, list_entries, list_rigs


def cmd_index(_args: argparse.Namespace) -> int:
    init_db()
    try:
        n = rebuild_index()
    except Exception as e:
        print(f"INDEX FAILED (publishing standards):\n{e}", file=sys.stderr)
        return 1
    print(f"Indexed {n} guide(s) into {db_path()}")
    print("All guides passed credit/source and completeness checks.")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    init_db()
    if not list_guides():
        rebuild_index()
    import uvicorn

    host = args.host
    port = args.port
    url = f"http://{host}:{port}"
    print(f"STWL Camper Suite v{__version__}")
    print(__copyright__)
    print(f"Offline UI: {url}")
    print(f"Project:    {project_root()}")
    print(f"Database:   {db_path()}")
    if args.open:
        webbrowser.open(url)
    uvicorn.run(
        "stwl_camper_suite.app:create_app",
        factory=True,
        host=host,
        port=port,
        log_level="info",
        reload=False,
    )
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    init_db()
    if not list_guides():
        rebuild_index()
    results = search_guides(args.query)
    if not results:
        print("No matches.")
        return 0
    for r in results:
        print(f"- [{r['category']}] {r['title']}  (id={r['id']})")
        snip = (r.get("snippet") or "").replace("\n", " ")
        if snip:
            print(f"    {snip[:160]}")
    return 0


def cmd_log(args: argparse.Namespace) -> int:
    init_db()
    if args.log_cmd == "list":
        for e in list_entries(limit=args.limit):
            rig = e.get("rig_name") or "—"
            st = e.get("status") or ""
            print(f"{e['performed_at']}  [{st}] [{rig}]  {e['title']}")
        return 0
    if args.log_cmd == "add":
        rid = args.rig_id
        add_entry(
            args.title,
            rig_id=rid,
            category=args.category,
            details=args.details,
            miles=args.miles,
            status=getattr(args, "status", None) or "completed",
            vendor_id=getattr(args, "vendor_id", None),
        )
        print("Logged.")
        return 0
    if args.log_cmd == "add-rig":
        i = add_rig(args.name, rig_type=args.type, vin=args.vin)
        print(f"Rig id={i}")
        return 0
    if args.log_cmd == "rigs":
        for r in list_rigs():
            print(f"{r['id']}: {r['name']} ({r.get('rig_type') or '—'})")
        return 0
    if args.log_cmd == "summary":
        s = shop_summary()
        print(s)
        return 0
    print("Unknown log command", file=sys.stderr)
    return 2


def cmd_vendor(args: argparse.Namespace) -> int:
    init_db()
    if args.vendor_cmd == "list":
        for v in list_vendors(active_only=False):
            star = "*" if v.get("preferred") else " "
            print(f"{v['id']}{star} {v['name']}  ({v.get('trade') or '—'})  {v.get('phone') or ''}")
        return 0
    if args.vendor_cmd == "add":
        i = add_vendor(
            args.name,
            trade=args.trade,
            phone=args.phone,
            preferred=bool(args.preferred),
        )
        print(f"Vendor id={i}")
        return 0
    print("Unknown vendor command", file=sys.stderr)
    return 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stwl-camper",
        description="STWL offline camper/trailer self-help suite",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("index", help="Rebuild offline full-text index from content/")
    s.set_defaults(func=cmd_index)

    s = sub.add_parser("serve", help="Run offline local web UI")
    s.add_argument(
        "--host",
        default=os.environ.get("STWL_HOST", "127.0.0.1"),
        help="Bind address (default 127.0.0.1; use 0.0.0.0 for Docker/HF)",
    )
    s.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT") or os.environ.get("STWL_PORT") or "8765"),
    )
    s.add_argument("--open", action="store_true", help="Open browser")
    s.set_defaults(func=cmd_serve)

    s = sub.add_parser("search", help="Search guides offline (CLI)")
    s.add_argument("query")
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("log", help="Owner service log")
    log_sub = s.add_subparsers(dest="log_cmd", required=True)
    ls = log_sub.add_parser("list", help="List recent log entries")
    ls.add_argument("--limit", type=int, default=50)
    ls.set_defaults(func=cmd_log)
    la = log_sub.add_parser("add", help="Add a service log entry")
    la.add_argument("title")
    la.add_argument("--rig-id", type=int, default=None)
    la.add_argument("--vendor-id", type=int, default=None)
    la.add_argument("--category", default=None)
    la.add_argument("--details", default=None)
    la.add_argument("--miles", type=float, default=None)
    la.add_argument("--status", default="completed")
    la.set_defaults(func=cmd_log)
    lr = log_sub.add_parser("add-rig", help="Register a rig profile")
    lr.add_argument("name")
    lr.add_argument("--type", default=None)
    lr.add_argument("--vin", default=None)
    lr.set_defaults(func=cmd_log)
    log_sub.add_parser("rigs", help="List rigs").set_defaults(func=cmd_log)
    log_sub.add_parser("summary", help="Shop CMMS summary").set_defaults(func=cmd_log)

    v = sub.add_parser("vendor", help="Vendor directory")
    vsub = v.add_subparsers(dest="vendor_cmd", required=True)
    vsub.add_parser("list", help="List vendors").set_defaults(func=cmd_vendor)
    va = vsub.add_parser("add", help="Add vendor")
    va.add_argument("name")
    va.add_argument("--trade", default=None)
    va.add_argument("--phone", default=None)
    va.add_argument("--preferred", action="store_true")
    va.set_defaults(func=cmd_vendor)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
