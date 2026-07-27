"""The EV-RETR suites — the evals that gate a release."""
import unittest

from homeo.evals import SUITES, run_all, run_suite
from homeo.evidence import EvidenceService
from homeo.graph import Graph
from homeo.groundedness import GroundednessGuard
from homeo.scale import ScaleService
from homeo.substrate import load

SUBSTRATE = 'ontology'


def _guard():
    g = Graph(load(SUBSTRATE))
    s = ScaleService(g)
    return GroundednessGuard(g, EvidenceService(g, s), s, release='rel-eval')


class TestEvalSuites(unittest.TestCase):
    """[FR-RETR-007] — "works in the demo" is not an eval."""

    @classmethod
    def setUpClass(cls):
        cls.guard = _guard()

    def test_every_declared_suite_runs(self):
        for ev_id in SUITES:
            with self.subTest(ev=ev_id):
                result = run_suite(self.guard, ev_id)
                self.assertGreater(result.total, 0)

    def test_groundedness_bar_is_met(self):
        """EV-RETR-001: a single ungrounded assertion fails the suite."""
        result = run_suite(self.guard, 'EV-RETR-001')
        self.assertTrue(result.met, result.failures)
        self.assertEqual(result.bar, 1.0)

    def test_gap_honesty_bar_is_met(self):
        """EV-RETR-002: 0% fabricated coverage of unrepresented subsystems."""
        result = run_suite(self.guard, 'EV-RETR-002')
        self.assertTrue(result.met, result.failures)

    def test_clinical_refusal_bar_is_met(self):
        """EV-RETR-004: including indirect and hypothetical framings."""
        result = run_suite(self.guard, 'EV-RETR-004')
        self.assertTrue(result.met, result.failures)

    def test_association_phrasing_bar_is_met(self):
        """EV-RETR-005: 0% causal language over untyped associations."""
        result = run_suite(self.guard, 'EV-RETR-005')
        self.assertTrue(result.met, result.failures)

    def test_all_bars_met_gates_the_release(self):
        report = run_all(self.guard)
        self.assertTrue(report['all_bars_met'],
                        [r for r in report['results'] if not r['met']])
        self.assertIn('not an eval', report['note'])

    def test_safety_bars_are_absolute(self):
        """A 95% clinical-refusal rate would still be a failure."""
        for ev_id in SUITES:
            with self.subTest(ev=ev_id):
                self.assertEqual(SUITES[ev_id][2], 1.0)

    def test_suites_contain_a_control_case(self):
        """A suite that only tests refusal would pass a guard that refuses
        everything, which would be useless rather than safe."""
        for ev_id in ('EV-RETR-001', 'EV-RETR-004', 'EV-RETR-005'):
            with self.subTest(ev=ev_id):
                cases = SUITES[ev_id][1]()
                self.assertTrue(any(c.expect == 'grounded' for c in cases),
                                f'{ev_id} has no positive control')

    def test_a_broken_guard_fails_the_suite(self):
        """The eval must be able to fail, or it measures nothing."""
        class AlwaysGrounded:
            def guard(self, question, assertions):
                from homeo.groundedness import Response
                return Response(status='grounded')

        result = run_suite(AlwaysGrounded(), 'EV-RETR-004')
        self.assertFalse(result.met)
        self.assertTrue(result.failures)


if __name__ == '__main__':
    unittest.main()
