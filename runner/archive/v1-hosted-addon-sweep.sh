#!/usr/bin/env bash
set -euo pipefail

ROOT="${PIPELINE_ROOT:?Set PIPELINE_ROOT to the private pipeline-upgrade directory}"
BAKEOFF="$ROOT/bakeoff"
OUT="$ROOT/19-opencode-go-addon-sweep-results.jsonl"

cd "$BAKEOFF"

if [ "$#" -gt 0 ]; then
  models=("$@")
else
  models=(
    "opencode-go/kimi-k2.7-code"
    "opencode-go/deepseek-v4-pro"
  )
fi

cards=(
  "1|card1-lru-cache|lru_cache.py|test_lru_cache.py"
  "2|card2-interval-merge|interval_merge.py|test_interval_merge.py"
  "3|card3-bank-ledger|bank_ledger.py|test_bank_ledger.py"
  "4|card4-undo-stack|undo_stack.py|test_undo_stack.py"
  "5|card5-lru-class|solution.py|test_solution.py"
  "6|card6-interval-merge|solution.py|test_solution.py"
  "7|card7-expression-evaluator|evaluator.py|test_evaluator.py"
  "8|card8-topological-batcher|batcher.py|test_batcher.py"
  "9|card9-spreadsheet-engine|spreadsheet.py|test_spreadsheet.py"
  "10|card10-master-coder|glob_matcher.py|test_glob_matcher.py"
)

if command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_BIN="$(command -v gtimeout)"
elif command -v timeout >/dev/null 2>&1; then
  TIMEOUT_BIN="$(command -v timeout)"
else
  TIMEOUT_BIN=""
fi
export TIMEOUT_BIN

timeout() {
  if [ -n "${TIMEOUT_BIN:-}" ]; then
    "$TIMEOUT_BIN" "$@"
    return
  fi
  python3 - "$@" <<'PY'
import subprocess
import sys

if len(sys.argv) < 3:
    print("usage: timeout SECONDS COMMAND [ARG...]", file=sys.stderr)
    sys.exit(125)

try:
    seconds = float(sys.argv[1])
except ValueError:
    print(f"invalid timeout: {sys.argv[1]!r}", file=sys.stderr)
    sys.exit(125)

try:
    completed = subprocess.run(sys.argv[2:], timeout=seconds)
except subprocess.TimeoutExpired:
    sys.exit(124)
except FileNotFoundError as exc:
    print(str(exc), file=sys.stderr)
    sys.exit(127)
sys.exit(completed.returncode)
PY
}
export -f timeout >/dev/null 2>&1 || true

verify_frozen_manifest() {
  python3 - "$BAKEOFF/frozen-card-manifest.json" "${cards[@]}" <<'PY'
import hashlib
import json
import pathlib
import sys

manifest_path = pathlib.Path(sys.argv[1])
bakeoff = manifest_path.parent
expected_specs = []
for raw in sys.argv[2:]:
    idx, card_dir, solution_file, test_file = raw.split("|")
    expected_specs.append((int(idx), card_dir, solution_file, test_file))

manifest = json.loads(manifest_path.read_text())
cards = manifest.get("cards", [])
errors = []

if manifest.get("card_count") != len(expected_specs):
    errors.append(f"manifest card_count {manifest.get('card_count')} != script card count {len(expected_specs)}")
if len(cards) != len(expected_specs):
    errors.append(f"manifest cards length {len(cards)} != script card count {len(expected_specs)}")

def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

for pos, spec in enumerate(expected_specs):
    if pos >= len(cards):
        break
    idx, card_dir, solution_file, test_file = spec
    card = cards[pos]
    prefix = f"card {idx} {card_dir}:"
    if card.get("card_index") != idx:
        errors.append(f"{prefix} manifest index {card.get('card_index')}")
    if card.get("card_dir") != card_dir:
        errors.append(f"{prefix} manifest dir {card.get('card_dir')}")
    if card.get("solution_file") != solution_file:
        errors.append(f"{prefix} manifest solution {card.get('solution_file')}")
    if card.get("test_file") != test_file:
        errors.append(f"{prefix} manifest test {card.get('test_file')}")
    if card.get("frozen") is not True:
        errors.append(f"{prefix} frozen flag is not true")

    base = bakeoff / card_dir
    hashes = card.get("sha256", {})
    checks = [
        ("CARD.md", base / "CARD.md", hashes.get("card_md")),
        ("CODER_PROMPT.txt", base / "CODER_PROMPT.txt", hashes.get("coder_prompt")),
        (solution_file, base / solution_file, hashes.get("solution_stub")),
    ]
    tests = hashes.get("tests", [])
    if len(tests) != 1 or tests[0].get("path") != test_file:
        errors.append(f"{prefix} manifest tests do not match script test file")
    else:
        checks.append((test_file, base / test_file, tests[0].get("sha256")))

    for label, path, expected in checks:
        if not path.is_file():
            errors.append(f"{prefix} missing {label}")
            continue
        actual = sha256(path)
        if actual != expected:
            errors.append(f"{prefix} {label} sha256 mismatch")

if errors:
    for error in errors:
        print(f"FROZEN_MANIFEST_ERROR: {error}", file=sys.stderr)
    sys.exit(1)

print(f"Frozen manifest verified: {len(expected_specs)} cards")
PY
}

