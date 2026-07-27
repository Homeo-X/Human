"""The agent runtime — the twelve-facet contract, enforced.

The load-bearing word is *enforced*. PRD_FR_Agent_Definition Facet 5 says tool
autonomy is enforced by the runtime and not the prompt, and this module is where
that is true: an agent cannot invoke a forbidden tool by being asked nicely,
because the invocation path checks the cell before the tool is reached.

No language model is bound here, deliberately. An agent is a principal with a
tool contract, a budget, and a run record; the intelligence that chooses actions
is pluggable and untrusted. That inversion is what makes the guarantees testable
without a provider — and what makes them survive a change of provider.

Realizes: FR-AGD-001 … FR-AGD-008, and the runtime object model in SPEC_MODEL.md
(Agent, Task, Plan, AgentRun, Step, ToolCall, Observation, Artifact, Approval,
Failure, Retry, Compensation, EvaluationRecord).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .curation import CurationError, CurationService, Proposal

# Effect classes and autonomy cells, per Facet 5. `forbidden` means no agent may
# reach the tool at all; `confirm` means a human Approval must exist first.
AUTO, CONFIRM, FORBIDDEN = 'auto', 'confirm', 'forbidden'
READ_ONLY, REVERSIBLE, IRREVERSIBLE = 'read-only', 'reversible', 'irreversible'


@dataclass(frozen=True)
class Tool:
    id: str
    name: str
    effect: str
    autonomy: str
    agents: frozenset[str]            # which agents may use it at all
    note: str = ''


# The TOOL register from PRD_FR_Agent_Definition Facet 5. Note the shape of the
# table: no irreversible tool is `auto` for any agent. That absence is deliberate
# and is asserted by a test.
TOOLS: dict[str, Tool] = {
    'TOOL-01': Tool('TOOL-01', 'graph read', READ_ONLY, AUTO,
                    frozenset({'*'})),
    'TOOL-02': Tool('TOOL-02', 'source fetch', READ_ONLY, AUTO,
                    frozenset({'*'})),
    'TOOL-03': Tool('TOOL-03', 'propose entity', REVERSIBLE, AUTO,
                    frozenset({'AGT-1', 'AGT-3', 'AGT-5', 'AGT-6'}),
                    'writes to the proposal queue only, never to the graph'),
    'TOOL-04': Tool('TOOL-04', 'propose claim (EVC-3 or weaker)', REVERSIBLE,
                    AUTO, frozenset({'AGT-2', 'AGT-4', 'AGT-5', 'AGT-6'})),
    'TOOL-05': Tool('TOOL-05', 'propose claim at EVC-1 or EVC-2', REVERSIBLE,
                    FORBIDDEN, frozenset(),
                    'exists only for human reviewers; no agent may reach it'),
    'TOOL-06': Tool('TOOL-06', 'promote compilation status', IRREVERSIBLE,
                    CONFIRM, frozenset({'AGT-1', 'AGT-4'})),
    'TOOL-07': Tool('TOOL-07', 'bind geometry', REVERSIBLE, AUTO,
                    frozenset({'AGT-7'}), 'unpublished assets only'),
    'TOOL-08': Tool('TOOL-08', 'publish', IRREVERSIBLE, CONFIRM, frozenset()),
    'TOOL-09': Tool('TOOL-09', 'run invariant harness', READ_ONLY, AUTO,
                    frozenset({'AGT-10'})),
    'TOOL-10': Tool('TOOL-10', 'run executable process', REVERSIBLE, AUTO,
                    frozenset({'AGT-8'})),
    'TOOL-11': Tool('TOOL-11', 'write overlay value', REVERSIBLE, AUTO,
                    frozenset({'AGT-9'}), 'overlay space only'),
    'TOOL-12': Tool('TOOL-12', 'write challenge finding', REVERSIBLE, AUTO,
                    frozenset({'AGT-12'}), 'the challenge register only'),
}

# The agent register, with the authority ceiling each one may not exceed.
AGENTS = {
    'AGT-1': 'Biological Ontology', 'AGT-2': 'Evidence', 'AGT-3': 'Anatomy',
    'AGT-4': 'Physiology', 'AGT-5': 'Cellular Biology',
    'AGT-6': 'Molecular Biology', 'AGT-7': '3D Representation',
    'AGT-8': 'Simulation', 'AGT-9': 'Personalization', 'AGT-10': 'Validation',
    'AGT-11': 'Provenance', 'AGT-12': 'Red-Team Biology',
}

# Facet 12 cost ceilings (NFR-025). Reaching one stops the run at a declared
# safe point — never a silent truncation.
DEFAULT_BUDGET = {'tool_calls': 50, 'steps': 30}

# Classes no agent may assign, at any autonomy level (BR-002).
AGENT_FORBIDDEN_CLASSES = frozenset({'EVC-1', 'EVC-2'})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


class AutonomyViolation(Exception):
    """A tool call that the contract does not permit. Raised by the runtime
    before the tool is reached, so no prompt wording can talk past it."""


class BudgetExhausted(Exception):
    """A ceiling was reached. The run stops at a declared safe point."""


@dataclass
class Observation:
    step: int
    tool: str
    result: object
    validated: bool
    note: str = ''
    at: str = field(default_factory=_now)

    def as_dict(self) -> dict:
        return {'step': self.step, 'tool': self.tool, 'result': self.result,
                'validated': self.validated, 'note': self.note, 'at': self.at}


@dataclass
class ToolCall:
    step: int
    tool: str
    args: dict
    outcome: str                       # returned | blocked
    reason: str = ''
    at: str = field(default_factory=_now)

    def as_dict(self) -> dict:
        return {'step': self.step, 'tool': self.tool, 'args': self.args,
                'outcome': self.outcome, 'reason': self.reason, 'at': self.at}


@dataclass
class Failure:
    step: int
    kind: str
    detail: str
    compensated: bool = False
    at: str = field(default_factory=_now)

    def as_dict(self) -> dict:
        return {'step': self.step, 'kind': self.kind, 'detail': self.detail,
                'compensated': self.compensated, 'at': self.at}


@dataclass
class AgentRun:
    id: str
    agent: str
    task: str
    state: str = 'queued'
    steps: int = 0
    tool_calls: list[ToolCall] = field(default_factory=list)
    observations: list[Observation] = field(default_factory=list)
    failures: list[Failure] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    budget: dict = field(default_factory=lambda: dict(DEFAULT_BUDGET))
    stopped_reason: str = ''
    seed: int | None = None

    @property
    def blocked_calls(self) -> list[ToolCall]:
        return [c for c in self.tool_calls if c.outcome == 'blocked']

    def as_dict(self) -> dict:
        return {
            'id': self.id, 'agent': self.agent, 'task': self.task,
            'state': self.state, 'steps': self.steps,
            'tool_calls': [c.as_dict() for c in self.tool_calls],
            'observations': [o.as_dict() for o in self.observations],
            'failures': [f.as_dict() for f in self.failures],
            'artifacts': list(self.artifacts), 'budget': self.budget,
            'stopped_reason': self.stopped_reason, 'seed': self.seed,
        }

    def summary(self) -> dict:
        """The honest terminal state: what changed and what did not."""
        return {
            'run': self.id, 'agent': self.agent, 'state': self.state,
            'steps': self.steps, 'calls': len(self.tool_calls),
            'blocked': len(self.blocked_calls),
            'artifacts_produced': list(self.artifacts),
            'failures': len(self.failures),
            'stopped_reason': self.stopped_reason or None,
            'canonical_changes': 0,
            'note': ('An agent run never changes canonical content. Anything '
                     'it produced is a proposal awaiting human review.'),
        }


# Content that looks like an instruction. Tool outputs are data; nothing an
# agent reads may escalate an autonomy cell (Facet 5, FR-AGD-005).
INJECTION_MARKERS = (
    'ignore previous', 'ignore the above', 'disregard', 'system:',
    'you are now', 'new instructions', 'override', 'grant yourself',
    'act as', 'sudo', 'approve this',
)


class AgentRuntime:
    """Runs agents under their contract. The contract is checked here."""

    def __init__(self, curation: CurationService):
        self.curation = curation
        self.runs: dict[str, AgentRun] = {}
        self._seq = 0

    # ---- runs ----------------------------------------------------------

    def start(self, agent: str, task: str, *, budget: dict | None = None,
              seed: int | None = None) -> AgentRun:
        if agent not in AGENTS:
            raise AutonomyViolation(f'{agent} is not a registered agent')
        self._seq += 1
        run = AgentRun(id=f'RUN:{self._seq:05d}', agent=agent, task=task,
                       state='executing',
                       budget=dict(budget or DEFAULT_BUDGET), seed=seed)
        self.runs[run.id] = run
        return run

    # ---- the enforcement point -----------------------------------------

    def call(self, run: AgentRun, tool_id: str, **args) -> Observation:
        """Every tool invocation passes through here.

        Order matters: budget, then registration, then permission, then
        autonomy. A forbidden call is recorded as a blocked ToolCall rather than
        silently dropped, because the attempt is the interesting event.
        """
        tool = TOOLS.get(tool_id)
        run.steps += 1

        if run.steps > run.budget.get('steps', DEFAULT_BUDGET['steps']):
            return self._stop(run, 'step budget exhausted')
        if len(run.tool_calls) >= run.budget.get(
                'tool_calls', DEFAULT_BUDGET['tool_calls']):
            return self._stop(run, 'tool-call budget exhausted')

        if tool is None:
            return self._block(run, tool_id, args,
                               f'{tool_id} is not a registered tool')
        if tool.autonomy == FORBIDDEN:
            return self._block(
                run, tool_id, args,
                f'{tool_id} ({tool.name}) is forbidden to every agent. '
                f'{tool.note or ""}'.strip())
        if '*' not in tool.agents and run.agent not in tool.agents:
            return self._block(
                run, tool_id, args,
                f'{run.agent} is not permitted {tool_id} ({tool.name}); '
                f'permitted: {", ".join(sorted(tool.agents)) or "none"}')
        if tool.autonomy == CONFIRM and not args.get('approval'):
            return self._block(
                run, tool_id, args,
                f'{tool_id} ({tool.name}) is {tool.effect} and requires a human '
                f'Approval before execution; none was supplied')
        if tool.effect == IRREVERSIBLE and tool.autonomy == AUTO:
            # Defensive: the register must never contain such a cell.
            return self._block(run, tool_id, args,
                               f'{tool_id} is irreversible and auto — '
                               f'inadmissible cell')

        result = args.get('result')
        note, validated = self._validate_observation(result)
        run.tool_calls.append(ToolCall(run.steps, tool_id, self._safe(args),
                                       'returned'))
        obs = Observation(run.steps, tool_id, result, validated, note)
        run.observations.append(obs)
        return obs

    def _block(self, run: AgentRun, tool_id: str, args: dict,
               reason: str) -> Observation:
        run.tool_calls.append(
            ToolCall(run.steps, tool_id, self._safe(args), 'blocked', reason))
        run.failures.append(Failure(run.steps, 'autonomy', reason))
        raise AutonomyViolation(reason)

    def _stop(self, run: AgentRun, reason: str) -> Observation:
        run.state = 'stopped_at_budget'
        run.stopped_reason = reason
        raise BudgetExhausted(
            f'{run.id}: {reason}. Stopped at a declared safe point; partial '
            f'work is labelled partial and is not queued.')

    @staticmethod
    def _safe(args: dict) -> dict:
        """Arguments recorded for audit, without dragging payloads into logs."""
        return {k: (v if isinstance(v, (str, int, float, bool, type(None)))
                    else f'<{type(v).__name__}>')
                for k, v in args.items() if k != 'result'}

    @staticmethod
    def _validate_observation(result) -> tuple[str, bool]:
        """Observations are validated before use (Facet 9).

        Instruction-shaped content is flagged and treated as data. It does not
        raise: refusing to read a source because it contains the word "override"
        would be its own denial-of-service.
        """
        text = json.dumps(result, ensure_ascii=False).lower() if result else ''
        hits = [m for m in INJECTION_MARKERS if m in text]
        if hits:
            return (f'instruction-shaped content in tool output '
                    f'({", ".join(hits)}); treated as data, autonomy '
                    f'unchanged', False)
        return '', True

    # ---- proposing -----------------------------------------------------

    def propose(self, run: AgentRun, *, kind: str, subsystem: str,
                level: int | None, payload: dict, sources: list[str],
                rationale: str) -> str:
        """Queue a proposal, attributed to the agent (FR-AGD-004).

        Refuses outright to propose a claim at a class no agent may assign —
        the check is here, not in the reviewer's judgment (FR-AGD-003).
        """
        cls = payload.get('evidence_class')
        if cls in AGENT_FORBIDDEN_CLASSES:
            self._block(run, 'TOOL-05', {'evidence_class': cls},
                        f'{run.agent} attempted to propose a claim at {cls}; '
                        f'no agent may assign EVC-1 or EVC-2 (BR-002)')
        tool = 'TOOL-03' if kind == 'entity' else 'TOOL-04'
        self.call(run, tool, kind=kind, subsystem=subsystem)
        proposal = Proposal(
            id=f'PROP:{run.id}:{len(run.artifacts) + 1}', kind=kind,
            subsystem=subsystem, level=level, payload=payload,
            proposed_by=run.agent,
            derivation={
                'run': run.id, 'agent': run.agent,
                'steps': [c.as_dict() for c in run.tool_calls],
                'sources': sources, 'rationale': rationale,
                'observations_flagged': [o.note for o in run.observations
                                         if not o.validated],
            })
        try:
            task = self.curation.submit(proposal)
        except CurationError as exc:
            run.failures.append(Failure(run.steps, 'queue', str(exc)))
            raise
        run.artifacts.append(task.id)
        return task.id

    def finish(self, run: AgentRun) -> dict:
        if run.state == 'executing':
            run.state = 'completed'
        return run.summary()


class RedTeamAgent:
    """AGT-12 — attacks only, and cannot do anything else.

    Its isolation is structural here rather than procedural: the class exposes
    no proposal method at all, so a finding cannot become a content change by
    being phrased as one. CH-08 observed that a finding's *text* can smuggle a
    remedy; that remains true and is a review concern, but the write path does
    not exist (FR-AGD-007).
    """

    def __init__(self, runtime: AgentRuntime):
        self.runtime = runtime
        self.findings: list[dict] = []

    def start(self, task: str) -> AgentRun:
        return self.runtime.start('AGT-12', task)

    def record_finding(self, run: AgentRun, severity: str, question: str,
                       finding: str) -> dict:
        if severity not in ('S1', 'S2', 'S3'):
            raise ValueError(f'severity must be S1, S2 or S3; got {severity!r}')
        self.runtime.call(run, 'TOOL-12', severity=severity)
        row = {'id': f'CH-{len(self.findings) + 1:02d}', 'severity': severity,
               'question': question, 'finding': finding, 'run': run.id}
        self.findings.append(row)
        return row
