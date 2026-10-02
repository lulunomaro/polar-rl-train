#!/usr/bin/env bash
set -Eeuo pipefail
if [[ $# -lt 5 || $# -gt 7 ]]; then
  echo "usage: $0 LABEL INIT_CHECKPOINT PROFILE ITERATIONS SEED [SPEED_MAX] [NUM_ENVS]" >&2
  exit 2
fi
LABEL=$1
INIT=$2
PROFILE=$3
ITERATIONS=$4
SEED=$5
SPEED_MAX=${6:-1.8}
NUM_ENVS=${7:-12000}
[[ "$LABEL" =~ ^flat_[A-Za-z0-9_]+$ ]]
[[ "$PROFILE" == mild || "$PROFILE" == full ]]
[[ "$ITERATIONS" =~ ^[1-9][0-9]*$ ]]
[[ "$SEED" =~ ^[1-9][0-9]*$ ]]
[[ "$NUM_ENVS" =~ ^[1-9][0-9]*$ ]]
ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
CODE="$ROOT/env_scaling_20260915/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
ASSET="$ROOT/repair_1536_20260915/asset/robot_tireload12_mat3.usd"
OUT="$ROOT/repair_zero_success_20260916/flat_dr/$LABEL"
test -f "$INIT"
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
export TAKEOVER_NUM_ENVS="$NUM_ENVS" RM_MOD4_USD="$ASSET"
export RM_SOLVER_POS=16 RM_SOLVER_VEL=4 RM_GYRO_STEPS_PER_ITER=48
export RM_DR_OFF=0 RM_ROUTE_CURRICULUM=0 RM_METRIC_PERIOD=5 RM_EPISODE_S=12
export RM_ROUTE_KINDS=run RM_ROUTE_WEIGHTS=run:1
export RM_RUN_SPEED_MIN=0.30 RM_RUN_SPEED_MAX="$SPEED_MAX"
export RM_TEACHER_BLEND_TUNNEL=0 RM_TEACHER_BLEND_FLY=0 RM_TEACHER_BLEND_JUMP=0
export RM_W_TUNNEL_ACTION_REFERENCE_ERROR=0 RM_W_FLY_ACTION_REFERENCE_ERROR=0
export RM_W_JUMP_ACTION_REFERENCE_ERROR=0
export RM_ROUTE_PROGRESS_SCALE=100 RM_ROUTE_PROGRESS_W=3 RM_ROUTE_SUCCESS_W=30
export RM_PARTIAL_WARMSTART=1 RM_KEEP_STD=0 RM_INIT_STD=0.10 RM_ENTROPY_COEF=0.0005
export RM_W_FLAT_ORIENT=-8 RM_W_ANG_VEL_XY=-0.20 RM_W_TORQUES=-0.00005
export RM_W_ACTION_L2_LEG=-0.05 RM_W_ACTION_L2_WHEEL=-0.015
export RM_W_ACTION_RATE=-0.14 RM_W_ACTION_ACC=-0.040 RM_W_LEG_SYMMETRY=-0.7
if [[ "$PROFILE" == mild ]]; then
  export RM_STIFFNESS_MIN=0.95 RM_STIFFNESS_MAX=1.05 RM_DAMPING_MIN=0.95 RM_DAMPING_MAX=1.05
  export RM_EFFORT_LEG_MIN=0.95 RM_EFFORT_LEG_MAX=1.05 RM_EFFORT_WHEEL_MIN=0.95 RM_EFFORT_WHEEL_MAX=1.05
  export RM_ARMATURE_MIN=0.85 RM_ARMATURE_MAX=1.20 RM_ENCODER_BIAS=0.008
  export RM_OBS_DELAY_MIN_LAG=0 RM_OBS_DELAY_MAX_LAG=1 RM_ACTION_DELAY_MIN_LAG=0 RM_ACTION_DELAY_MAX_LAG=0
  export RM_ACTION_DELAY_MS_MIN=0 RM_ACTION_DELAY_MS_MAX=2
  export RM_SHAPE_FRICTION_MIN=0.80 RM_SHAPE_FRICTION_MAX=1.20
  export RM_CHASSIS_MASS_ADD_MIN=-0.5 RM_CHASSIS_MASS_ADD_MAX=1.0
  export RM_CHASSIS_INERTIA_MIN=0.90 RM_CHASSIS_INERTIA_MAX=1.10
  export RM_LIMB_MASS_MIN=0.95 RM_LIMB_MASS_MAX=1.05 RM_LIMB_INERTIA_MIN=0.90 RM_LIMB_INERTIA_MAX=1.10
  export RM_WHEEL_MASS_MIN=0.95 RM_WHEEL_MASS_MAX=1.05 RM_WHEEL_INERTIA_MIN=0.90 RM_WHEEL_INERTIA_MAX=1.10
  export RM_COM_X=0.02 RM_COM_Y=0.01 RM_COM_Z=0.01
  export RM_GAS_STIFFNESS_MIN=0.90 RM_GAS_STIFFNESS_MAX=1.10 RM_GAS_DAMPING_MIN=0.90 RM_GAS_DAMPING_MAX=1.10
  export RM_PUSH_VX=0.15 RM_PUSH_VY=0.10 RM_PUSH_PITCH=0.15 RM_PUSH_FORCE_N=4 RM_PUSH_TORQUE_NM=0.3
else
  export RM_STIFFNESS_MIN=0.90 RM_STIFFNESS_MAX=1.10 RM_DAMPING_MIN=0.90 RM_DAMPING_MAX=1.10
  export RM_EFFORT_LEG_MIN=0.90 RM_EFFORT_LEG_MAX=1.10 RM_EFFORT_WHEEL_MIN=0.90 RM_EFFORT_WHEEL_MAX=1.10
  export RM_ARMATURE_MIN=0.70 RM_ARMATURE_MAX=1.40 RM_ENCODER_BIAS=0.015
  export RM_OBS_DELAY_MIN_LAG=0 RM_OBS_DELAY_MAX_LAG=2 RM_ACTION_DELAY_MIN_LAG=0 RM_ACTION_DELAY_MAX_LAG=0
  export RM_ACTION_DELAY_MS_MIN=0 RM_ACTION_DELAY_MS_MAX=5
  export RM_SHAPE_FRICTION_MIN=0.65 RM_SHAPE_FRICTION_MAX=1.35
  export RM_CHASSIS_MASS_ADD_MIN=-1.0 RM_CHASSIS_MASS_ADD_MAX=2.0
  export RM_CHASSIS_INERTIA_MIN=0.80 RM_CHASSIS_INERTIA_MAX=1.20
  export RM_LIMB_MASS_MIN=0.90 RM_LIMB_MASS_MAX=1.10 RM_LIMB_INERTIA_MIN=0.75 RM_LIMB_INERTIA_MAX=1.25
  export RM_WHEEL_MASS_MIN=0.90 RM_WHEEL_MASS_MAX=1.10 RM_WHEEL_INERTIA_MIN=0.80 RM_WHEEL_INERTIA_MAX=1.20
  export RM_COM_X=0.04 RM_COM_Y=0.02 RM_COM_Z=0.02
  export RM_GAS_STIFFNESS_MIN=0.80 RM_GAS_STIFFNESS_MAX=1.20 RM_GAS_DAMPING_MIN=0.75 RM_GAS_DAMPING_MAX=1.25
  export RM_PUSH_VX=0.40 RM_PUSH_VY=0.30 RM_PUSH_PITCH=0.40 RM_PUSH_FORCE_N=10 RM_PUSH_TORQUE_NM=1.0
fi
"$PY" -m py_compile "$CODE/route_isaac.py" "$CODE/skills_isaac.py" "$CODE/mod4_env.py" "$CODE/mod4_task.py"
"$PY" "$CODE/train_mod4_ppo.py" --headless --num_envs "$NUM_ENVS" \
  --additional_iterations "$ITERATIONS" --save_interval 10 --steps_per_env 48 \
  --learning_rate 0.000065 --run_name "$LABEL" --seed "$SEED" \
  --log_root "$OUT/logs" --init_checkpoint "$INIT" --report "$OUT/train_report.json" \
  >"$OUT/train.log" 2>&1
RUN=$(find "$OUT/logs" -mindepth 1 -maxdepth 1 -type d -name "*_$LABEL" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
LATEST=$(find "$RUN" -maxdepth 1 -type f -name 'model_*.pt' -printf '%p\n' | sort -V | tail -1)
test -f "$LATEST"
sha256sum "$LATEST" "$RUN/run_manifest.json" >"$OUT/SHA256SUMS"
printf '%s\n' "$LATEST" >"$OUT/LATEST_CHECKPOINT.txt"
printf 'PASS_FLAT_DR_STAGE label=%s profile=%s speed_max=%s envs=%s final=%s\n' \
  "$LABEL" "$PROFILE" "$SPEED_MAX" "$NUM_ENVS" "$LATEST"
