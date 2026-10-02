#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -lt 5 || $# -gt 7 ]]; then
  echo "usage: $0 LABEL INIT_CHECKPOINT BLEND ITERATIONS SEED [INIT_STD] [ACTION_ERROR_WEIGHT]" >&2
  exit 2
fi
LABEL=$1
INIT=$2
BLEND=$3
ITERATIONS=$4
SEED=$5
INIT_STD=${6:-0.03}
ACTION_ERROR_WEIGHT=${7:--100.0}
[[ "$LABEL" =~ ^tunnel_[A-Za-z0-9_]+$ ]]
[[ "$BLEND" =~ ^(0(\.[0-9]+)?|1(\.0+)?)$ ]]
[[ "$ITERATIONS" =~ ^[1-9][0-9]*$ ]]
[[ "$SEED" =~ ^[1-9][0-9]*$ ]]
[[ "$INIT_STD" =~ ^0\.[0-9]+$ ]]
[[ "$ACTION_ERROR_WEIGHT" =~ ^-[0-9]+(\.[0-9]+)?$ ]]

ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
CODE="$ROOT/env_scaling_20260915/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
ASSET="$ROOT/repair_1536_20260915/asset/robot_tireload12_mat3.usd"
OUT="$ROOT/repair_zero_success_20260916/tunnel_teacher_fine/$LABEL"
test -f "$INIT"
mkdir -p "$OUT"

exec 9>/tmp/mod4_takeover_gpu0.lock
flock -n 9 || { echo "GPU0 is owned by another MOD4 job" >&2; exit 80; }

# Strictly parse inert RM_* scalar assignments.  Never execute the shared env file.
while IFS= read -r line; do
  payload=${line#export }
  name=${payload%%=*}
  value=${payload#*=}
  if [[ "$line" == export\ * && "$name" =~ ^RM_[A-Z0-9_]+$ &&
        "$value" =~ ^[-A-Za-z0-9_.,:/+]+$ ]]; then
    export "$name=$value"
  fi
done < "$ROOT/takeover/common.env"

export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0
export TAKEOVER_NUM_ENVS=2048 RM_MOD4_USD="$ASSET"
export RM_SOLVER_POS=16 RM_SOLVER_VEL=4 RM_GYRO_STEPS_PER_ITER=48
export RM_DR_OFF=1 RM_ROUTE_CURRICULUM=0 RM_METRIC_PERIOD=5 RM_EPISODE_S=12
export RM_ROUTE_KINDS=tunnel_cross RM_ROUTE_WEIGHTS=tunnel_cross:1
export RM_TUNNEL_GOAL_X=0.90 RM_TUNNEL_SPAWN_LEAD_M=0.14 RM_TUNNEL_SPAWN_SAFE_U=0.44
export RM_TUNNEL_PRECROUCH_LEAD_M=0.34 RM_TUNNEL_SPEED_MIN=0.18 RM_TUNNEL_SPEED_MAX=0.18
export RM_TUNNEL_TEACHER_VX=0.18 RM_TUNNEL_CROUCH_MOVE_GATE=0 RM_CROUCH_POSE_W=2.0
export RM_W_TUNNEL_APPROACH=5.0 RM_W_TUNNEL_CROUCH=4.0 RM_W_TUNNEL_TRAV=12.0
export RM_ROUTE_PROGRESS_SCALE=100 RM_ROUTE_PROGRESS_W=4 RM_ROUTE_SUCCESS_W=80
export RM_W_TUNNEL_ACTION_REFERENCE_ERROR="$ACTION_ERROR_WEIGHT"
export RM_W_JUMP_POSE_REFERENCE=0 RM_W_JUMP_POSE_ERROR=0
export RM_W_JUMP_ACTION_REFERENCE_ERROR=0 RM_W_JUMP_STATION_ERROR=0
export RM_W_FLY_ACTION_REFERENCE_ERROR=0 RM_W_FLY_APPROACH=0 RM_W_FLIGHT_PROG=0
export RM_W_FLAT_ORIENT=-6 RM_W_ACTION_L2_LEG=-0.02 RM_W_ACTION_L2_WHEEL=-0.005
export RM_W_ACTION_RATE=-0.01 RM_W_ACTION_ACC=-0.002
export RM_PARTIAL_WARMSTART=1 RM_KEEP_STD=0 RM_INIT_STD="$INIT_STD" RM_ENTROPY_COEF=0.0002
export RM_TEACHER_BLEND_TUNNEL="$BLEND" RM_TEACHER_BLEND_JUMP=0 RM_TEACHER_BLEND_FLY=0

"$PY" -m py_compile "$CODE/skills_isaac.py" "$CODE/mod4_env.py" "$CODE/mod4_task.py"
"$PY" "$CODE/train_mod4_ppo.py" --headless --num_envs 2048 \
  --additional_iterations "$ITERATIONS" --save_interval 10 --steps_per_env 48 \
  --learning_rate 0.00008 --run_name "$LABEL" --seed "$SEED" \
  --log_root "$OUT/logs" --init_checkpoint "$INIT" --report "$OUT/train_report.json" \
  >"$OUT/train.log" 2>&1

RUN=$(find "$OUT/logs" -mindepth 1 -maxdepth 1 -type d -name "*_$LABEL" -printf '%T@ %p\n' \
  | sort -n | tail -1 | cut -d' ' -f2-)
LAST=$((ITERATIONS - 1))
test -f "$RUN/model_$LAST.pt"
sha256sum "$RUN/model_$LAST.pt" "$RUN/run_manifest.json" >"$OUT/SHA256SUMS"
echo "PASS_TUNNEL_STAGE label=$LABEL blend=$BLEND final=$RUN/model_$LAST.pt"
