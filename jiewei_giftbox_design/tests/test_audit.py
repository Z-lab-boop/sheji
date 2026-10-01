from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AuditTests(unittest.TestCase):
    def test_statuses_preserve_submission_gate(self):
        report = json.loads((ROOT / "07_audit" / "audit_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["technical_status"], "pass")
        self.assertEqual(report["submission_status"], "blocked_pending_real_sku_and_brand_assets")
        self.assertEqual(report["missing_inputs"], ["actual_sku_dimensions", "brand_assets_and_permission", "legal_food_copy", "entrant_identity"])

    def test_proxy_disclosure_survives_public_boards(self):
        for index in range(1, 7):
            svg = (ROOT / "05_boards" / "src" / f"board_{index:02d}.svg").read_text(encoding="utf-8")
            if index in (3, 4, 5, 6):
                self.assertIn("规格代理件", svg)


if __name__ == "__main__":
    unittest.main()
