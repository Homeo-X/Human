"""The pancreas test — the project's founding claim, against real content.

"Biology is a graph, not a tree; the pancreas belongs to both the digestive and
the endocrine system." The architecture answered that from the beginning:
containment and membership are separate relations, and the navigation tree is
derived rather than stored.

It had never been tested. Until `tools/curate_pancreas.py` the substrate held
**zero entities with more than one membership** and exactly one `member_of`
edge, so every test of the claim ran over a structure containing no instance of
the thing being tested. When one was added, three of six probes failed
immediately (D-019):

- the derived tree reached no organ from any system, because a system contains
  nothing and the tree was built from containment alone — a direct failure of
  FR-NAV-005's own acceptance criterion;
- coverage counted the pancreas once, under the subsystem its single-valued
  `subsystem` field named, so the endocrine system reported zero organs while
  containing one;
- search by subsystem found it under `digestive` only.

Each probe is frozen here. They are written against the real substrate on
purpose: a fixture would have passed all six from the start, which is exactly
how the gap survived.
"""
import unittest

from homeo.evidence import EvidenceService
from homeo.graph import Graph
from homeo.navigation import NavigationService
from homeo.projection import ProjectionService
from homeo.scale import ScaleService
from homeo.search import SearchService
from homeo.substrate import load

SUBSTRATE = 'ontology'
PANCREAS = 'UBERON:0001264'
DIGESTIVE = 'HOX:function:digestive'
ENDOCRINE = 'HOX:function:endocrine'
ISLET = 'UBERON:0000006'
BETA_CELL = 'CL:0000169'
INSULIN = 'CHEBI:145810'
ACINUS = 'UBERON:0001263'


def _services():
    graph = Graph(load(SUBSTRATE))
    scale = ScaleService(graph)
    evidence = EvidenceService(graph, scale)
    return (graph, scale, evidence,
            NavigationService(graph, scale, evidence),
            ProjectionService(graph, scale, evidence),
            SearchService(graph, evidence, scale))


class TestTheSubstrateContainsTheCase(unittest.TestCase):
    """Before anything else: the thing being tested must exist."""

    @classmethod
    def setUpClass(cls):
        cls.graph = _services()[0]

    def test_the_substrate_holds_a_multi_membership_organ(self):
        multi = [e.id for e in self.graph.entities()
                 if len(self.graph.memberships(e.id)) > 1]
        self.assertIn(PANCREAS, multi,
                      'the pancreas test needs a pancreas; without one every '
                      'assertion below passes vacuously')

    def test_both_memberships_are_recorded_without_primacy(self):
        """[FR-NAV-005] A list, never a primary plus others."""
        self.assertEqual([DIGESTIVE, ENDOCRINE],
                         self.graph.memberships(PANCREAS))

    def test_both_lineages_are_modelled_deeply_enough_to_diverge(self):
        """One shared organ, two branches that do not meet again."""
        for eid in (ACINUS, ISLET, BETA_CELL, INSULIN):
            self.assertIsNotNone(self.graph.get(eid), eid)
        self.assertIn(PANCREAS, self.graph.lineage(BETA_CELL))
        self.assertIn(PANCREAS, self.graph.lineage(ACINUS))


class TestProbe1DerivedTree(unittest.TestCase):
    """[FR-NAV-005] Reachable from every system it belongs to."""

    @classmethod
    def setUpClass(cls):
        cls.graph = _services()[0]

    def test_the_pancreas_is_reachable_from_the_digestive_system(self):
        children = [c.entity_id
                    for c in self.graph.navigation_tree(DIGESTIVE).children]
        self.assertIn(PANCREAS, children)

    def test_the_pancreas_is_reachable_from_the_endocrine_system(self):
        children = [c.entity_id
                    for c in self.graph.navigation_tree(ENDOCRINE).children]
        self.assertIn(PANCREAS, children)

    def test_the_tree_says_which_edge_it_followed(self):
        """Containment and membership are both navigable and not the same."""
        system = self.graph.navigation_tree(DIGESTIVE)
        self.assertEqual('member', system.child_kinds[PANCREAS])
        abdomen = self.graph.navigation_tree('UBERON:0000916')
        self.assertEqual('contains', abdomen.child_kinds[PANCREAS])

    def test_a_node_still_advertises_its_other_memberships(self):
        node = next(c for c in self.graph.navigation_tree(DIGESTIVE).children
                    if c.entity_id == PANCREAS)
        self.assertIn(ENDOCRINE, node.other_memberships)

    def test_the_tree_is_still_a_view(self):
        """[D-006] Reaching further must not make it canonical."""
        self.assertTrue(self.graph.navigation_tree(DIGESTIVE).is_view)


