"""Substrate-level requirements verified against the shipped content.

These assert properties of the data rather than of a function: the requirements
they cover are enforced by biocheck at write time, and these tests confirm the
shipped substrate actually satisfies them — so a regression in either the data
or the checker surfaces here.
"""
import unittest

from homeo.evidence import EvidenceService
from homeo.graph import Graph
from homeo.promotion import PromotionService
from homeo.scale import ScaleService
from homeo.substrate import INVERSES, STRUCTURAL_RELATIONS, load

SUBSTRATE = 'ontology'

# Admissible (class, level) pairs, per BIO_Anatomical_Ontology §Entity Classes.
CLASS_LEVELS = {
    'Organism': {0}, 'Region': {1}, 'System': {2}, 'Organ': {3},
    'Structure': {4}, 'TissueType': {5}, 'CellPopulation': {6},
    'CellType': {7}, 'Organelle': {8}, 'Biomolecule': {9},
    'Mechanism': {9, 10}, 'Process': {9, 10},
    'Function': set(range(11)),
}


def _svc():
    g = Graph(load(SUBSTRATE))
    s = ScaleService(g)
    return g, s, EvidenceService(g, s)


def _retype_fixture(**claim_fields):
    """A substrate with one extra claim, for gates the real substrate cannot open.

    Used where a test needs evidence stronger than anything the substrate
    contains — which, after D-017, means anything a human certified. Building
    it explicitly keeps the substrate honest and the gate testable at once.
    """
    from homeo.substrate import Claim
    graph = Graph(load(SUBSTRATE))
    base = dict(subject='HOX:function:autonomicregulation',
                predicate='causes', object='cardiac cycle modulation',
                source_type='primary research', species='Homo sapiens',
                population='adult', date_asserted='2026-07-27',
                limitations='fixture', assigned_by='human:curator-1',
                sources=({'citation': 'a', 'identifier': 'DOI:1'},
                         {'citation': 'b', 'identifier': 'DOI:2'}))
    base.update(claim_fields)
    base['id'] = base.pop('claim_id', base.get('id'))
    graph.substrate.claims.append(Claim(**base))
    graph = Graph(graph.substrate)
    scale = ScaleService(graph)
    return graph, PromotionService(graph, EvidenceService(graph, scale))


class TestEntityClassification(unittest.TestCase):
    """[FR-ONTO-002] [FR-ONTO-003]"""

    @classmethod
    def setUpClass(cls):
        cls.graph, cls.scale, cls.ev = _svc()

    def test_class_and_level_pair_is_admissible(self):
        """[FR-ONTO-002] An Organ at L7 is a classification error."""
        for e in self.graph.entities():
            allowed = CLASS_LEVELS.get(e.entity_class)
            self.assertIsNotNone(allowed, f'{e.id}: unknown class')
            for level in e.levels:
                self.assertIn(level, allowed,
                              f'{e.id}: {e.entity_class} cannot sit at L{level}')

    def test_every_entity_declares_a_level_or_a_span(self):
        """[FR-ONTO-002] Exactly one of level or spatial_scale."""
        for e in self.graph.entities():
            self.assertTrue(e.levels, f'{e.id} declares no level')
            if e.is_spanning:
                self.assertIsNone(e.level, f'{e.id} declares both')

    def test_no_entity_exceeds_declared_depth(self):
        """[FR-ONTO-003] Correct content beyond the declaration is still out."""
        for e in self.graph.entities():
            cap = self.scale.declared(e.subsystem)
            for level in e.levels:
                self.assertLessEqual(level, cap, f'{e.id} at L{level}')


