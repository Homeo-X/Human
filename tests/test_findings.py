"""The first content that is not a definition, and the first bound mesh.

Two things had been built and never exercised against real content. The
evidence ladder held 9 findings against 414 definitions, all of them
cardiovascular and all qualitative — so units, measurement conditions, the
population field and conflict representation were all verified against fixtures
or against nothing. And `depiction: depicted` had never once been produced,
because no geometry existed.

Both gaps were closed by adding real content, and both immediately surfaced a
defect that no amount of testing against fixtures had (D-031). The tests below
are written against the real substrate for that reason: a fixture would have
contained exactly the fields I already knew to include.
"""
import json
import os
import unittest

from homeo.evidence import EvidenceService
from homeo.graph import Graph
from homeo.navigation import NavigationService
from homeo.projection import (DEPICTED, DESCRIBED, UNAVAILABLE,
                              ProjectionService)
from homeo.scale import ScaleService
from homeo.substrate import load

SUBSTRATE = 'ontology'
HEART = 'UBERON:0000948'
LUNG = 'UBERON:0002048'
ASSET = 'ASSET:heart-exemplar-001'


def _services():
    graph = Graph(load(SUBSTRATE))
    scale = ScaleService(graph)
    evidence = EvidenceService(graph, scale)
    return graph, scale, evidence


class TestFindingsExist(unittest.TestCase):
    """[D-030] The substrate holds claims about a body, not only about words."""

    @classmethod
    def setUpClass(cls):
        graph, scale, cls.ev = _services()
        cls.findings = [c for c in cls.ev.all_claims() if c.is_evidence]

    def test_the_evidence_ladder_carries_more_than_a_handful(self):
        self.assertGreaterEqual(
            len(self.findings), 25,
            'the evidence register is the thing this project is for; a dozen '
            'records in it means the machinery has never been used')

    def test_findings_are_not_terminological(self):
        """[D-021] A definition may never be citable as evidence."""
        for claim in self.findings:
            self.assertFalse(claim.is_terminological, claim.id)
            self.assertTrue(claim.evidence_class.startswith('EVC-'), claim.id)

    def test_no_automated_actor_asserted_a_reviewed_class(self):
        """[BR-002] EVC-1 and EVC-2 require a human, and there is none."""
        for claim in self.findings:
            self.assertNotIn(claim.evidence_class, ('EVC-1', 'EVC-2'),
                             f'{claim.id} claims a class no agent may assign')
            self.assertFalse(claim.assigned_by.startswith('human:'), claim.id)


class TestQuantitiesCarryWhatMakesThemFacts(unittest.TestCase):
    """[INV-04] [INV-07] A number without its conditions is not a finding.

    This is the defect E2 was built to find and did. The first version of
    `tools/curate_respiratory.py` recorded fifteen quantities with units and no
    measurement conditions, and the validator asked for them on every one. It
    was right: "tidal volume is 500 mL" becomes a fact about a body only once it
    says at rest, upright, breathing air at sea level.
    """

    @classmethod
    def setUpClass(cls):
        _, _, ev = _services()
        cls.quantities = [c for c in ev.all_claims()
                          if c.is_evidence and isinstance(c.object, (int, float))
                          and not isinstance(c.object, bool)]

    def test_the_substrate_holds_quantitative_findings(self):
        self.assertGreaterEqual(len(self.quantities), 10)

    def test_every_quantity_carries_a_unit(self):
        for claim in self.quantities:
            self.assertTrue(claim.unit, f'{claim.id} is a bare number')

    def test_every_quantity_carries_its_measurement_conditions(self):
        for claim in self.quantities:
            self.assertTrue(
                claim.conditions,
                f'{claim.id} states a value with no conditions — the number is '
                f'not wrong, it is unusable')


class TestThePopulationFieldDiscriminates(unittest.TestCase):
    """[CH-05] The field was decorative on 94% of seeded claims.

    Its whole job is separating a genuine conflict from two populations. Total
    lung capacity differs by roughly 30% between adult males and females; if the
    field could not hold that, the model would have to call one of the two
    measurements wrong.
    """

    @classmethod
    def setUpClass(cls):
        _, _, cls.ev = _services()

    def _tlc(self):
        return [c for c in self.ev.claims_for(LUNG)
                if c.id.startswith('CLM:lung-tlc-')]

    def test_two_values_for_one_predicate_differ_by_population(self):
        pair = self._tlc()
        self.assertEqual(2, len(pair))
        self.assertNotEqual(pair[0].object, pair[1].object)
        self.assertNotEqual(pair[0].population, pair[1].population)

    def test_neither_is_recorded_as_conflicting_with_the_other(self):
        """Different populations are not disagreement."""
        for claim in self._tlc():
            self.assertEqual((), claim.conflicts_with, claim.id)
            self.assertNotEqual('EVC-7', claim.evidence_class)

    def test_no_finding_falls_back_to_the_blanket_population(self):
        for claim in self.ev.all_claims():
            if claim.is_evidence:
                self.assertNotEqual('unspecified in source', claim.population,
                                    f'{claim.id} reintroduced the CH-05 default')


