"""Claims, provenance, conflicts, and the negative space.

Two properties distinguish this from a citation store. First, every claim can
produce its complete provenance without human interpretation — a claim that
cannot is not admitted (FR-EVID-010). Second, `UNKNOWN` is an asserted, stored,
queryable claim rather than an absent row, so the model can answer what it does
not know (FR-EVID-005).

Realizes: FR-EVID-001, FR-EVID-002, FR-EVID-005, FR-EVID-006, FR-EVID-007,
FR-EVID-010, FR-EVID-011, FR-EVID-013, FR-SRCH-004.
"""
from __future__ import annotations

from dataclasses import dataclass

from .graph import Graph
from .substrate import (EVIDENCE_CLASSES, TERMINOLOGICAL_GRADES, UNKNOWN,
                        Claim)

# Source types that can support each class.
#
# A THIRD copy of this rule is exactly how the original divergence happened
# (D-013), so this one is derived from tools/biocheck.py, which itself derives
# from docs/BIO_Evidence_and_Provenance.md. The document remains the authority
# and there is one derivation chain rather than three independent tables.
def _admissible_sources() -> dict[str, frozenset[str]]:
    try:
        import sys
        sys.path.insert(0, 'tools')
        import biocheck                                    # noqa: PLC0415
        doc, _ = biocheck.load_ladder()
        table = doc or biocheck.CLASS_SOURCE
        return {k: frozenset(v) for k, v in table.items()}
    except Exception:
        # Standalone use without the tools directory: fall back to the two
        # classes whose misuse actually matters, stated as the ladder states
        # them — a reference textbook can never support EVC-1.
        return {
            'EVC-1': frozenset({'primary research', 'systematic review'}),
            'EVC-2': frozenset({'primary research', 'systematic review',
                                'reference textbook', 'anatomical atlas',
                                'curated database'}),
        }


CLASS_ADMISSIBLE_SOURCES = _admissible_sources()

# How a class constrains what a downstream surface may say with it
# (FR-EVID-011). Enforced in the pipeline rather than left to prompt wording,
# because prompt wording degrades under paraphrase.
PRESENTATION_CONSTRAINTS = {
    'EVC-1': 'may be stated directly, with its measurement conditions',
    'EVC-2': 'may be stated directly; independence of sources is the basis',
    'EVC-3': 'must be presented as modelled, naming the model that produced it',
    'EVC-4': 'must be presented as an approximation, never as a measurement',
    'EVC-5': 'must be presented as inferred, naming what it was inferred from',
    'EVC-6': 'must be marked hypothetical and must not be the default answer',
    'EVC-7': 'must present both positions with their sources; never resolve',
    'EVC-8': 'must state the gap; must not be omitted to make a summary tidy',
}


@dataclass(frozen=True)
class ProvenanceRecord:
    """The complete answer to "how do we know this?" (FR-EVID-010)."""
    claim_id: str
    subject: str
    predicate: str
    object: object
    unit: str | None
    evidence_class: str
    class_name: str
    presentation_constraint: str
    sources: tuple[dict, ...]
    source_type: str
    species: str
    transfer_justification: str | None
    population: str
    conditions: dict
    date_asserted: str
    limitations: str
    conflicts_with: tuple[str, ...]
    assigned_by: str
    reviewed_by_human: bool
    provenance_source: str | None

    def as_dict(self) -> dict:
        return {
            'claim': self.claim_id, 'subject': self.subject,
            'predicate': self.predicate, 'object': self.object,
            'unit': self.unit, 'evidence_class': self.evidence_class,
            'class_name': self.class_name,
            'presentation_constraint': self.presentation_constraint,
            'sources': list(self.sources), 'source_type': self.source_type,
            'species': self.species,
            'transfer_justification': self.transfer_justification,
            'population': self.population, 'conditions': self.conditions,
            'date_asserted': self.date_asserted, 'limitations': self.limitations,
            'conflicts_with': list(self.conflicts_with),
            'assigned_by': self.assigned_by,
            'reviewed_by_human': self.reviewed_by_human,
            'provenance_source': self.provenance_source,
        }


@dataclass
class NegativeSpace:
    """What the model does not know about a subject (FR-SRCH-004).

    Distinguishes three cases that a bare empty result conflates: gaps that were
    assessed and recorded, a subject assessed with no gaps found, and a subject
    never assessed at all.
    """
    subject: str
    assessed: bool
    unknown_claims: list[dict]
    unpopulated_levels: list[int]
    declared_depth: int | None
    statement: str

    def as_dict(self) -> dict:
        return {
            'subject': self.subject, 'assessed': self.assessed,
            'unknown_claims': self.unknown_claims,
            'unpopulated_levels': self.unpopulated_levels,
            'declared_depth': self.declared_depth,
            'statement': self.statement,
        }


