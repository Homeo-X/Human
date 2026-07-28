"""Navigation and projection — the semantic/physical zoom distinction, tested.

The central claim under test is that changing magnification and changing
ontological resolution are different operations that cannot be confused. A test
suite for that has to attack the confusion directly: magnify hard and assert the
level did not move; change level and assert the camera did not.
"""
import unittest

from homeo.api import Service, dispatch
from homeo.evidence import EvidenceService
from homeo.graph import Graph
from homeo.navigation import (AddressError, Layers, NavigationService,
                              NavigationSession, ViewState, encode)
from homeo.projection import (DEPICTED, DESCRIBED, UNAVAILABLE, UNPLACED,
                              ProjectionService)
from homeo.scale import ScaleService, TerminalAnswer
from homeo.substrate import load

SUBSTRATE = 'ontology'
HEART = 'UBERON:0000948'
LV = 'UBERON:0002084'
SARCOMERE = 'GO:0030017'


def _services(release='rel-test'):
    graph = Graph(load(SUBSTRATE))
    scale = ScaleService(graph)
    evidence = EvidenceService(graph, scale)
    return (graph,
            NavigationService(graph, scale, evidence, release=release),
            ProjectionService(graph, scale, evidence))


class TestZoomIsTwoOperations(unittest.TestCase):
    """[FR-NAV-001] — semantic zoom and physical zoom are distinct."""

    def setUp(self):
        _, self.nav, _ = _services()
        self.state = self.nav.enter('heart')

    def test_magnifying_never_changes_the_level(self):
        state = self.state
        for _ in range(6):
            state = self.nav.magnify(state, 2).state
        self.assertEqual(self.state.level, state.level,
                         'magnification changed the ontological resolution')

    def test_magnifying_reports_that_no_claim_changed(self):
        result = self.nav.magnify(self.state, 4)
        self.assertFalse(result.semantic_change)
        self.assertTrue(result.claim_unchanged)
        self.assertIsNone(result.transition)

    def test_changing_level_never_changes_magnification(self):
        magnified = self.nav.magnify(self.state, 8).state
        after = self.nav.set_level(magnified, 5).state
        self.assertEqual(magnified.magnification, after.magnification)
        self.assertEqual(5, after.level)

    def test_changing_level_is_announced_with_mode_and_limit(self):
        result = self.nav.set_level(self.state, 7)
        self.assertTrue(result.semantic_change)
        self.assertFalse(result.claim_unchanged)
        self.assertIsNotNone(result.transition)
        announced = result.transition.as_dict()
        self.assertEqual(7, announced['to_level'])
        self.assertTrue(announced['resolution_limit'])
        self.assertTrue(announced['representation_mode'])

    def test_magnification_stops_at_the_asset_resolution_limit(self):
        """Past the limit a renderer shows polygons, not anatomy."""
        result = self.nav.magnify(self.state, 1000)
        self.assertTrue(result.at_limit)
        self.assertEqual(self.nav.magnification_limit,
                         result.state.magnification)
        self.assertIn('not anatomy', result.note)

    def test_a_level_that_is_already_current_is_not_a_semantic_change(self):
        result = self.nav.set_level(self.state, self.state.level)
        self.assertFalse(result.semantic_change)

    def test_the_two_operations_are_separate_methods(self):
        """A surface binding a scroll wheel cannot reach the level setter."""
        import inspect
        params = inspect.signature(self.nav.magnify).parameters
        self.assertNotIn('level', params)
        self.assertNotIn('factor', inspect.signature(self.nav.set_level).parameters)

    def test_negative_magnification_is_rejected(self):
        with self.assertRaises(ValueError):
            self.nav.magnify(self.state, 0)


