#!/bin/bash
# run_cell.sh <card_dir> <sol_file> <test_file> <model> [prompt_override]
# copies fixture -> fresh run dir, dispatches coder, runs green/scope/anti-stub gates, prints RESULT line.
BASE="$(cd "$(dirname "$0")" && pwd)"
VENV=$BASE/.venv/bin/python
CARD_DIR="$1"; SOL="$2"; TST="$3"; MODEL="$4"
PROMPT_OVERRIDE="${5:-}"
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
tag="$(basename "$CARD_DIR")__$(echo "$MODEL" | sed 's#[/:]#_#g')"
RUN="$BASE/runs/$tag"
rm -rf "$RUN"; mkdir -p "$RUN"
cp "$BASE/$CARD_DIR/$SOL" "$BASE/$CARD_DIR/$TST" "$BASE/$CARD_DIR/CARD.md" "$BASE/$CARD_DIR/CODER_PROMPT.txt" "$RUN/"
if [ -n "$PROMPT_OVERRIDE" ]; then
  cp "$PROMPT_OVERRIDE" "$RUN/CODER_PROMPT.txt"
fi
cat > "$RUN/_effective_prompt.txt" <<EOF
You are in an isolated benchmark run directory: $RUN

Use ONLY files in the current directory.
Allowed reads: CARD.md, CODER_PROMPT.txt, $TST, $SOL
Allowed write: $SOL
Do not read or write the frozen source card directory under $BASE/$CARD_DIR.
If CODER_PROMPT.txt contains absolute paths, treat them as stale runner metadata and use the current-directory files instead.
Verify with:
$VENV -m pytest -q

$(cat "$RUN/CODER_PROMPT.txt")
EOF
cd "$RUN" || exit 9
t0=$(date +%s)
run_with_timeout 300 opencode run --pure --dir "$RUN" -m "$MODEL" "$(cat _effective_prompt.txt)" > _coder.out 2> _coder.err
crc=$?; wall=$(( $(date +%s) - t0 ))
# --- GATES ---
"$VENV" -m pytest -q > _gate_pytest.out 2>&1; grc=$?
green=FAIL; [ $grc -eq 0 ] && green=PASS
if grep -nE 'NotImplementedError|TODO|FIXME|^[[:space:]]*\.\.\.[[:space:]]*$' "$SOL" >/dev/null 2>&1; then stub=FAIL; else stub=OK; fi
if diff -q "$BASE/$CARD_DIR/$TST" "$TST" >/dev/null 2>&1; then testmod=OK; else testmod=MODIFIED; fi
extra=$(ls -1 | grep -vE "^($SOL|$TST|CARD.md|CODER_PROMPT.txt|_effective_prompt.txt|_coder.out|_coder.err|_gate_pytest.out|__pycache__|\.hypothesis)$" | tr '\n' ',' | sed 's/,$//')
scope=OK; [ -n "$extra" ] && scope="NEWFILE($extra)"; [ "$testmod" = MODIFIED ] && scope="${scope};TEST_MODIFIED"
verdict=FAIL; [ "$green" = PASS ] && [ "$stub" = OK ] && [ "$scope" = OK ] && verdict=PASS
echo "RESULT|$tag|wall=${wall}s|crc=$crc|green=$green|stub=$stub|scope=$scope|VERDICT=$verdict"
