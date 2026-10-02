#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 4 ]]; then
  echo "usage: $0 LABEL INIT_CHECKPOINT ITERATIONS SEED" >&2
  exit 2
fi
LABEL=$1
INIT=$2
ITERATIONS=$3
SEED=$4
[[ "$LABEL" =~ ^flat_[A-Za-z0-9_]+$ ]]
[[ "$ITERATIONS" =~ ^[1-9][0-9]*$ ]]
[[ "$SEED" =~ ^[1-9][0-9]*$ ]]

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
export TAKEOVER_NUM_ENVS=12000 RM_MOD4_USD="$ASSET"
export RM_SOLVER_POS=16 RM_SOLVER_VEL=4 RM_GYRO_STEPS_PER_ITER=48
export RM_DR_OFF=0 RM_DR_PROFILE=mild RM_ROUTE_CURRICULUM=0
export RM_METRIC_PERIOD=20 RM_EPISODE_S="${RM_RUN_EPISODE_S:-12}"
export RM_ROUTE_KINDS=run RM_ROUTE_WEIGHTS=run:1
export RM_RUN_SPEED_MIN=0.30 RM_RUN_SPEED_MAX=1.20 RM_RUN_STAND_FRACTION=0
export RM_RUN_BRAKE_GATE="${RM_RUN_BRAKE_GATE:-0}"
export RM_RUN_BRAKE_DIST_M="${RM_RUN_BRAKE_DIST_M:-0.90}"
export RM_RUN_STOP_SPEED_M_S="${RM_RUN_STOP_SPEED_M_S:-0.30}"
export RM_RUN_STOP_TILT_DEG="${RM_RUN_STOP_TILT_DEG:-8.0}"
export RM_RUN_STOP_ANG_XY_RAD_S="${RM_RUN_STOP_ANG_XY_RAD_S:-1.50}"

# The v6 deterministic audit measured 2.115 m/s RMS against a 0.3--1.2 m/s command and
# 1.543 m/s velocity error.  The Gaussian tracker is nearly flat that far away, so this
# continuation combines it with a non-saturating run-only error term.  Lower route bonuses
# remove the incentive to sprint through the 3.5 m route before tracking/stability can matter.
export RM_TRACK_SIGMA=0.50
export RM_W_TRACK_LIN="${RM_RUN_TRACK_WEIGHT:-4.0}"
export RM_W_RUN_VEL_ERROR="${RM_RUN_ERROR_WEIGHT:--1.0}"
export RM_W_RUN_AIRBORNE="${RM_RUN_AIR_WEIGHT:-0.0}"
export RM_ROUTE_PROGRESS_SCALE=100 RM_ROUTE_PROGRESS_W="${RM_RUN_PROGRESS_WEIGHT:-0.10}"
export RM_ROUTE_SUCCESS_W="${RM_RUN_SUCCESS_WEIGHT:-8.0}"
export RM_W_FLAT_ORIENT="${RM_RUN_ORIENT_WEIGHT:--20}"
export RM_W_ANG_VEL_XY="${RM_RUN_ANG_WEIGHT:--0.80}"
export RM_W_WHEEL_CONTACT="${RM_RUN_CONTACT_WEIGHT:-4.0}"
export RM_W_UNWANTED_AIR=-2.0 RM_W_GUIDE_CONTACT=-0.75
export RM_W_ACTION_RATE=-0.25 RM_W_ACTION_ACC=-0.080
export RM_W_ACTION_L2_LEG=-0.05 RM_W_ACTION_L2_WHEEL=-0.015
export RM_W_TORQUES=-0.00005 RM_W_LEG_SYMMETRY=-0.7
export RM_W_STAND_QUIET=0 RM_W_STAND_MOTION=0
export RM_PARTIAL_WARMSTART=1 RM_KEEP_STD=0 RM_INIT_STD=0.07 RM_ENTROPY_COEF=0.0002

