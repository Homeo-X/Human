"""Projection: what is in view, computed from the graph.

This is the module that makes "3D is a projection of the knowledge substrate"
a mechanism rather than a slogan. Given a `ViewState`, it computes a **view
specification**: which entities are in view at that ontological resolution,
what is known about where each one is, whether geometry exists for it, how the
in-view entities relate to each other, and what the evidence behind all of it
is. A renderer consumes that specification. It never queries the graph itself
and never decides what should be visible.

The inversion matters. In the usual arrangement a mesh is authored, a paragraph
is attached to it, and the model *is* the artwork — so anything without artwork
does not exist, and the ontology is decoration. Here the graph decides what is
in view and geometry is one optional attribute of an entity that is already
there. An entity with no mesh is projected as `described`, positioned by its
spatial identity, fully navigable (D-008). Nothing is invisible merely because
no one has modelled it yet.

Realizes: FR-NAV-007, FR-NAV-008, FR-SPAT-002, FR-SPAT-006.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .evidence import EvidenceService
from .graph import Graph
from .navigation import ViewState, encode
from .scale import ScaleService

# How an entity is available to a renderer. The distinction between the last
# two is the one that keeps the model honest: a structure nobody has modelled
# and a structure whose asset failed to load are different facts, and a viewer
# that renders both as an empty space teaches its users that the model is thin
# when it is the pipeline that is broken (FR-NAV-003 edge case).
DEPICTED = 'depicted'                  # geometry bound and available
DESCRIBED = 'described'                # spatial identity, no geometry authored
UNAVAILABLE = 'asset_unavailable'      # geometry declared, asset not resolvable
UNPLACED = 'unplaced'                  # no spatial identity at all


@dataclass(frozen=True)
class ProjectedEntity:
    """One entity as a renderer needs it — and no more than that."""
    entity: str
    label: str
    level: int | None
    entity_class: str
    subsystem: str
    compilation_status: str
    depiction: str
    position: str | None = None
    laterality: str | None = None
    coordinate_frame: str | None = None
    landmarks: tuple[str, ...] = ()
    geometry: tuple[dict, ...] = ()
    evidence_classes: tuple[str, ...] = ()
    weakest_class: str | None = None
    unknown_claims: int = 0
    review_state: str = 'provisional'
    address: str = ''
    note: str = ''

    def as_dict(self) -> dict:
        return {
            'entity': self.entity, 'label': self.label, 'level': self.level,
            'entity_class': self.entity_class, 'subsystem': self.subsystem,
            'compilation_status': self.compilation_status,
            'depiction': self.depiction, 'position': self.position,
            'laterality': self.laterality,
            'coordinate_frame': self.coordinate_frame,
            'landmarks': list(self.landmarks),
            'geometry': [dict(g) for g in self.geometry],
            'evidence_classes': list(self.evidence_classes),
            'weakest_class': self.weakest_class,
            'unknown_claims': self.unknown_claims,
            'review_state': self.review_state,
            'reviewed': self.review_state == 'reviewed',
            'address': self.address, 'note': self.note,
        }


@dataclass(frozen=True)
class Hidden:
    """What a filter removed, and why. Never a silent subtraction."""
    count: int
    by_filter: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {'count': self.count, 'by_filter': dict(self.by_filter)}


@dataclass(frozen=True)
class Projection:
    """The complete view specification for one state."""
    state: ViewState
    focus: ProjectedEntity | None
    entities: tuple[ProjectedEntity, ...]
    relations: tuple[dict, ...]
    lineage: tuple[dict, ...]
    hidden: Hidden
    depiction_summary: dict
    truncated: bool = False
    total_before_paging: int = 0
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {
            'state': self.state.as_dict(),
            'focus': self.focus.as_dict() if self.focus else None,
            'entities': [e.as_dict() for e in self.entities],
            'relations': [dict(r) for r in self.relations],
            'lineage': [dict(row) for row in self.lineage],
            'hidden': self.hidden.as_dict(),
            'depiction_summary': dict(self.depiction_summary),
            'truncated': self.truncated,
            'total_before_paging': self.total_before_paging,
            'notes': list(self.notes),
            'derivation': ('This view was computed from the knowledge graph. '
                           'Geometry is an attribute of an entity, not the '
                           'other way round: entities with no geometry are '
                           'present and positioned.'),
        }


class ProjectionService:
    """Derives view specifications. Renders nothing."""

    def __init__(self, graph: Graph, scale: ScaleService,
                 evidence: EvidenceService, page_size: int = 200):
        self.graph = graph
        self.scale = scale
        self.evidence = evidence
        self.page_size = page_size

    # ---- the projection ------------------------------------------------

    def project(self, state: ViewState, *, page_size: int | None = None
                ) -> Projection:
        """Compute what is in view for a state.

        The in-view set is the focus plus its immediate containment children,
        narrowed by isolation and by the layer filters. Whatever the filters
        remove is counted and reported rather than simply absent.
        """
        limit = page_size or self.page_size
        notes: list[str] = []
        focus_entity = self.graph.get(state.entity)
        if focus_entity is None:
            return Projection(
                state=state, focus=None, entities=(), relations=(),
                lineage=(), hidden=Hidden(0), depiction_summary={},
                notes=(f'{state.entity} is not in this release. Nothing is '
                       f'projected; this is a statement about the release, '
                       f'not about the anatomy.',))

        candidates, level_note = self._at_level(focus_entity, state.level)
        if level_note:
            notes.append(level_note)
        if state.isolated:
            allowed = set(state.isolated)
            removed = [c for c in candidates if c not in allowed]
            candidates = [c for c in candidates if c in allowed]
            if removed:
                notes.append(
                    f'Isolation is active: {len(removed)} structure(s) in this '
                    f'view are outside the isolated set. Isolation operates on '
                    f'entities and their contained parts, so it holds however '
                    f'geometry happens to be packaged. The focus is still '
                    f'reported even when it is itself outside the set, so a '
                    f'user never loses track of where they are.')

        kept, hidden_counts = self._apply_layers(candidates, state)
        total = len(kept)
        truncated = total > limit
        if truncated:
            notes.append(
                f'{total} entities are in view; the first {limit} are '
                f'returned. The full list is reachable by paging — it is not '
                f'the default because a level with thousands of entities is '
                f'not a view, it is a dump.')
            kept = kept[:limit]

        projected = tuple(self._project_entity(eid, state) for eid in kept)
        focus = next((p for p in projected if p.entity == state.entity), None)
        if focus is None:
            focus = self._project_entity(state.entity, state)

        summary: dict = {}
        for p in projected:
            summary[p.depiction] = summary.get(p.depiction, 0) + 1
        if summary.get(DESCRIBED) or summary.get(UNPLACED):
            notes.append(
                'Some structures in view have no geometry in this release. '
                'They are described and positioned rather than depicted; that '
                'is a statement about available assets, not about the body.')

        return Projection(
            state=state, focus=focus, entities=projected,
            relations=self._relations({p.entity for p in projected}),
            lineage=self._lineage(state),
            hidden=Hidden(sum(hidden_counts.values()), hidden_counts),
            depiction_summary=summary, truncated=truncated,
            total_before_paging=total, notes=tuple(notes))

    # ---- the in-view set at a requested resolution ----------------------

    def _at_level(self, focus, level: int) -> tuple[list[str], str]:
        """The entities in view at the requested ontological resolution.

        This is the operation the whole module is named for, and getting it
        wrong is easy in a way that is hard to notice: returning the focus and
        its immediate children regardless of the requested level produces a
        plausible view that silently ignores the level entirely. The first
        version of this method did exactly that, which made every claim about
        "the requested resolution" false.

        Three cases, all explicit:

        - at the focus's own level — the focus and what it directly holds;
        - deeper — the descendants that sit at the requested level, found by
          walking containment *and membership*, with the focus retained for
          orientation;
        - shallower — the ancestor at that level and what it holds.

        Membership is walked as well as containment because a system contains
        nothing: projecting the digestive system found no organs at all until
        the pancreas test made that visible (D-019).

        When nothing exists at the requested level the view says so and falls
        back to the focus alone. An empty view would be indistinguishable from
        a broken one.
        """
        here = focus.shallowest_level
        if here is None or level == here:
            return [focus.id] + list(self.graph.descendants(focus.id)), ''

        if level > here:
            found, frontier, seen = [], [focus.id], {focus.id}
            while frontier:
                nxt = []
                for eid in frontier:
                    for child in self.graph.descendants(eid):
                        if child in seen:
                            continue
                        seen.add(child)
                        entity = self.graph.get(child)
                        child_level = entity.shallowest_level if entity else None
                        if child_level == level:
                            found.append(child)
                        elif child_level is None or child_level < level:
                            nxt.append(child)
                frontier = nxt
            if not found:
                return [focus.id], (
                    f'Nothing is represented at L{level} beneath '
                    f'{focus.preferred_term} in this release. The focus is '
                    f'shown alone; that is a statement about the model, not '
                    f'about the anatomy — descend for the terminal answer.')
            return [focus.id] + sorted(found), (
                f'Showing L{level} content beneath {focus.preferred_term}. '
                f'The focus is retained for orientation and is at L{here}.')

        for ancestor_id in self.graph.lineage(focus.id):
            ancestor = self.graph.get(ancestor_id)
            if ancestor and ancestor.shallowest_level == level:
                return ([ancestor_id]
                        + list(self.graph.descendants(ancestor_id))), (
                    f'Ascended to L{level}: {ancestor.preferred_term}, which '
                    f'contains {focus.preferred_term}.')
        return [focus.id], (
            f'No ancestor of {focus.preferred_term} sits at L{level} in this '
            f'release, so the view could not ascend to it. The focus is shown '
            f'alone.')

    # ---- filters (FR-NAV-007) ------------------------------------------

    def _apply_layers(self, candidates: list[str],
                      state: ViewState) -> tuple[list[str], dict]:
        layers = state.layers
        counts: dict = {}
        if not layers.active:
            return candidates, counts

        kept: list[str] = []
        for eid in candidates:
            entity = self.graph.get(eid)
            if entity is None:
                continue
            if layers.systems and entity.subsystem not in layers.systems:
                counts['system'] = counts.get('system', 0) + 1
                continue
            if (layers.tissue_classes
                    and entity.entity_class not in layers.tissue_classes):
                counts['tissue_class'] = counts.get('tissue_class', 0) + 1
                continue
            if layers.evidence_classes:
                classes = {c.evidence_class
                           for c in self.evidence.claims_for(eid)}
                if not classes & layers.evidence_classes:
                    counts['evidence_class'] = (
                        counts.get('evidence_class', 0) + 1)
                    continue
            kept.append(eid)
        return kept, counts

    # ---- one entity ----------------------------------------------------

    def _project_entity(self, entity_id: str,
                        state: ViewState) -> ProjectedEntity:
        entity = self.graph.get(entity_id)
        si = self.graph.spatial_identity(entity_id)
        claims = self.evidence.claims_for(entity_id)
        classes = tuple(sorted({c.evidence_class for c in claims}))

        depiction, note = self._depiction(si)
        return ProjectedEntity(
            entity=entity_id,
            label=entity.preferred_term if entity else entity_id,
            level=entity.shallowest_level if entity else None,
            entity_class=entity.entity_class if entity else 'unknown',
            subsystem=entity.subsystem if entity else 'unknown',
            compilation_status=(entity.compilation_status if entity
                                else 'narrative'),
            depiction=depiction,
            position=si.anatomical_position if si else None,
            laterality=si.laterality if si else None,
            coordinate_frame=si.coordinate_frame if si else None,
            landmarks=si.landmarks if si else (),
            geometry=si.geometry if si else (),
            evidence_classes=classes,
            # The weakest class is reported, never an average: averaging a
            # measured claim with an inferred one produces a number describing
            # neither (CH-06).
            weakest_class=max(classes) if classes else None,
            unknown_claims=sum(1 for c in claims if c.is_unknown),
            review_state=(entity.review_state if entity else 'provisional'),
            address=encode(ViewState(
                entity=entity_id,
                level=(entity.shallowest_level if entity else state.level),
                release=state.release)),
            note=note)

    @staticmethod
    def _depiction(si) -> tuple[str, str]:
        if si is None:
            return UNPLACED, (
                'No spatial identity in this release: the model does not yet '
                'record where this is. It is still a real entity and still '
                'navigable.')
        if not si.geometry:
            return DESCRIBED, (
                'Described, not depicted: position and relations are known, no '
                'geometry has been authored.')
        missing = [g for g in si.geometry if not g.get('asset')]
        if missing:
            return UNAVAILABLE, (
                'Geometry is declared for this entity but the asset is not '
                'resolvable in this release. This is a pipeline failure, not '
                'an absence of anatomy.')
        return DEPICTED, ''

    # ---- relations among what is in view -------------------------------

    def _relations(self, in_view: set[str]) -> tuple[dict, ...]:
        """Edges whose endpoints are both on screen.

        Typed edges carry their type; untyped associations are included and
        labelled, so a renderer drawing a line between two structures can say
        whether the line means a mechanism or a co-occurrence.
        """
        rows = []
        for rel in self.graph.substrate.relationships:
            if rel.source in in_view and rel.target in in_view:
                rows.append({
                    'id': rel.id, 'source': rel.source, 'target': rel.target,
                    'type': rel.type,
                    'untyped': rel.is_untyped_association,
                    'note': ('Records that a relationship exists, not what '
                             'kind. Do not render as a mechanism.')
                    if rel.is_untyped_association else None})
        return tuple(sorted(rows, key=lambda r: r['id']))

    def _lineage(self, state: ViewState) -> tuple[dict, ...]:
        rows = []
        for eid in reversed(self.graph.lineage(state.entity)):
            entity = self.graph.get(eid)
            rows.append({
                'entity': eid,
                'label': entity.preferred_term if entity else eid,
                'level': entity.shallowest_level if entity else None})
        return tuple(rows)
