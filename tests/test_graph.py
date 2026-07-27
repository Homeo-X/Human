"""Graph, resolution, and the derived navigation view.

Every test names the FR ids it verifies, so `specgraph.py --trace src tests`
reports these requirements as test-verified rather than merely claimed
(AGENTS.md §10).
"""
import unittest

from homeo.graph import EntityRetired, Graph
from homeo.substrate import Entity, Substrate, load

SUBSTRATE = 'ontology'


class TestResolution(unittest.TestCase):
    """[FR-ONTO-001] [FR-ONTO-004] [FR-ONTO-008]"""

    @classmethod
    def setUpClass(cls):
        cls.graph = Graph(load(SUBSTRATE))

    def test_resolves_by_primary_identifier(self):
        """[FR-ONTO-001] External ontology term is the primary identifier."""
        self.assertEqual(self.graph.resolve('UBERON:0000948').preferred_term,
                         'Heart')

    def test_resolves_by_latin_synonym(self):
        """[FR-ONTO-008] Synonyms and their register are searchable."""
        self.assertEqual(self.graph.resolve('cor').id, 'UBERON:0000948')

    def test_resolves_by_clinical_synonym(self):
        """[FR-ONTO-008] Clinical vocabulary reaches the canonical entity."""
        self.assertEqual(self.graph.resolve('cardiomyocyte').id, 'CL:0000746')

    def test_unknown_reference_raises(self):
        """[FR-ONTO-001] An unresolvable reference is an error, not a guess."""
        with self.assertRaises(KeyError):
            self.graph.resolve('UBERON:9999999')

    def test_minted_ids_carry_a_reason(self):
        """[FR-ONTO-001] A minted id without a reason is inadmissible (INV-10)."""
        for e in self.graph.entities():
            if e.minted:
                self.assertTrue(e.minted_reason,
                                f'{e.id} is minted with no reason')

    def test_retired_identifier_yields_successor(self):
        """[FR-ONTO-004] A tombstone answers "this moved", not "this broke"."""
        sub = Substrate(entities=[
            Entity(id='HOX:organ:old', entity_class='Organ',
                   subsystem='cardiovascular', preferred_term='Old',
                   compilation_status='structured', level=3,
                   retired_at='2026-01-01', successor_id='HOX:organ:new'),
            Entity(id='HOX:organ:new', entity_class='Organ',
                   subsystem='cardiovascular', preferred_term='New',
                   compilation_status='structured', level=3)])
        g = Graph(sub)
        with self.assertRaises(EntityRetired) as ctx:
            g.resolve('HOX:organ:old')
        self.assertEqual(ctx.exception.successor, 'HOX:organ:new')
        # follow_retired lets a caller reach the tombstoned record deliberately.
        self.assertEqual(g.resolve('HOX:organ:old', follow_retired=True).id,
                         'HOX:organ:old')


