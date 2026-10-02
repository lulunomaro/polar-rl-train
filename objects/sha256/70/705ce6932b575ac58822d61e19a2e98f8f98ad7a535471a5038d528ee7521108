#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
CODE="$ROOT/env_scaling_20260915/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
ASSET="$ROOT/repair_1536_20260915/asset/robot_tireload12_mat3.usd"
BASE="$ROOT/logs/takeover_12000_mat3_spe48_sol16_4_20260915_v4/2026-09-15_23-36-10_s2b_specialist_recovery"
CKPT="$BASE/model_50.pt"
OUT="$ROOT/repair_zero_success_20260916/probe_v2"
mkdir -p "$OUT"

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

# Safe sparse-task curricula.  Tunnel reset remains in front of the roof; the full robot
# footprint cannot make spawn_footprint_floor mistake the roof for its support surface.
export RM_FLY_SPAWN_LEAD_M=1.50 RM_FLY_SPEED_MIN=1.80 RM_FLY_SPEED_MAX=2.20
export RM_TUNNEL_GOAL_X=0.90 RM_TUNNEL_SPAWN_LEAD_M=0.00
export RM_TUNNEL_PRECROUCH_LEAD_M=0.22 RM_TUNNEL_SPEED_MIN=0.60 RM_TUNNEL_SPEED_MAX=0.60
export RM_ROUTE_PROGRESS_SCALE=100 RM_ROUTE_PROGRESS_W=3 RM_ROUTE_SUCCESS_W=40
export RM_W_TUNNEL_APPROACH=4.0 RM_W_TUNNEL_CROUCH=2.0 RM_W_TUNNEL_TRAV=8.0

# Observable crouch/release reference, repeated until a real take-off is discovered.
export RM_JUMP_REFERENCE=1 RM_JUMP_LOAD_S=0.45 RM_JUMP_PUSH_S=0.30 RM_JUMP_CYCLE_S=1.20
export RM_JUMP_CROUCH_HEIGHT=0.22 RM_JUMP_STAND_HEIGHT=0.34
export RM_JUMP_LO=0.03 RM_JUMP_HI=0.03 RM_JUMP_HI_MAX=0.03
export RM_JUMP_PUSH_VZ_MIN=0.10 RM_JUMP_PUSH_VZ=0.45 RM_W_JUMP_XY_DRIFT=-10
export RM_W_LINE_Z=5.0 RM_W_FLIGHT_PROG=5.0

export RM_PARTIAL_WARMSTART=1 RM_KEEP_STD=0 RM_INIT_STD=0.16 RM_ENTROPY_COEF=0.001
export RM_W_ACTION_RATE=-0.08 RM_W_ACTION_ACC=-0.015 RM_W_FLAT_ORIENT=-6.0

"$PY" -m py_compile "$CODE/route_isaac.py" "$CODE/skills_isaac.py" \
  "$CODE/mod4_task.py" "$CODE/repair_contracts.py" "$CODE/repair_step.py" \
  "$CODE/eval_episodes_mod4.py"
"$PY" -m pytest -q "$CODE/test_takeover_contracts.py" >"$OUT/static_tests.log" 2>&1

"$PY" "$CODE/train_mod4_ppo.py" --headless --num_envs 2048 \
  --additional_iterations 61 --save_interval 10 --steps_per_env 48 \
  --learning_rate 0.00008 --run_name zero_repair_probe_v2 --seed 20260918 \
  --log_root "$OUT/logs" --init_checkpoint "$CKPT" \
  --report "$OUT/train_report.json" >"$OUT/train.log" 2>&1

RUN=$(find "$OUT/logs" -mindepth 1 -maxdepth 1 -type d -name '*_zero_repair_probe_v2' \
  -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
test -f "$RUN/model_60.pt"
"$PY" "$CODE/eval_episodes_mod4.py" --headless --checkpoint "$RUN/model_60.pt" \
  --manifest "$RUN/run_manifest.json" --num_envs 36 --steps 1250 --seed 20260919 \
  --training_route_scope --report "$OUT/eval_training_scope.json" \
  >"$OUT/eval_training_scope.log" 2>&1

sha256sum "$RUN/model_60.pt" "$RUN/run_manifest.json" >"$OUT/SHA256SUMS"
echo "PASS_ZERO_REPAIR_PROBE_V2 run=$RUN"
