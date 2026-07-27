"""The synthetic substrate generator, and the one property that really matters.

`tools/synth.py` fabricates anatomy. That is fine — it is a benchmark fixture —
but it makes the generator the single most dangerous tool in the repository:
this project's whole argument is that nothing enters the substrate unreviewed
and unsourced, and here is a program that produces a hundred thousand
plausible-shaped entities in nine seconds. If one ever reached `ontology/`, the
evidence apparatus would still pass green over content nobody wrote.

So the tests below are weighted accordingly. The timing behaviour is checked
lightly; the containment of the fixture is checked hard.
"""
import json
import os
import shutil
import tempfile
import unittest

import sys

sys.path.insert(0, 'tools')

import synth                                        # noqa: E402
from homeo.substrate import load                    # noqa: E402


class TestNothingSyntheticIsCanonical(unittest.TestCase):
    """[D-028] The fixture must never be reachable from the real substrate."""

    def test_no_synthetic_id_is_in_the_canonical_substrate(self):
        substrate = load('ontology')
        rows = (substrate.entities + substrate.claims
                + substrate.relationships + substrate.processes)
        offenders = [r.id for r in rows if r.id.startswith('SYN:')]
        self.assertEqual([], offenders,
                         'synthetic benchmark records reached ontology/')

    def test_the_generator_refuses_a_root_holding_real_records(self):
        with self.assertRaises(SystemExit) as caught:
            synth._refuse_real_content('ontology')
        self.assertIn('refusing to write', str(caught.exception))

    def test_the_guard_is_on_content_not_on_the_path(self):
        """A path allowlist would be a convention; this must be a property.

        Renaming `ontology/` to anything else would defeat a name check, and
        the failure would be silent — the generator would happily overwrite
        curated records in a directory it did not recognise.
        """
        tmp = tempfile.mkdtemp()
        try:
            with open(os.path.join(tmp, 'entities.json'), 'w') as fh:
                json.dump([{'id': 'UBERON:0000948'}], fh)
            with self.assertRaises(SystemExit):
                synth._refuse_real_content(tmp)
        finally:
            shutil.rmtree(tmp)

    def test_a_purely_synthetic_root_is_accepted(self):
        """The guard must not be so broad that it refuses its own output."""
        tmp = tempfile.mkdtemp()
        try:
            with open(os.path.join(tmp, 'entities.json'), 'w') as fh:
                json.dump([{'id': 'SYN:e0000001'}], fh)
            synth._refuse_real_content(tmp)          # must not raise
        finally:
            shutil.rmtree(tmp)

    def test_every_generated_record_is_namespaced_and_marked(self):
        built = synth.generate(200, 1.5, seed=1)
        for entity in built['entities']:
            self.assertTrue(entity['id'].startswith('SYN:'), entity['id'])
            self.assertIn('never enter the canonical substrate',
                          entity['provenance_source'])
        for claim in built['claims']:
            self.assertEqual('agent:synthetic', claim['assigned_by'])
            self.assertEqual('provisional', claim['review_state'])

    def test_no_generated_claim_asserts_a_reviewed_evidence_class(self):
        """[BR-002] Not even a fixture may mint EVC-1 or EVC-2."""
        built = synth.generate(500, 3.0, seed=2)
        classes = {c['evidence_class'] for c in built['claims']}
        self.assertNotIn('EVC-1', classes)
        self.assertNotIn('EVC-2', classes)


class TestTheFixtureHasTheRealShape(unittest.TestCase):
    """A fixture shaped unlike the substrate measures the wrong thing."""

    @classmethod
    def setUpClass(cls):
        cls.built = synth.generate(5_000, 1.53, seed=3)

    def test_it_contains_multi_membership_organs(self):
        """The pancreas case at fixture scale.

        A generated body where every organ belongs to exactly one system would
        benchmark only the single-parent path — which is how D-019 stayed
        hidden in the real substrate for as long as it did.
        """
        members = {}
        for rel in self.built['relationships']:
            if rel['type'] == 'member_of':
                members.setdefault(rel['source'], set()).add(rel['target'])
        multi = [k for k, v in members.items() if len(v) > 1]
        self.assertTrue(multi, 'no multi-membership organ in the fixture')

    def test_the_containment_spine_reaches_the_root(self):
        parents = {e['id']: e['part_of'] for e in self.built['entities']}
        deep = [e for e in self.built['entities'] if e['level'] >= 3]
        self.assertTrue(deep)
        for entity in deep[:50]:
            seen, current = 0, entity['id']
            while parents.get(current) and seen < 20:
                current = parents[current]
                seen += 1
            self.assertEqual('SYN:organism', current, entity['id'])

    def test_generation_is_deterministic(self):
        """A fixture that drifts makes every benchmark incomparable."""
        a = synth.generate(1_000, 1.53, seed=7)
        b = synth.generate(1_000, 1.53, seed=7)
        self.assertEqual(json.dumps(a, sort_keys=True),
                         json.dumps(b, sort_keys=True))

    def test_the_real_loader_accepts_it(self):
        """The benchmark is worthless if it exercises a parallel code path."""
        tmp = tempfile.mkdtemp()
        try:
            for name, rows in self.built.items():
                with open(os.path.join(tmp, f'{name}.json'), 'w') as fh:
                    json.dump(rows, fh)
            substrate = load(tmp)
            self.assertEqual(len(self.built['entities']),
                             len(substrate.entities))
        finally:
            shutil.rmtree(tmp)


if __name__ == '__main__':
    unittest.main()
