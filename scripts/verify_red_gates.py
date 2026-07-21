#!/usr/bin/env python3
"""Confirm that every published benchmark stub begins in a real pytest-red state."""

from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "benchmark" / "cards"
CATALOG = ROOT / "evidence" / "card-catalog.csv"
REFERENCE_C10 = (
    ROOT / "evidence" / "reference-artifacts" / "gpt55-xhigh-c10" / "glob_matcher.py"
)
PUBLIC_REPLAY_SEED = "20260721"


def natural_card_key(path: Path) -> int:
    match = re.match(r"card(\d+)", path.name)
    if match is None:
        raise ValueError(f"unrecognized card directory: {path.name}")
    return int(match.group(1))


def main() -> int:
    with CATALOG.open(newline="", encoding="utf-8") as handle:
        catalog_rows = list(csv.DictReader(handle))
    expected_counts = {row["slug"]: int(row["published_test_count"]) for row in catalog_rows}

    card_dirs = sorted(
        (path for path in CARDS.iterdir() if path.is_dir()),
        key=natural_card_key,
    )
    if len(card_dirs) != 10:
        print(
            f"RED-GATE VERIFY FAILED: expected 10 card directories, found {len(card_dirs)}",
            file=sys.stderr,
        )
        return 1
    if set(expected_counts) != {path.name for path in card_dirs}:
        print("RED-GATE VERIFY FAILED: card catalog and published directories disagree", file=sys.stderr)
        return 1

    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="strong-cards-hypothesis-") as hypothesis_storage:
        clean_environment = os.environ.copy()
        clean_environment["PYTHONDONTWRITEBYTECODE"] = "1"
        clean_environment["HYPOTHESIS_STORAGE_DIRECTORY"] = hypothesis_storage

        for card_dir in card_dirs:
            process = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "--color=no",
                    "-p",
                    "no:cacheprovider",
                    f"--hypothesis-seed={PUBLIC_REPLAY_SEED}",
                    str(card_dir),
                ],
                cwd=card_dir,
                env=clean_environment,
                check=False,
                capture_output=True,
                text=True,
            )
            output = process.stdout + process.stderr
            summaries = re.findall(r"(?:^|\s)(\d+) failed(?:,|\s|$)", output)
            observed_count = int(summaries[-1]) if summaries else None
            expected_count = expected_counts[card_dir.name]
            if process.returncode != 1 or observed_count != expected_count:
                failures.append(
                    f"{card_dir.name}: expected pytest exit 1 with {expected_count} failing tests, "
                    f"observed exit {process.returncode} and count {observed_count!r}"
                )
            else:
                summary = next(
                    (line for line in reversed(output.splitlines()) if " failed" in line),
                    "red",
                )
                print(f"{card_dir.name}: {summary}")

    if failures:
        for failure in failures:
            print(f"RED-GATE VERIFY FAILED: {failure}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="strong-cards-c10-reference-") as raw_directory:
        directory = Path(raw_directory)
        shutil.copy2(REFERENCE_C10, directory / "glob_matcher.py")
        shutil.copy2(
            CARDS / "card10-master-coder" / "test_glob_matcher.py",
            directory / "test_glob_matcher.py",
        )
        clean_environment = os.environ.copy()
        clean_environment["PYTHONDONTWRITEBYTECODE"] = "1"
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "--color=no",
                "-p",
                "no:cacheprovider",
                f"--hypothesis-seed={PUBLIC_REPLAY_SEED}",
                "test_glob_matcher.py",
            ],
            cwd=directory,
            env=clean_environment,
            check=False,
            capture_output=True,
            text=True,
        )
        output = process.stdout + process.stderr
        if process.returncode != 0 or re.search(r"\b7 passed\b", output) is None:
            print(
                "RED-GATE VERIFY FAILED: published GPT C10 reference did not replay as 7/7",
                file=sys.stderr,
            )
            print(output, file=sys.stderr)
            return 1
        summary = next(
            (line for line in reversed(output.splitlines()) if " passed" in line),
            "7 passed",
        )
        print(f"gpt55-xhigh-c10-reference: {summary}")

    print(
        "RED-GATE VERIFY PASSED: all ten stubs are red and the excluded GPT C10 "
        f"reference replays 7/7 with public seed {PUBLIC_REPLAY_SEED}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
