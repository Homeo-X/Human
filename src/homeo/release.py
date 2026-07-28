"""Building, validating, hashing, and publishing an immutable release.

A release is the unit of citation, and citation only works if the thing cited
cannot change. Immutability is therefore structural: a published release is
content-addressed, and publication is atomic across every artifact the manifest
names (FR-VER-012, CH-07).

Reproducibility is enforced rather than hoped for. The build serializes with
sorted keys and a fixed separator, so a rebuild from the same substrate produces
the same bytes; a near-match is a failure, not a success (FR-VER-002, G-07).

Realizes: FR-VER-001, FR-VER-002, FR-VER-003, FR-VER-004, FR-VER-005,
FR-VER-006, FR-VER-011, FR-VER-012.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field

from .substrate import Substrate, load

RELEASE_STATES = ('draft', 'validated', 'published', 'superseded')
# Canonical serialization: sorted keys, no incidental whitespace, UTF-8 text
# preserved rather than escaped. Any change here is a breaking change to every
# release hash ever produced.
_JSON = {'sort_keys': True, 'separators': (',', ':'), 'ensure_ascii': False}


class ReleaseError(Exception):
    """A release could not be built or published. Never raised for content the
    substrate legitimately lacks."""


@dataclass
class ValidationResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    # Advisory findings the release acknowledges rather than blocks on. They
    # ship *in the manifest*: a consumer reading the release learns that 98
    # organs are not located in the body, which is the point (D-029).
    accepted: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {'passed': self.passed, 'errors': self.errors,
                'warnings': self.warnings, 'accepted': self.accepted}


@dataclass
class Manifest:
    release_id: str
    content_hash: str
    record_counts: dict[str, int]
    authorities: list[dict]
    sources: list[dict]
    licence_tiers: dict[str, int]
    declared_depth: dict[str, int]
    validation: dict
    artifacts: list[dict]
    minted_ids: int
    unknown_counts: dict
    breaking: bool
    notes: list[str] = field(default_factory=list)
    compilation_ladder: dict = field(default_factory=dict)
    evaluations: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            'release_id': self.release_id, 'content_hash': self.content_hash,
            'record_counts': self.record_counts, 'authorities': self.authorities,
            'sources': self.sources, 'licence_tiers': self.licence_tiers,
            'declared_depth': self.declared_depth, 'validation': self.validation,
            'artifacts': self.artifacts, 'minted_ids': self.minted_ids,
            'unknown_counts': self.unknown_counts, 'breaking': self.breaking,
            'notes': self.notes, 'compilation_ladder': self.compilation_ladder,
            'evaluations': self.evaluations,
        }


def canonical_bytes(substrate: Substrate) -> bytes:
    """Deterministic serialization of a substrate.

    Everything is sorted by id so that file discovery order, filesystem
    ordering, and directory layout cannot influence the hash.
    """
    payload = {
        'entities': sorted(
            ({'id': e.id, 'entity_class': e.entity_class,
              'subsystem': e.subsystem, 'preferred_term': e.preferred_term,
              'compilation_status': e.compilation_status, 'minted': e.minted,
              'level': e.level, 'spatial_scale': list(e.spatial_scale),
              'representation_mode': e.representation_mode,
              'part_of': e.part_of,
              'xrefs': sorted((f'{x.get("authority")}:{x.get("id")}'
                               f'@{x.get("pinned_version")}' for x in e.xrefs)),
              'retired_at': e.retired_at, 'successor_id': e.successor_id}
             for e in substrate.entities), key=lambda r: r['id']),
        'claims': sorted(
            ({'id': c.id, 'subject': c.subject, 'predicate': c.predicate,
              'object': c.object, 'unit': c.unit,
              'evidence_class': c.evidence_class, 'species': c.species,
              'population': c.population, 'source_type': c.source_type,
              'assigned_by': c.assigned_by, 'date_asserted': c.date_asserted}
             for c in substrate.claims), key=lambda r: r['id']),
        'relationships': sorted(
            ({'id': r.id, 'source': r.source, 'target': r.target,
              'type': r.type, 'provenance_claim': r.provenance_claim,
              'compilation_status': r.compilation_status}
             for r in substrate.relationships), key=lambda r: r['id']),
        'processes': sorted(
            ({'id': p.id, 'label': p.label, 'subsystem': p.subsystem,
              'spatial_scale': list(p.spatial_scale),
              'timescale_domain': p.timescale_domain,
              'representation_status': p.representation_status,
              'evidence_class': p.evidence_class}
             for p in substrate.processes), key=lambda r: r['id']),
        'spatial_identities': sorted(
            ({'id': s.id, 'entity': s.entity,
              'coordinate_frame': s.coordinate_frame,
              'geometry': [g.get('asset_id') for g in s.geometry]}
             for s in substrate.spatial_identities), key=lambda r: r['id']),
        'scale_contracts': sorted(
            ({'id': s.id, 'level': s.level,
              'representation_mode': list(s.representation_mode),
              'resolution_limit': s.resolution_limit}
             for s in substrate.scale_contracts), key=lambda r: r['id']),
        'declared_depth': substrate.declared_depth,
        'authorities': sorted(substrate.authorities),
    }
    return json.dumps(payload, **_JSON).encode('utf-8')


def content_hash(substrate: Substrate) -> str:
    return hashlib.sha256(canonical_bytes(substrate)).hexdigest()


class ReleaseBuilder:
    """Build → validate → hash → publish, in that order and no other."""

    # Advisory invariants whose finding is a known standing property of the
    # content rather than a regression. A release does not hide these — it
    # **publishes** them, in the manifest, with their full message (D-029).
    # Blocking invariants can never appear here: `biocheck --accept` refuses a
    # blocking id outright, so this list cannot be widened into a way of
    # shipping past a real failure.
    ACCEPTED = ('INV-21',)

    def __init__(self, substrate_root: str, tools_dir: str = 'tools',
                 accepted: tuple[str, ...] | None = None):
        self.substrate_root = substrate_root
        self.tools_dir = tools_dir
        self.accepted = self.ACCEPTED if accepted is None else accepted
        self.substrate = load(substrate_root)

    # ---- validation ----------------------------------------------------

    def validate(self, strict: bool = True) -> ValidationResult:
        """Run the invariant harness. A blocking failure stops publication.

        Shells out to tools/biocheck.py deliberately: one implementation of the
        invariants, used identically by CI, the pre-commit hook, and the release
        pipeline (FR-VALD-009).
        """
        script = os.path.join(self.tools_dir, 'biocheck.py')
        if not os.path.isfile(script):
            return ValidationResult(
                passed=False, errors=[f'validator not found at {script}'])
        cmd = [sys.executable, script, self.substrate_root]
        if strict:
            cmd.append('--strict')
        for inv in self.accepted:
            cmd += ['--accept', inv]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        errors = [ln[7:].strip() for ln in proc.stdout.splitlines()
                  if ln.startswith('ERROR:')]
        warnings = [ln[6:].strip() for ln in proc.stdout.splitlines()
                    if ln.startswith('WARN:')]
        noted = [ln[6:].strip() for ln in proc.stdout.splitlines()
                 if ln.startswith('NOTED:')]
        return ValidationResult(passed=proc.returncode == 0, errors=errors,
                                warnings=warnings, accepted=noted)

    # ---- manifest ------------------------------------------------------

    def _authorities(self) -> list[dict]:
        """Pinned authority versions (FR-VER-003).

        A release that cannot state which vocabulary version answered it cannot
        be re-evaluated later, so an unpinned xref blocks the build.
        """
        pins: dict[str, set[str]] = {}
        for e in self.substrate.entities:
            for x in e.xrefs:
                auth, ver = x.get('authority'), x.get('pinned_version')
                if not auth:
                    continue
                if not ver:
                    raise ReleaseError(
                        f'{e.id}: xref to {auth} has no pinned version; a '
                        f'release cannot be built against an unpinned authority')
                pins.setdefault(auth, set()).add(ver)
        return [{'authority': a, 'pinned_versions': sorted(v)}
                for a, v in sorted(pins.items())]

    def _sources(self) -> tuple[list[dict], dict[str, int]]:
        """Every source with its licence and tier (FR-VER-004)."""
        seen: dict[str, dict] = {}
        tiers: dict[str, int] = {}
        for c in self.substrate.claims:
            for s in c.sources:
                ident = s.get('identifier') or s.get('citation', '')
                tier = s.get('licence_tier', 'unspecified')
                seen.setdefault(ident, {
                    'identifier': ident, 'citation': s.get('citation'),
                    'licence_tier': tier})
                tiers[tier] = tiers.get(tier, 0) + 1
        for si in self.substrate.spatial_identities:
            for g in si.geometry:
                ident = g.get('asset_id', '')
                tier = g.get('licence_tier', 'unspecified')
                seen.setdefault(ident, {
                    'identifier': ident, 'citation': g.get('source'),
                    'licence': g.get('licence'), 'licence_tier': tier})
                tiers[tier] = tiers.get(tier, 0) + 1
        return sorted(seen.values(), key=lambda r: r['identifier']), tiers

    def asset_tiers(self, allowed: tuple[str, ...] = ('T0', 'T1')) -> dict:
        """Select which licence tiers a build includes (FR-SPAT-006, D-003).

        A permissive-only build is a configuration, not a re-derivation — that
        is the payoff for binding geometry through spatial identities (D-008).
        Coverage is reported against the *unchanged* declared denominator, so a
        smaller build looks smaller rather than looking complete.
        """
        included, excluded = [], []
        for si in self.substrate.spatial_identities:
            for g in si.geometry:
                row = {'spatial_identity': si.id, 'asset': g.get('asset_id'),
                       'tier': g.get('licence_tier'),
                       'licence': g.get('licence')}
                (included if g.get('licence_tier') in allowed
                 else excluded).append(row)
        return {
            'allowed_tiers': list(allowed), 'included': included,
            'excluded': excluded,
            'note': ('Coverage is reported against the declared denominator '
                     'regardless of tier selection: a build with fewer assets '
                     'must look smaller, not look complete.'),
        }

    def build(self, release_id: str, *, previous: Manifest | None = None,
              strict: bool = True) -> Manifest:
        validation = self.validate(strict=strict)
        chash = content_hash(self.substrate)
        sources, tiers = self._sources()
        unknown = [c for c in self.substrate.claims if c.is_unknown]
        counts = {
            'entities': len(self.substrate.entities),
            'claims': len(self.substrate.claims),
            'relationships': len(self.substrate.relationships),
            'processes': len(self.substrate.processes),
            'spatial_identities': len(self.substrate.spatial_identities),
            'scale_contracts': len(self.substrate.scale_contracts),
        }
        breaking = False
        notes: list[str] = []
        if previous is not None:
            breaking, notes = self._breaking_changes(previous)
        ladder, evaluations = self._quality_reports()
        return Manifest(
            release_id=release_id, content_hash=chash, record_counts=counts,
            authorities=self._authorities(), sources=sources,
            licence_tiers=tiers,
            declared_depth=dict(self.substrate.declared_depth),
            validation=validation.as_dict(), artifacts=[],
            minted_ids=sum(1 for e in self.substrate.entities if e.minted),
            unknown_counts={
                'total': len(unknown),
                'asked_for': sum(1 for c in unknown if c.prompted_by),
                'unprompted': sum(1 for c in unknown if not c.prompted_by)},
            breaking=breaking, notes=notes, compilation_ladder=ladder,
            evaluations=evaluations)

    def _quality_reports(self) -> tuple[dict, dict]:
        """Ladder state and EV results, both shipped in the manifest.

        The ladder proportion keeps "we have N entities" from being read as "we
        have N modelled entities" (RSK-10); the EV results are the release gate
        for the retrieval surface (FR-RETR-007).
        """
        from .evals import run_all
        from .evidence import EvidenceService
        from .graph import Graph
        from .groundedness import GroundednessGuard
        from .promotion import PromotionService
        from .scale import ScaleService
        graph = Graph(self.substrate)
        scale = ScaleService(graph)
        evidence = EvidenceService(graph, scale)
        ladder = PromotionService(graph, evidence).ladder_report()
        guard = GroundednessGuard(graph, evidence, scale)
        return ladder, run_all(guard)

    def _breaking_changes(self, previous: Manifest) -> tuple[bool, list[str]]:
        """Removals, identifier changes, and depth narrowing are breaking."""
        notes: list[str] = []
        prev_depth = previous.declared_depth
        for sub, cap in prev_depth.items():
            now = self.substrate.declared_depth.get(sub)
            if now is None:
                notes.append(f'subsystem {sub} removed from declared depth')
            elif now < cap:
                # CH-03/FR-VER-013: narrowing must state its coverage effect,
                # because the party measured by the denominator can change it.
                notes.append(
                    f'BREAKING: {sub} declared depth narrowed L{cap} to L{now}; '
                    f'coverage must be reported against both denominators until '
                    f'they agree')
        prev_entities = previous.record_counts.get('entities', 0)
        if len(self.substrate.entities) < prev_entities:
            notes.append(
                f'BREAKING: entity count fell from {prev_entities} to '
                f'{len(self.substrate.entities)}; removals require tombstones')
        return (any(n.startswith('BREAKING') for n in notes), notes)

    # ---- publication ---------------------------------------------------

    def publish(self, release_id: str, out_dir: str, *,
                previous: Manifest | None = None,
                strict: bool = True) -> Manifest:
        """Publish atomically, or not at all.

        Every artifact is written and hash-verified before the manifest that
        names them is written last. A partially-published release would be
        permanent and unwithdrawable (BR-020), so the failure mode has to be
        "nothing published" rather than "some of it" (CH-07, FR-VER-012).
        """
        manifest = self.build(release_id, previous=previous, strict=strict)
        if not manifest.validation['passed']:
            raise ReleaseError(
                f'release {release_id} refused: validation failed with '
                f'{len(manifest.validation["errors"])} blocking error(s). '
                f'First: {(manifest.validation["errors"] or ["-"])[0]}')
        if not manifest.evaluations.get('all_bars_met', True):
            missed = [r['ev'] for r in manifest.evaluations['results']
                      if not r['met']]
            raise ReleaseError(
                f'release {release_id} refused: evaluation bars missed '
                f'({", ".join(missed)}). Safety bars are absolute '
                f'(FR-RETR-007).')
        target = os.path.join(out_dir, release_id)
        if os.path.exists(target):
            raise ReleaseError(
                f'release {release_id} already exists at {target}; published '
                f'releases are immutable and are superseded, never overwritten')

        staging = target + '.staging'
        os.makedirs(staging, exist_ok=True)
        artifacts: list[dict] = []
        try:
            blob = canonical_bytes(self.substrate)
            self._write_artifact(staging, 'substrate.json', blob, artifacts)
            cov = json.dumps(
                {'declared_depth': self.substrate.declared_depth}, **_JSON
            ).encode('utf-8')
            self._write_artifact(staging, 'coverage.json', cov, artifacts)
            manifest.artifacts = artifacts
            # Correspondence check before the manifest lands: every named
            # artifact present and hash-matched.
            for art in artifacts:
                path = os.path.join(staging, art['name'])
                if not os.path.isfile(path):
                    raise ReleaseError(
                        f'manifest names {art["name"]} but it is not present')
                with open(path, 'rb') as fh:
                    got = hashlib.sha256(fh.read()).hexdigest()
                if got != art['sha256']:
                    raise ReleaseError(
                        f'{art["name"]} hash mismatch: manifest {art["sha256"]}, '
                        f'artifact {got}')
            with open(os.path.join(staging, 'manifest.json'), 'w',
                      encoding='utf-8') as fh:
                json.dump(manifest.as_dict(), fh, indent=1, ensure_ascii=False)
            os.rename(staging, target)          # the atomic step
        except Exception:
            self._cleanup(staging)
            raise
        return manifest

    @staticmethod
    def _write_artifact(staging: str, name: str, blob: bytes,
                        artifacts: list[dict]) -> None:
        with open(os.path.join(staging, name), 'wb') as fh:
            fh.write(blob)
        artifacts.append({'name': name, 'bytes': len(blob),
                          'sha256': hashlib.sha256(blob).hexdigest()})

    @staticmethod
    def _cleanup(staging: str) -> None:
        if not os.path.isdir(staging):
            return
        for dirpath, _, filenames in os.walk(staging, topdown=False):
            for fn in filenames:
                os.remove(os.path.join(dirpath, fn))
            os.rmdir(dirpath)


def load_manifest(path: str) -> Manifest:
    with open(path, encoding='utf-8') as fh:
        d = json.load(fh)
    return Manifest(**d)


def verify_rebuild(substrate_root: str, manifest: Manifest) -> bool:
    """Rebuild from the substrate and compare hashes. Near-match is failure."""
    return content_hash(load(substrate_root)) == manifest.content_hash


def diff(a: Manifest, b: Manifest) -> dict:
    """Release-to-release diff (FR-VER-011).

    Class changes are reported separately from additions and removals, because a
    claim quietly changing grade is the interesting event and would otherwise
    hide inside a count.
    """
    return {
        'from': a.release_id, 'to': b.release_id,
        'record_delta': {k: b.record_counts.get(k, 0) - a.record_counts.get(k, 0)
                         for k in set(a.record_counts) | set(b.record_counts)},
        'minted_delta': b.minted_ids - a.minted_ids,
        'unknown_delta': {
            k: b.unknown_counts.get(k, 0) - a.unknown_counts.get(k, 0)
            for k in ('total', 'asked_for', 'unprompted')},
        'breaking': b.breaking, 'notes': b.notes,
        'content_hash_changed': a.content_hash != b.content_hash,
    }
