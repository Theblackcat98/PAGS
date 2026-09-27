## What PAGS is:

It is a small **project constitution plus delivery loop**:

- `AGENTS.md` — operating instructions for agents.
- `.pags/CHARTER.md` — identity, goals, non-goals, and principles.
- `.pags/WORK.md` — approved outcomes, current tasks, and the session handoff.
- `.pags/DECISIONS.md` — append-only rationale, supersession history, and exceptions.
- `README.md` — current user-facing contract.

The design separates **why**, **what is allowed**, **why a choice was made**, and **what is currently true**.

To keep this separation useful, the roadmap should describe outcomes and milestones, while executable work belongs in the task system. Scope, rationale, current architecture, and user-facing behavior should each have one source of truth.

## Portable version

I would generalize this as a **Project Constitution + Delivery System**:

```text
AGENTS.md              How agents work: loop, change table, authority, commands
.pags/CHARTER.md       What must not change casually
.pags/WORK.md          Now block, approved outcomes, and tasks nested under them
.pags/DECISIONS.md     Why choices were made; temporary exceptions
.pags/ARCHITECTURE.md  What the system currently looks like; known debt
README.md              How users operate it
```

`.pags/DESIGN.md` is the only optional document. Finished entries move to
`WORK-ARCHIVE.md` and `DECISIONS-ARCHIVE.md`, which agents create on first use.

Each concern gets one source of truth:

- Work answers: **what outcomes are approved, and what is being done now?**
- Decisions answer: **why was this chosen, and which rules are bent for now?**
- Architecture answers: **what exists today?**
- Charter answers: **what must not be changed casually?**

Entries are one headline line, `- ID [status] summary -> links`, with optional
indented `key: value` detail. IDs are `R-` outcomes, `T-` tasks, `D-`
decisions and exceptions, and `A-` known debt. Tasks sit indented under their
outcome; a new decision names the one it `replaces`. Links point one way only.

## Recommended workflow

1. Read the Now block in `.pags/WORK.md`.
2. Classify the change and read only what its row in the AGENTS.md change table lists.
3. Check scope. If the change is outside an approved outcome, add a `[proposed]` entry and ask the maintainer instead of implementing it.
4. Create or update the task under its outcome, with `done-when:` criteria.
5. Record a decision before expensive, difficult-to-reverse, dependency, public-interface, or architectural choices.
6. Implement the smallest coherent change.
7. Run the project’s format, lint, build, and test commands.
8. Update the records the change table names, and archive finished entries.
9. Mark the task done only with `evidence:` recorded.
10. Rewrite the Now block for the next session.

A useful rule is:

- New feature: approved WORK outcome + task; decision when needed.
- Bug fix: task + regression test; decision only if behavior or architecture changes.
- Dependency: decision + manifest/lockfile update.
- Architecture change: decision + architecture update.
- User-facing change: README or user documentation update.
- Scope/non-goal change: charter + WORK outcome + decision, approved by the maintainer.

## Greenfield adoption

Start small:

1. Write a one-page charter.
2. Define three to seven roadmap outcomes.
3. Add the first few tasks.
4. Record only decisions that are expensive to reverse.
5. Establish build, test, lint, and format commands early.
6. Add architecture documentation once the first real structure exists.

Do not create a large documentation system before the project needs it.

## Brownfield adoption

Do not treat existing code as automatically approved architecture.

1. Inventory the stack, commands, dependencies, tests, deployment, and current documentation.
2. Record observed behavior in `ARCHITECTURE.md`, not as intentional decisions.
3. Establish a test and CI baseline.
4. Backfill decisions only for important existing choices; mark unknown reasons as unknown.
5. Classify existing violations as:
   - accepted legacy behavior,
   - planned migration,
   - temporary exception,
   - or defect.
6. Give every exception a reason, owner, review date, and exit condition.
7. Apply the new rules to new work first, then improve legacy areas gradually.

The key distinction is:

```text
Current reality    -> ARCHITECTURE.md
Intended future    -> CHARTER.md + WORK.md
Allowed exception  -> DECISIONS.md  [exception until DATE]
Reason for choice  -> DECISIONS.md
```

Existing problems in a brownfield repo map to one record each: accepted legacy
to ARCHITECTURE known debt, planned migration to a WORK outcome, temporary
exception to DECISIONS, and defect to a WORK task.

I recommend formalizing this as a reusable template/bootstrap kit with separate greenfield and brownfield checklists.

## Reusable templates

The reusable document templates are in `.pags-templates/`. Start with
`.pags-templates/TEMPLATE-GUIDE.md` for the file map and greenfield/brownfield
adoption steps.

The core templates are:

- `AGENTS.md` — loop, change table, authority, commands, and definition of done
- `README.md` — user-facing project documentation
- `CHARTER.md` — mission, goals, non-goals, principles, and constraints
- `WORK.md` — Now block, outcomes, and tasks
- `DECISIONS.md` — decisions, exceptions, and dependency reasons
- `ARCHITECTURE.md` — current system structure and known debt

`DESIGN.md` is the only optional template.

## Guided installer

The dependency-free installer lives at `scripts/install-pags.py` and requires
Python 3.10 or later. From a PAGS checkout, run:

```text
./scripts/install-pags.py /path/to/repository
```

Omit the repository path to install into the current directory. The installer:

- detects greenfield or brownfield projects and lets the user confirm the mode;
- defaults to a minimal adoption profile;
- suggests optional documents from project markers;
- previews every create, replacement, and preserved file;
- fills the project name and the charter's creation date;
- keeps existing files by default;
- supports timestamped backups before explicit replacement; and
- can be rerun without changing installed documents.

Use `--dry-run` to inspect the installation plan without changing files. Use
`--yes` for non-interactive minimal installation, or choose `--profile core`
and `--profile complete` for wider adoption. Run
`./scripts/install-pags.py --help` for all options.

## Template format decisions (2026-09-27)

These were chosen by the maintainer to make the records cheaper for agents to
read and easier for humans to scan:

1. **Four records (plus optional DESIGN) instead of nine.** ROADMAP and TASKS merged into WORK.
   EXCEPTIONS and DEPENDENCIES merged into DECISIONS (an exception is a
   decision with an end date; versions stay in the lockfile). QUALITY merged
   into AGENTS.md, which is now the only place commands are listed. CHARTER
   and ARCHITECTURE stay separate to keep intended and observed apart.
2. **Headline plus optional detail.** One line per entry works as the index,
   so summary tables and two-way links are gone.
3. **Archive files.** Finished entries move to `*-ARCHIVE.md` so live files
   stay small.
4. **Short bracketed statuses.** Tasks use five statuses instead of eight;
   Verified and Done are merged, and done requires `evidence:`.

Consequences: placeholders changed to `{{…}}` because `[...]` now marks
status; examples moved into HTML comments; the installer fills the date only
in the charter header and no longer writes the local repository path. The
installed complete set dropped from about 3,000 to about 1,700 words, and a
blank decision entry from about 140 words to a few lines.

Open questions: where the records live (`.pags/` or `docs/pags/`), and
whether IDs need a scheme that cannot collide across parallel branches.
Follow-ups are tracked in the GitHub issues.

The recommended next step is to validate the installer and the new format in
one real greenfield and one real brownfield repository.
