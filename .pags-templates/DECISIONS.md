# {{PROJECT_NAME}} decisions

<!--
Why things were chosen, and which rules are bent for now.

Entry:   - D-### [status YYYY-MM-DD] the choice, in one line -> links
Detail:  indented `key: value` lines.
  Required: why (context and the main alternative), cost (consequences).
  Optional: replaces, approved-by, exit.

Statuses: proposed, accepted, rejected, replaced, exception until YYYY-MM-DD, resolved

Rules:
- Record a decision before a hard-to-reverse choice: a dependency, public
  interface, architectural pattern, data format or lasting UX choice.
- Agents may add [proposed] entries. Only the maintainer accepts a decision
  or grants an exception.
- Never rewrite an accepted entry. The only allowed edits are its status and
  moving it to the archive. To change direction, add a new entry with
  `replaces: D-###`, set the old entry to [replaced], and move the old entry
  to DECISIONS-ARCHIVE.md (create it if missing).
- Start dependency decisions with "Add dependency:" or "Remove dependency:".
  Versions live in the lockfile, not here.
- An exception bends a rule temporarily. It needs `exit:` and an end date.
  When the exit condition is met, set it to [resolved] and archive it. Only
  the maintainer may extend the date.
- Backfilled decisions in an existing codebase: if the reason is not known,
  write `why: unknown (backfilled YYYY-MM-DD)`. Never guess.

Example:
- D-012 [accepted 2026-09-20] Use SQLite for the offline write queue -> R-003
  why: writes must survive restarts on mobile; IndexedDB has no Node support
  cost: adds a native build step
  replaces: D-004
- D-020 [accepted 2026-09-22] Add dependency: better-sqlite3 -> D-012
  why: synchronous API fits the queue; maintained and MIT licensed
  cost: native module, needs prebuilt binaries for CI
- D-015 [exception until 2026-12-01] Skip end-to-end tests on Windows CI
  why: the runner image cannot start WebView2
  exit: runner image ships WebView2
  approved-by: sam 2026-09-24
-->

## Decisions

## Exceptions