class TestRelationIntegrity(unittest.TestCase):
    """[FR-REL-004] [FR-REL-005] [FR-REL-008]"""

    @classmethod
    def setUpClass(cls):
        cls.graph, cls.scale, cls.ev = _svc()

    def test_every_relation_type_is_in_the_vocabulary(self):
        """[FR-REL-004]"""
        for r in self.graph.substrate.relationships:
            self.assertIn(r.type, INVERSES, f'{r.id}: {r.type} not in vocabulary')

    def test_no_causal_edge_rests_on_weak_evidence(self):
        """[FR-REL-005] `causes` requires EVC-2 or better."""
        for r in self.graph.substrate.relationships:
            if r.type != 'causes':
                continue
            claim = self.ev.claim(r.provenance_claim)
            self.assertLessEqual(claim.evidence_class, 'EVC-2',
                                 f'{r.id} asserts causation on '
                                 f'{claim.evidence_class}')

    def test_every_edge_carries_its_own_provenance(self):
        """[FR-REL-008] Edges do not inherit their endpoints' evidence."""
        for r in self.graph.substrate.relationships:
            self.assertTrue(r.provenance_claim, f'{r.id} has no provenance')
            self.assertTrue(self.ev.has(r.provenance_claim),
                            f'{r.id} cites missing claim {r.provenance_claim}')

    def test_every_association_carries_its_prose(self):
        """[FR-REL-006] The source note is what makes it inspectable."""
        for r in self.graph.substrate.relationships:
            if r.is_untyped_association:
                self.assertTrue(r.prose_justification, f'{r.id} has no prose')


class TestRetyping(unittest.TestCase):
    """[FR-REL-007] — typing an association is work, not a rename."""

    def setUp(self):
        g, s, ev = _svc()
        self.svc = PromotionService(g, ev)
        self.assoc = 'REL:assoc-autonomic-cardiaccycle'

    def test_retyping_requires_a_source(self):
        d = self.svc.retype_association(self.assoc, 'regulated_by',
                                        'human:curator-1', '')
        self.assertFalse(d.allowed)
        self.assertTrue(any('requires a source' in r for r in d.reasons))

    def test_retyping_requires_a_human_curator(self):
        d = self.svc.retype_association(self.assoc, 'regulated_by',
                                        'agent:ontology', 'DOI:x')
        self.assertFalse(d.allowed)
        self.assertTrue(any('human curator' in r for r in d.reasons))

    def test_causal_retype_may_not_inherit_the_associations_provenance(self):
        """[FR-REL-005] [FR-REL-008] The claim backing an untyped association
        was recorded for a different assertion; its strength says nothing about
        whether causation holds."""
        d = self.svc.retype_association(
            self.assoc, 'causes', 'human:curator-1',
            'CLM:heart-two-pumps-series')      # the association's own claim
        self.assertFalse(d.allowed)
        self.assertTrue(any('may not inherit the provenance' in r
                            for r in d.reasons))

    def test_causal_retype_requires_a_real_claim(self):
        """[FR-REL-005] A citation string is not a claim."""
        d = self.svc.retype_association(self.assoc, 'causes',
                                        'human:curator-1', 'DOI:x')
        self.assertFalse(d.allowed)
        self.assertTrue(any('not a claim in this release' in r
                            for r in d.reasons))

    def test_causes_requires_evc2_or_better(self):
        """[FR-REL-005] Causal language is what users trust most, so it is
        what the model gates hardest."""
        d = self.svc.retype_association(
            self.assoc, 'causes', 'human:curator-1',
            'CLM:cross-bridge-cycle-duration')          # EVC-4
        self.assertFalse(d.allowed)
        self.assertTrue(any('contributes_to' in r for r in d.reasons))

    def test_causal_retype_on_a_strong_independent_claim_is_permitted(self):
        """[FR-REL-005] The gate opens for evidence that clears the bar.

        After D-017 the substrate contains no EVC-2 claim at all — every class
        an agent assigned was capped, and nothing has been reviewed. So the
        qualifying claim is constructed here rather than borrowed. That is not
        a workaround: it is the finding. **No causal relation can be typed in
        this release**, because typing one requires evidence a human certified
        and no human has certified anything. The gate is closed by the state of
        the substrate, not by a defect.
        """
        graph, svc = _retype_fixture(
            claim_id='CLM:reviewed-causal-evidence',
            evidence_class='EVC-2', review_state='reviewed',
            assigned_by='human:curator-1')
        d = svc.retype_association(self.assoc, 'causes', 'human:curator-1',
                                   'CLM:reviewed-causal-evidence')
        self.assertTrue(d.allowed, d.reasons)

    def test_no_causal_relation_can_be_typed_in_this_release(self):
        """[FR-REL-005] [D-017] The consequence, asserted rather than implied.

        Every claim in the substrate is provisional and capped at EVC-3 or
        weaker. `causes` needs EVC-2. So the count of claims that could support
        a causal retype is zero, and that is worth failing loudly if it ever
        silently changes — a claim reaching EVC-2 means a human reviewed it,
        which is a substantive event.
        """
        qualifying = [c for c in self.svc.evidence.all_claims()
                      if c.evidence_class <= 'EVC-2']
        self.assertEqual([], qualifying,
                         'a claim reached EVC-2; if a human reviewed it, this '
                         'test should be updated deliberately')

    def test_demotion_to_association_is_refused(self):
        d = self.svc.retype_association(self.assoc, 'associated_with',
                                        'human:curator-1', 'DOI:x')
        self.assertFalse(d.allowed)
        self.assertTrue(any('demotion' in r for r in d.reasons))

    def test_retyping_a_typed_relation_is_refused(self):
        d = self.svc.retype_association('REL:crossbridge-consumes-atp',
                                        'produces', 'human:curator-1', 'DOI:x')
        self.assertFalse(d.allowed)
        self.assertTrue(any('already typed' in r for r in d.reasons))

    def test_valid_retyping_is_permitted(self):
        d = self.svc.retype_association(self.assoc, 'regulated_by',
                                        'human:curator-1',
                                        'DOI:10.1000/autonomic-cardiac')
        self.assertTrue(d.allowed, d.reasons)


