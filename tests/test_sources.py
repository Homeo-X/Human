"""Source admission and licence tiers, on real content.

Two mechanisms specified in Phase 0 had never met the thing they were built for.

The **human warrant**: `obo.py` refuses a term with no FMA cross-reference (67
were refused on that ground) and then recorded the warrant only as prose, so the
identifier that justified admitting ~105 organs was unretrievable. One organ
carried an FMA xref. The rule was unauditable except by reading sentences.

The **licence tier**: D-003 admits share-alike geometry but quarantines it, and
`asset_tiers()` selects which tiers a build includes. Until BodyParts3D was
pinned, every asset in the substrate was permissive, so the exclusion branch had
never run on anything.
"""
import json
import os
import unittest

from homeo.graph import Graph
from homeo.release import ReleaseBuilder
from homeo.substrate import load

SUBSTRATE = 'ontology'
MANIFEST = os.path.join('ontology', 'assets', 'ASSETS.json')
REGISTRY = os.path.join('ontology', 'vocabularies', 'authorities.json')


class TestTheHumanWarrantIsStructured(unittest.TestCase):
    """[INV-10] [INV-12] [D-032] The rule that admitted an organ is retrievable."""

    @classmethod
    def setUpClass(cls):
        cls.graph = Graph(load(SUBSTRATE))
        cls.imported = [e for e in cls.graph.entities()
                        if e.level == 3
                        and 'UBERON' in str(e.provenance_source or '')]

    def test_the_import_actually_produced_organs(self):
        self.assertGreater(len(self.imported), 90)

    def test_almost_every_imported_organ_carries_its_fma_warrant(self):
        """The identifier, not a sentence about the identifier.

        Not all of them: a term may instead be warranted by membership of the
        human reference atlas, which is a different warrant and carries no FMA
        id. The assertion is that the *common* case is now data.
        """
        with_fma = [e for e in self.imported
                    if any(str(x.get('id', '')).startswith('FMA:')
                           for x in e.xrefs)]
        self.assertGreater(
            len(with_fma), 0.9 * len(self.imported),
            'the FMA cross-reference is what admitted these organs as human; '
            'if it is not on the record, the rule cannot be audited')

    def test_no_xref_names_an_unregistered_authority(self):
        """[INV-10] The importer filters to the registry rather than passing
        through whatever the source happened to carry (BTO, MESH, …)."""
        with open(REGISTRY, encoding='utf-8') as fh:
            registered = set(json.load(fh))
        for entity in self.graph.entities():
            for xref in entity.xrefs:
                # `authority` is the canonical field — the one INV-10 checks.
                # Deriving it from the `id` prefix instead fails on the
                # hand-seeded records, where `id` is a bare accession
                # (`{'authority': 'UniProt', 'id': 'P12883'}`).
                authority = xref.get('authority')
                self.assertIn(authority, registered,
                              f'{entity.id} cites unregistered {authority}')

    def test_a_cross_reference_is_pinned_to_the_snapshot_that_asserted_it(self):
        """We never opened an FMA release; what is pinned is UBERON saying so."""
        for entity in self.imported:
            for xref in entity.xrefs:
                if str(xref.get('id', '')).startswith('FMA:'):
                    self.assertTrue(xref.get('pinned_version'), entity.id)
                    self.assertIn('UBERON', xref.get('asserted_by', ''))


class TestLicenceTiersSeparate(unittest.TestCase):
    """[D-003] [BR-013] [FR-SPAT-005] [FR-SPAT-006] Share-alike is quarantined.

    The first content that exercises this. A permissive-only build must be a
    configuration change, not a re-derivation — that is the whole payoff for
    binding geometry through spatial identities.
    """

    @classmethod
    def setUpClass(cls):
        cls.builder = ReleaseBuilder(SUBSTRATE)
        with open(MANIFEST, encoding='utf-8') as fh:
            cls.manifest = json.load(fh)

    def test_the_substrate_holds_share_alike_assets_at_all(self):
        tiers = {a['licence_tier'] for a in self.manifest['assets'].values()}
        self.assertIn('T1', tiers, 'nothing here exercises the T1 path')
        self.assertIn('T0', tiers)

    def test_a_permissive_only_build_excludes_every_share_alike_asset(self):
        selection = self.builder.asset_tiers(('T0',))
        excluded = selection['excluded']
        self.assertTrue(excluded, 'a T0 build excluded nothing')
        for row in excluded:
            self.assertEqual('T1', row['tier'])
        for row in selection['included']:
            self.assertEqual('T0', row['tier'])

    def test_the_full_build_includes_both(self):
        selection = self.builder.asset_tiers(('T0', 'T1'))
        self.assertEqual([], selection['excluded'])
        self.assertGreater(len(selection['included']), 10)

    def test_every_share_alike_asset_carries_its_attribution(self):
        """CC-BY-SA is satisfied only if the credit travels with the asset."""
        for asset_id, record in self.manifest['assets'].items():
            if record['licence_tier'] == 'T1':
                self.assertIn('BodyParts3D', record['attribution'], asset_id)
                self.assertIn('Share Alike', record['attribution'], asset_id)

    def test_no_share_alike_bytes_are_in_the_repository(self):
        """[BR-013] The obligation must not arrive by accident."""
        for record in self.manifest['assets'].values():
            if record['licence_tier'] != 'T0':
                self.assertFalse(
                    os.path.isfile(os.path.join('ontology', record['file'])),
                    'share-alike bytes were committed into the substrate')


