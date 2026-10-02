#!/usr/bin/env bash
# Start one MOD4 arena training stage on the target 4090 (audit P2 pipeline).
#
#   bash scripts/start_mod4_stage.sh <stage> [init_checkpoint] [iterations]
#
# Every stage fixes its own route filter, so the spawn points, the observation mode bits, the
# reward terms and the evaluator's per-route buckets all agree (audit items 1/2/9).  Env vars
# are exported BEFORE the setsid block so the process tree inherits them -- the earlier
# hand-written one-liners lost them whenever a second launch was chained with `&`.
#
#   stage    routes                                            default envs
#   run      run                                               1024
#   jump     jump_in_place                                     512
#   terrain  ramp_up,ramp_down,step_up,step_down,rough_cross   512
#   tunnel   tunnel_cross                                      512
#   fly      fly_jump                                          512
#   spin     slope_spin                                        512
#   mix      (no filter -> all 15 delivered routes)            1024
#
# Override the size with NUM_ENVS=<n>.  Logs land in logs/isaac_mod4/stage_<stage>.log and the
# run directory carries run_manifest.json with the code hashes of that launch.
set -euo pipefail

STAGE="${1:?usage: start_mod4_stage.sh <run|jump|terrain|tunnel|fly|spin|mix> [ckpt] [iters]}"
INIT="${2:-}"
ITERS="${3:-1500}"

case "$STAGE" in
  run)     ROUTES="run";                                        DEF_ENVS=1024 ;;
  jump)    ROUTES="jump_in_place";                               DEF_ENVS=512 ;;
  terrain) ROUTES="ramp_up,ramp_down,step_up,step_down,rough_cross"; DEF_ENVS=512 ;;
  tunnel)  ROUTES="tunnel_cross";                                DEF_ENVS=512 ;;
  fly)     ROUTES="fly_jump";                                    DEF_ENVS=512 ;;
  spin)    ROUTES="slope_spin";                                  DEF_ENVS=512 ;;
  mix)     ROUTES="";                                            DEF_ENVS=1024 ;;
  *) echo "unknown stage: $STAGE" >&2; exit 2 ;;
esac

cd /home/egde/fangzhen_linux
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
LOG=logs/isaac_mod4/stage_${STAGE}.log
ARGS=(isaac/mod4/train_mod4_ppo.py --headless
      --num_envs "${NUM_ENVS:-$DEF_ENVS}" --additional_iterations "$ITERS"
      --run_name "mod4_p2_stage_${STAGE}")
if [ -n "$INIT" ]; then ARGS+=(--init_checkpoint "$INIT"); fi

export OMNI_KIT_ACCEPT_EULA=YES
export RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF="${RM_DR_OFF:-1}"
export RM_ROUTE_KINDS="$ROUTES"

echo "starting stage=$STAGE routes=${ROUTES:-all} envs=${NUM_ENVS:-$DEF_ENVS} iters=$ITERS"
[ -n "$INIT" ] && echo "  warm start: $INIT"
setsid nohup "$PY" "${ARGS[@]}" > "$LOG" 2>&1 < /dev/null &
echo "  pid=$!  log=$LOG"