class TestTraversal(unittest.TestCase):
    """[FR-REL-001] [FR-REL-002] [FR-REL-003] [FR-REL-006] [FR-REL-010]"""

    @classmethod
    def setUpClass(cls):
        cls.graph = Graph(load(SUBSTRATE))

    def test_every_edge_is_typed(self):
        """[FR-REL-001] Untyped edges are inadmissible."""
        for r in self.graph.substrate.relationships:
            self.assertTrue(r.type, f'{r.id} has no type')

    def test_inverse_traversal_reaches_the_same_edge(self):
        """[FR-REL-002] An edge is traversable from either endpoint."""
        out = self.graph.edges('HOX:mechanism:cross-bridge-cycle',
                               types={'consumes'}, direction='out')
        self.assertTrue(out)
        inbound = self.graph.edges('CHEBI:15422', types={'consumes'},
                                   direction='in')
        self.assertTrue(inbound)
        self.assertEqual(out[0].relation.id, inbound[0].relation.id)
        self.assertEqual(inbound[0].type, 'consumed_by')

    def test_containment_is_single_parent(self):
        """[FR-REL-003] part_of is single-parent (INV-02)."""
        counts = {}
        for r in self.graph.substrate.relationships:
            if r.type == 'part_of':
                counts[r.source] = counts.get(r.source, 0) + 1
        for eid, n in counts.items():
            self.assertEqual(n, 1, f'{eid} has {n} part_of parents')

    def test_associations_are_separable_from_typed_relations(self):
        """[FR-REL-006] A mechanism view can exclude untyped associations."""
        eid = 'HOX:mechanism:cross-bridge-cycle'
        with_assoc = self.graph.edges(eid, include_associations=True)
        without = self.graph.edges(eid, include_associations=False)
        self.assertLess(len(without), len(with_assoc))
        self.assertTrue(all(not e.is_untyped_association for e in without))

    def test_traversal_is_bounded(self):
        """[FR-REL-010] An unbounded traversal returns everything, uselessly."""
        near = self.graph.traverse('UBERON:0000948', limit=1)
        far = self.graph.traverse('UBERON:0000948', limit=4)
        self.assertLess(len(near), len(far))
        self.assertEqual(max(near.values()), 1)

    def test_negative_traversal_limit_rejected(self):
        """[FR-REL-010] A malformed bound is refused, not silently clamped."""
        with self.assertRaises(ValueError):
            self.graph.traverse('UBERON:0000948', limit=-1)


class TestNavigationView(unittest.TestCase):
    """[FR-REL-009] [FR-NAV-004] [FR-NAV-005] — the tree is a view (D-006)."""

    @classmethod
    def setUpClass(cls):
        cls.graph = Graph(load(SUBSTRATE))

    def test_tree_is_derived_not_stored(self):
        """[FR-REL-009] Regenerating the tree yields the same shape."""
        a = self.graph.navigation_tree('UBERON:0000468')
        b = self.graph.navigation_tree('UBERON:0000468')
        self.assertEqual(a, b)
        # No persistent representation exists to be edited into disagreement.
        self.assertFalse(hasattr(self.graph, '_tree'))

    def test_tree_node_declares_itself_a_view(self):
        """[FR-NAV-004] A surface cannot render a node without knowing it is a view."""
        node = self.graph.navigation_tree('UBERON:0000468')
        self.assertTrue(node.is_view)

    def test_multi_membership_is_visible_from_the_tree(self):
        """[FR-NAV-005] The pancreas case: memberships travel with the node."""
        sub = load(SUBSTRATE)
        sub.entities.append(Entity(
            id='HOX:organ:pancreas', entity_class='Organ',
            subsystem='digestive', preferred_term='Pancreas',
            compilation_status='structured', level=3,
            part_of='UBERON:0000468'))
        from homeo.substrate import Relationship
        for i, system in enumerate(('UBERON:0004535', 'UBERON:0000468')):
            sub.relationships.append(Relationship(
                id=f'REL:test-member-{i}', source='HOX:organ:pancreas',
                target=system, type='member_of',
                provenance_claim='CLM:heart-function-pump'))
        g = Graph(sub)
        node = g.navigation_tree('UBERON:0000468', max_depth=2)
        pancreas = [c for c in node.children
                    if c.entity_id == 'HOX:organ:pancreas']
        self.assertEqual(len(pancreas), 1)
        self.assertEqual(len(pancreas[0].other_memberships), 2,
                         'both memberships must be reachable from the tree')

    def test_lineage_is_cycle_safe(self):
        """[FR-NAV-010] A malformed cycle must stop, not hang."""
        sub = Substrate(entities=[
            Entity(id='A', entity_class='Organ', subsystem='cardiovascular',
                   preferred_term='A', compilation_status='structured',
                   level=3, part_of='B'),
            Entity(id='B', entity_class='Organ', subsystem='cardiovascular',
                   preferred_term='B', compilation_status='structured',
                   level=3, part_of='A')])
        self.assertEqual(set(Graph(sub).lineage('A')), {'A', 'B'})


if __name__ == '__main__':
    unittest.main()
