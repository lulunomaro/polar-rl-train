#!/usr/bin/env bash
# Dedicated detached supervisor for the 10-hour all-terrain run with the real tunnel.
#
# Production lineage as of 2026-09-09 23:07: rm2025_later_tunnel250_10h.
# The tunnel opening is the user-measured 250 mm high x 800 mm wide x 300 mm deep.
# The generic supervise_rm2025_later.sh defaults are also pinned to this experiment, but
# this wrapper adds a single-instance lock so a heartbeat cannot start a second guardian
# (and cannot fall back to an older proxy-only lineage).
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

export EXPERIMENT="${EXPERIMENT:-rm2025_later_tunnel250_v2_10h}"
export TARGET_ITER="${TARGET_ITER:-2400}"
export NUM_ENVS="${NUM_ENVS:-8192}"
export INTERVAL="${INTERVAL:-60}"

LOCK="${RM2025_TUNNEL_10H_LOCK:-/tmp/rm2025_allterrain_tunnel_10h_supervisor.lock}"
exec flock -n "$LOCK" bash "$ROOT/migration/linux/supervise_rm2025_later.sh"
