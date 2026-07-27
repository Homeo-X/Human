"""Search across the five modes, plus structured query."""
import unittest

from homeo.evidence import EvidenceService
from homeo.graph import Graph
from homeo.scale import ScaleService
from homeo.search import QuerySyntaxError, SearchService
from homeo.substrate import load

SUBSTRATE = 'ontology'


def _search():
    g = Graph(load(SUBSTRATE))
    s = ScaleService(g)
    return SearchService(g, EvidenceService(g, s), s)


class TestNameSearch(unittest.TestCase):
    """[FR-SRCH-001] [FR-SRCH-002]"""

    @classmethod
    def setUpClass(cls):
        cls.search = _search()

    def test_exact_term_outranks_substring(self):
        """[FR-SRCH-001] 'cor' must find the heart, not 'Cortex'."""
        rs = self.search.search('cor', 'name')
        self.assertEqual(rs.results[0].entity_id, 'UBERON:0000948')
        self.assertIn('synonym', rs.results[0].matched_on)

    def test_matched_form_is_reported(self):
        """[FR-SRCH-001] Showing which term matched teaches the vocabulary."""
        rs = self.search.search('cardiomyocyte', 'name')
        self.assertEqual(rs.results[0].matched_term, 'cardiomyocyte')
        self.assertIn('clinical', rs.results[0].matched_on)

    def test_results_carry_compilation_status(self):
        """[FR-SRCH-002] A results list is where grading is most easily lost."""
        rs = self.search.search('Heart', 'name')
        for r in rs.results:
            self.assertIn(r.compilation_status,
                          ('narrative', 'structured', 'mechanistic',
                           'parameterized'))

    def test_no_match_offers_near_terms_not_an_empty_result(self):
        """[FR-SRCH-001] An empty result teaches nothing."""
        rs = self.search.search('zzzznotathing', 'name')
        self.assertEqual(rs.results, [])
        self.assertIsNotNone(rs.statement)
        self.assertIn('No match', rs.statement)


class TestFunctionSearch(unittest.TestCase):
    """[FR-SRCH-003]"""

    @classmethod
    def setUpClass(cls):
        cls.search = _search()

    def test_matches_claims_not_only_labels(self):
        rs = self.search.search('propels blood', 'function')
        self.assertTrue(rs.results)
        self.assertEqual(rs.results[0].entity_id, 'UBERON:0000948')
        self.assertIsNotNone(rs.results[0].matched_claim)

    def test_narrative_hits_are_marked_as_descriptive(self):
        """[FR-SRCH-003] Narrative content must not imply a modelled function."""
        rs = self.search.search('hierarchical model', 'function')
        narrative = [r for r in rs.results
                     if r.compilation_status == 'narrative']
        self.assertTrue(narrative)
        self.assertIn('does not model it', narrative[0].note)

    def test_results_carry_the_matching_claims_class(self):
        """[FR-SRCH-002] The grade travels with the hit."""
        rs = self.search.search('propels blood', 'function')
        self.assertEqual(rs.results[0].evidence_class, 'EVC-2')


class TestClinicalSearch(unittest.TestCase):
    """[FR-SRCH-008] — mapping, never diagnosis."""

    @classmethod
    def setUpClass(cls):
        cls.search = _search()

    def test_clinical_term_maps_to_structures(self):
        rs = self.search.search('heart attack', 'clinical')
        ids = {r.entity_id for r in rs.results}
        self.assertIn('UBERON:0000948', ids)

    def test_result_states_it_is_a_mapping_not_a_diagnosis(self):
        rs = self.search.search('heart attack', 'clinical')
        self.assertIn('not a diagnosis', rs.results[0].note)
        self.assertIn('does not diagnose', rs.statement)

    def test_unmapped_term_states_the_boundary(self):
        rs = self.search.search('unknown syndrome', 'clinical')
        self.assertEqual(rs.results, [])
        self.assertIn('does not interpret, diagnose, or advise', rs.statement)