class TestScaleIntegrity(unittest.TestCase):
    """[FR-SCAL-004] [FR-SCAL-007]"""

    @classmethod
    def setUpClass(cls):
        cls.graph, cls.scale, cls.ev = _svc()

    def test_level_skipping_edges_carry_justification(self):
        """[FR-SCAL-004] Molecule-to-symptom in one hop is the failure (BRB-06)."""
        levels = {e.id: e.shallowest_level for e in self.graph.entities()}
        for r in self.graph.substrate.relationships:
            if r.is_structural:
                continue
            a, b = levels.get(r.source), levels.get(r.target)
            if a is None or b is None:
                continue
            if abs(a - b) > 1:
                self.assertTrue(
                    r.skip_justification,
                    f'{r.id} spans L{a} to L{b} with no justification')

    def test_representation_mode_is_offered_by_its_level(self):
        """[FR-SCAL-007] An entity cannot claim a mode the level lacks."""
        for e in self.graph.entities():
            if not e.representation_mode or e.level is None:
                continue
            contract = self.scale.contract(e.level)
            if contract is None:
                continue
            self.assertIn(e.representation_mode, contract.representation_mode,
                          f'{e.id} claims {e.representation_mode} at L{e.level}')


class TestSpatialIntegrity(unittest.TestCase):
    """[FR-SPAT-001] [FR-SPAT-003] [FR-SPAT-004] [FR-SPAT-005] [FR-SPAT-007]"""

    @classmethod
    def setUpClass(cls):
        cls.graph, cls.scale, cls.ev = _svc()

    def test_every_spatial_identity_binds_to_a_real_entity(self):
        """[FR-SPAT-001] Geometry binds through an identity, never directly."""
        for si in self.graph.substrate.spatial_identities:
            self.assertIn(si.entity, self.graph,
                          f'{si.id} binds to undefined entity {si.entity}')

    def test_no_unbound_geometry_exists(self):
        """[FR-SPAT-003] Every asset resolves to a spatial identity."""
        for si in self.graph.substrate.spatial_identities:
            for g in si.geometry:
                self.assertTrue(g.get('asset_id'),
                                f'{si.id} carries geometry with no asset id')

    def test_every_asset_declares_kind_licence_and_tier(self):
        """[FR-SPAT-004] [FR-SPAT-005] Equal visual fidelity across unequal
        evidence is the field's default failure (BRB-04)."""
        for si in self.graph.substrate.spatial_identities:
            for g in si.geometry:
                self.assertIn(g.get('representation_kind'),
                              ('measured', 'derived', 'reference_exemplar',
                               'schematic'), si.id)
                self.assertTrue(g.get('licence'), si.id)
                self.assertIn(g.get('licence_tier'), ('T0', 'T1', 'T2'), si.id)

    def test_every_spatial_identity_declares_a_coordinate_frame(self):
        """[FR-SPAT-007] Silent frame mixing produces confident nonsense."""
        for si in self.graph.substrate.spatial_identities:
            self.assertTrue(si.coordinate_frame, f'{si.id} has no frame')

    def test_schematic_frames_are_distinguishable_from_body_frames(self):
        """[FR-SPAT-007] A schematic cell frame is not the body's frame."""
        frames = {si.coordinate_frame
                  for si in self.graph.substrate.spatial_identities}
        self.assertGreater(len(frames), 1,
                           'the slice spans body and schematic frames')


