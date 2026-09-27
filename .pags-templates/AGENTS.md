# AGENTS.md: {{PROJECT_NAME}}

{{One sentence describing the project.}}

- Stack: {{languages, frameworks, runtimes}}
- Maintainer: {{name or handle}}. Approves outcomes, decisions, exceptions and charter changes.

## Records

| File | Answers |
|---|---|
| `.pags/CHARTER.md` | What must not change casually? |
| `.pags/WORK.md` | What is approved, and what is being done now? |
| `.pags/DECISIONS.md` | Why was this chosen? Which rules are bent for now? |
| `.pags/ARCHITECTURE.md` | What exists today? Created once real structure exists. |
| `README.md` | What do users rely on? |

Entries are one line each, `- ID [status] summary -> links`, with optional
indented `key: value` detail. List every entry with
`grep -nE '^\s*- [RTDA]-[0-9]+' .pags/*.md`. Each file's header comment gives
its statuses and rules, and `python3 .pags/check.py` enforces them.

## Loop

1. Read the Now block in `.pags/WORK.md`.
2. Find the change in the table below and read only what it lists.
3. If the change is outside an approved outcome, add a `[proposed]` entry,
   ask the maintainer, and stop until it is approved.
4. Add or update the task under its outcome.
5. Record a decision before a hard-to-reverse choice.
6. Make the smallest coherent change.
7. Run the checks under Commands until they pass.
8. Update the records the table names. Move finished entries to the archive.
9. Rewrite the Now block.

## Changes

| Change | Read first | Then update |
|---|---|---|
| New capability | Charter, Work | Outcome (maintainer approves), then a task |
| Scope or non-goal change | Charter, Work | Proposal to the maintainer, then Charter, Work and a decision |
| Architecture or public interface | Architecture, Decisions | Decision, Architecture |
| New or removed dependency | Decisions | Decision ("Add dependency: …"), lockfile |
| Refactor | Architecture, related decisions | Task; Architecture if structure changes |
| Security | Decisions, Architecture | Task; a decision if a policy changes |
| Bug fix | Architecture for the area | Task under Unplanned, regression test |
| User-visible behavior | README | README, in the same change |
| Temporary rule deviation | The rule being bent | Exception in Decisions (maintainer grants) |
| Formatting, typos, doc fixes | Nothing extra | Nothing, if scope is unchanged |

If a row names a record that does not exist yet, create it from the template.

## Authority

- Agents may propose outcomes and decisions, create and progress tasks inside
  approved outcomes, and record evidence, observations and unknowns.
- Only the maintainer may approve outcomes, accept decisions, grant or extend
  exceptions, and change the charter.
- When the maintainer approves something during a session, record it on the
  entry as `approved-by: NAME YYYY-MM-DD` and carry on.
- If a request conflicts with the charter or an accepted decision, write a
  proposal instead of implementing it.

## Commands

This is the only place commands are listed.

- Install: `{{command}}`
- Build: `{{command}}`
- Test: `{{command}}`
- Format: `{{command}}`
- Lint and typecheck: `{{command}}`
- Run: `{{command}}`
- Check records: `python3 .pags/check.py` (installed by PAGS; do not edit)

Use these commands. Adding a second toolchain or config needs a decision.

## Done means

- The change stays inside an approved outcome, or under Unplanned.
- Every command above that applies passes, including the records check.
- Each bug fix has a regression test.
- The records named in the change table are updated.
- README matches actual behavior.
- The task has `evidence:` with the command run and its result.
- No secrets and no unrelated changes are included.

<!-- Add project-specific quality rules here, e.g. required CI checks or manual platform checks. -->

## Local rules

- The nearest `AGENTS.md` in a subdirectory overrides this one for that area.
- Do not add dependencies, configuration or abstractions without a stated need.
- Never commit secrets, credentials, tokens or private keys.
