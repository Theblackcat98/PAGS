# PAGS: Portable Agent Guide System

PAGS is a portable agent guide system: a small set of records, rules and tools
for repositories where AI coding agents do much of the work. Agents forget
between sessions, add scope nobody asked for, change architecture quietly and
invent reasons for old code. PAGS gives a project one written answer to each
question an agent should ask before changing anything, a loop that keeps those
answers current, and a checker that fails when the records stop agreeing. It
works for new (greenfield) and existing (brownfield) projects and needs only
Python 3.10 or later.

A visual guide to the design is published from `docs/index.html` at
<https://theblackcat98.github.io/PAGS/> (GitHub Pages, served from the `/docs`
folder of `main`). Keep it in sync when the design changes.

## Quick start

```text
git clone https://github.com/Theblackcat98/PAGS.git
./PAGS/scripts/install-pags.py /path/to/your-repo
cd /path/to/your-repo
python3 .pags/check.py
```

Then fill in the charter, add the first outcomes to `.pags/WORK.md`, and fill
the commands in `AGENTS.md`. The checker lists every placeholder still left.

## What gets installed

```text
AGENTS.md              How agents work: loop, change table, authority, commands
README.md              What users rely on
.pags/CHARTER.md       What must not change casually
.pags/WORK.md          Now block, approved outcomes, and tasks nested under them
.pags/DECISIONS.md     Why choices were made; temporary exceptions
.pags/ARCHITECTURE.md  What exists today; known debt
.pags/DESIGN.md        Optional: interface and design contract
.pags/check.py         The records checker
```

Each record answers one question, so each fact has one home:

| Record | Answers |
|---|---|
| Charter | What must not change casually? |
| Work | What outcomes are approved, and what is being done now? |
| Decisions | Why was this chosen, and which rules are bent for now? |
| Architecture | What exists today? |
| README | What do users rely on? |

Finished entries move to `WORK-ARCHIVE.md` and `DECISIONS-ARCHIVE.md`, which
agents create on first use.

## How it works

Every record entry is one headline line, optionally followed by indented
`key: value` detail:

```text
- R-003 [approved] Offline edits sync when the network returns
  - T-014 [doing] Queue writes while offline -> D-012
    done-when: queued writes survive an app restart
- D-012 [accepted 2026-09-20] Use SQLite for the offline write queue -> R-003
  why: writes must survive restarts on mobile
  cost: adds a native build step
```

IDs are `R-` outcomes, `T-` tasks, `D-` decisions and exceptions, and `A-`
known debt. Tasks sit indented under their outcome, and a new decision names
the one it `replaces`, so links point one way only.

Agents follow the loop in `AGENTS.md`: read the Now block, look up the change
in the change table and read only what it lists, stop and propose if the work
is outside an approved outcome, make the smallest coherent change, run the
commands and the checker, update the records the table names, and rewrite the
Now block for the next session. Agents may propose. Only the maintainer
approves outcomes, decisions, exceptions and charter changes.

The change table, statuses and rules live in the templates themselves; see
[`.pags-templates/AGENTS.md`](.pags-templates/AGENTS.md) and each record's
header comment.

## Adoption

A **greenfield** project starts with a one-page charter and three to seven
outcomes, and adds ARCHITECTURE once real structure exists.

A **brownfield** project does not treat existing code as approved design. It
describes what exists in ARCHITECTURE, marks unconfirmed facts `(observed)`
or `(unknown)`, and backfills only important decisions, writing
`why: unknown` rather than guessing. Each existing problem goes to one
record:

| Problem | Record |
|---|---|
| Accepted legacy | ARCHITECTURE known debt `[accepted]` |
| Planned migration | WORK outcome, plus known debt `[planned]` |
| Temporary exception | DECISIONS `[exception until DATE]` |
| Defect | WORK task under Unplanned |

Step-by-step checklists for both are in
[`.pags-templates/TEMPLATE-GUIDE.md`](.pags-templates/TEMPLATE-GUIDE.md).

## Installer

`scripts/install-pags.py [target]` installs into the target directory (the
current directory by default). It:

- detects greenfield or brownfield and asks the user to confirm;
- defaults to the minimal profile; `--profile core` and `--profile complete`
  install more;
- previews every file it will create, replace, update or keep;
- fills the project name and the charter's creation date;
- keeps existing documents by default, and backs them up before an explicit
  replacement (`--conflict backup`);
- always installs `.pags/check.py`, and on a rerun updates a changed copy
  after backing it up;
- can be rerun safely.

Use `--dry-run` to see the plan without changing files and `--yes` for a
non-interactive install. `--help` lists every option.

## Records checker

`python3 .pags/check.py` checks that the records agree with each other. Run
it before each commit and in CI. It fails on duplicate or misplaced IDs,
unknown statuses, links to missing IDs, tasks outside an approved outcome,
done tasks without evidence, expired exceptions, broken `replaces` pairs, and
unfilled `{{placeholders}}` once the charter is accepted. It warns about
placeholders while the charter is a draft and about finished entries that
should be archived. `--strict` turns warnings into errors. The full list is
in the template guide.

