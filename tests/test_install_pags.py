import contextlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
TEMPLATES = ROOT / ".pags-templates"
HAS_GIT = shutil.which("git") is not None
GIT_ENV = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.com",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


installer = load("install_pags", "install-pags.py")


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env={**os.environ, **GIT_ENV})


def commit_files(repo: Path, count: int, folder: str = ".") -> None:
    directory = repo / folder
    directory.mkdir(parents=True, exist_ok=True)
    for index in range(count):
        (directory / "notes.md").write_text(f"revision {index}\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", f"change {index}")


class InstallerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.target = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def touch(self, *names: str) -> None:
        for name in names:
            path = self.target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("x\n", encoding="utf-8")

    def run_installer(self, *args: str, answers=None) -> tuple[int, str, list[str]]:
        """Run main() as if in a terminal, answering prompts with `answers(prompt)`."""
        prompts: list[str] = []

        def fake_input(prompt: str) -> str:
            prompts.append(prompt)
            return answers(prompt) if answers else ""

        output = io.StringIO()
        argv = ["install-pags", str(self.target), "--no-color", *args]
        with mock.patch.object(sys, "argv", argv), mock.patch("builtins.input", fake_input), mock.patch.object(
            sys.stdin, "isatty", return_value=True
        ), contextlib.redirect_stdout(output):
            code = installer.main()
        return code, output.getvalue(), prompts

    def run_process(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "install-pags.py"), str(self.target), "--no-color", *args],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
        )


class EnterDefaultsTest(InstallerTestCase):
    """#2: pressing Enter at every menu picks the first, recommended option."""

    def test_enter_keeps_existing_files_in_a_brownfield_repo(self) -> None:
        self.touch("README.md", "AGENTS.md", *(f"src/module_{n}.py" for n in range(10)))
        code, output, prompts = self.run_installer(
            answers=lambda prompt: "y" if "Apply this plan" in prompt else ""
        )
        self.assertEqual(code, 0, output)
        self.assertEqual((self.target / "README.md").read_text(), "x\n")
        self.assertEqual((self.target / "AGENTS.md").read_text(), "x\n")
        self.assertIn("Detected: brownfield", output)
        self.assertIn("Inventory the current stack", output)
        self.assertTrue((self.target / ".pags" / "ARCHITECTURE.md").exists())
        self.assertFalse((self.target / ".pags" / "DESIGN.md").exists())
        self.assertFalse(list(self.target.glob(".pags-backup-*")))
        menus = [prompt for prompt in prompts if "(default 1)" in prompt]
        self.assertEqual(len(menus), 3, prompts)

    def test_enter_selects_minimal_profile(self) -> None:
        code, output, _ = self.run_installer(answers=lambda prompt: "y" if "Apply" in prompt else "")
        self.assertEqual(code, 0, output)
        installed = sorted(p.relative_to(self.target).as_posix() for p in self.target.rglob("*") if p.is_file())
        self.assertEqual(
            installed,
            [".pags/CHARTER.md", ".pags/DECISIONS.md", ".pags/WORK.md", ".pags/check.py", "AGENTS.md", "README.md"],
        )

    def test_menu_numbers_still_select_other_options(self) -> None:
        def answers(prompt: str) -> str:
            if "Project type" in prompt:
                return "3"
            if "Choose" in prompt:
                return "2"
            return "y" if "Apply" in prompt else ""

        code, output, _ = self.run_installer(answers=answers)
        self.assertEqual(code, 0, output)
        self.assertIn("Inventory the current stack", output)
        self.assertTrue((self.target / ".pags" / "ARCHITECTURE.md").exists())

    def test_ask_choice_rejects_out_of_range_then_uses_default(self) -> None:
        printer = installer.Printer(False)
        replies = iter(["7", "abc", ""])
        with mock.patch("builtins.input", lambda _: next(replies)), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.ask_choice(printer, "Pick", ("a", "b")), 0)


class RenderedContentTest(InstallerTestCase):
    """#3 and #4: no local path is written, and only the charter gets a date."""

    def setUp(self) -> None:
        super().setUp()
        result = self.run_process("--yes", "--profile", "complete", "--project-name", "Demo")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.installed = [p for p in self.target.rglob("*") if p.is_file()]

    def test_no_local_path_is_written(self) -> None:
        for path in self.installed:
            content = path.read_text(encoding="utf-8")
            self.assertNotIn(str(self.target), content, path)
            self.assertNotIn(self.tmp.name, content, path)
            self.assertNotIn(str(Path.home()), content, path)
            self.assertNotIn("[PATH]", content, path)

    def test_only_the_charter_header_gets_the_install_date(self) -> None:
        today = date.today().isoformat()
        for path in self.installed:
            content = path.read_text(encoding="utf-8")
            if path.name == "CHARTER.md":
                self.assertIn(f"- {today} Charter created", content)
                self.assertEqual(content.count(today), 1)
            else:
                self.assertNotIn(today, content, path)

    def test_date_format_descriptions_are_untouched(self) -> None:
        for path in self.installed:
            if path.suffix != ".md" or path.parent.name != ".pags":
                continue
            source = (TEMPLATES / path.name).read_text(encoding="utf-8")
            self.assertEqual(path.read_text(encoding="utf-8").count("YYYY-MM-DD"), source.count("YYYY-MM-DD"), path)

    def test_no_double_brace_date_or_name_left(self) -> None:
        for path in self.installed:
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("{{DATE}}", content, path)
            self.assertNotIn("{{PROJECT_NAME}}", content, path)


