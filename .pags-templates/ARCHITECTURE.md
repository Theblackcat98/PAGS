# {{PROJECT_NAME}} architecture

<!--
What exists today, not what is planned. Planned change goes in WORK.md, and
reasons go in DECISIONS.md.

Mark anything you have not confirmed:
  (observed) seen in code or behavior, intent not confirmed
  (unknown)  nobody knows why; never guess at historical intent

Update this file in the same change that alters structure, interfaces or
invariants.

Known debt entry:  - A-### [status] observation -> links
  accepted: legacy we live with
  planned:  a migration exists, link its outcome (R-)
Temporary rule deviations are exceptions in DECISIONS.md, and plain defects
are tasks in WORK.md.

Example:
- A-001 [accepted] Config is parsed twice at startup (observed)
- A-002 [planned] Legacy REST client still used by sync -> R-005
-->

Last checked: not yet

## Overview

{{What the system is, what it talks to, and where it runs. One short paragraph.}}

## Map

- `{{path/}}` {{what lives here}}

## Flows

- {{main flow}}: {{entry point}} -> {{processing}} -> {{output}}

## Interfaces

- {{interface}}: {{who uses it, its contract, its compatibility promise}}

## Invariants

- {{a condition that must stay true}}

## Known debt
