"""The groundedness guard — INV-14 at runtime.

This is the component the whole retrieval architecture rests on, so it is tested
adversarially: the tests try to get unsupported content past it.
"""
import unittest

from homeo.evidence import EvidenceService
from homeo.graph import Graph
from homeo.groundedness import Assertion, GroundednessGuard
from homeo.scale import ScaleService
from homeo.substrate import load

SUBSTRATE = 'ontology'
REAL_CLAIM = 'CLM:heart-function-pump'
WEAK_CLAIM = 'CLM:cross-bridge-cycle-duration'      # EVC-4, approximated
ASSOC_CLAIM = 'CLM:heart-two-pumps-series'          # backs an association


def _guard(release='rel-test'):
    g = Graph(load(SUBSTRATE))
    s = ScaleService(g)
    return GroundednessGuard(g, EvidenceService(g, s), s, release=release)


class TestGroundedness(unittest.TestCase):
    """[FR-RETR-001] [FR-RETR-002]"""

    @classmethod
    def setUpClass(cls):
        cls.guard = _guard()

    def test_grounded_assertion_passes(self):
        """[FR-RETR-001] A properly cited assertion is rendered."""
        r = self.guard.guard('What does the heart do?', [
            Assertion('The heart propels blood.', [REAL_CLAIM])])
        self.assertTrue(r.ok)
        self.assertEqual(r.assertions[0].evidence_classes, ['EVC-2'])

    def test_assertion_without_a_claim_id_is_refused(self):
        """[FR-RETR-001] Fluency is not evidence."""
        r = self.guard.guard('q', [Assertion('It has four chambers.', [])])
        self.assertEqual(r.status, 'refused')
        self.assertIn('no claim id', r.reason)

    def test_assertion_citing_a_nonexistent_claim_is_refused(self):
        """[FR-RETR-001] A plausible citation is still checked."""
        r = self.guard.guard('q', [
            Assertion('Plausible sentence.', ['CLM:invented'])])
        self.assertEqual(r.status, 'refused')
        self.assertIn('does not exist', r.reason)

    def test_one_bad_assertion_refuses_the_whole_response(self):
        """[FR-RETR-001] Refuse rather than filter: partial output would ship
        the unsupported claim alongside supported ones."""
        r = self.guard.guard('q', [
            Assertion('The heart propels blood.', [REAL_CLAIM]),
            Assertion('And it regenerates fully after injury.', [])])
        self.assertEqual(r.status, 'refused')
        self.assertEqual(r.assertions, [])

    def test_per_assertion_classes_are_not_averaged(self):
        """[FR-RETR-002] CH-06: a composed sentence carries every class."""
        r = self.guard.guard('q', [
            Assertion('Composed statement.', [REAL_CLAIM, WEAK_CLAIM])])
        self.assertTrue(r.ok)
        a = r.assertions[0]
        self.assertEqual(len(a.evidence_classes), 2)
        self.assertIn('EVC-2', a.evidence_classes)
        self.assertIn('EVC-4', a.evidence_classes)
        # The weakest is reported alongside the full list, never instead of it.
        self.assertEqual(a.weakest_class, 'EVC-4')
        self.assertEqual(len(a.as_dict()['evidence_classes']), 2)

    def test_presentation_constraints_travel_with_the_assertion(self):
        """[FR-RETR-004] An approximation must be presented as one."""
        r = self.guard.guard('q', [Assertion('Rate statement.', [WEAK_CLAIM])])
        self.assertTrue(any('approximation' in c
                            for c in r.assertions[0].constraints))

    def test_response_is_release_pinned(self):
        """[FR-RETR-006] A caller must never guess what answered them."""
        r = self.guard.guard('q', [Assertion('x', [REAL_CLAIM])])
        self.assertEqual(r.release, 'rel-test')