class TestProbe2Lineage(unittest.TestCase):
    """[FR-ONTO-002] Containment stays single-parent — no arbitrary choice."""

    @classmethod
    def setUpClass(cls):
        cls.graph = _services()[0]

    def test_lineage_follows_containment_not_membership(self):
        self.assertEqual([PANCREAS, 'UBERON:0000916', 'UBERON:0000468'],
                         self.graph.lineage(PANCREAS))

    def test_no_system_appears_in_a_containment_lineage(self):
        """A system is not a container; a pancreas is not inside digestion."""
        for eid in (PANCREAS, BETA_CELL, ACINUS):
            self.assertNotIn(DIGESTIVE, self.graph.lineage(eid))
            self.assertNotIn(ENDOCRINE, self.graph.lineage(eid))

    def test_each_branch_reaches_the_organism_through_the_pancreas(self):
        for eid in (BETA_CELL, ACINUS):
            lineage = self.graph.lineage(eid)
            self.assertIn(PANCREAS, lineage)
            self.assertEqual('UBERON:0000468', lineage[-1])


class TestProbe3Coverage(unittest.TestCase):
    """[FR-SCAL-010] A system's coverage includes the organs it has."""

    @classmethod
    def setUpClass(cls):
        cls.graph, cls.scale = _services()[0], _services()[1]

    def _l3(self, subsystem):
        row = self.scale.coverage(subsystem)[0]
        return [c.populated for c in row.cells if c.level == 3][0]

    def test_the_pancreas_counts_in_both_systems(self):
        """Counted where it belongs, in both columns.

        Asserted against the pancreas itself rather than a total: the organ
        import filled these levels, and a test pinned to a count would break
        every time content arrives, which is the wrong thing to notice.
        """
        for subsystem in ('digestive', 'endocrine'):
            self.assertIn(PANCREAS, self._organs_in(subsystem), subsystem)
        self.assertGreaterEqual(self._l3('endocrine'), 1,
                                'the endocrine system reported zero organs '
                                'while containing at least one')

    def _organs_in(self, subsystem):
        return [e.id for e in self.graph.entities()
                if e.level == 3 and self.graph.in_subsystem(e.id, subsystem)]

    def test_a_single_membership_organ_counts_once(self):
        """The fix must not smear every entity across every system."""
        respiratory = self._organs_in('respiratory')
        self.assertNotIn(PANCREAS, respiratory,
                         'the pancreas is not a respiratory organ')
        self.assertNotIn('UBERON:0000948', respiratory,
                         'the heart is not a respiratory organ')
        self.assertTrue(respiratory, 'the respiratory system has organs')


