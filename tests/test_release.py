"""Release building, hashing, immutability, and atomic publication."""
import json
import os
import shutil
import tempfile
import unittest

from homeo.release import (Manifest, ReleaseBuilder, ReleaseError,
                           canonical_bytes, content_hash, diff, verify_rebuild)
from homeo.substrate import load

SUBSTRATE = 'ontology'


class TestDeterminism(unittest.TestCase):
    """[FR-VER-002] — G-07. A near-match is a failure, not a success."""

    def test_hash_is_stable_across_loads(self):
        self.assertEqual(content_hash(load(SUBSTRATE)),
                         content_hash(load(SUBSTRATE)))

    def test_serialization_is_order_independent(self):
        """File discovery order must not influence the hash."""
        a = load(SUBSTRATE)
        b = load(SUBSTRATE)
        b.entities.reverse()
        b.claims.reverse()
        b.relationships.reverse()
        self.assertEqual(canonical_bytes(a), canonical_bytes(b))

    def test_a_content_change_changes_the_hash(self):
        """Determinism must not mean insensitivity."""
        a = load(SUBSTRATE)
        before = content_hash(a)
        a.declared_depth['cardiovascular'] = 3
        self.assertNotEqual(before, content_hash(a))

    def test_rebuild_verification(self):
        builder = ReleaseBuilder(SUBSTRATE)
        manifest = builder.build('rel-verify')
        self.assertTrue(verify_rebuild(SUBSTRATE, manifest))


class TestManifest(unittest.TestCase):
    """[FR-VER-003] [FR-VER-004] [FR-VER-005]"""

    @classmethod
    def setUpClass(cls):
        cls.manifest = ReleaseBuilder(SUBSTRATE).build('rel-manifest')

    def test_every_authority_is_pinned(self):
        """[FR-VER-003] Without pinning, upstream change rewrites the past."""
        self.assertTrue(self.manifest.authorities)
        for row in self.manifest.authorities:
            self.assertTrue(row['pinned_versions'],
                            f'{row["authority"]} has no pinned version')

    def test_unpinned_xref_blocks_the_build(self):
        """[FR-VER-003] A release cannot be built against an unpinned authority."""
        builder = ReleaseBuilder(SUBSTRATE)
        target = next(e for e in builder.substrate.entities if e.xrefs)
        idx = builder.substrate.entities.index(target)
        broken = dict(target.__dict__)
        broken['xrefs'] = ({'authority': 'UBERON', 'id': 'X',
                            'pinned_version': ''},)
        from homeo.substrate import Entity
        builder.substrate.entities[idx] = Entity(**broken)
        with self.assertRaises(ReleaseError) as ctx:
            builder.build('rel-broken')
        self.assertIn('unpinned authority', str(ctx.exception))

    def test_sources_carry_licence_tiers(self):
        """[FR-VER-004] An export without its licence manifest transfers an
        obligation the recipient cannot see."""
        self.assertTrue(self.manifest.sources)
        for s in self.manifest.sources:
            self.assertIn('licence_tier', s)
        self.assertTrue(self.manifest.licence_tiers)

    def test_manifest_records_the_validation_result(self):
        """[FR-VER-005] The gate is in the pipeline, not in a checklist."""
        self.assertIn('passed', self.manifest.validation)
        self.assertTrue(self.manifest.validation['passed'])

    def test_manifest_publishes_the_honesty_metrics(self):
        """[FR-EVID-013] Minted-id drift and the UNKNOWN split ship with it."""
        self.assertGreater(self.manifest.minted_ids, 0)
        counts = self.manifest.unknown_counts
        self.assertEqual(counts['total'],
                         counts['asked_for'] + counts['unprompted'])


class TestPublication(unittest.TestCase):
    """[FR-VER-001] [FR-VER-012] — atomic, or not at all (CH-07)."""

    def setUp(self):
        self.out = tempfile.mkdtemp()
        self.builder = ReleaseBuilder(SUBSTRATE)

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)

    def test_publish_writes_every_named_artifact(self):
        m = self.builder.publish('rel-a', self.out)
        target = os.path.join(self.out, 'rel-a')
        for art in m.artifacts:
            self.assertTrue(os.path.isfile(os.path.join(target, art['name'])))
        self.assertTrue(os.path.isfile(os.path.join(target, 'manifest.json')))

    def test_manifest_artifact_hashes_match_on_disk(self):
        """[FR-VER-012] Correspondence is verified, not assumed."""
        import hashlib
        m = self.builder.publish('rel-b', self.out)
        for art in m.artifacts:
            path = os.path.join(self.out, 'rel-b', art['name'])
            with open(path, 'rb') as fh:
                self.assertEqual(hashlib.sha256(fh.read()).hexdigest(),
                                 art['sha256'])

    def test_republishing_the_same_id_is_refused(self):
        """[FR-VER-001] Published releases are superseded, never overwritten."""
        self.builder.publish('rel-c', self.out)
        with self.assertRaises(ReleaseError) as ctx:
            self.builder.publish('rel-c', self.out)
        self.assertIn('immutable', str(ctx.exception))

    def test_no_staging_directory_survives_a_successful_publish(self):
        self.builder.publish('rel-d', self.out)
        self.assertFalse(os.path.exists(os.path.join(self.out,
                                                     'rel-d.staging')))

    def test_failed_validation_refuses_publication(self):
        """[FR-VER-005] A blocking violation stops the release."""
        builder = ReleaseBuilder(SUBSTRATE)
        original = builder.validate

        def failing(strict=True):
            result = original(strict=strict)
            result.passed = False
            result.errors = ['INV-02 multiple part_of parents for X']
            return result

        builder.validate = failing
        with self.assertRaises(ReleaseError) as ctx:
            builder.publish('rel-fail', self.out)
        self.assertIn('validation failed', str(ctx.exception))
        self.assertFalse(os.path.exists(os.path.join(self.out, 'rel-fail')))

    def test_published_manifest_is_readable_json(self):
        m = self.builder.publish('rel-e', self.out)
        with open(os.path.join(self.out, 'rel-e', 'manifest.json'),
                  encoding='utf-8') as fh:
            on_disk = json.load(fh)
        self.assertEqual(on_disk['content_hash'], m.content_hash)


