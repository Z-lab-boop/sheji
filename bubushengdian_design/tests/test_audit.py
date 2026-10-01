from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AuditTests(unittest.TestCase):
    def test_audit_statuses_are_honest(self):
        report = json.loads((ROOT / "07_audit" / "audit_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["technical_status"], "pass")
        self.assertEqual(report["submission_status"], "candidate_pending_human_route_review")
        self.assertTrue(all(check["passed"] for check in report["checks"]))

    def test_manifest_has_required_types(self):
        content = (ROOT / "06_submission" / "source_manifest.csv").read_text(encoding="utf-8")
        for token in ("cad", "render", "board_source", "board_jpg", "board_pdf", "external_reference"):
            self.assertIn(token, content)


if __name__ == "__main__":
    unittest.main()