class TestAssociationPhrasing(unittest.TestCase):
    """[FR-RETR-009] — BRB-30: an association is not a mechanism."""

    @classmethod
    def setUpClass(cls):
        cls.guard = _guard()

    def test_causal_language_over_an_association_is_refused(self):
        r = self.guard.guard('q', [
            Assertion('Autonomic input causes contraction.', [ASSOC_CLAIM])])
        self.assertEqual(r.status, 'refused')
        self.assertIn('untyped association', r.reason)

    def test_several_causal_verbs_are_caught(self):
        for phrasing in ('This regulates that.', 'X leads to Y.',
                         'The mechanism is well understood.',
                         'A activates B.', 'This results in contraction.'):
            with self.subTest(phrasing=phrasing):
                r = self.guard.guard('q', [Assertion(phrasing, [ASSOC_CLAIM])])
                self.assertEqual(r.status, 'refused', phrasing)

    def test_descriptive_language_over_an_association_passes(self):
        """The association may be described — just not as a mechanism."""
        r = self.guard.guard('q', [
            Assertion('These two are recorded as related.', [ASSOC_CLAIM])])
        self.assertTrue(r.ok)

    def test_the_only_admissible_description_states_the_uncertainty(self):
        text = self.guard.describe_association('REL:assoc-autonomic-cardiaccycle')
        self.assertIn('unstated type', text)
        self.assertIn('without establishing how', text)

    def test_describing_a_typed_relation_as_an_association_is_rejected(self):
        with self.assertRaises(ValueError):
            self.guard.describe_association('REL:crossbridge-consumes-atp')


class TestClinicalRefusal(unittest.TestCase):
    """[FR-RETR-005] — BR-019 has no exceptions."""

    @classmethod
    def setUpClass(cls):
        cls.guard = _guard()

    def test_direct_clinical_question_is_declined(self):
        r = self.guard.guard('Do I have a heart attack?', [
            Assertion('The heart propels blood.', [REAL_CLAIM])])
        self.assertEqual(r.status, 'declined')

    def test_indirect_framing_does_not_change_the_answer(self):
        """UC-12: the framing must not be a way around the boundary."""
        for question in ('My father has chest pain, is it serious?',
                         'How do I treat this?',
                         'Should I be worried about my heart?',
                         'What is wrong with me?'):
            with self.subTest(question=question):
                r = self.guard.guard(question, [
                    Assertion('The heart propels blood.', [REAL_CLAIM])])
                self.assertEqual(r.status, 'declined', question)

    def test_clinical_check_precedes_groundedness(self):
        """A clinical question is declined even with perfect grounding."""
        r = self.guard.guard('Should I take medication for this?', [
            Assertion('The heart propels blood.', [REAL_CLAIM])])
        self.assertEqual(r.status, 'declined')
        self.assertEqual(r.assertions, [])

    def test_decline_is_useful_not_merely_a_refusal(self):
        r = self.guard.guard('Do I have a problem?', [])
        self.assertIn('available through search', r.statement)
        self.assertIn('not a medical device', r.boundary)

    def test_structural_question_is_not_declined(self):
        r = self.guard.guard('What is the heart made of?', [
            Assertion('The heart propels blood.', [REAL_CLAIM])])
        self.assertTrue(r.ok)


class TestGapAnswers(unittest.TestCase):
    """[FR-RETR-003] — stating a gap is different from refusing to answer."""

    @classmethod
    def setUpClass(cls):
        cls.guard = _guard()

    def test_no_claims_yields_a_gap_not_a_refusal(self):
        r = self.guard.guard('Tell me about the pineal gland at cell level', [])
        self.assertEqual(r.status, 'gap')
        self.assertIn('No recorded claims', r.statement)

    def test_gap_statement_is_about_the_model(self):
        r = self.guard.guard('anything', [])
        self.assertIn('statement about the model', r.statement)
        self.assertIn('not the biology', r.statement)

    def test_gap_cites_the_scale_contract(self):
        r = self.guard.guard('anything', [])
        self.assertIn('scale contract', r.statement)


if __name__ == '__main__':
    unittest.main()
