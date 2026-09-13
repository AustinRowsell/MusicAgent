#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
cd "${SCRIPT_DIR}/.."
source "${SCRIPT_DIR}/docker-common.sh"
MODEL="${1:-${MUSICAGENT_MODEL:-llama3.1:8b}}"

use_optional_local_ca_compose_override "Using optional local CA certificates from ./certs for Docker build and Ollama TLS trust."
docker compose --profile local-llm up -d ollama
exec docker compose --profile local-llm exec ollama ollama pull "$MODEL"
