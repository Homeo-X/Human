"""The groundedness guard — INV-14.

The only thing standing between a fluent language model and fabricated biology,
and it works by *refusing output* rather than by filtering it. A response whose
assertions do not each resolve to a graph claim id is not rendered, however
plausible it reads (FR-RETR-001).

The guard is deliberately independent of any model provider. It takes assertions
already paired with claim ids and verifies them; a generator that cannot supply
the pairing cannot pass. That inversion is the point — the language model is a
phrasing engine over retrieved claims, never a source of biology.

Realizes: FR-RETR-001, FR-RETR-002, FR-RETR-003, FR-RETR-004, FR-RETR-005,
FR-RETR-008, FR-RETR-009, and the runtime half of INV-14.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .evidence import PRESENTATION_CONSTRAINTS, EvidenceService
from .graph import Graph
from .substrate import EVIDENCE_CLASSES

# Language that asserts mechanism or causation. An untyped association may not
# be described with any of it (FR-RETR-009, BRB-30): the corpus told us that a
# relationship exists, not what kind.
CAUSAL_LANGUAGE = re.compile(
    r'\b(causes?|caused|causing|leads? to|results? in|triggers?|drives?|'
    r'produces?|induces?|mechanism|because of|due to|therefore|'
    r'consequently|activates?|inhibits?|regulates?)\b', re.I)

# Framings that request clinical interpretation. Indirect phrasings are included
# deliberately: the framing must not change the answer (UC-12).
#
# The classes are judgment requests, not keywords — asking for a diagnosis, a
# severity or urgency call, a treatment, a prognosis, or an assessment of a named
# person. Matching keywords alone would be defeated by the first paraphrase, and
# EV-RETR-004 exists to keep finding the ones that are.
CLINICAL_REQUEST = re.compile(
    r'\b('
    r'diagnos\w*|prognos\w*|treat\w*|prescri\w*|medicat\w*|'
    r'do i have|have i got|am i (having|going to)|'
    r'should i\b|do i need to|'
    r'is (it|this|that|he|she|they)\s+(serious|dangerous|normal|bad|urgent|'
    r'life.?threatening|an emergency)|'
    r'how (serious|bad|dangerous|urgent)\b|'
    r'(worried|worry|concerned) about|'
    r'what.{0,25}\bwrong\b|what.{0,15}\b(condition|disease|illness)\s+(is|do)|'
    r'my (father|mother|son|daughter|wife|husband|friend|partner|child|'
    r'brother|sister)\b|'
    r'how do i (cure|fix|treat|get rid of)|'
    r'is this (a |an )?\w*(itis|osis|emia|opathy|oma)\b'
    r')', re.I)

NON_DIAGNOSTIC_BOUNDARY = (
    'This system is an educational and research reference. It does not '
    'diagnose, treat, or offer medical advice, and it is not a medical device.')


@dataclass
class Assertion:
    """One assertion in a generated response, with the claims backing it.

    `claim_ids` is a list, not a single id: a useful sentence routinely composes
    several claims, and CH-06 established that forcing one-claim assertions
    produces unreadable prose. The resolution is to carry every backing class
    rather than to average them (FR-RETR-002).
    """
    text: str
    claim_ids: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {'text': self.text, 'claims': list(self.claim_ids)}


@dataclass
class GroundedAssertion:
    text: str
    claim_ids: list[str]
    evidence_classes: list[str]
    class_names: list[str]
    constraints: list[str]

    @property
    def weakest_class(self) -> str:
        """The weakest backing class — reported alongside, never instead of, the
        full list. An aggregate would hide exactly the distinction that matters.
        """
        return max(self.evidence_classes) if self.evidence_classes else 'EVC-8'

    def as_dict(self) -> dict:
        return {
            'text': self.text, 'claims': list(self.claim_ids),
            'evidence_classes': list(self.evidence_classes),
            'class_names': list(self.class_names),
            'weakest_class': self.weakest_class,
            'presentation_constraints': list(self.constraints),
        }


@dataclass
class Response:
    """The outcome of a guarded generation. `refused` and `gap` are first-class
    successes, not errors — the HTTP layer returns both with 200."""
    status: str                       # grounded | refused | gap | declined
    assertions: list[GroundedAssertion] = field(default_factory=list)
    reason: str | None = None
    statement: str | None = None
    boundary: str | None = None
    release: str | None = None

    @property
    def ok(self) -> bool:
        return self.status == 'grounded'

    def as_dict(self) -> dict:
        return {
            'status': self.status,
            'assertions': [a.as_dict() for a in self.assertions],
            'reason': self.reason, 'statement': self.statement,
            'boundary': self.boundary, 'release': self.release,
        }


class GroundednessGuard:
    def __init__(self, graph: Graph, evidence: EvidenceService,
                 scale=None, release: str | None = None):
        self.graph = graph
        self.evidence = evidence
        self.scale = scale
        self.release = release

    # ---- the guard -----------------------------------------------------

    def guard(self, question: str,
              assertions: list[Assertion]) -> Response:
        """Verify a candidate response. Refuse rather than filter.

        Order matters: the clinical check runs first, because a clinically-framed
        question is declined regardless of how well-grounded the candidate text
        happens to be.
        """
        if self.is_clinical_request(question):
            return self.decline_clinical(question)

        if not assertions:
            return Response(
                status='gap', statement=self._gap_statement(question),
                boundary=None, release=self.release)

        grounded: list[GroundedAssertion] = []
        for a in assertions:
            if not a.claim_ids:
                return self._refuse(
                    f'assertion carries no claim id: {a.text!r}')
            classes, names, constraints = [], [], []
            for cid in a.claim_ids:
                if not self.evidence.has(cid):
                    return self._refuse(
                        f'assertion cites claim {cid} which does not exist in '
                        f'release {self.release or "(unpinned)"}: {a.text!r}')
                claim = self.evidence.claim(cid)
                classes.append(claim.evidence_class)
                names.append(EVIDENCE_CLASSES.get(claim.evidence_class,
                                                  'UNRECOGNISED'))
                constraints.append(
                    PRESENTATION_CONSTRAINTS.get(claim.evidence_class, ''))
            violation = self._association_violation(a)
            if violation:
                return self._refuse(violation)
            grounded.append(GroundedAssertion(
                text=a.text, claim_ids=list(a.claim_ids),
                evidence_classes=classes, class_names=names,
                constraints=constraints))
        return Response(status='grounded', assertions=grounded,
                        boundary=NON_DIAGNOSTIC_BOUNDARY, release=self.release)

    def _refuse(self, reason: str) -> Response:
        return Response(
            status='refused', reason=reason,
            statement=('This response was refused before rendering because at '
                       'least one assertion did not resolve to a recorded '
                       'claim. Fluency is not evidence.'),
            release=self.release)

    # ---- association phrasing -------------------------------------------

    def _association_violation(self, a: Assertion) -> str | None:
        """Refuse causal language over an untyped association (FR-RETR-009)."""
        if not CAUSAL_LANGUAGE.search(a.text):
            return None
        for cid in a.claim_ids:
            for rel in self.graph.substrate.relationships:
                if rel.provenance_claim == cid and rel.is_untyped_association:
                    return (
                        f'assertion uses causal or mechanistic language over an '
                        f'untyped association ({rel.id}): {a.text!r}. The source '
                        f'states that a relationship exists, not what type it is.')
        return None

    def describe_association(self, relationship_id: str) -> str:
        """The only admissible phrasing for an untyped association."""
        for rel in self.graph.substrate.relationships:
            if rel.id == relationship_id:
                if not rel.is_untyped_association:
                    raise ValueError(f'{relationship_id} is a typed relation '
                                     f'({rel.type}); describe it as such')
                return (
                    'An observed relationship of unstated type. The source '
                    'records that these are related without establishing how. '
                    f'Source note: {rel.prose_justification}')
        raise KeyError(relationship_id)

    # ---- clinical framing ------------------------------------------------

    def is_clinical_request(self, question: str) -> bool:
        return bool(CLINICAL_REQUEST.search(question))

    def decline_clinical(self, question: str) -> Response:
        """Decline usefully: give the anatomy, refuse the interpretation.

        A bare refusal would be worse than useless — the user still has a real
        structural question underneath the clinical framing (UC-12).
        """
        return Response(
            status='declined',
            statement=('This question asks for clinical interpretation, which '
                       'this system does not provide under any framing. '
                       'Structural and mechanistic content about the '
                       'structures involved is available through search.'),
            boundary=NON_DIAGNOSTIC_BOUNDARY, release=self.release)

    # ---- gaps -----------------------------------------------------------

    def _gap_statement(self, question: str) -> str:
        base = ('No recorded claims support an answer to this question in '
                'release ' + (self.release or '(unpinned)') + '. ')
        if self.scale is None:
            return base + 'That is a statement about the model, not the biology.'
        unmet = sum(len(r.unmet_levels) for r in self.scale.coverage())
        return base + (
            f'This model declares {unmet} level(s) across its subsystems that '
            'hold no content yet; the scale contract records what each level '
            'would represent. That is a statement about the model, not the '
            'biology.')