class DetectionTest(InstallerTestCase):
    """#6: history and code decide; build files only break a tie."""

    def detect(self) -> "installer.Detection":
        return installer.detect_mode(self.target)

    def test_empty_folder_is_greenfield(self) -> None:
        self.assertEqual(self.detect().mode, "greenfield")

    def test_fresh_github_repo_is_greenfield(self) -> None:
        self.touch("README.md", "LICENSE", ".gitignore", ".editorconfig", ".github/workflows/ci.yml", "docs/intro.md")
        detection = self.detect()
        self.assertEqual(detection.mode, "greenfield", detection.reason)
        self.assertIn("0 non-doc files", detection.reason)

    def test_meson_project_is_brownfield(self) -> None:
        self.touch("meson.build", "src/main.c", "src/window.c", "data/app.desktop.in")
        detection = self.detect()
        self.assertEqual(detection.mode, "brownfield", detection.reason)
        self.assertIn("meson.build breaks the tie", detection.reason)

    def test_cmake_project_is_brownfield(self) -> None:
        self.touch("CMakeLists.txt", "src/main.cpp")
        self.assertEqual(self.detect().mode, "brownfield")

    def test_csproj_glob_marker(self) -> None:
        self.touch("App.csproj", "Program.cs")
        self.assertIn("App.csproj breaks the tie", self.detect().reason)

    def test_many_code_files_are_brownfield_without_markers(self) -> None:
        self.touch(*(f"scripts/tool_{n}.sh" for n in range(12)))
        detection = self.detect()
        self.assertEqual(detection.mode, "brownfield")
        self.assertIn("10+ non-doc files", detection.reason)

    def test_few_files_without_marker_are_greenfield(self) -> None:
        self.touch("main.py", "README.md")
        self.assertEqual(self.detect().mode, "greenfield")

    def test_skipped_directories_do_not_count(self) -> None:
        self.touch(*(f"node_modules/pkg/file_{n}.js" for n in range(12)), *(f".venv/lib/f{n}.py" for n in range(12)))
        self.assertEqual(self.detect().mode, "greenfield")

    def test_no_git_history_is_reported(self) -> None:
        self.assertIn("no git history", self.detect().reason)

    @unittest.skipUnless(HAS_GIT, "git is not installed")
    def test_long_history_is_brownfield(self) -> None:
        git(self.target, "init", "-q")
        self.touch("main.py")
        commit_files(self.target, 11)
        detection = self.detect()
        self.assertEqual(detection.mode, "brownfield", detection.reason)
        self.assertIn("11 commits", detection.reason)

    @unittest.skipUnless(HAS_GIT, "git is not installed")
    def test_short_history_is_greenfield(self) -> None:
        git(self.target, "init", "-q")
        self.touch("main.py")
        commit_files(self.target, 3)
        detection = self.detect()
        self.assertEqual(detection.mode, "greenfield", detection.reason)
        self.assertIn("3 commits", detection.reason)

    @unittest.skipUnless(HAS_GIT, "git is not installed")
    def test_new_package_in_a_monorepo_counts_only_its_own_history(self) -> None:
        git(self.target, "init", "-q")
        commit_files(self.target, 12, "services/old")
        self.touch("packages/new/index.py")
        commit_files(self.target, 1, "packages/new")
        detection = installer.detect_mode(self.target / "packages" / "new")
        self.assertEqual(detection.mode, "greenfield", detection.reason)
        self.assertIn("1 commit,", detection.reason)


class CliTest(InstallerTestCase):
    """#8: dry run without a terminal, declining, backups and name checks."""

    def test_dry_run_works_without_a_terminal(self) -> None:
        result = self.run_process("--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Dry run complete", result.stdout)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_real_install_without_a_terminal_still_needs_yes(self) -> None:
        result = self.run_process()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Use --yes", result.stdout)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_declining_the_plan_exits_zero(self) -> None:
        code, output, _ = self.run_installer(answers=lambda prompt: "n" if "Apply" in prompt else "")
        self.assertEqual(code, 0, output)
        self.assertIn("Plan declined. No files were changed.", output)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_interrupt_still_exits_130(self) -> None:
        def interrupt(prompt: str) -> str:
            raise KeyboardInterrupt

        code, output, _ = self.run_installer(answers=interrupt)
        self.assertEqual(code, 130, output)

    def test_blank_project_name_is_rejected(self) -> None:
        result = self.run_process("--yes", "--project-name", "  \n ")
        self.assertEqual(result.returncode, 1)
        self.assertIn("must not be empty", result.stdout)

    def test_backup_folder_ignores_itself(self) -> None:
        self.touch("README.md")
        result = self.run_process("--yes", "--conflict", "backup")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        backups = list(self.target.glob(".pags-backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / ".gitignore").read_text(), "*\n")
        self.assertEqual((backups[0] / "README.md").read_text(), "x\n")
        self.assertIn("ignored by git", result.stdout)

    @unittest.skipUnless(HAS_GIT, "git is not installed")
    def test_backup_folder_is_not_seen_by_git(self) -> None:
        git(self.target, "init", "-q")
        self.touch("README.md")
        self.run_process("--yes", "--conflict", "backup")
        status = subprocess.run(
            ["git", "-C", str(self.target), "status", "--porcelain", "--untracked-files=all"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        self.assertNotIn(".pags-backup", status)
        self.assertIn("AGENTS.md", status)


if __name__ == "__main__":
    unittest.main()
