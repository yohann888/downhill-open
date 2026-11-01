#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUTPUT_DIR="${DOWNHILL_SHOTS_DIR:-$HOME/downhill-shots}"
mkdir -p "$OUTPUT_DIR"
cd "$ROOT"

server_pid=""
if ! curl -fsS http://127.0.0.1:4301/tools/assets/rider-preview.html >/dev/null; then
  python3 -m http.server 4301 --bind 127.0.0.1 >/dev/null 2>&1 &
  server_pid=$!
  trap '[[ -z "$server_pid" ]] || kill "$server_pid" 2>/dev/null || true' EXIT
  for _ in $(seq 1 30); do
    if curl -fsS http://127.0.0.1:4301/tools/assets/rider-preview.html >/dev/null; then break; fi
    sleep 0.2
  done
fi

DOWNHILL_SHOTS_DIR="$OUTPUT_DIR" node tools/assets/capture-riders.mjs
