import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


pags_check = load("pags_check", "pags-check.py")

WORK = """\
# Demo work

## Now

- Focus: R-001
- Last session: nothing
- Next: start T-001
- Waiting on: nothing

## Outcomes

- R-001 [approved] Users can export reports
  approved-by: sam 2026-09-20
  - T-001 [doing] Add CSV export -> D-001
    done-when: a report downloads as CSV
  - T-002 [todo] Add PDF export

## Unplanned

- T-003 [todo] Fix crash on empty report

## Later
"""

DECISIONS = """\
# Demo decisions

## Decisions

- D-001 [accepted 2026-09-20] Stream CSV rows instead of buffering -> R-001
  why: reports can exceed memory
  cost: no total row count up front

## Exceptions

- D-002 [exception until 2026-12-01] Skip PDF tests on Windows CI
  why: the runner cannot install fonts
  exit: runner image ships fonts
"""

ARCHITECTURE = """\
# Demo architecture

## Known debt

- A-001 [accepted] Config is parsed twice at startup (observed)
- A-002 [planned] Legacy exporter still used by the CLI -> R-001
"""

CHARTER = """\
# Demo charter

Status: {status} <!-- draft | accepted -->
Maintainer: sam
"""


class RecordsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.records = self.root / ".pags"
        self.records.mkdir()
        self.write("WORK.md", WORK)
        self.write("DECISIONS.md", DECISIONS)
        self.write("ARCHITECTURE.md", ARCHITECTURE)
        self.write("CHARTER.md", CHARTER.format(status="accepted"))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, name: str, content: str) -> None:
        (self.records / name).write_text(textwrap.dedent(content), encoding="utf-8")

    def edit(self, name: str, old: str, new: str) -> None:
        path = self.records / name
        content = path.read_text(encoding="utf-8")
        self.assertIn(old, content)
        path.write_text(content.replace(old, new, 1), encoding="utf-8")

    def check(self, *extra: str) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = pags_check.main([str(self.root), "--today", "2026-09-27", *extra])
        return code, output.getvalue()

    def assertProblem(self, level: str, text: str) -> None:
        code, output = self.check()
        self.assertIn(f"{level}: {text}", output)
        if level == "error":
            self.assertEqual(code, 1, output)


