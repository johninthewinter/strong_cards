#!/usr/bin/env bash
set -euo pipefail

ROOT="${PIPELINE_ROOT:?Set PIPELINE_ROOT to the private pipeline-upgrade directory}"
BAKEOFF="$ROOT/bakeoff"
OUT="$ROOT/23-gemma-card10-only-results.jsonl"
CLAUDE_OLLAMA="${CLAUDE_OLLAMA:-claude-ollama}"
CODER_TIMEOUT="${CODER_TIMEOUT:-900}"
PYTEST_TIMEOUT="${PYTEST_TIMEOUT:-180}"

cd "$BAKEOFF"

if [ "$#" -gt 0 ]; then
  models=("$@")
else
  models=(
    "gemma4:31b-coding-mtp-bf16"
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

run_with_timeout() {
  if [ -n "$TIMEOUT_BIN" ]; then
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

with open(sys.argv[1], "a") as f:
    f.write(json.dumps(json.loads(os.environ["SWEEP_ROW_JSON"])) + "\n")
PY
}

json_row() {
  SWEEP_ROW_JSON="$(python3 - <<'PY'
import json
import os

row = {
    "runner": "claude-ollama",
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
}

warm_model() {
  local model="$1"
  echo "== WARM $model =="
  set +e
  warm_output="$(run_with_timeout 180 ollama run "$model" "Reply READY only." 2>&1)"
  warm_rc=$?
  set -e
  if [ "$warm_rc" -ne 0 ]; then
    SWEEP_ROW_JSON="$(MODEL="$model" RC="$warm_rc" TAIL="$(printf '%s' "$warm_output" | tail -c 4000)" python3 - <<'PY'
import json
import os

verdict = "TIMEOUT" if os.environ["RC"] == "124" else "UNAVAILABLE"
print(json.dumps({
    "runner": "claude-ollama",
    "model": os.environ["MODEL"],
    "warm": "FAIL",
    "warm_return_code": int(os.environ["RC"]),
    "verdict": verdict,
    "stdout_stderr_tail": os.environ["TAIL"],
}))
PY
)"
    export SWEEP_ROW_JSON
    append_json
    return 1
  fi
}

run_one() {
  local model="$1" idx="$2" card="$3" sol="$4" test="$5" attempt="$6"
  local prompt_override="${7:-}"
  local tag run started ended output coder_rc wall grc green stub testmod extra scope verdict result gate_tail output_tail prompt_override_used timeout_hit
  tag="$(basename "$card")__claude_ollama_$(printf '%s' "$model" | sed 's#[/:]#_#g')"
  run="$BAKEOFF/runs/$tag"
  rm -rf "$run"
  mkdir -p "$run"
  cp "$BAKEOFF/$card/$sol" "$BAKEOFF/$card/$test" "$BAKEOFF/$card/CARD.md" "$BAKEOFF/$card/CODER_PROMPT.txt" "$run/"
  if [ -n "$prompt_override" ]; then
    cp "$prompt_override" "$run/CODER_PROMPT.txt"
  fi
  {
    printf 'You are in isolated benchmark run directory: %s\n' "$run"
    printf 'Use ONLY files in the current directory.\n'
    printf 'Allowed reads: CARD.md, CODER_PROMPT.txt, %s, %s\n' "$sol" "$test"
    printf 'Allowed write: %s\n' "$sol"
    printf 'Do not read or write the frozen source card directory.\n'
    printf 'If CODER_PROMPT.txt contains absolute paths, treat them as stale and use the current directory files instead.\n'
    printf 'Verify with: %s -m pytest -q\n\n' "$BAKEOFF/.venv/bin/python"
    cat "$run/CODER_PROMPT.txt"
  } > "$run/_effective_prompt.txt"

  started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  t0=$(date +%s)
  set +e
  output="$(
    cd "$run" && \
      OLLAMA_MODEL="$model" \
      CLAUDE_CODE_SUBAGENT_MODEL="${CLAUDE_CODE_SUBAGENT_MODEL:-qwen3:1.7b}" \
      run_with_timeout "$CODER_TIMEOUT" "$CLAUDE_OLLAMA" -p \
        --permission-mode bypassPermissions \
        --tools "Read,Edit,Bash" \
        --output-format json \
        --no-session-persistence \
        --append-system-prompt "You are running under a local Ollama backend. Do not use Agent, Task, subagents, background agents, or fanout. Edit only the requested file in the current directory. Do not read parent directories." \
        "$(cat _effective_prompt.txt)" 2>&1
  )"
  coder_rc=$?
  set -e
  wall=$(( $(date +%s) - t0 ))
  ended="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '%s\n' "$output" > "$run/_coder.out"

  cd "$run" || exit 9
  set +e
  run_with_timeout "$PYTEST_TIMEOUT" "$BAKEOFF/.venv/bin/python" -m pytest -q > _gate_pytest.out 2>&1
  grc=$?
  set -e
  cd "$BAKEOFF" || exit 9

  green=FAIL
  [ "$grc" -eq 0 ] && green=PASS
  if grep -nE 'NotImplementedError|TODO|FIXME|^[[:space:]]*\.\.\.[[:space:]]*$' "$run/$sol" >/dev/null 2>&1; then
    stub=FAIL
  else
    stub=OK
  fi
  if diff -q "$BAKEOFF/$card/$test" "$run/$test" >/dev/null 2>&1; then
    testmod=OK
  else
    testmod=MODIFIED
  fi
  extra="$(cd "$run" && { ls -1 | grep -vE "^($sol|$test|CARD.md|CODER_PROMPT.txt|_effective_prompt.txt|_coder.out|_gate_pytest.out|__pycache__|\.hypothesis)$" || true; } | tr '\n' ',' | sed 's/,$//')"
  scope=OK
  [ -n "$extra" ] && scope="NEWFILE($extra)"
  [ "$testmod" = MODIFIED ] && scope="${scope};TEST_MODIFIED"
  verdict=FAIL
  [ "$green" = PASS ] && [ "$stub" = OK ] && [ "$scope" = OK ] && verdict=PASS
  timeout_hit=false
  if [ "$coder_rc" = "124" ] || [ "$grc" = "124" ]; then
    verdict=TIMEOUT
    timeout_hit=true
  fi
  result="RESULT|$tag|wall=${wall}s|crc=$coder_rc|green=$green|stub=$stub|scope=$scope|VERDICT=$verdict"
  gate_tail="$(tail -80 "$run/_gate_pytest.out" 2>/dev/null || true)"
  output_tail="$(printf '%s' "$output" | tail -c 4000)"
  prompt_override_used=false
  [ -n "$prompt_override" ] && prompt_override_used=true

  export SWEEP_MODEL="$model"
  export SWEEP_IDX="$idx"
  export SWEEP_CARD="$card"
  export SWEEP_SOL="$sol"
  export SWEEP_TEST="$test"
  export SWEEP_ATTEMPT="$attempt"
  export SWEEP_STARTED="$started"
  export SWEEP_ENDED="$ended"
  export SWEEP_RC="0"
  export SWEEP_CODER_RC="$coder_rc"
  export SWEEP_RESULT="$result"
  export SWEEP_VERDICT="$verdict"
  export SWEEP_RUN_DIR="$run"
  export SWEEP_OUTPUT_TAIL="$output_tail"
  export SWEEP_GATE_TAIL="$gate_tail"
  export SWEEP_PROMPT_OVERRIDE_USED="$prompt_override_used"
  export SWEEP_TIMEOUT_HIT="$timeout_hit"
  json_row
  printf '%s\n' "$result"
  [ "$verdict" = "PASS" ]
}

