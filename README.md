## What PAGS is:

It is a small **project constitution plus delivery loop**:

- `AGENTS.md` — operating instructions for agents.
- `.pags/CHARTER.md` — identity, goals, non-goals, and principles.
- `.pags/ROADMAP.md` — scope authorization and progress.
- `.pags/DECISIONS.md` — append-only rationale and supersession history.
- `README.md` — current user-facing contract.

The design separates **why**, **what is allowed**, **why a choice was made**, and **what is currently true**.

To keep this separation useful, the roadmap should describe outcomes and milestones, while executable work belongs in the task system. Scope, rationale, current architecture, and user-facing behavior should each have one source of truth.

## Portable version

I would generalize this as a **Project Constitution + Delivery System**:

```text
AGENTS.md              How agents work
.pags/CHARTER.md       What the project is and why it exists; boundaries
.pags/ROADMAP.md       Approved outcomes and milestones
.pags/TASKS.md         Executable todos and current work
.pags/DECISIONS.md     Why important choices were made
.pags/ARCHITECTURE.md  What the system currently looks like
README.md              How users operate it
```

Optional documents should be added only when needed: `.pags/DESIGN.md`, `.pags/DEPENDENCIES.md`, `.pags/QUALITY.md`, and `.pags/EXCEPTIONS.md`.

Each concern gets one source of truth:

- Roadmap answers: **what outcomes are approved?**
- Tasks answer: **what work is being done now?**
- Decisions answer: **why was this chosen?**
- Architecture answers: **what exists today?**
- Charter answers: **what must not be changed casually?**

Use IDs such as `R-001` for roadmap outcomes, `T-001` for tasks, and `D-001` for decisions. Tasks should link to roadmap items and decisions.

## Recommended workflow

1. Classify the change: bug, feature, refactor, dependency, architecture, security, or documentation.
2. Read the applicable `AGENTS.md`, charter, architecture, roadmap, and relevant decisions.
3. Check scope. If it conflicts with the charter or roadmap, propose a scope change instead of implementing it.
4. Create a task with acceptance criteria, dependencies, and verification steps.
5. Record a decision before expensive, difficult-to-reverse, dependency, public-interface, or architectural choices.
6. Implement the smallest coherent change.
7. Run the project’s format, lint, build, and test commands.
8. Update the relevant documents.
9. Mark the task verified only after evidence exists.

A useful rule is:

- New feature: roadmap item + task; decision when needed.
- Bug fix: task + regression test; decision only if behavior or architecture changes.
- Dependency: decision + manifest/lockfile update.
- Architecture change: decision + architecture update.
- User-facing change: README or user documentation update.
- Scope/non-goal change: charter + roadmap + decision.

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
Current reality  -> ARCHITECTURE.md
Intended future  -> CHARTER.md + ROADMAP.md
Allowed exception -> TASKS.md
Reason for choice -> DECISIONS.md
```

I recommend formalizing this as a reusable template/bootstrap kit with separate greenfield and brownfield checklists.

## Reusable templates

The reusable document templates are in `.pags-templates/`. Start with
`.pags-templates/TEMPLATE-GUIDE.md` for the file map and greenfield/brownfield
adoption steps.

The core templates are:

- `AGENTS.md` — working instructions for contributors and agents
- `README.md` — user-facing project documentation
- `CHARTER.md` — mission, goals, non-goals, and durable constraints
- `ROADMAP.md` — approved outcomes and milestones
- `TASKS.md` — executable work and task status
- `DECISIONS.md` — append-only decision history
- `ARCHITECTURE.md` — current system structure and behavior

Optional templates cover design, dependencies, quality, and exceptions.

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
- fills the project name, repository path, and current date;
- keeps existing files by default;
- supports timestamped backups before explicit replacement; and
- can be rerun without changing installed documents.

Use `--dry-run` to inspect the installation plan without changing files. Use
`--yes` for non-interactive minimal installation, or choose `--profile core`
and `--profile complete` for wider adoption. Run
`./scripts/install-pags.py --help` for all options.

The recommended next step is to validate the installer in one real greenfield
and one real brownfield repository.
