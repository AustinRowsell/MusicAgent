#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
cd "${SCRIPT_DIR}/.."
source "${SCRIPT_DIR}/docker-common.sh"
use_optional_local_ca_compose_override
crew="${1:-}"
case "$crew" in
  electronic|electronic_alt_pop|electronic-alt-pop)
    service="electronic-alt-pop-crew"
    ;;
  acoustic|singer_songwriter_acoustic|singer-songwriter-acoustic)
    service="singer-songwriter-acoustic-crew"
    ;;
  *)
    echo "Usage: $0 electronic|acoustic" >&2
    exit 2
    ;;
esac
shift || true
exec docker compose --profile crews run --rm "$service" "$@"
