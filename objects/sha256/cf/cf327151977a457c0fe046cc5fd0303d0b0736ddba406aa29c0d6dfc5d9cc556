#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
CODE="$ROOT/env_scaling_20260915/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
ASSET="$ROOT/repair_1536_20260915/asset/robot_tireload12_mat3.usd"
BASE="$ROOT/repair_zero_success_20260916/checkpoints/model_60_v3_pre_errorpenalty.pt"
OUT="$ROOT/repair_zero_success_20260916/tunnel_teacher_curriculum"
mkdir -p "$OUT"
test -f "$BASE"

exec 9>/tmp/mod4_takeover_gpu0.lock
flock -n 9 || { echo "GPU0 is owned by another MOD4 job" >&2; exit 80; }

# Do not execute the shared env file.  Import only inert RM_* scalar assignments whose names
# and values pass a strict allow-list; the stage-specific values below then override them.
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

# Same initial placement and action as the 4/4 deterministic CAD tunnel proof.
export RM_TUNNEL_GOAL_X=0.90 RM_TUNNEL_SPAWN_LEAD_M=0.14 RM_TUNNEL_SPAWN_SAFE_U=0.44
export RM_TUNNEL_PRECROUCH_LEAD_M=0.34 RM_TUNNEL_SPEED_MIN=0.18 RM_TUNNEL_SPEED_MAX=0.18
export RM_TUNNEL_TEACHER_VX=0.18 RM_TUNNEL_CROUCH_MOVE_GATE=0 RM_CROUCH_POSE_W=2.0
export RM_W_TUNNEL_APPROACH=5.0 RM_W_TUNNEL_CROUCH=4.0 RM_W_TUNNEL_TRAV=12.0
export RM_ROUTE_PROGRESS_SCALE=100 RM_ROUTE_PROGRESS_W=4 RM_ROUTE_SUCCESS_W=80

# The penalty is evaluated on PPO's original sample even while the plant receives a blend.
export RM_W_TUNNEL_ACTION_REFERENCE_ERROR=-20.0
export RM_W_JUMP_POSE_REFERENCE=0 RM_W_JUMP_POSE_ERROR=0
export RM_W_JUMP_ACTION_REFERENCE_ERROR=0 RM_W_JUMP_STATION_ERROR=0
export RM_W_FLY_ACTION_REFERENCE_ERROR=0 RM_W_FLY_APPROACH=0 RM_W_FLIGHT_PROG=0
export RM_W_FLAT_ORIENT=-6 RM_W_ACTION_L2_LEG=-0.02 RM_W_ACTION_L2_WHEEL=-0.005
export RM_PARTIAL_WARMSTART=1 RM_KEEP_STD=0 RM_INIT_STD=0.08 RM_ENTROPY_COEF=0.0005

latest_run() {
  find "$1" -mindepth 1 -maxdepth 1 -type d -name "*_$2" -printf '%T@ %p\n' \
    | sort -n | tail -1 | cut -d' ' -f2-
}

train_stage() {
  local label="$1" init="$2" blend="$3" iterations="$4" seed="$5"
  local stage="$OUT/$label"
  mkdir -p "$stage"
  export RM_TEACHER_BLEND_TUNNEL="$blend" RM_TEACHER_BLEND_JUMP=0 RM_TEACHER_BLEND_FLY=0
  export RM_W_ACTION_RATE=-0.01 RM_W_ACTION_ACC=-0.002
  "$PY" "$CODE/train_mod4_ppo.py" --headless --num_envs 2048 \
    --additional_iterations "$iterations" --save_interval 10 --steps_per_env 48 \
    --learning_rate 0.00008 --run_name "$label" --seed "$seed" \
    --log_root "$stage/logs" --init_checkpoint "$init" --report "$stage/train_report.json" \
    >"$stage/train.log" 2>&1
  local run
  run=$(latest_run "$stage/logs" "$label")
  local last=$((iterations - 1))
  test -f "$run/model_$last.pt"
  printf '%s\n' "$run/model_$last.pt"
}

eval_unassisted() {
  local label="$1" ckpt="$2" manifest="$3"
  export RM_TEACHER_BLEND_TUNNEL=0 RM_TEACHER_BLEND_JUMP=0 RM_TEACHER_BLEND_FLY=0
  "$PY" "$CODE/eval_episodes_mod4.py" --headless --checkpoint "$ckpt" \
    --manifest "$manifest" --num_envs 24 --steps 1250 --seed 20260929 \
    --training_route_scope --report "$OUT/${label}_unassisted.json" \
    >"$OUT/${label}_unassisted.log" 2>&1
}

# Assisted visitation -> half assistance -> fully deployable policy.
CKPT_A=$(train_stage tunnel_teacher_a "$BASE" 1.0 31 20260926)
RUN_A=$(dirname "$CKPT_A")
CKPT_B=$(train_stage tunnel_teacher_b "$CKPT_A" 0.5 31 20260927)
RUN_B=$(dirname "$CKPT_B")
CKPT_C=$(train_stage tunnel_teacher_c "$CKPT_B" 0.0 61 20260928)
RUN_C=$(dirname "$CKPT_C")
eval_unassisted tunnel_teacher_c "$CKPT_C" "$RUN_C/run_manifest.json"

sha256sum "$CKPT_A" "$CKPT_B" "$CKPT_C" >"$OUT/SHA256SUMS"
echo "PASS_TUNNEL_TEACHER_CURRICULUM final=$CKPT_C"
