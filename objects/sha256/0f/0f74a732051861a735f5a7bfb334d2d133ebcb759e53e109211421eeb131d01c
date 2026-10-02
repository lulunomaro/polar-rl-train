#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
CODE="$ROOT/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
LOG_ROOT="$ROOT/logs/takeover_20260914"
SUP="$LOG_ROOT/supervisor"
STATUS="$SUP/STATUS.json"
EXPORT="$ROOT/exports/takeover_20260914_resume10h"
mkdir -p "$SUP" "$EXPORT"

exec 9>/tmp/mod4_takeover_gpu0.lock
flock -n 9 || { echo 'GPU0 is owned by another MOD4 job' >&2; exit 80; }
if pgrep -af 'train_mod4_ppo.py|eval_episodes_mod4.py|export_final_policy.py' | grep -v "$PPID" | grep -q .; then
  echo 'refusing to share GPU with another Isaac job' >&2
  exit 81
fi

cd "$ROOT"
set -a
source takeover/common.env
set +a
export TAKEOVER_NUM_ENVS=1024

readarray -t source_vals < <(python3 - "$STATUS" <<'PY'
import json, sys
d=json.load(open(sys.argv[1],encoding='utf8'))
if d.get('status') != 'PAUSED_USER_REQUEST':
    raise SystemExit('resume requires PAUSED_USER_REQUEST, got '+str(d.get('status')))
print(d['checkpoint']); print(d['manifest']); print(d.get('checkpoint_sha256',''))
PY
)
checkpoint="${source_vals[0]}"
manifest="${source_vals[1]}"
expected_sha="${source_vals[2]}"
[[ -f "$checkpoint" && -f "$manifest" ]]
actual_sha=$(sha256sum "$checkpoint" | cut -d' ' -f1)
[[ -z "$expected_sha" || "$actual_sha" == "$expected_sha" ]]

started=$(date +%s)
deadline=$((started + 10*3600))
train_deadline=$((deadline - 15*60))
python3 - "$STATUS" "$started" "$deadline" "$checkpoint" "$manifest" <<'PY'
import json, sys, time
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text())
d.update(status='TRAINING',stage='recovery_dr',num_envs=1024,
         resume_started_epoch=int(sys.argv[2]),resume_deadline_epoch=int(sys.argv[3]),
         checkpoint=sys.argv[4],manifest=sys.argv[5],onnx=None,updated_epoch=int(time.time()))
p.write_text(json.dumps(d,indent=2)+'\n')
PY
echo "[$(date -Is)] resume10h started checkpoint=$checkpoint deadline_epoch=$deadline" >> "$SUP/timeline.log"

write_status () {
  local state="$1" stage="$2"
  python3 - "$STATUS" "$state" "$stage" "$checkpoint" "$manifest" <<'PY'
import json, sys, time
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text())
d.update(status=sys.argv[2],stage=sys.argv[3],checkpoint=sys.argv[4],manifest=sys.argv[5],
         updated_epoch=int(time.time()))
p.write_text(json.dumps(d,indent=2)+'\n')
PY
}

