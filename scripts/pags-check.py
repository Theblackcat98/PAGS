#!/usr/bin/env python3
"""Check that a project's PAGS records agree with each other.

Stdlib only; Python 3.10 or later. Exits 0 when there are no errors, 1 when
there are errors (or warnings with --strict), and 2 when the records cannot be
found. Run it from the repository root, in a pre-commit hook or in CI.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

VERSION = "1"

ENTRY_START = re.compile(r"^([ \t]*)- ([RTDA])-(\d+)\b")
ENTRY = re.compile(r"^([ \t]*)- ([RTDA])-(\d+) \[([^\]]*)\](.*)$")
DETAIL = re.compile(r"^[ \t]+([a-z][a-z-]*):[ \t]*(.*)$")
HEADING = re.compile(r"^#{1,6}[ \t]+(.*?)[ \t]*#*$")
FENCE = re.compile(r"^[ \t]*(```|~~~)")
ID_REF = re.compile(r"\b([RTDA])-(\d+)\b")
DATE = r"\d{4}-\d{2}-\d{2}"
DECISION_STATUS = re.compile(
    rf"^(?:(proposed|accepted|rejected|replaced|resolved)(?: ({DATE}))?|exception until ({DATE}))$"
)
PLACEHOLDER = re.compile(r"\{\{[^{}\n]*\}\}")
CHARTER_STATUS = re.compile(r"^Status:[ \t]*([A-Za-z]+)", re.MULTILINE)
PLACEHOLDER_OPT_OUT = "pags: no-placeholder-check"

STATUSES = {
    "R": ("proposed", "approved", "doing", "done", "dropped"),
    "T": ("todo", "doing", "blocked", "done", "dropped"),
    "A": ("accepted", "planned"),
}
HOME = {"R": "WORK", "T": "WORK", "D": "DECISIONS", "A": "ARCHITECTURE"}
REFERENCE_KEYS = ("replaces", "blocked-by")
FINISHED = {
    "R": {"done", "dropped"},
    "T": {"done", "dropped"},
    "D": {"replaced", "resolved"},
}
TASK_ACTIVE = {"doing", "blocked", "done"}
OUTCOME_OPEN = {"approved", "doing", "done"}


@dataclass
class Entry:
    prefix: str
    number: int
    raw_id: str
    status: str
    summary: str
    links: list[str]
    path: Path
    line: int
    indent: int
    section: str
    parent: Entry | None = None
    details: dict[str, tuple[str, int]] = field(default_factory=dict)

    @property
    def key(self) -> tuple[str, int]:
        return (self.prefix, self.number)

    @property
    def state(self) -> str:
        return self.status.split(" ", 1)[0]


@dataclass
class Problem:
    level: str
    path: Path
    line: int
    message: str


class Checker:
    def __init__(self, root: Path, records_dir: str, today: date) -> None:
        self.root = root
        self.records = root / records_dir
        self.today = today
        self.entries: list[Entry] = []
        self.problems: list[Problem] = []

    def error(self, path: Path, line: int, message: str) -> None:
        self.problems.append(Problem("error", path, line, message))

    def warn(self, path: Path, line: int, message: str) -> None:
        self.problems.append(Problem("warning", path, line, message))

    def display(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    def record_files(self) -> list[Path]:
        return sorted(path for path in self.records.glob("*.md") if path.is_file())

    def run(self) -> None:
        files = self.record_files()
        for path in files:
            self.parse(path)
        self.check_entries()
        self.check_placeholders(files)
        self.problems.sort(key=lambda problem: (self.display(problem.path), problem.line))

    def parse(self, path: Path) -> None:
        lines = visible_lines(path.read_text(encoding="utf-8"))
        section = ""
        stack: list[Entry] = []
        current: Entry | None = None
        in_fence = False
        for number, text in enumerate(lines, start=1):
            if FENCE.match(text):
                in_fence = not in_fence
                current = None
                continue
            if in_fence or not text.strip():
                continue
            heading = HEADING.match(text)
            if heading:
                section = heading.group(1).strip()
                stack = []
                current = None
                continue
            if ENTRY_START.match(text):
                current = self.parse_entry(path, number, text, section, stack)
                continue
            detail = DETAIL.match(text)
            if current and detail and indent_width(text) > current.indent:
                current.details.setdefault(detail.group(1), (detail.group(2).strip(), number))
                continue
            if indent_width(text) == 0:
                current = None

    def parse_entry(self, path: Path, number: int, text: str, section: str, stack: list[Entry]) -> Entry | None:
        match = ENTRY.match(text)
        if not match:
            self.error(path, number, "entry headline must look like `- ID [status] summary -> links`")
            return None
        indent_text, prefix, digits, status, rest = match.groups()
        summary, _, link_text = rest.partition(" -> ")
        entry = Entry(
            prefix=prefix,
            number=int(digits),
            raw_id=f"{prefix}-{digits}",
            status=" ".join(status.split()),
            summary=summary.strip(),
            links=[f"{p}-{n}" for p, n in ID_REF.findall(link_text)],
            path=path,
            line=number,
            indent=indent_width(indent_text),
            section=section,
        )
        while stack and stack[-1].indent >= entry.indent:
            stack.pop()
        entry.parent = stack[-1] if stack else None
        stack.append(entry)
        self.entries.append(entry)
        return entry

    def check_entries(self) -> None:
        by_key: dict[tuple[str, int], Entry] = {}
        for entry in self.entries:
            first = by_key.get(entry.key)
            if first:
                self.error(
                    entry.path,
                    entry.line,
                    f"{entry.raw_id} is already used at {self.display(first.path)}:{first.line}",
                )
            else:
                by_key[entry.key] = entry

        replaced_by: dict[tuple[str, int], Entry] = {}
        for entry in self.entries:
            self.check_file(entry)
            self.check_status(entry)
            for ref in self.references(entry):
                target = by_key.get(parse_id(ref))
                if target is None:
                    self.error(entry.path, entry.line, f"{entry.raw_id} links to {ref}, which does not exist")
            replaces = entry.details.get("replaces")
            if replaces:
                for ref in ID_REF.findall(replaces[0]):
                    target = by_key.get((ref[0], int(ref[1])))
                    if target is None:
                        continue
                    replaced_by[target.key] = entry
                    if target.state != "replaced":
                        self.error(
                            entry.path,
                            replaces[1],
                            f"{entry.raw_id} replaces {target.raw_id}, so {target.raw_id} must be [replaced]",
                        )
        for entry in self.entries:
            if entry.prefix == "D" and entry.state == "replaced" and entry.key not in replaced_by:
                self.error(
                    entry.path,
                    entry.line,
                    f"{entry.raw_id} is [replaced], but no decision says `replaces: {entry.raw_id}`",
                )

    def references(self, entry: Entry) -> list[str]:
        refs = list(entry.links)
        for key in REFERENCE_KEYS:
            if key in entry.details:
                refs.extend(f"{p}-{n}" for p, n in ID_REF.findall(entry.details[key][0]))
        return refs

    def check_file(self, entry: Entry) -> None:
        stem = entry.path.stem
        home = HOME[entry.prefix]
        if stem not in {home, f"{home}-ARCHIVE"}:
            self.error(entry.path, entry.line, f"{entry.raw_id} belongs in {home}.md")

    def check_status(self, entry: Entry) -> None:
        path, line, raw_id, state = entry.path, entry.line, entry.raw_id, entry.state
        archived = entry.path.stem.endswith("-ARCHIVE")
        if entry.prefix == "D":
            match = DECISION_STATUS.match(entry.status)
            if not match:
                self.error(
                    path,
                    line,
                    f"{raw_id} has status [{entry.status}]; use proposed, accepted, rejected, replaced "
                    "or resolved (optionally followed by YYYY-MM-DD), or `exception until YYYY-MM-DD`",
                )
                return
            stamp = match.group(2) or match.group(3)
            day = parse_date(stamp) if stamp else None
            if stamp and day is None:
                self.error(path, line, f"{raw_id} has an invalid date {stamp}")
            if match.group(3) and day:
                if day < self.today:
                    self.error(path, line, f"{raw_id} exception ended {stamp}; resolve it or ask the maintainer")
                if "exit" not in entry.details:
                    self.error(path, line, f"{raw_id} is an exception without `exit:`")
        else:
            allowed = STATUSES[entry.prefix]
            if entry.status not in allowed:
                self.error(path, line, f"{raw_id} has status [{entry.status}]; use {', '.join(allowed)}")
                return

        if entry.prefix == "T":
            self.check_task(entry, archived)
        if entry.prefix == "A" and state == "planned" and not any(ref.startswith("R-") for ref in entry.links):
            self.warn(path, line, f"{raw_id} is [planned] but does not link to its outcome (R-)")

        finished = FINISHED.get(entry.prefix, set())
        if not archived and state in finished:
            archive = f"{HOME[entry.prefix]}-ARCHIVE.md"
            self.warn(path, line, f"{raw_id} is [{state}]; move it to {archive}")
        if archived and entry.prefix in {"R", "T"} and state not in finished:
            self.warn(path, line, f"{raw_id} is [{state}] but sits in the archive")

    def check_task(self, entry: Entry, archived: bool) -> None:
        path, line, raw_id = entry.path, entry.line, entry.raw_id
        if entry.status == "done" and "evidence" not in entry.details:
            self.error(path, line, f"{raw_id} is [done] without `evidence:`")
        if archived:
            return
        parent = entry.parent
        if parent is None or parent.prefix != "R":
            if entry.section.lower() != "unplanned":
                self.error(path, line, f"{raw_id} must sit indented under an outcome (R-) or under Unplanned")
            return
        if entry.status in TASK_ACTIVE and parent.state not in OUTCOME_OPEN:
            self.error(
                path,
                line,
                f"{raw_id} is [{entry.status}] under {parent.raw_id}, which is [{parent.status}], not approved",
            )

    def check_placeholders(self, record_files: list[Path]) -> None:
        charter = self.records / "CHARTER.md"
        accepted = False
        if charter.is_file():
            match = CHARTER_STATUS.search("\n".join(visible_lines(charter.read_text(encoding="utf-8"))))
            accepted = bool(match) and match.group(1).lower() == "accepted"
        files = [self.root / "AGENTS.md", self.root / "README.md", *record_files]
        for path in files:
            if not path.is_file():
                continue
            content = path.read_text(encoding="utf-8")
            if PLACEHOLDER_OPT_OUT in content:
                continue
            found = [
                (number, len(PLACEHOLDER.findall(text)))
                for number, text in enumerate(visible_lines(content), start=1)
                if PLACEHOLDER.search(text)
            ]
            if not found:
                continue
            count = sum(hits for _, hits in found)
            message = f"{count} unfilled {{{{placeholder(s)}}}}; list them with grep -n '{{{{' {self.display(path)}"
            if accepted:
                self.error(path, found[0][0], message + " (the charter is accepted)")
            else:
                self.warn(path, found[0][0], message)


def visible_lines(content: str) -> list[str]:
    """Return the file's lines with HTML comments blanked, keeping line numbers."""

    def blank(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    return re.sub(r"<!--.*?-->", blank, content, flags=re.DOTALL).split("\n")


def indent_width(text: str) -> int:
    expanded = text.expandtabs(4)
    return len(expanded) - len(expanded.lstrip(" "))


def parse_id(ref: str) -> tuple[str, int]:
    prefix, number = ref.split("-", 1)
    return (prefix, int(number))


def parse_date(text: str) -> date | None:
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pags-check",
        description="Check that PAGS records agree with each other.",
    )
    parser.add_argument("root", nargs="?", default=".", help="Repository root (default: current directory)")
    parser.add_argument("--records-dir", default=".pags", help="Records folder under the root (default: .pags)")
    parser.add_argument("--today", help="Date to check exceptions against, YYYY-MM-DD (default: today)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--version", action="version", version=f"pags-check {VERSION}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    today = date.today()
    if args.today:
        parsed = parse_date(args.today)
        if parsed is None:
            parser.error(f"--today must be YYYY-MM-DD, not {args.today}")
        today = parsed
    root = Path(args.root).expanduser().resolve()
    checker = Checker(root, args.records_dir, today)
    if not checker.records.is_dir():
        print(f"pags-check: no records folder at {checker.records}", file=sys.stderr)
        return 2

    checker.run()
    for problem in checker.problems:
        print(f"{checker.display(problem.path)}:{problem.line}: {problem.level}: {problem.message}")
    errors = sum(problem.level == "error" for problem in checker.problems)
    warnings = len(checker.problems) - errors
    failed = errors > 0 or (args.strict and warnings > 0)
    summary = f"{len(checker.entries)} entries, {errors} error(s), {warnings} warning(s)"
    print(("FAIL " if failed else "ok   ") + summary)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
