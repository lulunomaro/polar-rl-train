#!/usr/bin/env bash
# Special-heavy curriculum with rehearsal (goal 2026-09-12 §4).
#
# Runs ONE training job at a time; after each phase it evaluates the new checkpoint (all routes,
# fixed seed) and continues from that checkpoint.  Every route that already works keeps a
# rehearsal slot, so learning a hard special cannot silently erase it.
#
#   ./run_special_phases.sh <checkpoint> [envs]
#
# Phases: tunnel (short goal -> full goal) -> rough -> spin -> fly -> jump.
set -uo pipefail
cd "$(dirname "$0")/../.."
LOG=logs/isaac_mod4/special_phases_$(date +%Y%m%d_%H%M%S).log
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
CKPT=${1:?usage: run_special_phases.sh <checkpoint> [envs]}
ENVS=${2:-512}

REHEARSAL="run:2,ramp_up:2,ramp_down:1,step_up:2,step_down:1,rough_cross:2,tunnel_cross:2,slope_spin:2,jump_in_place:1,fly_jump:2"

log() { echo "[phases] $*" | tee -a "$LOG"; }

latest_checkpoint() {
  local run_dir last
  run_dir=$(ls -dt logs/isaac_mod4/*_mod4_fixed_mixed/ 2>/dev/null | head -1)
  last=$(ls -t "$run_dir" 2>/dev/null | grep "^model_" | head -1)
  CKPT="${run_dir}${last}"
}

wait_for_training() {
  local label=$1 stable=0
  while true; do
    if pgrep -f "train_mod4_ppo.py --headless" >/dev/null; then stable=0; else
      stable=$((stable + 1)); [ "$stable" -ge 3 ] && break
    fi
    if tail -60 "$TRAIN_LOG" 2>/dev/null | grep -q "Traceback"; then
      log "$label: Traceback detected -- aborting chain"; exit 1
    fi
    sleep 30
  done
  latest_checkpoint
  log "$label done -> $CKPT"
}

phase() {
  local label=$1 weights=$2 iters=$3 goalx=$4
  log "=== phase $label iters=$iters tunnel_goal_x=$goalx"
  export RM_ROUTE_WEIGHTS="$weights"
  export RM_TUNNEL_GOAL_X="$goalx"
  TRAIN_LOG=logs/isaac_mod4/phase_${label}_$(date +%H%M%S).log
  FORCE=1 bash migration/linux/start_mod4_stage_fixedplant.sh mixed "$CKPT" "$ENVS" "$iters" \
    >"$TRAIN_LOG" 2>&1 || true
  grep -h "^\[launch\]" "$TRAIN_LOG" | tail -2 | tee -a "$LOG"
  sleep 20
  pgrep -f "train_mod4_ppo.py --headless" >/dev/null || {
    log "$label: training did not start -- aborting"; exit 1; }
  wait_for_training "$label"
  local OUT=docs/acceptance_phase_${label}
  mkdir -p "$OUT"
  OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 \
    $PY isaac/mod4/eval_terrain_mod4.py --headless --checkpoint "$CKPT" --num_envs 64 \
    --steps 2200 --seed 20260912 --report "$OUT/eval.json" >>"$LOG" 2>&1 || true
  $PY - "$OUT/eval.json" <<'PY' | tee -a "$LOG"
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception as exc:
    print("[phases] eval missing:", exc); raise SystemExit(0)
for k, v in sorted(d["route_kinds"].items()):
    print("[phases]   %-14s complete %.3f  progress %7.1f  spin %6.1f"
          % (k, v["complete_rate"], v["progress_sum"], v.get("spin_deg", 0.0)))
PY
}

phase tunnel_short "tunnel_cross:6,$REHEARSAL" 800 1.60
phase tunnel_full  "tunnel_cross:6,$REHEARSAL" 800 2.30
phase rough        "rough_cross:6,$REHEARSAL"  600 2.30
phase spin         "slope_spin:7,$REHEARSAL"   600 2.30
phase fly          "fly_jump:6,$REHEARSAL"     600 2.30
phase jump         "jump_in_place:5,$REHEARSAL" 600 2.30
log "all phases finished; final checkpoint = $CKPT"