class TestAddressing(unittest.TestCase):
    """[FR-NAV-006] — navigation state is addressable and restorable."""

    def setUp(self):
        _, self.nav, _ = _services()

    def test_a_state_round_trips_through_its_address(self):
        state = self.nav.with_layers(
            self.nav.magnify(self.nav.enter(LV), 2).state,
            evidence_classes={'EVC-2', 'EVC-3'}, systems={'cardiovascular'})
        state = self.nav.isolate(state, LV)
        restored = self.nav.restore(encode(state)).state
        self.assertEqual(state.entity, restored.entity)
        self.assertEqual(state.level, restored.level)
        self.assertEqual(state.magnification, restored.magnification)
        self.assertEqual(state.layers, restored.layers)
        self.assertEqual(state.isolated, restored.isolated)

    def test_encoding_is_deterministic(self):
        state = self.nav.enter(HEART)
        self.assertEqual(encode(state), encode(state))

    def test_an_address_is_readable_by_a_human(self):
        """An educator sharing a link should see where it points."""
        address = encode(self.nav.enter(LV))
        self.assertIn('l=4', address)
        self.assertIn('UBERON', address)

    def test_a_malformed_address_is_an_error_not_a_guess(self):
        for bad in ('', 'garbage', 'homeo:', 'homeo:e=X', 'homeo:l=3',
                    'homeo:e=X&l=notanumber'):
            with self.assertRaises(AddressError, msg=bad):
                self.nav.restore(bad)

    def test_an_address_to_an_unknown_entity_is_an_error(self):
        with self.assertRaises(AddressError):
            self.nav.restore('homeo:v=1&e=UBERON%3A9999999&l=3')

    def test_an_address_from_another_release_offers_but_does_not_switch(self):
        """Concurrency case: a new release is offered, never applied."""
        state = ViewState(entity=HEART, level=3, release='rel-2020-01-01')
        restoration = self.nav.restore(encode(state))
        self.assertTrue(restoration.restored)
        self.assertEqual('rel-test', restoration.state.release)
        self.assertEqual('rel-test', restoration.release_offered)
        self.assertTrue(any('never applied mid-session' in n
                            for n in restoration.notes))

    def test_a_retired_entity_resolves_to_its_successor_with_the_tombstone(self):
        """[FR-ONTO-004] An address outliving a rename still answers."""
        graph = Graph(load(SUBSTRATE))
        entity = graph.get(HEART)
        from dataclasses import replace as dc_replace
        graph.substrate.entities.append(dc_replace(
            entity, id='HOX:anatomy:cardiac-organ-old',
            successor_id=HEART, retired_at='2026-01-01', minted=True))
        graph = Graph(graph.substrate)
        scale = ScaleService(graph)
        nav = NavigationService(graph, scale,
                                EvidenceService(graph, scale),
                                release='rel-test')
        restoration = nav.restore(
            'homeo:v=1&e=HOX%3Aanatomy%3Acardiac-organ-old&l=3')
        self.assertTrue(restoration.restored)
        self.assertTrue(restoration.entity_moved)
        self.assertEqual(HEART, restoration.state.entity)
        self.assertEqual(HEART, restoration.tombstone['successor'])


class TestSession(unittest.TestCase):
    """[FR-NAV-006] [FR-NAV-011] — history, back, and the teaching path."""

    def setUp(self):
        _, self.nav, _ = _services()
        self.session = NavigationSession(self.nav)
        for ref in (HEART, LV, 'UBERON:0002349'):
            self.session.go(self.nav.enter(ref))

    def test_back_restores_the_previous_state_exactly(self):
        self.assertEqual(LV, self.session.back().entity)
        self.assertEqual(HEART, self.session.back().entity)

    def test_back_at_the_start_stays_put_rather_than_failing(self):
        self.session.back()
        self.session.back()
        self.assertEqual(HEART, self.session.back().entity)
        self.assertEqual(HEART, self.session.current.entity)

    def test_an_exported_path_replays_step_for_step(self):
        path = self.session.export_path('cardiac descent')
        self.assertEqual(3, len(path['steps']))
        replayed = self.session.replay(path)
        self.assertTrue(all(r.restored for r in replayed))
        self.assertEqual([HEART, LV, 'UBERON:0002349'],
                         [r.state.entity for r in replayed])

    def test_an_exported_path_warns_that_replay_is_release_dependent(self):
        self.assertIn('different release',
                      self.session.export_path()['note'])


