# {{PROJECT_NAME}} work

<!--
What is approved, and what is being done now.

Entry:   - ID [status] one-line summary -> links
Detail:  optional indented `key: value` lines under the entry.

Outcomes (R-) are approved results. Tasks (T-) deliver them and sit indented
under their outcome, so the link is the indentation.

Outcome statuses: proposed, approved, doing, done, dropped
Task statuses:    todo, doing, blocked, done, dropped
Required detail:  evidence, before a task is marked done
Optional detail:  approved-by, done-when, blocked-by, revisit, tested-commit, evidence-artifact

Rules:
- Agents may add outcomes as [proposed]. Only the maintainer approves them.
  Record an in-session approval as `approved-by: NAME YYYY-MM-DD`.
- Work on a task only when its outcome is [approved] or [doing], or when it
  sits under Unplanned.
- Mark a task done only with `evidence:`. This is an evidence contract with an unambiguous state (PASS, FAIL, NOT RUN, INCONCLUSIVE) followed by a description of the exact command or action.
  - Examples: `evidence: PASS pytest tests/`, `evidence: FAIL UI glitch on Safari`, `evidence: NOT RUN skipped due to missing API key`, `evidence: INCONCLUSIVE manual test flaky`.
  - For high-risk changes, add `tested-commit: COMMIT_HASH` or `evidence-artifact: path/to/logs/or/screenshot.png`.
- Move done and dropped entries to WORK-ARCHIVE.md, newest first. Create that
  file if it does not exist.
- Rewrite the Now block at the end of every session. Do not append to it.

Example:
- R-003 [approved] Offline edits sync when the network returns
  approved-by: sam 2026-09-20
  - T-014 [doing] Queue writes while offline -> D-012
    done-when: queued writes survive an app restart
  - T-015 [todo] Resolve conflicts on reconnect
-->

## Now

- Focus: {{outcome and task in progress, or "not started"}}
- Last session: {{what changed}}
- Next: {{the next concrete step}}
- Waiting on: {{approvals or blockers, or "nothing"}}

## Outcomes

- R-001 [proposed] {{first outcome, stated as a result a user would notice}}

## Unplanned

<!-- Bug fixes, maintenance and security work that need no outcome. -->

## Later

<!-- Ideas that are not approved and not being worked on. Add `revisit:` with a condition. -->
