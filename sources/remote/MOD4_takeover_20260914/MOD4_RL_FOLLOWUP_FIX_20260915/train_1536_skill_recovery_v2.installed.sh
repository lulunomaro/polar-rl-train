#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
WORK="$ROOT/env_scaling_20260915"
CODE="$WORK/source/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
RESUME_FROM_S2=${RM_RESUME_FROM_S2:-0}
DEFAULT_CHECKPOINT="$ROOT/logs/takeover_20260914/2026-09-15_08-47-15_9_full_dr_10h/model_2775.pt"
CHECKPOINT=${RM_RESUME_CHECKPOINT:-$DEFAULT_CHECKPOINT}
DERIVED_USD="$ROOT/repair_1536_20260915/asset/robot_tireload12.usd"
RUN_TAG=${RM_RUN_TAG:-takeover_1536_20260915_v2}
LOG_ROOT="$ROOT/logs/$RUN_TAG"
SUP="$LOG_ROOT/supervisor"
STATUS="$SUP/STATUS.json"
EXPORT="$ROOT/exports/$RUN_TAG"
ACCEPT="$ROOT/acceptance/$RUN_TAG"
mkdir -p "$SUP" "$EXPORT" "$ACCEPT"

exec 9>/tmp/mod4_takeover_gpu0.lock
flock -n 9 || { echo 'GPU0 is owned by another MOD4 job' >&2; exit 80; }
if pgrep -af 'train_mod4_ppo.py|eval_episodes_mod4.py|export_final_policy.py' | grep -v "$PPID" | grep -q .; then
  echo 'refusing to share GPU with another Isaac job' >&2
  exit 81
fi

DONE=0
GPU_MON_PID=''
write_status () {
  local state="$1" stage="$2" ckpt="${3:-$CHECKPOINT}" manifest="${4:-}"
  python3 - "$STATUS" "$state" "$stage" "$ckpt" "$manifest" <<'PY'
import json,sys,time
from pathlib import Path
p=Path(sys.argv[1]); old={}
if p.exists():
    try: old=json.loads(p.read_text())
    except Exception: old={}
old.update(schema='mod4_1536_recovery_v1', status=sys.argv[2], stage=sys.argv[3],
           num_envs=1536, checkpoint=sys.argv[4], manifest=sys.argv[5] or None,
           updated_epoch=int(time.time()))
p.write_text(json.dumps(old,indent=2)+'\n')
PY
}
on_exit () {
  rc=$?
  [[ -z "$GPU_MON_PID" ]] || kill "$GPU_MON_PID" 2>/dev/null || true
  if (( rc != 0 && DONE == 0 )); then
    write_status FAILED "${CURRENT_STAGE:-preflight}" "${checkpoint:-$CHECKPOINT}" "${manifest:-}"
    echo "[$(date -Is)] FAILED rc=$rc stage=${CURRENT_STAGE:-preflight}" >> "$SUP/timeline.log"
  fi
}
trap on_exit EXIT

[[ -f "$CHECKPOINT" && -f "$CODE/train_mod4_ppo.py" && -f "$DERIVED_USD" ]]
actual_sha=$(sha256sum "$CHECKPOINT" | cut -d' ' -f1)
if [[ "$RESUME_FROM_S2" != 1 ]]; then
  [[ "$actual_sha" == 741e0cdd242e53cea5d187f405b98e2f3931f4d9cd12a3cbc2832b342cb25c9f ]]
fi
printf '%s  %s\n' "$actual_sha" "$CHECKPOINT" > "$SUP/RESUME_CHECKPOINT.sha256"

write_status PREFLIGHT preflight "$CHECKPOINT" ''
"$PY" -m py_compile "$CODE/route_isaac.py" "$CODE/skills_isaac.py" \
  "$CODE/mod4_task.py" "$CODE/train_mod4_ppo.py"
"$PY" -m pytest -q "$CODE/test_takeover_contracts.py" > "$SUP/static_tests.log" 2>&1

