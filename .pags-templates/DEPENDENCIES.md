# [PROJECT_NAME] Dependencies

> Keep this inventory focused on direct, intentional, and architecturally
> significant dependencies. Record why each dependency exists and how it is
> reviewed.

- **Owner:** [OWNER_OR_TEAM]
- **Last reviewed:** YYYY-MM-DD
- **Update policy:** [POLICY]

## Dependency inventory

| Dependency | Version or range | Purpose | Owner | License | Security status | Last reviewed |
|---|---|---|---|---|---|---|
| [DEPENDENCY] | [VERSION] | [PURPOSE] | [OWNER] | [LICENSE] | [STATUS] | YYYY-MM-DD |

## Adding a dependency

Before adding a dependency:

1. Confirm that the existing platform or standard library cannot meet the need.
2. Record the alternatives considered.
3. Add a decision entry in `.pags/DECISIONS.md`.
4. Check maintenance activity, license, security history, and platform support.
5. Update this inventory and the project's lockfile or manifest.
6. Add the verification needed to detect breakage.

## Removing or replacing a dependency

- **Reason:** [REASON]
- **Replacement:** [REPLACEMENT_OR_NONE]
- **Migration risks:** [RISKS]
- **Removal plan:** [PLAN]
- **Related decision:** [D-XXX]

## Update policy

- **Patch updates:** [POLICY]
- **Minor updates:** [POLICY]
- **Major updates:** [POLICY]
- **Security updates:** [POLICY]
- **Automated updates:** [TOOL_OR_NONE]

## Known concerns

| Dependency | Concern | Impact | Review date | Owner |
|---|---|---|---|---|
| [DEPENDENCY] | [CONCERN] | [IMPACT] | YYYY-MM-DD | [OWNER] |
