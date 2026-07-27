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
