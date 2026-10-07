#!/usr/bin/env python3
"""run_all.py - rebuild and verify the entire course dataset in one command.

Runs every generator and check in the right order, stops on the first failure, and prints a
summary. Everything here is deterministic: running it twice produces byte-identical data, which
is what makes the lab expected-results tables reliable.

Usage:
    python3 scripts/run_all.py                # full run (needs openpyxl for the workbooks)
    python3 scripts/run_all.py --no-workbooks # skip the Excel build if openpyxl is unavailable
    python3 scripts/run_all.py --check-only   # verify the committed data, do not regenerate
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

STEPS = [
    ("Generate Mhondoro client data (18 tables + InjectionLog)", "generate_data.py", True),
    ("Generate Maxhub firm data (engagements, utilisation, pipeline, churn)", "generate_maxhub_data.py", True),
    ("Score the churn model", "ml_churn_model.py", True),
    ("Match near-duplicate vendor names (teaching sample)", "fuzzy_match_vendors.py --file data/practice/VendorName_Matching_Practice.csv", True),
    ("Build the Excel workbooks", "build_workbooks.py", False),
    ("Rebuild the data dictionary", "build_dictionary.py", False),
    ("Run the control-total checks", "verify_data.py", True),
]


def run(script: str, cwd: str) -> tuple[int, str]:
    parts = [sys.executable, os.path.join(HERE, script.split()[0])] + script.split()[1:]
    started = time.time()
    proc = subprocess.run(parts, cwd=cwd, capture_output=True, text=True)
    elapsed = time.time() - started
    output = (proc.stdout or "") + (proc.stderr or "")
    tail = "\n".join(output.rstrip().splitlines()[-6:])
    status = "OK " if proc.returncode == 0 else "FAIL"
    print(f"  [{status}] {script.split()[0]:<26} {elapsed:5.1f}s")
    if proc.returncode != 0:
        print("        " + "\n        ".join(output.rstrip().splitlines()[-12:]))
    return proc.returncode, tail


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Rebuild and verify the course dataset.")
    parser.add_argument("--no-workbooks", action="store_true",
                        help="skip the Excel workbook build (no openpyxl required)")
    parser.add_argument("--check-only", action="store_true",
                        help="run only the verification step against the committed data")
    args = parser.parse_args(argv)

    print("Maxhub Power BI course - dataset pipeline")
    print(f"Repository: {ROOT}\n")

    steps = STEPS
    if args.no_workbooks:
        steps = [s for s in steps if s[2] is not False or "dictionary" in s[1]]
    if args.check_only:
        steps = [s for s in steps if s[1].startswith("verify_data")]

    failures = []
    for label, script, required in steps:
        print(f"* {label}")
        code, _ = run(script, ROOT)
        if code != 0:
            if required:
                failures.append(script)
            else:
                print("        (optional step failed - continuing)")

    print()
    if failures:
        print("PIPELINE FAILED on: " + ", ".join(failures))
        print("Fix the failures above before using the data - the lab expected results depend on it.")
        return 1

    print("PIPELINE COMPLETE - all required steps passed.")
    print("Next: open Power BI Desktop and start Module 1, or Lab 01 if you are already set up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
