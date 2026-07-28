"""Verification is not review, and the difference has to be enforced.

An automated actor checked 13 findings against an openly licensed textbook and
recorded what it found. That is useful — it corrected a value and it upgraded
the provenance of three claims to a source a reader can actually open — and it
is **not** review. BR-002 forbids any agent assigning EVC-1 or EVC-2; D-017 and
INV-17 exist because this project has twice caught itself recording review that
never happened.

The temptation this file guards against is specific and will get stronger as the
register fills: 13 findings checked against a textbook *looks* like review, and
letting it count as review would empty out the one distinction the project's
correctness story rests on. So the boundary is a test, not a promise.

The matcher's own history is the argument for the boundary. Four successive
versions each produced confident false verdicts — image filenames read as
values, the blood-*brain* barrier answering for the blood-gas barrier, "97
percent of the alveolar surface area" offered as the number of alveoli. A
process that wrong that often must not be allowed to approve anything.
"""
import json
import os
import unittest

from homeo.evidence import EvidenceService
from homeo.graph import Graph
from homeo.scale import ScaleService
from homeo.substrate import load

REGISTER = os.path.join('ontology', 'VERIFICATION.json')


class TestVerificationChangesNoReviewState(unittest.TestCase):
    """[BR-002] [D-017] [INV-17] [D-033] The boundary, enforced."""

    @classmethod
    def setUpClass(cls):
        graph = Graph(load('ontology'))
        cls.evidence = EvidenceService(graph, ScaleService(graph))
        cls.entities = list(graph.entities())
        with open(REGISTER, encoding='utf-8') as fh:
            cls.register = json.load(fh)

    def test_the_reviewed_count_is_still_zero(self):
        """The number the whole project is judged by, unmoved by verification."""
        self.assertEqual(0, sum(1 for e in self.entities if e.is_reviewed))
        self.assertEqual(0, sum(1 for c in self.evidence.all_claims()
                                if c.is_reviewed))

    def test_no_verified_claim_was_promoted(self):
        """A confirmation is not a promotion. Every checked claim stays where
        it was, at a class an agent is allowed to assign."""
        checked = {r['claim'] for r in self.register['records']}
        for claim in self.evidence.all_claims():
            if claim.id in checked:
                self.assertNotIn(claim.evidence_class, ('EVC-1', 'EVC-2'),
                                 f'{claim.id} rose on the strength of a '
                                 f'machine check')
                self.assertEqual('provisional', claim.review_state, claim.id)

    def test_the_register_says_so_in_its_own_header(self):
        """A reader who finds this file alone must not mistake it for review."""
        note = self.register['note']
        self.assertIn('VERIFICATION IS NOT REVIEW', note)
        self.assertIn('does not approve', note)

    def test_no_record_carries_a_human_reviewer(self):
        for record in self.register['records']:
            self.assertNotIn('reviewer', record)
            self.assertNotIn('approved_by', record)
            for value in record.values():
                self.assertNotIn('human:', str(value))


class TestTheRegisterShowsItsWorking(unittest.TestCase):
    """A verdict without the sentence behind it is an opinion."""

    @classmethod
    def setUpClass(cls):
        with open(REGISTER, encoding='utf-8') as fh:
            cls.register = json.load(fh)

    def test_the_source_is_openly_licensed_and_identified(self):
        source = self.register['source']
        self.assertEqual('T0', source['licence_tier'])
        self.assertIn('CC BY', source['licence'])
        self.assertIn('1e', source['edition'],
                      'the edition must be recorded — 1e and 2e differ, and '
                      'the respiratory-rate correction came from that gap')

    def test_every_confirmation_quotes_what_it_turned_on(self):
        confirmed = [r for r in self.register['records']
                     if r['outcome'] == 'confirmed']
        self.assertTrue(confirmed)
        for record in confirmed:
            self.assertTrue(record['sentences'],
                            f'{record["claim"]} confirmed with nothing quoted')
            self.assertTrue(record['values_in_source'])
            self.assertTrue(record['section_sha256'],
                            'the section must be pinned, or the confirmation '
                            'cannot be reproduced')

    def test_an_uncovered_claim_is_not_recorded_as_refuted(self):
        """[EVC-8's logic] A source that does not mention something has not
        contradicted it. Ten of thirteen came back uncovered, which is a fact
        about this textbook, not about the biology."""
        for record in self.register['records']:
            self.assertIn(record['outcome'],
                          ('confirmed', 'not covered',
                           'candidate evidence, verdict withheld'))
            self.assertNotEqual('refuted', record['outcome'])

    def test_most_findings_rest_on_sources_nobody_can_open(self):
        """The uncomfortable result, asserted so it cannot be quietly dropped.

        The open textbook covers 3 of 13. The rest cite specialist works that
        are real, citable, and unopenable by a reader — which is exactly the
        provenance gap this pass was meant to measure.
        """
        uncovered = [r for r in self.register['records']
                     if r['outcome'] == 'not covered']
        self.assertGreater(len(uncovered), len(self.register['records']) / 2)


if __name__ == '__main__':
    unittest.main()
