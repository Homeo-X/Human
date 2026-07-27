"""The read API — routing, payload shape, and the status-code posture.

The posture under test: **the model's limits are 200s, and only genuine caller
errors are 4xx**. A system that 404s "we do not model that" teaches users its
honesty is a malfunction (TECH_API_Specification §Error Handling).
"""
import unittest

from homeo.api import Service, dispatch

SUBSTRATE = 'ontology'
RELEASE = 'rel-test'


def _svc():
    return Service(SUBSTRATE, release=RELEASE)


class TestEnvelope(unittest.TestCase):
    """TECH_API_Specification §Conventions"""

    @classmethod
    def setUpClass(cls):
        cls.svc = _svc()

    def test_every_response_states_the_release_that_answered(self):
        r = dispatch(self.svc, '/v1/entities/UBERON:0000948', {})
        self.assertEqual(r.body['release'], RELEASE)

    def test_every_response_carries_the_non_diagnostic_boundary(self):
        for path in ('/v1/entities/UBERON:0000948', '/v1/levels',
                     '/v1/coverage', '/v1/processes'):
            with self.subTest(path=path):
                r = dispatch(self.svc, path, {})
                self.assertIn('not a medical device',
                              r.body['boundary'].lower())


class TestEntityEndpoints(unittest.TestCase):
    """[FR-ONTO-006] [FR-EVID-002] [FR-SPAT-002]"""

    @classmethod
    def setUpClass(cls):
        cls.svc = _svc()

    def test_entity_payload_always_carries_compilation_status(self):
        """[FR-ONTO-006] Status is never optional in a payload (BRB-29)."""
        r = dispatch(self.svc, '/v1/entities/UBERON:0000948', {})
        self.assertEqual(r.status, 200)
        self.assertIn('compilation_status', r.body)
        self.assertTrue(r.body['compilation_status'])

    def test_entity_payload_summarises_claim_classes(self):
        """[FR-EVID-002] The grade is visible from the entity view."""
        r = dispatch(self.svc, '/v1/entities/UBERON:0000948', {})
        self.assertIn('classes', r.body['claim_summary'])
        self.assertTrue(r.body['claim_summary']['classes'])

    def test_entity_without_geometry_is_described_not_broken(self):
        """[FR-SPAT-002] Described, not depicted, is a designed state."""
        r = dispatch(self.svc, '/v1/entities/UBERON:0000948', {})
        note = r.body['spatial_identity']['note']
        self.assertIn('Described, not depicted', note)
        self.assertIn('not about the anatomy', note)

    def test_memberships_appear_on_the_entity(self):
        """[FR-NAV-005] Multi-system participation travels with the entity."""
        r = dispatch(self.svc, '/v1/entities/UBERON:0000948', {})
        self.assertIn('memberships', r.body)

    def test_unresolvable_entity_is_a_404(self):
        """A genuine caller error, unlike a model limit."""
        r = dispatch(self.svc, '/v1/entities/UBERON:9999999', {})
        self.assertEqual(r.status, 404)
        self.assertEqual(r.body['error']['code'], 'NOT_FOUND')

    def test_relations_flag_untyped_associations(self):
        """[FR-REL-006] Every surface showing one must label it."""
        r = dispatch(self.svc,
                     '/v1/entities/HOX:mechanism:cross-bridge-cycle/relations',
                     {})
        assoc = [x for x in r.body['relations'] if x['untyped_association']]
        self.assertTrue(assoc)
        self.assertTrue(assoc[0]['prose_justification'])

    def test_relations_can_be_filtered_by_type(self):
        """[FR-REL-010]"""
        r = dispatch(self.svc,
                     '/v1/entities/HOX:mechanism:cross-bridge-cycle/relations',
                     {'type': ['consumes']})
        self.assertTrue(r.body['relations'])
        self.assertTrue(all(x['type'] in ('consumes', 'consumed_by')
                            for x in r.body['relations']))

    def test_claims_endpoint_returns_full_provenance(self):
        """[FR-EVID-010]"""
        r = dispatch(self.svc, '/v1/entities/UBERON:0000948/claims', {})
        self.assertTrue(r.body['claims'])
        first = r.body['claims'][0]
        for key in ('evidence_class', 'species', 'population', 'limitations',
                    'presentation_constraint'):
            self.assertIn(key, first)

    def test_unknowns_endpoint_answers_what_is_not_known(self):
        """[FR-EVID-005] [FR-SRCH-004]"""
        r = dispatch(self.svc, '/v1/entities/UBERON:0002349/unknowns', {})
        self.assertEqual(r.status, 200)
        self.assertTrue(r.body['unknown_claims'])


