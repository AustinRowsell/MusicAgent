#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
cd "${SCRIPT_DIR}/.."
exec docker compose --profile local-llm run --rm musicagent-local-llm-cli create --output /app/outputs "$@"