verify_frozen_manifest
: > "$OUT"

for model in "${models[@]}"; do
  # Enforce the one-large-local-model rule for this local queue.
  ollama stop qwen3.6:35b-a3b-mtp-q8_0 >/dev/null 2>&1 || true
  ollama stop gemma4:31b-coding-mtp-bf16 >/dev/null 2>&1 || true

  if ! warm_model "$model"; then
    continue
  fi

  broken=0
  for spec in "${cards[@]}"; do
    IFS='|' read -r idx card sol test <<< "$spec"
    if [ "$idx" != "10" ]; then
      continue
    fi
    if [ "$broken" -eq 1 ] && [ "$idx" != "10" ]; then
      SWEEP_ROW_JSON="$(MODEL="$model" IDX="$idx" CARD="$card" python3 - <<'PY'
import json
import os

print(json.dumps({
    "runner": "claude-ollama",
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

    tag="$(basename "$card")__claude_ollama_$(printf '%s' "$model" | sed 's#[/:]#_#g')"
    retry_prompt="$BAKEOFF/runs/${tag}_retry_prompt.txt"
    rm -rf "$BAKEOFF/runs/${tag}_attempt1"
    cp -R "$BAKEOFF/runs/$tag" "$BAKEOFF/runs/${tag}_attempt1"
    {
      cat "$BAKEOFF/$card/CODER_PROMPT.txt"
      printf '\n\nPREVIOUS ATTEMPT FAILED - fix this:\n\n'
      tail -120 "$BAKEOFF/runs/${tag}_attempt1/_gate_pytest.out" 2>/dev/null || true
      tail -80 "$BAKEOFF/runs/${tag}_attempt1/_coder.out" 2>/dev/null || true
    } > "$retry_prompt"

    echo "== RUN $model card$idx $card attempt2 =="
    if ! run_one "$model" "$idx" "$card" "$sol" "$test" "2" "$retry_prompt"; then
      verify_frozen_manifest >/dev/null
      broken=1
    else
      verify_frozen_manifest >/dev/null
    fi
  done

  ollama stop "$model" >/dev/null 2>&1 || true
done

echo "WROTE $OUT"
