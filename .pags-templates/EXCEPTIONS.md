# [PROJECT_NAME] Exceptions

> Use this document for temporary, explicit deviations from the charter,
> roadmap, agent rules, architecture boundaries, or quality requirements. Do not
> use it to bypass a requirement without an owner and an exit condition.

- **Owner:** [OWNER_OR_TEAM]
- **Last reviewed:** YYYY-MM-DD

## Exception policy

An exception must:

- identify the rule or boundary being relaxed;
- explain why the exception is necessary;
- state the smallest affected scope;
- name an owner;
- define compensating controls or risks;
- include an expiry or review date; and
- define the exit condition for removing the exception.

## Active exceptions

| ID | Rule or boundary | Reason | Scope | Owner | Review date | Exit condition | Status |
|---|---|---|---|---|---|---|---|
| E-001 | [RULE] | [REASON] | [SCOPE] | [OWNER] | YYYY-MM-DD | [CONDITION] | active |

## Exception template

### E-00X — [Short title]

- **Status:** [ACTIVE | EXPIRED | RESOLVED]
- **Rule or boundary:** [LINK_OR_DESCRIPTION]
- **Reason:** [WHY_THE_NORMAL_PATH_IS_INSUFFICIENT]
- **Scope:** [FILES_COMPONENTS_OR_ENVIRONMENTS]
- **Owner:** [OWNER]
- **Created:** YYYY-MM-DD
- **Review date:** YYYY-MM-DD
- **Expiry date:** YYYY-MM-DD
- **Compensating controls:** [CONTROLS_OR_NONE]

#### Risks

- [RISK]

#### Exit condition

[What must change before this exception can be closed?]

#### Resolution

[What changed, when it changed, and what evidence verifies it.]

## Emergency exceptions

Emergency exceptions may be recorded after the fact only when delaying action
would cause unacceptable harm. They still require an owner, compensating
controls, and a follow-up review date.
