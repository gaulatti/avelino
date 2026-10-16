#!/usr/bin/env bash
set -euo pipefail
date -u +%FT%TZ > producer-start.txt
sleep 65
date -u +%FT%TZ > producer-exec.txt
exec /baseline/consumer-build/InstalledConsumer "$@"
