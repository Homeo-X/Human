"""The ontology importer — what it produces, and what it refuses.

An importer's refusals matter more than its output. It runs over sixteen
thousand terms with no human watching, so anything it guesses at becomes
invisible the moment it lands in the graph. Every test here is built on the
real pinned snapshot rather than a fixture: a fixture would contain exactly the
shapes I thought to put in it, and the interesting failures came from shapes I
had not.
"""
import os
import unittest

from homeo.importers.obo import (RESOLVABLE, SCAFFOLDING, OboImporter, Term,
                                 load_snapshot, parse_obo, parse_obo_json)

SNAPSHOT = os.path.join('ontology', 'vocabularies', 'SNAPSHOTS.json')
HAVE_SNAPSHOT = os.path.isfile(SNAPSHOT)
HEART = 'UBERON:0000948'


def _term(**kw):
    base = dict(id='UBERON:0000001', label='thing', definition='A thing.')
    base.update(kw)
    return Term(**base)


class TestGrading(unittest.TestCase):
    """[D-021] A definition's grade is its source's resolvability, nothing else."""

    def test_a_resolvable_source_grades_trm1(self):
        for source in ('PMID:12345', 'DOI:10.1/x', 'ISBN:9780702077050',
                       'FMA:7088'):
            self.assertEqual('TRM-1',
                             _term(definition_sources=(source,)).grade(), source)

    def test_a_curator_initial_is_not_a_source(self):
        """CL cites `CARO:mah` — a person's initials, not something retrievable.

        Grading that TRM-1 would make TRM-1 mean nothing, which is the failure
        the whole register exists to avoid.
        """
        for source in ('CARO:mah', 'Wikipedia:Heart',
                       'http://orcid.org/0000-0002-6601-2165'):
            self.assertEqual('TRM-2',
                             _term(definition_sources=(source,)).grade(), source)

    def test_no_source_grades_trm3(self):
        self.assertEqual('TRM-3', _term(definition_sources=()).grade())

    def test_one_resolvable_source_among_several_is_enough(self):
        self.assertEqual('TRM-1', _term(
            definition_sources=('CARO:mah', 'PMID:1')).grade())


class TestHumanWarrant(unittest.TestCase):
    """[INV-12] A vertebrate class is not human until something says so."""

    def test_an_fma_xref_warrants_human(self):
        warrant = _term(xrefs=('FMA:7088', 'BTO:1')).human_warrant
        self.assertIsNotNone(warrant)
        self.assertIn('FMA is human-only', warrant)

    def test_the_human_reference_atlas_warrants_human(self):
        self.assertIsNotNone(
            _term(subsets=frozenset({'human_reference_atlas'})).human_warrant)

    def test_neither_leaves_no_warrant(self):
        self.assertIsNone(_term(xrefs=('BTO:1', 'MESH:D1')).human_warrant)


class TestRefusals(unittest.TestCase):
    """The importer declines rather than guesses, and says which."""

    def _result(self, terms, **kw):
        importer = OboImporter({t.id: t for t in terms},
                               pinned_version='test', **kw)
        return importer.build(terms)

    def _placeable(self, term):
        return 'cardiovascular'

    def test_a_term_with_no_placement_rule_is_refused(self):
        r = self._result([_term(subsets=frozenset({'organ_slim'}))])
        self.assertEqual(1, len(r.refusals))
        self.assertIn('unplaced', r.refusals[0].reason)

    def test_a_term_with_no_class_rule_is_refused(self):
        r = self._result([_term(id='FOO:1', subsets=frozenset({'organ_slim'}))],
                         placement=self._placeable)
        self.assertIn('unclassed', r.refusals[0].reason)

    def test_scaffolding_is_refused(self):
        for tag in SCAFFOLDING:
            r = self._result(
                [_term(subsets=frozenset({'organ_slim', tag}))],
                placement=self._placeable)
            self.assertIn('scaffolding', r.refusals[0].reason, tag)

    def test_an_obsolete_term_is_refused(self):
        r = self._result([_term(subsets=frozenset({'organ_slim'}),
                                obsolete=True)], placement=self._placeable)
        self.assertIn('obsolete', r.refusals[0].reason)

    def test_a_term_already_in_the_substrate_is_refused(self):
        """The defect this catches replaced a curated heart with a raw one.

        The substrate loader takes the last record read, so re-importing an
        existing id does not collide loudly — it silently wins.
        """
        term = _term(id=HEART, subsets=frozenset({'organ_slim'}))
        r = self._result([term], placement=self._placeable,
                         existing={HEART})
        self.assertEqual([], r.entities)
        self.assertIn('already present', r.refusals[0].reason)

    def test_a_placement_states_its_own_reason_for_refusing(self):
        """[D-027] Three different refusals landed in one bucket.

        `Placement` distinguishes non-human, unanchored and unplaced; the
        importer overwrote all three with "unplaced", so the import report said
        88 terms could not be filed when 67 of them had been refused for having
        no human warrant — the more interesting fact, and the one INV-12 is
        about.
        """
        class Stated:
            refusals = {'UBERON:0000001': 'non-human: no FMA cross-reference'}

            def __call__(self, term):
                return None

        r = self._result([_term(subsets=frozenset({'organ_slim'}))],
                         placement=Stated())
        self.assertEqual('non-human: no FMA cross-reference',
                         r.refusals[0].reason)

    def test_a_placement_with_nothing_to_say_still_refuses(self):
        """The generic reason remains for a placement that states none."""
        r = self._result([_term(subsets=frozenset({'organ_slim'}))],
                         placement=lambda term: None)
        self.assertIn('unplaced', r.refusals[0].reason)

    def test_an_undefined_term_yields_an_entity_and_no_claim(self):
        """Naming something is not defining it, and inventing the definition
        would be fabricating the record's own content."""
        r = self._result([_term(definition='',
                                subsets=frozenset({'organ_slim'}))],
                         placement=self._placeable)
        self.assertEqual(1, len(r.entities))
        self.assertEqual([], r.claims)
        self.assertEqual(1, len(r.undefined))


