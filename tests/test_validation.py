"""The invariant harness, exercised as the release pipeline uses it.

These tests run tools/biocheck.py as a subprocess rather than importing it,
because that is exactly how the pre-commit hook, CI, and the release pipeline
invoke it — testing the import path would test something no caller uses.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

BIOCHECK = os.path.join('tools', 'biocheck.py')
SUBSTRATE = 'ontology'


def run(*args):
    return subprocess.run([sys.executable, BIOCHECK, *args],
                          capture_output=True, text=True, check=False)


class TestHarness(unittest.TestCase):
    """[FR-VALD-001] [FR-VALD-003] [FR-VALD-004] [FR-VALD-009]"""

    def test_clean_substrate_passes(self):
        """[FR-VALD-004] The pipeline's gate is green on the shipped substrate."""
        r = run(SUBSTRATE, '--strict')
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_exit_codes_match_specgraphs_idiom(self):
        """[FR-VALD-009] Two validators with different conventions is one
        validator people misread."""
        self.assertEqual(run(SUBSTRATE).returncode, 0)
        self.assertEqual(run('does-not-exist').returncode, 2)

    def test_report_states_what_validation_does_not_establish(self):
        """[FR-VALD-007] Passing checks is exactly when overconfidence sets in."""
        r = run(SUBSTRATE)
        self.assertIn('Consistency is not correctness', r.stdout)

    def test_json_output_is_machine_readable(self):
        """[FR-VALD-006] Results are recorded per release, not just printed."""
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, 'findings.json')
            run(SUBSTRATE, '--json', out)
            with open(out, encoding='utf-8') as fh:
                payload = json.load(fh)
            self.assertIn('findings', payload)


class TestNegativeTests(unittest.TestCase):
    """[FR-VALD-002] — a validator that cannot fail is not a validator."""

    def test_selftest_detects_every_injected_violation(self):
        r = run(SUBSTRATE, '--selftest')
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn('0 not detected', r.stdout)
        self.assertNotIn('NOT DETECTED', r.stdout)

    def test_selftest_covers_every_substrate_invariant(self):
        """Every INV except the runtime-only one is exercised."""
        r = run(SUBSTRATE, '--selftest')
        for n in range(1, 14):
            self.assertIn(f'INV-{n:02d}', r.stdout, f'INV-{n:02d} not exercised')
        self.assertIn('INV-15', r.stdout)
        # INV-14 is runtime-enforced by the groundedness guard, not the
        # substrate harness, and the report says so rather than omitting it.
        self.assertIn('INV-14  n/a here', r.stdout)


