#!/usr/bin/env bash
# Goal section 5 pipeline: 1024-env throughput test -> DR training -> acceptance.
#
#   ./run_dr_stage_mod4.sh <nominal_checkpoint> [tag] [dr_iters] [test_only]
#
# ONE training process at a time; refuses to start while train_mod4_ppo.py is alive.
# Requires patch_dr_battery_terrain.py to be applied (the launcher enforces it too).
set -uo pipefail
cd "$(dirname "$0")/../.."
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
CKPT=${1:?usage: run_dr_stage_mod4.sh <nominal_checkpoint> [tag] [dr_iters] [test_only]}
TAG=${2:-dr}
DR_ITERS=${3:-800}
TEST_ONLY=${4:-0}

LOG=logs/isaac_mod4/dr_stage_$(date +%Y%m%d_%H%M%S).log
log() { echo "[dr-stage] $*" | tee -a "$LOG"; }

if pgrep -f "train_mod4_ppo.py" >/dev/null; then
  log "REFUSING: a MOD4 training is already alive (one at a time)"
  pgrep -af "train_mod4_ppo.py" | tee -a "$LOG"
  exit 5
fi

latest_dr_run() { ls -dt logs/isaac_mod4/*_mod4_fixed_dr/ 2>/dev/null | head -1; }
latest_ckpt()   { local d=$1; ls -t "$d" 2>/dev/null | grep '^model_' | head -1; }

# launch_and_wait <label> <iters> -> sets TRAIN_LOG, exits on Traceback
launch_and_wait() {
  local label=$1 iters=$2 boot stable
  boot=$(mktemp /tmp/mod4_dr_boot.XXXX.log)
  FORCE=1 bash migration/linux/start_mod4_dr_fixedplant.sh "$CKPT" 1024 "$iters" >"$boot" 2>&1
  grep -h "^\[dr-launch\]" "$boot" | tee -a "$LOG"
  TRAIN_LOG=$(grep -o 'log=.*' "$boot" | tail -1 | cut -d= -f2)
  [ -n "${TRAIN_LOG:-}" ] && [ -f "$TRAIN_LOG" ] || { log "$label: could not resolve training log"; tail -20 "$boot" | tee -a "$LOG"; exit 1; }
  log "$label: training log = $TRAIN_LOG"
  sleep 60
  pgrep -f "train_mod4_ppo.py --headless" >/dev/null || { log "$label did not start"; tail -30 "$TRAIN_LOG" | tee -a "$LOG"; exit 1; }
  stable=0
  while true; do
    if pgrep -f "train_mod4_ppo.py --headless" >/dev/null; then stable=0; else
      stable=$((stable+1)); [ "$stable" -ge 3 ] && break
    fi
    if tail -120 "$TRAIN_LOG" | grep -q "Traceback"; then
      log "$label: Traceback detected -- aborting"; tail -40 "$TRAIN_LOG" | tee -a "$LOG"; exit 1
    fi
    sleep 60
  done
  log "$label finished"
}

# ---------------------------------------------------------------- 1) throughput test
log "=== 1024-env throughput / stability test (20 iters, DR ON) ==="
( for i in $(seq 1 40); do nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader; sleep 15; done ) > /tmp/mod4_dr_gpu.txt &
GPU_MON=$!
launch_and_wait "throughput test" 20
kill $GPU_MON 2>/dev/null || true
TEST_RUN=$(latest_dr_run)
{
  echo "checkpoint_in : $CKPT"
  echo "run_dir       : $TEST_RUN"
  echo "training_log  : ${TRAIN_LOG:-?}"
  echo "iters_logged  : $(grep -c 'Iteration time' "${TRAIN_LOG:-/dev/null}")"
  grep -E "Iteration time|Total steps" "${TRAIN_LOG:-/dev/null}" | tail -6
  echo "nan_events    : $(grep -c nan_detection "${TRAIN_LOG:-/dev/null}")"
  echo "traceback     : $(grep -c Traceback "${TRAIN_LOG:-/dev/null}")"
  echo "gpu_samples   : $(wc -l < /tmp/mod4_dr_gpu.txt)"
  sort -u /tmp/mod4_dr_gpu.txt | tail -6
} > docs/dr_throughput_1024.txt
cat docs/dr_throughput_1024.txt | tee -a "$LOG"
if [ "$TEST_ONLY" = "1" ]; then log "test-only requested -- stopping"; exit 0; fi

# ---------------------------------------------------------------- 2) DR run
log "=== DR training: 1024 env x $DR_ITERS iters from $CKPT ==="
launch_and_wait "DR training" "$DR_ITERS"
DR_RUN=$(latest_dr_run); DR_CKPT="$DR_RUN$(latest_ckpt "$DR_RUN")"
log "DR checkpoint = $DR_CKPT"

# ---------------------------------------------------------------- 3) acceptance
log "=== acceptance on $DR_CKPT ==="
bash migration/linux/eval_and_gate_mod4.sh terrain "$DR_CKPT" 64 2200 >>"$LOG" 2>&1 || true
bash migration/linux/final_acceptance_mod4.sh "$DR_CKPT" "$TAG" >>"$LOG" 2>&1 || true
log "done -> docs/acceptance_${TAG}/"
