#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
PAGS_ROOT = SCRIPT_DIR.parent
TEMPLATE_DIR = PAGS_ROOT / ".pags-templates"


@dataclass(frozen=True)
class Template:
    source: str
    destination: str
    summary: str
    source_dir: Path = TEMPLATE_DIR
    managed: bool = False
    mode: int = 0o644


CORE_TEMPLATES = (
    Template("AGENTS.md", "AGENTS.md", "Instructions for contributors and agents"),
    Template("README.md", "README.md", "User-facing project documentation"),
    Template("CHARTER.md", ".pags/CHARTER.md", "Identity, boundaries, and principles"),
    Template("WORK.md", ".pags/WORK.md", "Now block, approved outcomes, and tasks"),
    Template("DECISIONS.md", ".pags/DECISIONS.md", "Decisions, exceptions, and dependency reasons"),
    Template("ARCHITECTURE.md", ".pags/ARCHITECTURE.md", "Current system structure and behavior"),
)

OPTIONAL_TEMPLATES = (
    Template("DESIGN.md", ".pags/DESIGN.md", "Durable user experience and design language"),
)

# Tool files PAGS owns. Every profile installs them, and a rerun updates a
# changed copy after backing it up instead of keeping it.
MANAGED_FILES = (
    Template(
        "pags-check.py",
        ".pags/check.py",
        "Record checker: python3 .pags/check.py",
        source_dir=SCRIPT_DIR,
        managed=True,
        mode=0o755,
    ),
)

MINIMAL_TEMPLATE_NAMES = {
    "AGENTS.md",
    "README.md",
    "CHARTER.md",
    "WORK.md",
    "DECISIONS.md",
}

PROJECT_FILE_MARKERS = {
    ".editorconfig",
    ".gitignore",
    "BUILD.bazel",
    "Cargo.toml",
    "Gemfile",
    "Makefile",
    "Taskfile.yml",
    "build.gradle",
    "build.gradle.kts",
    "composer.json",
    "go.mod",
    "mix.exs",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "setup.cfg",
}

PROJECT_DIRECTORY_MARKERS = {
    ".github",
    "app",
    "apps",
    "lib",
    "src",
    "test",
    "tests",
}

class InstallerError(Exception):
    pass


class UserCancelled(Exception):
    pass


@dataclass
class Action:
    template: Template
    destination: Path
    status: str
    content: str = ""


class Printer:
    def __init__(self, color: bool) -> None:
        self.color = color

    def paint(self, text: str, *styles: str) -> str:
        if not self.color or not styles:
            return text
        codes = {
            "bold": "1",
            "dim": "2",
            "red": "31",
            "green": "32",
            "yellow": "33",
            "blue": "34",
            "magenta": "35",
            "cyan": "36",
        }
        prefix = "".join(f"\033[{codes[style]}m" for style in styles if style in codes)
        return f"{prefix}{text}\033[0m" if prefix else text

    def print(self, text: str = "") -> None:
        print(text)

    def banner(self, dry_run: bool) -> None:
        mode = "PLAN MODE" if dry_run else "GUIDED INSTALLER"
        self.print()
        self.print(self.paint("  P A G S", "bold", "cyan"))
        self.print(self.paint("  Project constitution, without the ceremony.", "dim"))
        self.print(self.paint(f"  {mode}  /  ------------------------------------------------", "dim"))

    def heading(self, text: str) -> None:
        self.print()
        self.print(self.paint(f"{text}", "bold"))

    def success(self, text: str) -> None:
        self.print(self.paint(f"OK  {text}", "green"))

    def warning(self, text: str) -> None:
        self.print(self.paint(f"!   {text}", "yellow"))

    def error(self, text: str) -> None:
        self.print(self.paint(f"ERR {text}", "red"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="install-pags",
        description="Install the PAGS project constitution and delivery system.",
    )
    parser.add_argument("target", nargs="?", default=".", help="Target repository (default: current directory)")
    parser.add_argument(
        "--mode",
        choices=("auto", "greenfield", "brownfield"),
        default="auto",
        help="Project type (default: auto-detect)",
    )
    parser.add_argument(
        "--profile",
        choices=("minimal", "core", "complete"),
        help="Template profile (default: minimal)",
    )
    parser.add_argument("--minimal", action="store_true", help="Use the minimal profile")
    parser.add_argument("--project-name", help="Project name used in generated headings")
    parser.add_argument(
        "--conflict",
        choices=("skip", "backup"),
        default="skip",
        help="Keep existing files or back them up before replacement (default: skip)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show the plan without changing files")
    parser.add_argument("--yes", action="store_true", help="Accept defaults without prompting")
    parser.add_argument("--no-color", action="store_true", help="Disable terminal colors")
    return parser


def has_project_markers(target: Path) -> bool:
    return any((target / marker).exists() for marker in PROJECT_FILE_MARKERS) or any(
        (target / marker).is_dir() for marker in PROJECT_DIRECTORY_MARKERS
    )


def detect_mode(target: Path) -> str:
    return "brownfield" if has_project_markers(target) else "greenfield"


def should_use_color(args: argparse.Namespace) -> bool:
    if args.no_color or os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return False
    return sys.stdout.isatty()


def ask_choice(printer: Printer, prompt: str, choices: Sequence[str], default: int) -> int:
    while True:
        try:
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt) as error:
            raise UserCancelled from error
        if not raw:
            return default
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            return int(raw) - 1
        printer.warning(f"Enter a number from 1 to {len(choices)}.")


