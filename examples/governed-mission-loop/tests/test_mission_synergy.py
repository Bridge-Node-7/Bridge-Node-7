"""Offline handoff tests. No external repo or runtime is loaded."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mission_synergy as sy

ROOT = Path(__file__).resolve().parents[1]
CYBER = json.loads((ROOT / "examples/synthetic_cyber_synergy.json").read_text(encoding="utf-8"))
MATERIALS = json.loads((ROOT / "examples/synthetic_materials_synergy.json").read_text(encoding="utf-8"))


class SynergyTests(unittest.TestCase):
    def test_cyber_route(self):
        p = sy.plan(copy.deepcopy(CYBER))
        self.assertEqual([s["capability"] for s in p["stages"]],
                         ["source-review", "cyber-review", "decision-brief"])
        self.assertEqual([a["status"] for a in p["action_preflight"]],
                         ["SIMULATED_ONLY", "SIMULATED_ONLY", "HUMAN_REVIEW_REQUIRED"])
        self.assertEqual(p["readiness"], "HUMAN_PREPARATION_ONLY")
        self.assertEqual(p["declared_uncertain_source_ids"], ["SRC-1", "SRC-2"])
        self.assertFalse(p["release_authorized"])
        self.assertFalse(p["external_execution_authorized"])

    def test_materials_route(self):
        p = sy.plan(copy.deepcopy(MATERIALS))
        self.assertEqual([s["capability"] for s in p["stages"]],
                         ["source-review", "materials-review", "mission-assurance", "decision-brief"])
        self.assertEqual(p["stages"][1]["owner"], "materials-to-mission")
        self.assertEqual(p["stages"][2]["owner"], "frontier-mission-assurance")
        self.assertEqual(p["human_review_proposals"], ["CHANGE-1"])

    def test_deterministic_result_and_digest(self):
        self.assertEqual(sy.plan(copy.deepcopy(CYBER)), sy.plan(copy.deepcopy(CYBER)))
        changed = copy.deepcopy(CYBER)
        changed["beneficiary"] += " and neighbors"
        self.assertNotEqual(sy.plan(changed)["request_sha256"], sy.plan(CYBER)["request_sha256"])

    def test_unknown_capability_rejected(self):
        m = copy.deepcopy(CYBER)
        m["capabilities"] = ["arbitrary-remote-action"]
        with self.assertRaisesRegex(ValueError, "unknown capability"):
            sy.plan(m)

    def test_duplicate_capabilities_rejected(self):
        m = copy.deepcopy(CYBER)
        m["capabilities"] = ["decision-brief", "decision-brief"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            sy.plan(m)

    def test_empty_capabilities_rejected(self):
        m = copy.deepcopy(CYBER)
        m["capabilities"] = []
        with self.assertRaisesRegex(ValueError, "nonempty bounded"):
            sy.plan(m)

    def test_private_handling_fails_closed(self):
        for handling in ("PRIVATE", "PROTECTED", "INTERNAL", "", None):
            m = copy.deepcopy(CYBER)
            m["handling"] = handling
            with self.subTest(handling=handling), self.assertRaisesRegex(ValueError, "SAFE STOP"):
                sy.plan(m)

    def test_unknown_field_rejected(self):
        m = copy.deepcopy(CYBER)
        m["auto_publish"] = True
        with self.assertRaisesRegex(ValueError, "unknown or missing"):
            sy.plan(m)

    def test_prohibited_action_fails_closed(self):
        m = copy.deepcopy(CYBER)
        m["mission"]["actions"][0]["kind"] = "TRANSFER_FUNDS"
        p = sy.plan(m)
        self.assertEqual(p["readiness"], "SAFE_STOP")
        self.assertEqual(p["blocked_proposals"], ["READ-1"])
        self.assertFalse(p["external_execution_authorized"])

    def test_unknown_action_fails_closed(self):
        m = copy.deepcopy(CYBER)
        m["mission"]["actions"][0]["kind"] = "EXECUTE_SHELL"
        self.assertEqual(sy.plan(m)["readiness"], "SAFE_STOP")

    def test_source_state_not_upgraded(self):
        m = copy.deepcopy(CYBER)
        m["mission"]["sources"][0]["state"] = "VERIFIED"
        p = sy.plan(m)
        self.assertEqual(p["declared_uncertain_source_ids"], ["SRC-2"])
        self.assertIn("Source states are declarations", p["limitations"][2])

    def test_input_is_not_mutated(self):
        m = copy.deepcopy(CYBER)
        sy.plan(m)
        self.assertEqual(m, CYBER)

    def test_markdown_public_only(self):
        doc = sy.as_markdown(sy.plan(CYBER))
        self.assertIn("https://github.com/Bridge-Node-7/ai-cyber-assurance", doc)
        self.assertIn("HUMAN_REVIEW_REQUIRED", doc)
        self.assertNotIn("github.com/Bridge-Node-7/intelligence-library", doc)

    def test_no_claimed_execution(self):
        p = sy.plan(CYBER)
        self.assertEqual(p["execution_state"], "SIMULATION")
        self.assertTrue(all(s["status"] == "HUMAN_PREPARATION_ONLY" for s in p["stages"]))

    def test_existing_mission_validation_reused(self):
        m = copy.deepcopy(CYBER)
        m["mission"]["actions"] = []
        with self.assertRaises(ValueError):
            sy.plan(m)


if __name__ == "__main__":
    unittest.main()
