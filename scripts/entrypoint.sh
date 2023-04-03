#!/usr/bin/env bash
set -eu

function main() {
    cmd=()
    if [[ "${SCUTTLE_OFF:-false}" != "true" ]]; then
      cmd+=("scuttle")
    fi
    if [[ $# -eq 0 ]]; then
      cmd+=("python")
       cmd+=("/app/main.py")
    else
      cmd+=($@)
    fi
    echo "${cmd[*]}"
}
$(main "$@")