class TestStatusCodePosture(unittest.TestCase):
    """The product's honesty, made machine-readable."""

    @classmethod
    def setUpClass(cls):
        cls.svc = _svc()

    def test_not_represented_is_200_not_404(self):
        """[FR-SCAL-003] The model has an answer; 404 would deny that."""
        r = dispatch(self.svc,
                     '/v1/entities/HOX:mechanism:cross-bridge-cycle/descend',
                     {})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body['code'], 'NOT_REPRESENTED')
        self.assertIn('statement about the model', r.body['statement'])

    def test_descend_returns_children_with_their_transition(self):
        """[FR-NAV-002] The crossing is announced with the payload."""
        r = dispatch(self.svc, '/v1/entities/UBERON:0000948/descend', {})
        self.assertEqual(r.status, 200)
        child = r.body['children'][0]
        self.assertIsNotNone(child['transition'])
        self.assertTrue(child['transition']['resolution_limit'])

    def test_refused_generation_is_200_with_a_reason(self):
        """[FR-RETR-001] A refusal is a valid answer, not a caller error."""
        r = dispatch(self.svc, '/v1/ask', {},
                     {'question': 'What does the heart do?',
                      'assertions': [{'text': 'It has four chambers.',
                                      'claims': []}]})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body['status'], 'refused')
        self.assertIn('no claim id', r.body['reason'])

    def test_grounded_generation_carries_per_assertion_classes(self):
        """[FR-RETR-002]"""
        r = dispatch(self.svc, '/v1/ask', {},
                     {'question': 'What does the heart do?',
                      'assertions': [{'text': 'It propels blood.',
                                      'claims': ['CLM:heart-function-pump']}]})
        self.assertEqual(r.body['status'], 'grounded')
        self.assertEqual(r.body['assertions'][0]['evidence_classes'], ['EVC-4'])

    def test_clinical_question_is_declined_at_200(self):
        """[FR-RETR-005] Declining is an answer, not an error."""
        r = dispatch(self.svc, '/v1/ask', {},
                     {'question': 'Do I have a heart attack?',
                      'assertions': []})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body['status'], 'declined')

    def test_non_executable_process_run_is_409_with_unmet_conditions(self):
        """[FR-SIM-001] A caller error about state, listing what is missing."""
        r = dispatch(self.svc, '/v1/processes/BPR-01/runs', {})
        self.assertEqual(r.status, 409)
        self.assertEqual(r.body['error']['code'], 'PROCESS_NOT_EXECUTABLE')
        self.assertTrue(r.body['error']['detail']['unmet'])

    def test_malformed_query_is_422_not_a_partial_result(self):
        """[FR-SRCH-005]"""
        r = dispatch(self.svc, '/v1/search',
                     {'q': ['class Organelle'], 'mode': ['structured']})
        self.assertEqual(r.status, 422)
        self.assertEqual(r.body['error']['code'], 'QUERY_SYNTAX')


class TestScaleEndpoints(unittest.TestCase):
    """[FR-SCAL-001] [FR-SCAL-009] [FR-SCAL-010]"""

    @classmethod
    def setUpClass(cls):
        cls.svc = _svc()

    def test_levels_endpoint_exposes_all_eleven_contracts(self):
        r = dispatch(self.svc, '/v1/levels', {})
        self.assertEqual(r.body['count'], 11)
        for row in r.body['levels']:
            self.assertTrue(row['resolution_limit'])

    def test_single_level_carries_the_full_contract(self):
        r = dispatch(self.svc, '/v1/levels/7', {})
        for key in ('data_model', 'spatial_model', 'functional_model',
                    'evidence_model', 'uncertainty_model',
                    'computational_cost', 'resolution_limit'):
            self.assertTrue(r.body[key], key)

    def test_coverage_reports_unmet_declarations(self):
        """[FR-SCAL-010] The unmet promise is the point of the view."""
        r = dispatch(self.svc, '/v1/coverage', {})
        self.assertGreater(r.body['unmet_declarations'], 0)

    def test_coverage_for_one_subsystem(self):
        r = dispatch(self.svc, '/v1/coverage', {'subsystem': ['cardiovascular']})
        self.assertEqual(r.body['declared_depth'], 10)
        self.assertEqual(len(r.body['levels']), 11)

    def test_unknown_subsystem_is_404(self):
        r = dispatch(self.svc, '/v1/coverage', {'subsystem': ['telepathy']})
        self.assertEqual(r.status, 404)

    def test_cross_scale_path_reports_contiguity_as_a_separate_fact(self):
        """[FR-SCAL-009] Reaching the destination and covering every level are
        two different claims, and the endpoint answers both."""
        r = dispatch(self.svc, '/v1/path',
                     {'from': ['UBERON:0000468'], 'to': ['GO:0030017']})
        self.assertTrue(r.body['path_found'])
        self.assertTrue(r.body['level_contiguous'])
        self.assertTrue(r.body['complete'])
        self.assertEqual([], r.body['missing_levels'])
        self.assertEqual(r.body['steps'][0]['level'], 0)

    def test_a_path_that_is_not_containment_reports_no_path(self):
        """[FR-SCAL-009] Two molecules in one reaction are not nested."""
        r = dispatch(self.svc, '/v1/path',
                     {'from': ['CHEBI:15422'], 'to': ['CHEBI:29108']})
        self.assertFalse(r.body['complete'])
        self.assertIn('No containment path', r.body['statement'])

    def test_path_without_parameters_is_422(self):
        r = dispatch(self.svc, '/v1/path', {})
        self.assertEqual(r.status, 422)


