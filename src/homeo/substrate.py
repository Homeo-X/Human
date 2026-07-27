"""Substrate loading and typed records.

Files are the canonical serialization (TECH_Data_Design §Storage Overview); this
module parses them into typed records. Nothing here derives or infers — a value
absent from the substrate is absent here, because inventing a default is how a
model acquires facts nobody asserted.

Realizes: FR-ONTO-001, FR-ONTO-006, FR-EVID-001, FR-PHYS-001, FR-SPAT-001.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

# D-007 compilation ladder. Order is meaningful: promotion is forward-only and
# a mechanistic claim may not rest on a narrative endpoint (INV-15).
COMPILATION_ORDER = ('narrative', 'structured', 'mechanistic', 'parameterized')
REPRESENTATION_ORDER = ('narrative', 'structured', 'parameterized', 'executable')

# BIO_Evidence_and_Provenance §Evidence Classes. UNKNOWN is a first-class,
# asserted value, not the absence of one.
EVIDENCE_CLASSES = {
    'EVC-1': 'VERIFIED',
    'EVC-2': 'STRONGLY_SUPPORTED',
    'EVC-3': 'MODELLED',
    'EVC-4': 'APPROXIMATED',
    'EVC-5': 'INFERRED',
    'EVC-6': 'HYPOTHESIZED',
    'EVC-7': 'CONFLICTING_EVIDENCE',
    'EVC-8': 'UNKNOWN',
}
UNKNOWN = 'EVC-8'

# Relations that describe structure rather than causation. The distinction
# matters in two places: the level-skip rule (biocheck INV-05) and the
# navigation tree, which is built from containment alone (D-006).
STRUCTURAL_RELATIONS = frozenset({
    'part_of', 'member_of', 'located_in', 'adjacent_to',
    'connected_to', 'composed_of', 'participates_in',
})
CONTAINMENT = 'part_of'
MEMBERSHIP = 'member_of'

# Inverses, per BIO_Anatomical_Ontology §Relationship Types (FR-REL-002).
INVERSES = {
    'part_of': 'has_part', 'member_of': 'has_member', 'located_in': 'location_of',
    'adjacent_to': 'adjacent_to', 'connected_to': 'connected_to',
    'composed_of': 'constitutes', 'innervated_by': 'innervates',
    'vascularized_by': 'vascularizes', 'drained_by': 'drains',
    'produces': 'produced_by', 'consumes': 'consumed_by',
    'transports': 'transported_by', 'converts': 'converted_by',
    'responds_to': 'signals_to', 'regulated_by': 'regulates',
    'activates': 'activated_by', 'inhibits': 'inhibited_by',
    'differentiates_into': 'differentiates_from',
    'originates_from': 'gives_rise_to', 'realizes': 'realized_by',
    'participates_in': 'has_participant', 'causes': 'caused_by',
    'contributes_to': 'contributed_to_by', 'associated_with': 'associated_with',
}


class SubstrateError(Exception):
    """Raised when the substrate cannot be loaded. Never raised for content the
    substrate legitimately does not hold — that is an answer, not an error."""


@dataclass(frozen=True)
class Entity:
    id: str
    entity_class: str
    subsystem: str
    preferred_term: str
    compilation_status: str
    minted: bool = False
    minted_reason: str | None = None
    level: int | None = None
    spatial_scale: tuple[int, ...] = ()
    level_contributions: dict[str, str] = field(default_factory=dict)
    representation_mode: str | None = None
    synonyms: tuple[dict, ...] = ()
    xrefs: tuple[dict, ...] = ()
    part_of: str | None = None
    variant_of: str | None = None
    promotion_blocked: bool = False
    provenance_source: str | None = None
    retired_at: str | None = None
    successor_id: str | None = None

    @property
    def is_spanning(self) -> bool:
        """A process acting across several levels rather than sitting at one."""
        return bool(self.spatial_scale)

    @property
    def levels(self) -> tuple[int, ...]:
        return self.spatial_scale if self.is_spanning else (
            () if self.level is None else (self.level,))

    @property
    def shallowest_level(self) -> int | None:
        ls = self.levels
        return min(ls) if ls else None

    @property
    def is_retired(self) -> bool:
        return self.retired_at is not None

    @property
    def compilation_rank(self) -> int:
        try:
            return COMPILATION_ORDER.index(self.compilation_status)
        except ValueError:
            return 0


@dataclass(frozen=True)
class Claim:
    id: str
    subject: str
    predicate: str
    object: Any
    evidence_class: str
    source_type: str
    species: str
    population: str
    date_asserted: str
    limitations: str
    assigned_by: str
    unit: str | None = None
    sources: tuple[dict, ...] = ()
    transfer_justification: str | None = None
    conditions: dict = field(default_factory=dict)
    conflicts_with: tuple[str, ...] = ()
    provenance_source: str | None = None
    prompted_by: str | None = None

    @property
    def is_unknown(self) -> bool:
        return self.evidence_class == UNKNOWN

    @property
    def class_name(self) -> str:
        return EVIDENCE_CLASSES.get(self.evidence_class, 'UNRECOGNISED')

    @property
    def is_cross_species(self) -> bool:
        return self.species not in ('Homo sapiens', 'not applicable')


@dataclass(frozen=True)
class Relationship:
    id: str
    source: str
    target: str
    type: str
    provenance_claim: str
    compilation_status: str = 'narrative'
    skip_justification: str | None = None
    prose_justification: str | None = None
    provenance_source: str | None = None

    @property
    def is_untyped_association(self) -> bool:
        """The corpus told us a relationship exists, not what kind (D-007).

        Callers must never render or describe these as mechanisms (BRB-30).
        """
        return self.type == 'associated_with'

    @property
    def is_structural(self) -> bool:
        return self.type in STRUCTURAL_RELATIONS

    @property
    def inverse_type(self) -> str:
        return INVERSES.get(self.type, f'inverse_of_{self.type}')


@dataclass(frozen=True)
class ScaleContract:
    id: str
    level: int
    represents: str
    representation_mode: tuple[str, ...]
    data_model: str
    spatial_model: str
    functional_model: str
    evidence_model: str
    uncertainty_model: str
    computational_cost: str
    resolution_limit: str


@dataclass(frozen=True)
class Process:
    id: str
    label: str
    subsystem: str
    spatial_scale: tuple[int, ...]
    timescale_domain: str
    representation_status: str
    evidence_class: str
    level_contributions: dict[str, str] = field(default_factory=dict)
    characteristic_duration: dict = field(default_factory=dict)
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    participants: tuple[str, ...] = ()
    state_variables: tuple[dict, ...] = ()
    mechanism: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    feedback_loops: tuple[dict, ...] = ()
    failure_states: tuple[dict, ...] = ()
    limitations: str = ''
    provenance_source: str | None = None

    @property
    def is_executable(self) -> bool:
        return self.representation_status == 'executable'


@dataclass(frozen=True)
class SpatialIdentity:
    """Where an entity is, independent of any geometry (D-008).

    Exists for entities with no mesh at all, which is what makes the model
    navigable and screen-reader-traversable before any art exists.
    """
    id: str
    entity: str
    coordinate_frame: str
    anatomical_position: str | None = None
    laterality: str | None = None
    contained_in: str | None = None
    adjacent_to: tuple[str, ...] = ()
    landmarks: tuple[str, ...] = ()
    geometry: tuple[dict, ...] = ()

    @property
    def has_geometry(self) -> bool:
        return bool(self.geometry)


def _tup(v):
    return tuple(v) if isinstance(v, (list, tuple)) else ()


def _entity(d: dict) -> Entity:
    return Entity(
        id=d['id'], entity_class=d['entity_class'], subsystem=d['subsystem'],
        preferred_term=d['preferred_term'], compilation_status=d['compilation_status'],
        minted=d.get('minted', False), minted_reason=d.get('minted_reason'),
        level=d.get('level'), spatial_scale=_tup(d.get('spatial_scale')),
        level_contributions=d.get('level_contributions', {}),
        representation_mode=d.get('representation_mode'),
        synonyms=_tup(d.get('synonyms')), xrefs=_tup(d.get('xrefs')),
        part_of=d.get('part_of'), variant_of=d.get('variant_of'),
        promotion_blocked=d.get('promotion_blocked', False),
        provenance_source=d.get('provenance_source'),
        retired_at=d.get('retired_at'), successor_id=d.get('successor_id'))


def _claim(d: dict) -> Claim:
    return Claim(
        id=d['id'], subject=d['subject'], predicate=d['predicate'], object=d['object'],
        evidence_class=d['evidence_class'], source_type=d['source_type'],
        species=d['species'], population=d['population'],
        date_asserted=d['date_asserted'], limitations=d['limitations'],
        assigned_by=d['assigned_by'], unit=d.get('unit'),
        sources=_tup(d.get('sources')),
        transfer_justification=d.get('transfer_justification'),
        conditions=d.get('conditions', {}),
        conflicts_with=_tup(d.get('conflicts_with')),
        provenance_source=d.get('provenance_source'),
        prompted_by=d.get('prompted_by'))


def _relationship(d: dict) -> Relationship:
    return Relationship(
        id=d['id'], source=d['source'], target=d['target'], type=d['type'],
        provenance_claim=d['provenance_claim'],
        compilation_status=d.get('compilation_status', 'narrative'),
        skip_justification=d.get('skip_justification'),
        prose_justification=d.get('prose_justification'),
        provenance_source=d.get('provenance_source'))


def _scale(d: dict) -> ScaleContract:
    return ScaleContract(
        id=d['id'], level=d['level'], represents=d['represents'],
        representation_mode=_tup(d['representation_mode']),
        data_model=d['data_model'], spatial_model=d['spatial_model'],
        functional_model=d['functional_model'], evidence_model=d['evidence_model'],
        uncertainty_model=d['uncertainty_model'],
        computational_cost=d['computational_cost'],
        resolution_limit=d['resolution_limit'])


def _process(d: dict) -> Process:
    return Process(
        id=d['id'], label=d['label'], subsystem=d['subsystem'],
        spatial_scale=_tup(d['spatial_scale']), timescale_domain=d['timescale_domain'],
        representation_status=d['representation_status'],
        evidence_class=d['evidence_class'],
        level_contributions=d.get('level_contributions', {}),
        characteristic_duration=d.get('characteristic_duration', {}),
        inputs=_tup(d.get('inputs')), outputs=_tup(d.get('outputs')),
        participants=_tup(d.get('participants')),
        state_variables=_tup(d.get('state_variables')),
        mechanism=_tup(d.get('mechanism')), depends_on=_tup(d.get('depends_on')),
        feedback_loops=_tup(d.get('feedback_loops')),
        failure_states=_tup(d.get('failure_states')),
        limitations=d.get('limitations', ''),
        provenance_source=d.get('provenance_source'))


def _spatial(d: dict) -> SpatialIdentity:
    return SpatialIdentity(
        id=d['id'], entity=d['entity'], coordinate_frame=d['coordinate_frame'],
        anatomical_position=d.get('anatomical_position'),
        laterality=d.get('laterality'), contained_in=d.get('contained_in'),
        adjacent_to=_tup(d.get('adjacent_to')), landmarks=_tup(d.get('landmarks')),
        geometry=_tup(d.get('geometry')))


@dataclass
class Substrate:
    """Everything the substrate holds, typed. The unit a release is built from."""
    entities: list[Entity] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    processes: list[Process] = field(default_factory=list)
    spatial_identities: list[SpatialIdentity] = field(default_factory=list)
    scale_contracts: list[ScaleContract] = field(default_factory=list)
    declared_depth: dict[str, int] = field(default_factory=dict)
    authorities: list[str] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)

    def record_count(self) -> int:
        return (len(self.entities) + len(self.claims) + len(self.relationships)
                + len(self.processes) + len(self.spatial_identities)
                + len(self.scale_contracts))


_PARSERS = {
    'entities': (_entity, 'entities'),
    'claims': (_claim, 'claims'),
    'relationships': (_relationship, 'relationships'),
    'processes': (_process, 'processes'),
    'spatial_identities': (_spatial, 'spatial_identities'),
    'scale_contracts': (_scale, 'scale_contracts'),
}


def load(root: str) -> Substrate:
    """Read every JSON file under root into a typed Substrate.

    File *names* carry the record type, matching the layout in TECH_Data_Design.
    An unrecognised filename is ignored rather than guessed at.
    """
    if not os.path.isdir(root):
        raise SubstrateError(f'not a directory: {root}')
    sub = Substrate()
    for dirpath, _, filenames in os.walk(root):
        for fn in sorted(filenames):
            if not fn.endswith('.json'):
                continue
            path = os.path.join(dirpath, fn)
            stem = fn[:-5]
            try:
                with open(path, encoding='utf-8') as fh:
                    payload = json.load(fh)
            except (OSError, ValueError) as exc:
                raise SubstrateError(f'{path}: {exc}') from exc
            sub.source_files.append(path)
            if stem in _PARSERS:
                parse, attr = _PARSERS[stem]
                rows = payload if isinstance(payload, list) else [payload]
                try:
                    getattr(sub, attr).extend(parse(r) for r in rows)
                except KeyError as exc:
                    raise SubstrateError(
                        f'{path}: record missing required field {exc}') from exc
            elif stem == 'declared_depth':
                sub.declared_depth.update(payload)
            elif stem == 'authorities':
                sub.authorities.extend(payload)
    sub.source_files.sort()
    return sub