def ask_confirmation(printer: Printer, prompt: str, default: bool) -> bool:
    suffix = "Y/n" if default else "y/N"
    while True:
        try:
            raw = input(f"{prompt} [{suffix}]: ").strip().lower()
        except (EOFError, KeyboardInterrupt) as error:
            raise UserCancelled from error
        if not raw:
            return default
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        printer.warning("Enter y or n.")


def choose_mode(args: argparse.Namespace, target: Path, printer: Printer) -> str:
    detected = detect_mode(target)
    if args.mode != "auto" or args.yes:
        return detected if args.mode == "auto" else args.mode
    printer.print()
    printer.print(
        f"  Detected: {printer.paint(detected, 'cyan')}  "
        f"({target.name})"
    )
    choice = ask_choice(
        printer,
        "  Project type: [1] Use detection  [2] Greenfield  [3] Brownfield: ",
        ("Use detection", "Greenfield", "Brownfield"),
        1,
    )
    if choice == 1:
        return "greenfield"
    if choice == 2:
        return "brownfield"
    return detected


def choose_profile(args: argparse.Namespace, mode: str, printer: Printer) -> str:
    if args.profile:
        return args.profile
    if args.minimal:
        return "minimal"
    if args.yes:
        return "minimal"
    printer.print()
    printer.print(f"  Adoption profile  ({printer.paint('minimal is recommended', 'dim')})")
    printer.print(f"    1  Minimal       Constitution, work, and decisions{' + current architecture' if mode == 'brownfield' else ''}")
    printer.print("    2  Core          All core PAGS documents")
    printer.print("    3  Complete      Core documents plus every optional template")
    choice = ask_choice(
        printer,
        "  Choose: ",
        ("Minimal", "Core", "Complete"),
        1,
    )
    return ("minimal", "core", "complete")[choice]


def choose_project_name(args: argparse.Namespace, target: Path, printer: Printer) -> str:
    detected = target.name.replace("-", " ").replace("_", " ").strip() or "Project"
    if args.project_name or args.yes:
        project_name = args.project_name or detected
    else:
        printer.print()
        try:
            project_name = input(f"  Project name [{detected}]: ").strip() or detected
        except (EOFError, KeyboardInterrupt) as error:
            raise UserCancelled from error
    project_name = " ".join(project_name.split())
    if not project_name or "\n" in project_name or "\r" in project_name:
        raise InstallerError("The project name must not be empty.")
    return project_name


def optional_defaults(template: Template, target: Path, mode: str) -> bool:
    return False


