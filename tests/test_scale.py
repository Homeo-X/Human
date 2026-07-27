"""Scale contracts, declared depth, the terminal answer, and coverage."""
import unittest

from homeo.graph import Graph
from homeo.scale import ScaleService, TerminalAnswer
from homeo.substrate import load

SUBSTRATE = 'ontology'


class TestContracts(unittest.TestCase):
    """[FR-SCAL-001] [FR-SCAL-008]"""

    @classmethod
    def setUpClass(cls):
        cls.scale = ScaleService(Graph(load(SUBSTRATE)))

    def test_all_eleven_levels_declared(self):
        """[FR-SCAL-001] L0 through L10 each have a contract."""
        for level in range(11):
            self.assertIsNotNone(self.scale.contract(level), f'L{level} missing')

    def test_every_contract_states_its_resolution_limit(self):
        """[FR-SCAL-001] An undeclared limit is how a model overclaims (BRB-01)."""
        for level in range(11):
            c = self.scale.contract(level)
            self.assertTrue(c.resolution_limit.strip(), f'L{level} has no limit')
            self.assertTrue(c.evidence_model.strip())
            self.assertTrue(c.representation_mode)

    def test_common_eight_level_scheme_maps_explicitly(self):
        """[FR-SCAL-008] Mapping prevents silent renumbering on ingest."""
        self.assertEqual(self.scale.map_common_scheme(1), 0)   # whole body
        self.assertEqual(self.scale.map_common_scheme(6), 7)   # cells
        self.assertEqual(self.scale.map_common_scheme(8), 9)   # mechanism
        with self.assertRaises(KeyError):
            self.scale.map_common_scheme(9)


class TestDeclaredDepth(unittest.TestCase):
    """[FR-SCAL-002] [FR-SCAL-006]"""

    @classmethod
    def setUpClass(cls):
        cls.scale = ScaleService(Graph(load(SUBSTRATE)))

    def test_declared_depth_is_enforced_not_advisory(self):
        """[FR-SCAL-002] L7 content in an L3 subsystem is out of contract."""
        self.assertTrue(self.scale.within_declared_depth('cardiovascular', 7))
        self.assertFalse(self.scale.within_declared_depth('endocrine', 7))

    def test_no_entity_exceeds_its_subsystems_declaration(self):
        """[FR-SCAL-002] Holds across the whole substrate, seed included."""
        for e in self.scale.graph.entities():
            cap = self.scale.declared(e.subsystem)
            self.assertIsNotNone(cap, f'{e.id}: subsystem has no declared depth')
            for level in e.levels:
                self.assertLessEqual(
                    level, cap,
                    f'{e.id} at L{level} exceeds declared L{cap} '
                    f'for {e.subsystem}')

    def test_spanning_entities_respect_depth_at_every_level(self):
        """[FR-SCAL-006] Spanning is not a route around the contract."""
        for e in self.scale.graph.entities():
            if not e.is_spanning:
                continue
            cap = self.scale.declared(e.subsystem)
            for level in e.spatial_scale:
                self.assertLessEqual(level, cap, f'{e.id} spans beyond L{cap}')

    def test_spanning_entities_state_per_level_contributions(self):
        """[FR-SCAL-005] A spanning entity says what it does at each level."""
        for e in self.scale.graph.entities():
            if e.is_spanning:
                self.assertTrue(e.level_contributions,
                                f'{e.id} spans levels with no contributions')


