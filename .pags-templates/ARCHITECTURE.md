# [PROJECT_NAME] Architecture

> This document describes the current system, not the intended future. Record
> intentional changes in `.pags/DECISIONS.md` and planned outcomes in
> `.pags/ROADMAP.md`.

- **Status:** [DRAFT | CURRENT]
- **Owner:** [OWNER_OR_TEAM]
- **Last reviewed:** YYYY-MM-DD
- **Applies to:** [VERSION_OR_RELEASE]

## System context

[Describe the system boundary, users, external systems, and runtime context.]

## Repository map

| Path or component | Responsibility | Owner | Notes |
|---|---|---|---|
| [PATH] | [RESPONSIBILITY] | [OWNER] | [NOTES] |

## Components

### [Component name]

- **Responsibility:** [WHAT_IT_OWNS]
- **Inputs:** [INPUTS]
- **Outputs:** [OUTPUTS]
- **State:** [STATE_AND_LIFECYCLE]
- **Failure behavior:** [HOW_FAILURES_ARE_HANDLED]
- **Related decisions:** [D-XXX]

## Runtime and data flow

[Describe the main flows from input to output. Include important synchronous,
asynchronous, persistence, and error paths.]

```text
[ACTOR] -> [ENTRY_POINT] -> [PROCESSING] -> [OUTPUT]
```

## Interfaces and contracts

| Interface | Consumers | Providers | Contract | Version or compatibility |
|---|---|---|---|---|
| [INTERFACE] | [CONSUMERS] | [PROVIDERS] | [CONTRACT] | [VERSION] |

## Invariants

The following conditions must remain true:

- [INVARIANT]
- [INVARIANT]

## Platform and capability matrix

| Capability | Supported platforms | Unsupported behavior | Fallback |
|---|---|---|---|
| [CAPABILITY] | [PLATFORMS] | [BEHAVIOR] | [FALLBACK] |

## Dependencies

Link to `.pags/DEPENDENCIES.md` when that document is used. List only direct or
architecturally significant dependencies here.

## Operational characteristics

- **Performance:** [EXPECTATIONS_OR_UNKNOWN]
- **Security:** [REQUIREMENTS]
- **Privacy:** [DATA_HANDLING]
- **Reliability:** [RECOVERY_OR_DEGRADATION]
- **Observability:** [LOGS_METRICS_OR_UNKNOWN]

## Known debt and uncertainty

| ID | Observation | Impact | Status | Exit condition |
|---|---|---|---|---|
| A-001 | [OBSERVED_CONDITION] | [IMPACT] | accepted | [CONDITION] |

For brownfield projects, mark facts as **observed**, **intended**, or
**unknown** until their rationale is confirmed. Do not invent historical
intent.

## Update rule

Update this document when the current structure, interfaces, invariants, or
operational behavior changes. Link the corresponding decision and task.
