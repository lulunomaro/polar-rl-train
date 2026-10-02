#!/usr/bin/env bash
# Wait for a checkpoint to exist, then run the acceptance gate on it.
#
#   bash migration/linux/run_acceptance_when_ready.sh <checkpoint> [num_envs] [max_wait_s]
#
# Used to grade an in-flight run at a save boundary without polling from outside: the wait
# costs nothing and the gate starts the moment the file is complete.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CKPT="${1:?usage: run_acceptance_when_ready.sh <checkpoint> [num_envs] [max_wait_s]}"
ENVS="${2:-128}"
WAIT="${3:-3600}"
waited=0
while [[ ! -f "$CKPT" ]]; do
  if (( waited >= WAIT )); then echo "TIMEOUT after ${waited}s waiting for $CKPT"; exit 3; fi
  sleep 10; waited=$((waited + 10))
done
echo "checkpoint appeared after ${waited}s: $CKPT"
exec bash "$ROOT/migration/linux/run_acceptance_later.sh" "$CKPT" "$ENVS"
