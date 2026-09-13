#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
cd "${SCRIPT_DIR}/.."
agent="${1:-}"
case "$agent" in
  groove|groove_architect|groove-architect)
    service="groove-architect-agent"
    ;;
  sound|sound_designer|sound-designer)
    service="sound-designer-agent"
    ;;
  critic|cyber_critic|cyber-critic)
    service="cyber-critic-agent"
    ;;
  lyricist|lyricist_poet|lyricist-poet)
    service="lyricist-poet-agent"
    ;;
  topliner)
    service="topliner-agent"
    ;;
  harmony|harmonic_accompanist|harmonic-accompanist)
    service="harmonic-accompanist-agent"
    ;;
  *)
    echo "Usage: $0 groove|sound|critic|lyricist|topliner|harmony" >&2
    exit 2
    ;;
esac
shift || true
exec docker compose --profile agents run --rm "$service" "$@"
