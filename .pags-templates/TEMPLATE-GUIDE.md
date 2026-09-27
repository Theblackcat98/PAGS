# PAGS template set

Templates for a project using the PAGS project constitution and delivery loop.

## Files

| Template | Installed at | Answers |
|---|---|---|
| `AGENTS.md` | `AGENTS.md` | How should I work here? Loop, change table, authority, commands, definition of done |
| `README.md` | `README.md` | What do users rely on? |
| `CHARTER.md` | `.pags/CHARTER.md` | What must not change casually? |
| `WORK.md` | `.pags/WORK.md` | What is approved, and what is being done now? Now block, outcomes, tasks |
| `DECISIONS.md` | `.pags/DECISIONS.md` | Why was this chosen? Which rules are bent for now? Includes exceptions and dependency reasons |
| `ARCHITECTURE.md` | `.pags/ARCHITECTURE.md` | What exists today? Includes known debt |
| `DESIGN.md` (optional) | `.pags/DESIGN.md` | What should the interface feel like? |

`WORK-ARCHIVE.md` and `DECISIONS-ARCHIVE.md` are created by agents the first
time an entry is finished or replaced. They have no template.

The installer also copies `scripts/pags-check.py` to `.pags/check.py` in every
profile. It is a tool, not a template: rerunning the installer updates a
changed copy after backing it up.

## Entry format

Every record entry is one headline line, optionally followed by indented
`key: value` detail lines:

```text
- R-003 [approved] Offline edits sync when the network returns
  approved-by: sam 2026-09-20
  - T-014 [doing] Queue writes while offline -> D-012
    done-when: queued writes survive an app restart
- D-012 [accepted 2026-09-20] Use SQLite for the offline write queue -> R-003
  why: writes must survive restarts on mobile; IndexedDB has no Node support
  cost: adds a native build step
```

| Prefix | Record | Statuses |
|---|---|---|
| `R-` | Outcome, in WORK | proposed, approved, doing, done, dropped |
| `T-` | Task, in WORK | todo, doing, blocked, done, dropped |
| `D-` | Decision or exception, in DECISIONS | proposed, accepted, rejected, replaced, exception until DATE, resolved |
| `A-` | Known debt, in ARCHITECTURE | accepted, planned |

The headline lines are the index. There are no summary tables to keep in
sync, and links point one way: a task sits under its outcome, and a new
decision names the one it `replaces`.

Placeholders use `{{…}}` so that `grep -rn '{{' AGENTS.md README.md .pags/`
finds every field that still needs filling. Examples live inside HTML
comments so agents do not mistake them for real entries.

## Checking the records

`python3 .pags/check.py` (Python 3.10 or later, no dependencies) reads
`AGENTS.md`, `README.md` and every `.pags/*.md` file, ignoring HTML comments.
Run it before each commit and in CI. It exits 1 when it finds an error:

- an ID used twice (archives included) or placed in the wrong file
- a status outside its prefix's list, or a malformed date
- a link, `replaces:` or `blocked-by:` that names a missing ID
- a task that is not under an outcome or under Unplanned, or that is active
  under an outcome that is not approved
- a `[done]` task without `evidence:`
- an exception past its end date or without `exit:`
- `replaces: D-x` where D-x is not `[replaced]`, or a `[replaced]` decision
  that nothing replaces
- unfilled `{{placeholders}}` once the charter says `Status: accepted`

It warns about unfilled placeholders while the charter is a draft, finished
entries still in live files, active entries in an archive, and `[planned]`
debt without an outcome link. `--strict` turns warnings into errors. A file
that legitimately contains `{{`, such as a README documenting a template
language, can opt out of the placeholder check with
`<!-- pags: no-placeholder-check -->`.

## Adoption

From a PAGS checkout, run the guided installer:

```text
./scripts/install-pags.py /path/to/repository
```

### Greenfield

1. Fill in the charter before choosing a stack.
2. Add three to seven outcomes to WORK and get them approved.
3. Fill in the commands in AGENTS.md as soon as they exist.
4. Record only decisions that are expensive to reverse.
5. Add ARCHITECTURE once the first real structure exists.

### Brownfield

1. Inventory the stack, commands, tests and deployment.
2. Describe what exists in ARCHITECTURE, marking unconfirmed facts
   `(observed)` or `(unknown)`.
3. Establish a test and CI baseline.
4. Backfill decisions only for important choices. Write `why: unknown` rather
   than guessing.
5. Sort each existing problem into one record:
   - accepted legacy: ARCHITECTURE known debt `[accepted]`
   - planned migration: an outcome in WORK, plus known debt `[planned]`
   - temporary exception: DECISIONS `[exception until DATE]`
   - defect: a task under Unplanned in WORK
6. Apply the rules to new work first. Improve legacy areas gradually.

## Customization

A project may rename sections or add domain-specific records, but it should
keep one source of truth for scope, work, decisions, current architecture and
user documentation.