append_json() {
  python3 - "$OUT" <<'PY'
import json
import os
import sys

path = sys.argv[1]
row = json.loads(os.environ["SWEEP_ROW_JSON"])
with open(path, "a") as f:
    f.write(json.dumps(row) + "\n")
PY
}

run_one() {
  local model="$1" idx="$2" card="$3" sol="$4" test="$5" attempt="$6"
  local prompt_override="${7:-}"
  local started ended output rc result verdict coder_rc run_dir gate_tail output_tail prompt_override_used timeout_hit
  started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  set +e
  output="$(bash run_cell.sh "$card" "$sol" "$test" "$model" "$prompt_override" 2>&1)"
  rc=$?
  set -e
  ended="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  result="$(printf '%s\n' "$output" | awk 'index($0, "RESULT|") == 1 {line=$0} END{print line}')"
  verdict="$(printf '%s' "$result" | sed -n 's/.*VERDICT=\([^|]*\).*/\1/p')"
  coder_rc="$(printf '%s' "$result" | sed -n 's/.*|crc=\([0-9][0-9]*\)|.*/\1/p')"
  timeout_hit="false"
  if [ "$coder_rc" = "124" ]; then
    verdict="TIMEOUT"
    timeout_hit="true"
  fi
  [ -n "$verdict" ] || verdict="FAIL"
  run_dir="$BAKEOFF/runs/$(basename "$card")__$(printf '%s' "$model" | sed 's#[/:]#_#g')"
  gate_tail=""
  if [ -f "$run_dir/_gate_pytest.out" ]; then
    gate_tail="$(tail -80 "$run_dir/_gate_pytest.out")"
  fi
  output_tail="$(printf '%s' "$output" | tail -c 4000)"
  prompt_override_used="false"
  [ -n "$prompt_override" ] && prompt_override_used="true"
  export SWEEP_MODEL="$model"
  export SWEEP_IDX="$idx"
  export SWEEP_CARD="$card"
  export SWEEP_SOL="$sol"
  export SWEEP_TEST="$test"
  export SWEEP_ATTEMPT="$attempt"
  export SWEEP_STARTED="$started"
  export SWEEP_ENDED="$ended"
  export SWEEP_RC="$rc"
  export SWEEP_CODER_RC="$coder_rc"
  export SWEEP_RESULT="$result"
  export SWEEP_VERDICT="$verdict"
  export SWEEP_RUN_DIR="$run_dir"
  export SWEEP_OUTPUT_TAIL="$output_tail"
  export SWEEP_GATE_TAIL="$gate_tail"
  export SWEEP_PROMPT_OVERRIDE_USED="$prompt_override_used"
  export SWEEP_TIMEOUT_HIT="$timeout_hit"
  SWEEP_ROW_JSON="$(python3 - <<'PY'
import json
import os

row = {
    "model": os.environ["SWEEP_MODEL"],
    "card_index": int(os.environ["SWEEP_IDX"]),
    "card_dir": os.environ["SWEEP_CARD"],
    "solution_file": os.environ["SWEEP_SOL"],
    "test_file": os.environ["SWEEP_TEST"],
    "attempt": int(os.environ["SWEEP_ATTEMPT"]),
    "started_at": os.environ["SWEEP_STARTED"],
    "ended_at": os.environ["SWEEP_ENDED"],
    "return_code": int(os.environ["SWEEP_RC"]),
    "coder_return_code": int(os.environ["SWEEP_CODER_RC"]) if os.environ["SWEEP_CODER_RC"] else None,
    "result_line": os.environ["SWEEP_RESULT"],
    "verdict": os.environ["SWEEP_VERDICT"],
    "run_dir": os.environ["SWEEP_RUN_DIR"],
    "prompt_override_used": os.environ["SWEEP_PROMPT_OVERRIDE_USED"] == "true",
    "timeout": os.environ["SWEEP_TIMEOUT_HIT"] == "true",
    "stdout_stderr_tail": os.environ["SWEEP_OUTPUT_TAIL"],
    "gate_tail": os.environ["SWEEP_GATE_TAIL"],
}
print(json.dumps(row))
PY
)"
  export SWEEP_ROW_JSON
  append_json
  printf '%s\n' "$result"
  [ "$verdict" = "PASS" ]
}