class TestSpatialSearch(unittest.TestCase):
    """[FR-SRCH-007] [FR-SPAT-008] — over spatial identities, not meshes."""

    @classmethod
    def setUpClass(cls):
        cls.search = _search()

    def test_adjacency_resolves_without_any_geometry(self):
        rs = self.search.search('adjacent_to:UBERON:0000948', 'spatial')
        self.assertTrue(rs.results)

    def test_containment_predicate(self):
        rs = self.search.search('contained_in:UBERON:0002084', 'spatial')
        self.assertEqual([r.entity_id for r in rs.results], ['UBERON:0000948'])

    def test_entity_without_spatial_identity_says_so(self):
        rs = self.search.search('adjacent_to:CHEBI:15422', 'spatial')
        self.assertIn('no spatial identity', rs.statement)

    def test_malformed_spatial_query_is_rejected(self):
        with self.assertRaises(QuerySyntaxError):
            self.search.search('adjacent UBERON:0000948', 'spatial')

    def test_unknown_predicate_is_rejected(self):
        with self.assertRaises(QuerySyntaxError):
            self.search.search('near:UBERON:0000948', 'spatial')


class TestNegativeSearch(unittest.TestCase):
    """[FR-SRCH-004] — the feature that makes honesty usable."""

    @classmethod
    def setUpClass(cls):
        cls.search = _search()

    def test_returns_recorded_gaps(self):
        rs = self.search.search('UBERON:0002349', 'negative')
        self.assertTrue(rs.results)
        self.assertEqual(rs.results[0].evidence_class, 'EVC-8')

    def test_reports_declared_but_unpopulated_levels(self):
        rs = self.search.search('UBERON:0000948', 'negative')
        self.assertIn('unpopulated levels', rs.statement)

    def test_never_assessed_is_distinct_from_no_gaps(self):
        rs = self.search.search('CHEBI:15422', 'negative')
        self.assertIn('not evidence that none exist', rs.statement)


class TestStructuredQuery(unittest.TestCase):
    """[FR-SRCH-005] [FR-SRCH-006]"""

    @classmethod
    def setUpClass(cls):
        cls.search = _search()

    def test_filters_by_class_and_subsystem(self):
        rs = self.search.search('class=Organelle subsystem=cardiovascular',
                                'structured')
        self.assertEqual(len(rs.results), 3)
        self.assertTrue(all(r.subsystem == 'cardiovascular'
                            for r in rs.results))

    def test_filters_by_level(self):
        rs = self.search.search('level=3', 'structured')
        self.assertTrue(all(r.level == 3 for r in rs.results))

    def test_filters_by_compilation_status(self):
        rs = self.search.search('status=mechanistic', 'structured')
        self.assertTrue(rs.results)
        self.assertTrue(all(r.compilation_status == 'mechanistic'
                            for r in rs.results))

    def test_filters_by_relation_presence(self):
        rs = self.search.search('relation=consumes', 'structured')
        self.assertTrue(rs.results)

    def test_malformed_query_reports_position_not_partial_results(self):
        """[FR-SRCH-005] Never a silent partial execution."""
        with self.assertRaises(QuerySyntaxError) as ctx:
            self.search.search('class Organelle', 'structured')
        self.assertIn('expected key=value', str(ctx.exception))

    def test_unknown_filter_key_is_rejected(self):
        with self.assertRaises(QuerySyntaxError):
            self.search.search('colour=red', 'structured')

    def test_evidence_filter_reports_what_it_hid(self):
        """[FR-SRCH-006] An empty filtered view must not read as 'nothing known'."""
        rs = self.search.search('class=CellType', 'structured',
                                min_class='EVC-2')
        self.assertGreater(rs.excluded_by_filter, 0)
        self.assertIn('EVC-2', rs.ranking_basis)

    def test_unknown_mode_is_rejected(self):
        with self.assertRaises(QuerySyntaxError):
            self.search.search('x', 'telepathy')


if __name__ == '__main__':
    unittest.main()
