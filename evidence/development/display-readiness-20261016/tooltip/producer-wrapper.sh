#!/usr/bin/env bash
set -euo pipefail
sleep 12
exec /baseline/consumer-build/InstalledConsumer "$@"