class ValidRecordsTest(RecordsTestCase):
    def test_clean_records_pass(self) -> None:
        code, output = self.check()
        self.assertEqual(code, 0, output)
        self.assertIn("ok   8 entries, 0 error(s), 0 warning(s)", output)

    def test_examples_in_comments_and_code_are_ignored(self) -> None:
        extra = "<!--\n- T-001 [bogus] example\n-->\n```text\n- R-001 [nope] sample\n```\n"
        self.edit("WORK.md", "## Later\n", "## Later\n\n" + extra)
        code, output = self.check()
        self.assertEqual(code, 0, output)

    def test_archive_entries_count_for_links_and_uniqueness(self) -> None:
        self.write("WORK-ARCHIVE.md", "# Archive\n\n- T-009 [done] Old task\n  evidence: make test passed\n")
        self.edit("DECISIONS.md", "-> R-001\n", "-> R-001, T-009\n")
        code, output = self.check()
        self.assertEqual(code, 0, output)

    def test_missing_records_folder(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            code = pags_check.main([str(self.root), "--records-dir", "docs/pags"])
        self.assertEqual(code, 2)
        self.assertIn("no records folder", output.getvalue())


class ErrorTest(RecordsTestCase):
    def test_duplicate_id(self) -> None:
        self.edit("WORK.md", "T-003 [todo]", "T-001 [todo]")
        self.assertProblem("error", "T-001 is already used at .pags/WORK.md:14")

    def test_duplicate_id_with_different_padding(self) -> None:
        self.edit("WORK.md", "T-003 [todo]", "T-0001 [todo]")
        self.assertProblem("error", "T-0001 is already used")

    def test_duplicate_id_across_archive(self) -> None:
        self.write("DECISIONS-ARCHIVE.md", "# Archive\n\n- D-001 [replaced 2026-01-01] Old choice\n")
        self.assertProblem("error", "D-001 is already used")

    def test_dangling_link(self) -> None:
        self.edit("WORK.md", "-> D-001", "-> D-009")
        self.assertProblem("error", "T-001 links to D-009, which does not exist")

    def test_dangling_blocked_by(self) -> None:
        self.edit("WORK.md", "T-002 [todo] Add PDF export", "T-002 [blocked] Add PDF export\n    blocked-by: T-042")
        self.assertProblem("error", "T-002 links to T-042, which does not exist")

    def test_bad_task_status(self) -> None:
        self.edit("WORK.md", "T-002 [todo]", "T-002 [ready]")
        self.assertProblem("error", "T-002 has status [ready]; use todo, doing, blocked, done, dropped")

    def test_bad_decision_status(self) -> None:
        self.edit("DECISIONS.md", "[accepted 2026-09-20]", "[approved]")
        self.assertProblem("error", "D-001 has status [approved]")

    def test_bad_decision_date(self) -> None:
        self.edit("DECISIONS.md", "[accepted 2026-09-20]", "[accepted 2026-13-01]")
        self.assertProblem("error", "D-001 has an invalid date 2026-13-01")

    def test_malformed_headline(self) -> None:
        self.edit("WORK.md", "T-002 [todo] Add PDF export", "T-002 todo Add PDF export")
        self.assertProblem("error", "entry headline must look like")

    def test_entry_in_wrong_file(self) -> None:
        self.edit("ARCHITECTURE.md", "## Known debt\n", "## Known debt\n\n- T-010 [todo] Stray task\n")
        self.assertProblem("error", "T-010 belongs in WORK.md")

    def test_orphan_task(self) -> None:
        self.edit("WORK.md", "## Later\n", "## Later\n\n- T-004 [todo] Floating task\n")
        self.assertProblem("error", "T-004 must sit indented under an outcome (R-) or under Unplanned")

    def test_task_under_unapproved_outcome(self) -> None:
        self.edit("WORK.md", "R-001 [approved]", "R-001 [proposed]")
        self.assertProblem("error", "T-001 is [doing] under R-001, which is [proposed], not approved")

    def test_done_without_evidence(self) -> None:
        self.edit("WORK.md", "T-002 [todo]", "T-002 [done]")
        self.assertProblem("error", "T-002 is [done] without `evidence:`")

    def test_expired_exception(self) -> None:
        self.edit("DECISIONS.md", "until 2026-12-01", "until 2026-09-01")
        self.assertProblem("error", "D-002 exception ended 2026-09-01")

    def test_exception_without_exit(self) -> None:
        self.edit("DECISIONS.md", "  exit: runner image ships fonts\n", "")
        self.assertProblem("error", "D-002 is an exception without `exit:`")

    def test_replaces_requires_replaced_status(self) -> None:
        new = "- D-003 [accepted 2026-09-26] Buffer small reports\n  replaces: D-001\n\n## Exceptions"
        self.edit("DECISIONS.md", "## Exceptions", new)
        self.assertProblem("error", "D-003 replaces D-001, so D-001 must be [replaced]")

    def test_replaced_requires_a_replacement(self) -> None:
        self.edit("DECISIONS.md", "[accepted 2026-09-20]", "[replaced 2026-09-26]")
        self.assertProblem("error", "D-001 is [replaced], but no decision says `replaces: D-001`")

    def test_replacement_pair_is_valid(self) -> None:
        self.edit("DECISIONS.md", "[accepted 2026-09-20]", "[replaced 2026-09-26]")
        new = "- D-003 [accepted 2026-09-26] Buffer small reports\n  replaces: D-001\n\n## Exceptions"
        self.edit("DECISIONS.md", "## Exceptions", new)
        code, output = self.check()
        self.assertEqual(code, 0, output)
        self.assertIn("warning: D-001 is [replaced]; move it to DECISIONS-ARCHIVE.md", output)


class WarningTest(RecordsTestCase):
    def test_finished_entry_left_in_live_file(self) -> None:
        self.edit("WORK.md", "T-002 [todo] Add PDF export", "T-002 [done] Add PDF export\n    evidence: ok")
        code, output = self.check()
        self.assertEqual(code, 0, output)
        self.assertIn("warning: T-002 is [done]; move it to WORK-ARCHIVE.md", output)
        self.assertEqual(self.check("--strict")[0], 1)

    def test_active_entry_in_archive(self) -> None:
        self.write("WORK-ARCHIVE.md", "# Archive\n\n- T-009 [doing] Not finished\n")
        self.assertProblem("warning", "T-009 is [doing] but sits in the archive")

    def test_planned_debt_without_outcome(self) -> None:
        self.edit("ARCHITECTURE.md", " -> R-001", "")
        self.assertProblem("warning", "A-002 is [planned] but does not link to its outcome (R-)")


class PlaceholderTest(RecordsTestCase):
    def test_placeholders_warn_while_charter_is_draft(self) -> None:
        self.write("CHARTER.md", CHARTER.format(status="draft") + "\n- {{a goal}}\n- {{another}} {{third}}\n")
        code, output = self.check()
        self.assertEqual(code, 0, output)
        self.assertIn(".pags/CHARTER.md:6: warning: 3 unfilled {{placeholder(s)}}", output)

    def test_placeholders_fail_once_charter_is_accepted(self) -> None:
        (self.root / "AGENTS.md").write_text("# Agents\n\n- Test: `{{command}}`\n", encoding="utf-8")
        self.assertProblem("error", "1 unfilled {{placeholder(s)}}; list them with grep -n '{{' AGENTS.md")

    def test_placeholders_in_comments_are_ignored(self) -> None:
        (self.root / "README.md").write_text("# Demo\n\n<!-- {{not a field}} -->\n", encoding="utf-8")
        code, output = self.check()
        self.assertEqual(code, 0, output)

    def test_file_can_opt_out(self) -> None:
        readme = "# Demo\n\n<!-- pags: no-placeholder-check -->\n\n```jinja\n{{ user.name }}\n```\n"
        (self.root / "README.md").write_text(readme, encoding="utf-8")
        code, output = self.check()
        self.assertEqual(code, 0, output)


class InstalledTemplatesTest(unittest.TestCase):
    def install(self, target: Path, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "install-pags.py"), str(target), "--yes", "--no-color", *extra],
            capture_output=True,
            text=True,
            check=True,
        )

    def test_fresh_install_passes_with_placeholder_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.install(target, "--profile", "complete", "--project-name", "Demo")
            checker = target / ".pags" / "check.py"
            self.assertTrue(checker.is_file())
            self.assertEqual(checker.read_text(), (SCRIPTS / "pags-check.py").read_text())
            result = subprocess.run(
                [sys.executable, str(checker)], cwd=target, capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("0 error(s)", result.stdout)
            self.assertIn("unfilled {{placeholder(s)}}", result.stdout)

            charter = target / ".pags" / "CHARTER.md"
            charter.write_text(charter.read_text().replace("Status: draft", "Status: accepted"))
            result = subprocess.run(
                [sys.executable, str(checker)], cwd=target, capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 1, result.stdout)

    def test_rerun_updates_a_changed_checker_with_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.install(target)
            checker = target / ".pags" / "check.py"
            result = self.install(target)
            self.assertIn("Nothing to do", result.stdout)

            checker.write_text("# old version\n")
            result = self.install(target)
            self.assertIn("update", result.stdout)
            self.assertEqual(checker.read_text(), (SCRIPTS / "pags-check.py").read_text())
            backups = list(target.glob(".pags-backup-*/.pags/check.py"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "# old version\n")


if __name__ == "__main__":
    unittest.main()
