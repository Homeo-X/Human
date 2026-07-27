"""The compilation ladder: promotion rules and their gates.

Promotion is where prose becomes a model, so it is the one place the substrate
has to be actively defended. Three rules do the defending: promotion requires
recorded work rather than reformatting, an upstream split blocks it until a
human resolves the ambiguity, and a claim set whose population field never
discriminates cannot support a structured entity.

Realizes: FR-ONTO-005, FR-ONTO-007, FR-ONTO-012, and the write-side of
FR-ONTO-006.
"""
from __future__ import annotations

from dataclasses import dataclass

from .evidence import EvidenceService
from .graph import Graph
from .substrate import COMPILATION_ORDER, Entity

# CH-05: a population field that is constant across a claim set cannot do the
# job it exists for — distinguishing a genuine conflict from two populations.
# These are the values that carry no discriminating information.
NON_DISCRIMINATING = frozenset({
    '', 'unspecified', 'unspecified in source', 'adult, unspecified in source',
    'not specified', 'unknown', 'n/a',
})


@dataclass(frozen=True)
class PromotionDecision:
    """The outcome of an attempted promotion. Refusals name what is missing."""
    allowed: bool
    entity_id: str
    from_status: str
    to_status: str
    reasons: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {'allowed': self.allowed, 'entity': self.entity_id,
                'from': self.from_status, 'to': self.to_status,
                'reasons': list(self.reasons)}


@dataclass(frozen=True)
class PromotionRequest:
    """A promotion must carry the work that justifies it (FR-ONTO-007).

    `reviewer` and `work_recorded` are mandatory and are what distinguish a
    promotion from a re-ingest: reformatting a narrative entity into a tidier
    file produces neither.
    """
    entity_id: str
    to_status: str
    reviewer: str
    work_recorded: str