class TestProbe4Projection(unittest.TestCase):
    """[FR-NAV-005] The view reaches what the graph says is there."""

    @classmethod
    def setUpClass(cls):
        _, _, _, cls.nav, cls.proj, _ = _services()

    def _at_l3(self, system):
        state = self.nav.set_level(self.nav.enter(system), 3).state
        return [e.entity for e in self.proj.project(state).entities]

    def test_projecting_a_system_at_l3_finds_its_organs(self):
        self.assertIn(PANCREAS, self._at_l3(DIGESTIVE))
        self.assertIn(PANCREAS, self._at_l3(ENDOCRINE))

    def test_projecting_a_system_at_its_own_level_shows_its_members(self):
        """The `level == here` path descends membership too.

        Probe 4 exercised the *deeper* branch only, because a system sits at L2
        and the probe asked for L3. A mutation reverting this branch to
        containment-only therefore survived the first mutation round.
        """
        state = self.nav.enter(DIGESTIVE)               # L2, its own level
        found = [e.entity for e in self.proj.project(state).entities]
        self.assertIn(PANCREAS, found)

    def test_projecting_deeper_reaches_the_right_branch(self):
        state = self.nav.set_level(self.nav.enter(PANCREAS), 7).state
        found = [e.entity for e in self.proj.project(state).entities]
        self.assertIn(BETA_CELL, found)
        self.assertIn('CL:0002064', found)          # acinar cell


class TestProbe5CrossScalePath(unittest.TestCase):
    """[FR-SCAL-009] Participation is not containment, and the path says so."""

    @classmethod
    def setUpClass(cls):
        cls.scale = _services()[1]

    def test_there_is_no_containment_path_to_insulin(self):
        result = self.scale.cross_scale_path('UBERON:0000468', INSULIN)
        self.assertFalse(result['complete'])
        self.assertIn('No containment path', result['statement'])

    def test_the_containment_path_to_the_beta_cell_is_complete(self):
        result = self.scale.cross_scale_path('UBERON:0000468', BETA_CELL)
        self.assertTrue(result['path_found'])
        self.assertIn(PANCREAS, [s['entity'] for s in result['steps']])


class TestProbe6Search(unittest.TestCase):
    """[FR-SRCH-005] Findable from every system it belongs to."""

    @classmethod
    def setUpClass(cls):
        cls.search = _services()[5]

    def _by_system(self, subsystem):
        return [r.entity_id for r in self.search.search(
            f'subsystem={subsystem}', 'structured', limit=99).results]

    def test_the_pancreas_is_found_under_both_systems(self):
        self.assertIn(PANCREAS, self._by_system('digestive'))
        self.assertIn(PANCREAS, self._by_system('endocrine'))

    def test_membership_search_does_not_leak_unrelated_entities(self):
        """A widened filter that matches everything answers nothing."""
        endocrine = self._by_system('endocrine')
        self.assertNotIn('UBERON:0000948', endocrine)      # the heart
        self.assertNotIn('GO:0030017', endocrine)          # a sarcomere


class TestAdmittedProvisionally(unittest.TestCase):
    """[D-017] Nothing here was reviewed, and every record says so."""

    @classmethod
    def setUpClass(cls):
        cls.graph, _, cls.ev, *_ = _services()

    def test_every_pancreatic_entity_is_provisional(self):
        for eid in (PANCREAS, ACINUS, ISLET, BETA_CELL, INSULIN):
            entity = self.graph.get(eid)
            self.assertEqual('provisional', entity.review_state, eid)
            self.assertEqual('agent:anatomy', entity.admitted_by, eid)

    def test_no_pancreatic_claim_names_a_human(self):
        for claim in self.ev.all_claims():
            if claim.subject in (PANCREAS, ACINUS, ISLET, BETA_CELL, INSULIN):
                self.assertFalse(claim.assigned_by.startswith('human:'))

    def test_the_pancreatic_claims_are_definitions_not_findings(self):
        """[D-021] Importing an organ tells you what a word means.

        Nothing here measured anything. The claims say what Gray's and Guyton
        call these structures, which is a terminological assertion graded by
        authority — not evidence about a body.
        """
        for claim in self.ev.all_claims():
            if claim.subject in (PANCREAS, ACINUS, ISLET, BETA_CELL, INSULIN):
                self.assertTrue(claim.is_terminological, claim.id)
                self.assertEqual('TRM-1', claim.evidence_class)
                self.assertTrue(claim.authority)
                self.assertFalse(claim.is_evidence,
                                 'a definition must not be citable as evidence')


if __name__ == '__main__':
    unittest.main()