class TestARealConflictIsRepresented(unittest.TestCase):
    """[FR-EVID-006] Both retained; the system never picks.

    Alveolar surface area is ~70 m² by the classic estimate and ~130 m² by
    design-based stereology. The disagreement is methodological and unresolved,
    which is what EVC-7 is for — and until this content arrived, nothing in the
    substrate had ever been in it.
    """

    @classmethod
    def setUpClass(cls):
        _, _, cls.ev = _services()

    def test_the_pair_names_each_other(self):
        a = self.ev.claim('CLM:lung-alveolar-surface-classic')
        b = self.ev.claim('CLM:lung-alveolar-surface-stereology')
        self.assertIn(b.id, a.conflicts_with)
        self.assertIn(a.id, b.conflicts_with)

    def test_both_are_graded_as_conflicting(self):
        for cid in ('CLM:lung-alveolar-surface-classic',
                    'CLM:lung-alveolar-surface-stereology'):
            self.assertEqual('EVC-7', self.ev.claim(cid).evidence_class)

    def test_the_service_returns_the_competing_value_rather_than_choosing(self):
        rival = self.ev.conflicts('CLM:lung-alveolar-surface-classic')
        self.assertEqual(1, len(rival))
        self.assertEqual(130, rival[0].object)
        self.assertIn('never resolve', rival[0].presentation_constraint)

    def test_each_side_states_the_method_that_produced_it(self):
        """A conflict with no stated methods is just two numbers."""
        for cid in ('CLM:lung-alveolar-surface-classic',
                    'CLM:lung-alveolar-surface-stereology'):
            self.assertTrue(self.ev.claim(cid).conditions.get('notes'))


class TestGeometryIsBound(unittest.TestCase):
    """[FR-SPAT-001..005] [D-031] The depiction states, on real content.

    `depicted` had never been produced. `ProjectionService._depiction` checked
    a key named `asset`, while the schema, the release pipeline and biocheck all
    use `asset_id` — so every schema-valid binding would have reported
    `asset_unavailable` forever, and called a naming mistake a pipeline failure.
    Binding one real mesh was what surfaced it.
    """

    @classmethod
    def setUpClass(cls):
        cls.graph, cls.scale, cls.ev = _services()
        cls.nav = NavigationService(cls.graph, cls.scale, cls.ev)

    def _depiction(self, entity, assets):
        proj = ProjectionService(self.graph, self.scale, self.ev,
                                 available_assets=assets)
        state = self.nav.enter(entity)
        found = [e for e in proj.project(state).entities
                 if e.entity == entity]
        self.assertTrue(found, f'{entity} not in its own projection')
        return found[0]

    def test_the_heart_has_a_geometry_binding(self):
        si = self.graph.spatial_identity(HEART)
        self.assertTrue(si.geometry, 'nothing is bound')
        binding = si.geometry[0]
        self.assertEqual(ASSET, binding['asset_id'])

    def test_a_present_asset_reads_depicted(self):
        self.assertEqual(DEPICTED, self._depiction(HEART, {ASSET}).depiction)

    def test_a_missing_asset_reads_asset_unavailable_and_says_why(self):
        """[FR-SPAT-002] A failed asset is a pipeline failure, not thin anatomy."""
        view = self._depiction(HEART, set())
        self.assertEqual(UNAVAILABLE, view.depiction)
        self.assertIn('pipeline failure', view.note)
        self.assertIn(ASSET, view.note)

    def test_an_entity_with_a_spatial_identity_and_no_geometry_is_described(self):
        """[FR-SPAT-002] Fully valid and fully navigable without geometry."""
        described = self._depiction('GO:0030017', {ASSET})
        self.assertEqual(DESCRIBED, described.depiction)

    def test_an_entity_with_no_spatial_identity_is_unplaced_not_described(self):
        """The two absences are different and must not be collapsed: one is
        'we have not authored a mesh', the other is 'we do not record where
        this is at all'."""
        from homeo.projection import UNPLACED
        self.assertEqual(UNPLACED,
                         self._depiction('UBERON:0002349', {ASSET}).depiction)

    def test_an_unchecked_deployment_says_it_did_not_check(self):
        """`None` is not 'everything is fine' — the caveat travels."""
        view = self._depiction(HEART, None)
        self.assertEqual(DEPICTED, view.depiction)
        self.assertIn('was not checked', view.note)

    def test_the_binding_is_not_claimed_to_be_measured(self):
        """[FR-SPAT-004] The whole problem statement is that a well-rendered
        guess is indistinguishable from a well-rendered measurement."""
        binding = self.graph.spatial_identity(HEART).geometry[0]
        self.assertEqual('reference_exemplar', binding['representation_kind'])
        self.assertNotEqual('measured', binding['representation_kind'])

    def test_the_binding_carries_its_licence_and_attribution(self):
        """[FR-SPAT-005] CC-BY is satisfied only if the credit travels."""
        binding = self.graph.spatial_identity(HEART).geometry[0]
        self.assertEqual('T0', binding['licence_tier'])
        self.assertIn('CC BY', binding['licence'])
        self.assertIn('neshallads', binding['attribution'])


class TestTheAssetIsPinnedAndNotVendored(unittest.TestCase):
    """[G-07] [BR-013] The manifest ships; the bytes do not."""

    MANIFEST = os.path.join('ontology', 'assets', 'ASSETS.json')

    def setUp(self):
        with open(self.MANIFEST, encoding='utf-8') as fh:
            self.manifest = json.load(fh)

    def test_every_asset_is_pinned_by_hash(self):
        for asset_id, record in self.manifest['assets'].items():
            self.assertEqual(64, len(record['sha256']), asset_id)
            self.assertTrue(record['url'].startswith('https://'), asset_id)
            self.assertGreater(record['bytes'], 0, asset_id)

    def test_no_asset_bytes_are_committed(self):
        """A share-alike or attribution obligation must not arrive by accident."""
        for record in self.manifest['assets'].values():
            self.assertFalse(
                os.path.isfile(os.path.join('ontology', record['file'])),
                'asset bytes were committed into the substrate tree')

    def test_no_asset_claims_to_be_measured(self):
        for asset_id, record in self.manifest['assets'].items():
            self.assertNotEqual('measured', record['representation_kind'],
                                f'{asset_id} claims to be a measurement')


if __name__ == '__main__':
    unittest.main()