set -a
source "$ROOT/takeover/common.env"
set +a
export TAKEOVER_NUM_ENVS=1536 RM_ROUTE_CURRICULUM=0
export RM_MOD4_USD="$DERIVED_USD" RM_GUIDE_FRICTION=0.02 RM_TIRE_ADD_MM=0
export RM_METRIC_PERIOD=20

checkpoint="$CHECKPOINT"
manifest=''
CURRENT_STAGE=smoke
write_status SMOKE smoke "$checkpoint" "$manifest"
export RM_DR_OFF=1 RM_ROUTE_KINDS='run,slope_spin,fly_jump,jump_in_place,tunnel_cross'
export RM_ROUTE_WEIGHTS='run:2,slope_spin:3,fly_jump:3,jump_in_place:3,tunnel_cross:4'
export RM_TUNNEL_GOAL_X=1.45 RM_TUNNEL_SPAWN_LEAD_M=0.15 RM_ROUGH_SPEED_MAX=0.8
export RM_JUMP_LO=0.05 RM_JUMP_HI=0.05 RM_JUMP_HI_MAX=0.05
export RM_GYRO_START=4.0 RM_GYRO_TARGET=5.0 RM_GYRO_EVERY=80
export RM_ENTROPY_COEF=0.0015 RM_INIT_STD=0.16
export RM_W_ACTION_RATE=-0.08 RM_W_ACTION_ACC=-0.015
timeout --signal=INT --kill-after=90 1200s "$PY" "$CODE/train_mod4_ppo.py" \
  --num_envs 128 --additional_iterations 16 --save_interval 9999 --steps_per_env 24 \
  --learning_rate 0.000075 --run_name smoke_skillfix --seed 20260915 \
  --log_root "$LOG_ROOT/smoke" --init_checkpoint "$checkpoint" > "$SUP/smoke.log" 2>&1
if grep -Eqi 'CUDA out of memory|nonfinite|NaN detected|Traceback \(most recent call last\)|64K materials' "$SUP/smoke.log"; then
  echo 'fatal signature in patched smoke run' >&2; exit 92
fi
grep -q 'Learning iteration' "$SUP/smoke.log"

: > "$SUP/gpu.csv"
(
  while true; do
    nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used,power.draw \
      --format=csv,noheader,nounits >> "$SUP/gpu.csv" 2>/dev/null || true
    sleep 2
  done
) & GPU_MON_PID=$!

stage_base () {
  set -a
  source "$ROOT/takeover/common.env"
  set +a
  export TAKEOVER_NUM_ENVS=1536 RM_ROUTE_CURRICULUM=0 RM_METRIC_PERIOD=20
  export RM_MOD4_USD="$DERIVED_USD" RM_GUIDE_FRICTION=0.02 RM_TIRE_ADD_MM=0
  export RM_ROUTE_KINDS=''
  export RM_JUMP_LAUNCH_READY=1
}

set_mild_dr () {
  export RM_STIFFNESS_MIN=0.95 RM_STIFFNESS_MAX=1.05 RM_DAMPING_MIN=0.95 RM_DAMPING_MAX=1.05
  export RM_EFFORT_LEG_MIN=0.95 RM_EFFORT_LEG_MAX=1.05 RM_EFFORT_WHEEL_MIN=0.95 RM_EFFORT_WHEEL_MAX=1.05
  export RM_ARMATURE_MIN=0.85 RM_ARMATURE_MAX=1.20 RM_ENCODER_BIAS=0.008
  export RM_OBS_DELAY_MIN_LAG=0 RM_OBS_DELAY_MAX_LAG=1 RM_ACTION_DELAY_MS_MIN=0 RM_ACTION_DELAY_MS_MAX=2
  export RM_SHAPE_FRICTION_MIN=0.80 RM_SHAPE_FRICTION_MAX=1.20 RM_CHASSIS_MASS_ADD_MIN=-0.5 RM_CHASSIS_MASS_ADD_MAX=1.0
  export RM_CHASSIS_INERTIA_MIN=0.90 RM_CHASSIS_INERTIA_MAX=1.10 RM_LIMB_MASS_MIN=0.95 RM_LIMB_MASS_MAX=1.05
  export RM_LIMB_INERTIA_MIN=0.90 RM_LIMB_INERTIA_MAX=1.10 RM_WHEEL_MASS_MIN=0.95 RM_WHEEL_MASS_MAX=1.05
  export RM_WHEEL_INERTIA_MIN=0.90 RM_WHEEL_INERTIA_MAX=1.10 RM_COM_X=0.02 RM_COM_Y=0.01 RM_COM_Z=0.01
  export RM_GAS_STIFFNESS_MIN=0.90 RM_GAS_STIFFNESS_MAX=1.10 RM_GAS_DAMPING_MIN=0.90 RM_GAS_DAMPING_MAX=1.10
}