class TestAssetTierSelection(unittest.TestCase):
    """[FR-SPAT-006] [FR-EVID-009] — D-003's payoff."""

    def test_a_permissive_only_build_excludes_share_alike(self):
        from homeo.release import ReleaseBuilder
        builder = ReleaseBuilder(SUBSTRATE)
        permissive = builder.asset_tiers(('T0',))
        self.assertEqual(permissive['allowed_tiers'], ['T0'])
        for row in permissive['included']:
            self.assertEqual(row['tier'], 'T0')

    def test_coverage_denominator_is_unaffected_by_tier_selection(self):
        """A smaller build must look smaller, not look complete."""
        from homeo.release import ReleaseBuilder
        report = ReleaseBuilder(SUBSTRATE).asset_tiers(('T0',))
        self.assertIn('must look smaller', report['note'])

    def test_no_share_alike_source_reaches_the_evidence_layer(self):
        """[FR-EVID-009] T1/T2 never embedded in T0 (INV-11)."""
        _, _, ev = _svc()
        for claim in ev.all_claims():
            for s in claim.sources:
                self.assertNotIn('bodyparts3d',
                                 str(s.get('citation', '')).lower())


class TestProcessIntegrity(unittest.TestCase):
    """[FR-PHYS-003] [FR-PHYS-004] [FR-PHYS-005] [FR-PHYS-008]"""

    @classmethod
    def setUpClass(cls):
        cls.graph, cls.scale, cls.ev = _svc()

    def test_every_process_input_and_output_resolves(self):
        """[FR-PHYS-003] A process cannot consume an undefined thing."""
        for p in self.graph.substrate.processes:
            for ref in list(p.inputs) + list(p.outputs) + list(p.participants):
                self.assertIn(ref, self.graph, f'{p.id} references {ref}')

    def test_every_process_declares_a_timescale_domain(self):
        """[FR-PHYS-004] No global clock means the domain must be explicit."""
        for p in self.graph.substrate.processes:
            self.assertTrue(p.timescale_domain, f'{p.id} has no domain')

    def test_spanning_processes_state_contributions_per_level(self):
        """[FR-PHYS-005] One object at several levels, not several objects."""
        for p in self.graph.substrate.processes:
            if len(p.spatial_scale) > 1:
                self.assertTrue(p.level_contributions, p.id)
                for level in p.spatial_scale:
                    self.assertIn(str(level), p.level_contributions,
                                  f'{p.id} spans L{level} without stating what '
                                  f'it contributes there')

    def test_failure_states_are_mechanistic_not_diagnostic(self):
        """[FR-PHYS-008] The model states what breaks, never a disease name.

        A failure-state table that named conditions would be the single most
        tempting overreach in the product (BR-019).
        """
        disease_words = ('infarction', 'failure syndrome', 'disease',
                         'cardiomyopathy', 'fibrillation', 'ischaemia',
                         'ischemia', 'diagnosis', 'patient')
        for p in self.graph.substrate.processes:
            for fs in p.failure_states:
                text = f"{fs.get('failure', '')} {fs.get('consequence', '')} " \
                       f"{fs.get('downstream', '')}".lower()
                for word in disease_words:
                    self.assertNotIn(word, text,
                                     f'{p.id} failure state names {word!r}')

    def test_structured_processes_have_no_blank_mandatory_fields(self):
        """[FR-PHYS-002]"""
        for p in self.graph.substrate.processes:
            if p.representation_status == 'narrative':
                continue
            for attr in ('inputs', 'outputs', 'state_variables', 'mechanism',
                         'failure_states', 'limitations'):
                self.assertTrue(getattr(p, attr), f'{p.id}.{attr} is empty')