class TestTerminalAnswer(unittest.TestCase):
    """[FR-SCAL-003] [FR-NAV-002] [FR-NAV-003]"""

    @classmethod
    def setUpClass(cls):
        cls.scale = ScaleService(Graph(load(SUBSTRATE)))

    def test_descending_below_declared_depth_returns_an_answer(self):
        """[FR-SCAL-003] Not an empty result and not an error."""
        result = self.scale.descend('HOX:mechanism:cross-bridge-cycle')
        self.assertIsInstance(result, TerminalAnswer)
        self.assertIn('Not represented at this level', result.statement)

    def test_terminal_answer_is_about_the_model_not_the_biology(self):
        """[FR-SCAL-003] The wording distinction is the whole point."""
        result = self.scale.terminal_answer('endocrine', 7)
        self.assertIn('statement about the model', result.statement)
        self.assertIn('not about the biology', result.statement)
        self.assertEqual(result.declared_level, 3)

    def test_terminal_answer_carries_the_resolution_limit(self):
        """[FR-SCAL-003] The user learns what the level cannot represent."""
        result = self.scale.terminal_answer('cardiovascular', 11)
        self.assertTrue(result.resolution_limit.strip())
        self.assertTrue(result.representation_mode)

    def test_descend_returns_children_when_they_exist(self):
        """[FR-SCAL-003] The terminal answer is reached only at the edge."""
        self.assertEqual(self.scale.descend('UBERON:0000948'),
                         ['UBERON:0002084'])

    def test_transition_announces_mode_and_limit(self):
        """[FR-NAV-002] Announced on every crossing, not once per session."""
        t = self.scale.transition(7, from_level=5).as_dict()
        self.assertEqual(t['to_level'], 7)
        self.assertTrue(t['resolution_limit'])
        self.assertFalse(t['located_in_body'])
        self.assertIn('not a located object', t['note'])

    def test_enumerated_level_is_located_in_body(self):
        """[FR-NAV-002] The note appears only where it is true."""
        t = self.scale.transition(3).as_dict()
        self.assertTrue(t['located_in_body'])
        self.assertIsNone(t['note'])


class TestCrossScalePath(unittest.TestCase):
    """[FR-SCAL-009]"""

    @classmethod
    def setUpClass(cls):
        cls.scale = ScaleService(Graph(load(SUBSTRATE)))

    def test_path_across_the_slice_is_found_but_not_complete(self):
        """[FR-SCAL-009] A path that skips a level is found, not complete.

        The slice has no L1 entity, so the containment chain jumps L0 to L2.
        Reporting that as complete is the failure the model exists to prevent,
        and it is what this tool did before D-013.
        """
        p = self.scale.cross_scale_path('UBERON:0000468', 'GO:0030017')
        self.assertTrue(p['path_found'])
        self.assertFalse(p['level_contiguous'])
        self.assertFalse(p['complete'])
        self.assertEqual(p['missing_levels'], [1])
        self.assertIn('skips L1', p['statement'])
        levels = [s['level'] for s in p['steps']]
        self.assertEqual((levels[0], levels[-1]), (0, 8))

    def test_a_contiguous_path_is_reported_complete(self):
        """[FR-SCAL-009] The gap report must not fire on a sound path."""
        p = self.scale.cross_scale_path('UBERON:0000948', 'GO:0030017')
        self.assertTrue(p['complete'])
        self.assertEqual(p['missing_levels'], [])

    def test_broken_chain_is_reported_not_silently_empty(self):
        """[FR-SCAL-009] The gap is the interesting result."""
        p = self.scale.cross_scale_path('CHEBI:15422', 'CHEBI:29108')
        self.assertFalse(p['complete'])
        self.assertIn('No containment path', p['statement'])


class TestCoverage(unittest.TestCase):
    """[FR-SCAL-010] — G-01's denominator, made visible."""

    @classmethod
    def setUpClass(cls):
        cls.scale = ScaleService(Graph(load(SUBSTRATE)))

    def test_coverage_reports_counts_against_declared_depth(self):
        """[FR-SCAL-010] Counts, never a bare percentage (BR-021)."""
        rows = self.scale.coverage('cardiovascular')
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.declared_depth, 10)
        self.assertEqual(len(row.cells), 11)
        self.assertTrue(any(c.populated for c in row.cells))

    def test_unmet_declarations_are_surfaced(self):
        """[FR-SCAL-010] A declared level with no content is a promise unkept."""
        summary = self.scale.coverage_summary()
        self.assertGreater(summary['unmet_declarations'], 0,
                           'the honest state of this release has unmet levels')
        self.assertIn('unmet declaration', summary['note'])

    def test_every_declared_subsystem_appears(self):
        """[FR-SCAL-010] Nothing is omitted from the coverage view."""
        rows = {r.subsystem for r in self.scale.coverage()}
        self.assertEqual(rows, set(self.scale.declared_depth))


if __name__ == '__main__':
    unittest.main()