class TestBlockingBehaviour(unittest.TestCase):
    """[FR-VALD-003] [FR-VALD-005] — blocking stops the write; messages are
    biological, not schematic."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = os.path.join(self.tmp, 'ontology')
        shutil.copytree(SUBSTRATE, self.root)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _mutate(self, relpath, fn):
        path = os.path.join(self.root, relpath)
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
        fn(data)
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(data, fh)

    def test_depth_violation_blocks_and_names_the_subsystem(self):
        """[FR-VALD-005] The message names the biology, not the schema."""
        def add(data):
            data.append({
                'id': 'HOX:celltype:test-beta-cell', 'minted': True,
                'minted_reason': 'test fixture', 'entity_class': 'CellType',
                'level': 7, 'subsystem': 'immune',
                'preferred_term': 'Test beta cell',
                'compilation_status': 'structured'})
        self._mutate('seed/entities.json', add)
        r = run(self.root)
        self.assertEqual(r.returncode, 1)
        self.assertIn('exceeds declared depth L3 for immune', r.stdout)

    def test_missing_unit_blocks(self):
        def strip(data):
            data[0]['state_variables'][0].pop('unit', None)
        self._mutate('cardiovascular/processes.json', strip)
        r = run(self.root)
        self.assertEqual(r.returncode, 1)
        self.assertIn('INV-04', r.stdout)
        self.assertIn('no unit', r.stdout)

    def test_advisory_finding_does_not_block(self):
        """[FR-VALD-003] Advisory reports without stopping the write."""
        def loosen(data):
            for row in data:
                if row['id'] == 'CL:0000746':
                    row['representation_mode'] = 'enumerated'
        self._mutate('cardiovascular/entities.json', loosen)
        r = run(self.root)
        self.assertEqual(r.returncode, 0, 'advisory must not block')
        self.assertIn('INV-13', r.stdout)
        # ...but --strict promotes it, which is what CI uses.
        self.assertEqual(run(self.root, '--strict').returncode, 1)


class TestCoverageReport(unittest.TestCase):
    """[FR-SCAL-010] — the same numbers the product surfaces."""

    def test_coverage_marks_unpopulated_declared_levels(self):
        r = run(SUBSTRATE, '--coverage')
        self.assertEqual(r.returncode, 0)
        self.assertIn('UNPOPULATED', r.stdout)
        self.assertIn('unmet declaration', r.stdout)


if __name__ == '__main__':
    unittest.main()


class TestVocabularyDivergenceIsWiredIn(unittest.TestCase):
    """[FR-VALD-001] [INV-19] [D-023] The check must run, not merely exist.

    A mutation that deleted the `relation_divergence` call from the main path
    survived the first round: `--selftest` invokes the function directly, so it
    certified a check that no longer ran anywhere else. These tests drive the
    real command-line path with a diverging document instead.
    """

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.doc = os.path.join(self.dir, 'BIO_Anatomical_Ontology.md')

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _doc_without(self, relation):
        """A copy of the real relation table with one row removed."""
        src = os.path.join('docs', 'BIO_Anatomical_Ontology.md')
        with open(src, encoding='utf-8') as fh:
            lines = [ln for ln in fh
                     if not ln.startswith(f'| `{relation}` |')]
        with open(self.doc, 'w', encoding='utf-8') as fh:
            fh.writelines(lines)
        return self.doc

    def test_a_diverging_relation_table_fails_the_real_run(self):
        """Driven through the CLI, so deleting the call site is visible."""
        r = run(SUBSTRATE, '--relations', self._doc_without('member_of'))
        self.assertEqual(1, r.returncode, r.stdout)
        self.assertIn('INV-19', r.stdout)
        self.assertIn('member_of', r.stdout)

    def test_a_code_only_relation_is_named_as_such(self):
        """[FR-VALD-005] The message must say which way the divergence runs.

        Without this, the generic inverse-mismatch branch reports the same
        divergence with wording that sends a reader to fix the wrong file.
        """
        r = run(SUBSTRATE, '--relations', self._doc_without('member_of'))
        self.assertIn('in the code vocabulary but absent from', r.stdout)

    def test_a_doc_only_relation_is_named_as_such(self):
        """[FR-VALD-005] The other direction, worded for the other fix."""
        import importlib.util
        spec = importlib.util.spec_from_file_location('bc', BIOCHECK)
        bc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bc)
        documented = dict(bc.load_relations())
        documented['documented_only'] = 'documented_only_inverse'
        findings = bc.relation_divergence(documented)
        self.assertTrue(any('but absent from the code vocabulary' in m
                            for _, _, m in findings), findings)

    def test_the_message_names_the_file_actually_read(self):
        """[FR-VALD-005] A message naming the default path when another was
        read sends a reader to the wrong file."""
        doc = self._doc_without('member_of')
        r = run(SUBSTRATE, '--relations', doc)
        self.assertIn(doc, r.stdout)

    def test_a_diverging_eco_table_fails_the_real_run(self):
        ladder = os.path.join(self.dir, 'ladder.md')
        src = os.path.join('docs', 'BIO_Evidence_and_Provenance.md')
        with open(src, encoding='utf-8') as fh:
            text = fh.read()
        with open(ladder, 'w', encoding='utf-8') as fh:
            fh.write(text.replace('| ECO:0000006 | experimental evidence | EVC-2 ',
                                  '| ECO:0000006 | experimental evidence | EVC-1 '))
        r = run(SUBSTRATE, '--ladder', ladder)
        self.assertEqual(1, r.returncode, r.stdout)
        self.assertIn('ECO:0000006', r.stdout)

    def test_the_shipped_document_and_code_agree(self):
        """The state that must hold: no divergence on the real pair."""
        import importlib.util
        spec = importlib.util.spec_from_file_location('bc', BIOCHECK)
        bc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bc)
        self.assertEqual([], bc.relation_divergence(bc.load_relations()))
        self.assertEqual([], bc.eco_divergence(bc.load_eco_mapping()))

    def test_every_documented_relation_is_usable_in_the_substrate(self):
        """A relation the code cannot type is a row nobody can act on."""
        import importlib.util
        sys.path.insert(0, 'src')
        from homeo.substrate import INVERSES
        spec = importlib.util.spec_from_file_location('bc', BIOCHECK)
        bc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bc)
        documented = bc.load_relations()
        self.assertEqual(set(documented), set(INVERSES))
        self.assertIn('is_a', documented)
        self.assertEqual('subsumes', documented['is_a'])
