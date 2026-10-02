#!/usr/bin/env bash
# Keep the later no-gimbal closed-chain training alive until TARGET_ITER.
# Restarts resume the newest checkpoint of the same experiment; it never touches the
# Isaac serial teacher or the earlier CC production checkpoints.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXPERIMENT="${EXPERIMENT:-rm2025_later_tunnel250_10h}"
TARGET_ITER="${TARGET_ITER:-2400}"
INTERVAL="${INTERVAL:-60}"
LOGDIR="$ROOT/logs/linux_launch"
mkdir -p "$LOGDIR"

latest_iter() {
  local root="$ROOT/train/logs/rsl_rl/$EXPERIMENT" best=-1 path base n
  [[ -d "$root" ]] || { echo -1; return; }
  while IFS= read -r path; do
    base="$(basename "$path")"; n="${base#model_}"; n="${n%.pt}"
    [[ "$n" =~ ^[0-9]+$ ]] || continue
    (( n > best )) && best="$n"
  done < <(find "$root" -type f -name 'model_[0-9]*.pt' -print 2>/dev/null)
  echo "$best"
}

while true; do
  iter="$(latest_iter)"
  # rsl_rl names the final checkpoint with the iteration BEFORE the increment, so a
  # 2400-iteration run ends at model_2399.pt; treating 2399 as unfinished put the
  # 09-10 run into a 65-second restart loop.  Stop at TARGET_ITER - 1.
  if (( iter >= TARGET_ITER - 1 )); then
    echo "$(date -Is) target reached: $iter >= $TARGET_ITER" | tee -a "$LOGDIR/supervise_rm2025_later.log"
    break
  fi
  # Trust the process table first: a stale pid file must never launch a second 8192-env
  # trainer on the same GPU (that happened once and produced two competing runs).
  if pgrep -f "[m]jlab.scripts.train" >/dev/null 2>&1 \
     || pgrep -f "[r]un_rm2025_later_training.sh" >/dev/null 2>&1 \
     || pgrep -f "[c]heck_model_identity.py" >/dev/null 2>&1; then
    sleep "$INTERVAL"
    continue
  fi
  echo "$(date -Is) training not alive (latest iter $iter); relaunching" \
    | tee -a "$LOGDIR/supervise_rm2025_later.log"
  RUN_NAME="prod_$(date +%Y%m%d_%H%M%S)" TARGET_ITER="$TARGET_ITER" \
    EXPERIMENT="$EXPERIMENT" NUM_ENVS="${NUM_ENVS:-8192}" \
    bash "$ROOT/migration/linux/run_rm2025_later_training.sh" \
    >> "$LOGDIR/supervise_rm2025_later.log" 2>&1 || true
  sleep 60
done