class PromotionService:
    def __init__(self, graph: Graph, evidence: EvidenceService):
        self.graph = graph
        self.evidence = evidence

    def evaluate(self, request: PromotionRequest) -> PromotionDecision:
        entity = self.graph.get(request.entity_id)
        if entity is None:
            return PromotionDecision(
                False, request.entity_id, 'unknown', request.to_status,
                (f'{request.entity_id} is not an entity in this release',))

        reasons: list[str] = []
        current = entity.compilation_status

        # Forward-only, one step at a time. A jump from narrative straight to
        # mechanistic would skip the typing work the ladder exists to record.
        try:
            here = COMPILATION_ORDER.index(current)
            there = COMPILATION_ORDER.index(request.to_status)
        except ValueError:
            return PromotionDecision(
                False, entity.id, current, request.to_status,
                (f'{request.to_status!r} is not a compilation status',))
        if there <= here:
            reasons.append(
                f'promotion is forward-only: {current} to {request.to_status} '
                f'is not a promotion')
        elif there - here > 1:
            reasons.append(
                f'promotion advances one step at a time: {current} to '
                f'{COMPILATION_ORDER[here + 1]} is the next admissible step')

        # FR-ONTO-007: recorded, reviewed work — never a reformat.
        if not request.reviewer.startswith('human:'):
            reasons.append(
                f'promotion requires a human reviewer; got {request.reviewer!r}')
        if not request.work_recorded.strip():
            reasons.append(
                'promotion requires a record of the curation work performed; '
                'reformatting or re-ingest promotes nothing')

        # FR-ONTO-005: an upstream split leaves the entity ambiguous.
        if entity.promotion_blocked:
            reasons.append(
                'promotion is blocked pending reviewer resolution of an '
                'upstream ontology change affecting this entity')

        # FR-ONTO-012 (CH-05): the population field must discriminate.
        if request.to_status == 'structured':
            reasons.extend(self._population_reasons(entity))

        return PromotionDecision(
            allowed=not reasons, entity_id=entity.id, from_status=current,
            to_status=request.to_status, reasons=tuple(reasons))

    def _population_reasons(self, entity: Entity) -> list[str]:
        claims = self.evidence.claims_for(entity.id)
        if not claims:
            return ['promotion to structured requires at least one claim; an '
                    'entity with no claims has nothing to structure']
        populations = {c.population.strip().lower() for c in claims
                       if not c.is_unknown}
        if not populations:
            return []          # only UNKNOWNs: nothing to discriminate yet
        if populations <= NON_DISCRIMINATING:
            return [
                'every claim carries a non-discriminating population '
                f'({", ".join(sorted(populations))}); the field cannot '
                'distinguish a genuine conflict from a population difference '
                'until it is narrowed']
        return []

    def apply(self, request: PromotionRequest) -> PromotionDecision:
        """Evaluate and, if allowed, advance the in-memory entity.

        Persistence is the curation plane's job (Phase 2); this returns the
        decision so a caller cannot advance a status without seeing it.
        """
        decision = self.evaluate(request)
        if not decision.allowed:
            return decision
        entity = self.graph.get(request.entity_id)
        idx = self.graph.substrate.entities.index(entity)
        promoted = Entity(**{**entity.__dict__,
                             'compilation_status': request.to_status})
        self.graph.substrate.entities[idx] = promoted
        self.graph._by_id[promoted.id] = promoted        # noqa: SLF001
        return decision

    # ---- retyping an association ---------------------------------------

    def retype_association(self, relationship_id: str, new_type: str,
                           reviewer: str, source: str) -> PromotionDecision:
        """Promote an untyped association to a specific relation (FR-REL-007).

        Knowing *that* two things are related is not knowing *how*. Retyping is
        curation work with a source, not a rename, so it requires both — and it
        is one-way: an edge is never demoted back to `associated_with`, because
        demotion would discard the reasoning that produced the type.
        """
        from .substrate import INVERSES
        rel = next((r for r in self.graph.substrate.relationships
                    if r.id == relationship_id), None)
        if rel is None:
            return PromotionDecision(
                False, relationship_id, 'unknown', new_type,
                (f'no relationship {relationship_id}',))
        reasons: list[str] = []
        if not rel.is_untyped_association:
            reasons.append(
                f'{relationship_id} is already typed as {rel.type}; retyping a '
                f'typed relation means retiring it and recording why')
        if new_type not in INVERSES:
            reasons.append(f'{new_type!r} is not in the relation vocabulary')
        if new_type == 'associated_with':
            reasons.append(
                'retyping to associated_with is a demotion; an edge is never '
                'demoted, because that would discard the reasoning that '
                'produced its type')
        if not reviewer.startswith('human:'):
            reasons.append(
                f'retyping requires a human curator; got {reviewer!r}')
        if not source.strip():
            reasons.append(
                'retyping requires a source: the corpus states that a '
                'relationship exists, not what type it is')
        if new_type in ('causes', 'contributes_to'):
            # The claim that backed the untyped association was recorded for a
            # different assertion; its strength says nothing about whether
            # causation holds. A causal retype needs its own claim, at its own
            # class — the FR-REL-008 principle applied one level further.
            if source == rel.provenance_claim:
                reasons.append(
                    f'{new_type} may not inherit the provenance of the untyped '
                    f'association ({rel.provenance_claim}); that claim was '
                    f'recorded for a different assertion. Supply a claim '
                    f'establishing the causal relation itself')
            elif not self.evidence.has(source):
                reasons.append(
                    f'{new_type} requires a claim id establishing the causal '
                    f'relation; {source!r} is not a claim in this release')
            elif new_type == 'causes':
                claim = self.evidence.claim(source)
                if claim.evidence_class > 'EVC-2':
                    reasons.append(
                        f'causes requires evidence class EVC-2 or better '
                        f'(FR-REL-005); {source} is {claim.evidence_class}. '
                        f'Consider contributes_to')
        return PromotionDecision(
            allowed=not reasons, entity_id=relationship_id,
            from_status=rel.type, to_status=new_type, reasons=tuple(reasons))

    # ---- reporting -----------------------------------------------------

    def ladder_report(self) -> dict:
        """How much of the model is still prose (RSK-10).

        Published per release so that "we have 157 entities" is never mistaken
        for "we have 157 modelled entities".
        """
        counts = {s: 0 for s in COMPILATION_ORDER}
        for e in self.graph.entities():
            counts[e.compilation_status] = counts.get(e.compilation_status, 0) + 1
        total = sum(counts.values())
        return {
            'counts': counts, 'total': total,
            'narrative_proportion': (counts['narrative'] / total) if total else 0.0,
            'blocked': sum(1 for e in self.graph.entities()
                           if e.promotion_blocked),
            'note': ('Narrative entities are described, not modelled. The '
                     'proportion is published so that entity count is never '
                     'mistaken for modelled coverage.'),
        }
