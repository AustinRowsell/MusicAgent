#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
cd "${SCRIPT_DIR}/.."
HOST="${MUSICAGENT_WEB_HOST:-127.0.0.1}"
PORT="${MUSICAGENT_WEB_PORT:-8000}"
exec uv run uvicorn musicagent.web.app:app --host "$HOST" --port "$PORT"