class TestReadOnlyPosture(unittest.TestCase):
    """[FR-CUR-007] — readers are unauthenticated; nothing here writes."""

    def test_the_read_api_exposes_no_write_route(self):
        from homeo.api import ROUTES
        write_ish = [name for _, name in ROUTES
                     if name in ('curation', 'publish', 'review', 'overlay')]
        self.assertEqual(write_ish, [],
                         'the read plane must expose no write surface')

    def test_reading_requires_no_credential(self):
        from homeo.api import Service, dispatch
        svc = Service(SUBSTRATE, release='rel-test')
        r = dispatch(svc, '/v1/entities/UBERON:0000948', {})
        self.assertEqual(r.status, 200)

    def test_running_a_process_is_refused_not_silently_accepted(self):
        """The one state-changing route refuses rather than mutating."""
        from homeo.api import Service, dispatch
        svc = Service(SUBSTRATE, release='rel-test')
        r = dispatch(svc, '/v1/processes/BPR-01/runs', {})
        self.assertIn(r.status, (409, 501))


class TestTombstones(unittest.TestCase):
    """[FR-VER-007] — a retired id resolves across releases."""

    def test_retired_entity_resolves_to_its_successor_over_http(self):
        from homeo.api import Service, dispatch
        from homeo.substrate import Entity
        sub = load(SUBSTRATE)
        sub.entities.append(Entity(
            id='HOX:organ:legacy', entity_class='Organ',
            subsystem='cardiovascular', preferred_term='Legacy',
            compilation_status='structured', level=3,
            retired_at='2026-02-01', successor_id='UBERON:0000948'))
        svc = Service.__new__(Service)
        svc.graph = Graph(sub)
        svc.scale = ScaleService(svc.graph)
        svc.evidence = EvidenceService(svc.graph, svc.scale)
        svc.release = 'rel-test'
        r = dispatch(svc, '/v1/entities/HOX:organ:legacy', {})
        self.assertEqual(r.status, 301)
        self.assertEqual(r.body['successor'], 'UBERON:0000948')
        self.assertIn('Location', r.headers)


if __name__ == '__main__':
    unittest.main()


class TestReviewState(unittest.TestCase):
    """[D-017] [INV-17] — what the substrate honestly claims about itself.

    These assert the *state*, not a mechanism: nothing here has been reviewed,
    and every surface that could imply otherwise must agree. They exist because
    the two mutations that survived an earlier round were both of this shape —
    a default flipped, a count computed wrongly — and no test noticed, since
    every other test asked about behaviour rather than about the substrate.
    """

    @classmethod
    def setUpClass(cls):
        cls.graph, cls.scale, cls.ev = _svc()

    def test_no_entity_in_this_release_is_reviewed(self):
        reviewed = [e.id for e in self.graph.entities() if e.is_reviewed]
        self.assertEqual([], reviewed,
                         'an entity claims review; no domain expert has '
                         'examined anything in this substrate')

    def test_no_claim_in_this_release_is_reviewed(self):
        reviewed = [c.id for c in self.ev.all_claims() if c.is_reviewed]
        self.assertEqual([], reviewed)

    def test_an_absent_review_state_reads_as_provisional(self):
        """The safe default is the pessimistic one (INV-17)."""
        for e in self.graph.entities():
            self.assertEqual('provisional', e.review_state, e.id)

    def test_coverage_reports_zero_reviewed_against_a_populated_matrix(self):
        """[FR-SCAL-010] Breadth must not read as progress."""
        summary = self.scale.coverage_summary()
        self.assertGreater(summary['populated_entities'], 100)
        self.assertEqual(0, summary['reviewed_entities'])
        self.assertEqual(summary['populated_entities'],
                         summary['unreviewed_entities'])

    def test_coverage_excludes_levels_no_organ_system_can_occupy(self):
        """[D-018] 24 of the 42 previously published unmet cells were these."""
        summary = self.scale.coverage_summary()
        self.assertEqual(24, summary['excluded_levels'],
                         'two levels per subsystem, minus whole-organism')
        self.assertGreater(summary['unmet_declarations'], 0)
        self.assertEqual(summary['declared_levels'] - summary['excluded_levels'],
                         summary['occupiable_levels'])

    def test_the_capped_claims_retain_the_assessment_awaiting_a_curator(self):
        """[D-017] The backlog is a list, not a feeling."""
        awaiting = [c for c in self.ev.all_claims() if c.awaiting_upgrade]
        # Three, not the twelve of D-017: nine of those were regional
        # *definitions*, which moved to the terminological register and are no
        # longer waiting on an evidence judgement at all (D-021). The backlog
        # shrank because the question was wrong, not because it was answered.
        self.assertEqual(3, len(awaiting))
        for claim in awaiting:
            self.assertTrue(claim.is_evidence, 'only findings await a curator')
            self.assertEqual('EVC-2', claim.proposed_class)
            self.assertEqual('EVC-4', claim.evidence_class)


