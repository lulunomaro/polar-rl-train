#!/usr/bin/env bash
# Dedicated detached supervisor for the 10-hour all-terrain production run.
#
# The generic supervise_rm2025_later.sh defaults to rm2025_later_cc_v2 / 16000 iters.
# That default is a rollback lineage; using it to guard the 10-hour run would relaunch
# the wrong experiment after a crash.  This wrapper pins the production experiment and
# holds a lock so a heartbeat or a human cannot start a second supervisor.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

export EXPERIMENT="${EXPERIMENT:-rm2025_later_allterrain_10h}"
export TARGET_ITER="${TARGET_ITER:-2400}"
export NUM_ENVS="${NUM_ENVS:-8192}"
export INTERVAL="${INTERVAL:-60}"

LOCK="${RM2025_10H_LOCK:-/tmp/rm2025_allterrain_10h_supervisor.lock}"
exec flock -n "$LOCK" bash "$ROOT/migration/linux/supervise_rm2025_later.sh"
