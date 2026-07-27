"""Navigation: view state, semantic zoom, and addressing.

The distinction this module exists to enforce is the project's central idea:
**semantic zoom is a change of ontological resolution, not a change of
magnification.** Moving from the heart to the myocardium is a different claim
about what the model represents; moving the camera closer is not a claim at all.
Interfaces conflate the two constantly, and the conflation is what makes a
zoomable anatomy app feel like a microscope that never actually resolves
anything. Here they are different operations on different fields, and
magnifying cannot change a level even by accident (FR-NAV-001).

Nothing in this module renders. It computes what a view *is* — the state, its
address, its history — leaving the drawing to whatever surface eventually
consumes it. That separation is what lets the navigation model be tested,
shared, and replayed with no viewer in existence (D-011 keeps the viewer gated;
the state model underneath it is not gated and is needed either way).

Realizes: FR-NAV-001, FR-NAV-004 … FR-NAV-011.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from urllib.parse import quote, unquote

from .evidence import EvidenceService
from .graph import EntityRetired, Graph
from .scale import LevelTransition, ScaleService

ADDRESS_SCHEME = 'homeo'
ADDRESS_VERSION = 1

# Magnification is bounded by what the asset actually resolves, not by what the
# renderer will happily interpolate. Past the limit the view stops and says so,
# rather than presenting polygon detail as anatomy (FR-NAV-001 edge case).
DEFAULT_MAGNIFICATION_LIMIT = 16.0

# The scale contract's range (BIO_Scale_Contract SCL-00 … SCL-10). An address
# outside it is malformed input, not a request the model must answer.
MIN_LEVEL, MAX_LEVEL = 0, 10


class AddressError(Exception):
    """An address that cannot be parsed. Distinct from one that parses and then
    resolves to a retired entity — that is an answer, not an error."""


@dataclass(frozen=True)
class Layers:
    """What is shown, and — equally — what is hidden and how much of it.

    A filter that silently removes content is indistinguishable from a model
    that never had it. Every projection through these filters reports the count
    it removed (FR-NAV-007).
    """
    systems: frozenset[str] = frozenset()
    tissue_classes: frozenset[str] = frozenset()
    evidence_classes: frozenset[str] = frozenset()

    @property
    def active(self) -> bool:
        return bool(self.systems or self.tissue_classes
                    or self.evidence_classes)

    def as_dict(self) -> dict:
        return {'systems': sorted(self.systems),
                'tissue_classes': sorted(self.tissue_classes),
                'evidence_classes': sorted(self.evidence_classes)}


@dataclass(frozen=True)
class ViewState:
    """`{entity, level, camera, layers, isolation, section}` per the module's
    States & Transitions section.

    Frozen: every navigation operation returns a new state. History is then a
    list of values rather than a log of mutations, which is what makes `back`
    and the replayable teaching path trivially correct.
    """
    entity: str
    level: int
    magnification: float = 1.0
    layers: Layers = field(default_factory=Layers)
    isolated: tuple[str, ...] = ()
    section: str | None = None
    release: str = 'unpinned'

    def as_dict(self) -> dict:
        return {'entity': self.entity, 'level': self.level,
                'magnification': self.magnification,
                'layers': self.layers.as_dict(),
                'isolated': list(self.isolated), 'section': self.section,
                'release': self.release}


@dataclass(frozen=True)
class ZoomResult:
    """The answer to "did that change what the model claims?" — always stated.

    `semantic_change` is False for every physical zoom and True for every level
    change, and the two operations are separate calls. A surface that binds a
    scroll wheel to `magnify` cannot accidentally reach `set_level`.
    """
    state: ViewState
    semantic_change: bool
    claim_unchanged: bool
    transition: LevelTransition | None = None
    at_limit: bool = False
    note: str = ''

    def as_dict(self) -> dict:
        return {'state': self.state.as_dict(),
                'semantic_change': self.semantic_change,
                'claim_unchanged': self.claim_unchanged,
                'transition': (self.transition.as_dict() if self.transition
                               else None),
                'at_limit': self.at_limit, 'note': self.note}


@dataclass(frozen=True)
class Restoration:
    """The result of decoding an address.

    A restoration can succeed while telling the caller that the world moved:
    the entity was retired, or the address was minted against a different
    release. Neither is an error and neither is silently applied.
    """
    state: ViewState
    restored: bool
    entity_moved: bool = False
    tombstone: dict | None = None
    release_offered: str | None = None
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {'state': self.state.as_dict(), 'restored': self.restored,
                'entity_moved': self.entity_moved, 'tombstone': self.tombstone,
                'release_offered': self.release_offered,
                'notes': list(self.notes)}


def encode(state: ViewState) -> str:
    """Serialize a view state to a stable, inspectable address.

    Deterministic key order, so the same state always produces the same string
    and an address can be compared, cached, and diffed. Readable on purpose: an
    educator sharing a link should be able to see that it points at the left
    ventricle at L4 without decoding anything.
    """
    parts = [f'v={ADDRESS_VERSION}', f'rel={quote(state.release, safe="")}',
             f'e={quote(state.entity, safe="")}', f'l={state.level}']
    if state.magnification != 1.0:
        parts.append(f'm={state.magnification:g}')
    # Every value is escaped, including the layer members. A subsystem or
    # tissue-class name containing a comma would otherwise split into two
    # filters on decode — silently, and in the direction of hiding more content
    # than the user asked to hide.
    if state.layers.systems:
        parts.append('sys=' + _join(state.layers.systems))
    if state.layers.tissue_classes:
        parts.append('tis=' + _join(state.layers.tissue_classes))
    if state.layers.evidence_classes:
        parts.append('evc=' + _join(state.layers.evidence_classes))
    if state.isolated:
        parts.append('iso=' + _join(state.isolated))
    if state.section:
        parts.append(f'sec={quote(state.section, safe="")}')
    return f'{ADDRESS_SCHEME}:' + '&'.join(parts)


def _join(values) -> str:
    return ','.join(quote(v, safe='') for v in sorted(values))


def _parse(address: str) -> dict:
    """Parse an address. An address is untrusted input, not a serialization.

    It arrives from a URL bar, a shared link, or a saved bookmark, so every
    field is validated here rather than trusted because `encode` produced a
    well-formed one. The magnification limit in particular is a claim about
    what the assets resolve; a limit enforced only on the `magnify` path would
    be bypassable by editing a link, which is precisely the surface where the
    overclaim would be seen.
    """
    if not address.startswith(ADDRESS_SCHEME + ':'):
        raise AddressError(
            f'not a {ADDRESS_SCHEME} address: {address[:40]!r}')
    # Split without decoding. `parse_qsl` would percent-decode each value
    # before the comma-separated members are split apart, so an escaped comma
    # inside a member would decode first and then split — turning one filter
    # into two. Decoding happens per member, after the split, at the use site.
    fields = {}
    for chunk in address[len(ADDRESS_SCHEME) + 1:].split('&'):
        if not chunk:
            continue
        key, sep, value = chunk.partition('=')
        if not sep:
            raise AddressError(f'malformed address field: {chunk[:40]!r}')
        fields[key] = value
    if 'e' not in fields or 'l' not in fields:
        raise AddressError('address must carry an entity (e) and a level (l)')
    try:
        level = int(fields['l'])
    except ValueError:
        raise AddressError(f'level is not an integer: {fields["l"]!r}') from None
    if not MIN_LEVEL <= level <= MAX_LEVEL:
        raise AddressError(
            f'L{level} is not a level in this model: the scale contract runs '
            f'L{MIN_LEVEL} to L{MAX_LEVEL} (BIO_Scale_Contract). This is a '
            f'malformed address, not a limit of the model')
    if 'm' in fields:
        try:
            magnification = float(fields['m'])
        except ValueError:
            raise AddressError(
                f'magnification is not a number: {fields["m"]!r}') from None
        if magnification <= 0:
            raise AddressError('magnification must be positive')
    return fields


class NavigationService:
    """Navigation over a pinned release."""

    def __init__(self, graph: Graph, scale: ScaleService,
                 evidence: EvidenceService | None = None,
                 release: str = 'unpinned',
                 magnification_limit: float = DEFAULT_MAGNIFICATION_LIMIT):
        self.graph = graph
        self.scale = scale
        self.evidence = evidence
        self.release = release
        self.magnification_limit = magnification_limit

    # ---- entering ------------------------------------------------------

    def enter(self, ref: str, **kwargs) -> ViewState:
        """Open a view on an entity at its own level."""
        entity = self.graph.resolve(ref)
        return ViewState(entity=entity.id,
                         level=entity.shallowest_level or 0,
                         release=self.release, **kwargs)

    # ---- physical zoom (FR-NAV-001) ------------------------------------

    def magnify(self, state: ViewState, factor: float) -> ZoomResult:
        """Change magnification. Changes nothing the model claims.

        Deliberately incapable of changing `level`: the returned state is the
        old one with a different camera. This is the whole of FR-NAV-001 on the
        physical side, and it is enforced by construction rather than by a rule
        someone has to remember.
        """
        if factor <= 0:
            raise ValueError('magnification must be positive')
        target = state.magnification * factor
        at_limit = target > self.magnification_limit
        applied = min(target, self.magnification_limit)
        note = ''
        if at_limit:
            note = (f'Magnification stops at {self.magnification_limit:g}x, '
                    f'the resolution limit of the assets in this release. '
                    f'Beyond it the renderer would show polygon detail, which '
                    f'is not anatomy.')
        return ZoomResult(state=replace(state, magnification=applied),
                          semantic_change=False, claim_unchanged=True,
                          at_limit=at_limit, note=note)

    # ---- semantic zoom (FR-NAV-001, FR-NAV-002) ------------------------

    def set_level(self, state: ViewState, level: int) -> ZoomResult:
        """Change ontological resolution. Always explicit, always announced.

        Magnification is carried through untouched — the two axes are
        independent, which is the point.
        """
        if level == state.level:
            return ZoomResult(state=state, semantic_change=False,
                              claim_unchanged=True,
                              note='Already at this level.')
        transition = self.scale.transition(level, from_level=state.level)
        return ZoomResult(state=replace(state, level=level),
                          semantic_change=True, claim_unchanged=False,
                          transition=transition,
                          note=('The model now represents different things. '
                                'This is a change of what is described, not of '
                                'how closely it is viewed.'))

    def descend(self, state: ViewState):
        """One level down, or the terminal answer (FR-NAV-003).

        Delegates the terminal case to the scale service rather than
        reimplementing it, so there is exactly one wording of "not represented"
        in the system.
        """
        result = self.scale.descend(state.entity)
        if not isinstance(result, list):
            return result                       # TerminalAnswer, a real view
        return [self.enter(child) for child in result]

    # ---- layers (FR-NAV-007) -------------------------------------------

    def with_layers(self, state: ViewState, *, systems=None,
                    tissue_classes=None, evidence_classes=None) -> ViewState:
        layers = Layers(
            systems=frozenset(systems if systems is not None
                              else state.layers.systems),
            tissue_classes=frozenset(tissue_classes if tissue_classes is not None
                                     else state.layers.tissue_classes),
            evidence_classes=frozenset(evidence_classes
                                       if evidence_classes is not None
                                       else state.layers.evidence_classes))
        return replace(state, layers=layers)

    # ---- isolation and sectioning (FR-NAV-008) -------------------------

    def isolate(self, state: ViewState, ref: str) -> ViewState:
        """Isolate an entity and everything contained in it.

        Entity-based, not mesh-based: isolating the left ventricle isolates the
        myocardium within it whether the artist shipped them as one mesh, two,
        or none at all. Behaviour that depended on asset packaging would be
        behaviour nobody could reason about.
        """
        entity = self.graph.resolve(ref)
        return replace(state, isolated=tuple(self._containment_closure(
            entity.id)))

    def _containment_closure(self, entity_id: str) -> list[str]:
        out, stack = [], [entity_id]
        seen = set()
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            out.append(current)
            stack.extend(self.graph.children(current))
        return sorted(out)

    def section(self, state: ViewState, plane: str) -> dict:
        """Apply a cut plane, and report honestly what can be said about it.

        **Crossing is not computable in this release.** Determining which
        structures a plane intersects requires geometry, and no entity in this
        substrate has any. What is returned is therefore the set of *candidate*
        entities — those with a spatial identity, which is the population a
        crossing test would be run against — explicitly marked
        `crossing: not_computable`.

        This method previously returned that same list under the word
        `crosses`, for any plane string including nonsense, which asserted a
        computed intersection that had never been computed. Naming the limit is
        the whole posture of this project (BRB-01); a plausible-looking answer
        derived from nothing is worse than a refusal.
        """
        candidates = []
        for si in self.graph.substrate.spatial_identities:
            entity = self.graph.get(si.entity)
            if entity is None or entity.is_retired:
                continue
            candidates.append({
                'entity': si.entity,
                'label': entity.preferred_term,
                'has_geometry': si.has_geometry,
                'position': si.anatomical_position,
                'laterality': si.laterality,
                'crossing': 'not_computable'})
        with_geometry = sum(1 for c in candidates if c['has_geometry'])
        return {
            'state': replace(state, section=plane).as_dict(),
            'plane': plane,
            'crossing_computed': False,
            'candidates': sorted(candidates, key=lambda c: c['entity']),
            'candidates_with_geometry': with_geometry,
            'statement': (
                f'A cut plane was recorded on the view state, but which '
                f'entities {plane!r} crosses cannot be determined in this '
                f'release: {with_geometry} of {len(candidates)} entities with '
                f'a spatial identity have geometry. The list returned is the '
                f'candidate population a crossing test would run against, not '
                f'a result. Sectioning operates on entities rather than meshes '
                f'(FR-NAV-008), so this becomes computable when geometry binds '
                f'in Phase 1 — the semantics do not change with it.'),
        }

    # ---- graph navigation alongside the tree (FR-NAV-009) --------------

    def follow(self, state: ViewState, relation: str) -> dict:
        """Traverse a typed relation, carrying the type into the answer.

        An untyped `associated_with` edge is traversable and is labelled as
        untyped, so a user can feel the difference between a mechanism and a
        co-occurrence (FR-REL-007's discipline, surfaced in navigation).
        """
        edges = [e for e in self.graph.edges(state.entity)
                 if e.type == relation]
        targets = []
        for edge in edges:
            other = self.graph.get(edge.other)
            targets.append({
                'entity': edge.other,
                'label': other.preferred_term if other else edge.other,
                'relation': edge.type,
                'direction': 'outbound' if edge.outbound else 'inbound',
                'untyped': edge.type == 'associated_with',
                'note': ('This edge records that a relationship exists, not '
                         'what kind. It is not a mechanism.')
                if edge.type == 'associated_with' else None})
        return {'from': state.entity, 'relation': relation,
                'targets': targets, 'count': len(targets)}

    # ---- lineage (FR-NAV-010) ------------------------------------------

    def context(self, state: ViewState) -> dict:
        """The parent chain, each ancestor one action away."""
        chain = []
        for eid in self.graph.lineage(state.entity):
            entity = self.graph.get(eid)
            chain.append({
                'entity': eid,
                'label': entity.preferred_term if entity else eid,
                'level': entity.shallowest_level if entity else None,
                'address': encode(replace(
                    state, entity=eid,
                    level=(entity.shallowest_level if entity else state.level)))})
        return {'entity': state.entity, 'lineage': list(reversed(chain)),
                'depth': len(chain)}

    # ---- addressing (FR-NAV-006) ---------------------------------------

    def restore(self, address: str) -> Restoration:
        """Decode an address against this release.

        Three things can be true at once and all three are reported: the state
        restored, the entity moved, and the address was minted against another
        release. The session keeps its pinned release; a newer one is *offered*,
        never applied under a user who is mid-session.
        """
        fields = _parse(address)
        notes: list[str] = []
        moved, tombstone = False, None

        ref = unquote(fields['e'])
        try:
            entity = self.graph.resolve(ref)
            entity_id = entity.id
            level = int(fields['l'])
        except EntityRetired as exc:
            moved = True
            tombstone = {'requested': ref, 'retired_at': exc.retired_at,
                         'successor': exc.successor}
            if exc.successor is None:
                notes.append(
                    f'{ref} was retired on {exc.retired_at} with no successor. '
                    f'The address is historically valid; the entity is not in '
                    f'this release.')
                return Restoration(
                    state=ViewState(entity=ref, level=int(fields['l']),
                                    release=self.release),
                    restored=False, entity_moved=True, tombstone=tombstone,
                    notes=tuple(notes))
            successor = self.graph.get(exc.successor)
            entity_id = exc.successor
            level = (successor.shallowest_level if successor
                     else int(fields['l']))
            notes.append(
                f'{ref} was retired on {exc.retired_at} and is succeeded by '
                f'{exc.successor}. The view was restored on the successor.')
        except KeyError:
            raise AddressError(
                f'{ref} is not an entity, xref, or synonym in this '
                f'release') from None

        offered = None
        minted_for = unquote(fields.get('rel', self.release))
        if minted_for != self.release:
            offered = self.release
            notes.append(
                f'This address was minted against release {minted_for}; the '
                f'session is pinned to {self.release}. The pinned release '
                f'answered. Switching is offered, never applied mid-session.')

        requested = float(fields.get('m', 1.0))
        magnification = min(requested, self.magnification_limit)
        if magnification != requested:
            notes.append(
                f'The address requested {requested:g}x magnification; it was '
                f'clamped to the {self.magnification_limit:g}x resolution '
                f'limit of this release\'s assets. The limit is a property of '
                f'the assets, so a hand-edited link does not raise it.')

        state = ViewState(
            entity=entity_id, level=level,
            magnification=magnification,
            layers=Layers(
                systems=frozenset(unquote(v) for v in _csv(fields.get('sys'))),
                tissue_classes=frozenset(
                    unquote(v) for v in _csv(fields.get('tis'))),
                evidence_classes=frozenset(
                    unquote(v) for v in _csv(fields.get('evc')))),
            isolated=tuple(unquote(i) for i in _csv(fields.get('iso'))),
            section=unquote(fields['sec']) if fields.get('sec') else None,
            release=self.release)
        return Restoration(state=state, restored=True, entity_moved=moved,
                           tombstone=tombstone, release_offered=offered,
                           notes=tuple(notes))


def _csv(value: str | None) -> list[str]:
    return [p for p in (value or '').split(',') if p]


@dataclass
class NavigationSession:
    """A user's path through the model, pinned to one release.

    History is a list of whole states, so `back` restores exactly what was
    there rather than attempting to invert an operation. Export produces
    addresses, which is what makes a teaching path replayable by anyone
    (FR-NAV-011).
    """
    service: NavigationService
    history: list[ViewState] = field(default_factory=list)

    @property
    def current(self) -> ViewState | None:
        return self.history[-1] if self.history else None

    def go(self, state: ViewState) -> ViewState:
        self.history.append(state)
        return state

    def back(self) -> ViewState | None:
        """Return to the previous state. Exploring is not punished."""
        if len(self.history) < 2:
            return self.current
        self.history.pop()
        return self.current

    def address(self) -> str:
        if self.current is None:
            raise ValueError('an empty session has no address')
        return encode(self.current)

    def export_path(self, title: str = '') -> dict:
        """A replayable sequence, for an educator who built one by exploring."""
        return {
            'title': title or 'Untitled path',
            'release': self.service.release,
            'steps': [{'address': encode(s), 'entity': s.entity,
                       'level': s.level} for s in self.history],
            'note': ('Replaying this path against a different release may land '
                     'on successors or on entities that no longer exist. Each '
                     'step reports that when it happens.'),
        }

    def replay(self, path: dict) -> list[Restoration]:
        """Replay an exported path, reporting each step honestly."""
        return [self.service.restore(step['address'])
                for step in path.get('steps', [])]
