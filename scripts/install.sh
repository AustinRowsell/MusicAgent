#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
PROJECT_ROOT="${SCRIPT_DIR}/.."
INSTALL_MODE="local"
RUN_CHECKS="true"

usage() {
  cat <<'USAGE'
Usage: ./scripts/install.sh [--local|--user] [--skip-checks]

Bootstraps MusicAgent for local development and CLI usage.

Options:
  --local        Create/sync the project .venv only. This is the default.
  --user         Also install the musicagent CLI as a uv tool from this checkout.
  --skip-checks  Skip post-install smoke checks.
  -h, --help     Show this help.

Examples:
  ./scripts/install.sh
  ./scripts/install.sh --user
  ./scripts/install.sh --skip-checks
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --local)
      INSTALL_MODE="local"
      ;;
    --user)
      INSTALL_MODE="user"
      ;;
    --skip-checks)
      RUN_CHECKS="false"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

cd "$PROJECT_ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it from https://docs.astral.sh/uv/ and re-run this script." >&2
  exit 1
fi

PYTHON_REQUIREMENT=">=3.14,<3.15"

ensure_consistent_venv() {
  if [[ ! -x .venv/bin/python ]]; then
    return
  fi

  local venv_check
  if venv_check="$(.venv/bin/python - <<'PY'
from __future__ import annotations

import importlib.util
import pathlib
import sys
import sysconfig

version = f"{sys.version_info.major}.{sys.version_info.minor}"
purelib = pathlib.Path(sysconfig.get_path("purelib"))
supported = (sys.version_info.major, sys.version_info.minor) == (3, 14)
site_packages_matches = f"python{version}" in purelib.parts
pip_available = importlib.util.find_spec("pip") is not None

if supported and site_packages_matches and pip_available:
    raise SystemExit(0)

print(f"  interpreter: {sys.executable}")
print(f"  version: {version}")
print(f"  site-packages: {purelib}")
print(f"  pip available: {pip_available}")
print(f"  supported by project: {supported}")
print(f"  site-packages matches interpreter: {site_packages_matches}")
raise SystemExit(1)
PY
  )"; then
    return
  fi

  echo "Existing .venv is inconsistent or unsupported for MusicAgent:" >&2
  echo "$venv_check" >&2
  echo "Removing project-local .venv so uv can recreate it with Python ${PYTHON_REQUIREMENT}." >&2
  rm -rf .venv
}

ensure_consistent_venv

if [[ ! -x .venv/bin/python ]] || ! .venv/bin/python -m pip --version >/dev/null 2>&1; then
  echo "Creating seeded project environment with Python ${PYTHON_REQUIREMENT}..."
  if ! uv venv --seed --python "$PYTHON_REQUIREMENT" .venv; then
    echo "uv venv failed. Retrying with system TLS certificates..." >&2
    uv venv --clear --seed --python "$PYTHON_REQUIREMENT" .venv --system-certs
  fi
fi

echo "Syncing project environment..."
if ! uv sync --dev --python "$PYTHON_REQUIREMENT"; then
  echo "uv sync failed. Retrying with system TLS certificates..." >&2
  uv sync --dev --python "$PYTHON_REQUIREMENT" --system-certs
fi

echo "Ensuring helper scripts are executable..."
chmod +x scripts/*.sh

if [[ "$INSTALL_MODE" == "user" ]]; then
  echo "Installing musicagent CLI as a uv tool from this checkout..."
  uv tool install --editable . --force
fi

if [[ "$RUN_CHECKS" == "true" ]]; then
  echo "Running CLI smoke check..."
  uv run musicagent crews

  echo "Running helper script syntax check..."
  bash -n scripts/*.sh
fi

cat <<'DONE'

MusicAgent installation complete.

Try:
  ./scripts/local-cli.sh crews
  ./scripts/local-cli.sh create --name demo --prompt "warm acoustic song" --crew acoustic --output outputs --dry-run --overwrite
  ./scripts/local-web.sh

Docker helpers are also available when Docker is running:
  ./scripts/docker-cli.sh crews
  ./scripts/docker-web.sh
DONE
