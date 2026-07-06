#!/usr/bin/env bash
# Sync boilerplate from gear-stack into AI Workspace (mirrored monorepo layout).
#
# Source of truth for what to copy/skip: docs/IMPLEMENTATION_KICKOFF.md (Krok 0).
# Use for initial bootstrap or periodic cherry-pick of upstream gear-stack changes.
#
# Usage:
#   ./scripts/rsync-from-gear-stack.sh              # dry-run (default)
#   ./scripts/rsync-from-gear-stack.sh --apply      # write changes
#   GEAR_STACK_SRC=/path/to/gear-stack ./scripts/rsync-from-gear-stack.sh --apply

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE="${GEAR_STACK_SRC:-${REPO_ROOT}/../gear-stack}"
DEST="${REPO_ROOT}"

DRY_RUN=1
if [[ "${1:-}" == "--apply" ]]; then
  DRY_RUN=0
elif [[ -n "${1:-}" ]]; then
  echo "Usage: $0 [--apply]" >&2
  exit 1
fi

if [[ ! -d "${SOURCE}" ]]; then
  echo "gear-stack source not found: ${SOURCE}" >&2
  echo "Set GEAR_STACK_SRC to override." >&2
  exit 1
fi

RSYNC_FLAGS=(
  -av
  --delete
  --exclude='.git/'
  --exclude='node_modules/'
  --exclude='dist/'
  --exclude='.env'
  --exclude='backups/'
  --exclude='.eslintcache'
  # AI Workspace–owned (never overwrite from gear-stack)
  --exclude='docs/'
  --exclude='README.md'
  --exclude='LICENSE'
  --exclude='.cursorrules'
  --exclude='scripts/rsync-from-gear-stack.sh'
  # gear-stack narrative / meta (not part of boilerplate)
  --exclude='CLAUDE.md'
  --exclude='BUGS.md'
  --exclude='CHANGELOG.md'
  --exclude='DEPLOYMENT.md'
  --exclude='FEATURES.md'
  --exclude='MIGRATION_*.md'
  --exclude='V2_*.md'
  --exclude='screenshot.png'
)

if [[ "${DRY_RUN}" -eq 1 ]]; then
  RSYNC_FLAGS+=(--dry-run)
  echo "Dry-run: no files will be modified. Pass --apply to sync."
else
  echo "Applying rsync from ${SOURCE} -> ${DEST}"
fi

echo "Source: ${SOURCE}/"
echo "Dest:   ${DEST}/"
echo

rsync "${RSYNC_FLAGS[@]}" "${SOURCE}/" "${DEST}/"

if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo
  echo "Review the list above, then run: $0 --apply"
fi