class TestTheSourceRuleReportsItsRefusals(unittest.TestCase):
    """[D-024] [D-032] Refusals are the honest half of an import."""

    @classmethod
    def setUpClass(cls):
        with open(MANIFEST, encoding='utf-8') as fh:
            cls.manifest = json.load(fh)

    def test_the_source_is_recorded_as_a_rule_not_as_a_list(self):
        """What a reviewer signs off is the source, once (D-026's shape)."""
        source = self.manifest['sources']['BodyParts3D']
        self.assertEqual('FMA', source['id_scheme'])
        self.assertEqual('T1', source['licence_tier'])
        self.assertEqual('derived', source['representation_kind'])

    def test_composite_organs_are_refused_with_a_reason(self):
        refusals = self.manifest['refusals']
        self.assertGreater(len(refusals), 50)
        for refusal in refusals:
            self.assertIn('no single mesh', refusal['reason'])
            self.assertTrue(refusal['fma'].startswith('FMA'))

    def test_the_index_the_join_depends_on_is_pinned_too(self):
        self.assertIn('ASSET:bodyparts3d-parts-index', self.manifest['assets'])

    def test_no_asset_claims_to_be_measured(self):
        """This project holds no measured geometry, and says so per asset."""
        for asset_id, record in self.manifest['assets'].items():
            self.assertNotEqual('measured', record['representation_kind'],
                                asset_id)


class TestMintedSpatialIdentitiesAssertAlmostNothing(unittest.TestCase):
    """[FR-SPAT-001] [D-032] A frame, so a mesh can bind. Nothing else.

    Position, laterality and containment are curation nobody has done. Absent is
    honest; guessed is indistinguishable from checked once it is in the graph.
    """

    @classmethod
    def setUpClass(cls):
        cls.minted = [si for si in load(SUBSTRATE).spatial_identities
                      if si.geometry
                      and si.geometry[0].get('licence_tier') == 'T1']

    def test_meshes_were_bound_through_spatial_identities(self):
        self.assertGreaterEqual(len(self.minted), 10)

    def test_each_declares_a_coordinate_frame(self):
        for si in self.minted:
            self.assertTrue(si.coordinate_frame, si.id)

    def test_none_invents_a_position_or_a_laterality(self):
        for si in self.minted:
            self.assertIsNone(si.anatomical_position, si.id)
            self.assertIsNone(si.laterality, si.id)
            self.assertEqual((), si.landmarks, si.id)


if __name__ == '__main__':
    unittest.main()


class TestTheProducersAreGuarded(unittest.TestCase):
    """The gates, driven directly rather than through their output.

    The first version of this file only read `ontology/` and `ASSETS.json`.
    Every mutation of the code that *writes* them survived, because committed
    artifacts do not change when you break their producer — the mirror image of
    the INV-19 case, where a check was exercised only through the function and
    the call site could be deleted freely. A gate needs a test that runs it.
    """

    def test_an_unregistered_cross_reference_is_dropped(self):
        """[INV-10] BTO and MESH ride along on UBERON terms; neither is ours."""
        import sys
        sys.path.insert(0, 'tools')
        from homeo.importers.obo import RULES, OboImporter, Term

        term = Term(id='UBERON:0000955', label='brain',
                    definition='The organ of thought.',
                    xrefs=('FMA:50801', 'BTO:0000142', 'MESH:D001921'),
                    subsets=frozenset({'organ_slim'}))
        importer = OboImporter({term.id: term}, pinned_version='test',
                               placement=lambda t: 'nervous')
        entity, _ = importer._entity(term, RULES[0])
        authorities = {x['authority'] for x in entity['xrefs']}
        self.assertIn('FMA', authorities, 'the human warrant was dropped')
        self.assertNotIn('BTO', authorities)
        self.assertNotIn('MESH', authorities)

    def test_a_spatial_identity_is_proposed_with_the_structural_tool(self):
        """[FR-AGD-003] AGT-3 holds TOOL-03 and not TOOL-04.

        Routing a spatial identity to the claim tool made the Anatomy agent
        unable to place anatomy. The contract was right; the routing was wrong.
        """
        from homeo.agents import AgentRuntime
        from homeo.curation import CurationService

        runtime = AgentRuntime(CurationService([], queue_ceiling=8))
        run = runtime.start('AGT-3', 'place a structure')
        task = runtime.propose(
            run, kind='spatial_identity', subsystem='foundational', level=3,
            payload={'spatial_identity': {'id': 'SPI:test', 'entity': 'X',
                                          'coordinate_frame': 'F'}},
            sources=['https://example.invalid'], rationale='test')
        self.assertTrue(task)
        self.assertTrue(any(c.tool == 'TOOL-03' for c in run.tool_calls),
                        'a spatial identity was not routed as structural')

    def test_a_share_alike_licence_may_never_be_labelled_permissive(self):
        """[BR-013] [D-003] The mislabel is the failure the tier exists to stop.

        Checked against the licence *string*, so relabelling the tier without
        changing the licence — the cheap mistake — is caught.
        """
        import sys
        sys.path.insert(0, 'tools')
        from fetch_assets import ASSETS, BODYPARTS3D

        sources = list(ASSETS.values()) + [BODYPARTS3D]
        for source in sources:
            licence = source['licence'].lower()
            share_alike = 'sa' in licence.replace('-', ' ').split() or \
                'share alike' in licence or 'share-alike' in licence
            if share_alike:
                self.assertEqual(
                    'T1', source['licence_tier'],
                    f'{source["licence"]} is share-alike and must be T1')
            else:
                self.assertEqual('T0', source['licence_tier'],
                                 f'{source["licence"]} is not share-alike')
