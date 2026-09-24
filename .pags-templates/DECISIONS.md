# [PROJECT_NAME] Decision Log

> Append-only record of important product, architecture, dependency, platform,
> security, and durable UX choices. Do not rewrite the historical decision body.
> To change a decision, add a new entry that supersedes it.

- **Owner:** [OWNER_OR_TEAM]
- **Last reviewed:** YYYY-MM-DD

## Rules

1. One entry records one meaningful choice.
2. Record the choice before implementation when it is expensive to reverse.
3. Include meaningful alternatives and their trade-offs.
4. Keep old entries intact. Add a superseding entry when direction changes.
5. Link decisions to roadmap items and tasks.
6. Record implementation and verification state separately from the decision's
   historical status.

## Status vocabulary

- **Proposed:** Under consideration.
- **Accepted:** Approved direction.
- **Rejected:** Considered and declined.
- **Superseded:** Replaced by a later decision.

## Decision index

| ID | Date | Status | Area | Summary | Supersedes | Superseded by |
|---|---|---|---|---|---|---|
| D-001 | YYYY-MM-DD | proposed | [AREA] | [SUMMARY] | — | — |

## Decision template

### D-00X — [Decision title]

- **Date:** YYYY-MM-DD
- **Status:** [PROPOSED | ACCEPTED | REJECTED | SUPERSEDED]
- **Owner:** [OWNER]
- **Reviewers:** [REVIEWERS_OR_NONE]
- **Area:** [PRODUCT | ARCHITECTURE | DEPENDENCY | SECURITY | UX | OPERATIONS]
- **Supersedes:** [D-XXX_OR_NONE]
- **Superseded by:** [D-XXX_OR_NONE]
- **Related roadmap items:** [R-XXX]
- **Related tasks:** [T-XXX]

#### Context

[What problem or constraint requires a choice? Include relevant constraints and
assumptions.]

#### Options considered

- **[OPTION_A]:** [DESCRIPTION, BENEFITS, COSTS]
- **[OPTION_B]:** [DESCRIPTION, BENEFITS, COSTS]
- **[OPTION_C]:** [DESCRIPTION, BENEFITS, COSTS]

#### Decision

[State the chosen direction clearly and precisely.]

#### Consequences

- **Benefits:** [BENEFIT]
- **Costs or risks:** [COST_OR_RISK]
- **Follow-up:** [REQUIRED_ACTION_OR_NONE]

#### Affected areas

[Components, interfaces, dependencies, documentation, or operational areas.]

#### Implementation and verification

- **Implementation status:** [NOT_STARTED | IN_PROGRESS | IMPLEMENTED]
- **Verification evidence:** [TESTS_CHECKS_OR_LINKS]
- **Last verified:** YYYY-MM-DD

## Supersession policy

A new decision must identify the old decision, explain why the direction
changed, and describe migration or compatibility work. Do not silently rewrite
the old entry.