export RM_GATE_RUN_ACTION_DELTA_RMS=0.45 RM_GATE_RUN_ACTION_D2_RMS=0.80
export RM_GATE_RUN_TILT_RMS_DEG=8.0 RM_GATE_RUN_ANG_XY_RMS=1.50
export RM_GATE_RUN_VEL_ERROR_RMS=0.75 RM_GATE_RUN_WHEEL_CONTACT=0.90
export RM_GATE_RUN_GUIDE_CONTACT=0.10

# Mild competition-domain randomization.  Full DR remains gated on nominal and mild passing.
export RM_STIFFNESS_MIN=0.95 RM_STIFFNESS_MAX=1.05
export RM_DAMPING_MIN=0.95 RM_DAMPING_MAX=1.05
export RM_EFFORT_LEG_MIN=0.95 RM_EFFORT_LEG_MAX=1.05
export RM_EFFORT_WHEEL_MIN=0.95 RM_EFFORT_WHEEL_MAX=1.05
export RM_ARMATURE_MIN=0.85 RM_ARMATURE_MAX=1.20 RM_ENCODER_BIAS=0.008
export RM_OBS_DELAY_MIN_LAG=0 RM_OBS_DELAY_MAX_LAG=1
export RM_ACTION_DELAY_MIN_LAG=0 RM_ACTION_DELAY_MAX_LAG=0
export RM_ACTION_DELAY_MS_MIN=0 RM_ACTION_DELAY_MS_MAX=2
export RM_SHAPE_FRICTION_MIN=0.80 RM_SHAPE_FRICTION_MAX=1.20
export RM_CHASSIS_MASS_ADD_MIN=-0.5 RM_CHASSIS_MASS_ADD_MAX=1.0
export RM_CHASSIS_INERTIA_MIN=0.90 RM_CHASSIS_INERTIA_MAX=1.10
export RM_LIMB_MASS_MIN=0.95 RM_LIMB_MASS_MAX=1.05
export RM_LIMB_INERTIA_MIN=0.90 RM_LIMB_INERTIA_MAX=1.10
export RM_WHEEL_MASS_MIN=0.95 RM_WHEEL_MASS_MAX=1.05
export RM_WHEEL_INERTIA_MIN=0.90 RM_WHEEL_INERTIA_MAX=1.10
export RM_COM_X=0.02 RM_COM_Y=0.01 RM_COM_Z=0.01
export RM_GAS_STIFFNESS_MIN=0.90 RM_GAS_STIFFNESS_MAX=1.10
export RM_GAS_DAMPING_MIN=0.90 RM_GAS_DAMPING_MAX=1.10
export RM_PUSH_VX=0.15 RM_PUSH_VY=0.10 RM_PUSH_PITCH=0.15
export RM_PUSH_FORCE_N=4 RM_PUSH_TORQUE_NM=0.3

"$PY" -m py_compile "$CODE/route_isaac.py" "$CODE/skills_isaac.py" \
  "$CODE/mod4_env.py" "$CODE/mod4_task.py" "$CODE/eval_episodes_mod4.py"
"$PY" -m pytest -q "$CODE/test_takeover_contracts.py" >"$OUT/static_tests.log" 2>&1
"$PY" "$CODE/train_mod4_ppo.py" --headless --num_envs 12000 \
  --additional_iterations "$ITERATIONS" --save_interval 5 --steps_per_env 48 \
  --learning_rate 0.00004 --run_name "$LABEL" --seed "$SEED" \
  --log_root "$OUT/logs" --init_checkpoint "$INIT" --report "$OUT/train_report.json" \
  >"$OUT/train.log" 2>&1

RUN=$(find "$OUT/logs" -mindepth 1 -maxdepth 1 -type d -name "*_$LABEL" \
  -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
LATEST=$(find "$RUN" -maxdepth 1 -type f -name 'model_*.pt' -printf '%p\n' | sort -V | tail -1)
test -f "$LATEST"
sha256sum "$LATEST" "$RUN/run_manifest.json" >"$OUT/SHA256SUMS"
printf '%s\n' "$LATEST" >"$OUT/LATEST_CHECKPOINT.txt"
printf 'PASS_RUN_STABILITY label=%s iterations=%s final=%s\n' \
  "$LABEL" "$ITERATIONS" "$LATEST"
