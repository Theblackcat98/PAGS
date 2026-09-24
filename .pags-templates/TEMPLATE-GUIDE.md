# PAGS Template Set

This directory contains the reusable document templates for a project using the
PAGS project constitution and delivery system.

## Core documents

| File | Copy to | Purpose |
|---|---|---|
| `AGENTS.md` | `AGENTS.md` | Working instructions for contributors and agents |
| `README.md` | `README.md` | User-facing project documentation |
| `CHARTER.md` | `.pags/CHARTER.md` | Mission, goals, non-goals, and durable constraints |
| `ROADMAP.md` | `.pags/ROADMAP.md` | Approved outcomes and milestones |
| `TASKS.md` | `.pags/TASKS.md` | Executable work and task status |
| `DECISIONS.md` | `.pags/DECISIONS.md` | Append-only decision history |
| `ARCHITECTURE.md` | `.pags/ARCHITECTURE.md` | Current system structure and behavior |

## Optional documents

Use these only when the project needs them:

| File | Copy to | Purpose |
|---|---|---|
| `DESIGN.md` | `.pags/DESIGN.md` | Durable user experience or interface language |
| `DEPENDENCIES.md` | `.pags/DEPENDENCIES.md` | Intentional dependency inventory and update policy |
| `QUALITY.md` | `.pags/QUALITY.md` | Test, CI, security, and verification policy |
| `EXCEPTIONS.md` | `.pags/EXCEPTIONS.md` | Temporary deviations with owners and exit conditions |

## Adoption

### Greenfield

1. Copy the core templates.
2. Fill in the charter before selecting implementation details.
3. Define a small set of roadmap outcomes.
4. Replace the project commands and toolchain placeholders.
5. Record only decisions that are expensive to reverse.
6. Add optional documents when the project has a concrete need for them.

### Brownfield

1. Inventory the existing system before editing it.
2. Record observed behavior in the architecture document.
3. Establish a test and CI baseline.
4. Separate accepted legacy behavior, planned migration, temporary exceptions,
   and defects.
5. Apply the new rules to new work first.
6. Improve legacy areas incrementally rather than rewriting them to satisfy the
   template.

## Customization

Keep the roles of the documents separate. A project may change the file layout
or add domain-specific documents, but it should retain one source of truth for
scope, tasks, decisions, current architecture, and user documentation.
