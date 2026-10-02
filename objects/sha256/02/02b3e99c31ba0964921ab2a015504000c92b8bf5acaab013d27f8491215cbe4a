#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
CODE="$ROOT/env_scaling_20260915/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
USD="$ROOT/repair_1536_20260915/asset/robot_tireload12_mat3.usd"
CKPT="$ROOT/logs/takeover_1536_20260915/2026-09-15_19-07-37_s2_mild_dr/model_599.pt"
NUM_ENVS="${1:?usage: $0 NUM_ENVS [ITERATIONS] [STEPS_PER_ENV] [SOLVER_POS] [SOLVER_VEL]}"
ITERS="${2:-16}"
STEPS_PER_ENV="${3:-48}"
SOLVER_POS="${4:-32}"
SOLVER_VEL="${5:-8}"
OUT="$ROOT/material_fix_20260915/probe_${NUM_ENVS}_spe${STEPS_PER_ENV}_sol${SOLVER_POS}_${SOLVER_VEL}"
mkdir -p "$OUT"

exec 9>/tmp/mod4_takeover_gpu0.lock
flock -n 9 || { echo "GPU0 is owned by another MOD4 job" >&2; exit 80; }
if pgrep -af 'train_mod4_ppo.py|eval_episodes_mod4.py|export_final_policy.py' \
  | grep -v "$PPID" | grep -q .; then
  echo "refusing to share GPU with another Isaac job" >&2
  exit 81
fi

set -a
source "$ROOT/takeover/common.env"
set +a
export CUDA_VISIBLE_DEVICES=0
export TAKEOVER_NUM_ENVS="$NUM_ENVS"
export RM_MOD4_USD="$USD"
export RM_GUIDE_FRICTION=0.02
export RM_TIRE_ADD_MM=0
export RM_DR_OFF=0
export RM_ROUTE_CURRICULUM=0
export RM_GYRO_STEPS_PER_ITER="$STEPS_PER_ENV"
export RM_SOLVER_POS="$SOLVER_POS"
export RM_SOLVER_VEL="$SOLVER_VEL"
export RM_METRIC_PERIOD=4
export RM_ROUTE_KINDS='run,slope_spin,fly_jump,jump_in_place,tunnel_cross'
export RM_ROUTE_WEIGHTS='run:2,slope_spin:3,fly_jump:3,jump_in_place:3,tunnel_cross:4'
export RM_TUNNEL_GOAL_X=1.45
export RM_TUNNEL_SPAWN_LEAD_M=0.15
export RM_ROUGH_SPEED_MAX=0.8
export RM_JUMP_LO=0.05 RM_JUMP_HI=0.05 RM_JUMP_HI_MAX=0.05
export RM_GYRO_START=4.0 RM_GYRO_TARGET=5.0 RM_GYRO_EVERY=80
export RM_ENTROPY_COEF=0.0015 RM_INIT_STD=0.16
export RM_W_ACTION_RATE=-0.08 RM_W_ACTION_ACC=-0.015

: > "$OUT/gpu.csv"
(
  while true; do
    nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used,power.draw \
      --format=csv,noheader,nounits >> "$OUT/gpu.csv" 2>/dev/null || true
    sleep 1
  done
) & MON=$!
cleanup () { kill "$MON" 2>/dev/null || true; }
trap cleanup EXIT

timeout --signal=INT --kill-after=90 1800s "$PY" "$CODE/train_mod4_ppo.py" \
  --num_envs "$NUM_ENVS" --additional_iterations "$ITERS" --save_interval 9999 \
  --steps_per_env "$STEPS_PER_ENV" --learning_rate 0.000075 \
  --run_name "mat3_probe_${NUM_ENVS}" --seed 20260915 \
  --log_root "$OUT/logs" --init_checkpoint "$CKPT" \
  --report "$OUT/runtime_report.json" > "$OUT/train.log" 2>&1

if grep -Eqi '64K materials|CUDA out of memory|nonfinite|NaN detected|Traceback \(most recent call last\)' "$OUT/train.log"; then
  echo "fatal signature in ${NUM_ENVS}-environment probe" >&2
  grep -nEi '64K materials|CUDA out of memory|nonfinite|NaN detected|Traceback \(most recent call last\)' "$OUT/train.log" | tail -30 >&2
  exit 92
fi
grep -q 'Learning iteration' "$OUT/train.log"
echo "PASS_MATERIAL_SCALING num_envs=$NUM_ENVS iterations=$ITERS steps_per_env=$STEPS_PER_ENV solver=$SOLVER_POS/$SOLVER_VEL"