run_stage () {
  local name="$1" iters="$2" lr="$3" run_dir next rc
  CURRENT_STAGE="$name"
  write_status TRAINING "$name" "$checkpoint" "$manifest"
  echo "[$(date -Is)] begin $name iters=$iters checkpoint=$checkpoint" >> "$SUP/timeline.log"
  set +e
  "$PY" "$CODE/train_mod4_ppo.py" --num_envs 1536 --additional_iterations "$iters" \
    --save_interval 25 --steps_per_env 24 --learning_rate "$lr" --run_name "$name" \
    --seed 20260915 --log_root "$LOG_ROOT" --init_checkpoint "$checkpoint" \
    > "$SUP/${name}.log" 2>&1
  rc=$?
  set -e
  (( rc == 0 )) || exit "$rc"
  if grep -Eqi 'CUDA out of memory|nonfinite|NaN detected|Traceback \(most recent call last\)|64K materials' "$SUP/${name}.log"; then
    echo "fatal signature in $name" >&2; exit 93
  fi
  run_dir=$(find "$LOG_ROOT" -mindepth 1 -maxdepth 1 -type d -name "*_${name}" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
  [[ -n "$run_dir" && -f "$run_dir/run_manifest.json" ]]
  next=$(find "$run_dir" -maxdepth 1 -type f -name 'model_*.pt' -printf '%f\n' | sort -V | tail -1)
  [[ -n "$next" ]]
  checkpoint="$run_dir/$next"; manifest="$run_dir/run_manifest.json"
  sha256sum "$checkpoint" "$manifest" >> "$SUP/CHECKPOINTS.sha256"
  echo "[$(date -Is)] end $name checkpoint=$checkpoint" >> "$SUP/timeline.log"
}

if [[ "$RESUME_FROM_S2" != 1 ]]; then
  # Phase 1: make every formerly dead skill produce a learnable signal under nominal physics.
  stage_base
  export RM_DR_OFF=1 RM_PARTIAL_WARMSTART=1 RM_KEEP_STD=0 RM_INIT_STD=0.18 RM_ENTROPY_COEF=0.0015
  export RM_ROUTE_WEIGHTS='run:2,ramp_up:6,ramp_down:2,step_up:6,step_down:2,rough_cross:6,slope_spin:6,fly_jump:6,jump_in_place:5,tunnel_cross:7'
  export RM_TUNNEL_GOAL_X=1.45 RM_TUNNEL_SPAWN_LEAD_M=0.15 RM_TUNNEL_PRECROUCH_LEAD_M=0.40
  export RM_ROUGH_SPEED_MAX=0.8 RM_JUMP_LO=0.06 RM_JUMP_HI=0.06 RM_JUMP_HI_MAX=0.06
  export RM_GYRO_START=4.0 RM_GYRO_TARGET=7.0 RM_GYRO_STEP=0.5 RM_GYRO_EVERY=80
  export RM_W_ACTION_RATE=-0.08 RM_W_ACTION_ACC=-0.015 RM_W_ACTION_L2_LEG=-0.08 RM_W_ACTION_L2_WHEEL=-0.02
  run_stage s1_signal_bootstrap 300 0.00010

  # Phase 2: introduce a deliberately narrow plant distribution.
  stage_base
  set_mild_dr
  export RM_DR_OFF=0 RM_PARTIAL_WARMSTART=1 RM_KEEP_STD=0 RM_INIT_STD=0.15 RM_ENTROPY_COEF=0.0010
  export RM_ROUTE_WEIGHTS='run:3,ramp_up:6,ramp_down:2,step_up:6,step_down:2,rough_cross:6,slope_spin:6,fly_jump:6,jump_in_place:5,tunnel_cross:7'
  export RM_TUNNEL_GOAL_X=1.80 RM_TUNNEL_SPAWN_LEAD_M=0.08 RM_TUNNEL_PRECROUCH_LEAD_M=0.32
  export RM_ROUGH_SPEED_MAX=1.1 RM_JUMP_LO=0.10 RM_JUMP_HI=0.10 RM_JUMP_HI_MAX=0.10
  export RM_GYRO_START=5.0 RM_GYRO_TARGET=9.0 RM_GYRO_STEP=0.5 RM_GYRO_EVERY=70
  export RM_W_ACTION_RATE=-0.10 RM_W_ACTION_ACC=-0.025 RM_W_ACTION_L2_LEG=-0.07 RM_W_ACTION_L2_WHEEL=-0.02
  run_stage s2_mild_dr 600 0.000085
fi

# Phase 2b: isolate the three manoeuvres whose old rewards/metrics were defective.  Keep the
# already-introduced mild DR and the proven 0.10 m jump target until real terminal-event counts
# exist; do not jump straight to 0.15 m on a mixed fly/in-place statistic.
stage_base
set_mild_dr
export RM_DR_OFF=0
export RM_PARTIAL_WARMSTART=1 RM_KEEP_STD=0 RM_INIT_STD=0.14 RM_ENTROPY_COEF=0.0010
export RM_ROUTE_KINDS='fly_jump,jump_in_place,tunnel_cross'
export RM_ROUTE_WEIGHTS='fly_jump:7,jump_in_place:6,tunnel_cross:8'
export RM_TUNNEL_GOAL_X=1.80 RM_TUNNEL_SPAWN_LEAD_M=0.05 RM_TUNNEL_PRECROUCH_LEAD_M=0.32
export RM_JUMP_LO=0.10 RM_JUMP_HI=0.10 RM_JUMP_HI_MAX=0.10
export RM_W_ACTION_RATE=-0.10 RM_W_ACTION_ACC=-0.025 RM_W_ACTION_L2_LEG=-0.07 RM_W_ACTION_L2_WHEEL=-0.02
run_stage s2b_specialist_recovery 450 0.000085

# Phase 3: full field, full route lengths and the recorded deployment DR ceiling.
stage_base
export RM_DR_OFF=0 RM_PARTIAL_WARMSTART=1 RM_KEEP_STD=0 RM_INIT_STD=0.13 RM_ENTROPY_COEF=0.0007
export RM_ROUTE_WEIGHTS='run:4,ramp_up:6,ramp_down:3,step_up:6,step_down:3,rough_cross:6,slope_spin:6,fly_jump:6,jump_in_place:5,tunnel_cross:7'
export RM_TUNNEL_GOAL_X=0 RM_TUNNEL_SPAWN_LEAD_M=0 RM_TUNNEL_PRECROUCH_LEAD_M=0.26
export RM_ROUGH_SPEED_MAX=1.5 RM_JUMP_LO=0.15 RM_JUMP_HI=0.15 RM_JUMP_HI_MAX=0.15
export RM_GYRO_START=6.0 RM_GYRO_TARGET=13.0 RM_GYRO_STEP=0.5 RM_GYRO_EVERY=70
export RM_W_ACTION_RATE=-0.12 RM_W_ACTION_ACC=-0.035 RM_W_ACTION_L2_LEG=-0.06 RM_W_ACTION_L2_WHEEL=-0.02
run_stage s3_full_dr 1250 0.000075

# Phase 4: preserve all skills under full DR while explicitly suppressing chatter.
stage_base
export RM_DR_OFF=0 RM_PARTIAL_WARMSTART=1 RM_KEEP_STD=0 RM_INIT_STD=0.10 RM_ENTROPY_COEF=0.0003
export RM_ROUTE_WEIGHTS='run:5,ramp_up:5,ramp_down:3,step_up:5,step_down:3,rough_cross:5,slope_spin:5,fly_jump:5,jump_in_place:4,tunnel_cross:6'
export RM_TUNNEL_GOAL_X=0 RM_TUNNEL_SPAWN_LEAD_M=0 RM_TUNNEL_PRECROUCH_LEAD_M=0.24
export RM_ROUGH_SPEED_MAX=1.7 RM_JUMP_LO=0.18 RM_JUMP_HI=0.18 RM_JUMP_HI_MAX=0.18
export RM_GYRO_START=8.0 RM_GYRO_TARGET=13.0 RM_GYRO_STEP=0.5 RM_GYRO_EVERY=80
export RM_W_ACTION_RATE=-0.22 RM_W_ACTION_ACC=-0.060 RM_W_ACTION_L2_LEG=-0.05 RM_W_ACTION_L2_WHEEL=-0.025
run_stage s4_smooth_consolidate 650 0.000050

CURRENT_STAGE=export
write_status EXPORTING export "$checkpoint" "$manifest"
"$PY" "$CODE/export_final_policy.py" --checkpoint "$checkpoint" --manifest "$manifest" \
  --out "$EXPORT/policy.onnx" > "$SUP/export.log" 2>&1
sha256sum "$checkpoint" "$manifest" "$EXPORT/policy.onnx" "$EXPORT/policy.contract.json" \
  > "$EXPORT/SHA256SUMS"

# Four independent seeds in both nominal and randomized physics. These results, rather than
# training reward, decide whether the old 0/4 failures have actually been removed.
CURRENT_STAGE=acceptance
write_status EVALUATING acceptance "$checkpoint" "$manifest"
acceptance_failed=0
for mode in nominal dr; do
  reports=()
  extra=(); [[ "$mode" == dr ]] && extra+=(--domain_rand)
  for seed in 20260915 20260916 20260917 20260918; do
    report="$ACCEPT/${mode}_${seed}.json"; reports+=("$report")
    "$PY" "$CODE/eval_episodes_mod4.py" --checkpoint "$checkpoint" --manifest "$manifest" \
      --num_envs 64 --steps 3500 --seed "$seed" --report "$report" "${extra[@]}" \
      > "$ACCEPT/${mode}_${seed}.log" 2>&1
  done
  if ! "$PY" "$CODE/aggregate_acceptance.py" "${reports[@]}" --profile "$mode" \
      --out "$ACCEPT/${mode}_summary.json" > "$ACCEPT/${mode}_summary.txt"; then
    acceptance_failed=1
  fi
done

if (( acceptance_failed )); then
  write_status NEEDS_TRAINING acceptance_failed "$checkpoint" "$manifest"
  echo "[$(date -Is)] deterministic acceptance failed; see $ACCEPT/*_summary.json" \
    >> "$SUP/timeline.log"
  DONE=1
  exit 0
fi

python3 - "$STATUS" "$checkpoint" "$manifest" "$EXPORT/policy.onnx" "$ACCEPT" <<'PY'
import json,sys,time
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text())
d.update(status='COMPLETE',stage='complete',checkpoint=sys.argv[2],manifest=sys.argv[3],
         onnx=sys.argv[4],acceptance_dir=sys.argv[5],completed_epoch=int(time.time()),
         updated_epoch=int(time.time()))
p.write_text(json.dumps(d,indent=2)+'\n')
PY
echo "[$(date -Is)] complete checkpoint=$checkpoint onnx=$EXPORT/policy.onnx" >> "$SUP/timeline.log"
DONE=1
