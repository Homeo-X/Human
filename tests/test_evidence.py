"""Claims, provenance, conflicts, and the negative space."""
import unittest

from homeo.evidence import EvidenceService
from homeo.graph import Graph
from homeo.scale import ScaleService
from homeo.substrate import UNKNOWN, load

SUBSTRATE = 'ontology'


def _services():
    g = Graph(load(SUBSTRATE))
    s = ScaleService(g)
    return g, s, EvidenceService(g, s)


class TestClaimRecord(unittest.TestCase):
    """[FR-EVID-001] [FR-EVID-002] [FR-EVID-007] [FR-EVID-008]"""

    @classmethod
    def setUpClass(cls):
        cls.graph, cls.scale, cls.ev = _services()

    def test_every_claim_carries_an_evidence_class(self):
        """[FR-EVID-002] A bare assertion is the failure mode (BRB-02)."""
        for c in self.ev.all_claims():
            self.assertTrue(c.evidence_class, f'{c.id} has no class')
            self.assertNotEqual(c.class_name, 'UNRECOGNISED', c.id)

    def test_every_claim_record_is_complete(self):
        """[FR-EVID-001] Missing a required field is inadmissible (INV-07)."""
        for c in self.ev.all_claims():
            for field in ('species', 'population', 'limitations',
                          'assigned_by', 'date_asserted'):
                self.assertTrue(getattr(c, field),
                                f'{c.id} missing {field}')

    def test_quantitative_claims_carry_units(self):
        """[FR-EVID-008] 70 mL and 70 % are different claims (INV-04)."""
        for c in self.ev.all_claims():
            obj = c.object
            numeric = isinstance(obj, (int, float)) and not isinstance(obj, bool)
            if isinstance(obj, dict):
                numeric = any(isinstance(v, (int, float))
                              and not isinstance(v, bool) for v in obj.values())
            if numeric:
                self.assertTrue(c.unit, f'{c.id} is quantitative with no unit')

    def test_cross_species_claims_carry_transfer_justification(self):
        """[FR-EVID-007] Unlabelled animal data is wrong, not approximate."""
        for c in self.ev.all_claims():
            if c.is_cross_species:
                self.assertTrue(c.transfer_justification,
                                f'{c.id} is {c.species} with no justification')

    def test_strong_classes_require_a_human_reviewer(self):
        """[FR-EVID-004] No agent may assign EVC-1 or EVC-2 (BR-002)."""
        for c in self.ev.all_claims():
            if c.evidence_class in ('EVC-1', 'EVC-2'):
                self.assertTrue(
                    c.assigned_by.startswith('human:'),
                    f'{c.id} is {c.evidence_class} assigned by {c.assigned_by}')

    def test_class_is_supported_by_its_source_type(self):
        """[FR-EVID-003] Confidence may not exceed what the source admits."""
        for c in self.ev.all_claims():
            self.assertTrue(self.ev.class_is_supported(c),
                            f'{c.id}: {c.evidence_class} from {c.source_type}')


class TestProvenance(unittest.TestCase):
    """[FR-EVID-010] [FR-EVID-011]"""

    @classmethod
    def setUpClass(cls):
        cls.graph, cls.scale, cls.ev = _services()

    def test_any_claim_produces_a_complete_provenance_record(self):
        """[FR-EVID-010] Without human interpretation."""
        for c in self.ev.all_claims():
            rec = self.ev.provenance(c.id).as_dict()
            for key in ('evidence_class', 'species', 'population',
                        'date_asserted', 'limitations', 'assigned_by',
                        'presentation_constraint'):
                self.assertIn(key, rec)
                self.assertIsNotNone(rec[key], f'{c.id}.{key} is null')

    def test_class_constrains_downstream_presentation(self):
        """[FR-EVID-011] Enforced in the pipeline, not in prompt wording."""
        approx = [c for c in self.ev.all_claims()
                  if c.evidence_class == 'EVC-4']
        self.assertTrue(approx, 'the slice should contain an approximation')
        rec = self.ev.provenance(approx[0].id)
        self.assertIn('approximation', rec.presentation_constraint)

    def test_provenance_marks_who_assigned_the_class(self):
        """[FR-EVID-004] The assigner is part of the record, not a side note."""
        rec = self.ev.provenance('CLM:heart-function-pump')
        self.assertTrue(rec.reviewed_by_human)
        seed = self.ev.provenance(
            'CLM:seed-cardiaccycle-definition')
        self.assertFalse(seed.reviewed_by_human,
                         'seed content was ingested, not reviewed')

    def test_no_claim_is_graded_verified(self):
        """[FR-EVID-003] No domain reviewer has examined this substrate, and a
        reference text cannot support EVC-1 however authoritative (D-013)."""
        verified = [c.id for c in self.ev.all_claims()
                    if c.evidence_class == 'EVC-1']
        self.assertEqual(verified, [],
                         'EVC-1 requires human in-vivo measurement under review')

    def test_agent_assigned_claims_never_reach_the_strong_classes(self):
        """[FR-EVID-004] BR-002, checked against the shipped content."""
        for c in self.ev.all_claims():
            if not c.assigned_by.startswith('human:'):
                self.assertNotIn(c.evidence_class, ('EVC-1', 'EVC-2'),
                                 f'{c.id} is {c.evidence_class} from '
                                 f'{c.assigned_by}')

    def test_strong_classes_require_independent_sources(self):
        """[FR-EVID-003] EVC-2 means sources agree, not that one source is good."""
        for c in self.ev.all_claims():
            if c.evidence_class in ('EVC-1', 'EVC-2'):
                self.assertGreaterEqual(
                    len(c.sources), 2,
                    f'{c.id} is {c.evidence_class} on {len(c.sources)} source(s)')