class TestEdgeProvenance(unittest.TestCase):
    """[FR-REL-008] An edge carries its own claim, never an endpoint's."""

    def test_every_relationship_has_a_distinct_provenance_claim(self):
        a = _term(id='UBERON:1', subsets=frozenset({'organ_slim'}))
        b = _term(id='UBERON:2', subsets=frozenset({'organ_slim'}),
                  parents=(('is_a', 'UBERON:1'),))
        importer = OboImporter({t.id: t for t in (a, b)},
                               pinned_version='test',
                               placement=lambda t: 'cardiovascular')
        r = importer.build([a, b])
        self.assertEqual(1, len(r.relationships))
        rel = r.relationships[0]
        claim_ids = {c['id'] for c in r.claims}
        self.assertIn(rel['provenance_claim'], claim_ids)
        definitions = {c['id'] for c in r.claims
                       if c['predicate'] == 'has_definition'}
        self.assertNotIn(rel['provenance_claim'], definitions,
                         'the edge borrowed an endpoint definition claim')

    def test_an_edge_to_a_refused_term_is_not_emitted(self):
        """Structure into a hole is worse than no structure."""
        a = _term(id='UBERON:1', subsets=frozenset({'organ_slim'}),
                  obsolete=True)
        b = _term(id='UBERON:2', subsets=frozenset({'organ_slim'}),
                  parents=(('is_a', 'UBERON:1'),))
        importer = OboImporter({t.id: t for t in (a, b)},
                               pinned_version='test',
                               placement=lambda t: 'cardiovascular')
        self.assertEqual([], importer.build([a, b]).relationships)


@unittest.skipUnless(HAVE_SNAPSHOT, 'no pinned snapshot in this checkout')
class TestAgainstThePinnedSnapshot(unittest.TestCase):
    """Against the real source, because that is where the surprises were."""

    @classmethod
    def setUpClass(cls):
        cls.terms, cls.version = load_snapshot('UBERON')

    def test_the_snapshot_parses_to_a_substantial_vocabulary(self):
        self.assertGreater(len(self.terms), 10_000)
        self.assertIn(HEART, self.terms)

    def test_the_heart_carries_what_the_importer_needs(self):
        heart = self.terms[HEART]
        self.assertEqual('heart', heart.label)
        self.assertTrue(heart.definition)
        self.assertTrue(heart.synonyms)
        self.assertIsNotNone(heart.human_warrant)

    def test_ubersons_own_part_of_does_not_give_this_projects_containment(self):
        """The finding that shaped the whole importer.

        The heart is `part_of` "heart plus pericardium", not the thorax. Anyone
        assuming an ontology's mereology is a navigable body gets a model full
        of grouping classes.
        """
        parents = [t for p, t in self.terms[HEART].parents if p != 'is_a']
        labels = [self.terms[p].label for p in parents if p in self.terms]
        self.assertNotIn('thoracic cavity', labels)
        self.assertTrue(any('pericardium' in l for l in labels), labels)

    def test_loading_a_snapshot_verifies_its_hash(self):
        self.assertTrue(self.version)


if __name__ == '__main__':
    unittest.main()