class TestProcessEndpoints(unittest.TestCase):
    """[FR-PHYS-001] [FR-PHYS-002]"""

    @classmethod
    def setUpClass(cls):
        cls.svc = _svc()

    def test_process_register_always_carries_representation_status(self):
        """[FR-PHYS-001] A named process must not render like a modelled one."""
        r = dispatch(self.svc, '/v1/processes', {})
        self.assertTrue(r.body['processes'])
        for p in r.body['processes']:
            self.assertIn(p['representation_status'],
                          ('narrative', 'structured', 'parameterized',
                           'executable'))

    def test_structured_process_carries_its_full_specification(self):
        """[FR-PHYS-002] No blank mandatory fields at structured or above."""
        r = dispatch(self.svc, '/v1/processes/BPR-01', {})
        for key in ('inputs', 'outputs', 'state_variables', 'mechanism',
                    'failure_states', 'limitations'):
            self.assertTrue(r.body[key], key)

    def test_every_state_variable_has_a_unit_and_a_class(self):
        """[FR-PHYS-006] A strong mechanism can contain weak numbers."""
        r = dispatch(self.svc, '/v1/processes/BPR-01', {})
        for sv in r.body['state_variables']:
            self.assertTrue(sv['unit'], sv['name'])
            self.assertTrue(sv['evidence_class'], sv['name'])

    def test_every_feedback_loop_names_its_damping(self):
        """[FR-PHYS-007] A loop with no damping is a diagram."""
        r = dispatch(self.svc, '/v1/processes/BPR-01', {})
        for loop in r.body['feedback_loops']:
            self.assertTrue(loop['damping'])


class TestSearchEndpoint(unittest.TestCase):
    """[FR-SRCH-001] [FR-SRCH-002] [FR-SRCH-004]"""

    @classmethod
    def setUpClass(cls):
        cls.svc = _svc()

    def test_search_defaults_to_name_mode(self):
        r = dispatch(self.svc, '/v1/search', {'q': ['Heart']})
        self.assertEqual(r.body['mode'], 'name')
        self.assertTrue(r.body['results'])

    def test_results_carry_status_and_class(self):
        r = dispatch(self.svc, '/v1/search',
                     {'q': ['propels blood'], 'mode': ['function']})
        first = r.body['results'][0]
        self.assertIn('compilation_status', first)
        self.assertIn('evidence_class', first)

    def test_negative_mode_is_reachable_over_http(self):
        r = dispatch(self.svc, '/v1/search',
                     {'q': ['UBERON:0002349'], 'mode': ['negative']})
        self.assertTrue(r.body['statement'])

    def test_filter_reports_what_it_excluded(self):
        r = dispatch(self.svc, '/v1/search',
                     {'q': ['class=CellType'], 'mode': ['structured'],
                      'class': ['EVC-2']})
        self.assertGreater(r.body['excluded_by_filter'], 0)


class TestRouting(unittest.TestCase):
    def test_unknown_route_is_404(self):
        r = dispatch(_svc(), '/v1/nonsense', {})
        self.assertEqual(r.status, 404)

    def test_release_endpoint_reports_computed_metrics(self):
        """[NFR-022] KPIs are computed from recorded data, never asserted."""
        r = dispatch(_svc(), '/v1/release', {})
        self.assertEqual(r.body['release'], RELEASE)
        self.assertIn('completeness', r.body)
        self.assertIn('coverage', r.body)


if __name__ == '__main__':
    unittest.main()
