from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AuditTests(unittest.TestCase):
    def test_status_is_conditionally_ready_only(self):
        report = json.loads((ROOT / "07_audit" / "audit_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["technical_status"], "pass")
        self.assertEqual(report["submission_status"], "conditionally_ready_pending_identity_signature")
        self.assertEqual(report["missing_inputs"], ["entrant_identity", "signed_registration_pdf"])
        self.assertNotIn("brand_assets_and_permission", report["missing_inputs"])

    def test_concept_disclosure_survives_public_boards(self):
        for index in (4, 5, 6):
            svg = (ROOT / "05_boards" / "src" / f"board_{index:02d}.svg").read_text(encoding="utf-8")
            self.assertIn("概念包装建议规格，投产前复核", svg)


if __name__ == "__main__":
    unittest.main()