class TestLayers(unittest.TestCase):
    """[FR-NAV-007] — filtering reports what it hid."""

    def setUp(self):
        _, self.nav, self.proj = _services()
        self.state = self.nav.enter(HEART)

    def test_filtering_by_evidence_class_counts_what_it_hid(self):
        filtered = self.nav.with_layers(self.state, evidence_classes={'EVC-1'})
        projection = self.proj.project(filtered)
        self.assertGreater(projection.hidden.count, 0)
        self.assertIn('evidence_class', projection.hidden.by_filter)

    def test_an_unfiltered_view_hides_nothing(self):
        projection = self.proj.project(self.state)
        self.assertEqual(0, projection.hidden.count)
        self.assertEqual({}, projection.hidden.by_filter)

    def test_filters_are_attributed_to_the_filter_that_applied_them(self):
        filtered = self.nav.with_layers(self.state, systems={'nervous'})
        projection = self.proj.project(filtered)
        self.assertEqual({'system': projection.hidden.count},
                         projection.hidden.by_filter)

    def test_setting_one_filter_leaves_the_others_alone(self):
        state = self.nav.with_layers(self.state, systems={'cardiovascular'})
        state = self.nav.with_layers(state, evidence_classes={'EVC-2'})
        self.assertEqual(frozenset({'cardiovascular'}), state.layers.systems)
        self.assertEqual(frozenset({'EVC-2'}), state.layers.evidence_classes)


class TestIsolationAndSectioning(unittest.TestCase):
    """[FR-NAV-008] — both operate on entities, not on meshes."""

    def setUp(self):
        self.graph, self.nav, self.proj = _services()

    def test_isolating_an_entity_includes_everything_contained_in_it(self):
        state = self.nav.isolate(self.nav.enter(HEART), LV)
        self.assertIn(LV, state.isolated)
        self.assertIn('UBERON:0002349', state.isolated)   # myocardium, inside LV
        self.assertIn(SARCOMERE, state.isolated)          # eight levels down

    def test_isolation_does_not_depend_on_geometry_being_present(self):
        """None of the isolated entities have meshes; isolation still holds."""
        state = self.nav.isolate(self.nav.enter(HEART), LV)
        depicted = [self.graph.spatial_identity(e) for e in state.isolated]
        self.assertFalse(any(si and si.has_geometry for si in depicted))
        self.assertGreater(len(state.isolated), 1)

    def test_the_focus_is_still_reported_when_isolation_excludes_it(self):
        state = self.nav.isolate(self.nav.enter(HEART), LV)
        projection = self.proj.project(state)
        self.assertEqual(HEART, projection.focus.entity)
        self.assertNotIn(HEART, [e.entity for e in projection.entities])

    def test_sectioning_does_not_claim_a_crossing_it_cannot_compute(self):
        """Crossing needs geometry, and no entity here has any.

        This is the defect a review caught: the method returned the same list
        under the key `crosses` for any plane, including a nonsense one, which
        asserted an intersection that had never been computed.
        """
        result = self.nav.section(self.nav.enter(HEART), 'transverse T8')
        self.assertFalse(result['crossing_computed'])
        self.assertNotIn('crosses', result)
        self.assertTrue(result['candidates'])
        self.assertTrue(all(c['crossing'] == 'not_computable'
                            for c in result['candidates']))
        self.assertIn('cannot be determined', result['statement'])

    def test_the_cut_plane_is_still_recorded_on_the_state(self):
        result = self.nav.section(self.nav.enter(HEART), 'sagittal midline')
        self.assertEqual('sagittal midline', result['state']['section'])


class TestGraphNavigation(unittest.TestCase):
    """[FR-NAV-009] — typed traversal alongside the tree."""

    def setUp(self):
        _, self.nav, _ = _services()

    def test_following_a_relation_carries_its_type(self):
        result = self.nav.follow(self.nav.enter(HEART), 'part_of')
        self.assertEqual(1, result['count'])
        self.assertEqual('part_of', result['targets'][0]['relation'])
        self.assertFalse(result['targets'][0]['untyped'])

    def test_an_untyped_association_is_traversable_and_labelled(self):
        graph, nav, _ = _services()
        untyped = [r for r in graph.substrate.relationships
                   if r.is_untyped_association]
        self.assertTrue(untyped, 'fixture requires an untyped association')
        result = nav.follow(nav.enter(untyped[0].source), 'associated_with')
        self.assertTrue(result['targets'])
        self.assertTrue(result['targets'][0]['untyped'])
        self.assertIn('not a mechanism', result['targets'][0]['note'])


