#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP_DIR="$ROOT_DIR/.agent-context"
STAMP_FILE="$STAMP_DIR/preflight.stamp"
ACK_TOKEN="I_READ_CONTEXT"
SCOPE="general"
ACK_VALUE=""
NO_PRINT=0

usage() {
  cat <<'USAGE'
Usage:
  pnpm agent:preflight -- [backend|frontend|content|docs] [--ack I_READ_CONTEXT] [--no-print]

Examples:
  pnpm agent:preflight -- backend
  pnpm agent:preflight -- content --ack I_READ_CONTEXT
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --)
      shift
      ;;
    backend|frontend|content|docs)
      SCOPE="$1"
      shift
      ;;
    --ack)
      if [[ $# -lt 2 ]]; then
        echo "Error: --ack requires a value."
        usage
        exit 2
      fi
      ACK_VALUE="$2"
      shift 2
      ;;
    --no-print)
      NO_PRINT=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: Unknown argument '$1'."
      usage
      exit 2
      ;;
  esac
done

SCOPED_FILE="AGENTS.md"
case "$SCOPE" in
  backend)
    SCOPED_FILE="src/backend/AGENTS.md"
    ;;
  frontend)
    SCOPED_FILE="src/app/AGENTS.md"
    ;;
  content)
    SCOPED_FILE="content/AGENTS.md"
    ;;
  docs)
    SCOPED_FILE="AGENTS.md"
    ;;
  general)
    SCOPED_FILE="AGENTS.md"
    ;;
esac

REQUIRED_FILES=(
  "docs/context/AGENT_BRIEF.md"
  "docs/context/CURRENT_STATE.md"
  "AGENTS.md"
)

if [[ "$SCOPED_FILE" != "AGENTS.md" ]]; then
  REQUIRED_FILES+=("$SCOPED_FILE")
fi

for rel_path in "${REQUIRED_FILES[@]}"; do
  abs_path="$ROOT_DIR/$rel_path"
  if [[ ! -f "$abs_path" ]]; then
    echo "Error: Required context file missing: $rel_path"
    exit 1
  fi
done

if [[ "$NO_PRINT" -eq 0 ]]; then
  for rel_path in "${REQUIRED_FILES[@]}"; do
    echo
    echo "===== $rel_path ====="
    sed -n '1,140p' "$ROOT_DIR/$rel_path"
  done
fi

if [[ -z "$ACK_VALUE" ]]; then
  if [[ -t 0 ]]; then
    echo
    printf "Type %s to confirm context pre-read: " "$ACK_TOKEN"
    read -r ACK_VALUE
  else
    echo
    echo "Non-interactive shell detected."
    echo "Run again with: --ack $ACK_TOKEN"
    exit 2
  fi
fi

if [[ "$ACK_VALUE" != "$ACK_TOKEN" ]]; then
  echo "Acknowledgment failed. Expected: $ACK_TOKEN"
  exit 1
fi

mkdir -p "$STAMP_DIR"
NOW_EPOCH="$(date +%s)"
NOW_UTC="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

cat > "$STAMP_FILE" <<EOF
timestamp=$NOW_EPOCH
time_utc=$NOW_UTC
scope=$SCOPE
scoped_file=$SCOPED_FILE
EOF

echo
echo "Preflight complete for scope: $SCOPE"
echo "Stamp written: .agent-context/preflight.stamp"
echo "Next: pnpm agent:scan -- <rg args>"
