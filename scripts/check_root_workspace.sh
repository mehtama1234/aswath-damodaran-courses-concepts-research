#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "[1/3] Compiling root workspace validation and build scripts"
python3 -m py_compile \
  "${SCRIPT_DIR}/applied_brief_metadata.py" \
  "${SCRIPT_DIR}/validate_applied_analysis.py" \
  "${SCRIPT_DIR}/validate_applied_evidence.py" \
  "${SCRIPT_DIR}/validate_root_workspace.py" \
  "${SCRIPT_DIR}/build_applied_analysis_index_page.py" \
  "${SCRIPT_DIR}/build_root_applied_analysis_pages.py" \
  "${SCRIPT_DIR}/build_applied_evidence_page.py" \
  "${SCRIPT_DIR}/build_root_workspace_artifacts.py"

echo "[2/3] Rebuilding root workspace artifacts"
python3 "${SCRIPT_DIR}/build_root_workspace_artifacts.py" --workspace-root "${WORKSPACE_ROOT}"

echo "[3/3] Running standalone root workspace validator"
python3 "${SCRIPT_DIR}/validate_root_workspace.py" --workspace-root "${WORKSPACE_ROOT}"

echo "Root workspace check passed."
