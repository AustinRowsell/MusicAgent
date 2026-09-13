#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
cd "${SCRIPT_DIR}/.."
MODEL="${1:-${MUSICAGENT_MODEL:-llama3.1:8b}}"
exec docker compose --profile local-llm run --rm ollama-pull "$MODEL"
