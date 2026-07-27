"""The compilation ladder — where prose becomes a model."""
import unittest

from homeo.evidence import EvidenceService
from homeo.graph import Graph
from homeo.promotion import PromotionRequest, PromotionService
from homeo.scale import ScaleService
from homeo.substrate import Entity, load

SUBSTRATE = 'ontology'
REVIEWER = 'human:reviewer-cardio-01'
WORK = 'typed 6 relations, assigned levels, reviewed sources'


def _service(substrate=None):
    g = Graph(substrate or load(SUBSTRATE))
    return g, PromotionService(g, EvidenceService(g, ScaleService(g)))


class TestPromotionRequiresWork(unittest.TestCase):
    """[FR-ONTO-007] — reformatting promotes nothing."""

    def setUp(self):
        self.graph, self.svc = _service()

    def test_promotion_without_recorded_work_is_refused(self):
        d = self.svc.evaluate(PromotionRequest(
            'HOX:function:cardiaccycle', 'structured', REVIEWER, ''))
        self.assertFalse(d.allowed)
        self.assertTrue(any('record of the curation work' in r
                            for r in d.reasons))

    def test_promotion_by_a_non_human_is_refused(self):
        """No agent advances the ladder (BR-002's discipline, applied here)."""
        d = self.svc.evaluate(PromotionRequest(
            'HOX:function:cardiaccycle', 'structured', 'agent:ontology', WORK))
        self.assertFalse(d.allowed)
        self.assertTrue(any('human reviewer' in r for r in d.reasons))

    def test_promotion_is_forward_only(self):
        d = self.svc.evaluate(PromotionRequest(
            'CL:0000746', 'structured', REVIEWER, WORK))
        self.assertFalse(d.allowed)
        self.assertTrue(any('forward-only' in r for r in d.reasons))

    def test_promotion_advances_one_step_at_a_time(self):
        """Skipping a rung would skip the work the rung records."""
        d = self.svc.evaluate(PromotionRequest(
            'HOX:function:cardiaccycle', 'mechanistic', REVIEWER, WORK))
        self.assertFalse(d.allowed)
        self.assertTrue(any('one step at a time' in r for r in d.reasons))

    def test_unknown_status_is_rejected(self):
        d = self.svc.evaluate(PromotionRequest(
            'CL:0000746', 'excellent', REVIEWER, WORK))
        self.assertFalse(d.allowed)

    def test_unknown_entity_is_rejected(self):
        d = self.svc.evaluate(PromotionRequest(
            'HOX:function:nonexistent', 'structured', REVIEWER, WORK))
        self.assertFalse(d.allowed)


class TestUpstreamSplitBlocks(unittest.TestCase):
    """[FR-ONTO-005] — an ambiguous term is not promoted on a guess."""

    def test_blocked_entity_cannot_be_promoted(self):
        sub = load(SUBSTRATE)
        idx = next(i for i, e in enumerate(sub.entities)
                   if e.id == 'HOX:function:cardiaccycle')
        sub.entities[idx] = Entity(**{**sub.entities[idx].__dict__,
                                      'promotion_blocked': True})
        _, svc = _service(sub)
        d = svc.evaluate(PromotionRequest(
            'HOX:function:cardiaccycle', 'structured', REVIEWER, WORK))
        self.assertFalse(d.allowed)
        self.assertTrue(any('upstream ontology change' in r for r in d.reasons))


class TestPopulationDiscrimination(unittest.TestCase):
    """[FR-ONTO-012] — CH-05: the field must actually discriminate."""

    def setUp(self):
        self.graph, self.svc = _service()

    def test_blanket_population_blocks_promotion(self):
        """The seed's 'adult, unspecified in source' cannot support structure."""
        d = self.svc.evaluate(PromotionRequest(
            'HOX:function:cardiaccycle', 'structured', REVIEWER, WORK))
        self.assertFalse(d.allowed)
        self.assertTrue(any('non-discriminating population' in r
                            for r in d.reasons))

    def test_discriminating_population_permits_promotion(self):
        from homeo.substrate import Claim
        sub = load(SUBSTRATE)
        sub.claims.append(Claim(
            id='CLM:test-specific', subject='HOX:function:cardiaccycle',
            predicate='has_definition', object='A specific claim.',
            evidence_class='EVC-2', source_type='primary research',
            species='Homo sapiens', population='healthy adults aged 20-40',
            date_asserted='2026-07-26', limitations='none identified',
            assigned_by=REVIEWER,
            sources=({'citation': 'X', 'identifier': 'DOI:x'},)))
        _, svc = _service(sub)
        d = svc.evaluate(PromotionRequest(
            'HOX:function:cardiaccycle', 'structured', REVIEWER, WORK))
        self.assertTrue(d.allowed, d.reasons)

    def test_entity_with_no_claims_cannot_be_structured(self):
        sub = load(SUBSTRATE)
        sub.entities.append(Entity(
            id='HOX:function:bare', entity_class='Function',
            subsystem='cardiovascular', preferred_term='Bare',
            compilation_status='narrative', level=2))
        _, svc = _service(sub)
        d = svc.evaluate(PromotionRequest(
            'HOX:function:bare', 'structured', REVIEWER, WORK))
        self.assertFalse(d.allowed)
        self.assertTrue(any('nothing to structure' in r for r in d.reasons))


class TestApply(unittest.TestCase):
    """[FR-ONTO-006] — a caller cannot advance a status without seeing why."""

    def test_apply_advances_only_when_allowed(self):
        from homeo.substrate import Claim
        sub = load(SUBSTRATE)
        sub.claims.append(Claim(
            id='CLM:test-specific', subject='HOX:function:cardiaccycle',
            predicate='has_definition', object='A specific claim.',
            evidence_class='EVC-2', source_type='primary research',
            species='Homo sapiens', population='healthy adults aged 20-40',
            date_asserted='2026-07-26', limitations='none identified',
            assigned_by=REVIEWER,
            sources=({'citation': 'X', 'identifier': 'DOI:x'},)))
        graph, svc = _service(sub)
        d = svc.apply(PromotionRequest(
            'HOX:function:cardiaccycle', 'structured', REVIEWER, WORK))
        self.assertTrue(d.allowed)
        self.assertEqual(graph.get('HOX:function:cardiaccycle').compilation_status,
                         'structured')

    def test_apply_leaves_status_untouched_when_refused(self):
        graph, svc = _service()
        before = graph.get('HOX:function:cardiaccycle').compilation_status
        svc.apply(PromotionRequest(
            'HOX:function:cardiaccycle', 'structured', 'agent:x', ''))
        self.assertEqual(graph.get('HOX:function:cardiaccycle').compilation_status,
                         before)


class TestLadderReport(unittest.TestCase):
    """RSK-10 — entity count must never be mistaken for modelled coverage."""

    def test_report_publishes_the_narrative_proportion(self):
        _, svc = _service()
        report = svc.ladder_report()
        self.assertEqual(sum(report['counts'].values()), report['total'])
        self.assertGreater(report['narrative_proportion'], 0.5,
                           'most of this release is still prose, honestly')
        self.assertIn('not modelled', report['note'])


if __name__ == '__main__':
    unittest.main()