class TestBreakingChanges(unittest.TestCase):
    """[FR-VER-006] [FR-VER-013] — CH-03: narrowing must be visible."""

    def test_narrowing_declared_depth_is_breaking(self):
        builder = ReleaseBuilder(SUBSTRATE)
        previous = builder.build('rel-prev')
        builder.substrate.declared_depth['endocrine'] = 2
        current = builder.build('rel-next', previous=previous)
        self.assertTrue(current.breaking)
        self.assertTrue(any('endocrine' in n and 'narrowed' in n
                            for n in current.notes))

    def test_narrowing_note_demands_both_denominators(self):
        """[FR-VER-013] The party measured can change the denominator."""
        builder = ReleaseBuilder(SUBSTRATE)
        previous = builder.build('rel-prev')
        builder.substrate.declared_depth['endocrine'] = 2
        current = builder.build('rel-next', previous=previous)
        note = next(n for n in current.notes if 'narrowed' in n)
        self.assertIn('both denominators', note)

    def test_entity_removal_is_breaking(self):
        builder = ReleaseBuilder(SUBSTRATE)
        previous = builder.build('rel-prev')
        builder.substrate.entities.pop()
        current = builder.build('rel-next', previous=previous)
        self.assertTrue(current.breaking)
        self.assertTrue(any('tombstone' in n for n in current.notes))

    def test_additive_change_is_not_breaking(self):
        builder = ReleaseBuilder(SUBSTRATE)
        previous = builder.build('rel-prev')
        current = builder.build('rel-next', previous=previous)
        self.assertFalse(current.breaking)


class TestDiff(unittest.TestCase):
    """[FR-VER-011] — class changes must not hide among additions."""

    def test_diff_reports_record_and_unknown_deltas(self):
        builder = ReleaseBuilder(SUBSTRATE)
        a = builder.build('rel-a')
        b = builder.build('rel-b')
        d = diff(a, b)
        self.assertFalse(d['content_hash_changed'])
        self.assertEqual(d['record_delta']['entities'], 0)
        self.assertIn('unknown_delta', d)

    def test_diff_detects_content_change(self):
        builder = ReleaseBuilder(SUBSTRATE)
        a = builder.build('rel-a')
        builder.substrate.declared_depth['immune'] = 2
        b = builder.build('rel-b', previous=a)
        self.assertTrue(diff(a, b)['content_hash_changed'])


if __name__ == '__main__':
    unittest.main()


class TestAcceptedFindingsArePublished(unittest.TestCase):
    """[FR-VER-006] [D-029] A release states the content's known limits.

    The alternative was a release pipeline blocked forever by an advisory
    finding it could describe perfectly well — 98 organs placed by system
    membership rather than by containment. Blocking would have produced no
    releases; hiding it would have produced dishonest ones. Publishing the
    finding in the manifest is the only option that matches what the rest of
    this project does with things it does not know.
    """

    def setUp(self):
        self.builder = ReleaseBuilder('ontology')

    def test_the_manifest_records_the_accepted_finding_in_full(self):
        manifest = self.builder.build('rel-accepted')
        accepted = manifest.validation['accepted']
        self.assertTrue(accepted, 'the standing finding vanished from the manifest')
        self.assertTrue(any('INV-21' in a for a in accepted))
        self.assertTrue(any('not located in the body' in a for a in accepted),
                        'the manifest kept the id but dropped what it means')

    def test_validation_still_passes_with_it(self):
        self.assertTrue(self.builder.validate().passed)

    def test_a_builder_accepting_nothing_does_not_pass(self):
        """Acceptance is a stated choice, never the default behaviour."""
        strict = ReleaseBuilder('ontology', accepted=())
        result = strict.validate()
        self.assertFalse(result.passed)
        self.assertTrue(any('INV-21' in w for w in result.warnings))
        self.assertEqual([], result.accepted)