def choose_templates(
    args: argparse.Namespace,
    mode: str,
    target: Path,
    printer: Printer,
) -> list[Template]:
    profile = choose_profile(args, mode, printer)
    if profile == "minimal":
        names = MINIMAL_TEMPLATE_NAMES | ({"ARCHITECTURE.md"} if mode == "brownfield" else set())
        selected = [template for template in CORE_TEMPLATES if template.source in names]
    elif profile == "core":
        selected = list(CORE_TEMPLATES)
    else:
        selected = list(CORE_TEMPLATES + OPTIONAL_TEMPLATES)

    if profile == "complete" or args.yes:
        return selected + list(MANAGED_FILES)

    recommended = [template for template in OPTIONAL_TEMPLATES if optional_defaults(template, target, mode)]
    if recommended:
        printer.print()
        printer.print(printer.paint("  Recommended additions", "bold"))
    else:
        printer.print()
        printer.print(printer.paint("  Optional additions", "bold"))

    selected_sources = {template.source for template in selected}
    for template in OPTIONAL_TEMPLATES:
        if template.source in selected_sources:
            continue
        default = optional_defaults(template, target, mode)
        label = "recommend" if default else "optional"
        include = ask_confirmation(
            printer,
            f"  Add {template.source:<16} {template.summary} ({label})",
            default,
        )
        if include:
            selected.append(template)
    return selected + list(MANAGED_FILES)


def choose_conflict_policy(
    args: argparse.Namespace,
    actions: list[Action],
    printer: Printer,
) -> str:
    if args.conflict != "skip" or args.yes or not actions:
        return args.conflict
    existing = [action for action in actions if action.destination.exists() and not action.template.managed]
    if not existing:
        return "skip"
    printer.print()
    printer.print(printer.paint("  Existing files", "yellow"))
    for action in existing:
        printer.print(f"    {action.template.destination}")
    choice = ask_choice(
        printer,
        "  Conflict policy: [1] Keep existing (recommended)  [2] Back up and replace: ",
        ("Keep existing", "Back up and replace"),
        1,
    )
    return ("skip", "backup")[choice]


def render_template(source: Path, target: Path, project_name: str, today: str) -> str:
    content = source.read_text(encoding="utf-8")
    content = content.replace("{{PROJECT_NAME}}", project_name)
    content = content.replace("{{DATE}}", today)
    return content


def make_actions(
    templates: Sequence[Template],
    target: Path,
    project_name: str,
    today: str,
    conflict_policy: str,
) -> list[Action]:
    actions: list[Action] = []
    for template in templates:
        source = template.source_dir / template.source
        if not source.is_file():
            raise InstallerError(f"Missing template: {source}")
        destination = target / template.destination
        if template.managed:
            content = source.read_text(encoding="utf-8")
            if not destination.exists():
                status = "create"
            elif destination.read_text(encoding="utf-8") == content:
                status = "keep"
            else:
                status = "update"
            actions.append(Action(template, destination, status, content))
            continue
        if destination.exists():
            status = "replace" if conflict_policy == "backup" else "keep"
        else:
            status = "create"
        content = "" if status == "keep" else render_template(source, target, project_name, today)
        actions.append(Action(template, destination, status, content))
    return actions


def relative_destination(action: Action) -> str:
    return action.template.destination


def print_plan(printer: Printer, actions: Sequence[Action], target: Path) -> None:
    printer.heading("Installation plan")
    width = max((len(relative_destination(action)) for action in actions), default=0)
    for action in actions:
        if action.status == "create":
            marker = printer.paint("+", "green")
            detail = "create"
        elif action.status == "replace":
            marker = printer.paint("~", "yellow")
            detail = "back up and replace"
        elif action.status == "update":
            marker = printer.paint("~", "yellow")
            detail = "back up and update to this PAGS version"
        else:
            marker = printer.paint("-", "dim")
            detail = "keep existing"
        printer.print(f"  {marker} {relative_destination(action):<{width}}  {printer.paint(detail, 'dim')}")
    create_count = sum(action.status == "create" for action in actions)
    replace_count = sum(action.status in {"replace", "update"} for action in actions)
    keep_count = sum(action.status == "keep" for action in actions)
    printer.print()
    printer.print(
        f"  Target: {printer.paint(str(target), 'cyan')}  |  "
        f"{create_count} create  {replace_count} replace  {keep_count} keep"
    )


