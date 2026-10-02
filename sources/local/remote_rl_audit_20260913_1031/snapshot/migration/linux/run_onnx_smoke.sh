#!/usr/bin/env bash
# CPU-only ONNX pipeline smoke: raw policy + yaw-trim-baked policy, both stamped as
# non-deployable smoke artifacts.  Runs while the GPU trains; needs no onnxruntime.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

export PYTHONPATH="$ROOT/train/rmvehicle/src:$ROOT/third_party/rc_mjlab/mjlab/src"
export CUDA_VISIBLE_DEVICES=""
PY="$ROOT/third_party/rc_mjlab/.venv/bin/python"
LOG="$ROOT/logs/linux_launch"
mkdir -p "$LOG"
CKPT="${CKPT:-}"
if [[ -z "$CKPT" ]]; then
  # Newest checkpoint outside seed/ (seed copies have no params/env.yaml, which the
  # export provenance check needs).
  CKPT="$(find "$ROOT/train/logs/rsl_rl/rm2025_later_cc_v2" \
          -path '*/seed/*' -prune -o -name 'model_[0-9]*.pt' -printf '%T@ %p\n' 2>/dev/null \
          | sort -n | tail -1 | cut -d' ' -f2-)"
fi
[[ -n "$CKPT" && -f "$CKPT" ]] || { echo "no checkpoint found" >&2; exit 2; }
echo "checkpoint: $CKPT"

rm -f "$LOG/onnx_smoke.done"
echo "=== raw export ==="
RM_YAW_TRIM=off "$PY" train/export_onnx.py \
  --task RM2025-Later-CC-Field-v0 --model later --device cpu --smoke \
  --checkpoint "$CKPT" \
  --out train/deploy/rm2025_later_smoke_raw.onnx \
  --contract-out train/deploy/contract_rm2025_later.json \
  > "$LOG/onnx_smoke_raw.log" 2>&1 \
  || echo "raw export FAILED (see onnx_smoke_raw.log)" >> "$LOG/onnx_smoke_raw.log"

# The yaw-trim bake needs onnxruntime, which the training venv deliberately lacks.
if "$PY" -c "import onnxruntime" >/dev/null 2>&1; then
  echo "=== yaw-trim bake (onnxruntime present) ==="
  "$PY" scripts/bake_yaw_trim.py \
    --onnx train/deploy/rm2025_later_smoke_raw.onnx \
    --out train/deploy/rm2025_later_smoke_trim.onnx \
    --contract train/deploy/contract_rm2025_later.json \
    > "$LOG/onnx_smoke_trim.log" 2>&1 \
    || echo "trim bake FAILED (see onnx_smoke_trim.log)" >> "$LOG/onnx_smoke_trim.log"
else
  echo "=== yaw-trim bake SKIPPED (no onnxruntime on this host) ==="
  echo "run scripts/bake_yaw_trim.py on a deployment host to produce the trimmed artifact" \
    > "$LOG/onnx_smoke_trim.log"
fi
echo DONE > "$LOG/onnx_smoke.done"
