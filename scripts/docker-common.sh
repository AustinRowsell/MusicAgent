#!/usr/bin/env bash

MUSICAGENT_LOCAL_CA_BUNDLE="certs/musicagent-local-ca-bundle.pem"

use_optional_local_ca_compose_override() {
  local message="${1:-Using optional local CA certificates from ./certs for Docker build and runtime TLS trust.}"
  local bundle_tmp="${MUSICAGENT_LOCAL_CA_BUNDLE}.tmp"

  if find certs -maxdepth 1 -type f \( -name "*.crt" -o -name "*.pem" \) ! -name "$(basename "${MUSICAGENT_LOCAL_CA_BUNDLE}")" -print -quit 2>/dev/null | grep -q .; then
    find certs -maxdepth 1 -type f \( -name "*.crt" -o -name "*.pem" \) ! -name "$(basename "${MUSICAGENT_LOCAL_CA_BUNDLE}")" -exec cat {} + > "${bundle_tmp}"
    mv "${bundle_tmp}" "${MUSICAGENT_LOCAL_CA_BUNDLE}"
    export COMPOSE_FILE="${COMPOSE_FILE:-compose.yaml:compose.local-certs.yaml}"
    echo "${message}"
  else
    rm -f "${bundle_tmp}"
    rm -f "${MUSICAGENT_LOCAL_CA_BUNDLE}"
  fi
}