class TestContext(unittest.TestCase):
    """[FR-NAV-010] — the lineage stays visible, each ancestor one action away."""

    def setUp(self):
        _, self.nav, _ = _services()

    def test_context_gives_the_full_chain_from_the_top(self):
        context = self.nav.context(self.nav.enter(SARCOMERE))
        levels = [row['level'] for row in context['lineage']]
        self.assertEqual([0, 1, 3, 4, 5, 6, 7, 8], levels)

    def test_every_ancestor_carries_a_directly_usable_address(self):
        context = self.nav.context(self.nav.enter(SARCOMERE))
        for row in context['lineage']:
            restored = self.nav.restore(row['address'])
            self.assertTrue(restored.restored)
            self.assertEqual(row['entity'], restored.state.entity)


class TestTerminalDescent(unittest.TestCase):
    """[FR-NAV-003] — descending past declared depth is a view, not an error."""

    def setUp(self):
        _, self.nav, _ = _services()

    def test_descent_past_declared_depth_returns_the_terminal_answer(self):
        result = self.nav.descend(
            self.nav.enter('HOX:mechanism:cross-bridge-cycle'))
        self.assertIsInstance(result, TerminalAnswer)

    def test_descent_with_children_returns_view_states(self):
        result = self.nav.descend(self.nav.enter(HEART))
        self.assertIsInstance(result, list)
        self.assertEqual([LV], [s.entity for s in result])


class TestProjection(unittest.TestCase):
    """[FR-SPAT-002] [FR-SPAT-006] — the view is derived from the graph."""

    def setUp(self):
        self.graph, self.nav, self.proj = _services()

    def test_an_entity_without_geometry_is_projected_not_omitted(self):
        """The inversion: geometry is an attribute, not the condition of
        existing.

        Asserted on the sarcomere rather than the heart since D-031 bound a
        mesh to the heart. The claim under test is unchanged; the example had
        to move because the substrate finally has a counter-example.
        """
        projection = self.proj.project(self.nav.enter('GO:0030017'))
        focus = projection.focus
        self.assertEqual(DESCRIBED, focus.depiction)
        self.assertTrue(focus.position, 'a described entity still has a place')
        self.assertIn('not depicted', focus.note)

    def test_an_entity_with_no_spatial_identity_is_still_in_view(self):
        projection = self.proj.project(self.nav.enter('CL:0000746'))
        self.assertEqual(UNPLACED, projection.focus.depiction)
        self.assertIn('still a real entity', projection.focus.note)

    def test_a_declared_but_unresolvable_asset_is_not_the_same_as_absence(self):
        """A pipeline failure must not read as thin anatomy."""
        from dataclasses import replace as dc_replace
        substrate = self.graph.substrate
        substrate.spatial_identities = [
            dc_replace(si, geometry=({'lod': 0, 'asset': None},))
            if si.entity == HEART else si
            for si in substrate.spatial_identities]
        graph = Graph(substrate)
        scale = ScaleService(graph)
        proj = ProjectionService(graph, scale, EvidenceService(graph, scale))
        nav = NavigationService(graph, scale)
        projection = proj.project(nav.enter(HEART))
        self.assertEqual(UNAVAILABLE, projection.focus.depiction)
        self.assertIn('pipeline failure', projection.focus.note)

    def test_relations_among_entities_in_view_are_included(self):
        projection = self.proj.project(self.nav.enter(HEART))
        in_view = {e.entity for e in projection.entities}
        for relation in projection.relations:
            self.assertIn(relation['source'], in_view)
            self.assertIn(relation['target'], in_view)

    def test_an_untyped_edge_is_marked_do_not_render_as_a_mechanism(self):
        graph, nav, proj = _services()
        untyped = next(r for r in graph.substrate.relationships
                       if r.is_untyped_association)
        state = nav.enter(untyped.source)
        projection = proj.project(state)
        rows = [r for r in projection.relations if r['untyped']]
        for row in rows:
            self.assertIn('not what kind', row['note'])

    def test_every_projected_entity_carries_its_evidence_and_status(self):
        projection = self.proj.project(self.nav.enter(HEART))
        for entity in projection.entities:
            self.assertTrue(entity.compilation_status)
            self.assertTrue(entity.address)

    def test_the_weakest_evidence_class_is_reported_never_an_average(self):
        """[CH-06] Averaging a measured claim with an inferred one describes
        neither, and reporting the strongest would flatter the entity.

        The cardiomyocyte carries both an EVC-3 claim and an EVC-8 (UNKNOWN)
        one. A surface colouring it by evidence must colour it by the weakest.
        """
        projection = self.proj.project(self.nav.enter('CL:0000746'))
        focus = projection.focus
        self.assertEqual(('EVC-3', 'EVC-8'), focus.evidence_classes)
        self.assertEqual('EVC-8', focus.weakest_class)

    def test_a_missing_focus_states_it_is_about_the_release(self):
        projection = self.proj.project(ViewState(entity='UBERON:9999999',
                                                 level=3))
        self.assertIsNone(projection.focus)
        self.assertIn('not about the anatomy', projection.notes[0])

    def test_a_large_level_is_paged_with_the_total_stated(self):
        projection = self.proj.project(self.nav.enter(HEART), page_size=1)
        self.assertTrue(projection.truncated)
        self.assertEqual(1, len(projection.entities))
        self.assertGreater(projection.total_before_paging, 1)
        self.assertTrue(any('not a view, it is a dump' in n
                            for n in projection.notes))

    def test_the_projection_says_it_came_from_the_graph(self):
        payload = self.proj.project(self.nav.enter(HEART)).as_dict()
        self.assertIn('computed from the knowledge graph',
                      payload['derivation'])


