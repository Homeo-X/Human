"""The curation plane — where anything becomes canonical.

This module is the project's correctness story. The validators establish
consistency; human review establishes everything else, and
BIO_Validation_Framework says so in its own closing section. Every path from a
proposal to canonical content terminates here, in an Approval record naming a
human who was competent to give it.

Three properties are enforced rather than requested:

- **No bypass.** There is no function here that admits content without an
  Approval, at any privilege level. The absence of an override is the guarantee.
- **Competence is scoped.** A reviewer may accept only within their declared
  subsystem and level. Scoping is what makes "expert review" more than a
  checkbox (FR-CUR-004).
- **Generation is throttled to review capacity.** An agent that outruns its
  reviewers produces a backlog that becomes a rubber stamp, which is RSK-02 —
  the risk the whole spec names as principal (FR-CUR-009, BR-023).

Realizes: FR-CUR-001 … FR-CUR-011.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

TASK_STATES = ('queued', 'in_review', 'accepted', 'rejected', 'blocked',
               'escalated')
# Kinds of change that reach canonical content. Each needs an Approval.
CHANGE_KINDS = ('entity', 'claim', 'relationship', 'process', 'promotion',
                'retype', 'adjudication')


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


class CurationError(Exception):
    """A curation action was refused. Never raised for content that is merely
    absent — only for actions the plane must not perform."""


@dataclass(frozen=True)
class Competence:
    """What a reviewer is qualified to accept.

    Deliberately narrow by default: a reviewer with no declared subsystems can
    review nothing, rather than everything. A permissions model that fails open
    is not a permissions model.
    """
    reviewer: str
    subsystems: frozenset[str] = frozenset()
    max_level: int = -1
    note: str = ''

    def covers(self, subsystem: str, level: int | None) -> bool:
        if not self.reviewer.startswith('human:'):
            return False
        if subsystem not in self.subsystems:
            return False
        return level is None or level <= self.max_level

    def why_not(self, subsystem: str, level: int | None) -> str:
        if not self.reviewer.startswith('human:'):
            return f'{self.reviewer} is not a human reviewer'
        if subsystem not in self.subsystems:
            return (f'{self.reviewer} has no declared competence in '
                    f'{subsystem} (declared: '
                    f'{", ".join(sorted(self.subsystems)) or "none"})')
        return (f'{self.reviewer} is competent to L{self.max_level}; this '
                f'content is at L{level}')


@dataclass
class Proposal:
    """A candidate change, with the derivation that lets a reviewer judge it.

    `derivation` is mandatory and is what separates a reviewable proposal from
    one a reviewer must reconstruct — and a reviewer forced to reconstruct
    context will approve on vibes (FR-CUR-002).
    """
    id: str
    kind: str
    subsystem: str
    level: int | None
    payload: dict
    proposed_by: str
    derivation: dict
    created_at: str = field(default_factory=_now)

    def reviewable(self) -> tuple[bool, str]:
        if self.kind not in CHANGE_KINDS:
            return False, f'unknown change kind {self.kind!r}'
        if not self.derivation.get('sources') and self.kind in (
                'claim', 'relationship'):
            return False, ('no sources in the derivation; a reviewer cannot '
                           'judge a claim without them')
        if not self.derivation.get('steps'):
            return False, ('no derivation steps recorded; the proposal cannot '
                           'be reviewed without showing how it was reached')
        return True, ''


@dataclass
class Review:
    reviewer: str
    decision: str                      # accepted | rejected | escalated
    reason: str
    at: str = field(default_factory=_now)

    def as_dict(self) -> dict:
        return {'reviewer': self.reviewer, 'decision': self.decision,
                'reason': self.reason, 'at': self.at}


@dataclass
class Approval:
    """The record required for any canonical change (BR-009).

    Carries a digest of exactly what was approved, so a later reader can tell
    whether the content that shipped is the content that was reviewed.
    """
    id: str
    task_id: str
    reviewer: str
    kind: str
    payload_digest: str
    at: str = field(default_factory=_now)

    def as_dict(self) -> dict:
        return {'id': self.id, 'task': self.task_id, 'reviewer': self.reviewer,
                'kind': self.kind, 'payload_digest': self.payload_digest,
                'at': self.at}


@dataclass
class Task:
    id: str
    proposal: Proposal
    state: str = 'queued'
    reviews: list[Review] = field(default_factory=list)
    approval: Approval | None = None
    blocked_reason: str = ''
    held_by: str | None = None

    def as_dict(self) -> dict:
        return {
            'id': self.id, 'state': self.state, 'kind': self.proposal.kind,
            'subsystem': self.proposal.subsystem, 'level': self.proposal.level,
            'proposed_by': self.proposal.proposed_by,
            'created_at': self.proposal.created_at,
            'derivation': self.proposal.derivation,
            'reviews': [r.as_dict() for r in self.reviews],
            'approval': self.approval.as_dict() if self.approval else None,
            'blocked_reason': self.blocked_reason,
            'held_by': self.held_by,
        }


def digest(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(',', ':'),
                   ensure_ascii=False).encode()).hexdigest()[:16]


class CurationService:
    """The queue, the gate, and the throttle."""

    def __init__(self, competences: list[Competence] | None = None,
                 queue_ceiling: int = 25):
        self.tasks: dict[str, Task] = {}
        self.competences = {c.reviewer: c for c in (competences or [])}
        self.queue_ceiling = queue_ceiling
        self._rejections: dict[str, list[tuple[str, str]]] = {}
        self._seq = 0

    # ---- intake --------------------------------------------------------

    def _next_id(self, prefix: str) -> str:
        self._seq += 1
        return f'{prefix}:{self._seq:05d}'

    def submit(self, proposal: Proposal) -> Task:
        """Queue a proposal, refusing what cannot be reviewed (FR-CUR-002).

        Also surfaces a prior rejection of substantially the same proposal, so
        an agent cannot regenerate rejected content indefinitely (FR-CUR-003).
        """
        ok, why = proposal.reviewable()
        if not ok:
            raise CurationError(f'{proposal.id} is not reviewable: {why}')
        if self.is_throttled(proposal.subsystem):
            raise CurationError(
                f'generation for {proposal.subsystem} is throttled: '
                f'{self.queue_depth(proposal.subsystem)} tasks pending against '
                f'a ceiling of {self.queue_ceiling}. Review capacity is the '
                f'planning unit, not agent capacity (BR-023)')
        task = Task(id=self._next_id('TASK'), proposal=proposal)
        prior = self._rejections.get(digest(proposal.payload))
        if prior:
            task.blocked_reason = (
                'a substantially identical proposal was rejected before: '
                + '; '.join(f'{who}: {why}' for who, why in prior))
            task.state = 'blocked'
        self.tasks[task.id] = task
        return task

    # ---- throttle ------------------------------------------------------

    def queue_depth(self, subsystem: str | None = None) -> int:
        return sum(1 for t in self.tasks.values()
                   if t.state in ('queued', 'in_review')
                   and (subsystem is None
                        or t.proposal.subsystem == subsystem))

    def is_throttled(self, subsystem: str) -> bool:
        """Generation pauses when the queue outruns review (FR-CUR-009)."""
        return self.queue_depth(subsystem) >= self.queue_ceiling

    def pending(self) -> list[Task]:
        """Tasks still awaiting a decision, oldest first.

        Blocked tasks are included: a proposal blocked by an earlier rejection
        still needs a reviewer to look at it, and hiding it would make the
        queue's depth disagree with the operator view's.
        """
        return sorted(
            (t for t in self.tasks.values()
             if t.state in ('queued', 'in_review', 'blocked', 'escalated')),
            key=lambda t: t.proposal.created_at)

    # ---- review --------------------------------------------------------

    def claim_task(self, task_id: str, reviewer: str) -> Task:
        """Soft lock, so two reviewers cannot decide the same task."""
        task = self._task(task_id)
        if task.held_by and task.held_by != reviewer:
            raise CurationError(
                f'{task_id} is held by {task.held_by}')
        task.held_by = reviewer
        task.state = 'in_review'
        return task

    def _task(self, task_id: str) -> Task:
        if task_id not in self.tasks:
            raise CurationError(f'no task {task_id}')
        return self.tasks[task_id]

    def can_review(self, reviewer: str, task_id: str) -> tuple[bool, str]:
        task = self._task(task_id)
        comp = self.competences.get(reviewer)
        if comp is None:
            return False, (f'{reviewer} has no declared competence; review '
                           f'scope is deny-by-default')
        if not comp.covers(task.proposal.subsystem, task.proposal.level):
            return False, comp.why_not(task.proposal.subsystem,
                                       task.proposal.level)
        return True, ''

    def accept(self, task_id: str, reviewer: str, reason: str) -> Approval:
        """Accept within competence, producing the Approval (FR-CUR-001)."""
        task = self._task(task_id)
        if task.state in ('accepted', 'rejected'):
            raise CurationError(
                f'{task_id} is already {task.state}; decisions are recorded '
                f'once and superseded, never overwritten')
        if task.state == 'blocked':
            raise CurationError(
                f'{task_id} is blocked: {task.blocked_reason}')
        ok, why = self.can_review(reviewer, task_id)
        if not ok:
            raise CurationError(f'out of competence scope — {why}')
        if not reason.strip():
            raise CurationError('acceptance requires a recorded reason')
        task.reviews.append(Review(reviewer, 'accepted', reason))
        task.approval = Approval(
            id=self._next_id('APPR'), task_id=task.id, reviewer=reviewer,
            kind=task.proposal.kind,
            payload_digest=digest(task.proposal.payload))
        task.state = 'accepted'
        return task.approval

    def reject(self, task_id: str, reviewer: str, reason: str) -> Task:
        """Reject with a reason that persists against the proposal (FR-CUR-003)."""
        task = self._task(task_id)
        if not reason.strip():
            raise CurationError(
                'rejection requires a reason; without one the same proposal '
                'returns unchanged')
        ok, why = self.can_review(reviewer, task_id)
        if not ok:
            raise CurationError(f'out of competence scope — {why}')
        task.reviews.append(Review(reviewer, 'rejected', reason))
        task.state = 'rejected'
        self._rejections.setdefault(digest(task.proposal.payload), []).append(
            (reviewer, reason))
        return task

    def escalate(self, task_id: str, reviewer: str, reason: str) -> Task:
        task = self._task(task_id)
        task.reviews.append(Review(reviewer, 'escalated', reason))
        task.state = 'escalated'
        return task

    def block(self, task_id: str, reason: str) -> Task:
        """A blocking condition is not a failure — it carries its resolution."""
        task = self._task(task_id)
        task.state = 'blocked'
        task.blocked_reason = reason
        return task

    # ---- adjudication --------------------------------------------------

    def adjudicate(self, task_id: str, reviewers: list[str],
                   resolution: str) -> Approval:
        """Conflict adjudication requires two reviewers (FR-CUR-005).

        Produces a new decision citing both positions; neither original is
        deleted, because erasing the losing side destroys the record of a real
        scientific disagreement.
        """
        task = self._task(task_id)
        if len(set(reviewers)) < 2:
            raise CurationError(
                'adjudication requires two distinct reviewers; one reviewer '
                'settling a conflict is not adjudication')
        for r in reviewers:
            ok, why = self.can_review(r, task_id)
            if not ok:
                raise CurationError(f'{r} cannot adjudicate — {why}')
        if not resolution.strip():
            raise CurationError('adjudication requires a recorded resolution')
        for r in reviewers:
            task.reviews.append(Review(r, 'accepted', resolution))
        task.approval = Approval(
            id=self._next_id('APPR'), task_id=task.id,
            reviewer=' + '.join(sorted(set(reviewers))), kind='adjudication',
            payload_digest=digest(task.proposal.payload))
        task.state = 'accepted'
        return task.approval

    # ---- batch ---------------------------------------------------------

    def accept_batch(self, task_ids: list[str], reviewer: str,
                     reason: str) -> list[Approval]:
        """One decision, recorded individually per item (FR-CUR-010).

        Batching is necessary at scale; recording one approval for fifty items
        is not, because the record would then not say what was approved.
        """
        approvals = []
        for tid in task_ids:
            approvals.append(self.accept(tid, reviewer,
                                         f'{reason} [batch of {len(task_ids)}]'))
        return approvals

    # ---- operator view -------------------------------------------------

    def operator_view(self) -> dict:
        """Queue depth, throughput and blockers (FR-CUR-008).

        Curation capacity is the project's real constraint; hiding it hides the
        bottleneck, which is how RSK-02 becomes invisible.
        """
        by_sub: dict[str, dict[str, int]] = {}
        for t in self.tasks.values():
            row = by_sub.setdefault(t.proposal.subsystem,
                                    {s: 0 for s in TASK_STATES})
            row[t.state] += 1
        blocked = [{'task': t.id, 'reason': t.blocked_reason}
                   for t in self.tasks.values() if t.state == 'blocked']
        decided = sum(1 for t in self.tasks.values()
                      if t.state in ('accepted', 'rejected'))
        return {
            'tasks': len(self.tasks),
            'queue_depth': self.queue_depth(),
            'queue_ceiling': self.queue_ceiling,
            'throttled_subsystems': sorted(
                s for s in by_sub if self.is_throttled(s)),
            'decided': decided,
            'by_subsystem': by_sub,
            'blocked': blocked,
            'reviewer_capacity': {
                c.reviewer: {'subsystems': sorted(c.subsystems),
                             'max_level': c.max_level}
                for c in self.competences.values()},
            'note': ('Review capacity is the binding constraint on this project '
                     '(RSK-02). It is published rather than inferred, because a '
                     'queue that outruns review becomes a rubber stamp while '
                     'every validator stays green.'),
        }

    # ---- persistence ---------------------------------------------------

    def save(self, path: str) -> str:
        """Write the queue so it outlives the process that made it.

        Reviewers are people with other jobs; a queue that exists only inside a
        running agent is a queue nobody reviews. The rejection ledger is saved
        with the tasks, because a rejection that does not survive a restart is
        an invitation to resubmit (FR-CUR-003).
        """
        payload = {
            'queue_ceiling': self.queue_ceiling,
            'seq': self._seq,
            'competences': [
                {'reviewer': c.reviewer, 'subsystems': sorted(c.subsystems),
                 'max_level': c.max_level, 'note': c.note}
                for c in self.competences.values()],
            'tasks': [{**t.as_dict(),
                       'payload': t.proposal.payload,
                       'proposal_id': t.proposal.id} for t in
                      self.tasks.values()],
            'rejections': {k: [list(v) for v in vs]
                           for k, vs in self._rejections.items()},
        }
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=1, ensure_ascii=False)
        return path

    @classmethod
    def load(cls, path: str) -> 'CurationService':
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
        svc = cls([Competence(c['reviewer'], frozenset(c['subsystems']),
                              c['max_level'], c.get('note', ''))
                   for c in data.get('competences', [])],
                  queue_ceiling=data.get('queue_ceiling', 25))
        svc._seq = data.get('seq', 0)
        for row in data.get('tasks', []):
            proposal = Proposal(
                id=row.get('proposal_id', row['id']), kind=row['kind'],
                subsystem=row['subsystem'], level=row['level'],
                payload=row.get('payload', {}),
                proposed_by=row['proposed_by'],
                derivation=row.get('derivation', {}),
                created_at=row.get('created_at', _now()))
            task = Task(id=row['id'], proposal=proposal, state=row['state'],
                        blocked_reason=row.get('blocked_reason', ''),
                        held_by=row.get('held_by'))
            task.reviews = [Review(r['reviewer'], r['decision'], r['reason'],
                                   r['at']) for r in row.get('reviews', [])]
            appr = row.get('approval')
            if appr:
                task.approval = Approval(appr['id'], appr['task'],
                                         appr['reviewer'], appr['kind'],
                                         appr['payload_digest'], appr['at'])
            svc.tasks[task.id] = task
        svc._rejections = {k: [tuple(v) for v in vs]
                           for k, vs in data.get('rejections', {}).items()}
        return svc

    def approvals(self) -> list[Approval]:
        return [t.approval for t in self.tasks.values() if t.approval]

    def accepted_payloads(self, kind: str | None = None) -> list[dict]:
        """Content cleared for canonical admission — approval-gated by
        construction, since only accepted tasks carry one."""
        out = []
        for t in self.tasks.values():
            if t.state == 'accepted' and t.approval is not None:
                if kind is None or t.proposal.kind == kind:
                    out.append({'payload': t.proposal.payload,
                                'approval': t.approval.as_dict(),
                                'task': t.id})
        return out
