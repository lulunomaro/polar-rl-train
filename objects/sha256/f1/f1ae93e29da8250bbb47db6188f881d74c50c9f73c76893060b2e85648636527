#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
CODE="$ROOT/isaac/mod4"
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
LOG_ROOT="$ROOT/logs/takeover_20260914"
SUP="$LOG_ROOT/supervisor"
STATUS="$SUP/STATUS.json"
EXPORT="$ROOT/exports/takeover_20260914_extended"
mkdir -p "$SUP" "$EXPORT"

# Only one queued extension may exist.  Wait without using the GPU until the original
# eight-hour supervisor releases its exclusive job lock.
exec 7>/tmp/mod4_takeover_extension_queue.lock
flock -n 7 || { echo 'an extension is already queued' >&2; exit 82; }
echo "[$(date -Is)] extension queued; waiting for original GPU owner" >> "$SUP/timeline.log"
exec 8>/tmp/mod4_takeover_gpu0.lock
flock 8

cd "$ROOT"
set -a
source takeover/common.env
set +a
export TAKEOVER_NUM_ENVS=1024
export RM_DR_OFF=0
export RM_ROUTE_WEIGHTS='run:4,ramp_up:3,ramp_down:2,step_up:4,step_down:2,rough_cross:4,slope_spin:4,fly_jump:4,jump_in_place:2,tunnel_cross:1'
export RM_INIT_STD=0.12

readarray -t source_vals < <(python3 - "$STATUS" <<'PY'
import json, sys
d=json.load(open(sys.argv[1], encoding='utf8'))
if d.get('status') != 'TRAINING_WINDOW_COMPLETE':
    raise SystemExit('original supervisor did not complete cleanly: '+str(d.get('status')))
print(d['checkpoint'])
print(d['manifest'])
PY
)
checkpoint="${source_vals[0]}"
manifest="${source_vals[1]}"
[[ -f "$checkpoint" && -f "$manifest" ]]

started=$(date +%s)
deadline=$((started + 8*3600))
train_deadline=$((deadline - 12*60))
python3 - "$STATUS" "$started" "$deadline" "$checkpoint" "$manifest" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text())
d.update(status='TRAINING', stage='extended_full_dr', num_envs=1024,
         extension_started_epoch=int(sys.argv[2]), extension_deadline_epoch=int(sys.argv[3]),
         checkpoint=sys.argv[4], manifest=sys.argv[5])
p.write_text(json.dumps(d,indent=2)+'\n')
PY
echo "[$(date -Is)] extended_full_dr started checkpoint=$checkpoint deadline_epoch=$deadline" >> "$SUP/timeline.log"

remaining=$((train_deadline - $(date +%s)))
set +e
timeout --signal=INT --kill-after=90 "${remaining}s" "$PY" "$CODE/train_mod4_ppo.py" \
  --num_envs 1024 --additional_iterations 5000 --save_interval 50 --steps_per_env 24 \
  --learning_rate 0.0001 --run_name 7_extended_full_dr --seed 20260921 \
  --log_root "$LOG_ROOT" --init_checkpoint "$checkpoint" \
  > "$SUP/7_extended_full_dr.log" 2>&1
rc=$?
set -e
run_dir=$(find "$LOG_ROOT" -mindepth 1 -maxdepth 1 -type d -name '*_7_extended_full_dr' -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
[[ -n "$run_dir" && -f "$run_dir/run_manifest.json" ]]
next=$(find "$run_dir" -maxdepth 1 -type f -name 'model_*.pt' -printf '%f\n' | sort -V | tail -1)
[[ -n "$next" ]]
if (( rc != 0 && rc != 124 && rc != 130 && rc != 137 )); then
  if grep -Eqi 'CUDA out of memory|nonfinite|NaN detected|Traceback \(most recent call last\)' "$SUP/7_extended_full_dr.log"; then
    echo "extended training failed rc=$rc" >&2
    exit 92
  fi
  exit "$rc"
fi
checkpoint="$run_dir/$next"
manifest="$run_dir/run_manifest.json"
sha256sum "$checkpoint" "$manifest" >> "$SUP/CHECKPOINTS.sha256"
echo "[$(date -Is)] extended_full_dr rc=$rc checkpoint=$checkpoint" >> "$SUP/timeline.log"

python3 - "$STATUS" "$checkpoint" "$manifest" <<'PY'
import json, sys, time
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text())
d.update(status='EXPORTING',stage='extended_export',checkpoint=sys.argv[2],manifest=sys.argv[3],
         updated_epoch=int(time.time()))
p.write_text(json.dumps(d,indent=2)+'\n')
PY
remaining=$((deadline - $(date +%s)))
if (( remaining > 120 )); then
  timeout --signal=INT --kill-after=30 "${remaining}s" "$PY" "$CODE/export_final_policy.py" \
    --checkpoint "$checkpoint" --manifest "$manifest" --out "$EXPORT/policy.onnx" \
    > "$SUP/extended_export.log" 2>&1 || true
fi
if [[ -f "$EXPORT/policy.onnx" ]]; then
  sha256sum "$EXPORT/policy.onnx" "$EXPORT/policy.contract.json" > "$EXPORT/SHA256SUMS"
fi
python3 - "$STATUS" "$checkpoint" "$manifest" "$EXPORT/policy.onnx" <<'PY'
import json, sys, time
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text())
onnx=sys.argv[4] if Path(sys.argv[4]).is_file() else None
d.update(status='EXTENDED_WINDOW_COMPLETE',stage='complete',checkpoint=sys.argv[2],
         manifest=sys.argv[3],onnx=onnx,completed_epoch=int(time.time()))
p.write_text(json.dumps(d,indent=2)+'\n')
PY
echo "[$(date -Is)] extension complete checkpoint=$checkpoint onnx=$EXPORT/policy.onnx" >> "$SUP/timeline.log"