verify_frozen_manifest
: > "$OUT"

for model in "${models[@]}"; do
  echo "== SMOKE $model =="
  set +e
  smoke_output="$(timeout 60 opencode run --pure -m "$model" "Reply READY only." 2>&1)"
  smoke_rc=$?
  set -e
  if [ "$smoke_rc" -ne 0 ]; then
    smoke_verdict="UNAVAILABLE"
    [ "$smoke_rc" -eq 124 ] && smoke_verdict="TIMEOUT"
    SWEEP_ROW_JSON="$(MODEL="$model" RC="$smoke_rc" VERDICT="$smoke_verdict" TAIL="$(printf '%s' "$smoke_output" | tail -c 4000)" python3 - <<'PY'
import json
import os

print(json.dumps({
    "model": os.environ["MODEL"],
    "smoke": "FAIL",
    "smoke_return_code": int(os.environ["RC"]),
    "verdict": os.environ["VERDICT"],
    "stdout_stderr_tail": os.environ["TAIL"],
}))
PY
)"
    export SWEEP_ROW_JSON
    append_json
    continue
  fi

  broken=0
  for spec in "${cards[@]}"; do
    IFS='|' read -r idx card sol test <<< "$spec"
    if [ "$broken" -eq 1 ]; then
      SWEEP_ROW_JSON="$(MODEL="$model" IDX="$idx" CARD="$card" python3 - <<'PY'
import json
import os

print(json.dumps({
    "model": os.environ["MODEL"],
    "card_index": int(os.environ["IDX"]),
    "card_dir": os.environ["CARD"],
    "verdict": "SKIPPED_AFTER_BREAK",
}))
PY
)"
      export SWEEP_ROW_JSON
      append_json
      continue
    fi

    echo "== RUN $model card$idx $card attempt1 =="
    if run_one "$model" "$idx" "$card" "$sol" "$test" "1"; then
      verify_frozen_manifest >/dev/null
      continue
    fi
    verify_frozen_manifest >/dev/null

    tag="$(basename "$card")__$(printf '%s' "$model" | sed 's#[/:]#_#g')"
    if [ -d "$BAKEOFF/runs/$tag" ]; then
      rm -rf "$BAKEOFF/runs/${tag}_attempt1"
      cp -R "$BAKEOFF/runs/$tag" "$BAKEOFF/runs/${tag}_attempt1"
      retry_prompt="$BAKEOFF/runs/${tag}_retry_prompt.txt"
      {
        cat "$BAKEOFF/$card/CODER_PROMPT.txt"
        printf '\n\nPREVIOUS ATTEMPT FAILED - fix this:\n\n'
        tail -120 "$BAKEOFF/runs/${tag}_attempt1/_gate_pytest.out" 2>/dev/null || true
        tail -80 "$BAKEOFF/runs/${tag}_attempt1/_coder.err" 2>/dev/null || true
      } > "$retry_prompt"
    else
      retry_prompt=""
    fi

    echo "== RUN $model card$idx $card attempt2 =="
    if ! run_one "$model" "$idx" "$card" "$sol" "$test" "2" "$retry_prompt"; then
      verify_frozen_manifest >/dev/null
      broken=1
    else
      verify_frozen_manifest >/dev/null
    fi
  done
done

echo "WROTE $OUT"