run_stage () {
  local name="$1" iters="$2" max_seconds="$3" lr="$4"
  local rc=0 run_dir next
  write_status TRAINING "$name"
  echo "[$(date -Is)] stage=$name iters=$iters lr=$lr checkpoint=$checkpoint" >> "$SUP/timeline.log"
  set +e
  timeout --signal=INT --kill-after=90 "${max_seconds}s" "$PY" "$CODE/train_mod4_ppo.py" \
    --num_envs 1024 --additional_iterations "$iters" --save_interval 25 --steps_per_env 24 \
    --learning_rate "$lr" --run_name "$name" --seed 20260922 \
    --log_root "$LOG_ROOT" --init_checkpoint "$checkpoint" > "$SUP/${name}.log" 2>&1
  rc=$?
  set -e
  run_dir=$(find "$LOG_ROOT" -mindepth 1 -maxdepth 1 -type d -name "*_${name}" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
  [[ -n "$run_dir" && -f "$run_dir/run_manifest.json" ]]
  next=$(find "$run_dir" -maxdepth 1 -type f -name 'model_*.pt' -printf '%f\n' | sort -V | tail -1)
  [[ -n "$next" ]]
  if grep -Eqi 'CUDA out of memory|nonfinite|NaN detected|Traceback \(most recent call last\)' "$SUP/${name}.log"; then
    echo "fatal signature in $name" >&2
    exit 92
  fi
  checkpoint="$run_dir/$next"
  manifest="$run_dir/run_manifest.json"
  sha256sum "$checkpoint" "$manifest" >> "$SUP/CHECKPOINTS.sha256"
  echo "[$(date -Is)] stage=$name rc=$rc checkpoint=$checkpoint" >> "$SUP/timeline.log"
  if (( rc == 124 || rc == 130 || rc == 137 )); then return 2; fi
  (( rc == 0 )) || exit "$rc"
}

# Recover the route buckets that collapsed to curriculum level zero under immediate full DR.
export RM_DR_OFF=0 RM_CURR_INIT_LEVEL=1 RM_INIT_STD=0.10
export RM_ROUTE_WEIGHTS='run:3,ramp_up:5,ramp_down:2,step_up:5,step_down:2,rough_cross:6,slope_spin:6,fly_jump:6,jump_in_place:3,tunnel_cross:4'
export RM_STIFFNESS_MIN=0.93 RM_STIFFNESS_MAX=1.07 RM_DAMPING_MIN=0.90 RM_DAMPING_MAX=1.10
export RM_EFFORT_LEG_MIN=0.93 RM_EFFORT_LEG_MAX=1.07 RM_EFFORT_WHEEL_MIN=0.93 RM_EFFORT_WHEEL_MAX=1.07
export RM_ARMATURE_MIN=0.80 RM_ARMATURE_MAX=1.25 RM_ENCODER_BIAS=0.010
export RM_OBS_DELAY_MAX_LAG=1 RM_ACTION_DELAY_MS_MAX=3 RM_SHAPE_FRICTION_MIN=0.75 RM_SHAPE_FRICTION_MAX=1.25
export RM_CHASSIS_MASS_ADD_MIN=-0.75 RM_CHASSIS_MASS_ADD_MAX=1.5 RM_COM_X=0.03 RM_COM_Y=0.015 RM_COM_Z=0.015
export RM_CHASSIS_INERTIA_MIN=0.85 RM_CHASSIS_INERTIA_MAX=1.15
export RM_LIMB_MASS_MIN=0.93 RM_LIMB_MASS_MAX=1.07 RM_LIMB_INERTIA_MIN=0.85 RM_LIMB_INERTIA_MAX=1.15
export RM_WHEEL_MASS_MIN=0.93 RM_WHEEL_MASS_MAX=1.07 RM_WHEEL_INERTIA_MIN=0.85 RM_WHEEL_INERTIA_MAX=1.15
export RM_GAS_STIFFNESS_MIN=0.85 RM_GAS_STIFFNESS_MAX=1.15 RM_GAS_DAMPING_MIN=0.85 RM_GAS_DAMPING_MAX=1.15
export RM_EFFORT_NOISE=0.02 RM_EFFORT_NOISE_WHEEL=0.015 RM_DEFAULT_DOF_POS_RANGE=0.02
export RM_LEG_FRICTION_MAX=0.07 RM_WHEEL_FRICTION_MAX=0.015 RM_RESTITUTION_MAX=0.06
cutoff=0
run_stage 8_recovery_dr 650 8000 0.0001 || cutoff=$?

if (( cutoff == 0 )); then
  # Restore the frozen full-DR ceiling, keeping the failure-focused route mixture.
  set -a
  source takeover/common.env
  set +a
  export TAKEOVER_NUM_ENVS=1024 RM_DR_OFF=0 RM_CURR_INIT_LEVEL=2 RM_INIT_STD=0.11
  export RM_ROUTE_WEIGHTS='run:3,ramp_up:5,ramp_down:2,step_up:5,step_down:2,rough_cross:6,slope_spin:6,fly_jump:6,jump_in_place:3,tunnel_cross:4'
  remaining=$((train_deadline - $(date +%s)))
  if (( remaining > 600 )); then
    run_stage 9_full_dr_10h 5000 "$remaining" 0.000075 || cutoff=$?
  fi
fi

write_status EXPORTING resume10h_export
remaining=$((deadline - $(date +%s)))
if (( remaining > 120 )); then
  timeout --signal=INT --kill-after=30 "${remaining}s" "$PY" "$CODE/export_final_policy.py" \
    --checkpoint "$checkpoint" --manifest "$manifest" --out "$EXPORT/policy.onnx" \
    > "$SUP/resume10h_export.log" 2>&1 || true
fi
if [[ -f "$EXPORT/policy.onnx" ]]; then
  sha256sum "$EXPORT/policy.onnx" "$EXPORT/policy.contract.json" > "$EXPORT/SHA256SUMS"
fi
python3 - "$STATUS" "$checkpoint" "$manifest" "$EXPORT/policy.onnx" <<'PY'
import json, sys, time
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text())
onnx=sys.argv[4] if Path(sys.argv[4]).is_file() else None
d.update(status='RESUME10H_COMPLETE',stage='complete',checkpoint=sys.argv[2],manifest=sys.argv[3],
         onnx=onnx,completed_epoch=int(time.time()))
p.write_text(json.dumps(d,indent=2)+'\n')
PY
echo "[$(date -Is)] resume10h complete checkpoint=$checkpoint onnx=$EXPORT/policy.onnx" >> "$SUP/timeline.log"
