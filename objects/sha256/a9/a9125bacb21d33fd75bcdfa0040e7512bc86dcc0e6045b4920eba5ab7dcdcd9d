#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
CODE="$ROOT/env_scaling_20260915/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
ASSET="$ROOT/repair_1536_20260915/asset/robot_tireload12_mat3.usd"
CKPT="$ROOT/repair_zero_success_20260916/checkpoints/model_60_v3_pre_errorpenalty.pt"
OUT="$ROOT/repair_zero_success_20260916/probe_v4"
mkdir -p "$OUT"
test -f "$CKPT"

exec 9>/tmp/mod4_takeover_gpu0.lock
flock -n 9 || { echo "GPU0 is owned by another MOD4 job" >&2; exit 80; }

set -a
source "$ROOT/takeover/common.env"
set +a
export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0
export TAKEOVER_NUM_ENVS=2048 RM_MOD4_USD="$ASSET"
export RM_SOLVER_POS=16 RM_SOLVER_VEL=4 RM_GYRO_STEPS_PER_ITER=48
export RM_DR_OFF=1 RM_ROUTE_CURRICULUM=0 RM_METRIC_PERIOD=10 RM_EPISODE_S=12
export RM_ROUTE_KINDS='fly_jump,jump_in_place,tunnel_cross'
export RM_ROUTE_WEIGHTS='fly_jump:3,jump_in_place:3,tunnel_cross:3'

# Fly bootstrap starts on the flat before the measured ramp base (x ~= -1.39 m) and uses a
# reachable command.  The normalized wheel-action teacher remains active only until launch.
export RM_FLY_SPAWN_LEAD_M=1.00 RM_FLY_SPEED_MIN=0.80 RM_FLY_SPEED_MAX=0.80
export RM_FLY_TEACHER_VX=0.80 RM_W_FLY_ACTION_REFERENCE_ERROR=-1.5
export RM_W_FLY_APPROACH=6.0 RM_W_FLIGHT_PROG=6.0

# The deterministic PI probe passed 4/4 at 0.18 m/s.  Use that exact low pose and wheel speed as
# a reward reference; policy actions still pass through the normal actuator/constraint plant.
export RM_TUNNEL_GOAL_X=0.90 RM_TUNNEL_SPAWN_LEAD_M=0.14 RM_TUNNEL_SPAWN_SAFE_U=0.44
export RM_TUNNEL_PRECROUCH_LEAD_M=0.34 RM_TUNNEL_SPEED_MIN=0.18 RM_TUNNEL_SPEED_MAX=0.18
export RM_TUNNEL_TEACHER_VX=0.18 RM_W_TUNNEL_ACTION_REFERENCE_ERROR=-2.0
export RM_TUNNEL_CROUCH_MOVE_GATE=0 RM_CROUCH_POSE_W=4.0
export RM_W_TUNNEL_APPROACH=5.0 RM_W_TUNNEL_CROUCH=4.0 RM_W_TUNNEL_TRAV=10.0
export RM_ROUTE_PROGRESS_SCALE=100 RM_ROUTE_PROGRESS_W=3 RM_ROUTE_SUCCESS_W=50

# Slow load, rapid release.  Negative errors have a unique optimum in both halves, unlike the
# retired positive reference that paid the policy for ignoring the crouch half.
export RM_JUMP_REFERENCE=1 RM_JUMP_LOAD_S=0.90 RM_JUMP_PUSH_S=0.25 RM_JUMP_CYCLE_S=1.50
export RM_JUMP_CROUCH_HEIGHT=0.21 RM_JUMP_STAND_HEIGHT=0.34
export RM_W_JUMP_POSE_REFERENCE=0 RM_W_JUMP_POSE_ERROR=-6.0
export RM_W_JUMP_ACTION_REFERENCE_ERROR=-2.0 RM_W_JUMP_STATION_ERROR=-2.0
export RM_JUMP_LO=0.025 RM_JUMP_HI=0.025 RM_JUMP_HI_MAX=0.025
export RM_JUMP_PUSH_VZ_MIN=0.10 RM_JUMP_PUSH_VZ=0.45 RM_W_JUMP_XY_DRIFT=-10
export RM_W_LINE_Z=6.0

export RM_PARTIAL_WARMSTART=1 RM_KEEP_STD=0 RM_INIT_STD=0.12 RM_ENTROPY_COEF=0.0008
export RM_W_ACTION_RATE=-0.05 RM_W_ACTION_ACC=-0.008 RM_W_FLAT_ORIENT=-6.0

"$PY" -m py_compile "$CODE/route_isaac.py" "$CODE/skills_isaac.py" "$CODE/mod4_task.py"
"$PY" -m pytest -q "$CODE/test_takeover_contracts.py" >"$OUT/static_tests.log" 2>&1

"$PY" "$CODE/train_mod4_ppo.py" --headless --num_envs 2048 \
  --additional_iterations 101 --save_interval 10 --steps_per_env 48 \
  --learning_rate 0.00008 --run_name zero_repair_probe_v4 --seed 20260922 \
  --log_root "$OUT/logs" --init_checkpoint "$CKPT" \
  --report "$OUT/train_report.json" >"$OUT/train.log" 2>&1

RUN=$(find "$OUT/logs" -mindepth 1 -maxdepth 1 -type d -name '*_zero_repair_probe_v4' \
  -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
test -f "$RUN/model_100.pt"
"$PY" "$CODE/eval_episodes_mod4.py" --headless --checkpoint "$RUN/model_100.pt" \
  --manifest "$RUN/run_manifest.json" --num_envs 36 --steps 1250 --seed 20260923 \
  --training_route_scope --report "$OUT/eval_training_scope.json" \
  >"$OUT/eval_training_scope.log" 2>&1

sha256sum "$RUN/model_100.pt" "$RUN/run_manifest.json" >"$OUT/SHA256SUMS"
echo "PASS_ZERO_REPAIR_PROBE_V4 run=$RUN"
