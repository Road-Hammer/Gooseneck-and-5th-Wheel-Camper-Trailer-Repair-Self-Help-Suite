from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from stwl_camper_suite.cmms import (
    add_entry,
    add_rig,
    add_vendor,
    link_vendor_to_guide,
    list_entries,
    shop_summary,
    vendors_for_guide_or_category,
)
from stwl_camper_suite.content_loader import get_guide, rebuild_index, search_guides


class SuiteSmokeTests(unittest.TestCase):
    def test_index_requires_credits_and_search_works(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            db = Path(tmp) / "test.db"
            n = rebuild_index(db)
            self.assertGreaterEqual(n, 7)
            hits = search_guides("breakaway", database=db)
            self.assertTrue(any("breakaway" in h["id"] for h in hits))
            g = get_guide("breakaway-switch-test", database=db)
            assert g is not None
            self.assertTrue(g.get("credits_list") or g.get("sources_list"))
            self.assertIn("STWL", " ".join(g.get("credits_list") or []))
            # FMCSA credit on cargo / safety-framework guides where used
            cargo = get_guide("cargo-securement-plain-english", database=db)
            assert cargo is not None
            blob = " ".join(cargo.get("sources_list") or []) + " ".join(cargo.get("credits_list") or [])
            self.assertIn("FMCSA", blob)

            rid = add_rig("Test Stock", rig_type="stock_trailer", database=db)
            vid = add_vendor("Test Shop", trade="brakes_axles", phone="555-0100", database=db)
            link_vendor_to_guide(vid, guide_id="breakaway-switch-test", category="brakes", database=db)
            add_entry(
                "Breakaway test",
                rig_id=rid,
                vendor_id=vid,
                guide_id="breakaway-switch-test",
                status="open",
                priority="high",
                database=db,
            )
            entries = list_entries(open_only=True, database=db)
            self.assertEqual(len(entries), 1)
            vendors = vendors_for_guide_or_category("breakaway-switch-test", "brakes", database=db)
            self.assertEqual(vendors[0]["name"], "Test Shop")
            summary = shop_summary(database=db)
            self.assertEqual(summary["open_work_orders"], 1)


if __name__ == "__main__":
    unittest.main()
