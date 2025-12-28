#!/usr/bin/env bash
set -e

# Usage:
#   ./init_ai_workflow.sh
#   ./init_ai_workflow.sh path/to/project-root
#
# By default, uses current directory as project root.

ROOT_DIR="${1:-.}"

echo "Initializing AI workflow structure in: $ROOT_DIR"

# Core folders
mkdir -p "$ROOT_DIR/.github/prompts"
mkdir -p "$ROOT_DIR/docs/psd"
mkdir -p "$ROOT_DIR/docs/plans"
mkdir -p "$ROOT_DIR/docs/references"
mkdir -p "$ROOT_DIR/docs/decisions"
mkdir -p "$ROOT_DIR/src/backend"
mkdir -p "$ROOT_DIR/src/frontend"
mkdir -p "$ROOT_DIR/src/shared"
mkdir -p "$ROOT_DIR/src/tests"
mkdir -p "$ROOT_DIR/plans"

# Git keepers (optional but useful)
touch "$ROOT_DIR/.github/.gitkeep"
touch "$ROOT_DIR/.github/prompts/.gitkeep"
touch "$ROOT_DIR/docs/.gitkeep"
touch "$ROOT_DIR/docs/psd/.gitkeep"
touch "$ROOT_DIR/docs/plans/.gitkeep"
touch "$ROOT_DIR/docs/references/.gitkeep"
touch "$ROOT_DIR/docs/decisions/.gitkeep"
touch "$ROOT_DIR/src/.gitkeep"
touch "$ROOT_DIR/src/backend/.gitkeep"
touch "$ROOT_DIR/src/frontend/.gitkeep"
touch "$ROOT_DIR/src/shared/.gitkeep"
touch "$ROOT_DIR/src/tests/.gitkeep"
touch "$ROOT_DIR/plans/.gitkeep"

# Optional Copilot instructions scaffold
COPILOT_INSTR="$ROOT_DIR/.github/copilot-instructions.md"
if [ ! -f "$COPILOT_INSTR" ]; then
  cat > "$COPILOT_INSTR" << 'EOF'
# Copilot Instructions (Global)

- Use .github/prompts/*.prompt.md as primary workflows.
- Prefer Plan mode over Agent/autonomous modes.
- Default coding style:
  - Keep functions small and focused.
  - Use clear, descriptive naming.
  - Add minimal but useful comments where intent is non-obvious.
- When in doubt, consult docs in /docs before inventing behavior.
EOF
  echo "Created $COPILOT_INSTR"
fi

# Optional AI workflow README scaffold
AI_README="$ROOT_DIR/AI_WORKFLOW_README.md"
if [ ! -f "$AI_README" ]; then
  cat > "$AI_README" << 'EOF'
# AI Workflow (Stub)

See AI_WORKFLOW.md for the full documentation once you add it.
EOF
  echo "Created stub $AI_README (replace with full AI_WORKFLOW.md)."
fi

echo "Done."
echo
echo "Next steps:"
echo "1) Copy your *.prompt.md files into .github/prompts/"
echo "2) Add the full AI workflow README as AI_WORKFLOW.md at the project root."