The canonical copy is `scripts/pags-check.py`, which can also be run from a
PAGS checkout against any repository: `scripts/pags-check.py /path/to/repo`.

## Repository layout

```text
.pags-templates/   Templates the installer copies, and TEMPLATE-GUIDE.md
scripts/           install-pags.py and pags-check.py
tests/             Tests; run with python3 -m unittest discover -s tests
docs/              The GitHub Pages visual guide
```

---

## Design notes

This part is for people working on PAGS itself: why it is shaped this way,
what has been decided, and what is still open. PAGS generalizes the
documentation system of Veritas, a separate project, so that it can be
adopted by any repository. It does not implement Veritas features.

### Approach

- **Separate the questions.** Why the project exists (charter), what is
  approved (work), why a choice was made (decisions) and what is true now
  (architecture) are different questions. Mixing them lets intended design
  and observed reality blur together.
- **One source of truth per question.** A fact written twice drifts, so
  records do not repeat each other: commands appear only in `AGENTS.md`,
  statuses only on the entry's headline, and links point one way.
- **Honesty about existing code.** Observed behavior is recorded as observed,
  and unknown reasons stay unknown.
- **Supersede, don't edit.** Accepted decisions are never rewritten; a new
  decision replaces the old one.
- **Bounded exceptions.** A bent rule has an end date and an exit condition.
- **Scope gates.** Agents propose; the maintainer approves.
- **Checked, not only written.** Agents follow written advice less reliably
  as their context fills up, so the rules that can be checked mechanically
  are checked by `pags check`.
- **Start small.** A greenfield project does not need a large documentation
  system on day one.

### Decisions

**2026-09-27: template format.** Chosen by the maintainer to make the records
cheaper for agents to read and easier for humans to scan.

1. **Four records (plus optional DESIGN) instead of nine.** ROADMAP and
   TASKS merged into WORK. EXCEPTIONS and DEPENDENCIES merged into DECISIONS
   (an exception is a decision with an end date; versions stay in the
   lockfile). QUALITY merged into AGENTS.md, which is the only place commands
   are listed. CHARTER and ARCHITECTURE stay separate to keep intended and
   observed apart.
2. **Headline plus optional detail.** One line per entry works as the index,
   so summary tables and two-way links are gone.
3. **Archive files.** Finished entries move to `*-ARCHIVE.md` so live files
   stay small.
4. **Short bracketed statuses.** Tasks use five statuses instead of eight;
   Verified and Done are merged, and done requires `evidence:`.

Consequences: placeholders changed to `{{…}}` because `[...]` marks status;
examples moved into HTML comments; the installer fills the date only in the
charter header and no longer writes the local repository path. The installed
complete set dropped from about 3,000 to about 1,700 words.

**2026-09-27: records checker.**

1. **Stdlib-only Python, installed into the project.** The installer copies
   `scripts/pags-check.py` to `.pags/check.py` in every profile, so hooks and
   CI work without a PAGS checkout. It is a managed file: reruns update a
   changed copy after a backup, unlike documents, which are kept.
2. **Placeholders warn in a draft and fail once the charter is accepted.** A
   fresh install passes, and accepting the charter is the point where
   unfilled fields become a defect. Files that legitimately contain `{{` can
   opt out.
3. **Errors are rules the templates state as "must"; warnings are
   housekeeping.** Archiving finished entries and linking planned debt to an
   outcome are warnings.
4. **Output is `path:line: level: message`** so editors and agents can jump
   to each problem, followed by a one-line summary.

**2026-09-27: this README.** One file in two parts: user documentation first,
design notes after, instead of a separate design document.

**2026-09-27: the name.** PAGS stands for Portable Agent Guide System.
"Portable" names what PAGS adds to the Veritas system it generalizes: the
same records and loop, adoptable by any repository, new or existing.

### Open questions

- Where the records live: `.pags/` or `docs/pags/`
  ([#17](https://github.com/Theblackcat98/PAGS/issues/17)). The checker
  takes `--records-dir`, so either works.
- An ID scheme that cannot collide across parallel branches
  ([#13](https://github.com/Theblackcat98/PAGS/issues/13)). The checker
  catches collisions after a merge but does not prevent them.
- Where the approver is named
  ([#11](https://github.com/Theblackcat98/PAGS/issues/11)).

The full list of follow-ups is tracked in
[#1](https://github.com/Theblackcat98/PAGS/issues/1).

### Next steps

1. Fix the installer's Enter-key default
   ([#2](https://github.com/Theblackcat98/PAGS/issues/2)) and extend the
   tests to the rest of the installer
   ([#9](https://github.com/Theblackcat98/PAGS/issues/9)).
2. Pilot PAGS on one real greenfield and one real brownfield repository
   ([#24](https://github.com/Theblackcat98/PAGS/issues/24)), running the
   checker in each, and adjust the error and warning split from what it
   finds.
