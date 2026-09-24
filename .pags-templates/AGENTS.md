# AGENTS.md — [PROJECT_NAME]

## Project snapshot

- **Purpose:** [One sentence describing the project.]
- **Stack:** [Languages, frameworks, and important runtimes.]
- **Repository root:** `[PATH]`
- **User documentation:** `README.md`
- **Task source:** `.pags/TASKS.md` or [EXTERNAL_TRACKER]
- **Primary maintainer:** [OWNER_OR_TEAM]

## Read before working

Read the documents that apply to the change:

1. `.pags/CHARTER.md`
2. `.pags/ARCHITECTURE.md`, if it exists
3. `.pags/ROADMAP.md`
4. `.pags/DECISIONS.md`
5. `.pags/DESIGN.md`, `.pags/QUALITY.md`, or other relevant documents
6. The nearest `AGENTS.md` when working inside a subproject or legacy area

For a brownfield project, read the architecture and known-debt sections before
assuming that existing behavior is intentional.

## Instruction precedence

- The nearest applicable `AGENTS.md` controls local working instructions.
- The charter defines product identity, boundaries, and non-goals.
- The roadmap defines approved outcomes and scope.
- Decisions explain the constraints created by important choices.
- The architecture document describes the current implementation.
- If a request conflicts with these documents, prepare a proposal instead of
  bypassing them.

## Working rules

1. Classify the work as a bug fix, feature, refactor, dependency, architecture,
   security, documentation, or maintenance change.
2. Check scope before implementation.
3. Create or update a task for work that is not a trivial, obvious correction.
4. Record a decision before an expensive, difficult-to-reverse, public-interface,
   dependency, architectural, or durable UX choice.
5. Keep changes within the approved boundaries and existing project conventions.
6. Prefer the smallest coherent change that solves the stated problem.
7. Do not add dependencies, configuration, or abstractions without a stated need.
8. Keep user documentation and implementation behavior synchronized.
9. Never commit secrets, credentials, tokens, or private keys.

## Change gates

| Change | Required record |
|---|---|
| New product capability | Roadmap item and task |
| Important technical or product choice | Decision entry |
| New dependency | Decision entry and dependency record |
| Architecture or public interface change | Decision entry and architecture update |
| User-visible behavior | User documentation update |
| Temporary rule deviation | Exception record with an exit condition |

Bug fixes, tests, formatting, and documentation corrections may proceed without
a new roadmap item when they do not change approved scope.

## Project commands

- **Install:** `[COMMAND]`
- **Build:** `[COMMAND]`
- **Test:** `[COMMAND]`
- **Format:** `[COMMAND]`
- **Lint/typecheck:** `[COMMAND]`
- **Run:** `[COMMAND]`
- **Release:** `[COMMAND]`

Use the repository's existing commands. Do not invent a second toolchain or
configuration for a change without a decision.

## Definition of done

A change is complete when:

- [ ] The requested behavior is implemented within scope.
- [ ] Relevant automated tests pass.
- [ ] Build, format, lint, and type checks pass when available.
- [ ] Failure and edge cases are handled deliberately.
- [ ] Required decision, task, exception, and documentation records are updated.
- [ ] User-facing documentation matches actual behavior.
- [ ] Verification evidence is recorded in the task or review artifact.
- [ ] No unrelated changes or secrets are included.

## Exceptions and escalation

Record temporary deviations in `.pags/EXCEPTIONS.md` when that document is in
use. Include the reason, scope, owner, review date, and exit condition. Stop and
ask for a decision when the charter, roadmap, or a durable decision would need
to change.
