#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
cd "${SCRIPT_DIR}/.."
source "${SCRIPT_DIR}/docker-common.sh"
use_optional_local_ca_compose_override
exec docker compose --profile app run --rm musicagent-cli musicagent "$@"