class TestNavigationEndpoints(unittest.TestCase):
    """[FR-NAV-001] [FR-NAV-006] — over the API surface."""

    @classmethod
    def setUpClass(cls):
        cls.svc = Service(SUBSTRATE, release='rel-test')

    def test_the_api_refuses_an_unqualified_zoom(self):
        """A client cannot say "zoom" without saying which kind."""
        r = dispatch(self.svc, '/v1/zoom/heart', {'amount': ['2']})
        self.assertEqual(422, r.status)
        self.assertIn('different operations', r.body['error']['message'])

    def test_physical_and_semantic_zoom_are_different_endpoints_results(self):
        physical = dispatch(self.svc, '/v1/zoom/heart',
                            {'kind': ['physical'], 'amount': ['4']})
        semantic = dispatch(self.svc, '/v1/zoom/heart',
                            {'kind': ['semantic'], 'amount': ['5']})
        self.assertFalse(physical.body['semantic_change'])
        self.assertTrue(semantic.body['semantic_change'])
        self.assertEqual(physical.body['state']['level'], 3)
        self.assertEqual(semantic.body['state']['level'], 5)

    def test_a_view_carries_its_own_address(self):
        r = dispatch(self.svc, '/v1/view/heart', {})
        self.assertEqual(200, r.status)
        restored = dispatch(self.svc, '/v1/restore',
                            {'address': [r.body['address']]})
        self.assertTrue(restored.body['restored'])

    def test_restore_without_an_address_is_a_caller_error(self):
        r = dispatch(self.svc, '/v1/restore', {})
        self.assertEqual(422, r.status)

    def test_a_view_of_a_missing_entity_is_404(self):
        r = dispatch(self.svc, '/v1/view/UBERON%3A9999999', {})
        self.assertEqual(404, r.status)

    def test_view_filters_report_the_hidden_count(self):
        r = dispatch(self.svc, '/v1/view/heart', {'evidence': ['EVC-1']})
        self.assertGreater(r.body['hidden']['count'], 0)

    def test_every_view_carries_the_non_diagnostic_boundary(self):
        r = dispatch(self.svc, '/v1/view/heart', {})
        self.assertIn('Not a medical device', r.body['boundary'])


if __name__ == '__main__':
    unittest.main()


