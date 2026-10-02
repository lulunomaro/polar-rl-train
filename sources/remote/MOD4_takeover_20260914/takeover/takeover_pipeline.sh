#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
CODE="$ROOT/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
BASELINE=/home/egde/fangzhen_linux/logs/isaac_mod4/2026-09-13_01-17-30_mod4_fixed_mixed/model_16295.pt
LOG_ROOT="$ROOT/logs/takeover_20260914"
SUP="$LOG_ROOT/supervisor"
EXPORT="$ROOT/exports/takeover_20260914"
NUM_ENVS="${TAKEOVER_NUM_ENVS:-1024}"
mkdir -p "$LOG_ROOT" "$SUP" "$EXPORT"

exec 9>/tmp/mod4_takeover_gpu0.lock
if ! flock -n 9; then
  echo "another MOD4 takeover owns GPU0" >&2
  exit 80
fi
if pgrep -af 'train_mod4_ppo.py|eval_episodes_mod4.py|export_final_policy.py' | grep -v "$PPID" | grep -q .; then
  echo "refusing to share GPU with another Isaac job" >&2
  pgrep -af 'train_mod4_ppo.py|eval_episodes_mod4.py|export_final_policy.py' >&2 || true
  exit 81
fi

cd "$ROOT"
set -a
source takeover/common.env
set +a
export TAKEOVER_BASELINE="$BASELINE"
export TAKEOVER_STARTED_EPOCH="$(date +%s)"
export TAKEOVER_DEADLINE_EPOCH="$((TAKEOVER_STARTED_EPOCH + 8*3600))"
export TAKEOVER_TRAIN_DEADLINE_EPOCH="$((TAKEOVER_DEADLINE_EPOCH - 12*60))"
export SUPERVISOR_STATUS="$SUP/STATUS.json"

