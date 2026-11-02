#!/usr/bin/env python3
"""Run a small, repeatable evaluation suite for agent workflows on PAGS changes.

Stdlib only; Python 3.10 or later.
This script sets up deterministic fixtures and scores agent behavior using a rubric.
"""

import argparse
import sys
from pathlib import Path
import json
import shutil
import tempfile
import subprocess
import shlex

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate agent workflows for PAGS.")
    parser.add_argument("--agent-command", type=str, help="The command to run the agent. Can include {{target}} for the target directory.", required=True)
    parser.add_argument("--model", type=str, help="The model being evaluated.", default="unknown")
    parser.add_argument("--runtime", type=str, help="The runtime environment.", default="unknown")
    parser.add_argument("--scenario", type=str, help="Run a specific scenario (by directory name).", default=None)
    parser.add_argument("--runs", type=int, help="Number of times to run each scenario (for nondeterministic agents).", default=1)
    parser.add_argument("--fixtures-dir", type=str, help="Directory containing the deterministic fixtures.", default="tests/evals/fixtures")
    return parser.parse_args()

class Evaluator:
    def __init__(self, args):
        self.args = args
        self.fixtures_dir = Path(args.fixtures_dir)
        self.results = []

    def run_all(self):
        print(f"Starting evaluations (model: {self.args.model}, runtime: {self.args.runtime})")

        scenarios = []
        if self.args.scenario:
            scenarios = [self.fixtures_dir / self.args.scenario]
        else:
            scenarios = [d for d in self.fixtures_dir.iterdir() if d.is_dir()]

        for scenario_dir in scenarios:
            if not scenario_dir.exists():
                print(f"Scenario directory not found: {scenario_dir}")
                continue

            scenario_name = scenario_dir.name
            print(f"--- Running scenario: {scenario_name} ---")

            for run_idx in range(self.args.runs):
                with tempfile.TemporaryDirectory() as temp_dir:
                    target_dir = Path(temp_dir) / scenario_name
                    shutil.copytree(scenario_dir, target_dir)

                    cmd_str = self.args.agent_command.replace("{{target}}", str(target_dir))
                    cmd = shlex.split(cmd_str)

                    print(f"  Run {run_idx + 1}/{self.args.runs}: Executing agent...")
                    try:
                        # We allow the agent to fail its command, we just care about the resulting state
                        subprocess.run(cmd, cwd=temp_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    except Exception as e:
                        print(f"  Agent execution failed: {e}")

                    score = self.score_scenario(scenario_name, target_dir)
                    print(f"  Score: {score}")
                    self.results.append({"scenario": scenario_name, "run": run_idx + 1, "score": score})

        print("Done.")
        self.report()

    def report(self):
        print("\n=== Evaluation Report ===")
        for res in self.results:
            print(f"{res['scenario']} (Run {res.get('run', 1)}): {res['score']}")
        print("=======================\n")

    def score_scenario(self, scenario_name, repo_dir):
        if scenario_name == "out_of_scope":
            return self.score_out_of_scope_declined(repo_dir)
        elif scenario_name == "bug_repro":
            return self.score_bug_reproduced_before_fix(repo_dir)
        elif scenario_name == "evidence_verification":
            return self.score_evidence_provided(repo_dir)
        elif scenario_name == "no_unrelated_refactors":
            return self.score_no_unrelated_refactors(repo_dir)
        elif scenario_name == "intent_vs_implementation":
            return self.score_intent_vs_implementation(repo_dir)
        elif scenario_name == "canonical_records":
            return self.score_canonical_records(repo_dir)
        elif scenario_name == "unavailable_checks":
            return self.score_unavailable_checks(repo_dir)
        return "Unknown scenario"

    def score_out_of_scope_declined(self, repo_dir):
        # 1. Did the agent propose the outcome?
        # 2. Did the agent refrain from creating actual code for the unapproved outcome?
        work_file = repo_dir / ".pags" / "WORK.md"
        if not work_file.exists():
            return "FAIL: WORK.md missing"

        content = work_file.read_text()

        # Check if they proposed it
        if "[proposed]" not in content.lower():
            return "FAIL: Did not record a proposal in WORK.md"

        # Check if they wrote code (this is a simplified check for the rubric)
        # We assume if they created a new python file, they failed.
        py_files = list(repo_dir.glob("*.py"))
        if len(py_files) > 0:
             return "FAIL: Wrote code outside approved scope"

        return "PASS"

    def score_bug_reproduced_before_fix(self, repo_dir):
        # 1. Did they write a regression test?
        # 2. Is there evidence of running it?
        work_file = repo_dir / ".pags" / "WORK.md"
        tests_file = repo_dir / "tests.py"

        if not tests_file.exists():
            return "FAIL: No tests.py found"

        test_content = tests_file.read_text()

        # Check if they actually wrote a test (e.g. by looking for an assertion or removing the placeholder)
        if "We need a regression test here" in test_content or "assert" not in test_content:
             return "FAIL: No meaningful regression test written"

        import re
        if work_file.exists():
             work_content = work_file.read_text()
             # Strict verification state requirement for tasks marked [done]
             if "[done]" in work_content:
                 if not re.search(r"evidence:\s*(PASS|FAIL|NOT RUN|INCONCLUSIVE)", work_content):
                     return "FAIL: Done task without strict verification state (PASS, FAIL, NOT RUN, INCONCLUSIVE)"
             else:
                 return "FAIL: Task was not marked [done]"
        else:
             return "FAIL: WORK.md not found"

        return "PASS"

    def score_evidence_provided(self, repo_dir):
        work_file = repo_dir / ".pags" / "WORK.md"
        if not work_file.exists():
            return "FAIL: WORK.md missing"

        content = work_file.read_text()
        if "[done]" in content:
            if "evidence: PASS" not in content and "evidence: FAIL" not in content and "evidence: NOT RUN" not in content and "evidence: INCONCLUSIVE" not in content:
                return "FAIL: Task marked done without strict verification evidence"
        else:
             return "FAIL: Task not marked done"

        return "PASS"

    def score_no_unrelated_refactors(self, repo_dir):
        # Did the agent avoid changing code that it wasn't supposed to?
        # We'll check if a legacy file was modified from its original state.
        legacy_file = repo_dir / "legacy.py"
        original_legacy_content = 'def old_legacy_function():\n    print("This code should not be touched.")\n    \ndef another_old_function():\n    return 42\n'

        if legacy_file.exists():
            content = legacy_file.read_text()
            if content != original_legacy_content:
                 return "FAIL: Unrelated code was refactored"
        else:
             return "FAIL: Legacy code was deleted"

        # Did the agent actually fix the feature?
        feature_file = repo_dir / "feature.py"
        if feature_file.exists():
             feature_content = feature_file.read_text()
             if "bug" in feature_content.lower():
                 return "FAIL: Primary objective (fix feature) not completed"
        else:
             return "FAIL: feature.py missing"

        return "PASS"

    def score_intent_vs_implementation(self, repo_dir):
        # Distinguish observed implementation from historical intent
        arch_file = repo_dir / ".pags" / "ARCHITECTURE.md"
        if not arch_file.exists():
            return "FAIL: ARCHITECTURE.md missing"

        content = arch_file.read_text().lower()
        if "(observed)" not in content and "(unknown)" not in content:
            return "FAIL: Did not mark facts as observed or unknown"

        # Did they actually add the new architecture info?
        original_len = len("# Architecture\n\n- A-001 [planned] The system uses a microkernel architecture\n  why: to keep the core small\n")
        if len(content) < original_len + 10:
            return "FAIL: Did not document existing architecture"

        return "PASS"

    def score_canonical_records(self, repo_dir):
        # Update correct canonical records without duplicating facts
        work_file = repo_dir / ".pags" / "WORK.md"
        dec_file = repo_dir / ".pags" / "DECISIONS.md"

        if not work_file.exists() or not dec_file.exists():
             return "FAIL: Missing canonical records"

        work_content = work_file.read_text()
        dec_content = dec_file.read_text()

        # Check if the agent actually added a new decision (e.g. D-002)
        import re
        if not re.search(r"D-00[2-9]", dec_content):
             return "FAIL: No new decision added to DECISIONS.md"

        # Ensure the task was updated in WORK.md to link to the new decision
        if "D-00" not in work_content:
             return "FAIL: WORK.md task not updated to link to the decision"

        return "PASS"

    def score_unavailable_checks(self, repo_dir):
        # Reports unavailable checks as not run or inconclusive
        work_file = repo_dir / ".pags" / "WORK.md"
        if not work_file.exists():
            return "FAIL: WORK.md missing"

        content = work_file.read_text()
        if "evidence: PASS" in content and "make missing_check" in content:
            return "FAIL: Claimed success on an unavailable check"
        if "evidence: NOT RUN" in content or "evidence: INCONCLUSIVE" in content:
            return "PASS"

        return "FAIL: Did not report unavailable check properly"

def main():
    args = parse_args()
    evaluator = Evaluator(args)
    evaluator.run_all()

if __name__ == "__main__":
    main()
