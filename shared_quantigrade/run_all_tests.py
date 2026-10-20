"""Unified Master Test Runner for Quantigrade Enterprise Suite.

Runs pytest independently across all project directories, ensuring isolated
sys.path context and aggregating test outcomes into an executive summary table.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECTS = [
    "WHITE CODING HARNESS",
    "Agent Evaluation Framework — El TAU-benchGAIA",
    "Compliance-as-Code Live Mesh",
    "CFO Director Financiero Autónomo para PYMEs PoC Purgatory",
    "Semantic Discovery Protocol",
    "QGRADE_OS Iwan reference",
]


def run_suite(project_dir: Path) -> tuple[int, int, str]:
    """Runs pytest within the specific project directory."""
    cmd = [sys.executable, "-m", "pytest", "-v", "tests"]
    proc = subprocess.run(cmd, cwd=str(project_dir), capture_output=True, text=True, check=False)
    output = proc.stdout + "\n" + proc.stderr

    passed = 0
    failed = 0
    for line in output.splitlines():
        if " passed in " in line or " passed," in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if p == "passed":
                    passed = int(parts[i - 1])
                elif p.startswith("failed"):
                    failed = int(parts[i - 1])

    return passed, failed, output


def main() -> int:
    base_dir = Path(__file__).resolve().parent.parent
    print(f"\n{'='*75}\nQUANTIGRADE ENTERPRISE MASTER TEST SUITE\n{'='*75}\n")

    total_passed = 0
    total_failed = 0
    summary_rows = []

    for proj in PROJECTS:
        p_path = base_dir / proj
        if not p_path.exists():
            continue

        print(f"--> Testing [{proj}] ...", end=" ", flush=True)
        passed, failed, _ = run_suite(p_path)
        total_passed += passed
        total_failed += failed

        status = "PASSED" if failed == 0 and passed > 0 else "FAILED"
        print(f"{status} ({passed} passed, {failed} failed)")
        summary_rows.append((proj, passed, failed, status))

    print(f"\n{'='*75}\nEXECUTIVE RESULTS SUMMARY\n{'='*75}")
    print(f"{'Project':<55} | {'Passed':<6} | {'Status'}")
    print("-" * 75)
    for name, p_count, f_count, st in summary_rows:
        print(f"{name:<55} | {p_count:<6} | {st}")
    print("-" * 75)
    print(f"TOTAL TESTS: {total_passed} PASSED | {total_failed} FAILED\n")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