(cd "$CODE" && "$PY" -m unittest -v test_takeover_contracts.py) > "$SUP/cpu_tests.log" 2>&1
"$PY" takeover/preflight.py > "$SUP/preflight.log" 2>&1
sha256sum takeover/common.env takeover/takeover_pipeline.sh isaac/mod4/*.py \
  "$RM_MOD4_USD" "$BASELINE" > "$SUP/FROZEN.sha256"

python3 - <<'PY'
import json, os, time
from pathlib import Path
p=Path(os.environ['SUPERVISOR_STATUS'])
p.write_text(json.dumps({'status':'PREFLIGHT_PASS','started_epoch':int(os.environ['TAKEOVER_STARTED_EPOCH']),
 'deadline_epoch':int(os.environ['TAKEOVER_DEADLINE_EPOCH']),'stage':None,
 'num_envs':int(os.environ['TAKEOVER_NUM_ENVS'])},indent=2)+'\n')
PY

checkpoint="$BASELINE"
final_manifest=""
stage_index=0

write_status () {
  STATUS_VALUE="$1" STAGE_VALUE="$2" CKPT_VALUE="$checkpoint" MANIFEST_VALUE="$final_manifest" \
  python3 - <<'PY'
import json, os, time
from pathlib import Path
p=Path(os.environ['SUPERVISOR_STATUS'])
d=json.loads(p.read_text()) if p.exists() else {}
d.update(status=os.environ['STATUS_VALUE'], stage=os.environ['STAGE_VALUE'],
         checkpoint=os.environ['CKPT_VALUE'], manifest=os.environ['MANIFEST_VALUE'],
         updated_epoch=int(time.time()))
p.write_text(json.dumps(d,indent=2)+'\n')
PY
}

run_stage () {
  local name="$1" iters="$2" dr="$3" weights="$4" std="$5" preset="$6"
  local now remain rc run_dir next
  now=$(date +%s)
  remain=$((TAKEOVER_TRAIN_DEADLINE_EPOCH - now))
  if (( remain < 600 )); then
    echo "[$(date -Is)] no budget for $name; keeping $checkpoint" | tee -a "$SUP/timeline.log"
    return 2
  fi
  export RM_DR_OFF="$dr" RM_ROUTE_WEIGHTS="$weights" RM_INIT_STD="$std"
  if [[ "$preset" == mild ]]; then
    export RM_STIFFNESS_MIN=0.95 RM_STIFFNESS_MAX=1.05 RM_DAMPING_MIN=0.95 RM_DAMPING_MAX=1.05
    export RM_EFFORT_LEG_MIN=0.95 RM_EFFORT_LEG_MAX=1.05 RM_EFFORT_WHEEL_MIN=0.95 RM_EFFORT_WHEEL_MAX=1.05
    export RM_ARMATURE_MIN=0.85 RM_ARMATURE_MAX=1.20 RM_ENCODER_BIAS=0.008
    export RM_OBS_DELAY_MAX_LAG=1 RM_ACTION_DELAY_MS_MAX=2 RM_SHAPE_FRICTION_MIN=0.80 RM_SHAPE_FRICTION_MAX=1.20
    export RM_CHASSIS_MASS_ADD_MIN=-0.5 RM_CHASSIS_MASS_ADD_MAX=1.0 RM_COM_X=0.02 RM_COM_Y=0.01 RM_COM_Z=0.01
    export RM_CHASSIS_INERTIA_MIN=0.90 RM_CHASSIS_INERTIA_MAX=1.10
    export RM_LIMB_MASS_MIN=0.95 RM_LIMB_MASS_MAX=1.05 RM_LIMB_INERTIA_MIN=0.90 RM_LIMB_INERTIA_MAX=1.10
    export RM_WHEEL_MASS_MIN=0.95 RM_WHEEL_MASS_MAX=1.05 RM_WHEEL_INERTIA_MIN=0.90 RM_WHEEL_INERTIA_MAX=1.10
    export RM_GAS_STIFFNESS_MIN=0.90 RM_GAS_STIFFNESS_MAX=1.10 RM_GAS_DAMPING_MIN=0.90 RM_GAS_DAMPING_MAX=1.10
    export RM_EFFORT_NOISE=0.015 RM_EFFORT_NOISE_WHEEL=0.01 RM_DEFAULT_DOF_POS_RANGE=0.015
    export RM_LEG_FRICTION_MAX=0.05 RM_WHEEL_FRICTION_MAX=0.01
    export RM_RESTITUTION_MAX=0.05
  elif [[ "$preset" == full ]]; then
    source takeover/common.env
    export RM_DR_OFF="$dr" RM_ROUTE_WEIGHTS="$weights" RM_INIT_STD="$std"
  fi
  stage_index=$((stage_index+1))
  echo "[$(date -Is)] stage=$name iters=$iters dr=$dr preset=$preset ckpt=$checkpoint budget_s=$remain" | tee -a "$SUP/timeline.log"
  write_status TRAINING "$name"
  set +e
  timeout --signal=INT --kill-after=90 "${remain}s" "$PY" "$CODE/train_mod4_ppo.py" \
    --num_envs "$NUM_ENVS" --additional_iterations "$iters" --save_interval 50 --steps_per_env 24 \
    --learning_rate 0.0001 --run_name "${stage_index}_${name}" --seed "$((20260914+stage_index))" \
    --log_root "$LOG_ROOT" --init_checkpoint "$checkpoint" \
    > "$SUP/${stage_index}_${name}.log" 2>&1
  rc=$?
  set -e
  run_dir=$(find "$LOG_ROOT" -mindepth 1 -maxdepth 1 -type d -name "*_${stage_index}_${name}" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
  if [[ -z "$run_dir" || ! -f "$run_dir/run_manifest.json" ]]; then
    echo "stage $name created no auditable run" >&2
    exit 90
  fi
  next=$(find "$run_dir" -maxdepth 1 -type f -name 'model_*.pt' -printf '%f\n' | sort -V | tail -1)
  if [[ -z "$next" ]]; then
    echo "stage $name produced no checkpoint" >&2
    exit 91
  fi
  if (( rc != 0 && rc != 124 && rc != 130 && rc != 137 )) && \
     grep -Eqi 'CUDA out of memory|nonfinite|NaN detected|Traceback \(most recent call last\)' "$SUP/${stage_index}_${name}.log"; then
    echo "stage $name log contains a fatal signature" >&2
    exit 92
  fi
  checkpoint="$run_dir/$next"
  final_manifest="$run_dir/run_manifest.json"
  sha256sum "$checkpoint" "$final_manifest" >> "$SUP/CHECKPOINTS.sha256"
  echo "[$(date -Is)] stage=$name rc=$rc -> $checkpoint" | tee -a "$SUP/timeline.log"
  if (( rc == 124 || rc == 130 || rc == 137 )); then
    write_status DEADLINE_CHECKPOINT "$name"
    return 2
  elif (( rc != 0 )); then
    exit "$rc"
  fi
}

trap 'rc=$?; write_status FAILED "${name:-pipeline}"; echo "pipeline failed rc=$rc" >> "$SUP/timeline.log"' ERR

W_FOUNDATION='run:8,ramp_up:2,ramp_down:2,step_up:2,step_down:2,rough_cross:3,slope_spin:1,fly_jump:1,jump_in_place:1,tunnel_cross:1'
W_TERRAIN='run:4,ramp_up:4,ramp_down:2,step_up:5,step_down:2,rough_cross:5,slope_spin:5,fly_jump:2,jump_in_place:1,tunnel_cross:1'
W_FLIGHT='run:4,ramp_up:3,ramp_down:2,step_up:3,step_down:2,rough_cross:3,slope_spin:3,fly_jump:7,jump_in_place:4,tunnel_cross:1'
W_BALANCED='run:4,ramp_up:3,ramp_down:2,step_up:4,step_down:2,rough_cross:4,slope_spin:4,fly_jump:4,jump_in_place:2,tunnel_cross:1'

run_stage foundation 400 1 "$W_FOUNDATION" 0.14 nominal || pipeline_cutoff=$?
[[ ${pipeline_cutoff:-0} -eq 2 ]] || run_stage terrain_spin 600 1 "$W_TERRAIN" 0.16 nominal || pipeline_cutoff=$?
[[ ${pipeline_cutoff:-0} -eq 2 ]] || run_stage flight_jump 650 1 "$W_FLIGHT" 0.18 nominal || pipeline_cutoff=$?
[[ ${pipeline_cutoff:-0} -eq 2 ]] || run_stage mixed_nominal 450 1 "$W_BALANCED" 0.14 nominal || pipeline_cutoff=$?
[[ ${pipeline_cutoff:-0} -eq 2 ]] || run_stage mild_dr 650 0 "$W_BALANCED" 0.16 mild || pipeline_cutoff=$?
# Consume the remaining protected window with the final DR distribution.  Save every 50
# iterations; the deadline signal may end this stage, and the newest complete checkpoint wins.
[[ ${pipeline_cutoff:-0} -eq 2 ]] || run_stage full_dr 5000 0 "$W_BALANCED" 0.14 full || pipeline_cutoff=$?

write_status EXPORTING final
remaining=$((TAKEOVER_DEADLINE_EPOCH - $(date +%s)))
if (( remaining > 180 )); then
  timeout --signal=INT --kill-after=30 "${remaining}s" "$PY" "$CODE/export_final_policy.py" \
    --checkpoint "$checkpoint" --manifest "$final_manifest" \
    --out "$EXPORT/policy.onnx" > "$SUP/export.log" 2>&1 || true
fi
if [[ -f "$EXPORT/policy.onnx" ]]; then
  sha256sum "$EXPORT/policy.onnx" "$EXPORT/policy.contract.json" > "$EXPORT/SHA256SUMS"
fi
FINAL_CKPT="$checkpoint" FINAL_MANIFEST="$final_manifest" FINAL_ONNX="$EXPORT/policy.onnx" \
python3 - <<'PY'
import json, os, time
from pathlib import Path
p=Path(os.environ['SUPERVISOR_STATUS']); d=json.loads(p.read_text())
d.update(status='TRAINING_WINDOW_COMPLETE',stage='complete',checkpoint=os.environ['FINAL_CKPT'],
 manifest=os.environ['FINAL_MANIFEST'],onnx=os.environ['FINAL_ONNX'] if Path(os.environ['FINAL_ONNX']).is_file() else None,
 completed_epoch=int(time.time()))
p.write_text(json.dumps(d,indent=2)+'\n')
PY
echo "[$(date -Is)] complete checkpoint=$checkpoint onnx=$EXPORT/policy.onnx" | tee -a "$SUP/timeline.log"
