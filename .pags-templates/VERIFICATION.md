# {{PROJECT_NAME}} verification

<!--
Optional. Use it when the project needs repeatable instructions for verifying real
application behavior (e.g. web, Android, desktop, TUI) beyond automated tests.
-->

## Prerequisites

- {{Environment variables (exclude secrets), system dependencies, or connected devices required}}

## Launch

- {{How to build and start the correct instance for testing}}
- {{Readiness checks (e.g. waiting for a log line or an HTTP 200)}}
- {{How to avoid testing a stale instance (e.g. clearing cache or rebuilding)}}

## Workflows

### {{Workflow name}}

- Expected outcome: {{what the user should see or experience}}
- Side effects: {{changes to databases, disk, or remote state}}
- Error paths: {{how it should fail gracefully}}

## Evidence

- {{How to capture useful logs, screenshots, HTTP responses, or state changes}}

## Teardown

- {{How to stop the application safely}}
- {{How to retain evidence and clean up test data}}

## Limitations

- {{Checks that remain manual or cannot be verified locally}}
