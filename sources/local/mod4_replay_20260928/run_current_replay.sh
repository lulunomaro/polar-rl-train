#!/usr/bin/env bash
# SCUT-style visual/trace replay for the current MOD4 flat run. Never launches PPO.
set -Eeuo pipefail

ROOT=/home/egde/fangzhen_linux
RUN=${MOD4_REPLAY_RUN:-$ROOT/runs4090/logs/2026-09-28_22-07-51_flat_v7_4090_20k_s16}
PY=${MOD4_REPLAY_PY:-/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python}

if [[ ! -f "$RUN/run_manifest.json" ]]; then
  echo "Missing run manifest: $RUN/run_manifest.json" >&2
  exit 2
fi
CHECKPOINT=$(find "$RUN" -maxdepth 1 -type f -name 'model_[0-9]*.pt' -printf '%f\n' | sort -V | tail -n 1)
if [[ -z "$CHECKPOINT" ]]; then
  echo "No completed model_*.pt found in $RUN" >&2
  exit 2
fi
if pgrep -f '[t]rain_mod4_ppo.py' >/dev/null && [[ ${REPLAY_ALLOW_CONCURRENT:-0} != 1 ]]; then
  echo "PPO is running. Replay would share the 4090; wait for it to finish or set REPLAY_ALLOW_CONCURRENT=1." >&2
  exit 3
fi

echo "Replay checkpoint: $RUN/$CHECKPOINT"
exec "$PY" "$ROOT/isaac/mod4/replay_mod4.py" \
  --checkpoint "$RUN/$CHECKPOINT" --manifest "$RUN/run_manifest.json" "$@"
