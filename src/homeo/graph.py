"""The knowledge graph: resolution, typed traversal, and the derived tree.

The graph is canonical; the navigation tree is a view computed from containment
edges (D-006). That asymmetry is enforced here rather than merely documented: the
tree has no persistent representation and no write path, so it cannot be edited
into disagreement with the graph.

Realizes: FR-ONTO-001, FR-ONTO-004, FR-ONTO-006, FR-REL-001, FR-REL-002,
FR-REL-003, FR-REL-006, FR-REL-009, FR-REL-010, FR-NAV-004, FR-NAV-005.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from .substrate import (CONTAINMENT, MEMBERSHIP, Entity, Relationship, Substrate,
                        SpatialIdentity)

DEFAULT_TRAVERSAL_LIMIT = 4


class EntityRetired(Exception):
    """A retired identifier resolved. Carries its successor so the caller can
    answer "this moved" rather than "this is broken" (FR-ONTO-004)."""

    def __init__(self, entity_id: str, successor: str | None, retired_at: str):
        self.entity_id = entity_id
        self.successor = successor
        self.retired_at = retired_at
        super().__init__(f'{entity_id} retired {retired_at}'
                         + (f', succeeded by {successor}' if successor else
                            ', no successor'))


@dataclass(frozen=True)
class Edge:
    """A traversed edge, oriented from the entity the caller asked about.

    `outbound` records which way the stored edge pointed, so a caller can tell
    "the heart produces X" from "X is produced by the heart" without re-reading
    the substrate.
    """
    relation: Relationship
    other: str
    outbound: bool

    @property
    def type(self) -> str:
        return self.relation.type if self.outbound else self.relation.inverse_type

    @property
    def is_untyped_association(self) -> bool:
        return self.relation.is_untyped_association


@dataclass(frozen=True)
class TreeNode:
    """A node of the derived navigation view.

    `other_memberships` is what stops the tree lying: an organ filed under one
    system still advertises every other system it belongs to (FR-NAV-005).
    """
    entity_id: str
    label: str
    level: int | None
    compilation_status: str
    children: tuple['TreeNode', ...]
    other_memberships: tuple[str, ...]
    # `{child_id: 'contains' | 'member'}`. An organ is *in* a region and
    # *belongs to* a system; both are navigable and they are not the same
    # relation, so the view says which is which rather than flattening them.
    child_kinds: dict = field(default_factory=dict)

    @property
    def is_view(self) -> bool:
        """Always true. Present so that any surface rendering a node has to
        acknowledge it is rendering a view and not the model (D-006)."""
        return True


class Graph:
    """An in-process graph over one substrate.

    Chosen over a graph database because the volumetrics in PRD_Data_Overview
    keep the whole graph in memory well past Phase 3, and a release must be
    loadable in full for reproducibility (G-07).
    """

    def __init__(self, substrate: Substrate):
        self.substrate = substrate
        self._by_id: dict[str, Entity] = {}
        self._aliases: dict[str, str] = {}
        self._out: dict[str, list[Relationship]] = {}
        self._in: dict[str, list[Relationship]] = {}
        self._spatial: dict[str, SpatialIdentity] = {}
        self._index()

    # ---- indexing ------------------------------------------------------

    def _index(self) -> None:
        for e in self.substrate.entities:
            self._by_id[e.id] = e
            self._alias(e.id, e.id)
            for x in e.xrefs:
                xid = x.get('id')
                if xid:
                    self._alias(xid, e.id)
            for s in e.synonyms:
                term = s.get('term')
                if term:
                    self._alias(term.lower(), e.id)
            self._alias(e.preferred_term.lower(), e.id)
        for r in self.substrate.relationships:
            self._out.setdefault(r.source, []).append(r)
            self._in.setdefault(r.target, []).append(r)
        for s in self.substrate.spatial_identities:
            self._spatial[s.entity] = s

    def _alias(self, key: str, entity_id: str) -> None:
        # First writer wins: a preferred term never loses to a synonym that
        # happens to collide with it.
        self._aliases.setdefault(key, entity_id)

    # ---- resolution ----------------------------------------------------

    def resolve(self, ref: str, follow_retired: bool = False) -> Entity:
        """Resolve by primary id, external xref, synonym, or preferred term.

        Raises EntityRetired for a tombstoned id unless follow_retired is set —
        the caller is expected to answer with the successor, not a 404
        (FR-ONTO-004, FR-VER-007).
        """
        eid = self._aliases.get(ref) or self._aliases.get(ref.lower())
        if eid is None:
            raise KeyError(ref)
        entity = self._by_id[eid]
        if entity.is_retired and not follow_retired:
            raise EntityRetired(entity.id, entity.successor_id,
                                entity.retired_at or '')
        return entity

    def get(self, entity_id: str) -> Entity | None:
        return self._by_id.get(entity_id)

    def __contains__(self, entity_id: str) -> bool:
        return entity_id in self._by_id

    def __len__(self) -> int:
        return len(self._by_id)

    def entities(self) -> Iterator[Entity]:
        return iter(self.substrate.entities)

    def spatial_identity(self, entity_id: str) -> SpatialIdentity | None:
        return self._spatial.get(entity_id)

    # ---- traversal -----------------------------------------------------

    def edges(self, entity_id: str, *, types: set[str] | None = None,
              direction: str = 'both',
              include_associations: bool = True) -> list[Edge]:
        """Typed edges touching an entity.

        `include_associations=False` is how a mechanism view excludes untyped
        associations, which must never be rendered as mechanisms (FR-REL-006).
        """
        found: list[Edge] = []
        if direction in ('out', 'both'):
            for r in self._out.get(entity_id, []):
                found.append(Edge(r, r.target, True))
        if direction in ('in', 'both'):
            for r in self._in.get(entity_id, []):
                found.append(Edge(r, r.source, False))
        if types is not None:
            found = [e for e in found if e.relation.type in types]
        if not include_associations:
            found = [e for e in found if not e.is_untyped_association]
        return found

    def neighbours(self, entity_id: str, *, types: set[str] | None = None,
                   direction: str = 'both') -> list[str]:
        return [e.other for e in self.edges(entity_id, types=types,
                                            direction=direction)]

    def traverse(self, start: str, *, types: set[str] | None = None,
                 limit: int = DEFAULT_TRAVERSAL_LIMIT,
                 include_associations: bool = True) -> dict[str, int]:
        """Breadth-first traversal to a stated depth.

        Bounded by construction: an unbounded traversal of a graph returns
        everything, which is the same as returning nothing (FR-REL-010).
        """
        if limit < 0:
            raise ValueError('traversal limit must not be negative')
        seen = {start: 0}
        frontier = [start]
        for depth in range(1, limit + 1):
            nxt: list[str] = []
            for node in frontier:
                for edge in self.edges(node, types=types,
                                       include_associations=include_associations):
                    if edge.other not in seen and edge.other in self._by_id:
                        seen[edge.other] = depth
                        nxt.append(edge.other)
            if not nxt:
                break
            frontier = nxt
        return seen

    # ---- containment and membership ------------------------------------

    def parent(self, entity_id: str) -> str | None:
        """The single containment parent (INV-02)."""
        entity = self._by_id.get(entity_id)
        if entity and entity.part_of:
            return entity.part_of
        for r in self._out.get(entity_id, []):
            if r.type == CONTAINMENT:
                return r.target
        return None

    def children(self, entity_id: str) -> list[str]:
        """What this entity contains. Containment only — never membership."""
        kids = [e.id for e in self.substrate.entities if e.part_of == entity_id]
        kids += [r.source for r in self._in.get(entity_id, [])
                 if r.type == CONTAINMENT and r.source not in kids]
        return sorted(set(kids))

    def descendants(self, entity_id: str) -> list[str]:
        """What is reachable one step down, by containment **or** membership.

        The distinction from `children` is the pancreas test's first finding.
        A system contains nothing — an organ is `part_of` a body region and a
        `member_of` a system — so a tree built from containment alone reaches no
        organ from any system, and navigating from the digestive system found
        nothing at all. FR-NAV-005 requires the pancreas to be reachable from
        every system it belongs to, and it was not: memberships were reported
        on a node and were not traversable.

        Each edge keeps its kind, so a caller can still tell "inside" from
        "belongs to". Collapsing them would trade one wrong answer for another.
        """
        return sorted(set(self.children(entity_id)) | set(self.members(entity_id)))

    def descendant_kinds(self, entity_id: str) -> dict[str, str]:
        """`{child_id: 'contains' | 'member'}` for one step down."""
        kinds = {c: 'contains' for c in self.children(entity_id)}
        for m in self.members(entity_id):
            kinds.setdefault(m, 'member')
        return kinds

    def lineage(self, entity_id: str) -> list[str]:
        """Containment path from the entity up to its root, entity first.

        Cycle-safe: INV-02 forbids containment cycles, but a traversal that
        would hang on malformed data is worse than one that stops.
        """
        path, seen, cur = [], set(), entity_id
        while cur and cur not in seen:
            path.append(cur)
            seen.add(cur)
            cur = self.parent(cur)
        return path

    def memberships(self, entity_id: str) -> list[str]:
        """Every system this entity belongs to — the pancreas case (D-006).

        Membership is many-to-many and carries no primacy: the caller receives a
        list, never a "primary" plus others.
        """
        return sorted({r.target for r in self._out.get(entity_id, [])
                       if r.type == MEMBERSHIP})

    def members(self, system_id: str) -> list[str]:
        return sorted({r.source for r in self._in.get(system_id, [])
                       if r.type == MEMBERSHIP})

    def in_subsystem(self, entity_id: str, subsystem: str) -> bool:
        """Whether an entity belongs to a subsystem, by field **or** by edge.

        `Entity.subsystem` is single-valued — a tree-shaped field on a model
        whose whole thesis is that biology is a graph. The pancreas test found
        the consequence: filed as `digestive`, the pancreas was invisible to
        every endocrine query, so the endocrine system reported zero organs
        while containing one.

        Changing the field to a list would ripple through declared depth,
        competence scoping, and every schema. Consulting the graph instead
        costs nothing and is more correct anyway: membership edges are the
        canonical statement of what belongs where (D-006), and the field is
        best read as the entity's primary filing rather than as the whole
        truth about it.
        """
        entity = self._by_id.get(entity_id)
        if entity is not None and entity.subsystem == subsystem:
            return True
        systems = {self._by_id[m].subsystem for m in self.memberships(entity_id)
                   if m in self._by_id}
        return subsystem in systems

    # ---- the derived navigation view -----------------------------------

    def navigation_tree(self, root: str | None = None, *,
                        max_depth: int = 12) -> TreeNode:
        """Compute the navigation tree from containment **and** membership.

        Derived on every call and never stored (D-006). Each node carries the
        memberships the tree cannot express, so a reader who follows the tree
        still sees that a structure participates elsewhere (FR-NAV-005), and
        each child records whether it was reached by containment or by
        membership.

        Built from containment alone until the pancreas test: no organ was
        reachable from any system, because a system contains nothing. The tree
        was structurally incapable of satisfying the acceptance criterion the
        project was founded on — and no test caught it, because the substrate
        held no organ with a system membership to reach.
        """
        if root is None:
            roots = [e.id for e in self.substrate.entities
                     if not e.is_retired and self.parent(e.id) is None]
            root = sorted(roots)[0] if roots else ''
        return self._build_node(root, max_depth, set())

    def _build_node(self, entity_id: str, depth: int,
                    seen: set[str]) -> TreeNode:
        entity = self._by_id.get(entity_id)
        seen = seen | {entity_id}
        kids: tuple[TreeNode, ...] = ()
        kinds = self.descendant_kinds(entity_id)
        if depth > 0:
            kids = tuple(self._build_node(c, depth - 1, seen)
                         for c in sorted(kinds) if c not in seen)
        return TreeNode(
            entity_id=entity_id,
            label=entity.preferred_term if entity else entity_id,
            level=entity.shallowest_level if entity else None,
            compilation_status=entity.compilation_status if entity else 'narrative',
            children=kids,
            other_memberships=tuple(self.memberships(entity_id)),
            child_kinds=dict(kinds))