class TestNegativeSpace(unittest.TestCase):
    """[FR-EVID-005] [FR-EVID-013] [FR-SRCH-004]"""

    @classmethod
    def setUpClass(cls):
        cls.graph, cls.scale, cls.ev = _services()

    def test_unknown_is_an_asserted_stored_claim(self):
        """[FR-EVID-005] Not an absent row."""
        unknowns = self.ev.unknowns()
        self.assertTrue(unknowns, 'the slice records gaps deliberately')
        for c in unknowns:
            self.assertEqual(c.evidence_class, UNKNOWN)
            self.assertTrue(c.limitations)

    def test_unknown_claims_are_returned_with_an_entitys_claims(self):
        """[FR-EVID-005] A gap is not hidden to make a list look complete."""
        rows = self.ev.claims_for('UBERON:0002349')
        self.assertTrue(any(c.is_unknown for c in rows))

    def test_unknown_count_splits_asked_for_from_unprompted(self):
        """[FR-EVID-013] The count detects deletion; the split detects padding."""
        counts = self.ev.unknown_counts()
        self.assertEqual(counts['total'],
                         counts['asked_for'] + counts['unprompted'])
        self.assertIn('padding', counts['note'])

    def test_negative_space_distinguishes_unassessed_from_no_gaps(self):
        """[FR-SRCH-004] Three cases an empty result would conflate."""
        with_gap = self.ev.negative_space('UBERON:0002349')
        self.assertTrue(with_gap.assessed)
        self.assertTrue(with_gap.unknown_claims)

        assessed_clean = self.ev.negative_space('UBERON:0000948')
        self.assertTrue(assessed_clean.assessed)
        self.assertFalse(assessed_clean.unknown_claims)
        self.assertIn('assessed', assessed_clean.statement)

        unassessed = self.ev.negative_space('CHEBI:15422')
        self.assertFalse(unassessed.assessed)
        self.assertIn('not evidence that none exist', unassessed.statement)

    def test_negative_space_reports_unpopulated_declared_levels(self):
        """[FR-SRCH-004] Scope gaps count as things the model does not hold."""
        ns = self.ev.negative_space('UBERON:0000948')
        self.assertEqual(ns.declared_depth, 10)
        self.assertIn(0, ns.unpopulated_levels)


class TestConflicts(unittest.TestCase):
    """[FR-EVID-006]"""

    @classmethod
    def setUpClass(cls):
        cls.graph, cls.scale, cls.ev = _services()

    def test_conflicting_claims_are_both_retained(self):
        """[FR-EVID-006] The system never selects between credible sources."""
        from homeo.substrate import Claim
        a = Claim(id='CLM:a', subject='UBERON:0000948', predicate='mass',
                  object=300, evidence_class='EVC-2',
                  source_type='primary research', species='Homo sapiens',
                  population='adult male', date_asserted='2026-01-01',
                  limitations='none identified', assigned_by='human:r1',
                  unit='g', sources=({'citation': 'A', 'identifier': 'DOI:a'},),
                  conflicts_with=('CLM:b',))
        b = Claim(id='CLM:b', subject='UBERON:0000948', predicate='mass',
                  object=250, evidence_class='EVC-2',
                  source_type='primary research', species='Homo sapiens',
                  population='adult female', date_asserted='2026-01-01',
                  limitations='none identified', assigned_by='human:r2',
                  unit='g', sources=({'citation': 'B', 'identifier': 'DOI:b'},),
                  conflicts_with=('CLM:a',))
        sub = load(SUBSTRATE)
        sub.claims.extend([a, b])
        g = Graph(sub)
        ev = EvidenceService(g, ScaleService(g))
        both = ev.claims_for('UBERON:0000948', predicate='mass')
        self.assertEqual(len(both), 2, 'neither claim was dropped')
        conflicts = ev.conflicts('CLM:a')
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].claim_id, 'CLM:b')
        # The populations differ, which is what makes this a scoping difference
        # rather than a contradiction — and the field is what surfaces it.
        self.assertNotEqual(conflicts[0].population, a.population)


class TestCompleteness(unittest.TestCase):
    """[FR-EVID-001] — G-03 is computed, never asserted."""

    def test_completeness_is_derived_from_records(self):
        _, _, ev = _services()
        report = ev.completeness()
        self.assertEqual(report['claims'], len(ev.all_claims()))
        self.assertAlmostEqual(
            report['proportion'],
            report['complete_records'] / report['claims'], places=6)
        self.assertEqual(sum(report['by_class'].values()), report['claims'])


if __name__ == '__main__':
    unittest.main()
