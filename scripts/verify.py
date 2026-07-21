#!/usr/bin/env python3
"""Verify the consistency and public hygiene of the Strong Cards pilot."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
BENCHMARK = ROOT / "benchmark" / "cards"


class VerificationError(RuntimeError):
    """Raised when a publication invariant is false."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"expected object in {path.relative_to(ROOT)}")
    return value


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(bool(rows), f"no rows in {path.relative_to(ROOT)}")
    return rows


def require_fields(rows: list[dict[str, str]], expected: tuple[str, ...], label: str) -> None:
    observed = tuple(rows[0])
    require(observed == expected, f"{label} header mismatch: expected {expected!r}, got {observed!r}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_study() -> None:
    study = read_json(EVIDENCE / "study.json")
    architecture = study["architecture"]
    benchmark = study["benchmark"]

    require(study["status"] == "first_test_preliminary", "study must remain labelled preliminary")
    require(
        architecture["runtime_control_plane_llm_orchestrator_or_coordinator"] is False,
        "runtime must declare no control-plane LLM coordinator",
    )
    require(
        architecture["runtime_controller"]["llm_control_plane_decisions_per_task_loop"] == 0,
        "runtime control-plane LLM decision count must be zero",
    )
    require(architecture["card_authoring"]["model"] == "GPT-5.5", "card-author model mismatch")
    require(architecture["card_authoring"]["reasoning_effort"] == "medium", "card-author effort mismatch")
    require(benchmark["published_cards"] == 10, "published-card count mismatch")
    require(benchmark["valid_comparative_cards"] == 9, "valid-card count mismatch")
    require(benchmark["comparative_card_ids"] == [f"C{i}" for i in range(1, 10)], "valid card IDs mismatch")
    require(benchmark["excluded_card_ids"] == ["C10"], "C10 must be the sole excluded card")
    require(
        benchmark["frozen_before_principal_comparison_sweeps"] is True,
        "deck must be recorded as frozen before the principal comparison sweeps",
    )
    require(
        benchmark["adaptive_deck_development_before_freeze"] is True,
        "adaptive deck development must be disclosed",
    )
    require(benchmark["hidden_tests"] is False, "v1 must not claim hidden tests")

    hardware = study["local_hardware"]
    require(hardware["soc"] == "Apple M5 Max", "local SoC mismatch")
    require(hardware["reported_core_count"] == 18, "reported core count mismatch")
    require(hardware["unified_memory_gb"] == 128, "reported memory mismatch")
    require(hardware["unique_machine_identifiers_published"] is False, "unique machine identifiers must stay private")

    surfaces = {item["surface"] for item in study["execution_surfaces"]}
    require(surfaces == {"claude-ollama", "OpenCode CLI", "Codex"}, "execution-surface set mismatch")
    for relative in study["public_evidence_files"]:
        path = (EVIDENCE / relative).resolve()
        require(path.is_relative_to(EVIDENCE), f"public evidence path escapes evidence directory: {relative}")
        require(path.is_file(), f"missing canonical public evidence file: {relative}")


def verify_card_catalog_and_hashes() -> None:
    rows = read_csv(EVIDENCE / "card-catalog.csv")
    require(len(rows) == 10, "card catalog must contain ten rows")
    require([row["card_id"] for row in rows] == [f"C{i}" for i in range(1, 11)], "card order mismatch")

    digest_fields = ("card_sha256", "prompt_sha256", "stub_sha256", "test_sha256")
    for row in rows:
        card_id = row["card_id"]
        card_dir = BENCHMARK / row["slug"]
        require(card_dir.is_dir(), f"missing published directory for {card_id}")
        require(row["frozen"] == "true", f"{card_id} must be marked frozen")
        require(row["red_gate_verified"] == "true", f"{card_id} red gate must be verified")
        for field in digest_fields:
            require(re.fullmatch(r"[0-9a-f]{64}", row[field]) is not None, f"invalid {field} for {card_id}")

        card_path = card_dir / "CARD.md"
        test_paths = sorted(card_dir.glob("test_*.py"))
        solution_paths = sorted(path for path in card_dir.glob("*.py") if not path.name.startswith("test_"))
        require(len(test_paths) == 1, f"{card_id} must publish exactly one test file")
        require(len(solution_paths) == 1, f"{card_id} must publish exactly one solution stub")
        require(sha256(card_path) == row["card_sha256"], f"{card_id} card hash mismatch")
        require(sha256(solution_paths[0]) == row["stub_sha256"], f"{card_id} stub hash mismatch")
        require(sha256(test_paths[0]) == row["test_sha256"], f"{card_id} test hash mismatch")

        if card_id == "C10":
            expected_status = "excluded"
        elif card_id == "C9":
            expected_status = "valid_with_known_public_test_gap"
        else:
            expected_status = "valid"
        require(row["comparative_status"] == expected_status, f"{card_id} comparative status mismatch")
        if card_id in {"C9", "C10"}:
            require(bool(row["exclusion_reason"]), f"{card_id} qualification reason is required")


def verify_model_tables() -> None:
    models = read_csv(EVIDENCE / "model-summary.csv")
    hosted = read_csv(EVIDENCE / "hosted-results.csv")
    local = read_csv(EVIDENCE / "local-attempts.csv")

    require_fields(
        models,
        (
            "model_id",
            "model_family",
            "execution_surface",
            "inference_location",
            "rankable_on_comparative_cards",
            "published_gate_cards_passed",
            "comparative_cards_total",
            "published_gate_ceiling",
            "first_comparative_break",
            "worker_wall_seconds_to_published_gate_ceiling",
            "retry_passes",
            "C10_observed",
            "C10_ranking_status",
            "comparison_note",
        ),
        "model-summary.csv",
    )
    require_fields(
        hosted,
        (
            "model_id",
            "execution_surface",
            "inference_location",
            *(f"C{i}" for i in range(1, 10)),
            "C10_observed",
            "published_gate_ceiling",
            "worker_wall_seconds_to_published_gate_ceiling",
            "comparative_break_class",
            "notes",
        ),
        "hosted-results.csv",
    )
    require_fields(
        local,
        (
            "source_run",
            "model_tag",
            "execution_surface",
            "inference_location",
            "hardware",
            "card_id",
            "attempt",
            "attempt_kind",
            "worker_wall_seconds",
            "timeout",
            "gate_passed",
            "gate_total",
            "stub_gate",
            "scope_gate",
            "runner_verdict",
            "comparative_score_effect",
            "note",
        ),
        "local-attempts.csv",
    )

    require(len(models) == 17, "model summary must contain 17 configurations")
    require(len(hosted) == 13, "hosted table must contain 13 routes")
    require(len(local) == 35, "local ledger must contain 35 events")
    require(len({row["model_id"] for row in models}) == 17, "model IDs must be unique")
    require(len({row["model_id"] for row in hosted}) == 13, "hosted route IDs must be unique")
    require(all(row["C10_ranking_status"] == "excluded_benchmark_defect" for row in models), "every C10 model result must be excluded")

    by_model = {row["model_id"]: row for row in models}

    local_by_model: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in local:
        local_by_model[event["model_tag"]].append(event)
        require(event["execution_surface"] == "claude-ollama", "local event surface mismatch")
        require(event["inference_location"] == "local_Ollama", "local event inference location mismatch")
        require(event["hardware"] == "M5_Max_18-core_128GB", "local event hardware mismatch")

    require(len(local_by_model) == 3, "local ledger must describe exactly three configurations")
    require(set(local_by_model).issubset(by_model), "local configurations missing from model summary")
    for model_id, events in local_by_model.items():
        accepted_cards = {
            int(event["card_id"][1:])
            for event in events
            if event["card_id"] != "C10"
            and event["runner_verdict"] == "PASS"
            and event["comparative_score_effect"] == "accepted_card"
        }
        published_passes = len(accepted_cards)
        ceiling = 0
        while ceiling + 1 in accepted_cards:
            ceiling += 1
        require(published_passes == ceiling, f"{model_id} has a non-contiguous accepted-card sequence")

        wall_to_ceiling = sum(
            int(event["worker_wall_seconds"])
            for event in events
            if event["card_id"] != "C10"
            and int(event["card_id"][1:]) <= ceiling
            and event["worker_wall_seconds"]
        )
        retry_passes = sum(
            event["card_id"] != "C10"
            and event["runner_verdict"] == "PASS"
            and event["attempt"].isdigit()
            and int(event["attempt"]) > 1
            for event in events
        )
        first_break = "none" if ceiling == 9 else f"C{ceiling + 1}"

        summary = by_model[model_id]
        require(summary["execution_surface"] == "claude-ollama", f"{model_id} summary surface mismatch")
        require(summary["inference_location"] == "local_Ollama", f"{model_id} must be local")
        require(summary["rankable_on_comparative_cards"] == "true", f"{model_id} must be rankable")
        require(int(summary["published_gate_cards_passed"]) == published_passes, f"{model_id} pass count mismatch")
        require(int(summary["comparative_cards_total"]) == 9, f"{model_id} comparative total mismatch")
        require(int(summary["published_gate_ceiling"]) == ceiling, f"{model_id} ceiling mismatch")
        require(summary["first_comparative_break"] == first_break, f"{model_id} first-break mismatch")
        require(
            int(summary["worker_wall_seconds_to_published_gate_ceiling"]) == wall_to_ceiling,
            f"{model_id} wall total mismatch",
        )
        require(int(summary["retry_passes"]) == retry_passes, f"{model_id} retry-pass count mismatch")

    hosted_nine = [row for row in hosted if row["published_gate_ceiling"] == "9"]
    require(len(hosted_nine) == 8, "exactly eight hosted routes must have full C1-C9 acceptance")
    study = read_json(EVIDENCE / "study.json")
    hosted_headlines = [
        item for item in study["headline_results"]
        if item["model"] == "hosted comparison group"
    ]
    require(len(hosted_headlines) == 1, "study must contain one hosted headline row")
    hosted_headline = hosted_headlines[0]
    require(
        set(hosted_headline["models_reaching_ceiling"]) == {row["model_id"] for row in hosted_nine},
        "study headline hosted routes disagree with hosted-results.csv",
    )
    require({row["model_id"] for row in hosted}.issubset(by_model), "hosted routes missing from model summary")
    for row in hosted:
        require(row["execution_surface"] == "OpenCode_CLI", f"hosted row surface mismatch for {row['model_id']}")
        require(row["inference_location"] == "hosted", f"hosted location mismatch for {row['model_id']}")

        accepted = [row[f"C{i}"] in {"PASS", "PASS_ON_RETRY"} for i in range(1, 10)]
        published_passes = sum(accepted)
        ceiling = 0
        while ceiling < 9 and accepted[ceiling]:
            ceiling += 1
        require(published_passes == ceiling, f"{row['model_id']} has a non-contiguous hosted pass sequence")
        first_break = "none" if ceiling == 9 else f"C{ceiling + 1}"
        retry_passes = sum(row[f"C{i}"] == "PASS_ON_RETRY" for i in range(1, 10))

        require(int(row["published_gate_ceiling"]) == ceiling, f"hosted recomputed ceiling mismatch for {row['model_id']}")
        summary = by_model[row["model_id"]]
        require(summary["execution_surface"] == "OpenCode_CLI", f"hosted summary surface mismatch for {row['model_id']}")
        require(summary["inference_location"] == "hosted", f"hosted summary location mismatch for {row['model_id']}")
        require(summary["rankable_on_comparative_cards"] == "true", f"{row['model_id']} must be rankable")
        require(int(summary["published_gate_cards_passed"]) == published_passes, f"hosted pass count mismatch for {row['model_id']}")
        require(int(summary["comparative_cards_total"]) == 9, f"hosted comparative total mismatch for {row['model_id']}")
        require(int(summary["published_gate_ceiling"]) == ceiling, f"hosted summary ceiling mismatch for {row['model_id']}")
        require(summary["first_comparative_break"] == first_break, f"hosted first-break mismatch for {row['model_id']}")
        require(
            summary["worker_wall_seconds_to_published_gate_ceiling"]
            == row["worker_wall_seconds_to_published_gate_ceiling"],
            f"hosted wall mismatch for {row['model_id']}",
        )
        require(int(summary["retry_passes"]) == retry_passes, f"hosted retry-pass mismatch for {row['model_id']}")

    expected_model_ids = set(local_by_model) | {row["model_id"] for row in hosted} | {"GPT-5.5_xhigh"}
    require(set(by_model) == expected_model_ids, "model summary contains missing or unexplained configurations")

    local_headlines = {
        item["model"]: item
        for item in study["headline_results"]
        if item["placement"] == "local"
    }
    require(
        set(local_headlines) == {"qwen3.6:27b-mtp-q8_0", "gemma4:31b-coding-mtp-bf16"},
        "study local headline model set mismatch",
    )
    for model_id, headline in local_headlines.items():
        require(
            int(headline["published_gate_cards_passed"])
            == int(by_model[model_id]["published_gate_cards_passed"]),
            f"study local headline pass count mismatch for {model_id}",
        )

    kimi = by_model["opencode-go/kimi-k2.7-code"]
    require(kimi["published_gate_cards_passed"] == "8", "Kimi K2.7 full-gate score mismatch")
    require("tests were green" in kimi["comparison_note"], "Kimi anti-stub qualification missing")

    gpt = by_model["GPT-5.5_xhigh"]
    require(gpt["rankable_on_comparative_cards"] == "false", "GPT C10-only run must not enter comparative ranking")
    require(gpt["published_gate_ceiling"] == "not_run", "GPT must not be given a C1-C9 ceiling")

    qwen_retry = [
        row for row in local
        if row["model_tag"] == "qwen3.6:27b-mtp-q8_0" and row["card_id"] == "C9"
    ]
    require(len(qwen_retry) == 2, "Qwen27 C9 must retain both attempts")
    require(qwen_retry[0]["runner_verdict"] == "TIMEOUT" and qwen_retry[0]["worker_wall_seconds"] == "900", "Qwen27 C9 first attempt mismatch")
    require(qwen_retry[1]["runner_verdict"] == "PASS" and qwen_retry[1]["worker_wall_seconds"] == "2006", "Qwen27 C9 retry mismatch")

    gemma_c9 = [
        row for row in local
        if row["model_tag"] == "gemma4:31b-coding-mtp-bf16" and row["card_id"] == "C9"
    ]
    require(len(gemma_c9) == 1 and gemma_c9[0]["runner_verdict"] == "PASS", "Gemma C9 result mismatch")
    require(gemma_c9[0]["worker_wall_seconds"] == "804", "Gemma C9 wall mismatch")

    c10_rows = [row for row in local if row["card_id"] == "C10"]
    require(
        c10_rows and all(row["comparative_score_effect"] == "excluded_card" for row in c10_rows),
        "local C10 rows must be excluded",
    )


def verify_card_matrix() -> None:
    matrix = read_csv(EVIDENCE / "card-matrix.csv")
    models = read_csv(EVIDENCE / "model-summary.csv")
    hosted = read_csv(EVIDENCE / "hosted-results.csv")
    local = read_csv(EVIDENCE / "local-attempts.csv")

    require_fields(
        matrix,
        (
            "rank",
            "model_id",
            "lane",
            *(f"C{i}" for i in range(1, 10)),
            "full_gate_score",
            "retry_passes",
            "first_break",
            "C10_diagnostic",
        ),
        "card-matrix.csv",
    )
    require(len(matrix) == 17, "card matrix must contain all 17 configurations")
    require(len({row["model_id"] for row in matrix}) == 17, "card matrix model IDs must be unique")

    summary = {row["model_id"]: row for row in models}
    by_matrix = {row["model_id"]: row for row in matrix}
    require(set(by_matrix) == set(summary), "card matrix and model summary model sets differ")

    rankable = [row for row in matrix if row["model_id"] != "GPT-5.5_xhigh"]
    score_counts: dict[int, int] = defaultdict(int)
    for row in rankable:
        score_counts[int(row["full_gate_score"])] += 1

    for row in matrix:
        model_id = row["model_id"]
        states = [row[f"C{i}"] for i in range(1, 10)]
        require(set(states).issubset({"P", "R", "G", "F", "N"}), f"unknown matrix state for {model_id}")
        require(row["C10_diagnostic"] == "N" or row["C10_diagnostic"].startswith("X:"), f"invalid C10 diagnostic for {model_id}")

        if model_id == "GPT-5.5_xhigh":
            require(row["rank"] == "" and row["full_gate_score"] == "", "GPT reference must stay unranked")
            require(states == ["N"] * 9, "GPT reference must not imply C1-C9 runs")
            require(row["C10_diagnostic"] == "X:PASS_7_OF_7", "GPT reference diagnostic mismatch")
            continue

        accepted = [state in {"P", "R"} for state in states]
        score = sum(accepted)
        ceiling = 0
        while ceiling < 9 and accepted[ceiling]:
            ceiling += 1
        require(score == ceiling, f"matrix has non-contiguous acceptance for {model_id}")
        require(int(row["full_gate_score"]) == score, f"matrix score mismatch for {model_id}")
        require(int(summary[model_id]["published_gate_cards_passed"]) == score, f"summary score mismatch for {model_id}")
        require(int(row["retry_passes"]) == states.count("R"), f"matrix retry count mismatch for {model_id}")
        require(int(summary[model_id]["retry_passes"]) == states.count("R"), f"summary retry mismatch for {model_id}")
        first_break = "none" if ceiling == 9 else f"C{ceiling + 1}"
        require(row["first_break"] == first_break, f"matrix breakpoint mismatch for {model_id}")

        expected_rank = 1 + sum(count for value, count in score_counts.items() if value > score)
        require(int(row["rank"]) == expected_rank, f"competition rank mismatch for {model_id}")

        expected_lane = "local" if summary[model_id]["inference_location"] == "local_Ollama" else "hosted"
        require(row["lane"] == expected_lane, f"matrix lane mismatch for {model_id}")

    hosted_state = {
        "PASS": "P",
        "PASS_ON_RETRY": "R",
        "FAIL_SCOPE_X2": "G",
        "FAIL_ANTISTUB_X2": "G",
        "SKIPPED": "N",
    }
    for result in hosted:
        matrix_row = by_matrix[result["model_id"]]
        for card in (f"C{i}" for i in range(1, 10)):
            expected = hosted_state.get(result[card], "F")
            require(matrix_row[card] == expected, f"hosted matrix cell mismatch for {result['model_id']} {card}")

    local_models = {
        row["model_tag"]
        for row in local
        if row["model_tag"] in by_matrix
    }
    require(len(local_models) == 3, "matrix must cover three local configurations")
    for model_id in local_models:
        model_events = [row for row in local if row["model_tag"] == model_id]
        for index in range(1, 10):
            card = f"C{index}"
            events = [row for row in model_events if row["card_id"] == card]
            accepted_events = [row for row in events if row["runner_verdict"] == "PASS"]
            if accepted_events:
                expected = "R" if any(int(row["attempt"]) > 1 for row in accepted_events) else "P"
            elif events and all(row["runner_verdict"] == "SKIPPED_AFTER_BREAK" for row in events):
                expected = "N"
            else:
                expected = "F"
            require(by_matrix[model_id][card] == expected, f"local matrix cell mismatch for {model_id} {card}")


def verify_runner_artifacts() -> None:
    rows = read_csv(EVIDENCE / "runner-artifacts.csv")
    require_fields(
        rows,
        (
            "artifact_id",
            "source_file",
            "source_sha256",
            "public_file",
            "public_sha256",
            "sanitization",
        ),
        "runner-artifacts.csv",
    )
    require(len(rows) == 6, "runner artifact manifest must contain six rows")
    require(len({row["artifact_id"] for row in rows}) == 6, "runner artifact IDs must be unique")

    for row in rows:
        require(re.fullmatch(r"[0-9a-f]{64}", row["source_sha256"]) is not None, "invalid source runner hash")
        require(re.fullmatch(r"[0-9a-f]{64}", row["public_sha256"]) is not None, "invalid public runner hash")
        path = (ROOT / row["public_file"]).resolve()
        require(path.is_relative_to(ROOT / "runner" / "archive"), f"runner path escapes archive: {row['public_file']}")
        require(path.is_file(), f"missing public runner: {row['public_file']}")
        require(sha256(path) == row["public_sha256"], f"public runner hash mismatch: {row['artifact_id']}")
        if row["sanitization"] == "byte_identical":
            require(row["source_sha256"] == row["public_sha256"], "byte-identical runner hashes differ")

        syntax = subprocess.run(["bash", "-n", str(path)], cwd=ROOT, check=False, capture_output=True, text=True)
        require(syntax.returncode == 0, f"bash syntax failure in {row['public_file']}: {syntax.stderr.strip()}")


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_accepted_artifacts() -> None:
    accepted = EVIDENCE / "accepted-artifacts"
    metadata = read_json(accepted / "metadata.json")
    require(metadata["card_id"] == "C9", "accepted-artifact card mismatch")
    artifacts = metadata["artifacts"]
    require(isinstance(artifacts, list) and len(artifacts) == 2, "expected two accepted Card 9 artifacts")

    by_model: dict[str, tuple[dict, ModuleType]] = {}
    for index, artifact in enumerate(artifacts):
        require(re.fullmatch(r"[0-9a-f]{64}", artifact["solution_sha256"]) is not None, "invalid solution hash")
        require(re.fullmatch(r"[0-9a-f]{64}", artifact["gate_output_sha256"]) is not None, "invalid gate-output hash")
        solution = (accepted / artifact["solution"]).resolve()
        gate_output = (accepted / artifact["gate_output"]).resolve()
        require(solution.is_relative_to(accepted) and solution.is_file(), "accepted solution path is invalid")
        require(gate_output.is_relative_to(accepted) and gate_output.is_file(), "accepted gate-output path is invalid")
        require(sha256(solution) == artifact["solution_sha256"], f"solution hash mismatch for {artifact['model']}")
        require(sha256(gate_output) == artifact["gate_output_sha256"], f"gate-output hash mismatch for {artifact['model']}")
        require("11 passed" in gate_output.read_text(encoding="utf-8"), f"gate output is not green for {artifact['model']}")
        require(artifact["published_gate"] == "11 passed", f"published gate metadata mismatch for {artifact['model']}")
        by_model[artifact["model"]] = (artifact, load_module(solution, f"accepted_card9_{index}"))

    qwen_id = "qwen3.6:27b-mtp-q8_0"
    gemma_id = "gemma4:31b-coding-mtp-bf16"
    require(set(by_model) == {qwen_id, gemma_id}, "accepted-artifact model set mismatch")
    qwen_meta, qwen = by_model[qwen_id]
    gemma_meta, gemma = by_model[gemma_id]

    multi_letter = {"AA1": 2, "AB1": "=AA1 + 3", "AC1": "=SUM(AA1:AB1)"}
    try:
        qwen.evaluate_workbook(multi_letter)
    except qwen.SpreadsheetError:
        pass
    else:
        raise VerificationError("Qwen Card 9 multi-letter probe no longer reproduces the disclosed error")
    require(
        gemma.evaluate_workbook(multi_letter) == {"AA1": 2, "AB1": 5, "AC1": 7},
        "Gemma Card 9 multi-letter probe mismatch",
    )

    for model_id, (artifact, module) in by_model.items():
        boolean_result = module.evaluate_workbook({"A1": True})
        require(boolean_result["A1"] is True, f"{model_id} no longer reproduces disclosed boolean acceptance")
        division_result = module.evaluate_workbook({"A1": 100000000000000000000, "B1": "=A1 / 3"})
        require(
            division_result["B1"] == 33333333333333331968,
            f"{model_id} no longer reproduces disclosed large-integer precision loss",
        )
        require(
            division_result["B1"] != 33333333333333333333,
            f"{model_id} unexpectedly returned the contract-exact division value",
        )
        require(artifact["posthoc_boolean_value_probe"] == "failed", f"boolean metadata mismatch for {model_id}")
        require(artifact["posthoc_unbounded_integer_division_probe"] == "failed", f"division metadata mismatch for {model_id}")

    require(qwen_meta["posthoc_multi_letter_probe"] == "failed", "Qwen multi-letter metadata mismatch")
    require(gemma_meta["posthoc_multi_letter_probe"] == "passed", "Gemma multi-letter metadata mismatch")

    probes = {probe["name"]: probe for probe in metadata["posthoc_probes"]}
    require(
        set(probes) == {"valid_multi_letter_cells", "boolean_value_rejection", "unbounded_integer_division"},
        "post-hoc probe manifest mismatch",
    )


def verify_card9_audit() -> None:
    text = (EVIDENCE / "card9-posthoc-audit.md").read_text(encoding="utf-8").lower()
    for marker in (
        "multi-letter",
        "boolean values",
        "unbounded integer division",
        "33333333333333331968",
        "33333333333333333333",
        "full-contract proof",
    ):
        require(marker in text, f"Card 9 post-hoc audit missing {marker!r}")


def verify_card10_audit() -> None:
    audit = read_json(EVIDENCE / "card10-audit.json")
    require(audit["audit_verdict"] == "invalid_for_capability_comparison", "C10 audit verdict mismatch")
    require(audit["ranking_included"] is False, "C10 must be excluded from ranking")
    require(audit["primary_defect"]["id"] == "slash_semantics", "C10 primary defect mismatch")
    require(
        audit["secondary_defect"]["id"] == "escaped_backslash_cardinality",
        "C10 secondary defect mismatch",
    )
    reference = audit["reference_run"]
    require(reference["published_gate"] == "PASS", "GPT published-gate result mismatch")
    require(reference["published_tests_passed"] == reference["published_tests_total"] == 7, "GPT test count mismatch")
    require(reference["capability_interpretation"] == "not_clean_semantic_evidence", "GPT interpretation must stay qualified")
    require("hardcoded" in reference["implementation_finding"], "hardcode finding missing")
    require("broadened" in reference["implementation_finding"], "escaped-backslash workaround finding missing")

    json_text = json.dumps(audit, ensure_ascii=False).lower()
    markdown_text = (EVIDENCE / "card10-audit.md").read_text(encoding="utf-8").lower()
    for label, text in (("JSON", json_text), ("Markdown", markdown_text)):
        require("slash" in text and "path" in text, f"C10 {label} audit is missing the slash contradiction")
        require("backslash" in text, f"C10 {label} audit is missing the backslash contradiction")
        require("escape" in text, f"C10 {label} audit is missing the escape-rule finding")


def verify_reference_artifact() -> None:
    reference_root = EVIDENCE / "reference-artifacts"
    metadata = read_json(reference_root / "metadata.json")
    require(metadata["artifact_id"] == "gpt55-xhigh-c10-reference", "C10 reference artifact ID mismatch")
    require(metadata["card_id"] == "C10", "C10 reference card mismatch")
    require(metadata["model"] == "GPT-5.5", "C10 reference model mismatch")
    require(metadata["reasoning_effort"] == "xhigh", "C10 reference effort mismatch")
    require(metadata["execution_surface"] == "Codex", "C10 reference surface mismatch")
    require(metadata["ranking_included"] is False, "C10 reference must stay excluded from ranking")

    solution = (reference_root / metadata["solution"]).resolve()
    gate_output = (reference_root / metadata["gate_output"]).resolve()
    require(solution.is_relative_to(reference_root) and solution.is_file(), "C10 reference solution path is invalid")
    require(gate_output.is_relative_to(reference_root) and gate_output.is_file(), "C10 gate-output path is invalid")
    require(sha256(solution) == metadata["solution_sha256"], "C10 reference solution hash mismatch")
    require(sha256(gate_output) == metadata["gate_output_sha256"], "C10 reference gate-output hash mismatch")
    require("7 passed in 0.33s" in gate_output.read_text(encoding="utf-8"), "C10 reference gate output mismatch")
    require(re.fullmatch(r"[0-9a-f]{64}", metadata["private_session_sha256"]) is not None, "invalid private session hash")

    gate = metadata["published_gate"]
    require(gate["status"] == "PASS", "C10 reference published-gate status mismatch")
    require(gate["tests_passed"] == gate["tests_total"] == 7, "C10 reference published-test count mismatch")
    require(gate["agent_wall_seconds"] == 167.625, "C10 reference agent wall mismatch")
    require(gate["pytest_seconds"] == 0.33, "C10 reference pytest wall mismatch")

    catalog_rows = [row for row in read_csv(EVIDENCE / "card-catalog.csv") if row["card_id"] == "C10"]
    require(len(catalog_rows) == 1, "card catalog must contain one C10 row")
    catalog_c10 = catalog_rows[0]
    frozen = metadata["frozen_input_sha256"]
    require(frozen["card"] == catalog_c10["card_sha256"], "C10 reference card-input hash mismatch")
    require(frozen["prompt"] == catalog_c10["prompt_sha256"], "C10 reference prompt-input hash mismatch")
    require(frozen["stub"] == catalog_c10["stub_sha256"], "C10 reference stub-input hash mismatch")
    require(frozen["public_normalized_test"] == catalog_c10["test_sha256"], "C10 public-test hash mismatch")
    require(
        frozen["original_test"] == "a9a1ba2a63b713b9e22c0862901b9743ea0156405f90e62cb34e9fe40cca3383",
        "C10 original frozen-test hash mismatch",
    )

    module = load_module(solution, "gpt55_xhigh_c10_reference")
    source = solution.read_text(encoding="utf-8")
    require('pattern == "a*b" and text == "a/b"' in source, "C10 slash hard-code is not inspectable")
    require(module.glob_match("a*b", "a/b") is False, "C10 slash workaround no longer reproduces")
    require(module.glob_match("a*c", "a/c") is True, "C10 slash branch is not demonstrably pair-specific")
    escaped_pattern = r"abc\\"
    require(module.glob_match(escaped_pattern, "abc" + "\\") is True, "C10 one-backslash behavior mismatch")
    require(module.glob_match(escaped_pattern, "abc" + "\\" * 2) is True, "C10 doubled-backslash workaround mismatch")
    require(module.glob_match(escaped_pattern, "abc" + "\\" * 3) is True, "C10 broadened-backslash behavior mismatch")

    audit = read_json(EVIDENCE / "card10-audit.json")["reference_run"]
    require(
        audit["published_solution"] == f"reference-artifacts/{metadata['solution']}",
        "C10 audit solution path mismatch",
    )
    require(audit["published_solution_sha256"] == metadata["solution_sha256"], "C10 audit solution hash mismatch")
    require(
        audit["published_gate_output"] == f"reference-artifacts/{metadata['gate_output']}",
        "C10 audit gate-output path mismatch",
    )
    require(audit["published_gate_output_sha256"] == metadata["gate_output_sha256"], "C10 audit gate-output hash mismatch")


def verify_protocol() -> None:
    required = {
        ROOT / "docs" / "strong-card-concept.md": (
            "## Definition",
            "## Formal object",
            "## Required properties",
            "## Division of labor",
            "## Authoring and execution lifecycle",
            "## Readiness test",
            "## What a Strong Card is not",
            "## Lessons from the pilot",
            "INVALID_CARD",
        ),
        ROOT / "docs" / "leaderboard.md": (
            "## What is being ranked",
            "## Every tested configuration, card by card",
            "## The result visible in one line",
            "## What the table does not say",
            "Spreadsheet engine",
            "GPT-5.5 xhigh reference",
        ),
        ROOT / "protocol" / "strong-card-template.md": (
            "## Canonical template",
            "## What is frozen",
            "## Card-authoring rules",
            "## The Card 10 lesson",
        ),
        ROOT / "protocol" / "controller-policy.md": (
            "## Card state machine",
            "## Ordered gates",
            "## Fixed transition table",
            "## One informed retry",
            "## Stop and escalation",
            "## Append-only evidence",
            "## Adapter boundary",
        ),
        ROOT / "protocol" / "minimal-loop.md": (
            "## Control flow",
            "## Reference pseudocode",
            "## Minimal adapter interface",
            "## Reproducibility requirements",
        ),
        ROOT / "PROOF-INDEX.md": (
            "## Evidence classes",
            "## Claim-to-proof map",
            "## Repository classification",
            "## Reproduction order",
            "## Public versus retained proof",
        ),
    }
    for path, markers in required.items():
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            require(marker in text, f"{path.relative_to(ROOT)} missing {marker}")


def public_files() -> list[Path]:
    command = ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"]
    result = subprocess.run(command, cwd=ROOT, check=False, capture_output=True)
    if result.returncode == 0:
        paths = [ROOT / value.decode("utf-8") for value in result.stdout.split(b"\0") if value]
        return sorted(path for path in paths if path.is_file())

    excluded_parts = {".git", ".private-inputs", "__pycache__", ".pytest_cache", ".hypothesis"}
    return sorted(
        path for path in ROOT.rglob("*")
        if path.is_file() and not excluded_parts.intersection(path.relative_to(ROOT).parts)
    )


def verify_public_hygiene() -> None:
    files = public_files()
    require(files, "no public files discovered")
    require(all(".private-inputs" not in path.parts for path in files), "private archive entered public file set")

    forbidden_literals = (
        "/" + "Users" + "/",
        "file" + ":///",
        "Hardware " + "UUID",
        "Provisioning " + "UDID",
        "[GITHUB" + "_LINK]",
        "[LIEN" + "_GITHUB]",
    )
    forbidden_topics = re.compile(r"\b(?:D" + "nD|Dragon" + r"lance)\b", re.IGNORECASE)
    credential = re.compile(r"(?:sk-[A-Za-z0-9_-]{16,}|(?:API|ACCESS|SECRET)_KEY\s*=)")
    emoji = re.compile(
        "["
        "\U0001F1E6-\U0001F1FF"
        "\U0001F300-\U0001FAFF"
        "\U00002600-\U000027BF"
        "]"
    )
    text_extensions = {".md", ".json", ".csv", ".py", ".sh", ".yml", ".yaml", ".cff", ".txt", ""}

    for path in files:
        relative = path.relative_to(ROOT)
        require(path.stat().st_size < 2_000_000, f"unexpected large public file: {relative}")
        if path.suffix.lower() not in text_extensions and path.name not in {"Makefile", "LICENSE"}:
            continue
        text = path.read_text(encoding="utf-8")
        for value in forbidden_literals:
            require(value not in text, f"public file {relative} contains forbidden value {value!r}")
        require(forbidden_topics.search(text) is None, f"public file {relative} names an excluded project")
        require(credential.search(text) is None, f"public file {relative} may contain a credential")
        require(emoji.search(text) is None, f"public file {relative} contains an emoji or pictograph")


def verify_internal_markdown_links() -> None:
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in public_files():
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for raw_target in link_pattern.findall(text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or re.match(r"^[a-z]+://", target):
                continue
            require(".private-inputs" not in target, f"private link in {path.relative_to(ROOT)}")
            resolved = (path.parent / target).resolve()
            require(resolved.exists(), f"broken internal link in {path.relative_to(ROOT)}: {raw_target}")


def main() -> int:
    checks = (
        verify_study,
        verify_card_catalog_and_hashes,
        verify_model_tables,
        verify_card_matrix,
        verify_runner_artifacts,
        verify_accepted_artifacts,
        verify_card9_audit,
        verify_card10_audit,
        verify_reference_artifact,
        verify_protocol,
        verify_public_hygiene,
        verify_internal_markdown_links,
    )
    try:
        for check in checks:
            check()
    except (VerificationError, KeyError, json.JSONDecodeError, OSError, ValueError) as error:
        print(f"VERIFY FAILED: {error}", file=sys.stderr)
        return 1

    print("VERIFY PASSED: evidence, hashes, protocol, links, posts, and public hygiene are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
