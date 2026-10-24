import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mission_loop as ml

DEMO = json.loads((Path(__file__).resolve().parents[1] / 'examples/synthetic_public_mission.json').read_text())


class MissionLoopTests(unittest.TestCase):
    def test_expected_demo_outcomes(self):
        outcome = ml.run(copy.deepcopy(DEMO))
        self.assertEqual([a['status'] for a in outcome['actions']],
                         ['SIMULATED_ONLY', 'SIMULATED_ONLY', 'HUMAN_REVIEW_REQUIRED', 'BLOCKED'])
        self.assertEqual(outcome['execution_state'], 'SIMULATION')
        self.assertEqual(outcome['remaining_planning_units'], 4)
        self.assertTrue(ml.verify_audit(outcome['audit']))

    def test_unknown_action_denied(self):
        m = copy.deepcopy(DEMO)
        m['actions'][0]['kind'] = 'RUN_ARBITRARY_SHELL'
        self.assertEqual(ml.run(m)['actions'][0]['status'], 'BLOCKED')

    def test_role_confusion_denied(self):
        m = copy.deepcopy(DEMO)
        m['actions'][0]['role'] = 'gtm'
        self.assertEqual(ml.run(m)['actions'][0]['reason'], 'role outside the declared action envelope')

    def test_budget_exceeded_denied(self):
        m = copy.deepcopy(DEMO)
        m['budget_units'] = 0
        self.assertEqual(ml.run(m)['actions'][0]['reason'], 'mission budget exceeded')

    def test_evidence_missing_denied(self):
        m = copy.deepcopy(DEMO)
        m['actions'][1]['source_ids'] = []
        self.assertEqual(ml.run(m)['actions'][1]['reason'], 'research brief requires declared evidence references')

    def test_evidence_unknown_denied(self):
        m = copy.deepcopy(DEMO)
        m['actions'][1]['source_ids'] = ['OTHER']
        self.assertEqual(ml.run(m)['actions'][1]['status'], 'BLOCKED')

    def test_duplicate_source_reference_denied(self):
        m = copy.deepcopy(DEMO)
        m['actions'][1]['source_ids'] = ['SRC-1', 'SRC-1']
        self.assertEqual(ml.run(m)['actions'][1]['status'], 'BLOCKED')

    def test_consequential_always_review(self):
        m = copy.deepcopy(DEMO)
        m['actions'] = [{"id": "CHANGE", "role": "engineering", "kind": "MODIFY_PERMISSIONS", "target": "service", "budget_units": 1, "source_ids": []}]
        self.assertEqual(ml.run(m)['actions'][0]['status'], 'HUMAN_REVIEW_REQUIRED')

    def test_internal_change_review(self):
        m = copy.deepcopy(DEMO)
        m['actions'] = [{"id": "CHANGE", "role": "engineering", "kind": "PREPARE_INTERNAL_CHANGE", "target": "local branch", "budget_units": 1, "source_ids": []}]
        self.assertEqual(ml.run(m)['actions'][0]['status'], 'HUMAN_REVIEW_REQUIRED')

    def test_prohibited_actions_always_blocked(self):
        for kind in ('TRANSFER_FUNDS', 'SIGN_CONTRACT', 'DELETE_RECORDS', 'SELF_MODIFY_AUTHORITY'):
            m = copy.deepcopy(DEMO)
            m['actions'][0]['kind'] = kind
            with self.subTest(kind=kind):
                self.assertEqual(ml.run(m)['actions'][0]['status'], 'BLOCKED')

    def test_unknown_domain_rejected(self):
        m = copy.deepcopy(DEMO)
        m['domain'] = 'universal_superintelligence'
        with self.assertRaises(ValueError):
            ml.run(m)

    def test_bool_budget_rejected(self):
        m = copy.deepcopy(DEMO)
        m['budget_units'] = True
        with self.assertRaises(ValueError):
            ml.run(m)

    def test_unknown_top_level_rejected(self):
        m = copy.deepcopy(DEMO)
        m['autonomous_execution'] = True
        with self.assertRaises(ValueError):
            ml.run(m)

    def test_audit_tamper_detected(self):
        a = ml.run(copy.deepcopy(DEMO))['audit']
        a[2]['event']['check']['status'] = 'BLOCKED'
        self.assertFalse(ml.verify_audit(a))

    def test_audit_reordering_detected(self):
        a = ml.run(copy.deepcopy(DEMO))['audit']
        a[1], a[2] = a[2], a[1]
        self.assertFalse(ml.verify_audit(a))

    def test_deterministic_run(self):
        self.assertEqual(ml.run(copy.deepcopy(DEMO)), ml.run(copy.deepcopy(DEMO)))

    def test_golden_evaluator(self):
        c = [{'name': 'base', 'mission': copy.deepcopy(DEMO),
              'expected_statuses': {'READ-1': 'SIMULATED_ONLY', 'BRIEF-1': 'SIMULATED_ONLY',
                                    'POST-1': 'HUMAN_REVIEW_REQUIRED', 'PAY-1': 'BLOCKED'}}]
        self.assertEqual(ml.evaluate_golden(c)['passed'], 1)
        c[0]['expected_statuses']['PAY-1'] = 'SIMULATED_ONLY'
        self.assertEqual(ml.evaluate_golden(c)['passed'], 0)

    def test_skill_promotion_only_recommendation(self):
        c = dict(golden_total=10, golden_passed=10, critical_violations=0,
                 baseline_cost_per_accepted=2.0, candidate_cost_per_accepted=1.5,
                 baseline_quality=.9, candidate_quality=.95)
        out = ml.assess_skill_promotion(c)
        self.assertEqual(out['disposition'], 'HUMAN_REVIEW_REQUIRED')
        c['critical_violations'] = 1
        self.assertEqual(ml.assess_skill_promotion(c)['disposition'], 'REJECT_CANDIDATE')

    def test_quality_regression_rejected(self):
        c = dict(golden_total=11, golden_passed=11, critical_violations=0,
                 baseline_cost_per_accepted=3, candidate_cost_per_accepted=2,
                 baseline_quality=.9, candidate_quality=.8)
        self.assertEqual(ml.assess_skill_promotion(c)['disposition'], 'REJECT_CANDIDATE')


if __name__ == '__main__':
    unittest.main()