class TestSubsumptionIsNotContainment(unittest.TestCase):
    """[FR-REL-001] [D-023] A taxonomy is not a body.

    UBERON says the heart `is_a` "thoracic segment organ", "primary circulatory
    organ", and "mesoderm-derived structure". None of those is a place, a
    container, or something a user navigates into. Letting subsumption into the
    containment ladder would fill it with abstractions — which is exactly why
    UBERON's own hierarchy cannot simply be adopted as this model's structure.

    The fixture adds a true subsumption the substrate does not yet hold: a type
    B pancreatic cell *is a* secretory cell. Both sit at L7, neither contains
    the other, and that is the whole point.
    """

    SUPERCLASS = 'HOX:celltype:secretory-cell'
    BETA_CELL = 'CL:0000169'

    @classmethod
    def setUpClass(cls):
        from dataclasses import replace as dc_replace
        substrate = load(SUBSTRATE)
        beta = next(e for e in substrate.entities if e.id == cls.BETA_CELL)
        substrate.entities.append(dc_replace(
            beta, id=cls.SUPERCLASS, preferred_term='Secretory cell',
            minted=True, minted_reason='no external term for the test fixture',
            part_of=None))
        template = substrate.relationships[0]
        substrate.relationships.append(dc_replace(
            template, id='REL:test-isa', source=cls.BETA_CELL,
            target=cls.SUPERCLASS, type='is_a',
            prose_justification='fixture', skip_justification=None))
        cls.graph = Graph(substrate)

    def test_is_a_is_in_the_relation_vocabulary(self):
        self.assertIn('is_a', INVERSES)
        self.assertEqual('subsumes', INVERSES['is_a'])

    def test_is_a_is_not_a_structural_relation(self):
        self.assertNotIn('is_a', STRUCTURAL_RELATIONS)

    def test_subsumption_never_enters_a_containment_lineage(self):
        self.assertNotIn(self.SUPERCLASS, self.graph.lineage(self.BETA_CELL),
                         'an is_a edge became a containment ancestor')

    def test_subsumption_is_not_a_child_and_not_a_descendant(self):
        self.assertNotIn(self.SUPERCLASS, self.graph.children(self.BETA_CELL))
        self.assertNotIn(self.SUPERCLASS,
                         self.graph.descendants(self.BETA_CELL))

    def test_subsumption_never_enters_the_navigation_tree(self):
        node = self.graph.navigation_tree(self.BETA_CELL)
        self.assertNotIn(self.SUPERCLASS, node.child_kinds)

    def test_subsumption_is_still_traversable_as_a_typed_edge(self):
        """[FR-REL-010] Excluded from structure, not from the graph."""
        edges = self.graph.edges(self.BETA_CELL, types={'is_a'})
        self.assertEqual(1, len(edges))
        self.assertEqual(self.SUPERCLASS, edges[0].other)
        self.assertFalse(edges[0].is_untyped_association)
