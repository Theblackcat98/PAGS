# [PROJECT_NAME] Quality

> Define the checks that establish confidence in changes. Keep commands exact
> so contributors and automation run the same checks.

- **Owner:** [OWNER_OR_TEAM]
- **Last reviewed:** YYYY-MM-DD

## Quality gates

| Check | Command or procedure | Required | Failure behavior |
|---|---|---|---|
| Format | `[COMMAND]` | yes | [BEHAVIOR] |
| Lint | `[COMMAND]` | yes | [BEHAVIOR] |
| Typecheck | `[COMMAND]` | when available | [BEHAVIOR] |
| Build | `[COMMAND]` | yes | [BEHAVIOR] |
| Unit tests | `[COMMAND]` | yes | [BEHAVIOR] |
| Integration tests | `[COMMAND]` | when applicable | [BEHAVIOR] |
| Documentation checks | `[COMMAND]` | when applicable | [BEHAVIOR] |

## Test levels

### Unit tests

[What must be tested in isolation and what coverage is expected?]

### Integration tests

[Which component boundaries, external interfaces, or workflows require
integration tests?]

### End-to-end tests

[Which user journeys or system boundaries require end-to-end tests?]

### Manual verification

[List checks that cannot be automated reliably, including supported platforms,
accessibility, performance, or visual behavior.]

## Environment matrix

| Environment | Versions | Purpose | Status |
|---|---|---|---|
| [ENVIRONMENT] | [VERSIONS] | [PURPOSE] | supported |

## CI requirements

- Pull requests run: [CHECKS]
- Required status checks: [CHECKS]
- Branch protection: [POLICY]
- Release checks: [CHECKS]

## Security and reliability checks

- [SECRET_SCANNING_OR_NONE]
- [DEPENDENCY_SCANNING_OR_NONE]
- [STATIC_ANALYSIS_OR_NONE]
- [RECOVERY_OR_FAILURE_TESTING]

## Definition of quality

A change is quality-verified when:

- [ ] Required automated checks pass.
- [ ] Relevant regression tests exist and pass.
- [ ] Failure behavior is explicit and tested.
- [ ] User-facing documentation is current.
- [ ] Verification evidence is recorded in the task or review artifact.