class EvidenceService:
    def __init__(self, graph: Graph, scale=None):
        self.graph = graph
        self.scale = scale
        self._by_id: dict[str, Claim] = {}
        self._by_subject: dict[str, list[Claim]] = {}
        for c in graph.substrate.claims:
            self._by_id[c.id] = c
            self._by_subject.setdefault(c.subject, []).append(c)

    # ---- lookup --------------------------------------------------------

    def claim(self, claim_id: str) -> Claim:
        return self._by_id[claim_id]

    def has(self, claim_id: str) -> bool:
        return claim_id in self._by_id

    def claims_for(self, subject: str, *, evidence_class: str | None = None,
                   predicate: str | None = None) -> list[Claim]:
        rows = self._by_subject.get(subject, [])
        if evidence_class:
            rows = [c for c in rows if c.evidence_class == evidence_class]
        if predicate:
            rows = [c for c in rows if c.predicate == predicate]
        return rows

    def all_claims(self) -> list[Claim]:
        return list(self._by_id.values())

    # ---- provenance ----------------------------------------------------

    def provenance(self, claim_id: str) -> ProvenanceRecord:
        c = self._by_id[claim_id]
        return ProvenanceRecord(
            claim_id=c.id, subject=c.subject, predicate=c.predicate,
            object=c.object, unit=c.unit, evidence_class=c.evidence_class,
            class_name=EVIDENCE_CLASSES.get(c.evidence_class, 'UNRECOGNISED'),
            presentation_constraint=PRESENTATION_CONSTRAINTS.get(
                c.evidence_class, 'no constraint recorded'),
            sources=c.sources, source_type=c.source_type, species=c.species,
            transfer_justification=c.transfer_justification,
            population=c.population, conditions=c.conditions,
            date_asserted=c.date_asserted, limitations=c.limitations,
            conflicts_with=c.conflicts_with, assigned_by=c.assigned_by,
            # Derived from the review state rather than from the shape of the
            # assigner string. Inferring review from an identifier prefix is
            # how a fabricated `human:` name passed for a review (D-017);
            # INV-17 keeps the two fields in agreement.
            reviewed_by_human=c.is_reviewed,
            provenance_source=c.provenance_source)

    def class_is_supported(self, claim: Claim) -> bool:
        """Whether the source type can carry the asserted class (INV-07)."""
        allowed = CLASS_ADMISSIBLE_SOURCES.get(claim.evidence_class)
        if allowed is None:
            return True
        return claim.source_type in allowed

    # ---- conflicts -----------------------------------------------------

    def conflicts(self, claim_id: str) -> list[ProvenanceRecord]:
        """Competing claims, both retained. The system never picks (FR-EVID-006)."""
        c = self._by_id[claim_id]
        return [self.provenance(other) for other in c.conflicts_with
                if other in self._by_id]

    def conflicted_claims(self) -> list[Claim]:
        return [c for c in self._by_id.values()
                if c.conflicts_with or c.evidence_class == 'EVC-7']

    # ---- negative space ------------------------------------------------

    def unknowns(self, subject: str | None = None) -> list[Claim]:
        rows = (self._by_subject.get(subject, []) if subject
                else list(self._by_id.values()))
        return [c for c in rows if c.is_unknown]

    def unknown_counts(self) -> dict:
        """Split asked-for from unprompted UNKNOWNs (FR-EVID-013, CH-10).

        The absolute count alone detects deletion but rewards padding; splitting
        it makes an inflated count visible as inflation.
        """
        asked = sum(1 for c in self.unknowns() if c.prompted_by)
        unprompted = sum(1 for c in self.unknowns() if not c.prompted_by)
        return {'total': asked + unprompted, 'asked_for': asked,
                'unprompted': unprompted,
                'note': ('Asked-for gaps were recorded in response to a query or '
                         'review; unprompted ones were asserted without being '
                         'requested. A rising unprompted count against a flat '
                         'asked-for count is padding, not diligence.')}

    def negative_space(self, subject: str) -> NegativeSpace:
        entity = self.graph.resolve(subject)
        unknown = self.unknowns(entity.id)
        all_claims = self._by_subject.get(entity.id, [])
        declared = None
        unpopulated: list[int] = []
        if self.scale is not None:
            declared = self.scale.declared(entity.subsystem)
            if declared is not None:
                rows = self.scale.coverage(entity.subsystem)
                if rows:
                    unpopulated = rows[0].unmet_levels
        if not all_claims:
            statement = (
                f'{entity.preferred_term} has no recorded claims in this '
                'release. Nothing has been assessed, so the absence of recorded '
                'gaps is not evidence that none exist.')
            assessed = False
        elif unknown:
            statement = (
                f'{len(unknown)} recorded gap(s) for {entity.preferred_term}. '
                'These are asserted UNKNOWNs, not missing data.')
            assessed = True
        else:
            statement = (
                f'{entity.preferred_term} has been assessed and carries no '
                'recorded UNKNOWN claims at its declared depth. Gaps beyond the '
                'declared depth are a scope statement, not an assessment.')
            assessed = True
        return NegativeSpace(
            subject=entity.id, assessed=assessed,
            unknown_claims=[self.provenance(c.id).as_dict() for c in unknown],
            unpopulated_levels=unpopulated, declared_depth=declared,
            statement=statement)

    # ---- reporting -----------------------------------------------------

    def completeness(self) -> dict:
        """G-03: proportion of claims with a complete evidence record.

        Reported per register (D-021). A single "165 claims" figure would let
        156 definitions stand in for the nine things this model has actually
        found out about a body — which is the number a reader of a coverage
        report is trying to learn.
        """
        required = ('species', 'population', 'limitations', 'assigned_by',
                    'date_asserted')
        total = len(self._by_id)
        biological = [c for c in self._by_id.values() if c.is_evidence]
        terminological = [c for c in self._by_id.values()
                          if c.is_terminological]
        complete = 0
        for c in self._by_id.values():
            if all(getattr(c, f) for f in required) and (
                    c.is_unknown or c.sources or c.is_terminological):
                complete += 1
        return {
            'claims': total,
            'biological_claims': len(biological),
            'terminological_claims': len(terminological),
            'complete_records': complete,
            'proportion': (complete / total) if total else 0.0,
            'unknown': self.unknown_counts(),
            'by_class': {k: sum(1 for c in biological
                                if c.evidence_class == k)
                         for k in EVIDENCE_CLASSES},
            'by_terminological_grade': {
                k: sum(1 for c in terminological if c.evidence_class == k)
                for k in TERMINOLOGICAL_GRADES},
            'note': ('`by_class` counts biological findings only. A definition '
                     'is not a finding and is graded on its own register '
                     '(D-021); conflating them was 94% of this substrate.'),
        }