def backup_path(target: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = target / f".pags-backup-{timestamp}"
    counter = 2
    while candidate.exists():
        candidate = target / f".pags-backup-{timestamp}-{counter}"
        counter += 1
    return candidate


def atomic_write(destination: Path, content: str, default_mode: int = 0o644) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    mode = destination.stat().st_mode & 0o777 if destination.exists() else default_mode
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.chmod(temporary, mode)
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def install(actions: Sequence[Action], target: Path) -> tuple[Path | None, list[Path]]:
    replace_actions = [action for action in actions if action.status in {"replace", "update"}]
    write_actions = [action for action in actions if action.status in {"create", "replace", "update"}]
    backup = backup_path(target) if replace_actions else None
    if backup:
        for action in replace_actions:
            backup_destination = backup / action.template.destination
            backup_destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(action.destination, backup_destination)
    written: list[Path] = []
    try:
        for action in write_actions:
            atomic_write(action.destination, action.content, action.template.mode)
            written.append(action.destination)
    except OSError as error:
        raise InstallerError(f"Installation stopped after {len(written)} file(s): {error}") from error
    return backup, written


def next_steps(printer: Printer, mode: str) -> None:
    printer.heading("Next")
    if mode == "brownfield":
        steps = (
            "Inventory the current stack, commands, dependencies, and behavior.",
            "Describe what exists in ARCHITECTURE; mark unconfirmed facts (observed) or (unknown).",
            "Sort existing problems into known debt, outcomes, exceptions, or tasks.",
            "Run python3 .pags/check.py before each commit and in CI.",
        )
    else:
        steps = (
            "Write the charter before selecting implementation details.",
            "Add three to seven outcomes to .pags/WORK.md and get them approved.",
            "Fill every remaining {{placeholder}}; python3 .pags/check.py lists them.",
            "Run python3 .pags/check.py before each commit and in CI.",
        )
    for index, step in enumerate(steps, start=1):
        printer.print(f"  {index}. {step}")
    printer.print()
    printer.print(printer.paint("  PAGS is installed. Keep the constitution current, not ceremonial.", "green"))
    printer.print()


def run(args: argparse.Namespace) -> int:
    printer = Printer(should_use_color(args))
    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        raise InstallerError(f"Target is not a directory: {target}")
    if not TEMPLATE_DIR.is_dir():
        raise InstallerError(f"Template directory not found: {TEMPLATE_DIR}")
    if not args.yes and not sys.stdin.isatty():
        raise InstallerError("Interactive input is unavailable. Use --yes for non-interactive use.")

    printer.banner(args.dry_run)
    mode = choose_mode(args, target, printer)
    project_name = choose_project_name(args, target, printer)
    templates = choose_templates(args, mode, target, printer)
    today = datetime.now().date().isoformat()
    initial_actions = make_actions(templates, target, project_name, today, "skip")
    conflict_policy = choose_conflict_policy(args, initial_actions, printer)
    actions = make_actions(templates, target, project_name, today, conflict_policy)
    print_plan(printer, actions, target)

    if not any(action.status in {"create", "replace", "update"} for action in actions):
        printer.print()
        printer.success("Selected PAGS documents are already present. Nothing to do.")
        return 0

    if not args.dry_run and not args.yes:
        printer.print()
        if not ask_confirmation(printer, "  Apply this plan?", False):
            raise UserCancelled

    printer.print()
    if args.dry_run:
        printer.success("Dry run complete. No files were changed.")
        return 0

    backup, written = install(actions, target)
    if backup:
        printer.warning(f"Backup created: {backup}")
    for destination in written:
        printer.success(f"{destination.relative_to(target)}")
    printer.print()
    printer.success(f"Installed {len(written)} document(s) in {target}")
    next_steps(printer, mode)
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.minimal and args.profile and args.profile != "minimal":
        parser.error("--minimal cannot be combined with a different --profile")
    printer = Printer(should_use_color(args))
    try:
        return run(args)
    except UserCancelled:
        printer.print()
        printer.warning("Installation cancelled. No files were changed.")
        return 130
    except (InstallerError, OSError) as error:
        printer.error(str(error))
        return 1
    except KeyboardInterrupt:
        printer.print()
        printer.warning("Installation cancelled.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
