#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP_FILE="$ROOT_DIR/.agent-context/preflight.stamp"
MAX_AGE_MINUTES="${AGENT_PREFLIGHT_MAX_AGE_MINUTES:-240}"

usage() {
  cat <<'USAGE'
Usage:
  pnpm agent:scan -- <rg args>

Examples:
  pnpm agent:scan -- "orchestrator" src/backend/app -n
  pnpm agent:scan -- "lead capture" src/app src/components -n
USAGE
}

if ! command -v rg >/dev/null 2>&1; then
  echo "Error: rg is required but not found."
  exit 1
fi

if [[ ! -f "$STAMP_FILE" ]]; then
  echo "Error: Missing preflight stamp."
  echo "Run first: pnpm agent:preflight -- <scope>"
  exit 1
fi

STAMP_TS="$(awk -F= '/^timestamp=/{print $2}' "$STAMP_FILE" | tr -d '[:space:]')"
STAMP_SCOPE="$(awk -F= '/^scope=/{print $2}' "$STAMP_FILE" | tr -d '[:space:]')"

if [[ -z "$STAMP_TS" ]] || ! [[ "$STAMP_TS" =~ ^[0-9]+$ ]]; then
  echo "Error: Invalid preflight stamp format."
  echo "Run again: pnpm agent:preflight -- <scope>"
  exit 1
fi

NOW_TS="$(date +%s)"
AGE_MINUTES="$(( (NOW_TS - STAMP_TS) / 60 ))"

if (( AGE_MINUTES > MAX_AGE_MINUTES )); then
  echo "Error: Preflight stamp is stale (${AGE_MINUTES}m old, limit ${MAX_AGE_MINUTES}m)."
  echo "Run again: pnpm agent:preflight -- <scope>"
  exit 1
fi

if [[ $# -eq 0 ]]; then
  usage
  exit 2
fi

if [[ "${1:-}" == "--" ]]; then
  shift
fi

if [[ $# -eq 0 ]]; then
  usage
  exit 2
fi

echo "Preflight OK (scope=${STAMP_SCOPE}, age=${AGE_MINUTES}m). Running rg..."
rg "$@"