class TestReviewFindings(unittest.TestCase):
    """Regression tests for defects a review of this module found.

    Each of these passed silently before, which is the point of writing them
    down: the implementations were plausible and wrong, and only a test that
    varies the input the code ignored can tell the difference.
    """

    def setUp(self):
        _, self.nav, self.proj = _services()

    # --- the projection ignored the level it claimed to honour ---

    def test_the_projection_honours_the_requested_level(self):
        heart = self.nav.enter(HEART)                       # L3
        at_l7 = self.nav.set_level(heart, 7).state
        shallow = {e.entity for e in self.proj.project(heart).entities}
        deep = {e.entity for e in self.proj.project(at_l7).entities}
        self.assertNotEqual(shallow, deep,
                            'the level was ignored: two resolutions produced '
                            'the same view')
        self.assertIn('CL:0000746', deep)                   # cardiomyocyte, L7
        self.assertNotIn('CL:0000746', shallow)

    def test_deeper_views_retain_the_focus_for_orientation(self):
        at_l7 = self.nav.set_level(self.nav.enter(HEART), 7).state
        projection = self.proj.project(at_l7)
        self.assertIn(HEART, [e.entity for e in projection.entities])
        self.assertTrue(any('retained for orientation' in n
                            for n in projection.notes))

    def test_a_level_with_no_content_says_so_rather_than_showing_the_wrong_set(self):
        at_l10 = self.nav.set_level(self.nav.enter(HEART), 10).state
        projection = self.proj.project(at_l10)
        self.assertEqual([HEART], [e.entity for e in projection.entities])
        self.assertTrue(any('Nothing is represented at L10' in n
                            for n in projection.notes))

    def test_ascending_reaches_the_ancestor_at_that_level(self):
        at_l1 = self.nav.set_level(self.nav.enter(SARCOMERE), 1).state
        projection = self.proj.project(at_l1)
        self.assertEqual('UBERON:0000915', projection.entities[0].entity)
        self.assertTrue(any('Ascended to L1' in n for n in projection.notes))

    # --- the magnification limit was bypassable by editing a link ---

    def test_an_address_cannot_raise_the_magnification_limit(self):
        restoration = self.nav.restore(
            f'homeo:v=1&rel=rel-test&e=UBERON%3A0000948&l=3&m=100000')
        self.assertEqual(self.nav.magnification_limit,
                         restoration.state.magnification)
        self.assertTrue(any('does not raise it' in n
                            for n in restoration.notes))

    def test_a_magnification_within_the_limit_survives_unchanged(self):
        restoration = self.nav.restore(
            'homeo:v=1&rel=rel-test&e=UBERON%3A0000948&l=3&m=4')
        self.assertEqual(4.0, restoration.state.magnification)
        self.assertEqual((), restoration.notes)

    def test_a_nonsense_magnification_is_a_malformed_address(self):
        for bad in ('m=abc', 'm=-3', 'm=0'):
            with self.assertRaises(AddressError, msg=bad):
                self.nav.restore(
                    f'homeo:v=1&e=UBERON%3A0000948&l=3&{bad}')

    # --- levels outside the scale contract were accepted ---

    def test_a_level_outside_the_scale_contract_is_refused(self):
        for level in (11, 99, -1):
            with self.assertRaises(AddressError, msg=str(level)):
                self.nav.restore(f'homeo:v=1&e=UBERON%3A0000948&l={level}')

    def test_both_ends_of_the_contract_are_valid(self):
        for level in (0, 10):
            self.assertTrue(self.nav.restore(
                f'homeo:v=1&e=UBERON%3A0000948&l={level}').restored)

    # --- layer values were not escaped, so a comma split a filter ---

    def test_a_layer_value_containing_a_comma_survives_the_round_trip(self):
        state = ViewState(entity=HEART, level=3, release='rel-test',
                          layers=Layers(systems=frozenset({'a,b'})))
        restored = self.nav.restore(encode(state)).state
        self.assertEqual(frozenset({'a,b'}), restored.layers.systems,
                         'the comma split one filter into two, hiding more '
                         'content than the user asked to hide')

    def test_an_isolated_id_containing_a_comma_survives(self):
        state = ViewState(entity=HEART, level=3, release='rel-test',
                          isolated=('HOX:x,y',))
        self.assertEqual(('HOX:x,y',),
                         self.nav.restore(encode(state)).state.isolated)
