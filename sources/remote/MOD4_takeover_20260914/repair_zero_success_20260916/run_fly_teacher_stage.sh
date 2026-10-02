#!/usr/bin/env bash
set -Eeuo pipefail
LABEL=${1:-fly_stage_a_v08}
INIT=${2:-/home/egde/rl_candidates/MOD4_takeover_20260914/logs/takeover_1536_20260915/2026-09-15_19-07-37_s2_mild_dr/model_599.pt}
ITERATIONS=${3:-80}
SPEED=${4:-0.80}
ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
CODE="$ROOT/env_scaling_20260915/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
ASSET="$ROOT/repair_1536_20260915/asset/robot_tireload12_mat3.usd"
OUT="$ROOT/repair_zero_success_20260916/fly_teacher/$LABEL"
mkdir -p "$OUT"
exec 9>/tmp/mod4_takeover_gpu0.lock
flock -n 9 || { echo "GPU0 is owned by another MOD4 job" >&2; exit 80; }
while IFS= read -r line; do
  payload=${line#export }
  name=${payload%%=*}
  value=${payload#*=}
  if [[ "$line" == export\ * && "$name" =~ ^RM_[A-Z0-9_]+$ && "$value" =~ ^[-A-Za-z0-9_.,:/+]+$ ]]; then
    export "$name=$value"
  fi
done < "$ROOT/takeover/common.env"
export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0
export TAKEOVER_NUM_ENVS=2048 RM_MOD4_USD="$ASSET"
export RM_SOLVER_POS=16 RM_SOLVER_VEL=4 RM_GYRO_STEPS_PER_ITER=48
export RM_DR_OFF=1 RM_ROUTE_CURRICULUM=0 RM_METRIC_PERIOD=5 RM_EPISODE_S=12
export RM_ROUTE_KINDS=fly_jump RM_ROUTE_WEIGHTS=fly_jump:1
export RM_FLY_SPEED_MIN="$SPEED" RM_FLY_SPEED_MAX="$SPEED" RM_FLY_TEACHER_VX="$SPEED"
export RM_TEACHER_BLEND_FLY=1 RM_TEACHER_BLEND_TUNNEL=0 RM_TEACHER_BLEND_JUMP=0
export RM_W_FLY_ACTION_REFERENCE_ERROR=-100 RM_W_FLY_APPROACH=8 RM_W_FLIGHT_PROG=8
export RM_W_LANDING_REC=4 RM_JUMP_LAUNCH_READY=1 RM_JUMP_LAUNCH_READY_W=4
export RM_ROUTE_PROGRESS_SCALE=100 RM_ROUTE_PROGRESS_W=4 RM_ROUTE_SUCCESS_W=80
export RM_W_TUNNEL_ACTION_REFERENCE_ERROR=0 RM_W_JUMP_ACTION_REFERENCE_ERROR=0
export RM_PARTIAL_WARMSTART=1 RM_KEEP_STD=0 RM_INIT_STD=0.05 RM_ENTROPY_COEF=0.0005
export RM_W_FLAT_ORIENT=-8 RM_W_ACTION_L2_LEG=-0.03 RM_W_ACTION_L2_WHEEL=-0.005
export RM_W_ACTION_RATE=-0.03 RM_W_ACTION_ACC=-0.008
"$PY" -m py_compile "$CODE/skills_isaac.py" "$CODE/mod4_env.py" "$CODE/mod4_task.py"
"$PY" "$CODE/train_mod4_ppo.py" --headless --num_envs 2048 \
  --additional_iterations "$ITERATIONS" --save_interval 10 --steps_per_env 48 \
  --learning_rate 0.00008 --run_name "$LABEL" --seed 20260938 \
  --log_root "$OUT/logs" --init_checkpoint "$INIT" --report "$OUT/train_report.json" \
  >"$OUT/train.log" 2>&1
RUN=$(find "$OUT/logs" -mindepth 1 -maxdepth 1 -type d -name "*_$LABEL" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
LATEST=$(find "$RUN" -maxdepth 1 -type f -name 'model_*.pt' -printf '%p\n' | sort -V | tail -1)
test -f "$LATEST"
sha256sum "$LATEST" "$RUN/run_manifest.json" >"$OUT/SHA256SUMS"
printf '%s\n' "$LATEST" >"$OUT/LATEST_CHECKPOINT.txt"
printf 'PASS_FLY_STAGE label=%s speed=%s final=%s\n' "$LABEL" "$SPEED" "$LATEST"
