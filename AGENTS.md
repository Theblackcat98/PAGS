# AGENTS.md — PAGS

## Project purpose

PAGS is a meta project. It designs a portable project constitution and delivery system inspired by `../veritas`, but it is not the Veritas application and does not implement Veritas features.

## Working rules

1. Read `README.md` before doing work. It is the current source of context, findings, open questions, and next steps.
2. Treat `../veritas` as a read-only reference unless the user explicitly asks to change it.
3. Do not add `CHARTER.md`, `ROADMAP.md`, `TASKS.md`, `DECISIONS.md`, or other governance files to PAGS unless explicitly requested. The proposed system is a design subject, not automatically PAGS's own process.
4. Keep work focused on the meta problem: making the Veritas-style system portable across greenfield and brownfield projects.
5. Work directly. Do not use subagents unless the user requests them.
6. Preserve the distinction between current project behavior, proposed future behavior, and unresolved design questions.
7. When new durable context is produced, update `README.md` rather than creating parallel documentation by default.
8. Do not modify application code or project files outside PAGS without explicit instruction.

## Research reference

When the Veritas implementation is relevant, inspect:

- `../veritas/AGENTS.md`
- `../veritas/docs/CHARTER.md`
- `../veritas/docs/ROADMAP.md`
- `../veritas/docs/DECISIONS.md`
- Other Veritas files only when they answer a specific design question.

## Continuation

At the end of a substantial work session, keep `README.md` useful for a future session by recording:

- What was learned or changed
- Decisions made
- Open questions
- Recommended next step

Do not copy the entire conversation into the repository.
