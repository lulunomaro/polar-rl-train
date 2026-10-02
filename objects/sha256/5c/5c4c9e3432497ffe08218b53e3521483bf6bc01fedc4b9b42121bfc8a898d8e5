#!/usr/bin/env bash
# Detached entry point for the v2 production training supervisor.
#
# The 2026-09-09 v1 run proved the delivered later plant needs its own reward scale
# (joint_acc was 99% of the episode reward; see docs/REWARD_SCALE_RM2025_LATER.md) and a
# smaller initial action std.  This wrapper pins the v2 settings in one place so a manual
# or automated relaunch cannot silently fall back to the v1 defaults.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export EXPERIMENT="${EXPERIMENT:-rm2025_later_cc_v2}"
export TARGET_ITER="${TARGET_ITER:-16000}"
export NUM_ENVS="${NUM_ENVS:-8192}"
export INTERVAL="${INTERVAL:-60}"

exec bash "$ROOT/migration/linux/supervise_rm2025_later.sh"
